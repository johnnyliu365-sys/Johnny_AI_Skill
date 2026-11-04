#!/usr/bin/env python3
"""Coverage-map guard: no test function leaves a spec file without a map row.

Usage: coverage_map.py --repo DIR --base COMMIT --candidate COMMIT --map PATH --specs DIR

The guard lists every test function present in a spec file under `--specs` at `--base`
and absent at `--candidate`, and requires a row for each of them in the map file read
at `--candidate`.

Spec file: a file named `test_*.py` below `--specs` (exact path-component prefix:
a sibling directory whose name only begins like `specs` is not below it). Test: a function (sync or async) whose name starts
with `test`, defined at module level or inside a class (nested classes included; also
inside module-level or class-level `if`, `try`, `with`, `for`, `while` and `match`
blocks, never inside another function). Test id: `<path>::<name>` or
`<path>::<Class>::<name>` (`<path>::<Outer>::<Inner>::<name>` when nested). A test that
moved to another file or was renamed is removed under its old id. Ids are compared
exactly, never trimmed.

Map file (UTF-8 JSON, read with `git show <candidate>:<map>`):

    {"rows": [{"assertion": <id>, "disposition": "carried" | "dropped" | "escalated",
               "carried_to": <id or "">, "reason": <text or "">, "ticket": <text or "">}]}

Defect codes (exit 1):
  UNMAPPED_REMOVAL          a removed test id has no valid map row
  CARRIED_TARGET_MISSING    `carried`, but `carried_to` is empty or names no test at the candidate
  DROPPED_WITHOUT_REASON    `dropped` with an empty or whitespace-only `reason`
  ESCALATED_WITHOUT_TICKET  `escalated` with an empty or whitespace-only `ticket`
  MAP_ROW_INVALID           an unknown disposition, a missing or non-string field, an empty or
                            whitespace-padded assertion, a duplicate assertion, a map file that
                            is not JSON of the required shape

A map file absent at the candidate while tests were removed is UNMAPPED_REMOVAL for each
of them; absent while nothing was removed it is exit 0. Rows are shape-checked wherever
they stand, but a row's disposition is judged only when its assertion is a removed id.

Output: one line per defect, then `removed=N defects=M`. Every id or text taken from the
repository is printed JSON-quoted with ASCII escapes, so the console encoding never
changes an exit code.

Exit codes: 0 pass, 1 contract red (defect lines on stdout), 2 tool fault (git cannot
serve a repository, a commit, a tree or a blob; a spec does not parse at either commit;
any unexpected error; message on stderr, never a traceback), 3 usage error (missing or
unknown option, empty value, an absolute path or a `..` segment in `--map` or `--specs`,
a revision that starts with `-`). A red is never reported as a tool fault and a tool
fault is never reported as a red.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import sys
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import NoReturn

USAGE = "usage: coverage_map.py --repo DIR --base COMMIT --candidate COMMIT --map PATH --specs DIR"

EXIT_PASS = 0
EXIT_RED = 1
EXIT_FAULT = 2
EXIT_USAGE = 3

TEST_PREFIX = "test"
SPEC_FILE_PREFIX = b"test_"
SPEC_FILE_SUFFIX = b".py"
_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")


class ToolFault(Exception):
    """git or the repository cannot serve the run: exit 2."""


class UsageError(Exception):
    """The command line is wrong: exit 3."""


class DefectCode(Enum):
    UNMAPPED_REMOVAL = "UNMAPPED_REMOVAL"
    CARRIED_TARGET_MISSING = "CARRIED_TARGET_MISSING"
    DROPPED_WITHOUT_REASON = "DROPPED_WITHOUT_REASON"
    ESCALATED_WITHOUT_TICKET = "ESCALATED_WITHOUT_TICKET"
    MAP_ROW_INVALID = "MAP_ROW_INVALID"


class Disposition(Enum):
    CARRIED = "carried"
    DROPPED = "dropped"
    ESCALATED = "escalated"


@dataclass(frozen=True, order=True)
class TestId:
    """A test function: spec path, enclosing class names (outermost first), function name."""

    __test__ = False  # not a pytest collection target

    path: str
    scope: tuple[str, ...]
    name: str

    @property
    def text(self) -> str:
        return "::".join((self.path, *self.scope, self.name))


@dataclass(frozen=True)
class MapRow:
    index: int
    assertion: str
    disposition: Disposition
    carried_to: str
    reason: str
    ticket: str


@dataclass(frozen=True)
class Defect:
    code: DefectCode
    subject: str
    detail: str

    def line(self) -> str:
        return f"{self.code.value} {_quote(self.subject)} {self.detail}"


@dataclass(frozen=True)
class CliArgs:
    repo: str
    base: str
    candidate: str
    map_path: str
    specs: str


@dataclass(frozen=True)
class TreeEntry:
    mode: bytes
    kind: bytes
    object_id: str


@dataclass(frozen=True)
class MapLoad:
    """What the map file at the candidate says."""

    rows: tuple[MapRow, ...]
    defects: tuple[Defect, ...]


@dataclass(frozen=True)
class Report:
    removed: int
    defects: tuple[Defect, ...]


def _quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=True)


# --------------------------------------------------------------------------- git


def run_git(repo: str, args: Sequence[str]) -> bytes:
    """Run one git query in `repo`; any failure is a tool fault carrying git's stderr."""
    command = ["git", "-C", repo, *args]
    try:
        done = subprocess.run(command, capture_output=True, stdin=subprocess.DEVNULL, check=False)
    except OSError as error:
        raise ToolFault(f"cannot run git: {error}") from error
    if done.returncode != 0:
        message = done.stderr.decode("utf-8", errors="replace").strip()
        raise ToolFault(f"git {' '.join(args)} failed ({done.returncode}): {message}")
    return done.stdout


