"""Behavioural tests for the contract_gate script (six defect codes, exit codes 0/1/2/3).

Every fixture is generated in a temporary directory; every expected value is derived
from the text the fixture wrote.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import contract_gate  # noqa: E402

SCRIPT = _SCRIPTS / "contract_gate.py"
CODES = (
    "NO_SPEC_FOR_REQUIREMENT",
    "SOURCE_MISSING",
    "SOURCE_DIGEST_MISMATCH",
    "RETIRED_REQUIREMENT_BOUND",
    "LITERAL_EXPECTED",
    "NO_MUTATION",
)
SOURCE_BYTES = b"source of truth\n"
LEDGER_ASSERT = "    assert value == expected_from_ledger"
GIT_ENVIRONMENT = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}
_TEMPLATES: list[tempfile.TemporaryDirectory[str]] = []
_TEMPLATE_REPO: list[Path] = []


def git(repo: Path, *args: str) -> str:
    """Run git in `repo` with a clean configuration; a failure fails the fixture."""
    environment = {**os.environ, **GIT_ENVIRONMENT}
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=environment, check=False)
    if done.returncode != 0:
        raise AssertionError(f"git {args}: {done.stderr.decode('utf-8', errors='replace')}")
    return done.stdout.decode("utf-8", errors="replace")


def init_repo(repo: Path) -> None:
    empty_template = repo.parent / "empty-template"
    empty_template.mkdir(exist_ok=True)
    git(repo.parent, "init", "-q", f"--template={empty_template}", str(repo))
    for key, value in (("core.autocrlf", "false"), ("core.safecrlf", "false"), ("commit.gpgsign", "false")):
        git(repo, "config", key, value)


def commit_all(repo: Path, message: str = "fixture") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--no-verify", "--allow-empty", "-m", message)


def setUpModule() -> None:
    holder = tempfile.TemporaryDirectory()
    _TEMPLATES.append(holder)
    repo = Path(holder.name).resolve() / "repo"
    repo.mkdir()
    init_repo(repo)
    (repo / "contracts").mkdir()
    (repo / "contracts" / "source.txt").write_bytes(SOURCE_BYTES)
    commit_all(repo)
    _TEMPLATE_REPO.append(repo)


def tearDownModule() -> None:
    for holder in _TEMPLATES:
        holder.cleanup()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def spec_body(*asserts: str) -> str:
    lines = ["def test_contract() -> None:", "    value = compute()", "    expected_from_ledger = load()"]
    lines += list(asserts) if asserts else [LEDGER_ASSERT]
    return "\n".join(lines) + "\n"


class Case(unittest.TestCase):
    """A temporary repository, snapshot and specs directory."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.base = Path(holder.name).resolve()
        self.repo = self.base / "repo"
        shutil.copytree(_TEMPLATE_REPO[0], self.repo)
        self.specs = self.repo / "specs"
        self.specs.mkdir(parents=True)
        self.source = self.repo / "contracts" / "source.txt"
        self.snapshot = self.base / "snapshot.json"

    # -- builders
    def write_snapshot(self, *rows: tuple[str, str]) -> None:
        payload = {"source": "s", "rows": [{"requirement_id": rid, "status": status} for rid, status in rows]}
        self.snapshot.write_text(json.dumps(payload), encoding="utf-8")

    def header(
        self,
        requirements: tuple[str, ...] = (),
        sources: tuple[str, ...] | None = None,
        mutations: tuple[str, ...] = ("drop-the-check",),
    ) -> str:
        if sources is None:
            sources = (f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}",)
        lines = [f"# requirement: {rid}" for rid in requirements]
        lines += [f"# source: {src}" for src in sources]
        lines += [f"# mutation: {name}" for name in mutations]
        return "\n".join(lines) + "\n"

    def write_spec(self, name: str, header: str, body: str | None = None, newline: str = "\n") -> Path:
        text = header + "\n" + (spec_body() if body is None else body)
        path = self.specs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.replace("\n", newline).encode("utf-8"))
        return path

    def good_spec(self, name: str, requirement: str) -> Path:
        return self.write_spec(name, self.header((requirement,)))

    def commit_source(self, relative: str, data: bytes) -> Path:
        """Write a source file and commit it, so that it is a blob at HEAD."""
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        commit_all(self.repo, f"add {relative}")
        return path

    # -- runners
    def argv(self, specs: Path | None = None) -> list[str]:
        return ["--repo", str(self.repo), "--snapshot", str(self.snapshot), "--specs", str(specs or self.specs)]

    def run_gate(self, argv: list[str] | None = None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = contract_gate.main(self.argv() if argv is None else argv)
        return code, out.getvalue(), err.getvalue()

    def red_lines(self) -> list[str]:
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, out + err)
        return out.splitlines()

    def codes(self) -> list[str]:
        return [line.split(" ", 1)[0] for line in self.red_lines()]

    def assert_green(self) -> None:
        code, out, err = self.run_gate()
        self.assertEqual(code, 0, out + err)


