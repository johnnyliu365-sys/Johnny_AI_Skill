"""P3: does the next thing to do survive the session being busy?

P2 recorded which ticket is in whose hands. What it still could not answer is
what happens to a worker's return that arrives while the control plane is in
the middle of something else. In a conversation the answer was "it is
mentioned, and then it is gone". This cell set is about the queue that catches
it instead.

The exactly-once cells use real processes rather than threads, for the reason
W5 paid to learn and P2 restated: threads share the interpreter's file
handles, so an in-process-only lock passes a threaded test and loses a genuine
race between two processes. A threaded version of the pull race below would go
green against an implementation with no file lock at all.

Every child pays its import cost, says `ready`, and blocks until the parent
releases all of them together. Without that gate each child would start
whenever its own interpreter finished importing, and that spread is tens of
milliseconds while the unprotected window inside a pull is one or two -- the
race would be decided by startup jitter rather than by the lock.

Nothing here sleeps, waits on a clock, or polls. A pull happens because a test
pulls, which is the whole consumer model: finish something, then ask.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from pydantic import ValidationError

from library.local_orchestration import dispatch_authority, work_queue
from library.local_orchestration import issuance_scoped_boundary
from library.local_orchestration import worker_assignment
from library.local_orchestration.issuance_scoped_boundary import (
    IssuanceScopedDispatchBoundary,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.work_queue import (
    WorkEnqueueFailure,
    WorkEnqueueRequest,
    WorkEnqueueStatus,
    WorkItemLifecycle,
    WorkPullFailure,
    WorkPullRequest,
    WorkPullResult,
    WorkPullStatus,
    WorkQueueReadStatus,
    WorkSource,
    enqueue_work,
    pull_work,
    queue_path,
    read_pending_work,
    read_work_queue,
)
from library.local_orchestration.worker_assignment import (
    WorkerClaimRequest,
    WorkerClaimResult,
    WorkerClaimStatus,
    WorkerSettlementRequest,
    WorkerSettlementStatus,
    claim_worker_assignment,
    settle_worker_assignment,
)
from tests.test_dispatch_authority import _layout, _repository
from tests.test_parallel_worker_dispatch import _HOST_NAMES

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_QUEUE_SOURCE = "library/local_orchestration/work_queue.py"

_A_COMMIT = "git_0123456789abcdef"
_B_COMMIT = "git_fedcba9876543210"

_PULL_CHILD = '''\
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.work_queue import WorkPullRequest, pull_work

layout = JohnnyRootLayout(base=Path(sys.argv[2]))
request = WorkPullRequest(consumer_ref=sys.argv[3])

# Pay the import cost, say so, then block until released. Blocking on a pipe
# is a blocking read, not a poll and not a timer.
print("ready", flush=True)
sys.stdin.readline()

result = pull_work(layout, request)
print(
    json.dumps(
        {
            "status": result.status.value,
            "failure": None if result.failure is None else result.failure.value,
            "item_id": None if result.item is None else result.item.item_id,
            "origin_ref": None if result.item is None else result.item.origin_ref,
            "sequence": None if result.item is None else result.item.sequence,
        }
    ),
    flush=True,
)
'''

_ENQUEUE_CHILD = '''\
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.work_queue import WorkEnqueueRequest, enqueue_work

layout = JohnnyRootLayout(base=Path(sys.argv[2]))
request = WorkEnqueueRequest.for_worker_return(sys.argv[3], "ticket-shared")

print("ready", flush=True)
sys.stdin.readline()

result = enqueue_work(layout, request)
print(
    json.dumps(
        {
            "status": result.status.value,
            "failure": None if result.failure is None else result.failure.value,
            "origin_ref": None if result.item is None else result.item.origin_ref,
            "sequence": None if result.item is None else result.item.sequence,
        }
    ),
    flush=True,
)
'''


def _race_children(
    script: Path, layout: JohnnyRootLayout, tails: tuple[str, ...], workspace: Path
) -> list[dict[str, object]]:
    """Act from genuinely separate processes released at the same instant.

    Each child is rooted in the temporary tree and never inside the checkout:
    governance 03 recorded that a concurrent process standing in the checkout
    can block a runtime lease teardown on Windows and poison later runs.
    """

    processes = [
        subprocess.Popen(
            (
                sys.executable,
                str(script),
                str(_REPOSITORY_ROOT),
                str(layout.base),
                tail,
            ),
            cwd=str(workspace),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        for tail in tails
    ]
    try:
        for process in processes:
            assert process.stdout is not None
            if process.stdout.readline().strip() != "ready":
                raise AssertionError(
                    "child never became ready: "
                    + (process.stderr.read() if process.stderr else "")
                )
        for process in processes:
            assert process.stdin is not None
            process.stdin.write("go\n")
            process.stdin.flush()
        verdicts: list[dict[str, object]] = []
        for process in processes:
            body, errors = process.communicate(timeout=180)
            lines = [line for line in body.splitlines() if line.strip()]
            if not lines:
                raise AssertionError("child produced no verdict: " + errors)
            verdicts.append(json.loads(lines[-1]))
        return verdicts
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.wait()


def _seed(temporary: str) -> tuple[JohnnyRootLayout, Path]:
    base = Path(temporary).resolve()
    return _layout(base), _repository(base)


def _return_request(
    origin: str = "claim-aaa", ticket: str = "ticket-aaa"
) -> WorkEnqueueRequest:
    return WorkEnqueueRequest.for_worker_return(origin, ticket)


def _commit_request(
    origin: str = _A_COMMIT, ticket: str = "ticket-bbb"
) -> WorkEnqueueRequest:
    return WorkEnqueueRequest.for_commit_trigger(origin, ticket)


def _pull(
    layout: JohnnyRootLayout, consumer: str = "consumer-main"
) -> WorkPullResult:
    return pull_work(layout, WorkPullRequest(consumer_ref=consumer))


class EnqueueReadbackTests(unittest.TestCase):
    """P3-R1: both admitted sources land, and land with the fields they carried."""

    def test_a_worker_return_enqueues_and_reads_back_field_for_field(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)

            result = enqueue_work(layout, _return_request())
            self.assertIs(result.status, WorkEnqueueStatus.ENQUEUED, f"{result.failure}")
            assert result.item is not None

            read = read_work_queue(layout)
            self.assertIs(read.status, WorkQueueReadStatus.READ)
            assert read.items is not None
            self.assertEqual(len(read.items), 1)
            stored = read.items[0]
            self.assertEqual(stored, result.item)
            self.assertIs(stored.source, WorkSource.WORKER_RETURN)
            self.assertEqual(stored.origin_ref, "claim-aaa")
            self.assertEqual(stored.ticket_ref, "ticket-aaa")
            self.assertIs(stored.lifecycle, WorkItemLifecycle.PENDING)
            self.assertIsNone(stored.pulled_by_ref)

    def test_a_commit_trigger_enqueues_and_reads_back_field_for_field(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)

            result = enqueue_work(layout, _commit_request())
            self.assertIs(result.status, WorkEnqueueStatus.ENQUEUED, f"{result.failure}")
            assert result.item is not None
            self.assertIs(result.item.source, WorkSource.COMMIT_TRIGGER)
            self.assertEqual(result.item.origin_ref, _A_COMMIT)
            self.assertEqual(result.item.ticket_ref, "ticket-bbb")

    def test_both_sources_coexist_on_one_queue(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            enqueue_work(layout, _commit_request())

            read = read_work_queue(layout)
            assert read.items is not None
            self.assertEqual(
                [item.source for item in read.items],
                [WorkSource.WORKER_RETURN, WorkSource.COMMIT_TRIGGER],
            )

    def test_the_queued_work_survives_a_process_that_never_saw_the_enqueue(self) -> None:
        """The actual break: a return must outlive whoever wrote it down."""

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())

            reopened = JohnnyRootLayout(base=layout.base)
            read = read_work_queue(reopened)
            self.assertIs(read.status, WorkQueueReadStatus.READ)
            assert read.items is not None
            self.assertEqual([item.origin_ref for item in read.items], ["claim-aaa"])

    def test_a_settled_assignment_is_an_admissible_enqueue_source(self) -> None:
        """Source one, end to end, with the wiring done by the caller.

        The queue never imports the assignment ledger; it takes the claim
        reference as an opaque string. This cell does the joining a wiring
        layer would do, so the source is proven without the module acquiring
        the capability.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(
                layout,
                WorkerClaimRequest(
                    receipt_ref="receipt-aaa",
                    worker_ref="worker-one",
                    worktree_ref="worktree-aaa-01",
                    branch_ref="branch-aaa-01",
                    repository_root=str(repository),
                    host_worktree_path=str(repository / ".worktrees" / "w1"),
                ),
            )
            self.assertIs(claimed.status, WorkerClaimStatus.CLAIMED, f"{claimed.failure}")
            assert claimed.assignment is not None
            settled = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )
            self.assertIs(settled.status, WorkerSettlementStatus.SETTLED)

            enqueued = enqueue_work(
                layout,
                WorkEnqueueRequest.for_worker_return(
                    claimed.assignment.claim_id, "ticket-aaa"
                ),
            )
            self.assertIs(
                enqueued.status, WorkEnqueueStatus.ENQUEUED, f"{enqueued.failure}"
            )

            pulled = _pull(layout)
            self.assertIs(pulled.status, WorkPullStatus.PULLED, f"{pulled.failure}")
            assert pulled.item is not None
            self.assertEqual(pulled.item.origin_ref, claimed.assignment.claim_id)


