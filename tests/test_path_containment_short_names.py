"""Ticket 63: a Windows 8.3 short name is the same path; a redirect is still refused."""

from __future__ import annotations

import ctypes
import os
import stat
import subprocess
import sys
import types
import unittest
from collections.abc import Callable, Iterator
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
    base: Path, link_to: Path, before: bool = False, at_call: int = 1
) -> tuple["mock._patch[object]", list[bool]]:
    """Patch ``Path.resolve`` so that one chosen resolution comes with a swap.

    On the ``at_call``-th call of ``Path.resolve`` (the first by default), right
    after the real resolution returns (right before it when ``before`` is set),
    the empty directory ``base`` is replaced by a junction to ``link_to``: the
    race the reviewer's probe N2 describes, and the windows between a component
    walk and a resolution. The list records whether the swap was made.
    """

    real_resolve = Path.resolve
    swapped: list[bool] = []
    calls: list[Path] = []

    def swap() -> None:
        os.rmdir(base)
        swapped.append(_make_junction(base, link_to))

    def resolve(self: Path, strict: bool = False) -> Path:
        calls.append(self)
        due = len(calls) == at_call
        if due and before:
            swap()
        result = real_resolve(self, strict=strict)
        if due and not before:
            swap()
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

    def test_a_case_twin_swapped_in_before_the_base_is_resolved_is_refused(self) -> None:
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            real = parent / "a"
            (real / "x").mkdir(parents=True)
            base = parent / "A"
            base.mkdir()
            patch, swapped = _swap_for_junction_after_resolving(base, real, before=True)
            try:
                with patch:
                    contained = resolves_within_root(base / "x", base)
            finally:
                if swapped:
                    os.rmdir(base)
            if swapped != [True]:
                self.skipTest("no junction can be created here")
            self.assertFalse(contained)

    def test_a_base_swapped_for_a_junction_before_the_second_resolution_is_refused(self) -> None:
        # The second resolution in the predicate is the target's. The anchor was
        # the base as resolved and checked, so a swap after that must not move it.
        with _layout() as (parent, _root, outside):
            (outside / "x").mkdir()
            base = parent / "late_swapped_base_with_a_long_name"
            base.mkdir()
            patch, swapped = _swap_for_junction_after_resolving(
                base, outside, before=True, at_call=2
            )
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


class CaseExactContainmentTests(unittest.TestCase):
    """Revision03 rule 1: containment folds no case (S63-14)."""

    def test_a_sibling_whose_name_pathlib_folds_to_the_roots_is_refused(self) -> None:
        # The reviewer's F1: U+212A folds to "k" under str.lower, not on NTFS.
        if sys.platform != "win32":
            self.skipTest("the fold of U+212A by pathlib equality is the Windows behaviour")
        with TemporaryDirectory() as temporary:
            parent = Path(temporary).resolve()
            root = parent / "\u212aroot"
            sibling = parent / "kroot"
            try:
                root.mkdir()
                sibling.mkdir()
            except OSError:
                self.skipTest("this volume cannot hold both spellings")
            if os.path.samefile(root, sibling):
                self.skipTest("this volume folds U+212A onto k")
            (sibling / "victim").mkdir()
            self.assertEqual(root, sibling)
            self.assertFalse(resolves_within_root(sibling / "victim", root))
            self.assertFalse(resolves_within_root(sibling / "new" / "leaf", root))
            self.assertFalse(resolves_within_root(sibling, root))
            (root / "inside").mkdir()
            self.assertTrue(resolves_within_root(root / "inside", root))

    def test_a_case_variant_sibling_in_a_case_sensitive_directory_is_refused(self) -> None:
        # The reviewer's F2.
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            root = parent / "Root"
            sibling = parent / "root"
            (sibling / "victim").mkdir(parents=True)
            root.mkdir()
            self.assertFalse(resolves_within_root(sibling / "victim", root))
            self.assertFalse(resolves_within_root(sibling / "new" / "leaf", root))
            self.assertFalse(resolves_within_root(sibling, root))
            self.assertTrue(resolves_within_root(root / "new", root))

    def test_the_final_check_is_an_exact_component_prefix(self) -> None:
        with _layout() as (_, root, _outside):
            with mock.patch.object(Path, "resolve", lambda self, strict=False: self):
                self.assertTrue(resolves_within_root(root / "x", root))
                self.assertFalse(resolves_within_root(Path(str(root).upper()) / "x", root))


