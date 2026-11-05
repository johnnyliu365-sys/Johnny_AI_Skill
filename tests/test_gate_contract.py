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
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zlib
from collections.abc import Callable
from pathlib import Path
from typing import IO
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


class GitCall:
    """One git child as the gate started it; `queries` are the lines the gate wrote to its standard input."""

    def __init__(self, command: list[str], env: dict[str, str] | None) -> None:
        self.command = command
        self.env = env
        self.queries: list[bytes] = []


HANG = b"<hang until killed>"


class SpyStdin:
    def __init__(self, process: "SpyProcess") -> None:
        self.process = process

    def write(self, data: bytes) -> int:
        process = self.process
        query = data[:-1] if data.endswith(b"\n") else data
        process.call.queries.append(query)
        if process.spy.on_query is not None:
            process.spy.on_query(query)
        reply = process.spy.replies(query) if process.spy.replies is not None else None
        process.fake = reply is not None
        process.hang = reply == HANG
        if reply is not None:
            process.pending.extend(b"" if reply == HANG else reply)
            return len(data)
        if process.real is not None and process.real.stdin is not None:
            return process.real.stdin.write(data)
        return len(data)

    def flush(self) -> None:
        if self.process.real is not None and self.process.real.stdin is not None:
            self.process.real.stdin.flush()

    def close(self) -> None:
        if self.process.real is not None and self.process.real.stdin is not None:
            self.process.real.stdin.close()


class SpyStdout:
    def __init__(self, process: "SpyProcess") -> None:
        self.process = process

    def readline(self) -> bytes:
        process = self.process
        if process.hang and not process.pending:
            process.killed.wait(10)
            return b""
        if process.fake or process.real is None or process.real.stdout is None:
            end = process.pending.find(b"\n")
            size = len(process.pending) if end < 0 else end + 1
            taken = bytes(process.pending[:size])
            del process.pending[:size]
            return taken
        return process.real.stdout.readline()

    def read(self, size: int = -1) -> bytes:
        process = self.process
        if process.fake or process.real is None or process.real.stdout is None:
            count = len(process.pending) if size < 0 else min(size, len(process.pending))
            taken = bytes(process.pending[:count])
            del process.pending[:count]
            return taken
        return process.real.stdout.read(size)

    def close(self) -> None:
        if self.process.real is not None and self.process.real.stdout is not None:
            self.process.real.stdout.close()


class SpyProcess:
    """Stands in for a `git cat-file --batch` child: the real one, or one that fails at once."""

    def __init__(self, spy: "GitSpy", call: GitCall, real: "subprocess.Popen[bytes] | None", failure: bytes = b"") -> None:
        self.spy = spy
        self.call = call
        self.real = real
        self.pending = bytearray()
        self.fake = real is None
        self.hang = False
        self.killed = threading.Event()
        self.stdin = SpyStdin(self)
        self.stdout = SpyStdout(self)
        self.stderr: io.BytesIO | IO[bytes] | None = io.BytesIO(failure) if real is None else real.stderr
        self.failed = real is None

    def kill(self) -> None:
        self.killed.set()
        if self.real is not None:
            self.real.kill()

    def poll(self) -> int | None:
        return 128 if self.real is None else self.real.poll()

    def wait(self, timeout: float | None = None) -> int:
        return 128 if self.real is None else self.real.wait(timeout)


class GitSpy:
    """Stands in for subprocess.run and subprocess.Popen: records every git child, runs it for real unless told to fail or lie.

    `replies(query)` may answer a line of the `cat-file --batch` standard input with bytes (or HANG)
    instead of the real answer; `on_query(query)` is called before each line is answered.
    """

    def __init__(
        self,
        fail_on: str | None = None,
        answers: dict[str, bytes] | None = None,
        replies: Callable[[bytes], bytes | None] | None = None,
        on_query: Callable[[bytes], None] | None = None,
        fail_start: bool = False,
    ) -> None:
        self.calls: list[GitCall] = []
        self.processes: list[SpyProcess] = []
        self.fail_on = fail_on
        self.answers = answers or {}
        self.replies = replies
        self.on_query = on_query
        self.fail_start = fail_start
        self.real = subprocess.run
        self.real_popen = subprocess.Popen

    def __call__(self, command: list[str], **kwargs: object) -> "subprocess.CompletedProcess[bytes]":
        env = kwargs.get("env")
        self.calls.append(GitCall(list(command), env if isinstance(env, dict) else None))
        if self.fail_on is not None and self.fail_on in command:
            return subprocess.CompletedProcess(command, 128, b"", b"fatal: injected failure")
        for flag, answer in self.answers.items():
            if flag in command:
                return subprocess.CompletedProcess(command, 0, answer, b"")
        return self.real(command, **kwargs)

    def popen(self, command: list[str], **kwargs: object) -> object:
        if "cat-file" not in command:
            return self.real_popen(command, **kwargs)
        env = kwargs.get("env")
        call = GitCall(list(command), env if isinstance(env, dict) else None)
        self.calls.append(call)
        if self.fail_start:
            raise OSError(2, "injected failure to start git")
        if self.fail_on is not None and self.fail_on in command:
            process = SpyProcess(self, call, None, b"fatal: injected failure")
        else:
            process = SpyProcess(self, call, self.real_popen(command, **kwargs))
        self.processes.append(process)
        return process

    def patched(self) -> "contextlib.AbstractContextManager[object]":
        return mock.patch.multiple(contract_gate.subprocess, run=self, Popen=self.popen)

    def lookups(self) -> list[GitCall]:
        return [call for call in self.calls if "cat-file" in call.command]

    def queries(self) -> list[bytes]:
        return [query for call in self.lookups() for query in call.queries]

    def alive(self) -> list[SpyProcess]:
        return [process for process in self.processes if process.poll() is None]


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

    def declare_many(self, *paths: str) -> list[str]:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), tuple(f"{path} sha256:{sha(SOURCE_BYTES)}" for path in paths)))
        code, out, err = self.run_gate()
        self.assertIn(code, (0, 1), out + err)
        return [line for line in out.splitlines() if not line.startswith("requirements=")]


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

    def test_a_digest_equal_but_for_late_characters_is_a_mismatch(self) -> None:
        self.write_snapshot(("R-1", "active"))
        real = sha(SOURCE_BYTES)
        for position in (8, 9, 31, 32, 62, 63):
            other = "0" if real[position] != "0" else "1"
            declared = real[:position] + other + real[position + 1 :]
            with self.subTest(position=position):
                self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{declared}",)))
                lines = self.red_lines()
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("SOURCE_DIGEST_MISMATCH specs/test_one.py: line 2: "), lines[0])
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{real}",)))
        self.assert_green()

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

    def test_a_chained_comparison_is_literal_when_any_operand_of_it_is(self) -> None:
        for expr in (
            "value < expected_from_ledger < 3",
            "value == expected_from_ledger == 'x'",
            "value < other < 3 < more",
            "value in expected_from_ledger == (1, 2)",
            "value is expected_from_ledger != 5",
            "value < expected_from_ledger <= other < 2.5",
            "value < other < more < b'raw'",
        ):
            with self.subTest(expr):
                self.assertEqual(len(self.literal_lines(f"    assert {expr}")), 1)
        for expr in (
            "value < expected_from_ledger < other",
            "value == expected_from_ledger == other == None",
            "value is expected_from_ledger is not None",
            "value < other < more < expected_from_ledger",
        ):
            with self.subTest(expr):
                self.assertEqual(self.literal_lines(f"    assert {expr}"), [])

    def test_a_signed_boolean_or_none_is_not_a_signed_number(self) -> None:
        for expr in (
            "value == -True",
            "value == +True",
            "value == -False",
            "-True == value",
            "value in (-True, +False)",
            "value == [-True]",
            "value == (1, -True)",
            "value == -None",
            "value == -value",
        ):
            with self.subTest(expr):
                self.assertEqual(self.literal_lines(f"    assert {expr}"), [])
        for expr in ("value == -1", "value == +1", "value == -1.5", "value == -3j", "value in (-1, +2)", "value == -(1)"):
            with self.subTest(expr):
                self.assertEqual(len(self.literal_lines(f"    assert {expr}")), 1)

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

    def test_a_url_source_alone_is_exit_2_source_unservable_never_a_red(self) -> None:
        self.write_snapshot(("R-1", "active"))
        url = "https://example.invalid/page"
        self.write_spec("test_url.py", self.header(("R-1",), (f"{url} sha256:{sha(b'x')}",)))
        got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("SOURCE_UNSERVABLE specs/test_url.py: line 2 source "), err)
        self.assertNotIn("SOURCE_MISSING", err)
        self.assertNotIn("NO_SPEC_FOR_REQUIREMENT", err)

    def test_every_url_scheme_is_a_url_source_and_never_a_red(self) -> None:
        self.write_snapshot(("R-1", "active"))
        for url in ("file:///etc/hosts", "file://host/share/x", "ftp://example.invalid/x", "s3://bucket/key", "ssh://git@example.invalid/x", "git+https://example.invalid/x"):
            for suffix in (f" sha256:{sha(b'x')}", ""):
                with self.subTest(url=url, digest=bool(suffix)):
                    self.write_spec("test_url.py", self.header(("R-1",), (f"{url}{suffix}",)))
                    got, out, err = self.run_gate()
                    self.assertEqual((got, out), (2, ""), err)
                    self.assertEqual(len(err.splitlines()), 1, err)
                    self.assertTrue(err.startswith("SOURCE_UNSERVABLE specs/test_url.py: line 2 source "), err)
                    self.assertNotIn("SOURCE_MISSING", err)

    def test_a_red_found_elsewhere_is_printed_and_the_fault_stays_on_stderr(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a_red.py", self.header(("R-9",)))
        self.write_spec("test_b_url.py", self.header(("R-1",), ("http://example.invalid/x sha256:" + sha(b"x"),)))
        got, out, err = self.run_gate()
        self.assertEqual(got, 1, err)
        self.assertEqual(out, "RETIRED_REQUIREMENT_BOUND specs/test_a_red.py: requirement 'R-9' is absent from the snapshot\n")
        lines = err.splitlines()
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("SOURCE_UNSERVABLE specs/test_b_url.py: line 2 source "), lines[0])
        self.assertEqual(lines[1], "requirements=1 specs=2 defects=1")

    def test_a_url_source_beside_a_literal_red_in_the_same_spec_reports_the_red(self) -> None:
        self.write_snapshot(("R-1", "active"))
        header = self.header(("R-1",), ("https://example.invalid/page sha256:" + sha(b"x"),))
        self.write_spec("test_url.py", header, spec_body("    assert value == 3"))
        got, out, err = self.run_gate()
        self.assertEqual(got, 1, err)
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertTrue(out.startswith("LITERAL_EXPECTED specs/test_url.py: line "), out)
        lines = err.splitlines()
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("SOURCE_UNSERVABLE specs/test_url.py: "), lines[0])
        self.assertEqual(lines[1], "requirements=1 specs=1 defects=1")

    def test_a_url_source_beside_an_unbound_requirement_reports_the_unbound_one(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.write_spec("test_url.py", self.header(("R-1",), ("https://example.invalid/page sha256:" + sha(b"x"),)))
        got, out, err = self.run_gate()
        self.assertEqual(got, 1, err)
        self.assertEqual(out, "NO_SPEC_FOR_REQUIREMENT R-2: no spec declares this active requirement\n")
        self.assertTrue(err.startswith("SOURCE_UNSERVABLE specs/test_url.py: "), err)

    def test_a_url_source_is_a_source_so_the_spec_is_not_also_missing_one(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_url.py", self.header(("R-1",), ("https://example.invalid/page sha256:" + sha(b"x"),)))
        got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.write_spec("test_url.py", self.header(("R-1",), ("https://example.invalid/page sha256:" + sha(b"x"),), ()))
        got, out, err = self.run_gate()
        self.assertEqual(got, 1, err)
        self.assertEqual(out, "NO_MUTATION specs/test_url.py: the spec declares a requirement but no mutation\n")

    def test_every_url_source_of_a_spec_is_its_own_fault_line(self) -> None:
        self.write_snapshot(("R-1", "active"))
        urls = tuple(f"https://example.invalid/{name} sha256:{sha(b'x')}" for name in ("one", "two"))
        self.write_spec("test_url.py", self.header(("R-1",), urls))
        got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 2, err)
        self.assertIn("line 2 ", err.splitlines()[0])
        self.assertIn("line 3 ", err.splitlines()[1])

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
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("HEAD does not name a commit", err)
        self.assertNotRegex(err.strip(), r": $")

    def test_a_git_failure_that_says_nothing_still_names_a_cause(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        silent = subprocess.CompletedProcess([], 128, b"", b"")
        with mock.patch.object(contract_gate.subprocess, "run", return_value=silent):
            got, out, err = self.run_gate()
        self.assertEqual((got, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertNotRegex(err.strip(), r": $")
        self.assertIn("git printed no message", err)

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

    def test_a_spec_that_serves_no_source_makes_no_lookup(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", "# requirement: R-1\n# mutation: m\n")
        spy = GitSpy()
        with spy.patched():
            self.assertEqual(self.codes(), ["SOURCE_MISSING"])
        self.assertEqual(
            [call.command[4:] for call in spy.calls],
            [["rev-parse", "--show-toplevel"], ["rev-parse", "--verify", "--quiet", "HEAD^{commit}"]],
        )
        self.assertEqual(spy.processes, [])

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

    UNICODE_SPACES = ("\x85", "\u00a0", "\u1680", "\u2000", "\u2003", "\u2028", "\u2029", "\u202f", "\u205f", "\u3000")

    def test_unicode_whitespace_is_not_the_separator_between_a_source_path_and_its_digest(self) -> None:
        self.write_snapshot(("R-1", "active"))
        for char in self.UNICODE_SPACES:
            with self.subTest(char=char):
                self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt{char}sha256:{sha(SOURCE_BYTES)}",)))
                lines = self.red_lines()
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])
                self.assertIn("has no `sha256:` digest", lines[0])
        for separator in (" ", "  ", "     "):
            with self.subTest(separator=separator):
                self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt{separator}sha256:{sha(SOURCE_BYTES)}",)))
                self.assert_green()

    def test_unicode_whitespace_does_not_make_a_declaration_key(self) -> None:
        self.write_snapshot(("R-1", "active"))
        for char in self.UNICODE_SPACES:
            extra = (
                f"#{char}requirement: R-9\n"
                f"# requirement{char}: R-9\n"
                f"#{char}source: contracts/nope.txt sha256:abc\n"
                f"# source{char}: contracts/nope.txt sha256:abc\n"
                f"#{char}mutation:\n"
                f"# mutation{char}:\n"
            )
            with self.subTest(char=char):
                self.write_spec("test_one.py", self.header(("R-1",)) + extra)
                self.assert_green()

    def test_a_mutation_line_whose_key_holds_a_unicode_space_is_not_a_mutation(self) -> None:
        self.write_snapshot(("R-1", "active"))
        for char in self.UNICODE_SPACES:
            with self.subTest(char=char):
                self.write_spec("test_one.py", self.header(("R-1",), mutations=()) + f"# mutation{char}: drop\n#{char}mutation: drop\n")
                self.assertEqual(self.codes(), ["NO_MUTATION"])

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
        ):
            with self.subTest(path):
                self.assertEqual(self.declare(path), [])

    def test_a_path_with_an_empty_dot_or_dot_dot_segment_is_not_canonical(self) -> None:
        for path in (
            "contracts//source.txt",
            "contracts/./source.txt",
            "specs/../contracts/source.txt",
            "././contracts/source.txt",
            "contracts\\\\source.txt",
        ):
            with self.subTest(path):
                self.assert_missing(path)
                self.assertIn("segment", self.declare(path)[0])

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
            env={"PYTHONIOENCODING": "cp950", "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "PATH": os.environ.get("PATH", "")},
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


class SpecDecoding(Case):
    """A spec is decoded the way Python decodes source; the decoded text is what is quoted."""

    def coded(self, coding: str, assertion: str, *, comment: str = "") -> bytes:
        text = f"# -*- coding: {coding} -*-\n" + comment + self.header(("R-1",)) + "\n" + spec_body(assertion)
        return text.encode(coding)

    def red(self, data: bytes, *rows: tuple[str, str]) -> list[str]:
        self.write_snapshot(*rows)
        (self.specs / "test_one.py").write_bytes(data)
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, out + err)
        self.assertNotIn("TOOL_FAULT", err)
        self.assertNotIn("Traceback", out + err)
        return out.splitlines()

    def only_literal_line(self, data: bytes) -> str:
        lines = self.red(data, ("R-1", "active"))
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("LITERAL_EXPECTED specs/test_one.py: line "), lines[0])
        return lines[0]

    def test_a_latin_1_spec_with_a_non_ascii_literal_is_a_red_quoting_the_decoded_text(self) -> None:
        line = self.only_literal_line(self.coded("latin-1", '    assert "\u00e9\u00e9\u00e9" == value'))
        self.assertTrue(line.endswith('"\u00e9\u00e9\u00e9" == value'), line)

    def test_a_cp950_spec_with_a_non_ascii_literal_is_a_red_quoting_the_decoded_text(self) -> None:
        line = self.only_literal_line(self.coded("cp950", '    assert value == "\u4e2d\u6587\u5b57"'))
        self.assertTrue(line.endswith('value == "\u4e2d\u6587\u5b57"'), line)

    def test_other_declared_codings_are_decoded_too(self) -> None:
        for coding, literal in (("shift_jis", "\u65e5\u672c\u8a9e"), ("koi8-r", "\u043f\u0440\u0438\u0432\u0435\u0442")):
            with self.subTest(coding):
                line = self.only_literal_line(self.coded(coding, f'    assert "{literal}" == value'))
                self.assertTrue(line.endswith(f'"{literal}" == value'), line)

    def test_a_utf_8_spec_with_astral_characters_before_the_literal_keeps_offsets_and_text_in_step(self) -> None:
        text = self.header(("R-1",)) + "\n" + spec_body('    assert ("\U0001f600", "\u00e9") == value', "    assert value == 3")
        lines = self.red(text.encode("utf-8"), ("R-1", "active"))
        self.assertEqual(len(lines), 2, lines)
        self.assertTrue(lines[0].endswith('("\U0001f600", "\u00e9") == value'), lines[0])
        self.assertTrue(lines[1].endswith("value == 3"), lines[1])

    def test_a_utf_8_byte_order_mark_is_honoured(self) -> None:
        text = self.header(("R-1",)) + "\n" + spec_body('    assert "\u00e9" == value')
        line = self.only_literal_line(b"\xef\xbb\xbf" + text.encode("utf-8"))
        self.assertTrue(line.endswith('"\u00e9" == value'), line)

    def test_a_non_utf_8_spec_that_asserts_against_the_ledger_is_green(self) -> None:
        self.write_snapshot(("R-1", "active"))
        header = "# -*- coding: latin-1 -*-\n# caf\u00e9 note\n" + self.header(("R-1",), mutations=("d\u00e9j\u00e0-vu",))
        (self.specs / "test_one.py").write_bytes((header + "\n" + spec_body()).encode("latin-1"))
        self.assert_green()

    def test_a_spec_that_cannot_be_decoded_is_a_red_of_that_spec_and_binds_nothing(self) -> None:
        shapes = {
            "an invalid utf-8 byte": b"# note\nx = '\xe9'\n",
            "a utf-16 file": "x = 1\n".encode("utf-16"),
            "an unknown coding": b"# coding: no-such-codec\nx = 1\n",
            "a coding that conflicts with the byte order mark": b"\xef\xbb\xbf# coding: latin-1\nx = 1\n",
            "bytes that are not the declared coding": b"# coding: ascii\nx = '\xe9'\n",
        }
        for name, data in shapes.items():
            with self.subTest(name):
                lines = self.red(data)
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("LITERAL_EXPECTED specs/test_one.py: "), lines[0])

    def test_an_undecodable_spec_leaves_its_requirements_unbound(self) -> None:
        lines = self.red(b"# requirement: R-1\n# source: x sha256:00\n# mutation: m\nx = '\xe9'\n", ("R-1", "active"))
        self.assertEqual(sorted(line.split(" ", 1)[0] for line in lines), ["LITERAL_EXPECTED", "NO_SPEC_FOR_REQUIREMENT"])


