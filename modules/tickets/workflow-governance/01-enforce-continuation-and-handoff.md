# 01 — Enforce Continuation and Implementation Handoff (POC)

## Ticket information

| Field | Value |
| --- | --- |
| ID | `01-enforce-continuation-and-handoff` |
| State | `IN_PROGRESS` — owner-approved on `2026-08-05`; implementation begins only after the assigned worktree fast-forwards to `main` |
| Type | POC / vertical policy slice |
| Implementation language | Python 3.11 for Router contracts/tests; Markdown for workflow, skill, and template policy artifacts |
| Control-plane owner | Codex / current worktree |
| Implementation owner | Codex implementation Agent / `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` / branch `codex/implementation-private-router-saas-01` |
| Reviewer | Codex control-plane / `C:\Users\<user>\Desktop\AI控制工作workflow` / branch `main` |
| Delivery environment | Local Python Router POC and detachable Codex/Claude guidance source |
| Baseline commit | `04146af` |
| Specification | [workflow-governance.md](../../spec/workflow-governance.md) — AC-1 through AC-8 |
| Requirement / Context | `CHG-20260805-009`; [workflow-governance/main.md](../../../doc/context/workflow-governance/main.md) |

### Worktree synchronization

The assigned implementation worktree is a clean, separate Git worktree but is currently at `7769710`, behind this approved specification and ticket plan. Before writing the first red test, its implementation owner must fast-forward it to `main` and verify that the approved specification, ticket, and this assignment are present. It may not cherry-pick only source files or begin from the old baseline.

## User-observable outcome

When a routed action completes, including an implementation or docs-only commit, the control plane records `ACTION_COMPLETED`, receives exactly one typed Router classification, and continues through the next safe stage without a ceremonial pause. It stops only at an explicit approval/decision gate or a concrete fail-closed condition. An implementation owner can return completion evidence for review or a `REQUIREMENT_CHANGED` event for re-Grill; it cannot silently alter approved architecture or frontend design.

## Scope

### In scope

1. Add strongly typed, fail-closed completion-evidence and implementation-return contract support to the existing Router POC, preserving existing public behavior where the new evidence is absent.
2. Make Profile/Router/continuation-runner handling of `ACTION_COMPLETED` observable: every completion has a declared next decision; only declared safe transitions auto-run; authority gates wait with a precise reason; all invalid or undeclared cases halt.
3. Update workflow and bundled-skill guidance so a commit is evidence, not a terminal response, and a control-plane Agent re-evaluates before replying.
4. Enforce the named separate implementation owner/reviewer handoff and return-event requirement in the ticket template; retain the explicit per-ticket owner override record.
5. Enforce formal frontend ticket composition/DI fields and the explicit non-frontend `N/A` reason in the template validation/contract path.
6. Add red-to-green tests, strict type checks, documentation/reference validation, and Code Review evidence for the changed policy.

### Out of scope

- Implementing any customer project, production UI, frontend runtime, web service, model invocation, Temporal worker, external Agent dispatcher, hosted service, payment, identity provider, database, or deployment.
- Creating a new host model turn or bypassing Codex/Claude approval controls.
- Persisting raw source, document, prompt, ContextPacket, paths, URIs, secrets, or PII in a completion/handoff contract.
- Altering any completed ticket or silently changing existing POC privacy/telemetry behavior.

## Target paths and architecture boundary

The implementation owner must confirm the actual paths before the first red test. The expected minimal change set is:

```text
library/workflow_router/contracts.py            # completion/return value objects and invariant checks
library/workflow_router/profile.py              # declared completion and authority transitions
library/workflow_router/router.py               # fail-closed decision classification
library/workflow_router/private_router.py       # bounded local continuation and return-event adapter
library/workflow_router/__init__.py             # public POC exports, only if a new contract is public
tests/test_workflow_router.py                    # deterministic Router/Profile contract tests
tests/test_private_router_metadata_gate.py       # continuation-runner and fail-closed regression tests
Workflow.md                                     # executable policy wording and router contract
AGENTS.md                                       # index-only entry/role reminder; no competing rules
skills/johnny-project-takeover/SKILL.md          # Codex/Claude active-task continuation guidance
modules/tickets/TEMPLATE.md                      # owner, return-event, frontend Composition Root/DI fields
modules/spec/TEMPLATE.md                         # frontend composition/DI and handoff references
```

