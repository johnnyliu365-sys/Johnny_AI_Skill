# W5 — Exactly-Once Must Hold Across Processes

| Field | Value |
| --- | --- |
| State | `CLOSED` |
| Origin | Owner directive 2026-08-20 ("再找一次孤兒lease原因 這會是影響router的一個問題") — the re-investigation proved the orphan-lease family exists in the review return path |
| Baseline | `main` = `394a230` |
| Workload | `STANDARD`; `HIGH_ASSURANCE` — double emission drives a workflow transition twice |

## How the orphan-lease re-investigation led here

The completed root-cause chain for the test-suite orphans (recorded in
governance 03's addendum):

1. Every `provision` scans **all** children of the shared runtime root and
   reads their markers — a frequent concurrent reader.
2. On Windows, a directory being enumerated or a file being read cannot be
   deleted: a concurrent scanner made 16 of 200 teardowns fail
   `DELETE_FAILED` in an isolated experiment.
3. The affected tests assert teardown success once, in `finally`, with no
   retry — a blocked teardown abandons the lease.
4. The abandoned lease is unclaimable by any later process (per-process claim
   map) — mass refusal until a human intervenes.

The family signature: **shared durable state + per-process reasoning + no
cross-process mutual exclusion**. The production audit found the same
signature in exactly one place — and it is recent code, W2/W3:
`review_return.py` and `review_return_consumption.py` hold no lock at all,
while every older shared-state component (`live_dispatch_metadata_boundary`,
`windows_senior_review_inbox_store`) takes an OS-visible exclusive file lock
around every operation.

## The defect

`submit_review_return` and `consume_next_return` are read-check-append
sequences. Across two processes (or two threads):

- two identical submits can both pass the idempotence check → duplicate
  records; two conflicting submits can both pass the conflict check;
- two consumers can both see the same pending return, both write a consumed
  marker, and **both emit a RouterEvent** — the double-driven transition
  W3's marker ordering was built to refuse. The ordering is correct within a
  process and worthless across two.

## Design

- Extract the exclusive file lock into `file_lock.py` and rewire **both**
  existing private copies to it. Two identical private implementations
  already violate the no-second-implementation rule; this ticket must not
  add a third.
- One lock file (`review-returns.lock` beside the returns file) guards both
  submit and consume, since they contend for the same resource.
- The full critical section is locked: read, check, append, readback. Event
  construction may stay outside; the pending-read and the marker-append may
  not be separated from each other.

## Authorized implementation scope

```text
library/local_orchestration/file_lock.py
library/local_orchestration/live_dispatch_metadata_boundary.py    # rewire only
library/local_orchestration/windows_senior_review_inbox_store.py  # rewire only
library/local_orchestration/review_return.py
library/local_orchestration/review_return_consumption.py
tests/test_review_return_concurrency.py
modules/tickets/workstation-dispatch/
modules/tickets/workflow-governance/03-suite-order-fragility.md   # addendum
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `W5-R1` | Two concurrent consumers with a deliberately widened race window emit exactly one event; the other reports `NOTHING_PENDING`. Before the fix the same harness produces two emissions (recorded as the red state). |
| `W5-R2` | Two concurrent identical submits record one entry; both report success. |
| `W5-R3` | Both pre-existing lock users still pass their full suites after the rewire — the extraction is byte-equivalent in behavior. |
| `W5-R4` | Reverse mutation: removing the lock from consumption turns R1 red. |
| `W5-R5` | `mypy --strict` clean; full suite green; zero residue. |

## Closure evidence (2026-08-20, control-plane executed)

- `W5-R1` Two concurrent consumers with a barrier-widened race window:
  outcomes are exactly `["EMITTED", "NOTHING_PENDING"]`, one event, one
  consumed marker. The pre-fix red state is preserved as the reverse
  mutation below rather than as a checked-in failing cell.
- `W5-R2` Two concurrent identical submits: `["ALREADY_RECORDED",
  "RECORDED"]`, one entry on file.
- `W5-R3` Both prior lock users (`live_dispatch_metadata_boundary`,
  `windows_senior_review_inbox_store`) rewired to the extracted
  `file_lock.ExclusiveWindowsFileLock` under their original private alias;
  their suites pass unchanged and the whole-chain qualification stays
  `5 passed`.
- `W5-R4` Reverse mutation: dropping the consumption lock turns the
  two-consumer cell red with a double emission; restored byte-identical.
- `W5-R5` `mypy --strict` clean; full suite `992 passed, 16 skipped`; zero
  residue.

The barrier technique deserves a note: it holds every caller inside the
read until both arrive or the barrier times out. Unsynchronized callers meet
at the barrier and proceed together — the widest race. Locked callers cannot
meet: the second waits at the lock, the barrier times out for the first, and
the serialization being asserted is exactly what makes the barrier
unreachable for two at once.
