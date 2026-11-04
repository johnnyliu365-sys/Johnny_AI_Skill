#!/usr/bin/env python3
"""Preflight gate: every tool a dispatch names starts and serves before any product edit.

Usage: preflight.py <dispatch-file> [--timeout SECONDS]

The dispatch file carries one `preflight:` block. The key starts at column 0 and the
block ends at the next line that starts at column 0. Each item looks like this, and every
value is one JSON value on its own line (a JSON string for `tool` and `expect`, a JSON
array of strings for `start` and `probe`):

    preflight:
      - tool: "<name>"
        start: ["<argv0>", "<arg>", ...]
        probe: ["<argv0>", "<arg>", ...]
        expect: "<substring>"

`start` runs to completion first, `probe` runs after it. Both run without a shell, with
the dispatch file's directory as working directory and an empty stdin, each bounded by
--timeout (default 120 seconds); a command that exceeds it is killed together with the
processes it started. A tool is served when `start` exits 0 and `probe` exits 0 with
`expect` somewhere in its output (stdout and stderr, decoded with replacement, compared
exactly and case-sensitively). Every tool is tried; each failing tool is reported, not
only the first.

Output: `tools=N served=N` on exit 0; one `TOOL_UNSERVED <tool>: <cause>` line per
failing tool on exit 2. Every printed subject is escaped to one line.

Exit codes: 0 every tool served, 2 tool fault (a tool is unserved, or the dispatch file
cannot be read, or an unexpected error), 3 usage error (bad arguments, no `preflight:`
block, a block that does not follow the grammar, an empty `expect`, text that holds a
lone surrogate or a control character). Preflight has no red: a contract red is exit 1 in
the other gates and never occurs here.
"""
from __future__ import annotations

import io
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass

USAGE = "usage: preflight.py <dispatch-file> [--timeout SECONDS]"

DEFAULT_TIMEOUT = 120.0
MAX_TIMEOUT = 86400.0
REAP_SECONDS = 30.0
EXPECT_SHOWN = 80

BLOCK_KEY = "preflight:"
ITEM_LINE = re.compile(r"^  - tool:(?: +(.*))?$")
KEY_LINE = re.compile(r"^    ([^\s:]+):(?: +(.*))?$")
LIST_KEYS = ("start", "probe")
ALL_KEYS = ("tool", "start", "probe", "expect")
TIMEOUT_TEXT = re.compile(r"^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$")

EXIT_SERVED = 0
EXIT_UNSERVED = 2
EXIT_USAGE = 3


class UsageError(Exception):
    """The arguments or the dispatch block are wrong: exit 3."""


@dataclass(frozen=True)
class PreflightItem:
    line: int
    tool: str
    start: tuple[str, ...]
    probe: tuple[str, ...]
    expect: str


@dataclass(frozen=True)
class CommandResult:
    launch_error: str | None
    timed_out: bool
    exit_code: int | None
    output: str


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


def _bad_character(text: str) -> str | None:
    """Name the first lone surrogate or control character in `text`, else None."""
    for char in text:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            return f"a lone surrogate (U+{code:04X})"
        if code <= 0x1F or code == 0x7F:
            return f"a control character (U+{code:04X})"
    return None


def _json_value(raw: str, number: int, key: str) -> object:
    try:
        value: object = json.loads(raw)
    except (ValueError, RecursionError):
        raise UsageError(f"line {number}: the value of {key} is not one JSON value") from None
    return value


def _checked_string(value: object, number: int, key: str) -> str:
    if not isinstance(value, str):
        raise UsageError(f"line {number}: {key} must be a JSON string")
    bad = _bad_character(value)
    if bad is not None:
        raise UsageError(f"line {number}: {key} holds {bad}")
    return value


