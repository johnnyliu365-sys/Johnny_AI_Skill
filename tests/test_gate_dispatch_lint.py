"""Behavioural tests for the dispatch_lint gate script (rules R1-R5, exit codes 0/1/3).

Every fixture is generated in a temporary directory; every expected value is derived
from the text the fixture wrote.
"""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import dispatch_lint  # noqa: E402

SCRIPT = _SCRIPTS / "dispatch_lint.py"
LINE_LIMIT = 400
CHAT_WORDS = ("請", "麻煩", "謝謝")
TERMINATOR = "。"
NON_CP950 = chr(0x0E01)  # outside code page 950


def rule_ids(problems: list[str]) -> list[str]:
    return [problem.split(" ", 1)[0] for problem in problems]


def dispatch(*body: str) -> str:
    """A valid two-field dispatch followed by the given extra lines."""
    return "\n".join(["ticket: T-1", "summary: do the work", *body]) + "\n"


class RuleTests(unittest.TestCase):
    def test_machine_form_text_passes(self) -> None:
        text = dispatch("items:", "  - first", "  - second", "| a | b |", "```", "free prose inside a fence", "```")
        self.assertEqual(dispatch_lint.lint(text), [])

    def test_r1_first_line_must_be_a_field(self) -> None:
        for first in ("field name: value", "- item"):
            with self.subTest(first):
                self.assertEqual(rule_ids(dispatch_lint.lint(first + "\nticket: T\n")), ["R1"])

    def test_r1_blank_leading_lines_are_skipped(self) -> None:
        self.assertEqual(dispatch_lint.lint("\n\nticket: T\n"), [])

    def test_r2_prose_line_is_reported_with_its_line_number(self) -> None:
        text = dispatch("this is prose")
        problems = dispatch_lint.lint(text)
        self.assertEqual(rule_ids(problems), ["R2"])
        number = text.splitlines().index("this is prose") + 1
        self.assertIn(f"line {number} ", problems[0])

    def test_r2_exempts_lists_tables_continuations_and_fences(self) -> None:
        text = dispatch("- item", "| a |", "  continuation", "```text", "prose in a fence", "```")
        self.assertEqual(dispatch_lint.lint(text), [])

    def test_r3_each_chat_word_outside_quotes_is_reported(self) -> None:
        for word in CHAT_WORDS:
            with self.subTest(word):
                problems = dispatch_lint.lint(dispatch(f"note: {word}"))
                self.assertEqual(rule_ids(problems), ["R3"])
                self.assertIn(repr(word), problems[0])

    def test_r3_is_not_triggered_inside_quotes_backticks_or_fences(self) -> None:
        word = CHAT_WORDS[0]
        for body in (f'note: "{word}"', f"note: '{word}'", f"note: `{word}`"):
            with self.subTest(body):
                self.assertEqual(dispatch_lint.lint(dispatch(body)), [])
        self.assertEqual(dispatch_lint.lint(dispatch("```", word, "```")), [])

    def test_r3_word_list_is_replaceable(self) -> None:
        text = dispatch("note: please")
        self.assertEqual(dispatch_lint.lint(text), [])
        self.assertEqual(rule_ids(dispatch_lint.lint(text, ["please"])), ["R3"])
        self.assertEqual(dispatch_lint.lint(dispatch(f"note: {CHAT_WORDS[0]}"), []), [])

    def test_every_default_chat_word_is_reported(self) -> None:
        self.assertGreaterEqual(len(dispatch_lint.DEFAULT_CHAT_WORDS), 1)
        for word in dispatch_lint.DEFAULT_CHAT_WORDS:
            with self.subTest(word):
                problems = dispatch_lint.lint(dispatch(f"note: {word}"))
                self.assertEqual(rule_ids(problems), ["R3"])
                self.assertIn(repr(word), problems[0])

    def test_default_chat_word_list_is_the_full_rule_list(self) -> None:
        self.assertEqual(
            dispatch_lint.DEFAULT_CHAT_WORDS,
            ("請", "你", "我們", "注意", "謝謝", "先做", "再做", "麻煩", "辛苦"),
        )

    def test_r4_terminator_outside_quotes_is_reported(self) -> None:
        self.assertEqual(rule_ids(dispatch_lint.lint(dispatch(f"note: done{TERMINATOR}"))), ["R4"])
        self.assertEqual(dispatch_lint.lint(dispatch(f'note: "done{TERMINATOR}"')), [])

    def test_r5_line_length_boundary(self) -> None:
        prefix = "note: "
        at_limit = prefix + "x" * (LINE_LIMIT - len(prefix))
        over = at_limit + "x"
        self.assertEqual(len(at_limit), LINE_LIMIT)
        self.assertEqual(dispatch_lint.lint(dispatch(at_limit)), [])
        problems = dispatch_lint.lint(dispatch(over))
        self.assertEqual(rule_ids(problems), ["R5"])
        self.assertIn(f"({len(over)})", problems[0])

    def test_r5_applies_to_line_1_of_a_one_line_document(self) -> None:
        first_line = "ticket: " + "x" * LINE_LIMIT
        for text in (first_line + chr(10), first_line):
            with self.subTest(len(text)):
                problems = dispatch_lint.lint(text)
                self.assertEqual(rule_ids(problems), ["R5"])
                self.assertIn("line 1 ", problems[0])

    def test_independent_violations_are_all_reported(self) -> None:
        text = "not a field\nticket: T\nprose line\n" + f"note: {CHAT_WORDS[0]}{TERMINATOR}\n"
        self.assertEqual(sorted(set(rule_ids(dispatch_lint.lint(text)))), ["R1", "R2", "R3", "R4"])


class ExitCodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="dl-")
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dispatch_lint.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_exit_0_prints_lint_pass(self) -> None:
        path = self.write("ok.yaml", dispatch("items:", "  - a"))
        code, out, err = self.run_main([str(path)])
        self.assertEqual((code, out, err), (0, "LINT PASS\n", ""))

    def test_exit_1_prints_every_problem_then_the_count(self) -> None:
        text = dispatch("prose one", "prose two")
        path = self.write("bad.yaml", text)
        problems = dispatch_lint.lint(text)
        code, out, _ = self.run_main([str(path)])
        self.assertEqual(code, 1)
        self.assertEqual(out.splitlines(), [*problems, f"LINT FAIL ({len(problems)})"])

    def test_exit_3_with_one_line_of_usage_for_every_usage_error(self) -> None:
        good = self.write("ok.yaml", dispatch())
        cases = {
            "no arguments": [],
            "two files": [str(good), str(good)],
            "missing file": [str(self.root / "absent.yaml")],
            "unknown option": ["--help"],
            "option without value": [str(good), "--chat-words"],
            "not utf-8": [str(self.write_bytes("binary.yaml", b"\xff\xfe\x00\xff"))],
        }
        for label, argv in cases.items():
            with self.subTest(label):
                code, out, err = self.run_main(argv)
                self.assertEqual(code, 3)
                self.assertEqual(out, "")
                self.assertEqual(len([line for line in err.splitlines() if line.startswith("usage:")]), 1, err)

    def write_bytes(self, name: str, data: bytes) -> Path:
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_no_arguments_prints_only_the_usage_line(self) -> None:
        _, _, err = self.run_main([])
        self.assertEqual(len(err.strip().splitlines()), 1, err)

    def test_chat_words_option_changes_the_verdict(self) -> None:
        path = self.write("custom.yaml", dispatch("note: please"))
        self.assertEqual(self.run_main([str(path)])[0], 0)
        self.assertEqual(self.run_main([str(path), "--chat-words", "please,thanks"])[0], 1)

    def test_blank_chat_word_lists_exit_3_and_never_void_rule_r3(self) -> None:
        path = self.write("chat.yaml", dispatch(f"note: {dispatch_lint.DEFAULT_CHAT_WORDS[0]}"))
        self.assertEqual(self.run_main([str(path)])[0], 1)
        for value in ("", ",", " ", " , ,", ",,,"):
            with self.subTest(repr(value)):
                code, out, err = self.run_main([str(path), "--chat-words", value])
                self.assertEqual(code, 3)
                self.assertEqual(out, "")
                self.assertEqual(len([line for line in err.splitlines() if line.startswith("usage:")]), 1, err)

    def test_chat_words_list_with_one_real_word_is_used(self) -> None:
        path = self.write("chat.yaml", dispatch("note: please"))
        for value in ("please", ",please,", " ,please"):
            with self.subTest(repr(value)):
                self.assertEqual(self.run_main([str(path), "--chat-words", value])[0], 1)

    def test_blank_chat_word_list_exits_3_as_a_process(self) -> None:
        path = self.write("chat.yaml", dispatch(f"note: {dispatch_lint.DEFAULT_CHAT_WORDS[0]}"))
        done = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(path), "--chat-words", ","],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)

    def test_script_exit_codes_as_a_process(self) -> None:
        good = self.write("good.yaml", dispatch())
        bad = self.write("bad.yaml", dispatch("prose"))
        expected = {(str(good),): 0, (str(bad),): 1, (): 3}
        for args, code in expected.items():
            with self.subTest(args=args):
                done = subprocess.run(
                    [sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8",
                )
                self.assertEqual(done.returncode, code, done.stdout + done.stderr)

    def test_a_red_with_a_non_cp950_character_exits_1_under_a_cp950_console(self) -> None:
        """The console encoding never changes an exit code (R4-2): a red stays 1, with no traceback."""
        env = {key: value for key, value in os.environ.items() if key not in ("PYTHONUTF8", "PYTHONIOENCODING")}
        env["PYTHONIOENCODING"] = "cp950"
        with self.assertRaises(UnicodeEncodeError):
            NON_CP950.encode("cp950")
        bad = self.write("nonascii.yaml", dispatch(f"prose {NON_CP950} line"))
        done = subprocess.run(
            [sys.executable, str(SCRIPT), str(bad)], capture_output=True, env=env,
        )
        out, err = done.stdout.decode("cp950"), done.stderr.decode("cp950", errors="replace")
        self.assertEqual(done.returncode, 1, out + err)
        self.assertNotIn("Traceback", err)
        self.assertIn("R2", out)
        self.assertIn(NON_CP950.encode("unicode_escape").decode("ascii"), out)
        self.assertIn("LINT FAIL (1)", out)


if __name__ == "__main__":
    unittest.main()
