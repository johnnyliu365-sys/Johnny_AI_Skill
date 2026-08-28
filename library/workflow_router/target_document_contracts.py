"""Strong contracts for bounded target-owned document transactions."""

from __future__ import annotations

from enum import Enum
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self, TypeAlias, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import (
    ArtifactTreeFamily,
    ArtifactTreeLifecycle,
    ArtifactTreeNode,
    EvidenceDigest,
    OpaqueMetadataId,
    ProjectId,
    ReviewedCommitReference,
)
from .role_supervision_contracts import (
    CompatibilityRevision,
    HandoffLeaf,
    ObservedControlPlaneState,
    ProtocolId,
    SchemaRevision,
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=False,
        revalidate_instances="always",
    )


TargetRelativePath: TypeAlias = Annotated[
    str,
    Field(
        pattern=(
            r"^(?:README\.md|PRD\.md|CONTEXT\.md|ProjectSchedule\.md|"
            r"doc/[A-Za-z0-9._/-]{1,220}|modules/[A-Za-z0-9._/-]{1,220})$"
        )
    ),
]
ContentDigest: TypeAlias = EvidenceDigest
FeatureSlug: TypeAlias = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{1,63}$")]
TicketSlug: TypeAlias = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9-]{2,95}$")]
Year: TypeAlias = Annotated[int, Field(ge=2000, le=9999)]


class ArtifactDocumentKind(str, Enum):
    ROOT_README = "ROOT_README"
    REQUIREMENT = "REQUIREMENT"
    REQUIREMENT_CHANGE = "REQUIREMENT_CHANGE"
    CONTEXT = "CONTEXT"
    GRILL_CONTEXT = "GRILL_CONTEXT"
    SPECIFICATION = "SPECIFICATION"
    TICKET = "TICKET"
    IMPLEMENTATION_EVIDENCE = "IMPLEMENTATION_EVIDENCE"
    REVIEW = "REVIEW"
    HANDOFF_README = "HANDOFF_README"
    HANDOFF_INDEX = "HANDOFF_INDEX"
    HANDOFF_LEAF = "HANDOFF_LEAF"


