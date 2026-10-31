from __future__ import annotations

from collections.abc import Sequence

import pytest
from pydantic import ValidationError

from library.workflow_router.contracts import (
    ArtifactKind,
    AuthorityState,
    ContinuationDirective,
    DeliveryStage,
    HumanWaitReason,
    ProcessStage,
    RouterEventKind,
    RouterOutcome,
)
from library.workflow_router.mainline_projection import (
    MainlineProjectionRequest,
    MainlineTicket,
    MainlineTicketStatus,
)
from library.workflow_router.private_router import (
    AutomaticContinuationExecutor,
    AutomaticContinuationRunner,
    EntitlementGrant,
    EntitlementMode,
    FakeEntitlementProvider,
    FakePrivateRouterService,
    PrivateRouterClient,
    ProductActionLabel,
    RedactedSummary,
    RouterRequestEnvelope,
    RouterResponseEnvelope,
)
from library.workflow_router.profile import build_router_poc_profile
from library.workflow_router.package_continuation import (
    PackageAttemptOutcome,
    PackageContinuationStatus,
    WorkPackageContinuationLimits,
)


_PROJECT = "prj_0123456789abcdef"
_ACCOUNT = "acct_0123456789abcdef"
_REV_A = "rev-" + "a" * 64
_REV_B = "rev-" + "b" * 64
_PRIVATE_A = "rev_" + "a" * 64
_PRIVATE_B = "rev_" + "b" * 64
_LIMITS = WorkPackageContinuationLimits(max_package_rechecks=16, max_ticket_steps=4)


def _ticket(
    ref: str,
    *,
    status: MainlineTicketStatus = MainlineTicketStatus.ADMITTED,
    required: bool = True,
    dependencies: tuple[str, ...] = (),
    revision: str = "rev-1111111111111111",
) -> MainlineTicket:
    return MainlineTicket(
        ticket_ref=ref,
        ticket_revision=revision,
        required=required,
        status=status,
        depends_on=dependencies,
        admission_ref=None if status is MainlineTicketStatus.PLANNED else f"admission-{ref}",
        evidence_refs=(f"evidence-{ref}",) if status is MainlineTicketStatus.COMPLETED else (),
    )


def _state(
    *tickets: MainlineTicket,
    source_revision: str = _REV_A,
    project_id: str = _PROJECT,
    mainline_ref: str = "mainline-work-package",
) -> MainlineProjectionRequest:
    return MainlineProjectionRequest(
        project_id=project_id,
        mainline_ref=mainline_ref,
        source_revision=source_revision,
        tickets=tuple(tickets),
    )


def _request(
    ticket_ref: str,
    *,
    stage: ProcessStage = ProcessStage.INTAKE,
    event: RouterEventKind = RouterEventKind.INTAKE,
    revision: str = _PRIVATE_A,
    project_id: str = _PROJECT,
    suffix: int = 1,
) -> RouterRequestEnvelope:
    return RouterRequestEnvelope(
        request_id=f"req_{suffix:032x}",
        account_subject_id=_ACCOUNT,
        opaque_project_id=project_id,
        project_entry_mode="new_project",
        entitlement_mode=EntitlementMode.FIRST_PROJECT_FREE,
        workflow_stage=stage,
        authority_state=AuthorityState.NOT_REQUIRED,
        delivery_stage=DeliveryStage.POC,
        router_event_kind=event,
        event_correlation_id=f"evt_{suffix:032x}",
        available_source_kinds=(
            ArtifactKind.PROJECT_GOAL
            if stage is ProcessStage.INTAKE
            else ArtifactKind.WAYFINDER_OUTPUT,
        ),
        revision_digests=(revision,),
        structured_redacted_summary=RedactedSummary(
            evidence_codes=("goal_captured",), risk_codes=("none",), source_count_bucket=1
        ),
        client_version="v1",
        ticket_reference=ticket_ref,
    )


class _StatePort:
    def __init__(self, snapshots: Sequence[object]) -> None:
        self.snapshots = list(snapshots)
        self.read_count = 0

    def read(self) -> object:
        self.read_count += 1
        if not self.snapshots:
            return None
        if len(self.snapshots) == 1:
            return self.snapshots[0]
        return self.snapshots.pop(0)


