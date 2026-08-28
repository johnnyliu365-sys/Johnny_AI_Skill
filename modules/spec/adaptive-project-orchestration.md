# Adaptive Project Orchestration Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Status | `REVISION_05_ROUTER_PHASE_APPROVED / REVISION_06_PROJECT_ISOLATION_APPROVED / REVISION_07_HOST_GATEWAY_APPROVED / REVISION_09_PROCEDURAL_MANAGED_ARTIFACT_BEHAVIOR_APPROVED / REVISION_10_MUTATION_STATE_ALGEBRA_APPROVED / REVISION_11_RECOVERABLE_RUNTIME_APPROVED / REVISION_12_ATOMIC_CONDITIONAL_REPLACE_CAPABILITY_GATE_APPROVED / REVISION_13_REMOTE_AUTHORITY_COMMIT_APPROVED / R09A_TICKET_OPENING_AUTHORIZED / R09B1_COMPLETE / R09B2_SUPERSEDED / CAP_RWW6_01_COMPLETE_ALL_EXECUTED_TUPLES_NO / CAP_REMOTE_AUTHORITY_01_TICKET_OPENING_AUTHORIZED / OTHER_APPROVED_SCOPES_UNCHANGED` |
| Author / baseline | Codex architecture owner / `5e351ce9d57af321dfb14c6b102e9749da7efc25` |
| Context | `doc/context/adaptive-project-orchestration/main.md` (prior sealed facts), `doc/context/adaptive-project-orchestration/adaptive-project-orchestration-r09-procedural-managed-artifact-behavior.md` (`SEALED / REVISION_09`), `doc/context/adaptive-project-orchestration/adaptive-project-orchestration-r11-recoverable-managed-artifact-runtime.md` (`SEALED / REVISION_11`), `doc/context/adaptive-project-orchestration/adaptive-project-orchestration-r12-atomic-conditional-replace-capability.md` (`SEALED / REVISION_12`), `doc/context/adaptive-project-orchestration/adaptive-project-orchestration-r13-remote-authority-commit.md` (`SEALED / REVISION_13`) and `doc/context/host-gateway-workspace-binding/codex-desktop-readback.md` (`SEALED`) |
| PRD | `PRD-20260813-016`, `PRD-20260813-017`, `PRD-20260814-019`, `PRD-20260815-020`, `PRD-20260815-022`, `PRD-20260815-024`, `PRD-20260822-031`, `PRD-20260828-043`, `PRD-20260828-044`, `PRD-20260828-045`, `PRD-20260829-046` |
| Requirement change / ADR | `CHG-20260813-016`, `CHG-20260813-017`, `CHG-20260814-019`, `CHG-20260815-020`, `CHG-20260815-022`, `CHG-20260815-024`, `CHG-20260822-031`, `CHG-20260828-043`, `CHG-20260828-044`, `CHG-20260828-045`, `CHG-20260829-046` / `ADR-20260813-008`, `ADR-20260813-009`, `ADR-20260814-011`, `ADR-20260815-013`, `ADR-20260828-031`, `ADR-20260828-032`, `ADR-20260828-033`, `ADR-20260829-034` |
| Implementation language | Python 3.11 strict typed contracts/adapters; host-specific integration only after capability proof |

## Problem and goal

Johnny must be easy to adopt for a small repository without weakening the
controls required by a high-risk product. Installation alone has no authority
to select or modify a target repository. After a user chooses a repository,
Johnny needs one guided initialization followed by reviewer-owned automatic
ticket execution. The amount of documentation, verification and implementation
capacity must be evidence-based and proportional to risk and coupling.

## Non-goals

- No target-project write during package installation.
- No silent task/model/worktree creation, host-login bypass or unverified host
  automation.
- No reduction of reviewer-only orchestration, TDD, typed contracts, XSS,
  Secret, ownership or guarded-integration gates. Exact workspace binding remains mandatory for
  `HIGH_ASSURANCE` host effects; an approved POC manual-evidence path records an absent binding
  as a named gap rather than representing it as proof.
- No model name, project file count or source-line count as authority or the
  sole complexity classifier.
- No unbounded Agent fan-out and no implementation-owner delegation.
- No direct post-POC development on the frozen accepted POC/stable ref, and no
  conflation of a staging integration baseline with a disposable test sandbox
  or a release.

## User flow and acceptance criteria

1. Installation exposes a Johnny-owned Getting Started README and an
   initialization command/action; it leaves every target repository unchanged.
2. The user selects a Git repository. Read-only preflight resolves its canonical
   identity, status, existing target-owned artifacts, host capabilities and the
   opaque Johnny-owned ticket-workspace storage reference. It does not persist the raw
   target path in Router state.
3. Johnny renders an exact initialization plan. One explicit confirmation
   authorizes only that plan.
4. Initialization writes only the explicitly approved target-owned project
   artifacts, records the opaque project-to-storage mapping below the per-user
   Johnny root, and opens/binds the reviewer when supported. It does not modify
   `.gitignore`, create a Johnny path in the target, or create an implementer.
5. At intake and before each ticket dispatch, the reviewer selects a delivery
   profile and resource plan from typed evidence. Approved tickets then cause
   the reviewer to create or reuse the minimum required implementer lanes.
6. After the first POC is independently accepted, one exact staging transition
   freezes the POC identity and admits the staging baseline used by every later
   feature/architecture ticket.
7. The architecture owner sleeps only after one exact owner-approved SPEC
   revision passes readiness. A Terra supervisor/reviewer then decomposes that
   revision into tickets admitted for a Luna implementation owner.
8. Unresolved semantics, architecture or assurance wake the architecture owner
   through the Router. Formal UI separately classifies an optional design
   source; Figma is never an installation prerequisite.

### AC-01 — Install/init separation

The installer writes only its owned payload/README/entry point. Target project
files, Git configuration, branches, worktrees and Agent tasks remain unchanged
through installation and preflight. One exact confirmed
`ProjectInitializationPlan` may write only its listed target-owned project
artifacts and external Johnny mapping; it grants no target Git or task-workspace
effect.

### AC-02 — Target-owned project material

After confirmation, Context, PRD, requirement changes, specifications, tickets,
progress/review evidence, tests and product source remain target-owned and
target-versioned. Johnny's `AGENTS.md`, `Workflow.md` and `CodeReview.md` remain
plugin-owned and are not copied into the target repository. Johnny-specific
manifests, runtime, cache, telemetry and worktree directories are forbidden in
the target. Dispatch must not attach a linked Git worktree to the target's
common directory, because `.git/worktrees` would persist a Johnny workspace
path. Standard target Git state may change only under the exact later
integration receipt that authorizes that Git effect.

### AC-03 — Project-neutral ticket workspace

Each implementation workspace is an exact receipt-bound standalone Git checkout
or isolated clone beneath a Johnny-owned per-user root selected by opaque
`ProjectId`; it is neither a child of the target repository nor a linked
`git worktree` of the target's common Git directory. Creation reads only the
exact committed baseline and immediately removes any persisted raw target-path
remote; later synchronization/integration resolves both endpoints transiently
inside the guarded Git adapter. Dispatch therefore leaves target bytes, refs,
config and `.git/worktrees` unchanged.

A path escape, reparse/symlink, hardlink/object-sharing dependency, foreign
child, dirty/stale base, wrong baseline, ownership mismatch or non-empty
unauthorized root halts before Git or host effect. Initialization creates no
workspace. Existing linked or target-local worktrees are never moved or deleted
by path manipulation: an already valid binding may finish only its existing
ticket, and a separately reviewed migration/cleanup ticket must retire legacy
target state. Every new or replacement workspace uses the isolated root.
Detach/uninstall revokes Johnny authority and removes only safely identified
Johnny-owned standalone workspace state; it never edits the target and never
blocks a successor from using native Git. Any legacy target Git residue is
reported as non-authoritative migration evidence, not kept as a runtime
dependency or silently removed.

### AC-04 — Reviewer-first activation

