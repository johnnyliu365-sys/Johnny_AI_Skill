"""Rework report: every code-review record counts its review rounds and the cause of each rework.

Usage:
  rework_report.py RECORD...

A RECORD is one code-review record (`doc/reviews/<feature>/<ticket>-...-code-review.md`). It holds
exactly one ticket, whose id is the file name up to its first `-`. Each review section of the
record ends with a fenced `rework-record` block that directly follows the section's
`review-verdict` block; a `CHANGE_DETECTED` return before any review has a `RETURN` block that
stands before the first review section. The block holds exactly these five lines, in this order,
each key once:

  candidate: <40 lower-case hex, or none (a RETURN block only)>
  round: <1, 2, 3 ... in order of appearance in the record; no leading zero>
  kind: INITIAL | CORRECTION | RETURN
  verdict: APPROVED | CHANGES_REQUESTED | BLOCKED | CONVERGENCE_REVIEW_REQUIRED | CHANGE_DETECTED
  causes: <empty, or causes joined by "," with no blank and no repeat, in this order:
          CONTROL_PLANE_RULE, RETURN_UNTRUE, DESIGN_UNFORESEEN, IMPLEMENTATION_DETAIL>

The causes follow from the findings (CodeReview.md section 3 and 4): they are empty for APPROVED, and
for CONVERGENCE_REVIEW_REQUIRED only when the record holds a convergence-disposition for that
candidate that says `disposition: APPROVED`; they are not empty for CHANGES_REQUESTED, BLOCKED
and CHANGE_DETECTED. A RETURN block names DESIGN_UNFORESEEN and nothing else.

Output, on stdout, in this order:
  one line per ticket: `<ticket> rounds=<n> CONTROL_PLANE_RULE=<a> RETURN_UNTRUE=<b>
    DESIGN_UNFORESEEN=<c> IMPLEMENTATION_DETAIL=<d> final=<verdict>` (a cause counts the rounds
    that name it; final is the last round's verdict as recorded); a record with a red has no line;
  `TOTAL tickets=<t> rounds=<n> CONTROL_PLANE_RULE=<a> RETURN_UNTRUE=<b> DESIGN_UNFORESEEN=<c>
    IMPLEMENTATION_DETAIL=<d>`;
  one line per red, naming the record and the reason.

Exit codes: 0 no red and no fault; 1 a red (every red is printed, and each fault goes to
standard error); 2 no red, but a record is unreadable or not UTF-8; 3 usage error. Red before fault,
as R4-2 sets it for every gate. Every printed subject is escaped to one line. Standard library only.
Output uses LF.
"""
from __future__ import annotations

import io
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePath

EXIT_PASS = 0
EXIT_RED = 1
EXIT_FAULT = 2
EXIT_USAGE = 3

USAGE = "usage: rework_report.py RECORD..."

CAUSES = ("CONTROL_PLANE_RULE", "RETURN_UNTRUE", "DESIGN_UNFORESEEN", "IMPLEMENTATION_DETAIL")
KINDS = ("INITIAL", "CORRECTION", "RETURN")
VERDICTS = ("APPROVED", "CHANGES_REQUESTED", "BLOCKED", "CONVERGENCE_REVIEW_REQUIRED", "CHANGE_DETECTED")
FIELDS = ("candidate", "round", "kind", "verdict", "causes")
RETURN_KIND = "RETURN"
RETURN_VERDICT = "CHANGE_DETECTED"
RETURN_CAUSE = "DESIGN_UNFORESEEN"
NO_CANDIDATE = "none"

REWORK_TAG = "rework-record"
VERDICT_TAG = "review-verdict"
DISPOSITION_TAG = "convergence-disposition"

FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([^\s`]*)[^`]*$")
FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
FIELD_LINE = re.compile(r"([a-z_]+):(?: (.*))?")
VERDICT_LINE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*?)[ \t]*")
CANDIDATE = re.compile(r"[0-9a-f]{40}")
ROUND = re.compile(r"[1-9][0-9]*")


