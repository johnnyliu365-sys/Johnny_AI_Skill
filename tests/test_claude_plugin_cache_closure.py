"""TDD cells for the installed Claude plugin cache closure."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.claude_plugin_cache_closure import (
    InstallClosureStatus,
    verify_installed_plugin_cache,
)
from library.local_orchestration.publication_repository_closure import (
    PublicationCommit,
    PublicationPayload,
)



def _git(root: Path, *arguments: str, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return completed.stdout.strip()


def _initialise(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Closure Test")
    _git(root, "config", "user.email", "closure@example.invalid")


def _parentless_commit(
    root: Path, entries: dict[str, bytes]
) -> tuple[PublicationCommit, PublicationPayload]:
    for relative, content in entries.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    index = root / "closure-test-index"
    environment = dict(os.environ)
    environment["GIT_INDEX_FILE"] = str(index)
    _git(root, "read-tree", "--empty", env=environment)
    for relative in entries:
        _git(root, "add", "--", relative, env=environment)
    tree = _git(root, "write-tree", env=environment)
    commit = _git(
        root,
        "commit-tree",
        tree,
        "-m",
        "payload closure",
        env={
            **environment,
            "GIT_AUTHOR_NAME": "Closure Test",
            "GIT_AUTHOR_EMAIL": "closure@example.invalid",
            "GIT_COMMITTER_NAME": "Closure Test",
            "GIT_COMMITTER_EMAIL": "closure@example.invalid",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
        },
    )
    typed_commit = PublicationCommit(value=commit)
    blob_ids = tuple(
        (relative, _git(root, "rev-parse", f"{commit}:{relative}"))
        for relative in sorted(entries)
    )
    return typed_commit, PublicationPayload(
        paths=tuple(sorted(entries)),
        blob_ids=blob_ids,
    )


def _cache_fixture(root: Path) -> tuple[PublicationCommit, PublicationPayload]:
    _initialise(root)
    commit, payload = _parentless_commit(root, {"payload.txt": b"payload\n"})
    _git(root, "update-ref", "refs/heads/main", commit.value)
    _git(root, "clean", "-fdx")
    _git(root, "checkout", "-q", "--detach", commit.value)
    _git(root, "update-ref", "-d", "refs/heads/main")
    return commit, payload


class InstalledPluginCacheClosureTests(unittest.TestCase):
    def test_c4_detached_payload_only_cache_is_verified(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _cache_fixture(root)
            result = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(result.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(result.reachable_refs, ())
            self.assertEqual(result.reachable_commits, (commit,))

    def test_c4_reachable_development_tree_turns_valid_cache_red(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _cache_fixture(root)
            before = _git(root, "for-each-ref", "--format=%(refname)=%(objectname)")
            development, _ = _parentless_commit(
                root,
                {"payload.txt": b"payload\n", "tests/development.py": b"development\n"},
            )
            _git(root, "update-ref", "refs/heads/main", development.value)
            rejected = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(rejected.status, InstallClosureStatus.SENTINEL_REACHABLE)
            _git(root, "update-ref", "-d", "refs/heads/main")
            restored = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(
                _git(root, "for-each-ref", "--format=%(refname)=%(objectname)"),
                before,
            )

    def test_c4_every_reachable_ref_is_checked_for_history_and_tree(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _cache_fixture(root)
            _git(root, "update-ref", "refs/heads/main", commit.value)
            rejected = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(rejected.status, InstallClosureStatus.VERIFIED)

            _git(root, "update-ref", "refs/heads/development", commit.value)
            invalid = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(invalid.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID)

    def test_c5_invalid_head_and_expected_pin_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _cache_fixture(root)
            wrong = PublicationCommit(value="f" * 40)
            mismatch = verify_installed_plugin_cache(root, payload, expected_head=wrong)
            self.assertEqual(mismatch.status, InstallClosureStatus.PLUGIN_CHECKOUT_MISMATCH)

            (root / ".git" / "HEAD").write_text(
                "ref: refs/heads/main\n", encoding="ascii"
            )
            invalid_ref = verify_installed_plugin_cache(root, payload)
            self.assertEqual(invalid_ref.status, InstallClosureStatus.PLUGIN_CHECKOUT_MISMATCH)
            self.assertEqual(commit, PublicationCommit.model_validate(commit))

    def test_l5_missing_cli_cache_data_is_named_and_not_verified(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            _initialise(root)
            payload = PublicationPayload(
                paths=("payload.txt",),
                blob_ids=(("payload.txt", "0" * 40),),
            )
            result = verify_installed_plugin_cache(root, payload)
            self.assertEqual(result.status, InstallClosureStatus.PLUGIN_CHECKOUT_MISMATCH)


if __name__ == "__main__":
    unittest.main()
