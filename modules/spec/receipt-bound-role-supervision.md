# Receipt-bound Role Supervision Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` |
| Status | `DRAFT / OWNER_APPROVAL_REQUIRED` |
| Author / baseline | Architecture owner / `main` / `2701ed563f26e116db69e8e4fcb84024754c9498` |
| Context | `doc/context/receipt-bound-role-supervision/main.md` |
| Shared Context | `CONTEXT.md` sealed by `CHG-20260815-023` |
| PRD / change | `PRD-20260815-023` / `CHG-20260815-023` |
| Architecture decision | `ADR-20260815-012` |
| Implementation language | Python 3.11 with `mypy --strict`; Markdown and validated JSON are artifact formats, not additional runtimes |
| Delivery profile | `HIGH_ASSURANCE` for live role wake, task replacement and external-effect boundaries; pure reducers/schemas may be decomposed only after exact ticket admission |

## Problem and goal

The existing Router can validate a supplied implementation return but has no proved production
capability that subscribes to one implementation task and wakes its named reviewer. Repeated
thread reads or heartbeats waste model tokens. Interval Git polling wastes CPU and I/O. A host
handoff-operation status cannot stand in for the implementation task.

The goal is the least-total-cost supervision path that still produces stable, traceable work:

```text
exact Git ref event
-> committed handoff validation
-> receipt/task/worktree/branch/baseline/provenance gate
-> one-shot RoleWakePort
-> named reviewer diagnosis and Router decision
```

Correctness, authority and stable project delivery are hard gates. Among designs that pass those
gates, choose the lowest total token cost, then the lowest idle CPU and I/O cost. Rework tokens
count as cost.

## Out of scope

- No heartbeat implementation or implicit heartbeat approval.
- No scheduled automation, cron, watchdog, recurring model/thread/Git/filesystem polling or
  active-turn blocking model wait.
- No new network service, MCP service, database, paid Provider or model host.
- No automatic creation of an architecture owner, reviewer or implementation task without the
  existing receipt-bound gateway authority.
- No production push, release, signing, deployment, migration or Secret authority.
- No requirement that a successor install Johnny or preserve Johnny's workflow after removal.
- No implementation ticket, dispatch or production adapter effect before exact owner approval of
  this SPEC and normal reviewer ticket admission.

## Responsibility and dependency boundaries

```text
Pure Router
  consumes validated metadata events and selects one typed continuation

Local supervision composition
  GitRefEventAdapter + HandoffValidator + SupervisionLeasePort + RoleWakePort

Reviewer
  sole Agent orchestrator; performs diagnosis, continuation, ticket replan and review

Architecture owner
  owns this SPEC and wakes only for typed architecture triggers

Implementation owner
  writes only its one admitted ticket/worktree and emits committed handoff evidence

Target project
  owns README, handoff tree, manifest, SPEC/ticket/review/evidence and product source

Plugin
  removable control plane; never target runtime, CI, hook, import or deployment dependency
```

Nondeterministic Git, clock, host-task and wake operations stay behind injected ports. The pure
Router and policy reducers receive only validated strong types. A notification is evidence to
re-read an exact authoritative source; it is never authority itself.

## Acceptance criteria

### AC-01 — Complete wake-chain preflight

Before implementation dispatch, capability readback must prove one exact composition:

```text
GitRefEventAdapter -> HandoffValidator -> RoleWakePort -> named reviewer
SupervisionLeasePort -> RoleWakePort -> named reviewer
```

The proof binds project, ticket, unconsumed dispatch receipt, reviewer, implementation owner,
task, workspace/worktree, branch, baseline, correlation, event source revision, monotonic
deadline capability and wake-port
revision. Missing or mismatched proof returns `HALT / ROLE_WAKE_CHAIN_UNAVAILABLE` before task,
worktree, source or host effect. A one-shot thread read, handoff-operation status, fake or
background watcher without a wake port is insufficient.

### AC-02 — Exact event source and registration race

The adapter observes only Git metadata required by the bound branch/ref. It may register native
notifications on the exact ref and necessary Git metadata parents, including packed-ref
replacement, but it must not scan a repository or working tree. Pre-registration and immediate
post-registration ref snapshots close the completion race. Duplicate notifications, ref writes
with the same value and replay deliver no second event or role wake.

