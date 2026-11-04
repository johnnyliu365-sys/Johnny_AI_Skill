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

History is read from raw objects and every object is hashed by this script. The repair
commit is resolved to its object id, then it, its first parent, both root trees and every
subtree the walk descends into are read raw through `git cat-file --batch` (the ids on
standard input, replace refs off) and hashed here: the header `<type> <size>`, a NUL byte
and the body, with SHA-1 or SHA-256 chosen by the width of the object ids. An object whose
hash differs from the id it was asked for, whose type is not the expected one, or that the
store cannot serve is a fault naming that id, so a forged loose object, an object served
through alternates or a damaged store never decides a verdict. The `tree` line and the
`parent` lines come from the verified commit, so a graft file, a replace ref, a shallow
file or a commit-graph cannot change which parent or which trees are compared. A merge is
recognised from its parent lines; a root commit is compared against the empty tree, which
needs no object; a first parent the object store cannot serve is a fault.

The changed paths come from this script's own walk of the two root trees, never from
`git diff`: the trees are compared entry by entry, a subtree is read only when its two ids
differ, and every path whose entry differs in id or in mode, or exists on one side only, is
reported (a whole subtree that exists on one side only is listed file by file; a type
change reports the path and what lay under it). Submodule pointers (gitlinks, mode 160000)
are compared by id and never descended, so they always count. Added, modified, deleted and
type-changed paths all count, and a rename is a deletion and an addition, so it counts on
both sides. No diff machinery, configuration, attribute or external driver is involved.
The revision given to `--repair` names a commit by id or by reference; a name that uses an
ancestry or path operator is a usage error, because git would answer it through the
history that grafts rewrite.

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

A dispatch block that holds a text defect is a red by itself and its entries cannot be
trusted, so none of that block's entries is used: a defective allowlist is not judged (no
path is called outside it) and a defective protected list protects nothing but the gate
scripts. The other block is clean and its entries are used as usual. Every rule that needs
no entry still applies: the text values of the changed paths, the single-parent rule and
the protection of the gate scripts, so a change to a gate script is reported next to the
text red. git is still asked, so any fault is reported too.

The dispatch file is decoded as UTF-8 with surrogate escapes, so no byte sequence makes it
unreadable. One UTF-8 byte order mark at the very start of the file is removed first, as in
the other gates; any other U+FEFF stays text. An undecodable byte or a raw control character on a block line (inside or
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
with the fault printed on standard error. It exits 2 only when it found no red. The paths
are judged level by level while the tree walk goes down: as soon as the trees of a level
have been verified, the paths they give are judged, before any deeper tree is read. A red
at a level that did verify is therefore reported beside a fault met deeper (or beside a
tree of the same level that did not verify), and a path of a tree that did not verify is
never judged. The one
exception is standard output that cannot be written: then no verdict can be delivered and
the exit is 2 whatever was found. A standard error that cannot be written decides the exit
only when there is nothing else to deliver: when every red line reached standard output
the exit is still 1.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
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
# Width in bytes of a raw object id in a tree, by the width in hex digits of the repository's ids.
RAW_ID_WIDTH = {40: 20, 64: 32}
MODE_TYPE_MASK = 0o170000
MODE_TREE = 0o040000
MODE_OCTAL = re.compile(r"[0-7]{1,7}")
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
class TreeEntry:
    """One entry of a raw tree object: its mode text and the id of what it names."""

    mode: str
    oid: str

    @property
    def is_tree(self) -> bool:
        return int(self.mode, 8) & MODE_TYPE_MASK == MODE_TREE


@dataclass(frozen=True)
class DispatchRules:
    """The entries of each block; a block that holds a text defect has none and is flagged."""

    allowlist: tuple[PathRule, ...]
    protected: tuple[PathRule, ...]
    text_defects: tuple[Defect, ...]
    allowlist_defective: bool = False
    protected_defective: bool = False


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
) -> tuple[tuple[PathRule, ...], bool]:
    """The entries of one block line and whether the block holds a text defect.

    A defective block yields no entries at all: they cannot be trusted. Its structure is
    still checked, so a usage error outranks the text red.
    """
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
    defective = bad is not None
    for position, element in enumerate(value, 1):
        where = f"line {number}, {key} entry {position}"
        if not isinstance(element, str):
            raise UsageError(f"{where}: an entry must be a JSON string")
        problem = bad_character(element)
        if problem is not None:
            if bad is None:
                text_defects.append(Defect(TEXT_VALUE_INVALID, quote(element), f"{where} holds {problem}"))
            defective = True
            continue
        rules.append(make_rule(element, where))
    return (() if defective else tuple(rules)), defective


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
    allowlist, allow_bad = _parse_line(lines, ALLOW_KEY, text_defects)
    protected, protect_bad = _parse_line(lines, PROTECT_KEY, text_defects)
    return DispatchRules(
        allowlist=allowlist,
        protected=protected,
        text_defects=tuple(text_defects),
        allowlist_defective=allow_bad,
        protected_defective=protect_bad,
    )


