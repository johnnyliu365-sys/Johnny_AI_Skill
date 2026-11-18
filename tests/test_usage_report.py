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
    IMPLEMENTATION: {"output_tokens_max": 1000, "processed_tokens_max": 5000},
    REVIEW: {"output_tokens_max": 800, "processed_tokens_max": 4000},
}
FIELD_NAMES = (
    "cell",
    "seat",
    "profile",
    "model",
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
                f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} output=400 processed=600 WITHIN\n"
                f"seat:{REVIEW}/run-2 {REVIEW} output=40 processed=60 WITHIN\n",
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
        self.assertEqual((code, out), (0, f"seat:{IMPLEMENTATION}/run-1 {IMPLEMENTATION} output=0 processed=0 WITHIN\n"))

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
        self.assertEqual((code, out), (1, "seat:made-up/run-1 made-up output=400 processed=600 UNKNOWN_PROFILE\n"))

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
            with self.subTest(name=name):
                self.assertIn(name, self.fault(usage(drop=[name])))

    def test_a_repeated_field_is_exit_two(self) -> None:
        self.assertIn("more than once", self.fault(usage(extra=["model: other"])))

    def test_fields_out_of_order_are_exit_two(self) -> None:
        lines = usage().split("\n")
        lines[3], lines[4] = lines[4], lines[3]
        self.assertIn("out of order", self.fault("\n".join(lines)))

    def test_a_negative_or_non_integer_count_is_exit_two(self) -> None:
        for bad in ("-1", "1.5", "abc", "", "01", "1e3", "NaN"):
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

    def test_a_fault_wins_over_a_red_and_the_good_receipts_print_nothing_wrong(self) -> None:
        red = self.receipt(usage(counts=(1, 1, 1, 9999)), name="red.md")
        broken = self.receipt(usage(drop=["model"]), name="broken.md")
        code, _, err = self.report(red, broken)
        self.assertEqual(code, 2)
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
        text = '{"%s": {"output_tokens_max": 1, "processed_tokens_max": 2}, "%s": {"output_tokens_max": 1, "processed_tokens_max": 2}}' % (IMPLEMENTATION, IMPLEMENTATION)
        self.assertIn("repeated", self.fault_for(self.raw(text)))
        inner = '{"%s": {"output_tokens_max": 1, "output_tokens_max": 3, "processed_tokens_max": 2}}' % IMPLEMENTATION
        self.assertIn("repeated", self.fault_for(self.raw(inner)))

    def test_nan_and_infinity_are_exit_two(self) -> None:
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                text = '{"%s": {"output_tokens_max": %s, "processed_tokens_max": 2}}' % (IMPLEMENTATION, constant)
                self.assertIn("refused", self.fault_for(self.raw(text)))

    def test_a_missing_profile_key_is_exit_two(self) -> None:
        for key in ("output_tokens_max", "processed_tokens_max"):
            with self.subTest(key=key):
                entry = {name: 1 for name in ("output_tokens_max", "processed_tokens_max") if name != key}
                self.assertIn(key, self.fault_for(self.write_json({IMPLEMENTATION: entry})))

    def test_an_unknown_profile_key_is_exit_two(self) -> None:
        entry = {"output_tokens_max": 1, "processed_tokens_max": 2, "extra": 3}
        self.assertIn("extra", self.fault_for(self.write_json({IMPLEMENTATION: entry})))

    def test_a_limit_that_is_not_an_integer_is_exit_two(self) -> None:
        for bad in (-1, 1.5, "10", True, None, [1]):
            with self.subTest(bad=bad):
                entry = {"output_tokens_max": bad, "processed_tokens_max": 2}
                self.fault_for(self.write_json({IMPLEMENTATION: entry}))
        self.fault_for(self.raw('{"%s": {"output_tokens_max": 1e3, "processed_tokens_max": 2}}' % IMPLEMENTATION))

    def test_a_top_level_that_is_not_a_non_empty_object_is_exit_two(self) -> None:
        for value in ([], {}, 5, "x", None):
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
        path = self.write_json({IMPLEMENTATION: {"output_tokens_max": 0, "processed_tokens_max": 0}})
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


if __name__ == "__main__":
    unittest.main()
