"""Type-only contracts for the isolated committed-mainline source fixture."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Literal, NoReturn, Protocol, Self, TypeAlias

from pydantic import BeforeValidator, BaseModel, ConfigDict, Field, ValidationError, model_validator

from library.local_orchestration.project_authority.contracts import (
    GitObservation,
    GitObservationSource,
)
from library.workflow_router.contracts import (
    EvidenceDigest,
    OpaqueMetadataId,
    ProjectId,
    RequirementChangeId,
    RequirementId,
    RevisionDigest,
)
from library.workflow_router.git_handoff_contracts import GitBlobReadStatus
from library.workflow_router.mainline_projection import (
    MainlineAdmissionRef,
    MainlineEvidenceRef,
    MainlineMetadataRef,
    MainlineProjection,
    MainlineProjectionRequest,
    MainlineRef,
    MainlineTicket,
    MainlineTicketRef,
    MainlineTicketStatus,
    project_mainline_tickets,
)
from library.workflow_router.role_supervision_contracts import SpecReference
from library.workflow_router.target_document_contracts import FeatureSlug


_WINDOWS_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")


@dataclass(frozen=True, slots=True)
class TargetRelativePath:
    """A canonical slash-separated relative path with no traversal segments."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("path value must be a string")
        if not self.value or self.value.startswith("/"):
            raise ValueError("path must be non-empty and relative")
        if "\\" in self.value or _WINDOWS_DRIVE_PREFIX.match(self.value) is not None:
            raise ValueError("path must use canonical relative separators")
        segments = self.value.split("/")
        if any(segment in ("", ".", "..") for segment in segments):
            raise ValueError("path cannot contain empty or traversal segments")
        if any(unicodedata.category(character) == "Cc" for character in self.value):
            raise ValueError("path cannot contain control characters")


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=False,
    )


class RawGitBlobReadResult(_StrictModel):
    """A single exact Git blob response; bytes exist only at the read boundary."""

    status: GitBlobReadStatus
    payload: bytes | None = None

    @model_validator(mode="after")
    def payload_matches_status(self) -> Self:
        if self.status is GitBlobReadStatus.FOUND:
            if self.payload is None:
                raise ValueError("found blob reads require raw bytes")
        elif self.payload is not None:
            raise ValueError("non-found blob reads cannot carry a payload")
        return self


class MainlineSourcePort(Protocol):
    """Read one path's raw bytes from the exact synthetic observation commit."""

    def read_blob(
        self,
        observation: GitObservation,
        artifact_ref: TargetRelativePath,
    ) -> RawGitBlobReadResult: ...


class MainlineSourceFailure(str, Enum):
    INDEX_NOT_FOUND = "INDEX_NOT_FOUND"
    INDEX_READ_UNAVAILABLE = "INDEX_READ_UNAVAILABLE"
    INDEX_SCHEMA_INVALID = "INDEX_SCHEMA_INVALID"
    INDEX_BINDING_MISMATCH = "INDEX_BINDING_MISMATCH"
    LEAF_NOT_FOUND = "LEAF_NOT_FOUND"
    LEAF_READ_UNAVAILABLE = "LEAF_READ_UNAVAILABLE"
    LEAF_DIGEST_MISMATCH = "LEAF_DIGEST_MISMATCH"
    PROJECTION_INVALID = "PROJECTION_INVALID"


class MainlineSourceScope(str, Enum):
    FIXTURE_ONLY = "FIXTURE_ONLY"


class MainlineSourceRequest(_StrictModel):
    """A fixture-only request bound to one normalized synthetic observation."""

    project_id: ProjectId
    feature: FeatureSlug
    observation: GitObservation

    @model_validator(mode="after")
    def observation_is_synthetic_worktree_head(self) -> Self:
        if self.observation.source is not GitObservationSource.WORKTREE_HEAD:
            raise ValueError("fixture requests require a synthetic WORKTREE_HEAD observation")
        return self


class MainlineSourceResult(_StrictModel):
    """Candidate metadata or one finite failure, always marked fixture-only."""

    scope: MainlineSourceScope = MainlineSourceScope.FIXTURE_ONLY
    projection: MainlineProjection | None = None
    failure: MainlineSourceFailure | None = None

    @model_validator(mode="after")
    def result_has_exactly_one_outcome(self) -> Self:
        if (self.projection is None) == (self.failure is None):
            raise ValueError("source result requires exactly one projection or failure")
        if self.scope is not MainlineSourceScope.FIXTURE_ONLY:
            raise ValueError("mainline source results are fixture-only")
        return self


_IndexRevisionSha: TypeAlias = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
_TicketStatus: TypeAlias = Literal["planned", "admitted", "in_progress", "waiting", "completed"]
_TargetRelativePathInput: TypeAlias = Annotated[
    TargetRelativePath,
    BeforeValidator(lambda value: _path_from_wire(value)),
]


