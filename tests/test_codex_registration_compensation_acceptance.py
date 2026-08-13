"""C1-C8 evidence for one integrated Codex registration rollback lane."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortManifest,
    CodexCompensationPortRequest,
)
from library.local_orchestration.codex_compensation_reducer import CodexCompensated
from library.local_orchestration.codex_registration_compensation_settlement import (
    settle_codex_registration_compensation,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexPluginId,
    CodexRegistrationAttemptId,
)
from library.local_orchestration.codex_registration_forward import (
    CodexRegistrationForwardCoordinator,
    admit_codex_registration_forward,
)
from library.local_orchestration.codex_registration_port import (
    CodexRegistrationPortCapability,
    CodexRegistrationPortRequest,
    admit_codex_registration_port,
)
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationCompensationClaim,
    CodexRegistrationSettlementAuthority,
    CodexRegistrationSettlementClaimBlocked,
    admit_codex_registration_settlement_authority,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationNextReadyPhase,
    CodexRegistrationReadyLease,
)
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
from tests.staging.codex_lifecycle_oracle.compensation_adapter import (
    CodexCompensationOracleAdapter,
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
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.registration_adapter import (
    CodexRegistrationOracleAdapter,
    create_oracle_registration_adapter,
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


CHILD_ARGUMENT = "--compensation-acceptance-child"
CHILD_TEMP_PREFIX = "e5-compensation-owned-"


def _request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=InstallationId(value="installation-000000000000e5b2"),
            root=InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
            marketplace=CodexMarketplaceName(value="acceptance-market"),
            plugin=CodexPluginName(value="acceptance-plugin"),
            marketplace_source=OwnedRelativePath(value="marketplaces/acceptance-market"),
        ),
        attempt_id=CodexRegistrationAttemptId(value="attempt-000000000000e5b2"),
        expected_version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=OwnedRelativePath(value="marketplaces/acceptance-market"),
        installed_locator=OwnedRelativePath(value="plugins/acceptance-plugin"),
        digest=ArtifactDigest(value="e" * 64),
        expected_auth_policy=CodexAuthPolicy(value="trusted-local"),
        expected_plugin_id=CodexPluginId(value="acceptance-plugin"),
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


def _ready_environment(
    owner_suffix: str,
) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease, CodexLifecycleOracle]:
    allocator = DisposableEnvironmentAllocator.from_project_runtime()
    provisioned = allocator.provision(EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}"))
    if type(provisioned) is not ProvisionedEnvironment:
        raise AssertionError("the exact project-owned lease was not provisioned")
    oracle = CodexLifecycleOracle(
        CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
    )
    return allocator, provisioned.environment, oracle


def _initialize(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> None:
    if type(oracle.initialize(lease)) is not OracleCompleted:
        raise AssertionError("oracle initialization failed")


def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
    lease_root = lease.root.path
    result = allocator.teardown(lease)
    if type(result) is not TeardownResult:
        raise AssertionError("unexpected teardown result")
    if result.status is not TeardownStatus.REMOVED or lease_root.exists():
        raise AssertionError("the exact lease was not removed")


def _admit_registration_authority(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
    request: CodexRegistrationPortRequest,
) -> tuple[CodexRegistrationOracleAdapter, CodexRegistrationSettlementAuthority, OracleIdentityBound]:
    bound = bind_oracle_identity(request)
    if type(bound) is not OracleIdentityBound:
        raise AssertionError("the frozen request did not bind to the oracle identity")
    adapter = create_oracle_registration_adapter(lease, oracle, bound)
    if type(adapter) is not CodexRegistrationOracleAdapter:
        raise AssertionError("the integrated E2 adapter was not admitted")
    port = admit_codex_registration_port(adapter)
    if type(port) is not CodexRegistrationPortCapability:
        raise AssertionError("the integrated E2 port was not admitted")
    forward = admit_codex_registration_forward(port)
    if type(forward) is not CodexRegistrationForwardCoordinator:
        raise AssertionError("the integrated forward coordinator was not admitted")
    authority = admit_codex_registration_settlement_authority(forward)
    if type(authority) is not CodexRegistrationSettlementAuthority:
        raise AssertionError("the integrated settlement authority was not admitted")
    return adapter, authority, bound


def _child_compensation() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e5b2")
    try:
        request = _request()
        _initialize(lease, oracle)
        _, authority, bound = _admit_registration_authority(lease, oracle, request)
        compensation = create_oracle_compensation_adapter(
            lease,
            oracle,
            _compensation_request(request),
        )
        if type(compensation) is not CodexCompensationOracleAdapter:
            return 2
        fresh = authority.begin(request)
        if type(fresh) is not CodexRegistrationReadyLease:
            return 3

        observed_actions: list[OracleAction] = []
        original_plugin_result: list[OracleCompleted] = []
        one_shot_calls = 0
        owned_state_seen = False
        owned_payload_seen = False
        replay_guard = False
        replay_calls = 0
        original_run = CodexLifecycleOracle.run

        def observed_run(
            current_oracle: CodexLifecycleOracle,
            current_lease: EnvironmentLease,
            command_value: object,
        ) -> OracleRunResult:
            nonlocal one_shot_calls, owned_state_seen, owned_payload_seen, replay_calls
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
                    owned_state_seen = len(state.marketplaces) == 1 and len(state.plugins) == 1
                    owned_payload_seen = plugin_path.is_file() and plugin_path.resolve(strict=True) == plugin_path
                return OracleBlocked(reason=OracleBlockReason.PROCESS_FAILED)
            return result

        with patch.object(CodexLifecycleOracle, "run", autospec=True, side_effect=observed_run):
            marketplace = authority.execute(fresh.lease)
            if type(marketplace) is not CodexRegistrationNextReadyPhase:
                return 4
            plugin = authority.execute(marketplace.lease)
            if type(plugin) is not CodexRegistrationNextReadyPhase:
                return 5
            claim = authority.execute(plugin.lease)
            if type(claim) is not CodexRegistrationCompensationClaim:
                return 6
            settled = settle_codex_registration_compensation(claim, compensation)
            if type(settled) is not CodexCompensated:
                return 7
            if settled.reasons or settled.remaining_authority:
                return 8

            state_path = oracle.state_path(lease)
            plugin_path = oracle.payload_root(lease) / "plugins" / "acceptance-plugin.json"
            state_after_settlement = state_path.read_bytes()
            state = OracleState.model_validate_json(state_after_settlement)
            if state.marketplaces or state.plugins or plugin_path.exists():
                return 9
            if bound.identity.plugin_installed_path != (
                r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\acceptance-plugin"
            ):
                return 10

            replay_state = state_path.read_bytes()
            replay_guard = True
            replay = settle_codex_registration_compensation(claim, compensation)
            if type(replay) is not CodexRegistrationSettlementClaimBlocked:
                return 11
            if replay_calls != 0 or state_path.read_bytes() != replay_state or plugin_path.exists():
                return 12

        if one_shot_calls != 1 or len(original_plugin_result) != 1:
            return 13
        if not owned_state_seen or not owned_payload_seen:
            return 14
        if observed_actions != [
            OracleAction.VERSION,
            OracleAction.MARKETPLACE_ADD,
            OracleAction.PLUGIN_ADD,
            OracleAction.PLUGIN_REMOVE,
            OracleAction.MARKETPLACE_REMOVE,
            OracleAction.PLUGIN_LIST,
            OracleAction.MARKETPLACE_LIST,
            OracleAction.ABSENCE,
        ]:
            return 15
        return 0
    finally:
        _teardown(allocator, lease)


class CodexRegistrationCompensationAcceptanceTests(unittest.TestCase):
    def test_c1_compensation_acceptance_module_is_available(self) -> None:
        self.assertTrue(callable(_child_compensation))

    def test_c2_to_c7_real_compensation_child_preserves_parent_and_temp(self) -> None:
        before_environment = tuple(sorted(os.environ.items()))
        with tempfile.TemporaryDirectory(prefix=CHILD_TEMP_PREFIX) as temporary_text:
            temporary = Path(temporary_text)
            child_environment = os.environ.copy()
            child_environment["LOCALAPPDATA"] = r"C:\Users\oracle\AppData\Local"
            child_environment["TEMP"] = str(temporary)
            child_environment["TMP"] = str(temporary)
            result = subprocess.run(
                (
                    sys.executable,
                    "-B",
                    "-m",
                    "tests.test_codex_registration_compensation_acceptance",
                    CHILD_ARGUMENT,
                ),
                cwd=Path(__file__).resolve().parents[1],
                env=child_environment,
                shell=False,
                timeout=60,
                check=False,
            )
            self.assertEqual(0, result.returncode)
            self.assertEqual((), tuple(temporary.iterdir()))
        self.assertEqual(before_environment, tuple(sorted(os.environ.items())))


def _run_child_if_requested() -> bool:
    if len(sys.argv) != 2 or sys.argv[1] != CHILD_ARGUMENT:
        return False
    raise SystemExit(_child_compensation())


if __name__ == "__main__":
    if not _run_child_if_requested():
        unittest.main()
