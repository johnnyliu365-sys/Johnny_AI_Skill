"""Behavioural tests for the coverage_map gate script (exit codes 0/1/2/3).

Every fixture is a throwaway git repository built in a temporary directory; every expected
id, count and message part is derived from the sources the fixture wrote.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import stat
import struct
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

    def commit_tree(self, entries: Mapping[str, bytes | None], parent: str | None = None) -> str:
        """A commit whose tree holds exactly `entries`: path -> blob bytes, or None for an empty tree object.

        The commit is made without the index, so a tree with nothing in it can be an entry.
        """

        def build(items: Mapping[tuple[str, ...], bytes | None]) -> str:
            records = b""
            for name in sorted({key[0] for key in items}):
                below = {key[1:]: value for key, value in items.items() if key[0] == name}
                if () not in below:
                    records += f"040000 tree {build(below)}\t{name}\n".encode("utf-8")
                elif below[()] is None:
                    records += f"040000 tree {build({})}\t{name}\n".encode("utf-8")
                else:
                    blob = git_bytes(self.dir, "hash-object", "-w", "--stdin", data=below[()]).decode("ascii").strip()
                    records += f"100644 blob {blob}\t{name}\n".encode("utf-8")
            return git_bytes(self.dir, "mktree", data=records).decode("ascii").strip()

        tree = build({tuple(path.split("/")): body for path, body in entries.items()})
        parents = ["-p", parent] if parent is not None else []
        return git(self.dir, "commit-tree", tree, *parents, "-m", "c").strip()


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
            for label, value in {"newline": "a\nb", "nul": "a\x00b", "delete": "a\x7fb", "tab": "\t", "unit separator": "a\x1fb", "surrogate": "a\ud800b"}.items():
                with self.subTest(key=key, value=label):
                    repo = Repo()
                    self.addCleanup(repo.close)
                    base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                    shaped = {**row(good, "dropped", reason="r"), key: value}
                    candidate = repo.commit({SPEC_A: functions("test_one"), MAP: json.dumps({"rows": [shaped]})})
                    result = run(repo, base, candidate)
                    self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                    self.assertEqual(result.lines[0], "MAP_ROW_INVALID \"rows[0]\" field " + key + " holds " + ("a lone surrogate" if label == "surrogate" else "a control character"))

    def test_the_text_rule_stops_at_the_control_characters(self) -> None:
        """U+0020 and U+0080 are text; U+001F and U+007F are not."""
        good = tid(SPEC_A, "test_two")
        for label, value in {"space": "a b", "one past delete": "a\u0080b", "last printable": "a~b"}.items():
            with self.subTest(label):
                repo = Repo()
                self.addCleanup(repo.close)
                base = repo.commit({SPEC_A: functions("test_one", "test_two")})
                shaped = row(good, "dropped", reason=value)
                candidate = repo.commit({SPEC_A: functions("test_one"), MAP: json.dumps({"rows": [shaped]})})
                self.assertEqual(run(repo, base, candidate).out, "removed=1 defects=0\n")

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

    def test_an_empty_tree_object_at_the_map_path_is_invalid_for_the_file(self) -> None:
        base = self.repo.commit_tree({SPEC_A: functions("test_one", "test_two").encode()})
        candidate = self.repo.commit_tree({SPEC_A: functions("test_one").encode(), MAP: None}, parent=base)
        result = run(self.repo, base, candidate)
        self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
        self.assertEqual(result.lines[0], "MAP_ROW_INVALID " + json.dumps(MAP) + " map path is not a file")
        self.assertEqual(self.summary(result), "removed=1 defects=2")

    def test_an_empty_tree_object_at_the_map_path_is_invalid_even_when_nothing_was_removed(self) -> None:
        base = self.repo.commit_tree({SPEC_A: functions("test_one").encode()})
        candidate = self.repo.commit_tree({SPEC_A: functions("test_one").encode(), MAP: None}, parent=base)
        result = run(self.repo, base, candidate)
        self.assert_red(result, "MAP_ROW_INVALID")
        self.assertEqual(self.summary(result), "removed=0 defects=1")

    def test_a_map_path_that_is_a_tree_is_invalid_even_when_nothing_was_removed(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP + "/note.txt": "x\n"})
        self.assert_red(run(self.repo, base, candidate), "MAP_ROW_INVALID")

    def repeated_row(self, extra: str) -> str:
        return (
            '{"rows": [{"assertion": ' + json.dumps(tid(SPEC_A, "test_two"))
            + ', "disposition": "dropped", "carried_to": "", "reason": "r", "ticket": ""' + extra + "}]}"
        )

    def test_a_repeated_key_in_a_row_makes_the_row_invalid_and_cover_nothing(self) -> None:
        cases = {
            "same value twice": (', "disposition": "dropped"', "disposition"),
            "last value differs": (', "reason": ""', "reason"),
            "extra key": (', "note": 1, "note": 2', "note"),
            "nested object": (', "note": {"a": 1, "a": 2}', "a"),
            "nested in a list": (', "note": [{"b": 1, "b": 1}]', "b"),
            "escaped spelling": (', "reas\\u006fn": "x"', "reason"),
        }
        for label, (extra, key) in cases.items():
            with self.subTest(label):
                result = self.removal(self.repeated_row(extra))
                self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                self.assertEqual(result.lines[0], 'MAP_ROW_INVALID "rows[0]" row repeats key ' + json.dumps(key))
                self.assertEqual(self.summary(result), "removed=1 defects=2")

    def test_a_row_of_a_kept_test_with_a_repeated_key_is_still_invalid(self) -> None:
        kept = '{"assertion": ' + json.dumps(tid(SPEC_A, "test_one")) + ', "disposition": "dropped", "carried_to": "", "reason": "r", "ticket": "", "ticket": ""}'
        done = json.dumps(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))
        result = self.removal('{"rows": [' + kept + ", " + done + "]}")
        self.assert_red(result, "MAP_ROW_INVALID")
        self.assertEqual(result.lines[0], 'MAP_ROW_INVALID "rows[0]" row repeats key "ticket"')

    def test_a_repeated_key_at_the_top_level_makes_the_file_invalid(self) -> None:
        rows = json.dumps([row(tid(SPEC_A, "test_two"), "dropped", reason="r")])
        cases = {
            "rows twice": ('{"rows": ' + rows + ', "rows": ' + rows + "}", "rows"),
            "rows twice, empty last": ('{"rows": ' + rows + ', "rows": []}', "rows"),
            "extra key": ('{"note": 1, "rows": ' + rows + ', "note": 2}', "note"),
            "nested object beside rows": ('{"rows": ' + rows + ', "note": {"a": 1, "a": 2}}', "a"),
        }
        for label, (body, key) in cases.items():
            with self.subTest(label):
                result = self.removal(body)
                self.assert_red(result, "MAP_ROW_INVALID", "UNMAPPED_REMOVAL")
                self.assertEqual(result.lines[0], "MAP_ROW_INVALID " + json.dumps(MAP) + " map file repeats key " + json.dumps(key))

    def test_a_repeated_key_with_nothing_removed_is_still_red(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP: '{"rows": [], "rows": []}'})
        self.assert_red(run(self.repo, base, candidate), "MAP_ROW_INVALID")

    def test_objects_without_a_repeated_key_are_untouched(self) -> None:
        extra = {**row(tid(SPEC_A, "test_two"), "dropped", reason="r"), "note": {"a": 1, "b": [{"c": 1}, {"c": 2}]}}
        self.assertEqual(self.removal(map_text(extra)).out, "removed=1 defects=0\n")

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
    "except_second": "try:\n    pass\nexcept ImportError:\n    pass\nexcept ValueError:\n    def {name}():\n        pass\n",
    "except_third": "try:\n    pass\nexcept ImportError:\n    pass\nexcept ValueError:\n    pass\nexcept OSError:\n    def {name}():\n        pass\n",
    "except_star": "try:\n    pass\nexcept* ImportError:\n    def {name}():\n        pass\n",
    "except_star_second": "try:\n    pass\nexcept* ImportError:\n    pass\nexcept* ValueError:\n    def {name}():\n        pass\n",
    "with": "with open(__file__):\n    def {name}():\n        pass\n",
    "async_with": "async with open(__file__):\n    def {name}():\n        pass\n",
    "for": "for _ in ():\n    def {name}():\n        pass\n",
    "for_else": "for _ in ():\n    pass\nelse:\n    def {name}():\n        pass\n",
    "async_for": "async for _ in ():\n    def {name}():\n        pass\n",
    "while": "while False:\n    def {name}():\n        pass\n",
    "while_else": "while False:\n    pass\nelse:\n    def {name}():\n        pass\n",
    "match": "match 1:\n    case _:\n        def {name}():\n            pass\n",
    "match_second": "match 1:\n    case 2:\n        pass\n    case _:\n        def {name}():\n            pass\n",
    "match_third": "match 1:\n    case 2:\n        pass\n    case 3:\n        pass\n    case _:\n        def {name}():\n            pass\n",
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


class HelperNestingTests(GuardCase):
    def removed_ids(self, before: str) -> list[str]:
        base = self.repo.commit({SPEC_A: before})
        candidate = self.repo.commit({SPEC_A: "x = 1\n"})
        result = run(self.repo, base, candidate)
        self.assertEqual(result.code, 1, result.out + result.err)
        return sorted(json.loads(line.split(" ", 2)[1]) for line in result.lines[:-1])

    def test_a_test_function_nested_in_a_helper_is_not_a_test(self) -> None:
        source = (
            "def helper():\n    def test_in_helper():\n        pass\n\n"
            "async def build():\n    async def test_in_async_helper():\n        pass\n\n"
            "def test_real():\n    pass\n"
        )
        self.assertEqual(self.removed_ids(source), [tid(SPEC_A, "test_real")])

    def test_a_test_in_a_block_or_class_inside_a_helper_is_not_a_test(self) -> None:
        source = (
            "def helper():\n"
            "    if True:\n        def test_in_block():\n            pass\n"
            "    class Inner:\n        def test_in_class(self):\n            pass\n"
            "class K:\n"
            "    def helper(self):\n        def test_in_method_helper():\n            pass\n"
            "    def test_real(self):\n        pass\n"
        )
        self.assertEqual(self.removed_ids(source), [tid(SPEC_A, "K", "test_real")])


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

    def test_an_empty_tree_object_at_specs_is_a_present_empty_tree(self) -> None:
        both = self.repo.commit_tree({SPECS: None})
        self.assertEqual(run(self.repo, both, both), Result(0, "removed=0 defects=0\n", ""))
        other = self.repo.commit_tree({"x.txt": b"1\n"})
        self.assertEqual(run(self.repo, both, other), Result(0, "removed=0 defects=0\n", ""))
        self.assertEqual(run(self.repo, other, both), Result(0, "removed=0 defects=0\n", ""))

    def test_an_empty_tree_object_at_one_commit_is_empty_at_that_commit(self) -> None:
        full = self.repo.commit_tree({SPEC_A: functions("test_one").encode()})
        empty = self.repo.commit_tree({SPECS: None})
        result = run(self.repo, full, empty)
        self.assert_red(result, "UNMAPPED_REMOVAL")
        self.assertEqual(self.summary(result), "removed=1 defects=1")
        self.assertEqual(run(self.repo, empty, full).out, "removed=0 defects=0\n")

    def test_an_empty_tree_object_below_specs_selects_that_subdirectory(self) -> None:
        both = self.repo.commit_tree({"specs/sub": None, SPEC_A: functions("test_one").encode()})
        self.assertEqual(run(self.repo, both, both, specs="specs/sub").out, "removed=0 defects=0\n")

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

    def assert_red_with_faults(self, result: Result, faults: int, *codes: str) -> None:
        self.assertEqual(result.code, 1, result.out + result.err)
        self.assertEqual(sorted(result.defect_codes()), sorted(codes), result.out)
        lines = result.err.splitlines()
        self.assertEqual(len(lines), faults, result.err)
        for line in lines:
            self.assertTrue(line.startswith("coverage_map: tool fault:"), result.err)
        self.assertNotIn("Traceback", result.err)

    def test_a_red_is_reported_before_a_fault(self) -> None:
        good = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        broken = self.repo.commit({"specs/test_b.py": "def (:\n", MAP: "{nope"})
        result = run(self.repo, good, broken)
        self.assert_red_with_faults(result, 1, "MAP_ROW_INVALID")
        self.assertIn(json.dumps("specs/test_b.py"), result.err)
        self.assertEqual(self.summary(result), "removed=0 defects=1")

    def test_a_removal_is_reported_when_another_spec_does_not_parse(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two"), "specs/test_b.py": functions("test_b1", "test_b2")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), "specs/test_b.py": "def (:\n"})
        result = run(self.repo, base, candidate)
        self.assert_red_with_faults(result, 1, "UNMAPPED_REMOVAL")
        self.assertIn(json.dumps(tid(SPEC_A, "test_two")), result.lines[0])
        self.assertEqual(self.summary(result), "removed=1 defects=1")

    def test_every_fault_is_printed_one_line_each(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two"), "specs/test_b.py": "def (:\n", "specs/test_c.py": "def (:\n"})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), "specs/test_b.py": None, "specs/test_c.py": None})
        result = run(self.repo, base, candidate)
        self.assert_red_with_faults(result, 2, "UNMAPPED_REMOVAL")
        self.assertIn(json.dumps("specs/test_b.py"), result.err)
        self.assertIn(json.dumps("specs/test_c.py"), result.err)

    def test_a_red_is_reported_when_the_base_cannot_be_served(self) -> None:
        self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP: "{nope"})
        result = run(self.repo, "0" * 40, candidate)
        self.assert_red_with_faults(result, 1, "MAP_ROW_INVALID")
        self.assertIn("fatal", result.err)

    def test_a_red_is_reported_when_specs_names_no_tree(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP: "{nope"})
        result = run(self.repo, base, candidate, specs="nowhere")
        self.assert_red_with_faults(result, 1, "MAP_ROW_INVALID")
        self.assertIn(json.dumps("nowhere"), result.err)

    def test_a_red_is_reported_when_a_spec_blob_cannot_be_read(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two"), "specs/test_b.py": functions("test_b")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), "specs/test_b.py": functions("test_b")})
        blob = git(self.repo.dir, "rev-parse", f"{base}:specs/test_b.py").strip()
        loose = self.repo.dir / ".git" / "objects" / blob[:2] / blob[2:]
        os.chmod(loose, stat.S_IWRITE)
        loose.unlink()
        result = run(self.repo, base, candidate)
        self.assert_red_with_faults(result, 2, "UNMAPPED_REMOVAL")

    def test_a_fault_with_no_red_is_exit_2_with_nothing_on_stdout(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: "def (:\n", MAP: map_text()})
        self.assert_fault(run(self.repo, base, candidate))

    def test_a_carried_target_in_an_unreadable_candidate_spec_is_not_judged(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        carried = map_text(row(tid(SPEC_A, "test_two"), "carried", tid("specs/test_b.py", "test_two")))
        candidate = self.repo.commit({SPEC_A: functions("test_one"), "specs/test_b.py": "def (:\n", MAP: carried})
        self.assert_fault(run(self.repo, base, candidate))
        sibling = map_text(row(tid(SPEC_A, "test_two"), "carried", tid("specs/test_c.py", "test_two")))
        again = self.repo.commit({MAP: sibling})
        result = run(self.repo, base, again)
        self.assert_red_with_faults(result, 1, "CARRIED_TARGET_MISSING")

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

    def test_a_carried_target_is_in_an_unreadable_spec_only_by_its_exact_path_and_separator(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        unreadable = "specs/test_b.py"
        for target, judged in {
            tid(unreadable, "test_two"): False,
            tid(unreadable, "Inner", "test_two"): False,
            unreadable: True,
            unreadable + ".bak::test_two": True,
            unreadable + "x::test_two": True,
            unreadable + ":test_two": True,
            unreadable[:-1] + "::test_two": True,
        }.items():
            with self.subTest(target=target):
                carried = map_text(row(tid(SPEC_A, "test_two"), "carried", target))
                candidate = self.repo.commit({SPEC_A: functions("test_one"), unreadable: "def (:\n", MAP: carried})
                result = run(self.repo, base, candidate)
                if judged:
                    self.assert_red_with_faults(result, 1, "CARRIED_TARGET_MISSING")
                else:
                    self.assert_fault(result)

    def test_a_red_is_reported_when_opening_a_side_fails_with_an_error_that_is_not_a_tool_fault(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one")})
        candidate = self.repo.commit({MAP: "{nope"})
        base_id = git(self.repo.dir, "rev-parse", base).strip()
        real = cm.read_tree

        def failing(repo: str, commit: str) -> dict[bytes, cm.TreeEntry]:
            if commit == base_id:
                raise RuntimeError("listing blew up")
            return real(repo, commit)

        with mock.patch.object(cm, "read_tree", failing):
            result = run(self.repo, base, candidate)
        self.assert_red_with_faults(result, 1, "MAP_ROW_INVALID")
        self.assertIn("unexpected RuntimeError: listing blew up", result.err)

    def test_a_red_is_reported_when_listing_the_tests_of_a_spec_fails_with_an_error_that_is_not_a_tool_fault(self) -> None:
        other = "specs/test_b.py"
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two"), other: functions("test_b1")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), other: functions("test_b1", "test_b2")})
        real = cm.parse_tests

        def failing(source: bytes, commit: str, path: str) -> cm.ParsedTests:
            if path == other:
                raise RuntimeError("parsing blew up")
            return real(source, commit, path)

        with mock.patch.object(cm, "parse_tests", failing):
            result = run(self.repo, base, candidate)
        self.assert_red_with_faults(result, 2, "UNMAPPED_REMOVAL")
        self.assertEqual(result.err.count("unexpected RuntimeError: parsing blew up"), 2, result.err)
        self.assertEqual(self.summary(result), "removed=1 defects=1")

    def test_every_fault_met_is_kept_when_reading_the_map_fails_with_an_error_that_is_not_a_tool_fault(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), "specs/test_b.py": "def (:\n", MAP: map_text()})
        map_blob = git(self.repo.dir, "rev-parse", f"{candidate}:{MAP}").strip()
        real = cm.read_blob

        def failing(repo: str, object_id: str) -> bytes:
            if object_id == map_blob:
                raise RuntimeError("map read blew up")
            return real(repo, object_id)

        with mock.patch.object(cm, "read_blob", failing):
            result = run(self.repo, base, candidate)
        self.assert_fault(result)
        lines = result.err.splitlines()
        self.assertEqual(len(lines), 2, result.err)
        self.assertIn(json.dumps("specs/test_b.py"), lines[0])
        self.assertIn("unexpected RuntimeError: map read blew up", lines[1])

    def test_a_spec_whose_base_blob_cannot_be_read_never_invents_a_missing_carried_target(self) -> None:
        other = "specs/test_b.py"
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two", "test_three"), other: functions("test_b1")})
        carried = map_text(row(tid(SPEC_A, "test_two"), "carried", tid(other, "test_b2")))
        candidate = self.repo.commit({SPEC_A: functions("test_one"), other: functions("test_b1", "test_b2"), MAP: carried})
        blob = git(self.repo.dir, "rev-parse", f"{base}:{other}").strip()
        loose = self.repo.dir / ".git" / "objects" / blob[:2] / blob[2:]
        os.chmod(loose, stat.S_IWRITE)
        loose.unlink()
        result = run(self.repo, base, candidate)
        self.assert_red_with_faults(result, 1, "UNMAPPED_REMOVAL")
        self.assertIn(json.dumps(tid(SPEC_A, "test_three")), result.lines[0])
        self.assertIn("cat-file", result.err)
        self.assertNotIn("unexpected", result.err)
        self.assertEqual(self.summary(result), "removed=2 defects=1")


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


HOSTILE_NAMES = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES",
)


class GitEnvironmentTests(GuardCase):
    def two_commits(self) -> tuple[str, str]:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one"), MAP: map_text(row(tid(SPEC_A, "test_two"), "dropped", reason="r"))})
        return base, candidate

    def decoy(self) -> Repo:
        other = Repo()
        self.addCleanup(other.close)
        other.commit({"decoy.txt": "1\n"})
        return other

    def test_a_git_dir_in_the_environment_does_not_change_the_result(self) -> None:
        base, candidate = self.two_commits()
        baseline = run(self.repo, base, candidate)
        self.assertEqual((baseline.code, baseline.out, baseline.err), (0, "removed=1 defects=0\n", ""))
        decoy = self.decoy()
        with mock.patch.dict(os.environ, {"GIT_DIR": str(decoy.dir / ".git")}):
            self.assertEqual(run(self.repo, base, candidate), baseline)

    def test_every_repository_selecting_variable_is_ignored(self) -> None:
        base, candidate = self.two_commits()
        baseline = run(self.repo, base, candidate)
        decoy = self.decoy()
        values = {
            "GIT_DIR": str(decoy.dir / ".git"),
            "GIT_WORK_TREE": str(decoy.dir),
            "GIT_INDEX_FILE": str(self.repo.dir / "no-such-index"),
            "GIT_OBJECT_DIRECTORY": str(decoy.dir / "no-such-objects"),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(decoy.dir / ".git" / "objects"),
            "GIT_NAMESPACE": "hostile",
            "GIT_CEILING_DIRECTORIES": str(self.repo.dir.parent),
            "GIT_COMMON_DIR": str(decoy.dir / ".git"),
        }
        self.assertEqual(set(HOSTILE_NAMES) - set(values), set())
        for name, value in values.items():
            with self.subTest(name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(run(self.repo, base, candidate), baseline)
        with mock.patch.dict(os.environ, values):
            self.assertEqual(run(self.repo, base, candidate), baseline)

    def test_a_git_dir_does_not_make_a_plain_directory_a_work_tree(self) -> None:
        self.two_commits()
        for extra in ({}, {"GIT_WORK_TREE": str(self.repo.dir)}):
            with self.subTest(sorted(extra)), tempfile.TemporaryDirectory(prefix="covmap-plain-") as plain:
                with mock.patch.dict(os.environ, {"GIT_DIR": str(self.repo.dir / ".git"), **extra}):
                    result = run_args(["--repo", plain, "--base", "HEAD", "--candidate", "HEAD", "--map", MAP, "--specs", SPECS])
                self.assertEqual((result.code, result.out), (2, ""), result.err)
                self.assertTrue(result.err.startswith("coverage_map: tool fault:"), result.err)

    def test_no_git_child_inherits_a_repository_selecting_variable(self) -> None:
        base, candidate = self.two_commits()
        real = subprocess.run
        environments: list[object] = []

        def spy(*args: object, **kwargs: object) -> object:
            environments.append(kwargs.get("env"))
            return real(*args, **kwargs)

        polluted = {name: "x" for name in (*HOSTILE_NAMES, "GIT_COMMON_DIR", "GIT_PREFIX")}
        with mock.patch.dict(os.environ, polluted), mock.patch.object(cm.subprocess, "run", spy):
            result = run(self.repo, base, candidate)
        self.assertEqual((result.code, result.out, result.err), (0, "removed=1 defects=0\n", ""))
        self.assertGreaterEqual(len(environments), 6)
        for environment in environments:
            self.assertIsInstance(environment, dict)
            names = {name.upper() for name in (environment if isinstance(environment, dict) else {})}
            self.assertEqual(names & set(polluted), set())

    def test_the_environment_given_to_git_keeps_everything_else(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_DIR": "x", "GIT_AUTHOR_NAME": "kept", "SOME_OTHER": "kept too"}):
            environment = cm.git_environment()
        self.assertNotIn("GIT_DIR", environment)
        self.assertEqual((environment["GIT_AUTHOR_NAME"], environment["SOME_OTHER"]), ("kept", "kept too"))

    def test_the_selecting_names_cover_the_ticket_list(self) -> None:
        self.assertGreaterEqual(set(cm.GIT_SELECTING_VARIABLES), set(HOSTILE_NAMES))

    def replace_blob(self, commit: str, path: str, body: str) -> str:
        """Make git serve `body` in place of the blob `path` holds at `commit`; returns what plain git now reads there."""
        old = git(self.repo.dir, "rev-parse", f"{commit}:{path}").strip()
        new = git_bytes(self.repo.dir, "hash-object", "-w", "--stdin", data=body.encode("utf-8")).decode("ascii").strip()
        git(self.repo.dir, "replace", "-f", old, new)
        return git(self.repo.dir, "show", f"{commit}:{path}")

    def test_a_replace_ref_on_a_spec_blob_does_not_change_what_the_guard_reads(self) -> None:
        base = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        candidate = self.repo.commit({SPEC_A: functions("test_one")})
        baseline = run(self.repo, base, candidate)
        self.assertEqual((baseline.code, baseline.defect_codes()), (1, ["UNMAPPED_REMOVAL"]), baseline.out)
        self.assertEqual(self.replace_blob(base, SPEC_A, functions("test_one")), functions("test_one"))
        self.assertEqual(run(self.repo, base, candidate), baseline)

    def test_a_replace_ref_on_the_map_blob_does_not_change_what_the_guard_reads(self) -> None:
        base, candidate = self.two_commits()
        baseline = run(self.repo, base, candidate)
        self.assertEqual((baseline.code, baseline.out, baseline.err), (0, "removed=1 defects=0\n", ""))
        self.assertEqual(self.replace_blob(candidate, MAP, map_text()), map_text())
        self.assertEqual(run(self.repo, base, candidate), baseline)

    def test_a_git_config_variable_is_not_given_to_git_and_replace_and_lazy_fetch_are_off(self) -> None:
        base, candidate = self.two_commits()
        baseline = run(self.repo, base, candidate)
        bad_config = self.repo.dir.parent / (self.repo.dir.name + "-bad.cfg")
        bad_config.write_text("[broken\n", encoding="utf-8")
        self.addCleanup(bad_config.unlink)
        hostile = {"GIT_CONFIG_COUNT": "1"}, {"GIT_CONFIG_GLOBAL": str(bad_config)}
        for extra in hostile:
            with self.subTest(sorted(extra)), mock.patch.dict(os.environ, extra):
                broken = subprocess.run(["git", "-C", str(self.repo.dir), "rev-parse", "HEAD"], capture_output=True)
                self.assertNotEqual(broken.returncode, 0, "the variable must break a plain git call for this test to mean anything")
                self.assertEqual(run(self.repo, base, candidate), baseline)
        real = subprocess.run
        calls: list[tuple[object, object]] = []

        def spy(*args: object, **kwargs: object) -> object:
            calls.append((args[0] if args else None, kwargs.get("env")))
            return real(*args, **kwargs)

        polluted = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_GLOBAL": str(bad_config), "GIT_NO_REPLACE_OBJECTS": "0", "GIT_NO_LAZY_FETCH": "0"}
        with mock.patch.dict(os.environ, polluted), mock.patch.object(cm.subprocess, "run", spy):
            self.assertEqual(run(self.repo, base, candidate), baseline)
        self.assertGreaterEqual(len(calls), 6)
        for command, environment in calls:
            self.assertIsInstance(command, list)
            self.assertIsInstance(environment, dict)
            arguments = command if isinstance(command, list) else []
            variables = environment if isinstance(environment, dict) else {}
            self.assertEqual(arguments[:4], ["git", "-C", str(self.repo.dir), "--no-replace-objects"])
            self.assertEqual([name for name in variables if name.upper().startswith("GIT_CONFIG_")], [])
            self.assertEqual((variables.get("GIT_NO_REPLACE_OBJECTS"), variables.get("GIT_NO_LAZY_FETCH")), ("1", "1"))

    def test_the_whole_git_config_family_is_dropped_and_none_of_it_reaches_a_git_child(self) -> None:
        base, candidate = self.two_commits()
        baseline = run(self.repo, base, candidate)
        bad_config = self.repo.dir.parent / (self.repo.dir.name + "-family.cfg")
        bad_config.write_text("[broken\n", encoding="utf-8")
        self.addCleanup(bad_config.unlink)
        family = {
            "GIT_CONFIG_SYSTEM": str(bad_config),
            "GIT_CONFIG_GLOBAL": str(bad_config),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_PARAMETERS": "'bogus",
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "include.path",
            "GIT_CONFIG_VALUE_0": str(bad_config),
            "GIT_CONFIG_KEY_1": "core.bare",
            "GIT_CONFIG_VALUE_1": "true",
        }
        breaking = (
            {"GIT_CONFIG_SYSTEM": family["GIT_CONFIG_SYSTEM"]},
            {"GIT_CONFIG_GLOBAL": family["GIT_CONFIG_GLOBAL"]},
            {"GIT_CONFIG_PARAMETERS": family["GIT_CONFIG_PARAMETERS"]},
            {key: family[key] for key in ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0", "GIT_CONFIG_KEY_1", "GIT_CONFIG_VALUE_1")},
        )
        for extra in breaking:
            with self.subTest(sorted(extra)), mock.patch.dict(os.environ, extra):
                plain = subprocess.run(["git", "-C", str(self.repo.dir), "rev-parse", "HEAD"], capture_output=True)
                self.assertNotEqual(plain.returncode, 0, "the variable must break a plain git call for this test to mean anything")
                self.assertEqual(run(self.repo, base, candidate), baseline)
        real = subprocess.run
        environments: list[object] = []

        def spy(*args: object, **kwargs: object) -> object:
            environments.append(kwargs.get("env"))
            return real(*args, **kwargs)

        with mock.patch.dict(os.environ, family), mock.patch.object(cm.subprocess, "run", spy):
            self.assertEqual(run(self.repo, base, candidate), baseline)
        self.assertGreaterEqual(len(environments), 6)
        for environment in environments:
            self.assertIsInstance(environment, dict)
            names = {name.upper() for name in (environment if isinstance(environment, dict) else {})}
            self.assertEqual(names & {name.upper() for name in family}, set())
            self.assertEqual([name for name in names if name.startswith("GIT_CONFIG")], [])

    def removal_with_a_grafted_parent(self) -> tuple[str, str]:
        """main^ is the commit holding two tests; a graft would make it a commit holding one. Returns (that commit, the graft line)."""
        parent = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        tip = self.repo.commit({SPEC_A: functions("test_one")})
        decoy = self.repo.commit_tree({SPEC_A: functions("test_one").encode("utf-8")}, parent=parent)
        return decoy, f"{tip} {decoy}\n"

    def run_relative(self) -> Result:
        return run(self.repo, "main^", "main")

    def test_a_graft_in_the_repository_does_not_move_a_relative_revision(self) -> None:
        decoy, line = self.removal_with_a_grafted_parent()
        baseline = self.run_relative()
        self.assertEqual((baseline.code, baseline.defect_codes(), self.summary(baseline)), (1, ["UNMAPPED_REMOVAL"], "removed=1 defects=1"), baseline.out)
        (self.repo.dir / ".git" / "info").mkdir(exist_ok=True)
        (self.repo.dir / ".git" / "info" / "grafts").write_text(line, encoding="ascii")
        self.assertEqual(git(self.repo.dir, "rev-parse", "main^").strip(), decoy, "the graft must move main^ for this test to mean anything")
        self.assertEqual(self.run_relative(), baseline)

    def test_an_inherited_graft_file_does_not_move_a_relative_revision(self) -> None:
        decoy, line = self.removal_with_a_grafted_parent()
        baseline = self.run_relative()
        self.assertEqual((baseline.code, baseline.defect_codes()), (1, ["UNMAPPED_REMOVAL"]), baseline.out)
        graft_file = self.repo.dir.parent / (self.repo.dir.name + "-inherited.grafts")
        graft_file.write_text(line, encoding="ascii")
        self.addCleanup(graft_file.unlink)
        with mock.patch.dict(os.environ, {"GIT_GRAFT_FILE": str(graft_file)}):
            moved = subprocess.run(["git", "-C", str(self.repo.dir), "rev-parse", "main^"], capture_output=True, text=True)
            self.assertEqual(moved.stdout.strip(), decoy, "the graft must move main^ for this test to mean anything")
            self.assertEqual(self.run_relative(), baseline)

    def test_every_git_child_runs_with_a_graft_file_that_does_not_exist(self) -> None:
        base, candidate = self.two_commits()
        inherited = self.repo.dir.parent / (self.repo.dir.name + "-inherited-too.grafts")
        inherited.write_text("", encoding="ascii")
        self.addCleanup(inherited.unlink)
        real = subprocess.run
        environments: list[object] = []

        def spy(*args: object, **kwargs: object) -> object:
            environments.append(kwargs.get("env"))
            return real(*args, **kwargs)

        with mock.patch.dict(os.environ, {"GIT_GRAFT_FILE": str(inherited)}), mock.patch.object(cm.subprocess, "run", spy):
            result = run(self.repo, base, candidate)
        self.assertEqual((result.code, result.out, result.err), (0, "removed=1 defects=0\n", ""))
        self.assertGreaterEqual(len(environments), 6)
        for environment in environments:
            self.assertIsInstance(environment, dict)
            variables = environment if isinstance(environment, dict) else {}
            given = [value for name, value in variables.items() if name.upper() == "GIT_GRAFT_FILE"]
            self.assertEqual(len(given), 1, variables)
            self.assertNotEqual(given[0], str(inherited))
            self.assertFalse(os.path.lexists(given[0]), given[0])

    # ticket 60, S54-17: git takes parents from the commit-graph file, which a writer of the store could forge
    def forge_commit_graph(self, victim: str, new_parent: str) -> None:
        """Write a commit-graph of every reachable commit, then make `new_parent` the first parent of `victim` in it."""
        git(self.repo.dir, "-c", "commitGraph.generationVersion=1", "commit-graph", "write", "--reachable", "--no-changed-paths")
        path = self.repo.dir / ".git" / "objects" / "info" / "commit-graph"
        data = bytearray(path.read_bytes())
        self.assertEqual(bytes(data[:4]), b"CGPH")
        chunks: dict[bytes, int] = {}
        for index in range(data[6] + 1):
            offset = 8 + 12 * index
            chunks[bytes(data[offset : offset + 4])] = struct.unpack(">Q", data[offset + 4 : offset + 12])[0]
        first_oid, commit_data = chunks[b"OIDL"], chunks[b"CDAT"]
        ids = [bytes(data[first_oid + 20 * n : first_oid + 20 * n + 20]).hex() for n in range((commit_data - first_oid) // 20)]
        record = commit_data + 36 * ids.index(victim)
        struct.pack_into(">I", data, record + 20, ids.index(new_parent))  # the first parent
        data[-20:] = hashlib.sha1(bytes(data[:-20])).digest()
        os.chmod(path, 0o666)
        path.write_bytes(bytes(data))

    def removal_with_a_forged_commit_graph(self) -> tuple[str, str]:
        """main^ is the commit holding two tests; the forged graph makes it a decoy holding one. Returns (the true parent, the decoy)."""
        parent = self.repo.commit({SPEC_A: functions("test_one", "test_two")})
        tip = self.repo.commit({SPEC_A: functions("test_one")})
        decoy = self.repo.commit_tree({SPEC_A: functions("test_one").encode("utf-8")}, parent=parent)
        git(self.repo.dir, "branch", "decoy", decoy)  # reachable, so the graph holds it
        self.forge_commit_graph(tip, decoy)
        return parent, decoy

    def test_a_forged_commit_graph_does_not_move_a_relative_revision(self) -> None:
        parent, decoy = self.removal_with_a_forged_commit_graph()
        self.assertEqual(git(self.repo.dir, "rev-parse", "main^").strip(), decoy, "the forged graph must move main^ for this test to mean anything")
        for base in ("main^", "main~1", "main^1", "HEAD^"):
            with self.subTest(base=base):
                result = run(self.repo, base, "main")
                self.assertEqual((result.code, result.defect_codes(), self.summary(result), result.err), (1, ["UNMAPPED_REMOVAL"], "removed=1 defects=1", ""), result.out)
        self.assertEqual(run(self.repo, parent, "main").code, 1)

    def test_every_git_child_runs_with_the_commit_graph_off(self) -> None:
        base, candidate = self.two_commits()
        real = subprocess.run
        commands: list[object] = []

        def spy(*args: object, **kwargs: object) -> object:
            commands.append(args[0] if args else None)
            return real(*args, **kwargs)

        with mock.patch.object(cm.subprocess, "run", spy):
            self.assertEqual(run(self.repo, base, candidate).code, 0)
        self.assertGreaterEqual(len(commands), 6)
        for command in commands:
            arguments = command if isinstance(command, list) else []
            self.assertTrue(
                any(arguments[at : at + 2] == ["-c", "core.commitGraph=false"] for at in range(len(arguments) - 1)),
                arguments,
            )


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
