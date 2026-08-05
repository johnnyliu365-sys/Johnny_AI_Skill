# Autonomous Multi-AI Collaboration and Audit — Grill Context

| Field | Value |
| --- | --- |
| Context state | `TICKET_01_DISPATCHED_PLANNING_GRILL` |
| Router event | `REQUIREMENT_CHANGED` after completion of the previous workflow-governance POC |
| Delivery stage | `POC` |
| Requirement change | `CHG-20260805-010` |
| Baseline | `4feeb94` (`docs: complete workflow governance handoff`) |
| Control-plane owner | Codex / current `main` worktree |
| Implementation owner | Codex implementation Agent / existing `workflow-implementation` worktree for ticket 01 |
| Required sources read | `AGENTS.md`, `Workflow.md` (Router, Grill, change control, specification, tickets, role boundary), `Defined_wayfinder.md`, `PRD.md`, `CONTEXT.md`, `ProjectSchedule.md`, `RequirementChangeLog.md`, completed Router/Workflow Governance POCs |

## Confirmed positioning

The repository is a non-commercial, detachable multi-AI workflow and audit control plane. It is not a SaaS, payment product, hosted private Router, model host, target-project runtime, CI dependency, or deployment service. The previously completed private Router POC remains historical technical evidence only.

## Collaboration topology selection

The project owner selected `1` available coding Agent on `2026-08-05`:

- Control-plane / planning / integration / reviewer: Codex, current `main` worktree.
- Implementation owner: Codex implementation Agent, existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree on `codex/implementation-private-router-saas-01`.
- Current implementation worktree HEAD: `a94e207`, confirmed as an ancestor of the current main ticket baseline `2372f1e` with five commits to synchronize. Only the implementation owner may perform that synchronization in its own worktree after ticket approval.
- Selected ticket: `01-topology-dispatch-lanes`. The owner replied `已轉交` on `2026-08-05`; this is the ticket-scoped approval and dispatch receipt. The implementation owner may synchronize its own worktree from this dispatch record, then start TDD.

## Ticket 01 dispatch receipt

| Field | Value |
| --- | --- |
| Ticket | `01-topology-dispatch-lanes` |
| Confirmation | Project owner: `已轉交` (`2026-08-05`) |
| Authority | Scoped approval plus delivery confirmation; no separate ticket-approval wait |
| Implementation owner | Codex implementation Agent / `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` / `codex/implementation-private-router-saas-01` |
| Control-plane / reviewer | Codex / current `main` worktree |
| Required action | Implementation owner synchronizes this dispatch-record main commit in its own worktree, then records its first red test before source implementation. |
| Planning-lane result | `AUTO_CONTINUE → GRILL` for ticket 02; it does not alter ticket 01's approved scope. |

## Grill decisions

| Question | Confirmed decision |
| --- | --- |
| What must start after plugin application? | Ask the user how many coding Agents are available: one implementation Agent with a separate implementation conversation/worktree, or two collaborating Agents with a named control-plane and implementation role. The plugin cannot itself create a host conversation or select a model; it only resolves the required capability/topology. |
| What does one-Agent availability mean? | It still uses two role-isolated sessions: the existing main control-plane session for Wayfinder/Grill/SPEC/tickets/audit and one newly provisioned implementation session/worktree. Host/model suggestions are capability preferences, not enforceable Router authority. |
| What does two-Agent availability mean? | A recommended topology is Claude as control-plane/main and Codex as implementation owner. Equivalent named capabilities are permitted if they satisfy the same role and worktree separation. |
| When does ticket dispatch wait? | After a committed ticket names an implementation owner, the control plane asks: `工單 <ticket-id> 是否已交付給 implementation owner <owner-id>？` No answer (or a negative answer) remains a precise dispatch wait; it is not a failure and does not start implementation. A positive confirmation is that ticket's scoped approval and delivery authority. |
| What follows confirmed dispatch? | Record a typed dispatch receipt, provision the ticket branch/worktree, supply the existing `ImplementationHandoff`, and route the planning lane immediately to the next Grill. The active ticket execution lane proceeds independently. |
| Why are two lanes necessary? | A single `ProjectRouter` stage cannot truthfully be both `GRILL` and `IMPLEMENT`. A project planning lane and one ticket-execution lane per dispatched ticket must have separate typed state, event correlation, ContextView, ownership and safety ceiling. |
| Who merges to `main`? | The `main` owner/integration capability performs an automatic guarded merge after a valid implementation return. The implementation owner never writes another Agent's checked-out `main` worktree. This preserves Git's one-worktree/one-owner invariant while retaining the requested no-human-pause behavior. |
| When is Grill audit run? | Immediately after an eligible integration to local `main`, before handoff, push, deployment or a dependent implementation. A failed audit creates a typed correction return and a new implementation worktree; it never silently declares success. |

