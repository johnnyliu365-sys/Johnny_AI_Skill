"""Persisted lifecycle oracle composed only from the integrated 05S1-05S3 seams."""

from __future__ import annotations

import hashlib
from pathlib import Path
import stat

from pydantic import BaseModel, ValidationError

from library.local_orchestration.host_contracts import CodexMarketplaceSource, CodexPluginEntry, CodexPluginList
from tests.staging.codex_protocol.contracts import CodexProtocolAccepted, CodexProtocolRejected, CodexProtocolSurface
from tests.staging.codex_protocol.fixture import CodexProtocolFixture
from tests.staging.environment_core.contracts import EnvironmentLease, revalidate_lease

from .contracts import (
    ORACLE_PAYLOAD_DIRECTORY_NAME,
    ORACLE_STAGING_CODEX_VERSION,
    OracleAction,
    OracleBlockReason,
    OracleBlocked,
    OracleCommand,
    OracleCompleted,
    OracleForeignSeeded,
    OracleIdentity,
    OracleInstalledPathPresent,
    OracleMarketplaceRecord,
    OraclePluginRecord,
    OracleRunResult,
    OracleState,
    OracleAbsent,
    revalidate_command,
    validated_command_path,
    validated_payload_root,
    validated_state_path,
)
from .protocol_runner import CodexLifecycleOracleRunner


_ACCEPTED_RESPONSE_FIELDS = ("surface", "payload")
_PLUGIN_LIST_FIELDS = ("installed", "available")
_PLUGIN_ENTRY_FIELDS = (
    "pluginId",
    "name",
    "marketplaceName",
    "version",
    "installed",
    "enabled",
    "source",
    "installPolicy",
    "authPolicy",
    "marketplaceSource",
)
_MARKETPLACE_SOURCE_FIELDS = ("type", "value")


