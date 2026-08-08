"""Metadata-only policy reads and Router-owned fixed dispatch responses.

The policy source is an ephemeral boundary.  It may provide a typed metadata
record, but document text is never accepted by, returned from, or stored in a
Router model.  Dispatch text is rendered only from a live plan retained by the
same :class:`PrivateRouterClient` that received the pending dispatch.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Annotated, Protocol

from pydantic import Field, model_validator

from .contracts import (
    EvidenceDigest,
    NonBlankText,
    OpaqueMetadataId,
    PendingDispatchDescriptor,
    RevisionDigest,
    RouterModel,
)

if TYPE_CHECKING:
    from .private_router import ContinuationPlan

CommitReference = Annotated[str, Field(pattern=r"^[0-9a-f]{7,64}$")]


class PolicyReadOutcome(str, Enum):
    """Finite outcome of an ephemeral policy metadata read."""

    LOADED = "loaded"
    HALT = "halt"


class PolicyReadError(str, Enum):
    """Stable errors that never echo source or exception detail."""

    SOURCE_UNAVAILABLE = "source_unavailable"
    SOURCE_FAILURE = "source_failure"
    INVALID_DOCUMENT = "invalid_document"


class PolicyDocumentMetadata(RouterModel):
    """The only policy information allowed to cross the source boundary."""

    source_id: OpaqueMetadataId
    revision: RevisionDigest
    evidence_digest: EvidenceDigest


class PolicyDocumentSource(Protocol):
    """Ephemeral source port; implementations must return typed metadata."""

    def read(self) -> object:
        """Read a document transiently without returning its text to the Router."""


class PendingDispatchPlanOwner(Protocol):
    """The narrow authority surface needed by the trusted formatter."""

    def owns_pending_dispatch_plan(self, plan: object) -> bool:
        """Return true only for the exact live plan object retained by the client."""


class PolicyDocumentResult(RouterModel):
    """Metadata-only result; deliberately has no text or arbitrary detail field."""

    outcome: PolicyReadOutcome
    metadata: PolicyDocumentMetadata | None = None
    error: PolicyReadError | None = None

    @model_validator(mode="after")
    def result_shape_is_unambiguous(self) -> PolicyDocumentResult:
        """Require a metadata record on success and a stable error on halt."""

        if self.outcome is PolicyReadOutcome.LOADED:
            if self.metadata is None or self.error is not None:
                raise ValueError("loaded policy result requires metadata only")
        elif self.metadata is not None or self.error is None:
            raise ValueError("halted policy result requires one stable error")
        return self


def read_policy_document(source: PolicyDocumentSource | None) -> PolicyDocumentResult:
    """Read only allowlisted policy metadata and fail closed for every other value."""

    if source is None:
        return PolicyDocumentResult(
            outcome=PolicyReadOutcome.HALT,
            error=PolicyReadError.SOURCE_UNAVAILABLE,
        )
    try:
        result = source.read()
    except Exception:
        return PolicyDocumentResult(
            outcome=PolicyReadOutcome.HALT,
            error=PolicyReadError.SOURCE_FAILURE,
        )
    if not isinstance(result, PolicyDocumentMetadata):
        return PolicyDocumentResult(
            outcome=PolicyReadOutcome.HALT,
            error=PolicyReadError.INVALID_DOCUMENT,
        )
    return PolicyDocumentResult(outcome=PolicyReadOutcome.LOADED, metadata=result)


class RenderOutcome(str, Enum):
    """Finite formatter outcomes."""

    RENDERED = "rendered"
    HALT = "halt"


class RenderError(str, Enum):
    """Stable response errors with no free-form detail."""

    UNTRUSTED_RESPONSE = "untrusted_response"
    INVALID_RESPONSE = "invalid_response"
    ARTIFACT_MISMATCH = "artifact_mismatch"
    FORMATTER_FAILURE = "formatter_failure"
    FORMATTER_OUTPUT_INVALID = "formatter_output_invalid"


class CommittedDispatchArtifacts(RouterModel):
    """Metadata references for the reviewed ticket and handoff documents."""

    ticket_docs_commit: CommitReference
    ticket_reference: OpaqueMetadataId
    handoff_docs_commit: CommitReference
    handoff_reference: OpaqueMetadataId


class FixedDispatchResponse(RouterModel):
    """A response candidate bound to one Router-created pending descriptor."""

    pending_dispatch: PendingDispatchDescriptor
    ticket_docs_commit: CommitReference
    ticket_reference: OpaqueMetadataId
    handoff_docs_commit: CommitReference
    handoff_reference: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId

    @model_validator(mode="after")
    def binds_exact_pending_dispatch(self) -> FixedDispatchResponse:
        """Prevent arbitrary ticket, handoff, or owner substitutions."""

        pending = self.pending_dispatch
        if (
            self.ticket_reference != pending.ticket_reference
            or self.handoff_reference != pending.reviewed_handoff_reference
            or self.implementation_owner_id != pending.implementation_owner_id
        ):
            raise ValueError("fixed response must match the pending dispatch descriptor")
        return self


class RenderedDispatchResponse(RouterModel):
    """The only response result exposed to the caller."""

    outcome: RenderOutcome
    text: NonBlankText | None = None
    error: RenderError | None = None

    @model_validator(mode="after")
    def output_shape_is_safe(self) -> RenderedDispatchResponse:
        """Never expose text together with a halt or omit text after rendering."""

        if self.outcome is RenderOutcome.RENDERED:
            if self.text is None or self.error is not None:
                raise ValueError("rendered response requires text only")
        elif self.text is not None or self.error is None:
            raise ValueError("halted response requires one stable error")
        return self


class DispatchResponseFormatter:
    """Deterministic formatter for a validated Router-owned response candidate."""

    def format(self, response: FixedDispatchResponse) -> str:
        """Return the fixed response shape and no source-derived content."""

        return (
            "工單 ready\n"
            f"- commit：{response.ticket_docs_commit}\n"
            f"- 工單：{response.ticket_reference}\n\n"
            "文件交接\n"
            f"- commit：{response.handoff_docs_commit}\n"
            f"- implementation owner：{response.implementation_owner_id}\n"
            f"- 工單 {response.ticket_reference} 是否已交付給 implementation owner "
            f"{response.implementation_owner_id}？"
        )


def _halt(error: RenderError) -> RenderedDispatchResponse:
    return RenderedDispatchResponse(outcome=RenderOutcome.HALT, error=error)


def render_dispatch_response(
    response: object,
    formatter: DispatchResponseFormatter | None = None,
) -> RenderedDispatchResponse:
    """Reject direct rendering; a live Private Router client is the authority."""

    del response, formatter
    return _halt(RenderError.UNTRUSTED_RESPONSE)


def render_trusted_dispatch_response(
    *,
    client: PendingDispatchPlanOwner,
    plan: ContinuationPlan,
    artifacts: CommittedDispatchArtifacts,
    formatter: DispatchResponseFormatter | None = None,
) -> RenderedDispatchResponse:
    """Render only when the client proves object-identity ownership of the plan."""

    if not client.owns_pending_dispatch_plan(plan):
        return _halt(RenderError.UNTRUSTED_RESPONSE)
    try:
        from .private_router import ContinuationMode, ContinuationPlan

        if not isinstance(plan, ContinuationPlan):
            return _halt(RenderError.INVALID_RESPONSE)
        pending = plan.pending_dispatch
        proposal = plan.ticket_proposal
        response = plan.response
        if (
            plan.mode is not ContinuationMode.WAIT_FOR_HUMAN
            or pending is None
            or proposal is None
            or response is None
            or response.pending_dispatch != pending
            or proposal.ticket_reference != pending.ticket_reference
            or artifacts.ticket_reference != pending.ticket_reference
            or artifacts.handoff_reference != pending.reviewed_handoff_reference
        ):
            return _halt(RenderError.INVALID_RESPONSE)
        candidate = FixedDispatchResponse(
            pending_dispatch=pending,
            ticket_docs_commit=artifacts.ticket_docs_commit,
            ticket_reference=artifacts.ticket_reference,
            handoff_docs_commit=artifacts.handoff_docs_commit,
            handoff_reference=artifacts.handoff_reference,
            implementation_owner_id=pending.implementation_owner_id,
        )
        deterministic = DispatchResponseFormatter()
        expected = deterministic.format(candidate)
        selected = formatter or deterministic
        rendered = selected.format(candidate)
        if rendered != expected:
            return _halt(RenderError.FORMATTER_OUTPUT_INVALID)
        return RenderedDispatchResponse(outcome=RenderOutcome.RENDERED, text=rendered)
    except Exception:
        return _halt(RenderError.FORMATTER_FAILURE)
