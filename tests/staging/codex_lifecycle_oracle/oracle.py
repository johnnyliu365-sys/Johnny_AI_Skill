"""Persisted lifecycle oracle composed only from the integrated 05S1-05S3 seams."""

from __future__ import annotations

from pathlib import Path
import stat

from pydantic import ValidationError

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
        if isinstance(result, OracleAbsent):
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
        if response.surface is not CodexProtocolSurface.PLUGIN_LIST:
            return OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN)
        try:
            state_path = validated_state_path(lease)
            payload_root = validated_payload_root(lease)
            owned_paths = (
                payload_root / "marketplaces" / f"{command.identity.marketplace_name}.json",
                payload_root / "plugins" / f"{command.identity.plugin_id}.json",
            )
            if state_path.exists() or any(path.exists() or _is_reparse(path) for path in owned_paths):
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
