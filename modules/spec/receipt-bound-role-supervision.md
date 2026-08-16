# Receipt-bound Role Supervision Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` |
| Status | `REVISION_01_APPROVED / REVISION_02_APPROVED / REVISION_03_APPROVED / REVISION_04_APPROVED / REVISION_05_APPROVED / REVISION_06_APPROVED / REVISION_07_APPROVED / ATTEMPT_003_PROVED_NO_EFFECT_CORRECTION / SENIOR_CORRECTION_TICKETING_AUTHORIZED` |
| Author / baseline | Architecture owner / `main` / `6569cd41bbf3ecbc04108da4150c30267951dda5` |
| Context | `doc/context/receipt-bound-role-supervision/main.md` |
| Shared Context | `CONTEXT.md` sealed by `CHG-20260816-025`; original role-supervision facts from `CHG-20260815-023` |
| PRD / change | `PRD-20260815-023`, `PRD-20260816-025`, `PRD-20260816-026`, `PRD-20260816-027`, `PRD-20260816-028`, `PRD-20260816-029`, `PRD-20260816-030`, `PRD-20260817-031` / `CHG-20260815-023`, `CHG-20260816-025`, `CHG-20260816-026`, `CHG-20260816-027`, `CHG-20260816-028`, `CHG-20260816-029`, `CHG-20260816-030`, `CHG-20260817-031` |
| Architecture decision | `ADR-20260815-012`, `ADR-20260816-014`, `ADR-20260816-015`, `ADR-20260816-016`, `ADR-20260816-017`, `ADR-20260817-018` |
| Implementation language | Python 3.11 with `mypy --strict`; Markdown and validated JSON are artifact formats, not additional runtimes |
| Delivery profile | `HIGH_ASSURANCE` for live role wake, task replacement and external-effect boundaries; pure reducers/schemas may be decomposed only after exact ticket admission |

## Problem and goal

The existing Router can validate a supplied implementation return but has no proved production
capability that subscribes to one implementation task and wakes its named reviewer. Repeated
thread reads or heartbeats waste model tokens. Interval Git polling wastes CPU and I/O. A host
handoff-operation status cannot stand in for the implementation task.

The reviewer role's user-facing project name is **Senior**. The goal is the least-total-cost
supervision path that still produces stable, traceable work:

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

Revision 03 closes the earlier gap between pure Router admission and a live host dispatch. It
adds durable approved-artifact and `TicketReceipt` state, one-shot dispatch claims, exact
task/workspace admission and finite host-effect settlement. It does not weaken the independent
Git-event/wake-chain gate or pretend that presence of a Codex thread tool is a subscription.

Revision 04 breaks the self-hosting cycle without weakening normal dispatch. It creates one
project-specific, finite bootstrap route for R03-01 through R03-03. The route uses committed
grant/attempt/result evidence, user relay only as a wake hint and an explicit positive activation
gate. It permanently disappears after the complete live capability is proven.

Revision 05 is the owner-approved ticket-defect recovery. It seals the failed first R03-01 attempt,
replaces that umbrella closure with contracts, a real durable transaction substrate, registry
behavior and receipt CAS behavior, fixes the strict-type command identity, and moves
write-producing review into reviewer-owned disposable storage. Its exact bounded detail is
indexed at
[`receipt-bound-role-supervision/r05-r03-ticket-defect-recovery.md`](receipt-bound-role-supervision/r05-r03-ticket-defect-recovery.md).
It authorizes Senior decomposition/ticket drafting only and creates no implementation authority.

The first owner-approved R03-00 policy bridge is a separate, narrower authority leaf at
[`receipt-bound-role-supervision/r05-r03-00-policy-bridge.md`](receipt-bound-role-supervision/r05-r03-00-policy-bridge.md).
Its route and grant were consumed; they are historical evidence and cannot be retried. Revision 06
corrects the immutable-admission and stale-baseline defects at
[`receipt-bound-role-supervision/r06-r03-00-immutable-admission.md`](receipt-bound-role-supervision/r06-r03-00-immutable-admission.md),
with successor bridge
[`BPB-R03-00-20260816-002`](receipt-bound-role-supervision/r06-r03-00-policy-bridge-02.md).
BPB-002 permits only independent Senior review of the exact bridge commit. The later sequence must
create a new ticket source and registry before any separately owner-approved grant; R03-01A
through R03-01D remain blocked.

Revision 07 closes the host identity and effect-boundary defect exposed after that sequence
created BDA-003. Senior explicitly sent the calling environment host, so the tool rejected the
call before resolving an `AppServerManager`; target task readback proves no delivery. The bounded
contract and exact one-operation recovery are at
[`receipt-bound-role-supervision/r07-host-bound-bootstrap-recovery.md`](receipt-bound-role-supervision/r07-host-bound-bootstrap-recovery.md).
It authorizes Senior correction ticketing and independent review, not Architecture dispatch.

## Out of scope

- No heartbeat implementation or implicit heartbeat approval.
- No scheduled automation, cron, watchdog, recurring model/thread/Git/filesystem polling or
  active-turn blocking model wait.
- No new network service, MCP service, database, paid Provider or model host.
- No host capability claim inferred from tool inventory, prompt text, profile/config bytes,
  screenshot or a process-local fake.
- No generic bootstrap fallback, implicit exception after `CAPABILITY_UNAVAILABLE`, bootstrap
  grant for another project/ticket or use after normal activation.
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

Live dispatch composition
  durable artifact registry + TicketReceiptStorePort + DispatchClaimStorePort
  + TaskWorkspaceAdmissionPort + ReviewerDispatchGatewayPort

Self-host bootstrap governance
  project-owner policy + Senior-owned immutable grant/attempt/result/review/integration leaves
  + user return-available relay + exact normal-activation proof

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

The live dispatch composition is not the host. It validates and persists metadata around one
injected Senior-only host effect. Its first envelope remains identifiers only; the adapter
resolves the committed ticket and handoff from the exact registry revision.

## Acceptance criteria

### AC-01 — Complete wake-chain preflight

Before implementation dispatch, capability readback must prove one exact composition:

```text
GitRefEventAdapter -> HandoffValidator -> RoleWakePort -> named reviewer
SupervisionLeasePort -> RoleWakePort -> named reviewer
```

The proof binds project, ticket, the Router-admitted ticket receipt, reviewer, implementation
owner, task, workspace/worktree, branch, baseline, correlation, event source revision, monotonic
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
- the ticket's Router receipt is the only currently valid receipt for that ticket and the active
  execution binding has not been replayed, closed or replaced.

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
receives a new task and correlation, and rejects stale old events. There is no separate
`ExecutionReceipt`: when every receipt-bound field remains valid, the replacement binding uses
the same ticket Router receipt; when a receipt-bound owner/worktree/branch/baseline field changes,
only the Router may first revoke the old receipt and issue one replacement receipt bound to the
same ticket. At no point may two receipts for the ticket be valid concurrently. If the old task
is unavailable, only its last committed validated state is recoverable. A new machine uses a
fresh clean checkout/worktree; an old machine path is not provenance.

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
last known non-replayable receipt reference when present. A receipt value committed in a handoff
or manifest is only an opaque historical provenance reference; the live private Router receipt,
grant and execution binding remain outside the target project and are removed with Johnny-owned
state. The observed lifecycle is historical metadata, not proof that a plugin remains installed
and not authority over a successor.

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
token claim requires provider-reported Johnny usage plus the exact user-requested counterfactual
method, tokenizer evidence and assumptions defined by Context Load Telemetry Revision 03.

### AC-20 — Closed receipt algebra

Outside the exact Revision-04 R03 self-host bootstrap route, every governed role action binds
exactly one member of this non-interchangeable union:

```text
WorkReceipt = TicketReceipt | StageWorkReceipt
```

`TicketReceipt` is one-to-one with one ticket and is the only member that can enter
implementation dispatch admission. Same-ticket correction retains the one valid receipt unless
a receipt-bound identity changes, in which case Router revocation precedes replacement.

