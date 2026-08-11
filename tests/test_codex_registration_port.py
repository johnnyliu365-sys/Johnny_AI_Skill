"""A1-A7 closure for the Codex registration port boundary."""

from __future__ import annotations

import copy
from enum import Enum
import ntpath
from typing import NoReturn, cast
import unittest

from pydantic import ValidationError

from library.local_orchestration import admit_codex_registration_port as exported_admit
import library.local_orchestration.codex_registration_port as registration_port
from library.local_orchestration.codex_command_attempts import (
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
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
    CodexRegistrationProof,
    CodexRegistrationProofRequest,
)
from library.local_orchestration.codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexFreshPreflightRejected,
    CodexFreshPreflightResult,
    CodexMarketplaceAddResult,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddResult,
    CodexPluginAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortCapability,
    CodexRegistrationPortRejectReason,
    CodexRegistrationPortRejected,
    CodexRegistrationPortRequest,
    CodexRegistrationPortValueRejectReason,
    CodexRegistrationPortValueRejected,
    admit_codex_registration_port,
    revalidate_fresh_preflight_result,
    revalidate_marketplace_add_result,
    revalidate_plugin_add_result,
    revalidate_registration_port_request,
)
from library.local_orchestration.contracts import (
    CANONICAL_INSTALL_ROOT,
    ArtifactDigest,
    InstallRoot,
    InstallationId,
    OwnedRelativePath,
)
from library.local_orchestration.host_contracts import (
    CodexBlockReason,
    CodexCliVersion,
    CodexMarketplaceName,
    CodexPluginName,
    CodexPreflightEligible,
    CodexPreflightRequest,
)


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
OTHER_INSTALLATION = InstallationId(value="installation-fedcba9876543210")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="probe-market")
PLUGIN = CodexPluginName(value="probe-plugin")
SOURCE = OwnedRelativePath(value="marketplaces/probe-market")
INSTALLED = OwnedRelativePath(value="plugins/probe-plugin")
VERSION = CodexCliVersion(value="1.2.3")
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")
OTHER_ATTEMPT = CodexRegistrationAttemptId(value="attempt-fedcba9876543210")
DIGEST = ArtifactDigest(value="a" * 64)
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")


class RequestField(str, Enum):
    PREFLIGHT = "preflight"
    ATTEMPT_ID = "attempt_id"
    EXPECTED_VERSION = "expected_version"
    SOURCE_LOCATOR = "source_locator"
    INSTALLED_LOCATOR = "installed_locator"
    DIGEST = "digest"
    EXPECTED_AUTH_POLICY = "expected_auth_policy"


class MissingValue:
    pass


class TrapCounter:
    def __init__(self) -> None:
        self.count = 0

    def hit(self) -> None:
        self.count += 1


class PlainTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("caller trap invoked")

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


MISSING = MissingValue()


def preflight(
    installation_id: InstallationId = INSTALLATION,
    marketplace: CodexMarketplaceName = MARKETPLACE,
    plugin: CodexPluginName = PLUGIN,
    source: OwnedRelativePath = SOURCE,
) -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=installation_id,
        root=ROOT,
        marketplace=marketplace,
        plugin=plugin,
        marketplace_source=source,
    )


def port_request(
    current_preflight: CodexPreflightRequest | None = None,
    attempt_id: CodexRegistrationAttemptId = ATTEMPT,
    expected_version: CodexCliVersion = VERSION,
    source_locator: OwnedRelativePath = SOURCE,
    installed_locator: OwnedRelativePath = INSTALLED,
    digest: ArtifactDigest = DIGEST,
    expected_auth_policy: CodexAuthPolicy = AUTH_POLICY,
) -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=preflight() if current_preflight is None else current_preflight,
        attempt_id=attempt_id,
        expected_version=expected_version,
        source_locator=source_locator,
        installed_locator=installed_locator,
        digest=digest,
        expected_auth_policy=expected_auth_policy,
    )


