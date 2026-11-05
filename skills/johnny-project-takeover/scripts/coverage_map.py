#!/usr/bin/env python3
"""Coverage-map guard: no test function leaves a spec file without a map row.

Usage: coverage_map.py --repo DIR --base COMMIT --candidate COMMIT --map PATH --specs DIR

The guard lists every test function present in a spec file under `--specs` at `--base`
and absent at `--candidate`, and requires a row for each of them in the map file read
at `--candidate`.

`--repo` must be the top level of a git work tree: a plain directory, or a subdirectory
of a work tree, is a tool fault. `--specs` must name a directory (a tree) at `--base`, at
`--candidate`, or at both; a path that names no tree at either commit is a tool fault (a guard
that checks nothing must not pass). A tree present at one commit only is read as empty at the
other; a present tree holding no spec file is not a fault. Trees are listed, not inferred: git
reports the tree entries themselves, so an empty tree object at `--specs` is a present, empty
tree (exit 0 when nothing was removed).

Spec file: a regular file (git mode 100644 or 100755) named `test_*.py` below `--specs`
(exact path-component prefix: a sibling directory whose name only begins like `specs` is not
below it). A symbolic link (120000) or a submodule entry (160000) is not a spec file and is
never parsed; a spec file that became a link at the candidate has all its tests removed.
Paths from git are decoded as UTF-8 with surrogateescape, so a path that is not UTF-8 is
still a test id (compared byte for byte, printed escaped), never a fault. Test: a function
(sync or async) whose name starts with `test`, defined at module level or inside a class
(nested classes included; also inside module-level or class-level `if`/`else`, `try`/`except`/
`else`/`finally`, `with`, `for`, `while` and `match` blocks, never inside another function).
Test id: `<path>::<name>` or `<path>::<Class>::<name>` (`<path>::<Outer>::<Inner>::<name>`
when nested). A test that moved to another file or was renamed is removed under its old id.
Ids are compared exactly, never trimmed. Specs are parsed with the grammar of the interpreter
that runs the guard (Python 3.11); a spec using later syntax does not parse and is a tool fault.

Map file (UTF-8 JSON, read as the blob at the candidate, found by `ls-tree` and read by
`cat-file`; never the working tree):

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
of them; absent while nothing was removed it is exit 0. A map path that names a tree, a
submodule entry or a link (an empty tree object included) is MAP_ROW_INVALID for the map path.
A key given twice in any object of the map file is MAP_ROW_INVALID: for the row (subject
`rows[N]`) when a row holds it, for the file when the top level or anything beside `rows`
does; a row that repeats a key covers nothing. Rows are shape-checked
wherever they stand, but a row's disposition is judged only when its assertion is a removed
id. A row that is invalid, or whose assertion is duplicated, covers nothing. Every string of a
row is valid Unicode without lone surrogates and without control characters (U+0000 to
U+001F, U+007F); a string that breaks this makes its row MAP_ROW_INVALID, so a map cannot
name a test whose path is not UTF-8.

Output: one line per defect, then `removed=N defects=M`. Every id or text taken from the
repository is printed JSON-quoted with ASCII escapes, so the console encoding never
changes an exit code. A defect or a fault is always one line: stderr messages are escaped
the same way, and no argument or parser message is echoed unescaped.

Exit codes: 0 pass, 1 contract red (defect lines on stdout), 2 tool fault (git cannot
serve a repository, a commit, a tree or a blob; `--repo` is not a work-tree top level;
`--specs` names no tree at either commit; a spec does not parse at either commit; any
unexpected error; one message per fault on stderr, never a traceback), 3 usage error (missing
or unknown option, empty value, an argument holding a lone surrogate or a control character,
an absolute path or a `..` segment in `--map` or `--specs`, a revision that starts with `-`).
Red before fault: the guard reports every red it can find and exits 1 when there is one, with
each fault it met printed on stderr; it exits 2 only when it found no red. A spec file that
cannot be read at either commit is judged by nothing (its tests are neither removed nor known
at the candidate, and a `carried_to` naming it is not judged), so a fault never invents a red.
A red is never reported as a tool fault when it was found, and a tool fault is never reported
as a red.

Every git child runs without the variables that select another repository (the git
directory, work tree, index file, object directory, alternate object directories, namespace,
ceiling directories, common directory and prefix), so a hook that exports them cannot point
the guard at another repository or make a plain directory pass as `--repo`. They also run
without the `GIT_CONFIG_*` variables, with `--no-replace-objects` and `GIT_NO_REPLACE_OBJECTS=1`
(a replace ref never redirects a lookup, so a blob read at a commit is the blob the commit
holds), with `-c core.commitGraph=false` (git takes no parent from a commit-graph file, which a
writer of the store could forge) and with `GIT_NO_LAZY_FETCH=1` (a lookup never fetches over the
network). `GIT_GRAFT_FILE` names a path that does not exist (any inherited value is dropped
first), so neither `info/grafts` nor an inherited graft file moves a parent: a relative revision
such as `main^` means what the commit objects say.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
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
_BAD_TEXT = re.compile("[\x00-\x1f\x7f\ud800-\udfff]")
REGULAR_MODES = frozenset((b"100644", b"100755"))
# Names that make git work on another repository, work tree or object store than the one
# named by `--repo`; none of them reaches a git child.
GIT_CONFIG_PREFIX = "GIT_CONFIG_"
GIT_SELECTING_VARIABLES = frozenset(
    (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_PREFIX",
    )
)
GIT_GRAFT_VARIABLE = "GIT_GRAFT_FILE"


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

    @property
    def is_regular_file(self) -> bool:
        """A regular blob: not a symbolic link (120000), not a submodule entry (160000)."""
        return self.kind == b"blob" and self.mode in REGULAR_MODES


@dataclass(frozen=True)
class MapLoad:
    """What the map file at the candidate says."""

    rows: tuple[MapRow, ...]
    defects: tuple[Defect, ...]


@dataclass(frozen=True)
class Report:
    removed: int
    defects: tuple[Defect, ...]
    faults: tuple[str, ...] = ()


def _quote(text: str) -> str:
    """JSON string with ASCII escapes (DEL included): one line, whatever the text holds."""
    return json.dumps(text, ensure_ascii=True).replace("\x7f", "\\u007f")


def _escape_char(char: str) -> str:
    number = ord(char)
    if number < 0x100:
        return f"\\x{number:02x}"
    return f"\\u{number:04x}" if number < 0x10000 else f"\\U{number:08x}"


def _oneline(text: str) -> str:
    """Printable ASCII only: a message that repeats raw input stays on one line."""
    return "".join(char if " " <= char <= "~" else _escape_char(char) for char in text)


def _text_problem(text: str) -> str | None:
    """Why `text` breaks the text-value rule, or None."""
    found = _BAD_TEXT.search(text)
    if found is None:
        return None
    return "a control character" if ord(found.group()) < 0x80 else "a lone surrogate"


# --------------------------------------------------------------------------- git


def git_environment() -> dict[str, str]:
    """The environment of a git child: the inherited one without the repository-selecting names and the `GIT_CONFIG_*` names, replace refs and lazy fetch off, grafts pointed at a path that does not exist."""
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() not in GIT_SELECTING_VARIABLES
        and not name.upper().startswith(GIT_CONFIG_PREFIX)
        and name.upper() not in ("GIT_NO_REPLACE_OBJECTS", "GIT_NO_LAZY_FETCH", GIT_GRAFT_VARIABLE)
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    environment[GIT_GRAFT_VARIABLE] = _absent_path()
    return environment


def _absent_path() -> str:
    """A path that names nothing: git reads no grafts from it, and neither `info/grafts` nor an inherited graft file is read."""
    path = os.path.join(tempfile.gettempdir(), f"coverage-map-no-graft-file-{uuid.uuid4().hex}")
    if os.path.lexists(path):
        raise ToolFault("cannot choose a graft file path that does not exist")
    return path


def run_git(repo: str, args: Sequence[str]) -> bytes:
    """Run one git query in `repo`; any failure is a tool fault carrying git's stderr."""
    command = ["git", "-C", repo, "--no-replace-objects", "-c", "core.commitGraph=false", *args]
    try:
        done = subprocess.run(command, capture_output=True, stdin=subprocess.DEVNULL, check=False, env=git_environment())
    except OSError as error:
        raise ToolFault(f"cannot run git: {error}") from error
    if done.returncode != 0:
        message = done.stderr.decode("utf-8", errors="replace").strip()
        raise ToolFault(f"git {' '.join(args)} failed ({done.returncode}): {message}")
    return done.stdout