def resolve_commit(repo: str, revision: str) -> str:
    out = run_git(repo, ["rev-parse", "--verify", f"{revision}^{{commit}}"])
    resolved = out.decode("ascii", errors="replace").strip()
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", resolved):
        raise ToolFault(f"git rev-parse gave no commit id for {revision!r}")
    return resolved


def read_tree(repo: str, commit: str) -> dict[bytes, TreeEntry]:
    """Every file of the commit: path bytes -> mode, type and object id."""
    out = run_git(repo, ["ls-tree", "-r", "-z", "--full-tree", commit])
    entries: dict[bytes, TreeEntry] = {}
    for record in out.split(b"\0"):
        if not record:
            continue
        head, separator, path = record.partition(b"\t")
        fields = head.split(b" ")
        if not separator or len(fields) != 3:
            raise ToolFault(f"git ls-tree gave an unreadable record at commit {commit}")
        entries[path] = TreeEntry(fields[0], fields[1], fields[2].decode("ascii", errors="replace"))
    return entries


def read_blob(repo: str, object_id: str) -> bytes:
    return run_git(repo, ["cat-file", "blob", object_id])


# ------------------------------------------------------------------ enumeration


def _collect(body: Sequence[ast.stmt], scope: tuple[str, ...], found: list[tuple[tuple[str, ...], str]]) -> None:
    """Gather test functions from a module or class body; never descend into functions."""
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith(TEST_PREFIX):
                found.append((scope, node.name))
        elif isinstance(node, ast.ClassDef):
            _collect(node.body, (*scope, node.name), found)
        elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While)):
            _collect(node.body, scope, found)
            _collect(node.orelse, scope, found)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            _collect(node.body, scope, found)
        elif isinstance(node, (ast.Try, ast.TryStar)):
            _collect(node.body, scope, found)
            for handler in node.handlers:
                _collect(handler.body, scope, found)
            _collect(node.orelse, scope, found)
            _collect(node.finalbody, scope, found)
        elif isinstance(node, ast.Match):
            for case in node.cases:
                _collect(case.body, scope, found)


def parse_tests(source: bytes, commit: str, path: str) -> tuple[tuple[tuple[str, ...], str], ...]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source, filename=path)
    except (SyntaxError, ValueError, RecursionError, MemoryError) as error:
        raise ToolFault(f"spec does not parse at commit {commit}: {_quote(path)}: {type(error).__name__}: {error}") from error
    found: list[tuple[tuple[str, ...], str]] = []
    _collect(tree.body, (), found)
    return tuple(found)


def _is_spec_path(path: bytes, prefix: bytes) -> bool:
    if prefix and not path.startswith(prefix + b"/"):
        return False
    name = path.rsplit(b"/", 1)[-1]
    return name.startswith(SPEC_FILE_PREFIX) and name.endswith(SPEC_FILE_SUFFIX)


