#!/usr/bin/env python3
"""Merge-queue integration script: submit a candidate, land it, read the CI result back.

Usage: integrate.py <submit|land|readback> --config <config> [options]

    submit    --ticket ID --candidate SHA --review PATH --submitter SEAT [--clears TICKET@SHA,...]
    land      (no options)
    readback  (no options)

The configuration is one JSON object (a JSON value per key; unknown, missing and repeated keys,
NaN, Infinity and text-rule breaks are usage errors naming the key): `remote`, `branch`,
`queue_branch` (default `<branch>-queue`), `queue_path`, `spec_command`, `invariant_command`,
`ci_status_command` (exactly one argument equal to `{sha}`) and `timeout_seconds` (default 600).
The queue is `{"entries": [...]}` at `queue_path` on the queue branch; an entry has exactly the
fields ticket, candidate, parent, review, review_candidate, reviewer, submitter, state,
landed_sha, reason and clears, all text. States: QUEUED, LANDED_PENDING_CI, LANDED, LANDED_CI_RED,
CLEARED and BOUNCED (terminal: all but QUEUED and LANDED_PENDING_CI).

Every run works in a fresh integration clone: an empty repository in a temporary directory,
filled by verified fetches of the integration branch, the queue branch and the one candidate being landed, with `transfer.fsckObjects=true` and
`fetch.fsckObjects=true`, so that no object of the run comes from a store a seat can write. The
clone is removed afterwards, also on failure. Every git child runs with `--no-replace-objects`,
`GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_GRAFT_FILE` at a fresh path that does not
exist and `-c core.commitGraph=false`, without the repository-selecting `GIT_*` variables and
without any `GIT_CONFIG*` or `GIT_TEST_*` variable, with `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL` at a path that does not exist, and is looked up in the absolute `PATH` entries only.

submit: reads the review record as the blob at the current remote tip of the branch (never from
the candidate), refuses a key that exists in any state (KEY_EXISTS), refuses a record that does
not approve the candidate (REVIEW_MISMATCH), then writes one QUEUED entry as one commit on the
queue branch, pushed with a lease on the queue-branch sha it read (QUEUE_MOVED when the lease is
lost; nothing is written). land: BLOCKED_BY_CI while an entry is LANDED_PENDING_CI or a
LANDED_CI_RED entry is not cleared by a queued one; otherwise the oldest admissible QUEUED entry
is handled in this order: the record at the tip must admit it (else REVIEW_MISMATCH, and no
configured command runs), the candidate must not be contained in the tip (ALREADY_LANDED), it is
merged into the tip as one merge commit, tip first parent (MERGE_CONFLICT; nothing runs), the specs
and invariants run on the merged tree (SPEC_RED, INVARIANT_RED), and the merge commit is pushed to the
branch together with its queue commit in one atomic push with a lease on each sha read (TIP_MOVED,
QUEUE_MOVED). A bounce is written to the queue branch only. readback: asks `ci_status_command`
about every LANDED_PENDING_CI entry (`green`, `red` or `pending`) and writes the result as one
queue commit pushed with a lease.

Red before fault: every red found is printed on standard output as `<CODE> <subject>: <detail>`
and the run exits 1; each fault is one line on standard error, and the run exits 2 only when it
found no red. A fault that leaves nothing to check (an unreadable configuration, an unreachable
remote, a queue file that breaks its schema) ends the run at once. Every printed subject is
escaped to one line. Exit codes: 0 landed, recorded or nothing to do; 1 an entry bounced or a
precondition is red; 2 git, the remote or a configured command cannot serve the run (also an
unexpected error, an interrupt, or a standard output or error that cannot be written); 3 usage.
"""
from __future__ import annotations

import ctypes
import io
import json
import math
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from typing import TextIO

USAGE = "usage: integrate.py <submit|land|readback> --config <config> [options]"

EXIT_OK = 0
EXIT_RED = 1
EXIT_FAULT = 2
EXIT_USAGE = 3

SUBCOMMANDS = ("submit", "land", "readback")

# Queue states.
QUEUED = "QUEUED"
LANDED_PENDING_CI = "LANDED_PENDING_CI"
LANDED = "LANDED"
LANDED_CI_RED = "LANDED_CI_RED"
CLEARED = "CLEARED"
BOUNCED = "BOUNCED"
STATES = (QUEUED, LANDED_PENDING_CI, LANDED, LANDED_CI_RED, CLEARED, BOUNCED)
LANDED_STATES = (LANDED_PENDING_CI, LANDED, LANDED_CI_RED, CLEARED)

# Reds (exit 1). The first five are written to the queue as the reason of a BOUNCED entry.
REVIEW_MISMATCH = "REVIEW_MISMATCH"
MERGE_CONFLICT = "MERGE_CONFLICT"
ALREADY_LANDED = "ALREADY_LANDED"
SPEC_RED = "SPEC_RED"
INVARIANT_RED = "INVARIANT_RED"
TIP_MOVED = "TIP_MOVED"
BOUNCE_REASONS = (REVIEW_MISMATCH, ALREADY_LANDED, MERGE_CONFLICT, SPEC_RED, INVARIANT_RED, TIP_MOVED)
# Reds that write nothing.
KEY_EXISTS = "KEY_EXISTS"
QUEUE_MOVED = "QUEUE_MOVED"
BLOCKED_BY_CI = "BLOCKED_BY_CI"

ENTRY_FIELDS = (
    "ticket",
    "candidate",
    "parent",
    "review",
    "review_candidate",
    "reviewer",
    "submitter",
    "state",
    "landed_sha",
    "reason",
    "clears",
)
REQUIRED_CONFIG_KEYS = ("remote", "branch", "queue_path", "spec_command", "invariant_command", "ci_status_command")
OPTIONAL_CONFIG_KEYS = ("queue_branch", "timeout_seconds")
SHA_PLACEHOLDER = "{sha}"
DEFAULT_TIMEOUT_SECONDS = 600
MAX_TIMEOUT_SECONDS = 86400
GIT_TIMEOUT_SECONDS = 900.0
REAP_SECONDS = 30.0
MAX_PATH_BYTES = 1024
SHOWN = 200

TICKET_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SHA_TEXT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
SEAT_ID = re.compile(r"seat:[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
BRANCH_TEXT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,199}")
DRIVE_LETTER = re.compile(r"[A-Za-z]:")
BATCH_SUFFIXES = (".bat", ".cmd")
DEFAULT_PATHEXT = ".COM;.EXE;.BAT;.CMD"
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([^\s`]*)[^`]*$")
FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
BLOCK_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*?)[ \t]*$")
SPEC_BASENAME = re.compile(rb"(?:^|/)test_[^/]*\.py$")
PAGES_PATH = "pages.json"
# Variables that select another repository, history, objects or settings than the clone itself holds
# (the shared list of the evidence gate: its thirteen names, every GIT_CONFIG* and every GIT_TEST_* name).
GIT_REMOVED = frozenset(
    (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_SHALLOW_FILE",
        "GIT_REPLACE_REF_BASE",
        "GIT_GRAFT_FILE",
        "GIT_PREFIX",
        "GIT_QUARANTINE_PATH",
    )
)
GIT_REMOVED_PREFIXES = ("GIT_CONFIG", "GIT_TEST_")
IDENTITY = {
    "GIT_AUTHOR_NAME": "merge-queue",
    "GIT_AUTHOR_EMAIL": "merge-queue@integrate.invalid",
    "GIT_COMMITTER_NAME": "merge-queue",
    "GIT_COMMITTER_EMAIL": "merge-queue@integrate.invalid",
}


class UsageError(Exception):
    """The arguments or the configuration are wrong: exit 3."""


class Fault(Exception):
    """The run cannot be served (git, the remote, a command, a file): exit 2."""


class JsonInputError(ValueError):
    """A JSON text that is not acceptable input."""


# ----------------------------------------------------------------------------- text


def escape(text: str) -> str:
    """Make `text` one printable line: backslash and every non-printable character escaped."""
    parts: list[str] = []
    for char in text:
        code = ord(char)
        if char == "\\":
            parts.append("\\\\")
        elif char.isprintable():
            parts.append(char)
        elif code <= 0xFF:
            parts.append(f"\\x{code:02x}")
        elif code <= 0xFFFF:
            parts.append(f"\\u{code:04x}")
        else:
            parts.append(f"\\U{code:08x}")
    return "".join(parts)


def printable_line(text: str) -> str:
    """The last safety net before output: a non-printable character left in `text` is escaped, a backslash is kept."""
    return "".join(char if char.isprintable() else escape(char) for char in text)


def shown(text: str) -> str:
    """`text` escaped and cut to a length that fits one line."""
    cut = text if len(text) <= SHOWN else text[:SHOWN] + "..."
    return escape(cut)


