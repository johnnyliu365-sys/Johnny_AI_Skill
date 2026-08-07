# Autonomous Multi-AI Collaboration and Audit — Grill Context

| Field | Value |
| --- | --- |
| Context state | `GRILL_CONVERGED_TO_CONTEXT` |
| Router event | `ACTION_COMPLETED` for Architecture, then Grill |
| Delivery stage | `POC` |
| Requirement change | `CHG-20260805-010` |
| Baseline | `4feeb94` (`docs: complete workflow governance handoff`) |
| Control-plane owner | Codex / current `main` worktree |
| Implementation owner | Codex implementation Agent / existing `workflow-implementation` worktree for ticket 01 |
| Required sources read | `AGENTS.md`, `Workflow.md` (Router, Grill, change control, specification, tickets, role boundary), `Defined_wayfinder.md`, `PRD.md`, `CONTEXT.md`, `ProjectSchedule.md`, `RequirementChangeLog.md`, completed Router/Workflow Governance POCs, `ADR-20260805-002` |

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

## Historical pre-Architecture working constraints

> The following are owner-confirmed operating constraints, not a completed Grill decision. They are architecture inputs and must be challenged by the next Grill.

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

## Architecture handoff and Grill convergence

The Architecture stage is supplied by [ADR-20260805-002](../../adr/ADR-20260805-002-autonomous-collaboration-control-plane.md). It defines the two-lane control plane, metadata-only Context boundary, injected external capabilities, `PENDING_AUDIT` isolation, and audit-before-review order.

### Grill findings

| ID | Question and evidence | Result / disposition |
| --- | --- | --- |
| G-01 | Can the existing Router express isolated planning and ticket lanes? `RouterState` has one `stage`; `profile.py` still binds implementation handoff to `TICKETS + APPROVAL_GRANTED → IMPLEMENT`. | The new lane/event public contracts are required. This is within ticket 01's approved scope; its direct and Private Router tests must remove the second approval path rather than preserve it as an alternative. |
| G-02 | Is every approved behaviour owned by a ticket? AC-11 requires a typed implementation return to wake the planning lane, but ticket 01 only covers dispatch and ticket 02 previously listed AC-6 through AC-8. | Ticket 02 now owns AC-11 through an injected event-source fake and dependent-proposal re-evaluation. It remains a `PLANNED` candidate until ticket 01 has reviewed public contracts. |
| G-03 | Does audit approval preserve the mandatory Code Review gate? Ticket 02 previously allowed `APPROVED` audit to permit handoff evidence. | Corrected: audit approval can route only to Code Review. Handoff, push, deployment and dependent work remain blocked until the existing review/handoff flow completes. |
| G-04 | Does the POC falsely promise background host or Git autonomy? `AutomaticContinuationRunner` runs only supplied local actions; `temporal_runtime.py` waits only for a human approval signal. | The POC models automatic routing only after an injected typed return arrives. A real host wake-up, model dispatch, physical worktree or Git operation remains out of scope and must be an explicit future adapter capability. |
| G-05 | Does the Architecture change the authority of ticket 01 already being implemented? | No. Ticket 01 stays `IN_PROGRESS` in its separate worktree and is judged only against its approved dispatch/lane scope. Uncommitted work was not read or used as Grill evidence. |

### Grill decision

**GO to Context with controlled ticket-plan corrections.** No product requirement, delivery stage, owner authority or active ticket 01 scope changed, so no `CHG` or additional human approval is required. Ticket 02 was corrected while still `PLANNED`; it will be automatically re-evaluated only after ticket 01 returns reviewed public-contract evidence. The next legal planning action is to retain this Context and await that automatic event, not to issue another user question.

## Ticket 01 review return

The submitted implementation `9b4d5cb` and docs-only handoff `7a8df21` were reviewed in [01-topology-dispatch-lanes-code-review.md](../../reviews/autonomous-collaboration-audit/01-topology-dispatch-lanes-code-review.md). Result: `CHANGES_REQUESTED`.

