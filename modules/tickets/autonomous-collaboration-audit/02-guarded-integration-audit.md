# 02 — Guarded Main Integration and Grill Audit

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-6 through AC-8 |
| Context / change | `doc/context/autonomous-collaboration-audit/main.md` / `CHG-20260805-010` |
| State | `PLANNED` — depends on ticket 01 contracts and separate ticket approval |
| Language | Python 3.11 and Markdown |
| Baseline | Ticket 01 approved integration contract |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / existing `workflow-implementation` / `codex/implementation-private-router-saas-01`; ticket remains unselected |
| Environment | Local fake Git/integration port only; no real push, deployment, target-project or external provider |

## User-observable outcome

A valid completed implementation return with a matching clean base queues exactly one local `main` integration and immediately requests Grill audit. Stale, dirty, conflicting, duplicate or lock-contended cases halt before any merge. A failed audit creates a correction route and never marks handoff/deploy/push as complete.

## Scope and boundary

In scope: typed integration request/result/audit state; exclusive integration port with fake tests; profile transitions; `PENDING_AUDIT` guard; correction routing and evidence. Out of scope: executing real Git commands, remote push, deployment, customer project write, host model dispatch, SaaS, billing, entitlement and UI.

Frontend composition / DI: `N/A` — no formal UI; the fake Git/integration port is injected through a named interface/constructor in the Router composition boundary.

## Handoff and role assignment

- Control-plane/main integration owner: Codex/current `main` worktree.
- Implementation owner: Codex implementation Agent; owns only its ticket branch/worktree once this planned ticket is separately approved.
- Reviewer / Grill audit owner: Codex/current `main` worktree; does not share the implementation worktree.
- Owner override: `N/A`.
- Handoff must include ticket/branch opaque reference, expected main revision, verification evidence, dispatch receipt and audit requirements. It must never contain paths, raw Git output, source text, prompt, URI, Secret or PII.

## TDD and defect checks

1. Red: matching completed return invokes exactly one injected integration operation then creates a `PENDING_AUDIT` Grill action.
2. Red: stale revision, dirty integration state, conflict, duplicate correlation and lock contention halt with no operation.
3. Red: `APPROVED` audit permits handoff evidence; `CHANGES_REQUESTED` provisions a correction route and blocks push/deploy/dependent work.
4. CodeReview §2.1: seven forbidden path reference forms, null/empty inputs, direct/indirect merge bypass, token N/A source scan, external/internal error mapping, injected port exception propagation, and mutation proof for revision/lock guards.

## Completion evidence

- Required: retained red outputs, deterministic fake-port tests, full regression/type/compile/privacy sentinel/smoke/diff evidence, and a docs-only WorkProgress commit.
