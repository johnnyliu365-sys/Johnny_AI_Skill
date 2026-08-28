# Remote Authority Commit Context

| Field | Value |
| --- | --- |
| Artifact ID / revision | `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260829-13` / `REVISION_13` |
| State | `ARCHITECTURE_DRAFT / GRILL_CONVERGED / OWNER_EXACT_APPROVAL_PENDING` |
| Requirement / ADR | `PRD-20260829-046` / `CHG-20260829-046` / `ADR-20260829-034` |
| Authority | Project owner selected Remote Authority Commit on 2026-08-29 (Asia/Taipei); this Context becomes sealed only with owner approval of the exact Revision 13 draft. |
| Supersession | Replaces Revision 12's local-filesystem implementation route only. It preserves RWW6, R09A planning, R09B1 result contracts, canonical resolution and the completed CAP evidence. |

## Confirmed facts

- `CAP-RWW6-01` qualified the currently executed Windows/NTFS, Linux/WSL DrvFS and
  CPython/NTFS tuples as `NO`. No local filesystem capability may execute the R09B2 write path.
- The declared authority-line model already makes a credential-free remote identity, a full
  authority ref and direct remote readback the integration truth. Local branches and
  `origin/<ref>` are diagnostics only.
- The authority ref must also reject force, ref deletion and ordinary bypass updates for the
  qualified writer identities. Otherwise a ref can return to a previously observed SHA and create
  an ABA gap that neither a fast-forward check nor direct readback can distinguish.
- A complete Git commit gives one immutable candidate document tree. A non-force fast-forward
  authority update can accept only a candidate that preserves the currently authoritative
  history; a competing authority writer therefore causes a finite rejection rather than an
  overwrite by this runtime.
- `R09B2`, `269a911` and `f99d836` remain non-integrated local-writer defect evidence. They are
  not a source, correction or fallback for this revision.
- The reusable-module catalog has no delivered `READY` card for a remote authority commit writer.
  This draft records a capability gap; it does not claim reuse of uncatalogued internal source.

## Architecture boundary and data pipeline

```text
validated ManagedArtifactPlan
  -> direct remote authority observation (full ref + commit SHA)
  -> isolated candidate-tree construction from that exact commit
  -> one direct-child candidate commit, with every planned document mutation
  -> non-force fast-forward authority transition
  -> direct remote readback
  -> AUTHORITY_INTEGRATED | STALE_AUTHORITY | PUSH_UNCONFIRMED | finite refusal
```

The candidate construction environment is disposable and is not the target worktree. It may hold
only the candidate Git object material needed for one attempt; it must not alter the caller's
worktree, index, HEAD, refs or remote-tracking refs. The authority transition operates only on the
declared full ref and only through the declared remote transport.

## Composition, lifetime and trust

- `RemoteAuthorityObservationPort` reads the authority ref directly and returns credential-free
  identity/SHA evidence.
- `RemoteAuthorityCommitPort` builds a direct-child complete candidate and requests the one
  non-force authority transition. It has no shared-worktree or local-filesystem target-write
  capability.
- The composition root injects the declared authority-line contract and opaque transport handle;
  credentials remain outside typed result, Router state, telemetry, logs and prompts.
- The remote authority service is the final mutation trust boundary. Arbitrary direct access to
  that service's private storage is outside the supported transport boundary; independent Git
  clients competing through the authority ref are in scope and must be preserved by rejection.
  Capability proof must also read back policy evidence that ordinary bypass, force and ref-delete
  paths are unavailable for the qualified authority identities.
- A successful authority commit is not a license to refresh, reset or check out another local
  worktree. Consumers may independently synchronize through normal repository workflow.

## Failure and recovery facts

`STALE_AUTHORITY`, remote policy rejection and unavailable transport have zero target effect. An
ambiguous delivery is resolved only by direct remote readback; unresolved state is
`PUSH_UNCONFIRMED` and stops. After an integrated authority commit, correction is a separately
reviewed forward candidate based on a fresh authority observation. Force/ref-delete/reset rollback
is forbidden.

## Boundary

This architecture draft opens no implementation lane and grants no source, credential, provider,
remote-test, push, publication, installation, release or deployment effect. The first successor,
if this Context and Revision 13 are approved, is evidence-only remote capability qualification.
