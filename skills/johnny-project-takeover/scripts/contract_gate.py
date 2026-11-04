#!/usr/bin/env python3
"""Contract gate: every requirement has a spec, every spec is bound and honest.

Usage: contract_gate.py --repo <dir> --snapshot <snapshot.json> --specs <dir>

The snapshot is a requirement snapshot file (a JSON object with a `rows` list; a row
has `requirement_id` and `status`, `active` or `retired`). The specs are every file
named `test_*.py` under `--specs`, which must lie inside `--repo`. A spec declares its
contract in its first comment block, the leading run of lines that start with `#`:

    # requirement: <id>                          one or more
    # source: <repository path> sha256:<hex>    one or more
    # mutation: <name>                           one or more

Defect codes (exit 1, one line `<code> <spec or requirement>: <detail>` each):
  NO_SPEC_FOR_REQUIREMENT, SOURCE_MISSING, SOURCE_DIGEST_MISMATCH,
  RETIRED_REQUIREMENT_BOUND, LITERAL_EXPECTED, NO_MUTATION.

Exit codes: 0 pass, 1 contract red, 2 tool fault (a file cannot be served, or a source
is a URL, which cannot be checked offline), 3 usage error (bad arguments, or the
snapshot argument is not a snapshot). A red is never reported as a tool fault and a
tool fault is never reported as a red. The console encoding never changes an exit
code: stdout and stderr keep the host encoding but escape what it cannot encode.
"""
from __future__ import annotations

import ast
import fnmatch
import hashlib
import io
import json
import os
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

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

DECLARATION = re.compile(r"#\s*([A-Za-z][A-Za-z0-9_-]*)\s*:(.*)$")
SOURCE_VALUE = re.compile(r"^(?:(?P<path>.*\S)\s+)?sha256:(?P<digest>\S*)$", re.DOTALL)
DIGEST = re.compile(r"^[0-9a-f]{64}$")
DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
LINE_BREAK = re.compile(r"\r\n|\r|\n")


class UsageError(Exception):
    """The command line, or the snapshot argument, is not acceptable (exit 3)."""


class ToolFault(Exception):
    """The gate cannot be served (exit 2)."""

    def __init__(self, label: str, message: str) -> None:
        super().__init__(message)
        self.label = label
        self.message = message


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
        detail = self.detail.replace("\r", " ").replace("\n", " ")
        return f"{self.code} {self.subject}: {detail}"


@dataclass(frozen=True)
class SourceLine:
    line: int
    path: str
    digest: str


@dataclass(frozen=True)
class SpecDeclaration:
    spec: str
    requirements: tuple[tuple[int, str], ...]
    sources: tuple[SourceLine, ...]
    mutation_lines: tuple[tuple[int, str], ...]
    malformed: tuple[Defect, ...]
    url_sources: tuple[tuple[int, str], ...]


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


# --------------------------------------------------------------------------- input


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ToolFault("TOOL_FAULT", f"cannot read {path}: {exc}") from exc


def parse_snapshot(raw: bytes, origin: str) -> tuple[Requirement, ...]:
    """Validate snapshot bytes into requirements; anything else is a usage error."""

    def refuse(reason: str) -> UsageError:
        return UsageError(f"{origin} is not a snapshot: {reason}")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise refuse(f"not UTF-8 ({exc.reason})") from exc
    try:
        data: object = json.loads(text)
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
        if not isinstance(identifier, str) or not identifier.strip():
            raise refuse(f"row {index} has no non-empty `requirement_id`")
        if status not in (STATUS_ACTIVE, STATUS_RETIRED):
            raise refuse(f"row {index} `status` is not `active` or `retired`")
        if identifier in seen:
            raise refuse(f"row {index} repeats requirement_id {identifier!r}")
        seen.add(identifier)
        found.append(Requirement(identifier, str(status)))
    return tuple(found)


def load_snapshot(path: Path) -> tuple[Requirement, ...]:
    return parse_snapshot(_read_bytes(path), str(path))


# ------------------------------------------------------------------ spec declarations


