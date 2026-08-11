"""A1-A5 TDD coverage for static Codex compensation-port admission."""

from __future__ import annotations

import unittest

from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortCapability,
    CodexCompensationPortManifest,
    CodexCompensationPortRejectReason,
    CodexCompensationPortRejected,
    CodexCompensationPortRequest,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
    admit_codex_compensation_port,
)
from library.local_orchestration.codex_registration_contracts import CodexAuthPolicy, CodexPluginId
from library.local_orchestration.contracts import ArtifactDigest, CANONICAL_INSTALL_ROOT, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import CodexCliVersion, CodexMarketplaceList, CodexMarketplaceName, CodexPluginList, CodexPluginName


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

_OPERATION_NAMES = (
    "remove_plugin",
    "remove_marketplace",
    "list_plugins",
    "list_marketplaces",
    "prove_installed_path_absent",
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


def request() -> CodexCompensationPortRequest:
    return CodexCompensationPortRequest(manifest=manifest())


def plugin_removal(current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
    return CodexPluginRemovalProof(manifest=current.manifest, status="REMOVED")


def marketplace_removal(current: CodexCompensationPortRequest) -> CodexMarketplaceRemovalProof:
    return CodexMarketplaceRemovalProof(manifest=current.manifest, status="REMOVED")


def plugin_list(current: CodexCompensationPortRequest) -> CodexPluginList:
    return CodexPluginList(installed=(), available=())


def marketplace_list(current: CodexCompensationPortRequest) -> CodexMarketplaceList:
    return CodexMarketplaceList(marketplaces=())


def path_absence(current: CodexCompensationPortRequest) -> CodexInstalledPathAbsenceProof:
    return CodexInstalledPathAbsenceProof(manifest=current.manifest, absent=True)


class ValidPort:
    """Plain instance methods are the only admitted adapter surface."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def remove_plugin(self, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
        self.calls.append("remove_plugin")
        return plugin_removal(current)

    def remove_marketplace(self, current: CodexCompensationPortRequest) -> CodexMarketplaceRemovalProof:
        self.calls.append("remove_marketplace")
        return marketplace_removal(current)

    def list_plugins(self, current: CodexCompensationPortRequest) -> CodexPluginList:
        self.calls.append("list_plugins")
        return plugin_list(current)

    def list_marketplaces(self, current: CodexCompensationPortRequest) -> CodexMarketplaceList:
        self.calls.append("list_marketplaces")
        return marketplace_list(current)

    def prove_installed_path_absent(self, current: CodexCompensationPortRequest) -> CodexInstalledPathAbsenceProof:
        self.calls.append("prove_installed_path_absent")
        return path_absence(current)


class _DescriptorTrap:
    def __init__(self) -> None:
        self.read_count = 0

    def __get__(self, instance: object, owner: type[object]) -> object:
        self.read_count += 1
        raise RuntimeError("descriptor was read")


class _PerInstanceCallable:
    def __call__(self, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
        raise AssertionError("per-instance callable was invoked")


class _MetadataTrap:
    def __getattribute__(self, name: str) -> object:
        raise RuntimeError("function metadata was read")


def _signature_metadata_trap(self: object, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
    raise AssertionError("metadata-trapped function was invoked")


object.__setattr__(_signature_metadata_trap, "__signature__", _MetadataTrap())
object.__setattr__(_signature_metadata_trap, "__wrapped__", _MetadataTrap())


def _plain_method(self: object, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
    raise AssertionError("invalid adapter operation was invoked")


def _property_value(self: object) -> CodexPluginRemovalProof:
    raise AssertionError("property operation was invoked")


def _zero_request(self: object) -> CodexPluginRemovalProof:
    raise AssertionError("zero-request operation was invoked")


def _two_requests(
    self: object,
    first: CodexCompensationPortRequest,
    second: CodexCompensationPortRequest,
) -> CodexPluginRemovalProof:
    raise AssertionError("two-request operation was invoked")


def _variadic(self: object, current: CodexCompensationPortRequest, *extra: object) -> CodexPluginRemovalProof:
    raise AssertionError("variadic operation was invoked")


def _required_keyword(self: object, current: CodexCompensationPortRequest, *, marker: str) -> CodexPluginRemovalProof:
    raise AssertionError("keyword-only operation was invoked")


def _defaulted(self: object, current: CodexCompensationPortRequest = request()) -> CodexPluginRemovalProof:
    raise AssertionError("defaulted operation was invoked")


def _adapter_with(operation_name: str, replacement: object, *, present: bool = True) -> object:
    members: dict[str, object] = {name: _plain_method for name in _OPERATION_NAMES}
    if present:
        members[operation_name] = replacement
    else:
        del members[operation_name]
    adapter_type = type("AdversarialPort", (), members)
    return adapter_type()


class _ReadTrapPort:
    def __getattribute__(self, name: str) -> object:
        raise RuntimeError("candidate attribute was read")

    def remove_plugin(self, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
        raise AssertionError("candidate operation was invoked")

    def remove_marketplace(self, current: CodexCompensationPortRequest) -> CodexMarketplaceRemovalProof:
        raise AssertionError("candidate operation was invoked")

    def list_plugins(self, current: CodexCompensationPortRequest) -> CodexPluginList:
        raise AssertionError("candidate operation was invoked")

    def list_marketplaces(self, current: CodexCompensationPortRequest) -> CodexMarketplaceList:
        raise AssertionError("candidate operation was invoked")

    def prove_installed_path_absent(self, current: CodexCompensationPortRequest) -> CodexInstalledPathAbsenceProof:
        raise AssertionError("candidate operation was invoked")


class _ExplodingPort(ValidPort):
    def __init__(self, failure: BaseException) -> None:
        super().__init__()
        self.failure = failure

    def remove_plugin(self, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
        raise self.failure


class CodexCompensationPortTests(unittest.TestCase):
    def test_a1_plain_methods_admit_a_frozen_capability_and_execute_only_after_admission(self) -> None:
        adapter = ValidPort()
        result = admit_codex_compensation_port(adapter)
        if not isinstance(result, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {result}")
        self.assertEqual([], adapter.calls)
        current = request()
        self.assertEqual("REMOVED", result.remove_plugin(current).status)
        self.assertEqual("REMOVED", result.remove_marketplace(current).status)
        self.assertEqual((), result.list_plugins(current).installed)
        self.assertEqual((), result.list_marketplaces(current).marketplaces)
        self.assertTrue(result.prove_installed_path_absent(current).absent)
        self.assertEqual(list(_OPERATION_NAMES), adapter.calls)
        self.assertEqual("ADMITTED", result.metadata().status)

    def test_a2_every_operation_shape_rejects_without_descriptor_or_operation_calls(self) -> None:
        cases: tuple[tuple[str, object, bool, CodexCompensationPortRejectReason], ...] = (
            ("missing", _plain_method, False, CodexCompensationPortRejectReason.MISSING_OPERATION),
            ("non_function", 7, True, CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION),
            ("property", property(_property_value), True, CodexCompensationPortRejectReason.PROPERTY_OPERATION),
            ("static", staticmethod(plugin_removal), True, CodexCompensationPortRejectReason.STATIC_METHOD_OPERATION),
            ("class", classmethod(_plain_method), True, CodexCompensationPortRejectReason.CLASS_METHOD_OPERATION),
            ("descriptor", _DescriptorTrap(), True, CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION),
            ("builtin", len, True, CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION),
            ("zero", _zero_request, True, CodexCompensationPortRejectReason.ZERO_REQUEST_ARGUMENTS),
            ("two", _two_requests, True, CodexCompensationPortRejectReason.TWO_REQUEST_ARGUMENTS),
            ("variadic", _variadic, True, CodexCompensationPortRejectReason.VARIADIC_ARGUMENTS),
            ("keyword", _required_keyword, True, CodexCompensationPortRejectReason.REQUIRED_KEYWORD_ARGUMENTS),
            ("defaulted", _defaulted, True, CodexCompensationPortRejectReason.DEFAULTED_ARGUMENTS),
        )
        for name in _OPERATION_NAMES:
            for shape, replacement, present, reason in cases:
                with self.subTest(operation=name, shape=shape):
                    candidate = _adapter_with(name, replacement, present=present)
                    result = admit_codex_compensation_port(candidate)
                    self._assert_rejected(result, reason)
        for name in _OPERATION_NAMES:
            with self.subTest(operation=name, shape="per_instance"):
                candidate = _adapter_with(name, _plain_method, present=False)
                object.__setattr__(candidate, name, _PerInstanceCallable())
                result = admit_codex_compensation_port(candidate)
                self._assert_rejected(result, CodexCompensationPortRejectReason.MISSING_OPERATION)

    def test_a3_candidate_descriptor_and_signature_traps_are_not_read(self) -> None:
        read_trap = _ReadTrapPort()
        admitted = admit_codex_compensation_port(read_trap)
        if not isinstance(admitted, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {admitted}")
        descriptor_members: dict[str, object] = {name: _DescriptorTrap() for name in _OPERATION_NAMES}
        descriptor_type = type("DescriptorPort", (), descriptor_members)
        descriptor_result = admit_codex_compensation_port(descriptor_type())
        self._assert_rejected(descriptor_result, CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION)
        for descriptor in descriptor_members.values():
            if not isinstance(descriptor, _DescriptorTrap):
                raise AssertionError("descriptor fixture lost its exact type")
            self.assertEqual(0, descriptor.read_count)
        metadata_members: dict[str, object] = {name: _plain_method for name in _OPERATION_NAMES}
        metadata_members["remove_plugin"] = _signature_metadata_trap
        metadata_type = type("MetadataPort", (), metadata_members)
        metadata_result = admit_codex_compensation_port(metadata_type())
        if not isinstance(metadata_result, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {metadata_result}")

    def test_a4_invalid_candidate_values_and_unrelated_class_members_reject_or_preserve_admission(self) -> None:
        invalid_candidates: tuple[object, ...] = (None, "", "   ", (), [], {})
        for candidate in invalid_candidates:
            with self.subTest(candidate=type(candidate).__name__):
                self._assert_rejected(
                    admit_codex_compensation_port(candidate),
                    CodexCompensationPortRejectReason.INVALID_CANDIDATE,
                )
        class ExtraMemberPort(ValidPort):
            unrelated = _DescriptorTrap()

        result = admit_codex_compensation_port(ExtraMemberPort())
        if not isinstance(result, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {result}")
        unrelated = type.__getattribute__(ExtraMemberPort, "__dict__")["unrelated"]
        if not isinstance(unrelated, _DescriptorTrap):
            raise AssertionError("unrelated fixture lost its exact type")
        self.assertEqual(0, unrelated.read_count)
        admitted = admit_codex_compensation_port(ValidPort())
        if not isinstance(admitted, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {admitted}")
        self._assert_rejected(
            admit_codex_compensation_port(admitted),
            CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION,
        )
        malformed_capability = object.__new__(CodexCompensationPortCapability)
        self._assert_rejected(
            admit_codex_compensation_port(malformed_capability),
            CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION,
        )

    def test_a5_bound_operations_propagate_actual_failures_and_metadata_stays_opaque(self) -> None:
        for failure in (RuntimeError("operation failure"), MemoryError(), KeyboardInterrupt(), SystemExit()):
            with self.subTest(failure=type(failure).__name__):
                result = admit_codex_compensation_port(_ExplodingPort(failure))
                if not isinstance(result, CodexCompensationPortCapability):
                    raise AssertionError(f"expected capability, received {result}")
                with self.assertRaises(type(failure)):
                    result.remove_plugin(request())
        rejected = admit_codex_compensation_port(None)
        self._assert_rejected(rejected, CodexCompensationPortRejectReason.INVALID_CANDIDATE)
        if not isinstance(rejected, CodexCompensationPortRejected):
            raise AssertionError(f"expected rejection, received {rejected}")
        admitted = admit_codex_compensation_port(ValidPort())
        if not isinstance(admitted, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {admitted}")
        payloads = (rejected.model_dump_json(), admitted.metadata().model_dump_json())
        for payload in payloads:
            for forbidden in ("exception", "candidate", "remove_plugin", "absolute", "receipt", "success"):
                with self.subTest(payload=payload, forbidden=forbidden):
                    self.assertNotIn(forbidden, payload)

    def _assert_rejected(
        self,
        result: CodexCompensationPortCapability | CodexCompensationPortRejected,
        reason: CodexCompensationPortRejectReason,
    ) -> None:
        if not isinstance(result, CodexCompensationPortRejected):
            raise AssertionError(f"expected rejection, received {result}")
        self.assertEqual("INVALID_PORT", result.status)
        self.assertIs(reason, result.reason)


if __name__ == "__main__":
    unittest.main()
