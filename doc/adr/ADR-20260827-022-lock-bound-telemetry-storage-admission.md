# ADR-20260827-022 — Lock-bound telemetry storage admission

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260827-041` / `CHG-20260827-041`
- Amends: telemetry-storage admission in `ADR-20260824-019`; it does not alter provider-usage,
  isolated-pair, pricing, target-isolation, or host-effect rules.

## Context

Ticket 06's first candidate proved strict identity, lifecycle and containment checks, then a
review counter-mutation showed that a failed lifecycle advance could leave stream bytes changed.
The local correction restored fixture bytes, but the review also identified the controlling
problem: a durable JSONL stream is shared state. Without cross-process exclusion, two valid
operations can interleave reads, writes, lifecycle changes or cleanup. Reporting that state as a
generic storage boundary failure would repeat the known lock-contention misclassification.

## Decision

1. Extend `TelemetryStorageDecision` with `LOCK_CONTENDED`. It means an exact requested stream
   was not entered; no codec, ledger, report, target, provider or retry effect occurred.
2. Define a provider-neutral, metadata-only storage lock port. A lock token is bound to the
   opaque storage identity and expected revision; it has no raw path or source content.
3. An adapter performs preliminary identity admission, obtains the lock, then re-admits exact
   ownership, revision, lifecycle and containment inside the lock. This is required for APPEND,
   READ, VALIDATE, DETACH and UNINSTALL alike.
4. Release runs in `finally`. A release failure cannot be reported as a completed operation.
   The existing `STORAGE_BOUNDARY_VIOLATION` is retained for this failed owned-boundary effect;
   it is not `LOCK_CONTENDED`.
5. The existing `file_lock.py` is deliberately not adopted: it lacks a delivered catalog card.
   Its formal capability selection is a prerequisite to any real lock-adapter implementation.
6. Ticket 06's candidate remains uncommitted evidence. It is blocked rather than integrated or
   silently widened; successor tickets start from a new authority baseline.

## Implementation sequence

1. Pure strict lock request/token/result/port contracts and reverse-mutation tests.
2. Catalog admission for one reusable cross-process lock capability, or an owner-approved new
   capability card.
3. Lock-bound ledger/storage adapter with holder-versus-contender fixture and an independent
   release-failure counter-mutation.
4. Only then: provider-terminal fake admission, and later separately authorized host probes.

## Alternatives rejected

- **Treat competition as a generic storage failure.** Rejected: it hides lock contention and
  prevents callers from taking the correct bounded retry/owner action.
- **Keep Ticket 06's byte-restoration patch and integrate it.** Rejected: rollback after one
  failure does not serialize separate processes.
- **Import `file_lock.py` directly.** Rejected: it bypasses the reusable-module catalog and
  leaves its public contract, dependency, and platform evidence unselected.
- **Use a runner, queue or polling loop as a lock.** Rejected: delivery infrastructure does not
  provide mutual exclusion and adds unrelated lifecycle complexity.
