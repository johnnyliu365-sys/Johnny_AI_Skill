# Code Review — Lock-bound storage contracts

| Field | Value |
| --- | --- |
| Feature | context-load-telemetry |
| Ticket / closure | 07-lock-bound-storage-contracts / CLOSURE-CONTEXT-TELEMETRY-07-LOCK-CONTRACTS revision 03 |
| Candidate | 0ded2ed4055fb4199f963395a45fb337e3e05ee8 |
| Reviewer | Terra/xhigh reviewer in root session |
| Conclusion | APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED |

## Admission and scope

- Ticket SHA revision 02: c65ebd919d70669b871e88f0115a0ffac4904271cdcde7805082a81d0ca619ea.
- Baseline was aefe9e65e79024c4c3c2bd9283e5ac7257cb7fa8 after the ticket-boundary correction.
- The candidate changes exactly four declared paths: telemetry storage contracts, their re-exports,
  the focused contract suite, and this ticket's element leaf.
- It realizes only Revision 04's metadata-only lock DTO/Protocol closure. There is no actual
  cross-process lock, stream or ledger adapter, file_lock import, provider/host call, runner,
  network, Git effect from source, target-project mutation, pricing claim or release.

## Findings

No blocking implementation, evidence, ticket or requirement finding remains.

The first guarded-integration attempt refused BOUNDARY_UNDECLARED. The ticket declared its
boundary with a tilde fence, while the real gate accepts only the canonical johnny-boundary fence.
The refusal left main unchanged. This was a TICKET_DEFECT, not an implementation correction:
ticket revision 02 corrected the fence and index hash only. The reviewed source blobs for all four
candidate files were byte-identical before and after candidate rebase.

## Evidence

| Check | Result |
| --- | --- |
| Focused contract suite | 21 passed |
| Strict type check | mypy --strict passed for contracts, re-export and focused tests |
| Compile gate | compileall passed for both contract modules |
| Candidate formatting | git diff --check passed |
| Boundary / ancestry | candidate descends from the corrected main baseline; exactly four declared paths changed |
| Implementer mutations | LM1 through LM4 each made named coverage red and were restored |
| Independent reviewer mutation | Changing the real TelemetryStorageLockReleased default from RELEASED to LOCK_ACQUIRED made TestValidContracts.test_lc1_valid_lock_shapes_and_typed_fake_round_trip fail with the expected finite discriminant validation error; byte-exact restoration returned all 21 tests green |
| Gate | admit_document_mutation returned INTEGRATED with integrated_commit equal to candidate SHA |
| Authority readback | non-force push to origin/main followed by direct remote SHA readback equalled candidate SHA |

## Closure mapping

- LC1: ordinary validated lock request, complete identity token, acquire/contended/release results
  and a typed fake port are covered.
- LC2 and LC3: strict grammar/nullability/extra-field/decision/response-shape rejection and all
  required token identity coordinates are covered.
- LC4: LOCK_CONTENDED is a finite TelemetryStorageFailure only; it cannot appear as a completed
  storage result.
- LC5 and LC6: the inherited AST allowlist continues to reject effectful/deferred imports and the
  lock port exposes only try_acquire and release; focused verification is green.

## Follow-up

The next dependency is not another source change to this ticket. ADR-20260827-022 requires a
delivered MODULE_CATALOG card and explicit reusable-capability selection before any real
cross-process lock adapter or reopened storage-adapter closure.