def parse_header(spec: str, text: str) -> SpecDeclaration:
    """Read the declarations of the first comment block of a spec."""
    requirements: list[tuple[int, str]] = []
    sources: list[SourceLine] = []
    mutations: list[tuple[int, str]] = []
    malformed: list[Defect] = []
    urls: list[tuple[int, str]] = []
    for number, raw in enumerate(LINE_BREAK.split(text.lstrip("﻿")), 1):
        line = raw.strip()
        if not line.startswith("#"):
            break
        match = DECLARATION.match(line)
        if match is None:
            continue
        key, value = match.group(1), match.group(2).strip()
        if key == "requirement":
            if value:
                requirements.append((number, value))
            else:
                malformed.append(Defect(NO_SPEC_FOR_REQUIREMENT, spec, f"line {number}: requirement declaration names no requirement"))
        elif key == "mutation":
            if value:
                mutations.append((number, value))
            else:
                malformed.append(Defect(NO_MUTATION, spec, f"line {number}: mutation declaration has an empty name"))
                mutations.append((number, ""))
        elif key == "source":
            if "://" in value:
                urls.append((number, value))
                continue
            parsed = SOURCE_VALUE.match(value)
            if parsed is None:
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source declaration has no `sha256:` digest: {value!r}"))
                continue
            path, digest = parsed.group("path"), parsed.group("digest")
            if path is None or not path.strip():
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source declaration has an empty path"))
            elif not DIGEST.match(digest):
                malformed.append(Defect(SOURCE_MISSING, spec, f"line {number}: source {path!r} digest is not 64 lower-case hex: {digest!r}"))
            else:
                sources.append(SourceLine(number, path.strip(), digest))
        else:
            malformed.append(Defect(LITERAL_EXPECTED, spec, f"line {number}: unknown declaration key {key!r}"))
    return SpecDeclaration(spec, tuple(requirements), tuple(sources), tuple(mutations), tuple(malformed), tuple(urls))


# ------------------------------------------------------------------ source resolution


def resolve_source(repo_real: Path, declared: str) -> tuple[Path | None, str]:
    """Resolve a repository-relative source; the second item is the reason when it is unusable.

    Separators are normalised, `.` and empty parts dropped, `..` is resolved lexically and
    may not leave the repository. Every part must match a directory entry exactly, so a
    case variant is a miss on every platform. The real path must stay inside the repository
    (a component-wise test, never a string prefix).
    """
    text = declared.replace("\\", "/")
    if not text.strip():
        return None, "empty path"
    if text.startswith("/") or DRIVE_PREFIX.match(text):
        return None, "absolute path"
    if text.endswith("/"):
        return None, "names a directory (trailing slash)"
    parts: list[str] = []
    for part in text.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None, "escapes the repository"
            parts.pop()
            continue
        parts.append(part)
    if not parts:
        return None, "names the repository root"
    current = repo_real
    for part in parts:
        try:
            names = os.listdir(current)
        except (FileNotFoundError, NotADirectoryError):
            return None, "not found"
        except OSError as exc:
            raise ToolFault("TOOL_FAULT", f"cannot list {current}: {exc}") from exc
        if part not in names:
            return None, "not found (names match exactly, including case)"
        current = current / part
    final = Path(os.path.realpath(current))
    if not final.is_relative_to(repo_real):
        return None, "escapes the repository"
    if not final.is_file():
        return None, "is not a regular file"
    return final, ""


def digest_of(path: Path) -> str:
    return hashlib.sha256(_read_bytes(path)).hexdigest()


# ------------------------------------------------------------------ literal expected


def _is_number(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Constant)
        and not isinstance(node.value, bool)
        and isinstance(node.value, (int, float, complex))
    )


def is_literal(node: ast.expr) -> bool:
    """A number, string or bytes constant, or a display made only of such constants.

    `None`, `True`, `False` and `...` are not literals; a signed number is.
    """
    if isinstance(node, ast.Constant):
        value = node.value
        if value is None or isinstance(value, bool):
            return False
        return isinstance(value, (int, float, complex, str, bytes))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _is_number(node.operand)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(is_literal(element) for element in node.elts)
    if isinstance(node, ast.Dict):
        return all(key is not None and is_literal(key) for key in node.keys) and all(is_literal(v) for v in node.values)
    return False


def compares_with_literal(test: ast.expr) -> bool:
    if isinstance(test, ast.Compare):
        return any(is_literal(operand) for operand in (test.left, *test.comparators))
    if isinstance(test, ast.BoolOp):
        return any(compares_with_literal(value) for value in test.values)
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return compares_with_literal(test.operand)
    return False


def literal_defects(spec: str, data: bytes) -> list[Defect]:
    try:
        tree = ast.parse(data)
    except (SyntaxError, ValueError, RecursionError) as exc:
        if isinstance(exc, SyntaxError):
            where = f"line {exc.lineno}" if exc.lineno is not None else "unknown line"
            return [Defect(LITERAL_EXPECTED, spec, f"syntax error {where}: {exc.msg}; the contract cannot be read")]
        return [Defect(LITERAL_EXPECTED, spec, f"the contract cannot be parsed: {exc}")]
    asserts = sorted(
        (node for node in ast.walk(tree) if isinstance(node, ast.Assert)),
        key=lambda node: (node.lineno, node.col_offset),
    )
    found: list[Defect] = []
    for node in asserts:
        if compares_with_literal(node.test):
            shown = ast.unparse(node.test)
            if len(shown) > 60:
                shown = shown[:57] + "..."
            found.append(Defect(LITERAL_EXPECTED, spec, f"line {node.lineno}: assert compares with a literal constant: {shown}"))
    return found


