from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from library.local_orchestration.boundary_map import (
    BoundaryChange,
    ChangeKind,
    EvaluationStatus,
    TicketModuleSelection,
    evaluate_module_changes,
    map_digest,
    parse_boundary_map,
)
from library.local_orchestration.boundary_map_admission import (
    BoundaryAdmissionFailure,
    BoundaryAdmissionRequest,
    BoundaryAdmissionResult,
    BoundaryAdmissionStatus,
    admit_module_boundary,
)
from library.local_orchestration.boundary_map_python import observe_python_dependencies
from library.local_orchestration.document_mutation_gate import (
    normalize_change_path,
    path_matches_entry,
)

_BASELINE = "a" * 40
_TICKET_PATH = "modules/tickets/38b.md"


def _map_bytes() -> bytes:
    return (
        "schema_revision = 1\n"
        'scope = "LOCAL_SOURCE_BOUNDARY"\n'
        f'baseline = "{_BASELINE}"\n\n'
        '[[modules]]\nid = "feature"\nroots = ["src/feature.py"]\n'
        'owner = "feature-team"\nresponsibility = "Own the feature entry point."\n'
        'kind = "LIBRARY"\nallowed_dependencies = ["shared"]\n\n'
        '[[modules]]\nid = "shared"\nroots = ["src/shared.py"]\n'
        'owner = "platform-team"\nresponsibility = "Provide shared feature contracts."\n'
        'kind = "SHARED"\nallowed_dependencies = []\n'
    ).encode("utf-8")


def _ticket(map_bytes: bytes, *, selected: tuple[str, ...] = ("feature",)) -> bytes:
    selected_text = ", ".join(f'"{module_id}"' for module_id in selected)
    return (
        "```johnny-module-boundary\n"
        "schema_revision = 1\n"
        f'map_sha256 = "{map_digest(map_bytes)}"\n'
        f'baseline = "{_BASELINE}"\n'
        f"selected_modules = [{selected_text}]\n"
        "```\n"
    ).encode("utf-8")


def _request(
    ticket: bytes,
    changes: tuple[BoundaryChange, ...] = (
        BoundaryChange("src/feature.py", ChangeKind.MODIFY, "100644"),
    ),
) -> BoundaryAdmissionRequest:
    return BoundaryAdmissionRequest(
        integration_ref="main",
        candidate_ref="candidate",
        merge_base=_BASELINE,
        ticket_path=_TICKET_PATH,
        integration_ticket=ticket,
        changes=changes,
    )


def _run_admission(
    request: BoundaryAdmissionRequest,
    blobs: dict[tuple[str, str], bytes],
    *,
    ancestor: Callable[[str, str], bool] | None = None,
) -> tuple[
    BoundaryAdmissionResult,
    list[tuple[str, str]],
    list[tuple[str, str]],
]:
    reads: list[tuple[str, str]] = []
    ancestry: list[tuple[str, str]] = []

    def read_blob(reference: str, path: str) -> bytes | None:
        reads.append((reference, path))
        return blobs.get((reference, path))

    def is_ancestor(base: str, reference: str) -> bool:
        ancestry.append((base, reference))
        return ancestor(base, reference) if ancestor is not None else base == _BASELINE

    result = admit_module_boundary(
        request,
        read_blob=read_blob,
        is_ancestor=is_ancestor,
        normalize_path=normalize_change_path,
        path_matches=path_matches_entry,
    )
    return result, reads, ancestry


def test_admission_reads_trusted_map_and_candidate_blobs_through_gate_callbacks() -> None:
    boundary_map = _map_bytes()
    ticket = _ticket(boundary_map)
    request = _request(ticket)
    result, reads, ancestry = _run_admission(
        request,
        {
            ("main", "shared/BOUNDARY_MAP.toml"): boundary_map,
            ("candidate", "src/feature.py"): b"from src.shared import VALUE\n",
        },
    )

    assert result.status is BoundaryAdmissionStatus.VERIFIED
    assert reads == [
        ("main", "shared/BOUNDARY_MAP.toml"),
        ("candidate", "src/feature.py"),
    ]
    assert ancestry == [(_BASELINE, "main"), (_BASELINE, _BASELINE)]


