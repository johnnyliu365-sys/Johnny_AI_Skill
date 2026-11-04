"""Evidence gate: a receipt proves every run cell or the run is red.

Usage:
  evidence_gate.py <receipt> --repo DIR --candidate SHA --tool PATH [--tool PATH ...]
                   [--require-cell NAME ...] [--evidence-root DIR]

A run cell is a `## <name>` section of the receipt holding the lines `cell: <name>`,
`candidate: <full sha>`, `tool_digest:` followed by `- <path>=<sha256>` lines,
`capture: <path relative to the evidence root>` and `exit: <comma-separated exit codes in
capture order>`, then the capture in one four-backtick fence. A section with `cell: STATEMENT`
is informational and carries none of `capture:`, `exit:` or a fence.

Defect codes (exit 1, one line `<code> <section>: <detail>` each): NO_CELLS, NOT_RUN,
CELL_FIELD_MISSING, STATEMENT_HAS_RUN_FIELDS, DUPLICATE_CELL, CANDIDATE_MISMATCH,
TOOL_DIGEST_MISSING, TOOL_DIGEST_STALE, CAPTURE_MISSING, CAPTURE_CR, BLOCK_MISMATCH,
EXIT_MISMATCH, FIELD_REPEATED, CELL_NAME_MISMATCH. The last line is `cells=N defects=M`.

A `tool_digest` path is judged in two steps, and neither can turn a red into a tool fault.
First its form: a canonical path is non-empty, at most 1024 bytes in UTF-8, holds no control
character, uses only the forward slash as separator, does not start with a slash or a colon,
has no drive letter and no empty, single-dot or double-dot segment; any other path is
TOOL_DIGEST_STALE. Then one literal lookup from the repository root: the line
`<candidate>:<path>` is written to the standard input of `git cat-file --batch-check` and,
for a blob, of `git cat-file --batch`; the path is never passed to git as a pathspec or on its
command line. A missing object or one that is not a blob (a tree, a submodule entry) is
TOOL_DIGEST_STALE; git failing to start, exiting non-zero or answering outside its documented
format is a tool fault. A `missing` answer is told apart from an unservable object: the parent
tree is read through the same standard input, and an entry that tree names as a blob but the
object store cannot serve is a tool fault, not an absent path. The root comes from the
repository, so `--repo` may be any directory inside it.

The listed values need no git, so they are judged before the lookup and whatever its outcome: a
value that is not 64 lower-case hex digits, and two different values listed for one path, are
TOOL_DIGEST_STALE beside a fault on that lookup. A `--tool` path that is not a blob at the
candidate is a tool fault and, since no receipt can list a digest for it, a TOOL_DIGEST_MISSING
red in every run cell, so it ends in exit 1.

Every git child runs with `--no-replace-objects`, `GIT_NO_REPLACE_OBJECTS=1` and
`GIT_NO_LAZY_FETCH=1`, with the repository-selecting `GIT_*` and the `GIT_CONFIG_*` variables
removed from its environment, and is started from the `PATH` entries that are absolute
directories only, never from the current directory: a replace ref never redirects a lookup and
a lookup never fetches. Every string read from the receipt is valid Unicode without lone surrogates
and without control characters; one that is not is a red, never a fault. Every subject
printed in a defect line is escaped, so one defect is always one line.

Exit codes: 0 pass, 1 contract red, 2 tool fault (git or the file system cannot serve the
check), 3 usage error. Red before fault: the gate reports every red it can find and exits 1 if
there is one, with each fault on standard error on one line; it exits 2 only when it found no
red. A red is never reported as a tool fault and a tool fault is never reported as a red.
Standard library only. Output uses LF and escapes what the console
cannot encode, so the console encoding never changes an exit code.
"""
from __future__ import annotations

import hashlib
import io
import os
import posixpath
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

EXIT_PASS = 0
EXIT_RED = 1
EXIT_FAULT = 2
EXIT_USAGE = 3

USAGE = (
    "usage: evidence_gate.py <receipt> --repo DIR --candidate SHA --tool PATH [--tool PATH ...] "
    "[--require-cell NAME ...] [--evidence-root DIR]"
)

