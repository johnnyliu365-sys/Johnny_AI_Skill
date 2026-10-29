"""Typed, opt-in ownership and dependency checks for local source changes.

The existing document gate remains the source of Git changes and canonical
path semantics. This module validates the versioned ownership map, binds a
ticket to that map, and checks Python imports in candidate blobs. It does not
classify semantic responsibility or enforce a host boundary.
"""

from __future__ import annotations

import ast
import hashlib
import re
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, TypeAdapter, ValidationError

MAP_PATH = "shared/BOUNDARY_MAP.toml"
MAX_MAP_BYTES = 1_048_576
MAX_PIN_BYTES = 8_192

PathNormalizer = Callable[[str], str | None]
PathMatcher = Callable[[str, str, bool], bool]


class ModuleKind(str, Enum):
    LIBRARY = "LIBRARY"
    SHARED = "SHARED"
    HARNESS = "HARNESS"
    SCRIPT = "SCRIPT"
    TEST = "TEST"


class ReadStatus(str, Enum):
    VALID = "VALID"
    UNDECLARED = "UNDECLARED"
    INVALID = "INVALID"


class EvaluationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REFUSED = "REFUSED"
    NOT_VERIFIED = "NOT_VERIFIED"


class ChangeKind(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"


@dataclass(frozen=True)
class ModuleRoot:
    path: str
    is_directory: bool

    @property
    def pattern(self) -> str:
        return self.path + "/" if self.is_directory else self.path


@dataclass(frozen=True)
class BoundaryModule:
    module_id: str
    roots: tuple[ModuleRoot, ...]
    owner: str
    responsibility: str
    kind: ModuleKind
    allowed_dependencies: tuple[str, ...]
    shared_alias: str | None


@dataclass(frozen=True)
class BoundaryMap:
    baseline: str
    modules: tuple[BoundaryModule, ...]


@dataclass(frozen=True)
class TicketModuleSelection:
    map_sha256: str
    baseline: str
    selected_modules: tuple[str, ...]


@dataclass(frozen=True)
class MapReadResult:
    status: ReadStatus
    boundary_map: BoundaryMap | None = None
    detail: str | None = None


@dataclass(frozen=True)
class TicketSelectionResult:
    status: ReadStatus
    selection: TicketModuleSelection | None = None
    detail: str | None = None


@dataclass(frozen=True)
class BoundaryChange:
    path: str
    kind: ChangeKind
    entry_mode: str


@dataclass(frozen=True)
class EvaluationResult:
    status: EvaluationStatus
    detail: str | None = None
    offending_path: str | None = None


class _RawModule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: StrictStr = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    roots: list[StrictStr] = Field(min_length=1, max_length=32)
    owner: StrictStr = Field(min_length=1, max_length=256)
    responsibility: StrictStr = Field(min_length=1, max_length=512)
    kind: Literal["LIBRARY", "SHARED", "HARNESS", "SCRIPT", "TEST"]
    allowed_dependencies: list[StrictStr] = Field(max_length=128)
    shared_alias: StrictStr | None = Field(default=None, min_length=1, max_length=128)


class _RawMap(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_revision: StrictInt
    scope: Literal["LOCAL_SOURCE_BOUNDARY"]
    baseline: StrictStr = Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
    modules: list[_RawModule] = Field(min_length=1, max_length=256)


class _RawSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_revision: StrictInt
    map_sha256: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")
    baseline: StrictStr = Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
    selected_modules: list[StrictStr] = Field(min_length=1, max_length=256)


_MAP_ADAPTER: TypeAdapter[_RawMap] = TypeAdapter(_RawMap)
_SELECTION_ADAPTER: TypeAdapter[_RawSelection] = TypeAdapter(_RawSelection)
_MODULE_BLOCK = re.compile(
    r"(?ms)^```johnny-module-boundary\r?\n(?P<body>.*?)(?P<close>^```\s*$|\Z)"
)
_MODULE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_SOURCE_SUFFIXES = frozenset(
    {
        ".py", ".pyi", ".ps1", ".psm1", ".psd1", ".ps1xml", ".cmd", ".bat",
        ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
        ".cs", ".fs", ".vb", ".java", ".kt", ".go", ".rs", ".c", ".h",
        ".cc", ".cpp", ".cxx", ".hpp", ".swift", ".rb", ".php", ".pl", ".lua",
    }
)


def _valid_text(value: str) -> bool:
    return bool(value.strip()) and value == value.strip()


def _canonical_root(raw: str, normalize_path: PathNormalizer) -> ModuleRoot | None:
    is_directory = raw.endswith("/")
    candidate = raw[:-1] if is_directory else raw
    normalized = normalize_path(candidate)
    if normalized is None or normalized != candidate:
        return None
    if any(character in candidate for character in ("*", "?", "[", "]")):
        return None
    return ModuleRoot(path=normalized, is_directory=is_directory)


def _roots_overlap(
    left: ModuleRoot, right: ModuleRoot, path_matches: PathMatcher, *, fold: bool = False
) -> bool:
    return path_matches(left.path, right.pattern, fold) or path_matches(
        right.path, left.pattern, fold
    )


def _validate_graph(modules: tuple[BoundaryModule, ...]) -> str | None:
    by_id = {module.module_id: module for module in modules}
    for module in modules:
        if len(set(module.allowed_dependencies)) != len(module.allowed_dependencies):
            return f"module {module.module_id!r} repeats an allowed dependency"
        for dependency_id in module.allowed_dependencies:
            dependency = by_id.get(dependency_id)
            if dependency is None:
                return f"module {module.module_id!r} names unknown dependency {dependency_id!r}"
            if dependency_id == module.module_id:
                return f"module {module.module_id!r} depends on itself"
            if module.kind is ModuleKind.SHARED and dependency.kind is not ModuleKind.SHARED:
                return f"shared module {module.module_id!r} may depend only on SHARED modules"
            if module.kind is ModuleKind.LIBRARY and dependency.kind in {
                ModuleKind.HARNESS,
                ModuleKind.TEST,
            }:
                return f"product module {module.module_id!r} cannot depend on {dependency.kind.value}"

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module_id: str) -> bool:
        if module_id in visiting:
            return False
        if module_id in visited:
            return True
        visiting.add(module_id)
        module = by_id[module_id]
        for dependency_id in module.allowed_dependencies:
            if not visit(dependency_id):
                return False
        visiting.remove(module_id)
        visited.add(module_id)
        return True

    for module in modules:
        if not visit(module.module_id):
            return "allowed dependency graph contains a cycle"
    return None


def parse_boundary_map(
    raw: bytes,
    normalize_path: PathNormalizer,
    path_matches: PathMatcher,
) -> MapReadResult:
    """Parse and validate the one bounded TOML map without coercing input."""

    if type(raw) is not bytes or len(raw) > MAX_MAP_BYTES:
        return MapReadResult(ReadStatus.INVALID, detail="map bytes exceed the bounded input contract")
    try:
        document = _MAP_ADAPTER.validate_python(tomllib.loads(raw.decode("utf-8")), strict=True)
    except (UnicodeDecodeError, tomllib.TOMLDecodeError, ValidationError):
        return MapReadResult(ReadStatus.INVALID, detail="map is not valid schema-revision-1 TOML")
    if document.schema_revision != 1:
        return MapReadResult(ReadStatus.INVALID, detail="map schema revision must be exactly 1")

    if len({module.id for module in document.modules}) != len(document.modules):
        return MapReadResult(ReadStatus.INVALID, detail="module IDs must be unique")
    converted: list[BoundaryModule] = []
    for raw_module in document.modules:
        if not _valid_text(raw_module.owner) or not _valid_text(raw_module.responsibility):
            return MapReadResult(ReadStatus.INVALID, detail=f"module {raw_module.id!r} has a blank or noncanonical owner/responsibility")
        if raw_module.shared_alias is not None and raw_module.kind != "SHARED":
            return MapReadResult(ReadStatus.INVALID, detail=f"only SHARED modules may declare shared_alias ({raw_module.id!r})")
        roots: list[ModuleRoot] = []
        for raw_root in raw_module.roots:
            root = _canonical_root(raw_root, normalize_path)
            if root is None:
                return MapReadResult(ReadStatus.INVALID, detail=f"module {raw_module.id!r} has a noncanonical or wildcard root")
            roots.append(root)
        if len({(root.path, root.is_directory) for root in roots}) != len(roots):
            return MapReadResult(ReadStatus.INVALID, detail=f"module {raw_module.id!r} repeats a root")
        converted.append(
            BoundaryModule(
                module_id=raw_module.id,
                roots=tuple(roots),
                owner=raw_module.owner,
                responsibility=raw_module.responsibility,
                kind=ModuleKind(raw_module.kind),
                allowed_dependencies=tuple(raw_module.allowed_dependencies),
                shared_alias=raw_module.shared_alias,
            )
        )

    all_roots = tuple(
        (module.module_id, root)
        for module in converted
        for root in module.roots
    )
    for index, (left_id, left_root) in enumerate(all_roots):
        for right_id, right_root in all_roots[index + 1 :]:
            if _roots_overlap(left_root, right_root, path_matches) or _roots_overlap(
                left_root, right_root, path_matches, fold=True
            ):
                return MapReadResult(
                    ReadStatus.INVALID,
                    detail=f"module roots overlap or collide by case: {left_id!r}, {right_id!r}",
                )

    aliases = [module.shared_alias.casefold() for module in converted if module.shared_alias]
    if len(set(aliases)) != len(aliases):
        return MapReadResult(ReadStatus.INVALID, detail="shared_alias values must be unique")

    modules = tuple(converted)
    graph_error = _validate_graph(modules)
    if graph_error is not None:
        return MapReadResult(ReadStatus.INVALID, detail=graph_error)
    return MapReadResult(
        ReadStatus.VALID,
        BoundaryMap(baseline=document.baseline, modules=modules),
    )


def parse_ticket_selection(markdown: str) -> TicketSelectionResult:
    """Read an optional pin block; absence preserves legacy-ticket behavior."""

    matches = tuple(_MODULE_BLOCK.finditer(markdown))
    if not matches:
        return TicketSelectionResult(ReadStatus.UNDECLARED)
    if (
        len(matches) != 1
        or not matches[0].group("close")
        or len(matches[0].group("body").encode("utf-8")) > MAX_PIN_BYTES
    ):
        return TicketSelectionResult(ReadStatus.INVALID, detail="ticket must contain one bounded module pin block")
    try:
        raw_selection = _SELECTION_ADAPTER.validate_python(
            tomllib.loads(matches[0].group("body")), strict=True
        )
    except (tomllib.TOMLDecodeError, ValidationError):
        return TicketSelectionResult(ReadStatus.INVALID, detail="ticket module pin block is not valid schema-revision-1 TOML")
    if raw_selection.schema_revision != 1:
        return TicketSelectionResult(ReadStatus.INVALID, detail="ticket schema revision must be exactly 1")
    selected = tuple(raw_selection.selected_modules)
    if any(not _MODULE_ID.fullmatch(module_id) for module_id in selected):
        return TicketSelectionResult(ReadStatus.INVALID, detail="selected module IDs must be canonical IDs")
    if len(set(selected)) != len(selected):
        return TicketSelectionResult(ReadStatus.INVALID, detail="selected module IDs must be unique without case collisions")
    return TicketSelectionResult(
        ReadStatus.VALID,
        TicketModuleSelection(
            map_sha256=raw_selection.map_sha256,
            baseline=raw_selection.baseline,
            selected_modules=selected,
        ),
    )


def map_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_source_path(change: BoundaryChange) -> bool:
    suffix = change.path.rsplit("/", 1)[-1].rsplit(".", 1)
    extension = f".{suffix[-1].casefold()}" if len(suffix) == 2 else ""
    return extension in _SOURCE_SUFFIXES or change.entry_mode == "100755"


def _module_matches_path(
    path: str, module: BoundaryModule, path_matches: PathMatcher, *, fold: bool
) -> bool:
    return any(path_matches(path, root.pattern, fold) for root in module.roots)


def _module_ids_for_import(
    import_name: str,
    modules: tuple[BoundaryModule, ...],
    normalize_path: PathNormalizer,
    path_matches: PathMatcher,
) -> tuple[str, ...]:
    if not import_name or any(not part.isidentifier() for part in import_name.split(".")):
        return ()
    base = import_name.replace(".", "/")
    candidates = (base + ".py", base + "/__init__.py", base)
    found: set[str] = set()
    for candidate in candidates:
        normalized = normalize_path(candidate)
        if normalized is None:
            continue
        for module in modules:
            if _module_matches_path(normalized, module, path_matches, fold=False):
                found.add(module.module_id)
    return tuple(sorted(found))


def _relative_import_name(
    source_path: str, level: int, module: str | None
) -> str | None:
    components = source_path[:-3].split("/")
    package = components[:-1]
    ascend = level - 1
    if ascend > len(package):
        return None
    root = package[: len(package) - ascend]
    if module:
        root.extend(module.split("."))
    return ".".join(root)


def _dynamic_import_present(tree: ast.AST) -> bool:
    importlib_names: set[str] = set()
    import_function_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "importlib":
                    importlib_names.add(alias.asname or "importlib")
        elif isinstance(node, ast.ImportFrom) and node.module == "importlib":
            for alias in node.names:
                if alias.name == "import_module":
                    import_function_names.add(alias.asname or alias.name)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name) and function.id in {
            "__import__", "eval", "exec", *import_function_names
        }:
            return True
        if (
            isinstance(function, ast.Attribute)
            and function.attr == "import_module"
            and isinstance(function.value, ast.Name)
            and function.value.id in importlib_names
        ):
            return True
    return False