Initialization creates or binds exactly one reviewer task only after host
capability and workspace identity readback. It creates no implementer.
Implementer worktrees/tasks are created or reused only by that reviewer after
a ticket-specific dispatch receipt. Unsupported automation returns a finite
manual-handoff/block result and cannot claim automatic activation.

### Revision 07 approved amendment — host-gateway workspace and profile binding

This owner-approved amendment completes the public contract surfaces that
`TAD-ADAPTIVE-R06-ISOLATION-01` leaves open for AC-03 and AC-04. It does not
approve an implementation ticket, issue a receipt, create a workspace/task,
call a host, deliver a handoff, or change the already-approved Revision 06
workspace-isolation rule.

The three contract families below are serial. First validate an already
active receipt and the reviewer capability; next reserve an idle host task
through that receipt-bound capability; next take exact host/profile and
workspace readback; only a valid admission may expose the existing one-shot
identifier-only delivery port. A host that cannot reserve a task without
starting an Agent turn, cannot read back the exact task workspace, or cannot
read back the effective profile and verified rank is unsupported. It returns a
finite no-effect result rather than using prompt text, a shell working
directory, a static configuration value, a model request, a CLI login or task
self-report as evidence.

`HIGH_ASSURANCE` applies: this is a new privileged host boundary. XSS is
`N/A`; untrusted host JSON is normalized at the adapter boundary and never
rendered as HTML/DOM/JavaScript. Provider credentials, provider invocation,
runner/subscription lifecycle and automatic wake remain outside this amendment.

#### AC-03R7 — Workspace identity verification

The Workspace Identity contract receives only one transient host workspace
root plus exact expected project/worktree/branch/baseline references. It must
prove all of the following before emitting an opaque proof:

1. platform-normalized absolute root equality;
2. resolved filesystem identity after reparse/symlink resolution; and
3. exact registered Git worktree metadata, branch and baseline ancestry.

Path equality alone, a prompt/handoff path, shell `cd`, environment value,
sibling access or task self-report is not proof. Any missing or disagreement
returns `TASK_WORKSPACE_MISMATCH` or a more specific finite workspace failure
before source, Git, task or host delivery effect. Durable records contain only
opaque project/task/workspace/worktree references, evidence digest and
revision; raw paths never cross the boundary.

#### AC-04R7 — Receipt-bound host admission

Only the exact reviewer capability for the exact approved artifact and active
receipt may reserve or reuse one idle implementation task. The reservation
must not start an Agent turn, expose ticket source, or deliver a prompt. Its
readback must attest the same host/project/task, effective semantic profile,
effective effort reference and verified capability rank that the request
expects. The implementation reviewer rank must be at least the implementation
rank. A host that offers only active prompt-driven task creation does not meet
this contract.

An exact descriptor/correlation check then combines the active receipt, host
readback and workspace proof. Only `ADMITTED` exposes a single downstream
delivery capability; every other result exposes no task-control port. The
delivery capability remains subject to the existing one-shot dispatch
composition and creates no automatic wake claim.

### Revision 08 approved amendment — POC-proportional admission evidence

`PRD-20260822-032` separates a bounded POC resolver closure from the privileged R07 host
boundary. It does not weaken R07, issue a receipt, create a task/worktree, bind a host profile,
invoke a provider, start a runner, or claim automatic wake.

#### AC-04R8 — POC manual-evidence path

Only a ticket that is explicitly `delivery_stage = POC`, has a committed evidence-backed
assessment without a hard `HIGH_ASSURANCE` trigger, and has no host/provider/process/Git/receipt
effect may use this path. Its implementation boundary remains ticket-scoped and reviewer-owned.
The completion evidence is the applicable document-mutation gate plus one reviewer-run
counter-mutation through a test path distinct from the implementation owner's recorded mutation.

If host workspace/profile/effort/rank readback is absent, the ticket records exactly
`KNOWN_GAP_WORKSPACE_BINDING_READBACK_UNAVAILABLE`. The gap cannot serve as a binding, receipt,
delivery, runner or wake assertion. It permits no privilege, task-control or host-control port.
Any request for those effects routes to the R07 `HIGH_ASSURANCE` admission path.

#### AC-05R8 — Stage and intensity remain distinct

`POC` is a delivery stage. `COMPACT`, `STANDARD` and `HIGH_ASSURANCE` remain intensities derived
from the committed workload evidence. The owner and reviewer record the selected POC manual path
from that evidence; intent to dispatch, a model label, prompt, repository size or source-line
count cannot lower an intensity. A hard trigger remains `HIGH_ASSURANCE` regardless of POC stage.

#### AC-07R8 — Proportional ceremony without false proof

The POC manual path retains target-owned requirements, a sealed Context revision, a bounded
ticket, strict typing, focused verification, independent review and reviewer counter-mutation.
It may omit high-assurance host-readback ceremony only because it exposes no host effect and
names the unavailable workspace binding as a known gap. The high-assurance path retains the full
R07 adversarial workspace/profile/readback verification.

### AC-05 — Evidence-based delivery profile

`COMPACT`, `STANDARD` and `HIGH_ASSURANCE` are selected from named evidence for
change surface, coupling, ambiguity/novelty, failure impact, reversibility,
verification environment and external effects. The highest applicable ticket
risk is authoritative over the apparent project size. Missing evidence never
defaults to `COMPACT`.

### AC-06 — Non-negotiable escalation

Authentication/authorization, Secrets/credentials, payment, personal/regulated
data, destructive migration, release/deployment/signing/supply-chain work,
irreversible external effects, concurrency/distributed consistency, sandbox
escape, Native Bridge/IPC/Extension capability and privileged XSS force
`HIGH_ASSURANCE`. Existing security and authority gates remain mandatory for
all profiles.

### AC-07 — Adaptive ceremony without lost traceability

`COMPACT` may shorten sections and omit an ADR when no decision changes, but it
must still preserve a target-owned requirement, acceptance closure, owner,
workspace, first-red/green evidence, affected regression checks and independent
review. `STANDARD` uses the normal workflow. `HIGH_ASSURANCE` adds explicit
architecture alternatives, threat/failure matrices and adversarial review.

### AC-08 — Model and lane resource plan

The reviewer creates a typed resource plan with `ECONOMY`, `BALANCED` or
`FRONTIER` capability tier, an exact implementer count, budget/capability
constraints and reasons. Model names are host mappings and grant no authority.
One implementer is the default for source work; more than one requires disjoint
ticket/file ownership, independent acceptance and safe integration order.
Docs/read-only work may use zero implementers.

### AC-09 — Bounded research assistance

The default helper count is zero. Only the reviewer may create a no-code,
read-only helper for a high-search, independently bounded task. The helper has
no repository write, Git, host-effect or Agent-control capability; its output
is evidence for the reviewer, not implementation authority.

### AC-10 — Reclassification

Requirement changes, newly discovered coupling, failed verification, security
classification changes or convergence failure re-run classification. A profile
may escalate automatically; downgrade requires complete evidence and cannot
erase already required tests, findings or immutable commits.

### AC-11 — Post-POC staging lifecycle

After independent POC review and owner acceptance, Johnny freezes the exact POC
commit/version identity and requires a digest-bound `StagingTransitionPlan`
before any later feature or architecture implementation. One explicit
confirmation may create or verify the local staging ref at the accepted commit.
Remote creation/fast-forward requires separate authority, remote-history
admission and exact SHA readback. Every subsequent ticket branch/worktree must
descend from the admitted staging SHA; stale, dirty, diverged, wrong-ancestry or
mismatched refs halt before source/Git/Agent effect. Guarded integration may
advance staging but cannot overwrite the frozen POC, imply release or replace
receipt-bound disposable effect testing.

### AC-12 — Tiered model lifecycle

One versioned `ProjectWorkflowProfile` binds semantic roles to opaque model and
capability references. The current default mapping is a highest-capability
architecture owner, Terra supervisor/reviewer and Luna implementation owner;
model identity grants no authority. The architecture owner may sleep only when
the exact owner-approved SPEC revision closes public contracts, finite states,
error meanings, ownership/dependency/effect boundaries, rollback, acceptance,
delivery profile, security/XSS and UI-source classification. Missing owner
approval waits for the owner; any other open design decision keeps or wakes the
architecture owner.