class NormalBehaviour(Case):
    def test_two_active_requirements_with_two_good_specs_pass(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.good_spec("test_one.py", "R-1")
        self.good_spec("test_two.py", "R-2")
        code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=2 specs=2 defects=0", ""))

    def test_a_retired_requirement_needs_no_spec(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-0", "retired"))
        self.good_spec("test_one.py", "R-1")
        self.assert_green()

    def test_one_spec_may_declare_several_requirements_sources_and_mutations(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.commit_source("contracts/second.txt", b"other")
        header = self.header(
            ("R-1", "R-2"),
            (f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}", f"contracts/second.txt sha256:{sha(b'other')}"),
            ("m1", "m2"),
        )
        self.write_spec("test_both.py", header)
        self.assert_green()

    def test_specs_are_found_in_nested_directories_only_by_name(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("deep/er/test_nested.py", self.header(("R-1",)))
        self.write_spec("helper.py", "", "assert value == 3\n")
        self.write_spec("test_notes.txt", "", "assert value == 3\n")
        code, out, _ = self.run_gate()
        self.assertEqual((code, out.strip()), (0, "requirements=1 specs=1 defects=0"))

    def test_spec_file_names_are_matched_case_sensitively(self) -> None:
        self.write_snapshot()
        for name in ("Test_x.py", "TEST_y.py", "test_z.PY", "Test_w.Py"):
            self.write_spec(name, "", "assert value == 3\n")
        code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=0 specs=0 defects=0", ""))
        self.write_spec("test_ok.py", "", "assert value == 3\n")
        self.assertEqual(self.codes(), ["LITERAL_EXPECTED"])

    def test_a_spec_without_a_requirement_binds_nothing_and_needs_no_mutation(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        self.write_spec("test_free.py", "# just a note\n")
        self.assert_green()


class DefectCodes(Case):
    def test_no_spec_for_requirement(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.good_spec("test_one.py", "R-1")
        self.assertEqual(self.red_lines(), ["NO_SPEC_FOR_REQUIREMENT R-2: no spec declares this active requirement"])

    def test_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/nope.txt sha256:{sha(b'x')}",)))
        lines = self.red_lines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])

    def test_a_requirement_with_no_source_line_is_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), ()))
        self.assertEqual(self.codes(), ["SOURCE_MISSING"])

    def test_source_digest_mismatch(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{sha(b'changed')}",)))
        lines = self.red_lines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("SOURCE_DIGEST_MISMATCH specs/test_one.py: "), lines[0])

    def test_digest_is_taken_over_the_blob_at_head_without_line_ending_changes(self) -> None:
        self.write_snapshot(("R-1", "active"))
        crlf = b"line one\r\nline two\r\n"
        lf = crlf.replace(b"\r\n", b"\n")
        working = self.commit_source("contracts/crlf.txt", crlf)
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/crlf.txt sha256:{sha(crlf)}",)))
        self.assert_green()
        git(self.repo, "config", "core.autocrlf", "true")
        working.write_bytes(lf)
        self.assert_green()
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/crlf.txt sha256:{sha(lf)}",)))
        self.assertEqual(self.codes(), ["SOURCE_DIGEST_MISMATCH"])

    def test_an_edit_in_the_working_tree_changes_nothing_until_it_is_committed(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        self.source.write_bytes(b"edited after the commit\n")
        self.assert_green()
        commit_all(self.repo, "edit")
        self.assertEqual(self.codes(), ["SOURCE_DIGEST_MISMATCH"])

    def test_a_source_that_is_not_a_blob_at_head_is_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        for name in ("untracked", "staged"):
            with self.subTest(name):
                (self.repo / "contracts" / f"{name}.txt").write_bytes(b"x")
                if name == "staged":
                    git(self.repo, "add", "contracts/staged.txt")
                self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/{name}.txt sha256:{sha(b'x')}",)))
                lines = self.red_lines()
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])

    def test_a_later_wrong_source_is_reported_after_a_correct_first_one(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.commit_source("contracts/second.txt", b"other")
        good = f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}"
        wrong = f"contracts/second.txt sha256:{sha(b'changed')}"
        gone = f"contracts/gone.txt sha256:{sha(b'x')}"
        self.write_spec("test_one.py", self.header(("R-1",), (good, wrong)))
        lines = self.red_lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_DIGEST_MISMATCH specs/test_one.py: line 3: "), lines[0])
        self.write_spec("test_one.py", self.header(("R-1",), (good, good, gone)))
        lines = self.red_lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 4: "), lines[0])
        self.write_spec("test_one.py", self.header(("R-1",), (wrong, good, gone)))
        self.assertEqual(self.codes(), ["SOURCE_DIGEST_MISMATCH", "SOURCE_MISSING"])

    def test_retired_requirement_bound(self) -> None:
        self.write_snapshot(("R-0", "retired"))
        self.good_spec("test_one.py", "R-0")
        self.assertEqual(self.red_lines(), ["RETIRED_REQUIREMENT_BOUND specs/test_one.py: requirement 'R-0' is retired"])

    def test_requirement_absent_from_the_snapshot_is_also_retired_bound(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        self.good_spec("test_ghost.py", "R-9")
        self.assertEqual(
            self.red_lines(), ["RETIRED_REQUIREMENT_BOUND specs/test_ghost.py: requirement 'R-9' is absent from the snapshot"]
        )

    def test_literal_expected(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), spec_body("    assert value == 3"))
        lines = self.red_lines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("LITERAL_EXPECTED specs/test_one.py: line "), lines[0])

    def test_no_mutation(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), mutations=()))
        self.assertEqual(self.red_lines(), ["NO_MUTATION specs/test_one.py: the spec declares a requirement but no mutation"])

    def test_a_spec_with_several_defects_reports_each_on_its_own_line(self) -> None:
        self.write_snapshot(("R-0", "retired"), ("R-2", "active"))
        header = self.header(("R-0",), (f"contracts/gone.txt sha256:{sha(b'x')}",), ())
        self.write_spec("test_bad.py", header, spec_body("    assert value == 3", "    assert value == 'x'"))
        lines = self.red_lines()
        found = sorted(line.split(" ", 1)[0] for line in lines)
        self.assertEqual(
            found,
            sorted(
                [
                    "LITERAL_EXPECTED",
                    "LITERAL_EXPECTED",
                    "NO_MUTATION",
                    "NO_SPEC_FOR_REQUIREMENT",
                    "RETIRED_REQUIREMENT_BOUND",
                    "SOURCE_MISSING",
                ]
            ),
        )
        self.assertEqual(len(lines), len(set(lines)))

    def test_every_line_is_code_subject_detail_and_the_six_codes_are_distinct(self) -> None:
        self.assertEqual(len(set(CODES)), 6)
        self.write_snapshot(("R-0", "retired"), ("R-2", "active"), ("R-3", "active"))
        wrong = f"contracts/source.txt sha256:{sha(b'wrong')}"
        self.write_spec("test_a.py", self.header(("R-0",), (wrong,), ()), spec_body("    assert value == 3"))
        self.write_spec("test_b.py", self.header(("R-3",), (f"contracts/gone.txt sha256:{sha(b'x')}",)))
        lines = self.red_lines()
        self.assertEqual(sorted({line.split(" ", 1)[0] for line in lines}), sorted(CODES))
        for line in lines:
            code, rest = line.split(" ", 1)
            subject, sep, detail = rest.partition(": ")
            self.assertEqual((code in CODES, bool(subject), sep, bool(detail)), (True, True, ": ", True), line)


