"""Staging-only acceptance over the integrated registration receipt removal path."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, TypeAlias
from unittest.mock import patch

from pydantic import BaseModel, ConfigDict, ValidationError

from library.local_orchestration.codex_receipt_removal_composition import (
    CodexReceiptRemovalNotInstalled,
    CodexReceiptRemovalRemoved,
    compose_codex_receipt_removal,
)
from library.local_orchestration.codex_receipt_removal_request import (
    CodexReceiptRemovalInvocation,
    CodexReceiptRemovalReady,
    build_codex_receipt_removal_request,
)
from library.local_orchestration.codex_registration_contracts import CodexRegistrationReceipt
from library.local_orchestration.codex_registration_forward import (
    CodexRegistrationForwardCoordinator,
    admit_codex_registration_forward,
)
from library.local_orchestration.codex_registration_port import (
    CodexRegistrationPortCapability,
    CodexRegistrationPortRequest,
    admit_codex_registration_port,
    revalidate_registration_port_request,
)
from library.local_orchestration.codex_registration_proof_settlement import settle_codex_registration_proof
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationProofClaim,
    CodexRegistrationSettlementAuthority,
    admit_codex_registration_settlement_authority,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationNextReadyPhase,
    CodexRegistrationReadyLease,
)
from tests.staging.codex_lifecycle_oracle.compensation_adapter import (
    CodexCompensationOracleAdapter,
    create_oracle_compensation_adapter,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleAction,
    OracleBlockReason,
    OracleBlocked,
    OracleCommand,
    OracleMarketplaceRecord,
    OraclePluginRecord,
    OracleRunResult,
    OracleState,
)
from tests.staging.codex_lifecycle_oracle.identity_binding import (
    OracleIdentityBound,
    bind_oracle_identity,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.registration_adapter import (
    CodexRegistrationOracleAdapter,
    create_oracle_registration_adapter,
)
from tests.staging.environment_core.contracts import EnvironmentLease, revalidate_lease


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class ReceiptRemovalAcceptancePhase(str, Enum):
    VERSION = "VERSION"
    MARKETPLACE_ADD = "MARKETPLACE_ADD"
    PLUGIN_ADD = "PLUGIN_ADD"
    MARKETPLACE_LIST = "MARKETPLACE_LIST"
    PLUGIN_LIST = "PLUGIN_LIST"
    PLUGIN_REMOVE = "PLUGIN_REMOVE"
    MARKETPLACE_REMOVE = "MARKETPLACE_REMOVE"
    ABSENCE = "ABSENCE"


class ReceiptRemovalAcceptanceRejectReason(str, Enum):
    INVALID_LEASE = "INVALID_LEASE"
    INVALID_ORACLE = "INVALID_ORACLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_IDENTITY = "INVALID_IDENTITY"
    INVALID_REGISTRATION_ADAPTER = "INVALID_REGISTRATION_ADAPTER"
    INVALID_REGISTRATION_PORT = "INVALID_REGISTRATION_PORT"
    INVALID_FORWARD = "INVALID_FORWARD"
    INVALID_SETTLEMENT = "INVALID_SETTLEMENT"
    REGISTRATION_SEQUENCE = "REGISTRATION_SEQUENCE"
    REGISTRATION_CLAIM = "REGISTRATION_CLAIM"
    INVALID_RECEIPT = "INVALID_RECEIPT"
    INVALID_REMOVAL_REQUEST = "INVALID_REMOVAL_REQUEST"
    INVALID_COMPENSATION_ADAPTER = "INVALID_COMPENSATION_ADAPTER"
    REMOVAL_BLOCKED = "REMOVAL_BLOCKED"
    REPLAY_BLOCKED = "REPLAY_BLOCKED"
    FOREIGN_STATE_CHANGED = "FOREIGN_STATE_CHANGED"
    OWNED_STATE_REMAINS = "OWNED_STATE_REMAINS"
    ACTION_ORDER_INVALID = "ACTION_ORDER_INVALID"


class ReceiptRemovalAcceptanceAccepted(_StrictModel):
    status: Literal["RECEIPT_REMOVAL_ACCEPTED"] = "RECEIPT_REMOVAL_ACCEPTED"
    receipt: CodexRegistrationReceipt
    phases: tuple[ReceiptRemovalAcceptancePhase, ...]
    first_removal: Literal["REMOVED"] = "REMOVED"
    replay: Literal["NOT_INSTALLED"] = "NOT_INSTALLED"
    owned_state_absent: Literal[True] = True
    owned_payload_absent: Literal[True] = True
    foreign_preserved: Literal[True] = True
    replay_zero_removals: Literal[True] = True


class ReceiptRemovalAcceptanceRejected(_StrictModel):
    status: Literal["RECEIPT_REMOVAL_BLOCKED"] = "RECEIPT_REMOVAL_BLOCKED"
    reason: ReceiptRemovalAcceptanceRejectReason


ReceiptRemovalAcceptanceResult: TypeAlias = (
    ReceiptRemovalAcceptanceAccepted | ReceiptRemovalAcceptanceRejected
)


@dataclass(frozen=True)
class _ForeignSnapshot:
    marketplaces: tuple[OracleMarketplaceRecord, ...]
    plugins: tuple[OraclePluginRecord, ...]
    payloads: tuple[tuple[str, bytes], ...]


_EXPECTED_PHASES: tuple[ReceiptRemovalAcceptancePhase, ...] = (
    ReceiptRemovalAcceptancePhase.VERSION,
    ReceiptRemovalAcceptancePhase.MARKETPLACE_ADD,
    ReceiptRemovalAcceptancePhase.PLUGIN_ADD,
    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
    ReceiptRemovalAcceptancePhase.ABSENCE,
    ReceiptRemovalAcceptancePhase.PLUGIN_REMOVE,
    ReceiptRemovalAcceptancePhase.MARKETPLACE_REMOVE,
    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
    ReceiptRemovalAcceptancePhase.ABSENCE,
    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
    ReceiptRemovalAcceptancePhase.ABSENCE,
)


def run_receipt_removal_acceptance(
    lease: object,
    oracle: object,
    request: object,
) -> ReceiptRemovalAcceptanceResult:
    """Run one real registration receipt and its exact removal/replay composition."""

    if type(lease) is not EnvironmentLease:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_LEASE)
    rebuilt_lease = revalidate_lease(lease)
    if type(rebuilt_lease) is not EnvironmentLease:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_LEASE)
    if type(oracle) is not CodexLifecycleOracle:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_ORACLE)
    rebuilt_request = revalidate_registration_port_request(request)
    if type(rebuilt_request) is not CodexRegistrationPortRequest:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_REQUEST)
    if rebuilt_request.expected_plugin_id.value != rebuilt_request.preflight.plugin.value:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_IDENTITY)
    binding = bind_oracle_identity(rebuilt_request)
    if type(binding) is not OracleIdentityBound:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_IDENTITY)
    registration_adapter = create_oracle_registration_adapter(rebuilt_lease, oracle, binding)
    if type(registration_adapter) is not CodexRegistrationOracleAdapter:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_REGISTRATION_ADAPTER)
    registration_port = admit_codex_registration_port(registration_adapter)
    if type(registration_port) is not CodexRegistrationPortCapability:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_REGISTRATION_PORT)
    forward = admit_codex_registration_forward(registration_port)
    if type(forward) is not CodexRegistrationForwardCoordinator:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_FORWARD)
    settlement = admit_codex_registration_settlement_authority(forward)
    if type(settlement) is not CodexRegistrationSettlementAuthority:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_SETTLEMENT)
    foreign_before = _foreign_snapshot(rebuilt_lease, oracle)
    if foreign_before is None:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_RECEIPT)

    observed_actions: list[OracleAction] = []
    original_run = CodexLifecycleOracle.run

    def observed_run(
        current_oracle: CodexLifecycleOracle,
        current_lease: EnvironmentLease,
        command_value: OracleCommand,
    ) -> OracleRunResult:
        if type(command_value) is not OracleCommand:
            return OracleBlocked(reason=OracleBlockReason.COMMAND_INVALID)
        command = command_value
        observed_actions.append(command.action)
        return original_run(current_oracle, current_lease, command)

    with patch.object(CodexLifecycleOracle, "run", autospec=True, side_effect=observed_run):
        fresh = settlement.begin(rebuilt_request)
        if type(fresh) is not CodexRegistrationReadyLease:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REGISTRATION_SEQUENCE)
        marketplace = settlement.execute(fresh.lease)
        if type(marketplace) is not CodexRegistrationNextReadyPhase:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REGISTRATION_SEQUENCE)
        plugin = settlement.execute(marketplace.lease)
        if type(plugin) is not CodexRegistrationNextReadyPhase:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REGISTRATION_SEQUENCE)
        claim = settlement.execute(plugin.lease)
        if type(claim) is not CodexRegistrationProofClaim:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REGISTRATION_CLAIM)
        receipt_result = settle_codex_registration_proof(claim, registration_adapter)
        if type(receipt_result) is not CodexRegistrationReceipt:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_RECEIPT)
        receipt = receipt_result
        if not _receipt_matches_request(receipt, rebuilt_request):
            return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_RECEIPT)
        invocation = CodexReceiptRemovalInvocation(
            installation_id=receipt.installation_id,
            root=receipt.root,
            receipt=receipt,
        )
        removal_request = build_codex_receipt_removal_request(invocation)
        if type(removal_request) is not CodexReceiptRemovalReady:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_REMOVAL_REQUEST)
        compensation_adapter = create_oracle_compensation_adapter(
            rebuilt_lease,
            oracle,
            removal_request.request,
        )
        if type(compensation_adapter) is not CodexCompensationOracleAdapter:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.INVALID_COMPENSATION_ADAPTER)
        first_removal = compose_codex_receipt_removal(invocation, compensation_adapter)
        if type(first_removal) is not CodexReceiptRemovalRemoved:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REMOVAL_BLOCKED)
        state_before_replay = _state_bytes(rebuilt_lease, oracle)
        if state_before_replay is None:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.OWNED_STATE_REMAINS)
        if not _owned_state_and_payload_absent(rebuilt_lease, oracle, receipt):
            return _rejected(ReceiptRemovalAcceptanceRejectReason.OWNED_STATE_REMAINS)
        foreign_after_removal = _foreign_snapshot(rebuilt_lease, oracle)
        if foreign_after_removal != foreign_before:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.FOREIGN_STATE_CHANGED)
        replay_start = len(observed_actions)
        replay = compose_codex_receipt_removal(invocation, compensation_adapter)
        if type(replay) is not CodexReceiptRemovalNotInstalled:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REPLAY_BLOCKED)
        if len(observed_actions) == replay_start:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REPLAY_BLOCKED)
        if any(
            action in (OracleAction.PLUGIN_REMOVE, OracleAction.MARKETPLACE_REMOVE)
            for action in observed_actions[replay_start:]
        ):
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REPLAY_BLOCKED)
        if _state_bytes(rebuilt_lease, oracle) != state_before_replay:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.REPLAY_BLOCKED)
        if _foreign_snapshot(rebuilt_lease, oracle) != foreign_before:
            return _rejected(ReceiptRemovalAcceptanceRejectReason.FOREIGN_STATE_CHANGED)

    phases = tuple(_phase_for_action(action) for action in observed_actions)
    if phases != _EXPECTED_PHASES:
        return _rejected(ReceiptRemovalAcceptanceRejectReason.ACTION_ORDER_INVALID)
    return ReceiptRemovalAcceptanceAccepted(receipt=receipt, phases=phases)


def _receipt_matches_request(
    receipt: CodexRegistrationReceipt,
    request: CodexRegistrationPortRequest,
) -> bool:
    return (
        receipt.installation_id == request.preflight.installation_id
        and receipt.root == request.preflight.root
        and receipt.marketplace == request.preflight.marketplace
        and receipt.plugin_id == request.expected_plugin_id
        and receipt.plugin_name == request.preflight.plugin
        and receipt.version == request.expected_version
        and receipt.source_locator == request.source_locator
        and receipt.installed_locator == request.installed_locator
        and receipt.auth_policy == request.expected_auth_policy
        and receipt.digest == request.digest
    )


def _foreign_snapshot(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
) -> _ForeignSnapshot | None:
    try:
        state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
        payload_root = oracle.payload_root(lease)
        payloads: list[tuple[str, bytes]] = []
        for marketplace_record in state.foreign_marketplaces:
            payload = _read_payload(payload_root, marketplace_record.locator)
            if payload is None:
                return None
            payloads.append((marketplace_record.locator, payload))
        for plugin_record in state.foreign_plugins:
            payload = _read_payload(payload_root, plugin_record.locator)
            if payload is None:
                return None
            payloads.append((plugin_record.locator, payload))
        return _ForeignSnapshot(
            marketplaces=state.foreign_marketplaces,
            plugins=state.foreign_plugins,
            payloads=tuple(payloads),
        )
    except (OSError, TypeError, ValidationError, ValueError):
        return None


def _read_payload(payload_root: Path, locator: str) -> bytes | None:
    path = payload_root / locator
    try:
        if path.parent.parent != payload_root or not path.is_file() or path.resolve(strict=True) != path:
            return None
        return path.read_bytes()
    except OSError:
        return None


def _state_bytes(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> bytes | None:
    try:
        return oracle.state_path(lease).read_bytes()
    except OSError:
        return None


def _owned_state_and_payload_absent(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
    receipt: CodexRegistrationReceipt,
) -> bool:
    try:
        state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
        if state.marketplaces or state.plugins:
            return False
        payload_root = oracle.payload_root(lease)
        owned_locators = (
            receipt.source_locator.value + ".json",
            receipt.installed_locator.value + ".json",
        )
        return all(not (payload_root / locator).exists() for locator in owned_locators)
    except (OSError, TypeError, ValidationError, ValueError):
        return False


def _phase_for_action(action: OracleAction) -> ReceiptRemovalAcceptancePhase:
    if action is OracleAction.VERSION:
        return ReceiptRemovalAcceptancePhase.VERSION
    if action is OracleAction.MARKETPLACE_ADD:
        return ReceiptRemovalAcceptancePhase.MARKETPLACE_ADD
    if action is OracleAction.PLUGIN_ADD:
        return ReceiptRemovalAcceptancePhase.PLUGIN_ADD
    if action is OracleAction.MARKETPLACE_LIST:
        return ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST
    if action is OracleAction.PLUGIN_LIST:
        return ReceiptRemovalAcceptancePhase.PLUGIN_LIST
    if action is OracleAction.PLUGIN_REMOVE:
        return ReceiptRemovalAcceptancePhase.PLUGIN_REMOVE
    if action is OracleAction.MARKETPLACE_REMOVE:
        return ReceiptRemovalAcceptancePhase.MARKETPLACE_REMOVE
    if action is OracleAction.ABSENCE:
        return ReceiptRemovalAcceptancePhase.ABSENCE
    raise AssertionError("unknown oracle action")


def _rejected(reason: ReceiptRemovalAcceptanceRejectReason) -> ReceiptRemovalAcceptanceRejected:
    return ReceiptRemovalAcceptanceRejected(reason=reason)
