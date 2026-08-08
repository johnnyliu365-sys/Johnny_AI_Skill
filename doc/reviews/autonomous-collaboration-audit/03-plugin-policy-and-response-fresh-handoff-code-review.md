# Code Review — Ticket 03 Fresh Handoff: Plugin Policy and Fixed Dispatch Response

| Field | Value |
| --- | --- |
| Review result | `CHANGES_REQUESTED` |
| Reviewed implementation | `a2c82d7` (`feat: bind plugin response to pending dispatch`) |
| Docs-only handoff | `70700d7` (`docs: hand off ticket three plugin response`) |
| Reviewed branch / owner | `codex/implementation-plugin-policy-and-response-03-rework` / Codex implementation Agent |
| Required ticket | `modules/tickets/autonomous-collaboration-audit/03-plugin-policy-and-response.md` |
| Governing specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-1, AC-3, AC-9, AC-10 |
| Review baseline | `0d52903`; it is the declared dependency-corrected source base and does not contain `4d68938` |
| Review date | `2026-08-08 (Asia/Taipei)` |

## Scope and evidence reviewed

- Only committed artifacts were reviewed: implementation `a2c82d7`, docs-only handoff `70700d7`, the approved SPEC/ticket/Context, the prior blocked review, and the current Router contracts.
- The submitted range is exactly `0d52903..70700d7`; the implementation commit is a descendant of the required base, and the blocked `4d68938` / `9eda250` source was not reused. CR-18 is therefore closed.
- CR-16 is closed: policy reads accept only `PolicyDocumentMetadata` and return stable metadata-only halt errors for text or source failures. The new model has no raw-text field.
- The ticket previously referred to seven response path/URI boundary forms without listing them individually. Per CodeReview §2.1 this is a ticket defect, so the ticket is corrected in this review commit without changing product scope.
- No implementation source was changed, staged, merged, pushed, installed, or deployed by the control plane. The reviewer's compile command created only the ignored `library/workflow_router/__pycache__/` in the implementation worktree; the assigned owner must remove that regenerable cache before its next handoff.

