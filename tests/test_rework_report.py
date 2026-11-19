"""Behavioural tests for rework_report.py (exit codes 0/1/2/3) and the rework-record block.

Every case writes its records into a temporary directory; every expected line is derived from the
rounds the case writes.
"""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Sequence
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = _ROOT / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import integrate  # noqa: E402
import rework_report  # noqa: E402

SCRIPT = _SCRIPTS / "rework_report.py"
FENCE = "`" * 3
OUTER = "`" * 4
CANDIDATES = ("a" * 40, "b" * 40, "c" * 40, "d" * 40)
CAUSE_NAMES = ("CONTROL_PLANE_RULE", "RETURN_UNTRUE", "DESIGN_UNFORESEEN", "IMPLEMENTATION_DETAIL")
SUBMITTER = "seat:implementation-standard/x-impl"
REVIEWER = "seat:ticket-review/x-rev"


def fenced(tag: str, lines: Sequence[str], fence: str = FENCE) -> str:
    return "\n".join([f"{fence}{tag}", *lines, fence]) + "\n"


def rework_lines(
    candidate: str = CANDIDATES[0],
    number: str = "1",
    kind: str = "INITIAL",
    verdict: str = "CHANGES_REQUESTED",
    causes: str = "IMPLEMENTATION_DETAIL",
) -> list[str]:
    return [f"candidate: {candidate}", f"round: {number}", f"kind: {kind}", f"verdict: {verdict}", f"causes: {causes}"]


def verdict_block(candidate: str = CANDIDATES[0], verdict: str = "CHANGES_REQUESTED") -> str:
    return fenced("review-verdict", [f"candidate: {candidate}", f"verdict: {verdict}", f"reviewer: {REVIEWER}", "reviewed_at: 2026-11-20"])


def disposition(candidate: str = CANDIDATES[0], answer: str = "APPROVED") -> str:
    return "## Convergence disposition\n\n" + fenced(
        "convergence-disposition",
        [f"candidate: {candidate}", "reviewer_verdict: CONVERGENCE_REVIEW_REQUIRED", f"disposition: {answer}", "rule: CodeReview §5 rule B"],
    )


def review(
    candidate: str = CANDIDATES[0],
    verdict: str = "CHANGES_REQUESTED",
    number: str = "1",
    kind: str = "INITIAL",
    causes: str | None = None,
    block_candidate: str | None = None,
    block_verdict: str | None = None,
) -> str:
    if causes is None:
        causes = "" if verdict == "APPROVED" else "IMPLEMENTATION_DETAIL"
    return (
        f"## Review {number}\n\nA finding table stands here.\n\n"
        + verdict_block(candidate, verdict)
        + "\n"
        + fenced("rework-record", rework_lines(block_candidate or candidate, number, kind, block_verdict or verdict, causes))
        + "\n"
    )


def returned(number: str = "1", candidate: str = "none", causes: str = "DESIGN_UNFORESEEN") -> str:
    return "## Returned before review\n\n" + fenced("rework-record", rework_lines(candidate, number, "RETURN", "CHANGE_DETECTED", causes)) + "\n"


def record(*parts: str) -> str:
    return "# REVIEW\n\n" + "".join(parts)


class ReportCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="reworkrep-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def write(self, name: str, text: str | bytes) -> Path:
        path = self.base / name
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
        return path

    def run_main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rework_report.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def report(self, text: str | bytes, name: str = "65-x-code-review.md") -> tuple[int, str, str]:
        return self.run_main(str(self.write(name, text)))

    def reds(self, text: str, name: str = "65-x-code-review.md") -> tuple[int, list[str], str]:
        code, out, err = self.report(text, name)
        lines = [line for line in out.splitlines() if not line.startswith("TOTAL ") and " rounds=" not in line]
        return code, lines, err

    def assertRed(self, text: str, code_word: str, name: str = "65-x-code-review.md") -> None:
        code, reds, _ = self.reds(text, name)
        self.assertEqual(code, 1, reds)
        self.assertTrue(any(code_word in line for line in reds), (code_word, reds))


