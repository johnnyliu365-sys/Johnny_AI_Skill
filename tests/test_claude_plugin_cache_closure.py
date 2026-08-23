"""TDD cells for the installed Claude plugin cache closure."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from library.local_orchestration import claude_plugin_cache_closure as cache_module
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


def _normal_clone_fixture(root: Path) -> tuple[PublicationCommit, PublicationPayload]:
    return _normal_clone_fixture_with_entries(root, {"payload.txt": b"payload\n"})


def _normal_clone_fixture_with_entries(
    root: Path, entries: dict[str, bytes]
) -> tuple[PublicationCommit, PublicationPayload]:
    _initialise(root)
    commit, payload = _parentless_commit(root, entries)
    _git(root, "config", "core.quotePath", "true")
    _git(root, "update-ref", "refs/heads/main", commit.value)
    _git(root, "update-ref", "refs/remotes/origin/main", commit.value)
    _git(root, "update-ref", "refs/tags/plugin-v1.2.3", commit.value)
    _git(root, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(root, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    return commit, payload


def _normal_clone_unicode_fixture(
    root: Path,
) -> tuple[PublicationCommit, PublicationPayload]:
    return _normal_clone_fixture_with_entries(
        root,
        {
            "library/功能集群/規則.py": b"payload\n",
            "payload.txt": b"payload\n",
        },
    )


def _unicode_cache_fixture(
    root: Path,
) -> tuple[PublicationCommit, PublicationPayload]:
    _initialise(root)
    commit, payload = _parentless_commit(
        root,
        {"library/功能集群/規則.py": b"payload\n"},
    )
    _git(root, "update-ref", "refs/heads/main", commit.value)
    _git(root, "clean", "-fdx")
    _git(root, "checkout", "-q", "--detach", commit.value)
    _git(root, "update-ref", "-d", "refs/heads/main")
    return commit, payload


class InstalledPluginCacheClosureTests(unittest.TestCase):
    def test_t13_1_normal_clone_unicode_payload_path_is_verified(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_unicode_fixture(root)
            result = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(result.status, InstallClosureStatus.VERIFIED)

    def test_t13_2_lossless_unicode_payload_keeps_exact_cache_evidence(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_unicode_fixture(root)
            result = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(result.status, InstallClosureStatus.VERIFIED)
            self.assertIsNone(result.difference)
            self.assertEqual(
                result.reachable_refs,
                (
                    "refs/heads/main",
                    "refs/remotes/origin/HEAD",
                    "refs/remotes/origin/main",
                    "refs/tags/plugin-v1.2.3",
                ),
            )
            self.assertEqual(result.reachable_commits, (commit,))

    def test_t13_3_malformed_tree_bytes_are_fail_closed(self) -> None:
        malformed = (
            ("invalid UTF-8", b"library/\xff.py\0"),
            ("missing terminal NUL", b"payload.txt"),
            ("empty entry", b"payload.txt\0\0"),
            ("absolute path", b"/payload.txt\0"),
            ("backslash", b"payload\\file.txt\0"),
            ("dot component", b"payload/./file.txt\0"),
            ("empty component", b"payload//file.txt\0"),
            ("traversal", b"payload/../file.txt\0"),
        )
        for label, listing in malformed:
            with self.subTest(case=label), TemporaryDirectory() as temporary:
                root = Path(temporary)
                commit, payload = _cache_fixture(root)
                original_git_bytes = cache_module._git_bytes

                def malformed_listing(
                    candidate_root: Path, *arguments: str
                ) -> bytes:
                    if arguments == (
                        "ls-tree",
                        "-r",
                        "-z",
                        "--name-only",
                        commit.value,
                    ):
                        return listing
                    return original_git_bytes(candidate_root, *arguments)

                with patch.object(
                    cache_module, "_git_bytes", side_effect=malformed_listing
                ):
                    result = verify_installed_plugin_cache(
                        root, payload, expected_head=commit
                    )
                self.assertEqual(
                    result.status, InstallClosureStatus.INSTALLED_TREE_MISMATCH
                )

    def test_t13_4_unicode_sentinel_remains_reachable(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture_with_entries(
                root,
                {
                    "payload.txt": b"payload\n",
                    "tests/功能.py": b"development\n",
                },
            )
            result = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(result.status, InstallClosureStatus.SENTINEL_REACHABLE)

    def test_t13_5_reachable_unicode_development_ref_restores_to_verified(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _unicode_cache_fixture(root)
            before = _git(root, "for-each-ref", "--format=%(refname)=%(objectname)")
            initial = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(initial.status, InstallClosureStatus.VERIFIED)

            development, _ = _parentless_commit(
                root,
                {
                    "library/功能集群/規則.py": b"payload\n",
                    "modules/審閱.py": b"development\n",
                },
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

    def test_s1_normal_clone_remote_head_is_verified(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture(root)
            result = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(result.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(
                result.reachable_refs,
                (
                    "refs/heads/main",
                    "refs/remotes/origin/HEAD",
                    "refs/remotes/origin/main",
                    "refs/tags/plugin-v1.2.3",
                ),
            )
            self.assertEqual(result.reachable_commits, (commit,))

    def test_s2_remote_head_requires_present_target_and_checked_out_root(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture(root)
            before = _git(
                root,
                "for-each-ref",
                "--format=%(refname)=%(objectname)",
            )
            _git(root, "update-ref", "-d", "refs/remotes/origin/main")
            missing = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(missing.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID)
            _git(root, "update-ref", "refs/remotes/origin/main", commit.value)
            restored = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)

            tree = _git(root, "rev-parse", f"{commit.value}^{{tree}}")
            other = PublicationCommit(
                value=_git(root, "commit-tree", tree, "-m", "same tree, different root")
            )
            _git(root, "update-ref", "refs/remotes/origin/main", other.value)
            different_root = verify_installed_plugin_cache(
                root, payload, expected_head=commit
            )
            self.assertEqual(
                different_root.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID
            )
            _git(root, "update-ref", "refs/remotes/origin/main", commit.value)
            restored = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(
                _git(
                    root,
                    "for-each-ref",
                    "--format=%(refname)=%(objectname)",
                ),
                before,
            )

    def test_s3_symbolic_head_grammar_is_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture(root)
            invalid_targets = (
                "refs/tags/plugin-v1.2.3",
                "refs/remotes/origin/plugin-v1.2.3",
                "refs/remotes/upstream/main",
            )
            for target in invalid_targets:
                with self.subTest(target=target):
                    _git(
                        root,
                        "symbolic-ref",
                        "refs/remotes/origin/HEAD",
                        target,
                    )
                    rejected = verify_installed_plugin_cache(
                        root, payload, expected_head=commit
                    )
                    self.assertEqual(
                        rejected.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID
                    )
                    _git(
                        root,
                        "symbolic-ref",
                        "refs/remotes/origin/HEAD",
                        "refs/remotes/origin/main",
                    )
                    restored = verify_installed_plugin_cache(
                        root, payload, expected_head=commit
                    )
                    self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)

            raw = (
                f"refs/heads/main\t{commit.value}\t\n"
                f"refs/remotes/bad../HEAD\t{commit.value}\t"
                "refs/remotes/bad../main\n"
            )

            def malformed_refs(_root: Path, *arguments: str) -> str:
                if arguments[0] == "for-each-ref":
                    return raw
                if arguments[:3] == ("rev-parse", "--git-path", "refs/remotes"):
                    return str(_root / ".git" / "refs/remotes")
                raise AssertionError(f"unexpected Git command: {arguments[0]}")

            with patch.object(cache_module, "_git", side_effect=malformed_refs):
                malformed = cache_module._read_refs(root)
            self.assertIsNone(malformed)

    def test_s3_loose_symbolic_ref_requires_exact_target_content(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture(root)
            head_file = root / ".git" / "refs" / "remotes" / "origin" / "HEAD"
            before = head_file.read_bytes()
            head_file.write_bytes(b"ref: refs/remotes/origin/main \n")
            rejected = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(rejected.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID)
            head_file.write_bytes(before)
            restored = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(head_file.read_bytes(), before)

    def test_s3_crlf_loose_symbolic_ref_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture(root)
            head_file = root / ".git" / "refs" / "remotes" / "origin" / "HEAD"
            before = head_file.read_bytes()
            head_file.write_bytes(b"ref: refs/remotes/origin/main\r\n")
            rejected = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(rejected.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID)
            head_file.write_bytes(before)
            restored = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(head_file.read_bytes(), before)

    def test_s4_development_ref_remains_rejected_with_normal_remote_head(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            commit, payload = _normal_clone_fixture(root)
            before = _git(
                root,
                "for-each-ref",
                "--format=%(refname)=%(objectname)",
            )
            development, _ = _parentless_commit(
                root,
                {"payload.txt": b"payload\n", "tests/development.py": b"development\n"},
            )
            _git(root, "update-ref", "refs/heads/development", development.value)
            rejected = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(rejected.status, InstallClosureStatus.INSTALLED_REF_SET_INVALID)
            _git(root, "update-ref", "-d", "refs/heads/development")
            restored = verify_installed_plugin_cache(root, payload, expected_head=commit)
            self.assertEqual(restored.status, InstallClosureStatus.VERIFIED)
            self.assertEqual(
                _git(
                    root,
                    "for-each-ref",
                    "--format=%(refname)=%(objectname)",
                ),
                before,
            )

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


if __name__ == "__main__":
    unittest.main()