class Boom(Exception):
    """An exception type the gate has never heard of."""


class BoomWithoutText(Exception):
    def __str__(self) -> str:
        raise RuntimeError("no text")


class PerSpecGuard(Case):
    """Whatever the analysis of a spec's bytes raises is a red of that spec, never exit 2."""

    EXCEPTIONS: tuple[BaseException, ...] = (
        RecursionError("deep"),
        MemoryError(),
        ValueError("v"),
        TypeError("t"),
        KeyError("k"),
        IndexError("i"),
        AttributeError("a"),
        ZeroDivisionError(),
        OverflowError("o"),
        SystemError("s"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad"),
        SyntaxError("s"),
        OSError(5, "io"),
        AssertionError("a"),
        NotImplementedError("n"),
        Boom("custom"),
        BoomWithoutText(),
    )

    def prepare(self, *asserts: str) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), spec_body(*asserts))

    def assert_one_unanalysable_red(self, label: str) -> list[str]:
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, f"{label}: {out}{err}")
        self.assertNotIn("TOOL_FAULT", err)
        self.assertNotIn("Traceback", out + err)
        lines = out.splitlines()
        reds = [line for line in lines if line.startswith("LITERAL_EXPECTED specs/test_one.py: the spec cannot be analysed")]
        self.assertEqual(len(reds), 1, f"{label}: {lines}")
        self.assertEqual(len(out.splitlines()), out.count("\n"), label)
        return lines

    def test_every_step_of_the_analysis_is_guarded_whatever_exception_type_it_raises(self) -> None:
        targets = (
            (contract_gate.ast, "parse"),
            (contract_gate, "parse_header"),
            (contract_gate, "decode_source"),
            (contract_gate, "literal_defects"),
            (contract_gate, "_source_text"),
            (contract_gate.ast, "walk"),
            (contract_gate.ast, "get_source_segment"),
        )
        self.prepare("    assert value == 3")
        for owner, name in targets:
            for exception in self.EXCEPTIONS:
                if name == "parse" and isinstance(exception, SyntaxError):
                    continue  # a syntax error from the parser is the in-band "cannot be read" red, tested elsewhere
                label = f"{name} raising {type(exception).__name__}"
                with self.subTest(label), mock.patch.object(owner, name, side_effect=exception):
                    self.assert_one_unanalysable_red(label)

    def test_a_failed_literal_analysis_keeps_the_declarations_that_were_read(self) -> None:
        self.prepare()
        with mock.patch.object(contract_gate, "literal_defects", side_effect=Boom("x")):
            lines = self.assert_one_unanalysable_red("literal_defects")
        self.assertEqual(len(lines), 1, lines)

    def test_a_failed_declaration_read_leaves_the_requirement_unbound(self) -> None:
        self.prepare()
        with mock.patch.object(contract_gate, "parse_header", side_effect=Boom("x")):
            lines = self.assert_one_unanalysable_red("parse_header")
        self.assertEqual(sorted(line.split(" ", 1)[0] for line in lines), ["LITERAL_EXPECTED", "NO_SPEC_FOR_REQUIREMENT"])

    def test_the_detail_names_the_reason_on_one_line_and_is_cut(self) -> None:
        self.prepare()
        message = "first line\nsecond\u2028line " + "x" * 5000
        with mock.patch.object(contract_gate, "literal_defects", side_effect=Boom(message)):
            lines = self.assert_one_unanalysable_red("long message")
        self.assertIn("Boom: first line\\nsecond\\u2028line", lines[0])
        self.assertLess(len(lines[0]), 400, len(lines[0]))

    def test_a_guarded_spec_does_not_stop_the_next_one(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.good_spec("test_a.py", "R-1")
        self.write_spec("test_b.py", self.header(("R-2",)), spec_body("    assert value == 3"))
        real = contract_gate.literal_defects

        def picky(spec: str, text: str) -> list[contract_gate.Defect]:
            if spec.endswith("test_a.py"):
                raise Boom("only the first")
            return real(spec, text)

        with mock.patch.object(contract_gate, "literal_defects", picky):
            code, out, _ = self.run_gate()
        self.assertEqual(code, 1)
        self.assertEqual(
            [line.split(": ", 1)[0] for line in out.splitlines()],
            ["LITERAL_EXPECTED specs/test_a.py", "LITERAL_EXPECTED specs/test_b.py"],
        )
        self.assertIn("line ", out.splitlines()[1])

    def test_a_syntax_error_and_a_parser_exception_are_both_one_red(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",)), "def broken(:\n")
        self.assertEqual(self.codes(), ["LITERAL_EXPECTED"])
        self.prepare()
        for exception in (RecursionError("deep"), MemoryError(), ValueError("source code string cannot contain null bytes")):
            with self.subTest(type(exception).__name__), mock.patch.object(contract_gate.ast, "parse", side_effect=exception):
                self.assert_one_unanalysable_red(type(exception).__name__)

    def test_only_the_disk_and_git_are_faults(self) -> None:
        self.prepare()
        original = Path.read_bytes

        def deny(path: Path) -> bytes:
            if path.name == "test_one.py":
                raise PermissionError(13, "Permission denied", str(path))
            return original(path)

        with mock.patch.object(Path, "read_bytes", deny):
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("test_one.py", err)
        with GitSpy(fail_on="rev-parse").patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("injected failure", err)


class SourceLookup(Case):
    """A canonical source path is looked up once, literally, through the standard input of git."""

    def test_a_very_long_source_path_is_source_missing_without_any_lookup(self) -> None:
        spy = GitSpy()
        for length in (1500, 40000, 400000):
            with self.subTest(length), spy.patched():
                lines = self.declare_many("a/" * (length // 2))
            self.assertEqual(len(lines), 1, lines[:2])
            self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0][:100])
            self.assertIn("longer than 1024 bytes", lines[0])
            self.assertLess(len(lines[0]), 3000)
        self.assertEqual(spy.lookups(), [])

    def test_the_path_length_limit_counts_utf_8_bytes_after_normalisation(self) -> None:
        for path, expected in (
            ("x" * 1024, "is not tracked at HEAD"),
            ("x" * 1025, "longer than 1024 bytes"),
            ("./" + "x" * 1024, "is not tracked at HEAD"),
            ("\u00e9" * 512, "is not tracked at HEAD"),
            ("\u00e9" * 513, "longer than 1024 bytes"),
            ("d/" * 511 + "ab", "is not tracked at HEAD"),
        ):
            with self.subTest(path[:12], length=len(path.encode("utf-8"))):
                lines = self.declare_many(path)
                self.assertEqual(len(lines), 1, lines)
                self.assertIn(expected, lines[0])

    def test_a_source_that_looks_like_a_pathspec_is_not_canonical_or_matches_only_itself(self) -> None:
        for path in (
            ":(glob)contracts/*",
            ":/contracts/source.txt",
            ":!contracts/source.txt",
            ":(top)contracts/source.txt",
            ":(literal)contracts/source.txt",
            ":contracts/source.txt",
            "contracts/:(glob)source.txt",
            "contracts/**",
            "contracts/*.txt",
            "contracts/[s]ource.txt",
            "contracts/sourc?.txt",
            "**/source.txt",
        ):
            with self.subTest(path):
                spy = GitSpy()
                with spy.patched():
                    lines = self.declare_many(path)
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])
                for call in spy.calls:
                    self.assertFalse(any("contracts" in argument for argument in call.command[3:]), call.command)

    def test_a_path_that_is_not_relative_is_refused_without_any_lookup(self) -> None:
        for path in (
            "/contracts/source.txt",
            "C:contracts/source.txt",
            "c:/contracts/source.txt",
            "C:\\contracts\\source.txt",
            ":contracts/source.txt",
            ":(glob)contracts/*",
            ":/contracts/source.txt",
            ":!contracts/source.txt",
        ):
            with self.subTest(path):
                spy = GitSpy()
                with spy.patched():
                    lines = self.declare_many(path)
                self.assertEqual(len(lines), 1, lines)
                self.assertIn("not a relative repository path", lines[0])
                self.assertEqual(spy.lookups(), [])

    def test_a_segment_problem_and_a_control_character_are_refused_without_any_lookup(self) -> None:
        for path, reason in (
            ("contracts//source.txt", "segment"),
            ("contracts/../contracts/source.txt", "segment"),
            ("contracts/", "segment"),
            ("contracts/so\x01urce.txt", "control character"),
        ):
            with self.subTest(path):
                spy = GitSpy()
                with spy.patched():
                    lines = self.declare_many(path)
                self.assertEqual(len(lines), 1, lines)
                self.assertIn(reason, lines[0])
                self.assertEqual(spy.lookups(), [])

    def test_no_source_reaches_git_on_a_command_line_or_as_a_name(self) -> None:
        self.commit_source("my docs/a b.txt", SOURCE_BYTES)
        spy = GitSpy()
        with spy.patched():
            self.assertEqual(self.declare_many("my docs/a b.txt"), [])
        lookups = spy.lookups()
        self.assertEqual([call.command[4:] for call in lookups], [["cat-file", "--batch"]])
        for query in spy.queries():
            self.assertRegex(query.decode("ascii"), r"^[0-9a-f]{40}$")
        for call in spy.calls:
            self.assertEqual(call.command[:4], ["git", "-C", str(self.repo), "--no-replace-objects"])
            self.assertFalse(any("a b.txt" in argument or "my docs" in argument for argument in call.command[4:]), call.command)

    def test_a_name_with_glob_characters_that_is_tracked_resolves_to_itself_only(self) -> None:
        git(self.repo, "config", "core.protectNTFS", "false")
        def track(name: str, data: bytes) -> None:
            identifier = subprocess.run(
                ["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                input=data,
                capture_output=True,
                env={**os.environ, **GIT_ENVIRONMENT},
                check=True,
            ).stdout.decode("ascii").strip()
            git(self.repo, "update-index", "--add", "--cacheinfo", f"100644,{identifier},{name}")

        track("star*name.txt", b"the star")
        track("starXname.txt", b"the X")
        track("[ab].txt", b"the class")
        track("a.txt", b"the a")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "glob names")
        self.write_snapshot(("R-1", "active"))
        for name, data, ok in (
            ("star*name.txt", b"the star", True),
            ("star*name.txt", b"the X", False),
            ("starXname.txt", b"the X", True),
            ("[ab].txt", b"the class", True),
            ("[ab].txt", b"the a", False),
            ("a.txt", b"the a", True),
            ("star?name.txt", b"the star", False),
        ):
            with self.subTest(name=name, ok=ok):
                self.write_spec("test_one.py", self.header(("R-1",), (f"{name} sha256:{sha(data)}",)))
                code, out, err = self.run_gate()
                self.assertEqual(code, 0 if ok else 1, out + err)

    def test_git_failing_during_a_lookup_is_exit_2_and_never_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        for failing in ("cat-file", "--batch", "--verify"):
            with self.subTest(failing), GitSpy(fail_on=failing).patched():
                code, out, err = self.run_gate()
                self.assertEqual((code, out), (2, ""))
                self.assertIn("injected failure", err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_tree_or_a_submodule_at_head_is_source_missing(self) -> None:
        lines = self.declare_many("contracts")
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("is not a blob at HEAD", lines[0])
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{'b' * 40},modules/sub")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "gitlink")
        lines = self.declare_many("modules/sub")
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])

    def test_the_digest_is_over_binary_content_with_every_byte_value(self) -> None:
        data = bytes(range(256)) * 3 + b"\r\n\n\r\x00 trailing\n\n"
        self.commit_source("contracts/binary.bin", data)
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/binary.bin sha256:{sha(data)}",)))
        self.assert_green()
        empty = b""
        self.commit_source("contracts/empty.bin", empty)
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/empty.bin sha256:{sha(empty)}",)))
        self.assert_green()