class FileIdentityTests(unittest.TestCase):
    """Revision03 rules 2 to 4: same directory by identity, held across the walk."""

    def test_a_case_twin_present_at_the_resolve_and_gone_at_the_walk_is_refused(self) -> None:
        # The reviewer's SW5: junction A to a at the resolve, the real A back for the walk.
        if sys.platform != "win32":
            self.skipTest("a junction swap is the Windows shape under test")
        with _case_sensitive_parent() as parent:
            if parent is None:
                self.skipTest("a case-sensitive directory cannot be created on this host")
            assert parent is not None
            twin = parent / "a"
            (twin / "x").mkdir(parents=True)
            base = parent / "A"
            (base / "x").mkdir(parents=True)
            held = parent / "held_real_A"
            real_resolve = Path.resolve
            made: list[bool] = []
            outcomes: list[bool] = []
            for target in (twin / "x", base / "x"):
                calls: list[Path] = []

                def resolve(self: Path, strict: bool = False) -> Path:
                    calls.append(self)
                    if len(calls) != 1:
                        return real_resolve(self, strict=strict)
                    os.rename(base, held)
                    made.append(_make_junction(base, twin))
                    result = real_resolve(self, strict=strict)
                    if made[-1]:
                        os.rmdir(base)
                    os.rename(held, base)
                    return result

                with mock.patch.object(Path, "resolve", resolve):
                    outcomes.append(resolves_within_root(target, base))
            if made != [True, True]:
                self.skipTest("no junction can be created here")
            # The twin is the anchor of the first call; its own child is then "inside".
            self.assertEqual([False, False], outcomes)

    def test_a_base_replaced_by_another_directory_after_the_resolve_is_refused(self) -> None:
        with _layout() as (parent, _root, _outside):
            base = parent / "replaced_base_with_a_long_name"
            base.mkdir()
            held = parent / "held_original_base"
            real_resolve = Path.resolve
            calls: list[Path] = []

            def resolve(self: Path, strict: bool = False) -> Path:
                calls.append(self)
                result = real_resolve(self, strict=strict)
                if len(calls) == 1:
                    os.rename(base, held)
                    os.mkdir(base)
                return result

            with mock.patch.object(Path, "resolve", resolve):
                self.assertFalse(resolves_within_root(base / "x", base))

    def test_an_identity_that_cannot_be_read_is_a_refusal(self) -> None:
        with _layout() as (_, root, _outside):
            real_stat = os.stat

            def stat(path: str | os.PathLike[str], *args: object, **kwargs: object) -> os.stat_result:
                if os.fspath(path) == str(root):
                    raise PermissionError(13, "denied")
                return real_stat(path, *args, **kwargs)  # type: ignore[arg-type]

            with mock.patch.object(os, "stat", side_effect=stat):
                self.assertFalse(resolves_within_root(root / "x", root))
                reason = path_containment._base_refusal_reason(root)
            self.assertIsNotNone(reason)
            assert reason is not None
            self.assertIn("identity", reason)

    def test_the_identity_of_a_missing_path_counts_the_missing_components(self) -> None:
        with _layout() as (_, root, _outside):
            here = path_containment._identity(root)
            assert here is not None
            self.assertEqual(0, here[2])
            self.assertEqual(
                (here[0], here[1], 2), path_containment._identity(root / "a" / "b")
            )

    def test_an_lstat_result_without_file_attributes_is_a_refusal(self) -> None:
        # S63-11: refuse rather than raise.
        if sys.platform != "win32":
            self.skipTest("the reparse attribute exists only on Windows")
        with _layout() as (_, root, _outside):
            bare = types.SimpleNamespace(st_mode=stat.S_IFDIR | 0o755)
            with mock.patch.object(os, "lstat", return_value=bare):
                result = path_containment._examine_component(root)
                self.assertIs(path_containment._Component.REFUSE, result.state)
                self.assertFalse(resolves_within_root(root / "x", root))


