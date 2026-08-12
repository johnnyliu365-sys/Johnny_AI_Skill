"""P1-P8 behavior evidence for one-shot Codex registration proof settlement."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import ntpath
from typing import NoReturn
import unittest

from library.local_orchestration.codex_command_attempts import (
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexMarketplaceAddObservation,
    CodexObservedAbsolutePath,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationAttemptId,
    CodexRegistrationProof,
    CodexRegistrationProofPortFailure,
    CodexRegistrationProofRequest,
    CodexRegistrationReceipt,
    CodexRegistrationRejected,
    CodexRegistrationRejectReason,
)
from library.local_orchestration.codex_registration_forward import (
    CodexRegistrationForwardCoordinator,
    admit_codex_registration_forward,
)
from library.local_orchestration.codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddSucceeded,
    CodexRegistrationPortCapability,
    CodexRegistrationPortRequest,
    admit_codex_registration_port,
)
from library.local_orchestration.codex_registration_proof_settlement import (
    settle_codex_registration_proof,
)
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationCompensationClaim,
    CodexRegistrationProofClaim,
    CodexRegistrationSettlementAuthority,
    CodexRegistrationSettlementClaimBlocked,
    CodexRegistrationSettlementClaimKind,
    admit_codex_registration_settlement_authority,
    consume_codex_registration_proof_claim,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationNextReadyPhase,
    CodexRegistrationReadyLease,
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
    CodexMarketplaceName,
    CodexPluginName,
    CodexPreflightEligible,
    CodexPreflightRequest,
)


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="settlement-market")
PLUGIN = CodexPluginName(value="settlement-plugin")
SOURCE = OwnedRelativePath(value="marketplaces/settlement-market")
INSTALLED = OwnedRelativePath(value="plugins/settlement-plugin")
VERSION = CodexCliVersion(value="1.2.3")
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")
DIGEST = ArtifactDigest(value="b" * 64)
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")
PLUGIN_ID = CodexPluginId(value="plugin-settlement-012345")


class PortOperation(str, Enum):
    FRESH = "FRESH"
    MARKETPLACE = "MARKETPLACE"
    PLUGIN = "PLUGIN"
    PROVE = "PROVE"


class ProofVariant(str, Enum):
    EXACT = "EXACT"
    DECLARED_FAILURE = "DECLARED_FAILURE"
    MALFORMED = "MALFORMED"
    INSTALLATION = "INSTALLATION"
    ROOT = "ROOT"
    MARKETPLACE = "MARKETPLACE"
    PLUGIN_ID = "PLUGIN_ID"
    PLUGIN_NAME = "PLUGIN_NAME"
    VERSION = "VERSION"
    SOURCE = "SOURCE"
    INSTALLED = "INSTALLED"
    AUTH_POLICY = "AUTH_POLICY"
    DIGEST = "DIGEST"
    MARKETPLACE_ROOT = "MARKETPLACE_ROOT"
    ALREADY_ADDED = "ALREADY_ADDED"
    PLUGIN_PATH = "PLUGIN_PATH"
    RUNTIME = "RUNTIME"
    MEMORY = "MEMORY"
    KEYBOARD = "KEYBOARD"
    EXIT = "EXIT"


def preflight() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )


def port_request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=preflight(),
        attempt_id=ATTEMPT,
        expected_version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=PLUGIN_ID,
    )


def observed_path(locator: OwnedRelativePath) -> CodexObservedAbsolutePath:
    return CodexObservedAbsolutePath(
        value=ntpath.join(ntpath.expandvars(CANONICAL_INSTALL_ROOT), *locator.parts())
    )


def expected_proof_request(current: CodexRegistrationPortRequest) -> CodexRegistrationProofRequest:
    """Expected B2B1 proof value used only to compare the live claim result."""

    return CodexRegistrationProofRequest(
        preflight=current.preflight,
        version=current.expected_version,
        marketplace_observation=CodexMarketplaceAddObservation(
            marketplace_name=current.preflight.marketplace,
            installed_root=observed_path(current.source_locator),
            already_added=False,
        ),
        plugin_observation=CodexPluginAddObservation(
            plugin_id=current.expected_plugin_id,
            name=current.preflight.plugin,
            marketplace_name=current.preflight.marketplace,
            version=current.expected_version,
            installed_path=observed_path(current.installed_locator),
            auth_policy=current.expected_auth_policy,
        ),
        source_locator=current.source_locator,
        installed_locator=current.installed_locator,
        digest=current.digest,
        expected_auth_policy=current.expected_auth_policy,
    )


class SettlementPort:
    """Fully shaped fake port; settlement must invoke only its prove operation."""

    def __init__(self, variant: ProofVariant = ProofVariant.EXACT) -> None:
        self.variant = variant
        self.calls: list[PortOperation] = []

    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> CodexFreshPreflightAccepted:
        self.calls.append(PortOperation.FRESH)
        return CodexFreshPreflightAccepted(
            request=current,
            eligible=CodexPreflightEligible(version=current.expected_version),
        )

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> CodexMarketplaceAddSucceeded:
        self.calls.append(PortOperation.MARKETPLACE)
        return CodexMarketplaceAddSucceeded(
            request=current,
            confirmed=CodexMarketplaceAddConfirmed(
                target=CodexCommandTarget.MARKETPLACE_ADD,
                start_state=CodexCommandStartState.STARTED,
                already_added=False,
            ),
            observation=CodexMarketplaceAddObservation(
                marketplace_name=current.preflight.marketplace,
                installed_root=observed_path(current.source_locator),
                already_added=False,
            ),
        )

    def add_plugin(self, current: CodexRegistrationPortRequest) -> CodexPluginAddSucceeded:
        self.calls.append(PortOperation.PLUGIN)
        return CodexPluginAddSucceeded(
            request=current,
            confirmed=CodexPluginAddConfirmed(
                target=CodexCommandTarget.PLUGIN_ADD,
                start_state=CodexCommandStartState.STARTED,
            ),
            observation=CodexPluginAddObservation(
                plugin_id=current.expected_plugin_id,
                name=current.preflight.plugin,
                marketplace_name=current.preflight.marketplace,
                version=current.expected_version,
                installed_path=observed_path(current.installed_locator),
                auth_policy=current.expected_auth_policy,
            ),
        )

    def prove(self, current: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        self.calls.append(PortOperation.PROVE)
        if self.variant is ProofVariant.DECLARED_FAILURE:
            raise CodexRegistrationProofPortFailure()
        if self.variant is ProofVariant.MALFORMED:
            return CodexRegistrationProof.model_construct()
        if self.variant is ProofVariant.RUNTIME:
            raise RuntimeError("unexpected proof failure")
        if self.variant is ProofVariant.MEMORY:
            raise MemoryError()
        if self.variant is ProofVariant.KEYBOARD:
            raise KeyboardInterrupt()
        if self.variant is ProofVariant.EXIT:
            raise SystemExit()
        proof = exact_proof(current)
        return mismatched_proof(proof, self.variant)


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
        auth_policy=request.expected_auth_policy,
        digest=request.digest,
        observed_marketplace_root=request.marketplace_observation.installed_root,
        observed_marketplace_already_added=request.marketplace_observation.already_added,
        observed_plugin_path=request.plugin_observation.installed_path,
    )


def mismatched_proof(proof: CodexRegistrationProof, variant: ProofVariant) -> CodexRegistrationProof:
    if variant is ProofVariant.EXACT:
        return proof
    if variant is ProofVariant.INSTALLATION:
        return proof.model_copy(update={"installation_id": InstallationId(value="installation-fedcba9876543210")})
    if variant is ProofVariant.ROOT:
        foreign_root = InstallRoot.model_construct(value=CANONICAL_INSTALL_ROOT + "X")
        return proof.model_copy(update={"root": foreign_root})
    if variant is ProofVariant.MARKETPLACE:
        return proof.model_copy(update={"marketplace": CodexMarketplaceName(value="foreign-market")})
    if variant is ProofVariant.PLUGIN_ID:
        return proof.model_copy(update={"plugin_id": CodexPluginId(value="plugin-foreign-012345")})
    if variant is ProofVariant.PLUGIN_NAME:
        return proof.model_copy(update={"plugin_name": CodexPluginName(value="foreign-plugin")})
    if variant is ProofVariant.VERSION:
        return proof.model_copy(update={"version": CodexCliVersion(value="9.9.9")})
    if variant is ProofVariant.SOURCE:
        return proof.model_copy(update={"source_locator": OwnedRelativePath(value="marketplaces/foreign-market")})
    if variant is ProofVariant.INSTALLED:
        return proof.model_copy(update={"installed_locator": OwnedRelativePath(value="plugins/foreign-plugin")})
    if variant is ProofVariant.AUTH_POLICY:
        return proof.model_copy(update={"auth_policy": CodexAuthPolicy(value="foreign-policy")})
    if variant is ProofVariant.DIGEST:
        return proof.model_copy(update={"digest": ArtifactDigest(value="c" * 64)})
    if variant is ProofVariant.MARKETPLACE_ROOT:
        return proof.model_copy(update={"observed_marketplace_root": CodexObservedAbsolutePath(value=r"C:\Foreign\market")})
    if variant is ProofVariant.ALREADY_ADDED:
        return proof.model_copy(update={"observed_marketplace_already_added": True})
    return proof.model_copy(update={"observed_plugin_path": CodexObservedAbsolutePath(value=r"C:\Foreign\plugin")})


def _capability(adapter: SettlementPort) -> CodexRegistrationPortCapability:
    admitted = admit_codex_registration_port(adapter)
    if type(admitted) is not CodexRegistrationPortCapability:
        raise AssertionError("test port was not admitted")
    return admitted


def _authority(adapter: SettlementPort) -> CodexRegistrationSettlementAuthority:
    coordinator = admit_codex_registration_forward(_capability(adapter))
    if type(coordinator) is not CodexRegistrationForwardCoordinator:
        raise AssertionError("test capability did not produce forward coordinator")
    admitted = admit_codex_registration_settlement_authority(coordinator)
    if type(admitted) is not CodexRegistrationSettlementAuthority:
        raise AssertionError("test coordinator did not produce settlement authority")
    return admitted


def _proof_claim(
    adapter: SettlementPort,
    current: CodexRegistrationPortRequest,
) -> tuple[CodexRegistrationSettlementAuthority, CodexRegistrationProofClaim]:
    authority = _authority(adapter)
    fresh = authority.begin(current)
    if type(fresh) is not CodexRegistrationReadyLease:
        raise AssertionError("fresh lease was not ready")
    marketplace = authority.execute(fresh.lease)
    if type(marketplace) is not CodexRegistrationNextReadyPhase:
        raise AssertionError("marketplace lease was not ready")
    plugin = authority.execute(marketplace.lease)
    if type(plugin) is not CodexRegistrationNextReadyPhase:
        raise AssertionError("plugin lease was not ready")
    claimed = authority.execute(plugin.lease)
    if type(claimed) is not CodexRegistrationProofClaim:
        raise AssertionError("terminal proof claim was not issued")
    return authority, claimed


class _PropertyPort:
    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    def add_plugin(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    @property
    def prove(self) -> object:
        raise AssertionError("property operation was read")


class _DescriptorTrap:
    def __init__(self) -> None:
        self.read_count = 0

    def __get__(self, instance: object, owner: type[object]) -> object:
        self.read_count += 1
        raise AssertionError("descriptor operation was read")


class _DescriptorPort:
    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    def add_plugin(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    prove = _DescriptorTrap()


class _LookupTrapPort:
    def __getattribute__(self, name: str) -> NoReturn:
        raise AssertionError(f"candidate lookup escaped admission: {name}")

    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    def add_plugin(self, current: CodexRegistrationPortRequest) -> NoReturn:
        raise AssertionError("invalid port operation was invoked")

    @property
    def prove(self) -> object:
        raise AssertionError("property operation was read")


class CodexRegistrationProofSettlementTests(unittest.TestCase):
    """P1-P8 finite proof settlement behavior."""

    def test_p1_settlement_module_is_present(self) -> None:
        self.assertTrue(callable(settle_codex_registration_proof))

    def test_p2_invalid_port_admission_leaves_claim_live_without_calls(self) -> None:
        invalid_candidates: tuple[object, ...] = (
            None,
            "",
            (),
            [],
            {},
            _PropertyPort(),
            _DescriptorPort(),
            _LookupTrapPort(),
        )
        for candidate in invalid_candidates:
            with self.subTest(candidate=type(candidate).__name__):
                adapter = SettlementPort()
                owner, claim = _proof_claim(adapter, port_request())
                adapter.calls.clear()
                result = settle_codex_registration_proof(claim, candidate)
                self._assert_registration_rejected(result, CodexRegistrationRejectReason.INVALID_PROOF_PORT)
                self.assertEqual([], adapter.calls)
                self.assertNotIsInstance(
                    consume_codex_registration_proof_claim(claim),
                    CodexRegistrationSettlementClaimBlocked,
                )
        descriptor = _DescriptorPort.__dict__["prove"]
        if type(descriptor) is not _DescriptorTrap:
            raise AssertionError("descriptor fixture is invalid")
        self.assertEqual(0, descriptor.read_count)

    def test_p3_only_one_exact_live_proof_claim_can_settle(self) -> None:
        invalid_claims: tuple[object, ...] = (None, "claim", (), [], {}, object())
        adapter = SettlementPort()
        for claim in invalid_claims:
            with self.subTest(claim=type(claim).__name__):
                result = settle_codex_registration_proof(claim, adapter)
                self._assert_claim_blocked(result)
        owner, live = _proof_claim(adapter, port_request())
        metadata = live.metadata()
        fabricated = object.__new__(CodexRegistrationProofClaim)
        object.__setattr__(fabricated, "_metadata", metadata)
        self._assert_claim_blocked(settle_codex_registration_proof(fabricated, adapter))
        altered = object.__new__(CodexRegistrationProofClaim)
        altered_metadata = metadata.model_copy(update={"kind": CodexRegistrationSettlementClaimKind.COMPENSATION})
        object.__setattr__(altered, "_metadata", altered_metadata)
        self._assert_claim_blocked(settle_codex_registration_proof(altered, adapter))
        wrong_kind = object.__new__(CodexRegistrationCompensationClaim)
        object.__setattr__(wrong_kind, "_metadata", metadata)
        self._assert_claim_blocked(settle_codex_registration_proof(wrong_kind, adapter))
        self._assert_claim_blocked(settle_codex_registration_proof(metadata, adapter))
        replay_owner, replay = _proof_claim(adapter, port_request())
        adapter.calls.clear()
        first = settle_codex_registration_proof(replay, adapter)
        if type(first) is not CodexRegistrationReceipt:
            raise AssertionError(f"live claim did not settle: {first}")
        self.assertEqual([PortOperation.PROVE], adapter.calls)
        adapter.calls.clear()
        self._assert_claim_blocked(settle_codex_registration_proof(replay, adapter))
        self.assertEqual([], adapter.calls)

    def test_p4_exact_claim_calls_only_prove_once_and_returns_metadata_receipt(self) -> None:
        adapter = SettlementPort()
        current = port_request()
        owner, claim = _proof_claim(adapter, current)
        adapter.calls.clear()
        result = settle_codex_registration_proof(claim, adapter)
        if type(result) is not CodexRegistrationReceipt:
            raise AssertionError(f"expected receipt, received {result}")
        self.assertEqual([PortOperation.PROVE], adapter.calls)
        self.assertEqual(INSTALLATION, result.installation_id)
        self.assertNotIn(observed_path(SOURCE).value, result.model_dump_json(warnings=False))
        request = expected_proof_request(current)
        self.assertEqual(request.installed_locator, result.installed_locator)
        self.assertEqual(request.expected_auth_policy, result.auth_policy)

    def test_p5_declared_malformed_and_all_exact_proof_mismatches_remain_finite(self) -> None:
        variants = (
            ProofVariant.DECLARED_FAILURE,
            ProofVariant.MALFORMED,
            ProofVariant.INSTALLATION,
            ProofVariant.ROOT,
            ProofVariant.MARKETPLACE,
            ProofVariant.PLUGIN_ID,
            ProofVariant.PLUGIN_NAME,
            ProofVariant.VERSION,
            ProofVariant.SOURCE,
            ProofVariant.INSTALLED,
            ProofVariant.AUTH_POLICY,
            ProofVariant.DIGEST,
            ProofVariant.MARKETPLACE_ROOT,
            ProofVariant.ALREADY_ADDED,
            ProofVariant.PLUGIN_PATH,
        )
        for variant in variants:
            with self.subTest(variant=variant.value):
                adapter = SettlementPort(variant)
                owner, claim = _proof_claim(adapter, port_request())
                adapter.calls.clear()
                result = settle_codex_registration_proof(claim, adapter)
                expected = CodexRegistrationRejectReason.PROOF_PORT_FAILED
                if variant in (ProofVariant.MALFORMED, ProofVariant.ROOT):
                    expected = CodexRegistrationRejectReason.INVALID_PROOF
                if variant not in (ProofVariant.DECLARED_FAILURE, ProofVariant.MALFORMED, ProofVariant.ROOT):
                    expected = CodexRegistrationRejectReason.PROOF_MISMATCH
                self._assert_registration_rejected(result, expected)
                self.assertEqual([PortOperation.PROVE], adapter.calls)

    def test_p6_unexpected_proof_failures_consume_claim_before_one_call_and_replay_blocks(self) -> None:
        variants = (ProofVariant.RUNTIME, ProofVariant.MEMORY, ProofVariant.KEYBOARD, ProofVariant.EXIT)
        errors: tuple[type[BaseException], ...] = (RuntimeError, MemoryError, KeyboardInterrupt, SystemExit)
        for variant, error in zip(variants, errors, strict=True):
            with self.subTest(variant=variant.value):
                adapter = SettlementPort(variant)
                owner, claim = _proof_claim(adapter, port_request())
                adapter.calls.clear()
                with self.assertRaises(error):
                    settle_codex_registration_proof(claim, adapter)
                self.assertEqual([PortOperation.PROVE], adapter.calls)
                self._assert_claim_blocked(settle_codex_registration_proof(claim, adapter))
                self.assertEqual([PortOperation.PROVE], adapter.calls)

    def test_p6_duplicate_settlement_consumes_once_before_one_proof_effect(self) -> None:
        adapter = SettlementPort()
        owner, claim = _proof_claim(adapter, port_request())
        adapter.calls.clear()
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = tuple(executor.map(lambda _: settle_codex_registration_proof(claim, adapter), range(2)))
        self.assertEqual(1, sum(type(result) is CodexRegistrationReceipt for result in results))
        self.assertEqual(1, sum(type(result) is CodexRegistrationSettlementClaimBlocked for result in results))
        self.assertEqual([PortOperation.PROVE], adapter.calls)

    def _assert_registration_rejected(
        self,
        result: object,
        reason: CodexRegistrationRejectReason,
    ) -> None:
        self.assertIs(type(result), CodexRegistrationRejected)
        if type(result) is not CodexRegistrationRejected:
            raise AssertionError(f"expected registration rejection, received {result}")
        self.assertIs(result.reason, reason)

    def _assert_claim_blocked(self, result: object) -> None:
        self.assertIs(type(result), CodexRegistrationSettlementClaimBlocked)


if __name__ == "__main__":
    unittest.main()
