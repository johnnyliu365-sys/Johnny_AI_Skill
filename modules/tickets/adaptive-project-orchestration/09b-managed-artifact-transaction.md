# R09B — managed-artifact transactional persistence and post-state proof

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-R09B-MANAGED-ARTIFACT-TRANSACTION` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 10 / AC-17R9, AC-17R10 and the Revision 09 serial closure item 2 |
| Requirement / Context / ADR | `PRD-20260828-043` / `CHG-20260828-043` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09` (`bf077fdbce324527b7f95ea8382967a12ef42ad9ef6fb74c98ce020186cf8bfc`) / `ADR-20260828-031` |
| State / closure | `OPEN / APPROVED / DISPATCH_READY`; `CLOSURE-ADAPTIVE-R09B-MANAGED-ARTIFACT-TRANSACTION-01`, ticket revision `r09b-01` |
| Approval authority | Project owner, 2026-08-28 (Asia/Taipei): approved this exact R09B serial successor and required implementation completion to be followed by independent adversarial evidence lanes before final review. |
| Source baseline / dependency | `17284f8c1c13d7ac793924a6bf396a39ea25403e`; candidate must descend from this approval-bearing `main`. R09A planner candidate is integrated at `91da8135e301992635d716c6cefa068ad950d807`. Read-only dependencies are `library/workflow_router/managed_artifact_planning.py`, `library/workflow_router/artifact_tree.py`, `library/workflow_router/target_document_contracts.py`, and the current `TransactionalTargetDocumentWriter`. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh; sole Agent-to-Agent orchestrator, final reviewer and sole integrator. |
| Implementation owner | `implementation-high-assurance` semantic profile — Luna/xhigh; one same-lifetime owner lane, no helper, no commit and no push. |
| Agent Context / worktree / branch | Allocate `SIDE-CONTEXT-ADAPTIVE-R09B-20260828-01` only after the ticket is integrated. Required implementation worktree `.worktrees/adaptive-r09b-managed-artifact-transaction`; branch `implement/adaptive-r09b-managed-artifact-transaction`; exact baseline `17284f8c1c13d7ac793924a6bf396a39ea25403e`. Same-lifetime allocation requires repository-contained worktree and Git metadata proof, but no runner, queue, receipt, descriptor, gateway or host-workspace readback. |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11, strict Pydantic contracts, complete annotations, `mypy --strict`, disposable Git repositories and deterministic forced-failure verification. `HIGH_ASSURANCE` is derived from a new cross-document destructive transaction boundary: recovery must restore every prior byte after an interleaved write/post-check failure. |
| XSS / effects | `XSS_NOT_APPLICABLE`. The closure adds a local target-document filesystem adapter exercised only against disposable repositories. It has no Git integration, runner, queue, receipt, host adapter, provider, network, environment, Secret, publication, installation, release or deployment effect. Target authority remains later R09C. |

## Boundary declaration

