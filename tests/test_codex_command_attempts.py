"""C1-C4 closure for pure Codex mutation command-attempt classification."""

from __future__ import annotations

from typing import cast
import unittest

from pydantic import BaseModel, ValidationError

from library.local_orchestration.codex_command_attempts import (
    CodexCommandClassificationRejectReason,
    CodexCommandClassificationRejected,
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
    CodexPreStartFailure,
    CodexPreStartFailureReason,
    CodexStartedFailure,
    CodexStartedFailureReason,
    classify_command_attempt,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAttemptEffect,
    CodexAttemptEffectState,
    CodexRegistrationAttemptId,
    CodexRegistrationAttemptJournal,
)
from library.local_orchestration.contracts import CANONICAL_INSTALL_ROOT, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import CodexMarketplaceName, CodexPluginName, CodexPreflightRequest


INSTALLATION = InstallationId(value="installation-0123456789abcdef")
ROOT = InstallRoot(value=CANONICAL_INSTALL_ROOT)
MARKETPLACE = CodexMarketplaceName(value="probe-market")
PLUGIN = CodexPluginName(value="probe-plugin")
ATTEMPT = CodexRegistrationAttemptId(value="attempt-0123456789abcdef")


def request() -> CodexPreflightRequest:
    return CodexPreflightRequest(
        installation_id=INSTALLATION,
        root=ROOT,
        marketplace=MARKETPLACE,
        plugin=PLUGIN,
        marketplace_source=OwnedRelativePath(value="marketplaces/probe-market"),
    )


def journal(
    marketplace_state: CodexAttemptEffectState,
    plugin_state: CodexAttemptEffectState,
) -> CodexRegistrationAttemptJournal:
    return CodexRegistrationAttemptJournal(
        request=request(),
        attempt_id=ATTEMPT,
        marketplace_state=marketplace_state,
        plugin_state=plugin_state,
    )


def pre_start(
    target: CodexCommandTarget,
    reason: CodexPreStartFailureReason,
) -> CodexPreStartFailure:
    return CodexPreStartFailure(
        target=target,
        reason=reason,
        start_state=CodexCommandStartState.NOT_STARTED,
    )


def started_failure(
    target: CodexCommandTarget,
    reason: CodexStartedFailureReason,
) -> CodexStartedFailure:
    return CodexStartedFailure(
        target=target,
        reason=reason,
        start_state=CodexCommandStartState.STARTED,
    )


def marketplace_confirmation(already_added: bool) -> CodexMarketplaceAddConfirmed:
    return CodexMarketplaceAddConfirmed(
        target=CodexCommandTarget.MARKETPLACE_ADD,
        start_state=CodexCommandStartState.STARTED,
        already_added=already_added,
    )


def plugin_confirmation() -> CodexPluginAddConfirmed:
    return CodexPluginAddConfirmed(
        target=CodexCommandTarget.PLUGIN_ADD,
        start_state=CodexCommandStartState.STARTED,
    )


class UnexpectedJournal:
    """Adversarial boundary object that raises only its declared exception type."""

    def __init__(self, exception_type: type[BaseException]) -> None:
        self._exception_type = exception_type

    def model_dump_json(self, *, warnings: bool = False) -> str:
        raise self._exception_type()


