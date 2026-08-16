# Revision 05 Context — R03 ticket-defect recovery

| Field | Value |
| --- | --- |
| Lifecycle | `ARCHITECTURE_COMPLETE / GRILL_CONVERGED / SPEC_DRAFT_PENDING_OWNER_APPROVAL` |
| Trigger | `CR-R03-01-001` at `6569cd41bbf3ecbc04108da4150c30267951dda5` |
| Prior implementation | `224b0242df876f6a41fd1b7e8f139195e9f40e42` / `NON_INTEGRABLE / EVIDENCE_ONLY` |
| Requirement | `PRD-20260816-028` / `CHG-20260816-028` |
| ADR | `ADR-20260816-017` |
| Parent Context | `doc/context/receipt-bound-role-supervision/main.md` Revision 04 |

## Scoped facts

- The failed ticket contained three separately observable domain closures: public contract
  validation, approved-artifact registration, and TicketReceipt issue/read CAS behavior.
- The assumed production installer-owned journal/checkpoint adapter does not exist in the current
  source tree. Existing `MetadataEventStorePort` and `InstallLedgerPort` production paths stop at
  Protocols/in-memory fakes, so another ticket cannot truthfully claim durable behavior by
  injecting them.
- Revision 03 already forbids a new database/service/MCP store and fixes live state beneath the
  Windows per-user Johnny-owned root. The missing production boundary must therefore be a local,
  standard-library, owned-filesystem transaction adapter rather than a new Provider choice.
- The smallest dependency-complete recovery chain is contracts, durable transaction substrate,
  artifact registry, then receipt CAS. Registry and receipt behavior share the substrate but
  remain separately testable domain closures.
- The strict-type failure is caused by the ticket command omitting the repository's established
  explicit-package-base mode. It is a verification-contract defect, not authority to modify the
  staging fixture from the R03 scope.
- A reviewer command created ignored cache/runtime residue in the Implementer worktree. Future
  write-producing review commands must execute in reviewer-owned disposable storage; a reviewer
  never cleans another owner's worktree.
- The failed implementation commit may be referenced as negative evidence only. Any selective
  source reuse requires a future exact ticket to name the source commit and reviewed finding;
  cherry-pick or implicit continuation is not authorized.

## Closed architecture decisions

1. Keep the root SPEC as the one effective feature specification and store Revision 05 detail in
   an indexed revision leaf so later roles load only the affected closure.
2. Use one typed `LiveDispatchMetadataState` and generation CAS port shared by later registry,
   receipt and claim behavior. Dynamic dictionaries/unvalidated blobs never cross inward.
3. Use a digest-derived per-project/ticket partition under an injected owned-root capability.
   Public requests and Router state never carry its filesystem locator.
4. Use one non-recurring exclusive lock acquisition, prepared/committed framed journal records,
   flushed same-directory checkpoint replacement and exact recovery readback. Contention or
   ambiguity fails closed without retry loops.
5. Keep recovery state bounded after a settled checkpoint; target-owned Git evidence, not the
   runtime journal, is the long-term audit trail.
6. Require focused strict typing during implementation and one isolated full verification during
   review. Both use `--explicit-package-bases --no-incremental` and repository-external cache.
7. Replace the no-receipt bootstrap phase with four exact phase IDs. Every phase still needs an
   owner-approved one-shot grant and user return relay; R03-02/R03-03 behavior otherwise remains
   unchanged.

## Boundaries

- No ticket, owner/task/worktree/branch/model binding, grant, receipt, dispatch or integration is
  selected by Architecture.
- No heartbeat, recurring wait/read, polling, scheduler, watchdog, database, network service,
  external dependency, target-project state, push, release or deployment.
- Revision 05 is not effective before exact owner approval. Until then no replacement ticket is
  dispatchable and R03-02/R03-03 remain blocked.
