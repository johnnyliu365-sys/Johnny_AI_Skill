# Code Review — Ticket 02 Correction: Guarded Integration and Grill Audit

| Field | Value |
| --- | --- |
| Review result | `CHANGES_REQUESTED` |
| Reviewed implementation | `b53cc55` (`fix: bind guarded integration to reviewed ticket lanes`) and its reviewed correction range from `d164fa4` |
| Docs-only handoff | `1a19183` (`docs: hand off guarded integration corrections`) |
| Reviewed branch / owner | `codex/implementation-guarded-integration-audit-02` / Codex implementation Agent |
| Required ticket | `modules/tickets/autonomous-collaboration-audit/02-guarded-integration-audit.md` |
| Governing specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-6 through AC-8, AC-11 |
| Review baseline | `d164fa4`; submitted worktree clean before and after review |
| Review date | `2026-08-08 (Asia/Taipei)` |

## Scope and evidence reviewed

- The correction range replays the Ticket-01 dispatch contracts and replaces the retired direct ticket-approval route. It adds a receipt/lane-bound coordinator, Router event vocabulary, private-router pending-dispatch storage, and correction tests.
- Only committed artifacts were reviewed. The control-plane `main`, Ticket-03 worktree, and implementation sources were not modified, staged, merged, pushed, installed, or deployed.
- The review runner's generated Python bytecode caches were removed after verification; the submitted implementation worktree is clean.

