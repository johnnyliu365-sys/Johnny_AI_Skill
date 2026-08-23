"""TDD cells for the read-only publication repository closure."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final
from unittest.mock import patch

from library.local_orchestration import publication_repository_closure as closure_module
from library.local_orchestration.publication_repository_closure import (
    PublicationClosureStatus,
    PublicationCommit,
    PublicationGeneratedPinCarrier,
    PublicationPayload,
    PublicationReleaseDeclaration,
    PublicationRepositoryRef,
    PublicationTreeDifference,
    PublicationVersion,
    payload_from_manifest,
    verify_publication_repository,
)


_REPO: Final[Path] = Path(__file__).resolve().parents[1]
_REMOTE_URL: Final[PublicationRepositoryRef] = PublicationRepositoryRef(
    value="https://example.invalid/johnny-plugin-publication.git"
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
    """Create a root commit whose tree contains exactly ``entries``."""

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


def _bare_remote(
    root: Path, source: Path, commit: PublicationCommit, *, tag: bool = True
) -> Path:
    remote = root / "publication.git"
    _git(root, "init", "--bare", "-q", str(remote))
    _git(source, "push", "--quiet", str(remote), f"{commit.value}:refs/heads/main")
    if tag:
        _git(
            source,
            "push",
            "--quiet",
            str(remote),
            f"{commit.value}:refs/tags/plugin-v1.2.3",
        )
    _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    return remote


def _replace_remote(source: Path, remote: Path, commit: PublicationCommit) -> None:
    _git(source, "push", "--force", "--quiet", str(remote), f"{commit.value}:refs/heads/main")
    _git(
        source,
        "push",
        "--force",
        "--quiet",
        str(remote),
        f"{commit.value}:refs/tags/plugin-v1.2.3",
    )


def _fixture(
    directory: Path,
    entries: dict[str, bytes] | None = None,
) -> tuple[Path, Path, PublicationCommit, PublicationPayload]:
    source = directory / "source"
    _initialise(source)
    actual_entries = entries or {"payload.txt": b"payload\n"}
    commit, payload = _parentless_commit(source, actual_entries)
    remote = _bare_remote(directory, source, commit)
    return source, remote, commit, payload


def _versioned_entries(
    version: str,
    filename: str,
    content: bytes,
    pin: str,
    *,
    extra: tuple[str, bytes] | None = None,
) -> dict[str, bytes]:
    plugin = {
        "name": "fixture-plugin",
        "version": version,
        "payload": {
            "trees": [".claude-plugin"],
            "files": [filename],
            "excludedSegments": ["__pycache__", ".git"],
            "excludedSuffixes": [".pyc", ".pyo"],
        },
    }
    marketplace = {
        "plugins": [
            {
                "name": "fixture-plugin",
                "version": version,
                "source": {
                    "source": "url",
                    "url": "https://example.invalid/publication.git",
                    "sha": pin,
                },
            }
        ]
    }
    entries = {
        ".claude-plugin/plugin.json": (
            json.dumps(plugin, indent=2) + "\n"
        ).encode("utf-8"),
        ".claude-plugin/marketplace.json": (
            json.dumps(marketplace, indent=2) + "\n"
        ).encode("utf-8"),
        filename: content,
    }
    if extra is not None:
        entries[extra[0]] = extra[1]
    return entries


def _versioned_fixture(
    directory: Path,
) -> tuple[Path, PublicationCommit, PublicationPayload, PublicationCommit]:
    source = directory / "versioned-source"
    _initialise(source)
    old_entries = _versioned_entries("0.4.10", "old.txt", b"old\n", "0" * 40)
    old_commit, _ = _parentless_commit(source, old_entries)
    current_entries = _versioned_entries(
        "0.4.11", "current.txt", b"current\n", "0" * 40
    )
    current_commit, _ = _parentless_commit(source, current_entries)
    _git(source, "update-ref", "refs/heads/main", current_commit.value)
    _git(
        source,
        "update-ref",
        "refs/tags/plugin-v0.4.11",
        current_commit.value,
    )
    _git(source, "update-ref", "refs/tags/plugin-v0.4.10", old_commit.value)
    _git(source, "symbolic-ref", "HEAD", "refs/heads/main")
    live_entries = _versioned_entries(
        "0.4.11", "current.txt", b"current\n", current_commit.value
    )
    for relative, content in live_entries.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    blob_ids = tuple(
        (relative, _git(source, "rev-parse", f"{current_commit.value}:{relative}"))
        for relative in sorted(live_entries)
    )
    payload = PublicationPayload(
        paths=tuple(relative for relative, _ in blob_ids),
        blob_ids=blob_ids,
    )
    return source, current_commit, payload, old_commit


def _restore_current_source(source: Path, current: PublicationCommit) -> None:
    entries = _versioned_entries(
        "0.4.11", "current.txt", b"current\n", current.value
    )
    for relative, content in entries.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


class PublicationRepositoryClosureTests(unittest.TestCase):
    def test_t12_release_dto_constructors_are_strongly_validated(self) -> None:
        carrier = PublicationGeneratedPinCarrier(
            pin_carrier=".claude-plugin/marketplace.json",
            recorded_sha="0" * 40,
        )
        declaration = PublicationReleaseDeclaration(
            version=PublicationVersion(value="0.4.11"),
            paths=(".claude-plugin/marketplace.json", "payload.txt"),
            carrier=carrier,
        )
        self.assertEqual(declaration.carrier.recorded_sha, "0" * 40)
        with self.assertRaises(ValueError):
            PublicationGeneratedPinCarrier(
                pin_carrier=".claude-plugin/marketplace.json",
                recorded_sha="1" * 40,
            )

    def test_t12_current_release_binding_and_blob_mutation(self) -> None:
        with TemporaryDirectory() as temporary:
            source, current, payload, _old = _versioned_fixture(Path(temporary))
            result = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(result.status, PublicationClosureStatus.VERIFIED)

            _git(source, "update-ref", "-d", "refs/tags/plugin-v0.4.11")
            missing_current_tag = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(
                missing_current_tag.status,
                PublicationClosureStatus.RELEASE_VERSION_MISMATCH,
            )
            _git(
                source,
                "update-ref",
                "refs/tags/plugin-v0.4.11",
                current.value,
            )

            changed_entries = _versioned_entries(
                "0.4.11", "current.txt", b"changed\n", "0" * 40
            )
            changed, _ = _parentless_commit(source, changed_entries)
            _git(source, "update-ref", "refs/heads/main", changed.value)
            _git(
                source,
                "update-ref",
                "refs/tags/plugin-v0.4.11",
                changed.value,
            )
            for relative, content in _versioned_entries(
                "0.4.11", "current.txt", b"current\n", current.value
            ).items():
                target = source / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            mutated = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=changed,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=changed,
            )
            self.assertEqual(mutated.status, PublicationClosureStatus.TREE_MISMATCH)
            self.assertIsNotNone(mutated.difference)
            assert mutated.difference is not None
            self.assertEqual(mutated.difference.content_mismatch, ("current.txt",))

            moved_current_entries = _versioned_entries(
                "0.4.11", "old.txt", b"old root\n", "0" * 40
            )
            moved_current, _ = _parentless_commit(source, moved_current_entries)
            _git(
                source,
                "update-ref",
                "refs/heads/main",
                current.value,
            )
            _git(
                source,
                "update-ref",
                "refs/tags/plugin-v0.4.11",
                moved_current.value,
            )
            _restore_current_source(source, current)
            moved = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(moved.status, PublicationClosureStatus.PIN_MISMATCH)

    def test_t12_retained_older_release_uses_its_own_path_declaration(self) -> None:
        with TemporaryDirectory() as temporary:
            source, current, payload, old = _versioned_fixture(Path(temporary))
            result = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(result.status, PublicationClosureStatus.VERIFIED)

            changed_old_entries = _versioned_entries(
                "0.4.10", "old.txt", b"historical bytes changed\n", "0" * 40
            )
            changed_old, _ = _parentless_commit(source, changed_old_entries)
            _git(source, "update-ref", "refs/tags/plugin-v0.4.10", changed_old.value)
            _restore_current_source(source, current)
            historical_bytes = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(historical_bytes.status, PublicationClosureStatus.VERIFIED)

            bad_old_entries = _versioned_entries(
                "0.4.10",
                "old.txt",
                b"old\n",
                "0" * 40,
                extra=("undeclared.txt", b"x\n"),
            )
            bad_old, _ = _parentless_commit(source, bad_old_entries)
            _git(source, "update-ref", "refs/tags/plugin-v0.4.10", bad_old.value)
            _restore_current_source(source, current)
            rejected = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(rejected.status, PublicationClosureStatus.TREE_MISMATCH)
            self.assertIsNotNone(rejected.difference)
            assert rejected.difference is not None
            self.assertEqual(rejected.difference.extra, ("undeclared.txt",))
            _git(source, "update-ref", "refs/tags/plugin-v0.4.10", old.value)

    def test_t12_target_declaration_and_version_failures_are_distinct(self) -> None:
        with TemporaryDirectory() as temporary:
            source, current, payload, old = _versioned_fixture(Path(temporary))
            wrong_version_entries = _versioned_entries(
                "0.4.12", "old.txt", b"old\n", "0" * 40
            )
            wrong_version, _ = _parentless_commit(source, wrong_version_entries)
            _git(source, "update-ref", "refs/tags/plugin-v0.4.10", wrong_version.value)
            _restore_current_source(source, current)
            version_result = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(
                version_result.status,
                PublicationClosureStatus.RELEASE_VERSION_MISMATCH,
            )

            malformed_entries = _versioned_entries(
                "0.4.10", "old.txt", b"old\n", "1" * 40
            )
            malformed_entries.pop(".claude-plugin/plugin.json")
            malformed, _ = _parentless_commit(source, malformed_entries)
            _git(source, "update-ref", "refs/tags/plugin-v0.4.10", malformed.value)
            _restore_current_source(source, current)
            declaration_result = verify_publication_repository(
                source,
                payload,
                _REMOTE_URL,
                expected_main=current,
                pin_carrier=".claude-plugin/marketplace.json",
                expected_pin=current,
            )
            self.assertEqual(
                declaration_result.status,
                PublicationClosureStatus.RELEASE_DECLARATION_INVALID,
            )
            _git(source, "update-ref", "refs/tags/plugin-v0.4.10", old.value)

    def test_c1_valid_main_and_release_tag_are_verified(self) -> None:
        with TemporaryDirectory() as temporary:
            _source, remote, commit, payload = _fixture(Path(temporary))
            result = verify_publication_repository(
                remote, payload, _REMOTE_URL, expected_main=commit
            )
            self.assertEqual(result.status, PublicationClosureStatus.VERIFIED)
            self.assertIsNotNone(result.snapshot)
            assert result.snapshot is not None
            self.assertEqual(
                tuple(ref.name for ref in result.snapshot.refs),
                ("refs/heads/main", "refs/tags/plugin-v1.2.3"),
            )
            self.assertEqual(result.difference, PublicationTreeDifference())

    def test_c2_foreign_ref_and_missing_main_are_named(self) -> None:
        with TemporaryDirectory() as temporary:
            source, remote, commit, payload = _fixture(Path(temporary))
            _git(remote, "update-ref", "refs/heads/development", commit.value)
            foreign = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(foreign.status, PublicationClosureStatus.REF_SET_INVALID)

            _git(remote, "update-ref", "-d", "refs/heads/development")
            _git(remote, "update-ref", "refs/notes/review", commit.value)
            unknown_namespace = verify_publication_repository(
                remote, payload, _REMOTE_URL
            )
            self.assertEqual(
                unknown_namespace.status, PublicationClosureStatus.REF_SET_INVALID
            )

            _git(remote, "update-ref", "-d", "refs/heads/main")
            _git(remote, "update-ref", "-d", "refs/notes/review")
            _git(remote, "symbolic-ref", "HEAD", "refs/tags/plugin-v1.2.3")
            missing = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(missing.status, PublicationClosureStatus.DEFAULT_BRANCH_INVALID)

            # The bare repository is still disposable; restore its default branch
            # before deleting the only admitted head for a distinct missing-main cell.
            _git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
            missing = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(missing.status, PublicationClosureStatus.MAIN_MISSING)
            self.assertTrue(source.exists())

    def test_c2_non_main_default_is_named_without_inference(self) -> None:
        with TemporaryDirectory() as temporary:
            _source, remote, _commit, payload = _fixture(Path(temporary))
            _git(remote, "symbolic-ref", "HEAD", "refs/heads/other")
            result = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(result.status, PublicationClosureStatus.DEFAULT_BRANCH_INVALID)

    def test_c3_parent_and_tree_differences_are_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            source, remote, commit, payload = _fixture(Path(temporary))
            _git(source, "update-ref", "refs/heads/work", commit.value)
            _git(source, "clean", "-fdx")
            _git(source, "checkout", "-q", "work")
            (source / "payload.txt").write_bytes(b"history\n")
            _git(source, "add", "payload.txt")
            _git(
                source,
                "-c",
                "user.name=Closure Test",
                "-c",
                "user.email=closure@example.invalid",
                "commit",
                "-qm",
                "history",
            )
            parent = PublicationCommit(value=_git(source, "rev-parse", "HEAD"))
            _replace_remote(source, remote, parent)
            result = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(result.status, PublicationClosureStatus.COMMIT_NOT_ROOT)

            extra_source, extra_remote, _extra_commit, _ = _fixture(
                Path(temporary) / "extra", {"payload.txt": b"payload\n", "extra.txt": b"x\n"}
            )
            extra = verify_publication_repository(
                extra_remote, payload, _REMOTE_URL
            )
            self.assertEqual(extra.status, PublicationClosureStatus.TREE_MISMATCH)
            self.assertIsNotNone(extra.difference)
            assert extra.difference is not None
            self.assertEqual(extra.difference.extra, ("extra.txt",))
            self.assertTrue(extra_source.exists())

    def test_c3_changed_blob_and_missing_path_are_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            changed_source, changed_remote, _commit, payload = _fixture(
                Path(temporary) / "changed"
            )
            changed_commit, _ = _parentless_commit(
                changed_source, {"payload.txt": b"changed\n"}
            )
            _replace_remote(changed_source, changed_remote, changed_commit)
            changed = verify_publication_repository(
                changed_remote, payload, _REMOTE_URL
            )
            self.assertEqual(changed.status, PublicationClosureStatus.TREE_MISMATCH)
            self.assertIsNotNone(changed.difference)
            assert changed.difference is not None
            self.assertEqual(changed.difference.content_mismatch, ("payload.txt",))

            missing_source, missing_remote, _commit, expected_payload = _fixture(
                Path(temporary) / "missing"
            )
            missing_commit, _ = _parentless_commit(
                missing_source, {"other.txt": b"other\n"}
            )
            _replace_remote(missing_source, missing_remote, missing_commit)
            missing = verify_publication_repository(
                missing_remote,
                expected_payload,
                _REMOTE_URL,
            )
            self.assertEqual(missing.status, PublicationClosureStatus.TREE_MISMATCH)
            self.assertIsNotNone(missing.difference)
            assert missing.difference is not None
            self.assertEqual(missing.difference.missing, ("payload.txt",))

    def test_c5_bad_boundary_and_malformed_git_result_fail_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            _source, remote, _commit, payload = _fixture(Path(temporary))
            with self.assertRaises(ValueError):
                PublicationRepositoryRef(value="not-https")
            result = verify_publication_repository(
                remote,
                PublicationPayload.model_construct(
                    paths=("payload.txt",), blob_ids=(("payload.txt", "bad"),)
                ),
                _REMOTE_URL,
            )
            self.assertEqual(result.status, PublicationClosureStatus.READBACK_MISMATCH)

            def malformed_git(_root: Path, *arguments: str) -> str:
                if arguments[0] == "symbolic-ref":
                    return "refs/heads/main\n"
                return "not-a-ref\n"

            with patch(
                "library.local_orchestration.publication_repository_closure._git",
                side_effect=malformed_git,
            ):
                malformed = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(malformed.status, PublicationClosureStatus.REF_SET_INVALID)

    def test_c5_non_commit_object_ref_is_a_named_rejection(self) -> None:
        with TemporaryDirectory() as temporary:
            source, remote, _commit, payload = _fixture(Path(temporary))
            blob = _git(source, "hash-object", "-w", "payload.txt")

            def non_commit_git(_root: Path, *arguments: str) -> str:
                command = arguments[0]
                if command == "symbolic-ref":
                    return "refs/heads/main\n"
                if command == "for-each-ref":
                    return (
                        f"refs/heads/main\t{blob}\t\n"
                        f"refs/tags/plugin-v1.2.3\t{blob}\t\n"
                    )
                if command == "cat-file":
                    return "blob\n"
                if command == "rev-list":
                    return ""
                raise AssertionError(f"unexpected Git command: {command}")

            with patch.object(closure_module, "_git", side_effect=non_commit_git):
                result = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(result.status, PublicationClosureStatus.COMMIT_NOT_ROOT)

    def test_n6_declared_carrier_requires_a_local_live_source(self) -> None:
        with TemporaryDirectory() as temporary:
            _source, remote, commit, payload = _fixture(Path(temporary))
            result = verify_publication_repository(
                remote,
                payload,
                _REMOTE_URL,
                expected_main=commit,
                pin_carrier="payload.txt",
                expected_pin=commit,
            )
            self.assertEqual(result.status, PublicationClosureStatus.TREE_MISMATCH)

    def test_c5_full_but_absent_sha_is_a_named_rejection(self) -> None:
        with TemporaryDirectory() as temporary:
            _source, remote, _commit, payload = _fixture(Path(temporary))
            absent = "f" * 40

            def absent_git(_root: Path, *arguments: str) -> str:
                command = arguments[0]
                if command == "symbolic-ref":
                    return "refs/heads/main\n"
                if command == "for-each-ref":
                    return (
                        f"refs/heads/main\t{absent}\t\n"
                        f"refs/tags/plugin-v1.2.3\t{absent}\t\n"
                    )
                if command == "cat-file":
                    raise closure_module._GitReadFailure
                raise AssertionError(f"unexpected Git command: {command}")

            with patch.object(closure_module, "_git", side_effect=absent_git):
                result = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(result.status, PublicationClosureStatus.COMMIT_NOT_ROOT)

    def test_c5_unreadable_and_malformed_ls_tree_are_named_rejections(self) -> None:
        with TemporaryDirectory() as temporary:
            _source, remote, commit, payload = _fixture(Path(temporary))

            def tree_git(_root: Path, *arguments: str) -> str:
                command = arguments[0]
                if command == "symbolic-ref":
                    return "refs/heads/main\n"
                if command == "for-each-ref":
                    return (
                        f"refs/heads/main\t{commit.value}\t\n"
                        f"refs/tags/plugin-v1.2.3\t{commit.value}\t\n"
                    )
                if command == "cat-file":
                    return "commit\n"
                if command == "rev-list":
                    return f"{commit.value}\n"
                if command == "ls-tree":
                    return "not-a-tree\x00"
                raise AssertionError(f"unexpected Git command: {command}")

            with patch.object(closure_module, "_git", side_effect=tree_git):
                malformed = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(malformed.status, PublicationClosureStatus.REMOTE_UNREACHABLE)

            def unreadable_git(_root: Path, *arguments: str) -> str:
                if arguments[0] == "ls-tree":
                    raise closure_module._GitReadFailure
                return tree_git(_root, *arguments)

            with patch.object(closure_module, "_git", side_effect=unreadable_git):
                unreadable = verify_publication_repository(remote, payload, _REMOTE_URL)
            self.assertEqual(unreadable.status, PublicationClosureStatus.REMOTE_UNREACHABLE)

    def test_manifest_adapter_returns_frozen_typed_payload(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / "plugin.json"
            payload_file = root / "payload.txt"
            payload_file.write_text("payload\n", encoding="utf-8")
            (root / "payload-dir").mkdir()
            (root / "payload-dir" / "item.txt").write_text("item\n", encoding="utf-8")
            manifest.write_text(
                '{"payload": {"trees": ["payload-dir"], "files": ["payload.txt"]}}',
                encoding="utf-8",
            )
            _initialise(root)
            payload = payload_from_manifest(root, manifest)
            self.assertEqual(
                payload.paths, ("payload-dir/item.txt", "payload.txt")
            )
            with self.assertRaises(ValueError):
                payload.paths += ("another.txt",)


if __name__ == "__main__":
    unittest.main()