The review found that the old `APPROVAL_GRANTED → IMPLEMENT` route remains a direct and indirect dispatch-confirmation bypass; Router state also loses the selected implementation capability/reviewer, the required opened-ticket `IN_PROGRESS` model is absent, and ticket-specific red/edge/mutation evidence is incomplete. Ticket 01 remains `IN_PROGRESS` in its named implementation worktree and returns to implementation. This is not a requirement change, so the planning lane does not re-enter Grill or open ticket 02.

### Correction review — `2e4f13e` / `f295c22`

The correction closes the original legacy-approval bypass, adds the `TicketProposal` `PLANNED → IN_PROGRESS` operation, and preserves the named implementation capability/reviewer in the Router state and ticket lane. Full regression (`84` tests), strict typing (`60` files) and whitespace validation passed against review baseline `8108cd9`.

It is nevertheless still `CHANGES_REQUESTED`. A positive receipt can be sent directly to a fresh Router state, yielding a ticket `IMPLEMENT` lane and planning `GRILL` lane without a persisted opened proposal, one dispatch-question record, or bound human confirmation. The Profile also retains `TICKETS + ACTION_COMPLETED → TICKET_APPROVAL_REQUIRED`, which is the removed ceremonial second wait, and the only valid dispatch path cannot carry and bind the reviewed `ImplementationHandoff`. The formal evidence and required corrections are in [the review report](../../reviews/autonomous-collaboration-audit/01-topology-dispatch-lanes-code-review.md).

Ticket 01 remains `IN_PROGRESS` and returns automatically to its named implementation owner. The control plane has aligned the sole workflow policy in the same review commit; the implementation owner must synchronize that baseline before the corrected return is reviewed again. This is not a requirement change; ticket 02 remains `PLANNED` and no integration, handoff, push, deployment or dependent implementation is authorized.

### Correction review — `43657a0` / `5871ec9`

The submitted correction is still `CHANGES_REQUESTED` and Ticket 01 remains `IN_PROGRESS`. It correctly binds the reviewed handoff and removes the second ticket-approval wait, but its private request envelope accepts `pending_dispatch` from the caller and inserts it directly into `RouterState`. Independent replay showed that a fresh client can submit a constructed matching descriptor and receipt, receiving `AUTO_RUN` and an `IMPLEMENT` ticket lane without issuing the required dispatch question first.

The next correction must make pending dispatch state Router-controlled: persist it from the dispatch-required result, load it internally by the opaque correlation for confirmation, invalidate it after use, and fail closed if a client attempts to supply or forge it. It must also retain a distinct `expected_main_revision`; comparing that integration baseline to `proposal_revision` is semantically invalid even when test fixtures share a value. These are implementation corrections only, not a requirement change. The formal evidence is in [the review report](../../reviews/autonomous-collaboration-audit/01-topology-dispatch-lanes-code-review.md).

### Correction review — `0639db6` / `e97cdcc`

CR-09 and CR-10 are now closed: the Private Router owns the pending descriptor, rejects raw caller-supplied pending data, consumes an accepted confirmation once, and uses a distinct expected-main baseline. Independent regression, strict typing, compilation and diff checks passed.

Ticket 01 remains `IN_PROGRESS` because CR-11 remains. The current service indexes pending state only by account/project/correlation, letting the same ticket issue a second dispatch question under a new correlation before the first is answered. Both correlations can then be confirmed and grant `IMPLEMENT`. The implementation owner must enforce one live pending question per ticket and atomically clear that ticket-level record on a successful confirmation. This is a same-ticket correction, not a requirement change; the formal return is [the review report](../../reviews/autonomous-collaboration-audit/01-topology-dispatch-lanes-code-review.md).

### Correction review — `67b049a` / `3fa2270`

Ticket 01 is now `READY_TO_MERGE`. Independent review approved the ticket-level pending index: a changed-correlation duplicate dispatch now halts with no grant, while successful confirmation clears both correlation and ticket indexes and permits a later reopen. The full regression (`90` tests), strict typing (`60` files), in-memory compilation and diff check passed; the implementation worktree is clean.

