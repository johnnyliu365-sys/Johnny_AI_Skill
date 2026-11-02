from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from library.local_orchestration.predictive_context_boundary import (
    BoundaryDecision,
    ContextBudgetAssessmentRequest,
    ContextBudgetAssessmentResult,
    ContextBudgetGuard,
    ContextCapacityObservation,
    ExpectedReturnBudget,
    NextUnitEstimate,
)
from library.local_orchestration.predictive_context_cli import main as cli_main


def make_observation(
    *,
    available: bool = True,
    used_context_tokens: int | None = 100,
    effective_host_capacity_tokens: int | None = 2_000,
    context_epoch: str | None = "epoch-2026-11-03",
    observation_ref: str | None = "observation-current",
) -> ContextCapacityObservation:
    return ContextCapacityObservation(
        available=available,
        used_context_tokens=used_context_tokens,
        effective_host_capacity_tokens=effective_host_capacity_tokens,
        context_epoch=context_epoch,
        observation_ref=observation_ref,
    )


def make_estimate(
    *,
    unit_ref: str = "unit-next",
    kind: str = "CONSERVATIVE",
    estimated_tokens: int = 200,
    evidence_ref: str = "estimate-evidence",
    sample_count: int | None = None,
) -> NextUnitEstimate:
    return NextUnitEstimate(
        unit_ref=unit_ref,
        kind=kind,
        estimated_tokens=estimated_tokens,
        evidence_ref=evidence_ref,
        sample_count=sample_count,
    )


def make_return(
    *,
    return_ref: str = "return-next",
    producer_ref: str = "producer-worker",
    dispatch_budget_ref: str = "budget-next",
    state: str = "EXPECTED",
    expected_accepted_tokens: int = 100,
    priority: str = "SUCCESS",
) -> ExpectedReturnBudget:
    return ExpectedReturnBudget(
        return_ref=return_ref,
        producer_ref=producer_ref,
        dispatch_budget_ref=dispatch_budget_ref,
        state=state,
        expected_accepted_tokens=expected_accepted_tokens,
        priority=priority,
    )


def make_request(
    *,
    ticket_ref: str = "ticket-current",
    context_ticket_ref: str = "ticket-current",
    unit_ref: str = "unit-next",
    phase: str = "PRE_UNIT",
    unit_kind: str = "TEST",
    execution_state: str = "NOT_STARTED",
    expected_context_epoch: str = "epoch-2026-11-03",
    observation: ContextCapacityObservation | None = None,
    estimate: NextUnitEstimate | None = None,
    dispatch_overhead_tokens: int = 20,
    review_reserve_tokens: int = 30,
    pending_returns: tuple[ExpectedReturnBudget, ...] = (),
) -> ContextBudgetAssessmentRequest:
    return ContextBudgetAssessmentRequest(
        schema_version="1",
        advisory_only=True,
        ticket_ref=ticket_ref,
        context_ticket_ref=context_ticket_ref,
        unit_ref=unit_ref,
        phase=phase,
        unit_kind=unit_kind,
        execution_state=execution_state,
        expected_context_epoch=expected_context_epoch,
        observation=observation if observation is not None else make_observation(),
        estimate=estimate if estimate is not None else make_estimate(unit_ref=unit_ref),
        dispatch_overhead_tokens=dispatch_overhead_tokens,
        review_reserve_tokens=review_reserve_tokens,
        pending_returns=pending_returns,
    )


def assess(request: ContextBudgetAssessmentRequest) -> ContextBudgetAssessmentResult:
    return ContextBudgetGuard().assess(request)


def invoke_cli(payload: bytes, arguments: tuple[str, ...] = ()) -> tuple[int, str]:
    source = io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8")
    output = io.StringIO()
    with (
        patch("sys.stdin", source),
        patch("sys.stdout", output),
        patch("sys.argv", ["predictive_context_cli", *arguments]),
    ):
        exit_code = cli_main()
    return exit_code, output.getvalue()