### AC-03 — Committed terminal handoff

Every ref change is only a hint. Validation reads the leaf from the observed commit with:

```text
git show <handoff-commit>:<exact-handoff-leaf>
```

The handoff must validate schema revision, content digest, project, SPEC/ticket revisions,
receipt, source role/task, target role, workspace/worktree, branch, baseline ancestry, result
commit ancestry, correlation, evidence references and finite terminal meaning. A working-tree
file, chat claim, screenshot, source-only commit or unrelated handoff cannot wake a role.

`COMPLETED`, `BLOCKED` and `CHANGE_DETECTED` map to the existing `ImplementationReturn` contract.
`ACTION_COMPLETED` and `REVIEW_HANDOFF` are event kinds, not new implementation outcomes.

### AC-04 — Reserved-path fault handling

An ordinary source commit is silent. A commit that changes or claims the reserved handoff path
but fails schema, digest, receipt, task, branch, ancestry or terminal validation produces exactly
one trusted `SUPERVISION_FAULT / INVALID_HANDOFF` for the named reviewer and then halts. The
invalid content itself never becomes trusted payload. Replays and unrelated branches are silent.

### AC-05 — No heartbeat or periodic fallback

After registration, idle supervision performs zero model calls, Router turns, thread reads, Git
reads, filesystem scans and recurring timer callbacks. The following phrases do not authorize a
heartbeat: ticket approval, dispatch confirmation, `AUTO_CONTINUE`, “monitor”, “continue” or
“do not stop”. Heartbeat requires separate, explicit, scope-bound user approval and is outside
this SPEC. Capability loss fails closed; it does not select `WAIT_FOR_HUMAN` or a periodic
fallback.

### AC-06 — Execution-start evidence and deadline origin

No supervision time is counted between handoff preparation and dispatch. A lease begins only
after host readback proves all of the following in one validated `IMPLEMENTATION_EXECUTION_STARTED`
event:

- the implementation owner received the exact ticket;
- task/workspace/worktree/branch/baseline bindings match;
- the task is active and the ticket is executable;
- the execution receipt has not been replayed or replaced.

Each active binding owns at most one one-shot native deadline. A one-shot deadline is not a
heartbeat: it emits no intermediate wake and fires once at the declared boundary.

### AC-07 — Reviewer wake and diagnosis

A validated terminal handoff, supervision deadline or trusted handoff fault may wake only the
named reviewer once. The reviewer first performs read-only diagnosis of task state, exact
worktree/branch/HEAD, baseline ancestry, commits/handoff and any running command/tool. It may not
expand ticket scope, mutate the implementation worktree, merge, push, deploy or wake the
architecture owner outside the finite routes below.

### AC-08 — Luna xhigh total ceiling and ticket repair

The default implementation owner mapping is Luna xhigh. Its total execution ceiling is thirty
minutes from `IMPLEMENTATION_EXECUTION_STARTED`. Commits, task stop/restart, reviewer diagnosis
and correction do not reset the clock. Luna receives no automatic `CONTINUE_IMPLEMENTATION`.

If Luna is stopped incomplete or reaches thirty minutes incomplete, classify
`TICKET_DEFECT / COMPLEXITY_EXCEEDED`. The reviewer first splits the approved SPEC closure along
an independently observable behavior/state, effect, ownership/Composition Root or verification
boundary. It never splits by file, line count or horizontal frontend/backend/test layers. If a
legal split exists, the smaller new tickets retain Luna xhigh. If no legal split exists, replace
the current execution once with Terra high under AC-12. No ticket meaning is invented.

### AC-09 — Terra-or-higher inactivity lease

Terra-or-higher uses a two-hour inactivity lease. A validated exact-branch ref advance resets the
deadline inside the adapter without a model wake. When the deadline fires, reviewer diagnosis
may send one `CONTINUE_IMPLEMENTATION` to the same ticket/task/receipt/worktree/branch only when
the task is stopped incomplete and the approved closure remains unchanged. This resets one final
two-hour inactivity lease.

A second incomplete stop/expiry returns `MODEL_CAPABILITY_INSUFFICIENT`; no further automatic
continuation is allowed. The Router may then wake the architecture owner under AC-10.

### AC-10 — Architecture-owner wake boundary

