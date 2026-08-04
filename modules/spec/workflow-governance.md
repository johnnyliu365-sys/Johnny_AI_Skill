# Continuous Workflow Governance POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` |
| Specification state | `APPROVED` |
| Authoring AI / baseline | Codex control plane / current worktree / `7769710` |
| Investigation Context | `doc/context/workflow-governance/main.md` |
| PRD reference | `PRD.md §13` |
| Requirement change | `CHG-20260805-009` |
| Shared Context backlink | `CONTEXT.md §衍生 SPEC 索引` |
| Delivery stage | `POC` |
| Implementation language | Python 3.11 for `library/workflow_router`; Markdown for workflow/skill/template policy artifacts |

## Problem, Goal, and Non-goals

The workflow describes automatic continuation, but an Agent can still treat a commit as the end of an active task. The control/implementation role split and frontend composition/DI rule also need an executable handoff and return contract, rather than isolated documentation statements.

This POC makes completion routing explicit. Every completed action—including a docs-only or implementation commit—emits `ACTION_COMPLETED`; the Router then determines the only legal continuation. It also makes implementation ownership, return events, and frontend architecture evidence mandatory for future tickets.

### In scope

- A policy contract that treats a commit as non-terminal completion evidence.
- Exact boundaries for `AUTO_CONTINUE`, `WAIT_FOR_HUMAN`, and fail-closed `HALT` after each completion event.
- A typed conceptual handoff/return model between control-plane and separately named implementation owners.
- Ticket/template/skill enforcement for frontend composition-first design and dependency injection.
- Static documentation and future policy-contract tests that can prove the above behaviour.

### Out of scope

- Target-project runtime dependencies, automatic source edits, model execution, model hosting, a background worker, an external Agent dispatcher, or bypassing Codex/Claude host approval controls.
- Any source, test, migration, deployment, or implementation commit by the control-plane Agent under the default role boundary.
- Changing completed tickets retroactively or granting a universal exception to the separate-owner rule.
- Copying raw ContextPacket content into Router state, handoff packets, telemetry, or shared Context.

## User Flow and Acceptance Criteria

```text
completed action/commit
  -> ACTION_COMPLETED
  -> Router Decision
       AUTO_CONTINUE -> exactly one safe next-stage action -> next event -> re-evaluate
       WAIT_FOR_HUMAN -> request the named approval/decision only
       HALT -> record the concrete fail-closed reason

approved ticket + control owner + separate implementation owner + reviewer
  -> implementation handoff packet
  -> implementation evidence -> review / handoff
  -> change detected -> REQUIREMENT_CHANGED -> Grill
```

Acceptance criteria:

1. A commit cannot alone end an active routed task. The control plane emits `ACTION_COMPLETED`, obtains one Router decision, and follows that decision before replying with a terminal status.
2. `AUTO_CONTINUE` occurs only for a declared Profile transition with required evidence, exactly one selected permitted capability, and no new human authority. It executes one legal action at a time and re-evaluates after each emitted event.
3. `WAIT_FOR_HUMAN` is used only for a declared approval/decision gate or irreversible external side effect. Its message identifies the exact decision or approval required.
4. Missing/invalid sources, missing/denied authority, unavailable capabilities, invalid decisions, validation/security/privacy failures, or undeclared transitions return `HALT`; the Agent neither invents a fallback route nor calls the condition a wait.
5. A ticket cannot enter implementation unless it names a control-plane owner, a separate named implementation owner, and a reviewer. An implementation owner returns completion evidence to the control plane and escalates any requirement, architecture, public-contract, frontend-design, or acceptance change as `REQUIREMENT_CHANGED`.
6. Every formal frontend ticket identifies component composition boundaries, Composition Root path/scope, named injectable interfaces, production bindings, test doubles, and loading/empty/error/permission/accessibility criteria. A non-frontend ticket explicitly records `N/A` with a reason.
7. The policy retains the detached-plugin contract: no target project imports the skill, relies on its cache, service, hook, CI, or runtime path. Host approval controls remain authoritative.
8. The handoff and return model records artifact references, source revision/span, side-context ID, consumer fingerprint, and evidence digest only. It must not persist raw source/document/prompt/ContextPacket text.

## Domain Model, Data Flow, and Responsibility Boundaries

```text
CompletionEvidence = {
  event_id,
  action_kind: DOCUMENTATION | IMPLEMENTATION | REVIEW | HANDOFF,
  artifact_refs,
  commit_ref?,
  verification_refs,
  emitted_event: ACTION_COMPLETED
}

ContinuationClass = AUTO_CONTINUE | WAIT_FOR_HUMAN | HALT

ImplementationHandoff = {
  ticket_ref,
  approved_spec_ref,
  context_refs,
  acceptance_refs,
  tdd_cut_refs,
  frontend_composition_ref?,
  control_owner,
  implementation_owner,
  reviewer
}

ImplementationReturn = {
  ticket_ref,
  status: COMPLETED | BLOCKED | CHANGE_DETECTED,
  evidence_refs,
  verification_refs,
  emitted_event: ACTION_COMPLETED | REQUIREMENT_CHANGED
}
```

