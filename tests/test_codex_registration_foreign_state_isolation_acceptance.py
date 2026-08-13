"""A1-A8 acceptance evidence for foreign registration-state isolation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from typing import TypeAlias
import unittest
from unittest.mock import patch

from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexPluginId,
    CodexRegistrationAttemptId,
)
from library.local_orchestration.codex_registration_port import CodexRegistrationPortRequest
from library.local_orchestration.contracts import (
    ArtifactDigest,
    InstallRoot,
    InstallationId,
    OwnedRelativePath,
)
from library.local_orchestration.host_contracts import (
    CodexCliVersion,
    CodexMarketplaceName,
    CodexPluginName,
    CodexPreflightRequest,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleCompleted,
    OracleForeignSeeded,
    OracleMarketplaceRecord,
    OraclePluginRecord,
    OracleState,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.registration_compensation_acceptance import (
    RegistrationCompensationAccepted,
    RegistrationCompensationPhase,
    run_registration_compensation_acceptance,
)
from tests.staging.codex_lifecycle_oracle.registration_success_acceptance import (
    RegistrationSuccessAccepted,
    RegistrationSuccessPhase,
    run_registration_success_acceptance,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownResult,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


OWNED_MARKETPLACE = "acceptance-market"
OWNED_PLUGIN = "acceptance-plugin"
FOREIGN_MARKETPLACE = f"{OWNED_MARKETPLACE}-foreign"
FOREIGN_PLUGIN = f"{OWNED_PLUGIN}-foreign"

MarketplaceTuple: TypeAlias = tuple[str, str, str, str]
PluginTuple: TypeAlias = tuple[str, str, str, str, str, str, str, str, str, str]

EXPECTED_SUCCESS_PHASES = (
    RegistrationSuccessPhase.VERSION,
    RegistrationSuccessPhase.MARKETPLACE_ADD,
    RegistrationSuccessPhase.PLUGIN_ADD,
    RegistrationSuccessPhase.MARKETPLACE_LIST,
    RegistrationSuccessPhase.PLUGIN_LIST,
)
EXPECTED_COMPENSATION_PHASES = (
    RegistrationCompensationPhase.VERSION,
    RegistrationCompensationPhase.MARKETPLACE_ADD,
    RegistrationCompensationPhase.PLUGIN_ADD,
    RegistrationCompensationPhase.PLUGIN_REMOVE,
    RegistrationCompensationPhase.MARKETPLACE_REMOVE,
    RegistrationCompensationPhase.PLUGIN_LIST,
    RegistrationCompensationPhase.MARKETPLACE_LIST,
    RegistrationCompensationPhase.ABSENCE,
)


@dataclass(frozen=True)
class _ForeignSnapshot:
    marketplaces: tuple[MarketplaceTuple, ...]
    plugins: tuple[PluginTuple, ...]
    marketplace_payload: bytes
    plugin_payload: bytes


def _request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=InstallationId(value="installation-000000000000e6a1"),
            root=InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
            marketplace=CodexMarketplaceName(value=OWNED_MARKETPLACE),
            plugin=CodexPluginName(value=OWNED_PLUGIN),
            marketplace_source=OwnedRelativePath(value=f"marketplaces/{OWNED_MARKETPLACE}"),
        ),
        attempt_id=CodexRegistrationAttemptId(value="attempt-000000000000e6a1"),
        expected_version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=OwnedRelativePath(value=f"marketplaces/{OWNED_MARKETPLACE}"),
        installed_locator=OwnedRelativePath(value=f"plugins/{OWNED_PLUGIN}"),
        digest=ArtifactDigest(value="a" * 64),
        expected_auth_policy=CodexAuthPolicy(value="trusted-local"),
        expected_plugin_id=CodexPluginId(value=OWNED_PLUGIN),
    )


def _foreign_marketplace() -> OracleMarketplaceRecord:
    root = "foreign-acceptance-market-root"
    payload = f"marketplace|{FOREIGN_MARKETPLACE}|{root}".encode("utf-8")
    return OracleMarketplaceRecord(
        name=FOREIGN_MARKETPLACE,
        root=root,
        locator=f"marketplaces/{FOREIGN_MARKETPLACE}.json",
        digest=hashlib.sha256(payload).hexdigest(),
    )


def _foreign_plugin() -> OraclePluginRecord:
    installed_path = rf"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\{FOREIGN_PLUGIN}"
    payload = (
        f"plugin|{FOREIGN_PLUGIN}|foreign-acceptance-plugin|{FOREIGN_MARKETPLACE}|foreign-v1|"
        f"foreign-acceptance-source|foreign-acceptance-policy|foreign-acceptance-auth|{installed_path}"
    ).encode("utf-8")
    return OraclePluginRecord(
        plugin_id=FOREIGN_PLUGIN,
        name="foreign-acceptance-plugin",
        marketplace_name=FOREIGN_MARKETPLACE,
        version="foreign-v1",
        source="foreign-acceptance-source",
        install_policy="foreign-acceptance-policy",
        auth_policy="foreign-acceptance-auth",
        installed_path=installed_path,
        locator=f"plugins/{FOREIGN_PLUGIN}.json",
        digest=hashlib.sha256(payload).hexdigest(),
    )


def _ready_oracle(
    allocator: DisposableEnvironmentAllocator,
    owner_suffix: str,
) -> tuple[EnvironmentLease, CodexLifecycleOracle]:
    provisioned = allocator.provision(EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}"))
    if type(provisioned) is not ProvisionedEnvironment:
        raise AssertionError("the exact project-owned lease was not provisioned")
    oracle = CodexLifecycleOracle(
        CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
    )
    if type(oracle.initialize(provisioned.environment)) is not OracleCompleted:
        raise AssertionError("oracle initialization failed")
    return provisioned.environment, oracle


def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
    root = lease.root.path
    result = allocator.teardown(lease)
    if type(result) is not TeardownResult:
        raise AssertionError("unexpected teardown result")
    if result.status is not TeardownStatus.REMOVED or root.exists():
        raise AssertionError("the exact caller-owned lease was not removed")


def _seed_foreign_state(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> None:
    marketplace_result = oracle.seed_foreign_marketplace(lease, _foreign_marketplace())
    plugin_result = oracle.seed_foreign_plugin(lease, _foreign_plugin())
    if type(marketplace_result) is not OracleForeignSeeded:
        raise AssertionError("foreign marketplace seed was not admitted")
    if type(plugin_result) is not OracleForeignSeeded:
        raise AssertionError("foreign plugin seed was not admitted")


def _marketplace_tuple(record: OracleMarketplaceRecord) -> MarketplaceTuple:
    return record.name, record.root, record.locator, record.digest


def _plugin_tuple(record: OraclePluginRecord) -> PluginTuple:
    return (
        record.plugin_id,
        record.name,
        record.marketplace_name,
        record.version,
        record.source,
        record.install_policy,
        record.auth_policy,
        record.installed_path,
        record.locator,
        record.digest,
    )


def _foreign_snapshot(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> _ForeignSnapshot:
    state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
    if len(state.foreign_marketplaces) != 1 or len(state.foreign_plugins) != 1:
        raise AssertionError("foreign seed cardinality is not exact")
    marketplace = state.foreign_marketplaces[0]
    plugin = state.foreign_plugins[0]
    marketplace_path = oracle.payload_root(lease) / marketplace.locator
    plugin_path = oracle.payload_root(lease) / plugin.locator
    if not marketplace_path.is_file() or not plugin_path.is_file():
        raise AssertionError("foreign seed payload is absent")
    return _ForeignSnapshot(
        marketplaces=tuple(_marketplace_tuple(record) for record in state.foreign_marketplaces),
        plugins=tuple(_plugin_tuple(record) for record in state.foreign_plugins),
        marketplace_payload=marketplace_path.read_bytes(),
        plugin_payload=plugin_path.read_bytes(),
    )


def _assert_foreign_unchanged(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
    expected: _ForeignSnapshot,
) -> None:
    actual = _foreign_snapshot(lease, oracle)
    if actual != expected:
        raise AssertionError("foreign records or payload bytes changed")


def _assert_owned_success(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> None:
    state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
    if len(state.marketplaces) != 1 or len(state.plugins) != 1:
        raise AssertionError("owned success state is not exact")
    marketplace = state.marketplaces[0]
    plugin = state.plugins[0]
    if marketplace.name != OWNED_MARKETPLACE or plugin.plugin_id != OWNED_PLUGIN:
        raise AssertionError("owned success identity is not exact")
    payload_root = oracle.payload_root(lease)
    if not (payload_root / marketplace.locator).is_file() or not (payload_root / plugin.locator).is_file():
        raise AssertionError("owned success payload is absent")


def _assert_owned_compensation_absent(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> None:
    state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
    if state.marketplaces or state.plugins:
        raise AssertionError("owned compensation state remains")
    payload_root = oracle.payload_root(lease)
    if (payload_root / f"marketplaces/{OWNED_MARKETPLACE}.json").exists():
        raise AssertionError("owned marketplace payload remains")
    if (payload_root / f"plugins/{OWNED_PLUGIN}.json").exists():
        raise AssertionError("owned plugin payload remains")


class CodexRegistrationForeignStateIsolationAcceptanceTests(unittest.TestCase):
    def test_a1_to_a8_success_and_compensation_preserve_prefix_similar_foreign_state(self) -> None:
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        success_lease, success_oracle = _ready_oracle(allocator, "000000000000e6a1")
        compensation_lease, compensation_oracle = _ready_oracle(allocator, "000000000000e6a2")
        try:
            with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                _seed_foreign_state(success_lease, success_oracle)
                success_foreign = _foreign_snapshot(success_lease, success_oracle)
                success_result = run_registration_success_acceptance(success_lease, success_oracle, _request())
                if type(success_result) is not RegistrationSuccessAccepted:
                    raise AssertionError("integrated success entrypoint did not accept")
                if success_result.metadata.phases != EXPECTED_SUCCESS_PHASES:
                    raise AssertionError("integrated success phases are not exact")
                _assert_owned_success(success_lease, success_oracle)
                _assert_foreign_unchanged(success_lease, success_oracle, success_foreign)

                _seed_foreign_state(compensation_lease, compensation_oracle)
                compensation_foreign = _foreign_snapshot(compensation_lease, compensation_oracle)
                compensation_result = run_registration_compensation_acceptance(
                    compensation_lease,
                    compensation_oracle,
                    _request(),
                )
                if type(compensation_result) is not RegistrationCompensationAccepted:
                    raise AssertionError("integrated compensation entrypoint did not accept")
                if compensation_result.phases != EXPECTED_COMPENSATION_PHASES:
                    raise AssertionError("integrated compensation phases are not exact")
                if not (
                    compensation_result.original_plugin_add_executed
                    and compensation_result.owned_state_observed
                    and compensation_result.owned_payload_observed
                    and compensation_result.logical_installed_path_absent
                    and compensation_result.physical_plugin_payload_absent
                    and compensation_result.replay_blocked
                ):
                    raise AssertionError("integrated compensation evidence is incomplete")
                _assert_owned_compensation_absent(compensation_lease, compensation_oracle)
                _assert_foreign_unchanged(compensation_lease, compensation_oracle, compensation_foreign)
        finally:
            _teardown(allocator, compensation_lease)
            _teardown(allocator, success_lease)


if __name__ == "__main__":
    unittest.main()
