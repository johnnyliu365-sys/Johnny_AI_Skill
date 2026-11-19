"""Wave-3 rule texts (ticket 74): the seven anchored rules and the Workflow section-3 link, held as a test.

Each rule stands at a named place in a named governance document, behind an HTML anchor on its own
line. This test finds every anchor exactly once, in its named file and section, and reads the rule's
block (the anchor line to the next anchor or heading, whichever comes first) for the terms the ticket
fixes. `Workflow.md` section 3 must link `#rule-process-tier`.

The check is a function over a root directory (`find_defects`), so each injection case below runs it on a
temporary copy of the documents with one sentence of the rules damaged, and must go red; the unmodified
copy must stay green. A named file that is missing or not UTF-8 is a defect that names the file.
"""
from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

REFERENCES = "skills/johnny-project-takeover/references"
ROUTER_CONTROL = f"{REFERENCES}/router-control.md"
IMPLEMENTATION_AUTHORITY = f"{REFERENCES}/implementation-authority.md"
SPECIFICATION_TICKETING = f"{REFERENCES}/specification-ticketing.md"
CODE_REVIEW = "CodeReview.md"
WORKFLOW = "Workflow.md"

HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")
FENCE = re.compile(r"^[ \t]*(```|~~~)")
ANCHOR_LINE = re.compile(r'^<a id="([^"]+)"></a>[ \t]*$')

WORKFLOW_SECTION_3 = "## 3. Tickets"
PROCESS_TIER_LINK = f"{SPECIFICATION_TICKETING}#rule-process-tier"


@dataclass(frozen=True)
class Rule:
    """One rule: its anchor id, its file, the heading that must be the nearest above it, and its terms.

    `terms` is a tuple of alternatives per required term: a block carries a term when it carries any of
    that term's alternatives.
    """

    rule_id: str
    path: str
    section: str  # the nearest heading above the anchor starts with this text, `#` marks included
    terms: tuple[tuple[str, ...], ...]


RULES: tuple[Rule, ...] = (
    Rule("rule-content-digest-only", ROUTER_CONTROL, "## Receipt integrity", (("digest",), ("--candidate",))),
    Rule("rule-seat-residue", IMPLEMENTATION_AUTHORITY, "## Allocation and correction", (("run id",), ("STATEMENT",))),
    Rule("rule-process-tier", SPECIFICATION_TICKETING, "## Ticket", (("Process tier",), ("standard",), ("strict",))),
    Rule("rule-smallest-fix", CODE_REVIEW, "## 4. ", (("rule B", "規則 B"),)),
    Rule("rule-consolidated-correction", IMPLEMENTATION_AUTHORITY, "## Allocation and correction", (("supersede",),)),
    Rule("rule-review-label", CODE_REVIEW, "## 5. ", (("CONVERGENCE_REVIEW_REQUIRED",),)),
    Rule("rule-dispatch-authoring", SPECIFICATION_TICKETING, "## Dispatch normalization", (("dispatch file",),)),
)

DOCUMENT_PATHS: tuple[str, ...] = tuple(sorted({rule.path for rule in RULES} | {WORKFLOW}))


class UnreadableDocument(Exception):
    """A named document is missing or not UTF-8; the message names the file."""


def read_lines(root: Path, relative: str) -> list[str]:
    path = root / relative
    try:
        text = path.read_bytes().decode("utf-8")
    except FileNotFoundError as exc:
        raise UnreadableDocument(f"{relative}: file is missing") from exc
    except UnicodeDecodeError as exc:
        raise UnreadableDocument(f"{relative}: not UTF-8 ({exc.reason})") from exc
    except OSError as exc:
        raise UnreadableDocument(f"{relative}: unreadable ({exc.strerror})") from exc
    return text.splitlines()


