# ADR-20260827-023 — Exclusive file-lock catalog admission

- Date: 2026-08-27 (Asia/Taipei)
- Status: ACCEPTED
- Decision makers: project owner and reviewer
- Related capability: exclusive-file-lock
- Related telemetry decision: ADR-20260827-022 / PRD-20260827-041 / CHG-20260827-041

## Context

Revision 04 requires every durable telemetry-storage operation to use an exclusive lock and
return a finite LOCK_CONTENDED result before stream, ledger or report effects. The repository
already contains library/local_orchestration/file_lock.py, but it had no MODULE_CATALOG card and
could not be selected or imported through the reusable-module process.

The owner authorized audit and catalog admission of that existing module. On this Windows host,
its direct process tests passed: 18 tests and 17 subtests establish exclusion, blocking, release,
abandoned-holder recovery, advisory semantics and the legacy alias. The module uses blocking
msvcrt.LK_LOCK on Windows; the existing test deliberately observes a waiter remain blocked for
three seconds while the primitive may later raise OSError after its bounded retry window.

## Decision

1. Catalog the existing module as exclusive-file-lock, READY only for its delivered blocking,
   cooperative-process exclusion behavior.
2. Preserve the existing ExclusiveFileLock and ExclusiveWindowsFileLock API and all current
   consumers unchanged. This admission copies no source and changes no executable behavior.
3. Record the capability's raw Path API, advisory semantics, Windows bounded-lock OSError and
   unproven POSIX runtime behavior as explicit constraints.
4. Reject direct selection for TelemetryStorageLockPort.try_acquire. The current module has no
   nonblocking finite contention outcome and does not distinguish a competing holder from other
   OSError causes. Calling it then relabeling every OSError as LOCK_CONTENDED would reproduce
   PITFALL-REGISTER C12.
5. Before a real telemetry lock adapter, create a separate capability closure for classified
   nonblocking acquisition while preserving the current blocking API. That closure must provide
   platform-specific process evidence and a public finite result before telemetry selects it.

## Consequences

The reusable catalog now has an honest, bounded descriptor for the existing primitive. It does
not unblock Ticket 06 or authorize a storage adapter. No telemetry source, provider, host, queue,
runner, target-project, secret, release or network behavior changes.
