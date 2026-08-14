"""Pure exact projection of compensation-oracle responses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict, ValidationError

from library.local_orchestration.host_contracts import (
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceSource,
    CodexPluginEntry,
    CodexPluginList,
)
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceRemove,
    CodexPluginRemove,
    CodexProtocolAccepted,
    CodexProtocolPayload,
    CodexProtocolSurface,
)

from .contracts import OracleAbsent, OracleAction, OracleBlocked, OracleCompleted, OracleInstalledPathPresent


class _StrictModel(BaseModel):
    """Keep the returned rejection a closed metadata-only value."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class CodexOracleResponseRejectReason(str, Enum):
    """Finite reasons that do not retain an oracle value or diagnostic."""

    INVALID_ACTION = "INVALID_ACTION"
    UNSUPPORTED_ACTION = "UNSUPPORTED_ACTION"
    INVALID_RESULT = "INVALID_RESULT"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    SURFACE_MISMATCH = "SURFACE_MISMATCH"
    ACTION_RESULT_MISMATCH = "ACTION_RESULT_MISMATCH"
    DEPENDENCY_BLOCKED = "DEPENDENCY_BLOCKED"


class CodexOracleResponseRejected(_StrictModel):
    """One finite rejection without raw reason, response, path or exception."""

    status: Literal["INVALID_RESPONSE"] = "INVALID_RESPONSE"
    reason: CodexOracleResponseRejectReason


CodexOracleResponseAdmission: TypeAlias = (
    CodexProtocolAccepted | OracleAbsent | OracleInstalledPathPresent | CodexOracleResponseRejected
)


@dataclass(frozen=True)
class _MarketplaceSourceAbsent:
    status: Literal["ABSENT"] = "ABSENT"


@dataclass(frozen=True)
class _MarketplaceSourceRebuiltValid:
    source: CodexMarketplaceSource
    status: Literal["REBUILT_VALID"] = "REBUILT_VALID"


@dataclass(frozen=True)
class _MarketplaceSourcePresentInvalid:
    status: Literal["PRESENT_INVALID"] = "PRESENT_INVALID"


_MarketplaceSourceAdmission: TypeAlias = (
    _MarketplaceSourceAbsent | _MarketplaceSourceRebuiltValid | _MarketplaceSourcePresentInvalid
)


_PROTOCOL_FIELDS: Final[tuple[str, ...]] = ("surface", "payload")
_PLUGIN_REMOVE_FIELDS: Final[tuple[str, ...]] = ("pluginId", "name", "marketplaceName")
_MARKETPLACE_REMOVE_FIELDS: Final[tuple[str, ...]] = ("marketplaceName", "installedRoot")
_MARKETPLACE_SOURCE_FIELDS: Final[tuple[str, ...]] = ("type", "value")
_MARKETPLACE_ENTRY_FIELDS: Final[tuple[str, ...]] = ("name", "root")
_PLUGIN_ENTRY_FIELDS: Final[tuple[str, ...]] = (
    "pluginId",
    "name",
    "marketplaceName",
    "version",
    "installed",
    "enabled",
    "source",
    "installPolicy",
    "authPolicy",
)
_MARKETPLACE_LIST_FIELDS: Final[tuple[str, ...]] = ("marketplaces",)
_PLUGIN_LIST_FIELDS: Final[tuple[str, ...]] = ("installed", "available")