`StageWorkReceipt` records Architecture, Grill, SPEC or Senior decomposition/audit work. It binds
one project, stage, role/task, exact artifact inputs, context epoch, expected return and evidence
revision. It cannot name an implementation workspace/branch as writable, consume a ticket
dispatch descriptor, authorize source mutation or grant any external effect. Converting or
copying one receipt kind into the other is `HALT / RECEIPT_KIND_MISMATCH`.

The R03-01 `BootstrapDispatchGrant` is neither a third union member nor a receipt. It is the
separately owner-approved, project/ticket-limited exception in AC-31–AC-38 and permanently closes
after normal activation.

### AC-21 — Receipt-bound runtime event adapters

A host adapter may register `MODEL_USAGE_REPORTED`, `ACTION_COMPLETED`, `REVIEW_HANDOFF` or a
trusted supervision fault only when registration returns an exact `event_source_ref`,
`subscription_id`, receipt, role/task and adapter revision. A callback performs ordinary bounded
code and persists metadata without waking a model. At receipt closure, one exact terminal
readback may reconcile missing/duplicate provider usage or completion events. There is no
recurring read, timer, heartbeat or polling fallback; absent capability produces a typed
unavailable/not-reported state.

### AC-22 — On-demand diagnostic owner

Only the Senior may activate a `DIAGNOSTIC_OWNER` through an admitted diagnosis ticket. The
fixed profile is `gpt-5.6-sol` with `xhigh` reasoning. It receives read-only evidence refs,
returns a bounded finding set to the Senior and cannot change source, Context, SPEC or ticket;
dispatch, review, integration and Agent control are forbidden. The role becomes inactive after
its one return. It has no heartbeat and no standing wake subscription.

### AC-23 — Revision-02 transition fence

Revision 02 adds receipt union, runtime event registration and diagnostic-owner boundaries. It
does not change the immutable Revision-01 approval evidence or existing implementation receipts.
Its exact text requires owner approval before the Senior may decompose or ticket it.

### AC-24 — Canonical live TicketReceipt

`TicketReceipt` is the only durable live implementation authority. It binds one project, exact
ticket revision/digest, reviewed ticket and handoff commits, Senior, implementation owner/task,
opaque worktree and branch fingerprints, expected baseline, Context epoch, pending-dispatch
descriptor digest, dispatch question/correlation, expected return and receipt digest. It contains
no raw path, URI, prompt, source, Context body, Secret or PII.

One project/ticket has at most one receipt in `ACTIVE` or `QUARANTINED`. A receipt does not expire.
`DELIVERED` does not consume it: it remains active through execution, same-ticket correction and
terminal handoff. Only Router-controlled revocation or terminal close changes that authority.
When a receipt-bound identity changes, revocation readback must precede one replacement; active
or quarantined lifecycles never overlap.

The existing `TicketDispatchReceipt` is retained as a compatibility projection used by
`IMPLEMENTATION_DISPATCH_CONFIRMED`. The projection is derived from one validated active
`TicketReceipt`; it is never issued, persisted or accepted as a second authority.

### AC-25 — Durable approved-artifact registry and issuance

The live registry atomically registers an immutable record containing project, ticket reference,
ticket revision/digest, ticket-doc commit, reviewed handoff reference, handoff-doc commit and
implementation owner. An identical registration is idempotent. The same registry identity with
different bytes is `ARTIFACT_IDENTITY_CONFLICT`; a missing, stale, closed or unreadable record
cannot issue a receipt.

Receipt issuance is compare-and-swap against the exact live `PendingDispatchDescriptor`, its
digest/revision and the registry record. Duplicate same-request issuance returns the existing
receipt; conflicting issuance returns `RECEIPT_CONFLICT`. A process-local map, reconstructed chat
state or caller-supplied receipt cannot satisfy this AC.

### AC-26 — Exact task/workspace admission before effect

Before a dispatch claim can reach the host, one exact readback validates:

- caller is the receipt-bound Senior and the target is the receipt-bound implementation task;
- task, opaque workspace/worktree fingerprint and restricted implementation profile agree;
- worktree is clean at the expected baseline and belongs to the registered project slot;
- Context Library resolves exactly the receipt-bound `context_epoch_ref` and no prior closed epoch
  is implicit input;
- branch mode is either `USE_BOUND_BRANCH` with an exact current branch or
  `CREATE_FRESH_BRANCH_FROM_BASELINE` with an absent target branch and clean released worktree;
- the complete receipt-bound Git-event/lease/`RoleWakePort` supervision capability is proven.

The fresh-branch mode authorizes only the implementation owner to create/switch its own branch
from the bound baseline after delivery. It does not let the Senior mutate the implementation
worktree. A dirty tree, existing conflicting branch, wrong baseline, ambiguous task, unproved
profile/Context or missing supervision chain halts before receipt claim or host effect.

### AC-27 — One-shot dispatch claim and host envelope

One active receipt may issue one `DispatchOperationClaim` for the finite action
`DELIVER_TICKET`. The claim binds the receipt, pending descriptor, registry revision, Senior,
owner task, operation ID and request digest. Claim is an internal one-shot capability; serialized
metadata, copied objects or the public envelope cannot recreate it.

The host-facing first envelope has exactly these fields and no copied contract body:

```text
ACTION_REQUIRED
dispatch_ref
registry_commit
ticket
receipt
owner_task
```

The Senior is the sole permitted caller. The implementation owner receives no dispatch/wake/
thread-control port, credential or alias. Port admission and claim consumption complete before
the first host call, and each admitted claim can reach the host at most once per attempt.

### AC-28 — Delivery settlement and uncertain-effect quarantine

The host adapter returns exactly one synchronous `HostDispatchOutcome`:

- `DELIVERED`: exact readback proves the envelope was accepted by the bound owner task. The
  dispatch claim becomes `SETTLED`; the `TicketReceipt` remains `ACTIVE`. This is delivery
  evidence, not `IMPLEMENTATION_EXECUTION_STARTED`.
- `NO_EFFECT`: exact adapter evidence proves no message/task/workspace effect occurred. The same
  operation ID may return from `CLAIMED` to `ISSUED` for one idempotent retry; no new receipt,
  correlation or operation is created.
- `EFFECT_UNCERTAIN`: timeout, ambiguous exception, missing result identity or unprovable
  readback quarantines both claim and receipt. No retry, replacement dispatch or execution-start
  event is legal until one separately invoked exact reconciliation proves delivered/no-effect or
  the Router revokes the receipt.

There is no recurring status read, timer, heartbeat, polling or automatic reconciliation. A
replay of `DELIVERED`, a settled claim or a quarantined operation reaches zero host effects.

### AC-29 — Metadata ownership, removal and compatibility

The production registry, receipt and claim adapters persist only bounded validated metadata in
the existing installer-owned journal/checkpoint boundary below
`%LOCALAPPDATA%\JohnnyAIWorkflow`. No database or target-local state is added. Atomic append and
checkpoint replacement must survive interruption without duplicate active receipts or claims.

Uninstall removes only ledger-proved Johnny-owned live registry/receipt/claim records and never
edits a target repository. Target-owned handoff history may retain only an opaque non-replayable
receipt reference. Existing process-local fakes remain test seams and historical evidence but
cannot be selected by a production composition root.

### AC-30 — Revision-03 transition fence and capability truth

Revision 03 is a prerequisite contract, not a dispatch. Its approval authorizes fresh Senior
decomposition only. Ticket admission must separate pure contract/reducer/storage work from the
privileged host adapter and integrated high-assurance proof.

Presence of `send_message_to_thread`, one-shot thread readback or handoff-operation status does
not by itself prove the exact live gateway or supervision subscription. If the implementation
environment cannot prove the required host result and wake chain, it returns the matching typed
capability halt. It may not substitute a fake, manual claim, heartbeat, repeated read or polling.

