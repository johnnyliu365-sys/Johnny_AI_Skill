"""Private pre-provisioned ownership-ledger lookup and compare-and-swap port."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, Protocol, Self, TypeAlias, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, model_validator

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.path_containment import resolves_within_root
from library.local_orchestration.telemetry_storage.contracts import (
    TelemetryStorageLifecycle,
    TelemetryStorageRef,
)
from library.workflow_router.contracts import ProjectId, RevisionDigest


class LedgerResolutionDecision(str, Enum):
    """Finite outcomes of lookup and compare-and-swap."""

    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    OWNERSHIP_MISMATCH = "OWNERSHIP_MISMATCH"
    CLOSED = "CLOSED"
    CONFLICT = "CONFLICT"
    BOUNDARY_REJECTED = "BOUNDARY_REJECTED"


RelativeStreamLocator = Annotated[
    str,
    Field(min_length=1, max_length=256),
]


class _LedgerModelMixin(BaseModel):
    """Marker for the immutable strict Pydantic models below."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class TelemetryOwnershipLedgerEntry(_LedgerModelMixin):
    """One complete, already-provisioned owned storage entry."""

    storage_ref: TelemetryStorageRef
    stream_locator: RelativeStreamLocator

    @model_validator(mode="after")
    def locator_is_relative(self) -> Self:
        pieces = self.stream_locator.replace("\\", "/").split("/")
        if (
            self.stream_locator.startswith(("/", "\\"))
            or ":" in self.stream_locator
            or any(piece in ("", ".", "..") for piece in pieces)
        ):
            raise ValueError("stream locator must be a relative internal locator")
        return self


class _LedgerEntryDocument(_LedgerModelMixin):
    """Canonical schema-versioned document for exactly one owned stream entry."""

    schema_version: Literal[1]
    entry: TelemetryOwnershipLedgerEntry


class TelemetryOwnershipLedgerFound(_LedgerModelMixin):
    """A matching entry, returned by lookup or a successful CAS."""

    decision: LedgerResolutionDecision = LedgerResolutionDecision.FOUND
    entry: TelemetryOwnershipLedgerEntry

    @model_validator(mode="after")
    def decision_is_found(self) -> Self:
        if self.decision is not LedgerResolutionDecision.FOUND:
            raise ValueError("found result requires FOUND")
        return self


class TelemetryOwnershipLedgerNotFound(_LedgerModelMixin):
    """No pre-provisioned entry exists for the requested storage reference."""

    decision: LedgerResolutionDecision = LedgerResolutionDecision.NOT_FOUND

    @model_validator(mode="after")
    def decision_is_not_found(self) -> Self:
        if self.decision is not LedgerResolutionDecision.NOT_FOUND:
            raise ValueError("not-found result requires NOT_FOUND")
        return self


class TelemetryOwnershipLedgerOwnershipMismatch(_LedgerModelMixin):
    """The entry exists but its immutable ownership or expected revision differs."""

    decision: LedgerResolutionDecision = LedgerResolutionDecision.OWNERSHIP_MISMATCH

    @model_validator(mode="after")
    def decision_is_mismatch(self) -> Self:
        if self.decision is not LedgerResolutionDecision.OWNERSHIP_MISMATCH:
            raise ValueError("mismatch result requires OWNERSHIP_MISMATCH")
        return self


class TelemetryOwnershipLedgerClosed(_LedgerModelMixin):
    """The matching entry is no longer active for storage operations."""

    decision: LedgerResolutionDecision = LedgerResolutionDecision.CLOSED

    @model_validator(mode="after")
    def decision_is_closed(self) -> Self:
        if self.decision is not LedgerResolutionDecision.CLOSED:
            raise ValueError("closed result requires CLOSED")
        return self


class TelemetryOwnershipLedgerConflict(_LedgerModelMixin):
    """The compare-and-swap expected revision is stale."""

    decision: LedgerResolutionDecision = LedgerResolutionDecision.CONFLICT

    @model_validator(mode="after")
    def decision_is_conflict(self) -> Self:
        if self.decision is not LedgerResolutionDecision.CONFLICT:
            raise ValueError("conflict result requires CONFLICT")
        return self


class TelemetryOwnershipLedgerBoundaryRejected(_LedgerModelMixin):
    """A malformed or unowned ledger operation was rejected without detail."""

    decision: LedgerResolutionDecision = LedgerResolutionDecision.BOUNDARY_REJECTED

    @model_validator(mode="after")
    def decision_is_boundary_rejected(self) -> Self:
        if self.decision is not LedgerResolutionDecision.BOUNDARY_REJECTED:
            raise ValueError("boundary result requires BOUNDARY_REJECTED")
        return self


TelemetryOwnershipLedgerResult: TypeAlias = (
    TelemetryOwnershipLedgerFound
    | TelemetryOwnershipLedgerNotFound
    | TelemetryOwnershipLedgerOwnershipMismatch
    | TelemetryOwnershipLedgerClosed
    | TelemetryOwnershipLedgerConflict
    | TelemetryOwnershipLedgerBoundaryRejected
)