class NormalBehaviourTests(ReportCase):
    def test_the_exact_lines_for_a_record_with_a_return_round_and_a_round_with_two_causes(self) -> None:
        text = record(
            returned(),
            review(CANDIDATES[0], "CHANGES_REQUESTED", "2", "INITIAL", "CONTROL_PLANE_RULE,RETURN_UNTRUE,IMPLEMENTATION_DETAIL"),
            review(CANDIDATES[1], "CHANGES_REQUESTED", "3", "CORRECTION", "IMPLEMENTATION_DETAIL"),
            review(CANDIDATES[2], "APPROVED", "4", "CORRECTION"),
        )
        code, out, err = self.report(text, "65-retire-code-review.md")
        self.assertEqual(
            (code, out, err),
            (
                0,
                "65 rounds=4 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=1 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=2 final=APPROVED\n"
                "TOTAL tickets=1 rounds=4 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=1 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=2\n",
                "",
            ),
        )

    def test_several_records_give_one_line_each_in_order_and_one_total(self) -> None:
        first = self.write("74-a-code-review.md", record(review(CANDIDATES[0], "APPROVED")))
        second = self.write(
            "70-b-code-review.md",
            record(
                review(CANDIDATES[1], "CHANGES_REQUESTED", "1", "INITIAL", "DESIGN_UNFORESEEN"),
                review(CANDIDATES[2], "CONVERGENCE_REVIEW_REQUIRED", "2", "CORRECTION", ""),
                disposition(CANDIDATES[2]),
            ),
        )
        code, out, err = self.run_main(str(first), str(second))
        self.assertEqual(
            (code, out, err),
            (
                0,
                "74 rounds=1 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=0 final=APPROVED\n"
                "70 rounds=2 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=0 final=CONVERGENCE_REVIEW_REQUIRED\n"
                "TOTAL tickets=2 rounds=3 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=0\n",
                "",
            ),
        )

    def test_final_is_the_last_rounds_verdict_as_recorded(self) -> None:
        text = record(review(CANDIDATES[0], "CHANGES_REQUESTED", "1", "INITIAL", "RETURN_UNTRUE"), review(CANDIDATES[1], "BLOCKED", "2", "CORRECTION", "IMPLEMENTATION_DETAIL"))
        code, out, _ = self.report(text)
        self.assertEqual(code, 0)
        self.assertTrue(out.splitlines()[0].endswith("final=BLOCKED"), out)

    def test_a_return_block_with_a_commit_candidate_is_a_round(self) -> None:
        text = record(returned(candidate=CANDIDATES[3]), review(CANDIDATES[0], "APPROVED", "2", "INITIAL"))
        code, out, _ = self.report(text)
        self.assertEqual(code, 0, out)
        self.assertIn("65 rounds=2 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=1", out)

    def test_every_cause_counts_once_under_its_own_name(self) -> None:
        text = record(review(CANDIDATES[0], "CHANGES_REQUESTED", "1", "INITIAL", ",".join(CAUSE_NAMES)))
        code, out, _ = self.report(text)
        self.assertEqual(code, 0, out)
        self.assertIn("65 rounds=1 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=1 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=1 final=CHANGES_REQUESTED", out)

    def test_a_crlf_record_and_a_byte_order_mark_are_read(self) -> None:
        text = record(review(CANDIDATES[0], "APPROVED")).replace("\n", "\r\n").encode("utf-8")
        self.assertEqual(self.report(b"\xef\xbb\xbf" + text)[0], 0)

    def test_a_block_inside_another_fence_is_not_a_block(self) -> None:
        shown = OUTER + "text\n" + fenced("rework-record", rework_lines(verdict="APPROVED")) + OUTER + "\n"
        self.assertRed(record(shown), "NO_REWORK_RECORD")

    def test_the_tilde_fence_is_read(self) -> None:
        text = record(
            "~~~review-verdict\n" + f"candidate: {CANDIDATES[0]}\nverdict: APPROVED\nreviewer: {REVIEWER}\n~~~\n",
            "~~~rework-record\n" + "\n".join(rework_lines(verdict="APPROVED", causes="")) + "\n~~~\n",
        )
        self.assertEqual(self.report(text)[0], 0)

    def test_blocks_are_paired_with_the_nearest_verdict_before_them(self) -> None:
        text = record(review(CANDIDATES[0], "CHANGES_REQUESTED", "1", "INITIAL"), review(CANDIDATES[1], "APPROVED", "2", "CORRECTION"))
        self.assertEqual(self.report(text)[0], 0)


