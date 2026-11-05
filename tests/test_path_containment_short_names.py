"""Ticket 63: a Windows 8.3 short name is the same path; a redirect is still refused."""

from __future__ import annotations

import ctypes
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


@contextmanager
def _junction(link: Path, target: Path) -> Iterator[bool]:
    """Create a junction and remove it afterwards; yield False when it cannot be made."""

    made = sys.platform == "win32" and _make_junction(link, target)
    try:
        yield made
    finally:
        if made:
            try:
                os.rmdir(link)
            except OSError:
                pass


@contextmanager
def _case_sensitive_parent() -> Iterator[Path | None]:
    """An empty directory whose names are case sensitive, or None where the host cannot."""

    with TemporaryDirectory() as temporary:
        parent = Path(temporary).resolve() / "case_sensitive_parent_directory"
        parent.mkdir()
        if sys.platform != "win32":
            yield None
            return
        completed = subprocess.run(
            ("fsutil.exe", "file", "setCaseSensitiveInfo", str(parent), "enable"),
            check=False,
            capture_output=True,
            shell=False,
            timeout=30,
        )
        if completed.returncode != 0:
            yield None
            return
        probe_lower = parent / "probe"
        probe_upper = parent / "PROBE"
        try:
            probe_lower.mkdir()
            probe_upper.mkdir()
        except OSError:
            yield None
            return
        os.rmdir(probe_lower)
        os.rmdir(probe_upper)
        yield parent


