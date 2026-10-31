"""Bounded, ticket-bound continuation for an approved local work package."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Protocol

from pydantic import Field, ValidationError

from .contracts import ProjectId, RevisionDigest, RouterModel
from .mainline_projection import (
    MainlineProjectionRequest,
    MainlineRef,
    MainlineTicket,
    MainlineTicketRef,
    MainlineTicketStatus,
    project_mainline_tickets,
)
from .private_router import (
    ContinuationMode,
    ContinuationPlan,
    OpaqueEventId,
    OpaqueRequestId,
    PrivateRouterClient,
    ProductActionLabel,
    RouterRequestEnvelope,
    RevisionDigest as PrivateRevisionDigest,
)


PositiveLimit = Annotated[int, Field(gt=0, strict=True)]
PackageSourceRevision = Annotated[str, Field(pattern=r"^rev-[0-9a-f]{64}$", strict=True)]


class WorkPackageContinuationLimits(RouterModel):
    """Positive bounds for fresh package reads and actions within one ticket."""

    max_package_rechecks: PositiveLimit
    max_ticket_steps: PositiveLimit


class PackageContinuationStatus(str, Enum):
    """Finite terminal states for one in-process continuation run."""

    COMPLETE = "complete"
    QUIESCENT = "quiescent"
    ENVIRONMENT_INTERRUPTED = "environment_interrupted"
    SAFETY_CEILING = "safety_ceiling"


class PackageAttemptOutcome(str, Enum):
    """Why one ticket attempt stopped before its next action."""

    ROUTER_WAIT = "router_wait"
    ROUTER_HALT = "router_halt"
    REQUEST_MISSING = "request_missing"
    REQUEST_BINDING_MISMATCH = "request_binding_mismatch"
    EXECUTOR_FAILED = "executor_failed"
    RETURN_BINDING_MISMATCH = "return_binding_mismatch"
    STATE_CHANGED = "state_changed"


class PackageStatePort(Protocol):
    """Fresh, typed view of the approved package's current mainline."""

    def read(self) -> MainlineProjectionRequest | None:
        """Return a candidate state or None when its source is unavailable."""


class PackageRequestPort(Protocol):
    """Resolve one Router request for an exact ticket and snapshot revision."""

    def read_request(
        self,
        ticket_ref: MainlineTicketRef,
        project_id: ProjectId,
        source_revision: PackageSourceRevision,
    ) -> RouterRequestEnvelope | None:
        """Read the request without making an action decision."""


class TicketBoundPackageExecutor(Protocol):
    """Execute only the action granted by the existing Private Router."""

    def execute(
        self,
        project_id: ProjectId,
        ticket_ref: MainlineTicketRef,
        source_revision: PackageSourceRevision,
        action_label: ProductActionLabel,
    ) -> RouterRequestEnvelope:
        """Return the next metadata envelope, bound to the same package item."""


class PackageActionStep(RouterModel):
    """Opaque evidence for one action admitted by the existing Router client."""

    project_id: ProjectId
    ticket_ref: MainlineTicketRef
    source_revision: PackageSourceRevision
    request_id: OpaqueRequestId
    request_event_id: OpaqueEventId
    action_label: ProductActionLabel
    result_request_id: OpaqueRequestId | None
    result_event_id: OpaqueEventId | None
    result_bound: bool


class PackageTicketAttempt(RouterModel):
    """One ticket observation and its bounded action trace."""

    project_id: ProjectId
    mainline_ref: MainlineRef
    ticket_ref: MainlineTicketRef
    ticket_revision: RevisionDigest
    source_revision: PackageSourceRevision
    outcome: PackageAttemptOutcome
    steps: tuple[PackageActionStep, ...]
    final_plan: ContinuationPlan | None


class WorkPackageRunResult(RouterModel):
    """Traceable terminal result, not a durable journal or closure certificate."""

    status: PackageContinuationStatus
    project_id: ProjectId | None
    mainline_ref: MainlineRef | None
    source_revision: PackageSourceRevision | None
    attempts: tuple[PackageTicketAttempt, ...]
    final_plan: ContinuationPlan | None
    remaining_ticket_refs: tuple[MainlineTicketRef, ...]
    package_rechecks: Annotated[int, Field(ge=0, strict=True)]
    total_steps: Annotated[int, Field(ge=0, strict=True)]