def test_boundary_decision_has_exact_finite_values() -> None:
    assert {decision.value for decision in BoundaryDecision} == {
        "EXECUTE_WITHOUT_COMPACTION",
        "CHECKPOINT_COMPACT_REVERIFY",
        "FRESH_CONTEXT_REQUIRED",
        "SERIAL_DECOMPOSITION_REQUIRED",
        "DEFER_UNTIL_UNIT_BOUNDARY",
        "OBSERVATION_UNAVAILABLE",
        "CONTEXT_EPOCH_MISMATCH",
        "UNIT_ESTIMATE_MISMATCH",
        "RETURN_SCHEDULE_REQUIRED",
        "INVALID_REQUEST",
    }


def test_observation_available_and_unavailable_round_trip() -> None:
    available = make_observation()
    unavailable = make_observation(
        available=False,
        used_context_tokens=None,
        effective_host_capacity_tokens=None,
        context_epoch=None,
        observation_ref=None,
    )
    assert ContextCapacityObservation.model_validate_json(available.model_dump_json()) == available
    assert ContextCapacityObservation.model_validate_json(unavailable.model_dump_json()) == unavailable


@pytest.mark.parametrize(
    "values",
    (
        {"available": True, "used_context_tokens": None},
        {"available": False, "used_context_tokens": 0},
        {"effective_host_capacity_tokens": 0},
        {"used_context_tokens": True},
        {"observation_ref": "x"},
    ),
)
def test_observation_rejects_incomplete_or_coerced_facts(values: dict[str, object]) -> None:
    raw: dict[str, object] = make_observation().model_dump()
    raw.update(values)
    with pytest.raises(ValidationError):
        ContextCapacityObservation.model_validate(raw)


@pytest.mark.parametrize(
    ("kind", "sample_count"),
    (("CONSERVATIVE", None), ("P90", 10), ("P95", 20)),
)
def test_estimate_variants_round_trip(kind: str, sample_count: int | None) -> None:
    estimate = make_estimate(kind=kind, sample_count=sample_count)
    assert NextUnitEstimate.model_validate_json(estimate.model_dump_json()) == estimate


@pytest.mark.parametrize(
    "values",
    (
        {"kind": "P90", "sample_count": None},
        {"kind": "CONSERVATIVE", "sample_count": 4},
        {"kind": "P95", "sample_count": 0},
        {"estimated_tokens": 0},
        {"estimated_tokens": 2.5},
    ),
)
def test_estimate_rejects_invalid_shape_and_primitives(values: dict[str, object]) -> None:
    raw: dict[str, object] = make_estimate().model_dump()
    raw.update(values)
    with pytest.raises(ValidationError):
        NextUnitEstimate.model_validate(raw)


@pytest.mark.parametrize("state", ("EXPECTED", "RECEIVED_UNACKNOWLEDGED"))
@pytest.mark.parametrize("priority", ("ALERT", "SUCCESS"))
def test_return_budget_state_and_priority_round_trip(state: str, priority: str) -> None:
    item = make_return(state=state, priority=priority)
    assert ExpectedReturnBudget.model_validate_json(item.model_dump_json()) == item


def test_request_round_trip_covers_all_finite_unit_phase_and_execution_states() -> None:
    for unit_kind in ("SQL", "GIT", "TEST", "OTHER"):
        for phase in ("PRE_UNIT", "POST_COMPACTION_REVERIFY"):
            for execution_state in ("NOT_STARTED", "RUNNING"):
                request = make_request(
                    unit_kind=unit_kind,
                    phase=phase,
                    execution_state=execution_state,
                )
                restored = ContextBudgetAssessmentRequest.model_validate_json(
                    request.model_dump_json()
                )
                assert restored == request


