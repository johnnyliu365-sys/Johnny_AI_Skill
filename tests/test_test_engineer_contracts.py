"""Constructor and JSON contract tests for independent test evidence."""

from __future__ import annotations

import unittest

from pydantic import TypeAdapter, ValidationError

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


class TestEngineerContractTests(unittest.TestCase):
    """Exercise every phase-1 public DTO through normal validation paths."""

    def _binding(self) -> TestBinding:
        return TestBinding(
            scope_ref="scope-review",
            project_ref="project-review",
            ticket_ref="ticket-review",
            candidate_sha=_CANDIDATE,
            test_suite_digest=_DIGEST,
            plan_digest=_OTHER_DIGEST,
            environment_digest=_DIGEST,
            implementer_id="implementer-review",
            engineer_id="engineer-review",
            reviewer_id="reviewer-review",
        )

    def _cell(
        self,
        cell_id: str = "cell-pass",
        verdict: TestVerdict = TestVerdict.PASS,
        reason_ref: str | None = None,
    ) -> TestCellObservation:
        return TestCellObservation(
            cell_id=cell_id,
            verdict=verdict,
            evidence_ref="evidence-review",
            evidence_digest=_DIGEST,
            reason_ref=reason_ref,
        )

    def _authority(self) -> TestReviewAuthority:
        return TestReviewAuthority(
            binding=self._binding(),
            expected_report_ref="report-review",
            expected_cell_ids=("cell-pass",),
            cleanup_required=True,
        )

    def _report(
        self,
        *,
        report_ref: str = "report-review",
        declared_verdict: TestVerdict = TestVerdict.PASS,
        cells: tuple[TestCellObservation, ...] = (),
        cleanup: TestCleanup = TestCleanup.CONFIRMED,
    ) -> IndependentTestReport:
        return IndependentTestReport(
            report_ref=report_ref,
            binding=self._binding(),
            declared_verdict=declared_verdict,
            cells=cells,
            cleanup=cleanup,
        )

    def test_enum_values_are_exact_uppercase_states(self) -> None:
        self.assertEqual(
            ("PASS", "FAIL", "BLOCKED", "INCONCLUSIVE"),
            tuple(value.value for value in TestVerdict),
        )
        self.assertEqual(
            ("NOT_REQUIRED", "CONFIRMED", "UNCONFIRMED"),
            tuple(value.value for value in TestCleanup),
        )
        self.assertEqual(
            ("NOT_FOUND", "UNAUTHORIZED", "UNQUALIFIED"),
            tuple(value.value for value in TestEvidenceUnavailableReason),
        )
        self.assertEqual(
            ("ADMITTED", "DENIED"),
            tuple(value.value for value in ReviewAdmissionStatus),
        )
        self.assertEqual(
            (
                "EVIDENCE_UNAVAILABLE",
                "RESOLVER_FAILURE",
                "BINDING_MISMATCH",
                "REPORT_MISMATCH",
                "CELL_COVERAGE_MISMATCH",
                "VERDICT_MISMATCH",
                "CLEANUP_INCOMPLETE",
                "TESTS_FAILED",
                "TESTS_BLOCKED",
                "TESTS_INCONCLUSIVE",
            ),
            tuple(value.value for value in ReviewAdmissionReason),
        )

    def test_ordinary_constructors_and_json_round_trip(self) -> None:
        binding = self._binding()
        passing = self._cell()
        failing = self._cell(
            cell_id="cell-fail",
            verdict=TestVerdict.FAIL,
            reason_ref="reason-failure",
        )
        authority = self._authority()
        empty_report = self._report()
        duplicate_cells_report = self._report(cells=(passing, passing))
        report = self._report(
            declared_verdict=TestVerdict.FAIL,
            cells=(passing, failing),
            cleanup=TestCleanup.UNCONFIRMED,
        )
        found = ResolvedTestEvidence(authority=authority, report=report)
        unavailable = UnavailableTestEvidence(
            reason=TestEvidenceUnavailableReason.UNQUALIFIED
        )
        request = ReviewAdmissionRequest(
            project_ref="project-review",
            scope_ref="scope-review",
            report_ref="report-review",
        )
        admitted = ReviewAdmissionDecision(
            status=ReviewAdmissionStatus.ADMITTED,
            verdict=TestVerdict.PASS,
            reason=None,
        )
        denied = ReviewAdmissionDecision(
            status=ReviewAdmissionStatus.DENIED,
            verdict=TestVerdict.FAIL,
            reason=ReviewAdmissionReason.TESTS_FAILED,
        )
        values = (
            binding,
            passing,
            failing,
            authority,
            empty_report,
            duplicate_cells_report,
            report,
            found,
            unavailable,
            request,
            admitted,
            denied,
        )
        for value in values:
            with self.subTest(model=type(value).__name__):
                restored = type(value).model_validate_json(value.model_dump_json())
                self.assertEqual(value, restored)

        adapter: TypeAdapter[TestEvidenceResolution] = TypeAdapter(TestEvidenceResolution)
        for value in (found, unavailable):
            with self.subTest(resolution=type(value).__name__):
                restored = adapter.validate_json(value.model_dump_json())
                self.assertEqual(value, restored)

    def test_required_fields_and_strict_primitives_reject(self) -> None:
        binding = self._binding()
        with self.assertRaises(ValidationError):
            TestBinding(**{**binding.model_dump(), "candidate_sha": 123})
        with self.assertRaises(ValidationError):
            TestBinding(**{**binding.model_dump(), "candidate_sha": "0" * 40})
        with self.assertRaises(ValidationError):
            TestBinding(**{**binding.model_dump(), "scope_ref": " scope-review"})
        with self.assertRaises(ValidationError):
            TestBinding(**{**binding.model_dump(), "reviewer_id": binding.engineer_id})
        with self.assertRaises(ValidationError):
            TestBinding(**{**binding.model_dump(), "unexpected": "field"})
        with self.assertRaises(ValidationError):
            TestCellObservation.model_validate(
                {
                    "cell_id": "cell-missing-reason",
                    "verdict": TestVerdict.FAIL,
                    "evidence_ref": "evidence-review",
                    "evidence_digest": _DIGEST,
                }
            )
        with self.assertRaises(ValidationError):
            TestCellObservation.model_validate(
                {
                    "cell_id": "cell-null-id",
                    "verdict": TestVerdict.PASS,
                    "evidence_ref": None,
                    "evidence_digest": _DIGEST,
                    "reason_ref": None,
                }
            )
        with self.assertRaises(ValidationError):
            TestReviewAuthority.model_validate(
                {
                    "binding": binding,
                    "expected_report_ref": "report-review",
                    "expected_cell_ids": ("cell-pass", "cell-pass"),
                    "cleanup_required": True,
                }
            )
        with self.assertRaises(ValidationError):
            TestReviewAuthority.model_validate(
                {
                    "binding": binding,
                    "expected_report_ref": "report-review",
                    "expected_cell_ids": ("cell-pass",),
                    "cleanup_required": 1,
                }
            )
        with self.assertRaises(ValidationError):
            TypeAdapter(TestEvidenceUnavailableReason).validate_python("NOT_FOUND ")

    def test_cell_verdict_reason_and_decision_shapes_are_closed(self) -> None:
        with self.assertRaises(ValidationError):
            self._cell(verdict=TestVerdict.PASS, reason_ref="reason-present")
        with self.assertRaises(ValidationError):
            self._cell(verdict=TestVerdict.BLOCKED)
        with self.assertRaises(ValidationError):
            ReviewAdmissionDecision(
                status=ReviewAdmissionStatus.ADMITTED,
                verdict=TestVerdict.FAIL,
                reason=None,
            )
        with self.assertRaises(ValidationError):
            ReviewAdmissionDecision(
                status=ReviewAdmissionStatus.DENIED,
                verdict=TestVerdict.PASS,
                reason=ReviewAdmissionReason.TESTS_FAILED,
            )
        with self.assertRaises(ValidationError):
            ReviewAdmissionDecision(
                status=ReviewAdmissionStatus.DENIED,
                verdict=TestVerdict.FAIL,
                reason=None,
            )

    def test_discriminated_resolution_rejects_unknown_or_null_status(self) -> None:
        adapter: TypeAdapter[TestEvidenceResolution] = TypeAdapter(TestEvidenceResolution)
        with self.assertRaises(ValidationError):
            adapter.validate_python({"status": "FOUND", "authority": None, "report": None})
        with self.assertRaises(ValidationError):
            adapter.validate_python({"status": "OTHER", "reason": "NOT_FOUND"})
        with self.assertRaises(ValidationError):
            adapter.validate_json('{"status": null, "reason": "NOT_FOUND"}')


if __name__ == "__main__":
    unittest.main()
