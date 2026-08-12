"""S1-S9 closure for Codex registration compensation settlement."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import ntpath
from typing import NoReturn, cast
import unittest

from library.local_orchestration.codex_command_attempts import (
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexStartedFailure,
    CodexStartedFailureReason,
)
from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortManifest,
    CodexCompensationPortRejected,
    CodexCompensationPortRequest,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
)
from library.local_orchestration.codex_compensation_reducer import (
    CodexCompensated,
    CodexCompensationFailed,
    CodexCompensationResult,
    CodexCompensationPlan,
    build_compensation_plan,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexMarketplaceAddObservation,
    CodexObservedAbsolutePath,
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
    CodexMarketplaceAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortCapability,
    CodexRegistrationPortRequest,
    admit_codex_registration_port,
)
from library.local_orchestration.codex_registration_reducer import (
    CodexRegistrationCompensationRequired,
)
from library.local_orchestration.codex_registration_settlement_authority import (
    CodexRegistrationCompensationClaim,
    CodexRegistrationProofClaim,
    CodexRegistrationSettlementAuthority,
    CodexRegistrationSettlementClaimBlocked,
    CodexRegistrationSettlementClaimBlockReason,
    admit_codex_registration_settlement_authority,
    consume_codex_registration_compensation_claim,
)
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationAddRecovery,
    CodexRegistrationNextReadyPhase,
    CodexRegistrationPhase,
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
    CodexMarketplaceList,
    CodexMarketplaceName,
    CodexPluginList,
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


_LIVE_AUTHORITIES: list[CodexRegistrationSettlementAuthority] = []


class CompensationOperation(str, Enum):
    REMOVE_PLUGIN = "REMOVE_PLUGIN"
    REMOVE_MARKETPLACE = "REMOVE_MARKETPLACE"
    LIST_PLUGINS = "LIST_PLUGINS"
    LIST_MARKETPLACES = "LIST_MARKETPLACES"
    PROVE_INSTALLED_PATH_ABSENT = "PROVE_INSTALLED_PATH_ABSENT"


class RaisedOperation(str, Enum):
    NONE = "NONE"
    RUNTIME = "RUNTIME"
    MEMORY = "MEMORY"
    KEYBOARD = "KEYBOARD"
    EXIT = "EXIT"


class CallerTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def _raise(self) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("caller protocol trap")

    def __getattr__(self, name: str) -> NoReturn:
        self._raise()

    def __eq__(self, other: object) -> bool:
        self._raise()

    def __hash__(self) -> int:
        self._raise()

    def __repr__(self) -> str:
        self._raise()


class PropertyPort:
    @property
    def remove_plugin(self) -> NoReturn:
        raise RuntimeError("descriptor must not execute")


def preflight() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )


def registration_request() -> CodexRegistrationPortRequest:
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


class RegistrationAdapter:
    """Exact in-memory registration fake that can issue terminal/recovery claims."""

    def __init__(self) -> None:
        self.marketplace_started_failure = False
        self.raise_marketplace = False

    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> CodexFreshPreflightAccepted:
        return CodexFreshPreflightAccepted(
            request=current,
            eligible=CodexPreflightEligible(version=current.expected_version),
        )

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> object:
        if self.raise_marketplace:
            raise RuntimeError("in-memory registration failure")
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
        raise AssertionError("plugin registration is not needed for compensation claims")

    def prove(self, current: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        raise AssertionError("proof settlement is outside this ticket")


class RecordingCompensationPort:
    """Admissible in-memory compensation capability with deterministic outcomes."""

    def __init__(self) -> None:
        self.calls: list[CompensationOperation] = []
        self.requests: list[CodexCompensationPortRequest] = []
        self.raised = RaisedOperation.NONE
        self.malformed_marketplace_removal = False

    def _record(self, operation: CompensationOperation, current: CodexCompensationPortRequest) -> None:
        self.calls.append(operation)
        self.requests.append(current)
        if self.raised is RaisedOperation.RUNTIME:
            raise RuntimeError("compensation runtime failure")
        if self.raised is RaisedOperation.MEMORY:
            raise MemoryError()
        if self.raised is RaisedOperation.KEYBOARD:
            raise KeyboardInterrupt()
        if self.raised is RaisedOperation.EXIT:
            raise SystemExit()

    def remove_plugin(self, current: CodexCompensationPortRequest) -> CodexPluginRemovalProof:
        self._record(CompensationOperation.REMOVE_PLUGIN, current)
        return CodexPluginRemovalProof(manifest=current.manifest, status="REMOVED")

    def remove_marketplace(self, current: CodexCompensationPortRequest) -> CodexMarketplaceRemovalProof:
        self._record(CompensationOperation.REMOVE_MARKETPLACE, current)
        if self.malformed_marketplace_removal:
            return cast(CodexMarketplaceRemovalProof, object())
        return CodexMarketplaceRemovalProof(manifest=current.manifest, status="REMOVED")

    def list_plugins(self, current: CodexCompensationPortRequest) -> CodexPluginList:
        self._record(CompensationOperation.LIST_PLUGINS, current)
        return CodexPluginList(installed=(), available=())

    def list_marketplaces(self, current: CodexCompensationPortRequest) -> CodexMarketplaceList:
        self._record(CompensationOperation.LIST_MARKETPLACES, current)
        return CodexMarketplaceList(marketplaces=())

    def prove_installed_path_absent(self, current: CodexCompensationPortRequest) -> CodexInstalledPathAbsenceProof:
        self._record(CompensationOperation.PROVE_INSTALLED_PATH_ABSENT, current)
        return CodexInstalledPathAbsenceProof(manifest=current.manifest, absent=True)


def registration_capability(adapter: RegistrationAdapter) -> CodexRegistrationPortCapability:
    admitted = admit_codex_registration_port(adapter)
    if type(admitted) is not CodexRegistrationPortCapability:
        raise AssertionError("registration adapter did not admit")
    return admitted


def authority(adapter: RegistrationAdapter) -> CodexRegistrationSettlementAuthority:
    forward = admit_codex_registration_forward(registration_capability(adapter))
    if type(forward) is not CodexRegistrationForwardCoordinator:
        raise AssertionError("forward coordinator did not admit")
    admitted = admit_codex_registration_settlement_authority(forward)
    if type(admitted) is not CodexRegistrationSettlementAuthority:
        raise AssertionError("settlement authority did not admit")
    _LIVE_AUTHORITIES.append(admitted)
    return admitted


def _live_authority(adapter: RegistrationAdapter) -> tuple[
    CodexRegistrationSettlementAuthority,
    CodexRegistrationReadyLease,
]:
    current = authority(adapter)
    return current, ready(current.begin(registration_request()))


def ready(value: object) -> CodexRegistrationReadyLease:
    if type(value) is not CodexRegistrationReadyLease:
        raise AssertionError(f"expected ready lease, got {type(value).__name__}")
    return value


def next_ready(value: object) -> CodexRegistrationNextReadyPhase:
    if type(value) is not CodexRegistrationNextReadyPhase:
        raise AssertionError(f"expected next ready phase, got {type(value).__name__}")
    return value


def terminal_claim() -> CodexRegistrationCompensationClaim:
    adapter = RegistrationAdapter()
    current, fresh = _live_authority(adapter)
    marketplace = next_ready(current.execute(fresh.lease))
    adapter.marketplace_started_failure = True
    claim = current.execute(marketplace.lease)
    if type(claim) is not CodexRegistrationCompensationClaim:
        raise AssertionError(f"expected terminal compensation claim, got {type(claim).__name__}")
    return claim


def recovery_claim() -> CodexRegistrationCompensationClaim:
    adapter = RegistrationAdapter()
    current, fresh = _live_authority(adapter)
    marketplace = next_ready(current.execute(fresh.lease))
    adapter.raise_marketplace = True
    with unittest.TestCase().assertRaises(RuntimeError):
        current.execute(marketplace.lease)
    claim = current.recovery(marketplace.lease)
    if type(claim) is not CodexRegistrationCompensationClaim:
        raise AssertionError(f"expected recovery compensation claim, got {type(claim).__name__}")
    return claim


def assert_claim_blocked(testcase: unittest.TestCase, value: object) -> None:
    testcase.assertIs(type(value), CodexRegistrationSettlementClaimBlocked)
    if type(value) is not CodexRegistrationSettlementClaimBlocked:
        raise AssertionError("expected claim block")
    testcase.assertIs(value.reason, CodexRegistrationSettlementClaimBlockReason.INVALID_CLAIM)


def assert_compensated(testcase: unittest.TestCase, value: object) -> CodexCompensated:
    testcase.assertIs(type(value), CodexCompensated)
    if type(value) is not CodexCompensated:
        raise AssertionError(f"expected compensation result, got {type(value).__name__}")
    return value


def assert_manifest(testcase: unittest.TestCase, actual: CodexCompensationPortManifest) -> None:
    testcase.assertEqual(INSTALLATION.value, actual.installation_id.value)
    testcase.assertEqual(ROOT.value, actual.root.value)
    testcase.assertEqual(MARKETPLACE.value, actual.marketplace.value)
    testcase.assertEqual(SOURCE.value, actual.marketplace_source.value)
    testcase.assertEqual(PLUGIN_ID.value, actual.plugin_id.value)
    testcase.assertEqual(PLUGIN.value, actual.plugin.value)
    testcase.assertEqual(VERSION.value, actual.version.value)
    testcase.assertEqual(INSTALLED.value, actual.installed_locator.value)
    testcase.assertEqual(AUTH_POLICY.value, actual.auth_policy.value)
    testcase.assertEqual(DIGEST.value, actual.digest.value)


class CodexRegistrationCompensationSettlementTests(unittest.TestCase):
    def test_s1_compensation_settlement_module_is_required(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            settle_codex_registration_compensation,
        )

        self.assertTrue(callable(settle_codex_registration_compensation))

    def test_s2_invalid_port_admission_leaves_the_live_claim_unconsumed(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            settle_codex_registration_compensation,
        )

        invalid_candidates: tuple[object, ...] = (None, "", " ", [], {}, CallerTrap(), PropertyPort())
        for candidate in invalid_candidates:
            with self.subTest(candidate=type(candidate).__name__):
                claim = terminal_claim()
                result = settle_codex_registration_compensation(claim, candidate)
                self.assertIs(type(result), CodexCompensationPortRejected)
                valid_port = RecordingCompensationPort()
                assert_compensated(self, settle_codex_registration_compensation(claim, valid_port))
                self.assertEqual(4, len(valid_port.calls))
        trap = invalid_candidates[5]
        if type(trap) is CallerTrap:
            self.assertEqual(0, trap.invocation_count)

    def test_s3_only_a_live_compensation_claim_can_reach_composition_once(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            settle_codex_registration_compensation,
        )

        live = terminal_claim()
        metadata = live.metadata()
        fabricated = object.__new__(CodexRegistrationCompensationClaim)
        object.__setattr__(fabricated, "_metadata", metadata)
        altered = terminal_claim()
        altered_metadata = object.__getattribute__(altered, "_metadata")
        object.__setattr__(altered_metadata, "phase", CodexRegistrationPhase.FRESH_PREFLIGHT)
        raw_terminal = CodexRegistrationCompensationRequired.model_construct()
        raw_recovery = CodexRegistrationAddRecovery.model_construct()
        wrong_kind = object.__new__(CodexRegistrationProofClaim)
        foreign = object.__new__(CodexRegistrationCompensationClaim)
        invalid_claims: tuple[object, ...] = (
            None,
            "",
            [],
            {},
            metadata,
            raw_terminal,
            raw_recovery,
            wrong_kind,
            foreign,
            fabricated,
            altered,
        )
        for invalid in invalid_claims:
            with self.subTest(claim=type(invalid).__name__):
                port = RecordingCompensationPort()
                assert_claim_blocked(self, settle_codex_registration_compensation(invalid, port))
                self.assertEqual([], port.calls)

        port = RecordingCompensationPort()
        assert_compensated(self, settle_codex_registration_compensation(live, port))
        call_count = len(port.calls)
        assert_claim_blocked(self, settle_codex_registration_compensation(live, port))
        self.assertEqual(call_count, len(port.calls))

    def test_s4_terminal_claim_derives_every_manifest_field_and_uses_its_plan(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            _terminal_context,
            settle_codex_registration_compensation,
        )

        claim = terminal_claim()
        decision = consume_codex_registration_compensation_claim(claim)
        self.assertIs(type(decision), CodexRegistrationCompensationRequired)
        if type(decision) is not CodexRegistrationCompensationRequired:
            raise AssertionError("expected consumed terminal compensation decision")
        context = _terminal_context(decision)
        self.assertIs(type(context), tuple)
        if type(context) is not tuple:
            raise AssertionError("expected terminal settlement context")
        self.assertIs(context[1], decision.plan)

        port = RecordingCompensationPort()
        assert_compensated(self, settle_codex_registration_compensation(terminal_claim(), port))
        self.assertEqual(
            (
                CompensationOperation.REMOVE_MARKETPLACE,
                CompensationOperation.LIST_PLUGINS,
                CompensationOperation.LIST_MARKETPLACES,
                CompensationOperation.PROVE_INSTALLED_PATH_ABSENT,
            ),
            tuple(port.calls),
        )
        self.assertEqual(4, len(port.requests))
        request = port.requests[0]
        self.assertTrue(all(observed is request for observed in port.requests))
        assert_manifest(self, request.manifest)

    def test_s5_recovery_claim_derives_manifest_and_rebuilds_the_only_plan(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            _recovery_context,
            settle_codex_registration_compensation,
        )

        claim = recovery_claim()
        decision = consume_codex_registration_compensation_claim(claim)
        self.assertIs(type(decision), CodexRegistrationAddRecovery)
        if type(decision) is not CodexRegistrationAddRecovery:
            raise AssertionError("expected consumed started-add recovery")
        context = _recovery_context(decision)
        self.assertIs(type(context), tuple)
        if type(context) is not tuple:
            raise AssertionError("expected recovery settlement context")
        expected_plan = build_compensation_plan(
            decision.journal,
            decision.request.preflight,
            decision.request.attempt_id,
        )
        self.assertIs(type(expected_plan), CodexCompensationPlan)
        if type(expected_plan) is not CodexCompensationPlan:
            raise AssertionError("expected recovery compensation plan")
        self.assertEqual(expected_plan.model_dump(), context[1].model_dump())

        port = RecordingCompensationPort()
        assert_compensated(self, settle_codex_registration_compensation(recovery_claim(), port))
        self.assertEqual(
            (
                CompensationOperation.REMOVE_MARKETPLACE,
                CompensationOperation.LIST_PLUGINS,
                CompensationOperation.LIST_MARKETPLACES,
                CompensationOperation.PROVE_INSTALLED_PATH_ABSENT,
            ),
            tuple(port.calls),
        )
        assert_manifest(self, port.requests[0].manifest)

    def test_s6_malformed_port_returns_stay_in_existing_finite_algebra(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            settle_codex_registration_compensation,
        )

        port = RecordingCompensationPort()
        port.malformed_marketplace_removal = True
        result = settle_codex_registration_compensation(terminal_claim(), port)
        self.assertIs(type(result), CodexCompensationFailed)
        self.assertEqual(4, len(port.calls))

    def test_s7_exception_propagation_replay_and_duplicate_settlement_are_exact(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            settle_codex_registration_compensation,
        )

        exception_types: tuple[tuple[RaisedOperation, type[BaseException]], ...] = (
            (RaisedOperation.RUNTIME, RuntimeError),
            (RaisedOperation.MEMORY, MemoryError),
            (RaisedOperation.KEYBOARD, KeyboardInterrupt),
            (RaisedOperation.EXIT, SystemExit),
        )
        for raised, exception_type in exception_types:
            with self.subTest(exception=raised):
                claim = terminal_claim()
                port = RecordingCompensationPort()
                port.raised = raised
                with self.assertRaises(exception_type):
                    settle_codex_registration_compensation(claim, port)
                self.assertEqual(1, len(port.calls))
                assert_claim_blocked(self, settle_codex_registration_compensation(claim, port))
                self.assertEqual(1, len(port.calls))

        claim = terminal_claim()
        port = RecordingCompensationPort()
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = (
                executor.submit(settle_codex_registration_compensation, claim, port),
                executor.submit(settle_codex_registration_compensation, claim, port),
            )
            results = tuple(future.result(timeout=5.0) for future in futures)
        self.assertEqual(1, sum(type(result) is CodexCompensated for result in results))
        self.assertEqual(1, sum(type(result) is CodexRegistrationSettlementClaimBlocked for result in results))
        self.assertEqual(4, len(port.calls))

    def test_s8_in_memory_settlement_has_no_renderer_or_external_effect_surface(self) -> None:
        from library.local_orchestration import codex_registration_compensation_settlement as settlement

        exported_names = frozenset(name for name in vars(settlement) if not name.startswith("_"))
        self.assertNotIn("subprocess", exported_names)
        self.assertNotIn("requests", exported_names)
        self.assertNotIn("socket", exported_names)
        self.assertNotIn("forward", exported_names)
        self.assertNotIn("receipt", exported_names)

    def test_s9_admission_before_consumption_preserves_the_claim(self) -> None:
        from library.local_orchestration.codex_registration_compensation_settlement import (
            settle_codex_registration_compensation,
        )

        claim = terminal_claim()
        self.assertIs(type(settle_codex_registration_compensation(claim, PropertyPort())), CodexCompensationPortRejected)
        port = RecordingCompensationPort()
        assert_compensated(self, settle_codex_registration_compensation(claim, port))


if __name__ == "__main__":
    unittest.main()