def test_request_rejects_bad_refs_extra_fields_and_primitive_coercion() -> None:
    raw: dict[str, object] = make_request().model_dump()
    raw["unexpected"] = "raw transcript"
    with pytest.raises(ValidationError):
        ContextBudgetAssessmentRequest.model_validate(raw)

    for field_name, value in (
        ("schema_version", "2"),
        ("advisory_only", False),
        ("ticket_ref", "bad/ref"),
        ("dispatch_overhead_tokens", True),
        ("review_reserve_tokens", -1),
    ):
        invalid: dict[str, object] = make_request().model_dump()
        invalid[field_name] = value
        with pytest.raises(ValidationError):
            ContextBudgetAssessmentRequest.model_validate(invalid)


def test_advisory_only_rejects_numeric_truthy_values_for_request_and_result() -> None:
    request = make_request()
    result = ContextBudgetAssessmentResult(
        schema_version="1",
        advisory_only=True,
        ticket_ref="ticket-current",
        unit_ref="unit-next",
        decision=BoundaryDecision.EXECUTE_WITHOUT_COMPACTION,
        projected_tokens=350,
        next_return_refs=(),
    )
    for model_type, raw in (
        (ContextBudgetAssessmentRequest, request.model_dump()),
        (ContextBudgetAssessmentResult, result.model_dump()),
    ):
        assert model_type.model_validate(raw).advisory_only is True
        assert model_type.model_validate_json(json.dumps(raw)).advisory_only is True
        for numeric_truthy in (1, 1.0):
            invalid: dict[str, object] = dict(raw)
            invalid["advisory_only"] = numeric_truthy
            with pytest.raises(ValidationError):
                model_type.model_validate(invalid)
            with pytest.raises(ValidationError):
                model_type.model_validate_json(json.dumps(invalid))


def test_request_rejects_duplicate_return_and_dispatch_budget_refs() -> None:
    first = make_return(return_ref="return-first", dispatch_budget_ref="budget-first")
    duplicate_return = make_return(return_ref="return-first", dispatch_budget_ref="budget-second")
    duplicate_budget = make_return(return_ref="return-second", dispatch_budget_ref="budget-first")
    assert make_request(pending_returns=(first, make_return(producer_ref="producer-worker-2"))).pending_returns
    for pending in ((first, duplicate_return), (first, duplicate_budget)):
        with pytest.raises(ValidationError):
            make_request(pending_returns=pending)


def test_request_rejects_success_before_alert_and_accepts_alert_first() -> None:
    alert = make_return(
        return_ref="return-alert",
        dispatch_budget_ref="budget-alert",
        priority="ALERT",
    )
    success = make_return(
        return_ref="return-success",
        dispatch_budget_ref="budget-success",
    )
    with pytest.raises(ValidationError):
        make_request(pending_returns=(success, alert))
    assert make_request(pending_returns=(alert, success)).pending_returns == (alert, success)


def test_result_constructor_and_json_round_trip_cover_all_decisions() -> None:
    early = {
        BoundaryDecision.FRESH_CONTEXT_REQUIRED,
        BoundaryDecision.UNIT_ESTIMATE_MISMATCH,
        BoundaryDecision.OBSERVATION_UNAVAILABLE,
        BoundaryDecision.CONTEXT_EPOCH_MISMATCH,
        BoundaryDecision.DEFER_UNTIL_UNIT_BOUNDARY,
    }
    for decision in BoundaryDecision:
        invalid = decision is BoundaryDecision.INVALID_REQUEST
        scheduled = decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
        result = ContextBudgetAssessmentResult(
            schema_version="1",
            advisory_only=True,
            ticket_ref=None if invalid else "ticket-current",
            unit_ref=None if invalid else "unit-next",
            decision=decision,
            projected_tokens=None if invalid or decision in early else 100,
            next_return_refs=("return-next",) if scheduled else (),
        )
        assert ContextBudgetAssessmentResult.model_validate_json(result.model_dump_json()) == result


