"""Regression evidence for receipt-bound guarded integration corrections."""

from __future__ import annotations

import unittest
from collections.abc import Callable
from threading import Event, Thread

from library.workflow_router import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    CapabilityRef,
    CollaborationDispatchPlan,
    CollaborationTopology,
    CollaborationTopologyPlan,
    ContinuationDirective,
    ImplementationReturn,
    ImplementationReturnStatus,
    PlanningLaneState,
    ProcessStage,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    TicketDispatchReceipt,
    TicketDispatchState,
    TicketLaneState,
    TicketProposalState,
    build_router_poc_profile,
)
from library.workflow_router.guarded_integration import (
    AuditDecision,
    AuditDeliveryState,
    AuditDisposition,
    CoordinatorOutcome,
    GuardedIntegrationCoordinator,
    GuardedIntegrationDecision,
    GuardedIntegrationError,
    GuardedIntegrationRouterAdapter,
    ImplementationReturnEvent,
    IntegrationResult,
    IntegrationStatus,
    MainSnapshot,
)


class FakeIntegrationPort:
    def __init__(self, *, result: IntegrationResult) -> None:
        self.result = result
        self.requests: list[object] = []

    def integrate(self, request: object) -> IntegrationResult:
        self.requests.append(request)
        return self.result


class FakeIntegrationLock:
    def __init__(self) -> None:
        self.requests = 0

    def try_acquire(self) -> bool:
        self.requests += 1
        return True

    def release(self) -> None:
        return None


class FakeAuditSink:
    def __init__(self) -> None:
        self.requests: list[object] = []

    def request_audit(self, request: object) -> None:
        self.requests.append(request)


class ReentrantReleaseLock:
    """Deliver one second return exactly when the first critical section releases."""

    def __init__(self) -> None:
        self.callback: Callable[[], GuardedIntegrationDecision] | None = None
        self.reentrant_result: GuardedIntegrationDecision | None = None
        self.release_count = 0

    def try_acquire(self) -> bool:
        return True

    def release(self) -> None:
        self.release_count += 1
        if self.release_count == 1 and self.callback is not None:
            self.reentrant_result = self.callback()


class SequencedIntegrationPort:
    """Return deterministic distinct main revisions for two attempted integrations."""

    def __init__(self, *, results: tuple[IntegrationResult, ...]) -> None:
        self._results = results
        self.requests: list[object] = []

    def integrate(self, request: object) -> IntegrationResult:
        index = len(self.requests)
        self.requests.append(request)
        return self._results[index]


class FirstAuditFailureSink:
    """Fail the first post-integration audit request and retain later calls as evidence."""

    def __init__(self) -> None:
        self.requests: list[object] = []

    def request_audit(self, request: object) -> None:
        self.requests.append(request)
        if len(self.requests) == 1:
            raise RuntimeError("audit request unavailable")


class ReentrantAuditSink:
    """Invoke one retry while delivery is in flight, optionally failing first."""

    def __init__(self, *, fail_first: bool = False) -> None:
        self.requests: list[object] = []
        self.fail_first = fail_first
        self.callback: Callable[[], tuple[GuardedIntegrationDecision, object | None]] | None = None
        self.reentrant_result: GuardedIntegrationDecision | None = None

    def request_audit(self, request: object) -> None:
        self.requests.append(request)
        if self.callback is not None:
            self.reentrant_result, _ = self.callback()
        if self.fail_first and len(self.requests) == 1:
            raise RuntimeError("audit request unavailable")


class BlockingAuditSink:
    """Pause delivery so a second thread can probe the in-flight admission state."""

    def __init__(self, *, fail_first: bool = False) -> None:
        self.requests: list[object] = []
        self.entered = Event()
        self.release = Event()
        self.fail_first = fail_first

    def request_audit(self, request: object) -> None:
        self.requests.append(request)
        attempt = len(self.requests)
        self.entered.set()
        if not self.release.wait(timeout=5):
            raise RuntimeError("audit request did not release")
        if self.fail_first and attempt == 1:
            raise RuntimeError("audit request unavailable")


