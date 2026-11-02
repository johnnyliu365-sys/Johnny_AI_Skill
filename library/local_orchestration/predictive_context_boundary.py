from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)


_Reference = Annotated[
    str,
    StringConstraints(
        strict=True,
        min_length=3,
        max_length=128,
        pattern=r"^[a-z][a-z0-9-]{2,127}$",
    ),
]
_TokenCount = Annotated[int, Field(ge=0, strict=True)]
_PositiveTokenCount = Annotated[int, Field(gt=0, strict=True)]
_PositiveSampleCount = Annotated[int, Field(gt=0, strict=True)]
_AssessmentPhase = Literal["PRE_UNIT", "POST_COMPACTION_REVERIFY"]
_UnitKind = Literal["SQL", "GIT", "TEST", "OTHER"]
_ExecutionState = Literal["NOT_STARTED", "RUNNING"]
_EstimateKind = Literal["CONSERVATIVE", "P90", "P95"]
_ReturnState = Literal["EXPECTED", "RECEIVED_UNACKNOWLEDGED"]
_ReturnPriority = Literal["ALERT", "SUCCESS"]


def _require_advisory_only(value: object) -> Literal[True]:
    if value is not True:
        raise ValueError("advisory_only must be the boolean true value")
    return True


_AdvisoryOnly = Annotated[Literal[True], BeforeValidator(_require_advisory_only)]


class BoundaryDecision(str, Enum):
    EXECUTE_WITHOUT_COMPACTION = "EXECUTE_WITHOUT_COMPACTION"
    CHECKPOINT_COMPACT_REVERIFY = "CHECKPOINT_COMPACT_REVERIFY"
    FRESH_CONTEXT_REQUIRED = "FRESH_CONTEXT_REQUIRED"
    SERIAL_DECOMPOSITION_REQUIRED = "SERIAL_DECOMPOSITION_REQUIRED"
    DEFER_UNTIL_UNIT_BOUNDARY = "DEFER_UNTIL_UNIT_BOUNDARY"
    OBSERVATION_UNAVAILABLE = "OBSERVATION_UNAVAILABLE"
    CONTEXT_EPOCH_MISMATCH = "CONTEXT_EPOCH_MISMATCH"
    UNIT_ESTIMATE_MISMATCH = "UNIT_ESTIMATE_MISMATCH"
    RETURN_SCHEDULE_REQUIRED = "RETURN_SCHEDULE_REQUIRED"
    INVALID_REQUEST = "INVALID_REQUEST"


_NO_PROJECTION_DECISIONS = frozenset(
    {
        BoundaryDecision.FRESH_CONTEXT_REQUIRED,
        BoundaryDecision.UNIT_ESTIMATE_MISMATCH,
        BoundaryDecision.OBSERVATION_UNAVAILABLE,
        BoundaryDecision.CONTEXT_EPOCH_MISMATCH,
        BoundaryDecision.DEFER_UNTIL_UNIT_BOUNDARY,
    }
)


class ContextCapacityObservation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )

    available: bool
    used_context_tokens: _TokenCount | None
    effective_host_capacity_tokens: _PositiveTokenCount | None
    context_epoch: _Reference | None
    observation_ref: _Reference | None

    @model_validator(mode="after")
    def validate_availability_evidence(self) -> Self:
        has_all_evidence = all(
            value is not None
            for value in (
                self.used_context_tokens,
                self.effective_host_capacity_tokens,
                self.context_epoch,
                self.observation_ref,
            )
        )
        has_any_evidence = any(
            value is not None
            for value in (
                self.used_context_tokens,
                self.effective_host_capacity_tokens,
                self.context_epoch,
                self.observation_ref,
            )
        )
        if self.available and not has_all_evidence:
            raise ValueError("available observations require all four evidence fields")
        if not self.available and has_any_evidence:
            raise ValueError("unavailable observations must not carry evidence fields")
        return self


class NextUnitEstimate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )

    unit_ref: _Reference
    kind: _EstimateKind
    estimated_tokens: _PositiveTokenCount
    evidence_ref: _Reference
    sample_count: _PositiveSampleCount | None

    @model_validator(mode="after")
    def validate_estimate_evidence(self) -> Self:
        if self.kind == "CONSERVATIVE" and self.sample_count is not None:
            raise ValueError("conservative estimates must not declare a sample count")
        if self.kind in ("P90", "P95") and self.sample_count is None:
            raise ValueError("percentile estimates require a positive sample count")
        return self