### AC-13 — Low-model ticket admission

The supervisor treats the approved SPEC as immutable input and returns exactly
`READY_LOW_MODEL`, `SPLIT_REQUIRED`, `UPSTREAM_DECISION_REQUIRED` or
`HIGH_ASSURANCE_REQUIRED`. `READY_LOW_MODEL` requires one observable closure,
one implementation owner, one primary change/effect boundary, a finite named
TDD matrix, deterministic verification and zero unresolved design decisions.
Decomposition follows behavior/state/effect/ownership/verification boundaries,
never file count, line count or horizontal frontend/backend/test layers. The
strong-type preflight and identifier-only dispatch remain mandatory.

### AC-14 — Optional design-source routing

Formal UI classifies `FIGMA`, `SCREENSHOT`, `DESIGN_BRIEF`,
`EXISTING_DESIGN_SYSTEM` or `NONE` together with a finite capability state.
Authorized Figma reads are bounded to exact files/nodes/frames/variants and
required metadata/assets. Unavailable or declined Figma can use another
approved source. Missing required visual input returns
`WAIT_FOR_HUMAN / UI_DESIGN_SOURCE_REQUIRED`; inaccessible exact Figma input
returns `HALT / DESIGN_SOURCE_UNAVAILABLE` only when the approved SPEC requires
that source. UI tickets deliver complete observable component/frame slices.
Design metadata alone does not trigger XSS; runtime source-to-renderer flow does.

### AC-15 — Architecture-owned shared Context

Shared project Context is drafted only by the architecture owner during
`ARCHITECTURE`/`GRILL` and sealed at `CONTEXT` before SPEC approval. It contains stable
cross-feature facts, invariant boundaries and metadata-only artifact indexes; ticket state,
handoffs, commits, tests, findings, branches/worktrees and duplicated SPEC/policy prose are
invalid content. After sealing, every supervisor, ticket splitter/dispatcher, implementer and
reviewer receives read/reference capability only. Missing facts return
`UPSTREAM_DECISION_REQUIRED`; changed facts return `REQUIREMENT_CHANGED`. A revision requires
the architecture owner, an approved change reference and the exact prior sealed revision.

### AC-16 — Ticket-scoped Agent Context

Every Agent works from one bounded `ContextView` resolved through artifact-tree references.
Durable Router state stores identifiers/revisions/digests only. An implementation view is bound
to exactly one ticket ID/revision, receipt, owner, worktree, branch, baseline and side-context ID.
A different ticket always closes the old view and creates a fresh identity; a same-ticket
correction rebinds the exact revised ticket/review baseline. No transcript, raw packet, inferred
decision or prior-ticket resume prose crosses either boundary.

### AC-17 — Tree-shaped workflow artifact, archive, and library lineage

Every workflow/process/document artifact family uses
`root index -> bounded partition index -> exact leaf`; an index contains only direct-child ID,
kind, revision, digest, lifecycle and child-index/leaf references. This applies to requirement,
change, shared/Agent Context, SPEC, ticket, review, progress/handoff/evidence, ADR/security,
archive-library and reusable-module families. Indexes never copy leaf bodies, descendant
inventories or chat/progress prose.

Each active product requirement is a one-to-one
`PRD-YYYYMMDD-NNN <-> CHG-YYYYMMDD-NNN` leaf. A retired pair leaves every active edge and enters
one immutable `ARCH-REQ-YYYYMMDD-NNN` archive-library leaf; the current tree retains only the
archive ID/reference. The archive library is itself a bounded root/partition/leaf tree, not a
flat historical ledger. Reusable-module discovery likewise follows capability-domain indexes to
one module-card leaf and adds nested meaning/ownership partitions before unrelated siblings
would force broad loading. The Router resolves one explicit path only and never scans,
flattens, recursively loads or persists a whole tree.

### AC-17R9 — Procedural managed-artifact mutation and behavior feedback

Revision 09 makes correct index maintenance part of the managed-artifact operation instead of a
second instruction an Agent must remember. The project owner approved the exact draft at
`ef1cd4a0c74023c58e04fd44d06c58c41b8daadf`; this authorizes reviewer opening of R09A only, not
dispatch, implementation, host hooks or publication.

`CREATE`, `REVISE`, `REPLACE` and `ARCHIVE` are distinct tagged requests with no nullable
action-dependent fields. `CREATE` and `REVISE` carry one exact selected path. `REPLACE` carries
the exact current and replacement paths; `ARCHIVE` carries the exact active and archive-library
paths. The caller supplies every path explicitly. The planner never discovers a destination by
scanning, file naming, chat text, absolute path or sibling traversal.

The pure planner reads metadata only and returns either one finite rejection or a plan containing
the exact baseline, action, selected path set, leaf mutations, every directly affected parent-index
mutation and the expected post-state resolutions. The transaction boundary compares the exact
baseline, writes the complete finite plan all-or-nothing, restores every original byte after any
failure and resolves every affected candidate path before returning `APPLIED`. An orphan leaf,
dangling edge, duplicate parent/ID, cycle, stale revision/digest edge, mixed lifecycle or partial
write is never success.

The first host adapter is Codex-specific and is packaged by the plugin rather than copied into a
target `.codex/` directory. It exposes one named managed operation, refuses only direct writes it
can classify reliably, and returns `RAW_MANAGED_WRITE_DENIED` before supported effects. At Stop it
validates the exact affected path set and may emit one correction continuation. A re-entered Stop
or an already-used continuation returns `BEHAVIOR_REPAIR_EXHAUSTED`; it cannot loop or claim an
unobserved repair. Hook input is untrusted ephemeral data and may not be executed or persisted.
Durable output excludes raw command, transcript, document body, Secret, URI and absolute path.

Host behavior capability is exactly `ACTIVE`, `UNAVAILABLE` or `NOT_APPLICABLE`. `ACTIVE` requires
installed trusted/enabled configuration plus real behavior qualification. `UNAVAILABLE` names a
missing or disabled adapter and cannot be represented as enforcement. `NOT_APPLICABLE` means the
current host path does not use that adapter. Neither absence nor presence of a host adapter changes
repository authority.

Before merge, the document-mutation gate derives affected managed paths from the candidate diff and
validates only their selected direct-parent chains against candidate post-state. It rejects missing
co-mutation, invalid lifecycle and every AC-17 topology failure before Git integration. A candidate
without managed-document changes incurs no unrelated full-tree scan. Gate success, non-force push
and direct authority-ref readback remain the only `AUTHORITY_INTEGRATED` result; host feedback or an
Agent's claim never substitutes for that proof.

Delivery profile still controls which documents exist. Revision 09 adds no required document type
or count; once an artifact is required or intentionally created, the same mutation invariant applies
under `COMPACT`, `STANDARD` and `HIGH_ASSURANCE`. Plugin detach removes the adapter/control plane
only and leaves target-owned documents, indexes and Git history unchanged.

### AC-17R10 — Proposed complete mutation-state and ancestor-cascade correction

R09A ticket decomposition exposed two missing public facts in approved Revision 09. First,
`REPLACE` and `ARCHIVE` need an exact `PRESENT -> ABSENT` source transition, but the Revision 09
node mutation always requires a present `next_*` state and the existing target-document mutation
supports only create/update. Second, changing a leaf digest changes its parent-index bytes and
digest, which changes that index's parent edge; valid post-state therefore cascades through every
ancestor on the selected path up to the root, not only the nearest parent.

Revision 10 is a correction, not a new feature. The project owner approved the exact correction at
`b0a973a8a66d0dbbd88e94990eaa8dc6716b7954`; this authorizes reviewer opening of R09A only.
R09A ticket approval and every implementation/effect transition remain separate.

Every selected path snapshot has one explicit terminal state:

```text
PRESENT = path_nodes contains exactly root, every selected partition and the terminal leaf
ABSENT  = path_nodes contains exactly root and every selected partition; the final parent has no
          edge to expected_leaf_ref, and no terminal leaf node is supplied
```

