"""Fresh TDD contracts for metadata-only policy reads and trusted dispatch output."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import cast

from library.workflow_router import (
    ApprovedDispatchArtifact,
    ArtifactRef,
    ArtifactKind,
    AuthorityState,
    CapabilityRef,
    CollaborationTopology,
    CollaborationTopologyPlan,
    ContinuationDirective,
    DeliveryStage,
    FakeEntitlementProvider,
    FakePrivateRouterService,
    HandoffArtifactReference,
    HandoffConsumerFingerprint,
    ImplementationHandoff,
    PendingDispatchDescriptor,
    PrivateRouterClient,
    ProcessStage,
    RedactedSummary,
    RouterEngine,
    RouterEventKind,
    RouterEvent,
    RouterRequestEnvelope,
    RouterState,
    StaticApprovedDispatchArtifactRegistry,
    TicketDispatchConfirmation,
    TicketDispatchReceipt,
    TicketProposal,
    TicketProposalState,
    TicketScope,
    build_router_poc_profile,
)
from library.workflow_router.policy_response import (
    CommittedDispatchArtifacts,
    DispatchResponseFormatter,
    FixedDispatchResponse,
    PolicyDocumentMetadata,
    PolicyDocumentResult,
    PolicyReadError,
    PolicyReadOutcome,
    render_dispatch_response,
    render_trusted_dispatch_response,
    read_policy_document,
)
from library.workflow_router.private_router import (
    ContinuationPlan,
    EntitlementGrant,
    EntitlementMode,
)


class _RawPolicySource:
    def __init__(self, value: str) -> None:
        self.value = value

    def read(self) -> str:
        return self.value


class _FailingPolicySource:
    def read(self) -> PolicyDocumentMetadata:
        raise RuntimeError("raw source failure must not cross the boundary")


class _MetadataPolicySource:
    def read(self) -> PolicyDocumentMetadata:
        return PolicyDocumentMetadata(
            source_id="policy-source-01",
            revision="rev-0123456789abcdef",
            evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )


class _MutatingFormatter(DispatchResponseFormatter):
    def format(self, response: FixedDispatchResponse) -> str:
        del response
        return "工單 ready\n/path/to/secret"


class _RaisingFormatter(DispatchResponseFormatter):
    def format(self, response: FixedDispatchResponse) -> str:
        del response
        raise RuntimeError("formatter detail must not escape")


class _FakePendingPlanOwner:
    def owns_pending_dispatch_plan(self, plan: object) -> bool:
        del plan
        return True


class PluginPolicyAndResponseTests(unittest.TestCase):
    """Prove policy text and dispatch authority stay outside public Router models."""

    def setUp(self) -> None:
        self.account = "acct_0123456789abcdef"
        self.project = "prj_fedcba9876543210"
        self.ticket_reference = "ticket-plugin-policy-03"
        self.control = CapabilityRef(
            capability_id="cap-control-plane",
            version="1",
            agent_profile="control-plane",
        )
        self.implementation = CapabilityRef(
            capability_id="cap-plugin-implementation",
            version="1",
            agent_profile="implementation-owner",
        )
        self.reviewer = CapabilityRef(
            capability_id="cap-plugin-reviewer",
            version="1",
            agent_profile="reviewer",
        )
        self.handoff = ImplementationHandoff(
            handoff_reference="handoff-plugin-policy-03",
            ticket_reference=self.ticket_reference,
            approved_spec_reference="spec-plugin-policy-03",
            expected_main_revision="rev-0123456789abcdef",
            context_references=(
                HandoffArtifactReference(
                    artifact_id="context-plugin-policy-03",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-plugin-policy-03",
                    side_context_id="side-plugin-policy-03",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-03",
                        execution_fingerprint="execution-plugin-03",
                    ),
                ),
            ),
            acceptance_references=("acceptance-ac-1",),
            tdd_references=("tdd-plugin-policy-03",),
            scope=TicketScope.NON_FRONTEND,
            non_frontend_reason="no formal UI boundary",
            ticket_docs_commit="b84c2a5",
            handoff_docs_commit="c569056",
            control_owner_id=self.control.capability_id,
            implementation_owner_id=self.implementation.capability_id,
            reviewer_id=self.reviewer.capability_id,
        )
        self.approved_registry = StaticApprovedDispatchArtifactRegistry(
            records=(
                ApprovedDispatchArtifact(
                    ticket_reference=self.ticket_reference,
                    handoff_reference=self.handoff.handoff_reference,
                    implementation_owner_id=self.implementation.capability_id,
                    ticket_docs_commit="b84c2a5",
                    handoff_docs_commit="c569056",
                ),
            )
        )
        service = FakePrivateRouterService(
            profile=build_router_poc_profile(),
            entitlement_provider=FakeEntitlementProvider(
                grants=(
                    EntitlementGrant(
                        account_subject_id=self.account,
                        opaque_project_id=self.project,
                        permitted_modes=(EntitlementMode.FIRST_PROJECT_FREE,),
                    ),
                )
            ),
            approved_dispatch_artifact_registry=self.approved_registry,
        )
        self.client = PrivateRouterClient(
            service=service,
            approved_dispatch_artifact_registry=self.approved_registry,
        )

    def _proposal(self) -> TicketProposal:
        return TicketProposal(
            ticket_reference=self.ticket_reference,
            state=TicketProposalState.IN_PROGRESS,
            implementation_owner_id=self.implementation.capability_id,
            dispatch_question_id="dispatch-question-plugin-03",
            proposal_revision="rev-0123456789abcdef",
        )

    def _request(
        self,
        *,
        event: RouterEventKind,
        event_id: str,
        handoff: ImplementationHandoff | None = None,
        receipt: TicketDispatchReceipt | None = None,
        confirmation: TicketDispatchConfirmation | None = None,
    ) -> RouterRequestEnvelope:
        return RouterRequestEnvelope(
            request_id=f"req_{event_id.removeprefix('evt_')}",
            account_subject_id=self.account,
            opaque_project_id=self.project,
            project_entry_mode="new_project",
            entitlement_mode=EntitlementMode.FIRST_PROJECT_FREE,
            workflow_stage=ProcessStage.TICKETS,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            router_event_kind=event,
            event_correlation_id=event_id,
            available_source_kinds=(ArtifactKind.TICKET,),
            revision_digests=(
                "rev_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            ),
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
            ticket_reference=self.ticket_reference,
            implementation_handoff=(
                handoff or self.handoff
                if event is RouterEventKind.TICKET_DISPATCH_REQUIRED
                else None
            ),
            dispatch_confirmation=confirmation,
            dispatch_receipt=receipt,
            ticket_proposal=self._proposal() if event is RouterEventKind.TICKET_DISPATCH_REQUIRED else None,
        )

    def _waiting_plan(self) -> ContinuationPlan:
        return self.client.route(
            raw_request=self._request(
                event=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                event_id="evt_00000000000000000000000000000071",
            ).model_dump()
        )

    def _artifacts(self, *, ticket: str | None = None) -> CommittedDispatchArtifacts:
        return CommittedDispatchArtifacts(
            ticket_docs_commit="b84c2a5",
            ticket_reference=ticket or self.ticket_reference,
            handoff_docs_commit="c569056",
            handoff_reference=self.handoff.handoff_reference,
        )

    def test_raw_policy_sentinel_is_rejected_and_never_serialized(self) -> None:
        sentinel = "SYNTHETIC_POLICY_SENTINEL_03"
        result = read_policy_document(_RawPolicySource(sentinel))
        self.assertEqual(PolicyReadOutcome.HALT, result.outcome)
        self.assertEqual(PolicyReadError.INVALID_DOCUMENT, result.error)
        self.assertIsNone(result.metadata)
        self.assertNotIn(sentinel, result.model_dump_json())
        self.assertNotIn(sentinel, str(result))
        self.assertNotIn("text", result.model_dump())

    def test_policy_source_failure_and_metadata_success_are_stable(self) -> None:
        failed = read_policy_document(_FailingPolicySource())
        self.assertEqual(PolicyReadOutcome.HALT, failed.outcome)
        self.assertEqual(PolicyReadError.SOURCE_FAILURE, failed.error)
        loaded = read_policy_document(_MetadataPolicySource())
        self.assertEqual(PolicyReadOutcome.LOADED, loaded.outcome)
        self.assertIsNotNone(loaded.metadata)
        self.assertNotIn("text", loaded.model_dump())

    def test_only_private_router_owned_pending_plan_can_render_exact_response(self) -> None:
        waiting = self._waiting_plan()
        self.assertIsNotNone(waiting.pending_dispatch)
        pending = cast(PendingDispatchDescriptor, waiting.pending_dispatch)
        rendered = self.client.render_dispatch_response(
            plan=waiting,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("rendered", rendered.outcome.value)
        self.assertIsNotNone(rendered.text)
        text = cast(str, rendered.text)
        self.assertIn("工單 ready", text)
        self.assertIn("- commit：b84c2a5", text)
        self.assertIn(f"- 工單：{pending.ticket_reference}", text)
        self.assertIn("文件交接", text)
        self.assertIn("- commit：c569056", text)
        self.assertIn(f"- implementation owner：{pending.implementation_owner_id}", text)
        self.assertIn(
            f"- 工單 {pending.ticket_reference} 是否已交付給 implementation owner {pending.implementation_owner_id}？",
            text,
        )
        asserted_artifacts = self.client.render_dispatch_response(
            plan=waiting,
            artifacts=self._artifacts(),
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("rendered", asserted_artifacts.outcome.value)
        self.assertEqual(text, asserted_artifacts.text)

    def test_forged_response_and_mismatched_artifacts_halt(self) -> None:
        waiting = self._waiting_plan()
        pending = cast(PendingDispatchDescriptor, waiting.pending_dispatch)
        forged = FixedDispatchResponse(
            pending_dispatch=pending,
            ticket_docs_commit=pending.ticket_docs_commit or "b84c2a5",
            ticket_reference=pending.ticket_reference,
            handoff_docs_commit=pending.handoff_docs_commit or "c569056",
            handoff_reference=pending.reviewed_handoff_reference,
            implementation_owner_id=pending.implementation_owner_id,
        )
        direct = render_dispatch_response(forged, DispatchResponseFormatter())
        self.assertEqual("halt", direct.outcome.value)
        self.assertIsNone(direct.text)
        forged_plan = waiting.model_copy(
            update={
                "pending_dispatch": pending.model_copy(
                    update={"ticket_reference": "ticket-forged-03"}
                )
            }
        )
        mismatch = self.client.render_dispatch_response(
            plan=forged_plan,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", mismatch.outcome.value)
        self.assertIsNone(mismatch.text)

    def test_indirect_fake_owner_copied_plan_and_alternate_client_halt(self) -> None:
        waiting = self._waiting_plan()
        fake_owner = render_trusted_dispatch_response(
            client=_FakePendingPlanOwner(),
            plan=waiting,
            artifacts=self._artifacts(),
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", fake_owner.outcome.value)
        self.assertIsNone(fake_owner.text)
        copied = type(waiting).model_validate(waiting.model_dump())
        copied_result = self.client.render_dispatch_response(
            plan=copied,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", copied_result.outcome.value)
        self.assertIsNone(copied_result.text)
        alternate = PrivateRouterClient(service=self.client._service)
        alternate_result = alternate.render_dispatch_response(
            plan=waiting,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", alternate_result.outcome.value)
        self.assertIsNone(alternate_result.text)

    def test_valid_shaped_forged_commits_and_handoff_halt(self) -> None:
        waiting = self._waiting_plan()
        forged_commits = self._artifacts().model_copy(
            update={"ticket_docs_commit": "deadbee", "handoff_docs_commit": "cafe123"}
        )
        forged_result = self.client.render_dispatch_response(
            plan=waiting,
            artifacts=forged_commits,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", forged_result.outcome.value)
        self.assertIsNone(forged_result.text)
        forged_handoff = self._artifacts().model_copy(
            update={"handoff_reference": "handoff-forged-03"}
        )
        handoff_result = self.client.render_dispatch_response(
            plan=waiting,
            artifacts=forged_handoff,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", handoff_result.outcome.value)
        self.assertIsNone(handoff_result.text)

    def test_unregistered_valid_shaped_handoff_substitutions_halt_before_pending(self) -> None:
        substitutions = (
            ("ticket_commit", {"ticket_docs_commit": "deadbee"}),
            ("handoff_commit", {"handoff_docs_commit": "cafe123"}),
            ("ticket_identity", {"ticket_reference": "ticket-forged-03"}),
            ("handoff_identity", {"handoff_reference": "handoff-forged-03"}),
            ("owner_identity", {"implementation_owner_id": "cap-forged-owner"}),
        )
        for index, (label, update) in enumerate(substitutions):
            with self.subTest(substitution=label):
                forged_handoff = self.handoff.model_copy(update=update)
                request = self._request(
                    event=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                    event_id=f"evt_{91 + index:032x}",
                    handoff=forged_handoff,
                )
                private_plan = self.client.route(raw_request=request.model_dump())
                self.assertEqual("halt", private_plan.mode.value)
                self.assertIsNone(private_plan.pending_dispatch)

                direct = RouterEngine(
                    approved_dispatch_artifact_registry=self.approved_registry,
                ).decide(
                    state=RouterState(
                        project_id=self.project,
                        stage=ProcessStage.TICKETS,
                        authority_state=AuthorityState.APPROVED,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(
                            ArtifactRef(
                                kind=ArtifactKind.TICKET,
                                identifier=self.ticket_reference,
                                uri="ticket://plugin-policy-03",
                                revision="b84c2a5",
                            ),
                        ),
                        topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
                        collaboration_plan=CollaborationTopologyPlan(
                            topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
                            control_plane=self.control,
                            implementation_owner=self.implementation,
                            reviewer=self.reviewer,
                        ),
                    ),
                    event=RouterEvent(
                        event_id=request.event_correlation_id,
                        kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                        implementation_handoff=forged_handoff,
                        ticket_proposal=self._proposal(),
                    ),
                    profile=build_router_poc_profile(),
                )
                self.assertEqual(ContinuationDirective.HALT, direct.continuation)
                self.assertIsNone(direct.pending_dispatch)

    def test_each_path_and_uri_boundary_is_rejected_at_artifact_boundary(self) -> None:
        boundary_values = (
            ("exact_equal", r"C:\repo\ticket.md"),
            ("one_extra_character_prefix", r"xC:\repo\ticket.md"),
            ("trailing_slash", "C:\\repo\\ticket.md\\"),
            ("casing_variant", r"c:\REPO\Ticket.MD"),
            ("url_encoded_variant", "C:%5Crepo%5Cticket.md"),
            ("traversal_variant", r"C:\repo\..\ticket.md"),
            ("empty_value", ""),
        )
        for label, boundary in boundary_values:
            for field in ("ticket_docs_commit", "handoff_docs_commit"):
                with self.subTest(boundary=f"{label}:{field}"):
                    payload: dict[str, object] = {
                        "ticket_docs_commit": "b84c2a5",
                        "ticket_reference": self.ticket_reference,
                        "handoff_docs_commit": "c569056",
                        "handoff_reference": self.handoff.handoff_reference,
                    }
                    payload[field] = boundary
                    with self.assertRaises(ValueError):
                        CommittedDispatchArtifacts.model_validate(payload)

    def test_omitted_null_empty_and_container_commit_values_halt(self) -> None:
        for field in ("ticket_docs_commit", "handoff_docs_commit"):
            other_field = "handoff_docs_commit" if field == "ticket_docs_commit" else "ticket_docs_commit"
            other_value = "c569056" if other_field == "handoff_docs_commit" else "b84c2a5"
            for label, value in (
                ("omitted", None),
                ("null", None),
                ("empty", ""),
                ("whitespace", "   "),
                ("empty_list", []),
                ("empty_object", {}),
            ):
                with self.subTest(field=field, value=label):
                    payload: dict[str, object] = {
                        "ticket_reference": self.ticket_reference,
                        "handoff_reference": self.handoff.handoff_reference,
                        other_field: other_value,
                    }
                    if label != "omitted":
                        payload[field] = value
                    with self.assertRaises(ValueError):
                        CommittedDispatchArtifacts.model_validate(payload)

    def test_invalid_commit_values_halt_before_private_pending_or_lane(self) -> None:
        for field in ("ticket_docs_commit", "handoff_docs_commit"):
            invalid_values: tuple[tuple[str, object], ...] = (
                ("omitted", None),
                ("null", None),
                ("empty", ""),
                ("whitespace", "   "),
                ("empty_list", []),
                ("empty_object", {}),
            )
            for index, (label, value) in enumerate(invalid_values):
                with self.subTest(field=field, value=label):
                    event_id = f"evt_{(0xA1 + index + (0 if field == 'ticket_docs_commit' else 16)):032x}"
                    payload = self._request(
                        event=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                        event_id=event_id,
                    ).model_dump()
                    handoff_payload = cast(dict[str, object], payload["implementation_handoff"])
                    if label == "omitted":
                        handoff_payload.pop(field)
                    else:
                        handoff_payload[field] = value
                    halted = self.client.route(raw_request=payload)
                    self.assertEqual("halt", halted.mode.value)
                    self.assertIsNone(halted.pending_dispatch)
                    self.assertEqual((), halted.ticket_lane_capabilities)

    def test_missing_reviewed_commits_halt_direct_and_private_before_pending_or_lane(self) -> None:
        missing_ticket = self.handoff.model_copy(update={"ticket_docs_commit": None})
        missing_handoff = self.handoff.model_copy(update={"handoff_docs_commit": None})
        missing_both = self.handoff.model_copy(
            update={"ticket_docs_commit": None, "handoff_docs_commit": None}
        )
        for label, handoff in (
            ("missing_ticket", missing_ticket),
            ("missing_handoff", missing_handoff),
            ("missing_both", missing_both),
        ):
            with self.subTest(case=label):
                request = self._request(
                    event=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                    event_id=f"evt_000000000000000000000000000000{80 + len(label):02d}",
                    handoff=handoff,
                )
                private_plan = self.client.route(raw_request=request.model_dump())
                self.assertEqual("halt", private_plan.mode.value)
                self.assertIsNone(private_plan.pending_dispatch)
                direct = RouterEngine().decide(
                    state=RouterState(
                        project_id=self.project,
                        stage=ProcessStage.TICKETS,
                        authority_state=AuthorityState.APPROVED,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(
                            ArtifactRef(
                                kind=ArtifactKind.TICKET,
                                identifier=self.ticket_reference,
                                uri="ticket://plugin-policy-03",
                                revision="b84c2a5",
                            ),
                        ),
                        topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
                        collaboration_plan=CollaborationTopologyPlan(
                            topology=CollaborationTopology.ONE_IMPLEMENTATION_AGENT,
                            control_plane=self.control,
                            implementation_owner=self.implementation,
                            reviewer=self.reviewer,
                        ),
                    ),
                    event=RouterEvent(
                        event_id=request.event_correlation_id,
                        kind=RouterEventKind.TICKET_DISPATCH_REQUIRED,
                        implementation_handoff=handoff,
                        ticket_proposal=self._proposal(),
                    ),
                    profile=build_router_poc_profile(),
                )
                self.assertEqual(ContinuationDirective.HALT, direct.continuation)
                self.assertIsNone(direct.pending_dispatch)

    def test_confirmation_consumes_pending_response_and_replay_halts(self) -> None:
        waiting = self._waiting_plan()
        pending = cast(PendingDispatchDescriptor, waiting.pending_dispatch)
        receipt = TicketDispatchReceipt(
            ticket_reference=pending.ticket_reference,
            implementation_owner_id=pending.implementation_owner_id,
            handoff_reference=pending.reviewed_handoff_reference,
            expected_main_revision=pending.expected_main_revision,
            correlation_id=pending.event_correlation_id,
            dispatch_question_id=pending.dispatch_question_id,
            worktree_fingerprint="worktree-plugin-03",
            branch_fingerprint="branch-plugin-03",
        )
        self.client.route(
            raw_request=self._request(
                event=RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
                event_id="evt_00000000000000000000000000000072",
                receipt=receipt,
                confirmation=TicketDispatchConfirmation.POSITIVE,
            ).model_dump()
        )
        replay = self.client.render_dispatch_response(
            plan=waiting,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", replay.outcome.value)
        self.assertIsNone(replay.text)

    def test_formatter_mutation_exception_and_invalid_commit_fail_closed(self) -> None:
        waiting = self._waiting_plan()
        mutated = self.client.render_dispatch_response(
            plan=waiting,
            formatter=_MutatingFormatter(),
        )
        self.assertEqual("halt", mutated.outcome.value)
        self.assertIsNone(mutated.text)
        failed = self.client.render_dispatch_response(
            plan=waiting,
            formatter=_RaisingFormatter(),
        )
        self.assertEqual("halt", failed.outcome.value)
        self.assertIsNone(failed.text)
        with self.assertRaises(ValueError):
            CommittedDispatchArtifacts(
                ticket_docs_commit="C:/secret/path",
                ticket_reference=self.ticket_reference,
                handoff_docs_commit="c569056",
                handoff_reference=self.handoff.handoff_reference,
            )

    def test_absent_pending_descriptor_and_mismatched_fixed_model_halt(self) -> None:
        halted = self.client.route(
            raw_request=self._request(
                event=RouterEventKind.APPROVAL_GRANTED,
                event_id="evt_00000000000000000000000000000074",
            ).model_dump()
        )
        absent = self.client.render_dispatch_response(
            plan=halted,
            formatter=DispatchResponseFormatter(),
        )
        self.assertEqual("halt", absent.outcome.value)
        self.assertIsNone(absent.text)
        waiting = self._waiting_plan()
        pending = cast(PendingDispatchDescriptor, waiting.pending_dispatch)
        with self.assertRaises(ValueError):
            FixedDispatchResponse(
                pending_dispatch=pending,
                ticket_docs_commit="b84c2a5",
                ticket_reference="ticket-forged-03",
                handoff_docs_commit="c569056",
                handoff_reference=pending.reviewed_handoff_reference,
                implementation_owner_id=pending.implementation_owner_id,
            )
        with self.assertRaises(ValueError):
            FixedDispatchResponse(
                pending_dispatch=pending,
                ticket_docs_commit=pending.ticket_docs_commit or "b84c2a5",
                ticket_reference=pending.ticket_reference,
                handoff_docs_commit=pending.handoff_docs_commit or "c569056",
                handoff_reference=pending.reviewed_handoff_reference,
                implementation_owner_id="cap-forged-owner",
            )

    def test_legacy_approval_route_is_not_a_dispatch_response(self) -> None:
        legacy = self.client.route(
            raw_request=self._request(
                event=RouterEventKind.APPROVAL_GRANTED,
                event_id="evt_00000000000000000000000000000073",
            ).model_dump()
        )
        self.assertEqual("halt", legacy.mode.value)
        self.assertIsNone(legacy.pending_dispatch)

    def test_workflow_skill_template_and_readme_publish_the_same_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / "Workflow.md").read_text(encoding="utf-8")
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        skill = (root / "skills" / "johnny-project-takeover" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        template = (root / "template" / "README.md").read_text(encoding="utf-8")
        for document in (workflow, agents, readme, skill, template):
            self.assertIn("metadata", document.lower())
            self.assertIn("pending", document.lower())
        self.assertIn("TICKETS + APPROVAL_GRANTED", workflow)
        self.assertIn("active product objective", readme)


if __name__ == "__main__":
    unittest.main()
