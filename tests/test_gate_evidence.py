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
        second = self.fx.cell("A")
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
        self.fx.write_receipt(self.fx.cell("Heading A", exit_value="1").render())
        out = self.fx.run()[1]
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("EXIT_MISMATCH Heading A: "), first)

    def test_every_code_is_distinct_and_printed(self) -> None:
        values = [code.value for code in evidence_gate.DefectCode]
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(len(values), 14)


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
        codes = self.red(self.fx.cell("A").render(), "## statement\ncell: statement\n")
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

    def test_directory_junction_pointing_outside_the_root_is_not_read(self) -> None:
        if os.name != "nt":
            self.skipTest("directory junctions exist on Windows only; the symlink test covers other hosts")
        outside = self.fx.base / "outside_dir"
        outside.mkdir()
        (outside / "A.txt").write_bytes(b"A ran\nexit=0\n")
        junction = self.fx.evidence / "jn"
        made = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)], capture_output=True)
        self.assertEqual(made.returncode, 0, made.stdout + made.stderr)  # a junction needs no privilege
        self.addCleanup(os.rmdir, junction)
        self.assertTrue((junction / "A.txt").is_file())  # the target reads fine; only confinement can refuse it
        self.assertEqual(self.capture_red("jn/A.txt"), ["CAPTURE_MISSING"])


class RepeatedFieldAndNameTests(GateTestCase):
    """A field given twice, a second fence, a heading that differs from the cell name."""

    def run_text(self, text: str) -> tuple[int, str, str]:
        self.fx.receipt.write_bytes(("# receipt\n\n" + text).encode("utf-8"))
        return self.fx.run()

    def with_extra_line(self, anchor: str, extra: str) -> str:
        text = self.fx.cell("A").render()
        self.assertEqual(text.count(anchor), 1)
        return text.replace(anchor, anchor + "\n" + extra)

    def test_a_second_single_value_field_is_field_repeated(self) -> None:
        other = "1" * 40
        for name, anchor, extra in (
            ("cell", "cell: A", "cell: A"),
            ("candidate", f"candidate: {self.fx.candidate}", f"candidate: {other}"),
            ("capture", "capture: A.txt", "capture: A.txt"),
            ("exit", "exit: 0", "exit: 1"),
        ):
            with self.subTest(field=name):
                code, out, _ = self.run_text(self.with_extra_line(anchor, extra))
                self.assertEqual(code, 1, out)
                self.assertIn(f"FIELD_REPEATED A: {name}: given more than once\n", out)

    def test_a_second_tool_digest_label_is_field_repeated(self) -> None:
        text = self.fx.cell("A").render().replace("capture: A.txt", "tool_digest:\ncapture: A.txt")
        code, out, _ = self.run_text(text)
        self.assertEqual((code, self.fx.codes(out)), (1, ["FIELD_REPEATED"]))
        self.assertIn("tool_digest: given more than once", out)

    def test_a_second_fence_is_field_repeated(self) -> None:
        text = self.fx.cell("A").render() + f"\n{FENCE}\nanother block\n{FENCE}\n"
        code, out, _ = self.run_text(text)
        self.assertEqual((code, self.fx.codes(out)), (1, ["FIELD_REPEATED"]))
        self.assertIn("FIELD_REPEATED A: second fenced block\n", out)

    def test_every_repeated_field_is_reported_once_each(self) -> None:
        text = self.fx.cell("A").render().replace("exit: 0", "exit: 0\nexit: 0\nexit: 0\ncell: A")
        code, out, _ = self.run_text(text)
        self.assertEqual((code, self.fx.codes(out)), (1, ["FIELD_REPEATED", "FIELD_REPEATED"]))

    def test_a_field_name_inside_the_fence_is_not_a_repeat(self) -> None:
        spec = self.fx.cell("A", "cell: A\nexit: 0\nexit=0\n")
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)

    def test_heading_different_from_the_cell_value_is_cell_name_mismatch(self) -> None:
        self.assertEqual(self.red(self.fx.cell("A", heading="B").render()), ["CELL_NAME_MISMATCH"])

    def test_cell_name_mismatch_line_names_both(self) -> None:
        self.fx.write_receipt(self.fx.cell("A", heading="B").render())
        out = self.fx.run()[1]
        self.assertIn("CELL_NAME_MISMATCH B: cell: line names 'A', the heading names 'B'\n", out)

    def test_the_name_comparison_is_case_sensitive(self) -> None:
        for heading, name in (("a", "A"), ("A", "a"), ("Cell", "cell")):
            with self.subTest(heading=heading, name=name):
                spec = self.fx.cell("A", heading=heading)
                spec.name = name
                self.assertEqual(self.red(spec.render()), ["CELL_NAME_MISMATCH"])

    def test_a_mismatched_cell_still_reports_every_other_defect(self) -> None:
        spec = self.fx.cell("A", exit_value="7", heading="B", candidate="1" * 40)
        spec.digests = [f"{TOOL_PATH}={sha256(b'wrong')}"]
        self.assertEqual(
            self.red(spec.render()),
            ["CELL_NAME_MISMATCH", "CANDIDATE_MISMATCH", "TOOL_DIGEST_STALE", "EXIT_MISMATCH"],
        )

    def test_a_mismatched_cell_is_still_checked_for_duplicates_and_capture(self) -> None:
        first = self.fx.cell("A")
        second = self.fx.cell("A", heading="B")
        second.capture_file = "absent.txt"
        codes = self.red(first.render(), second.render())
        self.assertEqual(codes, ["CELL_NAME_MISMATCH", "DUPLICATE_CELL", "CAPTURE_MISSING"])

    def test_a_mismatched_cell_still_counts_as_the_named_cell(self) -> None:
        self.fx.write_receipt(self.fx.cell("A", heading="B").render())
        code, out, _ = self.fx.run(["--require-cell", "A"])
        self.assertEqual((code, self.fx.codes(out)), (1, ["CELL_NAME_MISMATCH"]))  # reported once, not as NOT_RUN


