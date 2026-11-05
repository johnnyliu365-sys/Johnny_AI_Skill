"""Compare a pytest junit report with the registered failures of one operating system (ticket 59).

usage: python ci/check_registered_failures.py --os <linux|windows> --junit <file> [--list <file>]

The list is ``{"linux": [row, ...], "windows": [row, ...]}``; a row is
``{"test": <pytest node id>, "reason": <cause>, "follow_up": <ticket path or "environment">}``.

Exit codes:
  0  the failed and errored test ids of the report equal the registered set for ``--os``
  1  a mismatch; one line per subject:
       UNREGISTERED_FAILURE <id>      failed or errored, not registered
       REGISTERED_NOW_PASSING <id>    registered, ran and passed
       REGISTERED_NOT_FAILING <id>    registered, skipped or absent from the report
  2  the report or the list cannot be read or does not follow its schema (one line on stderr)
  3  bad arguments

Test ids are compared as whole strings, never by prefix. Every printed subject is escaped to
one ASCII line. Skipped tests are neither failures nor passes. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NoReturn

OPERATING_SYSTEMS = ("linux", "windows")
ROW_KEYS = frozenset({"test", "reason", "follow_up"})
DEFAULT_LIST = Path(__file__).resolve().with_name("registered-failures.json")


class InputFault(Exception):
    """The report or the list cannot be read or breaks its schema (exit 2)."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        print("usage error: " + escape(message), file=sys.stderr)
        raise SystemExit(3)


def escape(subject: str) -> str:
    """One ASCII line: control characters, newlines and non-ASCII become backslash escapes."""
    return subject.encode("unicode_escape").decode("ascii")


def load_registered(path: Path, operating_system: str) -> dict[str, dict[str, str]]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise InputFault(f"cannot read list {path}: {type(error).__name__}") from error
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        raise InputFault(f"list {path} is not JSON: {type(error).__name__}") from error
    if not isinstance(document, dict):
        raise InputFault("list is not an object keyed by operating system")
    unknown = sorted(str(key) for key in document if key not in OPERATING_SYSTEMS)
    if unknown:
        raise InputFault("list has an unknown operating system key: " + ", ".join(unknown))
    for name in OPERATING_SYSTEMS:
        if name not in document:
            raise InputFault(f"list lacks the operating system key {name}")
    result: dict[str, dict[str, str]] = {}
    for name in OPERATING_SYSTEMS:
        rows = document[name]
        if not isinstance(rows, list):
            raise InputFault(f"list for {name} is not an array")
        seen: set[str] = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or set(row) != ROW_KEYS:
                raise InputFault(f"row {index} of {name} must be an object with exactly test, reason and follow_up")
            for key in sorted(ROW_KEYS):
                value = row[key]
                if not isinstance(value, str) or not value.strip():
                    raise InputFault(f"row {index} of {name} has an empty or non-string {key}")
            test: str = row["test"]
            if test in seen:
                raise InputFault(f"row {index} of {name} repeats test id {test}")
            seen.add(test)
            if name == operating_system:
                result[test] = {"reason": row["reason"], "follow_up": row["follow_up"]}
    return result


def node_id(case: ET.Element) -> str:
    """The pytest node id of a junit ``testcase`` element.

    pytest writes ``classname`` as the dotted module path plus the class chain and ``name`` as the
    function name with its parameter id; the module is every part up to the first one named
    ``test_*`` (the suite is flat: ``tests/test_*.py``). A collection error has an empty classname
    and the dotted module path as its name.
    """
    name = case.get("name")
    if name is None or not name.strip():
        raise InputFault("a testcase has no name")
    classname = case.get("classname") or ""
    if not classname:
        return name.replace(".", "/") + ".py" if "::" not in name and "/" not in name else name
    parts = classname.split(".")
    split = len(parts)
    for index, part in enumerate(parts):
        if part.startswith("test_"):
            split = index + 1
            break
    module = "/".join(parts[:split]) + ".py"
    return "::".join([module, *parts[split:], name])


def load_report(path: Path) -> tuple[set[str], set[str]]:
    """Return (failed or errored node ids, passed node ids) of a junit report."""
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise InputFault(f"cannot read report {path}: {type(error).__name__}") from error
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise InputFault("report declares a DOCTYPE or an entity")
    try:
        root = ET.fromstring(raw)
    except (ET.ParseError, ValueError, RecursionError) as error:
        raise InputFault(f"report {path} is not well-formed XML: {type(error).__name__}") from error
    if root.tag not in ("testsuites", "testsuite"):
        raise InputFault("report root is neither testsuites nor testsuite")
    failed: set[str] = set()
    skipped: set[str] = set()
    ran: set[str] = set()
    for case in root.iter("testcase"):
        identifier = node_id(case)
        ran.add(identifier)
        if case.find("failure") is not None or case.find("error") is not None:
            failed.add(identifier)
        elif case.find("skipped") is not None:
            skipped.add(identifier)
    return failed, ran - failed - skipped


def compare(registered: set[str], failed: set[str], passed: set[str]) -> list[str]:
    lines = [f"UNREGISTERED_FAILURE {escape(i)}" for i in sorted(failed - registered)]
    for identifier in sorted(registered - failed):
        code = "REGISTERED_NOW_PASSING" if identifier in passed else "REGISTERED_NOT_FAILING"
        lines.append(f"{code} {escape(identifier)}")
    return lines


def main(argv: list[str]) -> int:
    parser = _Parser(prog="check_registered_failures.py", add_help=False)
    parser.add_argument("--os", dest="operating_system", required=True, choices=OPERATING_SYSTEMS)
    parser.add_argument("--junit", required=True)
    parser.add_argument("--list", dest="list_path", default=str(DEFAULT_LIST))
    try:
        arguments = parser.parse_args(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 3
    try:
        registered = load_registered(Path(arguments.list_path), arguments.operating_system)
        failed, passed = load_report(Path(arguments.junit))
    except InputFault as fault:
        print("INPUT_ERROR " + escape(str(fault)), file=sys.stderr)
        return 2
    lines = compare(set(registered), failed, passed)
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
