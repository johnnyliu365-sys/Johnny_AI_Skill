#!/usr/bin/env python3
"""Contract gate: every requirement has a spec, every spec is bound and honest.

Usage: contract_gate.py --repo <dir> --snapshot <snapshot.json> --specs <dir>

The snapshot is a requirement snapshot file (a JSON object with a `rows` list; a row
has `requirement_id`, 1 to 128 characters from letters, digits, dot, underscore, colon,
hyphen and slash, and `status`, `active` or `retired`; a key repeated in any object makes
the file not a snapshot). `--repo` must be the top level of a git work tree. The specs are
every file named `test_*.py` (case-sensitive) under `--specs`, which must lie inside
`--repo`; links and junctions under it are not followed. A spec declares its contract in
its first comment block, the leading run of lines that start with `#`:

    # requirement: <id>                          one or more
    # source: <repository path> sha256:<hex>    one or more
    # mutation: <name>                           one or more

Only these three lower-case keys are declarations; every other comment line is free text.
Of a declared value only the spaces and tabs around it are removed; a value that holds a
control character is a red with the code of its key.

A spec is decoded the way Python decodes source (its coding declaration or UTF-8, a byte
order mark honoured) and the decoded text is what is parsed, analysed and quoted. Everything
derived from a spec's bytes runs inside one per-spec guard: whatever exception it raises, it
is a red of that spec. Only reading a file from disk and running git are faults.

A declared source path must be canonical (not empty, at most 1024 bytes, no control
character, only a forward slash as separator once backslashes are normalised and one
leading dot-slash is dropped, no leading slash or colon, no drive letter, no empty, dot or
dot-dot segment). `HEAD` is resolved once, at the start of the run, to a full commit id; every
lookup of the run is a line on the standard input of one `git cat-file --batch` process, a full
object id, so a declared source is never a pathspec, never an object name and never on a command
line, a commit that lands during the run changes nothing in it, and the digest does not depend
on the host's line-ending settings. The commit is read, its `tree` line names the root tree, and
the trees are walked from the root by object id; the entry of a source is read from its parent
tree: a path the tree does not name, or names as a directory, is SOURCE_MISSING; so is an entry
that is a symbolic link or a submodule (a contract cites the content of a file, never a link).
An object a tree names but the object store cannot serve (pruned, or missing from a partial
clone; nothing is fetched) is a fault, never a red.

Every object the gate reads is hashed by the gate against the id it asked for: the header
`<type> <size>`, a NUL byte and the body, with SHA-1 or SHA-256 chosen by the width of the id.
An object that does not hash to its id (a forged or damaged loose object, an object served
through alternates) is a fault naming the id, never a red and never a pass, and the object store
is not used again in the run. Every git child ignores replace refs, never fetches lazily and
runs without the variables that select a repository, a work tree or a configuration.

Defect codes (exit 1, one line `<code> <spec or requirement>: <detail>` each, subject and
detail escaped so that one defect is always one line):
  NO_SPEC_FOR_REQUIREMENT, SOURCE_MISSING, SOURCE_DIGEST_MISMATCH,
  RETIRED_REQUIREMENT_BOUND, LITERAL_EXPECTED, NO_MUTATION.

Red before fault: the gate reports every red it can find and exits 1 if there is one, with each
fault (SOURCE_UNSERVABLE for a URL source or an unservable object, TOOL_FAULT for the rest) on
stderr on one line, then the summary. It exits 2 only when it found no red. A spec that cannot be
read may declare any requirement, so no requirement is then called unbound. After git fails the
lookups that remain are skipped (one fault line) and everything that needs none is still checked.

Exit codes: 0 pass, 1 contract red, 2 tool fault and no red (a file cannot be read, git cannot
serve a query, `--repo` is not a work tree top level, or a source is a URL, which cannot be
checked offline), 3 usage error (bad arguments, or the snapshot argument is not a snapshot; the
usage banner and one escaped error line are printed). A fault that leaves nothing to check (the
snapshot, `--repo`, `--specs`) ends the run at once. A red is never reported as a tool fault and a
tool fault is never reported as a red. The summary line goes to stdout at exit 0 and to stderr at
exit 1. The console encoding never changes an exit code: stdout and stderr keep the host encoding
but escape what it cannot encode. Fault and usage messages are escaped to one line as well.
"""
from __future__ import annotations

import ast
import fnmatch
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import threading
import tokenize
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypeVar

USAGE = "usage: contract_gate.py --repo <dir> --snapshot <snapshot.json> --specs <dir>"

NO_SPEC_FOR_REQUIREMENT = "NO_SPEC_FOR_REQUIREMENT"
SOURCE_MISSING = "SOURCE_MISSING"
SOURCE_DIGEST_MISMATCH = "SOURCE_DIGEST_MISMATCH"
RETIRED_REQUIREMENT_BOUND = "RETIRED_REQUIREMENT_BOUND"
LITERAL_EXPECTED = "LITERAL_EXPECTED"
NO_MUTATION = "NO_MUTATION"
SOURCE_UNSERVABLE = "SOURCE_UNSERVABLE"

STATUS_ACTIVE = "active"
STATUS_RETIRED = "retired"
SPEC_PATTERN = "test_*.py"
OPTIONS: tuple[str, ...] = ("--repo", "--snapshot", "--specs")
BLANKS = " \t"

