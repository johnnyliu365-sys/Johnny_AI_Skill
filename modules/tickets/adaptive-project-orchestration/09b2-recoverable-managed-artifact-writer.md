# R09B2 — recoverable managed-artifact writer

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-R09B2-RECOVERABLE-MANAGED-ARTIFACT-WRITER` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 11 / AC-17R11 and TDD item 24 (writer closure) |
| Requirement / Context / ADR | `PRD-20260828-044` / `CHG-20260828-044` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-11` (`42dc4e39c326e7791923b8be6785bf0cd46a54ba1ac63a12119837dbac3436a8`) / `ADR-20260828-032` |
| State / closure | `SUPERSEDED_ON_REVISION_13_APPROVAL / LOCAL_FILESYSTEM_MUTATION_ROUTE_RETIRED / NOT_INTEGRATED`; `CLOSURE-ADAPTIVE-R09B2-RECOVERABLE-MANAGED-ARTIFACT-WRITER-01` |
| Opening authority | Project owner, 2026-08-28 (Asia/Taipei): after accepting the R09B1 evidence-ordering deviation, authorized this one R09B2 writer-ticket opening only. The accepted control-plane authority is `bd816ac6dbcb498dd5fbdeca9b6bfd1255d58063`; it does not authorize implementation dispatch, target effects, integration, publication, installation, release or deployment. |
| Authority baseline / dependencies | Ticket baseline `bd816ac6dbcb498dd5fbdeca9b6bfd1255d58063`; R09A planner `91da8135e301992635d716c6cefa068ad950d807`; R09B1 result contracts `0b48120ed145a3c9a43989e2b353d2611a6f3052`. Candidate `269a911226ba6b849bf304a46829481916b0d97f` and its append-only correction `f99d8369363e1b4f4a230749133c69f81078a428` are non-integrated defect evidence: final check-then-replace/unlink remains TOCTOU and cannot satisfy RWW6. `CAP-RWW6-01` integrated at `5763caf5dc26e382dd8092545fde053063792a37` and qualified Windows/NTFS, Linux/WSL DrvFS and current CPython/NTFS abstraction as `NO`. `PRD-20260829-046` / `ADR-20260829-034` draft a Remote Authority Commit successor; on exact Revision 13 approval this local-filesystem ticket is superseded and may not receive another correction. |
| Control owner / reviewer | `ticket-review` semantic profile — Sol/high; sole Agent-to-Agent orchestrator, final reviewer and sole integrator. |
| Implementation owner | `implementation-high-assurance` semantic profile — Terra/xhigh, one-ticket exception. This writer is an indivisible multi-document effect/recovery closure; the former R09B bounded Luna attempt did not converge. The reviewer capability remains higher than the implementer. |
| Agent Context / worktree / branch | Allocate `SIDE-CONTEXT-ADAPTIVE-R09B2-20260828-01` only after a separate dispatch decision. Required worktree `.worktrees/adaptive-r09b2-recoverable-managed-artifact-writer`; branch `implement/adaptive-r09b2-recoverable-managed-artifact-writer`; candidate descends from this ticket's integrated authority baseline. Same-lifetime dispatch is direct reviewer allocation and one finite `wait_agent` return: no runner, queue, receipt, descriptor, gateway or host-workspace readback is required or created. |
| Delivery / language | `POC / HIGH_ASSURANCE / HIGH_ASSURANCE_REQUIRED`; Python 3.11, complete annotations, strict Pydantic boundary values, `mypy --strict`, ordinary public validators and disposable real Git repositories. |
| Reusable selection | `exclusive-file-lock@6b5a7c1`, public import `library.local_orchestration.file_lock: ExclusiveFileLock, FileLockAcquireDecision`. It is advisory mutual exclusion for cooperating runtimes only; every target effect still requires CAS revalidation. |
| XSS / effects | `XSS_NOT_APPLICABLE`. This ticket owns a local filesystem/Git-metadata runtime effect only. It creates no plugin/CLI authority, host adapter, runner, queue, receipt, provider, external target, publication, installation, release or deployment effect. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/target_document_management.py
create = tests/test_recoverable_managed_artifact_writer.py
modify = tests/test_recoverable_managed_artifact_writer.py
create = modules/element/python/adaptive-project-orchestration/09b2-recoverable-managed-artifact-writer/
modify = modules/element/python/adaptive-project-orchestration/09b2-recoverable-managed-artifact-writer/
forbid = library/local_orchestration/file_lock.py
forbid = library/workflow_router/target_document_contracts.py
forbid = library/workflow_router/managed_artifact_planning.py
forbid = library/workflow_router/artifact_tree.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/__init__.py
forbid = tests/test_target_document_management.py
forbid = tests/test_managed_artifact_planning.py
forbid = tests/test_workflow_artifact_tree.py
forbid = tests/test_managed_artifact_recovery_contracts.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Add `RecoverableManagedArtifactWriter` to
`library/local_orchestration/target_document_management.py`; retain the legacy
`TransactionalTargetDocumentWriter` unchanged. The new writer is constructed only from a
validated `TargetWorkspace`, accepts an existing `ManagedArtifactPlan`, returns the frozen
`ManagedArtifactWriteResult`, and exposes explicit active-record recovery through
`ManagedArtifactRecoveryResult`.

