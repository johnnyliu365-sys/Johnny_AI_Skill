"""C1-C8 closure for exact Codex compensation composition."""

from __future__ import annotations

from enum import Enum
from typing import NoReturn, cast
import unittest

from pydantic import BaseModel

from library.local_orchestration import (
    CodexCompensationObservationRejectReason,
    CodexCompensationObservationRejected,
    CodexCompensationObservationResult,
    compose_codex_compensation as exported_compose,
    observe_codex_compensation_operation as exported_observe,
)
from library.local_orchestration.codex_compensation_composition import (
    CodexCompensationObservationRejectReason as CompositionRejectReason,
    CodexCompensationObservationRejected as CompositionRejected,
    CodexCompensationObservationResult as CompositionObservationResult,
    compose_codex_compensation,
    observe_codex_compensation_operation,
)
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
from library.local_orchestration.codex_compensation_reducer import (
    CodexCompensated,
    CodexCompensationBlocked,
    CodexCompensationBlockReason,
    CodexCompensationFailed,
    CodexCompensationNoop,
    CodexCompensationStep,
    CodexInstalledLocationProof,
    CodexMarketplaceProof,
    CodexPluginListsProof,
    CodexCompensationPlan,
    CodexCompensationReason,
    CodexCompensationResult,
    CodexNoCompensationPlan,
    build_compensation_plan,
    CodexProofTruth,
    CodexRemovalConfirmed,
    CodexRemovalFailed,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAttemptEffectState,
    CodexAuthPolicy,
    CodexPluginId,
    CodexRegistrationAttemptId,
    CodexRegistrationAttemptJournal,
)
from library.local_orchestration.contracts import (
    CANONICAL_INSTALL_ROOT,
    ArtifactDigest,
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
    CodexPreflightRequest,
)


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="probe-market")
PLUGIN = CodexPluginName(value="probe-plugin")
PLUGIN_ID = CodexPluginId(value="plugin-probe-012345")
VERSION = CodexCliVersion(value="1.2.3")
SOURCE = OwnedRelativePath(value="marketplaces/probe-market")
INSTALLED = OwnedRelativePath(value="plugins/probe-plugin")
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")
DIGEST = ArtifactDigest(value="a" * 64)
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")


class OperationName(str, Enum):
    NONE = "none"
    REMOVE_PLUGIN = "remove_plugin"
    REMOVE_MARKETPLACE = "remove_marketplace"
    LIST_PLUGINS = "list_plugins"
    LIST_MARKETPLACES = "list_marketplaces"
    PROVE_INSTALLED_PATH_ABSENT = "prove_installed_path_absent"


class OperationFailure(str, Enum):
    RUNTIME_ERROR = "RuntimeError"
    MEMORY_ERROR = "MemoryError"
    KEYBOARD_INTERRUPT = "KeyboardInterrupt"
    SYSTEM_EXIT = "SystemExit"


class ManifestField(str, Enum):
    INSTALLATION_ID = "installation_id"
    ROOT = "root"
    MARKETPLACE = "marketplace"
    MARKETPLACE_SOURCE = "marketplace_source"
    PLUGIN_ID = "plugin_id"
    PLUGIN = "plugin"
    VERSION = "version"
    INSTALLED_LOCATOR = "installed_locator"
    AUTH_POLICY = "auth_policy"
    DIGEST = "digest"


class ManifestSeam(str, Enum):
    REQUEST = "request"
    PLUGIN_REMOVAL = "plugin_removal"
    MARKETPLACE_REMOVAL = "marketplace_removal"
    INSTALLED_PATH = "installed_path"


class FailureStateNode(str, Enum):
    FAILURE = "failure"
    MANIFEST = "manifest"
    INSTALLATION_ID = "installation_id"
    ROOT = "root"
    MARKETPLACE = "marketplace"
    MARKETPLACE_SOURCE = "marketplace_source"
    PLUGIN_ID = "plugin_id"
    PLUGIN = "plugin"
    VERSION = "version"
    INSTALLED_LOCATOR = "installed_locator"
    AUTH_POLICY = "auth_policy"
    DIGEST = "digest"


FAILURE_STATE_INJECTION_TABLE: tuple[FailureStateNode, ...] = (
    FailureStateNode.FAILURE,
    FailureStateNode.MANIFEST,
    FailureStateNode.INSTALLATION_ID,
    FailureStateNode.ROOT,
    FailureStateNode.MARKETPLACE,
    FailureStateNode.MARKETPLACE_SOURCE,
    FailureStateNode.PLUGIN_ID,
    FailureStateNode.PLUGIN,
    FailureStateNode.VERSION,
    FailureStateNode.INSTALLED_LOCATOR,
    FailureStateNode.AUTH_POLICY,
    FailureStateNode.DIGEST,
)


class MissingManifestValue:
    pass


class PlainManifestTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("manifest trap invoked")

    def __eq__(self, other: object) -> bool:
        self._raise()

    def __hash__(self) -> int:
        self._raise()

    def __str__(self) -> str:
        self._raise()

    def __repr__(self) -> str:
        self._raise()

    def __format__(self, format_spec: str) -> str:
        self._raise()


MISSING_MANIFEST_VALUE = MissingManifestValue()
FULL_ORDER = (
    OperationName.REMOVE_PLUGIN,
    OperationName.REMOVE_MARKETPLACE,
    OperationName.LIST_PLUGINS,
    OperationName.LIST_MARKETPLACES,
    OperationName.PROVE_INSTALLED_PATH_ABSENT,
)


def preflight_request() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )


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


def request_from_manifest(current_manifest: CodexCompensationPortManifest) -> CodexCompensationPortRequest:
    return CodexCompensationPortRequest(manifest=current_manifest)


def request() -> CodexCompensationPortRequest:
    return request_from_manifest(manifest())


def plan(
    marketplace_state: CodexAttemptEffectState,
    plugin_state: CodexAttemptEffectState,
) -> CodexCompensationPlan | CodexNoCompensationPlan:
    current_request = preflight_request()
    current_journal = CodexRegistrationAttemptJournal(
        request=current_request,
        attempt_id=ATTEMPT,
        marketplace_state=marketplace_state,
        plugin_state=plugin_state,
    )
    result = build_compensation_plan(current_journal, current_request, ATTEMPT)
    if isinstance(result, CodexCompensationBlocked):
        raise AssertionError(f"expected plan, received {result}")
    return result