class PullDeliveryTests(unittest.TestCase):
    """P3-R1: what was enqueued is what comes back, and it comes back once."""

    def test_a_pull_returns_the_item_with_the_fields_it_was_enqueued_with(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueued = enqueue_work(layout, _return_request())
            assert enqueued.item is not None

            pulled = _pull(layout)
            self.assertIs(pulled.status, WorkPullStatus.PULLED, f"{pulled.failure}")
            assert pulled.item is not None
            self.assertEqual(pulled.item.item_id, enqueued.item.item_id)
            self.assertEqual(pulled.item.origin_ref, enqueued.item.origin_ref)
            self.assertEqual(pulled.item.ticket_ref, enqueued.item.ticket_ref)
            self.assertIs(pulled.item.source, enqueued.item.source)
            self.assertEqual(pulled.item.sequence, enqueued.item.sequence)

    def test_a_pull_records_who_took_it_and_flips_the_lifecycle(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())

            pulled = _pull(layout, "consumer-session")
            assert pulled.item is not None
            self.assertIs(pulled.item.lifecycle, WorkItemLifecycle.PULLED)
            self.assertEqual(pulled.item.pulled_by_ref, "consumer-session")

            read = read_work_queue(layout)
            assert read.items is not None
            self.assertIs(read.items[0].lifecycle, WorkItemLifecycle.PULLED)
            self.assertEqual(read.items[0].pulled_by_ref, "consumer-session")

    def test_a_pulled_item_is_not_handed_out_a_second_time(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())

            first = _pull(layout)
            second = _pull(layout)
            self.assertIs(first.status, WorkPullStatus.PULLED)
            self.assertIs(second.status, WorkPullStatus.EMPTY)
            self.assertIsNone(second.item, "a drained queue must not repeat itself")

    def test_pending_work_excludes_what_has_already_been_taken(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            enqueue_work(layout, _commit_request())
            _pull(layout)

            pending = read_pending_work(layout)
            self.assertIs(pending.status, WorkQueueReadStatus.READ)
            assert pending.items is not None
            self.assertEqual([item.origin_ref for item in pending.items], [_A_COMMIT])

            full = read_work_queue(layout)
            assert full.items is not None
            self.assertEqual(len(full.items), 2, "a taken item stays on the record")


class DeclaredOrderTests(unittest.TestCase):
    """The order is a field, declared and recorded, not whatever the file holds.

    The declared order is admission order across both sources: strict FIFO on
    a `sequence` assigned inside the same exclusive lock that serialises the
    write. The alternative considered was priority by source -- worker returns
    before commit triggers -- and it was rejected because it can starve, and a
    return that is postponed forever has vanished in every sense the ticket
    cares about.
    """

    def test_items_come_back_in_admission_order_across_both_sources(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _commit_request(_A_COMMIT, "ticket-one"))
            enqueue_work(layout, _return_request("claim-bbb", "ticket-two"))
            enqueue_work(layout, _commit_request(_B_COMMIT, "ticket-three"))

            taken = [_pull(layout), _pull(layout), _pull(layout)]
            for result in taken:
                self.assertIs(result.status, WorkPullStatus.PULLED, f"{result.failure}")
            self.assertEqual(
                [result.item.ticket_ref for result in taken if result.item],
                ["ticket-one", "ticket-two", "ticket-three"],
                "neither source may overtake the other; admission order decides",
            )

    def test_the_sequence_is_strictly_increasing_and_starts_at_one(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request("claim-aaa"))
            enqueue_work(layout, _return_request("claim-bbb"))
            enqueue_work(layout, _return_request("claim-ccc"))

            read = read_work_queue(layout)
            assert read.items is not None
            self.assertEqual([item.sequence for item in read.items], [1, 2, 3])

    def test_pull_order_follows_the_recorded_sequence_not_the_file_order(self) -> None:
        """The cell that separates a declared order from an accidental one.

        The stored array is reversed on disk while the sequence numbers are
        left alone. An implementation that hands out `items[0]` passes every
        other ordering cell in this file and fails here.
        """

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request("claim-aaa", "ticket-one"))
            enqueue_work(layout, _return_request("claim-bbb", "ticket-two"))
            enqueue_work(layout, _return_request("claim-ccc", "ticket-three"))

            stored = json.loads(queue_path(layout).read_text(encoding="utf-8"))
            stored["items"] = list(reversed(stored["items"]))
            queue_path(layout).write_text(json.dumps(stored), encoding="utf-8")

            taken = [_pull(layout), _pull(layout), _pull(layout)]
            self.assertEqual(
                [result.item.ticket_ref for result in taken if result.item],
                ["ticket-one", "ticket-two", "ticket-three"],
                "order must come from the sequence field, not the array position",
            )

    def test_the_order_survives_a_reader_that_never_saw_the_enqueues(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request("claim-aaa", "ticket-one"))
            enqueue_work(layout, _commit_request(_A_COMMIT, "ticket-two"))

            reopened = JohnnyRootLayout(base=layout.base)
            pending = read_pending_work(reopened)
            assert pending.items is not None
            self.assertEqual(
                [item.ticket_ref for item in pending.items], ["ticket-one", "ticket-two"]
            )


class CrossProcessPullTests(unittest.TestCase):
    """P3-R2: exactly once, proven between real processes.

    Threads would share this interpreter's file handles. Two processes do not,
    which is the only arrangement in which a missing OS-level lock can fail.
    """

    def test_one_item_pulled_from_four_processes_is_delivered_exactly_once(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            base = Path(temporary).resolve()
            script = base / "pull_child.py"
            script.write_text(_PULL_CHILD, encoding="utf-8")
            enqueue_work(layout, _return_request())

            results = _race_children(
                script,
                layout,
                ("consumer-a", "consumer-b", "consumer-c", "consumer-d"),
                base,
            )

            self.assertEqual(len(results), 4, "every child must produce a verdict")
            pulled = [
                item for item in results if item["status"] == WorkPullStatus.PULLED.value
            ]
            empty = [
                item for item in results if item["status"] == WorkPullStatus.EMPTY.value
            ]
            self.assertEqual(
                len(pulled), 1, f"exactly one process may take the item: {results}"
            )
            self.assertEqual(
                len(empty),
                3,
                f"a loser must find the queue empty, not error: {results}",
            )
            for item in empty:
                with self.subTest(failure=item["failure"]):
                    self.assertIsNone(
                        item["failure"],
                        "losing a race is not a storage failure",
                    )

            read = read_work_queue(layout)
            assert read.items is not None
            self.assertEqual(len(read.items), 1)
            self.assertIs(read.items[0].lifecycle, WorkItemLifecycle.PULLED)
            self.assertEqual(read.items[0].item_id, pulled[0]["item_id"])

    def test_four_processes_pulling_four_items_share_nothing_and_lose_nothing(
        self,
    ) -> None:
        """The lost-update shape, which one item cannot expose.

        Without an OS-level lock every child reads the same queue, every child
        picks the same head, and the writes overwrite one another: the same
        item is delivered several times and the rest are silently still
        pending. Four items and four pullers make both halves visible.
        """

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            base = Path(temporary).resolve()
            script = base / "pull_child.py"
            script.write_text(_PULL_CHILD, encoding="utf-8")
            for origin in ("claim-aaa", "claim-bbb", "claim-ccc", "claim-ddd"):
                enqueue_work(layout, _return_request(origin))

            results = _race_children(
                script,
                layout,
                ("consumer-a", "consumer-b", "consumer-c", "consumer-d"),
                base,
            )

            for item in results:
                with self.subTest(status=item["status"]):
                    self.assertEqual(
                        item["status"],
                        WorkPullStatus.PULLED.value,
                        f"four pullers and four items must all be served: {results}",
                    )
            delivered = [item["origin_ref"] for item in results]
            self.assertEqual(
                len(set(delivered)),
                4,
                f"no item may be delivered to two processes: {results}",
            )

            read = read_work_queue(layout)
            assert read.items is not None
            self.assertEqual(
                sorted(item.lifecycle.value for item in read.items),
                [WorkItemLifecycle.PULLED.value] * 4,
                "nothing may be left pending once every puller was served",
            )

    def test_four_processes_enqueueing_at_once_lose_no_return(self) -> None:
        """A return that is overwritten by a concurrent enqueue has vanished.

        This is the same lost update seen from the writing side, and it is the
        exact failure the ticket forbids: the return disappeared because
        somebody else was busy at that instant.
        """

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            base = Path(temporary).resolve()
            script = base / "enqueue_child.py"
            script.write_text(_ENQUEUE_CHILD, encoding="utf-8")
            origins = ("claim-aaa", "claim-bbb", "claim-ccc", "claim-ddd")

            results = _race_children(script, layout, origins, base)

            for item in results:
                with self.subTest(origin=item["origin_ref"]):
                    self.assertEqual(
                        item["status"],
                        WorkEnqueueStatus.ENQUEUED.value,
                        f"{results}",
                    )
            read = read_work_queue(layout)
            assert read.items is not None
            self.assertEqual(
                sorted(item.origin_ref for item in read.items),
                sorted(origins),
                f"every concurrent return must survive: {results}",
            )
            self.assertEqual(
                len({item.sequence for item in read.items}),
                4,
                "two concurrent admissions may not share one position",
            )


class DuplicateOriginTests(unittest.TestCase):
    """One cause, one piece of work. A repeat is refused, not folded away."""

    def test_the_same_origin_twice_is_refused_by_name(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            first = enqueue_work(layout, _return_request())
            second = enqueue_work(layout, _return_request())

            self.assertIs(first.status, WorkEnqueueStatus.ENQUEUED)
            self.assertIs(second.status, WorkEnqueueStatus.REFUSED)
            self.assertIs(second.failure, WorkEnqueueFailure.ORIGIN_ALREADY_QUEUED)
            self.assertIsNone(second.item)

    def test_the_refused_repeat_does_not_displace_the_first(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            first = enqueue_work(layout, _return_request("claim-aaa", "ticket-one"))
            enqueue_work(layout, _return_request("claim-aaa", "ticket-two"))

            read = read_work_queue(layout)
            assert read.items is not None and first.item is not None
            self.assertEqual(len(read.items), 1)
            self.assertEqual(read.items[0], first.item)
            self.assertEqual(read.items[0].ticket_ref, "ticket-one")

    def test_a_repeat_is_still_refused_after_the_first_was_pulled(self) -> None:
        """Otherwise a finished piece of work reappears and is done twice."""

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            _pull(layout)
            repeat = enqueue_work(layout, _return_request())
            self.assertIs(repeat.failure, WorkEnqueueFailure.ORIGIN_ALREADY_QUEUED)

    def test_two_different_origins_each_get_their_own_item(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            first = enqueue_work(layout, _return_request("claim-aaa"))
            second = enqueue_work(layout, _return_request("claim-bbb"))
            assert first.item is not None and second.item is not None
            self.assertNotEqual(first.item.item_id, second.item.item_id)
            self.assertNotEqual(first.item.sequence, second.item.sequence)


class SourceNamingTests(unittest.TestCase):
    """Defect class 5: an origin that does not belong to its source is named.

    The two admitted namespaces are disjoint by construction -- a commit
    digest carries an underscore that an opaque reference forbids, and an
    opaque reference has no `git_` prefix -- so a swap is detectable rather
    than merely implausible.
    """

    def test_a_commit_digest_offered_as_a_worker_return_is_refused_by_name(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            result = enqueue_work(
                layout, WorkEnqueueRequest.for_worker_return(_A_COMMIT, "ticket-aaa")
            )
            self.assertIs(result.status, WorkEnqueueStatus.REFUSED)
            self.assertIs(result.failure, WorkEnqueueFailure.ORIGIN_SOURCE_MISMATCH)
            self.assertIsNone(result.item)

    def test_a_claim_reference_offered_as_a_commit_trigger_is_refused_by_name(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            result = enqueue_work(
                layout, WorkEnqueueRequest.for_commit_trigger("claim-aaa", "ticket-aaa")
            )
            self.assertIs(result.failure, WorkEnqueueFailure.ORIGIN_SOURCE_MISMATCH)

    def test_a_mismatched_source_writes_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(
                layout, WorkEnqueueRequest.for_worker_return(_A_COMMIT, "ticket-aaa")
            )
            read = read_work_queue(layout)
            self.assertEqual(read.items, ())

    def test_a_source_outside_the_two_admitted_ones_never_builds_a_request(self) -> None:
        with self.assertRaises(ValidationError):
            WorkEnqueueRequest(
                source="SOMETHING_ELSE",  # type: ignore[arg-type]
                origin_ref="claim-aaa",
                ticket_ref="ticket-aaa",
            )

    def test_mismatch_and_duplicate_are_different_names(self) -> None:
        self.assertIsNot(
            WorkEnqueueFailure.ORIGIN_SOURCE_MISMATCH,
            WorkEnqueueFailure.ORIGIN_ALREADY_QUEUED,
        )
        self.assertIsNot(
            WorkEnqueueFailure.ORIGIN_SOURCE_MISMATCH,
            WorkEnqueueFailure.STORAGE_UNAVAILABLE,
        )


class StorageFailClosedTests(unittest.TestCase):
    """P3-R3, the rule the ticket says decides success.

    A queue that cannot be read is not an empty queue. Folding the two
    together stops the main session silently and emits no signal at all.
    """

    def test_an_unreadable_queue_pulls_as_a_named_refusal_and_never_as_empty(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            queue_path(layout).write_text("{not json at all", encoding="utf-8")

            result = _pull(layout)
            self.assertIs(result.status, WorkPullStatus.REFUSED)
            self.assertIs(result.failure, WorkPullFailure.STORAGE_UNAVAILABLE)
            self.assertIsNot(
                result.status,
                WorkPullStatus.EMPTY,
                "an unreadable queue reported as empty is the false green",
            )
            self.assertIsNone(result.item)

    def test_an_unreadable_queue_reads_as_a_named_failure_not_as_empty(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            queue_path(layout).write_text("{not json at all", encoding="utf-8")

            read = read_work_queue(layout)
            self.assertIs(read.status, WorkQueueReadStatus.STORAGE_UNAVAILABLE)
            self.assertIsNone(
                read.items, "an unreadable queue must not present as an empty one"
            )

    def test_an_unreadable_queue_hides_no_pending_work(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            queue_path(layout).write_text("{not json at all", encoding="utf-8")

            pending = read_pending_work(layout)
            self.assertIs(pending.status, WorkQueueReadStatus.STORAGE_UNAVAILABLE)
            self.assertIsNone(
                pending.items,
                "reporting 'nothing to do' from a broken queue is the false green",
            )

    def test_an_enqueue_against_a_broken_queue_refuses_and_overwrites_nothing(
        self,
    ) -> None:
        """If a broken queue let a fresh write through, the work already
        queued would be erased in the same write that hid the evidence."""

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            corrupt = "{not json at all"
            queue_path(layout).write_text(corrupt, encoding="utf-8")

            result = enqueue_work(layout, _return_request("claim-bbb"))
            self.assertIs(result.status, WorkEnqueueStatus.REFUSED)
            self.assertIs(result.failure, WorkEnqueueFailure.STORAGE_UNAVAILABLE)
            self.assertEqual(
                queue_path(layout).read_text(encoding="utf-8"),
                corrupt,
                "a refusal must not rewrite the queue it could not read",
            )

    def test_a_pull_against_a_broken_queue_overwrites_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            corrupt = "{not json at all"
            queue_path(layout).write_text(corrupt, encoding="utf-8")

            _pull(layout)
            self.assertEqual(queue_path(layout).read_text(encoding="utf-8"), corrupt)

    def test_a_wrong_schema_queue_refuses_rather_than_being_reinterpreted(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            queue_path(layout).write_text(
                json.dumps({"schema_revision": "work-queue-v2"}), encoding="utf-8"
            )
            self.assertIs(
                read_work_queue(layout).status, WorkQueueReadStatus.STORAGE_UNAVAILABLE
            )
            self.assertIs(_pull(layout).failure, WorkPullFailure.STORAGE_UNAVAILABLE)

    def test_a_record_whose_origin_contradicts_its_source_is_a_storage_failure(
        self,
    ) -> None:
        """The durable invariant, checked on the way in as well as out."""

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            stored = json.loads(queue_path(layout).read_text(encoding="utf-8"))
            stored["items"][0]["source"] = WorkSource.COMMIT_TRIGGER.value
            queue_path(layout).write_text(json.dumps(stored), encoding="utf-8")

            self.assertIs(
                read_work_queue(layout).status, WorkQueueReadStatus.STORAGE_UNAVAILABLE
            )
            self.assertIs(_pull(layout).failure, WorkPullFailure.STORAGE_UNAVAILABLE)

    def test_two_records_sharing_one_position_are_a_storage_failure(self) -> None:
        """A duplicated sequence would make the declared order ambiguous."""

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request("claim-aaa"))
            enqueue_work(layout, _return_request("claim-bbb"))
            stored = json.loads(queue_path(layout).read_text(encoding="utf-8"))
            stored["items"][1]["sequence"] = stored["items"][0]["sequence"]
            queue_path(layout).write_text(json.dumps(stored), encoding="utf-8")

            self.assertIs(
                read_work_queue(layout).status, WorkQueueReadStatus.STORAGE_UNAVAILABLE
            )

    def test_a_directory_where_the_queue_belongs_is_a_storage_failure(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            queue_path(layout).mkdir(parents=True)

            self.assertIs(
                read_work_queue(layout).status, WorkQueueReadStatus.STORAGE_UNAVAILABLE
            )
            self.assertIs(
                enqueue_work(layout, _return_request()).failure,
                WorkEnqueueFailure.STORAGE_UNAVAILABLE,
            )
            self.assertIs(_pull(layout).failure, WorkPullFailure.STORAGE_UNAVAILABLE)


class InvariantViolationTests(unittest.TestCase):
    """Governance 16: the queue's own rule failing is not the disk failing.

    `enqueue_work` only ever checks `origin_ref` explicitly before committing;
    `item_id` has no explicit check anywhere because it is generated fresh by
    this module and assumed never to collide. Forcing that assumption to fail
    (rather than weakening the origin_ref check, which would remove real
    defense and duplicate `DuplicateOriginTests`) reaches the same second line
    of defense the P5 review's sibling defect described in P2 hits here too:
    `_WorkLedger.identities_and_positions_are_unique`.
    """

    def test_an_item_id_collision_is_named_as_an_invariant_not_as_storage(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request("claim-aaa"))

            with patch(
                "library.local_orchestration.work_queue.uuid.uuid4",
                return_value=uuid.UUID(int=0),
            ):
                first = enqueue_work(layout, _return_request("claim-bbb"))
                second = enqueue_work(layout, _return_request("claim-ccc"))

            self.assertIs(first.status, WorkEnqueueStatus.ENQUEUED, f"{first.failure}")
            self.assertIs(second.status, WorkEnqueueStatus.REFUSED)
            self.assertIs(
                second.failure, WorkEnqueueFailure.QUEUE_INVARIANT_VIOLATED
            )
            self.assertIsNot(
                second.failure,
                WorkEnqueueFailure.STORAGE_UNAVAILABLE,
                "a rule the queue enforces on itself is not a disk problem",
            )

    def test_an_invariant_violation_still_fails_closed_and_writes_nothing(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request("claim-aaa"))

            with patch(
                "library.local_orchestration.work_queue.uuid.uuid4",
                return_value=uuid.UUID(int=0),
            ):
                enqueue_work(layout, _return_request("claim-bbb"))
                before = queue_path(layout).read_text(encoding="utf-8")
                refused = enqueue_work(layout, _return_request("claim-ccc"))
                after = queue_path(layout).read_text(encoding="utf-8")

            self.assertIs(refused.status, WorkEnqueueStatus.REFUSED)
            self.assertEqual(
                before, after, "a refused write must not partially land"
            )


class EmptyAndAbsentTests(unittest.TestCase):
    """Defect class 2: absence, emptiness and unreadability stay three things."""

    def test_a_queue_nobody_wrote_to_pulls_as_empty(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            result = _pull(layout)
            self.assertIs(result.status, WorkPullStatus.EMPTY)
            self.assertIsNone(result.item)
            self.assertIsNone(
                result.failure, "nothing to do is a fact, not a failure"
            )

    def test_a_queue_nobody_wrote_to_reads_as_an_empty_success(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            read = read_work_queue(layout)
            self.assertIs(read.status, WorkQueueReadStatus.READ)
            self.assertEqual(read.items, ())
            self.assertIsNotNone(
                read.items, "no queued work is a successful read, not a failed one"
            )

    def test_empty_and_unreadable_are_two_distinguishable_results(self) -> None:
        """The distinction the whole ticket rests on, asserted directly."""

        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            empty = _pull(layout)
            queue_path(layout).write_text("{not json at all", encoding="utf-8")
            unreadable = _pull(layout)

            self.assertNotEqual(empty.status, unreadable.status)
            self.assertNotEqual(empty, unreadable)
            self.assertIsNone(empty.failure)
            self.assertIsNotNone(unreadable.failure)

    def test_a_refusal_can_never_carry_an_item(self) -> None:
        with self.assertRaises(ValidationError):
            work_queue.WorkPullResult(
                status=WorkPullStatus.REFUSED,
                failure=WorkPullFailure.STORAGE_UNAVAILABLE,
                item=work_queue.WorkItem(
                    item_id="work-aaa",
                    sequence=1,
                    source=WorkSource.WORKER_RETURN,
                    origin_ref="claim-aaa",
                    ticket_ref="ticket-aaa",
                    lifecycle=WorkItemLifecycle.PENDING,
                ),
            )

    def test_an_empty_result_can_never_carry_a_failure(self) -> None:
        with self.assertRaises(ValidationError):
            work_queue.WorkPullResult(
                status=WorkPullStatus.EMPTY,
                failure=WorkPullFailure.STORAGE_UNAVAILABLE,
            )

    def test_an_empty_origin_never_reaches_the_store(self) -> None:
        with self.assertRaises(ValidationError):
            WorkEnqueueRequest.for_worker_return("", "ticket-aaa")

    def test_an_empty_ticket_reference_never_reaches_the_store(self) -> None:
        with self.assertRaises(ValidationError):
            WorkEnqueueRequest.for_worker_return("claim-aaa", "")

    def test_an_empty_consumer_reference_never_reaches_the_store(self) -> None:
        with self.assertRaises(ValidationError):
            WorkPullRequest(consumer_ref="")

    def test_a_foreign_request_object_is_refused_as_invalid(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueued = enqueue_work(layout, object())  # type: ignore[arg-type]
            self.assertIs(enqueued.status, WorkEnqueueStatus.REFUSED)
            self.assertIs(enqueued.failure, WorkEnqueueFailure.REQUEST_INVALID)

            pulled = pull_work(layout, object())  # type: ignore[arg-type]
            self.assertIs(pulled.status, WorkPullStatus.REFUSED)
            self.assertIs(pulled.failure, WorkPullFailure.REQUEST_INVALID)

    def test_a_pull_request_is_not_accepted_in_place_of_an_enqueue_request(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            result = enqueue_work(layout, WorkPullRequest(consumer_ref="consumer-a"))  # type: ignore[arg-type]
            self.assertIs(result.failure, WorkEnqueueFailure.REQUEST_INVALID)


class OpaqueRecordTests(unittest.TestCase):
    """References stay opaque: no locator may enter the queue."""

    def test_a_path_shaped_origin_is_refused(self) -> None:
        for origin in ("claim/aaa", "claim\\aaa", "file://claim"):
            with self.subTest(origin=origin):
                with self.assertRaises(ValidationError):
                    WorkEnqueueRequest.for_worker_return(origin, "ticket-aaa")

    def test_a_path_shaped_ticket_reference_is_refused(self) -> None:
        with self.assertRaises(ValidationError):
            WorkEnqueueRequest.for_worker_return(
                "claim-aaa", "modules/tickets/p3-work-queue.md"
            )


class NoClockTests(unittest.TestCase):
    """Nothing here fires, and nothing here can be turned into something that does.

    The position field is an integer that answers "which came first" and
    cannot answer "how old is this", so no expiry rule can be built on it
    without changing the schema in the open.
    """

    def test_nothing_in_the_record_carries_a_clock(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            enqueue_work(layout, _return_request())
            stored = json.loads(queue_path(layout).read_text(encoding="utf-8"))
            for record in stored["items"]:
                for field in record:
                    with self.subTest(field=field):
                        self.assertNotIn("at_utc", field)
                        self.assertNotIn("time", field)
                        self.assertNotIn("_ms", field)
                        self.assertNotIn("deadline", field)
                        self.assertNotIn("expire", field)

    def test_the_module_reads_no_clock_and_starts_nothing(self) -> None:
        body = (_REPOSITORY_ROOT / _QUEUE_SOURCE).read_text(encoding="utf-8")
        for marker in (
            "import time",
            "from time import",
            "import datetime",
            "from datetime import",
            "monotonic",
            "perf_counter",
            "sleep",
            "import sched",
            "import asyncio",
            "Timer(",
            "Thread(",
            "start()",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, body)


class CapabilitySeparationTests(unittest.TestCase):
    """Defect class 3: the queue schedules work and holds no other authority.

    Asserted by object identity rather than by searching the source for names.
    A substring check passes for `admit_dispatch_v2` and fails for a comment,
    and neither has anything to do with whether the capability is reachable.
    """

    def test_no_name_in_this_module_is_an_issuance_or_assignment_object(self) -> None:
        forbidden = {
            id(dispatch_authority.admit_dispatch),
            id(dispatch_authority.create_dispatch_grant),
            id(dispatch_authority.read_dispatch_grant),
            id(IssuanceScopedDispatchBoundary),
            id(IssuanceScopedDispatchBoundary.issue_receipt),
            id(dispatch_authority),
            id(issuance_scoped_boundary),
            id(worker_assignment),
            id(worker_assignment.claim_worker_assignment),
            id(worker_assignment.settle_worker_assignment),
        }
        for name in dir(work_queue):
            with self.subTest(name=name):
                self.assertNotIn(id(getattr(work_queue, name)), forbidden)

    def test_the_module_exports_no_issuance_or_assignment_entry_point(self) -> None:
        for name in (
            "admit_dispatch",
            "create_dispatch_grant",
            "issue_receipt",
            "claim_worker_assignment",
            "settle_worker_assignment",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, work_queue.__all__)

    def test_a_work_item_cannot_carry_a_receipt_or_an_assignment_it_minted(self) -> None:
        for field in ("origin_ref", "ticket_ref"):
            with self.subTest(field=field):
                self.assertIs(
                    work_queue.WorkItem.model_fields[field].annotation, str
                )


class HostAgnosticTests(unittest.TestCase):
    """Scheduling must not learn how a worker is spawned.

    The owner's route is universal and stays universal only while this file
    refuses to know the difference between hosts. The canonical name list is
    imported from the upstream cell rather than copied, because a second copy
    is what stops being updated when a host is added.
    """

    def test_the_queue_names_no_host_at_all(self) -> None:
        body = (_REPOSITORY_ROOT / _QUEUE_SOURCE).read_text(encoding="utf-8").lower()
        for name in _HOST_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, body)


class UpstreamRegressionTests(unittest.TestCase):
    """Defect class 4: the assignment ledger is untouched and still composes."""

    def _claim(
        self, layout: JohnnyRootLayout, repository: Path, tag: str
    ) -> WorkerClaimResult:
        return claim_worker_assignment(
            layout,
            WorkerClaimRequest(
                receipt_ref=f"receipt-{tag}",
                worker_ref="worker-one",
                worktree_ref=f"worktree-{tag}-01",
                branch_ref=f"branch-{tag}-01",
                repository_root=str(repository),
                host_worktree_path=str(repository / ".worktrees" / "w1"),
            ),
        )

    def test_claim_and_settle_still_behave_alongside_the_queue(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            enqueue_work(layout, _return_request())

            claimed = self._claim(layout, repository, "aaa")
            self.assertIs(claimed.status, WorkerClaimStatus.CLAIMED, f"{claimed.failure}")
            assert claimed.assignment is not None

            _pull(layout)

            settled = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )
            self.assertIs(
                settled.status, WorkerSettlementStatus.SETTLED, f"{settled.failure}"
            )

    def test_queue_traffic_leaves_the_assignment_ledger_byte_identical(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            self._claim(layout, repository, "aaa")
            before = worker_assignment.ledger_path(layout).read_bytes()

            enqueue_work(layout, _return_request())
            enqueue_work(layout, _commit_request())
            _pull(layout)

            after = worker_assignment.ledger_path(layout).read_bytes()
            self.assertEqual(before, after, "scheduling must not touch the ledger")

    def test_a_broken_queue_does_not_break_the_assignment_ledger(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            queue_path(layout).write_text("{not json at all", encoding="utf-8")

            claimed = self._claim(layout, repository, "aaa")
            self.assertIs(claimed.status, WorkerClaimStatus.CLAIMED, f"{claimed.failure}")
            self.assertIs(
                worker_assignment.read_worker_assignments(layout).status,
                worker_assignment.AssignmentReadStatus.READ,
            )

    def test_the_two_stores_share_no_file_and_no_lock(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            self.assertNotEqual(queue_path(layout), worker_assignment.ledger_path(layout))
            self.assertNotEqual(
                work_queue.lock_path(layout), worker_assignment.lock_path(layout)
            )


if __name__ == "__main__":
    unittest.main()
