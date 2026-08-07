# Autonomous Multi-AI Collaboration and Audit — Ticket Set

> Approved SPEC: [autonomous-collaboration-audit.md](../../spec/autonomous-collaboration-audit.md) (`SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T`). These documents do not authorise source/test changes.

## Delivery objective

Deliver a non-commercial, detachable workflow control plane that selects a collaboration topology, requests human confirmation only when a ticket is delivered to a named implementation owner, then runs independent planning and ticket-execution lanes through guarded integration and Grill audit.

## Ticket status and dependency order

| Ticket | User-observable capability | State | Dependency |
| --- | --- | --- |
| [01-topology-dispatch-lanes](01-topology-dispatch-lanes.md) | Capability-count question and typed dispatch wait/receipt with parallel lane isolation | `READY_TO_MERGE` | Independent review approved; guarded local integration remains owned by ticket 02 |
| [02-guarded-integration-audit](02-guarded-integration-audit.md) | Valid implementation return reaches a guarded local main integration and automatic Grill audit | `IN_PROGRESS` | Delivery confirmed; implementation authority active in its separate ticket worktree |
| [03-plugin-policy-and-response](03-plugin-policy-and-response.md) | Codex/Claude guidance and fixed `工單 ready` / `文件交接` response | `IN_PROGRESS` | Selected by an independent planning Grill; awaiting one named delivery confirmation |

## Mandatory approval data

The project owner selected this topology on `2026-08-05`:

```text
1：main control-plane session + existing separate implementation session/worktree
```

The named implementation owner is Codex implementation Agent in `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` on `codex/implementation-private-router-saas-01`; the control-plane/reviewer is Codex/current `main` worktree. A positive delivery confirmation is the ticket-scoped approval and implementation authority; no second approval is requested. Ticket 01 was delivered on `2026-08-05`; Ticket 02 was delivered on `2026-08-07` and is active in its execution lane. The planning lane proceeds to Grill independently; ticket 03 remains `PLANNED` until selected.

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