def write_blob(repo: Path, data: bytes) -> str:
    """Store `data` as a blob of `repo` and return its object id."""
    return subprocess.run(
        ["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
        input=data,
        capture_output=True,
        env={**os.environ, **GIT_ENVIRONMENT},
        check=True,
    ).stdout.decode("ascii").strip()


def track_entry(repo: Path, name: str, data: bytes, mode: str = "100644") -> None:
    """Put an entry with an explicit mode in the index, without a work tree file."""
    git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{write_blob(repo, data)},{name}")


def remove_loose_object(repo: Path, oid: str) -> None:
    """Prune one loose object from the store of `repo`."""
    path = repo / ".git" / "objects" / oid[:2] / oid[2:]
    os.chmod(path, 0o666)
    path.unlink()
    exists = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", oid], capture_output=True, env={**os.environ, **GIT_ENVIRONMENT}, check=False)
    assert exists.returncode != 0, "the object is still served"


def raw_tree(*entries: tuple[str, str, bytes]) -> bytes:
    """The raw content of a tree: (mode, name, 20 raw id bytes) entries."""
    return b"".join(mode.encode("ascii") + b" " + name.encode("utf-8") + b"\0" + raw for mode, name, raw in entries)


def git_raw(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    """The raw standard output of git in `repo`, with a clean configuration; a failure fails the fixture."""
    done = subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, env={**os.environ, **GIT_ENVIRONMENT}, check=False)
    if done.returncode != 0:
        raise AssertionError(f"git {args}: {done.stderr.decode('utf-8', errors='replace')}")
    return done.stdout


def store_object(repo: Path, kind: str, body: bytes) -> str:
    """Store `body` as an object of `kind` exactly as given (no check of its shape) and return its id."""
    return git_raw(repo, "hash-object", "-w", "--literally", "-t", kind, "--stdin", data=body).decode("ascii").strip()


def point_head_at_commit(repo: Path, body: bytes) -> str:
    """Make the current branch name a commit with exactly this body; returns its id."""
    oid = store_object(repo, "commit", body)
    git(repo, "update-ref", "HEAD", oid)
    return oid


def point_head_at_tree(repo: Path, tree_body: bytes) -> str:
    """Make the current branch name a commit whose root tree has exactly this body (well formed or not)."""
    tree = store_object(repo, "tree", tree_body)
    stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nmessage\n"
    return point_head_at_commit(repo, f"tree {tree}\n{stamp}".encode("ascii"))


def forge_loose_object(repo: Path, oid: str, kind: str, body: bytes) -> None:
    """Overwrite the loose object `oid` with other content, as a writer of the shared store could."""
    path = repo / ".git" / "objects" / oid[:2] / oid[2:]
    assert path.is_file(), "the object is not a loose object"
    os.chmod(path, 0o666)
    path.write_bytes(zlib.compress(f"{kind} {len(body)}".encode("ascii") + b"\0" + body))
    served = git_raw(repo, "cat-file", kind, oid)
    assert served == body, "the forged content is not what the store serves"


def object_answer(oid: str, kind: str, content: bytes, declared_size: int | None = None) -> bytes:
    size = len(content) if declared_size is None else declared_size
    return f"{oid} {kind} {size}\n".encode("ascii") + content + b"\n"


class OneCommitPerRun(Case):
    """HEAD is resolved once to a full id; every lookup of the run is a line on one `cat-file --batch` process."""

    def test_head_is_resolved_once_and_every_lookup_goes_through_one_batch_process(self) -> None:
        self.commit_source("contracts/second.txt", b"other")
        self.commit_source("sub/deeper/third.txt", b"third")
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        first = f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}"
        second = f"contracts/second.txt sha256:{sha(b'other')}"
        third = f"sub/deeper/third.txt sha256:{sha(b'third')}"
        self.write_spec("test_a.py", self.header(("R-1",), (first, second)))
        self.write_spec("test_b.py", self.header(("R-2",), (first, third)))
        spy = GitSpy()
        with spy.patched():
            self.assert_green()
        verbs = [call.command[4:] for call in spy.calls]
        self.assertEqual(verbs.count(["rev-parse", "--verify", "--quiet", "HEAD^{commit}"]), 1, verbs)
        self.assertEqual(verbs.count(["cat-file", "--batch"]), 1, verbs)
        self.assertEqual(len(spy.lookups()), 1)
        head = git(self.repo, "rev-parse", "HEAD").strip()
        queries = spy.queries()
        self.assertEqual(queries[:2], [head.encode("ascii"), git(self.repo, "rev-parse", "HEAD^{tree}").strip().encode("ascii")])
        for query in queries:
            self.assertRegex(query.decode("ascii"), r"^[0-9a-f]{40}$")
        self.assertFalse(any(b"HEAD" in query or b"source" in query for query in queries), queries)
        self.assertEqual(spy.alive(), [])

    def test_a_commit_that_lands_during_the_run_changes_nothing_in_it(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.good_spec("test_a.py", "R-1")
        self.good_spec("test_b.py", "R-2")
        landed: list[bool] = []

        def land(query: bytes) -> None:
            if not landed:
                landed.append(True)
                self.commit_source("contracts/source.txt", b"landed during the run\n")

        spy = GitSpy(on_query=land)
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual(landed, [True])
        self.assertEqual((code, out, err), (0, "requirements=2 specs=2 defects=0\n", ""))
        self.assertEqual(self.codes(), ["SOURCE_DIGEST_MISMATCH", "SOURCE_DIGEST_MISMATCH"])

    def test_head_is_not_asked_again_for_each_source(self) -> None:
        self.write_snapshot(("R-1", "active"))
        sources = tuple(f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}" for _ in range(5))
        self.write_spec("test_a.py", self.header(("R-1",), sources))
        spy = GitSpy()
        with spy.patched():
            self.assert_green()
        self.assertEqual(len([call for call in spy.calls if "rev-parse" in call.command]), 2)
        self.assertEqual(len(spy.lookups()), 1)

    def test_the_batch_process_never_outlives_the_run(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_a.py", "R-1")
        green = GitSpy()
        with green.patched():
            self.assert_green()
        self.assertEqual((len(green.processes), green.alive()), (1, []))
        blob = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip()
        lying = GitSpy(replies=lambda query: b"garbage\n" if query == blob.encode("ascii") else None)
        with lying.patched():
            code, _, _ = self.run_gate()
        self.assertEqual(code, 2)
        self.assertEqual((len(lying.processes), lying.alive()), (1, []))
        with mock.patch.object(contract_gate, "check_spec", side_effect=RuntimeError("boom")):
            crashed = GitSpy()
            with crashed.patched():
                self.run_gate()
        self.assertEqual(crashed.alive(), [])


class TreeEntries(Case):
    """A source's tree entry is read from its parent tree: links and submodules are not files, and a file is."""

    def declare_exit(self, path: str, digest: str | None = None) -> tuple[int, list[str], str]:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), (f"{path} sha256:{digest or sha(SOURCE_BYTES)}",)))
        code, out, err = self.run_gate()
        return code, [line for line in out.splitlines() if not line.startswith("requirements=")], err

    def assert_not_a_regular_file(self, path: str, what: str, digest: str | None = None) -> None:
        code, lines, err = self.declare_exit(path, digest)
        self.assertEqual(code, 1, err)
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])
        self.assertIn(f"is not a regular file at HEAD ({what})", lines[0])
        self.assertNotIn("TOOL_FAULT", err)

    def test_a_tracked_symbolic_link_is_source_missing_whatever_digest_is_declared(self) -> None:
        link_text = b"source.txt"
        track_entry(self.repo, "contracts/link.txt", link_text, "120000")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "link")
        for digest in (sha(SOURCE_BYTES), sha(link_text), "0" * 64):
            with self.subTest(digest=digest[:8]):
                self.assert_not_a_regular_file("contracts/link.txt", "symbolic link", digest)

    def test_a_symbolic_link_source_never_stays_green_while_the_content_it_cites_changes(self) -> None:
        track_entry(self.repo, "contracts/link.txt", b"source.txt", "120000")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "link")
        before = self.declare_exit("contracts/link.txt")
        self.assertEqual(before[0], 1)
        changed = b"the target changed after the contract was written\n"
        self.source.write_bytes(changed)
        git(self.repo, "add", "contracts/source.txt")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "the target changes")
        for digest in (sha(SOURCE_BYTES), sha(changed)):
            with self.subTest(digest=digest[:8]):
                after = self.declare_exit("contracts/link.txt", digest)
                self.assertEqual(after[0], 1, after)
                self.assertEqual(after[1], before[1])

    def test_a_symbolic_link_in_the_middle_of_the_path_is_not_followed(self) -> None:
        track_entry(self.repo, "shortcut", b"contracts", "120000")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "directory link")
        code, lines, err = self.declare_exit("shortcut/source.txt")
        self.assertEqual(code, 1, err)
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])
        self.assertIn("is not tracked at HEAD", lines[0])

    def test_a_gitlink_in_the_middle_of_the_path_is_not_descended(self) -> None:
        contracts_tree = git(self.repo, "rev-parse", "HEAD:contracts").strip()
        for label, pointer in (("an id that names no object", "b" * 40), ("the id of a real tree holding the source", contracts_tree)):
            with self.subTest(label):
                git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{pointer},modules/sub")
                git(self.repo, "commit", "-q", "--no-verify", "--allow-empty", "-m", f"gitlink at {pointer[:4]}")
                code, lines, err = self.declare_exit("modules/sub/source.txt")
                self.assertEqual(code, 1, err)
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])
                self.assertIn("a directory on the path is not a directory", lines[0])
                self.assertNotIn("SOURCE_UNSERVABLE", err)
                self.assertNotIn("TOOL_FAULT", err)

    def test_a_submodule_entry_is_source_missing_not_a_fault(self) -> None:
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{'b' * 40},modules/sub")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "gitlink")
        self.assert_not_a_regular_file("modules/sub", "submodule")

    def test_a_directory_is_not_a_blob(self) -> None:
        self.commit_source("sub/x.txt", b"x")
        for path in ("contracts", "sub"):
            with self.subTest(path):
                code, lines, err = self.declare_exit(path)
                self.assertEqual(code, 1, err)
                self.assertEqual(len(lines), 1, lines)
                self.assertIn("is not a blob at HEAD (a directory)", lines[0])

    def test_an_executable_file_is_a_regular_file(self) -> None:
        track_entry(self.repo, "contracts/run.sh", b"#!/bin/sh\n", "100755")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "executable")
        self.assertEqual(self.declare_exit("contracts/run.sh", sha(b"#!/bin/sh\n"))[:2], (0, []))

    def test_a_path_through_a_file_or_a_missing_directory_is_not_tracked(self) -> None:
        for path in ("contracts/source.txt/inner.txt", "nowhere/source.txt", "contracts/nowhere/source.txt"):
            with self.subTest(path):
                code, lines, err = self.declare_exit(path)
                self.assertEqual(code, 1, err)
                self.assertEqual(len(lines), 1, lines)
                self.assertIn("is not tracked at HEAD", lines[0])

    def test_a_file_in_a_deep_directory_resolves_and_a_sibling_name_does_not(self) -> None:
        self.commit_source("a/b/c/d/e.txt", b"deep")
        self.assertEqual(self.declare_exit("a/b/c/d/e.txt", sha(b"deep"))[:2], (0, []))
        self.assertEqual(self.declare_exit("a/b/c/d/e.txtx", sha(b"deep"))[0], 1)
        self.assertEqual(self.declare_exit("a/b/c/D/e.txt", sha(b"deep"))[0], 1)

    def test_a_file_whose_name_is_a_prefix_of_another_is_told_apart(self) -> None:
        self.commit_source("contracts/source.txt.bak", b"backup")
        self.commit_source("contracts/source", b"short")
        self.assertEqual(self.declare_exit("contracts/source", sha(b"short"))[:2], (0, []))
        self.assertEqual(self.declare_exit("contracts/source.txt.bak", sha(b"backup"))[:2], (0, []))
        self.assertEqual(self.declare_exit("contracts/source.txt", sha(SOURCE_BYTES))[:2], (0, []))

    def test_non_ascii_names_resolve_by_their_utf_8_bytes(self) -> None:
        git(self.repo, "config", "core.quotepath", "false")
        self.commit_source("docs/中文/é.txt", b"text")
        self.assertEqual(self.declare_exit("docs/中文/é.txt", sha(b"text"))[:2], (0, []))
        self.assertEqual(self.declare_exit("docs/中文/e.txt", sha(b"text"))[0], 1)

    def test_a_large_blob_is_digested_in_blocks(self) -> None:
        data = bytes(range(256)) * 20000
        self.commit_source("contracts/large.bin", data)
        self.assertEqual(self.declare_exit("contracts/large.bin", sha(data))[:2], (0, []))
        self.assertEqual(self.declare_exit("contracts/large.bin", sha(data[:-1]))[0], 1)


