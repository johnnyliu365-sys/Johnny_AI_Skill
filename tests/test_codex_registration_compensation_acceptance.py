"""C1-C8 caller-owned lifecycle evidence for the E5 compensation entrypoint."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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
from tests.staging.codex_lifecycle_oracle.contracts import OracleCompleted, OracleState
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.registration_compensation_acceptance import (
    RegistrationCompensationAccepted,
    RegistrationCompensationRejectReason,
    RegistrationCompensationRejected,
    RegistrationCompensationPhase,
    run_registration_compensation_acceptance,
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
EXPECTED_PHASES = (
    RegistrationCompensationPhase.VERSION,
    RegistrationCompensationPhase.MARKETPLACE_ADD,
    RegistrationCompensationPhase.PLUGIN_ADD,
    RegistrationCompensationPhase.PLUGIN_REMOVE,
    RegistrationCompensationPhase.MARKETPLACE_REMOVE,
    RegistrationCompensationPhase.PLUGIN_LIST,
    RegistrationCompensationPhase.MARKETPLACE_LIST,
    RegistrationCompensationPhase.ABSENCE,
)


class _OracleSubclass(CodexLifecycleOracle):
    pass


class _RequestSubclass(CodexRegistrationPortRequest):
    pass


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


def _child_compensation() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e5b2")
    try:
        _initialize(lease, oracle)
        result = run_registration_compensation_acceptance(lease, oracle, _request())
        if type(result) is not RegistrationCompensationAccepted:
            return 2
        if result.phases != EXPECTED_PHASES:
            return 3
        if not (
            result.original_plugin_add_executed
            and result.owned_state_observed
            and result.owned_payload_observed
            and result.logical_installed_path_absent
            and result.physical_plugin_payload_absent
            and result.replay_blocked
        ):
            return 4
        state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
        plugin_path = oracle.payload_root(lease) / "plugins" / "acceptance-plugin.json"
        if state.marketplaces or state.plugins or plugin_path.exists():
            return 5
        return 0
    finally:
        _teardown(allocator, lease)


class CodexRegistrationCompensationAcceptanceTests(unittest.TestCase):
    def test_p1_compensation_entrypoint_module_is_available(self) -> None:
        self.assertTrue(callable(run_registration_compensation_acceptance))

    def test_p2_invalid_inputs_are_rejected_before_oracle_effect(self) -> None:
        allocator, lease, oracle = _ready_environment("000000000000e5b3")
        try:
            invalid_lease = run_registration_compensation_acceptance(object(), oracle, _request())
            self.assertIs(type(invalid_lease), RegistrationCompensationRejected)
            if type(invalid_lease) is not RegistrationCompensationRejected:
                raise AssertionError("invalid lease must be rejected")
            self.assertIs(invalid_lease.reason, RegistrationCompensationRejectReason.INVALID_LEASE)

            invalid_oracle = run_registration_compensation_acceptance(lease, object(), _request())
            self.assertIs(type(invalid_oracle), RegistrationCompensationRejected)
            if type(invalid_oracle) is not RegistrationCompensationRejected:
                raise AssertionError("invalid oracle must be rejected")
            self.assertIs(invalid_oracle.reason, RegistrationCompensationRejectReason.INVALID_ORACLE)

            subclass_oracle = object.__new__(_OracleSubclass)
            rejected_subclass_oracle = run_registration_compensation_acceptance(lease, subclass_oracle, _request())
            self.assertIs(type(rejected_subclass_oracle), RegistrationCompensationRejected)
            if type(rejected_subclass_oracle) is not RegistrationCompensationRejected:
                raise AssertionError("oracle subclass must be rejected")
            self.assertIs(rejected_subclass_oracle.reason, RegistrationCompensationRejectReason.INVALID_ORACLE)

            invalid_request = run_registration_compensation_acceptance(lease, oracle, object())
            self.assertIs(type(invalid_request), RegistrationCompensationRejected)
            if type(invalid_request) is not RegistrationCompensationRejected:
                raise AssertionError("invalid request must be rejected")
            self.assertIs(invalid_request.reason, RegistrationCompensationRejectReason.INVALID_REQUEST)

            subclass_request = object.__new__(_RequestSubclass)
            rejected_subclass_request = run_registration_compensation_acceptance(lease, oracle, subclass_request)
            self.assertIs(type(rejected_subclass_request), RegistrationCompensationRejected)
            if type(rejected_subclass_request) is not RegistrationCompensationRejected:
                raise AssertionError("request subclass must be rejected")
            self.assertIs(rejected_subclass_request.reason, RegistrationCompensationRejectReason.INVALID_REQUEST)

            malformed_request = CodexRegistrationPortRequest.model_construct()
            malformed = run_registration_compensation_acceptance(lease, oracle, malformed_request)
            self.assertIs(type(malformed), RegistrationCompensationRejected)
            if type(malformed) is not RegistrationCompensationRejected:
                raise AssertionError("constructed-invalid request must be rejected")
            self.assertIs(malformed.reason, RegistrationCompensationRejectReason.INVALID_REQUEST)

            mismatched = _request().model_copy(update={"expected_plugin_id": CodexPluginId(value="other-plugin")})
            identity_mismatch = run_registration_compensation_acceptance(lease, oracle, mismatched)
            self.assertIs(type(identity_mismatch), RegistrationCompensationRejected)
            if type(identity_mismatch) is not RegistrationCompensationRejected:
                raise AssertionError("identity mismatch must be rejected")
            self.assertIs(identity_mismatch.reason, RegistrationCompensationRejectReason.INVALID_IDENTITY)
            self.assertFalse(oracle.state_path(lease).exists())
        finally:
            _teardown(allocator, lease)

    def test_p3_to_p7_real_child_preserves_parent_temp_and_lease_ownership(self) -> None:
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