class UsageError(Exception):
    """The command line is malformed (exit 3)."""


def printable(text: str) -> str:
    """`text` escaped (Python repr rules, without the outer quotes) so it stays on one line."""
    return repr(text)[1:-1]


# ----------------------------------------------------------------------------- fences


@dataclass(frozen=True)
class Fence:
    tag: str
    line: int  # 1-based line of the opening fence
    body: tuple[str, ...]
    closed: bool


def parse_fences(text: str) -> list[Fence]:
    """Every top-level fenced block of `text`, in order; a fence inside another fence is body text."""
    fences: list[Fence] = []
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        opened = FENCE_OPEN.match(lines[index].rstrip("\r"))
        index += 1
        if opened is None:
            continue
        fence, tag = opened.group(1), opened.group(2)
        start = index
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
        fences.append(Fence(tag, start, tuple(body), closed))
    return fences


def block_fields(fence: Fence) -> dict[str, list[str]]:
    """The `key: value` lines of a review-verdict or convergence-disposition block (the reading integrate.py uses)."""
    fields: dict[str, list[str]] = {}
    for line in fence.body:
        if not line.strip(" \t") or line[0] in " \t-":
            continue
        matched = VERDICT_LINE.fullmatch(line)
        if matched is not None:
            fields.setdefault(matched.group(1), []).append(matched.group(2))
    return fields


def single(fields: dict[str, list[str]], name: str) -> str | None:
    values = fields.get(name, [])
    return values[0] if len(values) == 1 else None


# ----------------------------------------------------------------------------- judging one record


@dataclass(frozen=True)
class Round:
    candidate: str
    number: int
    kind: str
    verdict: str
    causes: tuple[str, ...]


@dataclass(frozen=True)
class Judgement:
    rounds: tuple[Round, ...]
    reds: tuple[str, ...]


@dataclass(frozen=True)
class Parsed:
    values: dict[str, str]
    reds: tuple[tuple[str, str], ...]  # (code, detail)


def read_block(fence: Fence) -> Parsed:
    """The five fields of a rework-record block, and the structural reds found in them."""
    seen: dict[str, list[str]] = {}
    order: list[str] = []
    reds: list[tuple[str, str]] = []
    for line in fence.body:
        matched = FIELD_LINE.fullmatch(line)
        if matched is None or matched.group(1) not in FIELDS:
            reds.append(("FIELD_UNKNOWN", f"the line {printable(line)} is not one of the five fields"))
            continue
        name = matched.group(1)
        order.append(name)
        seen.setdefault(name, []).append(matched.group(2) or "")
    for name in FIELDS:
        count = len(seen.get(name, []))
        if count == 0:
            reds.append(("FIELD_MISSING", f"the field {name} is missing"))
        elif count > 1:
            reds.append(("FIELD_REPEATED", f"the field {name} is repeated"))
    if not reds and tuple(order) != FIELDS:
        reds.append(("FIELD_ORDER", "the fields are not in the order " + ", ".join(FIELDS)))
    return Parsed({name: values[0] for name, values in seen.items()}, tuple(reds))


def cause_list(text: str) -> tuple[tuple[str, ...], tuple[str, str] | None]:
    """The causes of `text` and the first red found in it, if any."""
    if text == "":
        return (), None
    if any(ch in " \t" for ch in text):
        return (), ("VALUE_INVALID", f"causes {printable(text)} holds a blank")
    items = text.split(",")
    if any(item == "" for item in items):
        return (), ("VALUE_INVALID", f"causes {printable(text)} holds an empty item")
    for item in items:
        if item not in CAUSES:
            return (), ("UNKNOWN_CAUSE", f"{printable(item)} is not a cause")
    positions = [CAUSES.index(item) for item in items]
    if positions != sorted(set(positions)):
        return (), ("VALUE_INVALID", f"causes {printable(text)} repeats a cause or is out of table order")
    return tuple(items), None


