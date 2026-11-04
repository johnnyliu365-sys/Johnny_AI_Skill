#!/usr/bin/env python3
"""Tool-repair guard: a repair commit changes only allowlisted paths and never a protected one.

Usage: repair_guard.py --repo <dir> --repair <commit> --dispatch <dispatch-file>

The dispatch file carries two lines that start at column 0. Each value is one JSON array
of strings, and every entry is a repository-relative path in forward-slash form. An entry
that ends in `/` covers that directory and everything under it; any other entry is one
exact path:

    repair_allowlist: ["<path or directory/>", ...]
    protected_paths: ["<path or directory/>", ...]

The guard also always protects the directory this script lives in (the gate scripts),
whether or not `protected_paths` names it. An empty allowlist makes every change an outside
change; an empty protected list leaves only the gate scripts protected.

History is read from raw objects, never from git's answer about ancestry. The repair
commit is resolved to its object id, then read as a raw commit object through
`git cat-file --batch` (the id on standard input, replace refs off): its `tree` line and
its `parent` lines come from that object, and its first parent is read the same way for
its tree. The changed paths are those of `git diff --name-status -M -z` between the two
tree ids, with quoting off, so a graft file (in the repository, in the common directory of
a linked work tree, or named by the environment), a replace ref or a shallow file cannot
change which parent or which trees are compared. A merge is recognised from its parent
lines; a root commit is compared against the empty tree, which is asked from git for the
object format of the repository and never written down here; a first parent the object
store cannot serve is a fault. Added, modified, deleted, type-changed and renamed paths
all count, and a rename counts on both its old and its new side. Submodule pointers
(gitlinks) always count: the diff runs with submodule ignoring switched off both in the
configuration and on the command line, so neither the ignore setting of a tracked
submodule list nor a repository setting can hide a moved pointer; external diff drivers
and text conversion are off. The revision given to `--repair` names a commit by id or by
reference; a name that uses an ancestry or path operator is a usage error, because git
would answer it through the history that grafts rewrite.

Every git child runs with the environment variables that select a repository, a graft
file, a shallow file, a replace ref base or a configuration removed, and with replace
objects and lazy fetching switched off.

Matching is by path segment, never by character prefix: the directory entry `d/` covers
`d/x` and does not cover `d2/x` or a path named exactly `d`. Entries are compared exactly;
nothing is decoded or Unicode-normalised. On Windows case is compared in the fail-closed
direction on both sides: an allowlist entry covers a path when the two are equal ignoring
ASCII case only (a non-ASCII character must match exactly, so the allowlist never grows
beyond what the file system treats as one name), while a protected entry and the gate
script directory cover a path when the two are equal under full Unicode case folding (so
protection never shrinks). Elsewhere case matters.

Defect codes (one output line each, exit 1):

    OUTSIDE_ALLOWLIST        a changed path is covered by no allowlist entry
    PROTECTED_PATH_TOUCHED   a changed path is covered by a protected entry or a gate script
    REPAIR_NOT_SINGLE_PARENT the repair commit is a merge or a root commit
    TEXT_VALUE_INVALID       a string read from the dispatch file or from git holds a lone
                             surrogate, an undecodable byte or a control character
                             (U+0000-U+001F, U+007F)

Every printed subject is escaped with Python `repr`, so one defect is always one line. On
exit 0 the only output is `paths=N defects=0`, where N counts the distinct changed paths.

A dispatch that holds a text defect is a red by itself and its entries cannot be trusted,
so no entry is used: the allowlist and the protected entries are not judged. Every rule
that needs no entry still applies: the text values of the changed paths, the single-parent
rule and the protection of the gate scripts, so a change to a gate script is reported next
to the text red. git is still asked, so any fault is reported too.

The dispatch file is decoded as UTF-8 with surrogate escapes, so no byte sequence makes it
unreadable. An undecodable byte or a raw control character on a block line (inside or
outside a JSON string) is a TEXT_VALUE_INVALID red; the same on a line the gate does not
read is ignored. A block line that is not one JSON array of strings for any other reason
is a usage error.

Exit codes: 0 pass, 1 contract red (at least one defect), 2 tool fault (git cannot serve
the check, the repository is not a repository top level, the dispatch file cannot be
read, standard output or standard error cannot be written, an unexpected error), 3 usage
error (bad arguments, a dispatch without both lines, a line that is not one JSON array of
strings, a null value, an empty entry, an entry that is absolute, uses a backslash or holds
an empty, `.` or `..` segment). A text-value defect is a red (exit 1) in a file or in git
output and a usage error (exit 3) in an argument.

Red before fault: the guard reports every red it can find and exits 1 when there is one,
with the fault printed on standard error. It exits 2 only when it found no red. The one
exception is standard output that cannot be written: then no verdict can be delivered and
the exit is 2 whatever was found. A standard error that cannot be written decides the exit
only when there is nothing else to deliver: when every red line reached standard output
the exit is still 1.
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TextIO

USAGE = "usage: repair_guard.py --repo <dir> --repair <commit> --dispatch <dispatch-file>"

ALLOW_KEY = "repair_allowlist"
PROTECT_KEY = "protected_paths"
GATE_DIRECTORY = "skills/johnny-project-takeover/scripts/"

OUTSIDE_ALLOWLIST = "OUTSIDE_ALLOWLIST"
PROTECTED_PATH_TOUCHED = "PROTECTED_PATH_TOUCHED"
REPAIR_NOT_SINGLE_PARENT = "REPAIR_NOT_SINGLE_PARENT"
TEXT_VALUE_INVALID = "TEXT_VALUE_INVALID"

EXIT_PASS = 0
EXIT_RED = 1
EXIT_FAULT = 2
EXIT_USAGE = 3

GIT_TIMEOUT_SECONDS = 300.0
# Submodule pointers always count: ignoring is switched off in the configuration and on the
# command line (a per-submodule setting in a tracked list outranks the configuration only).
DIFF_OPTIONS = ("-c", "diff.ignoreSubmodules=none")
DIFF_FLAGS = ("--name-status", "-M", "-z", "--ignore-submodules=none", "--no-ext-diff", "--no-textconv")
DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
# Environment variables that would point git at some other repository than --repo, or at
# other history, objects or settings than the repository itself holds.
GIT_SELECTORS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
    "GIT_PREFIX",
    "GIT_CEILING_DIRECTORIES",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_GRAFT_FILE",
    "GIT_SHALLOW_FILE",
    "GIT_REPLACE_REF_BASE",
    "GIT_CONFIG",
)
# Every variable whose name starts with this prefix is removed (the configuration ones).
GIT_SCRUBBED_PREFIX = "GIT_CONFIG_"
# Variables every git child gets: replace objects off, no lazy fetch from a remote.
GIT_FORCED = (("GIT_NO_REPLACE_OBJECTS", "1"), ("GIT_NO_LAZY_FETCH", "1"))
OBJECT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
# A revision that goes through ancestry or a path: git answers these through rewritten history.
ANCESTRY_MARKS = ("^", "~", ":", "@{")


class UsageError(Exception):
    """The arguments or the dispatch lines are wrong: exit 3."""


class ToolFault(Exception):
    """git or the file system cannot serve the check: exit 2."""


@dataclass(frozen=True)
class PathRule:
    """One allowlist or protected entry: an exact path, or a directory when it ends in `/`."""

    entry: str
    is_directory: bool

    def covers(self, path: str, case_insensitive: bool, full_folding: bool = False) -> bool:
        """Whether this entry covers `path`.

        `case_insensitive` False compares exactly. True compares ignoring ASCII case only,
        or under full Unicode case folding when `full_folding` is also True.
        """
        entry, subject = self.entry, path
        if case_insensitive:
            if full_folding:
                entry, subject = entry.casefold(), subject.casefold()
            else:
                entry, subject = ascii_lower(entry), ascii_lower(subject)
        if self.is_directory:
            return subject.startswith(entry) and len(subject) > len(entry)
        return subject == entry


@dataclass(frozen=True)
class Defect:
    code: str
    subject: str
    detail: str

    def line(self) -> str:
        text = f"{self.code} {self.subject}"
        return f"{text}: {self.detail}" if self.detail else text


@dataclass(frozen=True)
class Arguments:
    repo: str
    repair: str
    dispatch: str


@dataclass(frozen=True)
class RawCommit:
    """The tree and the parents a raw commit object names; nothing git infers."""

    tree: str
    parents: tuple[str, ...]


@dataclass(frozen=True)
class DispatchRules:
    allowlist: tuple[PathRule, ...]
    protected: tuple[PathRule, ...]
    text_defects: tuple[Defect, ...]


ASCII_LOWER = {code: code + 32 for code in range(ord("A"), ord("Z") + 1)}


def ascii_lower(text: str) -> str:
    """`text` with the ASCII letters lowered and every other character left as it is."""
    return text.translate(ASCII_LOWER)


def quote(text: str) -> str:
    """One printable line for `text`: Python repr, which escapes every non-printable character."""
    return repr(text)


def bad_character(text: str) -> str | None:
    """Name the first lone surrogate or control character in `text`, else None."""
    for char in text:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            return f"a lone surrogate (U+{code:04X})"
        if code <= 0x1F or code == 0x7F:
            return f"a control character (U+{code:04X})"
    return None


def make_rule(entry: str, where: str) -> PathRule:
    """Validate one entry that holds no text defect; raise UsageError when it is not a clean path."""
    if not entry.strip():
        raise UsageError(f"{where}: an entry must not be empty")
    if "\\" in entry:
        raise UsageError(f"{where}: an entry must use forward slashes, got {quote(entry)}")
    if entry.startswith("/") or DRIVE_PREFIX.match(entry) is not None:
        raise UsageError(f"{where}: an entry must be repository-relative, got {quote(entry)}")
    is_directory = entry.endswith("/")
    body = entry[:-1] if is_directory else entry
    for segment in body.split("/"):
        if segment == "":
            raise UsageError(f"{where}: an entry must not hold an empty segment, got {quote(entry)}")
        if segment in (".", ".."):
            raise UsageError(f"{where}: an entry must not hold a {segment!r} segment, got {quote(entry)}")
    return PathRule(entry=entry, is_directory=is_directory)


def _parse_line(
    lines: Sequence[str], key: str, text_defects: list[Defect]
) -> tuple[PathRule, ...]:
    marker = key + ":"
    found = [(index, line) for index, line in enumerate(lines) if line.startswith(marker)]
    if not found:
        raise UsageError(f"no {key}: line in the dispatch")
    if len(found) > 1:
        raise UsageError(f"line {found[1][0] + 1}: {key} is given twice (first at line {found[0][0] + 1})")
    index, line = found[0]
    number = index + 1
    bad = bad_character(line)
    if bad is not None:
        text_defects.append(Defect(TEXT_VALUE_INVALID, quote(line), f"line {number} of the dispatch holds {bad}"))
    raw = line[len(marker):].strip(" ")
    if not raw:
        raise UsageError(f"line {number}: {key} has no value")
    value = _read_value(raw, key, number, bad is not None)
    rules: list[PathRule] = []
    for position, element in enumerate(value, 1):
        where = f"line {number}, {key} entry {position}"
        if not isinstance(element, str):
            raise UsageError(f"{where}: an entry must be a JSON string")
        problem = bad_character(element)
        if problem is not None:
            if bad is None:
                text_defects.append(Defect(TEXT_VALUE_INVALID, quote(element), f"{where} holds {problem}"))
            continue
        rules.append(make_rule(element, where))
    return tuple(rules)


def _read_value(raw: str, key: str, number: int, line_is_bad: bool) -> list[object]:
    """The JSON array on a block line; a bad character is a text red, never a structure error.

    A raw control character inside a JSON string is read as part of the string. A bad
    character anywhere else is judged as the blank it would have been, so the line is
    still checked for being one JSON array of strings.
    """
    try:
        value: object = json.loads(raw, strict=False)
    except (ValueError, RecursionError):
        value = None
        if line_is_bad:
            blanked = "".join(" " if bad_character(char) is not None else char for char in raw)
            try:
                value = json.loads(blanked, strict=False)
            except (ValueError, RecursionError):
                value = None
        if value is None:
            raise UsageError(f"line {number}: the value of {key} is not one JSON value") from None
    if not isinstance(value, list):
        raise UsageError(f"line {number}: {key} must be a JSON array of strings")
    return list(value)


def parse_dispatch(text: str) -> DispatchRules:
    """Read both lines of a dispatch text; raise UsageError when either breaks the grammar."""
    lines = [line[:-1] if line.endswith("\r") else line for line in text.split("\n")]
    text_defects: list[Defect] = []
    allowlist = _parse_line(lines, ALLOW_KEY, text_defects)
    protected = _parse_line(lines, PROTECT_KEY, text_defects)
    return DispatchRules(allowlist=allowlist, protected=protected, text_defects=tuple(text_defects))


def check_paths(
    paths: Sequence[str],
    allowlist: Sequence[PathRule],
    protected: Sequence[PathRule],
    case_insensitive: bool,
    judge_rules: bool = True,
) -> list[Defect]:
    """Defects of the changed `paths` against the rules; the gate directory is always protected.

    With `judge_rules` False the rules came from a dispatch that already holds a text
    defect, so no entry is used: neither an outside path nor a path under a protected
    entry can be judged fairly. What needs no entry still applies: the text values of the
    paths and the protection of the gate directory.
    """
    gate = PathRule(GATE_DIRECTORY, True)
    guarded = (*protected, gate) if judge_rules else (gate,)
    defects: list[Defect] = []
    for path in paths:
        problem = bad_character(path)
        if problem is not None:
            defects.append(Defect(TEXT_VALUE_INVALID, quote(path), f"a changed path holds {problem}"))
        if judge_rules and not any(rule.covers(path, case_insensitive, False) for rule in allowlist):
            defects.append(Defect(OUTSIDE_ALLOWLIST, quote(path), ""))
        hit = next((rule for rule in guarded if rule.covers(path, case_insensitive, True)), None)
        if hit is not None:
            defects.append(Defect(PROTECTED_PATH_TOUCHED, quote(path), f"covered by {quote(hit.entry)}"))
    return defects


def parse_name_status(data: bytes) -> list[str]:
    """Changed paths from `git diff --name-status -z` output; a rename or copy yields both sides."""
    tokens = data.split(b"\0")
    if tokens and tokens[-1] == b"":
        tokens.pop()
    paths: list[str] = []
    index = 0
    while index < len(tokens):
        status = tokens[index].decode("utf-8", errors="replace")
        width = 2 if status[:1] in ("R", "C") else 1
        if not status or index + width >= len(tokens):
            raise ToolFault(f"git printed a name-status record that cannot be read: {quote(status)}")
        for raw in tokens[index + 1:index + 1 + width]:
            path = raw.decode("utf-8", errors="surrogateescape")
            if path not in paths:
                paths.append(path)
        index += 1 + width
    return paths


def _git_environment() -> dict[str, str]:
    """The environment of a git child: nothing that selects other history or settings."""
    removed = frozenset(GIT_SELECTORS)
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() not in removed and not name.upper().startswith(GIT_SCRUBBED_PREFIX)
    }
    environment.update(GIT_FORCED)
    return environment


def run_git(repo: str, args: Sequence[str], stdin: bytes = b"", options: Sequence[str] = ()) -> bytes:
    """Run git inside `repo` and return stdout; any failure is a ToolFault carrying git's stderr."""
    command = ["git", "--no-replace-objects", "-c", "core.quotepath=false", "-C", repo, *options, *args]
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            env=_git_environment(),
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        reason = exc.strerror if isinstance(exc, OSError) and exc.strerror else type(exc).__name__
        raise ToolFault(f"git cannot be run: {quote(reason)}") from None
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        # git's text is input: quoted, so a message of many lines is still one line here.
        raise ToolFault(f"git {args[0]} failed with exit {completed.returncode}: {quote(message)}")
    return completed.stdout


