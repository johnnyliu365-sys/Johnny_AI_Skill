# Adaptive Project Orchestration Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Status | `REVISION_05_ROUTER_PHASE_APPROVED / REVISION_06_PROJECT_ISOLATION_APPROVED / REVISION_07_HOST_GATEWAY_APPROVED / REVISION_09_PROCEDURAL_MANAGED_ARTIFACT_BEHAVIOR_OWNER_REVIEW_REQUIRED / OTHER_APPROVED_SCOPES_UNCHANGED` |
| Author / baseline | Codex architecture owner / `4a43b182b2913b1ea9a00b8dbec212eb84c89a33` |
| Context | `doc/context/adaptive-project-orchestration/main.md` (prior sealed facts), `doc/context/adaptive-project-orchestration/adaptive-project-orchestration-r09-procedural-managed-artifact-behavior.md` (`SEALED / REVISION_09`) and `doc/context/host-gateway-workspace-binding/codex-desktop-readback.md` (`SEALED`) |
| PRD | `PRD-20260813-016`, `PRD-20260813-017`, `PRD-20260814-019`, `PRD-20260815-020`, `PRD-20260815-022`, `PRD-20260815-024`, `PRD-20260822-031`, `PRD-20260828-043` |
| Requirement change / ADR | `CHG-20260813-016`, `CHG-20260813-017`, `CHG-20260814-019`, `CHG-20260815-020`, `CHG-20260815-022`, `CHG-20260815-024`, `CHG-20260822-031`, `CHG-20260828-043` / `ADR-20260813-008`, `ADR-20260813-009`, `ADR-20260814-011`, `ADR-20260815-013`, `ADR-20260828-031` |
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
second instruction an Agent must remember. This amendment is `OWNER_REVIEW_REQUIRED`; it creates
no ticket or implementation authority until the project owner approves this exact SPEC revision.

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
ManagedArtifactMutationStatus = APPLIED | BASELINE_MISMATCH
                              | TRANSACTION_FAILED | ARTIFACT_TREE_INVALID
ManagedArtifactHostDecision = MANAGED_OPERATION_ALLOWED
                            | RAW_MANAGED_WRITE_DENIED
                            | REPAIR_REQUIRED
                            | BEHAVIOR_REPAIR_EXHAUSTED
                            | CAPABILITY_UNAVAILABLE

ManagedArtifactPath = {
  family, root_ref, partition_refs, leaf_ref
}

ManagedArtifactDesiredLeaf = {
  artifact_ref, next_revision, next_digest, next_lifecycle,
  replacement_bytes_ref
}

CreateManagedArtifactRequest = {
  project_id, baseline_commit, action = CREATE,
  selected_path, desired_leaf
}

ReviseManagedArtifactRequest = {
  project_id, baseline_commit, action = REVISE,
  selected_path, expected_leaf, desired_leaf
}

ReplaceManagedArtifactRequest = {
  project_id, baseline_commit, action = REPLACE,
  current_path, replacement_path, expected_current_leaf, desired_replacement_leaf
}

ArchiveManagedArtifactRequest = {
  project_id, baseline_commit, action = ARCHIVE,
  active_path, archive_path, expected_active_leaf, desired_archive_leaf
}

ManagedArtifactRequest = CreateManagedArtifactRequest
                       | ReviseManagedArtifactRequest
                       | ReplaceManagedArtifactRequest
                       | ArchiveManagedArtifactRequest

ManagedArtifactNodeBaseline = AbsentNodeBaseline { state = ABSENT }
                            | PresentNodeBaseline {
                                state = PRESENT, revision, digest, lifecycle
                              }

ManagedArtifactNodeMutation = {
  artifact_ref, expected_baseline,
  next_revision, next_digest, next_lifecycle, replacement_bytes_ref
}

ManagedArtifactPlan = {
  project_id, baseline_commit, action, selected_paths,
  leaf_mutations, direct_parent_index_mutations,
  expected_post_state_resolutions
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

Revision 09 remains a proposed amendment. After exact project-owner approval, the reviewer may
decompose only this serial closure set; each item still requires its own approved ticket before
dispatch:

1. R09A — pure tagged-request planner returns a complete leaf/direct-parent mutation plan or one
   finite no-effect rejection.
2. R09B — transactional writer applies one admitted plan atomically and proves every affected
   candidate path through the existing resolver before success.
3. R09C — repository admission derives affected managed paths from candidate diff and rejects an
   invalid candidate tree before integration without scanning unrelated source-only candidates.
4. R09D — Codex plugin adapter routes the managed operation, reliably classifiable direct-write
   refusal and one bounded Stop repair without becoming repository authority.
5. R09E — installed qualification proves `ACTIVE`, `UNAVAILABLE` and `NOT_APPLICABLE` honestly,
   including detach behavior, against a disposable target repository.

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
`4a43b182b2913b1ea9a00b8dbec212eb84c89a33`. The accepted ADR authorizes this Context/SPEC
change-control step, but it does not itself approve the exact SPEC text. Revision 09 remains
`OWNER_REVIEW_REQUIRED`; no R09 ticket, dispatch, hook, publication or installation is authorized
until the owner approves this exact draft.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `72438a30a4ad698be33292de8d63a7f2dc289daf` | Drafted Revision 06 to remove target-local Johnny ignore/worktree paths under `CHG-20260815-024`; owner approval pending. |
| 2026-08-15 | Project owner | Approved the exact Project-neutral Workspace Revision 06 and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-22 | Codex architecture owner / `control/executor-routing-p8-owner-override` / `bce019090819390d4368ec68e09392508aacbd2c` | Drafted Revision 07 host-gateway workspace/profile binding amendment under `CHG-20260822-031`; owner approval pending. |
| 2026-08-22 | Project owner | Approved the exact Revision 07 draft content at `1897339679312d92944403747aa7a2b1595d9c3e`; sealed its Context and authorized reviewer decomposition of the first no-effect ticket only. |
| 2026-08-23 | Project owner / `CHG-20260822-032` | Approved Revision 08: POC manual evidence records the workspace-binding gap; R07 readback stays mandatory only for high-assurance host effects; replacement P8R decomposition is authorized. |
| 2026-08-28 | Codex architecture owner / `codex/managed-artifact-behavior-architecture` / `4a43b182b2913b1ea9a00b8dbec212eb84c89a33` | Drafted Revision 09 from accepted ADR-031 and sealed Context `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09`; exact SPEC owner approval pending. |
