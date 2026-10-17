"""Pinned Git source tests for the test-consumer inventory adapter."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from library.local_orchestration.test_dependency_inventory import (
    DeclaredTestCommand,
    InventoryStatus,
)
from library.local_orchestration.test_dependency_source_adapter import (
    GitPinnedTestDependencyInventory,
    GitTestDependencySourceAdapter,
    TestDependencySourceError as SourceError,
    TestDependencySourceFailure as SourceFailure,
)


class GitTestDependencySourceAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.repository_root = Path(self._temporary_directory.name) / "repo"
        self.repository_root.mkdir()
        self._git("init", "--quiet")
        self._git("config", "user.name", "Test Owner")
        self._git("config", "user.email", "test@example.invalid")

    def test_reads_pinned_tree_and_traces_command_through_imports(self) -> None:
        self._write("tests/test_helper.py", "def helper() -> None: pass\n")
        self._write(
            "tests/test_wrapper.py",
            "from tests.test_helper import helper\n",
        )
        self._write("tests/test_consumer.py", "from tests import test_wrapper\n")
        pinned_commit = self._commit("initial")

        result = GitTestDependencySourceAdapter().read_inventory(
            self.repository_root,
            pinned_commit,
            "tests/test_helper.py",
            declared_commands=(
                DeclaredTestCommand(
                    "ci:pytest-consumer",
                    ("python", "-m", "pytest", "tests/test_consumer.py"),
                ),
            ),
        )

        self.assertIsInstance(result, GitPinnedTestDependencyInventory)
        self.assertEqual(pinned_commit, result.commit_sha)
        self.assertEqual(3, len(result.source_refs))
        self.assertEqual(InventoryStatus.COMPLETE, result.inventory.status)
        self.assertEqual(
            ("tests/test_wrapper.py",),
            result.inventory.direct_consumers,
        )
        self.assertEqual(
            ("ci:pytest-consumer", "tests/test_consumer.py"),
            result.inventory.transitive_consumers,
        )
        self.assertFalse(result.inventory.retirement_authorized)

    def test_pinned_result_does_not_drift_with_worktree_or_new_head(self) -> None:
        self._write("tests/test_helper.py", "def helper() -> None: pass\n")
        self._write("tests/test_wrapper.py", "from tests.test_helper import helper\n")
        self._write("tests/test_consumer.py", "from tests import test_wrapper\n")
        old_commit = self._commit("with-consumer")
        adapter = GitTestDependencySourceAdapter()

        self._write("tests/test_wrapper.py", "def wrapper() -> None: pass\n")
        untracked = self.repository_root / "tests" / "test_untracked.py"
        untracked.write_text("from tests.test_helper import helper\n", encoding="utf-8")
        old_after_worktree_change = adapter.read_inventory(
            self.repository_root, old_commit, "tests/test_helper.py"
        )
        self.assertEqual(("tests/test_wrapper.py",), old_after_worktree_change.inventory.direct_consumers)

        self._git("add", "tests/test_wrapper.py")
        self._git("commit", "--quiet", "-m", "remove-helper-dependency")
        new_commit = self._git_text("rev-parse", "HEAD")
        new_inventory = adapter.read_inventory(
            self.repository_root, new_commit, "tests/test_helper.py"
        )
        old_after_head_change = adapter.read_inventory(
            self.repository_root, old_commit, "tests/test_helper.py"
        )

        self.assertNotEqual(old_commit, new_commit)
        self.assertEqual((), new_inventory.inventory.direct_edges)
        self.assertEqual((), new_inventory.inventory.transitive_edges)
        self.assertFalse(new_inventory.inventory.retirement_authorized)
        self.assertEqual(("tests/test_wrapper.py",), old_after_head_change.inventory.direct_consumers)

    def test_git_replace_ref_cannot_change_pinned_commit_content(self) -> None:
        self._write("tests/test_helper.py", "def helper() -> None: pass\n")
        self._write("tests/test_consumer.py", "from tests.test_helper import helper\n")
        pinned_commit = self._commit("with-consumer")

        self._write("tests/test_consumer.py", "def test_independent() -> None: pass\n")
        replacement_commit = self._commit("without-consumer")
        self._git("replace", pinned_commit, replacement_commit)

        result = GitTestDependencySourceAdapter().read_inventory(
            self.repository_root, pinned_commit, "tests/test_helper.py"
        )

        self.assertEqual(pinned_commit, result.commit_sha)
        self.assertEqual(("tests/test_consumer.py",), result.inventory.direct_consumers)

    def test_git_replace_blob_cannot_change_pinned_source_content(self) -> None:
        self._write("tests/test_helper.py", "def helper() -> None: pass\n")
        self._write("tests/test_consumer.py", "from tests.test_helper import helper\n")
        pinned_commit = self._commit("with-consumer")
        original_blob = self._git_text(
            "rev-parse", f"{pinned_commit}:tests/test_consumer.py"
        )

        self._write("tests/test_consumer.py", "def test_independent() -> None: pass\n")
        replacement_commit = self._commit("without-consumer")
        replacement_blob = self._git_text(
            "rev-parse", f"{replacement_commit}:tests/test_consumer.py"
        )
        self._git("replace", original_blob, replacement_blob)

        result = GitTestDependencySourceAdapter().read_inventory(
            self.repository_root, pinned_commit, "tests/test_helper.py"
        )

        self.assertEqual(pinned_commit, result.commit_sha)
        self.assertEqual(("tests/test_consumer.py",), result.inventory.direct_consumers)

    def test_valid_empty_inventory_keeps_retirement_unauthorized(self) -> None:
        self._write("tests/test_independent.py", "def test_independent() -> None: pass\n")
        pinned_commit = self._commit("independent")

        result = GitTestDependencySourceAdapter().read_inventory(
            self.repository_root, pinned_commit, "tests/test_helper.py"
        )

        self.assertEqual(InventoryStatus.COMPLETE, result.inventory.status)
        self.assertEqual((), result.inventory.direct_edges)
        self.assertEqual((), result.inventory.transitive_edges)
        self.assertFalse(result.inventory.retirement_authorized)

    def test_rejects_abbreviated_and_non_commit_object_ids(self) -> None:
        self._write("tests/test_helper.py", "")
        pinned_commit = self._commit("one")
        tree_id = self._git_text("rev-parse", f"{pinned_commit}^{{tree}}")

        for invalid_commit in (pinned_commit[:8], tree_id):
            with self.subTest(invalid_commit=invalid_commit):
                with self.assertRaises(SourceError) as raised:
                    GitTestDependencySourceAdapter().read_inventory(
                        self.repository_root, invalid_commit, "tests/test_helper.py"
                    )
                self.assertEqual(
                    SourceFailure.INVALID_COMMIT_SHA
                    if invalid_commit == pinned_commit[:8]
                    else SourceFailure.COMMIT_NOT_FOUND_OR_NOT_COMMIT,
                    raised.exception.reason,
                )

    def test_rejects_invalid_repository_roots(self) -> None:
        adapter = GitTestDependencySourceAdapter()

        with self.assertRaises(SourceError) as missing_root:
            adapter.read_inventory(
                self.repository_root / "missing", "0" * 40, "tests/test_helper.py"
            )
        self.assertEqual(
            SourceFailure.INVALID_REPOSITORY_ROOT,
            missing_root.exception.reason,
        )

        non_repository = Path(self._temporary_directory.name) / "not-a-repository"
        non_repository.mkdir()
        with self.assertRaises(SourceError) as non_repository_error:
            adapter.read_inventory(non_repository, "0" * 40, "tests/test_helper.py")
        self.assertEqual(
            SourceFailure.INVALID_REPOSITORY_ROOT,
            non_repository_error.exception.reason,
        )

    def test_enforces_python_blob_count_and_size_limits(self) -> None:
        self._write("tests/test_a.py", "x = 1\n")
        self._write("tests/test_b.py", "x = 2\n")
        pinned_commit = self._commit("two-python-files")

        with self.assertRaises(SourceError) as too_many:
            GitTestDependencySourceAdapter(max_python_files=1).read_inventory(
                self.repository_root, pinned_commit, "tests/test_helper.py"
            )
        self.assertEqual(SourceFailure.LIMIT_EXCEEDED, too_many.exception.reason)

        with self.assertRaises(SourceError) as too_large:
            GitTestDependencySourceAdapter(max_blob_bytes=3).read_inventory(
                self.repository_root, pinned_commit, "tests/test_helper.py"
            )
        self.assertEqual(SourceFailure.LIMIT_EXCEEDED, too_large.exception.reason)

    def test_rejects_unbounded_total_source_bytes(self) -> None:
        self._write("tests/test_a.py", "x = 1\n")
        self._write("tests/test_b.py", "y = 2\n")
        pinned_commit = self._commit("two-python-files")

        with self.assertRaises(SourceError) as raised:
            GitTestDependencySourceAdapter(max_total_source_bytes=8).read_inventory(
                self.repository_root, pinned_commit, "tests/test_helper.py"
            )
        self.assertEqual(SourceFailure.LIMIT_EXCEEDED, raised.exception.reason)

    def test_rejects_invalid_utf8_python_blob(self) -> None:
        self._write_bytes("tests/test_invalid.py", b"value = '\xff'\n")
        pinned_commit = self._commit("invalid-utf8")

        with self.assertRaises(SourceError) as raised:
            GitTestDependencySourceAdapter().read_inventory(
                self.repository_root, pinned_commit, "tests/test_invalid.py"
            )
        self.assertEqual(SourceFailure.INVALID_UTF8, raised.exception.reason)

    def test_rejects_python_symlink_entry(self) -> None:
        self._write("tests/test_regular.py", "")
        self._commit("regular")
        link_blob = self._git(
            "hash-object", "-w", "--stdin", input_bytes=b"target.py"
        ).decode("ascii").strip()
        self._git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"120000,{link_blob},tests/test_link.py",
        )
        pinned_commit = self._commit("symlink")

        with self.assertRaises(SourceError) as raised:
            GitTestDependencySourceAdapter().read_inventory(
                self.repository_root, pinned_commit, "tests/test_regular.py"
            )
        self.assertEqual(
            SourceFailure.UNSUPPORTED_TREE_ENTRY,
            raised.exception.reason,
        )

    def test_rejects_python_gitlink_entry(self) -> None:
        self._write("tests/test_regular.py", "")
        linked_commit = self._commit("regular")
        self._git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{linked_commit},vendor/test_dependency.py",
        )
        pinned_commit = self._commit("gitlink")

        with self.assertRaises(SourceError) as raised:
            GitTestDependencySourceAdapter().read_inventory(
                self.repository_root, pinned_commit, "tests/test_regular.py"
            )
        self.assertEqual(
            SourceFailure.UNSUPPORTED_TREE_ENTRY,
            raised.exception.reason,
        )

    def test_rejects_non_python_symlink_entry(self) -> None:
        self._write("tests/test_regular.py", "")
        self._commit("regular")
        link_blob = self._git(
            "hash-object", "-w", "--stdin", input_bytes=b"target"
        ).decode("ascii").strip()
        self._git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"120000,{link_blob},vendor-link",
        )
        pinned_commit = self._commit("non-python-symlink")

        with self.assertRaises(SourceError) as raised:
            GitTestDependencySourceAdapter().read_inventory(
                self.repository_root, pinned_commit, "tests/test_regular.py"
            )
        self.assertEqual(
            SourceFailure.UNSUPPORTED_TREE_ENTRY,
            raised.exception.reason,
        )

    def test_rejects_non_python_gitlink_entry(self) -> None:
        self._write("tests/test_regular.py", "")
        linked_commit = self._commit("regular")
        self._git(
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{linked_commit},vendor",
        )
        pinned_commit = self._commit("non-python-gitlink")

        with self.assertRaises(SourceError) as raised:
            GitTestDependencySourceAdapter().read_inventory(
                self.repository_root, pinned_commit, "tests/test_regular.py"
            )
        self.assertEqual(
            SourceFailure.UNSUPPORTED_TREE_ENTRY,
            raised.exception.reason,
        )

    def test_does_not_execute_python_blob_content(self) -> None:
        marker = Path(self._temporary_directory.name) / "executed.txt"
        self._write(
            "tests/test_helper.py",
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n",
        )
        pinned_commit = self._commit("untrusted-source")

        GitTestDependencySourceAdapter().read_inventory(
            self.repository_root, pinned_commit, "tests/test_helper.py"
        )

        self.assertFalse(marker.exists())

    def _write(self, relative_path: str, text: str) -> None:
        self._write_bytes(relative_path, text.encode("utf-8"))

    def _write_bytes(self, relative_path: str, content: bytes) -> None:
        path = self.repository_root.joinpath(*relative_path.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self._git("add", "--", relative_path)

    def _commit(self, message: str) -> str:
        self._git("commit", "--quiet", "-m", message)
        return self._git_text("rev-parse", "HEAD")

    def _git_text(self, *arguments: str) -> str:
        return self._git(*arguments).decode("utf-8").strip()

    def _git(self, *arguments: str, input_bytes: bytes | None = None) -> bytes:
        completed = subprocess.run(
            ("git", "-C", str(self.repository_root), *arguments),
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=10,
        )
        return completed.stdout


if __name__ == "__main__":
    unittest.main()