def _git_text(repo: str, args: Sequence[str]) -> str:
    return run_git(repo, args).decode("utf-8", errors="replace").strip()


def require_repository_top(repo: str) -> None:
    """The directory must be a repository (a bare one, or the top level of a work tree)."""
    if _git_text(repo, ["rev-parse", "--is-bare-repository"]) == "true":
        return
    top = _git_text(repo, ["rev-parse", "--show-toplevel"])
    try:
        same = os.path.samefile(top, repo)
    except OSError as exc:
        raise ToolFault(f"cannot compare {quote(repo)} with {quote(top)}: {quote(exc.strerror or type(exc).__name__)}") from None
    if not same:
        raise ToolFault(f"{quote(repo)} is not the top level of a repository (it is inside {quote(top)})")


def _object_id(text: str, what: str) -> str:
    if OBJECT_ID.fullmatch(text) is None:
        raise ToolFault(f"git gave {what} that is not an object id: {quote(text)}")
    return text


def parse_commit(oid: str, body: bytes) -> RawCommit:
    """The tree and the parents of a raw commit object, read as git itself reads them.

    The header lines are the ones before the first blank line: `tree` comes first and the
    `parent` lines follow it directly; every other header is not read.
    """
    lines = body.split(b"\n\n", 1)[0].split(b"\n")
    width = len(oid)

    def field(line: bytes, key: bytes) -> str:
        value = line[len(key):].decode("ascii", errors="replace")
        if not line.startswith(key) or len(value) != width or OBJECT_ID.fullmatch(value) is None:
            shown = quote(line.decode("utf-8", errors="replace"))
            raise ToolFault(f"the commit {quote(oid)} has a header line that cannot be read: {shown}")
        return value

    tree = field(lines[0], b"tree ")
    parents: list[str] = []
    for line in lines[1:]:
        if not line.startswith(b"parent "):
            break
        parents.append(field(line, b"parent "))
    return RawCommit(tree=tree, parents=tuple(parents))