def check_paths(
    paths: Sequence[str],
    allowlist: Sequence[PathRule],
    protected: Sequence[PathRule],
    case_insensitive: bool,
    judge_allowlist: bool = True,
    judge_protected: bool = True,
) -> list[Defect]:
    """Defects of the changed `paths` against the rules; the gate directory is always protected.

    With `judge_allowlist` False the allowlist came from a block that holds a text defect,
    so no path can be called outside it; with `judge_protected` False the protected entries
    did, so they are not used. What needs no entry still applies: the text values of the
    paths and the protection of the gate directory.
    """
    gate = PathRule(GATE_DIRECTORY, True)
    guarded = (*protected, gate) if judge_protected else (gate,)
    defects: list[Defect] = []
    for path in paths:
        problem = bad_character(path)
        if problem is not None:
            defects.append(Defect(TEXT_VALUE_INVALID, quote(path), f"a changed path holds {problem}"))
        if judge_allowlist and not any(rule.covers(path, case_insensitive, False) for rule in allowlist):
            defects.append(Defect(OUTSIDE_ALLOWLIST, quote(path), ""))
        hit = next((rule for rule in guarded if rule.covers(path, case_insensitive, True)), None)
        if hit is not None:
            defects.append(Defect(PROTECTED_PATH_TOUCHED, quote(path), f"covered by {quote(hit.entry)}"))
    return defects


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


def object_hash(kind: str, body: bytes, width: int) -> str:
    """The id git gives an object: the hash of `<type> <size>`, a NUL byte and the body."""
    if width == 40:
        digest = hashlib.sha1(usedforsecurity=False)
    elif width == 64:
        digest = hashlib.sha256()
    else:
        raise ToolFault(f"an object id of {width} digits is neither SHA-1 nor SHA-256")
    digest.update(f"{kind} {len(body)}".encode("ascii") + b"\0" + body)
    return digest.hexdigest()


def read_objects(repo: str, ids: Sequence[str], kind: str) -> dict[str, bytes]:
    """Read the objects `ids` raw from the store and verify every one by hashing it here.

    All ids go to one `git cat-file --batch` on standard input (replace refs off). Each
    answer must name the id asked for, be of type `kind`, have the size its header says
    and hash to the id; anything else, and a missing object, is a ToolFault naming the id.
    Nothing git inferred is used: only the bytes of the object and what they hash to.
    """
    wanted = list(dict.fromkeys(ids))
    for oid in wanted:
        if OBJECT_ID.fullmatch(oid) is None:
            raise ToolFault(f"an object id was expected, got {quote(oid)}")
    if not wanted:
        return {}
    data = run_git(repo, ["cat-file", "--batch"], stdin=("\n".join(wanted) + "\n").encode("ascii"))
    found: dict[str, bytes] = {}
    position = 0
    for oid in wanted:
        end = data.find(b"\n", position)
        header = data[position:end].decode("ascii", errors="replace").split(" ") if end >= 0 else []
        if len(header) == 2 and header[0] == oid and header[1] == "missing":
            raise ToolFault(f"the object {quote(oid)} cannot be read from the object store{_shallow_hint(repo)}")
        if len(header) != 3 or header[0] != oid or not header[2].isdigit():
            shown = data[position:max(end, position)].decode("utf-8", errors="replace")
            raise ToolFault(f"git printed an object header that is not that of the object {quote(oid)}: {quote(shown)}")
        if header[1] != kind:
            raise ToolFault(f"the object {quote(oid)} is a {quote(header[1])}, not a {kind}")
        size = int(header[2])
        body = data[end + 1:end + 1 + size]
        if len(body) != size or data[end + 1 + size:end + 2 + size] != b"\n":
            raise ToolFault(f"git printed a body of the object {quote(oid)} that is not {size} bytes")
        if object_hash(kind, body, len(oid)) != oid:
            raise ToolFault(f"the object {quote(oid)} does not hash to its id: the store served forged or damaged content")
        found[oid] = body
        position = end + 2 + size
    if position != len(data):
        raise ToolFault("git printed more than the objects that were asked for")
    return found


