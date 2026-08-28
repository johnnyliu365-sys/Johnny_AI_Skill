# R09B1 — recoverable managed-artifact outcome contracts

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-R09B1-RECOVERABLE-MANAGED-ARTIFACT-CONTRACTS` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 11 / AC-17R11 and TDD item 24 (contract subset) |
| Requirement / Context / ADR | `PRD-20260828-044` / `CHG-20260828-044` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-11` (`42dc4e39c326e7791923b8be6785bf0cd46a54ba1ac63a12119837dbac3436a8`) / `ADR-20260828-032` |
| State / closure | `OPEN / APPROVED / NOT_DISPATCHED`; `CLOSURE-ADAPTIVE-R09B1-RECOVERABLE-MANAGED-ARTIFACT-CONTRACTS-01` |
| Approval authority | Project owner, 2026-08-28 (Asia/Taipei): approved Revision 11 at `e451cf13a1defe40f5a036a09805dcfc20c751f2` and authorized reviewer opening of one R09B successor ticket. This is the one contract-first successor; ticket dispatch remains a separate transition. |
| Source baseline / dependency | `0c59693bd9a9289b03cbb04998a6ea5173f74dd3`; R09A planner is integrated at `91da8135e301992635d716c6cefa068ad950d807`. R09B candidates `3817194c5861e7f8ea12a5a33f88667e4c89ad4e` and `0f031bb363fcddcb56c276ec99a28205fc5c9968` are read-only defect evidence, never source authority. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh; sole Agent-to-Agent orchestrator, final reviewer and sole integrator. |
| Implementation owner | `implementation-high-assurance` semantic profile — Luna/xhigh; one same-lifetime owner lane, no helper, no commit and no push. |
| Agent Context / worktree / branch | Allocate `SIDE-CONTEXT-ADAPTIVE-R09B1-20260828-01` only after ticket integration. Required implementation worktree `.worktrees/adaptive-r09b1-recovery-contracts`; branch `implement/adaptive-r09b1-recovery-contracts`; candidate must descend from this ticket's integrated authority baseline. Same-lifetime allocation needs repository-contained worktree and Git metadata proof, but no runner, queue, receipt, descriptor, gateway or host-workspace readback. |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11, strict Pydantic contracts, complete annotations, `mypy --strict`, ordinary public validators and JSON round-trips. The slice is `READY_LOW_MODEL`: it has one observable typed-contract closure, zero filesystem effect and no unresolved semantic decision. |
| XSS / effects | `XSS_NOT_APPLICABLE`. This ticket adds only provider-neutral value contracts and tests. It creates no recovery store, filesystem effect, lock acquisition, resolver call, Git mutation, host adapter, runner, queue, receipt, provider, publication, installation, release or deployment effect. |

## Boundary declaration

```johnny-boundary
modify = library/workflow_router/target_document_contracts.py
create = tests/test_managed_artifact_recovery_contracts.py
modify = tests/test_managed_artifact_recovery_contracts.py
create = modules/element/python/adaptive-project-orchestration/09b1-recoverable-managed-artifact-contracts/
modify = modules/element/python/adaptive-project-orchestration/09b1-recoverable-managed-artifact-contracts/
forbid = library/local_orchestration/
forbid = library/workflow_router/managed_artifact_planning.py
forbid = library/workflow_router/artifact_tree.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/__init__.py
forbid = tests/test_managed_artifact_planning.py
forbid = tests/test_workflow_artifact_tree.py
forbid = tests/test_target_document_management.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Add only additive, strict, public value contracts in `target_document_contracts.py`:

```text
ManagedArtifactWriteStatus = APPLIED | REJECTED | STORAGE_UNAVAILABLE | RECOVERY_REQUIRED

ManagedArtifactWriteFailure = BASELINE_MISMATCH | PATH_STATE_MISMATCH | PATH_ESCAPE
                            | STORAGE_UNAVAILABLE | POST_STATE_INVALID
                            | RUNTIME_INVARIANT_FAILED | RECOVERY_REQUIRED

ManagedArtifactWriteResult = {
  status,
  written_artifact_refs,
  written_digests,
  failure,
  recovery_ref
}