def read_commit(repo: str, oid: str) -> RawCommit:
    """Read the commit object `oid` raw from the object store (replace refs off)."""
    data = run_git(repo, ["cat-file", "--batch"], stdin=(oid + "\n").encode("ascii"))
    end = data.find(b"\n")
    header = data[:end].decode("ascii", errors="replace").split(" ") if end >= 0 else []
    if len(header) == 2 and header[0] == oid and header[1] == "missing":
        raise ToolFault(f"the object {quote(oid)} cannot be read from the object store{_shallow_hint(repo)}")
    if len(header) != 3 or header[0] != oid or header[1] != "commit" or not header[2].isdigit():
        shown = data[: max(end, 0)].decode("utf-8", errors="replace")
        raise ToolFault(f"git printed an object header that is not that of the commit {quote(oid)}: {quote(shown)}")
    size = int(header[2])
    body = data[end + 1:end + 1 + size]
    if len(body) != size or data[end + 1 + size:] != b"\n":
        raise ToolFault(f"git printed a body of the commit {quote(oid)} that is not {size} bytes")
    return parse_commit(oid, body)


def _shallow_hint(repo: str) -> str:
    """A reason to add to a missing object: a shallow repository lacks the parents of its boundary."""
    try:
        shallow = _git_text(repo, ["rev-parse", "--is-shallow-repository"]) == "true"
    except ToolFault:
        return ""
    return " (the repository is shallow)" if shallow else ""


