"""S1-S8 acceptance tests for the staging-only registration success harness."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from library.local_orchestration.codex_registration_contracts import (
    CodexPluginId,
    CodexAuthPolicy,
    CodexRegistrationAttemptId,
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
)
from library.local_orchestration.codex_registration_proof_settlement import settle_codex_registration_proof
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationProofClaim,
    CodexRegistrationSettlementAuthority,
    CodexRegistrationSettlementClaimBlocked,
    admit_codex_registration_settlement_authority,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationNextReadyPhase,
    CodexRegistrationReadyLease,
)
from library.local_orchestration.contracts import ArtifactDigest, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import (
    CodexCliVersion,
    CodexMarketplaceName,
    CodexPluginName,
    CodexPreflightRequest,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleAction,
    OracleBlockReason,
    OracleBlocked,
    OracleCommand,
    OracleCompleted,
    OracleIdentity,
    OracleRunResult,
    OracleState,
)
from tests.staging.codex_lifecycle_oracle.identity_binding import OracleIdentityBound, bind_oracle_identity
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.registration_adapter import (
    CodexRegistrationOracleAdapter,
    create_oracle_registration_adapter,
)
from tests.staging.codex_lifecycle_oracle.registration_success_acceptance import (
    RegistrationSuccessAccepted,
    RegistrationSuccessPhase,
    RegistrationSuccessRejectReason,
    RegistrationSuccessRejected,
    run_registration_success_acceptance,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


CHILD_SUCCESS_ARGUMENT = "--success-acceptance-child"
CHILD_CLAIM_ARGUMENT = "--claim-acceptance-child"
CHILD_PAYLOAD_ARGUMENT = "--payload-acceptance-child"
CHILD_TEMP_PREFIX = "e4-success-owned-"


class _ForwardCoordinatorSubclass(CodexRegistrationForwardCoordinator):
    pass


class _OracleSubclass(CodexLifecycleOracle):
    pass


def _request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=InstallationId(value="installation-000000000000e4b2"),
            root=InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
            marketplace=CodexMarketplaceName(value="acceptance-market"),
            plugin=CodexPluginName(value="acceptance-plugin"),
            marketplace_source=OwnedRelativePath(value="marketplaces/acceptance-market"),
        ),
        attempt_id=CodexRegistrationAttemptId(value="attempt-000000000000e4b2"),
        expected_version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=OwnedRelativePath(value="marketplaces/acceptance-market"),
        installed_locator=OwnedRelativePath(value="plugins/acceptance-plugin"),
        digest=ArtifactDigest(value="a" * 64),
        expected_auth_policy=CodexAuthPolicy(value="trusted-local"),
        expected_plugin_id=CodexPluginId(value="acceptance-plugin"),
    )


def _ready_environment(owner_suffix: str) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease, CodexLifecycleOracle]:
    allocator = DisposableEnvironmentAllocator.from_project_runtime()
    provisioned = allocator.provision(EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}"))
    if type(provisioned) is not ProvisionedEnvironment:
        raise AssertionError("failed to provision the test-owned environment")
    oracle = CodexLifecycleOracle(CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort())))
    return allocator, provisioned.environment, oracle


def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
    root = lease.root.path
    result = allocator.teardown(lease)
    if result.status is not TeardownStatus.REMOVED or root.exists():
        raise AssertionError("the exact E4 lease did not tear down")


def _initialize(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
) -> None:
    if type(oracle.initialize(lease)) is not OracleCompleted:
        raise AssertionError("oracle initialization failed")


def _child_success() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e4b2")
    try:
        _initialize(lease, oracle)
        before_state = oracle.state_path(lease).read_bytes()
        observed: list[OracleAction] = []
        original_run = oracle.run

        def observed_run(current: EnvironmentLease, action_command: object) -> OracleRunResult:
            if type(action_command) is not OracleCommand:
                return OracleBlocked(reason=OracleBlockReason.COMMAND_INVALID)
            command = action_command
            observed.append(command.action)
            return original_run(current, command)

        with patch.object(oracle, "run", side_effect=observed_run):
            result = run_registration_success_acceptance(lease, oracle, _request())
        if type(result) is not RegistrationSuccessAccepted:
            return 2
        if result.metadata.phases != (
            RegistrationSuccessPhase.VERSION,
            RegistrationSuccessPhase.MARKETPLACE_ADD,
            RegistrationSuccessPhase.PLUGIN_ADD,
            RegistrationSuccessPhase.MARKETPLACE_LIST,
            RegistrationSuccessPhase.PLUGIN_LIST,
        ):
            return 3
        if observed != [
            OracleAction.VERSION,
            OracleAction.MARKETPLACE_ADD,
            OracleAction.PLUGIN_ADD,
            OracleAction.MARKETPLACE_LIST,
            OracleAction.PLUGIN_LIST,
        ]:
            return 4
        if type(result.receipt) is not CodexRegistrationReceipt:
            return 5
        if oracle.state_path(lease).read_bytes() == before_state:
            return 8
        state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
        if (
            len(state.marketplaces) != 1
            or len(state.plugins) != 1
            or len(state.foreign_marketplaces) != 0
            or len(state.foreign_plugins) != 0
        ):
            return 6
        if result.receipt.digest != _request().digest:
            return 9
        return 0
    finally:
        _teardown(allocator, lease)


def _build_claim(
    lease: EnvironmentLease,
    oracle: CodexLifecycleOracle,
) -> tuple[
    CodexRegistrationOracleAdapter,
    CodexRegistrationProofClaim,
    CodexRegistrationSettlementAuthority,
]:
    binding = bind_oracle_identity(_request())
    if type(binding) is not OracleIdentityBound:
        raise AssertionError("request identity did not bind")
    adapter = create_oracle_registration_adapter(lease, oracle, binding)
    if type(adapter) is not CodexRegistrationOracleAdapter:
        raise AssertionError("adapter admission failed")
    port = admit_codex_registration_port(adapter)
    if type(port) is not CodexRegistrationPortCapability:
        raise AssertionError("port admission failed")
    forward = admit_codex_registration_forward(port)
    if type(forward) is not CodexRegistrationForwardCoordinator:
        raise AssertionError("forward admission failed")
    authority = admit_codex_registration_settlement_authority(forward)
    if type(authority) is not CodexRegistrationSettlementAuthority:
        raise AssertionError("settlement admission failed")
    fresh = authority.begin(_request())
    if type(fresh) is not CodexRegistrationReadyLease:
        raise AssertionError("fresh lease was not issued")
    marketplace = authority.execute(fresh.lease)
    if type(marketplace) is not CodexRegistrationNextReadyPhase:
        raise AssertionError("marketplace phase did not advance")
    plugin = authority.execute(marketplace.lease)
    if type(plugin) is not CodexRegistrationNextReadyPhase:
        raise AssertionError("plugin phase did not advance")
    claim = authority.execute(plugin.lease)
    if type(claim) is not CodexRegistrationProofClaim:
        raise AssertionError("proof claim was not issued")
    return adapter, claim, authority


def _child_claim() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e4b3")
    try:
        _initialize(lease, oracle)
        adapter, claim, authority = _build_claim(lease, oracle)
        _ = authority
        settled = settle_codex_registration_proof(claim, adapter)
        if type(settled) is not CodexRegistrationReceipt:
            return 3
        replay = settle_codex_registration_proof(claim, adapter)
        if type(replay) is not CodexRegistrationSettlementClaimBlocked:
            return 4
        fabricated = settle_codex_registration_proof(object(), adapter)
        if type(fabricated) is not CodexRegistrationSettlementClaimBlocked:
            return 5
        return 0
    finally:
        _teardown(allocator, lease)


def _child_payload() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e4b4")
    try:
        _initialize(lease, oracle)
        original_run = oracle.run

        def corrupt_after_plugin_list(current: EnvironmentLease, action_command: object) -> OracleRunResult:
            if type(action_command) is not OracleCommand:
                return OracleBlocked(reason=OracleBlockReason.COMMAND_INVALID)
            command = action_command
            result = original_run(current, command)
            if command.action is OracleAction.PLUGIN_LIST:
                plugin_path = oracle.payload_root(current) / "plugins" / "acceptance-plugin.json"
                plugin_path.write_bytes(b"tampered-plugin-payload")
            return result

        with patch.object(oracle, "run", side_effect=corrupt_after_plugin_list):
            result = run_registration_success_acceptance(lease, oracle, _request())
        if type(result) is not RegistrationSuccessRejected:
            return 3
        if result.reason is not RegistrationSuccessRejectReason.INVALID_PHYSICAL_PAYLOAD:
            return 4
        return 0
    finally:
        _teardown(allocator, lease)


class CodexRegistrationSuccessAcceptanceTests(unittest.TestCase):
    def test_s1_success_acceptance_module_is_available(self) -> None:
        self.assertTrue(callable(run_registration_success_acceptance))

    def test_s2_invalid_lease_or_request_is_rejected_before_effect(self) -> None:
        allocator, lease, oracle = _ready_environment("000000000000e4b5")
        try:
            invalid_lease = run_registration_success_acceptance(object(), oracle, _request())
            self.assertIs(type(invalid_lease), RegistrationSuccessRejected)
            if type(invalid_lease) is not RegistrationSuccessRejected:
                raise AssertionError("invalid lease must be rejected")
            self.assertIs(invalid_lease.reason, RegistrationSuccessRejectReason.INVALID_LEASE)
            invalid_request = run_registration_success_acceptance(lease, oracle, object())
            self.assertIs(type(invalid_request), RegistrationSuccessRejected)
            if type(invalid_request) is not RegistrationSuccessRejected:
                raise AssertionError("invalid request must be rejected")
            self.assertIs(invalid_request.reason, RegistrationSuccessRejectReason.INVALID_REQUEST)
            invalid_oracle = run_registration_success_acceptance(lease, object(), _request())
            self.assertIs(type(invalid_oracle), RegistrationSuccessRejected)
            if type(invalid_oracle) is not RegistrationSuccessRejected:
                raise AssertionError("invalid oracle must be rejected")
            self.assertIs(invalid_oracle.reason, RegistrationSuccessRejectReason.INVALID_ORACLE)
            mismatched_request = _request().model_copy(
                update={"expected_plugin_id": CodexPluginId(value="mismatch-plugin")}
            )
            mismatched = run_registration_success_acceptance(lease, oracle, mismatched_request)
            self.assertIs(type(mismatched), RegistrationSuccessRejected)
            if type(mismatched) is not RegistrationSuccessRejected:
                raise AssertionError("mismatched request must be rejected")
            self.assertIn(
                mismatched.reason,
                (RegistrationSuccessRejectReason.INVALID_IDENTITY, RegistrationSuccessRejectReason.INVALID_ADAPTER),
            )
            subclass_oracle = object.__new__(_OracleSubclass)
            invalid_subclass = run_registration_success_acceptance(lease, subclass_oracle, _request())
            self.assertIs(type(invalid_subclass), RegistrationSuccessRejected)
            if type(invalid_subclass) is not RegistrationSuccessRejected:
                raise AssertionError("oracle subclass must be rejected")
            self.assertIs(invalid_subclass.reason, RegistrationSuccessRejectReason.INVALID_ORACLE)
            constructed_forward = object.__new__(CodexRegistrationForwardCoordinator)
            subclass_forward = object.__new__(_ForwardCoordinatorSubclass)
            self.assertNotEqual(type(admit_codex_registration_forward(object())), CodexRegistrationForwardCoordinator)
            self.assertNotEqual(type(admit_codex_registration_settlement_authority(constructed_forward)), CodexRegistrationSettlementAuthority)
            self.assertNotEqual(type(admit_codex_registration_settlement_authority(subclass_forward)), CodexRegistrationSettlementAuthority)
            self.assertFalse(oracle.state_path(lease).exists())
        finally:
            _teardown(allocator, lease)

    def test_s3_s4_s5_s7_clean_child_success_order_payload_parent_preservation_unique_child_temp_absence_and_exact_lease_teardown(self) -> None:
        self._run_child(CHILD_SUCCESS_ARGUMENT)

    def test_s6_one_shot_claim_replay_and_fabrication_are_blocked(self) -> None:
        self._run_child(CHILD_CLAIM_ARGUMENT)

    def test_s8_physical_payload_identity_and_digest_gate(self) -> None:
        self._run_child(CHILD_PAYLOAD_ARGUMENT)

    def _run_child(self, argument: str) -> None:
        before_environment = tuple(sorted(os.environ.items()))
        with tempfile.TemporaryDirectory(prefix=CHILD_TEMP_PREFIX) as temporary_text:
            temporary = Path(temporary_text)
            child_environment = os.environ.copy()
            child_environment["LOCALAPPDATA"] = r"C:\Users\oracle\AppData\Local"
            child_environment["TEMP"] = str(temporary)
            child_environment["TMP"] = str(temporary)
            result = subprocess.run(
                (sys.executable, "-B", "-m", "tests.test_codex_registration_success_acceptance", argument),
                cwd=Path(__file__).resolve().parents[1],
                env=child_environment,
                shell=False,
                timeout=45,
                check=False,
            )
            self.assertEqual(0, result.returncode)
            self.assertEqual((), tuple(temporary.iterdir()))
        self.assertEqual(before_environment, tuple(sorted(os.environ.items())))


def _run_child_if_requested() -> bool:
    if len(sys.argv) != 2:
        return False
    if sys.argv[1] == CHILD_SUCCESS_ARGUMENT:
        raise SystemExit(_child_success())
    if sys.argv[1] == CHILD_CLAIM_ARGUMENT:
        raise SystemExit(_child_claim())
    if sys.argv[1] == CHILD_PAYLOAD_ARGUMENT:
        raise SystemExit(_child_payload())
    return False


if __name__ == "__main__":
    _run_child_if_requested()
    unittest.main()
