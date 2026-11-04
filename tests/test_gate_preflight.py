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

    def test_whitespace_only_expect_is_refused(self) -> None:
        for text in (" ", "   ", chr(0xA0), chr(0x2028), chr(0x3000), " " + chr(0xA0) + " "):
            with self.subTest(text=repr(text)):
                lines = item_lines("t", say("s"), say(" " * 4), text)
                err = self.assert_grammar_error(dispatch_text(*lines), line=6)
                self.assertIn("expect", err)
        padded = item_lines("t", say("s"), say(" x "), " x ")
        self.assertEqual(self.gate(dispatch_text(*padded))[0], 0)

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
        for char in ("\x00", "\x01", "\x0b", "\x0c", "\x1b", "\x1f", "\x7f", "\t"):
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
        for value in (
            "0", "0.0", "-1", "abc", "", "nan", "inf", "1e3", "1_0", "86401", "99999999999999999999", " 5",
            "5\n", "5\r\n", "5 ", "5\t", "\n5", chr(0xFF15), "5\x1f", "5\x00", "5\udc80",
        ):
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
        # Revision02: the error is the cause of that one tool (a TOOL_UNSERVED line on stdout), no longer a run-ending message.
        self.write(dispatch_text(*good_item()))
        with mock.patch.object(preflight, "check_item", side_effect=RuntimeError("boom")):
            code, out, err = self.run_main(str(self.path))
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(out, "TOOL_UNSERVED tool-a: unexpected error (RuntimeError: boom)\n")
        self.assertNotIn("Traceback", out)

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


WINDOWS = sys.platform == "win32"
PATHEXT_DEFAULT = ".COM;.EXE;.BAT;.CMD"


def program_name(base: str) -> str:
    """The file name a fake program gets so that the platform treats it as a program."""
    return base + (".exe" if WINDOWS else "")


class ArgumentTextTests(Fixture):
    """The dispatch-path argument and --timeout follow the text-value rule, before anything is read."""

    BAD_ARGUMENTS = {
        "LF": "a\nb",
        "TAB": "a\tb",
        "ESC": "a\x1bb",
        "NUL": "a\x00b",
        "U+001F": "a\x1fb",
        "DEL": "a\x7fb",
        "CR": "a\rb",
        "lone surrogate": "a\udc80b",
        "lone high surrogate": "\ud800",
        "trailing LF": "dispatch.yaml\n",
    }

    def run_without_reading(self, *args: str) -> tuple[int, str, str]:
        with mock.patch("builtins.open", side_effect=AssertionError("the file was read")):
            return self.run_main(*args)

    def test_a_bad_dispatch_path_is_exit_three_and_nothing_is_read(self) -> None:
        for label, name in self.BAD_ARGUMENTS.items():
            with self.subTest(bad=label):
                code, out, err = self.run_without_reading(name)
                self.assertEqual((code, out), (3, ""), err)
                self.assertIn("argument 1", err)
                self.assertEqual(len(err.splitlines()), 2)
                self.assertNotIn(name, err)

    def test_a_path_that_names_an_existing_file_is_still_refused_when_the_name_has_a_control_character(self) -> None:
        self.write(dispatch_text(*good_item()))
        for suffix in ("\n", "\t", "\x1b", "\x1f"):
            with self.subTest(suffix=repr(suffix)):
                self.assertEqual(self.run_main(str(self.path) + suffix)[0], 3)

    def test_a_bad_timeout_text_is_exit_three_and_nothing_is_read(self) -> None:
        for label, value in {**self.BAD_ARGUMENTS, "trailing LF": "5\n", "leading space": " 5", "trailing space": "5 "}.items():
            with self.subTest(bad=label):
                code, out, err = self.run_without_reading(str(self.path), "--timeout", value)
                self.assertEqual((code, out), (3, ""), err)
                self.assertEqual(len(err.splitlines()), 2)
                if preflight._bad_character(value) is not None:
                    self.assertIn("argument 3 holds", err)

    def test_a_timeout_text_is_matched_in_full(self) -> None:
        self.write(dispatch_text(*good_item()))
        for value in ("5", "5.", ".5", "0.5", "005", "30.25"):
            with self.subTest(value=value):
                self.assertEqual(self.run_main(str(self.path), "--timeout", value)[0], 0)
        for value in ("5\n", "5\n\n", "5\x00", "5e1", "+5", "5 ", chr(0xFF15)):
            with self.subTest(value=repr(value)):
                self.assertEqual(self.run_main(str(self.path), "--timeout", value)[0], 3)

    def test_the_default_timeout_is_one_hundred_and_twenty_seconds(self) -> None:
        self.assertEqual(preflight.DEFAULT_TIMEOUT, 120.0)
        self.write(dispatch_text(*good_item()))
        seen: list[float] = []

        def record(item: preflight.PreflightItem, cwd: str, timeout: float) -> None:
            seen.append(timeout)

        with mock.patch.object(preflight, "check_item", side_effect=record):
            self.assertEqual(self.run_main(str(self.path))[0], 0)
            self.assertEqual(self.run_main(str(self.path), "--timeout", "7")[0], 0)
        self.assertEqual(seen, [120.0, 7.0])

    def test_a_path_with_line_breaking_characters_prints_on_one_line_when_it_cannot_be_read(self) -> None:
        name = self.dir / f"x{LINE_SEPARATOR}y{NEXT_LINE}z"
        code, out, err = self.run_main(str(name))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)
        self.assertEqual(len(err.split("\n")), 2)
        self.assertIn("\\u2028", err)
        self.assertIn("\\x85", err)
        self.assertNotIn(LINE_SEPARATOR, err)

    def test_a_path_with_line_breaking_characters_prints_on_one_line_when_the_file_is_not_utf8(self) -> None:
        name = self.dir / f"x{LINE_SEPARATOR}y{NEXT_LINE}z.yaml"
        name.write_bytes(b"\xff\xfe")
        code, out, err = self.run_main(str(name))
        self.assertEqual((code, out), (3, ""))
        self.assertEqual(len(err.splitlines()), 2)
        self.assertIn("\\u2028", err)
        self.assertNotIn(LINE_SEPARATOR, err)