def read_commit(repo: str, oid: str) -> RawCommit:
    """Read the commit object `oid` raw from the object store and verify it by its hash."""
    return parse_commit(oid, read_objects(repo, [oid], "commit")[oid])


def _shallow_hint(repo: str) -> str:
    """A reason to add to a missing object: a shallow repository lacks the parents of its boundary."""
    try:
        shallow = _git_text(repo, ["rev-parse", "--is-shallow-repository"]) == "true"
    except ToolFault:
        return ""
    return " (the repository is shallow)" if shallow else ""


def parse_tree(oid: str, body: bytes) -> dict[bytes, TreeEntry]:
    """The entries of a raw tree object by name; a body that is not a clean tree is a ToolFault.

    An entry is `<octal mode> <name>`, a NUL byte and the raw id of as many bytes as the
    ids of the repository have. The body must be consumed exactly. A name that is empty,
    `.`, `..` or holds a slash, a mode that is not octal, and a name given twice are
    refused, because git never writes them and a path built from them would be wrong.
    """
    raw_width = RAW_ID_WIDTH.get(len(oid))
    if raw_width is None:
        raise ToolFault(f"an object id of {len(oid)} digits is neither SHA-1 nor SHA-256")
    entries: dict[bytes, TreeEntry] = {}
    position = 0
    while position < len(body):
        space = body.find(b" ", position)
        nul = body.find(b"\0", space + 1) if space >= 0 else -1
        if space < 0 or nul < 0 or nul + 1 + raw_width > len(body):
            raise ToolFault(f"the tree {quote(oid)} is malformed at byte {position}")
        mode = body[position:space].decode("ascii", errors="replace")
        name = body[space + 1:nul]
        if MODE_OCTAL.fullmatch(mode) is None:
            raise ToolFault(f"the tree {quote(oid)} has an entry with the mode {quote(mode)}")
        if name in (b"", b".", b"..") or b"/" in name:
            shown = name.decode("utf-8", errors="replace")
            raise ToolFault(f"the tree {quote(oid)} has an entry with the name {quote(shown)}")
        if name in entries:
            shown = name.decode("utf-8", errors="replace")
            raise ToolFault(f"the tree {quote(oid)} names {quote(shown)} twice")
        entries[name] = TreeEntry(mode=mode, oid=body[nul + 1:nul + 1 + raw_width].hex())
        position = nul + 1 + raw_width
    return entries


def _byte_key(text: str) -> bytes:
    """The order paths are listed in: the bytes of their UTF-8 form, whatever the walk order was."""
    return text.encode("utf-8", errors="surrogateescape")


def _read_trees(repo: str, ids: Sequence[str]) -> tuple[dict[str, bytes], ToolFault | None]:
    """The trees `ids` read raw and verified, and the first fault met while reading them.

    The ids go to git together. When anything about them is wrong, each is read again on
    its own, so every tree that verifies is still returned beside the fault that was met:
    the walk can then judge what it did verify before it reports the fault.
    """
    try:
        return read_objects(repo, ids, "tree"), None
    except ToolFault as fault:
        verified: dict[str, bytes] = {}
        for oid in dict.fromkeys(ids):
            try:
                verified.update(read_objects(repo, [oid], "tree"))
            except ToolFault:
                continue
        return verified, fault


