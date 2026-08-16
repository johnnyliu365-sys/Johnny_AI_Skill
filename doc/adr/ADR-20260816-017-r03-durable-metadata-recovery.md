# ADR-20260816-017: R03 durable metadata recovery and review isolation

- Date: `2026-08-16 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision maker: Project owner
- Trigger: `CR-R03-01-001` / review commit `6569cd41bbf3ecbc04108da4150c30267951dda5`
- Related change: `PRD-20260816-028` / `CHG-20260816-028`
- Related specification: Receipt-bound Role Supervision Revision 05 draft

## Context

The first R03-01 bootstrap implementation produced strict contracts and a forwarding adapter,
but the only persistence exercised by tests was an in-memory fake. The repository contains
`MetadataEventStorePort`, `InstallLedgerPort` and their fake implementations, but no production
installer-owned journal/checkpoint adapter that can be reused by the live registry or receipt
store. The frozen ticket also combined three independently observable closures and used a
strict-mypy command that discovers one staging fixture under two module identities.

Independent review then executed write-producing tools in the Implementer worktree and left
ignored cache/runtime residue. This did not change the implementation finding, but it violated
the role/worktree isolation objective and made clean-state evidence harder to interpret.

## Decision

1. Preserve the failed grant, implementation and review as immutable evidence. Do not correct,
   amend, reset, integrate or silently reuse them.
2. Replace the failed umbrella closure with four ordered stages:

   ```text
   R03-01A public contracts
       -> R03-01B durable owned-state transaction substrate
       -> R03-01C approved-artifact registry
       -> R03-01D TicketReceipt CAS store
       -> R03-02 admission/claim/settlement
       -> R03-03 live gateway/supervision proof
   ```

3. Implement the durable substrate as Windows per-user, Python-standard-library production
   source behind an injected Johnny-owned-root capability. It uses an exclusive one-shot file
   lock, digest-derived owned partition, framed journal records and a generationed checkpoint
   written through flushed same-directory temporary replacement. It introduces no database,
   service, target-project file or external package.
4. Recovery admits only a complete old or new generation. A prepared record plus an unchanged
   checkpoint is uncommitted; a matching advanced checkpoint is settled idempotently; torn,
   competing or mismatched evidence returns a finite recovery failure and performs no domain
   operation. There is no timed retry or recurring read.
5. Keep the journal bounded by checkpoint settlement and compaction under the same lock. Git
   artifacts remain the durable audit trail; the runtime journal is recovery state, not an
   append-only project history.
6. Use explicit-package-base strict typing with repository-external cache. Independent review
   materializes the exact candidate commit in reviewer-owned disposable storage and runs every
   write-producing verifier there. Read-only Git/diff/ancestry inspection may still target the
   original repository.

## Alternatives

| Alternative | Decision |
| --- | --- |
| Continue the failed R03-01 with a correction grant | Rejected: the ticket has multiple closures and its one-shot grant is consumed. |
| Treat the existing Protocol and in-memory fake as durable | Rejected: restart and interruption behavior remain simulated. |
| Add SQLite or an external database/service | Rejected: violates the approved detachable, dependency-minimal local boundary. |
| Put the durable substrate and registry in one Luna ticket | Rejected: transaction recovery and registry semantics are separately observable effect boundaries. |
| Run review directly in the Implementer worktree and clean afterward | Rejected: the reviewer would mutate another owner's workspace and contaminate evidence. |
| Reviewer-owned disposable clone/root | Adopted: exact commit bytes are testable without new branch authority or Implementer-worktree writes. |

## Consequences

- The bootstrap sequence is longer, but every implementation Context is smaller and a failed
  closure can be corrected without reloading registry, receipt and persistence concerns together.
- R03-01A through R03-01D remain no-receipt bootstrap phases and each needs a fresh exact owner
  grant. Normal receipt authority begins only after R03-01D is independently reviewed and
  integrated.
- The file adapter is Windows-specific in version one. Unsupported platforms return a typed
  capability result; they do not select a fake or database fallback.
- Review consumes bounded disk/CPU in a disposable root but avoids extra model turns caused by
  residue disputes. No heartbeat, automation, cron, watchdog or polling is added.

## Approval

- Project owner approved the exact decision on `2026-08-16 (Asia/Taipei)` from draft commit
  `c64681e847c1a6847c2588d127ed7f2749c914b5`.
- Approval authorizes SPEC sealing and Senior decomposition only. Workflow, CodeReview and
  executable Router policy remain unchanged until a separate policy-correction ticket is
  admitted, implemented and reviewed.
