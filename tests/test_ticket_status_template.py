"""The ticket status page: honest absences, inert text, resolvable colours.

The defect this suite exists to prevent is a page that looks calm because a
source failed. Several cells therefore assert what the page must *not* say --
a page that renders "no tickets" over the top of a file it could not parse is
worse than no page, and no positive assertion catches that.

The other half of the suite is about text the repository did not write for us.
Titles come from ticket files and subjects come from `git log`; both are
attacker-shaped in the ordinary case where somebody commits an angle bracket.
Escaping is asserted on attribute values too, which is where it is usually
missing.

Cells are written against the committed sample document rather than against
invented fixtures wherever possible, so the renderer is tested on the data it
will actually receive (pitfall register C6).
"""

from __future__ import annotations

import ast
import copy
import json
import re
import unittest
from pathlib import Path

from library.local_orchestration.ticket_status_template import render

_ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = (
    _ROOT / "library" / "local_orchestration" / "ticket_status_template.py"
)
_SAMPLE_PATH = (
    _ROOT / "modules" / "tickets" / "owner-visibility" / "v2-document-sample.json"
)

# The reassuring sentence. It may only ever appear when nothing failed to read.
_CALM = "沒有工單"

_TOKEN_DEFINITION = re.compile(r"(--[a-z0-9-]+)\s*:", re.IGNORECASE)
_TOKEN_USE = re.compile(r"var\((--[a-z0-9-]+)\)", re.IGNORECASE)


def _sample() -> dict:
    return json.loads(_SAMPLE_PATH.read_text(encoding="utf-8"))


def _stylesheet(page: str) -> str:
    return page.split("<style>", 1)[1].split("</style>", 1)[0]


def _rule_body(css: str, header: str) -> str:
    """The declarations of one rule; these blocks never nest."""

    start = css.index(header) + len(header)
    return css[start : css.index("}", start)]


def _one_ticket(**overrides: object) -> dict:
    ticket = {
        "id": "V9",
        "module": "owner-visibility",
        "title": "剛開的工單",
        "state": "NEEDS_OWNER",
        "why_waiting": None,
        "stages": [],
        "commit": None,
        "released_in": None,
        "ticket_path": "modules/tickets/owner-visibility/v9.md",
        "handoff_command": "git show HEAD -- modules/tickets/owner-visibility/v9.md",
    }
    ticket.update(overrides)
    return ticket


def _document(*tickets: dict, **overrides: object) -> dict:
    document = {
        "generated_at": "2026-08-20T20:14:00+08:00",
        "head": {"branch": "main", "commit": "c1bb040"},
        "release": None,
        "rollback": None,
        "tickets": list(tickets),
        "unreadable": [],
    }
    document.update(overrides)
    return document


class ApprovedLayoutTests(unittest.TestCase):
    """V2-U1 -- the sample document reaches the page the owner approved."""

    def setUp(self) -> None:
        self.page = render(_sample())

    def test_the_waiting_ticket_arrives_whole(self) -> None:
        self.assertIn('<div class="id">V1 · owner-visibility</div>', self.page)
        self.assertIn('<p class="name">Owner 狀態頁</p>', self.page)
        self.assertIn('<span class="st" data-s="done">R1 樣張</span>', self.page)
        self.assertIn('<span class="st" data-s="open">R4 通知</span>', self.page)
        self.assertIn('<span class="val">f3a2981</span>', self.page)
        self.assertIn("feat: render the owner status surface", self.page)
        self.assertIn(
            "<code>git show f3a2981 -- "
            "modules/tickets/owner-visibility/v1-owner-status-surface.md</code>",
            self.page,
        )
        self.assertIn("做出來的是工人進度頁", self.page)

    def test_the_done_ticket_arrives_whole(self) -> None:
        self.assertIn('<div class="id">E14 · event-runner-binding</div>', self.page)
        self.assertIn('<span class="st" data-s="done">R10 守衛</span>', self.page)
        self.assertIn('<span class="val">da33781</span>', self.page)
        self.assertIn(
            '<span class="lab">已發行於</span><span class="val">v0.4.5</span>',
            self.page,
        )
        self.assertIn(
            "<code>git show da33781 -- "
            "modules/tickets/event-runner-binding/e14-claude-branch-wake-command.md"
            "</code>",
            self.page,
        )

    def test_the_bar_answers_which_tree_this_is(self) -> None:
        self.assertIn("main <code>c1bb040</code>", self.page)
        self.assertIn("發行 <b>v0.4.5</b> <code>1233e45</code>", self.page)
        self.assertIn("回滾點 <code>f3a2981</code>", self.page)
        self.assertIn('<time datetime="2026-08-20T20:14:00+08:00">', self.page)
        self.assertIn("2026-08-20 20:14", self.page)

    def test_the_order_the_pipeline_promised_is_the_order_rendered(self) -> None:
        """NEEDS_OWNER first is the pipeline's job; re-sorting here would fork it."""

        self.assertLess(
            self.page.index("V1 · owner-visibility"),
            self.page.index("E14 · event-runner-binding"),
        )

    def test_a_populated_page_never_claims_to_be_empty(self) -> None:
        self.assertNotIn(_CALM, self.page)

    def test_the_page_is_reproducible(self) -> None:
        """No clock, no randomness: the document is the only input."""

        self.assertEqual(render(_sample()), render(_sample()))


