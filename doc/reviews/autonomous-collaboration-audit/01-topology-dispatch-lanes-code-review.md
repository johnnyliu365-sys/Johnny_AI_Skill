# Code Review｜01 — Topology Selection and Ticket Dispatch Lanes

| Field | Value |
| --- | --- |
| Review result | `CHANGES_REQUESTED` |
| Reviewed implementation | `9b4d5cb` (`feat: add collaboration dispatch lanes`) |
| Implementation handoff | `7a8df21` (`docs: record collaboration dispatch handoff`) |
| Reviewed branch / owner | `codex/implementation-private-router-saas-01` / Codex implementation Agent |
| Required ticket | `modules/tickets/autonomous-collaboration-audit/01-topology-dispatch-lanes.md` |
| Governing specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` |
| Review baseline | `dc5d4b8` on control-plane `main` |
| Review date | `2026-08-05 (Asia/Taipei)` |

## Scope and evidence reviewed

- Only committed artifacts were reviewed: implementation `9b4d5cb`, docs-only handoff `7a8df21`, the approved ticket/SPEC, current Architecture/Grill Context, and existing tests.
- The implementation worktree was clean. No uncommitted implementation file was read, modified, staged, merged or used as evidence.
- `9b4d5cb` has parent/base `b6cf8f8`; it does not include the subsequently committed dispatch clarification (`c18e914`) or Architecture/Grill commits (`a95b018`, `dc5d4b8`).

## Verification run

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` in the implementation worktree | Passed: `78` tests. |
| `python -m mypy --strict library tests` in the implementation worktree | Passed: `60` source files. |
| `git diff --check b6cf8f8 9b4d5cb` | Passed. |
| Worktree state during review | Clean. |

Passing regression and type checks do not override the authorization and acceptance failures below.

## Findings

### CR-01 — Legacy ticket approval still bypasses the required dispatch confirmation

**Impact:** A caller can submit `TICKETS + APPROVAL_GRANTED` together with an `ImplementationHandoff` and receive `IMPLEMENT`, without `TICKET_DISPATCH_REQUIRED`, a positive dispatch receipt, or the one required delivery-confirmation question. This violates SPEC AC-3, the ticket's direct/indirect authorization-bypass requirement, and the Architecture/Grill decision that the old path must not remain as an alternative.

**Evidence:**

- `library/workflow_router/profile.py:247` retains the legacy `APPROVAL_GRANTED → IMPLEMENT` rule; `:266` adds dispatch confirmation alongside it instead of replacing it.
- `library/workflow_router/contracts.py:387` still makes an `ImplementationHandoff` valid only for `APPROVAL_GRANTED`; `library/workflow_router/private_router.py:166` repeats the same indirect-boundary rule.
- `tests/test_workflow_router.py:324-390` explicitly asserts that the direct legacy handoff advances to `IMPLEMENT`.
- `tests/test_private_router_metadata_gate.py:290-341` explicitly asserts that the indirect Private Router legacy handoff returns `AUTO_RUN` and `IMPLEMENT`.

**Required correction:** Remove or fail-close the legacy transition and its request validation for this profile; dispatch confirmation must be the only ticket-scoped authority path. Add direct and Private Router regression tests proving the old event with a valid handoff halts with no Context, capability, worktree or dispatch grant.

### CR-02 — Router loses the selected implementation capability and reviewer at dispatch

**Impact:** The topology resolver verifies `CapabilityRef` values, but `RouterState` retains only a topology enum. `TicketDispatchReceipt` contains an opaque owner ID and `TicketLaneState` has neither `implementation_owner`/`reviewer` nor a selected implementation `CapabilityRef`. The confirmed decision exposes only `eligible_capabilities=(grill,)`. The Router therefore cannot uniformly select and grant the named implementation capability for the ticket lane.

**Evidence:**

- `library/workflow_router/contracts.py:409-416` stores only `topology` in `RouterState`.
- `library/workflow_router/contracts.py:451-464` has no implementation-owner capability or reviewer field in `TicketLaneState`.
- `library/workflow_router/profile.py:266-272` grants only the Grill capability.
- `library/workflow_router/router.py:188` returns only the planning rule's allowed capabilities; `:210-254` creates the ticket lane with source metadata but no allowed implementation capability, owner or reviewer.

