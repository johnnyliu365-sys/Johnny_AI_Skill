"""F1-F8 closure for Codex registration forward composition."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, astuple, is_dataclass
from enum import Enum
import ntpath
import pickle
from threading import Event
from types import MethodType
from typing import Callable, NoReturn, cast
import unittest

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
    CodexRegistrationForwardBlocked,
    CodexRegistrationForwardCoordinator,
    CodexRegistrationForwardRejectReason,
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
from library.local_orchestration.codex_registration_transaction import (
    CodexRegistrationAddRecovery,
    CodexRegistrationGeneration,
    CodexRegistrationLeaseMetadata,
    CodexRegistrationNextReadyPhase,
    CodexRegistrationPhase,
    CodexRegistrationPhaseLease,
    CodexRegistrationReadyLease,
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
OTHER_MARKETPLACE = CodexMarketplaceName(value="other-market")
PLUGIN = CodexPluginName(value="probe-plugin")
OTHER_PLUGIN = CodexPluginName(value="other-plugin")
SOURCE = OwnedRelativePath(value="marketplaces/probe-market")
OTHER_SOURCE = OwnedRelativePath(value="marketplaces/other-market")
INSTALLED = OwnedRelativePath(value="plugins/probe-plugin")
OTHER_INSTALLED = OwnedRelativePath(value="plugins/other-plugin")
VERSION = CodexCliVersion(value="1.2.3")
OTHER_VERSION = CodexCliVersion(value="9.9.9")
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")
OTHER_ATTEMPT = CodexRegistrationAttemptId(value="attempt-fedcba9876543210")
DIGEST = ArtifactDigest(value="a" * 64)
AUTH_POLICY = CodexAuthPolicy(value="trusted-local")
PLUGIN_ID = CodexPluginId(value="plugin-probe-012345")
FOREIGN_PLUGIN_ID = CodexPluginId(value="plugin-foreign-987654")
RAW_DIAGNOSTIC = "raw-diagnostic-must-not-escape"


class ForwardPhase(str, Enum):
    FRESH = "FRESH"
    MARKETPLACE = "MARKETPLACE"
    PLUGIN = "PLUGIN"


class FreshMode(str, Enum):
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    WRONG_TYPE = "WRONG_TYPE"
    WRONG_REQUEST = "WRONG_REQUEST"
    WRONG_ATTEMPT = "WRONG_ATTEMPT"
    WRONG_VERSION = "WRONG_VERSION"
    MALFORMED = "MALFORMED"


class AddMode(str, Enum):
    SUCCESS = "SUCCESS"
    PREEXISTING = "PREEXISTING"
    PRESTART_FAILURE = "PRESTART_FAILURE"
    STARTED_FAILURE = "STARTED_FAILURE"
    WRONG_TYPE = "WRONG_TYPE"
    WRONG_REQUEST = "WRONG_REQUEST"
    WRONG_ATTEMPT = "WRONG_ATTEMPT"
    WRONG_TARGET = "WRONG_TARGET"
    WRONG_VERSION = "WRONG_VERSION"
    WRONG_PLUGIN_ID = "WRONG_PLUGIN_ID"
    WRONG_PATH = "WRONG_PATH"
    WRONG_AUTH = "WRONG_AUTH"
    MALFORMED = "MALFORMED"


class CoordinatorEntry(str, Enum):
    BEGIN = "BEGIN"
    EXECUTE = "EXECUTE"
    RECOVERY = "RECOVERY"


class CoordinatorSlot(str, Enum):
    TOKEN = "_token"
    CAPABILITY = "_capability"
    TRANSACTION = "_transaction"


class InvalidCoordinatorShape(str, Enum):
    MISSING = "MISSING"
    FOREIGN = "FOREIGN"
    WRONG_TYPE = "WRONG_TYPE"


class CallerTrap:
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

    def __str__(self) -> str:
        self._raise()


class IndexTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def __index__(self) -> int:
        self.invocation_count += 1
        raise RuntimeError("INDEX_TRAP")


class DescriptorTrap:
    def __init__(self) -> None:
        self.invocation_count = 0

    def __get__(self, instance: object, owner: type[object]) -> NoReturn:
        self.invocation_count += 1
        raise RuntimeError("descriptor trap")


DESCRIPTOR_TRAP = DescriptorTrap()


class DescriptorCandidate:
    fresh_preflight = DESCRIPTOR_TRAP


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


def other_request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=OTHER_INSTALLATION,
            root=ROOT,
            marketplace=OTHER_MARKETPLACE,
            plugin=OTHER_PLUGIN,
            marketplace_source=OTHER_SOURCE,
        ),
        attempt_id=ATTEMPT,
        expected_version=VERSION,
        source_locator=OTHER_SOURCE,
        installed_locator=OTHER_INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=PLUGIN_ID,
    )


def observed_path(locator: OwnedRelativePath) -> CodexObservedAbsolutePath:
    return CodexObservedAbsolutePath(
        value=ntpath.join(ntpath.expandvars(CANONICAL_INSTALL_ROOT), *locator.parts())
    )


def fresh_success(current: CodexRegistrationPortRequest) -> CodexFreshPreflightAccepted:
    return CodexFreshPreflightAccepted(
        request=current,
        eligible=CodexPreflightEligible(version=current.expected_version),
    )


def marketplace_success(
    current: CodexRegistrationPortRequest,
    *,
    already_added: bool = False,
) -> CodexMarketplaceAddSucceeded:
    return CodexMarketplaceAddSucceeded(
        request=current,
        confirmed=CodexMarketplaceAddConfirmed(
            target=CodexCommandTarget.MARKETPLACE_ADD,
            start_state=CodexCommandStartState.STARTED,
            already_added=already_added,
        ),
        observation=CodexMarketplaceAddObservation(
            marketplace_name=current.preflight.marketplace,
            installed_root=observed_path(current.source_locator),
            already_added=already_added,
        ),
    )


def plugin_success(
    current: CodexRegistrationPortRequest,
    plugin_id: CodexPluginId = PLUGIN_ID,
) -> CodexPluginAddSucceeded:
    return CodexPluginAddSucceeded(
        request=current,
        confirmed=CodexPluginAddConfirmed(
            target=CodexCommandTarget.PLUGIN_ADD,
            start_state=CodexCommandStartState.STARTED,
        ),
        observation=CodexPluginAddObservation(
            plugin_id=plugin_id,
            name=current.preflight.plugin,
            marketplace_name=current.preflight.marketplace,
            version=current.expected_version,
            installed_path=observed_path(current.installed_locator),
            auth_policy=current.expected_auth_policy,
        ),
    )


class ForwardAdapter:
    def __init__(self) -> None:
        self.calls: list[ForwardPhase] = []
        self.requests: list[CodexRegistrationPortRequest] = []
        self.prove_count = 0
        self.fresh_mode = FreshMode.SUCCESS
        self.marketplace_mode = AddMode.SUCCESS
        self.plugin_mode = AddMode.SUCCESS
        self.exception_phase: ForwardPhase | None = None
        self.exception_value: RuntimeError | MemoryError | KeyboardInterrupt | SystemExit | None = None
        self.block_phase: ForwardPhase | None = None
        self.entered = Event()
        self.release = Event()
        self.reentrant_phase: ForwardPhase | None = None
        self.reentrant_action: Callable[[], object] | None = None
        self.reentrant_results: list[object] = []
        self.last_returned: object = object()

    def _before(self, phase: ForwardPhase, current: CodexRegistrationPortRequest) -> None:
        self.calls.append(phase)
        self.requests.append(current)
        if self.reentrant_phase is phase and self.reentrant_action is not None:
            action = self.reentrant_action
            self.reentrant_action = None
            self.reentrant_results.append(action())
        if self.block_phase is phase:
            self.entered.set()
            if not self.release.wait(timeout=5.0):
                raise RuntimeError("test synchronization timed out")
        if self.exception_phase is phase and self.exception_value is not None:
            raise self.exception_value

    def fresh_preflight(self, current: CodexRegistrationPortRequest) -> object:
        self._before(ForwardPhase.FRESH, current)
        if self.fresh_mode is FreshMode.REJECTED:
            returned: object = CodexFreshPreflightRejected(
                request=current,
                reason=CodexBlockReason.ACCESS_DENIED,
            )
        elif self.fresh_mode is FreshMode.WRONG_TYPE:
            returned = RAW_DIAGNOSTIC
        elif self.fresh_mode is FreshMode.WRONG_REQUEST:
            returned = fresh_success(other_request())
        elif self.fresh_mode is FreshMode.WRONG_ATTEMPT:
            returned = fresh_success(request(OTHER_ATTEMPT))
        elif self.fresh_mode is FreshMode.WRONG_VERSION:
            returned = CodexFreshPreflightAccepted(
                request=current,
                eligible=CodexPreflightEligible(version=OTHER_VERSION),
            )
        elif self.fresh_mode is FreshMode.MALFORMED:
            returned = CodexFreshPreflightAccepted.model_construct(
                request=current,
                eligible=CallerTrap(),
            )
        else:
            returned = fresh_success(current)
        self.last_returned = returned
        return returned

    def add_marketplace(self, current: CodexRegistrationPortRequest) -> object:
        self._before(ForwardPhase.MARKETPLACE, current)
        if self.marketplace_mode is AddMode.PREEXISTING:
            returned: object = marketplace_success(current, already_added=True)
        elif self.marketplace_mode is AddMode.PRESTART_FAILURE:
            returned = CodexRegistrationCommandFailed(
                request=current,
                failure=CodexPreStartFailure(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    reason=CodexPreStartFailureReason.ACCESS_DENIED,
                    start_state=CodexCommandStartState.NOT_STARTED,
                ),
            )
        elif self.marketplace_mode is AddMode.STARTED_FAILURE:
            returned = CodexRegistrationCommandFailed(
                request=current,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    reason=CodexStartedFailureReason.NONZERO_EXIT,
                    start_state=CodexCommandStartState.STARTED,
                ),
            )
        elif self.marketplace_mode is AddMode.WRONG_TYPE:
            returned = RAW_DIAGNOSTIC
        elif self.marketplace_mode is AddMode.WRONG_REQUEST:
            returned = marketplace_success(other_request())
        elif self.marketplace_mode is AddMode.WRONG_ATTEMPT:
            returned = marketplace_success(request(OTHER_ATTEMPT))
        elif self.marketplace_mode is AddMode.WRONG_TARGET:
            returned = CodexRegistrationCommandFailed(
                request=current,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    reason=CodexStartedFailureReason.IDENTITY_MISMATCH,
                    start_state=CodexCommandStartState.STARTED,
                ),
            )
        elif self.marketplace_mode is AddMode.WRONG_PATH:
            returned = CodexMarketplaceAddSucceeded(
                request=current,
                confirmed=CodexMarketplaceAddConfirmed(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    start_state=CodexCommandStartState.STARTED,
                    already_added=False,
                ),
                observation=CodexMarketplaceAddObservation(
                    marketplace_name=current.preflight.marketplace,
                    installed_root=observed_path(OTHER_SOURCE),
                    already_added=False,
                ),
            )
        elif self.marketplace_mode is AddMode.MALFORMED:
            returned = CodexMarketplaceAddSucceeded.model_construct(
                request=current,
                confirmed=CodexMarketplaceAddConfirmed(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    start_state=CodexCommandStartState.STARTED,
                    already_added=False,
                ),
                observation=CodexMarketplaceAddObservation.model_construct(
                    marketplace_name=CallerTrap(),
                    installed_root=observed_path(current.source_locator),
                    already_added=False,
                ),
            )
        else:
            returned = marketplace_success(current)
        self.last_returned = returned
        return returned

    def add_plugin(self, current: CodexRegistrationPortRequest) -> object:
        self._before(ForwardPhase.PLUGIN, current)
        if self.plugin_mode is AddMode.PRESTART_FAILURE:
            returned: object = CodexRegistrationCommandFailed(
                request=current,
                failure=CodexPreStartFailure(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    reason=CodexPreStartFailureReason.ACCESS_DENIED,
                    start_state=CodexCommandStartState.NOT_STARTED,
                ),
            )
        elif self.plugin_mode is AddMode.STARTED_FAILURE:
            returned = CodexRegistrationCommandFailed(
                request=current,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    reason=CodexStartedFailureReason.NONZERO_EXIT,
                    start_state=CodexCommandStartState.STARTED,
                ),
            )
        elif self.plugin_mode is AddMode.WRONG_TYPE:
            returned = RAW_DIAGNOSTIC
        elif self.plugin_mode is AddMode.WRONG_REQUEST:
            returned = plugin_success(other_request())
        elif self.plugin_mode is AddMode.WRONG_ATTEMPT:
            returned = plugin_success(request(OTHER_ATTEMPT))
        elif self.plugin_mode is AddMode.WRONG_TARGET:
            returned = CodexRegistrationCommandFailed(
                request=current,
                failure=CodexStartedFailure(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    reason=CodexStartedFailureReason.IDENTITY_MISMATCH,
                    start_state=CodexCommandStartState.STARTED,
                ),
            )
        elif self.plugin_mode is AddMode.WRONG_VERSION:
            returned = CodexPluginAddSucceeded(
                request=current,
                confirmed=CodexPluginAddConfirmed(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    start_state=CodexCommandStartState.STARTED,
                ),
                observation=CodexPluginAddObservation(
                    plugin_id=current.expected_plugin_id,
                    name=current.preflight.plugin,
                    marketplace_name=current.preflight.marketplace,
                    version=OTHER_VERSION,
                    installed_path=observed_path(current.installed_locator),
                    auth_policy=current.expected_auth_policy,
                ),
            )
        elif self.plugin_mode is AddMode.WRONG_PLUGIN_ID:
            returned = plugin_success(current, FOREIGN_PLUGIN_ID)
        elif self.plugin_mode is AddMode.WRONG_PATH:
            returned = CodexPluginAddSucceeded(
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
                    installed_path=observed_path(OTHER_INSTALLED),
                    auth_policy=current.expected_auth_policy,
                ),
            )
        elif self.plugin_mode is AddMode.WRONG_AUTH:
            returned = CodexPluginAddSucceeded(
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
                    auth_policy=CodexAuthPolicy(value="foreign-policy"),
                ),
            )
        elif self.plugin_mode is AddMode.MALFORMED:
            returned = CodexPluginAddSucceeded.model_construct(
                request=current,
                confirmed=CodexPluginAddConfirmed(
                    target=CodexCommandTarget.PLUGIN_ADD,
                    start_state=CodexCommandStartState.STARTED,
                ),
                observation=CodexPluginAddObservation.model_construct(
                    plugin_id=CallerTrap(),
                    name=current.preflight.plugin,
                    marketplace_name=current.preflight.marketplace,
                    version=current.expected_version,
                    installed_path=observed_path(current.installed_locator),
                    auth_policy=current.expected_auth_policy,
                ),
            )
        else:
            returned = plugin_success(current)
        self.last_returned = returned
        return returned

    def prove(self, current: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        self.prove_count += 1
        raise AssertionError("proof is outside forward composition")


def expect_capability(value: object) -> CodexRegistrationPortCapability:
    if type(value) is not CodexRegistrationPortCapability:
        raise AssertionError(f"expected capability, received {type(value).__name__}")
    return value


def capability(adapter: ForwardAdapter) -> CodexRegistrationPortCapability:
    return expect_capability(admit_codex_registration_port(adapter))


def expect_forward(value: object) -> CodexRegistrationForwardCoordinator:
    if type(value) is not CodexRegistrationForwardCoordinator:
        raise AssertionError(f"expected forward coordinator, received {type(value).__name__}")
    return value


def coordinator(adapter: ForwardAdapter) -> CodexRegistrationForwardCoordinator:
    return expect_forward(admit_codex_registration_forward(capability(adapter)))


def constructed_invalid_coordinator(
    reference: CodexRegistrationForwardCoordinator,
    foreign: CodexRegistrationForwardCoordinator,
    slot: CoordinatorSlot,
    shape: InvalidCoordinatorShape,
    trap: CallerTrap,
) -> CodexRegistrationForwardCoordinator:
    values: dict[CoordinatorSlot, object] = {
        CoordinatorSlot.TOKEN: object.__getattribute__(reference, CoordinatorSlot.TOKEN.value),
        CoordinatorSlot.CAPABILITY: object.__getattribute__(reference, CoordinatorSlot.CAPABILITY.value),
        CoordinatorSlot.TRANSACTION: object.__getattribute__(reference, CoordinatorSlot.TRANSACTION.value),
    }
    if shape is InvalidCoordinatorShape.MISSING:
        del values[slot]
    elif shape is InvalidCoordinatorShape.FOREIGN:
        values[slot] = object.__getattribute__(foreign, slot.value)
    else:
        values[slot] = trap
    fabricated = object.__new__(CodexRegistrationForwardCoordinator)
    for current_slot, value in values.items():
        object.__setattr__(fabricated, current_slot.value, value)
    return fabricated


def expect_ready(value: object) -> CodexRegistrationReadyLease:
    if type(value) is not CodexRegistrationReadyLease:
        raise AssertionError(f"expected ready lease, received {type(value).__name__}")
    return value


def expect_next(value: object) -> CodexRegistrationNextReadyPhase:
    if type(value) is not CodexRegistrationNextReadyPhase:
        raise AssertionError(f"expected next phase, received {type(value).__name__}")
    return value


def expect_terminal(value: object) -> CodexRegistrationTerminal:
    if type(value) is not CodexRegistrationTerminal:
        raise AssertionError(f"expected terminal, received {type(value).__name__}")
    return value


def assert_transaction_blocked(
    testcase: unittest.TestCase,
    value: object,
    reason: CodexRegistrationTransactionBlockReason,
) -> None:
    testcase.assertIs(type(value), CodexRegistrationTransactionBlocked)
    if type(value) is not CodexRegistrationTransactionBlocked:
        raise AssertionError(f"expected transaction block, received {type(value).__name__}")
    testcase.assertIs(value.reason, reason)


def ready_for_phase(
    current: CodexRegistrationForwardCoordinator,
    phase: ForwardPhase,
) -> CodexRegistrationReadyLease | CodexRegistrationNextReadyPhase:
    initial = expect_ready(current.begin(request()))
    if phase is ForwardPhase.FRESH:
        return initial
    marketplace = expect_next(current.execute(initial.lease))
    if phase is ForwardPhase.MARKETPLACE:
        return marketplace
    return expect_next(current.execute(marketplace.lease))


class CodexRegistrationForwardTests(unittest.TestCase):
    def test_f1_absent_forward_composition_module_is_required(self) -> None:
        self.assertTrue(callable(admit_codex_registration_forward))

    def test_f2_exact_capability_admits_without_effect_and_invalid_roots_block(self) -> None:
        adapter = ForwardAdapter()
        admitted_capability = capability(adapter)
        forward = admit_codex_registration_forward(admitted_capability)
        current = expect_forward(forward)
        self.assertEqual([], adapter.calls)
        self.assertEqual(0, adapter.prove_count)
        self.assertEqual(
            {"status": "FORWARD_ADMITTED", "operation_count": 3},
            current.metadata().model_dump(),
        )

        root_trap = CallerTrap()
        invalid_roots: tuple[object, ...] = (
            None,
            "text",
            (),
            [],
            {},
            object(),
            root_trap,
            DescriptorCandidate(),
        )
        for invalid in invalid_roots:
            with self.subTest(root_type=type(invalid).__name__):
                blocked = admit_codex_registration_forward(invalid)
                self.assertEqual(
                    CodexRegistrationForwardBlocked(
                        reason=CodexRegistrationForwardRejectReason.INVALID_PORT
                    ),
                    blocked,
                )
        self.assertEqual(0, root_trap.invocation_count)
        self.assertEqual(0, DESCRIPTOR_TRAP.invocation_count)

    def test_f2_capability_authority_owner_and_operation_shape_are_exact(self) -> None:
        trap = CallerTrap()

        forged_empty = object.__new__(CodexRegistrationPortCapability)

        invalid_authority = capability(ForwardAdapter())
        object.__setattr__(invalid_authority, "_authority", object())

        invalid_status = capability(ForwardAdapter())
        object.__setattr__(invalid_status, "status", trap)

        substituted = capability(ForwardAdapter())
        object.__setattr__(substituted, "fresh_preflight", substituted.add_marketplace)

        cross_owner = capability(ForwardAdapter())
        other_owner = capability(ForwardAdapter())
        object.__setattr__(cross_owner, "add_marketplace", other_owner.add_marketplace)

        non_method = capability(ForwardAdapter())
        object.__setattr__(non_method, "fresh_preflight", ForwardAdapter.fresh_preflight)

        invalid_cells = (
            forged_empty,
            invalid_authority,
            invalid_status,
            substituted,
            cross_owner,
            non_method,
        )
        for invalid in invalid_cells:
            with self.subTest(cell=id(invalid)):
                blocked = admit_codex_registration_forward(invalid)
                self.assertIs(type(blocked), CodexRegistrationForwardBlocked)
                if type(blocked) is not CodexRegistrationForwardBlocked:
                    raise AssertionError("invalid capability admitted")
                self.assertIs(blocked.reason, CodexRegistrationForwardRejectReason.INVALID_PORT)
        self.assertEqual(0, trap.invocation_count)

    def test_f2_coordinator_transfer_and_structural_serialization_are_forbidden(self) -> None:
        adapter = ForwardAdapter()
        current = coordinator(adapter)
        self.assertFalse(is_dataclass(current))
        transfers: tuple[Callable[[], object], ...] = (
            lambda: copy.copy(current),
            lambda: copy.deepcopy(current),
            lambda: pickle.dumps(current),
            lambda: cast(Callable[[object], object], asdict)(current),
            lambda: cast(Callable[[object], object], astuple)(current),
            lambda: vars(current),
        )
        for transfer in transfers:
            with self.subTest(transfer=transfer):
                with self.assertRaises(TypeError):
                    transfer()
        with self.assertRaises(TypeError):
            CodexRegistrationForwardCoordinator(
                object(),
                capability(adapter),
                CodexRegistrationTransactionCoordinator(),
            )
        public_text = repr(current) + repr(current.metadata().model_dump())
        for forbidden in ("ForwardAdapter", "bound method", "request", "token", "authority"):
            self.assertNotIn(forbidden, public_text)
        self.assertEqual([], adapter.calls)

    def test_f2_f8_rebuilt_capability_is_used_after_admission(self) -> None:
        adapter = ForwardAdapter()
        submitted = capability(adapter)
        current = expect_forward(admit_codex_registration_forward(submitted))
        substitute_adapter = ForwardAdapter()
        substitute = capability(substitute_adapter)
        object.__setattr__(submitted, "fresh_preflight", substitute.fresh_preflight)

        ready = expect_ready(current.begin(request()))
        expect_next(current.execute(ready.lease))
        self.assertEqual([ForwardPhase.FRESH], adapter.calls)
        self.assertEqual([], substitute_adapter.calls)

    def test_f3_f8_exact_phase_dispatch_order_and_requests(self) -> None:
        adapter = ForwardAdapter()
        current = coordinator(adapter)
        original = request()
        fresh = expect_ready(current.begin(original))
        self.assertEqual(1, fresh.lease.metadata().generation.value)
        marketplace = expect_next(current.execute(fresh.lease))
        self.assertEqual(2, marketplace.lease.metadata().generation.value)
        plugin = expect_next(current.execute(marketplace.lease))
        self.assertEqual(3, plugin.lease.metadata().generation.value)
        terminal = expect_terminal(current.execute(plugin.lease))

        self.assertEqual(
            [ForwardPhase.FRESH, ForwardPhase.MARKETPLACE, ForwardPhase.PLUGIN],
            adapter.calls,
        )
        self.assertEqual(3, len(adapter.requests))
        for rebuilt in adapter.requests:
            self.assertIsNot(rebuilt, original)
            self.assertEqual(original.model_dump(), rebuilt.model_dump())
        self.assertIs(type(terminal.decision), CodexRegistrationProofRequired)
        self.assertEqual(0, adapter.prove_count)

    def test_f4_f8_start_precedes_each_effect_and_blocks_reentry(self) -> None:
        for phase in ForwardPhase:
            with self.subTest(phase=phase):
                adapter = ForwardAdapter()
                current = coordinator(adapter)
                ready = ready_for_phase(current, phase)
                adapter.calls.clear()
                adapter.requests.clear()
                adapter.reentrant_phase = phase
                adapter.reentrant_action = lambda: current.execute(ready.lease)
                completed = current.execute(ready.lease)
                self.assertNotIsInstance(completed, CodexRegistrationTransactionBlocked)
                self.assertEqual([phase], adapter.calls)
                self.assertEqual(1, len(adapter.reentrant_results))
                assert_transaction_blocked(
                    self,
                    adapter.reentrant_results[0],
                    CodexRegistrationTransactionBlockReason.REPLAYED,
                )

    def test_f4_synchronized_duplicate_each_phase_is_single_call(self) -> None:
        for phase in ForwardPhase:
            with self.subTest(phase=phase):
                adapter = ForwardAdapter()
                current = coordinator(adapter)
                ready = ready_for_phase(current, phase)
                adapter.calls.clear()
                adapter.requests.clear()
                adapter.block_phase = phase
                with ThreadPoolExecutor(max_workers=1) as executor:
                    first = executor.submit(current.execute, ready.lease)
                    self.assertTrue(adapter.entered.wait(timeout=5.0))
                    duplicate = current.execute(ready.lease)
                    adapter.release.set()
                    completed = first.result(timeout=5.0)
                self.assertNotIsInstance(completed, CodexRegistrationTransactionBlocked)
                assert_transaction_blocked(
                    self,
                    duplicate,
                    CodexRegistrationTransactionBlockReason.REPLAYED,
                )
                self.assertEqual([phase], adapter.calls)

    def test_f4_stale_foreign_wrong_phase_metadata_and_fabricated_leases_are_zero_call(self) -> None:
        adapter = ForwardAdapter()
        current = coordinator(adapter)
        initial = expect_ready(current.begin(request()))
        marketplace = expect_next(current.execute(initial.lease))
        adapter.calls.clear()

        assert_transaction_blocked(
            self,
            current.execute(initial.lease),
            CodexRegistrationTransactionBlockReason.REPLAYED,
        )
        foreign = coordinator(ForwardAdapter())
        assert_transaction_blocked(
            self,
            foreign.execute(marketplace.lease),
            CodexRegistrationTransactionBlockReason.INVALID_LEASE,
        )
        assert_transaction_blocked(
            self,
            current.execute(marketplace.lease.metadata()),
            CodexRegistrationTransactionBlockReason.INVALID_LEASE,
        )

        fabricated = object.__new__(CodexRegistrationPhaseLease)
        object.__setattr__(fabricated, "_token", object())
        object.__setattr__(fabricated, "_owner", object())
        object.__setattr__(fabricated, "_metadata", marketplace.lease.metadata())
        assert_transaction_blocked(
            self,
            current.execute(fabricated),
            CodexRegistrationTransactionBlockReason.INVALID_LEASE,
        )

        wrong_phase = marketplace.lease.metadata().model_copy(
            update={"phase": CodexRegistrationPhase.PLUGIN_ADD}
        )
        object.__setattr__(marketplace.lease, "_metadata", wrong_phase)
        assert_transaction_blocked(
            self,
            current.execute(marketplace.lease),
            CodexRegistrationTransactionBlockReason.PHASE_MISMATCH,
        )
        with self.assertRaises(TypeError):
            copy.copy(initial.lease)
        self.assertEqual([], adapter.calls)

    def test_f5_declared_failures_return_existing_terminal_truth(self) -> None:
        fresh_adapter = ForwardAdapter()
        fresh_adapter.fresh_mode = FreshMode.REJECTED
        fresh_coordinator = coordinator(fresh_adapter)
        fresh_lease = expect_ready(fresh_coordinator.begin(request()))
        fresh_terminal = expect_terminal(fresh_coordinator.execute(fresh_lease.lease))
        self.assertIs(type(fresh_terminal.decision), CodexRegistrationBlocked)
        if type(fresh_terminal.decision) is CodexRegistrationBlocked:
            self.assertIs(
                fresh_terminal.decision.reason,
                CodexRegistrationBlockReason.FRESH_PREFLIGHT_REJECTED,
            )
        self.assertEqual([ForwardPhase.FRESH], fresh_adapter.calls)

        marketplace_modes = (
            (
                AddMode.PREEXISTING,
                CodexRegistrationBlocked,
                CodexRegistrationBlockReason.MARKETPLACE_PREEXISTING,
            ),
            (
                AddMode.PRESTART_FAILURE,
                CodexRegistrationBlocked,
                CodexRegistrationBlockReason.MARKETPLACE_ADD_NOT_STARTED,
            ),
            (AddMode.STARTED_FAILURE, CodexRegistrationCompensationRequired, None),
        )
        for marketplace_mode, expected_type, expected_reason in marketplace_modes:
            with self.subTest(marketplace=marketplace_mode):
                adapter = ForwardAdapter()
                current = coordinator(adapter)
                fresh = expect_ready(current.begin(request()))
                marketplace = expect_next(current.execute(fresh.lease))
                adapter.marketplace_mode = marketplace_mode
                terminal = expect_terminal(current.execute(marketplace.lease))
                self.assertIsInstance(terminal.decision, expected_type)
                if expected_reason is not None:
                    self.assertIs(type(terminal.decision), CodexRegistrationBlocked)
                    if type(terminal.decision) is CodexRegistrationBlocked:
                        self.assertIs(terminal.decision.reason, expected_reason)
                self.assertEqual(
                    [ForwardPhase.FRESH, ForwardPhase.MARKETPLACE],
                    adapter.calls,
                )

        for mode in (AddMode.PRESTART_FAILURE, AddMode.STARTED_FAILURE):
            with self.subTest(plugin=mode):
                adapter = ForwardAdapter()
                current = coordinator(adapter)
                plugin = ready_for_phase(current, ForwardPhase.PLUGIN)
                adapter.plugin_mode = mode
                terminal = expect_terminal(current.execute(plugin.lease))
                self.assertIsInstance(terminal.decision, CodexRegistrationCompensationRequired)
                self.assertEqual(0, adapter.prove_count)

    def test_f5_wrong_foreign_and_recursive_returns_stop_without_later_operation(self) -> None:
        fresh_modes = (
            FreshMode.WRONG_TYPE,
            FreshMode.WRONG_REQUEST,
            FreshMode.WRONG_ATTEMPT,
            FreshMode.WRONG_VERSION,
            FreshMode.MALFORMED,
        )
        for fresh_mode in fresh_modes:
            with self.subTest(fresh=fresh_mode):
                adapter = ForwardAdapter()
                adapter.fresh_mode = fresh_mode
                current = coordinator(adapter)
                terminal = expect_terminal(current.execute(expect_ready(current.begin(request())).lease))
                self.assertIs(type(terminal.decision), CodexRegistrationBlocked)
                if type(terminal.decision) is CodexRegistrationBlocked:
                    self.assertIs(
                        terminal.decision.reason,
                        CodexRegistrationBlockReason.FRESH_PREFLIGHT_INVALID,
                    )
                self.assertEqual([ForwardPhase.FRESH], adapter.calls)

        add_cells = (
            (ForwardPhase.MARKETPLACE, AddMode.WRONG_TYPE),
            (ForwardPhase.MARKETPLACE, AddMode.WRONG_REQUEST),
            (ForwardPhase.MARKETPLACE, AddMode.WRONG_ATTEMPT),
            (ForwardPhase.MARKETPLACE, AddMode.WRONG_TARGET),
            (ForwardPhase.MARKETPLACE, AddMode.WRONG_PATH),
            (ForwardPhase.MARKETPLACE, AddMode.MALFORMED),
            (ForwardPhase.PLUGIN, AddMode.WRONG_TYPE),
            (ForwardPhase.PLUGIN, AddMode.WRONG_REQUEST),
            (ForwardPhase.PLUGIN, AddMode.WRONG_ATTEMPT),
            (ForwardPhase.PLUGIN, AddMode.WRONG_TARGET),
            (ForwardPhase.PLUGIN, AddMode.WRONG_VERSION),
            (ForwardPhase.PLUGIN, AddMode.WRONG_PLUGIN_ID),
            (ForwardPhase.PLUGIN, AddMode.WRONG_PATH),
            (ForwardPhase.PLUGIN, AddMode.WRONG_AUTH),
            (ForwardPhase.PLUGIN, AddMode.MALFORMED),
        )
        for phase, add_mode in add_cells:
            with self.subTest(phase=phase, mode=add_mode):
                adapter = ForwardAdapter()
                current = coordinator(adapter)
                ready = ready_for_phase(current, phase)
                adapter.calls.clear()
                if phase is ForwardPhase.MARKETPLACE:
                    adapter.marketplace_mode = add_mode
                else:
                    adapter.plugin_mode = add_mode
                terminal = expect_terminal(current.execute(ready.lease))
                self.assertIs(type(terminal.decision), CodexRegistrationCompensationRequired)
                self.assertEqual([phase], adapter.calls)
                self.assertNotIn(RAW_DIAGNOSTIC, repr(terminal) + repr(terminal.model_dump()))

    def test_f5_f8_returned_value_is_completed_once(self) -> None:
        adapter = ForwardAdapter()
        current = coordinator(adapter)
        plugin = ready_for_phase(current, ForwardPhase.PLUGIN)
        adapter.calls.clear()
        terminal = expect_terminal(current.execute(plugin.lease))
        self.assertIs(type(adapter.last_returned), CodexPluginAddSucceeded)
        self.assertIs(type(terminal.decision), CodexRegistrationProofRequired)
        self.assertEqual([ForwardPhase.PLUGIN], adapter.calls)
        assert_transaction_blocked(
            self,
            current.execute(plugin.lease),
            CodexRegistrationTransactionBlockReason.REPLAYED,
        )
        self.assertEqual([ForwardPhase.PLUGIN], adapter.calls)

    def test_f6_f8_exception_stops_replay_and_recovery(self) -> None:
        exceptions = (
            RuntimeError("runtime marker"),
            MemoryError("memory marker"),
            KeyboardInterrupt("keyboard marker"),
            SystemExit("system marker"),
        )
        for phase in ForwardPhase:
            for raised_value in exceptions:
                with self.subTest(phase=phase, raised=type(raised_value).__name__):
                    adapter = ForwardAdapter()
                    current = coordinator(adapter)
                    ready = ready_for_phase(current, phase)
                    adapter.calls.clear()
                    adapter.exception_phase = phase
                    adapter.exception_value = raised_value
                    with self.assertRaises(type(raised_value)) as captured:
                        current.execute(ready.lease)
                    self.assertIs(captured.exception, raised_value)
                    self.assertEqual([phase], adapter.calls)
                    assert_transaction_blocked(
                        self,
                        current.execute(ready.lease),
                        CodexRegistrationTransactionBlockReason.REPLAYED,
                    )
                    self.assertEqual([phase], adapter.calls)
                    recovery = current.recovery(ready.lease)
                    if phase is ForwardPhase.FRESH:
                        assert_transaction_blocked(
                            self,
                            recovery,
                            CodexRegistrationTransactionBlockReason.PHASE_MISMATCH,
                        )
                    else:
                        self.assertIs(type(recovery), CodexRegistrationAddRecovery)
                        if type(recovery) is not CodexRegistrationAddRecovery:
                            raise AssertionError("expected add recovery")
                        if phase is ForwardPhase.MARKETPLACE:
                            self.assertIs(
                                recovery.journal.marketplace_state,
                                CodexAttemptEffectState.MAY_EXIST,
                            )
                            self.assertIs(
                                recovery.journal.plugin_state,
                                CodexAttemptEffectState.NOT_ATTEMPTED,
                            )
                        else:
                            self.assertIs(
                                recovery.journal.marketplace_state,
                                CodexAttemptEffectState.OWNED,
                            )
                            self.assertIs(
                                recovery.journal.plugin_state,
                                CodexAttemptEffectState.MAY_EXIST,
                            )
                    self.assertEqual(0, adapter.prove_count)

    def test_f7_constructed_invalid_fields_and_protocol_traps_are_finite(self) -> None:
        begin_trap = CallerTrap()
        invalid_begin = CodexRegistrationPortRequest.model_construct(
            preflight=preflight(),
            attempt_id=ATTEMPT,
            expected_version=VERSION,
            source_locator=SOURCE,
            installed_locator=INSTALLED,
            digest=DIGEST,
            expected_auth_policy=AUTH_POLICY,
            expected_plugin_id=begin_trap,
        )
        begin_adapter = ForwardAdapter()
        begin_result = coordinator(begin_adapter).begin(invalid_begin)
        assert_transaction_blocked(
            self,
            begin_result,
            CodexRegistrationTransactionBlockReason.INVALID_REQUEST,
        )
        self.assertEqual(0, begin_trap.invocation_count)
        self.assertEqual([], begin_adapter.calls)

        for field in ("status", "attempt_id"):
            with self.subTest(lease_field=field):
                trap = CallerTrap()
                adapter = ForwardAdapter()
                current = coordinator(adapter)
                ready = expect_ready(current.begin(request()))
                metadata = ready.lease.metadata()
                if field == "status":
                    invalid_metadata = CodexRegistrationLeaseMetadata.model_construct(
                        status=trap,
                        attempt_id=metadata.attempt_id,
                        phase=metadata.phase,
                        generation=metadata.generation,
                    )
                else:
                    invalid_metadata = CodexRegistrationLeaseMetadata.model_construct(
                        status="PHASE_LEASE",
                        attempt_id=CodexRegistrationAttemptId.model_construct(value=trap),
                        phase=metadata.phase,
                        generation=metadata.generation,
                    )
                object.__setattr__(ready.lease, "_metadata", invalid_metadata)
                assert_transaction_blocked(
                    self,
                    current.execute(ready.lease),
                    CodexRegistrationTransactionBlockReason.INVALID_LEASE,
                )
                self.assertEqual(0, trap.invocation_count)
                self.assertEqual([], adapter.calls)

    def test_f7_public_metadata_and_repr_are_bounded_and_effect_free(self) -> None:
        adapter = ForwardAdapter()
        current = coordinator(adapter)
        metadata = current.metadata()
        self.assertEqual(
            {"status": "FORWARD_ADMITTED", "operation_count": 3},
            metadata.model_dump(),
        )
        public_text = repr(current) + repr(metadata) + repr(metadata.model_dump())
        for forbidden in (
            "fresh_preflight",
            "add_marketplace",
            "add_plugin",
            "prove",
            "ForwardAdapter",
            "CodexRegistrationPortRequest",
            "attempt-",
            "C:\\",
            RAW_DIAGNOSTIC,
            "token",
            "authority",
        ):
            self.assertNotIn(forbidden, public_text)
        self.assertEqual([], adapter.calls)
        self.assertEqual(0, adapter.prove_count)

    def test_f7_fabricated_capability_fields_do_not_invoke_caller_protocols(self) -> None:
        trap = CallerTrap()
        valid = capability(ForwardAdapter())
        self.assertIs(type(valid.fresh_preflight), MethodType)
        object.__setattr__(valid, "add_plugin", trap)
        blocked = admit_codex_registration_forward(valid)
        self.assertIs(type(blocked), CodexRegistrationForwardBlocked)
        self.assertEqual(0, trap.invocation_count)

    def test_cr151_constructed_coordinator_authority_blocks_all_public_entries(self) -> None:
        for entry in CoordinatorEntry:
            for slot in CoordinatorSlot:
                for shape in InvalidCoordinatorShape:
                    with self.subTest(entry=entry, slot=slot, shape=shape):
                        adapter = ForwardAdapter()
                        foreign_adapter = ForwardAdapter()
                        current = coordinator(adapter)
                        foreign = coordinator(foreign_adapter)
                        trap = CallerTrap()
                        argument: object
                        if entry is CoordinatorEntry.BEGIN:
                            argument = request()
                        elif entry is CoordinatorEntry.EXECUTE:
                            argument = expect_ready(current.begin(request())).lease
                        else:
                            fresh = expect_ready(current.begin(request()))
                            marketplace = expect_next(current.execute(fresh.lease))
                            transaction_value: object = object.__getattribute__(current, "_transaction")
                            self.assertIs(type(transaction_value), CodexRegistrationTransactionCoordinator)
                            if type(transaction_value) is not CodexRegistrationTransactionCoordinator:
                                raise AssertionError("expected private transaction coordinator")
                            started = transaction_value.start(marketplace.lease)
                            self.assertNotIsInstance(started, CodexRegistrationTransactionBlocked)
                            adapter.calls.clear()
                            adapter.requests.clear()
                            argument = marketplace.lease

                        fabricated = constructed_invalid_coordinator(
                            current,
                            foreign,
                            slot,
                            shape,
                            trap,
                        )
                        result: object
                        if entry is CoordinatorEntry.BEGIN:
                            result = fabricated.begin(argument)
                        elif entry is CoordinatorEntry.EXECUTE:
                            result = fabricated.execute(argument)
                        else:
                            result = fabricated.recovery(argument)
                        assert_transaction_blocked(
                            self,
                            result,
                            CodexRegistrationTransactionBlockReason.INVALID_STATE,
                        )
                        self.assertEqual([], adapter.calls)
                        self.assertEqual([], foreign_adapter.calls)
                        self.assertEqual(0, trap.invocation_count)
                        if entry is CoordinatorEntry.BEGIN:
                            expect_ready(current.begin(argument))
                        elif entry is CoordinatorEntry.EXECUTE:
                            expect_next(current.execute(argument))
                            self.assertEqual([ForwardPhase.FRESH], adapter.calls)
                        else:
                            recovery = current.recovery(argument)
                            self.assertIs(type(recovery), CodexRegistrationAddRecovery)

    def test_cr151_constructed_coordinator_metadata_and_repr_share_authority_gate(self) -> None:
        for slot in CoordinatorSlot:
            for shape in InvalidCoordinatorShape:
                with self.subTest(slot=slot, shape=shape):
                    current = coordinator(ForwardAdapter())
                    foreign = coordinator(ForwardAdapter())
                    trap = CallerTrap()
                    fabricated = constructed_invalid_coordinator(
                        current,
                        foreign,
                        slot,
                        shape,
                        trap,
                    )
                    with self.assertRaises(TypeError):
                        fabricated.metadata()
                    with self.assertRaises(TypeError):
                        repr(fabricated)
                    self.assertEqual(0, trap.invocation_count)

    def test_cr152_reduce_ex_rejects_without_index_protocol(self) -> None:
        current = coordinator(ForwardAdapter())
        trap = IndexTrap()
        with self.assertRaises(TypeError):
            current.__reduce_ex__(trap)
        self.assertEqual(0, trap.invocation_count)


if __name__ == "__main__":
    unittest.main()