<a id="bootstrap-ac-31"></a>

### AC-31 — Project-specific bootstrap allowlist and role ownership

The bootstrap route exists only for this repository and the exact R03-01, R03-02 and R03-03
ticket revisions admitted by the Senior. It cannot be inferred from capability failure, reused
for PAG-01/PAG-02, copied to a controlled target project or extended by ticket prose. Any fourth
ticket, project mismatch, revised closure without change control or post-activation use returns
`HALT / BOOTSTRAP_SCOPE_FORBIDDEN`.

Architecture owns the policy and types only. The Senior remains the sole Agent-to-Agent
orchestrator and owns exact ticket admission, implementation owner/task, worktree, branch,
baseline, model/profile, Context epoch, expected return and dispatch action binding. Architecture
must not populate, select or send those execution fields.

### AC-32 — Immutable bootstrap artifact tree and claim-before-effect

The Senior records bootstrap state in a bounded target-owned direct-child tree below the existing
R03 ticket partition. The tree contains separate immutable grant, attempt, delivery-result,
relay-observation, review-decision, correction-grant, integration-grant/result and activation
leaves. Indexes contain only ID, kind, revision, digest, lifecycle and exact direct reference;
sealed leaves never change in place.

Before every new bootstrap claim the Senior first proves the exact target task/host and resolves
the host manager read-only. It then commits one `BootstrapDispatchAttempt` that binds and consumes
one exact grant. Only after that commit may the Senior invoke the delivery adapter once. A later
result leaf records `DELIVERED`, `NO_EFFECT` or `EFFECT_UNCERTAIN`. Crash after adapter invocation,
timeout, ambiguous exception, missing delivery identity or absent exact readback is uncertain and
receives no retry, new operation ID or automatic reconciliation. A new attempt normally requires
a new owner-approved grant. The sole BDA-003 pre-manager correction is governed by Revision 07
and continues the same operation rather than creating an attempt.

### AC-33 — R03-01 no-receipt bootstrap authority

R03-01 alone may start without a `TicketReceipt`. Its `BootstrapDispatchGrant` is an explicit
project-owner authority that binds every Senior-selected execution field, exact ticket/registry
commits, one initial action and expected return. It is not a `WorkReceipt` member, cannot create a
normal implementation lane, cannot be projected as `TicketDispatchReceipt` and cannot claim that
the live registry/issuer exists.

The identifiers-only bootstrap envelope replaces the ordinary `receipt` field with
`bootstrap_grant` and contains exactly:

```text
ACTION_REQUIRED
dispatch_ref
registry_commit
ticket
bootstrap_grant
owner_task
```

No source, prompt body, path, branch, baseline, TDD or copied contract may be added. The owner
resolves them from the committed grant/ticket inside its fixed task/worktree before mutation.

### AC-34 — User relay is wake hint, never evidence

Before normal activation the user may wake the Senior with exactly
`BOOTSTRAP_RETURN_AVAILABLE` plus `grant_ref`. The relay contains no commit claim, test result,
review conclusion or copied handoff. It cannot change state or prove completion.

After wake, the Senior performs read-only task/worktree/branch/commit/handoff validation against
the grant. Only an exact committed implementation return may enter review. No heartbeat,
automation, cron, watchdog, active-turn blocking wait, recurring thread/Git/filesystem read or
timed polling is permitted while waiting for the relay.

### AC-35 — Correction, review and integration authority

Every bootstrap review correction uses a new owner-approved one-shot correction/transport grant
bound to the same ticket and exact review decision. It is claimed before one correction message.
No previous initial/correction grant is reusable. For R03-02/R03-03, the same real receipt is
retained only when every ordinary same-ticket receipt-bound identity remains unchanged.

An independently `APPROVED` review may automatically create one separate
`BootstrapIntegrationGrant` under the already-approved policy. It binds the exact implementation
commit, review decision/commit, current main baseline, integration action/correlation and result
digest. The Senior may perform only the existing guarded local integration. `CHANGES_REQUESTED`,
stale/dirty main, mismatch, conflict, failed checks or absent review returns a typed halt and no
integration grant. Integration never authorizes push, release or deployment.

### AC-36 — Real receipt plus temporary transport for R03-02/R03-03

After reviewed R03-01 integration, R03-02 and R03-03 must use a real active `TicketReceipt` from
the integrated store. Their `BootstrapTransportGrant` authorizes only the still-missing transport
effect; it cannot issue, replace, bypass or repair the receipt and cannot label the dispatch as a
complete normal receipt-bound path.

The ordinary six-field envelope remains unchanged and carries the real receipt. Each transport
attempt still follows AC-32 and waits for the user relay at return. R03-03 is
`HIGH_ASSURANCE_REQUIRED` and requires a separate ticket-specific owner approval before its first
grant. Revision-04 approval alone is not R03-03 implementation authority.

### AC-37 — Normal activation and bounded automatic dispatch

Only all of the following can create one immutable `NormalActivationProof`:

- R03-01, R03-02 and R03-03 are independently reviewed and integrated in dependency order;
- R03-03 real host readback proves the Senior-only gateway and exact delivery semantics;
- the receipt-bound Git-event, lease and `RoleWakePort` supervision chain is real and proven;
- bootstrap grants/attempts are terminal and no uncertain effect or correction remains open;
- current main and capability revisions match the activation candidate.

The sole positive decision is `NORMAL_ACTIVE`. A fake, source/config inspection, tool inventory,
unit test or `CAPABILITY_UNAVAILABLE` is `NORMAL_CAPABILITY_UNPROVEN` and keeps bootstrap closed
to new tickets without enabling normal dispatch.

After `NORMAL_ACTIVE`, bootstrap authority is permanently `CLOSED`. Router may auto-dispatch only
one unique dependency-complete, already-approved low/standard ticket when exact receipt, owner,
task/worktree, branch/baseline, resource/model and supervision gates all pass. `HIGH_ASSURANCE`,
external/irreversible effect, requirement/architecture change, ambiguity, missing authority or
multiple eligible candidates remains `WAIT_FOR_HUMAN` or `HALT` as ordinarily defined.

### AC-38 — Revision-04 transition fence

Revision 04 authorizes only additive Senior correction/admission artifacts for the existing R03
ticket set. It creates no grant, attempt, receipt, task, worktree, branch, dispatch, review,
integration, wake or automatic ticket selection. `DEC-20260816-521` and existing R03 ticket leaves
remain immutable; Senior must add a correction decision and exact bootstrap leaves rather than
rewrite them.

### Revision 05 — approved ticket-defect recovery

The current Router event is `TICKET_DEFECT -> ARCHITECTURE / CHANGE_CONTROL`; the exact proposed
AC-39 through AC-47, typed durable-state contracts, replacement bootstrap dependency graph and
verification matrix are in
[`r05-r03-ticket-defect-recovery.md`](receipt-bound-role-supervision/r05-r03-ticket-defect-recovery.md).
This indexed leaf is part of this one feature SPEC and is owner-approved for Senior decomposition.
The consumed R03-01 grant cannot be replayed. Workflow, CodeReview and executable Router rules
remain unchanged until a separate policy-correction ticket is admitted, implemented and reviewed;
therefore no replacement bootstrap grant or dispatch is currently legal.

### Revision 06 — approved immutable-admission recovery

The first R03-00 route named an immutable `BLOCKED / NON_DISPATCHED` ticket and a baseline that
predated its own grant. Its delivery and Implementer halt are valid historical evidence, but no
retry is legal. AC-48 through AC-56 define a successor CS-02 admission source, additive registry,
exact bridge review and `CLAIM_INTRODUCTION_COMMIT` baseline at
[`r06-r03-00-immutable-admission.md`](receipt-bound-role-supervision/r06-r03-00-immutable-admission.md).
The exact bridge is
[`BPB-R03-00-20260816-002`](receipt-bound-role-supervision/r06-r03-00-policy-bridge-02.md).
At the Revision-06 seal, owner approval authorized only independent Senior review of that bridge
commit; no CS-02 ticket, grant, attempt or implementation authority existed at that time.