class ExpectedReturnBudget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )

    return_ref: _Reference
    producer_ref: _Reference
    dispatch_budget_ref: _Reference
    state: _ReturnState
    expected_accepted_tokens: _PositiveTokenCount
    priority: _ReturnPriority


class ContextBudgetAssessmentRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )

    schema_version: Literal["1"]
    advisory_only: _AdvisoryOnly
    ticket_ref: _Reference
    context_ticket_ref: _Reference
    unit_ref: _Reference
    phase: _AssessmentPhase
    unit_kind: _UnitKind
    execution_state: _ExecutionState
    expected_context_epoch: _Reference
    observation: ContextCapacityObservation
    estimate: NextUnitEstimate
    dispatch_overhead_tokens: _TokenCount
    review_reserve_tokens: _TokenCount
    pending_returns: tuple[ExpectedReturnBudget, ...]

    @model_validator(mode="after")
    def validate_unique_return_identity(self) -> Self:
        return_refs = tuple(item.return_ref for item in self.pending_returns)
        budget_refs = tuple(item.dispatch_budget_ref for item in self.pending_returns)
        if len(set(return_refs)) != len(return_refs):
            raise ValueError("return_ref values must be unique")
        if len(set(budget_refs)) != len(budget_refs):
            raise ValueError("dispatch_budget_ref values must be unique")
        success_seen = False
        for item in self.pending_returns:
            if item.priority == "SUCCESS":
                success_seen = True
            elif success_seen:
                raise ValueError("alerts must precede success returns")
        return self


class ContextBudgetAssessmentResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )

    schema_version: Literal["1"]
    advisory_only: _AdvisoryOnly
    ticket_ref: _Reference | None
    unit_ref: _Reference | None
    decision: BoundaryDecision
    projected_tokens: _TokenCount | None
    next_return_refs: tuple[_Reference, ...]

    @model_validator(mode="after")
    def validate_result_shape(self) -> Self:
        identities_missing = self.ticket_ref is None and self.unit_ref is None
        one_identity_missing = (self.ticket_ref is None) != (self.unit_ref is None)
        if one_identity_missing:
            raise ValueError("ticket_ref and unit_ref must be null together")
        if self.decision is BoundaryDecision.INVALID_REQUEST:
            if not identities_missing or self.projected_tokens is not None or self.next_return_refs:
                raise ValueError("invalid requests carry null identity and no projection or schedule")
            return self
        if identities_missing:
            raise ValueError("valid advice requires ticket_ref and unit_ref")
        if self.decision in _NO_PROJECTION_DECISIONS:
            if self.projected_tokens is not None:
                raise ValueError("early decisions must not carry arithmetic projections")
        elif self.projected_tokens is None:
            raise ValueError("arithmetic decisions require a nonnegative projection")
        if self.decision is BoundaryDecision.RETURN_SCHEDULE_REQUIRED:
            if not self.next_return_refs:
                raise ValueError("return scheduling requires a nonempty prefix")
            if len(set(self.next_return_refs)) != len(self.next_return_refs):
                raise ValueError("scheduled return references must be unique")
        elif self.next_return_refs:
            raise ValueError("only return scheduling may include return references")
        return self

    @classmethod
    def invalid_request(cls) -> ContextBudgetAssessmentResult:
        return cls(
            schema_version="1",
            advisory_only=True,
            ticket_ref=None,
            unit_ref=None,
            decision=BoundaryDecision.INVALID_REQUEST,
            projected_tokens=None,
            next_return_refs=(),
        )


