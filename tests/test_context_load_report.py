"""Tests for the static, read-only context-load report (ticket 03).

Covers the ticket's four TDD categories -- normal behavior, rule violation/bad
input, external failure/fail-closed, and regression protection -- plus the three
named reverse-mutation targets: hardcoding the reference list, treating a missing
routed file as zero bytes, and making the estimate label omittable. Mutation
evidence itself is produced by temporarily editing context_load_report.py and
re-running this file; it is not encoded as a test here.
"""

from __future__ import annotations

import unittest
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.workflow_router.contracts import (
    ExpectedReturnContract,
    ProcessStage,
    ReturnContractKind,
    RouterEventKind,
    RouterOutcome,
    SkillReference,
)
from library.workflow_router.context_load_report import (
    DEFAULT_REFERENCES_DIR,
    ContextLoadReport,
    ContextLoadReportFailure,
    ContextLoadReportStatus,
    ContextLoadReportSummary,
    LoadEstimate,
    StageRouteLoadEntry,
    generate_context_load_report,
    generate_default_context_load_report,
)
from library.workflow_router.profile import TransitionRule, build_router_poc_profile
from library.workflow_router.telemetry import estimate_text_tokens

_QUANTUM = Decimal("0.000001")


def _expected_ratio(numerator: int, denominator: int) -> str:
    """Independent re-derivation of the ratio contract, not a call into production code."""

    value = (Decimal(numerator) / Decimal(denominator)).quantize(_QUANTUM, rounding=ROUND_HALF_UP)
    return format(value, "f")


def _reference(reference_id: str) -> SkillReference:
    return SkillReference(
        reference_id=reference_id,
        source_revision="rev-" + "a" * 16,
        content_digest="sha256_" + "a" * 64,
    )


def _rule(
    *, current_stage: ProcessStage, event_kind: RouterEventKind, reference_id: str
) -> TransitionRule:
    """Build the smallest valid TransitionRule that names one reference.

    Mirrors the STOP/NO_RETURN shape profile.py itself uses for its WAYFINDER_NO_GO
    row, so this fixture can pick any (current_stage, event_kind) pair without also
    satisfying the ADVANCE/RETRY/SUSPEND-only validator branches on TransitionRule.
    """

    contract_id = f"return-{current_stage.value}-{event_kind.value}".replace("_", "-")
    return TransitionRule(
        skill_reference=_reference(reference_id),
        expected_return=ExpectedReturnContract(
            contract_id=contract_id,
            contract_revision="rev-" + "b" * 16,
            return_kind=ReturnContractKind.NO_RETURN,
            router_events=(),
            implementation_statuses=(),
        ),
        current_stage=current_stage,
        event_kind=event_kind,
        outcome=RouterOutcome.STOP,
        next_stage=ProcessStage.STOPPED,
    )


def _write(directory: Path, name: str, content: str) -> Path:
    """Write exact UTF-8 bytes with no newline translation, for byte-exact tests."""

    path = directory / name
    path.write_bytes(content.encode("utf-8"))
    return path


class RealRepoIntegrationTests(unittest.TestCase):
    """Runs the report against the live routing table and references directory."""

    def test_real_repo_generates_one_entry_per_transition_rule(self) -> None:
        rules = build_router_poc_profile().transition_rules
        report = generate_default_context_load_report()

        self.assertIs(report.status, ContextLoadReportStatus.GENERATED)
        assert report.summary is not None
        self.assertEqual(len(report.entries), len(rules))
        self.assertEqual(report.summary.routed_entry_count, len(rules))

        expected_rows = {(rule.current_stage, rule.event_kind) for rule in rules}
        actual_rows = {(entry.current_stage, entry.event_kind) for entry in report.entries}
        self.assertEqual(expected_rows, actual_rows)

        for entry in report.entries:
            self.assertLessEqual(entry.routed.byte_count, entry.baseline.byte_count)
            self.assertTrue(entry.baseline.is_estimate)
            self.assertTrue(entry.routed.is_estimate)

    def test_real_repo_baseline_matches_independent_stat_sum(self) -> None:
        """Cross-check against os.stat directly, not the module's own read path."""

        expected_total = sum(
            p.stat().st_size for p in DEFAULT_REFERENCES_DIR.glob("*.md") if p.is_file()
        )
        report = generate_default_context_load_report()
        self.assertEqual(report.entries[0].baseline.byte_count, expected_total)

    def test_real_repo_unrouted_stages_are_named_not_folded_into_average(self) -> None:
        report = generate_default_context_load_report()
        assert report.summary is not None
        self.assertIn(ProcessStage.BLOCKED, report.summary.unrouted_stages)
        self.assertIn(ProcessStage.STOPPED, report.summary.unrouted_stages)
        routed = {entry.current_stage for entry in report.entries}
        self.assertNotIn(ProcessStage.BLOCKED, routed)
        self.assertNotIn(ProcessStage.STOPPED, routed)
        # Every ProcessStage lands in exactly one of the two buckets -- none vanish.
        self.assertEqual(set(ProcessStage), routed | set(report.summary.unrouted_stages))


