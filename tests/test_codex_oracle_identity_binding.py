"""I1-I8 closure for the pure Codex oracle identity binding seam."""

from __future__ import annotations

from enum import Enum
from typing import NoReturn
import unittest

from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexPluginId,
    CodexRegistrationAttemptId,
)
from library.local_orchestration.codex_registration_port import CodexRegistrationPortRequest
from library.local_orchestration.contracts import (
    CANONICAL_INSTALL_ROOT,
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


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="oracle-market")
PLUGIN = CodexPluginName(value="oracle-plugin")
SOURCE = OwnedRelativePath(value="marketplaces/oracle-market")
INSTALLED = OwnedRelativePath(value="plugins/oracle-plugin")
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")
VERSION = CodexCliVersion(value="1.2.3")
DIGEST = ArtifactDigest(value="b" * 64)
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")
PLUGIN_ID = CodexPluginId(value="oracle-plugin")


class TrapKind(str, Enum):
    ATTRIBUTE = "ATTRIBUTE"
    EQUALITY = "EQUALITY"
    HASH = "HASH"
    REPRESENTATION = "REPRESENTATION"


class CallerProtocolTrap:
    def __init__(self) -> None:
        self.invocations: list[TrapKind] = []

    def __getattr__(self, name: str) -> NoReturn:
        self.invocations.append(TrapKind.ATTRIBUTE)
        raise RuntimeError("attribute trap")

    def __eq__(self, other: object) -> bool:
        self.invocations.append(TrapKind.EQUALITY)
        raise RuntimeError("equality trap")

    def __hash__(self) -> int:
        self.invocations.append(TrapKind.HASH)
        raise RuntimeError("hash trap")

    def __repr__(self) -> str:
        self.invocations.append(TrapKind.REPRESENTATION)
        raise RuntimeError("representation trap")


class RequestSubclass(CodexRegistrationPortRequest):
    """A caller-controlled derived shape that admission must reject."""


def request() -> CodexRegistrationPortRequest:
    preflight = CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )
    return CodexRegistrationPortRequest(
        preflight=preflight,
        attempt_id=ATTEMPT,
        expected_version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=PLUGIN_ID,
    )


def malformed_request(
    source: object,
    installed: object,
) -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest.model_construct(
        preflight=request().preflight,
        attempt_id=ATTEMPT,
        expected_version=VERSION,
        source_locator=source,
        installed_locator=installed,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=PLUGIN_ID,
    )


def assert_rejected(testcase: unittest.TestCase, value: object) -> None:
    from tests.staging.codex_lifecycle_oracle.identity_binding import (
        OracleIdentityBindingRejected,
    )

    testcase.assertIs(type(value), OracleIdentityBindingRejected)


