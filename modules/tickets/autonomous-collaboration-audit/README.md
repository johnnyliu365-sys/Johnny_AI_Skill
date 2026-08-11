# Autonomous Multi-AI Collaboration and Audit — Ticket Set

> Approved SPEC: [autonomous-collaboration-audit.md](../../spec/autonomous-collaboration-audit.md) (`SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T`). These documents do not authorise source/test changes.

## Delivery objective

Deliver a non-commercial, detachable workflow control plane that selects a collaboration topology, requests human confirmation only when a ticket is delivered to a named implementation owner, then runs independent planning and ticket-execution lanes through guarded integration and Grill audit.

## Ticket status and dependency order

| Ticket | User-observable capability | State | Dependency |
| --- | --- | --- |
| [01-topology-dispatch-lanes](01-topology-dispatch-lanes.md) | Capability-count question and typed dispatch wait/receipt with parallel lane isolation | `INTEGRATED` | Approved `67b049a` is patch-equivalent to rebased `0dc4da5`, which is in `main` through Ticket 02's reviewed integration baseline |
| [02-guarded-integration-audit](02-guarded-integration-audit.md) | Valid implementation return reaches a guarded local main integration and automatic Grill audit | `INTEGRATED` | Fourth correction review approved `906679a`; source fast-forwarded to `main` at `90e9191` |
| [03-plugin-policy-and-response](03-plugin-policy-and-response.md) | Codex/Claude guidance and fixed `工單 ready` / `文件交接` response | `INTEGRATED` | Rebased reviewed implementation `0a5b757` / `43033bf` fast-forwarded from `b34e59e`; the post-integration Grill audit found no new scope or correction route |
| [04-reviewer-only-orchestration-authority](04-reviewer-only-orchestration-authority.md) | Exact reviewer-only Agent effect authorization and implementation-owner denial | `PLANNED / DEPENDENCY_WAIT` | `CHG-20260811-012`; wait for local 06A host capability proof and release of the sole implementation lane |

## Mandatory approval data

The project owner selected this topology on `2026-08-05`:

```text
1：main control-plane session + existing separate implementation session/worktree
```

The named implementation owner is Codex implementation Agent; the control-plane/reviewer is Codex/current `main` worktree. A positive delivery confirmation is the ticket-scoped approval and implementation authority; no second approval is requested. Tickets 01 through 03 are integrated. `CHG-20260811-012` adds planned Ticket 04 without rewriting them. Only the named reviewer may control an implementation Agent; the implementation owner may not orchestrate any Agent. Ticket 03's receipt and blocked branch remain historical audit evidence only.

## Shared baseline

- SPEC: `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T`
- Change: `CHG-20260805-010`
- Context: [autonomous-collaboration-audit/main.md](../../../doc/context/autonomous-collaboration-audit/main.md)
- Documentation baseline: `2372f1e` (`docs: plan autonomous collaboration tickets`)
- Environment: local Python workflow-router POC and detachable Codex/Claude guidance. No SaaS, service deployment, model host, target-project dependency or external provider is in scope.

## Common delivery rules

- A `PLANNED` candidate becomes an opened ticket only when the control plane selects it. Opening immediately changes it to `IN_PROGRESS` and emits exactly one named dispatch question; it never waits for a second ticket-approval message.
- The `main` owner, not an implementation worktree, performs any guarded integration while holding the exclusive integration lock.
- The user-facing dispatch question follows a ticket approval and ticket docs commit: `工單 <ticket-id> 是否已交付給 implementation owner <owner-id>？`
- No reply or negative reply is `WAIT_FOR_HUMAN`; it grants no worktree, Context, capability or implementation permission.
- Positive dispatch starts the ticket lane and routes only the planning lane to the next Grill. It does not change any active ticket scope.
- A pre-audit local main merge is `PENDING_AUDIT`; it must not push, deploy, hand off or start dependent implementation until audit approval.
- A pending dependency waits for its typed implementation/audit event through the monitor; it is not `WAIT_FOR_HUMAN` and must automatically resume the next Grill when evidence arrives.