def _path_from_wire(value: object) -> TargetRelativePath:
    if type(value) is not str:
        raise ValueError("artifact paths must be JSON strings")
    return TargetRelativePath(value)


class _BindingWireBase(_StrictModel):
    artifact_ref: _TargetRelativePathInput
    revision_sha: _IndexRevisionSha


class _ContextBindingWire(_BindingWireBase):
    kind: Literal["context"]
    identity: OpaqueMetadataId


class _PrdBindingWire(_BindingWireBase):
    kind: Literal["prd"]
    identity: RequirementId


class _ChangeBindingWire(_BindingWireBase):
    kind: Literal["change"]
    identity: RequirementChangeId


class _SpecBindingWire(_BindingWireBase):
    kind: Literal["spec"]
    identity: SpecReference


_BindingWire: TypeAlias = Annotated[
    _ContextBindingWire | _PrdBindingWire | _ChangeBindingWire | _SpecBindingWire,
    Field(discriminator="kind"),
]


class _IndexTicketWire(_StrictModel):
    ticket_ref: MainlineTicketRef
    ticket_revision: RevisionDigest
    leaf_ref: _TargetRelativePathInput
    leaf_digest: EvidenceDigest
    required: bool
    status: _TicketStatus
    depends_on: list[MainlineTicketRef]
    admission_ref: MainlineAdmissionRef | None
    evidence_refs: list[MainlineEvidenceRef]


class _MainlineIndexWire(_StrictModel):
    schema_id: Literal["mainline-index/revision-01"]
    project_id: ProjectId
    feature: FeatureSlug
    mainline_ref: MainlineRef
    objective_ref: MainlineMetadataRef
    owner_ref: MainlineMetadataRef
    handoff_ref: MainlineMetadataRef
    bindings: list[_BindingWire]
    tickets: list[_IndexTicketWire] = Field(min_length=1)


class _TicketLeafWire(_StrictModel):
    schema_id: Literal["mainline-ticket/revision-01"]
    ticket_ref: MainlineTicketRef
    ticket_revision: RevisionDigest
    status: _TicketStatus
    depends_on: list[MainlineTicketRef]
    admission_ref: MainlineAdmissionRef | None
    evidence_refs: list[MainlineEvidenceRef]


class _InvalidFence(ValueError):
    """A Markdown source does not have exactly one correctly placed JSON fence."""


class _DuplicateJsonKey(ValueError):
    """A JSON object repeats a key at any nesting level."""