def _internal_namespace(import_name: str, modules: tuple[BoundaryModule, ...]) -> bool:
    first = import_name.split(".", 1)[0]
    return any(root.path.split("/", 1)[0] == first for module in modules for root in module.roots)


def _imports_for_node(
    node: ast.Import | ast.ImportFrom,
    source_path: str,
    modules: tuple[BoundaryModule, ...],
    normalize_path: PathNormalizer,
    path_matches: PathMatcher,
) -> tuple[str, ...] | None:
    if isinstance(node, ast.Import):
        names = tuple(alias.name for alias in node.names)
    else:
        base = (
            node.module or ""
            if node.level == 0
            else _relative_import_name(source_path, node.level, node.module)
        )
        if base is None:
            return None
        base_ids = _module_ids_for_import(base, modules, normalize_path, path_matches)
        alias_ids = tuple(
            module_id
            for alias in node.names
            if alias.name != "*"
            for module_id in _module_ids_for_import(
                f"{base}.{alias.name}" if base else alias.name,
                modules,
                normalize_path,
                path_matches,
            )
        )
        resolved_from_import = tuple(sorted(set(alias_ids or base_ids)))
        if resolved_from_import:
            return resolved_from_import
        internal_name = base or ""
        if _internal_namespace(internal_name, modules):
            return None
        return ()
    resolved_imports: list[str] = []
    for name in names:
        module_ids = _module_ids_for_import(name, modules, normalize_path, path_matches)
        if module_ids:
            resolved_imports.extend(module_ids)
        elif _internal_namespace(name, modules):
            return None
    return tuple(sorted(set(resolved_imports)))


