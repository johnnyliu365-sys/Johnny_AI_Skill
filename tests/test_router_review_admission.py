"""Router choke-point tests for bound review evidence."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from library.workflow_router import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    CompletionActionKind,
    CompletionEvidence,
    DeliveryStage,
    HandoffArtifactReference,
    HandoffConsumerFingerprint,
    ProcessStage,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    build_router_poc_profile,
)
from library.workflow_router.contracts import ModelRole, ModelRoleAssignment, RoleActivityState
from library.workflow_router.profile import ProjectWorkflowProfile
from library.workflow_router.test_engineer_contracts import (
    ResolvedTestEvidence,
    TestCleanup,
    TestEvidenceUnavailableReason,
    UnavailableTestEvidence,
)

_TESTS_DIRECTORY = str(Path(__file__).resolve().parent)
if _TESTS_DIRECTORY not in sys.path:
    sys.path.insert(0, _TESTS_DIRECTORY)

from test_review_admission import (
    StaticEvidenceResolver,
    _authority,
    _binding,
    _cell,
    _report,
)


_DIGEST = "sha256_" + "a" * 64


class RouterReviewAdmissionTests(unittest.TestCase):
    """Ensure every review entry and handoff path uses the same evidence gate."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.ticket = ArtifactRef(
            kind=ArtifactKind.TICKET,
            identifier="router-review-ticket",
            uri="ticket://router-review/ticket",
            revision="1",
        )
        self.scope_ref = "review-scope"
        self.report_ref = "review-report"
        binding = _binding(
            scope_ref=self.scope_ref,
            project_ref="router-framework-poc",
            ticket_ref="router-review-ticket",
        )
        authority = _authority(
            binding,
            expected_report_ref=self.report_ref,
            expected_cell_ids=("cell-pass",),
            cleanup_required=True,
        )
        report = _report(
            binding,
            report_ref=self.report_ref,
            cells=(_cell("cell-pass"),),
            cleanup=TestCleanup.CONFIRMED,
        )
        self.resolver = StaticEvidenceResolver(ResolvedTestEvidence(authority=authority, report=report))

    def _state(self, stage: ProcessStage) -> RouterState:
        return RouterState(
            project_id="router-framework-poc",
            stage=stage,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.ticket,),
            review_scope_ref=self.scope_ref,
        )

    def _event(
        self,
        kind: RouterEventKind,
        *,
        completion_evidence: CompletionEvidence | None = None,
        report_ref: str | None = None,
    ) -> RouterEvent:
        return RouterEvent(
            event_id=f"event-review-{kind.value}",
            kind=kind,
            completion_evidence=completion_evidence,
            test_report_ref=report_ref,
        )

    def _review_completion(self) -> CompletionEvidence:
        return CompletionEvidence(
            completion_id="completion-review",
            action_kind=CompletionActionKind.REVIEW,
            artifact_references=(
                HandoffArtifactReference(
                    artifact_id="review-artifact",
                    revision_digest="rev-0123456789abcdef",
                    source_span_id="review-span",
                    side_context_id="review-context",
                    consumer_fingerprint=HandoffConsumerFingerprint(
                        agent_profile_id="review-agent",
                        profile_version="review-profile",
                        worktree_fingerprint="review-worktree",
                        execution_fingerprint="review-execution",
                    ),
                ),
            ),
            verification_references=("review-verification",),
            evidence_digest=_DIGEST,
            commit_digest="git_0123456789abcdef",
        )

    def test_bare_smoke_pass_is_refused_before_review(self) -> None:
        decision = RouterEngine().decide(
            state=self._state(ProcessStage.SMOKE_TEST),
            event=self._event(RouterEventKind.VALIDATION_PASSED),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual((), decision.eligible_capabilities)
        self.assertEqual("test_review_not_admitted", decision.blockers[0].code.value)

    def test_complete_bound_report_admits_smoke_review_entry(self) -> None:
        decision = RouterEngine(test_evidence_resolver=self.resolver).decide(
            state=self._state(ProcessStage.SMOKE_TEST),
            event=self._event(
                RouterEventKind.VALIDATION_PASSED,
                report_ref=self.report_ref,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, decision.outcome)
        self.assertEqual(ProcessStage.REVIEW, decision.next_stage)
        self.assertEqual(1, self.resolver.calls)
        request = self.resolver.last_request
        if request is None:
            self.fail("the resolver must receive a bound request")
        self.assertEqual(self.report_ref, request.report_ref)

    def test_review_handoff_also_requires_bound_report(self) -> None:
        bare = RouterEngine().decide(
            state=self._state(ProcessStage.REVIEW),
            event=self._event(
                RouterEventKind.ACTION_COMPLETED,
                completion_evidence=self._review_completion(),
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, bare.outcome)
        self.assertEqual((), bare.eligible_capabilities)
        self.assertEqual("test_review_not_admitted", bare.blockers[0].code.value)

        admitted = RouterEngine(test_evidence_resolver=self.resolver).decide(
            state=self._state(ProcessStage.REVIEW),
            event=self._event(
                RouterEventKind.ACTION_COMPLETED,
                completion_evidence=self._review_completion(),
                report_ref=self.report_ref,
            ),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, admitted.outcome)
        self.assertEqual(ProcessStage.HANDOFF, admitted.next_stage)

    def test_custom_review_entry_and_unrelated_routes_use_distinct_behavior(self) -> None:
        audit_rule = self.profile.rule_for(
            current_stage=ProcessStage.GRILL,
            event_kind=RouterEventKind.AUDIT_COMPLETED,
        )
        if audit_rule is None:
            self.fail("the profile must declare the audit review entry")
        custom_rule_payload = audit_rule.model_dump()
        custom_rule_payload["current_stage"] = ProcessStage.ARCHITECTURE
        custom_rule = type(audit_rule).model_validate(custom_rule_payload)
        custom_profile_payload = self.profile.model_dump()
        custom_profile_payload["transition_rules"] = self.profile.transition_rules + (custom_rule,)
        custom_profile = ProjectWorkflowProfile.model_validate(
            custom_profile_payload
        )
        custom_state = self._state(ProcessStage.ARCHITECTURE)
        custom_event = self._event(
            RouterEventKind.AUDIT_COMPLETED,
            report_ref=self.report_ref,
        )
        for label, engine in (
            ("missing", RouterEngine()),
            (
                "unavailable",
                RouterEngine(
                    test_evidence_resolver=StaticEvidenceResolver(
                        UnavailableTestEvidence(
                            reason=TestEvidenceUnavailableReason.NOT_FOUND,
                        )
                    )
                ),
            ),
        ):
            for entry, state, profile in (
                ("audit", self._state(ProcessStage.GRILL), self.profile),
                ("custom-audit", custom_state, custom_profile),
            ):
                with self.subTest(entry=entry, admission=label):
                    refused = engine.decide(
                        state=state,
                        event=custom_event,
                        profile=profile,
                    )
                    self.assertEqual(RouterOutcome.SUSPEND, refused.outcome)
                    self.assertEqual((), refused.eligible_capabilities)
                    self.assertEqual("test_review_not_admitted", refused.blockers[0].code.value)

        custom_decision = RouterEngine(test_evidence_resolver=self.resolver).decide(
            state=custom_state,
            event=custom_event,
            profile=custom_profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, custom_decision.outcome)
        self.assertEqual(ProcessStage.REVIEW, custom_decision.next_stage)

        unrelated = RouterEngine().decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(
                    ArtifactRef(
                        kind=ArtifactKind.PROJECT_GOAL,
                        identifier="router-review-goal",
                        uri="project://router-review/goal",
                        revision="1",
                    ),
                ),
            ),
            event=self._event(RouterEventKind.INTAKE),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, unrelated.outcome)
        self.assertEqual(ProcessStage.WAYFINDER, unrelated.next_stage)

    def test_test_engineer_role_is_distinct_and_optional(self) -> None:
        default_roles = {assignment.role for assignment in self.profile.model_role_assignments}
        self.assertNotIn(ModelRole.TEST_ENGINEER, default_roles)
        test_engineer = ModelRoleAssignment(
            project_profile_ref=self.profile.profile_id,
            role=ModelRole.TEST_ENGINEER,
            model_ref="model-test-engineer",
            capability_refs=("cap-test-engineer",),
            activity_state=RoleActivityState.SLEEPING,
            evidence_refs=("evidence-test-engineer",),
        )
        explicit_payload = self.profile.model_dump()
        explicit_payload["model_role_assignments"] = self.profile.model_role_assignments + (
            test_engineer,
        )
        explicit_profile = ProjectWorkflowProfile.model_validate(explicit_payload)
        self.assertIn(
            ModelRole.TEST_ENGINEER,
            {assignment.role for assignment in explicit_profile.model_role_assignments},
        )

        missing_core_payload = self.profile.model_dump()
        missing_core_payload["model_role_assignments"] = tuple(
            assignment
            for assignment in self.profile.model_role_assignments
            if assignment.role is not ModelRole.RESEARCH_HELPER
        )
        with self.assertRaises(ValueError):
            ProjectWorkflowProfile.model_validate(missing_core_payload)

        duplicate_engineer_payload = explicit_profile.model_dump()
        duplicate_engineer_payload["model_role_assignments"] = explicit_profile.model_role_assignments + (
            ModelRoleAssignment(
                project_profile_ref=self.profile.profile_id,
                role=ModelRole.TEST_ENGINEER,
                model_ref="model-test-engineer-2",
                capability_refs=("cap-test-engineer-2",),
                activity_state=RoleActivityState.SLEEPING,
                evidence_refs=("evidence-test-engineer-2",),
            ),
        )
        with self.assertRaises(ValueError):
            ProjectWorkflowProfile.model_validate(duplicate_engineer_payload)


if __name__ == "__main__":
    unittest.main()