### Revision 07 — approved host-bound bootstrap no-effect recovery

The CS-02 route later reached BDA-003, but the Senior host call passed the calling environment
host instead of Implementer-2's authoritative host `local`. The manager lookup rejected the call
before adapter invocation and target readback proves no new delivery turn. AC-57 through AC-65
bind target host identity, require pre-claim manager admission, distinguish the effect boundary,
preserve historical BDR-003 and permit one same-operation continuation after a correction ticket
and independent review at
[`r07-host-bound-bootstrap-recovery.md`](receipt-bound-role-supervision/r07-host-bound-bootstrap-recovery.md).
No new grant, attempt or owner approval is created by that continuation.

## Strongly typed contracts

The following is contract notation, not an alternative implementation language. Python
implementation uses frozen/validated equivalents with no `Any` and passes `mypy --strict`.

```text
opaque HostId
opaque ThreadHostBindingRef

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
enum WorkReceiptKind { TICKET, STAGE_WORK }
enum StageWorkStage { ARCHITECTURE, GRILL, SPECIFICATION, SENIOR }
enum TicketReceiptLifecycle { ACTIVE, REVOKED, CLOSED, QUARANTINED }
enum ApprovedDispatchArtifactLifecycle { ACTIVE, CLOSED }
enum ArtifactRegistrationKind { REGISTERED, ALREADY_REGISTERED, IDENTITY_CONFLICT,
                                STORAGE_UNAVAILABLE }
enum ArtifactReadKind { FOUND, NOT_FOUND, STALE_REVISION, CLOSED, STORAGE_UNAVAILABLE }
enum ReceiptIssueKind { ISSUED, ALREADY_ISSUED, ARTIFACT_NOT_APPROVED,
                        PENDING_DESCRIPTOR_MISMATCH, RECEIPT_CONFLICT,
                        STORAGE_UNAVAILABLE }
enum ReceiptReadKind { FOUND, NOT_FOUND, STALE_REVISION, STORAGE_UNAVAILABLE }
enum WorkspacePreparationMode { USE_BOUND_BRANCH, CREATE_FRESH_BRANCH_FROM_BASELINE }
enum TaskWorkspaceAdmissionKind { READY, PREPARATION_REQUIRED, ROLE_FORBIDDEN,
                                  TASK_UNAVAILABLE, TASK_MISMATCH,
                                  WORKTREE_UNREGISTERED, WORKTREE_DIRTY,
                                  BRANCH_MISMATCH, BRANCH_CONFLICT,
                                  BASELINE_MISMATCH, PROFILE_UNPROVEN,
                                  CONTEXT_EPOCH_UNPROVEN,
                                  SUPERVISION_CHAIN_UNAVAILABLE,
                                  HOST_UNAVAILABLE }
enum DispatchOperationKind { DELIVER_TICKET }
enum DispatchClaimLifecycle { ISSUED, CLAIMED, SETTLED, CANCELLED, QUARANTINED }
enum DispatchClaimResultKind { ISSUED, ALREADY_ISSUED, CLAIMED, SETTLED,
                               CANCELLED, QUARANTINED, RECEIPT_NOT_ACTIVE,
                               CLAIM_MISMATCH, REPLAYED, STORAGE_UNAVAILABLE }
enum HostDispatchOutcome { DELIVERED, NO_EFFECT, EFFECT_UNCERTAIN }
enum DeliveryEffectBoundary { BEFORE_MANAGER_RESOLUTION, BEFORE_ADAPTER_INVOCATION,
                              ADAPTER_INVOCATION_STARTED, DELIVERY_ACKNOWLEDGED }
enum LiveDispatchDecisionKind { DISPATCH_DELIVERED, ALREADY_DELIVERED,
                                NO_EFFECT_RETRYABLE, EFFECT_UNCERTAIN_QUARANTINED,
                                ARTIFACT_REGISTRY_REJECTED,
                                PENDING_DESCRIPTOR_REJECTED,
                                RECEIPT_REJECTED, TASK_WORKSPACE_REJECTED,
                                GATEWAY_UNAVAILABLE, STORAGE_UNAVAILABLE }
enum BootstrapRoutePhase { R03_01_NO_RECEIPT, R03_02_RECEIPT_TRANSPORT,
                           R03_03_RECEIPT_TRANSPORT, NORMAL_ACTIVE, CLOSED }
enum BootstrapGrantKind { INITIAL_DISPATCH, CORRECTION_DISPATCH, TRANSPORT_DISPATCH,
                          TRANSPORT_CORRECTION, INTEGRATION }
enum BootstrapArtifactKind { POLICY, DISPATCH_GRANT, DISPATCH_ATTEMPT, DISPATCH_RESULT,
                             RELAY_OBSERVATION, REVIEW_DECISION, INTEGRATION_GRANT,
                             INTEGRATION_RESULT, NORMAL_ACTIVATION }
enum BootstrapDispatchOutcome { DELIVERED, NO_EFFECT, EFFECT_UNCERTAIN }
enum BootstrapReviewDecisionKind { APPROVED, CHANGES_REQUESTED, BLOCKED }
enum BootstrapIntegrationDecisionKind { INTEGRATED, INTEGRATION_BLOCKED }
enum NormalActivationDecisionKind { NORMAL_ACTIVE, NORMAL_CAPABILITY_UNPROVEN,
                                    NORMAL_ACTIVATION_BLOCKED }
enum RuntimeEventKind {
  MODEL_USAGE_REPORTED, ACTION_COMPLETED, REVIEW_HANDOFF, SUPERVISION_FAULT
}
enum DiagnosticRoleLifecycle { INACTIVE, ACTIVE, RETURNED }

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
  ReceiptRef router_receipt_ref;
  TaskRef implementation_task_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId baseline_commit;
  CorrelationId correlation_id;
  GitObservationMode mode;
  RoleWakeCapabilityProof wake_capability;
}

struct ExecutionStartedEvidence {
  TicketRef ticket_ref;
  ReceiptRef router_receipt_ref;
  TaskRef task_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId baseline_commit;
  MonotonicInstant started_at;
  EvidenceRefs host_readback_refs;
}

struct SupervisionLease {
  LeaseId lease_id;
  TicketRef ticket_ref;
  ReceiptRef router_receipt_ref;
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
  ReceiptRef router_receipt_ref;
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
  TicketRef ticket_ref;
  ReceiptRef active_router_receipt_ref;
  ExecutionBindingRef old_binding_ref;
  ExecutionBindingLifecycle old_lifecycle;
  std::optional<HandoffRef> checkpoint_ref;
  EvidenceRefs revocation_readback_refs;
  ExecutionBindingRef new_binding_ref;
  CorrelationId new_correlation_id;
}

struct StageWorkReceipt {
  StageWorkReceiptId receipt_id;
  ProjectId project_id;
  StageWorkStage stage;
  RoleRef role_ref;
  TaskRef task_ref;
  ArtifactRefs input_refs;
  ContextEpochRef context_epoch_ref;
  ExpectedReturnRef expected_return_ref;
  EvidenceRevision evidence_revision;
  ContentDigest receipt_digest;
}

struct ApprovedDispatchArtifactRecord {
  ApprovedDispatchArtifactRef artifact_ref;
  ApprovedDispatchArtifactLifecycle lifecycle;
  ProjectId project_id;
  TicketRef ticket_ref;
  TicketRevision ticket_revision;
  ContentDigest ticket_digest;
  CommitId ticket_docs_commit;
  HandoffRef reviewed_handoff_ref;
  CommitId handoff_docs_commit;
  RoleRef implementation_owner_ref;
  RegistryRevision registry_revision;
  ContentDigest record_digest;
}

struct ApprovedDispatchArtifactRegisterRequest {
  DispatchRegistryOperationId operation_id;
  RegistryRevision expected_registry_revision;
  ApprovedDispatchArtifactRecord candidate;
  ContentDigest request_digest;
}

struct ApprovedDispatchArtifactRegisterResult {
  ArtifactRegistrationKind kind;
  std::optional<ApprovedDispatchArtifactRecord> record;
  std::optional<DispatchFailureRef> failure_ref;
  RegistryRevision observed_registry_revision;
  ContentDigest result_digest;
}

struct ApprovedDispatchArtifactReadRequest {
  ApprovedDispatchArtifactRef artifact_ref;
  RegistryRevision expected_registry_revision;
  ContentDigest request_digest;
}

struct ApprovedDispatchArtifactReadResult {
  ArtifactReadKind kind;
  std::optional<ApprovedDispatchArtifactRecord> record;
  std::optional<DispatchFailureRef> failure_ref;
  RegistryRevision observed_registry_revision;
  ContentDigest result_digest;
}

struct TicketReceipt {
  TicketReceiptId receipt_id;
  TicketReceiptLifecycle lifecycle;
  ProjectId project_id;
  TicketRef ticket_ref;
  TicketRevision ticket_revision;
  ContentDigest ticket_digest;
  CommitId ticket_docs_commit;
  HandoffRef reviewed_handoff_ref;
  CommitId handoff_docs_commit;
  RoleRef senior_ref;
  TaskRef senior_task_ref;
  RoleRef implementation_owner_ref;
  TaskRef implementation_task_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId expected_baseline_commit;
  WorkspacePreparationMode workspace_preparation_mode;
  ContextEpochRef context_epoch_ref;
  PendingDispatchDescriptorRef pending_dispatch_ref;
  ContentDigest pending_dispatch_digest;
  DispatchQuestionId dispatch_question_id;
  CorrelationId correlation_id;
  ExpectedReturnRef expected_return_ref;
  ReceiptRevision receipt_revision;
  ContentDigest receipt_digest;
}

struct TicketReceiptIssueRequest {
  ReceiptIssueOperationId operation_id;
  ApprovedDispatchArtifactRef artifact_ref;
  RegistryRevision expected_registry_revision;
  PendingDispatchDescriptorRef pending_dispatch_ref;
  ContentDigest pending_dispatch_digest;
  TicketReceipt candidate;
  ContentDigest request_digest;
}

struct TicketReceiptIssueResult {
  ReceiptIssueKind kind;
  std::optional<TicketReceipt> receipt;
  std::optional<DispatchFailureRef> failure_ref;
  ContentDigest result_digest;
}

struct TicketReceiptReadRequest {
  TicketReceiptId receipt_id;
  ReceiptRevision expected_receipt_revision;
  ContentDigest request_digest;
}

struct TicketReceiptReadResult {
  ReceiptReadKind kind;
  std::optional<TicketReceipt> receipt;
  std::optional<DispatchFailureRef> failure_ref;
  ContentDigest result_digest;
}

struct TaskWorkspaceAdmissionRequest {
  DispatchAdmissionOperationId operation_id;
  TicketReceiptId receipt_id;
  RoleRef caller_senior_ref;
  TaskRef implementation_task_ref;
  WorktreeRef expected_worktree_ref;
  BranchRef expected_branch_ref;
  CommitId expected_baseline_commit;
  WorkspacePreparationMode workspace_preparation_mode;
  ModelProfileRef expected_model_profile_ref;
  ContextEpochRef expected_context_epoch_ref;
  RestrictedToolPolicyRef expected_tool_policy_ref;
  SupervisionCapabilityRef expected_supervision_capability_ref;
  ContentDigest request_digest;
}

struct TaskWorkspaceAdmissionResult {
  TaskWorkspaceAdmissionKind kind;
  TicketReceiptId receipt_id;
  std::optional<TaskRef> observed_task_ref;
  std::optional<WorktreeRef> observed_worktree_ref;
  std::optional<BranchRef> observed_branch_ref;
  std::optional<CommitId> observed_head_commit;
  std::optional<ModelProfileRef> observed_model_profile_ref;
  std::optional<ContextEpochRef> observed_context_epoch_ref;
  EvidenceRefs readback_refs;
  ContentDigest result_digest;
}

struct DispatchOperationClaim {
  DispatchClaimId claim_id;
  DispatchClaimLifecycle lifecycle;
  DispatchOperationKind operation_kind;
  DispatchOperationId dispatch_ref;
  TicketReceiptId receipt_id;
  PendingDispatchDescriptorRef pending_dispatch_ref;
  RegistryRevision registry_revision;
  RoleRef senior_ref;
  TaskRef owner_task_ref;
  ContentDigest envelope_digest;
  ClaimRevision claim_revision;
  ContentDigest claim_digest;
}

struct DispatchClaimTransitionRequest {
  DispatchClaimOperationId operation_id;
  DispatchClaimId claim_id;
  ClaimRevision expected_claim_revision;
  DispatchClaimLifecycle expected_lifecycle;
  DispatchClaimLifecycle requested_lifecycle;
  EvidenceRefs evidence_refs;
  ContentDigest request_digest;
}

struct DispatchClaimTransitionResult {
  DispatchClaimResultKind kind;
  std::optional<DispatchOperationClaim> claim;
  std::optional<DispatchFailureRef> failure_ref;
  ContentDigest result_digest;
}

struct ReviewerDispatchEnvelope {
  ActionRequiredLiteral action_required;
  DispatchOperationId dispatch_ref;
  CommitId registry_commit;
  TicketRef ticket;
  TicketReceiptId receipt;
  TaskRef owner_task;
}

struct ReviewerDispatchReadback {
  HostDispatchOutcome outcome;
  DispatchOperationId dispatch_ref;
  TicketReceiptId receipt_id;
  TaskRef owner_task_ref;
  std::optional<HostDeliveryRef> delivery_ref;
  std::optional<HostTaskRevision> observed_task_revision;
  EvidenceRefs readback_refs;
  ContentDigest result_digest;
}

struct LiveDispatchResult {
  LiveDispatchDecisionKind kind;
  TicketReceiptId receipt_id;
  DispatchOperationId dispatch_ref;
  std::optional<DispatchClaimId> claim_id;
  std::optional<HostDeliveryRef> delivery_ref;
  std::optional<DispatchFailureRef> failure_ref;
  EvidenceRefs evidence_refs;
  ContentDigest result_digest;
}

struct BootstrapRoutePolicy {
  BootstrapPolicyId policy_id;
  ProjectId project_id;
  SpecRef spec_ref;
  SpecRevision spec_revision;
  RequirementChangeRef change_ref;
  BootstrapTicketRefs allowlisted_ticket_refs;
  BootstrapRoutePhase current_phase;
  RoleRef architecture_owner_ref;
  RoleRef senior_ref;
  OwnerAuthorityRef owner_authority_ref;
  ArtifactRevision policy_revision;
  ContentDigest policy_digest;
}

struct BootstrapDispatchGrant {
  BootstrapGrantId grant_id;
  BootstrapPolicyId policy_id;
  BootstrapGrantKind grant_kind;
  BootstrapRoutePhase phase;
  ProjectId project_id;
  TicketRef ticket_ref;
  TicketRevision ticket_revision;
  ContentDigest ticket_digest;
  CommitId registry_commit;
  std::optional<TicketReceiptId> ticket_receipt_id;
  RoleRef senior_ref;
  TaskRef senior_task_ref;
  RoleRef implementation_owner_ref;
  TaskRef implementation_task_ref;
  HostId target_host_id;
  ThreadHostBindingRef host_binding_ref;
  WorktreeRef worktree_ref;
  BranchRef branch_ref;
  CommitId expected_baseline_commit;
  ModelProfileRef model_profile_ref;
  ContextEpochRef context_epoch_ref;
  ExpectedReturnRef expected_return_ref;
  std::optional<ReviewDecisionRef> correction_review_ref;
  OwnerAuthorityRef owner_authority_ref;
  ContentDigest grant_digest;
}

struct BootstrapDispatchAttempt {
  BootstrapAttemptId attempt_id;
  BootstrapGrantId grant_id;
  BootstrapGrantKind grant_kind;
  ProjectId project_id;
  TicketRef ticket_ref;
  RoleRef senior_ref;
  TaskRef owner_task_ref;
  HostId target_host_id;
  ThreadHostBindingRef host_binding_ref;
  CommitId claim_commit;
  DispatchOperationId dispatch_ref;
  ContentDigest envelope_digest;
  ArtifactRevision attempt_revision;
  ContentDigest attempt_digest;
}

struct BootstrapDispatchResult {
  BootstrapResultId result_id;
  BootstrapAttemptId attempt_id;
  BootstrapDispatchOutcome outcome;
  HostId target_host_id;
  DeliveryEffectBoundary effect_boundary;
  std::optional<HostDeliveryRef> delivery_ref;
  std::optional<HostTaskRevision> observed_task_revision;
  std::optional<DispatchFailureRef> failure_ref;
  EvidenceRefs readback_refs;
  ArtifactRevision result_revision;
  ContentDigest result_digest;
}

struct BootstrapRelayObservation {
  BootstrapRelayObservationId observation_id;
  BootstrapGrantId grant_id;
  BootstrapReturnAvailableLiteral event_kind;
  RoleRef target_senior_ref;
  EvidenceRevision observation_revision;
  ContentDigest observation_digest;
}

struct BootstrapReviewDecision {
  BootstrapReviewDecisionId decision_id;
  BootstrapGrantId grant_id;
  BootstrapReviewDecisionKind decision;
  TicketRef ticket_ref;
  RoleRef reviewer_ref;
  CommitId implementation_commit;
  ReviewRef review_ref;
  CommitId review_commit;
  EvidenceRefs verification_refs;
  ContentDigest decision_digest;
}

struct BootstrapIntegrationGrant {
  BootstrapIntegrationGrantId grant_id;
  BootstrapPolicyId policy_id;
  BootstrapReviewDecisionId approved_review_decision_id;
  TicketRef ticket_ref;
  CommitId implementation_commit;
  CommitId review_commit;
  CommitId expected_main_commit;
  IntegrationActionRef integration_action_ref;
  CorrelationId correlation_id;
  ContentDigest grant_digest;
}

struct BootstrapIntegrationResult {
  BootstrapIntegrationResultId result_id;
  BootstrapIntegrationGrantId grant_id;
  BootstrapIntegrationDecisionKind decision;
  std::optional<CommitId> integration_commit;
  std::optional<IntegrationFailureRef> failure_ref;
  EvidenceRefs readback_refs;
  ContentDigest result_digest;
}

struct NormalActivationProof {
  NormalActivationProofId proof_id;
  BootstrapPolicyId policy_id;
  IntegrationRefs r03_integration_refs;
  HostGatewayCapabilityProof host_gateway_proof;
  SupervisionCapabilityProof supervision_capability_proof;
  OpenBootstrapArtifactRefs open_artifact_refs;
  CommitId expected_main_commit;
  CapabilityRevision capability_revision;
  NormalActivationDecisionKind decision;
  std::optional<NormalActivationFailureRef> failure_ref;
  ContentDigest proof_digest;
}

port LiveApprovedDispatchArtifactRegistryPort {
  ApprovedDispatchArtifactRegisterResult register(
      ApprovedDispatchArtifactRegisterRequest request);
  ApprovedDispatchArtifactReadResult read_exact(
      ApprovedDispatchArtifactReadRequest request);
}

port TicketReceiptStorePort {
  TicketReceiptIssueResult issue_exact(TicketReceiptIssueRequest request);
  TicketReceiptReadResult read_exact(TicketReceiptReadRequest request);
}

port DispatchClaimStorePort {
  DispatchClaimTransitionResult issue_exact(DispatchOperationClaim candidate);
  DispatchClaimTransitionResult transition_exact(
      DispatchClaimTransitionRequest request);
}

port TaskWorkspaceAdmissionPort {
  TaskWorkspaceAdmissionResult admit(TaskWorkspaceAdmissionRequest request);
}

port ReviewerDispatchGatewayPort {
  ReviewerDispatchReadback deliver(
      DispatchOperationClaim claim, ReviewerDispatchEnvelope envelope);
}

struct RuntimeEventRegistration {
  EventSourceRef event_source_ref;
  SubscriptionId subscription_id;
  WorkReceiptRef receipt_ref;
  RoleRef role_ref;
  TaskRef task_ref;
  RuntimeEventKind event_kind;
  AdapterRevision adapter_revision;
  ContentDigest registration_digest;
}

struct DiagnosticRoleBinding {
  ProjectId project_id;
  TicketReceiptRef diagnosis_ticket_receipt_ref;
  RoleRef senior_ref;
  RoleRef diagnostic_owner_ref;
  ModelRef model_ref;
  ReasoningEffort reasoning_effort;
  DiagnosticRoleLifecycle lifecycle;
  EvidenceRefs bounded_read_refs;
}
```

