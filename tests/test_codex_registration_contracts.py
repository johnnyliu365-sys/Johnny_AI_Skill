"""C1-C4 closure for the effect-free Codex registration contract boundary."""

from __future__ import annotations

import ntpath
from typing import cast
import unittest

from pydantic import ValidationError

from library.local_orchestration.codex_registration_contracts import (
    CodexAttemptEffect,
    CodexAttemptEffectState,
    CodexAuthPolicy,
    CodexObservedAbsolutePath,
    CodexMarketplaceAddObservation,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationAttemptId,
    CodexRegistrationAttemptJournal,
    CodexRegistrationProof,
    CodexRegistrationProofPort,
    CodexRegistrationProofRequest,
    CodexRegistrationReceipt,
    CodexRegistrationRejectReason,
    CodexRegistrationRejected,
    issue_registration_receipt,
    revalidate_current_attempt_journal,
)
import library.local_orchestration.codex_registration_contracts as registration_contracts
from library.local_orchestration.contracts import ArtifactDigest, CANONICAL_INSTALL_ROOT, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import CodexCliVersion, CodexMarketplaceName, CodexPluginName, CodexPreflightRequest


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="probe-market")
PLUGIN = CodexPluginName(value="probe-plugin")
SOURCE_LOCATOR = OwnedRelativePath(value="marketplaces/probe-market")
INSTALLED_LOCATOR = OwnedRelativePath(value="plugins/probe-plugin")
VERSION = CodexCliVersion(value="1.2.3")
DIGEST = ArtifactDigest(value="a" * 64)
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")
MARKETPLACE_ROOT = CodexObservedAbsolutePath(value=ntpath.expandvars(CANONICAL_INSTALL_ROOT) + r"\marketplaces\probe-market")
PLUGIN_PATH = CodexObservedAbsolutePath(value=ntpath.expandvars(CANONICAL_INSTALL_ROOT) + r"\plugins\probe-plugin")
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")


def preflight_request() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE_LOCATOR,
    )


def marketplace_observation() -> CodexMarketplaceAddObservation:
    return CodexMarketplaceAddObservation(
        marketplace_name=MARKETPLACE,
        installed_root=MARKETPLACE_ROOT,
        already_added=False,
    )


def plugin_observation(auth_policy: CodexAuthPolicy = AUTH_POLICY) -> CodexPluginAddObservation:
    return CodexPluginAddObservation(
        plugin_id=CodexPluginId(value="probe-plugin-id"),
        name=PLUGIN,
        marketplace_name=MARKETPLACE,
        version=VERSION,
        installed_path=PLUGIN_PATH,
        auth_policy=auth_policy,
    )


def proof_request(
    expected_auth_policy: CodexAuthPolicy = AUTH_POLICY,
    observed_auth_policy: CodexAuthPolicy = AUTH_POLICY,
) -> CodexRegistrationProofRequest:
    request = CodexRegistrationProofRequest(
        preflight=preflight_request(),
        version=VERSION,
        marketplace_observation=marketplace_observation(),
        plugin_observation=plugin_observation(),
        source_locator=SOURCE_LOCATOR,
        installed_locator=INSTALLED_LOCATOR,
        digest=DIGEST,
    )
    return request.model_copy(
        update={
            "expected_auth_policy": expected_auth_policy,
            "plugin_observation": plugin_observation(observed_auth_policy),
        }
    )


