"""P2: does the ledger know which ticket is in whose hands, after the talking stops?

The upstream gate (P1) proved several workers can be dispatched at once. What
it never recorded is who received the work, so a worker that dies leaves no
trace and the control plane keeps believing the ticket is moving.

These cells use real processes for the exactly-once property rather than
threads, for the reason W5 paid to learn: threads share the interpreter's file
handles, so an in-process-only lock passes a threaded test and loses a genuine
race between two processes. A threaded version of the duplicate-claim cell
below would go green against an implementation with no file lock at all.

Nothing here waits, sleeps, or polls. An orphan is discovered because a test
reads, which is the whole liveness model: claim, settle, and look.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.local_orchestration import dispatch_authority, worker_assignment
from library.local_orchestration import issuance_scoped_boundary
from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionStatus,
    admit_dispatch,
    create_dispatch_grant,
)
from library.local_orchestration.issuance_scoped_boundary import (
    IssuanceScopedDispatchBoundary,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.worker_assignment import (
    AssignmentLifecycle,
    AssignmentReadStatus,
    WorkerAssignment,
    WorkerClaimFailure,
    WorkerClaimRequest,
    WorkerClaimStatus,
    WorkerSettlementFailure,
    WorkerSettlementRequest,
    WorkerSettlementStatus,
    claim_worker_assignment,
    ledger_path,
    read_orphan_assignments,
    read_worker_assignments,
    settle_worker_assignment,
)
from tests.test_dispatch_authority import _layout, _repository, _request
from tests.test_parallel_worker_dispatch import _HOST_NAMES

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_BOOKKEEPING_SOURCE = "library/local_orchestration/worker_assignment.py"

_CHILD = '''\
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.worker_assignment import (
    WorkerClaimRequest,
    claim_worker_assignment,
)

layout = JohnnyRootLayout(base=Path(sys.argv[2]))
request = WorkerClaimRequest.model_validate_json(
    Path(sys.argv[3]).read_text(encoding="utf-8")
)

# Pay the import cost, say so, then block until released.
#
# Without this gate each child starts claiming whenever its own interpreter
# finished importing, and that spread is tens of milliseconds while the
# unprotected window inside a claim is one or two. The race would then be
# decided by startup jitter rather than by the lock, and a build with no lock
# at all would pass most runs -- a test that fails one time in fifty is not a
# test. Blocking on a pipe is a blocking read, not a poll and not a timer.
print("ready", flush=True)
sys.stdin.readline()

result = claim_worker_assignment(layout, request)
print(
    json.dumps(
        {
            "status": result.status.value,
            "failure": None if result.failure is None else result.failure.value,
            "claim_id": None if result.assignment is None else result.assignment.claim_id,
        }
    ),
    flush=True,
)
'''


def _race_children(
    script: Path, layout: JohnnyRootLayout, request_files: tuple[Path, ...]
) -> list[dict]:
    """Claim from genuinely separate processes released at the same instant.

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
                str(path),
            ),
            cwd=str(path.parent),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        for path in request_files
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
        verdicts = []
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


def _claim_request(
    repository: Path,
    tag: str = "aaa",
    worker_ref: str = "worker-one",
    host_worktree_path: str | None = None,
) -> WorkerClaimRequest:
    return WorkerClaimRequest(
        receipt_ref=f"receipt-{tag}",
        worker_ref=worker_ref,
        worktree_ref=f"worktree-{tag}-01",
        branch_ref=f"branch-{tag}-01",
        repository_root=str(repository),
        host_worktree_path=(
            str(repository / ".worktrees" / "w1")
            if host_worktree_path is None
            else host_worktree_path
        ),
    )


def _seed(temporary: str) -> tuple[JohnnyRootLayout, Path]:
    base = Path(temporary).resolve()
    return _layout(base), _repository(base)