def bad_character(text: str) -> str | None:
    """Name the first lone surrogate or control character in `text`, else None."""
    for char in text:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            return f"a lone surrogate (U+{code:04X})"
        if code <= 0x1F or code == 0x7F:
            return f"a control character (U+{code:04X})"
    return None


def path_problem(path: str) -> str | None:
    """Why `path` is not a canonical repository-relative path, or None when it is canonical."""
    if not path:
        return "empty path"
    bad = bad_character(path)
    if bad is not None:
        return f"path holds {bad}"
    if len(path.encode("utf-8")) > MAX_PATH_BYTES:
        return f"path is longer than {MAX_PATH_BYTES} bytes"
    if "\\" in path:
        return "path holds a backslash"
    if path.startswith("/"):
        return "absolute path"
    if DRIVE_LETTER.match(path):
        return "path has a drive letter"
    if path.startswith(":"):
        return "path starts with ':' (pathspec magic)"
    if path.endswith("/"):
        return "path ends with a slash"
    for segment in path.split("/"):
        if not segment:
            return "path has an empty segment"
        if segment == ".":
            return "path has a '.' segment"
        if segment == "..":
            return "path has a '..' segment"
    return None


def branch_problem(name: str) -> str | None:
    """Why `name` is not a branch name this script accepts, or None."""
    if BRANCH_TEXT.fullmatch(name) is None:
        return "not a plain branch name (letters, digits, dot, underscore, hyphen and slash, starting with a letter or digit)"
    if name == "HEAD" or name.endswith("/") or name.endswith(".") or ".." in name or "//" in name:
        return "not an acceptable branch name"
    for segment in name.split("/"):
        if segment.startswith(".") or segment.endswith(".lock"):
            return "a segment starts with a dot or ends with .lock"
    return None


# ----------------------------------------------------------------------------- JSON


@dataclass(frozen=True)
class Refused:
    """Stands in a parsed document for a value JSON text may not hold (NaN, Infinity, a number out of range)."""

    why: str


def parse_json(raw: str, mark_refused: bool = False) -> object:
    """Parse `raw`; a repeated key, NaN, Infinity, a number out of range or too deep nesting is a JsonInputError.

    With `mark_refused` a NaN, an Infinity or a number out of range is left in the document as a `Refused`
    value instead, so that the caller can name the key that holds it."""

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise JsonInputError(f'repeated key "{shown(key)}"')
            result[key] = value
        return result

    def refuse_constant(name: str) -> object:
        if mark_refused:
            return Refused(f"{name}, which is not allowed")
        raise JsonInputError(f"{name} is not allowed")

    def finite_float(text: str) -> object:
        value = float(text)
        if not math.isfinite(value):
            if mark_refused:
                return Refused("a number out of range")
            raise JsonInputError("a number is out of range")
        return value

    try:
        value: object = json.loads(raw, object_pairs_hook=pairs, parse_constant=refuse_constant, parse_float=finite_float)
    except JsonInputError:
        raise
    except RecursionError:
        raise JsonInputError("nesting is too deep to parse") from None
    except ValueError as exc:
        raise JsonInputError(f"not valid JSON ({shown(str(exc))})") from None
    return value


def first_bad_text(value: object) -> str | None:
    """The first lone surrogate or control character in any string (key or value) of a parsed JSON value,
    or the reason of the first `Refused` value."""
    stack: list[object] = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, Refused):
            return item.why
        if isinstance(item, str):
            bad = bad_character(item)
            if bad is not None:
                return bad
        elif isinstance(item, dict):
            for key, child in item.items():
                stack.append(key)
                stack.append(child)
        elif isinstance(item, list):
            stack.extend(item)
    return None


# ----------------------------------------------------------------------------- data