def run_package_continuation(
    *,
    client: PrivateRouterClient,
    state_port: PackageStatePort,
    request_port: PackageRequestPort,
    executor: TicketBoundPackageExecutor,
    limits: WorkPackageContinuationLimits,
) -> WorkPackageRunResult:
    """Continue independent admitted tickets through the existing Router boundary."""

    limits = WorkPackageContinuationLimits.model_validate(limits.model_dump())
    attempts: list[PackageTicketAttempt] = []
    attempted: set[MainlineTicket] = set()
    ticket_steps: dict[MainlineTicketRef, int] = {}
    total_steps = 0
    package_rechecks = 0
    final_plan: ContinuationPlan | None = None
    initial_state = _read_state(state_port)
    if initial_state is None:
        return _result(PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, None, (), attempts, final_plan, 0, 0)

    initial_revision = _full_source_revision(initial_state.source_revision)
    included_refs = tuple(ticket.ticket_ref for ticket in initial_state.tickets)
    if initial_revision is None:
        return _result(
            PackageContinuationStatus.ENVIRONMENT_INTERRUPTED,
            initial_state,
            included_refs,
            attempts,
            final_plan,
            0,
            0,
        )

    expected_project = initial_state.project_id
    expected_mainline = initial_state.mainline_ref
    current_state = initial_state

    def finish(
        status: PackageContinuationStatus,
        state: MainlineProjectionRequest | None,
        *,
        pending: PackageTicketAttempt | None = None,
    ) -> WorkPackageRunResult:
        entries = tuple(attempts) + (() if pending is None else (pending,))
        return _result(
            status,
            state,
            included_refs,
            entries,
            final_plan,
            package_rechecks,
            total_steps,
        )

    def recheck() -> tuple[MainlineProjectionRequest | None, bool]:
        nonlocal package_rechecks
        if package_rechecks >= limits.max_package_rechecks:
            return None, True
        package_rechecks += 1
        return _read_state(state_port), False

    while True:
        if not _state_matches(current_state, expected_project, expected_mainline, included_refs):
            return finish(PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state)

        tickets = {ticket.ticket_ref: ticket for ticket in current_state.tickets}
        if all(tickets[ref].status is MainlineTicketStatus.COMPLETED for ref in included_refs):
            return finish(PackageContinuationStatus.COMPLETE, current_state)

        projection = project_mainline_tickets(current_state)
        ready = frozenset(projection.ready_for_recheck)
        candidate = next(
            (
                ticket
                for ticket in current_state.tickets
                if ticket.ticket_ref in included_refs
                and ticket.ticket_ref in ready
                and ticket.status is MainlineTicketStatus.ADMITTED
                and ticket not in attempted
            ),
            None,
        )
        if candidate is None:
            return finish(PackageContinuationStatus.QUIESCENT, current_state)

        source_revision = _full_source_revision(current_state.source_revision)
        if source_revision is None:
            return finish(PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state)
        attempted.add(candidate)
        steps: list[PackageActionStep] = []
        attempt_plan: ContinuationPlan | None = None
        outcome = PackageAttemptOutcome.STATE_CHANGED
        try:
            raw_request = request_port.read_request(
                candidate.ticket_ref, current_state.project_id, source_revision
            )
        except Exception:
            raw_request = None
        request = _validated_request(raw_request)

        if request is None:
            outcome = PackageAttemptOutcome.REQUEST_MISSING
        elif not isinstance(request, RouterRequestEnvelope) or not _request_is_bound(
            request, current_state.project_id, candidate.ticket_ref, source_revision
        ):
            outcome = PackageAttemptOutcome.REQUEST_BINDING_MISMATCH
        else:
            while True:
                try:
                    attempt_plan = client.route(raw_request=request.model_dump())
                except Exception:
                    outcome = PackageAttemptOutcome.ROUTER_HALT
                    break
                final_plan = attempt_plan
                if attempt_plan.mode is ContinuationMode.WAIT_FOR_HUMAN:
                    outcome = PackageAttemptOutcome.ROUTER_WAIT
                    break
                if attempt_plan.mode is ContinuationMode.HALT or attempt_plan.action_label is None:
                    outcome = PackageAttemptOutcome.ROUTER_HALT
                    break
                if ticket_steps.get(candidate.ticket_ref, 0) >= limits.max_ticket_steps:
                    pending = _make_attempt(
                        current_state, candidate, source_revision, outcome, steps, attempt_plan
                    )
                    return finish(PackageContinuationStatus.SAFETY_CEILING, current_state, pending=pending)

                fresh_state, ceiling = recheck()
                if ceiling:
                    pending = _make_attempt(
                        current_state, candidate, source_revision, outcome, steps, attempt_plan
                    )
                    return finish(PackageContinuationStatus.SAFETY_CEILING, current_state, pending=pending)
                if fresh_state is None:
                    pending = _make_attempt(
                        current_state, candidate, source_revision, outcome, steps, attempt_plan
                    )
                    return finish(
                        PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state, pending=pending
                    )
                if not _state_matches(fresh_state, expected_project, expected_mainline, included_refs):
                    pending = _make_attempt(
                        current_state,
                        candidate,
                        source_revision,
                        PackageAttemptOutcome.STATE_CHANGED,
                        steps,
                        attempt_plan,
                    )
                    return finish(
                        PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state, pending=pending
                    )
                fresh_source_revision = _full_source_revision(fresh_state.source_revision)
                if fresh_source_revision != source_revision:
                    current_state = fresh_state
                    outcome = PackageAttemptOutcome.STATE_CHANGED
                    break
                if fresh_state.tickets != current_state.tickets:
                    pending = _make_attempt(
                        current_state,
                        candidate,
                        source_revision,
                        PackageAttemptOutcome.STATE_CHANGED,
                        steps,
                        attempt_plan,
                    )
                    return finish(
                        PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state, pending=pending
                    )
                fresh_ticket = next(
                    (item for item in fresh_state.tickets if item.ticket_ref == candidate.ticket_ref),
                    None,
                )
                if (
                    fresh_ticket is None
                    or fresh_ticket != candidate
                    or fresh_ticket.status is not MainlineTicketStatus.ADMITTED
                    or candidate.ticket_ref not in project_mainline_tickets(fresh_state).ready_for_recheck
                ):
                    pending = _make_attempt(
                        current_state,
                        candidate,
                        source_revision,
                        PackageAttemptOutcome.STATE_CHANGED,
                        steps,
                        attempt_plan,
                    )
                    return finish(
                        PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state, pending=pending
                    )

                step = PackageActionStep(
                    project_id=fresh_state.project_id,
                    ticket_ref=candidate.ticket_ref,
                    source_revision=source_revision,
                    request_id=request.request_id,
                    request_event_id=request.event_correlation_id,
                    action_label=attempt_plan.action_label,
                    result_request_id=None,
                    result_event_id=None,
                    result_bound=False,
                )
                ticket_steps[candidate.ticket_ref] = ticket_steps.get(candidate.ticket_ref, 0) + 1
                total_steps += 1
                try:
                    raw_returned = executor.execute(
                        fresh_state.project_id,
                        candidate.ticket_ref,
                        source_revision,
                        attempt_plan.action_label,
                    )
                except Exception:
                    steps.append(step)
                    outcome = PackageAttemptOutcome.EXECUTOR_FAILED
                    break
                returned = _validated_request(raw_returned)
                if returned is None or not _request_is_bound(
                    returned, fresh_state.project_id, candidate.ticket_ref, source_revision
                ):
                    steps.append(step)
                    outcome = PackageAttemptOutcome.RETURN_BINDING_MISMATCH
                    break
                if attempt_plan.response is None:
                    steps.append(step)
                    outcome = PackageAttemptOutcome.ROUTER_HALT
                    break

                steps.append(
                    PackageActionStep(
                        project_id=fresh_state.project_id,
                        ticket_ref=candidate.ticket_ref,
                        source_revision=source_revision,
                        request_id=request.request_id,
                        request_event_id=request.event_correlation_id,
                        action_label=attempt_plan.action_label,
                        result_request_id=returned.request_id,
                        result_event_id=returned.event_correlation_id,
                        result_bound=True,
                    )
                )
                current_state = fresh_state
                request = returned

        attempt = _make_attempt(current_state, candidate, source_revision, outcome, steps, attempt_plan)
        attempts.append(attempt)
        if outcome is PackageAttemptOutcome.STATE_CHANGED:
            attempted.discard(candidate)
            continue

        fresh_state, ceiling = recheck()
        if ceiling:
            return finish(PackageContinuationStatus.SAFETY_CEILING, current_state)
        if fresh_state is None:
            return finish(PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, current_state)
        if not _state_matches(fresh_state, expected_project, expected_mainline, included_refs):
            return finish(PackageContinuationStatus.ENVIRONMENT_INTERRUPTED, fresh_state)
        current_state = fresh_state


