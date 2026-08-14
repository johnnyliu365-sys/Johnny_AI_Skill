"""Strongly typed contracts for the reusable workflow router."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


NonBlankText = Annotated[str, Field(min_length=1)]
PositiveTokenBudget = Annotated[int, Field(gt=0)]
OpaqueMetadataId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{2,127}$")]
ProjectId = Annotated[str, Field(pattern=r"^prj_[0-9a-f]{16}$")]
WorktreeFingerprint = Annotated[str, Field(pattern=r"^worktree-[a-z0-9]+-[0-9]{2}$")]
BranchFingerprint = Annotated[str, Field(pattern=r"^branch-[a-z0-9]+-[0-9]{2}$")]
RevisionDigest = Annotated[str, Field(pattern=r"^rev-[0-9a-f]{16,64}$")]
EvidenceDigest = Annotated[str, Field(pattern=r"^sha256_[0-9a-f]{64}$")]
CommitDigest = Annotated[str, Field(pattern=r"^git_[0-9a-f]{12,64}$")]
ReviewedCommitReference = Annotated[str, Field(pattern=r"^[0-9a-f]{7,64}$")]


class RouterModel(BaseModel):
    """Immutable, strict base model for values that cross router boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, str_strip_whitespace=True)


class ProcessStage(str, Enum):
    """The finite workflow stages the router may address."""

    INTAKE = "intake"
    WAYFINDER = "wayfinder"
    ARCHITECTURE = "architecture"
    GRILL = "grill"
    CONTEXT = "context"
    SPEC = "spec"
    TICKETS = "tickets"
    IMPLEMENT = "implement"
    SMOKE_TEST = "smoke_test"
    REVIEW = "review"
    HANDOFF = "handoff"
    BLOCKED = "blocked"
    STOPPED = "stopped"


class DeliveryStage(str, Enum):
    """A project's delivery maturity, defined by its own workflow profile."""

    POC = "poc"
    MVP = "mvp"
    COMMERCIAL = "commercial"


class RouterEventKind(str, Enum):
    """Only events in this closed set may drive a router transition."""

    INTAKE = "intake"
    WAYFINDER_GO = "wayfinder_go"
    WAYFINDER_NO_GO = "wayfinder_no_go"
    ACTION_COMPLETED = "action_completed"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    REQUIREMENT_CHANGED = "requirement_changed"
    CONTEXT_REFERENCE_CLOSED = "context_reference_closed"
    EXTERNAL_DECISION_REQUIRED = "external_decision_required"
    TICKET_DISPATCH_REQUIRED = "ticket_dispatch_required"
    IMPLEMENTATION_DISPATCH_CONFIRMED = "implementation_dispatch_confirmed"
    IMPLEMENTATION_RETURNED = "implementation_returned"
    INTEGRATION_COMPLETED = "integration_completed"
    AUDIT_COMPLETED = "audit_completed"


class CollaborationTopology(str, Enum):
    """The only supported role-isolated collaboration topologies."""

    ONE_IMPLEMENTATION_AGENT = "one_implementation_agent"
    TWO_COLLABORATING_AGENTS = "two_collaborating_agents"


class TicketDispatchConfirmation(str, Enum):
    """The ticket-scoped human dispatch response."""

    NEGATIVE = "negative"
    POSITIVE = "positive"


class TicketDispatchState(str, Enum):
    """The finite lifecycle of a dispatched ticket lane."""

    REQUIRED = "required"
    CONFIRMED = "confirmed"