class EscapingTests(unittest.TestCase):
    """V2-U2 -- text from files and from git is inert, attributes included."""

    def test_a_hostile_title_and_subject_never_reach_the_page_as_markup(self) -> None:
        page = render(
            _document(
                _one_ticket(
                    title='<script>alert("boom")</script>',
                    module='"><b>module</b>',
                    commit={"sha": "abc1234", "subject": '<script>alert("git")</script>'},
                    why_waiting="<img onerror=x src=y>",
                    handoff_command='git show "<script>"',
                ),
                unreadable=[
                    {
                        "label": "<script>label</script>",
                        "path": "C:/x/<img onerror=x>.md",
                        "reason": '"quoted"',
                    }
                ],
            )
        )
        self.assertNotIn("<script", page)
        self.assertNotIn("</script>", page)
        self.assertNotIn("<img onerror=x", page)
        self.assertNotIn('alert("boom")', page)
        self.assertNotIn("<b>module</b>", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("&quot;", page)

    def test_an_attribute_value_cannot_be_escaped_out_of(self) -> None:
        """`generated_at` lands in an attribute, which is the forgotten half."""

        page = render(_document(_one_ticket(), generated_at='" onload="alert(1)'))
        self.assertNotIn('onload="', page)
        self.assertNotIn('" onload=', page)
        self.assertIn("&quot; onload=&quot;alert(1)", page)

    def test_an_unparseable_timestamp_is_shown_rather_than_dropped(self) -> None:
        page = render(_document(_one_ticket(), generated_at="not a timestamp"))
        self.assertIn("not a timestamp", page)


class NullableFieldTests(unittest.TestCase):
    """V2-U3 -- every field documented as nullable will be null in practice."""

    def setUp(self) -> None:
        self.page = render(_document(_one_ticket()))

    def test_a_brand_new_ticket_still_renders_a_complete_row(self) -> None:
        self.assertIn('<article class="ticket" data-need="yes">', self.page)
        self.assertIn('<div class="id">V9 · owner-visibility</div>', self.page)
        self.assertIn('<p class="name">剛開的工單</p>', self.page)
        self.assertIn('<span class="badge" data-state="need">', self.page)
        self.assertIn("modules/tickets/owner-visibility/v9.md", self.page)
        self.assertIn("</article>", self.page)

    def test_an_absent_commit_is_stated_rather_than_left_as_a_gap(self) -> None:
        self.assertIn('<span class="lab">停在</span>', self.page)
        self.assertIn("尚未有 commit", self.page)

    def test_an_absent_stage_list_is_stated(self) -> None:
        self.assertIn("尚未列出階段", self.page)

    def test_absent_optional_blocks_are_omitted_rather_than_drawn_empty(self) -> None:
        self.assertNotIn("已發行於", self.page)
        self.assertNotIn("為什麼等你", self.page)

    def test_a_document_with_no_release_and_no_rollback_says_so(self) -> None:
        self.assertIn("尚未發行", self.page)
        self.assertIn("尚無回滾點", self.page)

    def test_nulls_in_every_nullable_position_at_once_do_not_raise(self) -> None:
        document = _document(
            generated_at=None, head=None, release=None, rollback=None
        )
        document["tickets"] = [
            _one_ticket(
                id=None,
                module=None,
                title=None,
                state="DONE",
                stages=None,
                commit=None,
                released_in=None,
                why_waiting=None,
                ticket_path=None,
                handoff_command=None,
            )
        ]
        document["unreadable"] = None
        page = render(document)
        self.assertIn('<article class="ticket"', page)
        self.assertTrue(page.rstrip().endswith("</html>"))


class UnreadableTests(unittest.TestCase):
    """V2-U4 -- the rule that outranks the layout."""

    def _broken(self, count: int = 1) -> dict:
        sources = [
            {
                "label": f"工單 0{index} 的狀態宣告",
                "path": f"modules/tickets/workflow-governance/0{index}.md",
                "reason": "找不到 johnny-status 區塊",
            }
            for index in range(1, count + 1)
        ]
        return _document(unreadable=sources)

    def test_an_unreadable_source_is_stated_with_its_path_and_reason(self) -> None:
        page = render(self._broken())
        self.assertIn('class="unreadable"', page)
        self.assertIn("本頁不完整", page)
        self.assertIn("工單 01 的狀態宣告", page)
        self.assertIn("modules/tickets/workflow-governance/01.md", page)
        self.assertIn("找不到 johnny-status 區塊", page)

    def test_the_count_is_stated_so_the_owner_knows_how_much_is_missing(self) -> None:
        page = render(self._broken(3))
        self.assertIn('data-unreadable="3"', page)
        self.assertIn("有 3 個來源讀不到", page)

    def test_a_list_short_because_of_a_failure_never_reads_as_nothing_to_do(
        self,
    ) -> None:
        """The whole page exists to prevent this one sentence appearing here."""

        page = render(self._broken())
        self.assertNotIn(
            _CALM,
            page,
            "the page told the owner there is no work while a source was unread",
        )
        self.assertIn("不是因為沒事", page)

    def test_a_genuinely_empty_page_is_allowed_to_say_so(self) -> None:
        page = render(_document())
        self.assertIn(_CALM, page)
        self.assertNotIn('class="unreadable"', page)
        self.assertNotIn("本頁不完整", page)

    def test_tickets_present_plus_a_failed_source_is_still_flagged(self) -> None:
        """Items present alongside a failure is the most deceptive state."""

        document = self._broken()
        document["tickets"] = _sample()["tickets"]
        page = render(document)
        self.assertIn('class="unreadable"', page)
        self.assertIn("本頁不完整", page)

    def test_the_warning_precedes_the_tickets(self) -> None:
        document = self._broken()
        document["tickets"] = _sample()["tickets"]
        page = render(document)
        self.assertLess(
            page.index('class="unreadable"'),
            page.index('<article class="ticket"'),
            "the owner can scroll past a warning that sits below the list",
        )


class StateDistinctionTests(unittest.TestCase):
    """V2-U5 -- the row is marked, not merely captioned."""

    def setUp(self) -> None:
        self.page = render(
            _document(
                _one_ticket(id="A", state="NEEDS_OWNER"),
                _one_ticket(id="B", state="IN_PROGRESS"),
                _one_ticket(id="C", state="DONE"),
            )
        )

    def test_the_row_itself_carries_the_distinction(self) -> None:
        rows = re.findall(r'<article class="ticket"[^>]*>', self.page)
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            [re.search(r'data-need="(\w+)"', row).group(1) for row in rows],
            ["yes", "no", "no"],
        )

    def test_the_distinction_survives_deleting_every_badge(self) -> None:
        """If the caption were the only carrier, this is where it would show."""

        stripped = re.sub(r'<span class="badge".*?</span>', "", self.page)
        self.assertIn('data-need="yes"', stripped)
        self.assertIn('data-need="no"', stripped)

    def test_the_three_states_do_not_collapse_into_one_badge(self) -> None:
        slugs = re.findall(r'<span class="badge" data-state="([a-z]+)"', self.page)
        self.assertEqual(slugs, ["need", "open", "done"])
        self.assertEqual(len(set(slugs)), 3, "two states share a badge treatment")

    def test_an_unrecognised_state_is_shown_rather_than_guessed_at(self) -> None:
        page = render(_document(_one_ticket(state="SOMETHING_NOBODY_WROTE_DOWN")))
        self.assertIn("SOMETHING_NOBODY_WROTE_DOWN", page)
        self.assertIn('data-need="no"', page)