def admit_codex_oracle_response(value: object, action: OracleAction) -> CodexOracleResponseAdmission:
    """Rebuild one exact response for one expected compensation action."""

    if type(action) is not OracleAction:
        return _rejected(CodexOracleResponseRejectReason.INVALID_ACTION)
    if not _is_supported_action(action):
        return _rejected(CodexOracleResponseRejectReason.UNSUPPORTED_ACTION)

    if type(value) is OracleBlocked:
        if _exact_dataclass_state(value, OracleBlocked, ("reason",)) is None:
            return _rejected(CodexOracleResponseRejectReason.INVALID_RESULT)
        return _rejected(CodexOracleResponseRejectReason.DEPENDENCY_BLOCKED)

    if type(value) is OracleAbsent:
        return _admit_absence(value, action)

    if type(value) is OracleInstalledPathPresent:
        return _admit_installed_path_present(value, action)

    if type(value) is not OracleCompleted:
        return _rejected(CodexOracleResponseRejectReason.INVALID_RESULT)

    completed_state = _exact_dataclass_state(value, OracleCompleted, ("response",))
    if completed_state is None:
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)
    if action is OracleAction.ABSENCE:
        return _rejected(CodexOracleResponseRejectReason.ACTION_RESULT_MISMATCH)

    expected_surface = _surface_for_action(action)
    if expected_surface is None:
        return _rejected(CodexOracleResponseRejectReason.UNSUPPORTED_ACTION)
    response = completed_state["response"]
    response_state = _exact_model_state(response, CodexProtocolAccepted, _PROTOCOL_FIELDS)
    if response_state is None:
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)
    surface = response_state["surface"]
    if type(surface) is not CodexProtocolSurface:
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)
    if surface is not expected_surface:
        return _rejected(CodexOracleResponseRejectReason.SURFACE_MISMATCH)

    payload = _rebuild_payload(expected_surface, response_state["payload"])
    if payload is None:
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)
    try:
        return CodexProtocolAccepted(surface=expected_surface, payload=payload)
    except (TypeError, ValidationError, ValueError):
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)


def _admit_absence(value: OracleAbsent, action: OracleAction) -> CodexOracleResponseAdmission:
    state = _exact_dataclass_state(value, OracleAbsent, ("action",))
    if state is None:
        return _rejected(CodexOracleResponseRejectReason.INVALID_RESULT)
    observed_action = state["action"]
    if type(observed_action) is not OracleAction or observed_action is not OracleAction.ABSENCE:
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)
    if action is not OracleAction.ABSENCE:
        return _rejected(CodexOracleResponseRejectReason.ACTION_RESULT_MISMATCH)
    return OracleAbsent()


def _admit_installed_path_present(
    value: OracleInstalledPathPresent,
    action: OracleAction,
) -> CodexOracleResponseAdmission:
    state = _exact_dataclass_state(value, OracleInstalledPathPresent, ("action",))
    if state is None:
        return _rejected(CodexOracleResponseRejectReason.INVALID_RESULT)
    observed_action = state["action"]
    if type(observed_action) is not OracleAction or observed_action is not OracleAction.ABSENCE:
        return _rejected(CodexOracleResponseRejectReason.MALFORMED_RESPONSE)
    if action is not OracleAction.ABSENCE:
        return _rejected(CodexOracleResponseRejectReason.ACTION_RESULT_MISMATCH)
    return OracleInstalledPathPresent()


def _rebuild_payload(surface: CodexProtocolSurface, value: object) -> CodexProtocolPayload | None:
    if surface is CodexProtocolSurface.PLUGIN_REMOVE:
        return _rebuild_plugin_remove(value)
    if surface is CodexProtocolSurface.MARKETPLACE_REMOVE:
        return _rebuild_marketplace_remove(value)
    if surface is CodexProtocolSurface.PLUGIN_LIST:
        return _rebuild_plugin_list(value)
    if surface is CodexProtocolSurface.MARKETPLACE_LIST:
        return _rebuild_marketplace_list(value)
    return None


def _rebuild_plugin_remove(value: object) -> CodexPluginRemove | None:
    state = _exact_model_state(value, CodexPluginRemove, _PLUGIN_REMOVE_FIELDS)
    if state is None:
        return None
    plugin_id = _text(state, "pluginId")
    name = _text(state, "name")
    marketplace_name = _text(state, "marketplaceName")
    if plugin_id is None or name is None or marketplace_name is None:
        return None
    try:
        return CodexPluginRemove(pluginId=plugin_id, name=name, marketplaceName=marketplace_name)
    except (TypeError, ValidationError, ValueError):
        return None


def _rebuild_marketplace_remove(value: object) -> CodexMarketplaceRemove | None:
    state = _exact_model_state(value, CodexMarketplaceRemove, _MARKETPLACE_REMOVE_FIELDS)
    if state is None:
        return None
    marketplace_name = _text(state, "marketplaceName")
    installed_root = _text(state, "installedRoot")
    if marketplace_name is None or installed_root is None:
        return None
    try:
        return CodexMarketplaceRemove(marketplaceName=marketplace_name, installedRoot=installed_root)
    except (TypeError, ValidationError, ValueError):
        return None