class ClaimReadbackTests(unittest.TestCase):
    """P2-R1: a claim is a durable fact, readable with the fields it was made with."""

    def test_a_claim_reads_back_field_for_field(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            request = _claim_request(repository)

            result = claim_worker_assignment(layout, request)
            self.assertIs(result.status, WorkerClaimStatus.CLAIMED, f"{result.failure}")
            assert result.assignment is not None

            read = read_worker_assignments(layout)
            self.assertIs(read.status, AssignmentReadStatus.READ)
            assert read.assignments is not None
            self.assertEqual(len(read.assignments), 1)
            stored = read.assignments[0]
            self.assertEqual(stored, result.assignment)
            self.assertEqual(stored.receipt_ref, request.receipt_ref)
            self.assertEqual(stored.worker_ref, request.worker_ref)
            self.assertEqual(stored.worktree_ref, request.worktree_ref)
            self.assertEqual(stored.branch_ref, request.branch_ref)
            self.assertIs(stored.lifecycle, AssignmentLifecycle.CLAIMED)

    def test_the_record_survives_a_process_that_never_saw_the_claim(self) -> None:
        """The actual break: the binding must outlive whoever wrote it down."""

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))

            reopened = JohnnyRootLayout(base=layout.base)
            read = read_worker_assignments(reopened)
            self.assertIs(read.status, AssignmentReadStatus.READ)
            assert read.assignments is not None
            self.assertEqual(
                [item.receipt_ref for item in read.assignments], ["receipt-aaa"]
            )

    def test_the_host_worktree_path_never_enters_the_record(self) -> None:
        """Paths are for the gate; the record keeps opaque identities only."""

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))
            body = ledger_path(layout).read_text(encoding="utf-8")
            self.assertNotIn(str(repository), body)
            self.assertNotIn("host_worktree_path", body)


