"""B1-B8 closure for exact receipt-removal composition."""

from __future__ import annotations

import unittest
from typing import NoReturn, cast

from library.local_orchestration import (
    CodexReceiptRemovalCompositionBlockReason,
    CodexReceiptRemovalCompositionBlocked,
    CodexReceiptRemovalCompositionResult,
    CodexReceiptRemovalNotInstalled,
    CodexReceiptRemovalRemoved,
    compose_codex_receipt_removal,
    ArtifactDigest,
    CodexAuthPolicy,
    CodexCliVersion,
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceName,
    CodexMarketplaceSource,
    CodexPluginEntry,
    CodexPluginId,
    CodexPluginList,
    CodexPluginName,
    CodexReceiptRemovalBlockReason,
    CodexReceiptRemovalInvocation,
    CodexRegistrationReceipt,
    InstallRoot,
    InstallationId,
    OwnedRelativePath,
)
from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortFailureReason,
    CodexCompensationPortManifest,
    CodexCompensationPortOperation,
    CodexCompensationPortOperationFailed,
    CodexCompensationPortRequest,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
)
from library.local_orchestration.codex_compensation_reducer import CodexProofTruth


class CodexReceiptRemovalCompositionTests(unittest.TestCase):
    def test_B1_public_contract_is_available(self) -> None:
        self.assertIsNotNone(CodexReceiptRemovalCompositionBlockReason)
        self.assertIsNotNone(CodexReceiptRemovalCompositionBlocked)
        self.assertIsNotNone(CodexReceiptRemovalCompositionResult)
        self.assertIsNotNone(CodexReceiptRemovalNotInstalled)
        self.assertIsNotNone(CodexReceiptRemovalRemoved)
        self.assertIsNotNone(compose_codex_receipt_removal)

    def test_B1_completed_replay_is_not_installed_and_reuses_one_request(self) -> None:
        port = _RecordingPort()
        result = compose_codex_receipt_removal(_invocation(), port)

        self.assertIsInstance(result, CodexReceiptRemovalNotInstalled)
        self.assertEqual(
            [
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
            ],
            port.calls,
        )
        self.assertEqual(1, len({id(request) for request in port.requests}))

    def test_B2_each_owned_residue_reaches_ordered_removal(self) -> None:
        cases: tuple[tuple[str, CodexPluginList, CodexMarketplaceList, CodexInstalledPathAbsenceProof], ...] = (
            ("plugin", _owned_plugins(), _empty_marketplaces(), _path(True)),
            ("marketplace", _empty_plugins(), _owned_marketplaces(), _path(True)),
            ("path", _empty_plugins(), _empty_marketplaces(), _path(False)),
            ("combined", _owned_plugins(), _owned_marketplaces(), _path(False)),
        )
        for name, plugins, marketplaces, path in cases:
            with self.subTest(name=name):
                port = _RecordingPort(
                    plugin_lists=[plugins, _empty_plugins()],
                    marketplace_lists=[marketplaces, _empty_marketplaces()],
                    paths=[path, _path(True)],
                )
                result = compose_codex_receipt_removal(_invocation(), port)
                self.assertIsInstance(result, CodexReceiptRemovalRemoved)
                self.assertEqual(
                    [
                        CodexCompensationPortOperation.LIST_PLUGINS,
                        CodexCompensationPortOperation.LIST_MARKETPLACES,
                        CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                        CodexCompensationPortOperation.REMOVE_PLUGIN,
                        CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                        CodexCompensationPortOperation.LIST_PLUGINS,
                        CodexCompensationPortOperation.LIST_MARKETPLACES,
                        CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                    ],
                    port.calls,
                )

    def test_B3_foreign_entries_coexist_with_owned_absence(self) -> None:
        port = _RecordingPort(
            plugin_lists=[_foreign_plugins(), _empty_plugins()],
            marketplace_lists=[_foreign_marketplaces(), _empty_marketplaces()],
            paths=[_path(True), _path(True)],
        )
        result = compose_codex_receipt_removal(_invocation(), port)
        self.assertIsInstance(result, CodexReceiptRemovalNotInstalled)
        self.assertNotIn(CodexCompensationPortOperation.REMOVE_PLUGIN, port.calls)
        self.assertNotIn(CodexCompensationPortOperation.REMOVE_MARKETPLACE, port.calls)

    def test_B3_invalid_preproofs_block_before_removal(self) -> None:
        cases: tuple[tuple[str, object, object, object], ...] = (
            ("plugin", object(), _empty_marketplaces(), _path(True)),
            ("marketplace", _empty_plugins(), object(), _path(True)),
            ("path", _empty_plugins(), _empty_marketplaces(), object()),
            (
                "plugin-declared-failure",
                _failure(CodexCompensationPortOperation.LIST_PLUGINS),
                _empty_marketplaces(),
                _path(True),
            ),
        )
        for name, plugins, marketplaces, path in cases:
            with self.subTest(name=name):
                port = _RecordingPort(
                    plugin_lists=[cast(CodexPluginList, plugins)],
                    marketplace_lists=[cast(CodexMarketplaceList, marketplaces)],
                    paths=[cast(CodexInstalledPathAbsenceProof, path)],
                )
                result = compose_codex_receipt_removal(_invocation(), port)
                self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
                blocked = cast(CodexReceiptRemovalCompositionBlocked, result)
                self.assertIs(
                    CodexReceiptRemovalCompositionBlockReason.PRE_REMOVAL_EVIDENCE_INVALID,
                    blocked.reason,
                )
                self.assertNotIn(CodexCompensationPortOperation.REMOVE_PLUGIN, port.calls)
                self.assertNotIn(CodexCompensationPortOperation.REMOVE_MARKETPLACE, port.calls)

    def test_B4_plugin_failure_short_circuits_marketplace(self) -> None:
        port = _RecordingPort(
            plugin_lists=[_owned_plugins()],
            marketplace_lists=[_empty_marketplaces()],
            paths=[_path(True)],
            plugin_removals=[_failure(CodexCompensationPortOperation.REMOVE_PLUGIN)],
        )
        result = compose_codex_receipt_removal(_invocation(), port)
        self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
        self.assertEqual(
            CodexReceiptRemovalCompositionBlockReason.PLUGIN_REMOVAL_FAILED,
            cast(CodexReceiptRemovalCompositionBlocked, result).reason,
        )
        self.assertEqual(4, len(port.calls))
        self.assertNotIn(CodexCompensationPortOperation.REMOVE_MARKETPLACE, port.calls)

    def test_B4_marketplace_failure_short_circuits_postproof(self) -> None:
        port = _RecordingPort(
            plugin_lists=[_owned_plugins()],
            marketplace_lists=[_empty_marketplaces()],
            paths=[_path(True)],
            marketplace_removals=[_failure(CodexCompensationPortOperation.REMOVE_MARKETPLACE)],
        )
        result = compose_codex_receipt_removal(_invocation(), port)
        self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
        self.assertEqual(
            CodexReceiptRemovalCompositionBlockReason.MARKETPLACE_REMOVAL_FAILED,
            cast(CodexReceiptRemovalCompositionBlocked, result).reason,
        )
        self.assertEqual(5, len(port.calls))
        self.assertNotIn(CodexCompensationPortOperation.LIST_PLUGINS, port.calls[5:])

    def test_B5_every_postproof_absence_conjunct_is_required(self) -> None:
        cases: tuple[tuple[str, CodexPluginList, CodexMarketplaceList, CodexInstalledPathAbsenceProof], ...] = (
            ("installed", _owned_plugins(), _empty_marketplaces(), _path(True)),
            ("available", _available_owned_plugins(), _empty_marketplaces(), _path(True)),
            ("marketplace", _empty_plugins(), _owned_marketplaces(), _path(True)),
            ("path", _empty_plugins(), _empty_marketplaces(), _path(False)),
        )
        for name, plugins, marketplaces, path in cases:
            with self.subTest(name=name):
                port = _RecordingPort(
                    plugin_lists=[_owned_plugins(), plugins],
                    marketplace_lists=[_empty_marketplaces(), marketplaces],
                    paths=[_path(True), path],
                )
                result = compose_codex_receipt_removal(_invocation(), port)
                self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
                self.assertEqual(
                    CodexReceiptRemovalCompositionBlockReason.POST_REMOVAL_EVIDENCE_INVALID,
                    cast(CodexReceiptRemovalCompositionBlocked, result).reason,
                )

    def test_B6_partial_retry_is_not_mistaken_for_completed_replay(self) -> None:
        port = _RecordingPort(
            plugin_lists=[_empty_plugins(), _empty_plugins()],
            marketplace_lists=[_owned_marketplaces(), _empty_marketplaces()],
            paths=[_path(True), _path(True)],
        )
        result = compose_codex_receipt_removal(_invocation(), port)
        self.assertIsInstance(result, CodexReceiptRemovalRemoved)
        self.assertIn(CodexCompensationPortOperation.REMOVE_PLUGIN, port.calls)
        self.assertIn(CodexCompensationPortOperation.REMOVE_MARKETPLACE, port.calls)

    def test_B7_invalid_invocation_does_not_inspect_port_candidate(self) -> None:
        trap = _CandidateTrap()
        result = compose_codex_receipt_removal(object(), trap)
        self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
        self.assertEqual(
            CodexReceiptRemovalCompositionBlockReason.INVALID_INVOCATION,
            cast(CodexReceiptRemovalCompositionBlocked, result).reason,
        )
        self.assertEqual(0, trap.inspections)

    def test_B7_receipt_identity_and_invalid_port_are_finite(self) -> None:
        bad_receipt = _receipt()
        result = compose_codex_receipt_removal(
            _invocation(
                receipt=bad_receipt,
                installation_id=InstallationId(value="installation-ffffffffffffffff"),
            ),
            object(),
        )
        self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
        self.assertEqual(
            CodexReceiptRemovalBlockReason.RECEIPT_MISMATCH.value,
            cast(CodexReceiptRemovalCompositionBlocked, result).reason.value,
        )

        invalid_port = compose_codex_receipt_removal(_invocation(), object())
        self.assertIsInstance(invalid_port, CodexReceiptRemovalCompositionBlocked)
        self.assertEqual(
            CodexReceiptRemovalCompositionBlockReason.INVALID_PORT,
            cast(CodexReceiptRemovalCompositionBlocked, invalid_port).reason,
        )

    def test_B7_invalid_receipt_is_finite_before_port_admission(self) -> None:
        invalid_receipt = CodexRegistrationReceipt.model_construct(
            installation_id=INSTALLATION,
            root=ROOT,
            marketplace=MARKETPLACE,
            plugin_id=PLUGIN_ID,
            plugin_name=PLUGIN,
            version=VERSION,
            source_locator=SOURCE,
            installed_locator=INSTALLED,
            auth_policy=AUTH_POLICY,
            digest=object(),
            _fields_set={
                "installation_id",
                "root",
                "marketplace",
                "plugin_id",
                "plugin_name",
                "version",
                "source_locator",
                "installed_locator",
                "auth_policy",
                "digest",
            },
        )
        invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=INSTALLATION,
            root=ROOT,
            receipt=invalid_receipt,
            _fields_set={"installation_id", "root", "receipt"},
        )
        result = compose_codex_receipt_removal(invocation, _CandidateTrap())
        self.assertIsInstance(result, CodexReceiptRemovalCompositionBlocked)
        self.assertEqual(
            CodexReceiptRemovalCompositionBlockReason.INVALID_RECEIPT,
            cast(CodexReceiptRemovalCompositionBlocked, result).reason,
        )

    def test_B7_adapter_exception_propagates_and_stops_subsequent_calls(self) -> None:
        port = _RaisingPort()
        with self.assertRaises(RuntimeError):
            compose_codex_receipt_removal(_invocation(), port)
        self.assertEqual(1, port.inspections)

    def test_B8_remove_order_is_plugin_before_marketplace(self) -> None:
        port = _RecordingPort(
            plugin_lists=[_owned_plugins(), _empty_plugins()],
            marketplace_lists=[_owned_marketplaces(), _empty_marketplaces()],
            paths=[_path(False), _path(True)],
        )
        compose_codex_receipt_removal(_invocation(), port)
        self.assertLess(
            port.calls.index(CodexCompensationPortOperation.REMOVE_PLUGIN),
            port.calls.index(CodexCompensationPortOperation.REMOVE_MARKETPLACE),
        )

    def test_B8_replay_has_zero_removal_calls(self) -> None:
        port = _RecordingPort()
        result = compose_codex_receipt_removal(_invocation(), port)
        self.assertIsInstance(result, CodexReceiptRemovalNotInstalled)
        self.assertEqual([], [
            call for call in port.calls
            if call in {
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
            }
        ])

    def test_B8_invalid_plugin_result_short_circuits_marketplace(self) -> None:
        port = _RecordingPort(
            plugin_lists=[_owned_plugins()],
            marketplace_lists=[_empty_marketplaces()],
            paths=[_path(True)],
            plugin_removals=[object()],
        )
        result = compose_codex_receipt_removal(_invocation(), port)
        self.assertEqual(
            CodexReceiptRemovalCompositionBlockReason.PLUGIN_REMOVAL_FAILED,
            cast(CodexReceiptRemovalCompositionBlocked, result).reason,
        )
        self.assertNotIn(CodexCompensationPortOperation.REMOVE_MARKETPLACE, port.calls)


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow")
MARKETPLACE = CodexMarketplaceName(value="probe-market")
PLUGIN_ID = CodexPluginId(value="plugin-probe-012345")
PLUGIN = CodexPluginName(value="probe-plugin")
VERSION = CodexCliVersion(value="1.2.3")
SOURCE = OwnedRelativePath(value="marketplaces/probe-market")
INSTALLED = OwnedRelativePath(value="plugins/probe-plugin")
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")
DIGEST = ArtifactDigest(value="a" * 64)