This completes ticket 01's approved dispatch/lane scope. It does not directly merge source into local `main`, push, deploy or hand off: guarded integration and its Grill audit are ticket 02's declared scope. The Router continuation is `ACTION_COMPLETED → planning Grill`, where the already planned ticket 02 can be evaluated against the reviewed public contracts.

## Planning Grill — ticket 02 selection

| Field | Value |
| --- | --- |
| Trigger | Ticket 01 review `APPROVED` at `d620463` |
| Required sources | Approved SPEC AC-6 through AC-8 and AC-11; accepted ADR-20260805-002; ticket 02; reviewed ticket-01 public contracts `67b049a`; current Context |
| Decision | `GO → TICKETS` — no requirement, architecture, UI, security or authority change detected |
| Selected ticket | `02-guarded-integration-audit` (`911218d`) |
| State | `IN_PROGRESS`, awaiting only its named delivery confirmation |
| Implementation owner | Codex implementation Agent; a separate ticket-02 worktree is provisioned only after confirmation |
| Reviewer / integration owner | Codex control-plane / current `main` worktree |

### Grill checks

- The reviewed ticket-01 contracts now supply the typed topology, pending-dispatch, receipt, ticket-lane and isolated planning-lane surface required by ticket 02; no speculative interface is needed.
- Ticket 02 owns the missing guarded local-main integration, lock, audit and typed implementation-return behaviour. Its injected fake integration port is a named composition-boundary dependency; it creates no real Git action, host turn, deployment or target-project write.
- No direct source integration is authorized by ticket 01's review. Ticket 02 must model `PENDING_AUDIT` and block push, deployment, handoff and dependent implementation until its audit/review rules are satisfied.
- The ticket selection does not alter ticket 01's approved scope. Its only human gate is the one dispatch-confirmation question below; no second ticket-approval question is permitted.

## Ticket 02 dispatch handoff

| Field | Value |
| --- | --- |
| Ticket docs commit | `911218d` |
| Ticket | `02-guarded-integration-audit` / AC-6 through AC-8, AC-11 |
| Reviewed dependency | Ticket-01 implementation `67b049a`, review approved at `d620463` |
| Owner | Codex implementation Agent / separate ticket-02 worktree after confirmation |
| Reviewer / integration capability | Codex control-plane / current `main` worktree |
| Required handoff metadata | clean expected-main revision, opaque ticket/branch reference, delivery receipt, verification references, Context references and audit requirements |
| Forbidden content | raw source/Context, prompt, path, URI, Git output, Secret and PII |

The pending Router event is `TICKET_DISPATCH_REQUIRED`. No Context, capability, branch, worktree or implementation grant exists until the project owner confirms delivery to the named implementation owner.

## Ticket 02 dispatch receipt

| Field | Value |
| --- | --- |
| Ticket | `02-guarded-integration-audit` / AC-6 through AC-8, AC-11 |
| Confirmation | Project owner: `已交付` (`2026-08-07`) |
| Ticket / handoff baseline | Ticket selection `911218d`; planning-Grill handoff `1d4292a` |
| Authority | Ticket-scoped implementation authority; no second approval or confirmation is required |
| Implementation owner | Codex implementation Agent / a separate ticket-02 worktree; it must not write the control-plane `main` worktree |
| Control-plane / reviewer | Codex / current `main` worktree |
| Execution lane | `IMPLEMENT` — start TDD and return a typed `ACTION_COMPLETED` only with the ticket's required evidence |
| Planning lane | `AUTO_CONTINUE → GRILL` — evaluate the next independently eligible planned ticket without consuming ticket-02 Context |

The receipt activates Ticket 02 only. It grants no physical integration, merge, push, deployment, handoff completion, or authority for any other ticket. Those effects remain guarded by Ticket 02's required evidence and review path.
