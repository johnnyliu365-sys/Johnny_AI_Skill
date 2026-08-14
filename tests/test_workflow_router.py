"""Acceptance tests for the reusable, profile-driven workflow router."""

from __future__ import annotations

import ast
import hashlib
import subprocess
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.workflow_router import (
    ArtifactKind,
    ArtifactRef,
    AgentUsage,
    AuthorityState,
    CitationLedger,
    CompletionActionKind,
    CompletionEvidence,
    ContinuationDirective,
    ConsumerFingerprint,
    ContextResolver,
    ContextUsageRecord,
    ContextUsageValidator,
    DeliveryStage,
    ExpectedReturnContract,
    FrontendCompositionContract,
    HandoffArtifactReference,
    HandoffConsumerFingerprint,
    HumanWaitReason,
    InMemorySourceGateway,
    ImplementationHandoff,
    ImplementationReturn,
    ImplementationReturnStatus,
    JsonlContextUsageStore,
    ProcessStage,
    ReferenceStatus,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    ReturnContractKind,
    SkillReference,
    RunAcceptance,
    SourceSnippet,
    TicketScope,
    build_router_graph,
    build_router_poc_profile,
)
from library.workflow_router.graph import RouterGraphState
from library.workflow_router.contracts import RouterDecision
from library.workflow_router.profile import ProjectWorkflowProfile, TransitionRule
from library.workflow_router.telemetry_cli import main as telemetry_main


@dataclass(frozen=True)
class _ExpectedRoute:
    current_stage: ProcessStage
    input_event: RouterEventKind
    reference_id: str
    return_kind: ReturnContractKind
    router_events: tuple[RouterEventKind, ...]
    implementation_statuses: tuple[ImplementationReturnStatus, ...]


@dataclass(frozen=True)
class _ExpectedPolicy:
    reference_id: str
    source_revision: str
    content_digest: str
    relative_path: str


_EXPECTED_ROUTES = (
    _ExpectedRoute(
        ProcessStage.INTAKE,
        RouterEventKind.INTAKE,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.WAYFINDER_GO, RouterEventKind.WAYFINDER_NO_GO),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.WAYFINDER,
        RouterEventKind.WAYFINDER_GO,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.WAYFINDER,
        RouterEventKind.WAYFINDER_NO_GO,
        "router-control",
        ReturnContractKind.NO_RETURN,
        (),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.ARCHITECTURE,
        RouterEventKind.ACTION_COMPLETED,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.GRILL,
        RouterEventKind.ACTION_COMPLETED,
        "context-routing",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.CONTEXT,
        RouterEventKind.ACTION_COMPLETED,
        "specification-ticketing",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.SPEC,
        RouterEventKind.ACTION_COMPLETED,
        "specification-ticketing",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.APPROVAL_GRANTED, RouterEventKind.APPROVAL_DENIED),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.SPEC,
        RouterEventKind.APPROVAL_GRANTED,
        "specification-ticketing",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.TICKET_DISPATCH_REQUIRED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.TICKETS,
        RouterEventKind.TICKET_DISPATCH_REQUIRED,
        "implementation-authority",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.TICKETS,
        RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.IMPLEMENT,
        RouterEventKind.IMPLEMENTATION_RETURNED,
        "implementation-tdd",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.VALIDATION_PASSED, RouterEventKind.VALIDATION_FAILED),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.GRILL,
        RouterEventKind.INTEGRATION_COMPLETED,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.GRILL,
        RouterEventKind.AUDIT_COMPLETED,
        "review-checks",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.IMPLEMENT,
        RouterEventKind.ACTION_COMPLETED,
        "implementation-tdd",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.VALIDATION_PASSED, RouterEventKind.VALIDATION_FAILED),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.SMOKE_TEST,
        RouterEventKind.VALIDATION_PASSED,
        "review-checks",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.SMOKE_TEST,
        RouterEventKind.VALIDATION_FAILED,
        "implementation-tdd",
        ReturnContractKind.IMPLEMENTATION_RETURN,
        (),
        (
            ImplementationReturnStatus.COMPLETED,
            ImplementationReturnStatus.BLOCKED,
            ImplementationReturnStatus.CHANGE_DETECTED,
        ),
    ),
    _ExpectedRoute(
        ProcessStage.REVIEW,
        RouterEventKind.ACTION_COMPLETED,
        "review-checks",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.HANDOFF,
        RouterEventKind.ACTION_COMPLETED,
        "router-control",
        ReturnContractKind.NO_RETURN,
        (),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.IMPLEMENT,
        RouterEventKind.REQUIREMENT_CHANGED,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.ACTION_COMPLETED,),
        (),
    ),
)


_EXPECTED_POLICIES = (
    _ExpectedPolicy(
        "router-control",
        "rev-23dd53ad68e5562f",
        "sha256_23dd53ad68e5562f39a35f06f9c21a970b6eb94eab3aeeae468cc8b5cd68b091",
        "skills/johnny-project-takeover/references/router-control.md",
    ),
    _ExpectedPolicy(
        "discovery-change",
        "rev-5d432a8246bce4ed",
        "sha256_5d432a8246bce4ed890289e24c50e2e29360df165eeb7f9355cb02228e1d10ef",
        "skills/johnny-project-takeover/references/discovery-change.md",
    ),
    _ExpectedPolicy(
        "context-routing",
        "rev-5f1e7958c70c8493",
        "sha256_5f1e7958c70c8493de83aa1481e0f3f3e59c5a40e745a12077eb372fa6e0815e",
        "skills/johnny-project-takeover/references/context-routing.md",
    ),
    _ExpectedPolicy(
        "specification-ticketing",
        "rev-c7011f440caa3ec8",
        "sha256_c7011f440caa3ec8fe83e119a110aa368ec4cc130cf71671d0199987140c8af7",
        "skills/johnny-project-takeover/references/specification-ticketing.md",
    ),
    _ExpectedPolicy(
        "implementation-authority",
        "rev-855117ed19c9c952",
        "sha256_855117ed19c9c952f8903bc56ce070d2cf3805fb51d7a450c46bbf8a00480f50",
        "skills/johnny-project-takeover/references/implementation-authority.md",
    ),
    _ExpectedPolicy(
        "implementation-tdd",
        "rev-38408006f23df3b6",
        "sha256_38408006f23df3b66a4368e2b8794cc099b84ea20417e56d881ff19512345574",
        "skills/johnny-project-takeover/references/implementation-tdd.md",
    ),
    _ExpectedPolicy(
        "review-checks",
        "rev-4b8527305609194a",
        "sha256_4b8527305609194ae9dd26c16a05ff72d22b1f20a8cb925175d6793766bb5f54",
        "skills/johnny-project-takeover/references/review-checks.md",
    ),
)


