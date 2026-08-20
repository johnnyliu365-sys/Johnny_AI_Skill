"""The ticket status page: honest absences, inert text, resolvable colours.

The defect this suite exists to prevent is a page that looks calm because a
source failed. Several cells therefore assert what the page must *not* say --
a page that renders "no tickets" over the top of a file it could not parse is
worse than no page, and no positive assertion catches that.

The second half is about text the repository did not write for us. Titles come
from ticket files and subjects come from `git log`; both are attacker-shaped in
the ordinary case where somebody commits an angle bracket. Escaping is asserted
on attribute values too, which is where it is usually missing.

The third half -- since the owner split "finished" from "accepted" -- is the
palette. Five states have to separate at a glance, so `PaletteTests` asserts
the *colours themselves* are far apart in hue rather than trusting that a
human looked once. That cell is what stops NEEDS_OWNER drifting back into the
amber band beside a yellow DONE row.

Cells are written against the committed sample document wherever possible, so
the renderer is tested on the data it will actually receive (pitfall C6).
"""

from __future__ import annotations

import ast
import copy
import itertools
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

# The order the pipeline sorts into: things a human must clear first, accepted
# work last. The template reproduces it and never re-derives it.
_PIPELINE_ORDER = ("NEEDS_OWNER", "REJECTED", "DONE", "IN_PROGRESS", "APPROVED")
_SLUG = {
    "NEEDS_OWNER": "needs-owner",
    "REJECTED": "rejected",
    "DONE": "done",
    "IN_PROGRESS": "in-progress",
    "APPROVED": "approved",
}
_REASON_STATES = ("NEEDS_OWNER", "REJECTED")

# The five colours a state can be wearing. `--open` is the deliberate neutral.
_STATE_TOKENS = ("--need", "--rejected", "--done", "--approved", "--open")
_MIN_HUE_GAP = 35.0
_CHROMATIC = 0.25

_TOKEN_DEFINITION = re.compile(r"(--[a-z0-9-]+)\s*:", re.IGNORECASE)
_TOKEN_USE = re.compile(r"var\((--[a-z0-9-]+)\)", re.IGNORECASE)
_TOKEN_VALUE = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;}]+)")
_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_ROW = re.compile(r'<article class="ticket" data-state="([a-z-]+)"')


def _sample() -> dict:
    return json.loads(_SAMPLE_PATH.read_text(encoding="utf-8"))


def _stylesheet(page: str) -> str:
    return page.split("<style>", 1)[1].split("</style>", 1)[0]


def _rule_body(css: str, header: str) -> str:
    """The declarations of one rule; these blocks never nest."""

    start = css.index(header) + len(header)
    return css[start : css.index("}", start)]


def _palette(block: str) -> dict:
    return {name: value.strip() for name, value in _TOKEN_VALUE.findall(block)}


def _hue_and_saturation(colour: str) -> tuple[float, float]:
    """HSV hue in degrees and saturation in 0..1, straight from the hex."""

    digits = colour.strip().lstrip("#")
    red, green, blue = (int(digits[at : at + 2], 16) for at in (0, 2, 4))
    high, low = max(red, green, blue), min(red, green, blue)
    span = high - low
    if not span:
        return 0.0, 0.0
    if high == red:
        hue = 60.0 * (((green - blue) / span) % 6)
    elif high == green:
        hue = 60.0 * ((blue - red) / span + 2)
    else:
        hue = 60.0 * ((red - green) / span + 4)
    return hue, span / high


def _hue_gap(first: float, second: float) -> float:
    gap = abs(first - second) % 360.0
    return min(gap, 360.0 - gap)


