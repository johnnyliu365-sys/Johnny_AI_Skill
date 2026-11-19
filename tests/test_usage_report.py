"""Behavioural tests for usage_report.py (exit codes 0/1/2/3).

Every case writes its receipts and expectation file into a temporary directory; every expected line
is derived from the numbers the case writes.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Sequence
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import usage_report  # noqa: E402

SCRIPT = _SCRIPTS / "usage_report.py"
FENCE = "`" * 4
IMPLEMENTATION = "implementation-standard"
REVIEW = "ticket-review"
LIMITS = {
    IMPLEMENTATION: {"model": "a-model", "effort": "high", "output_tokens_max": 1000, "processed_tokens_max": 5000},
    REVIEW: {"model": "a-model", "effort": "high", "output_tokens_max": 800, "processed_tokens_max": 4000},
}
FIELD_NAMES = (
    "cell",
    "seat",
    "profile",
    "model",
    "effort",
    "input_tokens",
    "cache_write_tokens",
    "cache_read_tokens",
    "output_tokens",
    "source",
)


def usage(
    profile: str = IMPLEMENTATION,
    run: str = "run-1",
    counts: tuple[int, int, int, int] = (100, 200, 300, 400),
    replace: dict[str, str] | None = None,
    drop: Sequence[str] = (),
    extra: Sequence[str] = (),
    heading: str | None = None,
) -> str:
    seat = f"seat:{profile}/{run}"
    values = {
        "cell": "USAGE",
        "seat": seat,
        "profile": profile,
        "model": "a-model",
        "effort": "high",
        "input_tokens": str(counts[0]),
        "cache_write_tokens": str(counts[1]),
        "cache_read_tokens": str(counts[2]),
        "output_tokens": str(counts[3]),
        "source": "host transcript usage",
    }
    values.update(replace or {})
    lines = [f"## {heading if heading is not None else 'USAGE ' + seat}"]
    lines.extend(f"{name}: {values[name]}" for name in FIELD_NAMES if name not in drop)
    lines.extend(extra)
    return "\n".join(lines) + "\n"


RUN_CELL = f"## A\ncell: A\ncandidate: {'a' * 40}\ntool_digest:\n- t.py={'b' * 64}\ncapture: A.txt\nexit: 0\n\n{FENCE}\nexit=0\n{FENCE}\n"


class ReportCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="usagerep-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.expectation = self.write_json(LIMITS)

    def write_json(self, value: object, name: str = "expectation.json") -> Path:
        path = self.base / name
        path.write_text(json.dumps(value), encoding="utf-8", newline="\n")
        return path

    def receipt(self, *parts: str, name: str = "RETURN.md", newline: str = "\n") -> Path:
        path = self.base / name
        text = "# receipt\n\n" + RUN_CELL + "\n" + "\n".join(parts)
        path.write_bytes(text.replace("\n", newline).encode("utf-8"))
        return path

    def run_main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = usage_report.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def report(self, *receipts: Path, expectation: Path | None = None) -> tuple[int, str, str]:
        return self.run_main("--expectation", str(expectation or self.expectation), *map(str, receipts))


class NormalBehaviourTests(ReportCase):
    def test_one_line_per_seat_and_exit_zero_when_all_are_within(self) -> None:
        path = self.receipt(usage(), usage(REVIEW, "run-2", (10, 20, 30, 40)))
        code, out, err = self.report(path)
        self.assertEqual(
            (code, out, err),
            (
                0,
                f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model=a-model effort=high output=400 processed=600 WITHIN\n"
                f"seat:{REVIEW}/run-2 {REVIEW} model=a-model effort=high output=40 processed=60 WITHIN\n",
                "",
            ),
        )

    def test_several_receipts_are_listed_in_order(self) -> None:
        first = self.receipt(usage(run="run-1"), name="one.md")
        second = self.receipt(usage(REVIEW, "run-2"), name="two.md")
        code, out, _ = self.report(first, second)
        self.assertEqual(code, 0)
        self.assertEqual([line.split(" ")[0] for line in out.splitlines()], [f"seat:{IMPLEMENTATION}/run-1", f"seat:{REVIEW}/run-2"])

    def test_zero_counts_are_within(self) -> None:
        code, out, _ = self.report(self.receipt(usage(counts=(0, 0, 0, 0))))
        self.assertEqual((code, out), (0, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model=a-model effort=high output=0 processed=0 WITHIN\n"))

    def test_a_crlf_receipt_and_a_byte_order_mark_are_read(self) -> None:
        path = self.receipt(usage(), newline="\r\n")
        path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
        self.assertEqual(self.report(path)[0], 0)

    def test_usage_text_inside_a_fence_is_not_a_cell(self) -> None:
        fenced = f"## B\ncell: B\n\n{FENCE}\n## USAGE seat:x/y\ncell: USAGE\n{FENCE}\n"
        code, out, _ = self.report(self.receipt(fenced, usage()))
        self.assertEqual((code, len(out.splitlines())), (0, 1))


class VerdictTests(ReportCase):
    def verdict(self, counts: tuple[int, int, int, int], profile: str = IMPLEMENTATION) -> tuple[int, str]:
        code, out, _ = self.report(self.receipt(usage(profile, counts=counts)))
        return code, out.split(" ")[-1].strip()

    def test_a_value_equal_to_its_maximum_is_within(self) -> None:
        self.assertEqual(self.verdict((5000, 0, 0, 1000)), (0, "WITHIN"))
        self.assertEqual(self.verdict((1000, 2000, 2000, 1000)), (0, "WITHIN"))

    def test_one_over_the_output_maximum_is_over_output(self) -> None:
        self.assertEqual(self.verdict((1, 1, 1, 1001)), (1, "OVER_OUTPUT"))

    def test_one_over_the_processed_maximum_is_over_processed(self) -> None:
        self.assertEqual(self.verdict((5001, 0, 0, 1)), (1, "OVER_PROCESSED"))
        self.assertEqual(self.verdict((1, 2, 4998, 1)), (1, "OVER_PROCESSED"))

    def test_both_over_lists_both_words(self) -> None:
        self.assertEqual(self.verdict((6000, 0, 0, 2000)), (1, "OVER_OUTPUT,OVER_PROCESSED"))

    def test_the_review_profile_uses_its_own_limits(self) -> None:
        self.assertEqual(self.verdict((100, 100, 100, 801), REVIEW), (1, "OVER_OUTPUT"))
        self.assertEqual(self.verdict((100, 100, 100, 800), REVIEW), (0, "WITHIN"))

    def test_an_unknown_profile_is_listed_and_exit_one(self) -> None:
        code, out, _ = self.report(self.receipt(usage("made-up")))
        self.assertEqual((code, out), (1, "seat:made-up/run-1 made-up model=a-model effort=high output=400 processed=600 UNKNOWN_PROFILE\n"))

    def test_every_problem_is_listed_not_only_the_first(self) -> None:
        path = self.receipt(usage(counts=(1, 1, 1, 5000)), usage("made-up", "run-2"), usage(REVIEW, "run-3"))
        code, out, _ = self.report(path)
        self.assertEqual(code, 1)
        self.assertEqual([line.split(" ")[-1] for line in out.splitlines()], ["OVER_OUTPUT", "UNKNOWN_PROFILE", "WITHIN"])


class PresenceTests(ReportCase):
    def test_a_receipt_without_a_usage_cell_is_exit_one(self) -> None:
        path = self.receipt()
        code, out, err = self.report(path)
        self.assertEqual((code, err), (1, ""))
        self.assertEqual(out, f"NO_USAGE {usage_report.printable(str(path))}\n")

    def test_every_receipt_without_a_usage_cell_is_listed(self) -> None:
        bare_one = self.receipt(name="one.md")
        good = self.receipt(usage(), name="two.md")
        bare_two = self.receipt(name="three.md")
        code, out, _ = self.report(bare_one, good, bare_two)
        self.assertEqual(code, 1)
        self.assertEqual([line.split(" ")[0] for line in out.splitlines()], ["NO_USAGE", f"seat:{IMPLEMENTATION}/run-1", "NO_USAGE"])


class ReceiptSchemaTests(ReportCase):
    def fault(self, *parts: str) -> str:
        code, out, err = self.report(self.receipt(*parts))
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertNotIn("Traceback", err)
        return err

    def test_a_missing_field_is_exit_two_for_each_field(self) -> None:
        for name in FIELD_NAMES[1:]:
            if name == "effort":
                continue  # optional: a cell without it prints EFFORT_UNRECORDED
            with self.subTest(name=name):
                self.assertIn(name, self.fault(usage(drop=[name])))

    def test_a_repeated_field_is_exit_two(self) -> None:
        self.assertIn("more than once", self.fault(usage(extra=["model: other"])))

    def test_fields_out_of_order_are_exit_two(self) -> None:
        lines = usage().split("\n")
        lines[3], lines[4] = lines[4], lines[3]
        self.assertIn("out of order", self.fault("\n".join(lines)))

    def test_a_negative_or_non_integer_count_is_exit_two(self) -> None:
        for bad in ("-1", "1.5", "abc", "", "01", "1e3", "NaN", "\u0662", "1\u0662", "5\u0662", "\uff11\uff12", "\u0967", "\u00b2", "1\u00b2"):
            with self.subTest(bad=bad):
                self.assertIn("output_tokens", self.fault(usage(replace={"output_tokens": bad})))

    def test_a_run_field_inside_usage_is_exit_two(self) -> None:
        for extra in ("candidate: x", "capture: x", "exit: 0", "tool_digest:"):
            with self.subTest(extra=extra):
                self.fault(usage(extra=[extra]))
        self.fault(usage(extra=["", FENCE, "exit=0", FENCE]))

    def test_two_usage_cells_for_one_seat_are_exit_two(self) -> None:
        self.assertIn("two USAGE cells", self.fault(usage(), usage()))

    def test_a_seat_or_heading_that_does_not_fit_is_exit_two(self) -> None:
        self.fault(usage(replace={"seat": "implementation-standard/run-1"}))
        self.fault(usage(replace={"profile": REVIEW}))
        self.fault(usage(heading="USAGE other"))

    def test_an_unreadable_receipt_is_exit_two(self) -> None:
        code, out, err = self.report(self.base / "no-such-receipt.md")
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)

    def test_an_undecodable_receipt_is_exit_two_with_one_line(self) -> None:
        path = self.base / "bad.md"
        path.write_bytes(b"## USAGE x\n\xff\xfe\n")
        code, out, err = self.report(path)
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)
        self.assertIn("not UTF-8", err)

    def test_a_red_and_a_fault_in_one_run_print_the_red_and_exit_one(self) -> None:
        red = self.receipt(usage(counts=(1, 1, 1, 9999)), name="red.md")
        broken = self.receipt(usage(drop=["model"]), name="broken.md")
        code, out, err = self.report(red, broken)
        self.assertEqual(code, 1)
        self.assertTrue(out.endswith("OVER_OUTPUT\n"), out)
        self.assertIn("model", err)

    def test_a_control_character_in_a_printed_subject_stays_on_one_line(self) -> None:
        path = self.receipt(usage(replace={"model": "a\x0bb"}))
        code, out, err = self.report(path)
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)

    def test_a_receipt_path_with_a_control_character_is_escaped(self) -> None:
        code, out, err = self.report(self.base / "no\x0bsuch.md")
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)
        self.assertIn("\\x0b", err)


class ExpectationSchemaTests(ReportCase):
    def fault_for(self, path: Path) -> str:
        code, out, err = self.report(self.receipt(usage()), expectation=path)
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertNotIn("Traceback", err)
        return err

    def raw(self, text: str, name: str = "raw.json") -> Path:
        path = self.base / name
        path.write_bytes(text.encode("utf-8"))
        return path

    def test_a_missing_expectation_file_is_exit_two(self) -> None:
        self.fault_for(self.base / "none.json")

    def test_text_that_is_not_json_is_exit_two(self) -> None:
        self.fault_for(self.raw("not json"))
        self.fault_for(self.raw(""))

    def test_a_repeated_key_is_exit_two(self) -> None:
        text = '{"%s": {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 2}, "%s": {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 2}}' % (IMPLEMENTATION, IMPLEMENTATION)
        self.assertIn("repeated", self.fault_for(self.raw(text)))
        inner = '{"%s": {"model": "a-model", "effort": "high", "output_tokens_max": 1, "output_tokens_max": 3, "processed_tokens_max": 2}}' % IMPLEMENTATION
        self.assertIn("repeated", self.fault_for(self.raw(inner)))

    def test_nan_and_infinity_are_exit_two(self) -> None:
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                text = '{"%s": {"model": "a-model", "effort": "high", "output_tokens_max": %s, "processed_tokens_max": 2}}' % (IMPLEMENTATION, constant)
                self.assertIn("refused", self.fault_for(self.raw(text)))

    def test_a_missing_profile_key_is_exit_two(self) -> None:
        for key in ("model", "effort", "output_tokens_max", "processed_tokens_max"):
            with self.subTest(key=key):
                entry = {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 1}
                del entry[key]
                self.assertIn(key, self.fault_for(self.write_json({IMPLEMENTATION: entry})))

    def test_an_unknown_profile_key_is_exit_two(self) -> None:
        entry = {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 2, "extra": 3}
        self.assertIn("extra", self.fault_for(self.write_json({IMPLEMENTATION: entry})))

    def test_a_limit_that_is_not_an_integer_is_exit_two(self) -> None:
        for bad in (-1, 1.5, "10", True, None, [1]):
            with self.subTest(bad=bad):
                entry = {"model": "a-model", "effort": "high", "output_tokens_max": bad, "processed_tokens_max": 2}
                self.fault_for(self.write_json({IMPLEMENTATION: entry}))
        self.fault_for(self.raw('{"%s": {"model": "a-model", "effort": "high", "output_tokens_max": 1e3, "processed_tokens_max": 2}}' % IMPLEMENTATION))

    def test_a_top_level_that_is_not_a_non_empty_object_is_exit_two(self) -> None:
        values: tuple[object, ...] = ([], {}, 5, "x", None)
        for value in values:
            with self.subTest(value=value):
                self.fault_for(self.write_json(value))

    def test_a_profile_that_is_not_an_object_is_exit_two(self) -> None:
        self.fault_for(self.write_json({IMPLEMENTATION: 5}))

    def test_a_byte_order_mark_and_invalid_utf8_are_exit_two(self) -> None:
        good = json.dumps(LIMITS)
        self.fault_for(self.raw("﻿" + good))
        path = self.base / "bytes.json"
        path.write_bytes(b'{"\xff": 1}')
        self.fault_for(path)

    def test_a_zero_limit_is_valid(self) -> None:
        path = self.write_json({IMPLEMENTATION: {"model": "a-model", "effort": "high", "output_tokens_max": 0, "processed_tokens_max": 0}})
        code, out, _ = self.report(self.receipt(usage(counts=(0, 0, 0, 0))), expectation=path)
        self.assertEqual((code, out.split(" ")[-1].strip()), (0, "WITHIN"))


class UsageErrorTests(ReportCase):
    def test_no_arguments_is_exit_three(self) -> None:
        code, out, err = self.run_main()
        self.assertEqual((code, out), (3, ""))
        self.assertIn("usage:", err)

    def test_a_missing_expectation_option_is_exit_three(self) -> None:
        self.assertEqual(self.run_main(str(self.receipt(usage())))[0], 3)

    def test_no_receipt_is_exit_three(self) -> None:
        self.assertEqual(self.run_main("--expectation", str(self.expectation))[0], 3)

    def test_an_unknown_or_repeated_option_is_exit_three(self) -> None:
        path = str(self.receipt(usage()))
        self.assertEqual(self.run_main("--expectation", str(self.expectation), "--verbose", path)[0], 3)
        self.assertEqual(self.run_main("--expectation", str(self.expectation), "--expectation", str(self.expectation), path)[0], 3)
        self.assertEqual(self.run_main("--expectation", str(self.expectation), "-x", path)[0], 3)

    def test_an_option_without_a_value_and_a_blank_receipt_are_exit_three(self) -> None:
        self.assertEqual(self.run_main("--expectation")[0], 3)
        self.assertEqual(self.run_main("--expectation", str(self.expectation), " ")[0], 3)

    def test_the_equals_form_is_accepted(self) -> None:
        code, _, _ = self.run_main(f"--expectation={self.expectation}", str(self.receipt(usage())))
        self.assertEqual(code, 0)


class ProcessTests(ReportCase):
    def command(self, *receipts: Path) -> list[str]:
        return [sys.executable, "-I", "-X", "utf8", str(SCRIPT), "--expectation", str(self.expectation), *map(str, receipts)]

    def test_output_is_lf_only_and_exit_zero(self) -> None:
        done = subprocess.run(self.command(self.receipt(usage())), capture_output=True)
        self.assertEqual(done.returncode, 0)
        self.assertNotIn(b"\r", done.stdout)
        self.assertEqual(done.stderr, b"")

    def test_exit_codes_through_the_process(self) -> None:
        over = self.receipt(usage(counts=(1, 1, 1, 9999)), name="over.md")
        self.assertEqual(subprocess.run(self.command(over), capture_output=True).returncode, 1)
        self.assertEqual(subprocess.run(self.command(self.base / "none.md"), capture_output=True).returncode, 2)
        done = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True)
        self.assertEqual(done.returncode, 3)
        self.assertNotIn(b"Traceback", done.stderr)

    def test_a_non_cp950_subject_under_a_cp950_console_does_not_change_the_exit(self) -> None:
        path = self.receipt(usage(profile="made-up", replace={"model": "m"}))
        env = {"PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0", "SYSTEMROOT": str(Path(sys.executable).parent)}
        done = subprocess.run([sys.executable, str(SCRIPT), "--expectation", str(self.expectation), str(path)], capture_output=True, env=env)
        self.assertEqual(done.returncode, 1, done.stderr)

    def test_the_script_uses_only_the_standard_library_and_no_any(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for banned in ("import requests", "import yaml", "# type: ignore", "typing import Any", ": Any", "-> Any"):
            self.assertNotIn(banned, source)



class RedBeforeFaultTests(ReportCase):
    """R4-2: every red the run can find is printed; the exit is 1 with a red, else 2 with a fault."""

    def test_an_over_seat_and_a_missing_receipt_print_the_red_and_exit_one(self) -> None:
        over = self.receipt(usage(counts=(1, 1, 1, 9999)), name="over.md")
        code, out, err = self.report(over, self.base / "no-such-receipt.md")
        self.assertEqual(code, 1)
        self.assertEqual(out, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model=a-model effort=high output=9999 processed=3 OVER_OUTPUT\n")
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("cannot read receipt", err)

    def test_a_receipt_without_usage_and_a_broken_one_print_no_usage_and_exit_one(self) -> None:
        bare = self.receipt(name="bare.md")
        broken = self.receipt(usage(drop=["model"]), name="broken.md")
        code, out, err = self.report(bare, broken)
        self.assertEqual(code, 1)
        self.assertEqual(out, f"NO_USAGE {usage_report.printable(str(bare))}\n")
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("model", err)

    def test_no_usage_stands_when_the_expectation_file_cannot_be_read(self) -> None:
        bare = self.receipt(name="bare.md")
        code, out, err = self.report(bare, expectation=self.base / "none.json")
        self.assertEqual(code, 1)
        self.assertEqual(out, f"NO_USAGE {usage_report.printable(str(bare))}\n")
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("expectation file", err)

    def test_the_verdicts_that_need_the_expectation_are_not_computed_without_it(self) -> None:
        code, out, err = self.report(self.receipt(usage()), expectation=self.base / "none.json")
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_fault_alone_is_exit_two(self) -> None:
        code, out, err = self.report(self.base / "no-such-receipt.md", self.receipt(usage(), name="good.md"))
        self.assertEqual(code, 2)
        self.assertEqual(out, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model=a-model effort=high output=400 processed=600 WITHIN\n")
        self.assertEqual(len(err.splitlines()), 1, err)

    def test_an_unknown_profile_beside_a_broken_receipt_is_exit_one(self) -> None:
        unknown = self.receipt(usage("made-up"), name="unknown.md")
        broken = self.receipt(usage(replace={"output_tokens": "-1"}), name="broken.md")
        code, out, err = self.report(broken, unknown)
        self.assertEqual(code, 1)
        self.assertTrue(out.endswith("UNKNOWN_PROFILE\n"), out)
        self.assertEqual(len(err.splitlines()), 1, err)


class DecimalCountTests(ReportCase):
    """A count of any length is a value: compared as text, never converted, never an error."""

    def line(self, counts: tuple[str, str, str, str], limits: dict[str, dict[str, object]] | None = None) -> tuple[int, str, str]:
        names = ("input_tokens", "cache_write_tokens", "cache_read_tokens", "output_tokens")
        path = self.receipt(usage(replace=dict(zip(names, counts))))
        expectation = self.write_json(limits, "big.json") if limits is not None else None
        return self.report(path, expectation=expectation)

    def test_a_huge_output_count_is_over_output_and_exit_one(self) -> None:
        huge = "9" * 5000
        code, out, err = self.line(("1", "1", "1", huge))
        self.assertEqual((code, err), (1, ""))
        self.assertEqual(out, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model=a-model effort=high output={huge} processed=3 OVER_OUTPUT\n")

    def test_a_huge_input_count_is_over_processed_and_exit_one(self) -> None:
        huge = "1" + "0" * 4999
        code, out, err = self.line((huge, "1", "1", "1"))
        self.assertEqual((code, err), (1, ""))
        self.assertTrue(out.endswith("OVER_PROCESSED\n"), out[-40:])
        self.assertIn("processed=" + "1" + "0" * 4998 + "2 ", out)

    def test_a_count_equal_to_a_long_limit_is_within_and_one_more_is_over(self) -> None:
        limit = 10**400
        limits = {IMPLEMENTATION: {"model": "a-model", "effort": "high", "output_tokens_max": limit, "processed_tokens_max": limit}}
        self.assertEqual(self.line(("1", "1", "1", str(limit)), limits)[0], 0)
        code, out, _ = self.line(("1", "1", "1", str(limit + 1)), limits)
        self.assertEqual((code, out.split(" ")[-1].strip()), (1, "OVER_OUTPUT"))

    def test_the_processed_sum_carries_across_the_three_counts(self) -> None:
        limit = 10**400
        limits = {IMPLEMENTATION: {"model": "a-model", "effort": "high", "output_tokens_max": 10, "processed_tokens_max": limit}}
        self.assertEqual(self.line((str(limit - 1), "1", "0", "1"), limits)[0], 0)
        code, out, _ = self.line((str(limit - 1), "1", "1", "1"), limits)
        self.assertEqual((code, out.split(" ")[-1].strip()), (1, "OVER_PROCESSED"))
        self.assertEqual(self.line(("999", "999", "999", "1"), {IMPLEMENTATION: {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 2997}})[0], 0)
        self.assertEqual(self.line(("999", "999", "999", "1"), {IMPLEMENTATION: {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 2996}})[0], 1)

    def test_the_decimal_helpers(self) -> None:
        self.assertEqual(usage_report.add_decimal("999", "1"), "1000")
        self.assertEqual(usage_report.add_decimal("0", "0"), "0")
        self.assertEqual(usage_report.add_decimal("5", "12345"), "12350")
        self.assertTrue(usage_report.is_greater("10", "9"))
        self.assertFalse(usage_report.is_greater("9", "10"))
        self.assertFalse(usage_report.is_greater("12", "12"))
        self.assertTrue(usage_report.is_greater("13", "12"))


class RecognitionTests(ReportCase):
    """A USAGE cell is recognised exactly as evidence_gate.py recognises it; none is skipped."""

    def fault_with(self, *parts: str) -> tuple[int, str, str]:
        return self.report(self.receipt(*parts))

    def test_a_usage_section_without_its_cell_line_is_not_skipped(self) -> None:
        code, out, err = self.fault_with(usage(), usage(REVIEW, "run-2", (1, 1, 1, 9999), drop=["cell"]))
        self.assertEqual(code, 2)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("cell", err)
        self.assertIn(f"seat:{REVIEW}/run-2", err)

    def test_a_misspelt_cell_line_under_a_usage_heading_is_not_skipped(self) -> None:
        for spelling in ("usage", "Usage", "USAGES", ""):
            with self.subTest(spelling=spelling):
                code, out, err = self.fault_with(usage(replace={"cell": spelling}))
                self.assertEqual((code, out), (2, ""))
                self.assertEqual(len(err.splitlines()), 1, err)
                self.assertIn("cell: line says", err)

    def test_a_bare_usage_heading_without_a_cell_line_is_not_skipped(self) -> None:
        code, _, err = self.fault_with("## USAGE\nseat: x\n")
        self.assertEqual(code, 2)
        self.assertIn("cell", err)

    def test_such_a_section_beside_a_red_still_lets_the_red_stand(self) -> None:
        bare = self.receipt(name="bare.md")
        broken = self.receipt(usage(drop=["cell"]), name="broken.md")
        code, out, err = self.report(bare, broken)
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("NO_USAGE"), out)
        self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_section_with_another_heading_and_no_cell_line_is_not_a_usage_cell(self) -> None:
        code, out, _ = self.fault_with("## Notes\nseat: x\n", usage())
        self.assertEqual((code, len(out.splitlines())), (0, 1))
        code, out, _ = self.fault_with("## USAGEX\nseat: x\n", usage())
        self.assertEqual((code, len(out.splitlines())), (0, 1))

    def test_the_cell_line_alone_decides_for_any_heading(self) -> None:
        code, _, err = self.fault_with(usage(heading="Other name"))
        self.assertEqual(code, 2)
        self.assertIn("heading", err)


SONNET = "claude-sonnet-5-5"
BOUND_LIMITS = {
    IMPLEMENTATION: {"model": SONNET, "effort": "high", "output_tokens_max": 1000, "processed_tokens_max": 5000},
    REVIEW: {"model": "claude-opus-5-5", "effort": "high", "output_tokens_max": 800, "processed_tokens_max": 4000},
}


class BindingTests(ReportCase):
    """The model and the effort are bound to the profile; a mismatch is a red, an absent effort alone is not."""

    def setUp(self) -> None:
        super().setUp()
        self.expectation = self.write_json(BOUND_LIMITS)

    def one(
        self,
        model: str = SONNET,
        effort: str | None = "high",
        counts: tuple[int, int, int, int] = (100, 200, 300, 400),
        profile: str = IMPLEMENTATION,
    ) -> tuple[int, str, str]:
        drop = ["effort"] if effort is None else []
        replace = {"model": model}
        if effort is not None:
            replace["effort"] = effort
        return self.report(self.receipt(usage(profile, counts=counts, replace=replace, drop=drop)))

    def words(
        self,
        model: str = SONNET,
        effort: str | None = "high",
        counts: tuple[int, int, int, int] = (100, 200, 300, 400),
        profile: str = IMPLEMENTATION,
    ) -> tuple[int, str]:
        code, out, err = self.one(model, effort, counts, profile)
        self.assertEqual(len(out.splitlines()), 1, out + err)
        return code, out.split(" ")[-1].strip()

    def test_a_cell_matching_its_profile_prints_model_effort_and_within(self) -> None:
        self.assertEqual(
            self.one(),
            (0, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model={SONNET} effort=high output=400 processed=600 WITHIN\n", ""),
        )

    def test_another_model_is_a_mismatch_and_exit_one(self) -> None:
        self.assertEqual(self.words(model="claude-opus-5-5"), (1, "MODEL_MISMATCH"))

    def test_a_model_that_only_extends_the_expected_one_is_a_mismatch(self) -> None:
        self.assertEqual(self.words(model=SONNET + "-fast"), (1, "MODEL_MISMATCH"))
        self.assertEqual(self.words(model="claude-sonnet-5"), (1, "MODEL_MISMATCH"))

    def test_the_model_is_compared_case_sensitively(self) -> None:
        self.assertEqual(self.words(model="Claude-Sonnet-5-5"), (1, "MODEL_MISMATCH"))

    def test_two_models_in_one_cell_are_a_mismatch_in_either_order(self) -> None:
        for model in (f"{SONNET},claude-opus-5-5", f"claude-opus-5-5,{SONNET}"):
            with self.subTest(model=model):
                self.assertEqual(self.words(model=model), (1, "MODEL_MISMATCH"))

    def test_another_effort_is_a_mismatch_and_exit_one(self) -> None:
        self.assertEqual(self.words(effort="medium"), (1, "EFFORT_MISMATCH"))

    def test_the_effort_is_compared_case_sensitively(self) -> None:
        self.assertEqual(self.words(effort="High"), (1, "EFFORT_MISMATCH"))

    def test_two_efforts_in_one_cell_are_a_mismatch_in_either_order(self) -> None:
        for effort in ("high,medium", "medium,high"):
            with self.subTest(effort=effort):
                self.assertEqual(self.words(effort=effort), (1, "EFFORT_MISMATCH"))

    def test_the_line_prints_the_value_lists_as_written(self) -> None:
        code, out, _ = self.one(model=f"claude-opus-5-5,{SONNET}", effort="medium,high")
        self.assertEqual(code, 1)
        self.assertIn(f" model=claude-opus-5-5,{SONNET} effort=medium,high output=", out)

    def test_every_word_comes_in_the_fixed_order(self) -> None:
        self.assertEqual(
            self.words(model="other", effort="low", counts=(6000, 0, 0, 2000)),
            (1, "MODEL_MISMATCH,EFFORT_MISMATCH,OVER_OUTPUT,OVER_PROCESSED"),
        )
        self.assertEqual(self.words(model="other", counts=(6000, 0, 0, 1)), (1, "MODEL_MISMATCH,OVER_PROCESSED"))
        self.assertEqual(self.words(effort="low", counts=(1, 1, 1, 2000)), (1, "EFFORT_MISMATCH,OVER_OUTPUT"))

    def test_an_unrecorded_effort_alone_prints_the_word_and_is_exit_zero(self) -> None:
        code, out, err = self.one(effort=None)
        self.assertEqual(
            (code, out, err),
            (0, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} model={SONNET} effort=UNRECORDED output=400 processed=600 EFFORT_UNRECORDED\n", ""),
        )

    def test_within_is_never_printed_beside_an_unrecorded_effort(self) -> None:
        _, out, _ = self.one(effort=None)
        self.assertNotIn("WITHIN", out)

    def test_an_unrecorded_effort_comes_last_and_the_other_words_make_the_cell_red(self) -> None:
        self.assertEqual(self.words(effort=None, counts=(1, 1, 1, 2000)), (1, "OVER_OUTPUT,EFFORT_UNRECORDED"))
        self.assertEqual(self.words(effort=None, model="other"), (1, "MODEL_MISMATCH,EFFORT_UNRECORDED"))
        self.assertEqual(
            self.words(effort=None, model="other", counts=(6000, 0, 0, 2000)),
            (1, "MODEL_MISMATCH,OVER_OUTPUT,OVER_PROCESSED,EFFORT_UNRECORDED"),
        )

    def test_an_unknown_profile_stands_alone_with_or_without_an_effort_line(self) -> None:
        for effort in ("high", "low", None):
            with self.subTest(effort=effort):
                code, out, _ = self.one(model="other", effort=effort, counts=(9000, 0, 0, 9000), profile="made-up")
                self.assertEqual(code, 1)
                self.assertTrue(out.endswith(" UNKNOWN_PROFILE\n"), out)
                self.assertEqual(len(out.split(" ")), 7)

    def test_each_profile_has_its_own_model(self) -> None:
        self.assertEqual(self.words(model="claude-opus-5-5", profile=REVIEW), (0, "WITHIN"))
        self.assertEqual(self.words(model=SONNET, profile=REVIEW), (1, "MODEL_MISMATCH"))

    def test_every_red_is_listed_not_only_the_first(self) -> None:
        path = self.receipt(
            usage(replace={"model": "other"}),
            usage(REVIEW, "run-2", replace={"model": "claude-opus-5-5"}),
            usage(REVIEW, "run-3", replace={"model": "claude-opus-5-5", "effort": "low"}),
        )
        code, out, _ = self.report(path)
        self.assertEqual(code, 1)
        self.assertEqual([line.split(" ")[-1] for line in out.splitlines()], ["MODEL_MISMATCH", "WITHIN", "EFFORT_MISMATCH"])

    def test_a_red_beside_a_broken_receipt_still_prints_and_exits_one(self) -> None:
        red = self.receipt(usage(replace={"model": "other"}), name="red.md")
        broken = self.receipt(usage(replace={"effort": "a, b"}), name="broken.md")
        code, out, err = self.report(red, broken)
        self.assertEqual(code, 1)
        self.assertTrue(out.endswith("MODEL_MISMATCH\n"), out)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("effort", err)


class ValueGrammarTests(ReportCase):
    """A value that breaks the grammar is a schema break (exit 2), in a receipt and in the expectation."""

    BAD = ("", "a b", "a, b", "a ,b", "a,", ",a", "a,,b", "a,a", "a,b,a", "-a", "a/b", "a:b")

    def setUp(self) -> None:
        super().setUp()
        self.expectation = self.write_json(BOUND_LIMITS)

    def receipt_fault(self, **replace: str) -> str:
        code, out, err = self.report(self.receipt(usage(replace=replace)))
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertNotIn("Traceback", err)
        return err

    def test_a_bad_model_in_a_receipt_is_exit_two(self) -> None:
        for bad in self.BAD:
            with self.subTest(bad=bad):
                self.assertIn("model", self.receipt_fault(model=bad))

    def test_a_bad_effort_in_a_receipt_is_exit_two(self) -> None:
        for bad in self.BAD:
            with self.subTest(bad=bad):
                self.assertIn("effort", self.receipt_fault(effort=bad))

    def test_a_valid_list_in_a_receipt_is_read(self) -> None:
        code, out, _ = self.report(self.receipt(usage(replace={"model": "a.b_c-d,e", "effort": "x,y,z"})))
        self.assertEqual(code, 1)
        self.assertIn(" model=a.b_c-d,e effort=x,y,z ", out)

    def test_the_effort_line_stands_only_directly_after_the_model_line(self) -> None:
        lines = usage().split("\n")
        effort = lines.pop(lines.index("effort: high"))
        before_model = lines.copy()
        before_model.insert(before_model.index("model: a-model"), effort)
        after_source = [*lines[:-1], effort, ""]
        after_input = lines.copy()
        after_input.insert(after_input.index("cache_write_tokens: 200"), effort)
        for label, moved in (("before model", before_model), ("after source", after_source), ("later", after_input)):
            with self.subTest(label):
                code, out, err = self.report(self.receipt("\n".join(moved)))
                self.assertEqual((code, out), (2, ""), err)
                self.assertIn("out of order", err)

    def test_an_effort_line_given_twice_is_exit_two(self) -> None:
        self.assertIn("more than once", self.receipt_fault_extra("effort: high"))

    def receipt_fault_extra(self, line: str) -> str:
        code, out, err = self.report(self.receipt(usage(extra=[line])))
        self.assertEqual((code, out), (2, ""), err)
        return err

    def entry_fault(self, entry: dict[str, object]) -> str:
        code, out, err = self.report(self.receipt(usage()), expectation=self.write_json({IMPLEMENTATION: entry}, "entry.json"))
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        return err

    def good_entry(self) -> dict[str, object]:
        return {"model": "a-model", "effort": "high", "output_tokens_max": 1, "processed_tokens_max": 1}

    def test_an_expectation_entry_missing_model_or_effort_is_exit_two(self) -> None:
        for key in ("model", "effort"):
            with self.subTest(key=key):
                entry = self.good_entry()
                del entry[key]
                self.assertIn(f"lacks {key}", self.entry_fault(entry))

    def test_an_expectation_model_or_effort_that_is_not_one_item_is_exit_two(self) -> None:
        for key in ("model", "effort"):
            for bad in (*self.BAD, "a,b", "<host-model>", "<host-effort>", 5, None, True, ["a"]):
                with self.subTest(key=key, bad=bad):
                    entry = self.good_entry()
                    entry[key] = bad
                    self.assertIn(key, self.entry_fault(entry))

    def test_the_unfilled_template_is_a_schema_break(self) -> None:
        template = Path(__file__).resolve().parents[1] / "template" / "doc" / "handoffs" / "governance" / "usage-expectation.TEMPLATE.json"
        code, out, err = self.report(self.receipt(usage()), expectation=template)
        self.assertEqual((code, out), (2, ""), err)
        self.assertIn("<host-", err)

    def test_the_template_filled_with_the_fixture_values_gives_within(self) -> None:
        template = Path(__file__).resolve().parents[1] / "template" / "doc" / "handoffs" / "governance" / "usage-expectation.TEMPLATE.json"
        text = template.read_text(encoding="utf-8").replace("<host-model>", "a-model").replace("<host-effort>", "high")
        filled = self.base / "filled.json"
        filled.write_text(text, encoding="utf-8", newline="\n")
        code, out, err = self.report(self.receipt(usage(counts=(1, 1, 1, 1))), expectation=filled)
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(out.endswith(" WITHIN\n"), out)

    def test_a_list_in_the_expectation_is_refused_even_though_a_receipt_may_hold_one(self) -> None:
        entry = self.good_entry()
        entry["model"] = "a-model,b"
        self.assertIn("model", self.entry_fault(entry))

    def test_the_repository_expectation_file_is_read_and_names_all_three_profiles(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        path = repo / "doc" / "handoffs" / "2026" / "workflow-governance" / "usage-expectation.json"
        limits = usage_report.load_expectation(path)
        self.assertEqual(set(limits), {IMPLEMENTATION, "implementation-elevated", REVIEW})
        self.assertEqual((limits[IMPLEMENTATION].model, limits[IMPLEMENTATION].effort), ("claude-sonnet-5-5", "high"))
        self.assertEqual((limits[REVIEW].model, limits[REVIEW].effort), ("claude-opus-5-5", "high"))
        self.assertEqual(
            (limits["implementation-elevated"].model, limits["implementation-elevated"].effort),
            (limits[REVIEW].model, limits[REVIEW].effort),
        )


class PrintedSubjectTests(unittest.TestCase):
    def test_the_no_usage_subject_is_escaped_on_every_platform(self) -> None:
        self.assertEqual(usage_report.no_usage_line(Path("a b")), "NO_USAGE a\\u2028b")
        self.assertEqual(usage_report.no_usage_line(Path("x\ny")), "NO_USAGE x\\ny")
        self.assertEqual(usage_report.no_usage_line(Path("a\x0bb")), "NO_USAGE a\\x0bb")


if __name__ == "__main__":
    unittest.main()
