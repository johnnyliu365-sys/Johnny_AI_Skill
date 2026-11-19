#!/usr/bin/env python3
"""Machine-form gate for dispatch and review-request messages.

Usage: dispatch_lint.py <dispatch-file> [--chat-words WORD[,WORD...]] [--ticket <ticket-file>]

Rules (each problem line starts with its rule id):
  R1  the first non-blank line is a field (`name: value`)
  R2  every line outside a code fence is a field, a list item, a table row or an
      indented continuation, never prose
  R3  no chat word outside quotes or backticks (default list is the Chinese
      politeness and filler words below; override with --chat-words)
  R4  no sentence terminator (the full-width period) outside quotes or backticks
  R5  one action per line: a line outside a code fence holds at most one action; a clause
      separator (a half-width `;` followed by a space, or a full-width `；`) outside
      backticks starts a second action; quotes do not hide it; the value of a `cmd:` field
      is one action however many shell statements it holds
  R6  no line longer than 2000 characters, inside a code fence or outside (runaway cap)
  R7  only with --ticket: the ticket's state row records the dispatch file's digest.
      R7 reads the first table row of the ticket whose first cell is exactly `狀態`. That
      cell must hold exactly one `dispatch=sha256:`; the run of `[0-9A-Za-z]` after it must
      be 64 characters, all in `[0-9a-f]`, and equal to the sha256 of the dispatch file's
      bytes. What follows the run (a space, `(`, `;` or the end of the cell) is ignored.
      A missing row, an empty cell, a missing or doubled `dispatch=sha256:`, a run of
      another length, upper-case hex or a different digest is a violation; the line names
      the expected and the found digest. Without --ticket the lint is R1 to R6 and R8.
  R8  a dispatch with a top-level `profile:` field also carries top-level `model:` and
      `effort:` fields. Top-level means a field at column 0 outside a code fence. Each of
      the two holds one non-empty item matching `[A-Za-z0-9][A-Za-z0-9._-]*`, optionally
      inside one pair of double quotes; a list is invalid, and so is a field given twice.
      After the per-line rules the lines are, each printed when it applies and in this
      order: `R8 profile: without model:`, `R8 profile: without effort:`,
      `R8 model: invalid`, `R8 effort: invalid`. R8 runs with or without --ticket.

Exit codes: 0 LINT PASS, 1 one or more rule violations, 3 usage error
(missing or extra argument, unreadable or non-UTF-8 dispatch or ticket file, unknown
option, a --chat-words list with no non-blank word, --ticket given without a value or
twice). A bad ticket file is decided before any rule runs and prints nothing on stdout. The console encoding never changes an exit
code: stdout and stderr keep the host encoding but escape what it cannot encode.
"""
from __future__ import annotations

import hashlib
import io
import re
import sys
from collections.abc import Sequence
from pathlib import Path

USAGE = "usage: dispatch_lint.py <dispatch-file> [--chat-words WORD[,WORD...]] [--ticket <ticket-file>]"

FIELD = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_.\- ]*:(\s|$)")
FIRST_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*:")
LIST = re.compile(r"^\s*- ")
DEFAULT_CHAT_WORDS: tuple[str, ...] = ("請", "你", "我們", "注意", "謝謝", "先做", "再做", "麻煩", "辛苦")
MAX_LINE = 2000
CMD_FIELD = re.compile(r"^\s*(?:-\s+)?cmd:(\s|$)")
SEPARATOR = re.compile(r"; |；")
STATE_CELL = "狀態"
DIGEST_TOKEN = "dispatch=sha256:"
DIGEST_RUN = re.compile(r"[0-9A-Za-z]*")
DIGEST_LENGTH = 64
LOWER_HEX = frozenset("0123456789abcdef")
TOP_FIELD = re.compile(r"(profile|model|effort):(.*)")
ITEM = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def count_actions(line: str) -> int:
    """Number of non-blank clauses in a line; backtick spans never split, quotes do."""
    if CMD_FIELD.match(line):
        return 1
    bare = re.sub(r"`[^`]*`", "``", line)
    return max(1, sum(1 for part in SEPARATOR.split(bare) if part.strip()))


def strip_quoted(line: str) -> str:
    """Blank out double-quoted, single-quoted and backticked spans."""
    line = re.sub(r'"[^\"]*"', '""', line)
    line = re.sub(r"'[^']*'", "''", line)
    return re.sub(r"`[^`]*`", "``", line)