def _receipt(*, root: InstallRoot = ROOT) -> CodexRegistrationReceipt:
    return CodexRegistrationReceipt(
        installation_id=INSTALLATION,
        root=root,
        marketplace=MARKETPLACE,
        plugin_id=PLUGIN_ID,
        plugin_name=PLUGIN,
        version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        auth_policy=AUTH_POLICY,
        digest=DIGEST,
    )


def _invocation(
    *,
    receipt: CodexRegistrationReceipt | None = None,
    installation_id: InstallationId | None = None,
) -> CodexReceiptRemovalInvocation:
    current = receipt or _receipt()
    return CodexReceiptRemovalInvocation(
        installation_id=installation_id or current.installation_id,
        root=current.root,
        receipt=current,
    )


def _owned_plugin() -> CodexPluginEntry:
    return CodexPluginEntry(
        pluginId=PLUGIN_ID.value,
        name=PLUGIN.value,
        marketplaceName=MARKETPLACE.value,
        version=VERSION.value,
        installed=True,
        enabled=True,
        source=INSTALLED.value,
        installPolicy="local",
        authPolicy=AUTH_POLICY.value,
        marketplaceSource=CodexMarketplaceSource(type="directory", value=SOURCE.value),
    )


def _foreign_plugin() -> CodexPluginEntry:
    return CodexPluginEntry(
        pluginId="plugin-foreign-012345",
        name="foreign-plugin",
        marketplaceName="foreign-market",
        version="1.0.0",
        installed=True,
        enabled=True,
        source="plugins/foreign-plugin",
        installPolicy="local",
        authPolicy=AUTH_POLICY.value,
        marketplaceSource=CodexMarketplaceSource(type="directory", value="marketplaces/foreign-market"),
    )


