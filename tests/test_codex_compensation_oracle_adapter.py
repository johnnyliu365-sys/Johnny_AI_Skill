"""A1-A8 closure for the thin Codex compensation oracle adapter."""

from __future__ import annotations

import unittest
from contextlib import AbstractContextManager
from typing import cast
from unittest.mock import patch

from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortCapability,
    CodexCompensationPortFailureReason,
    CodexCompensationPortManifest,
    CodexCompensationPortOperation,
    CodexCompensationPortOperationFailed,
    CodexCompensationPortRequest,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
    admit_codex_compensation_port,
)
from library.local_orchestration.codex_registration_contracts import CodexAuthPolicy, CodexPluginId
from library.local_orchestration.contracts import (
    ArtifactDigest,
    CANONICAL_INSTALL_ROOT,
    InstallRoot,
    InstallationId,
    OwnedRelativePath,
)
from library.local_orchestration.host_contracts import (
    CodexCliVersion,
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceName,
    CodexMarketplaceSource,
    CodexPluginEntry,
    CodexPluginList,
    CodexPluginName,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleAction,
    OracleBlockReason,
    OracleBlocked,
    OracleCommand,
    OracleCompleted,
    OracleIdentity,
    OracleRunResult,
    OracleAbsent,
)
from tests.staging.codex_lifecycle_oracle.identity_binding import (
    FIXED_STAGING_LOGICAL_ROOT,
    STAGING_PLUGIN_INSTALL_POLICY,
    STAGING_PLUGIN_SOURCE,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceRemove,
    CodexPluginRemove,
    CodexProtocolAccepted,
    CodexProtocolSurface,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentId,
    EnvironmentLocator,
    EnvironmentMarker,
    EnvironmentOverlay,
    EnvironmentOverlayEntry,
    EnvironmentOwnerId,
    EnvironmentPath,
    EnvironmentRelativeLocator,
    EnvironmentVariable,
)

from tests.staging.codex_lifecycle_oracle.compensation_adapter import (
    CodexCompensationOracleAdapter,
    CodexCompensationOracleAdapterRejected,
    CodexCompensationOracleAdapterRejectReason,
    create_oracle_compensation_adapter,
)


INSTALLATION = InstallationId(value="installation-000000000000e3e3")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="adapter-market")
PLUGIN = CodexPluginName(value="adapter-plugin-name")
PLUGIN_ID = CodexPluginId(value="adapter-plugin")
VERSION = CodexCliVersion(value="adapter-version")
SOURCE = OwnedRelativePath(value="marketplaces/adapter-market")
INSTALLED = OwnedRelativePath(value="plugins/adapter-plugin")
AUTH_POLICY = CodexAuthPolicy(value="adapter-auth")
DIGEST = ArtifactDigest(value="e" * 64)


def manifest() -> CodexCompensationPortManifest:
    return CodexCompensationPortManifest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        marketplace_source=SOURCE,
        plugin_id=PLUGIN_ID,
        plugin=PLUGIN,
        version=VERSION,
        installed_locator=INSTALLED,
        auth_policy=AUTH_POLICY,
        digest=DIGEST,
    )


def request() -> CodexCompensationPortRequest:
    return CodexCompensationPortRequest(manifest=manifest())


def identity() -> OracleIdentity:
    return OracleIdentity(
        marketplace_name=MARKETPLACE.value,
        marketplace_root=rf"{FIXED_STAGING_LOGICAL_ROOT}\marketplaces\adapter-market",
        plugin_id=PLUGIN_ID.value,
        plugin_name=PLUGIN.value,
        plugin_version=VERSION.value,
        plugin_source=STAGING_PLUGIN_SOURCE,
        plugin_install_policy=STAGING_PLUGIN_INSTALL_POLICY,
        plugin_auth_policy=AUTH_POLICY.value,
        plugin_installed_path=rf"{FIXED_STAGING_LOGICAL_ROOT}\plugins\adapter-plugin",
    )


def _oracle() -> CodexLifecycleOracle:
    return object.__new__(CodexLifecycleOracle)