## Proposed control flow

```text
plugin applied
  -> COLLABORATION_TOPOLOGY_REQUIRED (one / two coding Agents)
  -> typed topology + named role/worktree plan
  -> Wayfinder → Architecture → Grill → Context → SPEC → approval → tickets → approval

committed ticket + named implementation owner
  -> TICKET_DISPATCH_REQUIRED
  -> WAIT_FOR_HUMAN: confirm ticket was delivered to named implementation owner
  -> IMPLEMENTATION_DISPATCH_CONFIRMED
      ├─ ticket lane: provision branch/worktree → implement → verify → return
      └─ planning lane: next Grill

valid completed ticket return
  -> guarded local main integration
  -> Grill audit
      ├─ APPROVED: handoff-ready evidence
      └─ CHANGES_REQUESTED: correction ticket/worktree
```

## Fixed human-facing response

After a Grill-to-SPEC approval has generated committed ticket and handoff artifacts, the control plane responds only in this shape before the dispatch question. A positive delivery response is the ticket-scoped approval; no second approval question follows:

```text
工單 ready
- commit：<ticket docs commit SHA>
- 工單：<ticket ID / path>

文件交接
- commit：<handoff docs commit SHA>
- implementation owner：<owner ID>
- 需要確認：是否已交付工單給 implementer？
```

## Constraints, risks and exclusions

- A host may require its own user action to create a thread, choose Claude/Codex/model, or grant filesystem access. The plugin must expose this as a capability/authority requirement and cannot claim to bypass it.
- `main` integration requires a mutex and clean expected base SHA. A stale branch, conflict, failed verification, missing owner, or failed audit is `HALT`/`CHANGES_REQUESTED`, never an unsafe merge.
- A planning lane may Grill unrelated next scope while a ticket is executing. It must not alter an already approved ticket, consume the ticket's private ContextPacket, or start dependent implementation before audit approval.
- No SaaS, price, billing, customer account, entitlement, remote Router, network service, provider credential, raw-content transfer, target-project dependency or deployment is in this POC.

## Convergence

### Planning lane Grill — ticket 02 integration and audit

The main control-plane lane has moved to Grill while ticket 01 executes. Ticket 02 is a `PLANNED` candidate, not an opened ticket: opening it later must immediately mark it `IN_PROGRESS` and issue its own one dispatch question. Its externally observable outcome, fake-port boundary, no-real-Git restriction, stale/dirty/conflict/duplicate/lock fail-closed cases, `PENDING_AUDIT` isolation, and correction route are already bounded in the approved SPEC and candidate draft. It depends on ticket 01's eventual public lane/dispatch contracts, so it cannot be opened or receive delivery authority until ticket 01 returns reviewed evidence. This is an automatic event dependency, not a human wait or scope change.

Grill result: **GO — retain ticket 02 scope unchanged and automatically re-evaluate it when ticket 01 returns public contracts.** The planning lane has completed its next legal Grill action and is in an automatic event wait, not a human wait. No additional user decision is required at this point.