The control-plane Agent resolves the Router decision, minimum Context view, specification, ticket, handoff, review, and release evidence. It must not perform implementation work by default. The implementation owner implements only the approved handoff; it must not change scope, public contracts, architecture, UI composition, DI boundaries, or acceptance conditions without returning `CHANGE_DETECTED` and causing `REQUIREMENT_CHANGED`.

`CompletionEvidence` is an event descriptor, not a replacement for Git history or a permission to commit. It may reference a commit SHA when one exists, but a Router still verifies required sources and authority from the active Profile.

## Frontend Composition and Dependency-Injection Contract

For a ticket touching formal frontend/UI scope:

1. Pages, screens, layouts, and components have explicit composition responsibilities, inputs, outputs, and state boundaries. Business rules, data transforms, and side effects do not hide in an untestable visual component.
2. API clients, repositories, stores, navigation, clock, feature flags, analytics, i18n, permissions, and equivalent external capabilities enter through named interfaces and a Composition Root. Components do not create global singletons, read environment configuration, or access services implicitly.
3. The ticket defines Composition Root location, lifecycle/scope, production bindings, and the fake/stub substitutions used by tests.
4. Tests verify composition, injected dependency replacement, loading, empty, error, permission, and accessibility behaviour without live network, global state, or clock dependence.

For a non-frontend ticket, the ticket’s frontend section must read `N/A` and name why the scope does not touch a formal UI boundary.

## API, Event, Persistence, Permission, and Operations

This POC changes workflow policy and shared contracts; it adds no network API, database, cache, provider, credential, or deployment target. `ACTION_COMPLETED` and `REQUIREMENT_CHANGED` are existing Router event classes given explicit completion and return semantics.

The future policy implementation may update Workflow/skill/template source and policy-contract tests only through a separately approved ticket. If a future implementation adds a runtime worker, hosted service, or external dispatcher, it is a new requirement change and must begin at the relevant earlier gate.

## Test Cuts and TDD Design

The future implementation ticket must begin red and include the following explicit checks:

1. **Normal continuation:** a valid completed documentation or implementation action emits `ACTION_COMPLETED`, executes the single declared safe action, and re-evaluates rather than ending the active task.
2. **Approval gate:** a specification or ticket authority gate returns `WAIT_FOR_HUMAN` with a precise approval request and performs no unauthorized next-stage action.
3. **Fail-closed classification:** missing source/owner/authority/capability, invalid decision, privacy/security failure, and undeclared transition return `HALT`, not `WAIT_FOR_HUMAN` or a local fallback.
4. **Role boundary:** the default control-plane actor cannot be accepted as the implementation owner; a valid handoff contains separate control, implementation, and review responsibility references.
5. **Frontend contract:** a frontend ticket missing any composition/DI field is blocked; a non-frontend ticket with explicit `N/A` reason remains valid.
6. **Return path and regression:** a completed implementation return reaches review/handoff; a changed requirement routes to Grill; existing Router, telemetry, plugin-detach, and private Router POC behaviour remains valid.

## Risks, Compatibility, Rollback, and Deployment Preconditions

- **Host lifecycle limitation:** skills cannot force a new host model turn. Compatibility control: require continuation only while the active task exists; do not claim autonomous background operation.
- **Assigned-owner delay:** a separate implementation owner may be absent. Control: issue a precise assignment wait before implementation rather than allowing an unauthorized takeover.
- **Incorrect continuation:** a rule implementation may label an error as a wait. Control: contract tests cover each `HALT` condition and require no fallback Profile.
- **Documentation drift:** skills, Workflow, and templates can diverge. Control: the future ticket updates them as one atomic policy change and validates their cross-references.
- **Rollback:** revert the future policy implementation commit. The plugin remains detachable and target projects remain untouched; no data migration or deployment rollback is required.

## Convergence and Backlinks

- Shared Context backlink: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`, `modules/spec/workflow-governance.md`, control-plane POC only, `PRD.md §13`, `CHG-20260805-009`.
- Grill convergence: `doc/context/workflow-governance/main.md` confirms a GO to specification. This draft is the only active specification for the change.
- Baseline: `7769710` (`docs: require frontend composition handoff`). Its documentation remains the current policy baseline until a future ticket is approved and implemented.

## Revision Signatures

| Date | AI / baseline SHA | Summary |
| --- | --- | --- |
| 2026-08-05 | Codex control plane / `7769710` | Initial draft after the owner-directed post-commit Grill. |
| 2026-08-05 | Project owner / `04146af` | Approved the POC specification and authorised ticket planning only. |

## Approval Record

- Decision maker: project owner.
- Date: `2026-08-05 (Asia/Taipei)`.
- Approval scope: Continuous Workflow Governance POC specification. Ticket planning is authorised. No source, test, migration, deployment, or implementation commit is authorised until a second explicit ticket approval and a separate named implementation owner are recorded.