class CodexLifecycleOracle:
    """Issues fixed command files and accepts only a new child-produced 05S3 response."""

    def __init__(self, runner: CodexLifecycleOracleRunner) -> None:
        self._runner = runner
        self._fixture = CodexProtocolFixture.with_concrete_response_file(runner)

    def initialize(self, lease: EnvironmentLease) -> OracleBlocked | OracleCompleted:
        validated = revalidate_lease(lease)
        if not isinstance(validated, EnvironmentLease):
            return OracleBlocked(reason=OracleBlockReason.INVALID_LEASE)
        try:
            state_path = validated_state_path(validated)
            payload_root = validated_payload_root(validated)
            if state_path.exists() or _is_reparse(state_path):
                return OracleBlocked(reason=OracleBlockReason.INITIALIZATION_FAILED)
            payload_root.mkdir()
            if not _is_plain_directory(payload_root):
                return OracleBlocked(reason=OracleBlockReason.INITIALIZATION_FAILED)
            state = OracleState(
                owner=validated.owner,
                environment_id=validated.environment_id,
                codex_version=ORACLE_STAGING_CODEX_VERSION,
                marketplaces=(),
                plugins=(),
                foreign_marketplaces=(),
                foreign_plugins=(),
            )
            _write_state(state_path, state)
        except (OSError, ValidationError, ValueError):
            return OracleBlocked(reason=OracleBlockReason.INITIALIZATION_FAILED)
        command = OracleCommand(action=OracleAction.MARKETPLACE_LIST, identity=_default_identity())
        result = self.run(validated, command)
        if isinstance(result, (OracleAbsent, OracleInstalledPathPresent)):
            return OracleBlocked(reason=OracleBlockReason.PROCESS_FAILED)
        return result

    def run(self, lease: EnvironmentLease, command: OracleCommand) -> OracleRunResult:
        validated_lease = revalidate_lease(lease)
        if not isinstance(validated_lease, EnvironmentLease):
            return OracleBlocked(reason=OracleBlockReason.INVALID_LEASE)
        validated_command = revalidate_command(command)
        if isinstance(validated_command, OracleBlocked):
            return validated_command
        try:
            command_path = validated_command_path(validated_lease)
        except (OSError, ValueError):
            return OracleBlocked(reason=OracleBlockReason.PROCESS_FAILED)
        try:
            if command_path.exists() or _is_reparse(command_path):
                return OracleBlocked(reason=OracleBlockReason.COMMAND_INVALID)
        except OSError:
            return OracleBlocked(reason=OracleBlockReason.PROCESS_FAILED)
        try:
            command_path.write_text(validated_command.model_dump_json(warnings=False), encoding="utf-8")
            if not _is_plain_file(command_path):
                return _blocked_after_command_cleanup(command_path, OracleBlockReason.COMMAND_INVALID)
            response = self._fixture.run(validated_lease, validated_command.action.surface)
        except (OSError, ValueError):
            return _blocked_after_command_cleanup(command_path, OracleBlockReason.PROCESS_FAILED)
        cleanup_ok = _remove_exact_file(command_path)
        if not cleanup_ok:
            return OracleBlocked(reason=OracleBlockReason.COMMAND_CLEANUP_FAILED)
        if isinstance(response, CodexProtocolRejected):
            if response.reason.value == "PROCESS_FAILED":
                return OracleBlocked(reason=self._runner.last_block_reason)
            return OracleBlocked(reason=OracleBlockReason.PROTOCOL_REJECTED)
        if validated_command.action is OracleAction.ABSENCE:
            return self._absence_result(validated_lease, validated_command, response)
        return OracleCompleted(response=response)

    def seed_foreign_plugin(self, lease: EnvironmentLease, record: OraclePluginRecord) -> OracleForeignSeeded | OracleBlocked:
        return self._seed_foreign(lease, record, "foreign_plugins")

    def seed_foreign_marketplace(self, lease: EnvironmentLease, record: OracleMarketplaceRecord) -> OracleForeignSeeded | OracleBlocked:
        return self._seed_foreign(lease, record, "foreign_marketplaces")

    def state_path(self, lease: EnvironmentLease) -> Path:
        return validated_state_path(lease)

    def payload_root(self, lease: EnvironmentLease) -> Path:
        return validated_payload_root(lease)

    def _absence_result(
        self,
        lease: EnvironmentLease,
        command: OracleCommand,
        response: CodexProtocolAccepted,
    ) -> OracleRunResult:
        payload = _revalidate_absence_payload(response)
        if payload is None:
            return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
        try:
            state_path = validated_state_path(lease)
            payload_root = validated_payload_root(lease)
            state = _read_state(state_path)
            if state.plugins:
                if len(state.plugins) != 1:
                    return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
                plugin = state.plugins[0]
                if not _plugin_matches_identity(plugin, command.identity):
                    return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
                if len(state.marketplaces) != 1 or not _marketplace_matches_identity(
                    state.marketplaces[0], command.identity
                ):
                    return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
                if not _exact_plugin_payload(payload_root, plugin):
                    return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
                if not _plugin_list_matches_state(payload, state):
                    return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
                return OracleInstalledPathPresent()
            owned_plugin_path = payload_root / "plugins" / f"{command.identity.plugin_id}.json"
            if owned_plugin_path.exists() or _is_reparse(owned_plugin_path):
                return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
            expected_foreign_plugins = tuple(
                (
                    record.plugin_id,
                    record.name,
                    record.marketplace_name,
                    record.version,
                    record.source,
                    record.install_policy,
                    record.auth_policy,
                )
                for record in state.foreign_plugins
            )
            actual_plugins = tuple(
                (
                    entry.pluginId,
                    entry.name,
                    entry.marketplaceName,
                    entry.version,
                    entry.source,
                    entry.installPolicy,
                    entry.authPolicy,
                )
                for entry in payload.installed
            )
            if actual_plugins != expected_foreign_plugins or payload.available:
                return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
        except (OSError, ValueError):
            return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
        return OracleAbsent()

    def _seed_foreign(
        self,
        lease: EnvironmentLease,
        record: OracleMarketplaceRecord | OraclePluginRecord,
        collection: str,
    ) -> OracleForeignSeeded | OracleBlocked:
        try:
            state_path = validated_state_path(lease)
            payload_root = validated_payload_root(lease)
            state = _read_state(state_path)
            data = state.model_dump()
            value = data[collection]
            assert isinstance(value, tuple)
            data[collection] = (*value, record.model_dump())
            updated = OracleState.model_validate(data)
            _write_foreign_payload(payload_root, record)
            _write_state(state_path, updated)
        except (OSError, ValidationError, ValueError):
            return OracleBlocked(reason=OracleBlockReason.STATE_INVALID)
        return OracleForeignSeeded(collection=collection)