class DigestPathTests(GateTestCase):
    """A digest path of a bad form is a red; a well-formed one is read from the repository root."""

    def digest_result(self, extra_path: str, digest: str | None = None, repo: Path | None = None) -> tuple[int, list[str], str]:
        value = digest if digest is not None else sha256(b"x")
        spec = self.fx.cell("A", digests=self.fx.good_digests() + [f"{extra_path}={value}"])
        self.fx.write_receipt(spec.render())
        code, out, err = self.fx.run(repo=repo)
        self.assertEqual(err, "", err)
        return code, self.fx.codes(out), out

    def test_a_path_of_a_bad_form_is_tool_digest_stale_exit_one(self) -> None:
        for bad in (
            "../outside", "tools/../../outside", "tools/../tools/probe.py", "..\\outside",
            "/abs/probe.py", "\\\\host\\share\\probe.py", "C:/probe.py", "C:probe.py", "c:\\probe.py",
            ":(top)tools/probe.py", ":/tools/probe.py", ":x",
        ):
            with self.subTest(path=bad):
                code, codes, _ = self.digest_result(bad)
                self.assertEqual((code, codes), (1, ["TOOL_DIGEST_STALE"]))

    def test_an_empty_path_is_tool_digest_stale(self) -> None:
        code, codes, _ = self.digest_result("")
        self.assertEqual((code, codes), (1, ["TOOL_DIGEST_STALE"]))

    def test_a_well_formed_extra_path_with_its_digest_passes(self) -> None:
        code, codes, out = self.digest_result(OTHER_TOOL_PATH, sha256(OTHER_TOOL_BODY))
        self.assertEqual((code, codes), (0, []), out)

    def test_a_well_formed_extra_path_absent_at_the_candidate_is_stale(self) -> None:
        code, codes, _ = self.digest_result("tools/ghost.py")
        self.assertEqual((code, codes), (1, ["TOOL_DIGEST_STALE"]))

    def test_dots_inside_a_name_are_not_a_parent_segment(self) -> None:
        self.fx.write_tool("tools/a..b.py", b"x\n")
        self.fx.candidate = self.fx.commit("dotted name")
        code, codes, out = self.digest_result("tools/a..b.py", sha256(b"x\n"))
        self.assertEqual((code, codes), (0, []), out)

    def test_repo_a_subdirectory_gives_the_same_result_as_the_root(self) -> None:
        subdirectory = self.fx.repo / "tools"
        good = self.digest_result(OTHER_TOOL_PATH, sha256(OTHER_TOOL_BODY), repo=subdirectory)
        self.assertEqual(good[:2], (0, []), good[2])
        ghost = self.digest_result("tools/ghost.py", repo=subdirectory)
        self.assertEqual(ghost[:2], (1, ["TOOL_DIGEST_STALE"]))
        bad = self.digest_result("../outside", repo=subdirectory)
        self.assertEqual(bad[:2], (1, ["TOOL_DIGEST_STALE"]))

    def test_repo_a_subdirectory_reads_the_tool_arguments_from_the_root_too(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        code, out, err = self.fx.run(repo=self.fx.repo / "tools")
        self.assertEqual((code, out, err), (0, "cells=2 defects=0\n", ""))


class DigestLookupTests(GateTestCase):
    """Canonical form first, then one literal lookup through the standard input of git cat-file."""

    def add_entry(self, path: str, body: bytes | None = None, mode: str = "100644", object_id: str | None = None) -> str:
        """Commit an index entry without touching the working tree; returns the new candidate."""
        if object_id is None:
            made = subprocess.run(
                ["git", "-C", str(self.fx.repo), "hash-object", "-w", "--stdin"], input=body or b"", capture_output=True, check=True
            )
            object_id = made.stdout.decode("ascii").strip()
        git(self.fx.repo, "update-index", "--add", "--cacheinfo", f"{mode},{object_id},{path}")
        git(self.fx.repo, "commit", "-q", "-m", "entry")
        self.fx.candidate = git(self.fx.repo, "rev-parse", "HEAD").strip()
        return self.fx.candidate

    def listed(self, extra_path: str, digest: str | None = None) -> tuple[int, list[str], str, str]:
        value = digest if digest is not None else sha256(b"x")
        spec = self.fx.cell("A", digests=self.fx.good_digests() + [f"{extra_path}={value}"])
        self.fx.write_receipt(spec.render())
        code, out, err = self.fx.run()
        return code, self.fx.codes(out), out, err

    def assert_stale_without_asking_git(self, extra_path: str) -> None:
        asked: list[tuple[list[str], bytes | None]] = []
        real = subprocess.run

        def spy(command: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            raw = kwargs.get("input")
            asked.append((list(command), raw if isinstance(raw, bytes) else None))
            return real(command, *args, **kwargs)

        with mock.patch.object(evidence_gate.subprocess, "run", side_effect=spy):
            code, codes, out, err = self.listed(extra_path)
        self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)
        request = (f"{self.fx.candidate}:{extra_path}" + chr(10)).encode("utf-8")
        for command, raw in asked:
            self.assertNotEqual(raw, request, "a non-canonical path reached git")
            self.assertNotIn(extra_path, command)

    # one test per shape that is not canonical
    def test_backslash_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools\\second.py")

    def test_empty_segment_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools//second.py")

    def test_single_dot_segment_inside_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/./second.py")

    def test_the_path_dot_is_stale(self) -> None:
        self.assert_stale_without_asking_git(".")

    def test_a_leading_dot_segment_is_stale(self) -> None:
        self.assert_stale_without_asking_git("./tools/second.py")

    def test_a_trailing_slash_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/")

    def test_more_than_1024_bytes_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/" + "a" * (1025 - len("tools/")))

    def test_the_limit_counts_bytes_not_characters(self) -> None:
        wide = "tools/" + "\u00e9" * 510  # 510 characters, 1026 bytes
        self.assertLess(len(wide), 1024)
        self.assertEqual(len(wide.encode("utf-8")), 1026)
        self.assert_stale_without_asking_git(wide)

    def test_nul_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/se\x00cond.py")

    def test_del_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/se\x7fcond.py")

    def test_unit_separator_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/se\x1fcond.py")

    def test_a_leading_slash_is_stale(self) -> None:
        self.assert_stale_without_asking_git("/tools/second.py")

    def test_a_drive_letter_is_stale(self) -> None:
        self.assert_stale_without_asking_git("C:/tools/second.py")

    def test_a_leading_colon_is_stale(self) -> None:
        self.assert_stale_without_asking_git(":/tools/second.py")

    def test_a_parent_segment_is_stale(self) -> None:
        self.assert_stale_without_asking_git("tools/../tools/second.py")

    def test_each_refusal_names_its_own_reason(self) -> None:
        for path, reason in (
            ("", "empty path"), ("/tools/second.py", "absolute path"), ("tools//second.py", "empty segment"),
            ("tools/./second.py", "'.' segment"), ("tools/../second.py", "'..' segment"), ("tools\\second.py", "backslash"),
            ("C:/second.py", "drive letter"), (":/second.py", "pathspec magic"), ("tools/" + "a" * 1100, "longer than 1024"),
            ("tools/se\x7fcond.py", "control character"),
        ):
            with self.subTest(path=path[:20]):
                code, codes, out, err = self.listed(path)
                self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)
                self.assertIn(reason, out)

    # the boundaries on the canonical side: these paths are looked up and found
    def test_a_path_of_exactly_1024_bytes_is_looked_up(self) -> None:
        path = "tools/" + "a" * (1024 - len("tools/"))
        self.assertEqual(len(path.encode("utf-8")), 1024)
        self.add_entry(path, b"long\n")
        code, codes, out, _ = self.listed(path, sha256(b"long\n"))
        self.assertEqual((code, codes), (0, []), out)

    def test_a_space_a_tilde_and_a_caret_inside_a_name_are_canonical(self) -> None:
        for name in ("tools/with space.py", "tools/a~b.py", "tools/a^b.py", "tools/a=b.py"):
            with self.subTest(name=name):
                body = name.encode("utf-8") + b"\n"
                self.add_entry(name, body)
                code, codes, out, err = self.listed(name, sha256(body))
                self.assertEqual((code, codes, err), (0, [], ""), out)

    def test_a_path_that_looks_like_revision_syntax_is_still_a_literal_name(self) -> None:
        for name in (f"{TOOL_PATH}^{{blob}}", f"{TOOL_PATH}^{{}}", f"{TOOL_PATH}~1", f"{TOOL_PATH}^", f"{TOOL_PATH}@{{1}}"):
            with self.subTest(name=name):
                code, codes, out, err = self.listed(name, sha256(TOOL_BODY))
                self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)

    # what is found is judged by type
    def test_a_tree_at_the_candidate_is_stale(self) -> None:
        raw = subprocess.run(
            ["git", "-C", str(self.fx.repo), "cat-file", "tree", f"{self.fx.candidate}:tools"], capture_output=True, check=True
        ).stdout
        code, codes, out, err = self.listed("tools", sha256(raw))  # the digest of the tree's own bytes is still no blob
        self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)

    def test_a_gitlink_at_the_candidate_is_stale(self) -> None:
        raw = subprocess.run(
            ["git", "-C", str(self.fx.repo), "cat-file", "commit", self.fx.candidate], capture_output=True, check=True
        ).stdout
        self.add_entry("tools/sub", mode="160000", object_id=self.fx.candidate)  # an object that exists, of type commit
        code, codes, out, err = self.listed("tools/sub", sha256(raw))
        self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)

    def test_a_gitlink_to_an_absent_object_is_stale(self) -> None:
        self.add_entry("tools/sub", mode="160000", object_id="1" * 40)
        code, codes, out, err = self.listed("tools/sub", "1" * 40)
        self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)

    def test_a_symlink_is_a_blob_read_as_stored(self) -> None:
        self.add_entry("tools/link", b"probe.py", mode="120000")
        good = self.listed("tools/link", sha256(b"probe.py"))
        self.assertEqual(good[:2], (0, []), good[2])
        stale = self.listed("tools/link", sha256(TOOL_BODY))
        self.assertEqual(stale[:2], (1, ["TOOL_DIGEST_STALE"]))

    def test_a_missing_path_is_stale_not_a_fault(self) -> None:
        code, codes, out, err = self.listed("tools/ghost.py")
        self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)
        self.assertIn("is not present at candidate", out)

    def test_a_correct_required_line_plus_one_non_canonical_extra_line_is_red(self) -> None:
        code, codes, out, err = self.listed("tools//second.py", sha256(OTHER_TOOL_BODY))
        self.assertEqual((code, codes, err), (1, ["TOOL_DIGEST_STALE"], ""), out)

    # the shape of the lookup itself
    def setUp(self) -> None:
        super().setUp()
        self.addCleanup(self.release_lookup_patch)

    def spy_on_git(self) -> list[tuple[list[str], bytes | None]]:
        asked: list[tuple[list[str], bytes | None]] = []
        real = subprocess.run

        def spy(command: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            raw = kwargs.get("input")
            asked.append((list(command), raw if isinstance(raw, bytes) else None))
            return real(command, *args, **kwargs)

        patcher = mock.patch.object(evidence_gate.subprocess, "run", side_effect=spy)
        patcher.start()
        self.addCleanup(patcher.stop)
        return asked

    def test_a_digest_path_is_only_ever_written_to_standard_input_of_cat_file(self) -> None:
        asked = self.spy_on_git()
        spec = self.fx.cell("A", digests=self.fx.good_digests() + [f"{OTHER_TOOL_PATH}={sha256(OTHER_TOOL_BODY)}"])
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)
        self.assertTrue(asked)
        for command, raw in asked:
            self.assertEqual(command[:2], ["git", "-C"])
            verb = command[3]
            self.assertIn(verb, ("rev-parse", "cat-file"), command)
            self.assertNotIn(verb, ("ls-tree", "show"))
            for token in command:
                self.assertNotIn("second.py", token)
                self.assertNotIn("probe.py", token)
            if verb == "cat-file":
                self.assertIn(command[4:], (["--batch-check"], ["--batch"]))
                self.assertIsNotNone(raw)

    def test_each_path_is_looked_up_once_for_batch_check_and_once_for_content(self) -> None:
        asked = self.spy_on_git()
        extra = f"{OTHER_TOOL_PATH}={sha256(OTHER_TOOL_BODY)}"
        first = self.fx.cell("A", digests=self.fx.good_digests() + [extra])
        second = self.fx.cell("B", digests=self.fx.good_digests() + [extra])
        self.fx.write_receipt(first.render(), second.render())
        self.assertEqual(self.fx.run()[0], 0)
        for path in (TOOL_PATH, OTHER_TOOL_PATH):
            wanted = f"{self.fx.candidate}:{path}\n".encode("utf-8")
            for mode in ("--batch-check", "--batch"):
                count = sum(1 for command, raw in asked if command[3:5] == ["cat-file", mode] and raw == wanted)
                self.assertEqual(count, 1, (path, mode))

    def test_a_path_missing_at_the_candidate_never_asks_for_content(self) -> None:
        asked = self.spy_on_git()
        self.listed("tools/ghost.py")
        wanted = f"{self.fx.candidate}:tools/ghost.py\n".encode("utf-8")
        modes = [command[4] for command, raw in asked if command[3] == "cat-file" and raw == wanted]
        self.assertEqual(modes, ["--batch-check"])

    # a lookup failure is a fault, never a red
    _lookup_patch: "mock._patch[mock.MagicMock] | None" = None

    def release_lookup_patch(self) -> None:
        if self._lookup_patch is not None:
            self._lookup_patch.stop()
            self._lookup_patch = None

    def fail_lookup(self, mode: str, containing: bytes, returncode: int, stdout: bytes, stderr: bytes) -> None:
        real = subprocess.run

        def fake(command: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            raw = kwargs.get("input")
            if command[3:5] == ["cat-file", mode] and isinstance(raw, bytes) and containing in raw:
                return subprocess.CompletedProcess(command, returncode, stdout, stderr)
            return real(command, *args, **kwargs)

        self.release_lookup_patch()
        self._lookup_patch = mock.patch.object(evidence_gate.subprocess, "run", side_effect=fake)
        self._lookup_patch.start()

    def listed_extra_good(self) -> tuple[int, str, str]:
        spec = self.fx.cell("A", digests=self.fx.good_digests() + [f"{OTHER_TOOL_PATH}={sha256(OTHER_TOOL_BODY)}"])
        self.fx.write_receipt(spec.render())
        return self.fx.run()

    def test_batch_check_exiting_non_zero_is_exit_two_never_stale(self) -> None:
        self.fail_lookup("--batch-check", b"second.py", 128, b"", b"fatal: boom\nsecond line")
        code, out, err = self.listed_extra_good()
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("tool fault:"))
        self.assertIn("fatal: boom", err)
        self.assertEqual(len(err.splitlines()), 1)  # git's two lines are printed as one

    def test_a_failing_lookup_in_a_receipt_that_is_otherwise_red_is_still_exit_two(self) -> None:
        self.fail_lookup("--batch-check", b"second.py", 1, b"", b"fatal: boom")
        spec = self.fx.cell("A", exit_value="9", digests=self.fx.good_digests() + [f"{OTHER_TOOL_PATH}={sha256(OTHER_TOOL_BODY)}"])
        self.fx.write_receipt(spec.render())
        code, out, _ = self.fx.run()
        self.assertEqual((code, out), (2, ""))

    def test_batch_exiting_non_zero_is_exit_two(self) -> None:
        self.fail_lookup("--batch", b"second.py", 128, b"", b"fatal: boom")
        code, out, err = self.listed_extra_good()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("fatal: boom", err)

    def test_an_answer_outside_the_documented_format_is_exit_two(self) -> None:
        for answer in (b"", b"garbage\n", b"x blob 2\n", b"0" * 40 + b" blob\n", b"0" * 40 + b" blob 2\nextra\n"):
            with self.subTest(answer=answer):
                self.fail_lookup("--batch-check", b"second.py", 0, answer, b"")
                code, out, err = self.listed_extra_good()
                self.assertEqual((code, out), (2, ""), err)

    def test_a_content_answer_that_does_not_match_its_header_is_exit_two(self) -> None:
        for answer in (b"", b"0" * 40 + b" blob 5\nabc\n", b"nonsense\nabc\n"):
            with self.subTest(answer=answer):
                self.fail_lookup("--batch", b"second.py", 0, answer, b"")
                code, out, err = self.listed_extra_good()
                self.assertEqual((code, out), (2, ""), err)

    def test_a_tool_argument_that_is_a_tree_or_absent_is_exit_two(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        for tool in ("tools", "tools/none.py"):
            with self.subTest(tool=tool):
                code, out, err = self.fx.run(tools=[tool])
                self.assertEqual((code, out), (2, ""), err)
                self.assertIn("is not a blob", err)


class ExitLineTests(GateTestCase):
    def test_exit_equals_inside_a_longer_line_is_not_an_exit(self) -> None:
        spec = self.fx.cell("A", "ran with exit=3 inside\nexit=0\n", exit_value="0")
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)

    def test_a_capture_holding_exit_only_inside_longer_lines_has_no_exit(self) -> None:
        for text in ("child exit=0\n", "exit=0 \n", " exit=0\n", "exit=0;\n", "# exit=0\n", "exit=\n", "exit=x\n"):
            with self.subTest(text=text):
                spec = self.fx.cell("A", text, exit_value="0")
                self.assertEqual(self.red(spec.render()), ["EXIT_MISMATCH"])

    def test_listing_the_embedded_exit_is_a_mismatch(self) -> None:
        spec = self.fx.cell("A", "ran with exit=3 inside\nexit=0\n", exit_value="3,0")
        self.assertEqual(self.red(spec.render()), ["EXIT_MISMATCH"])

    def test_negative_and_multi_digit_exit_lines_count(self) -> None:
        spec = self.fx.cell("A", "exit=-1\nexit=255\n", exit_value="-1,255")
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)