class FileSystemDecidedRedirectTests(unittest.TestCase):
    """Revision02: a redirect is decided from the file system, not from a spelling."""

    def test_a_case_twin_junction_base_through_a_short_parent_is_refused(self) -> None:
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            real = parent / "a"
            real.mkdir()
            (real / "x").mkdir()
            with _junction(parent / "A", real) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                short_parent = _short_name(parent)
                if short_parent is None:
                    self.skipTest("this volume has no 8.3 short name for the test directory")
                assert short_parent is not None
                base = short_parent / "A"
                self.assertFalse(resolves_within_root(base / "x", base))
                self.assertFalse(resolves_within_root(real / "x", base))

    def test_a_case_twin_junction_base_under_a_long_parent_is_refused(self) -> None:
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            real = parent / "a"
            real.mkdir()
            (real / "x").mkdir()
            with _junction(parent / "A", real) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                base = parent / "A"
                self.assertFalse(resolves_within_root(base / "x", base))
                self.assertFalse(resolves_within_root(real / "x", base))

    def test_a_kelvin_sign_junction_base_is_refused(self) -> None:
        with _layout() as (parent, _root, _outside):
            real = parent / "k"
            real.mkdir()
            (real / "x").mkdir()
            with _junction(parent / "\u212a", real) as made:
                if not made or not (parent / "\u212a").is_dir():
                    self.skipTest("no junction named with U+212A can be created here")
                base = parent / "\u212a"
                self.assertFalse(resolves_within_root(base / "x", base))
                self.assertFalse(resolves_within_root(real / "x", base))

    def test_an_ohm_sign_junction_base_through_a_short_parent_is_refused(self) -> None:
        with _layout() as (parent, _root, _outside):
            real = parent / "\u03c9"
            real.mkdir()
            (real / "x").mkdir()
            with _junction(parent / "\u2126", real) as made:
                if not made or not (parent / "\u2126").is_dir():
                    self.skipTest("no junction named with U+2126 can be created here")
                short_parent = _short_name(parent)
                if short_parent is None:
                    self.skipTest("this volume has no 8.3 short name for the test directory")
                assert short_parent is not None
                base = short_parent / "\u2126"
                self.assertFalse(resolves_within_root(base / "x", base))
                self.assertFalse(resolves_within_root(real / "x", base))
                long_base = parent / "\u2126"
                self.assertFalse(resolves_within_root(long_base / "x", long_base))

    def test_a_junction_in_an_ancestor_of_the_base_is_refused(self) -> None:
        with _layout() as (parent, root, _outside):
            link = parent / "ancestor_redirect_with_a_long_name"
            with _junction(link, root) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                base = link / _LONG_CHILD_NAME
                self.assertFalse(resolves_within_root(base / "x", base))
                short = _short_name(link)
                if short is not None:
                    short_base = short / _LONG_CHILD_NAME
                    self.assertFalse(resolves_within_root(short_base / "x", short_base))

    def test_a_case_twin_junction_in_an_ancestor_of_the_base_is_refused(self) -> None:
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            real = parent / "a"
            (real / "sub").mkdir(parents=True)
            with _junction(parent / "A", real) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                base = parent / "A" / "sub"
                self.assertFalse(resolves_within_root(base / "x", base))
                self.assertFalse(resolves_within_root(real / "sub" / "x", base))

    def test_a_case_twin_junction_in_an_ancestor_through_a_short_parent_is_refused(self) -> None:
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            real = parent / "a"
            (real / "sub").mkdir(parents=True)
            with _junction(parent / "A", real) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                short_parent = _short_name(parent)
                if short_parent is None:
                    self.skipTest("this volume has no 8.3 short name for the test directory")
                assert short_parent is not None
                base = short_parent / "A" / "sub"
                self.assertFalse(resolves_within_root(base / "x", base))

    def test_a_kelvin_sign_junction_in_an_ancestor_of_the_base_is_refused(self) -> None:
        with _layout() as (parent, _root, _outside):
            real = parent / "k"
            (real / "sub").mkdir(parents=True)
            with _junction(parent / "K", real) as made:
                if not made or not (parent / "K").is_dir():
                    self.skipTest("no junction named with U+212A can be created here")
                base = parent / "K" / "sub"
                self.assertFalse(resolves_within_root(base / "x", base))
                self.assertFalse(resolves_within_root(real / "sub" / "x", base))

    def test_a_component_that_cannot_be_examined_is_a_refusal(self) -> None:
        with _layout() as (_, root, _outside):
            real_lstat = os.lstat
            denied = root / _LONG_CHILD_NAME

            def lstat(path: str | os.PathLike[str]) -> os.stat_result:
                if Path(path) == denied:
                    raise PermissionError(13, "denied")
                return real_lstat(path)

            with mock.patch.object(os, "lstat", side_effect=lstat):
                self.assertFalse(resolves_within_root(denied / "x", denied))
                reason = path_containment._base_refusal_reason(denied)
            self.assertIsNotNone(reason)
            assert reason is not None
            self.assertIn("cannot be examined", reason)

    def test_a_base_that_does_not_exist_yet_is_not_a_redirect(self) -> None:
        with _layout() as (_, root, _outside):
            future = root / "not" / "created" / "yet"
            self.assertIsNone(path_containment._base_refusal_reason(future))

    def test_a_relative_base_is_refused(self) -> None:
        with _layout() as (_, root, _outside):
            self.assertFalse(resolves_within_root(root, Path(_LONG_ROOT_NAME)))


def _swap_for_junction_after_resolving(
    base: Path, link_to: Path
) -> tuple["mock._patch[object]", list[bool]]:
    """Patch ``Path.resolve`` so the first resolution of ``base`` is followed by a swap.

    Right after the real resolution of ``base`` returns, the (empty) directory
    ``base`` is replaced by a junction to ``link_to``: the race the reviewer's
    probe N2 describes. The list records whether the swap was made.
    """

    real_resolve = Path.resolve
    swapped: list[bool] = []

    def resolve(self: Path, strict: bool = False) -> Path:
        result = real_resolve(self, strict=strict)
        if self == base and not swapped:
            os.rmdir(base)
            swapped.append(_make_junction(base, link_to))
        return result

    return mock.patch.object(Path, "resolve", resolve), swapped


