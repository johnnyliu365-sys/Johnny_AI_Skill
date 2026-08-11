# Autonomous Multi-AI Collaboration and Audit POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` |
| Status | `APPROVED` |
| Author / baseline | Codex control plane / `main` / `4feeb94` |
| Context | `doc/context/autonomous-collaboration-audit/main.md` |
| PRD | `PRD.md §14` |
| Change | `CHG-20260805-010`; reviewer-only authority revision `CHG-20260811-012` |
| Shared Context | `CONTEXT.md §衍生 SPEC 索引` |
| Implementation language | Python 3.11 for Router contracts/tests; Markdown for workflow/skill/templates |

## Problem, goal and exclusions

The current repository has completed Router and post-commit-continuation POCs, but its active documents still retain a commercial SaaS direction and a single project stage cannot model a planning Agent moving to the next Grill while an implementation Agent works on a dispatched ticket.

This POC makes the repository a non-commercial, detachable multi-AI collaboration and audit control plane. It must select a named collaboration topology, wait only for explicit ticket-delivery confirmation, run planning and ticket-execution lanes with separate state, provision safe Git work, route valid work automatically to integration and Grill audit, and expose every true human wait precisely.

Out of scope: SaaS, pricing, billing, user accounts, entitlements, remote/private Router deployment, model hosting, automatic host-thread/model creation, target-project runtime coupling, hooks, CI integration, production deployment, raw-content transfer, and changes to a target company project.

## User flow and acceptance criteria

1. On plugin application/takeover, before implementation planning, the control plane asks for the available coding-Agent count: `1` or `2`. It records only a typed topology and named capabilities; it does not claim to create a host thread or select a model itself.
2. For `1`, the topology reserves the existing main session for control-plane work and requires a separate implementation session/worktree. For `2`, it supports a named control-plane/main Agent and named implementation Agent; Claude-control/Codex-implementation is a recommendation, not a hard-coded vendor requirement.
3. A `PLANNED` ticket proposal is not yet an opened ticket. When the control plane formally opens one committed ticket, it immediately becomes `IN_PROGRESS` and emits `TICKET_DISPATCH_REQUIRED`. The displayed question names the ticket and its implementation owner. A positive delivery confirmation is that ticket's scoped approval and dispatch authority. Its reviewed ticket/handoff artifact identity is also bound to a named, validated opaque project ID, so an otherwise identical record from another authorized project cannot dispatch or render; a raw path, URI or arbitrary nonblank string is not a project ID. No reply or a negative reply produces only `WAIT_FOR_HUMAN` with no branch, Context, capability or implementation grant.
4. A confirmed dispatch requires a typed receipt that references the committed ticket, named implementation owner, reviewed handoff, expected base revision and correlation ID. It provisions one isolated branch/worktree and emits `IMPLEMENTATION_DISPATCH_CONFIRMED`.
5. The receipt simultaneously sends the planning lane to the next declared Grill and the ticket lane to `IMPLEMENT`. Their state, ContextView, source grants, consumer fingerprint, event IDs and safety ceilings are independent. Planning cannot change an approved active ticket.
6. The implementation owner starts from the approved main base, follows TDD, verification and commit rules, and returns only typed completion/block/change evidence. It cannot write the main control-plane worktree.
7. A valid completed ticket return with matching base revision, clean integration state and passing required checks triggers exactly one guarded local `main` integration by the main-owner capability, then immediately routes a Grill audit. Integration does not mean deploy, push, handoff, or permission to start dependent work.
8. A failed audit yields `CHANGES_REQUESTED` and provisions a correction worktree; an invalid/stale/conflicting return, failed validation, missing owner, unavailable capability or failed merge is `HALT`. Neither condition is disguised as a human wait.
9. After Grill-to-SPEC approval has produced committed ticket and handoff documents, the control-plane response exactly contains `工單 ready`, ticket docs commit, ticket reference, `文件交接`, handoff docs commit, implementation owner, and the dispatch-confirmation question.
10. Existing commercial Router POC records remain historical; no new commercial wording, price, entitlement, SaaS/hosted-service capability or payment integration may be introduced by this POC.
11. Waiting for an active ticket's typed implementation return is an automatic event wait, not `WAIT_FOR_HUMAN`: its monitor wakes the planning lane and re-evaluates pending ticket proposals without prompting the user.
12. Only the ticket's named reviewer may invoke Agent-to-Agent orchestration for its implementation owner: create/spawn/fork, dispatch/follow-up, steer, wait, interrupt and close. A valid effect binds project, ticket, reviewed handoff, unconsumed receipt, reviewer, target implementation owner, action and correlation.
13. The implementation owner has no orchestration authority. Direct tool calls, indirect adapters, copied/forged reviewer identity, wrong target and replay all return `HALT / ROLE_FORBIDDEN` before an Agent/thread effect. Model, agent name and prompt text are never authority.

