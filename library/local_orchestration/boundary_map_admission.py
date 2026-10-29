"""Bind a pinned boundary map to trusted refs before the existing merge gate."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from .boundary_map import (
    BoundaryChange,
    ChangeKind,
    EvaluationStatus,
    MAP_PATH,
    ReadStatus,
    evaluate_module_changes,
    map_digest,
    parse_boundary_map,
    parse_ticket_selection,
)
from .boundary_map_python import observe_python_dependencies

PathNormalizer = Callable[[str], str | None]
PathMatcher = Callable[[str, str, bool], bool]
BlobReader = Callable[[str, str], bytes | None]
AncestorReader = Callable[[str, str], bool]


class BoundaryAdmissionStatus(str, Enum):
    UNDECLARED = "UNDECLARED"
    VERIFIED = "VERIFIED"
    REFUSED = "REFUSED"
    NOT_VERIFIED = "NOT_VERIFIED"


class BoundaryAdmissionFailure(str, Enum):
    MISMATCH = "MISMATCH"
    VIOLATION = "VIOLATION"
    NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True)
class BoundaryAdmissionRequest:
    integration_ref: str
    candidate_ref: str
    merge_base: str
    ticket_path: str
    integration_ticket: bytes
    changes: tuple[BoundaryChange, ...]


@dataclass(frozen=True)
class BoundaryAdmissionResult:
    status: BoundaryAdmissionStatus
    failure: BoundaryAdmissionFailure | None = None
    detail: str | None = None
    offending_path: str | None = None


def _result(
    failure: BoundaryAdmissionFailure,
    detail: str,
    offending_path: str | None = None,
) -> BoundaryAdmissionResult:
    status = (
        BoundaryAdmissionStatus.NOT_VERIFIED
        if failure is BoundaryAdmissionFailure.NOT_VERIFIED
        else BoundaryAdmissionStatus.REFUSED
    )
    return BoundaryAdmissionResult(status, failure, detail, offending_path)


def admit_module_boundary(
    request: BoundaryAdmissionRequest,
    *,
    read_blob: BlobReader,
    is_ancestor: AncestorReader,
    normalize_path: PathNormalizer,
    path_matches: PathMatcher,
) -> BoundaryAdmissionResult:
    """Evaluate one integration-pinned map using the gate's bounded read callbacks."""

    if type(request) is not BoundaryAdmissionRequest:
        return _result(BoundaryAdmissionFailure.NOT_VERIFIED, "NOT_VERIFIED: invalid admission request")
    if type(request.integration_ticket) is not bytes:
        return _result(BoundaryAdmissionFailure.NOT_VERIFIED, "NOT_VERIFIED: integration ticket is not bytes", request.ticket_path)

    selection_result = parse_ticket_selection(
        request.integration_ticket.decode("utf-8", errors="replace")
    )
    if selection_result.status is ReadStatus.UNDECLARED:
        return BoundaryAdmissionResult(BoundaryAdmissionStatus.UNDECLARED)
    if selection_result.status is not ReadStatus.VALID or selection_result.selection is None:
        return _result(
            BoundaryAdmissionFailure.NOT_VERIFIED,
            selection_result.detail or "NOT_VERIFIED: ticket module pin is invalid",
            request.ticket_path,
        )
    selection = selection_result.selection

    map_bytes = read_blob(request.integration_ref, MAP_PATH)
    if map_bytes is None:
        return _result(
            BoundaryAdmissionFailure.NOT_VERIFIED,
            "NOT_VERIFIED: integration branch has no readable boundary map",
            MAP_PATH,
        )
    map_result = parse_boundary_map(map_bytes, normalize_path, path_matches)
    if map_result.status is not ReadStatus.VALID or map_result.boundary_map is None:
        return _result(
            BoundaryAdmissionFailure.NOT_VERIFIED,
            map_result.detail or "NOT_VERIFIED: integration boundary map is invalid",
            MAP_PATH,
        )
    if map_digest(map_bytes) != selection.map_sha256:
        return _result(
            BoundaryAdmissionFailure.MISMATCH,
            "ticket map digest does not match the integration-branch map",
            MAP_PATH,
        )
    if map_result.boundary_map.baseline != selection.baseline:
        return _result(
            BoundaryAdmissionFailure.MISMATCH,
            "ticket baseline does not match the integration-branch map",
            request.ticket_path,
        )
    if not is_ancestor(selection.baseline, request.integration_ref) or not is_ancestor(
        selection.baseline, request.merge_base
    ):
        return _result(
            BoundaryAdmissionFailure.MISMATCH,
            "pinned module baseline is not an ancestor of the reviewed source base",
            request.ticket_path,
        )

    normalized_changes = tuple(
        (normalize_path(change.path), change) for change in request.changes
    )
    if any(
        normalized is not None and normalized.casefold() == MAP_PATH.casefold()
        for normalized, _ in normalized_changes
    ):
        return _result(
            BoundaryAdmissionFailure.VIOLATION,
            "candidate cannot replace the integration-branch map that judges it",
            MAP_PATH,
        )
    ticket_changed = any(
        normalized is not None
        and normalized.casefold() == request.ticket_path.casefold()
        for normalized, _ in normalized_changes
    )
    if ticket_changed:
        candidate_ticket = read_blob(request.candidate_ref, request.ticket_path)
        candidate_selection = (
            parse_ticket_selection(candidate_ticket.decode("utf-8", errors="replace"))
            if candidate_ticket is not None
            else None
        )
        if (
            candidate_selection is None
            or candidate_selection.status is not ReadStatus.VALID
            or candidate_selection.selection != selection
        ):
            return _result(
                BoundaryAdmissionFailure.MISMATCH,
                "candidate changed or removed the integration-pinned module selection",
                request.ticket_path,
            )

    observations = {}
    for change in request.changes:
        if change.kind is ChangeKind.DELETE:
            continue
        leaf = change.path.rsplit("/", 1)[-1]
        extension = f".{leaf.rsplit('.', 1)[-1].casefold()}" if "." in leaf else ""
        if extension not in {".py", ".pyi"}:
            continue
        source = read_blob(request.candidate_ref, change.path)
        if source is not None:
            observations[change.path] = observe_python_dependencies(change.path, source)

    evaluation = evaluate_module_changes(
        map_result.boundary_map,
        selection,
        request.changes,
        observations,
        normalize_path,
        path_matches,
    )
    if evaluation.status is EvaluationStatus.VERIFIED:
        return BoundaryAdmissionResult(BoundaryAdmissionStatus.VERIFIED)
    if evaluation.status is EvaluationStatus.NOT_VERIFIED:
        return _result(
            BoundaryAdmissionFailure.NOT_VERIFIED,
            evaluation.detail or "NOT_VERIFIED: source dependency evaluation failed",
            evaluation.offending_path,
        )
    return _result(
        BoundaryAdmissionFailure.VIOLATION,
        evaluation.detail or "module boundary violation",
        evaluation.offending_path,
    )


__all__ = [
    "BoundaryAdmissionFailure",
    "BoundaryAdmissionRequest",
    "BoundaryAdmissionResult",
    "BoundaryAdmissionStatus",
    "admit_module_boundary",
]
