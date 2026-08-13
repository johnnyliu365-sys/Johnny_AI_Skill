"""Behavior tests for the staging-only Codex registration oracle adapter."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from library.local_orchestration.codex_command_attempts import (
    CodexCommandTarget,
    CodexPreStartFailure,
    CodexPreStartFailureReason,
    CodexStartedFailure,
    CodexStartedFailureReason,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexMarketplaceAddObservation,
    CodexObservedAbsolutePath,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationAttemptId,
    CodexRegistrationProofPortFailure,
    CodexRegistrationProofRequest,
)
from library.local_orchestration.codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexFreshPreflightRejected,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortCapability,
    CodexRegistrationPortRequest,
    admit_codex_registration_port,
)
from library.local_orchestration.contracts import ArtifactDigest, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import (
    CodexBlockReason,
    CodexCliVersion,
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceSource,
    CodexMarketplaceName,
    CodexPluginEntry,
    CodexPluginList,
    CodexPluginName,
    CodexPreflightRequest,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleBlockReason,
    OracleBlocked,
    OracleCompleted,
    OracleForeignSeeded,
    OracleMarketplaceRecord,
    OraclePluginRecord,
)
from tests.staging.codex_lifecycle_oracle.identity_binding import OracleIdentityBound, bind_oracle_identity
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.registration_adapter import (
    CodexRegistrationOracleAdapter,
    OracleRegistrationAdapterRejectReason,
    OracleRegistrationAdapterRejected,
    create_oracle_registration_adapter,
)
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceAdd,
    CodexProtocolAccepted,
    CodexProtocolSurface,
    CodexVersionObservation,
)
from tests.staging.environment_core.contracts import EnvironmentLease, EnvironmentOwnerId, ProvisionedEnvironment, TeardownStatus
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


CHILD_SUCCESS_ARGUMENT = "--adapter-child-success"
CHILD_INVALID_ARGUMENT = "--adapter-child-invalid-request"
CHILD_VERSION_ARGUMENT = "--adapter-child-version-mismatch"
CHILD_FOREIGN_LIST_ARGUMENT = "--adapter-child-foreign-list"
CHILD_OWNED_CARDINALITY_ARGUMENT = "--adapter-child-owned-cardinality"
CHILD_IDENTITY_ARGUMENT = "--adapter-child-identity-mismatch"
CHILD_PLUGIN_ORDER_ARGUMENT = "--adapter-child-plugin-order"
CHILD_CONSTRUCTED_ARGUMENT = "--adapter-child-constructed-request"
CHILD_PROOF_BEFORE_ARGUMENT = "--adapter-child-proof-before-adds"
CHILD_CONSTRUCTED_ADMISSION_ARGUMENT = "--adapter-child-constructed-admission"
CHILD_PREFLIGHT_CLASSIFICATION_ARGUMENT = "--adapter-child-preflight-classification"
CHILD_TEMP_PREFIX = "e2b-adapter-owned-"


def _request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=InstallationId(value="installation-000000000000e2b2"),
            root=InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
            marketplace=CodexMarketplaceName(value="adapter-market"),
            plugin=CodexPluginName(value="adapter-plugin"),
            marketplace_source=OwnedRelativePath(value="marketplaces/adapter-market"),
        ),
        attempt_id=CodexRegistrationAttemptId(value="attempt-000000000000e2b2"),
        expected_version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=OwnedRelativePath(value="marketplaces/adapter-market"),
        installed_locator=OwnedRelativePath(value="plugins/adapter-plugin"),
        digest=ArtifactDigest(value="e" * 64),
        expected_auth_policy=CodexAuthPolicy(value="trusted-local"),
        expected_plugin_id=CodexPluginId(value="adapter-plugin"),
    )


def _ready_environment(owner_suffix: str) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease, CodexLifecycleOracle]:
    allocator = DisposableEnvironmentAllocator.from_project_runtime()
    provisioned = allocator.provision(EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}"))
    if type(provisioned) is not ProvisionedEnvironment:
        raise AssertionError("failed to provision the test-owned environment")
    oracle = CodexLifecycleOracle(CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort())))
    return allocator, provisioned.environment, oracle


def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
    result = allocator.teardown(lease)
    if result.status is not TeardownStatus.REMOVED:
        raise AssertionError("the exact adapter lease did not tear down")


def _child_success() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b2")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 8
        preflight = admitted.fresh_preflight(_request())
        if type(preflight) is not CodexFreshPreflightAccepted:
            return 4
        marketplace = admitted.add_marketplace(_request())
        if type(marketplace) is not CodexMarketplaceAddSucceeded:
            return 5
        plugin = admitted.add_plugin(_request())
        if type(plugin) is not CodexPluginAddSucceeded:
            return 6
        proof_request = CodexRegistrationProofRequest(
            preflight=_request().preflight,
            version=_request().expected_version,
            marketplace_observation=marketplace.observation,
            plugin_observation=plugin.observation,
            source_locator=_request().source_locator,
            installed_locator=_request().installed_locator,
            digest=_request().digest,
            expected_auth_policy=_request().expected_auth_policy,
        )
        proof = admitted.prove(proof_request)
        if proof.plugin_id.value != _request().expected_plugin_id.value:
            return 9
        return 0
    finally:
        _teardown(allocator, lease)


def _child_invalid_request() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b5")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        before = oracle.state_path(lease).read_bytes()
        foreign = _request().model_copy(
            update={"attempt_id": CodexRegistrationAttemptId(value="attempt-000000000000e2b6")}
        )
        result = admitted.add_marketplace(foreign)
        if type(result) is not CodexRegistrationCommandFailed:
            return 5
        if type(result.failure) is not CodexPreStartFailure:
            return 6
        if result.failure.target is not CodexCommandTarget.MARKETPLACE_ADD:
            return 7
        if result.failure.reason is not CodexPreStartFailureReason.REQUEST_MISMATCH:
            return 8
        if oracle.state_path(lease).read_bytes() != before:
            return 9
        return 0
    finally:
        _teardown(allocator, lease)


def _child_version_mismatch() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b6")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        request = _request().model_copy(update={"expected_version": CodexCliVersion(value="caller-version")})
        binding = bind_oracle_identity(request)
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        result = admitted.fresh_preflight(request)
        if type(result) is not CodexFreshPreflightRejected:
            return 5
        if result.reason is not CodexBlockReason.UNSUPPORTED_CLI:
            return 6
        return 0
    finally:
        _teardown(allocator, lease)


def _child_foreign_list() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b7")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        marketplace = admitted.add_marketplace(_request())
        if type(marketplace) is not CodexMarketplaceAddSucceeded:
            return 5
        plugin = admitted.add_plugin(_request())
        if type(plugin) is not CodexPluginAddSucceeded:
            return 6
        proof_request = CodexRegistrationProofRequest(
            preflight=_request().preflight,
            version=_request().expected_version,
            marketplace_observation=marketplace.observation,
            plugin_observation=plugin.observation,
            source_locator=_request().source_locator,
            installed_locator=_request().installed_locator,
            digest=_request().digest,
            expected_auth_policy=_request().expected_auth_policy,
        )
        foreign_root = r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\foreign-market"
        foreign_bytes = f"marketplace|foreign-market|{foreign_root}".encode("utf-8")
        foreign_plugin_path = r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\foreign-plugin"
        foreign_plugin_bytes = (
            f"plugin|foreign-plugin|foreign-plugin-name|foreign-market|v1|foreign-source|"
            f"foreign-policy|foreign-auth|{foreign_plugin_path}"
        ).encode("utf-8")
        foreign = oracle.seed_foreign_marketplace(
            lease,
            OracleMarketplaceRecord(
                name="foreign-market",
                root=foreign_root,
                locator="marketplaces/foreign-market.json",
                digest=hashlib.sha256(foreign_bytes).hexdigest(),
            ),
        )
        if type(foreign) is not OracleForeignSeeded:
            return 7
        foreign_plugin = oracle.seed_foreign_plugin(
            lease,
            OraclePluginRecord(
                plugin_id="foreign-plugin",
                name="foreign-plugin-name",
                marketplace_name="foreign-market",
                version="v1",
                source="foreign-source",
                install_policy="foreign-policy",
                auth_policy="foreign-auth",
                installed_path=foreign_plugin_path,
                locator="plugins/foreign-plugin.json",
                digest=hashlib.sha256(foreign_plugin_bytes).hexdigest(),
            ),
        )
        if type(foreign_plugin) is not OracleForeignSeeded:
            return 8
        before_state = oracle.state_path(lease).read_bytes()
        before_marketplace = (oracle.payload_root(lease) / "marketplaces/foreign-market.json").read_bytes()
        before_plugin = (oracle.payload_root(lease) / "plugins/foreign-plugin.json").read_bytes()
        try:
            proof = admitted.prove(proof_request)
        except CodexRegistrationProofPortFailure:
            return 9
        if proof.plugin_id.value != _request().expected_plugin_id.value:
            return 10
        if (
            oracle.state_path(lease).read_bytes() != before_state
            or (oracle.payload_root(lease) / "marketplaces/foreign-market.json").read_bytes() != before_marketplace
            or (oracle.payload_root(lease) / "plugins/foreign-plugin.json").read_bytes() != before_plugin
        ):
            return 11
        return 0
    finally:
        _teardown(allocator, lease)


def _child_owned_cardinality() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b7")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        if type(binding) is not OracleIdentityBound:
            return 3
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 4
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 5
        marketplace = admitted.add_marketplace(_request())
        if type(marketplace) is not CodexMarketplaceAddSucceeded:
            return 6
        plugin = admitted.add_plugin(_request())
        if type(plugin) is not CodexPluginAddSucceeded:
            return 7
        proof_request = CodexRegistrationProofRequest(
            preflight=_request().preflight,
            version=_request().expected_version,
            marketplace_observation=marketplace.observation,
            plugin_observation=plugin.observation,
            source_locator=_request().source_locator,
            installed_locator=_request().installed_locator,
            digest=_request().digest,
            expected_auth_policy=_request().expected_auth_policy,
        )
        owned_marketplace = CodexMarketplaceEntry(
            name=binding.identity.marketplace_name,
            root=binding.identity.marketplace_root,
            marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
        )
        owned_plugin = CodexPluginEntry(
            pluginId=binding.identity.plugin_id,
            name=binding.identity.plugin_name,
            marketplaceName=binding.identity.marketplace_name,
            version=binding.identity.plugin_version,
            installed=True,
            enabled=True,
            source=binding.identity.plugin_source,
            installPolicy=binding.identity.plugin_install_policy,
            authPolicy=binding.identity.plugin_auth_policy,
            marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
        )
        foreign_marketplace = CodexMarketplaceEntry(
            name="foreign-market",
            root=r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\foreign-market",
            marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
        )
        foreign_plugin = CodexPluginEntry(
            pluginId="foreign-plugin",
            name="foreign-plugin-name",
            marketplaceName="foreign-market",
            version="v1",
            installed=True,
            enabled=True,
            source="foreign-source",
            installPolicy="foreign-policy",
            authPolicy="foreign-auth",
            marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
        )
        available_plugin = CodexPluginEntry(
            pluginId="available-plugin",
            name="available-plugin-name",
            marketplaceName="available-market",
            version="available-v1",
            installed=False,
            enabled=False,
            source="available-source",
            installPolicy="available-policy",
            authPolicy="available-auth",
            marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
        )
        cases = (
            (
                "marketplace_zero_plugin_one",
                (foreign_marketplace,),
                (owned_plugin,),
            ),
            (
                "marketplace_duplicate_plugin_one",
                (owned_marketplace, owned_marketplace),
                (owned_plugin,),
            ),
            (
                "marketplace_one_plugin_zero",
                (owned_marketplace,),
                (foreign_plugin,),
            ),
            (
                "marketplace_one_plugin_duplicate",
                (owned_marketplace,),
                (owned_plugin, owned_plugin),
            ),
        )
        before = oracle.state_path(lease).read_bytes()
        for case_name, marketplace_entries, plugin_entries in cases:
            _ = case_name
            responses = (
                OracleCompleted(
                    response=CodexProtocolAccepted(
                        surface=CodexProtocolSurface.MARKETPLACE_LIST,
                        payload=CodexMarketplaceList(marketplaces=marketplace_entries),
                    )
                ),
                OracleCompleted(
                    response=CodexProtocolAccepted(
                        surface=CodexProtocolSurface.PLUGIN_LIST,
                        payload=CodexPluginList(installed=plugin_entries, available=(available_plugin,)),
                    )
                ),
            )
            with patch.object(oracle, "run", side_effect=responses):
                try:
                    admitted.prove(proof_request)
                except CodexRegistrationProofPortFailure:
                    pass
                else:
                    return 8
            if oracle.state_path(lease).read_bytes() != before:
                return 9
        return 0
    finally:
        _teardown(allocator, lease)


def _child_identity_mismatch() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b8")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        foreign_identity = adapter._bound.identity.model_copy(
            update={"marketplace_root": r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\foreign"}
        )
        adapter._bound = adapter._bound.model_copy(update={"identity": foreign_identity})
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        expected_root = r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\adapter-market"
        response = OracleCompleted(
            response=CodexProtocolAccepted(
                surface=CodexProtocolSurface.MARKETPLACE_ADD,
                payload=CodexMarketplaceAdd(
                    marketplaceName="adapter-market",
                    installedRoot=expected_root,
                    alreadyAdded=False,
                ),
            )
        )
        with patch.object(oracle, "run", return_value=response):
            result = admitted.add_marketplace(_request())
        if type(result) is not CodexRegistrationCommandFailed:
            return 5
        if type(result.failure) is not CodexStartedFailure:
            return 6
        if result.failure.reason is not CodexStartedFailureReason.IDENTITY_MISMATCH:
            return 7
        return 0
    finally:
        _teardown(allocator, lease)


def _child_plugin_order() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2b9")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        before = oracle.state_path(lease).read_bytes()
        result = admitted.add_plugin(_request())
        if type(result) is not CodexRegistrationCommandFailed:
            return 5
        if type(result.failure) is not CodexPreStartFailure:
            return 6
        if result.failure.reason is not CodexPreStartFailureReason.INVALID_REQUEST:
            return 7
        if oracle.state_path(lease).read_bytes() != before:
            return 8
        return 0
    finally:
        _teardown(allocator, lease)


def _child_constructed_request() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2ba")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        malformed = CodexRegistrationPortRequest.model_construct(
            preflight=_request().preflight,
            attempt_id="not-a-typed-attempt",
            expected_version=_request().expected_version,
            source_locator=_request().source_locator,
            installed_locator=_request().installed_locator,
            digest=_request().digest,
            expected_auth_policy=_request().expected_auth_policy,
            expected_plugin_id=_request().expected_plugin_id,
        )
        before = oracle.state_path(lease).read_bytes()
        result = admitted.add_marketplace(malformed)
        if type(result) is not CodexRegistrationCommandFailed:
            return 5
        if type(result.failure) is not CodexPreStartFailure:
            return 6
        if result.failure.reason is not CodexPreStartFailureReason.INVALID_REQUEST:
            return 7
        if oracle.state_path(lease).read_bytes() != before:
            return 8
        return 0
    finally:
        _teardown(allocator, lease)


def _child_proof_before_adds() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2bb")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        request = _request()
        binding = bind_oracle_identity(request)
        if type(binding) is not OracleIdentityBound:
            return 3
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 4
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 5
        proof_request = CodexRegistrationProofRequest(
            preflight=request.preflight,
            version=request.expected_version,
            marketplace_observation=CodexMarketplaceAddObservation(
                marketplace_name=request.preflight.marketplace,
                installed_root=CodexObservedAbsolutePath(value=binding.identity.marketplace_root),
                already_added=False,
            ),
            plugin_observation=CodexPluginAddObservation(
                plugin_id=request.expected_plugin_id,
                name=request.preflight.plugin,
                marketplace_name=request.preflight.marketplace,
                version=request.expected_version,
                installed_path=CodexObservedAbsolutePath(value=binding.identity.plugin_installed_path),
                auth_policy=request.expected_auth_policy,
            ),
            source_locator=request.source_locator,
            installed_locator=request.installed_locator,
            digest=request.digest,
            expected_auth_policy=request.expected_auth_policy,
        )
        before = oracle.state_path(lease).read_bytes()
        try:
            admitted.prove(proof_request)
        except CodexRegistrationProofPortFailure:
            pass
        else:
            return 6
        if oracle.state_path(lease).read_bytes() != before:
            return 7
        return 0
    finally:
        _teardown(allocator, lease)


def _child_constructed_admission() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2bc")
    try:
        binding = bind_oracle_identity(_request())
        if type(binding) is not OracleIdentityBound:
            return 2
        malformed = OracleIdentityBound.model_construct(
            status="ORACLE_IDENTITY_BOUND",
            request=binding.request,
            identity=binding.identity,
        )
        object.__getattribute__(malformed, "__dict__")["injected"] = "untrusted"
        result = create_oracle_registration_adapter(lease, oracle, malformed)
        if type(result) is not OracleRegistrationAdapterRejected:
            return 3
        if result.reason is not OracleRegistrationAdapterRejectReason.INVALID_BINDING:
            return 4
        incomplete_lease = EnvironmentLease.model_construct(owner=lease.owner)
        lease_result = create_oracle_registration_adapter(incomplete_lease, oracle, binding)
        if type(lease_result) is not OracleRegistrationAdapterRejected:
            return 5
        if lease_result.reason is not OracleRegistrationAdapterRejectReason.INVALID_LEASE:
            return 6
        return 0
    finally:
        _teardown(allocator, lease)


def _child_preflight_classification() -> int:
    allocator, lease, oracle = _ready_environment("000000000000e2bd")
    try:
        if type(oracle.initialize(lease)) is not OracleCompleted:
            return 2
        binding = bind_oracle_identity(_request())
        adapter = create_oracle_registration_adapter(lease, oracle, binding)
        if type(adapter) is not CodexRegistrationOracleAdapter:
            return 3
        admitted = admit_codex_registration_port(adapter)
        if type(admitted) is not CodexRegistrationPortCapability:
            return 4
        malformed = OracleCompleted(
            response=CodexProtocolAccepted(
                surface=CodexProtocolSurface.MARKETPLACE_ADD,
                payload=CodexMarketplaceAdd(
                    marketplaceName="adapter-market",
                    installedRoot=r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\adapter-market",
                    alreadyAdded=False,
                ),
            )
        )
        mismatch = OracleCompleted(
            response=CodexProtocolAccepted(
                surface=CodexProtocolSurface.VERSION,
                payload=CodexVersionObservation(version="different-version"),
            )
        )
        cases: tuple[tuple[OracleBlocked | OracleCompleted, CodexBlockReason], ...] = (
            (OracleBlocked(reason=OracleBlockReason.STATE_INVALID), CodexBlockReason.COMMAND_FAILED),
            (malformed, CodexBlockReason.MALFORMED_OUTPUT),
            (mismatch, CodexBlockReason.UNSUPPORTED_CLI),
        )
        for response, expected_reason in cases:
            with patch.object(oracle, "run", return_value=response):
                result = admitted.fresh_preflight(_request())
            if type(result) is not CodexFreshPreflightRejected:
                return 5
            if result.reason is not expected_reason:
                return 6
        return 0
    finally:
        _teardown(allocator, lease)


class CodexRegistrationOracleAdapterTests(unittest.TestCase):
    """The adapter is a closed staging seam, not a caller-synthesized port."""

    def test_r1_factory_module_is_available(self) -> None:
        self.assertTrue(callable(create_oracle_registration_adapter))

    def test_r2_ambient_logical_root_mismatch_blocks_before_oracle_effect(self) -> None:
        allocator, lease, oracle = _ready_environment("000000000000e2b3")
        try:
            binding = bind_oracle_identity(_request())
            result = create_oracle_registration_adapter(lease, oracle, binding)
            self.assertIs(type(result), OracleRegistrationAdapterRejected)
            if type(result) is not OracleRegistrationAdapterRejected:
                raise AssertionError("expected a finite adapter rejection")
            self.assertIs(result.reason, OracleRegistrationAdapterRejectReason.LOGICAL_ROOT_MISMATCH)
            self.assertFalse(oracle.state_path(lease).exists())
        finally:
            _teardown(allocator, lease)

    def test_r2_invalid_binding_is_rejected_before_logical_root_or_oracle_effect(self) -> None:
        allocator, lease, oracle = _ready_environment("000000000000e2b4")
        try:
            result = create_oracle_registration_adapter(lease, oracle, object())
            self.assertIs(type(result), OracleRegistrationAdapterRejected)
            if type(result) is not OracleRegistrationAdapterRejected:
                raise AssertionError("invalid binding must reject before any oracle invocation")
            self.assertIs(result.reason, OracleRegistrationAdapterRejectReason.INVALID_BINDING)
            self.assertFalse(oracle.state_path(lease).exists())
        finally:
            _teardown(allocator, lease)

    def test_r7_child_success_uses_fixed_logical_environment_without_parent_mutation(self) -> None:
        self._run_child(CHILD_SUCCESS_ARGUMENT)

    def test_r3_child_version_is_persisted_not_caller_substituted(self) -> None:
        self._run_child(CHILD_VERSION_ARGUMENT)

    def test_r4_foreign_request_is_not_started_and_leaves_oracle_state_unchanged(self) -> None:
        self._run_child(CHILD_INVALID_ARGUMENT)

    def test_r6_foreign_fresh_list_preserves_owned_proof(self) -> None:
        self._run_child(CHILD_FOREIGN_LIST_ARGUMENT)

    def test_r6_zero_or_duplicate_owned_matches_raise_declared_proof_failure(self) -> None:
        self._run_child(CHILD_OWNED_CARDINALITY_ARGUMENT)

    def test_r4_accepted_payload_that_disagrees_with_retained_identity_is_started_failure(self) -> None:
        self._run_child(CHILD_IDENTITY_ARGUMENT)

    def test_r5_plugin_before_owned_marketplace_is_not_started_without_oracle_mutation(self) -> None:
        self._run_child(CHILD_PLUGIN_ORDER_ARGUMENT)

    def test_r4_constructed_invalid_request_is_not_started_without_oracle_mutation(self) -> None:
        self._run_child(CHILD_CONSTRUCTED_ARGUMENT)

    def test_r6_proof_before_same_instance_exact_adds_is_declared_failure_without_list_effect(self) -> None:
        self._run_child(CHILD_PROOF_BEFORE_ARGUMENT)

    def test_cr162_direct_constructor_requires_private_factory_authority(self) -> None:
        allocator, lease, oracle = _ready_environment("000000000000e2be")
        try:
            binding = bind_oracle_identity(_request())
            if type(binding) is not OracleIdentityBound:
                raise AssertionError("expected a finite identity binding")
            with self.assertRaises(TypeError):
                CodexRegistrationOracleAdapter(object(), lease, oracle, binding)
            self.assertFalse(oracle.state_path(lease).exists())
        finally:
            _teardown(allocator, lease)

    def test_cr163_constructed_bound_state_is_finitely_rejected(self) -> None:
        self._run_child(CHILD_CONSTRUCTED_ADMISSION_ARGUMENT)

    def test_cr164_preflight_classifies_block_malformed_and_version_mismatch(self) -> None:
        self._run_child(CHILD_PREFLIGHT_CLASSIFICATION_ARGUMENT)

    def _run_child(self, argument: str) -> None:
        before = tuple(sorted(os.environ.items()))
        with tempfile.TemporaryDirectory(prefix=CHILD_TEMP_PREFIX) as temporary_text:
            temporary = Path(temporary_text)
            child_environment = os.environ.copy()
            child_environment["LOCALAPPDATA"] = r"C:\Users\oracle\AppData\Local"
            child_environment["TEMP"] = str(temporary)
            child_environment["TMP"] = str(temporary)
            result = subprocess.run(
                (sys.executable, "-B", "-m", "tests.test_codex_registration_oracle_adapter", argument),
                cwd=Path(__file__).resolve().parents[1],
                env=child_environment,
                shell=False,
                timeout=30,
                check=False,
            )
            self.assertEqual(0, result.returncode)
            self.assertEqual((), tuple(temporary.iterdir()))
        self.assertEqual(before, tuple(sorted(os.environ.items())))


def _run_child_if_requested() -> bool:
    if len(sys.argv) != 2:
        return False
    child_action = sys.argv[1]
    if child_action == CHILD_SUCCESS_ARGUMENT:
        raise SystemExit(_child_success())
    if child_action == CHILD_INVALID_ARGUMENT:
        raise SystemExit(_child_invalid_request())
    if child_action == CHILD_VERSION_ARGUMENT:
        raise SystemExit(_child_version_mismatch())
    if child_action == CHILD_FOREIGN_LIST_ARGUMENT:
        raise SystemExit(_child_foreign_list())
    if child_action == CHILD_OWNED_CARDINALITY_ARGUMENT:
        raise SystemExit(_child_owned_cardinality())
    if child_action == CHILD_IDENTITY_ARGUMENT:
        raise SystemExit(_child_identity_mismatch())
    if child_action == CHILD_PLUGIN_ORDER_ARGUMENT:
        raise SystemExit(_child_plugin_order())
    if child_action == CHILD_CONSTRUCTED_ARGUMENT:
        raise SystemExit(_child_constructed_request())
    if child_action == CHILD_PROOF_BEFORE_ARGUMENT:
        raise SystemExit(_child_proof_before_adds())
    if child_action == CHILD_CONSTRUCTED_ADMISSION_ARGUMENT:
        raise SystemExit(_child_constructed_admission())
    if child_action == CHILD_PREFLIGHT_CLASSIFICATION_ARGUMENT:
        raise SystemExit(_child_preflight_classification())
    return False


if __name__ == "__main__":
    _run_child_if_requested()
    unittest.main()
