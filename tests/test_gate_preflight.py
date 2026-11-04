"""Behavioural tests for the preflight gate script (exit codes 0/2/3, no red).

Every fixture is generated in a temporary directory; the tool under test is the running
interpreter. Expected values are derived from the text a fixture wrote or from what the
tool printed, never copied from the script.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import preflight  # noqa: E402

SCRIPT = _SCRIPTS / "preflight.py"
PY = sys.executable
NON_CP950 = chr(0x0E01)  # outside code page 950
LINE_SEPARATOR = chr(0x2028)
NEXT_LINE = chr(0x85)
HEARTBEAT_SECONDS = 20.0

HEARTBEAT_SCRIPT = """\
import subprocess, sys, time

beat = sys.argv[1]
if len(sys.argv) > 2:
    subprocess.Popen([sys.executable, __file__, sys.argv[2]])
deadline = time.time() + {seconds}
while time.time() < deadline:
    with open(beat, "ab") as handle:
        handle.write(b"x")
    time.sleep(0.05)
""".format(seconds=HEARTBEAT_SECONDS)


def py(code: str, *args: str) -> list[str]:
    return [PY, "-c", code, *args]


def say(text: str) -> list[str]:
    return py("import sys;sys.stdout.write(sys.argv[1])", text)


def item_lines(tool: str, start: list[str], probe: list[str], expect: str, ascii_only: bool = True) -> list[str]:
    def dump(value: object) -> str:
        return json.dumps(value, ensure_ascii=ascii_only)

    return [
        f"  - tool: {dump(tool)}",
        f"    start: {dump(start)}",
        f"    probe: {dump(probe)}",
        f"    expect: {dump(expect)}",
    ]


def good_item(tool: str = "tool-a", marker: str = "ready") -> list[str]:
    return item_lines(tool, say("started"), say(marker), marker)


def dispatch_text(*block: str, before: tuple[str, ...] = ("title: x",), after: tuple[str, ...] = (), newline: str = "\n") -> str:
    lines = [*before, "preflight:", *block, *after]
    return newline.join(lines) + newline


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.dir = Path(holder.name)
        self.path = self.dir / "dispatch.yaml"

    def write(self, text: str) -> Path:
        self.path.write_bytes(text.encode("utf-8"))
        return self.path

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = preflight.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def gate(self, text: str, *extra: str) -> tuple[int, str, str]:
        self.write(text)
        return self.run_main(str(self.path), *extra)

    def assert_grammar_error(self, text: str, line: int | None = None) -> str:
        code, out, err = self.gate(text)
        self.assertEqual(code, 3, (out, err))
        self.assertEqual(out, "")
        self.assertIn("usage:", err)
        if line is not None:
            self.assertIn(f"line {line}", err)
        return err


class ServedTests(Fixture):
    def test_two_served_tools_exit_zero(self) -> None:
        code, out, err = self.gate(dispatch_text(*good_item("a", "one"), *good_item("b", "two")))
        self.assertEqual((code, out, err), (0, "tools=2 served=2\n", ""))

    def test_start_runs_before_probe_in_the_dispatch_directory(self) -> None:
        start = py("open('marker.txt','w').write('ready-now')")
        probe = py("print(open('marker.txt').read())")
        code, out, _ = self.gate(dispatch_text(*item_lines("t", start, probe, "ready-now")))
        self.assertEqual((code, out), (0, "tools=1 served=1\n"))
        self.assertEqual((self.dir / "marker.txt").read_text(), "ready-now")
        self.assertFalse((Path.cwd() / "marker.txt").exists())

    def test_the_block_ends_at_the_next_column_zero_line(self) -> None:
        text = dispatch_text(
            *good_item(),
            after=("cells:", "  - tool: not-a-preflight-item", "    start: not json"),
        )
        self.assertEqual(self.gate(text)[0], 0)

    def test_text_before_the_block_is_ignored(self) -> None:
        text = dispatch_text(*good_item(), before=("title: x", "  - tool: stray", "note: free text"))
        self.assertEqual(self.gate(text)[0], 0)

    def test_blank_lines_inside_the_block_are_skipped(self) -> None:
        item = good_item()
        text = dispatch_text(item[0], "", item[1], "   ", *item[2:])
        self.assertEqual(self.gate(text)[0], 0)

    def test_crlf_parses_like_lf(self) -> None:
        block = good_item("a", "one") + good_item("b", "two")
        lf = self.gate(dispatch_text(*block))
        crlf = self.gate(dispatch_text(*block, newline="\r\n"))
        self.assertEqual(lf, crlf)
        self.assertEqual(crlf[0], 0)

    def test_utf8_byte_order_mark_is_accepted(self) -> None:
        self.path.write_bytes(b"\xef\xbb\xbf" + dispatch_text(*good_item()).encode("utf-8"))
        self.assertEqual(self.run_main(str(self.path))[0], 0)

    def test_parse_returns_typed_items_with_their_line(self) -> None:
        text = dispatch_text(*item_lines("t", ["a", "b"], ["c"], "e"), before=("x: 1",))
        (parsed,) = preflight.parse_preflight(text)
        self.assertEqual(parsed, preflight.PreflightItem(line=3, tool="t", start=("a", "b"), probe=("c",), expect="e"))

    def test_probe_output_on_stderr_counts(self) -> None:
        probe = py("import sys;sys.stderr.write('from-stderr')")
        self.assertEqual(self.gate(dispatch_text(*item_lines("t", say("s"), probe, "from-stderr")))[0], 0)

    def test_expect_may_be_a_substring_anywhere_in_the_output(self) -> None:
        probe = py("print('alpha beta gamma');print('version 3.2 ok')")
        self.assertEqual(self.gate(dispatch_text(*item_lines("t", say("s"), probe, "3.2 ok")))[0], 0)

    def test_timeout_option_is_accepted(self) -> None:
        code, out, _ = self.gate(dispatch_text(*good_item()), "--timeout", "30.5")
        self.assertEqual((code, out), (0, "tools=1 served=1\n"))


class GrammarTests(Fixture):
    def test_no_block_is_exit_three(self) -> None:
        self.assert_grammar_error("title: x\nrole: seat\n")

    def test_indented_key_is_not_a_block(self) -> None:
        self.assert_grammar_error("title: x\n  preflight:\n" + "\n".join(good_item()) + "\n")

    def test_empty_block_is_exit_three(self) -> None:
        self.assert_grammar_error(dispatch_text(after=("cells:",)))

    def test_block_header_with_a_value_is_exit_three(self) -> None:
        self.assert_grammar_error("preflight: []\n", line=1)

    def test_second_block_is_exit_three(self) -> None:
        self.assert_grammar_error(dispatch_text(*good_item(), after=("preflight:", *good_item("b"))), line=7)

    def test_each_missing_key_is_exit_three_naming_the_item_line(self) -> None:
        full = good_item()
        keys = ("tool", "start", "probe", "expect")
        for drop in (1, 2, 3):
            with self.subTest(missing=keys[drop]):
                kept = [line for number, line in enumerate(full) if number != drop]
                err = self.assert_grammar_error(dispatch_text(*kept), line=3)
                self.assertIn(f"lacks the key {keys[drop]}", err)

    def test_an_item_without_a_tool_line_is_exit_three(self) -> None:
        self.assert_grammar_error(dispatch_text(*good_item()[1:]), line=3)

    def test_a_value_that_is_not_json_names_its_line(self) -> None:
        for key, number in (("tool", 3), ("start", 4), ("probe", 5), ("expect", 6)):
            with self.subTest(key=key):
                lines = good_item()
                index = ("tool", "start", "probe", "expect").index(key)
                prefix = lines[index].split(":", 1)[0]
                lines[index] = prefix + ": not json"
                self.assert_grammar_error(dispatch_text(*lines), line=number)

    def test_two_json_values_on_one_line_are_refused(self) -> None:
        lines = good_item()
        lines[3] = '    expect: "a" "b"'
        self.assert_grammar_error(dispatch_text(*lines), line=6)

    def test_a_key_with_no_value_is_refused(self) -> None:
        lines = good_item()
        lines[1] = "    start:"
        self.assert_grammar_error(dispatch_text(*lines), line=4)

    def test_wrong_types_are_refused(self) -> None:
        wrong = {
            "tool": ['["a"]', "1", "null", "true"],
            "expect": ["1", "null", '["a"]'],
            "start": ['"python"', "1", "null", '{"a": 1}', '["a", 1]', '["a", null]', '[["a"]]'],
            "probe": ['"python"', "null", '["a", false]'],
        }
        keys = ("tool", "start", "probe", "expect")
        for key, values in wrong.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    lines = good_item()
                    index = keys.index(key)
                    lines[index] = lines[index].split(":", 1)[0] + ": " + value
                    self.assert_grammar_error(dispatch_text(*lines), line=3 + index)

    def test_empty_argument_arrays_are_refused(self) -> None:
        for key in ("start", "probe"):
            with self.subTest(key=key):
                lines = good_item()
                index = ("tool", "start", "probe", "expect").index(key)
                lines[index] = lines[index].split(":", 1)[0] + ": []"
                self.assert_grammar_error(dispatch_text(*lines), line=3 + index)

    def test_empty_program_name_is_refused(self) -> None:
        lines = item_lines("t", [""], say("x"), "x")
        self.assert_grammar_error(dispatch_text(*lines), line=4)

    def test_empty_expect_is_refused_not_accepted(self) -> None:
        lines = item_lines("t", say("s"), say("anything"), "")
        err = self.assert_grammar_error(dispatch_text(*lines), line=6)
        self.assertIn("expect", err)

    def test_empty_or_blank_tool_name_is_refused(self) -> None:
        for name in ("", "   "):
            with self.subTest(name=name):
                self.assert_grammar_error(dispatch_text(*item_lines(name, say("s"), say("x"), "x")), line=3)

    def test_a_key_at_the_wrong_indent_is_refused_naming_the_line(self) -> None:
        for indent in ("", " ", "  ", "   ", "     ", "\t"):
            with self.subTest(indent=repr(indent)):
                lines = good_item()
                lines[2] = indent + lines[2].lstrip()
                code, _, err = self.gate(dispatch_text(*lines))
                self.assertEqual(code, 3)
                if indent:
                    self.assertIn("line 5", err)
        lines = good_item()
        lines[0] = "- tool: \"t\""
        self.assert_grammar_error(dispatch_text(*lines))
        lines = good_item()
        lines[0] = "    - tool: \"t\""
        self.assert_grammar_error(dispatch_text(*lines), line=3)

    def test_an_unknown_key_is_refused(self) -> None:
        lines = [*good_item(), '    note: "x"']
        err = self.assert_grammar_error(dispatch_text(*lines), line=7)
        self.assertIn("note", err)

    def test_a_repeated_key_is_refused(self) -> None:
        for extra in ('    expect: "y"', '    tool: "y"', "    start: [\"p\"]"):
            with self.subTest(extra=extra):
                self.assert_grammar_error(dispatch_text(*good_item(), extra), line=7)

    def test_a_key_before_the_first_item_is_refused(self) -> None:
        self.assert_grammar_error(dispatch_text('    start: ["p"]', *good_item()), line=3)

    def test_an_item_line_that_is_not_tool_first_is_refused(self) -> None:
        self.assert_grammar_error(dispatch_text('  - start: ["p"]'), line=3)

    def test_prose_inside_the_block_is_refused(self) -> None:
        self.assert_grammar_error(dispatch_text(*good_item(), "  just some words"), line=7)

    def test_file_that_is_not_utf8_is_exit_three(self) -> None:
        self.path.write_bytes(b"preflight:\n  - tool: \"\xff\"\n")
        code, _, err = self.run_main(str(self.path))
        self.assertEqual(code, 3)
        self.assertIn("UTF-8", err)


class TextValueTests(Fixture):
    """Lone surrogates and control characters are refused as exit 3, never a red (exit 1)."""

    BAD = {
        "lone high surrogate": '"\\ud800"',
        "lone low surrogate": '"a\\udfffb"',
        "NUL": '"\\u0000"',
        "newline": '"a\\nb"',
        "carriage return": '"a\\rb"',
        "tab": '"a\\tb"',
        "escape": '"\\u001b[0m"',
        "delete": '"\\u007f"',
    }

    def test_each_bad_string_is_exit_three_in_every_text_field(self) -> None:
        keys = ("tool", "start", "probe", "expect")
        for key in keys:
            for label, bad in self.BAD.items():
                with self.subTest(key=key, bad=label):
                    lines = good_item()
                    index = keys.index(key)
                    value = bad if key in ("tool", "expect") else f'["p", {bad}]'
                    lines[index] = lines[index].split(":", 1)[0] + ": " + value
                    code, out, err = self.gate(dispatch_text(*lines))
                    self.assertEqual(code, 3, (out, err))
                    self.assertEqual(out, "")
                    self.assertIn(f"line {3 + index}", err)
                    self.assertEqual(len(err.splitlines()), 2)

    def test_raw_control_characters_in_a_block_line_are_exit_three(self) -> None:
        for char in ("\x00", "\x01", "\x0b", "\x0c", "\x1b", "\x7f", "\t"):
            with self.subTest(char=repr(char)):
                lines = good_item()
                lines[3] = f'    expect: "a{char}b"'
                self.assert_grammar_error(dispatch_text(*lines), line=6)

    def test_a_control_character_between_json_tokens_is_exit_three(self) -> None:
        """A tab or a stray carriage return is legal JSON whitespace but a control character of the input."""
        for tail in ("\t", "\r\r", " \t", "\x0b"):
            with self.subTest(tail=repr(tail)):
                lines = good_item()
                lines[1] = lines[1] + tail
                code, out, err = self.gate(dispatch_text(*lines))
                self.assertEqual((code, out), (3, ""))
                self.assertIn("line 4", err)
        lines = good_item()
        lines[1] = lines[1].replace('["', '[\t"', 1)
        self.assert_grammar_error(dispatch_text(*lines), line=4)

    def test_a_paired_surrogate_escape_is_one_valid_character(self) -> None:
        probe = say(chr(0x1F600))
        lines = item_lines("t", say("s"), probe, chr(0x1F600), ascii_only=True)
        self.assertIn("\\ud83d\\ude00", "".join(lines))
        self.assertEqual(self.gate(dispatch_text(*lines))[0], 0)

    def test_a_text_defect_never_exits_one(self) -> None:
        for bad in self.BAD.values():
            lines = good_item()
            lines[3] = f"    expect: {bad}"
            self.assertNotEqual(self.gate(dispatch_text(*lines))[0], 1)

    def test_a_printed_tool_name_is_one_line(self) -> None:
        name = f"x{LINE_SEPARATOR}TOOL_UNSERVED forged{NEXT_LINE}y\\z"
        lines = item_lines(name, [str(self.dir / "absent-program")], say("x"), "x", ascii_only=False)
        code, out, _ = self.gate(dispatch_text(*lines))
        self.assertEqual(code, 2)
        self.assertEqual(len(out.splitlines()), 1)
        self.assertEqual(len(out.split("\n")), 2)
        self.assertIn("\\u2028", out)
        self.assertIn("\\x85", out)
        self.assertIn("\\\\z", out)

    def test_a_printed_expectation_is_one_line(self) -> None:
        lines = item_lines("t", say("s"), say("x"), f"a{LINE_SEPARATOR}b{NEXT_LINE}c", ascii_only=False)
        code, out, _ = self.gate(dispatch_text(*lines))
        self.assertEqual(code, 2)
        self.assertEqual(len(out.splitlines()), 1)
        self.assertIn("does not contain", out)

    def test_escape_makes_one_printable_line(self) -> None:
        self.assertEqual(preflight.escape("plain 文字"), "plain 文字")
        self.assertEqual(preflight.escape("a\\b"), "a\\\\b")
        self.assertEqual(preflight.escape("\n\r\x00\x7f"), "\\x0a\\x0d\\x00\\x7f")
        self.assertEqual(preflight.escape(LINE_SEPARATOR), "\\u2028")
        self.assertEqual(preflight.escape(chr(0x10FFFF)), "\\U0010ffff")
        self.assertEqual(preflight.escape("\ud800"), "\\ud800")


class ArgumentTests(Fixture):
    def test_no_argument_is_exit_three(self) -> None:
        code, out, err = self.run_main()
        self.assertEqual((code, out), (3, ""))
        self.assertTrue(err.startswith("usage:"))

    def test_two_files_are_exit_three(self) -> None:
        self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_main(str(self.path), str(self.path))[0], 3)

    def test_unknown_option_is_exit_three(self) -> None:
        self.write(dispatch_text(*good_item()))
        for option in ("--verbose", "-t", "--timeout=5"):
            with self.subTest(option=option):
                self.assertEqual(self.run_main(str(self.path), option)[0], 3)

    def test_an_unknown_option_alone_is_exit_three_not_a_file_name(self) -> None:
        for option in ("--verbose", "-x"):
            with self.subTest(option=option):
                code, out, err = self.run_main(option)
                self.assertEqual((code, out), (3, ""))
                self.assertIn("unknown option", err)

    def test_bad_timeout_values_are_exit_three(self) -> None:
        self.write(dispatch_text(*good_item()))
        for value in ("0", "0.0", "-1", "abc", "", "nan", "inf", "1e3", "1_0", "86401", "99999999999999999999", " 5"):
            with self.subTest(value=value):
                code, out, err = self.run_main(str(self.path), "--timeout", value)
                self.assertEqual((code, out), (3, ""))
                self.assertIn("--timeout", err)

    def test_timeout_without_a_value_or_twice_is_exit_three(self) -> None:
        self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_main(str(self.path), "--timeout")[0], 3)
        self.assertEqual(self.run_main(str(self.path), "--timeout", "5", "--timeout", "6")[0], 3)

    def test_timeout_may_come_before_the_file(self) -> None:
        self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_main("--timeout", "30", str(self.path))[0], 0)

    def test_arguments_are_checked_before_the_file_is_read(self) -> None:
        self.assertEqual(self.run_main(str(self.dir / "absent.yaml"), "--timeout", "0")[0], 3)


class UnservedTests(Fixture):
    def unserved(self, *block: str, timeout: str | None = None) -> list[str]:
        extra = () if timeout is None else ("--timeout", timeout)
        code, out, err = self.gate(dispatch_text(*block), *extra)
        self.assertEqual(code, 2, (out, err))
        self.assertEqual(err, "")
        return out.splitlines()

    def test_start_that_cannot_be_launched(self) -> None:
        (line,) = self.unserved(*item_lines("tool-x", [str(self.dir / "absent-program")], say("x"), "x"))
        self.assertTrue(line.startswith("TOOL_UNSERVED tool-x: start cannot be launched"), line)

    def test_probe_that_cannot_be_launched(self) -> None:
        (line,) = self.unserved(*item_lines("tool-x", say("s"), [str(self.dir / "absent-program")], "x"))
        self.assertTrue(line.startswith("TOOL_UNSERVED tool-x: probe cannot be launched"), line)

    def test_not_executable_programs_cannot_be_launched(self) -> None:
        plain = self.dir / "plain.txt"
        plain.write_text("not a program")
        for target in (plain, self.dir):
            with self.subTest(target=target.name):
                (line,) = self.unserved(*item_lines("t", [str(target)], say("x"), "x"))
                self.assertIn("start cannot be launched", line)

    def test_start_that_exits_non_zero(self) -> None:
        marker = self.dir / "probe-ran"
        probe = py("open(__import__('sys').argv[1],'w')", str(marker))
        (line,) = self.unserved(*item_lines("tool-x", py("raise SystemExit(7)"), probe, "x"))
        self.assertEqual(line, "TOOL_UNSERVED tool-x: start exited with code 7")
        self.assertFalse(marker.exists(), "probe must not run after a failed start")

    def test_probe_that_exits_non_zero(self) -> None:
        probe = py("import sys;sys.stdout.write('expected-text');raise SystemExit(4)")
        (line,) = self.unserved(*item_lines("tool-x", say("s"), probe, "expected-text"))
        self.assertEqual(line, "TOOL_UNSERVED tool-x: probe exited with code 4")

    def test_probe_output_without_the_expected_text(self) -> None:
        (line,) = self.unserved(*item_lines("tool-x", say("s"), say("something else"), "needle"))
        self.assertEqual(line, 'TOOL_UNSERVED tool-x: probe output does not contain the expected text "needle"')

    def test_expect_is_case_sensitive(self) -> None:
        (line,) = self.unserved(*item_lines("t", say("s"), say("Ready"), "ready"))
        self.assertIn("does not contain", line)

    def test_expect_is_compared_exactly_not_as_a_pattern(self) -> None:
        (line,) = self.unserved(*item_lines("t", say("s"), say("abc"), "a.c"))
        self.assertIn("does not contain", line)

    def test_a_long_expectation_is_shortened_in_the_report(self) -> None:
        (line,) = self.unserved(*item_lines("t", say("s"), say("x"), "q" * 500))
        self.assertLess(len(line), 300)

    def test_every_failing_tool_is_reported_not_only_the_first(self) -> None:
        block = [
            *item_lines("one", py("raise SystemExit(1)"), say("x"), "x"),
            *good_item("fine"),
            *item_lines("two", say("s"), say("x"), "needle"),
            *item_lines("three", say("s"), py("raise SystemExit(2)"), "x"),
        ]
        lines = self.unserved(*block)
        self.assertEqual(len(lines), 3)
        self.assertEqual([line.split(":", 1)[0] for line in lines], ["TOOL_UNSERVED one", "TOOL_UNSERVED two", "TOOL_UNSERVED three"])
        self.assertEqual(len({line.split(": ", 1)[1] for line in lines}), 3)

    def test_two_failing_tools_are_two_lines_and_a_served_tool_adds_none(self) -> None:
        block = [
            *item_lines("a", [str(self.dir / "absent-1")], say("x"), "x"),
            *item_lines("b", [str(self.dir / "absent-2")], say("x"), "x"),
        ]
        lines = self.unserved(*block)
        self.assertEqual(len(lines), 2)

    def test_dispatch_that_cannot_be_read_is_exit_two(self) -> None:
        for target in (self.dir / "absent.yaml", self.dir):
            with self.subTest(target=target.name):
                code, out, err = self.run_main(str(target))
                self.assertEqual((code, out), (2, ""))
                self.assertIn("cannot read", err)
                self.assertNotIn("Traceback", err)

    def test_an_unexpected_error_is_a_tool_fault_not_a_traceback(self) -> None:
        self.write(dispatch_text(*good_item()))
        with mock.patch.object(preflight, "check_item", side_effect=RuntimeError("boom")):
            code, out, err = self.run_main(str(self.path))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("boom", err)
        self.assertNotIn("Traceback", err)

    def test_only_the_three_exit_codes_occur(self) -> None:
        cases = [
            dispatch_text(*good_item()),
            dispatch_text(*item_lines("t", say("s"), say("x"), "y")),
            dispatch_text(*item_lines("t", say("s"), say("x"), "")),
            "no block\n",
        ]
        self.assertEqual([self.gate(text)[0] for text in cases], [0, 2, 3, 3])


class TimeoutTests(Fixture):
    def heartbeat(self) -> Path:
        script = self.dir / "heartbeat.py"
        script.write_text(HEARTBEAT_SCRIPT, encoding="utf-8")
        return script

    def assert_silent(self, *beats: Path) -> None:
        """Every heartbeat file exists and stops growing."""
        time.sleep(0.8)
        first = [beat.stat().st_size for beat in beats]
        time.sleep(0.8)
        second = [beat.stat().st_size for beat in beats]
        self.assertEqual(first, second, "a process is still running after the gate returned")
        for size in second:
            self.assertGreater(size, 0, "the child never started")

    def test_start_timeout_kills_the_child_and_reports_a_timeout(self) -> None:
        beat = self.dir / "beat-start"
        began = time.monotonic()
        code, out, _ = self.gate(
            dispatch_text(*item_lines("tool-x", [PY, str(self.heartbeat()), str(beat)], say("x"), "x")),
            "--timeout", "2",
        )
        elapsed = time.monotonic() - began
        self.assertEqual(code, 2)
        self.assertEqual(out.splitlines(), ["TOOL_UNSERVED tool-x: start timed out after 2s and was killed"])
        self.assertLess(elapsed, HEARTBEAT_SECONDS - 2)
        self.assert_silent(beat)

    def test_probe_timeout_kills_the_child_and_reports_a_timeout(self) -> None:
        beat = self.dir / "beat-probe"
        code, out, _ = self.gate(
            dispatch_text(*item_lines("tool-x", say("s"), [PY, str(self.heartbeat()), str(beat)], "x")),
            "--timeout", "2",
        )
        self.assertEqual(code, 2)
        self.assertEqual(out.splitlines(), ["TOOL_UNSERVED tool-x: probe timed out after 2s and was killed"])
        self.assert_silent(beat)

    def test_a_timed_out_child_leaves_its_own_children_dead_too(self) -> None:
        beat, grand = self.dir / "beat-parent", self.dir / "beat-grand"
        code, out, _ = self.gate(
            dispatch_text(*item_lines("t", say("s"), [PY, str(self.heartbeat()), str(beat), str(grand)], "x")),
            "--timeout", "2",
        )
        self.assertEqual(code, 2, out)
        self.assert_silent(beat, grand)

    def test_a_timeout_does_not_stop_the_other_tools(self) -> None:
        beat = self.dir / "beat-first"
        block = [
            *item_lines("slow", say("s"), [PY, str(self.heartbeat()), str(beat)], "x"),
            *item_lines("after", say("s"), say("x"), "needle"),
        ]
        code, out, _ = self.gate(dispatch_text(*block), "--timeout", "2")
        self.assertEqual(code, 2)
        lines = out.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("timed out", lines[0])
        self.assertIn("does not contain", lines[1])

    def test_a_child_inside_the_limit_is_not_killed(self) -> None:
        probe = py("import time;time.sleep(0.3);print('late-but-ok')")
        self.assertEqual(self.gate(dispatch_text(*item_lines("t", say("s"), probe, "late-but-ok")), "--timeout", "30")[0], 0)


class RegressionTests(Fixture):
    def test_shell_metacharacters_are_passed_literally(self) -> None:
        text = "a && b | c > redirected.txt ; d $(e) `f` %G% ^h"
        code, out, _ = self.gate(dispatch_text(*item_lines("t", say("s"), say(text), text)))
        self.assertEqual((code, out), (0, "tools=1 served=1\n"))
        self.assertFalse((self.dir / "redirected.txt").exists())
        self.assertEqual(os.listdir(self.dir), ["dispatch.yaml"])

    def test_a_program_name_with_shell_syntax_is_not_interpreted(self) -> None:
        name = f"{PY} -c pass && echo hi"
        (line,) = self.gate(dispatch_text(*item_lines("t", [name], say("x"), "x")))[1].splitlines()
        self.assertIn("start cannot be launched", line)

    def test_the_gate_runs_no_shell(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("shell=True", source)
        self.assertNotIn("os.system", source)

    def test_invalid_utf8_output_is_matched_after_replacement(self) -> None:
        probe = py("import sys;sys.stdout.buffer.write(b'\\xff\\xfe-tail-ok\\n')")
        self.assertEqual(self.gate(dispatch_text(*item_lines("t", say("s"), probe, "-tail-ok")))[0], 0)
        replaced = chr(0xFFFD) + chr(0xFFFD) + "-tail-ok"
        self.assertEqual(self.gate(dispatch_text(*item_lines("t", say("s"), probe, replaced)))[0], 0)

    def test_a_probe_that_reads_stdin_gets_end_of_file(self) -> None:
        probe = py("import sys;print('eof' if sys.stdin.read() == '' else 'data')")
        self.write(dispatch_text(*item_lines("t", say("s"), probe, "eof")))
        completed = subprocess.run(
            [PY, str(SCRIPT), str(self.path)], input=b"supplied input\n", capture_output=True, timeout=60
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_a_start_that_reads_stdin_does_not_hang(self) -> None:
        start = py("import sys;sys.stdin.read()")
        self.assertEqual(self.gate(dispatch_text(*item_lines("t", start, say("x"), "x")), "--timeout", "30")[0], 0)


class CommandLineTests(Fixture):
    def run_script(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
        merged = dict(os.environ)
        if env:
            merged.update(env)
        return subprocess.run([PY, str(SCRIPT), *args], capture_output=True, timeout=120, env=merged)

    def test_served_run(self) -> None:
        self.write(dispatch_text(*good_item()))
        done = self.run_script(str(self.path))
        self.assertEqual((done.returncode, done.stdout.decode().strip(), done.stderr), (0, "tools=1 served=1", b""))

    def test_unserved_run_has_no_traceback(self) -> None:
        self.write(dispatch_text(*item_lines("t", say("s"), say("x"), "y")))
        done = self.run_script(str(self.path))
        self.assertEqual(done.returncode, 2)
        self.assertNotIn(b"Traceback", done.stderr)
        self.assertEqual(done.stdout.decode().count("TOOL_UNSERVED"), 1)

    def test_usage_error_run_has_no_traceback(self) -> None:
        done = self.run_script()
        self.assertEqual(done.returncode, 3)
        self.assertTrue(done.stderr.decode().startswith("usage:"))
        self.assertNotIn(b"Traceback", done.stderr)

    def test_console_encoding_never_changes_the_exit_code(self) -> None:
        lines = item_lines(f"name-{NON_CP950}", say("s"), say("x"), "y", ascii_only=False)
        self.write(dispatch_text(*lines))
        done = self.run_script(str(self.path), env={"PYTHONIOENCODING": "cp950"})
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn(b"\\u0e01", done.stdout)


if __name__ == "__main__":
    unittest.main()