Before its first replace or unlink, the writer independently revalidates the complete plan shape,
Git `HEAD`, canonical relative paths, containment/reparse state, every expected current digest and
the complete candidate document/ancestor bindings. It obtains its private per-worktree recovery
location through Git's own `--git-path` resolution; it must not guess a `.git` directory. It writes
and fsyncs a private active record and raw baseline snapshots before any target effect, then takes
the selected advisory lock. The record contains only canonical relative identity, baseline and
candidate digest, action order, attempt count and an opaque recovery ref. Raw snapshot bytes remain
in private Git metadata and never enter a result, log, telemetry, prompt, router state or exception.

While holding the advisory lock, immediately before each deterministic replace/unlink the runtime
requires the target to equal the recorded baseline; immediately after it requires the target to
equal its own candidate. A writer that ignores the lock is therefore preserved by CAS: rollback or
recovery restores only when the current target still equals this writer's candidate identity; a
different identity is an external conflict and is never overwritten. Resolver input is constructed
only from canonical tuples already represented by the plan: exact family, root ref, ordered
explicit path refs and nodes. No string lookup, sibling discovery, fuzzy match or first-match path
may be introduced.

Any unsuccessful post-effect outcome runs restore and temporary-cleanup attempts exactly twice.
If exact baseline restoration/absence, zero temporary residue and no external conflict cannot be
proved, retain the active evidence, return the frozen `RECOVERY_REQUIRED` result and make every
later `apply` return that state with zero target effects until explicit recovery succeeds. Explicit
recovery may clear active state and raw snapshots only after it proves settlement; it retains a
metadata-only settled record. Expected resolver non-success is a finite post-state rejection after
the same recovery protocol. Only a narrow, writer-owned runtime invariant at that boundary maps to
`RUNTIME_INVARIANT_FAILED`; broad exception normalization is forbidden.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `RWW1` | In disposable real Git repositories, all four planned create/revise/replace/archive rows write exact bytes, complete selected ancestor updates and return canonical frozen applied evidence. |
| `RWW2` | Stale `HEAD`, malformed plan, path/reparse escape, baseline mismatch and pre-effect CAS mismatch return finite rejection with no target effect. |
| `RWW3` | A durable active record and private snapshots exist before the first target effect; records/results are sanitized and snapshot bodies never leave private Git metadata. |
| `RWW4` | A named forced early effect failure performs normal rollback and temporary cleanup, proves exact baseline restoration and leaves no active recovery requirement. |
| `RWW5` | Named forced restore or cleanup failure makes exactly two attempts, retains recovery evidence, returns `RECOVERY_REQUIRED`, and causes a later `apply` to make zero target effects; explicit recovery proves settlement before clearing active state. |
| `RWW6` | Independent cooperating lock contention is finite; an interleaved uncooperative external writer is preserved rather than overwritten during rollback or recovery. |
| `RWW7` | Expected canonical resolver non-success and a narrow writer-owned resolver invariant are distinguished as finite outcomes after recovery; no string resolver, sibling scan or first-match fallback is reachable. |
| `RWW8` | AST/source and regression checks prove the legacy writer, planner, resolver, frozen result contracts, lock implementation and package exports retain their existing behavior. |
| `RWM1` | Reverse-mutate the active-recovery guard to permit a later `apply`; `RWW5` turns red, then exact restoration returns green. |
| `RWM2` | Reverse-mutate candidate-identity comparison during rollback; the uncooperative external-writer preservation test turns red, then exact restoration returns green. |
| `RWM3` | Reverse-mutate the record-before-effect ordering guard; the durable-record test turns red, then exact restoration returns green. |

Tests use ordinary public validators and actual disposable Git worktrees. Named test-only fault
injection may force only the stated filesystem error; it must not mock success, bypass validation,
construct raw Pydantic state or simulate Git metadata without a real repository.

## Required reviewer-owned adversarial evidence

After `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, the Sol/high reviewer binds the exact
candidate SHA and runs both isolated, read-only Terra/xhigh evidence lanes before any integration.
Neither helper may modify, commit, push, dispatch, approve, integrate or exercise a real target,
provider, release or deployment.

1. **Adversarial transaction helper.** Attack boundary data, stale state transition, partial
   failure, duplicate recovery, CAS races, lock contention, rollback conflict and regression.
2. **Security/architecture helper.** Attack private-data leakage, recovery-record ordering,
   reparse containment, resolver ambiguity and legacy-writer compatibility.

The reviewer independently reproduces every finding, runs the complete closure set, and performs
one additional reviewer-owned pre-integration counter-mutation through a door unused by the
implementer or either helper. Missing a required evidence lane or a red-then-restored
counter-mutation is `BLOCKED`; helpers have no approval or integration authority.

## Verification and return

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_recoverable_managed_artifact_writer.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_target_document_management.py tests/test_managed_artifact_planning.py tests/test_workflow_artifact_tree.py tests/test_managed_artifact_recovery_contracts.py tests/test_file_lock.py
py -3.11 -m mypy --strict library/local_orchestration/target_document_management.py tests/test_recoverable_managed_artifact_writer.py
py -3.11 -m compileall -q library/local_orchestration/target_document_management.py
git diff --check <ticket-integrated-authority> HEAD
git status --short
```

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with RWW/RWM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
The implementation owner does not commit or push. The reviewer alone reviews, commits the exact
candidate, dispatches the two adversarial helpers, performs the independent counter-mutation,
then sends the candidate through the document-mutation gate.

Before integration, rollback is withholding the candidate. After integration, rollback is a
separately reviewed additive revert. This ticket grants no successor, broader target authority,
plugin/CLI trust, host adapter, runner, queue, receipt, provider, publication, installation,
release or deployment authority.
