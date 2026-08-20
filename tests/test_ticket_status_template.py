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
# Achromatic states cannot be told apart by hue, so brightness has to do it.
# 3.0 is the WCAG floor for a non-text UI boundary; white against the grey
# DONE badge measures far above it, and a grey nudged toward white falls under.
_MIN_ACHROMATIC_CONTRAST = 3.0
# The finished row is a grey ground beside white ones. With no hue to help,
# the fill has to be visibly darker than the card it replaces.
_MIN_ROW_FILL_VS_CARD = 1.25
_MIN_ROW_FILL_VS_PAGE = 1.12
_MAX_NEUTRAL_CHROMA = 30
_YELLOW_BAND = (35.0, 70.0)

# V2-S3. The unfinished stage chip had gone quiet: achromatic by rule, and
# separated from the finished chip by tone alone, which is the one channel the
# grounds do not leave room for (see the ceiling cell). So the difference is
# carried by form, and these are the steps it has to clear.
#
# The edge step is in CSS pixels of *visible* border: finished stages paint
# theirs `transparent`, so the whole doubled edge of the open chip is the step.
_MIN_STAGE_EDGE_STEP = 2.0
_MIN_STAGE_WEIGHT_STEP = 300
# Tone is a supporting channel, never the load-bearing one -- the floor is set
# below `_MIN_ACHROMATIC_CONTRAST` on purpose, because the ceiling cell proves
# that floor is unreachable here. It is pinned so the tonal help cannot be
# quietly given away while the form channels are being edited.
_MIN_STAGE_TONE_STEP = 2.0
# Small text. A stage chip is 11px monospace, so this is the floor it has to
# clear against every ground it can land on, and the thing that caps tone.
_MIN_CHIP_TEXT_CONTRAST = 4.5

_PX = re.compile(r"([\d.]+)px")


def _declared(body: str, name: str) -> str | None:
    """One declaration's value, or None when the rule does not set it."""

    matched = re.search(rf"(?:^|;)\s*{re.escape(name)}\s*:\s*([^;]+)", body)
    return matched.group(1).strip() if matched else None


def _border_width(body: str, inherited: float = 0.0) -> float:
    for name in ("border-width", "border"):
        value = _declared(body, name)
        if value:
            found = _PX.search(value)
            if found:
                return float(found.group(1))
    return inherited


def _border_paint(body: str, inherited: str | None = None) -> str | None:
    """What the rule paints its edge with: a token, a keyword, or nothing."""

    value = _declared(body, "border-color")
    if value:
        return value
    shorthand = _declared(body, "border")
    if shorthand:
        parts = shorthand.split(None, 2)
        return parts[2] if len(parts) > 2 else None
    return inherited


def _visible_edge(width: float, paint: str | None) -> float:
    """An edge painted `transparent` is not an edge, whatever it measures."""

    if not paint or paint.strip() == "transparent":
        return 0.0
    return width


