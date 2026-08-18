"""L3 closure tests: digest-verified payload extraction and launcher copy."""

from __future__ import annotations

import hashlib
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.payload_effect_ports import (
    RealLauncherEffectPort,
    RealPluginPayloadEffectPort,
)
from library.local_orchestration.plugin_install_transaction import (
    InstallEffectOutcomeStatus,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.windows_package_manifest import (
    PayloadManifest,
    PayloadManifestEntry,
)

_FILES: dict[str, bytes] = {
    "AGENTS.md": b"# agents entry\n",
    "johnny-router.ps1": b"# launcher stub\n",
    "library/local_orchestration/johnny_router_entry.py": b"# entry stub\n",
}


def _manifest() -> PayloadManifest:
    entries = tuple(
        PayloadManifestEntry(
            archive_relative_path=path,
            sha256=hashlib.sha256(content).hexdigest(),
            byte_length=len(content),
        )
        for path, content in sorted(_FILES.items())
    )
    return PayloadManifest(
        plugin_id="johnny-ai-skill",
        plugin_version="0.4.0",
        source_commit="a" * 40,
        dependency_lock_digest=build_approved_runtime_lock().lock_digest,
        entries=entries,
    )


def _write_bundle(
    path: Path,
    tamper_path: str | None = None,
    extra_path: str | None = None,
) -> PayloadManifest:
    manifest = _manifest()
    with zipfile.ZipFile(path, "w") as archive:
        for relative, content in _FILES.items():
            payload = b"tampered!" if relative == tamper_path else content
            archive.writestr(relative, payload)
        if extra_path is not None:
            archive.writestr(extra_path, b"foreign")
        archive.writestr("payload-manifest.json", manifest.canonical_json())
    return manifest


class RealPluginPayloadEffectPortTests(unittest.TestCase):
    def test_verified_bundle_extracts_exactly(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            bundle = base / "bundle.zip"
            manifest = _write_bundle(bundle)
            layout = JohnnyRootLayout(base=base / "jr")
            port = RealPluginPayloadEffectPort(layout, bundle)

            outcome = port.install("attempt-l3-01", manifest)

            self.assertIs(outcome.status, InstallEffectOutcomeStatus.COMPLETED)
            self.assertEqual(outcome.receipt, "plugin")
            for relative, content in _FILES.items():
                extracted = layout.plugin_root.joinpath(*relative.split("/"))
                self.assertEqual(extracted.read_bytes(), content)
            self.assertTrue(
                (layout.plugin_root / "payload-manifest.json").is_file()
            )

    def test_tampered_content_is_hash_mismatch_with_no_residue(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            bundle = base / "bundle.zip"
            manifest = _write_bundle(bundle, tamper_path="AGENTS.md")
            layout = JohnnyRootLayout(base=base / "jr")
            port = RealPluginPayloadEffectPort(layout, bundle)

            outcome = port.install("attempt-l3-02", manifest)

            self.assertIs(outcome.status, InstallEffectOutcomeStatus.HASH_MISMATCH)
            self.assertFalse(layout.plugin_root.exists())

    def test_foreign_archive_path_is_refused_before_extraction(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            bundle = base / "bundle.zip"
            manifest = _write_bundle(bundle, extra_path="library/foreign.py")
            layout = JohnnyRootLayout(base=base / "jr")
            port = RealPluginPayloadEffectPort(layout, bundle)

            outcome = port.install("attempt-l3-03", manifest)

            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertFalse(layout.plugin_root.exists())

    def test_populated_plugin_root_and_missing_bundle_are_unavailable(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            layout = JohnnyRootLayout(base=base / "jr")
            with self.subTest(case="populated_root"):
                bundle = base / "bundle.zip"
                manifest = _write_bundle(bundle)
                layout.plugin_root.mkdir(parents=True)
                keep = layout.plugin_root / "foreign.txt"
                keep.write_text("keep", encoding="utf-8")
                port = RealPluginPayloadEffectPort(layout, bundle)
                outcome = port.install("attempt-l3-04", manifest)
                self.assertIs(
                    outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE
                )
                self.assertTrue(keep.exists())
                keep.unlink()
                layout.plugin_root.rmdir()
            with self.subTest(case="missing_bundle"):
                port = RealPluginPayloadEffectPort(layout, base / "absent.zip")
                outcome = port.install("attempt-l3-05", _manifest())
                self.assertIs(
                    outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE
                )

    def test_remove_is_receipt_bound_and_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            layout = JohnnyRootLayout(base=base / "jr")
            port = RealPluginPayloadEffectPort(layout, base / "bundle.zip")
            self.assertFalse(port.remove("venv"))
            self.assertTrue(port.remove("plugin"))
            layout.plugin_root.mkdir(parents=True)
            (layout.plugin_root / "x.txt").write_text("x", encoding="utf-8")
            self.assertTrue(port.remove("plugin"))
            self.assertFalse(layout.plugin_root.exists())


class RealLauncherEffectPortTests(unittest.TestCase):
    def _prepare_payload(self, layout: JohnnyRootLayout) -> None:
        for relative, content in _FILES.items():
            target = layout.plugin_root.joinpath(*relative.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

    def test_launcher_and_entry_copy_from_verified_payload(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            self._prepare_payload(layout)
            port = RealLauncherEffectPort(layout)

            outcome = port.create("attempt-l3-06")

            self.assertIs(outcome.status, InstallEffectOutcomeStatus.COMPLETED)
            self.assertEqual(outcome.receipt, "launcher")
            self.assertEqual(
                (layout.launcher_root / "johnny-router.ps1").read_bytes(),
                _FILES["johnny-router.ps1"],
            )
            self.assertEqual(
                layout.runtime_entry.read_bytes(),
                _FILES["library/local_orchestration/johnny_router_entry.py"],
            )

    def test_missing_payload_sources_are_unavailable(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            port = RealLauncherEffectPort(layout)
            outcome = port.create("attempt-l3-07")
            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertFalse(layout.launcher_root.exists())
            self.assertFalse(layout.runtime_root.exists())

    def test_remove_clears_both_owned_directories(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            self._prepare_payload(layout)
            port = RealLauncherEffectPort(layout)
            self.assertIs(
                port.create("attempt-l3-08").status,
                InstallEffectOutcomeStatus.COMPLETED,
            )
            self.assertFalse(port.remove("plugin"))
            self.assertTrue(port.remove("launcher"))
            self.assertFalse(layout.launcher_root.exists())
            self.assertFalse(layout.runtime_root.exists())
            self.assertTrue(port.remove("launcher"))


if __name__ == "__main__":
    unittest.main()
