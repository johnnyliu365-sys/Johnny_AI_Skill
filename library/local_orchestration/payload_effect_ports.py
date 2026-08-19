"""Real payload and launcher effect ports: digest-verified, receipt-bound.

The payload port extracts exactly the manifest-listed files after per-file
SHA-256 verification; the launcher port copies the launcher script and the
runtime entry out of the verified payload. Nothing else is written.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import zipfile
from pathlib import Path

from .johnny_root_layout import JohnnyRootLayout
from .plugin_install_transaction import (
    InstallEffectOutcome,
    InstallEffectOutcomeStatus,
)
from .windows_package_manifest import PayloadManifest

_PLUGIN_RECEIPT = "plugin"
_LAUNCHER_RECEIPT = "launcher"
_MANIFEST_NAME = "payload-manifest.json"
_LAUNCHER_SCRIPT = "johnny-router.ps1"
_ENTRY_RELATIVE = "library/local_orchestration/johnny_router_entry.py"


def _resolves_within_root(target: Path, base: Path) -> bool:
    """Reject a target whose own path or any ancestor redirects elsewhere.

    Checking only an existing leaf misses two cases: a not-yet-created leaf
    under a redirected parent, and a redirected ancestor above it. The nearest
    existing ancestor is therefore resolved and required to stay inside the
    resolved Johnny root, with the unresolved remainder appended unchanged.
    """

    try:
        resolved_base = base.resolve()
        existing = target
        remainder: list[str] = []
        while not existing.exists():
            if existing.parent == existing:
                return False
            remainder.append(existing.name)
            existing = existing.parent
        resolved = existing.resolve().joinpath(*reversed(remainder))
        return resolved == resolved_base or resolved_base in resolved.parents
    except OSError:
        return False


def _unavailable() -> InstallEffectOutcome:
    return InstallEffectOutcome(status=InstallEffectOutcomeStatus.UNAVAILABLE)


def _clear_read_only(function: object, path: str, excinfo: object) -> None:
    os.chmod(path, stat.S_IWRITE)
    if os.path.isfile(path):
        os.unlink(path)
    else:
        os.rmdir(path)


def _delete_tree(root: Path) -> bool:
    try:
        if root.exists():
            shutil.rmtree(root, onerror=_clear_read_only)
    except OSError:
        return False
    return not root.exists()


class RealPluginPayloadEffectPort:
    """Extract exactly the verified bundle payload into the owned plugin root."""

    def __init__(self, layout: JohnnyRootLayout, bundle_zip: Path) -> None:
        self._layout = layout
        self._bundle_zip = bundle_zip

    def install(
        self, attempt_id: str, manifest: PayloadManifest
    ) -> InstallEffectOutcome:
        plugin_root = self._layout.plugin_root
        if plugin_root.exists() and any(plugin_root.iterdir()):
            return _unavailable()
        if not _resolves_within_root(plugin_root, self._layout.base):
            return _unavailable()

        expected = {
            entry.archive_relative_path: entry for entry in manifest.entries
        }
        try:
            with zipfile.ZipFile(self._bundle_zip) as archive:
                names = set(archive.namelist())
                if names != set(expected) | {_MANIFEST_NAME}:
                    # Foreign or missing archive paths are never extracted.
                    return _unavailable()
                for relative_path, entry in expected.items():
                    payload = archive.read(relative_path)
                    if (
                        len(payload) != entry.byte_length
                        or hashlib.sha256(payload).hexdigest() != entry.sha256
                    ):
                        _delete_tree(plugin_root)
                        return InstallEffectOutcome(
                            status=InstallEffectOutcomeStatus.HASH_MISMATCH
                        )
                    target = plugin_root.joinpath(*relative_path.split("/"))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(payload)
                manifest_bytes = archive.read(_MANIFEST_NAME)
                (plugin_root / _MANIFEST_NAME).write_bytes(manifest_bytes)
        except (OSError, ValueError, zipfile.BadZipFile, KeyError):
            _delete_tree(plugin_root)
            return _unavailable()
        return InstallEffectOutcome(
            status=InstallEffectOutcomeStatus.COMPLETED, receipt=_PLUGIN_RECEIPT
        )

    def remove(self, receipt: str) -> bool:
        if receipt != _PLUGIN_RECEIPT:
            return False
        return _delete_tree(self._layout.plugin_root)


class RealLauncherEffectPort:
    """Copy the launcher script and runtime entry out of the verified payload."""

    def __init__(self, layout: JohnnyRootLayout) -> None:
        self._layout = layout

    def create(self, attempt_id: str) -> InstallEffectOutcome:
        plugin_root = self._layout.plugin_root
        launcher_source = plugin_root / _LAUNCHER_SCRIPT
        entry_source = plugin_root.joinpath(*_ENTRY_RELATIVE.split("/"))
        if not launcher_source.is_file() or not entry_source.is_file():
            return _unavailable()
        launcher_root = self._layout.launcher_root
        runtime_root = self._layout.runtime_root
        for owned_root in (launcher_root, runtime_root):
            if owned_root.exists() and any(owned_root.iterdir()):
                return _unavailable()
            if not _resolves_within_root(owned_root, self._layout.base):
                return _unavailable()
        try:
            launcher_root.mkdir(parents=True, exist_ok=True)
            runtime_root.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(launcher_source, launcher_root / _LAUNCHER_SCRIPT)
            shutil.copyfile(entry_source, self._layout.runtime_entry)
        except OSError:
            _delete_tree(launcher_root)
            _delete_tree(runtime_root)
            return _unavailable()
        return InstallEffectOutcome(
            status=InstallEffectOutcomeStatus.COMPLETED, receipt=_LAUNCHER_RECEIPT
        )

    def remove(self, receipt: str) -> bool:
        if receipt != _LAUNCHER_RECEIPT:
            return False
        launcher_cleared = _delete_tree(self._layout.launcher_root)
        runtime_cleared = _delete_tree(self._layout.runtime_root)
        return launcher_cleared and runtime_cleared


__all__ = ["RealLauncherEffectPort", "RealPluginPayloadEffectPort"]
