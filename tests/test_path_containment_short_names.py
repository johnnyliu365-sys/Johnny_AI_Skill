"""Ticket 63: a Windows 8.3 short name is the same path; a redirect is still refused."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from library.local_orchestration import path_containment
from library.local_orchestration.path_containment import resolves_within_root

_LONG_ROOT_NAME = "containment_root_with_a_long_name"
_LONG_CHILD_NAME = "child_directory_with_a_long_name"


def _short_name(path: Path) -> Path | None:
    """The 8.3 spelling of an existing path, or None when the volume has none."""

    if sys.platform != "win32":
        return None
    import ctypes

    kernel32 = ctypes.windll.kernel32
    buffer = ctypes.create_unicode_buffer(1024)
    if int(kernel32.GetShortPathNameW(str(path), buffer, 1024)) == 0:
        return None
    short = Path(buffer.value)
    return short if short != path else None


def _make_junction(link: Path, target: Path) -> bool:
    completed = subprocess.run(
        ("cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)),
        check=False,
        capture_output=True,
        shell=False,
        timeout=30,
    )
    return completed.returncode == 0


def _make_redirect(link: Path, target: Path) -> bool:
    """A symlink where permitted, otherwise a junction (Windows only)."""

    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        return sys.platform == "win32" and _make_junction(link, target)


@contextmanager
def _layout() -> Iterator[tuple[Path, Path, Path]]:
    """A resolved temporary parent holding a long-named root and an outside sibling."""

    with TemporaryDirectory() as temporary:
        parent = Path(temporary).resolve()
        root = parent / _LONG_ROOT_NAME
        (root / _LONG_CHILD_NAME).mkdir(parents=True)
        outside = parent / "outside_directory_with_a_long_name"
        outside.mkdir()
        yield parent, root, outside


class PrefixTests(unittest.TestCase):
    def test_equal_child_and_not_yet_created_leaf_are_contained(self) -> None:
        with _layout() as (_, root, _outside):
            self.assertTrue(resolves_within_root(root, root))
            self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME, root))
            self.assertTrue(resolves_within_root(root / "new" / "leaf", root))

    def test_a_sibling_sharing_the_prefix_is_refused(self) -> None:
        with _layout() as (parent, root, _outside):
            sibling = parent / (_LONG_ROOT_NAME + "x")
            sibling.mkdir()
            self.assertFalse(resolves_within_root(sibling, root))

    def test_outside_traversal_and_empty_path_are_refused(self) -> None:
        with _layout() as (_, root, outside):
            self.assertFalse(resolves_within_root(outside, root))
            self.assertFalse(resolves_within_root(root / ".." / outside.name, root))
            self.assertFalse(resolves_within_root(Path(""), root))

    def test_a_trailing_separator_does_not_change_the_answer(self) -> None:
        with _layout() as (_, root, outside):
            self.assertTrue(resolves_within_root(Path(str(root) + os.sep), root))
            self.assertFalse(resolves_within_root(outside, Path(str(root) + os.sep)))


class ShortNameTests(unittest.TestCase):
    def _need_short(self, path: Path) -> Path:
        short = _short_name(path)
        if short is None:
            self.skipTest("this volume has no 8.3 short name for the test directory")
        assert short is not None
        return short

    def test_short_root_and_long_target_are_contained(self) -> None:
        with _layout() as (_, root, _outside):
            short = self._need_short(root)
            self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME, short))
            self.assertTrue(resolves_within_root(short / "new" / "leaf", short))
            self.assertTrue(resolves_within_root(short, short))

    def test_long_root_and_short_target_are_contained(self) -> None:
        with _layout() as (_, root, _outside):
            short = self._need_short(root)
            self.assertTrue(resolves_within_root(short / _LONG_CHILD_NAME, root))

    def test_the_short_name_of_a_directory_outside_the_root_is_refused(self) -> None:
        with _layout() as (_, root, outside):
            short_outside = self._need_short(outside)
            self.assertFalse(resolves_within_root(short_outside, root))
            self.assertFalse(resolves_within_root(short_outside, self._need_short(root)))

    def test_a_failed_long_name_lookup_is_a_refusal(self) -> None:
        with _layout() as (_, root, _outside):
            short = self._need_short(root)
            with mock.patch.object(path_containment, "_long_name", return_value=None):
                self.assertFalse(resolves_within_root(short / _LONG_CHILD_NAME, short))

    def test_the_long_name_lookup_of_a_missing_path_is_none(self) -> None:
        if sys.platform != "win32":
            self.skipTest("short-name lookup exists only on Windows")
        with _layout() as (_, root, _outside):
            missing = root / "does" / "not" / "exist"
            self.assertIsNone(path_containment._long_name(missing))


class RedirectTests(unittest.TestCase):
    def test_a_redirect_inside_the_root_pointing_outside_is_refused(self) -> None:
        with _layout() as (_, root, outside):
            link = root / "redirect_to_outside"
            if not _make_redirect(link, outside):
                self.skipTest("no symlink or junction can be created here")
            self.assertFalse(resolves_within_root(link, root))
            self.assertFalse(resolves_within_root(link / "leaf", root))

    def test_a_redirected_base_is_refused(self) -> None:
        with _layout() as (parent, _root, outside):
            link = parent / "redirected_base"
            if not _make_redirect(link, outside):
                self.skipTest("no symlink or junction can be created here")
            self.assertFalse(resolves_within_root(link / "leaf", link))
            self.assertFalse(resolves_within_root(outside / "leaf", link))

    def test_a_short_name_does_not_hide_a_redirect_inside_the_root(self) -> None:
        with _layout() as (_, root, outside):
            link = root / "redirect_with_a_long_name"
            if not _make_redirect(link, outside):
                self.skipTest("no symlink or junction can be created here")
            short = _short_name(link)
            if short is None:
                self.skipTest("this volume has no 8.3 short name for the redirect")
            assert short is not None
            self.assertFalse(resolves_within_root(short, root))
            self.assertFalse(resolves_within_root(short / "leaf", root))

    def test_a_short_name_root_does_not_hide_a_redirected_base(self) -> None:
        with _layout() as (parent, _root, outside):
            link = parent / "redirected_base_with_a_long_name"
            if not _make_redirect(link, outside):
                self.skipTest("no symlink or junction can be created here")
            short = _short_name(link)
            if short is None:
                self.skipTest("this volume has no 8.3 short name for the redirect")
            assert short is not None
            self.assertFalse(resolves_within_root(short / "leaf", short))
            self.assertFalse(resolves_within_root(outside / "leaf", short))


if __name__ == "__main__":
    unittest.main()