class CodexOracleIdentityBindingTests(unittest.TestCase):
    def test_i1_identity_binding_module_is_required(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import bind_oracle_identity

        self.assertTrue(callable(bind_oracle_identity))

    def test_i2_exact_request_is_recursively_rebuilt_with_one_identity(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import (
            OracleIdentityBound,
            bind_oracle_identity,
        )

        supplied = request()
        result = bind_oracle_identity(supplied)
        self.assertIs(type(result), OracleIdentityBound)
        if type(result) is not OracleIdentityBound:
            raise AssertionError("expected a bound oracle identity")
        self.assertEqual(supplied.model_dump(), result.request.model_dump())
        self.assertIsNot(supplied, result.request)
        self.assertIsNot(supplied.preflight, result.request.preflight)
        self.assertIsNot(supplied.preflight.installation_id, result.request.preflight.installation_id)
        self.assertIsNot(supplied.preflight.root, result.request.preflight.root)
        self.assertIsNot(supplied.preflight.marketplace, result.request.preflight.marketplace)
        self.assertIsNot(supplied.preflight.plugin, result.request.preflight.plugin)
        self.assertIsNot(supplied.preflight.marketplace_source, result.request.preflight.marketplace_source)
        self.assertIsNot(supplied.attempt_id, result.request.attempt_id)
        self.assertIsNot(supplied.expected_version, result.request.expected_version)
        self.assertIsNot(supplied.source_locator, result.request.source_locator)
        self.assertIsNot(supplied.installed_locator, result.request.installed_locator)
        self.assertIsNot(supplied.digest, result.request.digest)
        self.assertIsNot(supplied.expected_auth_policy, result.request.expected_auth_policy)
        self.assertIsNot(supplied.expected_plugin_id, result.request.expected_plugin_id)

    def test_i3_identity_maps_only_rebuilt_request_fields_and_staging_labels(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import (
            STAGING_PLUGIN_INSTALL_POLICY,
            STAGING_PLUGIN_SOURCE,
            OracleIdentityBound,
            bind_oracle_identity,
        )

        result = bind_oracle_identity(request())
        self.assertIs(type(result), OracleIdentityBound)
        if type(result) is not OracleIdentityBound:
            raise AssertionError("expected a bound oracle identity")
        identity = result.identity
        self.assertEqual(MARKETPLACE.value, identity.marketplace_name)
        self.assertEqual(PLUGIN.value, identity.plugin_name)
        self.assertEqual(PLUGIN_ID.value, identity.plugin_id)
        self.assertEqual(VERSION.value, identity.plugin_version)
        self.assertEqual(AUTH_POLICY.value, identity.plugin_auth_policy)
        self.assertEqual(STAGING_PLUGIN_SOURCE, identity.plugin_source)
        self.assertEqual(STAGING_PLUGIN_INSTALL_POLICY, identity.plugin_install_policy)

    def test_i4_windows_logical_paths_use_only_the_fixed_staging_root_and_locators(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import (
            FIXED_STAGING_LOGICAL_ROOT,
            OracleIdentityBound,
            bind_oracle_identity,
        )

        result = bind_oracle_identity(request())
        self.assertIs(type(result), OracleIdentityBound)
        if type(result) is not OracleIdentityBound:
            raise AssertionError("expected a bound oracle identity")
        self.assertEqual(
            FIXED_STAGING_LOGICAL_ROOT + r"\marketplaces\oracle-market",
            result.identity.marketplace_root,
        )
        self.assertEqual(
            FIXED_STAGING_LOGICAL_ROOT + r"\plugins\oracle-plugin",
            result.identity.plugin_installed_path,
        )
        self.assertNotIn(CANONICAL_INSTALL_ROOT, result.identity.marketplace_root)
        self.assertNotIn(CANONICAL_INSTALL_ROOT, result.identity.plugin_installed_path)

    def test_i5_invalid_shapes_and_logical_locator_forms_reject_without_caller_protocol(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import bind_oracle_identity

        trap = CallerProtocolTrap()
        constructed_missing = object.__new__(CodexRegistrationPortRequest)
        constructed_nested = request()
        object.__setattr__(constructed_nested, "preflight", CallerProtocolTrap())
        malformed_values: tuple[object, ...] = (
            None,
            "",
            " ",
            (),
            [],
            {},
            trap,
            RequestSubclass.model_construct(),
            constructed_missing,
            constructed_nested,
            malformed_request(
                OwnedRelativePath.model_construct(value="marketplaces/other-market"),
                INSTALLED,
            ),
            malformed_request(
                OwnedRelativePath.model_construct(value=r"marketplaces\oracle-market"),
                INSTALLED,
            ),
            malformed_request(
                OwnedRelativePath.model_construct(value="../oracle-market"),
                INSTALLED,
            ),
            malformed_request(
                SOURCE,
                OwnedRelativePath.model_construct(value="plugins/../oracle-plugin"),
            ),
            malformed_request(
                OwnedRelativePath.model_construct(value="file:///oracle-market"),
                INSTALLED,
            ),
        )
        for value in malformed_values:
            with self.subTest(value_type=type(value).__name__):
                assert_rejected(self, bind_oracle_identity(value))
        self.assertEqual([], trap.invocations)

    def test_i5_source_mismatch_returns_the_finite_mismatch_reason(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import (
            OracleIdentityBindingRejectReason,
            OracleIdentityBindingRejected,
            bind_oracle_identity,
        )

        supplied = malformed_request(
            OwnedRelativePath.model_construct(value="marketplaces/other-market"),
            INSTALLED,
        )
        result = bind_oracle_identity(supplied)
        self.assertIs(type(result), OracleIdentityBindingRejected)
        if type(result) is not OracleIdentityBindingRejected:
            raise AssertionError("expected a finite identity rejection")
        self.assertIs(result.reason, OracleIdentityBindingRejectReason.REQUEST_MISMATCH)

    def test_i5_constructed_extra_request_state_is_rejected_after_revalidation(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import bind_oracle_identity

        supplied = request()
        object.__setattr__(supplied, "untrusted_extra", "untrusted")
        assert_rejected(self, bind_oracle_identity(supplied))

    def test_i6_binding_result_exposes_only_data(self) -> None:
        from tests.staging.codex_lifecycle_oracle import identity_binding

        public_names = frozenset(name for name in vars(identity_binding) if not name.startswith("_"))
        self.assertNotIn("os", public_names)
        self.assertNotIn("subprocess", public_names)
        self.assertNotIn("Path", public_names)
        self.assertNotIn("OracleCommand", public_names)
        self.assertNotIn("CodexLifecycleOracle", public_names)

    def test_i7_binding_is_a_closed_data_result(self) -> None:
        from tests.staging.codex_lifecycle_oracle.identity_binding import (
            OracleIdentityBound,
            bind_oracle_identity,
        )

        result = bind_oracle_identity(request())
        self.assertIs(type(result), OracleIdentityBound)
        if type(result) is not OracleIdentityBound:
            raise AssertionError("expected a closed identity-bound result")
        self.assertEqual({"status", "request", "identity"}, set(result.model_dump()))


if __name__ == "__main__":
    unittest.main()