## Independent verification

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` | Passed: `122` tests. |
| `python -B -m pytest -q -p no:cacheprovider` | Passed: `122` tests and `115` subtests. |
| `python -B -m mypy --strict --no-incremental library tests` | Passed: `65` source files. |
| `python -B -m compileall -q library/workflow_router` | Passed: `13` modules. |
| `git diff --check 0d52903 a2c82d7` | Passed. |
| Raw policy sentinel / source exception | Passed: text is rejected and no content field is serialized; source exception maps to stable `SOURCE_FAILURE`. |
| Direct render API / replay / legacy route | Passed: direct render and replay halt; the retired `TICKETS + APPROVAL_GRANTED → IMPLEMENT` route halts. |
| Indirect owner forgery smoke | **Failed:** a structural fake whose `owns_pending_dispatch_plan()` returns `True` renders the response through `render_trusted_dispatch_response()`. |
| Shape-valid commit forgery smoke | **Failed:** replacement `ticket_docs_commit=deadbee` and `handoff_docs_commit=cafe123` render through `PrivateRouterClient.render_dispatch_response()`. |

## Blocking findings

### CR-25 — A caller-controlled structural protocol can forge the indirect Router-owner check

**Impact:** `render_trusted_dispatch_response()` accepts a public `PendingDispatchPlanOwner` protocol and trusts the supplied object's boolean result. Any caller with a genuine waiting plan can pass a different object whose `owns_pending_dispatch_plan()` returns `True`, then obtain the fixed dispatch question without the owning `PrivateRouterClient`. This is an indirect authorization bypass of the exact Router-owned live-plan requirement in AC-3 and Ticket 03 TDD item 3.

**Independent reproduction:** with a valid waiting plan, a local fake owner returning `True` produced `indirect_outcome=rendered` from the module-level trusted-render function.

**Evidence:** `library/workflow_router/policy_response.py:61-65,211-221` defines and accepts the structural protocol; `private_router.py:863-876` is safe only when callers choose its method, which the public helper does not require.

**Required correction:** remove the caller-supplied owner authority from every public/indirect render path. Keep the identity check inside `PrivateRouterClient`, or pass only an unforgeable client-private capability after that check; a generic protocol or callback must not decide authorization. Add a regression where a fake owner/callback, copied plan, alternate client, absent plan, replayed plan, and direct helper invocation all halt without text or capability.

### CR-26 — Commit references are caller-supplied format values, not Router-owned reviewed artifacts

**Impact:** `CommittedDispatchArtifacts` validates only commit-string shape. The pending descriptor carries ticket, handoff and owner references but no trusted ticket/handoff commit references. Consequently, a valid pending plan can render arbitrary regex-valid commit values, falsely presenting unreviewed artifacts as the `工單 ready` and `文件交接` commits. This violates the explicit Ticket 03 rule that arbitrary regex-valid ticket/commit/owner strings must halt and the policy text's claimed committed-artifact binding.

**Independent reproduction:** replacing only the artifact commits with `deadbee` and `cafe123` returned `forged_commit_outcome=rendered`.

**Evidence:** `library/workflow_router/policy_response.py:127-133,185-193` accepts and prints the supplied commits; `contracts.py:311-320` has no commit identity in `PendingDispatchDescriptor`; the submitted invalid-commit test tests only a path-shaped string, not a valid forged commit.

**Required correction:** carry the reviewed ticket and handoff commit references in Router-owned validated dispatch state (or an equivalent immutable descriptor created by the Router), and render only those values. Do not accept `CommittedDispatchArtifacts` as an untrusted caller input. Add individual red/green tests for valid-shaped forged ticket, handoff, owner and both commit references; all must halt, while the exact Router-owned descriptor renders.

## Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `CHANGES_REQUESTED` | Metadata models are explicit, but structural `Protocol` truth is not a trustworthy authority type and commit identity is absent from the dispatch state. |
| Coding and architecture rules | `CHANGES_REQUESTED` | The private-client method is composed correctly, but the parallel module-level entrypoint bypasses its composition boundary. |
| Logic and authorization | `CHANGES_REQUESTED` | CR-25 and CR-26 permit indirect response rendering outside the exact Router-owned pending descriptor and reviewed commits. |
| Boundary / exception handling | `APPROVED` | Raw policy text and source exception detail remain outside returned models; formatter exceptions and output mutation halt. |
| Security / privacy | `CHANGES_REQUESTED` | No raw policy content leaks, but forged metadata can create an authoritative-looking dispatch response. |
| Tests / smoke | `CHANGES_REQUESTED` | Regression/type/compile checks pass, but required fake-owner and shape-valid-commit negative cases are absent. |
| Dependencies | `APPROVED` | The fresh implementation is based on the approved Ticket-02 integration and follows the sole active Ticket-03 allocation. |
| SPEC / ticket / Context compliance | `CHANGES_REQUESTED` | CR-16 and CR-18 are closed; AC-3 and Ticket 03 TDD item 3 remain unsatisfied. |
| CodeReview §2.1 path-prefix CR | `CHANGES_REQUESTED` | The ticket now names all seven forms, but the submitted tests cover only one path-shaped formatter mutation and one invalid artifact value. |
| CodeReview §2.1 authority-bypass CR | `CHANGES_REQUESTED` | Direct rendering halts, but the indirect structural-owner path renders. |
| CodeReview §2.1 test-coverage CR | `CHANGES_REQUESTED` | Tests assert the intended client path but do not reverse the structural-owner or valid-commit conditions that make the bypass observable. |

## Return and continuation

Ticket 03 remains `IN_PROGRESS`. Its existing receipt `c569056` and sole Ticket-03 allocation remain valid, so `CHANGES_REQUESTED → IMPLEMENT` is automatic and is **not** a new user question. The assigned owner corrects only this ticket in the existing `codex/implementation-plugin-policy-and-response-03-rework` lane, begins a fresh red/green cycle for CR-25 and CR-26 (including the newly explicit seven path/URI cases), removes the regenerable bytecode cache, then returns a new implementation commit and docs-only handoff for independent review. No merge, push, installation, deployment, host configuration, target-project mutation, Secret, provider, or other-ticket authority is granted.