def test_repository_map_covers_the_implemented_admission_source_graph() -> None:
    repository = Path(__file__).resolve().parents[1]
    map_bytes = (repository / "shared/BOUNDARY_MAP.toml").read_bytes()
    parsed = parse_boundary_map(map_bytes, normalize_change_path, path_matches_entry)
    assert parsed.status.value == "VALID", parsed.detail
    assert parsed.boundary_map is not None
    boundary_map = parsed.boundary_map
    changed_paths = (
        "library/local_orchestration/boundary_map.py",
        "library/local_orchestration/boundary_map_python.py",
        "library/local_orchestration/boundary_map_admission.py",
        "library/local_orchestration/document_mutation_gate.py",
        "tests/test_boundary_map.py",
        "tests/test_boundary_map_admission.py",
        "tests/test_document_mutation_gate.py",
    )
    changes = tuple(
        BoundaryChange(path, ChangeKind.MODIFY, "100644") for path in changed_paths
    )
    observations = {
        path: observe_python_dependencies(path, (repository / path).read_bytes())
        for path in changed_paths
    }
    selection = TicketModuleSelection(
        map_sha256=map_digest(map_bytes),
        baseline=boundary_map.baseline,
        selected_modules=tuple(module.module_id for module in boundary_map.modules),
    )

    result = evaluate_module_changes(
        boundary_map,
        selection,
        changes,
        observations,
        normalize_change_path,
        path_matches_entry,
    )

    assert result.status is EvaluationStatus.VERIFIED, result


def test_unpinned_legacy_ticket_does_not_read_map_or_candidate() -> None:
    request = _request(b"# no module boundary pin\n")
    result, reads, ancestry = _run_admission(request, {})

    assert result.status is BoundaryAdmissionStatus.UNDECLARED
    assert reads == []
    assert ancestry == []


def test_candidate_map_replacement_is_refused_before_candidate_reads() -> None:
    boundary_map = _map_bytes()
    request = _request(
        _ticket(boundary_map),
        changes=(BoundaryChange("shared/BOUNDARY_MAP.toml", ChangeKind.MODIFY, "100644"),),
    )
    result, reads, ancestry = _run_admission(
        request, {("main", "shared/BOUNDARY_MAP.toml"): boundary_map}
    )

    assert result.status is BoundaryAdmissionStatus.REFUSED
    assert result.failure is BoundaryAdmissionFailure.VIOLATION
    assert reads == [("main", "shared/BOUNDARY_MAP.toml")]
    assert ancestry == [(_BASELINE, "main"), (_BASELINE, _BASELINE)]


def test_candidate_ticket_pin_rewrite_is_refused_before_source_observation() -> None:
    boundary_map = _map_bytes()
    ticket = _ticket(boundary_map)
    request = _request(
        ticket,
        changes=(
            BoundaryChange(_TICKET_PATH, ChangeKind.MODIFY, "100644"),
            BoundaryChange("src/feature.py", ChangeKind.MODIFY, "100644"),
        ),
    )
    result, reads, _ = _run_admission(
        request,
        {
            ("main", "shared/BOUNDARY_MAP.toml"): boundary_map,
            ("candidate", _TICKET_PATH): _ticket(boundary_map, selected=("feature", "shared")),
        },
    )

    assert result.status is BoundaryAdmissionStatus.REFUSED
    assert result.failure is BoundaryAdmissionFailure.MISMATCH
    assert reads == [
        ("main", "shared/BOUNDARY_MAP.toml"),
        ("candidate", _TICKET_PATH),
    ]


@pytest.mark.parametrize(
    "failure",
    ("missing-map", "bad-ancestry", "unreadable-source"),
)
def test_unverified_admission_inputs_fail_closed(failure: str) -> None:
    boundary_map = _map_bytes()
    request = _request(_ticket(boundary_map))
    blobs: dict[tuple[str, str], bytes] = {}
    ancestor: Callable[[str, str], bool] | None = None
    if failure != "missing-map":
        blobs[("main", "shared/BOUNDARY_MAP.toml")] = boundary_map
    if failure == "bad-ancestry":
        def reject_merge_base(base: str, reference: str) -> bool:
            return reference == "main"

        ancestor = reject_merge_base
    if failure == "unreadable-source":
        def accept_ancestry(base: str, reference: str) -> bool:
            return True

        ancestor = accept_ancestry

    result, _, _ = _run_admission(request, blobs, ancestor=ancestor)

    if failure == "bad-ancestry":
        assert result.status is BoundaryAdmissionStatus.REFUSED
        assert result.failure is BoundaryAdmissionFailure.MISMATCH
    else:
        assert result.status is BoundaryAdmissionStatus.NOT_VERIFIED
        assert result.failure is BoundaryAdmissionFailure.NOT_VERIFIED
