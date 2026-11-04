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

The changed paths of the repair commit are read from `git diff --name-status -M -z`
against its first parent, with quoting off. Added, modified, deleted, type-changed and
renamed paths all count, and a rename counts on both its old and its new side. A root
commit is compared against the empty tree.

Matching is by path segment, never by character prefix: the directory entry `d/` covers
`d/x` and does not cover `d2/x` or a path named exactly `d`. Entries are compared exactly;
nothing is decoded or Unicode-normalised. On Windows entries and paths are compared
case-insensitively (the file system folds case); elsewhere case matters.

Defect codes (one output line each, exit 1):

    OUTSIDE_ALLOWLIST        a changed path is covered by no allowlist entry
    PROTECTED_PATH_TOUCHED   a changed path is covered by a protected entry or a gate script
    REPAIR_NOT_SINGLE_PARENT the repair commit is a merge or a root commit
    TEXT_VALUE_INVALID       a string read from the dispatch file or from git holds a lone
                             surrogate or a control character (U+0000-U+001F, U+007F)

Every printed subject is escaped with Python `repr`, so one defect is always one line. On
exit 0 the only output is `paths=N defects=0`, where N counts the distinct changed paths.

Exit codes: 0 pass, 1 contract red (at least one defect), 2 tool fault (git cannot serve
the check, the repository is not a repository top level, the dispatch file cannot be
read, an unexpected error), 3 usage error (bad arguments, a dispatch without both lines,
a line that is not one JSON array of strings, a null value, an empty entry, an entry that
is absolute, uses a backslash or holds an empty, `.` or `..` segment). A red never exits 2
and a fault never exits 1. A text-value defect is a red (exit 1) in a file or in git
output and a usage error (exit 3) in an argument.
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
DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
# Environment variables that would point git at some other repository than --repo.
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
)


class UsageError(Exception):
    """The arguments or the dispatch lines are wrong: exit 3."""


class ToolFault(Exception):
    """git or the file system cannot serve the check: exit 2."""


@dataclass(frozen=True)
class PathRule:
    """One allowlist or protected entry: an exact path, or a directory when it ends in `/`."""

    entry: str
    is_directory: bool

    def covers(self, path: str, case_insensitive: bool) -> bool:
        entry, subject = self.entry, path
        if case_insensitive:
            entry, subject = entry.casefold(), subject.casefold()
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
class DispatchRules:
    allowlist: tuple[PathRule, ...]
    protected: tuple[PathRule, ...]
    text_defects: tuple[Defect, ...]


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
    try:
        value: object = json.loads(raw)
    except (ValueError, RecursionError):
        raise UsageError(f"line {number}: the value of {key} is not one JSON value") from None
    if not isinstance(value, list):
        raise UsageError(f"line {number}: {key} must be a JSON array of strings")
    rules: list[PathRule] = []
    for position, element in enumerate(value, 1):
        where = f"line {number}, {key} entry {position}"
        if not isinstance(element, str):
            raise UsageError(f"{where}: an entry must be a JSON string")
        problem = bad_character(element)
        if problem is not None:
            text_defects.append(Defect(TEXT_VALUE_INVALID, quote(element), f"{where} holds {problem}"))
            continue
        rules.append(make_rule(element, where))
    return tuple(rules)


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
) -> list[Defect]:
    """Defects of the changed `paths` against the rules; the gate directory is always protected."""
    guarded = (*protected, PathRule(GATE_DIRECTORY, True))
    defects: list[Defect] = []
    for path in paths:
        problem = bad_character(path)
        if problem is not None:
            defects.append(Defect(TEXT_VALUE_INVALID, quote(path), f"a changed path holds {problem}"))
        if not any(rule.covers(path, case_insensitive) for rule in allowlist):
            defects.append(Defect(OUTSIDE_ALLOWLIST, quote(path), ""))
        hit = next((rule for rule in guarded if rule.covers(path, case_insensitive)), None)
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
    environment = dict(os.environ)
    for name in GIT_SELECTORS:
        environment.pop(name, None)
    return environment