def _rebuild_plugin_list(value: object) -> CodexPluginList | None:
    state = _exact_model_state(value, CodexPluginList, _PLUGIN_LIST_FIELDS)
    if state is None:
        return None
    installed = state["installed"]
    available = state["available"]
    if type(installed) is not tuple or type(available) is not tuple:
        return None
    rebuilt_installed: list[CodexPluginEntry] = []
    rebuilt_available: list[CodexPluginEntry] = []
    for entry in cast(tuple[object, ...], installed):
        rebuilt = _rebuild_plugin_entry(entry)
        if rebuilt is None:
            return None
        rebuilt_installed.append(rebuilt)
    for entry in cast(tuple[object, ...], available):
        rebuilt = _rebuild_plugin_entry(entry)
        if rebuilt is None:
            return None
        rebuilt_available.append(rebuilt)
    try:
        return CodexPluginList(installed=tuple(rebuilt_installed), available=tuple(rebuilt_available))
    except (TypeError, ValidationError, ValueError):
        return None


def _rebuild_marketplace_list(value: object) -> CodexMarketplaceList | None:
    state = _exact_model_state(value, CodexMarketplaceList, _MARKETPLACE_LIST_FIELDS)
    if state is None:
        return None
    marketplaces = state["marketplaces"]
    if type(marketplaces) is not tuple:
        return None
    rebuilt_marketplaces: list[CodexMarketplaceEntry] = []
    for entry in cast(tuple[object, ...], marketplaces):
        rebuilt = _rebuild_marketplace_entry(entry)
        if rebuilt is None:
            return None
        rebuilt_marketplaces.append(rebuilt)
    try:
        return CodexMarketplaceList(marketplaces=tuple(rebuilt_marketplaces))
    except (TypeError, ValidationError, ValueError):
        return None


def _rebuild_plugin_entry(value: object) -> CodexPluginEntry | None:
    state = _exact_model_state(value, CodexPluginEntry, _PLUGIN_ENTRY_FIELDS, ("marketplaceSource",))
    if state is None:
        return None
    plugin_id = _text(state, "pluginId")
    name = _text(state, "name")
    marketplace_name = _text(state, "marketplaceName")
    version = _text(state, "version")
    installed = _boolean(state, "installed")
    enabled = _boolean(state, "enabled")
    source = _text(state, "source")
    install_policy = _text(state, "installPolicy")
    auth_policy = _text(state, "authPolicy")
    marketplace_source = _rebuild_marketplace_source(state["marketplaceSource"])
    if isinstance(marketplace_source, _MarketplaceSourcePresentInvalid):
        return None
    if (
        plugin_id is None
        or name is None
        or marketplace_name is None
        or version is None
        or installed is None
        or enabled is None
        or source is None
        or install_policy is None
        or auth_policy is None
    ):
        return None
    try:
        if isinstance(marketplace_source, _MarketplaceSourceAbsent):
            return CodexPluginEntry(
                pluginId=plugin_id,
                name=name,
                marketplaceName=marketplace_name,
                version=version,
                installed=installed,
                enabled=enabled,
                source=source,
                installPolicy=install_policy,
                authPolicy=auth_policy,
            )
        return CodexPluginEntry(
            pluginId=plugin_id,
            name=name,
            marketplaceName=marketplace_name,
            version=version,
            installed=installed,
            enabled=enabled,
            source=source,
            installPolicy=install_policy,
            authPolicy=auth_policy,
            marketplaceSource=marketplace_source.source,
        )
    except (TypeError, ValidationError, ValueError):
        return None


def _rebuild_marketplace_entry(value: object) -> CodexMarketplaceEntry | None:
    state = _exact_model_state(value, CodexMarketplaceEntry, _MARKETPLACE_ENTRY_FIELDS, ("marketplaceSource",))
    if state is None:
        return None
    name = _text(state, "name")
    root = _text(state, "root")
    marketplace_source = _rebuild_marketplace_source(state["marketplaceSource"])
    if isinstance(marketplace_source, _MarketplaceSourcePresentInvalid):
        return None
    if name is None or root is None:
        return None
    try:
        if isinstance(marketplace_source, _MarketplaceSourceAbsent):
            return CodexMarketplaceEntry(name=name, root=root)
        return CodexMarketplaceEntry(name=name, root=root, marketplaceSource=marketplace_source.source)
    except (TypeError, ValidationError, ValueError):
        return None