def malformed_request(field: RequestField, value: object) -> CodexRegistrationPortRequest:
    values: dict[str, object] = {
        "preflight": preflight(),
        "attempt_id": ATTEMPT,
        "expected_version": VERSION,
        "source_locator": SOURCE,
        "installed_locator": INSTALLED,
        "digest": DIGEST,
        "expected_auth_policy": AUTH_POLICY,
    }
    if value is MISSING:
        del values[field.value]
    else:
        values[field.value] = value
    return CodexRegistrationPortRequest.model_construct(_fields_set=set(values), **values)


def observed_path(locator: OwnedRelativePath) -> CodexObservedAbsolutePath:
    expanded_root = ntpath.expandvars(CANONICAL_INSTALL_ROOT)
    return CodexObservedAbsolutePath(value=ntpath.join(expanded_root, *locator.parts()))


def marketplace_success(
    request: CodexRegistrationPortRequest | None = None,
    observation: CodexMarketplaceAddObservation | None = None,
) -> CodexMarketplaceAddSucceeded:
    current_request = port_request() if request is None else request
    current_observation = (
        CodexMarketplaceAddObservation(
            marketplace_name=current_request.preflight.marketplace,
            installed_root=observed_path(current_request.source_locator),
            already_added=False,
        )
        if observation is None
        else observation
    )
    return CodexMarketplaceAddSucceeded(
        request=current_request,
        confirmed=CodexMarketplaceAddConfirmed(
            target=CodexCommandTarget.MARKETPLACE_ADD,
            start_state=CodexCommandStartState.STARTED,
            already_added=current_observation.already_added,
        ),
        observation=current_observation,
    )


def plugin_success(
    request: CodexRegistrationPortRequest | None = None,
    observation: CodexPluginAddObservation | None = None,
) -> CodexPluginAddSucceeded:
    current_request = port_request() if request is None else request
    current_observation = (
        CodexPluginAddObservation(
            plugin_id=CodexPluginId(value="plugin-probe-012345"),
            name=current_request.preflight.plugin,
            marketplace_name=current_request.preflight.marketplace,
            version=current_request.expected_version,
            installed_path=observed_path(current_request.installed_locator),
            auth_policy=current_request.expected_auth_policy,
        )
        if observation is None
        else observation
    )
    return CodexPluginAddSucceeded(
        request=current_request,
        confirmed=CodexPluginAddConfirmed(
            target=CodexCommandTarget.PLUGIN_ADD,
            start_state=CodexCommandStartState.STARTED,
        ),
        observation=current_observation,
    )


def fresh_result(request: CodexRegistrationPortRequest | None = None) -> CodexFreshPreflightAccepted:
    current_request = port_request() if request is None else request
    return CodexFreshPreflightAccepted(
        request=current_request,
        eligible=CodexPreflightEligible(version=current_request.expected_version),
    )


class ValidAdapter:
    def __init__(self) -> None:
        self.call_count = 0

    def fresh_preflight(self, request: CodexRegistrationPortRequest) -> CodexFreshPreflightResult:
        self.call_count += 1
        return fresh_result(request)

    def add_marketplace(self, request: CodexRegistrationPortRequest) -> CodexMarketplaceAddResult:
        self.call_count += 1
        return marketplace_success(request)

    def add_plugin(self, request: CodexRegistrationPortRequest) -> CodexPluginAddResult:
        self.call_count += 1
        return plugin_success(request)

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        self.call_count += 1
        raise AssertionError("proof must not execute during admission")


class OtherOperations:
    def add_marketplace(self, request: CodexRegistrationPortRequest) -> CodexMarketplaceAddResult:
        raise AssertionError("must not execute")

    def add_plugin(self, request: CodexRegistrationPortRequest) -> CodexPluginAddResult:
        raise AssertionError("must not execute")

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise AssertionError("must not execute")


class MissingOperationCandidate(OtherOperations):
    pass


class PropertyCandidate(OtherOperations):
    @property
    def fresh_preflight(self) -> CodexFreshPreflightResult:
        raise AssertionError("property descriptor must not execute")