ManagedArtifactRecoveryResult = {
  status: RECOVERED | RECOVERY_REQUIRED,
  recovery_ref
}
```

`APPLIED` carries one or more canonical opaque artifact refs and matching content digests, with no
failure/recovery ref. `REJECTED` carries no writes, one non-storage/non-recovery failure and no
recovery ref. `STORAGE_UNAVAILABLE` carries no writes, exactly `STORAGE_UNAVAILABLE` and no
recovery ref. `RECOVERY_REQUIRED` carries no writes, exactly `RECOVERY_REQUIRED` and one opaque
`recovery_ref`. `RUNTIME_INVARIANT_FAILED` is a finite `REJECTED` failure and never carries raw
exception, path, snapshot, source body or filesystem details. `ManagedArtifactRecoveryResult`
always carries exactly one opaque recovery ref; `RECOVERED` and `RECOVERY_REQUIRED` are its only
finite states.

The existing `TargetDocument*`, legacy `DocumentWrite*`, managed-artifact request/plan contracts,
planner and resolver remain compatibility fixtures. This ticket does not construct a recovery
journal or a writer. The next serial ticket alone owns private snapshots, two-attempt recovery,
lock-bound revalidation and canonical resolver invocation.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `RRC1` | Ordinary public construction and JSON round-trip accept each valid `ManagedArtifactWriteResult` outcome and both valid `ManagedArtifactRecoveryResult` states. |
| `RRC2` | Validators reject missing/null/extra fields, wrong primitive types, non-opaque refs, empty/misaligned APPLIED write tuples, a recovery ref on a normal result, a missing recovery ref on `RECOVERY_REQUIRED`, and every status/failure mismatch. |
| `RRC3` | `RUNTIME_INVARIANT_FAILED` is representable only as finite `REJECTED` with zero writes/recovery ref; no serialized output contains a raw exception, target path, snapshot body or absolute workspace location. |
| `RRC4` | Existing `TargetDocumentMutation`, `TargetDocumentPlan` and `DocumentWriteResult` ordinary constructors and JSON round-trips remain unchanged. |
| `RRC5` | AST/source gates prove this ticket changes no planner, resolver, local adapter, package export or legacy contract behavior; every new public name is explicitly exported only from this same contract module. |
| `RRC6` | Focused tests, target-document regressions, strict type check, compile and exact boundary/element-index checks pass. |
| `RTM1` | Reverse-mutate the `RECOVERY_REQUIRED` result-shape guard to accept a missing recovery ref; `RRC2` turns red, then exact restoration returns green. |
| `RTM2` | Reverse-mutate the invariant-failure/status pairing guard to accept `STORAGE_UNAVAILABLE`; `RRC3` turns red, then exact restoration returns green. |

The authentic test seam imports only ordinary public constructors from
`library.workflow_router.target_document_contracts`; it does not use model construct, casts, raw
mapping bypasses, private attributes or mocked success.

## Required reviewer-owned adversarial evidence

After `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, and only after binding the exact
candidate SHA and Closure revision, the Terra/xhigh reviewer dispatches two isolated read-only,
no-code evidence lanes. Both return finite sanitized evidence only; neither may modify, commit,
push, dispatch, approve, integrate or exercise a real target, provider, release or deployment.

1. **Required `AdversarialReviewPlan` helper — Terra/xhigh.** Attack `BOUNDARY_DATA`,
   `STATE_TRANSITION`, `ERROR_PARTIAL_FAILURE` and `REGRESSION`: invalid tagged result states,
   null/extra fields, recovery-ref leakage and legacy-contract preservation.
2. **Additional HIGH_ASSURANCE read-only research helper — Terra/xhigh.** Attack `SPEC_GAP`,
   `SECURITY_BOUNDARY`, `OBSERVABILITY` and source boundary: confirm the contract does not create a
   recovery-store/lock/resolver effect and does not serialize sensitive values.

The reviewer independently reproduces every finding, runs the complete closure set and makes one
additional counter-mutation through a door unused by implementation or helpers. Missing either
evidence lane is `BLOCKED`; helpers have no approval/integration authority.

## Verification and return

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_managed_artifact_recovery_contracts.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_target_document_management.py tests/test_managed_artifact_planning.py tests/test_workflow_artifact_tree.py
py -3.11 -m mypy --strict library/workflow_router/target_document_contracts.py tests/test_managed_artifact_recovery_contracts.py
py -3.11 -m compileall -q library/workflow_router/target_document_contracts.py
git diff --check <ticket-integrated-authority> HEAD
git status --short
```

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with RRC/RTM/type/compile
evidence; `BLOCKED -> HALT` naming the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
The implementation owner does not commit or push. This is one same-lifetime synchronous lane: the
reviewer allocates the worktree, waits once for the finite return, then sends the two reviewer-owned
read-only evidence lanes. No runner, durable queue, receipt, descriptor, gateway or host workspace
readback is required or created.

Before integration, rollback is withholding the candidate. After integration, rollback is a
separately reviewed additive revert. This ticket grants no R09B writer/recovery implementation,
R09C/R09D/R09E, gate, host adapter, target authority, publication, installation, release or
deployment authority.
