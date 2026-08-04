# Continuous Workflow Governance — Grill Context

| Field | Value |
| --- | --- |
| Context state | `GRILL_COMPLETE_TO_SPEC` |
| Router event | `REQUIREMENT_CHANGED` after commit `7769710` and the owner's instruction to continue directly into Grill |
| Delivery stage | `POC` |
| Requirement change | `CHG-20260805-009` |
| Baseline | `7769710` (`docs: require frontend composition handoff`) |
| Control-plane owner | Codex / current worktree |
| Implementation owner | Unassigned; required only before an approved implementation ticket can enter `IMPLEMENT` |
| Required sources read | `AGENTS.md`, `Workflow.md` (Router, Grill, change control, specification, tickets, role boundary), `Defined_wayfinder.md`, `CONTEXT.md`, `PRD.md`, `ProjectSchedule.md`, `doc/RequirementChangeLog.md`, existing Private Router POC Context and specification |

## Trigger and bounded scope

The owner corrected an observed behavior: after the policy/documentation commit, the Agent ended the task instead of emitting a completion event and continuing into Grill. The requested outcome is continuity through safe stages, not an autonomous background process or bypass of a real human approval gate.

This change governs the reusable workflow/plugin control plane. It does not change a company project, install a dependency, transmit Context content, add a service, or alter the completed `private-router-saas` ticket retroactively.

## Grill findings

| Question | Confirmed answer / decision |
| --- | --- |
| Is a commit a workflow terminal? | No. A commit, including a docs-only commit, is evidence that emits `ACTION_COMPLETED`. Router classification must occur before the Agent replies or declares the task complete. |
| When may the loop continue automatically? | Only when the Profile declares a legal transition, minimum required evidence exists, one permitted capability is selected, and no new human authority is required. The control plane then reads only the next-stage sources and performs one legal action before re-evaluating. |
| When must it wait? | Only for an explicit Profile/user authority gate, including specification approval, ticket approval, an unchosen material product decision, or an irreversible external side effect. A missing implementation owner is a material assignment decision before implementation, not a generic pause. |
| When must it halt? | Missing or invalid source, denied authority, unavailable capability, invalid Router decision, security/privacy issue, failed validation, or undeclared transition. It must not describe such a condition as a wait or invent a fallback Profile. |
| Who changes source and tests? | A separately named implementation owner. The control-plane Agent provides approved Context/SPEC/ticket and reviews returned evidence but does not make the implementation commit under the default role boundary. |
| How does implementation return to control? | The implementation owner returns an evidence event for a completed ticket. Any ambiguity or change to requirements, architecture, public contract, frontend composition/DI boundary, or acceptance criteria emits `REQUIREMENT_CHANGED` and routes back to Grill. |
| What must a frontend ticket contain? | Component/screen/layout composition boundaries; Composition Root location and scope; named injectable interfaces and production bindings; test fakes/stubs; and loading, empty, error, permission, and accessibility acceptance criteria. Non-frontend tickets record `N/A` with a reason. |

## Proposed control-flow contract

```text
completed action or commit
  -> ACTION_COMPLETED
  -> RouterDecision
      -> AUTO_CONTINUE: run one declared safe next-stage action, emit next event, re-evaluate
      -> WAIT_FOR_HUMAN: state only the exact authority/decision needed
      -> HALT: preserve evidence and report the concrete fail-closed condition

approved ticket + named implementation owner
  -> implementation handoff packet
  -> implementation evidence event -> review/handoff
  -> requirement/architecture/UI-contract change -> REQUIREMENT_CHANGED -> Grill
```

The handoff packet contains only approved artifact references, acceptance criteria, verified Context references, public-contract constraints, TDD cuts, and—where relevant—the frontend Composition Root and DI design. It does not grant the implementation owner permission to rewrite the product decision.

## Risks and controls

1. **Host turn limitation:** a skill cannot create a new Codex/Claude turn after the host has ended one. Control: continuity is mandatory within the active task; a later service/worker requires a separate approved change.
2. **Role deadlock:** a ticket cannot start without a separate named implementation owner. Control: Router emits an explicit assignment wait only at the implementation entry boundary; the control-plane Agent does not silently take over.
3. **False continuity:** a failure may be mislabeled as a wait. Control: test/validation must distinguish `WAIT_FOR_HUMAN` from `HALT`, with no fallback route.
4. **Frontend design drift:** a UI ticket can become a visual instruction with hidden dependencies. Control: ticket creation and review block the ticket unless its composition/DI evidence is complete.
5. **Context growth:** return events could copy full documents. Control: the handoff uses immutable artifact references, source span/revision, side-context ID, consumer fingerprint, and evidence digest; raw ContextPacket text remains local and ephemeral.

## Convergence

The Grill result is **GO to specification**. The complete scope has one formal draft: `modules/spec/workflow-governance.md`. No ticket may be created until the project owner explicitly approves that specification. The previous commit remains valid as the initial documentation baseline; any follow-up enforcement edit must be made by the future separately named implementation owner under an approved ticket.