def enumerate_tests(
    repo: str,
    commit: str,
    tree: Mapping[bytes, TreeEntry],
    specs: str,
    parsed: dict[str, tuple[tuple[tuple[str, ...], str], ...]],
) -> dict[str, TestId]:
    """Every test of every spec file under `specs` at `commit`, keyed by id text.

    `parsed` caches the parse of a blob by object id, so a file identical at both commits
    is read once.
    """
    prefix = specs.encode("utf-8")
    ids: dict[str, TestId] = {}
    for path_bytes in sorted(tree):
        entry = tree[path_bytes]
        if entry.kind != b"blob" or not _is_spec_path(path_bytes, prefix):
            continue
        try:
            path = path_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ToolFault(f"spec path is not UTF-8 at commit {commit}: {path_bytes!r}") from error
        if entry.object_id not in parsed:
            parsed[entry.object_id] = parse_tests(read_blob(repo, entry.object_id), commit, path)
        for scope, name in parsed[entry.object_id]:
            test = TestId(path, scope, name)
            ids[test.text] = test
    return ids


# -------------------------------------------------------------------------- map


def _invalid(subject: str, detail: str) -> Defect:
    return Defect(DefectCode.MAP_ROW_INVALID, subject, detail)


def _row_fields(index: int, raw: object) -> MapRow | Defect:
    subject = f"rows[{index}]"
    if not isinstance(raw, dict):
        return _invalid(subject, "row is not an object")
    texts: dict[str, str] = {}
    for key in ("assertion", "disposition", "carried_to", "reason", "ticket"):
        if key not in raw:
            return _invalid(subject, f"field {key} is missing")
        value: object = raw[key]
        if not isinstance(value, str):
            return _invalid(subject, f"field {key} is not a string")
        texts[key] = value
    assertion = texts["assertion"]
    if assertion.strip() == "":
        return _invalid(subject, "assertion is empty")
    if assertion != assertion.strip():
        return _invalid(subject, "assertion has surrounding whitespace")
    try:
        disposition = Disposition(texts["disposition"])
    except ValueError:
        return _invalid(subject, f"unknown disposition {_quote(texts['disposition'])}")
    return MapRow(index, assertion, disposition, texts["carried_to"], texts["reason"], texts["ticket"])


def parse_map(map_path: str, source: bytes) -> MapLoad:
    """Validate the map file at the boundary into typed rows; shape defects ride along."""
    try:
        text = source.decode("utf-8")
        document: object = json.loads(text)
    except (UnicodeDecodeError, ValueError, RecursionError):
        return MapLoad((), (_invalid(map_path, "map file is not UTF-8 JSON"),))
    if not isinstance(document, dict):
        return MapLoad((), (_invalid(map_path, "map file is not a JSON object"),))
    if "rows" not in document:
        return MapLoad((), (_invalid(map_path, "map file has no rows field"),))
    raw_rows: object = document["rows"]
    if not isinstance(raw_rows, list):
        return MapLoad((), (_invalid(map_path, "rows is not an array"),))
    defects: list[Defect] = []
    valid: list[MapRow] = []
    for index, raw in enumerate(raw_rows):
        parsed = _row_fields(index, raw)
        if isinstance(parsed, Defect):
            defects.append(parsed)
        else:
            valid.append(parsed)
    counts: dict[str, int] = {}
    for row in valid:
        counts[row.assertion] = counts.get(row.assertion, 0) + 1
    usable: list[MapRow] = []
    seen: set[str] = set()
    for row in valid:
        if counts[row.assertion] > 1:
            if row.assertion in seen:
                defects.append(_invalid(f"rows[{row.index}]", f"duplicate assertion {_quote(row.assertion)}"))
            seen.add(row.assertion)
            continue
        usable.append(row)
    defects.sort(key=lambda d: (_row_number(d.subject), d.detail))
    return MapLoad(tuple(usable), tuple(defects))


def _row_number(subject: str) -> int:
    found = re.fullmatch(r"rows\[(\d+)\]", subject)
    return int(found.group(1)) if found else -1


# --------------------------------------------------------------------- the guard