def changed_paths(repo: str, commit: str, reds: list[Defect]) -> list[str]:
    """The changed paths of `commit` against its first parent.

    The parents and the trees come from the raw commit objects, so no graft, replace ref
    or shallow file can change them. A merge or a root commit adds its red to `reds`
    before the first parent is read, so the red stands even when that read fails.
    """
    sha = _object_id(_git_text(repo, ["rev-parse", "--verify", f"{commit}^{{commit}}"]), "the commit id")
    repair = read_commit(repo, sha)
    if len(repair.parents) != 1:
        kind = "a root commit" if not repair.parents else f"a merge commit with {len(repair.parents)} parents"
        reds.append(Defect(REPAIR_NOT_SINGLE_PARENT, quote(commit), f"the repair is {kind}"))
    if repair.parents:
        base = read_commit(repo, repair.parents[0]).tree
    else:
        base = _git_text_stdin(repo, ["hash-object", "-t", "tree", "--stdin"])
    data = run_git(repo, ["diff", *DIFF_FLAGS, base, repair.tree], options=DIFF_OPTIONS)
    return parse_name_status(data)


def _git_text_stdin(repo: str, args: Sequence[str]) -> str:
    return run_git(repo, args, stdin=b"").decode("utf-8", errors="replace").strip()


class OutputFault(Exception):
    """Standard output or standard error cannot be written: exit 2."""