class BoundaryTests(Fixture):
    """The edges of the text rule and of the block, pinned."""

    def test_the_control_range_ends_at_u001f_and_is_u007f(self) -> None:
        for code, refused in ((0x1E, True), (0x1F, True), (0x20, False), (0x7E, False), (0x7F, True), (0x80, False)):
            with self.subTest(code=hex(code)):
                lines = good_item()
                lines[1] = f'    start: ["p", "a\\u{code:04x}b"]'
                if refused:
                    self.assert_grammar_error(dispatch_text(*lines), line=4)
                else:
                    (item,) = preflight.parse_preflight(dispatch_text(*lines))
                    self.assertEqual(item.start, ("p", f"a{chr(code)}b"))

    def test_a_tab_only_line_inside_the_block_is_exit_three(self) -> None:
        for filler in ("\t", "  \t", "\t  ", "    \t"):
            with self.subTest(filler=repr(filler)):
                item = good_item()
                self.assert_grammar_error(dispatch_text(item[0], filler, *item[1:]), line=4)

    def test_a_space_only_line_inside_the_block_is_skipped(self) -> None:
        item = good_item()
        self.assertEqual(self.gate(dispatch_text(item[0], "      ", *item[1:]))[0], 0)


class Argv0Tests(Fixture):
    """The gate resolves the program name itself: absolute as given, relative with a separator against the
    dispatch directory, a bare name in PATH only; batch files are refused."""

    def chdir(self, path: Path) -> None:
        old = os.getcwd()
        os.chdir(path)
        self.addCleanup(os.chdir, old)

    def fake(self, directory: Path, name: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_bytes(b"")
        path.chmod(0o755)
        return path

    def search_path(self, *directories: str) -> contextlib.AbstractContextManager[object]:
        return mock.patch.dict(os.environ, {"PATH": os.pathsep.join(directories), "PATHEXT": PATHEXT_DEFAULT})

    def test_an_absolute_name_is_used_as_given(self) -> None:
        program = self.fake(self.dir / "bin", program_name("tool"))
        self.assertEqual(preflight.resolve_argv0(str(program), str(self.dir / "elsewhere")), str(program))

    def test_a_relative_name_with_a_separator_is_joined_to_the_dispatch_directory(self) -> None:
        dispatch_dir, gate_dir = self.dir / "dispatch", self.dir / "gate"
        wanted = self.fake(dispatch_dir / "sub", program_name("prog"))
        self.fake(gate_dir / "sub", program_name("prog"))
        self.chdir(gate_dir)
        for spelling in ("sub/" + wanted.name, "sub\\" + wanted.name, "./sub/" + wanted.name):
            with self.subTest(spelling=spelling):
                resolved = preflight.resolve_argv0(spelling, str(dispatch_dir))
                if WINDOWS or "\\" not in spelling:
                    self.assertEqual(os.path.normcase(resolved), os.path.normcase(str(wanted)))
                self.assertTrue(os.path.isabs(resolved))
                self.assertTrue(resolved.startswith(str(dispatch_dir)), resolved)

    def test_a_relative_name_runs_the_dispatch_directory_copy_when_the_gate_runs_elsewhere(self) -> None:
        try:
            relative = os.path.relpath(PY, self.dir)
        except ValueError:
            self.skipTest("the interpreter is on another drive than the temporary directory")
        elsewhere = self.dir / "w" / "x" / "y" / "z" / "v"
        elsewhere.mkdir(parents=True)
        if os.path.exists(os.path.join(elsewhere, relative)):
            self.skipTest("the relative path also reaches the interpreter from the other directory")
        self.chdir(elsewhere)
        self.assertTrue("\\" in relative or "/" in relative)
        lines = item_lines("t", [relative, "-c", "pass"], [relative, "-c", "print('ran-the-relative-one')"], "ran-the-relative-one")
        self.assertEqual(self.gate(dispatch_text(*lines))[:2], (0, "tools=1 served=1\n"))

    def test_a_bare_name_is_never_looked_up_in_the_current_or_the_dispatch_directory(self) -> None:
        empty = self.dir / "empty"
        empty.mkdir()
        decoy = program_name("decoy-tool")
        self.fake(self.dir, decoy)
        self.fake(self.dir / "cwd", decoy)
        self.chdir(self.dir / "cwd")
        for entries in ((str(empty),), (str(empty), "", ".", "..", "cwd", str(Path("cwd"))), ("",)):
            with self.subTest(entries=entries), self.search_path(*entries):
                with self.assertRaises(preflight.ArgvZeroError) as caught:
                    preflight.resolve_argv0("decoy-tool", str(self.dir))
                self.assertIn("not found in PATH", str(caught.exception))
                with self.assertRaises(preflight.ArgvZeroError):
                    preflight.resolve_argv0(decoy, str(self.dir))

    def test_a_bare_name_is_found_in_the_first_path_directory_that_holds_it(self) -> None:
        first = self.fake(self.dir / "one", program_name("found-tool"))
        self.fake(self.dir / "two", program_name("found-tool"))
        with self.search_path(str(self.dir / "absent"), str(self.dir / "one"), str(self.dir / "two")):
            resolved = preflight.resolve_argv0("found-tool", str(self.dir))
        self.assertEqual(os.path.normcase(resolved), os.path.normcase(str(first)))

    def test_a_bare_name_that_is_not_found_is_unserved_with_its_own_cause(self) -> None:
        self.fake(self.dir, program_name("decoy-tool"))
        lines = item_lines("t", ["decoy-tool"], say("x"), "x")
        with self.search_path(str(self.dir / "empty")):
            code, out, _ = self.gate(dispatch_text(*lines))
        self.assertEqual(code, 2)
        (line,) = out.splitlines()
        self.assertTrue(line.startswith("TOOL_UNSERVED t: start cannot be resolved"), line)
        self.assertNotIn("cannot be launched", line)
        lines = item_lines("t", say("s"), ["decoy-tool"], "x")
        with self.search_path(str(self.dir / "empty")):
            code, out, _ = self.gate(dispatch_text(*lines))
        self.assertEqual(code, 2)
        self.assertTrue(out.startswith("TOOL_UNSERVED t: probe cannot be resolved"), out)

    def test_a_bare_name_found_in_path_serves_the_tool(self) -> None:
        with self.search_path(os.path.dirname(PY)):
            name = os.path.basename(PY)
            lines = item_lines("t", [name, "-c", "pass"], [name, "-c", "print('via-path')"], "via-path")
            self.assertEqual(self.gate(dispatch_text(*lines))[:2], (0, "tools=1 served=1\n"))

    @unittest.skipUnless(WINDOWS, "rooted names without a drive exist on Windows only")
    def test_a_rooted_name_without_a_drive_is_joined_to_the_dispatch_directory(self) -> None:
        drive = os.path.splitdrive(str(self.dir))[0]
        resolved = preflight.resolve_argv0("\\sub\\prog.exe", str(self.dir))
        self.assertEqual(os.path.splitdrive(resolved)[0].lower(), drive.lower())
        self.assertEqual(os.path.normcase(resolved), os.path.normcase(drive + "\\sub\\prog.exe"))

    @unittest.skipUnless(WINDOWS, "drive-relative names exist on Windows only")
    def test_a_drive_relative_name_is_not_resolved(self) -> None:
        with self.assertRaises(preflight.ArgvZeroError) as caught:
            preflight.resolve_argv0("C:prog.exe", str(self.dir))
        self.assertIn("relative to a drive", str(caught.exception))

    def test_batch_files_are_refused_in_every_case_and_spelling(self) -> None:
        for name in ("tool.cmd", "tool.CMD", "TOOL.Bat", "tool.bat", "tool.cmd ", "tool.cmd.", "tool.Cmd. ."):
            with self.subTest(name=name):
                with self.assertRaises(preflight.ArgvZeroError) as caught:
                    preflight.resolve_argv0(str(self.dir / name), str(self.dir))
                self.assertIn("batch file", str(caught.exception))
        for name in ("tool.cmd.exe", "tool.bat.py", "cmd", "tool.cmdx"):
            with self.subTest(name=name):
                preflight.resolve_argv0(str(self.dir / name), str(self.dir))

    def test_a_batch_file_is_unserved_and_never_run(self) -> None:
        marker = self.dir / "ran.txt"
        for name in ("tool.cmd", "TOOL.BAT"):
            batch = self.dir / name
            batch.write_bytes(b"@echo ran> ran.txt\r\n")
            batch.chmod(0o755)
            for position in ("start", "probe"):
                with self.subTest(name=name, position=position):
                    argv = [str(batch), "a&md,injected"]
                    lines = item_lines("t", argv, say("x"), "x") if position == "start" else item_lines("t", say("s"), argv, "x")
                    code, out, _ = self.gate(dispatch_text(*lines))
                    self.assertEqual(code, 2)
                    (line,) = out.splitlines()
                    self.assertTrue(line.startswith(f"TOOL_UNSERVED t: {position} is refused"), line)
                    self.assertIn("batch file", line)
                    self.assertFalse(marker.exists())
                    self.assertFalse((self.dir / "injected").exists())

    def test_a_batch_file_found_in_path_is_refused(self) -> None:
        batch = self.fake(self.dir / "bin", "tool.cmd")
        with self.search_path(str(batch.parent)):
            with self.assertRaises(preflight.ArgvZeroError) as caught:
                preflight.resolve_argv0("tool.cmd", str(self.dir))
            self.assertIn("batch file", str(caught.exception))
            if WINDOWS:
                with self.assertRaises(preflight.ArgvZeroError) as caught:
                    preflight.resolve_argv0("tool", str(self.dir))
                self.assertIn("batch file", str(caught.exception))

    def test_the_three_causes_are_distinct(self) -> None:
        batch = str(self.dir / "tool.cmd")
        absent = str(self.dir / "absent-program")
        causes = []
        for name in (batch, "no-such-bare-name-anywhere", absent):
            with self.search_path(str(self.dir / "empty")):
                (line,) = self.gate(dispatch_text(*item_lines("t", [name], say("x"), "x")))[1].splitlines()
            causes.append(line.split(": ", 1)[1])
        self.assertEqual(len({cause.split(" (", 1)[0] for cause in causes}), 3, causes)


class AnyFailureTests(Fixture):
    """The exit is 2 when any tool failed, whichever tool came last."""

    def test_an_unserved_tool_followed_by_a_served_one_is_exit_two(self) -> None:
        block = [*item_lines("bad", [str(self.dir / "absent-program")], say("x"), "x"), *good_item("fine")]
        code, out, err = self.gate(dispatch_text(*block))
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(out.splitlines(), [out.splitlines()[0]])
        self.assertTrue(out.startswith("TOOL_UNSERVED bad: start cannot be launched"))

    def test_the_position_of_the_failure_does_not_matter(self) -> None:
        bad = item_lines("bad", say("s"), say("x"), "needle")
        for label, block in {
            "first": [*bad, *good_item("a"), *good_item("b")],
            "middle": [*good_item("a"), *bad, *good_item("b")],
            "last": [*good_item("a"), *good_item("b"), *bad],
        }.items():
            with self.subTest(position=label):
                code, out, _ = self.gate(dispatch_text(*block))
                self.assertEqual(code, 2)
                self.assertEqual(len(out.splitlines()), 1)

    def test_an_unexpected_error_in_the_first_tool_still_tries_the_second(self) -> None:
        real = preflight.check_item
        calls: list[str] = []

        def flaky(item: preflight.PreflightItem, cwd: str, timeout: float) -> str | None:
            calls.append(item.tool)
            if item.tool == "first":
                raise RuntimeError("boom\nTOOL_UNSERVED forged: x")
            return real(item, cwd, timeout)

        block = [*good_item("first"), *item_lines("second", say("s"), say("x"), "needle"), *good_item("third")]
        with mock.patch.object(preflight, "check_item", side_effect=flaky):
            code, out, err = self.gate(dispatch_text(*block))
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(calls, ["first", "second", "third"])
        first, second = out.splitlines()
        self.assertEqual(first, "TOOL_UNSERVED first: unexpected error (RuntimeError: boom\\x0aTOOL_UNSERVED forged: x)")
        self.assertIn("does not contain", second)

    def test_an_unexpected_error_in_the_first_tool_and_a_served_second_is_exit_two(self) -> None:
        real = preflight.check_item

        def flaky(item: preflight.PreflightItem, cwd: str, timeout: float) -> str | None:
            if item.tool == "first":
                raise OSError("disk")
            return real(item, cwd, timeout)

        with mock.patch.object(preflight, "check_item", side_effect=flaky):
            code, out, _ = self.gate(dispatch_text(*good_item("first"), *good_item("second")))
        self.assertEqual(code, 2)
        self.assertEqual(out.count("TOOL_UNSERVED"), 1)


class OutputFailureTests(Fixture):
    """A standard output or error that cannot be written ends the run with exit 2, never another code."""

    def closed_stream(self) -> io.StringIO:
        stream = io.StringIO()
        stream.close()
        return stream

    def run_with_streams(self, out: io.StringIO | None, err: io.StringIO | None, *args: str) -> int:
        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", err):
            return preflight.main(list(args))

    def test_a_closed_stdout_is_exit_two_for_every_outcome(self) -> None:
        served = self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_with_streams(self.closed_stream(), io.StringIO(), str(served)), 2)
        unserved = self.write(dispatch_text(*item_lines("t", say("s"), say("x"), "y")))
        self.assertEqual(self.run_with_streams(self.closed_stream(), io.StringIO(), str(unserved)), 2)

    def test_a_closed_stderr_turns_a_usage_error_into_exit_two(self) -> None:
        self.assertEqual(self.run_with_streams(io.StringIO(), self.closed_stream()), 2)
        self.write("no block\n")
        self.assertEqual(self.run_with_streams(io.StringIO(), self.closed_stream(), str(self.path)), 2)
        self.assertEqual(self.run_with_streams(io.StringIO(), self.closed_stream(), str(self.dir / "absent.yaml")), 2)

    def test_missing_standard_streams_are_exit_two(self) -> None:
        served = self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_with_streams(None, io.StringIO(), str(served)), 2)
        self.assertEqual(self.run_with_streams(io.StringIO(), None), 2)

    def test_a_stream_that_raises_on_write_is_exit_two(self) -> None:
        class Broken(io.StringIO):
            def write(self, text: str) -> int:
                raise OSError(32, "Broken pipe")

        served = self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_with_streams(Broken(), io.StringIO(), str(served)), 2)

    def test_working_streams_keep_the_exit_codes(self) -> None:
        served = self.write(dispatch_text(*good_item()))
        self.assertEqual(self.run_with_streams(io.StringIO(), io.StringIO(), str(served)), 0)
        self.assertEqual(self.run_with_streams(io.StringIO(), io.StringIO()), 3)

    def run_script_with_dead_reader(self, stream: str, *args: str) -> subprocess.CompletedProcess[bytes]:
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            command = [PY, str(SCRIPT), *args]
            if stream == "stdout":
                return subprocess.run(command, stdin=subprocess.DEVNULL, stdout=write_fd, stderr=subprocess.PIPE, timeout=120)
            return subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=write_fd, timeout=120)
        finally:
            os.close(write_fd)

    def test_a_dead_stdout_pipe_is_exit_two_not_one_hundred_and_twenty(self) -> None:
        served = self.write(dispatch_text(*good_item()))
        done = self.run_script_with_dead_reader("stdout", str(served))
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertNotIn(b"Traceback", done.stderr)

    def test_a_dead_stderr_pipe_is_exit_two_not_three(self) -> None:
        done = self.run_script_with_dead_reader("stderr")
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertNotIn(b"Traceback", done.stdout)