def _python_imports(
    module: BoundaryModule,
    path: str,
    source: bytes,
    modules: tuple[BoundaryModule, ...],
    normalize_path: PathNormalizer,
    path_matches: PathMatcher,
) -> str | None:
    try:
        tree = ast.parse(source.decode("utf-8"), filename=path, type_comments=True)
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return "NOT_VERIFIED: changed Python source cannot be parsed as UTF-8 Python"
    if _dynamic_import_present(tree):
        return "NOT_VERIFIED: changed Python source uses unresolved dynamic loading"
    by_id = {entry.module_id: entry for entry in modules}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        imported_ids = _imports_for_node(node, path, modules, normalize_path, path_matches)
        if imported_ids is None:
            return "NOT_VERIFIED: changed Python source has an unresolved internal import"
        for dependency_id in imported_ids:
            target = by_id[dependency_id]
            if target.module_id == module.module_id:
                continue
            if module.kind is ModuleKind.SHARED and target.kind is not ModuleKind.SHARED:
                return "shared module depends on a non-SHARED module"
            if module.kind is ModuleKind.LIBRARY and target.kind in {ModuleKind.HARNESS, ModuleKind.TEST}:
                return f"product module imports {target.kind.value} module {target.module_id!r}"
            if target.module_id not in module.allowed_dependencies:
                return f"internal dependency {module.module_id!r} → {target.module_id!r} is not allowed"
    return None