No extra runtime source, target-project files, plugin cache dependency, service endpoint, hook, CI dependency, or persistence adapter may be added. Any necessary expansion returns `REQUIREMENT_CHANGED` to Grill.

### Composition and dependency-injection design

`N/A` — this ticket has no formal frontend/UI, component library, screen state, or UI external-access change. Its template change must nevertheless make the following fields mandatory for future frontend tickets: component/screen/layout boundaries; Composition Root path and scope; named injected interfaces; production bindings; test fakes; loading/empty/error/permission/accessibility acceptance. The template must require a concrete `N/A` rationale for non-frontend tickets.

The POC composition root remains the Router boundary: `RouterEngine` / `PrivateRouterClient` receive typed Profile/service/executor dependencies through constructors or ports. No module may instantiate a global singleton, read environment configuration, or perform implicit host/Agent dispatch.

## Contract and invariants

1. **Commit is evidence:** a commit reference may be attached to a typed completion event, but it never decides the next stage itself. Router/Profile validation is the sole decision point.
2. **Single safe action:** `AUTO_CONTINUE` grants at most one declared capability/action per decision. The runner re-routes after that action; it does not take a second action from stale state.
3. **Precise waiting:** `WAIT_FOR_HUMAN` may represent only a declared authority/decision gate. It names the approval/decision required and grants no Context, capability, or source read.
4. **Fail closed:** missing/invalid evidence, missing/denied authority, unknown owner/reviewer at implementation entry, unavailable capability, invalid response, exception, security/privacy failure, or undeclared transition becomes `HALT`; no fallback Profile or local inference is permitted.
5. **Separated handoff:** an implementation handoff contains approved references and role IDs only. Its return is `COMPLETED`, `BLOCKED`, or `CHANGE_DETECTED`; the last emits `REQUIREMENT_CHANGED` before any scope/contract/UI change is acted on.
6. **No raw Context transfer:** handoff/completion data records only identifiers, revisions, source spans, side-context ID, consumer fingerprint, and evidence digest. Raw ContextPacket/source text is not serialized or retained.
7. **Compatibility:** existing Router, telemetry, private-router privacy, and detachable-plugin behaviors stay green. A terminal `STOP` remains legal only where the Profile explicitly declares it, not because a commit happened.

## TDD plan and acceptance mapping

The implementation owner must preserve actual red-test output for each new behavior before minimal implementation. A test written only after implementation does not satisfy this ticket.

| Cut | Red → Green behavior | Specification acceptance |
| --- | --- | --- |
| Normal continuation | Valid completion evidence from docs or implementation re-routes, invokes exactly one declared safe action, and re-evaluates; commit text alone cannot end the active route | AC-1, AC-2 |
| Declared approval | SPEC/ticket approval and a material owner-assignment decision return a precise `WAIT_FOR_HUMAN`, with no granted Context/action | AC-3, AC-5 |
| Fail-closed classification | Missing/invalid evidence, source, authority, capability, response, or transition yields `HALT`, never a wait/fallback | AC-4, AC-8 |
| Handoff return | Separate owner handoff returns completion to review; changed requirement/contract/DI boundary emits `REQUIREMENT_CHANGED` to Grill | AC-5, AC-8 |
| Frontend template contract | A formal frontend ticket missing composition/DI data is blocked; a non-frontend ticket with explicit `N/A` rationale validates | AC-6 |
| Compatibility regression | Existing Router Profile, local continuation runner, telemetry, privacy, and detached-plugin tests remain green | AC-2, AC-7, AC-8 |

## Code Review defect checks

The reviewer must trace each applicable [CodeReview.md](../../../CodeReview.md) §2.1 category to executed tests and implementation, then conduct the required CR checks. `N/A` entries are still reviewed for scope drift.