Both shapes preserve explicit path order and reject missing intermediate nodes, a terminal edge in
an `ABSENT` snapshot, duplicate/cyclic/cross-family nodes, stale edge metadata and unselected nodes.
The planner never treats an earlier missing segment as terminal absence.

The action transition matrix is fixed:

| Action | Exact current state | Exact candidate state |
| --- | --- | --- |
| `CREATE` | selected destination path `ABSENT` | the same path `PRESENT` |
| `REVISE` | selected path `PRESENT` | the same leaf identity `PRESENT` with changed revision/digest and allowed lifecycle |
| `REPLACE` | current path `PRESENT`; explicit replacement path `ABSENT` | current path `ABSENT`; replacement path `PRESENT` |
| `ARCHIVE` | active path `PRESENT`; explicit archive-library path `ABSENT` | active path `ABSENT`; archive-library path `PRESENT / ARCHIVED` |

For each transition, the candidate supplies exact replacement bytes only through a tagged document
create/update mutation. A tagged delete carries only path, kind and expected current digest; it has
no content, next digest or sealed flag. The planner verifies the document digest against canonical
LF UTF-8 bytes, binds every semantic node transition to exactly one document mutation and rejects
extra or missing mutations. Existing `TargetDocumentMutation` and `TargetDocumentPlan` remain
unchanged for current consumers; R09 introduces additive managed-document variants.

Ancestor closure is deterministic. Starting at every changed terminal node, the plan updates its
direct parent edge to the candidate child kind/revision/digest/lifecycle or removes that edge for an
absent terminal. Because that index document changed, the plan repeats the same rule for its parent,
continuing only along the caller-selected path until the root mutation is included. Unselected
sibling edge metadata is copied byte-for-byte and no sibling node/body is loaded. A plan missing any
induced ancestor mutation returns `ANCESTOR_CASCADE_INCOMPLETE`; a mutation outside the selected
path set returns `UNRELATED_MUTATION`.

### AC-17R11 — Recoverable runtime transaction and canonical resolution

R09B bounded-convergence review proved that Revision 10 did not state how a durable rollback
failure, cleanup failure or uncooperative writer must be retained, nor how the runtime distinguishes
an expected resolver non-success from a runtime invariant failure. Revision 11 is a correction under
`PRD-20260828-044` / `CHG-20260828-044` and accepted `ADR-20260828-032`; it does not add host,
provider, repository-admission, release or installation authority.

The runtime owns transaction truth. Plugin/CLI input is a typed intent only. Before any filesystem
effect, the runtime independently validates the exact plan shape, `HEAD`, canonical relative path
and reparse-point containment, every expected current digest, the complete selected path transition,
and the complete candidate document/ancestor bindings. It persists a private recovery record and
snapshots under the worktree's Git metadata path, then takes the catalogued `exclusive-file-lock` for
cooperating runtime instances. The advisory lock never substitutes for revalidation against a writer
that ignores the lock.

Immediately before each replace/unlink, the runtime requires the target to still equal the recorded
baseline state. Immediately after an effect it requires the target to equal its own candidate state.
Rollback/recovery restores a target only while it still equals that runtime candidate identity; a
different current identity is preserved as an external conflict. Restore and temporary cleanup are
attempted exactly twice. Failure to prove every baseline byte/absence, zero temporary residue and
no external conflict persists the record and returns `RECOVERY_REQUIRED`; every later `apply` must
return the same state without target effects until explicit recovery proves completion.

The strict result contract adds finite `RECOVERY_REQUIRED` and `RUNTIME_INVARIANT_FAILED` outcomes
with opaque recovery identity only. Raw paths, snapshot bytes, exception text and filesystem details
never enter the result. `RUNTIME_INVARIANT_FAILED` is classified narrowly at the post-state resolver
boundary after the same recovery protocol; broad exception normalization remains forbidden.

Post-state resolution is canonical-only: existing `ArtifactTreeResolver` receives its exact family,
root ref, ordered explicit path refs and nodes. R09B must not add a string resolver, sibling scan,
fuzzy lookup or first-match behavior. If a later boundary adds an explicitly declared shorthand,
only one canonical candidate may resolve; zero and multiple candidates are finite non-successes.

### AC-17R12 — Atomic Conditional Replace capability gate

RWW6 remains unchanged. `AtomicConditionalReplace` is a runtime capability rather than an
assumption about `os.replace`, `rename`, `unlink` or the advisory `exclusive-file-lock`. R09B2 may
execute a target-document write only when the exact operating-system, filesystem backend and
filesystem abstraction have a qualification of `YES`, or `CONDITIONAL` with runtime proof that the
declared condition holds. An unqualified tuple returns a finite fail-closed refusal before any R09B2
target effect.

`YES` means an actual native primitive makes the final replacement or unlink atomically conditional
on the target still having the previously observed identity. A digest read followed by an ordinary
replacement, rename or unlink does not qualify: a lock-ignoring writer can act in that interval.
`CONDITIONAL` names every prerequisite and proves the runtime detects it; an unmatched condition is
`NO`. Evidence is specific to each Windows/Linux/backend/abstraction tuple and includes the native
primitive, race model, failure semantics and an adversarial reproduction that acts after the final
identity observation. API documentation, mocks and a different filesystem are not a substitute.

`CAP-RWW6-01` is the one evidence-only investigation authorized by this revision. It cannot repair
or reuse `f99d836`, introduce an available runtime mutation path, or weaken RWW6. If no supported
filesystem proves the capability, R09B2 remains blocked and the Router returns to architecture/SPEC
for a second explicit decision.

### AC-17R13 — Remote Authority Commit route

Revision 13 retains RWW6 and replaces only the unavailable local-filesystem route. A managed
artifact runtime may not alter the target worktree, index, local HEAD, local refs or remote-tracking
refs. It may construct one complete candidate Git commit from a direct authority-ref observation,
then ask the declared remote authority service for one non-force, fast-forward-only update of that
same full ref. The candidate has the directly observed authority SHA as its sole parent and carries
every canonical planned document mutation in one tree.

The remote authority ref is the conditional identity: a competing writer that advances it after
observation causes this candidate update to fail as `STALE_AUTHORITY`, without a target effect.
Success is only `AUTHORITY_INTEGRATED` after direct remote readback of that full ref equals the
candidate SHA. Transport/policy/credential absence, rejection or ambiguous delivery yields a
finite fail-closed result (`REMOTE_AUTHORITY_UNAVAILABLE`, `REMOTE_POLICY_REJECTED`,
`STALE_AUTHORITY` or `PUSH_UNCONFIRMED`); it does not authorize implicit fetch/rebase/merge,
retry, local fallback, force push, ref delete or reset.

Qualification also proves that force, ref delete and ordinary bypass updates are rejected for the
qualified authority identities. Without that policy an authority ref may return to a previously
observed SHA, creating an ABA gap that a candidate-parent check cannot detect. An unproved policy
is `REMOTE_POLICY_REJECTED` before any candidate construction or remote effect.

The route is provider-neutral. It must consume the existing declared authority-line contract and
credential-free remote identity, while keeping credentials out of typed results, Router state,
telemetry, logs and prompts. A provider-specific expected-head API may be one adapter only after
separate proof. A local bare-repository fixture, a Git API name, a prior fetch or a different
remote is not qualification for the actual declared authority remote.

The first Revision 13 successor is evidence-only `CAP-REMOTE-AUTHORITY-01`. It proves, on the
actual declared authority remote and an owner-authorized isolated test ref/repository, two
independent direct-child candidates from the same observed base: no more than one can integrate;
the losing attempt preserves the winning complete tree and returns a finite outcome; every result
is resolved by direct remote readback. Only a proved remote contract may later admit the new
remote-commit writer. R09B2 and `f99d836` are superseded local-path evidence and are not repair
authority.

## Typed contracts