class UnservableObjects(Case):
    """An object a tree names but the store cannot serve is a fault; a name the tree does not hold is a red."""

    def one_line_fault(self, err: str) -> str:
        lines = err.splitlines()
        self.assertEqual(len(lines), 1, err)
        return lines[0]

    def test_a_pruned_blob_is_exit_2_and_never_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        remove_loose_object(self.repo, git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip())
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        fault = self.one_line_fault(err)
        self.assertTrue(fault.startswith("SOURCE_UNSERVABLE specs/test_one.py: line 2 source 'contracts/source.txt': "), fault)
        self.assertNotIn("SOURCE_MISSING", fault)

    def test_a_pruned_tree_on_the_path_is_exit_2_and_never_source_missing(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        remove_loose_object(self.repo, git(self.repo, "rev-parse", "HEAD:contracts").strip())
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(self.one_line_fault(err).startswith("SOURCE_UNSERVABLE specs/test_one.py: line 2 source "), err)

    def test_a_pruned_root_tree_is_exit_2(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        remove_loose_object(self.repo, git(self.repo, "rev-parse", "HEAD^{tree}").strip())
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SOURCE_UNSERVABLE", self.one_line_fault(err))

    def test_a_name_the_tree_does_not_hold_stays_a_red_beside_a_pruned_one(self) -> None:
        self.write_snapshot(("R-1", "active"))
        remove_loose_object(self.repo, git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip())
        gone = f"contracts/gone.txt sha256:{sha(b'x')}"
        pruned = f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}"
        self.write_spec("test_one.py", self.header(("R-1",), (gone, pruned)))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(out.splitlines()), 1, out)
        self.assertTrue(out.startswith("SOURCE_MISSING specs/test_one.py: line 2: "), out)
        lines = err.splitlines()
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("SOURCE_UNSERVABLE specs/test_one.py: line 3 source "), lines[0])
        self.assertEqual(lines[1], "requirements=1 specs=1 defects=1")

    def test_a_pruned_blob_does_not_stop_the_other_sources_from_being_checked(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.commit_source("contracts/second.txt", b"other")
        remove_loose_object(self.repo, git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip())
        pruned = f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}"
        wrong = f"contracts/second.txt sha256:{sha(b'changed')}"
        self.write_spec("test_one.py", self.header(("R-1",), (pruned, wrong)))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("SOURCE_DIGEST_MISMATCH specs/test_one.py: line 3: "), out)
        self.assertIn("SOURCE_UNSERVABLE", err)

    def test_a_blobless_clone_is_exit_2_for_a_blob_and_the_gate_never_fetches(self) -> None:
        git(self.repo, "config", "uploadpack.allowFilter", "true")
        git(self.repo, "config", "uploadpack.allowAnySHA1InWant", "true")
        clone = self.base / "clone"
        made = subprocess.run(
            ["git", "clone", "-q", "--no-local", "--filter=blob:none", "--no-checkout", self.repo.as_uri(), str(clone)],
            capture_output=True,
            env={**os.environ, **GIT_ENVIRONMENT},
            check=False,
        )
        if made.returncode != 0:
            self.skipTest(f"this git cannot make a blobless clone: {made.stderr.decode('utf-8', errors='replace')}")
        blob = git(clone, "rev-parse", "HEAD:contracts/source.txt").strip()
        absent = subprocess.run(["git", "-C", str(clone), "-c", "fetch.negotiationAlgorithm=noop", "cat-file", "-e", blob], capture_output=True, env={**os.environ, **GIT_ENVIRONMENT, "GIT_NO_LAZY_FETCH": "1"}, check=False)
        self.assertNotEqual(absent.returncode, 0, "the clone already holds the blob")
        self.repo, self.specs = clone, clone / "specs"
        self.specs.mkdir()
        self.snapshot = self.base / "snapshot.json"
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertTrue(self.one_line_fault(err).startswith("SOURCE_UNSERVABLE specs/test_one.py: line 2 source "), err)
        still_absent = subprocess.run(["git", "-C", str(clone), "cat-file", "-e", blob], capture_output=True, env={**os.environ, **GIT_ENVIRONMENT, "GIT_NO_LAZY_FETCH": "1"}, check=False)
        self.assertNotEqual(still_absent.returncode, 0, "the gate fetched the blob")
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/gone.txt sha256:{sha(b'x')}",)))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("SOURCE_MISSING specs/test_one.py: line 2: "), out)