**Required correction:** Persist the validated named topology/capability plan in Router-controlled state or receipt-linked lane state; include typed implementation owner and reviewer references; create a ticket-lane-only implementation capability grant. Tests must prove unavailable, mismatched or cross-lane capabilities fail closed and a planning decision cannot obtain the ticket grant.

### CR-03 — Opened-ticket state required by the current specification is absent

**Impact:** Current SPEC AC-3 requires a `PLANNED` proposal to become `IN_PROGRESS` immediately when opened, before the one dispatch question. The implementation has `TicketDispatchState.REQUIRED/CONFIRMED`, but no `TicketProposal`, opened-ticket event, or project/ticket state that represents `IN_PROGRESS` while confirmation is pending.

**Evidence:**

- `library/workflow_router/contracts.py` adds dispatch state but no proposal/opened-ticket type.
- `tests/test_autonomous_collaboration.py` has five tests and none covers proposal selection, immediate `IN_PROGRESS`, or duplicate dispatch-question prevention.

**Required correction:** Implement the typed proposal/open transition required by the approved SPEC, including exactly-one dispatch question and no implementation grant before a positive delivery confirmation. Cover direct and Private Router paths.

### CR-04 — Required TDD evidence and boundary coverage are incomplete

**Impact:** The handoff records one import-time `ImportError` as red evidence for all new work. It does not retain one red result per TDD behaviour. The new test module has five tests and does not cover the ticket-mandated seven worktree-locator forms, five null/empty forms, direct and indirect approval bypass, adapter exception behaviour, or a mutation/reverse proof.

**Evidence:**

- `doc/WorkProgressReport.md` in `7a8df21`, `PRG-20260805-002`, records only one import error.
- `tests/test_autonomous_collaboration.py:68-244` has five test methods; its source contains no coverage for traversal, encoded, suffix, trailing-slash, case, null/whitespace/container, adapter-exception, mutation, legacy approval, ticket proposal or `IN_PROGRESS` cases.

**Required correction:** Before production changes, record red evidence for each missing behaviour. Add the exact TDD cases named in ticket 01 and CodeReview.md §2.1. A mutation/reverse check must demonstrate each dispatch guard test fails when its protected guard is removed or reversed.

## Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `CHANGES_REQUESTED` | New Pydantic models are explicit, but required owner/reviewer/capability state is lost after topology selection. |
| Coding and architecture rules | `CHANGES_REQUESTED` | Single global decision still carries both lane effects; the ticket lane lacks its Router-authorized capability boundary. |
| Logic and authorization | `CHANGES_REQUESTED` | CR-01 retains a direct and indirect authorization bypass. |
| Boundary / exception handling | `CHANGES_REQUESTED` | Required invalid locator, empty input, adapter exception and cross-lane cases lack executable evidence. |
| Security / privacy | `CHANGES_REQUESTED` | Metadata-only intent is sound, but bypassed dispatch authority permits unauthorized implementation progress. |
| Tests / smoke | `CHANGES_REQUESTED` | Regression/type checks pass; ticket-specific TDD evidence and required edge cases are incomplete. |
| Dependencies | `APPROVED` | No dependency change was introduced. |
| SPEC / ticket / Context compliance | `CHANGES_REQUESTED` | CR-01 through CR-04 conflict with current SPEC, ticket, and Grill convergence. |
| CodeReview §2.1 path-prefix CR | `CHANGES_REQUESTED` | Required seven forms are absent. |
| CodeReview §2.1 authority-bypass CR | `CHANGES_REQUESTED` | Existing tests demonstrate the forbidden bypass succeeds. |
| CodeReview §2.1 test-coverage CR | `CHANGES_REQUESTED` | Red evidence is not behaviour-specific and reverse proof is absent. |

## Return and continuation

