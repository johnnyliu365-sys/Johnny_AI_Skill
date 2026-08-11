"""B1-B5 closure for the pure Codex compensation planner and reducer."""

from __future__ import annotations

from typing import cast
import unittest

from pydantic import BaseModel, ValidationError

from library.local_orchestration.codex_compensation_reducer import (
    CodexCompensationBlocked,
    CodexCompensationBlockReason,
    CodexCompensationFailed,
    CodexCompensationNoop,
    CodexCompensationObservation,
    CodexCompensationPlan,
    CodexCompensationReason,
    CodexCompensationResult,
    CodexCompensationStep,
    CodexCompensated,
    CodexInstalledLocationProof,
    CodexMarketplaceProof,
    CodexNoCompensationPlan,
    CodexPluginListsProof,
    CodexProofTruth,
    CodexRemovalConfirmed,
    CodexRemovalFailed,
    build_compensation_plan,
    reduce_compensation,
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


def valid_plan(
    marketplace_state: CodexAttemptEffectState,
    plugin_state: CodexAttemptEffectState,
) -> CodexCompensationPlan | CodexNoCompensationPlan:
    result = build_compensation_plan(journal(marketplace_state, plugin_state), request(), ATTEMPT)
    if isinstance(result, CodexCompensationBlocked):
        raise AssertionError(f"expected plan, received {result}")
    return result


def success_outcomes(
    plan: CodexCompensationPlan | CodexNoCompensationPlan,
) -> tuple[CodexCompensationObservation, ...]:
    outcomes: list[CodexCompensationObservation] = []
    for step in plan.steps:
        if step in (CodexCompensationStep.REMOVE_PLUGIN, CodexCompensationStep.REMOVE_MARKETPLACE):
            outcomes.append(CodexRemovalConfirmed(step=step, status="CONFIRMED"))
        elif step is CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT:
            outcomes.append(
                CodexPluginListsProof(
                    step=step,
                    installed=CodexProofTruth.PROVED_ABSENT,
                    available=CodexProofTruth.PROVED_ABSENT,
                )
            )
        elif step is CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT:
            outcomes.append(CodexInstalledLocationProof(step=step, truth=CodexProofTruth.PROVED_ABSENT))
        else:
            outcomes.append(CodexMarketplaceProof(step=step, truth=CodexProofTruth.PROVED_ABSENT))
    return tuple(outcomes)


def replace_outcome(
    outcomes: tuple[CodexCompensationObservation, ...],
    index: int,
    replacement: CodexCompensationObservation,
) -> tuple[CodexCompensationObservation, ...]:
    return outcomes[:index] + (replacement,) + outcomes[index + 1 :]


class CodexCompensationReducerTests(unittest.TestCase):
    def test_b1_all_seven_legal_journal_pairs_have_exact_result(self) -> None:
        proof_steps = (
            CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
            CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
            CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
        )
        expected: tuple[
            tuple[CodexAttemptEffectState, CodexAttemptEffectState, tuple[CodexCompensationStep, ...]], ...
        ] = (
            (CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED, ()),
            (CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexCompensationStep.REMOVE_MARKETPLACE,) + proof_steps),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexCompensationStep.REMOVE_MARKETPLACE,) + proof_steps),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST, (CodexCompensationStep.REMOVE_PLUGIN, CodexCompensationStep.REMOVE_MARKETPLACE) + proof_steps),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED, (CodexCompensationStep.REMOVE_PLUGIN, CodexCompensationStep.REMOVE_MARKETPLACE) + proof_steps),
            (CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED, ()),
        )
        for marketplace_state, plugin_state, expected_steps in expected:
            with self.subTest(marketplace=marketplace_state, plugin=plugin_state):
                plan = valid_plan(marketplace_state, plugin_state)
                self.assertEqual(expected_steps, plan.steps)
                if expected_steps:
                    self.assertIsInstance(plan, CodexCompensationPlan)
                else:
                    self.assertIsInstance(plan, CodexNoCompensationPlan)
        unreachable = build_compensation_plan(
            journal(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.PREEXISTING),
            request(),
            ATTEMPT,
        )
        self.assert_blocked(unreachable, CodexCompensationBlockReason.UNREACHABLE_JOURNAL_STATE)

    def test_b1_illegal_malformed_cross_request_and_replay_reject_finitely(self) -> None:
        legal_pairs = {
            (CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.PREEXISTING),
            (CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED),
        }
        rejected_count = 0
        for marketplace_state in CodexAttemptEffectState:
            for plugin_state in CodexAttemptEffectState:
                if (marketplace_state, plugin_state) in legal_pairs:
                    continue
                malformed = CodexRegistrationAttemptJournal.model_construct(
                    request=request(),
                    attempt_id=ATTEMPT,
                    marketplace_state=marketplace_state,
                    plugin_state=plugin_state,
                )
                with self.subTest(marketplace=marketplace_state, plugin=plugin_state):
                    self.assert_blocked(
                        build_compensation_plan(malformed, request(), ATTEMPT),
                        CodexCompensationBlockReason.JOURNAL_INVALID,
                    )
                    rejected_count += 1
        self.assertEqual(9, rejected_count)
        cross_request = CodexPreflightRequest(
            installation_id=INSTALLATION,
            root=ROOT,
            marketplace=CodexMarketplaceName(value="other-market"),
            plugin=PLUGIN,
            marketplace_source=OwnedRelativePath(value="marketplaces/other-market"),
        )
        self.assert_blocked(
            build_compensation_plan(journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED), cross_request, ATTEMPT),
            CodexCompensationBlockReason.JOURNAL_REQUEST_MISMATCH,
        )
        replay = CodexRegistrationAttemptId(value="attempt-fedcba9876543210")
        self.assert_blocked(
            build_compensation_plan(journal(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED), request(), replay),
            CodexCompensationBlockReason.JOURNAL_ATTEMPT_MISMATCH,
        )
        malformed = CodexRegistrationAttemptJournal.model_construct(
            request=request(),
            attempt_id=ATTEMPT,
            marketplace_state="MAY_EXIST",
            plugin_state="NOT_ATTEMPTED",
        )
        self.assert_blocked(
            build_compensation_plan(malformed, request(), ATTEMPT),
            CodexCompensationBlockReason.JOURNAL_INVALID,
        )

    def test_b2_authority_alone_controls_removals_then_fixed_proofs(self) -> None:
        no_authority_plans = (
            valid_plan(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED),
            valid_plan(CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED),
        )
        for plan in no_authority_plans:
            with self.subTest(no_authority=plan.journal.marketplace_state):
                self.assertEqual((), plan.steps)
                self.assertEqual((), plan.journal.unresolved_removal_order())
        marketplace_only = valid_plan(CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED)
        self.assertEqual(
            (
                CodexCompensationStep.REMOVE_MARKETPLACE,
                CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
            ),
            marketplace_only.steps,
        )
        both_owned = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        self.assertEqual(CodexCompensationStep.REMOVE_PLUGIN, both_owned.steps[0])
        self.assertEqual(CodexCompensationStep.REMOVE_MARKETPLACE, both_owned.steps[1])
        self.assertEqual(
            (
                CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
            ),
            both_owned.steps[2:],
        )

    def test_b3_requires_exact_complete_outcome_sequence_and_preserves_failure(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        outcomes = success_outcomes(plan)
        self.assert_compensated(reduce_compensation(plan, outcomes))
        invalid_sequences = (
            outcomes[:-1],
            outcomes + (outcomes[-1],),
            (outcomes[1], outcomes[0]) + outcomes[2:],
            replace_outcome(
                outcomes,
                0,
                CodexRemovalConfirmed(
                    step=CodexCompensationStep.REMOVE_MARKETPLACE,
                    status="CONFIRMED",
                ),
            ),
        )
        for sequence in invalid_sequences:
            with self.subTest(sequence=sequence):
                self.assert_blocked(
                    reduce_compensation(plan, sequence),
                    CodexCompensationBlockReason.OUTCOME_SEQUENCE_INVALID,
                )
        altered_plan = CodexCompensationPlan.model_construct(
            journal=plan.journal,
            request=plan.request,
            attempt_id=plan.attempt_id,
            status="COMPENSATION_REQUIRED",
            steps=(CodexCompensationStep.REMOVE_MARKETPLACE,),
        )
        self.assert_blocked(
            reduce_compensation(altered_plan, outcomes),
            CodexCompensationBlockReason.PLAN_INVALID,
        )
        failed_then_complete = replace_outcome(
            outcomes,
            0,
            CodexRemovalFailed(
                step=CodexCompensationStep.REMOVE_PLUGIN,
                status="DECLARED_FAILURE",
            ),
        )
        failed = reduce_compensation(plan, failed_then_complete)
        self.assert_failed(
            failed,
            (CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE,),
            (),
        )
        self.assert_blocked(
            reduce_compensation(plan, failed_then_complete[:-1]),
            CodexCompensationBlockReason.OUTCOME_SEQUENCE_INVALID,
        )

    def test_b3_strict_models_reject_null_container_and_constructed_outcomes(self) -> None:
        observation_payloads: tuple[tuple[type[BaseModel], dict[str, object]], ...] = (
            (CodexRemovalConfirmed, {"step": CodexCompensationStep.REMOVE_PLUGIN, "status": "CONFIRMED"}),
            (CodexRemovalFailed, {"step": CodexCompensationStep.REMOVE_MARKETPLACE, "status": "DECLARED_FAILURE"}),
            (
                CodexPluginListsProof,
                {
                    "step": CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    "installed": CodexProofTruth.PROVED_ABSENT,
                    "available": CodexProofTruth.PROVED_ABSENT,
                },
            ),
            (
                CodexInstalledLocationProof,
                {"step": CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT, "truth": CodexProofTruth.PROVED_ABSENT},
            ),
            (
                CodexMarketplaceProof,
                {"step": CodexCompensationStep.PROVE_MARKETPLACE_ABSENT, "truth": CodexProofTruth.PROVED_ABSENT},
            ),
        )
        invalid_values: tuple[object, ...] = (None, "", " ", [], {})
        for model_type, payload in observation_payloads:
            for missing_field in payload:
                with self.subTest(model=model_type.__name__, missing=missing_field):
                    missing = dict(payload)
                    del missing[missing_field]
                    with self.assertRaises(ValidationError):
                        model_type.model_validate(missing)
            for field_name in payload:
                for invalid_value in invalid_values:
                    with self.subTest(model=model_type.__name__, field=field_name, value=repr(invalid_value)):
                        invalid = dict(payload)
                        invalid[field_name] = invalid_value
                        with self.assertRaises(ValidationError):
                            model_type.model_validate(invalid)
            with self.subTest(model=model_type.__name__, extra=True):
                with self.assertRaises(ValidationError):
                    model_type.model_validate(payload | {"extra": "forbidden"})
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        malformed_outcomes = success_outcomes(plan)
        malformed = CodexRemovalConfirmed.model_construct(
            step="REMOVE_PLUGIN",
            status="CONFIRMED",
        )
        self.assert_blocked(
            reduce_compensation(plan, replace_outcome(malformed_outcomes, 0, malformed)),
            CodexCompensationBlockReason.OUTCOME_INVALID,
        )

    def test_b4_truth_table_clears_only_current_authority_proved_absent(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        baseline = success_outcomes(plan)
        for installed_truth in CodexProofTruth:
            for available_truth in CodexProofTruth:
                with self.subTest(installed=installed_truth, available=available_truth):
                    candidate = replace_outcome(
                        baseline,
                        2,
                        CodexPluginListsProof(
                            step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                            installed=installed_truth,
                            available=available_truth,
                        ),
                    )
                    result = reduce_compensation(plan, candidate)
                    if (
                        installed_truth is CodexProofTruth.PROVED_ABSENT
                        and available_truth is CodexProofTruth.PROVED_ABSENT
                    ):
                        self.assert_compensated(result)
                    else:
                        if not isinstance(result, CodexCompensationFailed):
                            raise AssertionError(f"expected failed result, received {result}")
                        self.assertEqual((CodexAttemptEffect.PLUGIN,), result.remaining_authority)
        for truth in CodexProofTruth:
            with self.subTest(installed_location=truth):
                candidate = replace_outcome(
                    baseline,
                    4,
                    CodexInstalledLocationProof(
                        step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                        truth=truth,
                    ),
                )
                result = reduce_compensation(plan, candidate)
                if truth is CodexProofTruth.PROVED_ABSENT:
                    self.assert_compensated(result)
                else:
                    if not isinstance(result, CodexCompensationFailed):
                        raise AssertionError(f"expected failed result, received {result}")
                    self.assertEqual((CodexAttemptEffect.PLUGIN,), result.remaining_authority)
        for truth in CodexProofTruth:
            with self.subTest(marketplace=truth):
                candidate = replace_outcome(
                    baseline,
                    3,
                    CodexMarketplaceProof(
                        step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                        truth=truth,
                    ),
                )
                result = reduce_compensation(plan, candidate)
                if truth is CodexProofTruth.PROVED_ABSENT:
                    self.assert_compensated(result)
                else:
                    if not isinstance(result, CodexCompensationFailed):
                        raise AssertionError(f"expected failed result, received {result}")
                    self.assertEqual((CodexAttemptEffect.MARKETPLACE,), result.remaining_authority)
        truth_cases: tuple[tuple[int, CodexCompensationObservation, tuple[CodexAttemptEffect, ...]], ...] = (
            (
                2,
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.RESIDUE,
                    available=CodexProofTruth.PROVED_ABSENT,
                ),
                (CodexAttemptEffect.PLUGIN,),
            ),
            (
                2,
                CodexPluginListsProof(
                    step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                    installed=CodexProofTruth.PROVED_ABSENT,
                    available=CodexProofTruth.UNPROVED,
                ),
                (CodexAttemptEffect.PLUGIN,),
            ),
            (
                4,
                CodexInstalledLocationProof(
                    step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                    truth=CodexProofTruth.MISMATCH,
                ),
                (CodexAttemptEffect.PLUGIN,),
            ),
            (
                3,
                CodexMarketplaceProof(
                    step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                    truth=CodexProofTruth.MALFORMED,
                ),
                (CodexAttemptEffect.MARKETPLACE,),
            ),
        )
        for index, replacement, remaining in truth_cases:
            with self.subTest(index=index, replacement=replacement):
                result = reduce_compensation(plan, replace_outcome(baseline, index, replacement))
                if not isinstance(result, CodexCompensationFailed):
                    raise AssertionError(f"expected failed result, received {result}")
                self.assertEqual(remaining, result.remaining_authority)
        marketplace_only = valid_plan(CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED)
        foreign_plugin_truth = success_outcomes(marketplace_only)
        foreign_plugin_truth = replace_outcome(
            foreign_plugin_truth,
            1,
            CodexPluginListsProof(
                step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                installed=CodexProofTruth.RESIDUE,
                available=CodexProofTruth.RESIDUE,
            ),
        )
        foreign_plugin_truth = replace_outcome(
            foreign_plugin_truth,
            3,
            CodexInstalledLocationProof(
                step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                truth=CodexProofTruth.RESIDUE,
            ),
        )
        self.assert_compensated(reduce_compensation(marketplace_only, foreign_plugin_truth))

    def test_b5_frozen_results_ordered_unique_reasons_and_metadata_only_serialization(self) -> None:
        noop_plan = valid_plan(CodexAttemptEffectState.NOT_ATTEMPTED, CodexAttemptEffectState.NOT_ATTEMPTED)
        noop = reduce_compensation(noop_plan, ())
        self.assertIsInstance(noop, CodexCompensationNoop)
        self.assertEqual("COMPENSATION_NOT_REQUIRED", noop.status)
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        outcomes = success_outcomes(plan)
        outcomes = replace_outcome(
            outcomes,
            0,
            CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
        )
        outcomes = replace_outcome(
            outcomes,
            1,
            CodexRemovalFailed(step=CodexCompensationStep.REMOVE_MARKETPLACE, status="DECLARED_FAILURE"),
        )
        outcomes = replace_outcome(
            outcomes,
            2,
            CodexPluginListsProof(
                step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                installed=CodexProofTruth.RESIDUE,
                available=CodexProofTruth.UNPROVED,
            ),
        )
        outcomes = replace_outcome(
            outcomes,
            4,
            CodexInstalledLocationProof(
                step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                truth=CodexProofTruth.MISMATCH,
            ),
        )
        outcomes = replace_outcome(
            outcomes,
            3,
            CodexMarketplaceProof(
                step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                truth=CodexProofTruth.MALFORMED,
            ),
        )
        result = reduce_compensation(plan, outcomes)
        self.assert_failed(
            result,
            (
                CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE,
                CodexCompensationReason.MARKETPLACE_REMOVAL_DECLARED_FAILURE,
                CodexCompensationReason.PLUGIN_INSTALLED_RESIDUE,
                CodexCompensationReason.PLUGIN_AVAILABLE_UNPROVED,
                CodexCompensationReason.MARKETPLACE_MALFORMED,
                CodexCompensationReason.INSTALLED_LOCATION_MISMATCH,
            ),
            (CodexAttemptEffect.PLUGIN, CodexAttemptEffect.MARKETPLACE),
        )
        if not isinstance(result, CodexCompensationFailed):
            raise AssertionError(f"expected failed result, received {result}")
        serialized = result.model_dump_json(warnings=False)
        self.assertEqual(len(result.reasons), len(set(result.reasons)))
        for forbidden in ("command", "stdout", "stderr", "exception", "C:\\", "http"):
            self.assertNotIn(forbidden, serialized.casefold())
        self.assert_compensated(reduce_compensation(plan, success_outcomes(plan)))

    def test_r1_exact_plan_order_is_frozen_for_every_reachable_authority_pair(self) -> None:
        proof_steps = (
            CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
            CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
            CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
        )
        expected_plans: tuple[
            tuple[CodexAttemptEffectState, CodexAttemptEffectState, tuple[CodexCompensationStep, ...]], ...
        ] = (
            (CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexCompensationStep.REMOVE_MARKETPLACE,) + proof_steps),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED, (CodexCompensationStep.REMOVE_MARKETPLACE,) + proof_steps),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST, (CodexCompensationStep.REMOVE_PLUGIN, CodexCompensationStep.REMOVE_MARKETPLACE) + proof_steps),
            (CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED, (CodexCompensationStep.REMOVE_PLUGIN, CodexCompensationStep.REMOVE_MARKETPLACE) + proof_steps),
        )
        for marketplace_state, plugin_state, expected_steps in expected_plans:
            with self.subTest(marketplace=marketplace_state, plugin=plugin_state):
                self.assertEqual(expected_steps, valid_plan(marketplace_state, plugin_state).steps)

    def test_r2_completed_results_carry_exact_residual_journal_and_distinguish_authority(self) -> None:
        may_plan = valid_plan(CodexAttemptEffectState.MAY_EXIST, CodexAttemptEffectState.NOT_ATTEMPTED)
        may_outcomes = replace_outcome(
            success_outcomes(may_plan),
            2,
            CodexMarketplaceProof(
                step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                truth=CodexProofTruth.RESIDUE,
            ),
        )
        may_result = reduce_compensation(may_plan, may_outcomes)
        self.assert_failed(
            may_result,
            (CodexCompensationReason.MARKETPLACE_RESIDUE,),
            (CodexAttemptEffect.MARKETPLACE,),
        )
        self.assert_residual(
            may_result,
            CodexAttemptEffectState.MAY_EXIST,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )
        owned_plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.NOT_ATTEMPTED)
        owned_outcomes = replace_outcome(
            success_outcomes(owned_plan),
            2,
            CodexMarketplaceProof(
                step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                truth=CodexProofTruth.RESIDUE,
            ),
        )
        owned_result = reduce_compensation(owned_plan, owned_outcomes)
        self.assert_failed(
            owned_result,
            (CodexCompensationReason.MARKETPLACE_RESIDUE,),
            (CodexAttemptEffect.MARKETPLACE,),
        )
        self.assert_residual(
            owned_result,
            CodexAttemptEffectState.OWNED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )
        self.assertNotEqual(may_result.model_dump_json(warnings=False), owned_result.model_dump_json(warnings=False))
        with self.assertRaises(ValidationError):
            CodexCompensationFailed.model_validate(
                {
                    "status": "COMPENSATION_FAILED",
                    "reasons": (CodexCompensationReason.MARKETPLACE_RESIDUE,),
                    "remaining_authority": (CodexAttemptEffect.MARKETPLACE,),
                }
            )
        completed_plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        completed_result = reduce_compensation(completed_plan, success_outcomes(completed_plan))
        self.assert_compensated(completed_result)
        self.assert_residual(
            completed_result,
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )
        preexisting_plan = valid_plan(CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED)
        preexisting_result = reduce_compensation(preexisting_plan, ())
        self.assertIsInstance(preexisting_result, CodexCompensationNoop)
        self.assert_residual(
            preexisting_result,
            CodexAttemptEffectState.PREEXISTING,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )

    def test_r2_cross_attempt_substituted_state_and_stale_plan_block_finitely(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST)
        other_request = CodexPreflightRequest(
            installation_id=INSTALLATION,
            root=ROOT,
            marketplace=CodexMarketplaceName(value="other-market"),
            plugin=PLUGIN,
            marketplace_source=OwnedRelativePath(value="marketplaces/other-market"),
        )
        cross_request_plan = CodexCompensationPlan.model_construct(
            journal=plan.journal,
            request=other_request,
            attempt_id=ATTEMPT,
            identity=plan.identity,
            status="COMPENSATION_REQUIRED",
            steps=plan.steps,
        )
        self.assertIsInstance(reduce_compensation(cross_request_plan, success_outcomes(plan)), CodexCompensationBlocked)
        replay_plan = CodexCompensationPlan.model_construct(
            journal=plan.journal,
            request=plan.request,
            attempt_id=CodexRegistrationAttemptId(value="attempt-fedcba9876543210"),
            identity=plan.identity,
            status="COMPENSATION_REQUIRED",
            steps=plan.steps,
        )
        self.assertIsInstance(reduce_compensation(replay_plan, success_outcomes(plan)), CodexCompensationBlocked)
        substituted_state_plan = CodexCompensationPlan.model_construct(
            journal=journal(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED),
            request=plan.request,
            attempt_id=plan.attempt_id,
            identity=plan.identity,
            status="COMPENSATION_REQUIRED",
            steps=plan.steps,
        )
        self.assert_blocked(
            reduce_compensation(substituted_state_plan, success_outcomes(plan)),
            CodexCompensationBlockReason.PLAN_INVALID,
        )
        stale_plan = CodexCompensationPlan.model_construct(
            journal=plan.journal,
            request=plan.request,
            attempt_id=plan.attempt_id,
            identity=plan.identity,
            status="COMPENSATION_REQUIRED",
            steps=(
                CodexCompensationStep.REMOVE_PLUGIN,
                CodexCompensationStep.REMOVE_MARKETPLACE,
                CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
                CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
            ),
        )
        self.assert_blocked(
            reduce_compensation(stale_plan, success_outcomes(plan)),
            CodexCompensationBlockReason.PLAN_INVALID,
        )

    def test_r3_wrong_plan_metaclass_equality_traps_block_without_equality(self) -> None:
        exception_types: tuple[type[BaseException], ...] = (
            RuntimeError,
            MemoryError,
            KeyboardInterrupt,
            SystemExit,
        )
        for exception_type in exception_types:
            with self.subTest(exception=exception_type.__name__):
                class EqualityTrapMeta(type):
                    def __eq__(cls, other: object) -> bool:
                        raise exception_type()

                class EqualityTrapPlan(metaclass=EqualityTrapMeta):
                    pass

                trapped_plan = cast(CodexCompensationPlan, EqualityTrapPlan())
                self.assert_blocked(
                    reduce_compensation(trapped_plan, ()),
                    CodexCompensationBlockReason.PLAN_INVALID,
                )

    def test_r4_preexisting_authority_never_schedules_removal(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.PREEXISTING, CodexAttemptEffectState.NOT_ATTEMPTED)
        self.assertEqual((), plan.steps)
        result = reduce_compensation(plan, ())
        self.assertIsInstance(result, CodexCompensationNoop)
        self.assert_residual(
            result,
            CodexAttemptEffectState.PREEXISTING,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )

    def test_r4_complete_after_declared_failure_reduces_later_proofs(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.OWNED)
        outcomes = replace_outcome(
            success_outcomes(plan),
            0,
            CodexRemovalFailed(step=CodexCompensationStep.REMOVE_PLUGIN, status="DECLARED_FAILURE"),
        )
        result = reduce_compensation(plan, outcomes)
        self.assert_failed(
            result,
            (CodexCompensationReason.PLUGIN_REMOVAL_DECLARED_FAILURE,),
            (),
        )
        self.assert_residual(
            result,
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )

    def test_r4_early_plugin_clear_requires_every_fresh_plugin_proof(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST)
        outcomes = replace_outcome(
            success_outcomes(plan),
            4,
            CodexInstalledLocationProof(
                step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
                truth=CodexProofTruth.RESIDUE,
            ),
        )
        result = reduce_compensation(plan, outcomes)
        self.assertIsInstance(result, CodexCompensationFailed)
        self.assert_residual(
            result,
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.MAY_EXIST,
        )

    def test_r4_stale_authority_clears_only_after_exact_fresh_absence(self) -> None:
        plan = valid_plan(CodexAttemptEffectState.OWNED, CodexAttemptEffectState.MAY_EXIST)
        result = reduce_compensation(plan, success_outcomes(plan))
        self.assert_compensated(result)
        self.assert_residual(
            result,
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        )

    def assert_blocked(
        self,
        result: CodexCompensationPlan | CodexNoCompensationPlan | CodexCompensationResult,
        reason: CodexCompensationBlockReason,
    ) -> None:
        if not isinstance(result, CodexCompensationBlocked):
            raise AssertionError(f"expected blocked result, received {result}")
        self.assertIs(reason, result.reason)
        self.assertEqual("COMPENSATION_BLOCKED", result.status)

    def assert_compensated(self, result: CodexCompensationResult) -> None:
        if not isinstance(result, CodexCompensated):
            raise AssertionError(f"expected compensated result, received {result}")
        self.assertEqual("COMPENSATED", result.status)
        self.assertEqual((), result.reasons)
        self.assertEqual((), result.remaining_authority)

    def assert_failed(
        self,
        result: CodexCompensationResult,
        expected_reasons: tuple[CodexCompensationReason, ...],
        expected_remaining: tuple[CodexAttemptEffect, ...],
    ) -> None:
        if not isinstance(result, CodexCompensationFailed):
            raise AssertionError(f"expected failed result, received {result}")
        self.assertEqual("COMPENSATION_FAILED", result.status)
        self.assertEqual(expected_reasons, result.reasons)
        self.assertEqual(expected_remaining, result.remaining_authority)

    def assert_residual(
        self,
        result: CodexCompensationResult,
        marketplace_state: CodexAttemptEffectState,
        plugin_state: CodexAttemptEffectState,
    ) -> None:
        if isinstance(result, CodexCompensationBlocked):
            raise AssertionError(f"expected completed result, received {result}")
        residual = result.residual_journal
        self.assertEqual(request(), residual.request)
        self.assertEqual(ATTEMPT, residual.attempt_id)
        self.assertIs(marketplace_state, residual.marketplace_state)
        self.assertIs(plugin_state, residual.plugin_state)


if __name__ == "__main__":
    unittest.main()