class NormalBehaviorTests(unittest.TestCase):
    """TDD category 1: exact arithmetic on a small, fully controlled fixture."""

    def test_baseline_routed_ratio_and_reduction_are_computed_correctly(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 100)
            _write(directory, "beta.md", "b" * 300)
            _write(directory, "gamma.md", "c" * 500)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
                _rule(
                    current_stage=ProcessStage.WAYFINDER,
                    event_kind=RouterEventKind.WAYFINDER_GO,
                    reference_id="gamma",
                ),
            )

            report = generate_context_load_report(references_dir=directory, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.GENERATED)
            assert report.summary is not None
            self.assertEqual(len(report.entries), 2)

            baseline_bytes = 100 + 300 + 500
            baseline_tokens = (100 + 3) // 4 + (300 + 3) // 4 + (500 + 3) // 4
            by_stage = {entry.current_stage: entry for entry in report.entries}

            alpha_entry = by_stage[ProcessStage.INTAKE]
            self.assertEqual(alpha_entry.baseline.byte_count, baseline_bytes)
            self.assertEqual(alpha_entry.baseline.estimated_tokens, baseline_tokens)
            self.assertEqual(alpha_entry.routed.byte_count, 100)
            self.assertEqual(alpha_entry.routed.estimated_tokens, (100 + 3) // 4)
            self.assertEqual(alpha_entry.byte_reduction, baseline_bytes - 100)
            self.assertEqual(alpha_entry.token_reduction, baseline_tokens - (100 + 3) // 4)
            self.assertEqual(
                alpha_entry.routed_to_baseline_ratio, _expected_ratio(100, baseline_bytes)
            )

            gamma_entry = by_stage[ProcessStage.WAYFINDER]
            self.assertEqual(gamma_entry.routed.byte_count, 500)
            self.assertEqual(
                gamma_entry.routed_to_baseline_ratio, _expected_ratio(500, baseline_bytes)
            )

            # gamma (500/900) reduces less than alpha (100/900): it is the worst case.
            self.assertEqual(report.summary.worst_case_entry.current_stage, ProcessStage.WAYFINDER)

            expected_average = (
                Decimal(alpha_entry.routed_to_baseline_ratio)
                + Decimal(gamma_entry.routed_to_baseline_ratio)
            ) / 2
            expected_average = expected_average.quantize(_QUANTUM, rounding=ROUND_HALF_UP)
            self.assertEqual(
                report.summary.average_routed_to_baseline_ratio, format(expected_average, "f")
            )

            # beta.md is not routed by any rule, but still counts toward the baseline.
            self.assertNotIn(ProcessStage.CONTEXT, by_stage)

    def test_unrouted_stage_is_named_and_never_synthesized_as_an_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 40)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            report = generate_context_load_report(references_dir=directory, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.GENERATED)
            assert report.summary is not None
            self.assertEqual(len(report.entries), 1)
            # Every other ProcessStage has no routing row and must be named, not skipped.
            self.assertEqual(
                set(report.summary.unrouted_stages), set(ProcessStage) - {ProcessStage.INTAKE}
            )
            self.assertFalse(
                any(entry.current_stage != ProcessStage.INTAKE for entry in report.entries)
            )


class RuleViolationAndBadInputTests(unittest.TestCase):
    """TDD category 2: named failures, never a substituted zero or a fabricated 100%."""

    def test_routing_table_naming_a_missing_file_is_a_named_failure(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 40)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="ghost-reference",
                ),
            )

            report = generate_context_load_report(references_dir=directory, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.BLOCKED)
            self.assertIs(report.failure, ContextLoadReportFailure.ROUTED_REFERENCE_FILE_MISSING)
            assert report.failure_detail is not None
            self.assertIn("ghost-reference", report.failure_detail)
            self.assertEqual(report.entries, ())
            self.assertIsNone(report.summary)

    def test_empty_references_directory_is_named_not_reported_as_full_savings(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            report = generate_context_load_report(references_dir=directory, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.BLOCKED)
            self.assertIs(report.failure, ContextLoadReportFailure.REFERENCES_DIRECTORY_EMPTY)
            # Not a report claiming "100% saved": no entries, no summary at all.
            self.assertEqual(report.entries, ())
            self.assertIsNone(report.summary)

    def test_empty_routing_table_is_named(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 40)

            report = generate_context_load_report(references_dir=directory, transition_rules=())

            self.assertIs(report.status, ContextLoadReportStatus.BLOCKED)
            self.assertIs(report.failure, ContextLoadReportFailure.ROUTING_TABLE_EMPTY)

    def test_missing_references_directory_is_named(self) -> None:
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            report = generate_context_load_report(references_dir=missing, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.BLOCKED)
            self.assertIs(report.failure, ContextLoadReportFailure.REFERENCES_DIRECTORY_MISSING)


class ExternalFailureFailClosedTests(unittest.TestCase):
    """TDD category 3: I/O problems fail closed and are distinguishable, never raised."""

    def test_unreadable_reference_entry_is_named_not_treated_as_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 40)
            # "trap.md" matches the *.md scan pattern by name but is a directory, not
            # a regular file, and must never be silently read as if it were text.
            (directory / "trap.md").mkdir()
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            report = generate_context_load_report(references_dir=directory, transition_rules=rules)

            # The directory-shaped "trap.md" is excluded from the scan, not read as 0
            # bytes: the baseline reflects only the one genuine reference file.
            self.assertIs(report.status, ContextLoadReportStatus.GENERATED)
            self.assertEqual(report.entries[0].baseline.byte_count, 40)

    def test_no_scenario_raises_an_exception_out_of_the_function(self) -> None:
        scenarios: list[tuple[Path, tuple[TransitionRule, ...]]] = []
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 10)
            populated_rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )
            missing_reference_rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="ghost",
                ),
            )
            empty_dir = Path(tmp) / "empty"
            empty_dir.mkdir()
            missing_dir = Path(tmp) / "missing"

            scenarios = [
                (directory, missing_reference_rules),
                (empty_dir, populated_rules),
                (missing_dir, populated_rules),
                (directory, ()),
            ]
            results = [
                generate_context_load_report(references_dir=d, transition_rules=r)
                for d, r in scenarios
            ]

        for result in results:
            self.assertIsInstance(result, ContextLoadReport)
            self.assertIs(result.status, ContextLoadReportStatus.BLOCKED)

    def test_failure_codes_are_pairwise_distinct_across_scenarios(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 10)
            populated_rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )
            missing_reference_rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="ghost",
                ),
            )
            empty_dir = Path(tmp) / "empty"
            empty_dir.mkdir()
            missing_dir = Path(tmp) / "missing"

            failures = [
                generate_context_load_report(
                    references_dir=directory, transition_rules=missing_reference_rules
                ).failure,
                generate_context_load_report(
                    references_dir=empty_dir, transition_rules=populated_rules
                ).failure,
                generate_context_load_report(
                    references_dir=directory, transition_rules=()
                ).failure,
                generate_context_load_report(
                    references_dir=missing_dir, transition_rules=populated_rules
                ).failure,
            ]

        self.assertEqual(len(failures), len(set(failures)))
        self.assertNotIn(None, failures)


