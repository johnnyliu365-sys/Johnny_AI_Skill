"""D1-D8 closure for the pure Codex registration forward reducer."""

from __future__ import annotations

import copy
import ntpath
from typing import NoReturn
import unittest

from pydantic import ValidationError

import library.local_orchestration.codex_registration_reducer as registration_reducer
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
from library.local_orchestration.codex_compensation_reducer import (
    CodexCompensationPlan,
    CodexCompensationStep,
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
    CodexFreshPreflightRejected,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortRequest,
)
from library.local_orchestration.codex_registration_reducer import (
    CodexFreshPreflightPending,
    CodexMarketplaceAddPending,
    CodexPluginAddPending,
    CodexRegistrationBlockReason,
    CodexRegistrationBlocked,
    CodexRegistrationCompensationRequired,
    CodexRegistrationProofRequired,
    _journal_matches_request,
    _plan_matches_rebuild,
    advance_codex_registration,
    begin_codex_registration,
)
from library.local_orchestration.codex_registration_settlement_authority import (
    _rebuild_compensation_required,
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
FOREIGN_PLUGIN_ID = CodexPluginId(value="plugin-foreign-987654")

MARKETPLACE_PLAN_STEPS = (
    CodexCompensationStep.REMOVE_MARKETPLACE,
    CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
    CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
    CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
)
PLUGIN_FIRST_PLAN_STEPS = (
    CodexCompensationStep.REMOVE_PLUGIN,
    *MARKETPLACE_PLAN_STEPS,
)


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


def preflight() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=SOURCE,
    )


def request(
    attempt_id: CodexRegistrationAttemptId = ATTEMPT,
    plugin_id: CodexPluginId = PLUGIN_ID,
) -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=preflight(),
        attempt_id=attempt_id,
        expected_version=VERSION,
        source_locator=SOURCE,
        installed_locator=INSTALLED,
        digest=DIGEST,
        expected_auth_policy=AUTH_POLICY,
        expected_plugin_id=plugin_id,
    )


def malformed_request(plugin_id: object, missing: bool = False) -> CodexRegistrationPortRequest:
    values: dict[str, object] = {
        "preflight": preflight(),
        "attempt_id": ATTEMPT,
        "expected_version": VERSION,
        "source_locator": SOURCE,
        "installed_locator": INSTALLED,
        "digest": DIGEST,
        "expected_auth_policy": AUTH_POLICY,
        "expected_plugin_id": plugin_id,
    }
    if missing:
        del values["expected_plugin_id"]
    return CodexRegistrationPortRequest.model_construct(_fields_set=set(values), **values)


def observed_path(locator: OwnedRelativePath) -> CodexObservedAbsolutePath:
    expanded_root = ntpath.expandvars(CANONICAL_INSTALL_ROOT)
    return CodexObservedAbsolutePath(value=ntpath.join(expanded_root, *locator.parts()))


def fresh_accepted(current: CodexRegistrationPortRequest | None = None) -> CodexFreshPreflightAccepted:
    current_request = request() if current is None else current
    return CodexFreshPreflightAccepted(
        request=current_request,
        eligible=CodexPreflightEligible(version=current_request.expected_version),
    )


def marketplace_success(
    current: CodexRegistrationPortRequest | None = None,
    already_added: bool = False,
) -> CodexMarketplaceAddSucceeded:
    current_request = request() if current is None else current
    observation = CodexMarketplaceAddObservation(
        marketplace_name=current_request.preflight.marketplace,
        installed_root=observed_path(current_request.source_locator),
        already_added=already_added,
    )
    return CodexMarketplaceAddSucceeded(
        request=current_request,
        confirmed=CodexMarketplaceAddConfirmed(
            target=CodexCommandTarget.MARKETPLACE_ADD,
            start_state=CodexCommandStartState.STARTED,
            already_added=already_added,
        ),
        observation=observation,
    )


