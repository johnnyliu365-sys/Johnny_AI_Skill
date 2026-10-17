"""Immutable metadata projection for a cross-ticket work mainline."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Self, TypeAlias

from pydantic import AfterValidator, Field, model_validator

from .contracts import ProjectId, RevisionDigest, RouterModel


def _validate_metadata_reference(value: str) -> str:
    """Reject content-like words from otherwise opaque metadata identifiers."""

    content_markers = ("body", "path", "prompt", "secret", "source")
    if any(marker in value.split("-") for marker in content_markers):
        raise ValueError("metadata references cannot contain content markers")
    return value


MainlineMetadataRef: TypeAlias = Annotated[
    str,
    Field(pattern=r"^[a-z][a-z0-9-]{2,127}$"),
    AfterValidator(_validate_metadata_reference),
]
MainlineRef: TypeAlias = MainlineMetadataRef
MainlineTicketRef: TypeAlias = MainlineMetadataRef
MainlineAdmissionRef: TypeAlias = MainlineMetadataRef
MainlineEvidenceRef: TypeAlias = MainlineMetadataRef


class MainlineTicketStatus(str, Enum):
    """Finite lifecycle states represented by the mainline projection."""

    PLANNED = "planned"
    ADMITTED = "admitted"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    COMPLETED = "completed"


class MainlineTicket(RouterModel):
    """One revision-bound ticket node containing identifiers and status only."""

    ticket_ref: MainlineTicketRef
    ticket_revision: RevisionDigest
    required: bool
    status: MainlineTicketStatus
    depends_on: tuple[MainlineTicketRef, ...] = ()
    admission_ref: MainlineAdmissionRef | None = None
    evidence_refs: tuple[MainlineEvidenceRef, ...] = ()

    @model_validator(mode="after")
    def references_and_status_are_consistent(self) -> Self:
        if self.ticket_ref in self.depends_on:
            raise ValueError("a ticket cannot depend on itself")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError("dependency references must be unique")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence references must be unique")

        if self.status is MainlineTicketStatus.PLANNED:
            if self.admission_ref is not None or self.evidence_refs:
                raise ValueError("planned tickets cannot contain admission or evidence references")
        elif self.status is MainlineTicketStatus.ADMITTED:
            if self.admission_ref is None or self.evidence_refs:
                raise ValueError("admitted tickets require only an admission reference")
        elif self.status is MainlineTicketStatus.IN_PROGRESS:
            if self.admission_ref is None:
                raise ValueError("in-progress tickets require an admission reference")
        elif self.status is MainlineTicketStatus.COMPLETED:
            if self.admission_ref is None or not self.evidence_refs:
                raise ValueError("completed tickets require admission and evidence references")
        return self


def _dependency_graph_is_acyclic(tickets: tuple[MainlineTicket, ...]) -> bool:
    """Check the graph using the same active/complete DFS distinction as review graphs."""

    graph: dict[MainlineTicketRef, tuple[MainlineTicketRef, ...]] = {
        ticket.ticket_ref: ticket.depends_on for ticket in tickets
    }
    complete: set[MainlineTicketRef] = set()
    active: set[MainlineTicketRef] = set()

    def visit(ticket_ref: MainlineTicketRef) -> bool:
        if ticket_ref in complete:
            return True
        if ticket_ref in active:
            return False
        active.add(ticket_ref)
        for dependency in graph[ticket_ref]:
            if not visit(dependency):
                return False
        active.remove(ticket_ref)
        complete.add(ticket_ref)
        return True

    return all(visit(ticket_ref) for ticket_ref in graph)


class MainlineProjectionRequest(RouterModel):
    """A project/source-bound snapshot of the ticket nodes for one mainline."""

    project_id: ProjectId
    mainline_ref: MainlineRef
    source_revision: RevisionDigest
    tickets: tuple[MainlineTicket, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def ticket_graph_is_bound_and_valid(self) -> Self:
        ticket_refs = tuple(ticket.ticket_ref for ticket in self.tickets)
        if len(ticket_refs) != len(set(ticket_refs)):
            raise ValueError("ticket references must be unique")
        ticket_ref_set = set(ticket_refs)
        if any(
            dependency not in ticket_ref_set
            for ticket in self.tickets
            for dependency in ticket.depends_on
        ):
            raise ValueError("every dependency must name a mainline ticket")
        if not _dependency_graph_is_acyclic(self.tickets):
            raise ValueError("mainline dependency graph must be acyclic")

        tickets_by_ref = {ticket.ticket_ref: ticket for ticket in self.tickets}
        if any(
            ticket.status in (MainlineTicketStatus.IN_PROGRESS, MainlineTicketStatus.COMPLETED)
            and any(
                tickets_by_ref[dependency].status is not MainlineTicketStatus.COMPLETED
                for dependency in ticket.depends_on
            )
            for ticket in self.tickets
        ):
            raise ValueError("active or completed tickets require completed dependencies")
        return self


class MainlineProjection(RouterModel):
    """A read-only candidate view; neither field grants authority or closes work."""

    project_id: ProjectId
    mainline_ref: MainlineRef
    source_revision: RevisionDigest
    ready_for_recheck: tuple[MainlineTicketRef, ...]
    waiting: tuple[MainlineTicketRef, ...]
    incomplete_required: tuple[MainlineTicketRef, ...]
    closure_candidate: bool


def project_mainline_tickets(request: MainlineProjectionRequest) -> MainlineProjection:
    """Return candidate ticket references without dispatch, effects or formal closure."""

    completed = {
        ticket.ticket_ref
        for ticket in request.tickets
        if ticket.status is MainlineTicketStatus.COMPLETED
    }
    ready_for_recheck: list[MainlineTicketRef] = []
    waiting: list[MainlineTicketRef] = []
    incomplete_required: list[MainlineTicketRef] = []

    for ticket in request.tickets:
        is_complete = ticket.status is MainlineTicketStatus.COMPLETED
        dependencies_complete = all(dependency in completed for dependency in ticket.depends_on)

        if ticket.required and not is_complete:
            incomplete_required.append(ticket.ticket_ref)

        if ticket.status in (MainlineTicketStatus.PLANNED, MainlineTicketStatus.ADMITTED):
            if dependencies_complete:
                ready_for_recheck.append(ticket.ticket_ref)
            else:
                waiting.append(ticket.ticket_ref)
        elif ticket.status is MainlineTicketStatus.WAITING:
            waiting.append(ticket.ticket_ref)

    return MainlineProjection(
        project_id=request.project_id,
        mainline_ref=request.mainline_ref,
        source_revision=request.source_revision,
        ready_for_recheck=tuple(ready_for_recheck),
        waiting=tuple(waiting),
        incomplete_required=tuple(incomplete_required),
        closure_candidate=not incomplete_required,
    )