class LiteralRule(Case):
    def literal_lines(self, *asserts: str) -> list[str]:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), spec_body(*asserts))
        code, out, err = self.run_gate()
        self.assertIn(code, (0, 1), out + err)
        return [line for line in out.splitlines() if line.startswith("LITERAL_EXPECTED")]

    def test_ledger_names_are_not_literals(self) -> None:
        for expr in ("value == expected_from_ledger", "value == ledger['k']", "value == LEDGER.total", "value == [1, other]"):
            with self.subTest(expr):
                self.assertEqual(self.literal_lines(f"    assert {expr}"), [])

    def test_a_comparison_with_a_literal_on_either_side_is_literal(self) -> None:
        for expr in (
            "value == 3",
            "'a' == value",
            "value in (1, 2)",
            "value != 1.5",
            "value == -1",
            "value == b'raw'",
            "value == [1, 2]",
            "value == {'k': 'v'}",
            "value in {1, 2}",
            "value == (1, (2, 'x'))",
            "value == {'k': [1, 2]}",
            "0 < value",
            "value == 3j",
            "value == ()",
        ):
            with self.subTest(expr):
                lines = self.literal_lines(f"    assert {expr}")
                self.assertEqual(len(lines), 1, lines)

    def test_none_true_false_do_not_count(self) -> None:
        for expr in (
            "value is None",
            "value is not None",
            "value == None",
            "value is True",
            "value == False",
            "value in (None, True)",
            "value == (None, 1)",
            "value",
            "not value",
            "isinstance(value, int)",
        ):
            with self.subTest(expr):
                self.assertEqual(self.literal_lines(f"    assert {expr}"), [])

    def test_a_message_is_not_the_comparison(self) -> None:
        self.assertEqual(self.literal_lines("    assert value == expected_from_ledger, 'the value was 3'"), [])

    def test_a_computed_string_is_not_a_literal(self) -> None:
        self.assertEqual(self.literal_lines("    assert value == f'{expected_from_ledger}'"), [])

    def test_literals_hidden_in_boolean_logic_or_nested_scopes_are_found(self) -> None:
        for expr in ("value == expected_from_ledger and value != 3", "not (value == 3)"):
            with self.subTest(expr):
                self.assertEqual(len(self.literal_lines(f"    assert {expr}")), 1)
        body = "class T:\n    def test_m(self):\n        assert 7 == compute()\n"
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), body)
        self.assertEqual(self.codes(), ["LITERAL_EXPECTED"])

    def test_each_literal_assert_is_its_own_line_with_its_line_number(self) -> None:
        lines = self.literal_lines("    assert value == 3", LEDGER_ASSERT, "    assert value == 'x'")
        self.assertEqual(len(lines), 2)
        self.assertNotEqual(lines[0], lines[1])
        written = (self.specs / "test_one.py").read_text(encoding="utf-8").splitlines()
        first = written.index("    assert value == 3") + 1
        second = written.index("    assert value == 'x'") + 1
        self.assertIn(f"line {first}:", lines[0])
        self.assertIn(f"line {second}:", lines[1])

    def test_a_syntax_error_is_a_red_naming_the_line_and_never_a_traceback(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), "def test_x(:\n    pass\n")
        lines = self.red_lines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("LITERAL_EXPECTED specs/test_one.py: syntax error line "), lines[0])
        completed = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertNotIn("Traceback", completed.stdout + completed.stderr)

    def test_a_spec_with_a_null_byte_is_a_red_not_a_traceback(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), "x = 1\x00\n")
        self.assertEqual(self.codes(), ["LITERAL_EXPECTED"])

    def only_red_line(self, assertion: str) -> str:
        """Run one assertion through the real gate: exit 1, one LITERAL_EXPECTED line, no fault."""
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), spec_body(f"    assert {assertion}"))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertNotIn("Traceback", out + err)
        self.assertNotIn("TOOL_FAULT", err)
        lines = out.splitlines()
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("LITERAL_EXPECTED specs/test_one.py: line "), lines[0])
        return lines[0]

    def test_an_assert_behind_a_deep_chain_of_nots_is_a_red_never_a_fault(self) -> None:
        for count in (900, 1500):
            for expression in ("value == 3", "value == expected_from_ledger"):
                with self.subTest(count=count, expression=expression):
                    line = self.only_red_line("not " * count + expression)
                    self.assertIn("cannot be analysed", line)
                    self.assertLess(len(line), 300, len(line))

    def test_a_display_nested_beyond_the_budget_is_a_red_never_a_fault(self) -> None:
        line = self.only_red_line("value == " + "[" * 150 + "1" + "]" * 150)
        self.assertIn("cannot be analysed", line)
        self.assertLess(len(line), 300, len(line))

    def test_a_chain_of_nots_within_the_budget_is_analysed(self) -> None:
        self.assertIn("compares with a literal", self.only_red_line("not " * 10 + "value == 3"))
        self.assertEqual(self.literal_lines("    assert " + "not " * 10 + "value == expected_from_ledger"), [])

    def test_a_literal_too_large_to_render_is_a_red_with_the_source_text_truncated(self) -> None:
        for expression in ("value == 0x" + "f" * 4000, "value == '" + "x" * 5000 + "'", "value == b'" + "y" * 5000 + "'"):
            with self.subTest(expression[:20]):
                line = self.only_red_line(expression)
                self.assertTrue(line.endswith("..."), line)
                self.assertLess(len(line), 300, len(line))
                self.assertIn("value == ", line)

    def test_the_detail_is_the_source_text_of_the_assertion(self) -> None:
        line = self.only_red_line("value == 0xFF")
        self.assertTrue(line.endswith("value == 0xFF"), line)

    def test_an_analysis_fault_in_the_recursion_is_a_red_not_a_tool_fault(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)))
        with mock.patch.object(contract_gate, "compares_with_literal", side_effect=RecursionError("deep")):
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertTrue(out.startswith("LITERAL_EXPECTED specs/test_one.py: line "), out)
        self.assertNotIn("TOOL_FAULT", err)