```johnny-boundary
modify = library/workflow_router/target_document_contracts.py
modify = library/local_orchestration/target_document_management.py
create = tests/test_managed_artifact_transaction.py
modify = tests/test_managed_artifact_transaction.py
create = modules/element/python/adaptive-project-orchestration/09b-managed-artifact-transaction/
modify = modules/element/python/adaptive-project-orchestration/09b-managed-artifact-transaction/
forbid = library/workflow_router/managed_artifact_planning.py
forbid = library/workflow_router/artifact_tree.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/__init__.py
forbid = library/local_orchestration/__init__.py
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

Add one private successor adapter in
`library/local_orchestration/target_document_management.py`:

```python
TransactionalManagedArtifactWriter(workspace: TargetWorkspace)
apply(plan: ManagedArtifactPlan) -> ManagedArtifactWriteResult
```

It accepts only an already-`PLANNED` R09A `ManagedArtifactPlan` and observes the exact Git `HEAD`
before any target filesystem operation. It applies the plan's finite create/update/delete document
mutations as one all-or-nothing transaction. Before `APPLIED`, it proves every written document's
candidate bytes/digest and validates each `PRESENT` candidate post-state snapshot through the
existing `ArtifactTreeResolver`; an `ABSENT` snapshot proves only its explicit final-parent edge
is absent and is never reported as resolved. Any failed precondition, filesystem operation or
post-state proof restores every changed target path to its exact prior bytes/absence and returns
one finite, sanitized result.

The new `ManagedArtifactWriteResult` is an additive strict tagged output in
`target_document_contracts.py`. It exposes only finite status/failure plus opaque artifact
identities and digests. Its finite failures are `BASELINE_MISMATCH`, `PATH_STATE_MISMATCH`,
`PATH_ESCAPE`, `STORAGE_UNAVAILABLE` and `POST_STATE_INVALID`; it must not expose a raw path,
filesystem exception, document body, command, transcript or absolute workspace location.

`TransactionalTargetDocumentWriter`, `TargetDocumentPlan`, `TargetDocumentMutation`,
`DocumentWriteResult`, their serialization and their existing tests are compatibility fixtures:
R09B does not change their behavior. The successor neither plans a request, discovers a path,
creates a public package export, stages/commits, calls the repository gate nor grants target
mutation authority. R09C alone owns candidate-tree admission and integration.

`TicketDecompositionDecision = READY_LOW_MODEL` is **not** applicable: although the closure has
one adapter boundary, destructive multi-document recovery and a forced post-write failure are
the same indivisible transaction. The fixed architecture and finite outcome permit one
Luna/xhigh implementation owner under the derived `HIGH_ASSURANCE` profile; file count is not
the reason.

## Frozen transaction rules

1. Validate exact plan type and `HEAD == plan.baseline_commit` before path inspection, directory
   creation, temporary-file creation, write, unlink or resolver invocation. A stale baseline
   returns `BASELINE_MISMATCH` with zero target mutations.
2. Build one finite, normalized target-relative set from the plan's document mutations. Every
   create must be absent; every update/delete must be an existing regular non-symlink file whose
   canonical LF UTF-8 digest equals the expected current digest. Reject duplicate/escaped/symlink
   state before the first mutation.
3. Materialize only create/update temporary bytes, then apply every planned create/update/delete.
   Preserve prior bytes or absence for every target before the first replacement/unlink. A write,
   delete, decode or post-proof failure restores all already-applied entries in reverse order and
   removes temporary residue. No partial success exists.
4. On the candidate bytes, verify every create/update digest and every delete absence. Re-resolve
   every `PRESENT` post-state snapshot through the existing resolver. For `ABSENT`, verify the
   complete candidate prefix and absence only of the declared terminal edge; a missing earlier
   segment, terminal node/edge, duplicate/cycle/stale edge or mixed lifecycle is
   `POST_STATE_INVALID`.
5. Only then return `APPLIED` with canonical artifact-ref order and the matching finite digests.
   Re-applying the unchanged plan is not idempotent success: baseline/path state mismatch must
   return a finite failure without overwriting candidate bytes.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `MAT1` | Strict construction and JSON round-trip of every new R09B result/failure shape rejects missing/null/extra fields, mixed success/failure fields, raw paths and non-opaque identities. Existing writer contracts and serialized shapes remain unchanged. |
| `MAT2` | A planned `CREATE` and `REVISE` transaction over a disposable Git repository returns `APPLIED`; every affected file has exact candidate bytes/digest and every `PRESENT` post-state path resolves through `ArtifactTreeResolver`. |
| `MAT3` | A planned `REPLACE` and `ARCHIVE` transaction atomically deletes the old active leaf, creates the replacement/archive leaf, preserves unrelated sibling bytes and verifies present versus absent candidate paths with the distinct rules above. |
| `MAT4` | Stale Git baseline, existing create target, missing/update/delete target, wrong current digest, symlink/escape or duplicate path returns the exact finite failure before the first target mutation. |
| `MAT5` | A forced failure during a later create/update/delete, and a forced resolver/post-state failure after all writes, each restore every touched target to exact baseline bytes/absence and leave no `.target-document-*` or rollback residue. |
| `MAT6` | A candidate with a malformed present edge, malformed absent terminal/prefix, stale edge metadata, duplicate/cycle or changed document digest cannot return `APPLIED`; it restores prior bytes and returns `POST_STATE_INVALID`. |
| `MAT7` | A second application of the same plan fails closed without replacing/rewriting the first candidate bytes. Existing `TargetDocumentPlan` writer tests remain green unchanged. |
| `MAT8` | AST/source gates prove no change to legacy writer behavior; no planner/request construction, filesystem discovery, raw mapping/cast/`Any`/`object`, broad catch, Git mutation, staging/commit, package export, runner/queue/receipt/host/provider/network/environment access or exception/body/path serialization. |
| `MAT9` | Focused R09B tests, existing target-document and artifact-tree regressions, strict typing, compile and scope checks pass. The new element index binds the exact ticket/SPEC/Context/source/test references and says persistence is not repository authority. |
| `MTM1` | Reverse-mutate the pre-write `HEAD` comparison; `MAT4` turns red, then exact restoration returns green. |
| `MTM2` | Reverse-mutate the rollback path to omit one later target; `MAT5` turns red, then exact restoration returns green. |
| `MTM3` | Reverse-mutate the post-write resolver/absent-terminal check; `MAT6` turns red, then exact restoration returns green. |
| `MTM4` | Reverse-mutate the retry guard to accept an already-applied plan; `MAT7` turns red, then exact restoration returns green. |

The authentic test seam imports the new private managed writer and R09A plan types directly;
it uses disposable repositories and the real filesystem adapter, not mocked writer success.
Forced failures may patch only the exact post-preparation filesystem/resolver call they intend to
test. They must run with unfiltered output and restore the target in the test itself.

## Required reviewer-owned adversarial evidence

After `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, and only after binding the exact
candidate SHA and Closure revision, the Terra/xhigh reviewer dispatches these isolated,
read-only/no-code evidence lanes in parallel. Both return finite sanitized evidence only; neither
may modify, commit, push, dispatch, approve, integrate or exercise a real target, provider,
release or deployment.

