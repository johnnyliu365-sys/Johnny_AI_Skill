"""Behavioural tests for the evidence gate script (exit codes 0/1/2/3).

Every case builds its receipt, captures and a throwaway git repository in temporary
directories; every expected digest, sha and exit list is derived from those fixtures.
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
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import evidence_gate  # noqa: E402

SCRIPT = _SCRIPTS / "evidence_gate.py"
FENCE = "`" * 4
TOOL_PATH = "tools/probe.py"
OTHER_TOOL_PATH = "tools/second.py"
TOOL_BODY = b"print('probe')\n"
OTHER_TOOL_BODY = b"print('second')\n"
NON_CP950 = chr(0x0E01)  # outside code page 950


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr}")
    return done.stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class CellSpec:
    """One run cell; every field can be altered to build one defect at a time."""

    name: str
    candidate: str
    capture_file: str
    capture_text: str
    exit_value: str
    digests: list[str]
    label: bool = True
    candidate_line: bool = True
    capture_line: bool = True
    exit_line: bool = True
    fence: bool = True
    block_text: str | None = None  # defaults to the capture text
    heading: str | None = None

    def render(self) -> str:
        lines = [f"## {self.heading or self.name}", f"cell: {self.name}"]
        if self.candidate_line:
            lines.append(f"candidate: {self.candidate}")
        if self.label:
            lines.append("tool_digest:")
            lines.extend(f"- {entry}" for entry in self.digests)
        if self.capture_line:
            lines.append(f"capture: {self.capture_file}")
        if self.exit_line:
            lines.append(f"exit: {self.exit_value}")
        if self.fence:
            block = self.capture_text if self.block_text is None else self.block_text
            lines.append("")
            lines.append(FENCE)
            if block:
                lines.extend(block[:-1].split("\n") if block.endswith("\n") else block.split("\n"))
            lines.append(FENCE)
        return "\n".join(lines) + "\n"


@dataclass
class Fixture:
    """A temporary repository, an evidence directory and a good receipt of two cells and a statement."""

    tmp: tempfile.TemporaryDirectory[str] = field(default_factory=lambda: tempfile.TemporaryDirectory(prefix="evgate-"))

    def __post_init__(self) -> None:
        self.base = Path(self.tmp.name)
        self.repo = self.base / "repo"
        self.evidence = self.base / "evidence"
        self.repo.mkdir()
        self.evidence.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        self.write_tool(TOOL_PATH, TOOL_BODY)
        self.write_tool(OTHER_TOOL_PATH, OTHER_TOOL_BODY)
        self.candidate = self.commit("tools")
        self.receipt = self.base / "RETURN.md"

    def close(self) -> None:
        self.tmp.cleanup()

    def write_tool(self, path: str, body: bytes) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)

    def commit(self, message: str) -> str:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", message)
        return git(self.repo, "rev-parse", "HEAD").strip()

    def put_capture(self, name: str, text: str) -> str:
        target = self.evidence / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
        return name

    def good_digests(self) -> list[str]:
        return [f"{TOOL_PATH}={sha256(TOOL_BODY)}"]

    def cell(self, name: str, capture_text: str | None = None, exit_value: str | None = None, **overrides: object) -> CellSpec:
        text = capture_text if capture_text is not None else f"{name} ran\nexit=0\n"
        file = f"{name}.txt"
        self.put_capture(file, text)
        spec = CellSpec(
            name=name, candidate=self.candidate, capture_file=file, capture_text=text,
            exit_value=exit_value if exit_value is not None else "0", digests=self.good_digests(),
        )
        for key, value in overrides.items():
            setattr(spec, key, value)
        return spec

    def statement(self, heading: str = "Statement") -> str:
        return f"## {heading}\ncell: STATEMENT\n\nChanged assertions: none.\n"

    def write_receipt(self, *parts: str, newline: str = "\n") -> Path:
        text = "# receipt\n\n" + "\n".join(parts)
        self.receipt.write_bytes(text.replace("\n", newline).encode("utf-8"))
        return self.receipt

    def good_parts(self) -> list[str]:
        return [self.statement(), self.cell("A").render(), self.cell("B", "b out\nexit=0\n").render()]

    def run(
        self,
        extra: Sequence[str] = (),
        tools: Sequence[str] | None = None,
        candidate: str | None = None,
        repo: Path | None = None,
        receipt: Path | None = None,
        evidence: Path | None = None,
        use_root: bool = True,
    ) -> tuple[int, str, str]:
        argv = [str(receipt or self.receipt), "--repo", str(repo or self.repo), "--candidate", candidate or self.candidate]
        for tool in tools if tools is not None else [TOOL_PATH]:
            argv += ["--tool", tool]
        if use_root:  # without it the evidence root defaults to the receipt directory
            argv += ["--evidence-root", str(evidence or self.evidence)]
        argv += list(extra)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = evidence_gate.main(argv)
        return code, out.getvalue(), err.getvalue()

    def codes(self, output: str) -> list[str]:
        return [line.split(" ", 1)[0] for line in output.splitlines() if line and not line.startswith("cells=")]


class GateTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()
        self.addCleanup(self.fx.close)

    def red(self, *parts: str, extra: Sequence[str] = (), tools: Sequence[str] | None = None) -> list[str]:
        self.fx.write_receipt(*parts)
        code, out, err = self.fx.run(extra, tools=tools)
        self.assertEqual(code, 1, out + err)
        self.assertEqual(err, "")
        return self.fx.codes(out)


class NormalBehaviourTests(GateTestCase):
    def test_good_receipt_passes_with_the_cell_count(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        code, out, err = self.fx.run(["--require-cell", "A", "--require-cell", "B"])
        self.assertEqual((code, out, err), (0, "cells=2 defects=0\n", ""))

    def test_crlf_receipt_is_read_but_captures_are_not_normalised(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts(), newline="\r\n")
        code, out, _ = self.fx.run()
        self.assertEqual((code, out), (0, "cells=2 defects=0\n"))

    def test_evidence_root_defaults_to_the_receipt_directory(self) -> None:
        spec = self.fx.cell("A")
        (self.fx.base / "A.txt").write_bytes((self.fx.evidence / "A.txt").read_bytes())
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run(use_root=False)
        self.assertEqual((code, out), (0, "cells=1 defects=0\n"))

    def test_zero_byte_capture_with_an_empty_block_has_no_block_defect(self) -> None:
        spec = self.fx.cell("A", "", exit_value="0")
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run()
        self.assertEqual((code, self.fx.codes(out)), (1, ["EXIT_MISMATCH"]))  # only the exit list disagrees

    def test_capture_of_a_single_blank_line_needs_a_block_of_one_blank_line(self) -> None:
        spec = self.fx.cell("A", "\nexit=0\n")
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)
        spec.block_text = "exit=0\n"
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.codes(self.fx.run()[1]), ["BLOCK_MISMATCH"])

    def test_exit_list_may_hold_spaces_and_several_codes_in_order(self) -> None:
        spec = self.fx.cell("A", "one\nexit=1\ntwo\nexit=0\nexit=2\n", exit_value="1, 0, 2")
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)

    def test_heading_text_inside_the_fence_does_not_open_a_section(self) -> None:
        spec = self.fx.cell("A", "## not a section\ncell: nothing\nexit=0\n")
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run()
        self.assertEqual((code, out), (0, "cells=1 defects=0\n"))


class DefectCodeTests(GateTestCase):
    def test_no_cells_empty_receipt(self) -> None:
        self.fx.receipt.write_bytes(b"")
        code, out, _ = self.fx.run()
        self.assertEqual((code, self.fx.codes(out)), (1, ["NO_CELLS"]))
        self.assertTrue(out.endswith("cells=0 defects=1\n"))

    def test_no_cells_statement_only(self) -> None:
        self.assertEqual(self.red(self.fx.statement()), ["NO_CELLS"])

    def test_not_run_section_without_cell_line(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A").render(), "## Notes\nsome words\n"), ["NOT_RUN"])

    def test_not_run_section_with_empty_cell_value(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A").render(), "## Odd\ncell:\n"), ["NOT_RUN"])

    def test_not_run_required_cell_absent(self) -> None:
        self.assertEqual(self.red(*self.fx.good_parts(), extra=["--require-cell", "Z"]), ["NOT_RUN"])

    def test_cell_field_missing_each_field(self) -> None:
        for override, expected in (
            ({"candidate_line": False}, "candidate"),
            ({"label": False}, "tool_digest:"),
            ({"capture_line": False}, "capture"),
            ({"exit_line": False}, "exit"),
        ):
            with self.subTest(expected=expected):
                spec = self.fx.cell("A", **override)
                self.fx.write_receipt(spec.render())
                code, out, _ = self.fx.run()
                self.assertEqual(code, 1)
                self.assertIn(f"CELL_FIELD_MISSING A: {expected}\n", out)

    def test_statement_has_run_fields_capture_exit_and_fence(self) -> None:
        self.fx.put_capture("S.txt", "x\n")
        for body in ("capture: S.txt\n", "exit: 0\n", f"\n{FENCE}\nx\n{FENCE}\n"):
            with self.subTest(body=body):
                statement = "## Statement\ncell: STATEMENT\n" + body
                self.assertEqual(self.red(self.fx.cell("A").render(), statement), ["STATEMENT_HAS_RUN_FIELDS"])

    def test_statement_uses_a_required_cell_name(self) -> None:
        codes = self.red(self.fx.cell("A").render(), self.fx.statement("F1"), extra=["--require-cell", "F1"])
        self.assertEqual(codes, ["STATEMENT_HAS_RUN_FIELDS", "NOT_RUN"])

    def test_duplicate_cell(self) -> None:
        first = self.fx.cell("A")
        second = self.fx.cell("A", heading="A again")
        self.assertEqual(self.red(first.render(), second.render()), ["DUPLICATE_CELL"])

    def test_candidate_mismatch(self) -> None:
        other = "1" * 40
        self.assertEqual(self.red(self.fx.cell("A", candidate=other).render()), ["CANDIDATE_MISMATCH"])

    def test_tool_digest_missing_for_a_second_tool(self) -> None:
        codes = self.red(self.fx.cell("A").render(), tools=[TOOL_PATH, OTHER_TOOL_PATH])
        self.assertEqual(codes, ["TOOL_DIGEST_MISSING"])

    def test_tool_digest_missing_only_in_the_cell_that_lacks_it(self) -> None:
        both = [f"{TOOL_PATH}={sha256(TOOL_BODY)}", f"{OTHER_TOOL_PATH}={sha256(OTHER_TOOL_BODY)}"]
        good = self.fx.cell("A", digests=both)
        bad = self.fx.cell("B")
        self.fx.write_receipt(good.render(), bad.render())
        code, out, _ = self.fx.run(tools=[TOOL_PATH, OTHER_TOOL_PATH])
        self.assertEqual((code, out.splitlines()[0].split(":")[0]), (1, "TOOL_DIGEST_MISSING B"))

    def test_tool_digest_stale_against_the_candidate_blob(self) -> None:
        self.fx.write_tool(TOOL_PATH, b"print('changed')\n")
        new_candidate = self.fx.commit("change tool")
        self.fx.candidate = new_candidate
        stale = self.fx.cell("A", digests=[f"{TOOL_PATH}={sha256(TOOL_BODY)}"])
        self.fx.write_receipt(stale.render())
        code, out, _ = self.fx.run()
        self.assertEqual((code, self.fx.codes(out)), (1, ["TOOL_DIGEST_STALE"]))
        self.assertIn(sha256(b"print('changed')\n"), out)

    def test_tool_digest_stale_for_a_listed_path_absent_at_the_candidate(self) -> None:
        digests = self.fx.good_digests() + [f"tools/ghost.py={sha256(b'x')}"]
        self.assertEqual(self.red(self.fx.cell("A", digests=digests).render()), ["TOOL_DIGEST_STALE"])

    def test_tool_digest_stale_for_an_extra_listed_path_with_a_wrong_digest(self) -> None:
        digests = self.fx.good_digests() + [f"{OTHER_TOOL_PATH}={sha256(b'wrong')}"]
        self.assertEqual(self.red(self.fx.cell("A", digests=digests).render()), ["TOOL_DIGEST_STALE"])

    def test_tool_digest_stale_for_a_digest_line_without_equals(self) -> None:
        digests = self.fx.good_digests() + ["tools/second.py"]
        self.assertEqual(self.red(self.fx.cell("A", digests=digests).render()), ["TOOL_DIGEST_STALE"])

    def test_capture_missing(self) -> None:
        spec = self.fx.cell("A")
        (self.fx.evidence / "A.txt").unlink()
        self.assertEqual(self.red(spec.render()), ["CAPTURE_MISSING"])

    def test_capture_cr(self) -> None:
        text = "line\r\nexit=0\r\n"
        spec = self.fx.cell("A", text, block_text="line\nexit=0\n")
        # the block is the LF form; the capture holds CR: both defects, and the exit list still reads
        self.assertEqual(self.red(spec.render()), ["CAPTURE_CR", "BLOCK_MISMATCH"])

    def test_capture_cr_alone_when_the_block_cannot_differ(self) -> None:
        spec = self.fx.cell("A", "a\rb\nexit=0\n")  # a lone CR is carried into the block unchanged
        self.assertEqual(self.red(spec.render()), ["CAPTURE_CR"])

    def test_block_mismatch(self) -> None:
        spec = self.fx.cell("A", block_text="different\nexit=0\n")
        self.assertEqual(self.red(spec.render()), ["BLOCK_MISMATCH"])

    def test_block_mismatch_when_the_block_is_absent(self) -> None:
        spec = self.fx.cell("A", fence=False)
        self.assertEqual(self.red(spec.render()), ["BLOCK_MISMATCH"])

    def test_block_mismatch_when_the_fence_never_closes(self) -> None:
        text = self.fx.cell("A").render().rstrip("\n")
        self.assertTrue(text.endswith(FENCE))
        self.assertEqual(self.red(text[: -len(FENCE)]), ["BLOCK_MISMATCH"])

    def test_block_with_trailing_whitespace_differs(self) -> None:
        spec = self.fx.cell("A", block_text="A ran \nexit=0\n")
        self.assertEqual(self.red(spec.render()), ["BLOCK_MISMATCH"])

    def test_exit_mismatch_value(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", exit_value="1").render()), ["EXIT_MISMATCH"])

    def test_exit_mismatch_order_matters(self) -> None:
        spec = self.fx.cell("A", "x\nexit=1\nexit=0\n", exit_value="0,1")
        self.assertEqual(self.red(spec.render()), ["EXIT_MISMATCH"])

    def test_exit_mismatch_multiplicity_matters(self) -> None:
        spec = self.fx.cell("A", "x\nexit=0\nexit=0\n", exit_value="0")
        self.assertEqual(self.red(spec.render()), ["EXIT_MISMATCH"])

    def test_exit_mismatch_capture_without_exit_lines(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", "plain\n", exit_value="0").render()), ["EXIT_MISMATCH"])

    def test_a_cell_with_two_defects_reports_both_and_the_count(self) -> None:
        spec = self.fx.cell("A", exit_value="1", candidate="2" * 40)
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run()
        self.assertEqual((code, self.fx.codes(out)), (1, ["CANDIDATE_MISMATCH", "EXIT_MISMATCH"]))
        self.assertTrue(out.endswith("cells=1 defects=2\n"))

    def test_defect_lines_are_code_section_detail(self) -> None:
        self.fx.write_receipt(self.fx.cell("A", exit_value="1", heading="Heading A").render())
        out = self.fx.run()[1]
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("EXIT_MISMATCH Heading A: "), first)

    def test_every_code_is_distinct_and_printed(self) -> None:
        values = [code.value for code in evidence_gate.DefectCode]
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(len(values), 12)


class EscapeShapeTests(GateTestCase):
    """The shapes by which an earlier checker let a receipt pass or mislabelled a red as a fault."""

    def test_section_without_a_cell_line_is_not_skipped(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A").render(), "## B\ncapture: B.txt\nexit: 0\n"), ["NOT_RUN"])

    def test_statement_opt_out_cannot_hide_a_run_cell(self) -> None:
        self.fx.put_capture("B.txt", "exit=0\n")
        sneaky = f"## B\ncell: STATEMENT\ncandidate: x\ncapture: B.txt\nexit: 0\n\n{FENCE}\nexit=0\n{FENCE}\n"
        codes = self.red(self.fx.cell("A").render(), sneaky, extra=["--require-cell", "B"])
        # capture, exit, a fenced block and the required name each count; the required cell never ran
        self.assertEqual(codes, ["STATEMENT_HAS_RUN_FIELDS"] * 4 + ["NOT_RUN"])

    def test_lower_case_statement_is_a_run_cell_and_so_incomplete(self) -> None:
        codes = self.red(self.fx.cell("A").render(), "## s\ncell: statement\n")
        self.assertEqual(codes, ["CELL_FIELD_MISSING"] * 4)  # candidate, tool_digest:, capture, exit

    def test_missing_tool_digest_label_is_a_missing_field(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", label=False).render()), ["CELL_FIELD_MISSING"])

    def test_missing_capture_is_a_red_never_a_fault(self) -> None:
        spec = self.fx.cell("A")
        (self.fx.evidence / "A.txt").unlink()
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 1)

    def test_mixed_candidates_across_cells(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A").render(), self.fx.cell("B", candidate="3" * 40).render()), ["CANDIDATE_MISMATCH"])

    def test_exit_list_contradicting_the_capture(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", "exit=2\n", exit_value="0").render()), ["EXIT_MISMATCH"])

    def test_an_empty_run_is_not_a_pass(self) -> None:
        self.assertEqual(self.red("## Intro\ncell: STATEMENT\n"), ["NO_CELLS"])


class CapturePathTests(GateTestCase):
    """Path-prefix and empty-value cases of the capture reference."""

    def capture_result(self, reference: str) -> tuple[int, list[str]]:
        spec = self.fx.cell("A")
        spec.capture_file = reference
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run()
        return code, self.fx.codes(out)

    def capture_red(self, reference: str) -> list[str]:
        code, codes = self.capture_result(reference)
        self.assertEqual(code, 1)
        return codes

    def test_reference_equal_to_the_root(self) -> None:
        self.assertEqual(self.capture_red("."), ["CAPTURE_MISSING"])
        self.assertEqual(self.capture_red("./"), ["CAPTURE_MISSING"])

    def test_reference_that_is_a_directory(self) -> None:
        (self.fx.evidence / "sub").mkdir()
        self.assertEqual(self.capture_red("sub"), ["CAPTURE_MISSING"])

    def test_one_extra_character_in_the_root_name_is_a_sibling_not_the_root(self) -> None:
        sibling = self.fx.base / (self.fx.evidence.name + "2")
        sibling.mkdir()
        (sibling / "A.txt").write_bytes(b"A ran\nexit=0\n")
        self.assertEqual(self.capture_red(f"../{sibling.name}/A.txt"), ["CAPTURE_MISSING"])

    def test_trailing_slash(self) -> None:
        self.assertEqual(self.capture_red("A.txt/"), ["CAPTURE_MISSING"])
        self.assertEqual(self.capture_red("A.txt\\"), ["CAPTURE_MISSING"])

    def test_parent_traversal_is_never_read(self) -> None:
        (self.fx.base / "outside.txt").write_bytes(b"A ran\nexit=0\n")
        self.assertEqual(self.capture_red("../outside.txt"), ["CAPTURE_MISSING"])
        self.assertEqual(self.capture_red("sub/../../outside.txt"), ["CAPTURE_MISSING"])
        self.assertEqual(self.capture_red("..\\outside.txt"), ["CAPTURE_MISSING"])

    def test_traversal_that_stays_inside_the_root_resolves(self) -> None:
        (self.fx.evidence / "sub").mkdir()
        self.assertEqual(self.capture_result("sub/../A.txt"), (0, []))

    def test_absolute_path_is_never_read(self) -> None:
        absolute = str(self.fx.evidence / "A.txt")
        self.fx.put_capture("A.txt", "A ran\nexit=0\n")  # the target exists, so only confinement can refuse it
        self.assertEqual(self.capture_red(absolute), ["CAPTURE_MISSING"])
        self.assertEqual(self.capture_red("/A.txt"), ["CAPTURE_MISSING"])

    def test_drive_letter_is_never_read(self) -> None:
        self.assertEqual(self.capture_red("C:/Windows/win.ini"), ["CAPTURE_MISSING"])
        self.assertEqual(self.capture_red("C:A.txt"), ["CAPTURE_MISSING"])

    def test_case_variant_follows_the_file_system(self) -> None:
        (self.fx.evidence / "Sub").mkdir()
        (self.fx.evidence / "Sub" / "A.txt").write_bytes(b"A ran\nexit=0\n")
        variant = self.fx.evidence / "sub" / "A.txt"
        resolved = os.path.exists(variant)  # true on a case-insensitive file system
        code, codes = self.capture_result("sub/A.txt")
        self.assertEqual((code, codes), (0, []) if resolved else (1, ["CAPTURE_MISSING"]))

    def test_empty_capture_reference_is_a_missing_field(self) -> None:
        spec = self.fx.cell("A")
        spec.capture_file = ""
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run()
        self.assertEqual((code, self.fx.codes(out)), (1, ["CELL_FIELD_MISSING"]))

    def test_symlink_pointing_outside_the_root_is_not_read(self) -> None:
        outside = self.fx.base / "outside.txt"
        outside.write_bytes(b"A ran\nexit=0\n")
        link = self.fx.evidence / "link.txt"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are not available")
        self.assertEqual(self.capture_red("link.txt"), ["CAPTURE_MISSING"])


class EmptyAndTokenTests(GateTestCase):
    def test_empty_exit_value(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", exit_value="").render()), ["CELL_FIELD_MISSING"])

    def test_empty_tool_digest_list_names_every_tool(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", digests=[]).render()), ["TOOL_DIGEST_MISSING"])

    def test_digest_of_the_wrong_length_or_case_or_alphabet_is_stale(self) -> None:
        good = sha256(TOOL_BODY)
        for bad in (good[:63], good + "0", good.upper(), "g" * 64, ""):
            with self.subTest(bad=bad):
                spec = self.fx.cell("A", digests=[f"{TOOL_PATH}={bad}"])
                self.assertEqual(self.red(spec.render()), ["TOOL_DIGEST_STALE"])

    def test_short_candidate_is_a_missing_field(self) -> None:
        spec = self.fx.cell("A", candidate=self.fx.candidate[:12])
        self.assertEqual(self.red(spec.render()), ["CELL_FIELD_MISSING"])

    def test_upper_case_full_candidate_is_compared_exactly(self) -> None:
        spec = self.fx.cell("A", candidate=self.fx.candidate.upper())
        self.assertEqual(self.red(spec.render()), ["CANDIDATE_MISMATCH"])

    def test_non_hex_forty_character_candidate_is_a_missing_field(self) -> None:
        spec = self.fx.cell("A", candidate="z" * 40)
        self.assertEqual(self.red(spec.render()), ["CELL_FIELD_MISSING"])


class FaultTests(GateTestCase):
    def run_fault(
        self,
        candidate: str | None = None,
        tools: Sequence[str] | None = None,
        repo: Path | None = None,
        receipt: Path | None = None,
        evidence: Path | None = None,
    ) -> tuple[int, str, str]:
        code, out, err = self.fx.run(tools=tools, candidate=candidate, repo=repo, receipt=receipt, evidence=evidence)
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.assertNotIn("Traceback", out)
        return code, out, err

    def test_unknown_candidate_is_a_fault_with_git_stderr(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        _, out, err = self.run_fault(candidate="a" * 40)
        self.assertEqual(out, "")
        self.assertIn("fatal", err)
        self.assertTrue(err.startswith("tool fault:"))

    def test_tool_path_absent_from_the_candidate_is_a_fault(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        _, _, err = self.run_fault(tools=["tools/none.py"])
        self.assertIn("git show", err)

    def test_receipt_is_a_directory(self) -> None:
        self.run_fault(receipt=self.fx.base)

    def test_receipt_does_not_exist(self) -> None:
        self.run_fault(receipt=self.fx.base / "absent.md")

    def test_repo_is_not_a_repository(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        plain = self.fx.base / "plain"
        plain.mkdir()
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.fx.base)}):
            self.run_fault(repo=plain)

    def test_repo_directory_does_not_exist(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        self.run_fault(repo=self.fx.base / "nowhere")

    def test_evidence_root_is_not_a_directory(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        self.run_fault(evidence=self.fx.base / "RETURN.md")

    def test_git_cannot_start(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        with mock.patch.object(evidence_gate.subprocess, "run", side_effect=FileNotFoundError("git")):
            self.run_fault()

    def test_capture_unreadable_after_it_exists(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        with mock.patch.object(Path, "read_bytes", autospec=True, side_effect=_deny_captures):
            _, _, err = self.run_fault()
        self.assertIn("cannot read capture", err)

    def test_an_unexpected_error_is_a_fault_not_a_red(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        with mock.patch.object(evidence_gate, "check_receipt", side_effect=RuntimeError("boom")):
            _, _, err = self.run_fault()
        self.assertIn("RuntimeError", err)

    def test_a_fault_outranks_defects_in_the_receipt(self) -> None:
        self.fx.receipt.write_bytes(b"")
        code, _, _ = self.fx.run(candidate="b" * 40)
        self.assertEqual(code, 2)


_ORIGINAL_READ_BYTES = Path.read_bytes


def _deny_captures(self: Path) -> bytes:
    if self.suffix == ".txt":
        raise PermissionError("denied")
    return _ORIGINAL_READ_BYTES(self)


class UsageTests(GateTestCase):
    def usage(self, argv: Sequence[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = evidence_gate.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def base_argv(self) -> list[str]:
        return [str(self.fx.receipt), "--repo", str(self.fx.repo), "--candidate", self.fx.candidate, "--tool", TOOL_PATH]

    def test_no_arguments(self) -> None:
        code, out, err = self.usage([])
        self.assertEqual((code, out), (3, ""))
        self.assertTrue(err.startswith("usage:"))

    def test_missing_tool(self) -> None:
        self.assertEqual(self.usage(self.base_argv()[:-2])[0], 3)

    def test_missing_candidate(self) -> None:
        argv = self.base_argv()
        del argv[3:5]
        self.assertEqual(self.usage(argv)[0], 3)

    def test_missing_repo(self) -> None:
        argv = self.base_argv()
        del argv[1:3]
        self.assertEqual(self.usage(argv)[0], 3)

    def test_blank_tool_and_blank_require_cell(self) -> None:
        self.assertEqual(self.usage(self.base_argv() + ["--tool", "  "])[0], 3)
        self.assertEqual(self.usage(self.base_argv() + ["--require-cell", ""])[0], 3)

    def test_short_or_upper_case_candidate_argument(self) -> None:
        for bad in (self.fx.candidate[:12], self.fx.candidate.upper(), "", "z" * 40):
            argv = self.base_argv()
            argv[4] = bad
            with self.subTest(bad=bad):
                self.assertEqual(self.usage(argv)[0], 3)

    def test_unknown_option_extra_receipt_and_dangling_option(self) -> None:
        self.assertEqual(self.usage(self.base_argv() + ["--bogus"])[0], 3)
        self.assertEqual(self.usage(self.base_argv() + ["second.md"])[0], 3)
        self.assertEqual(self.usage(self.base_argv() + ["--require-cell"])[0], 3)
        self.assertEqual(self.usage(self.base_argv() + ["-x"])[0], 3)

    def test_repeated_single_options_and_blank_evidence_root(self) -> None:
        self.assertEqual(self.usage(self.base_argv() + ["--repo", "x"])[0], 3)
        self.assertEqual(self.usage(self.base_argv() + ["--evidence-root", " "])[0], 3)

    def test_equals_form_is_accepted(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        argv = [str(self.fx.receipt), f"--repo={self.fx.repo}", f"--candidate={self.fx.candidate}", f"--tool={TOOL_PATH}",
                f"--evidence-root={self.fx.evidence}"]
        self.assertEqual(self.usage(argv)[0], 0)

    def test_backslash_tool_path_is_normalised(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        code, _, _ = self.fx.run(tools=[TOOL_PATH.replace("/", "\\")])
        self.assertEqual(code, 0)

    def test_duplicate_tool_and_require_cell_arguments_collapse(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        code, out, _ = self.fx.run(["--require-cell", "A", "--require-cell", "A"], tools=[TOOL_PATH, TOOL_PATH])
        self.assertEqual((code, out), (0, "cells=2 defects=0\n"))


class ProcessTests(GateTestCase):
    """The script as a command: interpreter flags, line endings, console encoding."""

    def command(self, root: Path | None = None, isolated: bool = True) -> list[str]:
        flags = ["-I", "-X", "utf8"] if isolated else []
        return [
            sys.executable, *flags, str(SCRIPT), str(self.fx.receipt),
            "--repo", str(self.fx.repo), "--candidate", self.fx.candidate, "--tool", TOOL_PATH,
            "--evidence-root", str(root or self.fx.evidence),
        ]

    def test_output_is_lf_only_and_exit_zero(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        done = subprocess.run(self.command(), capture_output=True)
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"cells=2 defects=0\n", b""))

    def test_red_under_a_cp950_console_still_exits_one(self) -> None:
        self.fx.write_receipt(self.fx.cell("A", exit_value="1", heading="A " + NON_CP950).render())
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        done = subprocess.run(self.command(isolated=False), capture_output=True, env=env)
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertNotIn(b"Traceback", done.stderr)
        self.assertIn(b"\\u0e01", done.stdout)

    def test_usage_error_exits_three_without_traceback(self) -> None:
        done = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True)
        self.assertEqual(done.returncode, 3)
        self.assertNotIn(b"Traceback", done.stderr)

    def test_fault_exits_two_without_traceback(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        done = subprocess.run(self.command(root=self.fx.base / "nowhere"), capture_output=True)
        self.assertEqual(done.returncode, 2)
        self.assertNotIn(b"Traceback", done.stderr)

    def test_the_script_uses_only_the_standard_library(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for banned in ("import requests", "import yaml", "# type: ignore", "typing import Any", ": Any"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
