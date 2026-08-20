"""The owner status surface: honest lanes, distinct codes, atomic writes.

The defect this suite exists to prevent is a page that looks calm because a
source failed. Several cells therefore assert what the page must *not* say,
which is the only way to catch a lane that quietly renders "nothing waiting"
over the top of an unreadable file.
"""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.owner_status_surface import (
    Lane,
    LaneKind,
    OwnerStatusSurface,
    Severity,
    SurfaceItem,
    UnreadableSource,
    collect,
    owner_action,
    publish,
    render,
    surface_path,
    write_surface,
)

_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "library"
    / "local_orchestration"
    / "owner_status_surface.py"
)

# The four the ticket names: each one means a different job for the owner.
_OWNER_ACTIONABLE = (
    "CANDIDATE_INBOX",
    "BRANCH_HELD_BY_APP_TAB",
    "REVIEWER_NOT_MAPPED",
    "NOT_AUTHENTICATED",
)

_NOW = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)


def _surface(*lanes: Lane) -> OwnerStatusSurface:
    return OwnerStatusSurface(lanes=lanes, generated_at=_NOW)


class OwnerActionTests(unittest.TestCase):
    """A bare code is not an instruction; the owner needs the job named."""

    def test_every_owner_actionable_code_carries_its_own_instruction(self) -> None:
        instructions = {code: owner_action(code).instruction for code in _OWNER_ACTIONABLE}
        for code, instruction in instructions.items():
            with self.subTest(code=code):
                self.assertTrue(instruction.strip())
        self.assertEqual(
            len(set(instructions.values())),
            len(_OWNER_ACTIONABLE),
            "two codes share an instruction, so the page cannot tell them apart",
        )

    def test_the_codes_do_not_collapse_into_one_severity(self) -> None:
        """Four identical chips would make the lane a list, not a triage."""

        severities = {owner_action(code).severity for code in _OWNER_ACTIONABLE}
        self.assertGreaterEqual(len(severities), 3)

    def test_an_unknown_code_is_still_explained(self) -> None:
        action = owner_action("SOMETHING_NOBODY_WROTE_DOWN")
        self.assertTrue(action.instruction.strip())
        self.assertIs(action.severity, Severity.HOST)