class StaticMethodCandidate(OtherOperations):
    @staticmethod
    def fresh_preflight(request: CodexRegistrationPortRequest) -> CodexFreshPreflightResult:
        return fresh_result(request)


class ClassMethodCandidate(OtherOperations):
    @classmethod
    def fresh_preflight(cls, request: CodexRegistrationPortRequest) -> CodexFreshPreflightResult:
        return fresh_result(request)


class NonFunctionCandidate(OtherOperations):
    fresh_preflight = object()


class ZeroRequestCandidate(OtherOperations):
    def fresh_preflight(self) -> CodexFreshPreflightResult:
        return fresh_result()


class TwoRequestCandidate(OtherOperations):
    def fresh_preflight(
        self,
        request: CodexRegistrationPortRequest,
        other: CodexRegistrationPortRequest,
    ) -> CodexFreshPreflightResult:
        return fresh_result(request)


class DefaultRequestCandidate(OtherOperations):
    def fresh_preflight(
        self,
        request: CodexRegistrationPortRequest = port_request(),
    ) -> CodexFreshPreflightResult:
        return fresh_result(request)


class VariadicCandidate(OtherOperations):
    def fresh_preflight(
        self,
        request: CodexRegistrationPortRequest,
        *extra: object,
    ) -> CodexFreshPreflightResult:
        return fresh_result(request)


class KeywordOnlyCandidate(OtherOperations):
    def fresh_preflight(
        self,
        request: CodexRegistrationPortRequest,
        *,
        required: bool,
    ) -> CodexFreshPreflightResult:
        return fresh_result(request)


class InheritedAdapter(ValidAdapter):
    pass


class TrapDescriptor:
    def __init__(self) -> None:
        self.counter = TrapCounter()

    def __get__(self, instance: object, owner: type[object]) -> NoReturn:
        self.counter.hit()
        raise RuntimeError("descriptor invoked")


DESCRIPTOR = TrapDescriptor()


class DescriptorCandidate(OtherOperations):
    fresh_preflight = DESCRIPTOR


LOOKUP_COUNTER = TrapCounter()


class LookupTrapAdapter(ValidAdapter):
    def __getattribute__(self, name: str) -> object:
        LOOKUP_COUNTER.hit()
        raise RuntimeError("candidate lookup invoked")


META_COUNTER = TrapCounter()


class TrapMeta(type):
    def __getattribute__(cls, name: str) -> object:
        META_COUNTER.hit()
        raise RuntimeError("metaclass lookup invoked")


class MetaTrapAdapter(ValidAdapter, metaclass=TrapMeta):
    pass


BODY_COUNTER = TrapCounter()


class ProcessTrapAdapter:
    def fresh_preflight(self, request: CodexRegistrationPortRequest) -> CodexFreshPreflightResult:
        BODY_COUNTER.hit()
        raise RuntimeError("must not execute")

    def add_marketplace(self, request: CodexRegistrationPortRequest) -> CodexMarketplaceAddResult:
        BODY_COUNTER.hit()
        raise MemoryError("must not execute")

    def add_plugin(self, request: CodexRegistrationPortRequest) -> CodexPluginAddResult:
        BODY_COUNTER.hit()
        raise KeyboardInterrupt()

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        BODY_COUNTER.hit()
        raise SystemExit()


class MetadataTrapAdapter(ValidAdapter):
    pass


METADATA_TRAP = PlainTrap()
MetadataTrapAdapter.fresh_preflight.__annotations__["request"] = METADATA_TRAP
MetadataTrapAdapter.fresh_preflight.__dict__["__signature__"] = METADATA_TRAP
MetadataTrapAdapter.fresh_preflight.__dict__["__wrapped__"] = METADATA_TRAP


DEFAULT_METADATA_TRAP = PlainTrap()


class DefaultMetadataTrapCandidate(OtherOperations):
    def fresh_preflight(
        self,
        request: CodexRegistrationPortRequest = cast(CodexRegistrationPortRequest, DEFAULT_METADATA_TRAP),
    ) -> CodexFreshPreflightResult:
        return fresh_result(request)


REPRESENTATION_COUNTER = TrapCounter()


