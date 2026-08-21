"""P4: dispatch and integration each run as one path, and the gate is the door.

The upstream modules were complete and idle — every real integration was a
hand-typed merge. These cells pin the wiring: one dispatch path whose every
failure leaves whole books, one return-and-integrate path whose only exit
into `main` is `admit_document_mutation`, and failure codes that never fold.

The integration cells run against a real repository for the same reason the
gate's own tests do: the claim is "`main` did not move", and only a real
`main` can answer that.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import dispatch_session
from library.local_orchestration import document_mutation_gate
from library.local_orchestration import work_queue
from library.local_orchestration import worker_assignment
from library.local_orchestration.dispatch_authority import (
    admit_dispatch,
    create_dispatch_grant,
)
from library.local_orchestration.dispatch_session import (
    TicketResolution,
    WorkIntegrationFailure,
    WorkIntegrationRequest,
    WorkIntegrationStatus,
    WorkerDispatchFailure,
    WorkerDispatchRequest,
    WorkerDispatchResult,
    WorkerDispatchStatus,
    WorkerReturnFailure,
    WorkerReturnRequest,
    WorkerReturnStatus,
    WorkerSpawnStatus,
    dispatch_worker,
    integrate_next_work,
    record_worker_return,
)
from library.local_orchestration.document_mutation_gate import (
    DocumentMutationFailure,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.work_queue import (
    WorkEnqueueRequest,
    WorkEnqueueStatus,
    WorkItemLifecycle,
    WorkPullRequest,
    WorkSource,
    enqueue_work,
    pull_work,
    read_pending_work,
    read_work_queue,
)
from library.local_orchestration.worker_assignment import (
    AssignmentLifecycle,
    WorkerSettlementRequest,
    WorkerSettlementStatus,
    read_orphan_assignments,
    read_worker_assignments,
    settle_worker_assignment,
)
from library.workflow_router.live_dispatch_contracts import TicketReceipt
from tests.test_dispatch_authority import (
    _layout,
    _repository as _plain_repository,
    _request as _admission_request,
)
from tests.test_document_mutation_gate import (
    _TICKET,
    _commit,
    _repository as _git_repository,
    _run,
    _ticket_text,
    _write,
)

_WORKER = "worker-p4-cell-01"
_CONSUMER = "consumer-p4-main-01"


# ---------------------------------------------------------------------------
# Ports used as fixtures — including the fault-injection ones
# ---------------------------------------------------------------------------


class _RecordingSpawnPort:
    """A host that spawns successfully and remembers what it was handed."""

    def __init__(self) -> None:
        self.calls: list[tuple[TicketReceipt, worker_assignment.WorkerAssignment]] = []

    def spawn_worker(
        self,
        receipt: TicketReceipt,
        assignment: worker_assignment.WorkerAssignment,
    ) -> WorkerSpawnStatus:
        self.calls.append((receipt, assignment))
        return WorkerSpawnStatus.SPAWNED


class _FailingSpawnPort:
    def spawn_worker(self, receipt: object, assignment: object) -> WorkerSpawnStatus:
        return WorkerSpawnStatus.FAILED


class _RaisingSpawnPort:
    def spawn_worker(self, receipt: object, assignment: object) -> WorkerSpawnStatus:
        raise RuntimeError("the host fell over mid-spawn")


class _LedgerSabotagingSpawnPort:
    """Fails the spawn and breaks the assignment store before the compensation.

    The port callback is the one moment between the claim and the settlement,
    which makes it the only honest place to inject this fault.
    """

    def __init__(self, layout: JohnnyRootLayout) -> None:
        self._layout = layout

    def spawn_worker(self, receipt: object, assignment: object) -> WorkerSpawnStatus:
        worker_assignment.ledger_path(self._layout).write_text(
            "not a ledger", encoding="utf-8"
        )
        return WorkerSpawnStatus.FAILED


class _StaticResolver:
    def __init__(self, resolution: TicketResolution) -> None:
        self._resolution = resolution
        self.asked: list[str] = []

    def resolve_ticket(self, ticket_ref: str) -> TicketResolution | None:
        self.asked.append(ticket_ref)
        return self._resolution


class _NoneResolver:
    def resolve_ticket(self, ticket_ref: str) -> TicketResolution | None:
        return None


class _RaisingResolver:
    def resolve_ticket(self, ticket_ref: str) -> TicketResolution | None:
        raise RuntimeError("no map today")


class _TheftResolver:
    """Steals the head between the peek and the pull — the racing consumer."""

    def __init__(self, layout: JohnnyRootLayout) -> None:
        self._layout = layout

    def resolve_ticket(self, ticket_ref: str) -> TicketResolution | None:
        pull_work(
            self._layout, WorkPullRequest(consumer_ref="consumer-thief-01")
        )
        return TicketResolution(ticket_path=_TICKET, candidate_ref="candidate")


# ---------------------------------------------------------------------------
# Worlds
# ---------------------------------------------------------------------------


def _plain_world(base: Path) -> tuple[JohnnyRootLayout, Path]:
    """A granted layout and a bare repository directory: enough for the books."""

    layout = _layout(base)
    repository = _plain_repository(base)
    create_dispatch_grant(layout)
    return layout, repository


def _git_world(
    base: Path, *, modify: tuple[str, ...] = ("doc/",)
) -> tuple[JohnnyRootLayout, Path]:
    """A granted layout and a real repository whose `main` holds the ticket."""

    layout = _layout(base)
    root = _git_repository(base)
    (root / ".worktrees" / "w1").mkdir(parents=True)
    _write(root, _TICKET, _ticket_text(modify=modify))
    _write(root, "doc/existing.md", "before\n")
    _write(root, "library/untouchable.py", "keep\n")
    _commit(root, "baseline")
    create_dispatch_grant(layout)
    return layout, root


def _candidate(root: Path, relative: str, text: str) -> str:
    """One candidate branch carrying one change, with `main` left checked out."""

    _run(root, "checkout", "-q", "-b", "candidate")
    _write(root, relative, text)
    commit = _commit(root, "candidate work")
    _run(root, "checkout", "-q", "main")
    return commit


def _dispatched(
    layout: JohnnyRootLayout, repository: Path, port: _RecordingSpawnPort | None = None
) -> WorkerDispatchResult:
    result = dispatch_worker(
        layout,
        WorkerDispatchRequest(
            admission=_admission_request(repository), worker_ref=_WORKER
        ),
        port if port is not None else _RecordingSpawnPort(),
    )
    assert result.status is WorkerDispatchStatus.DISPATCHED, f"{result.failure}"
    assert result.receipt is not None and result.assignment is not None
    return result


def _return_request(dispatched: WorkerDispatchResult) -> WorkerReturnRequest:
    assert dispatched.receipt is not None and dispatched.assignment is not None
    return WorkerReturnRequest(
        claim_ref=dispatched.assignment.claim_id,
        receipt_ref=dispatched.receipt.receipt_id,
        ticket_ref=dispatched.receipt.ticket_reference,
    )


def _poison_queue(layout: JohnnyRootLayout) -> None:
    work_queue.queue_path(layout).write_text("not a queue", encoding="utf-8")


def _poison_ledger(layout: JohnnyRootLayout) -> None:
    worker_assignment.ledger_path(layout).write_text("not a ledger", encoding="utf-8")


# ---------------------------------------------------------------------------
# P4-R1: dispatch is one path, and every failure leaves whole books
# ---------------------------------------------------------------------------


class DispatchPathTests(unittest.TestCase):
    def test_one_call_issues_claims_and_spawns_in_order(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            port = _RecordingSpawnPort()

            result = _dispatched(layout, repository, port)

            assert result.receipt is not None and result.assignment is not None
            self.assertEqual(
                result.assignment.receipt_ref, result.receipt.receipt_id
            )
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertEqual(len(read.assignments), 1)
            self.assertIs(
                read.assignments[0].lifecycle, AssignmentLifecycle.CLAIMED
            )
            self.assertEqual(read.assignments[0].claim_id, result.assignment.claim_id)
            self.assertEqual(
                port.calls, [(result.receipt, result.assignment)]
            )
            queue = read_work_queue(layout)
            self.assertEqual(queue.items, ())

    def test_admission_refusal_leaves_no_claim_and_no_spawn(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)  # deliberately no grant
            repository = _plain_repository(base)
            port = _RecordingSpawnPort()

            result = dispatch_worker(
                layout,
                WorkerDispatchRequest(
                    admission=_admission_request(repository), worker_ref=_WORKER
                ),
                port,
            )

            self.assertIs(result.status, WorkerDispatchStatus.REFUSED)
            self.assertIs(result.failure, WorkerDispatchFailure.RECEIPT_REFUSED)
            self.assertEqual(result.upstream_failure, "DISPATCH_AUTHORITY_ABSENT")
            self.assertEqual(port.calls, [])
            read = read_worker_assignments(layout)
            self.assertEqual(read.assignments, ())

    def test_claim_refusal_spawns_nothing_and_is_named_apart(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            first = _dispatched(layout, repository)
            port = _RecordingSpawnPort()

            second = dispatch_worker(
                layout,
                WorkerDispatchRequest(
                    admission=_admission_request(repository),
                    worker_ref="worker-p4-cell-02",
                ),
                port,
            )

            self.assertIs(second.status, WorkerDispatchStatus.REFUSED)
            self.assertIs(second.failure, WorkerDispatchFailure.CLAIM_REFUSED)
            self.assertEqual(second.upstream_failure, "RECEIPT_ALREADY_CLAIMED")
            self.assertEqual(port.calls, [])
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertEqual(len(read.assignments), 1)
            assert first.assignment is not None
            self.assertEqual(read.assignments[0], first.assignment)

    def test_a_failed_spawn_settles_its_claim_and_leaves_no_orphan(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))

            result = dispatch_worker(
                layout,
                WorkerDispatchRequest(
                    admission=_admission_request(repository), worker_ref=_WORKER
                ),
                _FailingSpawnPort(),
            )

            self.assertIs(result.status, WorkerDispatchStatus.REFUSED)
            self.assertIs(result.failure, WorkerDispatchFailure.WORKER_SPAWN_FAILED)
            orphans = read_orphan_assignments(layout)
            self.assertEqual(orphans.assignments, ())
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertEqual(len(read.assignments), 1)
            self.assertIs(
                read.assignments[0].lifecycle, AssignmentLifecycle.SETTLED
            )

    def test_a_raising_spawn_port_fails_closed_identically(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))

            result = dispatch_worker(
                layout,
                WorkerDispatchRequest(
                    admission=_admission_request(repository), worker_ref=_WORKER
                ),
                _RaisingSpawnPort(),
            )

            self.assertIs(result.status, WorkerDispatchStatus.REFUSED)
            self.assertIs(result.failure, WorkerDispatchFailure.WORKER_SPAWN_FAILED)
            self.assertEqual(read_orphan_assignments(layout).assignments, ())

    def test_a_failed_compensation_is_named_apart_from_the_spawn_failure(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))

            result = dispatch_worker(
                layout,
                WorkerDispatchRequest(
                    admission=_admission_request(repository), worker_ref=_WORKER
                ),
                _LedgerSabotagingSpawnPort(layout),
            )

            self.assertIs(result.status, WorkerDispatchStatus.REFUSED)
            self.assertIs(
                result.failure, WorkerDispatchFailure.SPAWN_COMPENSATION_FAILED
            )
            self.assertEqual(result.upstream_failure, "STORAGE_UNAVAILABLE")


# ---------------------------------------------------------------------------
# P4-R2: a return settles then enqueues, and no failure leaves half a state
# ---------------------------------------------------------------------------


class WorkerReturnPathTests(unittest.TestCase):
    def test_a_return_settles_the_claim_and_queues_exactly_one_item(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)

            result = record_worker_return(layout, _return_request(dispatched))

            self.assertIs(result.status, WorkerReturnStatus.RECORDED)
            assert result.assignment is not None and result.item is not None
            self.assertIs(result.assignment.lifecycle, AssignmentLifecycle.SETTLED)
            self.assertIs(result.item.source, WorkSource.WORKER_RETURN)
            assert dispatched.assignment is not None
            self.assertEqual(result.item.origin_ref, dispatched.assignment.claim_id)
            assert dispatched.receipt is not None
            self.assertEqual(
                result.item.ticket_ref, dispatched.receipt.ticket_reference
            )
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)
            self.assertIs(queue.items[0].lifecycle, WorkItemLifecycle.PENDING)

    def test_a_second_return_is_refused_as_already_recorded(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            record_worker_return(layout, _return_request(dispatched))

            repeat = record_worker_return(layout, _return_request(dispatched))

            self.assertIs(repeat.status, WorkerReturnStatus.REFUSED)
            self.assertIs(
                repeat.failure, WorkerReturnFailure.RETURN_ALREADY_RECORDED
            )
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)

    def test_a_return_for_an_absent_claim_mutates_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _plain_world(Path(temporary))

            result = record_worker_return(
                layout,
                WorkerReturnRequest(
                    claim_ref="claim-p4-never-existed",
                    receipt_ref="receipt-vita-feature-001",
                    ticket_ref="ticket-vita-feature-001",
                ),
            )

            self.assertIs(result.status, WorkerReturnStatus.REFUSED)
            self.assertIs(result.failure, WorkerReturnFailure.RETURN_CLAIM_ABSENT)
            self.assertEqual(read_work_queue(layout).items, ())

    def test_a_return_with_the_wrong_receipt_leaves_the_claim_open(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            assert dispatched.assignment is not None

            result = record_worker_return(
                layout,
                WorkerReturnRequest(
                    claim_ref=dispatched.assignment.claim_id,
                    receipt_ref="receipt-vita-feature-999",
                    ticket_ref="ticket-vita-feature-001",
                ),
            )

            self.assertIs(result.status, WorkerReturnStatus.REFUSED)
            self.assertIs(
                result.failure, WorkerReturnFailure.RETURN_RECEIPT_MISMATCH
            )
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertIs(
                read.assignments[0].lifecycle, AssignmentLifecycle.CLAIMED
            )
            self.assertEqual(read_work_queue(layout).items, ())

    def test_an_unreadable_queue_refuses_before_any_settlement(self) -> None:
        """The half-state killer: the claim must still be open afterwards."""

        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            _poison_queue(layout)

            result = record_worker_return(layout, _return_request(dispatched))

            self.assertIs(result.status, WorkerReturnStatus.REFUSED)
            self.assertIs(result.failure, WorkerReturnFailure.QUEUE_UNAVAILABLE)
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertIs(
                read.assignments[0].lifecycle, AssignmentLifecycle.CLAIMED
            )

    def test_an_unreadable_ledger_refuses_before_any_enqueue(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            _poison_ledger(layout)

            result = record_worker_return(layout, _return_request(dispatched))

            self.assertIs(result.status, WorkerReturnStatus.REFUSED)
            self.assertIs(
                result.failure, WorkerReturnFailure.ASSIGNMENT_LEDGER_UNAVAILABLE
            )
            self.assertEqual(read_work_queue(layout).items, ())

    def test_an_interrupted_return_is_completed_not_duplicated(self) -> None:
        """Settled-but-never-queued is finished by the next call, exactly once."""

        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            assert dispatched.assignment is not None and dispatched.receipt is not None
            interrupted = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=dispatched.assignment.claim_id,
                    receipt_ref=dispatched.receipt.receipt_id,
                ),
            )
            self.assertIs(interrupted.status, WorkerSettlementStatus.SETTLED)

            result = record_worker_return(layout, _return_request(dispatched))

            self.assertIs(result.status, WorkerReturnStatus.RECORDED)
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)
            self.assertEqual(
                queue.items[0].origin_ref, dispatched.assignment.claim_id
            )

    def test_work_queued_without_a_settlement_is_surfaced_not_repaired(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            assert dispatched.assignment is not None
            enqueued = enqueue_work(
                layout,
                WorkEnqueueRequest.for_worker_return(
                    dispatched.assignment.claim_id, "ticket-vita-feature-001"
                ),
            )
            self.assertIs(enqueued.status, WorkEnqueueStatus.ENQUEUED)

            result = record_worker_return(layout, _return_request(dispatched))

            self.assertIs(result.status, WorkerReturnStatus.REFUSED)
            self.assertIs(
                result.failure, WorkerReturnFailure.RETURN_LEDGER_INCONSISTENT
            )
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertIs(
                read.assignments[0].lifecycle, AssignmentLifecycle.CLAIMED
            )

    def test_every_return_failure_carries_its_own_name(self) -> None:
        """Five induced failures, five different codes: the anti-folding pin."""

        codes: list[WorkerReturnFailure] = []
        for induce in (
            "queue-unreadable",
            "ledger-unreadable",
            "claim-absent",
            "receipt-mismatch",
            "duplicate-return",
        ):
            with TemporaryDirectory() as temporary:
                layout, repository = _plain_world(Path(temporary))
                dispatched = _dispatched(layout, repository)
                request = _return_request(dispatched)
                if induce == "queue-unreadable":
                    _poison_queue(layout)
                elif induce == "ledger-unreadable":
                    _poison_ledger(layout)
                elif induce == "claim-absent":
                    request = request.model_copy(
                        update={"claim_ref": "claim-p4-never-existed"}
                    )
                elif induce == "receipt-mismatch":
                    request = request.model_copy(
                        update={"receipt_ref": "receipt-vita-feature-999"}
                    )
                else:
                    record_worker_return(layout, request)
                result = record_worker_return(layout, request)
                self.assertIs(
                    result.status, WorkerReturnStatus.REFUSED, msg=induce
                )
                assert result.failure is not None
                codes.append(result.failure)
        self.assertEqual(len(set(codes)), len(codes), msg=f"{codes}")


# ---------------------------------------------------------------------------
# P4-R3: integration happens through the gate, and through nothing else
# ---------------------------------------------------------------------------


class IntegrationPathTests(unittest.TestCase):
    def _integration_request(self, root: Path) -> WorkIntegrationRequest:
        return WorkIntegrationRequest(
            consumer_ref=_CONSUMER,
            repository_root=str(root),
            integration_branch="main",
        )

    def test_a_full_round_trip_leaves_all_five_records(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, root = _git_world(base)
            candidate = _candidate(root, "doc/existing.md", "after\n")
            dispatched = _dispatched(layout, root)
            assert dispatched.assignment is not None
            returned = record_worker_return(layout, _return_request(dispatched))
            self.assertIs(returned.status, WorkerReturnStatus.RECORDED)

            result = integrate_next_work(
                layout,
                self._integration_request(root),
                _StaticResolver(
                    TicketResolution(ticket_path=_TICKET, candidate_ref="candidate")
                ),
            )

            self.assertIs(
                result.status, WorkIntegrationStatus.INTEGRATED, f"{result.failure}"
            )
            self.assertEqual(result.integrated_commit, candidate)

            # Record one: the claim, under the id the dispatch handed out.
            ledger = read_worker_assignments(layout)
            assert ledger.assignments is not None
            self.assertEqual(len(ledger.assignments), 1)
            self.assertEqual(
                ledger.assignments[0].claim_id, dispatched.assignment.claim_id
            )
            # Record two: the settlement of that same claim.
            self.assertIs(
                ledger.assignments[0].lifecycle, AssignmentLifecycle.SETTLED
            )
            # Records three and four: the item, enqueued and then pulled.
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)
            self.assertEqual(
                queue.items[0].origin_ref, dispatched.assignment.claim_id
            )
            self.assertIs(queue.items[0].lifecycle, WorkItemLifecycle.PULLED)
            self.assertEqual(queue.items[0].pulled_by_ref, _CONSUMER)
            # Record five: the integration, in the gate's own journal and on
            # the real `main`.
            lines = (
                document_mutation_gate.journal_path(layout)
                .read_text(encoding="utf-8")
                .splitlines()
            )
            last = json.loads(lines[-1])
            self.assertEqual(last["outcome"], "INTEGRATED")
            self.assertEqual(last["candidate_ref"], "candidate")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), candidate)

    def test_a_boundary_violating_candidate_never_reaches_main(self) -> None:
        """The wired path inherits the gate's guarantee: on refusal, no move."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, root = _git_world(base)
            before = _run(root, "rev-parse", "HEAD")
            _candidate(root, "library/untouchable.py", "changed\n")
            dispatched = _dispatched(layout, root)
            record_worker_return(layout, _return_request(dispatched))

            result = integrate_next_work(
                layout,
                self._integration_request(root),
                _StaticResolver(
                    TicketResolution(ticket_path=_TICKET, candidate_ref="candidate")
                ),
            )

            self.assertIs(result.status, WorkIntegrationStatus.REFUSED)
            self.assertIs(result.failure, WorkIntegrationFailure.GATE_REFUSED)
            self.assertIs(
                result.gate_failure,
                DocumentMutationFailure.MODIFICATION_OUTSIDE_BOUNDARY,
            )
            self.assertEqual(result.offending_path, "library/untouchable.py")
            self.assertEqual(_run(root, "rev-parse", "HEAD"), before)
            self.assertEqual(
                (root / "library" / "untouchable.py").read_text(encoding="utf-8"),
                "keep\n",
            )

    def test_an_empty_queue_is_a_named_empty_not_an_error(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, root = _plain_world(Path(temporary))

            result = integrate_next_work(
                layout,
                self._integration_request(root),
                _NoneResolver(),
            )

            self.assertIs(result.status, WorkIntegrationStatus.QUEUE_EMPTY)
            self.assertIsNone(result.failure)

    def test_an_unreadable_queue_is_never_reported_as_empty(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, root = _plain_world(Path(temporary))
            _poison_queue(layout)

            result = integrate_next_work(
                layout,
                self._integration_request(root),
                _NoneResolver(),
            )

            self.assertIs(result.status, WorkIntegrationStatus.REFUSED)
            self.assertIs(result.failure, WorkIntegrationFailure.QUEUE_UNAVAILABLE)

    def test_a_commit_trigger_at_the_head_is_deferred_untouched(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, root = _plain_world(Path(temporary))
            enqueued = enqueue_work(
                layout,
                WorkEnqueueRequest.for_commit_trigger(
                    "git_" + "a" * 40, "ticket-vita-feature-001"
                ),
            )
            self.assertIs(enqueued.status, WorkEnqueueStatus.ENQUEUED)

            result = integrate_next_work(
                layout,
                self._integration_request(root),
                _NoneResolver(),
            )

            self.assertIs(
                result.status, WorkIntegrationStatus.COMMIT_TRIGGER_PENDING
            )
            assert result.item is not None
            self.assertIs(result.item.source, WorkSource.COMMIT_TRIGGER)
            pending = read_pending_work(layout)
            assert pending.items is not None
            self.assertEqual(len(pending.items), 1)

    def test_an_unresolvable_ticket_consumes_nothing(self) -> None:
        for resolver in (_NoneResolver(), _RaisingResolver()):
            with self.subTest(resolver=type(resolver).__name__):
                with TemporaryDirectory() as temporary:
                    layout, repository = _plain_world(Path(temporary))
                    dispatched = _dispatched(layout, repository)
                    record_worker_return(layout, _return_request(dispatched))

                    result = integrate_next_work(
                        layout,
                        self._integration_request(repository),
                        resolver,
                    )

                    self.assertIs(result.status, WorkIntegrationStatus.REFUSED)
                    self.assertIs(
                        result.failure, WorkIntegrationFailure.TICKET_UNRESOLVED
                    )
                    pending = read_pending_work(layout)
                    assert pending.items is not None
                    self.assertEqual(len(pending.items), 1)

    def test_a_stolen_head_is_surfaced_not_judged_by_the_wrong_facts(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _plain_world(Path(temporary))
            dispatched = _dispatched(layout, repository)
            record_worker_return(layout, _return_request(dispatched))
            trigger = enqueue_work(
                layout,
                WorkEnqueueRequest.for_commit_trigger(
                    "git_" + "b" * 40, "ticket-vita-feature-001"
                ),
            )
            self.assertIs(trigger.status, WorkEnqueueStatus.ENQUEUED)

            result = integrate_next_work(
                layout,
                self._integration_request(repository),
                _TheftResolver(layout),
            )

            self.assertIs(result.status, WorkIntegrationStatus.REFUSED)
            self.assertIs(
                result.failure, WorkIntegrationFailure.PULLED_ITEM_MISMATCH
            )
            assert trigger.item is not None and result.item is not None
            self.assertEqual(result.item.item_id, trigger.item.item_id)


# ---------------------------------------------------------------------------
# P4-R4: there is no second path — pinned on the namespace, not the docs
# ---------------------------------------------------------------------------


class NoSecondPathTests(unittest.TestCase):
    """The module cannot reach Git or the stores except through the upstreams."""

    def setUp(self) -> None:
        self.source = Path(dispatch_session.__file__).read_text(encoding="utf-8")

    def test_the_module_holds_no_process_or_filesystem_capability(self) -> None:
        for name in ("subprocess", "os", "Popen", "pathlib", "shutil", "Path"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(dispatch_session, name))
        for token in (
            "subprocess",
            "Popen",
            "guarded_git",
            "windows_native_git_ref",
            "pathlib",
            "import os",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, self.source)

    def test_the_gate_entry_is_the_gate_itself(self) -> None:
        self.assertIs(
            dispatch_session.admit_document_mutation,
            document_mutation_gate.admit_document_mutation,
        )

    def test_every_upstream_entry_is_the_upstream_entry(self) -> None:
        import library.local_orchestration.dispatch_authority as authority

        for held, upstream in (
            (dispatch_session.admit_dispatch, admit_dispatch),
            (dispatch_session.admit_dispatch, authority.admit_dispatch),
            (
                dispatch_session.claim_worker_assignment,
                worker_assignment.claim_worker_assignment,
            ),
            (
                dispatch_session.settle_worker_assignment,
                worker_assignment.settle_worker_assignment,
            ),
            (dispatch_session.enqueue_work, work_queue.enqueue_work),
            (dispatch_session.pull_work, work_queue.pull_work),
        ):
            with self.subTest(entry=upstream.__name__):
                self.assertIs(held, upstream)

    def test_the_module_holds_no_issuance_surface(self) -> None:
        for name in (
            "IssuanceScopedDispatchBoundary",
            "issue_receipt",
            "register_artifact",
            "create_dispatch_grant",
        ):
            with self.subTest(name=name):
                self.assertFalse(hasattr(dispatch_session, name))
        self.assertNotIn("issuance_scoped_boundary", self.source)
        self.assertNotIn("create_dispatch_grant", self.source)

    def test_the_module_names_no_host(self) -> None:
        folded = self.source.casefold()
        for host in ("subagent", "claude", "codex", "antigravity", "gemini"):
            with self.subTest(host=host):
                self.assertNotIn(host, folded)


if __name__ == "__main__":
    unittest.main()