class RenderedItemTests(unittest.TestCase):
    """What a source said reaches the page, and hostile text stays inert."""

    def test_each_code_renders_its_code_severity_and_instruction(self) -> None:
        for code in _OWNER_ACTIONABLE:
            with self.subTest(code=code):
                page = render(
                    _surface(
                        Lane(LaneKind.WAITING, (SurfaceItem("待處理", code=code),))
                    )
                )
                action = owner_action(code)
                self.assertIn(f'data-code="{code}"', page)
                self.assertIn(f'data-severity="{action.severity.value}"', page)
                self.assertIn(action.instruction, page)

    def test_identifiers_are_escaped_rather_than_rendered_as_markup(self) -> None:
        page = render(
            _surface(
                Lane(
                    LaneKind.WAITING,
                    (
                        SurfaceItem(
                            "<script>alert(1)</script>",
                            identifiers=(("project_id", "<img onerror=x>"),),
                            code="CANDIDATE_INBOX",
                        ),
                    ),
                )
            )
        )
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn("<img onerror=x>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_relative_age_leads_and_the_absolute_time_is_present(self) -> None:
        page = render(
            _surface(
                Lane(
                    LaneKind.WAITING,
                    (
                        SurfaceItem(
                            "待處理",
                            code="CANDIDATE_INBOX",
                            observed_at=_NOW - timedelta(hours=3),
                        ),
                    ),
                )
            )
        )
        self.assertIn("3 小時前", page)
        self.assertIn("2026-08-20T09:00:00+00:00", page)


class UnreadableLaneTests(unittest.TestCase):
    """The rule the whole page exists to keep."""

    def test_an_unreadable_lane_says_so_and_never_reads_as_nothing(self) -> None:
        page = render(
            _surface(
                Lane(
                    LaneKind.WAITING,
                    (),
                    (UnreadableSource("候選收件匣", "C:/x/inbox.jsonl", "壞掉的一行"),),
                )
            )
        )
        self.assertIn('class="unreadable"', page)
        self.assertIn("這不是「沒事」", page)
        self.assertIn("C:/x/inbox.jsonl", page)
        self.assertNotIn(
            "沒有事情等你",
            page,
            "an unreadable lane rendered the reassuring empty message",
        )

    def test_a_readable_empty_lane_says_it_is_genuinely_empty(self) -> None:
        page = render(_surface(Lane(LaneKind.WAITING)))
        self.assertIn("沒有事情等你", page)
        # The footer explains the policy in prose, so search for the block
        # itself rather than the words, which would match that explanation.
        self.assertNotIn('class="unreadable"', page)

    def test_a_partially_read_lane_is_flagged_even_though_it_has_items(self) -> None:
        """Items present plus a failed source is the most deceptive state."""

        lane = Lane(
            LaneKind.WAITING,
            (SurfaceItem("待處理", code="CANDIDATE_INBOX"),),
            (UnreadableSource("runner 狀態", "C:/x/state.json", "壞了"),),
        )
        self.assertFalse(lane.is_trustworthy)
        page = render(_surface(lane))
        self.assertIn("不完整", page)
        self.assertIn("本頁不完整", page)

    def test_a_fully_read_page_carries_no_incompleteness_claim(self) -> None:
        page = render(_surface(Lane(LaneKind.WAITING), Lane(LaneKind.DONE)))
        self.assertNotIn("本頁不完整", page)


class CollectionTests(unittest.TestCase):
    """Reading real files: missing is not broken, and neither silences a peer."""

    def test_a_corrupt_inbox_is_reported_unreadable_not_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            from library.local_orchestration.wake_candidate_inbox import (
                candidate_inbox_path,
            )

            path = candidate_inbox_path(layout)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{ this is not a record\n", encoding="utf-8")

            waiting = collect(layout).lanes[0]
            self.assertFalse(waiting.is_trustworthy)
            self.assertEqual(len(waiting.unreadable), 1)
            self.assertIn("候選收件匣", waiting.unreadable[0].label)

    def test_an_absent_source_is_empty_and_trustworthy(self) -> None:
        """Nothing recorded is a real answer; it must not read as a failure."""

        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            surface = collect(layout)
            for lane in surface.lanes:
                with self.subTest(lane=lane.kind):
                    self.assertTrue(lane.is_trustworthy)
                    self.assertEqual(lane.items, ())

    def test_a_broken_source_does_not_silence_the_other_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            from library.local_orchestration.wake_candidate_inbox import (
                candidate_inbox_path,
            )

            path = candidate_inbox_path(layout)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("garbage\n", encoding="utf-8")

            surface = collect(layout)
            self.assertFalse(surface.lanes[0].is_trustworthy)
            self.assertTrue(surface.lanes[1].is_trustworthy)
            self.assertTrue(surface.lanes[2].is_trustworthy)

    def test_registered_subscriptions_without_a_running_runner_reach_the_owner(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            from library.local_orchestration.event_runner import (
                runner_state_path,
                subscriptions_path,
            )

            subscriptions = subscriptions_path(layout)
            subscriptions.parent.mkdir(parents=True, exist_ok=True)
            subscriptions.write_text("{}", encoding="utf-8")
            state = runner_state_path(layout)
            state.write_text(json.dumps({"status": "BLOCKED"}), encoding="utf-8")

            waiting = collect(layout).lanes[0]
            codes = [item.code for item in waiting.items]
            self.assertIn("RUNNER_NOT_RUNNING", codes)


class WriteTests(unittest.TestCase):
    """A half-written page is a lying page."""

    def test_publish_leaves_one_complete_file_and_no_temporary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            path = publish(layout)
            self.assertEqual(path, surface_path(layout))
            body = path.read_text(encoding="utf-8")
            self.assertTrue(body.startswith("<!doctype html>"))
            self.assertTrue(body.rstrip().endswith("</html>"))
            leftovers = list(Path(temporary).glob("*.tmp"))
            self.assertEqual(leftovers, [])

    def test_a_second_write_replaces_the_page_rather_than_appending(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            write_surface(layout, _surface(Lane(LaneKind.WAITING)))
            write_surface(layout, _surface(Lane(LaneKind.WAITING)))
            body = surface_path(layout).read_text(encoding="utf-8")
            self.assertEqual(body.count("<!doctype html>"), 1)


class DependencyTests(unittest.TestCase):
    """The runtime venv is hash-locked; this module may not widen it."""

    def test_the_module_imports_only_the_standard_library_and_its_siblings(
        self,
    ) -> None:
        allowed = {
            "__future__",
            "ast",
            "dataclasses",
            "datetime",
            "enum",
            "html",
            "json",
            "os",
            "pathlib",
        }
        tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    with self.subTest(module=alias.name):
                        self.assertIn(alias.name.split(".")[0], allowed)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                with self.subTest(module=node.module):
                    self.assertIn((node.module or "").split(".")[0], allowed)


if __name__ == "__main__":
    unittest.main()