class _RequestPort:
    def __init__(self, requests: dict[object, object]) -> None:
        self.requests = requests
        self.calls: list[tuple[str, str, str]] = []

    def read_request(self, ticket_ref: str, project_id: str, source_revision: str) -> object:
        self.calls.append((ticket_ref, project_id, source_revision))
        return self.requests.get((ticket_ref, source_revision), self.requests.get(ticket_ref))


class _PackageExecutor:
    def __init__(self, returns: Sequence[object] = ()) -> None:
        self.returns = list(returns)
        self.calls: list[tuple[str, str, str, ProductActionLabel]] = []

    def execute(
        self, project_id: str, ticket_ref: str, source_revision: str, action_label: ProductActionLabel
    ) -> object:
        self.calls.append((project_id, ticket_ref, source_revision, action_label))
        if not self.returns:
            raise AssertionError("unexpected package action")
        return self.returns.pop(0)


class _UnusedLegacyExecutor(AutomaticContinuationExecutor):
    def execute(self, *, action_label: ProductActionLabel) -> RouterRequestEnvelope:
        raise AssertionError("package continuation must use its ticket-bound executor")


class _WaitForAService:
    def __init__(self) -> None:
        self.normal = FakePrivateRouterService(
            profile=build_router_poc_profile(),
            entitlement_provider=FakeEntitlementProvider(
                grants=(
                    EntitlementGrant(
                        account_subject_id=_ACCOUNT,
                        opaque_project_id=_PROJECT,
                        permitted_modes=(EntitlementMode.FIRST_PROJECT_FREE,),
                    ),
                )
            ),
        )

    def decide(self, request: RouterRequestEnvelope) -> object:
        if request.ticket_reference == "ticket-a":
            return RouterResponseEnvelope(
                request_id=request.request_id,
                decision_id=f"dec_{'f' * 32}",
                outcome=RouterOutcome.SUSPEND,
                continuation=ContinuationDirective.WAIT_FOR_HUMAN,
                next_stage=None,
                action_label=ProductActionLabel.REQUEST_APPROVAL,
                allowed_action_labels=(),
                required_source_kinds=(),
                context_budget=None,
                wait_reason=HumanWaitReason.TICKET_APPROVAL_REQUIRED,
            )
        return self.normal.decide(request)


def _runner(service: object | None = None) -> AutomaticContinuationRunner:
    actual_service = service or FakePrivateRouterService(
        profile=build_router_poc_profile(),
        entitlement_provider=FakeEntitlementProvider(
            grants=(
                EntitlementGrant(
                    account_subject_id=_ACCOUNT,
                    opaque_project_id=_PROJECT,
                    permitted_modes=(EntitlementMode.FIRST_PROJECT_FREE,),
                ),
            )
        ),
    )
    return AutomaticContinuationRunner(
        client=PrivateRouterClient(service=actual_service),
        executor=_UnusedLegacyExecutor(),
    )


def _run(
    runner: AutomaticContinuationRunner,
    state_port: _StatePort,
    requests: _RequestPort,
    executor: _PackageExecutor,
    *,
    limits: WorkPackageContinuationLimits = _LIMITS,
):
    return runner.run_work_package_until_pause(
        state_port=state_port,
        request_port=requests,
        executor=executor,
        limits=limits,
    )


def test_runner_exposes_approved_work_package_entry() -> None:
    assert callable(getattr(AutomaticContinuationRunner, "run_work_package_until_pause", None))


@pytest.mark.parametrize("field", ["max_package_rechecks", "max_ticket_steps"])
@pytest.mark.parametrize("bad", [True, False, 0, -1, 1.5])
def test_positive_limits_reject_nonpositive_or_noninteger_values(field: str, bad: object) -> None:
    rechecks: object = bad if field == "max_package_rechecks" else 1
    steps: object = bad if field == "max_ticket_steps" else 1
    with pytest.raises(ValidationError):
        WorkPackageContinuationLimits(max_package_rechecks=rechecks, max_ticket_steps=steps)


def test_constructed_invalid_limits_are_rechecked_before_reading_state() -> None:
    limits = WorkPackageContinuationLimits.model_construct(max_package_rechecks=True, max_ticket_steps=1)
    states = _StatePort([_state(_ticket("ticket-a"))])
    with pytest.raises(ValidationError):
        _run(_runner(), states, _RequestPort({}), _PackageExecutor(), limits=limits)
    assert states.read_count == 0