class DanglingLinkTests(unittest.TestCase):
    """Revision04 S63-17: a link whose target does not exist yet is a link, not a gap."""

    def test_a_dangling_junction_pointing_outside_is_refused(self) -> None:
        # The reviewer's G1, G1b and G1c.
        if sys.platform != "win32":
            self.skipTest("a junction is the Windows shape under test")
        with _layout() as (parent, root, _outside):
            later = parent / "directory_that_does_not_exist_yet"
            link = root / "dangling_junction"
            with _junction(link, later) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                self.assertFalse(later.exists())
                self.assertFalse(resolves_within_root(link / "worktree", root))
                self.assertFalse(resolves_within_root(link, root))
                later.mkdir()
                self.assertFalse(resolves_within_root(link / "worktree", root))

    def test_a_dangling_symlink_pointing_outside_is_refused(self) -> None:
        with _layout() as (parent, root, _outside):
            later = parent / "directory_that_does_not_exist_yet"
            link = root / "dangling_symlink"
            try:
                os.symlink(later, link, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("no symlink can be created here")
            try:
                self.assertTrue(os.path.lexists(link))
                self.assertFalse(resolves_within_root(link / "worktree", root))
                self.assertFalse(resolves_within_root(link, root))
            finally:
                try:
                    os.unlink(link)
                except OSError:
                    pass

    def test_a_missing_path_without_a_link_is_still_contained(self) -> None:
        with _layout() as (_, root, _outside):
            self.assertTrue(resolves_within_root(root / "a" / "b", root))

    def test_the_existence_test_does_not_follow_links(self) -> None:
        with _layout() as (_, root, _outside):
            calls: list[Path] = []

            def exists(self: Path, *args: object, **kwargs: object) -> bool:
                calls.append(self)
                return False

            with mock.patch.object(Path, "exists", exists):
                self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME / "x", root))
            self.assertEqual([], calls)


def _stat_with_inode_zero(
    real_stat: Callable[..., os.stat_result],
) -> Callable[..., os.stat_result]:
    """An ``os.stat`` stand-in that reports ``st_ino == 0``, as a volume with no file index does."""

    def stat(path: str | os.PathLike[str], *args: object, **kwargs: object) -> os.stat_result:
        status = real_stat(path, *args, **kwargs)
        fields = list(status[:10])
        fields[1] = 0
        return os.stat_result(tuple(fields))

    return stat


