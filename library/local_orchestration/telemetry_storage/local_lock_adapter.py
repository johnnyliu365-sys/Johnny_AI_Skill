"""Local, bounded implementation of the telemetry-storage lock port."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from library.local_orchestration.file_lock import (
    ExclusiveFileLock,
    FileLockAcquireDecision,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.path_containment import resolves_within_root

from .contracts import (
    TelemetryStorageLockAcquired,
    TelemetryStorageLockContended,
    TelemetryStorageLockPort,
    TelemetryStorageLockRelease,
    TelemetryStorageLockReleaseFailed,
    TelemetryStorageLockReleased,
    TelemetryStorageLockRequest,
    TelemetryStorageLockToken,
)


class TelemetryStorageLockAdapterError(RuntimeError):
    """A sanitized failure at the local lock boundary."""


_VERSION_LABEL = "telemetry-storage-lock-v1"
_BOUNDARY_ERROR = "telemetry lock boundary rejected"
_IO_ERROR = "telemetry lock unavailable"


class LocalTelemetryStorageLockAdapter(TelemetryStorageLockPort):
    """Bind the typed telemetry lock port to one Johnny root."""

    def __init__(self, layout: JohnnyRootLayout) -> None:
        if not isinstance(layout, JohnnyRootLayout):
            raise TypeError("layout must be JohnnyRootLayout")
        self._layout = layout
        self._held: dict[str, tuple[ExclusiveFileLock, TelemetryStorageLockToken]] = {}

    @staticmethod
    def _digest(
        storage_ref: str,
        project_id: str,
        stream_id: str,
        ownership_ledger_ref: str,
    ) -> str:
        identity = "\0".join(
            (_VERSION_LABEL, storage_ref, project_id, stream_id, ownership_ledger_ref)
        )
        return sha256(identity.encode("utf-8")).hexdigest()

    @classmethod
    def _request_digest(cls, request: TelemetryStorageLockRequest) -> str:
        storage_ref = request.storage_ref
        return cls._digest(
            storage_ref.storage_ref,
            storage_ref.project_id,
            storage_ref.stream_id,
            storage_ref.ownership_ledger_ref,
        )

    @classmethod
    def _token_digest(cls, token: TelemetryStorageLockToken) -> str:
        return cls._digest(
            token.storage_ref,
            token.project_id,
            token.stream_id,
            token.ownership_ledger_ref,
        )

    def _paths(self, digest: str) -> tuple[Path, Path, Path]:
        telemetry_root = self._layout.telemetry_root
        lock_root = telemetry_root / "storage-locks"
        lock_path = lock_root / f"{digest}.lock"
        return telemetry_root, lock_root, lock_path

    def _open_lock(self, digest: str) -> tuple[ExclusiveFileLock, FileLockAcquireDecision]:
        telemetry_root, lock_root, lock_path = self._paths(digest)
        try:
            within_root = resolves_within_root(lock_root, telemetry_root)
        except (OSError, RuntimeError):
            raise TelemetryStorageLockAdapterError(_BOUNDARY_ERROR) from None
        if not within_root:
            raise TelemetryStorageLockAdapterError(_BOUNDARY_ERROR)
        try:
            lock_root.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise TelemetryStorageLockAdapterError(_IO_ERROR) from None
        try:
            within_root = resolves_within_root(lock_path, telemetry_root)
        except (OSError, RuntimeError):
            raise TelemetryStorageLockAdapterError(_BOUNDARY_ERROR) from None
        if not within_root:
            raise TelemetryStorageLockAdapterError(_BOUNDARY_ERROR)
        try:
            lock = ExclusiveFileLock(lock_path)
            decision = lock.try_acquire()
        except OSError:
            raise TelemetryStorageLockAdapterError(_IO_ERROR) from None
        return lock, decision

    def try_acquire(
        self, request: TelemetryStorageLockRequest
    ) -> TelemetryStorageLockAcquired | TelemetryStorageLockContended:
        """Attempt one bounded, nonblocking lock acquisition."""

        digest = self._request_digest(request)
        lock_ref = f"lock-{digest}"
        if lock_ref in self._held:
            return TelemetryStorageLockContended(
                storage_ref=request.storage_ref.storage_ref,
                storage_revision=request.storage_ref.storage_revision,
                failure_ref=f"contended-{digest}",
            )
        lock, decision = self._open_lock(digest)
        if decision is FileLockAcquireDecision.CONTENDED:
            return TelemetryStorageLockContended(
                storage_ref=request.storage_ref.storage_ref,
                storage_revision=request.storage_ref.storage_revision,
                failure_ref=f"contended-{digest}",
            )
        token = TelemetryStorageLockToken(
            lock_ref=lock_ref,
            storage_ref=request.storage_ref.storage_ref,
            project_id=request.storage_ref.project_id,
            stream_id=request.storage_ref.stream_id,
            ownership_ledger_ref=request.storage_ref.ownership_ledger_ref,
            storage_revision=request.storage_ref.storage_revision,
        )
        acquired = TelemetryStorageLockAcquired(lock_token=token)
        # The contracts revalidate nested models and therefore construct a
        # fresh token. Retain and return that exact DTO object for identity
        # checked release; no reconstructed token can unlock this handle.
        returned_token = acquired.lock_token
        self._held[lock_ref] = (lock, returned_token)
        return acquired

    def release(self, token: TelemetryStorageLockToken) -> TelemetryStorageLockRelease:
        """Release only the exact token object issued by this adapter."""

        failure_ref = f"release-{self._token_digest(token)}"
        held = self._held.get(token.lock_ref)
        if held is None or held[1] is not token:
            return TelemetryStorageLockReleaseFailed(
                lock_ref=token.lock_ref,
                storage_ref=token.storage_ref,
                storage_revision=token.storage_revision,
                failure_ref=failure_ref,
            )
        lock = held[0]
        try:
            lock.release()
        except OSError:
            return TelemetryStorageLockReleaseFailed(
                lock_ref=token.lock_ref,
                storage_ref=token.storage_ref,
                storage_revision=token.storage_revision,
                failure_ref=failure_ref,
            )
        finally:
            self._held.pop(token.lock_ref, None)
        return TelemetryStorageLockReleased(
            lock_ref=token.lock_ref,
            storage_ref=token.storage_ref,
            storage_revision=token.storage_revision,
        )


__all__ = ["LocalTelemetryStorageLockAdapter", "TelemetryStorageLockAdapterError"]
