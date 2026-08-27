# ADR-20260827-027 — Lock-bound telemetry transaction protocol

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner (Revision 07 authority) and architecture owner
- Related change: `PRD-20260827-041` / `CHG-20260827-041`
- Refines: `ADR-20260827-025` and `ADR-20260827-026`; it does not change public storage DTOs or
  authorize composition, provisioning or external effects.

## Context

The delivered lock port and corrected per-stream ledger now provide the required exclusion and
ownership substrates. The missing piece is a closed private protocol for one adapter to recover
interruption, mutate stream bytes, advance ledger lifecycle/revision and return the existing five
finite public operations without letting an implementer choose transaction semantics ad hoc.

## Decision

1. The private adapter is the only controlled legacy codec reader and implements existing
   `TelemetryStoragePort`. It holds the exact lock, recovers, re-admits the owned entry, then
   performs the operation. `JsonlContextUsageStore.append` remains prohibited.
2. `APPEND`, `DETACH` and `UNINSTALL` use a strict journal plus pre/post stream snapshots under
   the identity-derived transaction directory. Phases are `PREPARED`, `STREAM_APPLIED` and
   `LEDGER_APPLIED`; recovery accepts only the named complete pre/post grids, otherwise retains
   the journal and returns `STORAGE_BOUNDARY_VIOLATION`.
3. A domain-separated hash of identity, request revision, operation, lifecycle, locator and
   pre/post stream digests produces the deterministic next `rev-...` value. `VALIDATE` derives
   its opaque report ref from identity, unchanged revision and canonical validator report JSON;
   no report file is persisted.
4. `READ`/`VALIDATE` recover and re-admit under the same lock but retain expected revision.
   `DETACH`/`UNINSTALL` remove only their owned stream and write the matching ledger tombstone.
   Any release failure overrides an otherwise completed result.

## Consequences

- The next closure is one high-assurance private adapter ticket: `contracts <- adapter <-
  composition`; composition stays separate.
- Required proof covers all five response matrices, interruption at every phase/restart,
  incompatible journal state, real lock contention, under-lock TOCTOU, deterministic mutations,
  release failure, containment and target isolation.
- The protocol does not create public provisioning, legacy aggregate migration, provider/host,
  pricing, target-project, publication, release or deployment capabilities.

## Alternatives rejected

- **Update stream then ledger without a journal.** An interruption exposes a mixed state.
- **Use caller revision to decide recovery.** A caller can be stale; recovery first reads current
  immutable identity under lock and then performs ordinary admission.
- **Persist a validation report.** It introduces a new durable lifecycle with no current
  consumer; the response needs only deterministic opaque evidence.