def _lease(owner_suffix: str) -> EnvironmentLease:
    owner = EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}")
    environment_id = EnvironmentId(value=f"environment-{'0' * 16}{owner_suffix}")
    root_name = f"e3-{owner_suffix[-4:]}"
    root = EnvironmentLocator(value=rf"C:\E3\{root_name}")

    def child(relative: str) -> EnvironmentPath:
        return EnvironmentPath(
            relative=EnvironmentRelativeLocator(value=relative),
            absolute=EnvironmentLocator(value=rf"{root.value}\{relative}"),
        )

    profile = child("profile")
    local_app_data = child("local-app-data")
    roaming_app_data = child("roaming-app-data")
    temporary = child("temp")
    codex_home = child("codex-home")
    overlay = EnvironmentOverlay(
        entries=(
            EnvironmentOverlayEntry(key=EnvironmentVariable.USERPROFILE, path=profile.absolute),
            EnvironmentOverlayEntry(key=EnvironmentVariable.LOCALAPPDATA, path=local_app_data.absolute),
            EnvironmentOverlayEntry(key=EnvironmentVariable.APPDATA, path=roaming_app_data.absolute),
            EnvironmentOverlayEntry(key=EnvironmentVariable.TEMP, path=temporary.absolute),
            EnvironmentOverlayEntry(key=EnvironmentVariable.TMP, path=temporary.absolute),
            EnvironmentOverlayEntry(key=EnvironmentVariable.CODEX_HOME, path=codex_home.absolute),
        )
    )
    return EnvironmentLease(
        owner=owner,
        environment_id=environment_id,
        root=root,
        root_relative=EnvironmentRelativeLocator(value=root_name),
        profile=profile,
        local_app_data=local_app_data,
        roaming_app_data=roaming_app_data,
        temporary=temporary,
        codex_home=codex_home,
        overlay=overlay,
        marker=EnvironmentMarker(owner=owner, environment_id=environment_id, root=root),
    )


class _InMemoryOwner:
    """No-op owner marker for adapter-only tests; no runtime is allocated."""


def _ready(owner_suffix: str) -> tuple[_InMemoryOwner, EnvironmentLease, CodexLifecycleOracle]:
    return _InMemoryOwner(), _lease(owner_suffix), _oracle()


def _teardown(owner: _InMemoryOwner, lease: EnvironmentLease) -> None:
    del owner, lease