def _contrast_between(first: float, second: float) -> float:
    """Contrast straight from two luminances, for colours not yet chosen."""

    high, low = sorted((first, second), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _widest_legible_gap(grounds: tuple, floor: float = _MIN_CHIP_TEXT_CONTRAST) -> float:
    """The best two achromatic inks could ever do against these grounds.

    An achromatic ink can be placed at essentially any luminance, so the only
    question is which luminances stay readable on *every* ground the chip can
    land on. Sweeping that admissible set and taking its two ends gives the
    widest tonal gap the design could buy, regardless of which greys anybody
    picks -- which is what makes it a ceiling rather than a measurement of the
    greys currently in the file.
    """

    lit = [_luminance(ground) for ground in grounds]
    admissible = [
        step / 2000
        for step in range(2001)
        if all(_contrast_between(step / 2000, ground) >= floor for ground in lit)
    ]
    if len(admissible) < 2:
        return 0.0
    return _contrast_between(max(admissible), min(admissible))

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


def _chroma(colour: str) -> int:
    """Absolute max-min across channels. Relative saturation calls #12161c
    "saturated" because its channels differ by ten out of twenty-eight; this
    does not, which is what makes it the right measure for near-black greys."""

    digits = colour.strip().lstrip("#")
    channels = [int(digits[at : at + 2], 16) for at in (0, 2, 4)]
    return max(channels) - min(channels)


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
        "reason": None,
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
                reason="因為卡在這裡" if state in _REASON_STATES else None,
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
        # The glyph sits inside the title line, ahead of the words.
        self.assertIn('</svg>Owner 狀態頁</p>', self.page)
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
                    reason="<img onerror=x src=y>",
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
        self.assertIn('</svg>剛開的工單</p>', self.page)
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
        page = render(_document(_one_ticket(state="APPROVED", reason=None)))
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
                reason=None,
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
                _one_ticket(state="REJECTED", reason="喚醒證據沒有持久化，要補。")
            )
        )
        self.assertIn('<span class="badge" data-state="rejected">', page)
        self.assertIn("喚醒證據沒有持久化，要補。", page)
        self.assertIn("為什麼沒通過", page)

    def test_a_rejected_reason_is_not_captioned_as_a_needs_owner_reason(self) -> None:
        page = render(_document(_one_ticket(state="REJECTED", reason="要補。")))
        self.assertNotIn("為什麼等你", page)

    def test_a_missing_reason_is_stated_rather_than_swallowed(self) -> None:
        """The pipeline refuses to emit this; if one arrives, it must show."""

        for state in _REASON_STATES:
            with self.subTest(state=state):
                page = render(_document(_one_ticket(state=state, reason=None)))
                self.assertIn('data-missing="yes"', page)
                self.assertIn("這一列沒有附原因", page)

    def test_a_reason_carried_by_a_state_that_should_not_have_one_still_shows(
        self,
    ) -> None:
        """Dropping it silently would hide a pipeline defect from the owner."""

        page = render(_document(_one_ticket(state="DONE", reason="不該在這")))
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


