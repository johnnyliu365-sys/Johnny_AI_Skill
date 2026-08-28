# ADR-20260829-034 — Remote Authority Commit mutation

- Date: `2026-08-29 (Asia/Taipei)`
- Status: `PROPOSED / OWNER_DIRECTION_A_SELECTED / EXACT_REVISION_APPROVAL_PENDING`
- Decision maker: Project owner
- Related change: `PRD-20260829-046` / `CHG-20260829-046`
- Supersedes on approval: the local-filesystem execution route of `ADR-20260828-033`; it does not
  weaken RWW6 or invalidate the completed capability evidence.

## Context

`CAP-RWW6-01` produced `NO` for each executed local tuple. A digest check followed by ordinary
file replacement, rename or unlink remains unable to preserve a lock-ignoring writer between the
last observation and the final syscall. Continuing to repair `f99d836` would therefore violate
RWW6.

The project already has an accepted authority-line architecture: only a non-force remote update
plus direct remote SHA readback is integration truth. A managed document tree can be represented
by an immutable candidate Git commit instead of by an in-place local filesystem mutation.

## Proposed decision

1. Replace the R09B2 local filesystem writer with a Remote Authority Commit route. The runtime
   never directly mutates the target worktree.
2. Treat the directly observed authority-ref commit SHA as the complete target-tree identity. A
   candidate commit contains every planned document change and has that SHA as its sole parent.
3. The only final mutation is a non-force, fast-forward-only update of the declared full authority
   ref, followed by direct remote SHA readback. Capability proof must show the authority ref also
   rejects force, ref deletion and ordinary bypass updates for the qualified writer identities;
   otherwise a ref-identity ABA return to an old SHA remains possible. Stale authority rejects with
   no target effect.
4. `--force`, ref deletion, reset, implicit rebase/merge, local worktree fallback and automatic
   retry are forbidden. Compensation after integration is a separately reviewed forward commit.
5. The first successor is an evidence-only capability investigation against the actual declared
   authority remote. It must prove a two-writer race from the same base: at most one authority
   transition succeeds, the loser is finite and the winner's complete tree remains reachable.
6. The capability contract is provider-neutral. A GitHub `expectedHeadOid` implementation may be
   admitted later as an adapter, but GitHub is not a required provider and provider credentials
   never enter the control-plane data model.

## Consequences

- R09B2 is superseded rather than corrected. Its current candidates remain defect evidence.
- The new route preserves the RWW6 direction: a competing writer that first advances the authority
  ref is not overwritten by this runtime.
- It changes the mutation boundary from local shared files to the declared remote authority
  service. A target worktree becomes a consumer checkout, not the runtime's write target.
- The actual remote's behavior, ref policy, permissions and direct readback remain unproved until
  the successor capability ticket completes. Unsupported, denied or unprovable remotes fail
  closed; there is no local fallback.

## Alternatives rejected

- **Continue R09B2 with final digest checks.** It retains the proved TOCTOU interval.
- **Disable all managed mutation permanently.** Safe but abandons the approved managed-artifact
  capability even where a remote authority can prove the required conditional transition.
- **Immutable local version paths.** Avoids overwrite only by changing reader, migration and
  version-selection semantics; it is a broader product rewrite than the authority route.
- **Provider-specific storage/database first.** Adds a new secret, retention and provider trust
  boundary before proving the existing declared Git authority path.

## Recovery

Before remote confirmation, withhold the candidate. If the remote response is ambiguous, direct
readback decides only whether the candidate is authoritative, the observed base remains current or
the authority has moved; no blind retry occurs. After authority integration, a forward commit from
a fresh observed head is the only correction mechanism.