def require_top_level(repo: str) -> None:
    """`repo` must be the top level of a git work tree, not a directory inside one."""
    out = run_git(repo, ["rev-parse", "--show-toplevel"])
    top = out.decode("utf-8", errors="surrogateescape").rstrip("\r\n")
    try:
        same = os.path.samefile(top, repo)
    except OSError as error:
        raise ToolFault(f"cannot compare --repo {_quote(repo)} with the work-tree top level {_quote(top)}: {error}") from error
    if not same:
        raise ToolFault(f"--repo {_quote(repo)} is not the top level of a git work tree (the top level is {_quote(top)})")


def resolve_commit(repo: str, revision: str) -> str:
    out = run_git(repo, ["rev-parse", "--verify", f"{revision}^{{commit}}"])
    resolved = out.decode("ascii", errors="replace").strip()
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", resolved):
        raise ToolFault(f"git rev-parse gave no commit id for {revision!r}")
    return resolved


def read_tree(repo: str, commit: str) -> dict[bytes, TreeEntry]:
    """Every entry of the commit, tree entries included: path bytes -> mode, type and object id."""
    out = run_git(repo, ["ls-tree", "-r", "-t", "-z", "--full-tree", commit])
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
            tree = ast.parse(source, filename="<spec>")
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


def has_tree(tree: Mapping[bytes, TreeEntry], directory: str) -> bool:
    """Is `directory` (repository-relative, `/` separators, empty for the root) a tree entry?

    Trees are listed by git, not inferred from the files below them, so an empty tree
    object is a present, empty tree.
    """
    if directory == "":
        return True
    entry = tree.get(directory.encode("utf-8"))
    return entry is not None and entry.kind == b"tree"