class DocumentMutationMode(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"


class DocumentWriteStatus(str, Enum):
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    STORAGE_UNAVAILABLE = "STORAGE_UNAVAILABLE"


class DocumentWriteFailure(str, Enum):
    BASELINE_MISMATCH = "BASELINE_MISMATCH"
    PATH_STATE_MISMATCH = "PATH_STATE_MISMATCH"
    PATH_ESCAPE = "PATH_ESCAPE"
    STORAGE_UNAVAILABLE = "STORAGE_UNAVAILABLE"


def derive_document_digest(content: str) -> ContentDigest:
    if type(content) is not str:
        raise TypeError("document content must be exact text")
    canonical = content.replace("\r\n", "\n").replace("\r", "\n")
    return "sha256_" + sha256(canonical.encode("utf-8")).hexdigest()


class TargetDocumentMutation(_StrictModel):
    """One exact create/update with compare-and-swap content identity."""

    path: TargetRelativePath
    artifact_kind: ArtifactDocumentKind
    mode: DocumentMutationMode
    expected_current_digest: ContentDigest | None
    content: str = Field(min_length=1)
    content_digest: ContentDigest
    sealed: bool

    @model_validator(mode="after")
    def mutation_is_safe_and_exact(self) -> Self:
        path = PurePosixPath(self.path)
        if path.is_absolute() or ".." in path.parts or "." in path.parts:
            raise ValueError("target document path must be normalized and relative")
        lowered_parts = tuple(part.casefold() for part in path.parts)
        if any(
            part in (".git", ".codex", ".codex-plugin", ".claude-plugin")
            for part in lowered_parts
        ):
            raise ValueError("target transaction cannot write control-plane paths")
        if self.content_digest != derive_document_digest(self.content):
            raise ValueError("document digest must match exact UTF-8 content")
        if "\r" in self.content:
            raise ValueError("document mutations must use canonical LF newlines")
        if self.mode is DocumentMutationMode.CREATE:
            if self.expected_current_digest is not None:
                raise ValueError("create mutation requires an absent target")
        elif self.expected_current_digest is None:
            raise ValueError("update mutation requires an exact current digest")
        if self.sealed and self.mode is not DocumentMutationMode.CREATE:
            raise ValueError("sealed artifacts can only be created")
        if self.artifact_kind is ArtifactDocumentKind.HANDOFF_LEAF and not self.sealed:
            raise ValueError("handoff leaves must be sealed")
        return self


class TargetDocumentPlan(_StrictModel):
    """One project/baseline transaction over a finite explicit path set."""

    project_id: ProjectId
    baseline_commit: ReviewedCommitReference
    mutations: tuple[TargetDocumentMutation, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def paths_are_unique(self) -> Self:
        paths = tuple(mutation.path for mutation in self.mutations)
        if len(paths) != len(set(paths)):
            raise ValueError("one target document plan cannot repeat a path")
        return self


class DocumentWriteResult(_StrictModel):
    status: DocumentWriteStatus
    written_paths: tuple[TargetRelativePath, ...] = ()
    written_digests: tuple[ContentDigest, ...] = ()
    failure: DocumentWriteFailure | None = None

    @model_validator(mode="after")
    def exact_result_shape(self) -> Self:
        if self.status is DocumentWriteStatus.APPLIED:
            if (
                not self.written_paths
                or len(self.written_paths) != len(self.written_digests)
                or self.failure is not None
            ):
                raise ValueError("applied transaction requires exact written identities")
        elif self.written_paths or self.written_digests or self.failure is None:
            raise ValueError("rejected transaction returns only one failure")
        return self


class HandoffTreeBootstrapRequest(_StrictModel):
    """Inputs for a plugin-neutral project-owned handoff tree."""

    project_id: ProjectId
    baseline_commit: ReviewedCommitReference
    year: Year
    feature_slug: FeatureSlug
    ticket_slug: TicketSlug
    leaf: HandoffLeaf
    root_readme_content: str = Field(min_length=1)
    root_readme_digest: ContentDigest
    spec_path: TargetRelativePath
    protocol_id: ProtocolId
    schema_revision: SchemaRevision
    compatibility_revision: CompatibilityRevision
    minimum_adoption_capabilities: tuple[str, ...] = Field(min_length=1)
    control_plane_state: ObservedControlPlaneState

    @model_validator(mode="after")
    def bootstrap_bindings_are_exact(self) -> Self:
        if self.leaf.project_id != self.project_id:
            raise ValueError("handoff leaf must belong to the bootstrap project")
        if self.root_readme_digest != derive_document_digest(self.root_readme_content):
            raise ValueError("root README digest must match its exact current content")
        if not self.spec_path.startswith("modules/spec/"):
            raise ValueError("handoff README must link one target-owned SPEC")
        if len(self.minimum_adoption_capabilities) != len(
            set(self.minimum_adoption_capabilities)
        ):
            raise ValueError("minimum adoption capabilities must be unique")
        for capability in self.minimum_adoption_capabilities:
            if (
                not capability
                or capability != capability.strip()
                or any(marker in capability.casefold() for marker in ("/", "\\", "://", "plugin"))
            ):
                raise ValueError("adoption capabilities must be opaque plugin-neutral IDs")
        return self


class ManagedArtifactAction(str, Enum):
    """The four finite managed-artifact planning actions."""

    CREATE = "CREATE"
    REVISE = "REVISE"
    REPLACE = "REPLACE"
    ARCHIVE = "ARCHIVE"


class ManagedArtifactTerminalState(str, Enum):
    """The terminal presence state selected by one artifact path snapshot."""

    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class ManagedArtifactNodeStateKind(str, Enum):
    """The discriminant for one managed-artifact node state."""

    ABSENT = "ABSENT"
    PRESENT = "PRESENT"


class ManagedArtifactAbsentNodeState(_StrictModel):
    """The only state allowed for an absent terminal node."""

    state: Literal["ABSENT"] = "ABSENT"


class ManagedArtifactPresentNodeState(_StrictModel):
    """The complete metadata state of one present artifact node."""

    state: Literal["PRESENT"] = "PRESENT"
    revision: Annotated[str, Field(pattern=r"^rev-[0-9a-f]{16,64}$")]
    content_digest: ContentDigest
    lifecycle: ArtifactTreeLifecycle

    @model_validator(mode="after")
    def state_metadata_is_not_reserved(self) -> Self:
        if self.revision[4:] and all(character == "0" for character in self.revision[4:]):
            raise ValueError("managed artifact revisions must identify real content")
        if self.content_digest[7:] and all(
            character == "0" for character in self.content_digest[7:]
        ):
            raise ValueError("managed artifact digests must identify real content")
        return self


ManagedArtifactNodeState: TypeAlias = Annotated[
    Union[ManagedArtifactAbsentNodeState, ManagedArtifactPresentNodeState],
    Field(discriminator="state"),
]


class ManagedArtifactPathSnapshot(_StrictModel):
    """One caller-selected path and its current or candidate terminal state."""

    family: ArtifactTreeFamily
    root_ref: OpaqueMetadataId
    explicit_path_refs: tuple[OpaqueMetadataId, ...] = Field(min_length=3)
    expected_leaf_ref: OpaqueMetadataId
    terminal_state: ManagedArtifactTerminalState
    path_nodes: tuple[ArtifactTreeNode, ...] = Field(min_length=2)


class ManagedArtifactPathTransition(_StrictModel):
    """The exact current-to-candidate path transition for one action slot."""

    current: ManagedArtifactPathSnapshot
    candidate: ManagedArtifactPathSnapshot


ManagedArtifactTransition = ManagedArtifactPathTransition


class ManagedArtifactNodeMutation(_StrictModel):
    """One compare-and-swap metadata transition for an artifact-tree node."""

    artifact_ref: OpaqueMetadataId
    expected_state: ManagedArtifactNodeState
    next_state: ManagedArtifactNodeState

    @model_validator(mode="after")
    def state_must_change(self) -> Self:
        if self.expected_state == self.next_state:
            raise ValueError("managed artifact node mutations must change state")
        return self


def _managed_artifact_path_is_safe(path: str) -> bool:
    """Apply the target-relative and control-plane path boundary to new mutations."""

    normalized = PurePosixPath(path)
    if str(normalized) != path:
        return False
    if normalized.is_absolute() or ".." in normalized.parts or "." in normalized.parts:
        return False
    lowered_parts = tuple(part.casefold() for part in normalized.parts)
    return not any(
        part in (".git", ".codex", ".codex-plugin", ".claude-plugin")
        for part in lowered_parts
    )


class ManagedArtifactDocumentCreate(_StrictModel):
    """A document create bound to one newly present artifact node."""

    mode: Literal["CREATE"] = "CREATE"
    artifact_ref: OpaqueMetadataId
    path: TargetRelativePath
    kind: ArtifactDocumentKind
    content: str = Field(min_length=1)
    content_digest: ContentDigest
    sealed: bool

    @model_validator(mode="after")
    def create_document_is_canonical(self) -> Self:
        if not _managed_artifact_path_is_safe(self.path):
            raise ValueError("managed artifact document path must be normalized and relative")
        if "\r" in self.content or self.content_digest != derive_document_digest(self.content):
            raise ValueError("managed artifact create content must be canonical and exact")
        if self.kind is ArtifactDocumentKind.HANDOFF_LEAF and not self.sealed:
            raise ValueError("handoff leaves must be sealed")
        return self


class ManagedArtifactDocumentUpdate(_StrictModel):
    """A document update bound to one present artifact node."""

    mode: Literal["UPDATE"] = "UPDATE"
    artifact_ref: OpaqueMetadataId
    path: TargetRelativePath
    kind: ArtifactDocumentKind
    expected_current_digest: ContentDigest
    content: str = Field(min_length=1)
    content_digest: ContentDigest
    sealed: Literal[False] = False

    @model_validator(mode="after")
    def update_document_is_canonical(self) -> Self:
        if not _managed_artifact_path_is_safe(self.path):
            raise ValueError("managed artifact document path must be normalized and relative")
        if "\r" in self.content or self.content_digest != derive_document_digest(self.content):
            raise ValueError("managed artifact update content must be canonical and exact")
        return self


class ManagedArtifactDeleteDocument(_StrictModel):
    """A document delete bound to one terminal node becoming absent."""

    mode: Literal["DELETE"] = "DELETE"
    artifact_ref: OpaqueMetadataId
    path: TargetRelativePath
    kind: ArtifactDocumentKind
    expected_current_digest: ContentDigest

    @model_validator(mode="after")
    def delete_document_is_safe(self) -> Self:
        if not _managed_artifact_path_is_safe(self.path):
            raise ValueError("managed artifact document path must be normalized and relative")
        return self


ManagedArtifactDocumentMutation: TypeAlias = Annotated[
    Union[
        ManagedArtifactDocumentCreate,
        ManagedArtifactDocumentUpdate,
        ManagedArtifactDeleteDocument,
    ],
    Field(discriminator="mode"),
]


class ManagedArtifactCreateRequest(_StrictModel):
    """A typed absent-to-present managed-artifact create request."""

    action: Literal["CREATE"] = "CREATE"
    request_ref: OpaqueMetadataId
    baseline_commit: ReviewedCommitReference
    destination_transition: ManagedArtifactPathTransition
    proposed_document_mutations: tuple[ManagedArtifactDocumentMutation, ...] = Field(min_length=1)


class ManagedArtifactReviseRequest(_StrictModel):
    """A typed present-to-present managed-artifact revision request."""

    action: Literal["REVISE"] = "REVISE"
    request_ref: OpaqueMetadataId
    baseline_commit: ReviewedCommitReference
    selected_transition: ManagedArtifactPathTransition
    proposed_document_mutations: tuple[ManagedArtifactDocumentMutation, ...] = Field(min_length=1)


class ManagedArtifactReplaceRequest(_StrictModel):
    """A typed replacement of one present path with a distinct absent path."""

    action: Literal["REPLACE"] = "REPLACE"
    request_ref: OpaqueMetadataId
    baseline_commit: ReviewedCommitReference
    current_transition: ManagedArtifactPathTransition
    replacement_transition: ManagedArtifactPathTransition
    proposed_document_mutations: tuple[ManagedArtifactDocumentMutation, ...] = Field(min_length=1)


class ManagedArtifactArchiveRequest(_StrictModel):
    """A typed active-to-archive-library lifecycle movement request."""

    action: Literal["ARCHIVE"] = "ARCHIVE"
    request_ref: OpaqueMetadataId
    baseline_commit: ReviewedCommitReference
    active_transition: ManagedArtifactPathTransition
    archive_transition: ManagedArtifactPathTransition
    proposed_document_mutations: tuple[ManagedArtifactDocumentMutation, ...] = Field(min_length=1)


ManagedArtifactRequest: TypeAlias = Annotated[
    Union[
        ManagedArtifactCreateRequest,
        ManagedArtifactReviseRequest,
        ManagedArtifactReplaceRequest,
        ManagedArtifactArchiveRequest,
    ],
    Field(discriminator="action"),
]


class _ManagedArtifactPlanBase(_StrictModel):
    """Shared deterministic output fields for action-specific plans."""

    baseline_commit: ReviewedCommitReference
    node_mutations: tuple[ManagedArtifactNodeMutation, ...] = Field(min_length=1)
    document_mutations: tuple[ManagedArtifactDocumentMutation, ...] = Field(min_length=1)
    post_state_snapshots: tuple[ManagedArtifactPathSnapshot, ...] = Field(min_length=1)


class ManagedArtifactCreatePlan(_ManagedArtifactPlanBase):
    """Canonical plan for CREATE's destination slot."""

    action: Literal["CREATE"] = "CREATE"
    destination_transition: ManagedArtifactPathTransition


class ManagedArtifactRevisePlan(_ManagedArtifactPlanBase):
    """Canonical plan for REVISE's selected slot."""

    action: Literal["REVISE"] = "REVISE"
    selected_transition: ManagedArtifactPathTransition


class ManagedArtifactReplacePlan(_ManagedArtifactPlanBase):
    """Canonical plan for REPLACE's current and replacement slots."""

    action: Literal["REPLACE"] = "REPLACE"
    current_transition: ManagedArtifactPathTransition
    replacement_transition: ManagedArtifactPathTransition


class ManagedArtifactArchivePlan(_ManagedArtifactPlanBase):
    """Canonical plan for ARCHIVE's active and archive slots."""

    action: Literal["ARCHIVE"] = "ARCHIVE"
    active_transition: ManagedArtifactPathTransition
    archive_transition: ManagedArtifactPathTransition


ManagedArtifactPlan: TypeAlias = Annotated[
    Union[
        ManagedArtifactCreatePlan,
        ManagedArtifactRevisePlan,
        ManagedArtifactReplacePlan,
        ManagedArtifactArchivePlan,
    ],
    Field(discriminator="action"),
]


class ManagedArtifactPlanningDecision(str, Enum):
    """The finite no-plan decisions exposed by R09A."""

    PATH_INVALID = "PATH_INVALID"
    ARTIFACT_TREE_INVALID = "ARTIFACT_TREE_INVALID"
    EDGE_INVALID = "EDGE_INVALID"
    LIFECYCLE_INVALID = "LIFECYCLE_INVALID"
    TERMINAL_STATE_MISMATCH = "TERMINAL_STATE_MISMATCH"
    ANCESTOR_CASCADE_INCOMPLETE = "ANCESTOR_CASCADE_INCOMPLETE"
    DOCUMENT_MUTATION_MISMATCH = "DOCUMENT_MUTATION_MISMATCH"
    UNRELATED_MUTATION = "UNRELATED_MUTATION"


class ManagedArtifactPlannedResult(_StrictModel):
    """The exact success variant of the planning result."""

    status: Literal["PLANNED"] = "PLANNED"
    request_ref: OpaqueMetadataId
    plan: ManagedArtifactPlan


class ManagedArtifactRejectedResult(_StrictModel):
    """The exact rejection variant with no leaked plan or input content."""

    status: Literal["REJECTED"] = "REJECTED"
    request_ref: OpaqueMetadataId
    decision: ManagedArtifactPlanningDecision


ManagedArtifactPlanningResult: TypeAlias = Annotated[
    Union[ManagedArtifactPlannedResult, ManagedArtifactRejectedResult],
    Field(discriminator="status"),
]


__all__ = [
    "ArtifactDocumentKind",
    "ContentDigest",
    "DocumentMutationMode",
    "DocumentWriteFailure",
    "DocumentWriteResult",
    "DocumentWriteStatus",
    "HandoffTreeBootstrapRequest",
    "TargetDocumentMutation",
    "TargetDocumentPlan",
    "TargetRelativePath",
    "derive_document_digest",
    "ManagedArtifactAction",
    "ManagedArtifactArchivePlan",
    "ManagedArtifactArchiveRequest",
    "ManagedArtifactAbsentNodeState",
    "ManagedArtifactCreatePlan",
    "ManagedArtifactCreateRequest",
    "ManagedArtifactDeleteDocument",
    "ManagedArtifactDocumentCreate",
    "ManagedArtifactDocumentMutation",
    "ManagedArtifactDocumentUpdate",
    "ManagedArtifactNodeMutation",
    "ManagedArtifactNodeState",
    "ManagedArtifactNodeStateKind",
    "ManagedArtifactPathSnapshot",
    "ManagedArtifactPathTransition",
    "ManagedArtifactPlan",
    "ManagedArtifactPlannedResult",
    "ManagedArtifactPlanningDecision",
    "ManagedArtifactPlanningResult",
    "ManagedArtifactPresentNodeState",
    "ManagedArtifactRejectedResult",
    "ManagedArtifactReplacePlan",
    "ManagedArtifactReplaceRequest",
    "ManagedArtifactRequest",
    "ManagedArtifactRevisePlan",
    "ManagedArtifactReviseRequest",
    "ManagedArtifactTerminalState",
    "ManagedArtifactTransition",
]
