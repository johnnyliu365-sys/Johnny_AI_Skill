# ADR-20260827-025 — Pre-provisioned telemetry storage transactions

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260827-041` / `CHG-20260827-041`
- Amends: `ADR-20260827-022` for controlled durable stream and ownership-ledger state. It does
  not alter provider-usage evidence, pricing, target isolation, publication, release or host
  effects.

## Context

The delivered local lock port establishes exclusive access but deliberately does not read a
ledger, mutate stream bytes or advance lifecycle. The legacy path-taking JSONL append helper is
not a transaction: after a process interruption it can leave stream bytes and an ownership-ledger
lifecycle or revision out of agreement. Allowing a storage operation to create an entry on demand
would also make caller-supplied identity or location an authority source.

## Decision

1. A controlled `TelemetryStoragePort` operation may act only on an already provisioned,
   Johnny-owned ledger entry matching its exact opaque storage identity, project and stream. No
   storage operation creates, registers, repairs or discovers an entry from a caller-supplied
   root, path or identity.
2. A private `TelemetryOwnershipLedgerPort` resolves that entry, current lifecycle and revision,
   derives an internal relative locator and offers compare-and-swap lifecycle/revision advance.
   It exposes no public create, path or root capability.
3. `APPEND`, `DETACH` and `UNINSTALL` write a durable transaction journal before altering stream
   bytes or ledger state. Recovery runs under the exact stream lock and completes to the complete
   pre-operation state or complete post-operation state, never a mixed state.
4. `READ` and `VALIDATE` acquire the same exact lock, recover a pending transaction, and re-read
   exact ledger ownership, lifecycle, revision and containment before decoding the stream.
5. `JsonlContextUsageStore.append` is prohibited in the controlled adapter. Only strictly
   validated record decoding may remain internal to that adapter.
6. Lock contention remains `LOCK_CONTENDED` with no effect. A malformed ref, ownership mismatch,
   closed lifecycle, invalid record and owned-boundary failure retain their existing finite
   decisions. A release failure overrides a completion result.

## Consequences

- The durable adapter is `HIGH_ASSURANCE`: its evidence includes independent-process contention,
  transaction-phase interruption, restart recovery, compare-and-swap conflict, containment
  rejection and target-isolation checks.
- Ticket 06 remains superseded. Its candidate must not be read, rebased or integrated.
- The implementation is split so a private ownership-ledger/CAS substrate is reviewed before the
  adapter that combines recovery, stream mutation and lifecycle advance. Composition remains the
  only producer of a public `TelemetryStoragePort`.

## Alternatives rejected

- **Auto-create on the first storage request.** Rejected: it promotes caller input into storage
  authority and obscures provisioning ownership.
- **Write JSONL and update the ledger afterward.** Rejected: interruption can expose partial
  state even with a lock.
- **Return a boundary error after a partial write.** Rejected: an error label does not restore
  the ledger/stream invariant or make recovery deterministic.