class ContextBudgetGuard:
    __slots__ = ()

    def assess(
        self, request: ContextBudgetAssessmentRequest, /
    ) -> ContextBudgetAssessmentResult:
        try:
            raw_request: dict[str, object] = request.model_dump(warnings="none")
            validated = ContextBudgetAssessmentRequest.model_validate(raw_request)
        except (AttributeError, TypeError, ValidationError, ValueError):
            return ContextBudgetAssessmentResult.invalid_request()

        if validated.execution_state == "RUNNING":
            return _advice(validated, BoundaryDecision.DEFER_UNTIL_UNIT_BOUNDARY)
        if validated.ticket_ref != validated.context_ticket_ref:
            return _advice(validated, BoundaryDecision.FRESH_CONTEXT_REQUIRED)
        if validated.estimate.unit_ref != validated.unit_ref:
            return _advice(validated, BoundaryDecision.UNIT_ESTIMATE_MISMATCH)

        observation = validated.observation
        if not observation.available:
            return _advice(validated, BoundaryDecision.OBSERVATION_UNAVAILABLE)
        if observation.context_epoch != validated.expected_context_epoch:
            return _advice(validated, BoundaryDecision.CONTEXT_EPOCH_MISMATCH)
        if (
            observation.used_context_tokens is None
            or observation.effective_host_capacity_tokens is None
            or observation.context_epoch is None
            or observation.observation_ref is None
        ):
            return ContextBudgetAssessmentResult.invalid_request()

        capacity = observation.effective_host_capacity_tokens
        base_projection = (
            observation.used_context_tokens
            + validated.dispatch_overhead_tokens
            + validated.estimate.estimated_tokens
            + validated.review_reserve_tokens
        )
        fresh_projection = (
            validated.dispatch_overhead_tokens
            + validated.estimate.estimated_tokens
            + validated.review_reserve_tokens
        )

        if fresh_projection >= capacity:
            return _advice(
                validated,
                BoundaryDecision.SERIAL_DECOMPOSITION_REQUIRED,
                base_projection,
            )
        if base_projection >= capacity:
            decision = (
                BoundaryDecision.CHECKPOINT_COMPACT_REVERIFY
                if validated.phase == "PRE_UNIT"
                else BoundaryDecision.SERIAL_DECOMPOSITION_REQUIRED
            )
            return _advice(validated, decision, base_projection)

        has_alerts = any(item.priority == "ALERT" for item in validated.pending_returns)
        ordered_returns = (
            tuple(item for item in validated.pending_returns if item.priority == "ALERT")
            if has_alerts
            else validated.pending_returns
        )
        if not has_alerts:
            first_unacknowledged = next(
                (
                    item
                    for item in ordered_returns
                    if item.state == "RECEIVED_UNACKNOWLEDGED"
                ),
                None,
            )
            if first_unacknowledged is not None:
                return _advice(
                    validated,
                    BoundaryDecision.RETURN_SCHEDULE_REQUIRED,
                    base_projection,
                    (first_unacknowledged.return_ref,),
                )
        projection = base_projection
        selected_refs: list[_Reference] = []
        for item in ordered_returns:
            expected_tokens = (
                item.expected_accepted_tokens if item.state == "EXPECTED" else 0
            )
            if projection + expected_tokens >= capacity:
                break
            projection += expected_tokens
            selected_refs.append(item.return_ref)

        selected_prefix = tuple(selected_refs)
        if has_alerts and selected_prefix:
            return _advice(
                validated,
                BoundaryDecision.RETURN_SCHEDULE_REQUIRED,
                projection,
                selected_prefix,
            )
        if not has_alerts and len(selected_prefix) == len(ordered_returns):
            return _advice(
                validated,
                BoundaryDecision.EXECUTE_WITHOUT_COMPACTION,
                projection,
            )
        if selected_prefix:
            return _advice(
                validated,
                BoundaryDecision.RETURN_SCHEDULE_REQUIRED,
                projection,
                selected_prefix,
            )

        first = ordered_returns[0]
        first_tokens = first.expected_accepted_tokens
        if validated.phase == "PRE_UNIT" and fresh_projection + first_tokens < capacity:
            decision = BoundaryDecision.CHECKPOINT_COMPACT_REVERIFY
        else:
            decision = BoundaryDecision.SERIAL_DECOMPOSITION_REQUIRED
        return _advice(validated, decision, base_projection + first_tokens)


def _advice(
    request: ContextBudgetAssessmentRequest,
    decision: BoundaryDecision,
    projected_tokens: int | None = None,
    next_return_refs: tuple[_Reference, ...] = (),
) -> ContextBudgetAssessmentResult:
    return ContextBudgetAssessmentResult(
        schema_version="1",
        advisory_only=True,
        ticket_ref=request.ticket_ref,
        unit_ref=request.unit_ref,
        decision=decision,
        projected_tokens=projected_tokens,
        next_return_refs=next_return_refs,
    )
