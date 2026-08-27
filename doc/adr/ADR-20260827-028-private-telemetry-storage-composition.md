# ADR-20260827-028 — Private telemetry storage composition

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260827-041` / `CHG-20260827-041`
- Refines: `ADR-20260827-025` through `ADR-20260827-027`; it authorizes no provider, host,
  provisioning, target-project, publication, release or deployment effect.

## Context

Ticket 12 delivered the lock-bound transaction adapter but deliberately left it unbound. The
existing port contract is complete, and the ledger, local lock adapter and transaction adapter
all take the same injected `JohnnyRootLayout`. Leaving callers to recreate that dependency graph
would duplicate production binding and create an opportunity to mix lifetimes or layouts.

## Decision

1. `library/local_orchestration/telemetry_storage/composition.py` is the sole production binding
   point. Its one factory accepts a valid injected `JohnnyRootLayout` and returns the existing
   `TelemetryStoragePort`.
2. Each factory call creates one fresh `LocalTelemetryOwnershipLedger`,
   `LocalTelemetryStorageLockAdapter`, and `JohnnyOwnedTelemetryStorageAdapter`, all over the
   exact supplied layout. It has no module cache, singleton, registration or ambient
   configuration read.
3. Construction performs no storage operation and creates no Johnny-root, ledger, lock, stream,
   journal or report state. The factory is not re-exported from the storage-contract package;
   consumers depend on the port, while tests may replace it with a fake.
4. The composition closure changes no public storage DTO, legacy codec, ownership/lock/adapter
   behavior, provisioning protocol, provider/host boundary or target-project behavior.

## Consequences

- The next ticket is one low-model-ready, source-only composition closure with direct type and
  no-effect tests. It may create the composition module, its tests and its target-owned element
  index only.
- A future caller-integration or provisioning ticket remains separate. A composition factory is
  an object graph, not evidence that any owned identity exists or that a storage operation was
  performed.

## Alternatives rejected

- **Expose the private adapter from `telemetry_storage.__init__`.** Rejected: it widens the
  contract package and invites callers to choose private dependencies themselves.
- **Cache one global port.** Rejected: it makes layout/lifetime selection ambient and obscures
  test replacement.
- **Bind on first storage request.** Rejected: it would combine composition with invocation and
  violate the no-effect scope.