def _next_nonempty_line(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index
    return None


def _extract_contract_json(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    heading_indices = [index for index, line in enumerate(lines) if line == heading]
    json_open_indices = [index for index, line in enumerate(lines) if line == "```json"]
    if len(heading_indices) != 1 or len(json_open_indices) != 1:
        raise _InvalidFence

    heading_index = heading_indices[0]
    open_index = json_open_indices[0]
    next_content_index = _next_nonempty_line(lines, heading_index + 1)
    if next_content_index != open_index:
        raise _InvalidFence

    close_index = _next_nonempty_line(lines, open_index + 1)
    while close_index is not None and lines[close_index] != "```":
        close_index = _next_nonempty_line(lines, close_index + 1)
    if close_index is None:
        raise _InvalidFence
    return "\n".join(lines[open_index + 1 : close_index])


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise ValueError(f"non-JSON constant {value!r}")


def _load_json_object(text: str) -> dict[str, object]:
    decoded: object = json.loads(
        text,
        object_pairs_hook=_unique_json_object,
        parse_constant=_reject_json_constant,
    )
    if type(decoded) is not dict:
        raise ValueError("contract JSON must be an object")

    result: dict[str, object] = {}
    for raw_key, raw_value in decoded.items():
        key: object = raw_key
        value: object = raw_value
        if not isinstance(key, str):
            raise ValueError("contract object keys must be strings")
        result[key] = value
    return result


def _parse_index(markdown_bytes: bytes) -> _MainlineIndexWire:
    markdown = markdown_bytes.decode("utf-8", errors="strict")
    fenced_json = _extract_contract_json(markdown, "## Mainline source contract")
    decoded = _load_json_object(fenced_json)
    return _MainlineIndexWire.model_validate(decoded, strict=True)


def _parse_leaf(markdown_bytes: bytes) -> _TicketLeafWire:
    markdown = markdown_bytes.decode("utf-8", errors="strict")
    fenced_json = _extract_contract_json(markdown, "## Mainline ticket contract")
    decoded = _load_json_object(fenced_json)
    return _TicketLeafWire.model_validate(decoded, strict=True)


def _index_path(feature: FeatureSlug) -> TargetRelativePath:
    return TargetRelativePath(f"modules/tickets/{feature}/README.md")


def _is_same_feature_leaf(artifact_ref: TargetRelativePath, feature: FeatureSlug) -> bool:
    segments = artifact_ref.value.split("/")
    return (
        len(segments) == 4
        and segments[0] == "modules"
        and segments[1] == "tickets"
        and segments[2] == feature
        and segments[3].endswith(".md")
        and artifact_ref.value != _index_path(feature).value
    )


def _read_blob_once(
    port: MainlineSourcePort,
    observation: GitObservation,
    artifact_ref: TargetRelativePath,
) -> RawGitBlobReadResult | None:
    try:
        read_result = port.read_blob(observation, artifact_ref)
        return RawGitBlobReadResult.model_validate(read_result, strict=True)
    except Exception:
        return None


def _source_failure(failure: MainlineSourceFailure) -> MainlineSourceResult:
    return MainlineSourceResult(failure=failure)


def project_committed_mainline(
    request: MainlineSourceRequest,
    port: MainlineSourcePort,
) -> MainlineSourceResult:
    """Build a fixture-only candidate from one synthetic observation's committed blobs."""

    index_ref = _index_path(request.feature)
    index_read = _read_blob_once(port, request.observation, index_ref)
    if index_read is None or index_read.status is GitBlobReadStatus.UNAVAILABLE:
        return _source_failure(MainlineSourceFailure.INDEX_READ_UNAVAILABLE)
    if index_read.status is GitBlobReadStatus.NOT_FOUND:
        return _source_failure(MainlineSourceFailure.INDEX_NOT_FOUND)
    if index_read.payload is None:
        return _source_failure(MainlineSourceFailure.INDEX_READ_UNAVAILABLE)

    try:
        index = _parse_index(index_read.payload)
    except (UnicodeDecodeError, ValueError, ValidationError):
        return _source_failure(MainlineSourceFailure.INDEX_SCHEMA_INVALID)

    if index.project_id != request.project_id or index.feature != request.feature:
        return _source_failure(MainlineSourceFailure.INDEX_BINDING_MISMATCH)

    ticket_refs = tuple(ticket.ticket_ref for ticket in index.tickets)
    leaf_refs = tuple(ticket.leaf_ref for ticket in index.tickets)
    if len(ticket_refs) != len(set(ticket_refs)) or len(leaf_refs) != len(set(leaf_refs)):
        return _source_failure(MainlineSourceFailure.INDEX_SCHEMA_INVALID)
    if any(
        not _is_same_feature_leaf(ticket.leaf_ref, request.feature)
        for ticket in index.tickets
    ):
        return _source_failure(MainlineSourceFailure.INDEX_SCHEMA_INVALID)

    tickets: list[MainlineTicket] = []
    for index_ticket in index.tickets:
        leaf_read = _read_blob_once(port, request.observation, index_ticket.leaf_ref)
        if leaf_read is None or leaf_read.status is GitBlobReadStatus.UNAVAILABLE:
            return _source_failure(MainlineSourceFailure.LEAF_READ_UNAVAILABLE)
        if leaf_read.status is GitBlobReadStatus.NOT_FOUND:
            return _source_failure(MainlineSourceFailure.LEAF_NOT_FOUND)
        if leaf_read.payload is None:
            return _source_failure(MainlineSourceFailure.LEAF_READ_UNAVAILABLE)
        if "sha256_" + hashlib.sha256(leaf_read.payload).hexdigest() != index_ticket.leaf_digest:
            return _source_failure(MainlineSourceFailure.LEAF_DIGEST_MISMATCH)

        try:
            leaf = _parse_leaf(leaf_read.payload)
        except (UnicodeDecodeError, ValueError, ValidationError):
            return _source_failure(MainlineSourceFailure.PROJECTION_INVALID)

        if (
            leaf.ticket_ref != index_ticket.ticket_ref
            or leaf.ticket_revision != index_ticket.ticket_revision
            or leaf.status != index_ticket.status
            or leaf.depends_on != index_ticket.depends_on
            or leaf.admission_ref != index_ticket.admission_ref
            or leaf.evidence_refs != index_ticket.evidence_refs
        ):
            return _source_failure(MainlineSourceFailure.INDEX_BINDING_MISMATCH)

        try:
            tickets.append(
                MainlineTicket(
                    ticket_ref=leaf.ticket_ref,
                    ticket_revision=leaf.ticket_revision,
                    required=index_ticket.required,
                    status=MainlineTicketStatus(leaf.status),
                    depends_on=tuple(leaf.depends_on),
                    admission_ref=leaf.admission_ref,
                    evidence_refs=tuple(leaf.evidence_refs),
                )
            )
        except (TypeError, ValueError, ValidationError):
            return _source_failure(MainlineSourceFailure.PROJECTION_INVALID)

    try:
        projection_request = MainlineProjectionRequest(
            project_id=index.project_id,
            mainline_ref=index.mainline_ref,
            source_revision=f"rev-{request.observation.sha}",
            tickets=tuple(tickets),
        )
        projection = project_mainline_tickets(projection_request)
    except (TypeError, ValueError, ValidationError):
        return _source_failure(MainlineSourceFailure.PROJECTION_INVALID)

    return MainlineSourceResult(projection=projection)