def _make_attempt(
    state: MainlineProjectionRequest,
    ticket: MainlineTicket,
    source_revision: PackageSourceRevision,
    outcome: PackageAttemptOutcome,
    steps: list[PackageActionStep],
    plan: ContinuationPlan | None,
) -> PackageTicketAttempt:
    return PackageTicketAttempt(
        project_id=state.project_id,
        mainline_ref=state.mainline_ref,
        ticket_ref=ticket.ticket_ref,
        ticket_revision=ticket.ticket_revision,
        source_revision=source_revision,
        outcome=outcome,
        steps=tuple(steps),
        final_plan=plan,
    )


def _read_state(port: PackageStatePort) -> MainlineProjectionRequest | None:
    try:
        raw_state = port.read()
    except Exception:
        return None
    if not isinstance(raw_state, MainlineProjectionRequest):
        return None
    try:
        return MainlineProjectionRequest.model_validate(raw_state.model_dump())
    except (ValidationError, TypeError, ValueError):
        return None


def _validated_request(value: object) -> RouterRequestEnvelope | None:
    if not isinstance(value, RouterRequestEnvelope):
        return None
    try:
        return RouterRequestEnvelope.model_validate(value.model_dump())
    except (ValidationError, TypeError, ValueError):
        return None


def _full_source_revision(value: RevisionDigest) -> PackageSourceRevision | None:
    if len(value) != 68 or not value.startswith("rev-"):
        return None
    return value if all(char in "0123456789abcdef" for char in value[4:]) else None