def _default_identity() -> OracleIdentity:
    return OracleIdentity(
        marketplace_name="oracle-market",
        marketplace_root="oracle-root",
        plugin_id="oracle-plugin",
        plugin_name="oracle-plugin-name",
        plugin_version="v1",
        plugin_source="oracle-source",
        plugin_install_policy="oracle-policy",
        plugin_auth_policy="oracle-auth",
        plugin_installed_path=r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\oracle-plugin",
    )


def _revalidate_absence_payload(response: CodexProtocolAccepted) -> CodexPluginList | None:
    if type(response) is not CodexProtocolAccepted:
        return None
    response_state = _exact_model_state(response, _ACCEPTED_RESPONSE_FIELDS)
    if response_state is None:
        return None
    surface = response_state["surface"]
    payload = response_state["payload"]
    if type(surface) is not CodexProtocolSurface or surface is not CodexProtocolSurface.PLUGIN_LIST:
        return None
    if type(payload) is not CodexPluginList or not _exact_plugin_list(payload):
        return None
    try:
        rebuilt = CodexProtocolAccepted.model_validate(response.model_dump(warnings=False))
    except (AttributeError, ValidationError, ValueError):
        return None
    if type(rebuilt) is not CodexProtocolAccepted or type(rebuilt.payload) is not CodexPluginList:
        return None
    return rebuilt.payload


def _plugin_matches_identity(record: OraclePluginRecord, identity: OracleIdentity) -> bool:
    return (
        record.plugin_id == identity.plugin_id
        and record.name == identity.plugin_name
        and record.marketplace_name == identity.marketplace_name
        and record.version == identity.plugin_version
        and record.source == identity.plugin_source
        and record.install_policy == identity.plugin_install_policy
        and record.auth_policy == identity.plugin_auth_policy
        and record.installed_path == identity.plugin_installed_path
        and record.locator == f"plugins/{identity.plugin_id}.json"
    )


def _marketplace_matches_identity(record: OracleMarketplaceRecord, identity: OracleIdentity) -> bool:
    return (
        record.name == identity.marketplace_name
        and record.root == identity.marketplace_root
        and record.locator == f"marketplaces/{identity.marketplace_name}.json"
    )


def _exact_plugin_payload(payload_root: Path, record: OraclePluginRecord) -> bool:
    if record.locator != f"plugins/{record.plugin_id}.json":
        return False
    path = payload_root / record.locator
    if path.parent.parent != payload_root or not _is_plain_file(path):
        return False
    try:
        actual = path.read_bytes()
    except OSError:
        return False
    expected = _plugin_payload(record)
    return actual == expected and hashlib.sha256(actual).hexdigest() == record.digest


def _plugin_list_matches_state(payload: CodexPluginList, state: OracleState) -> bool:
    if payload.available:
        return False
    expected = tuple(
        _state_plugin_tuple(record)
        for record in (*state.plugins, *state.foreign_plugins)
    )
    actual: list[tuple[str, str, str, str, bool, bool, str, str, str, str, str]] = []
    for entry in payload.installed:
        observed = _response_plugin_tuple(entry)
        if observed is None:
            return False
        actual.append(observed)
    return tuple(actual) == expected


def _state_plugin_tuple(
    record: OraclePluginRecord,
) -> tuple[str, str, str, str, bool, bool, str, str, str, str, str]:
    return (
        record.plugin_id,
        record.name,
        record.marketplace_name,
        record.version,
        True,
        True,
        record.source,
        record.install_policy,
        record.auth_policy,
        "local",
        "oracle-source",
    )


def _response_plugin_tuple(
    entry: CodexPluginEntry,
) -> tuple[str, str, str, str, bool, bool, str, str, str, str, str] | None:
    if not _exact_plugin_entry(entry):
        return None
    source = entry.marketplaceSource
    if type(source) is not CodexMarketplaceSource:
        return None
    return (
        entry.pluginId,
        entry.name,
        entry.marketplaceName,
        entry.version,
        entry.installed,
        entry.enabled,
        entry.source,
        entry.installPolicy,
        entry.authPolicy,
        source.type,
        source.value,
    )


