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


## Revision 04 — gates-first control plane (owner-approved 2026-11-03)

Source: `PRD-20261103-043` / `CHG-20261103-043`. This revision changes how transitions are decided; it does not change the role boundary, the P0 list or the review conclusion vocabulary.

### R4-1 State lives in files

- A ticket leaf, its receipt and the merge queue (`MERGE-QUEUE.json`) are the only state. Nothing an agent holds in memory is authoritative. A pending dispatch is the ticket's state row plus the digest of its dispatch file: the dispatch file is the machine-form dispatch that dispatch lint admits (R4-2), kept in the target project at `doc/handoffs/<year>/governance/dispatch/<ticket>-<n>.yaml` (path parameterised) so any host can recompute its digest, and while the dispatch is pending the State row carries `dispatch=sha256:<hex>` of it (the template field arrives with the wave-2 state-file templates ticket); the merge queue holds integration candidates only. The live `PendingDispatchDescriptor` of the cross-lifetime bridge is retained as a transitional path until wave 3, not as the default; the single-consume and anti-replay guarantees it gave at integration are carried by the queue (R4-7). Any session, on any host, resumes from these files.
- `ACTION_COMPLETED`, `ImplementationReturn`, `ImplementationHandoff`, `WAIT_FOR_HUMAN` and `HALT` remain the vocabulary of receipts and return records. They are written into the receipt by the agent that finished the action; no Router process has to be re-entered for them to count.

### R4-2 Transitions are decided by scripts

| Gate | Decides | Exit |
| --- | --- | --- |
| dispatch lint | a dispatch is machine-form (fields, commands, assertions) | 0 / 1 / 3 |
| preflight | every named test tool starts and serves what the page or module needs, before any product edit | 0 / 2 / 3 |
| contract gate | every requirement id has a spec, every spec cites an existing source at its recorded digest, no spec binds a retired requirement, no literal expected value, every contract has a named mutation | 0 / 1 / 3 |
| evidence gate | every cell carries candidate, tool digest and capture; stale tool digests and missing captures fail | 0 / 1 / 2 / 3 |
| coverage map | every retired assertion is carried, dropped with a reason, or escalated | 0 / 1 / 3 |
| integration | the candidate has an independent review record with verdict `APPROVED`, the queue entry fast-forwards onto the current tip, affected specs rerun green, remote sha equals the sha checked, then push | 0 / 1 / 2 / 3 |

Exit code meaning is fixed across all gates: 0 pass, 1 contract red, 2 tool fault, 3 usage error. A red is never reported as a tool fault and a tool fault is never reported as a red.

### R4-3 Bounded tool repair and escalation filter

- A seat that meets a tool fault repairs the tool inside a declared allowlist, in its own commit, without touching assertions, expected values, product code or any gate. A repair guard checks the diff.
- A seat escalates to the owner only for the P0 list, a genuine requirement conflict (`REQUIREMENT_CHANGED`) or a forbidden-versus-required clash. Tool faults, verifiable facts and receipt format never reach the owner.

### R4-4 Integration is a script, not a role

The reviewer alone owns the review conclusion. Integration is executed by the versioned integration script from the merge queue by whoever holds budget; the submitter is responsible for a fast-forwardable candidate. A single fixed integrator is not required and must not be assumed.

### R4-5 Stages by intake mode

The eleven-stage sequence applies to `GREENFIELD`. `TAKEOVER` and `DELTA` enter from a requirement snapshot (one row per requirement item with a stable id, source reference and digest) directly into tickets; Wayfinder contributes only its bounded information-gap protocol.

### R4-6 Tests in four layers; CI holds invariants only

- harness (no assertions) / fixtures / contract sources and ledgers (expected values with provenance) / one-contract-per-file specs that read from the layers above.
- CI runs two classes, positively pinned: hard business rules and security locks. Removing or weakening one is a red. Requirement-driven regression runs inside the ticket loop, not in CI.
- A contract-preserving change (copy, asset, style parameter with no behaviour, layout or acceptance change) takes the fast lane: existing contract, implement, existing specs, integrate. Touching any expected value leaves the fast lane.

### R4-7 Wave-2 schemas (binding for the implementation tickets)