def plugin_success(
    current: CodexRegistrationPortRequest | None = None,
    plugin_id: CodexPluginId | None = None,
) -> CodexPluginAddSucceeded:
    current_request = request() if current is None else current
    current_plugin_id = current_request.expected_plugin_id if plugin_id is None else plugin_id
    return CodexPluginAddSucceeded(
        request=current_request,
        confirmed=CodexPluginAddConfirmed(
            target=CodexCommandTarget.PLUGIN_ADD,
            start_state=CodexCommandStartState.STARTED,
        ),
        observation=CodexPluginAddObservation(
            plugin_id=current_plugin_id,
            name=current_request.preflight.plugin,
            marketplace_name=current_request.preflight.marketplace,
            version=current_request.expected_version,
            installed_path=observed_path(current_request.installed_locator),
            auth_policy=current_request.expected_auth_policy,
        ),
    )


def command_failure(
    current: CodexRegistrationPortRequest,
    target: CodexCommandTarget,
    reason: CodexPreStartFailureReason | CodexStartedFailureReason,
) -> CodexRegistrationCommandFailed:
    failure: CodexPreStartFailure | CodexStartedFailure
    if isinstance(reason, CodexPreStartFailureReason):
        failure = CodexPreStartFailure(
            target=target,
            reason=reason,
            start_state=CodexCommandStartState.NOT_STARTED,
        )
    else:
        failure = CodexStartedFailure(
            target=target,
            reason=reason,
            start_state=CodexCommandStartState.STARTED,
        )
    return CodexRegistrationCommandFailed(request=current, failure=failure)


def fresh_pending() -> CodexFreshPreflightPending:
    result = begin_codex_registration(request())
    if not isinstance(result, CodexFreshPreflightPending):
        raise AssertionError("expected fresh pending")
    return result


def marketplace_pending() -> CodexMarketplaceAddPending:
    initial = fresh_pending()
    result = advance_codex_registration(initial, fresh_accepted(initial.request))
    if not isinstance(result, CodexMarketplaceAddPending):
        raise AssertionError("expected marketplace pending")
    return result


def plugin_pending() -> CodexPluginAddPending:
    current = marketplace_pending()
    result = advance_codex_registration(current, marketplace_success(current.request))
    if not isinstance(result, CodexPluginAddPending):
        raise AssertionError("expected plugin pending")
    return result


