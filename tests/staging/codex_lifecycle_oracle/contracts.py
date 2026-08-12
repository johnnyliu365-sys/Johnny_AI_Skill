"""Strict contracts and fixed locators for the Ticket 05S4 lifecycle oracle."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from pathlib import Path
import re
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from tests.staging.codex_protocol.contracts import CodexProtocolAccepted, CodexProtocolSurface
from tests.staging.environment_core.contracts import EnvironmentId, EnvironmentLease, EnvironmentOwnerId, revalidate_lease


ORACLE_COMMAND_FILE_NAME = ".johnny-05s4-command.json"
ORACLE_STATE_FILE_NAME = ".johnny-05s4-state.json"
ORACLE_PAYLOAD_DIRECTORY_NAME = "oracle-payloads"
ORACLE_STAGING_CODEX_VERSION = "oracle-staging-version"


class StrictModel(BaseModel):
    """Reject dynamic values at the persisted-oracle boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


def _nonblank(value: str, label: str) -> str:
    if not value or value != value.strip() or "\x00" in value:
        raise ValueError(f"{label} must be nonblank and NUL-free")
    return value


def _logical_installed_path(value: str, label: str) -> str:
    """Accept one normalized drive-qualified Windows observation, never a locator."""

    text = _nonblank(value, label)
    if "/" in text or "%2e" in text.lower() or "%2f" in text.lower() or "%5c" in text.lower():
        raise ValueError(f"{label} must not contain alternate or encoded separators")
    if re.fullmatch(r'[A-Za-z]:\\(?:[^\\/:?*"<>|]+\\)*[^\\/:?*"<>|]+', text) is None:
        raise ValueError(f"{label} must be a normalized drive-qualified Windows absolute path")
    if any(segment in (".", "..") for segment in text.split("\\")):
        raise ValueError(f"{label} must not contain traversal components")
    if any(segment.endswith((" ", ".")) for segment in text.split("\\")):
        raise ValueError(f"{label} must not contain Windows-ambiguous segments")
    return text


class OracleAction(str, Enum):
    MARKETPLACE_ADD = "MARKETPLACE_ADD"
    MARKETPLACE_LIST = "MARKETPLACE_LIST"
    MARKETPLACE_REMOVE = "MARKETPLACE_REMOVE"
    PLUGIN_ADD = "PLUGIN_ADD"
    PLUGIN_LIST = "PLUGIN_LIST"
    PLUGIN_REMOVE = "PLUGIN_REMOVE"
    VERSION = "VERSION"
    ABSENCE = "ABSENCE"

    @property
    def surface(self) -> CodexProtocolSurface:
        surfaces = {
            OracleAction.MARKETPLACE_ADD: CodexProtocolSurface.MARKETPLACE_ADD,
            OracleAction.MARKETPLACE_LIST: CodexProtocolSurface.MARKETPLACE_LIST,
            OracleAction.MARKETPLACE_REMOVE: CodexProtocolSurface.MARKETPLACE_REMOVE,
            OracleAction.PLUGIN_ADD: CodexProtocolSurface.PLUGIN_ADD,
            OracleAction.PLUGIN_LIST: CodexProtocolSurface.PLUGIN_LIST,
            OracleAction.PLUGIN_REMOVE: CodexProtocolSurface.PLUGIN_REMOVE,
            OracleAction.VERSION: CodexProtocolSurface.VERSION,
            OracleAction.ABSENCE: CodexProtocolSurface.PLUGIN_LIST,
        }
        return surfaces[self]


class OracleBlockReason(str, Enum):
    INVALID_LEASE = "INVALID_LEASE"
    INITIALIZATION_FAILED = "INITIALIZATION_FAILED"
    COMMAND_INVALID = "COMMAND_INVALID"
    COMMAND_CLEANUP_FAILED = "COMMAND_CLEANUP_FAILED"
    STATE_MISSING = "STATE_MISSING"
    STATE_INVALID = "STATE_INVALID"
    TOPOLOGY_INVALID = "TOPOLOGY_INVALID"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    PROCESS_FAILED = "PROCESS_FAILED"
    PROTOCOL_REJECTED = "PROTOCOL_REJECTED"
    ABSENCE_NOT_PROVEN = "ABSENCE_NOT_PROVEN"


class OracleChildExitCode(IntEnum):
    SUCCESS = 0
    COMMAND_INVALID = 64
    STATE_MISSING = 65
    STATE_INVALID = 66
    TOPOLOGY_INVALID = 67
    DIGEST_MISMATCH = 68
    IO_FAILED = 69

    @property
    def block_reason(self) -> OracleBlockReason:
        reasons = {
            OracleChildExitCode.COMMAND_INVALID: OracleBlockReason.COMMAND_INVALID,
            OracleChildExitCode.STATE_MISSING: OracleBlockReason.STATE_MISSING,
            OracleChildExitCode.STATE_INVALID: OracleBlockReason.STATE_INVALID,
            OracleChildExitCode.TOPOLOGY_INVALID: OracleBlockReason.TOPOLOGY_INVALID,
            OracleChildExitCode.DIGEST_MISMATCH: OracleBlockReason.DIGEST_MISMATCH,
            OracleChildExitCode.IO_FAILED: OracleBlockReason.PROCESS_FAILED,
        }
        return reasons.get(self, OracleBlockReason.PROCESS_FAILED)