def _owned_marketplace() -> CodexMarketplaceEntry:
    return CodexMarketplaceEntry(
        name=MARKETPLACE.value,
        root=r"C:\disposable\probe-market",
        marketplaceSource=CodexMarketplaceSource(type="directory", value=SOURCE.value),
    )


def _foreign_marketplace() -> CodexMarketplaceEntry:
    return CodexMarketplaceEntry(
        name="foreign-market",
        root=r"C:\disposable\foreign-market",
        marketplaceSource=CodexMarketplaceSource(type="directory", value="marketplaces/foreign-market"),
    )


def _owned_plugins() -> CodexPluginList:
    return CodexPluginList(installed=(_owned_plugin(),), available=())


def _available_owned_plugins() -> CodexPluginList:
    return CodexPluginList(installed=(), available=(_owned_plugin(),))


def _foreign_plugins() -> CodexPluginList:
    return CodexPluginList(installed=(_foreign_plugin(),), available=())


def _empty_plugins() -> CodexPluginList:
    return CodexPluginList(installed=(), available=())


def _owned_marketplaces() -> CodexMarketplaceList:
    return CodexMarketplaceList(marketplaces=(_owned_marketplace(),))


def _foreign_marketplaces() -> CodexMarketplaceList:
    return CodexMarketplaceList(marketplaces=(_foreign_marketplace(),))