class ThemeTests(unittest.TestCase):
    """V2-U7 -- light, dark, and the unstamped "system" state all resolve."""

    def setUp(self) -> None:
        self.css = _stylesheet(render(_sample()))
        self.root = _TOKEN_DEFINITION.findall(_rule_body(self.css, ":root{"))
        self.system = _TOKEN_DEFINITION.findall(
            _rule_body(self.css, ':root:not([data-theme="light"]){')
        )
        self.stamped = _TOKEN_DEFINITION.findall(
            _rule_body(self.css, ':root[data-theme="dark"]{')
        )

    def test_the_bare_root_palette_is_complete(self) -> None:
        self.assertEqual(self.css.count(":root{"), 1)
        self.assertTrue(self.root)
        self.assertLessEqual(set(self.system), set(self.root))
        self.assertLessEqual(set(self.stamped), set(self.root))

    def test_every_colour_used_resolves_without_a_media_query(self) -> None:
        """A token defined only in a dark block is invisible in the default state."""

        for token in set(_TOKEN_USE.findall(self.css)):
            with self.subTest(token=token):
                self.assertIn(token, self.root)

    def test_no_token_is_defined_outside_the_three_root_blocks(self) -> None:
        remainder = self.css
        for header in (
            ":root{",
            ':root:not([data-theme="light"]){',
            ':root[data-theme="dark"]{',
        ):
            remainder = remainder.replace(_rule_body(remainder, header), "")
        self.assertEqual(_TOKEN_DEFINITION.findall(remainder), [])

    def test_the_toggle_and_the_system_preference_agree(self) -> None:
        self.assertEqual(set(self.system), set(self.stamped))

    def test_body_paints_an_explicit_token_background(self) -> None:
        self.assertIn("background:var(--bg)", _rule_body(self.css, "body{"))