class TicketIdTests(ReportCase):
    def test_the_ticket_id_is_the_file_name_up_to_the_first_dash(self) -> None:
        text = record(review(CANDIDATES[0], "APPROVED"))
        for name, expected in (("65-a-b-code-review.md", "65"), ("650-a-code-review.md", "650"), ("6-a-code-review.md", "6")):
            with self.subTest(name):
                code, out, _ = self.report(text, name)
                self.assertEqual(code, 0)
                self.assertTrue(out.startswith(f"{expected} rounds=1 "), out)

    def test_ticket_65_and_ticket_650_are_two_tickets(self) -> None:
        text = record(review(CANDIDATES[0], "APPROVED"))
        first = self.write("65-a-code-review.md", text)
        second = self.write("650-a-code-review.md", text)
        code, out, _ = self.run_main(str(first), str(second))
        self.assertEqual(code, 0, out)
        self.assertIn("TOTAL tickets=2 rounds=2", out)

    def test_the_directory_part_of_the_path_does_not_make_the_id(self) -> None:
        folder = self.base / "a-b-c"
        folder.mkdir()
        path = folder / "65-x-code-review.md"
        path.write_text(record(review(CANDIDATES[0], "APPROVED")), encoding="utf-8")
        code, out, _ = self.run_main(str(path))
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("65 rounds=1 "), out)

    def test_two_records_of_one_ticket_are_a_red(self) -> None:
        text = record(review(CANDIDATES[0], "APPROVED"))
        first = self.write("65-a-code-review.md", text)
        second = self.write("65-b-code-review.md", text)
        code, out, _ = self.run_main(str(first), str(second))
        self.assertEqual(code, 1)
        self.assertIn("DUPLICATE_TICKET", out)

    def test_a_file_name_without_an_id_is_a_red(self) -> None:
        self.assertRed(record(review(CANDIDATES[0], "APPROVED")), "TICKET_ID", "-x-code-review.md")