Ordinary `BLOCKED`, time expiry and implementation defects do not directly wake architecture.
Only the Router's typed conditions may do so:

- `SPEC_AMBIGUOUS` or `SPEC_CONTRADICTORY`;
- `PUBLIC_CONTRACT_UNDEFINED` or unprovable AC;
- `ARCHITECTURE_CONFLICT` or cross-ticket design conflict;
- `REQUIREMENT_CHANGED` or a new external/privileged boundary;
- a newly applicable `HIGH_ASSURANCE` trigger;
- `MODEL_CAPABILITY_INSUFFICIENT` after the finite convergence policy is exhausted.

If a required architecture wake capability is unavailable, return
`HALT / ARCHITECTURE_WAKE_CAPABILITY_UNAVAILABLE`. Heartbeat is not a fallback.

### AC-11 — Write-owning execution identity

The authority unit is the write-owning execution session/task. Opening or restarting a shell,
IDE, command or subprocess under the same admitted task/worktree does not change the binding.
Changing the Agent task, effective writer, host or machine does.

`ExecutionBindingLifecycle` is:

```text
ACTIVE -> REPLACEMENT_PENDING -> REPLACED -> CLOSED
```

Old and new bindings never write concurrently. If the old task is available, it first commits a
bounded checkpoint handoff. The gateway then revokes the old write lease/subscription and host
readback proves it cannot write. The new binding validates project/ticket/branch/checkpoint,
receives a new task, correlation and execution receipt, and rejects stale old events. If the old
task is unavailable, only its last committed validated state is recoverable. A new machine uses
a fresh clean checkout/worktree; an old machine path is not provenance.

### AC-12 — Model rebind and one-ticket override

If the host proves an in-place model rebind, the same task may receive a new binding revision.
Otherwise controlled task replacement applies. The Luna-to-Terra-high escalation is limited to
the current ticket execution. On terminal handoff the override expires. The next new ticket uses
the Profile's Luna xhigh default; a completed Terra task is not artificially “downgraded”.

### AC-13 — Target-owned handoff tree and provenance

Each target project uses its existing equivalent path or this default:

```text
doc/handoffs/
  README.md
  index.json
  <year>/
    README.md
    index.json
    <feature>/
      README.md
      index.json
      <ticket-id>/
        README.md
        index.json
        <handoff-id>.json
```

Every index contains only direct-child ID, artifact kind, revision, digest, lifecycle and exact
child-index/leaf reference. It never copies leaf bodies, descendant inventories, progress prose
or chat history. A correction creates a new leaf with `previous_handoff_ref` and optional
`supersedes_ref`; sealed leaves are never edited in place.

The provenance chain is:

```text
project identity -> SPEC revision -> ticket revision -> dispatch receipt
-> task/role/worktree binding -> implementation commit -> handoff leaf commit
-> wake event -> review commit -> integration commit
```

Git SHA proves bytes and ancestry, not Agent identity. Identity comes from receipt/gateway/task/
workspace readback and correlation. Missing, cyclic, duplicate-parent, stale-revision or digest-
mismatched edges return `HALT / HANDOFF_PROVENANCE_INVALID`.

### AC-14 — Plugin-neutral root manifest and README

`doc/handoffs/index.json` is a plugin-neutral, machine-readable root manifest. It records project
and protocol identity, schema/compatibility revision, direct-child partitions, exact active-leaf
references/digests, minimum adoption capabilities, last observed control-plane lifecycle and the
last known non-replayable receipt reference when present. The observed lifecycle is historical
metadata, not proof that a plugin remains installed and not authority over a successor.

The project root `README.md` provides a concise human operation entry point covering normal
handoff, shell versus task replacement, model escalation, team ownership, deployment separation,
plugin removal and optional re-adoption. The approved SPEC and active Router remain normative
only while Johnny is voluntarily in use.

### AC-15 — Unconditional plugin removal

The user may remove Johnny before any checkpoint, push, readback, effect settlement or successor
adoption. Uninstall cannot be blocked by Router state and must not add, modify or remove target
source, configuration, CI, data or formal artifacts. After removal:

- the successor may use any tools and workflow;
- Johnny's last manifest and receipts are informational historical evidence only;
- Johnny does not guarantee preservation of uncommitted work or completion/cancellation of an
  in-flight external effect;
