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
only the first, and the exit is 2 when any tool failed, whichever tool came last.

The gate resolves each program name itself, the same way on every platform: a name that
carries a drive (a letter and a colon at its start, or the extended-length or share
prefix) must be absolute, and this is checked first, before every other rule, so a name
that is relative to a drive is refused and never joined to anything; an absolute
name is used as given; a relative name that contains a path separator (slash or
backslash) is joined to the dispatch file's directory; a bare name is looked up in the
search-path entries only (with the executable extensions of the platform on Windows),
never in the current directory or the dispatch directory. A program whose resolved name
ends in the extension of a batch file (any letter case) is refused, because Windows runs
it through the command interpreter, which reads its arguments as commands. Name the
interpreter or the executable instead.

A child that was started and whose serving then raised an unexpected error is killed
together with the processes it started before the next tool runs. A dispatch path that
names a device (a path component whose name, up to its first dot or colon and without
trailing blanks, is a reserved device name, or a path in the device namespace) is a usage
error and is never opened, whatever the platform. So is a dispatch path that is not a plain
path: one that starts with two separators (a share path, or an extended-length or device
spelling), or with a separator followed by a namespace marker (one or two question marks, or
a single dot, then a separator), or that has the global root of the object manager as a
component (compared as a device name is, up to the first dot or colon, in any letter case, and
after a drive letter and colon at the start of the path is set aside, as for a device name);
both slash directions and any mix of them count, and nothing is opened to decide it.

An interrupt after a child started kills that child with the processes it started, then ends
the run as a tool fault: exit 2 with one line on standard error and no traceback. An interrupt
in any other window of the run (the start of `main`, the setup of the streams, the printing of the
result, the final flush) ends it the same way: exit 2 with the one line, never the status the
interpreter gives an interrupt that nothing handles.

Output: `tools=N served=N` on exit 0; one `TOOL_UNSERVED <tool>: <cause>` line per
failing tool on exit 2. Every printed subject is escaped to one line.