def lint(text: str, chat_words: Sequence[str] | None = None) -> list[str]:
    words = DEFAULT_CHAT_WORDS if chat_words is None else tuple(chat_words)
    chat = re.compile("(" + "|".join(re.escape(word) for word in words) + ")") if words else None
    lines = text.splitlines()
    problems: list[str] = []
    first = next((line for line in lines if line.strip()), "")
    if not FIRST_FIELD.match(first):
        problems.append(f"R1 first line is not a field: {first[:80]!r}")
    in_fence = False
    for number, line in enumerate(lines, 1):
        if len(line) > MAX_LINE:
            problems.append(f"R6 line {number} too long ({len(line)})")
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue
        if not (FIELD.match(line) or LIST.match(line) or line.lstrip().startswith("|") or line.startswith("  ")):
            problems.append(f"R2 line {number} is prose, not field/list/continuation: {line.strip()[:80]!r}")
        bare = strip_quoted(line)
        match = chat.search(bare) if chat else None
        if match:
            problems.append(f"R3 line {number} chat word {match.group(1)!r} outside quotes: {line.strip()[:80]!r}")
        if "。" in bare:
            problems.append(f"R4 line {number} sentence terminator outside quotes: {line.strip()[:80]!r}")
        actions = count_actions(line)
        if actions > 1:
            problems.append(f"R5 line {number} holds {actions} actions; put each on its own list item")
    problems.extend(check_seat_binding(lines))
    return problems


def binding_value_valid(raw: str) -> bool:
    """One item of the value grammar, optionally inside one pair of double quotes."""
    value = raw.strip()
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return ITEM.fullmatch(value) is not None


def check_seat_binding(lines: Sequence[str]) -> list[str]:
    """R8: a dispatch with a top-level `profile:` also names its `model:` and `effort:`."""
    found: dict[str, list[str]] = {"profile": [], "model": [], "effort": []}
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        matched = TOP_FIELD.fullmatch(line)
        if matched is not None:
            found[matched.group(1)].append(matched.group(2))
    if not found["profile"]:
        return []
    problems: list[str] = []
    if not found["model"]:
        problems.append("R8 profile: without model:")
    if not found["effort"]:
        problems.append("R8 profile: without effort:")
    for name in ("model", "effort"):
        values = found[name]
        if values and (len(values) > 1 or not binding_value_valid(values[0])):
            problems.append(f"R8 {name}: invalid")
    return problems


def state_cell(ticket_text: str) -> str | None:
    """The 狀態 cell of the first table row whose first cell is exactly `狀態`, or None."""
    for line in ticket_text.splitlines():
        row = line.strip()
        if not row.startswith("|"):
            continue
        first, separator, rest = row[1:].partition("|")
        if separator and first.strip() == STATE_CELL:
            rest = rest.rstrip()
            return (rest[:-1] if rest.endswith("|") else rest).strip()
    return None


def check_dispatch_digest(ticket_text: str, dispatch_bytes: bytes) -> list[str]:
    """R7: the ticket's state row carries the sha256 of the dispatch file's bytes."""
    expected = hashlib.sha256(dispatch_bytes).hexdigest()
    head = f"R7 state row: expected {DIGEST_TOKEN}{expected}, found"
    cell = state_cell(ticket_text)
    if cell is None:
        return [f"{head} no state row"]
    if not cell:
        return [f"{head} an empty state cell"]
    count = cell.count(DIGEST_TOKEN)
    if count == 0:
        return [f"{head} no {DIGEST_TOKEN}"]
    if count > 1:
        return [f"{head} {count} {DIGEST_TOKEN} in the state cell"]
    match = DIGEST_RUN.match(cell.partition(DIGEST_TOKEN)[2])
    found = match.group(0) if match else ""
    shown = found if found else "nothing"
    if len(found) != DIGEST_LENGTH:
        return [f"{head} {shown} ({len(found)} characters, not {DIGEST_LENGTH})"]
    if not set(found) <= LOWER_HEX:
        return [f"{head} {found} (not 64 lower-case hex digits)"]
    if found != expected:
        return [f"{head} {found} (a different digest)"]
    return []


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
        print(f"dispatch_lint.py: error: {message}", file=sys.stderr)
    return 3


def main(argv: Sequence[str] | None = None) -> int:
    _harden_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    chat_words: list[str] | None = None
    ticket: str | None = None
    positional: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--chat-words":
            if index + 1 >= len(args):
                return _usage_error("--chat-words needs a value")
            chat_words = [word for word in args[index + 1].split(",") if word.strip()]
            if not chat_words:
                return _usage_error("--chat-words needs at least one non-blank word")
            index += 2
            continue
        if arg == "--ticket":
            if index + 1 >= len(args):
                return _usage_error("--ticket needs a value")
            if ticket is not None:
                return _usage_error("--ticket given twice")
            ticket = args[index + 1]
            index += 2
            continue
        if arg.startswith("-"):
            return _usage_error(f"unknown option {arg}")
        positional.append(arg)
        index += 1
    if len(positional) != 1:
        return _usage_error()
    try:
        data = Path(positional[0]).read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _usage_error(f"cannot read {positional[0]}: {exc}")
    ticket_text: str | None = None
    if ticket is not None:
        try:
            ticket_text = Path(ticket).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return _usage_error(f"cannot read {ticket}: {exc}")
    problems = lint(text, chat_words)
    if ticket_text is not None:
        problems.extend(check_dispatch_digest(ticket_text, data))
    for problem in problems:
        print(problem)
    print("LINT PASS" if not problems else f"LINT FAIL ({len(problems)})")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