class OracleIdentity(StrictModel):
    marketplace_name: str
    marketplace_root: str
    plugin_id: str
    plugin_name: str
    plugin_version: str
    plugin_source: str
    plugin_install_policy: str
    plugin_auth_policy: str
    plugin_installed_path: str

    _text = field_validator(
        "marketplace_name",
        "marketplace_root",
        "plugin_id",
        "plugin_name",
        "plugin_version",
        "plugin_source",
        "plugin_install_policy",
        "plugin_auth_policy",
        "plugin_installed_path",
    )(classmethod(lambda cls, value: _nonblank(value, "identity field")))

    @field_validator("plugin_installed_path")
    @classmethod
    def exact_logical_installed_path(cls, value: str) -> str:
        return _logical_installed_path(value, "plugin installed path")

    @model_validator(mode="after")
    def canonical_effect_names(self) -> OracleIdentity:
        values = (self.marketplace_name, self.plugin_id)
        if any(re.fullmatch(r"[a-z][a-z0-9-]*", value) is None for value in values):
            raise ValueError("owned identity names must be canonical segments")
        return self


class OracleCommand(StrictModel):
    action: OracleAction
    identity: OracleIdentity


class OracleMarketplaceRecord(StrictModel):
    name: str
    root: str
    locator: str
    digest: str

    _text = field_validator("name", "root", "locator", "digest")(classmethod(lambda cls, value: _nonblank(value, "marketplace field")))

    @model_validator(mode="after")
    def exact_marketplace_locator(self) -> OracleMarketplaceRecord:
        if self.locator != f"marketplaces/{self.name}.json" or re.fullmatch(r"[0-9a-f]{64}", self.digest) is None:
            raise ValueError("marketplace record has an invalid owned locator or digest")
        return self


class OraclePluginRecord(StrictModel):
    plugin_id: str
    name: str
    marketplace_name: str
    version: str
    source: str
    install_policy: str
    auth_policy: str
    installed_path: str
    locator: str
    digest: str

    _text = field_validator(
        "plugin_id",
        "name",
        "marketplace_name",
        "version",
        "source",
        "install_policy",
        "auth_policy",
        "installed_path",
        "locator",
        "digest",
    )(classmethod(lambda cls, value: _nonblank(value, "plugin field")))

    @field_validator("installed_path")
    @classmethod
    def exact_logical_installed_path(cls, value: str) -> str:
        return _logical_installed_path(value, "plugin installed path")

    @model_validator(mode="after")
    def exact_plugin_locator(self) -> OraclePluginRecord:
        if self.locator != f"plugins/{self.plugin_id}.json" or re.fullmatch(r"[0-9a-f]{64}", self.digest) is None:
            raise ValueError("plugin record has an invalid owned locator or digest")
        return self


class OracleState(StrictModel):
    owner: EnvironmentOwnerId
    environment_id: EnvironmentId
    codex_version: str
    marketplaces: tuple[OracleMarketplaceRecord, ...]
    plugins: tuple[OraclePluginRecord, ...]
    foreign_marketplaces: tuple[OracleMarketplaceRecord, ...]
    foreign_plugins: tuple[OraclePluginRecord, ...]

    _version = field_validator("codex_version")(classmethod(lambda cls, value: _nonblank(value, "codex version")))

    @model_validator(mode="after")
    def unique_collection_identities(self) -> OracleState:
        marketplace_collections = (self.marketplaces, self.foreign_marketplaces)
        plugin_collections = (self.plugins, self.foreign_plugins)
        marketplace_duplicates = any(
            len({record.name for record in collection}) != len(collection)
            for collection in marketplace_collections
        )
        plugin_duplicates = any(
            len({record.plugin_id for record in collection}) != len(collection)
            for collection in plugin_collections
        )
        if marketplace_duplicates or plugin_duplicates:
            raise ValueError("state collection contains duplicate identities")
        return self


@dataclass(frozen=True)
class OracleCompleted:
    response: CodexProtocolAccepted


@dataclass(frozen=True)
class OracleAbsent:
    action: OracleAction = OracleAction.ABSENCE


@dataclass(frozen=True)
class OracleForeignSeeded:
    collection: str


@dataclass(frozen=True)
class OracleBlocked:
    reason: OracleBlockReason


OracleRunResult: TypeAlias = OracleCompleted | OracleAbsent | OracleBlocked


def revalidate_command(command: OracleCommand) -> OracleCommand | OracleBlocked:
    """Reject constructed commands before a command-file write."""

    try:
        return OracleCommand.model_validate(command.model_dump(warnings=False))
    except (AttributeError, ValidationError, ValueError):
        return OracleBlocked(reason=OracleBlockReason.COMMAND_INVALID)


def validated_state_path(lease: EnvironmentLease) -> Path:
    """Return the fixed state locator only for a strict live lease."""

    validated = revalidate_lease(lease)
    if not isinstance(validated, EnvironmentLease):
        raise ValueError("invalid lease")
    return validated.codex_home.absolute.path / ORACLE_STATE_FILE_NAME


def validated_command_path(lease: EnvironmentLease) -> Path:
    """Return the fixed command locator only for a strict live lease."""

    validated = revalidate_lease(lease)
    if not isinstance(validated, EnvironmentLease):
        raise ValueError("invalid lease")
    return validated.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME


def validated_payload_root(lease: EnvironmentLease) -> Path:
    """Return the fixed payload directory only for a strict live lease."""

    validated = revalidate_lease(lease)
    if not isinstance(validated, EnvironmentLease):
        raise ValueError("invalid lease")
    return validated.codex_home.absolute.path / ORACLE_PAYLOAD_DIRECTORY_NAME