class RedTests(ReportCase):
    def test_a_record_with_no_block_is_a_red(self) -> None:
        self.assertRed("# REVIEW\n\n" + verdict_block(), "NO_REWORK_RECORD")

    def test_an_unclosed_fence_is_a_red(self) -> None:
        text = record(review(CANDIDATES[0], "APPROVED")) + "```text\nnever closed\n"
        self.assertRed(text, "UNCLOSED_FENCE")

    def test_an_unclosed_rework_block_is_a_red(self) -> None:
        text = record(verdict_block(CANDIDATES[0], "APPROVED"), "```rework-record\n" + "\n".join(rework_lines(verdict="APPROVED", causes="")) + "\n")
        self.assertRed(text, "UNCLOSED_FENCE")

    def test_a_missing_field_is_a_red_for_each_field(self) -> None:
        for index, name in enumerate(rework_report.FIELDS):
            with self.subTest(name):
                lines = rework_lines()
                del lines[index]
                text = record(verdict_block(), fenced("rework-record", lines))
                self.assertRed(text, "FIELD_MISSING")

    def test_a_repeated_field_is_a_red_for_each_field(self) -> None:
        for index, name in enumerate(rework_report.FIELDS):
            with self.subTest(name):
                lines = rework_lines()
                lines.insert(index, lines[index])
                text = record(verdict_block(), fenced("rework-record", lines))
                self.assertRed(text, "FIELD_REPEATED")

    def test_fields_out_of_order_are_a_red(self) -> None:
        lines = rework_lines()
        lines[1], lines[2] = lines[2], lines[1]
        self.assertRed(record(verdict_block(), fenced("rework-record", lines)), "FIELD_ORDER")

    def test_a_sixth_line_a_blank_line_and_a_loose_line_are_a_red(self) -> None:
        for extra in ("note: more", "", "not a field", "Round: 1"):
            with self.subTest(extra):
                text = record(verdict_block(), fenced("rework-record", [*rework_lines(), extra]))
                self.assertRed(text, "FIELD_UNKNOWN")

    def test_round_values_outside_the_grammar_are_a_red(self) -> None:
        for number in ("01", "0", "-1", "1.0", "one", " 1", "1 ", "+1", ""):
            with self.subTest(number):
                text = record(verdict_block(), fenced("rework-record", rework_lines(number=number)))
                code, reds, _ = self.reds(text)
                self.assertEqual(code, 1, reds)

    def test_candidate_values_outside_the_grammar_are_a_red(self) -> None:
        for value in ("a" * 39, "a" * 41, "A" * 40, "g" * 40, "none", "NONE", "", "a" * 64):
            with self.subTest(value):
                text = record(verdict_block(CANDIDATES[0]), fenced("rework-record", rework_lines(candidate=value)))
                code, reds, _ = self.reds(text)
                self.assertEqual(code, 1, reds)

    def test_candidate_none_outside_a_return_block_is_a_red(self) -> None:
        text = record(verdict_block(), fenced("rework-record", rework_lines(candidate="none")))
        self.assertRed(text, "candidate none")

    def test_kind_and_verdict_outside_their_domain_are_a_red(self) -> None:
        for kind, verdict in (("initial", "CHANGES_REQUESTED"), ("FIRST", "CHANGES_REQUESTED"), ("INITIAL", "approved"), ("INITIAL", "MERGED"), ("", "BLOCKED")):
            with self.subTest((kind, verdict)):
                text = record(verdict_block(CANDIDATES[0], verdict), fenced("rework-record", rework_lines(kind=kind, verdict=verdict)))
                code, reds, _ = self.reds(text)
                self.assertEqual(code, 1, reds)

    def test_a_return_block_has_the_verdict_change_detected(self) -> None:
        text = record("## Returned\n\n" + fenced("rework-record", rework_lines("none", "1", "RETURN", "BLOCKED", "DESIGN_UNFORESEEN")))
        self.assertRed(text, "CHANGE_DETECTED")

    def test_an_unknown_cause_is_a_red_and_names_the_cause(self) -> None:
        for causes in ("MADE_UP", "IMPLEMENTATION_DETAIL,MADE_UP", "control_plane_rule", "Implementation_Detail"):
            with self.subTest(causes):
                code, reds, _ = self.reds(record(review(causes=causes)))
                self.assertEqual(code, 1, reds)
                self.assertTrue(any("UNKNOWN_CAUSE" in line for line in reds), reds)

    def test_a_cause_list_outside_its_grammar_is_a_red(self) -> None:
        for causes in (
            "CONTROL_PLANE_RULE, RETURN_UNTRUE",
            "CONTROL_PLANE_RULE ,RETURN_UNTRUE",
            "CONTROL_PLANE_RULE,",
            ",CONTROL_PLANE_RULE",
            "CONTROL_PLANE_RULE,,RETURN_UNTRUE",
            "CONTROL_PLANE_RULE,CONTROL_PLANE_RULE",
            "RETURN_UNTRUE,CONTROL_PLANE_RULE",
            "IMPLEMENTATION_DETAIL,DESIGN_UNFORESEEN",
            " IMPLEMENTATION_DETAIL",
        ):
            with self.subTest(causes):
                code, reds, _ = self.reds(record(review(causes=causes)))
                self.assertEqual(code, 1, reds)

    def test_empty_causes_on_a_changes_requested_blocked_or_change_detected_round_are_a_red(self) -> None:
        for verdict in ("CHANGES_REQUESTED", "BLOCKED"):
            with self.subTest(verdict):
                self.assertRed(record(review(verdict=verdict, causes="")), "CAUSES_RULE")
        self.assertRed(record(returned(causes="")), "CAUSES_RULE")

    def test_empty_causes_may_be_written_without_the_blank_after_the_colon(self) -> None:
        lines = rework_lines(verdict="APPROVED", causes="")
        lines[-1] = "causes:"
        self.assertEqual(self.report(record(verdict_block(CANDIDATES[0], "APPROVED"), fenced("rework-record", lines)))[0], 0)

    def test_causes_on_an_approved_round_are_a_red(self) -> None:
        for causes in ("IMPLEMENTATION_DETAIL", "CONTROL_PLANE_RULE,RETURN_UNTRUE"):
            with self.subTest(causes):
                self.assertRed(record(review(verdict="APPROVED", causes=causes)), "CAUSES_RULE")

    def test_convergence_causes_follow_the_disposition(self) -> None:
        empty = review(CANDIDATES[0], "CONVERGENCE_REVIEW_REQUIRED", causes="")
        filled = review(CANDIDATES[0], "CONVERGENCE_REVIEW_REQUIRED", causes="IMPLEMENTATION_DETAIL")
        cases = (
            ("empty with an approved disposition", empty + disposition(CANDIDATES[0]), 0),
            ("filled with an approved disposition", filled + disposition(CANDIDATES[0]), 1),
            ("empty without a disposition", empty, 1),
            ("filled without a disposition", filled, 0),
            ("empty with a disposition for another candidate", empty + disposition(CANDIDATES[1]), 1),
            ("empty with a disposition that is not approved", empty + disposition(CANDIDATES[0], "CHANGES_REQUESTED"), 1),
            ("filled with a disposition that is not approved", filled + disposition(CANDIDATES[0], "CHANGES_REQUESTED"), 0),
        )
        for label, body, expected in cases:
            with self.subTest(label):
                code, reds, _ = self.reds(record(body))
                self.assertEqual(code, expected, reds)
                if expected:
                    self.assertTrue(any("CAUSES_RULE" in line for line in reds), reds)

    def test_a_return_block_names_design_unforeseen_and_nothing_else(self) -> None:
        for causes in ("IMPLEMENTATION_DETAIL", "DESIGN_UNFORESEEN,IMPLEMENTATION_DETAIL", "CONTROL_PLANE_RULE"):
            with self.subTest(causes):
                self.assertRed(record(returned(causes=causes)), "CAUSES_RULE")

    def test_a_round_that_does_not_start_at_one_is_a_red(self) -> None:
        self.assertRed(record(review(number="2")), "ROUND_SEQUENCE")

    def test_a_skipped_round_is_a_red(self) -> None:
        text = record(review(CANDIDATES[0], number="1"), review(CANDIDATES[1], "APPROVED", "3", "CORRECTION"))
        self.assertRed(text, "ROUND_SEQUENCE")

    def test_a_repeated_round_is_a_red(self) -> None:
        text = record(review(CANDIDATES[0], number="1"), review(CANDIDATES[1], "APPROVED", "1", "CORRECTION"))
        self.assertRed(text, "ROUND_SEQUENCE")

    def test_rounds_out_of_order_are_a_red(self) -> None:
        text = record(review(CANDIDATES[0], number="2"), review(CANDIDATES[1], "APPROVED", "1", "CORRECTION"))
        code, reds, _ = self.reds(text)
        self.assertEqual(code, 1)
        self.assertEqual(sum("ROUND_SEQUENCE" in line for line in reds), 2, reds)

    def test_a_verdict_that_differs_from_the_review_verdict_is_a_red(self) -> None:
        for block_verdict in ("BLOCKED", "APPROVED"):
            with self.subTest(block_verdict):
                causes = "" if block_verdict == "APPROVED" else "IMPLEMENTATION_DETAIL"
                text = record(review(CANDIDATES[0], "CHANGES_REQUESTED", block_verdict=block_verdict, causes=causes))
                self.assertRed(text, "VERDICT_MISMATCH")

    def test_a_candidate_that_differs_from_the_review_verdict_is_a_red(self) -> None:
        self.assertRed(record(review(CANDIDATES[0], block_candidate=CANDIDATES[1])), "CANDIDATE_MISMATCH")

    def test_the_cross_check_uses_the_nearest_verdict_not_the_first(self) -> None:
        text = record(
            verdict_block(CANDIDATES[0], "CHANGES_REQUESTED"),
            fenced("rework-record", rework_lines(CANDIDATES[0], "1")),
            verdict_block(CANDIDATES[1], "APPROVED"),
            fenced("rework-record", rework_lines(CANDIDATES[0], "2", "CORRECTION", "CHANGES_REQUESTED")),
        )
        code, reds, _ = self.reds(text)
        self.assertEqual(code, 1)
        self.assertTrue(any("VERDICT_MISMATCH" in line for line in reds), reds)
        self.assertTrue(any("CANDIDATE_MISMATCH" in line for line in reds), reds)

    def test_a_malformed_review_verdict_does_not_pair(self) -> None:
        text = record(fenced("review-verdict", ["candidate: " + CANDIDATES[0]]), fenced("rework-record", rework_lines()))
        self.assertRed(text, "VERDICT_MISMATCH")

    def test_a_block_with_no_review_verdict_before_it_is_a_red(self) -> None:
        text = record(fenced("rework-record", rework_lines()), verdict_block())
        self.assertRed(text, "NO_REVIEW_VERDICT")

    def test_a_return_block_after_the_first_review_verdict_is_a_red(self) -> None:
        text = record(review(CANDIDATES[0], "CHANGES_REQUESTED", "1", "INITIAL"), returned("2"))
        self.assertRed(text, "RETURN_AFTER_VERDICT")

    def test_each_red_is_one_escaped_line_naming_the_record(self) -> None:
        code, out, _ = self.report(record(review(number="2")), "65-a b-code-review.md")
        self.assertEqual(code, 1)
        reds = [line for line in out.splitlines() if "ROUND_SEQUENCE" in line]
        self.assertEqual(len(reds), 1, out)
        self.assertIn("65-a\\u2028b-code-review.md", reds[0])

    def test_every_red_is_printed_not_only_the_first(self) -> None:
        text = record(
            review(CANDIDATES[0], "CHANGES_REQUESTED", "2", "INITIAL", "MADE_UP"),
            review(CANDIDATES[1], "APPROVED", "9", "CORRECTION", "IMPLEMENTATION_DETAIL", block_candidate=CANDIDATES[2]),
        )
        code, reds, _ = self.reds(text)
        self.assertEqual(code, 1)
        for word in ("ROUND_SEQUENCE", "UNKNOWN_CAUSE", "CAUSES_RULE", "CANDIDATE_MISMATCH"):
            self.assertTrue(any(word in line for line in reds), (word, reds))

    def test_a_record_with_a_red_has_no_ticket_line_and_the_total_leaves_it_out(self) -> None:
        good = self.write("74-a-code-review.md", record(review(CANDIDATES[0], "APPROVED")))
        bad = self.write("75-a-code-review.md", record(review(number="2")))
        code, out, _ = self.run_main(str(good), str(bad))
        lines = out.splitlines()
        self.assertEqual(code, 1)
        self.assertTrue(lines[0].startswith("74 rounds=1 "), lines)
        self.assertEqual(lines[1], "TOTAL tickets=1 rounds=1 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=0")
        self.assertEqual(len(lines), 3, lines)