Result nullability is closed:

- registration/read/issue success kinds require their exact record/receipt and no failure;
  rejection kinds require one failure and no record/receipt;
- `TaskWorkspaceAdmissionResult` requires exact observed values and non-empty readback refs for
  `READY`/`PREPARATION_REQUIRED`; an unavailable value stays absent and may never be fabricated;
- `DELIVERED` requires one `delivery_ref` and exact task revision; `NO_EFFECT` forbids a delivery
  ref; `EFFECT_UNCERTAIN` may carry only the last trustworthy readback fields;
- `DISPATCH_DELIVERED`/`ALREADY_DELIVERED` require claim and delivery refs with no failure;
  rejection/quarantine kinds require the corresponding failure and forbid invented success refs.

The live use case evaluates failures in this fixed order before the first effect: public schema
and digest; project and Senior role; approved artifact/revision; pending descriptor; existing
receipt/claim; task/workspace/branch/baseline; model/profile/tool policy/Context epoch; supervision
chain; gateway capability; durable claim transition; host delivery/readback. An earlier failure
prevents every later port call. Storage failure always fails closed and never falls back to
process-local state.

Bootstrap nullability and identity are also closed:

- the Revision-04 executable policy allowlist contains exactly the current
  R03-01/R03-02/R03-03 revisions and no other ticket. The separately approved BPB is a manual
  pre-policy bridge for exact R03-00, not an allowlist member; `NORMAL_ACTIVE` can transition only
  to `CLOSED`, never back to a bootstrap phase;