def test_waiting_ticket_does_not_freeze_independent_admitted_ticket() -> None:
    initial = _state(_ticket("ticket-a"), _ticket("ticket-b"))
    completed = _state(
        _ticket("ticket-a"),
        _ticket("ticket-b", status=MainlineTicketStatus.COMPLETED),
        source_revision=_REV_B,
    )
    requests = _RequestPort({
        "ticket-a": _request("ticket-a", suffix=1),
        "ticket-b": _request("ticket-b", suffix=2),
    })
    executor = _PackageExecutor([_request("ticket-b", stage=ProcessStage.WAYFINDER,
                                           event=RouterEventKind.WAYFINDER_NO_GO, suffix=3)])
    states = _StatePort([initial, initial, initial, completed])

    result = _run(_runner(_WaitForAService()), states, requests, executor)

    assert result.status is PackageContinuationStatus.QUIESCENT
    assert [attempt.outcome for attempt in result.attempts] == [
        PackageAttemptOutcome.ROUTER_WAIT,
        PackageAttemptOutcome.ROUTER_HALT,
    ]
    assert [call[1] for call in executor.calls] == ["ticket-b"]
    assert [call[0] for call in requests.calls] == ["ticket-a", "ticket-b"]
    assert result.remaining_ticket_refs == ("ticket-a",)


def test_dependency_and_planned_tickets_never_get_requests_or_actions() -> None:
    initial = _state(
        _ticket("ticket-a"),
        _ticket("ticket-b"),
        _ticket("ticket-c", dependencies=("ticket-a",)),
        _ticket("ticket-d", status=MainlineTicketStatus.PLANNED),
    )
    requests = _RequestPort({
        "ticket-a": _request("ticket-a", stage=ProcessStage.WAYFINDER,
                              event=RouterEventKind.WAYFINDER_NO_GO, suffix=1),
        "ticket-b": _request("ticket-b", stage=ProcessStage.WAYFINDER,
                              event=RouterEventKind.WAYFINDER_NO_GO, suffix=2),
    })
    states = _StatePort([initial])
    result = _run(_runner(), states, requests, _PackageExecutor())

    assert result.status is PackageContinuationStatus.QUIESCENT
    assert [call[0] for call in requests.calls] == ["ticket-a", "ticket-b"]
    assert not result.attempts[0].steps and not result.attempts[1].steps
    assert result.remaining_ticket_refs == ("ticket-a", "ticket-b", "ticket-c", "ticket-d")


@pytest.mark.parametrize(
    "provided_request",
    [
        _request("ticket-a", project_id="prj_1123456789abcdef"),
        _request("ticket-x"),
        _request("ticket-a", revision=_PRIVATE_B),
        RouterRequestEnvelope.model_construct(),
    ],
)
def test_untrusted_request_must_be_deep_validated_and_exactly_bound(provided_request: object) -> None:
    states = _StatePort([_state(_ticket("ticket-a"))])
    executor = _PackageExecutor()
    service = FakePrivateRouterService(
        profile=build_router_poc_profile(),
        entitlement_provider=FakeEntitlementProvider(grants=()),
    )
    result = _run(_runner(service), states, _RequestPort({"ticket-a": provided_request}), executor)

    assert result.status is PackageContinuationStatus.QUIESCENT
    assert result.attempts[0].outcome in (
        PackageAttemptOutcome.REQUEST_BINDING_MISMATCH,
        PackageAttemptOutcome.REQUEST_MISSING,
    )
    assert service.request_count == 0
    assert not executor.calls


@pytest.mark.parametrize(
    "returned",
    [
        _request("ticket-x", suffix=2),
        _request("ticket-a", project_id="prj_1123456789abcdef", suffix=2),
        _request("ticket-a", revision=_PRIVATE_B, suffix=2),
        RouterRequestEnvelope.model_construct(),
    ],
)
def test_foreign_executor_return_is_rejected_before_router_can_consume_it(returned: object) -> None:
    states = _StatePort([_state(_ticket("ticket-a"))])
    service = FakePrivateRouterService(
        profile=build_router_poc_profile(),
        entitlement_provider=FakeEntitlementProvider(
            grants=(EntitlementGrant(account_subject_id=_ACCOUNT, opaque_project_id=_PROJECT,
                                     permitted_modes=(EntitlementMode.FIRST_PROJECT_FREE,)),)
        ),
    )
    executor = _PackageExecutor([returned])
    result = _run(
        _runner(service), states,
        _RequestPort({"ticket-a": _request("ticket-a", suffix=1)}), executor,
    )

    assert result.status is PackageContinuationStatus.QUIESCENT
    assert result.attempts[0].outcome is PackageAttemptOutcome.RETURN_BINDING_MISMATCH
    assert result.total_steps == 1 and service.request_count == 1
    assert result.attempts[0].steps[0].result_bound is False


