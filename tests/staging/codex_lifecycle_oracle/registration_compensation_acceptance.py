"""One reusable staging-only E5 registration-compensation transaction."""

from __future__ import annotations

from enum import Enum
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict

from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortManifest,
    CodexCompensationPortRequest,
)
from library.local_orchestration.codex_compensation_reducer import CodexCompensated
from library.local_orchestration.codex_registration_compensation_settlement import (
    settle_codex_registration_compensation,
)
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
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationCompensationClaim,
    CodexRegistrationSettlementAuthority,
    CodexRegistrationSettlementAuthorityBlocked,
    CodexRegistrationSettlementClaimBlocked,
    admit_codex_registration_settlement_authority,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationNextReadyPhase,
    CodexRegistrationReadyLease,
)
from tests.staging.codex_lifecycle_oracle.compensation_adapter import (
    CodexCompensationOracleAdapter,
    CodexCompensationOracleAdapterRejected,
    create_oracle_compensation_adapter,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleAction,
    OracleBlockReason,
    OracleBlocked,
    OracleCommand,
    OracleCompleted,
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
from unittest.mock import patch


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class RegistrationCompensationPhase(str, Enum):
    VERSION = "VERSION"
    MARKETPLACE_ADD = "MARKETPLACE_ADD"
    PLUGIN_ADD = "PLUGIN_ADD"
    PLUGIN_REMOVE = "PLUGIN_REMOVE"
    MARKETPLACE_REMOVE = "MARKETPLACE_REMOVE"
    PLUGIN_LIST = "PLUGIN_LIST"
    MARKETPLACE_LIST = "MARKETPLACE_LIST"
    ABSENCE = "ABSENCE"


class RegistrationCompensationRejectReason(str, Enum):
    INVALID_LEASE = "INVALID_LEASE"
    INVALID_ORACLE = "INVALID_ORACLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_IDENTITY = "INVALID_IDENTITY"
    INVALID_ADAPTER = "INVALID_ADAPTER"
    AUTHORITY_BLOCKED = "AUTHORITY_BLOCKED"
    TRANSACTION_BLOCKED = "TRANSACTION_BLOCKED"
    COMPENSATION_BLOCKED = "COMPENSATION_BLOCKED"
    ACTION_ORDER_INVALID = "ACTION_ORDER_INVALID"
    EVIDENCE_INVALID = "EVIDENCE_INVALID"


class RegistrationCompensationAccepted(_StrictModel):
    status: Literal["COMPENSATION_ACCEPTED"] = "COMPENSATION_ACCEPTED"
    phases: tuple[RegistrationCompensationPhase, ...]
    original_plugin_add_executed: bool
    owned_state_observed: bool
    owned_payload_observed: bool
    logical_installed_path_absent: bool
    physical_plugin_payload_absent: bool
    replay_blocked: bool


class RegistrationCompensationRejected(_StrictModel):
    status: Literal["COMPENSATION_REJECTED"] = "COMPENSATION_REJECTED"
    reason: RegistrationCompensationRejectReason


RegistrationCompensationResult: TypeAlias = (
    RegistrationCompensationAccepted | RegistrationCompensationRejected
)


_EXPECTED_PHASES: tuple[RegistrationCompensationPhase, ...] = (
    RegistrationCompensationPhase.VERSION,
    RegistrationCompensationPhase.MARKETPLACE_ADD,
    RegistrationCompensationPhase.PLUGIN_ADD,
    RegistrationCompensationPhase.PLUGIN_REMOVE,
    RegistrationCompensationPhase.MARKETPLACE_REMOVE,
    RegistrationCompensationPhase.PLUGIN_LIST,
    RegistrationCompensationPhase.MARKETPLACE_LIST,
    RegistrationCompensationPhase.ABSENCE,
)


def run_registration_compensation_acceptance(
    lease: object,
    oracle: object,
    request: object,
) -> RegistrationCompensationResult:
    """Run one exact accepted E5 transaction without owning its lifecycle."""

    if type(lease) is not EnvironmentLease:
        return _rejected(RegistrationCompensationRejectReason.INVALID_LEASE)
    rebuilt_lease = revalidate_lease(lease)
    if type(rebuilt_lease) is not EnvironmentLease:
        return _rejected(RegistrationCompensationRejectReason.INVALID_LEASE)
    if type(oracle) is not CodexLifecycleOracle:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ORACLE)
    rebuilt_request = revalidate_registration_port_request(request)
    if type(rebuilt_request) is not CodexRegistrationPortRequest:
        return _rejected(RegistrationCompensationRejectReason.INVALID_REQUEST)
    if rebuilt_request.expected_plugin_id.value != rebuilt_request.preflight.plugin.value:
        return _rejected(RegistrationCompensationRejectReason.INVALID_IDENTITY)
    bound = bind_oracle_identity(rebuilt_request)
    if type(bound) is not OracleIdentityBound:
        return _rejected(RegistrationCompensationRejectReason.INVALID_IDENTITY)

    registration_adapter = create_oracle_registration_adapter(rebuilt_lease, oracle, bound)
    if type(registration_adapter) is not CodexRegistrationOracleAdapter:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)
    registration_port = admit_codex_registration_port(registration_adapter)
    if type(registration_port) is not CodexRegistrationPortCapability:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)
    forward = admit_codex_registration_forward(registration_port)
    if type(forward) is not CodexRegistrationForwardCoordinator:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)
    authority = admit_codex_registration_settlement_authority(forward)
    if type(authority) is CodexRegistrationSettlementAuthorityBlocked:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)
    if type(authority) is not CodexRegistrationSettlementAuthority:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)

    compensation_request = _compensation_request(rebuilt_request)
    compensation_adapter = create_oracle_compensation_adapter(
        rebuilt_lease,
        oracle,
        compensation_request,
    )
    if type(compensation_adapter) is CodexCompensationOracleAdapterRejected:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)
    if type(compensation_adapter) is not CodexCompensationOracleAdapter:
        return _rejected(RegistrationCompensationRejectReason.INVALID_ADAPTER)

    observed_actions: list[OracleAction] = []
    original_plugin_result: list[OracleCompleted] = []
    one_shot_calls = 0
    owned_state_observed = False
    owned_payload_observed = False
    replay_guard = False
    replay_calls = 0
    original_run = CodexLifecycleOracle.run

    def observed_run(
        current_oracle: CodexLifecycleOracle,
        current_lease: EnvironmentLease,
        command_value: object,
    ) -> OracleRunResult:
        nonlocal one_shot_calls, owned_state_observed, owned_payload_observed, replay_calls
        if type(command_value) is not OracleCommand:
            return OracleBlocked(reason=OracleBlockReason.COMMAND_INVALID)
        command = command_value
        if replay_guard:
            replay_calls += 1
            return OracleBlocked(reason=OracleBlockReason.PROCESS_FAILED)
        observed_actions.append(command.action)
        result = original_run(current_oracle, current_lease, command)
        if command.action is OracleAction.PLUGIN_ADD and one_shot_calls == 0:
            one_shot_calls += 1
            if type(result) is OracleCompleted:
                original_plugin_result.append(result)
                state = OracleState.model_validate_json(
                    current_oracle.state_path(current_lease).read_bytes()
                )
                plugin_path = current_oracle.payload_root(current_lease) / "plugins" / "acceptance-plugin.json"
                owned_state_observed = len(state.marketplaces) == 1 and len(state.plugins) == 1
                owned_payload_observed = plugin_path.is_file() and plugin_path.resolve(strict=True) == plugin_path
            return OracleBlocked(reason=OracleBlockReason.PROCESS_FAILED)
        return result

    with patch.object(CodexLifecycleOracle, "run", autospec=True, side_effect=observed_run):
        fresh = authority.begin(rebuilt_request)
        if type(fresh) is not CodexRegistrationReadyLease:
            return _rejected(RegistrationCompensationRejectReason.AUTHORITY_BLOCKED)
        marketplace = authority.execute(fresh.lease)
        if type(marketplace) is not CodexRegistrationNextReadyPhase:
            return _rejected(RegistrationCompensationRejectReason.TRANSACTION_BLOCKED)
        plugin = authority.execute(marketplace.lease)
        if type(plugin) is not CodexRegistrationNextReadyPhase:
            return _rejected(RegistrationCompensationRejectReason.TRANSACTION_BLOCKED)
        claim = authority.execute(plugin.lease)
        if type(claim) is not CodexRegistrationCompensationClaim:
            return _rejected(RegistrationCompensationRejectReason.TRANSACTION_BLOCKED)
        settled = settle_codex_registration_compensation(claim, compensation_adapter)
        if type(settled) is not CodexCompensated:
            return _rejected(RegistrationCompensationRejectReason.COMPENSATION_BLOCKED)
        if settled.reasons or settled.remaining_authority:
            return _rejected(RegistrationCompensationRejectReason.EVIDENCE_INVALID)

        state_path = oracle.state_path(rebuilt_lease)
        plugin_path = oracle.payload_root(rebuilt_lease) / "plugins" / "acceptance-plugin.json"
        state_before_replay = state_path.read_bytes()
        state = OracleState.model_validate_json(state_before_replay)
        logical_absent = not state.marketplaces and not state.plugins
        physical_absent = not plugin_path.exists()
        if not logical_absent or not physical_absent:
            return _rejected(RegistrationCompensationRejectReason.EVIDENCE_INVALID)
        replay_guard = True
        replay = settle_codex_registration_compensation(claim, compensation_adapter)
        replay_blocked = type(replay) is CodexRegistrationSettlementClaimBlocked
        if not replay_blocked or replay_calls != 0:
            return _rejected(RegistrationCompensationRejectReason.EVIDENCE_INVALID)
        if state_path.read_bytes() != state_before_replay or plugin_path.exists():
            return _rejected(RegistrationCompensationRejectReason.EVIDENCE_INVALID)

    phases = tuple(RegistrationCompensationPhase(action.value) for action in observed_actions)
    if phases != _EXPECTED_PHASES:
        return _rejected(RegistrationCompensationRejectReason.ACTION_ORDER_INVALID)
    if one_shot_calls != 1 or len(original_plugin_result) != 1:
        return _rejected(RegistrationCompensationRejectReason.EVIDENCE_INVALID)
    if not owned_state_observed or not owned_payload_observed:
        return _rejected(RegistrationCompensationRejectReason.EVIDENCE_INVALID)
    return RegistrationCompensationAccepted(
        phases=phases,
        original_plugin_add_executed=True,
        owned_state_observed=owned_state_observed,
        owned_payload_observed=owned_payload_observed,
        logical_installed_path_absent=logical_absent,
        physical_plugin_payload_absent=physical_absent,
        replay_blocked=replay_blocked,
    )


def _compensation_request(request: CodexRegistrationPortRequest) -> CodexCompensationPortRequest:
    return CodexCompensationPortRequest(
        manifest=CodexCompensationPortManifest(
            installation_id=request.preflight.installation_id,
            root=request.preflight.root,
            marketplace=request.preflight.marketplace,
            marketplace_source=request.preflight.marketplace_source,
            plugin_id=request.expected_plugin_id,
            plugin=request.preflight.plugin,
            version=request.expected_version,
            installed_locator=request.installed_locator,
            auth_policy=request.expected_auth_policy,
            digest=request.digest,
        )
    )


def _rejected(reason: RegistrationCompensationRejectReason) -> RegistrationCompensationRejected:
    return RegistrationCompensationRejected(reason=reason)