class FileProtocolTests(unittest.TestCase):
    """Double-clicked from Explorer, with no server and no network."""

    def setUp(self) -> None:
        self.page = render(_sample())

    def test_the_page_is_a_single_self_contained_document(self) -> None:
        self.assertTrue(self.page.startswith("<!doctype html>"))
        self.assertTrue(self.page.rstrip().endswith("</html>"))
        self.assertIn('<meta charset="utf-8">', self.page)
        self.assertIn("<style>", self.page)

    def test_nothing_on_the_page_reaches_for_the_network(self) -> None:
        for forbidden in ("<script", "<link", "fetch(", "http://", "https://", "@import"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.page)


class DependencyTests(unittest.TestCase):
    """The runtime venv is hash-locked; this module may not widen it."""

    def setUp(self) -> None:
        self.tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))

    def test_the_module_imports_only_the_standard_library(self) -> None:
        allowed = {"__future__", "datetime", "html"}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    with self.subTest(module=alias.name):
                        self.assertIn(alias.name.split(".")[0], allowed)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                with self.subTest(module=node.module):
                    self.assertIn((node.module or "").split(".")[0], allowed)

    def test_the_template_never_touches_the_filesystem(self) -> None:
        """Writing the page is the pipeline's job; rendering it is this one's."""

        called = {
            node.func.id
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        for forbidden in ("open", "print", "exec", "eval"):
            with self.subTest(call=forbidden):
                self.assertNotIn(forbidden, called)

    def test_rendering_does_not_mutate_the_document_it_was_given(self) -> None:
        document = _sample()
        before = copy.deepcopy(document)
        render(document)
        self.assertEqual(document, before)


if __name__ == "__main__":
    unittest.main()
