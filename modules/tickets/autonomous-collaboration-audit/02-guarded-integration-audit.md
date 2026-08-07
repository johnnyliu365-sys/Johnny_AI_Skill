# 02 — Guarded Main Integration, Event Wake, and Grill Audit

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-6 through AC-8, AC-11 |
| Context / change | `doc/context/autonomous-collaboration-audit/main.md` / `CHG-20260805-010` |
| State | `IN_PROGRESS` — independent second correction review of `67745a3` / `2d218d2` returned `CHANGES_REQUESTED` for CR-23; correction authority remains active in the separate ticket-02 worktree |
| Language | Python 3.11 and Markdown |
| Baseline | Reviewed ticket 01 public contracts: `67b049a`; the dispatch handoff must record the clean expected `main` revision before worktree provisioning |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / separate ticket-02 worktree provisioned under the confirmed delivery authority; it must not share the control-plane `main` worktree |
| Environment | Local fake Git/integration port only; no real push, deployment, target-project or external provider |

## User-observable outcome

A valid completed implementation return wakes only the dependent planning proposals, queues exactly one local `main` integration for the matching clean ticket lane, and immediately requests Grill audit. Stale, dirty, conflicting, duplicate or lock-contended cases halt before any planning grant or merge. A failed audit creates a correction route and never marks handoff/deploy/push as complete.

## Scope and boundary

In scope: typed implementation-return event subscription and dependent-proposal re-evaluation; integration request/result/audit state; exclusive integration port with fake tests; profile transitions; `PENDING_AUDIT` guard; correction routing, Code Review gate and evidence. The event source and integration port are injected fakes; neither creates a real worker, host conversation, worktree, Git command, push or deployment. Out of scope: remote push, deployment, customer project write, host model dispatch, SaaS, billing, entitlement and UI.

Frontend composition / DI: `N/A` — no formal UI; the fake Git/integration port is injected through a named interface/constructor in the Router composition boundary.

## Handoff and role assignment

- Control-plane/main integration owner: Codex/current `main` worktree.
- Implementation owner: Codex implementation Agent, after the project owner confirms this ticket has been delivered; that owner owns only its ticket branch/worktree.
- Reviewer / Grill audit owner: Codex/current `main` worktree; does not share the implementation worktree.
- Owner override: `N/A`.
- Handoff must include ticket/branch opaque reference, expected main revision, verification evidence, dispatch receipt and audit requirements. It must never contain paths, raw Git output, source text, prompt, URI, Secret or PII.
- The approved ticket-01 public contract is a reviewed dependency, not permission to integrate it directly into `main`; the ticket-02 fake integration port owns the guarded integration behaviour.

## TDD and defect checks

1. Red: one valid typed completed return wakes exactly its dependent planning proposals, invokes exactly one injected integration operation for its own ticket lane, then creates `PENDING_AUDIT` and one Grill-audit action. The planning and ticket ContextView/event IDs remain distinct.
2. Red: stale revision, dirty integration state, conflict, duplicate correlation, missing/invalid return event and lock contention halt with no proposal grant, integration operation or merge.
3. Red: `APPROVED` audit routes only to the existing Code Review gate; it does not hand off, push, deploy or start dependent implementation. `CHANGES_REQUESTED` provisions a correction route and blocks those effects.
4. Red: the injected event source may deliver a return but cannot create a host model turn, physical worktree or real Git operation; adapter absence or exception halts with a stable error.
5. CodeReview §2.1: seven forbidden path reference forms, null/empty inputs, direct/indirect merge bypass, token N/A source scan, external/internal error mapping, injected port exception propagation, and mutation proof for revision/lock guards.

## Completion evidence

- Required: retained red outputs, deterministic fake-port tests, full regression/type/compile/privacy sentinel/smoke/diff evidence, and a docs-only WorkProgress commit.