FENCE = "`" * 4
STATEMENT = "STATEMENT"
CR = b"\r"
FULL_SHA = re.compile(r"[0-9a-fA-F]{40}")
LOWER_FULL_SHA = re.compile(r"[0-9a-f]{40}")
FIELD_LINE = re.compile(r"(cell|candidate|capture|exit):[ \t]*(.*)")
DIGEST_LABEL = re.compile(r"tool_digest:.*")
EXIT_LINE = re.compile(r"exit=(-?[0-9]+)")
DRIVE_PREFIX = re.compile(r"[A-Za-z]:")
RECEIPT_SECTION = "(receipt)"
BYTE_CODEC = "utf-8"
BYTE_ERRORS = "surrogateescape"
HORIZONTAL_SPACE = " 	"
MAX_DIGEST_PATH_BYTES = 1024
OBJECT_REPLY = re.compile(r"([0-9a-f]{40}|[0-9a-f]{64}) ([a-z]+)(?: ([0-9]+))?")
OBJECT_NAME = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
DIGEST_VALUE = re.compile(r"[0-9a-f]{64}")
BLOB = "blob"
REPEAT_ORDER = ("cell", "candidate", "tool_digest", "capture", "exit", "fence")
NO_REPLACE_FLAG = "--no-replace-objects"
GIT_FIXED_ENVIRONMENT = {"GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1"}
GIT_REMOVED_VARIABLES = frozenset(
    {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_PREFIX",
        "GIT_QUARANTINE_PATH",
        "GIT_REPLACE_REF_BASE",
        "GIT_GRAFT_FILE",
        "GIT_SHALLOW_FILE",
    }
)
GIT_CONFIG_PREFIX = "GIT_CONFIG"
TREE = "tree"
SUBMODULE = "submodule"
TREE_MODE = "40000"
GITLINK_MODE = "160000"
BLOB_MODES = frozenset({"100644", "100755", "120000"})


class ToolFault(Exception):
    """git or the file system cannot serve the check (exit 2)."""


class UsageError(Exception):
    """The command line is malformed (exit 3)."""


class DefectCode(Enum):
    NO_CELLS = "NO_CELLS"
    NOT_RUN = "NOT_RUN"
    CELL_FIELD_MISSING = "CELL_FIELD_MISSING"
    STATEMENT_HAS_RUN_FIELDS = "STATEMENT_HAS_RUN_FIELDS"
    DUPLICATE_CELL = "DUPLICATE_CELL"
    CANDIDATE_MISMATCH = "CANDIDATE_MISMATCH"
    TOOL_DIGEST_MISSING = "TOOL_DIGEST_MISSING"
    TOOL_DIGEST_STALE = "TOOL_DIGEST_STALE"
    CAPTURE_MISSING = "CAPTURE_MISSING"
    CAPTURE_CR = "CAPTURE_CR"
    BLOCK_MISMATCH = "BLOCK_MISMATCH"
    EXIT_MISMATCH = "EXIT_MISMATCH"
    FIELD_REPEATED = "FIELD_REPEATED"
    CELL_NAME_MISMATCH = "CELL_NAME_MISMATCH"


def has_bad_text(text: str) -> bool:
    """True when `text` holds a control character (U+0000-U+001F, U+007F) or a lone surrogate."""
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F or 0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def printable(text: str) -> str:
    """`text` escaped (Python repr rules, without the outer quotes) so it stays on one line."""
    return repr(text)[1:-1]


@dataclass(frozen=True)
class Defect:
    code: DefectCode
    section: str
    detail: str

    def render(self) -> str:
        return f"{self.code.value} {printable(self.section)}: {printable(self.detail)}"


@dataclass(frozen=True)
class Arguments:
    receipt: Path
    repo: Path
    candidate: str
    tools: tuple[str, ...]
    require_cells: tuple[str, ...]
    evidence_root: Path | None


@dataclass
class Section:
    """One `## <heading>` section of the receipt, parsed once."""

    heading: str
    fields: dict[str, str] = field(default_factory=dict)
    has_digest_label: bool = False
    digest_lines: list[str] = field(default_factory=list)
    fence_count: int = 0
    block_lines: list[str] = field(default_factory=list)
    block_closed: bool = False
    repeated: list[str] = field(default_factory=list)

    def note_repeat(self, name: str) -> None:
        if name not in self.repeated:
            self.repeated.append(name)

    @property
    def cell_value(self) -> str | None:
        return self.fields.get("cell")

    @property
    def is_statement(self) -> bool:
        return self.fields.get("cell") == STATEMENT


@dataclass(frozen=True)
class GitResult:
    returncode: int
    stdout: bytes
    stderr: str


@dataclass
class Report:
    """What one run found: the reds, the faults (each once), and the run cells counted so far."""

    cells: int = 0
    defects: list[Defect] = field(default_factory=list)
    faults: list[str] = field(default_factory=list)

    def fault(self, message: str) -> None:
        if message not in self.faults:
            self.faults.append(message)


