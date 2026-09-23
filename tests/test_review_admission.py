"""Pure review-admission reduction tests with a typed evidence resolver fake."""

from __future__ import annotations

import unittest

from library.workflow_router.review_admission import ReviewAdmissionGate
from library.workflow_router.test_engineer_contracts import (
    IndependentTestReport,
    ReviewAdmissionDecision,
    ReviewAdmissionReason,
    ReviewAdmissionRequest,
    ReviewAdmissionStatus,
    ResolvedTestEvidence,
    TestBinding,
    TestCellObservation,
    TestCleanup,
    TestEvidenceResolution,
    TestEvidenceUnavailableReason,
    TestReviewAuthority,
    TestVerdict,
    UnavailableTestEvidence,
)


_CANDIDATE = "1234567890abcdef1234567890abcdef12345678"
_DIGEST = "sha256_" + "a" * 64
_OTHER_DIGEST = "sha256_" + "b" * 64


class StaticEvidenceResolver:
    """Typed fake resolver used only to exercise the pure admission gate."""

    def __init__(self, result: TestEvidenceResolution, *, raises: bool = False) -> None:
        self.result = result
        self.raises = raises
        self.calls = 0
        self.last_request: ReviewAdmissionRequest | None = None

    def resolve(self, *, request: ReviewAdmissionRequest) -> TestEvidenceResolution:
        self.calls += 1
        self.last_request = request
        if self.raises:
            raise RuntimeError("resolver failure is deliberately opaque")
        return self.result


def _binding(*, suffix: str = "") -> TestBinding:
    return TestBinding(
        scope_ref=f"scope-review{suffix}",
        project_ref=f"project-review{suffix}",
        ticket_ref=f"ticket-review{suffix}",
        candidate_sha=_CANDIDATE,
        test_suite_digest=_DIGEST,
        plan_digest=_OTHER_DIGEST,
        environment_digest=_DIGEST,
        implementer_id=f"implementer-review{suffix}",
        engineer_id=f"engineer-review{suffix}",
        reviewer_id=f"reviewer-review{suffix}",
    )


def _cell(
    cell_id: str,
    verdict: TestVerdict = TestVerdict.PASS,
    reason_ref: str | None = None,
) -> TestCellObservation:
    return TestCellObservation(
        cell_id=cell_id,
        verdict=verdict,
        evidence_ref=f"evidence-{cell_id}",
        evidence_digest=_DIGEST,
        reason_ref=reason_ref,
    )


def _authority(
    binding: TestBinding,
    *,
    expected_report_ref: str = "report-review",
    expected_cell_ids: tuple[str, ...] = ("cell-pass",),
    cleanup_required: bool = True,
) -> TestReviewAuthority:
    return TestReviewAuthority(
        binding=binding,
        expected_report_ref=expected_report_ref,
        expected_cell_ids=expected_cell_ids,
        cleanup_required=cleanup_required,
    )


def _report(
    binding: TestBinding,
    *,
    report_ref: str = "report-review",
    declared_verdict: TestVerdict = TestVerdict.PASS,
    cells: tuple[TestCellObservation, ...] = (),
    cleanup: TestCleanup = TestCleanup.CONFIRMED,
) -> IndependentTestReport:
    return IndependentTestReport(
        report_ref=report_ref,
        binding=binding,
        declared_verdict=declared_verdict,
        cells=cells,
        cleanup=cleanup,
    )


def _request(
    *,
    project_ref: str = "project-review",
    scope_ref: str = "scope-review",
    report_ref: str = "report-review",
) -> ReviewAdmissionRequest:
    return ReviewAdmissionRequest(
        project_ref=project_ref,
        scope_ref=scope_ref,
        report_ref=report_ref,
    )


def _found(
    *,
    binding: TestBinding | None = None,
    authority: TestReviewAuthority | None = None,
    report: IndependentTestReport | None = None,
) -> ResolvedTestEvidence:
    selected_binding = binding or _binding()
    selected_authority = authority or _authority(selected_binding)
    selected_report = report or _report(
        selected_binding,
        cells=(_cell("cell-pass"),),
    )
    return ResolvedTestEvidence(authority=selected_authority, report=selected_report)


