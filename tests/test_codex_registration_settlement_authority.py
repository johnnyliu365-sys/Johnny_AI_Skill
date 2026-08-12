"""C1-C8 closure for Codex registration settlement-claim authority."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, astuple, is_dataclass
from enum import Enum
import gc
import ntpath
import pickle
from typing import Callable, NoReturn, cast
import unittest
from weakref import ref

import library.local_orchestration.codex_registration_settlement_authority as settlement_module
from library.local_orchestration.codex_command_attempts import (
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
    CodexStartedFailure,
    CodexStartedFailureReason,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAttemptEffectState,
    CodexAuthPolicy,
    CodexMarketplaceAddObservation,
    CodexObservedAbsolutePath,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationAttemptId,
    CodexRegistrationProof,
    CodexRegistrationProofRequest,
)
from library.local_orchestration.codex_registration_forward import (
    CodexRegistrationForwardCoordinator,
    admit_codex_registration_forward,
)
from library.local_orchestration.codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexFreshPreflightRejected,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortCapability,
    CodexRegistrationPortRequest,
    admit_codex_registration_port,
)
from library.local_orchestration.codex_registration_reducer import (
    CodexRegistrationBlockReason,
    CodexRegistrationBlocked,
    CodexRegistrationCompensationRequired,
    CodexRegistrationProofRequired,
)
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationCompensationClaim,
    CodexRegistrationProofClaim,
    CodexRegistrationSettlementAuthority,
    CodexRegistrationSettlementAuthorityBlocked,
    CodexRegistrationSettlementAuthorityRejectReason,
    CodexRegistrationSettlementClaimBlocked,
    CodexRegistrationSettlementClaimBlockReason,
    CodexRegistrationSettlementClaimKind,
    admit_codex_registration_settlement_authority,
    consume_codex_registration_compensation_claim,
    consume_codex_registration_proof_claim,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationAddRecovery,
    CodexRegistrationNextReadyPhase,
    CodexRegistrationReadyLease,
    CodexRegistrationTerminal,
    CodexRegistrationTransactionBlockReason,
    CodexRegistrationTransactionBlocked,
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


class CallPhase(str, Enum):
    FRESH = "FRESH"
    MARKETPLACE = "MARKETPLACE"
    PLUGIN = "PLUGIN"


class CallerTrap:
    """Fails if admission relies on caller equality, hashing, or representation."""

    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("caller protocol trap")

    def __eq__(self, other: object) -> bool:
        self._raise()

    def __hash__(self) -> int:
        self._raise()

    def __repr__(self) -> str:
        self._raise()


def preflight() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )


def request() -> CodexRegistrationPortRequest:
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


class SettlementAdapter:
    """Admitted in-memory operation fake; its proof operation must never run here."""

    def __init__(self) -> None:
        self.calls: list[CallPhase] = []
        self.fresh_rejected = False
        self.marketplace_started_failure = False
        self.plugin_started_failure = False
        self.raise_marketplace = False
        self.prove_count = 0

    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> object:
        self.calls.append(CallPhase.FRESH)
        if self.fresh_rejected:
            return CodexFreshPreflightRejected(request=current, reason=CodexBlockReason.ACCESS_DENIED)
        return CodexFreshPreflightAccepted(
            request=current,
            eligible=CodexPreflightEligible(version=current.expected_version),
        )

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> object:
        self.calls.append(CallPhase.MARKETPLACE)
        if self.raise_marketplace:
            raise RuntimeError("in-memory marketplace exception")
        if self.marketplace_started_failure:
            return CodexRegistrationCommandFailed(
                request=current,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    reason=CodexStartedFailureReason.NONZERO_EXIT,
                    start_state=CodexCommandStartState.STARTED,
                ),
            )
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

    def add_plugin(self, current: CodexRegistrationPortRequest) -> object:
        self.calls.append(CallPhase.PLUGIN)
        if self.plugin_started_failure:
            return CodexRegistrationCommandFailed(
                request=current,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    reason=CodexStartedFailureReason.NONZERO_EXIT,
                    start_state=CodexCommandStartState.STARTED,
                ),
            )
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
        self.prove_count += 1
        raise AssertionError("proof is outside terminal-claim authority")


def capability(adapter: SettlementAdapter) -> CodexRegistrationPortCapability:
    admitted = admit_codex_registration_port(adapter)
    if type(admitted) is not CodexRegistrationPortCapability:
        raise AssertionError("in-memory adapter was not admitted")
    return admitted


def forward(adapter: SettlementAdapter) -> CodexRegistrationForwardCoordinator:
    admitted = admit_codex_registration_forward(capability(adapter))
    if type(admitted) is not CodexRegistrationForwardCoordinator:
        raise AssertionError("admitted capability did not produce a forward coordinator")
    return admitted


def authority(adapter: SettlementAdapter) -> CodexRegistrationSettlementAuthority:
    admitted = admit_codex_registration_settlement_authority(forward(adapter))
    if type(admitted) is not CodexRegistrationSettlementAuthority:
        raise AssertionError("exact forward coordinator did not admit")
    return admitted


def ready(value: object) -> CodexRegistrationReadyLease:
    if type(value) is not CodexRegistrationReadyLease:
        raise AssertionError(f"expected ready lease, got {type(value).__name__}")
    return value


def next_ready(value: object) -> CodexRegistrationNextReadyPhase:
    if type(value) is not CodexRegistrationNextReadyPhase:
        raise AssertionError(f"expected next ready phase, got {type(value).__name__}")
    return value


def proof_claim(value: object) -> CodexRegistrationProofClaim:
    if type(value) is not CodexRegistrationProofClaim:
        raise AssertionError(f"expected proof claim, got {type(value).__name__}")
    return value


def compensation_claim(value: object) -> CodexRegistrationCompensationClaim:
    if type(value) is not CodexRegistrationCompensationClaim:
        raise AssertionError(f"expected compensation claim, got {type(value).__name__}")
    return value


def assert_authority_blocked(testcase: unittest.TestCase, value: object) -> None:
    testcase.assertIs(type(value), CodexRegistrationSettlementAuthorityBlocked)
    if type(value) is not CodexRegistrationSettlementAuthorityBlocked:
        raise AssertionError("expected settlement authority block")
    testcase.assertIs(value.reason, CodexRegistrationSettlementAuthorityRejectReason.INVALID_COORDINATOR)


def assert_claim_blocked(testcase: unittest.TestCase, value: object) -> None:
    testcase.assertIs(type(value), CodexRegistrationSettlementClaimBlocked)
    if type(value) is not CodexRegistrationSettlementClaimBlocked:
        raise AssertionError("expected settlement claim block")
    testcase.assertIs(value.reason, CodexRegistrationSettlementClaimBlockReason.INVALID_CLAIM)


def plugin_claim(current: CodexRegistrationSettlementAuthority) -> CodexRegistrationProofClaim:
    fresh = ready(current.begin(request()))
    marketplace = next_ready(current.execute(fresh.lease))
    plugin = next_ready(current.execute(marketplace.lease))
    return proof_claim(current.execute(plugin.lease))


class CodexRegistrationSettlementAuthorityTests(unittest.TestCase):
    """Finite C1-C8 evidence over admitted in-memory B2B coordinator fakes."""

    def test_c1_settlement_authority_module_is_required(self) -> None:
        self.assertTrue(callable(admit_codex_registration_settlement_authority))

    def test_c2_exact_forward_provenance_admits_without_effect_and_invalid_values_block(self) -> None:
        adapter = SettlementAdapter()
        live_forward = forward(adapter)
        admitted = admit_codex_registration_settlement_authority(live_forward)
        self.assertIs(type(admitted), CodexRegistrationSettlementAuthority)
        if type(admitted) is not CodexRegistrationSettlementAuthority:
            raise AssertionError("live forward coordinator did not admit")
        self.assertEqual(
            {"status": "SETTLEMENT_AUTHORITY_ADMITTED", "operation_count": 3},
            admitted.metadata().model_dump(),
        )
        trap = CallerTrap()
        invalid_values: tuple[object, ...] = (
            None,
            "text",
            (),
            [],
            {},
            trap,
            object.__new__(CodexRegistrationForwardCoordinator),
        )
        for invalid in invalid_values:
            with self.subTest(invalid_type=type(invalid).__name__):
                assert_authority_blocked(self, admit_codex_registration_settlement_authority(invalid))
        cloned_forward = object.__new__(CodexRegistrationForwardCoordinator)
        for slot in ("_token", "_capability", "_transaction"):
            object.__setattr__(
                cloned_forward,
                slot,
                object.__getattribute__(live_forward, slot),
            )
        assert_authority_blocked(self, admit_codex_registration_settlement_authority(cloned_forward))
        self.assertEqual(0, trap.invocation_count)
        self.assertEqual([], adapter.calls)
        with self.assertRaises(TypeError):
            CodexRegistrationSettlementAuthority(live_forward)
        wrapper_transfers: tuple[Callable[[], object], ...] = (
            lambda: copy.copy(admitted),
            lambda: copy.deepcopy(admitted),
            lambda: pickle.dumps(admitted),
            lambda: cast(Callable[[object], object], asdict)(admitted),
            lambda: cast(Callable[[object], object], astuple)(admitted),
            lambda: vars(admitted),
        )
        for transfer in wrapper_transfers:
            with self.subTest(transfer=transfer):
                with self.assertRaises(TypeError):
                    transfer()
        for forbidden in (
            "authority_registry",
            "claim_registry",
            "AuthorityRecord",
            "ClaimRecord",
            "_build_settlement_authority_system",
        ):
            self.assertFalse(hasattr(settlement_module, forbidden))

    def test_c3_forwards_ready_and_terminal_blocked_data_but_claims_exact_terminal_kinds(self) -> None:
        adapter = SettlementAdapter()
        current = authority(adapter)
        fresh = ready(current.begin(request()))
        marketplace = next_ready(current.execute(fresh.lease))
        self.assertEqual([CallPhase.FRESH], adapter.calls)
        plugin = next_ready(current.execute(marketplace.lease))
        claim = proof_claim(current.execute(plugin.lease))
        self.assertEqual([CallPhase.FRESH, CallPhase.MARKETPLACE, CallPhase.PLUGIN], adapter.calls)
        self.assertEqual(0, adapter.prove_count)
        self.assertIs(type(consume_codex_registration_proof_claim(claim)), CodexRegistrationProofRequired)

        blocked_adapter = SettlementAdapter()
        blocked_adapter.fresh_rejected = True
        blocked_current = authority(blocked_adapter)
        blocked_terminal = blocked_current.execute(ready(blocked_current.begin(request())).lease)
        self.assertIs(type(blocked_terminal), CodexRegistrationTerminal)
        if type(blocked_terminal) is CodexRegistrationTerminal:
            self.assertIs(type(blocked_terminal.decision), CodexRegistrationBlocked)
            if type(blocked_terminal.decision) is CodexRegistrationBlocked:
                self.assertIs(blocked_terminal.decision.reason, CodexRegistrationBlockReason.FRESH_PREFLIGHT_REJECTED)

        compensation_adapter = SettlementAdapter()
        compensation_current = authority(compensation_adapter)
        compensation_fresh = ready(compensation_current.begin(request()))
        compensation_marketplace = next_ready(compensation_current.execute(compensation_fresh.lease))
        compensation_adapter.marketplace_started_failure = True
        terminal_claim = compensation_claim(compensation_current.execute(compensation_marketplace.lease))
        self.assertIs(
            type(consume_codex_registration_compensation_claim(terminal_claim)),
            CodexRegistrationCompensationRequired,
        )

    def test_c3_started_add_recovery_becomes_compensation_claim_and_blocked_recovery_stays_exact(self) -> None:
        adapter = SettlementAdapter()
        current = authority(adapter)
        fresh = ready(current.begin(request()))
        marketplace = next_ready(current.execute(fresh.lease))
        adapter.raise_marketplace = True
        with self.assertRaises(RuntimeError):
            current.execute(marketplace.lease)
        recovered_claim = compensation_claim(current.recovery(marketplace.lease))
        self.assertEqual(2, recovered_claim.metadata().generation.value)
        recovered = consume_codex_registration_compensation_claim(recovered_claim)
        self.assertIs(type(recovered), CodexRegistrationAddRecovery)
        if type(recovered) is CodexRegistrationAddRecovery:
            self.assertIs(recovered.journal.marketplace_state, CodexAttemptEffectState.MAY_EXIST)
            self.assertIs(recovered.journal.plugin_state, CodexAttemptEffectState.NOT_ATTEMPTED)
            assert_claim_blocked(self, consume_codex_registration_compensation_claim(recovered))

        fresh_adapter = SettlementAdapter()
        fresh_current = authority(fresh_adapter)
        fresh_lease = ready(fresh_current.begin(request()))
        blocked = fresh_current.recovery(fresh_lease.lease)
        self.assertIs(type(blocked), CodexRegistrationTransactionBlocked)
        if type(blocked) is CodexRegistrationTransactionBlocked:
            self.assertIs(blocked.reason, CodexRegistrationTransactionBlockReason.PHASE_MISMATCH)

    def test_c4_claim_metadata_is_finite_and_transfer_fabrication_are_forbidden(self) -> None:
        adapter = SettlementAdapter()
        claim = plugin_claim(authority(adapter))
        metadata = claim.metadata()
        self.assertEqual("SETTLEMENT_CLAIM", metadata.status)
        self.assertIs(metadata.kind, CodexRegistrationSettlementClaimKind.PROOF)
        self.assertFalse(is_dataclass(claim))
        transfers: tuple[Callable[[], object], ...] = (
            lambda: copy.copy(claim),
            lambda: copy.deepcopy(claim),
            lambda: pickle.dumps(claim),
            lambda: cast(Callable[[object], object], asdict)(claim),
            lambda: cast(Callable[[object], object], astuple)(claim),
            lambda: vars(claim),
        )
        for transfer in transfers:
            with self.subTest(transfer=transfer):
                with self.assertRaises(TypeError):
                    transfer()
        with self.assertRaises(TypeError):
            CodexRegistrationProofClaim(metadata)
        public_text = repr(claim) + repr(metadata.model_dump())
        for forbidden in ("request", "plan", "receipt", "token", "authority", "SettlementAdapter"):
            self.assertNotIn(forbidden, public_text)
        fabricated = object.__new__(CodexRegistrationProofClaim)
        object.__setattr__(fabricated, "_metadata", metadata)
        assert_claim_blocked(self, consume_codex_registration_proof_claim(fabricated))
        assert_claim_blocked(self, consume_codex_registration_proof_claim(metadata))
        altered = plugin_claim(authority(SettlementAdapter()))
        altered_metadata = altered.metadata().model_copy(
            update={"kind": CodexRegistrationSettlementClaimKind.COMPENSATION}
        )
        object.__setattr__(altered, "_metadata", altered_metadata)
        assert_claim_blocked(self, consume_codex_registration_proof_claim(altered))
        trapped = plugin_claim(authority(SettlementAdapter()))
        metadata_trap = CallerTrap()
        object.__setattr__(trapped, "_metadata", metadata_trap)
        assert_claim_blocked(self, consume_codex_registration_proof_claim(trapped))
        self.assertEqual(0, metadata_trap.invocation_count)
        self.assertEqual(0, adapter.prove_count)

    def test_c5_kind_identity_and_atomic_tombstone_reject_wrong_clone_and_replay(self) -> None:
        current = authority(SettlementAdapter())
        claim = plugin_claim(current)
        assert_claim_blocked(self, consume_codex_registration_compensation_claim(claim))
        first = consume_codex_registration_proof_claim(claim)
        self.assertIs(type(first), CodexRegistrationProofRequired)
        assert_claim_blocked(self, consume_codex_registration_proof_claim(claim))

        other_claim = plugin_claim(authority(SettlementAdapter()))
        cloned = object.__new__(CodexRegistrationProofClaim)
        object.__setattr__(cloned, "_metadata", other_claim.metadata())
        assert_claim_blocked(self, consume_codex_registration_proof_claim(cloned))

    def test_c6_duplicate_consume_is_synchronized_and_owner_collection_reclaims_claim(self) -> None:
        current = authority(SettlementAdapter())
        claim = plugin_claim(current)
        with ThreadPoolExecutor(max_workers=2) as executor:
            first_future = executor.submit(consume_codex_registration_proof_claim, claim)
            second_future = executor.submit(consume_codex_registration_proof_claim, claim)
            results = (first_future.result(timeout=5.0), second_future.result(timeout=5.0))
        self.assertEqual(1, sum(type(value) is CodexRegistrationProofRequired for value in results))
        self.assertEqual(1, sum(type(value) is CodexRegistrationSettlementClaimBlocked for value in results))

        owner = authority(SettlementAdapter())
        unconsumed = plugin_claim(owner)
        owner_reference = ref(owner)
        del owner
        gc.collect()
        self.assertIsNone(owner_reference())
        assert_claim_blocked(self, consume_codex_registration_proof_claim(unconsumed))

    def test_c8_reverse_exact_b2b_provenance_blocks_unregistered_settlement_wrapper(self) -> None:
        adapter = SettlementAdapter()
        current = authority(adapter)
        forged = object.__new__(CodexRegistrationSettlementAuthority)
        object.__setattr__(forged, "_coordinator", object.__getattribute__(current, "_coordinator"))
        assert_authority_blocked(self, forged.begin(request()))
        self.assertEqual([], adapter.calls)

    def test_c8_reverse_terminal_and_recovery_kind_classification_issues_only_matching_claims(self) -> None:
        proof_adapter = SettlementAdapter()
        self.assertIs(type(plugin_claim(authority(proof_adapter))), CodexRegistrationProofClaim)

        terminal_adapter = SettlementAdapter()
        terminal_current = authority(terminal_adapter)
        terminal_adapter.plugin_started_failure = True
        fresh = ready(terminal_current.begin(request()))
        marketplace = next_ready(terminal_current.execute(fresh.lease))
        plugin = next_ready(terminal_current.execute(marketplace.lease))
        compensation = compensation_claim(terminal_current.execute(plugin.lease))
        assert_claim_blocked(self, consume_codex_registration_proof_claim(compensation))
        self.assertIs(
            type(consume_codex_registration_compensation_claim(compensation)),
            CodexRegistrationCompensationRequired,
        )

        recovery_adapter = SettlementAdapter()
        recovery_current = authority(recovery_adapter)
        recovery_fresh = ready(recovery_current.begin(request()))
        recovery_marketplace = next_ready(recovery_current.execute(recovery_fresh.lease))
        recovery_adapter.raise_marketplace = True
        with self.assertRaises(RuntimeError):
            recovery_current.execute(recovery_marketplace.lease)
        self.assertIs(
            type(recovery_current.recovery(recovery_marketplace.lease)),
            CodexRegistrationCompensationClaim,
        )

    def test_c8_reverse_atomic_tombstone_blocks_the_second_identical_claim_consume(self) -> None:
        current = authority(SettlementAdapter())
        claim = plugin_claim(current)
        self.assertIs(type(consume_codex_registration_proof_claim(claim)), CodexRegistrationProofRequired)
        assert_claim_blocked(self, consume_codex_registration_proof_claim(claim))

    def test_c8_reverse_claim_kind_identity_blocks_cross_kind_consume(self) -> None:
        current = authority(SettlementAdapter())
        claim = plugin_claim(current)
        assert_claim_blocked(self, consume_codex_registration_compensation_claim(claim))
        self.assertIs(type(consume_codex_registration_proof_claim(claim)), CodexRegistrationProofRequired)

    def test_c8_reverse_lexical_closure_hides_all_mutable_registration_surface(self) -> None:
        forbidden_surface = (
            "authority_registry",
            "claim_registry",
            "AuthorityRecord",
            "ClaimRecord",
            "register",
            "reclaim",
            "_build_settlement_authority_system",
        )
        for name in forbidden_surface:
            with self.subTest(name=name):
                self.assertFalse(hasattr(settlement_module, name))
