"""Staging-only success acceptance over the integrated registration composition."""

from __future__ import annotations

from enum import Enum
import hashlib
from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError

from library.local_orchestration.codex_registration_contracts import (
    CodexRegistrationReceipt,
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
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleIdentity,
    OracleState,
    validated_payload_root,
    validated_state_path,
)
from tests.staging.codex_lifecycle_oracle.identity_binding import (
    OracleIdentityBound,
    bind_oracle_identity,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.environment_core.contracts import EnvironmentLease, revalidate_lease
from tests.staging.codex_lifecycle_oracle.registration_adapter import (
    CodexRegistrationOracleAdapter,
    create_oracle_registration_adapter,
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class RegistrationSuccessPhase(str, Enum):
    VERSION = "VERSION"
    MARKETPLACE_ADD = "MARKETPLACE_ADD"
    PLUGIN_ADD = "PLUGIN_ADD"
    MARKETPLACE_LIST = "MARKETPLACE_LIST"
    PLUGIN_LIST = "PLUGIN_LIST"


class RegistrationSuccessRejectReason(str, Enum):
    INVALID_LEASE = "INVALID_LEASE"
    INVALID_ORACLE = "INVALID_ORACLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_IDENTITY = "INVALID_IDENTITY"
    INVALID_ADAPTER = "INVALID_ADAPTER"
    INVALID_PORT = "INVALID_PORT"
    INVALID_FORWARD = "INVALID_FORWARD"
    INVALID_SETTLEMENT = "INVALID_SETTLEMENT"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    CLAIM_BLOCKED = "CLAIM_BLOCKED"
    INVALID_RECEIPT = "INVALID_RECEIPT"
    INVALID_STATE = "INVALID_STATE"
    INVALID_PHYSICAL_PAYLOAD = "INVALID_PHYSICAL_PAYLOAD"


class RegistrationSuccessMetadata(_StrictModel):
    status: Literal["REGISTRATION_SUCCESS_METADATA"] = "REGISTRATION_SUCCESS_METADATA"
    phases: tuple[RegistrationSuccessPhase, ...]
    owned_marketplace_verified: Literal[True] = True
    owned_plugin_verified: Literal[True] = True
    proof_claim_settled: Literal[True] = True


class RegistrationSuccessAccepted(_StrictModel):
    status: Literal["REGISTRATION_SUCCESS_ACCEPTED"] = "REGISTRATION_SUCCESS_ACCEPTED"
    receipt: CodexRegistrationReceipt
    metadata: RegistrationSuccessMetadata


class RegistrationSuccessRejected(_StrictModel):
    status: Literal["REGISTRATION_SUCCESS_BLOCKED"] = "REGISTRATION_SUCCESS_BLOCKED"
    reason: RegistrationSuccessRejectReason


RegistrationSuccessAcceptanceResult: TypeAlias = RegistrationSuccessAccepted | RegistrationSuccessRejected


_EXPECTED_PHASES: tuple[RegistrationSuccessPhase, ...] = (
    RegistrationSuccessPhase.VERSION,
    RegistrationSuccessPhase.MARKETPLACE_ADD,
    RegistrationSuccessPhase.PLUGIN_ADD,
    RegistrationSuccessPhase.MARKETPLACE_LIST,
    RegistrationSuccessPhase.PLUGIN_LIST,
)


def run_registration_success_acceptance(
    lease: object,
    oracle: object,
    request: object,
) -> RegistrationSuccessAcceptanceResult:
    """Run one exact fresh success path and return no live authority."""

    if type(lease) is not EnvironmentLease:
        return _rejected(RegistrationSuccessRejectReason.INVALID_LEASE)
    validated_lease = revalidate_lease(lease)
    if type(validated_lease) is not EnvironmentLease:
        return _rejected(RegistrationSuccessRejectReason.INVALID_LEASE)
    if type(oracle) is not CodexLifecycleOracle:
        return _rejected(RegistrationSuccessRejectReason.INVALID_ORACLE)
    rebuilt_request = revalidate_registration_port_request(request)
    if type(rebuilt_request) is not CodexRegistrationPortRequest:
        return _rejected(RegistrationSuccessRejectReason.INVALID_REQUEST)
    binding = bind_oracle_identity(rebuilt_request)
    if type(binding) is not OracleIdentityBound:
        return _rejected(RegistrationSuccessRejectReason.INVALID_IDENTITY)
    adapter = _admit_adapter(validated_lease, oracle, binding)
    if adapter is None:
        return _rejected(RegistrationSuccessRejectReason.INVALID_ADAPTER)
    port = admit_codex_registration_port(adapter)
    if type(port) is not CodexRegistrationPortCapability:
        return _rejected(RegistrationSuccessRejectReason.INVALID_PORT)
    forward = admit_codex_registration_forward(port)
    if type(forward) is not CodexRegistrationForwardCoordinator:
        return _rejected(RegistrationSuccessRejectReason.INVALID_FORWARD)
    settlement = admit_codex_registration_settlement_authority(forward)
    if type(settlement) is not CodexRegistrationSettlementAuthority:
        return _rejected(RegistrationSuccessRejectReason.INVALID_SETTLEMENT)

    fresh = settlement.begin(rebuilt_request)
    if type(fresh) is not CodexRegistrationReadyLease:
        return _rejected(RegistrationSuccessRejectReason.INVALID_SEQUENCE)
    marketplace = settlement.execute(fresh.lease)
    if type(marketplace) is not CodexRegistrationNextReadyPhase:
        return _rejected(RegistrationSuccessRejectReason.INVALID_SEQUENCE)
    plugin = settlement.execute(marketplace.lease)
    if type(plugin) is not CodexRegistrationNextReadyPhase:
        return _rejected(RegistrationSuccessRejectReason.INVALID_SEQUENCE)
    claim = settlement.execute(plugin.lease)
    if type(claim) is not CodexRegistrationProofClaim:
        return _rejected(RegistrationSuccessRejectReason.CLAIM_BLOCKED)

    settled = settle_codex_registration_proof(claim, adapter)
    if type(settled) is not CodexRegistrationReceipt:
        return _rejected(RegistrationSuccessRejectReason.CLAIM_BLOCKED)
    physical_reason = _verify_owned_state_and_payload(validated_lease, binding.identity, rebuilt_request)
    if physical_reason is not None:
        return _rejected(physical_reason)
    if not _receipt_matches_request(settled, rebuilt_request):
        return _rejected(RegistrationSuccessRejectReason.INVALID_RECEIPT)
    return RegistrationSuccessAccepted(
        receipt=settled,
        metadata=RegistrationSuccessMetadata(phases=_EXPECTED_PHASES),
    )


def _admit_adapter(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
    binding: OracleIdentityBound,
) -> CodexRegistrationOracleAdapter | None:

    admitted = create_oracle_registration_adapter(lease, oracle, binding)
    if type(admitted) is not CodexRegistrationOracleAdapter:
        return None
    return admitted


def _verify_owned_state_and_payload(
    lease: EnvironmentLease,
    identity: OracleIdentity,
    request: CodexRegistrationPortRequest,
) -> RegistrationSuccessRejectReason | None:
    try:
        state_path = validated_state_path(lease)
        payload_root = validated_payload_root(lease)
        state = OracleState.model_validate_json(state_path.read_bytes())
    except (OSError, TypeError, ValidationError, ValueError):
        return RegistrationSuccessRejectReason.INVALID_STATE
    if len(state.marketplaces) != 1 or len(state.plugins) != 1:
        return RegistrationSuccessRejectReason.INVALID_STATE
    marketplace = state.marketplaces[0]
    plugin = state.plugins[0]
    if (
        marketplace.name != identity.marketplace_name
        or marketplace.root != identity.marketplace_root
        or plugin.plugin_id != identity.plugin_id
        or plugin.name != identity.plugin_name
        or plugin.marketplace_name != identity.marketplace_name
        or plugin.version != identity.plugin_version
        or plugin.source != identity.plugin_source
        or plugin.install_policy != identity.plugin_install_policy
        or plugin.auth_policy != identity.plugin_auth_policy
        or plugin.installed_path != identity.plugin_installed_path
        or request.expected_version.value != plugin.version
    ):
        return RegistrationSuccessRejectReason.INVALID_STATE
    marketplace_path = payload_root / "marketplaces" / f"{identity.marketplace_name}.json"
    plugin_path = payload_root / "plugins" / f"{identity.plugin_id}.json"
    expected_marketplace = f"marketplace|{marketplace.name}|{marketplace.root}".encode("utf-8")
    expected_plugin = (
        f"plugin|{plugin.plugin_id}|{plugin.name}|{plugin.marketplace_name}|{plugin.version}|"
        f"{plugin.source}|{plugin.install_policy}|{plugin.auth_policy}|{plugin.installed_path}"
    ).encode("utf-8")
    try:
        marketplace_bytes = marketplace_path.read_bytes()
        plugin_bytes = plugin_path.read_bytes()
    except OSError:
        return RegistrationSuccessRejectReason.INVALID_PHYSICAL_PAYLOAD
    if (
        marketplace_bytes != expected_marketplace
        or plugin_bytes != expected_plugin
        or hashlib.sha256(marketplace_bytes).hexdigest() != marketplace.digest
        or hashlib.sha256(plugin_bytes).hexdigest() != plugin.digest
    ):
        return RegistrationSuccessRejectReason.INVALID_PHYSICAL_PAYLOAD
    return None


def _receipt_matches_request(receipt: CodexRegistrationReceipt, request: CodexRegistrationPortRequest) -> bool:
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


def _rejected(reason: RegistrationSuccessRejectReason) -> RegistrationSuccessRejected:
    return RegistrationSuccessRejected(reason=reason)
