# W2 — Reviewer Return Path

| Field | Value |
| --- | --- |
| State | `CLOSED` |
| Baseline | `main` = `ebb0ae7` |
| Workload | `STANDARD`; `HIGH_ASSURANCE` — a verdict is an authority-bearing artifact |
| Depends on | W1 (dispatch admission), E10/E12 (the wake actually reaches an agent) |

## One outcome

A woken reviewer can return its verdict, and the return is durable, typed and
unforgeable:

```text
johnny-router review submit <verdict.json>
```

This closes the loop. Everything before it exists: dispatch issues a receipt,
the runner arms on the exact ref, a commit delivers a real wake, and an agent
acts. What is missing is the way back.

## The authority rule that shapes this

A verdict must not be mintable. Two durable facts must already be true before
one is recorded, and both are *read*, never asserted by the caller:

1. The receipt named by the verdict exists in the durable checkpoint and is
   `ACTIVE` — the ticket was really dispatched.
2. A role wake attempt for that receipt exists with lifecycle `HOST_ACCEPTED`
   — the reviewer was really woken. A verdict for a review nobody was asked
   to perform is refused `WAKE_NOT_DELIVERED`.

The runner's unbatched composition bypasses the Senior review inbox, so the
batched `ReviewBatchDecisionRequest` path does not apply here; this is the
single-handoff counterpart.

## Design

- `read_role_wake_attempt` is added to `LiveDispatchMetadataBoundary`,
  following the existing `read_artifact` / `read_receipt` shape exactly:
  read-only, lock-held, finite typed result. Additive; no existing method,
  contract or checkpoint field changes.
- `ReviewReturnScopedDispatchBoundary` exposes exactly the two reads this
  path needs — `read_receipt`, `read_role_wake_attempt` — and nothing that
  can write the checkpoint. Third facade, same discipline as the wake-scoped
  and issuance-scoped ones.
- Verdicts are stored in an append-only `review-returns.jsonl` under the
  Johnny root, not in the durable checkpoint: the checkpoint's schema is
  reviewed and frozen, and a return is control-plane bookkeeping, following
  the install-journal and dispatch-journal precedent.
- The recorded return is read back before success is reported.
- Idempotence: the same reviewer returning the same verdict for the same
  receipt and handoff twice records one entry and reports success both times.
  A *different* verdict for the same pair is refused `VERDICT_CONFLICT` — a
  verdict, once returned, is evidence.

## Authorized implementation scope

```text
library/workflow_router/role_wake_contracts.py        # additive read request/result only
library/local_orchestration/live_dispatch_metadata_boundary.py   # additive read method only
library/local_orchestration/review_return_boundary.py
library/local_orchestration/review_return.py
library/local_orchestration/review_cli.py
library/local_orchestration/johnny_live_cli.py        # one routing addition
tests/test_review_return.py
modules/tickets/workstation-dispatch/
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `W2-R1` | A verdict for an undispatched receipt refuses `RECEIPT_NOT_DISPATCHED` and records nothing. |
| `W2-R2` | A verdict for a dispatched receipt whose wake was never delivered refuses `WAKE_NOT_DELIVERED` and records nothing; a wake settled `NO_EFFECT` or `EFFECT_UNCERTAIN` is equally insufficient. |
| `W2-R3` | With receipt dispatched and wake `HOST_ACCEPTED`, the verdict records, reads back, and carries reviewer, verdict, handoff and reviewed commit. |
| `W2-R4` | Identical repeat is idempotent (one entry, success twice); a conflicting verdict for the same receipt and handoff refuses `VERDICT_CONFLICT` without altering the recorded one. |
| `W2-R5` | The return path holds no write-capable boundary: pinned by runtime-binding identity on the object the path actually constructs, plus absence of issuance and wake-claim methods. |
| `W2-R6` | The full loop composes in one test: dispatch admission issues, a wake attempt is settled `HOST_ACCEPTED`, the verdict returns and reads back. |
| `W2-R7` | Reverse mutations: dropping the wake check turns R2 red; dropping the conflict check turns R4 red. |
| `W2-R8` | `mypy --strict` clean; full suite green; zero residue; every existing wake and dispatch test still green (the boundary addition is additive). |

## Closure evidence (2026-08-19, control-plane executed)

- `W2-R1` A verdict for an undispatched receipt refuses
  `RECEIPT_NOT_DISPATCHED`; the returns file is never created.
- `W2-R2` A dispatched receipt with no wake refuses `WAKE_NOT_DELIVERED`, and
  a wake settled `NO_EFFECT` or `EFFECT_UNCERTAIN` is equally insufficient —
  only `HOST_ACCEPTED` counts as a delivery.
- `W2-R3` With both facts true the verdict records and reads back carrying
  reviewer, verdict, handoff and reviewed commit.
- `W2-R4` Identical repeat reports `ALREADY_RECORDED` with one entry on file;
  a contradicting verdict refuses `VERDICT_CONFLICT` and the recorded one is
  unchanged. A second reviewer returns separately, as it should.
- `W2-R5` The facade exposes exactly `read_receipt` and
  `read_role_wake_attempt`; issuance and wake-claim methods are absent. The
  discriminating cell asserts the runtime object the path actually builds.
- `W2-R6` The loop closes in one test: `admit_dispatch` issues, a wake settles
  `HOST_ACCEPTED`, the verdict returns and reads back against that receipt.
- `W2-R7` Reverse mutations: removing the wake check turns three cells red;
  removing the conflict check turns R4's cell red. Restored byte-identical.
- `W2-R8` `mypy --strict` clean; full suite `980 passed, 11 skipped`; gated
  qualifications `10 passed`; zero residue. The boundary addition is additive
  and every existing wake and dispatch test stayed green.

CLI smoke through `run_live_cli`: submit before any wake →
`BLOCKED/WAKE_NOT_DELIVERED` exit 2; after a delivered wake → `RECORDED`
exit 0; again → `ALREADY_RECORDED` exit 0; `review list` → the one return.

Follow-ups, recorded not done: Router-side consumption of the returns file
(this ticket delivers the durable, unforgeable record; deciding the next
stage from it is Router work), and README documentation in the next release
pass.
