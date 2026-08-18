"""Acceptance tests for the reusable, profile-driven workflow router."""

from __future__ import annotations

import ast
import hashlib
import json
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.workflow_router import (
    AgentContextActorRole,
    AgentContextDecisionKind,
    AgentContextKind,
    AgentContextLease,
    AgentContextLifecycle,
    AgentContextOperation,
    AgentContextTransitionDecision,
    AgentContextTransitionRequest,
    AgentContextUpstreamState,
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
    ModelRole,
    ModelRoleAssignment,
    ProcessStage,
    ReferenceStatus,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    ReturnContractKind,
    RoleActivityState,
    SharedContextAccessDecision,
    SharedContextAccessRequest,
    SharedContextContentManifest,
    SharedContextLifecycle,
    SharedContextOperation,
    SharedContextActorRole,
    SharedContextMutationDecision,
    SharedContextState,
    SkillReference,
    RunAcceptance,
    SourceSnippet,
    TicketScope,
    build_router_graph,
    build_router_poc_profile,
)
from library.workflow_router.graph import RouterGraphState
from library.workflow_router.contracts import (
    BranchFingerprint,
    EvidenceDigest,
    OpaqueMetadataId,
    ProjectId,
    RevisionDigest,
    ReviewedCommitReference,
    RouterDecision,
    WorktreeFingerprint,
)
from library.workflow_router.profile import ProjectWorkflowProfile, TransitionRule
from library.workflow_router.telemetry_cli import main as telemetry_main


@dataclass(frozen=True)
class _ExpectedRoute:
    current_stage: ProcessStage
    input_event: RouterEventKind
    reference_id: OpaqueMetadataId
    return_kind: ReturnContractKind
    router_events: tuple[RouterEventKind, ...]
    implementation_statuses: tuple[ImplementationReturnStatus, ...]


@dataclass(frozen=True)
class _ExpectedPolicy:
    reference_id: OpaqueMetadataId
    source_revision: RevisionDigest
    content_digest: EvidenceDigest
    relative_path: PurePosixPath


