# Receipt-bound Role Supervision Revision 05 — R03 ticket-defect recovery

| Field | Value |
| --- | --- |
| Kind | `SPEC_REVISION_LEAF` |
| Lifecycle | `DRAFT / OWNER_APPROVAL_PENDING / NON_DISPATCHABLE` |
| Parent SPEC | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` |
| Requirement | `PRD-20260816-028` / `CHG-20260816-028` |
| Context | `doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md` |
| ADR | `ADR-20260816-017` |
| Trigger evidence | `doc/reviews/receipt-bound-role-supervision/R03-01-bootstrap-code-review.md` / `CR-R03-01-001` / `6569cd41bbf3ecbc04108da4150c30267951dda5` |
| Language | Python 3.11, frozen/validated strong types, `mypy --strict` with explicit package bases |
| XSS | `N/A`; no renderer or JavaScript path |

This leaf is additive detail of the parent SPEC, not a second effective feature specification.
It becomes effective only after the project owner approves its exact revision. Until then the
Router remains `WAIT_FOR_HUMAN` and the original failed R03-01 cannot be corrected or replayed.

## Dependency graph and observable closures

```text
R03-01A CONTRACT_FREEZE
    -> R03-01B DURABLE_STATE_TRANSACTION
    -> R03-01C APPROVED_ARTIFACT_REGISTRY
    -> R03-01D TICKET_RECEIPT_CAS
    -> R03-02 TASK_ADMISSION_CLAIM_SETTLEMENT
    -> R03-03 LIVE_GATEWAY_SUPERVISION_PROOF
```

`R03-01A` is the permitted prior shared-contract ticket from the decomposition policy. Every
later stage is an independently observable effect or domain-state closure. A ticket may not merge
two stages merely because they use the same metadata file or Python package.

## Acceptance criteria

### AC-39 — Failed-attempt and change-control fence

`R03-01-CS-01`, `BDG-R03-01-20260816-001`, its attempt/result leaves, implementation commit
`224b0242df876f6a41fd1b7e8f139195e9f40e42` and `CR-R03-01-001` remain immutable historical evidence. The grant is consumed; the
implementation is `NON_INTEGRABLE`; the ticket is `TICKET_DEFECT`. No reset, amend, correction
grant, integration grant, receipt projection or silent source reuse is legal.

The failed commit may appear in a later ticket only as an exact non-authoritative reference with
the review finding. Reuse of any candidate bytes must be explicitly admitted and re-proved under
the new closure; historical tests are not evidence for the new ticket.

### AC-40 — Replacement bootstrap allowlist and phase order

After owner approval, the effective project-specific bootstrap policy replaces the original
R03-01 phase with exactly `R03-01A`, `R03-01B`, `R03-01C` and `R03-01D`, followed by the existing
R03-02 and R03-03 logical stages. No other project, ticket ID, revision or ordering is allowed.

R03-01A through R03-01D are no-receipt phases. Each requires one separately committed,
project-owner-approved `BootstrapDispatchGrant`, one claim-before-effect attempt and one user
return relay. A predecessor must be independently reviewed and integrated before the next phase
can be admitted. Only reviewed R03-01D integration may allow R03-02 receipt issuance. R03-02 and
R03-03 keep the Revision-04 real-receipt plus one-shot transport-grant rule.

Architecture defines these logical phases but does not create the tickets or choose any
implementation owner, task, worktree, branch, baseline, model, Context view or dispatch action.

### AC-41 — R03-01A public contract freeze

R03-01A owns only ordinary constructors/validators/serialization for the existing
`ApprovedDispatchArtifactRecord`, registry request/result, `TicketReceipt`, receipt request/result,
claim state and the following durable boundary. It performs no filesystem, lock, registry,
receipt, claim, host or Agent effect.

```text
enum DurableMetadataReadKind {
  EMPTY, FOUND, LOCK_UNAVAILABLE, CORRUPT_STATE, STORAGE_UNAVAILABLE
}
enum DurableMetadataWriteKind {
  COMMITTED, ALREADY_COMMITTED, GENERATION_CONFLICT,
  LOCK_UNAVAILABLE, RECOVERY_REQUIRED, STORAGE_UNAVAILABLE
}
enum DurableJournalPhase { PREPARED, COMMITTED }

struct LiveDispatchMetadataState {
  MetadataSchemaRevision schema_revision;
  MetadataPartitionRef partition_ref;
  MetadataGeneration generation;
  ApprovedDispatchArtifactRecords artifact_records;
  TicketReceipts ticket_receipts;
  DispatchOperationClaims dispatch_claims;
  ContentDigest state_digest;
}

struct DurableMetadataReadRequest {
  MetadataOperationId operation_id;
  MetadataPartitionRef partition_ref;
  ContentDigest request_digest;
}

struct DurableMetadataReadResult {
  DurableMetadataReadKind kind;
  optional<LiveDispatchMetadataState> state;
  optional<DispatchFailureRef> failure_ref;
  ContentDigest result_digest;
}

