"""Disposable-copy harness for the scripted SourceProjectA package qualification.

Every write stays inside caller-supplied disposable directories. The original
Vita repository is only ever read through exact read-only Git queries.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

from library.local_orchestration.plugin_uninstall_transaction import (
    OwnedStateKind,
    OwnedStateRecord,
    PluginUninstallLedger,
    PluginUninstallPorts,
    UninstallLedgerReadResult,
    UninstallLedgerReadStatus,
    UninstallOwnershipProbe,
)
from library.local_orchestration.windows_package_manifest import PayloadManifest

_ORIGINAL_ENVIRONMENT_KEY = "JOHNNY_VITA_ORIGINAL"
_OWNED_MARKER_NAME = ".johnny-owned"
_LEDGER_FILE_NAME = "ledger.json"

_KIND_RECEIPTS: tuple[tuple[OwnedStateKind, str], ...] = (
    (OwnedStateKind.PLUGIN_PAYLOAD, "plugin"),
    (OwnedStateKind.VENV, "venv"),
    (OwnedStateKind.LAUNCHER, "launcher"),
    (OwnedStateKind.QUEUE, "queue"),
    (OwnedStateKind.TELEMETRY, "telemetry"),
)


def resolve_original_root() -> Path | None:
    """Resolve the read-only original repository from the explicit environment override."""

    override = os.environ.get(_ORIGINAL_ENVIRONMENT_KEY)
    if not override:
        return None
    candidate = Path(override)
    if candidate.is_dir() and (candidate / ".git").exists():
        return candidate
    return None


def _run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=False,
        capture_output=True,
        shell=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout.decode("utf-8", errors="replace")


@dataclass(frozen=True, slots=True)
class GitIdentity:
    """Metadata-only repository identity: HEAD plus a status digest."""

    head: str
    status_digest: str


def read_git_identity(root: Path) -> GitIdentity:
    """Read HEAD and a digest of the exact porcelain status; never any content."""

    head = _run_git(root, "rev-parse", "HEAD").strip()
    porcelain = _run_git(root, "status", "--porcelain")
    return GitIdentity(
        head=head,
        status_digest=hashlib.sha256(porcelain.encode("utf-8")).hexdigest(),
    )


def tree_digest(root: Path) -> str:
    """Digest every file path and byte in one disposable tree, in sorted order."""

    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\x1f")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\x1e")
    return digest.hexdigest()


def build_disposable_target(
    original: Path,
    destination: Path,
    *,
    max_file_bytes: int = 131072,
    max_total_bytes: int = 16 * 1024 * 1024,
) -> int:
    """Copy a bounded, deterministic subset of tracked files into a disposable target."""

    listing = _run_git(original, "ls-files", "-z")
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    total = 0
    for relative in sorted(entry for entry in listing.split("\x00") if entry):
        if "�" in relative:
            # Undecodable byte in the tracked name; skip it in the bounded copy.
            continue
        source = original.joinpath(*relative.split("/"))
        if not source.is_file():
            continue
        size = source.stat().st_size
        if size > max_file_bytes:
            continue
        if total + size > max_total_bytes:
            break
        target = destination.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied += 1
        total += size
    return copied


def delete_disposable_tree(root: Path) -> bool:
    """Delete one disposable tree completely, clearing read-only Git objects."""

    def _clear_read_only(
        function: object, path: str, excinfo: object
    ) -> None:
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path) if os.path.isfile(path) else os.rmdir(path)

    shutil.rmtree(root, onerror=_clear_read_only)
    return not root.exists()


def _owned_path(johnny_root: Path, receipt: str) -> Path:
    return johnny_root / receipt


def scripted_install(
    zip_path: Path,
    johnny_root: Path,
    manifest: PayloadManifest,
) -> tuple[PluginUninstallLedger, tuple[str, ...]]:
    """Install the candidate only into the Johnny-owned disposable root."""

    receipt_id = "receipt-vita-scripted-qualification-01"
    extracted: list[str] = []
    plugin_root = _owned_path(johnny_root, "plugin")
    allowed = {entry.archive_relative_path for entry in manifest.entries} | {
        "payload-manifest.json"
    }
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if name not in allowed:
                raise RuntimeError("bundle carries a non-manifest path")
            archive.extract(name, plugin_root)
            extracted.append(name)

    venv_root = _owned_path(johnny_root, "venv")
    venv_root.mkdir(parents=True, exist_ok=True)
    (venv_root / "pyvenv.cfg").write_text(
        "home = scripted-qualification\n", encoding="utf-8"
    )
    launcher_root = _owned_path(johnny_root, "launcher")
    launcher_root.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        plugin_root / "johnny-router.ps1", launcher_root / "johnny-router.ps1"
    )
    queue_root = _owned_path(johnny_root, "queue")
    queue_root.mkdir(parents=True, exist_ok=True)
    (queue_root / "queue.json").write_text("[]", encoding="utf-8")
    telemetry_root = _owned_path(johnny_root, "telemetry")
    telemetry_root.mkdir(parents=True, exist_ok=True)
    (telemetry_root / "evidence.jsonl").write_text("", encoding="utf-8")

    records = []
    for kind, receipt in _KIND_RECEIPTS:
        owned_root = _owned_path(johnny_root, receipt)
        (owned_root / _OWNED_MARKER_NAME).write_text(receipt_id, encoding="utf-8")
        records.append(OwnedStateRecord(kind=kind, receipt=receipt))
    ledger = PluginUninstallLedger(receipt_id=receipt_id, records=tuple(records))
    (johnny_root / _LEDGER_FILE_NAME).write_text(
        ledger.model_dump_json(), encoding="utf-8"
    )
    return ledger, tuple(extracted)


class _FsLedgerPort:
    def __init__(self, johnny_root: Path) -> None:
        self._path = johnny_root / _LEDGER_FILE_NAME

    def read(self) -> UninstallLedgerReadResult:
        if not self._path.is_file():
            return UninstallLedgerReadResult(
                status=UninstallLedgerReadStatus.ABSENT, ledger=None
            )
        ledger = PluginUninstallLedger.model_validate_json(
            self._path.read_text(encoding="utf-8")
        )
        return UninstallLedgerReadResult(
            status=UninstallLedgerReadStatus.PRESENT, ledger=ledger
        )

    def remove(self, receipt_id: str) -> bool:
        try:
            self._path.unlink()
        except OSError:
            return False
        return True


class _ScriptedShutdownPort:
    """Scripted qualification runs no live worker, so shutdown always completes."""

    def block(self, receipt_id: str) -> bool:
        return True

    def cancel_all(self, receipt_id: str) -> bool:
        return True

    def stop_all(self, receipt_id: str) -> bool:
        return True


class _FsOwnedStatePort:
    def __init__(self, johnny_root: Path, receipt_id: str) -> None:
        self._johnny_root = johnny_root
        self._receipt_id = receipt_id

    def probe(self, record: OwnedStateRecord) -> UninstallOwnershipProbe:
        owned_root = _owned_path(self._johnny_root, record.receipt)
        if not owned_root.exists():
            return UninstallOwnershipProbe.OWNED
        marker = owned_root / _OWNED_MARKER_NAME
        if not marker.is_file():
            return UninstallOwnershipProbe.FOREIGN
        if marker.read_text(encoding="utf-8") != self._receipt_id:
            return UninstallOwnershipProbe.FOREIGN
        return UninstallOwnershipProbe.OWNED

    def remove(self, record: OwnedStateRecord) -> bool:
        owned_root = _owned_path(self._johnny_root, record.receipt)
        if not owned_root.exists():
            return True
        try:
            shutil.rmtree(owned_root)
        except OSError:
            return False
        return True

    def has_owned_state(self, receipt_id: str) -> bool:
        for _, receipt in _KIND_RECEIPTS:
            marker = _owned_path(self._johnny_root, receipt) / _OWNED_MARKER_NAME
            if marker.is_file() and marker.read_text(encoding="utf-8") == receipt_id:
                return True
        return False


class _FsAbsencePort:
    def __init__(self, johnny_root: Path) -> None:
        self._johnny_root = johnny_root

    def verify_absent(self, record: OwnedStateRecord) -> bool:
        return not _owned_path(self._johnny_root, record.receipt).exists()


def build_uninstall_ports(
    johnny_root: Path, receipt_id: str
) -> PluginUninstallPorts:
    """Filesystem-backed uninstall ports scoped strictly to the disposable root."""

    shutdown = _ScriptedShutdownPort()
    return PluginUninstallPorts(
        ledger=_FsLedgerPort(johnny_root),
        work_admission=shutdown,
        subscriptions=shutdown,
        runners=shutdown,
        owned_state=_FsOwnedStatePort(johnny_root, receipt_id),
        absence=_FsAbsencePort(johnny_root),
    )
