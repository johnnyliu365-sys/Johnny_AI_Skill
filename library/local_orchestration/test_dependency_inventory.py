"""Pure AST inventory of test consumers from caller-read source text."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class InventoryStatus(StrEnum):
    COMPLETE = "COMPLETE"
    UNRESOLVED = "UNRESOLVED"


class DependencyKind(StrEnum):
    IMPORT = "IMPORT"
    IMPORTLIB = "IMPORTLIB"
    SUBPROCESS = "SUBPROCESS"
    DECLARED_COMMAND = "DECLARED_COMMAND"


UnresolvedReason = Literal[
    "DYNAMIC_IMPORT",
    "RELATIVE_TEST_IMPORT",
    "DYNAMIC_COMMAND",
    "UNSUPPORTED_ENTRY_COMMAND",
    "UNPARSEABLE_SOURCE",
]


@dataclass(frozen=True, slots=True)
class PythonSource:
    source_ref: str
    source_text: str

    def __post_init__(self) -> None:
        if not self.source_ref.strip():
            raise ValueError("source_ref must be non-empty")


@dataclass(frozen=True, slots=True)
class DeclaredTestCommand:
    command_ref: str
    argv: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.command_ref.strip() or not self.argv:
            raise ValueError("command_ref and literal argv must be non-empty")


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    consumer_ref: str
    consumed_ref: str
    kind: DependencyKind


@dataclass(frozen=True, slots=True)
class UnresolvedDependency:
    source_ref: str
    reason: UnresolvedReason


@dataclass(frozen=True, slots=True)
class RetirementInventory:
    test_ref: str
    status: InventoryStatus
    direct_edges: tuple[DependencyEdge, ...]
    transitive_edges: tuple[DependencyEdge, ...]
    unresolved: tuple[UnresolvedDependency, ...]
    retirement_authorized: Literal[False] = False

    @property
    def direct_consumers(self) -> tuple[str, ...]:
        return tuple(sorted({edge.consumer_ref for edge in self.direct_edges}))

    @property
    def transitive_consumers(self) -> tuple[str, ...]:
        return tuple(sorted({edge.consumer_ref for edge in self.transitive_edges}))


_SUBPROCESS_METHODS = {"run", "call", "Popen", "check_call", "check_output"}


def normalize_test_ref(reference: str) -> str:
    """Accept a dotted module ref or repository-relative Python file ref."""

    normalized = reference.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized[:-3].replace("/", ".") if normalized.endswith(".py") else normalized.replace("/", ".")


class PythonTestConsumerInventory:
    """Analyze bounded source text and argv declarations without filesystem effects."""

    def __init__(
        self,
        sources: tuple[PythonSource, ...],
        declared_commands: tuple[DeclaredTestCommand, ...] = (),
    ) -> None:
        source_refs = [source.source_ref for source in sources]
        command_refs = [command.command_ref for command in declared_commands]
        if len(source_refs) != len(set(source_refs)):
            raise ValueError("source_ref values must be unique")
        if len(command_refs) != len(set(command_refs)):
            raise ValueError("command_ref values must be unique")

        edges: set[DependencyEdge] = set()
        unresolved: set[UnresolvedDependency] = set()
        source_modules = {normalize_test_ref(ref) for ref in source_refs}
        for source in sources:
            _scan_source(source, source_modules, edges, unresolved)
        for command in declared_commands:
            targets = _targets_from_argv(command.argv, source_modules)
            if not targets:
                unresolved.add(
                    UnresolvedDependency(command.command_ref, "UNSUPPORTED_ENTRY_COMMAND")
                )
            else:
                edges.update(
                    DependencyEdge(command.command_ref, target, DependencyKind.DECLARED_COMMAND)
                    for target in targets
                )
        self._edges = tuple(sorted(edges, key=_edge_key))
        self._unresolved = tuple(
            sorted(unresolved, key=lambda item: (item.source_ref, item.reason))
        )

    def retirement_inventory(self, test_ref: str) -> RetirementInventory:
        """Return exact graph edges; no result from this method grants retirement."""

        target = normalize_test_ref(test_ref)
        incoming: dict[str, list[DependencyEdge]] = {}
        for edge in self._edges:
            incoming.setdefault(edge.consumed_ref, []).append(edge)

        direct = tuple(sorted(incoming.get(target, ()), key=_edge_key))
        frontier = {normalize_test_ref(edge.consumer_ref) for edge in direct}
        visited = set(frontier)
        transitive: set[DependencyEdge] = set()
        while frontier:
            parent_edges = [edge for ref in frontier for edge in incoming.get(ref, ())]
            parents = {
                normalize_test_ref(edge.consumer_ref)
                for edge in parent_edges
                if normalize_test_ref(edge.consumer_ref) not in visited
            }
            transitive.update(
                edge
                for edge in parent_edges
                if normalize_test_ref(edge.consumer_ref) in parents
            )
            visited.update(parents)
            frontier = parents

        return RetirementInventory(
            test_ref=target,
            status=InventoryStatus.UNRESOLVED if self._unresolved else InventoryStatus.COMPLETE,
            direct_edges=direct,
            transitive_edges=tuple(sorted(transitive, key=_edge_key)),
            unresolved=self._unresolved,
        )


def retirement_inventory(
    test_ref: str,
    sources: tuple[PythonSource, ...],
    declared_commands: tuple[DeclaredTestCommand, ...] = (),
) -> RetirementInventory:
    return PythonTestConsumerInventory(sources, declared_commands).retirement_inventory(test_ref)


def _scan_source(
    source: PythonSource,
    source_modules: set[str],
    edges: set[DependencyEdge],
    unresolved: set[UnresolvedDependency],
) -> None:
    try:
        tree = ast.parse(source.source_text, filename=source.source_ref)
    except SyntaxError:
        unresolved.add(UnresolvedDependency(source.source_ref, "UNPARSEABLE_SOURCE"))
        return

    modules: dict[str, set[str]] = {"importlib": set(), "subprocess": set()}
    functions: dict[str, set[str]] = {"import_module": set(), "subprocess": set()}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name
                if root in modules:
                    modules[root].add(alias.asname or root)
                if root.startswith("tests.") or root in source_modules:
                    edges.add(DependencyEdge(source.source_ref, root, DependencyKind.IMPORT))
                elif root == "tests":
                    unresolved.add(UnresolvedDependency(source.source_ref, "DYNAMIC_IMPORT"))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "importlib":
                functions["import_module"].update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name == "import_module"
                )
            if node.module == "subprocess":
                functions["subprocess"].update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name in _SUBPROCESS_METHODS
                )
            if node.level and normalize_test_ref(source.source_ref).startswith("tests."):
                unresolved.add(UnresolvedDependency(source.source_ref, "RELATIVE_TEST_IMPORT"))
            elif node.level == 0 and node.module == "tests":
                for alias in node.names:
                    if alias.name == "*":
                        unresolved.add(UnresolvedDependency(source.source_ref, "DYNAMIC_IMPORT"))
                    else:
                        edges.add(
                            DependencyEdge(
                                source.source_ref,
                                f"tests.{alias.name}",
                                DependencyKind.IMPORT,
                            )
                        )
            elif node.level == 0 and node.module:
                imported_source: str | None
                if node.module.startswith("tests."):
                    imported_source = node.module
                else:
                    imported_source = next(
                        (
                            target
                            for target in (
                                node.module,
                                *(f"{node.module}.{alias.name}" for alias in node.names),
                            )
                            if target in source_modules
                        ),
                        None,
                    )
                if imported_source is not None:
                    edges.add(
                        DependencyEdge(source.source_ref, imported_source, DependencyKind.IMPORT)
                    )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        called = _dotted_name(node.func)
        if _is_importlib_call(called, modules["importlib"], functions["import_module"]):
            target = _literal_string(node)
            if target is None:
                unresolved.add(UnresolvedDependency(source.source_ref, "DYNAMIC_IMPORT"))
            elif _is_test_module(target) or normalize_test_ref(target) in source_modules:
                edges.add(
                    DependencyEdge(
                        source.source_ref,
                        normalize_test_ref(target),
                        DependencyKind.IMPORTLIB,
                    )
                )
        elif _is_subprocess_call(called, modules["subprocess"], functions["subprocess"]):
            argv = _literal_argv(node)
            targets = _targets_from_argv(argv, source_modules) if argv is not None else None
            if targets is None or _uses_shell(node):
                unresolved.add(UnresolvedDependency(source.source_ref, "DYNAMIC_COMMAND"))
            else:
                edges.update(
                    DependencyEdge(source.source_ref, target, DependencyKind.SUBPROCESS)
                    for target in targets
                )


def _dotted_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else None
    return None


def _is_importlib_call(called: str | None, modules: set[str], functions: set[str]) -> bool:
    return called == "__import__" or called in functions or any(
        called == f"{module}.import_module" for module in modules
    )


def _is_subprocess_call(called: str | None, modules: set[str], functions: set[str]) -> bool:
    return called in functions or any(
        called == f"{module}.{method}"
        for module in modules
        for method in _SUBPROCESS_METHODS
    )


def _literal_string(node: ast.Call) -> str | None:
    if node.args and isinstance(node.args[0], ast.Constant):
        value = node.args[0].value
        return value if isinstance(value, str) else None
    return None


def _literal_argv(node: ast.Call) -> tuple[str, ...] | None:
    if not node.args or not isinstance(node.args[0], (ast.List, ast.Tuple)):
        return None
    values: list[str] = []
    for item in node.args[0].elts:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            values.append(item.value)
        elif _dotted_name(item) == "sys.executable":
            values.append("python")
        else:
            return None
    return tuple(values) if values else None


def _uses_shell(node: ast.Call) -> bool:
    return any(
        keyword.arg == "shell"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in node.keywords
    )


def _targets_from_argv(
    argv: tuple[str, ...] | None,
    source_modules: set[str],
) -> tuple[str, ...] | None:
    if not argv:
        return None
    executable = argv[0].replace("\\", "/").rsplit("/", 1)[-1].lower()
    if executable not in {"python", "python.exe", "py", "py.exe", "pytest", "pytest.exe", "py.test"}:
        return None
    targets: set[str] = set()
    for index, item in enumerate(argv[1:], start=1):
        if item == "-m" and index + 1 < len(argv):
            module = argv[index + 1]
            if module in {"pytest", "unittest"}:
                continue
            if _is_test_module(module) or normalize_test_ref(module) in source_modules:
                targets.add(normalize_test_ref(module))
            elif module.startswith("tests"):
                return None
        elif item.startswith("tests.") or normalize_test_ref(item) in source_modules:
            targets.add(normalize_test_ref(item))
        elif item.replace("\\", "/").startswith("tests/") and item.endswith(".py"):
            targets.add(normalize_test_ref(item))
        elif item.endswith(".py") and normalize_test_ref(item) in source_modules:
            targets.add(normalize_test_ref(item))
        elif "tests." in item or "tests/" in item.replace("\\", "/"):
            return None
    return tuple(sorted(targets)) or None


def _is_test_module(reference: str) -> bool:
    return normalize_test_ref(reference).startswith("tests.")


def _edge_key(edge: DependencyEdge) -> tuple[str, str, str]:
    return edge.consumer_ref, edge.consumed_ref, edge.kind.value


__all__ = [
    "DeclaredTestCommand",
    "DependencyEdge",
    "DependencyKind",
    "InventoryStatus",
    "PythonSource",
    "PythonTestConsumerInventory",
    "RetirementInventory",
    "UnresolvedDependency",
    "retirement_inventory",
]