- `R03_01_NO_RECEIPT` requires `ticket_receipt_id = None`; both receipt-transport phases require
  one exact active receipt. Any opposite shape is `BOOTSTRAP_RECEIPT_KIND_MISMATCH`;
- correction grant kinds require one exact `correction_review_ref`; initial/transport initial
  grants forbid it. Architecture owner identity never substitutes for the Senior-selected
  implementation bindings;
- one grant has exactly one attempt. The attempt's committed claim predates adapter invocation and
  prevents a second effect-bearing invocation regardless of whether a result leaf exists. The
  exact Revision-07 BDA-003 correction proves the first tool rejection occurred before manager/
  adapter invocation and therefore permits its one remaining same-operation call;
- bootstrap `DELIVERED` requires exact target host, `DELIVERY_ACKNOWLEDGED`, delivery/task revision
  and no failure; `NO_EFFECT` requires an explicit pre-invocation boundary and failure proof while
  forbidding delivery/task revision; `EFFECT_UNCERTAIN` carries only trustworthy readback plus its
  last known boundary/failure and never permits reuse;
- a relay observation contains only the return-available literal, grant and target Senior. It
  carries no implementation, test or review evidence;
- integration `INTEGRATED` requires one integration commit and no failure; blocked integration
  requires one failure and no integration commit;
