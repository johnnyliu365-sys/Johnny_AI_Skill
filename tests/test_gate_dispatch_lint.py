"""Behavioural tests for the dispatch_lint gate script (rules R1-R8, exit codes 0/1/3).

Every fixture is generated in a temporary directory; every expected value is derived
from the text the fixture wrote.
"""
from __future__ import annotations

import contextlib
import hashlib
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
LINE_LIMIT = 2000
FULL_WIDTH_SEMICOLON = chr(0xFF1B)
CHAT_WORDS = ("請", "麻煩", "謝謝")
TERMINATOR = "。"
NON_CP950 = chr(0x0E01)  # outside code page 950
STATE = "狀態"
TOKEN = "dispatch=sha256:"


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

    def test_r6_line_length_boundary(self) -> None:
        prefix = "note: "
        at_limit = prefix + "x" * (LINE_LIMIT - len(prefix))
        over = at_limit + "x"
        self.assertEqual(len(at_limit), LINE_LIMIT)
        self.assertEqual(dispatch_lint.lint(dispatch(at_limit)), [])
        problems = dispatch_lint.lint(dispatch(over))
        self.assertEqual(rule_ids(problems), ["R6"])
        self.assertIn(f"({len(over)})", problems[0])

    def test_r6_applies_to_line_1_of_a_one_line_document(self) -> None:
        first_line = "ticket: " + "x" * LINE_LIMIT
        for text in (first_line + chr(10), first_line):
            with self.subTest(len(text)):
                problems = dispatch_lint.lint(text)
                self.assertEqual(rule_ids(problems), ["R6"])
                self.assertIn("line 1 ", problems[0])

    def test_r6_applies_inside_a_code_fence_too(self) -> None:
        blob = "x" * (LINE_LIMIT + 1)
        self.assertEqual(rule_ids(dispatch_lint.lint(dispatch("```", blob, "```"))), ["R6"])
        self.assertEqual(dispatch_lint.lint(dispatch("```", blob[:-1], "```")), [])

    def test_a_line_between_the_old_and_the_new_limit_is_no_longer_a_problem(self) -> None:
        line = "note: " + "x" * 600
        self.assertEqual(dispatch_lint.lint(dispatch(line)), [])

    def test_r5_one_action_passes(self) -> None:
        self.assertEqual(dispatch_lint.lint(dispatch("note: one action only")), [])
        self.assertEqual(dispatch_lint.lint(dispatch("note: one action;")), [])
        self.assertEqual(dispatch_lint.lint(dispatch("note: one action; ")), [])

    def test_r5_two_actions_are_reported_with_the_count_and_line_number(self) -> None:
        text = dispatch("note: first; second")
        problems = dispatch_lint.lint(text)
        self.assertEqual(rule_ids(problems), ["R5"])
        number = text.splitlines().index("note: first; second") + 1
        self.assertEqual(problems[0], f"R5 line {number} holds 2 actions; put each on its own list item")

    def test_r5_three_actions_are_counted(self) -> None:
        problems = dispatch_lint.lint(dispatch("note: a; b; c"))
        self.assertEqual(rule_ids(problems), ["R5"])
        self.assertIn("holds 3 actions;", problems[0])

    def test_r5_full_width_separator_counts_with_or_without_a_space(self) -> None:
        for body in (f"note: first{FULL_WIDTH_SEMICOLON}second", f"note: first{FULL_WIDTH_SEMICOLON} second"):
            with self.subTest(body):
                self.assertEqual(rule_ids(dispatch_lint.lint(dispatch(body))), ["R5"])

    def test_r5_separator_inside_backticks_does_not_count(self) -> None:
        for body in (
            "note: run `a; b` once",
            f"note: run `a{FULL_WIDTH_SEMICOLON}b` once",
            "note: run `a` then `b; c`",
        ):
            with self.subTest(body):
                self.assertEqual(dispatch_lint.lint(dispatch(body)), [])

    def test_r5_an_unbalanced_backtick_does_not_hide_the_rest_of_the_line(self) -> None:
        self.assertEqual(rule_ids(dispatch_lint.lint(dispatch("note: open ` then a; b"))), ["R5"])

    def test_r5_separator_outside_backticks_still_counts_next_to_a_span(self) -> None:
        self.assertEqual(rule_ids(dispatch_lint.lint(dispatch("note: `x`; `y`"))), ["R5"])

    def test_r5_separator_in_a_cmd_value_does_not_count(self) -> None:
        for body in ('cmd: "a; b; c"', "  cmd: a; b", '- cmd: "a; b"', f"cmd: a{FULL_WIDTH_SEMICOLON}b"):
            with self.subTest(body):
                self.assertEqual(dispatch_lint.lint(dispatch(body)), [])

    def test_r5_the_cmd_exemption_is_only_for_a_field_named_cmd(self) -> None:
        for body in ('mycmd: "a; b"', 'note: cmd: a; b', 'cmd2: "a; b"', "- run the cmd: a; b"):
            with self.subTest(body):
                self.assertEqual(rule_ids(dispatch_lint.lint(dispatch(body))), ["R5"])

    def test_r5_separator_inside_quotes_counts(self) -> None:
        for body in ('note: "first; second"', "note: 'first; second'"):
            with self.subTest(body):
                self.assertEqual(rule_ids(dispatch_lint.lint(dispatch(body))), ["R5"])

    def test_r5_a_semicolon_without_a_following_space_is_not_a_separator(self) -> None:
        self.assertEqual(dispatch_lint.lint(dispatch("note: a;b")), [])

    def test_r5_empty_and_blank_lines_are_not_actions(self) -> None:
        self.assertEqual(dispatch_lint.lint(dispatch("", "     ", "note: x")), [])

    def test_r5_does_not_apply_inside_a_code_fence(self) -> None:
        self.assertEqual(dispatch_lint.lint(dispatch("```", "a; b; c", "```")), [])

    def test_r5_exits_1_as_a_process_and_names_the_rule(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dl-") as tmp:
            path = Path(tmp) / "two.yaml"
            path.write_text(dispatch("note: first; second"), encoding="utf-8", newline="\n")
            done = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), str(path)], capture_output=True, text=True, encoding="utf-8",
            )
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("R5 line 3 holds 2 actions; put each on its own list item", done.stdout)

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


