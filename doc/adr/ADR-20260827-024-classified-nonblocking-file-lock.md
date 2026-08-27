# ADR-20260827-024 — Classified nonblocking file-lock acquisition

- Date: 2026-08-27 (Asia/Taipei)
- Status: ACCEPTED
- Decision makers: project owner and reviewer
- Related requirement: PRD-20260827-041 / CHG-20260827-041
- Depends on: ADR-20260827-022 and ADR-20260827-023

## Context

ADR-20260827-023 catalogued `ExclusiveFileLock` as READY only for its delivered blocking
cross-process exclusion behavior. That was intentionally insufficient for the lock-bound
telemetry contract: Windows `msvcrt.LK_LOCK` has a bounded retry and can raise an unclassified
`OSError`, so catching every error and calling it contention would reproduce PITFALL-REGISTER C12.

The owner authorized a narrow upstream capability closure, not a telemetry adapter. Before this
decision, a direct two-process Windows probe opened the contender's handle successfully while an
independent child held the same one-byte lock. `msvcrt.LK_NBLCK` then failed immediately with
`OSError(errno=13, strerror="Permission denied")`; `winerror` was absent and elapsed time rounded
to `0.0ms`. This is the only local runtime evidence used to identify Windows contention.

## Decision

1. Keep `ExclusiveFileLock`, its `ExclusiveWindowsFileLock` alias, context-manager behavior, and
   all six blocking consumers compatible. No caller is migrated in this closure.
2. Add a separate finite API: `FileLockAcquireDecision = ACQUIRED | CONTENDED`,
   `try_acquire() -> FileLockAcquireDecision`, and a matching explicit `release() -> None`.
   `ACQUIRED` retains the one handle opened by that instance; `CONTENDED` retains none.
3. `try_acquire` has no timeout, retry, polling, worker, child-process workaround, or implicit
   fall-through to blocking acquisition. Misuse of the lock object's own lifecycle is a named
   programming error, not an extra success-like result.
4. On Windows, bind `LK_NBLCK` once at module import. After this instance has opened the lock
   file successfully, classify exactly `OSError(errno=EACCES)` from that nonblocking binding as
   `CONTENDED`. Propagate every other `OSError` unchanged. On POSIX, bind
   `LOCK_EX | LOCK_NB` and classify only `EACCES`/`EAGAIN`; do not claim POSIX runtime evidence
   until it is executed there.
5. A real independent-process holder/contender test, normal acquire/release test, existing
   blocking regression suite, injected non-contention error propagation test, strict typing,
   source guard, and review counter-mutation are mandatory before integration.
6. This does not implement `TelemetryStorageLockPort`, lock-token minting, storage re-admission,
   JSONL/ledger effects, provider/host behavior, token/cost accounting, target-project mutation,
   publication, release, or deployment.

## Consequences

The reusable capability gains a precise, immediately observable competition result while C12's
error distinction remains intact. A later local telemetry adapter may select this delivered
revision through the catalog, translate only `CONTENDED` into metadata-only `LOCK_CONTENDED`, and
must still prove locking and re-admission at the storage boundary. Ticket 06 remains blocked; its
preserved pre-lock candidate is neither corrected nor integrated by this decision.

## Rejected alternatives

- Reuse blocking `LK_LOCK` and translate any delayed `OSError` to contention: rejects real I/O
  errors and reproduces C12.
- Add a timeout, retry, queue, runner, or background process: changes the primitive's ownership
  and delivery scope without improving this finite acquisition contract.
- Implement the telemetry adapter at the same time: mixes reusable lock behavior with storage
  ownership and would leave neither closure independently reviewable.