def test_unchanged_observation_is_attempted_only_once() -> None:
    state = _state(_ticket("ticket-a"))
    requests = _RequestPort({
        "ticket-a": _request("ticket-a", stage=ProcessStage.WAYFINDER,
                              event=RouterEventKind.WAYFINDER_NO_GO, suffix=1),
    })
    service = FakePrivateRouterService(
        profile=build_router_poc_profile(), entitlement_provider=FakeEntitlementProvider(grants=())
    )
    result = _run(_runner(service), _StatePort([state]), requests, _PackageExecutor())

    assert result.status is PackageContinuationStatus.QUIESCENT
    assert len(result.attempts) == 1
    assert len(requests.calls) == 1 and service.request_count == 1


def test_graph_identity_drift_stops_package_globally() -> None:
    original = _state(_ticket("ticket-a"))
    drifted = _state(_ticket("ticket-a"), _ticket("ticket-b"))
    states = _StatePort([original, drifted])
    requests = _RequestPort({
        "ticket-a": _request("ticket-a", suffix=1),
        "ticket-b": _request("ticket-b", suffix=2),
    })

    result = _run(_runner(_WaitForAService()), states, requests, _PackageExecutor())

    assert result.status is PackageContinuationStatus.ENVIRONMENT_INTERRUPTED
    assert [call[0] for call in requests.calls] == ["ticket-a"]
    assert result.remaining_ticket_refs == ("ticket-a",)


@pytest.mark.parametrize("changed_fact", ["admission_ref", "dependency", "required", "evidence"])
def test_same_revision_ticket_fact_drift_interrupts_before_any_effect(changed_fact: str) -> None:
    ticket_a = _ticket("ticket-a", dependencies=("ticket-b",))
    ticket_b = _ticket("ticket-b", status=MainlineTicketStatus.COMPLETED)
    changed_a = ticket_a
    changed_b = ticket_b
    if changed_fact == "admission_ref":
        changed_a = ticket_a.model_copy(update={"admission_ref": "admission-replaced"})
    elif changed_fact == "dependency":
        changed_a = ticket_a.model_copy(update={"depends_on": ()})
    elif changed_fact == "required":
        changed_a = ticket_a.model_copy(update={"required": False})
    else:
        changed_b = ticket_b.model_copy(update={"evidence_refs": ("evidence-replaced",)})

    initial = _state(ticket_a, ticket_b)
    conflicting_same_revision = _state(changed_a, changed_b)
    executor = _PackageExecutor([
        _request("ticket-a", stage=ProcessStage.WAYFINDER,
                 event=RouterEventKind.WAYFINDER_NO_GO, suffix=2),
    ])
    result = _run(
        _runner(), _StatePort([initial, conflicting_same_revision]),
        _RequestPort({"ticket-a": _request("ticket-a", suffix=1)}), executor,
    )

    assert result.status is PackageContinuationStatus.ENVIRONMENT_INTERRUPTED
    assert result.attempts[0].outcome is PackageAttemptOutcome.STATE_CHANGED
    assert not result.attempts[0].steps
    assert not executor.calls


@pytest.mark.parametrize("identity", ["project", "mainline"])
def test_project_or_mainline_drift_stops_before_action(identity: str) -> None:
    initial = _state(_ticket("ticket-a"))
    drifted = _state(
        _ticket("ticket-a"),
        project_id="prj_1123456789abcdef" if identity == "project" else _PROJECT,
        mainline_ref="mainline-other" if identity == "mainline" else "mainline-work-package",
    )
    result = _run(
        _runner(), _StatePort([initial, drifted]),
        _RequestPort({"ticket-a": _request("ticket-a", suffix=1)}), _PackageExecutor(),
    )

    assert result.status is PackageContinuationStatus.ENVIRONMENT_INTERRUPTED
    assert result.total_steps == 0


