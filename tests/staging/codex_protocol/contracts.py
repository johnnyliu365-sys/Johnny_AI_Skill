"""Strict documented Codex protocol shapes and exact response-file port."""

from __future__ import annotations

from enum import Enum
import json
from pathlib import Path
import stat
from typing import Literal, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from library.local_orchestration.host_contracts import CodexMarketplaceList, CodexPluginList
from tests.staging.environment_core.contracts import EnvironmentLease, revalidate_lease


RESPONSE_FILE_NAME = ".johnny-05s3-response.json"
MAX_RESPONSE_BYTES = 65_536


class StrictModel(BaseModel):
    """Reject all unchecked protocol values at the test-only boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class CodexProtocolSurface(str, Enum):
    MARKETPLACE_ADD = "MARKETPLACE_ADD"
    MARKETPLACE_LIST = "MARKETPLACE_LIST"
    MARKETPLACE_REMOVE = "MARKETPLACE_REMOVE"
    PLUGIN_ADD = "PLUGIN_ADD"
    PLUGIN_LIST = "PLUGIN_LIST"
    PLUGIN_REMOVE = "PLUGIN_REMOVE"
    VERSION = "VERSION"


class CodexProtocolRejectReason(str, Enum):
    PROCESS_FAILED = "PROCESS_FAILED"
    RESPONSE_MISSING = "RESPONSE_MISSING"
    RESPONSE_BOUNDARY_INVALID = "RESPONSE_BOUNDARY_INVALID"
    RESPONSE_TOO_LARGE = "RESPONSE_TOO_LARGE"
    INVALID_UTF8 = "INVALID_UTF8"
    MALFORMED_JSON = "MALFORMED_JSON"
    DUPLICATE_KEY = "DUPLICATE_KEY"
    SCHEMA_INVALID = "SCHEMA_INVALID"
    CLEANUP_FAILED = "CLEANUP_FAILED"


def _nonblank(value: str, label: str) -> str:
    if not value or value != value.strip():
        raise ValueError(f"{label} must be a nonblank string")
    return value


class CodexMarketplaceAdd(StrictModel):
    marketplaceName: str
    installedRoot: str
    alreadyAdded: bool

    _text = field_validator("marketplaceName", "installedRoot")(classmethod(lambda cls, value: _nonblank(value, "field")))


class CodexMarketplaceRemove(StrictModel):
    marketplaceName: str
    installedRoot: str

    _text = field_validator("marketplaceName", "installedRoot")(classmethod(lambda cls, value: _nonblank(value, "field")))


class CodexPluginAdd(StrictModel):
    pluginId: str
    name: str
    marketplaceName: str
    version: str
    installedPath: str
    authPolicy: str

    _text = field_validator(
        "pluginId",
        "name",
        "marketplaceName",
        "version",
        "installedPath",
        "authPolicy",
    )(classmethod(lambda cls, value: _nonblank(value, "field")))


class CodexPluginRemove(StrictModel):
    pluginId: str
    name: str
    marketplaceName: str

    _text = field_validator("pluginId", "name", "marketplaceName")(classmethod(lambda cls, value: _nonblank(value, "field")))


class CodexVersionObservation(StrictModel):
    """One child-observed version with no caller-provided identity fields."""

    version: str

    _text = field_validator("version")(classmethod(lambda cls, value: _nonblank(value, "version")))


CodexProtocolPayload: TypeAlias = (
    CodexMarketplaceAdd
    | CodexMarketplaceList
    | CodexMarketplaceRemove
    | CodexPluginAdd
    | CodexPluginList
    | CodexPluginRemove
    | CodexVersionObservation
)


class CodexProtocolAccepted(StrictModel):
    surface: CodexProtocolSurface
    payload: CodexProtocolPayload

    @model_validator(mode="after")
    def payload_matches_selected_surface(self) -> CodexProtocolAccepted:
        expected = {
            CodexProtocolSurface.MARKETPLACE_ADD: CodexMarketplaceAdd,
            CodexProtocolSurface.MARKETPLACE_LIST: CodexMarketplaceList,
            CodexProtocolSurface.MARKETPLACE_REMOVE: CodexMarketplaceRemove,
            CodexProtocolSurface.PLUGIN_ADD: CodexPluginAdd,
            CodexProtocolSurface.PLUGIN_LIST: CodexPluginList,
            CodexProtocolSurface.PLUGIN_REMOVE: CodexPluginRemove,
            CodexProtocolSurface.VERSION: CodexVersionObservation,
        }[self.surface]
        if not isinstance(self.payload, expected):
            raise ValueError("payload does not match the selected protocol surface")
        return self


class CodexProtocolRejected(StrictModel):
    surface: CodexProtocolSurface
    reason: CodexProtocolRejectReason


class ResponseFileInspection(str, Enum):
    ABSENT = "ABSENT"
    PRESENT = "PRESENT"
    BOUNDARY_INVALID = "BOUNDARY_INVALID"


class ResponseFileRemoval(str, Enum):
    REMOVED = "REMOVED"
    ALREADY_ABSENT = "ALREADY_ABSENT"
    FAILED = "FAILED"


class ResponseFileBytes(StrictModel):
    value: bytes


class ResponseFileTooLarge(StrictModel):
    reason: Literal[CodexProtocolRejectReason.RESPONSE_TOO_LARGE] = CodexProtocolRejectReason.RESPONSE_TOO_LARGE


class ResponseFileBoundaryInvalid(StrictModel):
    reason: Literal[CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID] = CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID


ResponseFileRead: TypeAlias = ResponseFileBytes | ResponseFileTooLarge | ResponseFileBoundaryInvalid


class ResponseFilePort(Protocol):
    """Required binding to the one fixed child response file."""

    def inspect(self, lease: EnvironmentLease) -> ResponseFileInspection:
        """Inspect only the fixed response-file locator for this exact lease."""

    def read(self, lease: EnvironmentLease) -> ResponseFileRead:
        """Read at most the declared response size from that exact file."""

    def remove(self, lease: EnvironmentLease) -> ResponseFileRemoval:
        """Remove only that exact ordinary response file."""


class ExactResponseFilePort:
    """Concrete exact-file filesystem binding with no caller-selected locator."""

    def inspect(self, lease: EnvironmentLease) -> ResponseFileInspection:
        try:
            path = _response_path(lease)
        except ValueError:
            return ResponseFileInspection.BOUNDARY_INVALID
        try:
            path.lstat()
        except FileNotFoundError:
            return ResponseFileInspection.ABSENT
        except OSError:
            return ResponseFileInspection.BOUNDARY_INVALID
        if _is_reparse(path) or not path.is_file():
            return ResponseFileInspection.BOUNDARY_INVALID
        return ResponseFileInspection.PRESENT

    def read(self, lease: EnvironmentLease) -> ResponseFileRead:
        try:
            path = _response_path(lease)
        except ValueError:
            return ResponseFileBoundaryInvalid()
        if _is_reparse(path) or not path.is_file():
            return ResponseFileBoundaryInvalid()
        try:
            if path.stat().st_size > MAX_RESPONSE_BYTES:
                return ResponseFileTooLarge()
            with path.open("rb") as response:
                return ResponseFileBytes(value=response.read(MAX_RESPONSE_BYTES))
        except OSError:
            return ResponseFileBoundaryInvalid()

    def remove(self, lease: EnvironmentLease) -> ResponseFileRemoval:
        try:
            path = _response_path(lease)
        except ValueError:
            return ResponseFileRemoval.FAILED
        try:
            path.lstat()
        except FileNotFoundError:
            return ResponseFileRemoval.ALREADY_ABSENT
        except OSError:
            return ResponseFileRemoval.FAILED
        if _is_reparse(path) or not path.is_file():
            return ResponseFileRemoval.FAILED
        try:
            path.unlink()
        except OSError:
            return ResponseFileRemoval.FAILED
        return ResponseFileRemoval.REMOVED


class _DuplicateJsonKey(ValueError):
    """Internal decoder signal that never crosses the protocol result boundary."""


def parse_codex_protocol_payload(
    surface: CodexProtocolSurface,
    raw: bytes,
) -> CodexProtocolPayload | CodexProtocolRejectReason:
    """Decode one strict response without carrying dynamic JSON inward."""

    try:
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return CodexProtocolRejectReason.INVALID_UTF8
    try:
        parsed: object = json.loads(decoded, object_pairs_hook=_strict_json_object)
    except _DuplicateJsonKey:
        return CodexProtocolRejectReason.DUPLICATE_KEY
    except (json.JSONDecodeError, RecursionError, ValueError):
        return CodexProtocolRejectReason.MALFORMED_JSON
    if not isinstance(parsed, dict):
        return CodexProtocolRejectReason.SCHEMA_INVALID
    try:
        if surface is CodexProtocolSurface.MARKETPLACE_ADD:
            return CodexMarketplaceAdd.model_validate(parsed)
        if surface is CodexProtocolSurface.MARKETPLACE_LIST:
            return CodexMarketplaceList.model_validate(parsed)
        if surface is CodexProtocolSurface.MARKETPLACE_REMOVE:
            return CodexMarketplaceRemove.model_validate(parsed)
        if surface is CodexProtocolSurface.PLUGIN_ADD:
            return CodexPluginAdd.model_validate(parsed)
        if surface is CodexProtocolSurface.PLUGIN_LIST:
            return CodexPluginList.model_validate(parsed)
        if surface is CodexProtocolSurface.VERSION:
            return CodexVersionObservation.model_validate(parsed)
        return CodexPluginRemove.model_validate(parsed)
    except (ValidationError, ValueError, TypeError):
        return CodexProtocolRejectReason.SCHEMA_INVALID


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    object_value: dict[str, object] = {}
    for key, value in pairs:
        if key in object_value:
            raise _DuplicateJsonKey()
        object_value[key] = value
    return object_value


def _response_path(lease: EnvironmentLease) -> Path:
    validated = revalidate_lease(lease)
    if not isinstance(validated, EnvironmentLease):
        raise ValueError("invalid environment lease")
    temporary = validated.temporary.absolute.path
    if _is_reparse(temporary) or not temporary.is_dir():
        raise ValueError("invalid response directory")
    return temporary / RESPONSE_FILE_NAME


def _is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except OSError:
        return True
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