@dataclass(frozen=True)
class Side:
    """One commit of the comparison: its id and every entry of its tree."""

    commit: str
    tree: dict[bytes, TreeEntry]


@dataclass(frozen=True)
class SpecScan:
    """What the spec files say: the removed tests, and the candidate paths that could not be read."""

    removed: tuple[TestId, ...]
    candidate_ids: dict[str, TestId]
    unknown_paths: frozenset[str]


ParsedTests = tuple[tuple[tuple[str, ...], str], ...]


def _fault_text(error: Exception) -> str:
    return str(error) if isinstance(error, ToolFault) else f"unexpected {type(error).__name__}: {error}"


def open_side(repo: str, revision: str, faults: list[str]) -> Side | None:
    """Resolve and list one commit; a failure is noted as a fault and the side is unknown."""
    try:
        commit = resolve_commit(repo, revision)
        return Side(commit, read_tree(repo, commit))
    except Exception as error:  # noqa: BLE001 - noted as a fault, so that a red found elsewhere still reports
        faults.append(_fault_text(error))
        return None


def _spec_files(tree: Mapping[bytes, TreeEntry], prefix: bytes) -> dict[bytes, TreeEntry]:
    return {path: entry for path, entry in tree.items() if entry.is_regular_file and _is_spec_path(path, prefix)}


