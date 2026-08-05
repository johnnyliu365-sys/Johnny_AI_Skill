"""TDD acceptance tests for the approved collaboration dispatch ticket."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from library.workflow_router import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    CapabilityRef,
    CollaborationTopology,
    CollaborationTopologyResolver,
    ContinuationDirective,
    DeliveryStage,
    HumanWaitReason,
    LaneKind,
    PlanningLaneState,
    ProcessStage,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    TicketDispatchConfirmation,
    TicketDispatchReceipt,
    TicketDispatchState,
    build_router_poc_profile,
)
from library.workflow_router.private_router import (
    ContinuationMode,
    EntitlementGrant,
    EntitlementMode,
    FakeEntitlementProvider,
    FakePrivateRouterService,
    PrivateRouterClient,
    ProductActionLabel,
    RedactedSummary,
    RouterRequestEnvelope,
)


class AutonomousCollaborationTests(unittest.TestCase):
    """Prove topology and dispatch remain typed, isolated, and fail closed."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.engine = RouterEngine()
        self.ticket = ArtifactRef(
            kind=ArtifactKind.TICKET,
            identifier="ticket-topology-dispatch-01",
            uri="ticket://autonomous-collaboration-audit/01",
            revision="b6cf8f8",
        )
        self.control = CapabilityRef(
            capability_id="cap-control-plane",
            version="1",
            agent_profile="control-plane",
        )
        self.implementation = CapabilityRef(
            capability_id="cap-implementation-owner",
            version="1",
            agent_profile="implementation-owner",
        )

    def test_topology_selection_rejects_unknown_count_or_unavailable_capability(self) -> None:
        resolver = CollaborationTopologyResolver()
        with self.assertRaises(ValueError):
            resolver.select(
                available_agent_count=0,
                control_plane=self.control,
                implementation_owner=self.implementation,
                available_capabilities=(self.control, self.implementation),
            )
        with self.assertRaises(ValueError):
            resolver.select(
                available_agent_count=3,
                control_plane=self.control,
                implementation_owner=self.implementation,
                available_capabilities=(self.control, self.implementation),
            )
        with self.assertRaises(ValueError):
            resolver.select(
                available_agent_count=1,
                control_plane=self.control,
                implementation_owner=self.implementation,
                available_capabilities=(self.control,),
            )

        one = resolver.select(
            available_agent_count=1,
            control_plane=self.control,
            implementation_owner=self.implementation,
            available_capabilities=(self.control, self.implementation),
        )
        two = resolver.select(
            available_agent_count=2,
            control_plane=self.control,
            implementation_owner=self.implementation,
            available_capabilities=(self.control, self.implementation),
        )
        self.assertEqual(CollaborationTopology.ONE_IMPLEMENTATION_AGENT, one.topology)
        self.assertEqual(CollaborationTopology.TWO_COLLABORATING_AGENTS, two.topology)
        self.assertEqual((), one.host_thread_references)

    def test_dispatch_without_or_with_negative_confirmation_waits_without_grants(self) -> None:
        state = self._ticket_state()
        for confirmation in (None, TicketDispatchConfirmation.NEGATIVE):
            event = RouterEvent(
                event_id="dispatch-required-0001",
                kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                dispatch_confirmation=confirmation,
            )
            decision = self.engine.decide(state=state, event=event, profile=self.profile)
            self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
            self.assertEqual(ContinuationDirective.WAIT_FOR_HUMAN, decision.continuation)
            self.assertEqual(
                HumanWaitReason.TICKET_DISPATCH_CONFIRMATION_REQUIRED,
                decision.wait_reason,
            )
            self.assertEqual((), decision.required_sources)
            self.assertEqual((), decision.eligible_capabilities)
            self.assertIsNone(decision.dispatch_plan)

    def test_positive_receipt_creates_one_ticket_plan_and_planning_grill_route(self) -> None:
        receipt = self._receipt()
        decision = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, decision.outcome)
        self.assertEqual(ContinuationDirective.AUTO_CONTINUE, decision.continuation)
        self.assertEqual(ProcessStage.GRILL, decision.next_stage)
        self.assertEqual((self.ticket,), decision.required_sources)
        self.assertIsNotNone(decision.dispatch_plan)
        assert decision.dispatch_plan is not None
        self.assertEqual(TicketDispatchState.CONFIRMED, decision.dispatch_plan.ticket_lane.dispatch_state)
        self.assertEqual(ProcessStage.IMPLEMENT, decision.dispatch_plan.ticket_lane.execution_stage)
        self.assertEqual(ProcessStage.GRILL, decision.dispatch_plan.planning_lane.stage)
        self.assertNotEqual(
            decision.dispatch_plan.planning_lane.context_view_id,
            decision.dispatch_plan.ticket_lane.context_view_id,
        )
        self.assertNotEqual(
            decision.dispatch_plan.planning_lane.side_context_id,
            decision.dispatch_plan.ticket_lane.side_context_id,
        )
        self.assertEqual((self.ticket.identifier,), decision.dispatch_plan.planning_lane.active_ticket_refs)
        progressed = decision.dispatch_plan.with_planning_progress(
            stage=ProcessStage.CONTEXT,
            event_id="planning-progress-0001",
        )
        self.assertEqual(ProcessStage.CONTEXT, progressed.planning_lane.stage)
        self.assertEqual(
            decision.dispatch_plan.ticket_lane,
            progressed.ticket_lane,
            "planning progress must not mutate the ticket lane",
        )
        with self.assertRaises(ValidationError):
            progressed.ticket_lane.execution_stage = ProcessStage.GRILL

    def test_dispatch_receipt_mismatch_halts_before_grant(self) -> None:
        receipt = self._receipt()
        with self.assertRaises(ValidationError):
            TicketDispatchReceipt(
                ticket_reference=receipt.ticket_reference,
                implementation_owner_id=receipt.implementation_owner_id,
                handoff_reference=receipt.handoff_reference,
                expected_main_revision=receipt.expected_main_revision,
                correlation_id="https://raw-context.invalid",
                worktree_fingerprint=receipt.worktree_fingerprint,
                branch_fingerprint=receipt.branch_fingerprint,
            )
        decision = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id="dispatch-required-0002",
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual(ContinuationDirective.HALT, decision.continuation)
        self.assertIsNone(decision.dispatch_plan)
        self.assertEqual((), decision.eligible_capabilities)

    def test_private_router_dispatch_wait_and_receipt_preserve_lane_plan(self) -> None:
        account = "acct_0123456789abcdef"
        project = "prj_fedcba9876543210"
        service = FakePrivateRouterService(
            profile=self.profile,
            entitlement_provider=FakeEntitlementProvider(
                grants=(
                    EntitlementGrant(
                        account_subject_id=account,
                        opaque_project_id=project,
                        permitted_modes=(EntitlementMode.FIRST_PROJECT_FREE,),
                    ),
                )
            ),
        )
        client = PrivateRouterClient(service=service)
        wait_request = self._private_request(
            account=account,
            project=project,
            event=RouterEventKind.TICKET_DISPATCH_REQUIRED,
            event_id="evt_00000000000000000000000000000061",
        )
        waiting = client.route(raw_request=wait_request.model_dump())
        self.assertEqual(ContinuationMode.WAIT_FOR_HUMAN, waiting.mode)
        self.assertEqual(ProductActionLabel.REQUEST_APPROVAL, waiting.action_label)
        self.assertIsNone(waiting.dispatch_plan)

        receipt = self._receipt()
        confirmed = self._private_request(
            account=account,
            project=project,
            event=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
            event_id="evt_00000000000000000000000000000062",
            dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
            dispatch_receipt=TicketDispatchReceipt(
                ticket_reference=receipt.ticket_reference,
                implementation_owner_id=receipt.implementation_owner_id,
                handoff_reference=receipt.handoff_reference,
                expected_main_revision=receipt.expected_main_revision,
                correlation_id="evt_00000000000000000000000000000062",
                worktree_fingerprint=receipt.worktree_fingerprint,
                branch_fingerprint=receipt.branch_fingerprint,
            ),
        )
        plan = client.route(raw_request=confirmed.model_dump())
        self.assertEqual(ContinuationMode.AUTO_RUN, plan.mode)
        self.assertEqual(ProductActionLabel.CONFIRM_ASSUMPTIONS, plan.action_label)
        self.assertIsNotNone(plan.dispatch_plan)
        assert plan.dispatch_plan is not None
        self.assertEqual(ProcessStage.IMPLEMENT, plan.dispatch_plan.ticket_lane.execution_stage)
        self.assertEqual(ProcessStage.GRILL, plan.dispatch_plan.planning_lane.stage)

    def _ticket_state(self) -> RouterState:
        return RouterState(
            project_id="autonomous-collaboration-audit",
            stage=ProcessStage.TICKETS,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.ticket,),
            topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
        )

    def _receipt(self) -> TicketDispatchReceipt:
        return TicketDispatchReceipt(
            ticket_reference=self.ticket.identifier,
            implementation_owner_id="agent-implementation-owner",
            handoff_reference="handoff-topology-dispatch-01",
            expected_main_revision="rev-0123456789abcdef",
            correlation_id="dispatch-confirmed-0001",
            worktree_fingerprint="worktree-implementation-01",
            branch_fingerprint="branch-implementation-01",
        )

    def _private_request(
        self,
        *,
        account: str,
        project: str,
        event: RouterEventKind,
        event_id: str,
        dispatch_confirmation: TicketDispatchConfirmation | None = None,
        dispatch_receipt: TicketDispatchReceipt | None = None,
    ) -> RouterRequestEnvelope:
        return RouterRequestEnvelope(
            request_id=f"req_{event_id.removeprefix('evt_')}",
            account_subject_id=account,
            opaque_project_id=project,
            project_entry_mode="new_project",
            entitlement_mode=EntitlementMode.FIRST_PROJECT_FREE,
            workflow_stage=ProcessStage.TICKETS,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            router_event_kind=event,
            event_correlation_id=event_id,
            available_source_kinds=(ArtifactKind.TICKET,),
            revision_digests=("rev_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",),
            structured_redacted_summary=RedactedSummary(
                evidence_codes=("goal_captured",),
                risk_codes=(),
                source_count_bucket=1,
            ),
            client_version="v1",
            topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
            ticket_reference=self.ticket.identifier,
            dispatch_confirmation=dispatch_confirmation,
            dispatch_receipt=dispatch_receipt,
        )


if __name__ == "__main__":
    unittest.main()