def _harden_streams() -> None:
    """Keep the host's encoding but never let an unencodable character raise on output."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (OSError, ValueError):
                pass


def _emit(stream: TextIO | None, text: str) -> None:
    """Write `text` and flush it now, so a stream that cannot take it fails here and not at exit."""
    if stream is None:
        raise OutputFault("the stream is closed")
    try:
        stream.write(text)
        stream.flush()
    except (OSError, ValueError) as exc:
        raise OutputFault(type(exc).__name__) from None


def _usage_error(message: str | None = None) -> int:
    text = USAGE + "\n"
    if message:
        text += f"repair_guard.py: error: {message}\n"
    _emit(sys.stderr, text)
    return EXIT_USAGE


def parse_arguments(args: Sequence[str]) -> Arguments:
    """Read the three options; raise UsageError for anything else."""
    names = ("--repo", "--repair", "--dispatch")
    given: dict[str, str] = {}
    index = 0
    while index < len(args):
        arg = args[index]
        if arg not in names:
            if arg.startswith("-"):
                raise UsageError(f"unknown option {quote(arg)}")
            raise UsageError(f"unexpected argument {quote(arg)}")
        if arg in given:
            raise UsageError(f"{arg} is given twice")
        if index + 1 >= len(args):
            raise UsageError(f"{arg} needs a value")
        value = args[index + 1]
        problem = bad_character(value)
        if problem is not None:
            raise UsageError(f"the value of {arg} holds {problem}")
        if not value.strip():
            raise UsageError(f"the value of {arg} must not be empty")
        if arg == "--repair" and value.startswith("-"):
            raise UsageError(f"the value of --repair must be a commit, got {quote(value)}")
        if arg == "--repair" and any(mark in value for mark in ANCESTRY_MARKS):
            raise UsageError(f"the value of --repair must name a commit by id or reference, got {quote(value)}")
        given[arg] = value
        index += 2
    for name in names:
        if name not in given:
            raise UsageError(f"{name} is required")
    return Arguments(repo=given["--repo"], repair=given["--repair"], dispatch=given["--dispatch"])


def read_dispatch(path: str) -> str:
    """The dispatch text: UTF-8 with surrogate escapes, so an undecodable byte is never a fault."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        raise ToolFault(f"cannot read {quote(path)}: {quote(exc.strerror or type(exc).__name__)}") from None
    return raw.decode("utf-8-sig", errors="surrogateescape")


