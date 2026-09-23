"""Router choke-point tests for bound review evidence."""

from __future__ import annotations

import unittest

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
from library.workflow_router.test_engineer_contracts import (
    IndependentTestReport,
    ReviewAdmissionRequest,
    ResolvedTestEvidence,
    TestBinding,
    TestCleanup,
    TestReviewAuthority,
    TestVerdict,
)
from library.workflow_router.test_engineer_contracts import TestCellObservation, TestEvidenceResolution


_DIGEST = "sha256_" + "a" * 64
_OTHER_DIGEST = "sha256_" + "b" * 64
_CANDIDATE = "1234567890abcdef1234567890abcdef12345678"


class RouterEvidenceResolver:
    """Small typed resolver fixture for Router entry-point tests."""

    def __init__(self, result: TestEvidenceResolution) -> None:
        self.result = result
        self.calls = 0
        self.last_request: ReviewAdmissionRequest | None = None

    def resolve(self, *, request: ReviewAdmissionRequest) -> TestEvidenceResolution:
        self.calls += 1
        self.last_request = request
        return self.result


def _router_cell(cell_id: str) -> TestCellObservation:
    return TestCellObservation(
        cell_id=cell_id,
        verdict=TestVerdict.PASS,
        evidence_ref=f"evidence-{cell_id}",
        evidence_digest=_DIGEST,
        reason_ref=None,
    )


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
        binding = TestBinding(
            scope_ref=self.scope_ref,
            project_ref="router-framework-poc",
            ticket_ref="router-review-ticket",
            candidate_sha=_CANDIDATE,
            test_suite_digest=_DIGEST,
            plan_digest=_OTHER_DIGEST,
            environment_digest=_DIGEST,
            implementer_id="router-implementer",
            engineer_id="router-engineer",
            reviewer_id="router-reviewer",
        )
        authority = TestReviewAuthority(
            binding=binding,
            expected_report_ref=self.report_ref,
            expected_cell_ids=("cell-pass",),
            cleanup_required=True,
        )
        report = IndependentTestReport(
            report_ref=self.report_ref,
            binding=binding,
            declared_verdict=TestVerdict.PASS,
            cells=(_router_cell("cell-pass"),),
            cleanup=TestCleanup.CONFIRMED,
        )
        self.resolver = RouterEvidenceResolver(
            ResolvedTestEvidence(authority=authority, report=report)
        )

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
        custom_profile = self.profile.model_copy(
            update={
                "transition_rules": self.profile.transition_rules
                + (
                    audit_rule.model_copy(
                        update={"current_stage": ProcessStage.ARCHITECTURE},
                    ),
                )
            }
        )
        custom_state = self._state(ProcessStage.ARCHITECTURE)
        custom_event = self._event(
            RouterEventKind.AUDIT_COMPLETED,
            report_ref=self.report_ref,
        )
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


if __name__ == "__main__":
    unittest.main()