@dataclass(frozen=True)
class TreeRead:
    """One object read by name: its type, and for a tree the mode of each entry by name."""

    kind: str
    entries: dict[bytes, str]


# ----------------------------------------------------------------------------- arguments


def digest_path_problem(path: str) -> str | None:
    """Why `path` is not a canonical repository-relative path, or None when it is canonical."""
    if not path:
        return "empty path"
    if has_bad_text(path):
        return "path holds a control character or a lone surrogate"
    if len(path.encode(BYTE_CODEC)) > MAX_DIGEST_PATH_BYTES:
        return f"path is longer than {MAX_DIGEST_PATH_BYTES} bytes"
    if "\\" in path:
        return "path holds a backslash"
    if path.startswith("/"):
        return "absolute path"
    if DRIVE_PREFIX.match(path):
        return "path has a drive letter"
    if path.startswith(":"):
        return "path starts with ':' (pathspec magic)"
    for segment in path.split("/"):
        if not segment:
            return "path has an empty segment"
        if segment == ".":
            return "path has a '.' segment"
        if segment == "..":
            return "path has a '..' segment"
    return None


def parse_arguments(argv: Sequence[str]) -> Arguments:
    receipt: str | None = None
    repo: str | None = None
    candidate: str | None = None
    tools: list[str] = []
    require_cells: list[str] = []
    evidence_root: str | None = None
    singles = {"--repo", "--candidate", "--evidence-root"}
    repeats = {"--tool", "--require-cell"}
    index = 0
    while index < len(argv):
        token = argv[index]
        index += 1
        if token.startswith("--"):
            name, equals, inline = token.partition("=")
            if name not in singles and name not in repeats:
                raise UsageError(f"unknown option {printable(name)}")
            if equals:
                value = inline
            else:
                if index >= len(argv):
                    raise UsageError(f"{printable(name)} needs a value")
                value = argv[index]
                index += 1
            if name == "--repo":
                if repo is not None:
                    raise UsageError("--repo given twice")
                repo = value
            elif name == "--candidate":
                if candidate is not None:
                    raise UsageError("--candidate given twice")
                candidate = value
            elif name == "--evidence-root":
                if evidence_root is not None:
                    raise UsageError("--evidence-root given twice")
                evidence_root = value
            elif name == "--tool":
                tools.append(value)
            else:
                require_cells.append(value)
        elif token.startswith("-") and len(token) > 1:
            raise UsageError(f"unknown option {printable(token)}")
        else:
            if receipt is not None:
                raise UsageError("more than one receipt argument")
            receipt = token
    if receipt is None or not receipt.strip():
        raise UsageError("the receipt path is required")
    if repo is None or not repo.strip():
        raise UsageError("--repo is required")
    if candidate is None or LOWER_FULL_SHA.fullmatch(candidate) is None:
        raise UsageError("--candidate must be a full 40-character lower-case commit sha")
    if evidence_root is not None and not evidence_root.strip():
        raise UsageError("--evidence-root must not be blank")
    if not tools:
        raise UsageError("at least one --tool is required")
    if any(not tool.strip() for tool in tools):
        raise UsageError("--tool must not be blank")
    if any(not name.strip() for name in require_cells):
        raise UsageError("--require-cell must not be blank")
    if any(has_bad_text(value) for value in [*tools, *require_cells]):
        raise UsageError("--tool and --require-cell must not hold control characters or lone surrogates")
    normalised_tools = unique([tool.strip().replace("\\", "/") for tool in tools])
    for tool in normalised_tools:
        problem = digest_path_problem(tool)
        if problem is not None:
            raise UsageError(f"--tool {printable(tool)}: {problem}")
    return Arguments(
        receipt=Path(receipt),
        repo=Path(repo),
        candidate=candidate,
        tools=tuple(normalised_tools),
        require_cells=tuple(unique([name.strip() for name in require_cells])),
        evidence_root=Path(evidence_root) if evidence_root is not None else None,
    )