def inspect_repair(arguments: Arguments, rules: DispatchRules, reds: list[Defect]) -> int:
    """Check the repair commit; every red found is added to `reds` before any fault is raised.

    Returns the number of distinct changed paths.
    """
    require_repository_top(arguments.repo)
    paths = changed_paths(arguments.repo, arguments.repair, reds)
    judge_rules = not rules.text_defects
    reds.extend(check_paths(paths, rules.allowlist, rules.protected, sys.platform == "win32", judge_rules))
    return len(paths)


def run(arguments: Arguments) -> int:
    text = read_dispatch(arguments.dispatch)
    rules = parse_dispatch(text)
    reds: list[Defect] = list(rules.text_defects)
    fault: str | None = None
    count = 0
    try:
        count = inspect_repair(arguments, rules, reds)
    except ToolFault as exc:
        fault = str(exc)
    except Exception as exc:  # noqa: BLE001 - any unexpected error is a tool fault, never a traceback
        fault = f"{quote(type(exc).__name__)}: {quote(str(exc))}"
    if reds:
        _emit(sys.stdout, "".join(defect.line() + "\n" for defect in reds))
        if fault is not None:
            # Every red reached standard output; a standard error that fails now loses only the fault.
            try:
                _emit(sys.stderr, f"repair_guard.py: tool fault: {fault}\n")
            except OutputFault:
                pass
        return EXIT_RED
    if fault is not None:
        _emit(sys.stderr, f"repair_guard.py: tool fault: {fault}\n")
        return EXIT_FAULT
    _emit(sys.stdout, f"paths={count} defects=0\n")
    return EXIT_PASS


def main(argv: Sequence[str] | None = None) -> int:
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        try:
            arguments = parse_arguments(args)
        except UsageError as exc:
            return _usage_error(str(exc))
        try:
            return run(arguments)
        except UsageError as exc:
            return _usage_error(str(exc))
        except ToolFault as exc:
            _emit(sys.stderr, f"repair_guard.py: tool fault: {exc}\n")
            return EXIT_FAULT
    except OutputFault:
        return EXIT_FAULT


def _release_broken_streams() -> None:
    """Point a stream that cannot be written at the null device, so the exit flush cannot fail.

    Python turns a failed flush at interpreter exit into exit status 120, which would
    replace the exit 2 this script has already decided on.
    """
    for number, stream in ((1, sys.stdout), (2, sys.stderr)):
        try:
            if stream is None:
                raise ValueError("closed")
            stream.flush()
        except (OSError, ValueError):
            try:
                descriptor = os.open(os.devnull, os.O_WRONLY)
                os.dup2(descriptor, number)
                os.close(descriptor)
            except OSError:
                pass


if __name__ == "__main__":
    code = main()
    _release_broken_streams()
    sys.exit(code)