class OneResolutionTests(unittest.TestCase):
    """Correction 2: the base is resolved once and what was resolved was checked."""

    def setUp(self) -> None:
        if sys.platform != "win32":
            self.skipTest("a junction swap is the Windows shape under test")

    def test_a_base_swapped_for_a_junction_after_it_is_resolved_is_refused(self) -> None:
        with _layout() as (parent, _root, outside):
            (outside / "x").mkdir()
            base = parent / "swapped_base_with_a_long_name"
            base.mkdir()
            patch, swapped = _swap_for_junction_after_resolving(base, outside)
            try:
                with patch:
                    contained = resolves_within_root(base / "x", base)
            finally:
                if swapped:
                    os.rmdir(base)
            if swapped != [True]:
                self.skipTest("no junction can be created here")
            self.assertFalse(contained)

    def test_a_case_twin_swapped_in_after_the_base_is_resolved_is_refused(self) -> None:
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            real = parent / "a"
            (real / "x").mkdir(parents=True)
            base = parent / "A"
            base.mkdir()
            patch, swapped = _swap_for_junction_after_resolving(base, real)
            try:
                with patch:
                    contained = resolves_within_root(base / "x", base)
            finally:
                if swapped:
                    os.rmdir(base)
            if swapped != [True]:
                self.skipTest("no junction can be created here")
            self.assertFalse(contained)

    def test_the_base_is_resolved_exactly_once(self) -> None:
        with _layout() as (_, root, _outside):
            real_resolve = Path.resolve
            resolved: list[Path] = []

            def resolve(self: Path, strict: bool = False) -> Path:
                if self == root:
                    resolved.append(self)
                return real_resolve(self, strict=strict)

            with mock.patch.object(Path, "resolve", resolve):
                self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME, root))
            self.assertEqual(1, len(resolved))

    def test_the_resolved_spelling_is_examined_as_well_as_the_given_one(self) -> None:
        with _layout() as (_, root, _outside):
            short = _short_name(root)
            if short is None:
                self.skipTest("this volume has no 8.3 short name for the test directory")
            assert short is not None
            real_lstat = os.lstat

            def lstat(path: str | os.PathLike[str]) -> os.stat_result:
                if os.fspath(path) == str(root):
                    raise PermissionError(13, "denied")
                return real_lstat(path)

            self.assertTrue(resolves_within_root(short / _LONG_CHILD_NAME, short))
            with mock.patch.object(os, "lstat", side_effect=lstat):
                self.assertFalse(resolves_within_root(short / _LONG_CHILD_NAME, short))


class TypedStateTests(unittest.TestCase):
    def test_a_component_result_is_an_enum_member(self) -> None:
        with _layout() as (parent, root, _outside):
            passed = path_containment._examine_component(root)
            self.assertIs(path_containment._Component.PASS, passed.state)
            missing = path_containment._examine_component(root / "not" / "there")
            self.assertIs(path_containment._Component.MISSING, missing.state)
            self.assertIsNone(missing.reason)
            link = parent / "typed_state_junction"
            with _junction(link, root) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                refused = path_containment._examine_component(link)
                self.assertIs(path_containment._Component.REFUSE, refused.state)
                self.assertIsInstance(refused.reason, str)

    def test_the_component_states_are_exactly_pass_refuse_and_missing(self) -> None:
        self.assertEqual(
            {"PASS", "REFUSE", "MISSING"},
            {member.name for member in path_containment._Component},
        )

    def test_the_last_lookup_error_is_a_typed_field(self) -> None:
        self.assertIsInstance(path_containment._lookup_state, path_containment._LookupState)
        self.assertIsInstance(path_containment._lookup_state.error, int)

    def test_the_reason_function_is_private(self) -> None:
        self.assertFalse(hasattr(path_containment, "base_refusal_reason"))
        self.assertEqual(["resolves_within_root"], list(path_containment.__all__))