- `NORMAL_ACTIVE` requires the three exact integration refs, positive real host/supervision
  proofs, an empty open-artifact set and no failure. Every other decision requires a failure and
  grants no normal dispatch.

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
9. Replacement tests prove old/new non-overlap, revocation readback, one-active-ticket-receipt
   semantics, new binding/correlation, stale-event rejection, same-shell no-op, new-machine clean
   worktree and last-commit-only crash recovery. They reject `ExecutionReceiptRef`, concurrent
   same-ticket receipts and non-Router receipt replacement.
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
15. Receipt-union tests reject StageWork-to-ticket conversion, source/workspace authority on a
    StageWork receipt, a second live ticket receipt, wrong stage/role/task/context epoch and
    replay before Agent or filesystem effect.
16. Runtime-event tests require exact event source, subscription, receipt, role/task and adapter
    revision; callback deduplication and one closure reconciliation are deterministic. Missing
    capability never selects heartbeat, recurring read or polling.
17. Diagnostic-role tests enforce the exact Sol xhigh profile, Senior-only activation,
    read-only finding return, one-shot lifecycle and denial of source/spec/ticket/context writes,
    dispatch, review, integration and Agent control.
18. Transition tests preserve all Revision-01 receipts and evidence and reject Revision-02
    decomposition/ticketing before exact owner approval.
19. `TicketReceipt` constructor/schema tests cover every named field and lifecycle, reject raw
    locators/content, expiration fields, a second active/quarantined receipt and any attempt to
    use the legacy `TicketDispatchReceipt` projection as live authority.
20. Durable registry tests prove exact registration, identical idempotence, commit/digest/owner/
    project collision, closed/stale/unavailable reads, interruption recovery and zero receipt or
    host calls after an earlier failure.
21. Receipt-store tests prove compare-and-swap issuance from one exact pending descriptor,
    duplicate same-request readback, conflicting issuance, revocation-before-replacement, no
    expiry and receipt survival after dispatch-claim settlement.
22. Task/workspace admission tests cover both branch modes and every finite rejection. Fresh
    branch admission requires absent target branch plus a clean released worktree at the exact
    baseline; the Senior never mutates that worktree.
23. Dispatch-claim tests prove one live non-transferable claim, synchronized duplicate consume,
    copied/forged/replayed claims, wrong Senior/task/receipt/descriptor/registry revision and
    storage failure all reach zero host effects.
24. Envelope tests assert exactly the six canonical identifier fields, no copied ticket body,
    prompt, path, URI or extra field, and exact re-resolution from the registered commit.
25. Host-result tests prove `DELIVERED` settles only the claim, `NO_EFFECT` permits only the same
    operation retry and `EFFECT_UNCERTAIN` quarantines without retry. Timeout/exception/ambiguous
    readback reverse mutations must turn red.
26. Composition/source gates reject the process-local registry/fake in production, heartbeat,
    recurring reads, polling, timer loops, new DB/service/MCP state and target-local receipt
    persistence. Each gate has one bounded reverse-mutation proof.
27. Integrated high-assurance acceptance uses a disposable owned metadata root and a proved host
    fake/adapter boundary. Tool inventory or synthetic success remains `CAPABILITY_UNAVAILABLE`;
    the test creates no live task, message, branch, target write or wake unless a later ticket
    carries the exact effect authority.
28. Revision-04 bootstrap policy/schema tests cover the exact three-ticket allowlist, phase order,
    no-receipt R03-01 shape, receipt-required R03-02/R03-03 shape, architecture/Senior role
    separation and rejection of every other project/ticket/revision or post-activation use. The
    separate BPB review proves it is not projected into that executable allowlist.
29. Artifact-tree tests prove direct-child-only indexes, immutable additive leaves, exact digests
    and one grant/one attempt. A claimed grant with no result is uncertain and never callable
    unless a Revision-07 typed pre-adapter proof authorizes the exact same-operation continuation.
30. Envelope tests prove R03-01 substitutes only `bootstrap_grant` for `receipt`; R03-02/R03-03
    retain the ordinary real-receipt envelope. Extra/missing/copied contract fields fail before
    the Senior host call.
31. Relay tests prove `BOOTSTRAP_RETURN_AVAILABLE + grant_ref` can only select Senior readback;
    copied commit/test/handoff claims never become evidence and no recurring wait/read exists.
32. Review/correction tests require a new owner-approved grant for every new attempt, retain an
    R03-02/R03-03 receipt only under unchanged identity and reject replay of every prior grant.
    The exact Revision-07 BDA-003 continuation is settlement of the existing operation, not a new
    attempt or grant.
33. Integration tests issue a distinct grant only from exact `APPROVED` review and prove
    implementation/review/main baseline binding, guarded integration, stale/conflict failure and
    absence of push/release/deploy authority.
34. Activation tests require three reviewed integrations, real positive gateway/supervision
    proofs and zero open/uncertain bootstrap artifacts. Fake/unsupported evidence stays unproven;
    positive activation permanently closes bootstrap.
35. Auto-dispatch tests admit exactly one unique approved dependency-ready low/standard ticket
    after activation and preserve owner waits/halts for high assurance, external effects,
    change/ambiguity, missing gate or multiple candidates.

## Reviewer decomposition constraints

After exact owner approval, the reviewer may compile this SPEC into the smallest vertical
closures. A safe dependency order is:

1. strong typed handoff/index/manifest contracts and pure validators;
2. pure supervision lease and model-policy reducer;
3. exact Git ref event adapter plus handoff readback/deduplication;
4. proved `RoleWakePort` composition and capability preflight;
5. controlled execution/model replacement;
6. target-owned tree/bootstrap and root README integration;
7. integrated high-assurance acceptance and resource qualification;
8. closed TicketReceipt/StageWorkReceipt algebra and admission fence;
9. receipt-bound runtime event registration and terminal reconciliation;
10. on-demand diagnostic-owner lifecycle and read-only finding return.
11. canonical live `TicketReceipt`, durable artifact registry and receipt-store reducers;
12. task/workspace admission plus one-shot dispatch-claim settlement;
13. Senior-only host adapter and integrated high-assurance capability proof.
14. additive Revision-04 bootstrap admission/correction artifacts for the existing R03 sequence;
    no new implementation ticket is created merely to represent the exception.
15. Revision-07 target-host binding, pre-claim host admission and the exact BDA-003 no-effect
    correction/continuation; no BDG-004 or BDA-004 may represent that continuation.

Items 8 through 10 are approved Revision-02 boundaries available for fresh Senior decomposition.
Existing Revision-01 admission evidence is immutable; approval itself creates no ticket.

Items 11 through 13 are approved Revision-03 prerequisite boundaries. The Senior must keep pure
metadata/storage work separate from the privileged host effect. Item 13 cannot be admitted as
`READY_LOW_MODEL`; a truthful unsupported result is valid evidence but does not unblock dispatch.

Item 14 is the approved Revision-04 re-admission route. Senior must amend status through additive
decision/grant leaves, not rewrite `DEC-20260816-521` or the three ticket bodies. Selecting exact
owners/workspaces and performing dispatch remain Senior actions outside architecture scope.

Item 15 is the approved Revision-07 correction boundary. Senior compiles one exact correction
ticket and obtains independent review before creating the additive correction/continuation leaf
or making the one permitted host call. Architecture does not create the ticket or call the host.

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
- A durable receipt store prevents process loss from manufacturing authority, but it cannot make
  an unavailable host task/wake API available. Capability truth remains a separate hard gate.
- An ambiguous host timeout may leave a quarantined ticket unable to dispatch until exact manual
  reconciliation or Router revocation. This is intentional; duplicate implementation is the
  higher-risk failure.
- Revision-03 rollback closes/quarantines live claims, removes only installer-ledger-owned state
  and restores the prior fail-closed no-live-dispatch condition. It never deletes target history.
- Bootstrap commit-before-effect conservatively strands a grant only when the effect boundary is
  uncertain. A trusted rejection before manager/adapter invocation is proved no-effect and may
  continue only the same operation identity under Revision 07; it cannot create a new grant,
  attempt or second call.