def _request_is_bound(
    request: RouterRequestEnvelope,
    project_id: ProjectId,
    ticket_ref: MainlineTicketRef,
    source_revision: PackageSourceRevision,
) -> bool:
    expected_digest: PrivateRevisionDigest = "rev_" + source_revision[4:]
    return (
        request.opaque_project_id == project_id
        and request.ticket_reference == ticket_ref
        and expected_digest in request.revision_digests
    )


def _state_matches(
    state: MainlineProjectionRequest,
    project_id: ProjectId,
    mainline_ref: MainlineRef,
    included_refs: tuple[MainlineTicketRef, ...],
) -> bool:
    current_refs = {ticket.ticket_ref for ticket in state.tickets}
    return (
        state.project_id == project_id
        and state.mainline_ref == mainline_ref
        and current_refs == set(included_refs)
        and _full_source_revision(state.source_revision) is not None
    )


def _result(
    status: PackageContinuationStatus,
    state: MainlineProjectionRequest | None,
    included_refs: tuple[MainlineTicketRef, ...],
    attempts: list[PackageTicketAttempt] | tuple[PackageTicketAttempt, ...],
    final_plan: ContinuationPlan | None,
    package_rechecks: int,
    total_steps: int,
) -> WorkPackageRunResult:
    tickets = {} if state is None else {ticket.ticket_ref: ticket for ticket in state.tickets}
    remaining = tuple(
        ref
        for ref in included_refs
        if ref not in tickets or tickets[ref].status is not MainlineTicketStatus.COMPLETED
    )
    return WorkPackageRunResult(
        status=status,
        project_id=None if state is None else state.project_id,
        mainline_ref=None if state is None else state.mainline_ref,
        source_revision=None if state is None else _full_source_revision(state.source_revision),
        attempts=tuple(attempts),
        final_plan=final_plan,
        remaining_ticket_refs=remaining,
        package_rechecks=package_rechecks,
        total_steps=total_steps,
    )


__all__ = (
    "PackageActionStep",
    "PackageAttemptOutcome",
    "PackageContinuationStatus",
    "PackageRequestPort",
    "PackageStatePort",
    "PackageTicketAttempt",
    "PackageSourceRevision",
    "TicketBoundPackageExecutor",
    "WorkPackageContinuationLimits",
    "WorkPackageRunResult",
    "run_package_continuation",
)