def foreign_manifest() -> CodexCompensationPortManifest:
    return CodexCompensationPortManifest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        marketplace_source=SOURCE,
        plugin_id=CodexPluginId(value="plugin-foreign-012345"),
        plugin=PLUGIN,
        version=VERSION,
        installed_locator=INSTALLED,
        auth_policy=AUTH_POLICY,
        digest=DIGEST,
    )


def plugin_entry(
    plugin_id: str = PLUGIN_ID.value,
    name: str = PLUGIN.value,
    marketplace_name: str = MARKETPLACE.value,
    version: str = VERSION.value,
    auth_policy: str = AUTH_POLICY.value,
) -> CodexPluginEntry:
    return CodexPluginEntry(
        pluginId=plugin_id,
        name=name,
        marketplaceName=marketplace_name,
        version=version,
        installed=True,
        enabled=True,
        source=INSTALLED.value,
        installPolicy="local",
        authPolicy=auth_policy,
        marketplaceSource=CodexMarketplaceSource(type="directory", value=SOURCE.value),
    )


def marketplace_entry(source_value: str = SOURCE.value) -> CodexMarketplaceEntry:
    return CodexMarketplaceEntry(
        name=MARKETPLACE.value,
        root="C:\\disposable\\marketplace",
        marketplaceSource=CodexMarketplaceSource(type="directory", value=source_value),
    )


def malformed_manifest(
    field: ManifestField,
    value: object,
) -> CodexCompensationPortManifest:
    values: dict[str, object] = {
        "installation_id": INSTALLATION,
        "root": ROOT,
        "marketplace": MARKETPLACE,
        "marketplace_source": SOURCE,
        "plugin_id": PLUGIN_ID,
        "plugin": PLUGIN,
        "version": VERSION,
        "installed_locator": INSTALLED,
        "auth_policy": AUTH_POLICY,
        "digest": DIGEST,
    }
    if value is MISSING_MANIFEST_VALUE:
        del values[field.value]
    else:
        values[field.value] = value
    return CodexCompensationPortManifest.model_construct(_fields_set=set(values), **values)


