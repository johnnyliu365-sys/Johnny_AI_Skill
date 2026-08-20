"""Tests for the V2 owner ticket status template."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
import unittest

from library.local_orchestration import ticket_status_template as template


_ROOT = Path(__file__).resolve().parents[1]
_SAMPLE_PATH = (
    _ROOT / "modules" / "tickets" / "owner-visibility" / "v2-document-sample.json"
)
_MODULE_PATH = (
    _ROOT
    / "library"
    / "local_orchestration"
    / "ticket_status_template.py"
)


def _load_sample() -> dict:
    return json.loads(_SAMPLE_PATH.read_text(encoding="utf-8"))


class ContractTests(unittest.TestCase):
    """V2-U1: contract fields are rendered for a real sample document."""

    def test_sample_document_renders_expected_fields(self) -> None:
        page = template.render(_load_sample())
        self.assertIn("V1", page)
        self.assertIn("R1", page)
        self.assertIn("f3a2981", page)
        self.assertIn("git show f3a2981 -- modules/tickets/owner-visibility/v1-owner-status-surface.md", page)
        self.assertIn("da33781", page)
        self.assertIn("git show da33781 -- modules/tickets/event-runner-binding/e14-claude-branch-wake-command.md", page)


class SafetyTests(unittest.TestCase):
    """V2-U2 and V2-U3."""

    def test_untrusted_text_is_escaped(self) -> None:
        doc = {
            "generated_at": "2026-08-20T20:14:00+08:00",
            "head": {"branch": "main", "commit": "abc"},
            "release": None,
            "rollback": None,
            "tickets": [
                {
                    "id": "X",
                    "module": "danger",
                    "title": "<script>alert(1)</script>",
                    "state": "DONE",
                    "why_waiting": None,
                    "stages": [],
                    "commit": {"sha": '<img src="x" onerror="alert(1)">', "subject": '"quoted"'},
                    "released_in": None,
                    "ticket_path": "<b>x</b>",
                    "handoff_command": 'cmd "x"',
                }
            ],
            "unreadable": [],
        }
        page = template.render(doc)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn('<img src="x" onerror="alert(1)">', page)
        self.assertNotIn("<b>x</b>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("&lt;img src=&quot;x&quot; onerror=&quot;alert(1)&quot;&gt;", page)
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)

    def test_nullable_fields_still_render_a_complete_row(self) -> None:
        doc = {
            "generated_at": "2026-08-20T20:14:00+08:00",
            "head": {"branch": "main", "commit": "abc"},
            "release": None,
            "rollback": None,
            "tickets": [
                {
                    "id": "X",
                    "module": "mod",
                    "title": "Null-safe",
                    "state": "IN_PROGRESS",
                    "why_waiting": None,
                    "stages": [],
                    "commit": None,
                    "released_in": None,
                    "ticket_path": "modules/tickets/x.md",
                    "handoff_command": "echo done",
                }
            ],
            "unreadable": [],
        }
        page = template.render(doc)
        self.assertIn("<article", page)
        self.assertIn("article", page)
        self.assertIn("Null-safe", page)
        self.assertIn("未完成提交", page)
        self.assertIn("未發行", page)


class UnreadableTests(unittest.TestCase):
    """V2-U4: missing source list must be prominent."""

    def test_unreadable_block_is_prominent_when_present(self) -> None:
        doc = _load_sample()
        doc["unreadable"] = [
            {
                "label": "工單 03 的狀態宣告",
                "path": "modules/tickets/workflow-governance/03-suite-fragility.md",
                "reason": "找不到 johnny-status 區塊",
            }
        ]
        page = template.render(doc)
        self.assertIn("無法完整讀取來源", page)
        self.assertIn("工單 03 的狀態宣告", page)
        self.assertIn("找不到 johnny-status 區塊", page)
        self.assertIn("modules/tickets/workflow-governance/03-suite-fragility.md", page)

    def test_unreadable_block_is_not_emitted_when_empty(self) -> None:
        doc = _load_sample()
        doc["unreadable"] = []
        page = template.render(doc)
        self.assertNotIn("無法完整讀取來源", page)


class StateTests(unittest.TestCase):
    """V2-U5: distinguish NEEDS_OWNER from DONE in structure, not words."""

    def test_state_is_structural_data_attribute(self) -> None:
        doc = {
            "generated_at": "2026-08-20T20:14:00+08:00",
            "head": {"branch": "main", "commit": "abc"},
            "release": None,
            "rollback": None,
            "tickets": [
                {
                    "id": "X",
                    "module": "mod",
                    "title": "Need owner",
                    "state": "NEEDS_OWNER",
                    "why_waiting": "test",
                    "stages": [],
                    "commit": {"sha": "a", "subject": "s"},
                    "released_in": None,
                    "ticket_path": "a",
                    "handoff_command": "echo a",
                },
                {
                    "id": "Y",
                    "module": "mod",
                    "title": "Done",
                    "state": "DONE",
                    "why_waiting": None,
                    "stages": [],
                    "commit": {"sha": "b", "subject": "s"},
                    "released_in": None,
                    "ticket_path": "b",
                    "handoff_command": "echo b",
                },
            ],
            "unreadable": [],
        }
        page = template.render(doc)
        self.assertIn('data-state="NEEDS_OWNER"', page)
        self.assertIn('data-state="DONE"', page)


class DependencyTests(unittest.TestCase):
    """V2-U6: pure stdlib + sibling imports only."""

    def test_module_imports_only_allowed_dependencies(self) -> None:
        allowed = {
            "__future__",
            "ast",
            "html",
            "json",
            "pathlib",
            "typing",
        }
        tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertIn(alias.name.split(".")[0], allowed)
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                if node.level:
                    continue
                self.assertIn(node.module.split(".")[0], allowed)


class ThemeTests(unittest.TestCase):
    """V2-U7: theme tokens are CSS-variable driven."""

    _STYLE_EXTRACT = re.compile(r"<style>(.*?)</style>", re.S)

    def test_theme_variables_use_root_tokens(self) -> None:
        page = template.render(_load_sample())
        style_match = self._STYLE_EXTRACT.search(page)
        self.assertIsNotNone(style_match)
        style = style_match.group(1)
        self.assertIn("body{", style)
        self.assertIn("background:var(--surface-bg)", style)
        self.assertIn(":root{", style)
        self.assertIn(":root[data-theme=\"dark\"]", style)
        self.assertIn("@media (prefers-color-scheme: dark)", style)
        self.assertRegex(style, r":root\\[data-theme=\"dark\"\\][\\s\\S]*--surface-bg:var\\(--bg-dark\\)")
        dark_block = style.split(":root[data-theme=\"dark\"]", 1)[1]
        self.assertNotRegex(dark_block, r"#[0-9A-Fa-f]{3,8}\\b")
        media_block = style.split("@media (prefers-color-scheme: dark)", 1)[1]
        self.assertNotRegex(media_block, r"#[0-9A-Fa-f]{3,8}\\b")