def _adapter(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> CodexCompensationOracleAdapter:
    with patch(
        "tests.staging.codex_lifecycle_oracle.compensation_adapter.ntpath.expandvars",
        return_value=FIXED_STAGING_LOGICAL_ROOT,
    ):
        result = create_oracle_compensation_adapter(lease, oracle, request())
    if type(result) is not CodexCompensationOracleAdapter:
        raise AssertionError(f"expected adapter, received {result}")
    return result


def _response(surface: CodexProtocolSurface, payload: object) -> OracleCompleted:
    return OracleCompleted(
        response=CodexProtocolAccepted.model_construct(surface=surface, payload=payload)
    )


def _plugin_remove_payload() -> CodexPluginRemove:
    return CodexPluginRemove(
        pluginId=PLUGIN_ID.value,
        name=PLUGIN.value,
        marketplaceName=MARKETPLACE.value,
    )


def _marketplace_remove_payload() -> CodexMarketplaceRemove:
    return CodexMarketplaceRemove(
        marketplaceName=MARKETPLACE.value,
        installedRoot=identity().marketplace_root,
    )


def _plugin_entry(name: str, plugin_id: str) -> CodexPluginEntry:
    return CodexPluginEntry(
        pluginId=plugin_id,
        name=name,
        marketplaceName=MARKETPLACE.value,
        version=VERSION.value,
        installed=True,
        enabled=True,
        source="foreign-source" if plugin_id.startswith("foreign") else STAGING_PLUGIN_SOURCE,
        installPolicy="foreign-policy" if plugin_id.startswith("foreign") else STAGING_PLUGIN_INSTALL_POLICY,
        authPolicy="foreign-auth" if plugin_id.startswith("foreign") else AUTH_POLICY.value,
        marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
    )


def _marketplace_entry(name: str) -> CodexMarketplaceEntry:
    return CodexMarketplaceEntry(
        name=name,
        root=identity().marketplace_root if name == MARKETPLACE.value else rf"C:\Foreign\{name}",
        marketplaceSource=CodexMarketplaceSource(type="local", value="oracle-source"),
    )


def _failure(
    value: object,
    operation: CodexCompensationPortOperation,
    reason: CodexCompensationPortFailureReason,
) -> CodexCompensationPortOperationFailed:
    if type(value) is not CodexCompensationPortOperationFailed:
        raise AssertionError(f"expected finite operation failure, received {value}")
    if value.operation is not operation or value.reason is not reason:
        raise AssertionError(f"unexpected operation failure: {value}")
    return value


def _run_with(
    oracle: CodexLifecycleOracle,
    response: OracleRunResult,
    actions: list[OracleAction],
) -> AbstractContextManager[object]:
    def run(lease: EnvironmentLease, command: OracleCommand) -> OracleRunResult:
        actions.append(command.action)
        return response

    return patch.object(oracle, "run", side_effect=run)


class CodexCompensationOracleAdapterTests(unittest.TestCase):
    def test_a1_factory_and_port_admit_exactly_five_operations(self) -> None:
        allocator, lease, oracle = _ready("000000000000a301")
        try:
            adapter = _adapter(lease, oracle)
            admitted = admit_codex_compensation_port(adapter)
            self.assertIs(type(admitted), CodexCompensationPortCapability)
            if type(admitted) is not CodexCompensationPortCapability:
                raise AssertionError("expected five-operation capability")
            self.assertEqual(5, admitted.metadata().operation_count)
        finally:
            _teardown(allocator, lease)

    def test_a1_invalid_factory_inputs_reject_without_oracle_effect(self) -> None:
        allocator, lease, oracle = _ready("000000000000a302")
        try:
            with patch(
                "tests.staging.codex_lifecycle_oracle.compensation_adapter.ntpath.expandvars",
                return_value=FIXED_STAGING_LOGICAL_ROOT,
            ):
                invalid_lease = EnvironmentLease.model_construct(owner=lease.owner)
                result = create_oracle_compensation_adapter(invalid_lease, oracle, request())
                self.assertIs(type(result), CodexCompensationOracleAdapterRejected)
                if type(result) is not CodexCompensationOracleAdapterRejected:
                    raise AssertionError("invalid lease must reject")
                self.assertIs(result.reason, CodexCompensationOracleAdapterRejectReason.INVALID_LEASE)
                result = create_oracle_compensation_adapter(lease, object(), request())
                self.assertIs(type(result), CodexCompensationOracleAdapterRejected)
                if type(result) is not CodexCompensationOracleAdapterRejected:
                    raise AssertionError("invalid oracle must reject")
                self.assertIs(result.reason, CodexCompensationOracleAdapterRejectReason.INVALID_ORACLE)
                result = create_oracle_compensation_adapter(lease, oracle, None)
                self.assertIs(type(result), CodexCompensationOracleAdapterRejected)
                if type(result) is not CodexCompensationOracleAdapterRejected:
                    raise AssertionError("invalid request must reject")
                self.assertIs(result.reason, CodexCompensationOracleAdapterRejectReason.INVALID_REQUEST)
        finally:
            _teardown(allocator, lease)

    def test_a2_invalid_and_foreign_requests_fail_before_effect(self) -> None:
        allocator, lease, oracle = _ready("000000000000a303")
        try:
            adapter = _adapter(lease, oracle)
            admitted = admit_codex_compensation_port(adapter)
            if type(admitted) is not CodexCompensationPortCapability:
                raise AssertionError("expected admitted adapter")
            subclass_type = type("RequestSubclass", (CodexCompensationPortRequest,), {})
            foreign = request().model_copy(
                update={"manifest": manifest().model_copy(update={"plugin": CodexPluginName(value="foreign-plugin")})}
            )
            injected = request()
            object.__getattribute__(injected, "__dict__")["injected"] = "forbidden"
            invalid_values: tuple[object, ...] = (
                None,
                "request",
                (),
                [],
                {},
                subclass_type(manifest=manifest()),
                CodexCompensationPortRequest.model_construct(),
                foreign,
                injected,
            )
            actions: list[OracleAction] = []
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_REMOVE, _plugin_remove_payload()), actions):
                for supplied in invalid_values:
                    result = admitted.remove_plugin(cast(CodexCompensationPortRequest, supplied))
                    failed = _failure(
                        result,
                        CodexCompensationPortOperation.REMOVE_PLUGIN,
                        CodexCompensationPortFailureReason.REQUEST_INVALID,
                    )
                    self.assertEqual(request().manifest.model_dump(), failed.manifest.model_dump())
            self.assertEqual([], actions)
        finally:
            _teardown(allocator, lease)

    def test_a3_plugin_remove_uses_one_action_and_exact_identity(self) -> None:
        allocator, lease, oracle = _ready("000000000000a304")
        try:
            adapter = _adapter(lease, oracle)
            actions: list[OracleAction] = []
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_REMOVE, _plugin_remove_payload()), actions):
                result = adapter.remove_plugin(request())
            self.assertIs(type(result), CodexPluginRemovalProof)
            if type(result) is not CodexPluginRemovalProof:
                raise AssertionError("expected plugin removal proof")
            self.assertIsNot(result.manifest, request().manifest)
            self.assertEqual([OracleAction.PLUGIN_REMOVE], actions)

            wrong = CodexPluginRemove(pluginId="foreign-plugin", name=PLUGIN.value, marketplaceName=MARKETPLACE.value)
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_REMOVE, wrong), actions):
                _failure(
                    adapter.remove_plugin(request()),
                    CodexCompensationPortOperation.REMOVE_PLUGIN,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
            with _run_with(oracle, OracleBlocked(reason=OracleBlockReason.STATE_INVALID), actions):
                _failure(
                    adapter.remove_plugin(request()),
                    CodexCompensationPortOperation.REMOVE_PLUGIN,
                    CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
                )
        finally:
            _teardown(allocator, lease)

    def test_a4_marketplace_remove_uses_one_action_and_exact_identity(self) -> None:
        allocator, lease, oracle = _ready("000000000000a305")
        try:
            adapter = _adapter(lease, oracle)
            actions: list[OracleAction] = []
            with _run_with(oracle, _response(CodexProtocolSurface.MARKETPLACE_REMOVE, _marketplace_remove_payload()), actions):
                result = adapter.remove_marketplace(request())
            self.assertIs(type(result), CodexMarketplaceRemovalProof)
            if type(result) is not CodexMarketplaceRemovalProof:
                raise AssertionError("expected marketplace removal proof")
            self.assertEqual([OracleAction.MARKETPLACE_REMOVE], actions)

            wrong = CodexMarketplaceRemove(marketplaceName=MARKETPLACE.value, installedRoot=r"C:\Foreign\wrong")
            with _run_with(oracle, _response(CodexProtocolSurface.MARKETPLACE_REMOVE, wrong), actions):
                _failure(
                    adapter.remove_marketplace(request()),
                    CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
        finally:
            _teardown(allocator, lease)

    def test_a5_lists_return_rebuilt_data_without_filtering_foreign_entries(self) -> None:
        allocator, lease, oracle = _ready("000000000000a306")
        try:
            adapter = _adapter(lease, oracle)
            plugin_payload = CodexPluginList(
                installed=(_plugin_entry(PLUGIN.value, PLUGIN_ID.value), _plugin_entry("foreign-name", "foreign-plugin")),
                available=(),
            )
            marketplace_payload = CodexMarketplaceList(
                marketplaces=(_marketplace_entry(MARKETPLACE.value), _marketplace_entry("foreign-market")),
            )
            actions: list[OracleAction] = []
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_LIST, plugin_payload), actions):
                plugins = adapter.list_plugins(request())
            self.assertIs(type(plugins), CodexPluginList)
            if type(plugins) is not CodexPluginList:
                raise AssertionError("expected plugin list")
            self.assertEqual(plugin_payload.model_dump(), plugins.model_dump())
            self.assertIsNot(plugin_payload, plugins)
            self.assertEqual(2, len(plugins.installed))

            with _run_with(oracle, _response(CodexProtocolSurface.MARKETPLACE_LIST, marketplace_payload), actions):
                marketplaces = adapter.list_marketplaces(request())
            self.assertIs(type(marketplaces), CodexMarketplaceList)
            if type(marketplaces) is not CodexMarketplaceList:
                raise AssertionError("expected marketplace list")
            self.assertEqual(marketplace_payload.model_dump(), marketplaces.model_dump())
            self.assertEqual(2, len(marketplaces.marketplaces))
            self.assertEqual([OracleAction.PLUGIN_LIST, OracleAction.MARKETPLACE_LIST], actions)

            malformed = OracleCompleted(
                response=CodexProtocolAccepted.model_construct(
                    surface=CodexProtocolSurface.PLUGIN_LIST,
                    payload=CodexPluginList.model_construct(installed=("malformed",), available=()),
                )
            )
            with _run_with(oracle, malformed, actions):
                _failure(
                    adapter.list_plugins(request()),
                    CodexCompensationPortOperation.LIST_PLUGINS,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
        finally:
            _teardown(allocator, lease)

    def test_a6_absence_proof_requires_exact_admitted_oracle_absent(self) -> None:
        allocator, lease, oracle = _ready("000000000000a307")
        try:
            adapter = _adapter(lease, oracle)
            actions: list[OracleAction] = []
            with _run_with(oracle, OracleAbsent(), actions):
                result = adapter.prove_installed_path_absent(request())
            self.assertIs(type(result), CodexInstalledPathAbsenceProof)
            if type(result) is not CodexInstalledPathAbsenceProof:
                raise AssertionError("expected absence proof")
            self.assertTrue(result.absent)
            self.assertEqual([OracleAction.ABSENCE], actions)

            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_LIST, CodexPluginList(installed=(), available=())), actions):
                _failure(
                    adapter.prove_installed_path_absent(request()),
                    CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
            with _run_with(oracle, OracleBlocked(reason=OracleBlockReason.ABSENCE_NOT_PROVEN), actions):
                _failure(
                    adapter.prove_installed_path_absent(request()),
                    CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                    CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
                )
        finally:
            _teardown(allocator, lease)

    def test_a8_reverse_request_before_effect(self) -> None:
        allocator, lease, oracle = _ready("000000000000a308")
        try:
            adapter = _adapter(lease, oracle)
            actions: list[OracleAction] = []
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_REMOVE, _plugin_remove_payload()), actions):
                _failure(
                    adapter.remove_plugin(cast(CodexCompensationPortRequest, None)),
                    CodexCompensationPortOperation.REMOVE_PLUGIN,
                    CodexCompensationPortFailureReason.REQUEST_INVALID,
                )
            self.assertEqual([], actions)
        finally:
            _teardown(allocator, lease)

    def test_a8_reverse_action_binding(self) -> None:
        allocator, lease, oracle = _ready("000000000000a309")
        try:
            adapter = _adapter(lease, oracle)
            actions: list[OracleAction] = []
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_REMOVE, _plugin_remove_payload()), actions):
                result = adapter.remove_plugin(request())
            self.assertIs(type(result), CodexPluginRemovalProof)
            self.assertEqual([OracleAction.PLUGIN_REMOVE], actions)
        finally:
            _teardown(allocator, lease)

    def test_a8_reverse_removal_identity(self) -> None:
        allocator, lease, oracle = _ready("000000000000a30a")
        try:
            adapter = _adapter(lease, oracle)
            wrong = CodexPluginRemove(pluginId="foreign-plugin", name=PLUGIN.value, marketplaceName=MARKETPLACE.value)
            with _run_with(oracle, _response(CodexProtocolSurface.PLUGIN_REMOVE, wrong), []):
                _failure(
                    adapter.remove_plugin(request()),
                    CodexCompensationPortOperation.REMOVE_PLUGIN,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
        finally:
            _teardown(allocator, lease)

    def test_a8_reverse_response_admission(self) -> None:
        allocator, lease, oracle = _ready("000000000000a30b")
        try:
            adapter = _adapter(lease, oracle)
            forged = CodexProtocolAccepted.model_construct(
                surface=CodexProtocolSurface.PLUGIN_REMOVE,
                payload=_plugin_remove_payload(),
            )
            object.__getattribute__(forged, "__dict__")["injected"] = "forbidden"
            with _run_with(oracle, OracleCompleted(response=forged), []):
                _failure(
                    adapter.remove_plugin(request()),
                    CodexCompensationPortOperation.REMOVE_PLUGIN,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
        finally:
            _teardown(allocator, lease)

    def test_a8_reverse_absence_gate(self) -> None:
        allocator, lease, oracle = _ready("000000000000a30c")
        try:
            adapter = _adapter(lease, oracle)
            admitted_non_absence = CodexProtocolAccepted.model_construct(
                surface=CodexProtocolSurface.PLUGIN_LIST,
                payload=CodexPluginList(installed=(), available=()),
            )
            with patch.object(CodexCompensationOracleAdapter, "_run", return_value=admitted_non_absence):
                _failure(
                    adapter.prove_installed_path_absent(request()),
                    CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                    CodexCompensationPortFailureReason.EVIDENCE_INVALID,
                )
        finally:
            _teardown(allocator, lease)

    def test_a7_exact_oracle_substitution_drives_five_in_memory_operations(self) -> None:
        owner, lease, oracle = _ready("000000000000a30d")
        try:
            adapter = _adapter(lease, oracle)
            plugin_payload = CodexPluginList(
                installed=(_plugin_entry(PLUGIN.value, PLUGIN_ID.value), _plugin_entry("foreign-name", "foreign-plugin")),
                available=(),
            )
            marketplace_payload = CodexMarketplaceList(
                marketplaces=(_marketplace_entry(MARKETPLACE.value), _marketplace_entry("foreign-market")),
            )
            actions: list[OracleAction] = []

            def deterministic_run(current_lease: EnvironmentLease, command: OracleCommand) -> OracleRunResult:
                self.assertEqual(current_lease, lease)
                actions.append(command.action)
                if command.action is OracleAction.PLUGIN_LIST:
                    return _response(CodexProtocolSurface.PLUGIN_LIST, plugin_payload)
                if command.action is OracleAction.MARKETPLACE_LIST:
                    return _response(CodexProtocolSurface.MARKETPLACE_LIST, marketplace_payload)
                if command.action is OracleAction.PLUGIN_REMOVE:
                    return _response(CodexProtocolSurface.PLUGIN_REMOVE, _plugin_remove_payload())
                if command.action is OracleAction.MARKETPLACE_REMOVE:
                    return _response(CodexProtocolSurface.MARKETPLACE_REMOVE, _marketplace_remove_payload())
                if command.action is OracleAction.ABSENCE:
                    return OracleAbsent()
                raise AssertionError("unexpected oracle action")

            with patch.object(CodexLifecycleOracle, "run", side_effect=deterministic_run):
                plugins = adapter.list_plugins(request())
                marketplaces = adapter.list_marketplaces(request())
                removed_plugin = adapter.remove_plugin(request())
                removed_marketplace = adapter.remove_marketplace(request())
                absence = adapter.prove_installed_path_absent(request())

            self.assertEqual(
                [
                    OracleAction.PLUGIN_LIST,
                    OracleAction.MARKETPLACE_LIST,
                    OracleAction.PLUGIN_REMOVE,
                    OracleAction.MARKETPLACE_REMOVE,
                    OracleAction.ABSENCE,
                ],
                actions,
            )
            self.assertIs(type(plugins), CodexPluginList)
            self.assertIs(type(marketplaces), CodexMarketplaceList)
            if type(plugins) is not CodexPluginList or type(marketplaces) is not CodexMarketplaceList:
                raise AssertionError("expected rebuilt list payloads")
            self.assertEqual(2, len(plugins.installed))
            self.assertEqual(2, len(marketplaces.marketplaces))
            self.assertEqual("foreign-plugin", plugins.installed[1].pluginId)
            self.assertEqual("foreign-market", marketplaces.marketplaces[1].name)
            self.assertIs(type(removed_plugin), CodexPluginRemovalProof)
            self.assertIs(type(removed_marketplace), CodexMarketplaceRemovalProof)
            self.assertIs(type(absence), CodexInstalledPathAbsenceProof)
        finally:
            _teardown(owner, lease)


if __name__ == "__main__":
    unittest.main()