class CodexRegistrationReducerTests(unittest.TestCase):
    def test_d1_begin_requires_the_new_reducer_boundary(self) -> None:
        self.assertTrue(callable(begin_codex_registration))

    def test_b1_terminal_compensation_retains_the_exact_registration_request(self) -> None:
        current = marketplace_pending()
        terminal = advance_codex_registration(current, None)
        self.assertIsInstance(terminal, CodexRegistrationCompensationRequired)
        if not isinstance(terminal, CodexRegistrationCompensationRequired):
            raise AssertionError("expected terminal compensation")
        self.assertEqual(current.request.model_dump(), terminal.request.model_dump())

    def test_b2_every_terminal_compensation_path_carries_exact_request_context(self) -> None:
        marketplace = marketplace_pending()
        plugin = plugin_pending()
        cases: tuple[tuple[CodexMarketplaceAddPending | CodexPluginAddPending, object], ...] = (
            (marketplace, None),
            (
                plugin,
                command_failure(
                    plugin.request,
                    CodexCommandTarget.PLUGIN_ADD,
                    CodexStartedFailureReason.IDENTITY_MISMATCH,
                ),
            ),
        )
        for current, result in cases:
            with self.subTest(phase=current.status):
                terminal = advance_codex_registration(current, result)
                self.assertIsInstance(terminal, CodexRegistrationCompensationRequired)
                if not isinstance(terminal, CodexRegistrationCompensationRequired):
                    raise AssertionError("expected terminal compensation")
                self.assertEqual(current.request.model_dump(), terminal.request.model_dump())
                self.assertEqual(current.request.preflight.model_dump(), terminal.journal.request.model_dump())
                self.assertEqual(current.request.preflight.model_dump(), terminal.plan.request.model_dump())
                self.assertEqual(current.request.attempt_id.model_dump(), terminal.journal.attempt_id.model_dump())
                self.assertEqual(current.request.attempt_id.model_dump(), terminal.plan.attempt_id.model_dump())

    def test_b3_terminal_compensation_rejects_mismatched_request_journal_and_plan(self) -> None:
        terminal = self.compensation_terminal()
        other_preflight = terminal.request.preflight.model_copy(
            update={"marketplace": CodexMarketplaceName(value="other-market")}
        )
        mismatched_requests: tuple[tuple[str, CodexRegistrationPortRequest], ...] = (
            ("preflight", terminal.request.model_copy(update={"preflight": other_preflight})),
            ("attempt", terminal.request.model_copy(update={"attempt_id": OTHER_ATTEMPT})),
        )
        for field_name, altered_request in mismatched_requests:
            with self.subTest(context="request", field=field_name):
                altered = terminal.model_copy(update={"request": altered_request})
                self.assert_context_rejected(altered)

        malformed_fields = (
            "preflight",
            "attempt_id",
            "expected_version",
            "source_locator",
            "installed_locator",
            "digest",
            "expected_auth_policy",
            "expected_plugin_id",
        )
        for field_name in malformed_fields:
            with self.subTest(context="request-shape", field=field_name):
                trap = PlainTrap()
                malformed_request = terminal.request.model_copy(update={field_name: trap})
                self.assert_context_rejected(terminal.model_copy(update={"request": malformed_request}))
                self.assertEqual(0, trap.invocation_count)

        altered_journal = terminal.journal.model_copy(update={"attempt_id": OTHER_ATTEMPT})
        alternate_plan = terminal.plan.model_copy(
            update={
                "journal": altered_journal,
                "attempt_id": OTHER_ATTEMPT,
                "identity": terminal.plan.identity.model_copy(update={"attempt_id": OTHER_ATTEMPT}),
            }
        )
        self.assert_context_rejected(
            terminal.model_copy(update={"journal": altered_journal, "plan": alternate_plan})
        )

    def test_b3_terminal_compensation_rejects_rebuilt_plan_substitution(self) -> None:
        terminal = self.compensation_terminal()
        substitutions: tuple[tuple[str, CodexCompensationPlan], ...] = (
            ("status", terminal.plan.model_copy(update={"status": "NO_COMPENSATION_REQUIRED"})),
            ("order", terminal.plan.model_copy(update={"steps": tuple(reversed(terminal.plan.steps))})),
            (
                "identity",
                terminal.plan.model_copy(
                    update={
                        "identity": terminal.plan.identity.model_copy(
                            update={"marketplace_state": CodexAttemptEffectState.NOT_ATTEMPTED}
                        )
                    }
                ),
            ),
        )
        for field_name, altered_plan in substitutions:
            with self.subTest(context="plan", field=field_name):
                self.assert_context_rejected(terminal.model_copy(update={"plan": altered_plan}))

    def test_b6_request_journal_equality_rejects_a_foreign_attempt(self) -> None:
        terminal = self.compensation_terminal()
        altered_journal = terminal.journal.model_copy(update={"attempt_id": OTHER_ATTEMPT})
        self.assertFalse(_journal_matches_request(altered_journal, terminal.request))

    def test_b6_rebuilt_plan_equality_rejects_an_order_substitution(self) -> None:
        terminal = self.compensation_terminal()
        altered_plan = terminal.plan.model_copy(update={"steps": tuple(reversed(terminal.plan.steps))})
        self.assertFalse(_plan_matches_rebuild(terminal.plan, altered_plan))

    def test_b4_settlement_rebuild_preserves_context_and_rejects_constructed_invalid_context(self) -> None:
        terminal = self.compensation_terminal()
        rebuilt = _rebuild_compensation_required(terminal)
        self.assertEqual(terminal.model_dump(), rebuilt.model_dump())

        altered_journal = terminal.journal.model_copy(update={"attempt_id": OTHER_ATTEMPT})
        altered = terminal.model_copy(update={"journal": altered_journal})
        with self.assertRaises(ValidationError):
            _rebuild_compensation_required(altered)

    def compensation_terminal(self) -> CodexRegistrationCompensationRequired:
        terminal = advance_codex_registration(marketplace_pending(), None)
        if not isinstance(terminal, CodexRegistrationCompensationRequired):
            raise AssertionError("expected terminal compensation")
        return terminal

    def assert_context_rejected(self, value: CodexRegistrationCompensationRequired) -> None:
        with self.assertRaises(ValidationError):
            CodexRegistrationCompensationRequired.model_validate(value)

    def test_r2_d1_exact_pending_copies_and_reconstruction_reduce_identically(self) -> None:
        fresh = fresh_pending()
        marketplace = marketplace_pending()
        plugin = plugin_pending()
        cases: tuple[tuple[str, CodexFreshPreflightPending | CodexMarketplaceAddPending | CodexPluginAddPending, object], ...] = (
            ("fresh", fresh, fresh_accepted(fresh.request)),
            ("marketplace", marketplace, marketplace_success(marketplace.request)),
            ("plugin", plugin, plugin_success(plugin.request)),
        )
        for phase, original, exact_result in cases:
            with self.subTest(phase=phase):
                expected = advance_codex_registration(original, exact_result)
                variants = (
                    original,
                    copy.copy(original),
                    copy.deepcopy(original),
                    type(original).model_validate(original.model_dump()),
                )
                for variant in variants:
                    actual = advance_codex_registration(variant, exact_result)
                    self.assertIs(type(expected), type(actual))
                    self.assertEqual(expected.model_dump(), actual.model_dump())
                repeated = advance_codex_registration(original, exact_result)
                self.assertIs(type(expected), type(repeated))
                self.assertEqual(expected.model_dump(), repeated.model_dump())

    def test_r2_d2_private_identity_authority_is_completely_absent(self) -> None:
        module_names = registration_reducer.__dict__
        self.assertNotIn("_StateAuthority", module_names)
        self.assertNotIn("_STATE_AUTHORITY", module_names)
        self.assertNotIn("_authorize_pending", module_names)
        self.assertNotIn("_has_current_authority", module_names)
        for pending in (fresh_pending(), marketplace_pending(), plugin_pending()):
            self.assertIsNone(pending.__pydantic_private__)
            self.assertNotIn("_authority", pending.__dict__)
            self.assertNotIn("_identity", pending.__dict__)

    def test_r2_d4_public_pending_and_terminal_data_is_metadata_safe(self) -> None:
        fresh = fresh_pending()
        marketplace = marketplace_pending()
        plugin = plugin_pending()
        proof = advance_codex_registration(plugin, plugin_success(plugin.request))
        compensation = advance_codex_registration(marketplace, None)
        blocked = advance_codex_registration(
            fresh,
            CodexFreshPreflightRejected(request=fresh.request, reason=CodexBlockReason.COLLISION),
        )
        decisions = (fresh, marketplace, plugin, proof, compensation, blocked)
        forbidden = (
            "_authority",
            "_identity",
            "lease",
            "generation",
            "receipt",
            "callable",
            "raw_output",
            "secret",
        )
        for decision in decisions:
            public_text = f"{decision.model_dump()} {repr(decision)}".casefold()
            for token in forbidden:
                with self.subTest(decision=type(decision).__name__, token=token):
                    self.assertNotIn(token, public_text)

    def test_cr149_missing_required_pending_status_returns_invalid_state(self) -> None:
        fresh = fresh_pending()
        marketplace = marketplace_pending()
        plugin = plugin_pending()
        cases: tuple[tuple[str, CodexFreshPreflightPending | CodexMarketplaceAddPending | CodexPluginAddPending, object], ...] = (
            (
                "fresh",
                CodexFreshPreflightPending.model_construct(request=fresh.request, journal=fresh.journal),
                fresh_accepted(fresh.request),
            ),
            (
                "marketplace",
                CodexMarketplaceAddPending.model_construct(request=marketplace.request, journal=marketplace.journal),
                marketplace_success(marketplace.request),
            ),
            (
                "plugin",
                CodexPluginAddPending.model_construct(
                    request=plugin.request,
                    journal=plugin.journal,
                    marketplace_observation=plugin.marketplace_observation,
                ),
                plugin_success(plugin.request),
            ),
        )
        for phase, pending, exact_result in cases:
            with self.subTest(phase=phase):
                object.__delattr__(pending, "status")
                self.assert_blocked(
                    advance_codex_registration(pending, exact_result),
                    CodexRegistrationBlockReason.INVALID_STATE,
                )

    def test_d2_begin_rebuilds_exact_request_and_blocks_all_invalid_shapes(self) -> None:
        supplied = request()
        result = begin_codex_registration(supplied)
        self.assertIsInstance(result, CodexFreshPreflightPending)
        if not isinstance(result, CodexFreshPreflightPending):
            raise AssertionError("expected fresh pending")
        self.assertIsNot(supplied, result.request)
        self.assertEqual(CodexAttemptEffectState.NOT_ATTEMPTED, result.journal.marketplace_state)
        self.assertEqual(CodexAttemptEffectState.NOT_ATTEMPTED, result.journal.plugin_state)
        self.assertEqual((), result.journal.unresolved_removal_order())

        trap = PlainTrap()
        invalid_values: tuple[tuple[str, object], ...] = (
            ("missing", malformed_request(PLUGIN_ID, missing=True)),
            ("none", None),
            ("empty", ""),
            ("whitespace", " "),
            ("list", []),
            ("dict", {}),
            ("plain-object", trap),
            ("constructed-invalid", malformed_request(PLUGIN_ID.value)),
        )
        for label, value in invalid_values:
            with self.subTest(shape=label):
                blocked = begin_codex_registration(value)
                self.assert_blocked(blocked, CodexRegistrationBlockReason.INVALID_REQUEST)
        self.assertEqual(0, trap.invocation_count)

    def test_d3_fresh_phase_accepts_only_exact_current_eligible_truth(self) -> None:
        current = fresh_pending()
        advanced = advance_codex_registration(current, fresh_accepted(current.request))
        self.assertIsInstance(advanced, CodexMarketplaceAddPending)

        rejected = CodexFreshPreflightRejected(
            request=current.request,
            reason=CodexBlockReason.COLLISION,
        )
        self.assert_blocked(
            advance_codex_registration(current, rejected),
            CodexRegistrationBlockReason.FRESH_PREFLIGHT_REJECTED,
        )
        wrong_version = CodexFreshPreflightAccepted(
            request=current.request,
            eligible=CodexPreflightEligible(version=CodexCliVersion(value="9.9.9")),
        )
        foreign = fresh_accepted(request(attempt_id=OTHER_ATTEMPT))
        trap = PlainTrap()
        invalid_values: tuple[object, ...] = (None, "", " ", [], {}, trap, wrong_version, foreign)
        for value in invalid_values:
            blocked = advance_codex_registration(current, value)
            self.assert_blocked(blocked, CodexRegistrationBlockReason.FRESH_PREFLIGHT_INVALID)
            self.assertNotIn(observed_path(SOURCE).value, repr(blocked))
        self.assertEqual(0, trap.invocation_count)

    def test_d4_marketplace_matrix_preserves_only_exact_new_ownership(self) -> None:
        current = marketplace_pending()
        new_result = advance_codex_registration(current, marketplace_success(current.request))
        self.assertIsInstance(new_result, CodexPluginAddPending)
        if not isinstance(new_result, CodexPluginAddPending):
            raise AssertionError("expected plugin pending")
        self.assertEqual(CodexAttemptEffectState.OWNED, new_result.journal.marketplace_state)
        self.assertEqual(CodexAttemptEffectState.NOT_ATTEMPTED, new_result.journal.plugin_state)

        for pre_start_reason in CodexPreStartFailureReason:
            blocked = advance_codex_registration(
                current,
                command_failure(current.request, CodexCommandTarget.MARKETPLACE_ADD, pre_start_reason),
            )
            self.assert_blocked(blocked, CodexRegistrationBlockReason.MARKETPLACE_ADD_NOT_STARTED)
        for started_reason in CodexStartedFailureReason:
            compensated = advance_codex_registration(
                current,
                command_failure(current.request, CodexCommandTarget.MARKETPLACE_ADD, started_reason),
            )
            self.assert_compensation(compensated, CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED, MARKETPLACE_PLAN_STEPS)

        wrong_target = command_failure(
            current.request,
            CodexCommandTarget.PLUGIN_ADD,
            CodexStartedFailureReason.IDENTITY_MISMATCH,
        )
        self.assert_compensation(
            advance_codex_registration(current, wrong_target),
            CodexAttemptEffectState.MAY_EXIST,
            CodexAttemptEffectState.NOT_ATTEMPTED,
            MARKETPLACE_PLAN_STEPS,
        )
        foreign_success = marketplace_success(request(attempt_id=OTHER_ATTEMPT))
        self.assert_compensation(
            advance_codex_registration(current, foreign_success),
            CodexAttemptEffectState.MAY_EXIST,
            CodexAttemptEffectState.NOT_ATTEMPTED,
            MARKETPLACE_PLAN_STEPS,
        )

    def test_d4_d7_preexisting_marketplace_never_grants_removal_authority(self) -> None:
        current = marketplace_pending()
        result = advance_codex_registration(current, marketplace_success(current.request, already_added=True))
        self.assert_blocked(result, CodexRegistrationBlockReason.MARKETPLACE_PREEXISTING)
        self.assertNotIsInstance(result, CodexRegistrationCompensationRequired)

    def test_d4_d7_malformed_marketplace_return_compensates_conservatively(self) -> None:
        current = marketplace_pending()
        trap = PlainTrap()
        malformed_values: tuple[object, ...] = (None, "", " ", [], {}, trap)
        for value in malformed_values:
            with self.subTest(shape=type(value).__name__):
                self.assert_compensation(
                    advance_codex_registration(current, value),
                    CodexAttemptEffectState.MAY_EXIST,
                    CodexAttemptEffectState.NOT_ATTEMPTED,
                    MARKETPLACE_PLAN_STEPS,
                )
        self.assertEqual(0, trap.invocation_count)

    def test_d5_plugin_matrix_returns_only_proof_or_exact_compensation(self) -> None:
        current = plugin_pending()
        for pre_start_reason in CodexPreStartFailureReason:
            compensated = advance_codex_registration(
                current,
                command_failure(current.request, CodexCommandTarget.PLUGIN_ADD, pre_start_reason),
            )
            self.assert_compensation(compensated, CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED, MARKETPLACE_PLAN_STEPS)
        for started_reason in CodexStartedFailureReason:
            compensated = advance_codex_registration(
                current,
                command_failure(current.request, CodexCommandTarget.PLUGIN_ADD, started_reason),
            )
            self.assert_compensation(compensated, CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST, PLUGIN_FIRST_PLAN_STEPS)

        trap = PlainTrap()
        untrusted_values: tuple[object, ...] = (
            None,
            "",
            " ",
            [],
            {},
            trap,
            command_failure(
                current.request,
                CodexCommandTarget.MARKETPLACE_ADD,
                CodexStartedFailureReason.IDENTITY_MISMATCH,
            ),
            plugin_success(request(attempt_id=OTHER_ATTEMPT)),
            plugin_success(current.request, FOREIGN_PLUGIN_ID),
        )
        for value in untrusted_values:
            self.assert_compensation(
                advance_codex_registration(current, value),
                CodexAttemptEffectState.OWNED,
                CodexAttemptEffectState.MAY_EXIST,
                PLUGIN_FIRST_PLAN_STEPS,
            )
        self.assertEqual(0, trap.invocation_count)

    def test_d5_d7_proof_binds_exact_expected_plugin_id(self) -> None:
        current = plugin_pending()
        result = advance_codex_registration(current, plugin_success(current.request))
        self.assertIsInstance(result, CodexRegistrationProofRequired)
        if not isinstance(result, CodexRegistrationProofRequired):
            raise AssertionError("expected proof request")
        self.assertEqual(CodexAttemptEffectState.OWNED, result.journal.marketplace_state)
        self.assertEqual(CodexAttemptEffectState.OWNED, result.journal.plugin_state)
        self.assertEqual(PLUGIN_ID.value, result.proof_request.plugin_observation.plugin_id.value)
        self.assertEqual(current.marketplace_observation, result.proof_request.marketplace_observation)
        self.assertEqual(current.request.expected_version, result.proof_request.version)
        self.assertFalse(hasattr(result, "receipt"))

    def test_d6_d7_plugin_before_marketplace_is_rejected(self) -> None:
        current = fresh_pending()
        result = advance_codex_registration(current, plugin_success(current.request))
        self.assert_blocked(result, CodexRegistrationBlockReason.FRESH_PREFLIGHT_INVALID)

    def test_d6_phase_terminal_and_invalid_nested_shape_guards_are_closed(self) -> None:
        fresh = fresh_pending()
        missing_request = CodexMarketplaceAddPending.model_construct(journal=fresh.journal)
        self.assert_blocked(
            advance_codex_registration(missing_request, marketplace_success(fresh.request)),
            CodexRegistrationBlockReason.INVALID_STATE,
        )
        missing_journal = CodexMarketplaceAddPending.model_construct(request=fresh.request)
        self.assert_blocked(
            advance_codex_registration(missing_journal, marketplace_success(fresh.request)),
            CodexRegistrationBlockReason.INVALID_STATE,
        )
        current_plugin = plugin_pending()
        missing_observation = CodexPluginAddPending.model_construct(
            request=current_plugin.request,
            journal=current_plugin.journal,
        )
        self.assert_blocked(
            advance_codex_registration(missing_observation, plugin_success(current_plugin.request)),
            CodexRegistrationBlockReason.INVALID_STATE,
        )

        trap_values: tuple[object, ...] = (None, "", " ", [], {}, PlainTrap())
        for value in trap_values:
            request_state = marketplace_pending()
            object.__setattr__(request_state, "request", value)
            self.assert_blocked(
                advance_codex_registration(request_state, marketplace_success()),
                CodexRegistrationBlockReason.INVALID_STATE,
            )
            journal_state = marketplace_pending()
            object.__setattr__(journal_state, "journal", value)
            self.assert_blocked(
                advance_codex_registration(journal_state, marketplace_success()),
                CodexRegistrationBlockReason.INVALID_STATE,
            )
            observation_state = plugin_pending()
            object.__setattr__(observation_state, "marketplace_observation", value)
            self.assert_blocked(
                advance_codex_registration(observation_state, plugin_success()),
                CodexRegistrationBlockReason.INVALID_STATE,
            )
        self.assertTrue(all(not isinstance(value, PlainTrap) or value.invocation_count == 0 for value in trap_values))

        terminal = advance_codex_registration(fresh, CodexFreshPreflightRejected(request=fresh.request, reason=CodexBlockReason.COLLISION))
        self.assert_blocked(
            advance_codex_registration(terminal, fresh_accepted(fresh.request)),
            CodexRegistrationBlockReason.INVALID_STATE,
        )
        market = marketplace_pending()
        replay = advance_codex_registration(market, fresh_accepted(market.request))
        self.assertNotIsInstance(replay, CodexPluginAddPending)
        self.assertNotIsInstance(replay, CodexRegistrationProofRequired)

    def assert_blocked(self, result: object, reason: CodexRegistrationBlockReason) -> None:
        if not isinstance(result, CodexRegistrationBlocked):
            raise AssertionError(f"expected block, received {type(result).__name__}")
        self.assertIs(reason, result.reason)
        self.assertEqual({"status": "REGISTRATION_BLOCKED", "reason": reason}, result.model_dump())

    def assert_compensation(
        self,
        result: object,
        marketplace_state: CodexAttemptEffectState,
        plugin_state: CodexAttemptEffectState,
        steps: tuple[CodexCompensationStep, ...],
    ) -> None:
        if not isinstance(result, CodexRegistrationCompensationRequired):
            raise AssertionError(f"expected compensation, received {type(result).__name__}")
        self.assertIsInstance(result.plan, CodexCompensationPlan)
        self.assertEqual(marketplace_state, result.journal.marketplace_state)
        self.assertEqual(plugin_state, result.journal.plugin_state)
        self.assertEqual(steps, result.plan.steps)
        self.assertEqual(result.journal, result.plan.journal)


if __name__ == "__main__":
    unittest.main()
