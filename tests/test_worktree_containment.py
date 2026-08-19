"""Governance 02: agent worktrees live under the repository root, or refuse."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.worktree_containment import (
    WORKTREE_DIRECTORY_NAME,
    WorktreeContainmentFailure,
    WorktreeContainmentStatus,
    registered_worktree_paths,
    sanctioned_worktree_path,
    sanctioned_worktree_root,
    verify_worktree_contained,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _make_junction(link: Path, target: Path) -> bool:
    completed = subprocess.run(
        ("cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)),
        check=False,
        capture_output=True,
        shell=False,
        timeout=30,
    )
    return completed.returncode == 0


class SanctionedPathTests(unittest.TestCase):
    def test_r1_the_sanctioned_root_is_the_ignored_dot_directory(self) -> None:
        self.assertEqual(WORKTREE_DIRECTORY_NAME, ".worktrees")
        root = Path("C:/repo") if os.name == "nt" else Path("/repo")
        self.assertEqual(sanctioned_worktree_root(root), root / ".worktrees")
        self.assertEqual(
            sanctioned_worktree_path(root, "l9"), root / ".worktrees" / "l9"
        )

    def test_r1_the_repository_ignore_rule_is_committed(self) -> None:
        body = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/.worktrees/", body)

    def test_a_ticket_id_may_not_escape_its_segment(self) -> None:
        root = Path("C:/repo") if os.name == "nt" else Path("/repo")
        backslash_segment = "a" + chr(92) + "b"
        for hostile in ("../elsewhere", "a/b", backslash_segment, "", ".", ".."):
            with self.subTest(hostile=hostile):
                with self.assertRaises(ValueError):
                    sanctioned_worktree_path(root, hostile)


class ContainmentVerificationTests(unittest.TestCase):
    def test_r3_a_sibling_worktree_outside_the_root_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            repository = base / "repo"
            (repository / ".worktrees").mkdir(parents=True)
            sibling = base / "repo-l9"
            sibling.mkdir()
            status, failure = verify_worktree_contained(repository, sibling)
            self.assertIs(status, WorktreeContainmentStatus.REFUSED)
            self.assertIs(
                failure, WorktreeContainmentFailure.OUTSIDE_REPOSITORY_ROOT
            )

    def test_r3_the_sanctioned_path_is_admitted(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve() / "repo"
            worktree = sanctioned_worktree_path(repository, "l9")
            worktree.mkdir(parents=True)
            status, failure = verify_worktree_contained(repository, worktree)
            self.assertIs(status, WorktreeContainmentStatus.CONTAINED)
            self.assertIsNone(failure)

    def test_r3_inside_the_root_but_outside_the_sanctioned_directory_refuses(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve() / "repo"
            stray = repository / "workspaces" / "l9"
            stray.mkdir(parents=True)
            status, failure = verify_worktree_contained(repository, stray)
            self.assertIs(status, WorktreeContainmentStatus.REFUSED)
            self.assertIs(
                failure, WorktreeContainmentFailure.NOT_THE_SANCTIONED_DIRECTORY
            )

    def test_an_absent_repository_root_refuses(self) -> None:
        with TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve() / "missing"
            status, failure = verify_worktree_contained(
                repository, repository / ".worktrees" / "l9"
            )
            self.assertIs(status, WorktreeContainmentStatus.REFUSED)
            self.assertIs(
                failure, WorktreeContainmentFailure.REPOSITORY_ROOT_INVALID
            )


class ReparseEvasionTests(unittest.TestCase):
    """R4: a redirected path must not buy admission."""

    def test_r4_a_worktree_reached_through_a_junction_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            repository = base / "repo"
            (repository / WORKTREE_DIRECTORY_NAME).mkdir(parents=True)
            outside = base / "outside"
            outside.mkdir()
            link = repository / WORKTREE_DIRECTORY_NAME / "l9"
            if not _make_junction(link, outside):
                self.skipTest("junction creation unavailable on this host")
            status, failure = verify_worktree_contained(repository, link)
            self.assertIs(status, WorktreeContainmentStatus.REFUSED)
            self.assertIs(
                failure, WorktreeContainmentFailure.OUTSIDE_REPOSITORY_ROOT
            )

    def test_r4_a_junctioned_repository_root_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            real = base / "real"
            (real / WORKTREE_DIRECTORY_NAME / "l9").mkdir(parents=True)
            link = base / "linked"
            if not _make_junction(link, real):
                self.skipTest("junction creation unavailable on this host")
            status, failure = verify_worktree_contained(
                link, link / WORKTREE_DIRECTORY_NAME / "l9"
            )
            self.assertIs(status, WorktreeContainmentStatus.REFUSED)
            self.assertIs(
                failure, WorktreeContainmentFailure.OUTSIDE_REPOSITORY_ROOT
            )


class RegisteredWorktreeReadbackTests(unittest.TestCase):
    def test_r5_this_repository_registers_only_contained_worktrees(self) -> None:
        registered = registered_worktree_paths(_REPO_ROOT)
        self.assertTrue(registered, "git worktree readback returned nothing")
        main_checkout = registered[0].resolve()
        for path in registered[1:]:
            with self.subTest(path=str(path)):
                status, failure = verify_worktree_contained(main_checkout, path)
                self.assertIs(
                    status,
                    WorktreeContainmentStatus.CONTAINED,
                    f"{path} is not repo-contained: {failure}",
                )


if __name__ == "__main__":
    unittest.main()
