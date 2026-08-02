"""Strongly typed contracts for the reusable workflow router."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


NonBlankText = Annotated[str, Field(min_length=1)]
PositiveTokenBudget = Annotated[int, Field(gt=0)]


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
    NO_DECLARED_TRANSITION = "no_declared_transition"
    SOURCE_UNAVAILABLE = "source_unavailable"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"


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


class RouterEvent(RouterModel):
    """A unique, validated request to re-evaluate the workflow."""

    event_id: NonBlankText
    kind: RouterEventKind


class RouterState(RouterModel):
    """The compact state required for one deterministic routing decision."""

    project_id: NonBlankText
    stage: ProcessStage
    authority_state: AuthorityState
    delivery_stage: DeliveryStage
    artifact_refs: tuple[ArtifactRef, ...]


class CapabilityRef(RouterModel):
    """An allowlisted capability, not an authority grant."""

    capability_id: NonBlankText
    version: NonBlankText
    agent_profile: NonBlankText


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

    outcome: RouterOutcome
    next_stage: ProcessStage | None
    required_sources: tuple[ArtifactRef, ...]
    context_view: ContextView | None = None
    eligible_capabilities: tuple[CapabilityRef, ...]
    blockers: tuple[RouterBlocker, ...] = ()

    @model_validator(mode="after")
    def decision_shape_is_consistent(self) -> RouterDecision:
        """Ensure advance and fail-closed outcomes cannot be represented ambiguously."""

        if self.outcome is RouterOutcome.ADVANCE and self.next_stage is None:
            raise ValueError("advance decisions require next_stage")
        if self.outcome is RouterOutcome.SUSPEND and self.next_stage is not None:
            raise ValueError("suspend decisions must not invent a next_stage")
        if self.outcome is RouterOutcome.STOP and self.next_stage is not ProcessStage.STOPPED:
            raise ValueError("stop decisions must target stopped")
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