- User relay adds a temporary manual interaction but no background token/CPU cost. It disappears
  only after real activation proof; inability to prove R03-03 leaves normal dispatch disabled.
- Revision-04 rollback closes the allowlisted policy and leaves immutable bootstrap provenance in
  Git. It cannot reactivate a consumed grant or alter an already-integrated implementation.
- R03-00 bridge rollback closes only the current BPB-002 authority and restores the fail-closed
  policy-correction blocker. BPB-001 remains consumed history. Rollback cannot widen Revision 04,
  dispatch A–D or alter any ticket/grant/attempt evidence.
- Deployment implementation is not authorized here. Any future deployment ticket independently
  applies the security effect boundary and exact environment/artifact readback.

## Convergence and lineage

- Sealed shared Context: `CONTEXT.md` under `CHG-20260816-025`; original role-supervision facts
  are authorized by `CHG-20260815-023` and Revision-02 facts by `CHG-20260816-025`.
- Revision-03 live-dispatch facts are authorized by `PRD-20260816-026` /
  `CHG-20260816-026`; they do not alter the sealed shared Context body.
- Revision-04 self-host bootstrap facts are authorized by `PRD-20260816-027` /
  `CHG-20260816-027`; they do not create a generic target-project exception.
- Revision-05 recovery facts are authorized by `PRD-20260816-028` / `CHG-20260816-028`;
  the one-ticket R03-00 bridge is authorized by `PRD-20260816-029` / `CHG-20260816-029`.
- Revision-06 immutable-admission recovery and BPB-002 are authorized by `PRD-20260816-030` /
  `CHG-20260816-030`; they preserve the consumed BPB-001 route as historical evidence.
- Revision-07 host-bound bootstrap recovery is authorized by `PRD-20260817-031` /
  `CHG-20260817-031`; it preserves BDG/BDA/BDR-003 while correcting the proved pre-manager result.
- Feature Context: `doc/context/receipt-bound-role-supervision/main.md`.
- Active requirement leaves:
  `doc/requirements/active/2026/workflow-governance/REQ-20260815-023.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260816-025.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260816-026.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260816-027.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260816-029.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260816-030.md` and
  `doc/requirements/active/2026/workflow-governance/REQ-20260817-031.md`.
- ADRs: `doc/adr/ADR-20260815-012-receipt-bound-event-driven-completion-supervision.md` and
  `doc/adr/ADR-20260816-014-project-neutral-orchestration-evidence-and-counterfactual-telemetry.md`
  and `doc/adr/ADR-20260816-015-live-receipt-dispatch-settlement.md`.
- Bootstrap ADR: `doc/adr/ADR-20260816-016-self-host-bootstrap-dispatch-exception.md`.
- Host-bound recovery ADR:
  `doc/adr/ADR-20260817-018-host-bound-bootstrap-no-effect-recovery.md`.
- XSS classification: `N/A`; this feature has no Browser/WebView/HTML/DOM/JavaScript renderer
  flow. A future UI or untrusted renderer integration re-runs the XSS gate.
- New external effects: role wake and task replacement are privileged Agent-control effects and
  therefore `HIGH_ASSURANCE`. Push, release and deployment remain out of scope.
- Open architecture questions: none after owner Grill convergence through `2026-08-17`.
- Current governed return: `APPROVAL_GRANTED -> ACTION_COMPLETED / SPEC`; the only next route is
  `TICKETS / SENIOR_CORRECTION_TICKET` for Revision 07 followed by independent review.
  Architecture does not select an execution owner, create the ticket or call the host. Approval
  alone creates no continuation record or implementation effect.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `2701ed563f26e116db69e8e4fcb84024754c9498` | Independent draft after completed Grill; replaces the unapproved attempt to revise the collaboration-audit SPEC. |
| 2026-08-15 | Architecture owner / `main` / `f7eb3d3c9c88c23c3bc29bc9565ebc5b3b7096f9` | Removed the separate execution-receipt concept, bound supervision to the ticket's sole active Router receipt and reattached the draft to the latest sealed shared Context. |
| 2026-08-15 | Project owner | Approved the exact Receipt-bound Role Supervision SPEC including the single-active Router receipt revision and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-16 | Architecture owner / `main` / `2a8287831259243e230911e1082f0ec87895d3c5` | Drafted Revision 02 closed receipt algebra, runtime event registration and on-demand diagnostic owner under `CHG-20260816-025`; exact owner approval pending. |
| 2026-08-16 | Project owner | Approved the exact Receipt-bound Role Supervision Revision 02 and authorized fresh Senior decomposition only. |
| 2026-08-16 | Architecture owner / `main` / `a8a27e6b61f4a50debd90f421da8cd53661b965b` | Added Revision 03 durable live TicketReceipt, approved-artifact registry, exact task/workspace admission and one-shot host dispatch settlement under `CHG-20260816-026`. |
| 2026-08-16 | Project owner | Approved the Revision-03 live receipt dispatch prerequisite and authorized fresh Senior decomposition only; four previously recorded Revision blockers remain a later sequence. |
| 2026-08-16 | Architecture owner / `main` / `48e8ca8b9e404d81694415c7c4e9a9c81b3f859d` | Added Revision 04 finite self-host bootstrap grant/attempt/relay/review/integration and normal-activation contracts under `CHG-20260816-027`. |
| 2026-08-16 | Project owner | Approved Revision 04 decisions: project-only R03 scope, user return relay, new grant per correction, separate automatic integration grant, real-receipt transport bridge for R03-02/R03-03, high-assurance R03-03 approval and bounded normal auto-dispatch. |
| 2026-08-16 | Architecture owner / `main` / baseline `6569cd41bbf3ecbc04108da4150c30267951dda5` | Drafted Revision 05 after `CR-R03-01-001`: immutable failed-attempt fence, four-stage R03-01 replacement, real owned-file durable transaction contract, truthful strict-type baseline and reviewer-owned disposable verification. Exact owner approval pending. |
| 2026-08-16 | Project owner / approved draft `c64681e847c1a6847c2588d127ed7f2749c914b5` | Approved Revision 05 for Senior decomposition and policy-correction/replacement-ticket drafting only; no grant, dispatch, implementation or executable policy mutation is authorized by approval alone. |
| 2026-08-16 | Project owner / Architecture Grill | Approved `BPB-R03-00-20260816-001` as a review-gated, one-ticket bridge for R03-00 only; direct R03-01A–D coverage remains forbidden. |
| 2026-08-16 | Project owner / Architecture Grill | Approved Revision 06 and `BPB-R03-00-20260816-002`: preserve the consumed CS-01 route, require a new self-admitting CS-02 registry, and use the consuming attempt introduction commit as execution baseline. |
| 2026-08-17 | Project owner / Architecture Grill | Approved Revision 07: bind target host from target-task readback, admit host manager before claim, correct BDR-003 through an additive proved-no-effect decision and permit one same-operation continuation at `hostId=local` without BDG-004/BDA-004 or another owner grant. |

## Approval record

- Decision maker: project owner.
- Architecture/Grill direction: confirmed through `2026-08-16 (Asia/Taipei)`.
- Exact SPEC revision: Revision 01 `APPROVED`; Revision 02 `APPROVED`; Revision 03
  `APPROVED`; Revision 04 `APPROVED`; Revision 05 `APPROVED`; Revision 06 `APPROVED`;
  Revision 07 `APPROVED`; BPB-001 `HISTORICAL / CONSUMED`; BDG/BDA/BDR-003
  `HISTORICAL / IMMUTABLE` on `2026-08-17`.
- Approval effect: authorizes Senior to create and independently review one exact Revision-07
  correction ticket, then continue only the existing BDA-003 operation once at explicit
  `hostId=local`. It creates no ticket itself, new grant, new attempt, receipt, second host call,
  heartbeat, push, release or deployment authority.