def disposition_approves(fences: Sequence[Fence], candidate: str) -> bool:
    """True when the record holds a convergence-disposition for `candidate` that says disposition: APPROVED."""
    for fence in fences:
        if fence.tag != DISPOSITION_TAG or not fence.closed:
            continue
        fields = block_fields(fence)
        if single(fields, "candidate") == candidate and single(fields, "disposition") == "APPROVED":
            return True
    return False


def judge_block(fence: Fence, position: int, fences: Sequence[Fence]) -> tuple[Round | None, list[tuple[int, str, str]]]:
    """Judge one rework-record block; its round when it holds no red, and every red found."""
    found: list[tuple[int, str, str]] = []

    def red(code: str, detail: str) -> None:
        found.append((fence.line, code, detail))

    parsed = read_block(fence)
    for code, detail in parsed.reds:
        red(code, detail)
    values = parsed.values
    candidate = values.get("candidate")
    number_text = values.get("round")
    kind = values.get("kind")
    verdict = values.get("verdict")
    causes_text = values.get("causes")
    if candidate is not None and CANDIDATE.fullmatch(candidate) is None and candidate != NO_CANDIDATE:
        red("VALUE_INVALID", f"candidate {printable(candidate)} is not 40 lower-case hex digits or none")
    if candidate == NO_CANDIDATE and kind != RETURN_KIND:
        red("VALUE_INVALID", "candidate none is allowed in a RETURN block only")
    number = 0
    if number_text is not None:
        if ROUND.fullmatch(number_text) is None:
            red("VALUE_INVALID", f"round {printable(number_text)} is not a positive number without a leading zero")
        else:
            number = int(number_text)
    if number != 0 and number != position:
        red("ROUND_SEQUENCE", f"round {number} stands at position {position}")
    if kind is not None and kind not in KINDS:
        red("VALUE_INVALID", f"kind {printable(kind)} is not INITIAL, CORRECTION or RETURN")
    if verdict is not None and verdict not in VERDICTS:
        red("VALUE_INVALID", f"verdict {printable(verdict)} is not a verdict of the block")
    if kind == RETURN_KIND and verdict is not None and verdict != RETURN_VERDICT:
        red("VALUE_INVALID", "a RETURN block has the verdict CHANGE_DETECTED")
    causes: tuple[str, ...] = ()
    causes_listed = False
    if causes_text is not None:
        causes, problem = cause_list(causes_text)
        if problem is None:
            causes_listed = True
        else:
            red(problem[0], problem[1])
    # the causes follow from the findings (item 3)
    if causes_listed and candidate is not None and verdict in VERDICTS:
        empty_expected = verdict == "APPROVED" or (
            verdict == "CONVERGENCE_REVIEW_REQUIRED" and disposition_approves(fences, candidate)
        )
        if kind == RETURN_KIND:
            if causes != (RETURN_CAUSE,):
                red("CAUSES_RULE", "a RETURN block names DESIGN_UNFORESEEN and nothing else")
        elif empty_expected and causes:
            red("CAUSES_RULE", f"the causes of this {verdict} round are empty")
        elif not empty_expected and not causes:
            red("CAUSES_RULE", f"the causes of this {verdict} round are not empty")
    # pairing with the review-verdict block
    verdict_fences = [item for item in fences if item.tag == VERDICT_TAG]
    if kind == RETURN_KIND:
        if verdict_fences and verdict_fences[0].line < fence.line:
            red("RETURN_AFTER_VERDICT", "a RETURN block stands after the first review-verdict block")
    else:
        before = [item for item in verdict_fences if item.line < fence.line]
        if not before:
            red("NO_REVIEW_VERDICT", "no review-verdict block stands before this block")
        else:
            paired = block_fields(before[-1])
            if verdict is not None and single(paired, "verdict") != verdict:
                red("VERDICT_MISMATCH", f"the verdict differs from the review-verdict block at line {before[-1].line}")
            if candidate is not None and single(paired, "candidate") != candidate:
                red("CANDIDATE_MISMATCH", f"the candidate differs from the review-verdict block at line {before[-1].line}")
    if found or candidate is None or kind is None or verdict is None:
        return None, found
    return Round(candidate, number, kind, verdict, causes), found