def _empty_marketplaces() -> CodexMarketplaceList:
    return CodexMarketplaceList(marketplaces=())


def _path(absent: bool) -> CodexInstalledPathAbsenceProof:
    return CodexInstalledPathAbsenceProof.model_construct(
        manifest=CodexCompensationPortManifest(
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
        ),
        absent=absent,
        _fields_set={"manifest", "absent"},
    )


def _manifest() -> CodexCompensationPortManifest:
    return _path(True).manifest


def _failure(operation: CodexCompensationPortOperation) -> CodexCompensationPortOperationFailed:
    return CodexCompensationPortOperationFailed(
        manifest=_manifest(),
        operation=operation,
        reason=CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
    )


class _RecordingPort:
    def __init__(
        self,
        *,
        plugin_lists: list[object] | None = None,
        marketplace_lists: list[object] | None = None,
        paths: list[object] | None = None,
        plugin_removals: list[object] | None = None,
        marketplace_removals: list[object] | None = None,
    ) -> None:
        self.calls: list[CodexCompensationPortOperation] = []
        self.requests: list[CodexCompensationPortRequest] = []
        self.plugin_lists = plugin_lists or [_empty_plugins()]
        self.marketplace_lists = marketplace_lists or [_empty_marketplaces()]
        self.paths = paths or [_path(True)]
        self.plugin_removals = plugin_removals or [
            CodexPluginRemovalProof(manifest=_manifest(), status="REMOVED")
        ]
        self.marketplace_removals = marketplace_removals or [
            CodexMarketplaceRemovalProof(manifest=_manifest(), status="REMOVED")
        ]

    def _record(self, operation: CodexCompensationPortOperation, request: CodexCompensationPortRequest) -> None:
        self.calls.append(operation)
        self.requests.append(request)

    def _next(self, values: list[object]) -> object:
        if len(values) == 1:
            return values[0]
        return values.pop(0)

    def remove_plugin(self, request: CodexCompensationPortRequest) -> object:
        self._record(CodexCompensationPortOperation.REMOVE_PLUGIN, request)
        return self._next(self.plugin_removals)

    def remove_marketplace(self, request: CodexCompensationPortRequest) -> object:
        self._record(CodexCompensationPortOperation.REMOVE_MARKETPLACE, request)
        return self._next(self.marketplace_removals)

    def list_plugins(self, request: CodexCompensationPortRequest) -> object:
        self._record(CodexCompensationPortOperation.LIST_PLUGINS, request)
        return self._next(self.plugin_lists)

    def list_marketplaces(self, request: CodexCompensationPortRequest) -> object:
        self._record(CodexCompensationPortOperation.LIST_MARKETPLACES, request)
        return self._next(self.marketplace_lists)

    def prove_installed_path_absent(self, request: CodexCompensationPortRequest) -> object:
        self._record(CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT, request)
        return self._next(self.paths)


class _CandidateTrap:
    def __init__(self) -> None:
        self.inspections = 0

    def __getattribute__(self, name: str) -> object:
        if name not in {"inspections", "__class__", "__dict__", "__getattribute__"}:
            object.__setattr__(self, "inspections", object.__getattribute__(self, "inspections") + 1)
            raise AssertionError("candidate inspected")
        return object.__getattribute__(self, name)


class _RaisingPort(_RecordingPort):
    def __init__(self) -> None:
        super().__init__(plugin_lists=[_owned_plugins()])
        self.inspections = 0

    def list_plugins(self, request: CodexCompensationPortRequest) -> object:
        self.inspections += 1
        raise RuntimeError("declared test seam exception")
