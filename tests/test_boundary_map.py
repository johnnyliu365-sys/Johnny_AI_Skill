from __future__ import annotations

from dataclasses import replace

import pytest

from collections.abc import Callable

from library.local_orchestration.boundary_map import (
    BoundaryChange,
    BoundaryMap,
    ChangeKind,
    DependencyObservationStatus,
    EvaluationResult,
    EvaluationStatus,
    MapReadResult,
    ReadStatus,
    TicketModuleSelection,
    evaluate_module_changes,
    map_digest,
    parse_boundary_map,
    parse_ticket_selection,
)
from library.local_orchestration.boundary_map_python import observe_python_dependencies
from library.local_orchestration.document_mutation_gate import (
    normalize_change_path,
    path_matches_entry,
)

_BASELINE = "a" * 40


def _module(
    module_id: str,
    root: str,
    kind: str,
    dependencies: tuple[str, ...] = (),
    *,
    alias: str | None = None,
    owner: str = "team",
    responsibility: str = "one clear responsibility",
) -> str:
    lines = [
        "[[modules]]",
        f'id = "{module_id}"',
        f'roots = ["{root}"]',
        f'owner = "{owner}"',
        f'responsibility = "{responsibility}"',
        f'kind = "{kind}"',
        "allowed_dependencies = ["
        + ", ".join(f'"{dependency}"' for dependency in dependencies)
        + "]",
    ]
    if alias is not None:
        lines.append(f'shared_alias = "{alias}"')
    return "\n".join(lines)


def _map_text(*modules: str) -> str:
    header = (
        "schema_revision = 1\n"
        'scope = "LOCAL_SOURCE_BOUNDARY"\n'
        f'baseline = "{_BASELINE}"\n\n'
    )
    return header + "\n\n".join(modules) + "\n"


def _valid_text() -> str:
    return _map_text(
        _module("feature", "src/feature.py", "LIBRARY", ("shared",)),
        _module("shared", "src/shared.py", "SHARED", alias="term-normalizer"),
        _module("peer", "src/peer.py", "LIBRARY"),
        _module("contract_tests", "tests/test_feature.py", "TEST", ("feature",)),
        _module("shell_entry", "scripts/run.ps1", "SCRIPT"),
    )


def _read(text: str) -> MapReadResult:
    return parse_boundary_map(
        text.encode("utf-8"), normalize_change_path, path_matches_entry
    )


def _valid_map() -> BoundaryMap:
    result = _read(_valid_text())
    assert result.status is ReadStatus.VALID
    assert result.boundary_map is not None
    return result.boundary_map


def _selection(*module_ids: str) -> TicketModuleSelection:
    raw = _valid_text().encode("utf-8")
    return TicketModuleSelection(
        map_sha256=map_digest(raw),
        baseline=_BASELINE,
        selected_modules=module_ids,
    )


def _evaluate(
    path: str,
    source: bytes | None,
    *,
    selected: tuple[str, ...] = ("feature", "shared"),
    kind: ChangeKind = ChangeKind.MODIFY,
    entry_mode: str = "100644",
) -> EvaluationResult:
    sources = (
        {}
        if source is None
        else {path: observe_python_dependencies(path, source)}
    )
    return evaluate_module_changes(
        _valid_map(),
        _selection(*selected),
        (BoundaryChange(path, kind, entry_mode),),
        sources,
        normalize_change_path,
        path_matches_entry,
    )


def test_schema_one_map_builds_a_typed_finite_module_set() -> None:
    result = _read(_valid_text())
    assert result.status is ReadStatus.VALID
    assert result.boundary_map is not None
    assert result.boundary_map.baseline == _BASELINE
    assert result.boundary_map.modules[1].shared_alias == "term-normalizer"