Exit codes: 0 every tool served, 2 tool fault (a tool is unserved, or the dispatch file
cannot be read, or an unexpected error, or an interrupt, or standard output or standard error cannot be
written), 3 usage error (bad arguments, no `preflight:` block, a block that does not
follow the grammar, an empty or blank `expect`, text that holds a lone surrogate or a
control character, in the dispatch file or in an argument, a dispatch path that names a
device or is not a plain path). Preflight has no red: a
contract red is exit 1 in the other gates and never occurs here.
"""
from __future__ import annotations

import ctypes
import io
import json
import math
import os
import re
import signal
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TextIO

USAGE = "usage: preflight.py <dispatch-file> [--timeout SECONDS]"

DEFAULT_TIMEOUT = 120.0
MAX_TIMEOUT = 86400.0
REAP_SECONDS = 30.0
EXPECT_SHOWN = 80
ERROR_SHOWN = 200

BLOCK_KEY = "preflight:"
ITEM_LINE = re.compile(r"^  - tool:(?: +(.*))?$")
KEY_LINE = re.compile(r"^    ([^\s:]+):(?: +(.*))?$")
LIST_KEYS = ("start", "probe")
ALL_KEYS = ("tool", "start", "probe", "expect")
TIMEOUT_TEXT = re.compile(r"[0-9]+(?:\.[0-9]*)?|\.[0-9]+")
BATCH_SUFFIXES = (".bat", ".cmd")
DRIVE_LETTER = re.compile(r"[A-Za-z]:")
SUPERSCRIPT_DIGITS = chr(0xB9) + chr(0xB2) + chr(0xB3)
DEVICE_NAMES = frozenset(
    ["CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$", "CLOCK$"]
    + [f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in "0123456789" + SUPERSCRIPT_DIGITS]
)
DEVICE_NAMESPACE_PREFIXES = ("\\\\.\\", "//./", "\\\\./", "//.\\")
# After every backslash is turned into a slash: two separators, or a separator with one of the namespace markers.
NAMESPACE_ROOTS = ("//", "/?/", "/??/", "/./")
GLOBAL_ROOT = "GLOBALROOT"
DEFAULT_PATHEXT = ".COM;.EXE;.BAT;.CMD"

EXIT_SERVED = 0
EXIT_UNSERVED = 2
EXIT_USAGE = 3


class UsageError(Exception):
    """The arguments or the dispatch block are wrong: exit 3."""


class ArgvZeroError(Exception):
    """The program name cannot be turned into a program the gate may run: the tool is unserved."""


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
    refusal: str | None = None


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
    if not expect.strip():
        raise UsageError(
            f"line {draft.values['expect'][0]}: expect must not be empty or blank (an empty expectation proves nothing)"
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


def _kill_tree(process: subprocess.Popen[bytes]) -> None:
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
    """A letter and a colon at the start, the extended-length or share prefix, or (on Windows) any drive the platform sees."""
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


def resolve_argv0(argv0: str, base: str) -> str:
    """Turn `argv0` into the absolute program path the gate launches; raise ArgvZeroError when it must not run."""
    if _names_a_drive(argv0) and not _fully_absolute(argv0):
        raise ArgvZeroError(f'cannot be resolved (the name "{escape(argv0)}" is relative to a drive)')
    if "/" in argv0 or "\\" in argv0:
        if _fully_absolute(argv0):
            program = argv0
        else:
            program = os.path.abspath(os.path.join(base, argv0))
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
            raise ArgvZeroError(f'cannot be resolved (the name "{escape(argv0)}" is not found in PATH)')
        program = found
    if _is_batch_file(program):
        raise ArgvZeroError(
            f'is refused ("{escape(argv0)}" is a batch file that Windows runs through the command interpreter; '
            "name the interpreter or the executable instead)"
        )
    return program


def run_command(argv: Sequence[str], cwd: str, timeout: float) -> CommandResult:
    """Run `argv` without a shell, empty stdin, output to a temporary file, bounded by `timeout`."""
    try:
        program = resolve_argv0(argv[0], cwd)
    except ArgvZeroError as exc:
        return CommandResult(None, False, None, "", str(exc))
    with tempfile.TemporaryFile() as sink:
        try:
            process = subprocess.Popen(
                [program, *argv[1:]],
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
            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                _kill_tree(process)
            sink.seek(0)
            output = sink.read().decode("utf-8", errors="replace")
        except BaseException:
            # Whatever went wrong after the child started, it must not outlive this call (revision03).
            if process.poll() is None:
                _kill_tree(process)
            raise
    return CommandResult(None, timed_out, exit_code, output)


def _timeout_text(timeout: float) -> str:
    return f"{timeout:g}s"


def _failure(label: str, result: CommandResult, timeout: float) -> str | None:
    """The cause when `result` of the command `label` is not a clean exit, else None."""
    if result.refusal is not None:
        return f"{label} {result.refusal}"
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


Outcome = tuple[int, str, str]


def _usage(message: str | None = None) -> Outcome:
    err = USAGE + "\n"
    if message:
        err += f"preflight.py: error: {message}\n"
    return EXIT_USAGE, "", err


def _write(stream: TextIO | None, text: str) -> bool:
    """Write and flush `text`; False when the stream is missing, closed or broken."""
    if not text:
        return True
    if stream is None:
        return False
    try:
        stream.write(text)
        stream.flush()
    except (OSError, ValueError):
        return False
    return True


def _emit(outcome: Outcome) -> int:
    """Print the outcome; a standard output or error that cannot be written makes the exit 2."""
    code, out, err = outcome
    out_ok = _write(sys.stdout, out)
    err_ok = _write(sys.stderr, err)
    return code if out_ok and err_ok else EXIT_UNSERVED


def _parse_timeout(text: str) -> float:
    if TIMEOUT_TEXT.fullmatch(text) is None:
        raise UsageError(f"--timeout needs a positive number of seconds, got {escape(text)}")
    value = float(text)
    if not math.isfinite(value) or value <= 0 or value > MAX_TIMEOUT:
        raise UsageError(f"--timeout must be above 0 and at most {MAX_TIMEOUT:g} seconds, got {escape(text)}")
    return value


def _component_stem(component: str) -> str:
    """A path component up to its first dot or colon, without trailing blanks."""
    return re.split(r"[.:]", component, maxsplit=1)[0].rstrip(" ")


def names_a_device(path: str) -> bool:
    """True when `path` names a reserved device or lies in the device namespace; a pure text check, nothing is opened."""
    if path.startswith(DEVICE_NAMESPACE_PREFIXES):
        return True
    rest = path[2:] if DRIVE_LETTER.match(path) is not None else path
    for component in rest.replace("\\", "/").split("/"):
        if _component_stem(component).upper() in DEVICE_NAMES:
            return True
    return False


def names_a_namespace(path: str) -> bool:
    """True when `path` is not a plain path: it starts with two separators (a share path, or an extended-length or
    device spelling), with a separator and a namespace marker, or names the global root of the object manager;
    either slash direction, any mix. A pure text check, nothing is opened."""
    text = path.replace("\\", "/")
    if text.startswith(NAMESPACE_ROOTS):
        return True
    # a drive letter and colon at the start belong to no component: `C:GLOBALROOT/x` has the global root as its first
    rest = text[2:] if DRIVE_LETTER.match(text) is not None else text
    for component in rest.split("/"):
        if _component_stem(component).upper() == GLOBAL_ROOT:
            return True
    return False


def _parse_arguments(args: Sequence[str]) -> tuple[str, float]:
    for number, arg in enumerate(args, start=1):
        bad = _bad_character(arg)
        if bad is not None:
            raise UsageError(f"argument {number} holds {bad}")
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
    if names_a_device(positional[0]):
        raise UsageError("the dispatch path names a device, not a file; it is not opened")
    if names_a_namespace(positional[0]):
        raise UsageError("the dispatch path is not a plain path (a share, namespace or global-root spelling); it is not opened")
    return positional[0], DEFAULT_TIMEOUT if timeout is None else timeout


def _serve(item: PreflightItem, cwd: str, timeout: float) -> str | None:
    """check_item, with an unexpected error turned into the cause of this tool alone."""
    try:
        return check_item(item, cwd, timeout)
    except Exception as exc:  # noqa: BLE001 - one tool's unexpected error never ends the run
        shown = str(exc)
        if len(shown) > ERROR_SHOWN:
            shown = shown[:ERROR_SHOWN] + "..."
        return f"unexpected error ({escape(type(exc).__name__)}: {escape(shown)})"


def _gate(args: Sequence[str]) -> Outcome:
    try:
        path, timeout = _parse_arguments(args)
    except UsageError as exc:
        return _usage(str(exc))
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except (OSError, ValueError) as exc:
        reason = exc.strerror if isinstance(exc, OSError) and exc.strerror else type(exc).__name__
        return EXIT_UNSERVED, "", f"preflight.py: tool fault: cannot read {escape(path)}: {escape(reason)}\n"
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return _usage(f"{escape(path)} is not UTF-8 text")
    try:
        items = parse_preflight(text)
    except UsageError as exc:
        return _usage(str(exc))
    cwd = os.path.dirname(os.path.abspath(path))
    lines: list[str] = []
    for item in items:
        cause = _serve(item, cwd, timeout)
        if cause is not None:
            lines.append(f"TOOL_UNSERVED {escape(item.tool)}: {cause}\n")
    if lines:
        return EXIT_UNSERVED, "".join(lines), ""
    return EXIT_SERVED, f"tools={len(items)} served={len(items)}\n", ""


INTERRUPTED_LINE = "preflight.py: tool fault: interrupted\n"


def _interrupted() -> int:
    """An interrupt that no handler of the run met: one line on standard error and exit 2."""
    _write(sys.stderr, INTERRUPTED_LINE)
    return EXIT_UNSERVED


def main(argv: Sequence[str] | None = None) -> int:
    try:
        _harden_streams()
        args = list(sys.argv[1:] if argv is None else argv)
        try:
            outcome = _gate(args)
        except KeyboardInterrupt:
            # A child that was started is already killed with its tree (run_command); the run ends as a tool fault.
            outcome = EXIT_UNSERVED, "", INTERRUPTED_LINE
        except Exception as exc:  # noqa: BLE001 - any unexpected error is a tool fault, never a red and never a traceback
            outcome = EXIT_UNSERVED, "", f"preflight.py: tool fault: {escape(type(exc).__name__)}: {escape(str(exc))}\n"
        return _emit(outcome)
    except KeyboardInterrupt:  # outside the handlers above: the start of the run, the streams, the printing
        return _interrupted()


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
    try:
        code = main()
        _settle("stdout")
        _settle("stderr")
    except KeyboardInterrupt:  # an interrupt in the last flush ends the run as a tool fault too
        return _interrupted()
    return code


if __name__ == "__main__":
    sys.exit(entry())