def diff_trees(
    repo: str, left: str | None, right: str | None, on_level: Callable[[Sequence[str]], None] | None = None
) -> list[str]:
    """Every path whose entry differs between two root trees, from this script's own walk.

    `left` or `right` None is the empty tree. The trees are compared entry by entry; a
    subtree is read (and hashed) only when the ids of its two sides differ, and the walk
    goes down one level at a time so each level is one read. A path is reported when its
    entry differs in id or mode or exists on one side only; a subtree that exists on one
    side only, or that turns into something else, is listed file by file. A gitlink (mode
    160000) is an entry like a file: compared by id and never descended.

    `on_level` is called with the new paths of a level as soon as the trees that give them
    are verified, before any deeper tree is read, so a verdict on those paths does not wait
    for the rest of the walk. A tree that does not verify or cannot be parsed stops the walk
    after its level has been handed over: the paths of the trees of that level that did
    verify are handed over too, and the first fault is raised.
    """
    paths: list[str] = []
    seen: set[str] = set()
    level: list[tuple[str, str | None, str | None]] = [("", left, right)]
    while level:
        needed = [oid for _, old_id, new_id in level for oid in (old_id, new_id) if oid is not None]
        loaded, fault = _read_trees(repo, needed)
        following: list[tuple[str, str | None, str | None]] = []
        found: list[str] = []
        for prefix, left_id, right_id in level:
            if any(oid is not None and oid not in loaded for oid in (left_id, right_id)):
                continue
            try:
                before = parse_tree(left_id, loaded[left_id]) if left_id is not None else {}
                after = parse_tree(right_id, loaded[right_id]) if right_id is not None else {}
            except ToolFault as malformed:
                fault = fault or malformed
                continue
            for name in sorted(before.keys() | after.keys()):
                old, new = before.get(name), after.get(name)
                if old == new:
                    continue
                path = prefix + name.decode("utf-8", errors="surrogateescape")
                if old is not None and new is not None and old.is_tree and new.is_tree:
                    if old.mode != new.mode:
                        found.append(path)
                    if old.oid != new.oid:
                        following.append((path + "/", old.oid, new.oid))
                    continue
                only_trees = (old is None or old.is_tree) and (new is None or new.is_tree)
                if not only_trees:
                    found.append(path)
                for entry in (old, new):
                    if entry is None or not entry.is_tree:
                        continue
                    if entry.oid == object_hash("tree", b"", len(entry.oid)):
                        # an empty subtree holds no file to list, so the directory itself is the change
                        if only_trees:
                            found.append(path)
                    elif entry is old:
                        following.append((path + "/", entry.oid, None))
                    else:
                        following.append((path + "/", None, entry.oid))
        fresh = sorted((path for path in dict.fromkeys(found) if path not in seen), key=_byte_key)
        seen.update(fresh)
        paths.extend(fresh)
        if on_level is not None and fresh:
            on_level(fresh)
        if fault is not None:
            raise fault
        level = following
    return sorted(paths, key=_byte_key)


def changed_paths(
    repo: str, commit: str, reds: list[Defect], on_level: Callable[[Sequence[str]], None] | None = None
) -> list[str]:
    """The changed paths of `commit` against its first parent.

    `on_level` is handed the paths of each level of the tree walk as that level is verified.

    The commit, its first parent and every tree used are read raw and hashed here, so no
    graft, replace ref, shallow file, commit-graph or forged object can change what is
    compared. A merge or a root commit adds its red to `reds` before the first parent is
    read, so the red stands even when that read fails.
    """
    sha = _object_id(_git_text(repo, ["rev-parse", "--verify", f"{commit}^{{commit}}"]), "the commit id")
    repair = read_commit(repo, sha)
    if len(repair.parents) != 1:
        kind = "a root commit" if not repair.parents else f"a merge commit with {len(repair.parents)} parents"
        reds.append(Defect(REPAIR_NOT_SINGLE_PARENT, quote(commit), f"the repair is {kind}"))
    base = read_commit(repo, repair.parents[0]).tree if repair.parents else None
    if base == repair.tree:
        return []
    return diff_trees(repo, base, repair.tree, on_level)


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

    The paths are judged level by level as the walk verifies each tree, so a red at a level
    that did verify stands beside a fault met deeper. The reds of the paths are added in the
    byte order of the paths, whichever level they were found at. Returns the number of
    distinct changed paths.
    """
    require_repository_top(arguments.repo)
    judged: dict[str, list[Defect]] = {}

    def judge(level_paths: Sequence[str]) -> None:
        for path in level_paths:
            if path not in judged:
                judged[path] = check_paths(
                    [path],
                    rules.allowlist,
                    rules.protected,
                    sys.platform == "win32",
                    not rules.allowlist_defective,
                    not rules.protected_defective,
                )

    try:
        paths = changed_paths(arguments.repo, arguments.repair, reds, judge)
        judge(paths)
    finally:
        reds.extend(defect for path in sorted(judged, key=_byte_key) for defect in judged[path])
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
