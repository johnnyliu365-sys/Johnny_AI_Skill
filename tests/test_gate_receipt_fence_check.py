"""Behavioural tests for the receipt_fence_check gate script.

Every fixture is generated in a temporary directory; every expected count is derived
from what the fixture wrote.
"""
from __future__ import annotations

import contextlib
import io
import os
import posixpath
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import receipt_fence_check as rf  # noqa: E402

EXPECTED_ELISIONS = ("(empty)", "<snip>", "…", "...")
SCRIPT = _SCRIPTS / "receipt_fence_check.py"
NON_CP950 = chr(0x0E01)  # outside code page 950


class ReceiptFenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rf-")
        self.root = Path(self.tmp.name)
        self.ev = self.root / "evidence"
        self.ev.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def check(self, cap: str = "out.txt", body: str = "ok\n", command: bool = True) -> int:
        (self.ev / cap).write_text(body, encoding="utf-8", newline="\n")
        before = f"cmd: tool > {cap} 2>&1; echo exit=0 >> {cap}\n" if command else ""
        receipt = self.root / "receipt.md"
        receipt.write_text(f"## delivery\n{before}capture: {cap}\n```text\n{body.rstrip()}\n```\n", encoding="utf-8")
        return rf.explicit(receipt, "## delivery", self.ev)

    def test_body_matches_and_mismatch_fails(self) -> None:
        self.assertEqual(self.check(), 0)
        (self.ev / "out.txt").write_text("actual", encoding="utf-8")
        receipt = self.root / "mismatch.md"
        receipt.write_text("## delivery\ncmd: tool > out.txt\ncapture: out.txt\n```text\nother\n```\n", encoding="utf-8")
        self.assertEqual(rf.explicit(receipt, "## delivery", self.ev), 1)

    def test_cli_three_fences_normalizes_newlines_and_counts_two_failures(self) -> None:
        (self.ev / "same.txt").write_bytes(b"same\n")
        (self.ev / "actual.txt").write_bytes(b"actual\n")
        receipt = self.root / "three.md"
        lines = [
            "## delivery",
            "cmd: tool > same.txt",
            "capture: same.txt",
            "```text",
            "same",
            "```",
            "cmd: tool > actual.txt",
            "capture: actual.txt",
            "```text",
            "different",
            "```",
            "cmd: tool > missing.txt",
            "capture: missing.txt",
            "```text",
            "absent",
            "```",
        ]
        receipt.write_bytes("\r\n".join(lines).encode("utf-8") + b"\r\n")
        result, output = run_cli(rf, [str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(result, 1)
        self.assertIn("FAIL BODY_MISMATCH at section line 9: actual.txt", output)
        self.assertIn("FAIL CAPTURE_MISSING at section line 14:", output)
        self.assertTrue(output.endswith("fences=3 failures=2\n"), output)

    def test_scan_lf_receipt_and_capture_stay_green(self) -> None:
        root = self.root / "lf-tree"
        evidence = root / "evidence"
        evidence.mkdir(parents=True)
        capture = evidence / "lf.txt"
        receipt = root / "receipt.md"
        capture.write_bytes(b"captured LF\n")
        receipt.write_bytes(
            b"## delivery\ncmd: tool > lf.txt\ncapture: lf.txt\n```text\ncaptured LF\n```\n"
        )
        self.assertNotIn(b"\r\n", capture.read_bytes())
        self.assertNotIn(b"\r\n", receipt.read_bytes())
        result, output = run_cli(rf, ["--scan", str(root)])
        self.assertEqual(result, 0)
        self.assertTrue(output.endswith("receipts=1 sections=1 skipped=0 fences=1 failures=0 legacy_cmd=0 legacy_ref=1\n"), output)

    def test_requires_nearby_capture(self) -> None:
        n, failures = rf.check_section(["## x", "```text", "x", "```"], self.ev, 0)
        self.assertEqual(n, 1)
        self.assertTrue(any("FENCE_CAPTURE_MISSING" in f for f in failures))

    def test_capture_distance_three_is_in_and_four_is_out(self) -> None:
        (self.ev / "near.txt").write_text("x", encoding="utf-8")
        (self.ev / "far.txt").write_text("x", encoding="utf-8")
        near = ["capture: near.txt", "padding one", "padding two", "```text", "x", "```"]
        far = ["capture: far.txt", "padding one", "padding two", "padding three", "```text", "x", "```"]
        _, near_failures = rf.check_section(near, self.ev, 0)
        _, far_failures = rf.check_section(far, self.ev, 0)
        self.assertFalse(any("FENCE_CAPTURE_MISSING" in f for f in near_failures), near_failures)
        self.assertTrue(any("FENCE_CAPTURE_MISSING" in f for f in far_failures), far_failures)

    def test_elisions_must_be_captured(self) -> None:
        (self.ev / "out.txt").write_text("ok", encoding="utf-8")
        lines = ["cmd: tool > out.txt", "capture: out.txt", "```text", "ok", "...", "```"]
        _, failures = rf.check_section(lines, self.ev, 0)
        self.assertTrue(any("ELISION_MISSING" in f for f in failures))

    def test_every_elision_marker_has_positive_and_negative_case(self) -> None:
        self.assertTrue(elision_oracle(rf))

    def test_scan_ambiguity_and_missing(self) -> None:
        self.assertTrue(scan_ambiguity_oracle(rf))

    def test_cli_scan_skip_missing_ambiguous_and_subheading_counts(self) -> None:
        root = self.root / "tree"
        good_ev = root / "a" / "evidence"
        bad_ev = root / "b" / "evidence"
        for name in ("good-a.txt", "good-b.txt"):
            (good_ev / name).parent.mkdir(parents=True, exist_ok=True)
            (good_ev / name).write_text(name + "\n", encoding="utf-8")
        (bad_ev / "left").mkdir(parents=True)
        (bad_ev / "right").mkdir()
        (bad_ev / "left" / "same.txt").write_text("same\n", encoding="utf-8")
        (bad_ev / "right" / "same.txt").write_text("same\n", encoding="utf-8")
        (root / "a" / "receipt.md").write_text(
            "## legacy\nignored text\n```text\nnot scanned\n```\n"
            "## current\ncapture: good-a.txt\n```text\ngood-a.txt\n```\n"
            "### nested\ncapture: good-b.txt\n```text\ngood-b.txt\n```\n",
            encoding="utf-8",
        )
        (root / "b" / "receipt.md").write_text(
            "## bad\ncapture: same.txt\n```text\nsame\n```\n"
            "capture: absent.txt\n```text\nmissing\n```\n",
            encoding="utf-8",
        )
        result, output = run_cli(rf, ["--scan", str(root)])
        self.assertEqual(result, 1)
        self.assertIn("FAIL SCAN_CAPTURE_AMBIGUOUS", output)
        self.assertIn("FAIL SCAN_CAPTURE_MISSING", output)
        self.assertTrue(output.endswith("receipts=2 sections=2 skipped=1 fences=4 failures=4 legacy_cmd=2 legacy_ref=2\n"), output)

    def test_cmd_required_explicit(self) -> None:
        self.assertEqual(self.check(command=False), 1)

    def test_scan_mixed_command_section_requires_command_for_every_capture(self) -> None:
        root = self.root / "tree"
        ev = root / "evidence"
        ev.mkdir(parents=True)
        (ev / "present.txt").write_text("present\n", encoding="utf-8")
        (ev / "mixed.txt").write_text("mixed\n", encoding="utf-8")
        (root / "receipt.md").write_text(
            "## mixed\ncmd: tool > present.txt\ncapture: present.txt\n````text\npresent\n````\n"
            "capture: mixed.txt\n```text\nmixed\n```\n",
            encoding="utf-8",
        )
        result, output = run_cli(rf, ["--scan", str(root)])
        self.assertEqual(result, 1)
        self.assertIn("FAIL CMD_MISSING at section line", output)
        self.assertTrue(output.endswith("receipts=1 sections=1 skipped=0 fences=2 failures=1 legacy_cmd=0 legacy_ref=1\n"), output)

    def test_cli_requires_cmd_and_usage_exit_codes(self) -> None:
        receipt = self.root / "no-command.md"
        receipt.write_text("## delivery\ncapture: out.txt\n```text\nok\n```\n", encoding="utf-8")
        (self.ev / "out.txt").write_text("ok\n", encoding="utf-8")
        result, output = run_cli(rf, [str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(result, 1)
        self.assertIn("FAIL CMD_MISSING at section line 2", output)
        result, output = run_cli(rf, [])
        self.assertEqual(result, 3)
        self.assertIn("usage:", output)

    def test_placeholder_and_redirect_guards(self) -> None:
        lines = ["cmd: run <receipt> > other.txt", "capture: out.txt", "```text", "x", "```"]
        _, failures = rf.check_section(lines, self.ev, 0)
        self.assertTrue(any("CMD_PLACEHOLDER" in f for f in failures))
        self.assertTrue(any("CMD_NO_REDIRECT" in f for f in failures))

    def test_scan_applies_guards_only_when_section_has_cmd(self) -> None:
        root = self.root / "tree"
        ev = root / "evidence"
        ev.mkdir(parents=True)
        (ev / "legacy.txt").write_text("legacy\n", encoding="utf-8")
        (ev / "out.txt").write_text("ok\n", encoding="utf-8")
        (root / "receipt.md").write_text(
            "## legacy\ncapture: legacy.txt\n```text\nlegacy\n```\n"
            "## current\ncmd: tool <arg> > other.txt\ncapture: out.txt\n```text\nok\n```\n",
            encoding="utf-8",
        )
        result, output = run_cli(rf, ["--scan", str(root)])
        self.assertEqual(result, 1)
        self.assertIn("FAIL CMD_PLACEHOLDER at section line", output)
        self.assertIn("FAIL CMD_NO_REDIRECT at section line", output)
        self.assertTrue(output.endswith("receipts=1 sections=2 skipped=0 fences=2 failures=2 legacy_cmd=1 legacy_ref=2\n"), output)

    def test_self_note_excludes_its_own_fence(self) -> None:
        (self.ev / "note.txt").write_text("fences=0 (excluding this run's own capture fence) failures=0", encoding="utf-8")
        receipt = self.root / "self.md"
        receipt.write_text("## delivery\ncmd: py checker --self-note > note.txt 2>&1; echo exit=0 >> note.txt\ncapture: note.txt\n```text\nfences=0 (excluding this run's own capture fence) failures=0\n```\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = rf.main([str(receipt), "## delivery", str(self.ev), "--self-note"])
        self.assertEqual(result, 0)
        self.assertIn("fences=0 (excluding this run's own capture fence) failures=0", output.getvalue())

    def test_self_note_is_bound_to_its_receipt_and_section(self) -> None:
        self.assertTrue(self_note_oracle(rf))

    def test_redirect_targets_and_append_shapes(self) -> None:
        self.assertTrue(redirect_target_oracle(rf))

    def test_nested_bare_capture_resolution_and_negative_controls(self) -> None:
        self.assertTrue(nested_bare_capture_oracle(rf))

    def test_evd_declaration_resolves_prefixed_targets(self) -> None:
        self.assertTrue(evd_oracle(rf))


    def test_wrapper_shells_are_stripped(self) -> None:
        self.assertTrue(wrapper_oracle(rf))



    def test_copy_item_and_add_content_path(self) -> None:
        self.assertTrue(copy_item_oracle(rf))



    def test_authority_root_maps_absolute_prefix(self) -> None:
        self.assertTrue(authority_root_oracle(rf))


    def test_bounded_relative_bases(self) -> None:
        self.assertTrue(bounded_base_oracle(rf))



    def test_exit_echo_command_word(self) -> None:
        self.assertTrue(exit_echo_oracle(rf))


    def test_w6_negative_real_echo_without_redirect_stays_red(self) -> None:
        lines = ["cmd: echo exit=$?", "capture: out.txt", "```text", "ok", "```"]
        _, failures = rf.check_section(lines, self.ev, 0, True, command_cwd=self.root)
        self.assertTrue(any("CMD_NO_REDIRECT" in f for f in failures), failures)

    def test_authority_root_with_spaces(self) -> None:
        self.assertTrue(authority_root_space_oracle(rf))


    def test_authority_root_equals_scan_cwd_inplace(self) -> None:
        self.assertTrue(authority_root_inplace_oracle(rf))


    def test_placeholder_resolved_at_every_absolute_comparison_entry_point(self) -> None:
        self.assertTrue(placeholder_resolution_oracle(rf))


    def test_filter_chain(self) -> None:
        self.assertTrue(filter_chain_oracle(rf))



    def test_loop_redirect(self) -> None:
        self.assertTrue(loop_redirect_oracle(rf))

    def test_chain_member_overwrite_breaks_chain(self) -> None:
        self.assertTrue(chain_overwrite_oracle(rf))

    def test_joined_exit_echo_is_its_own_statement(self) -> None:
        self.assertTrue(joined_exit_oracle(rf))

    def test_evd_rejects_dotdot(self) -> None:
        self.assertTrue(evd_dotdot_oracle(rf))

    def test_placeholder_requires_declaration(self) -> None:
        self.assertTrue(placeholder_declaration_oracle(rf))

    def test_exit_append_must_precede_filter_read(self) -> None:
        self.assertTrue(late_exit_append_oracle(rf))

    def test_legacy_unclaimed_exit_allowlist(self) -> None:
        self.assertTrue(legacy_unclaimed_exit_oracle(rf))

    def test_target_normalization_matches_posix_semantics(self) -> None:
        self.assertTrue(target_normalization_oracle(rf))




def run_cli(module: ModuleType, args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        result = module.main(args)
    return result, output.getvalue()


def run_scan_fixture(
    module: ModuleType, text_factory: Callable[[Path, Path], str], captures: dict[str, str]
) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="rf-scan-oracle-") as temp:
        root = Path(temp) / "tree"
        receipt = root / "receipt.md"
        evidence = root / "evidence"
        evidence.mkdir(parents=True)
        for name, content in captures.items():
            target = evidence / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        receipt.write_text(text_factory(receipt, evidence), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.scan(root)
        return result, output.getvalue()


def self_note_oracle(module: ModuleType) -> bool:
    external_note = "fences=7 (excluding this run's own capture fence) failures=0"
    matching_external = """## delivery
cmd: py -3 scripts/receipt_fence_check.py 'outside.md' '## delivery' evidence --self-note > external.txt
capture: external.txt
```text
fences=7 (excluding this run's own capture fence) failures=0
```
"""
    result, output = run_scan_fixture(module, lambda _r, _e: matching_external, {"external.txt": external_note + "\n"})
    if result != 0 or "failures=0" not in output:
        return False

    def own_note(receipt: Path, evidence: Path) -> str:
        return (
            "## delivery\n"
            f"cmd: py -3 scripts/receipt_fence_check.py '{receipt}' '## delivery' '{evidence}' --self-note > own.txt\n"
            "capture: own.txt\n```text\nfences=0 (excluding this run's own capture fence) failures=0\n```\n"
        )

    result, output = run_scan_fixture(
        module,
        own_note,
        {"own.txt": "fences=0 (excluding this run's own capture fence) failures=0\n"},
    )
    if result != 0:
        return False

    def own_note_option_first(receipt: Path, evidence: Path) -> str:
        return (
            "## delivery\n"
            f"cmd: py -3 scripts/receipt_fence_check.py --self-note '{receipt}' '## delivery' '{evidence}' > own.txt\n"
            "capture: own.txt\n```text\nfences=0 (excluding this run's own capture fence) failures=0\n```\n"
        )

    result, output = run_scan_fixture(
        module,
        own_note_option_first,
        {"own.txt": "fences=0 (excluding this run's own capture fence) failures=0\n"},
    )
    if result != 0:
        return False

    def wrong_count(receipt: Path, evidence: Path) -> str:
        return (
            "## delivery\n"
            f"cmd: py -3 scripts/receipt_fence_check.py '{receipt}' '## delivery' '{evidence}' --self-note > own.txt\n"
            "capture: own.txt\n```text\nfences=9 (excluding this run's own capture fence) failures=0\n```\n"
        )

    result, output = run_scan_fixture(
        module,
        wrong_count,
        {"own.txt": "fences=9 (excluding this run's own capture fence) failures=0\n"},
    )
    if result != 1 or "SELF_NOTE_COUNT_MISMATCH" not in output:
        return False

    def nonfinal_note(receipt: Path, evidence: Path) -> str:
        return (
            "## delivery\n"
            f"cmd: py -3 scripts/receipt_fence_check.py '{receipt}' '## delivery' '{evidence}' --self-note > own.txt\n"
            "capture: own.txt\n```text\nfences=0 (excluding this run's own capture fence) failures=0\n```\n"
            "cmd: tool > later.txt\ncapture: later.txt\n```text\nlater\n```\n"
        )

    result, output = run_scan_fixture(
        module,
        nonfinal_note,
        {
            "own.txt": "fences=0 (excluding this run's own capture fence) failures=0\n",
            "later.txt": "later\n",
        },
    )
    if result != 1 or "SELF_NOTE_NOT_FINAL" not in output:
        return False

    def mismatched_external(_receipt: Path, _evidence: Path) -> str:
        return (
            "## delivery\n"
            "cmd: py -3 scripts/receipt_fence_check.py 'outside.md' '## delivery' evidence --self-note > external.txt\n"
            "capture: external.txt\n```text\nwrong external output\n```\n"
        )

    result, output = run_scan_fixture(
        module,
        mismatched_external,
        {"external.txt": external_note + "\n"},
    )
    return result == 1 and "BODY_MISMATCH" in output


def redirect_target_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf cmd exact ") as temp:
        command_cwd = Path(temp)
        evidence = command_cwd / "docs" / "receipts" / "evidence" / "unit-a" / "c1" / "phase2"
        evidence.mkdir(parents=True)
        actual = evidence / "out.txt"
        actual.write_text("ok\n", encoding="utf-8")
        spaced = str(actual)
        repo_relative = actual.relative_to(command_cwd).as_posix()
        neighboring_relative = (actual.parent.parent / "other" / actual.name).relative_to(command_cwd).as_posix()
        commands = [
            f"tool *> '{spaced}'; $rc=$LASTEXITCODE; \"exit=$rc\" >> '{spaced}'",
            f"tool *> '{spaced}'; $captureExit=0; Add-Content -LiteralPath '{spaced}' -Value \"exit=$captureExit\" -Encoding utf8",
            f"tool > \"{spaced}\" 2>&1; echo exit=$? >> \"{spaced}\"",
            f"tool > {repo_relative}; echo exit=0 >> {repo_relative}",
            'tool > out.txt; "exit=$rc" >> out.txt',
            "cmd.exe /d /c \"git cat-file blob 0123456789abcdef0123456789abcdef01234567 > out.txt\"",
            "`tool > out.txt 2>&1; echo exit=$? >> out.txt`",
            f"Get-Content -LiteralPath 'raw.txt' -Tail 2 > '{spaced}'; if(-not $?){{exit 1}}",
        ]
        invalid = [
            "tool > other.txt; type out.txt",
            "tool > out.txt.old",
            f"tool > {neighboring_relative}; type out.txt",
            "echo '>out.txt'",
            "tool > out.txt; echo exit=0",
            "tool > out.txt; echo exit=0 >> other.txt",
            'tool > out.txt; "exit=$rc" >> other.txt',
            'tool > out.txt; "exit=$rc"',
            "tool *> out.txt; Add-Content -LiteralPath 'other.txt' -Value 'exit=0'",
        ]
        for command in commands:
            lines = [f"cmd: {command}", "capture: out.txt", "```text", "ok", "```"]
            _fences, failures = module.check_section(lines, evidence, 0, True, command_cwd=command_cwd)
            if failures:
                print(f"target accepted form rejected: {command!r}: {failures!r}")
                return False
        for command in invalid:
            lines = [f"cmd: {command}", "capture: out.txt", "```text", "ok", "```"]
            _fences, failures = module.check_section(lines, evidence, 0, True, command_cwd=command_cwd)
            if not any("CMD_NO_REDIRECT" in failure for failure in failures):
                print(f"target invalid form accepted: {command!r}: {failures!r}")
                return False

        exit_only_capture = evidence / "exit-only.txt"
        exit_only_capture.write_text("exit=0\n", encoding="utf-8")
        exit_only_lines = ["cmd: git diff --quiet old new; echo exit=$? > exit-only.txt", "capture: exit-only.txt", "```text", "exit=0", "```"]
        _fences, failures = module.check_section(exit_only_lines, evidence, 0, True, command_cwd=command_cwd)
        if failures:
            print(f"target exit-only capture rejected: {failures!r}")
            return False

        for command in ("git diff --quiet old new; echo exit=$? > other.txt", "git diff --quiet old new; echo exit=$?"):
            lines = [f"cmd: {command}", "capture: exit-only.txt", "```text", "exit=0", "```"]
            _fences, failures = module.check_section(lines, evidence, 0, True, command_cwd=command_cwd)
            if not any("CMD_NO_REDIRECT" in failure for failure in failures):
                print(f"target exit-only invalid form accepted: {command!r}: {failures!r}")
                return False
        return True


def nested_bare_capture_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-nested-bare-") as temp:
        root = Path(temp) / "tree"
        evidence = root / "evidence"
        capture = evidence / "unit-12" / "c0" / "name.txt"
        capture.parent.mkdir(parents=True)
        capture.write_text("actual\n", encoding="utf-8")
        lines = ["cmd: tool > name.txt", "capture: unit-12/c0/name.txt", "```text", "actual", "```"]
        _, explicit_failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if explicit_failures:
            print(f"target nested bare explicit rejected: {explicit_failures!r}")
            return False

        receipt = root / "receipt.md"
        receipt.write_text(
            "## delivery\ncmd: tool > name.txt\ncapture: name.txt\n```text\nactual\n```\n",
            encoding="utf-8",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.scan(root)
        if result != 0 or not output.getvalue().endswith(
            "receipts=1 sections=1 skipped=0 fences=1 failures=0 legacy_cmd=0 legacy_ref=1\n"
        ):
            print(f"target nested bare scan rejected: result={result} output={output.getvalue()!r}")
            return False

        (evidence / "unit-13" / "c0").mkdir(parents=True)
        (evidence / "unit-13" / "c0" / "name.txt").write_text("actual\n", encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.scan(root)
        if result != 1 or "FAIL SCAN_CAPTURE_AMBIGUOUS" not in output.getvalue():
            print(f"target duplicate basename not RF4: result={result} output={output.getvalue()!r}")
            return False

        for wrong_target in ("unit-13/c0/name.txt", str(evidence / "unit-13" / "c0" / "name.txt")):
            wrong_lines = [f"cmd: tool > {wrong_target}", "capture: unit-12/c0/name.txt", "```text", "actual", "```"]
            _, failures = module.check_section(wrong_lines, evidence, 0, True, command_cwd=root)
            if not any("CMD_NO_REDIRECT" in failure for failure in failures):
                print(f"target wrong full target accepted: {wrong_target!r}: {failures!r}")
                return False

        body_mismatch = ["cmd: tool > name.txt", "capture: unit-12/c0/name.txt", "```text", "different", "```"]
        _, failures = module.check_section(body_mismatch, evidence, 0, True, command_cwd=root)
        if not any("BODY_MISMATCH" in failure for failure in failures) or any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"target nested body mismatch oracle invalid: {failures!r}")
            return False
    return True


def evd_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-evd-") as temp:
        root = Path(temp)
        evidence = root / "doc" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")

        prefixed = {
            "$EVD/out.txt": "$EVD",
            "${EVD}/out.txt": "${EVD}",
            "$env:EVD/out.txt": "$env:EVD",
            "%EVD%\\out.txt": "%EVD%",
        }
        for target, label in prefixed.items():
            lines = [
                "EVD=doc/receipts/evidence",
                f"cmd: tool > {target}",
                "capture: out.txt",
                "```text",
                "ok",
                "```",
            ]
            _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
            if failures:
                print(f"evd positive rejected for {label}: {failures!r}")
                return False

        no_decl = ["cmd: tool > $EVD/out.txt", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(no_decl, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"evd no-declaration negative accepted: {failures!r}")
            return False

        outside = root / "doc" / "elsewhere"
        outside.mkdir(parents=True)
        lines = [
            "EVD=doc/elsewhere",
            "cmd: tool > $EVD/out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"evd outside-evidence-root negative accepted: {failures!r}")
            return False

        lines = [
            "EVD=doc/receipts/evidence/../../elsewhere",
            "cmd: tool > $EVD/out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"evd dotdot-escape negative accepted: {failures!r}")
            return False

        (evidence / "other.txt").write_text("other\n", encoding="utf-8")
        lines = [
            "EVD=doc/receipts/evidence",
            "cmd: tool > $EVD/other.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"evd wrong-target-under-declared-dir negative accepted: {failures!r}")
            return False
    return True


def wrapper_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-wrapper-") as temp:
        root = Path(temp)
        evidence = root / "evidence"
        evidence.mkdir()
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")

        positives = [
            'cmd.exe /c "tool > out.txt"',
            "cmd /d /s /c 'tool > out.txt'",
            "cmd /s /c \"tool > out.txt\"",
            "cmd.exe /d /c \"tool > out.txt\"",
            "`cmd.exe /c \"tool > out.txt\"`",
            "set FOO=bar&& tool > out.txt",
            '`cmd.exe /d /c "set FOO=bar&& tool > out.txt"`',
            "cmd /d /s /c 'tool > out.txt'; $rc=$LASTEXITCODE; if($rc -ne 0){exit $rc}",
        ]
        for command in positives:
            lines = [f"cmd: {command}", "capture: out.txt", "```text", "ok", "```"]
            _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
            if failures:
                print(f"wrapper positive rejected: {command!r}: {failures!r}")
                return False

        negatives = [
            'cmd.exe /c "tool > other.txt"',            # wrapped payload redirects elsewhere
            'cmd.exe /c "tool > out.txt',                # payload quotes do not close
            "cmd /d /s /c 'tool > out.txt",               # single-quote payload does not close
        ]
        for command in negatives:
            lines = [f"cmd: {command}", "capture: out.txt", "```text", "ok", "```"]
            _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
            if not any("CMD_NO_REDIRECT" in failure for failure in failures):
                print(f"wrapper negative accepted: {command!r}: {failures!r}")
                return False
    return True


def copy_item_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-copyitem-") as temp:
        root = Path(temp)
        evidence = root  # bare Copy-Item source/dest resolve cwd-relative (copy); real
        evidence.mkdir(exist_ok=True)  # shapes always use full paths, never bare ones.
        (evidence / "capture.txt").write_text("ok\n", encoding="utf-8")

        command = "tool > ./tmp.txt; $rc=$LASTEXITCODE; Copy-Item -LiteralPath ./tmp.txt -Destination capture.txt -Force; exit $rc"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"copy positive (redirect+Copy-Item) rejected: {failures!r}")
            return False

        command = (
            "tool *> ./tmp.txt; $rc=$LASTEXITCODE; "
            "Add-Content -LiteralPath ./tmp.txt -Value ('exit='+$rc); "
            "Copy-Item -LiteralPath ./tmp.txt -Destination capture.txt -Force"
        )
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"copy positive (redirect+Add-Content+Copy-Item chain) rejected: {failures!r}")
            return False

        command = "tool > capture.txt; Add-Content -Path capture.txt -Value done"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"copy positive (Add-Content -Path) rejected: {failures!r}")
            return False

        command = "tool > ./tmp2.txt; Copy-Item ./tmp2.txt capture.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"copy positive (positional Copy-Item) rejected: {failures!r}")
            return False

        command = "tool > ./tmp.txt; Copy-Item -LiteralPath ./tmp.txt -Destination other.txt -Force"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"copy negative (destination elsewhere) accepted: {failures!r}")
            return False

        command = "Copy-Item -LiteralPath unrelated-preexisting.txt -Destination capture.txt -Force"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"copy negative (source not produced) accepted: {failures!r}")
            return False

        command = "Copy-Item -LiteralPath ./tmp.txt -Destination capture.txt -Force"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"copy negative (Copy-Item alone) accepted: {failures!r}")
            return False
    return True


def authority_root_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-authority-") as temp:
        root = Path(temp)
        evidence = root / "doc" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        old_root = "C:\\OLD\\authority-checkout"

        target = f"{old_root}\\doc\\receipts\\evidence\\out.txt"
        lines = [
            f"authority_root={old_root}",
            f"cmd: tool > {target}",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"authority positive rejected: {failures!r}")
            return False

        lines = [
            f"authority_root={old_root}",
            "cmd: tool > C:\\SOME\\OTHER\\ROOT\\doc\\receipts\\evidence\\out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"authority negative (unknown other root) accepted: {failures!r}")
            return False

        lines = [
            f"authority_root={old_root}",
            f"cmd: tool > {old_root}\\doc\\receipts\\evidence\\sibling\\out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"authority negative (wrong-neighbor) accepted: {failures!r}")
            return False

        lines = [
            f"authority_root={old_root}",
            f"cmd: tool > {old_root}\\doc\\receipts\\elsewhere\\out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"authority negative (same basename, different path) accepted: {failures!r}")
            return False

        lines = [
            f"authority_root={old_root}",
            f"cmd: tool > {old_root}\\doc\\receipts\\evidence\\..\\..\\escape\\out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"authority negative (.. escape) accepted: {failures!r}")
            return False
    return True


def bounded_base_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-bounded-") as temp:
        root = Path(temp)
        receipt_dir = root / "doc" / "receipts"
        evidence = receipt_dir / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")

        target = "doc/receipts/evidence/out.txt"
        lines = [f"cmd: tool > {target}", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"bounded positive (base 1: scan cwd) rejected: {failures!r}")
            return False

        target = "evidence/out.txt"
        lines = [f"cmd: tool > {target}", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"bounded positive (base 2: receipt directory) rejected: {failures!r}")
            return False

        (evidence / "sub").mkdir()
        (evidence / "sub" / "nested.txt").write_text("ok\n", encoding="utf-8")
        target = "sub/nested.txt"
        lines = [f"cmd: tool > {target}", "capture: sub/nested.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"bounded positive (base 3: evidence root) rejected: {failures!r}")
            return False

        coincide_root = root / "coincide"
        coincide_evidence = coincide_root / "evidence"
        coincide_evidence.mkdir(parents=True)
        (coincide_evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        target = "evidence/out.txt"
        lines = [f"cmd: tool > {target}", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, coincide_evidence, 0, True, command_cwd=coincide_root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"bounded negative (two bases both hit the capture) accepted: {failures!r}")
            return False

        other_root_root = root / "other_root"
        other_root_evidence = other_root_root / "nested" / "evidence"
        other_root_evidence.mkdir(parents=True)
        (other_root_evidence / "sub").mkdir()
        (other_root_evidence / "sub" / "capture.txt").write_text("ok\n", encoding="utf-8")
        (other_root_root / "sub").mkdir()
        (other_root_root / "sub" / "capture.txt").write_text("different\n", encoding="utf-8")
        lines = ["cmd: tool > sub/capture.txt", "capture: sub/capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, other_root_evidence, 0, True, command_cwd=other_root_root)
        if not any("AMBIGUOUS_TARGET" in failure for failure in failures):
            print(f"ambiguous negative (capture hit + other existing file) accepted: {failures!r}")
            return False

        amb_root = root / "amb"
        amb_receipt_dir = amb_root / "doc" / "receipts"
        amb_evidence = amb_receipt_dir / "evidence"
        (amb_evidence / "capture-dir").mkdir(parents=True)
        (amb_evidence / "capture-dir" / "capture.txt").write_text("ok\n", encoding="utf-8")
        (amb_root / "shared").mkdir(parents=True)
        (amb_root / "shared" / "same.txt").write_text("root copy\n", encoding="utf-8")
        (amb_evidence / "shared").mkdir(parents=True)
        (amb_evidence / "shared" / "same.txt").write_text("evidence copy\n", encoding="utf-8")
        lines = ["cmd: tool > shared/same.txt", "capture: capture-dir/capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, amb_evidence, 0, True, command_cwd=amb_root)
        if not any("AMBIGUOUS_TARGET" in failure for failure in failures):
            print(f"bounded negative (ambiguous target) not reported: {failures!r}")
            return False

        lines = ["cmd: tool > ../../escape/out.txt", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"bounded negative (.. escape) accepted: {failures!r}")
            return False

        (evidence / "othersub").mkdir()
        (evidence / "othersub" / "nested.txt").write_text("different\n", encoding="utf-8")
        lines = ["cmd: tool > othersub/nested.txt", "capture: sub/nested.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"bounded negative (same basename, other directory) accepted: {failures!r}")
            return False
    return True


def exit_echo_oracle(module: ModuleType) -> bool:
    positives = [
        "echo exit=$? >> out.txt",
        'Write-Output "exit=$?" >> out.txt',
        'printf "exit=%d" $LASTEXITCODE >> out.txt',
        '"exit=$rc" >> out.txt',
    ]
    for statement in positives:
        tokens = module._shell_tokens(statement)
        if not module._has_exit_output(tokens, statement):
            print(f"exit-echo positive not detected as exit echo: {statement!r}")
            return False

    negatives = [
        "Select-String -Pattern 'exit=' file.txt > out.txt",
        "grep 'exit=' file.txt > out.txt",
        'findstr "exit=" file.txt > out.txt',
        "rg 'exit=' file.txt > out.txt",
        "Get-Content file.txt | Select-String -Pattern '^exit=' *> out.txt",
    ]
    for statement in negatives:
        tokens = module._shell_tokens(statement)
        if module._has_exit_output(tokens, statement):
            print(f"exit-echo negative wrongly detected as exit echo: {statement!r}")
            return False

    with tempfile.TemporaryDirectory(prefix="rf-exit-echo-") as temp:
        evidence = Path(temp)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        lines = [
            "cmd: Get-Content raw.txt | Select-String -Pattern 'foo|^exit=' | ForEach-Object { $_.Line } *> out.txt",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=evidence)
        if failures:
            print(f"exit-echo integration positive rejected: {failures!r}")
            return False

        lines = ["cmd: echo exit=$?", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=evidence)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"exit-echo negative (echo exit= without redirect) accepted: {failures!r}")
            return False
    return True


def authority_root_space_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-space-") as temp:
        root = Path(temp)
        evidence = root / "doc" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        space_root = "C:\\Fake Authority\\project root"

        target = f"{space_root}\\doc\\receipts\\evidence\\out.txt"
        lines = [
            f"authority_root={space_root}",
            f"cmd: tool > {target}",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"root-space positive rejected: {failures!r}")
            return False

        lines = [f"cmd: tool > {target}", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"root-space negative (undeclared space path) accepted: {failures!r}")
            return False

        lines = [
            "authority_root=C:\\Some Other\\root with spaces",
            f"cmd: tool > {target}",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"root-space negative (non-matching declared root) accepted: {failures!r}")
            return False
    return True


def authority_root_inplace_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-inplace ") as temp:
        root = Path(temp)
        if " " not in str(root):
            print(f"inplace-root fixture root has no space: {root!r}")
            return False
        evidence = root / "doc" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        authority_root = str(root)
        target = f"{authority_root}\\doc\\receipts\\evidence\\out.txt"

        lines = [
            f"authority_root={authority_root}",
            f"cmd: tool > {target}",
            "capture: out.txt",
            "```text",
            "ok",
            "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"inplace-root in-place positive rejected: {failures!r}")
            return False

        lines = [f"cmd: tool > {target}", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"inplace-root negative (undeclared root) accepted: {failures!r}")
            return False
    return True


def placeholder_resolution_oracle(module: ModuleType) -> bool:

    def build_case(root: Path) -> tuple[str, list[str]]:
        cap = "sample-14-self-note-delivery-legacy.txt"
        run_file = f"{root}\\docs\\receipts\\evidence\\sample-14-self-note-delivery-legacy-run.txt"
        final_file = f"{root}\\docs\\receipts\\evidence\\{cap}"
        command = (
            "& powershell -NoProfile -ExecutionPolicy Bypass -File "
            f"'{root}\\docs\\receipts\\evidence\\sample-14-materialize-explicit-evidence.ps1' "
            f"-Heading '## delivery-legacy' -RepoRoot '{root}' -SelfNote *> '{run_file}'; "
            "$rc=$LASTEXITCODE; "
            f"\"exit=$rc\" >> '{run_file}'; "
            f"Copy-Item -LiteralPath '{run_file}' -Destination '{final_file}' -Force"
        )
        lines = [
            f"authority_root={root}",
            f"cmd: `{command}`",
            f"capture: {cap}",
            "```text",
            "evidence_root=C:\\Temp\\sample-14-explicit-evidence-delivery-legacy",
            "fences=23 (excluding this run's own capture fence) failures=0",
            "exit=0",
            "```",
        ]
        return cap, lines

    with tempfile.TemporaryDirectory(prefix="rf-inplace ") as temp:
        root = Path(temp)
        if " " not in str(root):
            print(f"placeholder in-place fixture root has no space: {root!r}")
            return False
        evidence = root / "docs" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        cap, lines = build_case(root)
        (evidence / cap).write_text(
            "evidence_root=C:\\Temp\\sample-14-explicit-evidence-delivery-legacy\n"
            "fences=23 (excluding this run's own capture fence) failures=0\nexit=0\n",
            encoding="utf-8",
        )
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"placeholder in-place positive rejected: {failures!r}")
            return False

    with tempfile.TemporaryDirectory(prefix="rf-declared ") as declared_temp, \
            tempfile.TemporaryDirectory(prefix="rf-clone-") as clone_temp:
        declared_root = Path(declared_temp)
        clone_root = Path(clone_temp)
        if " " not in str(declared_root):
            print(f"placeholder declared-root fixture has no space: {declared_root!r}")
            return False
        evidence = clone_root / "docs" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        cap, lines = build_case(declared_root)
        (evidence / cap).write_text(
            "evidence_root=C:\\Temp\\sample-14-explicit-evidence-delivery-legacy\n"
            "fences=23 (excluding this run's own capture fence) failures=0\nexit=0\n",
            encoding="utf-8",
        )
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=clone_root)
        if failures:
            print(f"placeholder clone (scan root != declared root) positive rejected: {failures!r}")
            return False
    return True


def filter_chain_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-filter-") as temp:
        root = Path(temp)
        evidence = root  # bare chain filenames resolve cwd-relative; real shapes
        evidence.mkdir(exist_ok=True)  # always use full paths, never bare ones.
        (evidence / "capture.txt").write_text("ok\n", encoding="utf-8")

        command = (
            "tool > ./tmp.txt 2>&1; echo exit=$? >> ./tmp.txt; tail -25 ./tmp.txt > capture.txt"
        )
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"filter positive (tail chain) rejected: {failures!r}")
            return False

        command = (
            "tool *> ./tmp.txt; $rc=$LASTEXITCODE; Add-Content -LiteralPath ./tmp.txt -Value ('exit='+$rc); "
            "Get-Content -LiteralPath ./tmp.txt | Select-String -Pattern '^exit=' | ForEach-Object { $_.Line } *> capture.txt"
        )
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"filter positive (Get-Content | Select-String chain) rejected: {failures!r}")
            return False

        command = "cat unrelated-preexisting.txt > mid.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"filter negative (filter reads unproduced file) accepted: {failures!r}")
            return False

        command = "tool > ./tmp.txt 2>&1; echo exit=$? >> ./tmp.txt; tail -25 ./tmp.txt > other.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"filter negative (chain ends elsewhere) accepted: {failures!r}")
            return False

        command = "tool > ./tmp.txt 2>&1; echo exit=$? >> other.txt; tail -25 ./tmp.txt > capture.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"filter negative (exit append outside chain) accepted: {failures!r}")
            return False

        command = "tool > ./tmp.txt 2>&1; echo exit=$? >> ./tmp.txt; othertool > ./tmp.txt; tail -25 ./tmp.txt > capture.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"filter negative (chain member overwritten) accepted: {failures!r}")
            return False
    return True


def loop_redirect_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-loop-") as temp:
        root = Path(temp)
        evidence = root
        evidence.mkdir(exist_ok=True)
        (evidence / "capture.txt").write_text("ok\n", encoding="utf-8")

        command = 'for f in a b c; do py -3 "$f" > /dev/null 2>&1; echo exit=$?; done > capture.txt 2>&1'
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"loop positive (loop redirect) rejected: {failures!r}")
            return False

        command = 'for f in a b c; do py -3 "$f" > /dev/null 2>&1; echo exit=$? >> other.txt; done > capture.txt 2>&1'
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"loop negative (echo has its own wrong redirect) accepted: {failures!r}")
            return False

        command = 'for f in a b c; do py -3 "$f"; echo exit=$?; done'
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"loop negative (no loop redirect at all) accepted: {failures!r}")
            return False
    return True


def chain_overwrite_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-overwrite-") as temp:
        root = Path(temp)
        evidence = root
        evidence.mkdir(exist_ok=True)
        (evidence / "capture.txt").write_text("ok\n", encoding="utf-8")
        (evidence / "unrelated.txt").write_text("noise\n", encoding="utf-8")

        command = (
            'tool *> ./tmp.txt; $rc=$LASTEXITCODE; "exit=$rc" >> ./tmp.txt; '
            "tail unrelated.txt > ./tmp.txt; tail ./tmp.txt > capture.txt"
        )
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"overwrite negative (filter overwrites produced path) accepted: {failures!r}")
            return False

        command = (
            'tool *> ./tmp2.txt; $rc=$LASTEXITCODE; "exit=$rc" >> ./tmp2.txt; '
            "Copy-Item -LiteralPath unrelated.txt -Destination ./tmp2.txt -Force; "
            "tail ./tmp2.txt > capture.txt"
        )
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"overwrite negative (Copy-Item overwrites produced path) accepted: {failures!r}")
            return False

        command = 'tool *> ./tmp3.txt; $rc=$LASTEXITCODE; "exit=$rc" >> ./tmp3.txt; tail ./tmp3.txt > capture.txt'
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"overwrite positive (no overwrite, ordinary chain) rejected: {failures!r}")
            return False
    return True


def joined_exit_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-joined-") as temp:
        root = Path(temp)
        evidence = root
        evidence.mkdir(exist_ok=True)
        (evidence / "capture.txt").write_text("ok\n", encoding="utf-8")

        command = "tool > capture.txt && echo exit=$? >> other.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"joined negative (&& joined exit to wrong file) accepted: {failures!r}")
            return False

        command = "tool > capture.txt || echo exit=$? >> other2.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"joined negative (|| joined exit to wrong file) accepted: {failures!r}")
            return False

        command = "tool *> capture.txt && echo exit=$? >> capture.txt"
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"joined positive (&& joined exit correctly to capture) rejected: {failures!r}")
            return False
    return True


def evd_dotdot_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-evddotdot-") as temp:
        root = Path(temp)
        evidence = root / "doc" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")

        lines = [
            "EVD=doc/receipts/evidence",
            "cmd: tool > $EVD/../evidence/out.txt",
            "capture: out.txt",
            "```text", "ok", "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"evd-dotdot negative ($EVD/../evidence/out.txt) accepted: {failures!r}")
            return False

        lines = [
            "EVD=doc/receipts/evidence",
            "cmd: tool > $EVD/out.txt",
            "capture: out.txt",
            "```text", "ok", "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"evd-dotdot positive ($EVD/out.txt) rejected: {failures!r}")
            return False
    return True


def placeholder_declaration_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-placeholder-") as temp:
        root = Path(temp)
        evidence = root / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        literal_placeholder = "Z:\\__RF_AUTHORITY_ROOT_PLACEHOLDER__"

        target = f"{literal_placeholder}\\evidence\\out.txt"
        lines = [f"cmd: tool > '{target}'", "capture: out.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"placeholder-decl negative (undeclared placeholder literal) accepted: {failures!r}")
            return False

        authority_root = str(root)
        target2 = f"{authority_root}\\evidence\\out.txt"
        lines = [
            f"authority_root={authority_root}",
            f"cmd: tool > '{target2}'",
            "capture: out.txt",
            "```text", "ok", "```",
        ]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"placeholder-decl positive (declared authority_root) rejected: {failures!r}")
            return False
    return True


def late_exit_append_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-late-") as temp:
        root = Path(temp)
        evidence = root
        evidence.mkdir(exist_ok=True)
        (evidence / "capture.txt").write_text("ok\n", encoding="utf-8")

        command = 'tool *> ./tmp.txt; tail ./tmp.txt > capture.txt; $rc=$LASTEXITCODE; "exit=$rc" >> ./tmp.txt'
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if not any("CMD_NO_REDIRECT" in failure for failure in failures):
            print(f"late-append negative (exit appended after filter read) accepted: {failures!r}")
            return False

        command = 'tool *> ./tmp2.txt; $rc=$LASTEXITCODE; "exit=$rc" >> ./tmp2.txt; tail ./tmp2.txt > capture.txt'
        lines = [f"cmd: {command}", "capture: capture.txt", "```text", "ok", "```"]
        _, failures = module.check_section(lines, evidence, 0, True, command_cwd=root)
        if failures:
            print(f"late-append positive (exit appended before filter read) rejected: {failures!r}")
            return False
    return True


def legacy_unclaimed_exit_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-legacy-") as temp:
        root = Path(temp)
        evidence = root / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("exit=0\n", encoding="utf-8")
        receipt = root / "receipt.md"
        receipt.write_text(
            "## delivery\ncmd: bash assemble.sh > out.txt 2>&1\ncapture: out.txt\n```text\nexit=0\n```\n",
            encoding="utf-8",
        )
        lines = ["cmd: bash assemble.sh > out.txt 2>&1", "capture: out.txt", "```text", "exit=0", "```"]

        counter = [0]
        _, failures = module.check_section(
            lines, evidence, 0, True, command_cwd=root,
            legacy_counter=counter, legacy_receipt_path=str(receipt), legacy_heading="## delivery",
        )
        if not any("LEGACY_UNCLAIMED_EXIT" in failure for failure in failures) or counter[0] != 1:
            print(f"legacy negative (no allowlist) accepted: failures={failures!r} counter={counter}")
            return False

        allowed = {(str(receipt), "## delivery", "out.txt")}
        counter2 = [0]
        _, failures2 = module.check_section(
            lines, evidence, 0, True, command_cwd=root,
            legacy_allowlist=allowed, legacy_counter=counter2,
            legacy_receipt_path=str(receipt), legacy_heading="## delivery",
        )
        if failures2 or counter2[0] != 1:
            print(f"legacy positive (allowlisted) rejected: failures={failures2!r} counter={counter2}")
            return False

        (evidence / "ordinary.txt").write_text("exit=0\n", encoding="utf-8")
        ordinary_lines = [
            "cmd: tool > ordinary.txt; echo exit=$? >> ordinary.txt",
            "capture: ordinary.txt", "```text", "exit=0", "```",
        ]
        counter3 = [0]
        _, failures3 = module.check_section(
            ordinary_lines, evidence, 0, True, command_cwd=root,
            legacy_counter=counter3, legacy_receipt_path=str(receipt), legacy_heading="## delivery",
        )
        if failures3 or counter3[0] != 0:
            print(f"legacy negative control (ordinary exit echo) miscounted: failures={failures3!r} counter={counter3}")
            return False
    return True


def target_normalization_oracle(module: ModuleType) -> bool:
    raw_relative = (
        r"docs\receipts\evidence\repair"
        r"\sample-11\readback\sample-11-readback-x.txt"
    )
    expected = (
        "docs/receipts/evidence/repair"
        "/sample-11/readback/sample-11-readback-x.txt"
    )
    if posixpath.normpath(raw_relative) == posixpath.normpath(expected):
        print("normalize oracle: raw backslash target was unexpectedly already posix-equal")
        return False
    normalized = module._normalize_target(raw_relative)
    if posixpath.normpath(normalized) != posixpath.normpath(expected):
        print(f"normalize oracle: normalized relative target mismatched the posix oracle: {normalized!r}")
        return False

    raw_absolute = "C:\\Users\\someone\\Desktop\\project root\\docs\\x\\y.txt"
    if posixpath.isabs(raw_absolute) or posixpath.isabs(module._normalize_target(raw_absolute)):
        print("normalize oracle: posixpath.isabs unexpectedly recognised a drive letter")
        return False
    if not module._target_is_absolute(raw_absolute):
        print("normalize oracle: _target_is_absolute rejected the raw drive-letter form")
        return False
    if not module._target_is_absolute(module._normalize_target(raw_absolute)):
        print("normalize oracle: _target_is_absolute rejected the normalized drive-letter form")
        return False

    already_posix = "receipt-repair/sample-11/out.txt"
    if module._normalize_target(already_posix) != already_posix:
        print("normalize oracle: an already-POSIX-style target was altered")
        return False
    if module._target_is_absolute(already_posix):
        print("normalize oracle: a relative POSIX-style target was reported absolute")
        return False
    return True


def elision_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-oracle-") as temp:
        evidence = Path(temp) / "evidence"
        evidence.mkdir()
        for index, marker in enumerate(EXPECTED_ELISIONS):
            capture = f"elision-{index}.txt"
            body = marker
            path = evidence / capture
            path.write_text(body + "\n", encoding="utf-8")
            lines = [f"cmd: tool > {capture}", f"capture: {capture}", "```text", body, "```"]
            fences, positive_failures = module.check_section(lines, evidence, 0)
            if fences != 1 or positive_failures:
                return False

            path.write_text("ordinary content\n", encoding="utf-8")
            fences, negative_failures = module.check_section(lines, evidence, 0)
            if fences != 1 or not any(
                "ELISION_MISSING" in failure and repr(marker) in failure
                for failure in negative_failures
            ):
                return False
    return True


def scan_ambiguity_oracle(module: ModuleType) -> bool:
    with tempfile.TemporaryDirectory(prefix="rf-oracle-") as temp:
        root = Path(temp) / "tree"
        ev = root / "r" / "evidence"
        (ev / "a").mkdir(parents=True)
        (ev / "b").mkdir()
        (ev / "a" / "same.txt").write_text("x", encoding="utf-8")
        (ev / "b" / "same.txt").write_text("x", encoding="utf-8")
        (root / "r" / "receipt.md").write_text(
            "## current\ncapture: same.txt\n```text\nx\n```\n", encoding="utf-8"
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.scan(root)
        return result == 1 and "FAIL SCAN_CAPTURE_AMBIGUOUS" in output.getvalue()






class ExitCodeContractTests(unittest.TestCase):
    """0 pass, 1 contract red, 2 evidence root unreadable, 3 usage error, through main()."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rf-exit-")
        self.root = Path(self.tmp.name)
        self.ev = self.root / "evidence"
        self.ev.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def build_receipt(self, captures: dict[str, str], bodies: dict[str, str] | None = None) -> Path:
        """Write one section with one fence per capture; returns the receipt path."""
        shown = captures if bodies is None else bodies
        parts = ["## delivery"]
        for name, content in captures.items():
            (self.ev / name).write_text(content, encoding="utf-8", newline="\n")
            parts += [f"cmd: tool > {name} 2>&1", f"capture: {name}", "```text", shown[name].rstrip("\n"), "```"]
        receipt = self.root / "receipt.md"
        receipt.write_text("\n".join(parts) + "\n", encoding="utf-8")
        return receipt

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rf.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_exit_0_and_fence_count_derive_from_the_fixture(self) -> None:
        captures = {f"cap-{index}.txt": f"line {index}\n" for index in range(4)}
        receipt = self.build_receipt(captures)
        code, out, _ = self.run_main([str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(code, 0)
        self.assertTrue(out.endswith(f"fences={len(captures)} failures=0\n"), out)

    def test_exit_1_when_a_fence_body_differs_from_its_capture(self) -> None:
        captures = {"a.txt": "actual\n", "b.txt": "same\n"}
        receipt = self.build_receipt(captures, bodies={"a.txt": "edited\n", "b.txt": "same\n"})
        code, out, _ = self.run_main([str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(code, 1)
        mismatched = [name for name in captures if captures[name] != {"a.txt": "edited\n", "b.txt": "same\n"}[name]]
        self.assertEqual(out.count("FAIL BODY_MISMATCH"), len(mismatched))
        self.assertTrue(out.endswith(f"failures={len(mismatched)}\n"), out)

    def test_exit_2_when_the_evidence_root_is_not_a_readable_directory(self) -> None:
        receipt = self.build_receipt({"a.txt": "x\n"})
        missing = self.root / "no-such-evidence-dir"
        code, out, _ = self.run_main([str(receipt), "## delivery", str(missing)])
        self.assertEqual(code, 2)
        self.assertIn("EVIDENCE_ROOT_UNREADABLE", out)
        not_a_dir = self.root / "plain-file"
        not_a_dir.write_text("x", encoding="utf-8")
        code, out, _ = self.run_main([str(receipt), "## delivery", str(not_a_dir)])
        self.assertEqual(code, 2)
        code, out, _ = self.run_main(["--scan", str(missing)])
        self.assertEqual(code, 2)
        self.assertIn("SCAN_ROOT_UNREADABLE", out)

    def test_an_unexpected_error_exits_2_never_1(self) -> None:
        receipt = self.build_receipt({"a.txt": "x\n"})
        with mock.patch.object(rf, "explicit", side_effect=RuntimeError("boom")):
            code, out, err = self.run_main([str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(code, 2, out + err)
        self.assertIn("tool fault", err)
        self.assertIn("boom", err)

    def test_a_scan_entry_that_cannot_be_read_exits_2_never_1(self) -> None:
        scan_root = self.root / "scan"
        (scan_root / "broken.md").mkdir(parents=True)
        code, out, err = self.run_main(["--scan", str(scan_root)])
        self.assertEqual(code, 2, out + err)
        self.assertIn("tool fault", err)

    def test_exit_3_prints_one_line_of_usage_for_every_usage_error(self) -> None:
        receipt = self.build_receipt({"a.txt": "x\n"})
        cases = {
            "no arguments": [],
            "too few positionals": [str(receipt), "## delivery"],
            "unknown option": [str(receipt), "## delivery", str(self.ev), "--no-such-option"],
        }
        for label, argv in cases.items():
            with self.subTest(label):
                code, _, err = self.run_main(argv)
                self.assertEqual(code, 3)
                usage_lines = [line for line in err.splitlines() if line.startswith("usage:")]
                self.assertEqual(len(usage_lines), 1, err)
        code, _, err = self.run_main([])
        self.assertEqual(len(err.strip().splitlines()), 1, err)

    def test_exit_3_for_a_heading_that_names_no_section_and_for_a_missing_receipt(self) -> None:
        receipt = self.build_receipt({"a.txt": "x\n"})
        code, out, _ = self.run_main([str(receipt), "## no such heading", str(self.ev)])
        self.assertEqual(code, 3)
        self.assertIn("section heading not found", out)
        code, out, _ = self.run_main([str(self.root / "absent.md"), "## delivery", str(self.ev)])
        self.assertEqual(code, 3)

    def test_exit_3_for_an_unreadable_allowlist_file(self) -> None:
        receipt = self.build_receipt({"a.txt": "x\n"})
        code, _, err = self.run_main(
            [str(receipt), "## delivery", str(self.ev), "--legacy-allowlist", str(self.root / "absent.tsv")]
        )
        self.assertEqual(code, 3)
        self.assertIn("usage:", err)

    def test_authority_root_option_maps_a_foreign_absolute_prefix(self) -> None:
        repo = self.root / "repo"
        evidence = repo / "docs" / "receipts" / "evidence"
        evidence.mkdir(parents=True)
        (evidence / "out.txt").write_text("ok\n", encoding="utf-8")
        foreign = "D:/elsewhere/checkout"
        receipt = repo / "docs" / "receipts" / "receipt.md"
        receipt.write_text(
            f"## delivery\ncmd: tool > {foreign}/docs/receipts/evidence/out.txt 2>&1\ncapture: out.txt\n```text\nok\n```\n",
            encoding="utf-8",
        )
        previous = Path.cwd()
        try:
            os.chdir(repo)
            without_option, _, _ = self.run_main([str(receipt), "## delivery", str(evidence)])
            with_option, out, _ = self.run_main(
                [str(receipt), "## delivery", str(evidence), "--authority-root", foreign]
            )
            scan_with_option, _, _ = self.run_main(["--scan", str(repo), "--authority-root", foreign])
            scan_without_option, _, _ = self.run_main(["--scan", str(repo)])
        finally:
            os.chdir(previous)
        self.assertEqual(without_option, 1)
        self.assertEqual(with_option, 0, out)
        self.assertEqual(scan_with_option, 0)
        self.assertEqual(scan_without_option, 1)

    def test_legacy_allowlist_file_admits_exactly_the_listed_row(self) -> None:
        (self.ev / "legacy.txt").write_text("done\nexit=0\n", encoding="utf-8", newline="\n")
        receipt = self.root / "receipt.md"
        receipt.write_text(
            "## delivery\ncmd: tool > legacy.txt 2>&1\ncapture: legacy.txt\n```text\ndone\nexit=0\n```\n",
            encoding="utf-8",
        )
        argv = [str(receipt), "## delivery", str(self.ev)]
        code, out, _ = self.run_main(argv)
        self.assertEqual(code, 1)
        self.assertIn("LEGACY_UNCLAIMED_EXIT", out)
        allowlist = self.root / "allow.tsv"
        allowlist.write_text(
            "# receipt\theading\tcapture\n" + "\t".join([receipt.as_posix(), "## delivery", "legacy.txt"]) + "\n",
            encoding="utf-8",
        )
        code, out, _ = self.run_main(argv + ["--legacy-allowlist", str(allowlist)])
        self.assertEqual(code, 0, out)
        self.assertIn("legacy_unclaimed_exit=1", out)
        allowlist.write_text("\t".join([receipt.as_posix(), "## delivery", "other.txt"]) + "\n", encoding="utf-8")
        code, _, _ = self.run_main(argv + ["--legacy-allowlist", str(allowlist)])
        self.assertEqual(code, 1)

    def test_a_red_with_a_non_cp950_capture_name_exits_1_under_a_cp950_console(self) -> None:
        """The console encoding never changes an exit code (R4-2): a red stays 1, with no traceback."""
        with self.assertRaises(UnicodeEncodeError):
            NON_CP950.encode("cp950")
        env = {key: value for key, value in os.environ.items() if key not in ("PYTHONUTF8", "PYTHONIOENCODING")}
        env["PYTHONIOENCODING"] = "cp950"
        name = f"cap-{NON_CP950}.txt"
        receipt = self.root / "receipt.md"
        receipt.write_text(
            f"## delivery\ncmd: tool > {name} 2>&1\ncapture: {name}\n```text\nok\n```\n", encoding="utf-8",
        )
        done = subprocess.run(
            [sys.executable, str(SCRIPT), str(receipt), "## delivery", str(self.ev)], capture_output=True, env=env,
        )
        out, err = done.stdout.decode("cp950"), done.stderr.decode("cp950", errors="replace")
        self.assertEqual(done.returncode, 1, out + err)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("tool fault", err)
        self.assertIn("CAPTURE_MISSING", out)
        self.assertIn(NON_CP950.encode("unicode_escape").decode("ascii"), out)


class RunThatCheckedNothingTests(unittest.TestCase):
    """Ticket 58 / ticket 48 F-06: a run that checked nothing never exits 0; `--help` and the unused option exit 3."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rf-nothing-")
        self.root = Path(self.tmp.name)
        self.ev = self.root / "evidence"
        self.ev.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rf.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_a_section_with_zero_fences_is_exit_1_with_a_named_code(self) -> None:
        receipt = self.root / "receipt.md"
        receipt.write_text("## delivery\nprose only, no fenced block\n", encoding="utf-8")
        code, out, err = self.run_main([str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(code, 1, out + err)
        self.assertIn("FAIL NO_FENCES", out)
        self.assertTrue(out.endswith("fences=0 failures=1\n"), out)

    def test_a_heading_with_a_fence_is_not_no_fences(self) -> None:
        (self.ev / "out.txt").write_text("ok\n", encoding="utf-8")
        receipt = self.root / "receipt.md"
        receipt.write_text("## delivery\ncmd: tool > out.txt 2>&1; echo exit=0 >> out.txt\ncapture: out.txt\n```text\nok\n```\n", encoding="utf-8")
        code, out, _ = self.run_main([str(receipt), "## delivery", str(self.ev)])
        self.assertEqual(code, 0, out)
        self.assertNotIn("NO_FENCES", out)

    def test_the_name_of_a_section_is_printed_on_one_line(self) -> None:
        receipt = self.root / "receipt.md"
        receipt.write_text("## a\nno fences\n", encoding="utf-8")
        code, out, _ = self.run_main([str(receipt), "## a b\x1b[0m", str(self.ev)])
        self.assertEqual(code, 3)
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertIn("\\u2028", out)
        self.assertIn("\\x1b", out)

    def test_scan_of_a_directory_with_no_receipt_is_exit_1_with_a_named_code(self) -> None:
        empty = self.root / "empty-scan"
        empty.mkdir()
        (empty / "notes.txt").write_text("not a receipt", encoding="utf-8")
        code, out, err = self.run_main(["--scan", str(empty)])
        self.assertEqual(code, 1, out + err)
        self.assertIn("FAIL SCAN_NO_RECEIPTS", out)
        self.assertIn("receipts=0", out)

    def test_scan_of_receipts_with_no_checked_section_is_exit_1_with_a_named_code(self) -> None:
        tree = self.root / "idle-scan"
        tree.mkdir()
        (tree / "receipt.md").write_text("## summary\nno capture line and no fence here\n", encoding="utf-8")
        code, out, err = self.run_main(["--scan", str(tree)])
        self.assertEqual(code, 1, out + err)
        self.assertIn("FAIL SCAN_NOTHING_CHECKED", out)
        self.assertIn("skipped=1", out)

    def test_scan_of_a_section_with_a_capture_line_and_no_fence_is_red(self) -> None:
        tree = self.root / "capture-scan"
        (tree / "evidence").mkdir(parents=True)
        (tree / "evidence" / "out.txt").write_text("ok\n", encoding="utf-8")
        (tree / "receipt.md").write_text("## delivery\ncmd: tool > out.txt\ncapture: out.txt\nno fence follows\n", encoding="utf-8")
        code, out, err = self.run_main(["--scan", str(tree)])
        self.assertEqual(code, 1, out + err)
        self.assertIn("NO_FENCES", out)

    def test_scan_that_checked_something_still_exits_0(self) -> None:
        tree = self.root / "checked-scan"
        (tree / "evidence").mkdir(parents=True)
        (tree / "evidence" / "out.txt").write_text("ok\n", encoding="utf-8")
        (tree / "receipt.md").write_text("## delivery\ncmd: tool > out.txt\ncapture: out.txt\n```text\nok\n```\n", encoding="utf-8")
        code, out, err = self.run_main(["--scan", str(tree)])
        self.assertEqual(code, 0, out + err)

    def test_help_exits_3_like_the_other_gate_scripts(self) -> None:
        for flag in ("--help", "-h"):
            with self.subTest(flag):
                code, out, err = self.run_main([flag])
                self.assertEqual(code, 3, out + err)
                self.assertEqual(len([line for line in err.splitlines() if line.startswith("usage:")]), 1, err)

    def test_extra_positional_arguments_to_scan_are_exit_3(self) -> None:
        tree = self.root / "scan-extra"
        tree.mkdir()
        code, out, err = self.run_main(["--scan", str(tree), "stray-argument"])
        self.assertEqual(code, 3, out + err)
        self.assertIn("stray-argument", err)
        self.assertEqual(out, "")

    def test_require_cmd_is_removed_and_giving_it_is_exit_3(self) -> None:
        receipt = self.root / "receipt.md"
        receipt.write_text("## delivery\n```text\nx\n```\n", encoding="utf-8")
        code, out, err = self.run_main([str(receipt), "## delivery", str(self.ev), "--require-cmd"])
        self.assertEqual(code, 3, out + err)
        code, out, err = self.run_main(["--scan", str(self.root), "--require-cmd"])
        self.assertEqual(code, 3, out + err)

    def test_the_subprocess_exit_codes_agree_with_main(self) -> None:
        for argv, expected in ((["--help"], 3), (["--scan", str(self.root / "no-such-dir")], 2)):
            with self.subTest(argv):
                done = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True)
                self.assertEqual(done.returncode, expected, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