def _rebuild_marketplace_source(value: object) -> _MarketplaceSourceAdmission:
    if value is None:
        return _MarketplaceSourceAbsent()
    state = _exact_model_state(value, CodexMarketplaceSource, _MARKETPLACE_SOURCE_FIELDS)
    if state is None:
        return _MarketplaceSourcePresentInvalid()
    source_type = _text(state, "type")
    source_value = _text(state, "value")
    if source_type is None or source_value is None:
        return _MarketplaceSourcePresentInvalid()
    try:
        return _MarketplaceSourceRebuiltValid(
            source=CodexMarketplaceSource(type=source_type, value=source_value)
        )
    except (TypeError, ValidationError, ValueError):
        return _MarketplaceSourcePresentInvalid()


def _surface_for_action(action: OracleAction) -> CodexProtocolSurface | None:
    if action is OracleAction.PLUGIN_REMOVE:
        return CodexProtocolSurface.PLUGIN_REMOVE
    if action is OracleAction.MARKETPLACE_REMOVE:
        return CodexProtocolSurface.MARKETPLACE_REMOVE
    if action is OracleAction.PLUGIN_LIST:
        return CodexProtocolSurface.PLUGIN_LIST
    if action is OracleAction.MARKETPLACE_LIST:
        return CodexProtocolSurface.MARKETPLACE_LIST
    return None


def _is_supported_action(action: OracleAction) -> bool:
    return action is OracleAction.ABSENCE or _surface_for_action(action) is not None


def _text(state: dict[str, object], field: str) -> str | None:
    value = state[field]
    return value if type(value) is str else None


def _boolean(state: dict[str, object], field: str) -> bool | None:
    value = state[field]
    return value if type(value) is bool else None


def _exact_model_state(
    value: object,
    expected_type: type[BaseModel],
    required_fields: tuple[str, ...],
    optional_fields: tuple[str, ...] = (),
) -> dict[str, object] | None:
    if type(value) is not expected_type:
        return None
    state = _model_state(value)
    if state is None:
        return None
    try:
        extras: object = object.__getattribute__(value, "__pydantic_extra__")
        private: object = object.__getattribute__(value, "__pydantic_private__")
        fields_set: object = object.__getattribute__(value, "__pydantic_fields_set__")
    except AttributeError:
        return None
    if extras is not None or private is not None or type(fields_set) is not set:
        return None
    allowed_fields = required_fields + optional_fields
    if len(state) != len(allowed_fields) or len(fields_set) < len(required_fields):
        return None
    if any(type(key) is not str for key in state) or any(type(key) is not str for key in fields_set):
        return None
    if any(field not in state or field not in fields_set for field in required_fields):
        return None
    if any(field not in state for field in optional_fields):
        return None
    if len(fields_set) > len(allowed_fields) or any(field not in allowed_fields for field in fields_set):
        return None
    for field in optional_fields:
        optional_value = state[field]
        if field in fields_set and optional_value is None:
            return None
        if field not in fields_set and optional_value is not None:
            return None
    return state


def _model_state(value: object) -> dict[str, object] | None:
    try:
        state: object = object.__getattribute__(value, "__dict__")
    except AttributeError:
        return None
    if type(state) is not dict:
        return None
    return cast(dict[str, object], state)


def _exact_dataclass_state(
    value: object,
    expected_type: type[object],
    expected_fields: tuple[str, ...],
) -> dict[str, object] | None:
    if type(value) is not expected_type:
        return None
    try:
        state: object = object.__getattribute__(value, "__dict__")
    except AttributeError:
        return None
    if type(state) is not dict:
        return None
    values = cast(dict[str, object], state)
    if len(values) != len(expected_fields):
        return None
    if any(type(key) is not str for key in values):
        return None
    if any(field not in values for field in expected_fields):
        return None
    return values


def _rejected(reason: CodexOracleResponseRejectReason) -> CodexOracleResponseRejected:
    return CodexOracleResponseRejected(status="INVALID_RESPONSE", reason=reason)