_EXPECTED_ROUTES: tuple[_ExpectedRoute, ...] = (
    _ExpectedRoute(
        ProcessStage.INTAKE,
        RouterEventKind.INTAKE,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (
            RouterEventKind.WAYFINDER_GO,
            RouterEventKind.WAYFINDER_NO_GO,
            RouterEventKind.WAYFINDER_INFO_REQUIRED,
        ),
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
        RouterEventKind.WAYFINDER_INFO_REQUIRED,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (RouterEventKind.OWNER_INPUT_PROVIDED,),
        (),
    ),
    _ExpectedRoute(
        ProcessStage.WAYFINDER,
        RouterEventKind.OWNER_INPUT_PROVIDED,
        "discovery-change",
        ReturnContractKind.ROUTER_EVENT,
        (
            RouterEventKind.WAYFINDER_GO,
            RouterEventKind.WAYFINDER_NO_GO,
            RouterEventKind.WAYFINDER_INFO_REQUIRED,
        ),
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


_EXPECTED_POLICIES: tuple[_ExpectedPolicy, ...] = (
    _ExpectedPolicy(
        "router-control",
        "rev-9b005bbc31dca89d",
        "sha256_9b005bbc31dca89d7e2e9394f095543c03c0ae5dd7eeaca70197d2a887466c0c",
        PurePosixPath("skills/johnny-project-takeover/references/router-control.md"),
    ),
    _ExpectedPolicy(
        "discovery-change",
        "rev-a1687d4fa9960e43",
        "sha256_a1687d4fa9960e439e7e390c4d9cdc4d62db6d93d69e4123dce0cc970b72216a",
        PurePosixPath("skills/johnny-project-takeover/references/discovery-change.md"),
    ),
    _ExpectedPolicy(
        "context-routing",
        "rev-db155a0be96c756f",
        "sha256_db155a0be96c756f4b79270ada14c088b338a21e878caff994ae31a41638859d",
        PurePosixPath("skills/johnny-project-takeover/references/context-routing.md"),
    ),
    _ExpectedPolicy(
        "specification-ticketing",
        "rev-26e443dfca8e8434",
        "sha256_26e443dfca8e84342bb2ca40d748ac155a2b34010fcd6dc7fd5b59c6de5936b3",
        PurePosixPath("skills/johnny-project-takeover/references/specification-ticketing.md"),
    ),
    _ExpectedPolicy(
        "implementation-authority",
        "rev-855117ed19c9c952",
        "sha256_855117ed19c9c952f8903bc56ce070d2cf3805fb51d7a450c46bbf8a00480f50",
        PurePosixPath("skills/johnny-project-takeover/references/implementation-authority.md"),
    ),
    _ExpectedPolicy(
        "implementation-tdd",
        "rev-38408006f23df3b6",
        "sha256_38408006f23df3b66a4368e2b8794cc099b84ea20417e56d881ff19512345574",
        PurePosixPath("skills/johnny-project-takeover/references/implementation-tdd.md"),
    ),
    _ExpectedPolicy(
        "review-checks",
        "rev-4b8527305609194a",
        "sha256_4b8527305609194ae9dd26c16a05ff72d22b1f20a8cb925175d6793766bb5f54",
        PurePosixPath("skills/johnny-project-takeover/references/review-checks.md"),
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
                source_revision="rev-9b005bbc31dca89d",
                content_digest="sha256_9b005bbc31dca89d7e2e9394f095543c03c0ae5dd7eeaca70197d2a887466c0c",
            ),
            halt_return_contract=ExpectedReturnContract(
                contract_id="router-control-no-return",
                contract_revision="rev-9b005bbc31dca89d",
                return_kind=ReturnContractKind.NO_RETURN,
                router_events=(),
                implementation_statuses=(),
            ),
            transition_rules=(
                TransitionRule(
                    skill_reference=SkillReference(
                        reference_id="legacy-route-architecture-action-completed",
                        source_revision="rev-a1687d4fa9960e43",
                        content_digest="sha256_a1687d4fa9960e439e7e390c4d9cdc4d62db6d93d69e4123dce0cc970b72216a",
                    ),
                    expected_return=ExpectedReturnContract(
                        contract_id="return-action-completed",
                        contract_revision="rev-a1687d4fa9960e43",
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
            shared_context_ref="ctx-shared-project",
            architecture_owner_capability_ref="cap-architecture-owner",
            model_role_assignments=(
                ModelRoleAssignment(
                    project_profile_ref="legacy-router-profile",
                    role=ModelRole.ARCHITECTURE_OWNER,
                    model_ref="model-legacy-architecture",
                    capability_refs=("cap-legacy-architecture",),
                    activity_state=RoleActivityState.ACTIVE,
                    evidence_refs=("evidence-legacy-architecture",),
                ),
                ModelRoleAssignment(
                    project_profile_ref="legacy-router-profile",
                    role=ModelRole.SUPERVISOR_REVIEWER,
                    model_ref="model-legacy-supervisor",
                    capability_refs=("cap-legacy-supervisor",),
                    activity_state=RoleActivityState.ACTIVE,
                    evidence_refs=("evidence-legacy-supervisor",),
                ),
                ModelRoleAssignment(
                    project_profile_ref="legacy-router-profile",
                    role=ModelRole.IMPLEMENTATION_OWNER,
                    model_ref="model-legacy-implementation",
                    capability_refs=("cap-legacy-implementation",),
                    activity_state=RoleActivityState.ACTIVE,
                    evidence_refs=("evidence-legacy-implementation",),
                ),
                ModelRoleAssignment(
                    project_profile_ref="legacy-router-profile",
                    role=ModelRole.RESEARCH_HELPER,
                    model_ref="model-legacy-research",
                    capability_refs=("cap-legacy-research",),
                    activity_state=RoleActivityState.SLEEPING,
                    evidence_refs=("evidence-legacy-research",),
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

    _revision = "rev-a1687d4fa9960e43"
    _digest = "sha256_a1687d4fa9960e439e7e390c4d9cdc4d62db6d93d69e4123dce0cc970b72216a"

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

    def _manifest(
        self,
        *,
        revision: RevisionDigest = "rev-0123456789abcdef",
        content_digest: EvidenceDigest = (
            "sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        ),
        suffix: str = "one",
    ) -> SharedContextContentManifest:
        return SharedContextContentManifest(
            revision=revision,
            content_digest=content_digest,
            stable_fact_refs=(f"fact-{suffix}",),
            invariant_boundary_refs=(f"boundary-{suffix}",),
            artifact_index_refs=(f"artifact-{suffix}",),
        )

    def _state(
        self,
        *,
        lifecycle: SharedContextLifecycle,
        revision: RevisionDigest | None = None,
        content_digest: EvidenceDigest | None = None,
        context_ref: OpaqueMetadataId = "ctx-shared-project",
    ) -> SharedContextState:
        return SharedContextState(
            context_ref=context_ref,
            lifecycle=lifecycle,
            revision=revision,
            content_digest=content_digest,
        )

    def _request(
        self,
        *,
        operation: SharedContextOperation,
        process_stage: ProcessStage,
        actor_role: SharedContextActorRole = SharedContextActorRole.ARCHITECTURE_OWNER,
        actor_capability_ref: OpaqueMetadataId = "cap-architecture-owner",
        expected_current_revision: RevisionDigest | None = None,
        candidate_manifest: SharedContextContentManifest | None = None,
        change_authority_state: AuthorityState = AuthorityState.NOT_REQUIRED,
        approved_change_ref: OpaqueMetadataId | None = None,
        context_ref: OpaqueMetadataId = "ctx-shared-project",
        request_ref: OpaqueMetadataId = "request-shared-context",
    ) -> SharedContextAccessRequest:
        return SharedContextAccessRequest(
            request_ref=request_ref,
            context_ref=context_ref,
            operation=operation,
            process_stage=process_stage,
            actor_role=actor_role,
            actor_capability_ref=actor_capability_ref,
            expected_current_revision=expected_current_revision,
            candidate_manifest=candidate_manifest,
            change_authority_state=change_authority_state,
            approved_change_ref=approved_change_ref,
        )

    def test_shared_context_public_entrypoint_exists(self) -> None:
        profile = build_router_poc_profile()
        request = self._request(
            operation=SharedContextOperation.CREATE_DRAFT,
            process_stage=ProcessStage.ARCHITECTURE,
            candidate_manifest=self._manifest(),
        )
        decision = RouterEngine().decide_shared_context_access(
            request=request,
            state=self._state(lifecycle=SharedContextLifecycle.ABSENT),
            profile=profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, decision.decision)

    def test_shared_context_contracts_round_trip_and_reject_operation_matrix(self) -> None:
        manifest = self._manifest()
        absent = self._state(lifecycle=SharedContextLifecycle.ABSENT)
        create = self._request(
            operation=SharedContextOperation.CREATE_DRAFT,
            process_stage=ProcessStage.ARCHITECTURE,
            candidate_manifest=manifest,
        )
        decision = SharedContextAccessDecision(
            request_ref=create.request_ref,
            context_ref=create.context_ref,
            operation=create.operation,
            decision=SharedContextMutationDecision.ALLOW,
            resulting_state=absent,
        )
        self.assertEqual(
            manifest,
            SharedContextContentManifest.model_validate_json(manifest.model_dump_json()),
        )
        self.assertEqual(
            absent,
            SharedContextState.model_validate_json(absent.model_dump_json()),
        )
        self.assertEqual(
            create,
            SharedContextAccessRequest.model_validate_json(create.model_dump_json()),
        )
        self.assertEqual(
            decision,
            SharedContextAccessDecision.model_validate_json(decision.model_dump_json()),
        )

        operation_payloads = {
            SharedContextOperation.CREATE_DRAFT: create.model_dump(),
            SharedContextOperation.REVISE_DRAFT: self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=self._manifest(
                    revision="rev-1123456789abcdef",
                    content_digest=(
                        "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
                    ),
                    suffix="two",
                ),
            ).model_dump(),
            SharedContextOperation.SEAL: self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision=manifest.revision,
            ).model_dump(),
            SharedContextOperation.READ_REFERENCE: self._request(
                operation=SharedContextOperation.READ_REFERENCE,
                process_stage=ProcessStage.REVIEW,
                expected_current_revision=manifest.revision,
                actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
                actor_capability_ref="cap-reviewer",
            ).model_dump(),
        }
        for operation, payload in operation_payloads.items():
            with self.subTest(operation=operation, invalid="missing"):
                missing = dict(payload)
                missing.pop("candidate_manifest", None)
                missing.pop("expected_current_revision", None)
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(missing)
            with self.subTest(operation=operation, invalid="extra"):
                extra = dict(payload)
                extra["progress_refs"] = ("progress-ref",)
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(extra)
            with self.subTest(operation=operation, invalid="wrong_operation"):
                wrong_operation = dict(payload)
                wrong_operation["operation"] = "unsupported"
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(wrong_operation)

        create_wrong = create.model_dump()
        create_wrong["expected_current_revision"] = manifest.revision
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(create_wrong)
        create_wrong = create.model_dump()
        create_wrong["change_authority_state"] = AuthorityState.APPROVED
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(create_wrong)
        revise_payload = operation_payloads[SharedContextOperation.REVISE_DRAFT]
        revise_wrong = dict(revise_payload)
        revise_wrong["candidate_manifest"] = None
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(revise_wrong)
        seal_payload = operation_payloads[SharedContextOperation.SEAL]
        seal_wrong = dict(seal_payload)
        seal_wrong["candidate_manifest"] = manifest
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(seal_wrong)
        read_wrong = dict(operation_payloads[SharedContextOperation.READ_REFERENCE])
        read_wrong["approved_change_ref"] = "change-approved"
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(read_wrong)

    def test_shared_context_manifest_and_state_are_metadata_only(self) -> None:
        manifest = self._manifest()
        invalid_manifests = (
            {"revision": self._revision, "content_digest": self._digest},
            {
                **manifest.model_dump(),
                "revision": "rev-0000000000000000",
            },
            {
                **manifest.model_dump(),
                "content_digest": "sha256_0000000000000000000000000000000000000000000000000000000000000000",
            },
            {
                **manifest.model_dump(),
                "artifact_index_refs": manifest.stable_fact_refs,
            },
            {
                **manifest.model_dump(),
                "progress_refs": ("progress-ref",),
            },
            {
                **manifest.model_dump(),
                "raw_text": "not metadata",
            },
            {
                **manifest.model_dump(),
                "uri": "file://outside",
            },
            {
                **manifest.model_dump(),
                "stable_fact_refs": ("prompt-ref",),
            },
            {
                **manifest.model_dump(),
                "stable_fact_refs": ("secret-ref",),
            },
        )
        for payload in invalid_manifests:
            with self.assertRaises(ValidationError):
                SharedContextContentManifest.model_validate(payload)

        with self.assertRaises(ValidationError):
            self._state(
                lifecycle=SharedContextLifecycle.ABSENT,
                revision=manifest.revision,
            )
        with self.assertRaises(ValidationError):
            self._state(
                lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
                content_digest=manifest.content_digest,
            )
        with self.assertRaises(ValidationError):
                SharedContextState.model_validate(
                {
                    "context_ref": "ctx-shared-project",
                    "lifecycle": SharedContextLifecycle.SEALED,
                    "revision": "rev-0000000000000000",
                    "content_digest": manifest.content_digest,
                }
            )

    def test_shared_context_profile_accepts_distinct_project_metadata(self) -> None:
        profile = build_router_poc_profile()
        alternate = ProjectWorkflowProfile.model_validate(
            {
                **profile.model_dump(),
                "shared_context_ref": "ctx-profile-project",
                "architecture_owner_capability_ref": "cap-profile-architecture-owner",
            }
        )
        self.assertEqual("ctx-profile-project", alternate.shared_context_ref)
        self.assertEqual(
            "cap-profile-architecture-owner",
            alternate.architecture_owner_capability_ref,
        )

    def test_shared_context_manifest_accepts_semantic_tree_reference_ids(self) -> None:
        manifest = SharedContextContentManifest(
            revision="rev-0123456789abcdef",
            content_digest=(
                "sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
            stable_fact_refs=("fact-requirement-current",),
            invariant_boundary_refs=("boundary-invariant-current",),
            artifact_index_refs=("idx-ticket-current",),
        )
        self.assertEqual(("idx-ticket-current",), manifest.artifact_index_refs)

    def test_shared_context_rejects_reserved_expected_revision(self) -> None:
        manifest = self._manifest()
        revised_manifest = self._manifest(
            revision="rev-1123456789abcdef",
            content_digest=(
                "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
            ),
            suffix="two",
        )
        valid_requests = (
            self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=revised_manifest,
            ),
            self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision=manifest.revision,
            ),
            self._request(
                operation=SharedContextOperation.READ_REFERENCE,
                process_stage=ProcessStage.REVIEW,
                expected_current_revision=manifest.revision,
                actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
                actor_capability_ref="cap-reviewer",
            ),
        )
        for request in valid_requests:
            with self.subTest(operation=request.operation):
                payload = request.model_dump()
                payload["expected_current_revision"] = "rev-0000000000000000"
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(payload)

    def test_shared_context_profile_and_allowed_rows_are_exact(self) -> None:
        profile = build_router_poc_profile()
        self.assertEqual("2", profile.profile_version)
        self.assertEqual("ctx-shared-project", profile.shared_context_ref)
        self.assertEqual("cap-architecture-owner", profile.architecture_owner_capability_ref)
        profile_payload = profile.model_dump()
        for field, value in (
            ("shared_context_ref", None),
            ("shared_context_ref", "file-ref"),
            ("shared_context_ref", "prompt-ref"),
            ("shared_context_ref", "secret-ref"),
            ("architecture_owner_capability_ref", "ctx-shared-project"),
            ("architecture_owner_capability_ref", "file-ref"),
            ("architecture_owner_capability_ref", "prompt-ref"),
            ("architecture_owner_capability_ref", "secret-ref"),
        ):
            with self.subTest(field=field, value=value):
                invalid = dict(profile_payload)
                invalid[field] = value
                with self.assertRaises(ValidationError):
                    ProjectWorkflowProfile.model_validate(invalid)

        manifest = self._manifest()
        revised_manifest = self._manifest(
            revision="rev-1123456789abcdef",
            content_digest=(
                "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
            ),
            suffix="two",
        )
        engine = RouterEngine()
        absent = self._state(lifecycle=SharedContextLifecycle.ABSENT)
        created = engine.decide_shared_context_access(
            request=self._request(
                operation=SharedContextOperation.CREATE_DRAFT,
                process_stage=ProcessStage.ARCHITECTURE,
                candidate_manifest=manifest,
            ),
            state=absent,
            profile=profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, created.decision)
        self.assertEqual(SharedContextLifecycle.ARCHITECTURE_DRAFT, created.resulting_state.lifecycle)
        self.assertEqual(manifest.revision, created.resulting_state.revision)
        self.assertEqual(manifest.content_digest, created.resulting_state.content_digest)

        draft = self._state(
            lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
            revision=manifest.revision,
            content_digest=manifest.content_digest,
        )
        revised = engine.decide_shared_context_access(
            request=self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=revised_manifest,
            ),
            state=draft,
            profile=profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, revised.decision)
        self.assertEqual(SharedContextLifecycle.ARCHITECTURE_DRAFT, revised.resulting_state.lifecycle)
        self.assertEqual(revised_manifest.revision, revised.resulting_state.revision)

        sealed = self._state(
            lifecycle=SharedContextLifecycle.SEALED,
            revision=manifest.revision,
            content_digest=manifest.content_digest,
        )
        reopened = engine.decide_shared_context_access(
            request=self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.ARCHITECTURE,
                expected_current_revision=manifest.revision,
                candidate_manifest=revised_manifest,
                change_authority_state=AuthorityState.APPROVED,
                approved_change_ref="change-approved",
            ),
            state=sealed,
            profile=profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, reopened.decision)
        self.assertEqual(SharedContextLifecycle.ARCHITECTURE_DRAFT, reopened.resulting_state.lifecycle)

        sealed_from_draft = engine.decide_shared_context_access(
            request=self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision=manifest.revision,
            ),
            state=draft,
            profile=profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, sealed_from_draft.decision)
        self.assertEqual(SharedContextLifecycle.SEALED, sealed_from_draft.resulting_state.lifecycle)

        for stage in (
            ProcessStage.SPEC,
            ProcessStage.TICKETS,
            ProcessStage.IMPLEMENT,
            ProcessStage.SMOKE_TEST,
            ProcessStage.REVIEW,
            ProcessStage.HANDOFF,
        ):
            for actor_role in SharedContextActorRole:
                with self.subTest(stage=stage, actor_role=actor_role):
                    read = engine.decide_shared_context_access(
                        request=self._request(
                            operation=SharedContextOperation.READ_REFERENCE,
                            process_stage=stage,
                            actor_role=actor_role,
                            actor_capability_ref="cap-reader",
                            expected_current_revision=manifest.revision,
                        ),
                        state=sealed,
                        profile=profile,
                    )
                    self.assertEqual(SharedContextMutationDecision.ALLOW, read.decision)
                    self.assertEqual(sealed, read.resulting_state)

        serialized = reopened.model_dump()
        self.assertEqual(
            {"request_ref", "context_ref", "operation", "decision", "resulting_state"},
            set(serialized),
        )
        self.assertNotIn("raw_text", reopened.model_dump_json())
        self.assertNotIn("progress", reopened.model_dump_json())

    def test_shared_context_wrong_role_stage_and_illegal_lifecycle_are_forbidden(self) -> None:
        profile = build_router_poc_profile()
        engine = RouterEngine()
        manifest = self._manifest()
        absent = self._state(lifecycle=SharedContextLifecycle.ABSENT)
        draft = self._state(
            lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
            revision=manifest.revision,
            content_digest=manifest.content_digest,
        )
        sealed = self._state(
            lifecycle=SharedContextLifecycle.SEALED,
            revision=manifest.revision,
            content_digest=manifest.content_digest,
        )
        write_cases = (
            (
                SharedContextOperation.CREATE_DRAFT,
                absent,
                ProcessStage.ARCHITECTURE,
                SharedContextActorRole.SUPERVISOR_REVIEWER,
                "cap-supervisor",
                None,
                manifest,
            ),
            (
                SharedContextOperation.REVISE_DRAFT,
                draft,
                ProcessStage.GRILL,
                SharedContextActorRole.ARCHITECTURE_OWNER,
                "cap-other",
                manifest.revision,
                self._manifest(
                    revision="rev-1123456789abcdef",
                    content_digest=(
                        "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
                    ),
                    suffix="two",
                ),
            ),
            (
                SharedContextOperation.SEAL,
                draft,
                ProcessStage.SPEC,
                SharedContextActorRole.ARCHITECTURE_OWNER,
                "cap-architecture-owner",
                manifest.revision,
                None,
            ),
        )
        for operation, state, stage, role, capability, expected, candidate in write_cases:
            with self.subTest(operation=operation, reason="writer-or-stage"):
                request = self._request(
                    operation=operation,
                    process_stage=stage,
                    actor_role=role,
                    actor_capability_ref=capability,
                    expected_current_revision=expected,
                    candidate_manifest=candidate,
                )
                decision = engine.decide_shared_context_access(
                    request=request,
                    state=state,
                    profile=profile,
                )
                self.assertEqual(SharedContextMutationDecision.FORBID_ROLE_OR_STAGE, decision.decision)
                self.assertEqual(state, decision.resulting_state)

        illegal_cases = (
            (SharedContextOperation.CREATE_DRAFT, draft, ProcessStage.ARCHITECTURE, manifest),
            (SharedContextOperation.SEAL, sealed, ProcessStage.CONTEXT, None),
            (SharedContextOperation.READ_REFERENCE, draft, ProcessStage.REVIEW, None),
        )
        for operation, state, stage, candidate in illegal_cases:
            with self.subTest(operation=operation, lifecycle=state.lifecycle):
                expected = (
                    None
                    if operation is SharedContextOperation.CREATE_DRAFT
                    else state.revision
                )
                request = self._request(
                    operation=operation,
                    process_stage=stage,
                    expected_current_revision=expected,
                    candidate_manifest=candidate,
                    actor_role=(
                        SharedContextActorRole.RESEARCH_HELPER
                        if operation is SharedContextOperation.READ_REFERENCE
                        else SharedContextActorRole.ARCHITECTURE_OWNER
                    ),
                    actor_capability_ref=(
                        "cap-reader"
                        if operation is SharedContextOperation.READ_REFERENCE
                        else "cap-architecture-owner"
                    ),
                )
                decision = engine.decide_shared_context_access(
                    request=request,
                    state=state,
                    profile=profile,
                )
                self.assertEqual(SharedContextMutationDecision.FORBID_ROLE_OR_STAGE, decision.decision)
                self.assertEqual(state, decision.resulting_state)

    def test_shared_context_stale_and_change_control_precedence_are_exact(self) -> None:
        profile = build_router_poc_profile()
        engine = RouterEngine()
        manifest = self._manifest()
        revised_manifest = self._manifest(
            revision="rev-1123456789abcdef",
            content_digest=(
                "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
            ),
            suffix="two",
        )
        draft = self._state(
            lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
            revision=manifest.revision,
            content_digest=manifest.content_digest,
        )
        sealed = self._state(
            lifecycle=SharedContextLifecycle.SEALED,
            revision=manifest.revision,
            content_digest=manifest.content_digest,
        )

        stale_requests = (
            self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision=manifest.revision,
                context_ref="ctx-other-project",
            ),
            self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision="rev-1123456789abcdef",
            ),
            self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=manifest,
            ),
        )
        states = (draft, draft, draft)
        for request, state in zip(stale_requests, states):
            with self.subTest(request=request.request_ref, operation=request.operation):
                decision = engine.decide_shared_context_access(
                    request=request,
                    state=state,
                    profile=profile,
                )
                self.assertEqual(SharedContextMutationDecision.STALE_REVISION, decision.decision)
                self.assertEqual(state, decision.resulting_state)

        require_change = engine.decide_shared_context_access(
            request=self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=revised_manifest,
            ),
            state=sealed,
            profile=profile,
        )
        self.assertEqual(
            SharedContextMutationDecision.REQUIRE_CHANGE_CONTROL,
            require_change.decision,
        )
        self.assertEqual(sealed, require_change.resulting_state)

    def test_shared_context_supervisor_write_reversal_is_red_when_admitted(self) -> None:
        profile = build_router_poc_profile()
        request = self._request(
            operation=SharedContextOperation.CREATE_DRAFT,
            process_stage=ProcessStage.ARCHITECTURE,
            actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
            actor_capability_ref="cap-architecture-owner",
            candidate_manifest=self._manifest(),
        )
        decision = RouterEngine().decide_shared_context_access(
            request=request,
            state=self._state(lifecycle=SharedContextLifecycle.ABSENT),
            profile=profile,
        )
        self.assertEqual(SharedContextMutationDecision.FORBID_ROLE_OR_STAGE, decision.decision)

    def test_shared_context_sealed_revise_without_change_proof_is_red_when_admitted(self) -> None:
        profile = build_router_poc_profile()
        manifest = self._manifest()
        revised_manifest = self._manifest(
            revision="rev-1123456789abcdef",
            content_digest=(
                "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
            ),
            suffix="two",
        )
        decision = RouterEngine().decide_shared_context_access(
            request=self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=revised_manifest,
                change_authority_state=AuthorityState.NOT_REQUIRED,
                approved_change_ref=None,
            ),
            state=self._state(
                lifecycle=SharedContextLifecycle.SEALED,
                revision=manifest.revision,
                content_digest=manifest.content_digest,
            ),
            profile=profile,
        )
        self.assertEqual(
            SharedContextMutationDecision.REQUIRE_CHANGE_CONTROL,
            decision.decision,
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

    def test_profile_route_table_and_policy_metadata_are_exact(self) -> None:
        profile = build_router_poc_profile()
        self.assertEqual("router-control", profile.router_control_reference.reference_id)
        self.assertEqual(
            "rev-9b005bbc31dca89d",
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
                repository_bytes = policy_path.read_bytes().replace(b"\r\n", b"\n")
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
            Path("tests/test_workflow_router.py"),
        )
        class_names = {
            "SkillReference",
            "ExpectedReturnContract",
            "TransitionRule",
            "ProjectWorkflowProfile",
            "RouterDecision",
            "SharedContextContentManifest",
            "SharedContextState",
            "SharedContextAccessRequest",
            "SharedContextAccessDecision",
            "AgentContextKind",
            "AgentContextActorRole",
            "AgentContextLifecycle",
            "AgentContextOperation",
            "AgentContextUpstreamState",
            "AgentContextDecisionKind",
            "AgentContextLease",
            "AgentContextTransitionRequest",
            "AgentContextTransitionDecision",
            "_PolicyRoute",
            "_ExpectedRoute",
            "_ExpectedPolicy",
        }
        new_contract_class_names = {
            "SharedContextContentManifest",
            "SharedContextState",
            "SharedContextAccessRequest",
            "SharedContextAccessDecision",
            "AgentContextLease",
            "AgentContextTransitionRequest",
            "AgentContextTransitionDecision",
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
            "shared_context_ref",
            "architecture_owner_capability_ref",
            "context_ref",
            "lifecycle",
            "revision",
            "stable_fact_refs",
            "invariant_boundary_refs",
            "artifact_index_refs",
            "request_ref",
            "operation",
            "process_stage",
            "actor_role",
            "actor_capability_ref",
            "expected_current_revision",
            "candidate_manifest",
            "change_authority_state",
            "approved_change_ref",
            "decision",
            "resulting_state",
            "project_id",
            "context_kind",
            "artifact_path_refs",
            "ticket_ref",
            "ticket_revision",
            "receipt_ref",
            "owner_ref",
            "worktree_ref",
            "branch_ref",
            "baseline_revision",
            "control_baseline_ref",
            "side_context_id",
            "expected_return_ref",
            "invalidation_refs",
            "upstream_state",
            "expected_current_lease_ref",
            "expected_current_side_context_id",
            "candidate_lease",
            "prior_lease_result",
            "active_lease",
        }
        nullable_field_names = {
            "revision",
            "content_digest",
            "expected_current_revision",
            "candidate_manifest",
            "approved_change_ref",
            "expected_current_lease_ref",
            "expected_current_side_context_id",
            "candidate_lease",
            "prior_lease_result",
            "active_lease",
        }
        expected_class_fields = {
            "library/workflow_router/contracts.py": {
                "SharedContextContentManifest": {
                    "revision": "RevisionDigest",
                    "content_digest": "EvidenceDigest",
                    "stable_fact_refs": "tuple[OpaqueMetadataId, ...]",
                    "invariant_boundary_refs": "tuple[OpaqueMetadataId, ...]",
                    "artifact_index_refs": "tuple[OpaqueMetadataId, ...]",
                },
                "SharedContextState": {
                    "context_ref": "OpaqueMetadataId",
                    "lifecycle": "SharedContextLifecycle",
                    "revision": "RevisionDigest | None",
                    "content_digest": "EvidenceDigest | None",
                },
                "SharedContextAccessRequest": {
                    "request_ref": "OpaqueMetadataId",
                    "context_ref": "OpaqueMetadataId",
                    "operation": "SharedContextOperation",
                    "process_stage": "ProcessStage",
                    "actor_role": "SharedContextActorRole",
                    "actor_capability_ref": "OpaqueMetadataId",
                    "expected_current_revision": "RevisionDigest | None",
                    "candidate_manifest": "SharedContextContentManifest | None",
                    "change_authority_state": "AuthorityState",
                    "approved_change_ref": "OpaqueMetadataId | None",
                },
                "SharedContextAccessDecision": {
                    "request_ref": "OpaqueMetadataId",
                    "context_ref": "OpaqueMetadataId",
                    "operation": "SharedContextOperation",
                    "decision": "SharedContextMutationDecision",
                    "resulting_state": "SharedContextState",
                },
                "AgentContextLease": {
                    "lease_ref": "OpaqueMetadataId",
                    "project_id": "ProjectId",
                    "context_kind": "AgentContextKind",
                    "lifecycle": "AgentContextLifecycle",
                    "actor_role": "AgentContextActorRole",
                    "actor_capability_ref": "OpaqueMetadataId",
                    "artifact_path_refs": "tuple[OpaqueMetadataId, ...]",
                    "ticket_ref": "OpaqueMetadataId",
                    "ticket_revision": "RevisionDigest",
                    "receipt_ref": "OpaqueMetadataId",
                    "owner_ref": "OpaqueMetadataId",
                    "worktree_ref": "WorktreeFingerprint",
                    "branch_ref": "BranchFingerprint",
                    "baseline_revision": "RevisionDigest",
                    "control_baseline_ref": "ReviewedCommitReference",
                    "side_context_id": "OpaqueMetadataId",
                    "expected_return_ref": "OpaqueMetadataId",
                    "invalidation_refs": "tuple[OpaqueMetadataId, ...]",
                },
                "AgentContextTransitionRequest": {
                    "request_ref": "OpaqueMetadataId",
                    "operation": "AgentContextOperation",
                    "upstream_state": "AgentContextUpstreamState",
                    "expected_current_lease_ref": "OpaqueMetadataId | None",
                    "expected_current_side_context_id": "OpaqueMetadataId | None",
                    "candidate_lease": "AgentContextLease | None",
                },
                "AgentContextTransitionDecision": {
                    "request_ref": "OpaqueMetadataId",
                    "operation": "AgentContextOperation",
                    "decision": "AgentContextDecisionKind",
                    "prior_lease_result": "AgentContextLease | None",
                    "active_lease": "AgentContextLease | None",
                },
            },
            "library/workflow_router/profile.py": {
                "_PolicyRoute": {"reference_id": "OpaqueMetadataId"},
            },
            "tests/test_workflow_router.py": {
                "_ExpectedRoute": {"reference_id": "OpaqueMetadataId"},
                "_ExpectedPolicy": {
                    "reference_id": "OpaqueMetadataId",
                    "source_revision": "RevisionDigest",
                    "content_digest": "EvidenceDigest",
                    "relative_path": "PurePosixPath",
                },
            },
        }
        expected_module_annotations = {
            "library/workflow_router/profile.py": {
                "_POLICY_REFERENCES": "tuple[SkillReference, ...]",
                "_POLICY_ROUTES": "tuple[_PolicyRoute, ...]",
            },
            "tests/test_workflow_router.py": {
                "_EXPECTED_ROUTES": "tuple[_ExpectedRoute, ...]",
                "_EXPECTED_POLICIES": "tuple[_ExpectedPolicy, ...]",
            },
        }
        expected_function_parameters = {
            "library/workflow_router/profile.py": {
                "_policy_reference_for": {"reference_id": "OpaqueMetadataId"},
            },
            "library/workflow_router/router.py": {
                "decide_shared_context_access": {
                    "request": "SharedContextAccessRequest",
                    "state": "SharedContextState",
                    "profile": "ProjectWorkflowProfile",
                },
                "decide_agent_context_transition": {
                    "request": "AgentContextTransitionRequest",
                    "current_lease": "AgentContextLease | None",
                },
            },
        }
        expected_function_returns = {
            "library/workflow_router/router.py": {
                "decide_agent_context_transition": "AgentContextTransitionDecision",
            },
        }
        expected_local_annotations = {
            "library/workflow_router/profile.py": {
                "has_unique_transition_keys": {
                    "references": "dict[OpaqueMetadataId, SkillReference]",
                },
                "_expected_return_for": {"contract_id": "OpaqueMetadataId"},
            },
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
                    "callable(",
                    "model_construct",
                    "model_copy",
                    "getattr(",
                    "hasattr(",
                    "setattr(",
                    "type: ignore",
                ):
                    self.assertNotIn(forbidden, surface)
                if class_name in new_contract_class_names:
                    annotations = {
                        node.target.id: ast.unparse(node.annotation)
                        for node in node.body
                        if isinstance(node, ast.AnnAssign)
                        and isinstance(node.target, ast.Name)
                    }
                    self.assertNotIn("str", annotations.values())
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
                        if "None" in annotation:
                            self.assertIn(ast_node.target.id, nullable_field_names)
                        self.assertNotIn("Any", annotation)
                        self.assertNotIn("object", annotation)
            source_key = source_path.as_posix()
            for class_name, fields in expected_class_fields.get(source_key, {}).items():
                class_node = class_nodes.get(class_name)
                self.assertIsNotNone(class_node)
                if class_node is None:
                    continue
                annotations = {
                    node.target.id: ast.unparse(node.annotation)
                    for node in class_node.body
                    if isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id in fields
                }
                for field_name, expected_annotation in fields.items():
                    self.assertEqual(expected_annotation, annotations.get(field_name))
            module_annotations = {
                node.target.id: ast.unparse(node.annotation)
                for node in tree.body
                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
            }
            for name, expected_annotation in expected_module_annotations.get(source_key, {}).items():
                self.assertEqual(expected_annotation, module_annotations.get(name))
            functions = {
                node.name: node
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            for function_name, parameters in expected_function_parameters.get(
                source_key, {}
            ).items():
                function_node = functions.get(function_name)
                self.assertIsNotNone(function_node)
                if function_node is None:
                    continue
                function_annotations = {
                    parameter.arg: ast.unparse(parameter.annotation)
                    for parameter in (
                        *function_node.args.posonlyargs,
                        *function_node.args.args,
                        *function_node.args.kwonlyargs,
                    )
                    if parameter.annotation is not None
                }
                for parameter_name, expected_annotation in parameters.items():
                    self.assertEqual(
                        expected_annotation,
                        function_annotations.get(parameter_name),
                    )
            functions_with_returns = expected_function_returns.get(source_key, {})
            for function_name, expected_annotation in functions_with_returns.items():
                function_node = functions.get(function_name)
                self.assertIsNotNone(function_node)
                if function_node is not None and function_node.returns is not None:
                    self.assertEqual(expected_annotation, ast.unparse(function_node.returns))
            for function_name, locals_ in expected_local_annotations.get(source_key, {}).items():
                function_node = functions.get(function_name)
                self.assertIsNotNone(function_node)
                if function_node is None:
                    continue
                local_annotations = {
                    node.target.id: ast.unparse(node.annotation)
                    for node in ast.walk(function_node)
                    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                }
                for local_name, expected_annotation in locals_.items():
                    self.assertEqual(expected_annotation, local_annotations.get(local_name))
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


class AgentContextLeaseGateTests(unittest.TestCase):
    """Exercise the ticket-scoped Agent Context lease lifecycle gate."""

    def _lease(
        self,
        *,
        lease_ref: OpaqueMetadataId = "lease-r02b",
        project_id: ProjectId = "prj_0123456789abcdef",
        lifecycle: AgentContextLifecycle = AgentContextLifecycle.ACTIVE,
        actor_capability_ref: OpaqueMetadataId = "owner-r02b",
        artifact_path_refs: tuple[OpaqueMetadataId, ...] = ("artifact-r02b-leaf",),
        ticket_ref: OpaqueMetadataId = "ticket-r02b",
        ticket_revision: RevisionDigest = "rev-0123456789abcdef",
        receipt_ref: OpaqueMetadataId = "receipt-r02b",
        owner_ref: OpaqueMetadataId = "owner-r02b",
        worktree_ref: WorktreeFingerprint = "worktree-router-02",
        branch_ref: BranchFingerprint = "branch-router-02",
        baseline_revision: RevisionDigest = "rev-1123456789abcdef",
        control_baseline_ref: ReviewedCommitReference = "0123456789abcdef",
        side_context_id: OpaqueMetadataId = "side-context-r02b",
        expected_return_ref: OpaqueMetadataId = "ret-agent-context-review-handoff-r02b",
        invalidation_refs: tuple[OpaqueMetadataId, ...] = (),
    ) -> AgentContextLease:
        return AgentContextLease(
            lease_ref=lease_ref,
            project_id=project_id,
            context_kind=AgentContextKind.IMPLEMENTATION_TICKET,
            lifecycle=lifecycle,
            actor_role=AgentContextActorRole.IMPLEMENTATION_OWNER,
            actor_capability_ref=actor_capability_ref,
            artifact_path_refs=artifact_path_refs,
            ticket_ref=ticket_ref,
            ticket_revision=ticket_revision,
            receipt_ref=receipt_ref,
            owner_ref=owner_ref,
            worktree_ref=worktree_ref,
            branch_ref=branch_ref,
            baseline_revision=baseline_revision,
            control_baseline_ref=control_baseline_ref,
            side_context_id=side_context_id,
            expected_return_ref=expected_return_ref,
            invalidation_refs=invalidation_refs,
        )

    def _request(
        self,
        *,
        request_ref: OpaqueMetadataId = "request-r02b",
        operation: AgentContextOperation = AgentContextOperation.OPEN,
        upstream_state: AgentContextUpstreamState = AgentContextUpstreamState.CURRENT,
        expected_current_lease_ref: OpaqueMetadataId | None = None,
        expected_current_side_context_id: OpaqueMetadataId | None = None,
        candidate_lease: AgentContextLease | None = None,
    ) -> AgentContextTransitionRequest:
        return AgentContextTransitionRequest(
            request_ref=request_ref,
            operation=operation,
            upstream_state=upstream_state,
            expected_current_lease_ref=expected_current_lease_ref,
            expected_current_side_context_id=expected_current_side_context_id,
            candidate_lease=candidate_lease,
        )

    def _correction_lease(self, prior: AgentContextLease) -> AgentContextLease:
        return self._lease(
            lease_ref="lease-r02b-correction",
            artifact_path_refs=("artifact-r02b-correction",),
            baseline_revision="rev-2123456789abcdef",
            control_baseline_ref="1123456789abcdef",
            side_context_id="side-context-r02b-correction",
            invalidation_refs=(prior.side_context_id,),
        )

    def _switch_lease(self, prior: AgentContextLease) -> AgentContextLease:
        return self._lease(
            lease_ref="lease-r02b-switch",
            artifact_path_refs=("artifact-r02b-switch",),
            ticket_ref="ticket-r02b-next",
            ticket_revision="rev-2123456789abcdef",
            receipt_ref="receipt-r02b-next",
            branch_ref="branch-router-03",
            baseline_revision="rev-3123456789abcdef",
            control_baseline_ref="2123456789abcdef",
            side_context_id="side-context-r02b-switch",
            expected_return_ref="ret-agent-context-review-handoff-next",
            invalidation_refs=(prior.side_context_id,),
        )

    def _decision_for(
        self,
        *,
        request: AgentContextTransitionRequest,
        current_lease: AgentContextLease | None,
    ) -> AgentContextTransitionDecision:
        return RouterEngine().decide_agent_context_transition(
            request=request,
            current_lease=current_lease,
        )

    def test_open_admits_one_active_implementation_lease(self) -> None:
        lease = self._lease(lease_ref="lease-r02b-open")
        request = self._request(
            request_ref="request-r02b-open",
            candidate_lease=lease,
        )

        decision = self._decision_for(
            request=request,
            current_lease=None,
        )

        self.assertEqual(AgentContextDecisionKind.ALLOW, decision.decision)
        self.assertIsNone(decision.prior_lease_result)
        self.assertEqual(lease, decision.active_lease)

    def test_public_contracts_are_finite_and_json_round_trip_exactly(self) -> None:
        self.assertEqual(
            {member.value for member in AgentContextKind},
            {"implementation_ticket"},
        )
        self.assertEqual(
            {member.value for member in AgentContextActorRole},
            {"implementation_owner"},
        )
        self.assertEqual(
            {member.value for member in AgentContextLifecycle},
            {"active", "closed", "invalidated"},
        )
        self.assertEqual(
            {member.value for member in AgentContextOperation},
            {"open", "resume", "rebind_correction", "switch_ticket", "close"},
        )
        self.assertEqual(
            {member.value for member in AgentContextUpstreamState},
            {"current", "missing", "requirement_changed"},
        )
        self.assertEqual(
            {member.value for member in AgentContextDecisionKind},
            {
                "allow",
                "agent_context_binding_mismatch",
                "agent_context_stale",
                "upstream_decision_required",
                "requirement_changed",
            },
        )

        current = self._lease()
        correction = self._correction_lease(current)
        switch = self._switch_lease(current)
        requests = (
            self._request(
                request_ref="request-r02b-open-round-trip",
                candidate_lease=current,
            ),
            self._request(
                request_ref="request-r02b-row-two-round-trip",
                operation=AgentContextOperation.RESUME,
                expected_current_lease_ref=current.lease_ref,
                expected_current_side_context_id=current.side_context_id,
                candidate_lease=current,
            ),
            self._request(
                request_ref="request-r02b-correction-round-trip",
                operation=AgentContextOperation.REBIND_CORRECTION,
                expected_current_lease_ref=current.lease_ref,
                expected_current_side_context_id=current.side_context_id,
                candidate_lease=correction,
            ),
            self._request(
                request_ref="request-r02b-switch-round-trip",
                operation=AgentContextOperation.SWITCH_TICKET,
                expected_current_lease_ref=current.lease_ref,
                expected_current_side_context_id=current.side_context_id,
                candidate_lease=switch,
            ),
            self._request(
                request_ref="request-r02b-close-round-trip",
                operation=AgentContextOperation.CLOSE,
                expected_current_lease_ref=current.lease_ref,
                expected_current_side_context_id=current.side_context_id,
            ),
        )
        for request in requests:
            with self.subTest(operation=request.operation):
                self.assertEqual(
                    request,
                    AgentContextTransitionRequest.model_validate_json(
                        request.model_dump_json()
                    ),
                )

        decision = self._decision_for(
            request=requests[0],
            current_lease=None,
        )
        self.assertEqual(
            decision,
            AgentContextTransitionDecision.model_validate_json(decision.model_dump_json()),
        )
        self.assertEqual(
            {
                "lease_ref",
                "project_id",
                "context_kind",
                "lifecycle",
                "actor_role",
                "actor_capability_ref",
                "artifact_path_refs",
                "ticket_ref",
                "ticket_revision",
                "receipt_ref",
                "owner_ref",
                "worktree_ref",
                "branch_ref",
                "baseline_revision",
                "control_baseline_ref",
                "side_context_id",
                "expected_return_ref",
                "invalidation_refs",
            },
            set(current.model_dump()),
        )

    def test_public_contracts_reject_wrong_null_extra_and_duplicate_shapes(self) -> None:
        current = self._lease()
        open_request = self._request(candidate_lease=current)
        invalid_open_payloads = (
            {**open_request.model_dump(), "expected_current_lease_ref": current.lease_ref},
            {**open_request.model_dump(), "expected_current_side_context_id": current.side_context_id},
            {**open_request.model_dump(), "candidate_lease": None},
            {**open_request.model_dump(), "unknown_field": "not-allowed"},
            {**open_request.model_dump(), "operation": "unknown"},
        )
        resume_request = self._request(
            operation=AgentContextOperation.RESUME,
            expected_current_lease_ref=current.lease_ref,
            expected_current_side_context_id=current.side_context_id,
            candidate_lease=current,
        )
        invalid_replacement_payloads = (
            {**resume_request.model_dump(), "expected_current_lease_ref": None},
            {**resume_request.model_dump(), "expected_current_side_context_id": None},
            {**resume_request.model_dump(), "candidate_lease": None},
            {
                **self._request(
                    operation=AgentContextOperation.CLOSE,
                    expected_current_lease_ref=current.lease_ref,
                    expected_current_side_context_id=current.side_context_id,
                ).model_dump(),
                "candidate_lease": current,
            },
        )
        for payload in invalid_open_payloads + invalid_replacement_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError):
                    AgentContextTransitionRequest.model_validate(payload)

        invalid_lease_payloads = (
            {**current.model_dump(), "artifact_path_refs": ("artifact-r02b-leaf", "artifact-r02b-leaf")},
            {**current.model_dump(), "ticket_revision": "rev-0000000000000000"},
            {**current.model_dump(), "baseline_revision": "rev-0000000000000000"},
            {**current.model_dump(), "control_baseline_ref": "0000000000000000"},
            {**current.model_dump(), "actor_capability_ref": "owner-r02b-other"},
            {**current.model_dump(), "invalidation_refs": ("side-context-r02b",)},
            {**current.model_dump(), "artifact_path_refs": ("artifact/path-policy",)},
            {**current.model_dump(), "raw_context": "not-allowed"},
        )
        for payload in invalid_lease_payloads:
            with self.subTest(invalid_lease=payload):
                with self.assertRaises(ValidationError):
                    AgentContextLease.model_validate(payload)

    def test_semantic_leaf_ids_are_portable_but_locators_and_raw_fields_reject(self) -> None:
        semantic_cases = (
            ("artifact source", ("artifact-source-index",), "ticket-r02b", "ret-agent-context-review-handoff-r02b"),
            ("ticket prompt", ("artifact-r02b-leaf",), "ticket-prompt-hardening", "ret-agent-context-review-handoff-r02b"),
            ("return resume", ("artifact-r02b-leaf",), "ticket-r02b", "return-resume-review"),
            ("artifact path", ("artifact-path-policy",), "ticket-r02b", "ret-agent-context-review-handoff-r02b"),
            ("artifact text", ("artifact-text-contract",), "ticket-r02b", "ret-agent-context-review-handoff-r02b"),
        )
        for label, artifact_path_refs, ticket_ref, expected_return_ref in semantic_cases:
            with self.subTest(semantic_id=label):
                lease = self._lease(
                    lease_ref=f"lease-semantic-{label.replace(' ', '-')}",
                    artifact_path_refs=artifact_path_refs,
                    ticket_ref=ticket_ref,
                    expected_return_ref=expected_return_ref,
                )
                self.assertEqual(artifact_path_refs, lease.artifact_path_refs)
                self.assertEqual(ticket_ref, lease.ticket_ref)
                self.assertEqual(expected_return_ref, lease.expected_return_ref)

        negative_payloads = (
            {**self._lease().model_dump(), "artifact_path_refs": ("artifact/path-policy",)},
            {**self._lease().model_dump(), "raw_context": "transcript-not-allowed"},
        )
        for payload in negative_payloads:
            with self.subTest(invalid_lease=payload):
                with self.assertRaises(ValidationError):
                    AgentContextLease.model_validate(payload)

    def test_public_decisions_reject_contradictory_result_shapes(self) -> None:
        current = self._lease()
        correction = self._correction_lease(current)
        switch = self._switch_lease(current)
        closed = self._lease(lifecycle=AgentContextLifecycle.CLOSED)
        different_active = self._lease(lease_ref="lease-r02b-different-active")
        cases = (
            (
                "open without active",
                AgentContextOperation.OPEN,
                AgentContextDecisionKind.ALLOW,
                None,
                None,
            ),
            (
                "open with closed active",
                AgentContextOperation.OPEN,
                AgentContextDecisionKind.ALLOW,
                None,
                closed,
            ),
            (
                "rejected with active replacement",
                AgentContextOperation.RESUME,
                AgentContextDecisionKind.AGENT_CONTEXT_BINDING_MISMATCH,
                current,
                current,
            ),
            (
                "close with active replacement",
                AgentContextOperation.CLOSE,
                AgentContextDecisionKind.ALLOW,
                current,
                current,
            ),
            (
                "correction with active prior",
                AgentContextOperation.REBIND_CORRECTION,
                AgentContextDecisionKind.ALLOW,
                current,
                correction,
            ),
            (
                "switch with active prior",
                AgentContextOperation.SWITCH_TICKET,
                AgentContextDecisionKind.ALLOW,
                current,
                switch,
            ),
            (
                "resume with different active lease",
                AgentContextOperation.RESUME,
                AgentContextDecisionKind.ALLOW,
                current,
                different_active,
            ),
        )
        for label, operation, decision, prior, active in cases:
            payload = {
                "request_ref": f"request-invalid-decision-{label.replace(' ', '-')}",
                "operation": operation,
                "decision": decision,
                "prior_lease_result": prior,
                "active_lease": active,
            }
            json_payload = {
                "request_ref": payload["request_ref"],
                "operation": operation.value,
                "decision": decision.value,
                "prior_lease_result": None if prior is None else prior.model_dump(mode="json"),
                "active_lease": None if active is None else active.model_dump(mode="json"),
            }
            with self.subTest(decision_shape=label):
                with self.assertRaises(ValidationError):
                    AgentContextTransitionDecision.model_validate(payload)
                with self.assertRaises(ValidationError):
                    AgentContextTransitionDecision.model_validate_json(json.dumps(json_payload))

    def test_all_five_transition_rows_have_exact_lifecycle_results(self) -> None:
        current = self._lease()
        correction = self._correction_lease(current)
        switch = self._switch_lease(current)
        rows = (
            (
                AgentContextOperation.OPEN,
                self._request(request_ref="request-open-row", candidate_lease=current),
                None,
                AgentContextDecisionKind.ALLOW,
                None,
                current,
            ),
            (
                AgentContextOperation.RESUME,
                self._request(
                    request_ref="request-row-two",
                    operation=AgentContextOperation.RESUME,
                    expected_current_lease_ref=current.lease_ref,
                    expected_current_side_context_id=current.side_context_id,
                    candidate_lease=current,
                ),
                current,
                AgentContextDecisionKind.ALLOW,
                AgentContextLifecycle.ACTIVE,
                current,
            ),
            (
                AgentContextOperation.REBIND_CORRECTION,
                self._request(
                    request_ref="request-correction-row",
                    operation=AgentContextOperation.REBIND_CORRECTION,
                    expected_current_lease_ref=current.lease_ref,
                    expected_current_side_context_id=current.side_context_id,
                    candidate_lease=correction,
                ),
                current,
                AgentContextDecisionKind.ALLOW,
                AgentContextLifecycle.INVALIDATED,
                correction,
            ),
            (
                AgentContextOperation.SWITCH_TICKET,
                self._request(
                    request_ref="request-switch-row",
                    operation=AgentContextOperation.SWITCH_TICKET,
                    expected_current_lease_ref=current.lease_ref,
                    expected_current_side_context_id=current.side_context_id,
                    candidate_lease=switch,
                ),
                current,
                AgentContextDecisionKind.ALLOW,
                AgentContextLifecycle.CLOSED,
                switch,
            ),
            (
                AgentContextOperation.CLOSE,
                self._request(
                    request_ref="request-close-row",
                    operation=AgentContextOperation.CLOSE,
                    expected_current_lease_ref=current.lease_ref,
                    expected_current_side_context_id=current.side_context_id,
                ),
                current,
                AgentContextDecisionKind.ALLOW,
                AgentContextLifecycle.CLOSED,
                None,
            ),
        )
        for operation, request, prior, expected_decision, expected_lifecycle, active in rows:
            with self.subTest(operation=operation):
                decision = self._decision_for(request=request, current_lease=prior)
                self.assertEqual(expected_decision, decision.decision)
                self.assertEqual(active, decision.active_lease)
                if expected_lifecycle is None:
                    self.assertIsNone(decision.prior_lease_result)
                else:
                    self.assertIsNotNone(decision.prior_lease_result)
                    if decision.prior_lease_result is not None:
                        self.assertEqual(expected_lifecycle, decision.prior_lease_result.lifecycle)

    def test_binding_mismatches_are_independent_and_do_not_replace_current(self) -> None:
        current = self._lease()
        cases = (
            (
                "expected lease",
                current,
                "lease-r02b-other",
                current.side_context_id,
            ),
            (
                "expected side context",
                current,
                current.lease_ref,
                "side-context-r02b-other",
            ),
            ("project", self._lease(project_id="prj_fedcba9876543210"), current.lease_ref, current.side_context_id),
            ("lease", self._lease(lease_ref="lease-r02b-other"), current.lease_ref, current.side_context_id),
            ("ticket", self._lease(ticket_ref="ticket-r02b-other"), current.lease_ref, current.side_context_id),
            (
                "ticket revision",
                self._lease(ticket_revision="rev-2123456789abcdef"),
                current.lease_ref,
                current.side_context_id,
            ),
            ("receipt", self._lease(receipt_ref="receipt-r02b-other"), current.lease_ref, current.side_context_id),
            (
                "owner",
                self._lease(
                    owner_ref="owner-r02b-other",
                    actor_capability_ref="owner-r02b-other",
                ),
                current.lease_ref,
                current.side_context_id,
            ),
            ("worktree", self._lease(worktree_ref="worktree-router-03"), current.lease_ref, current.side_context_id),
            ("branch", self._lease(branch_ref="branch-router-03"), current.lease_ref, current.side_context_id),
            (
                "baseline",
                self._lease(baseline_revision="rev-2123456789abcdef"),
                current.lease_ref,
                current.side_context_id,
            ),
            (
                "control baseline",
                self._lease(control_baseline_ref="fedcba9876543210"),
                current.lease_ref,
                current.side_context_id,
            ),
            (
                "side context",
                self._lease(side_context_id="side-context-r02b-other"),
                current.lease_ref,
                current.side_context_id,
            ),
            (
                "expected return",
                self._lease(expected_return_ref="ret-agent-context-review-handoff-other"),
                current.lease_ref,
                current.side_context_id,
            ),
            (
                "artifact refs",
                self._lease(artifact_path_refs=("artifact-r02b-other",)),
                current.lease_ref,
                current.side_context_id,
            ),
        )
        for label, candidate, expected_lease, expected_side in cases:
            with self.subTest(mismatch=label):
                request = self._request(
                    request_ref=f"request-mismatch-{label.replace(' ', '-')}",
                    operation=AgentContextOperation.RESUME,
                    expected_current_lease_ref=expected_lease,
                    expected_current_side_context_id=expected_side,
                    candidate_lease=candidate,
                )
                decision = self._decision_for(request=request, current_lease=current)
                self.assertEqual(
                    AgentContextDecisionKind.AGENT_CONTEXT_BINDING_MISMATCH,
                    decision.decision,
                )
                self.assertEqual(current, decision.prior_lease_result)
                self.assertIsNone(decision.active_lease)

    def test_same_ticket_correction_requires_stable_binding_and_fresh_metadata(self) -> None:
        current = self._lease()
        valid = self._correction_lease(current)
        valid_request = self._request(
            operation=AgentContextOperation.REBIND_CORRECTION,
            expected_current_lease_ref=current.lease_ref,
            expected_current_side_context_id=current.side_context_id,
            candidate_lease=valid,
        )
        valid_decision = self._decision_for(request=valid_request, current_lease=current)
        self.assertEqual(AgentContextDecisionKind.ALLOW, valid_decision.decision)
        self.assertEqual(AgentContextLifecycle.INVALIDATED, valid_decision.prior_lease_result.lifecycle if valid_decision.prior_lease_result is not None else None)

        invalid_revision = self._lease(
            lease_ref=valid.lease_ref,
            artifact_path_refs=valid.artifact_path_refs,
            ticket_revision="rev-2123456789abcdef",
            baseline_revision=valid.baseline_revision,
            control_baseline_ref=valid.control_baseline_ref,
            side_context_id=valid.side_context_id,
            invalidation_refs=(current.side_context_id,),
        )
        invalid_lease_ref = self._lease(
            lease_ref=current.lease_ref,
            artifact_path_refs=valid.artifact_path_refs,
            baseline_revision=valid.baseline_revision,
            control_baseline_ref=valid.control_baseline_ref,
            side_context_id=valid.side_context_id,
            invalidation_refs=(current.side_context_id,),
        )
        invalid_baseline = self._lease(
            lease_ref=valid.lease_ref,
            artifact_path_refs=valid.artifact_path_refs,
            baseline_revision=current.baseline_revision,
            control_baseline_ref=valid.control_baseline_ref,
            side_context_id=valid.side_context_id,
            invalidation_refs=(current.side_context_id,),
        )
        invalidation = self._lease(
            lease_ref=valid.lease_ref,
            artifact_path_refs=valid.artifact_path_refs,
            baseline_revision=valid.baseline_revision,
            control_baseline_ref=valid.control_baseline_ref,
            side_context_id=valid.side_context_id,
            invalidation_refs=(),
        )
        for label, candidate in (
            ("ticket revision", invalid_revision),
            ("lease", invalid_lease_ref),
            ("baseline", invalid_baseline),
            ("invalidation", invalidation),
        ):
            with self.subTest(correction=label):
                decision = self._decision_for(
                    request=self._request(
                        request_ref=f"request-invalid-correction-{label.replace(' ', '-')}",
                        operation=AgentContextOperation.REBIND_CORRECTION,
                        expected_current_lease_ref=current.lease_ref,
                        expected_current_side_context_id=current.side_context_id,
                        candidate_lease=candidate,
                    ),
                    current_lease=current,
                )
                self.assertEqual(
                    AgentContextDecisionKind.AGENT_CONTEXT_BINDING_MISMATCH,
                    decision.decision,
                )
                self.assertEqual(current, decision.prior_lease_result)
                self.assertIsNone(decision.active_lease)

    def test_stale_upstream_and_requirement_precedence_are_exact(self) -> None:
        current = self._lease()
        closed = self._lease(lifecycle=AgentContextLifecycle.CLOSED)
        invalidated = self._lease(lifecycle=AgentContextLifecycle.INVALIDATED)
        resume_request = self._request(
            operation=AgentContextOperation.RESUME,
            expected_current_lease_ref=current.lease_ref,
            expected_current_side_context_id=current.side_context_id,
            candidate_lease=current,
        )
        for stale in (None, closed, invalidated):
            with self.subTest(stale=stale):
                decision = self._decision_for(request=resume_request, current_lease=stale)
                self.assertEqual(AgentContextDecisionKind.AGENT_CONTEXT_STALE, decision.decision)
                self.assertEqual(stale, decision.prior_lease_result)
                self.assertIsNone(decision.active_lease)

        correction = self._correction_lease(current)
        switch = self._switch_lease(current)
        for stale in (closed, invalidated):
            for operation, candidate in (
                (AgentContextOperation.RESUME, current),
                (AgentContextOperation.REBIND_CORRECTION, correction),
                (AgentContextOperation.SWITCH_TICKET, switch),
                (AgentContextOperation.CLOSE, None),
            ):
                with self.subTest(stale=stale.lifecycle, operation=operation):
                    decision = self._decision_for(
                        request=self._request(
                            request_ref=f"request-stale-{operation.value.replace('resume', 'row-two').replace('_', '-')}",
                            operation=operation,
                            expected_current_lease_ref=stale.lease_ref,
                            expected_current_side_context_id=stale.side_context_id,
                            candidate_lease=candidate,
                        ),
                        current_lease=stale,
                    )
                    self.assertEqual(
                        AgentContextDecisionKind.AGENT_CONTEXT_STALE,
                        decision.decision,
                    )
                    self.assertEqual(stale, decision.prior_lease_result)
                    self.assertIsNone(decision.active_lease)

        missing = self._decision_for(
            request=self._request(
                request_ref="request-upstream-missing",
                upstream_state=AgentContextUpstreamState.MISSING,
                candidate_lease=current,
            ),
            current_lease=current,
        )
        self.assertEqual(AgentContextDecisionKind.UPSTREAM_DECISION_REQUIRED, missing.decision)
        self.assertEqual(current, missing.prior_lease_result)
        self.assertIsNone(missing.active_lease)

        changed = self._decision_for(
            request=self._request(
                request_ref="request-requirement-changed",
                upstream_state=AgentContextUpstreamState.REQUIREMENT_CHANGED,
                candidate_lease=current,
            ),
            current_lease=current,
        )
        self.assertEqual(AgentContextDecisionKind.REQUIREMENT_CHANGED, changed.decision)
        self.assertIsNotNone(changed.prior_lease_result)
        if changed.prior_lease_result is not None:
            self.assertEqual(AgentContextLifecycle.INVALIDATED, changed.prior_lease_result.lifecycle)
        self.assertIsNone(changed.active_lease)

    def test_reversal_rows_reject_changed_revision_replay_and_reused_switch_context(self) -> None:
        current = self._lease()
        changed_revision = self._lease(
            lease_ref="lease-r02b-correction",
            artifact_path_refs=("artifact-r02b-correction",),
            ticket_revision="rev-2123456789abcdef",
            baseline_revision="rev-2123456789abcdef",
            control_baseline_ref="1123456789abcdef",
            side_context_id="side-context-r02b-correction",
            invalidation_refs=(current.side_context_id,),
        )
        changed_revision_decision = self._decision_for(
            request=self._request(
                request_ref="request-reversal-revision",
                operation=AgentContextOperation.REBIND_CORRECTION,
                expected_current_lease_ref=current.lease_ref,
                expected_current_side_context_id=current.side_context_id,
                candidate_lease=changed_revision,
            ),
            current_lease=current,
        )
        self.assertEqual(
            AgentContextDecisionKind.AGENT_CONTEXT_BINDING_MISMATCH,
            changed_revision_decision.decision,
        )

        closed = self._lease(lifecycle=AgentContextLifecycle.CLOSED)
        replay = self._decision_for(
            request=self._request(
                request_ref="request-reversal-replay",
                operation=AgentContextOperation.RESUME,
                expected_current_lease_ref=closed.lease_ref,
                expected_current_side_context_id=closed.side_context_id,
                candidate_lease=current,
            ),
            current_lease=closed,
        )
        self.assertEqual(AgentContextDecisionKind.AGENT_CONTEXT_STALE, replay.decision)

        reused_side = self._lease(
            lease_ref="lease-r02b-switch-reused-side",
            artifact_path_refs=("artifact-r02b-switch-reused-side",),
            ticket_ref="ticket-r02b-next",
            ticket_revision="rev-2123456789abcdef",
            receipt_ref="receipt-r02b-next",
            branch_ref="branch-router-03",
            baseline_revision="rev-3123456789abcdef",
            control_baseline_ref="2123456789abcdef",
            side_context_id=current.side_context_id,
            expected_return_ref="ret-agent-context-review-handoff-next",
            invalidation_refs=(),
        )
        reused_side_decision = self._decision_for(
            request=self._request(
                request_ref="request-reversal-side-context",
                operation=AgentContextOperation.SWITCH_TICKET,
                expected_current_lease_ref=current.lease_ref,
                expected_current_side_context_id=current.side_context_id,
                candidate_lease=reused_side,
            ),
            current_lease=current,
        )
        self.assertEqual(
            AgentContextDecisionKind.AGENT_CONTEXT_BINDING_MISMATCH,
            reused_side_decision.decision,
        )


if __name__ == "__main__":
    unittest.main()