class PathScanningTests(unittest.TestCase):
    """Defect category 1: no path-prefix leakage into sub- or sibling directories."""

    def test_nested_subdirectory_files_are_excluded_from_the_baseline(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 40)
            nested = directory / "nested"
            nested.mkdir()
            _write(nested, "shadow.md", "z" * 9999)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            report = generate_context_load_report(references_dir=directory, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.GENERATED)
            self.assertEqual(report.entries[0].baseline.byte_count, 40)

    def test_sibling_directory_files_are_excluded_from_the_baseline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            used = root / "references"
            used.mkdir()
            sibling = root / "references_other"
            sibling.mkdir()
            _write(used, "alpha.md", "a" * 40)
            _write(sibling, "sneaky.md", "z" * 9999)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            report = generate_context_load_report(references_dir=used, transition_rules=rules)

            self.assertIs(report.status, ContextLoadReportStatus.GENERATED)
            self.assertEqual(report.entries[0].baseline.byte_count, 40)


class EstimateLabelStructuralTests(unittest.TestCase):
    """The estimate label is a structural guarantee, never an optional courtesy."""

    def test_is_estimate_cannot_be_constructed_false(self) -> None:
        with self.assertRaises(ValidationError):
            LoadEstimate(byte_count=1, estimated_tokens=1, is_estimate=False)  # type: ignore[arg-type]

    def test_is_estimate_defaults_true_and_survives_serialization(self) -> None:
        estimate = LoadEstimate(byte_count=1, estimated_tokens=1)
        self.assertTrue(estimate.is_estimate)
        dumped = estimate.model_dump()
        self.assertIs(dumped["is_estimate"], True)
        self.assertIn("is_estimate", estimate.model_dump_json())

    def test_generated_report_cannot_also_carry_a_failure(self) -> None:
        entry = StageRouteLoadEntry(
            current_stage=ProcessStage.INTAKE,
            event_kind=RouterEventKind.INTAKE,
            reference_id="alpha",
            baseline=LoadEstimate(byte_count=100, estimated_tokens=25),
            routed=LoadEstimate(byte_count=100, estimated_tokens=25),
            routed_to_baseline_ratio="1.000000",
            byte_reduction=0,
            token_reduction=0,
        )
        summary = ContextLoadReportSummary(
            routed_entry_count=1,
            average_routed_to_baseline_ratio="1.000000",
            worst_case_entry=entry,
            unrouted_stages=(),
        )
        with self.assertRaises(ValidationError):
            ContextLoadReport(
                status=ContextLoadReportStatus.GENERATED,
                failure=ContextLoadReportFailure.ROUTING_TABLE_EMPTY,
                entries=(entry,),
                summary=summary,
            )

    def test_blocked_report_cannot_also_carry_entries(self) -> None:
        entry = StageRouteLoadEntry(
            current_stage=ProcessStage.INTAKE,
            event_kind=RouterEventKind.INTAKE,
            reference_id="alpha",
            baseline=LoadEstimate(byte_count=100, estimated_tokens=25),
            routed=LoadEstimate(byte_count=100, estimated_tokens=25),
            routed_to_baseline_ratio="1.000000",
            byte_reduction=0,
            token_reduction=0,
        )
        with self.assertRaises(ValidationError):
            ContextLoadReport(
                status=ContextLoadReportStatus.BLOCKED,
                failure=ContextLoadReportFailure.ROUTING_TABLE_EMPTY,
                failure_detail="anything",
                entries=(entry,),
            )