class RepresentationTrapAdapter(ValidAdapter):
    def __repr__(self) -> NoReturn:
        REPRESENTATION_COUNTER.hit()
        raise RuntimeError("candidate representation invoked")


class CodexRegistrationPortTests(unittest.TestCase):
    def test_a1_exact_request_source_binding_and_all_49_root_shape_cells(self) -> None:
        exact = port_request()
        rebuilt = revalidate_registration_port_request(exact)
        self.assertIsInstance(rebuilt, CodexRegistrationPortRequest)
        self.assertIsNot(exact, rebuilt)
        invalid_values: tuple[tuple[str, object], ...] = (
            ("missing", MISSING),
            ("none", None),
            ("empty", ""),
            ("whitespace", " "),
            ("list", []),
            ("dict", {}),
            ("plain", PlainTrap()),
        )
        cell_count = 0
        for field in RequestField:
            for label, value in invalid_values:
                with self.subTest(field=field.value, value=label):
                    result = revalidate_registration_port_request(malformed_request(field, value))
                    self.assert_rejected(result, CodexRegistrationPortValueRejectReason.INVALID_REQUEST)
                    if isinstance(value, PlainTrap):
                        self.assertEqual(0, value.invocation_count)
                    cell_count += 1
        self.assertEqual(49, cell_count)
        foreign_source = OwnedRelativePath(value="marketplaces/other-market")
        mismatched = CodexRegistrationPortRequest.model_construct(
            preflight=preflight(),
            attempt_id=ATTEMPT,
            expected_version=VERSION,
            source_locator=foreign_source,
            installed_locator=INSTALLED,
            digest=DIGEST,
            expected_auth_policy=AUTH_POLICY,
        )
        self.assert_rejected(
            revalidate_registration_port_request(mismatched),
            CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
        )
        with self.assertRaises(ValidationError):
            CodexRegistrationPortRequest(
                preflight=preflight(),
                attempt_id=ATTEMPT,
                expected_version=VERSION,
                source_locator=foreign_source,
                installed_locator=INSTALLED,
                digest=DIGEST,
                expected_auth_policy=AUTH_POLICY,
            )

    def test_a2_exact_result_envelopes_rebuild_and_mismatches_are_finite(self) -> None:
        expected = port_request()
        fresh_cases: tuple[CodexFreshPreflightResult, ...] = (
            fresh_result(expected),
            CodexFreshPreflightRejected(request=expected, reason=CodexBlockReason.COLLISION),
        )
        for fresh_value in fresh_cases:
            fresh_rebuilt = revalidate_fresh_preflight_result(fresh_value, expected)
            self.assertIs(type(fresh_value), type(fresh_rebuilt))
            self.assertIsNot(fresh_value, fresh_rebuilt)
        marketplace_cases: tuple[CodexMarketplaceAddResult, ...] = (
            marketplace_success(expected),
            CodexRegistrationCommandFailed(
                request=expected,
                failure=CodexPreStartFailure(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    reason=CodexPreStartFailureReason.ACCESS_DENIED,
                    start_state=CodexCommandStartState.NOT_STARTED,
                ),
            ),
            CodexRegistrationCommandFailed(
                request=expected,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    reason=CodexStartedFailureReason.NONZERO_EXIT,
                    start_state=CodexCommandStartState.STARTED,
                ),
            ),
        )
        for marketplace_value in marketplace_cases:
            marketplace_rebuilt = revalidate_marketplace_add_result(marketplace_value, expected)
            self.assertIs(type(marketplace_value), type(marketplace_rebuilt))
            self.assertIsNot(marketplace_value, marketplace_rebuilt)
        plugin_cases: tuple[CodexPluginAddResult, ...] = (
            plugin_success(expected),
            CodexRegistrationCommandFailed(
                request=expected,
                failure=CodexPreStartFailure(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    reason=CodexPreStartFailureReason.EXECUTABLE_UNAVAILABLE,
                    start_state=CodexCommandStartState.NOT_STARTED,
                ),
            ),
            CodexRegistrationCommandFailed(
                request=expected,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    reason=CodexStartedFailureReason.TIMEOUT_AFTER_START,
                    start_state=CodexCommandStartState.STARTED,
                ),
            ),
        )
        for plugin_value in plugin_cases:
            plugin_rebuilt = revalidate_plugin_add_result(plugin_value, expected)
            self.assertIs(type(plugin_value), type(plugin_rebuilt))
            self.assertIsNot(plugin_value, plugin_rebuilt)
        alternate_marketplace = CodexMarketplaceName(value="other-market")
        alternate_source = OwnedRelativePath(value="marketplaces/other-market")
        alternate_requests = (
            port_request(current_preflight=preflight(installation_id=OTHER_INSTALLATION)),
            port_request(attempt_id=OTHER_ATTEMPT),
            port_request(expected_version=CodexCliVersion(value="9.9.9")),
            port_request(
                current_preflight=preflight(
                    marketplace=alternate_marketplace,
                    source=alternate_source,
                ),
                source_locator=alternate_source,
            ),
            port_request(installed_locator=OwnedRelativePath(value="plugins/other-plugin")),
            port_request(digest=ArtifactDigest(value="b" * 64)),
            port_request(expected_auth_policy=CodexAuthPolicy(value="other-policy")),
        )
        for alternate in alternate_requests:
            with self.subTest(bound_request=alternate):
                self.assert_rejected(
                    revalidate_fresh_preflight_result(fresh_result(alternate), expected),
                    CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
                )
                self.assert_rejected(
                    revalidate_marketplace_add_result(marketplace_success(alternate), expected),
                    CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
                )
                self.assert_rejected(
                    revalidate_plugin_add_result(plugin_success(alternate), expected),
                    CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
                )
        wrong_fresh_version = CodexFreshPreflightAccepted(
            request=expected,
            eligible=CodexPreflightEligible(version=CodexCliVersion(value="9.9.9")),
        )
        self.assert_rejected(
            revalidate_fresh_preflight_result(wrong_fresh_version, expected),
            CodexRegistrationPortValueRejectReason.VERSION_MISMATCH,
        )
        wrong_plugin_version = plugin_success(
            expected,
            CodexPluginAddObservation(
                plugin_id=CodexPluginId(value="plugin-probe-012345"),
                name=PLUGIN,
                marketplace_name=MARKETPLACE,
                version=CodexCliVersion(value="9.9.9"),
                installed_path=observed_path(INSTALLED),
                auth_policy=AUTH_POLICY,
            ),
        )
        self.assert_rejected(
            revalidate_plugin_add_result(wrong_plugin_version, expected),
            CodexRegistrationPortValueRejectReason.VERSION_MISMATCH,
        )
        wrong_marketplace_path = marketplace_success(
            expected,
            CodexMarketplaceAddObservation(
                marketplace_name=MARKETPLACE,
                installed_root=CodexObservedAbsolutePath(
                    value=observed_path(SOURCE).value + "-foreign",
                ),
                already_added=False,
            ),
        )
        self.assert_rejected(
            revalidate_marketplace_add_result(wrong_marketplace_path, expected),
            CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
        )
        plugin_mismatch_observations = (
            CodexPluginAddObservation(
                plugin_id=CodexPluginId(value="plugin-probe-012345"),
                name=CodexPluginName(value="other-plugin"),
                marketplace_name=MARKETPLACE,
                version=VERSION,
                installed_path=observed_path(INSTALLED),
                auth_policy=AUTH_POLICY,
            ),
            CodexPluginAddObservation(
                plugin_id=CodexPluginId(value="plugin-probe-012345"),
                name=PLUGIN,
                marketplace_name=CodexMarketplaceName(value="other-market"),
                version=VERSION,
                installed_path=observed_path(INSTALLED),
                auth_policy=AUTH_POLICY,
            ),
            CodexPluginAddObservation(
                plugin_id=CodexPluginId(value="plugin-probe-012345"),
                name=PLUGIN,
                marketplace_name=MARKETPLACE,
                version=VERSION,
                installed_path=CodexObservedAbsolutePath(
                    value=observed_path(INSTALLED).value + "-foreign",
                ),
                auth_policy=AUTH_POLICY,
            ),
            CodexPluginAddObservation(
                plugin_id=CodexPluginId(value="plugin-probe-012345"),
                name=PLUGIN,
                marketplace_name=MARKETPLACE,
                version=VERSION,
                installed_path=observed_path(INSTALLED),
                auth_policy=CodexAuthPolicy(value="other-policy"),
            ),
        )
        for mismatch_observation in plugin_mismatch_observations:
            self.assert_rejected(
                revalidate_plugin_add_result(plugin_success(expected, mismatch_observation), expected),
                CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
            )
        malformed_values = (PlainTrap(), PlainTrap(), PlainTrap(), PlainTrap(), PlainTrap())
        malformed_fresh = CodexFreshPreflightAccepted.model_construct(
            request=expected,
            eligible=CodexPreflightEligible.model_construct(version=malformed_values[0]),
        )
        malformed_marketplace = CodexMarketplaceAddSucceeded.model_construct(
            request=expected,
            confirmed=marketplace_success(expected).confirmed,
            observation=CodexMarketplaceAddObservation.model_construct(
                marketplace_name=malformed_values[1],
                installed_root=observed_path(SOURCE),
                already_added=False,
            ),
        )
        malformed_plugin = CodexPluginAddSucceeded.model_construct(
            request=expected,
            confirmed=plugin_success(expected).confirmed,
            observation=CodexPluginAddObservation.model_construct(
                plugin_id=CodexPluginId(value="plugin-probe-012345"),
                name=PLUGIN,
                marketplace_name=MARKETPLACE,
                version=VERSION,
                installed_path=observed_path(INSTALLED),
                auth_policy=malformed_values[2],
            ),
        )
        malformed_failure = CodexRegistrationCommandFailed.model_construct(
            request=expected,
            failure=CodexPreStartFailure.model_construct(
                target=CodexCommandTarget.PLUGIN_ADD,
                reason=malformed_values[3],
                start_state=CodexCommandStartState.NOT_STARTED,
            ),
        )
        malformed_cases = (
            revalidate_fresh_preflight_result(malformed_fresh, expected),
            revalidate_marketplace_add_result(malformed_marketplace, expected),
            revalidate_plugin_add_result(malformed_plugin, expected),
            revalidate_plugin_add_result(malformed_failure, expected),
            revalidate_fresh_preflight_result(
                CodexFreshPreflightAccepted.model_construct(
                    request=malformed_request(RequestField.DIGEST, malformed_values[4]),
                    eligible=CodexPreflightEligible(version=VERSION),
                ),
                expected,
            ),
        )
        for result in malformed_cases:
            self.assert_rejected(result, CodexRegistrationPortValueRejectReason.INVALID_RESULT)
        self.assertTrue(all(value.invocation_count == 0 for value in malformed_values))
        request_dump = str(expected.model_dump())
        self.assertNotIn(observed_path(SOURCE).value, request_dump)
        self.assertEqual(
            observed_path(SOURCE).value,
            marketplace_success(expected).observation.installed_root.value,
        )

    def test_a2_wrong_operation_targets_are_rejected_exactly(self) -> None:
        expected = port_request()
        wrong_confirmation = CodexMarketplaceAddConfirmed.model_construct(
            target=CodexCommandTarget.PLUGIN_ADD,
            start_state=CodexCommandStartState.STARTED,
            already_added=False,
        )
        wrong_success = CodexMarketplaceAddSucceeded.model_construct(
            request=expected,
            confirmed=wrong_confirmation,
            observation=marketplace_success(expected).observation,
        )
        self.assert_rejected(
            revalidate_marketplace_add_result(wrong_success, expected),
            CodexRegistrationPortValueRejectReason.TARGET_MISMATCH,
        )
        wrong_failure = CodexRegistrationCommandFailed(
            request=expected,
            failure=CodexPreStartFailure(
                target=CodexCommandTarget.MARKETPLACE_ADD,
                reason=CodexPreStartFailureReason.ACCESS_DENIED,
                start_state=CodexCommandStartState.NOT_STARTED,
            ),
        )
        self.assert_rejected(
            revalidate_plugin_add_result(wrong_failure, expected),
            CodexRegistrationPortValueRejectReason.TARGET_MISMATCH,
        )
        wrong_plugin_confirmation = CodexPluginAddConfirmed.model_construct(
            target=CodexCommandTarget.MARKETPLACE_ADD,
            start_state=CodexCommandStartState.STARTED,
        )
        wrong_plugin_success = CodexPluginAddSucceeded.model_construct(
            request=expected,
            confirmed=wrong_plugin_confirmation,
            observation=plugin_success(expected).observation,
        )
        self.assert_rejected(
            revalidate_plugin_add_result(wrong_plugin_success, expected),
            CodexRegistrationPortValueRejectReason.TARGET_MISMATCH,
        )
        marketplace_wrong_failure = CodexRegistrationCommandFailed(
            request=expected,
            failure=CodexStartedFailure(
                target=CodexCommandTarget.PLUGIN_ADD,
                reason=CodexStartedFailureReason.NONZERO_EXIT,
                start_state=CodexCommandStartState.STARTED,
            ),
        )
        self.assert_rejected(
            revalidate_marketplace_add_result(marketplace_wrong_failure, expected),
            CodexRegistrationPortValueRejectReason.TARGET_MISMATCH,
        )

    def test_a3_private_factory_authority_and_metadata_only_admission(self) -> None:
        adapter = ValidAdapter()
        admitted = admit_codex_registration_port(adapter)
        self.assertIs(exported_admit, admit_codex_registration_port)
        self.assertIsInstance(admitted, CodexRegistrationPortCapability)
        if not isinstance(admitted, CodexRegistrationPortCapability):
            raise AssertionError("expected admitted capability")
        self.assertEqual({"status": "ADMITTED", "operation_count": 4}, admitted.metadata().model_dump())
        self.assertEqual(0, adapter.call_count)
        representation = repr(admitted)
        self.assertNotIn("fresh_preflight=<", representation)
        self.assertNotIn("\\", representation)
        fake_token = registration_port._CapabilityToken()
        with self.assertRaises(TypeError):
            CodexRegistrationPortCapability(
                fake_token,
                adapter.fresh_preflight,
                adapter.add_marketplace,
                adapter.add_plugin,
                adapter.prove,
            )
        copied_token = copy.copy(registration_port._CAPABILITY_TOKEN)
        with self.assertRaises(TypeError):
            CodexRegistrationPortCapability(
                copied_token,
                adapter.fresh_preflight,
                adapter.add_marketplace,
                adapter.add_plugin,
                adapter.prove,
            )
        forged = object.__new__(CodexRegistrationPortCapability)
        with self.assertRaises((AttributeError, TypeError)):
            forged.metadata()
        self.assertEqual(0, adapter.call_count)

    def test_a4_all_candidate_and_method_shapes_are_finite_and_inheritance_admits(self) -> None:
        cases: tuple[tuple[object, CodexRegistrationPortRejectReason], ...] = (
            (None, CodexRegistrationPortRejectReason.INVALID_CANDIDATE),
            ("", CodexRegistrationPortRejectReason.INVALID_CANDIDATE),
            (" ", CodexRegistrationPortRejectReason.INVALID_CANDIDATE),
            ([], CodexRegistrationPortRejectReason.INVALID_CANDIDATE),
            ({}, CodexRegistrationPortRejectReason.INVALID_CANDIDATE),
            ((), CodexRegistrationPortRejectReason.INVALID_CANDIDATE),
            (MissingOperationCandidate(), CodexRegistrationPortRejectReason.MISSING_OPERATION),
            (PropertyCandidate(), CodexRegistrationPortRejectReason.PROPERTY_OPERATION),
            (StaticMethodCandidate(), CodexRegistrationPortRejectReason.STATIC_METHOD_OPERATION),
            (ClassMethodCandidate(), CodexRegistrationPortRejectReason.CLASS_METHOD_OPERATION),
            (NonFunctionCandidate(), CodexRegistrationPortRejectReason.NON_PLAIN_FUNCTION),
            (ZeroRequestCandidate(), CodexRegistrationPortRejectReason.ZERO_REQUEST_ARGUMENTS),
            (TwoRequestCandidate(), CodexRegistrationPortRejectReason.TWO_REQUEST_ARGUMENTS),
            (DefaultRequestCandidate(), CodexRegistrationPortRejectReason.DEFAULTED_ARGUMENTS),
            (VariadicCandidate(), CodexRegistrationPortRejectReason.VARIADIC_ARGUMENTS),
            (KeywordOnlyCandidate(), CodexRegistrationPortRejectReason.REQUIRED_KEYWORD_ARGUMENTS),
        )
        for candidate, reason in cases:
            with self.subTest(reason=reason.value, candidate=type(candidate).__name__):
                result = admit_codex_registration_port(candidate)
                if not isinstance(result, CodexRegistrationPortRejected):
                    raise AssertionError("expected rejected candidate")
                self.assertIs(reason, result.reason)
                self.assertEqual({"status": "INVALID_PORT", "reason": reason}, result.model_dump())
        inherited = InheritedAdapter()
        self.assertIsInstance(admit_codex_registration_port(inherited), CodexRegistrationPortCapability)
        self.assertEqual(0, inherited.call_count)

    def test_a5_descriptor_candidate_metadata_and_process_traps_are_never_invoked(self) -> None:
        LOOKUP_COUNTER.count = 0
        META_COUNTER.count = 0
        BODY_COUNTER.count = 0
        DESCRIPTOR.counter.count = 0
        METADATA_TRAP.invocation_count = 0
        DEFAULT_METADATA_TRAP.invocation_count = 0
        REPRESENTATION_COUNTER.count = 0
        lookup_result = admit_codex_registration_port(LookupTrapAdapter())
        meta_candidate = object.__new__(MetaTrapAdapter)
        meta_result = admit_codex_registration_port(meta_candidate)
        descriptor_result = admit_codex_registration_port(DescriptorCandidate())
        metadata_result = admit_codex_registration_port(MetadataTrapAdapter())
        process_result = admit_codex_registration_port(ProcessTrapAdapter())
        default_metadata_result = admit_codex_registration_port(DefaultMetadataTrapCandidate())
        representation_result = admit_codex_registration_port(RepresentationTrapAdapter())
        self.assertIsInstance(lookup_result, CodexRegistrationPortCapability)
        self.assertIsInstance(meta_result, CodexRegistrationPortCapability)
        self.assertIsInstance(descriptor_result, CodexRegistrationPortRejected)
        self.assertIsInstance(metadata_result, CodexRegistrationPortCapability)
        self.assertIsInstance(process_result, CodexRegistrationPortCapability)
        self.assertIsInstance(default_metadata_result, CodexRegistrationPortRejected)
        self.assertIsInstance(representation_result, CodexRegistrationPortCapability)
        self.assertEqual(0, LOOKUP_COUNTER.count)
        self.assertEqual(0, META_COUNTER.count)
        self.assertEqual(0, DESCRIPTOR.counter.count)
        self.assertEqual(0, METADATA_TRAP.invocation_count)
        self.assertEqual(0, DEFAULT_METADATA_TRAP.invocation_count)
        self.assertEqual(0, REPRESENTATION_COUNTER.count)
        self.assertEqual(0, BODY_COUNTER.count)

    def assert_rejected(
        self,
        result: object,
        reason: CodexRegistrationPortValueRejectReason,
    ) -> None:
        if not isinstance(result, CodexRegistrationPortValueRejected):
            raise AssertionError(f"expected value rejection, received {type(result).__name__}")
        self.assertIs(reason, result.reason)
        self.assertEqual({"status": "INVALID_VALUE", "reason": reason}, result.model_dump())


if __name__ == "__main__":
    unittest.main()
