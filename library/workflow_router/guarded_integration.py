"""Typed, fake-backed guarded integration and Grill-audit orchestration."""

from __future__ import annotations

from enum import Enum
from typing import Protocol

from pydantic import Field, model_validator

from .contracts import (
    ImplementationReturn,
    ImplementationReturnStatus,
    NonBlankText,
    OpaqueMetadataId,
    ProcessStage,
    RevisionDigest,
    RouterEventKind,
    RouterModel,
)


class ProposalState(str, Enum):
    """The dependent proposal states visible to the planning lane."""

    PLANNED = "planned"
    WOKEN = "woken"


class IntegrationStatus(str, Enum):
    """Typed results returned by the injected local integration port."""

    COMPLETED = "completed"
    STALE_REVISION = "stale_revision"
    DIRTY_MAIN = "dirty_main"
    CONFLICT = "conflict"
    VALIDATION_FAILED = "validation_failed"


class AuditDisposition(str, Enum):
    """The only Grill-audit dispositions for a pending local integration."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"


class CoordinatorOutcome(str, Enum):
    """Safe outcomes emitted by the ticket-02 coordinator."""

    PENDING_AUDIT = "pending_audit"
    CODE_REVIEW = "code_review"
    CORRECTION = "correction"
    HALT = "halt"


class GuardedIntegrationError(str, Enum):
    """Stable fail-closed errors with no adapter or source disclosure."""

    INVALID_RETURN = "invalid_return"
    DUPLICATE_RETURN = "duplicate_return"
    STALE_MAIN_REVISION = "stale_main_revision"
    DIRTY_MAIN = "dirty_main"
    INTEGRATION_CONFLICT = "integration_conflict"
    VALIDATION_FAILED = "validation_failed"
    LOCK_CONTENDED = "lock_contended"
    LOCK_FAILURE = "lock_failure"
    ADAPTER_UNAVAILABLE = "adapter_unavailable"
    ADAPTER_FAILURE = "adapter_failure"
    INVALID_AUDIT = "invalid_audit"
    PENDING_AUDIT_ACTIVE = "pending_audit_active"


class MainSnapshot(RouterModel):
    """The trusted metadata snapshot against which one return is guarded."""

    revision: RevisionDigest
    is_clean: bool
    has_conflict: bool = False


class DependentProposal(RouterModel):
    """A planning proposal that may be woken by exactly its dependency return."""

    proposal_id: OpaqueMetadataId
    dependency_ticket_reference: OpaqueMetadataId
    state: ProposalState
    context_view_id: OpaqueMetadataId
    event_id: OpaqueMetadataId


class ImplementationReturnEvent(RouterModel):
    """A metadata-only implementation return with lane identity and base revision."""

    event_id: OpaqueMetadataId
    correlation_id: OpaqueMetadataId
    event_kind: RouterEventKind
    ticket_reference: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId
    reviewer_id: OpaqueMetadataId
    expected_main_revision: RevisionDigest
    worktree_fingerprint: OpaqueMetadataId
    branch_fingerprint: OpaqueMetadataId
    planning_context_view_id: OpaqueMetadataId
    ticket_context_view_id: OpaqueMetadataId
    planning_event_id: OpaqueMetadataId
    ticket_event_id: OpaqueMetadataId
    implementation_return: ImplementationReturn

    @model_validator(mode="after")
    def return_is_bound_to_one_ticket_and_two_lanes(self) -> ImplementationReturnEvent:
        """Reject mismatched event contracts before any integration side effect."""

        if self.event_kind is not RouterEventKind.ACTION_COMPLETED:
            raise ValueError("implementation return events must be action_completed")
        if self.implementation_return.ticket_reference != self.ticket_reference:
            raise ValueError("implementation return ticket does not match its event")
        if self.implementation_owner_id == self.reviewer_id:
            raise ValueError("implementation owner and reviewer must remain distinct")
        if self.planning_context_view_id == self.ticket_context_view_id:
            raise ValueError("planning and ticket ContextView IDs must remain distinct")
        if self.planning_event_id == self.ticket_event_id:
            raise ValueError("planning and ticket event IDs must remain distinct")
        return self


class IntegrationRequest(RouterModel):
    """The only metadata passed to the injected local integration port."""

    ticket_reference: OpaqueMetadataId
    correlation_id: OpaqueMetadataId
    expected_main_revision: RevisionDigest
    implementation_owner_id: OpaqueMetadataId
    reviewer_id: OpaqueMetadataId
    worktree_fingerprint: OpaqueMetadataId
    branch_fingerprint: OpaqueMetadataId


class IntegrationResult(RouterModel):
    """A deterministic fake-port result; it never contains raw Git output."""

    status: IntegrationStatus
    integrated_main_revision: RevisionDigest | None = None

    @model_validator(mode="after")
    def completed_result_has_revision(self) -> IntegrationResult:
        """Require a new main revision only when the fake integration completed."""

        if self.status is IntegrationStatus.COMPLETED and self.integrated_main_revision is None:
            raise ValueError("completed integration must return its revision digest")
        if self.status is not IntegrationStatus.COMPLETED and self.integrated_main_revision is not None:
            raise ValueError("failed integration cannot claim an integrated revision")
        return self


class PendingAudit(RouterModel):
    """The local main state after integration and before the Grill audit."""

    ticket_reference: OpaqueMetadataId
    correlation_id: OpaqueMetadataId
    integrated_main_revision: RevisionDigest
    audit_event_id: OpaqueMetadataId
    state: NonBlankText = "PENDING_AUDIT"

    @model_validator(mode="after")
    def state_is_pending_audit(self) -> PendingAudit:
        """Keep the guarded state closed; callers cannot forge a later stage."""

        if self.state != "PENDING_AUDIT":
            raise ValueError("pending audit state must remain PENDING_AUDIT")
        return self


class AuditRequest(RouterModel):
    """A typed request for the existing Grill audit gate."""

    ticket_reference: OpaqueMetadataId
    correlation_id: OpaqueMetadataId
    pending_audit: PendingAudit

    @model_validator(mode="after")
    def request_matches_pending_audit(self) -> AuditRequest:
        """Bind the audit request to the exact pending integration."""

        if (
            self.ticket_reference != self.pending_audit.ticket_reference
            or self.correlation_id != self.pending_audit.correlation_id
        ):
            raise ValueError("audit request does not match pending integration")
        return self


class AuditDecision(RouterModel):
    """The typed result returned by the injected Grill-audit boundary."""

    ticket_reference: OpaqueMetadataId
    correlation_id: OpaqueMetadataId
    disposition: AuditDisposition


class CorrectionRoute(RouterModel):
    """A correction handoff descriptor with no push, deploy, or implementation grant."""

    ticket_reference: OpaqueMetadataId
    correlation_id: OpaqueMetadataId
    action_label: NonBlankText = "correction_worktree"

    @model_validator(mode="after")
    def route_is_correction_only(self) -> CorrectionRoute:
        """Prevent a correction descriptor from being repurposed as delivery."""

        if self.action_label != "correction_worktree":
            raise ValueError("correction routes must remain correction_worktree")
        return self


class GuardedIntegrationDecision(RouterModel):
    """The safe coordinator result; grants are explicit and default to false."""

    outcome: CoordinatorOutcome
    error: GuardedIntegrationError | None = None
    next_stage: ProcessStage | None = None
    action_label: NonBlankText | None = None
    awakened_proposal_ids: tuple[OpaqueMetadataId, ...] = ()
    pending_audit: PendingAudit | None = None
    audit_request: AuditRequest | None = None
    correction_route: CorrectionRoute | None = None
    handoff_allowed: bool = False
    push_allowed: bool = False
    deploy_allowed: bool = False
    dependent_implementation_allowed: bool = False

    @model_validator(mode="after")
    def safe_shape(self) -> GuardedIntegrationDecision:
        """Prevent a halt or audit transition from carrying delivery grants."""

        if self.outcome is CoordinatorOutcome.HALT:
            if self.error is None or self.next_stage is not None or self.action_label is not None:
                raise ValueError("halt decisions require only a stable error")
            if (
                self.awakened_proposal_ids
                or self.pending_audit is not None
                or self.audit_request is not None
                or self.correction_route is not None
            ):
                raise ValueError("halt decisions cannot wake proposals or create an audit")
        if self.outcome is CoordinatorOutcome.PENDING_AUDIT:
            if self.pending_audit is None or self.audit_request is None:
                raise ValueError("pending-audit decisions require an audit request")
            if (
                self.error is not None
                or self.next_stage is not None
                or self.action_label is not None
                or self.correction_route is not None
            ):
                raise ValueError("pending-audit decisions do not advance the workflow stage")
        if self.outcome is CoordinatorOutcome.CODE_REVIEW:
            if self.next_stage is not ProcessStage.REVIEW or self.action_label != "code_review":
                raise ValueError("approved audits route only to code review")
            if (
                self.error is not None
                or self.awakened_proposal_ids
                or self.pending_audit is not None
                or self.audit_request is not None
                or self.correction_route is not None
            ):
                raise ValueError("approved audits consume pending-audit state")
        if self.outcome is CoordinatorOutcome.CORRECTION:
            if self.correction_route is None:
                raise ValueError("changes-requested audits require a correction route")
            if (
                self.error is not None
                or self.next_stage is not None
                or self.action_label is not None
                or self.awakened_proposal_ids
                or self.pending_audit is not None
                or self.audit_request is not None
            ):
                raise ValueError("correction routes cannot carry delivery or audit state")
        if self.handoff_allowed or self.push_allowed or self.deploy_allowed or self.dependent_implementation_allowed:
            raise ValueError("guarded integration never grants delivery side effects")
        return self


class IntegrationPort(Protocol):
    """Injected fake-only integration capability; no real Git operation is implied."""

    def integrate(self, request: IntegrationRequest) -> IntegrationResult:
        """Return a typed deterministic result."""


class IntegrationLock(Protocol):
    """Injected exclusive lock boundary for one local integration."""

    def try_acquire(self) -> bool:
        """Return false on contention without waiting or merging."""

    def release(self) -> None:
        """Release the local fake lock."""


class AuditSink(Protocol):
    """Injected Grill-audit request sink."""

    def request_audit(self, request: AuditRequest) -> None:
        """Queue exactly one typed audit request."""


class ReturnEventSource(Protocol):
    """Injected event source that can deliver a typed return only."""

    def next_return(self) -> ImplementationReturnEvent | None:
        """Return one event, or none when no return is available."""


class GuardedIntegrationCoordinator:
    """Guard implementation returns, wake dependents, and route one Grill audit."""

    def __init__(
        self,
        *,
        integration_port: IntegrationPort,
        integration_lock: IntegrationLock,
        audit_sink: AuditSink,
        main_snapshot: MainSnapshot,
        dependent_proposals: tuple[DependentProposal, ...],
    ) -> None:
        self._integration_port = integration_port
        self._integration_lock = integration_lock
        self._audit_sink = audit_sink
        self._main_snapshot = main_snapshot
        self._dependent_proposals = dependent_proposals
        self._seen_correlations: set[str] = set()
        self._seen_event_ids: set[str] = set()
        self._pending_audit: PendingAudit | None = None

    def consume_return(self, source: ReturnEventSource | None) -> GuardedIntegrationDecision:
        """Read only an injected event; adapter absence or exceptions halt safely."""

        if source is None:
            return self._halt(GuardedIntegrationError.ADAPTER_UNAVAILABLE)
        try:
            event = source.next_return()
        except Exception:
            return self._halt(GuardedIntegrationError.ADAPTER_FAILURE)
        return self.handle_return(event)

    def handle_return(
        self,
        event: ImplementationReturnEvent | None,
    ) -> GuardedIntegrationDecision:
        """Perform every guard before invoking the injected integration port."""

        if event is None:
            return self._halt(GuardedIntegrationError.INVALID_RETURN)
        try:
            event = ImplementationReturnEvent.model_validate(event.model_dump())
        except Exception:
            return self._halt(GuardedIntegrationError.INVALID_RETURN)
        if event.implementation_return.status is not ImplementationReturnStatus.COMPLETED:
            return self._halt(GuardedIntegrationError.INVALID_RETURN)
        if event.correlation_id in self._seen_correlations or event.event_id in self._seen_event_ids:
            return self._halt(GuardedIntegrationError.DUPLICATE_RETURN)
        if (
            self._pending_audit is not None
            and self._pending_audit.ticket_reference == event.ticket_reference
        ):
            return self._halt(GuardedIntegrationError.PENDING_AUDIT_ACTIVE)
        self._seen_correlations.add(event.correlation_id)
        self._seen_event_ids.add(event.event_id)
        if event.expected_main_revision != self._main_snapshot.revision:
            return self._halt(GuardedIntegrationError.STALE_MAIN_REVISION)
        if not self._main_snapshot.is_clean:
            return self._halt(GuardedIntegrationError.DIRTY_MAIN)
        if self._main_snapshot.has_conflict:
            return self._halt(GuardedIntegrationError.INTEGRATION_CONFLICT)
        try:
            acquired = self._integration_lock.try_acquire()
        except Exception:
            return self._halt(GuardedIntegrationError.LOCK_FAILURE)
        if not acquired:
            return self._halt(GuardedIntegrationError.LOCK_CONTENDED)
        release_failed = False
        try:
            try:
                integration_result = self._integration_port.integrate(
                    IntegrationRequest(
                        ticket_reference=event.ticket_reference,
                        correlation_id=event.correlation_id,
                        expected_main_revision=event.expected_main_revision,
                        implementation_owner_id=event.implementation_owner_id,
                        reviewer_id=event.reviewer_id,
                        worktree_fingerprint=event.worktree_fingerprint,
                        branch_fingerprint=event.branch_fingerprint,
                    )
                )
            except Exception:
                return self._halt(GuardedIntegrationError.ADAPTER_FAILURE)
        finally:
            try:
                self._integration_lock.release()
            except Exception:
                release_failed = True
        if release_failed:
            return self._halt(GuardedIntegrationError.LOCK_FAILURE)
        try:
            integration_result = IntegrationResult.model_validate(integration_result.model_dump())
        except Exception:
            return self._halt(GuardedIntegrationError.ADAPTER_FAILURE)
        integration_status = integration_result.status
        if integration_status is not IntegrationStatus.COMPLETED:
            return self._halt(self._error_for_integration(integration_status))
        assert integration_result.integrated_main_revision is not None
        pending_audit = PendingAudit(
            ticket_reference=event.ticket_reference,
            correlation_id=event.correlation_id,
            integrated_main_revision=integration_result.integrated_main_revision,
            audit_event_id=f"audit-{event.correlation_id}",
        )
        audit_request = AuditRequest(
            ticket_reference=event.ticket_reference,
            correlation_id=event.correlation_id,
            pending_audit=pending_audit,
        )
        try:
            self._audit_sink.request_audit(audit_request)
        except Exception:
            return self._halt(GuardedIntegrationError.ADAPTER_FAILURE)
        self._pending_audit = pending_audit
        awakened = self._wake_dependents(ticket_reference=event.ticket_reference)
        return GuardedIntegrationDecision(
            outcome=CoordinatorOutcome.PENDING_AUDIT,
            awakened_proposal_ids=awakened,
            pending_audit=pending_audit,
            audit_request=audit_request,
        )

    def handle_audit(self, decision: AuditDecision) -> GuardedIntegrationDecision:
        """Consume one pending audit and preserve the existing Code Review gate."""

        try:
            decision = AuditDecision.model_validate(decision.model_dump())
        except Exception:
            return self._halt(GuardedIntegrationError.INVALID_AUDIT)
        pending = self._pending_audit
        if (
            pending is None
            or pending.ticket_reference != decision.ticket_reference
            or pending.correlation_id != decision.correlation_id
        ):
            return self._halt(GuardedIntegrationError.INVALID_AUDIT)
        self._pending_audit = None
        if decision.disposition is AuditDisposition.APPROVED:
            return GuardedIntegrationDecision(
                outcome=CoordinatorOutcome.CODE_REVIEW,
                next_stage=ProcessStage.REVIEW,
                action_label="code_review",
            )
        return GuardedIntegrationDecision(
            outcome=CoordinatorOutcome.CORRECTION,
            correction_route=CorrectionRoute(
                ticket_reference=decision.ticket_reference,
                correlation_id=decision.correlation_id,
            ),
        )

    def _wake_dependents(self, *, ticket_reference: str) -> tuple[OpaqueMetadataId, ...]:
        """Wake only matching planned proposals; unrelated work remains untouched."""

        awakened: list[OpaqueMetadataId] = []
        next_proposals: list[DependentProposal] = []
        for proposal in self._dependent_proposals:
            if (
                proposal.dependency_ticket_reference == ticket_reference
                and proposal.state is ProposalState.PLANNED
            ):
                next_proposals.append(proposal.model_copy(update={"state": ProposalState.WOKEN}))
                awakened.append(proposal.proposal_id)
            else:
                next_proposals.append(proposal)
        self._dependent_proposals = tuple(next_proposals)
        return tuple(awakened)

    @staticmethod
    def _error_for_integration(status: IntegrationStatus) -> GuardedIntegrationError:
        """Map adapter results to stable internal errors without leaking adapter details."""

        mapping = {
            IntegrationStatus.STALE_REVISION: GuardedIntegrationError.STALE_MAIN_REVISION,
            IntegrationStatus.DIRTY_MAIN: GuardedIntegrationError.DIRTY_MAIN,
            IntegrationStatus.CONFLICT: GuardedIntegrationError.INTEGRATION_CONFLICT,
            IntegrationStatus.VALIDATION_FAILED: GuardedIntegrationError.VALIDATION_FAILED,
        }
        return mapping[status]

    @staticmethod
    def _halt(error: GuardedIntegrationError) -> GuardedIntegrationDecision:
        """Build the only halted shape; it grants no source, lane, or delivery effect."""

        return GuardedIntegrationDecision(outcome=CoordinatorOutcome.HALT, error=error)