| Category | Ticket treatment and required evidence |
| --- | --- |
| 1. Path-prefix mismatch | `N/A` at the completion/handoff boundary: no path or URI is accepted. Test that forbidden path/URI-like fields are rejected rather than normalized or prefix-compared; CR confirms no newly reachable source-read path bypasses the Router gate. |
| 2. null / empty values | Required completion IDs, role IDs, evidence references, and return statuses cover null, empty string, whitespace, and empty container equivalents at the boundary. |
| 3. authorization bypass | Direct and indirect paths to continuation/context/implementation entry require the same valid Router decision and separate-owner check. CR starts at the composition root and enumerates reachable paths. |
| 4. token format / comparison | `N/A`: this ticket introduces no credential/token secret. Opaque IDs use strict structural validation and exact equality; source scan confirms no credential comparison was introduced. |
| 5. error-code consistency | Each fail-closed reason maps to a stable external plan shape and an internal typed blocker/error reason, without leaking source or private profile detail. |
| 6. external exception behavior | Service/executor/template-validation exceptions result in a typed `HALT` or validation failure with specified propagation behavior; tests assert both observable plan and exception boundary. |
| 7. actual test coverage | Reviewer maps every AC and table row to a red-test record and final assertion, then reverses/removes the implementation path to confirm the test fails. |

## Verification and evidence

The implementation owner must use current project commands and record exact output in the ticket/element evidence:

```powershell
python -m unittest discover -s tests
python -m mypy --strict library tests
python -m py_compile library/workflow_router/*.py
git diff --check
```

Additionally run a source/privacy sentinel scan proving new contracts do not serialize raw ContextPacket/source/prompt/path/URI/secret/PII values, and a documentation-link/template contract check. Any unavailable tool or changed command must be returned to the control plane before substitution.

## Implementation evidence (2026-08-05)

- Red: `python -m unittest tests.test_workflow_router.WorkflowRouterTests.test_completion_evidence_and_implementation_handoff_are_typed_and_fail_closed tests.test_workflow_router.WorkflowRouterTests.test_requirement_change_from_implementation_routes_back_to_grill tests.test_private_router_metadata_gate.PrivateRouterMetadataGateTests.test_completion_evidence_re_routes_once_and_implementation_return_change_reenters_grill -v` failed before the implementation with `ImportError: cannot import name 'CompletionActionKind'` from `library.workflow_router`.
- Green: `python -m unittest discover -s tests` — 68 tests passed.
- Strict types: `python -m mypy --strict library tests` — no issues in 58 source files.
- Compile: `python -m py_compile library/workflow_router/*.py` — passed.
- Smoke/privacy: `python -m unittest tests.test_private_router_metadata_gate -v` — 8 tests passed, including continuation, fail-closed, and source/URI/prompt sentinel checks.
- Formatting: `git diff --check` — passed.
- Scope: implementation worktree only; no target-project runtime, network, persistence, secret, or raw Context transfer added.

## Completion definition and handoff

- [ ] Every AC and TDD cut maps to a retained red test and green verification result.
- [ ] `ACTION_COMPLETED` is processed before task completion; no safe next stage stops ceremonially.
- [ ] Only declared authority gates wait; all failure cases halt without fallback.
- [ ] Completion/handoff contracts are strongly typed and contain no raw Context data.
- [ ] Future frontend tickets are blocked without all composition/DI evidence; non-frontend tickets require explicit `N/A` rationale.
- [ ] Separate implementation owner and reviewer are recorded; the implementation commit is made in the implementation owner’s worktree.
- [ ] Code Review §2.1 evidence and smoke test are complete; existing regression suites are green.

## Approval gate

The specification was approved on `2026-08-05`. The project owner assigned the separate implementation worktree and Codex control-plane reviewer on `2026-08-05`, then explicitly approved `01-enforce-continuation-and-handoff` on `2026-08-05`.

Implementation is authorised only in the named implementation worktree after it fast-forwards to `main` and confirms this approval, the approved specification, and the ticket are present. The control-plane Agent remains prohibited from making this ticket's source/test/implementation commit.