def test_foreign_completed_snapshot_preserves_last_trusted_package_result() -> None:
    original = _state(_ticket("ticket-a"))
    foreign = _state(
        _ticket("ticket-a", status=MainlineTicketStatus.COMPLETED),
        source_revision=_REV_B,
        project_id="prj_1123456789abcdef",
        mainline_ref="mainline-foreign",
    )
    result = _run(
        _runner(), _StatePort([original, foreign]),
        _RequestPort({"ticket-a": _request("ticket-a", suffix=1)}), _PackageExecutor(),
    )

    assert result.status is PackageContinuationStatus.ENVIRONMENT_INTERRUPTED
    assert result.project_id == original.project_id
    assert result.mainline_ref == original.mainline_ref
    assert result.source_revision == original.source_revision
    assert result.remaining_ticket_refs == ("ticket-a",)


def test_changed_snapshot_refreshes_request_and_never_executes_stale_next_step() -> None:
    before = _state(_ticket("ticket-a"), source_revision=_REV_A)
    after = _state(_ticket("ticket-a", revision="rev-2222222222222222"), source_revision=_REV_B)
    complete = _state(_ticket("ticket-a", status=MainlineTicketStatus.COMPLETED),
                       source_revision=_REV_B)
    states = _StatePort([before, before, after, after, complete])
    requests = _RequestPort({
        ("ticket-a", _REV_A): _request("ticket-a", suffix=1),
        ("ticket-a", _REV_B): _request("ticket-a", revision=_PRIVATE_B, suffix=3),
    })
    # The first automatic return stays on the old snapshot, but revalidation sees _REV_B
    # before any second effect; the outer package pass must resolve a fresh bound request.
    executor = _PackageExecutor([
        _request("ticket-a", suffix=2),
        _request("ticket-a", stage=ProcessStage.WAYFINDER,
                 event=RouterEventKind.WAYFINDER_NO_GO, revision=_PRIVATE_B, suffix=4),
    ])
    result = _run(_runner(), states, requests, executor)

    assert result.status is PackageContinuationStatus.COMPLETE
    assert [call[2] for call in requests.calls] == [_REV_A, _REV_B]
    assert [call[2] for call in executor.calls] == [_REV_A, _REV_B]
    assert result.total_steps == 2


def test_optional_included_ticket_must_complete_before_complete_status() -> None:
    initial = _state(
        _ticket("ticket-required", status=MainlineTicketStatus.COMPLETED),
        _ticket("ticket-optional", required=False),
    )
    complete = _state(
        _ticket("ticket-required", status=MainlineTicketStatus.COMPLETED),
        _ticket("ticket-optional", required=False, status=MainlineTicketStatus.COMPLETED),
        source_revision=_REV_B,
    )
    requests = _RequestPort({
        "ticket-optional": _request("ticket-optional", suffix=1),
    })
    executor = _PackageExecutor([
        _request("ticket-optional", stage=ProcessStage.WAYFINDER,
                 event=RouterEventKind.WAYFINDER_NO_GO, suffix=2),
    ])
    result = _run(_runner(), _StatePort([initial, initial, complete]), requests, executor)

    assert result.status is PackageContinuationStatus.COMPLETE
    assert not result.remaining_ticket_refs
    assert requests.calls[0][0] == "ticket-optional"
    assert executor.calls[0][1] == "ticket-optional"


def test_invalid_snapshot_and_short_source_revision_stop_before_request() -> None:
    malformed = MainlineProjectionRequest.model_construct(
        project_id=_PROJECT, mainline_ref="mainline-work-package", source_revision=_REV_A, tickets=(),
    )
    for snapshot in (malformed, _state(_ticket("ticket-a"), source_revision="rev-0123456789abcdef")):
        states = _StatePort([snapshot])
        requests = _RequestPort({})
        result = _run(_runner(), states, requests, _PackageExecutor())
        assert result.status is PackageContinuationStatus.ENVIRONMENT_INTERRUPTED
        assert not requests.calls


def test_safety_ceiling_is_not_reported_as_package_completion() -> None:
    auto = _request("ticket-a", suffix=1)
    returned = _request("ticket-a", suffix=2)
    states = _StatePort([_state(_ticket("ticket-a"))])
    result = _run(
        _runner(), states, _RequestPort({"ticket-a": auto}), _PackageExecutor([returned]),
        limits=WorkPackageContinuationLimits(max_package_rechecks=8, max_ticket_steps=1),
    )

    assert result.status is PackageContinuationStatus.SAFETY_CEILING
    assert result.remaining_ticket_refs == ("ticket-a",)
    assert result.total_steps == 1
