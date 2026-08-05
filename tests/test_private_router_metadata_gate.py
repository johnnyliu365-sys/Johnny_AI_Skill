"""TDD acceptance tests for the private Router POC metadata gate."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from library.workflow_router import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    CompletionActionKind,
    CompletionEvidence,
    ConsumerFingerprint,
    ContinuationDirective,
    DeliveryStage,
    HandoffArtifactReference,
    HandoffConsumerFingerprint,
    InMemorySourceGateway,
    ImplementationHandoff,
    ImplementationReturn,
    ImplementationReturnStatus,
    ProcessStage,
    RouterEventKind,
    RouterOutcome,
    SourceSnippet,
    TicketScope,
    build_router_poc_profile,
)
from library.workflow_router.private_router import (
    AutomaticContinuationRunner,
    ContinuationMode,
    EntitlementGrant,
    EntitlementMode,
    FakeEntitlementProvider,
    FakePrivateRouterService,
    LocalContextGate,
    LocalMetadataNormalizer,
    PrivateRouterClient,
    ProductActionLabel,
    RedactedSummary,
    RouterRequestEnvelope,
    RouterResponseEnvelope,
    RouterServiceErrorCode,
)
from library.workflow_router.router import ContextResolver


class PrivateRouterMetadataGateTests(unittest.TestCase):
    """Prove the POC is metadata-only, fail-closed, and continuously routed when safe."""

    def setUp(self) -> None:
        self.account_subject_id = "acct_0123456789abcdef"
        self.project_id = "prj_fedcba9876543210"
        self.entitlements = FakeEntitlementProvider(
            grants=(
                EntitlementGrant(
                    account_subject_id=self.account_subject_id,
                    opaque_project_id=self.project_id,
                    permitted_modes=(EntitlementMode.FIRST_PROJECT_FREE,),
                ),
            )
        )
        self.service = FakePrivateRouterService(
            profile=build_router_poc_profile(),
            entitlement_provider=self.entitlements,
        )
        self.client = PrivateRouterClient(service=self.service)

    def test_valid_metadata_autoruns_until_the_first_explicit_human_gate(self) -> None:
        initial = self.request_for(
            stage=ProcessStage.INTAKE,
            event=RouterEventKind.INTAKE,
            event_id="evt_00000000000000000000000000000001",
            source_kinds=(ArtifactKind.PROJECT_GOAL,),
        )
        runner = AutomaticContinuationRunner(
            client=self.client,
            executor=ScriptedExecutor(
                requests=(
                    self.request_for(
                        stage=ProcessStage.WAYFINDER,
                        event=RouterEventKind.WAYFINDER_GO,
                        event_id="evt_00000000000000000000000000000002",
                        source_kinds=(ArtifactKind.WAYFINDER_OUTPUT,),
                    ),
                    self.request_for(
                        stage=ProcessStage.ARCHITECTURE,
                        event=RouterEventKind.ACTION_COMPLETED,
                        event_id="evt_00000000000000000000000000000003",
                        source_kinds=(ArtifactKind.ARCHITECTURE,),
                    ),
                    self.request_for(
                        stage=ProcessStage.GRILL,
                        event=RouterEventKind.ACTION_COMPLETED,
                        event_id="evt_00000000000000000000000000000004",
                        source_kinds=(ArtifactKind.GRILL,),
                    ),
                    self.request_for(
                        stage=ProcessStage.CONTEXT,
                        event=RouterEventKind.ACTION_COMPLETED,
                        event_id="evt_00000000000000000000000000000005",
                        source_kinds=(ArtifactKind.CONTEXT,),
                    ),
                    self.request_for(
                        stage=ProcessStage.SPEC,
                        event=RouterEventKind.ACTION_COMPLETED,
                        event_id="evt_00000000000000000000000000000006",
                        source_kinds=(ArtifactKind.SPEC,),
                    ),
                )
            ),
        )

        result = runner.run_until_pause(initial_request=initial, max_auto_steps=6)

        self.assertEqual(ContinuationMode.WAIT_FOR_HUMAN, result.final_plan.mode)
        self.assertEqual(ProductActionLabel.REQUEST_APPROVAL, result.final_plan.action_label)
        self.assertEqual(5, result.auto_steps)
        self.assertIsNone(result.final_plan.error_code)

    def test_metadata_normalizer_rejects_sensitive_unknown_or_empty_input_before_transport(self) -> None:
        valid = self.request_for(
            stage=ProcessStage.INTAKE,
            event=RouterEventKind.INTAKE,
            event_id="evt_00000000000000000000000000000011",
            source_kinds=(ArtifactKind.PROJECT_GOAL,),
        ).model_dump()
        invalid_payloads = (
            {**valid, "source_path": "C:/company/secret.py"},
            {**valid, "uri": "project://company/secret"},
            {**valid, "filename": "secret.py"},
            {**valid, "source_path": "../company/secret.py"},
            {**valid, "prompt": "read all customer source"},
            {**valid, "account_subject_id": None},
            {**valid, "revision_digests": ()},
            {**valid, "available_source_kinds": ()},
            {**valid, "structured_redacted_summary": {}},
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                result = self.client.route(raw_request=payload)
                self.assertEqual(ContinuationMode.HALT, result.mode)
                self.assertEqual(RouterServiceErrorCode.ROUTER_INPUT_INVALID, result.error_code)
        self.assertEqual(0, self.service.request_count)

    def test_denied_entitlement_and_service_failure_do_not_open_context_or_fallback_locally(self) -> None:
        denied_client = PrivateRouterClient(
            service=FakePrivateRouterService(
                profile=build_router_poc_profile(),
                entitlement_provider=FakeEntitlementProvider(grants=()),
            )
        )
        request = self.request_for(
            stage=ProcessStage.INTAKE,
            event=RouterEventKind.INTAKE,
            event_id="evt_00000000000000000000000000000021",
            source_kinds=(ArtifactKind.PROJECT_GOAL,),
        )
        denied = denied_client.route(raw_request=request.model_dump())
        self.assertEqual(ContinuationMode.HALT, denied.mode)
        self.assertEqual(RouterServiceErrorCode.ROUTER_ENTITLEMENT_DENIED, denied.error_code)

        source = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="local-goal",
            uri="project://local/goal",
            revision="1",
        )
        resolver = ContextResolver(
            source_gateway=InMemorySourceGateway(
                snippets=(SourceSnippet(source=source, span="goal", text="local-only sentinel"),)
            )
        )
        with self.assertRaises(PermissionError):
            LocalContextGate().resolve(
                plan=denied,
                resolver=resolver,
                event_id="evt_00000000000000000000000000000021",
                required_sources=(source,),
                target_artifact=source,
                consumer=ConsumerFingerprint(
                    agent_profile="local-test",
                    profile_version="1",
                    worktree_id="test-worktree",
                    execution_id="test-execution",
                ),
            )

        unavailable = PrivateRouterClient(service=RaisingService()).route(raw_request=request.model_dump())
        self.assertEqual(ContinuationMode.HALT, unavailable.mode)
        self.assertEqual(RouterServiceErrorCode.ROUTER_SERVICE_UNAVAILABLE, unavailable.error_code)

    def test_response_correlation_is_exact_retry_stable_and_has_no_source_sentinel(self) -> None:
        request = self.request_for(
            stage=ProcessStage.INTAKE,
            event=RouterEventKind.INTAKE,
            event_id="evt_00000000000000000000000000000031",
            source_kinds=(ArtifactKind.PROJECT_GOAL,),
        )
        first = self.client.route(raw_request=request.model_dump())
        retry = self.client.route(raw_request=request.model_dump())
        next_event = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.INTAKE,
                event=RouterEventKind.INTAKE,
                event_id="evt_00000000000000000000000000000032",
                source_kinds=(ArtifactKind.PROJECT_GOAL,),
            ).model_dump()
        )

        self.assertIsNotNone(first.response)
        self.assertIsNotNone(retry.response)
        self.assertIsNotNone(next_event.response)
        assert first.response is not None
        assert retry.response is not None
        assert next_event.response is not None
        self.assertEqual(first.response.decision_id, retry.response.decision_id)
        self.assertNotEqual(first.response.decision_id, next_event.response.decision_id)
        serialized = self.service.captured_requests_json()
        self.assertNotIn("local-only sentinel", serialized)
        self.assertNotIn("project://", serialized)
        self.assertNotIn("prompt", serialized)

    def test_malformed_ids_and_response_replay_or_mismatch_fail_closed(self) -> None:
        valid = self.request_for(
            stage=ProcessStage.INTAKE,
            event=RouterEventKind.INTAKE,
            event_id="evt_00000000000000000000000000000035",
            source_kinds=(ArtifactKind.PROJECT_GOAL,),
        ).model_dump()
        malformed = self.client.route(
            raw_request={**valid, "event_correlation_id": "evt_not-an-opaque-id"}
        )
        self.assertEqual(RouterServiceErrorCode.ROUTER_INPUT_INVALID, malformed.error_code)

        mismatch = PrivateRouterClient(service=MismatchedResponseService()).route(raw_request=valid)
        self.assertEqual(ContinuationMode.HALT, mismatch.mode)
        self.assertEqual(RouterServiceErrorCode.ROUTER_RESPONSE_INVALID, mismatch.error_code)

    def test_context_gate_allows_only_a_valid_automatic_plan_and_honours_its_budget(self) -> None:
        request = self.request_for(
            stage=ProcessStage.INTAKE,
            event=RouterEventKind.INTAKE,
            event_id="evt_00000000000000000000000000000041",
            source_kinds=(ArtifactKind.PROJECT_GOAL,),
        )
        plan = self.client.route(raw_request=request.model_dump())
        source = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="local-goal",
            uri="project://local/goal",
            revision="1",
        )
        resolved = LocalContextGate().resolve(
            plan=plan,
            resolver=ContextResolver(
                source_gateway=InMemorySourceGateway(
                    snippets=(SourceSnippet(source=source, span="goal", text="minimal local source"),)
                )
            ),
            event_id="evt_00000000000000000000000000000041",
            required_sources=(source,),
            target_artifact=source,
            consumer=ConsumerFingerprint(
                agent_profile="local-test",
                profile_version="1",
                worktree_id="test-worktree",
                execution_id="test-execution",
            ),
        )
        self.assertEqual(1_000, resolved.view.token_budget)
        self.assertNotIn("minimal local source", resolved.view.model_dump_json())

    def test_ticket_completion_is_an_explicit_human_gate_not_an_unbounded_suspend(self) -> None:
        ticket_wait = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.TICKETS,
                event=RouterEventKind.ACTION_COMPLETED,
                event_id="evt_00000000000000000000000000000045",
                source_kinds=(ArtifactKind.TICKET,),
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.WAIT_FOR_HUMAN, ticket_wait.mode)
        self.assertEqual(ProductActionLabel.REQUEST_APPROVAL, ticket_wait.action_label)
        self.assertIsNone(ticket_wait.error_code)

    def test_ticket_approval_requires_metadata_handoff_on_the_indirect_client_path(self) -> None:
        bare = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.TICKETS,
                event=RouterEventKind.APPROVAL_GRANTED,
                event_id="evt_00000000000000000000000000000049",
                source_kinds=(ArtifactKind.TICKET,),
                authority_state=AuthorityState.APPROVED,
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.HALT, bare.mode)
        self.assertEqual(RouterServiceErrorCode.ROUTER_POLICY_BLOCKED, bare.error_code)
        self.assertEqual((), bare.required_source_kinds)

        handoff = ImplementationHandoff(
            ticket_reference="ticket-workflow-governance-01",
            approved_spec_reference="spec-workflow-governance-01",
            context_references=(
                HandoffArtifactReference(
                    artifact_id="context-workflow-governance",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-ticket-handoff",
                    side_context_id="scx-ticket-handoff-02",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-01",
                        execution_fingerprint="execution-handoff-02",
                    ),
                ),
            ),
            acceptance_references=("acceptance-ticket-handoff-01",),
            tdd_references=("tdd-ticket-handoff-01",),
            scope=TicketScope.NON_FRONTEND,
            non_frontend_reason="router policy has no formal UI boundary",
            control_owner_id="actor-controlplane-01",
            implementation_owner_id="actor-implementation-01",
            reviewer_id="actor-reviewer-01",
        )
        granted = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.TICKETS,
                event=RouterEventKind.APPROVAL_GRANTED,
                event_id="evt_00000000000000000000000000000050",
                source_kinds=(ArtifactKind.TICKET,),
                authority_state=AuthorityState.APPROVED,
                implementation_handoff=handoff,
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.HALT, granted.mode)
        self.assertEqual(RouterServiceErrorCode.ROUTER_POLICY_BLOCKED, granted.error_code)
        self.assertIsNone(granted.action_label)
        self.assertEqual((), granted.required_source_kinds)

        malformed_frontend = handoff.model_dump()
        malformed_frontend.update(
            {
                "scope": TicketScope.FRONTEND,
                "non_frontend_reason": None,
                "frontend_composition": {
                    "component_boundaries": "screen composes approval components",
                    "dependency_scope": "screen-scoped injected ports",
                    "injected_interfaces": ("router-client-port",),
                    "production_bindings": "production client binding",
                    "test_doubles": "fake client",
                    "state_acceptance": "loading and error are asserted",
                },
            }
        )
        with self.assertRaises(ValidationError):
            RouterRequestEnvelope.model_validate(
                {
                    **self.request_for(
                        stage=ProcessStage.TICKETS,
                        event=RouterEventKind.APPROVAL_GRANTED,
                        event_id="evt_00000000000000000000000000000051",
                        source_kinds=(ArtifactKind.TICKET,),
                        authority_state=AuthorityState.APPROVED,
                    ).model_dump(),
                    "implementation_handoff": malformed_frontend,
                }
            )
        with self.assertRaises(ValidationError):
            self.request_for(
                stage=ProcessStage.SPEC,
                event=RouterEventKind.APPROVAL_GRANTED,
                event_id="evt_00000000000000000000000000000052",
                source_kinds=(ArtifactKind.SPEC,),
                authority_state=AuthorityState.APPROVED,
                implementation_handoff=handoff,
            )

    def test_completion_evidence_re_routes_once_and_implementation_return_change_reenters_grill(self) -> None:
        completion = CompletionEvidence(
            completion_id="cmp-doc-00000002",
            action_kind=CompletionActionKind.DOCUMENTATION,
            artifact_references=(
                HandoffArtifactReference(
                    artifact_id="architecture-router-poc",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-architecture-summary",
                    side_context_id="scx-architecture-0002",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-01",
                        execution_fingerprint="execution-0002",
                    ),
                ),
            ),
            verification_references=("verification-completion-01",),
            evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            commit_digest="git_0123456789abcdef",
        )
        completed = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.ARCHITECTURE,
                event=RouterEventKind.ACTION_COMPLETED,
                event_id="evt_00000000000000000000000000000046",
                source_kinds=(ArtifactKind.ARCHITECTURE,),
                completion_evidence=completion,
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.AUTO_RUN, completed.mode)
        self.assertEqual(ProductActionLabel.CONFIRM_ASSUMPTIONS, completed.action_label)

        return_event = ImplementationReturn(
            ticket_reference="ticket-workflow-governance-01",
            status=ImplementationReturnStatus.CHANGE_DETECTED,
            evidence_references=("evidence-change-01",),
            verification_references=("verification-change-01",),
            evidence_digest=completion.evidence_digest,
            emitted_event=RouterEventKind.REQUIREMENT_CHANGED,
        )
        changed = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.IMPLEMENT,
                event=RouterEventKind.REQUIREMENT_CHANGED,
                event_id="evt_00000000000000000000000000000047",
                source_kinds=(ArtifactKind.CHANGE,),
                implementation_return=return_event,
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.AUTO_RUN, changed.mode)
        self.assertEqual(ProductActionLabel.CONFIRM_ASSUMPTIONS, changed.action_label)

        blocked_return = return_event.model_copy(
            update={
                "status": ImplementationReturnStatus.BLOCKED,
                "emitted_event": RouterEventKind.ACTION_COMPLETED,
            }
        )
        blocked = self.client.route(
            raw_request=self.request_for(
                stage=ProcessStage.IMPLEMENT,
                event=RouterEventKind.ACTION_COMPLETED,
                event_id="evt_00000000000000000000000000000048",
                source_kinds=(ArtifactKind.TICKET,),
                implementation_return=blocked_return,
            ).model_dump()
        )
        self.assertEqual(ContinuationMode.HALT, blocked.mode)
        self.assertEqual(RouterServiceErrorCode.ROUTER_POLICY_BLOCKED, blocked.error_code)

    def request_for(
        self,
        *,
        stage: ProcessStage,
        event: RouterEventKind,
        event_id: str,
        source_kinds: tuple[ArtifactKind, ...],
        authority_state: AuthorityState = AuthorityState.NOT_REQUIRED,
        completion_evidence: CompletionEvidence | None = None,
        implementation_return: ImplementationReturn | None = None,
        implementation_handoff: ImplementationHandoff | None = None,
    ) -> RouterRequestEnvelope:
        return RouterRequestEnvelope(
            request_id=f"req_{event_id.removeprefix('evt_')}",
            account_subject_id=self.account_subject_id,
            opaque_project_id=self.project_id,
            project_entry_mode="new_project",
            entitlement_mode=EntitlementMode.FIRST_PROJECT_FREE,
            workflow_stage=stage,
            authority_state=authority_state,
            delivery_stage=DeliveryStage.POC,
            router_event_kind=event,
            event_correlation_id=event_id,
            available_source_kinds=source_kinds,
            revision_digests=(
                "rev_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            ),
            structured_redacted_summary=RedactedSummary(
                evidence_codes=("goal_captured",),
                risk_codes=(),
                source_count_bucket=1,
            ),
            client_version="v1",
            completion_evidence=completion_evidence,
            implementation_return=implementation_return,
            implementation_handoff=implementation_handoff,
        )


class ScriptedExecutor:
    """A test-only local executor that supplies the next locally-normalised event."""

    def __init__(self, *, requests: tuple[RouterRequestEnvelope, ...]) -> None:
        self._requests = list(requests)

    def execute(self, *, action_label: ProductActionLabel) -> RouterRequestEnvelope:
        if not self._requests:
            raise AssertionError(f"unexpected automatic action: {action_label.value}")
        return self._requests.pop(0)


class RaisingService:
    """A deliberately failing remote boundary used to prove no local fallback exists."""

    def decide(self, request: RouterRequestEnvelope) -> object:
        raise TimeoutError("private service unavailable")


class MismatchedResponseService:
    """Returns a syntactically valid but correlation-mismatched response."""

    def decide(self, request: RouterRequestEnvelope) -> object:
        return RouterResponseEnvelope(
            request_id="req_ffffffffffffffffffffffffffffffff",
            decision_id="dec_ffffffffffffffffffffffffffffffff",
            outcome=RouterOutcome.ADVANCE,
            continuation=ContinuationDirective.AUTO_CONTINUE,
            next_stage=ProcessStage.WAYFINDER,
            action_label=ProductActionLabel.DEFINE_STARTING_POINT,
            allowed_action_labels=(ProductActionLabel.DEFINE_STARTING_POINT,),
            required_source_kinds=(ArtifactKind.PROJECT_GOAL,),
            context_budget=1_000,
        )


if __name__ == "__main__":
    unittest.main()