- no Johnny rule may claim to govern the successor unless the successor deliberately adopts it.

### AC-16 — Optional re-adoption

A successor who chooses Johnny starts a new takeover from repository facts and committed
artifacts. It creates new control-plane identity, live descriptors, task/workspace bindings,
correlations and receipts. Historical receipts cannot authorize a new task or external effect.
The successor may instead ignore or archive the historical Johnny artifacts under its own
authorized project process.

### AC-17 — Engineering-team concurrency

While Johnny is attached, one ticket/branch/worktree has one active writer. Reviewer,
architecture and audit roles remain read-only against implementation worktrees. Parallel team
work requires disjoint tickets, branches, worktrees and observable acceptance closures. A human
or Agent ownership transfer uses AC-11; no shared writable task is inferred from repository
membership or chat instructions.

### AC-18 — Deployment and external effects

Development task/receipt authority never authorizes push, merge, release, signing, migration or
deployment. Such work requires a separate target SPEC/ticket and explicit scope-bound effect
authority binding exact owner, action, target, environment, receipt, baseline/artifact digest and
correlation, followed by exact result readback. Deployment runners may differ from development
terminals; they bind the accepted commit/artifact, not a developer's path. Plugin removal does
not modify runtime, CI or deployed artifacts and does not promise to settle an effect already in
flight.

### AC-19 — Cost and resource acceptance

The production adapter registers at most one observation composition per active execution
binding, never per shell. Implementations may multiplex native watchers while retaining exact
binding isolation. During a deterministic ten-minute quiet qualification:

- model calls, Router turns, thread reads, Git reads, filesystem scans and recurring timer
  callbacks after arming are all zero;
- no role is awakened;
- process CPU-time growth attributable to the adapter is at most one second;
- no repository-wide handle or cross-ticket event is registered.

Structural zero-call evidence proves the behavior but not a percentage token saving. Any saved-
token claim requires matched provider-reported usage under the existing telemetry policy.

## Strongly typed contracts

The following is contract notation, not an alternative implementation language. Python
implementation uses frozen/validated equivalents with no `Any` and passes `mypy --strict`.