struct DurableMetadataWriteRequest {
  MetadataOperationId operation_id;
  MetadataPartitionRef partition_ref;
  MetadataGeneration expected_generation;
  LiveDispatchMetadataState candidate;
  ContentDigest request_digest;
}

struct DurableMetadataWriteResult {
  DurableMetadataWriteKind kind;
  MetadataGeneration observed_generation;
  optional<LiveDispatchMetadataState> state;
  optional<DispatchFailureRef> failure_ref;
  ContentDigest result_digest;
}
```

Success kinds require exact reconstructed state and no failure. Failure kinds require one finite
failure and no candidate state. IDs, generation, enums, tuple members, digests and nullability are
strict; `Any`, generic object/dictionary payload, cast, dynamic lookup, bypass constructor, raw
path/URI, prompt, Context, Secret or PII is rejected before a storage port call.

`MetadataPartitionRef` is derived from validated project/ticket identity. It is not a filesystem
path and cannot be supplied as an owned-root locator. `LiveDispatchMetadataState` already reserves
typed claim state so R03-02 can use the same durable boundary without changing its persistence
schema.

R03-01A also freezes `JohnnyOwnedStateRootCapability` as a runtime-only opaque capability. Its
ordinary admission factory compares one validated `OwnedInstallLedger` identity, the fixed
per-user Johnny root observation and the `runtime/live-dispatch/v1` owned-state registration,
then returns exactly `ADMITTED`, `LEDGER_MISMATCH`, `ROOT_MISMATCH` or `UNAVAILABLE`. The absolute
root is retained only inside the admitted adapter instance; the capability has no public
constructor, serializer, equality-copy path or raw locator field. A disposable test factory is a
separate test seam and cannot be imported by production composition.

### AC-42 — R03-01B real durable state transaction

R03-01B owns one concrete Windows standard-library adapter implementing the AC-41 state read/CAS
port. Production construction requires an unforgeable `JohnnyOwnedStateRootCapability` supplied
by the local runtime composition root. Tests may inject a disposable equivalent; a Protocol,
process-local map, singleton or test fake cannot be selected by production composition.

The adapter derives this fixed relative layout internally from the partition digest:

```text
runtime/live-dispatch/v1/<partition-digest>/state.json
runtime/live-dispatch/v1/<partition-digest>/journal.jsonl
runtime/live-dispatch/v1/<partition-digest>/state.lock
runtime/live-dispatch/v1/<partition-digest>/state.<operation-digest>.tmp
```

All locators are descendants of the proved owned root. The fixed
`runtime/live-dispatch/v1` subtree is registered as owned runtime state in the install ledger;
every derived descendant passes the owned-relative-path validator before creation or removal.
No caller/path/environment string crosses the domain interface.

The version-one Windows lock is one byte at offset zero of `state.lock`, acquired once with
standard-library `msvcrt.LK_NBLCK` after the adapter creates/validates that one-byte owned file.
The OS releases it on process death, so no stale model/owner token is persisted. Contention
returns `LOCK_UNAVAILABLE` without sleep, retry, timer or recurring read.

Under the lock, one write transaction executes in this order:

1. read and strictly validate checkpoint, journal tail, digests and current generation;
2. return the prior committed result for the same operation/digest, or reject replay/conflict;
3. compare `expected_generation` and candidate identity;
4. append one length/digest-framed canonical `PREPARED` record and flush it to stable storage;
5. write the complete next checkpoint to the same-directory operation temp file, flush it, and
   atomically replace `state.json`;
6. append and flush the matching `COMMITTED` frame;
7. read back checkpoint generation/digest before returning `COMMITTED`.

Recovery admits only these cases:

- complete checkpoint plus no open prepared frame: return that generation;
- one intact prepared frame plus the old checkpoint: treat the operation as uncommitted, remove
  only its proved owned temp residue, and permit only the exact same operation to retry;
- one intact prepared frame plus its matching advanced checkpoint: append the missing committed
  frame and return `ALREADY_COMMITTED`;
- torn frame, digest mismatch, unknown schema, multiple open preparations, competing operation or
  checkpoint/journal disagreement: `RECOVERY_REQUIRED` with no domain mutation.

After committed readback, the adapter compacts the journal under the same lock to one settlement
anchor plus any single open prepared frame. Compaction uses the same flushed temporary-replace
rule. Runtime recovery files therefore remain bounded; Git artifacts, not this journal, provide
long-term audit history. Every admitted `OSError`/locking/encoding failure maps to one finite
storage result; broad catch and false success are forbidden.

### AC-43 — R03-01C approved-artifact registry closure

R03-01C consumes only the integrated AC-41/AC-42 port. It registers and reads one immutable
approved-artifact record through generation CAS. Identical operation and bytes are idempotent;
same identity with changed project/ticket/revision/digest/commit/handoff/owner bytes is
`ARTIFACT_IDENTITY_CONFLICT`. Stale generation, closed record, unavailable/corrupt storage or
failed durable settlement returns its exact finite result and makes zero receipt/host calls.

The closure includes restart and interruption proof using a newly constructed concrete adapter
over the same disposable owned root. Reconstructing a second wrapper over one in-memory object is
not restart evidence.

### AC-44 — R03-01D TicketReceipt CAS closure

R03-01D consumes the integrated registry and durable state port. It issues/reads the one canonical
`TicketReceipt` only from an exact approved record and live pending descriptor. Same operation,
request digest and candidate returns the prior receipt. Changed identity, descriptor, generation
or a second `ACTIVE|QUARANTINED` receipt returns the existing finite conflict; revocation readback
must precede replacement. Delivery/claim settlement never consumes the receipt.

Receipt state and registry generation settle in one AC-42 transaction. Storage failure,
interruption or uncertain recovery never falls back to memory and never returns or dispatches a
new receipt. Restart proof constructs a new adapter instance over the same owned files and proves
the one-live-receipt invariant.

### AC-45 — Truthful strict-type and test verification

The obsolete `python -m mypy --strict library tests` command is not reused because it maps one
unchanged staging source to two module identities. New tickets resolve exact file arguments and
an external cache root, then use this semantic command shape:

```text
python -m mypy --strict --explicit-package-bases --no-incremental \
  --cache-dir <owned-external-cache> <exact-ticket-files-and-direct-contracts>