```text
DeliveryProfile = COMPACT | STANDARD | HIGH_ASSURANCE
ImplementationModelTier = ECONOMY | BALANCED | FRONTIER
ResearchSupport = NONE | REVIEWER_OWNED_READ_ONLY
StagingRefState = ABSENT | EXACT_ACCEPTED_POC | VERIFIED_FAST_FORWARD
RemotePublicationMode = LOCAL_ONLY | CREATE_REMOTE | FAST_FORWARD_REMOTE
ModelRole = ARCHITECTURE_OWNER | SUPERVISOR_REVIEWER
          | IMPLEMENTATION_OWNER | RESEARCH_HELPER
RoleActivityState = ACTIVE | SLEEPING | WAKE_REQUIRED
SpecificationReadinessDecision = READY_FOR_SUPERVISION
                               | ARCHITECTURE_OWNER_REQUIRED
                               | OWNER_APPROVAL_REQUIRED
TicketDecompositionDecision = READY_LOW_MODEL | SPLIT_REQUIRED
                            | UPSTREAM_DECISION_REQUIRED
                            | HIGH_ASSURANCE_REQUIRED
DesignSourceKind = FIGMA | SCREENSHOT | DESIGN_BRIEF
                 | EXISTING_DESIGN_SYSTEM | NONE
DesignCapabilityState = AVAILABLE_AUTHORIZED | AVAILABLE_NOT_AUTHORIZED
                      | UNAVAILABLE | DECLINED
SharedContextOperation = CREATE_DRAFT | REVISE_DRAFT | SEAL | READ_REFERENCE
SharedContextLifecycle = ABSENT | ARCHITECTURE_DRAFT | SEALED
SharedContextMutationDecision = ALLOW | REQUIRE_CHANGE_CONTROL
                              | FORBID_ROLE_OR_STAGE | STALE_REVISION
ArtifactNodeKind = ROOT_INDEX | PARTITION_INDEX | LEAF
ArtifactLifecycle = ACTIVE | CLOSED | ARCHIVED
ArtifactFamily = REQUIREMENT_CHANGE | SHARED_CONTEXT | AGENT_CONTEXT
               | SPECIFICATION | TICKET | REVIEW | PROGRESS_EVIDENCE
               | ADR_SECURITY | ARCHIVE_LIBRARY | REUSABLE_MODULE
ArtifactTreeDecision = RESOLVED | ARTIFACT_TREE_INVALID | ARTIFACT_PATH_NOT_FOUND
AgentContextKind = ARCHITECTURE | SUPERVISION | IMPLEMENTATION | RESEARCH
AgentContextLifecycle = OPEN | CLOSED | INVALIDATED
RequirementLifecycle = ACTIVE | ARCHIVED
JohnnyTicketWorkspaceStorageLifecycle = REGISTERED | DETACHED | REMOVED

DeliveryAssessment = {
  project_id, ticket_ref?, change_surface, coupling, ambiguity,
  failure_impact, reversibility, verification_environment,
  external_effects, escalation_triggers, evidence_refs
}

ImplementationResourcePlan = {
  delivery_profile, model_tier, implementer_count,
  independent_lane_refs, research_support, budget_ceiling_ref,
  host_capability_refs, rationale_refs
}

ProjectInitializationPlan = {
  project_id, repository_identity_ref, expected_base,
  target_artifact_manifest, johnny_ticket_workspace_storage_ref,
  reviewer_profile_ref, host_capability_refs, plan_digest
}

JohnnyTicketWorkspaceStorageRef = {
  storage_ref, project_id, ownership_ledger_ref,
  root_identity_digest, lifecycle
}

HostTaskReservationLifecycle = IDLE_RESERVED | BOUND | RELEASED
HostCapabilityReadbackStatus = VERIFIED | CAPABILITY_UNAVAILABLE
                             | PAYLOAD_INVALID | PROJECT_REQUIRED
                             | TASK_NOT_READY | PROFILE_UNVERIFIED
                             | PROFILE_MISMATCH
WorkspaceIdentityVerificationStatus = VERIFIED | TASK_WORKSPACE_MISMATCH
                                      | GIT_METADATA_UNAVAILABLE
                                      | WORKTREE_UNREGISTERED | BASELINE_MISMATCH
ReceiptBoundHostAdmissionStatus = ADMITTED | REVIEWER_FORBIDDEN
                                 | RECEIPT_UNAVAILABLE | DESCRIPTOR_MISMATCH
                                 | REPLAY_DETECTED | CAPABILITY_UNAVAILABLE
                                 | TASK_WORKSPACE_MISMATCH
                                 | REVIEWER_CAPABILITY_INSUFFICIENT

HostTaskReservationRequest = {
  reviewer_capability_ref, approved_artifact_ref, receipt_ref,
  expected_project_ref, expected_worktree_ref, expected_branch_ref,
  expected_baseline_ref, implementation_profile_ref, correlation_ref
}

HostTaskReservationReadback = {
  reservation_ref, host_ref, project_ref, task_ref, lifecycle,
  reservation_evidence_ref, observation_digest
}

HostCapabilityReadbackRequest = {
  reservation_ref, expected_host_ref, expected_project_ref, expected_task_ref,
  expected_profile_ref, expected_effort_ref, minimum_capability_rank
}

HostCapabilityObservation = {
  host_ref, project_ref, task_ref, effective_profile_ref,
  effective_effort_ref, verified_capability_rank, capability_evidence_ref,
  observation_digest
}

HostCapabilityReadbackResult = {
  status, observation?, failure?
}

WorkspaceIdentityVerificationRequest = {
  host_observation_ref, expected_project_ref, expected_worktree_ref,
  expected_branch_ref, expected_baseline_ref, transient_workspace_root
}

WorkspaceIdentityProof = {
  project_ref, workspace_ref, worktree_ref, branch_ref, baseline_ref,
  filesystem_identity_ref, git_metadata_ref, evidence_digest
}

WorkspaceIdentityVerificationResult = {
  status, proof?, failure?
}

ReceiptBoundHostAdmissionRequest = {
  reviewer_capability_ref, approved_artifact_ref, active_receipt_ref,
  descriptor_ref, correlation_ref, host_observation_ref,
  workspace_proof_ref, implementation_profile_ref, reviewer_profile_ref
}

ReceiptBoundHostAdmissionResult = {
  status, downstream_delivery_capability_ref?, failure?
}

StagingTransitionPlan = {
  project_id, repository_identity_ref, accepted_poc_commit,
  expected_staging_ref, expected_staging_state,
  frozen_version_record_ref, remote_publication_mode,
  remote_history_ref?, plan_digest
}

ModelRoleAssignment = {
  project_profile_ref, role, model_ref, capability_refs,
  activity_state, evidence_refs
}

SpecificationReadinessAssessment = {
  project_profile_ref, specification_ref, specification_revision,
  owner_approval_ref?, closed_contract_refs, classification_refs,
  decision, wake_reason?
}

TicketAdmissionAssessment = {
  specification_ref, ticket_ref, closure_ref, owner_ref,
  change_effect_boundary_ref, tdd_matrix_ref, verification_ref,
  open_decision_refs, decision
}

UIImplementationContract = {
  design_source_kind, design_capability_state, design_source_ref?,
  component_frame_ref, semantic_dom_ref, state_matrix_ref,
  responsive_ref, token_asset_refs, accessibility_ref,
  visual_acceptance_ref, xss_classification_ref
}

SharedContextMutationRequest = {
  project_id, context_ref, expected_revision?, candidate_revision?,
  candidate_content_digest?, content_kind_refs, operation, actor_role,
  actor_capability_ref, process_stage, approved_change_ref?
}

AgentContextLease = {
  lease_ref, project_id, context_kind, lifecycle, actor_role, actor_capability_ref,
  artifact_path_refs, ticket_ref?, ticket_revision?, receipt_ref?, owner_ref?,
  worktree_ref?, branch_ref?, baseline_revision?, side_context_id, invalidation_refs
}

ArtifactChildRef = {
  child_id, child_kind, revision, content_digest, lifecycle, target_ref
}

ArtifactIndexNode = {
  node_id, family, node_kind, revision, content_digest, lifecycle, child_refs
}

ArtifactPathResolution = {
  family, root_ref, explicit_path_refs, expected_leaf_ref,
  decision, resolved_leaf_ref?, invalid_reason?
}

ManagedArtifactAction = CREATE | REVISE | REPLACE | ARCHIVE
ManagedArtifactCapabilityState = ACTIVE | UNAVAILABLE | NOT_APPLICABLE
ManagedArtifactPlanDecision = PLANNED | ARTIFACT_PATH_NOT_FOUND
                            | PARENT_INDEX_NOT_FOUND | EDGE_STATE_MISMATCH
                            | DUPLICATE_PARENT | LIFECYCLE_CONFLICT
                            | BASELINE_MISMATCH | ARTIFACT_TREE_INVALID
                            | TERMINAL_STATE_MISMATCH
                            | ANCESTOR_CASCADE_INCOMPLETE
                            | DOCUMENT_MUTATION_MISMATCH
                            | UNRELATED_MUTATION
ManagedArtifactMutationStatus = APPLIED | BASELINE_MISMATCH
                              | TRANSACTION_FAILED | ARTIFACT_TREE_INVALID
ManagedArtifactHostDecision = MANAGED_OPERATION_ALLOWED
                            | RAW_MANAGED_WRITE_DENIED
                            | REPAIR_REQUIRED
                            | BEHAVIOR_REPAIR_EXHAUSTED
                            | CAPABILITY_UNAVAILABLE

ManagedArtifactTerminalState = PRESENT | ABSENT

ManagedArtifactPathSnapshot = {
  family, root_ref, explicit_path_refs, expected_leaf_ref,
  terminal_state, path_nodes
}

ManagedArtifactPathTransition = {
  current_snapshot, candidate_snapshot
}

CreateManagedArtifactRequest = {
  project_id, baseline_commit, action = CREATE,
  destination_transition, proposed_document_mutations
}

ReviseManagedArtifactRequest = {
  project_id, baseline_commit, action = REVISE,
  selected_transition, proposed_document_mutations
}

ReplaceManagedArtifactRequest = {
  project_id, baseline_commit, action = REPLACE,
  current_transition, replacement_transition, proposed_document_mutations
}

ArchiveManagedArtifactRequest = {
  project_id, baseline_commit, action = ARCHIVE,
  active_transition, archive_transition, proposed_document_mutations
}

ManagedArtifactRequest = CreateManagedArtifactRequest
                       | ReviseManagedArtifactRequest
                       | ReplaceManagedArtifactRequest
                       | ArchiveManagedArtifactRequest

ManagedArtifactNodeState = AbsentNodeState { state = ABSENT }
                         | PresentNodeState {
                             state = PRESENT, revision, digest, lifecycle
                           }

ManagedArtifactNodeMutation = {
  artifact_ref, expected_state, next_state
}

ManagedDocumentCreate = {
  mode = CREATE, path, artifact_kind, content, content_digest, sealed
}

ManagedDocumentUpdate = {
  mode = UPDATE, path, artifact_kind, expected_current_digest,
  content, content_digest, sealed = false
}

ManagedDocumentDelete = {
  mode = DELETE, path, artifact_kind, expected_current_digest
}

ManagedDocumentMutation = ManagedDocumentCreate
                        | ManagedDocumentUpdate
                        | ManagedDocumentDelete

ManagedArtifactPlan = {
  project_id, baseline_commit, action, path_transitions,
  node_mutations, document_mutations, expected_post_state_snapshots
}

RequirementLineageRef = {
  prd_ref, change_ref, lifecycle, active_leaf_ref?, archive_bundle_ref?,
  replacement_prd_ref?, replacement_change_ref?, revision, content_digest
}
```