```text
enum GitObservationMode { NATIVE_REF_EVENT, UNAVAILABLE }
enum WakeCapabilityState { PROVEN, UNAVAILABLE }
enum ImplementationTerminalKind { COMPLETED, BLOCKED, CHANGE_DETECTED }
enum SupervisionEventKind {
  ACTION_COMPLETED, REVIEW_HANDOFF, SUPERVISION_DEADLINE, SUPERVISION_FAULT
}
enum SupervisionFaultKind { INVALID_HANDOFF, WAKE_CHAIN_LOST, STALE_BINDING }
enum SupervisionClass { LUNA_XHIGH_DEFAULT, TERRA_OR_HIGHER }
enum LeaseKind { TOTAL_EXECUTION, INACTIVITY }
enum ExecutionBindingLifecycle { ACTIVE, REPLACEMENT_PENDING, REPLACED, CLOSED }
enum ArtifactLifecycle { ACTIVE, CLOSED, SUPERSEDED, ARCHIVED }
enum ObservedControlPlaneState { ATTACHED, DETACHING, DETACHED, ADOPTING }

struct RoleWakeCapabilityProof {
  ProjectId project_id;
  ReviewerRef reviewer_ref;
  CapabilityRevision wake_port_revision;
  WakeCapabilityState state;
  EvidenceRefs evidence_refs;
}

struct GitEventRegistration {
  EventSourceRef event_source_ref;
  SubscriptionId subscription_id;
  ProjectId project_id;
  TicketRef ticket_ref;
  ReceiptRef dispatch_receipt_ref;
  TaskRef implementation_task_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId baseline_commit;
  CorrelationId correlation_id;
  GitObservationMode mode;
  RoleWakeCapabilityProof wake_capability;
}

struct ExecutionStartedEvidence {
  ExecutionReceiptRef execution_receipt_ref;
  TaskRef task_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId baseline_commit;
  MonotonicInstant started_at;
  EvidenceRefs host_readback_refs;
}

struct SupervisionLease {
  LeaseId lease_id;
  ExecutionReceiptRef execution_receipt_ref;
  SupervisionClass supervision_class;
  LeaseKind lease_kind;
  MonotonicInstant origin;
  Duration duration;
  ResetCount reset_count;
  ContinueCount continue_count;
}

struct HandoffLeaf {
  HandoffId handoff_id;
  SchemaRevision schema_revision;
  ProjectId project_id;
  SpecRef spec_ref;
  SpecRevision spec_revision;
  TicketRef ticket_ref;
  TicketRevision ticket_revision;
  ReceiptRef receipt_ref;
  RoleRef source_role_ref;
  TaskRef source_task_ref;
  RoleRef target_role_ref;
  std::optional<TaskRef> target_task_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId baseline_commit;
  CommitId result_commit;
  ImplementationTerminalKind terminal_kind;
  std::optional<HandoffRef> previous_handoff_ref;
  std::optional<HandoffRef> supersedes_ref;
  EvidenceRefs evidence_refs;
  CorrelationId correlation_id;
  ContentDigest content_digest;
}

struct HandoffChildRef {
  ArtifactId child_id;
  ArtifactKind child_kind;
  ArtifactRevision revision;
  ContentDigest content_digest;
  ArtifactLifecycle lifecycle;
  ArtifactRef target_ref;
}

struct HandoffRootManifest {
  ProjectId project_id;
  ProtocolId handoff_protocol_id;
  SchemaRevision schema_revision;
  CompatibilityRevision minimum_compatible_revision;
  ArtifactRevision manifest_revision;
  ChildRefs direct_child_refs;
  CapabilityRefs minimum_adoption_capabilities;
  ObservedControlPlaneState last_observed_control_plane_state;
  EvidenceRevision last_observation_revision;
  std::optional<ReceiptRef> last_non_replayable_receipt_ref;
}

struct ExecutionReplacement {
  ReplacementId replacement_id;
  ExecutionBindingRef old_binding_ref;
  ExecutionBindingLifecycle old_lifecycle;
  std::optional<HandoffRef> checkpoint_ref;
  EvidenceRefs revocation_readback_refs;
  ExecutionBindingRef new_binding_ref;
  ExecutionReceiptRef new_execution_receipt_ref;
  CorrelationId new_correlation_id;
}
```

Opaque refs and IDs must be validated named types. Dynamic JSON, Git output and host payloads are
validated and normalized at the adapter boundary before entering these contracts. Durable
Router state, telemetry and errors never contain raw filesystem paths, URIs, source, prompts,
Secrets, PII or untrusted handoff bodies.

## TDD and independent verification closure

1. Public-constructor/schema round trips cover every enum, optional field, digest and ID wrapper;
   null, empty, whitespace, extra-field, coercion, wrong finite value and bypass construction
   fail closed. `mypy --strict` is mandatory.
2. Capability tests reject missing `event_source_ref`, `subscription_id`, exact branch/task/
   receipt binding or wake-port proof before any host effect. Active-turn wait and handoff-
   operation status never qualify.
3. Native-event tests use deterministic fakes and disposable real Git repositories for loose
   refs, atomic ref replacement and packed refs. Pre/post registration races, duplicate native
   signals, unchanged SHA, cross-branch commits and cancellation deliver at most one event.
4. Handoff tests validate every leaf field independently through `git show`; working-tree-only,
   wrong receipt/task/worktree/branch/baseline, non-descendant result, digest mismatch, invalid
   terminal meaning, source-only commit and replay never wake a role.
5. Reserved-path tests prove an invalid claimed handoff creates one sanitized fault and halt,
   while an ordinary source commit remains silent. Reverse mutation of every gate must turn red.
6. Source/AST composition gates reject heartbeat, recurring timer loops, cron/scheduler/watchdog,
   recurring thread/Git/filesystem reads, repository scans and active-turn wait. Each reverse
   mutation has one dedicated red test.
7. Fake monotonic-clock tests prove no lease before execution-start readback, Luna's exact
   thirty-minute non-resettable ceiling, Terra's exact two-hour ref-activity resets, one Terra
   continuation and second-stop architecture routing.
8. Luna ticket-repair tests cover every legal split dimension, reject horizontal/file/line
   splits and prove Terra-high replacement occurs only when no independent closure exists.
9. Replacement tests prove old/new non-overlap, revocation readback, fresh receipt/correlation,
   stale-event rejection, same-shell no-op, new-machine clean worktree and last-commit-only crash
   recovery.
