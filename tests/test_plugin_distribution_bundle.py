from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Callable
from unittest import TestCase
from unittest.mock import patch
import zipfile

from pydantic import ValidationError

from library.local_orchestration.plugin_bundle_builder import (
    PluginBundleBuildFailure,
    PluginBundleBuildRequest,
    PluginBundleBuildResult,
    PluginBundleBuildStatus,
    PluginBundleBuilder,
)
from library.local_orchestration.runtime_dependency_lock import build_approved_runtime_lock
from library.local_orchestration.windows_package_manifest import (
    PayloadManifest,
    PayloadManifestEntry,
    build_payload_manifest,
)


_CANDIDATE_NAME = "johnny-ai-skill-0.4.5.zip"
_SOURCE_COMMIT = "a" * 40


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=False,
        capture_output=True,
        text=True,
        shell=False,
        timeout=30,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def _commit(root: Path, message: str) -> str:
    _run_git(root, "add", "--all")
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "pd09-test",
            "GIT_AUTHOR_EMAIL": "pd09@example.invalid",
            "GIT_COMMITTER_NAME": "pd09-test",
            "GIT_COMMITTER_EMAIL": "pd09@example.invalid",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000",
        }
    )
    completed = subprocess.run(
        ("git", "-C", str(root), "commit", "-m", message),
        check=False,
        capture_output=True,
        text=True,
        shell=False,
        timeout=30,
        env=environment,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return _run_git(root, "rev-parse", "HEAD")


def _copy_manifest_payload(
    source_root: Path,
    manifest: PayloadManifest,
    target_root: Path,
) -> None:
    for entry in manifest.entries:
        source = source_root.joinpath(*entry.archive_relative_path.split("/"))
        target = target_root.joinpath(*entry.archive_relative_path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def _template_manifest() -> PayloadManifest:
    return build_payload_manifest(
        _repository_root(),
        _SOURCE_COMMIT,
        build_approved_runtime_lock(),
    )


def _create_repository(
    parent: Path,
    name: str,
    template: PayloadManifest,
    mutate: Callable[[Path], None] | None = None,
) -> tuple[Path, str]:
    root = parent / name
    root.mkdir()
    _copy_manifest_payload(_repository_root(), template, root)
    if mutate is not None:
        mutate(root)
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.name", "pd09-local")
    _run_git(root, "config", "user.email", "pd09-local@example.invalid")
    return root, _commit(root, "payload")


def _manifest(root: Path, source_commit: str) -> PayloadManifest:
    return build_payload_manifest(root, source_commit, build_approved_runtime_lock())


def _request(
    repository_root: Path,
    output_root: Path,
    manifest: PayloadManifest,
) -> PluginBundleBuildRequest:
    return PluginBundleBuildRequest(
        repository_root=repository_root,
        output_root=output_root,
        manifest=manifest,
    )


class PluginBundleBuilderTests(TestCase):
    def test_bundled_result_rejects_noncanonical_success_digests(self) -> None:
        valid = PluginBundleBuildResult(
            status=PluginBundleBuildStatus.BUNDLED,
            source_commit="a" * 40,
            manifest_digest="b" * 64,
            archive_sha256="c" * 64,
            archive_byte_length=1,
        )
        for field, malformed in (
            ("source_commit", "A" * 40),
            ("manifest_digest", "g" * 64),
            ("archive_sha256", "C" * 64),
        ):
            with self.subTest(field=field):
                payload = valid.model_dump()
                payload[field] = malformed
                with self.assertRaises(ValidationError):
                    PluginBundleBuildResult.model_validate(payload, strict=True)

    def test_same_commit_and_toolchain_emit_identical_zip_bytes(self) -> None:
        template = _template_manifest()
        with tempfile.TemporaryDirectory(prefix="pd09-identical-") as temp_name:
            parent = Path(temp_name)
            first_root, first_commit = _create_repository(parent, "first", template)
            second_root, second_commit = _create_repository(parent, "second", template)
            self.assertEqual(first_commit, second_commit)
            first_output = parent / "first-output"
            second_output = parent / "second-output"
            first_output.mkdir()
            second_output.mkdir()
            manifest = _manifest(first_root, first_commit)

            first = PluginBundleBuilder().build(_request(first_root, first_output, manifest))
            second = PluginBundleBuilder().build(_request(second_root, second_output, manifest))

            self.assertEqual(PluginBundleBuildStatus.BUNDLED, first.status)
            self.assertEqual(first, second)
            first_bytes = (first_output / _CANDIDATE_NAME).read_bytes()
            second_bytes = (second_output / _CANDIDATE_NAME).read_bytes()
            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(hashlib.sha256(first_bytes).hexdigest(), first.archive_sha256)

    def test_changed_clean_source_identity_emits_new_manifest_and_archive(self) -> None:
        template = _template_manifest()

        def change_readme(root: Path) -> None:
            (root / "README.md").write_bytes(b"Ticket 09 changed payload\n")

        with tempfile.TemporaryDirectory(prefix="pd09-changed-") as temp_name:
            parent = Path(temp_name)
            first_root, first_commit = _create_repository(parent, "first", template)
            second_root, second_commit = _create_repository(parent, "second", template, change_readme)
            first_output = parent / "first-output"
            second_output = parent / "second-output"
            first_output.mkdir()
            second_output.mkdir()
            first_manifest = _manifest(first_root, first_commit)
            second_manifest = _manifest(second_root, second_commit)

            first = PluginBundleBuilder().build(_request(first_root, first_output, first_manifest))
            second = PluginBundleBuilder().build(_request(second_root, second_output, second_manifest))

            self.assertEqual(PluginBundleBuildStatus.BUNDLED, first.status)
            self.assertEqual(PluginBundleBuildStatus.BUNDLED, second.status)
            self.assertNotEqual(first.source_commit, second.source_commit)
            self.assertNotEqual(first.manifest_digest, second.manifest_digest)
            self.assertNotEqual(first.archive_sha256, second.archive_sha256)

    def test_zip_metadata_and_manifest_last_are_canonical(self) -> None:
        template = _template_manifest()
        with tempfile.TemporaryDirectory(prefix="pd09-zip-") as temp_name:
            parent = Path(temp_name)
            source_root, source_commit = _create_repository(parent, "source", template)
            output_root = parent / "output"
            output_root.mkdir()
            manifest = _manifest(source_root, source_commit)
            result = PluginBundleBuilder().build(_request(source_root, output_root, manifest))
            self.assertEqual(PluginBundleBuildStatus.BUNDLED, result.status)

            with zipfile.ZipFile(output_root / _CANDIDATE_NAME) as archive:
                infos = archive.infolist()
                names = tuple(info.filename for info in infos)
                self.assertEqual(
                    tuple(entry.archive_relative_path for entry in manifest.entries)
                    + ("payload-manifest.json",),
                    names,
                )
                self.assertEqual("payload-manifest.json", names[-1])
                self.assertEqual(b"", archive.comment)
                for info in infos:
                    self.assertFalse(info.is_dir())
                    self.assertEqual((1980, 1, 1, 0, 0, 0), info.date_time)
                    self.assertEqual(3, info.create_system)
                    self.assertEqual(zipfile.ZIP_DEFLATED, info.compress_type)
                    self.assertEqual(b"", info.extra)
                    self.assertEqual(b"", info.comment)
                    self.assertEqual(info.filename, info.filename.encode("utf-8").decode("utf-8"))
                    mode = info.external_attr >> 16
                    self.assertEqual(0o100000, mode & 0o170000)
                    self.assertEqual(0o644, mode & 0o777)
                self.assertEqual(
                    manifest.canonical_json().encode("utf-8"),
                    archive.read("payload-manifest.json"),
                )

    def test_source_and_output_gates_block_without_candidate(self) -> None:
        template = _template_manifest()
        with tempfile.TemporaryDirectory(prefix="pd09-gates-") as temp_name:
            parent = Path(temp_name)

            dirty_root, dirty_commit = _create_repository(parent, "dirty", template)
            dirty_output = parent / "dirty-output"
            dirty_output.mkdir()
            dirty_manifest = _manifest(dirty_root, dirty_commit)
            (dirty_root / "README.md").write_bytes(b"dirty\n")
            dirty = PluginBundleBuilder().build(_request(dirty_root, dirty_output, dirty_manifest))
            self.assertEqual(PluginBundleBuildFailure.SOURCE_DIRTY, dirty.failure)
            self.assertFalse((dirty_output / _CANDIDATE_NAME).exists())

            wrong_root, wrong_commit = _create_repository(parent, "wrong", template)
            wrong_manifest = _manifest(wrong_root, wrong_commit)
            (wrong_root / "README.md").write_bytes(b"new commit\n")
            new_commit = _commit(wrong_root, "new source identity")
            wrong_output = parent / "wrong-output"
            wrong_output.mkdir()
            wrong_request = _request(wrong_root, wrong_output, wrong_manifest)
            wrong = PluginBundleBuilder().build(wrong_request)
            self.assertEqual(PluginBundleBuildFailure.SOURCE_IDENTITY_MISMATCH, wrong.failure)
            self.assertNotEqual(wrong_commit, new_commit)

            mismatch_root, mismatch_commit = _create_repository(parent, "mismatch", template)
            mismatch_output = parent / "mismatch-output"
            mismatch_output.mkdir()
            mismatch_manifest = _manifest(mismatch_root, mismatch_commit).model_copy(
                update={"plugin_version": "9.9.9"}
            )
            mismatch = PluginBundleBuilder().build(
                _request(mismatch_root, mismatch_output, mismatch_manifest)
            )
            self.assertEqual(PluginBundleBuildFailure.MANIFEST_MISMATCH, mismatch.failure)

            existing_root, existing_commit = _create_repository(parent, "existing", template)
            existing_output = parent / "existing-output"
            existing_output.mkdir()
            (existing_output / _CANDIDATE_NAME).write_bytes(b"existing")
            existing = PluginBundleBuilder().build(
                _request(existing_root, existing_output, _manifest(existing_root, existing_commit))
            )
            self.assertEqual(PluginBundleBuildFailure.OUTPUT_UNAVAILABLE, existing.failure)

            invalid_output_root, invalid_commit = _create_repository(parent, "invalid", template)
            invalid = PluginBundleBuilder().build(
                _request(
                    invalid_output_root,
                    invalid_output_root / "not-created",
                    _manifest(invalid_output_root, invalid_commit),
                )
            )
            self.assertEqual(PluginBundleBuildFailure.REQUEST_INVALID, invalid.failure)

    def test_missing_changed_and_symlink_entries_block_with_finite_failures(self) -> None:
        template = _template_manifest()
        with tempfile.TemporaryDirectory(prefix="pd09-entries-") as temp_name:
            parent = Path(temp_name)
            missing_root, missing_commit = _create_repository(parent, "missing", template)
            old_manifest = _manifest(missing_root, missing_commit)
            (missing_root / "README.md").unlink()
            missing_commit = _commit(missing_root, "remove payload")
            missing_output = parent / "missing-output"
            missing_output.mkdir()
            missing = PluginBundleBuilder().build(
                _request(
                    missing_root,
                    missing_output,
                    old_manifest.model_copy(update={"source_commit": missing_commit}),
                )
            )
            self.assertEqual(PluginBundleBuildFailure.ENTRY_UNAVAILABLE, missing.failure)

            changed_root, changed_commit = _create_repository(parent, "changed", template)
            changed_manifest = _manifest(changed_root, changed_commit)
            (changed_root / "README.md").write_bytes(b"changed committed payload\n")
            changed_commit = _commit(changed_root, "change payload")
            changed_output = parent / "changed-output"
            changed_output.mkdir()
            changed = PluginBundleBuilder().build(
                _request(
                    changed_root,
                    changed_output,
                    changed_manifest.model_copy(update={"source_commit": changed_commit}),
                )
            )
            self.assertEqual(PluginBundleBuildFailure.ENTRY_CONTENT_MISMATCH, changed.failure)

            symlink_root, symlink_commit = _create_repository(parent, "symlink", template)
            symlink_path = symlink_root / "library" / "linked-readme.md"
            symlink_path.write_bytes(b"symlink sentinel")
            symlink_commit = _commit(symlink_root, "add symlink")
            symlink_output = parent / "symlink-output"
            symlink_output.mkdir()
            symlink_manifest = _manifest(symlink_root, symlink_commit)
            original_is_symlink = Path.is_symlink

            def sentinel_is_symlink(path: Path) -> bool:
                return path == symlink_path or original_is_symlink(path)

            with patch.object(Path, "is_symlink", autospec=True, side_effect=sentinel_is_symlink):
                symlink = PluginBundleBuilder().build(
                    _request(symlink_root, symlink_output, symlink_manifest)
                )
            self.assertEqual(PluginBundleBuildFailure.ENTRY_UNAVAILABLE, symlink.failure)

    def test_manifest_rejects_duplicate_and_excluded_identities_before_build(self) -> None:
        entry = PayloadManifestEntry(
            archive_relative_path="README.md",
            sha256="0" * 64,
            byte_length=0,
        )
        with self.assertRaises(ValidationError):
            PayloadManifest(
                schema_version=1,
                plugin_id="johnny-ai-skill",
                plugin_version="0.4.0",
                source_commit=_SOURCE_COMMIT,
                dependency_lock_digest="1" * 64,
                entries=(entry, entry),
            )
        with self.assertRaises(ValidationError):
            PayloadManifestEntry(
                archive_relative_path="tests/target-project/sentinel.txt",
                sha256="0" * 64,
                byte_length=0,
            )

    def test_extracted_bundle_loads_shipped_content_without_development_checkout(self) -> None:
        template = _template_manifest()
        extracted_path: Path | None = None
        candidate_path: Path | None = None
        with tempfile.TemporaryDirectory(prefix="pd09-isolated-") as temp_name:
            parent = Path(temp_name)
            source_root, source_commit = _create_repository(parent, "source", template)
            output_root = parent / "output"
            output_root.mkdir()
            manifest = _manifest(source_root, source_commit)
            result = PluginBundleBuilder().build(_request(source_root, output_root, manifest))
            self.assertEqual(PluginBundleBuildStatus.BUNDLED, result.status)
            candidate_path = output_root / _CANDIDATE_NAME
            extracted_path = parent / "extracted"
            extracted_path.mkdir()
            with zipfile.ZipFile(candidate_path) as archive:
                archive.extractall(extracted_path)

            child = """
from pathlib import Path
import importlib
root = Path.cwd().resolve()
assert (root / 'skills' / 'johnny-project-takeover' / 'SKILL.md').read_text(encoding='utf-8')
assert (root / 'skills' / 'apply-reusable-modules' / 'SKILL.md').read_text(encoding='utf-8')
assert (root / 'library' / 'MODULE_CATALOG.md').is_file()
router = importlib.import_module('library.workflow_router')
assert Path(router.__file__).resolve().is_relative_to(root)
print('isolated-bundle-ok')
"""
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(extracted_path)
            completed = subprocess.run(
                (sys.executable, "-B", "-c", child),
                cwd=extracted_path,
                check=False,
                capture_output=True,
                text=True,
                shell=False,
                timeout=30,
                env=environment,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("isolated-bundle-ok", completed.stdout)

        self.assertIsNotNone(candidate_path)
        self.assertIsNotNone(extracted_path)
        self.assertFalse(candidate_path.exists())
        self.assertFalse(extracted_path.exists())