def _checked_argv(value: object, number: int, key: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise UsageError(f"line {number}: {key} must be a JSON array of strings")
    if not value:
        raise UsageError(f"line {number}: {key} must not be an empty array")
    argv: list[str] = []
    for element in value:
        argv.append(_checked_string(element, number, key))
    if not argv[0]:
        raise UsageError(f"line {number}: the first element of {key} must not be empty")
    return tuple(argv)


@dataclass
class _Draft:
    line: int
    values: dict[str, tuple[int, object]]


def _finish(draft: _Draft) -> PreflightItem:
    for key in ALL_KEYS:
        if key not in draft.values:
            raise UsageError(f"item at line {draft.line} lacks the key {key}")
    tool = _checked_string(draft.values["tool"][1], draft.values["tool"][0], "tool")
    if not tool.strip():
        raise UsageError(f"line {draft.values['tool'][0]}: tool must not be empty")
    expect = _checked_string(draft.values["expect"][1], draft.values["expect"][0], "expect")
    if not expect:
        raise UsageError(
            f"line {draft.values['expect'][0]}: expect must not be empty (an empty expectation proves nothing)"
        )
    start = _checked_argv(draft.values["start"][1], draft.values["start"][0], "start")
    probe = _checked_argv(draft.values["probe"][1], draft.values["probe"][0], "probe")
    return PreflightItem(line=draft.line, tool=tool, start=start, probe=probe, expect=expect)


def parse_preflight(text: str) -> list[PreflightItem]:
    """Parse the `preflight:` block of a dispatch text; raise UsageError when it breaks the grammar."""
    lines = [line[:-1] if line.endswith("\r") else line for line in text.split("\n")]
    header: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(BLOCK_KEY):
            if header is not None:
                raise UsageError(f"line {index + 1}: a second preflight: block")
            if line[len(BLOCK_KEY):].strip(" ") != "":
                raise UsageError(f"line {index + 1}: preflight: takes no value on its own line")
            header = index
    if header is None:
        raise UsageError("no preflight: block in the dispatch")
    items: list[PreflightItem] = []
    draft: _Draft | None = None
    for index in range(header + 1, len(lines)):
        line = lines[index]
        number = index + 1
        if line and line[0] not in " \t":
            break
        if not line.strip(" "):
            continue
        bad = _bad_character(line)
        if bad is not None:
            raise UsageError(f"line {number}: the line holds {bad}")
        item_match = ITEM_LINE.match(line)
        key_match = KEY_LINE.match(line)
        if item_match is not None:
            if draft is not None:
                items.append(_finish(draft))
            draft = _Draft(line=number, values={})
            key, raw = "tool", item_match.group(1)
        elif key_match is not None:
            if draft is None:
                raise UsageError(f"line {number}: a key before the first item")
            key, raw = key_match.group(1), key_match.group(2)
            if key not in ALL_KEYS or key == "tool":
                if key == "tool":
                    raise UsageError(f"line {number}: tool is repeated inside one item")
                raise UsageError(f"line {number}: unknown key {escape(key)}")
        else:
            raise UsageError(f"line {number}: not an item (two spaces, - tool:) or a key (four spaces): {escape(line.strip(' ')[:60])}")
        assert draft is not None
        if key in draft.values:
            raise UsageError(f"line {number}: {key} is repeated inside one item")
        if raw is None or not raw.strip(" "):
            raise UsageError(f"line {number}: {key} has no value")
        draft.values[key] = (number, _json_value(raw.strip(" "), number, key))
    if draft is not None:
        items.append(_finish(draft))
    if not items:
        raise UsageError("the preflight: block holds no item")
    return items


def _kill_tree(process: subprocess.Popen[bytes]) -> None:
    """Kill the process and every process it started, then reap it."""
    if sys.platform == "win32":
        taskkill = shutil.which("taskkill") or "taskkill"
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


def run_command(argv: Sequence[str], cwd: str, timeout: float) -> CommandResult:
    """Run `argv` without a shell, empty stdin, output to a temporary file, bounded by `timeout`."""
    with tempfile.TemporaryFile() as sink:
        try:
            process = subprocess.Popen(
                list(argv),
                stdin=subprocess.DEVNULL,
                stdout=sink,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                shell=False,
                start_new_session=sys.platform != "win32",
            )
        except (OSError, ValueError) as exc:
            reason = exc.strerror if isinstance(exc, OSError) and exc.strerror else str(exc)
            return CommandResult(f"{type(exc).__name__}: {reason}", False, None, "")
        timed_out = False
        exit_code: int | None = None
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_tree(process)
        sink.seek(0)
        output = sink.read().decode("utf-8", errors="replace")
    return CommandResult(None, timed_out, exit_code, output)


def _timeout_text(timeout: float) -> str:
    return f"{timeout:g}s"


def _failure(label: str, result: CommandResult, timeout: float) -> str | None:
    """The cause when `result` of the command `label` is not a clean exit, else None."""
    if result.launch_error is not None:
        return f"{label} cannot be launched ({escape(result.launch_error)})"
    if result.timed_out:
        return f"{label} timed out after {_timeout_text(timeout)} and was killed"
    if result.exit_code != 0:
        return f"{label} exited with code {result.exit_code}"
    return None


def check_item(item: PreflightItem, cwd: str, timeout: float) -> str | None:
    """Return None when the tool is served, else the cause."""
    started = run_command(item.start, cwd, timeout)
    cause = _failure("start", started, timeout)
    if cause is not None:
        return cause
    probed = run_command(item.probe, cwd, timeout)
    cause = _failure("probe", probed, timeout)
    if cause is not None:
        return cause
    if item.expect not in probed.output:
        shown = item.expect if len(item.expect) <= EXPECT_SHOWN else item.expect[:EXPECT_SHOWN] + "..."
        return f'probe output does not contain the expected text "{escape(shown)}"'
    return None


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
        print(f"preflight.py: error: {message}", file=sys.stderr)
    return EXIT_USAGE


def _parse_timeout(text: str) -> float:
    if TIMEOUT_TEXT.match(text) is None:
        raise UsageError(f"--timeout needs a positive number of seconds, got {escape(text)}")
    value = float(text)
    if not math.isfinite(value) or value <= 0 or value > MAX_TIMEOUT:
        raise UsageError(f"--timeout must be above 0 and at most {MAX_TIMEOUT:g} seconds, got {escape(text)}")
    return value


def _parse_arguments(args: Sequence[str]) -> tuple[str, float]:
    timeout: float | None = None
    positional: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--timeout":
            if timeout is not None:
                raise UsageError("--timeout is given twice")
            if index + 1 >= len(args):
                raise UsageError("--timeout needs a value")
            timeout = _parse_timeout(args[index + 1])
            index += 2
            continue
        if arg.startswith("-"):
            raise UsageError(f"unknown option {escape(arg)}")
        positional.append(arg)
        index += 1
    if len(positional) != 1:
        raise UsageError("exactly one dispatch file is required")
    return positional[0], DEFAULT_TIMEOUT if timeout is None else timeout


def main(argv: Sequence[str] | None = None) -> int:
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        path, timeout = _parse_arguments(args)
    except UsageError as exc:
        return _usage_error(str(exc))
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        print(f"preflight.py: tool fault: cannot read {escape(path)}: {escape(exc.strerror or type(exc).__name__)}", file=sys.stderr)
        return EXIT_UNSERVED
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return _usage_error(f"{escape(path)} is not UTF-8 text")
    try:
        items = parse_preflight(text)
    except UsageError as exc:
        return _usage_error(str(exc))
    try:
        cwd = os.path.dirname(os.path.abspath(path))
        failures: list[str] = []
        for item in items:
            cause = check_item(item, cwd, timeout)
            if cause is not None:
                failures.append(f"TOOL_UNSERVED {escape(item.tool)}: {cause}")
    except Exception as exc:  # noqa: BLE001 - any unexpected error is a tool fault, never a red and never a traceback
        print(f"preflight.py: tool fault: {escape(type(exc).__name__)}: {escape(str(exc))}", file=sys.stderr)
        return EXIT_UNSERVED
    if failures:
        for line in failures:
            print(line)
        return EXIT_UNSERVED
    print(f"tools={len(items)} served={len(items)}")
    return EXIT_SERVED


if __name__ == "__main__":
    sys.exit(main())
