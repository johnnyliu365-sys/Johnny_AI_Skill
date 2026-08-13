"""TDD coverage for the pure 05C1 receipt-removal projection."""

from __future__ import annotations

import unittest
from typing import cast

from pydantic import BaseModel

from library.local_orchestration import (
    ArtifactDigest,
    CodexAuthPolicy,
    CodexCliVersion,
    CodexMarketplaceName,
    CodexPluginId,
    CodexPluginName,
    CodexReceiptRemovalBlockReason,
    CodexReceiptRemovalBlocked,
    CodexReceiptRemovalInvocation,
    CodexReceiptRemovalReady,
    CodexRegistrationReceipt,
    InstallRoot,
    InstallationId,
    OwnedRelativePath,
    build_codex_receipt_removal_request,
)
from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortManifest,
    CodexCompensationPortRequest,
)
from library.local_orchestration.codex_receipt_removal_request import (
    CodexReceiptRemovalResult,
)


class _ReceiptSubclass(CodexRegistrationReceipt):
    def __eq__(self, other: object) -> bool:
        raise AssertionError("receipt equality must not run")

    def model_dump_json(self, *args: object, **kwargs: object) -> str:
        raise AssertionError("receipt serialization must not run")


class _InvocationSubclass(CodexReceiptRemovalInvocation):
    def __getattribute__(self, name: str) -> object:
        if name in {"installation_id", "root", "receipt", "model_dump_json"}:
            raise AssertionError("invocation descriptor must not run")
        return super().__getattribute__(name)

    def __eq__(self, other: object) -> bool:
        raise AssertionError("invocation equality must not run")


def _receipt(
    *,
    installation_id: InstallationId | None = None,
    root: InstallRoot | None = None,
    source_locator: OwnedRelativePath | None = None,
    plugin_name: CodexPluginName | None = None,
) -> CodexRegistrationReceipt:
    return CodexRegistrationReceipt(
        installation_id=installation_id
        or InstallationId(value="installation-00000000000005c1"),
        root=root or InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
        marketplace=CodexMarketplaceName(value="acceptance-market"),
        plugin_id=CodexPluginId(value="acceptance-plugin-id"),
        plugin_name=plugin_name or CodexPluginName(value="acceptance-plugin"),
        version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=source_locator or OwnedRelativePath(value="marketplaces/acceptance-market"),
        installed_locator=OwnedRelativePath(value="plugins/acceptance-plugin"),
        auth_policy=CodexAuthPolicy(value="trusted-local"),
        digest=ArtifactDigest(value="a" * 64),
    )


def _invocation(
    *,
    installation_id: InstallationId | None = None,
    root: InstallRoot | None = None,
    receipt: CodexRegistrationReceipt | None = None,
) -> CodexReceiptRemovalInvocation:
    current_receipt = receipt or _receipt()
    return CodexReceiptRemovalInvocation(
        installation_id=installation_id or current_receipt.installation_id,
        root=root or current_receipt.root,
        receipt=current_receipt,
    )


def _assert_blocked(
    testcase: unittest.TestCase,
    result: CodexReceiptRemovalResult,
    reason: CodexReceiptRemovalBlockReason,
) -> None:
    testcase.assertIsInstance(result, CodexReceiptRemovalBlocked)
    blocked = cast(CodexReceiptRemovalBlocked, result)
    testcase.assertEqual("UNINSTALL_BLOCKED", blocked.status)
    testcase.assertIs(reason, blocked.reason)


def _assert_ready(
    testcase: unittest.TestCase, result: CodexReceiptRemovalResult
) -> CodexReceiptRemovalReady:
    testcase.assertIsInstance(result, CodexReceiptRemovalReady)
    ready = cast(CodexReceiptRemovalReady, result)
    testcase.assertEqual("READY", ready.status)
    testcase.assertIs(type(ready.receipt), CodexRegistrationReceipt)
    testcase.assertIs(type(ready.request), CodexCompensationPortRequest)
    testcase.assertIs(type(ready.request.manifest), CodexCompensationPortManifest)
    return ready


