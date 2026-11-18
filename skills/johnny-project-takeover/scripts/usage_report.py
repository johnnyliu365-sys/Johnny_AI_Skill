"""Usage report: every receipt records its token use per seat, compared with the expectation.

Usage:
  usage_report.py --expectation FILE RECEIPT [RECEIPT ...]

The expectation file is a JSON object with one entry per semantic profile; an entry is an object
with exactly `output_tokens_max` and `processed_tokens_max`, two integers >= 0. A receipt holds
`## USAGE <seat>` sections (the grammar evidence_gate.py validates): the lines `cell: USAGE`,
`seat`, `profile`, `model`, `input_tokens`, `cache_write_tokens`, `cache_read_tokens`,
`output_tokens` and `source`, in this order, one per line.

For every USAGE cell one line is printed:
  `<seat> <profile> output=<n> processed=<n> <verdict>`
where processed is input + cache write + cache read and the verdict is WITHIN, OVER_OUTPUT
(output > output_tokens_max), OVER_PROCESSED (processed > processed_tokens_max), both of the last
two joined by a comma when both hold, or UNKNOWN_PROFILE. A value equal to its maximum is WITHIN.
A receipt without a USAGE cell prints `NO_USAGE <receipt>`.

Exit codes: 0 every seat is within its expectation; 1 a receipt has no USAGE cell, a profile is
unknown, or a seat is over its expectation (every one is listed); 2 a receipt or the expectation
file cannot be read or breaks its schema (each fault is one line on standard error, and 2 wins
over 1); 3 usage error. JSON input refuses repeated keys, NaN and Infinity. Every printed subject
is escaped to one line. Standard library only. Output uses LF.
"""
from __future__ import annotations

import io
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

EXIT_PASS = 0
EXIT_RED = 1
EXIT_FAULT = 2
EXIT_USAGE = 3

USAGE = "usage: usage_report.py --expectation FILE RECEIPT [RECEIPT ...]"

FENCE = "`" * 4
HORIZONTAL_SPACE = " \t"
USAGE_CELL = "USAGE"
FIELDS = (
    "cell",
    "seat",
    "profile",
    "model",
    "input_tokens",
    "cache_write_tokens",
    "cache_read_tokens",
    "output_tokens",
    "source",
)
COUNT_FIELDS = ("input_tokens", "cache_write_tokens", "cache_read_tokens", "output_tokens")
FIELD_LINE = re.compile(r"([A-Za-z_]+):[ \t]*(.*)")
COUNT = re.compile(r"0|[1-9][0-9]*")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
SEAT = re.compile(r"seat:([A-Za-z0-9][A-Za-z0-9._-]*)/([A-Za-z0-9][A-Za-z0-9._-]*)")
LIMIT_KEYS = ("output_tokens_max", "processed_tokens_max")

WITHIN = "WITHIN"
OVER_OUTPUT = "OVER_OUTPUT"
OVER_PROCESSED = "OVER_PROCESSED"
UNKNOWN_PROFILE = "UNKNOWN_PROFILE"
NO_USAGE = "NO_USAGE"


class InputFault(Exception):
    """A receipt or the expectation file cannot be read or breaks its schema (exit 2)."""


class UsageError(Exception):
    """The command line is malformed (exit 3)."""


def printable(text: str) -> str:
    """`text` escaped (Python repr rules, without the outer quotes) so it stays on one line."""
    return repr(text)[1:-1]


def has_bad_text(text: str) -> bool:
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F or 0xD800 <= ord(ch) <= 0xDFFF for ch in text)


@dataclass(frozen=True)
class Limits:
    output_tokens_max: int
    processed_tokens_max: int


@dataclass(frozen=True)
class Seat:
    seat: str
    profile: str
    output_tokens: int
    processed_tokens: int


@dataclass(frozen=True)
class Arguments:
    expectation: Path
    receipts: tuple[Path, ...]


# ----------------------------------------------------------------------------- arguments


def parse_arguments(argv: Sequence[str]) -> Arguments:
    expectation: str | None = None
    receipts: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        index += 1
        if token.startswith("--"):
            name, equals, inline = token.partition("=")
            if name != "--expectation":
                raise UsageError(f"unknown option {printable(name)}")
            if equals:
                value = inline
            else:
                if index >= len(argv):
                    raise UsageError("--expectation needs a value")
                value = argv[index]
                index += 1
            if expectation is not None:
                raise UsageError("--expectation given twice")
            expectation = value
        elif token.startswith("-") and len(token) > 1:
            raise UsageError(f"unknown option {printable(token)}")
        else:
            receipts.append(token)
    if expectation is None or not expectation.strip():
        raise UsageError("--expectation is required")
    if not receipts:
        raise UsageError("at least one receipt is required")
    if any(not receipt.strip() for receipt in receipts):
        raise UsageError("a receipt path must not be blank")
    return Arguments(Path(expectation), tuple(Path(receipt) for receipt in receipts))