def _tests_of(
    repo: str,
    commit: str,
    entry: TreeEntry | None,
    path: str,
    parsed: dict[str, ParsedTests],
    faults: list[str],
) -> ParsedTests | None:
    """The tests of one spec file (none when it is absent), or None when it cannot be read."""
    if entry is None:
        return ()
    try:
        if entry.object_id not in parsed:
            parsed[entry.object_id] = parse_tests(read_blob(repo, entry.object_id), commit, path)
        return parsed[entry.object_id]
    except Exception as error:  # noqa: BLE001 - noted as a fault, so that a red found elsewhere still reports
        faults.append(_fault_text(error))
        return None


def scan_specs(repo: str, base: Side | None, candidate: Side, specs: str, faults: list[str]) -> SpecScan:
    """Every test removed between the sides, file by file.

    A file that cannot be read at either side is noted as a fault and judged by nothing: its
    tests are neither removed nor known at the candidate.
    """
    prefix = specs.encode("utf-8")
    base_files = _spec_files(base.tree, prefix) if base is not None else {}
    candidate_files = _spec_files(candidate.tree, prefix)
    parsed: dict[str, ParsedTests] = {}
    removed: dict[str, TestId] = {}
    candidate_ids: dict[str, TestId] = {}
    unknown: set[str] = set()
    for path_bytes in sorted(set(base_files) | set(candidate_files)):
        path = path_bytes.decode("utf-8", errors="surrogateescape")
        base_tests: ParsedTests | None = ()
        if base is not None:
            base_tests = _tests_of(repo, base.commit, base_files.get(path_bytes), path, parsed, faults)
        candidate_tests = _tests_of(repo, candidate.commit, candidate_files.get(path_bytes), path, parsed, faults)
        if candidate_tests is None:
            unknown.add(path)
            continue
        here = {TestId(path, scope, name).text: TestId(path, scope, name) for scope, name in candidate_tests}
        candidate_ids.update(here)
        if base is None or base_tests is None:
            continue
        for scope, name in base_tests:
            test = TestId(path, scope, name)
            if test.text not in here:
                removed[test.text] = test
    return SpecScan(tuple(sorted(removed.values())), candidate_ids, frozenset(unknown))


# -------------------------------------------------------------------------- map


def _invalid(subject: str, detail: str) -> Defect:
    return Defect(DefectCode.MAP_ROW_INVALID, subject, detail)


class _Object(dict[str, object]):
    """A JSON object that remembers the first key it was given twice."""

    repeated: str | None = None


def _object(pairs: list[tuple[str, object]]) -> _Object:
    result = _Object()
    for key, value in pairs:
        if key in result and result.repeated is None:
            result.repeated = key
        result[key] = value
    return result


def _repeated_key(value: object) -> str | None:
    """The first key given twice in `value` or in any object below it (iterative, so depth is no limit)."""
    pending: list[object] = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, _Object) and item.repeated is not None:
            return item.repeated
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return None


def _row_fields(index: int, raw: object) -> MapRow | Defect:
    subject = f"rows[{index}]"
    if not isinstance(raw, dict):
        return _invalid(subject, "row is not an object")
    repeated = _repeated_key(raw)
    if repeated is not None:
        return _invalid(subject, f"row repeats key {_quote(repeated)}")
    texts: dict[str, str] = {}
    for key in ("assertion", "disposition", "carried_to", "reason", "ticket"):
        if key not in raw:
            return _invalid(subject, f"field {key} is missing")
        value: object = raw[key]
        if not isinstance(value, str):
            return _invalid(subject, f"field {key} is not a string")
        problem = _text_problem(value)
        if problem is not None:
            return _invalid(subject, f"field {key} holds {problem}")
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
        document: object = json.loads(text, object_pairs_hook=_object)
    except (UnicodeDecodeError, ValueError, RecursionError):
        return MapLoad((), (_invalid(map_path, "map file is not UTF-8 JSON"),))
    if not isinstance(document, dict):
        return MapLoad((), (_invalid(map_path, "map file is not a JSON object"),))
    outside = document.repeated if isinstance(document, _Object) else None
    if outside is None:
        outside = _repeated_key([value for key, value in document.items() if key != "rows"])
    if outside is not None:
        return MapLoad((), (_invalid(map_path, f"map file repeats key {_quote(outside)}"),))
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


