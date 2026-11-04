#!/usr/bin/env python3
"""Take, verify and diff versioned requirement snapshots that are never overwritten.

Usage:
  requirement_snapshot.py take --source NAME --input ROWS.json [--root DIR] [--taken-at ISO-8601-UTC]
  requirement_snapshot.py verify SNAPSHOT.json
  requirement_snapshot.py diff --source NAME VA VB [--root DIR]

A snapshot is one JSON file per source and version, `<root>/<source>/<date>-v<n>.json`
(default root `doc/requirements/snapshots`):

    {"source": <name>, "taken_at": <ISO-8601 UTC>, "source_sha256": <sha256>, "rows": [...]}

A row has `requirement_id` (unique in the file; 1 to 128 characters from letters, digits and
`._:-/`), `page_id`, `title`, `type`,
`source_ref` (a URL or a repository-relative path, never a host absolute path),
`source_sha256` (64 lower-case hex), `status` (`active` | `retired`) and `version`
(integer >= 1). The snapshot `source_sha256` is the sha256 of the canonical JSON of the
rows: keys sorted, separators `,` and `:`, UTF-8, rows sorted by `requirement_id`;
`taken_at` is not part of it. The file is written with LF and a final LF.

`take` writes the next version (the highest published version plus one, whatever the date), or
writes nothing and prints `<path> unchanged` when the rows equal the latest version's rows. A
snapshot file is never overwritten or edited: it is written to a temporary name in its own
directory and then created exclusively under its final name.

A version number is unique per source. Before it publishes, `take` claims the number by creating
`<root>/<source>/.v<n>.claim` exclusively, re-scans the published files, and if a published file
already carries version `n` or higher it removes its claim and exits 2 (another writer won).
A claim it cannot create, and a claim file left behind by a crash, are exit 2 naming the claim
file; the owner removes a stale claim by hand. Claim files are never committed: ignore `.v*.claim`.

Every string read from an input is valid Unicode without lone surrogates and without control
characters (U+0000 to U+001F, U+007F); a string that breaks this is a red of the input
(ROW_FIELD_TYPE, exit 1), never a tool fault. Every subject printed in a defect line is printed
as its escaped form (Python `repr`) unless it is plain, so one defect is always one line.

`diff` prints `added`, `removed` and `changed` requirement ids, one per line.

Defect codes (exit 1, one line `<code> <requirement_id or field>: <detail>` each):
ROW_FIELD_MISSING; ROW_FIELD_TYPE (a field of the wrong type, an unexpected field, a blank or
disallowed requirement_id, a string that breaks the text-value rule, input that is not JSON or has
no rows list); DUPLICATE_REQUIREMENT; STATUS_UNKNOWN; SOURCE_REF_ABSOLUTE (a source_ref that is
empty, starts with `/`, a backslash or `~`, carries a drive letter or `file:`, or has a `..` segment; a
URL with a scheme is allowed); DIGEST_FORMAT; SNAPSHOT_DIGEST_MISMATCH (a stored version whose
source_sha256 does not match its rows: reported by verify, and by take or diff whenever they read
that version); NAME_INVALID (a source name with a path separator, `..`, characters outside
[A-Za-z0-9._-], a trailing dot, a Windows reserved device name, or a case variant of an existing
source; applied by take, verify and diff alike).

Exit codes: 0 pass, 1 contract red (named defect codes), 2 tool fault (the file system cannot
serve the run, a version file is missing, a lost version race or a stale claim, any unexpected
error), 3 usage error.
A red is never reported as a tool fault and a tool fault is never reported as a red.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import secrets
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from pathlib import Path
from typing import cast

USAGE = (
    "usage: requirement_snapshot.py take --source NAME --input ROWS.json [--root DIR] [--taken-at ISO]\n"
    "       requirement_snapshot.py verify SNAPSHOT.json\n"
    "       requirement_snapshot.py diff --source NAME VA VB [--root DIR]"
)

DEFAULT_ROOT = "doc/requirements/snapshots"

NAME_PATTERN = re.compile(r"[A-Za-z0-9._-]+")
DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}")
VERSION_FILE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})-v(\d+)\.json")
VERSION_ARG_PATTERN = re.compile(r"v?(\d+)")
ID_PATTERN = re.compile(r"[A-Za-z0-9._:/-]{1,128}")
SUBJECT_PATTERN = re.compile(r"[A-Za-z0-9._:/\[\]-]{1,128}")
CLAIM_PATTERN = re.compile(r"\.v\d+\.claim")
URL_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+.-]+://")
DRIVE_PATTERN = re.compile(r"[A-Za-z]:")
RESERVED_DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul", *(f"com{n}" for n in range(1, 10)), *(f"lpt{n}" for n in range(1, 10))}
)

ROW_FIELDS = (
    "requirement_id", "page_id", "title", "type", "source_ref", "source_sha256", "status", "version",
)
TOP_FIELDS = ("source", "taken_at", "source_sha256", "rows")


# ---------------------------------------------------------------------- types


class DefectCode(StrEnum):
    ROW_FIELD_MISSING = "ROW_FIELD_MISSING"
    ROW_FIELD_TYPE = "ROW_FIELD_TYPE"
    DUPLICATE_REQUIREMENT = "DUPLICATE_REQUIREMENT"
    STATUS_UNKNOWN = "STATUS_UNKNOWN"
    SOURCE_REF_ABSOLUTE = "SOURCE_REF_ABSOLUTE"
    DIGEST_FORMAT = "DIGEST_FORMAT"
    SNAPSHOT_DIGEST_MISMATCH = "SNAPSHOT_DIGEST_MISMATCH"
    NAME_INVALID = "NAME_INVALID"


class Status(StrEnum):
    ACTIVE = "active"
    RETIRED = "retired"


def shown(text: str) -> str:
    """A subject as it is printed: plain text stays as it is, anything else is escaped (one line)."""
    return text if SUBJECT_PATTERN.fullmatch(text) is not None else repr(text)


@dataclass(frozen=True)
class Defect:
    code: DefectCode
    subject: str
    detail: str

    def render(self) -> str:
        return f"{self.code.value} {shown(self.subject)}: {self.detail}"


@dataclass(frozen=True)
class Row:
    requirement_id: str
    page_id: str
    title: str
    type: str
    source_ref: str
    source_sha256: str
    status: Status
    version: int

    def to_json(self) -> dict[str, str | int]:
        return {
            "requirement_id": self.requirement_id,
            "page_id": self.page_id,
            "title": self.title,
            "type": self.type,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "status": self.status.value,
            "version": self.version,
        }


@dataclass(frozen=True)
class Snapshot:
    source: str
    taken_at: str
    source_sha256: str
    rows: tuple[Row, ...]


@dataclass(frozen=True)
class VersionFile:
    version: int
    path: Path


class ToolFault(Exception):
    """The run cannot be served (file system, race, ambiguous store): exit 2, never a red."""


class UsageError(Exception):
    """Bad arguments: exit 3."""


# --------------------------------------------------------------------- digest


def canonical_rows_bytes(rows: Sequence[Row]) -> bytes:
    ordered = sorted(rows, key=lambda row: row.requirement_id)
    return json.dumps(
        [row.to_json() for row in ordered], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def rows_digest(rows: Sequence[Row]) -> str:
    return hashlib.sha256(canonical_rows_bytes(rows)).hexdigest()


def snapshot_bytes(snapshot: Snapshot) -> bytes:
    ordered = sorted(snapshot.rows, key=lambda row: row.requirement_id)
    document: dict[str, str | list[dict[str, str | int]]] = {
        "source": snapshot.source,
        "taken_at": snapshot.taken_at,
        "source_sha256": snapshot.source_sha256,
        "rows": [row.to_json() for row in ordered],
    }
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


# ----------------------------------------------------------------- validation


def name_defects(name: str, subject: str = "source") -> list[Defect]:
    """A source name is one safe path segment: [A-Za-z0-9._-], not all dots, no trailing dot."""
    problems: list[str] = []
    if not name:
        problems.append("is empty")
    elif NAME_PATTERN.fullmatch(name) is None:
        problems.append("holds a path separator or a character outside [A-Za-z0-9._-]")
    elif name.strip(".") == "":
        problems.append("is only dots")
    elif name.endswith("."):
        problems.append("ends with a dot")
    elif name.split(".", 1)[0].casefold() in RESERVED_DEVICE_NAMES:
        problems.append("is a reserved device name")
    return [Defect(DefectCode.NAME_INVALID, subject, f"{name!r} {problem}") for problem in problems]


def source_ref_problem(ref: str) -> str | None:
    """Why a source_ref is not a URL or a repository-relative path; None when it is one."""
    if ref == "":
        return "is empty"
    if ref.startswith(("/", "\\", "~")):
        return "is a host absolute path"
    if ref.lower().startswith("file:"):
        return "is a host absolute path"
    if URL_PATTERN.match(ref) is not None:
        return None
    if DRIVE_PATTERN.match(ref) is not None:
        return "is a host absolute path"
    if ".." in re.split(r"[/\\]", ref):
        return "has a .. segment"
    return None


def text_problem(value: str) -> str | None:
    """The text-value rule: no lone surrogate and no control character in any input string."""
    for character in value:
        code = ord(character)
        if 0xD800 <= code <= 0xDFFF:
            return "holds a lone surrogate"
        if code < 0x20 or code == 0x7F:
            return "holds a control character"
    return None


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _subject_of(raw: dict[str, object], index: int) -> str:
    identifier = raw.get("requirement_id")
    if isinstance(identifier, str) and identifier.strip():
        return identifier
    return f"rows[{index}]"


def _field_defects(raw: dict[str, object], index: int) -> tuple[Row | None, list[Defect]]:
    subject = _subject_of(raw, index)
    defects: list[Defect] = []
    for name in raw:
        if name not in ROW_FIELDS:
            defects.append(Defect(DefectCode.ROW_FIELD_TYPE, subject, f"unexpected field {name!r}"))
    for name in ROW_FIELDS:
        if name not in raw:
            defects.append(Defect(DefectCode.ROW_FIELD_MISSING, subject, f"field {name} is missing"))
    if defects:
        return None, defects

    def text(name: str) -> str | None:
        value = raw[name]
        if isinstance(value, str):
            problem = text_problem(value)
            if problem is not None and name != "requirement_id":
                defects.append(Defect(DefectCode.ROW_FIELD_TYPE, subject, f"field {name} {problem}"))
            return value
        defects.append(Defect(DefectCode.ROW_FIELD_TYPE, subject, f"field {name} must be a string"))
        return None

    requirement_id = text("requirement_id")
    if requirement_id is not None:
        if not requirement_id.strip():
            defects.append(Defect(DefectCode.ROW_FIELD_TYPE, subject, "field requirement_id must not be empty"))
        else:
            id_problem = text_problem(requirement_id)
            if id_problem is not None:
                defects.append(Defect(DefectCode.ROW_FIELD_TYPE, subject, f"field requirement_id {id_problem}"))
            elif ID_PATTERN.fullmatch(requirement_id) is None:
                defects.append(Defect(
                    DefectCode.ROW_FIELD_TYPE, subject,
                    "field requirement_id must be 1 to 128 characters from letters, digits and ._:-/",
                ))
    page_id = text("page_id")
    title = text("title")
    kind = text("type")
    source_ref = text("source_ref")
    if source_ref is not None:
        ref_problem = source_ref_problem(source_ref)
        if ref_problem is not None:
            defects.append(Defect(DefectCode.SOURCE_REF_ABSOLUTE, subject, f"source_ref {source_ref!r} {ref_problem}"))
    digest = text("source_sha256")
    if digest is not None and DIGEST_PATTERN.fullmatch(digest) is None:
        defects.append(Defect(DefectCode.DIGEST_FORMAT, subject, "source_sha256 must be 64 lower-case hex characters"))
    status_text = text("status")
    status: Status | None = None
    if status_text is not None:
        try:
            status = Status(status_text)
        except ValueError:
            defects.append(Defect(DefectCode.STATUS_UNKNOWN, subject, f"status {status_text!r} is not active or retired"))
    version_value = raw["version"]
    version: int | None = None
    if isinstance(version_value, int) and not isinstance(version_value, bool) and version_value >= 1:
        version = version_value
    else:
        defects.append(Defect(DefectCode.ROW_FIELD_TYPE, subject, "field version must be an integer >= 1"))
    if defects:
        return None, defects
    assert requirement_id is not None and page_id is not None and title is not None  # narrowed above
    assert kind is not None and source_ref is not None and digest is not None  # narrowed above
    assert status is not None and version is not None  # narrowed above
    return Row(requirement_id, page_id, title, kind, source_ref, digest, status, version), []


def parse_rows(raw_rows: object) -> tuple[list[Row], list[Defect]]:
    """Turn dynamic rows into typed rows; every defect of every row is reported."""
    if not isinstance(raw_rows, list):
        return [], [Defect(DefectCode.ROW_FIELD_TYPE, "rows", "rows must be a list")]
    rows: list[Row] = []
    defects: list[Defect] = []
    first_seen: dict[str, int] = {}
    for index, entry in enumerate(cast("list[object]", raw_rows)):
        if not isinstance(entry, dict):
            defects.append(Defect(DefectCode.ROW_FIELD_TYPE, f"rows[{index}]", "a row must be an object"))
            continue
        raw = cast("dict[str, object]", entry)
        identifier = raw.get("requirement_id")
        if isinstance(identifier, str) and identifier.strip():
            if identifier in first_seen:
                defects.append(Defect(
                    DefectCode.DUPLICATE_REQUIREMENT, identifier,
                    f"appears at rows[{first_seen[identifier]}] and rows[{index}]",
                ))
            else:
                first_seen[identifier] = index
        row, row_defects = _field_defects(raw, index)
        defects.extend(row_defects)
        if row is not None:
            rows.append(row)
    return rows, defects


def parse_taken_at(text: str) -> str | None:
    """A UTC instant in ISO-8601 form; returns the canonical YYYY-MM-DDTHH:MM:SSZ, else None."""
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None or moment.utcoffset() != timedelta(0):
        return None
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _decode_json(data: bytes, subject: str) -> tuple[object | None, list[Defect]]:
    try:
        text = data.decode("utf-8-sig")
        value: object = json.loads(text)
    except (UnicodeDecodeError, ValueError):
        return None, [Defect(DefectCode.ROW_FIELD_TYPE, subject, "not valid UTF-8 JSON")]
    return value, []


def parse_input(data: bytes) -> tuple[list[Row], list[Defect]]:
    """The rows file given to `take`: JSON that holds a `rows` list."""
    value, defects = _decode_json(data, "input")
    if defects:
        return [], defects
    if not isinstance(value, dict) or "rows" not in value:
        return [], [Defect(DefectCode.ROW_FIELD_TYPE, "rows", "the input has no rows list")]
    return parse_rows(cast("dict[str, object]", value)["rows"])


def parse_snapshot(data: bytes) -> tuple[Snapshot | None, list[Defect]]:
    """A snapshot file: shape, rows, source name and the digest of the rows."""
    value, defects = _decode_json(data, "snapshot")
    if defects:
        return None, defects
    if not isinstance(value, dict):
        return None, [Defect(DefectCode.ROW_FIELD_TYPE, "snapshot", "a snapshot must be a JSON object")]
    top = cast("dict[str, object]", value)
    for name in top:
        if name not in TOP_FIELDS:
            defects.append(Defect(DefectCode.ROW_FIELD_TYPE, name, "unexpected top-level field"))
    for name in TOP_FIELDS:
        if name not in top:
            defects.append(Defect(DefectCode.ROW_FIELD_MISSING, name, f"field {name} is missing"))
    if defects:
        return None, defects
    source = top["source"]
    taken_at = top["taken_at"]
    stored_digest = top["source_sha256"]
    if not isinstance(source, str):
        defects.append(Defect(DefectCode.ROW_FIELD_TYPE, "source", "field source must be a string"))
    else:
        defects.extend(name_defects(source))
    if not isinstance(taken_at, str) or parse_taken_at(taken_at) is None:
        defects.append(Defect(DefectCode.ROW_FIELD_TYPE, "taken_at", "field taken_at must be an ISO-8601 UTC instant"))
    digest_ok = False
    if not isinstance(stored_digest, str):
        defects.append(Defect(DefectCode.ROW_FIELD_TYPE, "source_sha256", "field source_sha256 must be a string"))
    elif DIGEST_PATTERN.fullmatch(stored_digest) is None:
        defects.append(Defect(DefectCode.DIGEST_FORMAT, "source_sha256", "must be 64 lower-case hex characters"))
    else:
        digest_ok = True
    rows, row_defects = parse_rows(top["rows"])
    defects.extend(row_defects)
    if digest_ok and not row_defects and isinstance(stored_digest, str):
        recomputed = rows_digest(rows)
        if recomputed != stored_digest:
            defects.append(Defect(
                DefectCode.SNAPSHOT_DIGEST_MISMATCH, "source_sha256",
                f"recorded {stored_digest}, rows give {recomputed}",
            ))
    if defects or not isinstance(source, str) or not isinstance(taken_at, str) or not isinstance(stored_digest, str):
        return None, defects
    return Snapshot(source, taken_at, stored_digest, tuple(rows)), []


# ----------------------------------------------------------------- file system


def read_file(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ToolFault(f"cannot read {path}: {exc}") from exc


def list_versions(directory: Path) -> list[VersionFile]:
    """Version files of one source directory, oldest version first; absent directory means none."""
    try:
        entries = sorted(os.listdir(directory))
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise ToolFault(f"cannot list {directory}: {exc}") from exc
    found: list[VersionFile] = []
    for entry in entries:
        matched = VERSION_FILE_PATTERN.fullmatch(entry)
        if matched is not None:
            found.append(VersionFile(int(matched.group(2)), directory / entry))
    return sorted(found, key=lambda item: item.version)


def _latest(versions: Sequence[VersionFile]) -> VersionFile | None:
    if not versions:
        return None
    top = versions[-1]
    twins = [item for item in versions if item.version == top.version]
    if len(twins) > 1:
        names = ", ".join(item.path.name for item in twins)
        raise ToolFault(f"version {top.version} exists more than once: {names}")
    return top


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        view = view[written:]


def _publish_exclusive(temporary: Path, target: Path) -> None:
    """Give the finished temporary file its final name without ever replacing an existing file."""
    if os.name == "nt":
        os.rename(temporary, target)  # fails when the target exists
        return
    os.link(temporary, target)  # fails when the target exists
    os.unlink(temporary)


def write_exclusive(target: Path, data: bytes) -> None:
    """Write through a temporary name in the same directory, then create the target exclusively."""
    temporary = target.with_name(f".{target.name}.{secrets.token_hex(6)}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    created = False
    try:
        descriptor = os.open(temporary, flags, 0o644)
        created = True
        try:
            _write_all(descriptor, data)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _publish_exclusive(temporary, target)
    except FileExistsError as exc:
        raise ToolFault(f"{target} or its temporary file already exists; nothing is overwritten") from exc
    except OSError as exc:
        raise ToolFault(f"cannot write {target}: {exc}") from exc
    finally:
        if created:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def _claim_version(directory: Path, number: int) -> Path:
    """Claim a version number: refuse while any claim file exists, then create ours exclusively."""
    try:
        entries = sorted(os.listdir(directory))
    except OSError as exc:
        raise ToolFault(f"cannot list {directory}: {exc}") from exc
    for entry in entries:
        if CLAIM_PATTERN.fullmatch(entry) is not None:
            raise ToolFault(
                f"claim file {directory / entry} exists: another writer holds it, or a crashed run left it "
                "(the owner removes a stale claim by hand)"
            )
    claim = directory / f".v{number}.claim"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(claim, flags, 0o644)
    except FileExistsError as exc:
        raise ToolFault(f"claim file {claim} exists: another writer holds it") from exc
    except OSError as exc:
        raise ToolFault(f"cannot create claim file {claim}: {exc}") from exc
    try:
        _write_all(descriptor, f"{os.getpid()}\n".encode("ascii"))
    except OSError as exc:
        os.close(descriptor)
        _remove_claim(claim)
        raise ToolFault(f"cannot write claim file {claim}: {exc}") from exc
    os.close(descriptor)
    return claim


def _remove_claim(claim: Path) -> bool:
    try:
        os.unlink(claim)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return True


def _release_claim(claim: Path, published: bool) -> None:
    if not _remove_claim(claim) and published:
        raise ToolFault(f"the version was published but the claim file {claim} could not be removed; remove it by hand")


def _case_collisions(root: Path, source: str) -> list[Defect]:
    try:
        entries = os.listdir(root)
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise ToolFault(f"cannot list {root}: {exc}") from exc
    return [
        Defect(DefectCode.NAME_INVALID, "source", f"{source!r} collides with the existing directory {entry!r}")
        for entry in entries
        if entry != source and entry.casefold() == source.casefold()
    ]


# --------------------------------------------------------------------- commands


def _print_defects(defects: Sequence[Defect]) -> None:
    for defect in defects:
        print(defect.render())


def run_take(source: str, input_path: Path, root: Path, taken_at: str | None) -> int:
    defects = name_defects(source)
    if defects:
        _print_defects(defects)
        return 1
    if taken_at is None:
        moment = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        parsed = parse_taken_at(taken_at)
        if parsed is None:
            raise UsageError(f"--taken-at {taken_at!r} is not an ISO-8601 UTC instant")
        moment = parsed
    rows, defects = parse_input(read_file(input_path))
    if defects:
        _print_defects(defects)
        return 1
    digest = rows_digest(rows)
    defects = _case_collisions(root, source)
    if defects:
        _print_defects(defects)
        return 1
    directory = root / source
    latest = _latest(list_versions(directory))
    if latest is not None:
        previous, defects = parse_snapshot(read_file(latest.path))
        if previous is None:
            _print_defects(defects)
            return 1
        if previous.source_sha256 == digest:
            print(f"{latest.path} unchanged")
            return 0
    number = 1 if latest is None else latest.version + 1
    target = directory / f"{moment[:10]}-v{number}.json"
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ToolFault(f"cannot create {directory}: {exc}") from exc
    claim = _claim_version(directory, number)
    published = False
    try:
        newest = _latest(list_versions(directory))
        if newest is not None and newest.version >= number:
            raise ToolFault(f"version {newest.version} was published by another writer; take again")
        write_exclusive(target, snapshot_bytes(Snapshot(source, moment, digest, tuple(rows))))
        published = True
    finally:
        _release_claim(claim, published)
    print(target)
    return 0


def run_verify(path: Path) -> int:
    snapshot, defects = parse_snapshot(read_file(path))
    if snapshot is None:
        _print_defects(defects)
        return 1
    print(f"OK rows={len(snapshot.rows)}")
    return 0


def _load_version(directory: Path, number: int) -> tuple[Snapshot | None, list[Defect]]:
    matching = [item for item in list_versions(directory) if item.version == number]
    if not matching:
        raise ToolFault(f"version {number} does not exist in {directory}")
    if len(matching) > 1:
        raise ToolFault(f"version {number} exists more than once in {directory}")
    return parse_snapshot(read_file(matching[0].path))


def run_diff(source: str, first: int, second: int, root: Path) -> int:
    defects = name_defects(source)
    if defects:
        _print_defects(defects)
        return 1
    defects = _case_collisions(root, source)
    if defects:
        _print_defects(defects)
        return 1
    directory = root / source
    older, older_defects = _load_version(directory, first)
    newer, newer_defects = _load_version(directory, second)
    if older is None or newer is None:
        _print_defects([*older_defects, *newer_defects])
        return 1
    before = {row.requirement_id: row for row in older.rows}
    after = {row.requirement_id: row for row in newer.rows}
    for identifier in sorted(after.keys() - before.keys()):
        print(f"added {shown(identifier)}")
    for identifier in sorted(before.keys() - after.keys()):
        print(f"removed {shown(identifier)}")
    for identifier in sorted(before.keys() & after.keys()):
        if before[identifier] != after[identifier]:
            print(f"changed {shown(identifier)}")
    return 0


# -------------------------------------------------------------------------- CLI


def _take_options(args: Sequence[str]) -> dict[str, str]:
    allowed = ("--source", "--input", "--root", "--taken-at")
    return _options(args, allowed)


def _options(args: Sequence[str], allowed: Sequence[str]) -> dict[str, str]:
    found: dict[str, str] = {}
    index = 0
    while index < len(args):
        name = args[index]
        if name not in allowed:
            raise UsageError(f"unknown option {name}" if name.startswith("-") else f"unexpected argument {name}")
        if index + 1 >= len(args):
            raise UsageError(f"{name} needs a value")
        if name in found:
            raise UsageError(f"{name} given twice")
        found[name] = args[index + 1]
        index += 2
    return found


def _version_number(text: str) -> int:
    matched = VERSION_ARG_PATTERN.fullmatch(text)
    if matched is None or int(matched.group(1)) < 1:
        raise UsageError(f"{text!r} is not a version (v<n> or <n>, n >= 1)")
    return int(matched.group(1))


def _dispatch(args: Sequence[str]) -> int:
    if not args:
        raise UsageError("a command is required: take, verify or diff")
    command, rest = args[0], list(args[1:])
    if command == "take":
        options = _take_options(rest)
        for required in ("--source", "--input"):
            if required not in options:
                raise UsageError(f"{required} is required")
        return run_take(
            options["--source"], Path(options["--input"]), Path(options.get("--root", DEFAULT_ROOT)),
            options.get("--taken-at"),
        )
    if command == "verify":
        if len(rest) != 1 or rest[0].startswith("-"):
            raise UsageError("verify takes exactly one snapshot file")
        return run_verify(Path(rest[0]))
    if command == "diff":
        positional: list[str] = []
        flags: list[str] = []
        index = 0
        while index < len(rest):
            if rest[index].startswith("-"):
                flags.extend(rest[index:index + 2])
                index += 2
            else:
                positional.append(rest[index])
                index += 1
        options = _options(flags, ("--source", "--root"))
        if "--source" not in options:
            raise UsageError("--source is required")
        if len(positional) != 2:
            raise UsageError("diff takes exactly two versions")
        return run_diff(
            options["--source"], _version_number(positional[0]), _version_number(positional[1]),
            Path(options.get("--root", DEFAULT_ROOT)),
        )
    raise UsageError(f"unknown command {command}")


def _harden_streams() -> None:
    """Keep the host's encoding but never let an unencodable character raise on output."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (OSError, ValueError):
                pass


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command; every unexpected error is a tool fault (exit 2), never a red (exit 1)."""
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        return _dispatch(args)
    except UsageError as exc:
        print(USAGE, file=sys.stderr)
        print(f"requirement_snapshot.py: error: {exc}", file=sys.stderr)
        return 3
    except ToolFault as exc:
        print(f"requirement_snapshot.py: tool fault: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - an uncaught error must never reach the caller as exit 1
        print(f"requirement_snapshot.py: tool fault: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