## Domain model, data flow and responsibility boundary

```text
CollaborationTopology = ONE_IMPLEMENTATION_AGENT | TWO_COLLABORATING_AGENTS
TicketProposal = { ticket_id, state: PLANNED, dependency_refs }
PlanningLaneState = { project_id, stage, topology, artifact_refs, active_ticket_refs }
TicketLaneState = { ticket_id, dispatch_state, execution_stage, expected_main_revision,
                    implementation_owner, reviewer, artifact_refs }
TicketDispatchReceipt = { ticket_ref, implementation_owner, handoff_ref,
                          expected_main_revision, event_id, acknowledgement }
ApprovedDispatchArtifact = { project_id, ticket_ref, handoff_ref,
                              implementation_owner, ticket_docs_commit,
                              handoff_docs_commit }
TicketEvent = TICKET_DISPATCH_REQUIRED | IMPLEMENTATION_DISPATCH_CONFIRMED
            | IMPLEMENTATION_RETURNED | INTEGRATION_COMPLETED | AUDIT_COMPLETED
AgentRole = REVIEWER | IMPLEMENTATION_OWNER
OrchestrationAction = CREATE | DISPATCH | FOLLOW_UP | STEER | WAIT | INTERRUPT | CLOSE
ReviewerOrchestrationGrant = { project_id, ticket_ref, reviewed_handoff_ref,
                               receipt_ref, reviewer_id, implementation_owner_id,
                               action, correlation_id }
OrchestrationDecision = AUTHORIZED | ROLE_FORBIDDEN | RECEIPT_INVALID
```

The control-plane/main owner owns Wayfinder, Architecture, Grill, Context, SPEC, tickets, dispatch question, guarded integration, audit and handoff. The implementation owner owns only its assigned ticket branch/worktree, TDD, source/tests, verification and implementation commit. The integration capability may update `main` only while holding an exclusive project lock and only after a validated return; it is an automated action, not a second human approval.

For Agent-to-Agent effects the named reviewer, not a generic control-plane or implementation capability, is the sole authority. The orchestration adapter accepts only a previously issued exact grant and consumes its receipt/action binding at most once. It exposes no fallback that infers authority from an agent profile string.

`ImplementationHandoff` and `ImplementationReturn` remain metadata-only. New topology/dispatch values may carry opaque IDs, revision digests, event IDs, artifact references and consumer fingerprints, never raw ContextPacket/source/document text, prompt, path, URI, Secret or PII.

## API, persistence, permission and operations

This POC extends local typed Router/Profile/skill/template contracts only. It adds no network API, database, cache, provider, credential or deployment. A local persistence adapter may save only validated descriptors required to resume lane state; raw Context stays ephemeral and local to the consuming Agent worktree.

`WAIT_FOR_HUMAN` is allowed only for topology selection, SPEC approval, the ticket dispatch question and irreversible external actions. Dispatch confirmation is the ticket-scoped approval; it must not be split into a second ceremonial approval. `HALT` is required for invalid, unavailable or unsafe technical conditions. The host's own conversation/model/worktree permissions remain authoritative.

## Frontend composition and dependency injection

`N/A` — this POC changes no formal end-user frontend. If a future UI is added, it must define its composition boundary, Composition Root, injected interfaces, bindings, test fakes and loading/empty/error/permission/accessibility acceptance before implementation.

## Implementation handoff and return

