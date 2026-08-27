"""Strict, effect-free request and response contracts for telemetry storage."""

from __future__ import annotations

from enum import Enum
from typing import Protocol, Self, TypeAlias, runtime_checkable

from pydantic import ConfigDict, model_validator

from library.workflow_router.contracts import (
    OpaqueMetadataId,
    ProjectId,
    RevisionDigest,
    RouterModel,
)
from library.workflow_router.telemetry import ContextUsageRecord, NonNegativeCount
class _StorageModel(RouterModel):
    """Frozen strict model with nested-instance revalidation for this boundary."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class TelemetryStorageLifecycle(str, Enum):
    """The finite lifecycle of an owned telemetry stream."""

    ACTIVE = "ACTIVE"
    DETACHED = "DETACHED"
    REMOVED = "REMOVED"


class TelemetryStorageOperation(str, Enum):
    """The finite operations admitted by the storage port."""

    APPEND = "APPEND"
    READ = "READ"
    VALIDATE = "VALIDATE"
    DETACH = "DETACH"
    UNINSTALL = "UNINSTALL"


class TelemetryStorageLockDecision(str, Enum):
    """The finite outcomes of one lock acquire or release operation."""

    LOCK_ACQUIRED = "LOCK_ACQUIRED"
    LOCK_CONTENDED = "LOCK_CONTENDED"
    RELEASED = "RELEASED"
    RELEASE_FAILED = "RELEASE_FAILED"


class TelemetryStorageDecision(str, Enum):
    """The finite completed and failed storage decisions."""

    COMPLETED = "COMPLETED"
    STORAGE_REF_INVALID = "STORAGE_REF_INVALID"
    STORAGE_OWNERSHIP_MISMATCH = "STORAGE_OWNERSHIP_MISMATCH"
    STORAGE_CLOSED = "STORAGE_CLOSED"
    STORAGE_BOUNDARY_VIOLATION = "STORAGE_BOUNDARY_VIOLATION"
    RECORD_INVALID = "RECORD_INVALID"
    LOCK_CONTENDED = "LOCK_CONTENDED"


_NO_RECORD_OPERATIONS: tuple[TelemetryStorageOperation, ...] = (
    TelemetryStorageOperation.READ,
    TelemetryStorageOperation.VALIDATE,
    TelemetryStorageOperation.DETACH,
    TelemetryStorageOperation.UNINSTALL,
)
_FAILURE_DECISIONS: tuple[TelemetryStorageDecision, ...] = (
    TelemetryStorageDecision.STORAGE_REF_INVALID,
    TelemetryStorageDecision.STORAGE_OWNERSHIP_MISMATCH,
    TelemetryStorageDecision.STORAGE_CLOSED,
    TelemetryStorageDecision.STORAGE_BOUNDARY_VIOLATION,
    TelemetryStorageDecision.RECORD_INVALID,
    TelemetryStorageDecision.LOCK_CONTENDED,
)


class TelemetryStorageRef(_StorageModel):
    """Opaque identity supplied to a future ownership-ledger adapter."""

    storage_ref: OpaqueMetadataId
    project_id: ProjectId
    stream_id: OpaqueMetadataId
    ownership_ledger_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    lifecycle: TelemetryStorageLifecycle


class TelemetryStorageLockRequest(_StorageModel):
    """A strict lock admission request bound to one opaque storage reference."""

    storage_ref: TelemetryStorageRef
    expected_project_id: ProjectId
    expected_storage_revision: RevisionDigest


class TelemetryStorageLockToken(_StorageModel):
    """The complete opaque identity returned only after lock acquisition."""

    lock_ref: OpaqueMetadataId
    storage_ref: OpaqueMetadataId
    project_id: ProjectId
    stream_id: OpaqueMetadataId
    ownership_ledger_ref: OpaqueMetadataId
    storage_revision: RevisionDigest


class TelemetryStorageLockAcquired(_StorageModel):
    """A successful acquire result carrying exactly one bound lock token."""

    decision: TelemetryStorageLockDecision = TelemetryStorageLockDecision.LOCK_ACQUIRED
    lock_token: TelemetryStorageLockToken

    @model_validator(mode="after")
    def decision_is_acquired(self) -> Self:
        if self.decision is not TelemetryStorageLockDecision.LOCK_ACQUIRED:
            raise ValueError("acquired results require LOCK_ACQUIRED")
        return self


class TelemetryStorageLockContended(_StorageModel):
    """A finite acquire contention result without any lock token."""

    decision: TelemetryStorageLockDecision = TelemetryStorageLockDecision.LOCK_CONTENDED
    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    failure_ref: OpaqueMetadataId

    @model_validator(mode="after")
    def decision_is_contended(self) -> Self:
        if self.decision is not TelemetryStorageLockDecision.LOCK_CONTENDED:
            raise ValueError("contention results require LOCK_CONTENDED")
        return self


TelemetryStorageLockAcquire: TypeAlias = (
    TelemetryStorageLockAcquired | TelemetryStorageLockContended
)


class TelemetryStorageLockReleased(_StorageModel):
    """A successful release result with no token or failure payload."""

    decision: TelemetryStorageLockDecision = TelemetryStorageLockDecision.RELEASED
    lock_ref: OpaqueMetadataId
    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest

    @model_validator(mode="after")
    def decision_is_released(self) -> Self:
        if self.decision is not TelemetryStorageLockDecision.RELEASED:
            raise ValueError("released results require RELEASED")
        return self


class TelemetryStorageLockReleaseFailed(_StorageModel):
    """A finite release failure carrying only one opaque failure reference."""

    decision: TelemetryStorageLockDecision = TelemetryStorageLockDecision.RELEASE_FAILED
    lock_ref: OpaqueMetadataId
    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    failure_ref: OpaqueMetadataId

    @model_validator(mode="after")
    def decision_is_release_failed(self) -> Self:
        if self.decision is not TelemetryStorageLockDecision.RELEASE_FAILED:
            raise ValueError("release failures require RELEASE_FAILED")
        return self


TelemetryStorageLockRelease: TypeAlias = (
    TelemetryStorageLockReleased | TelemetryStorageLockReleaseFailed
)


@runtime_checkable
class TelemetryStorageLockPort(Protocol):
    """The future lock dependency seam; it performs no locking here."""

    def try_acquire(
        self, request: TelemetryStorageLockRequest
    ) -> TelemetryStorageLockAcquire:
        """Attempt one lock acquisition and return a finite result."""

        ...

    def release(self, token: TelemetryStorageLockToken) -> TelemetryStorageLockRelease:
        """Release one previously acquired token and return a finite result."""

        ...


class AppendTelemetryStorageRequest(_StorageModel):
    """The only request variant that carries a telemetry record."""

    storage_ref: TelemetryStorageRef
    expected_project_id: ProjectId
    expected_storage_revision: RevisionDigest
    operation: TelemetryStorageOperation = TelemetryStorageOperation.APPEND
    record: ContextUsageRecord

    @model_validator(mode="after")
    def operation_is_append(self) -> Self:
        """Keep the record-bearing variant exclusive to APPEND."""

        if self.operation is not TelemetryStorageOperation.APPEND:
            raise ValueError("append requests require APPEND")
        return self


class NoRecordTelemetryStorageRequest(_StorageModel):
    """A request variant for operations that carry no additional payload."""

    storage_ref: TelemetryStorageRef
    expected_project_id: ProjectId
    expected_storage_revision: RevisionDigest
    operation: TelemetryStorageOperation

    @model_validator(mode="after")
    def operation_is_no_record(self) -> Self:
        """Keep record-free operations separate from APPEND."""

        if self.operation not in _NO_RECORD_OPERATIONS:
            raise ValueError("the no-record variant does not admit APPEND")
        return self


TelemetryStorageRequest: TypeAlias = (
    AppendTelemetryStorageRequest | NoRecordTelemetryStorageRequest
)


class TelemetryStorageReadPayload(_StorageModel):
    """The complete immutable READ result in ledger append order."""

    records: tuple[ContextUsageRecord, ...]


def _validate_completed_shape(
    *,
    operation: TelemetryStorageOperation,
    expected_operation: TelemetryStorageOperation,
    decision: TelemetryStorageDecision,
    lifecycle: TelemetryStorageLifecycle,
    expected_lifecycle: TelemetryStorageLifecycle,
) -> None:
    """Validate the common discriminants of one completed response."""

    if operation is not expected_operation:
        raise ValueError("response operation does not match its response variant")
    if decision is not TelemetryStorageDecision.COMPLETED:
        raise ValueError("completed responses require COMPLETED")
    if lifecycle is not expected_lifecycle:
        raise ValueError("response lifecycle does not match its response variant")


class CompletedAppendResponse(_StorageModel):
    """Successful APPEND response."""

    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    operation: TelemetryStorageOperation = TelemetryStorageOperation.APPEND
    decision: TelemetryStorageDecision = TelemetryStorageDecision.COMPLETED
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.ACTIVE
    record_count: NonNegativeCount

    @model_validator(mode="after")
    def response_shape_is_append(self) -> Self:
        _validate_completed_shape(
            operation=self.operation,
            expected_operation=TelemetryStorageOperation.APPEND,
            decision=self.decision,
            lifecycle=self.lifecycle,
            expected_lifecycle=TelemetryStorageLifecycle.ACTIVE,
        )
        return self


class CompletedReadResponse(_StorageModel):
    """Successful READ response with a count matching its complete payload."""

    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    operation: TelemetryStorageOperation = TelemetryStorageOperation.READ
    decision: TelemetryStorageDecision = TelemetryStorageDecision.COMPLETED
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.ACTIVE
    record_count: NonNegativeCount
    read_payload: TelemetryStorageReadPayload

    @model_validator(mode="after")
    def response_shape_is_read(self) -> Self:
        _validate_completed_shape(
            operation=self.operation,
            expected_operation=TelemetryStorageOperation.READ,
            decision=self.decision,
            lifecycle=self.lifecycle,
            expected_lifecycle=TelemetryStorageLifecycle.ACTIVE,
        )
        if self.record_count != len(self.read_payload.records):
            raise ValueError("READ record_count must equal the payload record count")
        return self


class CompletedValidateResponse(_StorageModel):
    """Successful VALIDATE response with its opaque report reference."""

    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    operation: TelemetryStorageOperation = TelemetryStorageOperation.VALIDATE
    decision: TelemetryStorageDecision = TelemetryStorageDecision.COMPLETED
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.ACTIVE
    record_count: NonNegativeCount
    validation_report_ref: OpaqueMetadataId

    @model_validator(mode="after")
    def response_shape_is_validate(self) -> Self:
        _validate_completed_shape(
            operation=self.operation,
            expected_operation=TelemetryStorageOperation.VALIDATE,
            decision=self.decision,
            lifecycle=self.lifecycle,
            expected_lifecycle=TelemetryStorageLifecycle.ACTIVE,
        )
        return self


class CompletedDetachResponse(_StorageModel):
    """Successful DETACH response."""

    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    operation: TelemetryStorageOperation = TelemetryStorageOperation.DETACH
    decision: TelemetryStorageDecision = TelemetryStorageDecision.COMPLETED
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.DETACHED
    record_count: NonNegativeCount

    @model_validator(mode="after")
    def response_shape_is_detach(self) -> Self:
        _validate_completed_shape(
            operation=self.operation,
            expected_operation=TelemetryStorageOperation.DETACH,
            decision=self.decision,
            lifecycle=self.lifecycle,
            expected_lifecycle=TelemetryStorageLifecycle.DETACHED,
        )
        return self


class CompletedUninstallResponse(_StorageModel):
    """Successful UNINSTALL response."""

    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    operation: TelemetryStorageOperation = TelemetryStorageOperation.UNINSTALL
    decision: TelemetryStorageDecision = TelemetryStorageDecision.COMPLETED
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.REMOVED
    record_count: NonNegativeCount

    @model_validator(mode="after")
    def response_shape_is_uninstall(self) -> Self:
        _validate_completed_shape(
            operation=self.operation,
            expected_operation=TelemetryStorageOperation.UNINSTALL,
            decision=self.decision,
            lifecycle=self.lifecycle,
            expected_lifecycle=TelemetryStorageLifecycle.REMOVED,
        )
        return self


class TelemetryStorageFailure(_StorageModel):
    """A finite failed result without lifecycle, count or success payload fields."""

    storage_ref: OpaqueMetadataId
    storage_revision: RevisionDigest
    operation: TelemetryStorageOperation
    decision: TelemetryStorageDecision
    failure_ref: OpaqueMetadataId

    @model_validator(mode="after")
    def decision_is_failure(self) -> Self:
        if self.decision not in _FAILURE_DECISIONS:
            raise ValueError("failure responses require a non-completed decision")
        return self


TelemetryStorageResponse: TypeAlias = (
    CompletedAppendResponse
    | CompletedReadResponse
    | CompletedValidateResponse
    | CompletedDetachResponse
    | CompletedUninstallResponse
    | TelemetryStorageFailure
)


@runtime_checkable
class TelemetryStoragePort(Protocol):
    """The sole typed caller port; implementations belong to a later ticket."""

    def execute(self, request: TelemetryStorageRequest) -> TelemetryStorageResponse:
        """Execute one already-validated request through a future adapter."""

        ...


__all__ = (
    "AppendTelemetryStorageRequest",
    "CompletedAppendResponse",
    "CompletedDetachResponse",
    "CompletedReadResponse",
    "CompletedUninstallResponse",
    "CompletedValidateResponse",
    "NoRecordTelemetryStorageRequest",
    "TelemetryStorageDecision",
    "TelemetryStorageFailure",
    "TelemetryStorageLifecycle",
    "TelemetryStorageLockAcquire",
    "TelemetryStorageLockAcquired",
    "TelemetryStorageLockContended",
    "TelemetryStorageLockDecision",
    "TelemetryStorageLockPort",
    "TelemetryStorageLockRelease",
    "TelemetryStorageLockReleaseFailed",
    "TelemetryStorageLockReleased",
    "TelemetryStorageLockRequest",
    "TelemetryStorageLockToken",
    "TelemetryStorageOperation",
    "TelemetryStoragePort",
    "TelemetryStorageReadPayload",
    "TelemetryStorageRef",
    "TelemetryStorageRequest",
    "TelemetryStorageResponse",
)