`9b4d5cb` must not be merged into `main`. Ticket 01 remains `IN_PROGRESS` and returns to its named implementation owner for the corrections above. The owner must synchronize the current control-plane documentation baseline in its own worktree, record new red evidence, implement only the approved ticket scope, rerun verification, and submit a new implementation commit plus docs-only handoff.

This is a normal `CHANGES_REQUESTED → IMPLEMENT` return, not `REQUIREMENT_CHANGED`: no product requirement or ticket scope was changed. Ticket 02 remains a dependent `PLANNED` candidate and cannot be opened. No push, deployment, handoff or next-ticket implementation is authorized.

---

## Correction review — `2e4f13e` / `f295c22`

| Field | Value |
| --- | --- |
| Review result | `CHANGES_REQUESTED` |
| Reviewed implementation | `2672d62` → `2e4f13e` (`fix: close dispatch approval bypass`) |
| Docs-only handoff | `082a120` → `f295c22` (`docs: return dispatch correction handoff`) |
| Required baseline | `8108cd9` on control-plane `main` |
| Branch / owner | `codex/implementation-private-router-saas-01` / Codex implementation Agent |
| Review date | `2026-08-06 (Asia/Taipei)` |

### Verified corrections

- The submitted branch has merge-base `8108cd9`; it contains neither a merge commit nor reset-based history rewrite.
- The direct and Private Router legacy `TICKETS + APPROVAL_GRANTED + ImplementationHandoff` route now returns `SUSPEND + HALT` with no source, Context, capability, lane or worktree grant.
- `TicketProposal.open()` makes the selected proposal `IN_PROGRESS` once and requires one dispatch-question ID.
- `RouterState` retains a typed `CollaborationTopologyPlan`; the confirmed ticket lane contains the selected implementation capability and reviewer.
- The committed worktree is clean. `python -B -m unittest discover -s tests` passed (`84` tests), `python -m mypy --strict library tests` passed (`60` source files), and `git diff --check 8108cd9 2e4f13e` passed.

### Remaining findings

#### CR-05 — A positive receipt can still bypass the opened proposal and the one delivery question

**Impact:** `IMPLEMENTATION_DISPATCH_CONFIRMED` currently grants the planning Grill route and the ticket-lane `IMPLEMENT` capability from a receipt alone. `RouterState` has no pending/opened proposal or dispatch-question record, and the confirmation event does not carry or verify one. A caller can therefore skip `TICKET_DISPATCH_REQUIRED`, its `IN_PROGRESS` transition, and the required named human delivery question while still receiving an execution plan. This violates SPEC AC-3 through AC-5 and the ticket's single ticket-scoped authority rule.

**Evidence:** `tests/test_autonomous_collaboration.py` deliberately calls `RouterEngine.decide()` with a fresh `_ticket_state()` and only `IMPLEMENTATION_DISPATCH_CONFIRMED` plus a positive receipt; it asserts `AUTO_CONTINUE`, a planning `GRILL` lane and a ticket `IMPLEMENT` lane. Neither `RouterState` nor `TicketDispatchReceipt` contains a prior dispatch-question/proposal correlation. `router.py` validates ticket, owner, topology and current event correlation, but has no persisted pending-dispatch validation.

**Required correction:** Persist a metadata-only pending-dispatch descriptor in Router-controlled state/checkpoint after the opened proposal produces its one question. Confirmed dispatch must match that descriptor's ticket, named owner, question/correlation and reviewed-handoff reference; a receipt without it, a duplicate confirmation, or any mismatch must `HALT` with no grant. Add direct and Private Router regression tests for every bypass form.

#### CR-06 — The Profile still exposes the obsolete ticket-completion approval wait

**Impact:** The user-approved flow opens a selected committed ticket immediately and asks only the delivery-confirmation question. `build_router_poc_profile()` still declares `TICKETS + ACTION_COMPLETED` as `WAIT_FOR_HUMAN` with `TICKET_APPROVAL_REQUIRED`. An Agent that correctly reports ticket-document completion to the Router is therefore sent to the ceremonial approval gate the specification explicitly removes.

