"""Governance consistency: the ticket 47 one-off sweeps, held as a test (ticket 58, change-log row 13).

Ticket 47 proved the Revision 04 governance rewrite with three evidence scripts that were run once:
`doc/reviews/workflow-governance/evidence/47/d7_sweep.py` (the retired-rule sweep), `d8_precedence.py`
(the precedence note on historical SPECs and dated handover runbooks) and the D9 grep (the precedence
sentence of `Workflow.md` section 0). Those scripts stay as reviewed. This test carries their rules
forward so that a reworded document that brings a retired rule back goes red in CI, with the
additions ticket 58 lists:

* the sweep runs over the routed set and over every SPEC under `modules/spec/` and every runbook
  under `doc/runbooks/`; a hit in a historical SPEC or runbook is tolerated only under the
  precedence note and is reported by file and count (row 13);
* both halves of R4-1 (a pending dispatch is the ticket state row plus the dispatch-file digest;
  the queue holds integration candidates only), as retired phrasings and as positive statements
  in `AGENTS.md`, `Workflow.md` section 0 and the SPEC's R4-1 (N8-04);
* R3-07 and N9-06: no sentence names a reviewer, a fixed integrator or "the reviewer who approved
  it" as the one who integrates, merges, pushes or lands; the words "integration script" no longer
  mask such a sentence; the Chinese 代為 commit form and the queue-row dispatch form are patterns;
* N9-04: the absence of the precedence note on `modules/spec/TEMPLATE.md` and `README.md` is
  checked with the regular expression that checks presence;
* N9-05: the precedence sentence is pinned by rule and by place.

Every pattern is data (see PATTERNS and the tables after it), one comment per source finding, and has
an injection case below: a copy of the routed documents in a temporary directory with one retired
sentence restored, which must go red; the unmodified copy must stay green.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The routed governance set: the roots of the ticket 47 D7 instrument (revision09).
ROUTED_ROOTS: tuple[str, ...] = (
    "AGENTS.md",
    "Workflow.md",
    "CodeReview.md",
    "skills",
    "modules/spec/workflow-governance.md",
    "doc/runbooks/dispatch-model-profile.md",
    "template",
)
SPEC_DIRECTORY = "modules/spec"
RUNBOOK_DIRECTORY = "doc/runbooks"
ROUTED_RUNBOOK = "doc/runbooks/dispatch-model-profile.md"
GOVERNANCE_SPEC = "modules/spec/workflow-governance.md"
SPEC_TEMPLATE = "modules/spec/TEMPLATE.md"
SPEC_INDEX = "modules/spec/README.md"
# D8: the three files of modules/spec/ that are not historical SPECs.
SPEC_NOT_HISTORICAL: tuple[str, ...] = (GOVERNANCE_SPEC, SPEC_TEMPLATE, SPEC_INDEX)
# Row 13 / N9-04: these two must carry no precedence note, however it is worded.
NOTE_FORBIDDEN: tuple[str, ...] = (SPEC_TEMPLATE, SPEC_INDEX)
WORKFLOW = "Workflow.md"
AGENTS = "AGENTS.md"
CODE_REVIEW = "CodeReview.md"

# ------------------------------------------------------------------ patterns (data)

NOUN = (
    r"(live[- ]descriptor|pending descriptor|dispatch descriptor|its descriptor|receipt-bound|"
    r"PendingDispatchDescriptor|merge-queue file|durable bridge|the bridge\b)"
)
VERB = r"\b(mandatory|required|requires?|must|default|keeps?|retains?|reserved|bound|only)\b"
# Bridge-internal sentences that state the Revision 04 rule (ticket 47 D7, unchanged).
BRIDGE_EXEMPT: tuple[str, ...] = (
    r"\bR4-1\b", r"not the default", r"\bNOT_REQUIRED\b", r"\bnot required\b", r"does not (consume|require)",
    r"bridge-free", r"until (it retires|wave 3)", r"no receipt, descriptor", r"must not halt",
    r"is `NOT_REQUIRED`", r"needs no bridge", r"bridge (route|path)", r"transitional", r"過渡", r"\bneither\b",
    r"requires? no\b", r"nor requires?", r"must not\b", r"\boptional\b",
)
# N9-06: only a negation of the executor itself exempts a sentence that names a reviewer next to an
# integration verb. "integration script", "整合腳本" and R4-4 no longer do: the F-07 injection
# ("by the reviewer who approved it") sits in a sentence that names the script.
REVIEWER_NEGATED: tuple[str, ...] = (
    r"not by the reviewer", r"never the reviewer", r"is not the reviewer", r"not the reviewer\b",
    r"reviewer never\b", r"who is not (that candidate|its reviewer)", r"is not its reviewer",
    r"does not (integrate|merge|push|land)", r"never (integrates|merges|pushes|lands|submits)",
    r"differs from", r"superseded", r"\bnot (by|via) a reviewer",
)
# S58-01 and S58-10 (revision02): a Chinese negation exempts a sentence only when it negates the reviewer as
# the executor, which means an executor verb follows it directly. After the reviewer: 審閱者不得代為,
# 審閱者不得整合 (the negation, then an executor verb). Before the reviewer: 不由審閱者執行, 並非審閱者整合,
# or an executor verb just before the negation (整合不由審閱者, 整合者並非審閱者). A 不得 of an unrelated clause
# ("審閱者不得略過閘門，核准後代為 commit") exempts nothing, and neither does a negation whose verb is another.
_ZH_REVIEWER = r"(?:審閱者|審查者|reviewer)"
_ZH_EXECUTOR_VERB = r"(?:代為|整合|合併|推送|落地|執行|commit)"
_ZH_NEGATION = r"(?:不由|不是|並非|而非|不等於|不指定|不得由|不可由|不能由|非由)"
_ZH_NEGATION_AFTER = r"(?:不得|不可|不能|不會|不是|並非|不等於|不指定)"
REVIEWER_NEGATED_ZH: tuple[str, ...] = (
    _ZH_NEGATION + r"(?:該|其|核准的|任何)?" + _ZH_REVIEWER + r"(?:本人|自己)?" + _ZH_EXECUTOR_VERB,
    _ZH_EXECUTOR_VERB + r"[^，。；,.;|]{0,4}" + _ZH_NEGATION + r"(?:該|其|核准的|任何)?" + _ZH_REVIEWER,
    _ZH_REVIEWER + r"(?:本人|自己)?" + _ZH_NEGATION_AFTER + _ZH_EXECUTOR_VERB,
)
FIXED_INTEGRATOR_NEGATED: tuple[str, ...] = (
    r"must not be assumed", r"no fixed integrator", r"not required", r"不指定固定整合者", r"不指定固定的個人整合者",
    r"not a fixed integrator", r"is not an integrator",
)
QUEUE_DISPATCH_NEGATED: tuple[str, ...] = (
    r"只承載整合候選", r"integration candidates only", r"only integration candidates?", r"not (a |an )?(merge[- ])?queue (row|entry)",
    r"never (a |an )?(merge[- ])?queue (row|entry)", r"\bis not (a |an )?(merge[- ])?queue (row|entry)",
    r"不是[^。；|]{0,20}佇列", r"而非[^。；|]{0,20}佇列", r"不以[^。；|]{0,20}佇列",
)
QUEUE_HOLDS_ONLY_CANDIDATES: tuple[str, ...] = (
    r"integration candidates? only\b", r"\bonly (the )?integration candidates?\b",
    r"只(承載|存放|保存|包含|含有|放)整合候選", r"整合候選(而已|為限)",
)

_REVIEWER_EN = r"reviewers?\b"
_REVIEWER_ZH = r"(審閱者|審查者|reviewer)"


@dataclass(frozen=True)
class Pattern:
    """One retired-rule phrasing: where it comes from, what finds it, which sentences state the rule instead."""

    name: str
    source: str
    regex: re.Pattern[str]
    exempt: tuple[str, ...]
    bridge_note_exempts: bool = False


PATTERNS: tuple[Pattern, ...] = (
    # ticket 47 D7 a1, with the N9-06 correction: no "integration script" / R4-4 exemption.
    Pattern(
        "a1 reviewer integrates", "ticket 47 D7 a1; N9-06; R3-07; F-07",
        re.compile(_REVIEWER_EN + r"[^.;|]{0,240}\bintegrat\w*|\bintegrat\w*[^.;|]{0,160}" + _REVIEWER_EN, re.I),
        REVIEWER_NEGATED,
    ),
    # ticket 47 D7 a2 (unchanged).
    Pattern(
        "a2 reviewer submits", "ticket 47 D7 a2",
        re.compile(_REVIEWER_EN + r"[^.;|]{0,240}\bsubmi(t|ts|ssion)\b", re.I),
        (r"never submits", r"who is not (that candidate|its reviewer)", r"is not its reviewer", r"differs from",
         r"not the reviewer", r"superseded"),
    ),
    # ticket 47 D7 a3 with N9-06: no "integration script" exemption.
    Pattern(
        "a3 fixed integrator role", "ticket 47 D7 a3; R3-07; N9-06",
        re.compile(r"\b(owns?|owner of|responsible for)\b[^.;|]{0,120}\bguarded integration\b|整合負責人|固定整合者|\bfixed integrator\b|\bdesignated integrator\b", re.I),
        FIXED_INTEGRATOR_NEGATED,
    ),
    Pattern(
        "b1 bridge required or default", "ticket 47 D7 b1; R4-1",
        re.compile(NOUN + r"[^.;|]{0,160}" + VERB + "|" + VERB + r"[^.;|]{0,160}" + NOUN, re.I),
        BRIDGE_EXEMPT, True,
    ),
    Pattern(
        "b2 cross-lifetime requires controls", "ticket 47 D7 b2; R4-1",
        re.compile(r"cross-lifetime[^.;|]{0,160}" + VERB + "|" + VERB + r"[^.;|]{0,160}cross-lifetime", re.I),
        BRIDGE_EXEMPT, True,
    ),
    # D7 c with N9-06: merge, push, land and the 代為 commit form join the Chinese verbs; no 整合腳本 / R4-4 exemption.
    Pattern(
        "c 審閱者整合 (zh)", "ticket 47 D7 c; N9-06 (代為 commit); R3-07",
        re.compile(
            _REVIEWER_ZH + r"[^。；|]{0,80}(整合|合併|推送|代為|落地)|(整合|合併|推送|落地)[^。；|]{0,60}(審閱者|審查者)"
        ),
        REVIEWER_NEGATED_ZH,
    ),
    Pattern(
        "d 過渡路徑為預設 (zh)", "ticket 47 D7 d; R4-1",
        re.compile(
            r"(descriptor|bridge|受據綁定|receipt-bound)[^。；|]{0,80}(必須|預設|唯一|保留|僅)"
            r"|(必須|預設|唯一)[^。；|]{0,80}(descriptor|bridge|受據綁定|receipt-bound)"
        ),
        (r"不是預設", r"不再是預設", r"過渡", r"\bR4-1\b", r"退場", r"僅限過渡"), True,
    ),
    Pattern(
        "e dispatch carries a descriptor", "ticket 47 D7 e; R4-1",
        re.compile(r"dispatch[^.;。；]{0,100}\bdescriptor\b|\bdescriptor\b[^.;。；]{0,100}dispatch", re.I),
        BRIDGE_EXEMPT + (r"live descriptor 是", r"僅限"), True,
    ),
    # N9-06: a reviewer who merges, pushes or lands (verbs the D7 a1 pattern never had).
    Pattern(
        "g1 reviewer merges, pushes or lands", "N9-06; R3-07",
        re.compile(
            _REVIEWER_EN + r"[^.;|]{0,160}\b(merg(e|es|ed|ing)|push(es|ed|ing)?|land(s|ed|ing)?"
            r"|commits? (the|it|them|a|on behalf)|commit(s|ted) (on behalf|to the candidate))\b"
            r"|\b(merg(e|es|ed|ing)|push(es|ed|ing)?|land(s|ed|ing)?)\b[^.;|]{0,120}\bby (the )?reviewers?\b",
            re.I,
        ),
        REVIEWER_NEGATED,
    ),
    # Row 13 / N8-04, first half of R4-1: a pending dispatch is a queue row (English and Chinese forms).
    Pattern(
        "h1 dispatch is a queue row", "row 13; N8-04 (R4-1 half one); N9-06 (派工以整合佇列列表示)",
        re.compile(
            r"\bdispatch(es)?\b[^.;|]{0,80}\b(merge[- ])?queue (row|entry)\b"
            r"|\b(merge[- ])?queue (row|entry)\b[^.;|]{0,60}\b(is|are|as|carries|represents?)\b[^.;|]{0,30}\bdispatch"
            r"|派工[^。；|]{0,30}(整合)?佇列(列|項|條目)|(整合)?佇列(列|項|條目)[^。；|]{0,30}(表示|代表)[^。；|]{0,10}派工",
            re.I,
        ),
        QUEUE_DISPATCH_NEGATED,
    ),
    # Row 13 / N8-04, second half of R4-1: the queue holds something other than integration candidates.
    Pattern(
        "h2 queue holds more than candidates", "row 13; N8-04 (R4-1 half two)",
        re.compile(
            r"\b(merge[- ])?queue( file)?\s+(holds?|carr(y|ies)|contains?|stores?|keeps?)\b[^.;|]{0,100}"
            r"|(整合)?佇列(列)?\s*(承載|存放|保存|包含|含有)[^。；|]{0,40}",
            re.I,
        ),
        QUEUE_HOLDS_ONLY_CANDIDATES,
    ),
)

# R3-07: a sentence that names who executes integration. It must name the integration script.
EXECUTION_SENTENCE = re.compile(
    r"\bintegration\b[^.;|]{0,60}\b(is|are|was|be)\b[^.;|]{0,20}\b(executed|run|performed|carried out)\b"
    r"|\b(executes?|runs?|performs?)\s+(the\s+)?integration\b(?!\s+(clone|gate|receipt|branch|queue|script))"
    r"|\bintegration\b[^.;|]{0,40}\bexecuted by\b"
    r"|整合[^。；|]{0,20}由[^。；|]{0,30}(執行|進行)"
    r"|由[^。；|]{0,30}(執行|進行)[^。；|]{0,10}整合"
    r"|整合[^。；|]{0,30}執行",
    re.I,
)
INTEGRATION_SCRIPT = re.compile(r"integration script|整合腳本", re.I)

DATED_ROW = re.compile(r"^\|\s*20\d\d-\d\d-\d\d\s*\|")
SCOPE_NOTE = re.compile(r"^>\s*Scope note.*(not the default[^\n]{0,160}R4-1|R4-1[^\n]{0,160}not the default)", re.I)
RECORD_SECTIONS = ("amendments", "revision signatures", "approval record", "revision record")
LIST_ITEM = re.compile(r"^\s*([-*]|\d+\.)\s|^\s*\|")
SENTENCE_SEPARATORS = ".;|。；"
# D8: the precedence note, a blockquote line naming the change, R4-1 and R4-4.
PRECEDENCE_NOTE = re.compile(r"^>\s*Precedence note.*CHG-20261103-043.*R4-1.*R4-4", re.I)
# D9 / N9-05: the precedence sentence of Workflow.md section 0.
PRECEDENCE_PHRASE = "以其檔頭的優先序註記讀取"


# ------------------------------------------------------------------------ engine


@dataclass(frozen=True)
class Hit:
    path: str
    line: int
    pattern: str
    sentence: str
    verdict: str  # LIVE, or the reason the hit is tolerated


@dataclass
class Sweep:
    hits: list[Hit]
    defects: list[str]

    def live(self) -> list[Hit]:
        return [hit for hit in self.hits if hit.verdict == LIVE]

    def tolerated_under_note(self) -> list[Hit]:
        return [hit for hit in self.hits if hit.verdict == TOLERATED_NOTE]


LIVE = "LIVE RETIRED RULE"
TOLERATED_NOTE = "tolerated: the file carries the precedence note"


def normalise(text: str) -> str:
    return text.replace("\r\n", "\n")


def read_strict(base: Path, relative: str, defects: list[str]) -> str | None:
    """The text of `relative`, or None with a defect: a missing or undecodable file is red, never skipped."""
    path = base / relative
    try:
        data = path.read_bytes()
    except OSError as error:
        defects.append(f"MISSING_OR_UNREADABLE {relative}: {type(error).__name__}")
        return None
    try:
        return normalise(data.decode("utf-8"))
    except UnicodeDecodeError as error:
        defects.append(f"UNDECODABLE {relative}: {error.reason}")
        return None


def markdown_under(base: Path, root: str, defects: list[str]) -> list[str]:
    """Repository-relative `.md` paths under `root` (a file or a directory); a root that is absent or empty is a defect."""
    target = base / root
    if target.is_file():
        return [root]
    if not target.is_dir():
        defects.append(f"MISSING_ROOT {root}")
        return []
    found = sorted(
        path.relative_to(base).as_posix() for path in target.rglob("*.md") if path.is_file()
    )
    if not found:
        defects.append(f"EMPTY_ROOT {root}")
    return found


def under(path: str, directory: str) -> bool:
    """Whether `path` is inside `directory`: the directory name is matched whole, never as a string prefix."""
    return path.startswith(directory.rstrip("/") + "/")


def is_record(path: str) -> bool:
    """A ticket or a review record of this line (ticket 47 D7 class 3)."""
    return under(path, "modules/tickets") or under(path, "doc/reviews")


def units(text: str) -> Iterator[tuple[int, str, str]]:
    """Paragraph-joined units (ticket 47 D7): table row, list item with its continuation lines, heading,
    each line of a fenced block (fences are scanned, not skipped), or a wrapped paragraph.
    Yields (first line, unit text, current section heading)."""
    out: list[tuple[int, str, str]] = []
    buffer: list[str] = []
    start = 0
    kind = ""
    in_fence = False
    section = ""

    def flush() -> None:
        nonlocal buffer, kind
        if buffer:
            out.append((start, " ".join(line.strip() for line in buffer), section))
        buffer, kind = [], ""

    for number, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            flush()
            out.append((number, line.strip(), section))
            continue
        if line.startswith("#"):
            flush()
            section = line.strip("# ").strip()
            out.append((number, line.strip(), section))
            continue
        if not line.strip():
            flush()
            continue
        if LIST_ITEM.match(line):
            flush()
            buffer, start, kind = [line], number, "item"
            continue
        if kind == "item" and line[:1].isspace():
            buffer.append(line)
            continue
        if kind == "item":
            flush()
        if not buffer:
            start, kind = number, "para"
        buffer.append(line)
    flush()
    return iter(out)


def sentence_of(unit: str, match: re.Match[str]) -> str:
    low = max([unit.rfind(char, 0, match.start()) for char in SENTENCE_SEPARATORS] + [-1]) + 1
    high = min([i for i in (unit.find(char, match.end()) for char in SENTENCE_SEPARATORS) if i != -1] + [len(unit)])
    return unit[low:high]


def head_lines(text: str, count: int = 5) -> list[str]:
    return [line for line in text.split("\n") if line.strip()][:count]


def carries_note(text: str) -> bool:
    """D8 presence: the precedence note is a blockquote within the first five non-empty lines."""
    return any(PRECEDENCE_NOTE.match(line) for line in head_lines(text))


def note_anywhere(text: str) -> bool:
    """N9-04 absence: the same expression as the presence check, on every line of the file."""
    return any(PRECEDENCE_NOTE.match(line) for line in text.split("\n")) or "Precedence note (`CHG-20261103-043`)" in text


def bridge_scoped(text: str) -> bool:
    return any(SCOPE_NOTE.match(line) for line in head_lines(text))


# S58-02 and S58-11 (revision02): a backticked `reviewer` or `submitter` is a field name, not a person, only in
# the field-list form R4-7 uses ("... reads `review_candidate` and `reviewer` from the review record"; the
# Entry and block lists end at a closing bracket or a full stop): a run of two or more backticked names joined
# by list separators, followed by `from`, a closing bracket or a full stop. A single backticked name, or a list
# followed by any other word ("`reviewer` and `submitter` must merge", "... are the ones who merge"), is a person.
_FIELD_TOKEN = r"`[A-Za-z_][A-Za-z_0-9]*`"
_FIELD_SEPARATOR = r"\s*(?:,|，|、|\band\b|\bor\b|及|與|和)\s*"
FIELD_LIST = re.compile(
    r"(?P<run>" + _FIELD_TOKEN + r"(?:" + _FIELD_SEPARATOR + _FIELD_TOKEN + r")+)"
    r"(?=\s*(?:[)）.。]|$)|\s+from\b)",
    re.I,
)
FIELD_NAME = re.compile(r"`(reviewer|submitter)`")


def mask_field_lists(unit: str) -> str:
    """`unit` with `reviewer` and `submitter` replaced by FIELD inside field lists, and nowhere else."""
    return FIELD_LIST.sub(lambda match: FIELD_NAME.sub("FIELD", match.group("run")), unit)


def classify(path: str, text: str, historical: bool) -> list[Hit]:
    """Every pattern match of one document, each with its verdict."""
    record = is_record(path)
    scoped = bridge_scoped(text)
    noted = carries_note(text)
    hits: list[Hit] = []
    for start, raw_unit, section in units(text):
        unit = mask_field_lists(raw_unit)
        for pattern in PATTERNS:
            seen: set[str] = set()
            for match in pattern.regex.finditer(unit):
                sentence = sentence_of(unit, match)
                if sentence in seen:
                    continue
                seen.add(sentence)
                if record:
                    continue
                if DATED_ROW.match(unit) or section.lower().startswith(RECORD_SECTIONS):
                    continue
                if any(re.search(marker, sentence, re.I) for marker in pattern.exempt):
                    continue
                if pattern.bridge_note_exempts and scoped:
                    continue
                verdict = TOLERATED_NOTE if (historical and noted) else LIVE
                hits.append(Hit(path, start, pattern.name, sentence.strip()[:220], verdict))
    return hits


def execution_defects(path: str, text: str) -> list[Hit]:
    """R3-07: a sentence that names who executes integration must name the integration script."""
    hits: list[Hit] = []
    if is_record(path):
        return hits
    for start, unit, section in units(text):
        if DATED_ROW.match(unit) or section.lower().startswith(RECORD_SECTIONS):
            continue
        seen: set[str] = set()
        for match in EXECUTION_SENTENCE.finditer(unit):
            sentence = sentence_of(unit, match)
            if sentence in seen:
                continue
            seen.add(sentence)
            if not INTEGRATION_SCRIPT.search(sentence):
                hits.append(Hit(path, start, "x integration executor without the script", sentence.strip()[:220], LIVE))
    return hits


def routed_files(base: Path, defects: list[str]) -> list[str]:
    files: list[str] = []
    for root in ROUTED_ROOTS:
        files.extend(markdown_under(base, root, defects))
    # The template and the index of modules/spec/ are not historical SPECs and carry no note:
    # they are swept as routed documents.
    for relative in NOTE_FORBIDDEN:
        if relative not in files:
            files.append(relative)
    return sorted(set(files))


def historical_files(base: Path, defects: list[str]) -> list[str]:
    """Every SPEC under modules/spec/ and every runbook under doc/runbooks/ that the routed set does not cover."""
    specs = [p for p in markdown_under(base, SPEC_DIRECTORY, defects) if p not in SPEC_NOT_HISTORICAL]
    runbooks = [p for p in markdown_under(base, RUNBOOK_DIRECTORY, defects) if p != ROUTED_RUNBOOK]
    return sorted(set(specs + runbooks))


def sweep(base: Path) -> Sweep:
    result = Sweep([], [])
    for path in routed_files(base, result.defects):
        text = read_strict(base, path, result.defects)
        if text is None:
            continue
        result.hits.extend(classify(path, text, historical=False))
        result.hits.extend(execution_defects(path, text))
    for path in historical_files(base, result.defects):
        text = read_strict(base, path, result.defects)
        if text is None:
            continue
        result.hits.extend(classify(path, text, historical=True))
    return result


def tolerated_report(result: Sweep) -> list[str]:
    counts: dict[str, int] = {}
    for hit in result.tolerated_under_note():
        counts[hit.path] = counts.get(hit.path, 0) + 1
    return [f"tolerated under the precedence note: {path}: {count} hit(s)" for path, count in sorted(counts.items())]


# --------------------------------------------------- D8: the note on every covered file


def note_defects(base: Path) -> list[str]:
    """Every historical SPEC and every dated handover runbook opens with the note; the template and the index carry none."""
    defects: list[str] = []
    covered = [p for p in markdown_under(base, SPEC_DIRECTORY, defects) if p not in SPEC_NOT_HISTORICAL]
    covered += [p for p in markdown_under(base, RUNBOOK_DIRECTORY, defects) if Path(p).name.startswith("handover-")]
    for path in covered:
        text = read_strict(base, path, defects)
        if text is not None and not carries_note(text):
            defects.append(f"NOTE_MISSING {path}")
    for path in NOTE_FORBIDDEN:
        text = read_strict(base, path, defects)
        if text is not None and note_anywhere(text):
            defects.append(f"NOTE_PRESENT_BUT_EXCLUDED {path}")
    return defects


# ----------------------------------------------------- both halves of R4-1, positively


def section_of(text: str, heading: re.Pattern[str], stop: re.Pattern[str]) -> str | None:
    lines = text.split("\n")
    begin = next((i for i, line in enumerate(lines) if heading.match(line)), None)
    if begin is None:
        return None
    end = next((i for i in range(begin + 1, len(lines)) if stop.match(lines[i])), len(lines))
    return "\n".join(lines[begin:end])


WORKFLOW_SECTION_ZERO = re.compile(r"^## 0\.")
ANY_H2 = re.compile(r"^## ")
SPEC_R41 = re.compile(r"^### R4-1\b")
ANY_H3_OR_H2 = re.compile(r"^#{2,3} ")

DISPATCH_HALF = re.compile(
    r"(?=.*(dispatch|派工))(?=.*(ticket'?s? state row|票面狀態列))(?=.*digest)", re.I | re.S
)
QUEUE_HALF = re.compile(
    r"(整合佇列|merge queue|queue)[^.;。；|]{0,60}"
    r"(只承載整合候選|holds integration candidates only|integration candidates only|only integration candidates)",
    re.I,
)


def states_both_halves(scope: str) -> list[str]:
    missing: list[str] = []
    flat = [unit for _, unit, _ in units(scope)]
    if not any(DISPATCH_HALF.search(sentence_of(unit, m)) for unit in flat for m in re.finditer(r"dispatch|派工", unit, re.I)):
        missing.append("a pending dispatch is the ticket state row plus the dispatch-file digest")
    if not any(QUEUE_HALF.search(unit) for unit in flat):
        missing.append("the queue holds integration candidates only")
    return missing


def r41_defects(base: Path) -> list[str]:
    defects: list[str] = []
    scopes = (
        (AGENTS, None, None),
        (WORKFLOW, WORKFLOW_SECTION_ZERO, ANY_H2),
        (GOVERNANCE_SPEC, SPEC_R41, ANY_H3_OR_H2),
    )
    for path, heading, stop in scopes:
        text = read_strict(base, path, defects)
        if text is None:
            continue
        scope = text
        if heading is not None and stop is not None:
            found = section_of(text, heading, stop)
            if found is None:
                defects.append(f"R41_SECTION_MISSING {path}")
                continue
            scope = found
        for half in states_both_halves(scope):
            defects.append(f"R41_HALF_MISSING {path}: {half}")
    return defects


# ----------------------------------------------- R3-07: the integration script, positively


R44_SCRIPT_BY_BUDGET = re.compile(r"integration is executed by the versioned integration script[^.]{0,60}by whoever holds budget", re.I)
R44_NO_FIXED = re.compile(r"single fixed integrator is not required and must not be assumed", re.I)


def r307_defects(base: Path) -> list[str]:
    defects: list[str] = []
    spec = read_strict(base, GOVERNANCE_SPEC, defects)
    if spec is not None:
        section = section_of(spec, re.compile(r"^### R4-4\b"), ANY_H3_OR_H2)
        if section is None:
            defects.append(f"R44_SECTION_MISSING {GOVERNANCE_SPEC}")
        else:
            flat = " ".join(section.split())
            if not R44_SCRIPT_BY_BUDGET.search(flat):
                defects.append("R44_SCRIPT_BY_BUDGET_MISSING: integration is executed by the versioned integration script by whoever holds budget")
            if not R44_NO_FIXED.search(flat):
                defects.append("R44_NO_FIXED_INTEGRATOR_MISSING: a single fixed integrator is not required and must not be assumed")
    review = read_strict(base, CODE_REVIEW, defects)
    if review is not None and not R44_SCRIPT_BY_BUDGET.search(" ".join(review.split())):
        defects.append(f"R44_SCRIPT_BY_BUDGET_MISSING {CODE_REVIEW}")
    return defects


# --------------------------------------------- N9-05: the precedence sentence, by rule and place


# S58-03 (revision02): the rule is pinned exactly, with nothing (no 不, no 以外) between its parts.
PRECEDENCE_REVERSED_OK = re.compile(r"與 R4-1、R4-4 衝突處以本修訂為準")
PRECEDENCE_NOT_COMPETING = re.compile(r"不構成互相競爭的 reference")
PRECEDENCE_NO_INVALID = re.compile(r"不觸發 `?ROUTE_REFERENCE_INVALID`?")
PRECEDENCE_SPEC_SCOPE = re.compile(r"早於 Revision 04 的專案 SPEC")
PRECEDENCE_RUNBOOK_SCOPE = re.compile(r"runbooks 目錄[^；。]{0,40}(交接|handover)[^；。]{0,10}runbook")
PRECEDENCE_RUNBOOK_NOTE = re.compile(r"同一優先序註記|同一(份)?註記")


def precedence_defects(base: Path) -> list[str]:
    defects: list[str] = []
    text = read_strict(base, WORKFLOW, defects)
    if text is None:
        return defects
    occurrences = text.count(PRECEDENCE_PHRASE)
    if occurrences != 1:
        defects.append(f"PRECEDENCE_SENTENCE_COUNT {occurrences} (one expected)")
        return defects
    scope = section_of(text, WORKFLOW_SECTION_ZERO, ANY_H2)
    if scope is None:
        defects.append("PRECEDENCE_SECTION_ZERO_MISSING")
        return defects
    if PRECEDENCE_PHRASE not in scope:
        defects.append("PRECEDENCE_SENTENCE_OUTSIDE_SECTION_ZERO")
        return defects
    bullet = next((unit for _, unit, _ in units(scope) if PRECEDENCE_PHRASE in unit), "")
    checks = (
        (PRECEDENCE_REVERSED_OK, "Revision 04 (R4-1, R4-4) prevails over the noted documents"),
        (PRECEDENCE_NOT_COMPETING, "reading them through the note is not a competing reference"),
        (PRECEDENCE_NO_INVALID, "reading them raises no ROUTE_REFERENCE_INVALID"),
        (PRECEDENCE_SPEC_SCOPE, "it covers the SPECs that predate Revision 04"),
        (PRECEDENCE_RUNBOOK_SCOPE, "it covers the dated handover runbooks under doc/runbooks/"),
        (PRECEDENCE_RUNBOOK_NOTE, "it covers only runbooks that carry the same precedence note"),
    )
    for expression, meaning in checks:
        if not expression.search(bullet):
            defects.append(f"PRECEDENCE_RULE_MISSING: {meaning}")
    return defects


def handover_citation_defects(base: Path) -> list[str]:
    """Part B: every dated handover runbook cites the Workflow.md section 0 sentence instead of granting itself the waiver."""
    defects: list[str] = []
    for path in markdown_under(base, RUNBOOK_DIRECTORY, defects):
        if not Path(path).name.startswith("handover-"):
            continue
        text = read_strict(base, path, defects)
        if text is None:
            continue
        note = next((line for line in head_lines(text) if PRECEDENCE_NOTE.match(line)), None)
        if note is None:
            continue  # NOTE_MISSING is reported by note_defects
        if not re.search(r"Workflow\.md[^.]{0,20}section 0", note, re.I):
            defects.append(f"HANDOVER_NOTE_DOES_NOT_CITE_WORKFLOW_SECTION_0 {path}")
    return defects


# --------------------------------------------------------------- the temporary copy


def copy_documents(destination: Path) -> None:
    """The routed and historical documents (Markdown only) of this checkout, in the same layout."""
    wanted = list(ROUTED_ROOTS) + [SPEC_DIRECTORY, RUNBOOK_DIRECTORY]
    for root in wanted:
        source = REPO / root
        if source.is_file():
            (destination / root).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination / root)
        else:
            for path in source.rglob("*.md"):
                target = destination / path.relative_to(REPO)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)


class TemporaryDocuments(unittest.TestCase):
    """Each test gets its own copy of the documents; the copy is built once per class and cloned."""

    template: tempfile.TemporaryDirectory[str]
    template_path: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.template = tempfile.TemporaryDirectory(prefix="govcons-template-")
        cls.template_path = Path(cls.template.name)
        copy_documents(cls.template_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.template.cleanup()

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory(prefix="govcons-")
        self.addCleanup(holder.cleanup)
        self.base = Path(holder.name) / "repo"
        shutil.copytree(self.template_path, self.base)

    def edit(self, relative: str, change: Callable[[str], str]) -> None:
        path = self.base / relative
        path.write_text(change(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")

    def append(self, relative: str, sentence: str) -> None:
        self.edit(relative, lambda text: text.rstrip("\n") + "\n\n" + sentence + "\n")

    def live_names(self) -> list[str]:
        return sorted({hit.pattern for hit in sweep(self.base).live()})


# ================================================================ the real tree

# S58-05: the tolerated hits of the real tree, by file and count. A change here is a decision: read the new
# sentences, then update this list in the same commit.
EXPECTED_TOLERATED: list[str] = [
    "tolerated under the precedence note: doc/runbooks/handover-2026-08-22-plugin-distribution.md: 3 hit(s)",
    "tolerated under the precedence note: modules/spec/adaptive-project-orchestration.md: 1 hit(s)",
    "tolerated under the precedence note: modules/spec/claude-code-plugin-distribution.md: 1 hit(s)",
    "tolerated under the precedence note: modules/spec/executor-routing.md: 2 hit(s)",
    "tolerated under the precedence note: modules/spec/project-authority-integration.md: 1 hit(s)",
]


class RealTreeTests(unittest.TestCase):
    """The checkout as it stands: every rule green, every tolerated hit reported."""

    result: Sweep

    @classmethod
    def setUpClass(cls) -> None:
        cls.result = sweep(REPO)

    def test_no_file_of_the_sweep_is_missing_or_undecodable(self) -> None:
        self.assertEqual(self.result.defects, [])

    def test_no_retired_rule_is_live_in_the_routed_set_or_in_a_spec_or_runbook_without_the_note(self) -> None:
        live = self.result.live()
        self.assertEqual([], [f"{h.path}:{h.line} ({h.pattern}) {h.sentence}" for h in live])

    def test_every_tolerated_hit_is_reported_by_file_and_count(self) -> None:
        report = tolerated_report(self.result)
        for line in report:
            print(line, file=sys.stderr)
        # S58-05: the report is part of the result, so a new or a vanished tolerated file is red.
        self.assertEqual(report, EXPECTED_TOLERATED)
        tolerated = self.result.tolerated_under_note()
        self.assertEqual(len(report), len({hit.path for hit in tolerated}))
        counted = 0
        for line in report:
            found = re.search(r": (\d+) hit\(s\)$", line)
            self.assertIsNotNone(found, line)
            counted += int(found.group(1)) if found else 0
        self.assertEqual(counted, len(tolerated))
        # The routed set carries no tolerated hit: only historical files can sit under a note.
        routed = set(routed_files(REPO, []))
        self.assertEqual([h.path for h in tolerated if h.path in routed], [])

    def test_the_handover_runbook_hit_is_tolerated_only_by_its_note(self) -> None:
        handover = "doc/runbooks/handover-2026-08-22-plugin-distribution.md"
        tolerated = [h for h in self.result.tolerated_under_note() if h.path == handover]
        self.assertTrue(any("代為" in h.sentence for h in tolerated), [h.sentence for h in tolerated])

    def test_every_historical_spec_and_dated_runbook_carries_the_note_and_the_template_and_index_carry_none(self) -> None:
        self.assertEqual(note_defects(REPO), [])

    def test_agents_workflow_section_zero_and_the_spec_state_both_halves_of_r4_1(self) -> None:
        self.assertEqual(r41_defects(REPO), [])

    def test_the_integration_script_run_by_whoever_holds_budget_is_stated_in_the_spec_and_in_code_review(self) -> None:
        self.assertEqual(r307_defects(REPO), [])

    def test_the_precedence_sentence_is_pinned_by_rule_and_place(self) -> None:
        self.assertEqual(precedence_defects(REPO), [])

    def test_every_dated_handover_runbook_cites_the_workflow_sentence(self) -> None:
        self.assertEqual(handover_citation_defects(REPO), [])


# ====================================================== injections: part A rules


class InjectionTests(TemporaryDocuments):
    """Each retired sentence restored in a temporary copy goes red; the unmodified copy is green."""

    def test_the_unmodified_copy_is_green(self) -> None:
        result = sweep(self.base)
        self.assertEqual(result.defects, [])
        self.assertEqual(result.live(), [])

    # ---- the eight injections of the ticket 47 review (N9-06 lists them as 8 injections, 2 caught by D7)
    INJECTIONS: tuple[tuple[str, str, str], ...] = (
        ("a1 reviewer integrates", "AGENTS.md", "The reviewer integrates the approved candidate by hand after the review."),
        ("a1 reviewer integrates", "Workflow.md", "Integration is executed by the versioned integration script from the merge queue by the reviewer who approved it."),
        ("g1 reviewer merges, pushes or lands", "CodeReview.md", "After approval the reviewer merges the candidate into the integration branch."),
        ("g1 reviewer merges, pushes or lands", "CodeReview.md", "After approval the reviewer pushes the candidate to the remote."),
        ("g1 reviewer merges, pushes or lands", "CodeReview.md", "The reviewer lands the candidate through the integration script."),
        ("c 審閱者整合 (zh)", "Workflow.md", "審閱者審完後代為 commit 到候選分支，再過閘門。"),
        ("h1 dispatch is a queue row", "AGENTS.md", "派工以整合佇列列表示。"),
        ("a3 fixed integrator role", "template/README.md", "A fixed integrator owns guarded integration for every ticket and runs the integration script."),
        # revision02: the reviewer's counter-mutations CM1 (S58-01) and CM2 (S58-02), both red now
        ("c 審閱者整合 (zh)", "Workflow.md", "審閱者核准後代為 commit 到候選分支，不得略過閘門。"),
        ("g1 reviewer merges, pushes or lands", "CodeReview.md", "After approval the `reviewer` merges the candidate into main."),
        # correction 2: the reviewer's CM10 (S58-10), CM12 and CM13 (S58-11), red now
        ("c 審閱者整合 (zh)", "Workflow.md", "審閱者不得略過閘門，核准後代為 commit 到候選分支。"),
        ("g1 reviewer merges, pushes or lands", "CodeReview.md", "After approval `reviewer` and `submitter` must merge the candidate into main."),
        ("g1 reviewer merges, pushes or lands", "CodeReview.md", "After approval `reviewer`, `submitter` are the ones who merge the candidate into main."),
    )

    def test_the_f07_injection_the_executor_of_r4_4_reworded_to_the_reviewer_who_approved_it_goes_red(self) -> None:
        """The F-07 door: "by whoever holds budget" becomes "by the reviewer who approved it" inside R4-4 itself."""
        self.edit(GOVERNANCE_SPEC, lambda text: self.removed(text, "by whoever holds budget", "by the reviewer who approved it"))
        self.assertIn("a1 reviewer integrates", {hit.pattern for hit in sweep(self.base).live() if hit.path == GOVERNANCE_SPEC})
        self.assertTrue(any("R44_SCRIPT_BY_BUDGET_MISSING" in defect for defect in r307_defects(self.base)))

    def test_each_ticket_47_injection_and_the_f07_one_goes_red_with_its_pattern(self) -> None:
        for expected, relative, sentence in self.INJECTIONS:
            with self.subTest(expected=expected, file=relative, sentence=sentence):
                self.setUp()
                self.append(relative, sentence)
                self.assertIn(expected, self.live_names())

    def test_the_injections_also_hit_the_files_they_were_added_to(self) -> None:
        for expected, relative, sentence in self.INJECTIONS:
            with self.subTest(expected=expected, file=relative):
                self.setUp()
                self.append(relative, sentence)
                paths = {hit.path for hit in sweep(self.base).live() if hit.pattern == expected}
                self.assertIn(relative, paths)

    def test_the_words_integration_script_do_not_mask_a_reviewer_named_as_executor(self) -> None:
        for sentence in (
            "The reviewer who approved it runs the integration script.",
            "The integration script is run by the reviewer.",
            "審閱者執行整合腳本並整合候選。",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("Workflow.md", sentence)
                self.assertTrue(self.live_names(), sentence)

    def test_negations_of_the_executor_stay_green(self) -> None:
        for sentence in (
            "Integration is executed by the versioned integration script, not by the reviewer.",
            "The reviewer never merges, pushes or lands a candidate.",
            "整合不由審閱者執行，由整合腳本執行。",
            "審閱者不得代為 commit 或整合候選。",
            "審閱者本人不得整合候選，由整合腳本執行。",
            "整合者並非審閱者，由持有預算者執行整合腳本。",
            "整合不由審閱者本人執行，由整合腳本執行。",
            "The integration script reads `review_candidate` and `reviewer` from the review record, not from the queue row.",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("Workflow.md", sentence)
                self.assertEqual(self.live_names(), [], sentence)

    def test_a_negation_of_an_unrelated_clause_or_a_backticked_person_exempts_nothing(self) -> None:
        """S58-01 and S58-02: the exemptions are tied to the executor and to the field-list form."""
        for sentence in (
            "審閱者核准後代為 commit 到候選分支，不得略過閘門。",
            "審閱者核准後整合候選，並非可選步驟。",
            "審閱者不得略過閘門，核准後代為 commit 到候選分支。",
            "審閱者並非可略過的環節，核准後整合候選。",
            "核准後整合候選到候選分支，不是審閱者可略過的環節。",
            "不得略過閘門，審閱者核准後代為 commit 到候選分支。",
            "After approval `reviewer` and `submitter` must merge the candidate into main.",
            "After approval `reviewer`, `submitter` are the ones who merge the candidate into main.",
            "After approval the `reviewer` merges the candidate into main.",
            "After approval the `reviewer` and `submitter` merge the candidate into main.",
            "The `reviewer` integrates the approved candidate by hand.",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("Workflow.md", sentence)
                self.assertTrue(self.live_names(), sentence)

    def test_the_field_list_form_masks_the_names_and_nothing_else(self) -> None:
        self.assertEqual(
            mask_field_lists("reads `review_candidate` and `reviewer` from the review record"),
            "reads `review_candidate` and FIELD from the review record",
        )
        self.assertEqual(mask_field_lists("Entry (`ticket`, `reviewer`, `submitter`) must differ"), "Entry (`ticket`, FIELD, FIELD) must differ")
        self.assertEqual(mask_field_lists("the `reviewer` merges it"), "the `reviewer` merges it")
        self.assertEqual(mask_field_lists("the `reviewer` and `submitter` merge it"), "the `reviewer` and `submitter` merge it")
        for tail in ("must merge it", "are the ones who merge it", "is the one who merges it", "of the record merge it", ", merge it"):
            self.assertEqual(mask_field_lists("the `reviewer` and `submitter` " + tail), "the `reviewer` and `submitter` " + tail, tail)

    # ---- the remaining D7 patterns
    D7_INJECTIONS: tuple[tuple[str, str, str], ...] = (
        ("a2 reviewer submits", "AGENTS.md", "The reviewer submits the candidate to the queue after approval."),
        ("b1 bridge required or default", "Workflow.md", "The live descriptor is mandatory for every dispatch."),
        ("b2 cross-lifetime requires controls", "CodeReview.md", "A cross-lifetime handoff requires the bridge controls."),
        ("d 過渡路徑為預設 (zh)", "Workflow.md", "descriptor 預設為每次派工的路徑。"),
        ("e dispatch carries a descriptor", "AGENTS.md", "Each dispatch carries a descriptor that the host consumes."),
    )

    def test_each_remaining_d7_pattern_goes_red_on_its_injection(self) -> None:
        for expected, relative, sentence in self.D7_INJECTIONS:
            with self.subTest(expected=expected, sentence=sentence):
                self.setUp()
                self.append(relative, sentence)
                self.assertIn(expected, self.live_names())

    # ---- row 13 / N8-04: both halves of R4-1, as retired phrasings
    def test_a_sentence_that_makes_the_dispatch_a_queue_row_is_red_in_english_and_chinese(self) -> None:
        for sentence in (
            "A pending dispatch is a queue row in the merge queue.",
            "The dispatch is carried by a queue entry.",
            "派工以整合佇列列表示。",
            "整合佇列列代表派工。",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("Workflow.md", sentence)
                self.assertIn("h1 dispatch is a queue row", self.live_names())

    def test_a_sentence_that_makes_the_queue_hold_more_than_candidates_is_red_in_english_and_chinese(self) -> None:
        for sentence in (
            "The merge queue holds dispatch descriptors and integration candidates.",
            "The queue carries every pending dispatch.",
            "整合佇列承載派工與整合候選。",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("AGENTS.md", sentence)
                self.assertIn("h2 queue holds more than candidates", self.live_names())

    def test_the_positive_statements_of_both_halves_stay_green(self) -> None:
        for sentence in (
            "The merge queue holds integration candidates only.",
            "整合佇列列只承載整合候選。",
            "A dispatch is never a queue row.",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("Workflow.md", sentence)
                self.assertNotIn("h1 dispatch is a queue row", self.live_names())
                self.assertNotIn("h2 queue holds more than candidates", self.live_names())

    def test_each_routed_document_must_state_both_halves(self) -> None:
        halves = (
            ("a pending dispatch is the ticket state row", AGENTS, "dispatch 以票面狀態列（含派工檔 digest）表示"),
            ("the queue holds integration candidates only", AGENTS, "只承載整合候選"),
            ("a pending dispatch is the ticket state row", WORKFLOW, "以票面狀態列（含派工檔 digest）表示"),
            ("the queue holds integration candidates only", WORKFLOW, "只承載整合候選"),
            ("a pending dispatch is the ticket state row", GOVERNANCE_SPEC, "A pending dispatch is the ticket's state row plus the digest of its dispatch file"),
            ("the queue holds integration candidates only", GOVERNANCE_SPEC, "the merge queue holds integration candidates only"),
        )
        for half, relative, phrase in halves:
            with self.subTest(half=half, file=relative):
                self.setUp()
                self.edit(relative, self.remover(phrase))
                defects = r41_defects(self.base)
                self.assertTrue(any(relative in d and half in d for d in defects), defects)

    def test_the_halves_are_read_in_the_right_place_not_anywhere_in_the_file(self) -> None:
        """Workflow.md states them in section 0 only: the same sentence moved below section 0 does not count."""
        self.edit(WORKFLOW, lambda text: self.removed(text, "整合佇列列只承載整合候選（R4-7）"))
        self.append(WORKFLOW, "整合佇列列只承載整合候選。")
        defects = r41_defects(self.base)
        self.assertTrue(any(WORKFLOW in d and "queue holds integration candidates only" in d for d in defects), defects)

    @classmethod
    def remover(cls, phrase: str) -> Callable[[str], str]:
        return lambda text: cls.removed(text, phrase)

    @staticmethod
    def prefixer(line: str) -> Callable[[str], str]:
        return lambda text: line + "\n\n" + text

    @staticmethod
    def removed(text: str, phrase: str, replacement: str = "（已移除）") -> str:
        if phrase not in text:
            raise AssertionError(f"phrase not present: {phrase}")
        return text.replace(phrase, replacement, 1)

    # ---- R3-07
    def test_a_sentence_that_names_who_executes_integration_must_name_the_script(self) -> None:
        for sentence in (
            "Integration is executed by the maintainer on duty.",
            "整合由值班者執行。",
            "The release owner runs the integration by hand.",
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.append("Workflow.md", sentence)
                names = self.live_names()
                self.assertIn("x integration executor without the script", names)

    def test_a_sentence_that_names_the_script_as_executor_stays_green(self) -> None:
        self.append("Workflow.md", "Integration is executed by the versioned integration script by whoever holds budget.")
        self.assertEqual(self.live_names(), [])

    def test_the_spec_and_code_review_must_state_the_script_run_by_whoever_holds_budget(self) -> None:
        self.edit(GOVERNANCE_SPEC, lambda text: self.removed(text, "by whoever holds budget"))
        self.assertTrue(any("R44_SCRIPT_BY_BUDGET_MISSING" in d for d in r307_defects(self.base)))
        self.setUp()
        self.edit(GOVERNANCE_SPEC, lambda text: self.removed(text, "A single fixed integrator is not required and must not be assumed."))
        self.assertTrue(any("R44_NO_FIXED_INTEGRATOR_MISSING" in d for d in r307_defects(self.base)))
        self.setUp()
        self.edit(CODE_REVIEW, lambda text: re.sub(r"by\s+whoever\s+holds\s+budget", "by someone", text, count=1))
        self.assertTrue(any(CODE_REVIEW in d for d in r307_defects(self.base)))

    # ---- row 13: the widened sweep, tolerated hits, the note
    def test_a_retired_sentence_in_a_historical_spec_without_the_note_is_red(self) -> None:
        spec = "modules/spec/router-framework.md"
        self.edit(spec, lambda text: re.sub(r"^>\s*Precedence note[^\n]*\n", "", text, count=1, flags=re.M))
        self.append(spec, "The reviewer integrates the candidate by hand.")
        live = [h for h in sweep(self.base).live() if h.path == spec]
        self.assertTrue(live, "a hit without the note must be LIVE")
        self.assertIn(f"NOTE_MISSING {spec}", note_defects(self.base))

    def test_the_same_sentence_under_the_note_is_tolerated_and_reported_with_its_count(self) -> None:
        spec = "modules/spec/router-framework.md"
        self.append(spec, "The reviewer integrates the candidate by hand.")
        self.append(spec, "The reviewer merges the candidate by hand.")
        result = sweep(self.base)
        self.assertEqual([h for h in result.live() if h.path == spec], [])
        self.assertIn(f"tolerated under the precedence note: {spec}: 2 hit(s)", tolerated_report(result))

    def test_a_retired_sentence_in_a_dated_runbook_without_the_note_is_red(self) -> None:
        runbook = "doc/runbooks/handover-2026-08-22-plugin-distribution.md"
        self.edit(runbook, lambda text: re.sub(r"^>\s*Precedence note[^\n]*\n", "", text, count=1, flags=re.M))
        live = [h for h in sweep(self.base).live() if h.path == runbook]
        self.assertTrue(live)
        self.assertIn(f"NOTE_MISSING {runbook}", note_defects(self.base))

    def test_a_note_below_the_first_five_lines_does_not_count(self) -> None:
        spec = "modules/spec/review-assurance.md"

        def move_note(text: str) -> str:
            match = re.search(r"^>\s*Precedence note[^\n]*\n", text, flags=re.M)
            assert match is not None
            body = text.replace(match.group(0), "", 1)
            return "\n".join(["# t", "", "a", "", "b", "", "c", "", "d", "", "e", "", match.group(0).strip(), "", body])

        self.edit(spec, move_note)
        self.assertIn(f"NOTE_MISSING {spec}", note_defects(self.base))

    def test_an_undecodable_or_missing_or_empty_document_is_red_not_skipped(self) -> None:
        (self.base / "modules/spec/router-framework.md").write_bytes(b"\xff\xfe\x00bad")
        self.assertTrue(any(d.startswith("UNDECODABLE modules/spec/router-framework.md") for d in sweep(self.base).defects))
        self.setUp()
        (self.base / "AGENTS.md").unlink()
        self.assertTrue(any("AGENTS.md" in d for d in sweep(self.base).defects))
        self.setUp()
        shutil.rmtree(self.base / "template")
        self.assertIn("MISSING_ROOT template", sweep(self.base).defects)
        self.setUp()
        (self.base / "modules/spec/router-framework.md").write_bytes(b"")
        self.assertIn("NOTE_MISSING modules/spec/router-framework.md", note_defects(self.base))

    def test_a_missing_routed_directory_is_red_and_an_empty_one_too(self) -> None:
        for path in list((self.base / "doc/runbooks").glob("*.md")):
            path.unlink()
        defects = sweep(self.base).defects
        self.assertIn("EMPTY_ROOT doc/runbooks", defects)
        self.assertIn("MISSING_ROOT doc/runbooks/dispatch-model-profile.md", defects)

    def test_a_similarly_named_directory_is_not_a_sweep_root_and_not_a_record(self) -> None:
        self.assertFalse(under("modules/spec-old/x.md", SPEC_DIRECTORY))
        self.assertFalse(under("modules/specs/x.md", SPEC_DIRECTORY))
        self.assertTrue(under("modules/spec/x.md", SPEC_DIRECTORY))
        self.assertFalse(is_record("modules/tickets-old/a.md"))
        self.assertFalse(is_record("doc/reviews-old/a.md"))
        self.assertTrue(is_record("modules/tickets/a.md"))
        self.assertTrue(is_record("doc/reviews/workflow-governance/a.md"))
        # a retired sentence in a look-alike directory is not exempt as a record, and is not a SPEC either
        stray = self.base / "modules/spec-old"
        stray.mkdir()
        (stray / "x.md").write_text("The reviewer integrates the candidate.\n", encoding="utf-8")
        self.assertNotIn("modules/spec-old/x.md", {h.path for h in sweep(self.base).hits})
        self.assertEqual(len(classify("modules/tickets-old/a.md", "The reviewer integrates the candidate.\n", False)), 1)
        self.assertEqual(classify("modules/tickets/a.md", "The reviewer integrates the candidate.\n", False), [])

    def test_records_dated_rows_and_amendment_sections_are_exempt(self) -> None:
        text = "The reviewer integrates the candidate.\n"
        self.assertEqual(classify("modules/tickets/x.md", text, False), [])
        self.assertEqual(classify("doc/reviews/x.md", text, False), [])
        self.assertEqual(classify("a.md", "| 2026-11-03 | The reviewer integrates the candidate. |\n", False), [])
        self.assertEqual(classify("a.md", "## Amendments\n\nThe reviewer integrates the candidate.\n", False), [])
        self.assertEqual(len(classify("a.md", "## Rules\n\nThe reviewer integrates the candidate.\n", False)), 1)

    def test_a_bridge_scope_note_exempts_only_the_bridge_patterns(self) -> None:
        note = "> Scope note: the bridge route is not the default (R4-1).\n\n"
        self.assertEqual(classify("a.md", note + "The live descriptor is mandatory.\n", False), [])
        self.assertEqual(len(classify("a.md", note + "The reviewer integrates the candidate.\n", False)), 1)

    def test_fenced_lines_are_scanned_and_a_wrapped_paragraph_is_one_unit(self) -> None:
        self.assertEqual(len(classify("a.md", "```text\nThe reviewer integrates the candidate.\n```\n", False)), 1)
        self.assertEqual(len(classify("a.md", "The reviewer\nintegrates the candidate\nby hand.\n", False)), 1)

    # ---- N9-04: the template and the index carry no note, however it is worded
    def test_a_reworded_note_on_the_template_or_the_index_is_red(self) -> None:
        for relative in NOTE_FORBIDDEN:
            for wording in (
                "> Precedence note: CHG-20261103-043 gives R4-1 and R4-4 priority over every SPEC.",
                "> precedence NOTE (see CHG-20261103-043): R4-1 then R4-4 prevail.",
            ):
                with self.subTest(file=relative, wording=wording):
                    self.setUp()
                    self.edit(relative, self.prefixer(wording))
                    self.assertIn(f"NOTE_PRESENT_BUT_EXCLUDED {relative}", note_defects(self.base))

    def test_a_note_far_below_the_head_of_the_template_or_the_index_is_still_red(self) -> None:
        for relative in NOTE_FORBIDDEN:
            with self.subTest(file=relative):
                self.setUp()
                self.append(relative, "> Precedence note: CHG-20261103-043, R4-1 and R4-4 prevail.")
                self.assertIn(f"NOTE_PRESENT_BUT_EXCLUDED {relative}", note_defects(self.base))

    def test_the_old_exact_substring_is_still_caught(self) -> None:
        self.append(SPEC_TEMPLATE, "Precedence note (`CHG-20261103-043`) is quoted here.")
        self.assertIn(f"NOTE_PRESENT_BUT_EXCLUDED {SPEC_TEMPLATE}", note_defects(self.base))

    # ---- N9-05: the precedence sentence by rule and place
    def test_the_precedence_sentence_reversed_moved_or_narrowed_is_red(self) -> None:
        # S58-03: every case first asserts that the phrase it changes is present (`removed` raises when it is not),
        # so a case can never become a no-op; the two reviewer doors (CM3) are cases of their own.
        exact = "與 R4-1、R4-4 衝突處以本修訂為準"
        meaning_rule = "Revision 04 (R4-1, R4-4) prevails"
        cases: tuple[tuple[str, Callable[[str], str], str], ...] = (
            ("reversed precedence", lambda t: self.removed(t, exact, "與 R4-1、R4-4 衝突處以該 SPEC 為準"), meaning_rule),
            ("CM3 door 1: negated", lambda t: self.removed(t, exact, "與 R4-1、R4-4 衝突處不以本修訂為準"), meaning_rule),
            ("CM3 door 2: anything else than R4-1 and R4-4", lambda t: self.removed(t, exact, "與 R4-1、R4-4 以外的衝突處以本修訂為準"), meaning_rule),
            ("only R4-1", lambda t: self.removed(t, exact, "與 R4-1 衝突處以本修訂為準"), meaning_rule),
            ("competing reference allowed", lambda t: self.removed(t, "不構成互相競爭的 reference", "構成互相競爭的 reference"), "not a competing reference"),
            ("raises the halt", lambda t: self.removed(t, "不觸發 `ROUTE_REFERENCE_INVALID`", "觸發 `ROUTE_REFERENCE_INVALID`"), "raises no ROUTE_REFERENCE_INVALID"),
            ("runbooks left out", lambda t: self.removed_pattern(t, r"，以及 runbooks 目錄[^，]*，", "，"), "dated handover runbooks"),
            ("SPECs left out", lambda t: self.removed(t, "早於 Revision 04 的專案 SPEC", "專案 SPEC"), "SPECs that predate Revision 04"),
            ("any runbook, noted or not", lambda t: self.removed(t, "同一優先序註記", "優先序註記"), "carry the same precedence note"),
        )
        for name, change, meaning in cases:
            with self.subTest(name):
                self.setUp()
                self.edit(WORKFLOW, change)
                defects = precedence_defects(self.base)
                self.assertTrue(any(meaning in d for d in defects), defects)

    def test_a_case_whose_phrase_is_absent_raises_instead_of_turning_into_a_no_op(self) -> None:
        """S58-03: `removed` and `removed_pattern` assert that the phrase is present before they change it."""
        with self.assertRaises(AssertionError):
            self.removed("abc", "zzz", "y")
        with self.assertRaises(AssertionError):
            self.removed_pattern("abc", "zzz", "y")
        self.assertEqual(self.removed("abc", "b", "y"), "ayc")

    @staticmethod
    def removed_pattern(text: str, pattern: str, replacement: str) -> str:
        """`re.sub` that raises when the pattern matches nothing: a case never turns into a no-op."""
        changed, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            raise AssertionError(f"pattern not present: {pattern}")
        return changed

    def test_the_precedence_sentence_moved_out_of_section_zero_is_red(self) -> None:
        def move(text: str) -> str:
            line = next(l for l in text.split("\n") if PRECEDENCE_PHRASE in l)
            without = text.replace(line + "\n", "", 1)
            return without.rstrip("\n") + "\n\n" + line + "\n"

        self.edit(WORKFLOW, move)
        self.assertIn("PRECEDENCE_SENTENCE_OUTSIDE_SECTION_ZERO", precedence_defects(self.base))

    def test_the_precedence_sentence_absent_or_duplicated_is_red(self) -> None:
        self.edit(WORKFLOW, lambda t: self.removed(t, PRECEDENCE_PHRASE, "以其檔頭讀取"))
        self.assertTrue(any(d.startswith("PRECEDENCE_SENTENCE_COUNT 0") for d in precedence_defects(self.base)))
        self.setUp()
        self.append(WORKFLOW, f"- 另一句 {PRECEDENCE_PHRASE}。")
        self.assertTrue(any(d.startswith("PRECEDENCE_SENTENCE_COUNT 2") for d in precedence_defects(self.base)))

    # ---- part B: the handover runbook cites the sentence
    def test_a_handover_note_that_grants_itself_the_waiver_is_red(self) -> None:
        runbook = "doc/runbooks/handover-2026-08-22-plugin-distribution.md"
        self.edit(runbook, lambda t: self.removed(t, "`Workflow.md` section 0", "this note"))
        self.assertIn(f"HANDOVER_NOTE_DOES_NOT_CITE_WORKFLOW_SECTION_0 {runbook}", handover_citation_defects(self.base))


class PatternTableTests(unittest.TestCase):
    """The patterns are data: each one names its source finding and has an injection above."""

    INJECTED = {
        "a1 reviewer integrates", "a2 reviewer submits", "a3 fixed integrator role", "b1 bridge required or default",
        "b2 cross-lifetime requires controls", "c 審閱者整合 (zh)", "d 過渡路徑為預設 (zh)", "e dispatch carries a descriptor",
        "g1 reviewer merges, pushes or lands", "h1 dispatch is a queue row", "h2 queue holds more than candidates",
    }

    def test_every_pattern_has_a_source_comment_and_an_injection_case(self) -> None:
        self.assertEqual({pattern.name for pattern in PATTERNS}, self.INJECTED)
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.name):
                self.assertTrue(pattern.source)

    def test_no_pattern_of_the_reviewer_family_is_masked_by_the_integration_script_words(self) -> None:
        for pattern in PATTERNS:
            if pattern.name.split()[0] in {"a1", "a3", "c", "g1"}:
                with self.subTest(pattern=pattern.name):
                    for marker in pattern.exempt:
                        self.assertNotRegex("integration script", marker)
                        self.assertNotRegex("整合腳本", marker)
                        self.assertNotRegex("R4-4", marker)


if __name__ == "__main__":
    unittest.main()
