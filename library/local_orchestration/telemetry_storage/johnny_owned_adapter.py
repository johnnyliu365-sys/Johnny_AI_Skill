"""Private lock-bound transaction adapter for owned metadata-only telemetry."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, NamedTuple, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.path_containment import resolves_within_root
from library.local_orchestration.telemetry_storage.contracts import (
    AppendTelemetryStorageRequest,
    CompletedAppendResponse,
    CompletedDetachResponse,
    CompletedReadResponse,
    CompletedUninstallResponse,
    CompletedValidateResponse,
    NoRecordTelemetryStorageRequest,
    TelemetryStorageDecision,
    TelemetryStorageFailure,
    TelemetryStorageLifecycle,
    TelemetryStorageLockAcquired,
    TelemetryStorageLockContended,
    TelemetryStorageLockPort,
    TelemetryStorageLockReleased,
    TelemetryStorageLockRequest,
    TelemetryStorageLockToken,
    TelemetryStorageOperation,
    TelemetryStoragePort,
    TelemetryStorageReadPayload,
    TelemetryStorageRef,
    TelemetryStorageRequest,
    TelemetryStorageResponse,
)
from library.local_orchestration.telemetry_storage.ownership_ledger import (
    TelemetryOwnershipLedgerClosed,
    TelemetryOwnershipLedgerEntry,
    TelemetryOwnershipLedgerFound,
    TelemetryOwnershipLedgerNotFound,
    TelemetryOwnershipLedgerOwnershipMismatch,
    TelemetryOwnershipLedgerPort,
    TelemetryOwnershipLedgerResult,
)
from library.workflow_router.contracts import OpaqueMetadataId, RevisionDigest
from library.workflow_router.telemetry import (
    ContextUsageRecord,
    ContextUsageValidator,
    JsonlContextUsageStore,
    NonNegativeCount,
)


_RelativeLocator = Annotated[str, Field(min_length=1, max_length=512)]
_Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class _TransactionPhase(str, Enum):
    PREPARED = "PREPARED"
    STREAM_APPLIED = "STREAM_APPLIED"
    LEDGER_APPLIED = "LEDGER_APPLIED"


class _AdapterModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class _TransactionJournal(_AdapterModel):
    """The complete private state needed to recover one mutation."""

    schema_version: Literal[1]
    storage_ref: TelemetryStorageRef
    operation: TelemetryStorageOperation
    expected_storage_revision: RevisionDigest
    next_storage_revision: RevisionDigest
    pre_lifecycle: TelemetryStorageLifecycle
    post_lifecycle: TelemetryStorageLifecycle
    stream_locator: _RelativeLocator
    pre_exists: bool
    post_exists: bool
    pre_sha256: _Digest
    post_sha256: _Digest
    pre_record_count: NonNegativeCount
    post_record_count: NonNegativeCount
    phase: _TransactionPhase

    @model_validator(mode="after")
    def locator_is_relative(self) -> Self:
        pieces = self.stream_locator.replace("\\", "/").split("/")
        if (
            self.stream_locator.startswith(("/", "\\"))
            or ":" in self.stream_locator
            or any(piece in ("", ".", "..") for piece in pieces)
        ):
            raise ValueError("stream locator must be relative")
        return self


class _StreamState(NamedTuple):
    exists: bool
    raw: bytes
    records: tuple[ContextUsageRecord, ...]


class _SnapshotState(NamedTuple):
    exists: bool
    raw: bytes
    records: tuple[ContextUsageRecord, ...]


class _TransactionPaths(NamedTuple):
    telemetry_root: Path
    transaction_root: Path
    transaction_directory: Path
    journal_path: Path
    pre_snapshot_path: Path
    post_snapshot_path: Path
    stream_path: Path
    legacy_aggregate_path: Path


class _TransactionBoundaryViolation(Exception):
    """Internal failure marker that carries no user-visible detail."""


class _InvalidTelemetryRecord(Exception):
    """Internal marker for a stream that fails strict record decoding."""


class JohnnyOwnedTelemetryStorageAdapter(TelemetryStoragePort):
    """Execute owned telemetry operations while retaining one exact lock."""

    def __init__(
        self,
        layout: JohnnyRootLayout,
        ledger: TelemetryOwnershipLedgerPort,
        lock: TelemetryStorageLockPort,
    ) -> None:
        if not isinstance(layout, JohnnyRootLayout):
            raise TypeError("layout must be JohnnyRootLayout")
        if not isinstance(ledger, TelemetryOwnershipLedgerPort):
            raise TypeError("ledger must implement TelemetryOwnershipLedgerPort")
        if not isinstance(lock, TelemetryStorageLockPort):
            raise TypeError("lock must implement TelemetryStorageLockPort")
        self._layout = layout
        self._ledger = ledger
        self._lock = lock

    @staticmethod
    def _identity_digest(storage_ref: TelemetryStorageRef) -> str:
        identity = "\0".join(
            (
                storage_ref.storage_ref,
                storage_ref.project_id,
                storage_ref.stream_id,
                storage_ref.ownership_ledger_ref,
            )
        )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    @staticmethod
    def _relative_locator_is_safe(locator: str) -> bool:
        pieces = locator.replace("\\", "/").split("/")
        return not (
            locator.startswith(("/", "\\"))
            or ":" in locator
            or any(piece in ("", ".", "..") for piece in pieces)
        )

    def _base_paths(self, storage_ref: TelemetryStorageRef) -> tuple[Path, ...]:
        telemetry_root = self._layout.telemetry_root
        transaction_root = telemetry_root / "storage-transactions"
        transaction_directory = transaction_root / self._identity_digest(storage_ref)
        journal_path = transaction_directory / "journal.json"
        pre_snapshot_path = transaction_directory / "pre.stream"
        post_snapshot_path = transaction_directory / "post.stream"
        legacy_aggregate_path = telemetry_root / "ownership-ledger" / "ledger.json"
        return (
            telemetry_root,
            transaction_root,
            transaction_directory,
            journal_path,
            pre_snapshot_path,
            post_snapshot_path,
            legacy_aggregate_path,
        )

    def _paths(
        self, storage_ref: TelemetryStorageRef, stream_locator: str
    ) -> _TransactionPaths:
        if not self._relative_locator_is_safe(stream_locator):
            raise _TransactionBoundaryViolation
        base = self._base_paths(storage_ref)
        return _TransactionPaths(
            telemetry_root=base[0],
            transaction_root=base[1],
            transaction_directory=base[2],
            journal_path=base[3],
            pre_snapshot_path=base[4],
            post_snapshot_path=base[5],
            stream_path=base[0] / stream_locator,
            legacy_aggregate_path=base[6],
        )

    @staticmethod
    def _paths_are_owned(paths: tuple[Path, ...], telemetry_root: Path) -> bool:
        try:
            checks = tuple(
                resolves_within_root(path, telemetry_root) for path in paths
            )
        except (OSError, RuntimeError):
            return False
        return all(checks)

    @staticmethod
    def _legacy_present(path: Path) -> bool:
        try:
            path.lstat()
        except FileNotFoundError:
            return False
        except OSError:
            raise _TransactionBoundaryViolation from None
        return True

    def _ensure_paths_owned(self, paths: _TransactionPaths) -> None:
        path_values = (
            paths.telemetry_root,
            paths.transaction_root,
            paths.transaction_directory,
            paths.journal_path,
            paths.pre_snapshot_path,
            paths.post_snapshot_path,
            paths.stream_path,
            paths.legacy_aggregate_path,
        )
        if not self._paths_are_owned(path_values, paths.telemetry_root):
            raise _TransactionBoundaryViolation
        if self._legacy_present(paths.legacy_aggregate_path):
            raise _TransactionBoundaryViolation

    @staticmethod
    def _failure_ref(
        request: TelemetryStorageRequest, prefix: str
    ) -> OpaqueMetadataId:
        return f"{prefix}-{JohnnyOwnedTelemetryStorageAdapter._identity_digest(request.storage_ref)[:32]}"

    @staticmethod
    def _failure(
        request: TelemetryStorageRequest,
        decision: TelemetryStorageDecision,
        failure_ref: OpaqueMetadataId | None = None,
    ) -> TelemetryStorageFailure:
        prefix = {
            TelemetryStorageDecision.STORAGE_OWNERSHIP_MISMATCH: "ownership-mismatch",
            TelemetryStorageDecision.STORAGE_CLOSED: "storage-closed",
            TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION: "storage-boundary",
            TelemetryStorageDecision.RECORD_INVALID: "record-invalid",
            TelemetryStorageDecision.LOCK_CONTENDED: "lock-contended",
        }[decision]
        return TelemetryStorageFailure(
            storage_ref=request.storage_ref.storage_ref,
            storage_revision=request.expected_storage_revision,
            operation=request.operation,
            decision=decision,
            failure_ref=failure_ref or JohnnyOwnedTelemetryStorageAdapter._failure_ref(request, prefix),
        )

    @staticmethod
    def _ledger_failure(
        request: TelemetryStorageRequest,
        result: TelemetryOwnershipLedgerResult,
    ) -> TelemetryStorageFailure:
        if isinstance(result, TelemetryOwnershipLedgerClosed):
            return JohnnyOwnedTelemetryStorageAdapter._failure(
                request, TelemetryStorageDecision.STORAGE_CLOSED
            )
        if isinstance(result, TelemetryOwnershipLedgerOwnershipMismatch) or isinstance(
            result, TelemetryOwnershipLedgerNotFound
        ):
            return JohnnyOwnedTelemetryStorageAdapter._failure(
                request, TelemetryStorageDecision.STORAGE_OWNERSHIP_MISMATCH
            )
        return JohnnyOwnedTelemetryStorageAdapter._failure(
            request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION
        )

    @staticmethod
    def _ledger_entry(
        request: TelemetryStorageRequest,
        result: TelemetryOwnershipLedgerResult,
    ) -> tuple[TelemetryOwnershipLedgerEntry | None, TelemetryStorageFailure | None]:
        if isinstance(result, TelemetryOwnershipLedgerFound):
            return result.entry, None
        return None, JohnnyOwnedTelemetryStorageAdapter._ledger_failure(request, result)

    @staticmethod
    def _entry_matches_request(
        entry: TelemetryOwnershipLedgerEntry,
        request: TelemetryStorageRequest,
    ) -> bool:
        current = entry.storage_ref
        requested = request.storage_ref
        return (
            current.storage_ref == requested.storage_ref
            and current.project_id == requested.project_id
            and current.stream_id == requested.stream_id
            and current.ownership_ledger_ref == requested.ownership_ledger_ref
            and current.storage_revision == request.expected_storage_revision
            and current.lifecycle is TelemetryStorageLifecycle.ACTIVE
            and requested.storage_revision == request.expected_storage_revision
            and requested.lifecycle is TelemetryStorageLifecycle.ACTIVE
            and request.expected_project_id == requested.project_id
        )

    @staticmethod
    def _lock_token_matches(
        token: TelemetryStorageLockToken,
        request: TelemetryStorageRequest,
    ) -> bool:
        requested = request.storage_ref
        return (
            token.storage_ref == requested.storage_ref
            and token.project_id == requested.project_id
            and token.stream_id == requested.stream_id
            and token.ownership_ledger_ref == requested.ownership_ledger_ref
            and token.storage_revision == request.expected_storage_revision
        )

    def _atomic_write_bytes(
        self, target: Path, telemetry_root: Path, raw: bytes
    ) -> None:
        temporary_hint = target.with_name(f".{target.name}.tmp")
        if not self._paths_are_owned(
            (telemetry_root, target.parent, target, temporary_hint), telemetry_root
        ):
            raise _TransactionBoundaryViolation
        temporary_path: Path | None = None
        descriptor = -1
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{target.stem}-", suffix=".tmp", dir=str(target.parent)
            )
            temporary_path = Path(temporary_name)
            if not resolves_within_root(temporary_path, telemetry_root):
                raise _TransactionBoundaryViolation
            os.close(descriptor)
            descriptor = -1
            temporary_path.write_bytes(raw)
            with temporary_path.open("r+b") as handle:
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, target)
        except (OSError, TypeError, ValueError):
            raise _TransactionBoundaryViolation from None
        except _TransactionBoundaryViolation:
            raise
        finally:
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except (FileNotFoundError, OSError):
                    pass

    def _read_stream(
        self, paths: _TransactionPaths
    ) -> _StreamState:
        try:
            records = JsonlContextUsageStore.read(path=paths.stream_path)
            raw = paths.stream_path.read_bytes()
        except FileNotFoundError:
            return _StreamState(False, b"", ())
        except (OSError, TypeError):
            raise _TransactionBoundaryViolation from None
        except ValueError:
            raise _InvalidTelemetryRecord from None
        return _StreamState(True, raw, records)

    @staticmethod
    def _canonical_records(records: tuple[ContextUsageRecord, ...]) -> bytes:
        if not records:
            return b""
        lines = tuple(
            json.dumps(
                record.model_dump(mode="json"),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            for record in records
        )
        return ("\n".join(lines) + "\n").encode("utf-8")

    @staticmethod
    def _snapshot_digest(raw: bytes) -> str:
        return hashlib.sha256(raw).hexdigest()

    def _write_snapshot(
        self, path: Path, telemetry_root: Path, state: _StreamState
    ) -> None:
        if state.exists:
            self._atomic_write_bytes(path, telemetry_root, state.raw)
            return
        self._remove_file(path, telemetry_root)

    @staticmethod
    def _remove_file(path: Path, telemetry_root: Path) -> None:
        try:
            if not resolves_within_root(path, telemetry_root):
                raise _TransactionBoundaryViolation
            path.unlink(missing_ok=True)
        except (OSError, RuntimeError):
            raise _TransactionBoundaryViolation from None

    def _write_journal(self, journal: _TransactionJournal) -> None:
        paths = self._base_paths(journal.storage_ref)
        if not self._paths_are_owned(paths, paths[0]):
            raise _TransactionBoundaryViolation
        if self._legacy_present(paths[6]):
            raise _TransactionBoundaryViolation
        raw = (
            json.dumps(
                journal.model_dump(mode="json"),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        self._atomic_write_bytes(paths[3], paths[0], raw)

    @staticmethod
    def _with_phase(
        journal: _TransactionJournal, phase: _TransactionPhase
    ) -> _TransactionJournal:
        return _TransactionJournal(
            schema_version=1,
            storage_ref=journal.storage_ref,
            operation=journal.operation,
            expected_storage_revision=journal.expected_storage_revision,
            next_storage_revision=journal.next_storage_revision,
            pre_lifecycle=journal.pre_lifecycle,
            post_lifecycle=journal.post_lifecycle,
            stream_locator=journal.stream_locator,
            pre_exists=journal.pre_exists,
            post_exists=journal.post_exists,
            pre_sha256=journal.pre_sha256,
            post_sha256=journal.post_sha256,
            pre_record_count=journal.pre_record_count,
            post_record_count=journal.post_record_count,
            phase=phase,
        )

    @staticmethod
    def _revision(
        storage_ref: TelemetryStorageRef,
        expected_revision: RevisionDigest,
        operation: TelemetryStorageOperation,
        post_lifecycle: TelemetryStorageLifecycle,
        stream_locator: str,
        pre_sha256: str,
        post_sha256: str,
    ) -> RevisionDigest:
        locator_sha256 = hashlib.sha256(stream_locator.encode("utf-8")).hexdigest()
        material = "\0".join(
            (
                "telemetry-storage-revision-v1",
                storage_ref.storage_ref,
                storage_ref.project_id,
                storage_ref.stream_id,
                storage_ref.ownership_ledger_ref,
                expected_revision,
                operation.value,
                post_lifecycle.value,
                locator_sha256,
                pre_sha256,
                post_sha256,
            )
        )
        return f"rev-{hashlib.sha256(material.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _report_ref(
        storage_ref: TelemetryStorageRef,
        current_revision: RevisionDigest,
        report_json: str,
    ) -> OpaqueMetadataId:
        identity = "\0".join(
            (
                storage_ref.storage_ref,
                storage_ref.project_id,
                storage_ref.stream_id,
                storage_ref.ownership_ledger_ref,
            )
        )
        material = "\0".join((identity, current_revision, report_json))
        return f"validation-{hashlib.sha256(material.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _journal_is_owned(
        journal: _TransactionJournal,
        request: TelemetryStorageRequest,
        entry: TelemetryOwnershipLedgerEntry,
    ) -> bool:
        return (
            journal.storage_ref.storage_ref == request.storage_ref.storage_ref
            and journal.storage_ref.project_id == request.storage_ref.project_id
            and journal.storage_ref.stream_id == request.storage_ref.stream_id
            and journal.storage_ref.ownership_ledger_ref == request.storage_ref.ownership_ledger_ref
            and journal.storage_ref.storage_revision == journal.expected_storage_revision
            and journal.storage_ref.lifecycle is journal.pre_lifecycle
            and journal.stream_locator == entry.stream_locator
            and journal.operation
            in (
                TelemetryStorageOperation.APPEND,
                TelemetryStorageOperation.DETACH,
                TelemetryStorageOperation.UNINSTALL,
            )
        )

    def _read_snapshot(
        self,
        path: Path,
        telemetry_root: Path,
        expected_exists: bool,
        expected_sha256: str,
        expected_count: int,
    ) -> _SnapshotState:
        try:
            exists = path.exists() or path.is_symlink()
        except OSError:
            raise _TransactionBoundaryViolation from None
        if not expected_exists:
            if exists:
                raise _TransactionBoundaryViolation
            return _SnapshotState(False, b"", ())
        if not exists or not resolves_within_root(path, telemetry_root):
            raise _TransactionBoundaryViolation
        try:
            raw = path.read_bytes()
            records = JsonlContextUsageStore.read(path=path)
        except (OSError, TypeError, ValueError):
            raise _TransactionBoundaryViolation from None
        if self._snapshot_digest(raw) != expected_sha256 or len(records) != expected_count:
            raise _TransactionBoundaryViolation
        return _SnapshotState(True, raw, records)

    @staticmethod
    def _state_matches(
        state: _StreamState | _SnapshotState,
        expected_exists: bool,
        expected_sha256: str,
        expected_count: int,
    ) -> bool:
        if state.exists != expected_exists:
            return False
        if not expected_exists:
            return state.raw == b"" and not state.records
        return (
            hashlib.sha256(state.raw).hexdigest() == expected_sha256
            and len(state.records) == expected_count
        )

    def _cleanup_transaction(self, paths: _TransactionPaths) -> None:
        self._remove_file(paths.pre_snapshot_path, paths.telemetry_root)
        self._remove_file(paths.post_snapshot_path, paths.telemetry_root)
        try:
            paths.journal_path.unlink()
        except FileNotFoundError:
            raise _TransactionBoundaryViolation from None
        except OSError:
            raise _TransactionBoundaryViolation from None
        try:
            paths.transaction_directory.rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            pass
        try:
            paths.transaction_root.rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    def _discard_unjournaled(self, paths: _TransactionPaths) -> None:
        try:
            self._remove_file(paths.pre_snapshot_path, paths.telemetry_root)
            self._remove_file(paths.post_snapshot_path, paths.telemetry_root)
            paths.transaction_directory.rmdir()
        except _TransactionBoundaryViolation:
            return
        except OSError:
            return

    def _recover_pending(
        self,
        request: TelemetryStorageRequest,
        current_entry: TelemetryOwnershipLedgerEntry | None,
    ) -> None:
        base = self._base_paths(request.storage_ref)
        if not self._paths_are_owned(base, base[0]):
            raise _TransactionBoundaryViolation
        base_paths = _TransactionPaths(
            telemetry_root=base[0],
            transaction_root=base[1],
            transaction_directory=base[2],
            journal_path=base[3],
            pre_snapshot_path=base[4],
            post_snapshot_path=base[5],
            stream_path=base[0],
            legacy_aggregate_path=base[6],
        )
        try:
            journal_exists = base_paths.journal_path.exists() or base_paths.journal_path.is_symlink()
        except OSError:
            raise _TransactionBoundaryViolation from None
        if not journal_exists:
            try:
                transaction_directory_exists = (
                    base_paths.transaction_directory.exists()
                    or base_paths.transaction_directory.is_symlink()
                )
                snapshot_exists = (
                    base_paths.pre_snapshot_path.exists()
                    or base_paths.pre_snapshot_path.is_symlink()
                    or base_paths.post_snapshot_path.exists()
                    or base_paths.post_snapshot_path.is_symlink()
                )
            except OSError:
                raise _TransactionBoundaryViolation from None
            if transaction_directory_exists or snapshot_exists:
                raise _TransactionBoundaryViolation
            return
        if current_entry is None:
            raise _TransactionBoundaryViolation
        try:
            journal_text = base_paths.journal_path.read_text(encoding="utf-8")
            journal = _TransactionJournal.model_validate_json(journal_text)
        except (OSError, TypeError, ValueError):
            raise _TransactionBoundaryViolation from None
        if not self._journal_is_owned(journal, request, current_entry):
            raise _TransactionBoundaryViolation
        if (
            journal.pre_lifecycle is not TelemetryStorageLifecycle.ACTIVE
            or (
                journal.operation is TelemetryStorageOperation.APPEND
                and (
                    journal.post_lifecycle is not TelemetryStorageLifecycle.ACTIVE
                    or not journal.post_exists
                )
            )
            or (
                journal.operation is TelemetryStorageOperation.DETACH
                and (
                    journal.post_lifecycle is not TelemetryStorageLifecycle.DETACHED
                    or journal.post_exists
                )
            )
            or (
                journal.operation is TelemetryStorageOperation.UNINSTALL
                and (
                    journal.post_lifecycle is not TelemetryStorageLifecycle.REMOVED
                    or journal.post_exists
                )
            )
        ):
            raise _TransactionBoundaryViolation
        paths = self._paths(request.storage_ref, journal.stream_locator)
        if not self._paths_are_owned(
            (
                paths.telemetry_root,
                paths.transaction_root,
                paths.transaction_directory,
                paths.journal_path,
                paths.pre_snapshot_path,
                paths.post_snapshot_path,
                paths.stream_path,
                paths.legacy_aggregate_path,
            ),
            paths.telemetry_root,
        ):
            raise _TransactionBoundaryViolation
        if self._legacy_present(paths.legacy_aggregate_path):
            raise _TransactionBoundaryViolation
        pre = self._read_snapshot(
            paths.pre_snapshot_path,
            paths.telemetry_root,
            journal.pre_exists,
            journal.pre_sha256,
            journal.pre_record_count,
        )
        post = self._read_snapshot(
            paths.post_snapshot_path,
            paths.telemetry_root,
            journal.post_exists,
            journal.post_sha256,
            journal.post_record_count,
        )
        stream = self._read_stream(paths)
        stream_pre = self._state_matches(
            stream,
            journal.pre_exists,
            journal.pre_sha256,
            journal.pre_record_count,
        )
        stream_post = self._state_matches(
            stream,
            journal.post_exists,
            journal.post_sha256,
            journal.post_record_count,
        )
        ledger_pre = (
            current_entry.storage_ref.storage_revision == journal.expected_storage_revision
            and current_entry.storage_ref.lifecycle is journal.pre_lifecycle
        )
        ledger_post = (
            current_entry.storage_ref.storage_revision == journal.next_storage_revision
            and current_entry.storage_ref.lifecycle is journal.post_lifecycle
        )
        restore_pre = (
            journal.phase is _TransactionPhase.PREPARED and stream_post and ledger_pre
        ) or (
            journal.phase is _TransactionPhase.STREAM_APPLIED and stream_post and ledger_pre
        )
        retain_post = (
            journal.phase is _TransactionPhase.STREAM_APPLIED and stream_post and ledger_post
        ) or (
            journal.phase is _TransactionPhase.LEDGER_APPLIED and stream_post and ledger_post
        )
        retain_pre = journal.phase is _TransactionPhase.PREPARED and stream_pre and ledger_pre
        if not (restore_pre or retain_post or retain_pre):
            raise _TransactionBoundaryViolation
        if restore_pre:
            if pre.exists:
                self._atomic_write_bytes(paths.stream_path, paths.telemetry_root, pre.raw)
            else:
                self._remove_file(paths.stream_path, paths.telemetry_root)
        self._cleanup_transaction(paths)

    def _apply_stream(
        self, paths: _TransactionPaths, post: _StreamState
    ) -> None:
        if post.exists:
            self._atomic_write_bytes(paths.stream_path, paths.telemetry_root, post.raw)
        else:
            self._remove_file(paths.stream_path, paths.telemetry_root)

    def _prepare_transaction(
        self,
        request: TelemetryStorageRequest,
        entry: TelemetryOwnershipLedgerEntry,
        pre: _StreamState,
        post: _StreamState,
        next_revision: RevisionDigest,
        post_lifecycle: TelemetryStorageLifecycle,
    ) -> tuple[_TransactionPaths, _TransactionJournal]:
        paths = self._paths(request.storage_ref, entry.stream_locator)
        path_values = (
            paths.telemetry_root,
            paths.transaction_root,
            paths.transaction_directory,
            paths.journal_path,
            paths.pre_snapshot_path,
            paths.post_snapshot_path,
            paths.stream_path,
            paths.legacy_aggregate_path,
        )
        if not self._paths_are_owned(path_values, paths.telemetry_root):
            raise _TransactionBoundaryViolation
        if self._legacy_present(paths.legacy_aggregate_path):
            raise _TransactionBoundaryViolation
        try:
            paths.transaction_directory.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise _TransactionBoundaryViolation from None
        journal = _TransactionJournal(
            schema_version=1,
            storage_ref=request.storage_ref,
            operation=request.operation,
            expected_storage_revision=request.expected_storage_revision,
            next_storage_revision=next_revision,
            pre_lifecycle=entry.storage_ref.lifecycle,
            post_lifecycle=post_lifecycle,
            stream_locator=entry.stream_locator,
            pre_exists=pre.exists,
            post_exists=post.exists,
            pre_sha256=self._snapshot_digest(pre.raw),
            post_sha256=self._snapshot_digest(post.raw),
            pre_record_count=len(pre.records),
            post_record_count=len(post.records),
            phase=_TransactionPhase.PREPARED,
        )
        try:
            self._write_snapshot(paths.pre_snapshot_path, paths.telemetry_root, pre)
            self._write_snapshot(paths.post_snapshot_path, paths.telemetry_root, post)
            self._write_journal(journal)
        except Exception:
            self._discard_unjournaled(paths)
            raise _TransactionBoundaryViolation from None
        return paths, journal

    def _execute_append(
        self,
        request: AppendTelemetryStorageRequest,
        entry: TelemetryOwnershipLedgerEntry,
    ) -> TelemetryStorageResponse:
        paths = self._paths(request.storage_ref, entry.stream_locator)
        self._ensure_paths_owned(paths)
        pre = self._read_stream(paths)
        post_records = pre.records + (request.record,)
        post = _StreamState(True, self._canonical_records(post_records), post_records)
        next_revision = self._revision(
            request.storage_ref,
            request.expected_storage_revision,
            request.operation,
            TelemetryStorageLifecycle.ACTIVE,
            entry.stream_locator,
            self._snapshot_digest(pre.raw),
            self._snapshot_digest(post.raw),
        )
        transaction_paths, journal = self._prepare_transaction(
            request,
            entry,
            pre,
            post,
            next_revision,
            TelemetryStorageLifecycle.ACTIVE,
        )
        self._apply_stream(transaction_paths, post)
        self._write_journal(self._with_phase(journal, _TransactionPhase.STREAM_APPLIED))
        ledger_result = self._ledger.compare_and_swap(
            request.storage_ref,
            request.expected_project_id,
            request.expected_storage_revision,
            TelemetryStorageLifecycle.ACTIVE,
            next_revision,
        )
        if not isinstance(ledger_result, TelemetryOwnershipLedgerFound):
            raise _TransactionBoundaryViolation
        if (
            ledger_result.entry.stream_locator != entry.stream_locator
            or ledger_result.entry.storage_ref.storage_ref != request.storage_ref.storage_ref
            or ledger_result.entry.storage_ref.project_id != request.storage_ref.project_id
            or ledger_result.entry.storage_ref.stream_id != request.storage_ref.stream_id
            or ledger_result.entry.storage_ref.ownership_ledger_ref
            != request.storage_ref.ownership_ledger_ref
            or ledger_result.entry.storage_ref.storage_revision != next_revision
            or ledger_result.entry.storage_ref.lifecycle is not TelemetryStorageLifecycle.ACTIVE
        ):
            raise _TransactionBoundaryViolation
        self._write_journal(self._with_phase(journal, _TransactionPhase.LEDGER_APPLIED))
        self._cleanup_transaction(transaction_paths)
        return CompletedAppendResponse(
            storage_ref=request.storage_ref.storage_ref,
            storage_revision=next_revision,
            record_count=len(post_records),
        )

    def _execute_remove(
        self,
        request: NoRecordTelemetryStorageRequest,
        entry: TelemetryOwnershipLedgerEntry,
        lifecycle: TelemetryStorageLifecycle,
    ) -> TelemetryStorageResponse:
        paths = self._paths(request.storage_ref, entry.stream_locator)
        self._ensure_paths_owned(paths)
        pre = self._read_stream(paths)
        post = _StreamState(False, b"", ())
        next_revision = self._revision(
            request.storage_ref,
            request.expected_storage_revision,
            request.operation,
            lifecycle,
            entry.stream_locator,
            self._snapshot_digest(pre.raw),
            self._snapshot_digest(post.raw),
        )
        transaction_paths, journal = self._prepare_transaction(
            request, entry, pre, post, next_revision, lifecycle
        )
        self._apply_stream(transaction_paths, post)
        self._write_journal(self._with_phase(journal, _TransactionPhase.STREAM_APPLIED))
        ledger_result = self._ledger.compare_and_swap(
            request.storage_ref,
            request.expected_project_id,
            request.expected_storage_revision,
            lifecycle,
            next_revision,
        )
        if not isinstance(ledger_result, TelemetryOwnershipLedgerFound):
            raise _TransactionBoundaryViolation
        if (
            ledger_result.entry.stream_locator != entry.stream_locator
            or ledger_result.entry.storage_ref.storage_ref != request.storage_ref.storage_ref
            or ledger_result.entry.storage_ref.project_id != request.storage_ref.project_id
            or ledger_result.entry.storage_ref.stream_id != request.storage_ref.stream_id
            or ledger_result.entry.storage_ref.ownership_ledger_ref
            != request.storage_ref.ownership_ledger_ref
            or ledger_result.entry.storage_ref.storage_revision != next_revision
            or ledger_result.entry.storage_ref.lifecycle is not lifecycle
        ):
            raise _TransactionBoundaryViolation
        self._write_journal(self._with_phase(journal, _TransactionPhase.LEDGER_APPLIED))
        self._cleanup_transaction(transaction_paths)
        if lifecycle is TelemetryStorageLifecycle.DETACHED:
            return CompletedDetachResponse(
                storage_ref=request.storage_ref.storage_ref,
                storage_revision=next_revision,
                record_count=len(pre.records),
            )
        return CompletedUninstallResponse(
            storage_ref=request.storage_ref.storage_ref,
            storage_revision=next_revision,
            record_count=len(pre.records),
        )

    def _execute_read(
        self,
        request: NoRecordTelemetryStorageRequest,
        entry: TelemetryOwnershipLedgerEntry,
    ) -> TelemetryStorageResponse:
        paths = self._paths(request.storage_ref, entry.stream_locator)
        self._ensure_paths_owned(paths)
        state = self._read_stream(paths)
        return CompletedReadResponse(
            storage_ref=request.storage_ref.storage_ref,
            storage_revision=request.expected_storage_revision,
            record_count=len(state.records),
            read_payload=TelemetryStorageReadPayload(records=state.records),
        )

    def _execute_validate(
        self,
        request: NoRecordTelemetryStorageRequest,
        entry: TelemetryOwnershipLedgerEntry,
    ) -> TelemetryStorageResponse:
        paths = self._paths(request.storage_ref, entry.stream_locator)
        self._ensure_paths_owned(paths)
        state = self._read_stream(paths)
        report = ContextUsageValidator().validate(records=state.records)
        report_json = json.dumps(
            report.model_dump(mode="json"),
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        return CompletedValidateResponse(
            storage_ref=request.storage_ref.storage_ref,
            storage_revision=request.expected_storage_revision,
            record_count=len(state.records),
            validation_report_ref=self._report_ref(
                request.storage_ref,
                request.expected_storage_revision,
                report_json,
            ),
        )

    def _execute_locked(
        self, request: TelemetryStorageRequest, preliminary_entry: TelemetryOwnershipLedgerEntry
    ) -> TelemetryStorageResponse:
        current_result = self._ledger.resolve_current(request.storage_ref)
        current_entry, current_failure = self._ledger_entry(request, current_result)
        if current_failure is not None:
            if isinstance(current_result, TelemetryOwnershipLedgerNotFound):
                self._recover_pending(request, None)
            else:
                return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        else:
            self._recover_pending(request, current_entry)
        final_result = self._ledger.resolve(
            request.storage_ref,
            request.expected_project_id,
            request.expected_storage_revision,
        )
        entry, failure = self._ledger_entry(request, final_result)
        if failure is not None:
            return failure
        if (
            entry is None
            or not self._entry_matches_request(entry, request)
            or not self._entry_matches_request(preliminary_entry, request)
            or preliminary_entry.stream_locator != entry.stream_locator
        ):
            return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        try:
            if isinstance(request, AppendTelemetryStorageRequest):
                return self._execute_append(request, entry)
            if request.operation is TelemetryStorageOperation.READ:
                return self._execute_read(request, entry)
            if request.operation is TelemetryStorageOperation.VALIDATE:
                return self._execute_validate(request, entry)
            if request.operation is TelemetryStorageOperation.DETACH:
                return self._execute_remove(request, entry, TelemetryStorageLifecycle.DETACHED)
            if request.operation is TelemetryStorageOperation.UNINSTALL:
                return self._execute_remove(request, entry, TelemetryStorageLifecycle.REMOVED)
            return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        except _InvalidTelemetryRecord:
            return self._failure(request, TelemetryStorageDecision.RECORD_INVALID)

    def execute(self, request: TelemetryStorageRequest) -> TelemetryStorageResponse:
        """Execute one validated request through preliminary and under-lock admission."""

        try:
            preliminary_result = self._ledger.resolve(
                request.storage_ref,
                request.expected_project_id,
                request.expected_storage_revision,
            )
            preliminary_entry, preliminary_failure = self._ledger_entry(
                request, preliminary_result
            )
            if preliminary_failure is not None:
                return preliminary_failure
            if (
                preliminary_entry is None
                or not self._entry_matches_request(preliminary_entry, request)
            ):
                return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
            lock_request = TelemetryStorageLockRequest(
                storage_ref=request.storage_ref,
                expected_project_id=request.expected_project_id,
                expected_storage_revision=request.expected_storage_revision,
            )
            lock_result = self._lock.try_acquire(lock_request)
        except Exception:
            return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        if isinstance(lock_result, TelemetryStorageLockContended):
            if (
                lock_result.storage_ref != request.storage_ref.storage_ref
                or lock_result.storage_revision != request.expected_storage_revision
            ):
                return self._failure(
                    request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION
                )
            return self._failure(
                request,
                TelemetryStorageDecision.LOCK_CONTENDED,
                failure_ref=lock_result.failure_ref,
            )
        if not isinstance(lock_result, TelemetryStorageLockAcquired):
            return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        primary: TelemetryStorageResponse
        try:
            if not self._lock_token_matches(lock_result.lock_token, request):
                primary = self._failure(
                    request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION
                )
            else:
                primary = self._execute_locked(request, preliminary_entry)
        except Exception:
            primary = self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        try:
            release_result = self._lock.release(lock_result.lock_token)
        except Exception:
            return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        if (
            not isinstance(release_result, TelemetryStorageLockReleased)
            or release_result.lock_ref != lock_result.lock_token.lock_ref
            or release_result.storage_ref != request.storage_ref.storage_ref
            or release_result.storage_revision != request.expected_storage_revision
        ):
            return self._failure(request, TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION)
        return primary


__all__ = ["JohnnyOwnedTelemetryStorageAdapter"]
