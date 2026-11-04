"""Behavioural tests for the coverage_map gate script (exit codes 0/1/2/3).

Every fixture is a throwaway git repository built in a temporary directory; every expected
id, count and message part is derived from the sources the fixture wrote.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import coverage_map as cm  # noqa: E402

SCRIPT = _SCRIPTS / "coverage_map.py"
MAP = "gov/coverage-map.json"
SPECS = "specs"
SPEC_A = "specs/test_a.py"
NON_CP950 = chr(0x0E01)  # outside code page 950
CODES = (
    "UNMAPPED_REMOVAL",
    "CARRIED_TARGET_MISSING",
    "DROPPED_WITHOUT_REASON",
    "ESCALATED_WITHOUT_TICKET",
    "MAP_ROW_INVALID",
)


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.protectNTFS=false", *args],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr}")
    return done.stdout


def git_bytes(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.protectNTFS=false", *args],
        cwd=repo, capture_output=True, input=data,
    )
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr!r}")
    return done.stdout


class Repo:
    """A temporary repository; each commit writes (or deletes) the given files.

    `raw` adds index entries no working-tree file backs: path bytes -> (mode, content). Mode
    160000 takes a commit id as content; other modes take the blob bytes. `git add -A` drops
    such entries on the next commit, so every commit names the raw entries it wants kept.
    """

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="covmap-")
        self.dir = Path(self.tmp.name)
        git(self.dir, "init", "-q", "-b", "main")
        git(self.dir, "config", "core.autocrlf", "false")

    def close(self) -> None:
        def writable(function: Callable[[str], object], path: str, _info: object) -> None:
            os.chmod(path, stat.S_IWRITE)
            function(path)

        try:
            self.tmp.cleanup()
        except OSError:
            import shutil

            shutil.rmtree(self.dir, onerror=writable)

    def commit(
        self,
        files: Mapping[str, str | None],
        newline: str = "\n",
        raw: Mapping[bytes, tuple[str, bytes]] | None = None,
    ) -> str:
        for name, body in files.items():
            target = self.dir / name
            if body is None:
                target.unlink()
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8", newline=newline) as handle:
                handle.write(body)
        git(self.dir, "add", "-A")
        if raw:
            records = b""
            for path, (mode, content) in raw.items():
                if mode == "160000":
                    object_id = content.decode("ascii")
                else:
                    object_id = git_bytes(self.dir, "hash-object", "-w", "--stdin", data=content).decode("ascii").strip()
                records += f"{mode} {object_id}\t".encode("ascii") + path + b"\0"
            git_bytes(self.dir, "update-index", "-z", "--index-info", data=records)
        git(self.dir, "commit", "-q", "--allow-empty", "-m", "c")
        return git(self.dir, "rev-parse", "HEAD").strip()


@dataclass(frozen=True)
class Result:
    code: int
    out: str
    err: str

    @property
    def lines(self) -> list[str]:
        return self.out.splitlines()

    def defect_codes(self) -> list[str]:
        return [line.split(" ", 1)[0] for line in self.lines[:-1]]


def run(repo: Repo, base: str, candidate: str, *, map_path: str = MAP, specs: str = SPECS) -> Result:
    return run_args(["--repo", str(repo.dir), "--base", base, "--candidate", candidate, "--map", map_path, "--specs", specs])


def run_args(argv: Sequence[str]) -> Result:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cm.main(argv)
    return Result(code, out.getvalue(), err.getvalue())


def functions(*names: str, indent: str = "") -> str:
    return "".join(f"{indent}def {name}():\n{indent}    pass\n\n" for name in names)


def row(assertion: str, disposition: str, carried_to: str = "", reason: str = "", ticket: str = "") -> dict[str, str]:
    return {"assertion": assertion, "disposition": disposition, "carried_to": carried_to, "reason": reason, "ticket": ticket}


def map_text(*rows: Mapping[str, object]) -> str:
    return json.dumps({"rows": list(rows)})


def tid(path: str, *parts: str) -> str:
    return "::".join((path, *parts))


class GuardCase(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.addCleanup(self.repo.close)

    def removal(self, map_body: str | None, *, before: str | None = None, after: str | None = None) -> Result:
        """Base has test_one and test_two; the candidate drops test_two (and carries the map)."""
        base = self.repo.commit({SPEC_A: before if before is not None else functions("test_one", "test_two")})
        files: dict[str, str | None] = {SPEC_A: after if after is not None else functions("test_one")}
        if map_body is not None:
            files[MAP] = map_body
        candidate = self.repo.commit(files)
        return run(self.repo, base, candidate)

    def assert_red(self, result: Result, *codes: str) -> None:
        self.assertEqual(result.code, 1, result.out + result.err)
        self.assertEqual(sorted(result.defect_codes()), sorted(codes), result.out)
        self.assertEqual(result.err, "")

    def summary(self, result: Result) -> str:
        return result.lines[-1]


class NormalBehaviourTests(GuardCase):
    def test_removed_test_carried_to_a_new_test_passes(self) -> None:
        body = map_text(row(tid(SPEC_A, "test_two"), "carried", tid(SPEC_A, "test_three")))
        result = self.removal(body, after=functions("test_one", "test_three"))
        self.assertEqual((result.code, result.out, result.err), (0, "removed=1 defects=0\n", ""))

    def test_nothing_removed_and_no_map_passes(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        result = run(self.repo, base, candidate)
        self.assertEqual((result.code, result.out), (0, "removed=0 defects=0\n"))

    def test_dropped_with_reason_and_escalated_with_ticket_pass(self) -> None:
        before = functions("test_one", "test_two", "test_three")
        base = self.repo.commit({SPEC_A: before})
        candidate = self.repo.commit({
            SPEC_A: functions("test_one"),
            MAP: map_text(
                row(tid(SPEC_A, "test_two"), "dropped", reason="superseded by the contract"),
                row(tid(SPEC_A, "test_three"), "escalated", ticket="ref-9"),
            ),
        })
        result = run(self.repo, base, candidate)
        self.assertEqual((result.code, result.out), (0, "removed=2 defects=0\n"))

    def test_map_absent_with_removals_is_unmapped_for_each(self) -> None:
        result = self.removal(None, before=functions("test_one", "test_two", "test_three"), after=functions("test_one"))
        self.assert_red(result, "UNMAPPED_REMOVAL", "UNMAPPED_REMOVAL")
        self.assertEqual(self.summary(result), "removed=2 defects=2")

    def test_map_absent_with_a_spec_added_passes(self) -> None:
        base = self.repo.commit({"README": "x\n"})
        candidate = self.repo.commit({SPEC_A: functions("test_one")})
        self.assertEqual(run(self.repo, base, candidate).code, 0)

    def test_base_equal_to_candidate_passes(self) -> None:
        sha = self.repo.commit({SPEC_A: functions("test_one")})
        self.assertEqual(run(self.repo, sha, sha).out, "removed=0 defects=0\n")


class DefectCodeTests(GuardCase):
    def test_unmapped_removal(self) -> None:
        result = self.removal(map_text(row(tid(SPEC_A, "test_other"), "dropped", reason="r")))
        self.assert_red(result, "UNMAPPED_REMOVAL")
        self.assertIn(json.dumps(tid(SPEC_A, "test_two")), result.lines[0])
        self.assertEqual(self.summary(result), "removed=1 defects=1")

    def test_two_removed_tests_with_one_row_give_one_unmapped(self) -> None:
        result = self.removal(
            map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r")),
            before=functions("test_one", "test_two", "test_three"),
            after=functions("test_one"),
        )
        self.assert_red(result, "UNMAPPED_REMOVAL")
        self.assertIn("test_three", result.lines[0])
        self.assertEqual(self.summary(result), "removed=2 defects=1")

    def test_carried_target_missing_variants(self) -> None:
        targets = {
            "empty": "",
            "whitespace": "   ",
            "unknown": tid(SPEC_A, "test_nowhere"),
            "itself": tid(SPEC_A, "test_two"),
            "padded": " " + tid(SPEC_A, "test_one"),
            "other file": tid("specs/test_gone.py", "test_one"),
        }
        for label, target in targets.items():
            with self.subTest(label):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "carried", target))})
                result = run(repo, base, candidate)
                self.assert_red(result, "CARRIED_TARGET_MISSING")
                self.assertIn("is empty" if label == "empty" else "names no test", result.lines[0])

    def test_carried_to_an_existing_test_in_another_file_passes(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({
            SPEC_A: functions("test_one"),
            "specs/test_b.py": functions("test_two"),
            MAP: map_text(row(tid(SPEC_A, "test_two"), "carried", tid("specs/test_b.py", "test_two"))),
        })
        self.assertEqual(run(self.repo, base, candidate).out, "removed=1 defects=0\n")

    def test_dropped_without_reason(self) -> None:
        for reason in ("", " ", "\u3000"):
            with self.subTest(repr(reason)):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason=reason, ticket="ref-1"))})
                self.assert_red(run(repo, base, candidate), "DROPPED_WITHOUT_REASON")

    def test_escalated_without_ticket(self) -> None:
        for ticket in ("", " ", "\u3000"):
            with self.subTest(repr(ticket)):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "escalated", reason="why", ticket=ticket))})
                self.assert_red(run(repo, base, candidate), "ESCALATED_WITHOUT_TICKET")

    def test_map_row_invalid_row_shapes(self) -> None:
        good = tid(SPEC_A, "test_two")
        shapes: dict[str, object] = {
            "unknown disposition": row(good, "kept"),
            "wrong case": row(good, "Dropped", reason="r"),
            "empty disposition": row(good, ""),
            "missing reason": {k: v for k, v in row(good, "dropped", reason="r").items() if k != "reason"},
            "missing assertion": {k: v for k, v in row(good, "dropped", reason="r").items() if k != "assertion"},
            "null field": {**row(good, "dropped", reason="r"), "ticket": None},
            "number field": {**row(good, "dropped", reason="r"), "carried_to": 3},
            "list field": {**row(good, "dropped", reason="r"), "reason": ["r"]},
            "empty assertion": row("", "dropped", reason="r"),
            "blank assertion": row("  ", "dropped", reason="r"),
            "not an object": "text",
            "null row": None,
        }
        for label, shape in shapes.items():
            with self.subTest(label):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: json.dumps({"rows": [shape]})})
                result = run(repo, base, candidate)
                self.assertEqual(result.code, 1)
                self.assertIn("MAP_ROW_INVALID", result.defect_codes())
                self.assertIn("rows[0]", result.lines[0])

    def test_assertion_with_surrounding_whitespace_is_invalid_not_trimmed(self) -> None:
        padded = " " + tid(SPEC_A, "test_two") + " "
        result = self.removal(map_text(row(padded, "dropped", reason="r")))
        self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")

    def test_duplicate_assertion_is_invalid_and_covers_nothing(self) -> None:
        both = row(tid(SPEC_A, "test_two"), "dropped", reason="r")
        result = self.removal(map_text(both, both))
        self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
        self.assertIn("rows[1]", [line for line in result.lines if line.startswith("MAP_ROW_INVALID")][0])

    def test_file_level_invalid_maps(self) -> None:
        bodies = {
            "not json": "{nope",
            "empty file": "",
            "array": "[]",
            "missing rows": "{}",
            "rows not array": json.dumps({"rows": {"a": 1}}),
            "rows null": json.dumps({"rows": None}),
            "bom": "\ufeff" + map_text(),
        }
        for label, body in bodies.items():
            with self.subTest(label):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: body})
                result = run(repo, base, candidate)
                self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                self.assertIn(json.dumps(MAP), result.lines[0])

    def test_invalid_map_with_nothing_removed_is_still_red(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP: "{nope"})
        self.assert_red(run(self.repo, base, candidate), "MAP_ROW_INVALID")

    def test_map_that_is_not_utf8_is_invalid(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        self.repo.commit({SPEC_A: functions("test_one")})
        (self.repo.dir / MAP).parent.mkdir(parents=True, exist_ok=True)
        with open(self.repo.dir / MAP, "wb") as handle:
            handle.write(b'{"rows": [], "x": "\xff"}')
        git(self.repo.dir, "add", "-A")
        git(self.repo.dir, "commit", "-q", "-m", "m")
        head = git(self.repo.dir, "rev-parse", "HEAD").strip()
        self.assert_red(run(self.repo, base, head), "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")

    def test_a_shape_invalid_row_covers_nothing_and_the_removed_id_is_still_printed(self) -> None:
        good = tid(SPEC_A, "test_two")
        shapes: dict[str, object] = {
            "unknown disposition": row(good, "kept"),
            "missing field": {k: v for k, v in row(good, "dropped", reason="r").items() if k != "reason"},
            "non-string field": {**row(good, "dropped", reason="r"), "ticket": 3},
            "control character": row(good, "dropped", reason="line\nbreak"),
            "padded assertion": row(" " + good, "dropped", reason="r"),
        }
        expected = "UNMAPPED_REMOVAL " + json.dumps(good) + " removed test has no map row"
        for label, shape in shapes.items():
            with self.subTest(label):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: json.dumps({"rows": [shape]})})
                result = run(repo, base, candidate)
                self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                self.assertIn(expected, result.lines)
                self.assertEqual(self.summary(result), "removed=1 defects=2")

    def test_a_string_with_a_control_character_or_lone_surrogate_makes_its_row_invalid(self) -> None:
        good = tid(SPEC_A, "test_two")
        for key in ("assertion", "disposition", "carried_to", "reason", "ticket"):
            for label, value in {"newline": "a\nb", "nul": "a\x00b", "delete": "a\x7fb", "tab": "\t", "surrogate": "a\ud800b"}.items():
                with self.subTest(key=key, value=label):
                    repo = Repo()
                    self.addCleanup(repo.close)
                    base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                    shaped = {**row(good, "dropped", reason="r"), key: value}
                    candidate = repo.commit({SPEC_A: functions("test_one"), MAP: json.dumps({"rows": [shaped]})})
                    result = run(repo, base, candidate)
                    self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                    self.assertEqual(result.lines[0], "MAP_ROW_INVALID \"rows[0]\" field " + key + " holds " + ("a lone surrogate" if label == "surrogate" else "a control character"))

    def test_a_map_path_that_is_not_a_regular_file_is_invalid_for_the_file(self) -> None:
        kinds: dict[str, Callable[[str], tuple[Mapping[str, str | None], Mapping[bytes, tuple[str, bytes]] | None]]] = {
            "tree": lambda seed: ({MAP + "/note.txt": "x\n"}, None),
            "submodule": lambda seed: ({}, {MAP.encode(): ("160000", seed.encode("ascii"))}),
            "link": lambda seed: ({}, {MAP.encode(): ("120000", map_text().encode())}),
        }
        for label, build in kinds.items():
            with self.subTest(label):
                repo = Repo()
                self.addCleanup(repo.close)
                seed = repo.commit({"x.txt": "1\n"})
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                files, raw = build(seed)
                candidate = repo.commit({SPEC_A: functions("test_one"), **files}, raw=raw)
                result = run(repo, base, candidate)
                self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                self.assertEqual(result.lines[0], "MAP_ROW_INVALID " + json.dumps(MAP) + " map path is not a file")
                self.assertEqual(self.summary(result), "removed=1 defects=2")

    def test_a_map_path_that_is_a_tree_is_invalid_even_when_nothing_was_removed(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP + "/note.txt": "x\n"})
        self.assert_red(run(self.repo, base, candidate), "MAP_ROW_INVALID")

    def test_empty_rows_and_empty_fields(self) -> None:
        self.assert_red(self.removal(map_text()), "UNMAPPED_REMOVAL")
        result = self.removal(map_text(row(tid(SPEC_A, "test_two"), "carried", "", "", "")))
        self.assert_red(result, "CARRIED_TARGET_MISSING")

    def test_rows_of_kept_tests_are_shape_checked_but_not_judged(self) -> None:
        stale = row(tid(SPEC_A, "test_one"), "dropped", reason="")
        done = row(tid(SPEC_A, "test_two"), "dropped", reason="r")
        self.assertEqual(self.removal(map_text(stale, done)).out, "removed=1 defects=0\n")
        broken = row(tid(SPEC_A, "test_one"), "nonsense")
        self.assert_red(self.removal(map_text(broken, done)), "MAP_ROW_INVALID")

    def test_extra_row_keys_are_tolerated(self) -> None:
        extra = {**row(tid(SPEC_A, "test_two"), "dropped", reason="r"), "note": "x"}
        self.assertEqual(self.removal(map_text(extra)).code, 0)

    def test_codes_are_distinct_and_a_red_never_exits_2(self) -> None:
        self.assertEqual(len(set(CODES)), 5)
        self.assertEqual({code.value for code in cm.DefectCode}, set(CODES))
        bodies = [
            None,
            map_text(row(tid(SPEC_A, "test_two"), "carried")),
            map_text(row(tid(SPEC_A, "test_two"), "dropped")),
            map_text(row(tid(SPEC_A, "test_two"), "escalated")),
            map_text(row(tid(SPEC_A, "test_two"), "wat")),
        ]
        seen: set[str] = set()
        for body in bodies:
            repo = Repo()
            self.addCleanup(repo.close)
            base = repo.commit({SPEC_A: functions("test_one", "test_two")})
            files: dict[str, str | None] = {SPEC_A: functions("test_one")}
            if body is not None:
                files[MAP] = body
            result = run(repo, base, repo.commit(files))
            self.assertEqual(result.code, 1)
            seen.update(result.defect_codes())
        self.assertEqual(seen, set(CODES))

    def test_map_is_read_at_the_candidate_not_the_working_tree(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one")})
        later = self.repo.commit({MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))})
        self.assert_red(run(self.repo, base, candidate), "UNMAPPED_REMOVAL")
        self.assertEqual(run(self.repo, base, later).code, 0)
        # the working tree copy counts for nothing, in either direction
        with open(self.repo.dir / MAP, "w", encoding="utf-8") as handle:
            handle.write(map_text())
        self.assertEqual(run(self.repo, base, later).code, 0)
        with open(self.repo.dir / MAP, "w", encoding="utf-8") as handle:
            handle.write(map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r")))
        self.assert_red(run(self.repo, base, candidate), "UNMAPPED_REMOVAL")


class EnumerationTests(GuardCase):
    def removed_ids(self, before: Mapping[str, str | None], after: Mapping[str, str | None], specs: str = SPECS) -> list[str]:
        base = self.repo.commit(before)
        candidate = self.repo.commit(after)
        result = run(self.repo, base, candidate, specs=specs)
        self.assertEqual(result.code, 1 if result.lines[-1] != "removed=0 defects=0" else 0, result.out + result.err)
        return sorted(json.loads(line.split(" ", 2)[1]) for line in result.lines[:-1] if line.startswith("UNMAPPED_REMOVAL"))

    def test_renamed_test_counts_as_removed_under_its_old_id(self) -> None:
        ids = self.removed_ids({SPEC_A: functions("test_one")}, {SPEC_A: functions("test_uno")})
        self.assertEqual(ids, [tid(SPEC_A, "test_one")])

    def test_test_moved_to_another_file_counts_as_removed(self) -> None:
        ids = self.removed_ids({SPEC_A: functions("test_one")}, {SPEC_A: "", "specs/test_b.py": functions("test_one")})
        self.assertEqual(ids, [tid(SPEC_A, "test_one")])

    def test_class_level_tests_nested_classes_and_async(self) -> None:
        before = (
            "class Alpha:\n    def test_m(self):\n        pass\n\n"
            "    class Inner:\n        async def test_deep(self):\n            pass\n\n"
            "async def test_async():\n    pass\n"
        )
        ids = self.removed_ids({SPEC_A: before}, {SPEC_A: "x = 1\n"})
        self.assertEqual(ids, sorted([tid(SPEC_A, "test_async"), tid(SPEC_A, "Alpha", "test_m"), tid(SPEC_A, "Alpha", "Inner", "test_deep")]))

    def test_only_functions_starting_with_test_count(self) -> None:
        before = (
            "def helper():\n    pass\n\n"
            "def check_x():\n    pass\n\n"
            "def test_real():\n    def test_inner():\n        pass\n\n"
            "class Box:\n    def setup(self):\n        pass\n    test_attr = 1\n"
        )
        ids = self.removed_ids({SPEC_A: before}, {SPEC_A: "x = 1\n"})
        self.assertEqual(ids, [tid(SPEC_A, "test_real")])

    def test_tests_inside_module_level_blocks_count(self) -> None:
        before = "import sys\nif sys.platform:\n    def test_cond():\n        pass\ntry:\n    def test_try():\n        pass\nexcept ImportError:\n    pass\n"
        ids = self.removed_ids({SPEC_A: before}, {SPEC_A: "x = 1\n"})
        self.assertEqual(ids, sorted([tid(SPEC_A, "test_cond"), tid(SPEC_A, "test_try")]))

    def test_a_file_deleted_entirely_removes_every_test(self) -> None:
        ids = self.removed_ids({SPEC_A: functions("test_one", "test_two")}, {SPEC_A: None})
        self.assertEqual(ids, [tid(SPEC_A, "test_one"), tid(SPEC_A, "test_two")])

    def test_a_spec_added_at_the_candidate_removes_nothing(self) -> None:
        base = self.repo.commit({"x.txt": "1\n"})
        candidate = self.repo.commit({SPEC_A: functions("test_one")})
        self.assertEqual(run(self.repo, base, candidate).out, "removed=0 defects=0\n")

    def test_crlf_files(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")}, newline="\r\n")
        candidate = self.repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))}, newline="\r\n")
        self.assertEqual(run(self.repo, base, candidate).out, "removed=1 defects=0\n")

    def test_a_test_defined_twice_is_removed_only_when_no_definition_remains(self) -> None:
        ids = self.removed_ids({SPEC_A: functions("test_one", "test_one")}, {SPEC_A: functions("test_one")})
        self.assertEqual(ids, [])

    def test_non_ascii_names_are_printed_escaped(self) -> None:
        name = "test_" + NON_CP950
        ids = self.removed_ids({SPEC_A: functions(name)}, {SPEC_A: "x = 1\n"})
        self.assertEqual(ids, [tid(SPEC_A, name)])

    def test_only_test_py_files_are_specs(self) -> None:
        files = {
            "specs/helper.py": functions("test_a"),
            "specs/test_x.txt": functions("test_b"),
            "specs/mytest_x.py": functions("test_c"),
            "specs/test_real.py": functions("test_d"),
        }
        ids = self.removed_ids(files, {name: None for name in files})
        self.assertEqual(ids, [tid("specs/test_real.py", "test_d")])


BLOCKS = {
    "if": "if True:\n    def {name}():\n        pass\n",
    "elif": "if False:\n    pass\nelif True:\n    def {name}():\n        pass\n",
    "if_else": "if False:\n    pass\nelse:\n    def {name}():\n        pass\n",
    "try": "try:\n    def {name}():\n        pass\nexcept ImportError:\n    pass\n",
    "except": "try:\n    pass\nexcept ImportError:\n    def {name}():\n        pass\n",
    "try_else": "try:\n    pass\nexcept ImportError:\n    pass\nelse:\n    def {name}():\n        pass\n",
    "finally": "try:\n    pass\nfinally:\n    def {name}():\n        pass\n",
    "except_star": "try:\n    pass\nexcept* ImportError:\n    def {name}():\n        pass\n",
    "with": "with open(__file__):\n    def {name}():\n        pass\n",
    "async_with": "async with open(__file__):\n    def {name}():\n        pass\n",
    "for": "for _ in ():\n    def {name}():\n        pass\n",
    "for_else": "for _ in ():\n    pass\nelse:\n    def {name}():\n        pass\n",
    "async_for": "async for _ in ():\n    def {name}():\n        pass\n",
    "while": "while False:\n    def {name}():\n        pass\n",
    "while_else": "while False:\n    pass\nelse:\n    def {name}():\n        pass\n",
    "match": "match 1:\n    case _:\n        def {name}():\n            pass\n",
    "nested": "if True:\n    with open(__file__):\n        for _ in ():\n            def {name}():\n                pass\n",
}


class BlockKindTests(GuardCase):
    def removed_ids(self, before: str) -> list[str]:
        base = self.repo.commit({SPEC_A: before})
        candidate = self.repo.commit({SPEC_A: "x = 1\n"})
        result = run(self.repo, base, candidate)
        self.assertEqual(result.code, 1, result.out + result.err)
        return sorted(json.loads(line.split(" ", 2)[1]) for line in result.lines[:-1])

    def test_tests_inside_every_block_kind_are_found_at_module_and_class_level(self) -> None:
        names = {kind: "test_" + kind for kind in BLOCKS}
        module = "".join(BLOCKS[kind].format(name=names[kind]) + "\n" for kind in BLOCKS)
        klass = "class K:\n" + textwrap.indent(module, "    ")
        expected = sorted([tid(SPEC_A, name) for name in names.values()] + [tid(SPEC_A, "K", name) for name in names.values()])
        self.assertEqual(self.removed_ids(module + klass), expected)

    def test_each_block_kind_is_found_on_its_own(self) -> None:
        for kind, template in BLOCKS.items():
            for where in ("module", "class"):
                with self.subTest(kind, where=where):
                    repo = Repo()
                    self.addCleanup(repo.close)
                    source = template.format(name="test_x")
                    if where == "class":
                        source = "class K:\n" + textwrap.indent(source, "    ")
                    base = repo.commit({SPEC_A: source})
                    candidate = repo.commit({SPEC_A: "x = 1\n"})
                    result = run(repo, base, candidate)
                    expected = tid(SPEC_A, "test_x") if where == "module" else tid(SPEC_A, "K", "test_x")
                    self.assertEqual(result.lines[0].split(" ", 2)[1], json.dumps(expected), result.out + result.err)

    def test_a_function_inside_a_block_inside_a_function_is_not_a_test(self) -> None:
        source = "def test_outer():\n    if True:\n        def test_inner():\n            pass\n"
        self.assertEqual(self.removed_ids(source), [tid(SPEC_A, "test_outer")])


class SpecsPrefixTests(GuardCase):
    def scenario(self) -> tuple[str, str]:
        files = {
            "specs/test_in.py": functions("test_in"),
            "specs/sub/test_deep.py": functions("test_deep"),
            "specs2/test_out.py": functions("test_out"),
            "spec/test_short.py": functions("test_short"),
            "other/specs/test_nested.py": functions("test_nested"),
        }
        base = self.repo.commit(files)
        candidate = self.repo.commit({name: None for name in files})
        return base, candidate

    def removed_with(self, specs: str) -> list[str]:
        base, candidate = self.scenario()
        result = run(self.repo, base, candidate, specs=specs)
        self.assertEqual(result.code, 1, result.out + result.err)
        return sorted(json.loads(line.split(" ", 2)[1]) for line in result.lines[:-1])

    def test_prefix_is_a_path_component_not_a_string_prefix(self) -> None:
        expected = [tid("specs/sub/test_deep.py", "test_deep"), tid("specs/test_in.py", "test_in")]
        self.assertEqual(self.removed_with("specs"), expected)

    def test_trailing_slash_backslash_and_dot_forms_are_equivalent(self) -> None:
        expected = self.removed_with("specs")
        for form in ("specs/", "specs\\", "./specs", ".\\specs\\", "specs//"):
            with self.subTest(form):
                self.assertEqual(self.removed_with(form), expected)

    def test_a_subdirectory_selects_only_itself(self) -> None:
        self.assertEqual(self.removed_with("specs/sub"), [tid("specs/sub/test_deep.py", "test_deep")])

    def test_dot_selects_the_whole_repository(self) -> None:
        self.assertEqual(len(self.removed_with(".")), 5)

    def test_a_specs_path_naming_no_tree_at_either_commit_is_a_fault(self) -> None:
        base, candidate = self.scenario()
        for specs in ("nowhere", "specs/sub/none", "Specs", "specs/test_in.py", "specs/sub/test_deep.py"):
            with self.subTest(specs):
                result = run(self.repo, base, candidate, specs=specs)
                self.assertEqual((result.code, result.out), (2, ""), result.err)
                self.assertTrue(result.err.startswith("coverage_map: tool fault:"), result.err)
                self.assertIn(json.dumps(specs), result.err)
                self.assertIn(base, result.err)
                self.assertIn(candidate, result.err)

    def test_a_present_tree_holding_no_spec_file_passes(self) -> None:
        base = self.repo.commit({"empty/README.txt": "x\n"})
        candidate = self.repo.commit({"empty/NOTES.txt": "y\n"})
        self.assertEqual(run(self.repo, base, candidate, specs="empty").out, "removed=0 defects=0\n")

    def test_a_tree_present_at_one_commit_only_is_empty_at_the_other(self) -> None:
        base = self.repo.commit({"x.txt": "1\n"})
        candidate = self.repo.commit({SPEC_A: functions("test_one")})
        self.assertEqual(run(self.repo, base, candidate).out, "removed=0 defects=0\n")
        self.assertEqual(run(self.repo, candidate, base).out, "UNMAPPED_REMOVAL " + json.dumps(tid(SPEC_A, "test_one")) + " removed test has no map row\nremoved=1 defects=1\n")

    def test_a_specs_path_naming_a_submodule_entry_is_a_fault(self) -> None:
        seed = self.repo.commit({"x.txt": "1\n"})
        raw = {b"vendored": ("160000", seed.encode("ascii"))}
        base = self.repo.commit({SPEC_A: functions("test_one")}, raw=raw)
        candidate = self.repo.commit({"y.txt": "2\n"}, raw=raw)
        result = run(self.repo, base, candidate, specs="vendored")
        self.assertEqual((result.code, result.out), (2, ""), result.err)

    def test_specs_path_with_pathspec_magic_is_literal(self) -> None:
        base, candidate = self.scenario()
        result = run(self.repo, base, candidate, specs="spec*")
        self.assertEqual((result.code, result.out), (2, ""), result.err)
        self.assertIn(json.dumps("spec*"), result.err)


class FaultTests(GuardCase):
    def two_commits(self) -> tuple[str, str]:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))})
        return base, candidate

    def assert_fault(self, result: Result) -> None:
        self.assertEqual(result.code, 2, result.out + result.err)
        self.assertEqual(result.out, "")
        self.assertNotIn("Traceback", result.err)
        self.assertTrue(result.err.startswith("coverage_map: tool fault:"), result.err)

    def test_unknown_base_and_candidate_exit_2_with_git_stderr(self) -> None:
        base, candidate = self.two_commits()
        missing = "0" * 40
        for label, pair in {"base": (missing, candidate), "candidate": (base, missing), "name": ("no-such-ref", candidate)}.items():
            with self.subTest(label):
                result = run(self.repo, *pair)
                self.assert_fault(result)
                self.assertIn("fatal", result.err)

    def test_repo_that_is_not_a_repository_exits_2(self) -> None:
        with tempfile.TemporaryDirectory(prefix="covmap-plain-") as plain:
            result = run_args(["--repo", plain, "--base", "HEAD", "--candidate", "HEAD", "--map", MAP, "--specs", SPECS])
        self.assert_fault(result)
        self.assertIn("fatal", result.err)

    def test_a_plain_directory_inside_a_work_tree_exits_2(self) -> None:
        self.two_commits()
        plain = self.repo.dir / "plain"
        plain.mkdir()
        for label, directory in {"plain directory": plain, "directory holding tracked files": self.repo.dir / "gov"}.items():
            with self.subTest(label):
                result = run_args(["--repo", str(directory), "--base", "HEAD", "--candidate", "HEAD", "--map", MAP, "--specs", SPECS])
                self.assert_fault(result)
                self.assertIn("top level", result.err)

    def test_the_top_level_may_be_spelled_in_other_ways(self) -> None:
        base, candidate = self.two_commits()
        (self.repo.dir / "gov").mkdir(exist_ok=True)
        for label, spelling in {
            "trailing separator": str(self.repo.dir) + os.sep,
            "dot dot detour": str(self.repo.dir / "gov" / ".."),
        }.items():
            with self.subTest(label):
                result = run_args(["--repo", spelling, "--base", base, "--candidate", candidate, "--map", MAP, "--specs", SPECS])
                self.assertEqual((result.code, result.out), (0, "removed=1 defects=0\n"), result.err)

    def test_a_fault_message_with_non_ascii_input_is_escaped_to_one_line(self) -> None:
        self.two_commits()
        result = run(self.repo, "caf\u00e9", "HEAD")
        self.assert_fault(result)
        self.assertTrue(result.err.isascii(), result.err)
        self.assertEqual(result.err.count("\n"), 1, result.err)
        self.assertIn("caf\\xe9", result.err)

    def test_a_parse_fault_does_not_repeat_the_raw_path(self) -> None:
        good = self.repo.commit({"specs/test_a\u00e9.py": functions("test_one")})
        broken = self.repo.commit({"specs/test_a\u00e9.py": "def (:\n"})
        result = run(self.repo, good, broken)
        self.assert_fault(result)
        self.assertTrue(result.err.isascii(), result.err)
        self.assertEqual(result.err.count("\n"), 1, result.err)

    def test_repo_path_that_does_not_exist_exits_2(self) -> None:
        missing = str(self.repo.dir / "missing")
        self.assert_fault(run_args(["--repo", missing, "--base", "HEAD", "--candidate", "HEAD", "--map", MAP, "--specs", SPECS]))

    def test_git_that_cannot_start_exits_2(self) -> None:
        base, candidate = self.two_commits()
        with mock.patch.object(cm.subprocess, "run", side_effect=FileNotFoundError("git")):
            self.assert_fault(run(self.repo, base, candidate))

    def test_spec_that_does_not_parse_exits_2_naming_commit_and_path(self) -> None:
        good = self.repo.commit({SPEC_A: functions("test_one")})
        broken = self.repo.commit({SPEC_A: "def test_a(:\n"})
        for label, pair in {"candidate side": (good, broken), "base side": (broken, good)}.items():
            with self.subTest(label):
                result = run(self.repo, *pair)
                self.assert_fault(result)
                self.assertIn(pair[1] if label == "candidate side" else pair[0], result.err)
                self.assertIn(json.dumps(SPEC_A), result.err)

    def test_spec_that_is_not_python_source_exits_2(self) -> None:
        good = self.repo.commit({SPEC_A: functions("test_one")})
        with open(self.repo.dir / SPEC_A, "wb") as handle:
            handle.write(b"\xff\xfe\x00 def test_a\n")
        git(self.repo.dir, "add", "-A")
        git(self.repo.dir, "commit", "-q", "-m", "bin")
        bad = git(self.repo.dir, "rev-parse", "HEAD").strip()
        self.assert_fault(run(self.repo, good, bad))

    def test_a_fault_wins_over_a_red(self) -> None:
        good = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        broken = self.repo.commit({"specs/test_b.py": "def (:\n", MAP: "{nope"})
        self.assert_fault(run(self.repo, good, broken))

    def test_unreadable_blob_exits_2(self) -> None:
        base, candidate = self.two_commits()
        blob = git(self.repo.dir, "rev-parse", f"{base}:{SPEC_A}").strip()
        loose = self.repo.dir / ".git" / "objects" / blob[:2] / blob[2:]
        os.chmod(loose, stat.S_IWRITE)
        loose.unlink()
        self.assert_fault(run(self.repo, base, candidate))

    def test_unreadable_map_blob_exits_2(self) -> None:
        base, candidate = self.two_commits()
        blob = git(self.repo.dir, "rev-parse", f"{candidate}:{MAP}").strip()
        loose = self.repo.dir / ".git" / "objects" / blob[:2] / blob[2:]
        os.chmod(loose, stat.S_IWRITE)
        loose.unlink()
        self.assert_fault(run(self.repo, base, candidate))

    def test_git_failing_for_each_query_exits_2_with_its_message(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), MAP: map_text()})
        real = cm.run_git
        calls: list[Sequence[str]] = []

        def counting(repo: str, args: Sequence[str]) -> bytes:
            calls.append(args)
            return real(repo, args)

        with mock.patch.object(cm, "run_git", counting):
            self.assert_red(run(self.repo, base, candidate), "UNMAPPED_REMOVAL")
        queries = len(calls)
        self.assertGreaterEqual(queries, 6)
        self.assertEqual({call[0] for call in calls}, {"rev-parse", "ls-tree", "cat-file"})
        for failing in range(queries):
            with self.subTest(query=calls[failing][0], index=failing):
                seen = 0

                def failing_at(repo: str, args: Sequence[str]) -> bytes:
                    nonlocal seen
                    seen += 1
                    if seen == failing + 1:
                        raise cm.ToolFault("injected git failure")
                    return real(repo, args)

                with mock.patch.object(cm, "run_git", failing_at):
                    result = run(self.repo, base, candidate)
                self.assert_fault(result)
                self.assertIn("injected git failure", result.err)

    def test_an_unexpected_error_is_a_fault_not_a_red(self) -> None:
        base, candidate = self.two_commits()
        with mock.patch.object(cm, "judge", side_effect=RuntimeError("boom")):
            result = run(self.repo, base, candidate)
        self.assert_fault(result)
        self.assertIn("boom", result.err)


class EntryKindTests(GuardCase):
    """Links, submodules and paths git serves as bytes."""

    def seed(self) -> str:
        return self.repo.commit({"x.txt": "1\n"})

    def test_a_submodule_entry_under_specs_is_not_a_spec_file(self) -> None:
        raw = {b"specs/test_sub.py": ("160000", self.seed().encode("ascii"))}
        base = self.repo.commit({SPEC_A: functions("test_one")}, raw=raw)
        same = self.repo.commit({"y.txt": "2\n"}, raw=raw)
        gone = self.repo.commit({"z.txt": "3\n"})
        self.assertEqual(run(self.repo, base, same).out, "removed=0 defects=0\n")
        self.assertEqual(run(self.repo, base, gone).out, "removed=0 defects=0\n")

    def test_a_symlinked_spec_that_did_not_change_is_never_parsed(self) -> None:
        raw = {SPEC_A.encode(): ("120000", b"def (:\n")}
        base = self.repo.commit({"x.txt": "1\n"}, raw=raw)
        candidate = self.repo.commit({"y.txt": "2\n"}, raw=raw)
        self.assertEqual(run(self.repo, base, candidate).out, "removed=0 defects=0\n")

    def test_a_spec_replaced_by_a_link_has_all_its_tests_removed(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: None}, raw={SPEC_A.encode(): ("120000", b"def (:\n")})
        result = run(self.repo, base, candidate)
        self.assert_red(result, "UNMAPPED_REMOVAL", "UNMAPPED_REMOVAL")
        self.assertEqual(self.summary(result), "removed=2 defects=2")

    def test_an_executable_spec_is_a_spec_file(self) -> None:
        base = self.repo.commit({"x.txt": "1\n"}, raw={SPEC_A.encode(): ("100755", functions("test_one").encode())})
        candidate = self.repo.commit({"y.txt": "2\n"})
        self.assert_red(run(self.repo, base, candidate), "UNMAPPED_REMOVAL")

    def test_a_spec_path_that_is_not_utf8_is_a_test_id_not_a_fault(self) -> None:
        path = b"specs/test_\xff.py"
        test_id = "specs/test_\udcff.py::test_one"
        raw = {path: ("100644", functions("test_one").encode())}
        base = self.repo.commit({"x.txt": "1\n"}, raw=raw)
        same = self.repo.commit({"y.txt": "2\n"}, raw=raw)
        self.assertEqual(run(self.repo, base, same).out, "removed=0 defects=0\n")
        gone = self.repo.commit({"z.txt": "3\n"})
        result = run(self.repo, base, gone)
        self.assert_red(result, "UNMAPPED_REMOVAL")
        self.assertEqual(result.lines[0], "UNMAPPED_REMOVAL " + json.dumps(test_id) + " removed test has no map row")
        self.assertTrue(result.out.isascii())
        # a map cannot name it: its text breaks the text-value rule
        mapped = self.repo.commit({MAP: map_text(row(test_id, "dropped", reason="r"))})
        self.assert_red(run(self.repo, base, mapped), "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")

    def test_a_newline_in_a_spec_path_stays_on_one_line(self) -> None:
        path = b"specs/test_a\nb.py"
        quoted = json.dumps("specs/test_a\nb.py")
        broken = self.repo.commit({"x.txt": "1\n"}, raw={path: ("100644", b"def (:\n")})
        fixed = self.repo.commit({"y.txt": "2\n"}, raw={path: ("100644", functions("test_one").encode())})
        gone = self.repo.commit({"z.txt": "3\n"})
        fault = run(self.repo, fixed, broken)
        self.assertEqual((fault.code, fault.out), (2, ""))
        self.assertEqual(fault.err.count("\n"), 1, fault.err)
        self.assertIn(quoted, fault.err)
        red = run(self.repo, fixed, gone)
        self.assertEqual(red.code, 1)
        self.assertEqual(len(red.lines), 2, red.out)
        self.assertIn(json.dumps("specs/test_a\nb.py::test_one"), red.lines[0])


class UsageTests(GuardCase):
    def good(self, **override: str) -> list[str]:
        values = {"--repo": str(self.repo.dir), "--base": "HEAD", "--candidate": "HEAD", "--map": MAP, "--specs": SPECS}
        values.update({"--" + key: value for key, value in override.items()})
        return [part for pair in values.items() for part in pair]

    def setUp(self) -> None:
        super().setUp()
        self.repo.commit({SPEC_A: functions("test_one")})

    def assert_usage(self, argv: Sequence[str]) -> None:
        result = run_args(argv)
        self.assertEqual(result.code, 3, result.out + result.err)
        self.assertEqual(result.out, "")
        self.assertIn("usage: coverage_map.py", result.err)
        self.assertNotIn("Traceback", result.err)

    def test_the_good_baseline_passes(self) -> None:
        self.assertEqual(run_args(self.good()).code, 0)

    def test_missing_arguments_exit_3(self) -> None:
        self.assert_usage([])
        full = self.good()
        for index in range(0, len(full), 2):
            with self.subTest(full[index]):
                self.assert_usage(full[:index] + full[index + 2:])

    def test_unknown_option_extra_positional_and_help_exit_3(self) -> None:
        self.assert_usage([*self.good(), "--extra", "1"])
        self.assert_usage([*self.good(), "stray"])
        self.assert_usage(["--help"])
        self.assert_usage(["--repo"])
        self.assert_usage([*self.good(), "--bas", "x"])

    def test_empty_and_blank_values_exit_3(self) -> None:
        for option in ("repo", "base", "candidate", "map", "specs"):
            for value in ("", "  "):
                with self.subTest(option=option, value=value):
                    self.assert_usage(self.good(**{option: value}))

    def test_absolute_paths_are_refused(self) -> None:
        for value in ("/abs", "\\abs", "C:\\abs", "C:/abs", "c:rel", "//server/share", str(Path(self.repo.dir).resolve())):
            for option in ("map", "specs"):
                with self.subTest(option=option, value=value):
                    self.assert_usage(self.good(**{option: value}))

    def test_parent_segments_are_refused(self) -> None:
        for value in ("..", "../x", "a/../b", "a\\..\\b", "a/.."):
            for option in ("map", "specs"):
                with self.subTest(option=option, value=value):
                    self.assert_usage(self.good(**{option: value}))

    def test_map_must_name_a_file(self) -> None:
        for value in (".", "./", "/", ".\\"):
            with self.subTest(value):
                self.assert_usage(self.good(map=value))

    def test_revisions_starting_with_a_dash_are_refused(self) -> None:
        self.assert_usage(self.good(base="--output=x"))
        self.assert_usage(self.good(candidate="-1"))

    def test_a_lone_surrogate_or_control_character_in_any_argument_exits_3(self) -> None:
        for option in ("repo", "base", "candidate", "map", "specs"):
            for value in ("a\ud800b", "a\x01b", "a\nb", "a\x7fb", "a\tb", "a\x00b"):
                with self.subTest(option=option, value=value):
                    result = run_args(self.good(**{option: value}))
                    self.assertEqual((result.code, result.out), (3, ""), result.err)
                    self.assertEqual(result.err.splitlines(), [f"coverage_map: --{option} holds " + ("a lone surrogate" if value == "a\ud800b" else "a control character"), cm.USAGE])

    def test_an_unknown_argument_is_echoed_on_one_escaped_line(self) -> None:
        result = run_args([*self.good(), "stray\nline\u00e9"])
        self.assertEqual((result.code, result.out), (3, ""))
        lines = result.err.splitlines()
        self.assertEqual(len(lines), 2, result.err)
        self.assertIn("stray\\x0aline\\xe9", lines[0])
        self.assertTrue(result.err.isascii())

    def test_map_backslash_form_is_read_as_the_same_path(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))})
        self.assertEqual(run(self.repo, base, candidate, map_path="gov\\coverage-map.json").code, 0)
        self.assertEqual(run(self.repo, base, candidate, map_path="./gov//coverage-map.json").code, 0)


class CommandLineTests(GuardCase):
    def invoke(self, argv: Sequence[str], encoding: str | None = None) -> subprocess.CompletedProcess[bytes]:
        env = dict(os.environ)
        if encoding is not None:
            env["PYTHONIOENCODING"] = encoding
            env.pop("PYTHONUTF8", None)
        return subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, env=env)

    def test_exit_codes_through_a_real_process(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        red = self.repo.commit({SPEC_A: functions("test_one")})
        green = self.repo.commit({MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))})
        common = ["--repo", str(self.repo.dir), "--map", MAP, "--specs", SPECS]
        self.assertEqual(self.invoke([*common, "--base", base, "--candidate", green]).returncode, 0)
        done = self.invoke([*common, "--base", base, "--candidate", red])
        self.assertEqual((done.returncode, done.stderr), (1, b""))
        self.assertEqual(self.invoke([*common, "--base", "0" * 40, "--candidate", red]).returncode, 2)
        self.assertEqual(self.invoke(["--repo"]).returncode, 3)

    def test_a_red_under_a_cp950_console_still_exits_1(self) -> None:
        name = "test_" + NON_CP950
        base = self.repo.commit({SPEC_A: functions(name)})
        candidate = self.repo.commit({SPEC_A: "x = 1\n"})
        done = self.invoke(["--repo", str(self.repo.dir), "--base", base, "--candidate", candidate, "--map", MAP, "--specs", SPECS], encoding="cp950")
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertIn(b"UNMAPPED_REMOVAL", done.stdout)
        self.assertIn(b"removed=1 defects=1", done.stdout)


if __name__ == "__main__":
    unittest.main()