def evaluate_module_changes(
    boundary_map: BoundaryMap,
    selection: TicketModuleSelection,
    changes: tuple[BoundaryChange, ...],
    candidate_sources: Mapping[str, bytes],
    normalize_path: PathNormalizer,
    path_matches: PathMatcher,
) -> EvaluationResult:
    """Check changed-code ownership and resolvable Python dependency edges."""

    modules = boundary_map.modules
    by_id = {module.module_id: module for module in modules}
    if any(selected not in by_id for selected in selection.selected_modules):
        return EvaluationResult(EvaluationStatus.REFUSED, "selected module ID is absent from the map")
    selected = frozenset(selection.selected_modules)

    for change in sorted(changes, key=lambda item: item.path):
        if not _is_source_path(change):
            continue
        normalized = normalize_path(change.path)
        if normalized is None or normalized != change.path:
            return EvaluationResult(EvaluationStatus.REFUSED, "changed source path is not canonical", change.path)
        owners = tuple(
            module
            for module in modules
            if _module_matches_path(normalized, module, path_matches, fold=False)
        )
        if len(owners) != 1:
            folded = any(
                _module_matches_path(normalized, module, path_matches, fold=True)
                for module in modules
            )
            reason = "changed source path collides by case" if folded else "changed source path has no unique owner"
            return EvaluationResult(EvaluationStatus.REFUSED, reason, normalized)
        owner = owners[0]
        if owner.module_id not in selected:
            return EvaluationResult(EvaluationStatus.REFUSED, f"owning module {owner.module_id!r} is not selected", normalized)
        leaf = normalized.rsplit("/", 1)[-1]
        extension = f".{leaf.rsplit('.', 1)[-1].casefold()}" if "." in leaf else ""
        if extension not in {".py", ".pyi"}:
            return EvaluationResult(
                EvaluationStatus.NOT_VERIFIED,
                f"NOT_VERIFIED: no qualified dependency parser for {extension or 'extensionless'} source",
                normalized,
            )
        if change.kind is ChangeKind.DELETE:
            continue
        source = candidate_sources.get(normalized)
        if source is None:
            return EvaluationResult(
                EvaluationStatus.NOT_VERIFIED,
                "NOT_VERIFIED: candidate Python blob is unavailable",
                normalized,
            )
        import_error = _python_imports(
            owner, normalized, source, modules, normalize_path, path_matches
        )
        if import_error is not None:
            status = (
                EvaluationStatus.NOT_VERIFIED
                if import_error.startswith("NOT_VERIFIED:")
                else EvaluationStatus.REFUSED
            )
            return EvaluationResult(status, import_error, normalized)
    return EvaluationResult(EvaluationStatus.VERIFIED)


__all__ = [
    "BoundaryChange",
    "BoundaryMap",
    "BoundaryModule",
    "ChangeKind",
    "EvaluationResult",
    "EvaluationStatus",
    "MAP_PATH",
    "MapReadResult",
    "ModuleKind",
    "ModuleRoot",
    "ReadStatus",
    "TicketModuleSelection",
    "TicketSelectionResult",
    "evaluate_module_changes",
    "map_digest",
    "parse_boundary_map",
    "parse_ticket_selection",
]