class ReviewAdmissionTests(unittest.TestCase):
    """Cover identity, coverage, reduction, cleanup and resolver failure gates."""

    def _evaluate(
        self,
        result: TestEvidenceResolution,
        request: ReviewAdmissionRequest | None = None,
        *,
        raises: bool = False,
    ) -> tuple[ReviewAdmissionDecision, StaticEvidenceResolver]:
        resolver = StaticEvidenceResolver(result, raises=raises)
        decision = ReviewAdmissionGate(resolver=resolver).evaluate(request or _request())
        return decision, resolver

    def test_unavailable_and_throwing_resolvers_fail_closed_without_exception_text(self) -> None:
        unavailable = UnavailableTestEvidence(
            reason=TestEvidenceUnavailableReason.UNQUALIFIED
        )
        unavailable_decision, unavailable_resolver = self._evaluate(unavailable)
        self.assertEqual(ReviewAdmissionStatus.DENIED, unavailable_decision.status)
        self.assertEqual(TestVerdict.BLOCKED, unavailable_decision.verdict)
        self.assertEqual(ReviewAdmissionReason.EVIDENCE_UNAVAILABLE, unavailable_decision.reason)
        self.assertEqual(1, unavailable_resolver.calls)

        throwing_decision, throwing_resolver = self._evaluate(_found(), raises=True)
        self.assertEqual(ReviewAdmissionStatus.DENIED, throwing_decision.status)
        self.assertEqual(TestVerdict.INCONCLUSIVE, throwing_decision.verdict)
        self.assertEqual(ReviewAdmissionReason.RESOLVER_FAILURE, throwing_decision.reason)
        self.assertEqual(1, throwing_resolver.calls)

        no_resolver = ReviewAdmissionGate().evaluate(_request())
        self.assertEqual(TestVerdict.BLOCKED, no_resolver.verdict)
        self.assertEqual(ReviewAdmissionReason.EVIDENCE_UNAVAILABLE, no_resolver.reason)

    def test_reduction_precedence_and_complete_pass_admission(self) -> None:
        binding = _binding()
        authority = _authority(binding, expected_cell_ids=("cell-pass",))
        cases = (
            (TestVerdict.PASS, TestVerdict.PASS, TestCleanup.CONFIRMED, ReviewAdmissionStatus.ADMITTED, None),
            (
                TestVerdict.FAIL,
                TestVerdict.FAIL,
                TestCleanup.UNCONFIRMED,
                ReviewAdmissionStatus.DENIED,
                ReviewAdmissionReason.TESTS_FAILED,
            ),
            (
                TestVerdict.BLOCKED,
                TestVerdict.BLOCKED,
                TestCleanup.CONFIRMED,
                ReviewAdmissionStatus.DENIED,
                ReviewAdmissionReason.TESTS_BLOCKED,
            ),
            (
                TestVerdict.INCONCLUSIVE,
                TestVerdict.INCONCLUSIVE,
                TestCleanup.CONFIRMED,
                ReviewAdmissionStatus.DENIED,
                ReviewAdmissionReason.TESTS_INCONCLUSIVE,
            ),
        )
        for cell_verdict, declared_verdict, cleanup, status, reason in cases:
            with self.subTest(verdict=cell_verdict):
                report = _report(
                    binding,
                    declared_verdict=declared_verdict,
                    cells=(
                        _cell(
                            "cell-pass",
                            cell_verdict,
                            None if cell_verdict is TestVerdict.PASS else "reason-cell",
                        ),
                    ),
                    cleanup=cleanup,
                )
                decision, _ = self._evaluate(
                    ResolvedTestEvidence(authority=authority, report=report)
                )
                self.assertEqual(status, decision.status)
                self.assertEqual(reason, decision.reason)
                self.assertEqual(cell_verdict, decision.verdict)

        mixed_report = _report(
            binding,
            declared_verdict=TestVerdict.FAIL,
            cells=(
                _cell("cell-pass", TestVerdict.BLOCKED, "reason-blocked"),
                _cell("cell-fail", TestVerdict.FAIL, "reason-fail"),
                _cell("cell-inconclusive", TestVerdict.INCONCLUSIVE, "reason-inconclusive"),
            ),
        )
        mixed_authority = _authority(
            binding,
            expected_cell_ids=("cell-pass", "cell-fail", "cell-inconclusive"),
        )
        mixed_decision, _ = self._evaluate(
            ResolvedTestEvidence(authority=mixed_authority, report=mixed_report)
        )
        self.assertEqual(TestVerdict.FAIL, mixed_decision.verdict)
        self.assertEqual(ReviewAdmissionReason.TESTS_FAILED, mixed_decision.reason)

    def test_binding_and_report_identity_mismatches_are_distinct(self) -> None:
        binding = _binding()
        authority = _authority(binding)
        report_with_foreign_binding = _report(_binding(suffix="-foreign"), cells=(_cell("cell-pass"),))
        binding_decision, _ = self._evaluate(
            ResolvedTestEvidence(authority=authority, report=report_with_foreign_binding)
        )
        self.assertEqual(ReviewAdmissionReason.BINDING_MISMATCH, binding_decision.reason)

        report = _report(binding, cells=(_cell("cell-pass"),))
        stale_authority = _authority(binding, expected_report_ref="report-current")
        stale_request = _request(report_ref="report-old")
        report_decision, _ = self._evaluate(
            ResolvedTestEvidence(authority=stale_authority, report=report), stale_request
        )
        self.assertEqual(ReviewAdmissionReason.REPORT_MISMATCH, report_decision.reason)

        scope_decision, _ = self._evaluate(
            ResolvedTestEvidence(authority=authority, report=report),
            _request(scope_ref="scope-foreign"),
        )
        self.assertEqual(ReviewAdmissionReason.BINDING_MISMATCH, scope_decision.reason)

    def test_exact_cell_coverage_rejects_empty_missing_extra_and_duplicate(self) -> None:
        binding = _binding()
        authority = _authority(binding, expected_cell_ids=("cell-one", "cell-two"))
        reports = (
            _report(binding, cells=()),
            _report(binding, cells=(_cell("cell-one"),)),
            _report(binding, cells=(_cell("cell-one"), _cell("cell-extra"))),
            _report(binding, cells=(_cell("cell-one"), _cell("cell-one"))),
        )
        for report in reports:
            with self.subTest(cells=tuple(cell.cell_id for cell in report.cells)):
                decision, _ = self._evaluate(
                    ResolvedTestEvidence(authority=authority, report=report)
                )
                self.assertEqual(
                    ReviewAdmissionReason.CELL_COVERAGE_MISMATCH,
                    decision.reason,
                )

    def test_declared_verdict_and_cleanup_guards_never_admit(self) -> None:
        binding = _binding()
        authority = _authority(binding, cleanup_required=True)
        wrong_verdict = _report(
            binding,
            declared_verdict=TestVerdict.FAIL,
            cells=(_cell("cell-pass"),),
        )
        wrong_decision, _ = self._evaluate(
            ResolvedTestEvidence(authority=authority, report=wrong_verdict)
        )
        self.assertEqual(TestVerdict.INCONCLUSIVE, wrong_decision.verdict)
        self.assertEqual(ReviewAdmissionReason.VERDICT_MISMATCH, wrong_decision.reason)

        for cleanup in (TestCleanup.NOT_REQUIRED, TestCleanup.UNCONFIRMED):
            with self.subTest(cleanup=cleanup):
                incomplete = _report(
                    binding,
                    cells=(_cell("cell-pass"),),
                    cleanup=cleanup,
                )
                incomplete_decision, _ = self._evaluate(
                    ResolvedTestEvidence(authority=authority, report=incomplete)
                )
                self.assertEqual(TestVerdict.BLOCKED, incomplete_decision.verdict)
                self.assertEqual(
                    ReviewAdmissionReason.CLEANUP_INCOMPLETE,
                    incomplete_decision.reason,
                )

        optional_cleanup_authority = _authority(binding, cleanup_required=False)
        optional_report = _report(
            binding,
            cells=(_cell("cell-pass"),),
            cleanup=TestCleanup.NOT_REQUIRED,
        )
        optional_decision, _ = self._evaluate(
            ResolvedTestEvidence(
                authority=optional_cleanup_authority,
                report=optional_report,
            )
        )
        self.assertEqual(ReviewAdmissionStatus.ADMITTED, optional_decision.status)


if __name__ == "__main__":
    unittest.main()