All persisted forms are metadata-only and contain opaque references rather
than raw project paths, source, prompts, Secrets or PII.

For each `*Result`, success requires its one named success value and every
success payload; every non-success value requires exactly one matching failure
and no success payload. Optional fields above are nullable only in the matching
finite result shape; they are not dynamic/default values. All public DTOs are
frozen, strict and extra-free Python 3.11 contracts.

Host-gateway admission evaluates in this fixed order: strict request shape;
reviewer capability; exact approved artifact and active receipt; descriptor and
correlation/replay identity; idle-reservation lifecycle; exact host/project/task
readback; effective profile/effort/rank; three-part workspace proof; then
`ADMITTED`. A failure at any position returns its named status and exposes no
later capability. The delivery port is therefore unreachable before all prior
checks succeed.

## TDD and review closure

1. Installation proves zero target-project/Git/task effects.
2. Initialization rejects wrong repository identity, dirty/stale base, missing
   confirmation, altered plan digest, path escape/reparse, foreign workspace,
   unsupported reviewer activation and replay before effect.
3. Exact confirmed initialization writes only the approved target-owned artifact
   manifest and an external opaque project/storage mapping, then reads back the
   reviewer binding; retry is idempotent. Target bytes and Git status differ only
   by the explicitly listed project artifacts: no `.gitignore`, `.johnny`,
   `.johnny-router`, plugin manifest, runtime, cache, telemetry or worktree path
   is added.
4. Workspace-creation tests prove no target ref/config/index/object/worktree
   metadata change, no linked common Git directory, no hardlink/object-sharing
   dependency and no persisted raw target-path remote. The isolated checkout is
   bound to the exact baseline commit, and target integration remains a separate
   guarded effect.
5. Classification tables cover every factor and hard escalation trigger;
   missing/constructed/extra/null/wrong finite values fail closed.
6. A tiny but privileged-XSS/payment/Secret example selects
   `HIGH_ASSURANCE`; a large generated but local reversible change cannot gain
   more implementers without disjoint ownership evidence.
7. Resource plans reject unavailable model tiers, zero implementers for source
   work, overlapping lanes, excessive counts, implementation-owned helpers and
   copied/replayed authority.
8. Reverse mutations must expose removal of each hard escalation rule,
   default-one implementer, disjoint-lane gate, reviewer-only helper ownership,
   plan-digest binding and exact workspace-root validation.
9. Review must independently verify the selected profile against the actual
   diff/risk, not merely accept the Router label.
10. Post-POC transition rejects an unreviewed/ambiguous POC commit, altered plan,
   dirty or stale base, wrong ancestry, unexpected local/remote ref, divergence,
   force/reset/delete semantics and mismatched SHA readback before effect.
11. Every later ticket rejects a branch/worktree not descended from its exact
    admitted staging SHA. Tests independently prove that staging integration
    cannot mutate the frozen POC/version record or claim release, and that
    disposable environment success cannot grant Git baseline authority.
12. SPEC-readiness tests reject missing owner approval and every independently
    omitted contract/classification field; only the exact complete revision can
    put the architecture owner to sleep.
13. Wake-routing tests cover ambiguous/contradictory SPEC, undefined contract,
    architecture/cross-ticket conflict, requirement change, unprovable AC, new
    external boundary, hard assurance trigger and bounded model insufficiency.
14. Ticket-admission tests cover each missing closure dimension, multi-owner or
    multi-effect slices, horizontal split and unresolved decisions. Reverse
    mutation of every admission gate changes `READY_LOW_MODEL` to the exact
    non-ready decision.
15. UI-source tests cover every source/capability combination, exact Figma
    required/unrequired distinctions, fallback, human wait and halt. XSS remains
    based on runtime source/sink data rather than design-source kind.
16. Every new decision returns the exact versioned policy reference and expected
    typed return. Missing, stale or competing route references halt before
    capability, task, worktree, Git or host effect.
17. Shared-Context tests admit create only in the early architecture sequence,
    admit revision only with architecture ownership, exact prior revision and
    approved change authority, and reject every ticket/supervisor/implementation/
    review write before filesystem effect. Content-schema tests reject progress,
    ticket, commit, test and review material without using a line-count limit.
18. Agent-Context tests prove a different ticket, ticket revision, receipt, owner, worktree,
    branch or baseline invalidates the prior view before source/Agent effect. Same-ticket
    correction requires an exact revised binding; closed/invalidated views cannot be replayed.
19. Generic artifact-tree tests cover every declared process/document family and reject cycles,
    duplicate parents/IDs, dangling child refs, stale revision/digest edges, leaf bodies in
    indexes, recursive flattening and cross-root aliases. Requirement-lineage tests reject
    active/archive overlap, unmatched PRD/CHG suffixes and archived leaves reachable through an
    active edge. Archive/reusable-library tests prove bounded direct-child indexes and load only
    the selected partition/card/archive branch.
