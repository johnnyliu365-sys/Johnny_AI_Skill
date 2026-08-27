# ADR-20260827-026 — Per-stream ownership-ledger readiness

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner (Revision 07 authority) and architecture owner
- Related change: `PRD-20260827-041` / `CHG-20260827-041`
- Refines: `ADR-20260827-025`; it does not alter any public telemetry-storage contract or
  authorize a telemetry storage operation.

## Context

Ticket 10 correctly kept the ownership ledger private and pre-provisioned, but its single
`ownership-ledger/ledger.json` document contains entries for every stream. The later lock port
locks one exact stream identity, not every stream. Two holders of different stream locks could
therefore read the same aggregate document and each replace it, losing a successful update from
the other stream. The next transaction adapter must not be built on that representation.

Recovery also needs to locate a current owned entry after an interruption before it can know
whether a caller's expected revision is the pre-state or post-state revision. Reusing ordinary
revision admission for that lookup would force recovery to trust the caller revision or guess.

## Decision

1. Store each private ownership entry in a durable document derived only from the exact
   `(storage_ref, project_id, stream_id, ownership_ledger_ref)` identity. The derivation is
   domain-separated SHA-256 and the internal path passes containment before every filesystem
   effect. One exact stream lock now serializes the only ledger entry it can mutate.
2. The private port offers a recovery-only immutable-identity lookup. It ignores a supplied
   storage revision, matches the four immutable coordinates, and returns the current entry
   without provisioning, lifecycle admission or mutation. After recovery, ordinary operations
   still require exact expected-revision and lifecycle admission.
3. The former aggregate `ownership-ledger/ledger.json` shape is not silently migrated,
   interpreted or repaired by controlled storage code. It is not a valid per-stream entry.
4. Before the lock-bound transaction adapter, a separately reviewed ledger-readiness correction
   must prove independent processes updating different exact streams preserve both entries.

## Consequences

- The ledger-readiness correction remains private: it changes no package export, public DTO,
  composition root, legacy codec, lock port or provisioning surface.
- The later adapter can now use the existing exact stream lock as a valid serialization boundary
  for journal recovery, stream mutation and ledger CAS.
- The correction is `HIGH_ASSURANCE` because it writes durable ownership state; it is still a
  fully closed single private seam suitable for Luna/xhigh implementation and Terra/xhigh review.

## Alternatives rejected

- **Keep one aggregate document and rely on per-stream locks.** Rejected: those locks do not
  serialize two different streams, so lost update remains possible.
- **Add a global ledger lock.** Rejected for this POC closure: it broadens contention and lock
  ownership beyond the exact-stream contract without solving the per-stream representation
  mismatch as directly.
- **Migrate or repair the aggregate file on lookup.** Rejected: it creates an implicit
  provisioning/repair effect and makes caller-facing storage operations own compatibility work.