@dataclass(frozen=True)
class Config:
    remote: str
    branch: str
    queue_branch: str
    queue_path: str
    spec_command: tuple[str, ...]
    invariant_command: tuple[str, ...]
    ci_status_command: tuple[str, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class QueueEntry:
    ticket: str
    candidate: str
    parent: str
    review: str
    review_candidate: str
    reviewer: str
    submitter: str
    state: str
    landed_sha: str
    reason: str
    clears: str

    @property
    def key(self) -> str:
        return f"{self.ticket}@{self.candidate}"

    @property
    def clear_keys(self) -> tuple[str, ...]:
        return tuple(self.clears.split(",")) if self.clears else ()

    def as_json(self) -> dict[str, str]:
        return {
            "ticket": self.ticket,
            "candidate": self.candidate,
            "parent": self.parent,
            "review": self.review,
            "review_candidate": self.review_candidate,
            "reviewer": self.reviewer,
            "submitter": self.submitter,
            "state": self.state,
            "landed_sha": self.landed_sha,
            "reason": self.reason,
            "clears": self.clears,
        }


@dataclass(frozen=True)
class ReviewVerdict:
    candidate: str
    verdict: str
    reviewer: str
    reviewed_at: str


@dataclass(frozen=True)
class Bounce:
    reason: str
    detail: str


@dataclass(frozen=True)
class ReviewCheck:
    verdict: ReviewVerdict | None
    problems: tuple[str, ...]


@dataclass(frozen=True)
class SubmitArguments:
    ticket: str
    candidate: str
    review: str
    submitter: str
    clears: str


@dataclass(frozen=True)
class Arguments:
    subcommand: str
    config: str
    submit: SubmitArguments | None


class Report:
    """What a run prints: reds and notes on standard output, faults on standard error."""

    def __init__(self) -> None:
        self.out: list[str] = []
        self.err: list[str] = []
        self.reds = 0
        self.faults = 0

    def note(self, line: str) -> None:
        self.out.append(line)

    def red(self, code: str, subject: str, detail: str) -> None:
        self.reds += 1
        self.out.append(f"{code} {escape(subject)}: {detail}")

    def fault(self, text: str) -> None:
        self.faults += 1
        self.err.append(f"integrate.py: tool fault: {text}")

    @property
    def code(self) -> int:
        if self.reds:
            return EXIT_RED
        if self.faults:
            return EXIT_FAULT
        return EXIT_OK


# ----------------------------------------------------------------------------- configuration


def _config_error(key: str, problem: str) -> UsageError:
    return UsageError(f"config key `{escape(key)}`: {problem}")


def _command_value(key: str, value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise _config_error(key, "must be a non-empty JSON array of strings")
    argv: list[str] = []
    for element in value:
        if not isinstance(element, str):
            raise _config_error(key, "must hold only strings")
        argv.append(element)
    if not argv[0]:
        raise _config_error(key, "the first element must not be empty")
    return tuple(argv)


def _text_value(key: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise _config_error(key, "must be a non-empty JSON string")
    return value


def parse_config(raw: bytes) -> Config:
    """Turn the bytes of a configuration file into a Config; UsageError names the key at fault."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise UsageError("config is not UTF-8 text") from None
    try:
        document = parse_json(text, mark_refused=True)
    except JsonInputError as exc:
        raise UsageError(f"config: {exc}") from None
    if isinstance(document, Refused):
        raise UsageError(f"config: {document.why}")
    if not isinstance(document, dict):
        raise UsageError("config must be one JSON object")
    for name, value in document.items():
        bad = first_bad_text(name)
        if bad is not None:
            raise _config_error(name, f"the key holds {bad}")
        bad = first_bad_text(value)
        if bad is not None:
            raise _config_error(name, f"the value holds {bad}")
    for key in document:
        if key not in REQUIRED_CONFIG_KEYS and key not in OPTIONAL_CONFIG_KEYS:
            raise _config_error(key, "unknown key")
    for key in REQUIRED_CONFIG_KEYS:
        if key not in document:
            raise _config_error(key, "missing key")
    remote = _text_value("remote", document["remote"])
    if remote.startswith("-"):
        raise _config_error("remote", "must not start with a hyphen")
    branch = _text_value("branch", document["branch"])
    problem = branch_problem(branch)
    if problem is not None:
        raise _config_error("branch", problem)
    queue_branch = branch + "-queue"
    if "queue_branch" in document:
        queue_branch = _text_value("queue_branch", document["queue_branch"])
        problem = branch_problem(queue_branch)
        if problem is not None:
            raise _config_error("queue_branch", problem)
    if queue_branch == branch:
        raise _config_error("queue_branch", "must differ from branch")
    queue_path = _text_value("queue_path", document["queue_path"])
    problem = path_problem(queue_path)
    if problem is not None:
        raise _config_error("queue_path", problem)
    spec_command = _command_value("spec_command", document["spec_command"])
    invariant_command = _command_value("invariant_command", document["invariant_command"])
    ci_status_command = _command_value("ci_status_command", document["ci_status_command"])
    if ci_status_command[0] == SHA_PLACEHOLDER or ci_status_command[1:].count(SHA_PLACEHOLDER) != 1:
        raise _config_error("ci_status_command", f"must hold exactly one argument equal to {SHA_PLACEHOLDER} after the program")
    timeout_seconds = DEFAULT_TIMEOUT_SECONDS
    if "timeout_seconds" in document:
        number = document["timeout_seconds"]
        if isinstance(number, bool) or not isinstance(number, int) or number <= 0 or number > MAX_TIMEOUT_SECONDS:
            raise _config_error("timeout_seconds", f"must be an integer from 1 to {MAX_TIMEOUT_SECONDS}")
        timeout_seconds = number
    return Config(
        remote=remote,
        branch=branch,
        queue_branch=queue_branch,
        queue_path=queue_path,
        spec_command=spec_command,
        invariant_command=invariant_command,
        ci_status_command=ci_status_command,
        timeout_seconds=timeout_seconds,
    )


def read_file(path: str, what: str) -> bytes:
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except (OSError, ValueError) as exc:
        reason = exc.strerror if isinstance(exc, OSError) and exc.strerror else type(exc).__name__
        raise Fault(f"cannot read {what} {shown(path)}: {shown(reason)}") from None


# ----------------------------------------------------------------------------- arguments


def _option_value(args: Sequence[str], index: int, name: str) -> str:
    if index + 1 >= len(args) or args[index + 1].startswith("--"):
        raise UsageError(f"{name} needs a value")
    return args[index + 1]


def _clears_problem(value: str) -> str | None:
    if not value:
        return "--clears must not be empty; leave the option out for no keys"
    seen: set[str] = set()
    for key in value.split(","):
        ticket, at, sha = key.partition("@")
        if not at or TICKET_ID.fullmatch(ticket) is None or SHA_TEXT.fullmatch(sha) is None:
            return f"--clears holds {shown(key)}, which is not <ticket>@<full lower-case sha>"
        if key in seen:
            return f"--clears names {shown(key)} twice"
        seen.add(key)
    return None


def parse_arguments(args: Sequence[str]) -> Arguments:
    for number, arg in enumerate(args, start=1):
        bad = bad_character(arg)
        if bad is not None:
            raise UsageError(f"argument {number} holds {bad}")
    if not args:
        raise UsageError("a subcommand is required")
    subcommand = args[0]
    if subcommand not in SUBCOMMANDS:
        raise UsageError(f"unknown subcommand {shown(subcommand)}")
    allowed = ["--config"]
    if subcommand == "submit":
        allowed += ["--ticket", "--candidate", "--review", "--submitter", "--clears"]
    values: dict[str, str] = {}
    index = 1
    while index < len(args):
        name = args[index]
        if name not in allowed:
            if name.startswith("-"):
                raise UsageError(f"unknown option {shown(name)} for {subcommand}")
            raise UsageError(f"unexpected argument {shown(name)}")
        if name in values:
            raise UsageError(f"{name} is given twice")
        values[name] = _option_value(args, index, name)
        index += 2
    config = values.get("--config", "")
    if not config:
        raise UsageError("--config <config> is required")
    if subcommand != "submit":
        return Arguments(subcommand, config, None)
    for name in ("--ticket", "--candidate", "--review", "--submitter"):
        if not values.get(name):
            raise UsageError(f"{name} is required")
    ticket, candidate = values["--ticket"], values["--candidate"]
    review, submitter = values["--review"], values["--submitter"]
    if TICKET_ID.fullmatch(ticket) is None:
        raise UsageError(f"--ticket {shown(ticket)} is not a ticket id (letters, digits, dot, underscore, hyphen)")
    if SHA_TEXT.fullmatch(candidate) is None:
        raise UsageError(f"--candidate {shown(candidate)} is not a full lower-case sha")
    problem = path_problem(review)
    if problem is not None:
        raise UsageError(f"--review: {problem}")
    if SEAT_ID.fullmatch(submitter) is None:
        raise UsageError(f"--submitter {shown(submitter)} is not seat:<profile>/<run-id>")
    clears = values.get("--clears", "")
    if "--clears" in values:
        problem = _clears_problem(clears)
        if problem is not None:
            raise UsageError(problem)
    return Arguments(subcommand, config, SubmitArguments(ticket, candidate, review, submitter, clears))


# ----------------------------------------------------------------------------- queue file


def _entry_error(index: int, ticket: str, field: str, problem: str) -> Fault:
    label = f"entry {index + 1}" + (f" ({shown(ticket)})" if ticket else "")
    return Fault(f"queue file: {label}, field {field}: {problem}")


def parse_queue(raw: bytes, width: int) -> list[QueueEntry]:
    """Parse a queue file; a file that breaks the schema is a Fault naming the entry and the field."""
    if raw.startswith(b"\xef\xbb\xbf"):
        raise Fault("queue file: starts with a byte order mark")
    if b"\r" in raw:
        raise Fault("queue file: holds a carriage return (the file is LF only)")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Fault("queue file: not UTF-8 text") from None
    try:
        document = parse_json(text)
    except JsonInputError as exc:
        raise Fault(f"queue file: {exc}") from None
    bad = first_bad_text(document)
    if bad is not None:
        raise Fault(f"queue file: holds {bad}")
    if not isinstance(document, dict) or list(document.keys()) != ["entries"]:
        raise Fault('queue file: must be one object with the one key "entries"')
    rows = document["entries"]
    if not isinstance(rows, list):
        raise Fault("queue file: entries must be a list")
    entries: list[QueueEntry] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise _entry_error(index, "", "entry", "must be an object")
        raw_ticket = row.get("ticket")
        label = raw_ticket if isinstance(raw_ticket, str) else ""
        for name in row:
            if name not in ENTRY_FIELDS:
                raise _entry_error(index, label, shown(name), "unknown field")
        values: dict[str, str] = {}
        for name in ENTRY_FIELDS:
            if name not in row:
                raise _entry_error(index, label, name, "missing field")
            value = row[name]
            if not isinstance(value, str):
                raise _entry_error(index, label, name, "must be a string")
            values[name] = value
        entry = QueueEntry(**values)
        _check_entry(index, entry, width)
        if entry.key in seen:
            raise _entry_error(index, entry.ticket, "candidate", "the key (ticket, candidate) is repeated")
        seen.add(entry.key)
        entries.append(entry)
    return entries


def _check_entry(index: int, entry: QueueEntry, width: int) -> None:
    def fail(field: str, problem: str) -> Fault:
        return _entry_error(index, entry.ticket, field, problem)

    if TICKET_ID.fullmatch(entry.ticket) is None:
        raise fail("ticket", "not a ticket id")
    for name in ("candidate", "parent", "review_candidate"):
        value = getattr(entry, name)
        if SHA_TEXT.fullmatch(value) is None or len(value) != width:
            raise fail(name, f"not a full lower-case sha of {width} hex digits")
    problem = path_problem(entry.review)
    if problem is not None:
        raise fail("review", problem)
    for name in ("reviewer", "submitter"):
        if SEAT_ID.fullmatch(getattr(entry, name)) is None:
            raise fail(name, "not seat:<profile>/<run-id>")
    if entry.state not in STATES:
        raise fail("state", "not a queue state")
    if entry.state in LANDED_STATES:
        if SHA_TEXT.fullmatch(entry.landed_sha) is None or len(entry.landed_sha) != width:
            raise fail("landed_sha", f"not a full lower-case sha of {width} hex digits")
    elif entry.landed_sha:
        raise fail("landed_sha", f"must be empty in state {entry.state}")
    if entry.state == BOUNCED:
        if entry.reason not in BOUNCE_REASONS:
            raise fail("reason", "not a bounce reason")
    elif entry.reason:
        raise fail("reason", f"must be empty in state {entry.state}")
    if entry.clears and _clears_problem(entry.clears) is not None:
        raise fail("clears", "not a comma-separated list of <ticket>@<sha> keys")
    for key in entry.clear_keys:
        if len(key.partition("@")[2]) != width:
            raise fail("clears", f"a key does not hold a sha of {width} hex digits")


def serialize_queue(entries: Sequence[QueueEntry]) -> bytes:
    document = {"entries": [entry.as_json() for entry in entries]}
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


# ----------------------------------------------------------------------------- review record


@dataclass(frozen=True)
class Block:
    tag: str
    fields: Mapping[str, tuple[str, ...]]
    problem: str | None


def parse_blocks(text: str) -> list[Block]:
    """Every fenced block of `text` tagged review-verdict or convergence-disposition, in order of appearance."""
    blocks: list[Block] = []
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        opened = FENCE_OPEN.match(lines[index].rstrip("\r"))
        index += 1
        if opened is None:
            continue
        fence, tag = opened.group(1), opened.group(2)
        body: list[str] = []
        closed = False
        while index < len(lines):
            line = lines[index].rstrip("\r")
            index += 1
            ender = FENCE_CLOSE.match(line)
            if ender is not None and ender.group(1)[0] == fence[0] and len(ender.group(1)) >= len(fence):
                closed = True
                break
            body.append(line)
        if tag in ("review-verdict", "convergence-disposition"):
            blocks.append(_read_block(tag, body, closed))
    return blocks


def _read_block(tag: str, body: Sequence[str], closed: bool) -> Block:
    fields: dict[str, list[str]] = {}
    problem: str | None = None if closed else "the block is not closed"
    for line in body:
        if not line.strip(" \t"):
            continue
        if line[0] in " \t-":
            continue
        matched = BLOCK_LINE.match(line)
        if matched is None:
            problem = problem or f"line {shown(line)} is not `key: value`"
            continue
        name, value = matched.group(1), matched.group(2)
        bad = bad_character(value)
        if bad is not None:
            problem = problem or f"the value of {name} holds {bad}"
        if name in fields:
            problem = problem or f"the key {name} is repeated"
        fields.setdefault(name, []).append(value)
    return Block(tag, {name: tuple(values) for name, values in fields.items()}, problem)


def _single(block: Block, name: str) -> str | None:
    values = block.fields.get(name, ())
    return values[0] if len(values) == 1 else None


def check_review(
    record: bytes | None,
    candidate: str,
    submitter: str,
    row_review_candidate: str | None,
    row_reviewer: str | None,
) -> ReviewCheck:
    """Judge a review record for `candidate`; every problem found is returned, none is raised.

    `row_review_candidate` and `row_reviewer` are the copies a queue row carries (None at submit time).
    """
    if record is None:
        return ReviewCheck(None, ("the review record does not exist at the integration tip",))
    try:
        text = record.decode("utf-8")
    except UnicodeDecodeError:
        return ReviewCheck(None, ("the review record is not UTF-8 text",))
    blocks = parse_blocks(text)
    verdict_blocks = [block for block in blocks if block.tag == "review-verdict"]
    problems: list[str] = []
    if any(submitter in block.fields.get("reviewer", ()) for block in verdict_blocks):
        problems.append("the submitter appears as reviewer in a review-verdict block of the record")
    matching = [block for block in verdict_blocks if candidate in block.fields.get("candidate", ())]
    if not matching:
        problems.append("the record holds no review-verdict block for the candidate")
        return ReviewCheck(None, tuple(problems))
    last = matching[-1]
    if last.problem is not None:
        problems.append(f"the last review-verdict block for the candidate is malformed ({last.problem})")
        return ReviewCheck(None, tuple(problems))
    block_candidate = _single(last, "candidate")
    verdict = _single(last, "verdict")
    reviewer = _single(last, "reviewer")
    if block_candidate != candidate or verdict is None or reviewer is None:
        problems.append("the last review-verdict block for the candidate lacks one candidate, verdict and reviewer line each")
        return ReviewCheck(None, tuple(problems))
    if verdict == "APPROVED":
        pass
    elif verdict == "CONVERGENCE_REVIEW_REQUIRED":
        dispositions = [
            block
            for block in blocks
            if block.tag == "convergence-disposition" and candidate in block.fields.get("candidate", ())
        ]
        if not dispositions:
            problems.append("the verdict is CONVERGENCE_REVIEW_REQUIRED and the record holds no convergence-disposition for the candidate")
        elif dispositions[-1].problem is not None or _single(dispositions[-1], "disposition") != "APPROVED":
            problems.append("the convergence-disposition for the candidate is malformed or does not say disposition: APPROVED")
    else:
        problems.append(f"the verdict is {shown(verdict)}, not APPROVED")
    if SEAT_ID.fullmatch(reviewer) is None:
        problems.append(f"the reviewer {shown(reviewer)} is not seat:<profile>/<run-id>")
    elif reviewer == submitter:
        problems.append("the submitter and the reviewer are the same seat")
    if row_review_candidate is not None and row_review_candidate != block_candidate:
        problems.append("the row's review_candidate differs from the record")
    if row_reviewer is not None and row_reviewer != reviewer:
        problems.append("the row's reviewer differs from the record")
    result = ReviewVerdict(block_candidate, verdict, reviewer, (_single(last, "reviewed_at") or ""))
    return ReviewCheck(result if not problems else None, tuple(problems))


# ----------------------------------------------------------------------------- affected specs


@dataclass(frozen=True)
class Page:
    paths: tuple[str, ...]


class PagesError(ValueError):
    """The page registry cannot be read."""


def parse_pages(raw: bytes) -> list[Page]:
    """Read the page registry: a list of page objects, or an object holding that list under `pages`."""
    try:
        document = parse_json(raw.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise PagesError("not UTF-8 text") from None
    except JsonInputError as exc:
        raise PagesError(str(exc)) from None
    bad = first_bad_text(document)
    if bad is not None:
        raise PagesError(f"holds {bad}")
    rows = document.get("pages") if isinstance(document, dict) else document
    if not isinstance(rows, list):
        raise PagesError("must be a list of pages or an object with a pages list")
    pages: list[Page] = []
    for number, row in enumerate(rows, start=1):
        paths = row.get("paths") if isinstance(row, dict) else None
        if not isinstance(paths, list):
            raise PagesError(f"page {number} has no paths list")
        owned: list[str] = []
        for path in paths:
            if not isinstance(path, str):
                raise PagesError(f"page {number} holds a path that is not a string")
            problem = path_problem(path[:-1] if path.endswith("/") else path)
            if problem is not None:
                raise PagesError(f"page {number}: {problem}")
            owned.append(path)
        pages.append(Page(tuple(owned)))
    return pages


def covers(entry: str, path: str) -> bool:
    """A directory entry (trailing slash) covers every path below it by whole segment; a file entry covers itself."""
    if entry.endswith("/"):
        return path.startswith(entry)
    return path == entry


def affected_specs(changed: Sequence[str], specs: Mapping[str, str], pages: Sequence[Page]) -> list[str]:
    """The specs a change touches: the spec itself changed, or its text names a changed path, or a page owns both."""
    affected: set[str] = set()
    changed_set = set(changed)
    for path in specs:
        if path in changed_set:
            affected.add(path)
    if changed:
        ordered = sorted(changed_set, key=lambda item: (-len(item), item))
        alternatives = "|".join(re.escape(path) for path in ordered)
        naming = re.compile(rf"(?<![A-Za-z0-9._-])(?:{alternatives})(?![A-Za-z0-9_-]|[./][A-Za-z0-9_])")
        for path, text in specs.items():
            if naming.search(text) is not None:
                affected.add(path)
    for page in pages:
        if any(covers(entry, path) for entry in page.paths for path in changed_set):
            for spec in specs:
                if any(covers(entry, spec) for entry in page.paths):
                    affected.add(spec)
    return sorted(affected)


# ----------------------------------------------------------------------------- processes


@dataclass(frozen=True)
class Completed:
    code: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool
    launch_error: str | None
    refusal: str | None = None


def _system_taskkill() -> str | None:
    """The absolute path of the system's taskkill program (Windows only), else None; it is never searched for."""
    if sys.platform != "win32":
        return None
    buffer = ctypes.create_unicode_buffer(32768)
    length = int(ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer)))
    if length <= 0 or length >= len(buffer):
        return None
    path = os.path.join(buffer.value, "taskkill.exe")
    return path if os.path.isabs(path) and os.path.isfile(path) else None


def kill_tree(process: subprocess.Popen[bytes]) -> None:
    """Kill the process and every process it started, then reap it."""
    if sys.platform == "win32":
        taskkill = _system_taskkill()
        if taskkill is not None:
            try:
                subprocess.run(
                    [taskkill, "/F", "/T", "/PID", str(process.pid)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=REAP_SECONDS,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError):
                pass
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        process.kill()
    except OSError:
        pass
    try:
        process.wait(timeout=REAP_SECONDS)
    except subprocess.TimeoutExpired:
        pass


def run_process(
    argv: Sequence[str],
    cwd: str,
    env: Mapping[str, str],
    timeout: float,
    stdin: bytes | None = None,
) -> Completed:
    """Run `argv` without a shell; output goes to temporary files; a run past `timeout` is killed with its tree."""
    with tempfile.TemporaryFile() as out_sink, tempfile.TemporaryFile() as err_sink, tempfile.TemporaryFile() as in_source:
        if stdin is not None:
            in_source.write(stdin)
            in_source.flush()
            in_source.seek(0)
        try:
            process = subprocess.Popen(
                list(argv),
                stdin=in_source if stdin is not None else subprocess.DEVNULL,
                stdout=out_sink,
                stderr=err_sink,
                cwd=cwd,
                env=dict(env),
                shell=False,
                start_new_session=sys.platform != "win32",
            )
        except (OSError, ValueError) as exc:
            reason = exc.strerror if isinstance(exc, OSError) and exc.strerror else str(exc)
            return Completed(None, b"", b"", False, f"{type(exc).__name__}: {reason}")
        timed_out = False
        code: int | None = None
        try:
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                kill_tree(process)
            out_sink.seek(0)
            err_sink.seek(0)
            return Completed(code, out_sink.read(), err_sink.read(), timed_out, None)
        except BaseException:
            if process.poll() is None:
                kill_tree(process)
            raise


# ----------------------------------------------------------------------------- argv0 resolution (the rules of the preflight gate)


def _is_batch_file(path: str) -> bool:
    return path.rstrip(" .").lower().endswith(BATCH_SUFFIXES)


def _fully_absolute(path: str) -> bool:
    """Absolute on every platform; on Windows a drive (or share) is part of it, a rooted name alone is not."""
    if not os.path.isabs(path):
        return False
    if sys.platform != "win32":
        return True
    drive, rest = os.path.splitdrive(path)
    return drive != "" and rest[:1] in ("\\", "/")


def _names_a_drive(name: str) -> bool:
    if DRIVE_LETTER.match(name) is not None or name.startswith("\\\\"):
        return True
    return sys.platform == "win32" and os.path.splitdrive(name)[0] != ""


def _search_directories() -> list[str]:
    """The PATH entries that name a directory without the help of the current directory."""
    directories: list[str] = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if sys.platform == "win32":
            entry = entry.strip().strip('"')
        if entry and _fully_absolute(entry):
            directories.append(entry)
    return directories


def _candidate_names(name: str) -> list[str]:
    if sys.platform != "win32":
        return [name]
    extensions = [ext.lower() for ext in os.environ.get("PATHEXT", DEFAULT_PATHEXT).split(";") if ext]
    if not extensions:
        extensions = [ext.lower() for ext in DEFAULT_PATHEXT.split(";")]
    if name.lower().endswith(tuple(extensions)):
        return [name]
    return [name + ext for ext in extensions]


def _is_program_file(path: str) -> bool:
    if not os.path.isfile(path):
        return False
    return sys.platform == "win32" or os.access(path, os.X_OK)


class ArgvZeroError(Exception):
    """The program name cannot be turned into a program this script may run."""


def resolve_argv0(argv0: str, base: str) -> str:
    """Turn `argv0` into the absolute program path to launch; raise ArgvZeroError when it must not run."""
    if _names_a_drive(argv0) and not _fully_absolute(argv0):
        raise ArgvZeroError(f'cannot be resolved (the name "{shown(argv0)}" is relative to a drive)')
    if "/" in argv0 or "\\" in argv0:
        program = argv0 if _fully_absolute(argv0) else os.path.abspath(os.path.join(base, argv0))
    else:
        found: str | None = None
        for directory in _search_directories():
            for candidate in _candidate_names(argv0):
                path = os.path.join(directory, candidate)
                if _is_program_file(path):
                    found = path
                    break
            if found is not None:
                break
        if found is None:
            raise ArgvZeroError(f'cannot be resolved (the name "{shown(argv0)}" is not found in PATH)')
        program = found
    if _is_batch_file(program):
        raise ArgvZeroError(f'is refused ("{shown(argv0)}" is a batch file; name the interpreter or the executable instead)')
    return program


# ----------------------------------------------------------------------------- git


def git_environment(graft_path: str, extra: Mapping[str, str] | None = None) -> dict[str, str]:
    """The environment of a git child (and of a configured command): nothing that selects other history or settings."""
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() not in GIT_REMOVED and not name.upper().startswith(GIT_REMOVED_PREFIXES)
    }
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = graft_path + ".global-config"
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    environment["GIT_GRAFT_FILE"] = graft_path
    environment["GIT_TERMINAL_PROMPT"] = "0"
    if extra:
        environment.update(extra)
    return environment


def find_git() -> str:
    """The git program, looked up in the absolute PATH entries only."""
    for directory in _search_directories():
        for candidate in _candidate_names("git"):
            path = os.path.join(directory, candidate)
            if _is_program_file(path) and not _is_batch_file(path):
                return path
    raise Fault("git cannot be found in the PATH entries")


@dataclass(frozen=True)
class BlobRead:
    kind: str  # "missing", "blob" or "other"
    data: bytes


class Git:
    """Runs git inside one directory with the scrubbed environment and the options every child gets."""

    def __init__(self, exe: str, cwd: str, scratch: str) -> None:
        self.exe = exe
        self.cwd = cwd
        self.scratch = scratch

    def _fresh(self, label: str) -> str:
        return os.path.join(self.scratch, f"{label}-{uuid.uuid4().hex}")

    def run(
        self,
        args: Sequence[str],
        *,
        options: Sequence[str] = (),
        stdin: bytes | None = None,
        check: bool = True,
        extra_env: Mapping[str, str] | None = None,
    ) -> Completed:
        command = [
            self.exe,
            "--no-replace-objects",
            "-c",
            "core.commitGraph=false",
            "-c",
            "core.quotepath=false",
            "-c",
            "core.autocrlf=false",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "gc.auto=0",
            "-c",
            "maintenance.auto=false",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "protocol.ext.allow=never",
            "-c",
            f"core.hooksPath={self._fresh('no-hooks')}",
            "-C",
            self.cwd,
            *options,
            *args,
        ]
        done = run_process(command, self.cwd, git_environment(self._fresh("no-graft"), extra_env), GIT_TIMEOUT_SECONDS, stdin)
        label = args[0]
        if done.launch_error is not None:
            raise Fault(f"git cannot be run: {shown(done.launch_error)}")
        if done.timed_out:
            raise Fault(f"git {label} timed out after {GIT_TIMEOUT_SECONDS:g}s and was killed")
        if check and done.code != 0:
            raise Fault(f"git {label} failed with exit {done.code}: {self.message(done)}")
        return done

    @staticmethod
    def message(done: Completed) -> str:
        text = done.stderr.decode("utf-8", errors="replace").strip()
        return shown(text.splitlines()[-1] if text else "no message")

    def text(self, args: Sequence[str], options: Sequence[str] = ()) -> str:
        return self.run(args, options=options).stdout.decode("utf-8", errors="replace").strip()

    def read_blobs(self, commit: str, paths: Sequence[str]) -> dict[str, BlobRead]:
        """Read the blob at each path of `commit` through one `cat-file --batch`; a path is never a pathspec."""
        if not paths:
            return {}
        request = "".join(f"{commit}:{path}\n" for path in paths).encode("utf-8")
        data = self.run(["cat-file", "--batch"], stdin=request).stdout
        result: dict[str, BlobRead] = {}
        position = 0
        for path in paths:
            newline = data.find(b"\n", position)
            if newline < 0:
                raise Fault("git cat-file --batch answered outside its documented format")
            header = data[position:newline].decode("utf-8", errors="replace")
            position = newline + 1
            if header.endswith(" missing"):
                result[path] = BlobRead("missing", b"")
                continue
            parts = header.split(" ")
            if len(parts) != 3 or not parts[2].isdigit():
                raise Fault("git cat-file --batch answered outside its documented format")
            size = int(parts[2])
            body = data[position : position + size]
            if len(body) != size or data[position + size : position + size + 1] != b"\n":
                raise Fault("git cat-file --batch answered outside its documented format")
            position += size + 1
            result[path] = BlobRead("blob" if parts[1] == "blob" else "other", body if parts[1] == "blob" else b"")
        return result


def local_remote(remote: str) -> str:
    """A remote that names an existing local directory is made absolute; every other spelling is kept."""
    return os.path.abspath(remote) if os.path.isdir(remote) else remote


class Clone:
    """The fresh integration clone of one run."""

    def __init__(self, git: Git, scratch: str, config: Config, tip: str, queue_sha: str | None, width: int) -> None:
        self.git = git
        self.scratch = scratch
        self.config = config
        self.tip = tip
        self.queue_sha = queue_sha
        self.width = width

    @staticmethod
    def open(config: Config, exe: str) -> Clone:
        """Create the clone and fill it by a verified fetch; remove it again when that fails."""
        scratch = tempfile.mkdtemp(prefix="integrate-clone-")
        try:
            return Clone._fill(config, exe, scratch)
        except BaseException:
            remove_tree(scratch)
            raise

    @staticmethod
    def _fill(config: Config, exe: str, scratch: str) -> Clone:
        remote = local_remote(config.remote)
        root = os.path.join(scratch, "clone")
        os.mkdir(root)
        outside = Git(exe, scratch, scratch)
        listed = outside.run(["ls-remote", "--", remote, f"refs/heads/{config.branch}", f"refs/heads/{config.queue_branch}"], check=False)
        if listed.code != 0:
            raise Fault(f"the remote cannot be reached: {Git.message(listed)}")
        width = 0
        wanted = [f"refs/heads/{config.branch}"]
        for line in listed.stdout.decode("utf-8", errors="replace").splitlines():
            sha, _, ref = line.partition("\t")
            if ref == f"refs/heads/{config.branch}" and SHA_TEXT.fullmatch(sha) is not None:
                width = len(sha)
            elif ref == f"refs/heads/{config.queue_branch}" and SHA_TEXT.fullmatch(sha) is not None:
                wanted.append(ref)
        if not width:
            raise Fault(f"the remote has no branch {shown(config.branch)}")
        outside.run(
            ["init", "--quiet", "--template=", f"--object-format={'sha256' if width == 64 else 'sha1'}", root],
            options=("-c", "init.defaultBranch=integration"),
        )
        git = Git(exe, root, scratch)
        fetched = git.run(
            ["fetch", "--quiet", "--no-tags", "--no-recurse-submodules", "--no-write-fetch-head", "--", remote, *(f"+{ref}:refs/remotes/origin/{ref.removeprefix('refs/heads/')}" for ref in wanted)],
            options=("-c", "transfer.fsckObjects=true", "-c", "fetch.fsckObjects=true"),
            check=False,
        )
        if fetched.code != 0:
            raise Fault(f"the verified fetch failed: {Git.message(fetched)}")
        tip = Clone._ref(git, f"refs/remotes/origin/{config.branch}")
        if tip is None:
            raise Fault(f"the fetch did not bring the branch {shown(config.branch)}")
        queue_sha = Clone._ref(git, f"refs/remotes/origin/{config.queue_branch}")
        return Clone(git, scratch, config, tip, queue_sha, width)

    @staticmethod
    def _ref(git: Git, name: str) -> str | None:
        done = git.run(["rev-parse", "--verify", "--quiet", f"{name}^{{commit}}"], check=False)
        if done.code == 0:
            return done.stdout.decode("utf-8", errors="replace").strip()
        if done.code == 1:
            return None
        raise Fault(f"git rev-parse failed with exit {done.code}: {Git.message(done)}")

    def fetch_candidate(self, sha: str) -> None:
        """Bring the commit `sha` of a queued candidate into the clone through a verified fetch; a remote that offers none leaves the clone as it is.

        Only that commit is fetched, through the remote branch that points at it when there is one, else by its sha.
        An object that fails the check of the fetch is a Fault, never a silent skip."""
        remote = local_remote(self.config.remote)
        listed = self.git.run(["ls-remote", "--", remote], check=False)
        if listed.code != 0:
            raise Fault(f"the remote cannot be reached: {Git.message(listed)}")
        heads: list[str] = []
        for line in listed.stdout.decode("utf-8", errors="replace").splitlines():
            found, _, ref = line.partition("\t")
            if found == sha and ref.startswith("refs/heads/"):
                heads.append(ref)
        target = sorted(heads)[0] if heads else sha
        fetched = self.git.run(
            ["fetch", "--quiet", "--no-tags", "--no-recurse-submodules", "--no-write-fetch-head", "--", remote, target],
            options=("-c", "transfer.fsckObjects=true", "-c", "fetch.fsckObjects=true"),
            check=False,
        )
        if fetched.code != 0 and heads:
            raise Fault(f"the verified fetch failed: {Git.message(fetched)}")

    def close(self) -> str | None:
        """Remove the clone; the reason when that fails."""
        return remove_tree(self.scratch)

    # ------------------------------------------------------------------ queue

    def read_queue(self) -> list[QueueEntry]:
        if self.queue_sha is None:
            return []
        read = self.git.read_blobs(self.queue_sha, [self.config.queue_path])[self.config.queue_path]
        if read.kind == "missing":
            return []
        if read.kind != "blob":
            raise Fault("queue file: the queue path is not a file on the queue branch")
        return parse_queue(read.data, self.width)

    def queue_commit(self, entries: Sequence[QueueEntry], message: str) -> str:
        """One commit on top of the queue branch (or an orphan commit) whose tree holds the queue file."""
        blob = self.git.run(["hash-object", "-w", "--stdin"], stdin=serialize_queue(entries)).stdout.decode("ascii", errors="replace").strip()
        if self.queue_sha is None:
            self.git.run(["read-tree", "--empty"])
        else:
            self.git.run(["read-tree", self.queue_sha])
        line = f"100644 {blob}\t{self.config.queue_path}\n".encode("utf-8")
        self.git.run(["update-index", "--index-info"], stdin=line)
        tree = self.git.text(["write-tree"])
        parents = ["-p", self.queue_sha] if self.queue_sha is not None else []
        return self.git.run(["commit-tree", tree, *parents, "-m", message], extra_env=IDENTITY).stdout.decode("ascii", errors="replace").strip()

    def push(self, updates: Sequence[tuple[str, str, str | None]]) -> Completed:
        """Push each (branch, new sha, expected sha or None for an absent branch) with a lease on the expected sha."""
        args = ["push", "--quiet"]
        if len(updates) > 1:
            args.append("--atomic")
        for branch, _, expected in updates:
            args.append(f"--force-with-lease=refs/heads/{branch}:{expected or ''}")
        args.append("--")
        args.append(local_remote(self.config.remote))
        for branch, new, _ in updates:
            args.append(f"{new}:refs/heads/{branch}")
        return self.git.run(args, options=("-c", "transfer.fsckObjects=true"), check=False)

    def remote_refs(self) -> dict[str, str]:
        """The remote's current sha of the branch and of the queue branch (a branch that is absent is left out)."""
        names = [f"refs/heads/{self.config.branch}", f"refs/heads/{self.config.queue_branch}"]
        listed = self.git.run(["ls-remote", "--", local_remote(self.config.remote), *names], check=False)
        if listed.code != 0:
            raise Fault(f"the remote cannot be reached: {Git.message(listed)}")
        result: dict[str, str] = {}
        for line in listed.stdout.decode("utf-8", errors="replace").splitlines():
            sha, _, ref = line.partition("\t")
            if ref in names:
                result[ref.removeprefix("refs/heads/")] = sha
        return result


def _make_writable(function: Callable[..., object], path: str, excinfo: object) -> None:
    """rmtree's error hook: git's object files are read-only on Windows; make the entry writable and try again."""
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        function(path)
    except OSError:
        pass


def remove_tree(path: str) -> str | None:
    """Remove a directory tree; the reason when something is left behind, else None."""
    shutil.rmtree(path, onerror=_make_writable)
    if os.path.exists(path):
        return f"{shown(path)} could not be removed"
    return None


# ----------------------------------------------------------------------------- configured commands


def run_command(label: str, argv: Sequence[str], cwd: str, config: Config, scratch: str) -> int:
    """Run a configured command in `cwd`; its exit code, or a Fault when it cannot serve the run."""
    done = run_raw_command(label, argv, cwd, config, scratch)
    if done.code is None:
        raise Fault(f"{label} did not finish")
    return done.code


def run_raw_command(label: str, argv: Sequence[str], cwd: str, config: Config, scratch: str) -> Completed:
    try:
        program = resolve_argv0(argv[0], cwd)
    except ArgvZeroError as exc:
        raise Fault(f"{label} {exc}") from None
    environment = git_environment(os.path.join(scratch, f"no-graft-{uuid.uuid4().hex}"))
    done = run_process([program, *argv[1:]], cwd, environment, float(config.timeout_seconds))
    if done.launch_error is not None:
        raise Fault(f"{label} cannot be launched ({shown(done.launch_error)})")
    if done.timed_out:
        raise Fault(f"{label} timed out after {config.timeout_seconds}s and was killed")
    return done


def ci_status(argv: Sequence[str], sha: str, cwd: str, config: Config, scratch: str) -> str:
    """Ask the CI-status command about `sha`: green, red or pending; any other answer is a Fault."""
    filled = [sha if argument == SHA_PLACEHOLDER else argument for argument in argv]
    done = run_raw_command("ci_status_command", filled, cwd, config, scratch)
    if done.code != 0:
        raise Fault(f"ci_status_command exited with code {done.code}")
    try:
        text = done.stdout.decode("utf-8")
    except UnicodeDecodeError:
        raise Fault("ci_status_command answered text that is not UTF-8") from None
    if text.endswith("\r\n"):
        text = text[:-2]
    elif text.endswith("\n"):
        text = text[:-1]
    if text not in ("green", "red", "pending"):
        raise Fault(f"ci_status_command answered {shown(text)}, not green, red or pending")
    return text


# ----------------------------------------------------------------------------- the three subcommands


class Integrator:
    def __init__(self, config: Config, exe: str, report: Report) -> None:
        self.config = config
        self.exe = exe
        self.report = report

    # ------------------------------------------------------------------ shared

    def _record(self, clone: Clone, review: str) -> bytes | None:
        read = clone.git.read_blobs(clone.tip, [review])[review]
        return read.data if read.kind == "blob" else None

    def _write_queue(self, clone: Clone, entries: Sequence[QueueEntry], message: str, subject: str) -> bool:
        """Push a queue commit with a lease on the queue sha read; False (a red) when the lease is lost."""
        commit = clone.queue_commit(entries, message)
        done = clone.push([(self.config.queue_branch, commit, clone.queue_sha)])
        if done.code == 0:
            return True
        if clone.remote_refs().get(self.config.queue_branch) != clone.queue_sha:
            self.report.red(QUEUE_MOVED, subject, "the queue branch moved since it was read; nothing is written, run again")
            return False
        raise Fault(f"git push failed with exit {done.code}: {Git.message(done)}")

    # ------------------------------------------------------------------ submit

    def submit(self, arguments: SubmitArguments) -> None:
        clone = Clone.open(self.config, self.exe)
        try:
            self._submit(clone, arguments)
        finally:
            self._close(clone)

    def _close(self, clone: Clone) -> None:
        left = clone.close()
        if left is not None:
            self.report.err.append(f"integrate.py: warning: {left}")

    def _submit(self, clone: Clone, arguments: SubmitArguments) -> None:
        for name, sha in (("--candidate", arguments.candidate),):
            if len(sha) != clone.width:
                raise UsageError(f"{name} does not have the {clone.width} hex digits of this repository's object ids")
        for key in arguments.clears.split(",") if arguments.clears else ():
            if len(key.partition("@")[2]) != clone.width:
                raise UsageError(f"--clears {shown(key)} does not hold a sha of {clone.width} hex digits")
        subject = f"{arguments.ticket}@{arguments.candidate}"
        entries = clone.read_queue()
        if any(entry.key == subject for entry in entries):
            self.report.red(KEY_EXISTS, subject, "the key is already in the queue (any state refuses a resubmission)")
        check = check_review(self._record(clone, arguments.review), arguments.candidate, arguments.submitter, None, None)
        for problem in check.problems:
            self.report.red(REVIEW_MISMATCH, subject, problem)
        if self.report.reds or check.verdict is None:
            return
        entry = QueueEntry(
            ticket=arguments.ticket,
            candidate=arguments.candidate,
            parent=clone.tip,
            review=arguments.review,
            review_candidate=check.verdict.candidate,
            reviewer=check.verdict.reviewer,
            submitter=arguments.submitter,
            state=QUEUED,
            landed_sha="",
            reason="",
            clears=arguments.clears,
        )
        if self._write_queue(clone, [*entries, entry], f"merge-queue: submit {subject}", subject):
            self.report.note(f"QUEUED {escape(subject)} parent={clone.tip}")

    # ------------------------------------------------------------------ land

    def land(self) -> None:
        clone = Clone.open(self.config, self.exe)
        try:
            self._land(clone)
        finally:
            self._close(clone)

    def _land(self, clone: Clone) -> None:
        entries = clone.read_queue()
        pending = [entry for entry in entries if entry.state == LANDED_PENDING_CI]
        red = [entry for entry in entries if entry.state == LANDED_CI_RED]
        queued = [entry for entry in entries if entry.state == QUEUED]
        red_keys = {entry.key for entry in red}
        admissible = queued
        if pending:
            for entry in pending:
                self.report.red(BLOCKED_BY_CI, entry.key, "landed and its CI result is not read back yet; run readback")
            return
        if red:
            admissible = [entry for entry in queued if red_keys <= set(entry.clear_keys)]
            if not admissible:
                for entry in red:
                    self.report.red(BLOCKED_BY_CI, entry.key, "its CI result is red and no queued entry clears every red key")
                return
        if not admissible:
            self.report.note("NOTHING_TO_LAND no admissible QUEUED entry")
            return
        entry = admissible[0]
        bounces, faults, merged = self._judge(clone, entry)
        for bounce in bounces:
            self.report.red(bounce.reason, entry.key, bounce.detail)
        for text in faults:
            self.report.fault(text)
        if bounces:
            self._bounce(clone, entries, entry, bounces[0].reason)
            return
        if faults:
            return
        self._push_landing(clone, entries, entry, merged)

    def _judge(self, clone: Clone, entry: QueueEntry) -> tuple[list[Bounce], list[str], str]:
        """Every red and every fault found for `entry`, and the merge commit the checks ran on ("" when none was made).

        The order is the ticket's: the record must admit the entry before anything else is done; then the
        candidate is merged into the tip; only then do the configured commands run, on the merged tree."""
        bounces: list[Bounce] = []
        faults: list[str] = []
        try:
            check = check_review(self._record(clone, entry.review), entry.candidate, entry.submitter, entry.review_candidate, entry.reviewer)
            for problem in check.problems:
                bounces.append(Bounce(REVIEW_MISMATCH, problem))
            if entry.review_candidate != entry.candidate:
                bounces.append(Bounce(REVIEW_MISMATCH, "the row's review_candidate differs from the candidate"))
        except Fault as exc:
            faults.append(str(exc))
        if bounces or faults:
            return bounces, faults, ""
        try:
            merged = self._merge(clone, entry, bounces)
        except Fault as exc:
            faults.append(str(exc))
            return bounces, faults, ""
        if merged is None:
            return bounces, faults, ""
        self._run_checks(clone, entry, merged, bounces, faults)
        return bounces, faults, merged

    def _merge(self, clone: Clone, entry: QueueEntry, bounces: list[Bounce]) -> str | None:
        """Make one merge commit of the candidate into the tip (tip first parent, candidate second); nothing is checked out yet.

        The sha of the merge commit; None, with the bounce added, when the candidate is not offered, is already
        contained in the tip, shares no history with it or conflicts with it."""
        clone.fetch_candidate(entry.candidate)
        kinds = clone.git.run(["cat-file", "--batch-check"], stdin=f"{entry.candidate}\n".encode("ascii")).stdout.decode("utf-8", errors="replace").split()
        if len(kinds) != 3 or kinds[1] != "commit":
            bounces.append(Bounce(MERGE_CONFLICT, "the candidate is not a commit the remote offers; there is nothing to merge"))
            return None
        contained = clone.git.run(["merge-base", "--is-ancestor", entry.candidate, clone.tip], check=False)
        if contained.code == 0:
            bounces.append(Bounce(ALREADY_LANDED, "the candidate is already contained in the current tip"))
            return None
        if contained.code != 1:
            raise Fault(f"git merge-base failed with exit {contained.code}: {Git.message(contained)}")
        shared = clone.git.run(["merge-base", clone.tip, entry.candidate], check=False)
        if shared.code == 1:
            bounces.append(Bounce(MERGE_CONFLICT, "the candidate shares no history with the current tip"))
            return None
        if shared.code != 0:
            raise Fault(f"git merge-base failed with exit {shared.code}: {Git.message(shared)}")
        merge = clone.git.run(["merge-tree", "--write-tree", "--no-messages", clone.tip, entry.candidate], check=False)
        if merge.code == 1:
            bounces.append(Bounce(MERGE_CONFLICT, "the candidate does not merge into the current tip without a conflict"))
            return None
        lines = merge.stdout.decode("ascii", errors="replace").split()
        if merge.code != 0 or not lines or SHA_TEXT.fullmatch(lines[0]) is None:
            raise Fault(f"git merge-tree failed with exit {merge.code}: {Git.message(merge)}")
        made = clone.git.run(
            ["commit-tree", lines[0], "-p", clone.tip, "-p", entry.candidate, "-m", f"merge-queue: land {entry.key}"],
            extra_env=IDENTITY,
        )
        return made.stdout.decode("ascii", errors="replace").strip()

    def _run_checks(self, clone: Clone, entry: QueueEntry, merged: str, bounces: list[Bounce], faults: list[str]) -> None:
        try:
            specs, problems = self._affected(clone, merged)
        except Fault as exc:
            faults.append(str(exc))
            return
        for problem in problems:
            bounces.append(Bounce(SPEC_RED, problem))
        try:
            clone.git.run(["checkout", "--quiet", "--detach", "--force", merged])
        except Fault as exc:
            faults.append(str(exc))
            return
        if not problems:
            if specs:
                self._command(clone, "spec_command", [*self.config.spec_command, *(("./" + s if s.startswith("-") else s) for s in specs)], SPEC_RED, bounces, faults)
            else:
                self.report.note(f"SPECS {escape(entry.key)}: no spec is affected; spec_command is not run")
        self._command(clone, "invariant_command", self.config.invariant_command, INVARIANT_RED, bounces, faults)

    def _command(
        self,
        clone: Clone,
        label: str,
        argv: Sequence[str],
        reason: str,
        bounces: list[Bounce],
        faults: list[str],
    ) -> None:
        try:
            code = run_command(label, argv, clone.git.cwd, self.config, clone.scratch)
        except Fault as exc:
            faults.append(str(exc))
            return
        if code != 0:
            bounces.append(Bounce(reason, f"{label} exited with code {code}"))

    def _affected(self, clone: Clone, merged: str) -> tuple[list[str], list[str]]:
        """The affected spec paths of the landing (the paths the merge commit changes in the tip), and the reds that stop them from being known."""
        problems: list[str] = []
        changed_raw = clone.git.run(["diff-tree", "-r", "-z", "--name-only", "--no-renames", clone.tip, merged]).stdout
        tree_raw = clone.git.run(["ls-tree", "-r", "-z", "--name-only", merged]).stdout
        changed: list[str] = []
        for item in changed_raw.split(b"\0"):
            if item:
                changed.append(self._clean_path(item, problems))
        spec_paths: list[str] = []
        for item in tree_raw.split(b"\0"):
            if item and SPEC_BASENAME.search(item) is not None:
                spec_paths.append(self._clean_path(item, problems))
        if problems:
            return [], sorted(set(problems))
        texts: dict[str, str] = {}
        for path, read in clone.git.read_blobs(merged, spec_paths).items():
            texts[path] = read.data.decode("utf-8", errors="replace") if read.kind == "blob" else ""
        pages: list[Page] = []
        registry = clone.git.read_blobs(merged, [PAGES_PATH])[PAGES_PATH]
        if registry.kind == "other":
            return [], ["pages.json is not a file"]
        if registry.kind == "blob":
            try:
                pages = parse_pages(registry.data)
            except PagesError as exc:
                return [], [f"pages.json cannot be read: {exc}"]
        return affected_specs([path for path in changed if path], texts, pages), []

    @staticmethod
    def _clean_path(raw: bytes, problems: list[str]) -> str:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append("a changed or spec path is not UTF-8 text")
            return ""
        bad = bad_character(text)
        if bad is not None:
            problems.append(f"a changed or spec path holds {bad}")
            return ""
        return text

    def _bounce(self, clone: Clone, entries: Sequence[QueueEntry], entry: QueueEntry, reason: str) -> None:
        """Record the bounce on the queue branch only; a failure to record it is a fault, the red stays."""
        updated = [replace(item, state=BOUNCED, reason=reason) if item.key == entry.key else item for item in entries]
        try:
            self._write_queue(clone, updated, f"merge-queue: bounce {entry.key} {reason}", entry.key)
        except Fault as exc:
            self.report.fault(str(exc))

    def _push_landing(self, clone: Clone, entries: Sequence[QueueEntry], entry: QueueEntry, merged: str) -> None:
        updated = [
            replace(item, state=LANDED_PENDING_CI, landed_sha=merged, reason="") if item.key == entry.key else item
            for item in entries
        ]
        commit = clone.queue_commit(updated, f"merge-queue: land {entry.key}")
        done = clone.push(
            [(self.config.branch, merged, clone.tip), (self.config.queue_branch, commit, clone.queue_sha)]
        )
        if done.code == 0:
            self.report.note(f"LANDED_PENDING_CI {escape(entry.key)} landed_sha={merged}")
            return
        now = clone.remote_refs()
        if now.get(self.config.queue_branch) != clone.queue_sha:
            self.report.red(QUEUE_MOVED, entry.key, "the queue branch moved since it was read; nothing is written, run again")
            return
        if now.get(self.config.branch) != clone.tip:
            self.report.red(TIP_MOVED, entry.key, "the integration branch moved since it was read; the entry is bounced, resubmit under a new key")
            self._bounce(clone, entries, entry, TIP_MOVED)
            return
        raise Fault(f"git push failed with exit {done.code}: {Git.message(done)}")

    # ------------------------------------------------------------------ readback

    def readback(self) -> None:
        clone = Clone.open(self.config, self.exe)
        try:
            self._readback(clone)
        finally:
            self._close(clone)

    def _readback(self, clone: Clone) -> None:
        entries = clone.read_queue()
        pending = [entry for entry in entries if entry.state == LANDED_PENDING_CI]
        if not pending:
            self.report.note("READBACK pending=0")
            return
        clone.git.run(["checkout", "--quiet", "--detach", "--force", clone.tip])
        states = {entry.key: entry.state for entry in entries}
        changes: list[str] = []
        unchanged = 0
        for entry in pending:
            try:
                answer = ci_status(self.config.ci_status_command, entry.landed_sha, clone.git.cwd, self.config, clone.scratch)
            except Fault as exc:
                self.report.fault(f"{escape(entry.key)}: {exc}")
                continue
            if answer == "pending":
                unchanged += 1
            elif answer == "red":
                states[entry.key] = LANDED_CI_RED
                changes.append(f"READBACK {escape(entry.key)} {LANDED_PENDING_CI} -> {LANDED_CI_RED}")
            else:
                states[entry.key] = LANDED
                changes.append(f"READBACK {escape(entry.key)} {LANDED_PENDING_CI} -> {LANDED}")
                for key in entry.clear_keys:
                    if states.get(key) == LANDED_CI_RED:
                        states[key] = CLEARED
                        changes.append(f"READBACK {escape(key)} {LANDED_CI_RED} -> {CLEARED}")
        if changes:
            updated = [replace(entry, state=states[entry.key]) for entry in entries]
            if not self._write_queue(clone, updated, "merge-queue: readback", "readback"):
                return
        for line in changes:
            self.report.note(line)
        self.report.note(f"READBACK pending={unchanged} recorded={len(changes)}")


# ----------------------------------------------------------------------------- command line


def _harden_streams() -> None:
    """Keep the host's encoding but never let an unencodable character raise on output."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (OSError, ValueError):
                pass


def _write(stream: TextIO | None, lines: Sequence[str]) -> bool:
    """Write and flush the lines; False when the stream is missing, closed or broken."""
    if not lines:
        return True
    if stream is None:
        return False
    try:
        stream.write("".join(printable_line(line) + "\n" for line in lines))
        stream.flush()
    except (OSError, ValueError):
        return False
    return True


def _emit(report: Report) -> int:
    code = report.code
    out_ok = _write(sys.stdout, report.out)
    err_ok = _write(sys.stderr, report.err)
    return code if out_ok and err_ok else EXIT_FAULT


def run(args: Sequence[str]) -> Report:
    """One whole run; the Report holds what to print and what to exit with."""
    report = Report()
    try:
        arguments = parse_arguments(args)
        config = parse_config(read_file(arguments.config, "config"))
        integrator = Integrator(config, find_git(), report)
        if arguments.subcommand == "submit" and arguments.submit is not None:
            integrator.submit(arguments.submit)
        elif arguments.subcommand == "land":
            integrator.land()
        else:
            integrator.readback()
    except UsageError as exc:
        return UsageReport(str(exc))
    except Fault as exc:
        report.fault(str(exc))
    except KeyboardInterrupt:
        report.fault("interrupted")
    except Exception as exc:  # noqa: BLE001 - any unexpected error is a tool fault, never a traceback
        report.fault(f"unexpected {escape(type(exc).__name__)}: {shown(str(exc))}")
    return report


class UsageReport(Report):
    """A run that ended as a usage error: the usage line and one error line on standard error, exit 3."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.err = [USAGE, f"integrate.py: error: {message}"]

    @property
    def code(self) -> int:
        return EXIT_USAGE


def main(argv: Sequence[str] | None = None) -> int:
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    return _emit(run(args))


def _settle(name: str) -> None:
    """Flush a standard stream; one that cannot be flushed is replaced so the interpreter's own flush at exit stays silent."""
    stream = getattr(sys, name)
    if stream is None:
        return
    try:
        stream.flush()
    except (OSError, ValueError):
        setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))


def entry() -> int:
    """The command-line entry: main, then a last flush that cannot turn the exit into 120."""
    code = main()
    _settle("stdout")
    _settle("stderr")
    return code


if __name__ == "__main__":
    sys.exit(entry())
