# Continuous Workflow Governance POC — Ticket Set

> Approved specification: [workflow-governance.md](../../spec/workflow-governance.md) (`SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`). This ticket set creates no implementation authority by itself.

## Delivery objective

Deliver one control-plane policy vertical slice: completion evidence must re-enter the Router, safe stages continue in the active task, declared authority gates wait precisely, unsafe conditions halt, and implementation work returns its evidence or a requirement-change event to the control plane. The slice applies the same rules to formal frontend handoff without adding a target-project runtime dependency.

## Ticket status

| Ticket | User-observable capability | State | Required authority |
| --- | --- | --- | --- |
| [01-enforce-continuation-and-handoff](01-enforce-continuation-and-handoff.md) | Post-commit Router continuation, typed implementation return, and policy/template enforcement | `DONE` | Review approved; integrated into `main` by merge `2f545c8` (the ticket file records the closure; this row had gone stale) |
| [02-repo-contained-worktree-layout](02-repo-contained-worktree-layout.md) | Every agent's worktree lives under the repository root, proven host-side | `CLOSED` | Owner-executed 2026-08-19; R1-R6 green, reverse mutation proven. The dispatch-admission gate its R3 anticipated is now wired by workstation-dispatch W1 |
| [03-suite-order-fragility](03-suite-order-fragility.md) | A poisoned shared runtime root is reported once, with its cause and remedy, instead of eighty misleading failures | `CLOSED` | Real cause found: per-process claim map versus a shared on-disk root, orphaned by concurrent pytest processes. The opening diagnosis was wrong and is corrected in place |
| [04-skill-implies-a-runtime-that-may-not-exist](04-skill-implies-a-runtime-that-may-not-exist.md) | The skill no longer narrates wakes nothing performs; agents must verify automation readiness before claiming any automatic effect | `CLOSED` | Found by the owner watching a false wake narrative on a real project; ships as 0.4.4 |
| [24-independent-admitted-ticket-continuation](24-independent-admitted-ticket-continuation.md) | A waiting ticket cannot freeze an unrelated admitted ticket or transfer its authority | `PARTIAL_REVIEWED / FULL_CLOSURE_BLOCKED` | Candidate `953c2cea` rejected; `e0bbe9e5` Owner-effect slice approved, independent ticket replay absent |
| [25-refactor-test-seam-transfer](25-refactor-test-seam-transfer.md) | A responsibility split moves behavior tests and mutation targets with the production seam before the next split | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `970b99cc`; overall checklist 04 still open |
| [26-active-writer-worktree-branch-uniqueness](26-active-writer-worktree-branch-uniqueness.md) | The existing worker-claim ledger rejects two active writers on one worktree or branch | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `9cedb55f`; generic prewrite protection still open |
| [27-evidence-linked-ticket-status-projection](27-evidence-linked-ticket-status-projection.md) | Opt-in evidence-bearing stage projection rejects false APPROVED with required work unverified | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `3196712d`; parent/finding closure still open |
| [28-minimal-complete-dispatch-ticket](28-minimal-complete-dispatch-ticket.md) | One ticket template carries sourced Expected, I/O, failure/boundary acceptance and stop/review conditions | `CLOSURE_REVISION_02 / REIMPLEMENT_ADMITTED` | Convergence fixed active-slot proof; prior two refusals and budget preserved |
| [29-mainline-ticket-projection](29-mainline-ticket-projection.md) | Separate the work mainline from a single ticket; recommend next recheck without granting dispatch | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `2fa4ca6f`; trusted source and formal closure remain open |

## Shared baseline

- Specification: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` (`APPROVED` on `2026-08-05`)
- Change: `CHG-20260805-009`
- Context: [workflow-governance/main.md](../../../doc/context/workflow-governance/main.md)
- Documentation baseline: `04146af` (`docs: draft continuous workflow governance`)
- Delivery environment: local Python workflow-router POC plus detached Codex/Claude guidance source. No hosted service, background worker, target-project dependency, or external provider is in scope.

## Authority and handoff

Codex/current worktree is the control-plane owner and reviewer. The implementation owner is the separate `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree on branch `codex/implementation-private-router-saas-01`. It is currently based on `7769710` and must fast-forward to `main` before the first red test. The project owner approved this ticket on `2026-08-05`; source/test work is authorised only in that assigned worktree.

The implementation handoff consists of the approved specification, this ticket, Context references, TDD cuts, exact target paths, and the return-event rules. A completion returns evidence for review; a requirement, architecture, public-contract, frontend composition/DI, or acceptance change returns `REQUIREMENT_CHANGED` to Grill.