class FaultTests(ReportCase):
    def test_an_undecodable_record_beside_a_record_with_a_red_gives_exit_one_and_the_fault_on_standard_error(self) -> None:
        bad = self.write("75-a-code-review.md", b"\xff\xfe not utf-8 \x80")
        red = self.write("76-a-code-review.md", record(review(number="2")))
        code, out, err = self.run_main(str(bad), str(red))
        self.assertEqual(code, 1)
        self.assertIn("ROUND_SEQUENCE", out)
        self.assertNotIn("not UTF-8", out)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("75-a-code-review.md", err)
        self.assertIn("not UTF-8", err)

    def test_a_missing_record_beside_a_record_with_a_red_gives_exit_one(self) -> None:
        red = self.write("76-a-code-review.md", record(review(number="2")))
        code, out, err = self.run_main(str(self.base / "77-missing-code-review.md"), str(red))
        self.assertEqual(code, 1)
        self.assertIn("ROUND_SEQUENCE", out)
        self.assertIn("cannot read", err)

    def test_an_undecodable_record_alone_gives_exit_two_and_does_not_raise(self) -> None:
        code, out, err = self.report(b"\xff\xfe\x80", "75-a-code-review.md")
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertEqual(out, "TOTAL tickets=0 rounds=0 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=0\n")

    def test_an_undecodable_record_beside_a_good_one_gives_exit_two_and_keeps_the_good_line(self) -> None:
        good = self.write("74-a-code-review.md", record(review(CANDIDATES[0], "APPROVED")))
        bad = self.write("75-a-code-review.md", b"\x80")
        code, out, err = self.run_main(str(good), str(bad))
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("74 rounds=1 "), out)
        self.assertIn("75-a-code-review.md", err)

    def test_a_directory_in_place_of_a_record_is_a_fault_not_a_raise(self) -> None:
        folder = self.base / "75-a-code-review.md"
        folder.mkdir()
        code, _, err = self.run_main(str(folder))
        self.assertEqual(code, 2)
        self.assertIn("cannot read", err)

    def test_an_unexpected_error_is_a_fault(self) -> None:
        original = rework_report.judge
        self.addCleanup(setattr, rework_report, "judge", original)

        def boom(text: str) -> rework_report.Judgement:
            raise RuntimeError("a\nb")

        setattr(rework_report, "judge", boom)
        code, out, err = self.report(record(review(CANDIDATES[0], "APPROVED")))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(err, "input fault: unexpected RuntimeError: a\\nb\n")