**Evidence:** `profile.py` retains the `ProcessStage.TICKETS` / `RouterEventKind.ACTION_COMPLETED` rule with `requires_human_approval=True` and `HumanWaitReason.TICKET_APPROVAL_REQUIRED`. No correction test submits that event and proves it cannot become a second human wait.

**Required correction:** Remove or fail-close this obsolete transition and make the control-plane ticket-opening path emit the validated `TICKET_DISPATCH_REQUIRED` event directly. Add a regression test proving ticket completion cannot produce `TICKET_APPROVAL_REQUIRED` or any implementation grant.

#### CR-07 — The reviewed implementation handoff is not usable or bound on the only legal dispatch path

**Impact:** `ImplementationHandoff` is still accepted only with `APPROVAL_GRANTED`, which is now deliberately blocked. The confirmed-dispatch path accepts only an opaque `handoff_reference` in a receipt and never validates it against a reviewed `ImplementationHandoff`, the opened proposal, or Router-controlled pending state. Consequently the required SPEC/ticket/Context/TDD/role handoff has no valid, verified place in the legal dispatch sequence.

**Evidence:** `contracts.py` and `private_router.py` reject any `ImplementationHandoff` unless its event is legacy `APPROVAL_GRANTED`; `RouterEventKind.IMPLEMENTATION_DISPATCH_CONFIRMED` accepts a receipt without that object. The dispatch tests construct the confirmation directly with an arbitrary receipt handoff ID, so no binding is exercised.

**Required correction:** Move the metadata-only handoff validation to the legal dispatch lifecycle, give it a stable opaque reference, and bind the later receipt to the pending reviewed handoff before granting either lane. Cover direct and Private Router mismatch, omitted-handoff and legacy-event cases.

#### CR-08 — The sole governing workflow text still documents the removed legacy transition

**Impact:** `Workflow.md` is the declared sole workflow standard. Its role-boundary section still says the Profile may accept `TICKETS + APPROVAL_GRANTED → IMPLEMENT` with an `ImplementationHandoff`, directly contradicting the corrected Router guard and the approved SPEC. Following the document would reintroduce the bypass.

**Evidence:** `Workflow.md:361`; ticket 01 explicitly includes the policy text necessary for the dispatch behaviours.

**Disposition:** The control plane has corrected this policy in the same review record: it now defines open proposal → one dispatch question → pending metadata descriptor → positive bound receipt → two lanes, explicitly rejects the legacy transition, and states that `TICKETS + ACTION_COMPLETED` is not a second approval wait. The implementation owner must synchronize that committed control-plane baseline before the next review.

### Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `CHANGES_REQUESTED` | New values are strongly typed, but pending authorization state and handoff binding are absent. |
| Coding and architecture rules | `CHANGES_REQUESTED` | Receipt confirmation is evaluated independently of the preceding Router decision. |
| Logic and authorization | `CHANGES_REQUESTED` | CR-05 permits an execution grant without the mandated delivery question. |
| Boundary / exception handling | `CHANGES_REQUESTED` | Missing, duplicate and mismatched pending-dispatch/handoff states are untested. |
| Security / privacy | `CHANGES_REQUESTED` | Metadata-only design remains sound; unbound receipt authority is not. |
| Tests / smoke | `CHANGES_REQUESTED` | Regression/type checks pass, but required bypass and legacy-completion tests are absent. |
| Dependencies | `APPROVED` | No dependency change was introduced. |
| SPEC / ticket / Context compliance | `CHANGES_REQUESTED` | CR-05 through CR-08 conflict with AC-3 through AC-5 and the governing workflow. |

### Return and continuation

`2e4f13e` must not be merged into `main`. Ticket 01 remains `IN_PROGRESS` and returns to its named implementation owner for CR-05 through CR-07; CR-08 policy alignment is complete in the control-plane review commit. This remains `CHANGES_REQUESTED → IMPLEMENT`, not `REQUIREMENT_CHANGED`: the approved requirement is unchanged. Ticket 02 remains `PLANNED`; no integration, push, handoff, deployment or dependent implementation is authorized.