20. Revision 07 tests construct every public host-gateway DTO through ordinary validators and
    reject extra/unknown states, nullability violations, bypass constructors, path-only proof,
    stale/absent profile evidence, lower-rank reviewer, active-task reservation, receipt replay,
    descriptor mismatch and directory/readback drift. Reverse mutations must prove that removing
    each of the three workspace checks, accepting an asserted profile, or exposing delivery before
    `ADMITTED` turns the closure red. The current host's missing effective-profile readback must
    produce the named no-effect `CAPABILITY_UNAVAILABLE` result.
21. Revision 08 tests prove that a POC no-effect ticket records the exact known workspace-binding
    gap and still requires document-gate plus reviewer counter-mutation evidence; it must reject
    a claim that the gap proves host binding, receipt delivery, runner activation or automatic
    wake. A `HIGH_ASSURANCE` ticket with the same missing/asserted/stale/mismatched/lower-rank
    readback must reject before any source or Agent-control effect.
22. Revision 09 tests construct every tagged managed-artifact request and public result through
    ordinary validators; prove exact-path planning without sibling discovery; force failure after
    each leaf/index write and verify byte-exact rollback; and reject stale baseline, orphan,
    dangling, duplicate-parent/ID, cycle, stale metadata and mixed lifecycle post-state. Official
    Codex hook fixtures prove supported raw-write refusal, exactly one Stop repair and exhaustion;
    missing/disabled hooks return `UNAVAILABLE`. Repository-gate counter-mutations remove one
    required parent co-mutation and one archive/replacement edge and must turn red before merge.
    Detach qualification proves target documents and indexes are unchanged.
23. Revision 10 correction tests cover all four action rows with ordinary tagged constructors;
    distinguish terminal absence from a missing intermediate path; and reject contradictory
    present/absent node and create/update/delete document shapes. A leaf digest mutation must induce
    every selected ancestor index mutation through the root while leaving sibling metadata exact.
    Reverse mutations omit one grandparent update, accept an earlier missing segment as terminal
    absence and add content to a delete; each turns its governing test red and restores green.
24. Revision 11 tests create a real recovery record before the first effect; force durable restore
    and cleanup failure; prove the two-attempt bound, preserved private recovery evidence,
    `RECOVERY_REQUIRED` and zero later apply effects; and prove an explicit recovery clears the
    active record only after exact restoration. Independent-process cooperating lock contention,
    an uncooperative interleaved writer, pre-effect CAS, post-effect CAS and rollback conflict each
    preserve external bytes rather than restoring stale data. Tests construct resolver input only
    from canonical path tuples, reject an ambiguous shorthand seam without first-match selection,
    and distinguish finite resolver decisions from the narrow runtime-invariant failure result.
25. Revision 12 capability tests qualify Windows, Linux and the current filesystem abstraction as
    `YES`, `NO` or `CONDITIONAL` with exact native primitive, race model and failure semantics. A
    claimed `YES` must reproduce a lock-ignoring mutation strictly after the last identity
    observation and prove the final mutation does not overwrite it. A reverse mutation that treats
    digest-check-plus-ordinary-replace/unlink as `YES` turns red. Missing platform/backend proof is
    `NO`, not a skipped or assumed success, and causes no R09B2 target effect.
26. Revision 13 tests prove that a complete candidate tree has exactly one directly observed
    authority parent, that its only authority transition is non-force and fast-forward-only, and
    that a two-writer same-base race preserves the first accepted remote tree while the stale
    candidate has no target effect. They reject a local worktree write, local-ref mutation,
    force/ref-delete/reset path, implicit retry/rebase/merge, claimed `AUTHORITY_INTEGRATED`
    without exact direct remote readback, and actual-remote qualification inferred from a fixture
    or different remote. They also reject a claimed capability without direct policy evidence that
    force, ref delete and ordinary bypass updates are unavailable for qualified identities. An
    ambiguous delivery remains `PUSH_UNCONFIRMED` until readback.

## Candidate vertical ticket sequence

Only the Router phase below is currently authorized for formal tickets. Each
item is a separate low-model-admitted closure and must pass independent review
before its dependent starts:

1. Versioned skill-reference and expected-return Router contracts.
2. R02A shared-Context lifecycle and mutation-authority gate.
3. R02B ticket-scoped Agent-Context lease and invalidation gate.
4. R02C1 generic workflow artifact topology and exact-path resolution gate.
5. R02C2 active PRD/CHG retirement and archive-lineage gate.
6. R02C3 bounded archive/reusable-library index and selection gate.
7. R03 SPEC-readiness plus model-role sleep/wake decision kernel.
8. R04 low-model ticket-admission decision kernel.
9. R05 optional UI design-source decision kernel.
10. R06 integrated Profile/Router acceptance across references, Context authority, wake, admission and
   metadata-only serialization.

Initialization, project-neutral isolated-workspace lifecycle, legacy-worktree
migration, post-POC staging, installer
composition and packaging remain later phases and are not ticket-authorized by
this revision. The completed 06G0P return remains immutable but its independent
review/integration and dependent 06G tickets are paused until Router acceptance.

Revision 07 authorizes reviewer decomposition only. Its first candidate must be a
no-effect strict-contract/readback closure; that candidate still requires its own
approved ticket and receipt before any implementation lane. Host-task reservation
and identifier-only delivery remain subsequent serial closures and require their
own approved tickets and receipts.

Revision 09 is approved. The reviewer may decompose only this serial closure set; each item still
requires its own approved ticket before dispatch:

1. R09A — the pure tagged-request planner returns one complete
   present/absent path-transition plan, including every induced selected ancestor mutation through
   root, or one finite no-effect rejection.
2. R09B — the Revision 11 successor closure is serial: R09B1 supplies its strict public outcome
   contracts, then `CAP-RWW6-01` qualifies Atomic Conditional Replace before R09B2 may own the
   recoverable transactional writer. R09B2 applies one admitted plan only on a qualified tuple,
   persists private recovery evidence before its first effect, and proves every affected candidate
   path through the existing resolver before success. Legacy R09B and the non-integrated R09B2
   candidates remain blocked and are never dispatch authority.
3. R09C — repository admission derives affected managed paths from candidate diff and rejects an
   invalid candidate tree before integration without scanning unrelated source-only candidates.
4. R09D — Codex plugin adapter routes the managed operation, reliably classifiable direct-write
   refusal and one bounded Stop repair without becoming repository authority.
5. R09E — installed qualification proves `ACTIVE`, `UNAVAILABLE` and `NOT_APPLICABLE` honestly,
   including detach behavior, against a disposable target repository.

Revision 13 replaces only the unfinished local R09B2 portion:

1. `CAP-REMOTE-AUTHORITY-01` proves the actual declared remote's non-force conditional authority
   transition through an owner-authorized isolated effect target. It changes no production target
   document and creates no runtime writer.
2. A later R09B remote-authority writer ticket may consume only that exact proof. It constructs a
   full candidate commit and handles direct-readback, stale and unconfirmed results; it has no
   local target-worktree write capability.
3. R09B2 is superseded on approval and its candidates remain non-integrated evidence. R09C–R09E
   remain unopened and receive no authority from this draft.

Plugin payload regeneration, pinning, publication and installation are a later, separately
authorized effect ticket after R09A-R09E source closure. A provider adapter for Claude or another
host is not part of Revision 09.

## Approval

The project owner approved the product direction and post-POC staging
requirement on `2026-08-13`, approved the tiered model/decomposition/UI
direction and Router-first implementation on `2026-08-14`, and required
architecture-owned sealed shared Context, ticket-scoped Agent Context and bounded trees for every
workflow/process/document family, including recursively bounded archive and reusable libraries,
on `2026-08-15`. Revision 05 authorizes only AC-12 through AC-17 together with the Router portions
of AC-05 through AC-10 and the ten Router ticket candidates above. Exact
initialization and staging implementation tickets under AC-01 through AC-04 and
AC-11 remain `OWNER_REVIEW_REQUIRED`.