class UsageTests(ReportCase):
    def test_no_record_is_a_usage_error(self) -> None:
        code, out, err = self.run_main()
        self.assertEqual((code, out), (3, ""))
        self.assertTrue(err.startswith("usage: rework_report.py RECORD...\n"), err)

    def test_an_option_and_a_blank_path_are_usage_errors(self) -> None:
        for argv in (("--json", "x.md"), ("-x",), ("--",), (" ",)):
            with self.subTest(argv):
                code, out, _ = self.run_main(*argv)
                self.assertEqual((code, out), (3, ""))

    def test_the_real_command_line_works_and_never_prints_a_traceback(self) -> None:
        path = self.write("74-a-code-review.md", record(review(CANDIDATES[0], "APPROVED")))
        good = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
        self.assertEqual((good.returncode, good.stderr), (0, ""))
        self.assertTrue(good.stdout.startswith("74 rounds=1 "), good.stdout)
        usage = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual((usage.returncode, usage.stdout), (3, ""))
        bad = self.write("75-a-code-review.md", b"\xff")
        fault = subprocess.run([sys.executable, str(SCRIPT), str(bad)], capture_output=True, text=True)
        self.assertEqual(fault.returncode, 2)
        self.assertNotIn("Traceback", fault.stderr)


class IntegrateIgnoresTheBlockTests(unittest.TestCase):
    def check(self, text: str, candidate: str) -> tuple[object, tuple[str, ...]]:
        result = integrate.check_review(text.encode("utf-8"), candidate, SUBMITTER, None, None)
        return result.verdict, tuple(result.problems)

    def test_check_review_gives_the_same_result_with_and_without_the_block(self) -> None:
        cases = (
            (CANDIDATES[0], "APPROVED"),
            (CANDIDATES[0], "CHANGES_REQUESTED"),
            (CANDIDATES[0], "BLOCKED"),
        )
        for candidate, verdict in cases:
            with self.subTest(verdict):
                bare = "# REVIEW\n\n" + verdict_block(candidate, verdict)
                with_block = bare + "\n" + fenced("rework-record", rework_lines(candidate, "1", "INITIAL", verdict, "" if verdict == "APPROVED" else "IMPLEMENTATION_DETAIL"))
                self.assertEqual(self.check(bare, candidate), self.check(with_block, candidate))

    def test_check_review_gives_the_same_result_for_a_convergence_record_with_and_without_the_block(self) -> None:
        candidate = CANDIDATES[1]
        bare = "# REVIEW\n\n" + verdict_block(candidate, "CONVERGENCE_REVIEW_REQUIRED") + "\n" + disposition(candidate)
        with_block = (
            "# REVIEW\n\n"
            + verdict_block(candidate, "CONVERGENCE_REVIEW_REQUIRED")
            + "\n"
            + fenced("rework-record", rework_lines(candidate, "1", "CORRECTION", "CONVERGENCE_REVIEW_REQUIRED", ""))
            + "\n"
            + disposition(candidate)
        )
        self.assertEqual(self.check(bare, candidate), self.check(with_block, candidate))

    def test_a_malformed_block_does_not_change_the_result_either(self) -> None:
        candidate = CANDIDATES[0]
        bare = "# REVIEW\n\n" + verdict_block(candidate, "APPROVED")
        broken = bare + "\n" + fenced("rework-record", ["not a field", "round: 01"])
        self.assertEqual(self.check(bare, candidate), self.check(broken, candidate))