class RecordingPort:
    def __init__(self) -> None:
        current_manifest = manifest()
        self.calls: list[OperationName] = []
        self.requests: list[CodexCompensationPortRequest] = []
        self.failure_operation = OperationName.NONE
        self.failure = OperationFailure.RUNTIME_ERROR
        self.plugin_removal_result: object = CodexPluginRemovalProof(
            manifest=current_manifest,
            status="REMOVED",
        )
        self.marketplace_removal_result: object = CodexMarketplaceRemovalProof(
            manifest=current_manifest,
            status="REMOVED",
        )
        self.plugin_list_result: object = CodexPluginList(installed=(), available=())
        self.marketplace_list_result: object = CodexMarketplaceList(marketplaces=())
        self.path_result: object = CodexInstalledPathAbsenceProof(
            manifest=current_manifest,
            absent=True,
        )

    def _record(self, operation: OperationName, current: CodexCompensationPortRequest) -> None:
        self.calls.append(operation)
        self.requests.append(current)
        if operation is self.failure_operation:
            self._raise_failure()

    def _raise_failure(self) -> NoReturn:
        if self.failure is OperationFailure.RUNTIME_ERROR:
            raise RuntimeError("operation failed")
        if self.failure is OperationFailure.MEMORY_ERROR:
            raise MemoryError()
        if self.failure is OperationFailure.KEYBOARD_INTERRUPT:
            raise KeyboardInterrupt()
        raise SystemExit()

    def remove_plugin(self, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
        self._record(OperationName.REMOVE_PLUGIN, current)
        return cast(CodexPluginRemovalProof, self.plugin_removal_result)

    def remove_marketplace(self, current: CodexCompensationPortRequest) -> CodexMarketplaceRemovalProof:
        self._record(OperationName.REMOVE_MARKETPLACE, current)
        return cast(CodexMarketplaceRemovalProof, self.marketplace_removal_result)

    def list_plugins(self, current: CodexCompensationPortRequest) -> CodexPluginList:
        self._record(OperationName.LIST_PLUGINS, current)
        return cast(CodexPluginList, self.plugin_list_result)

    def list_marketplaces(self, current: CodexCompensationPortRequest) -> CodexMarketplaceList:
        self._record(OperationName.LIST_MARKETPLACES, current)
        return cast(CodexMarketplaceList, self.marketplace_list_result)

    def prove_installed_path_absent(
        self,
        current: CodexCompensationPortRequest,
    ) -> CodexInstalledPathAbsenceProof:
        self._record(OperationName.PROVE_INSTALLED_PATH_ABSENT, current)
        return cast(CodexInstalledPathAbsenceProof, self.path_result)


def finite_failure(
    current_manifest: CodexCompensationPortManifest,
    operation: CodexCompensationPortOperation,
) -> CodexCompensationPortOperationFailed:
    return CodexCompensationPortOperationFailed(
        manifest=current_manifest,
        operation=operation,
        status="FAILED",
        reason=CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
    )


class FailureSubclass(CodexCompensationPortOperationFailed):
    """Caller-controlled derived failure values cannot enter composition."""


class OperationText(str):
    """String subclasses are not exact operation enum values."""


class ModelStorageCorruption(str, Enum):
    EXTRA = "extra"
    PRIVATE = "private"


class NestedResponseTarget(str, Enum):
    PLUGIN_ENTRY = "plugin_entry"
    MARKETPLACE_ENTRY = "marketplace_entry"
    MARKETPLACE_SOURCE = "marketplace_source"


def corrupt_model_storage(value: BaseModel, corruption: ModelStorageCorruption) -> BaseModel:
    if corruption is ModelStorageCorruption.EXTRA:
        object.__setattr__(value, "__pydantic_extra__", {"foreign": "state"})
    else:
        object.__setattr__(value, "__pydantic_private__", {"foreign": "state"})
    return value


def corrupted_nested_response(
    target: NestedResponseTarget,
    corruption: ModelStorageCorruption,
) -> CodexPluginList | CodexMarketplaceList:
    if target is NestedResponseTarget.PLUGIN_ENTRY:
        entry = plugin_entry()
        corrupt_model_storage(entry, corruption)
        return CodexPluginList(installed=(entry,), available=())
    marketplace = marketplace_entry()
    if target is NestedResponseTarget.MARKETPLACE_SOURCE:
        source: object = marketplace.marketplaceSource
        if not isinstance(source, CodexMarketplaceSource):
            raise AssertionError("expected marketplace source")
        corrupt_model_storage(source, corruption)
    else:
        corrupt_model_storage(marketplace, corruption)
    return CodexMarketplaceList(marketplaces=(marketplace,))


class RequestSubclass(CodexCompensationPortRequest):
    """Caller-controlled request subclasses cannot enter observation admission."""


def failure_state_node(
    failure: CodexCompensationPortOperationFailed,
    node: FailureStateNode,
) -> BaseModel:
    """Select one fixed failure/manifest node without dynamic member lookup."""

    current_manifest = failure.manifest
    if node is FailureStateNode.FAILURE:
        return failure
    if node is FailureStateNode.MANIFEST:
        return current_manifest
    if node is FailureStateNode.INSTALLATION_ID:
        return current_manifest.installation_id
    if node is FailureStateNode.ROOT:
        return current_manifest.root
    if node is FailureStateNode.MARKETPLACE:
        return current_manifest.marketplace
    if node is FailureStateNode.MARKETPLACE_SOURCE:
        return current_manifest.marketplace_source
    if node is FailureStateNode.PLUGIN_ID:
        return current_manifest.plugin_id
    if node is FailureStateNode.PLUGIN:
        return current_manifest.plugin
    if node is FailureStateNode.VERSION:
        return current_manifest.version
    if node is FailureStateNode.INSTALLED_LOCATOR:
        return current_manifest.installed_locator
    if node is FailureStateNode.AUTH_POLICY:
        return current_manifest.auth_policy
    if node is FailureStateNode.DIGEST:
        return current_manifest.digest
    raise AssertionError("unknown failure state node")


def capability(adapter: RecordingPort) -> CodexCompensationPortCapability:
    admitted = admit_codex_compensation_port(adapter)
    if not isinstance(admitted, CodexCompensationPortCapability):
        raise AssertionError(f"expected admitted port, received {admitted}")
    return admitted


class CodexCompensationCompositionTests(unittest.TestCase):
    def test_cr174_corrupted_original_response_state_maps_to_finite_nonaffirmative_results(self) -> None:
        top_level_cases: tuple[tuple[CodexCompensationPortOperation, BaseModel, object], ...] = (
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexPluginRemovalProof(manifest=manifest(), status="REMOVED"),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexMarketplaceRemovalProof(manifest=manifest(), status="REMOVED"),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexPluginList(installed=(), available=()),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.MALFORMED,
                    available=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexMarketplaceList(marketplaces=()),
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                CodexInstalledPathAbsenceProof(manifest=manifest(), absent=True),
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
        )
        for corruption in ModelStorageCorruption:
            for operation, value, expected in top_level_cases:
                with self.subTest(corruption=corruption.value, operation=operation.value):
                    current = value.model_copy(deep=True)
                    corrupt_model_storage(current, corruption)
                    result = observe_codex_compensation_operation(operation, current, request())
                    self.assertEqual(expected, result)

        nested_cases: tuple[
            tuple[NestedResponseTarget, CodexCompensationPortOperation, object],
            ...,
        ] = (
            (
                NestedResponseTarget.PLUGIN_ENTRY,
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.MALFORMED,
                    available=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                NestedResponseTarget.MARKETPLACE_ENTRY,
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                NestedResponseTarget.MARKETPLACE_SOURCE,
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
        )
        for corruption in ModelStorageCorruption:
            for target, operation, expected in nested_cases:
                with self.subTest(corruption=corruption.value, target=target.value):
                    value = corrupted_nested_response(target, corruption)
                    result = observe_codex_compensation_operation(operation, value, request())
                    self.assertEqual(expected, result)

    def test_a1_public_observation_contract_and_all_five_successes(self) -> None:
        self.assertIs(exported_observe, observe_codex_compensation_operation)
        self.assertIs(CodexCompensationObservationRejectReason, CompositionRejectReason)
        self.assertIs(CodexCompensationObservationRejected, CompositionRejected)
        self.assertIs(CodexCompensationObservationResult, CompositionObservationResult)
        self.assertEqual(
            ("INVALID_OPERATION", "INVALID_REQUEST"),
            tuple(reason.value for reason in CodexCompensationObservationRejectReason),
        )
        current_request = request()
        success_values: tuple[tuple[CodexCompensationPortOperation, object, object], ...] = (
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexPluginRemovalProof(manifest=manifest(), status="REMOVED"),
                CodexRemovalConfirmed(step=CodexCompensationStep.REMOVE_PLUGIN, status="CONFIRMED"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexMarketplaceRemovalProof(manifest=manifest(), status="REMOVED"),
                CodexRemovalConfirmed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="CONFIRMED"),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexPluginList(installed=(), available=()),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.PROVED_ABSENT,
                    available=CodexProofTruth.PROVED_ABSENT,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexMarketplaceList(marketplaces=()),
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.PROVED_ABSENT,
                ),
            ),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                CodexInstalledPathAbsenceProof(manifest=manifest(), absent=True),
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.PROVED_ABSENT,
                ),
            ),
        )
        for operation, value, expected in success_values:
            with self.subTest(operation=operation.value):
                result = observe_codex_compensation_operation(operation, value, current_request)
                self.assertEqual(expected, result)

    def test_a2_each_operation_maps_failure_foreign_and_malformed_values(self) -> None:
        cases: tuple[tuple[CodexCompensationPortOperation, object, object], ...] = (
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                finite_failure(manifest(), CodexCompensationPortOperation.REMOVE_PLUGIN),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexPluginRemovalProof(manifest=foreign_manifest(), status="REMOVED"),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                object(),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                finite_failure(manifest(), CodexCompensationPortOperation.REMOVE_MARKETPLACE),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexMarketplaceRemovalProof(manifest=foreign_manifest(), status="REMOVED"),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                object(),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                finite_failure(manifest(), CodexCompensationPortOperation.LIST_PLUGINS),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.UNPROVED,
                    available=CodexProofTruth.UNPROVED,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexPluginList(installed=(plugin_entry(plugin_id="foreign-plugin-012345"),), available=()),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.PROVED_ABSENT,
                    available=CodexProofTruth.PROVED_ABSENT,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                object(),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.MALFORMED,
                    available=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                finite_failure(manifest(), CodexCompensationPortOperation.LIST_MARKETPLACES),
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.UNPROVED,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexMarketplaceList(marketplaces=(marketplace_entry("foreign/source"),)),
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MISMATCH,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                object(),
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                finite_failure(manifest(), CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT),
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.UNPROVED,
                ),
            ),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                CodexInstalledPathAbsenceProof(manifest=foreign_manifest(), absent=True),
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.MISMATCH,
                ),
            ),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                object(),
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
        )
        for operation, value, expected in cases:
            with self.subTest(operation=operation.value, value_type=type(value).__name__):
                self.assertEqual(expected, observe_codex_compensation_operation(operation, value, request()))

    def test_a3_invalid_operation_admission_precedes_all_other_access(self) -> None:
        invalid_operations: tuple[object, ...] = (
            None,
            "REMOVE_PLUGIN",
            OperationName.REMOVE_PLUGIN,
            OperationText("REMOVE_PLUGIN"),
            (),
            [],
            {},
            set(),
        )
        for candidate in invalid_operations:
            with self.subTest(candidate_type=type(candidate).__name__):
                request_trap = PlainManifestTrap()
                response_trap = PlainManifestTrap()
                result = observe_codex_compensation_operation(candidate, response_trap, request_trap)
                if not isinstance(result, CodexCompensationObservationRejected):
                    raise AssertionError(f"expected rejection, received {result}")
                self.assertIs(CodexCompensationObservationRejectReason.INVALID_OPERATION, result.reason)
                self.assertEqual(0, request_trap.invocation_count)
                self.assertEqual(0, response_trap.invocation_count)

        trap = PlainManifestTrap()
        result = observe_codex_compensation_operation(trap, trap, trap)
        if not isinstance(result, CodexCompensationObservationRejected):
            raise AssertionError(f"expected rejection, received {result}")
        self.assertIs(CodexCompensationObservationRejectReason.INVALID_OPERATION, result.reason)
        self.assertEqual(0, trap.invocation_count)

    def test_a4_invalid_request_precedes_response_classification(self) -> None:
        invalid_manifest = malformed_manifest(ManifestField.PLUGIN_ID, MISSING_MANIFEST_VALUE)
        extra_request = request()
        object.__setattr__(extra_request, "__pydantic_extra__", {"foreign": "state"})
        private_request = request()
        object.__setattr__(private_request, "__pydantic_private__", {"foreign": "state"})
        invalid_requests: tuple[object, ...] = (
            None,
            "request",
            (),
            [],
            {},
            set(),
            RequestSubclass.model_construct(manifest=manifest()),
            CodexCompensationPortRequest.model_construct(),
            CodexCompensationPortRequest.model_construct(manifest=invalid_manifest),
            extra_request,
            private_request,
        )
        for invalid_request in invalid_requests:
            with self.subTest(request_type=type(invalid_request).__name__):
                response_trap = PlainManifestTrap()
                result = observe_codex_compensation_operation(
                    CodexCompensationPortOperation.REMOVE_PLUGIN,
                    response_trap,
                    invalid_request,
                )
                if not isinstance(result, CodexCompensationObservationRejected):
                    raise AssertionError(f"expected rejection, received {result}")
                self.assertIs(CodexCompensationObservationRejectReason.INVALID_REQUEST, result.reason)
                self.assertEqual(0, response_trap.invocation_count)

    def test_a5_response_subclasses_constructed_values_and_traps_remain_finite(self) -> None:
        cases: tuple[tuple[CodexCompensationPortOperation, object, object], ...] = (
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                FailureSubclass(
                    manifest=manifest(),
                    operation=CodexCompensationPortOperation.REMOVE_PLUGIN,
                    status="FAILED",
                    reason=CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
                ),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexCompensationPortOperationFailed.model_construct(),
                CodexRemovalFailed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="DECLARED_FAILURE"),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexPluginList.model_construct(),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.MALFORMED,
                    available=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexMarketplaceList.model_construct(),
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                CodexInstalledPathAbsenceProof.model_construct(),
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
            ),
            (
                CodexCompensationPortOperation.LIST_PLUGINS,
                PlainManifestTrap(),
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.MALFORMED,
                    available=CodexProofTruth.MALFORMED,
                ),
            ),
        )
        for operation, value, expected in cases:
            with self.subTest(operation=operation.value, value_type=type(value).__name__):
                self.assertEqual(expected, observe_codex_compensation_operation(operation, value, request()))

    def test_a7_named_dispatch_and_request_precedence_guards_are_observable(self) -> None:
        valid_value = CodexPluginRemovalProof(manifest=manifest(), status="REMOVED")
        valid_request = request()
        self.assertEqual(
            CodexRemovalConfirmed(step=CodexCompensationStep.REMOVE_PLUGIN, status="CONFIRMED"),
            observe_codex_compensation_operation(
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                valid_value,
                valid_request,
            ),
        )
        self.assertEqual(
            CodexPluginListsProof(
                step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                installed=CodexProofTruth.PROVED_ABSENT,
                available=CodexProofTruth.PROVED_ABSENT,
            ),
            observe_codex_compensation_operation(
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexPluginList(installed=(), available=()),
                valid_request,
            ),
        )
        invalid_request = CodexCompensationPortRequest.model_construct()
        response_trap = PlainManifestTrap()
        rejected = observe_codex_compensation_operation(
            CodexCompensationPortOperation.REMOVE_PLUGIN,
            response_trap,
            invalid_request,
        )
        if not isinstance(rejected, CodexCompensationObservationRejected):
            raise AssertionError(f"expected rejection, received {rejected}")
        self.assertIs(CodexCompensationObservationRejectReason.INVALID_REQUEST, rejected.reason)
        self.assertEqual(0, response_trap.invocation_count)

    def test_c1_exact_admission_and_no_compensation_are_zero_call(self) -> None:
        self.assertIs(exported_compose, compose_codex_compensation)
        required_plan = plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        current_request = request()
        invalid_capabilities: tuple[object, ...] = (
            None,
            "",
            " ",
            [],
            {},
            object.__new__(CodexCompensationPortCapability),
        )
        for invalid_capability in invalid_capabilities:
            with self.subTest(capability=type(invalid_capability).__name__):
                self.assert_plan_invalid(
                    compose_codex_compensation(
                        cast(CodexCompensationPortCapability, invalid_capability),
                        current_request,
                        required_plan,
                    )
                )
        invalid_requests: tuple[object, ...] = (
            None,
            "",
            " ",
            [],
            {},
            CodexCompensationPortRequest.model_construct(),
        )
        for invalid_request in invalid_requests:
            with self.subTest(request=type(invalid_request).__name__):
                adapter = RecordingPort()
                self.assert_plan_invalid(
                    compose_codex_compensation(
                        capability(adapter),
                        cast(CodexCompensationPortRequest, invalid_request),
                        required_plan,
                    )
                )
                self.assertEqual([], adapter.calls)
        invalid_plans: tuple[object, ...] = (
            None,
            "",
            [],
            {},
            CodexCompensationPlan.model_construct(),
        )
        for invalid_plan in invalid_plans:
            with self.subTest(plan=type(invalid_plan).__name__):
                adapter = RecordingPort()
                self.assert_plan_invalid(
                    compose_codex_compensation(
                        capability(adapter),
                        current_request,
                        cast(CodexCompensationPlan, invalid_plan),
                    )
                )
                self.assertEqual([], adapter.calls)
        mismatched_request = request_from_manifest(
            CodexCompensationPortManifest(
                installation_id=INSTALLATION,
                root=ROOT,
                marketplace=CodexMarketplaceName(value="other-market"),
                marketplace_source=OwnedRelativePath(value="marketplaces/other-market"),
                plugin_id=PLUGIN_ID,
                plugin=PLUGIN,
                version=VERSION,
                installed_locator=INSTALLED,
                auth_policy=AUTH_POLICY,
                digest=DIGEST,
            )
        )
        mismatch_adapter = RecordingPort()
        self.assert_plan_invalid(
            compose_codex_compensation(capability(mismatch_adapter), mismatched_request, required_plan)
        )
        self.assertEqual([], mismatch_adapter.calls)
        stale_plan = CodexCompensationPlan.model_construct(
            journal=required_plan.journal,
            request=required_plan.request,
            attempt_id=required_plan.attempt_id,
            identity=required_plan.identity,
            status="COMPENSATION_REQUIRED",
            steps=tuple(reversed(required_plan.steps)),
        )
        stale_adapter = RecordingPort()
        self.assert_plan_invalid(
            compose_codex_compensation(capability(stale_adapter), current_request, stale_plan)
        )
        self.assertEqual([], stale_adapter.calls)
        no_plan = plan(
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )
        no_adapter = RecordingPort()
        result = compose_codex_compensation(capability(no_adapter), current_request, no_plan)
        self.assertIsInstance(result, CodexCompensationNoop)
        self.assertEqual([], no_adapter.calls)

    def test_q5_composition_consumes_public_request_revalidation_before_any_operation(self) -> None:
        current_request = request()
        object.__getattribute__(current_request, "__dict__")["injected"] = "state"
        adapter = RecordingPort()
        self.assert_plan_invalid(
            compose_codex_compensation(
                capability(adapter),
                current_request,
                plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
            )
        )
        self.assertEqual([], adapter.calls)

    def test_c2_exact_step_dispatch_order_mapping_and_same_request_identity(self) -> None:
        cases = (
            (
                CodexAttemptEffectState.OWNED,
                CodexAttemptEffectState.OWNED,
                FULL_ORDER,
            ),
            (
                CodexAttemptEffectState.OWNED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
                (
                    OperationName.REMOVE_MARKETPLACE,
                    OperationName.LIST_PLUGINS,
                    OperationName.LIST_MARKETPLACES,
                    OperationName.PROVE_INSTALLED_PATH_ABSENT,
                ),
            ),
        )
        for marketplace_state, plugin_state, expected_calls in cases:
            with self.subTest(marketplace=marketplace_state, plugin=plugin_state):
                adapter = RecordingPort()
                current_request = request()
                result = compose_codex_compensation(
                    capability(adapter),
                    current_request,
                    plan(marketplace_state, plugin_state),
                )
                self.assertIsInstance(result, CodexCompensated)
                self.assertEqual(expected_calls, tuple(adapter.calls))
                self.assertTrue(all(observed is current_request for observed in adapter.requests))

    def test_c3_each_finite_wrong_return_continues_and_reduces_exact_failure(self) -> None:
        cases: tuple[
            tuple[OperationName, tuple[CodexCompensationReason, ...], CodexAttemptEffectState, CodexAttemptEffectState],
            ...,
        ] = (
            (
                OperationName.REMOVE_PLUGIN,
                (CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE,),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
            ),
            (
                OperationName.REMOVE_MARKETPLACE,
                (CodexCompensationReason.MARKETPLACE_REMOVAL_DECLARED_FAILURE,),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
            ),
            (
                OperationName.LIST_PLUGINS,
                (
                    CodexCompensationReason.PLUGIN_INSTALLED_MALFORMED,
                    CodexCompensationReason.PLUGIN_AVAILABLE_MALFORMED,
                ),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.OWNED,
            ),
            (
                OperationName.LIST_MARKETPLACES,
                (CodexCompensationReason.MARKETPLACE_MALFORMED,),
                CodexAttemptEffectState.OWNED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
            ),
            (
                OperationName.PROVE_INSTALLED_PATH_ABSENT,
                (CodexCompensationReason.INSTALLED_LOCATION_MALFORMED,),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.OWNED,
            ),
        )
        for operation, reasons, marketplace_state, plugin_state in cases:
            with self.subTest(operation=operation.value):
                adapter = RecordingPort()
                self.set_operation_result(adapter, operation, object())
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                self.assert_failed(result, reasons, marketplace_state, plugin_state)
                self.assertEqual(FULL_ORDER, tuple(adapter.calls))

    def test_c4_removal_and_all_three_proof_surfaces_map_exact_truth(self) -> None:
        for operation in (OperationName.REMOVE_PLUGIN, OperationName.REMOVE_MARKETPLACE):
            expected_reason = (
                CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE
                if operation is OperationName.REMOVE_PLUGIN
                else CodexCompensationReason.MARKETPLACE_REMOVAL_DECLARED_FAILURE
            )
            wrong_values: tuple[tuple[str, object], ...] = (
                ("wrong_type", object()),
                (
                    "wrong_status",
                    CodexPluginRemovalProof.model_construct(manifest=manifest(), status="FAILED")
                    if operation is OperationName.REMOVE_PLUGIN
                    else CodexMarketplaceRemovalProof.model_construct(manifest=manifest(), status="FAILED"),
                ),
                (
                    "foreign_manifest",
                    CodexPluginRemovalProof(manifest=foreign_manifest(), status="REMOVED")
                    if operation is OperationName.REMOVE_PLUGIN
                    else CodexMarketplaceRemovalProof(manifest=foreign_manifest(), status="REMOVED"),
                ),
            )
            for label, value in wrong_values:
                with self.subTest(operation=operation.value, value=label):
                    adapter = RecordingPort()
                    self.set_operation_result(adapter, operation, value)
                    result = compose_codex_compensation(
                        capability(adapter),
                        request(),
                        plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                    )
                    self.assert_failed(
                        result,
                        (expected_reason,),
                        CodexAttemptEffectState.NOT_ATTEMPTED,
                        CodexAttemptEffectState.NOT_ATTEMPTED,
                    )
        malformed_plugin = CodexPluginEntry.model_construct(
            pluginId=PLUGIN_ID.value,
            name=None,
            marketplaceName=MARKETPLACE.value,
            version=VERSION.value,
            installed=True,
            enabled=True,
            source=INSTALLED.value,
            installPolicy="local",
            authPolicy=AUTH_POLICY.value,
        )
        plugin_cases: tuple[tuple[str, CodexPluginList, tuple[CodexCompensationReason, ...]], ...] = (
            ("absent", CodexPluginList(installed=(), available=()), ()),
            (
                "installed_residue",
                CodexPluginList(installed=(plugin_entry(),), available=()),
                (CodexCompensationReason.PLUGIN_INSTALLED_RESIDUE,),
            ),
            (
                "available_residue",
                CodexPluginList(installed=(), available=(plugin_entry(),)),
                (CodexCompensationReason.PLUGIN_AVAILABLE_RESIDUE,),
            ),
            (
                "installed_mismatch",
                CodexPluginList(installed=(plugin_entry(name="other-plugin"),), available=()),
                (CodexCompensationReason.PLUGIN_INSTALLED_MISMATCH,),
            ),
            (
                "available_mismatch",
                CodexPluginList(installed=(), available=(plugin_entry(version="9.9.9"),)),
                (CodexCompensationReason.PLUGIN_AVAILABLE_MISMATCH,),
            ),
            (
                "malformed",
                CodexPluginList.model_construct(installed=(malformed_plugin,), available=()),
                (
                    CodexCompensationReason.PLUGIN_INSTALLED_MALFORMED,
                    CodexCompensationReason.PLUGIN_AVAILABLE_MALFORMED,
                ),
            ),
        )
        for label, plugin_list, reasons in plugin_cases:
            with self.subTest(plugin_truth=label):
                adapter = RecordingPort()
                adapter.plugin_list_result = plugin_list
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                if not reasons:
                    self.assertIsInstance(result, CodexCompensated)
                else:
                    self.assert_failed(
                        result,
                        reasons,
                        CodexAttemptEffectState.NOT_ATTEMPTED,
                        CodexAttemptEffectState.OWNED,
                    )
        malformed_marketplace = CodexMarketplaceEntry.model_construct(
            name=MARKETPLACE.value,
            root=None,
            marketplaceSource=CodexMarketplaceSource(type="directory", value=SOURCE.value),
        )
        marketplace_cases: tuple[
            tuple[str, CodexMarketplaceList, tuple[CodexCompensationReason, ...]], ...
        ] = (
            ("absent", CodexMarketplaceList(marketplaces=()), ()),
            (
                "residue",
                CodexMarketplaceList(marketplaces=(marketplace_entry(),)),
                (CodexCompensationReason.MARKETPLACE_RESIDUE,),
            ),
            (
                "mismatch",
                CodexMarketplaceList(marketplaces=(marketplace_entry("marketplaces/other"),)),
                (CodexCompensationReason.MARKETPLACE_MISMATCH,),
            ),
            (
                "malformed",
                CodexMarketplaceList.model_construct(marketplaces=(malformed_marketplace,)),
                (CodexCompensationReason.MARKETPLACE_MALFORMED,),
            ),
        )
        for label, marketplace_list, reasons in marketplace_cases:
            with self.subTest(marketplace_truth=label):
                adapter = RecordingPort()
                adapter.marketplace_list_result = marketplace_list
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                if not reasons:
                    self.assertIsInstance(result, CodexCompensated)
                else:
                    self.assert_failed(
                        result,
                        reasons,
                        CodexAttemptEffectState.OWNED,
                        CodexAttemptEffectState.NOT_ATTEMPTED,
                    )
        path_cases: tuple[tuple[str, object, tuple[CodexCompensationReason, ...]], ...] = (
            ("absent", CodexInstalledPathAbsenceProof(manifest=manifest(), absent=True), ()),
            (
                "residue",
                CodexInstalledPathAbsenceProof(manifest=manifest(), absent=False),
                (CodexCompensationReason.INSTALLED_LOCATION_RESIDUE,),
            ),
            (
                "mismatch",
                CodexInstalledPathAbsenceProof(manifest=foreign_manifest(), absent=True),
                (CodexCompensationReason.INSTALLED_LOCATION_MISMATCH,),
            ),
            (
                "malformed",
                CodexInstalledPathAbsenceProof.model_construct(manifest=manifest(), absent="true"),
                (CodexCompensationReason.INSTALLED_LOCATION_MALFORMED,),
            ),
        )
        for label, path_result, reasons in path_cases:
            with self.subTest(path_truth=label):
                adapter = RecordingPort()
                adapter.path_result = path_result
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                if not reasons:
                    self.assertIsInstance(result, CodexCompensated)
                else:
                    self.assert_failed(
                        result,
                        reasons,
                        CodexAttemptEffectState.NOT_ATTEMPTED,
                        CodexAttemptEffectState.OWNED,
                    )

    def test_c5_all_280_recursive_manifest_cells_are_finite_and_trap_free(self) -> None:
        invalid_values: tuple[tuple[str, object], ...] = (
            ("missing", MISSING_MANIFEST_VALUE),
            ("none", None),
            ("empty", ""),
            ("whitespace", " "),
            ("list", []),
            ("dict", {}),
            ("plain_object", PlainManifestTrap()),
        )
        cell_count = 0
        for seam in ManifestSeam:
            for field in ManifestField:
                for label, value in invalid_values:
                    with self.subTest(seam=seam.value, field=field.value, value=label):
                        adapter = RecordingPort()
                        bad_manifest = malformed_manifest(field, value)
                        current_request = request()
                        if seam is ManifestSeam.REQUEST:
                            current_request = CodexCompensationPortRequest.model_construct(manifest=bad_manifest)
                        elif seam is ManifestSeam.PLUGIN_REMOVAL:
                            adapter.plugin_removal_result = CodexPluginRemovalProof.model_construct(
                                manifest=bad_manifest,
                                status="REMOVED",
                            )
                        elif seam is ManifestSeam.MARKETPLACE_REMOVAL:
                            adapter.marketplace_removal_result = CodexMarketplaceRemovalProof.model_construct(
                                manifest=bad_manifest,
                                status="REMOVED",
                            )
                        else:
                            adapter.path_result = CodexInstalledPathAbsenceProof.model_construct(
                                manifest=bad_manifest,
                                absent=True,
                            )
                        result = compose_codex_compensation(
                            capability(adapter),
                            current_request,
                            plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                        )
                        if seam is ManifestSeam.REQUEST:
                            self.assert_plan_invalid(result)
                            self.assertEqual([], adapter.calls)
                        else:
                            self.assertIsInstance(result, CodexCompensationFailed)
                            self.assertEqual(FULL_ORDER, tuple(adapter.calls))
                        if isinstance(value, PlainManifestTrap):
                            self.assertEqual(0, value.invocation_count)
                        cell_count += 1
        self.assertEqual(280, cell_count)

    def test_c6_all_20_operation_exceptions_propagate_and_stop_exactly(self) -> None:
        for operation_index, operation in enumerate(FULL_ORDER):
            for failure in OperationFailure:
                with self.subTest(operation=operation.value, failure=failure.value):
                    adapter = RecordingPort()
                    adapter.failure_operation = operation
                    adapter.failure = failure
                    expected_exception: type[Exception]
                    if failure is OperationFailure.RUNTIME_ERROR:
                        expected_exception = RuntimeError
                    elif failure is OperationFailure.MEMORY_ERROR:
                        expected_exception = MemoryError
                    elif failure is OperationFailure.KEYBOARD_INTERRUPT:
                        with self.assertRaises(KeyboardInterrupt):
                            compose_codex_compensation(
                                capability(adapter),
                                request(),
                                plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                            )
                        self.assertEqual(FULL_ORDER[: operation_index + 1], tuple(adapter.calls))
                        continue
                    else:
                        with self.assertRaises(SystemExit):
                            compose_codex_compensation(
                                capability(adapter),
                                request(),
                                plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                            )
                        self.assertEqual(FULL_ORDER[: operation_index + 1], tuple(adapter.calls))
                        continue
                    with self.assertRaises(expected_exception):
                        compose_codex_compensation(
                            capability(adapter),
                            request(),
                            plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                        )
                    self.assertEqual(FULL_ORDER[: operation_index + 1], tuple(adapter.calls))

    def test_f1_f3_f4_matching_finite_operation_failures_reduce_without_success(self) -> None:
        cases: tuple[
            tuple[
                OperationName,
                CodexCompensationPortOperation,
                tuple[CodexCompensationReason, ...],
                CodexAttemptEffectState,
                CodexAttemptEffectState,
            ],
            ...,
        ] = (
            (
                OperationName.REMOVE_PLUGIN,
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                (CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE,),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
            ),
            (
                OperationName.REMOVE_MARKETPLACE,
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                (CodexCompensationReason.MARKETPLACE_REMOVAL_DECLARED_FAILURE,),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
            ),
            (
                OperationName.LIST_PLUGINS,
                CodexCompensationPortOperation.LIST_PLUGINS,
                (
                    CodexCompensationReason.PLUGIN_INSTALLED_UNPROVED,
                    CodexCompensationReason.PLUGIN_AVAILABLE_UNPROVED,
                ),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.OWNED,
            ),
            (
                OperationName.LIST_MARKETPLACES,
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                (CodexCompensationReason.MARKETPLACE_UNPROVED,),
                CodexAttemptEffectState.OWNED,
                CodexAttemptEffectState.NOT_ATTEMPTED,
            ),
            (
                OperationName.PROVE_INSTALLED_PATH_ABSENT,
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                (CodexCompensationReason.INSTALLED_LOCATION_UNPROVED,),
                CodexAttemptEffectState.NOT_ATTEMPTED,
                CodexAttemptEffectState.OWNED,
            ),
        )
        for operation, failure_operation, reasons, marketplace_state, plugin_state in cases:
            with self.subTest(operation=operation.value):
                adapter = RecordingPort()
                self.set_operation_result(adapter, operation, finite_failure(manifest(), failure_operation))
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                self.assert_failed(
                    result,
                    reasons,
                    marketplace_state,
                    plugin_state,
                )
                self.assertEqual(FULL_ORDER, tuple(adapter.calls))

    def test_f5_finite_failure_wrong_operation_or_manifest_cannot_prove_or_confirm(self) -> None:
        invalid_values: tuple[object, ...] = (
            None,
            "",
            (),
            [],
            {},
            CodexCompensationPortOperationFailed.model_construct(),
            finite_failure(foreign_manifest(), CodexCompensationPortOperation.REMOVE_PLUGIN),
            finite_failure(foreign_manifest(), CodexCompensationPortOperation.LIST_PLUGINS),
            finite_failure(manifest(), CodexCompensationPortOperation.REMOVE_MARKETPLACE),
        )
        for value in invalid_values:
            with self.subTest(value_type=type(value).__name__):
                adapter = RecordingPort()
                adapter.plugin_list_result = value
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                self.assert_failed(
                    result,
                    (
                        CodexCompensationReason.PLUGIN_INSTALLED_MALFORMED,
                        CodexCompensationReason.PLUGIN_AVAILABLE_MALFORMED,
                    ),
                    CodexAttemptEffectState.NOT_ATTEMPTED,
                    CodexAttemptEffectState.OWNED,
                )
                self.assertEqual(FULL_ORDER, tuple(adapter.calls))

    def test_f3_matching_removal_failure_retains_only_authority_not_independently_proved_absent(self) -> None:
        plugin_adapter = RecordingPort()
        plugin_adapter.plugin_removal_result = finite_failure(
            manifest(),
            CodexCompensationPortOperation.REMOVE_PLUGIN,
        )
        plugin_adapter.plugin_list_result = finite_failure(
            manifest(),
            CodexCompensationPortOperation.LIST_PLUGINS,
        )
        plugin_result = compose_codex_compensation(
            capability(plugin_adapter),
            request(),
            plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
        )
        self.assert_failed(
            plugin_result,
            (
                CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE,
                CodexCompensationReason.PLUGIN_INSTALLED_UNPROVED,
                CodexCompensationReason.PLUGIN_AVAILABLE_UNPROVED,
            ),
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.OWNED,
        )
        marketplace_adapter = RecordingPort()
        marketplace_adapter.marketplace_removal_result = finite_failure(
            manifest(),
            CodexCompensationPortOperation.REMOVE_MARKETPLACE,
        )
        marketplace_adapter.marketplace_list_result = finite_failure(
            manifest(),
            CodexCompensationPortOperation.LIST_MARKETPLACES,
        )
        marketplace_result = compose_codex_compensation(
            capability(marketplace_adapter),
            request(),
            plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
        )
        self.assert_failed(
            marketplace_result,
            (
                CodexCompensationReason.MARKETPLACE_REMOVAL_DECLARED_FAILURE,
                CodexCompensationReason.MARKETPLACE_UNPROVED,
            ),
            CodexAttemptEffectState.OWNED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )

    def test_f5_failure_subclass_constructed_and_recursive_injected_state_are_trap_free(self) -> None:
        malformed_values: list[object] = [
            FailureSubclass(
                manifest=manifest(),
                operation=CodexCompensationPortOperation.LIST_PLUGINS,
                status="FAILED",
                reason=CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
            ),
            CodexCompensationPortOperationFailed.model_construct(),
            CodexCompensationPortOperationFailed.model_construct(
                manifest=PlainManifestTrap(),
                operation=CodexCompensationPortOperation.LIST_PLUGINS,
                status="FAILED",
                reason=CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
            ),
        ]
        for node in FAILURE_STATE_INJECTION_TABLE:
            failure = finite_failure(
                manifest().model_copy(deep=True),
                CodexCompensationPortOperation.LIST_PLUGINS,
            )
            object.__setattr__(failure_state_node(failure, node), "untrusted_extra", "untrusted")
            malformed_values.append(failure)
        for value in malformed_values:
            with self.subTest(value_type=type(value).__name__):
                adapter = RecordingPort()
                adapter.plugin_list_result = value
                result = compose_codex_compensation(
                    capability(adapter),
                    request(),
                    plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
                )
                self.assert_failed(
                    result,
                    (
                        CodexCompensationReason.PLUGIN_INSTALLED_MALFORMED,
                        CodexCompensationReason.PLUGIN_AVAILABLE_MALFORMED,
                    ),
                    CodexAttemptEffectState.NOT_ATTEMPTED,
                    CodexAttemptEffectState.OWNED,
                )
                self.assertEqual(FULL_ORDER, tuple(adapter.calls))
        trap = malformed_values[2]
        if type(trap) is not CodexCompensationPortOperationFailed:
            raise AssertionError("expected exact trap envelope")
        trapped_manifest = object.__getattribute__(trap, "manifest")
        if type(trapped_manifest) is not PlainManifestTrap:
            raise AssertionError("expected exact trap manifest")
        self.assertEqual(0, trapped_manifest.invocation_count)

    def set_operation_result(
        self,
        adapter: RecordingPort,
        operation: OperationName,
        value: object,
    ) -> None:
        if operation is OperationName.REMOVE_PLUGIN:
            adapter.plugin_removal_result = value
        elif operation is OperationName.REMOVE_MARKETPLACE:
            adapter.marketplace_removal_result = value
        elif operation is OperationName.LIST_PLUGINS:
            adapter.plugin_list_result = value
        elif operation is OperationName.LIST_MARKETPLACES:
            adapter.marketplace_list_result = value
        else:
            adapter.path_result = value

    def assert_plan_invalid(self, result: CodexCompensationResult) -> None:
        if not isinstance(result, CodexCompensationBlocked):
            raise AssertionError(f"expected blocked result, received {result}")
        self.assertIs(CodexCompensationBlockReason.PLAN_INVALID, result.reason)

    def assert_failed(
        self,
        result: CodexCompensationResult,
        reasons: tuple[CodexCompensationReason, ...],
        marketplace_state: CodexAttemptEffectState,
        plugin_state: CodexAttemptEffectState,
    ) -> None:
        if not isinstance(result, CodexCompensationFailed):
            raise AssertionError(f"expected failed result, received {result}")
        self.assertEqual(reasons, result.reasons)
        self.assertIs(marketplace_state, result.residual_journal.marketplace_state)
        self.assertIs(plugin_state, result.residual_journal.plugin_state)


if __name__ == "__main__":
    unittest.main()
