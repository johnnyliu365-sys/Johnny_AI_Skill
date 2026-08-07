"""TDD acceptance tests for guarded local-main integration and Grill audit."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from library.workflow_router import (
    CompletionActionKind,
    ImplementationReturn,
    ImplementationReturnStatus,
    RouterEventKind,
)
from library.workflow_router.guarded_integration import (
    AuditDecision,
    AuditDisposition,
    AuditRequest,
    CoordinatorOutcome,
    CorrectionRoute,
    DependentProposal,
    GuardedIntegrationCoordinator,
    GuardedIntegrationError,
    IntegrationLock,
    IntegrationPort,
    IntegrationResult,
    IntegrationStatus,
    MainSnapshot,
    PendingAudit,
    ProposalState,
    ReturnEventSource,
    ImplementationReturnEvent,
)


class FakeIntegrationPort:
    """A deterministic integration adapter that records calls without Git access."""

    def __init__(self, *, result: IntegrationResult) -> None:
        self.result = result
        self.requests: list[object] = []

    def integrate(self, request: object) -> IntegrationResult:
        self.requests.append(request)
        return self.result


class RaisingIntegrationPort:
    """Integration adapter exceptions map to a stable halt."""

    def integrate(self, request: object) -> IntegrationResult:
        raise RuntimeError("integration adapter unavailable")


class FakeIntegrationLock:
    """A typed lock fake with deterministic contention and release evidence."""

    def __init__(self, *, acquired: bool = True) -> None:
        self.acquired = acquired
        self.acquire_count = 0
        self.release_count = 0

    def try_acquire(self) -> bool:
        self.acquire_count += 1
        return self.acquired

    def release(self) -> None:
        self.release_count += 1


class FakeAuditSink:
    """An injected Grill-audit port; it cannot hand off, push, or deploy."""

    def __init__(self) -> None:
        self.requests: list[AuditRequest] = []

    def request_audit(self, request: AuditRequest) -> None:
        self.requests.append(request)


class RaisingAuditSink:
    """Audit adapter exceptions cannot grant a later workflow stage."""

    def request_audit(self, request: AuditRequest) -> None:
        raise RuntimeError("audit adapter unavailable")


class FakeReturnSource:
    """An event source that can deliver only one typed return event."""

    def __init__(self, event: ImplementationReturnEvent | None) -> None:
        self.event = event

    def next_return(self) -> ImplementationReturnEvent | None:
        return self.event


class RaisingReturnSource:
    """An adapter failure must become a stable halt, never a grant."""

    def next_return(self) -> ImplementationReturnEvent | None:
        raise RuntimeError("adapter unavailable")


class GuardedIntegrationAuditTests(unittest.TestCase):
    """Keep integration, wake-up, audit and safety boundaries deterministic."""

    def setUp(self) -> None:
        self.ticket = "ticket-guarded-integration-02"
        self.main_revision = "rev-0123456789abcdef"
        self.integrated_revision = "rev-abcdef0123456789"
        self.proposals = (
            DependentProposal(
                proposal_id="proposal-dependent-01",
                dependency_ticket_reference=self.ticket,
                state=ProposalState.PLANNED,
                context_view_id="ctx-planning-dependent-01",
                event_id="evt-planning-dependent-01",
            ),
            DependentProposal(
                proposal_id="proposal-unrelated-01",
                dependency_ticket_reference="ticket-other-01",
                state=ProposalState.PLANNED,
                context_view_id="ctx-planning-other-01",
                event_id="evt-planning-other-01",
            ),
        )
        self.integration = FakeIntegrationPort(
            result=IntegrationResult(
                status=IntegrationStatus.COMPLETED,
                integrated_main_revision=self.integrated_revision,
            )
        )
        self.lock = FakeIntegrationLock()
        self.audit = FakeAuditSink()
        self.coordinator = self._coordinator()

    def _coordinator(
        self,
        *,
        integration: FakeIntegrationPort | None = None,
        lock: FakeIntegrationLock | None = None,
        snapshot: MainSnapshot | None = None,
    ) -> GuardedIntegrationCoordinator:
        return GuardedIntegrationCoordinator(
            integration_port=integration or self.integration,
            integration_lock=lock or self.lock,
            audit_sink=self.audit,
            main_snapshot=snapshot
            or MainSnapshot(revision=self.main_revision, is_clean=True),
            dependent_proposals=self.proposals,
        )

    def _event(
        self,
        *,
        correlation_id: str = "return-correlation-01",
        event_id: str = "event-return-01",
    ) -> ImplementationReturnEvent:
        return ImplementationReturnEvent(
            event_id=event_id,
            correlation_id=correlation_id,
            event_kind=RouterEventKind.ACTION_COMPLETED,
            ticket_reference=self.ticket,
            implementation_owner_id="implementation-owner",
            reviewer_id="reviewer",
            expected_main_revision=self.main_revision,
            worktree_fingerprint="worktree-ticket-02",
            branch_fingerprint="branch-ticket-02",
            planning_context_view_id="ctx-planning-ticket-02",
            ticket_context_view_id="ctx-ticket-ticket-02",
            planning_event_id="evt-planning-ticket-02",
            ticket_event_id="evt-ticket-ticket-02",
            implementation_return=ImplementationReturn(
                ticket_reference=self.ticket,
                status=ImplementationReturnStatus.COMPLETED,
                evidence_references=("evidence-ticket-02",),
                verification_references=("verification-ticket-02",),
                evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                emitted_event=RouterEventKind.ACTION_COMPLETED,
            ),
        )

    def test_valid_return_integrates_once_wakes_dependents_and_starts_one_audit(self) -> None:
        decision = self.coordinator.handle_return(self._event())
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, decision.outcome)
        self.assertEqual(("proposal-dependent-01",), decision.awakened_proposal_ids)
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(1, self.lock.acquire_count)
        self.assertEqual(1, self.lock.release_count)
        self.assertIsNotNone(decision.pending_audit)
        self.assertIsNotNone(decision.audit_request)
        self.assertEqual(1, len(self.audit.requests))
        assert decision.pending_audit is not None
        self.assertEqual(self.integrated_revision, decision.pending_audit.integrated_main_revision)
        self.assertNotEqual(self._event().planning_context_view_id, self._event().ticket_context_view_id)
        self.assertNotEqual(self._event().planning_event_id, self._event().ticket_event_id)

    def test_stale_dirty_conflict_and_lock_contention_halt_before_side_effects(self) -> None:
        cases = (
            ("stale", MainSnapshot(revision="rev-ffffffffffffffff", is_clean=True), IntegrationStatus.COMPLETED, True),
            ("dirty", MainSnapshot(revision=self.main_revision, is_clean=False), IntegrationStatus.COMPLETED, True),
            ("conflict", MainSnapshot(revision=self.main_revision, is_clean=True, has_conflict=True), IntegrationStatus.COMPLETED, True),
            ("lock", MainSnapshot(revision=self.main_revision, is_clean=True), IntegrationStatus.COMPLETED, False),
        )
        for name, snapshot, integration_status, acquired in cases:
            with self.subTest(case=name):
                integration = FakeIntegrationPort(
                    result=IntegrationResult(
                        status=integration_status,
                        integrated_main_revision=self.integrated_revision
                        if integration_status is IntegrationStatus.COMPLETED
                        else None,
                    )
                )
                lock = FakeIntegrationLock(acquired=acquired)
                decision = self._coordinator(
                    integration=integration,
                    lock=lock,
                    snapshot=snapshot,
                ).handle_return(self._event(correlation_id=f"return-{name}-01"))
                self.assertEqual(CoordinatorOutcome.HALT, decision.outcome)
                self.assertEqual((), decision.awakened_proposal_ids)
                self.assertEqual((), tuple(integration.requests))
                self.assertIsNone(decision.pending_audit)

    def test_duplicate_return_missing_return_and_invalid_status_halt_without_wake(self) -> None:
        first = self.coordinator.handle_return(self._event())
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, first.outcome)
        duplicate = self.coordinator.handle_return(self._event())
        self.assertEqual(CoordinatorOutcome.HALT, duplicate.outcome)
        self.assertEqual(GuardedIntegrationError.DUPLICATE_RETURN, duplicate.error)
        self.assertEqual(1, len(self.integration.requests))
        active = self.coordinator.handle_return(
            self._event(correlation_id="return-correlation-02", event_id="event-return-02")
        )
        self.assertEqual(CoordinatorOutcome.HALT, active.outcome)
        self.assertEqual(GuardedIntegrationError.PENDING_AUDIT_ACTIVE, active.error)
        self.assertEqual(1, len(self.integration.requests))
        replayed_with_new_correlation = self.coordinator.handle_return(
            self._event(correlation_id="return-correlation-03")
        )
        self.assertEqual(CoordinatorOutcome.HALT, replayed_with_new_correlation.outcome)
        self.assertEqual(GuardedIntegrationError.DUPLICATE_RETURN, replayed_with_new_correlation.error)
        self.assertEqual(1, len(self.integration.requests))

        missing = self._coordinator().handle_return(None)
        self.assertEqual(CoordinatorOutcome.HALT, missing.outcome)
        self.assertEqual(GuardedIntegrationError.INVALID_RETURN, missing.error)

        blocked_return = self._event().implementation_return
        assert blocked_return is not None
        blocked_event = self._event(correlation_id="return-blocked-01").model_copy(
            update={
                "implementation_return": blocked_return.model_copy(
                    update={"status": ImplementationReturnStatus.BLOCKED}
                )
            }
        )
        blocked = self._coordinator().handle_return(blocked_event)
        self.assertEqual(CoordinatorOutcome.HALT, blocked.outcome)
        self.assertEqual(GuardedIntegrationError.INVALID_RETURN, blocked.error)

        forged = self._event(event_id="event-forged-01").model_construct(
            event_kind=RouterEventKind.VALIDATION_FAILED,
        )
        rejected_forgery = self._coordinator().handle_return(forged)
        self.assertEqual(CoordinatorOutcome.HALT, rejected_forgery.outcome)
        self.assertEqual(GuardedIntegrationError.INVALID_RETURN, rejected_forgery.error)

    def test_approved_audit_routes_only_to_code_review(self) -> None:
        decision = self.coordinator.handle_return(self._event())
        assert decision.pending_audit is not None
        approved = self.coordinator.handle_audit(
            AuditDecision(
                ticket_reference=self.ticket,
                correlation_id=decision.pending_audit.correlation_id,
                disposition=AuditDisposition.APPROVED,
            )
        )
        self.assertEqual(CoordinatorOutcome.CODE_REVIEW, approved.outcome)
        self.assertEqual("code_review", approved.action_label)
        self.assertIsNone(approved.correction_route)
        self.assertFalse(approved.handoff_allowed)
        self.assertFalse(approved.push_allowed)
        self.assertFalse(approved.deploy_allowed)
        self.assertFalse(approved.dependent_implementation_allowed)

    def test_changes_requested_creates_correction_route_without_delivery_effects(self) -> None:
        decision = self.coordinator.handle_return(self._event())
        assert decision.pending_audit is not None
        changed = self.coordinator.handle_audit(
            AuditDecision(
                ticket_reference=self.ticket,
                correlation_id=decision.pending_audit.correlation_id,
                disposition=AuditDisposition.CHANGES_REQUESTED,
            )
        )
        self.assertEqual(CoordinatorOutcome.CORRECTION, changed.outcome)
        self.assertIsNotNone(changed.correction_route)
        self.assertFalse(changed.handoff_allowed)
        self.assertFalse(changed.push_allowed)
        self.assertFalse(changed.deploy_allowed)
        self.assertFalse(changed.dependent_implementation_allowed)

    def test_event_source_absence_and_exception_are_stable_halts_without_host_or_git_actions(self) -> None:
        missing = self.coordinator.consume_return(None)
        self.assertEqual(CoordinatorOutcome.HALT, missing.outcome)
        self.assertEqual(GuardedIntegrationError.ADAPTER_UNAVAILABLE, missing.error)
        failed = self.coordinator.consume_return(RaisingReturnSource())
        self.assertEqual(CoordinatorOutcome.HALT, failed.outcome)
        self.assertEqual(GuardedIntegrationError.ADAPTER_FAILURE, failed.error)
        delivered = self.coordinator.consume_return(FakeReturnSource(self._event(correlation_id="return-source-01")))
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, delivered.outcome)
        self.assertEqual(1, len(self.integration.requests))

        integration_failed = self._coordinator(
            integration=RaisingIntegrationPort(),  # type: ignore[arg-type]
        ).handle_return(self._event(correlation_id="return-integration-failure-01"))
        self.assertEqual(CoordinatorOutcome.HALT, integration_failed.outcome)
        self.assertEqual(GuardedIntegrationError.ADAPTER_FAILURE, integration_failed.error)

        audit_failed = GuardedIntegrationCoordinator(
            integration_port=self.integration,
            integration_lock=self.lock,
            audit_sink=RaisingAuditSink(),
            main_snapshot=MainSnapshot(revision=self.main_revision, is_clean=True),
            dependent_proposals=self.proposals,
        ).handle_return(self._event(correlation_id="return-audit-failure-01"))
        self.assertEqual(CoordinatorOutcome.HALT, audit_failed.outcome)
        self.assertEqual(GuardedIntegrationError.ADAPTER_FAILURE, audit_failed.error)

    def test_metadata_contract_rejects_paths_and_context_text(self) -> None:
        with self.assertRaises(ValidationError):
            ImplementationReturnEvent.model_validate(
                {
                    **self._event().model_dump(),
                    "worktree_fingerprint": "C:/repo/.git",
                }
            )
        with self.assertRaises(ValidationError):
            AuditRequest(
                ticket_reference=self.ticket,
                correlation_id="audit-correlation-01",
                pending_audit=PendingAudit(
                    ticket_reference=self.ticket,
                    correlation_id="return-correlation-01",
                    integrated_main_revision=self.integrated_revision,
                    audit_event_id="evt-audit-01",
                ),
                raw_context="secret source text",  # type: ignore[call-arg]
            )


if __name__ == "__main__":
    unittest.main()