@pytest.mark.parametrize(
    "mutation",
    (
        lambda text: text.replace("schema_revision = 1", "schema_revision = true"),
        lambda text: text.replace('scope = "LOCAL_SOURCE_BOUNDARY"', 'scope = "OTHER"'),
        lambda text: text.replace('owner = "team"', 'owner = "   "', 1),
        lambda text: text.replace('responsibility = "one clear responsibility"', 'responsibility = " "', 1),
        lambda text: text.replace('allowed_dependencies = ["shared"]', 'allowed_dependencies = ["missing"]'),
        lambda text: text.replace('roots = ["src/feature.py"]', 'roots = ["src/*.py"]'),
        lambda text: text.replace('roots = ["src/feature.py"]', 'roots = ["src/../feature.py"]'),
        lambda text: text.replace('kind = "LIBRARY"', 'kind = "UNKNOWN"', 1),
    ),
)
def test_schema_type_owner_dependency_and_root_errors_refuse(
    mutation: Callable[[str], str],
) -> None:
    assert _read(mutation(_valid_text())).status is ReadStatus.INVALID


def test_unknown_top_level_key_is_rejected() -> None:
    assert _read(_valid_text() + "unexpected = true\n").status is ReadStatus.INVALID


def test_duplicate_and_case_colliding_roots_refuse() -> None:
    repeated = _map_text(
        _module("feature", "src/feature.py", "LIBRARY"),
        _module("other", "src/feature.py", "LIBRARY"),
    )
    case_collision = _map_text(
        _module("feature", "src/Feature.py", "LIBRARY"),
        _module("other", "src/feature.py", "LIBRARY"),
    )
    assert _read(repeated).status is ReadStatus.INVALID
    assert _read(case_collision).status is ReadStatus.INVALID


def test_overlapping_roots_and_duplicate_module_ids_refuse() -> None:
    overlap = _map_text(
        _module("feature", "src/", "LIBRARY"),
        _module("other", "src/feature.py", "LIBRARY"),
    )
    duplicate_ids = _map_text(
        _module("feature", "src/one.py", "LIBRARY"),
        _module("feature", "src/two.py", "LIBRARY"),
    )
    assert _read(overlap).status is ReadStatus.INVALID
    assert _read(duplicate_ids).status is ReadStatus.INVALID


def test_shared_module_cannot_depend_on_product_or_test_modules() -> None:
    text = _map_text(
        _module("feature", "src/feature.py", "LIBRARY"),
        _module("shared", "src/shared.py", "SHARED", ("feature",), alias="common"),
    )
    assert _read(text).status is ReadStatus.INVALID


def test_dependency_cycle_refuses() -> None:
    text = _map_text(
        _module("first", "src/first.py", "LIBRARY", ("second",)),
        _module("second", "src/second.py", "LIBRARY", ("first",)),
    )
    assert _read(text).status is ReadStatus.INVALID


def test_missing_ticket_pin_is_legacy_but_malformed_pin_is_not_verified() -> None:
    assert parse_ticket_selection("# legacy ticket\n").status is ReadStatus.UNDECLARED
    malformed = "```johnny-module-boundary\nschema_revision = 1\nunknown = true\n```"
    assert parse_ticket_selection(malformed).status is ReadStatus.INVALID
    unclosed = "```johnny-module-boundary\nschema_revision = 1\n"
    assert parse_ticket_selection(unclosed).status is ReadStatus.INVALID
    selection = _selection("feature")
    valid = (
        "```johnny-module-boundary\n"
        f'schema_revision = 1\nmap_sha256 = "{selection.map_sha256}"\n'
        f'baseline = "{_BASELINE}"\nselected_modules = ["feature"]\n```\n'
    )
    assert parse_ticket_selection(valid + unclosed).status is ReadStatus.INVALID


def test_ticket_selection_is_strict_unique_and_bounded() -> None:
    valid = (
        "```johnny-module-boundary\n"
        'schema_revision = 1\nmap_sha256 = "' + "b" * 64 + '"\n'
        f'baseline = "{_BASELINE}"\nselected_modules = ["feature", "shared"]\n```'
    )
    parsed = parse_ticket_selection(valid)
    assert parsed.status is ReadStatus.VALID
    assert parsed.selection is not None
    assert parsed.selection.selected_modules == ("feature", "shared")
    assert parse_ticket_selection(valid + valid).status is ReadStatus.INVALID
    assert parse_ticket_selection(valid.replace('["feature", "shared"]', '["feature", "feature"]')).status is ReadStatus.INVALID