## Independent verification

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` | Passed: `102` tests. |
| `python -m pytest -q` | Passed: `102` tests and `105` subtests. |
| `python -m mypy --strict --no-incremental library tests` | Passed: `63` source files. |
| In-memory compile of `library/workflow_router/*.py` | Passed: `11` modules. |
| `git diff --check d164fa4 b53cc55` | Passed. |
| Reviewer-identity substitution | Incorrectly accepted the reviewer capability's generic `agent_profile` in place of its named capability ID and invoked integration. |
| Lock-release re-entry | Incorrectly allowed a second receipt-bound ticket integration after the first port returned but before the first `PENDING_AUDIT` state was installed. |
| Audit-sink exception | Incorrectly advanced the trusted main snapshot, discarded `PENDING_AUDIT`, then allowed a second matching ticket integration. |
| Router audit transition | Incorrectly returns `WAIT_FOR_HUMAN` for `INTEGRATION_COMPLETED`, although this POC requires automatic Grill audit. |

## Findings

### CR-19 — Reviewer and owner checks accept a generic capability profile instead of the named actor identity

**Impact:** The receipt-bound coordinator is intended to require the exact ticket, handoff, owner, reviewer, worktree, branch, correlation, revision, and lane identities. Instead, `_matches_trusted_dispatch()` accepts either a capability ID or the capability's `agent_profile` for owner/reviewer fields. The Router dispatch checks use the same alternatives. `agent_profile` is a role/category, not a unique named actor; a plan with multiple agents using the same profile cannot prove which reviewer handled the return. This reintroduces the precise identity binding CR-12 required.

**Independent reproduction:** using the committed correction fixture, the trusted reviewer capability ID was `reviewer-02` and its profile was `reviewer`. Replacing only `ImplementationReturnEvent.reviewer_id` with `reviewer` returned `PENDING_AUDIT` and recorded an integration request.

**Evidence:** `library/workflow_router/guarded_integration.py:533-543` accepts `lane.reviewer.agent_profile`; `library/workflow_router/router.py:214-235,291-305` accepts profile aliases in proposal, handoff, pending receipt, and owner checks. No committed test substitutes a generic role for a different named reviewer.

**Required correction:** establish one opaque, named actor identity for each control, implementation, and reviewer role, then require exact equality everywhere the dispatch, receipt, handoff, return, and lane are compared. Keep `agent_profile` only as a descriptive capability type. Add direct and injected-source negative tests for profile-for-ID substitution for both owner and reviewer, with zero integration/audit/wake side effects.

### CR-20 — The integration lock is released before main/audit state is made atomically visible

**Impact:** `handle_return()` releases the injected integration lock immediately after `integrate()` returns. Only afterward does it update `_main_snapshot`, create `_pending_audit`, and invoke the audit sink. A concurrent return can enter this window, see the old snapshot and no active audit, acquire the now-free lock, and start a second integration. The global pending-audit check therefore does not protect the interval it is meant to protect.

**Independent reproduction:** a deterministic lock whose first `release()` synchronously delivered a valid, differently-ticketed return yielded two `PENDING_AUDIT` decisions, two integration requests, and two audit requests. This requires no source/path/secret input and demonstrates the state-order race directly.

**Evidence:** `library/workflow_router/guarded_integration.py:436` releases the lock; `_main_snapshot` and `_pending_audit` are not assigned until `:449` and `:469`. The committed global-pending test calls the second return only after the first call has completed, so it cannot exercise this interleaving.

**Required correction:** keep the exclusive critical section until the new trusted main revision and an integration-pending/audit-lock record have been committed atomically. A second return at every interleaving point must halt before port invocation. Add a deterministic re-entrant/concurrent regression; do not rely on the fake lock's usual sequential behaviour as proof.

### CR-21 — Audit-sink failure loses the post-integration audit lock and permits a later integration

**Impact:** After a successful integration the coordinator advances `_main_snapshot`, but it installs `_pending_audit` only after `audit_sink.request_audit()` succeeds. If that injected sink raises, the method returns `HALT` with no pending-audit record. A subsequent ticket whose expected revision matches the newly advanced main can integrate even though the first main change was never audited. This violates AC-7/8 and the specification's `PENDING_AUDIT` isolation requirement.

**Independent reproduction:** a fake port returned revisions `rev-111...` then `rev-222...`, while the sink raised only for the first audit request. The first return halted with `ADAPTER_FAILURE` and left `pending_audit` empty; a receipt-bound second return for `rev-111...` then reached `PENDING_AUDIT` and invoked a second integration.

**Evidence:** `library/workflow_router/guarded_integration.py:449-469` advances main, calls the fallible sink, and sets the global pending state last. The tests cover an audit sink exception only as a generic halt; they do not attempt a second integration afterward.

**Required correction:** retain an unambiguous pending-audit/integration lock before invoking the fallible audit adapter, and preserve it on adapter failure until a deterministic retry/recovery event has been validated. A failure must halt the current path without making any later integration eligible. Add the two-ticket failure/retry regression and assert that no push, handoff, deployment, dependent implementation, or second integration is allowed.

### CR-22 — A normal automated Grill audit is modelled as a new human approval wait

**Impact:** The approved POC says it waits only for the topology question, SPEC approval, ticket delivery confirmation, and irreversible external actions. Valid integration must automatically route to Grill audit; invalid or failed audit conditions halt or create a correction route rather than masquerading as a human wait. The submitted Profile maps `INTEGRATION_COMPLETED` to `SUSPEND + WAIT_FOR_HUMAN` with `INTEGRATION_AUDIT_REQUIRED`, adding an unapproved pause and preventing the promised closed loop.

**Independent reproduction:** a valid `GRILL + INTEGRATION_COMPLETED` Router decision returned `ContinuationDirective.WAIT_FOR_HUMAN`.

**Evidence:** `library/workflow_router/profile.py:269-274` marks the integration audit rule `requires_human_approval=True`; the correction test asserts only `SUSPEND`, not its continuation directive. This conflicts with SPEC AC-7/8, §API/operations, and `Workflow.md` §0.1.1.

**Required correction:** model the normal audit request as `AUTO_CONTINUE` to the declared Grill capability, with its typed audit result returning either review or correction. Do not require an authority change for an internal POC audit. Preserve `WAIT_FOR_HUMAN` only for the approved gates, and add an end-to-end assertion that valid integration reaches Grill without prompting the user.

## Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `CHANGES_REQUESTED` | Contracts are explicit, but capability profile names are incorrectly used as actor identities. |
| Coding and architecture rules | `CHANGES_REQUESTED` | Global audit state is not atomically protected by the integration lock. |
| Logic and authorization | `CHANGES_REQUESTED` | CR-19 allows reviewer identity substitution; CR-20/21 allow multiple pre-audit integrations. |
| Boundary / exception handling | `CHANGES_REQUESTED` | A fallible audit adapter can leave an integrated main revision untracked and unlocked. |
| Security / privacy | `CHANGES_REQUESTED` | Metadata-only shape is preserved, but its identity and audit provenance are not fail-closed. |
| Tests / smoke | `CHANGES_REQUESTED` | Regression/type/compile checks pass, but omit identity-alias, release-window, and post-sink-failure sequences. |
| Dependencies | `APPROVED` | The correction includes the reviewed Ticket-01 dispatch surface and tracks its source baseline. |
| SPEC / ticket / Context compliance | `CHANGES_REQUESTED` | CR-19 through CR-22 conflict with AC-7/8 and the approved automated, one-active-audit control plane. |
| CodeReview §2.1 path-prefix CR | `APPROVED` | The corrected suite covers seven locator forms and null/empty values. |
| CodeReview §2.1 authority-bypass CR | `CHANGES_REQUESTED` | Generic reviewer aliases and release-window re-entry reach the integration port. |
| CodeReview §2.1 exception CR | `CHANGES_REQUESTED` | Audit-sink exception loses the pending-audit guard. |
| CodeReview §2.1 test-coverage CR | `CHANGES_REQUESTED` | Required interleaving and post-failure mutation regressions are missing. |

## Return and continuation

`b53cc55` and `1a19183` must not be merged, pushed, deployed, or used to unblock Ticket 03. Ticket 02 remains `IN_PROGRESS` and returns automatically to its named implementation owner for CR-19 through CR-22. This is `CHANGES_REQUESTED → IMPLEMENT`, not a new user approval, requirement change, or generic wait.

Ticket 03 remains blocked. The only legal continuation is a new committed Ticket-02 correction and docs-only handoff from the existing Ticket-02 worktree, followed by another independent review.
