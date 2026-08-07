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
    CollaborationTopologyPlan,
    CollaborationTopologyResolver,
    ContinuationDirective,
    ConsumerFingerprint,
    ContextResolver,
    DeliveryStage,
    HumanWaitReason,
    HandoffArtifactReference,
    HandoffConsumerFingerprint,
    ImplementationHandoff,
    LaneKind,
    PlanningLaneState,
    PendingDispatchDescriptor,
    ProcessStage,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    SourceSnippet,
    TicketDispatchConfirmation,
    TicketDispatchReceipt,
    TicketDispatchState,
    TicketProposal,
    TicketProposalState,
    TicketScope,
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
        self.reviewer = CapabilityRef(
            capability_id="cap-reviewer",
            version="1",
            agent_profile="reviewer",
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
        with self.assertRaises(ValueError):
            resolver.select(
                available_agent_count=1,
                control_plane=self.control,
                implementation_owner=self.implementation,
                reviewer=self.reviewer,
                available_capabilities=(self.control, self.implementation),
            )
        with self.assertRaises(ValueError):
            resolver.select(
                available_agent_count=1,
                control_plane=self.control,
                implementation_owner=self.implementation,
                available_capabilities=(),
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
                implementation_handoff=self._handoff(),
                ticket_proposal=self._proposal(),
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
            self.assertEqual((), decision.ticket_lane_capabilities)
            self.assertEqual(self._proposal(), decision.ticket_proposal)
            self.assertEqual(
                self._pending().model_copy(update={"event_correlation_id": "dispatch-required-0001"}),
                decision.pending_dispatch,
            )
            self.assertIsNone(decision.dispatch_plan)

    def test_positive_receipt_requires_pending_proposal_question_and_reviewed_handoff(self) -> None:
        receipt = self._receipt()
        bypass = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, bypass.outcome)
        self.assertEqual(ContinuationDirective.HALT, bypass.continuation)
        self.assertEqual("pending_dispatch_required", bypass.blockers[0].code.value)

        pending_state = self._ticket_state().model_copy(update={"pending_dispatch": self._pending()})
        accepted = self.engine.decide(
            state=pending_state,
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, accepted.outcome)
        self.assertEqual((self.implementation,), accepted.ticket_lane_capabilities)

        for mismatch in (
            {"handoff_reference": "handoff-other-01"},
            {"dispatch_question_id": "dispatch-question-other-01"},
            {"correlation_id": "dispatch-correlation-other-01"},
            {"ticket_reference": "ticket-other-01"},
        ):
            with self.subTest(mismatch=mismatch):
                mismatched = self.engine.decide(
                    state=pending_state,
                    event=RouterEvent(
                        event_id=receipt.correlation_id,
                        kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                        dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                        dispatch_receipt=receipt.model_copy(update=mismatch),
                    ),
                    profile=self.profile,
                )
                self.assertEqual(RouterOutcome.SUSPEND, mismatched.outcome)
                self.assertEqual(ContinuationDirective.HALT, mismatched.continuation)

        duplicate = self.engine.decide(
            state=pending_state.model_copy(update={"pending_dispatch": None}),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, duplicate.outcome)
        self.assertEqual(ContinuationDirective.HALT, duplicate.continuation)

    def test_dispatch_question_requires_reviewed_handoff_and_cannot_repeat(self) -> None:
        missing_handoff = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id="dispatch-handoff-missing-0001",
                kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                ticket_proposal=self._proposal(),
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, missing_handoff.outcome)
        self.assertEqual(ContinuationDirective.HALT, missing_handoff.continuation)
        self.assertEqual("implementation_handoff_required", missing_handoff.blockers[0].code.value)

        pending_state = self._ticket_state().model_copy(update={"pending_dispatch": self._pending()})
        repeated = self.engine.decide(
            state=pending_state,
            event=RouterEvent(
                event_id="dispatch-question-repeat-0001",
                kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                implementation_handoff=self._handoff(),
                ticket_proposal=self._proposal(),
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, repeated.outcome)
        self.assertEqual(ContinuationDirective.HALT, repeated.continuation)
        self.assertEqual("invalid_pending_dispatch", repeated.blockers[0].code.value)

    def test_ticket_documentation_completion_does_not_open_a_second_approval_wait(self) -> None:
        decision = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id="ticket-docs-completed-0001",
                kind=RouterEventKind.ACTION_COMPLETED,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual(ContinuationDirective.HALT, decision.continuation)
        self.assertEqual("no_declared_transition", decision.blockers[0].code.value)

    def test_legacy_ticket_approval_with_handoff_is_blocked_until_dispatch(self) -> None:
        decision = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id="legacy-approval-bypass-0001",
                kind=RouterEventKind.APPROVAL_GRANTED,
                implementation_handoff=self._handoff(),
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual(ContinuationDirective.HALT, decision.continuation)
        self.assertIsNone(decision.next_stage)
        self.assertEqual((), decision.required_sources)
        self.assertEqual((), decision.eligible_capabilities)
        self.assertEqual((), decision.ticket_lane_capabilities)
        self.assertIsNone(decision.dispatch_plan)

    def test_dispatch_requires_an_opened_in_progress_ticket_proposal(self) -> None:
        planned_proposal = TicketProposal(
            ticket_reference=self.ticket.identifier,
            state=TicketProposalState.PLANNED,
            implementation_owner_id=self.implementation.agent_profile,
            proposal_revision="rev-0123456789abcdef",
        )
        opened_proposal = planned_proposal.open(dispatch_question_id="dispatch-question-0001")
        self.assertEqual(TicketProposalState.IN_PROGRESS, opened_proposal.state)
        self.assertEqual("dispatch-question-0001", opened_proposal.dispatch_question_id)
        with self.assertRaises(ValueError):
            opened_proposal.open(dispatch_question_id="dispatch-question-0002")
        decision = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id="dispatch-without-proposal-0001",
                kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual(ContinuationDirective.HALT, decision.continuation)
        self.assertIsNone(decision.next_stage)
        planned = self.engine.decide(
            state=self._ticket_state(),
            event=RouterEvent(
                event_id="dispatch-planned-proposal-0001",
                kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                ticket_proposal=self._proposal().model_copy(
                    update={"state": TicketProposalState.PLANNED, "dispatch_question_id": None}
                ),
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, planned.outcome)
        self.assertEqual(ContinuationDirective.HALT, planned.continuation)

    def test_ticket_lane_retains_named_implementation_capability_and_reviewer(self) -> None:
        receipt = self._receipt()
        decision = self.engine.decide(
            state=self._ticket_state().model_copy(update={"pending_dispatch": self._pending()}),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertIsNotNone(decision.dispatch_plan)
        assert decision.dispatch_plan is not None
        self.assertTrue(hasattr(decision.dispatch_plan.ticket_lane, "implementation_capability"))
        self.assertTrue(hasattr(decision.dispatch_plan.ticket_lane, "reviewer"))
        self.assertTrue(decision.ticket_lane_capabilities)
        mismatched_state = self._ticket_state().model_copy(
            update={"topology": CollaborationTopology.TWO_COLLABORATING_AGENTS}
        )
        halted = self.engine.decide(
            state=mismatched_state,
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, halted.outcome)
        self.assertEqual("topology_required", halted.blockers[0].code.value)

    def test_positive_receipt_creates_one_ticket_plan_and_planning_grill_route(self) -> None:
        receipt = self._receipt()
        decision = self.engine.decide(
            state=self._ticket_state().model_copy(update={"pending_dispatch": self._pending()}),
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
                dispatch_question_id=receipt.dispatch_question_id,
                worktree_fingerprint=receipt.worktree_fingerprint,
                branch_fingerprint=receipt.branch_fingerprint,
            )
        with self.assertRaises(ValidationError):
            TicketDispatchReceipt.model_validate({})
        for invalid_worktree in (
            "worktree-implementation-01/",
            "worktree-implementation-01\\suffix",
            "WORKTREE-IMPLEMENTATION-01",
            "worktree-implementation-01%2fencoded",
            "worktree-implementation-01-../traversal",
            "",
            None,
        ):
            with self.subTest(invalid_worktree=invalid_worktree), self.assertRaises(ValidationError):
                TicketDispatchReceipt.model_validate(
                    {
                        **receipt.model_dump(),
                        "worktree_fingerprint": invalid_worktree,
                    }
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
        owner_mismatch = self.engine.decide(
            state=self._ticket_state().model_copy(update={"pending_dispatch": self._pending()}),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt.model_copy(
                    update={"implementation_owner_id": "other-implementation-owner"}
                ),
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, owner_mismatch.outcome)
        self.assertEqual(ContinuationDirective.HALT, owner_mismatch.continuation)
        self.assertEqual("invalid_pending_dispatch", owner_mismatch.blockers[0].code.value)

    def test_null_empty_and_container_dispatch_inputs_fail_closed(self) -> None:
        receipt = self._receipt()
        for field_name, invalid_value in (
            ("worktree_fingerprint", None),
            ("worktree_fingerprint", ""),
            ("worktree_fingerprint", " "),
            ("branch_fingerprint", {}),
            ("branch_fingerprint", []),
        ):
            with self.subTest(field_name=field_name, invalid_value=invalid_value), self.assertRaises(
                ValidationError
            ):
                TicketDispatchReceipt.model_validate(
                    {**receipt.model_dump(), field_name: invalid_value}
                )
        with self.assertRaises(ValidationError):
            CollaborationTopologyPlan.model_validate(
                {
                    "topology": None,
                    "control_plane": self.control.model_dump(),
                    "implementation_owner": self.implementation.model_dump(),
                    "reviewer": self.reviewer.model_dump(),
                }
            )
        with self.assertRaises(ValueError):
            CollaborationTopologyResolver().select(
                available_agent_count=1,
                control_plane=self.control,
                implementation_owner=self.implementation,
                available_capabilities=None,  # type: ignore[arg-type]
            )

    def test_dispatch_source_adapter_exception_is_not_converted_to_a_grant(self) -> None:
        class ExplodingSourceGateway:
            def read(self, source: ArtifactRef) -> SourceSnippet:
                raise RuntimeError("adapter unavailable")

        with self.assertRaisesRegex(RuntimeError, "adapter unavailable"):
            ContextResolver(source_gateway=ExplodingSourceGateway()).resolve(
                event_id="dispatch-adapter-exception-0001",
                required_sources=(self.ticket,),
                target_artifact=self.ticket,
                consumer=ConsumerFingerprint(
                    agent_profile="implementation-owner",
                    profile_version="profile-v1",
                    worktree_id="worktree-implementation-01",
                    execution_id="execution-ticket-01",
                ),
            )

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
        missing_handoff = client.route(
            raw_request=self._private_request(
                account=account,
                project=project,
                event=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                event_id="evt_00000000000000000000000000000060",
                include_dispatch_handoff=False,
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.HALT, missing_handoff.mode)
        waiting = client.route(raw_request=wait_request.model_dump())
        self.assertEqual(ContinuationMode.WAIT_FOR_HUMAN, waiting.mode)
        self.assertEqual(ProductActionLabel.REQUEST_APPROVAL, waiting.action_label)
        self.assertIsNone(waiting.dispatch_plan)
        self.assertEqual(self._proposal(), waiting.ticket_proposal)
        self.assertEqual((), waiting.ticket_lane_capabilities)

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
                correlation_id="evt_00000000000000000000000000000061",
                dispatch_question_id=receipt.dispatch_question_id,
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
        self.assertEqual((self.implementation,), plan.ticket_lane_capabilities)

        replay = client.route(raw_request=confirmed.model_dump())
        self.assertEqual(ContinuationMode.HALT, replay.mode)
        self.assertIsNone(replay.dispatch_plan)
        self.assertEqual((), replay.ticket_lane_capabilities)

    def test_private_router_rejects_forged_pending_dispatch_from_fresh_client(self) -> None:
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
        receipt = self._receipt().model_copy(
            update={"correlation_id": "evt_00000000000000000000000000000064"}
        )
        forged = self._private_request(
            account=account,
            project=project,
            event=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
            event_id="evt_00000000000000000000000000000064",
            dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
            dispatch_receipt=receipt,
        ).model_dump()
        forged["pending_dispatch"] = self._pending().model_dump()
        plan = client.route(raw_request=forged)
        self.assertEqual(ContinuationMode.HALT, plan.mode)
        self.assertIsNone(plan.dispatch_plan)
        self.assertEqual((), plan.ticket_lane_capabilities)

    def test_expected_main_revision_is_separate_from_proposal_revision(self) -> None:
        receipt = self._receipt()
        self.assertNotEqual(self._pending().proposal_revision, self._pending().expected_main_revision)
        decision = self.engine.decide(
            state=self._ticket_state().model_copy(update={"pending_dispatch": self._pending()}),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt,
            ),
            profile=self.profile,
        )
        self.assertEqual(ContinuationDirective.AUTO_CONTINUE, decision.continuation)
        mismatched = self.engine.decide(
            state=self._ticket_state().model_copy(update={"pending_dispatch": self._pending()}),
            event=RouterEvent(
                event_id=receipt.correlation_id,
                kind=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                dispatch_confirmation=TicketDispatchConfirmation.POSITIVE,
                dispatch_receipt=receipt.model_copy(
                    update={"expected_main_revision": "rev-ffffffffffffffff"}
                ),
            ),
            profile=self.profile,
        )
        self.assertEqual(ContinuationDirective.HALT, mismatched.continuation)
        self.assertEqual("invalid_pending_dispatch", mismatched.blockers[0].code.value)

    def test_private_router_legacy_ticket_approval_with_handoff_is_blocked(self) -> None:
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
        plan = PrivateRouterClient(service=service).route(
            raw_request=self._private_request(
                account=account,
                project=project,
                event=RouterEventKind.APPROVAL_GRANTED,
                event_id="evt_00000000000000000000000000000063",
                implementation_handoff=self._handoff(),
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.HALT, plan.mode)
        self.assertEqual((), plan.required_source_kinds)
        self.assertIsNone(plan.dispatch_plan)

    def _ticket_state(self) -> RouterState:
        return RouterState(
            project_id="autonomous-collaboration-audit",
            stage=ProcessStage.TICKETS,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.ticket,),
            topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
            collaboration_plan=CollaborationTopologyPlan(
                topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
                control_plane=self.control,
                implementation_owner=self.implementation,
                reviewer=self.reviewer,
            ),
            pending_dispatch=None,
        )

    def _pending(self) -> PendingDispatchDescriptor:
        return PendingDispatchDescriptor(
            ticket_reference=self.ticket.identifier,
            proposal_revision="rev-0123456789abcdef",
            expected_main_revision="rev-abcdef0123456789",
            dispatch_question_id="dispatch-question-0001",
            implementation_owner_id=self.implementation.agent_profile,
            reviewed_handoff_reference="handoff-topology-dispatch-01",
            event_correlation_id="dispatch-confirmed-0001",
        )

    def _proposal(self) -> TicketProposal:
        planned = TicketProposal(
            ticket_reference=self.ticket.identifier,
            state=TicketProposalState.PLANNED,
            implementation_owner_id=self.implementation.agent_profile,
            proposal_revision="rev-0123456789abcdef",
        )
        return planned.open(dispatch_question_id="dispatch-question-0001")

    def _handoff(self) -> ImplementationHandoff:
        return ImplementationHandoff(
            handoff_reference="handoff-topology-dispatch-01",
            ticket_reference=self.ticket.identifier,
            approved_spec_reference="spec-autonomous-collaboration-01",
            expected_main_revision="rev-abcdef0123456789",
            context_references=(
                HandoffArtifactReference(
                    artifact_id="context-autonomous-collaboration",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-ticket-dispatch",
                    side_context_id="side-ticket-dispatch",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-01",
                        execution_fingerprint="execution-ticket-01",
                    ),
                ),
            ),
            acceptance_references=("acceptance-ac-1",),
            tdd_references=("tdd-dispatch-lanes",),
            scope=TicketScope.NON_FRONTEND,
            non_frontend_reason="no formal UI boundary",
            control_owner_id="control-plane",
            implementation_owner_id="implementation-owner",
            reviewer_id="reviewer",
        )

    def _receipt(self) -> TicketDispatchReceipt:
        return TicketDispatchReceipt(
            ticket_reference=self.ticket.identifier,
            implementation_owner_id="implementation-owner",
            handoff_reference="handoff-topology-dispatch-01",
            expected_main_revision="rev-abcdef0123456789",
            correlation_id="dispatch-confirmed-0001",
            dispatch_question_id="dispatch-question-0001",
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
        implementation_handoff: ImplementationHandoff | None = None,
        include_dispatch_handoff: bool = True,
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
            collaboration_plan=CollaborationTopologyPlan(
                topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
                control_plane=self.control,
                implementation_owner=self.implementation,
                reviewer=self.reviewer,
            ),
            ticket_reference=self.ticket.identifier,
            implementation_handoff=(
                implementation_handoff
                if implementation_handoff is not None
                else self._handoff()
                if event is RouterEventKind.TICKET_DISPATCH_REQUIRED and include_dispatch_handoff
                else None
            ),
            dispatch_confirmation=dispatch_confirmation,
            dispatch_receipt=dispatch_receipt,
            ticket_proposal=(
                self._proposal()
                if event is RouterEventKind.TICKET_DISPATCH_REQUIRED
                else None
            ),
        )


if __name__ == "__main__":
    unittest.main()
