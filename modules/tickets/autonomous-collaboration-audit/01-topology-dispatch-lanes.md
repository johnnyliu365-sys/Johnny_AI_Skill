# 01 — Topology Selection and Ticket Dispatch Lanes

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-1 through AC-5 |
| Context / change | `doc/context/autonomous-collaboration-audit/main.md` / `CHG-20260805-010` |
| State | `AWAITING_TICKET_APPROVAL` — topology and named owners recorded; separate ticket approval required |
| Language | Python 3.11 and Markdown |
| Baseline | `2372f1e` |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` / `codex/implementation-private-router-saas-01` |
| Environment | Local Router POC; no Git mutation, network, target-project or host-thread creation |

## User-observable outcome

The plugin asks whether one or two coding Agents are available. After an approved ticket's docs commit, it asks whether that exact ticket has been delivered to its named implementation owner. An unanswered/negative dispatch is a precise wait without grants; confirmed dispatch creates separate planning and ticket-execution descriptors so the planning lane can enter its next Grill without mutating the ticket lane.

## Scope and boundary

In scope: strong typed topology, ticket-lane, dispatch-receipt and event contracts; Profile/Router direct and private-boundary decisions; lane correlation/Context isolation; tests and policy text needed for these behaviours.

Out of scope: actual host conversation/model creation, real filesystem worktree creation, main merge, audit, SaaS, entitlement, provider, UI, deployment, target-project change or raw-context persistence.

Frontend composition / DI: `N/A` — no formal UI boundary. Reason: typed local Router/skill policy only.

## Handoff and role assignment

- Control-plane owner: Codex/current `main` worktree.
- Implementation owner: Codex implementation Agent / existing `workflow-implementation` worktree. It must synchronize from the approved main base after this ticket approval and before its first red test.
- Reviewer: Codex/current `main` worktree; it does not share the implementation worktree.
- Owner override: `N/A`.
- `ImplementationHandoff`: approved SPEC/ticket/Context/TDD metadata references, expected baseline and named role IDs only.
- `ImplementationReturn`: `COMPLETED → ACTION_COMPLETED`; `BLOCKED → HALT`; `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`.

## TDD and defect checks

1. Red: omitted/unknown topology or unavailable named capability rejects without an execution grant; valid one/two topology produces a finite plan.
2. Red: direct and Private Router path without/with negative dispatch confirmation returns `WAIT_FOR_HUMAN` with no source, Context, capability or worktree plan; a valid typed receipt produces one ticket plan and one planning-Grill route.
3. Red: concurrent planning event cannot change the dispatched ticket's state, source grant, event ID or side-context ID.
4. CodeReview §2.1: path prefix applies to any supplied worktree reference — exact, suffix, trailing slash, case, encoded, traversal and empty forms; null/undefined/empty/whitespace/empty container topology/receipt; direct and indirect authorization bypass; token N/A source scan; stable error code; adapter exception; mutation proof of dispatch guard.

## Completion evidence

- Required: red-test names/reasons, affected regression suite, `mypy --strict`, no-bytecode compile, privacy/source-field sentinel, smoke path, and `git diff --check`.
- Ticket docs commit is evidence only; after its approval the dispatch question is the next human gate.