@runtime_checkable
class TelemetryOwnershipLedgerPort(Protocol):
    """Private lookup/CAS seam for the later lock-bound storage adapter."""

    def resolve(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: ProjectId,
        expected_storage_revision: RevisionDigest,
    ) -> TelemetryOwnershipLedgerResult:
        """Resolve one exact pre-provisioned entry."""

        ...

    def resolve_current(
        self, storage_ref: TelemetryStorageRef
    ) -> TelemetryOwnershipLedgerResult:
        """Resolve current state by immutable identity for recovery only."""

        ...

    def compare_and_swap(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: ProjectId,
        expected_storage_revision: RevisionDigest,
        next_lifecycle: TelemetryStorageLifecycle,
        next_storage_revision: RevisionDigest,
    ) -> TelemetryOwnershipLedgerResult:
        """Atomically replace only the current lifecycle and revision pair."""

        ...


class _LedgerBoundaryViolation(Exception):
    """Internal sentinel carrying no user-visible filesystem detail."""


class LocalTelemetryOwnershipLedger(TelemetryOwnershipLedgerPort):
    """Read and CAS a pre-provisioned ledger below one injected Johnny root."""

    def __init__(self, layout: JohnnyRootLayout) -> None:
        if not isinstance(layout, JohnnyRootLayout):
            raise TypeError("layout must be JohnnyRootLayout")
        self._layout = layout

    @staticmethod
    def _entry_digest(storage_ref: TelemetryStorageRef) -> str:
        identity = "\0".join(
            (
                "johnny-telemetry-ownership-ledger-v1",
                storage_ref.storage_ref,
                storage_ref.project_id,
                storage_ref.stream_id,
                storage_ref.ownership_ledger_ref,
            )
        )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def _paths(
        self, storage_ref: TelemetryStorageRef
    ) -> tuple[Path, Path, Path, Path, Path, Path]:
        telemetry_root = self._layout.telemetry_root
        ownership_root = telemetry_root / "ownership-ledger"
        entries_root = ownership_root / "entries"
        entry_path = entries_root / f"{self._entry_digest(storage_ref)}.json"
        temporary_path = entry_path.with_name(f".{entry_path.stem}.tmp")
        legacy_path = ownership_root / "ledger.json"
        return (
            telemetry_root,
            ownership_root,
            entries_root,
            entry_path,
            temporary_path,
            legacy_path,
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
    def _legacy_present(legacy_path: Path) -> bool:
        try:
            legacy_path.lstat()
        except FileNotFoundError:
            return False
        except OSError:
            raise _LedgerBoundaryViolation from None
        return True

    def _read_document(
        self, storage_ref: TelemetryStorageRef
    ) -> _LedgerEntryDocument | None:
        (
            telemetry_root,
            ownership_root,
            entries_root,
            entry_path,
            temporary_path,
            legacy_path,
        ) = self._paths(storage_ref)
        paths = (
            telemetry_root,
            ownership_root,
            entries_root,
            entry_path,
            temporary_path,
            legacy_path,
        )
        if not self._paths_are_owned(paths, telemetry_root):
            raise _LedgerBoundaryViolation
        try:
            if self._legacy_present(legacy_path):
                raise _LedgerBoundaryViolation
            text = entry_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except _LedgerBoundaryViolation:
            raise
        except OSError:
            raise _LedgerBoundaryViolation from None
        try:
            document = _LedgerEntryDocument.model_validate_json(text)
        except (TypeError, ValueError):
            raise _LedgerBoundaryViolation from None
        if not self._identity_matches(document.entry.storage_ref, storage_ref):
            raise _LedgerBoundaryViolation
        return document

    @staticmethod
    def _serialize(document: _LedgerEntryDocument) -> str:
        return (
            json.dumps(
                document.model_dump(mode="json"),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )

    def _write_document(
        self, storage_ref: TelemetryStorageRef, document: _LedgerEntryDocument
    ) -> None:
        (
            telemetry_root,
            ownership_root,
            entries_root,
            entry_path,
            temporary_path_hint,
            legacy_path,
        ) = self._paths(storage_ref)
        paths = (
            telemetry_root,
            ownership_root,
            entries_root,
            entry_path,
            temporary_path_hint,
            legacy_path,
        )
        if not self._paths_are_owned(paths, telemetry_root):
            raise _LedgerBoundaryViolation
        try:
            if self._legacy_present(legacy_path):
                raise _LedgerBoundaryViolation
        except _LedgerBoundaryViolation:
            raise
        except OSError:
            raise _LedgerBoundaryViolation from None
        temporary_path: Path | None = None
        descriptor = -1
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{entry_path.stem}-", suffix=".tmp", dir=str(entries_root)
            )
            temporary_path = Path(temporary_name)
            try:
                if not resolves_within_root(temporary_path, telemetry_root):
                    raise _LedgerBoundaryViolation
            except (OSError, RuntimeError):
                raise _LedgerBoundaryViolation from None
            os.close(descriptor)
            descriptor = -1
            temporary_path.write_text(self._serialize(document), encoding="utf-8")
            with temporary_path.open("r+b") as handle:
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, entry_path)
        except (OSError, TypeError, ValueError):
            raise _LedgerBoundaryViolation from None
        except _LedgerBoundaryViolation:
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

    @staticmethod
    def _owned_entry_matches(
        entry: TelemetryOwnershipLedgerEntry,
        storage_ref: TelemetryStorageRef,
        expected_project_id: ProjectId,
    ) -> bool:
        current = entry.storage_ref
        return (
            current.project_id == expected_project_id
            and current.project_id == storage_ref.project_id
            and current.stream_id == storage_ref.stream_id
            and current.ownership_ledger_ref == storage_ref.ownership_ledger_ref
        )

    @staticmethod
    def _identity_matches(
        current: TelemetryStorageRef, requested: TelemetryStorageRef
    ) -> bool:
        return (
            current.storage_ref == requested.storage_ref
            and current.project_id == requested.project_id
            and current.stream_id == requested.stream_id
            and current.ownership_ledger_ref == requested.ownership_ledger_ref
        )

    @staticmethod
    def _closed(entry: TelemetryOwnershipLedgerEntry) -> bool:
        return entry.storage_ref.lifecycle in (
            TelemetryStorageLifecycle.DETACHED,
            TelemetryStorageLifecycle.REMOVED,
        )

    @staticmethod
    def _replace_entry(
        document: _LedgerEntryDocument,
        next_entry: TelemetryOwnershipLedgerEntry,
    ) -> _LedgerEntryDocument:
        return _LedgerEntryDocument(schema_version=1, entry=next_entry)

    def resolve(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: ProjectId,
        expected_storage_revision: RevisionDigest,
    ) -> TelemetryOwnershipLedgerResult:
        """Resolve without provisioning, repairing, or changing the ledger."""

        try:
            document = self._read_document(storage_ref)
            if document is None:
                return TelemetryOwnershipLedgerNotFound()
            entry = document.entry
            if not self._owned_entry_matches(entry, storage_ref, expected_project_id):
                return TelemetryOwnershipLedgerOwnershipMismatch()
            if entry.storage_ref.storage_revision != expected_storage_revision:
                return TelemetryOwnershipLedgerOwnershipMismatch()
            if self._closed(entry):
                return TelemetryOwnershipLedgerClosed()
            return TelemetryOwnershipLedgerFound(entry=entry)
        except _LedgerBoundaryViolation:
            return TelemetryOwnershipLedgerBoundaryRejected()

    def resolve_current(
        self, storage_ref: TelemetryStorageRef
    ) -> TelemetryOwnershipLedgerResult:
        """Recover current state by immutable identity without admission or mutation."""

        try:
            document = self._read_document(storage_ref)
            if document is None:
                return TelemetryOwnershipLedgerNotFound()
            return TelemetryOwnershipLedgerFound(entry=document.entry)
        except _LedgerBoundaryViolation:
            return TelemetryOwnershipLedgerBoundaryRejected()

    def compare_and_swap(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: ProjectId,
        expected_storage_revision: RevisionDigest,
        next_lifecycle: TelemetryStorageLifecycle,
        next_storage_revision: RevisionDigest,
    ) -> TelemetryOwnershipLedgerResult:
        """Replace one matching entry's lifecycle and revision atomically."""

        try:
            document = self._read_document(storage_ref)
            if document is None:
                return TelemetryOwnershipLedgerNotFound()
            entry = document.entry
            if not self._owned_entry_matches(entry, storage_ref, expected_project_id):
                return TelemetryOwnershipLedgerOwnershipMismatch()
            if entry.storage_ref.storage_revision != expected_storage_revision:
                return TelemetryOwnershipLedgerConflict()
            if self._closed(entry):
                return TelemetryOwnershipLedgerClosed()
            current = entry.storage_ref
            next_reference = TelemetryStorageRef(
                storage_ref=current.storage_ref,
                project_id=current.project_id,
                stream_id=current.stream_id,
                ownership_ledger_ref=current.ownership_ledger_ref,
                storage_revision=next_storage_revision,
                lifecycle=next_lifecycle,
            )
            next_entry = TelemetryOwnershipLedgerEntry(
                storage_ref=next_reference,
                stream_locator=entry.stream_locator,
            )
            updated = self._replace_entry(document, next_entry)
            self._write_document(storage_ref, updated)
            return TelemetryOwnershipLedgerFound(entry=next_entry)
        except _LedgerBoundaryViolation:
            return TelemetryOwnershipLedgerBoundaryRejected()


__all__ = [
    "LedgerResolutionDecision",
    "RelativeStreamLocator",
    "TelemetryOwnershipLedgerEntry",
    "TelemetryOwnershipLedgerFound",
    "TelemetryOwnershipLedgerNotFound",
    "TelemetryOwnershipLedgerOwnershipMismatch",
    "TelemetryOwnershipLedgerClosed",
    "TelemetryOwnershipLedgerConflict",
    "TelemetryOwnershipLedgerBoundaryRejected",
    "TelemetryOwnershipLedgerResult",
    "TelemetryOwnershipLedgerPort",
    "LocalTelemetryOwnershipLedger",
]