def unique(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# ----------------------------------------------------------------------------- git


def git_environment(source: Mapping[str, str]) -> dict[str, str]:
    """`source` for a git child: the repository-selecting and config variables removed, replace refs
    and lazy fetching switched off."""
    kept = {
        key: value
        for key, value in source.items()
        if key.upper() not in GIT_REMOVED_VARIABLES
        and key.upper() not in GIT_FIXED_ENVIRONMENT
        and not key.upper().startswith(GIT_CONFIG_PREFIX)
    }
    kept.update(GIT_FIXED_ENVIRONMENT)
    return kept


def git_executable(path_value: str | None) -> str:
    """The first git executable in an absolute directory of `path_value`; the current directory is never searched."""
    names = ("git.exe", "git.com") if os.name == "nt" else ("git",)
    for entry in (path_value or "").split(os.pathsep):
        folder = entry.strip('"')
        if not folder or not Path(folder).is_absolute():
            continue
        for name in names:
            candidate = os.path.join(folder, name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    raise ToolFault("cannot start git: no executable named git in an absolute PATH entry")


def run_git(repo: Path, args: Sequence[str], stdin: bytes | None = None) -> GitResult:
    try:
        executable = git_executable(os.environ.get("PATH"))
        done = subprocess.run(
            [executable, "-C", str(repo), NO_REPLACE_FLAG, *args],
            capture_output=True,
            input=stdin,
            env=git_environment(os.environ),
        )
    except OSError as error:
        raise ToolFault(f"cannot start git: {error}") from error
    return GitResult(done.returncode, done.stdout, done.stderr.decode("utf-8", errors="replace").strip())


def parse_tree(body: bytes, raw_width: int) -> dict[bytes, str]:
    """Mode of each entry by name in the stored bytes of a tree whose object names are `raw_width` bytes."""
    entries: dict[bytes, str] = {}
    position = 0
    while position < len(body):
        space = body.find(b" ", position)
        nul = body.find(b"\0", space + 1) if space >= 0 else -1
        if space < 0 or nul < 0 or nul + 1 + raw_width > len(body):
            raise ToolFault("git cat-file --batch returned a tree outside its documented format")
        name = body[space + 1 : nul]
        if name in entries:
            raise ToolFault("git cat-file --batch returned a tree that names an entry twice")
        entries[name] = body[position:space].decode("ascii", errors="replace")
        position = nul + 1 + raw_width
    return entries


def is_missing_answer(header: bytes, name: bytes) -> bool:
    """True when `header` is `<name> missing` or `<object name> missing` for exactly this request."""
    subject, _, word = header.rpartition(b" ")
    return word == b"missing" and (
        subject == name or OBJECT_NAME.fullmatch(subject.decode("ascii", errors="replace")) is not None
    )


class GitView:
    """Reads blobs of one candidate commit by literal lookup and caches their sha256."""

    def __init__(self, repo: Path, candidate: str) -> None:
        self._repo = repo
        self._candidate = candidate
        self._cache: dict[str, str | None] = {}
        self._faults: dict[str, ToolFault] = {}
        self._trees: dict[str, TreeRead | None] = {}
        self._unusable: ToolFault | None = None

    def mark_unusable(self, fault: ToolFault) -> None:
        """Every later lookup raises `fault` without starting git."""
        self._unusable = fault

    def verify(self) -> None:
        inside = run_git(self._repo, ["rev-parse", "--git-dir"])
        if inside.returncode != 0:
            raise ToolFault(f"{self._repo} is not a usable git repository: {inside.stderr}")
        top = run_git(self._repo, ["rev-parse", "--show-toplevel"])
        if top.returncode == 0:
            # the lookup is rooted at the repository top, whichever directory --repo names
            root = top.stdout.decode("utf-8", errors="replace").strip()
            if root:
                self._repo = Path(root)
        found = run_git(self._repo, ["rev-parse", "--verify", f"{self._candidate}^{{commit}}"])
        if found.returncode != 0:
            raise ToolFault(f"git cannot resolve candidate {self._candidate}: {found.stderr}")

    def _ask(self, mode: str, request: bytes) -> bytes:
        """The standard output of `git cat-file <mode>` for one request line; any failure is a tool fault."""
        if self._unusable is not None:
            raise self._unusable
        asked = run_git(self._repo, ["cat-file", mode], request)
        if asked.returncode != 0:
            raise ToolFault(f"git cat-file {mode} exited {asked.returncode}: {asked.stderr}")
        return asked.stdout

    def _blob(self, path: str) -> bytes | None:
        """The stored bytes of `<candidate>:<path>`; None when it is absent or not a blob.

        An object that the candidate's own tree names as a blob but the object store cannot serve is a tool fault.
        """
        problem = digest_path_problem(path)
        if problem is not None:  # a caller must have judged the form; git is never asked about this path
            raise ToolFault(f"internal error: lookup of a non-canonical path {printable(path)}: {problem}")
        name = f"{self._candidate}:{path}".encode(BYTE_CODEC)
        request = name + b"\n"
        reply = self._ask("--batch-check", request)
        first, newline, rest = reply.partition(b"\n")
        if not newline or rest:
            raise ToolFault("git cat-file --batch-check answered outside its documented format")
        if is_missing_answer(first, name):
            self._settle_missing(path, final=True)
            return None
        checked = OBJECT_REPLY.fullmatch(first.decode("ascii", errors="replace"))
        if checked is None:
            raise ToolFault("git cat-file --batch-check answered outside its documented format")
        if checked.group(2) != BLOB:  # a tree, a commit, or a submodule entry (which has no size)
            return None
        if checked.group(3) is None:
            raise ToolFault("git cat-file --batch-check answered outside its documented format")
        fetched = self._ask("--batch", request)
        header, newline, body = fetched.partition(b"\n")
        if not newline or header != first:
            raise ToolFault("git cat-file --batch answered outside its documented format")
        size = int(checked.group(3))
        if len(body) != size + 1 or not body.endswith(b"\n"):
            raise ToolFault("git cat-file --batch returned a body that does not match its size")
        return body[:size]

    def _read_tree(self, folder: str) -> TreeRead | None:
        """The object `<candidate>:<folder>` read through standard input (the root tree for an empty folder)."""
        if folder not in self._trees:
            name = f"{self._candidate}:{folder}".encode(BYTE_CODEC)
            fetched = self._ask("--batch", name + b"\n")
            header, newline, body = fetched.partition(b"\n")
            if not newline:
                raise ToolFault("git cat-file --batch answered outside its documented format")
            if is_missing_answer(header, name):
                if body:
                    raise ToolFault("git cat-file --batch answered outside its documented format")
                self._trees[folder] = None
            else:
                matched = OBJECT_REPLY.fullmatch(header.decode("ascii", errors="replace"))
                if matched is None:
                    raise ToolFault("git cat-file --batch answered outside its documented format")
                if matched.group(3) is None:  # a submodule entry whose object is absent has no size and no body
                    if matched.group(2) != SUBMODULE or body:
                        raise ToolFault("git cat-file --batch answered outside its documented format")
                    self._trees[folder] = TreeRead(SUBMODULE, {})
                    return self._trees[folder]
                size = int(matched.group(3))
                if len(body) != size + 1 or not body.endswith(b"\n"):
                    raise ToolFault("git cat-file --batch returned a body that does not match its size")
                kind = matched.group(2)
                entries = parse_tree(body[:size], len(matched.group(1)) // 2) if kind == TREE else {}
                self._trees[folder] = TreeRead(kind, entries)
        return self._trees[folder]

    def _settle_missing(self, path: str, final: bool) -> None:
        """`path` was answered `missing`: return when it is absent or names no blob, raise when its tree names it.

        The parent tree decides. An entry that tree names as a blob (or, for a directory that has to be
        entered, as a tree) is an object the store cannot serve: a tool fault. A submodule entry is no blob.
        """
        folder, _, leaf = path.rpartition("/")
        parent = self._read_tree(folder)
        if parent is None:
            if not folder:
                raise ToolFault(f"the root tree of candidate {self._candidate} cannot be served by the object store")
            self._settle_missing(folder, final=False)  # the parent is absent, or named by its own parent and unservable
            return
        if parent.kind != TREE:
            return  # the parent is a file or a submodule entry, so nothing lies below it
        mode = parent.entries.get(leaf.encode(BYTE_CODEC))
        if mode is None or mode == GITLINK_MODE:
            return
        if mode == TREE_MODE and final:
            return  # a directory is no blob
        if mode in BLOB_MODES and not final:
            return  # a file has nothing below it
        if mode == TREE_MODE or mode in BLOB_MODES:
            raise ToolFault(
                f"git cannot serve {printable(path)} at candidate {self._candidate}: "
                "its tree names the entry but the object store does not hold it"
            )
        raise ToolFault(f"the tree of {printable(folder or '.')} names {printable(path)} with the unknown mode {mode}")

    def required_digest(self, path: str) -> str:
        """sha256 of a blob of the candidate; a path that is not a blob there is a tool fault."""
        digest = self.digest_or_absent(path)
        if digest is None:
            raise ToolFault(f"tool path {printable(path)} is not a blob at candidate {self._candidate} (git cat-file)")
        return digest

    def digest_or_absent(self, path: str) -> str | None:
        """sha256 of the blob, or None when the path is absent or not a blob (a red, not a fault)."""
        if path in self._faults:
            raise self._faults[path]
        if path not in self._cache:
            try:
                data = self._blob(path)
            except ToolFault as error:
                self._faults[path] = error
                raise
            self._cache[path] = None if data is None else hashlib.sha256(data).hexdigest()
        return self._cache[path]


# ----------------------------------------------------------------------------- receipt parsing


def decode_receipt(raw: bytes) -> str:
    text = raw.decode(BYTE_CODEC, errors=BYTE_ERRORS)
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.replace("\r\n", "\n")


def parse_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    current: Section | None = None
    in_fence = False
    capturing = False
    collecting_digests = False
    for line in text.split("\n"):
        is_fence = line.rstrip() == FENCE
        if not in_fence and line.startswith("## ") and not is_fence:
            current = Section(heading=line[3:].strip(HORIZONTAL_SPACE))
            sections.append(current)
            capturing = False
            collecting_digests = False
            continue
        if is_fence:
            if not in_fence:
                in_fence = True
                collecting_digests = False
                if current is not None:
                    current.fence_count += 1
                    capturing = current.fence_count == 1
                    if current.fence_count == 2:
                        current.note_repeat("fence")
            else:
                in_fence = False
                if current is not None and capturing:
                    current.block_closed = True
                capturing = False
            continue
        if current is None:
            continue
        if in_fence:
            if capturing:
                current.block_lines.append(line)
            continue
        if collecting_digests:
            if line.startswith("- "):
                current.digest_lines.append(line[2:])
                continue
            collecting_digests = False
        if DIGEST_LABEL.fullmatch(line.rstrip()):
            if current.has_digest_label:
                current.note_repeat("tool_digest")
            current.has_digest_label = True
            collecting_digests = True
            continue
        matched = FIELD_LINE.fullmatch(line.rstrip(HORIZONTAL_SPACE))
        if matched is not None:
            name = matched.group(1)
            if name in current.fields:
                current.note_repeat(name)
            else:
                current.fields[name] = matched.group(2).strip(HORIZONTAL_SPACE)
    return sections


def block_bytes(section: Section) -> bytes:
    """The lines between the fences joined with LF plus a final LF; empty block is zero bytes."""
    if not section.block_lines:
        return b""
    return ("\n".join(section.block_lines) + "\n").encode(BYTE_CODEC, errors=BYTE_ERRORS)


# ----------------------------------------------------------------------------- capture access


def resolve_capture(evidence_root: Path, raw: str) -> Path | None:
    """The capture file named by `raw` inside the evidence root, or None when it escapes or is empty."""
    if raw.endswith(("/", "\\")):
        return None
    normalised = raw.replace("\\", "/")
    if has_bad_text(normalised) or normalised.startswith("/") or DRIVE_PREFIX.match(normalised):
        return None
    relative = posixpath.normpath(normalised)
    if relative in (".", "..") or relative.startswith("../") or posixpath.isabs(relative):
        return None
    root_real = os.path.realpath(evidence_root)
    target_real = os.path.realpath(os.path.join(root_real, relative))
    root_key = os.path.normcase(root_real)
    target_key = os.path.normcase(target_real)
    if target_key == root_key or not target_key.startswith(root_key.rstrip(os.sep) + os.sep):
        return None
    return Path(target_real)


def read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise ToolFault(f"cannot read capture {path}: {error}") from error


def captured_exits(data: bytes) -> list[str]:
    exits: list[str] = []
    for line in data.decode(BYTE_CODEC, errors=BYTE_ERRORS).split("\n"):
        matched = EXIT_LINE.fullmatch(line.rstrip("\r"))
        if matched is not None:
            exits.append(matched.group(1))
    return exits


# ----------------------------------------------------------------------------- checks


def first_difference(left: bytes, right: bytes) -> int:
    limit = min(len(left), len(right))
    for offset in range(limit):
        if left[offset] != right[offset]:
            return offset
    return limit


def check_statement(section: Section, require_cells: Sequence[str]) -> list[Defect]:
    defects: list[Defect] = []
    for name in ("capture", "exit"):
        if name in section.fields:
            defects.append(Defect(DefectCode.STATEMENT_HAS_RUN_FIELDS, section.heading, f"statement carries {name}:"))
    if section.fence_count > 0:
        defects.append(Defect(DefectCode.STATEMENT_HAS_RUN_FIELDS, section.heading, "statement carries a fenced block"))
    if section.heading in require_cells:
        defects.append(
            Defect(DefectCode.STATEMENT_HAS_RUN_FIELDS, section.heading, "statement uses a required cell name")
        )
    return defects


def check_digests(section: Section, args: Arguments, git: GitView, report: Report) -> list[Defect]:
    defects: list[Defect] = []
    listed: dict[str, list[str]] = {}
    for line in section.digest_lines:
        path, equals, value = line.rpartition("=")
        path = path.strip(HORIZONTAL_SPACE)
        value = value.strip(HORIZONTAL_SPACE)
        if not equals:
            defects.append(Defect(DefectCode.TOOL_DIGEST_STALE, section.heading, f"malformed digest line '{line}'"))
            continue
        problem = digest_path_problem(path)
        if problem is not None:
            defects.append(Defect(DefectCode.TOOL_DIGEST_STALE, section.heading, f"digest path '{path}': {problem}"))
            continue
        listed.setdefault(path, []).append(value)
    for tool in args.tools:
        if tool not in listed:
            defects.append(Defect(DefectCode.TOOL_DIGEST_MISSING, section.heading, tool))
    for path, values in listed.items():
        # the values are judged before the lookup and whatever its outcome: they need no git
        well_formed: list[str] = []
        for value in values:
            if DIGEST_VALUE.fullmatch(value) is None:
                defects.append(
                    Defect(
                        DefectCode.TOOL_DIGEST_STALE,
                        section.heading,
                        f"{path} lists '{value}', which is not 64 lower-case hex digits",
                    )
                )
            else:
                well_formed.append(value)
        disagree = len(set(values)) > 1
        if disagree:
            defects.append(
                Defect(
                    DefectCode.TOOL_DIGEST_STALE,
                    section.heading,
                    f"{path} is listed with {len(set(values))} different values",
                )
            )
        try:
            expected = git.digest_or_absent(path)
        except ToolFault as error:  # git cannot serve this line: a fault, and the values were judged above
            report.fault(str(error))
            continue
        if disagree:
            continue  # the disagreement is already a red; no value can be the one the blob gives
        for value in well_formed:
            if expected is None:
                defects.append(
                    Defect(DefectCode.TOOL_DIGEST_STALE, section.heading, f"{path} is not present at candidate {args.candidate}")
                )
            elif value != expected:
                defects.append(
                    Defect(
                        DefectCode.TOOL_DIGEST_STALE,
                        section.heading,
                        f"{path} lists '{value}', the blob at {args.candidate} gives {expected}",
                    )
                )
    return defects


def check_capture(section: Section, evidence_root: Path, report: Report) -> list[Defect]:
    defects: list[Defect] = []
    raw = section.fields.get("capture", "")
    target = resolve_capture(evidence_root, raw)
    if target is None or not target.is_file():
        defects.append(Defect(DefectCode.CAPTURE_MISSING, section.heading, f"'{raw}' is not a file under the evidence root"))
        return defects
    try:
        data = read_bytes(target)
    except ToolFault as error:  # the capture exists but cannot be read: a fault, and the cell's capture is not judged
        report.fault(str(error))
        return defects
    if CR in data:
        defects.append(Defect(DefectCode.CAPTURE_CR, section.heading, f"'{raw}' holds {data.count(CR)} CR bytes"))
    if section.fence_count == 0 or not section.block_closed:
        defects.append(Defect(DefectCode.BLOCK_MISMATCH, section.heading, "no closed four-backtick block"))
    else:
        block = block_bytes(section)
        if block != data:
            defects.append(
                Defect(
                    DefectCode.BLOCK_MISMATCH,
                    section.heading,
                    f"block is {len(block)} bytes, capture '{raw}' is {len(data)} bytes, "
                    f"first difference at byte {first_difference(block, data)}",
                )
            )
    exit_value = section.fields.get("exit")
    if exit_value:
        listed = [part.strip(HORIZONTAL_SPACE) for part in exit_value.split(",")]
        actual = captured_exits(data)
        if listed != actual:
            defects.append(
                Defect(
                    DefectCode.EXIT_MISMATCH,
                    section.heading,
                    f"exit lists {','.join(listed)}, capture holds {','.join(actual) or '(none)'}",
                )
            )
    return defects


def check_run_cell(
    section: Section, args: Arguments, git: GitView, evidence_root: Path | None, report: Report
) -> list[Defect]:
    defects: list[Defect] = []
    for name in REPEAT_ORDER:
        if name in section.repeated:
            what = "second fenced block" if name == "fence" else f"{name}: given more than once"
            defects.append(Defect(DefectCode.FIELD_REPEATED, section.heading, what))
    candidate = section.fields.get("candidate", "")
    if FULL_SHA.fullmatch(candidate) is None:
        defects.append(Defect(DefectCode.CELL_FIELD_MISSING, section.heading, "candidate"))
    elif candidate != args.candidate:
        defects.append(
            Defect(DefectCode.CANDIDATE_MISMATCH, section.heading, f"cell lists '{candidate}', expected {args.candidate}")
        )
    if not section.has_digest_label:
        defects.append(Defect(DefectCode.CELL_FIELD_MISSING, section.heading, "tool_digest:"))
    else:
        defects.extend(check_digests(section, args, git, report))
    if not section.fields.get("capture"):
        defects.append(Defect(DefectCode.CELL_FIELD_MISSING, section.heading, "capture"))
    if not section.fields.get("exit"):
        defects.append(Defect(DefectCode.CELL_FIELD_MISSING, section.heading, "exit"))
    if section.fields.get("capture") and evidence_root is not None:
        defects.extend(check_capture(section, evidence_root, report))
    return defects


def check_receipt(text: str, args: Arguments, git: GitView, evidence_root: Path | None, report: Report) -> None:
    """Judge every section; the reds and the run-cell count go into `report` as they are found."""
    defects = report.defects
    run_names: dict[str, str] = {}
    for section in parse_sections(text):
        value = section.cell_value
        if has_bad_text(section.heading) or (value is not None and has_bad_text(value)):
            defects.append(
                Defect(DefectCode.NOT_RUN, section.heading, "section name or cell name holds a control character or a lone surrogate")
            )
            continue
        if value is None:
            defects.append(Defect(DefectCode.NOT_RUN, section.heading, "section has no cell: line"))
            continue
        if section.is_statement:
            defects.extend(check_statement(section, args.require_cells))
            continue
        if not value:
            defects.append(Defect(DefectCode.NOT_RUN, section.heading, "cell: line names no cell"))
            continue
        report.cells += 1
        if value != section.heading:
            defects.append(
                Defect(DefectCode.CELL_NAME_MISMATCH, section.heading, f"cell: line names '{value}', the heading names '{section.heading}'")
            )
        if value in run_names:
            defects.append(
                Defect(DefectCode.DUPLICATE_CELL, section.heading, f"cell {value} already defined by section {run_names[value]}")
            )
        else:
            run_names[value] = section.heading
        defects.extend(check_run_cell(section, args, git, evidence_root, report))
    if report.cells == 0:
        defects.append(Defect(DefectCode.NO_CELLS, RECEIPT_SECTION, "the receipt holds no run cell"))
    for name in args.require_cells:
        if name not in run_names:
            defects.append(Defect(DefectCode.NOT_RUN, name, "required cell has no run cell"))


# ----------------------------------------------------------------------------- entry points


def read_receipt(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise ToolFault(f"cannot read receipt {path}: {error}") from error


def conclude(report: Report) -> int:
    """Print the outcome: every red on standard output, every fault on standard error, red before fault."""
    if report.defects:
        for defect in report.defects:
            print(defect.render())
        print(f"cells={report.cells} defects={len(report.defects)}")
    for message in report.faults:
        print(f"tool fault: {printable(message)}", file=sys.stderr)
    if report.defects:
        return EXIT_RED
    if report.faults:
        return EXIT_FAULT
    print(f"cells={report.cells} defects=0")
    return EXIT_PASS


def execute(args: Arguments) -> int:
    raw = read_receipt(args.receipt)  # without the receipt no red can be found at all
    report = Report()
    evidence_root: Path | None = args.evidence_root if args.evidence_root is not None else args.receipt.resolve().parent
    if evidence_root is not None and not evidence_root.is_dir():
        report.fault(f"evidence root {evidence_root} is not a readable directory")
        evidence_root = None  # the captures cannot be judged; every other check still runs
    git = GitView(args.repo, args.candidate)
    try:
        git.verify()
    except ToolFault as error:  # git cannot serve any lookup; the checks that need none still run
        git.mark_unusable(error)
        report.fault(str(error))
    for tool in args.tools:
        try:
            git.required_digest(tool)
        except ToolFault as error:
            report.fault(str(error))
    try:
        check_receipt(decode_receipt(raw), args, git, evidence_root, report)
    except ToolFault as error:
        report.fault(str(error))
    except Exception as error:  # an unexpected error is a tool fault, never a red; the reds found so far stand
        report.fault(f"unexpected {type(error).__name__}: {error}")
    return conclude(report)


def main(argv: Sequence[str]) -> int:
    try:
        args = parse_arguments(argv)
    except UsageError as error:
        print(f"{USAGE}\nerror: {error}", file=sys.stderr)
        return EXIT_USAGE
    try:
        return execute(args)
    except ToolFault as error:
        print(f"tool fault: {printable(str(error))}", file=sys.stderr)
        return EXIT_FAULT
    except Exception as error:  # an unexpected error is a tool fault, never a red
        print(f"tool fault: unexpected {type(error).__name__}: {printable(str(error))}", file=sys.stderr)
        return EXIT_FAULT


def configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace", newline="\n")


if __name__ == "__main__":
    configure_streams()
    sys.exit(main(sys.argv[1:]))