1. **Required `AdversarialReviewPlan` helper — Terra/xhigh.**
   `profile_requirement=REQUIRED`, `isolation_disposition=PROVED_READ_ONLY_SNAPSHOT`,
   `effect_scope=NO_EXTERNAL_EFFECT`; attack `ERROR_PARTIAL_FAILURE`, `CONSISTENCY`,
   `CONCURRENCY` and `IDEMPOTENCY`. It must try a late write failure, post-write resolver failure,
   retry and competing baseline/path state, and return candidate-bound `FINDINGS`, `NO_FINDINGS`,
   `BLOCKED`, `UNAVAILABLE` or `NOT_APPLICABLE` evidence.
2. **Additional HIGH_ASSURANCE read-only research helper — Terra/xhigh.**
   This is the profile's separately permitted optional research lane, not a co-reviewer or a
   second authority plan. It attacks `SPEC_GAP`, `BOUNDARY_DATA`, `STATE_TRANSITION`, `REGRESSION`
   and `OBSERVABILITY`: tagged plan/result shape, null/empty/Unicode/path-prefix/symlink input,
   present/absent transitions, legacy-writer preservation and sanitized failure output.

The reviewer independently reproduces every claimed finding, runs the complete closure set and
performs one additional counter-mutation through a door not used by the implementation owner or
helpers. Missing required adversarial evidence is `BLOCKED`; the helpers are evidence only and
the Terra/xhigh reviewer alone concludes `APPROVED`/`CHANGES_REQUESTED`/`BLOCKED` and alone
integrates.

## Verification and return

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_managed_artifact_transaction.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_target_document_management.py tests/test_workflow_artifact_tree.py tests/test_managed_artifact_planning.py
py -3.11 -m mypy --strict library/workflow_router/target_document_contracts.py library/local_orchestration/target_document_management.py tests/test_managed_artifact_transaction.py
py -3.11 -m compileall -q library/workflow_router/target_document_contracts.py library/local_orchestration/target_document_management.py
git diff --check 17284f8c1c13d7ac793924a6bf396a39ea25403e HEAD
git status --short
```

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with MAT/MTM/type/compile
evidence; `BLOCKED -> HALT` naming the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
The implementation owner does not commit or push. This is one same-lifetime synchronous lane:
the reviewer allocates the worktree, waits once for the finite return, then sends the two
reviewer-owned read-only evidence lanes. No runner, durable queue, receipt, descriptor, gateway
or host workspace readback is required or created.

Before integration, rollback is withholding the candidate. After integration, rollback is a
separately reviewed additive revert. This ticket grants no R09C/R09D/R09E, gate, host adapter,
target authority, publication, installation, release or deployment authority.