class WorkflowRouterTests(unittest.TestCase):
    """Keep the POC closed, strongly typed, and free of shared raw context."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.engine = RouterEngine()
        self.goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-framework-goal",
            uri="project://router-framework/goal",
            revision="1",
        )
        self.wayfinder_output = ArtifactRef(
            kind=ArtifactKind.WAYFINDER_OUTPUT,
            identifier="wayfinder-router-poc",
            uri="context://router-framework/wayfinder",
            revision="1",
        )

    def test_intake_and_go_have_only_the_profile_declared_next_stage(self) -> None:
        intake_state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.INTAKE,
            authority_state=AuthorityState.NOT_REQUIRED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.goal,),
        )
        intake = self.engine.decide(
            state=intake_state,
            event=RouterEvent(event_id="evt-intake-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, intake.outcome)
        self.assertEqual(ProcessStage.WAYFINDER, intake.next_stage)

        go_state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.WAYFINDER,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.wayfinder_output,),
        )
        go = self.engine.decide(
            state=go_state,
            event=RouterEvent(event_id="evt-go-001", kind=RouterEventKind.WAYFINDER_GO),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, go.outcome)
        self.assertEqual(ProcessStage.ARCHITECTURE, go.next_stage)

    def test_human_approval_wait_and_no_go_are_explicit(self) -> None:
        specification = ArtifactRef(
            kind=ArtifactKind.SPEC,
            identifier="SPEC-ROUTER-POC-001",
            uri="spec://router-framework/poc-001",
            revision="1",
        )
        pending_state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.SPEC,
            authority_state=AuthorityState.PENDING,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(specification,),
        )
        suspended = self.engine.decide(
            state=pending_state,
            event=RouterEvent(event_id="evt-spec-pending", kind=RouterEventKind.ACTION_COMPLETED),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, suspended.outcome)
        self.assertIsNone(suspended.next_stage)
        self.assertEqual("wait_for_human", suspended.continuation.value)
        self.assertEqual(HumanWaitReason.SPECIFICATION_APPROVAL_REQUIRED, suspended.wait_reason)

        no_go = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.WAYFINDER,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(self.wayfinder_output,),
            ),
            event=RouterEvent(event_id="evt-no-go-001", kind=RouterEventKind.WAYFINDER_NO_GO),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.STOP, no_go.outcome)
        self.assertEqual(ProcessStage.STOPPED, no_go.next_stage)

    def test_completion_evidence_and_implementation_handoff_are_typed_and_fail_closed(self) -> None:
        architecture = ArtifactRef(
            kind=ArtifactKind.ARCHITECTURE,
            identifier="router-poc-architecture",
            uri="architecture://router-framework/poc",
            revision="1",
        )
        evidence = CompletionEvidence(
            completion_id="cmp-doc-00000001",
            action_kind=CompletionActionKind.DOCUMENTATION,
            artifact_references=(
                HandoffArtifactReference(
                    artifact_id="architecture-router-poc",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-architecture-summary",
                    side_context_id="scx-architecture-0001",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-01",
                        execution_fingerprint="execution-0001",
                    ),
                ),
            ),
            verification_references=("verification-router-green-01",),
            evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            commit_digest="git_0123456789abcdef",
        )
        decision = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.ARCHITECTURE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(architecture,),
            ),
            event=RouterEvent(
                event_id="evt-completion-001",
                kind=RouterEventKind.ACTION_COMPLETED,
                completion_evidence=evidence,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, decision.outcome)
        self.assertEqual(ProcessStage.GRILL, decision.next_stage)

        handoff = ImplementationHandoff(
            handoff_reference="handoff-workflow-governance-01",
            ticket_reference="ticket-workflow-governance-01",
            approved_spec_reference="spec-workflow-governance-01",
            expected_main_revision="rev-0123456789abcdef",
            context_references=evidence.artifact_references,
            acceptance_references=("acceptance-ac-01",),
            tdd_references=("tdd-cut-normal-continuation",),
            scope=TicketScope.NON_FRONTEND,
            non_frontend_reason="router policy has no formal UI boundary",
            control_owner_id="actor-controlplane-01",
            implementation_owner_id="actor-implementation-01",
            reviewer_id="actor-reviewer-01",
        )
        self.assertEqual(TicketScope.NON_FRONTEND, handoff.scope)
        change_return = ImplementationReturn(
            ticket_reference=handoff.ticket_reference,
            status=ImplementationReturnStatus.CHANGE_DETECTED,
            evidence_references=("evidence-contract-change-01",),
            verification_references=("verification-contract-change-01",),
            evidence_digest=evidence.evidence_digest,
            emitted_event=RouterEventKind.REQUIREMENT_CHANGED,
        )
        self.assertEqual(RouterEventKind.REQUIREMENT_CHANGED, change_return.emitted_event)

        with self.assertRaises(ValidationError):
            CompletionEvidence(
                completion_id="",
                action_kind=CompletionActionKind.DOCUMENTATION,
                artifact_references=(),
                verification_references=(),
                evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            )
        with self.assertRaises(ValidationError):
            HandoffArtifactReference(
                artifact_id="context://raw-source-must-not-transfer",
                revision_digest="rev-0123456789abcdef",
                source_span_id="span-source",
                side_context_id="scx-source-0001",
                consumer_fingerprint=evidence.artifact_references[0].consumer_fingerprint,
            )
        with self.assertRaises(ValidationError):
            ImplementationHandoff(
                handoff_reference="handoff-frontend-invalid-01",
                ticket_reference="ticket-workflow-governance-01",
                approved_spec_reference="spec-workflow-governance-01",
                expected_main_revision="rev-0123456789abcdef",
                context_references=evidence.artifact_references,
                acceptance_references=("acceptance-ac-01",),
                tdd_references=("tdd-cut-normal-continuation",),
                scope=TicketScope.FRONTEND,
                control_owner_id="actor-same-owner-01",
                implementation_owner_id="actor-same-owner-01",
                reviewer_id="actor-reviewer-01",
            )
        frontend_handoff = ImplementationHandoff(
            handoff_reference="handoff-frontend-contract-01",
            ticket_reference="ticket-frontend-contract-01",
            approved_spec_reference="spec-frontend-contract-01",
            expected_main_revision="rev-0123456789abcdef",
            context_references=evidence.artifact_references,
            acceptance_references=("acceptance-frontend-01",),
            tdd_references=("tdd-frontend-01",),
            scope=TicketScope.FRONTEND,
            frontend_composition=FrontendCompositionContract(
                component_boundaries="screen composes status panel and approval action",
                composition_root_reference="composition-root-router-ui",
                dependency_scope="screen-scoped injected ports",
                injected_interfaces=("router-client-port", "clock-port"),
                production_bindings="production-router-client binding",
                test_doubles="fake-router-client and fake-clock",
                state_acceptance="loading empty error permission and accessibility states are asserted",
            ),
            control_owner_id="actor-controlplane-01",
            implementation_owner_id="actor-implementation-01",
            reviewer_id="actor-reviewer-01",
        )
        self.assertIsNotNone(frontend_handoff.frontend_composition)

    def test_requirement_change_from_implementation_routes_back_to_grill(self) -> None:
        change = ArtifactRef(
            kind=ArtifactKind.CHANGE,
            identifier="CHG-ROUTER-RETURN-001",
            uri="change://router-framework/return-001",
            revision="1",
        )
        decision = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.IMPLEMENT,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(change,),
            ),
            event=RouterEvent(
                event_id="evt-change-return-001",
                kind=RouterEventKind.REQUIREMENT_CHANGED,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, decision.outcome)
        self.assertEqual(ProcessStage.GRILL, decision.next_stage)

    def test_blocked_implementation_return_halts_the_direct_router_entrypoint(self) -> None:
        ticket = ArtifactRef(
            kind=ArtifactKind.TICKET,
            identifier="workflow-governance-ticket-01",
            uri="ticket://workflow-governance/01",
            revision="1",
        )
        blocked_return = ImplementationReturn(
            ticket_reference="ticket-workflow-governance-01",
            status=ImplementationReturnStatus.BLOCKED,
            evidence_references=("evidence-implementation-blocked-01",),
            verification_references=("verification-implementation-blocked-01",),
            evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            emitted_event=RouterEventKind.ACTION_COMPLETED,
        )

        decision = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.IMPLEMENT,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(ticket,),
            ),
            event=RouterEvent(
                event_id="evt-implementation-blocked-001",
                kind=RouterEventKind.ACTION_COMPLETED,
                implementation_return=blocked_return,
            ),
            profile=self.profile,
        )

        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual("halt", decision.continuation.value)
        self.assertIsNone(decision.next_stage)
        self.assertEqual((), decision.required_sources)
        self.assertEqual((), decision.eligible_capabilities)
        self.assertIsNone(decision.context_view)
        self.assertEqual("implementation_return_blocked", decision.blockers[0].code.value)

    def test_ticket_approval_requires_a_valid_handoff_at_the_direct_router_entrypoint(self) -> None:
        ticket = ArtifactRef(
            kind=ArtifactKind.TICKET,
            identifier="workflow-governance-ticket-01",
            uri="ticket://workflow-governance/01",
            revision="1",
        )
        state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.TICKETS,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(ticket,),
        )
        bare = self.engine.decide(
            state=state,
            event=RouterEvent(
                event_id="evt-ticket-approval-bare-001",
                kind=RouterEventKind.APPROVAL_GRANTED,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, bare.outcome)
        self.assertEqual("halt", bare.continuation.value)
        self.assertIsNone(bare.next_stage)
        self.assertEqual((), bare.required_sources)
        self.assertEqual((), bare.eligible_capabilities)
        self.assertIsNone(bare.context_view)
        self.assertEqual("legacy_ticket_approval_blocked", bare.blockers[0].code.value)

        handoff = ImplementationHandoff(
            handoff_reference="handoff-workflow-governance-approval-01",
            ticket_reference="ticket-workflow-governance-01",
            approved_spec_reference="spec-workflow-governance-01",
            expected_main_revision="rev-0123456789abcdef",
            context_references=(
                HandoffArtifactReference(
                    artifact_id="context-workflow-governance",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-ticket-handoff",
                    side_context_id="scx-ticket-handoff-01",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-01",
                        execution_fingerprint="execution-handoff-01",
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
        granted = self.engine.decide(
            state=state,
            event=RouterEvent(
                event_id="evt-ticket-approval-handoff-001",
                kind=RouterEventKind.APPROVAL_GRANTED,
                implementation_handoff=handoff,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, granted.outcome)
        self.assertEqual("halt", granted.continuation.value)
        self.assertIsNone(granted.next_stage)
        self.assertEqual("legacy_ticket_approval_blocked", granted.blockers[0].code.value)

        specification = ArtifactRef(
            kind=ArtifactKind.SPEC,
            identifier="workflow-governance-spec-01",
            uri="spec://workflow-governance/01",
            revision="1",
        )
        undeclared = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.SPEC,
                authority_state=AuthorityState.APPROVED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(specification,),
            ),
            event=RouterEvent(
                event_id="evt-specification-approval-handoff-001",
                kind=RouterEventKind.APPROVAL_GRANTED,
                implementation_handoff=handoff,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, undeclared.outcome)
        self.assertEqual("halt", undeclared.continuation.value)
        self.assertEqual("implementation_handoff_undeclared", undeclared.blockers[0].code.value)

        with self.assertRaisesRegex(ValidationError, "cannot share an event"):
            RouterEvent(
                event_id="evt-ticket-approval-conflict-001",
                kind=RouterEventKind.APPROVAL_GRANTED,
                implementation_handoff=handoff,
                implementation_return=ImplementationReturn(
                    ticket_reference=handoff.ticket_reference,
                    status=ImplementationReturnStatus.COMPLETED,
                    evidence_references=("evidence-handoff-conflict-01",),
                    verification_references=("verification-handoff-conflict-01",),
                    evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                    emitted_event=RouterEventKind.ACTION_COMPLETED,
                ),
            )

        frontend_payload = handoff.model_dump()
        frontend_payload.update(
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
            ImplementationHandoff.model_validate(frontend_payload)
        with self.assertRaises(ValidationError):
            ImplementationHandoff.model_validate(
                {**handoff.model_dump(), "implementation_owner_id": handoff.control_owner_id}
            )

    def test_legacy_action_completed_rule_routes_without_new_evidence_but_rejects_it_when_undeclared(self) -> None:
        legacy_profile = ProjectWorkflowProfile(
            profile_id="legacy-router-profile",
            profile_version="1",
            delivery_stage=DeliveryStage.POC,
            router_control_reference=SkillReference(
                reference_id="router-control",
                source_revision="rev-5d432a8246bce4ed",
                content_digest="sha256_5d432a8246bce4ed890289e24c50e2e29360df165eeb7f9355cb02228e1d10ef",
            ),
            halt_return_contract=ExpectedReturnContract(
                contract_id="router-control-no-return",
                contract_revision="rev-5d432a8246bce4ed",
                return_kind=ReturnContractKind.NO_RETURN,
                router_events=(),
                implementation_statuses=(),
            ),
            transition_rules=(
                TransitionRule(
                    skill_reference=SkillReference(
                        reference_id="legacy-route-architecture-action-completed",
                        source_revision="rev-5d432a8246bce4ed",
                        content_digest="sha256_5d432a8246bce4ed890289e24c50e2e29360df165eeb7f9355cb02228e1d10ef",
                    ),
                    expected_return=ExpectedReturnContract(
                        contract_id="return-action-completed",
                        contract_revision="rev-5d432a8246bce4ed",
                        return_kind=ReturnContractKind.ROUTER_EVENT,
                        router_events=(RouterEventKind.ACTION_COMPLETED,),
                        implementation_statuses=(),
                    ),
                    current_stage=ProcessStage.ARCHITECTURE,
                    event_kind=RouterEventKind.ACTION_COMPLETED,
                    outcome=RouterOutcome.ADVANCE,
                    next_stage=ProcessStage.GRILL,
                    required_source_kinds=(ArtifactKind.ARCHITECTURE,),
                ),
            ),
        )
        architecture = ArtifactRef(
            kind=ArtifactKind.ARCHITECTURE,
            identifier="legacy-architecture",
            uri="architecture://legacy/poc",
            revision="1",
        )
        state = RouterState(
            project_id="legacy-router-poc",
            stage=ProcessStage.ARCHITECTURE,
            authority_state=AuthorityState.NOT_REQUIRED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(architecture,),
        )
        legacy = self.engine.decide(
            state=state,
            event=RouterEvent(
                event_id="evt-legacy-action-completed-001",
                kind=RouterEventKind.ACTION_COMPLETED,
            ),
            profile=legacy_profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, legacy.outcome)
        self.assertEqual(ProcessStage.GRILL, legacy.next_stage)

        completion_evidence = CompletionEvidence(
            completion_id="cmp-doc-legacy-0001",
            action_kind=CompletionActionKind.DOCUMENTATION,
            artifact_references=(
                HandoffArtifactReference(
                    artifact_id="architecture-legacy-poc",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="span-architecture-summary",
                    side_context_id="scx-architecture-legacy-01",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="agent-control-plane-v1",
                        profile_version="profile-v1",
                        worktree_fingerprint="worktree-control-01",
                        execution_fingerprint="execution-legacy-01",
                    ),
                ),
            ),
            verification_references=("verification-legacy-action-01",),
            evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )
        rejected = self.engine.decide(
            state=state,
            event=RouterEvent(
                event_id="evt-legacy-action-completed-002",
                kind=RouterEventKind.ACTION_COMPLETED,
                completion_evidence=completion_evidence,
            ),
            profile=legacy_profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, rejected.outcome)
        self.assertEqual("halt", rejected.continuation.value)
        self.assertEqual("invalid_completion_evidence", rejected.blockers[0].code.value)

    def test_handoff_contracts_reject_locator_and_empty_boundary_inputs(self) -> None:
        consumer = HandoffConsumerFingerprint(
            agent_profile_id="agent-control-plane-v1",
            profile_version="profile-v1",
            worktree_fingerprint="worktree-control-01",
            execution_fingerprint="execution-boundary-01",
        )
        reference = HandoffArtifactReference(
            artifact_id="architecture-router-poc",
            revision_digest="rev-0123456789abcdef",
            source_span_id="span-architecture-summary",
            side_context_id="scx-architecture-boundary-01",
            consumer_fingerprint=consumer,
        )
        reference_payload = reference.model_dump()
        forbidden_locator_forms = (
            "C:/handoff/reference",
            "C:/handoff/reference-x",
            "C:/handoff/reference/",
            "c:/HANDOFF/REFERENCE",
            "C%3A%2Fhandoff%2Freference",
            "../handoff/reference",
            "",
        )
        for source_path in forbidden_locator_forms:
            with self.subTest(source_path=source_path):
                with self.assertRaises(ValidationError):
                    HandoffArtifactReference.model_validate(
                        {**reference_payload, "source_path": source_path}
                    )

        completion = CompletionEvidence(
            completion_id="cmp-doc-boundary-01",
            action_kind=CompletionActionKind.DOCUMENTATION,
            artifact_references=(reference,),
            verification_references=("verification-boundary-01",),
            evidence_digest="sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )
        invalid_boundary_collections: tuple[object, ...] = (None, (), [], {})
        for invalid_id in (None, "", "   "):
            with self.subTest(completion_id=invalid_id):
                with self.assertRaises(ValidationError):
                    CompletionEvidence.model_validate(
                        {**completion.model_dump(), "completion_id": invalid_id}
                    )
        for invalid_collection in invalid_boundary_collections:
            with self.subTest(completion_artifacts=invalid_collection):
                with self.assertRaises(ValidationError):
                    CompletionEvidence.model_validate(
                        {**completion.model_dump(), "artifact_references": invalid_collection}
                    )
            with self.subTest(completion_evidence=invalid_collection):
                with self.assertRaises(ValidationError):
                    CompletionEvidence.model_validate(
                        {**completion.model_dump(), "verification_references": invalid_collection}
                    )

        handoff = ImplementationHandoff(
            handoff_reference="handoff-workflow-governance-boundary-01",
            ticket_reference="ticket-workflow-governance-01",
            approved_spec_reference="spec-workflow-governance-01",
            expected_main_revision="rev-0123456789abcdef",
            context_references=(reference,),
            acceptance_references=("acceptance-boundary-01",),
            tdd_references=("tdd-boundary-01",),
            scope=TicketScope.NON_FRONTEND,
            non_frontend_reason="router policy has no formal UI boundary",
            control_owner_id="actor-controlplane-01",
            implementation_owner_id="actor-implementation-01",
            reviewer_id="actor-reviewer-01",
        )
        for invalid_owner in (None, "", "   "):
            with self.subTest(control_owner_id=invalid_owner):
                with self.assertRaises(ValidationError):
                    ImplementationHandoff.model_validate(
                        {**handoff.model_dump(), "control_owner_id": invalid_owner}
                    )

        implementation_return = ImplementationReturn(
            ticket_reference=handoff.ticket_reference,
            status=ImplementationReturnStatus.COMPLETED,
            evidence_references=("evidence-boundary-01",),
            verification_references=("verification-return-boundary-01",),
            evidence_digest=completion.evidence_digest,
            emitted_event=RouterEventKind.ACTION_COMPLETED,
        )
        for invalid_status in (None, "", "   "):
            with self.subTest(status=invalid_status):
                with self.assertRaises(ValidationError):
                    ImplementationReturn.model_validate(
                        {**implementation_return.model_dump(), "status": invalid_status}
                    )
        for invalid_collection in invalid_boundary_collections:
            with self.subTest(return_evidence=invalid_collection):
                with self.assertRaises(ValidationError):
                    ImplementationReturn.model_validate(
                        {**implementation_return.model_dump(), "evidence_references": invalid_collection}
                    )

    def test_policy_documents_and_templates_keep_completion_and_handoff_contract_in_sync(self) -> None:
        root = Path(__file__).resolve().parents[1]
        required_terms = {
            "Workflow.md": (
                "commit",
                "ACTION_COMPLETED",
                "ImplementationHandoff",
                "ImplementationReturn",
                "WAIT_FOR_HUMAN",
                "HALT",
            ),
            "AGENTS.md": ("#workflow-router", "#role-boundary", "ACTION_COMPLETED"),
            "skills/johnny-project-takeover/SKILL.md": (
                "ACTION_COMPLETED",
                "ImplementationReturn",
                "REQUIREMENT_CHANGED",
            ),
            "modules/tickets/TEMPLATE.md": (
                "ImplementationReturn",
                "Owner override record",
                "N/A reason",
                "Composition Root",
            ),
            "modules/spec/TEMPLATE.md": (
                "ImplementationHandoff",
                "ImplementationReturn",
                "Composition Root",
            ),
        }
        for relative_path, terms in required_terms.items():
            with self.subTest(path=relative_path):
                document = (root / relative_path).read_text(encoding="utf-8")
                for term in terms:
                    with self.subTest(term=term):
                        self.assertIn(term, document)

    def test_delivery_stage_must_match_the_approved_profile(self) -> None:
        decision = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.MVP,
                artifact_refs=(self.goal,),
            ),
            event=RouterEvent(event_id="evt-maturity-mismatch-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual("delivery_stage_mismatch", decision.blockers[0].code.value)

    def test_ambiguous_required_source_kind_fails_closed_instead_of_loading_all_matches(self) -> None:
        alternate_goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-framework-goal-alternate",
            uri="project://router-framework/goal-alternate",
            revision="1",
        )
        decision = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(self.goal, alternate_goal),
            ),
            event=RouterEvent(event_id="evt-ambiguous-source-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual("ambiguous_required_source", decision.blockers[0].code.value)

    def test_each_new_reference_has_a_new_id_but_retry_is_idempotent(self) -> None:
        source = ArtifactRef(
            kind=ArtifactKind.CONTEXT,
            identifier="router-cost-assumption",
            uri="context://router-framework/poc-cost",
            revision="4",
        )
        target = ArtifactRef(
            kind=ArtifactKind.GRILL,
            identifier="GRILL-ROUTER-POC-001",
            uri="grill://router-framework/poc-001",
            revision="1",
        )
        gateway = InMemorySourceGateway(
            snippets=(
                SourceSnippet(source=source, span="poc.cost", text="no paid provider"),
            )
        )
        resolver = ContextResolver(source_gateway=gateway)
        consumer = ConsumerFingerprint(
            agent_profile="architecture",
            profile_version="1",
            worktree_id="worktree-a",
            execution_id="run-001",
        )

        first = resolver.resolve(
            event_id="evt-reference-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=consumer,
        )
        retry = resolver.resolve(
            event_id="evt-reference-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=consumer,
        )
        next_reference = resolver.resolve(
            event_id="evt-reference-002",
            required_sources=(source,),
            target_artifact=target,
            consumer=consumer,
        )
        other_consumer = resolver.resolve(
            event_id="evt-reference-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=ConsumerFingerprint(
                agent_profile="spec",
                profile_version="1",
                worktree_id="worktree-b",
                execution_id="run-003",
            ),
        )
        self.assertEqual(first.view.references[0].side_context_id, retry.view.references[0].side_context_id)
        self.assertNotEqual(first.view.references[0].side_context_id, next_reference.view.references[0].side_context_id)
        self.assertNotEqual(first.view.references[0].side_context_id, other_consumer.view.references[0].side_context_id)
        self.assertEqual("no paid provider", first.packet.snippets[0].text)
        self.assertNotIn("no paid provider", first.view.model_dump_json())

    def test_closed_reference_maps_without_raw_text_and_invalidates_by_revision(self) -> None:
        source = ArtifactRef(
            kind=ArtifactKind.CONTEXT,
            identifier="router-cost-assumption",
            uri="context://router-framework/poc-cost",
            revision="4",
        )
        target = ArtifactRef(
            kind=ArtifactKind.SPEC,
            identifier="SPEC-ROUTER-POC-001",
            uri="spec://router-framework/poc-001",
            revision="1",
        )
        resolved = ContextResolver(
            source_gateway=InMemorySourceGateway(
                snippets=(SourceSnippet(source=source, span="poc.cost", text="private evidence"),)
            )
        ).resolve(
            event_id="evt-close-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=ConsumerFingerprint(
                agent_profile="spec",
                profile_version="1",
                worktree_id="worktree-b",
                execution_id="run-002",
            ),
        )
        ledger = CitationLedger()
        closed = ledger.close(reference=resolved.view.references[0])
        self.assertEqual(ReferenceStatus.CLOSED, closed.status)
        mapped = ledger.references_for_source(source=source)
        self.assertEqual(target, mapped[0].target_artifact)
        self.assertNotIn("private evidence", ledger.model_dump_json())

        invalidated = ledger.invalidate_source(
            source=ArtifactRef(
                kind=source.kind,
                identifier=source.identifier,
                uri=source.uri,
                revision="5",
            )
        )
        self.assertEqual(ReferenceStatus.INVALIDATED, invalidated[0].status)

    def test_langgraph_routes_auto_continue_human_wait_and_failure_separately(self) -> None:
        graph = build_router_graph(engine=self.engine)
        completed = RouterGraphState.model_validate(
            graph.invoke(
                RouterGraphState(
                    router_state=RouterState(
                        project_id="router-framework-poc",
                        stage=ProcessStage.INTAKE,
                        authority_state=AuthorityState.NOT_REQUIRED,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(self.goal,),
                    ),
                    router_event=RouterEvent(event_id="evt-graph-001", kind=RouterEventKind.INTAKE),
                    profile=self.profile,
                )
            )
        )
        assert completed.decision is not None
        self.assertEqual(RouterOutcome.ADVANCE, completed.decision.outcome)
        self.assertEqual("continue", completed.graph_terminal)

        blocked = RouterGraphState.model_validate(
            graph.invoke(
                RouterGraphState(
                    router_state=RouterState(
                        project_id="router-framework-poc",
                        stage=ProcessStage.WAYFINDER,
                        authority_state=AuthorityState.PENDING,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(self.wayfinder_output,),
                    ),
                    router_event=RouterEvent(
                        event_id="evt-graph-002",
                        kind=RouterEventKind.ACTION_COMPLETED,
                    ),
                    profile=self.profile,
                )
            )
        )
        assert blocked.decision is not None
        self.assertEqual(RouterOutcome.SUSPEND, blocked.decision.outcome)
        self.assertEqual("halted", blocked.graph_terminal)

        specification = ArtifactRef(
            kind=ArtifactKind.SPEC,
            identifier="SPEC-ROUTER-POC-001",
            uri="spec://router-framework/poc-001",
            revision="1",
        )
        waiting = RouterGraphState.model_validate(
            graph.invoke(
                RouterGraphState(
                    router_state=RouterState(
                        project_id="router-framework-poc",
                        stage=ProcessStage.SPEC,
                        authority_state=AuthorityState.PENDING,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(specification,),
                    ),
                    router_event=RouterEvent(
                        event_id="evt-graph-003",
                        kind=RouterEventKind.ACTION_COMPLETED,
                    ),
                    profile=self.profile,
                )
            )
        )
        self.assertEqual("waiting", waiting.graph_terminal)

    def test_agents_mcp_and_temporal_adapters_load_without_external_services(self) -> None:
        from library.workflow_router.integrations import (
            AgentCapabilityDefinition,
            McpResourceGateway,
            OpenAICapabilityAdapter,
        )
        from library.workflow_router.temporal_runtime import RouterRoundInput, route_round

        intake = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(self.goal,),
            ),
            event=RouterEvent(event_id="evt-adapter-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        capability = intake.eligible_capabilities[0]
        agent = OpenAICapabilityAdapter(
            definitions=(
                AgentCapabilityDefinition(
                    capability=capability,
                    agent_name="wayfinder-agent",
                    instructions="Use only the supplied ContextView descriptor.",
                ),
            )
        ).resolve(capability=capability)
        self.assertEqual("wayfinder-agent", agent.name)
        self.assertEqual((), tuple(agent.handoffs))
        self.assertEqual("McpResourceGateway", McpResourceGateway.__name__)

        activity_decision = route_round(
            RouterRoundInput(
                router_state=RouterState(
                    project_id="router-framework-poc",
                    stage=ProcessStage.INTAKE,
                    authority_state=AuthorityState.NOT_REQUIRED,
                    delivery_stage=DeliveryStage.POC,
                    artifact_refs=(self.goal,),
                ),
                router_event=RouterEvent(
                    event_id="evt-temporal-activity-001",
                    kind=RouterEventKind.INTAKE,
                ),
                profile=self.profile,
            )
        )
        self.assertEqual(RouterOutcome.ADVANCE, activity_decision.outcome)

    def test_temporal_approval_signal_requires_matching_authority_state(self) -> None:
        from library.workflow_router.temporal_runtime import ApprovalSignal

        granted = ApprovalSignal(
            router_event=RouterEvent(
                event_id="evt-approval-001",
                kind=RouterEventKind.APPROVAL_GRANTED,
            ),
            authority_state=AuthorityState.APPROVED,
        )
        self.assertEqual(AuthorityState.APPROVED, granted.authority_state)
        with self.assertRaises(ValidationError):
            ApprovalSignal(
                router_event=RouterEvent(
                    event_id="evt-approval-002",
                    kind=RouterEventKind.APPROVAL_GRANTED,
                ),
                authority_state=AuthorityState.PENDING,
            )


class ContextLoadTelemetryTests(unittest.TestCase):
    """Verify metadata-only evidence and fail-closed context-load comparisons."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="telemetry-goal",
            uri="project://telemetry/private-goal",
            revision="1",
        )
        self.target = ArtifactRef(
            kind=ArtifactKind.WAYFINDER_OUTPUT,
            identifier="WAYFINDER-TELEMETRY-001",
            uri="context://telemetry/wayfinder",
            revision="1",
        )
        self.state = RouterState(
            project_id="telemetry-poc",
            stage=ProcessStage.INTAKE,
            authority_state=AuthorityState.NOT_REQUIRED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.goal,),
        )
        self.event = RouterEvent(event_id="evt-telemetry-001", kind=RouterEventKind.INTAKE)
        self.decision = RouterEngine().decide(
            state=self.state,
            event=self.event,
            profile=self.profile,
        )
        self.raw_text = "never-persist-this-unique-raw-context"
        self.snippet = SourceSnippet(source=self.goal, span="goal.summary", text=self.raw_text)
        self.resolved = ContextResolver(
            source_gateway=InMemorySourceGateway(snippets=(self.snippet,))
        ).resolve(
            event_id=self.event.event_id,
            required_sources=self.decision.required_sources,
            target_artifact=self.target,
            consumer=ConsumerFingerprint(
                agent_profile="wayfinder",
                profile_version="1",
                worktree_id="telemetry-worktree",
                execution_id="telemetry-run",
            ),
        )
        self.agent = AgentUsage(
            provider="test-provider",
            model="test-model",
            consumer=ConsumerFingerprint(
                agent_profile="wayfinder",
                profile_version="1",
                worktree_id="telemetry-worktree",
                execution_id="telemetry-run",
            ),
            provider_input_tokens=2_000,
            provider_output_tokens=250,
            tool_read_count=1,
            retry_count=0,
            duration_ms=20,
        )

    def test_router_record_round_trips_without_raw_text_or_uri(self) -> None:
        record = ContextUsageRecord.from_router(
            run_id="router-run-001",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        with TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "router-usage.jsonl"
            JsonlContextUsageStore.append(path=log_path, record=record)
            serialized = log_path.read_text(encoding="utf-8")
            restored = JsonlContextUsageStore.read(path=log_path)
        self.assertNotIn(self.raw_text, serialized)
        self.assertNotIn(self.goal.uri, serialized)
        self.assertEqual((record,), restored)
        self.assertFalse(record.context.raw_text_in_shared_state)
        self.assertEqual(1, record.context.actual_source_count)

    def test_matched_baseline_and_router_prove_provider_token_reduction(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-001",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-001",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        report = ContextUsageValidator().validate(records=(baseline, router))
        self.assertTrue(report.evidence_valid)
        self.assertTrue(report.reduction_verified)
        self.assertEqual(5_000, report.median_reduction_basis_points)

    def test_guard_or_usage_failure_rejects_reduction_claim(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-002",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-002",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent.model_copy(update={"provider_input_tokens": None}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        report = ContextUsageValidator().validate(records=(baseline, router))
        self.assertFalse(report.evidence_valid)
        self.assertFalse(report.reduction_verified)

    def test_router_guard_violation_rejects_reduction_claim(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-003",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-003",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        invalid_context = router.context.model_copy(
            update={"undeclared_source_count": router.context.actual_source_count}
        )
        invalid_router = router.model_copy(update={"context": invalid_context})
        report = ContextUsageValidator().validate(records=(baseline, invalid_router))
        self.assertFalse(report.evidence_valid)
        self.assertFalse(report.reduction_verified)
        self.assertEqual("undeclared_source", report.issues[0].code.value)

    def test_budget_breach_is_rejected_before_context_packet_creation(self) -> None:
        oversized_snippet = SourceSnippet(
            source=self.goal,
            span="goal.oversized",
            text="x" * 4_004,
        )
        with self.assertRaisesRegex(ValueError, "exceeds its Router token budget"):
            ContextResolver(
                source_gateway=InMemorySourceGateway(snippets=(oversized_snippet,))
            ).resolve(
                event_id=self.event.event_id,
                required_sources=self.decision.required_sources,
                target_artifact=self.target,
                consumer=self.agent.consumer,
            )

    def test_cli_accepts_only_a_verified_local_jsonl(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-005",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-005",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        with TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "router-usage.jsonl"
            JsonlContextUsageStore.append(path=log_path, record=baseline)
            JsonlContextUsageStore.append(path=log_path, record=router)
            output = StringIO()
            with redirect_stdout(output):
                result = telemetry_main((str(log_path), "--minimum-reduction-bps", "5000"))
        self.assertEqual(0, result)
        self.assertIn('"reduction_verified": true', output.getvalue())

    def test_context_resolver_rejects_mismatched_source_adapter_output(self) -> None:
        other_source = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="other-goal",
            uri="project://telemetry/other-goal",
            revision="1",
        )

        class MismatchedSourceGateway:
            def read(self, source: ArtifactRef) -> SourceSnippet:
                return SourceSnippet(source=other_source, span="wrong", text="wrong source")

        with self.assertRaisesRegex(ValueError, "undeclared source"):
            ContextResolver(source_gateway=MismatchedSourceGateway()).resolve(
                event_id=self.event.event_id,
                required_sources=self.decision.required_sources,
                target_artifact=self.target,
                consumer=self.agent.consumer,
            )


class RouteInstructionContractTests(unittest.TestCase):
    """Exercise the versioned policy reference and finite return contract boundary."""

    _revision = "rev-5d432a8246bce4ed"
    _digest = "sha256_5d432a8246bce4ed890289e24c50e2e29360df165eeb7f9355cb02228e1d10ef"

    def _skill(self, reference_id: str = "route-test-policy") -> SkillReference:
        return SkillReference(
            reference_id=reference_id,
            source_revision=self._revision,
            content_digest=self._digest,
        )

    def _router_contract(self) -> ExpectedReturnContract:
        return ExpectedReturnContract(
            contract_id="return-action-completed",
            contract_revision=self._revision,
            return_kind=ReturnContractKind.ROUTER_EVENT,
            router_events=(RouterEventKind.ACTION_COMPLETED,),
            implementation_statuses=(),
        )

    def _assert_profile_fallback(
        self,
        decision: RouterDecision,
        profile: ProjectWorkflowProfile,
    ) -> None:
        self.assertEqual(profile.router_control_reference, decision.skill_reference)
        self.assertEqual(profile.halt_return_contract, decision.expected_return)

    def test_finite_contracts_round_trip_and_reject_complete_invalid_matrix(self) -> None:
        implementation_contract = ExpectedReturnContract(
            contract_id="return-implementation",
            contract_revision=self._revision,
            return_kind=ReturnContractKind.IMPLEMENTATION_RETURN,
            router_events=(),
            implementation_statuses=(
                ImplementationReturnStatus.COMPLETED,
                ImplementationReturnStatus.CHANGE_DETECTED,
            ),
        )
        no_return_contract = ExpectedReturnContract(
            contract_id="return-no-return",
            contract_revision=self._revision,
            return_kind=ReturnContractKind.NO_RETURN,
            router_events=(),
            implementation_statuses=(),
        )
        valid_contracts = (self._router_contract(), implementation_contract, no_return_contract)
        for contract in valid_contracts:
            with self.subTest(return_kind=contract.return_kind):
                rebuilt = ExpectedReturnContract.model_validate_json(contract.model_dump_json())
                self.assertEqual(contract, rebuilt)

        rebuilt_skill = SkillReference.model_validate_json(self._skill().model_dump_json())
        self.assertEqual(self._skill(), rebuilt_skill)

        with self.assertRaises(ValidationError):
            SkillReference(
                reference_id="route-policy",
                source_revision="rev-0000000000000000",
                content_digest=self._digest,
            )
        with self.assertRaises(ValidationError):
            SkillReference(
                reference_id="route-policy",
                source_revision=self._revision,
                content_digest="sha256_0000000000000000000000000000000000000000000000000000000000000000",
            )

        for reference_id in ("route-prompt", "route-secret", "route://policy", "route\\policy"):
            with self.subTest(reference_id=reference_id), self.assertRaises(ValidationError):
                self._skill(reference_id)
        with self.assertRaises(ValidationError):
            SkillReference.model_validate(
                {"source_revision": self._revision, "content_digest": self._digest}
            )
        with self.assertRaises(ValidationError):
            SkillReference.model_validate(
                {
                    "reference_id": "route-policy",
                    "source_revision": self._revision,
                    "content_digest": None,
                }
            )
        with self.assertRaises(ValidationError):
            SkillReference.model_validate(
                {
                    "reference_id": "route-policy",
                    "source_revision": self._revision,
                    "content_digest": self._digest,
                    "extra": "forbidden",
                }
            )

        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-empty-router",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.ROUTER_EVENT,
                router_events=(),
                implementation_statuses=(),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-mixed-router",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.ROUTER_EVENT,
                router_events=(RouterEventKind.ACTION_COMPLETED,),
                implementation_statuses=(ImplementationReturnStatus.COMPLETED,),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-duplicate-router",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.ROUTER_EVENT,
                router_events=(RouterEventKind.ACTION_COMPLETED, RouterEventKind.ACTION_COMPLETED),
                implementation_statuses=(),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-empty-implementation",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.IMPLEMENTATION_RETURN,
                router_events=(),
                implementation_statuses=(),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-mixed-implementation",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.IMPLEMENTATION_RETURN,
                router_events=(RouterEventKind.ACTION_COMPLETED,),
                implementation_statuses=(ImplementationReturnStatus.COMPLETED,),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-duplicate-implementation",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.IMPLEMENTATION_RETURN,
                router_events=(),
                implementation_statuses=(
                    ImplementationReturnStatus.COMPLETED,
                    ImplementationReturnStatus.COMPLETED,
                ),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract(
                contract_id="return-nonempty-no-return",
                contract_revision=self._revision,
                return_kind=ReturnContractKind.NO_RETURN,
                router_events=(RouterEventKind.ACTION_COMPLETED,),
                implementation_statuses=(),
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract.model_validate(
                {
                    **self._router_contract().model_dump(),
                    "return_kind": None,
                }
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract.model_validate(
                {
                    **self._router_contract().model_dump(),
                    "router_events": None,
                }
            )
        with self.assertRaises(ValidationError):
            ExpectedReturnContract.model_validate(
                {
                    **self._router_contract().model_dump(),
                    "unexpected": "forbidden",
                }
            )

    def _git_file_bytes(self, relative_path: str) -> bytes:
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ("git", "-C", str(root), "show", f"HEAD:{relative_path}"),
            check=True,
            capture_output=True,
        )
        return result.stdout

    def test_profile_route_table_and_policy_metadata_are_exact(self) -> None:
        profile = build_router_poc_profile()
        self.assertEqual("router-control", profile.router_control_reference.reference_id)
        self.assertEqual(
            "rev-23dd53ad68e5562f",
            profile.router_control_reference.source_revision,
        )
        self.assertEqual(
            ReturnContractKind.NO_RETURN,
            profile.halt_return_contract.return_kind,
        )
        self.assertEqual((), profile.halt_return_contract.router_events)
        self.assertEqual((), profile.halt_return_contract.implementation_statuses)

        expected_keys = {(route.current_stage, route.input_event) for route in _EXPECTED_ROUTES}
        actual_keys = {(rule.current_stage, rule.event_kind) for rule in profile.transition_rules}
        self.assertEqual(expected_keys, actual_keys)
        self.assertEqual(len(_EXPECTED_ROUTES), len(profile.transition_rules))
        for expected in _EXPECTED_ROUTES:
            with self.subTest(route=(expected.current_stage, expected.input_event)):
                rule = profile.rule_for(
                    current_stage=expected.current_stage,
                    event_kind=expected.input_event,
                )
                if rule is None:
                    self.fail("expected route is missing from the POC profile")
                self.assertEqual(expected.reference_id, rule.skill_reference.reference_id)
                self.assertEqual(expected.return_kind, rule.expected_return.return_kind)
                self.assertEqual(expected.router_events, rule.expected_return.router_events)
                self.assertEqual(
                    expected.implementation_statuses,
                    rule.expected_return.implementation_statuses,
                )
                expected_contract_id = (
                    f"return-{expected.current_stage.value.replace('_', '-')}-"
                    f"{expected.input_event.value.replace('_', '-')}"
                )
                self.assertEqual(expected_contract_id, rule.expected_return.contract_id)
                self.assertEqual(
                    rule.skill_reference.source_revision,
                    rule.expected_return.contract_revision,
                )

        references = (profile.router_control_reference,) + tuple(
            rule.skill_reference for rule in profile.transition_rules
        )
        for expected_policy in _EXPECTED_POLICIES:
            with self.subTest(policy=expected_policy.reference_id):
                policy_path = (
                    Path(__file__).resolve().parents[1] / expected_policy.relative_path
                )
                repository_bytes = self._git_file_bytes(expected_policy.relative_path)
                self.assertEqual(
                    policy_path.read_bytes().replace(b"\r\n", b"\n"),
                    repository_bytes,
                )
                self.assertEqual(
                    expected_policy.content_digest,
                    "sha256_" + hashlib.sha256(repository_bytes).hexdigest(),
                )
                matching = tuple(
                    reference
                    for reference in references
                    if reference.reference_id == expected_policy.reference_id
                )
                self.assertGreaterEqual(len(matching), 1)
                for reference in matching:
                    self.assertEqual(expected_policy.source_revision, reference.source_revision)
                    self.assertEqual(expected_policy.content_digest, reference.content_digest)

    def test_profile_rejects_conflicting_reference_metadata_and_revision_mismatch(self) -> None:
        profile = build_router_poc_profile()
        first_rule = profile.transition_rules[0]
        conflicting_rule = TransitionRule.model_validate(
            {
                **first_rule.model_dump(),
                "skill_reference": {
                    "reference_id": first_rule.skill_reference.reference_id,
                    "source_revision": "rev-5f1e7958c70c8493",
                    "content_digest": "sha256_5f1e7958c70c8493de83aa1481e0f3f3e59c5a40e745a12077eb372fa6e0815e",
                },
            }
        )
        with self.assertRaises(ValidationError):
            ProjectWorkflowProfile.model_validate(
                {
                    **profile.model_dump(),
                    "transition_rules": (conflicting_rule,) + profile.transition_rules[1:],
                }
            )

        mismatched_rule = TransitionRule.model_validate(
            {
                **first_rule.model_dump(),
                "expected_return": {
                    **first_rule.expected_return.model_dump(),
                    "contract_revision": "rev-5f1e7958c70c8493",
                },
            }
        )
        with self.assertRaises(ValidationError):
            ProjectWorkflowProfile.model_validate(
                {
                    **profile.model_dump(),
                    "transition_rules": (mismatched_rule,) + profile.transition_rules[1:],
                }
            )

        with self.assertRaises(ValidationError):
            ProjectWorkflowProfile.model_validate(
                {
                    **profile.model_dump(),
                    "halt_return_contract": {
                        **profile.halt_return_contract.model_dump(),
                        "contract_revision": "rev-5f1e7958c70c8493",
                    },
                }
            )

    def test_success_retry_and_declared_wait_copy_the_exact_rule_contract(self) -> None:
        profile = build_router_poc_profile()
        engine = RouterEngine()
        goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-contract-goal",
            uri="project://router-contract/goal",
            revision="1",
        )
        intake_rule = profile.rule_for(
            current_stage=ProcessStage.INTAKE,
            event_kind=RouterEventKind.INTAKE,
        )
        if intake_rule is None:
            self.fail("POC profile must declare the intake rule")
        intake = engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(goal,),
            ),
            event=RouterEvent(event_id="evt-contract-intake", kind=RouterEventKind.INTAKE),
            profile=profile,
        )
        self.assertEqual(intake_rule.skill_reference, intake.skill_reference)
        self.assertEqual(intake_rule.expected_return, intake.expected_return)

        ticket = ArtifactRef(
            kind=ArtifactKind.TICKET,
            identifier="router-contract-ticket",
            uri="ticket://router-contract/ticket",
            revision="1",
        )
        retry_rule = profile.rule_for(
            current_stage=ProcessStage.SMOKE_TEST,
            event_kind=RouterEventKind.VALIDATION_FAILED,
        )
        if retry_rule is None:
            self.fail("POC profile must declare the validation retry rule")
        retry = engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.SMOKE_TEST,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(ticket,),
            ),
            event=RouterEvent(
                event_id="evt-contract-retry",
                kind=RouterEventKind.VALIDATION_FAILED,
            ),
            profile=profile,
        )
        self.assertEqual(retry_rule.skill_reference, retry.skill_reference)
        self.assertEqual(retry_rule.expected_return, retry.expected_return)

        wait_rule = profile.rule_for(
            current_stage=ProcessStage.SPEC,
            event_kind=RouterEventKind.ACTION_COMPLETED,
        )
        if wait_rule is None:
            self.fail("POC profile must declare the specification wait rule")
        specification = ArtifactRef(
            kind=ArtifactKind.SPEC,
            identifier="router-contract-spec",
            uri="spec://router-contract/spec",
            revision="1",
        )
        wait = engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.SPEC,
                authority_state=AuthorityState.PENDING,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(specification,),
            ),
            event=RouterEvent(
                event_id="evt-contract-wait",
                kind=RouterEventKind.ACTION_COMPLETED,
            ),
            profile=profile,
        )
        self.assertEqual(wait_rule.skill_reference, wait.skill_reference)
        self.assertEqual(wait_rule.expected_return, wait.expected_return)
        self.assertEqual(ContinuationDirective.WAIT_FOR_HUMAN, wait.continuation)

    def test_fail_closed_paths_use_the_profile_router_control_no_return(self) -> None:
        profile = build_router_poc_profile()
        engine = RouterEngine()
        delivery_mismatch = engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.MVP,
                artifact_refs=(),
            ),
            event=RouterEvent(event_id="evt-contract-delivery", kind=RouterEventKind.INTAKE),
            profile=profile,
        )
        self._assert_profile_fallback(delivery_mismatch, profile)

        missing_source = engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(),
            ),
            event=RouterEvent(event_id="evt-contract-missing", kind=RouterEventKind.INTAKE),
            profile=profile,
        )
        self._assert_profile_fallback(missing_source, profile)

        undeclared = engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.STOPPED,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(),
            ),
            event=RouterEvent(event_id="evt-contract-undeclared", kind=RouterEventKind.INTAKE),
            profile=profile,
        )
        self._assert_profile_fallback(undeclared, profile)

    def test_decision_serialization_contains_only_the_new_finite_metadata_contract(self) -> None:
        profile = build_router_poc_profile()
        goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-contract-serialization-goal",
            uri="project://router-contract/serialization-goal",
            revision="1",
        )
        decision = RouterEngine().decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(goal,),
            ),
            event=RouterEvent(
                event_id="evt-contract-serialization",
                kind=RouterEventKind.INTAKE,
            ),
            profile=profile,
        )
        serialized = decision.model_dump()
        self.assertEqual(
            {"reference_id", "source_revision", "content_digest"},
            set(serialized["skill_reference"]),
        )
        self.assertEqual(
            {
                "contract_id",
                "contract_revision",
                "return_kind",
                "router_events",
                "implementation_statuses",
            },
            set(serialized["expected_return"]),
        )
        self.assertNotIn("uri", serialized["skill_reference"])
        self.assertNotIn("prompt", serialized["skill_reference"]["reference_id"])
        self.assertNotIn("secret", serialized["skill_reference"]["reference_id"])

    def test_new_contract_surface_has_strong_annotations_and_no_bypass_constructs(self) -> None:
        source_paths = (
            Path("library/workflow_router/contracts.py"),
            Path("library/workflow_router/profile.py"),
            Path("library/workflow_router/router.py"),
        )
        class_names = {
            "SkillReference",
            "ExpectedReturnContract",
            "TransitionRule",
            "ProjectWorkflowProfile",
            "RouterDecision",
        }
        field_names = {
            "reference_id",
            "source_revision",
            "content_digest",
            "contract_id",
            "contract_revision",
            "return_kind",
            "router_events",
            "implementation_statuses",
            "skill_reference",
            "expected_return",
            "router_control_reference",
            "halt_return_contract",
        }
        for source_path in source_paths:
            source = source_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            class_nodes = {
                class_node.name: class_node
                for class_node in ast.walk(tree)
                if isinstance(class_node, ast.ClassDef) and class_node.name in class_names
            }
            for class_name in class_names.intersection(class_nodes):
                node = class_nodes[class_name]
                surface = ast.unparse(node)
                for forbidden in (
                    "Any",
                    "object",
                    "cast(",
                    "model_construct",
                    "model_copy",
                    "getattr(",
                    "hasattr(",
                    "setattr(",
                    "type: ignore",
                ):
                    self.assertNotIn(forbidden, surface)
                for child_node in ast.walk(node):
                    if isinstance(child_node, ast.ExceptHandler):
                        self.assertIsNotNone(child_node.type)
            for ast_node in ast.walk(tree):
                if isinstance(ast_node, (ast.Import, ast.ImportFrom)):
                    self.assertNotIn("inspect", ast.unparse(ast_node))
            for ast_node in ast.walk(tree):
                if isinstance(ast_node, ast.AnnAssign) and isinstance(ast_node.target, ast.Name):
                    if ast_node.target.id in field_names:
                        annotation = ast.unparse(ast_node.annotation)
                        self.assertNotIn("Optional", annotation)
                        self.assertNotIn("None", annotation)
                        self.assertNotIn("Any", annotation)
                        self.assertNotIn("object", annotation)

    def test_required_skill_reference_is_required(self) -> None:
        with self.assertRaises(ValidationError):
            TransitionRule.model_validate(
                {
                    "expected_return": self._router_contract(),
                    "current_stage": ProcessStage.ARCHITECTURE,
                    "event_kind": RouterEventKind.ACTION_COMPLETED,
                    "outcome": RouterOutcome.ADVANCE,
                    "next_stage": ProcessStage.GRILL,
                }
            )

    def test_successful_decision_copies_exact_rule_contract(self) -> None:
        profile = build_router_poc_profile()
        rule = profile.rule_for(
            current_stage=ProcessStage.INTAKE,
            event_kind=RouterEventKind.INTAKE,
        )
        if rule is None:
            self.fail("POC profile must declare the intake rule")
        goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-contract-reversal-goal",
            uri="project://router-contract/reversal-goal",
            revision="1",
        )
        decision = RouterEngine().decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(goal,),
            ),
            event=RouterEvent(event_id="evt-contract-reversal", kind=RouterEventKind.INTAKE),
            profile=profile,
        )
        self.assertEqual(rule.skill_reference, decision.skill_reference)
        self.assertEqual(rule.expected_return, decision.expected_return)


if __name__ == "__main__":
    unittest.main()