class TicketProposalState(str, Enum):
    """The opened-ticket lifecycle before and after dispatch confirmation."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"


class TicketEvent(str, Enum):
    """Events emitted by the typed ticket dispatch lane."""

    TICKET_DISPATCH_REQUIRED = "ticket_dispatch_required"
    IMPLEMENTATION_DISPATCH_CONFIRMED = "implementation_dispatch_confirmed"


class LaneKind(str, Enum):
    """The two independent state lanes created by a confirmed dispatch."""

    PLANNING = "planning"
    TICKET = "ticket"


class AuthorityState(str, Enum):
    """The current human authorization state for the requested transition."""

    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"
    NOT_REQUIRED = "not_required"


class RouterOutcome(str, Enum):
    """The finite results that a router may emit."""

    ADVANCE = "advance"
    RETRY = "retry"
    SUSPEND = "suspend"
    STOP = "stop"


class ContinuationDirective(str, Enum):
    """The sole safe disposition after a Router decision."""

    AUTO_CONTINUE = "auto_continue"
    WAIT_FOR_HUMAN = "wait_for_human"
    HALT = "halt"


class HumanWaitReason(str, Enum):
    """The finite human decisions that may produce a non-error wait."""

    SPECIFICATION_APPROVAL_REQUIRED = "specification_approval_required"
    TICKET_APPROVAL_REQUIRED = "ticket_approval_required"
    IMPLEMENTATION_OWNER_ASSIGNMENT_REQUIRED = "implementation_owner_assignment_required"
    TICKET_DISPATCH_CONFIRMATION_REQUIRED = "ticket_dispatch_confirmation_required"
    INTEGRATION_AUDIT_REQUIRED = "integration_audit_required"


class CompletionActionKind(str, Enum):
    """The completed action classes that may be recorded as metadata-only evidence."""

    DOCUMENTATION = "documentation"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    HANDOFF = "handoff"


class TicketScope(str, Enum):
    """Whether a ticket changes a formal UI boundary."""

    FRONTEND = "frontend"
    NON_FRONTEND = "non_frontend"


class ImplementationReturnStatus(str, Enum):
    """The finite results an implementation owner may return to the control plane."""

    COMPLETED = "completed"
    BLOCKED = "blocked"
    CHANGE_DETECTED = "change_detected"


class ReturnContractKind(str, Enum):
    """The finite return families a routed action may produce."""

    ROUTER_EVENT = "router_event"
    IMPLEMENTATION_RETURN = "implementation_return"
    NO_RETURN = "no_return"


class SkillReference(RouterModel):
    """Versioned metadata identifying a later-resolved skill policy."""

    reference_id: OpaqueMetadataId
    source_revision: RevisionDigest
    content_digest: EvidenceDigest

    @model_validator(mode="after")
    def reference_id_is_metadata_only(self) -> SkillReference:
        """Reject locator and sensitive markers before a registry resolves the reference."""

        normalized = self.reference_id.casefold()
        forbidden_markers = ("://", "\\", "/", "prompt", "secret")
        if any(marker in normalized for marker in forbidden_markers):
            raise ValueError("skill reference IDs are metadata-only")
        return self


class ExpectedReturnContract(RouterModel):
    """Finite return family and event/status set expected from a selected skill."""

    contract_id: OpaqueMetadataId
    contract_revision: RevisionDigest
    return_kind: ReturnContractKind
    router_events: tuple[RouterEventKind, ...]
    implementation_statuses: tuple[ImplementationReturnStatus, ...]

    @model_validator(mode="after")
    def return_family_is_finite_and_consistent(self) -> ExpectedReturnContract:
        """Keep each return family disjoint, non-empty where required, and duplicate-free."""

        if len(self.router_events) != len(set(self.router_events)):
            raise ValueError("router events must be unique")
        if len(self.implementation_statuses) != len(set(self.implementation_statuses)):
            raise ValueError("implementation statuses must be unique")
        if self.return_kind is ReturnContractKind.ROUTER_EVENT:
            if not self.router_events or self.implementation_statuses:
                raise ValueError("router-event contracts require only non-empty router events")
        elif self.return_kind is ReturnContractKind.IMPLEMENTATION_RETURN:
            if not self.implementation_statuses or self.router_events:
                raise ValueError(
                    "implementation-return contracts require only non-empty implementation statuses"
                )
        elif self.router_events or self.implementation_statuses:
            raise ValueError("no-return contracts require empty event and status tuples")
        return self


class ArtifactKind(str, Enum):
    """Kinds of official sources and products that may be referenced."""

    PROJECT_GOAL = "project_goal"
    WAYFINDER_OUTPUT = "wayfinder_output"
    ARCHITECTURE = "architecture"
    GRILL = "grill"
    CONTEXT = "context"
    SPEC = "spec"
    TICKET = "ticket"
    CHANGE = "change"
    SECURITY_POLICY = "security_policy"


class BlockerCode(str, Enum):
    """Reasons that force a fail-closed router decision."""

    AUTHORITY_REQUIRED = "authority_required"
    DELIVERY_STAGE_MISMATCH = "delivery_stage_mismatch"
    MISSING_REQUIRED_SOURCE = "missing_required_source"
    AMBIGUOUS_REQUIRED_SOURCE = "ambiguous_required_source"
    NO_DECLARED_TRANSITION = "no_declared_transition"
    SOURCE_UNAVAILABLE = "source_unavailable"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    INVALID_COMPLETION_EVIDENCE = "invalid_completion_evidence"
    IMPLEMENTATION_RETURN_BLOCKED = "implementation_return_blocked"
    IMPLEMENTATION_HANDOFF_REQUIRED = "implementation_handoff_required"
    IMPLEMENTATION_HANDOFF_UNDECLARED = "implementation_handoff_undeclared"
    TOPOLOGY_REQUIRED = "topology_required"
    DISPATCH_RECEIPT_REQUIRED = "dispatch_receipt_required"
    INVALID_DISPATCH_RECEIPT = "invalid_dispatch_receipt"
    LEGACY_TICKET_APPROVAL_BLOCKED = "legacy_ticket_approval_blocked"
    TICKET_PROPOSAL_REQUIRED = "ticket_proposal_required"
    INVALID_TICKET_PROPOSAL = "invalid_ticket_proposal"
    PENDING_DISPATCH_REQUIRED = "pending_dispatch_required"
    INVALID_PENDING_DISPATCH = "invalid_pending_dispatch"


class ReferenceStatus(str, Enum):
    """Lifecycle of a metadata-only Context reference edge."""

    OPEN = "open"
    CLOSED = "closed"
    INVALIDATED = "invalidated"


class ArtifactRef(RouterModel):
    """A versioned pointer to one official source or workflow artifact."""

    kind: ArtifactKind
    identifier: NonBlankText
    uri: NonBlankText
    revision: NonBlankText

    @property
    def logical_key(self) -> tuple[ArtifactKind, str, str]:
        """Return the identity that remains stable across revisions."""

        return (self.kind, self.identifier, self.uri)


class TicketDispatchReceipt(RouterModel):
    """Metadata-only proof that one approved ticket was delivered to its owner."""

    ticket_reference: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId
    handoff_reference: OpaqueMetadataId
    expected_main_revision: RevisionDigest
    correlation_id: NonBlankText
    dispatch_question_id: OpaqueMetadataId
    worktree_fingerprint: WorktreeFingerprint
    branch_fingerprint: BranchFingerprint

    @model_validator(mode="after")
    def correlation_is_metadata_only(self) -> TicketDispatchReceipt:
        """Reject locators and sensitive labels at the dispatch boundary."""

        lowered = self.correlation_id.lower()
        if any(marker in lowered for marker in ("://", "\\", "/", "prompt", "secret")):
            raise ValueError("correlation_id must be metadata-only")
        return self

    @property
    def ticket_ref(self) -> str:
        """Expose the spec terminology without storing a second field."""

        return self.ticket_reference

    @property
    def implementation_owner(self) -> str:
        """Expose the spec terminology without storing a second field."""

        return self.implementation_owner_id

    @property
    def handoff_ref(self) -> str:
        """Expose the spec terminology without storing a second field."""

        return self.handoff_reference


class TicketProposal(RouterModel):
    """A selected ticket opened in progress before its single dispatch question."""

    ticket_reference: OpaqueMetadataId
    state: TicketProposalState
    implementation_owner_id: OpaqueMetadataId
    dispatch_question_id: OpaqueMetadataId | None = None
    proposal_revision: RevisionDigest

    @model_validator(mode="after")
    def question_matches_open_state(self) -> TicketProposal:
        """Require exactly one question identifier only after the proposal is opened."""

        if self.state is TicketProposalState.PLANNED and self.dispatch_question_id is not None:
            raise ValueError("planned ticket proposals cannot carry a dispatch question")
        if self.state is TicketProposalState.IN_PROGRESS and self.dispatch_question_id is None:
            raise ValueError("opened ticket proposals require one dispatch question")
        return self

    def open(self, *, dispatch_question_id: OpaqueMetadataId) -> TicketProposal:
        """Open one planned proposal and emit its single named dispatch question."""

        if self.state is not TicketProposalState.PLANNED:
            raise ValueError("only planned ticket proposals may be opened")
        return TicketProposal(
            ticket_reference=self.ticket_reference,
            state=TicketProposalState.IN_PROGRESS,
            implementation_owner_id=self.implementation_owner_id,
            dispatch_question_id=dispatch_question_id,
            proposal_revision=self.proposal_revision,
        )


class PendingDispatchDescriptor(RouterModel):
    """Metadata-only authorization state created by one opened dispatch question."""

    ticket_reference: OpaqueMetadataId
    proposal_revision: RevisionDigest
    expected_main_revision: RevisionDigest
    dispatch_question_id: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId
    reviewed_handoff_reference: OpaqueMetadataId
    event_correlation_id: NonBlankText
    ticket_docs_commit: ReviewedCommitReference | None = None
    handoff_docs_commit: ReviewedCommitReference | None = None

    @property
    def ticket_ref(self) -> str:
        """Expose the specification terminology without duplicating state."""

        return self.ticket_reference

    @property
    def reviewed_handoff_ref(self) -> str:
        """Expose the reviewed handoff reference as an opaque metadata ID."""

        return self.reviewed_handoff_reference


class HandoffConsumerFingerprint(RouterModel):
    """Opaque consumer identity suitable for handoff metadata, never a local path or prompt."""

    agent_profile_id: OpaqueMetadataId
    profile_version: OpaqueMetadataId
    worktree_fingerprint: OpaqueMetadataId
    execution_fingerprint: OpaqueMetadataId


class HandoffArtifactReference(RouterModel):
    """An opaque source/revision/span mapping without URI, path, or source text."""

    artifact_id: OpaqueMetadataId
    revision_digest: RevisionDigest
    source_span_id: OpaqueMetadataId
    side_context_id: OpaqueMetadataId
    consumer_fingerprint: HandoffConsumerFingerprint


class CompletionEvidence(RouterModel):
    """Typed completion metadata; a commit digest is evidence and never a route decision."""

    completion_id: OpaqueMetadataId
    action_kind: CompletionActionKind
    artifact_references: tuple[HandoffArtifactReference, ...] = Field(min_length=1)
    verification_references: tuple[OpaqueMetadataId, ...] = Field(min_length=1)
    evidence_digest: EvidenceDigest
    commit_digest: CommitDigest | None = None
    emitted_event: RouterEventKind = RouterEventKind.ACTION_COMPLETED

    @model_validator(mode="after")
    def emits_only_completion(self) -> CompletionEvidence:
        """Prevent a completed action from smuggling an unrelated workflow event."""

        if self.emitted_event is not RouterEventKind.ACTION_COMPLETED:
            raise ValueError("completion evidence must emit action_completed")
        return self


class FrontendCompositionContract(RouterModel):
    """The required, explicit UI composition and dependency-injection handoff surface."""

    component_boundaries: NonBlankText
    composition_root_reference: OpaqueMetadataId
    dependency_scope: NonBlankText
    injected_interfaces: tuple[OpaqueMetadataId, ...] = Field(min_length=1)
    production_bindings: NonBlankText
    test_doubles: NonBlankText
    state_acceptance: NonBlankText


class ImplementationHandoff(RouterModel):
    """Approved implementation input with opaque references and separated responsibilities."""

    handoff_reference: OpaqueMetadataId
    ticket_reference: OpaqueMetadataId
    approved_spec_reference: OpaqueMetadataId
    expected_main_revision: RevisionDigest
    context_references: tuple[HandoffArtifactReference, ...] = Field(min_length=1)
    acceptance_references: tuple[OpaqueMetadataId, ...] = Field(min_length=1)
    tdd_references: tuple[OpaqueMetadataId, ...] = Field(min_length=1)
    scope: TicketScope
    frontend_composition: FrontendCompositionContract | None = None
    non_frontend_reason: NonBlankText | None = None
    control_owner_id: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId
    reviewer_id: OpaqueMetadataId
    ticket_docs_commit: ReviewedCommitReference | None = None
    handoff_docs_commit: ReviewedCommitReference | None = None

    @model_validator(mode="after")
    def enforces_role_separation_and_frontend_contract(self) -> ImplementationHandoff:
        """Reject owner collisions and incomplete frontend/non-frontend declarations."""

        if self.control_owner_id == self.implementation_owner_id:
            raise ValueError("control_owner_id and implementation_owner_id must be different")
        if self.reviewer_id == self.implementation_owner_id:
            raise ValueError("reviewer_id and implementation_owner_id must be different")
        if self.scope is TicketScope.FRONTEND:
            if self.frontend_composition is None or self.non_frontend_reason is not None:
                raise ValueError("frontend handoffs require composition data and no non-frontend reason")
        elif self.frontend_composition is not None or self.non_frontend_reason is None:
            raise ValueError("non-frontend handoffs require an N/A reason and no frontend composition")
        return self

    @property
    def handoff_ref(self) -> str:
        """Expose the specification terminology without storing a second field."""

        return self.handoff_reference


class ImplementationReturn(RouterModel):
    """Metadata-only return from an implementation owner; changes re-enter Grill."""

    ticket_reference: OpaqueMetadataId
    status: ImplementationReturnStatus
    evidence_references: tuple[OpaqueMetadataId, ...] = Field(min_length=1)
    verification_references: tuple[OpaqueMetadataId, ...] = Field(min_length=1)
    evidence_digest: EvidenceDigest
    emitted_event: RouterEventKind

    @model_validator(mode="after")
    def status_matches_the_only_legal_return_event(self) -> ImplementationReturn:
        """Keep scope changes on the requirement-change route rather than silent patching."""

        if self.status is ImplementationReturnStatus.CHANGE_DETECTED:
            if self.emitted_event is not RouterEventKind.REQUIREMENT_CHANGED:
                raise ValueError("change_detected must emit requirement_changed")
        elif self.emitted_event not in (
            RouterEventKind.ACTION_COMPLETED,
            RouterEventKind.IMPLEMENTATION_RETURNED,
        ):
            raise ValueError("completed and blocked returns must emit action_completed")
        return self


class CapabilityRef(RouterModel):
    """An allowlisted capability, not an authority grant."""

    capability_id: NonBlankText
    version: NonBlankText
    agent_profile: NonBlankText

    @model_validator(mode="after")
    def capability_id_is_not_a_descriptive_profile(self) -> CapabilityRef:
        """Keep an authority-bearing opaque capability separate from its description."""

        if self.capability_id == self.agent_profile:
            raise ValueError("capability ID must not equal an agent profile")
        return self


class CollaborationTopologyPlan(RouterModel):
    """A finite topology and its named capabilities, never a host-thread grant."""

    topology: CollaborationTopology
    control_plane: CapabilityRef
    implementation_owner: CapabilityRef
    reviewer: CapabilityRef
    host_thread_references: tuple[OpaqueMetadataId, ...] = ()

    @model_validator(mode="after")
    def roles_are_distinct(self) -> CollaborationTopologyPlan:
        """Prevent the implementation capability from colliding with either reviewer role."""

        if self.implementation_owner.capability_id in (
            self.control_plane.capability_id,
            self.reviewer.capability_id,
        ):
            raise ValueError("implementation capability must be role-isolated")
        return self


class RouterEvent(RouterModel):
    """A unique, validated request to re-evaluate the workflow."""

    event_id: NonBlankText
    kind: RouterEventKind
    completion_evidence: CompletionEvidence | None = None
    implementation_return: ImplementationReturn | None = None
    implementation_handoff: ImplementationHandoff | None = None
    dispatch_confirmation: TicketDispatchConfirmation | None = None
    dispatch_receipt: TicketDispatchReceipt | None = None
    lane_kind: LaneKind | None = None
    lane_id: OpaqueMetadataId | None = None
    ticket_proposal: TicketProposal | None = None

    @model_validator(mode="after")
    def completion_metadata_matches_event(self) -> RouterEvent:
        """Allow legacy action events while rejecting completion evidence on unrelated events."""

        if self.completion_evidence is not None and self.kind is not RouterEventKind.ACTION_COMPLETED:
            raise ValueError("completion_evidence is valid only for action_completed")
        if self.completion_evidence is not None and self.implementation_return is not None:
            raise ValueError("completion_evidence and implementation_return cannot share an event")
        if self.implementation_handoff is not None:
            if self.completion_evidence is not None or self.implementation_return is not None:
                raise ValueError("implementation_handoff cannot share an event with completion or return")
            if self.kind not in (
                RouterEventKind.APPROVAL_GRANTED,
                RouterEventKind.TICKET_DISPATCH_REQUIRED,
            ):
                raise ValueError("implementation_handoff requires a ticket dispatch lifecycle event")
        if self.implementation_return is not None and self.implementation_return.emitted_event is not self.kind:
            raise ValueError("implementation_return event must match router event kind")
        if self.dispatch_confirmation is not None or self.dispatch_receipt is not None:
            if self.kind not in (
                RouterEventKind.TICKET_DISPATCH_REQUIRED,
                RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
            ):
                raise ValueError("dispatch metadata requires a ticket dispatch event")
        if (
            self.dispatch_receipt is not None
            and self.kind is not RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED
        ):
            raise ValueError("dispatch receipts require confirmed dispatch")
        if self.ticket_proposal is not None and self.kind is not RouterEventKind.TICKET_DISPATCH_REQUIRED:
            raise ValueError("ticket proposals require a dispatch-required event")
        if self.lane_kind is None and self.lane_id is not None:
            raise ValueError("lane_id requires lane_kind")
        if self.lane_kind is not None and self.lane_id is None:
            raise ValueError("lane_kind requires lane_id")
        return self


class RouterState(RouterModel):
    """The compact state required for one deterministic routing decision."""

    project_id: NonBlankText
    stage: ProcessStage
    authority_state: AuthorityState
    delivery_stage: DeliveryStage
    artifact_refs: tuple[ArtifactRef, ...]
    topology: CollaborationTopology | None = None
    collaboration_plan: CollaborationTopologyPlan | None = None
    pending_dispatch: PendingDispatchDescriptor | None = None


class PlanningLaneState(RouterModel):
    """Independent planning-lane state created by a confirmed ticket dispatch."""

    project_id: NonBlankText
    stage: ProcessStage
    topology: CollaborationTopology
    artifact_refs: tuple[ArtifactRef, ...]
    active_ticket_refs: tuple[OpaqueMetadataId, ...]
    context_view_id: OpaqueMetadataId
    side_context_id: OpaqueMetadataId
    event_id: OpaqueMetadataId
    safety_ceiling: PositiveTokenBudget


class TicketLaneState(RouterModel):
    """Independent ticket-execution state with no mutable planning-lane handle."""

    ticket_id: OpaqueMetadataId
    dispatch_state: TicketDispatchState
    execution_stage: ProcessStage
    expected_main_revision: RevisionDigest
    source_grants: tuple[ArtifactKind, ...]
    context_view_id: OpaqueMetadataId
    side_context_id: OpaqueMetadataId
    event_id: OpaqueMetadataId
    worktree_fingerprint: WorktreeFingerprint
    branch_fingerprint: BranchFingerprint
    safety_ceiling: PositiveTokenBudget
    implementation_capability: CapabilityRef
    reviewer: CapabilityRef


class CollaborationDispatchPlan(RouterModel):
    """The immutable pair of planning and ticket lanes from one receipt."""

    receipt: TicketDispatchReceipt
    planning_lane: PlanningLaneState
    ticket_lane: TicketLaneState

    @model_validator(mode="after")
    def has_one_exact_named_ticket_lane(self) -> CollaborationDispatchPlan:
        """Bind the receipt to named actor identities, never descriptive profiles."""

        if (
            self.receipt.ticket_reference != self.ticket_lane.ticket_id
            or self.receipt.expected_main_revision != self.ticket_lane.expected_main_revision
            or self.receipt.worktree_fingerprint != self.ticket_lane.worktree_fingerprint
            or self.receipt.branch_fingerprint != self.ticket_lane.branch_fingerprint
            or self.receipt.implementation_owner_id
            != self.ticket_lane.implementation_capability.capability_id
            or self.receipt.ticket_reference not in self.planning_lane.active_ticket_refs
        ):
            raise ValueError("dispatch receipt must bind one exact named ticket lane")
        return self

    def with_planning_progress(
        self,
        *,
        stage: ProcessStage,
        event_id: OpaqueMetadataId,
    ) -> CollaborationDispatchPlan:
        """Advance only the planning descriptor while preserving ticket execution state."""

        return self.model_copy(
            update={
                "planning_lane": self.planning_lane.model_copy(
                    update={"stage": stage, "event_id": event_id}
                )
            }
        )


class RouterBlocker(RouterModel):
    """A typed explanation for a fail-closed decision."""

    code: BlockerCode
    detail: NonBlankText


class ConsumerFingerprint(RouterModel):
    """Identifies the agent/worktree execution that consumed a Context span."""

    agent_profile: NonBlankText
    profile_version: NonBlankText
    worktree_id: NonBlankText
    execution_id: NonBlankText


class ContextReference(RouterModel):
    """One metadata-only, one-time reference from source Context to a target artifact."""

    source_context: ArtifactRef
    source_revision: NonBlankText
    source_span: NonBlankText
    side_context_id: NonBlankText
    consumer_fingerprint: ConsumerFingerprint
    target_artifact: ArtifactRef
    status: ReferenceStatus = ReferenceStatus.OPEN

    @model_validator(mode="after")
    def revision_matches_source(self) -> ContextReference:
        """Prevent a reference from claiming a revision different from its source."""

        if self.source_revision != self.source_context.revision:
            raise ValueError("source_revision must match source_context.revision")
        return self


class ContextView(RouterModel):
    """A persistent descriptor for a temporary Context packet; it contains no raw text."""

    view_id: NonBlankText
    purpose: NonBlankText
    references: tuple[ContextReference, ...]
    token_budget: PositiveTokenBudget
    invalidation_events: tuple[RouterEventKind, ...]


class RouterDecision(RouterModel):
    """The only legal output of the pure router engine."""

    skill_reference: SkillReference
    expected_return: ExpectedReturnContract
    outcome: RouterOutcome
    continuation: ContinuationDirective
    next_stage: ProcessStage | None
    required_sources: tuple[ArtifactRef, ...]
    context_view: ContextView | None = None
    eligible_capabilities: tuple[CapabilityRef, ...]
    blockers: tuple[RouterBlocker, ...] = ()
    wait_reason: HumanWaitReason | None = None
    dispatch_plan: CollaborationDispatchPlan | None = None
    ticket_lane_capabilities: tuple[CapabilityRef, ...] = ()
    ticket_proposal: TicketProposal | None = None
    pending_dispatch: PendingDispatchDescriptor | None = None

    @model_validator(mode="after")
    def decision_shape_is_consistent(self) -> RouterDecision:
        """Ensure advance and fail-closed outcomes cannot be represented ambiguously."""

        if self.outcome in (RouterOutcome.ADVANCE, RouterOutcome.RETRY) and self.next_stage is None:
            raise ValueError("advancing and retry decisions require next_stage")
        if (
            self.outcome is RouterOutcome.ADVANCE
            and self.continuation is not ContinuationDirective.AUTO_CONTINUE
        ):
            raise ValueError("advance decisions must auto-continue")
        if (
            self.outcome is RouterOutcome.RETRY
            and self.continuation is not ContinuationDirective.AUTO_CONTINUE
        ):
            raise ValueError("retry decisions must auto-continue")
        if self.outcome is RouterOutcome.SUSPEND and self.next_stage is not None:
            raise ValueError("suspend decisions must not invent a next_stage")
        if (
            self.outcome is RouterOutcome.SUSPEND
            and self.continuation is ContinuationDirective.AUTO_CONTINUE
        ):
            raise ValueError("suspend decisions must wait or halt")
        if self.outcome is RouterOutcome.STOP and self.next_stage is not ProcessStage.STOPPED:
            raise ValueError("stop decisions must target stopped")
        if self.outcome is RouterOutcome.STOP and self.continuation is not ContinuationDirective.HALT:
            raise ValueError("stop decisions must halt")
        if self.continuation is ContinuationDirective.WAIT_FOR_HUMAN:
            if self.outcome is not RouterOutcome.SUSPEND or self.wait_reason is None:
                raise ValueError("human waits require a suspended decision and a precise wait reason")
            if self.required_sources or self.eligible_capabilities or self.context_view is not None:
                raise ValueError("human waits cannot grant Context or capabilities")
            if self.dispatch_plan is not None:
                raise ValueError("human waits cannot grant dispatch plans")
            if self.ticket_lane_capabilities:
                raise ValueError("human waits cannot grant ticket-lane capabilities")
            if self.pending_dispatch is not None and self.ticket_proposal is None:
                raise ValueError("pending dispatch state requires its opened ticket proposal")
            if (
                self.pending_dispatch is not None
                and self.ticket_proposal is not None
                and (
                    self.pending_dispatch.ticket_reference != self.ticket_proposal.ticket_reference
                    or self.pending_dispatch.proposal_revision != self.ticket_proposal.proposal_revision
                    or self.pending_dispatch.dispatch_question_id != self.ticket_proposal.dispatch_question_id
                    or self.pending_dispatch.implementation_owner_id
                    != self.ticket_proposal.implementation_owner_id
                )
            ):
                raise ValueError("pending dispatch state must match its opened ticket proposal")
        elif self.ticket_proposal is not None or self.pending_dispatch is not None:
            raise ValueError("automatic or halted decisions cannot carry pending dispatch state")
        elif self.wait_reason is not None:
            raise ValueError("only human waits may declare a wait reason")
        if self.continuation is ContinuationDirective.HALT and self.dispatch_plan is not None:
            raise ValueError("halted decisions cannot grant dispatch plans")
        if self.continuation is ContinuationDirective.HALT and self.ticket_lane_capabilities:
            raise ValueError("halted decisions cannot grant ticket-lane capabilities")
        if self.continuation is ContinuationDirective.HALT and self.ticket_proposal is not None:
            raise ValueError("halted decisions cannot carry an opened proposal")
        return self


class SourceSnippet(RouterModel):
    """Raw source text returned by a source adapter; never store this in shared state."""

    source: ArtifactRef
    span: NonBlankText
    text: NonBlankText


@dataclass(frozen=True, slots=True)
class ContextPacket:
    """Ephemeral raw Context held only by the consuming Agent/worktree."""

    snippets: tuple[SourceSnippet, ...]


@dataclass(frozen=True, slots=True)
class ResolvedContext:
    """Pair a durable descriptor with an ephemeral raw packet."""

    view: ContextView
    packet: ContextPacket
