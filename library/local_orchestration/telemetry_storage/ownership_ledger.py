"""Private pre-provisioned ownership-ledger lookup and compare-and-swap port."""

from __future__ import annotations

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
from library.workflow_router.contracts import OpaqueMetadataId, ProjectId, RevisionDigest


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


class _LedgerDocument(_LedgerModelMixin):
    """Canonical schema-versioned file shape; never part of the public port."""

    schema_version: Literal[1]
    entries: tuple[TelemetryOwnershipLedgerEntry, ...]

    @model_validator(mode="after")
    def entries_are_unique(self) -> Self:
        identities = tuple(entry.storage_ref.storage_ref for entry in self.entries)
        if len(set(identities)) != len(identities):
            raise ValueError("ledger identities must be unique")
        return self


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

    def _paths(self) -> tuple[Path, Path]:
        telemetry_root = self._layout.telemetry_root
        ledger_path = telemetry_root / "ownership-ledger" / "ledger.json"
        return telemetry_root, ledger_path

    def _paths_are_owned(self) -> bool:
        telemetry_root, ledger_path = self._paths()
        try:
            root_is_owned = resolves_within_root(telemetry_root, telemetry_root)
            ledger_is_owned = resolves_within_root(ledger_path, telemetry_root)
        except (OSError, RuntimeError):
            return False
        return root_is_owned and ledger_is_owned

    def _read_document(self) -> _LedgerDocument | None:
        if not self._paths_are_owned():
            raise _LedgerBoundaryViolation
        _, ledger_path = self._paths()
        try:
            text = ledger_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError:
            raise _LedgerBoundaryViolation from None
        try:
            return _LedgerDocument.model_validate_json(text)
        except (TypeError, ValueError):
            raise _LedgerBoundaryViolation from None

    @staticmethod
    def _serialize(document: _LedgerDocument) -> str:
        return (
            json.dumps(
                document.model_dump(mode="json"),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )

    def _write_document(self, document: _LedgerDocument) -> None:
        if not self._paths_are_owned():
            raise _LedgerBoundaryViolation
        _, ledger_path = self._paths()
        temporary_path: Path | None = None
        descriptor = -1
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".ledger-", suffix=".tmp", dir=str(ledger_path.parent)
            )
            temporary_path = Path(temporary_name)
            os.close(descriptor)
            descriptor = -1
            temporary_path.write_text(self._serialize(document), encoding="utf-8")
            with temporary_path.open("r+b") as handle:
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, ledger_path)
        except (OSError, TypeError, ValueError):
            raise _LedgerBoundaryViolation from None
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
    def _entry_for(
        document: _LedgerDocument, storage_ref: TelemetryStorageRef
    ) -> TelemetryOwnershipLedgerEntry | None:
        for entry in document.entries:
            if entry.storage_ref.storage_ref == storage_ref.storage_ref:
                return entry
        return None

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
    def _closed(entry: TelemetryOwnershipLedgerEntry) -> bool:
        return entry.storage_ref.lifecycle in (
            TelemetryStorageLifecycle.DETACHED,
            TelemetryStorageLifecycle.REMOVED,
        )

    @staticmethod
    def _replace_entry(
        document: _LedgerDocument,
        old_entry: TelemetryOwnershipLedgerEntry,
        next_entry: TelemetryOwnershipLedgerEntry,
    ) -> _LedgerDocument:
        entries = tuple(
            next_entry if entry is old_entry else entry for entry in document.entries
        )
        return _LedgerDocument(schema_version=1, entries=entries)

    def resolve(
        self,
        storage_ref: TelemetryStorageRef,
        expected_project_id: ProjectId,
        expected_storage_revision: RevisionDigest,
    ) -> TelemetryOwnershipLedgerResult:
        """Resolve without provisioning, repairing, or changing the ledger."""

        try:
            document = self._read_document()
            if document is None:
                return TelemetryOwnershipLedgerNotFound()
            entry = self._entry_for(document, storage_ref)
            if entry is None:
                return TelemetryOwnershipLedgerNotFound()
            if not self._owned_entry_matches(entry, storage_ref, expected_project_id):
                return TelemetryOwnershipLedgerOwnershipMismatch()
            if entry.storage_ref.storage_revision != expected_storage_revision:
                return TelemetryOwnershipLedgerOwnershipMismatch()
            if self._closed(entry):
                return TelemetryOwnershipLedgerClosed()
            return TelemetryOwnershipLedgerFound(entry=entry)
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
            document = self._read_document()
            if document is None:
                return TelemetryOwnershipLedgerNotFound()
            entry = self._entry_for(document, storage_ref)
            if entry is None:
                return TelemetryOwnershipLedgerNotFound()
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
            updated = self._replace_entry(document, entry, next_entry)
            self._write_document(updated)
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