```

Implementers run the focused ticket tests and exact strict file set in their own worktree.
Independent review runs the focused, affected-regression and one full repository matrix exactly
once over the candidate commit in reviewer-owned disposable storage. The full strict command uses
the same flags over `library tests`. Python tests use `-B`; cache, bytecode, temporary roots and
runtime state must be outside the source checkout or inside the disposable review copy and be
read back absent after disposal.

The explicit-package-base option fixes module identity only; it may not hide or exclude a changed
source error. A failing changed file, direct public contract or reverse-mutation gate remains a
blocking type/evidence defect.

### AC-46 — Independent review workspace isolation

The Senior may read implementation Git refs, diff, ancestry, porcelain and committed handoff
evidence without mutation. Before running any command that can write cache, bytecode, test output,
temporary runtime data or build artifacts, the Senior creates a local `git clone --no-hardlinks`
inside a Senior-owned disposable root, checks out the exact candidate commit detached, and reads
back the exact HEAD/tree identity. That root has no implementation authority, branch reuse or
target-project content.

The Senior removes only that proved disposable root after evidence capture. It never cleans,
resets, stashes, checks out, creates a branch in, or deletes residue from an Implementer worktree.
If the candidate worktree was already contaminated, review reports the exact owner/residue and
uses committed bytes; cleanup is a separate owner-authorized action and not a reason to alter the
finding.

### AC-47 — Revision-05 transition fence

Owner approval authorizes the Senior to add a fresh decomposition decision and exact ticket
leaves only. Every ticket must still pass schema, low-model/capability admission and receive its
own bootstrap grant. Approval creates no execution owner/task/worktree/branch/model selection,
grant, receipt, dispatch, integration, normal activation, push, release or deployment.

No Workflow, CodeReview or executable Router rule changes before this revision is approved and a
separate implementation/policy correction is admitted. All no-heartbeat, manual-relay,
claim-before-effect, uncertain-effect and normal-activation rules remain in force.

## Required verification matrix for later ticketing

1. Contract tests cover every field, finite status, nullability, canonical round trip, wrong
   union member, duplicate identity and dynamic/bypass rejection.
2. Durable transaction tests cover first write, read, same-operation idempotence, generation
   conflict, two-process lock contention, restart, prepared-before-checkpoint interruption,
   checkpoint-before-commit interruption, torn/mismatched evidence and bounded compaction.
3. Registry tests cover exact registration/read, identical idempotence, every identity collision,
   stale/closed/unavailable state and zero downstream calls after a failed durable transition.
4. Receipt tests cover exact issuance/read, duplicate request, descriptor mismatch, competing
   receipt, revocation-before-replacement, restart and survival after later claim settlement.
5. Source/composition gates reject fake production selection, process-local state, raw locator,
   target-project persistence, SQLite/database/service/MCP/network use, unbounded journal,
   heartbeat, recurring read, polling, sleep/retry loop and broad catch.
6. Review-isolation evidence proves candidate bytes equal the implementation commit, all
   write-producing tools ran only in reviewer-owned disposable storage, the disposable root was
   removed, and the Implementer worktree received no reviewer write.

## Rollback and compatibility

- Before approval, delete/revert only this draft's docs commit; no runtime/source effect exists.
- After approval, a future implementation rollback reverts only the independently integrated
  stage commit in reverse dependency order. It never rewrites the failed historical branch or a
  target repository.
- Existing Revision-01 through Revision-04 evidence remains readable. Revision 05 changes only
  the failed bootstrap decomposition, persistence truth and review-execution boundary.