class CaseComparisonTests(unittest.TestCase):
    def test_a_lookup_that_differs_by_a_character_only_pathlib_folds_is_refused(self) -> None:
        # str.lower (pathlib equality) folds U+212A to "k"; the file system does not.
        if sys.platform != "win32":
            self.skipTest("short-name aliases exist only on Windows")
        with TemporaryDirectory() as temporary:
            parent = Path(temporary).resolve()
            root = parent / "kroot_directory_with_a_long_name"
            root.mkdir()
            short = _short_name(root)
            if short is None:
                self.skipTest("this volume has no 8.3 short name for the test directory")
            assert short is not None
            folded = parent / "\u212aroot_directory_with_a_long_name"
            self.assertEqual(root, folded)
            with mock.patch.object(path_containment, "_long_name", return_value=folded):
                self.assertFalse(resolves_within_root(short / "x", short))

    def test_a_different_case_of_the_same_directory_is_the_same_directory(self) -> None:
        if sys.platform != "win32":
            self.skipTest("case-insensitive naming is the Windows behaviour under test")
        with _layout() as (_, root, _outside):
            shouted = Path(str(root).upper())
            self.assertTrue(resolves_within_root(shouted / _LONG_CHILD_NAME.upper(), shouted))


class LongNameLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the long-name lookup exists only on Windows")

    def test_a_result_longer_than_the_first_buffer_is_read_after_a_retry(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the long-name lookup exists only on Windows")
        long_text = "C:\\" + "\\".join(["directory_name_of_some_length"] * 40)
        self.assertGreater(len(long_text), 1024)
        sizes: list[int] = []

        def fake(_name: str, buffer: ctypes.Array[ctypes.c_wchar], size: int) -> int:
            sizes.append(size)
            if size <= len(long_text):
                return len(long_text) + 1
            buffer.value = long_text
            return len(long_text)

        with mock.patch.object(path_containment, "_get_long_path_name", fake):
            result = path_containment._long_name(Path("C:\\anything"))
        self.assertEqual(Path(long_text), result)
        self.assertEqual(2, len(sizes))
        self.assertGreater(sizes[1], len(long_text))

    def test_a_result_that_keeps_growing_is_a_refusal(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the long-name lookup exists only on Windows")
        def fake(_name: str, _buffer: ctypes.Array[ctypes.c_wchar], size: int) -> int:
            return size + 5

        with mock.patch.object(path_containment, "_get_long_path_name", fake):
            self.assertIsNone(path_containment._long_name(Path("C:\\anything")))

    def test_a_failed_lookup_reads_the_last_error_into_the_refusal_reason(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the long-name lookup exists only on Windows")
        with _layout() as (_, root, _outside):
            short = _short_name(root)
            if short is None:
                self.skipTest("this volume has no 8.3 short name for the test directory")
            assert short is not None

            def fake(_name: str, _buffer: ctypes.Array[ctypes.c_wchar], _size: int) -> int:
                ctypes.set_last_error(5)
                return 0

            with mock.patch.object(path_containment, "_get_long_path_name", fake):
                reason = path_containment._base_refusal_reason(short)
            self.assertIsNotNone(reason)
            assert reason is not None
            self.assertIn("Windows error 5", reason)

    def test_the_real_lookup_of_a_missing_path_reports_a_windows_error(self) -> None:
        with _layout() as (_, root, _outside):
            self.assertIsNone(path_containment._long_name(root / "does" / "not" / "exist"))
            self.assertIn(path_containment._last_lookup_error(), (2, 3))

    def test_the_kernel_function_is_declared_once_with_last_error(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the long-name lookup exists only on Windows")
        from ctypes import wintypes

        function = path_containment._get_long_path_name
        self.assertEqual(
            [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD], list(function.argtypes)
        )
        self.assertIs(wintypes.DWORD, function.restype)
        self.assertIsInstance(path_containment._kernel32, ctypes.WinDLL)
        self.assertIs(path_containment._kernel32.GetLongPathNameW, function)


if __name__ == "__main__":
    unittest.main()