def run_git(repo: str, args: Sequence[str], stdin: bytes = b"") -> bytes:
    """Run git inside `repo` and return stdout; any failure is a ToolFault carrying git's stderr."""
    command = ["git", "--no-replace-objects", "-c", "core.quotepath=false", "-C", repo, *args]
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


def changed_paths(repo: str, commit: str) -> tuple[list[str], int]:
    """The changed paths of `commit` against its first parent, and its parent count."""
    sha = _git_text(repo, ["rev-parse", "--verify", f"{commit}^{{commit}}"])
    parents = _git_text(repo, ["rev-list", "--parents", "-n", "1", sha]).split()[1:]
    if not parents and _git_text(repo, ["rev-parse", "--is-shallow-repository"]) == "true":
        raise ToolFault("the repository is shallow: a root commit cannot be told from the shallow boundary")
    if parents:
        base = parents[0]
    else:
        base = _git_text_stdin(repo, ["hash-object", "-t", "tree", "--stdin"])
    data = run_git(repo, ["diff", "--name-status", "-M", "-z", base, sha])
    return parse_name_status(data), len(parents)


def _git_text_stdin(repo: str, args: Sequence[str]) -> str:
    return run_git(repo, args, stdin=b"").decode("utf-8", errors="replace").strip()


def _harden_streams() -> None:
    """Keep the host's encoding but never let an unencodable character raise on output."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (OSError, ValueError):
                pass


def _usage_error(message: str | None = None) -> int:
    print(USAGE, file=sys.stderr)
    if message:
        print(f"repair_guard.py: error: {message}", file=sys.stderr)
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
        given[arg] = value
        index += 2
    for name in names:
        if name not in given:
            raise UsageError(f"{name} is required")
    return Arguments(repo=given["--repo"], repair=given["--repair"], dispatch=given["--dispatch"])


def main(argv: Sequence[str] | None = None) -> int:
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        arguments = parse_arguments(args)
    except UsageError as exc:
        return _usage_error(str(exc))
    try:
        with open(arguments.dispatch, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        print(
            f"repair_guard.py: tool fault: cannot read {quote(arguments.dispatch)}: {quote(exc.strerror or type(exc).__name__)}",
            file=sys.stderr,
        )
        return EXIT_FAULT
    try:
        text = raw.decode("utf-8-sig", errors="surrogatepass")
    except UnicodeDecodeError:
        return _usage_error(f"{quote(arguments.dispatch)} is not UTF-8 text")
    try:
        rules = parse_dispatch(text)
    except UsageError as exc:
        return _usage_error(str(exc))
    if rules.text_defects:
        for defect in rules.text_defects:
            print(defect.line())
        return EXIT_RED
    try:
        require_repository_top(arguments.repo)
        paths, parent_count = changed_paths(arguments.repo, arguments.repair)
        defects: list[Defect] = []
        if parent_count != 1:
            kind = "a root commit" if parent_count == 0 else f"a merge commit with {parent_count} parents"
            defects.append(Defect(REPAIR_NOT_SINGLE_PARENT, quote(arguments.repair), f"the repair is {kind}"))
        defects.extend(check_paths(paths, rules.allowlist, rules.protected, sys.platform == "win32"))
    except ToolFault as exc:
        print(f"repair_guard.py: tool fault: {exc}", file=sys.stderr)
        return EXIT_FAULT
    except Exception as exc:  # noqa: BLE001 - any unexpected error is a tool fault, never a red and never a traceback
        print(f"repair_guard.py: tool fault: {quote(type(exc).__name__)}: {quote(str(exc))}", file=sys.stderr)
        return EXIT_FAULT
    if defects:
        for defect in defects:
            print(defect.line())
        return EXIT_RED
    print(f"paths={len(paths)} defects=0")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
