"""T1-T8 closure for process-local Codex registration transaction authority."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import ntpath
import pickle
from threading import Barrier
from typing import NoReturn
import unittest

from library.local_orchestration.codex_command_attempts import (
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAttemptEffectState,
    CodexAuthPolicy,
    CodexMarketplaceAddObservation,
    CodexObservedAbsolutePath,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationAttemptId,
)
from library.local_orchestration.codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddSucceeded,
    CodexRegistrationPortRequest,
)
from library.local_orchestration.codex_registration_reducer import (
    CodexFreshPreflightPending,
    CodexMarketplaceAddPending,
    CodexPluginAddPending,
    CodexRegistrationBlocked,
    CodexRegistrationProofRequired,
    begin_codex_registration,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationAddRecovery,
    CodexRegistrationGeneration,
    CodexRegistrationLeaseMetadata,
    CodexRegistrationNextReadyPhase,
    CodexRegistrationPhase,
    CodexRegistrationPhaseLease,
    CodexRegistrationReadyLease,
    CodexRegistrationStartedPhase,
    CodexRegistrationTerminal,
    CodexRegistrationTransactionBlockReason,
    CodexRegistrationTransactionBlocked,
    CodexRegistrationTransactionCoordinator,
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
MARKETPLACE = CodexMarketplaceName(value="probe-market")
PLUGIN = CodexPluginName(value="probe-plugin")
SOURCE = OwnedRelativePath(value="marketplaces/probe-market")
INSTALLED = OwnedRelativePath(value="plugins/probe-plugin")
VERSION = CodexCliVersion(value="1.2.3")
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")
OTHER_ATTEMPT = CodexRegistrationAttemptId(value="attempt-fedcba9876543210")
DIGEST = ArtifactDigest(value="a" * 64)
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")
PLUGIN_ID = CodexPluginId(value="plugin-probe-012345")


class PlainTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("caller trap invoked")

    def __eq__(self, other: object) -> bool:
        self._raise()

    def __repr__(self) -> str:
        self._raise()

    def __str__(self) -> str:
        self._raise()

    def __iter__(self) -> NoReturn:
        self._raise()


class CallerProtocolTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self, message: str) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError(message)


class ComparisonTrap(CallerProtocolTrap):
    def __eq__(self, other: object) -> bool:
        self._raise("comparison trap")


class HashEqualityTrap(CallerProtocolTrap):
    def __hash__(self) -> int:
        self._raise("hash trap")

    def __eq__(self, other: object) -> bool:
        self._raise("equality trap")


def preflight() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )


def request(attempt_id: CodexRegistrationAttemptId = ATTEMPT) -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=preflight(),
        attempt_id=attempt_id,
        expected_version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=PLUGIN_ID,
    )


def constructed_invalid_request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest.model_construct(
        preflight=preflight(),
        attempt_id=ATTEMPT,
        expected_version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=PLUGIN_ID.value,
    )


def missing_request_field() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest.model_construct(
        preflight=preflight(),
        attempt_id=ATTEMPT,
        expected_version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
    )


def observed_path(locator: OwnedRelativePath) -> CodexObservedAbsolutePath:
    return CodexObservedAbsolutePath(value=ntpath.join(ntpath.expandvars(CANONICAL_INSTALL_ROOT), *locator.parts()))


def fresh_accepted(current: CodexRegistrationPortRequest) -> CodexFreshPreflightAccepted:
    return CodexFreshPreflightAccepted(
        request=current,
        eligible=CodexPreflightEligible(version=current.expected_version),
    )


def marketplace_success(current: CodexRegistrationPortRequest) -> CodexMarketplaceAddSucceeded:
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


def plugin_success(current: CodexRegistrationPortRequest) -> CodexPluginAddSucceeded:
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


def expect_ready(value: object) -> CodexRegistrationReadyLease:
    if not isinstance(value, CodexRegistrationReadyLease):
        raise AssertionError(f"expected initial ready lease, received {type(value).__name__}")
    return value


def expect_next(value: object) -> CodexRegistrationNextReadyPhase:
    if not isinstance(value, CodexRegistrationNextReadyPhase):
        raise AssertionError(f"expected next ready phase, received {type(value).__name__}")
    return value


def expect_started(value: object) -> CodexRegistrationStartedPhase:
    if not isinstance(value, CodexRegistrationStartedPhase):
        raise AssertionError(f"expected started phase, received {type(value).__name__}")
    return value


def expect_terminal(value: object) -> CodexRegistrationTerminal:
    if not isinstance(value, CodexRegistrationTerminal):
        raise AssertionError(f"expected terminal, received {type(value).__name__}")
    return value


def assert_blocked(
    testcase: unittest.TestCase,
    value: object,
    reason: CodexRegistrationTransactionBlockReason,
) -> None:
    testcase.assertIsInstance(value, CodexRegistrationTransactionBlocked)
    if not isinstance(value, CodexRegistrationTransactionBlocked):
        raise AssertionError(f"expected transaction block, received {type(value).__name__}")
    testcase.assertEqual(reason, value.reason)


def advance_to_marketplace(
    coordinator: CodexRegistrationTransactionCoordinator,
    initial: CodexRegistrationReadyLease,
) -> CodexRegistrationNextReadyPhase:
    expect_started(coordinator.start(initial.lease))
    return expect_next(coordinator.complete(initial.lease, fresh_accepted(initial.pending.request)))


def advance_to_plugin(
    coordinator: CodexRegistrationTransactionCoordinator,
    initial: CodexRegistrationReadyLease,
) -> CodexRegistrationNextReadyPhase:
    marketplace = advance_to_marketplace(coordinator, initial)
    expect_started(coordinator.start(marketplace.lease))
    return expect_next(coordinator.complete(marketplace.lease, marketplace_success(marketplace.pending.request)))


def complete_exact_proof(
    coordinator: CodexRegistrationTransactionCoordinator,
    initial: CodexRegistrationReadyLease,
) -> CodexRegistrationTerminal:
    plugin = advance_to_plugin(coordinator, initial)
    expect_started(coordinator.start(plugin.lease))
    return expect_terminal(coordinator.complete(plugin.lease, plugin_success(plugin.pending.request)))


class CodexRegistrationTransactionTests(unittest.TestCase):
    def test_t1_absent_transaction_authority_module_is_required(self) -> None:
        self.assertTrue(callable(CodexRegistrationTransactionCoordinator))

    def test_t2_begin_rebuilds_fresh_and_rejects_invalid_and_live_duplicates(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        supplied = request()
        expected = begin_codex_registration(supplied)
        ready = expect_ready(coordinator.begin(supplied))
        self.assertEqual(CodexRegistrationPhase.FRESH_PREFLIGHT, ready.lease.metadata().phase)
        self.assertEqual(1, ready.lease.metadata().generation.value)
        self.assertIsInstance(ready.pending, CodexFreshPreflightPending)
        self.assertIsNot(expected, ready.pending)
        if not isinstance(expected, CodexFreshPreflightPending):
            raise AssertionError("expected B1 fresh pending")
        self.assertEqual(expected.model_dump(), ready.pending.model_dump())
        assert_blocked(
            self,
            coordinator.begin(supplied),
            CodexRegistrationTransactionBlockReason.DUPLICATE_ATTEMPT,
        )

        trap = PlainTrap()
        invalid_values: tuple[object, ...] = (
            missing_request_field(),
            None,
            "",
            " ",
            [],
            {},
            trap,
            constructed_invalid_request(),
        )
        for value in invalid_values:
            with self.subTest(shape=type(value).__name__):
                assert_blocked(
                    self,
                    CodexRegistrationTransactionCoordinator().begin(value),
                    CodexRegistrationTransactionBlockReason.INVALID_REQUEST,
                )
        self.assertEqual(0, trap.invocation_count)

    def test_t3_t7_atomic_duplicate_start_exclusion(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        ready = expect_ready(coordinator.begin(request()))
        barrier = Barrier(3)

        def start_once() -> CodexRegistrationStartedPhase | CodexRegistrationTransactionBlocked:
            barrier.wait()
            return coordinator.start(ready.lease)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = (executor.submit(start_once), executor.submit(start_once))
            barrier.wait()
            outcomes = [future.result(timeout=5) for future in futures]
        self.assertEqual(1, sum(isinstance(value, CodexRegistrationStartedPhase) for value in outcomes))
        replayed = [value for value in outcomes if isinstance(value, CodexRegistrationTransactionBlocked)]
        self.assertEqual(1, len(replayed))
        self.assertEqual(CodexRegistrationTransactionBlockReason.REPLAYED, replayed[0].reason)

    def test_t4_three_phases_use_monotonic_generations_and_terminal_replay_blocks(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        fresh = expect_ready(coordinator.begin(request()))
        marketplace = advance_to_marketplace(coordinator, fresh)
        plugin = advance_to_plugin_from_marketplace(coordinator, marketplace)
        self.assertEqual(1, fresh.lease.metadata().generation.value)
        self.assertEqual(2, marketplace.lease.metadata().generation.value)
        self.assertEqual(3, plugin.lease.metadata().generation.value)
        self.assertEqual(CodexRegistrationPhase.FRESH_PREFLIGHT, fresh.lease.metadata().phase)
        self.assertEqual(CodexRegistrationPhase.MARKETPLACE_ADD, marketplace.lease.metadata().phase)
        self.assertEqual(CodexRegistrationPhase.PLUGIN_ADD, plugin.lease.metadata().phase)
        expect_started(coordinator.start(plugin.lease))
        terminal = expect_terminal(coordinator.complete(plugin.lease, plugin_success(plugin.pending.request)))
        self.assertIsInstance(terminal.decision, CodexRegistrationProofRequired)
        assert_blocked(self, coordinator.start(fresh.lease), CodexRegistrationTransactionBlockReason.REPLAYED)
        assert_blocked(
            self,
            coordinator.complete(plugin.lease, plugin_success(plugin.pending.request)),
            CodexRegistrationTransactionBlockReason.REPLAYED,
        )
        assert_blocked(
            self,
            coordinator.complete(marketplace.lease, marketplace_success(marketplace.pending.request)),
            CodexRegistrationTransactionBlockReason.REPLAYED,
        )

    def test_t4_t7_generation_equality_is_required(self) -> None:
        for delta in (-1, 1):
            with self.subTest(delta=delta):
                coordinator = CodexRegistrationTransactionCoordinator()
                fresh = expect_ready(coordinator.begin(request()))
                ready = advance_to_marketplace(coordinator, fresh)
                metadata = ready.lease.metadata()
                object.__setattr__(
                    ready.lease,
                    "_metadata",
                    CodexRegistrationLeaseMetadata(
                        attempt_id=metadata.attempt_id,
                        phase=metadata.phase,
                        generation=CodexRegistrationGeneration(value=metadata.generation.value + delta),
                    ),
                )
                assert_blocked(self, coordinator.start(ready.lease), CodexRegistrationTransactionBlockReason.REPLAYED)

    def test_t4_wrong_phase_and_never_started_complete_block_finitely(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        fresh = expect_ready(coordinator.begin(request()))
        assert_blocked(
            self,
            coordinator.complete(fresh.lease, fresh_accepted(fresh.pending.request)),
            CodexRegistrationTransactionBlockReason.INVALID_STATE,
        )
        metadata = fresh.lease.metadata()
        object.__setattr__(
            fresh.lease,
            "_metadata",
            CodexRegistrationLeaseMetadata(
                attempt_id=metadata.attempt_id,
                phase=CodexRegistrationPhase.MARKETPLACE_ADD,
                generation=metadata.generation,
            ),
        )
        assert_blocked(
            self,
            coordinator.start(fresh.lease),
            CodexRegistrationTransactionBlockReason.PHASE_MISMATCH,
        )

        wrong_result_coordinator = CodexRegistrationTransactionCoordinator()
        wrong_result_ready = expect_ready(wrong_result_coordinator.begin(request()))
        expect_started(wrong_result_coordinator.start(wrong_result_ready.lease))
        terminal = expect_terminal(
            wrong_result_coordinator.complete(
                wrong_result_ready.lease,
                marketplace_success(wrong_result_ready.pending.request),
            )
        )
        self.assertIsInstance(terminal.decision, CodexRegistrationBlocked)

    def test_t5_lease_transfer_fabrication_and_metadata_are_not_authority(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        ready = expect_ready(coordinator.begin(request()))
        for label, transfer in (
            ("copy", lambda: copy.copy(ready.lease)),
            ("deepcopy", lambda: copy.deepcopy(ready.lease)),
            ("pickle", lambda: pickle.loads(pickle.dumps(ready.lease))),
        ):
            with self.subTest(transfer=label):
                with self.assertRaisesRegex(TypeError, "transaction lease transfer is forbidden"):
                    transfer()
        with self.assertRaisesRegex(TypeError, "transaction lease construction is forbidden"):
            CodexRegistrationPhaseLease(object(), coordinator, ready.lease.metadata())
        with self.assertRaisesRegex(TypeError, "transaction lease construction is forbidden"):
            CodexRegistrationPhaseLease(ready.lease._token, coordinator, ready.lease.metadata())

        metadata = ready.lease.metadata()
        assert_blocked(self, coordinator.start(metadata), CodexRegistrationTransactionBlockReason.INVALID_LEASE)
        forged = object.__new__(CodexRegistrationPhaseLease)
        assert_blocked(self, coordinator.start(forged), CodexRegistrationTransactionBlockReason.INVALID_LEASE)

        for label, attempt_id in (
            ("case", CodexRegistrationAttemptId.model_construct(value=ATTEMPT.value.upper())),
            ("prefix", CodexRegistrationAttemptId.model_construct(value=ATTEMPT.value + "x")),
            ("unrelated", OTHER_ATTEMPT),
        ):
            with self.subTest(attempt_id=label):
                fabricated = object.__new__(CodexRegistrationPhaseLease)
                object.__setattr__(fabricated, "_token", ready.lease._token)
                object.__setattr__(fabricated, "_owner", coordinator)
                object.__setattr__(
                    fabricated,
                    "_metadata",
                    CodexRegistrationLeaseMetadata.model_construct(
                        attempt_id=attempt_id,
                        phase=metadata.phase,
                        generation=metadata.generation,
                    ),
                )
                assert_blocked(
                    self,
                    coordinator.start(fabricated),
                    CodexRegistrationTransactionBlockReason.INVALID_LEASE,
                )

        safe_text = f"{ready.lease.metadata().model_dump()} {repr(ready.lease)}".casefold()
        for forbidden in ("operation", "callable", "raw_output", "\\", "secret", "receipt"):
            self.assertNotIn(forbidden, safe_text)

    def test_cr150_t5_caller_protocol_traps_block_without_invocation(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        ready = expect_ready(coordinator.begin(request()))
        exact = ready.lease.metadata()
        comparison_trap = ComparisonTrap()
        hash_trap = HashEqualityTrap()
        trapped_attempt = CodexRegistrationAttemptId.model_construct(value=hash_trap)
        cases: tuple[tuple[str, CodexRegistrationLeaseMetadata, CallerProtocolTrap], ...] = (
            (
                "status-comparison",
                CodexRegistrationLeaseMetadata.model_construct(
                    status=comparison_trap,
                    attempt_id=exact.attempt_id,
                    phase=exact.phase,
                    generation=exact.generation,
                ),
                comparison_trap,
            ),
            (
                "attempt-hash",
                CodexRegistrationLeaseMetadata.model_construct(
                    attempt_id=trapped_attempt,
                    phase=exact.phase,
                    generation=exact.generation,
                ),
                hash_trap,
            ),
        )
        for label, metadata, trap in cases:
            with self.subTest(cell=label):
                fabricated = object.__new__(CodexRegistrationPhaseLease)
                object.__setattr__(fabricated, "_token", ready.lease._token)
                object.__setattr__(fabricated, "_owner", coordinator)
                object.__setattr__(fabricated, "_metadata", metadata)
                assert_blocked(
                    self,
                    coordinator.start(fabricated),
                    CodexRegistrationTransactionBlockReason.INVALID_LEASE,
                )
                self.assertEqual(0, trap.invocation_count)

    def test_t5_t7_owning_coordinator_identity_is_required(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        other = CodexRegistrationTransactionCoordinator()
        ready = expect_ready(coordinator.begin(request()))
        assert_blocked(self, other.start(ready.lease), CodexRegistrationTransactionBlockReason.INVALID_LEASE)
        object.__setattr__(ready.lease, "_owner", other)
        assert_blocked(self, coordinator.start(ready.lease), CodexRegistrationTransactionBlockReason.INVALID_LEASE)

    def test_t2_t7_terminal_tombstone_retains_duplicate_attempt_id(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        complete_exact_proof(coordinator, expect_ready(coordinator.begin(request())))
        assert_blocked(
            self,
            coordinator.begin(request()),
            CodexRegistrationTransactionBlockReason.DUPLICATE_ATTEMPT,
        )

    def test_t6_t7_started_add_recovery_is_conservative(self) -> None:
        coordinator = CodexRegistrationTransactionCoordinator()
        fresh = expect_ready(coordinator.begin(request()))
        expect_started(coordinator.start(fresh.lease))
        assert_blocked(
            self,
            coordinator.recovery(fresh.lease),
            CodexRegistrationTransactionBlockReason.PHASE_MISMATCH,
        )
        marketplace = expect_next(coordinator.complete(fresh.lease, fresh_accepted(fresh.pending.request)))
        assert_blocked(
            self,
            coordinator.recovery(marketplace.lease),
            CodexRegistrationTransactionBlockReason.INVALID_STATE,
        )
        expect_started(coordinator.start(marketplace.lease))
        marketplace_recovery = coordinator.recovery(marketplace.lease)
        self.assertIsInstance(marketplace_recovery, CodexRegistrationAddRecovery)
        if not isinstance(marketplace_recovery, CodexRegistrationAddRecovery):
            raise AssertionError("expected marketplace recovery")
        self.assertEqual(marketplace.pending.request.model_dump(), marketplace_recovery.request.model_dump())
        self.assertEqual(marketplace.pending.request.attempt_id, marketplace_recovery.journal.attempt_id)
        self.assertEqual(CodexAttemptEffectState.MAY_EXIST, marketplace_recovery.journal.marketplace_state)
        self.assertEqual(CodexAttemptEffectState.NOT_ATTEMPTED, marketplace_recovery.journal.plugin_state)
        plugin = expect_next(
            coordinator.complete(marketplace.lease, marketplace_success(marketplace.pending.request))
        )
        expect_started(coordinator.start(plugin.lease))
        plugin_recovery = coordinator.recovery(plugin.lease)
        self.assertIsInstance(plugin_recovery, CodexRegistrationAddRecovery)
        if not isinstance(plugin_recovery, CodexRegistrationAddRecovery):
            raise AssertionError("expected plugin recovery")
        self.assertEqual(CodexAttemptEffectState.OWNED, plugin_recovery.journal.marketplace_state)
        self.assertEqual(CodexAttemptEffectState.MAY_EXIST, plugin_recovery.journal.plugin_state)
        self.assertEqual(plugin.pending.request.model_dump(), plugin_recovery.request.model_dump())
        self.assertEqual(plugin.pending.request.attempt_id, plugin_recovery.journal.attempt_id)


def advance_to_plugin_from_marketplace(
    coordinator: CodexRegistrationTransactionCoordinator,
    marketplace: CodexRegistrationNextReadyPhase,
) -> CodexRegistrationNextReadyPhase:
    expect_started(coordinator.start(marketplace.lease))
    return expect_next(coordinator.complete(marketplace.lease, marketplace_success(marketplace.pending.request)))


if __name__ == "__main__":
    unittest.main()