class RedBeforeFault(Case):
    """The gate reports every red it can find and exits 1 if there is one; each fault is one line on stderr."""

    def lines_of(self, text: str) -> list[str]:
        return text.splitlines()

    def test_an_unreadable_spec_beside_a_red_reports_the_red(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        locked = self.good_spec("test_locked.py", "R-1")
        original = Path.read_bytes

        def deny(path: Path) -> bytes:
            if path.name == "test_locked.py":
                raise PermissionError(13, "Permission denied", str(path))
            return original(path)

        with mock.patch.object(Path, "read_bytes", deny):
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(self.lines_of(out)), 1, out)
        self.assertTrue(out.startswith("LITERAL_EXPECTED specs/test_a_red.py: line "), out)
        lines = self.lines_of(err)
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("TOOL_FAULT cannot read "), lines[0])
        self.assertIn(locked.name, lines[0])
        self.assertEqual(lines[1], "requirements=1 specs=2 defects=1")

    def test_a_requirement_is_not_called_unbound_when_a_spec_could_not_be_read(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        self.good_spec("test_locked.py", "R-1")
        original = Path.read_bytes

        def deny(path: Path) -> bytes:
            if path.name == "test_locked.py":
                raise PermissionError(13, "Permission denied", str(path))
            return original(path)

        with mock.patch.object(Path, "read_bytes", deny):
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertNotIn("NO_SPEC_FOR_REQUIREMENT", out)
        self.assertEqual(len(self.lines_of(out)), 1, out)

    def test_a_git_fault_after_reds_exits_1_with_one_fault_line(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        self.good_spec("test_b.py", "R-1")
        self.write_spec("test_c.py", self.header(("R-2",)), spec_body("    assert value == 7"))
        with GitSpy(fail_on="cat-file").patched():
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        found = self.lines_of(out)
        self.assertEqual(len(found), 2, out)
        self.assertTrue(found[0].startswith("LITERAL_EXPECTED specs/test_a_red.py: "), found[0])
        self.assertTrue(found[1].startswith("LITERAL_EXPECTED specs/test_c.py: "), found[1])
        lines = self.lines_of(err)
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("TOOL_FAULT "), lines[0])
        self.assertIn("injected failure", lines[0])
        self.assertEqual(lines[1], "requirements=2 specs=3 defects=2")

    def test_a_git_answer_outside_its_format_after_reds_exits_1(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        self.good_spec("test_b.py", "R-1")
        blob = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip().encode("ascii")
        spy = GitSpy(replies=lambda query: b"garbage\n" if query == blob else None)
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(self.lines_of(out)), 1, out)
        lines = self.lines_of(err)
        self.assertEqual(len(lines), 2, err)
        self.assertIn("outside its format", lines[0])

    def test_a_repository_without_a_commit_still_reports_the_reds_that_need_no_git(self) -> None:
        fresh = self.base / "fresh"
        fresh.mkdir()
        init_repo(fresh)
        self.repo, self.specs = fresh, fresh / "specs"
        self.specs.mkdir()
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", self.header(("R-1",), mutations=()), spec_body("    assert value == 3"))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(sorted(line.split(" ", 1)[0] for line in out.splitlines()), ["LITERAL_EXPECTED", "NO_MUTATION"])
        lines = self.lines_of(err)
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("TOOL_FAULT "), lines[0])
        self.assertEqual(lines[1], "requirements=1 specs=1 defects=2")

    def test_a_fault_with_no_red_is_exit_2_and_prints_no_summary(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        with GitSpy(fail_on="cat-file").patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(self.lines_of(err)), 1, err)
        self.assertNotIn("requirements=", err)

    def test_a_directory_that_cannot_be_listed_is_a_fault_beside_the_reds_of_the_others(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        (self.specs / "locked").mkdir()
        real = os.scandir

        def scandir(path: str | os.PathLike[str]) -> object:
            if Path(path).name == "locked":
                raise PermissionError(13, "Permission denied", str(path))
            return real(path)

        with mock.patch.object(contract_gate.os, "scandir", scandir):
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertEqual(len(self.lines_of(out)), 1, out)
        self.assertNotIn("NO_SPEC_FOR_REQUIREMENT", out)
        lines = self.lines_of(err)
        self.assertEqual(len(lines), 2, err)
        self.assertTrue(lines[0].startswith("TOOL_FAULT cannot list "), lines[0])

    def test_faults_and_the_summary_are_each_one_escaped_line_in_discovery_order(self) -> None:
        self.write_snapshot(("R-1", "active"))
        urls = tuple(f"https://example.invalid/{name} forged sha256:{sha(b'x')}" for name in ("one", "two"))
        self.write_spec("test_a.py", self.header(("R-1",), urls), spec_body("    assert value == 3"))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        lines = self.lines_of(err)
        self.assertEqual(len(lines), 3, repr(err))
        self.assertEqual(err.count("\n"), 3, repr(err))
        self.assertIn("line 2 ", lines[0])
        self.assertIn("line 3 ", lines[1])
        self.assertIn("\\u2028", lines[0])
        self.assertEqual(lines[2], "requirements=1 specs=1 defects=1")

    def test_an_unexpected_error_while_checking_one_spec_is_a_fault_and_the_others_are_still_checked(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a.py", "", "assert value == 3\n")
        self.write_spec("test_b.py", "", "assert value == 4\n")
        real = contract_gate.check_spec

        def check(spec: str, data: bytes, reader: contract_gate.HeadReader, status: dict[str, str]) -> contract_gate.SpecResult:
            if spec.endswith("test_a.py"):
                raise RuntimeError("boom")
            return real(spec, data, reader, status)

        with mock.patch.object(contract_gate, "check_spec", check):
            code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("LITERAL_EXPECTED specs/test_b.py: "), out)
        self.assertIn("unexpected RuntimeError while checking specs/test_a.py: boom", err)
        self.assertNotIn("Traceback", err)

    def test_an_unexpected_error_withholds_the_unbound_requirements(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.good_spec("test_a.py", "R-1")
        self.good_spec("test_b.py", "R-2")
        real = contract_gate.check_spec

        def check(spec: str, data: bytes, reader: contract_gate.HeadReader, status: dict[str, str]) -> contract_gate.SpecResult:
            if spec.endswith("test_a.py"):
                raise RuntimeError("boom")
            return real(spec, data, reader, status)

        with mock.patch.object(contract_gate, "check_spec", check):
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(self.lines_of(err)), 1, err)
        self.assertIn("unexpected RuntimeError while checking specs/test_a.py: boom", err)
        self.assertNotIn("NO_SPEC_FOR_REQUIREMENT", out + err)

    def test_the_preconditions_stay_faults_at_once(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_a.py", "", "assert value == 3\n")
        self.snapshot.unlink()
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)

    def test_the_real_command_line_exits_1_with_the_red_and_the_fault(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_url.py", self.header(("R-1",), (f"https://example.invalid/x sha256:{sha(b'x')}",)), spec_body("    assert value == 3"))
        done = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertTrue(done.stdout.startswith("LITERAL_EXPECTED specs/test_url.py: line "), done.stdout)
        self.assertTrue(done.stderr.startswith("SOURCE_UNSERVABLE specs/test_url.py: "), done.stderr)
        self.assertNotIn("Traceback", done.stderr)


class BatchAnswers(Case):
    """Every answer of the batch process is checked; one that is not exactly what was asked for is a tool fault."""

    def setUp(self) -> None:
        super().setUp()
        self.blob = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip()
        self.head = git(self.repo, "rev-parse", "HEAD").strip()
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")

    def answered(self, query_text: str, answer: bytes) -> tuple[int, str, str]:
        spy = GitSpy(replies=lambda query: answer if query == query_text.encode("ascii") else None)
        with spy.patched():
            result = self.run_gate()
        self.assertEqual(spy.alive(), [])
        return result

    def blob_answered(self, answer: bytes) -> tuple[int, str, str]:
        return self.answered(self.blob, answer)

    def test_a_missing_answer_for_a_named_blob_is_a_source_fault(self) -> None:
        code, out, err = self.blob_answered(f"{self.blob} missing\n".encode("ascii"))
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("SOURCE_UNSERVABLE specs/test_one.py: "), err)

    def test_an_answer_that_is_not_exactly_missing_for_this_query_is_a_tool_fault(self) -> None:
        blob = self.blob
        other = "a" * 40
        answers = {
            "two spaces": f"{blob}  missing\n",
            "extra word": f"{blob} missing extra\n",
            "other name": f"{other} missing\n",
            "upper case": f"{blob} Missing\n",
            "ambiguous": f"{blob} ambiguous\n",
            "no name": " missing\n",
            "no space": f"{blob}missing\n",
            "bare word": "missing\n",
            "missing a name only at the end": f"x {blob} missing\n",
        }
        for label, answer in answers.items():
            with self.subTest(label):
                code, out, err = self.blob_answered(answer.encode("ascii"))
                self.assertEqual((code, out), (2, ""), err)
                self.assertTrue(err.startswith("TOOL_FAULT "), err)
                self.assertNotIn("SOURCE_UNSERVABLE", err)
                self.assertNotIn("SOURCE_MISSING", err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_an_answer_with_a_body_of_another_size_than_its_header_is_a_tool_fault(self) -> None:
        blob = self.blob
        answers = {
            "a longer body": f"{blob} blob 3\nabcd\n".encode("ascii"),
            "a shorter body": f"{blob} blob 10\nabc\n".encode("ascii"),
            "no line feed after the body": f"{blob} blob 3\nabc".encode("ascii"),
            "a wrong byte after the body": f"{blob} blob 3\nabcX".encode("ascii"),
            "no body": f"{blob} blob 3\n".encode("ascii"),
            "an empty body that is not empty": f"{blob} blob 0\nabc\n".encode("ascii"),
        }
        for label, answer in answers.items():
            with self.subTest(label):
                code, out, err = self.blob_answered(answer)
                self.assertEqual((code, out), (2, ""), err)
                self.assertTrue(err.startswith("TOOL_FAULT "), err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_an_answer_for_another_object_or_of_another_shape_is_a_tool_fault(self) -> None:
        blob = self.blob
        answers = {
            "another object id": object_answer("a" * 40, "blob", b"abc"),
            "a tree for a blob": object_answer(blob, "tree", b"abc"),
            "a commit for a blob": object_answer(blob, "commit", b"abc"),
            "an unknown type": f"{blob} thing 3\nabc\n".encode("ascii"),
            "no size": f"{blob} blob\n".encode("ascii"),
            "a negative size": f"{blob} blob -3\nabc\n".encode("ascii"),
            "an id of the wrong length": object_answer("a" * 39, "blob", b"abc"),
            "an upper case id": object_answer(blob.upper(), "blob", b"abc"),
            "garbage": b"garbage\n",
            "an empty line": b"\n",
            "end of output": b"",
            "no line feed": f"{blob} blob 3".encode("ascii"),
        }
        for label, answer in answers.items():
            with self.subTest(label):
                code, out, err = self.blob_answered(answer)
                self.assertEqual((code, out), (2, ""), err)
                self.assertTrue(err.startswith("TOOL_FAULT "), err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_tree_answer_outside_its_format_is_a_tool_fault(self) -> None:
        raw = bytes(20)
        bodies = {
            "a name twice": raw_tree(("100644", "a", raw), ("100644", "a", raw)),
            "a mode that is not octal": raw_tree(("10x644", "a", raw)),
            "an empty mode": raw_tree(("", "a", raw)),
            "an empty name": raw_tree(("100644", "", raw)),
            "a name with a slash": raw_tree(("100644", "a/b", raw)),
            "an id cut short": raw_tree(("100644", "a", raw[:7])),
            "no terminator": b"100644 a",
            "a mode only": b"100644",
            "a trailing byte": raw_tree(("100644", "a", raw)) + b"x",
        }
        for label, body in bodies.items():
            with self.subTest(label):
                point_head_at_tree(self.repo, body)
                code, out, err = self.run_gate()
                self.assertEqual((code, out), (2, ""), err)
                self.assertTrue(err.startswith("TOOL_FAULT "), err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_root_that_is_not_a_tree_or_a_commit_without_a_tree_line_is_a_tool_fault(self) -> None:
        stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nmessage\n"
        commits = {
            "a blob named as the root tree": f"tree {self.blob}\n{stamp}",
            "a commit named as the root tree": f"tree {self.head}\n{stamp}",
            "no tree line": f"parent {self.head}\n{stamp}",
            "a tree id cut short": f"tree {self.blob[:39]}\n{stamp}",
            "a tree id in capitals": f"tree {self.blob.upper()}\n{stamp}",
        }
        for label, text in commits.items():
            with self.subTest(label):
                # git itself refuses to name such a commit by a ref, so the gate is told its id directly
                oid = store_object(self.repo, "commit", text.encode("ascii"))
                with mock.patch.object(contract_gate, "resolve_head", return_value=oid):
                    code, out, err = self.run_gate()
                self.assertEqual((code, out), (2, ""), err)
                self.assertTrue(err.startswith("TOOL_FAULT "), err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_tree_outside_its_format_stops_the_store_for_every_later_source_and_spec(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        both = (f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}", f"contracts/source.txt sha256:{sha(b'other')}")
        self.write_spec("test_a.py", self.header(("R-1",), both))
        self.write_spec("test_b.py", self.header(("R-2",), both))
        point_head_at_tree(self.repo, raw_tree(("100644", "a", bytes(20)), ("100644", "a", bytes(20))))
        head = git(self.repo, "rev-parse", "HEAD").strip()
        spy = GitSpy()
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("names one entry twice", err)
        self.assertEqual(spy.queries(), [head.encode("ascii"), git(self.repo, "rev-parse", "HEAD^{tree}").strip().encode("ascii")])

    def test_a_blob_whose_content_reads_as_a_tree_is_not_accepted_as_a_subtree(self) -> None:
        disguised = write_blob(self.repo, raw_tree(("100644", "source.txt", bytes.fromhex(self.blob))))
        point_head_at_tree(self.repo, raw_tree(("40000", "contracts", bytes.fromhex(disguised))))
        queries: list[bytes] = []
        spy = GitSpy(on_query=queries.append)
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("TOOL_FAULT "), err)
        self.assertIn("another kind of object", err)
        self.assertIn(disguised, err)
        self.assertNotIn(self.blob.encode("ascii"), queries)

    def test_an_answer_that_names_another_object_than_the_one_asked_for_is_a_tool_fault_even_with_the_right_body(self) -> None:
        other = "a" * 40
        subtree = git(self.repo, "rev-parse", "HEAD:contracts").strip()
        root = git(self.repo, "rev-parse", "HEAD^{tree}").strip()
        for label, asked in (("blob", self.blob), ("subtree", subtree), ("root tree", root), ("commit", self.head)):
            with self.subTest(label):
                kind = git(self.repo, "cat-file", "-t", asked).strip()
                body = git_raw(self.repo, "cat-file", kind, asked)
                code, out, err = self.answered(asked, object_answer(other, kind, body))
                self.assertEqual((code, out), (2, ""), err)
                self.assertTrue(err.startswith("TOOL_FAULT "), err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_tree_that_names_nothing_the_spec_cites_makes_the_source_missing(self) -> None:
        point_head_at_tree(self.repo, raw_tree(("100644", "other", bytes(20))))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("SOURCE_MISSING specs/test_one.py: line 2: "), out)
        self.assertIn("is not tracked at HEAD", out)

    def test_a_tree_entry_with_an_unusual_mode_is_not_a_regular_file(self) -> None:
        point_head_at_tree(self.repo, raw_tree(("100644", "contracts", bytes(20))))
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("SOURCE_MISSING specs/test_one.py: line 2: "), out)
        self.assertIn("is not tracked at HEAD", out)

    def test_head_answered_outside_its_format_is_a_fault(self) -> None:
        for label, answer in {"not hex": b"zzzz\n", "short": b"abc123\n", "empty": b"", "two lines": b"a" * 40 + b"\n" + b"a" * 40 + b"\n", "no line feed": b"a" * 40}.items():
            with self.subTest(label), GitSpy(answers={"HEAD^{commit}": answer}).patched():
                code, out, err = self.run_gate()
                self.assertEqual((code, out), (2, ""), err)
                self.assertIn("outside its format", err)

    def test_a_batch_process_that_cannot_start_is_a_tool_fault(self) -> None:
        with GitSpy(fail_start=True).patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("cannot run git", err)
        self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_batch_process_that_never_answers_is_stopped_and_is_a_tool_fault(self) -> None:
        spy = GitSpy(replies=lambda query: HANG)
        started = time.monotonic()
        with mock.patch.object(contract_gate, "GIT_TIMEOUT_SECONDS", 0.5), spy.patched():
            code, out, err = self.run_gate()
        self.assertLess(time.monotonic() - started, 5.0, "the silent process was not stopped by the time limit")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("ended before it answered", err)
        self.assertEqual(spy.alive(), [])

    def test_a_failure_of_the_store_is_one_fault_for_every_source_and_spec(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        self.commit_source("contracts/second.txt", b"other")
        both = (f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}", f"contracts/second.txt sha256:{sha(b'other')}")
        self.write_spec("test_a.py", self.header(("R-1",), both))
        self.write_spec("test_b.py", self.header(("R-2",), both))
        spy = GitSpy(replies=lambda query: b"garbage\n")
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertEqual(len(spy.queries()), 1)


FORGED = b"forged content that nobody committed\n"


class ForgedObjects(Case):
    """Every object the gate reads is hashed by the gate against the id it asked for (S53-28)."""

    def setUp(self) -> None:
        super().setUp()
        self.write_snapshot(("R-1", "active"))
        self.blob = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip()
        self.subtree = git(self.repo, "rev-parse", "HEAD:contracts").strip()
        self.root = git(self.repo, "rev-parse", "HEAD^{tree}").strip()
        self.head = git(self.repo, "rev-parse", "HEAD").strip()

    def declare(self, data: bytes) -> None:
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{sha(data)}",)))

    def assert_forgery_is_a_fault(self, oid: str, data: bytes) -> str:
        self.declare(data)
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("TOOL_FAULT "), err)
        self.assertIn(oid, err)
        self.assertIn("does not hash to its id", err)
        self.assertNotIn("SOURCE_", err)
        return err

    def test_a_forged_loose_blob_is_a_fault_naming_its_id_whatever_digest_is_declared(self) -> None:
        self.declare(SOURCE_BYTES)
        self.assert_green()
        forge_loose_object(self.repo, self.blob, "blob", FORGED)
        for data in (FORGED, SOURCE_BYTES):
            with self.subTest(declared=sha(data)[:8]):
                self.assert_forgery_is_a_fault(self.blob, data)

    def test_a_forged_loose_subtree_is_a_fault_naming_its_id(self) -> None:
        forged_blob = write_blob(self.repo, FORGED)
        forge_loose_object(self.repo, self.subtree, "tree", raw_tree(("100644", "source.txt", bytes.fromhex(forged_blob))))
        self.assert_forgery_is_a_fault(self.subtree, FORGED)

    def test_a_forged_loose_root_tree_is_a_fault_naming_its_id(self) -> None:
        forge_loose_object(self.repo, self.root, "tree", raw_tree(("40000", "contracts", bytes.fromhex(self.subtree)), ("100644", "extra.txt", bytes.fromhex(self.blob))))
        self.assert_forgery_is_a_fault(self.root, SOURCE_BYTES)

    def test_a_forged_loose_commit_is_a_fault_naming_its_id(self) -> None:
        stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nforged\n"
        forge_loose_object(self.repo, self.head, "commit", f"tree {self.root}\n{stamp}".encode("ascii"))
        self.declare(SOURCE_BYTES)
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("TOOL_FAULT "), err)
        self.assertIn(self.head, err)

    def test_a_commit_answer_that_does_not_hash_to_the_id_asked_for_is_a_fault_naming_it(self) -> None:
        forged_blob = write_blob(self.repo, FORGED)
        other_subtree = store_object(self.repo, "tree", raw_tree(("100644", "source.txt", bytes.fromhex(forged_blob))))
        other_root = store_object(self.repo, "tree", raw_tree(("40000", "contracts", bytes.fromhex(other_subtree))))
        stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nforged\n"
        answer = object_answer(self.head, "commit", f"tree {other_root}\n{stamp}".encode("ascii"))
        self.declare(FORGED)
        spy = GitSpy(replies=lambda query: answer if query == self.head.encode("ascii") else None)
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("TOOL_FAULT "), err)
        self.assertIn(self.head, err)
        self.assertIn("does not hash to its id", err)
        self.assertEqual(spy.queries(), [self.head.encode("ascii")])

    # ticket 60, S53-30: the comparison of the hash with the id covers every digit of the id
    @staticmethod
    def neighbour(oid: str, flip: int, index: int = -1) -> str:
        """`oid` with one hex digit changed (the last by default): the id of an object that does not exist and differs from `oid` in that digit only."""
        at = index % len(oid)
        return oid[:at] + format(int(oid[at], 16) ^ flip, "x") + oid[at + 1 :]

    def assert_a_near_miss_is_a_fault(self, asked: str, kind: str, body: bytes) -> None:
        answer = object_answer(asked, kind, body)
        spy = GitSpy(replies=lambda query: answer if query == asked.encode("ascii") else None)
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("TOOL_FAULT "), err)
        self.assertIn(asked, err)
        self.assertIn("does not hash to its id", err)
        self.assertNotIn("SOURCE_", err)
        self.assertEqual(spy.queries()[-1], asked.encode("ascii"))
        self.assertEqual(spy.alive(), [])

    def test_a_blob_answer_whose_body_hashes_to_an_id_that_differs_only_in_the_last_digit_is_a_fault(self) -> None:
        genuine = write_blob(self.repo, FORGED)
        for flip in (1, 2, 4, 8):
            asked = self.neighbour(genuine, flip)
            with self.subTest(flip=flip):
                self.assertNotEqual(asked, genuine)
                point_head_at_tree(
                    self.repo,
                    raw_tree(("40000", "contracts", bytes.fromhex(store_object(self.repo, "tree", raw_tree(("100644", "source.txt", bytes.fromhex(asked))))))),
                )
                self.declare(FORGED)
                self.assert_a_near_miss_is_a_fault(asked, "blob", FORGED)

    def test_a_blob_answer_whose_body_hashes_to_an_id_that_differs_in_one_digit_anywhere_is_a_fault(self) -> None:
        genuine = write_blob(self.repo, FORGED)
        for index in (0, 1, 8, 19, 20, 31, 32, 38, 39):
            asked = self.neighbour(genuine, 1, index)
            with self.subTest(index=index):
                self.assertNotEqual(asked, genuine)
                point_head_at_tree(
                    self.repo,
                    raw_tree(("40000", "contracts", bytes.fromhex(store_object(self.repo, "tree", raw_tree(("100644", "source.txt", bytes.fromhex(asked))))))),
                )
                self.declare(FORGED)
                self.assert_a_near_miss_is_a_fault(asked, "blob", FORGED)

    def test_a_tree_answer_whose_body_hashes_to_an_id_that_differs_in_one_digit_anywhere_is_a_fault(self) -> None:
        root_body = git_raw(self.repo, "cat-file", "tree", self.root)
        stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nmessage\n"
        for index in (0, 1, 8, 19, 20, 31, 32, 38, 39):
            asked = self.neighbour(self.root, 1, index)
            with self.subTest(index=index):
                point_head_at_commit(self.repo, f"tree {asked}\n{stamp}".encode("ascii"))
                self.declare(SOURCE_BYTES)
                self.assert_a_near_miss_is_a_fault(asked, "tree", root_body)

    def test_a_tree_answer_whose_body_hashes_to_an_id_that_differs_only_in_the_last_digit_is_a_fault(self) -> None:
        root_body = git_raw(self.repo, "cat-file", "tree", self.root)
        stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nmessage\n"
        for flip in (1, 2, 4, 8):
            asked = self.neighbour(self.root, flip)
            with self.subTest(flip=flip):
                point_head_at_commit(self.repo, f"tree {asked}\n{stamp}".encode("ascii"))
                self.declare(SOURCE_BYTES)
                self.assert_a_near_miss_is_a_fault(asked, "tree", root_body)

    # ticket 60, S53-31: a blob entry that serves an object of another kind is a fault naming the id
    def assert_another_kind_is_a_fault(self, kind: str, body: bytes) -> None:
        forge_loose_object(self.repo, self.blob, kind, body)
        self.declare(SOURCE_BYTES)
        spy = GitSpy()
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertTrue(err.startswith("TOOL_FAULT "), err)
        self.assertIn(self.blob, err)
        self.assertIn("another kind of object", err)
        self.assertIn("mismatch", err)
        self.assertIn(f"({kind})", err)
        self.assertNotIn("SOURCE_", err)
        self.assertEqual(spy.alive(), [])

    def test_a_blob_entry_that_serves_a_tree_is_a_fault_naming_its_id(self) -> None:
        self.assert_another_kind_is_a_fault("tree", raw_tree(("100644", "source.txt", bytes.fromhex(self.blob))))

    def test_a_blob_entry_that_serves_a_commit_is_a_fault_naming_its_id(self) -> None:
        stamp = "author A <a@example.invalid> 0 +0000\ncommitter A <a@example.invalid> 0 +0000\n\nforged\n"
        self.assert_another_kind_is_a_fault("commit", f"tree {self.root}\n{stamp}".encode("ascii"))

    def test_a_blob_entry_that_serves_another_kind_is_a_fault_beside_a_red(self) -> None:
        forge_loose_object(self.repo, self.blob, "tree", raw_tree(("100644", "source.txt", bytes.fromhex(self.blob))))
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        self.declare(SOURCE_BYTES)
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("LITERAL_EXPECTED specs/test_a_red.py: "), out)
        self.assertEqual(len(err.splitlines()), 2, err)
        self.assertIn(self.blob, err.splitlines()[0])

    def test_a_forgery_beside_a_red_exits_1_with_the_fault_and_never_passes(self) -> None:
        forge_loose_object(self.repo, self.blob, "blob", FORGED)
        self.write_spec("test_a_red.py", "", "assert value == 3\n")
        self.declare(FORGED)
        code, out, err = self.run_gate()
        self.assertEqual(code, 1, err)
        self.assertTrue(out.startswith("LITERAL_EXPECTED specs/test_a_red.py: "), out)
        lines = err.splitlines()
        self.assertEqual(len(lines), 2, err)
        self.assertIn(self.blob, lines[0])
        self.assertIn("does not hash to its id", lines[0])

    def test_the_store_is_not_used_again_after_a_forgery(self) -> None:
        self.commit_source("contracts/second.txt", b"other")
        self.write_snapshot(("R-1", "active"), ("R-2", "active"))
        blob = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip()
        forge_loose_object(self.repo, blob, "blob", FORGED)
        both = (f"contracts/source.txt sha256:{sha(FORGED)}", f"contracts/second.txt sha256:{sha(b'other')}")
        self.write_spec("test_a.py", self.header(("R-1",), both))
        self.write_spec("test_b.py", self.header(("R-2",), both))
        spy = GitSpy()
        with spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertEqual(spy.queries()[-1], blob.encode("ascii"))
        self.assertEqual(spy.alive(), [])

    def test_an_honest_store_is_never_called_forged(self) -> None:
        data = bytes(range(256)) * 5000
        self.commit_source("contracts/large.bin", data)
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/large.bin sha256:{sha(data)}", f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}")))
        self.assert_green()

    def test_the_hash_is_the_one_git_gives_an_object(self) -> None:
        for kind, body in (("blob", b""), ("blob", FORGED), ("tree", raw_tree(("100644", "a", bytes(20)))), ("commit", b"tree x\n\nm\n")):
            with self.subTest(kind=kind, size=len(body)):
                oid = store_object(self.repo, kind, body)
                hasher = contract_gate.object_hasher(oid, kind, len(body))
                hasher.update(body)
                self.assertEqual(hasher.hexdigest(), oid)

    def test_an_id_of_another_width_than_the_two_hashes_is_refused(self) -> None:
        for width in (0, 39, 41, 63, 65):
            with self.subTest(width=width), self.assertRaises(contract_gate.ToolFault):
                contract_gate.object_hasher("a" * width, "blob", 0)