def heading_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Return (index, heading text with its `#` marks) for each heading outside code fences."""
    found: list[tuple[int, str]] = []
    in_fence = False
    for index, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            found.append((index, f"{match.group(1)} {match.group(2)}"))
    return found


def block_of(lines: list[str], anchor_index: int) -> list[str]:
    """The lines after the anchor up to the next anchor or heading, or the end of the file."""
    headings = {index for index, _ in heading_lines(lines)}
    block: list[str] = []
    for index in range(anchor_index + 1, len(lines)):
        if index in headings or ANCHOR_LINE.match(lines[index]):
            break
        block.append(lines[index])
    return block


def nearest_heading(lines: list[str], anchor_index: int) -> str:
    above = [text for index, text in heading_lines(lines) if index < anchor_index]
    return above[-1] if above else ""


def rule_defects(root: Path, rule: Rule, documents: dict[str, list[str]]) -> list[str]:
    defects: list[str] = []
    lines = documents[rule.path]
    marker = f'id="{rule.rule_id}"'
    on_own_line = [index for index, line in enumerate(lines) if (m := ANCHOR_LINE.match(line)) and m.group(1) == rule.rule_id]
    anywhere = sum(line.count(marker) for line in lines)
    if len(on_own_line) != 1 or anywhere != 1:
        defects.append(
            f"{rule.rule_id}: expected exactly one anchor line in {rule.path}, "
            f"found {len(on_own_line)} on its own line and {anywhere} in all"
        )
        return defects
    for other_path, other_lines in documents.items():
        if other_path != rule.path and any(marker in line for line in other_lines):
            defects.append(f"{rule.rule_id}: the anchor also stands in {other_path}")
    anchor_index = on_own_line[0]
    heading = nearest_heading(lines, anchor_index)
    if not heading.startswith(rule.section):
        defects.append(
            f"{rule.rule_id}: in {rule.path} it stands under {heading!r}, expected a section starting {rule.section!r}"
        )
    block = block_of(lines, anchor_index)
    block_text = "\n".join(block)
    if not block_text.strip():
        defects.append(f"{rule.rule_id}: the block after the anchor in {rule.path} is empty")
    for alternatives in rule.terms:
        if not any(term in block_text for term in alternatives):
            defects.append(
                f"{rule.rule_id}: the block in {rule.path} lacks the term {' or '.join(repr(t) for t in alternatives)}"
            )
    return defects


def workflow_link_defects(documents: dict[str, list[str]]) -> list[str]:
    lines = documents[WORKFLOW]
    start = next((i for i, line in enumerate(lines) if line.strip() == WORKFLOW_SECTION_3), None)
    if start is None:
        return [f"{WORKFLOW}: section {WORKFLOW_SECTION_3!r} not found"]
    end = len(lines)
    for index, text in heading_lines(lines):
        if index > start and text.startswith("## "):
            end = index
            break
    section = "\n".join(lines[start:end])
    if f"]({PROCESS_TIER_LINK})" not in section:
        return [f"{WORKFLOW}: section 3 does not link {PROCESS_TIER_LINK}"]
    return []


def find_defects(root: Path) -> list[str]:
    """Every defect of the rule texts under `root`; an unreadable named file is one defect naming it."""
    documents: dict[str, list[str]] = {}
    defects: list[str] = []
    for relative in DOCUMENT_PATHS:
        try:
            documents[relative] = read_lines(root, relative)
        except UnreadableDocument as exc:
            defects.append(str(exc))
    if defects:
        return defects
    for rule in RULES:
        defects.extend(rule_defects(root, rule, documents))
    defects.extend(workflow_link_defects(documents))
    return defects


def copy_documents(destination: Path) -> None:
    for relative in DOCUMENT_PATHS:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / relative, target)


def anchor_line(rule_id: str) -> str:
    return f'<a id="{rule_id}"></a>'


class RuleTextsInRepository(unittest.TestCase):
    def test_every_rule_stands_at_its_place_with_its_terms(self) -> None:
        self.assertEqual(find_defects(REPO), [])

    def test_the_seven_rules_are_the_seven_named_ones(self) -> None:
        self.assertEqual(
            [rule.rule_id for rule in RULES],
            [
                "rule-content-digest-only",
                "rule-seat-residue",
                "rule-process-tier",
                "rule-smallest-fix",
                "rule-consolidated-correction",
                "rule-review-label",
                "rule-dispatch-authoring",
            ],
        )


class RuleTextsInjection(unittest.TestCase):
    """Each case damages a temporary copy in one way; the copy must go red, and the clean copy green."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        copy_documents(self.root)

    def rewrite(self, relative: str, change: Callable[[str], str]) -> None:
        path = self.root / relative
        before = path.read_bytes().decode("utf-8")
        after = change(before)
        self.assertTrue(before != after, "the injection changed nothing")
        path.write_bytes(after.encode("utf-8"))

    def assertRed(self, *fragments: str) -> None:
        defects = find_defects(self.root)
        self.assertTrue(defects, "the damaged copy stayed green")
        joined = "\n".join(defects)
        for fragment in fragments:
            self.assertIn(fragment, joined)

    def test_the_clean_copy_is_green(self) -> None:
        self.assertEqual(find_defects(self.root), [])

    def test_removed_anchor_is_red(self) -> None:
        line = anchor_line("rule-content-digest-only")
        self.rewrite(ROUTER_CONTROL, lambda text: text.replace(line + "\n", "", 1))
        self.assertRed("rule-content-digest-only", ROUTER_CONTROL)

    def test_anchor_moved_to_another_section_is_red(self) -> None:
        line = anchor_line("rule-review-label") + "\n"

        def move(text: str) -> str:
            removed = text.replace(line, "", 1)
            return removed.replace("## 4. Finding 路由\n", "## 4. Finding 路由\n\n" + line, 1)

        self.rewrite(CODE_REVIEW, move)
        self.assertRed("rule-review-label", "expected a section starting '## 5. '")

    def test_duplicated_anchor_is_red(self) -> None:
        line = anchor_line("rule-process-tier") + "\n"
        self.rewrite(SPECIFICATION_TICKETING, lambda text: text.replace(line, line + "\ntext\n\n" + line, 1))
        self.assertRed("rule-process-tier", "found 2")

    def test_anchor_standing_in_a_second_file_is_red(self) -> None:
        line = anchor_line("rule-smallest-fix")
        self.rewrite(WORKFLOW, lambda text: text + "\n" + line + "\n")
        self.assertRed("rule-smallest-fix", f"also stands in {WORKFLOW}")

    def test_longer_id_is_not_the_anchor(self) -> None:
        line = anchor_line("rule-process-tier")
        self.rewrite(SPECIFICATION_TICKETING, lambda text: text.replace(line, anchor_line("rule-process-tier-x"), 1))
        self.assertRed("rule-process-tier", "found 0")

    def test_longer_id_beside_the_anchor_does_not_count_as_a_duplicate(self) -> None:
        line = anchor_line("rule-process-tier")
        self.rewrite(SPECIFICATION_TICKETING, lambda text: text.replace(line, line + "\n\n" + anchor_line("rule-process-tier-x"), 1))
        self.assertEqual(
            [d for d in find_defects(self.root) if "found 2" in d],
            [],
        )

    def test_anchor_followed_by_an_empty_paragraph_is_red(self) -> None:
        self.rewrite(
            SPECIFICATION_TICKETING,
            lambda text: text[: text.index(anchor_line("rule-dispatch-authoring")) + len(anchor_line("rule-dispatch-authoring"))] + "\n",
        )
        self.assertRed("rule-dispatch-authoring", "is empty")

    def test_removed_required_term_is_red(self) -> None:
        def strip(text: str) -> str:
            start = text.index(anchor_line("rule-seat-residue"))
            end = text.index(anchor_line("rule-consolidated-correction"))
            return text[:start] + text[start:end].replace("run id", "tag") + text[end:]

        self.rewrite(IMPLEMENTATION_AUTHORITY, strip)
        self.assertRed("rule-seat-residue", "'run id'")

    def test_removed_workflow_link_is_red(self) -> None:
        self.rewrite(WORKFLOW, lambda text: text.replace(f"]({PROCESS_TIER_LINK})", "](#tickets)"))
        self.assertRed("section 3 does not link", PROCESS_TIER_LINK)

    def test_workflow_link_moved_out_of_section_3_is_red(self) -> None:
        link = f"]({PROCESS_TIER_LINK})"

        def move(text: str) -> str:
            return text.replace(link, "](#tickets)", 1) + f"\n[x{link}\n"

        self.rewrite(WORKFLOW, move)
        self.assertRed("section 3 does not link")

    def test_missing_file_is_red_and_named(self) -> None:
        (self.root / CODE_REVIEW).unlink()
        self.assertRed(f"{CODE_REVIEW}: file is missing")

    def test_non_utf8_file_is_red_and_named(self) -> None:
        (self.root / ROUTER_CONTROL).write_bytes(b"# Router\n\xff\xfe\n")
        self.assertRed(f"{ROUTER_CONTROL}: not UTF-8")


if __name__ == "__main__":
    unittest.main()