DECLARATION = re.compile(r"#[ \t]*(requirement|source|mutation)[ \t]*:(.*)$")
REQUIREMENT_ID = re.compile(r"[A-Za-z0-9._:/-]{1,128}")
SOURCE_VALUE = re.compile(r"^(?:(?P<path>.*[^ \t])[ \t]+)?sha256:(?P<digest>[^ \t]*)$", re.DOTALL)
DIGEST = re.compile(r"^[0-9a-f]{64}$")
DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
LINE_BREAK = re.compile(r"\r\n|\r|\n")
CONTROL_TEXT = re.compile("[\\x00-\\x1f\\x7f\\ud800-\\udfff]")
OBJECT_ID = re.compile(rb"[0-9a-f]{40}|[0-9a-f]{64}")
OBJECT_HEADER = re.compile(rb"([0-9a-f]{40}|[0-9a-f]{64}) (blob|tree|commit|tag) ([0-9]+)")
TREE_MODE = re.compile(rb"[0-7]{1,7}")

DETAIL_LIMIT = 120
ANALYSIS_DEPTH = 64
SOURCE_PATH_LIMIT = 1024
GIT_TIMEOUT_SECONDS = 60
DIGEST_BLOCK = 1 << 20
# Variables that make git work on another repository, work tree or object store than the one
# named by `--repo`; none of them reaches a git child.
GIT_SELECTING_VARIABLES: tuple[str, ...] = (
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
# The GIT_CONFIG variables (GIT_CONFIG, GIT_CONFIG_GLOBAL, GIT_CONFIG_COUNT and the like) are removed too.
# Reparse tags of a symbolic link and of a mount point (a junction) on Windows.
LINK_REPARSE_TAGS: tuple[int, ...] = (0xA000000C, 0xA0000003)


class UsageError(Exception):
    """The command line, or the snapshot argument, is not acceptable (exit 3)."""


class ToolFault(Exception):
    """The gate cannot be served (exit 2)."""

    def __init__(self, label: str, message: str) -> None:
        super().__init__(message)
        self.label = label
        self.message = message


class Unanalysable(Exception):
    """An assertion nests deeper than the analysis budget."""


class RepeatedKey(ValueError):
    """A JSON object repeats a key."""


def escape_text(text: str) -> str:
    """Keep printable characters and write every other one as a backslash escape.

    Line breaks, control characters, U+2028, NEL and lone surrogates all become escapes,
    so a printed subject or detail cannot span two lines or forge another line.
    """
    return "".join(char if char.isprintable() else repr(char)[1:-1] for char in text)


def _shorten(text: str) -> str:
    return text if len(text) <= DETAIL_LIMIT else text[: DETAIL_LIMIT - 3] + "..."


def _quote(text: str) -> str:
    """`text` as a quoted literal, cut to DETAIL_LIMIT characters, for use inside a message."""
    return _shorten(repr(text))


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    status: str


@dataclass(frozen=True)
class Defect:
    code: str
    subject: str
    detail: str

    def render(self) -> str:
        return f"{self.code} {escape_text(self.subject)}: {escape_text(self.detail)}"


@dataclass(frozen=True)
class SourceLine:
    """A declared source: `canonical` is the path to look up, or None with `problem` saying why not."""

    line: int
    declared: str
    digest: str
    canonical: str | None
    problem: str


@dataclass(frozen=True)
class SpecDeclaration:
    spec: str
    requirements: tuple[tuple[int, str], ...]
    sources: tuple[SourceLine, ...]
    mutation_lines: tuple[tuple[int, str], ...]
    malformed: tuple[Defect, ...]
    url_sources: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class SpecAnalysis:
    """Everything derived from the bytes of one spec; `declaration` is None when it could not be read."""

    declaration: SpecDeclaration | None
    literal_defects: tuple[Defect, ...]


@dataclass(frozen=True)
class Arguments:
    repo: Path
    snapshot: Path
    specs: Path


@dataclass(frozen=True)
class Report:
    requirements: int
    specs: int
    defects: tuple[Defect, ...]
    faults: tuple[ToolFault, ...] = ()


# --------------------------------------------------------------------------- input


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ToolFault("TOOL_FAULT", f"cannot read {path}: {exc}") from exc


def _no_repeated_key(pairs: list[tuple[str, object]]) -> dict[str, object]:
    found: dict[str, object] = {}
    for key, value in pairs:
        if key in found:
            raise RepeatedKey(f"the key {_quote(key)} is repeated in an object")
        found[key] = value
    return found


def parse_snapshot(raw: bytes, origin: str) -> tuple[Requirement, ...]:
    """Validate snapshot bytes into requirements; anything else is a usage error."""

    def refuse(reason: str) -> UsageError:
        return UsageError(f"{origin} is not a snapshot: {reason}")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise refuse(f"not UTF-8 ({exc.reason})") from exc
    try:
        data: object = json.loads(text, object_pairs_hook=_no_repeated_key)
    except RepeatedKey as exc:
        raise refuse(str(exc)) from exc
    except (ValueError, RecursionError) as exc:
        raise refuse(f"not JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise refuse("the top level is not a JSON object")
    rows: object = data.get("rows")
    if not isinstance(rows, list):
        raise refuse("no `rows` list")
    found: list[Requirement] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise refuse(f"row {index} is not an object")
        identifier: object = row.get("requirement_id")
        status: object = row.get("status")
        if not isinstance(identifier, str) or REQUIREMENT_ID.fullmatch(identifier) is None:
            raise refuse(f"row {index} `requirement_id` is not 1 to 128 characters of letters, digits, dot, underscore, colon, hyphen, slash")
        if status not in (STATUS_ACTIVE, STATUS_RETIRED):
            raise refuse(f"row {index} `status` is not `active` or `retired`")
        if identifier in seen:
            raise refuse(f"row {index} repeats requirement_id {identifier}")
        seen.add(identifier)
        found.append(Requirement(identifier, str(status)))
    return tuple(found)


def load_snapshot(path: Path) -> tuple[Requirement, ...]:
    return parse_snapshot(_read_bytes(path), str(path))


# ------------------------------------------------------------------ spec declarations


def decode_source(data: bytes) -> str:
    """Decode spec bytes the way Python decodes source: a coding declaration or UTF-8, a BOM honoured."""
    encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
    return data.decode(encoding)


def normalise_source(declared: str) -> tuple[str | None, str]:
    """Turn a declared source into its canonical `/`-separated repository path.

    Backslashes become forward slashes and one leading dot-slash is dropped; nothing else is
    normalised. What is left must be a canonical path, otherwise the second item says why not.
    """
    text = declared.replace("\\", "/")
    if text.startswith("./"):
        text = text[2:]
    if not text:
        return None, "is an empty path"
    if CONTROL_TEXT.search(text):
        return None, "contains a control character or a lone surrogate"
    if len(text.encode("utf-8")) > SOURCE_PATH_LIMIT:
        return None, f"is longer than {SOURCE_PATH_LIMIT} bytes"
    if text.startswith("/") or text.startswith(":") or DRIVE_PREFIX.match(text):
        return None, "is not a relative repository path (leading slash or colon, or a drive letter)"
    for part in text.split("/"):
        if part in ("", ".", ".."):
            return None, "has an empty, dot or dot-dot segment"
    return text, ""


def parse_header(spec: str, text: str) -> SpecDeclaration:
    """Read the declarations of the first comment block of a spec.

    Only the lower-case keys `requirement`, `source` and `mutation` declare anything;
    every other comment line is free text. A value loses only the spaces and tabs around
    it; a value with a control character or a lone surrogate is a red with its key's code.
    """
    requirements: list[tuple[int, str]] = []
    sources: list[SourceLine] = []
    mutations: list[tuple[int, str]] = []
    malformed: list[Defect] = []
    urls: list[tuple[int, str]] = []
    for number, raw in enumerate(LINE_BREAK.split(text), 1):
        line = raw.strip(BLANKS)
        if not line.startswith("#"):
            break
        match = DECLARATION.match(line)
        if match is None:
            continue
        key, value = match.group(1), match.group(2).strip(BLANKS)
        broken = CONTROL_TEXT.search(value) is not None
        if key == "requirement":
            if not value:
                malformed.append(Defect(RETIRED_REQUIREMENT_BOUND, spec, f"line {number}: requirement declaration names no requirement of the snapshot"))
            elif broken:
                malformed.append(Defect(RETIRED_REQUIREMENT_BOUND, spec, f"line {number}: requirement value contains a control character or a lone surrogate"))
            else:
                requirements.append((number, value))
        elif key == "mutation":
            if not value:
                malformed.append(Defect(NO_MUTATION, spec, f"line {number}: mutation declaration has an empty name"))
                mutations.append((number, ""))
            elif broken:
                malformed.append(Defect(NO_MUTATION, spec, f"line {number}: mutation value contains a control character or a lone surrogate"))
                mutations.append((number, ""))
            else:
                mutations.append((number, value))
        else:
            if broken:
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source value contains a control character or a lone surrogate"))
                continue
            if "://" in value:
                urls.append((number, value))
                continue
            parsed = SOURCE_VALUE.match(value)
            if parsed is None:
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source declaration has no `sha256:` digest: {_quote(value)}"))
                continue
            path, digest = parsed.group("path"), parsed.group("digest")
            if path is None:
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source declaration has an empty path"))
            elif not DIGEST.match(digest):
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source {_quote(path)} digest is not 64 lower-case hex: {_quote(digest)}"))
            else:
                canonical, problem = normalise_source(path)
                sources.append(SourceLine(number, path, digest, canonical, problem))
    return SpecDeclaration(spec, tuple(requirements), tuple(sources), tuple(mutations), tuple(malformed), tuple(urls))


# ------------------------------------------------------------------ source resolution


def _git_environment() -> dict[str, str]:
    """The environment of every git child: nothing that picks a repository or a configuration,
    replace refs ignored, no lazy fetch over the network."""
    selecting = set(GIT_SELECTING_VARIABLES)
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() not in selecting and name.upper() != "GIT_CONFIG" and not name.upper().startswith("GIT_CONFIG_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    return environment


def _git_command(repo: Path, args: Sequence[str]) -> list[str]:
    return ["git", "-C", str(repo), "--no-replace-objects", *args]


def _git(repo: Path, args: Sequence[str], silent_failure: str = "git printed no message") -> bytes:
    """Run git in `repo`; any failure to serve the query is a tool fault.

    `args` never holds a declared source: a source never reaches git at all, only object ids do.
    `silent_failure` is the cause named when git fails and says nothing.
    """
    try:
        done = subprocess.run(
            _git_command(repo, args), stdin=subprocess.DEVNULL, capture_output=True, check=False, env=_git_environment(), timeout=GIT_TIMEOUT_SECONDS
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise ToolFault("TOOL_FAULT", f"cannot run git: {exc}") from exc
    if done.returncode != 0:
        message = done.stderr.decode("utf-8", errors="replace").strip() or silent_failure
        raise ToolFault("TOOL_FAULT", f"git {args[0]} failed (exit {done.returncode}): {message}")
    return done.stdout


def require_work_tree_top_level(repo: Path) -> None:
    """`--repo` must be the top level of a git work tree; anything else is a tool fault."""
    answer = _git(repo, ["rev-parse", "--show-toplevel"])
    lines = answer.split(b"\n")
    if len(lines) != 2 or lines[1] != b"" or not lines[0]:
        raise ToolFault("TOOL_FAULT", f"git rev-parse --show-toplevel answered outside its format for {repo}")
    top = os.fsdecode(lines[0])
    try:
        same = os.path.samefile(top, repo)
    except OSError as exc:
        raise ToolFault("TOOL_FAULT", f"cannot compare the work tree top level {_quote(top)} with --repo {repo}: {exc}") from exc
    if not same:
        raise ToolFault("TOOL_FAULT", f"--repo {repo} is not the top level of its git work tree ({_quote(top)})")


def resolve_head(repo: Path) -> str:
    """The full object id of the commit `HEAD` names, asked once per run."""
    answer = _git(repo, ["rev-parse", "--verify", "--quiet", "HEAD^{commit}"], "HEAD does not name a commit (the repository has no commit)")
    lines = answer.split(b"\n")
    if len(lines) != 2 or lines[1] != b"" or OBJECT_ID.fullmatch(lines[0]) is None:
        raise ToolFault("TOOL_FAULT", "git rev-parse HEAD answered outside its format")
    return lines[0].decode("ascii")


@dataclass(frozen=True)
class Header:
    """The first line of a `git cat-file --batch` answer for an object that exists."""

    oid: str
    kind: str
    size: int


@dataclass(frozen=True)
class TreeEntry:
    mode: int
    oid: str


class UnservableSource(ToolFault):
    """A tree names an object that the object store cannot serve (a fault, never a red)."""

    def __init__(self, message: str) -> None:
        super().__init__(SOURCE_UNSERVABLE, message)


class StoreSkipped(Exception):
    """The object store already failed in this run: no further lookup is made and no further fault is added."""


T = TypeVar("T")


class Body(Protocol):
    """The body of an object answered by the store, read in order."""

    def read(self, size: int = -1, /) -> bytes: ...


class Hasher(Protocol):
    """What the hash of an object offers (SHA-1 or SHA-256 from hashlib)."""

    def update(self, data: bytes, /) -> None: ...

    def hexdigest(self) -> str: ...


def object_hasher(oid: str, kind: str, size: int) -> Hasher:
    """A hash that has taken the header git hashes first: `<type> <size>` and a NUL byte.

    SHA-1 or SHA-256 is chosen by the width of the id; any other width is a fault.
    """
    hasher: Hasher
    if len(oid) == 40:
        hasher = hashlib.sha1(usedforsecurity=False)
    elif len(oid) == 64:
        hasher = hashlib.sha256()
    else:
        raise ToolFault("TOOL_FAULT", f"an object id of {len(oid)} digits is neither SHA-1 nor SHA-256")
    hasher.update(f"{kind} {size}".encode("ascii") + b"\0")
    return hasher


class HashedBody:
    """The body of one answer: every byte read through it is also fed to the hash of the object."""

    def __init__(self, stream: Body, hasher: Hasher) -> None:
        self.stream = stream
        self.hasher = hasher

    def read(self, size: int = -1, /) -> bytes:
        data = self.stream.read(size)
        self.hasher.update(data)
        return data


class ObjectStore:
    """One `git cat-file --batch` process for the whole run.

    Every lookup is a line on its standard input: a full object id. No declared source is ever
    written to it, so a source is never a pathspec, never an object name and never on a command
    line. Every object that comes back is hashed here against the id that was asked for.
    """

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.process: subprocess.Popen[bytes] | None = None
        self.broken = False

    def _start(self) -> subprocess.Popen[bytes]:
        if self.process is None:
            try:
                self.process = subprocess.Popen(
                    _git_command(self.repo, ["cat-file", "--batch"]),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=_git_environment(),
                )
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                raise self.fail(f"cannot run git: {exc}") from exc
        return self.process

    def fail(self, message: str) -> ToolFault:
        """The store cannot be trusted any more: stop the process and say why, once."""
        self.broken = True
        process = self.process
        detail = ""
        if process is not None:
            try:
                process.kill()
                if process.stderr is not None:
                    detail = process.stderr.read().decode("utf-8", errors="replace").strip()
            except (OSError, ValueError):
                pass
        return ToolFault("TOOL_FAULT", f"{message}: {detail}" if detail else message)

    def lookup(self, oid: str, consume: Callable[[Header, Body], T]) -> T | None:
        """Ask for the object `oid`. None when git answers `missing` for exactly this id.

        `consume` reads the body of an object that exists from the answer stream, which must
        then end in one line feed. The gate hashes what it read (`<type> <size>`, a NUL byte
        and the body) and the result must be `oid`. Any other answer (another object id than the
        one asked for, an unknown shape, a body of another size, an early end of the output, a
        body that does not hash to the id) is a tool fault naming what went wrong, and the store
        is not used again.
        """
        query = oid.encode("ascii")
        if self.broken:
            raise StoreSkipped
        process = self._start()
        stdin, stdout = process.stdin, process.stdout
        if stdin is None or stdout is None:
            raise self.fail("git cat-file has no standard streams")
        timer = threading.Timer(GIT_TIMEOUT_SECONDS, process.kill)
        timer.start()
        try:
            try:
                stdin.write(query + b"\n")
                stdin.flush()
                line = stdout.readline()
            except (OSError, ValueError) as exc:
                raise self.fail(f"git cat-file could not be asked: {exc}") from exc
            if not line.endswith(b"\n"):
                raise self.fail("git cat-file ended before it answered")
            if line == query + b" missing\n":
                return None
            matched = OBJECT_HEADER.fullmatch(line[:-1])
            if matched is None or matched.group(1).decode("ascii") != oid:
                raise self.fail("git cat-file answered outside its format")
            header = Header(matched.group(1).decode("ascii"), matched.group(2).decode("ascii"), int(matched.group(3)))
            try:
                hasher = object_hasher(oid, header.kind, header.size)
                result = consume(header, HashedBody(stdout, hasher))
                ending = stdout.read(1)
            except (OSError, ValueError) as exc:
                raise self.fail(f"git cat-file could not be read: {exc}") from exc
            if ending != b"\n":
                raise self.fail("git cat-file answered a body of another size than its header says")
            if hasher.hexdigest() != oid:
                raise self.fail(f"the object {oid} does not hash to its id: the store served forged or damaged content")
            return result
        finally:
            timer.cancel()

    def close(self) -> None:
        """End the process; it never outlives the run."""
        process, self.process = self.process, None
        if process is None:
            return
        try:
            if process.stdin is not None:
                process.stdin.close()
        except OSError:
            pass
        try:
            process.wait(timeout=5)
        except (OSError, subprocess.SubprocessError):
            process.kill()
            try:
                process.wait(timeout=5)
            except (OSError, subprocess.SubprocessError):
                pass
        for stream in (process.stdout, process.stderr):
            try:
                if stream is not None:
                    stream.close()
            except OSError:
                pass


def _read_exactly(stream: Body, size: int) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("the answer ended inside the body")
    return data


def _digest_of(stream: Body, size: int) -> str:
    """sha256 of the next `size` bytes of `stream`, read in blocks."""
    digest = hashlib.sha256()
    remaining = size
    while remaining:
        block = stream.read(min(remaining, DIGEST_BLOCK))
        if not block:
            raise ValueError("the answer ended inside the body")
        digest.update(block)
        remaining -= len(block)
    return digest.hexdigest()


def parse_tree(content: bytes, raw_size: int) -> dict[bytes, TreeEntry]:
    """The entries of a raw tree object: an octal mode, a space, a name, a NUL and a raw object id, repeated."""
    entries: dict[bytes, TreeEntry] = {}
    position = 0
    while position < len(content):
        space = content.find(b" ", position)
        nul = content.find(b"\0", space + 1) if space >= 0 else -1
        end = nul + 1 + raw_size
        mode_text = content[position:space] if space >= 0 else b""
        name = content[space + 1 : nul] if nul >= 0 else b""
        if nul < 0 or end > len(content) or TREE_MODE.fullmatch(mode_text) is None or not name or b"/" in name:
            raise ToolFault("TOOL_FAULT", "git cat-file answered a tree outside its format")
        if name in entries:
            raise ToolFault("TOOL_FAULT", "git cat-file answered a tree that names one entry twice")
        entries[name] = TreeEntry(int(mode_text, 8), content[nul + 1 : end].hex())
        position = end
    return entries


def _kind_of(mode: int) -> str:
    return {0o040000: "directory", 0o120000: "symbolic link", 0o160000: "submodule", 0o100000: "file"}.get(mode & 0o170000, "other")


ABSENT = "is not tracked at HEAD (names match exactly, including case)"


class HeadReader:
    """Reads canonical repository paths of one commit of one repository, by walking its trees.

    The commit is the one `HEAD` named at the start of the run; every lookup goes through one
    object store. The tree entry of a source is read from its parent tree, so a symbolic link or a
    submodule is told from a file by its mode, and an entry the store cannot serve is told from
    one the tree does not name.
    """

    def __init__(self, repo: Path, head: str | None) -> None:
        self.head = head
        self.store = ObjectStore(repo)
        self.trees: dict[str, dict[bytes, TreeEntry]] = {}
        self.root: dict[bytes, TreeEntry] | None = None
        self.raw_size = 0 if head is None else len(head) // 2
        if head is None:
            self.store.broken = True

    def close(self) -> None:
        self.store.close()

    def _load_tree(self, oid: str, unservable: str) -> dict[bytes, TreeEntry]:
        served = self.store.lookup(oid, lambda header, stream: (header, _read_exactly(stream, header.size)))
        if served is None:
            raise UnservableSource(unservable)
        header, content = served
        if header.kind != "tree":
            raise self.store.fail(f"git cat-file answered a tree lookup for {oid} with another kind of object")
        try:
            return parse_tree(content, self.raw_size)
        except ToolFault as fault:
            self.store.broken = True
            raise fault

    def _root_tree_id(self, head: str) -> str:
        """The `tree` line of the commit `head`, read raw and hashed like every object."""
        served = self.store.lookup(head, lambda header, stream: (header, _read_exactly(stream, header.size)))
        if served is None:
            raise UnservableSource("the commit of HEAD cannot be served by the object store")
        header, content = served
        if header.kind != "commit":
            raise self.store.fail(f"git cat-file answered a commit lookup for {head} with another kind of object")
        line = content.split(b"\n", 1)[0]
        if not line.startswith(b"tree ") or OBJECT_ID.fullmatch(line[5:]) is None or len(line) - 5 != len(head):
            self.store.broken = True
            raise ToolFault("TOOL_FAULT", f"the commit {head} has no readable tree line")
        return line[5:].decode("ascii")

    def _root_tree(self) -> dict[bytes, TreeEntry]:
        if self.root is None:
            if self.head is None:
                raise StoreSkipped
            self.root = self._load_tree(self._root_tree_id(self.head), "the tree of HEAD cannot be served by the object store")
        return self.root

    def _subtree(self, entry: TreeEntry) -> dict[bytes, TreeEntry]:
        if entry.oid not in self.trees:
            message = "a tree on the path is named by its parent tree but the object store cannot serve it"
            self.trees[entry.oid] = self._load_tree(entry.oid, message)
        return self.trees[entry.oid]

    def read(self, path: str) -> tuple[str | None, str]:
        """The sha256 of the content of the regular file at `<commit>:<path>`; the second item is the reason when there is none.

        A tree that does not name the path, or names a link, a submodule or a directory in its
        place, gives no digest and a reason (a red). An object that a tree names and the store
        cannot serve raises `UnservableSource` (a fault).
        """
        names = [part.encode("utf-8") for part in path.split("/")]
        tree = self._root_tree()
        for name in names[:-1]:
            entry = tree.get(name)
            if entry is None:
                return None, ABSENT
            if _kind_of(entry.mode) != "directory":
                return None, "is not tracked at HEAD (a directory on the path is not a directory)"
            tree = self._subtree(entry)
        entry = tree.get(names[-1])
        if entry is None:
            return None, ABSENT
        kind = _kind_of(entry.mode)
        if kind == "directory":
            return None, "is not a blob at HEAD (a directory)"
        if kind != "file":
            return None, f"is not a regular file at HEAD ({kind})"
        digest = self.store.lookup(entry.oid, self._blob_digest)
        if digest is None:
            raise UnservableSource("the source is named by its parent tree but the object store cannot serve it")
        return digest, ""

    @staticmethod
    def _blob_digest(header: Header, stream: Body) -> str:
        if header.kind != "blob":
            raise ValueError("a file entry is not a blob")
        return _digest_of(stream, header.size)


# ------------------------------------------------------------------ literal expected


def _is_number(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Constant)
        and not isinstance(node.value, bool)
        and isinstance(node.value, (int, float, complex))
    )


def is_literal(node: ast.expr, depth: int = 0) -> bool:
    """A number, string or bytes constant, or a display made only of such constants.

    `None`, `True`, `False` and `...` are not literals; a signed number is. A display
    nested deeper than the analysis budget raises `Unanalysable`.
    """
    if depth > ANALYSIS_DEPTH:
        raise Unanalysable
    if isinstance(node, ast.Constant):
        value = node.value
        if value is None or isinstance(value, bool):
            return False
        return isinstance(value, (int, float, complex, str, bytes))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _is_number(node.operand)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(is_literal(element, depth + 1) for element in node.elts)
    if isinstance(node, ast.Dict):
        return all(key is not None and is_literal(key, depth + 1) for key in node.keys) and all(
            is_literal(value, depth + 1) for value in node.values
        )
    return False


def compares_with_literal(test: ast.expr, depth: int = 0) -> bool:
    if depth > ANALYSIS_DEPTH:
        raise Unanalysable
    if isinstance(test, ast.Compare):
        return any(is_literal(operand, depth + 1) for operand in (test.left, *test.comparators))
    if isinstance(test, ast.BoolOp):
        return any(compares_with_literal(value, depth + 1) for value in test.values)
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return compares_with_literal(test.operand, depth + 1)
    return False


def _source_text(text: str, node: ast.expr) -> str:
    """The source of `node` in the decoded text, never rendered from the tree, cut to DETAIL_LIMIT characters."""
    segment = ast.get_source_segment(text, node)
    return _shorten("<source text unavailable>" if segment is None else segment)


def literal_defects(spec: str, text: str) -> list[Defect]:
    """The LITERAL_EXPECTED defects of the decoded text of a spec; a text that does not parse is one."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        where = f"line {exc.lineno}" if exc.lineno is not None else "unknown line"
        return [Defect(LITERAL_EXPECTED, spec, f"syntax error {where}: {exc.msg}; the contract cannot be read")]
    asserts = sorted(
        (node for node in ast.walk(tree) if isinstance(node, ast.Assert)),
        key=lambda node: (node.lineno, node.col_offset),
    )
    found: list[Defect] = []
    for node in asserts:
        try:
            literal = compares_with_literal(node.test)
            note = "assert compares with a literal constant"
        except (Unanalysable, RecursionError):
            literal = True
            note = "assert cannot be analysed within the gate's limits (nesting too deep)"
        if literal:
            found.append(Defect(LITERAL_EXPECTED, spec, f"line {node.lineno}: {note}: {_source_text(text, node.test)}"))
    return found


def analyse_spec(spec: str, data: bytes) -> SpecAnalysis:
    """Everything derived from the bytes of one spec, inside the one per-spec guard.

    Decoding, reading the declarations, parsing, walking the tree and rendering a detail all
    run here. Whatever any of them raises is a red of this spec (a LITERAL_EXPECTED defect
    saying the spec cannot be analysed and why); no exception from here is ever a tool fault.
    Nothing in here reads a file or runs git.
    """
    declaration: SpecDeclaration | None = None
    literals: tuple[Defect, ...] = ()
    try:
        text = decode_source(data)
        declaration = parse_header(spec, text)
        literals = tuple(literal_defects(spec, text))
    except Exception as exc:
        try:
            reason = str(exc)
        except Exception:
            reason = ""
        label = f"{type(exc).__name__}: {reason}" if reason else type(exc).__name__
        literals = (Defect(LITERAL_EXPECTED, spec, f"the spec cannot be analysed ({_shorten(label)}); the contract cannot be read"),)
    return SpecAnalysis(declaration, literals)


# ------------------------------------------------------------------------ the gate


def _is_link(entry: os.DirEntry[str]) -> bool:
    """A symbolic link or, on Windows, a junction: neither is followed."""
    try:
        if entry.is_symlink():
            return True
        info = entry.stat(follow_symlinks=False)
    except OSError as exc:
        raise ToolFault("TOOL_FAULT", f"cannot inspect {entry.path}: {exc}") from exc
    tag: int = getattr(info, "st_reparse_tag", 0)
    return tag in LINK_REPARSE_TAGS


def discover_specs(specs_real: Path, faults: list[ToolFault]) -> list[Path]:
    """Every regular file named `test_*.py` under `specs_real`; links and junctions are not followed.

    A directory that cannot be listed or an entry that cannot be inspected is a fault added to
    `faults`; the walk goes on with everything else.
    """
    found: list[Path] = []
    pending: list[Path] = [specs_real]
    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                listing = sorted(entries, key=lambda entry: entry.name)
        except OSError as exc:
            faults.append(ToolFault("TOOL_FAULT", f"cannot list {directory}: {exc}"))
            continue
        for entry in listing:
            try:
                if _is_link(entry):
                    continue
                is_directory = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except (OSError, ToolFault) as exc:
                faults.append(ToolFault("TOOL_FAULT", f"cannot inspect {entry.path}: {exc}"))
                continue
            if is_directory:
                pending.append(Path(entry.path))
            elif is_file and fnmatch.fnmatchcase(entry.name, SPEC_PATTERN):
                found.append(Path(entry.path))
    return sorted(found, key=lambda path: path.relative_to(specs_real).as_posix())


@dataclass(frozen=True)
class SpecResult:
    defects: tuple[Defect, ...]
    declared: tuple[str, ...]
    faults: tuple[ToolFault, ...]


def check_spec(spec: str, data: bytes, reader: HeadReader, status: dict[str, str]) -> SpecResult:
    """Every red of one spec and every fault met while checking it; a fault never drops a red."""
    analysis = analyse_spec(spec, data)
    defects: list[Defect] = []
    declared: list[str] = []
    faults: list[ToolFault] = []
    declaration = analysis.declaration
    if declaration is not None:
        for number, value in declaration.url_sources:
            faults.append(ToolFault(SOURCE_UNSERVABLE, f"{spec}: line {number} source {_quote(value)} is a URL and cannot be verified offline"))
        defects.extend(declaration.malformed)
        for source in declaration.sources:
            digest: str | None = None
            reason = source.problem
            if source.canonical is not None:
                try:
                    digest, reason = reader.read(source.canonical)
                except StoreSkipped:
                    continue
                except ToolFault as fault:
                    faults.append(ToolFault(fault.label, f"{spec}: line {source.line} source {_quote(source.declared)}: {fault.message}"))
                    continue
            if digest is None:
                defects.append(Defect(SOURCE_MISSING, spec, f"line {source.line}: source {_quote(source.declared)} {reason}"))
            elif digest != source.digest:
                defects.append(Defect(SOURCE_DIGEST_MISMATCH, spec, f"line {source.line}: source {_quote(source.declared)} does not match the declared digest"))
        for _, identifier in declaration.requirements:
            if identifier in declared:
                continue
            declared.append(identifier)
            current = status.get(identifier)
            if current is None:
                defects.append(Defect(RETIRED_REQUIREMENT_BOUND, spec, f"requirement {_quote(identifier)} is absent from the snapshot"))
            elif current == STATUS_RETIRED:
                defects.append(Defect(RETIRED_REQUIREMENT_BOUND, spec, f"requirement {_quote(identifier)} is retired"))
        if declaration.requirements:
            has_source = bool(declaration.sources or declaration.url_sources)
            if not has_source and not any(d.code == SOURCE_MISSING for d in declaration.malformed):
                defects.append(Defect(SOURCE_MISSING, spec, "the spec declares a requirement but no source"))
            if not declaration.mutation_lines:
                defects.append(Defect(NO_MUTATION, spec, "the spec declares a requirement but no mutation"))
    defects.extend(analysis.literal_defects)
    return SpecResult(tuple(defects), tuple(declared), tuple(faults))


def run(arguments: Arguments) -> Report:
    """Find every red the run can find; faults are collected beside them (red before fault).

    A fault that leaves nothing to check (`--repo`, the snapshot, `--specs`) is raised at once.
    A fault met while checking (a spec that cannot be read, a URL source, a source the object
    store cannot serve, git failing) is added to the report and the rest of the run goes on.
    """
    repo_real = Path(os.path.realpath(arguments.repo))
    if not repo_real.is_dir():
        raise ToolFault("TOOL_FAULT", f"--repo {arguments.repo} is not a directory")
    require_work_tree_top_level(repo_real)
    requirements = load_snapshot(arguments.snapshot)
    specs_real = Path(os.path.realpath(arguments.specs))
    if not specs_real.is_dir():
        raise ToolFault("TOOL_FAULT", f"--specs {arguments.specs} is not a directory")
    if not specs_real.is_relative_to(repo_real):
        raise UsageError(f"--specs {arguments.specs} is not inside --repo {arguments.repo}")
    status = {item.requirement_id: item.status for item in requirements}
    faults: list[ToolFault] = []
    spec_paths = discover_specs(specs_real, faults)
    complete = not faults
    head: str | None = None
    try:
        head = resolve_head(repo_real)
    except ToolFault as fault:
        faults.append(fault)
    reader = HeadReader(repo_real, head)
    defects: list[Defect] = []
    declared: set[str] = set()
    try:
        for spec_path in spec_paths:
            spec = spec_path.relative_to(repo_real).as_posix()
            try:
                data = _read_bytes(spec_path)
            except ToolFault as fault:
                faults.append(fault)
                complete = False
                continue
            try:
                result = check_spec(spec, data, reader, status)
            except Exception as exc:  # outside a spec's bytes an unexpected error is a fault of the run, never a traceback
                faults.append(ToolFault("TOOL_FAULT", f"unexpected {type(exc).__name__} while checking {spec}: {exc}"))
                complete = False
                continue
            defects.extend(result.defects)
            declared.update(result.declared)
            faults.extend(result.faults)
    finally:
        reader.close()
    if complete:
        # A requirement is unbound only when every spec was read; a spec that could not be read may declare it.
        for item in sorted(requirements, key=lambda entry: entry.requirement_id):
            if item.status == STATUS_ACTIVE and item.requirement_id not in declared:
                defects.append(Defect(NO_SPEC_FOR_REQUIREMENT, item.requirement_id, "no spec declares this active requirement"))
    return Report(len(requirements), len(spec_paths), tuple(defects), tuple(faults))


# ---------------------------------------------------------------------------- CLI


def parse_arguments(args: Sequence[str]) -> Arguments:
    values: dict[str, str] = {}
    index = 0
    while index < len(args):
        arg = args[index]
        name, equals, inline = arg.partition("=")
        if name not in OPTIONS:
            raise UsageError(f"unknown option or argument {_quote(arg)}")
        if name in values:
            raise UsageError(f"{name} given more than once")
        if equals:
            value = inline
            index += 1
        else:
            if index + 1 >= len(args) or args[index + 1].startswith("-"):
                raise UsageError(f"{name} needs a value")
            value = args[index + 1]
            index += 2
        if not value.strip():
            raise UsageError(f"{name} needs a non-empty value")
        values[name] = value
    missing = [name for name in OPTIONS if name not in values]
    if missing:
        raise UsageError(f"missing {', '.join(missing)}")
    return Arguments(Path(values["--repo"]), Path(values["--snapshot"]), Path(values["--specs"]))


def _harden_streams() -> None:
    """Keep the host's encoding but never let an unencodable character raise on output."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (OSError, ValueError):
                pass


def main(argv: Sequence[str] | None = None) -> int:
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        report = run(parse_arguments(args))
    except UsageError as exc:
        print(USAGE, file=sys.stderr)
        print(f"contract_gate.py: error: {escape_text(str(exc))}", file=sys.stderr)
        return 3
    except ToolFault as exc:
        print(f"{escape_text(exc.label)} {escape_text(exc.message)}", file=sys.stderr)
        return 2
    except Exception as exc:  # outside a spec's bytes an unexpected error is a tool fault, never a traceback
        print(f"TOOL_FAULT unexpected {type(exc).__name__}: {escape_text(str(exc))}", file=sys.stderr)
        return 2
    summary = f"requirements={report.requirements} specs={report.specs} defects={len(report.defects)}"
    for defect in report.defects:
        print(defect.render())
    for fault in report.faults:
        print(f"{escape_text(fault.label)} {escape_text(fault.message)}", file=sys.stderr)
    if report.defects:
        print(summary, file=sys.stderr)
        return 1
    if report.faults:
        return 2
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
