"""Strongly typed contracts for the disposable environment core."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator


class StrictModel(BaseModel):
    """Reject unvalidated dynamic data at the environment boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class EnvironmentOwnerId(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def opaque_owner(cls, value: str) -> str:
        if re.fullmatch(r"environment-owner-[0-9a-f]{16}", value) is None:
            raise ValueError("owner id must be a strict opaque identifier")
        return value


class EnvironmentId(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def generated_id(cls, value: str) -> str:
        if re.fullmatch(r"environment-[0-9a-f]{32}", value) is None:
            raise ValueError("environment id must be a generated opaque identifier")
        return value


class EnvironmentRelativeLocator(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def canonical_relative_locator(cls, value: str) -> str:
        if re.fullmatch(r"[a-z][a-z0-9-]*", value) is None:
            raise ValueError("relative locator must be one canonical segment")
        return value


class EnvironmentLocator(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def absolute_locator(cls, value: str) -> str:
        path = Path(value)
        if not value or value != value.strip() or not path.is_absolute():
            raise ValueError("environment locator must be an absolute path")
        return str(path)

    @property
    def path(self) -> Path:
        return Path(self.value)


class EnvironmentPath(StrictModel):
    relative: EnvironmentRelativeLocator
    absolute: EnvironmentLocator


class EnvironmentVariable(str, Enum):
    USERPROFILE = "USERPROFILE"
    LOCALAPPDATA = "LOCALAPPDATA"
    APPDATA = "APPDATA"
    TEMP = "TEMP"
    TMP = "TMP"
    CODEX_HOME = "CODEX_HOME"


class EnvironmentOverlayEntry(StrictModel):
    key: EnvironmentVariable
    path: EnvironmentLocator


class EnvironmentOverlay(StrictModel):
    entries: tuple[EnvironmentOverlayEntry, ...]

    @model_validator(mode="after")
    def exact_fixed_keys(self) -> EnvironmentOverlay:
        expected = tuple(EnvironmentVariable)
        if tuple(entry.key for entry in self.entries) != expected:
            raise ValueError("environment overlay must contain the exact fixed key set")
        return self


class EnvironmentMarker(StrictModel):
    owner: EnvironmentOwnerId
    environment_id: EnvironmentId
    root: EnvironmentLocator


class EnvironmentLease(StrictModel):
    owner: EnvironmentOwnerId
    environment_id: EnvironmentId
    root: EnvironmentLocator
    root_relative: EnvironmentRelativeLocator
    profile: EnvironmentPath
    local_app_data: EnvironmentPath
    roaming_app_data: EnvironmentPath
    temporary: EnvironmentPath
    codex_home: EnvironmentPath
    overlay: EnvironmentOverlay
    marker: EnvironmentMarker

    @model_validator(mode="after")
    def exact_owned_layout(self) -> EnvironmentLease:
        if self.root_relative.value != self.root.path.name:
            raise ValueError("root-relative locator must name the exact root")
        declared = (
            ("profile", self.profile),
            ("local-app-data", self.local_app_data),
            ("roaming-app-data", self.roaming_app_data),
            ("temp", self.temporary),
            ("codex-home", self.codex_home),
        )
        for expected, child in declared:
            if child.relative.value != expected or child.absolute.path.parent != self.root.path:
                raise ValueError("declared child must be directly owned by the environment root")
        expected_overlay = (
            self.profile.absolute,
            self.local_app_data.absolute,
            self.roaming_app_data.absolute,
            self.temporary.absolute,
            self.temporary.absolute,
            self.codex_home.absolute,
        )
        if tuple(entry.path for entry in self.overlay.entries) != expected_overlay:
            raise ValueError("overlay paths must bind the exact owned children")
        if self.marker.owner != self.owner or self.marker.environment_id != self.environment_id or self.marker.root != self.root:
            raise ValueError("marker must bind the exact environment lease")
        return self

    @property
    def marker_path(self) -> Path:
        return self.root.path / ".johnny-stage-env-owner.json"


class EnvironmentFault(str, Enum):
    NONE = "NONE"
    AFTER_ROOT = "AFTER_ROOT"
    AFTER_MARKER = "AFTER_MARKER"


class ProvisionBlockReason(str, Enum):
    INVALID_OWNER = "INVALID_OWNER"
    OWNER_REPLAYED = "OWNER_REPLAYED"
    FAULT_AFTER_ROOT = "FAULT_AFTER_ROOT"
    FAULT_AFTER_MARKER = "FAULT_AFTER_MARKER"
    INITIALIZATION_FAILED = "INITIALIZATION_FAILED"


@dataclass(frozen=True)
class ProvisionedEnvironment:
    environment: EnvironmentLease


@dataclass(frozen=True)
class ProvisionBlocked:
    reason: ProvisionBlockReason


ProvisionResult = ProvisionedEnvironment | ProvisionBlocked


class TeardownStatus(str, Enum):
    REMOVED = "REMOVED"
    ALREADY_ABSENT = "ALREADY_ABSENT"
    BLOCKED = "BLOCKED"


class TeardownBlockReason(str, Enum):
    NONE = "NONE"
    INVALID_LEASE = "INVALID_LEASE"
    ROOT_REPARSE = "ROOT_REPARSE"
    ROOT_ESCAPE = "ROOT_ESCAPE"
    MARKER_MISSING = "MARKER_MISSING"
    MARKER_MISMATCH = "MARKER_MISMATCH"
    CHILD_ESCAPE = "CHILD_ESCAPE"


class TeardownResult(StrictModel):
    status: TeardownStatus
    reason: TeardownBlockReason


def revalidate_owner(owner: EnvironmentOwnerId) -> EnvironmentOwnerId | ProvisionBlocked:
    """Reject constructed or malformed owner instances without touching disk."""

    try:
        return EnvironmentOwnerId.model_validate(owner.model_dump())
    except (AttributeError, ValidationError, ValueError):
        return ProvisionBlocked(reason=ProvisionBlockReason.INVALID_OWNER)


def revalidate_lease(lease: EnvironmentLease) -> EnvironmentLease | TeardownResult:
    """Reject constructed or malformed lease instances before teardown effects."""

    try:
        return EnvironmentLease.model_validate(lease.model_dump())
    except (AttributeError, ValidationError, ValueError):
        return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.INVALID_LEASE)