class Sha256Repository(Case):
    """A repository whose object ids are SHA-256: ids are 64 digits wide and trees hold 32-byte raw ids."""

    def setUp(self) -> None:
        super().setUp()
        repo = self.base / "repo256"
        repo.mkdir()
        empty_template = self.base / "empty-template-256"
        empty_template.mkdir()
        made = subprocess.run(
            ["git", "-C", str(self.base), "init", "-q", "--object-format=sha256", f"--template={empty_template}", str(repo)],
            capture_output=True,
            env={**os.environ, **GIT_ENVIRONMENT},
            check=False,
        )
        if made.returncode != 0:
            self.skipTest(f"this git cannot make a SHA-256 repository: {made.stderr.decode('utf-8', errors='replace')}")
        for key, value in (("core.autocrlf", "false"), ("core.safecrlf", "false"), ("commit.gpgsign", "false")):
            git(repo, "config", key, value)
        (repo / "contracts").mkdir()
        (repo / "contracts" / "source.txt").write_bytes(SOURCE_BYTES)
        (repo / "specs").mkdir()
        commit_all(repo)
        self.repo, self.specs = repo, repo / "specs"
        self.write_snapshot(("R-1", "active"))
        self.head = git(repo, "rev-parse", "HEAD").strip()
        self.assertEqual(len(self.head), 64)

    def test_a_source_in_a_sha_256_repository_is_read_and_digested(self) -> None:
        self.good_spec("test_one.py", "R-1")
        self.assert_green()
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{sha(b'changed')}",)))
        self.assertEqual(self.codes(), ["SOURCE_DIGEST_MISMATCH"])

    def test_every_query_is_a_64_digit_id_and_the_walk_goes_down_a_directory(self) -> None:
        self.commit_source("contracts/deeper/third.txt", b"third")
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/deeper/third.txt sha256:{sha(b'third')}",)))
        spy = GitSpy()
        with spy.patched():
            self.assert_green()
        self.assertEqual(len(spy.queries()), 5)
        for query in spy.queries():
            self.assertRegex(query.decode("ascii"), r"^[0-9a-f]{64}$")

    def test_a_link_and_a_submodule_and_a_missing_name_are_told_apart(self) -> None:
        track_entry(self.repo, "contracts/link.txt", b"source.txt", "120000")
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{'b' * 64},modules/sub")
        git(self.repo, "commit", "-q", "--no-verify", "-m", "link and gitlink")
        for path, reason in (("contracts/link.txt", "symbolic link"), ("modules/sub", "submodule"), ("contracts/nope.txt", "is not tracked")):
            with self.subTest(path):
                self.write_spec("test_one.py", self.header(("R-1",), (f"{path} sha256:{sha(SOURCE_BYTES)}",)))
                lines = self.red_lines()
                self.assertEqual(len(lines), 1, lines)
                self.assertIn(reason, lines[0])

    def test_a_forged_blob_in_a_sha_256_repository_is_a_fault_naming_its_id(self) -> None:
        blob = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip()
        forge_loose_object(self.repo, blob, "blob", FORGED)
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{sha(FORGED)}",)))
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertIn(blob, err)
        self.assertIn("does not hash to its id", err)

    def test_a_pruned_blob_in_a_sha_256_repository_is_unservable(self) -> None:
        self.good_spec("test_one.py", "R-1")
        remove_loose_object(self.repo, git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip())
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""), err)
        self.assertTrue(err.startswith("SOURCE_UNSERVABLE "), err)


