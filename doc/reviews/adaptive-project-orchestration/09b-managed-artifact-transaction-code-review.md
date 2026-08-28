# R09B Managed-Artifact Transaction — Code Review

| Field | Value |
| --- | --- |
| Review identity | `REVIEW-ADAPTIVE-R09B-MANAGED-ARTIFACT-TRANSACTION-01` |
| Ticket authority | `TICKET-ADAPTIVE-R09B-MANAGED-ARTIFACT-TRANSACTION` revision `r09b-01` on `main` at `a0312bf0c1c4bac157b3c9a2905d9a04ab5313ca` |
| SPEC / Context | Adaptive Project Orchestration Revision 10 / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09` |
| Reviewed candidates | Initial `3817194c5861e7f8ea12a5a33f88667e4c89ad4e`; one additive correction `0f031bb363fcddcb56c276ec99a28205fc5c9968`; branch `implement/adaptive-r09b-managed-artifact-transaction` |
| Roles | Luna/xhigh implementation owner; current Terra/xhigh reviewer and sole integration owner; two independent Terra/xhigh reviewer-owned evidence lanes per candidate |
| Conclusion | `BLOCKED / CONVERGENCE_REVIEW_REQUIRED / MODEL_CAPABILITY_INSUFFICIENT / NOT_INTEGRATED` |

## Admission and isolation

The reviewer read the exact ticket, Revision 10 SPEC, sealed Context, ADR-031, actual candidate
diffs, branch ancestry and implementation worktree status. Both candidate commits descend from the
ticket baseline; the worktree was clean at each return. The implementation owner neither committed
nor pushed. The reviewer committed each candidate only to bind a stable SHA for review; neither
candidate entered `admit_document_mutation`.

The lane was same-lifetime synchronous and used no runner, durable queue, receipt, descriptor,
gateway or host-workspace readback. All behavior probes used disposable local Git repositories.
XSS, UI, Secret, provider, network, release and deployment surfaces are not applicable to this
candidate; target authority remains R09C and no real target repository was changed.

## Initial review and adversarial evidence

The initial candidate returned green focused/regression/type/compile commands but failed six
frozen cells. The reviewer independently reproduced a durable replacement that raised after
writing and left a later candidate file, a post-preflight competing write overwritten as
`APPLIED`, a Windows junction that wrote outside the disposable workspace, a valid document digest
not bound to its snapshot node, a mixed-lifecycle ABSENT prefix, and missing required result fields
accepted by defaults.

The required `AdversarialReviewPlan` attacked `ERROR_PARTIAL_FAILURE`, `CONSISTENCY`,
`CONCURRENCY` and `IDEMPOTENCY`; the separately permitted HIGH_ASSURANCE read-only helper attacked
`SPEC_GAP`, `BOUNDARY_DATA`, `STATE_TRANSITION`, `REGRESSION` and `OBSERVABILITY`. Both returned
candidate-bound `FINDINGS`. The reviewer confirmed them before requesting the one allowed additive
same-ticket correction.

## Correction review and convergence finding

Correction candidate `0f031bb363fcddcb56c276ec99a28205fc5c9968` correctly makes missing result
fields invalid, rejects real Windows junctions, binds document digests to snapshot nodes and rejects
mixed lifecycle. It also restores ordinary durable-then-raise update/delete paths. These are closed
evidence, not approval.

Three blocking properties remain:

1. **CAS has an external-writer overwrite.** When a target differs after preflight, the candidate
   returns `REJECTED / PATH_STATE_MISMATCH` but its abort routine restores every preflight entry,
   including an entry never written by this transaction. The reviewer injected independent content
   after preflight; final bytes were the stale preflight baseline, not the independent content.
   A change injected after the final comparison can also be replaced without detection.
2. **Persistent recovery/cleanup failure leaves an unprovable partial state.** The reviewer made
   the second replacement durable-then-failing and all rollback replacements fail. The result was
   `STORAGE_UNAVAILABLE`, but two files retained candidate bytes. A persistent temporary cleanup
   failure similarly leaves residue. A finite failure code detects this state but does not satisfy
   MAT5's required restored state/no residue.
3. **Post-proof error policy is internally contradictory.** The ticket requires a finite sanitized
   result for a failed post-state proof and also forbids broad error normalization. The correction
   propagates a forced resolver `RuntimeError` after restoration; the reviewer observed the raw
   exception rather than a finite result. Catching it broadly would conflict with MAT8, while the
   approved closure declares no typed resolver-fault/recovery result.

The second independent adversarial pass against the correction candidate reproduced the first two
items and independently reported the third. The Terra reviewer also reproduced persistent rollback
failure and resolver escape directly. Therefore this is the permitted correction review, not a
third implementation iteration.

## Executed evidence

Commands were run directly with unfiltered output on the candidate worktree:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_managed_artifact_transaction.py
  initial: 14 passed, 1 skipped
  correction: 17 passed, 2 skipped
py -3.11 -m pytest -q -p no:cacheprovider tests/test_target_document_management.py tests/test_workflow_artifact_tree.py tests/test_managed_artifact_planning.py
  31 passed, 35 subtests passed
py -3.11 -m mypy --strict library/workflow_router/target_document_contracts.py library/local_orchestration/target_document_management.py tests/test_managed_artifact_transaction.py
  Success: no issues found in 3 source files
py -3.11 -m compileall -q library/workflow_router/target_document_contracts.py library/local_orchestration/target_document_management.py
  exit 0
git diff --check a0312bf0c1c4bac157b3c9a2905d9a04ab5313ca 0f031bb363fcddcb56c276ec99a28205fc5c9968
  exit 0
```

Reviewer-owned probes also produced the following discriminating counter-evidence, then discarded
the disposable repositories: durable second replacement plus persistent rollback failure left
candidate root/partition bytes; a forced resolver fault escaped while filesystem restoration held;
and an injected competing write was rejected but replaced with the stale prior bytes. The source
candidate was not modified for any review probe.

## Required continuation

`AUTO_CONTINUE` is unavailable. The Router result is
`WAIT_FOR_HUMAN / ARCHITECTURE_OWNER_REQUIRED` with
`MODEL_CAPABILITY_INSUFFICIENT` and `UPSTREAM_DECISION_REQUIRED` evidence. The owner must choose
and approve a revised architecture/SPEC/ticket closure that defines: (a) durable recovery state and
restart behavior when restoration/cleanup cannot complete, (b) CAS/lock ownership and behavior for
cooperating versus uncooperative writers, and (c) finite dependency-fault mapping without raw error
leakage. Only after that sealed decision may the reviewer open a successor ticket or ask for the
single-ticket implementation-model escalation allowed by the Profile.

No source candidate was integrated, pushed, released, published, installed or deployed. R09C, R09D
and R09E remain unopened and unauthorized.