def _luminance(colour: str) -> float:
    digits = colour.strip().lstrip("#")
    channels = [int(digits[at : at + 2], 16) / 255 for at in (0, 2, 4)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _rules(css: str) -> list:
    """(selector, declarations) pairs, with comments stripped off the front."""

    return _RULE.findall(re.sub(r"/\*.*?\*/", "", css, flags=re.S))


def _badge_inks(css: str) -> dict:
    """Map each badge state to the (background, ink) tokens its rules resolve to."""

    base_background = base_ink = None
    per_state: dict = {}
    for selector, body in _rules(css):
        selector = selector.strip()
        background = re.search(r"background:var\((--[a-z0-9-]+)\)", body)
        ink = re.search(r"color:var\((--[a-z0-9-]+)\)", body)
        if selector == ".badge":
            base_background = background.group(1) if background else base_background
            base_ink = ink.group(1) if ink else base_ink
        matched = re.fullmatch(r'\.badge\[data-state="([a-z-]+)"\]', selector)
        if matched:
            per_state[matched.group(1)] = (
                background.group(1) if background else None,
                ink.group(1) if ink else None,
            )
    return {
        state: (background or base_background, ink or base_ink)
        for state, (background, ink) in per_state.items()
    }


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


def _every_state(order: tuple = _PIPELINE_ORDER) -> dict:
    return _document(
        *[
            _one_ticket(
                id=f"T{index}",
                state=state,
                why_waiting="因為卡在這裡" if state in _REASON_STATES else None,
            )
            for index, state in enumerate(order)
        ]
    )


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

    def test_a_populated_page_never_claims_to_be_empty(self) -> None:
        self.assertNotIn(_CALM, self.page)

    def test_the_page_is_reproducible(self) -> None:
        """No clock, no randomness: the document is the only input."""

        self.assertEqual(render(_sample()), render(_sample()))


class OrderingTests(unittest.TestCase):
    """Sorting is the pipeline's job; reproducing it exactly is this one's."""

    def test_the_order_the_pipeline_emitted_is_the_order_rendered(self) -> None:
        page = render(_every_state())
        self.assertEqual(
            _ROW.findall(page), [_SLUG[state] for state in _PIPELINE_ORDER]
        )

    def test_the_template_does_not_re_sort_what_it_is_given(self) -> None:
        """Two orderings in one system is one ordering nobody can test."""

        reversed_order = tuple(reversed(_PIPELINE_ORDER))
        page = render(_every_state(reversed_order))
        self.assertEqual(
            _ROW.findall(page), [_SLUG[state] for state in reversed_order]
        )


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

    def test_a_hostile_state_cannot_escape_the_row_attribute(self) -> None:
        page = render(_document(_one_ticket(state='" data-need="yes')))
        # The slug is looked up in a table, never interpolated from input, so a
        # hostile state cannot forge an attribute; the raw text survives only
        # as escaped characters in the badge caption.
        self.assertIn(
            '<article class="ticket" data-state="unknown" data-need="no">', page
        )
        self.assertIn("&quot; data-need=&quot;yes", page)

    def test_an_unparseable_timestamp_is_shown_rather_than_dropped(self) -> None:
        page = render(_document(_one_ticket(), generated_at="not a timestamp"))
        self.assertIn("not a timestamp", page)


class NullableFieldTests(unittest.TestCase):
    """V2-U3 -- every field documented as nullable will be null in practice."""

    def setUp(self) -> None:
        self.page = render(_document(_one_ticket()))

    def test_a_brand_new_ticket_still_renders_a_complete_row(self) -> None:
        self.assertIn(
            '<article class="ticket" data-state="needs-owner" data-need="yes">',
            self.page,
        )
        self.assertIn('<div class="id">V9 · owner-visibility</div>', self.page)
        self.assertIn('<p class="name">剛開的工單</p>', self.page)
        self.assertIn('<span class="badge" data-state="needs-owner">', self.page)
        self.assertIn("modules/tickets/owner-visibility/v9.md", self.page)
        self.assertIn("</article>", self.page)

    def test_an_absent_commit_is_stated_rather_than_left_as_a_gap(self) -> None:
        self.assertIn('<span class="lab">停在</span>', self.page)
        self.assertIn("尚未有 commit", self.page)

    def test_an_absent_stage_list_is_stated(self) -> None:
        self.assertIn("尚未列出階段", self.page)

    def test_absent_optional_blocks_are_omitted_rather_than_drawn_empty(self) -> None:
        self.assertNotIn("已發行於", self.page)

    def test_a_state_that_needs_no_reason_draws_no_reason_block(self) -> None:
        page = render(_document(_one_ticket(state="APPROVED", why_waiting=None)))
        self.assertNotIn('class="why"', page)
        self.assertNotIn("為什麼", page)

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


class ReasonTests(unittest.TestCase):
    """A row may never say work failed without saying what to fix."""

    def test_a_rejected_ticket_shows_its_reason(self) -> None:
        page = render(
            _document(
                _one_ticket(state="REJECTED", why_waiting="喚醒證據沒有持久化，要補。")
            )
        )
        self.assertIn('<span class="badge" data-state="rejected">', page)
        self.assertIn("喚醒證據沒有持久化，要補。", page)
        self.assertIn("為什麼沒通過", page)

    def test_a_rejected_reason_is_not_captioned_as_a_needs_owner_reason(self) -> None:
        page = render(_document(_one_ticket(state="REJECTED", why_waiting="要補。")))
        self.assertNotIn("為什麼等你", page)

    def test_a_missing_reason_is_stated_rather_than_swallowed(self) -> None:
        """The pipeline refuses to emit this; if one arrives, it must show."""

        for state in _REASON_STATES:
            with self.subTest(state=state):
                page = render(_document(_one_ticket(state=state, why_waiting=None)))
                self.assertIn('data-missing="yes"', page)
                self.assertIn("這一列沒有附原因", page)

    def test_a_reason_carried_by_a_state_that_should_not_have_one_still_shows(
        self,
    ) -> None:
        """Dropping it silently would hide a pipeline defect from the owner."""

        page = render(_document(_one_ticket(state="DONE", why_waiting="不該在這")))
        self.assertIn("不該在這", page)


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
        self.page = render(_every_state())

    def test_the_row_itself_carries_the_state(self) -> None:
        self.assertEqual(
            _ROW.findall(self.page), [_SLUG[state] for state in _PIPELINE_ORDER]
        )

    def test_the_distinction_survives_deleting_every_badge(self) -> None:
        """If the caption were the only carrier, this is where it would show."""

        stripped = re.sub(r'<span class="badge".*?</span>', "", self.page)
        self.assertEqual(len(set(_ROW.findall(stripped))), len(_PIPELINE_ORDER))

    def test_the_five_states_do_not_collapse_into_one_badge(self) -> None:
        slugs = re.findall(r'<span class="badge" data-state="([a-z-]+)"', self.page)
        self.assertEqual(slugs, [_SLUG[state] for state in _PIPELINE_ORDER])
        self.assertEqual(len(set(slugs)), 5, "two states share a badge treatment")

    def test_only_the_states_a_human_must_clear_are_flagged_for_the_owner(self) -> None:
        flags = re.findall(r'<article class="ticket" data-state="[a-z-]+" '
                           r'data-need="(\w+)"', self.page)
        self.assertEqual(flags, ["yes", "yes", "no", "no", "no"])

    def test_an_unrecognised_state_is_shown_rather_than_guessed_at(self) -> None:
        page = render(_document(_one_ticket(state="SOMETHING_NOBODY_WROTE_DOWN")))
        self.assertIn("SOMETHING_NOBODY_WROTE_DOWN", page)
        self.assertIn('data-state="unknown"', page)
        self.assertIn('data-need="no"', page)


class PaletteTests(unittest.TestCase):
    """The owner split the states so they would read apart. This checks that."""

    def setUp(self) -> None:
        self.css = _stylesheet(render(_sample()))
        self.palettes = {
            "light": _palette(_rule_body(self.css, ":root{")),
            "dark": _palette(_rule_body(self.css, ':root[data-theme="dark"]{')),
        }

    def test_every_state_has_its_own_colour_on_both_grounds(self) -> None:
        for ground, palette in self.palettes.items():
            with self.subTest(ground=ground):
                values = [palette[token] for token in _STATE_TOKENS]
                self.assertEqual(len(set(values)), len(_STATE_TOKENS))

    def test_the_chromatic_states_are_far_apart_in_hue(self) -> None:
        """NEEDS_OWNER sat in the amber band beside a yellow DONE. Never again."""

        for ground, palette in self.palettes.items():
            hues, neutrals = {}, []
            for token in _STATE_TOKENS:
                hue, saturation = _hue_and_saturation(palette[token])
                if saturation < _CHROMATIC:
                    neutrals.append(token)
                else:
                    hues[token] = hue
            with self.subTest(ground=ground, check="one neutral at most"):
                self.assertLessEqual(len(neutrals), 1)
            for left, right in itertools.combinations(sorted(hues), 2):
                with self.subTest(ground=ground, pair=(left, right)):
                    self.assertGreaterEqual(
                        _hue_gap(hues[left], hues[right]),
                        _MIN_HUE_GAP,
                        f"{left} and {right} read as the same colour at a glance",
                    )

    def test_finished_work_is_a_filled_row_not_only_a_chip(self) -> None:
        """The owner asked for a yellow 底, which means the ground, not a badge."""

        body = _rule_body(self.css, '.ticket[data-state="done"]{')
        self.assertIn("background:var(--done-bg)", body)
        self.assertIn("border-color:var(--done)", body)

    def test_the_yellow_fill_keeps_an_edge_on_both_grounds(self) -> None:
        """A pale yellow can match the page in brightness and lose its border.

        Hue alone is not enough: a fill that differs only in hue disappears for
        a reader who cannot separate those hues, and on a poorly calibrated
        panel. The fill has to be measurably darker than what surrounds it.
        """

        for ground, palette in self.palettes.items():
            for neighbour in ("--bg", "--card"):
                with self.subTest(ground=ground, against=neighbour):
                    self.assertGreaterEqual(
                        _contrast(palette["--done-bg"], palette[neighbour]),
                        1.12,
                        "the finished row blends into what surrounds it",
                    )

    def test_every_badge_is_legible_on_both_grounds(self) -> None:
        """Yellow is the one that loses its text, so nothing may assume white."""

        inks = _badge_inks(self.css)
        self.assertEqual(len(inks), 5)
        for ground, palette in self.palettes.items():
            for state, (background, ink) in sorted(inks.items()):
                with self.subTest(ground=ground, state=state):
                    self.assertIsNotNone(background)
                    self.assertIsNotNone(ink)
                    self.assertGreaterEqual(
                        _contrast(palette[background], palette[ink]), 4.5
                    )

    def test_the_unreadable_slab_is_the_loudest_thing_on_the_page(self) -> None:
        for ground, palette in self.palettes.items():
            with self.subTest(ground=ground):
                self.assertGreater(_contrast(palette["--alarm"], palette["--bg"]), 8.0)
                self.assertGreater(
                    _contrast(palette["--alarm"], palette["--alarm-ink"]), 8.0
                )

    def test_the_unreadable_block_borrows_no_state_colour(self) -> None:
        """It is not a sixth state, and must not be readable as one."""

        for selector, body in _RULE.findall(self.css):
            if ".unreadable" not in selector:
                continue
            for token in _STATE_TOKENS + ("--need-bg", "--done-bg", "--rejected-bg"):
                with self.subTest(selector=selector.strip(), token=token):
                    self.assertNotIn(f"var({token})", body)

    def test_no_badge_hardcodes_its_ink(self) -> None:
        """White on a light ground is the way yellow loses its text."""

        for selector, body in _RULE.findall(self.css):
            if ".badge" in selector and "color:" in body:
                with self.subTest(selector=selector.strip()):
                    self.assertIn("color:var(--", body)


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

    def test_every_state_colour_is_redefined_for_dark(self) -> None:
        for token in _STATE_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, self.system)
                self.assertIn(token, self.stamped)

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