class DeclarationText(Case):
    """A declaration value loses only spaces and tabs; a control character makes it a red of its key."""

    CONTROLS = ("\x01", "\x0b", "\x0c", "\x1b", "\x1c", "\x1f", "\x7f", "\t")

    def run_header(self, header: str) -> tuple[int, list[str]]:
        self.write_snapshot(("R-1", "active"))
        self.write_spec("test_one.py", header)
        code, out, err = self.run_gate()
        self.assertNotIn("TOOL_FAULT", err)
        return code, out.splitlines()

    def good_source(self) -> str:
        return f"contracts/source.txt sha256:{sha(SOURCE_BYTES)}"

    def test_a_control_character_in_a_requirement_value_is_retired_requirement_bound(self) -> None:
        for control in self.CONTROLS:
            for shape in ("R-1{c}", "{c}R-1", "R{c}-1", "R-1{c} "):
                value = shape.format(c=control)
                if value.strip(" \t") == "R-1":
                    continue
                with self.subTest(value=value):
                    code, lines = self.run_header(f"# requirement: {value}\n# source: {self.good_source()}\n# mutation: m\n")
                    self.assertEqual(code, 1, lines)
                    self.assertEqual(sorted(line.split(" ", 1)[0] for line in lines), ["NO_SPEC_FOR_REQUIREMENT", "RETIRED_REQUIREMENT_BOUND"])
                    bound = [line for line in lines if line.startswith("RETIRED_REQUIREMENT_BOUND")]
                    self.assertTrue(bound[0].startswith("RETIRED_REQUIREMENT_BOUND specs/test_one.py: line 1: "), bound[0])

    def test_a_control_character_in_a_source_value_is_source_missing(self) -> None:
        digest = sha(SOURCE_BYTES)
        for control in self.CONTROLS:
            shapes = [f"contracts/so{control}urce.txt sha256:{digest}"]
            if control != "\t":  # a tab around a value is removed, not refused
                shapes += [
                    f"contracts/source.txt{control} sha256:{digest}",
                    f"contracts/source.txt sha256:{digest}{control}",
                    f"{control}contracts/source.txt sha256:{digest}",
                ]
            for shape in shapes:
                with self.subTest(value=shape):
                    code, lines = self.run_header(f"# requirement: R-1\n# source: {shape}\n# mutation: m\n")
                    self.assertEqual(code, 1, lines)
                    self.assertEqual(len(lines), 1, lines)
                    self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])

    def test_a_control_character_in_a_mutation_value_is_no_mutation(self) -> None:
        for control in self.CONTROLS:
            for shape in ("m{c}", "{c}m", "m{c}n"):
                value = shape.format(c=control)
                if value.strip(" \t") == "m":
                    continue
                with self.subTest(value=value):
                    code, lines = self.run_header(f"# requirement: R-1\n# source: {self.good_source()}\n# mutation: {value}\n")
                    self.assertEqual(code, 1, lines)
                    self.assertEqual(len(lines), 1, lines)
                    self.assertTrue(lines[0].startswith("NO_MUTATION specs/test_one.py: line 3: "), lines[0])

    def test_only_spaces_and_tabs_around_a_value_are_removed(self) -> None:
        header = (
            f"#\t requirement:\t  R-1 \t\n#  source: \t{self.good_source()}\t \n# mutation:\t m n \t\n"
        )
        code, lines = self.run_header(header)
        self.assertEqual((code, lines), (0, ["requirements=1 specs=1 defects=0"]))

    def test_characters_that_str_strip_would_remove_do_not_bind_the_requirement(self) -> None:
        for char in ("\x85", "\u2028", "\u2029", "\u00a0", "\u3000", "\u200b"):
            with self.subTest(char=char):
                code, lines = self.run_header(f"# requirement: R-1{char}\n# source: {self.good_source()}\n# mutation: m\n")
                self.assertEqual(code, 1, lines)
                self.assertIn("NO_SPEC_FOR_REQUIREMENT R-1: no spec declares this active requirement", lines)
                self.assertTrue(any(line.startswith("RETIRED_REQUIREMENT_BOUND specs/test_one.py: requirement 'R-1") for line in lines), lines)

    def test_a_control_character_in_free_text_is_not_a_declaration_problem(self) -> None:
        header = "# note \x01\x1b\x1c here\n# SPDX-License-Identifier: MIT\x0b\n" + self.header(("R-1",))
        code, lines = self.run_header(header)
        self.assertEqual((code, lines), (0, ["requirements=1 specs=1 defects=0"]))

    def test_the_text_rule_runs_before_the_url_rule(self) -> None:
        code, lines = self.run_header(f"# requirement: R-1\n# source: https://example.invalid/\x01 sha256:{sha(b'x')}\n# mutation: m\n")
        self.assertEqual(code, 1, lines)
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SOURCE_MISSING specs/test_one.py: line 2: "), lines[0])


