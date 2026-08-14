---
name: johnny-project-takeover
description: Route a new, inherited, or active software project through Johnny's Wayfinder, architecture, requirements, specification, ticket, implementation, review, handoff, POC/MVP/commercial, and staging workflow. Use when Codex must take over or resume a project, select the next governed stage, dispatch or review an implementer, minimize Agent context, or apply Johnny workflow policy without adding a runtime dependency to the target project.
---

# Johnny Project Takeover

Treat this plugin as an external control plane. It guides target-owned work but never becomes a
target project's runtime, CI, hook, import, submodule or symlink dependency.

## Start

1. Read the target project's own `AGENTS.md` and authority record.
2. Read `../../Workflow.md` only far enough to identify the current stage and its routing row.
3. Read exactly the reference named by that row, plus the minimum committed target artifacts it
   requires. Do not load unrelated references, the full library or chat history.
4. Execute one legal action, emit its typed completion event and return to the Router. Do not
   select the next stage locally.

Default delivery maturity is `POC` unless an approved target artifact proves otherwise.

## Reference router

All references are one level below this file and canonical for the named concern. Read each
file completely only when its condition applies.

| Condition or stage | Read |
| --- | --- |
| Any Router event, continuation, dispatch receipt or completion return | [Router control contract](references/router-control.md) |
| Intake profile, resource plan, maturity change, POC freeze or staging | [Delivery profile and lifecycle](references/delivery-profile.md) |
| Model-role assignment, SPEC readiness, architecture-owner sleep/wake or escalation | [Model role lifecycle](references/model-role-routing.md) |
| ContextView, source selection, capability selection or side-context mapping | [Minimal Context routing](references/context-routing.md) |
| Wayfinder, Architecture, Grill or requirement change | [Discovery and change control](references/discovery-change.md) |
| Untrusted data enters Browser/WebView/HTML/DOM/JavaScript | [XSS review](references/xss-review.md) |
| Secret, production log, Provider, webhook or external effect | [Security boundary](references/security-boundary.md) |
| SPEC, ticket, type preflight, frontend contract or dispatch envelope | [Specification and ticketing](references/specification-ticketing.md) |
| Approved-SPEC decomposition, low-model admission or convergence replan | [Ticket decomposition](references/ticket-decomposition.md) |
| Formal UI, Figma/screenshot/brief/design-system input or visual acceptance | [UI design handoff](references/ui-design-handoff.md) |
| Owner/task/worktree admission, Agent control or correction allocation | [Implementation authority](references/implementation-authority.md) |
| Admitted ticket implementation, TDD, type, smoke or completion | [Implementation TDD](references/implementation-tdd.md) |
| Ticket TDD design or independent code review | [Independent review checks](references/review-checks.md) and `../../CodeReview.md` |
| Architecture/SPEC/ticket language decision | [Implementation language policy](references/language-policy.md) |

If an indexed reference is absent, unreadable, version-mismatched or ambiguous, halt before
mutation with `ROUTE_REFERENCE_INVALID`. Do not reconstruct the missing rule from memory.

## Closed loop

```text
INTAKE → WAYFINDER → ARCHITECTURE → GRILL → CONTEXT → SPEC → TICKETS
      → IMPLEMENT → SMOKE_TEST → REVIEW → HANDOFF
```

- `AUTO_CONTINUE`: execute the one declared next action when sources, evidence, authority and
  capability are complete; then route again.
- `WAIT_FOR_HUMAN`: pause only for a declared approval/owner decision or irreversible effect.
- `HALT`: stop on invalid source, authority, capability, verification, security boundary or
  undeclared transition. Never guess, fallback or wait indefinitely.
- `REQUIREMENT_CHANGED`: return to change control and the affected earlier stage.

An implementation or docs-only commit emits `ACTION_COMPLETED`; a commit does not itself select
the next stage. This skill cannot bypass host approval, permission or receipt enforcement.

Durable Router state contains metadata only. A pending dispatch remains bound to its live
descriptor. The implementation owner returns an `ImplementationReturn`; `CHANGE_DETECTED`
emits `REQUIREMENT_CHANGED` rather than changing the ticket locally.

## Minimal implementation handoff

The implementer receives identifiers, not copied governance text: exact ticket/registry commit,
receipt, owner task and at most one bounded resume state. The exact ticket supplies scope,
contracts, TDD, verification and return format. The selected reference supplies the applicable
method. The Router and host gateway supply authority.

## Reusable modules

When reusable source is relevant, invoke `$apply-reusable-modules`, select the minimum `READY`
card and record its ID/revision/contract in approved target-owned artifacts. Any adopted behavior
must become target-owned, versioned and tested. Never link the target runtime to this plugin.

## Detach

Removing the plugin removes only its skills, workflow references and catalog access. It must not
remove or alter target source, configuration, CI, data or formal artifacts.
