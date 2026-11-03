#!/usr/bin/env python3
"""Machine-form gate for dispatch and review-request messages.

Usage: dispatch_lint.py <dispatch-file> [--chat-words WORD[,WORD...]]

Rules (each problem line starts with its rule id):
  R1  the first non-blank line is a field (`name: value`)
  R2  every line outside a code fence is a field, a list item, a table row or an
      indented continuation, never prose
  R3  no chat word outside quotes or backticks (default list is the Chinese
      politeness and filler words below; override with --chat-words)
  R4  no sentence terminator (the full-width period) outside quotes or backticks
  R5  no line longer than 400 characters

Exit codes: 0 LINT PASS, 1 one or more rule violations, 3 usage error
(missing or extra argument, unreadable or non-UTF-8 file, unknown option, a
--chat-words list with no non-blank word).
"""
from __future__ import annotations

import re
import sys
from collections.abc import Sequence
from pathlib import Path

USAGE = "usage: dispatch_lint.py <dispatch-file> [--chat-words WORD[,WORD...]]"

FIELD = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_.\- ]*:(\s|$)")
FIRST_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*:")
LIST = re.compile(r"^\s*- ")
DEFAULT_CHAT_WORDS: tuple[str, ...] = ("請", "你", "我們", "注意", "謝謝", "先做", "再做", "麻煩", "辛苦")
MAX_LINE = 400


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
        if len(line) > MAX_LINE:
            problems.append(f"R5 line {number} too long ({len(line)})")
    return problems


def _usage_error(message: str | None = None) -> int:
    print(USAGE, file=sys.stderr)
    if message:
        print(f"dispatch_lint.py: error: {message}", file=sys.stderr)
    return 3


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    chat_words: list[str] | None = None
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
        if arg.startswith("-"):
            return _usage_error(f"unknown option {arg}")
        positional.append(arg)
        index += 1
    if len(positional) != 1:
        return _usage_error()
    try:
        text = Path(positional[0]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _usage_error(f"cannot read {positional[0]}: {exc}")
    problems = lint(text, chat_words)
    for problem in problems:
        print(problem)
    print("LINT PASS" if not problems else f"LINT FAIL ({len(problems)})")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