def test_changed_python_owner_must_be_selected_and_unique() -> None:
    assert _evaluate("src/feature.py", b"value = 1\n").status is EvaluationStatus.VERIFIED
    assert _evaluate(
        "src/feature.py", b"value = 1\n", selected=("shared",)
    ).status is EvaluationStatus.REFUSED
    assert _evaluate("src/unowned.py", b"value = 1\n").status is EvaluationStatus.REFUSED
    assert _evaluate("src/Feature.py", b"value = 1\n").status is EvaluationStatus.REFUSED


def test_python_ast_imports_allow_only_declared_internal_edges() -> None:
    allowed = _evaluate("src/feature.py", b"import src.shared\n")
    denied = _evaluate("src/feature.py", b"import tests.test_feature\n")
    undeclared = _evaluate("src/feature.py", b"import src.peer\n")
    external = _evaluate("src/feature.py", b"import json\nfrom pathlib import Path\n")
    assert allowed.status is EvaluationStatus.VERIFIED
    assert denied.status is EvaluationStatus.REFUSED
    assert undeclared.status is EvaluationStatus.REFUSED
    assert "not allowed" in (undeclared.detail or "")
    assert external.status is EvaluationStatus.VERIFIED


def test_relative_python_imports_use_the_same_declared_dependency_edge() -> None:
    result = _evaluate("src/feature.py", b"from . import shared\n")
    assert result.status is EvaluationStatus.VERIFIED


@pytest.mark.parametrize(
    "source",
    (
        b"from ..peer import Thing\n",
        b"from src import shared, unowned\n",
        b"from builtins import __import__ as load_module\nload_module('src.shared')\n",
    ),
    ids=("relative-import-escapes-top-level", "mixed-resolved-and-unknown", "aliased-builtin-loader"),
)
def test_unresolved_or_escaping_python_imports_are_not_verified(source: bytes) -> None:
    result = _evaluate("src/feature.py", source)
    assert result.status is EvaluationStatus.NOT_VERIFIED
    assert result.detail is not None and result.detail.startswith("NOT_VERIFIED:")


def test_ast_observation_is_typed_and_fails_closed_for_builtin_aliases() -> None:
    observation = observe_python_dependencies(
        "src/feature.py",
        b"from builtins import __import__ as load_module\nload_module('src.shared')\n",
    )
    assert observation.status is DependencyObservationStatus.NOT_VERIFIED
    assert observation.imports == ()
    assert observation.detail is not None


def test_from_mapped_module_importing_a_symbol_remains_verified() -> None:
    result = _evaluate("src/feature.py", b"from src.shared import normalize\n")
    assert result.status is EvaluationStatus.VERIFIED


@pytest.mark.parametrize(
    "source",
    (
        b"import importlib as il\nversion_name = il.__name__\n",
        b"import importlib as il\nversion_name = getattr(il, '__name__')\n",
    ),
    ids=("ordinary-module-attribute", "ordinary-getattr-attribute"),
)
def test_non_loader_importlib_attributes_remain_verified(source: bytes) -> None:
    result = _evaluate("src/feature.py", source)
    assert result.status is EvaluationStatus.VERIFIED


def test_dynamic_import_syntax_and_unreadable_python_are_not_verified() -> None:
    dynamic = _evaluate("src/feature.py", b"module = __import__('src.shared')\n")
    syntax = _evaluate("src/feature.py", b"def incomplete(:\n")
    missing = _evaluate("src/feature.py", None)
    assert dynamic.status is EvaluationStatus.NOT_VERIFIED
    assert syntax.status is EvaluationStatus.NOT_VERIFIED
    assert missing.status is EvaluationStatus.NOT_VERIFIED


def test_unsupported_script_parser_is_not_reported_as_a_pass() -> None:
    result = _evaluate("scripts/run.ps1", b"Write-Output 'hello'\n", selected=("shell_entry",))
    assert result.status is EvaluationStatus.NOT_VERIFIED
    assert result.detail is not None and result.detail.startswith("NOT_VERIFIED:")


def test_deleting_owned_python_needs_no_candidate_source_blob() -> None:
    result = _evaluate(
        "src/feature.py", None, kind=ChangeKind.DELETE
    )
    assert result.status is EvaluationStatus.VERIFIED


def test_map_and_ticket_pins_are_immutable_values() -> None:
    selection = _selection("feature", "shared")
    assert replace(selection, map_sha256="0" * 64) != selection