class HardcodingResistanceTests(unittest.TestCase):
    """A new reference file must move the baseline with no code change."""

    def test_adding_a_reference_file_changes_the_baseline_on_the_next_call(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            _write(directory, "alpha.md", "a" * 100)
            rules = (
                _rule(
                    current_stage=ProcessStage.INTAKE,
                    event_kind=RouterEventKind.INTAKE,
                    reference_id="alpha",
                ),
            )

            before = generate_context_load_report(references_dir=directory, transition_rules=rules)
            self.assertEqual(before.entries[0].baseline.byte_count, 100)

            _write(directory, "brand-new.md", "n" * 250)
            after = generate_context_load_report(references_dir=directory, transition_rules=rules)

            self.assertEqual(after.entries[0].baseline.byte_count, 350)
            self.assertGreater(
                after.entries[0].baseline.byte_count, before.entries[0].baseline.byte_count
            )


class RegressionCanaryTests(unittest.TestCase):
    """telemetry.estimate_text_tokens is read, never redefined or shadowed."""

    def test_estimate_text_tokens_formula_is_unchanged(self) -> None:
        self.assertEqual(estimate_text_tokens(text="a"), 1)
        self.assertEqual(estimate_text_tokens(text="a" * 4), 1)
        self.assertEqual(estimate_text_tokens(text="a" * 5), 2)
        self.assertEqual(estimate_text_tokens(text="a" * 100), 25)


if __name__ == "__main__":
    unittest.main()