class KillToolTests(Fixture):
    """The process-tree kill on Windows runs the system's taskkill by absolute path, never a lookalike."""

    def chdir(self, path: Path) -> None:
        old = os.getcwd()
        os.chdir(path)
        self.addCleanup(os.chdir, old)

    @unittest.skipUnless(WINDOWS, "taskkill is the Windows tree kill")
    def test_the_system_taskkill_is_an_absolute_existing_path(self) -> None:
        path = preflight._system_taskkill()
        assert path is not None
        self.assertTrue(os.path.isabs(path))
        self.assertTrue(os.path.isfile(path))
        self.assertEqual(os.path.basename(path).lower(), "taskkill.exe")

    def test_a_planted_taskkill_is_not_run_and_the_child_is_still_killed(self) -> None:
        plant = self.dir / "plant"
        plant.mkdir()
        for folder in (plant, self.dir):
            for name in ("taskkill.cmd", "taskkill.bat", "taskkill"):
                (folder / name).write_bytes(b"@echo planted> planted.txt\r\n")
                (folder / name).chmod(0o755)
        self.chdir(plant)
        beat = self.dir / "beat"
        script = self.dir / "heartbeat.py"
        script.write_text(HEARTBEAT_SCRIPT, encoding="utf-8")
        code, out, _ = self.gate(dispatch_text(*item_lines("t", say("s"), [PY, str(script), str(beat)], "x")), "--timeout", "2")
        self.assertEqual(code, 2, out)
        self.assertIn("timed out", out)
        self.assertFalse((plant / "planted.txt").exists())
        self.assertFalse((self.dir / "planted.txt").exists())
        time.sleep(0.8)
        first = beat.stat().st_size
        time.sleep(0.8)
        self.assertEqual(first, beat.stat().st_size, "the child still runs")
        self.assertGreater(first, 0)