class RealRecordsTests(unittest.TestCase):
    """The ten wave-3 code-review records carry blocks that the report accepts (observation O1)."""

    RECORDS = (
        "65-retire-engine-and-private-router-code-review.md",
        "66-retire-bridge-code-review.md",
        "67-governance-document-sweep-code-review.md",
        "68-archive-router-specs-and-adrs-code-review.md",
        "69-token-use-per-seat-code-review.md",
        "70-wave2-template-and-hygiene-code-review.md",
        "72-dispatch-lint-one-action-per-line-code-review.md",
        "74-wave3-rule-texts-code-review.md",
        "75-own-tickets-follow-the-harness-code-review.md",
        "76-seat-model-and-effort-bound-code-review.md",
    )
    EXPECTED = (
        "65 rounds=3 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=1 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=1 final=APPROVED",
        "66 rounds=2 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=1 final=APPROVED",
        "67 rounds=2 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=1 final=APPROVED",
        "68 rounds=2 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=1 final=APPROVED",
        "69 rounds=2 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=1 final=CONVERGENCE_REVIEW_REQUIRED",
        "70 rounds=3 CONTROL_PLANE_RULE=1 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=1 IMPLEMENTATION_DETAIL=1 final=CONVERGENCE_REVIEW_REQUIRED",
        "72 rounds=2 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=1 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=1 final=CONVERGENCE_REVIEW_REQUIRED",
        "74 rounds=1 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=0 final=APPROVED",
        "75 rounds=1 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=0 final=APPROVED",
        "76 rounds=1 CONTROL_PLANE_RULE=0 RETURN_UNTRUE=0 DESIGN_UNFORESEEN=0 IMPLEMENTATION_DETAIL=0 final=APPROVED",
        "TOTAL tickets=10 rounds=19 CONTROL_PLANE_RULE=4 RETURN_UNTRUE=2 DESIGN_UNFORESEEN=2 IMPLEMENTATION_DETAIL=7",
    )

    def test_the_report_over_the_ten_backfilled_records_gives_exit_zero_and_the_expected_lines(self) -> None:
        folder = _ROOT / "doc" / "reviews" / "workflow-governance"
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rework_report.main([str(folder / name) for name in self.RECORDS])
        self.assertEqual((code, err.getvalue()), (0, ""))
        self.assertEqual(out.getvalue().splitlines(), list(self.EXPECTED))


class ProcessTextTests(unittest.TestCase):
    def test_code_review_section_3_names_the_block_and_who_writes_it(self) -> None:
        text = " ".join((_ROOT / "CodeReview.md").read_text(encoding="utf-8").split())
        section = text.split("## 3.", 1)[1].split("## 4.", 1)[0]
        for phrase in ("rework-record", "directly follows", "review-verdict", "causes", "RETURN"):
            with self.subTest(phrase):
                self.assertIn(phrase, section)

    def test_the_readme_names_the_report_and_its_section(self) -> None:
        readme = (_SCRIPTS / "README.md").read_text(encoding="utf-8")
        self.assertIn("## rework_report.py", readme)
        section = readme.split("## rework_report.py", 1)[1].split("\n## ", 1)[0]
        for word in CAUSE_NAMES:
            with self.subTest(word):
                self.assertIn(word, section)
        for phrase in ("Red before fault", "NO_REWORK_RECORD", "TOTAL tickets="):
            with self.subTest(phrase):
                self.assertIn(phrase, " ".join(section.split()))


if __name__ == "__main__":
    unittest.main()