def _exact_plugin_list(value: CodexPluginList) -> bool:
    state = _exact_model_state(value, _PLUGIN_LIST_FIELDS)
    if state is None:
        return False
    installed = state["installed"]
    available = state["available"]
    if type(installed) is not tuple or type(available) is not tuple:
        return False
    return all(_exact_plugin_entry(entry) for entry in (*installed, *available))


def _exact_plugin_entry(value: object) -> bool:
    if type(value) is not CodexPluginEntry:
        return False
    state = _exact_model_state(value, _PLUGIN_ENTRY_FIELDS)
    if state is None:
        return False
    text_fields = ("pluginId", "name", "marketplaceName", "version", "source", "installPolicy", "authPolicy")
    if any(type(state[field]) is not str for field in text_fields):
        return False
    if type(state["installed"]) is not bool or type(state["enabled"]) is not bool:
        return False
    source = state["marketplaceSource"]
    return type(source) is CodexMarketplaceSource and _exact_marketplace_source(source)


def _exact_marketplace_source(value: CodexMarketplaceSource) -> bool:
    state = _exact_model_state(value, _MARKETPLACE_SOURCE_FIELDS)
    return state is not None and type(state["type"]) is str and type(state["value"]) is str


def _exact_model_state(value: BaseModel, fields: tuple[str, ...]) -> dict[str, object] | None:
    state = value.__dict__
    fields_set = value.__pydantic_fields_set__
    if type(state) is not dict or value.__pydantic_extra__ is not None or value.__pydantic_private__ is not None:
        return None
    if type(fields_set) is not set or len(state) != len(fields) or len(fields_set) != len(fields):
        return None
    if any(type(key) is not str for key in state) or any(type(field) is not str for field in fields_set):
        return None
    if any(field not in state or field not in fields_set for field in fields):
        return None
    return {field: state[field] for field in fields}


def _read_state(path: Path) -> OracleState:
    if not _is_plain_file(path):
        raise ValueError("state file unavailable")
    return OracleState.model_validate_json(path.read_text(encoding="utf-8"))


def _write_state(path: Path, state: OracleState) -> None:
    temporary = path.with_suffix(".next")
    temporary.write_text(state.model_dump_json(warnings=False), encoding="utf-8")
    temporary.replace(path)


def _write_foreign_payload(payload_root: Path, record: OracleMarketplaceRecord | OraclePluginRecord) -> None:
    target = payload_root / record.locator
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = _marketplace_payload(record) if isinstance(record, OracleMarketplaceRecord) else _plugin_payload(record)
    target.write_bytes(payload)


def _marketplace_payload(record: OracleMarketplaceRecord) -> bytes:
    return f"marketplace|{record.name}|{record.root}".encode("utf-8")


def _plugin_payload(record: OraclePluginRecord) -> bytes:
    return (
        f"plugin|{record.plugin_id}|{record.name}|{record.marketplace_name}|{record.version}|{record.source}|"
        f"{record.install_policy}|{record.auth_policy}|{record.installed_path}"
    ).encode("utf-8")


def _remove_exact_file(path: Path) -> bool:
    if not path.exists():
        return True
    if not _is_plain_file(path):
        return False
    try:
        path.unlink()
    except OSError:
        return False
    return True


def _blocked_after_command_cleanup(command_path: Path, reason: OracleBlockReason) -> OracleBlocked:
    if not _remove_exact_file(command_path):
        return OracleBlocked(reason=OracleBlockReason.COMMAND_CLEANUP_FAILED)
    return OracleBlocked(reason=reason)


def _is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except FileNotFoundError:
        return False
    except OSError:
        return True
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _is_plain_file(path: Path) -> bool:
    if _is_reparse(path):
        return False
    try:
        return path.is_file() and path.resolve(strict=True) == path
    except OSError:
        return False


def _is_plain_directory(path: Path) -> bool:
    if _is_reparse(path):
        return False
    try:
        return path.is_dir() and path.resolve(strict=True) == path
    except OSError:
        return False