class RepoTopLevel(Case):
    """`--repo` is the top level of a git work tree, and git runs without repository-selecting variables."""

    def argv_with_repo(self, repo: Path) -> list[str]:
        return ["--repo", str(repo), "--snapshot", str(self.snapshot), "--specs", str(self.specs)]

    def decoy(self) -> Path:
        decoy = self.base / "decoy"
        decoy.mkdir()
        init_repo(decoy)
        (decoy / "other.txt").write_bytes(b"other")
        commit_all(decoy)
        return decoy

    def test_a_subdirectory_of_the_work_tree_is_exit_2(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        for sub in (self.specs, self.repo / "contracts", self.specs / "inner"):
            with self.subTest(sub.name):
                sub.mkdir(exist_ok=True)
                code, out, err = self.run_gate(self.argv_with_repo(sub))
                self.assertEqual((code, out), (2, ""), err)
                self.assertIn("top level", err)
                self.assertEqual(len(err.splitlines()), 1, err)

    def test_a_plain_directory_inside_the_work_tree_is_exit_2(self) -> None:
        self.write_snapshot()
        plain = self.repo / "plain"
        (plain / "specs").mkdir(parents=True)
        code, out, err = self.run_gate(["--repo", str(plain), "--snapshot", str(self.snapshot), "--specs", str(plain / "specs")])
        self.assertEqual((code, out), (2, ""), err)
        self.assertIn("top level", err)

    def test_a_spelling_of_the_top_level_that_reaches_it_is_accepted(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        for spelling in (str(self.repo) + os.sep, str(self.repo / "specs" / ".."), str(self.repo / "."), str(self.repo).replace("\\", "/")):
            with self.subTest(spelling):
                code, out, err = self.run_gate(["--repo", spelling, "--snapshot", str(self.snapshot), "--specs", str(self.specs)])
                self.assertEqual((code, out.strip(), err), (0, "requirements=1 specs=1 defects=0", ""))

    def test_git_answering_a_toplevel_outside_its_format_is_exit_2(self) -> None:
        self.write_snapshot()
        for answer in (b"", b"\n", b"a\nb\n", b"no newline"):
            with self.subTest(answer=answer):
                done = subprocess.CompletedProcess([], 0, answer, b"")
                with mock.patch.object(contract_gate.subprocess, "run", return_value=done):
                    code, out, err = self.run_gate()
                self.assertEqual((code, out), (2, ""), err)

    def test_an_inherited_repository_variable_does_not_change_the_result(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        baseline = self.run_gate()
        self.assertEqual(baseline, (0, "requirements=1 specs=1 defects=0\n", ""))
        decoy = self.decoy()
        empty_objects = self.base / "empty-objects"
        empty_objects.mkdir()
        hostile = {
            "GIT_DIR": str(decoy / ".git"),
            "GIT_WORK_TREE": str(decoy),
            "GIT_INDEX_FILE": str(self.base / "no-such-index"),
            "GIT_OBJECT_DIRECTORY": str(empty_objects),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(decoy / ".git" / "objects"),
            "GIT_NAMESPACE": "hostile",
            "GIT_CEILING_DIRECTORIES": str(self.base),
            "GIT_COMMON_DIR": str(decoy / ".git"),
        }
        self.assertEqual(set(hostile), {name for name in contract_gate.GIT_SELECTING_VARIABLES} - {"GIT_PREFIX"})
        for name, value in hostile.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(self.run_gate(), baseline)
        with mock.patch.dict(os.environ, hostile):
            self.assertEqual(self.run_gate(), baseline)

    def test_no_git_child_inherits_a_repository_selecting_variable(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        spy = GitSpy()
        polluted = {name: "x" for name in contract_gate.GIT_SELECTING_VARIABLES}
        with mock.patch.dict(os.environ, polluted), spy.patched():
            code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=1 specs=1 defects=0", ""))
        self.assertGreaterEqual(len(spy.calls), 1)
        for call in spy.calls:
            self.assertIsNotNone(call.env)
            names = {name.upper() for name in (call.env or {})}
            self.assertEqual(names & set(contract_gate.GIT_SELECTING_VARIABLES), set(), call.command)

    def test_a_replace_ref_on_a_source_blob_never_redirects_the_lookup(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        self.assertEqual(self.run_gate(), (0, "requirements=1 specs=1 defects=0\n", ""))
        fake = b"a replacement blob\n"
        real_id = git(self.repo, "rev-parse", "HEAD:contracts/source.txt").strip()
        fake_id = subprocess.run(
            ["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
            input=fake,
            capture_output=True,
            env={**os.environ, **GIT_ENVIRONMENT},
            check=True,
        ).stdout.decode("ascii").strip()
        git(self.repo, "replace", real_id, fake_id)
        self.assertEqual(git(self.repo, "show", "HEAD:contracts/source.txt").encode("utf-8"), fake)
        self.assertEqual(self.run_gate(), (0, "requirements=1 specs=1 defects=0\n", ""))
        self.write_spec("test_one.py", self.header(("R-1",), (f"contracts/source.txt sha256:{sha(fake)}",)))
        self.assertEqual(self.codes(), ["SOURCE_DIGEST_MISMATCH"])

    def test_every_git_child_ignores_replace_refs_and_never_fetches(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        spy = GitSpy()
        with spy.patched():
            self.assert_green()
        self.assertGreaterEqual(len(spy.calls), 3)
        for call in spy.calls:
            self.assertIn("--no-replace-objects", call.command, call.command)
            self.assertEqual((call.env or {}).get("GIT_NO_REPLACE_OBJECTS"), "1", call.command)
            self.assertEqual((call.env or {}).get("GIT_NO_LAZY_FETCH"), "1", call.command)

    def test_the_git_environment_overrides_a_hostile_replace_or_fetch_setting(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_NO_REPLACE_OBJECTS": "0", "GIT_NO_LAZY_FETCH": "0"}):
            environment = contract_gate._git_environment()
        self.assertEqual((environment["GIT_NO_REPLACE_OBJECTS"], environment["GIT_NO_LAZY_FETCH"]), ("1", "1"))

    def test_git_configuration_variables_never_reach_git_and_do_not_change_the_result(self) -> None:
        self.write_snapshot(("R-1", "active"))
        self.good_spec("test_one.py", "R-1")
        baseline = self.run_gate()
        self.assertEqual(baseline, (0, "requirements=1 specs=1 defects=0\n", ""))
        bare = self.base / "bare.config"
        bare.write_text("[core]\n\tbare = true\n", encoding="utf-8")
        hostile = {
            "GIT_CONFIG": str(bare),
            "GIT_CONFIG_GLOBAL": str(bare),
            "GIT_CONFIG_SYSTEM": str(bare),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.bare",
            "GIT_CONFIG_VALUE_0": "true",
            "GIT_CONFIG_PARAMETERS": "'core.bare=true'",
        }
        for name, value in hostile.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertNotIn(name, contract_gate._git_environment())
                self.assertEqual(self.run_gate(), baseline)
        with mock.patch.dict(os.environ, hostile):
            self.assertEqual(self.run_gate(), baseline)

    def test_the_environment_given_to_git_keeps_everything_else(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_DIR": "x", "GIT_AUTHOR_NAME": "kept", "SOME_OTHER": "kept too"}):
            environment = contract_gate._git_environment()
        self.assertNotIn("GIT_DIR", environment)
        self.assertEqual((environment["GIT_AUTHOR_NAME"], environment["SOME_OTHER"]), ("kept", "kept too"))


class SnapshotKeys(Case):
    def expect_three(self, text: str) -> str:
        self.snapshot.write_text(text, encoding="utf-8")
        code, out, err = self.run_gate()
        self.assertEqual((code, out), (3, ""), err)
        self.assertIn("is not a snapshot", err)
        return err

    def test_a_repeated_key_in_any_object_is_not_a_snapshot(self) -> None:
        shapes = {
            "top level": '{"rows": [], "rows": []}',
            "escaped spelling of the same key": '{"rows": [], "\\u0072ows": []}',
            "in a row": '{"rows": [{"requirement_id": "R-1", "requirement_id": "R-2", "status": "active"}]}',
            "status repeated": '{"rows": [{"requirement_id": "R-1", "status": "active", "status": "retired"}]}',
            "in an unrelated object": '{"rows": [], "meta": {"a": 1, "a": 2}}',
            "in a nested list": '{"rows": [], "meta": [{"a": 1, "a": 1}]}',
        }
        for name, text in shapes.items():
            with self.subTest(name):
                self.assertIn("repeated", self.expect_three(text))

    def test_keys_that_differ_are_not_repeated(self) -> None:
        self.snapshot.write_text('{"rows": [], "ROWS": [], "Rows": []}', encoding="utf-8")
        code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=0 specs=0 defects=0", ""))

    def test_a_snapshot_with_no_repeated_key_is_read_as_before(self) -> None:
        self.write_snapshot(("R-1", "active"), ("R-2", "retired"))
        self.good_spec("test_one.py", "R-1")
        self.assert_green()


class LinksNotFollowed(Case):
    def link(self, link: Path, target: Path, directory: bool = True) -> None:
        """Make a symbolic link, or on Windows a junction; skip the test when neither can be made."""
        try:
            os.symlink(target, link, target_is_directory=directory)
        except (OSError, NotImplementedError):
            if os.name != "nt" or not directory:
                self.skipTest("this host cannot make a link here")
            made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, check=False)
            if made.returncode != 0:
                self.skipTest("this host cannot make a junction")
        remove = os.rmdir if os.name == "nt" and directory else os.unlink
        self.addCleanup(remove, link)

    def prepare_outside(self) -> Path:
        outside = self.repo / "elsewhere"
        outside.mkdir()
        (outside / "test_far.py").write_text("def test_far():\n    assert compute() == 3\n", encoding="utf-8")
        return outside

    def test_a_directory_link_or_junction_under_specs_is_not_followed(self) -> None:
        outside = self.prepare_outside()
        self.write_snapshot()
        code, out, _ = self.run_gate(self.argv(outside))
        self.assertEqual(code, 1, out)
        self.assertEqual(len(out.splitlines()), 1, out)
        self.link(self.specs / "linked", outside)
        nested = self.specs / "deep" / "er"
        nested.mkdir(parents=True)
        self.link(nested / "again", outside)
        code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=0 specs=0 defects=0", ""))

    def test_a_link_to_a_spec_file_is_not_followed(self) -> None:
        outside = self.prepare_outside()
        self.write_snapshot()
        self.link(self.specs / "test_linked.py", outside / "test_far.py", directory=False)
        code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=0 specs=0 defects=0", ""))

    def test_real_directories_beside_a_link_are_still_walked(self) -> None:
        outside = self.prepare_outside()
        self.write_snapshot(("R-1", "active"))
        self.link(self.specs / "linked", outside)
        self.write_spec("real/test_real.py", self.header(("R-1",)))
        code, out, err = self.run_gate()
        self.assertEqual((code, out.strip(), err), (0, "requirements=1 specs=1 defects=0", ""))


class OneLineMessages(Case):
    def test_a_usage_message_with_hostile_text_is_two_lines_and_forges_nothing(self) -> None:
        for hostile in ("--bogus\nCODE forged", "--bogus\r\nCODE forged", "--bogus\u2028x\u0085y", "--bogus\x1b[2J\x00", "--bogus\udc80"):
            with self.subTest(hostile):
                code, out, err = self.run_gate([hostile])
                self.assertEqual((code, out), (3, ""))
                lines = err.splitlines()
                self.assertEqual(len(lines), 2, repr(err))
                self.assertEqual(err.count("\n"), 2, repr(err))
                self.assertTrue(lines[0].startswith("usage: "), lines[0])
                self.assertTrue(lines[1].startswith("contract_gate.py: error: unknown option or argument "), lines[1])
                self.assertTrue(all(char.isprintable() for char in err.replace("\n", "")), repr(err))

    def test_a_hostile_snapshot_error_is_one_escaped_line(self) -> None:
        self.write_snapshot()
        name = self.base / "snap\u2028shot\u0085.json"
        try:
            name.write_text("not json", encoding="utf-8")
        except OSError:
            self.skipTest("this file system refuses the name")
        code, out, err = self.run_gate(self.argv_with_snapshot(name))
        self.assertEqual((code, out), (3, ""))
        self.assertEqual(len(err.splitlines()), 2, repr(err))
        self.assertIn("\\u2028", err)

    def argv_with_snapshot(self, snapshot: Path) -> list[str]:
        return ["--repo", str(self.repo), "--snapshot", str(snapshot), "--specs", str(self.specs)]

    def test_a_hostile_missing_snapshot_is_one_escaped_fault_line(self) -> None:
        missing = self.base / "gone\u2028\u0085.json"
        code, out, err = self.run_gate(self.argv_with_snapshot(missing))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, repr(err))
        self.assertEqual(err.count("\n"), 1, repr(err))
        self.assertIn("\\u2028", err)

    def test_a_fault_with_a_hostile_label_and_message_is_one_line(self) -> None:
        fault = contract_gate.ToolFault("LA\nBEL\u2028", "msg\r\nCODE forged\u0085\x1b\udc80")
        with mock.patch.object(contract_gate, "run", side_effect=fault):
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, repr(err))
        self.assertEqual(err.count("\n"), 1, repr(err))
        self.assertTrue(err.startswith("LA\\nBEL\\u2028 msg\\r\\nCODE forged"), repr(err))

    def test_a_collected_fault_with_a_hostile_label_and_message_is_one_line_beside_a_red(self) -> None:
        fault = contract_gate.ToolFault("LA\nBEL ", "msg\r\nCODE forged\u0085\x1b\udc80")
        red = contract_gate.Defect("NO_MUTATION", "specs/test_a.py", "detail")
        for defects, expected in (((), 2), ((red,), 1)):
            with self.subTest(expected=expected):
                report = contract_gate.Report(1, 1, defects, (fault,))
                with mock.patch.object(contract_gate, "run", return_value=report):
                    code, out, err = self.run_gate()
                self.assertEqual(code, expected)
                lines = err.splitlines()
                count = 1 if expected == 2 else 2
                self.assertEqual(len(lines), count, repr(err))
                self.assertEqual(err.count("\n"), count, repr(err))
                self.assertTrue(lines[0].startswith("LA\\nBEL\\u2028 msg\\r\\nCODE forged"), repr(err))

    def test_an_unexpected_error_with_a_hostile_message_is_one_line(self) -> None:
        with mock.patch.object(contract_gate, "run", side_effect=RuntimeError("a\nb\u2028c\x1b")):
            code, out, err = self.run_gate()
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(err, "TOOL_FAULT unexpected RuntimeError: a\\nb\\u2028c\\x1b\n")

    def test_the_real_command_line_prints_one_line_for_a_fault_and_two_for_a_usage_error(self) -> None:
        fault = subprocess.run([sys.executable, str(SCRIPT), *self.argv()], capture_output=True, text=True)
        self.assertEqual((fault.returncode, fault.stdout, len(fault.stderr.splitlines())), (2, "", 1))
        usage = subprocess.run([sys.executable, str(SCRIPT), "--x\nforged"], capture_output=True, text=True)
        self.assertEqual((usage.returncode, usage.stdout, len(usage.stderr.splitlines())), (3, "", 2))
        self.assertNotIn("Traceback", fault.stderr + usage.stderr)


class ReadmeNamesEveryScript(unittest.TestCase):
    NUMBER_WORDS = {
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
        "Six": 6,
        "Seven": 7,
        "Eight": 8,
        "Nine": 9,
        "Ten": 10,
        "Eleven": 11,
        "Twelve": 12,
        "Thirteen": 13,
        "Fourteen": 14,
        "Fifteen": 15,
        "Sixteen": 16,
        "Seventeen": 17,
        "Eighteen": 18,
        "Nineteen": 19,
        "Twenty": 20,
    }

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

    def test_the_number_words_run_from_two_to_twenty_without_a_gap(self) -> None:
        self.assertEqual(sorted(self.NUMBER_WORDS.values()), list(range(2, 21)))
        self.assertEqual(self.NUMBER_WORDS["Nine"], 9)
        self.assertEqual(self.NUMBER_WORDS["Twenty"], 20)

    def contract_gate_section(self) -> str:
        return " ".join(self.readme.split("## contract_gate.py", 1)[1].split("\n## ", 1)[0].split())

    def test_the_contract_gate_section_says_red_before_fault(self) -> None:
        section = self.contract_gate_section()
        for stale in ("a fault stops the run", "no defect is printed", "a fault never exits 1", "A tracked symbolic link is a blob of its link text"):
            with self.subTest(stale):
                self.assertNotIn(stale, section)
        for phrase in ("red before fault", "resolved once", "symbolic link", "submodule", "one `cat-file --batch` process", "stderr"):
            with self.subTest(phrase):
                self.assertIn(phrase, section)

    def test_the_contract_gate_section_says_every_object_is_hashed_by_the_gate(self) -> None:
        section = self.contract_gate_section()
        for phrase in (
            "Every object the gate reads is hashed by the gate against the id it asked for",
            "SHA-1 or SHA-256 chosen by the width of the id",
            "naming the id",
            "walks the trees from the root by object id",
            "HEAD does not name a commit",
        ):
            with self.subTest(phrase):
                self.assertIn(phrase, section)
        self.assertNotIn("asks for that commit's tree", section)
        docstring = contract_gate.__doc__ or ""
        self.assertIn("Every object the gate reads is hashed by the gate against the id it asked for", " ".join(docstring.split()))

    def test_the_contract_gate_section_describes_spaces_tabs_and_the_usage_line_as_the_code_does(self) -> None:
        section = self.contract_gate_section()
        self.assertIn("only the spaces and tabs around it are removed", section)
        self.assertIn("usage banner and one escaped error line", section)

    def test_the_unexpected_error_rule_names_every_script(self) -> None:
        paragraphs = [text for text in self.introduction.split("\n\n") if "unexpected error" in text]
        self.assertEqual(len(paragraphs), 1, paragraphs)
        for name in self.scripts:
            with self.subTest(name):
                self.assertIn(name, paragraphs[0])


if __name__ == "__main__":
    unittest.main()