10. Artifact-tree tests validate direct-child-only indexes, exact path resolution, digest and
    lifecycle edges, immutable correction leaves, plugin-neutral manifest parsing and absence of
    raw prompts/Secrets/PII. Cycles, duplicate parents and stale digests halt.
11. Detach tests prove uninstall writes nothing to a target project and has no checkpoint,
    push/readback/effect-settlement precondition. Re-adoption tests reject every historical live
    receipt and issue a fresh takeover identity.
12. Documentation tests verify the root README decision table, exact SPEC/Router links and
    explicit statements for no heartbeat, deployment separation and successor freedom.
13. Quiet-resource qualification proves AC-19 with counters and process CPU time. Provider usage
    comparisons are reported separately and never inferred from structural tests.
14. Live wake, task replacement and effect-boundary review use `HIGH_ASSURANCE`; fake success,
    lower model choice or source inspection never upgrades an unproved host capability.

## Reviewer decomposition constraints

After exact owner approval, the reviewer may compile this SPEC into the smallest vertical
closures. A safe dependency order is:

1. strong typed handoff/index/manifest contracts and pure validators;
2. pure supervision lease and model-policy reducer;
3. exact Git ref event adapter plus handoff readback/deduplication;
4. proved `RoleWakePort` composition and capability preflight;
5. controlled execution/model replacement;
6. target-owned tree/bootstrap and root README integration;
7. integrated high-assurance acceptance and resource qualification.

These are decomposition boundaries, not tickets or dispatch authority. The reviewer must split
further when one candidate contains more than one observable closure or effect owner, and must
route any missing meaning back to architecture.

## Risks, compatibility, rollback and deployment prerequisites

- Native filesystem/Git notification APIs are hints and may coalesce events. Correctness comes
  from authoritative post-event Git readback and idempotent validation.
- A host without a proved role-wake port cannot dispatch under this feature. It may still use a
  separately authorized manual workflow, but cannot claim this automatic supervision mode.
- Packed refs, branch deletion, history rewrite and force updates require explicit negative
  coverage; unexpected non-descendant history halts.
- One-shot deadlines consume negligible idle CPU but require monotonic-clock and cancellation
  correctness. They must never be implemented as repeating timers.
- Plugin removal intentionally prioritizes user control over clean automation shutdown. The root
  README must state that uncommitted work and in-flight effects may need independent recovery.
- Rollback closes exact subscriptions/deadlines, disables the wake composition and leaves target
  source, Git history and committed handoff artifacts intact.
- Deployment implementation is not authorized here. Any future deployment ticket independently
  applies the security effect boundary and exact environment/artifact readback.

## Convergence and lineage

- Sealed shared Context: `CONTEXT.md`, revision authorized by `CHG-20260815-023`.
- Feature Context: `doc/context/receipt-bound-role-supervision/main.md`.
- Active requirement leaf:
  `doc/requirements/active/2026/workflow-governance/REQ-20260815-023.md`.
- ADR: `doc/adr/ADR-20260815-012-receipt-bound-event-driven-completion-supervision.md`.
- XSS classification: `N/A`; this feature has no Browser/WebView/HTML/DOM/JavaScript renderer
  flow. A future UI or untrusted renderer integration re-runs the XSS gate.
- New external effects: role wake and task replacement are privileged Agent-control effects and
  therefore `HIGH_ASSURANCE`. Push, release and deployment remain out of scope.
- Open architecture questions: none after owner Grill decisions D11, D12 and D8a through D8e as
  corrected on `2026-08-15`.
- Current Router return: `OWNER_APPROVAL_REQUIRED`; no ticket planning or dispatch yet.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `2701ed563f26e116db69e8e4fcb84024754c9498` | Independent draft after completed Grill; replaces the unapproved attempt to revise the collaboration-audit SPEC. |

## Approval record

- Decision maker: project owner.
- Architecture/Grill decisions: confirmed through `2026-08-15 (Asia/Taipei)`.
- Exact SPEC revision: `OWNER_APPROVAL_REQUIRED`.
- Approval effect when granted: authorizes reviewer decomposition and ticket drafting only. It
  does not authorize dispatch, implementation, heartbeat, push, release or deployment.