def judge(removed: Sequence[TestId], candidate_ids: Mapping[str, TestId], load: MapLoad | None) -> tuple[Defect, ...]:
    defects: list[Defect] = list(load.defects) if load is not None else []
    rows: dict[str, MapRow] = {row.assertion: row for row in load.rows} if load is not None else {}
    for test in removed:
        row = rows.get(test.text)
        if row is None:
            defects.append(Defect(DefectCode.UNMAPPED_REMOVAL, test.text, "removed test has no map row"))
        elif row.disposition is Disposition.CARRIED:
            if row.carried_to == "":
                defects.append(Defect(DefectCode.CARRIED_TARGET_MISSING, test.text, "carried_to is empty"))
            elif row.carried_to not in candidate_ids:
                defects.append(
                    Defect(DefectCode.CARRIED_TARGET_MISSING, test.text, f"carried_to {_quote(row.carried_to)} names no test at the candidate")
                )
        elif row.disposition is Disposition.DROPPED:
            if row.reason.strip() == "":
                defects.append(Defect(DefectCode.DROPPED_WITHOUT_REASON, test.text, "dropped row has no reason"))
        elif row.ticket.strip() == "":
            defects.append(Defect(DefectCode.ESCALATED_WITHOUT_TICKET, test.text, "escalated row has no ticket"))
    return tuple(defects)


def check(args: CliArgs) -> Report:
    run_git(args.repo, ["rev-parse", "--git-dir"])
    base = resolve_commit(args.repo, args.base)
    candidate = resolve_commit(args.repo, args.candidate)
    base_tree = read_tree(args.repo, base)
    candidate_tree = read_tree(args.repo, candidate)
    parsed: dict[str, tuple[tuple[tuple[str, ...], str], ...]] = {}
    base_ids = enumerate_tests(args.repo, base, base_tree, args.specs, parsed)
    candidate_ids = enumerate_tests(args.repo, candidate, candidate_tree, args.specs, parsed)
    removed = sorted(base_ids[key] for key in base_ids if key not in candidate_ids)
    load: MapLoad | None = None
    entry = candidate_tree.get(args.map_path.encode("utf-8"))
    if entry is not None:
        if entry.kind == b"blob":
            load = parse_map(args.map_path, read_blob(args.repo, entry.object_id))
        else:
            load = MapLoad((), (_invalid(args.map_path, "map path is not a file"),))
    return Report(len(removed), judge(removed, candidate_ids, load))


# -------------------------------------------------------------------- the CLI


def normalize_relative(raw: str, option: str, allow_root: bool) -> str:
    """A repository-relative path with `/` separators; absolute paths and `..` are refused."""
    if raw.strip() == "" or "\0" in raw:
        raise UsageError(f"{option} must not be empty")
    path = raw.replace("\\", "/")
    if path.startswith("/") or _DRIVE_PREFIX.match(path):
        raise UsageError(f"{option} must be repository-relative, not absolute")
    segments = [segment for segment in path.split("/") if segment not in ("", ".")]
    if ".." in segments:
        raise UsageError(f"{option} must not contain '..'")
    if not segments and not allow_root:
        raise UsageError(f"{option} must name a file")
    return "/".join(segments)


def _revision(raw: str, option: str) -> str:
    if raw.strip() == "":
        raise UsageError(f"{option} must not be empty")
    if raw.startswith("-"):
        raise UsageError(f"{option} must not start with '-'")
    return raw


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise UsageError(message)


def parse_args(argv: Sequence[str]) -> CliArgs:
    parser = _Parser(prog="coverage_map.py", add_help=False, allow_abbrev=False)
    for option in ("--repo", "--base", "--candidate", "--map", "--specs"):
        parser.add_argument(option, required=True, dest=option[2:])
    namespace = parser.parse_args(list(argv))
    repo: str = namespace.repo
    if repo.strip() == "" or "\0" in repo:
        raise UsageError("--repo must not be empty")
    return CliArgs(
        repo=repo,
        base=_revision(namespace.base, "--base"),
        candidate=_revision(namespace.candidate, "--candidate"),
        map_path=normalize_relative(namespace.map, "--map", allow_root=False),
        specs=normalize_relative(namespace.specs, "--specs", allow_root=True),
    )


def _keep_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace")


def main(argv: Sequence[str] | None = None) -> int:
    _keep_console_encoding()
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        args = parse_args(arguments)
    except UsageError as error:
        print(f"coverage_map: {error}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    try:
        report = check(args)
    except ToolFault as error:
        print(f"coverage_map: tool fault: {error}", file=sys.stderr)
        return EXIT_FAULT
    except Exception as error:  # noqa: BLE001 - an unexpected error is a tool fault, never a red
        print(f"coverage_map: tool fault: unexpected {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_FAULT
    for defect in report.defects:
        print(defect.line())
    print(f"removed={report.removed} defects={len(report.defects)}")
    return EXIT_RED if report.defects else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