def _names_unknown_path(test_id: str, unknown_paths: frozenset[str]) -> bool:
    """Does the id name a test in a spec file that could not be read at the candidate?"""
    return any(test_id.startswith(path + "::") for path in unknown_paths)


def judge(
    removed: Sequence[TestId],
    candidate_ids: Mapping[str, TestId],
    load: MapLoad | None,
    unknown_paths: frozenset[str] = frozenset(),
) -> tuple[Defect, ...]:
    defects: list[Defect] = list(load.defects) if load is not None else []
    rows: dict[str, MapRow] = {row.assertion: row for row in load.rows} if load is not None else {}
    for test in removed:
        row = rows.get(test.text)
        if row is None:
            defects.append(Defect(DefectCode.UNMAPPED_REMOVAL, test.text, "removed test has no map row"))
        elif row.disposition is Disposition.CARRIED:
            if row.carried_to == "":
                defects.append(Defect(DefectCode.CARRIED_TARGET_MISSING, test.text, "carried_to is empty"))
            elif row.carried_to not in candidate_ids and not _names_unknown_path(row.carried_to, unknown_paths):
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
    """Find every red it can; a fault met on the way is noted, never a reason to drop a red."""
    require_top_level(args.repo)
    faults: list[str] = []
    base = open_side(args.repo, args.base, faults)
    candidate = open_side(args.repo, args.candidate, faults)
    if base is not None and candidate is not None:
        if not (has_tree(base.tree, args.specs) or has_tree(candidate.tree, args.specs)):
            faults.append(f"--specs {_quote(args.specs)} names no tree at base {base.commit} or at candidate {candidate.commit}")
    if candidate is None:
        return Report(0, (), tuple(faults))
    scan = scan_specs(args.repo, base, candidate, args.specs, faults)
    load: MapLoad | None = None
    readable = True
    entry = candidate.tree.get(args.map_path.encode("utf-8"))
    if entry is not None and entry.is_regular_file:
        try:
            load = parse_map(args.map_path, read_blob(args.repo, entry.object_id))
        except Exception as error:  # noqa: BLE001 - noted as a fault, so that a red found elsewhere still reports
            faults.append(_fault_text(error))
            readable = False
    elif entry is not None:
        load = MapLoad((), (_invalid(args.map_path, "map path is not a file"),))
    if not readable:
        return Report(len(scan.removed), (), tuple(faults))
    try:
        defects = judge(scan.removed, scan.candidate_ids, load, scan.unknown_paths)
    except Exception as error:  # noqa: BLE001 - noted as a fault
        faults.append(_fault_text(error))
        defects = ()
    return Report(len(scan.removed), defects, tuple(faults))


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
    for option in ("--repo", "--base", "--candidate", "--map", "--specs"):
        problem = _text_problem(getattr(namespace, option[2:]))
        if problem is not None:
            raise UsageError(f"{option} holds {problem}")
    repo: str = namespace.repo
    if repo.strip() == "":
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
        print(f"coverage_map: {_oneline(str(error))}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE
    try:
        report = check(args)
    except ToolFault as error:
        print(f"coverage_map: tool fault: {_oneline(str(error))}", file=sys.stderr)
        return EXIT_FAULT
    except Exception as error:  # noqa: BLE001 - an unexpected error is a tool fault, never a red
        detail = f"unexpected {type(error).__name__}: {error}"
        print(f"coverage_map: tool fault: {_oneline(detail)}", file=sys.stderr)
        return EXIT_FAULT
    if report.defects or not report.faults:
        for defect in report.defects:
            print(defect.line())
        print(f"removed={report.removed} defects={len(report.defects)}")
    for fault in report.faults:
        print(f"coverage_map: tool fault: {_oneline(fault)}", file=sys.stderr)
    if report.defects:
        return EXIT_RED
    return EXIT_FAULT if report.faults else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
