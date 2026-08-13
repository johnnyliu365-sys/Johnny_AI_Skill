"""P1-P8 closure for pure compensation-oracle response admission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast
import unittest

from library.local_orchestration.host_contracts import (
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceSource,
    CodexPluginEntry,
    CodexPluginList,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleAbsent,
    OracleAction,
    OracleBlocked,
    OracleBlockReason,
    OracleCompleted,
)
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceRemove,
    CodexPluginRemove,
    CodexProtocolPayload,
    CodexProtocolAccepted,
    CodexProtocolSurface,
)
from tests.staging.codex_lifecycle_oracle.response_admission import (
    CodexOracleResponseAdmission,
    CodexOracleResponseRejectReason,
    CodexOracleResponseRejected,
    admit_codex_oracle_response,
)


PLUGIN_REMOVE = CodexPluginRemove(
    pluginId="owned-plugin",
    name="owned-plugin-name",
    marketplaceName="owned-market",
)
MARKETPLACE_REMOVE = CodexMarketplaceRemove(
    marketplaceName="owned-market",
    installedRoot=r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\owned-market",
)
MARKETPLACE_SOURCE = CodexMarketplaceSource(type="marketplace", value="owned-market")


class DerivedCompleted(OracleCompleted):
    """A result subclass that must not cross the response boundary."""


class DerivedAccepted(CodexProtocolAccepted):
    """An exact-shaped protocol envelope subclass."""


class DerivedPluginEntry(CodexPluginEntry):
    """An exact-shaped nested payload subclass."""


class ProtocolTrap:
    """A caller object whose protocols must never be observed."""

    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"caller protocol executed: {name}")


@dataclass(frozen=True)
class NonAction:
    value: str


def _completed(surface: CodexProtocolSurface, payload: CodexProtocolPayload) -> OracleCompleted:
    return OracleCompleted(
        response=CodexProtocolAccepted(
            surface=surface,
            payload=payload,
        )
    )


def _constructed_completed(surface: object, payload: object) -> OracleCompleted:
    response = CodexProtocolAccepted.model_construct(surface=surface, payload=payload)
    return OracleCompleted(response=response)


def _admit(value: object, action: object) -> CodexOracleResponseAdmission:
    return admit_codex_oracle_response(value, cast(OracleAction, action))


def _assert_rejected(
    testcase: unittest.TestCase,
    value: object,
    action: object,
    reason: CodexOracleResponseRejectReason,
) -> None:
    result = _admit(value, action)
    testcase.assertIs(type(result), CodexOracleResponseRejected)
    if type(result) is not CodexOracleResponseRejected:
        raise AssertionError("expected finite response rejection")
    testcase.assertIs(result.reason, reason)
    testcase.assertEqual(result.status, "INVALID_RESPONSE")


class CodexOracleResponseAdmissionTests(unittest.TestCase):
    """The boundary is a pure, exact, metadata-only projection."""

    def test_p1_public_module_and_function_exist(self) -> None:
        self.assertTrue(callable(admit_codex_oracle_response))

    def test_p2_invalid_actions_results_and_top_level_shapes_are_finite(self) -> None:
        valid = _completed(CodexProtocolSurface.PLUGIN_REMOVE, PLUGIN_REMOVE)
        _assert_rejected(self, valid, NonAction("not-an-action"), CodexOracleResponseRejectReason.INVALID_ACTION)
        _assert_rejected(self, valid, OracleAction.VERSION, CodexOracleResponseRejectReason.UNSUPPORTED_ACTION)
        _assert_rejected(self, ProtocolTrap(), OracleAction.PLUGIN_REMOVE, CodexOracleResponseRejectReason.INVALID_RESULT)
        _assert_rejected(self, DerivedCompleted(response=valid.response), OracleAction.PLUGIN_REMOVE, CodexOracleResponseRejectReason.INVALID_RESULT)

        constructed = CodexProtocolAccepted.model_construct(surface=CodexProtocolSurface.PLUGIN_REMOVE)
        _assert_rejected(
            self,
            OracleCompleted(response=constructed),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )
        forged = CodexProtocolAccepted.model_construct(surface=CodexProtocolSurface.PLUGIN_REMOVE, payload=PLUGIN_REMOVE)
        object.__getattribute__(forged, "__dict__")["injected"] = "forbidden"
        _assert_rejected(
            self,
            OracleCompleted(response=forged),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )

    def test_p3_plugin_remove_rebuilds_exact_response_and_rejects_matrix(self) -> None:
        original = _completed(CodexProtocolSurface.PLUGIN_REMOVE, PLUGIN_REMOVE)
        result = _admit(original, OracleAction.PLUGIN_REMOVE)
        self.assertIs(type(result), CodexProtocolAccepted)
        if type(result) is not CodexProtocolAccepted:
            raise AssertionError("expected accepted plugin removal")
        self.assertIsNot(result, original.response)
        self.assertIsNot(result.payload, original.response.payload)
        self.assertEqual(result, original.response)

        _assert_rejected(
            self,
            _constructed_completed(CodexProtocolSurface.MARKETPLACE_REMOVE, MARKETPLACE_REMOVE),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.SURFACE_MISMATCH,
        )
        _assert_rejected(
            self,
            _constructed_completed(CodexProtocolSurface.PLUGIN_REMOVE, MARKETPLACE_REMOVE),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )
        missing = CodexProtocolAccepted.model_construct(surface=CodexProtocolSurface.PLUGIN_REMOVE)
        _assert_rejected(
            self,
            OracleCompleted(response=missing),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )
        nested = CodexPluginRemove.model_construct(pluginId="owned-plugin", name="owned-plugin-name")
        _assert_rejected(
            self,
            _constructed_completed(CodexProtocolSurface.PLUGIN_REMOVE, nested),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )

    def test_p4_marketplace_remove_rebuilds_exact_response_and_rejects_matrix(self) -> None:
        original = _completed(CodexProtocolSurface.MARKETPLACE_REMOVE, MARKETPLACE_REMOVE)
        result = _admit(original, OracleAction.MARKETPLACE_REMOVE)
        self.assertIs(type(result), CodexProtocolAccepted)
        if type(result) is not CodexProtocolAccepted:
            raise AssertionError("expected accepted marketplace removal")
        self.assertIsNot(result, original.response)
        self.assertIsNot(result.payload, original.response.payload)
        self.assertEqual(result, original.response)

        _assert_rejected(
            self,
            _constructed_completed(CodexProtocolSurface.PLUGIN_REMOVE, PLUGIN_REMOVE),
            OracleAction.MARKETPLACE_REMOVE,
            CodexOracleResponseRejectReason.SURFACE_MISMATCH,
        )
        _assert_rejected(
            self,
            _constructed_completed(CodexProtocolSurface.MARKETPLACE_REMOVE, PLUGIN_REMOVE),
            OracleAction.MARKETPLACE_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )
        nested = CodexMarketplaceRemove.model_construct(marketplaceName="owned-market")
        _assert_rejected(
            self,
            _constructed_completed(CodexProtocolSurface.MARKETPLACE_REMOVE, nested),
            OracleAction.MARKETPLACE_REMOVE,
            CodexOracleResponseRejectReason.MALFORMED_RESPONSE,
        )

    def test_p5_plugin_list_rebuilds_nested_entries_without_filtering_data(self) -> None:
        owned = CodexPluginEntry(
            pluginId="owned-plugin",
            name="owned-plugin-name",
            marketplaceName="owned-market",
            version="1.0.0",
            installed=True,
            enabled=True,
            source="owned-source",
            installPolicy="global",
            authPolicy="trusted",
            marketplaceSource=MARKETPLACE_SOURCE,
        )
        duplicate = CodexPluginEntry(
            pluginId="owned-plugin",
            name="duplicate-data",
            marketplaceName="foreign-market",
            version="2.0.0",
            installed=False,
            enabled=False,
            source="foreign-source",
            installPolicy="local",
            authPolicy="untrusted",
        )
        response = _completed(
            CodexProtocolSurface.PLUGIN_LIST,
            CodexPluginList(installed=(owned, duplicate), available=(duplicate,)),
        )
        result = _admit(response, OracleAction.PLUGIN_LIST)
        self.assertIs(type(result), CodexProtocolAccepted)
        if type(result) is not CodexProtocolAccepted:
            raise AssertionError("expected accepted plugin list")
        self.assertIs(type(result.payload), CodexPluginList)
        if type(result.payload) is not CodexPluginList:
            raise AssertionError("expected plugin-list payload")
        self.assertEqual(len(result.payload.installed), 2)
        self.assertEqual(len(result.payload.available), 1)
        self.assertEqual(result.payload.installed[0].marketplaceSource, MARKETPLACE_SOURCE)
        self.assertIsNot(result.payload.installed[0], owned)
        self.assertIsNot(result.payload.installed[0].marketplaceSource, MARKETPLACE_SOURCE)

        derived = DerivedPluginEntry(
            pluginId=owned.pluginId,
            name=owned.name,
            marketplaceName=owned.marketplaceName,
            version=owned.version,
            installed=owned.installed,
            enabled=owned.enabled,
            source=owned.source,
            installPolicy=owned.installPolicy,
            authPolicy=owned.authPolicy,
        )
        malformed = _completed(CodexProtocolSurface.PLUGIN_LIST, CodexPluginList(installed=(derived,), available=()))
        _assert_rejected(self, malformed, OracleAction.PLUGIN_LIST, CodexOracleResponseRejectReason.MALFORMED_RESPONSE)

    def test_p6_marketplace_list_rebuilds_nested_entries_and_source(self) -> None:
        entry = CodexMarketplaceEntry(
            name="owned-market",
            root=r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\marketplaces\owned-market",
            marketplaceSource=MARKETPLACE_SOURCE,
        )
        response = _completed(
            CodexProtocolSurface.MARKETPLACE_LIST,
            CodexMarketplaceList(marketplaces=(entry,)),
        )
        result = _admit(response, OracleAction.MARKETPLACE_LIST)
        self.assertIs(type(result), CodexProtocolAccepted)
        if type(result) is not CodexProtocolAccepted:
            raise AssertionError("expected accepted marketplace list")
        self.assertIs(type(result.payload), CodexMarketplaceList)
        if type(result.payload) is not CodexMarketplaceList:
            raise AssertionError("expected marketplace-list payload")
        self.assertEqual(result.payload.marketplaces[0].name, entry.name)
        self.assertIsNot(result.payload.marketplaces[0], entry)
        self.assertIsNot(result.payload.marketplaces[0].marketplaceSource, MARKETPLACE_SOURCE)

        constructed = CodexMarketplaceEntry.model_construct(name="owned-market")
        malformed = _completed(CodexProtocolSurface.MARKETPLACE_LIST, CodexMarketplaceList(marketplaces=(constructed,)))
        _assert_rejected(self, malformed, OracleAction.MARKETPLACE_LIST, CodexOracleResponseRejectReason.MALFORMED_RESPONSE)

    def test_p7_absence_gate_and_block_are_metadata_only(self) -> None:
        absence = OracleAbsent()
        result = _admit(absence, OracleAction.ABSENCE)
        self.assertIs(type(result), OracleAbsent)
        if type(result) is not OracleAbsent:
            raise AssertionError("expected accepted absence")
        self.assertIsNot(result, absence)

        _assert_rejected(self, absence, OracleAction.PLUGIN_LIST, CodexOracleResponseRejectReason.ACTION_RESULT_MISMATCH)
        _assert_rejected(
            self,
            _completed(CodexProtocolSurface.PLUGIN_LIST, CodexPluginList(installed=(), available=())),
            OracleAction.ABSENCE,
            CodexOracleResponseRejectReason.ACTION_RESULT_MISMATCH,
        )

        blocked = OracleBlocked(reason=cast(OracleBlockReason, ProtocolTrap()))
        blocked_result = _admit(blocked, OracleAction.PLUGIN_REMOVE)
        self.assertIs(type(blocked_result), CodexOracleResponseRejected)
        if type(blocked_result) is not CodexOracleResponseRejected:
            raise AssertionError("expected dependency-blocked result")
        self.assertIs(blocked_result.reason, CodexOracleResponseRejectReason.DEPENDENCY_BLOCKED)
        self.assertNotIn("ProtocolTrap", repr(blocked_result))

    def test_p8_reverse_surface_matching_guard(self) -> None:
        _assert_rejected(
            self,
            _completed(CodexProtocolSurface.MARKETPLACE_REMOVE, MARKETPLACE_REMOVE),
            OracleAction.PLUGIN_REMOVE,
            CodexOracleResponseRejectReason.SURFACE_MISMATCH,
        )

    def test_p8_reverse_recursive_exact_state_guard(self) -> None:
        constructed_entry = CodexPluginEntry.model_construct(
            pluginId="owned-plugin",
            name="owned-plugin-name",
            marketplaceName="owned-market",
            version="1.0.0",
            installed=True,
            enabled=True,
            source="owned-source",
            installPolicy="global",
        )
        response = _completed(
            CodexProtocolSurface.PLUGIN_LIST,
            CodexPluginList(installed=(constructed_entry,), available=()),
        )
        _assert_rejected(self, response, OracleAction.PLUGIN_LIST, CodexOracleResponseRejectReason.MALFORMED_RESPONSE)

    def test_p8_reverse_absence_gate(self) -> None:
        _assert_rejected(self, OracleAbsent(), OracleAction.PLUGIN_REMOVE, CodexOracleResponseRejectReason.ACTION_RESULT_MISMATCH)


if __name__ == "__main__":
    unittest.main()