class WarningGlyphTests(unittest.TestCase):
    """The waiting state signals with a shape, so it survives without colour."""

    def setUp(self) -> None:
        self.page = render(_every_state())

    def test_the_triangle_is_drawn_rather_than_typed(self) -> None:
        """An emoji is a different glyph per platform, and fonts recolour it."""

        self.assertIn('<svg class="warn"', self.page)
        for typed in ("⚠", "⚠️", "❗", "‼", "🔺", "🔶"):
            with self.subTest(typed=typed):
                self.assertNotIn(typed, self.page)

    def test_the_triangle_is_yellow_with_a_black_mark_inside(self) -> None:
        glyph = self.page[self.page.index('<svg class="warn"') :]
        glyph = glyph[: glyph.index("</svg>")]
        self.assertIn('fill="var(--warn-fill)"', glyph)
        self.assertIn('fill="var(--warn-glyph)"', glyph)
        self.assertIn('stroke="var(--warn-glyph)"', glyph)

    def test_only_the_waiting_state_carries_the_triangle(self) -> None:
        self.assertEqual(self.page.count('<svg class="warn"'), 1)
        approved = render(_document(_one_ticket(state="APPROVED", reason=None)))
        self.assertNotIn("<svg", approved)

    def test_the_glyph_is_announced_rather_than_left_as_decoration(self) -> None:
        self.assertIn('role="img"', self.page)
        self.assertIn('aria-label="等你決定"', self.page)

    def test_the_glyph_carries_no_namespace_url(self) -> None:
        """Inline SVG needs none, and it would be the page's only http:// ."""

        self.assertNotIn("xmlns", self.page)


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

    def test_finished_work_is_grey_rather_than_a_hue(self) -> None:
        """S1-1: the owner moved DONE out of the chromatic palette entirely."""

        for ground, palette in self.palettes.items():
            with self.subTest(ground=ground):
                self.assertLessEqual(
                    _chroma(palette["--done"]), _MAX_NEUTRAL_CHROMA
                )

    def test_the_achromatic_states_are_separated_by_brightness(self) -> None:
        """S1-2. Hue cannot separate white from grey, so nothing else may try.

        The hue-gap cell skips these two by construction -- it only compares
        chromatic tokens -- so without this cell the palette could collapse
        NEEDS_OWNER and DONE into the same tone and stay green.
        """

        for ground, palette in self.palettes.items():
            neutrals = [
                token
                for token in _STATE_TOKENS
                if _hue_and_saturation(palette[token])[1] < _CHROMATIC
            ]
            for left, right in itertools.combinations(sorted(neutrals), 2):
                with self.subTest(ground=ground, pair=(left, right)):
                    self.assertGreaterEqual(
                        _contrast(palette[left], palette[right]),
                        _MIN_ACHROMATIC_CONTRAST,
                        f"{left} and {right} are both grey and the same weight",
                    )

    def test_the_grey_fill_keeps_an_edge_on_both_grounds(self) -> None:
        """A grey ground beside a white one has only brightness to work with.

        This threshold is higher than the yellow fill needed, because the
        yellow had hue in reserve and this does not.
        """

        for ground, palette in self.palettes.items():
            for neighbour, floor in (
                ("--card", _MIN_ROW_FILL_VS_CARD),
                ("--bg", _MIN_ROW_FILL_VS_PAGE),
            ):
                with self.subTest(ground=ground, against=neighbour):
                    self.assertGreaterEqual(
                        _contrast(palette["--done-bg"], palette[neighbour]),
                        floor,
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

    def test_stage_chips_stay_out_of_the_states_hue_budget(self) -> None:
        """They were green when IN_PROGRESS became green. Now they own no hue.

        Stage completion and ticket verdict mean nothing to each other, so a
        green chip inside a green-badged row reads as agreement that is not
        there. Achromatic chips cannot collide with any state, including
        whichever colour the owner picks next.
        """

        for ground, palette in self.palettes.items():
            for token in ("--stage-done", "--stage-open"):
                with self.subTest(ground=ground, token=token):
                    self.assertLessEqual(
                        _chroma(palette[token]),
                        30,
                        "a stage chip is carrying a hue it can collide with",
                    )

    def test_a_verdict_and_a_stage_are_not_the_same_vocabulary(self) -> None:
        """S1-3, and the reason it is structural rather than a threshold.

        Both wear grey now, and tone cannot separate them: the badge grey needs
        white ink and the chip grey needs to sit on white and on the grey DONE
        ground, which forces both into the same narrow band (they measure about
        1.10:1 apart). So the rule is form, not tone -- a filled pill is always
        a verdict on the ticket, an outline is always a stage. Picking two
        greys far enough apart to pass an eye test is the thing this cell
        exists to stop somebody doing instead.
        """

        filled, outlined = [], []
        for selector, body in _rules(self.css):
            selector = selector.strip()
            declares_fill = re.search(r"background:var\(--[a-z0-9-]+\)", body)
            if re.fullmatch(r'\.badge\[data-state="[a-z-]+"\]', selector):
                filled.append((selector, bool(declares_fill)))
            if re.fullmatch(r'\.st(\[data-s="[a-z-]+"\])?', selector):
                outlined.append((selector, bool(declares_fill)))

        self.assertEqual(len(filled), 5)
        self.assertTrue(outlined)
        for selector, declares_fill in filled:
            with self.subTest(rule=selector):
                self.assertTrue(declares_fill, "a state badge stopped being filled")
        for selector, declares_fill in outlined:
            with self.subTest(rule=selector):
                self.assertFalse(declares_fill, "a stage chip took a filled ground")

    def test_the_only_yellow_left_on_the_page_is_the_warning_glyph(self) -> None:
        """Confirmed, not assumed: DONE leaving takes yellow with it."""

        low, high = _YELLOW_BAND
        found = []
        for ground, palette in self.palettes.items():
            for token, value in palette.items():
                if not value.startswith("#") or _chroma(value) <= _MAX_NEUTRAL_CHROMA:
                    continue
                hue, _ = _hue_and_saturation(value)
                if low <= hue <= high:
                    found.append((ground, token))
                    with self.subTest(ground=ground, token=token):
                        self.assertTrue(
                            token.startswith("--warn"),
                            f"{token} is yellow and is not the warning triangle",
                        )
        self.assertTrue(found, "the warning triangle stopped being yellow")

    def test_the_white_badge_declares_an_edge(self) -> None:
        """A badge that does not separate from the card must draw its own line."""

        for selector, body in _rules(self.css):
            matched = re.fullmatch(r'\.badge\[data-state="([a-z-]+)"\]', selector.strip())
            background = re.search(r"background:var\((--[a-z0-9-]+)\)", body)
            if not matched or not background:
                continue
            for ground, palette in self.palettes.items():
                separation = _contrast(palette[background.group(1)], palette["--card"])
                if separation >= 1.2:
                    continue
                with self.subTest(ground=ground, state=matched.group(1)):
                    self.assertIn(
                        "border-color:var(--",
                        body,
                        "this badge is the same tone as the card and has no edge",
                    )

    def _row(self, slug: str) -> str:
        """The row rule for a state, or empty when it declares none."""

        try:
            return _rule_body(self.css, f'.ticket[data-state="{slug}"]{{')
        except ValueError:
            return ""

    def test_the_loudness_ordering_holds_end_to_end(self) -> None:
        """S2-3, extended onto the cell that already owned this question.

        Structural, because badge luminance alone would say the opposite: in
        dark mode the white NEEDS_OWNER badge measures louder than the red
        REJECTED one, and the row treatments are what put that right.
        """

        self.assertIn("box-shadow:inset", self._row("rejected"))
        self.assertNotIn("box-shadow", self._row("needs-owner"))

        # Accepted work carries no emphasis mechanism whatsoever.
        approved = self._row("approved")
        for mechanism in ("box-shadow", "background:var(", "border-width"):
            with self.subTest(mechanism=mechanism):
                self.assertNotIn(mechanism, approved)
        page = render(_document(_one_ticket(state="APPROVED", reason=None)))
        self.assertNotIn("<svg", page)

    def test_the_two_quiet_states_differ_without_colour(self) -> None:
        """S2-1: the difference is an edge style, not a second hue."""

        self.assertIn("border-style:dashed", self._row("in-progress"))
        self.assertNotIn("dashed", self._row("approved"))

    def test_all_five_stay_separable_with_colour_removed(self) -> None:
        """S2-2, and the cell that shows why S2 was worth doing at all.

        Converted to greyscale the badges very nearly collapse: the closest
        pair measures about 1.03:1 in light mode, so hue is carrying almost
        none of the distinction and row form is carrying almost all of it. Two
        states with no form were therefore two states that did not exist for
        anyone who could not separate blue from green.

        So a pair counts as separable only if their rows differ structurally,
        or their badges differ by a real amount once colour is discarded.
        """

        shapes = {}
        for state, slug in _SLUG.items():
            page = render(
                _document(
                    _one_ticket(
                        state=state,
                        reason="因為" if state in _REASON_STATES else None,
                    )
                )
            )
            body = self._row(slug)
            shapes[slug] = (
                '<svg class="warn"' in page,
                bool(re.search(r"background:var\(--[a-z0-9-]+\)", body)),
                "box-shadow" in body,
                "border-style:dashed" in body,
            )

        inks = _badge_inks(self.css)
        for left, right in itertools.combinations(sorted(shapes), 2):
            if shapes[left] != shapes[right]:
                continue
            for ground, palette in self.palettes.items():
                with self.subTest(ground=ground, pair=(left, right)):
                    self.assertGreaterEqual(
                        _contrast(palette[inks[left][0]], palette[inks[right][0]]),
                        _MIN_ACHROMATIC_CONTRAST,
                        f"{left} and {right} are the same row with the same "
                        "brightness once the colour is gone",
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


class StageSignalTests(unittest.TestCase):
    """V2-S3 -- the unfinished stage is worth looking at again, without a hue.

    The approved mockup gave the open chip an amber outline. Amber left when
    the chips went achromatic to stop colliding with IN_PROGRESS green, and
    what remained -- an ink-coloured 1px box identical in construction to the
    box beside it -- is not a signal, because every chip in the row was the
    same object at a different brightness.

    Both channels that would normally fix that are closed. A hue is closed by
    rule: `test_stage_chips_stay_out_of_the_states_hue_budget` caps chip chroma
    so a chip can never collide with a state colour, including one the owner
    has not picked yet, and the yellow band is reserved for the warning
    triangle. Tone is closed by measurement rather than by rule, which is what
    the ceiling cell below records.

    So the signal is form, and the form is enclosure: finished stages give up
    their box, the unfinished one keeps it and doubles it. That also means no
    colour on the page changed, so S3-2 holds by construction -- there is no
    new value that could collide with anything.
    """

    def setUp(self) -> None:
        self.css = _stylesheet(render(_sample()))
        self.palettes = {
            "light": _palette(_rule_body(self.css, ":root{")),
            "dark": _palette(_rule_body(self.css, ':root[data-theme="dark"]{')),
        }
        base = _rule_body(self.css, ".st{")
        self.base_width = _border_width(base)
        self.base_paint = _border_paint(base)
        self.chip_size = float(_PX.search(_declared(base, "font-size")).group(1))
        self.chips = {}
        for slug in ("done", "open"):
            body = _rule_body(self.css, f'.st[data-s="{slug}"]{{')
            self.chips[slug] = {
                "body": body,
                "paint": _border_paint(body, self.base_paint),
                "edge": _visible_edge(
                    _border_width(body, self.base_width),
                    _border_paint(body, self.base_paint),
                ),
                "weight": int(_declared(body, "font-weight") or 400),
                "ink": _declared(body, "color"),
            }

    def test_the_unfinished_stage_is_the_only_boxed_chip_in_the_row(self) -> None:
        """S3-1. Being the sole enclosure is what the amber was really doing.

        The colour only made the outline visible; the outline was the signal.
        A box nothing else in the row has does the same work with no hue.
        """

        self.assertEqual(self.chips["done"]["paint"], "transparent")
        self.assertGreater(self.chips["open"]["edge"], 0.0)
        self.assertEqual(
            self.chips["done"]["edge"],
            0.0,
            "finished stages took their box back and the open chip is one of a set again",
        )

    def test_the_step_between_the_two_chips_clears_every_channel(self) -> None:
        """S3-1, with the thresholds in the assertions rather than the prose.

        Three independent channels, all of which survive being converted to
        greyscale. Making the two chips the same on any one of them is meant
        to turn this cell red on that channel alone.
        """

        self.assertGreaterEqual(
            self.chips["open"]["edge"] - self.chips["done"]["edge"],
            _MIN_STAGE_EDGE_STEP,
            "the unfinished chip's edge no longer outweighs the finished one's",
        )
        self.assertGreaterEqual(
            self.chips["open"]["weight"] - self.chips["done"]["weight"],
            _MIN_STAGE_WEIGHT_STEP,
            "the two chips are set at the same ink weight",
        )
        for ground, palette in self.palettes.items():
            with self.subTest(ground=ground):
                self.assertGreaterEqual(
                    _contrast(palette["--stage-open"], palette["--stage-done"]),
                    _MIN_STAGE_TONE_STEP,
                    "the supporting tonal difference was given away",
                )

    def test_both_chips_stay_readable_on_both_grounds_they_land_on(self) -> None:
        """A chip sits on a plain card or on the grey DONE row, never one only.

        This is the floor that caps the tonal channel, so it is asserted rather
        than assumed -- the ceiling cell's arithmetic is only true while this
        is the floor being applied.
        """

        for ground, palette in self.palettes.items():
            for token in ("--stage-open", "--stage-done"):
                for under in ("--card", "--done-bg"):
                    with self.subTest(ground=ground, token=token, under=under):
                        self.assertGreaterEqual(
                            _contrast(palette[token], palette[under]),
                            _MIN_CHIP_TEXT_CONTRAST,
                            f"{token} is not readable on {under}",
                        )

    def test_tone_could_not_have_carried_this_signal(self) -> None:
        """The measurement that forced S3-1 onto form, kept as a live premise.

        Not a measurement of the greys in the file -- a ceiling on every grey
        anybody could pick. A chip ink has to clear the small-text floor on the
        card *and* on the grey DONE row, and in dark mode those two grounds sit
        close enough together that the surviving band is narrow: the widest gap
        two achromatic inks can reach measures about 2.87:1, under the 3.0 this
        suite requires of two achromatic things that must read apart, and the
        ink that reaches it is pure white with zero margin left on the DONE
        ground. Pushing the chip greys apart therefore cannot work, and this
        cell exists to stop the next person spending a round finding that out.

        It fails if the grounds ever move far enough apart to reopen the tonal
        channel. That is not a regression; it means the reason this ticket
        chose form has expired and the choice is worth making again.
        """

        palette = self.palettes["dark"]
        ceiling = _widest_legible_gap((palette["--card"], palette["--done-bg"]))
        self.assertLess(
            ceiling,
            _MIN_ACHROMATIC_CONTRAST,
            f"two achromatic chip inks can now reach {ceiling:.3f}:1 on these "
            "grounds, so tone could separate the stage chips on its own; the "
            "form-carries-it reasoning behind V2-S3 is worth revisiting",
        )

    def test_a_stage_the_page_cannot_classify_never_reads_as_finished(self) -> None:
        """The one direction an unrecognised stage must not fail in.

        Finished work is what gives up its box, so a chip falling through to
        the base treatment must not also arrive boxless -- that would render a
        stage nobody could classify as one that is complete.
        """

        page = render(
            _document(
                _one_ticket(
                    stages=[
                        {"ref": "R1", "label": "樣張", "state": "HALF_WAY"},
                        {"ref": "R2", "label": "通知", "state": "DONE"},
                    ]
                )
            )
        )
        self.assertIn('<span class="st" data-s="unknown">R1 樣張</span>', page)
        self.assertGreater(
            _visible_edge(self.base_width, self.base_paint),
            self.chips["done"]["edge"],
            "an unclassified stage is drawn exactly like a finished one",
        )

    def test_the_stage_chip_stays_quieter_than_the_row_it_sits_in(self) -> None:
        """S3-3. A stage is a detail of the row, never the row's conclusion.

        Structural, for the reason `test_the_loudness_ordering_holds_end_to_end`
        already records: measured luminance ranks these the wrong way round,
        because the open chip wears the page's full ink and a badge does not.
        What actually orders them is which mechanisms each is allowed to use.
        The row owns the loud ones -- a filled ground, an inset bar -- and the
        chip owns none of them, so the chip cannot win however dark its edge.
        """

        badge = _rule_body(self.css, ".badge{")
        badge_size = float(_PX.search(_declared(badge, "font-size")).group(1))
        bar = _PX.search(_declared(_rule_body(
            self.css, '.ticket[data-state="rejected"]{'), "box-shadow"))

        for slug, chip in sorted(self.chips.items()):
            with self.subTest(chip=slug):
                # The two mechanisms that belong to the row and the badge.
                self.assertIsNone(_declared(chip["body"], "background"))
                self.assertIsNone(_declared(chip["body"], "box-shadow"))
                # A chip's edge never outweighs the row's own emphasis bar.
                self.assertLess(chip["edge"], float(bar.group(1)))
                self.assertLessEqual(chip["weight"], 700)
        self.assertLess(
            self.chip_size, badge_size, "a stage chip is set larger than a verdict"
        )

        # And the drawn signal stays the row's alone: no chip smuggles a glyph.
        page = render(_sample())
        stages = page[page.index('<div class="stages">') :]
        self.assertNotIn("<svg", stages[: stages.index("</div>")])


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