class IdentityEdgeTests(unittest.TestCase):
    """Revision04 S63-19 and S63-20: an identity that is not one, and a missing attribute."""

    def test_an_inode_of_zero_is_an_unreadable_identity(self) -> None:
        # The reviewer's G5b: with no file index every directory would "match".
        with _layout() as (_, root, _outside):
            stand_in = _stat_with_inode_zero(os.stat)
            with mock.patch.object(os, "stat", side_effect=stand_in):
                self.assertIsNone(path_containment._identity(root))
                self.assertIsNone(path_containment._identity(root / "missing" / "x"))
                self.assertFalse(resolves_within_root(root / "x", root))
                reason = path_containment._base_refusal_reason(root)
            self.assertIsNotNone(reason)
            assert reason is not None
            self.assertIn("identity", reason)
            self.assertTrue(resolves_within_root(root / "x", root))

    def test_a_real_stat_result_whose_attributes_are_none_is_a_refusal(self) -> None:
        # The reviewer's N6 and N6b: a real os.stat_result built without the field.
        if sys.platform != "win32":
            self.skipTest("the reparse attribute exists only on Windows")
        with _layout() as (_, root, _outside):
            real = os.lstat(root)
            bare = os.stat_result(tuple(real[:10]))
            self.assertIsNone(bare.st_file_attributes)
            with mock.patch.object(os, "lstat", return_value=bare):
                result = path_containment._examine_component(root)
                self.assertIs(path_containment._Component.REFUSE, result.state)
                self.assertIsNotNone(result.reason)
                self.assertIs(False, resolves_within_root(root / "x", root))
                reason = path_containment._base_refusal_reason(root)
            self.assertIsNotNone(reason)

    def test_a_non_integer_attribute_is_a_refusal(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the reparse attribute exists only on Windows")
        with _layout() as (_, root, _outside):
            odd = types.SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_file_attributes="16")
            with mock.patch.object(os, "lstat", return_value=odd):
                self.assertIs(
                    path_containment._Component.REFUSE,
                    path_containment._examine_component(root).state,
                )

    def test_a_real_lstat_result_with_attributes_is_still_read(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the reparse attribute exists only on Windows")
        with _layout() as (_, root, _outside):
            self.assertIs(
                path_containment._Component.PASS, path_containment._examine_component(root).state
            )


@contextmanager
def _substituted_drive(directory: Path) -> Iterator[Path | None]:
    """Map a free drive letter to ``directory`` with ``subst``; None where that cannot be done."""

    if sys.platform != "win32":
        yield None
        return
    letter = next((c for c in "QRSTUVWXYZ" if not os.path.exists(f"{c}:\\")), None)
    if letter is None:
        yield None
        return
    made = (
        subprocess.run(
            ("subst.exe", f"{letter}:", str(directory)),
            check=False,
            capture_output=True,
            timeout=30,
        ).returncode
        == 0
    )
    try:
        yield Path(f"{letter}:\\") if made else None
    finally:
        if made:
            subprocess.run(
                ("subst.exe", f"{letter}:", "/d"), check=False, capture_output=True, timeout=30
            )


class SameDirectorySpellingTests(unittest.TestCase):
    """Revision04 S63-18: a spelling of the root that names it by identity is the root.

    Each of these once failed a string comparison and now passes the identity
    check. None of them admits a path outside the root, which is what is pinned.
    """

    def _assert_outside_is_refused(
        self, spelling: Path, outside: Path, traversal: bool = True
    ) -> None:
        self.assertFalse(resolves_within_root(outside / "victim", spelling))
        self.assertFalse(resolves_within_root(outside, spelling))
        if traversal:
            # A drive root has no parent, so ".." through it stays inside; the
            # drive-letter test passes traversal=False.
            self.assertFalse(
                resolves_within_root(spelling / ".." / outside.name / "victim", spelling)
            )

    def test_a_trailing_dot_or_space_spelling_of_the_root_admits_nothing_outside(self) -> None:
        if sys.platform != "win32":
            self.skipTest("trailing dots and spaces are ignored by Windows only")
        with _layout() as (_, root, outside):
            (outside / "victim").mkdir()
            for suffix in (".", " ", ". ", " ."):
                with self.subTest(suffix=repr(suffix)):
                    spelling = Path(str(root) + suffix)
                    self._assert_outside_is_refused(spelling, outside)
                    self.assertFalse(
                        resolves_within_root(Path(str(outside) + suffix) / "victim", spelling)
                    )

    def test_an_index_allocation_spelling_of_the_root_admits_nothing_outside(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the stream suffix exists on NTFS only")
        with _layout() as (_, root, outside):
            (outside / "victim").mkdir()
            spelling = Path(str(root) + "::$INDEX_ALLOCATION")
            self._assert_outside_is_refused(spelling, outside)
            self.assertFalse(
                resolves_within_root(
                    Path(str(outside) + "::$INDEX_ALLOCATION") / "victim", spelling
                )
            )

    def test_a_device_prefix_spelling_of_the_root_admits_nothing_outside(self) -> None:
        if sys.platform != "win32":
            self.skipTest("the device prefix exists on Windows only")
        with _layout() as (_, root, outside):
            (outside / "victim").mkdir()
            spelling = Path("\\\\.\\" + str(root))
            self._assert_outside_is_refused(spelling, outside)
            self.assertFalse(
                resolves_within_root(Path("\\\\.\\" + str(outside)) / "victim", spelling)
            )

    def test_a_substituted_drive_for_the_root_admits_nothing_outside(self) -> None:
        if sys.platform != "win32":
            self.skipTest("subst drives exist on Windows only")
        with _layout() as (_, root, outside):
            (outside / "victim").mkdir()
            with _substituted_drive(root) as drive:
                if drive is None:
                    self.skipTest("no drive letter can be substituted here")
                assert drive is not None
                self._assert_outside_is_refused(drive, outside, traversal=False)
                with _substituted_drive(outside) as other:
                    if other is None:
                        self.skipTest("no second drive letter can be substituted here")
                    assert other is not None
                    self.assertFalse(resolves_within_root(other / "victim", drive))
                    self.assertFalse(resolves_within_root(other / "victim", root))
                    self.assertFalse(resolves_within_root(other, drive))
                # The root is still the root through its own drive letter.
                self.assertTrue(resolves_within_root(drive / _LONG_CHILD_NAME, drive))
                self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME, drive))


