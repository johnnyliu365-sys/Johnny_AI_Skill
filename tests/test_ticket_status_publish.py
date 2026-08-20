"""Wiring the two halves: the charset the page claims, and a whole file.

Both cells here catch failures that leave every other test green. A page
written in the host's default charset renders as mojibake while its own tests
pass, and a page read mid-write shows the owner a shorter list than the truth.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.ticket_status_publish import (
    page_path,
    publish,
    write_page,
)

_CHINESE = "等你決定"


def _repository(directory: Path) -> Path:
    subprocess.run(("git", "init", "-q", str(directory)), check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(
            ("git", "-C", str(directory), "config", name, value), check=True
        )
    folder = directory / "modules" / "tickets" / "demo"
    folder.mkdir(parents=True)
    (folder / "v9-demo.md").write_text(
        "# 測試工單\n\n```johnny-status\n"
        "id = V9\ntitle = 測試用工單\nstate = NEEDS_OWNER\n"
        "why_waiting = 等你決定方向\nstage = R1 | 樣張 | DONE\n"
        "```\n",
        encoding="utf-8",
    )
    subprocess.run(("git", "-C", str(directory), "add", "-A"), check=True)
    subprocess.run(
        ("git", "-C", str(directory), "commit", "-q", "-m", "ticket: open V9"),
        check=True,
    )
    return directory


class CharsetTests(unittest.TestCase):
    """The page declares UTF-8, so the bytes on disk have to be UTF-8.

    Python's default text encoding on this host is cp950. Writing without an
    explicit encoding produces a file whose bytes disagree with its own
    charset declaration: every test still passes and the owner double-clicks
    into mojibake.
    """

    def test_the_written_bytes_decode_as_utf8_and_carry_the_chinese(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            path = write_page(layout, f"<!doctype html><p>{_CHINESE}</p>")
            raw = path.read_bytes()
            self.assertIn(_CHINESE.encode("utf-8"), raw)
            self.assertEqual(raw.decode("utf-8").count(_CHINESE), 1)

    def test_the_bytes_are_not_the_hosts_default_encoding(self) -> None:
        """Discriminating: cp950 encodes this text to different bytes."""

        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            path = write_page(layout, _CHINESE)
            raw = path.read_bytes()
            self.assertNotEqual(raw, _CHINESE.encode("cp950"))
            self.assertEqual(raw, _CHINESE.encode("utf-8"))


class ReplacementTests(unittest.TestCase):
    """A refreshing browser must never read a half-written page."""

    def test_no_temporary_file_survives_the_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            write_page(layout, "<!doctype html><p>a</p>")
            self.assertEqual(list(Path(temporary).glob("*.tmp")), [])

    def test_a_second_write_replaces_rather_than_appends(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary))
            write_page(layout, "<!doctype html><p>first</p>")
            path = write_page(layout, "<!doctype html><p>second</p>")
            body = path.read_text(encoding="utf-8")
            self.assertNotIn("first", body)
            self.assertIn("second", body)


class PublishTests(unittest.TestCase):
    """End to end: a real repository reaches a real page on disk."""

    def test_a_declared_ticket_reaches_the_published_page(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            root = _repository(Path(workspace) / "repo")
            with tempfile.TemporaryDirectory() as johnny:
                layout = JohnnyRootLayout(base=Path(johnny))
                path = publish(root, layout)
                self.assertEqual(path, page_path(layout))
                body = path.read_bytes().decode("utf-8")
                self.assertIn("V9", body)
                self.assertIn("測試用工單", body)
                self.assertIn("等你決定方向", body)
                self.assertIn("git show", body)


if __name__ == "__main__":
    unittest.main()
