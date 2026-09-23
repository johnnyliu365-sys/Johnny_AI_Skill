"""Pure admission of independently resolved test evidence for formal review."""

from __future__ import annotations

from collections.abc import Sequence

from .test_engineer_contracts import (
    IndependentTestReport,
    ReviewAdmissionDecision,
    ReviewAdmissionReason,
    ReviewAdmissionRequest,
    ReviewAdmissionStatus,
    ResolvedTestEvidence,
    TestCleanup,
    TestEvidenceResolver,
    TestCellObservation,
    TestVerdict,
    UnavailableTestEvidence,
)


class ReviewAdmissionGate:
    """Reduce one trusted evidence resolution into a fail-closed decision."""

    def __init__(self, *, resolver: TestEvidenceResolver | None = None) -> None:
        self._resolver = resolver

    def evaluate(self, request: ReviewAdmissionRequest) -> ReviewAdmissionDecision:
        """Resolve and validate the exact report requested by the review transition."""

        resolver = self._resolver
        if resolver is None:
            return self._denied(TestVerdict.BLOCKED, ReviewAdmissionReason.EVIDENCE_UNAVAILABLE)
        try:
            resolution = resolver.resolve(request=request)
        except Exception:
            return self._denied(TestVerdict.INCONCLUSIVE, ReviewAdmissionReason.RESOLVER_FAILURE)
        if isinstance(resolution, UnavailableTestEvidence):
            return self._denied(TestVerdict.BLOCKED, ReviewAdmissionReason.EVIDENCE_UNAVAILABLE)
        return self._evaluate_resolved(request=request, resolution=resolution)

    def _evaluate_resolved(
        self,
        *,
        request: ReviewAdmissionRequest,
        resolution: ResolvedTestEvidence,
    ) -> ReviewAdmissionDecision:
        authority = resolution.authority
        report = resolution.report
        if (
            request.project_ref != authority.binding.project_ref
            or request.scope_ref != authority.binding.scope_ref
            or report.binding != authority.binding
        ):
            return self._denied(TestVerdict.INCONCLUSIVE, ReviewAdmissionReason.BINDING_MISMATCH)
        if not (
            request.report_ref == authority.expected_report_ref
            and report.report_ref == authority.expected_report_ref
        ):
            return self._denied(TestVerdict.INCONCLUSIVE, ReviewAdmissionReason.REPORT_MISMATCH)
        if not self._has_exact_cell_coverage(authority.expected_cell_ids, report):
            return self._denied(
                TestVerdict.INCONCLUSIVE,
                ReviewAdmissionReason.CELL_COVERAGE_MISMATCH,
            )

        reduced = self._reduce(report.cells)
        if reduced is TestVerdict.FAIL:
            return self._denied(TestVerdict.FAIL, ReviewAdmissionReason.TESTS_FAILED)
        if report.declared_verdict is not reduced:
            return self._denied(TestVerdict.INCONCLUSIVE, ReviewAdmissionReason.VERDICT_MISMATCH)
        if reduced is TestVerdict.BLOCKED:
            return self._denied(TestVerdict.BLOCKED, ReviewAdmissionReason.TESTS_BLOCKED)
        if reduced is TestVerdict.INCONCLUSIVE:
            return self._denied(TestVerdict.INCONCLUSIVE, ReviewAdmissionReason.TESTS_INCONCLUSIVE)
        if report.cleanup is TestCleanup.UNCONFIRMED or (
            authority.cleanup_required and report.cleanup is not TestCleanup.CONFIRMED
        ):
            return self._denied(TestVerdict.BLOCKED, ReviewAdmissionReason.CLEANUP_INCOMPLETE)
        return ReviewAdmissionDecision(
            status=ReviewAdmissionStatus.ADMITTED,
            verdict=TestVerdict.PASS,
            reason=None,
        )

    @staticmethod
    def _has_exact_cell_coverage(
        expected_cell_ids: tuple[str, ...],
        report: IndependentTestReport,
    ) -> bool:
        observed = tuple(cell.cell_id for cell in report.cells)
        return len(observed) == len(expected_cell_ids) and set(observed) == set(expected_cell_ids)

    @staticmethod
    def _reduce(cells: Sequence[TestCellObservation]) -> TestVerdict:
        verdicts = tuple(cell.verdict for cell in cells)
        if TestVerdict.FAIL in verdicts:
            return TestVerdict.FAIL
        if TestVerdict.BLOCKED in verdicts:
            return TestVerdict.BLOCKED
        if TestVerdict.INCONCLUSIVE in verdicts:
            return TestVerdict.INCONCLUSIVE
        return TestVerdict.PASS

    @staticmethod
    def _denied(
        verdict: TestVerdict,
        reason: ReviewAdmissionReason,
    ) -> ReviewAdmissionDecision:
        return ReviewAdmissionDecision(
            status=ReviewAdmissionStatus.DENIED,
            verdict=verdict,
            reason=reason,
        )


__all__ = ("ReviewAdmissionGate",)
