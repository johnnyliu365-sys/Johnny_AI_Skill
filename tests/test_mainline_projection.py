from __future__ import annotations

import pytest
from pydantic import ValidationError

from library.workflow_router import (
    MainlineProjectionRequest,
    MainlineTicket,
    MainlineTicketStatus,
    project_mainline_tickets,
)


def _ticket(
    ticket_ref: str,
    *,
    status: MainlineTicketStatus,
    required: bool = True,
    dependencies: tuple[str, ...] = (),
    admission_ref: str | None = None,
    evidence_refs: tuple[str, ...] = (),
) -> MainlineTicket:
    revision_suffix = {
        "ticket-alpha": "1",
        "ticket-beta": "2",
        "ticket-gamma": "3",
        "ticket-delta": "4",
        "ticket-epsilon": "5",
    }.get(ticket_ref, "9")
    return MainlineTicket(
        ticket_ref=ticket_ref,
        ticket_revision=f"rev-{revision_suffix * 16}",
        required=required,
        status=status,
        depends_on=dependencies,
        admission_ref=admission_ref,
        evidence_refs=evidence_refs,
    )


def _request(tickets: tuple[MainlineTicket, ...]) -> MainlineProjectionRequest:
    return MainlineProjectionRequest(
        project_id="prj_0123456789abcdef",
        mainline_ref="mainline-example",
        source_revision="rev-abcdef0123456789",
        tickets=tickets,
    )


def test_waiting_ticket_does_not_block_independent_candidate_or_borrow_dependency() -> None:
    request = _request(
        (
            _ticket(
                "ticket-alpha",
                status=MainlineTicketStatus.WAITING,
                admission_ref="admission-alpha",
            ),
            _ticket(
                "ticket-beta",
                status=MainlineTicketStatus.ADMITTED,
                admission_ref="admission-beta",
            ),
            _ticket(
                "ticket-gamma",
                status=MainlineTicketStatus.PLANNED,
                dependencies=("ticket-alpha",),
            ),
        )
    )

    projection = project_mainline_tickets(request)

    assert projection.ready_for_recheck == ("ticket-beta",)
    assert projection.waiting == ("ticket-alpha", "ticket-gamma")
    assert projection.incomplete_required == (
        "ticket-alpha",
        "ticket-beta",
        "ticket-gamma",
    )
    assert projection.closure_candidate is False


def test_completing_independent_ticket_does_not_close_mainline_with_required_work_open() -> None:
    request = _request(
        (
            _ticket(
                "ticket-alpha",
                status=MainlineTicketStatus.WAITING,
                admission_ref="admission-alpha",
            ),
            _ticket(
                "ticket-beta",
                status=MainlineTicketStatus.COMPLETED,
                admission_ref="admission-beta",
                evidence_refs=("evidence-beta",),
            ),
            _ticket(
                "ticket-gamma",
                status=MainlineTicketStatus.PLANNED,
                dependencies=("ticket-alpha",),
            ),
        )
    )

    projection = project_mainline_tickets(request)

    assert projection.ready_for_recheck == ()
    assert projection.waiting == ("ticket-alpha", "ticket-gamma")
    assert projection.incomplete_required == ("ticket-alpha", "ticket-gamma")
    assert projection.closure_candidate is False


def test_pending_optional_ticket_does_not_block_closure_candidate() -> None:
    request = _request(
        (
            _ticket(
                "ticket-delta",
                status=MainlineTicketStatus.COMPLETED,
                admission_ref="admission-delta",
                evidence_refs=("evidence-delta",),
            ),
            _ticket(
                "ticket-epsilon",
                status=MainlineTicketStatus.PLANNED,
                required=False,
            ),
        )
    )

    projection = project_mainline_tickets(request)

    assert projection.incomplete_required == ()
    assert projection.ready_for_recheck == ("ticket-epsilon",)
    assert projection.closure_candidate is True


def test_projection_preserves_project_mainline_and_source_revision_binding() -> None:
    request = _request(
        (
            _ticket(
                "ticket-alpha",
                status=MainlineTicketStatus.PLANNED,
            ),
        )
    )

    projection = project_mainline_tickets(request)

    assert projection.project_id == request.project_id
    assert projection.mainline_ref == request.mainline_ref
    assert projection.source_revision == request.source_revision


def test_unknown_dependency_is_rejected() -> None:
    request = (
        _ticket(
            "ticket-alpha",
            status=MainlineTicketStatus.PLANNED,
            dependencies=("ticket-unknown",),
        ),
    )

    with pytest.raises(ValidationError, match="every dependency must name a mainline ticket"):
        _request(request)


def test_duplicate_ticket_reference_is_rejected() -> None:
    ticket = _ticket("ticket-alpha", status=MainlineTicketStatus.PLANNED)

    with pytest.raises(ValidationError, match="ticket references must be unique"):
        _request((ticket, ticket))


def test_self_dependency_is_rejected() -> None:
    with pytest.raises(ValidationError, match="a ticket cannot depend on itself"):
        _ticket(
            "ticket-alpha",
            status=MainlineTicketStatus.PLANNED,
            dependencies=("ticket-alpha",),
        )


def test_duplicate_dependency_reference_is_rejected() -> None:
    with pytest.raises(ValidationError, match="dependency references must be unique"):
        _ticket(
            "ticket-alpha",
            status=MainlineTicketStatus.PLANNED,
            dependencies=("ticket-beta", "ticket-beta"),
        )


def test_dependency_cycle_is_rejected() -> None:
    request = (
        _ticket(
            "ticket-alpha",
            status=MainlineTicketStatus.PLANNED,
            dependencies=("ticket-beta",),
        ),
        _ticket(
            "ticket-beta",
            status=MainlineTicketStatus.PLANNED,
            dependencies=("ticket-alpha",),
        ),
    )

    with pytest.raises(ValidationError, match="mainline dependency graph must be acyclic"):
        _request(request)


def test_in_progress_ticket_cannot_skip_an_incomplete_dependency() -> None:
    request = (
        _ticket("ticket-alpha", status=MainlineTicketStatus.WAITING),
        _ticket(
            "ticket-beta",
            status=MainlineTicketStatus.IN_PROGRESS,
            admission_ref="admission-beta",
            dependencies=("ticket-alpha",),
        ),
    )

    with pytest.raises(ValidationError, match="active or completed tickets require completed dependencies"):
        _request(request)


def test_completed_ticket_requires_admission_and_evidence_references() -> None:
    with pytest.raises(ValidationError, match="completed tickets require admission and evidence references"):
        _ticket("ticket-alpha", status=MainlineTicketStatus.COMPLETED)


def test_prompt_like_metadata_reference_is_rejected() -> None:
    for reference in ("prompt-content", "source-body", "path-reference", "../source/body"):
        with pytest.raises(ValidationError):
            _ticket(reference, status=MainlineTicketStatus.PLANNED)


def test_metadata_reference_can_contain_a_non_reserved_word_substring() -> None:
    ticket = _ticket("ticket-resource", status=MainlineTicketStatus.PLANNED)

    projection = project_mainline_tickets(_request((ticket,)))

    assert projection.ready_for_recheck == ("ticket-resource",)