def digest_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ticket_text(state_cell: str | None, *, before: tuple[str, ...] = (), after: tuple[str, ...] = ()) -> str:
    """A ticket whose table holds one state row with the given cell (None: no state row at all)."""
    rows = ["| 欄位 | 內容 |", "| --- | --- |", *before]
    if state_cell is not None:
        rows.append(f"| {STATE} | {state_cell} |")
    rows.extend(after)
    return "# 75｜ticket\n\n" + "\n".join(rows) + "\n"


class DispatchDigestTests(unittest.TestCase):
    """R7: the ticket's state row records the digest of the dispatch file's bytes."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="dl-")
        self.root = Path(self.tmp.name)
        self.dispatch_bytes = dispatch("note: the dispatch under test").encode("utf-8")
        self.dispatch_path = self.root / "JAS-1-1.yaml"
        self.dispatch_path.write_bytes(self.dispatch_bytes)
        self.digest = digest_of(self.dispatch_bytes)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_ticket(self, text: str | bytes, name: str = "ticket.md") -> Path:
        path = self.root / name
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
        return path

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dispatch_lint.main(argv)
        return code, out.getvalue(), err.getvalue()

    def usage_lines(self, err: str) -> int:
        return len([line for line in err.splitlines() if line.startswith("usage:")])

    def lint_with(
        self, state_cell: str | None, before: tuple[str, ...] = (), after: tuple[str, ...] = (),
    ) -> tuple[int, list[str]]:
        ticket = self.write_ticket(ticket_text(state_cell, before=before, after=after))
        code, out, err = self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])
        self.assertEqual(err, "")
        lines = out.splitlines()
        self.assertEqual(lines[-1], "LINT PASS" if code == 0 else f"LINT FAIL ({len(lines) - 1})")
        return code, lines[:-1]

    def assert_red(
        self, state_cell: str | None, found: str, before: tuple[str, ...] = (), after: tuple[str, ...] = (),
    ) -> None:
        code, lines = self.lint_with(state_cell, before=before, after=after)
        self.assertEqual(code, 1, lines)
        self.assertEqual(rule_ids(lines), ["R7"], lines)
        self.assertIn(f"expected {TOKEN}{self.digest}", lines[0])
        self.assertIn(f"found {found}", lines[0])

    def test_the_matching_digest_passes(self) -> None:
        self.assertEqual(self.lint_with(f"`INTEGRATED`; {TOKEN}{self.digest}"), (0, []))

    def test_what_follows_the_run_is_ignored(self) -> None:
        tails = ("", " ", " (`doc/x/JAS-1-1.yaml`)", "(`doc/x/JAS-1-1.yaml`)", "; receipt `a.md`", ";receipt", " （note）", "\t")
        for tail in tails:
            with self.subTest(tail=tail):
                self.assertEqual(self.lint_with(f"`DONE`; {TOKEN}{self.digest}{tail}"), (0, []))

    def test_the_digest_may_stand_first_in_the_cell(self) -> None:
        self.assertEqual(self.lint_with(f"{TOKEN}{self.digest}"), (0, []))

    def test_a_pipe_inside_the_state_cell_does_not_cut_the_digest_off(self) -> None:
        self.assertEqual(self.lint_with(f"`DONE` | note; {TOKEN}{self.digest}"), (0, []))

    def test_the_digest_is_of_the_file_bytes(self) -> None:
        crlf = self.dispatch_bytes.replace(b"\n", b"\r\n")
        self.dispatch_path.write_bytes(crlf)
        self.assertEqual(self.lint_with(f"`DONE`; {TOKEN}{digest_of(crlf)}"), (0, []))
        code, lines = self.lint_with(f"`DONE`; {TOKEN}{self.digest}")
        self.assertEqual((code, rule_ids(lines)), (1, ["R7"]))
        self.assertIn(f"expected {TOKEN}{digest_of(crlf)}", lines[0])

    def test_a_ticket_with_crlf_line_ends_passes(self) -> None:
        text = ticket_text(f"`DONE`; {TOKEN}{self.digest}").replace("\n", "\r\n")
        ticket = self.write_ticket(text)
        self.assertEqual(self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])[0], 0)

    def test_the_first_state_row_is_the_one_read(self) -> None:
        other = digest_of(b"another file")
        self.assert_red(
            f"`DONE`; {TOKEN}{other}", other + " (a different digest)", after=(f"| {STATE} | {TOKEN}{self.digest} |",),
        )
        self.assertEqual(
            self.lint_with(f"`DONE`; {TOKEN}{self.digest}", after=(f"| {STATE} | {TOKEN}{other} |",)), (0, []),
        )

    def test_only_a_row_whose_first_cell_is_exactly_the_state_cell_counts(self) -> None:
        decoys = (
            f"| {STATE}說明 | {TOKEN}{self.digest} |",
            f"| 前{STATE} | {TOKEN}{self.digest} |",
            f"| x | {STATE} | {TOKEN}{self.digest} |",
            f"{STATE} | {TOKEN}{self.digest}",
            f"{TOKEN}{self.digest}",
        )
        for decoy in decoys:
            with self.subTest(decoy=decoy):
                self.assert_red(None, "no state row", before=(decoy,))

    def test_a_state_row_without_a_trailing_pipe_is_read(self) -> None:
        ticket = self.write_ticket(f"| {STATE} | `DONE`; {TOKEN}{self.digest}\n")
        self.assertEqual(self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])[0], 0)

    def test_no_state_row_is_red(self) -> None:
        self.assert_red(None, "no state row")

    def test_an_empty_ticket_has_no_state_row(self) -> None:
        ticket = self.write_ticket("")
        code, out, _ = self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])
        self.assertEqual(code, 1)
        self.assertIn("found no state row", out)

    def test_an_empty_or_blank_state_cell_is_red(self) -> None:
        for cell in ("", "   "):
            with self.subTest(repr(cell)):
                self.assert_red(cell, "an empty state cell")

    def test_a_cell_without_the_token_is_red(self) -> None:
        cells = (
            "`PLANNED`",
            f"`DONE`; dispatch=sha1:{self.digest}",
            f"`DONE`; {self.digest}",
            f"`DONE`; dispatch={self.digest}",
        )
        for cell in cells:
            with self.subTest(cell):
                self.assert_red(cell, f"no {TOKEN}")

    def test_the_token_with_nothing_after_it_is_red(self) -> None:
        for cell in (TOKEN, f"`DONE`; {TOKEN}", f"`DONE`; {TOKEN} (`x`)"):
            with self.subTest(cell):
                self.assert_red(cell, "nothing (0 characters, not 64)")

    def test_two_tokens_in_the_cell_are_red_even_when_both_match(self) -> None:
        self.assert_red(f"`DONE`; {TOKEN}{self.digest}; {TOKEN}{self.digest}", f"2 {TOKEN} in the state cell")

    def test_a_run_of_63_or_65_characters_is_red(self) -> None:
        for run in (self.digest[:-1], self.digest + "0", self.digest + self.digest[:1]):
            with self.subTest(len(run)):
                self.assert_red(f"`DONE`; {TOKEN}{run} (`x`)", f"{run} ({len(run)} characters, not 64)")

    def test_a_run_that_continues_with_a_letter_is_red(self) -> None:
        run = self.digest + "x"
        self.assert_red(f"`DONE`; {TOKEN}{run}", f"{run} (65 characters, not 64)")

    def test_upper_case_hex_is_red_even_when_it_is_the_right_digest(self) -> None:
        run = self.digest.upper()
        self.assertNotEqual(run, self.digest)
        self.assert_red(f"`DONE`; {TOKEN}{run}", f"{run} (not 64 lower-case hex digits)")

    def test_one_upper_case_digit_is_red(self) -> None:
        position = next(i for i, ch in enumerate(self.digest) if ch.isalpha())
        run = self.digest[:position] + self.digest[position].upper() + self.digest[position + 1:]
        self.assert_red(f"`DONE`; {TOKEN}{run}", f"{run} (not 64 lower-case hex digits)")

    def test_a_run_of_64_non_hex_letters_is_red(self) -> None:
        run = "g" * 64
        self.assert_red(f"`DONE`; {TOKEN}{run}", f"{run} (not 64 lower-case hex digits)")

    def test_the_digest_of_another_file_is_red(self) -> None:
        other = digest_of(b"another file")
        self.assert_red(f"`DONE`; {TOKEN}{other}", f"{other} (a different digest)")

    def test_the_whole_digest_is_compared_not_a_prefix(self) -> None:
        for position in (0, 15, 16, 17, 32, 63):
            with self.subTest(position=position):
                flipped = "1" if self.digest[position] != "1" else "2"
                run = self.digest[:position] + flipped + self.digest[position + 1:]
                self.assert_red(f"`DONE`; {TOKEN}{run}", f"{run} (a different digest)")

    def test_a_dispatch_file_changed_by_one_byte_after_the_digest_was_written_is_red(self) -> None:
        cell = f"`DONE`; {TOKEN}{self.digest}"
        self.assertEqual(self.lint_with(cell), (0, []))
        self.dispatch_path.write_bytes(self.dispatch_bytes + b" ")
        changed = digest_of(self.dispatch_bytes + b" ")
        code, lines = self.lint_with(cell)
        self.assertEqual((code, rule_ids(lines)), (1, ["R7"]))
        self.assertIn(f"expected {TOKEN}{changed}", lines[0])
        self.assertIn(f"found {self.digest}", lines[0])

    def test_r7_is_added_to_the_r1_to_r6_lines_not_instead_of_them(self) -> None:
        bad = dispatch("note: first; second")
        self.dispatch_path.write_text(bad, encoding="utf-8", newline="\n")
        ticket = self.write_ticket(ticket_text(f"`DONE`; {TOKEN}{digest_of(b'x')}"))
        code, out, _ = self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])
        self.assertEqual(code, 1)
        lines = out.splitlines()
        self.assertEqual(rule_ids(lines[:-1]), ["R5", "R7"])
        self.assertEqual(lines[:1], dispatch_lint.lint(bad))
        self.assertEqual(lines[-1], "LINT FAIL (2)")

    def test_a_matching_digest_does_not_hide_an_r1_to_r6_violation(self) -> None:
        bad = dispatch("note: first; second").encode("utf-8")
        self.dispatch_path.write_bytes(bad)
        ticket = self.write_ticket(ticket_text(f"`DONE`; {TOKEN}{digest_of(bad)}"))
        code, out, _ = self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])
        self.assertEqual(code, 1)
        self.assertEqual(rule_ids(out.splitlines()[:-1]), ["R5"])

    def test_without_the_option_the_output_ignores_every_ticket(self) -> None:
        for text in (dispatch("note: ok"), dispatch("prose", "note: a; b")):
            with self.subTest(text):
                self.dispatch_path.write_text(text, encoding="utf-8", newline="\n")
                problems = dispatch_lint.lint(text)
                verdict = "LINT PASS" if not problems else f"LINT FAIL ({len(problems)})"
                stdout = "".join(f"{line}\n" for line in [*problems, verdict])
                self.assertEqual(self.run_main([str(self.dispatch_path)]), (0 if not problems else 1, stdout, ""))
                self.assertNotIn("R7", stdout)

    def test_without_the_option_a_crlf_dispatch_gives_the_same_output_as_lint(self) -> None:
        text = dispatch("prose", "note: a; b")
        self.dispatch_path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        problems = dispatch_lint.lint(text)
        code, out, _ = self.run_main([str(self.dispatch_path)])
        self.assertEqual(code, 1)
        self.assertEqual(out.splitlines(), [*problems, f"LINT FAIL ({len(problems)})"])

    def test_an_unreadable_ticket_exits_3_with_empty_stdout(self) -> None:
        folder = self.root / "folder"
        folder.mkdir()
        for label, path in (("missing", self.root / "absent.md"), ("a directory", folder)):
            with self.subTest(label):
                code, out, err = self.run_main([str(self.dispatch_path), "--ticket", str(path)])
                self.assertEqual((code, out), (3, ""))
                self.assertEqual(self.usage_lines(err), 1, err)

    def test_a_non_utf8_ticket_exits_3_with_empty_stdout(self) -> None:
        ticket = self.write_ticket(b"\xff\xfe\x00\xff")
        code, out, err = self.run_main([str(self.dispatch_path), "--ticket", str(ticket)])
        self.assertEqual((code, out), (3, ""))
        self.assertEqual(self.usage_lines(err), 1, err)

    def test_a_bad_ticket_is_decided_before_the_rules_run(self) -> None:
        self.dispatch_path.write_text(dispatch("prose", "note: a; b"), encoding="utf-8", newline="\n")
        code, out, _ = self.run_main([str(self.dispatch_path), "--ticket", str(self.root / "absent.md")])
        self.assertEqual((code, out), (3, ""))

    def test_the_ticket_option_usage_errors_exit_3(self) -> None:
        ticket = self.write_ticket(ticket_text(f"`DONE`; {TOKEN}{self.digest}"))
        cases = {
            "no value": [str(self.dispatch_path), "--ticket"],
            "twice": [str(self.dispatch_path), "--ticket", str(ticket), "--ticket", str(ticket)],
            "no dispatch": ["--ticket", str(ticket)],
        }
        for label, argv in cases.items():
            with self.subTest(label):
                code, out, err = self.run_main(argv)
                self.assertEqual((code, out), (3, ""))
                self.assertEqual(self.usage_lines(err), 1, err)

    def test_the_ticket_option_may_come_before_the_dispatch_or_beside_chat_words(self) -> None:
        ticket = self.write_ticket(ticket_text(f"`DONE`; {TOKEN}{self.digest}"))
        for argv in (
            ["--ticket", str(ticket), str(self.dispatch_path)],
            [str(self.dispatch_path), "--chat-words", "please", "--ticket", str(ticket)],
        ):
            with self.subTest(argv[:1]):
                self.assertEqual(self.run_main(argv), (0, "LINT PASS\n", ""))

    def test_the_usage_line_and_docstring_name_the_ticket_option_and_r7(self) -> None:
        self.assertIn("--ticket <ticket-file>", dispatch_lint.USAGE)
        self.assertIn("R7", dispatch_lint.__doc__ or "")

    def test_the_process_exit_codes(self) -> None:
        good = self.write_ticket(ticket_text(f"`DONE`; {TOKEN}{self.digest}"), "good.md")
        red = self.write_ticket(ticket_text(f"`DONE`; {TOKEN}{digest_of(b'x')}"), "red.md")
        expected = ((good, 0, "LINT PASS\n"), (red, 1, None), (self.root / "absent.md", 3, ""))
        for ticket, code, stdout in expected:
            with self.subTest(ticket.name):
                done = subprocess.run(
                    [sys.executable, "-I", str(SCRIPT), str(self.dispatch_path), "--ticket", str(ticket)],
                    capture_output=True, text=True, encoding="utf-8",
                )
                self.assertEqual(done.returncode, code, done.stdout + done.stderr)
                if stdout is not None:
                    self.assertEqual(done.stdout, stdout)
                else:
                    self.assertIn("R7 state row: expected", done.stdout)


WITHOUT_MODEL = "R8 profile: without model:"
WITHOUT_EFFORT = "R8 profile: without effort:"
MODEL_INVALID = "R8 model: invalid"
EFFORT_INVALID = "R8 effort: invalid"


def bound(*body: str, model: str | None = "claude-sonnet-5-5", effort: str | None = "high") -> str:
    """A dispatch with a profile field and, unless None, the model and effort fields."""
    fields = ['profile: "implementation-standard"']
    if model is not None:
        fields.append(f"model: {model}")
    if effort is not None:
        fields.append(f"effort: {effort}")
    return dispatch(*fields, *body)


def r8(text: str) -> list[str]:
    return [problem for problem in dispatch_lint.lint(text) if problem.startswith("R8")]


class SeatBindingTests(unittest.TestCase):
    """R8: a dispatch with a top-level profile names its model and effort, each one item."""

    def test_a_bound_dispatch_passes(self) -> None:
        self.assertEqual(dispatch_lint.lint(bound()), [])

    def test_a_dispatch_without_a_profile_field_is_never_an_r8_case(self) -> None:
        for text in (dispatch(), dispatch("model: a b"), dispatch("effort: a, b"), dispatch("model: x", "effort: y")):
            with self.subTest(text):
                self.assertEqual(r8(text), [])

    def test_each_value_may_stand_inside_one_pair_of_double_quotes(self) -> None:
        for model, effort in (('"claude-sonnet-5-5"', '"high"'), ("claude-sonnet-5-5", "high"), ('"a.b_c-d"', "X9")):
            with self.subTest(model=model, effort=effort):
                self.assertEqual(r8(bound(model=model, effort=effort)), [])

    def test_a_missing_model_field_is_named(self) -> None:
        self.assertEqual(r8(bound(model=None)), [WITHOUT_MODEL])

    def test_a_missing_effort_field_is_named(self) -> None:
        self.assertEqual(r8(bound(effort=None)), [WITHOUT_EFFORT])

    def test_both_missing_prints_model_first(self) -> None:
        self.assertEqual(r8(bound(model=None, effort=None)), [WITHOUT_MODEL, WITHOUT_EFFORT])

    def test_an_invalid_model_value_is_named_for_each_defect_form(self) -> None:
        for bad in ("", '""', '" "', "a, b", "a,b", "a b", "a,a", '"a', 'a"', '""a""', "'a'", "-a", "a/b", "a:b", "(a)"):
            with self.subTest(bad=bad):
                self.assertEqual(r8(bound(model=bad)), [MODEL_INVALID])

    def test_an_invalid_effort_value_is_named_for_each_defect_form(self) -> None:
        for bad in ("", '""', '" "', "a, b", "a,b", "a b", "a,a", '"a', 'a"', '""a""', "'a'", "-a", "a/b", "a:b", "(a)"):
            with self.subTest(bad=bad):
                self.assertEqual(r8(bound(effort=bad)), [EFFORT_INVALID])

    def test_a_list_is_invalid_in_a_dispatch_even_when_it_would_be_a_valid_list(self) -> None:
        self.assertEqual(r8(bound(model="a,b")), [MODEL_INVALID])
        self.assertEqual(r8(bound(effort='"a,b"')), [EFFORT_INVALID])

    def test_the_four_lines_come_in_the_fixed_order(self) -> None:
        self.assertEqual(r8(bound(model=None, effort="a b")), [WITHOUT_MODEL, EFFORT_INVALID])
        self.assertEqual(r8(bound(model="a b", effort=None)), [WITHOUT_EFFORT, MODEL_INVALID])
        self.assertEqual(r8(bound(model="", effort="")), [MODEL_INVALID, EFFORT_INVALID])

    def test_a_field_given_twice_is_invalid(self) -> None:
        self.assertEqual(r8(bound("model: claude-sonnet-5-5")), [MODEL_INVALID])
        self.assertEqual(r8(bound("effort: high")), [EFFORT_INVALID])

    def test_only_a_field_at_column_zero_outside_a_fence_counts(self) -> None:
        indented = dispatch('profile: "implementation-standard"', "  model: m", "  effort: e")
        self.assertEqual(r8(indented), [WITHOUT_MODEL, WITHOUT_EFFORT])
        listed = dispatch('profile: "implementation-standard"', "- model: m", "- effort: e")
        self.assertEqual(r8(listed), [WITHOUT_MODEL, WITHOUT_EFFORT])
        fenced = dispatch('profile: "implementation-standard"', "```", "model: m", "effort: e", "```")
        self.assertEqual(r8(fenced), [WITHOUT_MODEL, WITHOUT_EFFORT])
        self.assertEqual(r8(bound("```", "model: a b", "effort: a b", "```")), [])

    def test_a_profile_inside_a_fence_or_indented_is_not_a_profile_field(self) -> None:
        self.assertEqual(r8(dispatch("```", 'profile: "p"', "```")), [])
        self.assertEqual(r8(dispatch('  profile: "p"')), [])
        self.assertEqual(r8(dispatch("- profile: p")), [])

    def test_a_field_whose_name_only_starts_with_model_or_effort_is_another_field(self) -> None:
        text = dispatch('profile: "implementation-standard"', "model_name: m", "effort_level: e", "models: m", "efforts: e")
        self.assertEqual(r8(text), [WITHOUT_MODEL, WITHOUT_EFFORT])

    def test_the_fence_rule_matches_the_per_line_rules_after_a_closed_fence(self) -> None:
        text = bound("```", "free prose", "```", "note: ok")
        self.assertEqual(dispatch_lint.lint(text), [])
        text = dispatch("```", "model: m", "```", 'profile: "p"', "model: m", "effort: e")
        self.assertEqual(r8(text), [])

    def test_r8_follows_the_per_line_rules_and_does_not_replace_them(self) -> None:
        text = bound("prose line", model=None)
        problems = dispatch_lint.lint(text)
        self.assertEqual(rule_ids(problems), ["R2", "R8"])
        self.assertEqual(problems[-1], WITHOUT_MODEL)

    def test_a_crlf_dispatch_is_read_the_same_way(self) -> None:
        text = bound(model=None)
        self.assertEqual(r8(text.replace("\n", "\r\n")), [WITHOUT_MODEL])
        self.assertEqual(r8(bound().replace("\n", "\r\n")), [])


class SeatBindingProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="dl-r8-")
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dispatch_lint.main(argv)
        return code, out.getvalue(), err.getvalue()

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def test_a_missing_field_is_exit_1_with_the_line_and_the_count(self) -> None:
        path = self.write("d.yaml", bound(model=None, effort=None))
        self.assertEqual(self.run_main([str(path)]), (1, f"{WITHOUT_MODEL}\n{WITHOUT_EFFORT}\nLINT FAIL (2)\n", ""))

    def test_a_bound_dispatch_is_exit_0(self) -> None:
        path = self.write("d.yaml", bound())
        self.assertEqual(self.run_main([str(path)]), (0, "LINT PASS\n", ""))

    def test_r8_runs_with_ticket_and_the_digest_rule_still_runs(self) -> None:
        text = bound(model="a b")
        path = self.write("d.yaml", text)
        digest = digest_of(text.encode("utf-8"))
        good = self.write("good.md", ticket_text(f"`DONE`; {TOKEN}{digest}"))
        code, out, _ = self.run_main([str(path), "--ticket", str(good)])
        self.assertEqual((code, out), (1, f"{MODEL_INVALID}\nLINT FAIL (1)\n"))
        wrong = self.write("wrong.md", ticket_text(f"`DONE`; {TOKEN}{digest_of(b'x')}"))
        code, out, _ = self.run_main([str(path), "--ticket", str(wrong)])
        self.assertEqual(code, 1)
        self.assertEqual(rule_ids(out.splitlines()), ["R8", "R7", "LINT"])

    def test_r8_alone_with_a_matching_digest_and_a_bound_dispatch_passes(self) -> None:
        text = bound()
        path = self.write("d.yaml", text)
        good = self.write("good.md", ticket_text(f"`DONE`; {TOKEN}{digest_of(text.encode('utf-8'))}"))
        self.assertEqual(self.run_main([str(path), "--ticket", str(good)]), (0, "LINT PASS\n", ""))

    def test_without_ticket_the_output_is_as_before_for_a_file_without_a_profile_field(self) -> None:
        text = dispatch("prose", "note: a; b", "model: a b")
        path = self.write("d.yaml", text)
        code, out, _ = self.run_main([str(path)])
        before = [problem for problem in dispatch_lint.lint(text) if not problem.startswith("R8")]
        self.assertEqual(code, 1)
        self.assertEqual(out.splitlines(), [*before, f"LINT FAIL ({len(before)})"])
        self.assertNotIn("R8", out)

    def test_the_docstring_names_r8_and_its_four_lines(self) -> None:
        doc = dispatch_lint.__doc__ or ""
        for needle in ("R8", WITHOUT_MODEL, WITHOUT_EFFORT, MODEL_INVALID, EFFORT_INVALID):
            with self.subTest(needle):
                self.assertIn(needle, doc)

    def test_the_process_exit_code_is_1_for_a_missing_field(self) -> None:
        path = self.write("d.yaml", bound(effort=None))
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), str(path)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(done.stdout, f"{WITHOUT_EFFORT}\nLINT FAIL (1)\n")


if __name__ == "__main__":
    unittest.main()