def test_result_rejects_inconsistent_nullability_projection_and_schedule() -> None:
    base: dict[str, object] = {
        "schema_version": "1",
        "advisory_only": True,
        "ticket_ref": "ticket-current",
        "unit_ref": "unit-next",
        "decision": BoundaryDecision.EXECUTE_WITHOUT_COMPACTION,
        "projected_tokens": 100,
        "next_return_refs": (),
    }
    for changes in (
        {"ticket_ref": None},
        {"decision": BoundaryDecision.INVALID_REQUEST},
        {"decision": BoundaryDecision.RETURN_SCHEDULE_REQUIRED},
        {"next_return_refs": ("return-next",)},
        {"decision": BoundaryDecision.FRESH_CONTEXT_REQUIRED},
    ):
        invalid = dict(base)
        invalid.update(changes)
        with pytest.raises(ValidationError):
            ContextBudgetAssessmentResult.model_validate(invalid)

    bad_invalid: dict[str, object] = dict(base)
    bad_invalid.update(
        {
            "ticket_ref": None,
            "unit_ref": None,
            "decision": BoundaryDecision.INVALID_REQUEST,
        }
    )
    with pytest.raises(ValidationError):
        ContextBudgetAssessmentResult.model_validate(bad_invalid)


def test_guard_is_constructible_without_state() -> None:
    assert type(ContextBudgetGuard()) is ContextBudgetGuard
    assert ContextBudgetGuard() is not ContextBudgetGuard()


def test_guard_assess_accepts_only_positional_request_argument() -> None:
    with pytest.raises(TypeError):
        ContextBudgetGuard().assess(request=make_request())
    assert assess(make_request()).decision is BoundaryDecision.EXECUTE_WITHOUT_COMPACTION