class StrictTargetWalkTests(unittest.TestCase):
    """Revision05: the target side asks the file system, component by component."""

    def test_a_dangling_junction_through_an_in_root_junction_is_refused(self) -> None:
        # The reviewer's H1, H1b, H1d: J1 -> root/sub/notyet, and root/sub -> outside.
        if sys.platform != "win32":
            self.skipTest("a junction is the Windows shape under test")
        with _layout() as (_, root, outside):
            sub = root / "sub"
            link = root / "J1"
            with _junction(sub, outside) as made_sub:
                if not made_sub:
                    self.skipTest("no junction can be created here")
                with _junction(link, sub / "notyet") as made:
                    if not made:
                        self.skipTest("no junction can be created here")
                    self.assertFalse(resolves_within_root(link / "wt", root))
                    self.assertFalse(resolves_within_root(link, root))
                    self.assertFalse(resolves_within_root(link / "a" / "b" / "c", root))
                    (outside / "notyet").mkdir()
                    self.assertFalse(resolves_within_root(link / "wt", root))

    def test_a_chain_of_dangling_junctions_is_refused(self) -> None:
        # The reviewer's H1c: J3 -> root/J2/notyet, J2 -> parent/later (missing).
        if sys.platform != "win32":
            self.skipTest("a junction is the Windows shape under test")
        with _layout() as (parent, root, _outside):
            with _junction(root / "J2", parent / "later") as made2:
                if not made2:
                    self.skipTest("no junction can be created here")
                with _junction(root / "J3", root / "J2" / "notyet") as made3:
                    if not made3:
                        self.skipTest("no junction can be created here")
                    self.assertFalse(resolves_within_root(root / "J3" / "wt", root))
                    self.assertFalse(resolves_within_root(root / "J3", root))

    def test_a_junction_inside_the_root_pointing_inside_the_root_is_refused(self) -> None:
        # S63-23: N1, N1b and f1. P0 refuses every reparse point.
        if sys.platform != "win32":
            self.skipTest("a junction is the Windows shape under test")
        with _layout() as (_, root, _outside):
            link = root / "inner_link"
            with _junction(link, root / _LONG_CHILD_NAME) as made:
                if not made:
                    self.skipTest("no junction can be created here")
                self.assertFalse(resolves_within_root(link, root))
                self.assertFalse(resolves_within_root(link / "leaf", root))
                self.assertFalse(resolves_within_root(link / "a" / "b", root))
                self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME / "leaf", root))

    def test_a_symlink_inside_the_root_pointing_inside_the_root_is_refused(self) -> None:
        with _layout() as (_, root, _outside):
            link = root / "inner_symlink"
            try:
                os.symlink(root / _LONG_CHILD_NAME, link, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("no symlink can be created here")
            try:
                self.assertFalse(resolves_within_root(link, root))
                self.assertFalse(resolves_within_root(link / "leaf", root))
            finally:
                os.unlink(link)

    def test_a_component_that_fails_with_a_reparse_error_is_refused(self) -> None:
        # The reviewer's f2: lstat under a third-party reparse point gives error 1920.
        with _layout() as (_, root, _outside):
            real_lstat = os.lstat
            bad = root / "unreadable"

            def lstat(path: str | os.PathLike[str]) -> os.stat_result:
                if Path(path) == bad:
                    raise OSError(1920, "the file cannot be accessed by the system")
                return real_lstat(path)

            with mock.patch.object(os, "lstat", side_effect=lstat):
                self.assertFalse(resolves_within_root(bad / "leaf", root))
                self.assertFalse(resolves_within_root(bad, root))

    def test_an_access_denied_component_before_a_junction_is_refused(self) -> None:
        # The reviewer's P1: only "not found" means missing.
        with _layout() as (_, root, _outside):
            real_lstat = os.lstat
            denied = root / "D"

            def lstat(path: str | os.PathLike[str]) -> os.stat_result:
                if Path(path) == denied:
                    raise PermissionError(13, "denied")
                if denied in Path(path).parents:
                    raise FileNotFoundError(2, "not found")
                return real_lstat(path)

            with mock.patch.object(os, "lstat", side_effect=lstat):
                self.assertFalse(resolves_within_root(denied / "J" / "wt", root))

    def test_only_not_found_and_not_a_directory_mean_missing(self) -> None:
        with _layout() as (_, root, _outside):
            real_lstat = os.lstat
            for error in (FileNotFoundError(2, "x"), NotADirectoryError(20, "x")):
                missing = root / "gone"

                def lstat(
                    path: str | os.PathLike[str], raised: OSError = error, gone: Path = missing
                ) -> os.stat_result:
                    if Path(path) == gone:
                        raise raised
                    return real_lstat(path)

                with mock.patch.object(os, "lstat", side_effect=lstat):
                    self.assertTrue(resolves_within_root(missing / "x", root))

    def test_a_file_with_a_remainder_below_it_is_not_an_error(self) -> None:
        with _layout() as (_, root, _outside):
            (root / "file.txt").write_text("x", encoding="utf-8")
            self.assertTrue(resolves_within_root(root / "file.txt" / "x", root))

    def test_the_nearest_existing_component_is_resolved_strictly(self) -> None:
        with _layout() as (_, root, _outside):
            real_resolve = Path.resolve
            seen: list[bool] = []

            def resolve(self: Path, strict: bool = False) -> Path:
                if self != root:
                    seen.append(strict)
                return real_resolve(self, strict=strict)

            with mock.patch.object(Path, "resolve", resolve):
                self.assertTrue(resolves_within_root(root / _LONG_CHILD_NAME / "x", root))
            self.assertEqual([True], seen)

    def test_a_failed_strict_resolution_is_a_refusal(self) -> None:
        with _layout() as (_, root, _outside):
            real_resolve = Path.resolve

            def resolve(self: Path, strict: bool = False) -> Path:
                if strict:
                    raise FileNotFoundError(2, "dangling")
                return real_resolve(self, strict=strict)

            with mock.patch.object(Path, "resolve", resolve):
                self.assertIs(False, resolves_within_root(root / "x", root))

    def test_any_exception_from_a_file_system_call_is_a_refusal(self) -> None:
        with _layout() as (_, root, _outside):
            real_resolve = Path.resolve

            def resolve(self: Path, strict: bool = False) -> Path:
                if strict:
                    raise RuntimeError("symlink loop")
                return real_resolve(self, strict=strict)

            with mock.patch.object(Path, "resolve", resolve):
                self.assertIs(False, resolves_within_root(root / "x", root))

    def test_a_nul_in_the_target_is_a_refusal_and_does_not_raise(self) -> None:
        # The reviewer's Z1.
        with _layout() as (_, root, _outside):
            self.assertIs(False, resolves_within_root(Path(str(root) + os.sep + "a\x00b"), root))

    def test_a_literal_parent_component_is_a_refusal(self) -> None:
        # The reviewer's D1, D2, Z6: no ".." and no "." is ever walked.
        with _layout() as (_, root, outside):
            self.assertFalse(resolves_within_root(root / ".." / outside.name, root))
            self.assertFalse(resolves_within_root(root / "sub" / ".." / "x", root))
            if sys.platform == "win32":
                verbatim = Path("\\\\?\\" + str(root) + "\\..\\" + outside.name + "\\made")
                self.assertIn("..", verbatim.parts)
                self.assertIs(False, resolves_within_root(verbatim, root))

    def test_a_stream_separator_after_the_drive_is_a_refusal(self) -> None:
        if sys.platform != "win32":
            self.skipTest("streams exist on NTFS only")
        with _layout() as (_, root, _outside):
            self.assertIs(False, resolves_within_root(Path(str(root) + "\\x:stream"), root))
            self.assertIs(
                False, resolves_within_root(Path(str(root) + "::$INDEX_ALLOCATION") / "x", root)
            )

    def test_the_old_target_side_calls_are_gone(self) -> None:
        source = Path(path_containment.__file__).read_text(encoding="utf-8")
        self.assertNotIn("lexists", source)
        self.assertNotIn(".resolve()", source.split("def _resolve_target")[1])


if __name__ == "__main__":
    unittest.main()