class DuplicateClaimTests(unittest.TestCase):
    """P2-R2: one ticket, one pair of hands. The property the line rests on."""

    def test_a_second_claim_on_one_receipt_is_refused_by_name(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            first = claim_worker_assignment(layout, _claim_request(repository))
            second = claim_worker_assignment(
                layout, _claim_request(repository, worker_ref="worker-two")
            )

            self.assertIs(first.status, WorkerClaimStatus.CLAIMED)
            self.assertIs(second.status, WorkerClaimStatus.REFUSED)
            self.assertIs(second.failure, WorkerClaimFailure.RECEIPT_ALREADY_CLAIMED)
            self.assertIsNone(second.assignment)

    def test_the_refused_second_claim_does_not_displace_the_first(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            first = claim_worker_assignment(layout, _claim_request(repository))
            claim_worker_assignment(
                layout, _claim_request(repository, worker_ref="worker-two")
            )

            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertEqual(len(read.assignments), 1)
            assert first.assignment is not None
            self.assertEqual(read.assignments[0], first.assignment)
            self.assertEqual(read.assignments[0].worker_ref, "worker-one")

    def test_an_identical_repeat_is_refused_rather_than_folded_away(self) -> None:
        """Not idempotent, deliberately.

        A repeat issuance asserts the same fact because a receipt is a function
        of its artifact. A repeat claim asserts *who holds this now*, so an
        identical-looking second claim is still a second assertion -- and the
        case it would hide is a worker replaced without the first settling,
        which is exactly the orphan this module exists to expose.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))
            repeat = claim_worker_assignment(layout, _claim_request(repository))
            self.assertIs(repeat.status, WorkerClaimStatus.REFUSED)
            self.assertIs(repeat.failure, WorkerClaimFailure.RECEIPT_ALREADY_CLAIMED)

    def test_a_settled_claim_still_refuses_a_second_claim_on_that_receipt(
        self,
    ) -> None:
        """The settled row is a tombstone, and P5 leans its whole weight on it.

        A receipt reference that has ever appeared here can never be claimed
        again, whatever lifecycle its row reached. That is what makes ending a
        compensated receipt safe: the retired receipt cannot come back into
        somebody's hands beside its successor, so the successor really is the
        only claimable receipt on the ticket. If a settled row stopped
        blocking, the redispatch route would hand one ticket out twice.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(layout, _claim_request(repository))
            assert claimed.assignment is not None
            settled = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )
            self.assertIs(settled.status, WorkerSettlementStatus.SETTLED)

            again = claim_worker_assignment(
                layout, _claim_request(repository, worker_ref="worker-two")
            )

            self.assertIs(again.status, WorkerClaimStatus.REFUSED)
            self.assertIs(again.failure, WorkerClaimFailure.RECEIPT_ALREADY_CLAIMED)
            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertEqual(len(read.assignments), 1)
            self.assertIs(read.assignments[0].lifecycle, AssignmentLifecycle.SETTLED)
            self.assertEqual(read.assignments[0].worker_ref, "worker-one")

    def test_two_different_receipts_each_get_their_own_assignment(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            first = claim_worker_assignment(layout, _claim_request(repository, "aaa"))
            second = claim_worker_assignment(layout, _claim_request(repository, "bbb"))
            self.assertIs(first.status, WorkerClaimStatus.CLAIMED)
            self.assertIs(second.status, WorkerClaimStatus.CLAIMED)
            assert first.assignment is not None and second.assignment is not None
            self.assertNotEqual(first.assignment.claim_id, second.assignment.claim_id)


class CrossProcessClaimTests(unittest.TestCase):
    """P2-R3: exactly once, proven between real processes.

    Threads would share this interpreter's file handles. Two processes do not,
    which is the only arrangement in which a missing OS-level lock can fail.
    """

    def test_one_receipt_claimed_from_four_processes_binds_exactly_once(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            base = Path(temporary).resolve()
            script = base / "child.py"
            script.write_text(_CHILD, encoding="utf-8")
            request = _claim_request(repository)
            paths = []
            for name in ("race-a", "race-b", "race-c", "race-d"):
                path = base / f"{name}.json"
                path.write_text(request.model_dump_json(), encoding="utf-8")
                paths.append(path)

            results = _race_children(script, layout, tuple(paths))

            self.assertEqual(len(results), 4, "every child must produce a verdict")
            claimed = [
                item
                for item in results
                if item["status"] == WorkerClaimStatus.CLAIMED.value
            ]
            refused = [
                item
                for item in results
                if item["status"] == WorkerClaimStatus.REFUSED.value
            ]
            self.assertEqual(
                len(claimed), 1, f"exactly one process may bind the receipt: {results}"
            )
            self.assertEqual(len(refused), 3, f"{results}")
            for item in refused:
                with self.subTest(failure=item["failure"]):
                    self.assertEqual(
                        item["failure"],
                        WorkerClaimFailure.RECEIPT_ALREADY_CLAIMED.value,
                        "a loser must lose for the stated reason, not by storage error",
                    )

            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertEqual(
                len(read.assignments),
                1,
                "the ledger must hold exactly the one binding that won",
            )
            self.assertEqual(read.assignments[0].claim_id, claimed[0]["claim_id"])


class SettlementTests(unittest.TestCase):
    """P2-R4: settling closes the claim that was made, and only that one."""

    def test_settling_a_claim_closes_it(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(layout, _claim_request(repository))
            assert claimed.assignment is not None

            settled = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )
            self.assertIs(settled.status, WorkerSettlementStatus.SETTLED)
            assert settled.assignment is not None
            self.assertIs(settled.assignment.lifecycle, AssignmentLifecycle.SETTLED)

            read = read_worker_assignments(layout)
            assert read.assignments is not None
            self.assertIs(read.assignments[0].lifecycle, AssignmentLifecycle.SETTLED)

    def test_settling_with_the_wrong_receipt_is_refused_and_the_claim_stands(
        self,
    ) -> None:
        """A settlement must close the claim it names, not whatever that id hit.

        Looking up by `claim_id` alone would let a stale or copied id retire a
        different ticket's assignment, and the orphan it was hiding would go
        with it. So the refusal is checked *and* the survival of the claim.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(layout, _claim_request(repository, "aaa"))
            claim_worker_assignment(layout, _claim_request(repository, "bbb"))
            assert claimed.assignment is not None

            mismatched = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-bbb"
                ),
            )
            self.assertIs(mismatched.status, WorkerSettlementStatus.REFUSED)
            self.assertIs(
                mismatched.failure, WorkerSettlementFailure.SETTLEMENT_RECEIPT_MISMATCH
            )
            self.assertIsNone(mismatched.assignment)

            orphans = read_orphan_assignments(layout)
            assert orphans.assignments is not None
            self.assertIn(
                "receipt-aaa",
                [item.receipt_ref for item in orphans.assignments],
                "a refused settlement must leave the orphan visible",
            )

    def test_settling_an_unknown_claim_is_refused_by_its_own_name(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            result = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id="claim-never-made", receipt_ref="receipt-aaa"
                ),
            )
            self.assertIs(result.status, WorkerSettlementStatus.REFUSED)
            self.assertIs(result.failure, WorkerSettlementFailure.ASSIGNMENT_ABSENT)

    def test_settling_twice_is_refused_distinctly_from_never_claimed(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(layout, _claim_request(repository))
            assert claimed.assignment is not None
            settlement = WorkerSettlementRequest(
                claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
            )
            settle_worker_assignment(layout, settlement)
            again = settle_worker_assignment(layout, settlement)

            self.assertIs(again.status, WorkerSettlementStatus.REFUSED)
            self.assertIs(
                again.failure, WorkerSettlementFailure.ASSIGNMENT_ALREADY_SETTLED
            )
            self.assertIsNot(
                again.failure,
                WorkerSettlementFailure.ASSIGNMENT_ABSENT,
                "already done and never started are different facts",
            )


class OrphanVisibilityTests(unittest.TestCase):
    """P2-R5: a claim nobody settled surfaces on read, carrying who and where."""

    def test_an_unsettled_claim_is_an_orphan_naming_its_receipt_and_worktree(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository, "aaa"))

            orphans = read_orphan_assignments(layout)
            self.assertIs(orphans.status, AssignmentReadStatus.READ)
            assert orphans.assignments is not None
            self.assertEqual(len(orphans.assignments), 1)
            orphan = orphans.assignments[0]
            self.assertEqual(orphan.receipt_ref, "receipt-aaa")
            self.assertEqual(orphan.worktree_ref, "worktree-aaa-01")
            self.assertEqual(orphan.branch_ref, "branch-aaa-01")
            self.assertEqual(orphan.worker_ref, "worker-one")

    def test_a_settled_claim_is_not_an_orphan_but_is_still_on_the_ledger(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(layout, _claim_request(repository))
            assert claimed.assignment is not None
            settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )

            self.assertEqual(read_orphan_assignments(layout).assignments, ())
            full = read_worker_assignments(layout)
            assert full.assignments is not None
            self.assertEqual(len(full.assignments), 1)

    def test_orphans_separate_from_settled_work_on_a_mixed_ledger(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            done = claim_worker_assignment(layout, _claim_request(repository, "aaa"))
            claim_worker_assignment(layout, _claim_request(repository, "bbb"))
            assert done.assignment is not None
            settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=done.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )

            orphans = read_orphan_assignments(layout)
            assert orphans.assignments is not None
            self.assertEqual(
                [item.receipt_ref for item in orphans.assignments], ["receipt-bbb"]
            )

    def test_nothing_in_the_record_carries_a_clock(self) -> None:
        """No timestamp field, so no timeout rule can be built without a schema change.

        A timestamp would not itself be a timer, but it is the only thing a
        timer needs. Keeping it out means "expire claims older than N" cannot
        be added quietly.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))
            stored = json.loads(ledger_path(layout).read_text(encoding="utf-8"))
            for record in stored["assignments"]:
                for field in record:
                    with self.subTest(field=field):
                        self.assertNotIn("at_utc", field)
                        self.assertNotIn("time", field)
                        self.assertNotIn("_ms", field)
                        self.assertNotIn("deadline", field)
                        self.assertNotIn("expire", field)


class StorageFailClosedTests(unittest.TestCase):
    """P2-R6: not knowing whether anyone is working is not the same as nobody working."""

    def test_an_unparseable_ledger_reads_as_a_named_failure_not_as_empty(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))
            ledger_path(layout).write_text("{not json at all", encoding="utf-8")

            read = read_worker_assignments(layout)
            self.assertIs(read.status, AssignmentReadStatus.STORAGE_UNAVAILABLE)
            self.assertIsNone(
                read.assignments,
                "an unreadable ledger must not present as an empty one",
            )

    def test_an_unreadable_ledger_hides_no_orphans(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))
            ledger_path(layout).write_text("{not json at all", encoding="utf-8")

            orphans = read_orphan_assignments(layout)
            self.assertIs(orphans.status, AssignmentReadStatus.STORAGE_UNAVAILABLE)
            self.assertIsNone(
                orphans.assignments,
                "reporting 'no orphans' from a broken ledger is the false green",
            )

    def test_a_wrong_schema_ledger_refuses_rather_than_being_reinterpreted(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            ledger_path(layout).write_text(
                json.dumps({"schema_revision": "worker-assignment-v2"}),
                encoding="utf-8",
            )
            self.assertIs(
                read_worker_assignments(layout).status,
                AssignmentReadStatus.STORAGE_UNAVAILABLE,
            )

    def test_a_claim_against_a_broken_ledger_refuses_and_overwrites_nothing(
        self,
    ) -> None:
        """The fail-closed case that matters most.

        If a broken ledger let a fresh claim through, the ticket already in
        somebody's hands would be handed out a second time -- and the evidence
        that it had been would be gone in the same write.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claim_worker_assignment(layout, _claim_request(repository))
            corrupt = "{not json at all"
            ledger_path(layout).write_text(corrupt, encoding="utf-8")

            result = claim_worker_assignment(
                layout, _claim_request(repository, "bbb")
            )
            self.assertIs(result.status, WorkerClaimStatus.REFUSED)
            self.assertIs(result.failure, WorkerClaimFailure.STORAGE_UNAVAILABLE)
            self.assertEqual(
                ledger_path(layout).read_text(encoding="utf-8"),
                corrupt,
                "a refusal must not rewrite the ledger it could not read",
            )

    def test_a_settlement_against_a_broken_ledger_refuses_as_storage_not_absent(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            claimed = claim_worker_assignment(layout, _claim_request(repository))
            assert claimed.assignment is not None
            ledger_path(layout).write_text("{not json at all", encoding="utf-8")

            result = settle_worker_assignment(
                layout,
                WorkerSettlementRequest(
                    claim_id=claimed.assignment.claim_id, receipt_ref="receipt-aaa"
                ),
            )
            self.assertIs(result.status, WorkerSettlementStatus.REFUSED)
            self.assertIs(result.failure, WorkerSettlementFailure.STORAGE_UNAVAILABLE)
            self.assertIsNot(
                result.failure,
                WorkerSettlementFailure.ASSIGNMENT_ABSENT,
                "an unreadable ledger must never look like an absent claim",
            )

    def test_a_directory_where_the_ledger_belongs_is_a_storage_failure(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            ledger_path(layout).mkdir(parents=True)

            self.assertIs(
                read_worker_assignments(layout).status,
                AssignmentReadStatus.STORAGE_UNAVAILABLE,
            )
            self.assertIs(
                claim_worker_assignment(layout, _claim_request(repository)).failure,
                WorkerClaimFailure.STORAGE_UNAVAILABLE,
            )


class EmptyAndAbsentTests(unittest.TestCase):
    """Defect class 2: absence, empty identity and empty reference stay distinct."""

    def test_no_assignment_at_all_reads_as_an_empty_success(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            read = read_worker_assignments(layout)
            self.assertIs(read.status, AssignmentReadStatus.READ)
            self.assertEqual(read.assignments, ())
            self.assertIsNotNone(
                read.assignments,
                "nobody working is a successful read, not a failed one",
            )

    def test_an_empty_receipt_reference_never_reaches_the_store(self) -> None:
        with TemporaryDirectory() as temporary:
            _, repository = _seed(temporary)
            with self.assertRaises(ValidationError):
                WorkerClaimRequest(
                    receipt_ref="",
                    worker_ref="worker-one",
                    worktree_ref="worktree-aaa-01",
                    branch_ref="branch-aaa-01",
                    repository_root=str(repository),
                    host_worktree_path=str(repository / ".worktrees" / "w1"),
                )

    def test_an_empty_worker_reference_never_reaches_the_store(self) -> None:
        with TemporaryDirectory() as temporary:
            _, repository = _seed(temporary)
            with self.assertRaises(ValidationError):
                _claim_request(repository, worker_ref="")

    def test_an_empty_worktree_path_is_refused_as_input_not_as_containment(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            _, repository = _seed(temporary)
            with self.assertRaises(ValidationError):
                _claim_request(repository, host_worktree_path="")

    def test_a_foreign_request_object_is_refused_as_invalid(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, _ = _seed(temporary)
            result = claim_worker_assignment(layout, object())  # type: ignore[arg-type]
            self.assertIs(result.status, WorkerClaimStatus.REFUSED)
            self.assertIs(result.failure, WorkerClaimFailure.REQUEST_INVALID)

            settlement = settle_worker_assignment(layout, object())  # type: ignore[arg-type]
            self.assertIs(
                settlement.failure, WorkerSettlementFailure.REQUEST_INVALID
            )


class WorktreePathMatchingTests(unittest.TestCase):
    """Defect class 1: the prefix family, on the path that decides admission."""

    def test_the_sanctioned_root_itself_matches_by_equality(self) -> None:
        """Equality is a match, inherited unchanged from the issuance gate.

        Restating containment locally is how a reparse-point evasion returns,
        so this module imports the reviewed predicate and inherits its edges,
        including this one: the sanctioned root equals itself and is contained.
        A stricter rule here would admit a path for issuance and refuse the
        same path for claiming, which is a worse failure than this edge.
        """

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            result = claim_worker_assignment(
                layout,
                _claim_request(
                    repository, host_worktree_path=str(repository / ".worktrees")
                ),
            )
            self.assertIs(result.status, WorkerClaimStatus.CLAIMED)

    def test_one_extra_character_on_the_sanctioned_root_is_refused(self) -> None:
        """`.worktreesX` is a string prefix match and a different directory."""

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            impostor = repository / ".worktreesX" / "w1"
            impostor.mkdir(parents=True)
            result = claim_worker_assignment(
                layout, _claim_request(repository, host_worktree_path=str(impostor))
            )
            self.assertIs(result.status, WorkerClaimStatus.REFUSED)
            self.assertIs(
                result.failure, WorkerClaimFailure.WORKTREE_OUTSIDE_REPOSITORY_ROOT
            )

    def test_a_sibling_repository_directory_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            sibling = repository.parent / f"{repository.name}-w1"
            sibling.mkdir(parents=True)
            result = claim_worker_assignment(
                layout, _claim_request(repository, host_worktree_path=str(sibling))
            )
            self.assertIs(
                result.failure, WorkerClaimFailure.WORKTREE_OUTSIDE_REPOSITORY_ROOT
            )

    def test_a_trailing_separator_does_not_change_the_verdict(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            with_separator = str(repository / ".worktrees" / "w1") + "\\"
            result = claim_worker_assignment(
                layout,
                _claim_request(repository, host_worktree_path=with_separator),
            )
            self.assertIs(result.status, WorkerClaimStatus.CLAIMED, f"{result.failure}")

    def test_a_case_variant_of_a_contained_worktree_is_still_contained(self) -> None:
        """On this filesystem these are one directory, so they must decide alike."""

        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            variant = str(repository / ".WORKTREES" / "W1")
            result = claim_worker_assignment(
                layout, _claim_request(repository, host_worktree_path=variant)
            )
            self.assertIs(result.status, WorkerClaimStatus.CLAIMED, f"{result.failure}")

    def test_a_traversal_out_of_the_repository_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            outside = repository.parent / "outside"
            outside.mkdir(parents=True)
            traversal = str(repository / ".worktrees" / ".." / ".." / "outside")
            result = claim_worker_assignment(
                layout, _claim_request(repository, host_worktree_path=traversal)
            )
            self.assertIs(result.status, WorkerClaimStatus.REFUSED)
            self.assertIs(
                result.failure, WorkerClaimFailure.WORKTREE_OUTSIDE_REPOSITORY_ROOT
            )

    def test_a_refused_worktree_writes_no_assignment(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            outside = repository.parent / "elsewhere"
            outside.mkdir(parents=True)
            claim_worker_assignment(
                layout, _claim_request(repository, host_worktree_path=str(outside))
            )
            read = read_worker_assignments(layout)
            self.assertEqual(read.assignments, ())


class IssuanceSeparationTests(unittest.TestCase):
    """Defect class 3: bookkeeping may refer to a receipt and may never mint one.

    Asserted by object identity rather than by searching the source for names.
    A substring check passes for `admit_dispatch_v2` and fails for a comment,
    and neither has anything to do with whether the capability is reachable.
    """

    def test_no_name_in_this_module_is_an_issuance_object(self) -> None:
        forbidden = {
            id(dispatch_authority.admit_dispatch),
            id(dispatch_authority.create_dispatch_grant),
            id(dispatch_authority.read_dispatch_grant),
            id(IssuanceScopedDispatchBoundary),
            id(IssuanceScopedDispatchBoundary.issue_receipt),
            id(dispatch_authority),
            id(issuance_scoped_boundary),
        }
        for name in dir(worker_assignment):
            with self.subTest(name=name):
                self.assertNotIn(id(getattr(worker_assignment, name)), forbidden)

    def test_the_module_exports_no_issuance_entry_point(self) -> None:
        for name in ("admit_dispatch", "create_dispatch_grant", "issue_receipt"):
            with self.subTest(name=name):
                self.assertNotIn(name, worker_assignment.__all__)

    def test_an_assignment_cannot_carry_a_receipt_it_minted(self) -> None:
        """`receipt_ref` is an opaque reference, never a receipt object."""

        annotation = WorkerAssignment.model_fields["receipt_ref"].annotation
        self.assertIs(annotation, str)


class HostAgnosticTests(unittest.TestCase):
    """The bookkeeping side must not learn how a worker is spawned.

    The owner's route is universal and stays universal only while this file
    refuses to know the difference between hosts. The canonical name list is
    imported from the upstream cell rather than copied, because a second copy
    is what stops being updated when a host is added.
    """

    def test_the_assignment_ledger_names_no_host_at_all(self) -> None:
        body = (
            (_REPOSITORY_ROOT / _BOOKKEEPING_SOURCE).read_text(encoding="utf-8").lower()
        )
        for name in _HOST_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, body)


class UpstreamRegressionTests(unittest.TestCase):
    """Defect class 4 regression: the issuance gate is untouched and composes."""

    def test_admit_dispatch_still_dispatches_alongside_the_ledger(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            create_dispatch_grant(layout)
            admitted = admit_dispatch(layout, _request(repository))
            self.assertIs(
                admitted.status, DispatchAdmissionStatus.DISPATCHED, f"{admitted.failure}"
            )
            assert admitted.receipt is not None

            claimed = claim_worker_assignment(
                layout,
                WorkerClaimRequest(
                    receipt_ref=admitted.receipt.receipt_id,
                    worker_ref="worker-one",
                    worktree_ref=admitted.receipt.worktree_fingerprint,
                    branch_ref=admitted.receipt.branch_fingerprint,
                    repository_root=str(repository),
                    host_worktree_path=str(repository / ".worktrees" / "w1"),
                ),
            )
            self.assertIs(claimed.status, WorkerClaimStatus.CLAIMED, f"{claimed.failure}")

            orphans = read_orphan_assignments(layout)
            assert orphans.assignments is not None
            self.assertEqual(
                [item.receipt_ref for item in orphans.assignments],
                [admitted.receipt.receipt_id],
            )

    def test_the_ledger_leaves_the_issuance_metadata_alone(self) -> None:
        with TemporaryDirectory() as temporary:
            layout, repository = _seed(temporary)
            create_dispatch_grant(layout)
            admitted = admit_dispatch(layout, _request(repository))
            assert admitted.receipt is not None
            metadata = layout.queue_root / "metadata"
            before = sorted(
                path.read_bytes() for path in metadata.rglob("*") if path.is_file()
            )

            claim_worker_assignment(layout, _claim_request(repository))

            after = sorted(
                path.read_bytes() for path in metadata.rglob("*") if path.is_file()
            )
            self.assertEqual(before, after, "bookkeeping must not touch issuance state")


if __name__ == "__main__":
    unittest.main()