def test_safe_projection_includes_observed_usage_dispatch_and_review_reserve() -> None:
    request = make_request(
        observation=make_observation(used_context_tokens=100, effective_host_capacity_tokens=351),
        estimate=make_estimate(estimated_tokens=200),
        dispatch_overhead_tokens=20,
        review_reserve_tokens=30,
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.EXECUTE_WITHOUT_COMPACTION
    assert result.projected_tokens == 350
    assert result.next_return_refs == ()


def test_exact_capacity_requires_pre_unit_checkpoint() -> None:
    request = make_request(
        observation=make_observation(used_context_tokens=100, effective_host_capacity_tokens=350),
        estimate=make_estimate(estimated_tokens=200),
        dispatch_overhead_tokens=20,
        review_reserve_tokens=30,
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.CHECKPOINT_COMPACT_REVERIFY
    assert result.projected_tokens == 350


@pytest.mark.parametrize("unit_kind", ("SQL", "GIT", "TEST", "OTHER"))
def test_running_unit_defers_until_boundary_for_every_unit_kind(unit_kind: str) -> None:
    result = assess(make_request(unit_kind=unit_kind, execution_state="RUNNING"))
    assert result.decision is BoundaryDecision.DEFER_UNTIL_UNIT_BOUNDARY
    assert result.projected_tokens is None


def test_changed_context_ticket_requires_fresh_context_before_projection() -> None:
    result = assess(make_request(ticket_ref="ticket-child", context_ticket_ref="ticket-parent"))
    assert result.decision is BoundaryDecision.FRESH_CONTEXT_REQUIRED
    assert result.projected_tokens is None


def test_early_decision_precedence_is_running_ticket_unit_observation_epoch() -> None:
    unavailable = make_observation(
        available=False,
        used_context_tokens=None,
        effective_host_capacity_tokens=None,
        context_epoch=None,
        observation_ref=None,
    )
    conflicting = make_request(
        execution_state="RUNNING",
        ticket_ref="ticket-child",
        context_ticket_ref="ticket-parent",
        estimate=make_estimate(unit_ref="unit-other"),
        observation=unavailable,
    )
    assert assess(conflicting).decision is BoundaryDecision.DEFER_UNTIL_UNIT_BOUNDARY

    changed_ticket = make_request(
        ticket_ref="ticket-child",
        context_ticket_ref="ticket-parent",
        estimate=make_estimate(unit_ref="unit-other"),
        observation=unavailable,
    )
    assert assess(changed_ticket).decision is BoundaryDecision.FRESH_CONTEXT_REQUIRED

    wrong_unit = make_request(
        estimate=make_estimate(unit_ref="unit-other"),
        observation=unavailable,
    )
    assert assess(wrong_unit).decision is BoundaryDecision.UNIT_ESTIMATE_MISMATCH


def test_wrong_estimate_unit_is_rejected_before_projection() -> None:
    result = assess(make_request(estimate=make_estimate(unit_ref="unit-other")))
    assert result.decision is BoundaryDecision.UNIT_ESTIMATE_MISMATCH
    assert result.projected_tokens is None


def test_unavailable_observation_remains_unknown_before_epoch_comparison() -> None:
    result = assess(
        make_request(
            expected_context_epoch="epoch-newer",
            observation=make_observation(
                available=False,
                used_context_tokens=None,
                effective_host_capacity_tokens=None,
                context_epoch=None,
                observation_ref=None,
            ),
        )
    )
    assert result.decision is BoundaryDecision.OBSERVATION_UNAVAILABLE
    assert result.projected_tokens is None


def test_wrong_context_epoch_refuses_projection() -> None:
    result = assess(
        make_request(
            expected_context_epoch="epoch-expected",
            observation=make_observation(context_epoch="epoch-observed"),
        )
    )
    assert result.decision is BoundaryDecision.CONTEXT_EPOCH_MISMATCH
    assert result.projected_tokens is None


def test_guard_revalidates_bypassed_nested_input_and_returns_unidentified_invalid() -> None:
    valid = make_request()
    raw: dict[str, object] = valid.model_dump()
    raw["dispatch_overhead_tokens"] = True
    unsafe = ContextBudgetAssessmentRequest.model_construct(**raw)
    result = assess(unsafe)
    assert result.decision is BoundaryDecision.INVALID_REQUEST
    assert result.ticket_ref is None and result.unit_ref is None
    assert result.projected_tokens is None and result.next_return_refs == ()

    malformed_observation = ContextCapacityObservation.model_construct(
        available=True,
        used_context_tokens=None,
        effective_host_capacity_tokens=2_000,
        context_epoch="epoch-2026-11-03",
        observation_ref="observation-current",
    )
    nested_raw: dict[str, object] = valid.model_dump()
    nested_raw["observation"] = malformed_observation
    unsafe_nested = ContextBudgetAssessmentRequest.model_construct(**nested_raw)
    assert assess(unsafe_nested).decision is BoundaryDecision.INVALID_REQUEST


def test_pre_unit_overflow_can_compact_when_fresh_window_fits() -> None:
    result = assess(
        make_request(
            observation=make_observation(used_context_tokens=1_800, effective_host_capacity_tokens=2_000)
        )
    )
    assert result.decision is BoundaryDecision.CHECKPOINT_COMPACT_REVERIFY
    assert result.projected_tokens == 2_050


def test_post_compaction_overflow_requires_serial_decomposition_without_another_loop() -> None:
    result = assess(
        make_request(
            phase="POST_COMPACTION_REVERIFY",
            observation=make_observation(used_context_tokens=1_800, effective_host_capacity_tokens=2_000),
        )
    )
    assert result.decision is BoundaryDecision.SERIAL_DECOMPOSITION_REQUIRED
    assert result.projected_tokens == 2_050


def test_fresh_dispatch_estimate_and_review_that_cannot_fit_requires_serial_work() -> None:
    result = assess(
        make_request(
            observation=make_observation(used_context_tokens=0, effective_host_capacity_tokens=250),
            estimate=make_estimate(estimated_tokens=200),
            dispatch_overhead_tokens=20,
            review_reserve_tokens=30,
        )
    )
    assert result.decision is BoundaryDecision.SERIAL_DECOMPOSITION_REQUIRED
    assert result.projected_tokens == 250


def test_all_success_returns_that_fit_do_not_require_a_schedule() -> None:
    request = make_request(
        pending_returns=(
            make_return(return_ref="return-first", dispatch_budget_ref="budget-first", expected_accepted_tokens=100),
            make_return(return_ref="return-second", dispatch_budget_ref="budget-second", expected_accepted_tokens=150),
        )
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.EXECUTE_WITHOUT_COMPACTION
    assert result.projected_tokens == 600
    assert result.next_return_refs == ()


def test_return_window_selects_only_maximal_feasible_ordered_prefix_at_strict_capacity() -> None:
    request = make_request(
        observation=make_observation(used_context_tokens=100, effective_host_capacity_tokens=650),
        pending_returns=(
            make_return(return_ref="return-first", dispatch_budget_ref="budget-first", expected_accepted_tokens=200),
            make_return(return_ref="return-second", dispatch_budget_ref="budget-second", expected_accepted_tokens=100),
            make_return(return_ref="return-third", dispatch_budget_ref="budget-third", expected_accepted_tokens=10),
        ),
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
    assert result.projected_tokens == 550
    assert result.next_return_refs == ("return-first",)


def test_alerts_are_ordered_ahead_of_success_even_when_success_also_fits() -> None:
    request = make_request(
        observation=make_observation(used_context_tokens=100, effective_host_capacity_tokens=600),
        pending_returns=(
            make_return(
                return_ref="alert-first",
                dispatch_budget_ref="budget-alert-first",
                expected_accepted_tokens=100,
                priority="ALERT",
            ),
            make_return(
                return_ref="alert-second",
                dispatch_budget_ref="budget-alert-second",
                expected_accepted_tokens=150,
                priority="ALERT",
            ),
            make_return(return_ref="success-first", dispatch_budget_ref="budget-success-first", expected_accepted_tokens=20),
            make_return(return_ref="success-second", dispatch_budget_ref="budget-success-second", expected_accepted_tokens=20),
        ),
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
    assert result.projected_tokens == 450
    assert result.next_return_refs == ("alert-first",)


def test_unacknowledged_success_is_selected_before_later_returns_even_when_all_fit() -> None:
    request = make_request(
        observation=make_observation(used_context_tokens=200, effective_host_capacity_tokens=500),
        estimate=make_estimate(estimated_tokens=100),
        pending_returns=(
            make_return(
                return_ref="return-received",
                dispatch_budget_ref="budget-received",
                state="RECEIVED_UNACKNOWLEDGED",
                expected_accepted_tokens=200,
            ),
            make_return(
                return_ref="return-expected",
                dispatch_budget_ref="budget-expected",
                expected_accepted_tokens=100,
            ),
        ),
    )
    first = assess(request)
    second = assess(request)
    assert 350 + request.pending_returns[1].expected_accepted_tokens < 500
    assert first.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
    assert first.next_return_refs == ("return-received",)
    assert first.projected_tokens == 350
    assert first == second
    assert request.pending_returns[0].state == "RECEIVED_UNACKNOWLEDGED"


def test_first_unacknowledged_success_precedes_later_expected_and_is_not_auto_acknowledged() -> None:
    unacknowledged = make_return(
        return_ref="return-unacknowledged",
        dispatch_budget_ref="budget-unacknowledged",
        state="RECEIVED_UNACKNOWLEDGED",
        expected_accepted_tokens=200,
    )
    expected = make_return(
        return_ref="return-later",
        dispatch_budget_ref="budget-later",
        expected_accepted_tokens=100,
    )
    request = make_request(
        observation=make_observation(used_context_tokens=200, effective_host_capacity_tokens=430),
        estimate=make_estimate(estimated_tokens=100),
        pending_returns=(unacknowledged, expected),
    )
    first = assess(request)
    assert first.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
    assert first.projected_tokens == 350
    assert first.next_return_refs == ("return-unacknowledged",)
    assert assess(request) == first

    acknowledged_by_caller = make_request(
        observation=request.observation,
        estimate=request.estimate,
        pending_returns=(expected,),
    )
    progressed = assess(acknowledged_by_caller)
    assert progressed.decision is BoundaryDecision.CHECKPOINT_COMPACT_REVERIFY
    assert progressed.next_return_refs == ()


def test_unacknowledged_success_precedes_earlier_expected_when_window_is_tight() -> None:
    expected = make_return(
        return_ref="return-earlier-expected",
        dispatch_budget_ref="budget-earlier-expected",
        expected_accepted_tokens=100,
    )
    unacknowledged = make_return(
        return_ref="return-later-unacknowledged",
        dispatch_budget_ref="budget-later-unacknowledged",
        state="RECEIVED_UNACKNOWLEDGED",
        expected_accepted_tokens=100,
    )
    request = make_request(
        observation=make_observation(used_context_tokens=200, effective_host_capacity_tokens=430),
        estimate=make_estimate(estimated_tokens=100),
        pending_returns=(expected, unacknowledged),
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
    assert result.projected_tokens == 350
    assert result.next_return_refs == ("return-later-unacknowledged",)
    assert request.pending_returns[1].state == "RECEIVED_UNACKNOWLEDGED"


def test_alert_selection_keeps_unacknowledged_success_pending() -> None:
    unacknowledged_success = make_return(
        return_ref="return-unacknowledged-success",
        dispatch_budget_ref="budget-unacknowledged-success",
        state="RECEIVED_UNACKNOWLEDGED",
        expected_accepted_tokens=200,
    )
    alert = make_return(
        return_ref="return-alert",
        dispatch_budget_ref="budget-alert",
        expected_accepted_tokens=100,
        priority="ALERT",
    )
    request = make_request(pending_returns=(alert, unacknowledged_success))
    result = assess(request)
    assert result.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED
    assert result.next_return_refs == ("return-alert",)
    assert request.pending_returns[1].state == "RECEIVED_UNACKNOWLEDGED"


def test_no_first_expected_return_fit_compacts_only_when_fresh_fit_is_possible() -> None:
    request = make_request(
        observation=make_observation(used_context_tokens=100, effective_host_capacity_tokens=500),
        estimate=make_estimate(estimated_tokens=200),
        dispatch_overhead_tokens=20,
        review_reserve_tokens=30,
        pending_returns=(
            make_return(return_ref="return-too-large", dispatch_budget_ref="budget-too-large", expected_accepted_tokens=240),
        ),
    )
    result = assess(request)
    assert result.decision is BoundaryDecision.CHECKPOINT_COMPACT_REVERIFY
    assert result.projected_tokens == 590
    assert result.next_return_refs == ()

    post_compaction = make_request(
        observation=request.observation,
        estimate=request.estimate,
        dispatch_overhead_tokens=request.dispatch_overhead_tokens,
        review_reserve_tokens=request.review_reserve_tokens,
        phase="POST_COMPACTION_REVERIFY",
        pending_returns=request.pending_returns,
    )
    assert assess(post_compaction).decision is BoundaryDecision.SERIAL_DECOMPOSITION_REQUIRED


def test_cli_emits_one_advisory_json_result_and_uses_success_exit() -> None:
    request = make_request()
    exit_code, output = invoke_cli(request.model_dump_json().encode("utf-8"))
    result = ContextBudgetAssessmentResult.model_validate_json(output)
    assert exit_code == 0
    assert output.endswith("\n")
    assert result.decision is BoundaryDecision.EXECUTE_WITHOUT_COMPACTION
    assert result.advisory_only is True
    assert result.ticket_ref == request.ticket_ref and result.unit_ref == request.unit_ref


def test_cli_advisory_that_defers_has_nonzero_valid_advice_exit() -> None:
    request = make_request(execution_state="RUNNING")
    exit_code, output = invoke_cli(request.model_dump_json().encode("utf-8"))
    result = ContextBudgetAssessmentResult.model_validate_json(output)
    assert exit_code == 3
    assert result.decision is BoundaryDecision.DEFER_UNTIL_UNIT_BOUNDARY


@pytest.mark.parametrize("payload", (b"", b"{not-json", b"[]"))
def test_cli_malformed_or_wrong_shape_returns_fixed_invalid_result(payload: bytes) -> None:
    exit_code, output = invoke_cli(payload)
    result = ContextBudgetAssessmentResult.model_validate_json(output)
    assert exit_code == 2
    assert result.decision is BoundaryDecision.INVALID_REQUEST
    assert result.ticket_ref is None and result.unit_ref is None


def test_cli_rejects_unknown_fields_including_raw_transcript() -> None:
    raw = json.loads(make_request().model_dump_json())
    assert isinstance(raw, dict)
    raw["raw_transcript"] = "do not retain or interpret this field"
    exit_code, output = invoke_cli(json.dumps(raw).encode("utf-8"))
    result = ContextBudgetAssessmentResult.model_validate_json(output)
    assert exit_code == 2
    assert result.decision is BoundaryDecision.INVALID_REQUEST
    assert result.next_return_refs == ()


def test_cli_rejects_primitive_coercion_and_duplicate_budget_identity() -> None:
    primitive = json.loads(make_request().model_dump_json())
    assert isinstance(primitive, dict)
    primitive["dispatch_overhead_tokens"] = True
    primitive_code, primitive_output = invoke_cli(json.dumps(primitive).encode("utf-8"))
    primitive_result = ContextBudgetAssessmentResult.model_validate_json(primitive_output)
    assert primitive_code == 2
    assert primitive_result.decision is BoundaryDecision.INVALID_REQUEST

    duplicate = json.loads(make_request().model_dump_json())
    assert isinstance(duplicate, dict)
    item = make_return(return_ref="return-other", dispatch_budget_ref="budget-next")
    duplicate["pending_returns"] = [make_return().model_dump(), item.model_dump()]
    duplicate_code, duplicate_output = invoke_cli(json.dumps(duplicate).encode("utf-8"))
    duplicate_result = ContextBudgetAssessmentResult.model_validate_json(duplicate_output)
    assert duplicate_code == 2
    assert duplicate_result.decision is BoundaryDecision.INVALID_REQUEST


def test_cli_accepts_exact_bound_and_rejects_oversized_input() -> None:
    valid = make_request().model_dump_json().encode("utf-8")
    exact_bound = valid + b" " * (65_536 - len(valid))
    assert len(exact_bound) == 65_536
    accepted_code, accepted_output = invoke_cli(exact_bound)
    accepted = ContextBudgetAssessmentResult.model_validate_json(accepted_output)
    assert accepted_code == 0
    assert accepted.decision is BoundaryDecision.EXECUTE_WITHOUT_COMPACTION

    oversized = valid + b" " * (65_537 - len(valid))
    assert len(oversized) == 65_537
    rejected_code, rejected_output = invoke_cli(oversized)
    rejected = ContextBudgetAssessmentResult.model_validate_json(rejected_output)
    assert rejected_code == 2
    assert rejected.decision is BoundaryDecision.INVALID_REQUEST


def test_cli_rejects_path_or_host_arguments() -> None:
    exit_code, output = invoke_cli(make_request().model_dump_json().encode("utf-8"), ("C:/other.json",))
    result = ContextBudgetAssessmentResult.model_validate_json(output)
    assert exit_code == 2
    assert result.decision is BoundaryDecision.INVALID_REQUEST