This approval does not rewrite historical POC evidence, review/integrate 06G0P,
authorize target-project mutation, or authorize push, package, install, release
or deployment. Every Router implementation still requires its own committed
ticket, receipt, named implementation owner and independent review.

Revision 06 was approved by the project owner on `2026-08-15` under
`CHG-20260815-024` and `ADR-20260815-013`. It replaces only the target-local
worktree/ignore-path semantics in AC-01 through AC-04 and their contracts/tests;
it does not reopen or broaden the approved Revision 05 Router phase. The
reviewer may now decompose this exact isolation closure into independently
admitted tickets. This approval creates no dispatch receipt and grants no
source, target-Git, migration/cleanup or external-effect authority.

Revision 07 was approved by the project owner on `2026-08-22` under
`CHG-20260822-031`, bounded by `CTX-HOST-GATEWAY-20260822-01` and
`TAD-ADAPTIVE-R06-ISOLATION-01`. The approved draft-content baseline is
`1897339679312d92944403747aa7a2b1595d9c3e`; this approval record adds only the
seal and authority transition. It supplies the missing host capability/readback,
workspace-identity and receipt-bound admission algebra for AC-03/AC-04. It seals
the Context and authorizes reviewer decomposition of the first no-effect ticket
only; it neither opens an implementation lane nor authorizes any host, workspace,
task, receipt, source or external effect.

Revision 08 was approved by the project owner on `2026-08-23` under
`CHG-20260822-032`, bounded by `CTX-EXECUTOR-ROUTING-20260823-02` and
`CTX-HOST-GATEWAY-20260823-02`. It returns the P8R pure resolver to a POC/
`STANDARD` manual-evidence route, preserves R07 as a separate `HIGH_ASSURANCE` host boundary,
and authorizes reviewer decomposition of the replacement P8R ticket only. It does not authorize
host, task, workspace, receipt, runner, provider, source or external effects.

Revision 09 was drafted after the project owner accepted `ADR-20260828-031` at candidate commit
`4a43b182b2913b1ea9a00b8dbec212eb84c89a33`. The project owner then approved the exact Revision 09
draft at `ef1cd4a0c74023c58e04fd44d06c58c41b8daadf`. This authorizes reviewer creation of the R09A
ticket only. It does not approve that ticket, open a dispatch lane or authorize hook, publication
or installation effects.

Revision 10 was drafted after R09A decomposition proved that approved Revision 09 could not express
delete/absence and did not explicitly close digest propagation through all selected ancestors. The
project owner approved the exact correction at
`b0a973a8a66d0dbbd88e94990eaa8dc6716b7954`. It is a fail-closed contract correction under the same
`PRD-20260828-043` / `CHG-20260828-043`; it does not change the owner-approved feature direction.
Only reviewer opening of R09A is now authorized; ticket approval and dispatch remain separate.

Revision 11 records the project owner's recovery, runtime trust-boundary and canonical-resolution
decisions under `CHG-20260828-044` / `ADR-20260828-032`. It supersedes no completed R09A behavior
and preserves the blocked R09B candidates as evidence. The project owner approved the exact Revision
11 draft at `e451cf13a1defe40f5a036a09805dcfc20c751f2`; that first successor authority was consumed
by the completed R09B1 public-contract slice. On 2026-08-28, after accepting R09B1's recorded
evidence-ordering deviation, the owner separately authorized opening one R09B2 recoverable-writer
ticket. This does not open an implementation lane or authorize Git mutation, host adapter,
publication or installation effects.

Revision 12 records the project owner's decision to retain RWW6 and to make Atomic Conditional
Replace an explicit platform/backend capability gate under `CHG-20260828-045` / `ADR-20260828-033`.
The R09B2 candidates are blocked evidence and may not receive another implementer correction.
Only the evidence-only `CAP-RWW6-01` ticket is authorized; it does not make a runtime mutation path
available until its exact qualification is independently accepted.

Revision 13 is approved after the owner selected Remote Authority Commit as the second architecture
decision under `CHG-20260829-046` / `ADR-20260829-034`. It replaces the local-filesystem mutation
route only, preserves RWW6 and authorizes reviewer opening of `CAP-REMOTE-AUTHORITY-01` only. It
requires proof of the actual remote authority contract before any remote writer ticket and grants
no source, remote-test, credential, provider, push, publication, installation, release or
deployment effect.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `72438a30a4ad698be33292de8d63a7f2dc289daf` | Drafted Revision 06 to remove target-local Johnny ignore/worktree paths under `CHG-20260815-024`; owner approval pending. |
| 2026-08-15 | Project owner | Approved the exact Project-neutral Workspace Revision 06 and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-22 | Codex architecture owner / `control/executor-routing-p8-owner-override` / `bce019090819390d4368ec68e09392508aacbd2c` | Drafted Revision 07 host-gateway workspace/profile binding amendment under `CHG-20260822-031`; owner approval pending. |
| 2026-08-22 | Project owner | Approved the exact Revision 07 draft content at `1897339679312d92944403747aa7a2b1595d9c3e`; sealed its Context and authorized reviewer decomposition of the first no-effect ticket only. |
| 2026-08-23 | Project owner / `CHG-20260822-032` | Approved Revision 08: POC manual evidence records the workspace-binding gap; R07 readback stays mandatory only for high-assurance host effects; replacement P8R decomposition is authorized. |
| 2026-08-28 | Codex architecture owner / `codex/managed-artifact-behavior-architecture` / `4a43b182b2913b1ea9a00b8dbec212eb84c89a33` | Drafted Revision 09 from accepted ADR-031 and sealed Context `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09`; exact SPEC owner approval pending. |
| 2026-08-28 | Project owner / exact candidate `ef1cd4a0c74023c58e04fd44d06c58c41b8daadf` | Approved Revision 09 procedural managed-artifact behavior and authorized reviewer opening of R09A only; ticket approval, dispatch and effects remain separate. |
| 2026-08-28 | Codex architecture owner / `control/adaptive-r09a-upstream-correction` / `c33b87cb27ca49a94cce0ae315923652a930667f` | R09A decomposition returned `UPSTREAM_DECISION_REQUIRED`; drafted Revision 10 additive mutation-state and ancestor-cascade correction, owner approval pending. |
| 2026-08-28 | Project owner / exact candidate `b0a973a8a66d0dbbd88e94990eaa8dc6716b7954` | Approved Revision 10 mutation-state and ancestor-cascade correction; authorized reviewer opening of R09A only. |
| 2026-08-28 | Codex architecture owner / `control/adaptive-r09b-recovery-architecture` / `5e351ce9d57af321dfb14c6b102e9749da7efc25` | Drafted Revision 11 recoverable runtime correction from the owner's three architecture decisions; exact SPEC owner approval pending. |
| 2026-08-28 | Project owner / exact candidate `e451cf13a1defe40f5a036a09805dcfc20c751f2` | Approved Revision 11 recoverable runtime correction; authorized reviewer opening of one R09B successor ticket only. |
| 2026-08-28 | Project owner / current owner authority | After R09B1 completed and its evidence-ordering deviation was explicitly accepted, authorized reviewer opening of one R09B2 recoverable-writer ticket only; approval, dispatch and effects remain separate. |
| 2026-08-28 | Project owner / `PRD-20260828-045` | Retained RWW6 unchanged; approved the Atomic Conditional Replace capability gate and authorized opening only `CAP-RWW6-01` before any further R09B2 implementation. |
| 2026-08-29 | Codex architecture owner / `control/adaptive-r13-remote-authority-architecture` / `eb1a818e9550589dd649a2af328f7272c185a428` | Drafted Revision 13 Remote Authority Commit after the owner selected option A; exact SPEC approval pending. |
| 2026-08-29 | Project owner / exact candidate `3453f3e5709502bff64647eb2b4d6ad0b829212a` | Approved Revision 13 Remote Authority Commit and authorized reviewer opening of `CAP-REMOTE-AUTHORITY-01` only; no remote or implementation effect authority. |