def exact_proof(request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
    return CodexRegistrationProof(
        installation_id=request.preflight.installation_id,
        root=request.preflight.root,
        marketplace=request.preflight.marketplace,
        plugin_id=request.plugin_observation.plugin_id,
        plugin_name=request.plugin_observation.name,
        version=request.version,
        source_locator=request.source_locator,
        installed_locator=request.installed_locator,
        auth_policy=request.plugin_observation.auth_policy,
        digest=request.digest,
        observed_marketplace_root=request.marketplace_observation.installed_root,
        observed_marketplace_already_added=request.marketplace_observation.already_added,
        observed_plugin_path=request.plugin_observation.installed_path,
    )


class ExactProofPort(CodexRegistrationProofPort):
    """A typed proof port that returns the complete current proof."""

    def __init__(self) -> None:
        self.calls = 0

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        self.calls += 1
        return exact_proof(request)


class RequestOnlyProofPort(CodexRegistrationProofPort):
    """Ignores observed fields and therefore cannot authorize a receipt."""

    def __init__(self, mismatch: str) -> None:
        self._mismatch = mismatch

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        proof = exact_proof(request)
        if self._mismatch == "marketplace-root":
            return proof.model_copy(update={"observed_marketplace_root": CodexObservedAbsolutePath(value=r"C:\Foreign\market")})
        if self._mismatch == "plugin-path":
            return proof.model_copy(update={"observed_plugin_path": CodexObservedAbsolutePath(value=r"C:\Foreign\plugin")})
        return proof.model_copy(update={"auth_policy": CodexAuthPolicy(value="foreign-policy")})


class MismatchedProofPort(CodexRegistrationProofPort):
    """Returns one shape-valid proof mismatch for the selected binding field."""

    def __init__(self, proof: CodexRegistrationProof) -> None:
        self._proof = proof

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        return self._proof


class TypedFailureProofPort(CodexRegistrationProofPort):
    """Raises only the ticket-declared typed port failure."""

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise registration_contracts.CodexRegistrationProofPortFailure()


class MalformedProofPort(CodexRegistrationProofPort):
    """Returns a typed-but-constructed proof that must be rejected at the boundary."""

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        return CodexRegistrationProof.model_construct()


class RuntimeFailureProofPort(CodexRegistrationProofPort):
    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise RuntimeError


class MemoryFailureProofPort(CodexRegistrationProofPort):
    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise MemoryError


class KeyboardFailureProofPort(CodexRegistrationProofPort):
    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise KeyboardInterrupt


class ExitFailureProofPort(CodexRegistrationProofPort):
    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise SystemExit


class CodexRegistrationContractsTests(unittest.TestCase):
    def test_t1_c1_observations_are_strict_before_any_proof_authority_exists(self) -> None:
        invalid_values: tuple[object, ...] = (None, "", " ", [], {})
        for value in invalid_values:
            with self.subTest(marketplace_name=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexMarketplaceName.model_validate({"value": value})
            with self.subTest(plugin_id=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexPluginId.model_validate({"value": value})
            with self.subTest(auth_policy=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexAuthPolicy.model_validate({"value": value})
        marketplace_fields: dict[str, object] = {
            "marketplace_name": MARKETPLACE,
            "installed_root": MARKETPLACE_ROOT,
            "already_added": False,
        }
        plugin_fields: dict[str, object] = {
            "plugin_id": CodexPluginId(value="probe-plugin-id"),
            "name": PLUGIN,
            "marketplace_name": MARKETPLACE,
            "version": VERSION,
            "installed_path": PLUGIN_PATH,
            "auth_policy": AUTH_POLICY,
        }
        for field in marketplace_fields:
            with self.subTest(marketplace_missing=field):
                missing = dict(marketplace_fields)
                del missing[field]
                with self.assertRaises(ValidationError):
                    CodexMarketplaceAddObservation.model_validate(missing)
        for field in plugin_fields:
            with self.subTest(plugin_missing=field):
                missing = dict(plugin_fields)
                del missing[field]
                with self.assertRaises(ValidationError):
                    CodexPluginAddObservation.model_validate(missing)
        for field in ("marketplace_name", "installed_root"):
            for value in invalid_values:
                with self.subTest(marketplace_field=field, value=repr(value)):
                    invalid = dict(marketplace_fields)
                    invalid[field] = value
                    with self.assertRaises(ValidationError):
                        CodexMarketplaceAddObservation.model_validate(invalid)
        for field in ("plugin_id", "name", "marketplace_name", "version", "installed_path", "auth_policy"):
            for value in invalid_values:
                with self.subTest(plugin_field=field, value=repr(value)):
                    invalid = dict(plugin_fields)
                    invalid[field] = value
                    with self.assertRaises(ValidationError):
                        CodexPluginAddObservation.model_validate(invalid)
        invalid_paths: tuple[object, ...] = (
            None,
            "",
            " ",
            "relative\\plugin",
            "file:///foreign/plugin",
            r"C:\owned\..\foreign",
            r"C:\owned%2Fplugin",
            [],
            {},
        )
        for value in invalid_paths:
            with self.subTest(observed_path=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexObservedAbsolutePath.model_validate({"value": value})
        with self.assertRaises(ValidationError):
            CodexMarketplaceAddObservation.model_validate({
                "marketplace_name": MARKETPLACE,
                "installed_root": MARKETPLACE_ROOT,
                "already_added": False,
                "extra": "forbidden",
            })
        with self.assertRaises(ValidationError):
            CodexPluginAddObservation.model_validate(plugin_fields | {"extra": "forbidden"})
        for value in (None, "false", 1, [], {}):
            with self.subTest(already_added=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexMarketplaceAddObservation.model_validate({
                        "marketplace_name": MARKETPLACE,
                        "installed_root": MARKETPLACE_ROOT,
                        "already_added": value,
                    })
        port = ExactProofPort()
        unsafe = proof_request().model_copy(update={"source_locator": OwnedRelativePath.model_construct(value="../foreign")})
        result = issue_registration_receipt(unsafe, port)
        self._assert_rejected(result, CodexRegistrationRejectReason.INVALID_INPUT)
        self.assertEqual(0, port.calls)

    def test_t2_c2_c3_exact_proof_emits_metadata_only_receipt_and_rejects_all_mismatches(self) -> None:
        request = proof_request()
        port = ExactProofPort()
        result = issue_registration_receipt(request, port)
        if not isinstance(result, CodexRegistrationReceipt):
            raise AssertionError(f"expected exact receipt, received {result}")
        self.assertEqual(1, port.calls)
        self.assertEqual(INSTALLATION, result.installation_id)
        self.assertEqual(INSTALLED_LOCATOR, result.installed_locator)
        self.assertEqual(AUTH_POLICY, result.auth_policy)
        serialized = result.model_dump_json(warnings=False)
        self.assertNotIn(MARKETPLACE_ROOT.value, serialized)
        self.assertNotIn(PLUGIN_PATH.value, serialized)
        foreign_observations = (
            ("marketplace-root", {"marketplace_observation": marketplace_observation().model_copy(update={"installed_root": CodexObservedAbsolutePath(value=r"C:\Foreign\market")})}),
            ("plugin-path", {"plugin_observation": plugin_observation().model_copy(update={"installed_path": CodexObservedAbsolutePath(value=r"C:\Foreign\plugin")})}),
        )
        for label, update in foreign_observations:
            with self.subTest(foreign_observation=label):
                foreign_request = request.model_copy(update=update)
                foreign_port = ExactProofPort()
                self._assert_rejected(
                    issue_registration_receipt(foreign_request, foreign_port),
                    CodexRegistrationRejectReason.INVALID_INPUT,
                )
                self.assertEqual(0, foreign_port.calls)
        request_only_cells = ("marketplace-root", "plugin-path", "auth-policy")
        for cell in request_only_cells:
            with self.subTest(request_only=cell):
                self._assert_rejected(
                    issue_registration_receipt(request, RequestOnlyProofPort(cell)),
                    CodexRegistrationRejectReason.PROOF_MISMATCH,
                )
        mismatches = (
            exact_proof(request).model_copy(update={"installation_id": InstallationId(value="installation-fedcba9876543210")} ),
            exact_proof(request).model_copy(update={"marketplace": CodexMarketplaceName(value="other-market")} ),
            exact_proof(request).model_copy(update={"plugin_id": CodexPluginId(value="other-plugin-id")} ),
            exact_proof(request).model_copy(update={"plugin_name": CodexPluginName(value="other-plugin")} ),
            exact_proof(request).model_copy(update={"version": CodexCliVersion(value="9.9.9")} ),
            exact_proof(request).model_copy(update={"source_locator": OwnedRelativePath(value="marketplaces/other-market")} ),
            exact_proof(request).model_copy(update={"installed_locator": OwnedRelativePath(value="plugins/other-plugin")} ),
            exact_proof(request).model_copy(update={"auth_policy": CodexAuthPolicy(value="other-policy")} ),
            exact_proof(request).model_copy(update={"digest": ArtifactDigest(value="b" * 64)}),
            exact_proof(request).model_copy(update={"observed_marketplace_root": CodexObservedAbsolutePath(value=r"C:\Users\Tester\AppData\Local\JohnnyAIWorkflowX\marketplaces\probe-market")} ),
            exact_proof(request).model_copy(update={"observed_plugin_path": CodexObservedAbsolutePath(value=r"C:\Users\Tester\AppData\Local\JohnnyAIWorkflow\plugins\probe-plugin-copy")} ),
            exact_proof(request).model_copy(update={"observed_marketplace_already_added": True}),
        )
        for proof in mismatches:
            with self.subTest(proof=proof):
                self._assert_rejected(
                    issue_registration_receipt(request, MismatchedProofPort(proof)),
                    CodexRegistrationRejectReason.PROOF_MISMATCH,
                )
        invalid_root = exact_proof(request).model_copy(update={"root": InstallRoot.model_construct(value=CANONICAL_INSTALL_ROOT + "X")})
        self._assert_rejected(
            issue_registration_receipt(request, MismatchedProofPort(invalid_root)),
            CodexRegistrationRejectReason.INVALID_PROOF,
        )

    def test_r1_expected_auth_policy_blocks_foreign_observation_before_proof_port(self) -> None:
        foreign_policy = CodexAuthPolicy(value="foreign-policy")
        request = proof_request(AUTH_POLICY, foreign_policy)
        port = ExactProofPort()
        self._assert_rejected(
            issue_registration_receipt(request, port),
            CodexRegistrationRejectReason.INVALID_INPUT,
        )
        self.assertEqual(0, port.calls)

    def test_r2_proof_port_failure_algebra_is_finite_and_process_control_propagates(self) -> None:
        request = proof_request()
        self._assert_rejected(
            issue_registration_receipt(request, TypedFailureProofPort()),
            CodexRegistrationRejectReason.PROOF_PORT_FAILED,
        )
        self._assert_rejected(
            issue_registration_receipt(request, MalformedProofPort()),
            CodexRegistrationRejectReason.INVALID_PROOF,
        )
        wrong_ports: tuple[object, ...] = (None, object())
        for wrong_port in wrong_ports:
            with self.subTest(wrong_port=type(wrong_port).__name__):
                self._assert_rejected(
                    issue_registration_receipt(request, cast(CodexRegistrationProofPort, wrong_port)),
                    CodexRegistrationRejectReason.INVALID_PROOF_PORT,
                )
        unexpected_ports: tuple[tuple[type[BaseException], CodexRegistrationProofPort], ...] = (
            (RuntimeError, RuntimeFailureProofPort()),
            (MemoryError, MemoryFailureProofPort()),
            (KeyboardInterrupt, KeyboardFailureProofPort()),
            (SystemExit, ExitFailureProofPort()),
        )
        for exception_type, unexpected_port in unexpected_ports:
            with self.subTest(exception=exception_type.__name__):
                with self.assertRaises(exception_type):
                    issue_registration_receipt(request, unexpected_port)

    def test_r4_every_path_boundary_cell_rejects_before_proof_port(self) -> None:
        exact = proof_request()
        exact_port = ExactProofPort()
        self.assertIsInstance(issue_registration_receipt(exact, exact_port), CodexRegistrationReceipt)
        self.assertEqual(1, exact_port.calls)
        invalid_paths: tuple[tuple[str, str], ...] = (
            ("prefix-plus-character", MARKETPLACE_ROOT.value + "X"),
            ("trailing-slash", MARKETPLACE_ROOT.value + "\\"),
            ("case", MARKETPLACE_ROOT.value.replace("probe-market", "Probe-market")),
            ("url-encoded-separator", MARKETPLACE_ROOT.value.replace("marketplaces\\", "marketplaces%2F")),
            ("traversal", MARKETPLACE_ROOT.value.replace("marketplaces\\probe-market", "marketplaces\\..\\probe-market")),
            ("empty", ""),
        )
        for label, path in invalid_paths:
            for observed_field in ("marketplace-root", "plugin-path"):
                with self.subTest(path_cell=label, observed_field=observed_field):
                    invalid_path = CodexObservedAbsolutePath.model_construct(value=path)
                    if observed_field == "marketplace-root":
                        invalid_request = exact.model_copy(
                            update={
                                "marketplace_observation": marketplace_observation().model_copy(
                                    update={"installed_root": invalid_path}
                                )
                            }
                        )
                    else:
                        invalid_request = exact.model_copy(
                            update={
                                "plugin_observation": plugin_observation().model_copy(
                                    update={"installed_path": invalid_path}
                                )
                            }
                        )
                    port = ExactProofPort()
                    self._assert_rejected(
                        issue_registration_receipt(invalid_request, port),
                        CodexRegistrationRejectReason.INVALID_INPUT,
                    )
                    self.assertEqual(0, port.calls)

    def test_t3_c4_attempt_journal_enforces_order_and_plugin_first_removal_authority(self) -> None:
        legal_cells = (
            (CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED, ()),
            (CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexAttemptEffect.MARKETPLACE,)),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexAttemptEffect.MARKETPLACE,)),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST, (CodexAttemptEffect.PLUGIN, CodexAttemptEffect.MARKETPLACE)),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED, (CodexAttemptEffect.PLUGIN, CodexAttemptEffect.MARKETPLACE)),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.PREEXISTING, (CodexAttemptEffect.MARKETPLACE,)),
            (CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED, ()),
        )
        for marketplace_state, plugin_state, expected in legal_cells:
            with self.subTest(marketplace=marketplace_state, plugin=plugin_state):
                journal = CodexRegistrationAttemptJournal(
                    request=preflight_request(),
                    attempt_id=ATTEMPT,
                    marketplace_state=marketplace_state,
                    plugin_state=plugin_state,
                )
                self.assertEqual(expected, journal.unresolved_removal_order())
        states: tuple[CodexAttemptEffectState, ...] = tuple(CodexAttemptEffectState)
        legal_pairs = tuple((marketplace, plugin) for marketplace, plugin, _ in legal_cells)
        for marketplace_state in states:
            for plugin_state in states:
                pair = (marketplace_state, plugin_state)
                if pair in legal_pairs:
                    continue
                with self.subTest(illegal_marketplace=marketplace_state, illegal_plugin=plugin_state):
                    with self.assertRaises(ValidationError):
                        CodexRegistrationAttemptJournal(
                            request=preflight_request(),
                            attempt_id=ATTEMPT,
                            marketplace_state=marketplace_state,
                            plugin_state=plugin_state,
                        )
        journal = CodexRegistrationAttemptJournal(
            request=preflight_request(),
            attempt_id=ATTEMPT,
            marketplace_state=CodexAttemptEffectState.OWNED,
            plugin_state=CodexAttemptEffectState.MAY_EXIST,
        )
        same_attempt = revalidate_current_attempt_journal(journal, preflight_request(), ATTEMPT)
        self.assertIsInstance(same_attempt, CodexRegistrationAttemptJournal)
        replay = revalidate_current_attempt_journal(
            journal,
            preflight_request(),
            CodexRegistrationAttemptId(value="attempt-fedcba9876543210"),
        )
        self._assert_rejected(replay, CodexRegistrationRejectReason.JOURNAL_ATTEMPT_MISMATCH)
        other_request = CodexPreflightRequest(
            installation_id=INSTALLATION,
            root=ROOT,
            marketplace=CodexMarketplaceName(value="other-market"),
            plugin=PLUGIN,
            marketplace_source=OwnedRelativePath(value="marketplaces/other-market"),
        )
        cross_request = revalidate_current_attempt_journal(journal, other_request, ATTEMPT)
        self._assert_rejected(cross_request, CodexRegistrationRejectReason.JOURNAL_REQUEST_MISMATCH)
        malformed = CodexRegistrationAttemptJournal.model_construct(
            request=preflight_request(),
            attempt_id=ATTEMPT,
            marketplace_state=CodexAttemptEffectState.NOT_ATTEMPTED,
            plugin_state=CodexAttemptEffectState.MAY_EXIST,
        )
        self._assert_rejected(
            revalidate_current_attempt_journal(malformed, preflight_request(), ATTEMPT),
            CodexRegistrationRejectReason.JOURNAL_INVALID,
        )
        with self.assertRaises(ValidationError):
            CodexRegistrationAttemptJournal.model_validate({
                "request": preflight_request(),
                "attempt_id": ATTEMPT,
                "marketplace_state": CodexAttemptEffectState.OWNED,
                "plugin_state": CodexAttemptEffectState.MAY_EXIST,
                "extra": "forbidden",
            })

    def test_t4_recursive_models_reject_constructed_values_and_preserve_preexisting_without_removal_authority(self) -> None:
        request = proof_request()
        port = ExactProofPort()
        constructed = request.model_copy(update={"plugin_observation": CodexPluginAddObservation.model_construct(plugin_id=[], name=PLUGIN)})
        self._assert_rejected(issue_registration_receipt(constructed, port), CodexRegistrationRejectReason.INVALID_INPUT)
        self.assertEqual(0, port.calls)
        journal = CodexRegistrationAttemptJournal(
            request=preflight_request(),
            attempt_id=ATTEMPT,
            marketplace_state=CodexAttemptEffectState.PREEXISTING,
            plugin_state=CodexAttemptEffectState.NOT_ATTEMPTED,
        )
        self.assertEqual((), journal.unresolved_removal_order())

    @staticmethod
    def _assert_rejected(
        result: CodexRegistrationReceipt | CodexRegistrationRejected | CodexRegistrationAttemptJournal,
        expected: CodexRegistrationRejectReason,
    ) -> None:
        if not isinstance(result, CodexRegistrationRejected):
            raise AssertionError(f"expected rejection, received {result}")
        if result.reason is not expected:
            raise AssertionError(f"expected {expected}, received {result.reason}")


if __name__ == "__main__":
    unittest.main()