class ReceiptEncodingTests(GateTestCase):
    def test_a_utf8_bom_before_the_first_heading_is_read(self) -> None:
        self.fx.receipt.write_bytes(b"\xef\xbb\xbf" + self.fx.cell("A").render().encode("utf-8"))
        code, out, _ = self.fx.run()
        self.assertEqual((code, out), (0, "cells=1 defects=0\n"))

    def test_a_bom_with_crlf_line_endings_is_read(self) -> None:
        text = self.fx.cell("A").render().replace("\n", "\r\n")
        self.fx.receipt.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
        code, out, _ = self.fx.run()
        self.assertEqual((code, out), (0, "cells=1 defects=0\n"))


class TextValueTests(GateTestCase):
    """Lone surrogates and control characters in receipt fields are reds; every printed subject is one line."""

    def run_bytes(self, raw: bytes, extra: Sequence[str] = ()) -> tuple[int, str, str]:
        self.fx.receipt.write_bytes(raw)
        return self.fx.run(extra)

    def assert_one_line_per_defect(self, out: str) -> None:
        lines = out.split("\n")
        self.assertEqual(lines[-1], "")
        self.assertEqual(len(out.splitlines()), len(lines) - 1, repr(out))  # no hidden line separator
        for line in out.splitlines()[:-1]:
            self.assertRegex(line, r"^[A-Z_]+ ")
        self.assertRegex(out.splitlines()[-1], r"^cells=\d+ defects=\d+$")

    def test_invalid_utf8_in_a_capture_reference_is_a_red(self) -> None:
        raw = self.fx.cell("A").render().encode("utf-8").replace(b"capture: A.txt", b"capture: A\xff.txt")
        code, out, err = self.run_bytes(raw)
        self.assertEqual((code, err, self.fx.codes(out)), (1, "", ["CAPTURE_MISSING"]))
        self.assertIn("\\udcff", out)
        self.assert_one_line_per_defect(out)

    def test_invalid_utf8_in_candidate_exit_and_digest_value_is_a_red(self) -> None:
        text = self.fx.cell("A").render().encode("utf-8")
        digest = sha256(TOOL_BODY).encode()
        for old, new in (
            (b"exit: 0", b"exit: 0\xff"),
            (self.fx.candidate.encode(), self.fx.candidate.encode()[:-1] + b"\xfe"),
            (digest, digest[:-1] + b"\xfe"),
        ):
            with self.subTest(old=old[:8]):
                code, out, err = self.run_bytes(text.replace(old, new, 1))
                self.assertEqual((code, err), (1, ""))
                self.assert_one_line_per_defect(out)

    def test_a_lone_surrogate_encoded_as_cesu_bytes_is_a_red(self) -> None:
        raw = self.fx.cell("A").render().encode("utf-8").replace(b"capture: A.txt", b"capture: A\xed\xa0\x80.txt")
        code, out, err = self.run_bytes(raw)
        self.assertEqual((code, err, self.fx.codes(out)), (1, "", ["CAPTURE_MISSING"]))

    def test_control_characters_in_a_capture_reference_are_never_read(self) -> None:
        for control in ("\x00", "\x01", "\x1b", "\x7f", "\t"):
            with self.subTest(control=repr(control)):
                text = self.fx.cell("A").render().replace("capture: A.txt", f"capture: A{control}b.txt")
                code, out, err = self.run_bytes(text.encode("utf-8"))
                self.assertEqual((code, err, self.fx.codes(out)), (1, "", ["CAPTURE_MISSING"]))
                self.assert_one_line_per_defect(out)

    def test_a_trailing_control_character_is_not_stripped_away(self) -> None:
        for field_line in ("capture: A.txt", "exit: 0", f"candidate: {self.fx.candidate}"):
            with self.subTest(field=field_line):
                text = self.fx.cell("A").render().replace(field_line, field_line + "\x1f")
                code, out, err = self.run_bytes(text.encode("utf-8"))
                self.assertEqual((code, err), (1, ""))
                self.assert_one_line_per_defect(out)

    def test_a_control_character_in_a_digest_path_is_a_stale_digest(self) -> None:
        spec = self.fx.cell("A", digests=self.fx.good_digests() + [f"tools/se\x01cond.py={sha256(b'x')}"])
        code, out, err = self.run_bytes(spec.render().encode("utf-8"))
        self.assertEqual((code, err, self.fx.codes(out)), (1, "", ["TOOL_DIGEST_STALE"]))
        self.assertIn("\\x01", out)
        self.assert_one_line_per_defect(out)

    def test_a_control_character_in_a_heading_or_cell_name_is_not_run(self) -> None:
        text = self.fx.cell("A").render()
        for variant in (text.replace("## A", "## A\x01").replace("cell: A", "cell: A\x01"), text.replace("## A", "## A\x0b")):
            with self.subTest(variant=variant[:12]):
                code, out, err = self.run_bytes(("## ok\ncell: STATEMENT\n" + variant).encode("utf-8"))
                self.assertEqual((code, err), (1, ""))
                self.assertIn("NOT_RUN ", out)
                self.assertIn("NO_CELLS ", out)
                self.assert_one_line_per_defect(out)

    def test_del_and_the_unit_separator_in_a_cell_name_are_reds_and_a_space_is_not(self) -> None:
        for control in ("\x7f", "\x1f", "\x00", "\x01"):
            with self.subTest(control=repr(control)):
                name = f"A{control}b"
                spec = self.fx.cell("A", heading=name)
                spec.name = name
                code, out, err = self.run_bytes(spec.render().encode("utf-8"))
                self.assertEqual((code, err), (1, ""))
                self.assertIn("NOT_RUN ", out)
                self.assertIn("NO_CELLS ", out)
                self.assert_one_line_per_defect(out)
        spaced = self.fx.cell("A b")
        code, out, err = self.run_bytes(spaced.render().encode("utf-8"))
        self.assertEqual((code, out, err), (0, "cells=1 defects=0\n", ""))

    def test_a_statement_heading_with_a_control_character_is_a_red(self) -> None:
        raw = ("## S\x02\ncell: STATEMENT\n\n" + self.fx.cell("A").render()).encode("utf-8")
        code, out, _ = self.run_bytes(raw)
        self.assertEqual((code, self.fx.codes(out)), (1, ["NOT_RUN"]))

    def test_line_separators_in_a_printed_subject_cannot_forge_a_line(self) -> None:
        forged = "B\u2028NO_CELLS x\u2029more\x85end"
        text = self.fx.cell("A", heading=forged).render()
        code, out, err = self.run_bytes(("# t\n\n" + text).encode("utf-8"))
        self.assertEqual((code, err), (1, ""))
        self.assertEqual(self.fx.codes(out), ["CELL_NAME_MISMATCH"])
        self.assertEqual(len(out.splitlines()), 2, repr(out))
        self.assertIn("\\u2028", out)
        self.assertIn("\\x85", out)

    def test_a_required_cell_name_is_printed_on_one_line_and_bad_ones_are_usage_errors(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        code, out, err = self.fx.run(["--require-cell", "Z\u2028NO_CELLS x"])
        self.assertEqual((code, err), (1, ""))
        self.assertEqual(len(out.splitlines()), 2, repr(out))
        for bad in ("Z\nNO_CELLS x", "Z\udcff"):
            with self.subTest(bad=bad):
                code, _, err = self.fx.run(["--require-cell", bad])
                self.assertEqual(code, 3, err)

    def test_a_tool_argument_with_a_control_character_is_a_usage_error(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        code, out, err = self.fx.run(tools=[TOOL_PATH, "tools/a\x01b.py"])
        self.assertEqual((code, out), (3, ""))
        self.assertNotIn("\x01", err)

    def test_a_candidate_value_is_printed_escaped(self) -> None:
        text = self.fx.cell("A").render().replace(f"candidate: {self.fx.candidate}", "candidate: " + "\x07" * 40)
        code, out, err = self.run_bytes(text.encode("utf-8"))
        self.assertEqual((code, err), (1, ""))
        self.assert_one_line_per_defect(out)
        self.assertNotIn("\x07", out)

    def test_a_capture_may_hold_control_characters_it_is_data_not_a_field(self) -> None:
        spec = self.fx.cell("A", "esc \x1b[0m\x0c\nexit=0\n")
        self.fx.write_receipt(spec.render())
        self.assertEqual(self.fx.run()[0], 0)


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
        self.assertIn("is not a blob", err)

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

    def test_a_tool_path_that_is_not_canonical_is_a_usage_error(self) -> None:
        self.fx.write_receipt(*self.fx.good_parts())
        for bad in ("tools//probe.py", "tools/./probe.py", "./tools/probe.py", "tools/", "/tools/probe.py",
                    "tools/../probe.py", ":x", "C:/probe.py", "tools/" + "a" * 1025):
            with self.subTest(tool=bad[:40]):
                argv = [str(self.fx.receipt), "--repo", str(self.fx.repo), "--candidate", self.fx.candidate, "--tool", bad]
                code, out, err = self.usage(argv)
                self.assertEqual((code, out), (3, ""))
                self.assertTrue(err.startswith("usage:"))
                self.assertEqual(len(err.splitlines()), 2)

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