class CodexReceiptRemovalRequestTests(unittest.TestCase):
    def test_R1_exact_integrated_receipt_produces_ready_request_and_exports(self) -> None:
        receipt = _receipt()
        result = build_codex_receipt_removal_request(_invocation(receipt=receipt))
        ready = _assert_ready(self, result)

        self.assertEqual(receipt.installation_id.value, ready.receipt.installation_id.value)
        self.assertEqual(receipt.root.value, ready.receipt.root.value)
        self.assertEqual(receipt.digest.value, ready.receipt.digest.value)
        self.assertEqual(receipt.installation_id.value, ready.request.manifest.installation_id.value)
        self.assertEqual(receipt.root.value, ready.request.manifest.root.value)
        self.assertEqual(receipt.marketplace.value, ready.request.manifest.marketplace.value)
        self.assertEqual(receipt.plugin_name.value, ready.request.manifest.plugin.value)

    def test_R2_every_receipt_field_maps_once_with_source_and_plugin_renames(self) -> None:
        receipt = _receipt()
        ready = _assert_ready(self, build_codex_receipt_removal_request(_invocation(receipt=receipt)))
        manifest = ready.request.manifest
        expected_pairs = (
            (receipt.installation_id.value, manifest.installation_id.value),
            (receipt.root.value, manifest.root.value),
            (receipt.marketplace.value, manifest.marketplace.value),
            (receipt.source_locator.value, manifest.marketplace_source.value),
            (receipt.plugin_id.value, manifest.plugin_id.value),
            (receipt.plugin_name.value, manifest.plugin.value),
            (receipt.version.value, manifest.version.value),
            (receipt.installed_locator.value, manifest.installed_locator.value),
            (receipt.auth_policy.value, manifest.auth_policy.value),
            (receipt.digest.value, manifest.digest.value),
        )
        self.assertTrue(all(source == target for source, target in expected_pairs))
        self.assertEqual(10, len(expected_pairs))
        self.assertNotIn("source_locator", manifest.model_fields_set)
        self.assertNotIn("plugin_name", manifest.model_fields_set)

    def test_R3_installation_mismatch_is_receipt_mismatch(self) -> None:
        mismatch = InstallationId(value="installation-00000000000005c2")
        result = build_codex_receipt_removal_request(_invocation(installation_id=mismatch))
        _assert_blocked(self, result, CodexReceiptRemovalBlockReason.RECEIPT_MISMATCH)

    def test_R4_constructed_noncanonical_invocation_root_is_invalid_invocation(self) -> None:
        receipt = _receipt()
        mismatch = InstallRoot.model_construct(value=r"%LOCALAPPDATA%\OtherJohnnyAIWorkflow")
        invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=receipt.installation_id,
            root=mismatch,
            receipt=receipt,
        )
        result = build_codex_receipt_removal_request(invocation)
        _assert_blocked(self, result, CodexReceiptRemovalBlockReason.INVALID_INVOCATION)

    def test_R4_constructed_invalid_invocation_installation_id_is_invalid_invocation(self) -> None:
        receipt = _receipt()
        invalid_id = InstallationId.model_construct(value="")
        invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=invalid_id,
            root=receipt.root,
            receipt=receipt,
        )
        result = build_codex_receipt_removal_request(invocation)
        _assert_blocked(self, result, CodexReceiptRemovalBlockReason.INVALID_INVOCATION)

    def test_R4_constructed_invalid_receipt_root_is_invalid_receipt(self) -> None:
        receipt = _receipt()
        invalid_receipt = CodexRegistrationReceipt.model_construct(
            installation_id=receipt.installation_id,
            root=InstallRoot.model_construct(value=r"%LOCALAPPDATA%\OtherJohnnyAIWorkflow"),
            marketplace=receipt.marketplace,
            plugin_id=receipt.plugin_id,
            plugin_name=receipt.plugin_name,
            version=receipt.version,
            source_locator=receipt.source_locator,
            installed_locator=receipt.installed_locator,
            auth_policy=receipt.auth_policy,
            digest=receipt.digest,
        )
        invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=receipt.installation_id,
            root=receipt.root,
            receipt=invalid_receipt,
        )
        result = build_codex_receipt_removal_request(invocation)
        _assert_blocked(self, result, CodexReceiptRemovalBlockReason.INVALID_RECEIPT)

    def test_R4_null_scalar_and_container_invocations_are_invalid(self) -> None:
        candidates: tuple[object, ...] = (None, 5, "receipt", [], {}, ("receipt",))
        for candidate in candidates:
            with self.subTest(candidate_type=type(candidate).__name__):
                result = build_codex_receipt_removal_request(candidate)
                _assert_blocked(self, result, CodexReceiptRemovalBlockReason.INVALID_INVOCATION)

    def test_R4_missing_extra_private_and_malformed_constructed_state_is_finite(self) -> None:
        missing = CodexReceiptRemovalInvocation.model_construct()
        missing_receipt = CodexRegistrationReceipt.model_construct()
        malformed_receipt = CodexRegistrationReceipt.model_construct(
            installation_id="not-an-installation-id",
            root=_receipt().root,
            marketplace=_receipt().marketplace,
            plugin_id=_receipt().plugin_id,
            plugin_name=_receipt().plugin_name,
            version=_receipt().version,
            source_locator=_receipt().source_locator,
            installed_locator=_receipt().installed_locator,
            auth_policy=_receipt().auth_policy,
            digest=_receipt().digest,
        )
        malformed_invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=_receipt().installation_id,
            root=_receipt().root,
            receipt=malformed_receipt,
        )
        extra_invocation = _invocation()
        object.__setattr__(extra_invocation, "__pydantic_extra__", {"injected": "value"})
        private_receipt = _receipt()
        object.__setattr__(private_receipt, "__pydantic_private__", {"secret": "value"})
        private_invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=private_receipt.installation_id,
            root=private_receipt.root,
            receipt=private_receipt,
        )

        _assert_blocked(
            self,
            build_codex_receipt_removal_request(missing),
            CodexReceiptRemovalBlockReason.INVALID_INVOCATION,
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(
                CodexReceiptRemovalInvocation.model_construct(
                    installation_id=_receipt().installation_id,
                    root=_receipt().root,
                    receipt=missing_receipt,
                )
            ),
            CodexReceiptRemovalBlockReason.INVALID_RECEIPT,
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(malformed_invocation),
            CodexReceiptRemovalBlockReason.INVALID_RECEIPT,
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(extra_invocation),
            CodexReceiptRemovalBlockReason.INVALID_INVOCATION,
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(private_invocation),
            CodexReceiptRemovalBlockReason.INVALID_RECEIPT,
        )

    def test_R4_subclass_and_invalid_nested_values_are_rejected(self) -> None:
        base = _receipt()
        subclass = _ReceiptSubclass.model_construct(**object.__getattribute__(base, "__dict__"))
        subclass_invocation = CodexReceiptRemovalInvocation.model_construct(
            installation_id=base.installation_id,
            root=base.root,
            receipt=subclass,
        )
        invalid_values: tuple[tuple[str, object], ...] = (
            ("root", object()),
            ("source_locator", None),
            ("version", 11),
            ("auth_policy", []),
            ("digest", "not-a-digest"),
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(subclass_invocation),
            CodexReceiptRemovalBlockReason.INVALID_RECEIPT,
        )
        for field, invalid_value in invalid_values:
            with self.subTest(field=field):
                state = dict(object.__getattribute__(base, "__dict__"))
                state[field] = invalid_value
                candidate = CodexRegistrationReceipt.model_construct(**state)
                invocation = CodexReceiptRemovalInvocation.model_construct(
                    installation_id=base.installation_id,
                    root=base.root,
                    receipt=candidate,
                )
                _assert_blocked(
                    self,
                    build_codex_receipt_removal_request(invocation),
                    CodexReceiptRemovalBlockReason.INVALID_RECEIPT,
                )

    def test_R4_valid_serialized_reload_is_accepted_as_persisted_identity(self) -> None:
        original = _invocation()
        reloaded = CodexReceiptRemovalInvocation.model_validate_json(original.model_dump_json())
        ready = _assert_ready(self, build_codex_receipt_removal_request(reloaded))
        self.assertEqual(original.receipt.digest.value, ready.receipt.digest.value)

    def test_R5_subclass_traps_are_rejected_without_descriptor_equality_or_serialization(self) -> None:
        base = _receipt()
        trapped_receipt = _ReceiptSubclass.model_construct(**object.__getattribute__(base, "__dict__"))
        trapped_invocation = _InvocationSubclass.model_construct(
            installation_id=base.installation_id,
            root=base.root,
            receipt=trapped_receipt,
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(trapped_invocation),
            CodexReceiptRemovalBlockReason.INVALID_INVOCATION,
        )

    def test_R6_reverse_receipt_identity_gate_mutates_then_restores_exact_serialized_bytes(self) -> None:
        original = _invocation()
        original_bytes = original.model_dump_json()
        mutated = _invocation(
            installation_id=InstallationId(value="installation-00000000000005c2")
        )
        _assert_blocked(
            self,
            build_codex_receipt_removal_request(mutated),
            CodexReceiptRemovalBlockReason.RECEIPT_MISMATCH,
        )
        restored = CodexReceiptRemovalInvocation.model_validate_json(original_bytes)
        _assert_ready(self, build_codex_receipt_removal_request(restored))
        self.assertEqual(original_bytes, restored.model_dump_json())

    def test_R6_reverse_source_mapping_mutates_then_restores_exact_serialized_bytes(self) -> None:
        original = _receipt()
        original_bytes = original.model_dump_json()
        changed = _receipt(source_locator=OwnedRelativePath(value="marketplaces/other-source"))
        changed_result = build_codex_receipt_removal_request(_invocation(receipt=changed))
        changed_ready = _assert_ready(self, changed_result)
        self.assertEqual("marketplaces/other-source", changed_ready.request.manifest.marketplace_source.value)
        restored = CodexRegistrationReceipt.model_validate_json(original_bytes)
        restored_ready = _assert_ready(
            self, build_codex_receipt_removal_request(_invocation(receipt=restored))
        )
        self.assertEqual(original.source_locator.value, restored_ready.request.manifest.marketplace_source.value)
        self.assertEqual(original_bytes, restored.model_dump_json())

    def test_R6_reverse_plugin_mapping_mutates_then_restores_exact_serialized_bytes(self) -> None:
        original = _receipt()
        original_bytes = original.model_dump_json()
        changed = _receipt(plugin_name=CodexPluginName(value="other-plugin"))
        changed_ready = _assert_ready(
            self, build_codex_receipt_removal_request(_invocation(receipt=changed))
        )
        self.assertEqual("other-plugin", changed_ready.request.manifest.plugin.value)
        restored = CodexRegistrationReceipt.model_validate_json(original_bytes)
        restored_ready = _assert_ready(
            self, build_codex_receipt_removal_request(_invocation(receipt=restored))
        )
        self.assertEqual(original.plugin_name.value, restored_ready.request.manifest.plugin.value)
        self.assertEqual(original_bytes, restored.model_dump_json())


if __name__ == "__main__":
    unittest.main()
