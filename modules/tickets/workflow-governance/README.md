# Continuous Workflow Governance POC — Ticket Set

> Approved specification: [workflow-governance.md](../../spec/workflow-governance.md) (`SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`). This ticket set creates no implementation authority by itself.

## Delivery objective

Deliver one control-plane policy vertical slice: completion evidence must re-enter the Router, safe stages continue in the active task, declared authority gates wait precisely, unsafe conditions halt, and implementation work returns its evidence or a requirement-change event to the control plane. The slice applies the same rules to formal frontend handoff without adding a target-project runtime dependency.

## Ticket status

| Ticket | User-observable capability | State | Required authority |
| --- | --- | --- | --- |
| [01-enforce-continuation-and-handoff](01-enforce-continuation-and-handoff.md) | Post-commit Router continuation, typed implementation return, and policy/template enforcement | `PLANNED` | Explicit ticket approval plus a separately named implementation owner and reviewer |

## Shared baseline

- Specification: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` (`APPROVED` on `2026-08-05`)
- Change: `CHG-20260805-009`
- Context: [workflow-governance/main.md](../../../doc/context/workflow-governance/main.md)
- Documentation baseline: `04146af` (`docs: draft continuous workflow governance`)
- Delivery environment: local Python workflow-router POC plus detached Codex/Claude guidance source. No hosted service, background worker, target-project dependency, or external provider is in scope.

## Authority and handoff

Codex/current worktree is the control-plane owner and reviewer. The implementation owner is the separate `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree on branch `codex/implementation-private-router-saas-01`. It is currently based on `7769710` and must fast-forward to `main` before the first red test. The project owner must still explicitly approve this ticket before any source, test, migration, deployment, or implementation commit begins.

The implementation handoff consists of the approved specification, this ticket, Context references, TDD cuts, exact target paths, and the return-event rules. A completion returns evidence for review; a requirement, architecture, public-contract, frontend composition/DI, or acceptance change returns `REQUIREMENT_CHANGED` to Grill.