The future ticket must identify a separate implementation owner, reviewer, ticket branch/worktree, expected main revision, dispatch receipt, Context references, TDD cuts and verification commands. `COMPLETED` returns to guarded integration/audit; `BLOCKED` halts; `CHANGE_DETECTED` emits `REQUIREMENT_CHANGED` to Grill. The main owner and implementation owner must never share a worktree without a ticket-scoped project-owner override.

## TDD design and Code Review checks

The approved implementation ticket must first produce executable red evidence for every new behaviour:

1. Topology selection rejects no/unknown Agent count and unavailable named capability without granting execution.
2. Dispatch has direct and indirect Router tests: missing/negative confirmation waits with no grants; a typed affirmative receipt creates exactly one ticket work plan and routes planning to Grill.
3. Parallel-lane tests prove a planning Grill event cannot mutate the active ticket lane and cannot reuse its ContextView/side-context IDs.
4. Branch/integration tests cover matching base, stale base, dirty main, conflict, duplicate return and lock contention. Every unsafe case halts before merge.
5. Audit tests prove valid integration emits one audit action; changes requested create a correction route without handoff/push/deploy.
6. Fixed response tests assert the required Chinese labels and commit/ticket/owner references.
7. A ticket-open event changes only the selected proposal to `IN_PROGRESS`, emits its dispatch question once, and an implementation return wakes dependent proposals without a human prompt.
8. CodeReview.md §2.1: seven locator forms for any worktree/path boundary, null/empty values, direct/indirect authorization bypass, N/A token scan, stable error mapping, adapter exceptions, and reverse/mutation proof for dispatch and integration guards. The approved-artifact project-ID boundary rejects null/empty/whitespace and path/URI/traversal values. Dispatch authorization tests instantiate a second entitled opaque project with otherwise identical ticket/handoff/owner/commit values; it must halt before pending state, rendering, receipt acceptance or lane grant.
9. Reviewer-only orchestration tests cover every finite action. One exact reviewer grant succeeds once; implementation-owner direct calls, an indirect wrapper, generic control-plane substitution, copied/forged reviewer, wrong ticket/handoff/receipt/target/correlation and replay all return `ROLE_FORBIDDEN` or the exact receipt error before a fake host effect. Reverse mutation of the role check and receipt consumption must fail their matching tests.

## Risks, compatibility, rollback and deployment

- The skill cannot create an external Codex/Claude host conversation or force a chosen model. It must halt/ask only when that host capability is absent.
- Merging prior to Grill audit leaves local `main` in `PENDING_AUDIT`; it must not be pushed, handed off, deployed or used by dependent implementation until audit passes. A failed audit creates a correction route.
- Existing metadata-only Router POC contracts may have commercial names. They remain historical until a scoped cleanup ticket replaces/removes them; no silent deletion or compatibility claim is made here.
- Rollback reverts the future policy implementation commit. No data migration, deployment or target-project recovery is required.

## Convergence and backlinks

- Shared Context: `CONTEXT.md`, this SPEC, PRD §14 and `CHG-20260805-010`.
- Grill result: `GO to specification`; ticket planning is authorised.
- Required approval: project owner approved this exact SPEC on `2026-08-05`. For each named ticket, a positive dispatch confirmation is the separate, ticket-scoped implementation authority.

## Revision signatures

| Date | Author / baseline | Summary |
| --- | --- | --- |
| 2026-08-05 | Codex control plane / `4feeb94` | Initial non-commercial multi-AI collaboration and audit draft. |
| 2026-08-05 | Project owner | Approved the SPEC and authorised ticket planning only. |
| 2026-08-05 | Project owner | Clarified that `已轉交` is the named ticket's approval and dispatch confirmation, not a second approval after delivery. |
| 2026-08-11 | Project owner / `CHG-20260811-012` | Approved reviewer-only Agent orchestration and implementation-owner tool denial; integrated tickets remain immutable evidence and a new Ticket 04 carries the delta. |

## Approval record

- Decision maker: project owner.
- Date: `2026-08-05 (Asia/Taipei)`.
- Approval scope: this SPEC including the `CHG-20260811-012` revision and ticket planning. A ticket's source/test implementation is authorised only when a named implementation owner/worktree receives the ticket and the project owner confirms dispatch; only the named reviewer may perform Agent-to-Agent orchestration and no separate ceremonial ticket approval is required.
