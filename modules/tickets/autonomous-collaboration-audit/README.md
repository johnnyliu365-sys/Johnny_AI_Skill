# Autonomous Multi-AI Collaboration and Audit — Ticket Set

> Approved SPEC: [autonomous-collaboration-audit.md](../../spec/autonomous-collaboration-audit.md) (`SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T`). These documents do not authorise source/test changes.

## Delivery objective

Deliver a non-commercial, detachable workflow control plane that selects a collaboration topology, requests human confirmation only when a ticket is delivered to a named implementation owner, then runs independent planning and ticket-execution lanes through guarded integration and Grill audit.

## Ticket status and dependency order

| Ticket | User-observable capability | State | Dependency |
| --- | --- | --- |
| [01-topology-dispatch-lanes](01-topology-dispatch-lanes.md) | Capability-count question and typed dispatch wait/receipt with parallel lane isolation | `AWAITING_TICKET_APPROVAL` | First vertical slice |
| [02-guarded-integration-audit](02-guarded-integration-audit.md) | Valid implementation return reaches a guarded local main integration and automatic Grill audit | `PLANNED` | 01 contracts |
| [03-plugin-policy-and-response](03-plugin-policy-and-response.md) | Codex/Claude guidance and fixed `工單 ready` / `文件交接` response | `PLANNED` | 01 events; may run after 01 review |

## Mandatory approval data

The project owner selected this topology on `2026-08-05`:

```text
1：main control-plane session + existing separate implementation session/worktree
```

The named implementation owner is Codex implementation Agent in `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` on `codex/implementation-private-router-saas-01`; the control-plane/reviewer is Codex/current `main` worktree. No ticket may enter `IMPLEMENT` until separately approved. Ticket 01 is the only selected ticket; tickets 02–03 remain `PLANNED`.

## Shared baseline

- SPEC: `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T`
- Change: `CHG-20260805-010`
- Context: [autonomous-collaboration-audit/main.md](../../../doc/context/autonomous-collaboration-audit/main.md)
- Documentation baseline: `2372f1e` (`docs: plan autonomous collaboration tickets`)
- Environment: local Python workflow-router POC and detachable Codex/Claude guidance. No SaaS, service deployment, model host, target-project dependency or external provider is in scope.

## Common delivery rules

- The `main` owner, not an implementation worktree, performs any guarded integration while holding the exclusive integration lock.
- The user-facing dispatch question follows a ticket approval and ticket docs commit: `工單 <ticket-id> 是否已交付給 implementation owner <owner-id>？`
- No reply or negative reply is `WAIT_FOR_HUMAN`; it grants no worktree, Context, capability or implementation permission.
- Positive dispatch starts the ticket lane and routes only the planning lane to the next Grill. It does not change any active ticket scope.
- A pre-audit local main merge is `PENDING_AUDIT`; it must not push, deploy, hand off or start dependent implementation until audit approval.