# ----------------------------------------------------------------------------- strict JSON


def refuse_constant(name: str) -> NoReturn:
    raise ValueError(f"constant {name} is refused")


def refuse_repeats(pairs: list[tuple[str, object]]) -> dict[str, object]:
    found: dict[str, object] = {}
    for key, value in pairs:
        if key in found:
            raise ValueError(f"the key {printable(key)} is repeated in an object")
        found[key] = value
    return found


def read_file(path: Path, what: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise InputFault(f"cannot read {what} {printable(str(path))}: {printable(str(error))}") from error


def load_expectation(path: Path) -> dict[str, Limits]:
    raw = read_file(path, "expectation file")
    origin = f"expectation file {printable(str(path))}"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InputFault(f"{origin} is not UTF-8 ({error.reason})") from error
    if text.startswith("﻿"):
        raise InputFault(f"{origin} starts with a byte order mark")
    try:
        data: object = json.loads(text, object_pairs_hook=refuse_repeats, parse_constant=refuse_constant)
    except (ValueError, RecursionError) as error:
        raise InputFault(f"{origin} is not accepted JSON: {printable(str(error))}") from error
    if not isinstance(data, dict) or not data:
        raise InputFault(f"{origin} is not a non-empty JSON object of profiles")
    limits: dict[str, Limits] = {}
    for profile, entry in data.items():
        if NAME.fullmatch(profile) is None:
            raise InputFault(f"{origin}: {printable(profile)} is not a profile reference")
        if not isinstance(entry, dict):
            raise InputFault(f"{origin}: profile {printable(profile)} is not an object")
        for key in LIMIT_KEYS:
            if key not in entry:
                raise InputFault(f"{origin}: profile {printable(profile)} lacks {key}")
        for key in entry:
            if key not in LIMIT_KEYS:
                raise InputFault(f"{origin}: profile {printable(profile)} has the unknown key {printable(str(key))}")
        output_max: object = entry[LIMIT_KEYS[0]]
        processed_max: object = entry[LIMIT_KEYS[1]]
        if not isinstance(output_max, int) or isinstance(output_max, bool) or output_max < 0:
            raise InputFault(f"{origin}: profile {printable(profile)} {LIMIT_KEYS[0]} is not an integer >= 0")
        if not isinstance(processed_max, int) or isinstance(processed_max, bool) or processed_max < 0:
            raise InputFault(f"{origin}: profile {printable(profile)} {LIMIT_KEYS[1]} is not an integer >= 0")
        limits[profile] = Limits(output_max, processed_max)
    return limits


# ----------------------------------------------------------------------------- receipts


def split_usage_sections(text: str) -> list[tuple[str, list[str]]]:
    """Each `## ` section whose cell: line says USAGE, as (heading, lines outside fences); fences respected."""
    sections: list[tuple[str, list[str]]] = []
    current: tuple[str, list[str]] | None = None
    in_fence = False
    for line in text.split("\n"):
        is_fence = line.rstrip() == FENCE
        if not in_fence and line.startswith("## ") and not is_fence:
            current = (line[3:].strip(HORIZONTAL_SPACE), [])
            sections.append(current)
            continue
        if is_fence:
            in_fence = not in_fence
            if current is not None:
                current[1].append(FENCE)
            continue
        if current is not None and not in_fence:
            current[1].append(line)
    found: list[tuple[str, list[str]]] = []
    for heading, lines in sections:
        for line in lines:
            matched = FIELD_LINE.fullmatch(line.rstrip(HORIZONTAL_SPACE))
            if matched is not None and matched.group(1) == "cell":
                if matched.group(2).strip(HORIZONTAL_SPACE) == USAGE_CELL:
                    found.append((heading, lines))
                break
    return found


def parse_usage(heading: str, lines: Sequence[str], origin: str) -> Seat:
    def refuse(reason: str) -> InputFault:
        return InputFault(f"{origin}: section {printable(heading)}: {reason}")

    values: dict[str, str] = {}
    order: list[str] = []
    for raw in lines:
        line = raw.rstrip(HORIZONTAL_SPACE)
        if not line:
            continue
        if has_bad_text(line.replace("\t", " ")):
            raise refuse("a line holds a control character")
        if line == FENCE:
            raise refuse("a USAGE cell carries a fenced block")
        matched = FIELD_LINE.fullmatch(line)
        if matched is None:
            raise refuse(f"line is not `name: value`: {printable(line)}")
        name, value = matched.group(1), matched.group(2).strip(HORIZONTAL_SPACE)
        if name not in FIELDS:
            raise refuse(f"unknown field {printable(name)}: (run fields are not allowed)")
        if name in values:
            raise refuse(f"{name}: given more than once")
        values[name] = value
        order.append(name)
    for name in FIELDS:
        if name not in values:
            raise refuse(f"field {name} is missing")
    if order != list(FIELDS):
        raise refuse(f"fields are out of order: {','.join(order)}")
    for name in ("model", "source"):
        if not values[name] or has_bad_text(values[name]):
            raise refuse(f"{name} is empty or holds a control character")
    for name in COUNT_FIELDS:
        if COUNT.fullmatch(values[name]) is None:
            raise refuse(f"{name} is not an integer >= 0: {printable(values[name])}")
    seat = SEAT.fullmatch(values["seat"])
    if seat is None:
        raise refuse(f"seat is not seat:<profile>/<run-id>: {printable(values['seat'])}")
    if NAME.fullmatch(values["profile"]) is None or seat.group(1) != values["profile"]:
        raise refuse("profile is not the profile the seat names")
    if heading != f"{USAGE_CELL} {values['seat']}":
        raise refuse(f"heading must be '{USAGE_CELL} {printable(values['seat'])}'")
    processed = int(values["input_tokens"]) + int(values["cache_write_tokens"]) + int(values["cache_read_tokens"])
    return Seat(values["seat"], values["profile"], int(values["output_tokens"]), processed)


def load_receipt(path: Path) -> list[Seat]:
    raw = read_file(path, "receipt")
    origin = f"receipt {printable(str(path))}"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InputFault(f"{origin} is not UTF-8 ({error.reason})") from error
    if text.startswith("﻿"):
        text = text[1:]
    text = text.replace("\r\n", "\n")
    seats: list[Seat] = []
    seen: set[str] = set()
    for heading, lines in split_usage_sections(text):
        seat = parse_usage(heading, lines, origin)
        if seat.seat in seen:
            raise InputFault(f"{origin}: seat {printable(seat.seat)} has two USAGE cells")
        seen.add(seat.seat)
        seats.append(seat)
    return seats


# ----------------------------------------------------------------------------- verdicts


def verdict(seat: Seat, limits: dict[str, Limits]) -> str:
    expected = limits.get(seat.profile)
    if expected is None:
        return UNKNOWN_PROFILE
    over: list[str] = []
    if seat.output_tokens > expected.output_tokens_max:
        over.append(OVER_OUTPUT)
    if seat.processed_tokens > expected.processed_tokens_max:
        over.append(OVER_PROCESSED)
    return ",".join(over) if over else WITHIN


def execute(args: Arguments) -> int:
    faults: list[str] = []
    try:
        limits = load_expectation(args.expectation)
    except InputFault as error:
        faults.append(str(error))
        limits = {}
    red = False
    lines: list[str] = []
    for path in args.receipts:
        try:
            seats = load_receipt(path)
        except InputFault as error:
            faults.append(str(error))
            continue
        if not seats:
            lines.append(f"{NO_USAGE} {printable(str(path))}")
            red = True
            continue
        for seat in seats:
            result = verdict(seat, limits)
            if result != WITHIN:
                red = True
            lines.append(
                f"{printable(seat.seat)} {printable(seat.profile)} "
                f"output={seat.output_tokens} processed={seat.processed_tokens} {result}"
            )
    if faults:
        for message in faults:
            print(f"input fault: {message}", file=sys.stderr)
        return EXIT_FAULT
    for line in lines:
        print(line)
    return EXIT_RED if red else EXIT_PASS


def main(argv: Sequence[str]) -> int:
    try:
        args = parse_arguments(argv)
    except UsageError as error:
        print(f"{USAGE}\nerror: {error}", file=sys.stderr)
        return EXIT_USAGE
    try:
        return execute(args)
    except Exception as error:  # an unexpected error is a fault, never a pass
        print(f"input fault: unexpected {type(error).__name__}: {printable(str(error))}", file=sys.stderr)
        return EXIT_FAULT


def configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace", newline="\n")


if __name__ == "__main__":
    configure_streams()
    sys.exit(main(sys.argv[1:]))