class ReceiptBoundCorrectionTests(unittest.TestCase):
    """The coordinator may consume only a Router-owned, receipt-bound lane."""

    def setUp(self) -> None:
        self.revision = "rev-0123456789abcdef"
        self.integrated_revision = "rev-abcdef0123456789"
        self.ticket = "ticket-guarded-correction-02"
        self.owner = "implementation-owner-02"
        self.reviewer = "reviewer-02"
        self.integration = FakeIntegrationPort(
            result=IntegrationResult(
                status=IntegrationStatus.COMPLETED,
                integrated_main_revision=self.integrated_revision,
            )
        )
        self.lock = FakeIntegrationLock()
        self.audit = FakeAuditSink()

    def _event(
        self,
        *,
        ticket: str | None = None,
        correlation: str = "return-correction-01",
        event_id: str = "event-correction-01",
        owner: str | None = None,
        worktree: str = "worktree-ticket-02",
        expected_revision: str | None = None,
    ) -> ImplementationReturnEvent:
        selected_ticket = ticket or self.ticket
        return ImplementationReturnEvent(
            event_id=event_id,
            correlation_id=correlation,
            event_kind=RouterEventKind.IMPLEMENTATION_RETURNED,
            ticket_reference=selected_ticket,
            implementation_owner_id=owner or self.owner,
            reviewer_id=self.reviewer,
            expected_main_revision=expected_revision or self.revision,
            worktree_fingerprint=worktree,
            branch_fingerprint="branch-ticket-02",
            planning_context_view_id="ctx-planning-correction-02",
            ticket_context_view_id="ctx-ticket-correction-02",
            planning_event_id="evt-planning-correction-02",
            ticket_event_id="evt-ticket-correction-02",
            dispatch_receipt=TicketDispatchReceipt(
                ticket_reference=selected_ticket,
                implementation_owner_id=owner or self.owner,
                handoff_reference="handoff-correction-02",
                expected_main_revision=expected_revision or self.revision,
                correlation_id=correlation,
                dispatch_question_id="dispatch-question-correction-02",
                worktree_fingerprint=worktree,
                branch_fingerprint="branch-ticket-02",
            ),
            implementation_return=ImplementationReturn(
                ticket_reference=selected_ticket,
                status=ImplementationReturnStatus.COMPLETED,
                evidence_references=("evidence-correction-02",),
                verification_references=("verification-correction-02",),
                evidence_digest=(
                    "sha256_0123456789abcdef0123456789abcdef"
                    "0123456789abcdef0123456789abcdef"
                ),
                emitted_event=RouterEventKind.IMPLEMENTATION_RETURNED,
            ),
        )

    def _plan(self, event: ImplementationReturnEvent) -> CollaborationDispatchPlan:
        implementation = CapabilityRef(
            capability_id=event.implementation_owner_id,
            version="1",
            agent_profile="implementation-owner",
        )
        reviewer = CapabilityRef(
            capability_id=event.reviewer_id,
            version="1",
            agent_profile="reviewer",
        )
        control = CapabilityRef(
            capability_id="control-plane-02",
            version="1",
            agent_profile="control-plane",
        )
        topology = CollaborationTopologyPlan(
            topology=CollaborationTopology.TWO_COLLABORATING_AGENTS,
            control_plane=control,
            implementation_owner=implementation,
            reviewer=reviewer,
        )
        assert event.dispatch_receipt is not None
        return CollaborationDispatchPlan(
            receipt=event.dispatch_receipt,
            planning_lane=PlanningLaneState(
                project_id="project-correction-02",
                stage=ProcessStage.GRILL,
                topology=topology.topology,
                artifact_refs=(),
                active_ticket_refs=(event.ticket_reference,),
                context_view_id=event.planning_context_view_id,
                side_context_id="side-planning-correction-02",
                event_id=event.planning_event_id,
                safety_ceiling=100,
            ),
            ticket_lane=TicketLaneState(
                ticket_id=event.ticket_reference,
                dispatch_state=TicketDispatchState.CONFIRMED,
                execution_stage=ProcessStage.IMPLEMENT,
                expected_main_revision=event.expected_main_revision,
                source_grants=(ArtifactKind.TICKET,),
                context_view_id=event.ticket_context_view_id,
                side_context_id="side-ticket-correction-02",
                event_id=event.ticket_event_id,
                worktree_fingerprint=event.worktree_fingerprint,
                branch_fingerprint=event.branch_fingerprint,
                safety_ceiling=100,
                implementation_capability=implementation,
                reviewer=reviewer,
            ),
        )

    def _coordinator(
        self,
        *,
        plans: tuple[CollaborationDispatchPlan, ...],
    ) -> GuardedIntegrationCoordinator:
        return GuardedIntegrationCoordinator(
            integration_port=self.integration,
            integration_lock=self.lock,
            audit_sink=self.audit,
            main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
            dependent_proposals=(),
            dispatch_plans=plans,
        )

    def test_unregistered_direct_and_source_returns_halt_before_side_effects(self) -> None:
        event = self._event()
        coordinator = self._coordinator(plans=())
        self.assertEqual(
            GuardedIntegrationError.DISPATCH_NOT_BOUND,
            coordinator.handle_return(event).error,
        )
        self.assertEqual((), tuple(self.integration.requests))
        self.assertEqual((), tuple(self.audit.requests))

        class Source:
            def next_return(self) -> ImplementationReturnEvent:
                return event

        self.assertEqual(
            GuardedIntegrationError.DISPATCH_NOT_BOUND,
            coordinator.consume_return(Source()).error,
        )
        self.assertEqual((), tuple(self.integration.requests))

    def test_lane_mismatch_and_seven_locator_forms_fail_closed(self) -> None:
        event = self._event()
        plan = self._plan(event)
        for mismatch in (
            {"implementation_owner_id": "unregistered-owner-02"},
            {"worktree_fingerprint": "worktree-other-02"},
            {"expected_main_revision": "rev-ffffffffffffffff"},
        ):
            with self.subTest(mismatch=mismatch):
                mismatched = event.model_copy(update=mismatch)
                result = self._coordinator(plans=(plan,)).handle_return(mismatched)
                self.assertIn(
                    result.error,
                    (GuardedIntegrationError.DISPATCH_NOT_BOUND, GuardedIntegrationError.INVALID_RETURN),
                )
                self.assertEqual((), tuple(self.integration.requests))
        for locator in (
            r"C:\repo\.git",
            "C:/repo/.git",
            "/repo/.git",
            r"\\server\share",
            "file:///repo/.git",
            "https://example.invalid/repo",
            "..\\repo\\.git",
        ):
            with self.subTest(locator=locator):
                with self.assertRaises(ValueError):
                    ImplementationReturnEvent.model_validate(
                        event.model_dump() | {"worktree_fingerprint": locator}
                    )

    def test_generic_actor_profiles_cannot_substitute_named_owner_or_reviewer(self) -> None:
        event = self._event()
        plan = self._plan(event)
        for field_name, generic_profile in (
            ("implementation_owner_id", "implementation-owner"),
            ("reviewer_id", "reviewer"),
        ):
            with self.subTest(field=field_name):
                substituted = event.model_copy(update={field_name: generic_profile})
                decision = self._coordinator(plans=(plan,)).handle_return(substituted)
                self.assertIn(
                    decision.error,
                    (GuardedIntegrationError.INVALID_RETURN, GuardedIntegrationError.DISPATCH_NOT_BOUND),
                )
                self.assertEqual((), tuple(self.integration.requests))
                self.assertEqual((), tuple(self.audit.requests))

                class Source:
                    def next_return(self) -> ImplementationReturnEvent:
                        return substituted

                injected = self._coordinator(plans=(plan,)).consume_return(Source())
                self.assertIn(
                    injected.error,
                    (GuardedIntegrationError.INVALID_RETURN, GuardedIntegrationError.DISPATCH_NOT_BOUND),
                )
                self.assertEqual((), tuple(self.integration.requests))
                self.assertEqual((), tuple(self.audit.requests))

    def test_lock_release_cannot_admit_a_second_ticket_before_pending_audit(self) -> None:
        first = self._event(correlation="return-lock-first-02", event_id="event-lock-first-02")
        second = self._event(
            ticket="ticket-guarded-lock-other",
            correlation="return-lock-second-02",
            event_id="event-lock-second-02",
        )
        reentrant_lock = ReentrantReleaseLock()
        coordinator = GuardedIntegrationCoordinator(
            integration_port=self.integration,
            integration_lock=reentrant_lock,
            audit_sink=self.audit,
            main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
            dependent_proposals=(),
            dispatch_plans=(self._plan(first), self._plan(second)),
        )
        reentrant_lock.callback = lambda: coordinator.handle_return(second)
        initial = coordinator.handle_return(first)
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, initial.outcome)
        self.assertIsNotNone(reentrant_lock.reentrant_result)
        assert reentrant_lock.reentrant_result is not None
        self.assertEqual(GuardedIntegrationError.PENDING_AUDIT_ACTIVE, reentrant_lock.reentrant_result.error)
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(1, len(self.audit.requests))

    def test_audit_sink_failure_retains_pending_audit_and_blocks_later_ticket(self) -> None:
        first_revision = "rev-1111111111111111"
        second_revision = "rev-2222222222222222"
        first = self._event(correlation="return-audit-failure-02", event_id="event-audit-failure-02")
        second = self._event(
            ticket="ticket-guarded-audit-other",
            correlation="return-audit-second-02",
            event_id="event-audit-second-02",
            expected_revision=first_revision,
        )
        integration = SequencedIntegrationPort(
            results=(
                IntegrationResult(
                    status=IntegrationStatus.COMPLETED,
                    integrated_main_revision=first_revision,
                ),
                IntegrationResult(
                    status=IntegrationStatus.COMPLETED,
                    integrated_main_revision=second_revision,
                ),
            )
        )
        audit = FirstAuditFailureSink()
        adapter = GuardedIntegrationRouterAdapter(coordinator=GuardedIntegrationCoordinator(
            integration_port=integration,
            integration_lock=FakeIntegrationLock(),
            audit_sink=audit,
            main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
            dependent_proposals=(),
            dispatch_plans=(self._plan(first), self._plan(second)),
        ))
        failed, failed_event = adapter.handle_return(first)
        self.assertEqual(GuardedIntegrationError.ADAPTER_FAILURE, failed.error)
        self.assertIsNone(failed_event)
        retry, integration_event = adapter.retry_pending_audit()
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, retry.outcome)
        self.assertIsNotNone(retry.pending_audit)
        self.assertIsNotNone(integration_event)
        assert integration_event is not None
        self.assertEqual(RouterEventKind.INTEGRATION_COMPLETED, integration_event.kind)
        duplicate_retry, duplicate_event = adapter.retry_pending_audit()
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, duplicate_retry.outcome)
        self.assertIsNone(duplicate_event)
        blocked, blocked_event = adapter.handle_return(second)
        self.assertEqual(GuardedIntegrationError.PENDING_AUDIT_ACTIVE, blocked.error)
        self.assertIsNone(blocked_event)
        self.assertEqual(1, len(integration.requests))
        self.assertEqual(2, len(audit.requests))

    def test_initial_audit_delivery_reentry_is_admitted_once(self) -> None:
        event = self._event(correlation="return-audit-reentrant-02", event_id="event-audit-reentrant-02")
        sink = ReentrantAuditSink()
        adapter = GuardedIntegrationRouterAdapter(
            coordinator=GuardedIntegrationCoordinator(
                integration_port=self.integration,
                integration_lock=self.lock,
                audit_sink=sink,
                main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
                dependent_proposals=(),
                dispatch_plans=(self._plan(event),),
            )
        )
        sink.callback = adapter.retry_pending_audit
        decision, integration_event = adapter.handle_return(event)
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, decision.outcome)
        self.assertIsNotNone(integration_event)
        self.assertEqual(AuditDeliveryState.DELIVERED, adapter._coordinator.audit_delivery_state)
        self.assertIsNotNone(sink.reentrant_result)
        assert sink.reentrant_result is not None
        self.assertEqual(GuardedIntegrationError.AUDIT_DELIVERY_ACTIVE, sink.reentrant_result.error)
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(1, len(sink.requests))

    def test_failed_audit_retry_reentry_resets_then_delivers_once(self) -> None:
        event = self._event(correlation="return-audit-retry-reentrant-02", event_id="event-audit-retry-reentrant-02")
        sink = ReentrantAuditSink(fail_first=True)
        adapter = GuardedIntegrationRouterAdapter(
            coordinator=GuardedIntegrationCoordinator(
                integration_port=self.integration,
                integration_lock=self.lock,
                audit_sink=sink,
                main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
                dependent_proposals=(),
                dispatch_plans=(self._plan(event),),
            )
        )
        sink.callback = adapter.retry_pending_audit
        failed, failed_event = adapter.handle_return(event)
        self.assertEqual(GuardedIntegrationError.ADAPTER_FAILURE, failed.error)
        self.assertIsNone(failed_event)
        self.assertEqual(AuditDeliveryState.RETRYABLE, adapter._coordinator.audit_delivery_state)
        retry, retry_event = adapter.retry_pending_audit()
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, retry.outcome)
        self.assertIsNotNone(retry_event)
        self.assertEqual(AuditDeliveryState.DELIVERED, adapter._coordinator.audit_delivery_state)
        self.assertIsNotNone(sink.reentrant_result)
        assert sink.reentrant_result is not None
        self.assertEqual(GuardedIntegrationError.AUDIT_DELIVERY_ACTIVE, sink.reentrant_result.error)
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(2, len(sink.requests))
        duplicate, duplicate_event = adapter.retry_pending_audit()
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, duplicate.outcome)
        self.assertIsNone(duplicate_event)
        self.assertEqual(2, len(sink.requests))

    def test_initial_audit_delivery_concurrency_is_admitted_once(self) -> None:
        event = self._event(correlation="return-audit-concurrent-02", event_id="event-audit-concurrent-02")
        sink = BlockingAuditSink()
        adapter = GuardedIntegrationRouterAdapter(
            coordinator=GuardedIntegrationCoordinator(
                integration_port=self.integration,
                integration_lock=self.lock,
                audit_sink=sink,
                main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
                dependent_proposals=(),
                dispatch_plans=(self._plan(event),),
            )
        )
        result: list[tuple[GuardedIntegrationDecision, RouterEvent | None]] = []
        worker = Thread(target=lambda: result.append(adapter.handle_return(event)), daemon=True)
        worker.start()
        self.assertTrue(sink.entered.wait(timeout=5))
        concurrent, concurrent_event = adapter.retry_pending_audit()
        self.assertEqual(GuardedIntegrationError.AUDIT_DELIVERY_ACTIVE, concurrent.error)
        self.assertIsNone(concurrent_event)
        sink.release.set()
        worker.join(timeout=5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(1, len(result))
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, result[0][0].outcome)
        self.assertIsNotNone(result[0][1])
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(1, len(sink.requests))

    def test_failed_audit_retry_concurrency_is_retryable_and_single_delivery(self) -> None:
        event = self._event(
            correlation="return-audit-concurrent-retry-02",
            event_id="event-audit-concurrent-retry-02",
        )
        sink = BlockingAuditSink(fail_first=True)
        adapter = GuardedIntegrationRouterAdapter(
            coordinator=GuardedIntegrationCoordinator(
                integration_port=self.integration,
                integration_lock=self.lock,
                audit_sink=sink,
                main_snapshot=MainSnapshot(revision=self.revision, is_clean=True),
                dependent_proposals=(),
                dispatch_plans=(self._plan(event),),
            )
        )
        initial_result: list[tuple[GuardedIntegrationDecision, RouterEvent | None]] = []
        initial_worker = Thread(target=lambda: initial_result.append(adapter.handle_return(event)), daemon=True)
        initial_worker.start()
        self.assertTrue(sink.entered.wait(timeout=5))
        sink.release.set()
        initial_worker.join(timeout=5)
        self.assertFalse(initial_worker.is_alive())
        self.assertEqual(GuardedIntegrationError.ADAPTER_FAILURE, initial_result[0][0].error)
        sink.entered.clear()
        sink.release.clear()
        retry_result: list[tuple[GuardedIntegrationDecision, RouterEvent | None]] = []
        retry_worker = Thread(target=lambda: retry_result.append(adapter.retry_pending_audit()), daemon=True)
        retry_worker.start()
        self.assertTrue(sink.entered.wait(timeout=5))
        concurrent, concurrent_event = adapter.retry_pending_audit()
        self.assertEqual(GuardedIntegrationError.AUDIT_DELIVERY_ACTIVE, concurrent.error)
        self.assertIsNone(concurrent_event)
        sink.release.set()
        retry_worker.join(timeout=5)
        self.assertFalse(retry_worker.is_alive())
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, retry_result[0][0].outcome)
        self.assertIsNotNone(retry_result[0][1])
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(2, len(sink.requests))

    def test_pending_audit_is_global_and_revision_advances_after_integration(self) -> None:
        first = self._event()
        second = self._event(
            ticket="ticket-guarded-correction-other",
            correlation="return-correction-other",
            event_id="event-correction-other",
        )
        coordinator = self._coordinator(plans=(self._plan(first), self._plan(second)))
        first_result = coordinator.handle_return(first)
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, first_result.outcome)
        second_result = coordinator.handle_return(second)
        self.assertEqual(GuardedIntegrationError.PENDING_AUDIT_ACTIVE, second_result.error)
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(1, len(self.audit.requests))

        assert first_result.pending_audit is not None
        approved = coordinator.handle_audit(
            AuditDecision(
                ticket_reference=first.ticket_reference,
                correlation_id=first.correlation_id,
                disposition=AuditDisposition.APPROVED,
            )
        )
        self.assertEqual(CoordinatorOutcome.CODE_REVIEW, approved.outcome)
        replay_receipt = first.dispatch_receipt
        assert replay_receipt is not None
        old_revision = coordinator.handle_return(
            first.model_copy(
                update={
                    "correlation_id": "return-old-replay",
                    "dispatch_receipt": replay_receipt.model_copy(
                        update={"correlation_id": "return-old-replay"}
                    ),
                }
            )
        )
        self.assertEqual(GuardedIntegrationError.DISPATCH_NOT_BOUND, old_revision.error)
        self.assertEqual(self.integrated_revision, coordinator.main_snapshot.revision)
        old_other = coordinator.handle_return(second)
        self.assertEqual(GuardedIntegrationError.STALE_MAIN_REVISION, old_other.error)
        self.assertEqual(1, len(self.integration.requests))
        self.assertEqual(1, len(self.integration.requests))

    def test_reviewed_router_profile_composes_return_integration_and_audit(self) -> None:
        profile = build_router_poc_profile()
        self.assertIsNone(profile.rule_for(
            current_stage=ProcessStage.TICKETS,
            event_kind=RouterEventKind.APPROVAL_GRANTED,
        ))
        for event_kind in (
            RouterEventKind.TICKET_DISPATCH_REQUIRED,
            RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
            RouterEventKind.IMPLEMENTATION_RETURNED,
            RouterEventKind.INTEGRATION_COMPLETED,
            RouterEventKind.AUDIT_COMPLETED,
        ):
            self.assertTrue(any(rule.event_kind is event_kind for rule in profile.transition_rules))

        ticket_ref = ArtifactRef(
            kind=ArtifactKind.TICKET,
            identifier=self.ticket,
            uri="ticket://correction-02",
            revision="rev-0123456789abcdef",
        )
        state = RouterState(
            project_id="project-correction-02",
            stage=ProcessStage.IMPLEMENT,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=profile.delivery_stage,
            artifact_refs=(ticket_ref,),
        )
        event = self._event()
        returned = RouterEngine().decide(
            state=state,
            event=RouterEvent(
                event_id=event.event_id,
                kind=RouterEventKind.IMPLEMENTATION_RETURNED,
                implementation_return=event.implementation_return,
            ),
            profile=profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, returned.outcome)
        self.assertEqual(ProcessStage.SMOKE_TEST, returned.next_stage)

        audit_state = state.model_copy(update={"stage": ProcessStage.GRILL})
        integrated = RouterEngine().decide(
            state=audit_state,
            event=RouterEvent(event_id="integration-completed-02", kind=RouterEventKind.INTEGRATION_COMPLETED),
            profile=profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, integrated.outcome)
        self.assertEqual(ContinuationDirective.AUTO_CONTINUE, integrated.continuation)
        self.assertEqual(ProcessStage.GRILL, integrated.next_stage)
        self.assertIsNone(integrated.wait_reason)
        audited = RouterEngine().decide(
            state=audit_state,
            event=RouterEvent(event_id="audit-completed-02", kind=RouterEventKind.AUDIT_COMPLETED),
            profile=profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, audited.outcome)
        self.assertEqual(ProcessStage.REVIEW, audited.next_stage)

    def test_coordinator_adapter_emits_only_reviewed_router_events(self) -> None:
        event = self._event(correlation="return-adapter-02", event_id="event-adapter-02")
        adapter = GuardedIntegrationRouterAdapter(
            coordinator=self._coordinator(plans=(self._plan(event),))
        )
        pending, integration_event = adapter.handle_return(event)
        self.assertEqual(CoordinatorOutcome.PENDING_AUDIT, pending.outcome)
        self.assertIsNotNone(integration_event)
        assert integration_event is not None
        self.assertEqual(RouterEventKind.INTEGRATION_COMPLETED, integration_event.kind)
        assert pending.pending_audit is not None
        approved, audit_event = adapter.handle_audit(
            AuditDecision(
                ticket_reference=event.ticket_reference,
                correlation_id=pending.pending_audit.correlation_id,
                disposition=AuditDisposition.APPROVED,
            )
        )
        self.assertEqual(CoordinatorOutcome.CODE_REVIEW, approved.outcome)
        self.assertIsNotNone(audit_event)
        assert audit_event is not None
        self.assertEqual(RouterEventKind.AUDIT_COMPLETED, audit_event.kind)


if __name__ == "__main__":
    unittest.main()
