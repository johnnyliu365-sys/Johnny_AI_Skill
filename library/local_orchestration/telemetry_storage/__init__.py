"""Pure typed contracts for the future telemetry-storage adapter boundary."""

from .contracts import (
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
    TelemetryStorageOperation,
    TelemetryStoragePort,
    TelemetryStorageReadPayload,
    TelemetryStorageRef,
    TelemetryStorageRequest,
    TelemetryStorageResponse,
)

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
    "TelemetryStorageOperation",
    "TelemetryStoragePort",
    "TelemetryStorageReadPayload",
    "TelemetryStorageRef",
    "TelemetryStorageRequest",
    "TelemetryStorageResponse",
)
