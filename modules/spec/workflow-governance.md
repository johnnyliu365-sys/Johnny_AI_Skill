# Continuous Workflow Governance POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` |
| Specification state | `APPROVED` |
| Authoring AI / baseline | Codex control plane / current worktree / `7769710` |
| Investigation Context | `doc/context/workflow-governance/main.md` |
| PRD reference | `PRD-20260805-009` |
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

- Shared Context backlink: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`, `modules/spec/workflow-governance.md`, control-plane POC only, `PRD-20260805-009`, `CHG-20260805-009`.
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

## Proposed revision 02 — trusted continuation and admission (not effective)

| Field | Proposed value |
| --- | --- |
| State | `NOT_EFFECTIVE / OWNER_LIMITED_REVISION_AUTHORIZED / INDEPENDENT_REVIEW_PENDING` |
| Requirement lineage | Existing `PRD-20260805-009` / `CHG-20260805-009`; the proposed amendment in `doc/requirements/active/2026/workflow-governance/REQ-20260805-009.md` |
| Evidence baseline | Owner's 2026-10-18 `doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` revision 14, items 01–03, 07, 09 and 11; Ticket 24 closure revision 03, Tickets 28–30 and 38 and their independent reviews |
| Owner's limited revision authority | On 2026-10-18 the owner accepted final-content commit `1669e8e20f0a30894606e16f9ea1a10e4f0c5ba3` (SPEC blob `be9b79eed12dd76ec8f37fe83f3be90b86a4895d`, identical to this branch's `b6ac5f8a` blob) as the correction baseline, limited to the trusted authority anchor, formal closure and staged activation below; this is not implementation or activation approval |
| Exact revision evidence slots | Corrected proposal commit/blob: `PENDING_THIS_COMMIT` / `PENDING_THIS_BLOB`; independent review report/verdict: `PENDING`; owner exact SPEC approval: `PENDING`; approved build ticket and candidate SHA: `PENDING`; qualification/replay evidence: `PENDING`; scoped activation decision and effective authority ref/SHA: `PENDING` |

This append-only proposal does not revise AC 1–8, the 2026-08-05 approval,
existing ticket grants or completed work. Its intended scope is the current
workflow-governance POC and the existing Router/Host/Review entrypoints. It
does not authorize production SQL, a paid call, a new runner, a target-project
dependency, push, publication or another external effect.

### Additional architecture and acceptance, conditional on owner approval

**AC-9 — trusted cross-ticket mainline and independent continuation.** The
existing target-owned `modules/tickets/<feature>/README.md` index is the
mainline source after a versioned migration records one mainline ID, objective,
owner, handoff reference, required/optional ticket set and exact dependency
edges, bound to approved Context/PRD/CHG/SPEC revisions. Its trust anchor is
the owner's versioned, already admitted `ProjectAuthorityContract` and its
approved declaration artifact: the declared remote repository identity,
validated full `project_authority_ref` and declaration
revision, not a ref supplied by the caller, index or ticket. Before an affected
dispatch, continuation or closure effect, use the existing direct remote
observation contract to read that declared ref afresh and read the official
index and exact ticket leaves from the observed commit. Check remote identity,
full ref, observation freshness, commit and source revisions; a caller's SHA
is only an assertion to compare. The reader derives
the graph from those committed leaves; caller-built
`MainlineProjectionRequest`, local tracking refs, prompts and ticket self-report
are not authority. The Router may consume `mainline_projection.py` only as a
candidate view after the source boundary verifies project, mainline, ticket
identity, revision and graph completeness. Keep raw text ephemeral and durable
Router state metadata-only. A missing, stale, ambiguous, contradictory or
unreadable direct remote or formal source readback blocks only the affected
ticket/closure before its effect; it does not freeze an independently admissible
ticket.

For each candidate ticket, the existing Router/Host dispatch admission must
independently read back that ticket's approved leaf, live grant, owner/worktree
binding, dependency completion and applicable source/evidence revisions at its
own effect boundary. A waits on its precise Owner-owned effect without granting
or executing it; an unrelated B with no dependency on A and its own valid
admission follows its already declared safe route. A dependent C, or B with a
missing/stale grant, source or dependency proof, is refused. B's completion
does not close A or the mainline. No ticket borrows A's receipt, authority,
approval or evidence. `ready_for_recheck` never means admitted.

**AC-10 — pre-effect ticket completeness.** Before either a same-lifetime
native owner spawn or a cross-lifetime receipt/dispatch effect, the admission
actor must read the exact approved ticket leaf and its approved SPEC/AC and
sealed Context bindings. It verifies the ticket has a sourced,
observable Expected; named input/output, finite state and error behavior;
normal/failure/boundary AC; stop condition; control owner, distinct implementer
and independent reviewer; exact dependency readiness; verification and typed
return; and the machine-readable modify/create/delete/forbid boundary. For
each allowed new code or test/script file, it checks a distinct responsibility,
consumer, acceptance cell, reuse decision and dependency direction, plus the
ticket's bounded growth and evidence-output declarations. Placeholder text,
example/fenced/commented fields, missing references, conflicting revisions or
an Expected invented by the implementer are incomplete. On the existing
same-lifetime lane, `codex-native-same-lifetime-delegation.md` binds a reviewer
check before `collaboration.spawn_agent`; it is an instruction-level path, not
a qualified hard Host intercept. On the cross-lifetime lane,
`library/local_orchestration/dispatch_authority.py::admit_dispatch` is the
existing receipt-effect entrypoint, but does not yet perform this committed
ticket completeness readback. A hard pre-effect refusal claim for either lane
requires a separately qualified intercept at that lane's actual Host effect
boundary. Until it exists, reviewer checks and template validation cannot
close AC-10 or checklist 03; any new dispatch requiring this revision's hard
guarantee is blocked rather than reported as Host-enforced. The qualified
intercept must refuse before spawn, receipt issuance or dispatch, without an
external dispatcher or a new grant. The later Git-diff boundary remains a
separate check. A changed business Expected returns to existing requirement
change control.

**AC-11 — evidence-linked formal closure and structural review.** Formal
`APPROVED`/`DONE` and mainline closure require the existing Review/Router
admission path to resolve the exact candidate SHA, approved Expected,
Closure revision, required child tickets, dependencies, every blocking
Finding disposition, an independent reviewer identity/verdict and readable
AC-by-AC evidence bound to that candidate through the formal source readback.
The same path must resolve independently observed review evidence and the
test/type/build/smoke checks required by that approved ticket and Profile.
An inapplicable check, such as build or smoke for a docs-only ticket, may be
recorded `N/A` only with its reason; required evidence cannot be marked `N/A`.
A projection's `closure_candidate`, a green summary, a ticket
label or an unverified report cannot close work. An optional unfinished item
does not block required-work closure; an open required child, unresolved
blocking Finding, stale candidate/source, unreadable AC evidence or unverified
consumer does. No required work may be marked `DONE` from a projection or
incomplete evidence. A failed readback blocks only the affected ticket or
mainline closure, not another independent admitted ticket. Same-ticket
correction retains the original requirement, ticket, finite Closure revision,
budget and still-valid evidence, and rechecks affected consumers; an unrelated
hardening idea follows the existing `OUT_OF_SCOPE_HARDENING` route.

The independent reviewer compares the actual candidate diff with the ticket's
reuse decision and declared modified/created/deleted paths, separately for
product code and test/scripts. Growth or mixed responsibilities triggers a
documented structural review of the actual dependencies, consumers and test
seams. Mere line count neither approves nor requires a split. An undeclared
path fails the existing integration boundary; unjustified duplication or an
unresolved responsibility conflict is a ticket/review finding under the
existing Closure rules. A test-script move is not evidence that a product
responsibility was split. No second Gate or automatic semantic classifier is
implied.

### Required replay and entrypoints

1. At the current `library/workflow_router/mainline_projection.py` consumer
   and `library/workflow_router/router.py` / `private_router.py` decision path,
   replay one committed fictional A/B/C mainline: A has a precise effect wait;
   B is independent and live-admitted; C depends on A. B continues, C does
   not, and B completion leaves A and the required mainline open. Mutations
   that globally freeze B or admit B/C from caller-built metadata, an arbitrary
   caller ref, stale direct observation or unreadable official leaf must turn
   the named cells red and restore to green.
2. At the reviewer-controlled same-lifetime native delegation path, prove the
   reviewer checks the committed ticket before spawn, and report that result
   as instruction-level evidence only. At the separately qualified hard Host
   intercept for that lane, and at cross-lifetime
   `library/local_orchestration/dispatch_authority.py::admit_dispatch`, prove
   a complete approved ticket reaches only its existing dispatch route. Remove
   Expected, stop condition, distinct reviewer, dependency proof, or one new
   file's responsibility from the committed ticket and prove refusal occurs
   before spawn, receipt issuance or dispatch. Without a qualified intercept,
   record a capability gap; reviewer assertion or template-only green results
   cannot satisfy hard Host admission.
3. At `library/workflow_router/review_admission.py`, the existing guarded
   integration/Review route and the ticket-status projection consumer, prove
   exact-candidate positive closure, a reasoned docs-only `N/A`, and negative
   cases for an open required child, open blocking Finding, missing independent
   reviewer, stale or unreadable AC evidence, `N/A` on a required check and a
   product/test-script responsibility mismatch.
   A projection may display these states, but only
   the existing formal Review/Router route can authorize closure. Reviewer
   records the actual diff, reused modules, modified paths, impact/consumer
   scope and independent reverse-mutation results.

These are acceptance entrypoints, not preauthorized source-file changes.
Ticket 29's caller-built projection, Ticket 24's A-only wait, and Tickets
28/38's template checks remain valid local slices; none alone proves this
revision. Ticket 30 remains non-dispatchable until architecture preflight
binds the exact trusted source and per-ticket Host admission path. If existing
target-owned sources do not contain a complete mainline objective, owner,
handoff and dependency index, or the Host cannot read them at the effect
boundary, return a typed source/architecture gap through the existing Router.
The current workflow-governance `README.md` has a delivery objective and
ticket table, but no complete required/optional dependency graph or current
per-ticket handoff binding; it is not yet an admissible AC-9 source. The
current `admit_dispatch` accepts a caller-provided artifact and does not
perform AC-10's committed-ticket completeness readback; native same-lifetime
delegation has no qualified hard Host intercept. Neither behavior is
defensibly authorized as a completed Host/mainline capability by AC 1–8.
Do not synthesize that authority from metadata or expand Ticket 30 locally.

### Staged approval, build, verification and activation

1. **SPEC approval.** Finish this bounded correction, record its exact final
   commit/blob and independent review evidence, then obtain the project owner's
   exact approval of that reviewed revision. The 2026-10-18 limited drafting
   authority above does not make AC-9–11 effective or authorize a Host effect.
2. **Build.** Use the owner-approved revised SPEC as the bounded build
   acceptance source, and route implementation through the currently effective
   ticket schema, owner approval, role/worktree preflight and existing Router
   gates. Only a separately approved ticket can authorize source/test changes;
   this proposal does not dispatch Ticket 30 or issue a new grant by itself.
3. **Verification.** At exact built candidate SHA, independently review the
   AC-9–11 positive/negative replays and qualify the actual direct-remote,
   formal-source and Host effect intercepts for each lane claimed. Record
   readable evidence refs and failures. `LOCAL_INTEGRATED` is not remote
   `AUTHORITY_INTEGRATED`; any required push and direct remote SHA readback
   remain separate effects under the existing authority-line contract.
4. **Formal activation.** Only an explicit scoped owner decision, bound to the
   approved SPEC, reviewed built commit, qualified entrypoints, passing replay
   evidence and effective authority ref/SHA, enables AC-9–11 for that scope.
   Without a qualified Host intercept, no hard-gate claim or activation for
   that lane. Missing or later-invalid evidence suspends only its affected
   admission or closure; it does not revoke existing effective grants or
   freeze unrelated tickets with independently valid authority.

Existing approved SPEC AC 1–8, issued grants/receipts, active lanes and
completed-ticket evidence retain their original scope; this proposal neither
revokes nor silently upgrades them. After scoped activation, any new or
repeated dispatch in that scope must pass AC-9/10 against its exact current
approved ticket, and formal closure must pass AC-11. A legacy ticket lacking
required fields is amended under the original requirement and ticket identity,
with its approval and Closure revision preserved or explicitly revised as
required by existing change control. No second PRD, parallel mainline
authority, new ticket solely for this SPEC proposal, new framework or
automatic migration is authorized.