class ShellTests(Fixture):
    def test_metacharacters_without_spaces_are_passed_literally(self) -> None:
        code_text = "__import__('sys').stdout.write(__import__('sys').argv[1])"
        self.assertNotIn(" ", code_text)
        for text in ("a&b", "x|y", "a>b", "a<b", "a^b", "%PATH%", "a&&b", "a||b", "(x)", "a;b", "$(x)", "`x`", "!x!", "a,b"):
            with self.subTest(text=text):
                lines = item_lines("t", [PY, "-c", "pass"], [PY, "-c", code_text, text], text)
                self.assertEqual(self.gate(dispatch_text(*lines))[:2], (0, "tools=1 served=1\n"))
                self.assertEqual(os.listdir(self.dir), ["dispatch.yaml"])

    def test_the_gate_launches_with_shell_false_only(self) -> None:
        with mock.patch.object(preflight.subprocess, "Popen", wraps=subprocess.Popen) as launched:
            self.assertEqual(self.gate(dispatch_text(*good_item()))[0], 0)
        self.assertEqual([call.kwargs.get("shell") for call in launched.call_args_list], [False, False])


class DriveRuleTests(Fixture):
    """Revision03 (S55-13): a name that carries a drive must be absolute, and this is checked before every other rule."""

    RELATIVE_TO_A_DRIVE = (
        "Z:prog.exe",
        "Z:sub\\prog.exe",
        "Z:sub/prog.exe",
        "C:sub\\prog.exe",
        "c:prog",
        "C:",
        "Z:sub\\tool.cmd",
        "C:tool.BAT",
        "\\\\?\\C:prog.exe",
        "\\\\server",
    )

    def fake(self, directory: Path, name: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_bytes(b"")
        path.chmod(0o755)
        return path

    def test_every_name_relative_to_a_drive_is_refused_with_the_drive_cause(self) -> None:
        for name in self.RELATIVE_TO_A_DRIVE:
            with self.subTest(name=name):
                with self.assertRaises(preflight.ArgvZeroError) as caught:
                    preflight.resolve_argv0(name, str(self.dir))
                self.assertIn("relative to a drive", str(caught.exception))
                self.assertNotIn("batch file", str(caught.exception))
                self.assertNotIn("not found in PATH", str(caught.exception))

    def test_a_name_relative_to_a_drive_is_unserved_and_nothing_is_launched(self) -> None:
        for name in self.RELATIVE_TO_A_DRIVE:
            for position in ("start", "probe"):
                with self.subTest(name=name, position=position):
                    argv = [name, "-c", "pass"]
                    lines = item_lines("t", argv, say("x"), "x") if position == "start" else item_lines("t", say("s"), argv, "x")
                    with mock.patch.object(preflight.subprocess, "Popen", wraps=subprocess.Popen) as launched:
                        code, out, err = self.gate(dispatch_text(*lines))
                    self.assertEqual((code, err), (2, ""))
                    (line,) = out.splitlines()
                    self.assertTrue(line.startswith(f"TOOL_UNSERVED t: {position} cannot be resolved"), line)
                    self.assertIn("relative to a drive", line)
                    self.assertEqual(len(launched.call_args_list), 0 if position == "start" else 1)

    @unittest.skipUnless(WINDOWS, "a drive-relative name next to the dispatch directory needs a drive")
    def test_a_drive_relative_name_on_the_dispatch_drive_is_not_joined_to_the_dispatch_directory(self) -> None:
        drive = os.path.splitdrive(str(self.dir))[0]
        decoy = self.fake(self.dir / "sub", "prog.exe")
        self.fake(self.dir, "prog.exe")
        self.assertTrue(decoy.is_file())
        for spelling in (drive + "sub\\prog.exe", drive + "sub/prog.exe", drive + "prog.exe"):
            with self.subTest(spelling=spelling):
                with self.assertRaises(preflight.ArgvZeroError) as caught:
                    preflight.resolve_argv0(spelling, str(self.dir))
                self.assertIn("relative to a drive", str(caught.exception))

    @unittest.skipUnless(WINDOWS, "absolute names with a drive exist on Windows only")
    def test_absolute_names_with_a_drive_are_still_used_as_given(self) -> None:
        for name in ("C:\\x\\y.exe", "C:/x/y.exe", "c:\\x\\y.exe", "\\\\?\\C:\\x\\y.exe", "\\\\server\\share\\y.exe"):
            with self.subTest(name=name):
                self.assertEqual(preflight.resolve_argv0(name, str(self.dir)), name)

    @unittest.skipUnless(WINDOWS, "absolute names with a drive exist on Windows only")
    def test_an_absolute_batch_file_with_a_drive_is_still_a_batch_refusal(self) -> None:
        with self.assertRaises(preflight.ArgvZeroError) as caught:
            preflight.resolve_argv0("C:\\x\\tool.cmd", str(self.dir))
        self.assertIn("batch file", str(caught.exception))

    def test_names_without_a_drive_are_not_caught_by_the_drive_rule(self) -> None:
        for name in ("sub\\x.exe", "sub/x.exe", "./x.exe", "..\\x.exe"):
            with self.subTest(name=name):
                resolved = preflight.resolve_argv0(name, str(self.dir))
                self.assertTrue(os.path.isabs(resolved))


class Argv0EnvironmentTests(Fixture):
    """Revision03 (S55-15, S55-16): PATHEXT from the environment, and quotes and blanks around a PATH entry."""

    def fake(self, directory: Path, name: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_bytes(b"")
        path.chmod(0o755)
        return path

    def resolve(self, name: str, path_value: str, pathext: str | None) -> str:
        with mock.patch.dict(os.environ, {"PATH": path_value}):
            if pathext is None:
                os.environ.pop("PATHEXT", None)
            else:
                os.environ["PATHEXT"] = pathext
            return preflight.resolve_argv0(name, str(self.dir))

    def not_found(self, name: str, path_value: str, pathext: str | None) -> str:
        with self.assertRaises(preflight.ArgvZeroError) as caught:
            self.resolve(name, path_value, pathext)
        return str(caught.exception)

    def same(self, left: str, right: Path) -> None:
        self.assertEqual(os.path.normcase(left), os.path.normcase(str(right)))

    @unittest.skipUnless(WINDOWS, "PATHEXT decides bare names on Windows only")
    def test_a_non_default_pathext_decides_which_bare_names_resolve(self) -> None:
        bindir = self.dir / "bin"
        only_foo = self.fake(bindir, "alpha.foo")
        self.fake(bindir, "beta.exe")
        self.same(self.resolve("alpha", str(bindir), ".FOO"), only_foo)
        self.assertIn("not found in PATH", self.not_found("alpha", str(bindir), PATHEXT_DEFAULT))
        self.assertIn("not found in PATH", self.not_found("beta", str(bindir), ".FOO"))

    @unittest.skipUnless(WINDOWS, "PATHEXT decides bare names on Windows only")
    def test_the_order_of_pathext_decides_between_two_matches(self) -> None:
        bindir = self.dir / "bin"
        foo = self.fake(bindir, "tool.foo")
        exe = self.fake(bindir, "tool.exe")
        self.same(self.resolve("tool", str(bindir), ".FOO;.EXE"), foo)
        self.same(self.resolve("tool", str(bindir), ".EXE;.FOO"), exe)

    @unittest.skipUnless(WINDOWS, "PATHEXT decides bare names on Windows only")
    def test_pathext_is_read_without_regard_to_letter_case_and_empty_items(self) -> None:
        bindir = self.dir / "bin"
        foo = self.fake(bindir, "tool.foo")
        for pathext in (".foo", ".Foo", ";.FOO", ".FOO;", ";;.FOO;;"):
            with self.subTest(pathext=pathext):
                self.same(self.resolve("tool", str(bindir), pathext), foo)

    @unittest.skipUnless(WINDOWS, "PATHEXT decides bare names on Windows only")
    def test_a_missing_or_empty_pathext_means_the_default_list(self) -> None:
        bindir = self.dir / "bin"
        exe = self.fake(bindir, "tool.exe")
        for pathext in (None, "", ";", ";;"):
            with self.subTest(pathext=pathext):
                self.same(self.resolve("tool", str(bindir), pathext), exe)

    @unittest.skipUnless(WINDOWS, "PATHEXT decides bare names on Windows only")
    def test_a_bare_name_that_already_ends_in_a_listed_extension_gets_no_second_one(self) -> None:
        bindir = self.dir / "bin"
        foo = self.fake(bindir, "tool.foo")
        self.same(self.resolve("tool.foo", str(bindir), ".FOO"), foo)
        self.same(self.resolve("TOOL.FOO", str(bindir), ".foo"), foo)

    @unittest.skipIf(WINDOWS, "PATHEXT is ignored off Windows")
    def test_pathext_is_ignored_off_windows(self) -> None:
        bindir = self.dir / "bin"
        plain = self.fake(bindir, "tool")
        self.fake(bindir, "other.foo")
        self.assertEqual(self.resolve("tool", str(bindir), ".FOO"), str(plain))
        self.assertIn("not found in PATH", self.not_found("other", str(bindir), ".FOO"))

    @unittest.skipUnless(WINDOWS, "quotes and blanks around a PATH entry are removed on Windows only")
    def test_quotes_and_blanks_around_a_path_entry_are_removed(self) -> None:
        bindir = self.dir / "bin"
        exe = self.fake(bindir, "tool.exe")
        for entry in (f'"{bindir}"', f"  {bindir}  ", f' "{bindir}" ', f"\t{bindir}\t", f'\t"{bindir}"\t', f'"{bindir}'):
            with self.subTest(entry=entry):
                self.same(self.resolve("tool", entry, None), exe)

    @unittest.skipUnless(WINDOWS, "quotes and blanks around a PATH entry are removed on Windows only")
    def test_an_entry_that_is_only_quotes_or_blanks_is_skipped(self) -> None:
        bindir = self.dir / "bin"
        exe = self.fake(bindir, "tool.exe")
        for junk in ('""', '"   "', "   ", "\t", '" "'):
            with self.subTest(junk=junk):
                self.assertIn("not found in PATH", self.not_found("tool", junk, None))
                self.same(self.resolve("tool", junk + os.pathsep + str(bindir), None), exe)

    @unittest.skipIf(WINDOWS, "entries are used as they are off Windows")
    def test_a_path_entry_is_used_as_it_is_off_windows(self) -> None:
        bindir = self.dir / "bin"
        plain = self.fake(bindir, "tool")
        self.assertEqual(self.resolve("tool", str(bindir), None), str(plain))
        for entry in (f'"{bindir}"', f"  {bindir}  "):
            with self.subTest(entry=entry):
                self.assertIn("not found in PATH", self.not_found("tool", entry, None))


class RunLevelErrorTests(Fixture):
    """Revision03 (S55-14): an unexpected error outside the tool loop is exit 2 with one stderr line and no traceback."""

    def assert_one_fault_line(self, code: int, out: str, err: str, kind: str, shown: str) -> None:
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(err, f"preflight.py: tool fault: {kind}: {shown}\n")
        self.assertEqual(len(err.splitlines()), 1)
        self.assertNotIn("Traceback", err)

    def test_an_unexpected_error_while_parsing_is_exit_two_one_line(self) -> None:
        self.write(dispatch_text(*good_item()))
        with mock.patch.object(preflight, "parse_preflight", side_effect=RuntimeError("boom")):
            code, out, err = self.run_main(str(self.path))
        self.assert_one_fault_line(code, out, err, "RuntimeError", "boom")

    def test_an_unexpected_error_before_the_file_is_read_is_exit_two_one_line(self) -> None:
        self.write(dispatch_text(*good_item()))
        with mock.patch.object(preflight, "_parse_arguments", side_effect=OSError("disk")):
            code, out, err = self.run_main(str(self.path))
        self.assert_one_fault_line(code, out, err, "OSError", "disk")

    def test_the_text_of_the_error_is_one_escaped_line(self) -> None:
        self.write(dispatch_text(*good_item()))
        text = f"a\nTOOL_UNSERVED forged: x{LINE_SEPARATOR}b{NEXT_LINE}c\\d"
        with mock.patch.object(preflight, "parse_preflight", side_effect=ValueError(text)):
            code, out, err = self.run_main(str(self.path))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)
        self.assertEqual(len(err.split("\n")), 2)
        for shown in ("\\x0a", "\\u2028", "\\x85", "\\\\d"):
            self.assertIn(shown, err)

    def test_the_run_level_error_is_exit_two_without_a_traceback_on_the_command_line(self) -> None:
        self.write(dispatch_text(*good_item()))
        driver = (
            "import sys; sys.path.insert(0, sys.argv[1]); del sys.argv[1]; import preflight\n"
            "def boom(text): raise RuntimeError('boom')\n"
            "preflight.parse_preflight = boom\n"
            "sys.exit(preflight.entry())\n"
        )
        done = subprocess.run(
            [PY, "-c", driver, str(_SCRIPTS), str(self.path)], capture_output=True, timeout=120, stdin=subprocess.DEVNULL
        )
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertNotIn(b"Traceback", done.stderr)


class ChildCleanupTests(Fixture):
    """Revision03 (S55-17): a child whose serving raised is killed before the next tool runs."""

    def script(self) -> Path:
        script = self.dir / "heartbeat.py"
        script.write_text(HEARTBEAT_SCRIPT, encoding="utf-8")
        return script

    def track(self, error: BaseException) -> tuple[list[subprocess.Popen[bytes]], list[int | None], contextlib.AbstractContextManager[object]]:
        """Patch the launcher: the first child of the interpreter fails its first wait with `error`; the state of the
        first child is recorded each time a later child of the interpreter is launched."""
        real = subprocess.Popen
        launched: list[subprocess.Popen[bytes]] = []
        state_at_next_launch: list[int | None] = []
        raised: list[bool] = []

        def launch(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
            argv = args[0] if args else kwargs.get("args")
            ours = isinstance(argv, list) and bool(argv) and argv[0] == PY
            if ours and launched:
                state_at_next_launch.append(launched[0].poll())
            process = real(*args, **kwargs)
            if ours:
                launched.append(process)
                if len(launched) == 1:
                    original = process.wait

                    def wait(timeout: float | None = None) -> int:
                        if not raised:
                            raised.append(True)
                            raise error
                        return original(timeout=timeout)

                    setattr(process, "wait", wait)
            return process

        self.addCleanup(self.reap, launched)
        return launched, state_at_next_launch, mock.patch.object(preflight.subprocess, "Popen", side_effect=launch)

    def reap(self, launched: list[subprocess.Popen[bytes]]) -> None:
        for process in launched:
            if process.poll() is None:
                preflight._kill_tree(process)

    def assert_silent(self, beat: Path) -> None:
        def size() -> int:
            return beat.stat().st_size if beat.exists() else 0

        time.sleep(0.8)
        first = size()
        time.sleep(0.8)
        self.assertEqual(first, size(), "the child is still running")

    def test_a_child_whose_serving_raised_is_dead_before_the_next_tool_starts(self) -> None:
        beat = self.dir / "beat"
        block = [*item_lines("first", [PY, str(self.script()), str(beat)], say("x"), "x"), *good_item("second")]
        launched, at_next_launch, patched = self.track(RuntimeError("boom"))
        with patched:
            code, out, err = self.gate(dispatch_text(*block))
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(out, "TOOL_UNSERVED first: unexpected error (RuntimeError: boom)\n")
        self.assertEqual(len(launched), 3)
        self.assertEqual(len(at_next_launch), 2)
        self.assertIsNotNone(at_next_launch[0], "the first child was still running when the next tool launched")
        self.assertIsNotNone(launched[0].poll())
        self.assert_silent(beat)

    def test_an_interrupt_after_the_child_started_also_kills_it(self) -> None:
        beat = self.dir / "beat"
        launched, _, patched = self.track(KeyboardInterrupt())
        with patched:
            with self.assertRaises(KeyboardInterrupt):
                preflight.run_command([PY, str(self.script()), str(beat)], str(self.dir), 30.0)
        self.assertEqual(len(launched), 1)
        self.assertIsNotNone(launched[0].poll())
        self.assert_silent(beat)


class DeviceNameTests(Fixture):
    """Revision03 (S55-18): a device name as the dispatch path is exit 3, and nothing is opened."""

    DEVICES = (
        "CON", "CONIN$", "AUX", "COM1", "con", "Aux", "NUL", "PRN", "LPT1", "COM9", "COM0", "CONOUT$", "CLOCK$",
        "COM" + chr(0xB9), "LPT" + chr(0xB2), "con.txt", "CON.yaml", "CON ", "CON.", "nul.tar.gz", "con:stream",
        "dir\\CON", "dir/aux", "C:\\dir\\NUL", "C:CON", "sub/COM3/x.yaml", "..\\AUX", "x/aux /y.yaml",
        "\\\\.\\CON", "\\\\.\\pipe\\name", "//./COM1", "\\\\?\\CON",
    )
    NOT_DEVICES = (
        "CONSOLE.yaml", "COM10", "COM", "CONIN", "AUXILIARY", "NULL", "PRNT", "LPT10", "dispatch.yaml", "x.con",
        "con_1", "ccon", "COMA", "dir.con/x.yaml",
    )

    def refuse(self, *args: str) -> tuple[int, str, str]:
        with mock.patch("builtins.open", side_effect=AssertionError("a device was opened")):
            return self.run_main(*args)

    def test_each_device_name_is_exit_three_and_is_not_opened(self) -> None:
        for name in self.DEVICES:
            with self.subTest(name=name):
                code, out, err = self.refuse(name)
                self.assertEqual((code, out), (3, ""), err)
                self.assertIn("names a device", err)
                self.assertEqual(len(err.splitlines()), 2)
                self.assertTrue(err.startswith("usage:"))

    def test_the_named_cases_of_the_ticket(self) -> None:
        for name in ("CON", "CONIN$", "AUX", "COM1"):
            with self.subTest(name=name):
                self.assertEqual(self.refuse(name)[0], 3)

    def test_a_device_name_with_an_option_in_either_order_is_exit_three(self) -> None:
        for args in (("CON", "--timeout", "5"), ("--timeout", "5", "CON")):
            with self.subTest(args=args):
                self.assertEqual(self.refuse(*args)[0], 3)

    def test_names_that_only_look_like_a_device_are_read_as_files(self) -> None:
        for name in self.NOT_DEVICES:
            with self.subTest(name=name):
                code, out, err = self.run_main(str(self.dir / name))
                self.assertEqual((code, out), (2, ""))
                self.assertIn("cannot read", err)

    def test_the_check_is_text_only_and_sorts_the_two_lists(self) -> None:
        probes = [mock.patch.object(os.path, attr, side_effect=AssertionError("the filesystem was probed")) for attr in ("exists", "isfile", "isdir", "lexists")]
        with probes[0], probes[1], probes[2], probes[3]:
            for name in self.DEVICES:
                with self.subTest(name=name):
                    self.assertTrue(preflight.names_a_device(name))
            for name in self.NOT_DEVICES:
                with self.subTest(name=name):
                    self.assertFalse(preflight.names_a_device(name))

    def test_the_character_rule_still_comes_first_and_the_exit_is_never_one(self) -> None:
        for name in ("CON/a\n", "AUX/b\x00", "COM1/c\udc80", "x/CON\t"):
            with self.subTest(name=repr(name)):
                code, _, err = self.refuse(name)
                self.assertEqual(code, 3)
                self.assertIn("argument 1 holds", err)


if __name__ == "__main__":
    unittest.main()
