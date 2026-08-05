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
