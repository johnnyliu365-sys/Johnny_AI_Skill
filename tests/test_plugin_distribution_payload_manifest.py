from __future__ import annotations

import importlib
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Iterator
from unittest import TestCase

from pydantic import ValidationError

from library.local_orchestration.runtime_dependency_lock import build_approved_runtime_lock
from library.local_orchestration.windows_package_manifest import (
    PayloadManifest,
    PayloadManifestEntry,
    build_payload_manifest,
)


_SOURCE_COMMIT = "a" * 40


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _entry(path: str) -> PayloadManifestEntry:
    return PayloadManifestEntry(
        archive_relative_path=path,
        sha256="0" * 64,
        byte_length=0,
    )


def _manifest(entries: tuple[PayloadManifestEntry, ...]) -> PayloadManifest:
    return PayloadManifest(
        schema_version=1,
        plugin_id="johnny-ai-skill",
        plugin_version="0.3.2",
        source_commit=_SOURCE_COMMIT,
        dependency_lock_digest="1" * 64,
        entries=entries,
    )


def _copy_manifest_entries(manifest: PayloadManifest, source_root: Path, target_root: Path) -> None:
    for entry in manifest.entries:
        source = source_root.joinpath(*entry.archive_relative_path.split("/"))
        target = target_root.joinpath(*entry.archive_relative_path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


@contextmanager
def _isolated_library_import(fixture_root: Path, development_root: Path) -> Iterator[None]:
    original_path = list(sys.path)
    saved_modules: dict[str, ModuleType] = {}
    for module_name in tuple(sys.modules):
        if module_name == "library" or module_name.startswith("library."):
            module = sys.modules.pop(module_name)
            if module is not None:
                saved_modules[module_name] = module

    development_path = development_root.resolve()
    isolated_path = [str(fixture_root)]
    for path_text in original_path:
        if not path_text:
            continue
        candidate = Path(path_text)
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved == development_path or development_path in resolved.parents:
            continue
        isolated_path.append(path_text)
    sys.path = isolated_path
    try:
        yield
    finally:
        for module_name in tuple(sys.modules):
            if module_name == "library" or module_name.startswith("library."):
                del sys.modules[module_name]
        sys.modules.update(saved_modules)
        sys.path = original_path


class PayloadManifestTests(TestCase):
    def test_payload_manifest_round_trips_canonically(self) -> None:
        manifest = build_payload_manifest(
            _repository_root(),
            _SOURCE_COMMIT,
            build_approved_runtime_lock(),
        )

        rebuilt = PayloadManifest.model_validate_json(manifest.canonical_json(), strict=True)

        self.assertEqual(manifest, rebuilt)
        self.assertEqual(manifest.canonical_digest(), rebuilt.canonical_digest())

    def test_payload_manifest_contains_the_complete_allowlist(self) -> None:
        manifest = build_payload_manifest(
            _repository_root(),
            _SOURCE_COMMIT,
            build_approved_runtime_lock(),
        )
        paths = tuple(entry.archive_relative_path for entry in manifest.entries)

        self.assertEqual(paths, tuple(sorted(paths)))
        self.assertIn(".codex-plugin/plugin.json", paths)
        self.assertIn("skills/johnny-project-takeover/SKILL.md", paths)
        self.assertIn("skills/apply-reusable-modules/SKILL.md", paths)
        self.assertIn("library/MODULE_CATALOG.md", paths)
        self.assertIn("AGENTS.md", paths)
        self.assertIn("Workflow.md", paths)
        self.assertIn("CodeReview.md", paths)
        self.assertIn("README.md", paths)
        self.assertIn("requirements-runtime.lock", paths)
        self.assertTrue(all(not path.startswith("doc/") for path in paths))
        self.assertTrue(all(not path.startswith("modules/") for path in paths))
        self.assertTrue(all(not path.startswith("tests/") for path in paths))
        self.assertTrue(all("__pycache__" not in path for path in paths))
        self.assertTrue(all(not path.endswith((".pyc", ".pyo")) for path in paths))

    def test_payload_manifest_rejects_duplicate_entries(self) -> None:
        duplicate = _entry("README.md")

        with self.assertRaises(ValidationError):
            _manifest((duplicate, duplicate))

    def test_payload_manifest_rejects_excluded_target_tree(self) -> None:
        with self.assertRaises(ValidationError):
            _entry("tests/target-project/sentinel.txt")

    def test_payload_manifest_rejects_escape_and_self_entry_paths(self) -> None:
        for path in (
            "../README.md",
            "/absolute.txt",
            "C:/absolute.txt",
            "skills\\escape.txt",
            "payload-manifest.json",
        ):
            with self.subTest(path=path), self.assertRaises(ValidationError):
                _entry(path)

    def test_payload_manifest_rejects_invalid_digest_and_length(self) -> None:
        with self.assertRaises(ValidationError):
            PayloadManifestEntry(
                archive_relative_path="README.md",
                sha256="A" * 64,
                byte_length=0,
            )
        with self.assertRaises(ValidationError):
            PayloadManifestEntry(
                archive_relative_path="README.md",
                sha256="0" * 64,
                byte_length=-1,
            )

    def test_payload_manifest_fixture_imports_router_and_shipped_content(self) -> None:
        source_root = _repository_root()
        manifest = build_payload_manifest(
            source_root,
            _SOURCE_COMMIT,
            build_approved_runtime_lock(),
        )

        with tempfile.TemporaryDirectory(prefix="pd03-manifest-") as temp_name:
            fixture_root = Path(temp_name)
            _copy_manifest_entries(manifest, source_root, fixture_root)
            self.assertEqual(
                "johnny-ai-skill",
                (fixture_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
                .split('"name": "', 1)[1]
                .split('"', 1)[0],
            )
            self.assertTrue(
                (fixture_root / "skills" / "johnny-project-takeover" / "SKILL.md").is_file()
            )
            self.assertTrue(
                (fixture_root / "skills" / "apply-reusable-modules" / "SKILL.md").is_file()
            )
            self.assertTrue((fixture_root / "library" / "MODULE_CATALOG.md").is_file())

            with _isolated_library_import(fixture_root, source_root):
                router = importlib.import_module("library.workflow_router")
                router_file = router.__file__
                self.assertIsNotNone(router_file)
                self.assertTrue(str(Path(router_file).resolve()).startswith(str(fixture_root.resolve())))
