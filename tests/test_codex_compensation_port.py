"""A1-A5 TDD coverage for static Codex compensation-port admission."""

from __future__ import annotations

import unittest
from enum import Enum
from typing import NoReturn, cast

from pydantic import BaseModel, ValidationError

from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortCapability,
    CodexCompensationPortFailureReason,
    CodexCompensationPortManifest,
    CodexCompensationPortOperation,
    CodexCompensationPortOperationFailed,
    CodexCompensationPortRejectReason,
    CodexCompensationPortRejected,
    CodexCompensationPortRequest,
    CodexCompensationPortValueRejected,
    CodexCompensationPortValueRejectReason,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
    admit_codex_compensation_port,
    revalidate_codex_compensation_port_request,
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
_MANIFEST_VALUE_FIELDS = (
    "installation_id",
    "root",
    "marketplace",
    "marketplace_source",
    "plugin_id",
    "plugin",
    "version",
    "installed_locator",
    "auth_policy",
    "digest",
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


class FiniteFailurePort:
    """Admitted plain methods that return one finite failure value."""

    def __init__(self, failure: CodexCompensationPortOperationFailed) -> None:
        self.failure = failure

    def remove_plugin(self, current: CodexCompensationPortRequest) -> CodexCompensationPortOperationFailed:
        return self.failure

    def remove_marketplace(self, current: CodexCompensationPortRequest) -> CodexCompensationPortOperationFailed:
        return self.failure

    def list_plugins(self, current: CodexCompensationPortRequest) -> CodexCompensationPortOperationFailed:
        return self.failure

    def list_marketplaces(self, current: CodexCompensationPortRequest) -> CodexCompensationPortOperationFailed:
        return self.failure

    def prove_installed_path_absent(
        self,
        current: CodexCompensationPortRequest,
    ) -> CodexCompensationPortOperationFailed:
        return self.failure


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


class _TrapSurface(str, Enum):
    """The four caller-controlled class surfaces forbidden during admission."""

    CANDIDATE_CLASS = "candidate_class"
    METACLASS_MRO = "metaclass_mro"
    METACLASS_DICTIONARY = "metaclass_dictionary"
    METACLASS_EQUALITY = "metaclass_equality"


class _TrapRead:
    """Records a forbidden metadata read before raising its exact failure type."""

    def __init__(self, failure_type: type[BaseException]) -> None:
        self.failure_type = failure_type
        self.read_count = 0

    def fail(self) -> NoReturn:
        self.read_count += 1
        raise self.failure_type("caller metadata was read")


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


def _trapped_candidate(
    surface: _TrapSurface,
    failure_type: type[BaseException],
) -> tuple[object, _TrapRead]:
    """Build a valid adapter whose one unsafe metadata path raises on access."""

    trap = _TrapRead(failure_type)
    if surface is _TrapSurface.CANDIDATE_CLASS:
        def candidate_class_property(instance: object) -> object:
            trap.fail()

        candidate_type = type(
            "CandidateClassTrapPort",
            (ValidPort,),
            {"__class__": property(candidate_class_property)},
        )
        return candidate_type(), trap
    if surface is _TrapSurface.METACLASS_EQUALITY:
        def metaclass_equality(left: object, right: object) -> bool:
            trap.fail()

        metaclass = type(
            "EqualityTrapMetaclass",
            (type,),
            {"__eq__": metaclass_equality},
        )
    else:
        def metaclass_property(owner: object) -> object:
            trap.fail()

        member_name = "__mro__"
        if surface is _TrapSurface.METACLASS_DICTIONARY:
            member_name = "__dict__"
        metaclass = type(
            "DescriptorTrapMetaclass",
            (type,),
            {member_name: property(metaclass_property)},
        )
    candidate_type = metaclass("MetaclassTrapPort", (ValidPort,), {})
    return candidate_type(), trap


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


class _RequestProtocolTrap:
    """Raises if revalidation touches a caller-controlled protocol."""

    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("request protocol was invoked")

    def __eq__(self, other: object) -> bool:
        self._raise()

    def __hash__(self) -> int:
        self._raise()

    def __str__(self) -> str:
        self._raise()

    def __repr__(self) -> str:
        self._raise()

    def model_dump(self) -> object:
        self._raise()


class CodexCompensationPortTests(unittest.TestCase):
    def test_t1_absent_false_ordinary_constructor_is_a_valid_truth_state(self) -> None:
        proof = CodexInstalledPathAbsenceProof(manifest=manifest(), absent=False)
        self.assertFalse(proof.absent)

    def test_t2_exact_true_false_construct_and_round_trip_as_bools(self) -> None:
        for absent in (True, False):
            with self.subTest(absent=absent):
                proof = CodexInstalledPathAbsenceProof(manifest=manifest(), absent=absent)
                self.assertIs(type(proof.absent), bool)
                reloaded = CodexInstalledPathAbsenceProof.model_validate_json(proof.model_dump_json())
                self.assertIs(type(reloaded.absent), bool)
                self.assertEqual(absent, reloaded.absent)
                self.assertEqual(proof.manifest.model_dump(), reloaded.manifest.model_dump())

    def test_t3_non_bool_truth_cells_fail_ordinary_validation(self) -> None:
        invalid_values: tuple[object, ...] = (0, 1, "true", None, [], {}, (True,))
        for invalid_value in invalid_values:
            with self.subTest(value_type=type(invalid_value).__name__):
                with self.assertRaises(ValidationError):
                    CodexInstalledPathAbsenceProof(
                        manifest=manifest(),
                        absent=cast(bool, invalid_value),
                    )

    def test_q1_request_revalidation_has_one_closed_finite_rejection(self) -> None:
        result = revalidate_codex_compensation_port_request(None)
        if not isinstance(result, CodexCompensationPortValueRejected):
            raise AssertionError(f"expected finite revalidation rejection, received {result}")
        self.assertEqual((CodexCompensationPortValueRejectReason.INVALID_REQUEST,), tuple(CodexCompensationPortValueRejectReason))
        self.assertEqual("INVALID_VALUE", result.status)
        self.assertIs(CodexCompensationPortValueRejectReason.INVALID_REQUEST, result.reason)
        self.assertEqual({"status", "reason"}, set(result.model_dump()))

    def test_q2_revalidation_rebuilds_every_request_node_without_original_identity(self) -> None:
        original = request()
        result = revalidate_codex_compensation_port_request(original)
        if type(result) is not CodexCompensationPortRequest:
            raise AssertionError(f"expected rebuilt request, received {result}")
        rebuilt = result
        self.assertEqual(original.model_dump(), rebuilt.model_dump())
        self.assertIsNot(original, rebuilt)
        self.assertIsNot(original.manifest, rebuilt.manifest)
        self.assertIsNot(original.manifest.installation_id, rebuilt.manifest.installation_id)
        self.assertIsNot(original.manifest.root, rebuilt.manifest.root)
        self.assertIsNot(original.manifest.marketplace, rebuilt.manifest.marketplace)
        self.assertIsNot(original.manifest.marketplace_source, rebuilt.manifest.marketplace_source)
        self.assertIsNot(original.manifest.plugin_id, rebuilt.manifest.plugin_id)
        self.assertIsNot(original.manifest.plugin, rebuilt.manifest.plugin)
        self.assertIsNot(original.manifest.version, rebuilt.manifest.version)
        self.assertIsNot(original.manifest.installed_locator, rebuilt.manifest.installed_locator)
        self.assertIsNot(original.manifest.auth_policy, rebuilt.manifest.auth_policy)
        self.assertIsNot(original.manifest.digest, rebuilt.manifest.digest)

    def test_q3_raw_subclass_constructed_invalid_and_recursive_injected_values_reject(self) -> None:
        class RequestSubclass(CodexCompensationPortRequest):
            pass

        invalid_values: tuple[object, ...] = (
            None,
            "request",
            (),
            [],
            {},
            RequestSubclass(manifest=manifest()),
            CodexCompensationPortRequest.model_construct(),
            CodexCompensationPortRequest.model_construct(manifest=CodexCompensationPortManifest.model_construct()),
            object.__new__(CodexCompensationPortRequest),
        )
        for invalid_value in invalid_values:
            with self.subTest(kind=type(invalid_value).__name__):
                self._assert_value_rejected(revalidate_codex_compensation_port_request(invalid_value))

        for field_name in _MANIFEST_VALUE_FIELDS:
            with self.subTest(nested_type=field_name):
                nested_invalid = request()
                manifest_state = object.__getattribute__(nested_invalid.manifest, "__dict__")
                manifest_state[field_name] = object()
                self._assert_value_rejected(revalidate_codex_compensation_port_request(nested_invalid))

        for field_name in _MANIFEST_VALUE_FIELDS:
            with self.subTest(constructed_nested_type=field_name):
                constructed_nested = request()
                manifest_state = object.__getattribute__(constructed_nested.manifest, "__dict__")
                original_value = manifest_state[field_name]
                if not isinstance(original_value, BaseModel):
                    raise AssertionError("test fixture lost its exact nested model")
                manifest_state[field_name] = type(original_value).model_construct()
                self._assert_value_rejected(revalidate_codex_compensation_port_request(constructed_nested))

        for state_node in ("request", "manifest", *_MANIFEST_VALUE_FIELDS):
            with self.subTest(injected_state_node=state_node):
                injected = request()
                if state_node == "request":
                    node: object = injected
                elif state_node == "manifest":
                    node = injected.manifest
                else:
                    node = object.__getattribute__(injected.manifest, state_node)
                object.__getattribute__(node, "__dict__")["injected"] = "state"
                self._assert_value_rejected(revalidate_codex_compensation_port_request(injected))

    def test_q4_revalidation_never_invokes_raw_or_constructed_request_protocols(self) -> None:
        raw_trap = _RequestProtocolTrap()
        self._assert_value_rejected(revalidate_codex_compensation_port_request(raw_trap))
        self.assertEqual(0, raw_trap.invocation_count)

        nested_trap = _RequestProtocolTrap()
        constructed = CodexCompensationPortRequest.model_construct(manifest=nested_trap)
        self._assert_value_rejected(revalidate_codex_compensation_port_request(constructed))
        self.assertEqual(0, nested_trap.invocation_count)

    def test_q6_outer_state_gate_rejects_injected_request_state(self) -> None:
        current = request()
        object.__getattribute__(current, "__dict__")["injected"] = "state"
        self._assert_value_rejected(revalidate_codex_compensation_port_request(current))

    def test_q6_nested_state_gate_rejects_injected_value_state(self) -> None:
        current = request()
        object.__getattribute__(current.manifest.digest, "__dict__")["injected"] = "state"
        self._assert_value_rejected(revalidate_codex_compensation_port_request(current))

    def test_a1_plain_methods_admit_a_frozen_capability_and_execute_only_after_admission(self) -> None:
        adapter = ValidPort()
        result = admit_codex_compensation_port(adapter)
        if not isinstance(result, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {result}")
        self.assertEqual([], adapter.calls)
        current = request()
        self.assertEqual("REMOVED", result.remove_plugin(current).status)
        self.assertEqual("REMOVED", result.remove_marketplace(current).status)
        plugins = result.list_plugins(current)
        if not isinstance(plugins, CodexPluginList):
            raise AssertionError("expected exact plugin-list result")
        self.assertEqual((), plugins.installed)
        marketplaces = result.list_marketplaces(current)
        if not isinstance(marketplaces, CodexMarketplaceList):
            raise AssertionError("expected exact marketplace-list result")
        self.assertEqual((), marketplaces.marketplaces)
        path_proof = result.prove_installed_path_absent(current)
        if not isinstance(path_proof, CodexInstalledPathAbsenceProof):
            raise AssertionError("expected exact installed-path absence result")
        self.assertTrue(path_proof.absent)
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

    def test_r2_all_candidate_and_metaclass_traps_remain_unread(self) -> None:
        surfaces: tuple[_TrapSurface, ...] = (
            _TrapSurface.CANDIDATE_CLASS,
            _TrapSurface.METACLASS_MRO,
            _TrapSurface.METACLASS_DICTIONARY,
            _TrapSurface.METACLASS_EQUALITY,
        )
        failure_types: tuple[type[BaseException], ...] = (
            RuntimeError,
            MemoryError,
            KeyboardInterrupt,
            SystemExit,
        )
        for surface in surfaces:
            for failure_type in failure_types:
                with self.subTest(surface=surface.value, failure=failure_type.__name__):
                    candidate, trap = _trapped_candidate(surface, failure_type)
                    result = admit_codex_compensation_port(candidate)
                    if not isinstance(result, CodexCompensationPortCapability):
                        raise AssertionError(f"expected capability, received {result}")
                    self.assertEqual(0, trap.read_count)

    def test_a4_invalid_candidate_values_and_unrelated_class_members_reject_or_preserve_admission(self) -> None:
        invalid_candidates: tuple[object, ...] = (None, "", "   ", (), [], {})
        for candidate in invalid_candidates:
            with self.subTest(candidate=type(candidate).__name__):
                self._assert_rejected(
                    admit_codex_compensation_port(candidate),
                    CodexCompensationPortRejectReason.INVALID_CANDIDATE,
                )
        unrelated = _DescriptorTrap()

        class ExtraMemberPort(ValidPort):
            unrelated_member = unrelated

        result = admit_codex_compensation_port(ExtraMemberPort())
        if not isinstance(result, CodexCompensationPortCapability):
            raise AssertionError(f"expected capability, received {result}")
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

    def test_f1_f2_f6_finite_operation_failure_is_closed_and_admitted_by_every_alias(self) -> None:
        self.assertEqual(
            (
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
            ),
            tuple(CodexCompensationPortOperation),
        )
        self.assertEqual(
            (
                CodexCompensationPortFailureReason.REQUEST_INVALID,
                CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            ),
            tuple(CodexCompensationPortFailureReason),
        )
        cases: tuple[tuple[CodexCompensationPortOperation, str], ...] = (
            (CodexCompensationPortOperation.REMOVE_PLUGIN, "remove_plugin"),
            (CodexCompensationPortOperation.REMOVE_MARKETPLACE, "remove_marketplace"),
            (CodexCompensationPortOperation.LIST_PLUGINS, "list_plugins"),
            (CodexCompensationPortOperation.LIST_MARKETPLACES, "list_marketplaces"),
            (
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                "prove_installed_path_absent",
            ),
        )
        for operation, operation_name in cases:
            with self.subTest(operation=operation.value):
                current = request()
                failure = CodexCompensationPortOperationFailed(
                    manifest=current.manifest,
                    operation=operation,
                    status="FAILED",
                    reason=CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED,
                )
                admitted = admit_codex_compensation_port(FiniteFailurePort(failure))
                if not isinstance(admitted, CodexCompensationPortCapability):
                    raise AssertionError(f"expected admitted failure port, received {admitted}")
                if operation_name == "remove_plugin":
                    returned: object = admitted.remove_plugin(current)
                elif operation_name == "remove_marketplace":
                    returned = admitted.remove_marketplace(current)
                elif operation_name == "list_plugins":
                    returned = admitted.list_plugins(current)
                elif operation_name == "list_marketplaces":
                    returned = admitted.list_marketplaces(current)
                else:
                    returned = admitted.prove_installed_path_absent(current)
                self.assertIs(failure, returned)
                payload = failure.model_dump()
                self.assertEqual({"manifest", "operation", "status", "reason"}, set(payload))
                self.assertEqual("FAILED", payload["status"])
                self.assertIn("root", payload["manifest"])
                self.assertNotIn("path", payload)
                self.assertNotIn("locator", payload)
                serialized = failure.model_dump_json()
                for forbidden in ("exception", "diagnostic", "callable", "oracle"):
                    self.assertNotIn(forbidden, serialized)

    def _assert_rejected(
        self,
        result: CodexCompensationPortCapability | CodexCompensationPortRejected,
        reason: CodexCompensationPortRejectReason,
    ) -> None:
        if not isinstance(result, CodexCompensationPortRejected):
            raise AssertionError(f"expected rejection, received {result}")
        self.assertEqual("INVALID_PORT", result.status)
        self.assertIs(reason, result.reason)

    def _assert_value_rejected(self, result: object) -> None:
        if type(result) is not CodexCompensationPortValueRejected:
            raise AssertionError(f"expected finite value rejection, received {result}")
        rejected = result
        self.assertEqual("INVALID_VALUE", rejected.status)
        self.assertIs(CodexCompensationPortValueRejectReason.INVALID_REQUEST, rejected.reason)


if __name__ == "__main__":
    unittest.main()