def judge(text: str) -> Judgement:
    """Judge the text of one record; every red is returned with its line, none is raised."""
    fences = parse_fences(text)
    found: list[tuple[int, str, str]] = []  # (line, code, detail)
    for fence in fences:
        if not fence.closed:
            found.append((fence.line, "UNCLOSED_FENCE", "a fence is never closed"))
    blocks = [fence for fence in fences if fence.tag == REWORK_TAG]
    if not blocks:
        found.append((0, "NO_REWORK_RECORD", "the record holds no rework-record block"))
    rounds: list[Round] = []
    for position, fence in enumerate(blocks, start=1):
        item, block_reds = judge_block(fence, position, fences)
        found.extend(block_reds)
        if item is not None:
            rounds.append(item)
    found.sort(key=lambda entry: entry[0])
    reds = tuple(
        (f"{code} (line {line}): {detail}" if line else f"{code}: {detail}") for line, code, detail in found
    )
    return Judgement(tuple(rounds), reds)


# ----------------------------------------------------------------------------- running


@dataclass(frozen=True)
class Totals:
    tickets: int
    rounds: int
    counts: tuple[int, int, int, int]


def ticket_id(path: str) -> str:
    return PurePath(path).name.partition("-")[0]


def count_line(label: str, rounds: int, counts: Sequence[int]) -> str:
    parts = " ".join(f"{cause}={count}" for cause, count in zip(CAUSES, counts))
    return f"{label} rounds={rounds} {parts}"


def execute(records: Sequence[str]) -> int:
    lines: list[str] = []
    red_lines: list[str] = []
    faults: list[str] = []
    seen_tickets: dict[str, str] = {}
    totals = [0, 0, 0, 0]
    ticket_count = 0
    round_count = 0
    for record in records:
        name = printable(record)
        ticket = ticket_id(record)
        record_reds: list[str] = []
        if ticket == "":
            record_reds.append(f"{name} TICKET_ID: the file name gives no ticket id before its first -")
        elif ticket in seen_tickets:
            record_reds.append(f"{name} DUPLICATE_TICKET: ticket {printable(ticket)} is already held by {seen_tickets[ticket]}")
        else:
            seen_tickets[ticket] = name
        try:
            raw = Path(record).read_bytes()
        except OSError as error:
            faults.append(f"{name}: cannot read the record: {printable(str(error))}")
            red_lines.extend(record_reds)
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            faults.append(f"{name}: the record is not UTF-8 ({printable(error.reason)})")
            red_lines.extend(record_reds)
            continue
        judgement = judge(text)
        record_reds.extend(f"{name} {red}" for red in judgement.reds)
        red_lines.extend(record_reds)
        if record_reds:
            continue
        counts = [sum(1 for item in judgement.rounds if cause in item.causes) for cause in CAUSES]
        lines.append(count_line(printable(ticket), len(judgement.rounds), counts) + f" final={judgement.rounds[-1].verdict}")
        ticket_count += 1
        round_count += len(judgement.rounds)
        totals = [total + count for total, count in zip(totals, counts)]
    lines.append(count_line(f"TOTAL tickets={ticket_count}", round_count, totals))
    for line in lines + red_lines:
        print(line)
    for fault in faults:
        print(f"input fault: {fault}", file=sys.stderr)
    if red_lines:
        return EXIT_RED
    return EXIT_FAULT if faults else EXIT_PASS


def main(argv: Sequence[str]) -> int:
    try:
        if not argv:
            raise UsageError("at least one record is required")
        for token in argv:
            if token.startswith("-") and len(token) > 1:
                raise UsageError(f"unknown option {printable(token)}")
            if not token.strip():
                raise UsageError("a record path must not be blank")
    except UsageError as error:
        print(f"{USAGE}\nerror: {error}", file=sys.stderr)
        return EXIT_USAGE
    try:
        return execute(argv)
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