class SnapshotAndFaults(Case):
    def expect(self, code: int, argv: list[str] | None = None) -> str:
        got, out, err = self.run_gate(argv)
        self.assertEqual(got, code, out + err)
        self.assertNotIn("Traceback", out + err)
        return out + err

    def test_unreadable_snapshot_is_exit_2(self) -> None:
        self.assertIn("snapshot.json", self.expect(2))

    def test_a_directory_as_snapshot_is_exit_2(self) -> None:
        self.snapshot.mkdir()
        self.expect(2)

    def test_snapshot_that_is_not_json_is_exit_3_with_the_reason(self) -> None:
        self.snapshot.write_text("not json {", encoding="utf-8")
        self.assertIn("is not a snapshot", self.expect(3))

    def test_snapshot_that_is_not_utf8_is_exit_3(self) -> None:
        self.snapshot.write_bytes(b"\xff\xfe\x00")
        self.assertIn("is not a snapshot", self.expect(3))

    def test_snapshot_shapes_that_are_not_r4_7_snapshots_are_exit_3(self) -> None:
        shapes: dict[str, object] = {
            "list": [],
            "no rows": {"source": "s"},
            "rows not a list": {"rows": {}},
            "row not an object": {"rows": ["R-1"]},
            "no requirement_id": {"rows": [{"status": "active"}]},
            "no status": {"rows": [{"requirement_id": "R-1"}]},
            "empty id": {"rows": [{"requirement_id": "", "status": "active"}]},
            "blank id": {"rows": [{"requirement_id": "  ", "status": "active"}]},
            "id not a string": {"rows": [{"requirement_id": 1, "status": "active"}]},
            "unknown status": {"rows": [{"requirement_id": "R-1", "status": "draft"}]},
            "null status": {"rows": [{"requirement_id": "R-1", "status": None}]},
            "duplicate id": {"rows": [{"requirement_id": "R", "status": "active"}] * 2},
            "id with a trailing newline": {"rows": [{"requirement_id": "R-1\n", "status": "active"}]},
            "id with an embedded newline": {"rows": [{"requirement_id": "R\n-1", "status": "active"}]},
            "id with a carriage return": {"rows": [{"requirement_id": "R-1\r", "status": "active"}]},
            "id with a surrounding space": {"rows": [{"requirement_id": " R-1", "status": "active"}]},
            "id with U+2028": {"rows": [{"requirement_id": "R-\u2028", "status": "active"}]},
            "id with NEL": {"rows": [{"requirement_id": "R-\u0085", "status": "active"}]},
            "id with a control character": {"rows": [{"requirement_id": "R-\u0001", "status": "active"}]},
            "id with a lone surrogate": {"rows": [{"requirement_id": "R-\ud800", "status": "active"}]},
            "id with a letter outside ASCII": {"rows": [{"requirement_id": "R-\u00e9", "status": "active"}]},
            "id with a space inside": {"rows": [{"requirement_id": "R 1", "status": "active"}]},
            "id longer than 128 characters": {"rows": [{"requirement_id": "R" * 129, "status": "active"}]},
        }
        for name, shape in shapes.items():
            with self.subTest(name):
                self.snapshot.write_text(json.dumps(shape), encoding="utf-8")
                self.assertIn("is not a snapshot", self.expect(3))

    def test_ids_in_the_character_set_are_accepted_and_compared_exactly(self) -> None:
        longest = "R" * 128
        self.write_snapshot((longest, "active"), ("A.b_c:d-e/f", "active"), ("Req-1", "active"))
        self.good_spec("test_a.py", longest)
        self.good_spec("test_b.py", "A.b_c:d-e/f")
        self.good_spec("test_c.py", "req-1")
        self.assertEqual(sorted(self.codes()), ["NO_SPEC_FOR_REQUIREMENT", "RETIRED_REQUIREMENT_BOUND"])

    def test_empty_rows_is_a_valid_snapshot_and_every_spec_binds_an_absent_requirement(self) -> None:
        self.write_snapshot()
        code, out, _ = self.run_gate()
        self.assertEqual((code, out.strip()), (0, "requirements=0 specs=0 defects=0"))
        self.good_spec("test_one.py", "R-1")
        self.assertEqual(self.codes(), ["RETIRED_REQUIREMENT_BOUND"])

    def test_empty_specs_directory_makes_every_active_requirement_red(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"), ("R-0", "retired"))
        lines = self.red_lines()
        self.assertEqual([line.split(":")[0] for line in lines], ["NO_SPEC_FOR_REQUIREMENT R-1", "NO_SPEC_FOR_REQUIREMENT R-2"])

    def test_specs_not_a_directory_is_exit_2(self) -> None:
        self.write_snapshot()
        self.expect(2, self.argv(self.repo / "missing"))
        self.expect(2, self.argv(self.source))

    def test_repo_not_a_directory_is_exit_2(self) -> None:
        self.write_snapshot()
        argv = self.argv()
        argv[1] = str(self.base / "no-repo")
        self.expect(2, argv)

    def test_specs_outside_the_repository_is_a_usage_error(self) -> None:
        self.write_snapshot()
        outside = self.base / "elsewhere"
        outside.mkdir()
        self.expect(3, self.argv(outside))

    def test_specs_in_a_sibling_sharing_the_repository_prefix_is_a_usage_error(self) -> None:
        self.write_snapshot()
        sibling = self.base / "repo-evil"
        sibling.mkdir()
        (sibling / "test_x.py").write_text("x = 1\n", encoding="utf-8")
        self.expect(3, self.argv(sibling))

    def test_specs_may_be_the_repository_root(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        code, out, _ = self.run_gate(self.argv(self.repo))
        self.assertEqual((code, out.strip()), (0, "requirements=1 specs=1 defects=0"))

    def test_a_url_source_is_exit_2_source_unservable_never_a_red(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        url = "https://example.invalid/page"
        self.write_spec("test_url.py", self.header(("R-1",), (f"{url} sha256:{sha(b'x')}",)))
        got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn("SOURCE_UNSERVABLE", err)
        self.assertIn("specs/test_url.py", err)
        self.assertNotIn("NO_SPEC_FOR_REQUIREMENT", err)

    def test_a_fault_beats_a_red_found_elsewhere(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a_red.py", self.header(("R-9",)))
        self.write_spec("test_b_url.py", self.header(("R-1",), ("http://example.invalid/x sha256:" + sha(b"x"),)))
        got, out, _ = self.run_gate()
        self.assertEqual((got, out), (2, ""))

    def test_an_unreadable_spec_file_is_exit_2_naming_the_path(self) -> None:
        self.write_snapshot(("R-1", "active"))
        locked = self.good_spec("test_locked.py", "R-1")
        original = Path.read_bytes

        def deny(path: Path) -> bytes:
            if path.name == "test_locked.py":
                raise PermissionError(13, "Permission denied", str(path))
            return original(path)

        with mock.patch.object(Path, "read_bytes", deny):
            got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn(locked.name, err)
        self.assertNotIn("Traceback", err)

    def test_git_failing_to_serve_a_source_is_exit_2(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        failed = subprocess.CompletedProcess([], 128, b"", b"fatal: the object store is broken")
        with mock.patch.object(contract_gate.subprocess, "run", return_value=failed):
            got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn("the object store is broken", err)
        self.assertNotIn("Traceback", err)

    def test_a_missing_git_executable_is_exit_2(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        with mock.patch.object(contract_gate.subprocess, "run", side_effect=FileNotFoundError(2, "git")):
            got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn("cannot run git", err)

    def test_a_repository_without_a_commit_is_exit_2(self) -> None:
        fresh = self.base / "fresh"
        fresh.mkdir()
        init_repo(fresh)
        self.repo, self.specs = fresh, fresh / "specs"
        self.specs.mkdir()
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn("TOOL_FAULT", err)

    def test_a_directory_that_is_not_a_repository_is_exit_2(self) -> None:
        plain = self.base / "plain"
        (plain / "specs").mkdir(parents=True)
        self.repo, self.specs = plain, plain / "specs"
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.base)}):
            got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn("TOOL_FAULT", err)

    def test_a_repository_that_serves_no_source_needs_no_git(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", "# requirement: R-1\n# mutation: m\n")
        with mock.patch.object(contract_gate.subprocess, "run", side_effect=AssertionError("git was run")):
            self.assertEqual(self.codes(), ["SOURCE_MISSING"])

    def test_an_unexpected_error_is_exit_2_without_a_traceback(self) -> None:
        self.write_snapshot()
        with mock.patch.object(contract_gate, "run", side_effect=RuntimeError("boom")):
            got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertIn("boom", err)
        self.assertNotIn("Traceback", err)

    def test_a_red_is_exit_1_and_a_fault_is_exit_2_through_the_real_command_line(self) -> None:
        self.write_snapshot(("R-1", "active"))
        red = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual(red.returncode, 1)
        self.assertTrue(red.stdout.startswith("NO_SPEC_FOR_REQUIREMENT R-1: "))
        self.snapshot.unlink()
        fault = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual((fault.returncode, fault.stdout), (2, ""))
        self.assertNotIn("Traceback", fault.stderr)

    def test_bad_arguments_are_exit_3_with_a_usage_line(self) -> None:
        self.write_snapshot()
        good = self.argv()
        bad: list[list[str]] = [
            [],
            good[:4],
            [*good, "--extra"],
            [*good, "stray"],
            [*good, "--repo", str(self.repo)],
            ["--repo", "--snapshot", str(self.snapshot), "--specs", str(self.specs)],
            ["--repo", str(self.repo), "--snapshot", str(self.snapshot), "--specs"],
            ["--repo", "", "--snapshot", str(self.snapshot), "--specs", str(self.specs)],
            ["--bogus", "x", *good],
        ]
        for argv in bad:
            with self.subTest(argv):
                self.assertIn("usage:", self.expect(3, argv))

    def test_equals_form_of_options_is_accepted(self) -> None:
        self.write_snapshot()
        argv = [f"--repo={self.repo}", f"--snapshot={self.snapshot}", f"--specs={self.specs}"]
        self.expect(0, argv)


class Declarations(Case):
    def test_declarations_after_the_first_code_line_are_ignored(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        header = self.header(("R-1",))
        late = "# requirement: R-2\n# mutation: late\n# source: contracts/nope.txt sha256:" + sha(b"x") + "\n"
        self.write_spec("test_one.py", header, "import os\n" + late + spec_body())
        self.assertEqual(self.red_lines(), ["NO_SPEC_FOR_REQUIREMENT R-2: no spec declares this active requirement"])

    def test_a_late_mutation_does_not_satisfy_no_mutation(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), mutations=()), "import os\n# mutation: late\n" + spec_body())
        self.assertEqual(self.codes(), ["NO_MUTATION"])

    def test_a_docstring_before_the_comments_ends_the_header(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", '"""doc"""\n' + self.header(("R-1",)), spec_body())
        self.assertEqual(self.codes(), ["NO_SPEC_FOR_REQUIREMENT"])

    def test_a_blank_line_ends_the_header(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", "# requirement: R-1\n\n# mutation: m\n", spec_body())
        self.assertEqual(sorted(self.codes()), ["NO_MUTATION", "SOURCE_MISSING"])

    def test_crlf_spec_files_read_the_same(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), newline="\r\n")
        self.assert_green()
        self.write_spec("test_one.py", self.header(("R-1",), mutations=()), newline="\r\n")
        self.assertEqual(self.codes(), ["NO_MUTATION"])

    def test_a_bom_and_lone_cr_line_breaks_are_read(self) -> None:
        self.write_snapshot(("R-1", "active"))
        text = "\ufeff" + self.header(("R-1",)).replace("\n", "\r") + "\r" + spec_body().replace("\n", "\r")
        (self.specs / "test_one.py").write_bytes(text.encode("utf-8"))
        self.assert_green()

    def test_requirement_ids_are_case_sensitive(self) -> None:
        self.write_snapshot(("Req-1", "active"))
        self.good_spec("test_one.py", "req-1")
        self.assertEqual(sorted(self.codes()), ["NO_SPEC_FOR_REQUIREMENT", "RETIRED_REQUIREMENT_BOUND"])

    def test_surrounding_whitespace_is_stripped_from_declared_values(self) -> None:
        self.write_snapshot(("R-1", "active"))
        header = (
            "#   requirement:   R-1   \n"
            f"#\tsource:\tcontracts/source.txt   sha256:{sha(SOURCE_BYTES)}  \n"
            "#  mutation:   drop  \n"
        )
        self.write_spec("test_one.py", header)
        self.assert_green()

    def test_empty_declaration_values_are_reported_with_the_code_of_their_clause(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_req.py", "# requirement:   \n")
        self.write_spec("test_src.py", self.header(("R-1",), ("   ",)))
        self.write_spec("test_mut.py", self.header(("R-1",), mutations=("  ",)))
        lines = self.red_lines()
        by_spec = {line.split(" ")[1].rstrip(":"): line.split(" ")[0] for line in lines if "specs/" in line.split(" ")[1]}
        self.assertEqual(by_spec["specs/test_req.py"], "RETIRED_REQUIREMENT_BOUND")
        self.assertEqual(by_spec["specs/test_src.py"], "SOURCE_MISSING")
        self.assertEqual(by_spec["specs/test_mut.py"], "NO_MUTATION")
        self.assertEqual(len([line for line in lines if "specs/test_mut.py" in line]), 1)
        self.assertTrue(all("line 1:" in line for line in lines if "specs/test_req.py" in line))

    def test_malformed_digests_are_source_missing_naming_the_line(self) -> None:
        good = sha(SOURCE_BYTES)
        cases = {
            "63 characters": good[:-1],
            "65 characters": good + "0",
            "upper case": good.upper(),
            "non hex": "g" * 64,
            "empty": "",
        }
        for name, digest in cases.items():
            with self.subTest(name):
                self.write_snapshot(("R-1", "active"))
                self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{digest}",)))
                lines = self.red_lines()
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])

    def test_a_source_without_a_digest_or_without_a_path_is_source_missing(self) -> None:
        for value in ("contracts/source.txt", f"sha256:{sha(SOURCE_BYTES)}", "contracts/source.txt sha256"):
            with self.subTest(value):
                self.write_snapshot(("R-1", "active"))
                self.write_spec("test_one.py", self.header(("R-1",), (value,)))
                self.assertEqual(self.codes(), ["SOURCE_MISSING"])

    def test_only_the_three_lower_case_keys_are_declarations(self) -> None:
        self.write_snapshot(("R-1", "active"))
        free_text = (
            "# SPDX-License-Identifier: MIT\n"
            "# Note: see the design page\n"
            "# mutaton: a typo is free text\n"
            "# Requirement: R-9\n"
            "# REQUIREMENT: R-8\n"
            "# Source: contracts/nope.txt sha256:abc\n"
            "# Mutation:\n"
            "# requirements: R-7\n"
            "# requirement R-6\n"
        )
        self.write_spec("test_one.py", self.header(("R-1",)) + free_text)
        self.assert_green()

    def test_an_upper_case_key_does_not_satisfy_a_declaration(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", "# Requirement: R-1\n# Source: x\n# Mutation: m\n")
        self.assertEqual(self.codes(), ["NO_SPEC_FOR_REQUIREMENT"])

    def test_free_comments_and_a_shebang_in_the_header_are_not_declarations(self) -> None:
        self.write_snapshot(("R-1", "active"))
        header = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n# Spec for the login page.\n" + self.header(("R-1",))
        self.write_spec("test_one.py", header)
        self.assert_green()

    def test_duplicate_declarations_of_one_requirement_report_once(self) -> None:
        self.write_snapshot(("R-0", "retired"))
        self.write_spec("test_one.py", self.header(("R-0", "R-0")))
        self.assertEqual(self.codes(), ["RETIRED_REQUIREMENT_BOUND"])


class SourcePaths(Case):
    def declare(self, path: str, digest: str | None = None) -> list[str]:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), (f"{path} sha256:{digest or sha(SOURCE_BYTES)}",)))
        code, out, err = self.run_gate()
        self.assertIn(code, (0, 1), out + err)
        return [line for line in out.splitlines() if not line.startswith("requirements=")]

    def assert_missing(self, path: str) -> None:
        lines = self.declare(path)
        self.assertEqual(len(lines), 1, (path, lines))
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2"), lines[0])

    def test_dot_slash_and_backslashes_resolve_the_same(self) -> None:
        for path in (
            "contracts/source.txt",
            "./contracts/source.txt",
            "contracts\\source.txt",
            ".\\contracts\\source.txt",
            "contracts//source.txt",
            "contracts/./source.txt",
            "specs/../contracts/source.txt",
        ):
            with self.subTest(path):
                self.assertEqual(self.declare(path), [])

    def test_dot_dot_escaping_the_repository_is_source_missing(self) -> None:
        for path in (
            "../repo/contracts/source.txt",
            "../contracts/source.txt",
            "..\\contracts\\source.txt",
            "../source.txt",
            "contracts/../../x",
            "contracts/../../contracts/source.txt",
            "..\\repo\\contracts\\source.txt",
        ):
            with self.subTest(path):
                self.assert_missing(path)

    def test_a_sibling_directory_sharing_the_repository_prefix_is_not_inside_it(self) -> None:
        sibling = self.base / "repo2"
        sibling.mkdir()
        (sibling / "f.txt").write_bytes(SOURCE_BYTES)
        self.assert_missing("../repo2/f.txt")
        self.assert_missing("..\\repo2\\f.txt")

    def test_the_repository_root_and_directories_are_not_sources(self) -> None:
        for path in (".", "./", "contracts", "contracts/", "contracts\\", "specs/.."):
            with self.subTest(path):
                self.assert_missing(path)

    def test_a_trailing_slash_on_a_file_is_refused(self) -> None:
        self.assert_missing("contracts/source.txt/")

    def test_one_extra_or_missing_character_is_not_found(self) -> None:
        self.assert_missing("contracts/source.txtx")
        self.assert_missing("contracts/source.tx")
        self.assert_missing("contract/source.txt")

    def test_a_case_variant_is_not_found_on_any_platform(self) -> None:
        self.assert_missing("Contracts/source.txt")
        self.assert_missing("contracts/SOURCE.TXT")

    def test_an_absolute_path_is_refused_even_when_the_file_exists(self) -> None:
        self.assert_missing(str(self.source))
        self.assert_missing(self.source.as_posix())
        self.assert_missing("/contracts/source.txt")
        self.assert_missing("C:contracts/source.txt")

    def test_an_empty_path_is_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", "# requirement: R-1\n# source: sha256:" + sha(SOURCE_BYTES) + "\n# mutation: m\n")
        self.assertEqual(self.codes(), ["SOURCE_MISSING"])

    def test_a_path_through_a_file_is_not_found(self) -> None:
        self.assert_missing("contracts/source.txt/inner")

    def test_a_tracked_symbolic_link_is_not_a_regular_file(self) -> None:
        link_target = self.base / "outside.txt"
        link_target.write_bytes(SOURCE_BYTES)
        identifier = subprocess.run(
            ["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
            input=str(link_target).encode("utf-8"),
            capture_output=True,
            env={**os.environ, **GIT_ENVIRONMENT},
            check=True,
        ).stdout.decode("ascii").strip()
        git(self.repo, "update-index", "--add", "--cacheinfo", f"120000,{identifier},contracts/link.txt")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "link")
        lines = self.declare("contracts/link.txt")
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2"), lines[0])
        self.assertIn("not a regular file", lines[0])

    def test_a_directory_at_head_is_not_a_source(self) -> None:
        for path in ("contracts", "specs/.."):
            with self.subTest(path):
                self.assert_missing(path)

    def test_a_control_character_in_a_source_path_is_source_missing_not_a_fault(self) -> None:
        for path in ("contracts/so\x00urce.txt", "contracts/so\x01urce.txt", "contracts/so\x7furce.txt", "contracts/so\x85urce.txt"):
            with self.subTest(path):
                self.write_snapshot(("R-1", "active"))
                self.write_spec("test_one.py", self.header(("R-1",), (f"{path} sha256:{sha(SOURCE_BYTES)}",)))
                code, out, err = self.run_gate()
                self.assertEqual(code, 1, out + err)
                self.assertTrue(out.startswith("SOURCE_MISSING specs/test_one.py: line 2"), out)
                self.assertEqual(len(out.splitlines()), 2 if path == "contracts/so\x00urce.txt" else 1, out)

    def test_a_glob_character_in_a_source_path_matches_only_itself(self) -> None:
        self.assert_missing("contracts/*")
        self.assert_missing("contracts/sourc?.txt")

    def test_a_source_in_a_subdirectory_with_spaces_resolves(self) -> None:
        self.commit_source("my docs/a b.txt", SOURCE_BYTES)
        self.assertEqual(self.declare("my docs/a b.txt"), [])


class Streams(Case):
    def test_an_unencodable_character_in_a_red_does_not_change_the_exit(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", "# requirement: R-\u0e01\n# mutation: m\n")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *self.argv()],
            capture_output=True,
            env={"PYTHONIOENCODING": "cp950", "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "PATH": ""},
        )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn(b"RETIRED_REQUIREMENT_BOUND", completed.stdout)

    def test_the_summary_is_on_stdout_at_exit_0(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        code, out, err = self.run_gate()
        self.assertEqual((code, out, err), (0, "requirements=1 specs=1 defects=0\n", ""))

    def test_the_summary_is_on_stderr_at_exit_1_and_defect_lines_on_stdout(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(err, "requirements=2 specs=0 defects=2\n")
        self.assertEqual(len(out.splitlines()), 2)
        self.assertNotIn("requirements=", out)

    def test_the_same_streams_through_the_real_command_line(self) -> None:
        self.write_snapshot(("R-1", "active"))
        red = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual((red.returncode, red.stderr), (1, "requirements=1 specs=0 defects=1\n"))
        self.good_spec("test_one.py", "R-1")
        green = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual((green.returncode, green.stdout, green.stderr), (0, "requirements=1 specs=1 defects=0\n", ""))


class OneLinePerDefect(Case):
    HOSTILE = ("a\nb", "a\rb", "a\r\nb", "a\u2028b", "a\u2029b", "a\x85b", "a\x00b", "a\x1bb", "a\x0bb", "a\x0cb", "a\x7fb", "a\udc80b")

    def test_a_rendered_defect_is_one_line_whatever_its_subject_or_detail(self) -> None:
        for hostile in self.HOSTILE:
            for subject, detail in ((hostile, "detail"), ("subject", hostile), (hostile, hostile)):
                with self.subTest(hostile=hostile, subject=subject == hostile, detail=detail == hostile):
                    rendered = contract_gate.Defect("NO_MUTATION", subject, detail).render()
                    self.assertEqual(len(rendered.splitlines()), 1, repr(rendered))
                    self.assertTrue(rendered.isprintable(), repr(rendered))
                    self.assertTrue(rendered.startswith("NO_MUTATION "))

    def test_printable_text_is_kept_as_it_is(self) -> None:
        self.assertEqual(contract_gate.escape_text("R-\u0e01 a b/c.py"), "R-\u0e01 a b/c.py")
        self.assertEqual(contract_gate.escape_text("a\nb"), "a\\nb")
        self.assertEqual(contract_gate.escape_text("a\udc80b"), "a\\udc80b")

    def test_a_spec_name_with_line_separator_characters_stays_one_line(self) -> None:
        self.write_snapshot()
        name = "test_a\u2028b\u0085c\u2029d.py"
        try:
            self.write_spec(name, "", "assert value == 3\n")
        except OSError:
            self.skipTest("this file system refuses the name")
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(out.splitlines()), 1, repr(out))
        self.assertEqual(out.count("\n"), 1, repr(out))
        self.assertIn("\\u2028", out)
        self.assertIn("\\x85", out)

    def test_a_declared_value_with_a_separator_character_stays_one_line(self) -> None:
        self.write_snapshot(("R-1", "active"))
        header = "# requirement: R-1\u2028forged\x0b\n# source: contracts/a\u2028b.txt sha256:" + sha(b"x") + "\n# mutation: m\u0085n\n"
        self.write_spec("test_one.py", header)
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(out.splitlines()), len(out.split("\n")) - 1, repr(out))
        self.assertTrue(all(line.split(" ", 1)[0] in CODES for line in out.splitlines()), repr(out))

    def test_a_source_digest_with_hostile_text_stays_one_line(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), ("contracts/source.txt sha256:ab\u2028cd",)))
        code, out, _ = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(len(out.splitlines()), 1, repr(out))


class ReadmeNamesEveryScript(unittest.TestCase):
    NUMBER_WORDS = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8}

    def setUp(self) -> None:
        self.readme = (_SCRIPTS / "README.md").read_text(encoding="utf-8")
        self.introduction = self.readme.split("\n## ", 1)[0]
        self.scripts = sorted(path.name for path in _SCRIPTS.glob("*.py"))

    def test_the_introduction_names_every_script_in_the_directory(self) -> None:
        self.assertIn("contract_gate.py", self.scripts)
        for name in self.scripts:
            with self.subTest(name):
                self.assertIn(name, self.introduction)

    def test_the_introduction_counts_the_scripts_that_exist(self) -> None:
        word = self.introduction.split("# Gate scripts", 1)[1].split()[0]
        self.assertEqual(self.NUMBER_WORDS.get(word), len(self.scripts), word)

    def test_the_unexpected_error_rule_names_every_script(self) -> None:
        paragraphs = [text for text in self.introduction.split("\n\n") if "unexpected error" in text]
        self.assertEqual(len(paragraphs), 1, paragraphs)
        for name in self.scripts:
            with self.subTest(name):
                self.assertIn(name, paragraphs[0])


if __name__ == "__main__":
    unittest.main()