- Merge-queue file: `doc/handoffs/<year>/governance/MERGE-QUEUE.json` in the target project by default; the path is a parameter of the integration script. Entry: `ticket`, `candidate` (full sha), `parent` (tip sha checked), `review` (repository-relative path of the review record), `review_candidate` (the sha that review verified; must equal `candidate`), `reviewer`, `submitter` (must differ from `reviewer`), `state` (`QUEUED` | `LANDED` | `LANDED_CI_RED` | `CLEARED` | `BOUNCED`), `landed_sha`, `reason` (bounce codes only), `clears` (the keys of every `LANDED_CI_RED` entry this entry fixes, written `<ticket>@<candidate>` and comma-separated, else empty). The integration script reads `review_candidate` and `reviewer` from the review record at `review`, not from the queue row; the row carries copies, and a copy that differs from the record bounces the entry with reason `REVIEW_MISMATCH`. Key = (`ticket`, `candidate`); a key already in a terminal state (`LANDED`, `LANDED_CI_RED`, `CLEARED`, `BOUNCED`) is refused (anti-replay). Landing = compare-and-swap: the queue file commit read at admission and the remote tip sha read at admission must both still hold at push time, otherwise `BOUNCED` with reason `TIP_MOVED` or `QUEUE_MOVED` (single consume). Affected specs = every spec whose file, or whose page entry in `pages.json`, names a path changed by the candidate, plus the CI invariant classes; `pages.json` is the target project's page registry when one exists (one entry per page, listing the paths that page owns), and without it affected specs are derived from file paths alone; they rerun on the fast-forwarded tree before push. After push the CI result for the landed sha is read back: green marks `LANDED`; red marks `LANDED_CI_RED`, which requires a follow-up ticket and blocks further landings until cleared. Clearing: while one or more blocks hold, the only entries the script admits are those whose `clears` lists every currently red key; when that entry lands with a green CI result for its landed sha the block lifts and each cleared entry moves to `CLEARED` (terminal, kept as a record). Only a green CI readback clears the block; no manual override exists. Lock: one lock row with run id and start time; a lock older than 30 minutes may be reclaimed by the next run regardless of its holder, because liveness cannot be tested across hosts; the reclaiming run records `LOCK_RECLAIMED` with the stale run id, and a holder that was in fact still running fails its own compare-and-swap at push time and bounces with `QUEUE_MOVED`.
- Review record block: the integration script reads the last fenced block tagged `review-verdict` in the file at `review` whose `candidate` equals the queue `candidate`; fields `candidate` (full sha), `verdict`, `reviewer`, `reviewed_at`. `reviewer` and `submitter` share one format, `seat:<profile>/<run-id>`, where `run-id` is the identifier the host assigned to the run; the script checks the format, that the two differ, and that the `submitter` identity appears as `reviewer` in no `review-verdict` block of the candidate's record; the entry is written after the record exists and copies `review_candidate` and `reviewer` from it; proving that the host issued an identity is the wave-2 review-run receipt, not this gate. No such block for the candidate, or a verdict other than `APPROVED`, bounces with `REVIEW_MISMATCH`. Records that predate this rule gain the block when the wave-2 script lands.
- Receipt cell: `cell`, `candidate`, `tool_digest` (one line per tool file, `path=sha256` of the blob at `candidate`), `capture` (repository-relative path), `exit`. A cell without all five fields is `NOT_RUN`.
- Requirement snapshot: a JSON file per source and version at `doc/requirements/snapshots/<source>/<date>-v<n>.json` in the target project (path parameterised), holding `source`, `taken_at`, `source_sha256` and `rows`. Row: `requirement_id`, `page_id`, `title`, `type`, `source_ref` (URL or path), `source_sha256`, `status`, `version`. A new snapshot never overwrites an earlier version; later edits become the next version.
- Contract gate codes: `NO_SPEC_FOR_REQUIREMENT`, `SOURCE_MISSING`, `SOURCE_DIGEST_MISMATCH`, `RETIRED_REQUIREMENT_BOUND`, `LITERAL_EXPECTED`, `NO_MUTATION`. Any code is exit 1.
- Post-push readback: the integration script records the CI run result for the landed sha and, where a deploy target exists, the served fingerprint of at least one changed file; both go into the integration receipt before the entry is marked `LANDED`.
- Exit mapping is the single table in R4-2; a gate that cannot start (missing interpreter, unreadable input directory) exits 2, never 1.

### Revision Signatures (Revision 04)

| Date | AI / baseline SHA | Summary |
| --- | --- | --- |
| 2026-11-03 | Control plane / `a1cb6c1` | Revision 04 drafted under the owner takeover instruction of 2026-11-03. |
| 2026-11-03 | Control plane / `d581ebc` | R4-7 added; the live dispatch descriptor kept as a transitional path with the queue carrying single-consume and anti-replay. Decision taken by the control plane under the takeover authority; owner confirmation requested in the next owner reply. |
| 2026-11-03 | Project owner / `3896c3c` | Confirmed the R4-1 / R4-7 decision: the live dispatch descriptor stays a transitional path until wave 3; the default dispatch is the ticket state row plus the dispatch-file digest; single-consume and anti-replay are carried by the merge queue at integration; the queue script is the first wave-2 ticket. |