# ------------------------------------------------------------------------ the gate


def discover_specs(specs_real: Path) -> list[Path]:
    def fail(exc: OSError) -> None:
        raise ToolFault("TOOL_FAULT", f"cannot list {exc.filename}: {exc}")

    found: list[Path] = []
    for directory, subdirs, files in os.walk(specs_real, onerror=fail):
        subdirs.sort()
        for name in sorted(files):
            if fnmatch.fnmatchcase(name, SPEC_PATTERN):
                found.append(Path(directory) / name)
    return sorted(found, key=lambda path: path.relative_to(specs_real).as_posix())


def check_spec(spec_path: Path, spec: str, repo_real: Path, status: dict[str, str]) -> tuple[list[Defect], list[str]]:
    data = _read_bytes(spec_path)
    declaration = parse_header(spec, data.decode("utf-8", errors="replace"))
    if declaration.url_sources:
        number, value = declaration.url_sources[0]
        raise ToolFault(SOURCE_UNSERVABLE, f"{spec}: line {number} source {value!r} is a URL and cannot be verified offline")
    defects: list[Defect] = list(declaration.malformed)
    for source in declaration.sources:
        resolved, reason = resolve_source(repo_real, source.path)
        if resolved is None:
            defects.append(Defect(SOURCE_MISSING, spec, f"line {source.line}: source {source.path!r} {reason}"))
        elif digest_of(resolved) != source.digest:
            defects.append(Defect(SOURCE_DIGEST_MISMATCH, spec, f"line {source.line}: source {source.path!r} does not match the declared digest"))
    declared: list[str] = []
    for _, identifier in declaration.requirements:
        if identifier in declared:
            continue
        declared.append(identifier)
        current = status.get(identifier)
        if current is None:
            defects.append(Defect(RETIRED_REQUIREMENT_BOUND, spec, f"requirement {identifier!r} is absent from the snapshot"))
        elif current == STATUS_RETIRED:
            defects.append(Defect(RETIRED_REQUIREMENT_BOUND, spec, f"requirement {identifier!r} is retired"))
    if declaration.requirements:
        if not declaration.sources and not any(d.code == SOURCE_MISSING for d in declaration.malformed):
            defects.append(Defect(SOURCE_MISSING, spec, "the spec declares a requirement but no source"))
        if not declaration.mutation_lines:
            defects.append(Defect(NO_MUTATION, spec, "the spec declares a requirement but no mutation"))
    defects.extend(literal_defects(spec, data))
    return defects, declared


def run(arguments: Arguments) -> Report:
    repo_real = Path(os.path.realpath(arguments.repo))
    if not repo_real.is_dir():
        raise ToolFault("TOOL_FAULT", f"--repo {arguments.repo} is not a directory")
    requirements = load_snapshot(arguments.snapshot)
    specs_real = Path(os.path.realpath(arguments.specs))
    if not specs_real.is_dir():
        raise ToolFault("TOOL_FAULT", f"--specs {arguments.specs} is not a directory")
    if not specs_real.is_relative_to(repo_real):
        raise UsageError(f"--specs {arguments.specs} is not inside --repo {arguments.repo}")
    status = {item.requirement_id: item.status for item in requirements}
    spec_paths = discover_specs(specs_real)
    defects: list[Defect] = []
    declared: set[str] = set()
    for spec_path in spec_paths:
        spec = spec_path.relative_to(repo_real).as_posix()
        found, identifiers = check_spec(spec_path, spec, repo_real, status)
        defects.extend(found)
        declared.update(identifiers)
    for item in sorted(requirements, key=lambda entry: entry.requirement_id):
        if item.status == STATUS_ACTIVE and item.requirement_id not in declared:
            defects.append(Defect(NO_SPEC_FOR_REQUIREMENT, item.requirement_id, "no spec declares this active requirement"))
    return Report(len(requirements), len(spec_paths), tuple(defects))


# ---------------------------------------------------------------------------- CLI


def parse_arguments(args: Sequence[str]) -> Arguments:
    values: dict[str, str] = {}
    index = 0
    while index < len(args):
        arg = args[index]
        name, equals, inline = arg.partition("=")
        if name not in OPTIONS:
            raise UsageError(f"unknown option or argument {arg!r}")
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
        print(f"contract_gate.py: error: {exc}", file=sys.stderr)
        return 3
    except ToolFault as exc:
        print(f"{exc.label} {exc.message}", file=sys.stderr)
        return 2
    except Exception as exc:  # an unexpected error is a tool fault, never a red, never a traceback
        print(f"TOOL_FAULT unexpected {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    summary = f"requirements={report.requirements} specs={report.specs} defects={len(report.defects)}"
    if report.defects:
        for defect in report.defects:
            print(defect.render())
        print(summary, file=sys.stderr)
        return 1
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