class CodexCommandAttemptTests(unittest.TestCase):
    def test_n1_no_effect_pre_start_reasons_are_closed_and_not_started(self) -> None:
        expected_reasons = (
            CodexPreStartFailureReason.INVALID_REQUEST,
            CodexPreStartFailureReason.REQUEST_MISMATCH,
        )
        for target in CodexCommandTarget:
            for reason in expected_reasons:
                with self.subTest(target=target, reason=reason):
                    observation = CodexPreStartFailure(
                        target=target,
                        reason=reason,
                        start_state=CodexCommandStartState.NOT_STARTED,
                    )
                    self.assertIs(CodexCommandStartState.NOT_STARTED, observation.start_state)

    def test_t1_c1_requires_every_declared_observation_field(self) -> None:
        observation_payloads: tuple[tuple[type[BaseModel], dict[str, object]], ...] = (
            (
                CodexPreStartFailure,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "reason": CodexPreStartFailureReason.ACCESS_DENIED,
                    "start_state": CodexCommandStartState.NOT_STARTED,
                },
            ),
            (
                CodexStartedFailure,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "reason": CodexStartedFailureReason.NONZERO_EXIT,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
            (
                CodexMarketplaceAddConfirmed,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "start_state": CodexCommandStartState.STARTED,
                    "already_added": False,
                },
            ),
            (
                CodexPluginAddConfirmed,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
        )
        for model_type, payload in observation_payloads:
            for missing_field in payload:
                with self.subTest(model=model_type.__name__, missing=missing_field):
                    missing_payload = dict(payload)
                    del missing_payload[missing_field]
                    with self.assertRaises(ValidationError):
                        model_type.model_validate(missing_payload)

    def test_t1_c1_rejects_constructed_raw_python_literals(self) -> None:
        raw_cases = (
            (
                CodexPreStartFailure.model_construct(
                    target="MARKETPLACE_ADD",
                    reason="ACCESS_DENIED",
                    start_state="NOT_STARTED",
                ),
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            ),
            (
                CodexStartedFailure.model_construct(
                    target="MARKETPLACE_ADD",
                    reason="NONZERO_EXIT",
                    start_state="STARTED",
                ),
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            ),
            (
                CodexMarketplaceAddConfirmed.model_construct(
                    target="MARKETPLACE_ADD",
                    start_state="STARTED",
                    already_added=False,
                ),
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            ),
            (
                CodexMarketplaceAddConfirmed.model_construct(
                    target=CodexCommandTarget.MARKETPLACE_ADD,
                    start_state=CodexCommandStartState.STARTED,
                    already_added="false",
                ),
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            ),
            (
                CodexPluginAddConfirmed.model_construct(
                    target="PLUGIN_ADD",
                    start_state="STARTED",
                ),
                journal(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED),
            ),
        )
        for observation, current_journal in raw_cases:
            with self.subTest(observation=type(observation).__name__):
                self._assert_rejected(
                    classify_command_attempt(observation, current_journal, request(), ATTEMPT),
                    CodexCommandClassificationRejectReason.INVALID_OBSERVATION,
                )

    def test_t1_c1_complete_strict_boundary_shape_table(self) -> None:
        observation_payloads: tuple[tuple[type[BaseModel], dict[str, object]], ...] = (
            (
                CodexPreStartFailure,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "reason": CodexPreStartFailureReason.ACCESS_DENIED,
                    "start_state": CodexCommandStartState.NOT_STARTED,
                },
            ),
            (
                CodexStartedFailure,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "reason": CodexStartedFailureReason.NONZERO_EXIT,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
            (
                CodexMarketplaceAddConfirmed,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "start_state": CodexCommandStartState.STARTED,
                    "already_added": False,
                },
            ),
            (
                CodexPluginAddConfirmed,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
        )
        invalid_values: tuple[object, ...] = (None, "", " ", [], {})
        for model_type, payload in observation_payloads:
            for field_name in payload:
                for invalid_value in invalid_values:
                    with self.subTest(model=model_type.__name__, field=field_name, value=repr(invalid_value)):
                        invalid_payload = dict(payload)
                        invalid_payload[field_name] = invalid_value
                        with self.assertRaises(ValidationError):
                            model_type.model_validate(invalid_payload)
            with self.subTest(model=model_type.__name__, extra="forbidden"):
                with self.assertRaises(ValidationError):
                    model_type.model_validate(payload | {"extra": "forbidden"})
        wrong_literal_payloads: tuple[tuple[type[BaseModel], dict[str, object]], ...] = (
            (
                CodexPreStartFailure,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "reason": CodexStartedFailureReason.NONZERO_EXIT,
                    "start_state": CodexCommandStartState.NOT_STARTED,
                },
            ),
            (
                CodexPreStartFailure,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "reason": CodexPreStartFailureReason.ACCESS_DENIED,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
            (
                CodexStartedFailure,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "reason": CodexPreStartFailureReason.ACCESS_DENIED,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
            (
                CodexStartedFailure,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "reason": CodexStartedFailureReason.NONZERO_EXIT,
                    "start_state": CodexCommandStartState.NOT_STARTED,
                },
            ),
            (
                CodexMarketplaceAddConfirmed,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "start_state": CodexCommandStartState.STARTED,
                    "already_added": False,
                },
            ),
            (
                CodexMarketplaceAddConfirmed,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "start_state": CodexCommandStartState.NOT_STARTED,
                    "already_added": False,
                },
            ),
            (
                CodexPluginAddConfirmed,
                {
                    "target": CodexCommandTarget.MARKETPLACE_ADD,
                    "start_state": CodexCommandStartState.STARTED,
                },
            ),
            (
                CodexPluginAddConfirmed,
                {
                    "target": CodexCommandTarget.PLUGIN_ADD,
                    "start_state": CodexCommandStartState.NOT_STARTED,
                },
            ),
        )
        for model_type, wrong_payload in wrong_literal_payloads:
            with self.subTest(model=model_type.__name__, wrong=wrong_payload):
                with self.assertRaises(ValidationError):
                    model_type.model_validate(wrong_payload)

    def test_t1_c1_all_finite_observations_are_strict_and_start_state_bound(self) -> None:
        pre_start_reasons = tuple(CodexPreStartFailureReason)
        started_reasons = tuple(CodexStartedFailureReason)
        self.assertEqual(5, len(pre_start_reasons))
        self.assertEqual(6, len(started_reasons))
        for target in CodexCommandTarget:
            for pre_start_reason in pre_start_reasons:
                with self.subTest(pre_start_target=target, reason=pre_start_reason):
                    pre_start_observation = pre_start(target, pre_start_reason)
                    self.assertIs(CodexCommandStartState.NOT_STARTED, pre_start_observation.start_state)
            for started_reason in started_reasons:
                with self.subTest(started_target=target, reason=started_reason):
                    started_observation = started_failure(target, started_reason)
                    self.assertIs(CodexCommandStartState.STARTED, started_observation.start_state)
        fresh_marketplace_confirmation = marketplace_confirmation(already_added=False)
        existing_marketplace_confirmation = marketplace_confirmation(already_added=True)
        confirmed_plugin = plugin_confirmation()
        self.assertIs(CodexCommandTarget.MARKETPLACE_ADD, fresh_marketplace_confirmation.target)
        self.assertIs(CodexCommandTarget.MARKETPLACE_ADD, existing_marketplace_confirmation.target)
        self.assertIs(CodexCommandTarget.PLUGIN_ADD, confirmed_plugin.target)
        required_models: tuple[tuple[type[CodexPreStartFailure | CodexStartedFailure | CodexMarketplaceAddConfirmed], dict[str, object]], ...] = (
            (
                CodexPreStartFailure,
                {"target": CodexCommandTarget.MARKETPLACE_ADD, "reason": CodexPreStartFailureReason.ACCESS_DENIED},
            ),
            (
                CodexStartedFailure,
                {"target": CodexCommandTarget.PLUGIN_ADD, "reason": CodexStartedFailureReason.NONZERO_EXIT},
            ),
            (CodexMarketplaceAddConfirmed, {"already_added": False}),
        )
        for model_type, fields in required_models:
            for field in fields:
                with self.subTest(missing_model=model_type.__name__, missing_field=field):
                    missing = dict(fields)
                    del missing[field]
                    with self.assertRaises(ValidationError):
                        model_type.model_validate(missing)
            with self.subTest(extra_model=model_type.__name__):
                with self.assertRaises(ValidationError):
                    model_type.model_validate(fields | {"extra": "forbidden"})
        invalid_values: tuple[object, ...] = (None, "", " ", [], {})
        for value in invalid_values:
            with self.subTest(pre_start_target=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexPreStartFailure.model_validate({"target": value, "reason": CodexPreStartFailureReason.ACCESS_DENIED})
            with self.subTest(pre_start_reason=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexPreStartFailure.model_validate({"target": CodexCommandTarget.MARKETPLACE_ADD, "reason": value})
            with self.subTest(started_target=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexStartedFailure.model_validate({"target": value, "reason": CodexStartedFailureReason.NONZERO_EXIT})
            with self.subTest(started_reason=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexStartedFailure.model_validate({"target": CodexCommandTarget.PLUGIN_ADD, "reason": value})
            with self.subTest(already_added=repr(value)):
                with self.assertRaises(ValidationError):
                    CodexMarketplaceAddConfirmed.model_validate({"already_added": value})
        with self.assertRaises(ValidationError):
            CodexPreStartFailure.model_validate({
                "target": CodexCommandTarget.MARKETPLACE_ADD,
                "reason": CodexPreStartFailureReason.ACCESS_DENIED,
                "start_state": CodexCommandStartState.STARTED,
            })
        with self.assertRaises(ValidationError):
            CodexStartedFailure.model_validate({
                "target": CodexCommandTarget.PLUGIN_ADD,
                "reason": CodexStartedFailureReason.NONZERO_EXIT,
                "start_state": CodexCommandStartState.NOT_STARTED,
            })
        with self.assertRaises(ValidationError):
            CodexPluginAddConfirmed.model_validate({"extra": "forbidden"})
        constructed_observations = (
            CodexPreStartFailure.model_construct(
                target=CodexCommandTarget.MARKETPLACE_ADD,
                reason=CodexPreStartFailureReason.ACCESS_DENIED,
                start_state=CodexCommandStartState.STARTED,
            ),
            CodexStartedFailure.model_construct(
                target=CodexCommandTarget.PLUGIN_ADD,
                reason=CodexStartedFailureReason.NONZERO_EXIT,
                start_state=CodexCommandStartState.NOT_STARTED,
            ),
            CodexMarketplaceAddConfirmed.model_construct(
                target=CodexCommandTarget.PLUGIN_ADD,
                start_state=CodexCommandStartState.STARTED,
                already_added=False,
            ),
            CodexPluginAddConfirmed.model_construct(
                target=CodexCommandTarget.MARKETPLACE_ADD,
                start_state=CodexCommandStartState.STARTED,
            ),
        )
        for constructed in constructed_observations:
            with self.subTest(constructed=type(constructed).__name__):
                self._assert_rejected(
                    classify_command_attempt(
                        constructed,
                        journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
                        request(),
                        ATTEMPT,
                    ),
                    CodexCommandClassificationRejectReason.INVALID_OBSERVATION,
                )

    def test_t2_c2_admission_is_exact_for_all_fourteen_command_journal_pairs(self) -> None:
        legal_states = (
            (CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.PREEXISTING),
            (CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED),
        )
        observations = (
            pre_start(CodexCommandTarget.MARKETPLACE_ADD, CodexPreStartFailureReason.ACCESS_DENIED),
            pre_start(CodexCommandTarget.PLUGIN_ADD, CodexPreStartFailureReason.ACCESS_DENIED),
        )
        success_pairs = {
            (CodexCommandTarget.MARKETPLACE_ADD, CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexCommandTarget.PLUGIN_ADD, CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED),
        }
        success_count = 0
        rejection_count = 0
        for observation in observations:
            for marketplace_state, plugin_state in legal_states:
                with self.subTest(target=observation.target, marketplace=marketplace_state, plugin=plugin_state):
                    result = classify_command_attempt(
                        observation,
                        journal(marketplace_state, plugin_state),
                        request(),
                        ATTEMPT,
                    )
                    pair = (observation.target, marketplace_state, plugin_state)
                    if pair in success_pairs:
                        self.assertIsInstance(result, CodexRegistrationAttemptJournal)
                        success_count += 1
                    else:
                        self._assert_rejected(result, CodexCommandClassificationRejectReason.INVALID_SEQUENCE)
                        rejection_count += 1
        self.assertEqual(2, success_count)
        self.assertEqual(12, rejection_count)
        malformed = CodexRegistrationAttemptJournal.model_construct(
            request=request(),
            attempt_id=ATTEMPT,
            marketplace_state=CodexAttemptEffectState.MAY_EXIST,
            plugin_state=CodexAttemptEffectState.OWNED,
        )
        self._assert_rejected(
            classify_command_attempt(observations[0], malformed, request(), ATTEMPT),
            CodexCommandClassificationRejectReason.JOURNAL_INVALID,
        )
        replayed_attempt = CodexRegistrationAttemptId(value="attempt-fedcba9876543210")
        self._assert_rejected(
            classify_command_attempt(
                observations[0],
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
                request(),
                replayed_attempt,
            ),
            CodexCommandClassificationRejectReason.JOURNAL_ATTEMPT_MISMATCH,
        )
        other_request = CodexPreflightRequest(
            installation_id=INSTALLATION,
            root=ROOT,
            marketplace=CodexMarketplaceName(value="other-market"),
            plugin=PLUGIN,
            marketplace_source=OwnedRelativePath(value="marketplaces/other-market"),
        )
        self._assert_rejected(
            classify_command_attempt(
                observations[0],
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
                other_request,
                ATTEMPT,
            ),
            CodexCommandClassificationRejectReason.JOURNAL_REQUEST_MISMATCH,
        )

    def test_t3_c3_exact_transition_preserves_or_grants_only_declared_authority(self) -> None:
        admitted_targets = (
            (CodexCommandTarget.MARKETPLACE_ADD, journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED)),
            (CodexCommandTarget.PLUGIN_ADD, journal(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED)),
        )
        for target, before in admitted_targets:
            for reason in CodexPreStartFailureReason:
                with self.subTest(pre_start_target=target, reason=reason):
                    result = classify_command_attempt(pre_start(target, reason), before, request(), ATTEMPT)
                    self._assert_journal(result, before.marketplace_state, before.plugin_state, before.unresolved_removal_order())
                    self.assertEqual(before, result)
        for target, before in admitted_targets:
            expected_state = (
                (CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED)
                if target is CodexCommandTarget.MARKETPLACE_ADD
                else (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST)
            )
            expected_order = (
                (CodexAttemptEffect.MARKETPLACE,)
                if target is CodexCommandTarget.MARKETPLACE_ADD
                else (CodexAttemptEffect.PLUGIN, CodexAttemptEffect.MARKETPLACE)
            )
            for started_reason in CodexStartedFailureReason:
                with self.subTest(started_target=target, reason=started_reason):
                    result = classify_command_attempt(started_failure(target, started_reason), before, request(), ATTEMPT)
                    self._assert_journal(result, expected_state[0], expected_state[1], expected_order)
        marketplace_before = journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED)
        fresh_marketplace = classify_command_attempt(marketplace_confirmation(already_added=False), marketplace_before, request(), ATTEMPT)
        self._assert_journal(fresh_marketplace, CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexAttemptEffect.MARKETPLACE,))
        existing_marketplace = classify_command_attempt(marketplace_confirmation(already_added=True), marketplace_before, request(), ATTEMPT)
        self._assert_journal(existing_marketplace, CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED, ())
        plugin_before = journal(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED)
        plugin_result = classify_command_attempt(plugin_confirmation(), plugin_before, request(), ATTEMPT)
        self._assert_journal(plugin_result, CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED, (CodexAttemptEffect.PLUGIN, CodexAttemptEffect.MARKETPLACE))

    def test_t4_c4_results_are_limited_and_unexpected_exceptions_propagate(self) -> None:
        valid_result = classify_command_attempt(
            marketplace_confirmation(already_added=False),
            journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            request(),
            ATTEMPT,
        )
        self.assertIsInstance(valid_result, CodexRegistrationAttemptJournal)
        rejected = classify_command_attempt(
            plugin_confirmation(),
            journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            request(),
            ATTEMPT,
        )
        self._assert_rejected(rejected, CodexCommandClassificationRejectReason.INVALID_SEQUENCE)
        serialized = rejected.model_dump_json(warnings=False)
        for forbidden_field in ("receipt", "compensation", "success", "stdout", "stderr", "path", "exception"):
            self.assertNotIn(forbidden_field, serialized)
        malformed = CodexPluginAddConfirmed.model_construct(target=CodexCommandTarget.MARKETPLACE_ADD)
        self._assert_rejected(
            classify_command_attempt(
                malformed,
                journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
                request(),
                ATTEMPT,
            ),
            CodexCommandClassificationRejectReason.INVALID_OBSERVATION,
        )
        for exception_type in (RuntimeError, MemoryError, KeyboardInterrupt, SystemExit):
            with self.subTest(exception=exception_type.__name__):
                unexpected_journal = cast(CodexRegistrationAttemptJournal, UnexpectedJournal(exception_type))
                with self.assertRaises(exception_type):
                    classify_command_attempt(
                        pre_start(CodexCommandTarget.MARKETPLACE_ADD, CodexPreStartFailureReason.ACCESS_DENIED),
                        unexpected_journal,
                        request(),
                        ATTEMPT,
                    )

    def _assert_journal(
        self,
        result: CodexRegistrationAttemptJournal | CodexCommandClassificationRejected,
        marketplace_state: CodexAttemptEffectState,
        plugin_state: CodexAttemptEffectState,
        removal_order: tuple[CodexAttemptEffect, ...],
    ) -> None:
        if not isinstance(result, CodexRegistrationAttemptJournal):
            raise AssertionError(f"expected journal, received {result}")
        self.assertIs(marketplace_state, result.marketplace_state)
        self.assertIs(plugin_state, result.plugin_state)
        self.assertEqual(removal_order, result.unresolved_removal_order())

    def _assert_rejected(
        self,
        result: CodexRegistrationAttemptJournal | CodexCommandClassificationRejected,
        expected: CodexCommandClassificationRejectReason,
    ) -> None:
        if not isinstance(result, CodexCommandClassificationRejected):
            raise AssertionError(f"expected rejection, received {result}")
        if result.reason is not expected:
            raise AssertionError(f"expected {expected}, received {result.reason}")


if __name__ == "__main__":
    unittest.main()
