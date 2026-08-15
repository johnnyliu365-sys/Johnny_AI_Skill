# Adaptive Project Orchestration Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Status | `REVISION_05_ROUTER_PHASE_APPROVED / REVISION_06_PROJECT_ISOLATION_APPROVED / REVISION_07_APPROVED / SENIOR_DECOMPOSITION_AUTHORIZED` |
| Author / baseline | Codex control plane / current `main` |
| Context | `doc/context/adaptive-project-orchestration/main.md` |
| PRD | `PRD-20260813-016`, `PRD-20260813-017`, `PRD-20260814-019`, `PRD-20260815-020`, `PRD-20260815-022`, `PRD-20260815-024`, `PRD-20260816-025` |
| Requirement change / ADR | `CHG-20260813-016`, `CHG-20260813-017`, `CHG-20260814-019`, `CHG-20260815-020`, `CHG-20260815-022`, `CHG-20260815-024`, `CHG-20260816-025` / `ADR-20260813-008`, `ADR-20260813-009`, `ADR-20260814-011`, `ADR-20260815-013`, `ADR-20260816-014` |
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
  Secret, ownership, workspace-binding or guarded-integration gates.
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
4. Initialization writes only explicitly approved target-owned project artifacts,
   records the opaque project-to-storage mapping below the per-user Johnny root,
   and creates or binds the project's architecture owner. It does not modify
   `.gitignore`, create a Johnny path in the target, create empty governance files,
   bind the Senior before ticketing readiness, or create an implementer.
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

A path escape, reparse/symlink, target-owned object reference, mutable cross-project object,
foreign child, stale base, wrong baseline, ownership mismatch or non-empty unauthorized root
halts before Git or host effect. Johnny may maintain an internal append-only content-addressed
seed/object pool under its own per-user root. A workspace may reference only an immutable
baseline generation whose repository identity, commit, object digest and ownership ledger are
verified. The target repository never references or depends on that pool.

Initialization creates no ticket workspace. Existing linked or target-local worktrees are never
moved or deleted by path manipulation: an already valid binding may finish only its existing
ticket, and a separately reviewed migration/cleanup ticket must retire legacy target state.
Every new or replacement workspace uses the isolated root. Detach/uninstall first revokes live
receipt/task/grant authority, then deletes exact ledger-proved Johnny-owned standalone
workspaces, unreferenced generations and finally the pool, including dirty owned workspaces.
Unproved items are reported and skipped, but do not block removal of other Johnny-owned state or
constrain a successor. Target and legacy linked worktrees are never deleted.

### AC-04 — Staged project-role activation

Initialization creates or binds exactly one project architecture-owner task only after host
capability and identity readback. It creates no Senior or implementer. After Grill convergence,
sealed Context and owner-ready SPEC, the Router creates or binds exactly one project Senior near
the ticketing boundary. Implementer worktrees/tasks are created or reused only by that Senior
after a ticket-specific dispatch receipt. Unsupported activation returns a finite typed result
and cannot claim an active role.

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

### AC-18 — Project-exclusive role roster

Each `ProjectId` has at most one active `ARCHITECTURE_OWNER`, one active
`SUPERVISOR_REVIEWER` (user-facing name: Senior), and a resource-plan-bounded set of
`IMPLEMENTATION_OWNER` slots. A takeover may `CREATE_NEW` or `BIND_EXISTING` using an exact host
task/conversation identity. Readback must prove the identity, role, project, model profile,
context library and binding epoch. One active role identity cannot bind another project.

A `DIAGNOSTIC_OWNER` is an optional on-demand, read-only project slot created only by a Senior
diagnosis ticket. Its required model profile is `gpt-5.6-sol` with `xhigh` reasoning. It may read
bounded evidence and return findings but cannot write source/SPEC/ticket/Context, dispatch,
review, integrate or control another Agent. It becomes inactive after the diagnosis and has no
heartbeat.

### AC-19 — Persistent Implementer slot and Context Library

A project may reuse one logical Implementer slot/branch across sequential tickets to avoid
branch and task proliferation. The target project owns a tree-shaped Context Library indexed by
project, role slot and ticket `context_epoch_id`. Each epoch contains only exact refs/digests for
that ticket's sealed SPEC, ticket, baseline, implementation/review/handoff evidence and closure.

At model execution, the Router exposes only the current epoch leaf plus explicitly resolved
dependencies. Closing or invalidating a ticket seals the epoch and removes it from the active
view; the library retains its identifier for audit and repair. A repair ticket creates a new
epoch referencing the minimum old ticket/commit/review leaves. If the host proves the prior
epoch is excluded, the project slot may be reused; otherwise a fresh execution branch is the
fail-closed fallback.

### AC-20 — Immutable seed generations

The Johnny-owned Git seed/object pool imports only missing, verified objects. It stores no raw
target path or credential and never changes an existing generation. Each workspace binds an
exact repository identity, baseline commit, generation ID and content digest. An old ticket
continues using its original generation after newer imports. No generation or object prune is
allowed while a live receipt references it. Pool and generation cleanup is ownership-ledger
driven and follows AC-03.

### AC-21 — Minimal target initialization manifest

`ProjectInitializationPlan.target_artifact_manifest` is a finite tuple of entries containing
artifact kind, exact target-owned path, `ADOPT` or `CREATE`, expected pre-state/digest, expected
post-digest and template revision when creation applies. Existing same-purpose documents are
adopted without overwrite, merge or parallel replacement. A missing requirement is a later
docs ticket, not permission to fill a file during initialization.

No empty Context/PRD/CHG/SPEC/ticket/review tree is created. A root README is created only when
absent and explicitly present in the approved manifest. It explains setup, role/ticket flow,
project-native handoff, terminal/machine replacement, deployment separation, plugin removal and
the successor's freedom to use another workflow. `.johnny*`, receipts, telemetry, seed/cache,
runtime and workspace entries are invalid manifest entries.

### AC-22 — Revision-07 transition fence

Revision 07 is a contract correction to the prior approved project-isolation direction. It does
not retroactively alter completed Router work or the Senior's existing non-dispatchable
admission leaves. After exact owner approval, the Senior creates new admission artifacts from
the revised sealed Context/SPEC. No historical decision leaf is edited or promoted.

## Typed contracts

```text
DeliveryProfile = COMPACT | STANDARD | HIGH_ASSURANCE
ImplementationModelTier = ECONOMY | BALANCED | FRONTIER
ResearchSupport = NONE | REVIEWER_OWNED_READ_ONLY
StagingRefState = ABSENT | EXACT_ACCEPTED_POC | VERIFIED_FAST_FORWARD
RemotePublicationMode = LOCAL_ONLY | CREATE_REMOTE | FAST_FORWARD_REMOTE
ModelRole = ARCHITECTURE_OWNER | SUPERVISOR_REVIEWER
          | IMPLEMENTATION_OWNER | DIAGNOSTIC_OWNER | RESEARCH_HELPER
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
AgentContextKind = ARCHITECTURE | SUPERVISION | IMPLEMENTATION | DEBUGGING | RESEARCH
AgentContextLifecycle = OPEN | CLOSED | INVALIDATED
RequirementLifecycle = ACTIVE | ARCHIVED
JohnnyTicketWorkspaceStorageLifecycle = REGISTERED | DETACHED | REMOVED
RoleBindingMode = CREATE_NEW | BIND_EXISTING
ProjectRoleBindingDecision = ACTIVATED | ALREADY_BOUND_SAME_PROJECT
                           | ROLE_LIMIT_EXCEEDED | IDENTITY_BOUND_OTHER_PROJECT
                           | IDENTITY_UNREADABLE | CAPABILITY_UNAVAILABLE
                           | MANUAL_HANDOFF_REQUIRED | READBACK_MISMATCH
                           | RECEIPT_REPLAYED
InitializationArtifactOperation = ADOPT | CREATE
InitializationManifestDecision = VALID | TARGET_STATE_MISMATCH
                               | SAME_PURPOSE_ARTIFACT_CONFLICT
                               | JOHNNY_ARTIFACT_FORBIDDEN
                               | POST_DIGEST_MISMATCH
ContextEpochLifecycle = ACTIVE | SEALED | INVALIDATED
SeedGenerationLifecycle = ACTIVE | UNREFERENCED | REMOVED
TicketWorkspaceDecision = CREATED | REUSED | STORAGE_REF_INVALID
                        | RECEIPT_MISMATCH | BASELINE_MISMATCH
                        | SEED_GENERATION_INVALID | OWNERSHIP_MISMATCH
                        | TARGET_DEPENDENCY_DETECTED | RESOURCE_PLAN_INVALID

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
  architecture_owner_profile_ref, host_capability_refs, plan_digest
}

TargetArtifactManifestEntry = {
  artifact_kind, target_owned_ref, operation,
  expected_pre_state, expected_pre_digest?, expected_post_digest,
  template_revision?
}

TargetArtifactManifest = {
  manifest_ref, project_id, entry_refs,
  expected_repository_state_digest, manifest_digest
}

InitializationManifestValidation = {
  manifest_ref, decision, validated_entry_refs,
  failure_entry_ref?, expected_digest?, observed_digest?
}

ProjectRoleBinding = {
  binding_ref, project_id, role, binding_mode, task_ref,
  model_profile_ref, context_library_ref, binding_epoch,
  receipt_ref, expected_readback_digest, decision
}

ContextEpochRef = {
  context_epoch_id, project_id, role_slot_ref, ticket_ref,
  lifecycle, artifact_path_refs, content_digest, predecessor_refs
}

SeedGenerationRef = {
  seed_pool_ref, repository_identity_ref, generation_id,
  baseline_commit, object_set_digest, ownership_ledger_ref, lifecycle
}

TicketWorkspaceRequest = {
  project_id, ticket_ref, ticket_receipt_ref, task_ref,
  workspace_ref, branch_ref, baseline_commit, seed_generation_ref,
  workspace_storage_ref, resource_plan_ref, expected_owned_state,
  correlation_id, request_digest
}

TicketWorkspaceResult = {
  decision, workspace_ref?, branch_ref?, baseline_commit?,
  seed_generation_ref?, ownership_proof_ref?, failure_ref?, result_digest
}

JohnnyTicketWorkspaceStorageRef = {
  storage_ref, project_id, ownership_ledger_ref,
  root_identity_digest, lifecycle
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

RequirementLineageRef = {
  prd_ref, change_ref, lifecycle, active_leaf_ref?, archive_bundle_ref?,
  replacement_prd_ref?, replacement_change_ref?, revision, content_digest
}
```

All persisted forms are metadata-only and contain opaque references rather
than raw project paths, source, prompts, Secrets or PII.

### Revision-07 Composition Root and decision precedence

The Johnny launcher is the only Composition Root. It injects a read-only target-artifact probe,
`TargetArtifactManifestPort`, `ProjectRoleBindingPort`, `SeedGenerationStore`,
`TicketWorkspacePort` and `OwnershipLedgerPort`; pure validators never open paths, run Git or
control Agents directly. Dependency order is fixed:

```text
typed contracts and decision algebra
-> target initialization manifest validation/effect
-> architecture-owner readback
-> later Senior activation/readback
-> ticket receipt/resource/seed admission
-> standalone workspace effect/readback
```

Manifest validation evaluates forbidden Johnny artifact, same-purpose conflict, expected target
state and post-digest in that order before any write. Workspace admission evaluates receipt,
resource plan, storage/ownership, target dependency, seed generation and baseline in that order
before Git effect. On `CREATED`/`REUSED`, `failure_ref` is absent and all workspace/baseline/
seed/ownership fields are present; on every failure, those success fields are absent and one
sanitized `failure_ref` is present. Role activation reports `MANUAL_HANDOFF_REQUIRED` only when
the approved host mode explicitly permits a human handoff; it never claims an active binding.

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
   metadata change, no linked common Git directory, no target-owned or mutable
   cross-project object dependency and no persisted raw target-path remote. A
   Johnny-internal seed generation must be immutable, ledger-proved and bound to
   the exact baseline/digest. Target integration remains a separate guarded effect.
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
20. Role-roster tests cover create/bind/readback, both role caps, cross-project identity reuse,
    replay, mismatch, staged Senior activation, dispatch-only Implementer activation and the
    read-only diagnostic role/model profile.
21. Context-Library tests prove current-epoch-only exposure, immutable closure, ticket switch,
    correction and repair references, host exclusion readback and fresh-branch fallback.
22. Seed-pool tests reject target dependency, mutable generations, unverified/missing objects,
    stale digest, cross-project write, live-receipt prune and raw-path persistence. Detach tests
    preserve target/legacy worktrees while deleting only exact ledger-owned state.
23. Initialization-manifest tests adopt same-purpose artifacts, reject parallel/empty/Johnny
    files, reject stale pre/post digests and create the root README only when exact approved
    manifest authority exists.
24. Transition tests prove the historical Revision-06 admission leaves remain immutable and no
    Revision-07 ticket/dispatch can exist before exact owner approval and fresh Senior admission.
25. Manifest/workspace/role matrices cover every decision precedence and result-nullability
    branch, prove all effect ports are injected only by the Composition Root and reject a
    success result carrying failure fields or a failure carrying workspace authority.

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

Initialization, project-neutral isolated-workspace lifecycle, immutable seed-pool lifecycle,
project role roster, Context Library, legacy-worktree migration, post-POC staging, installer
composition and packaging remain later phases and are not ticket-authorized by
the previous Router approval alone. Approved Revision 07 now permits fresh Senior decomposition
only for its exact closures. The completed 06G0P return remains immutable but its independent
review/integration and dependent 06G tickets are paused until Router acceptance.

## Approval

The project owner approved the product direction and post-POC staging
requirement on `2026-08-13`, approved the tiered model/decomposition/UI
direction and Router-first implementation on `2026-08-14`, and required
architecture-owned sealed shared Context, ticket-scoped Agent Context and bounded trees for every
workflow/process/document family, including recursively bounded archive and reusable libraries,
on `2026-08-15`. Revision 05 authorized only AC-12 through AC-17 together with the Router portions
of AC-05 through AC-10 and the ten Router ticket candidates above. Revision 06 later approved
the named project-isolation portions of AC-01 through AC-04, and Revision 07 approves their
role/manifest/workspace corrections plus AC-18 through AC-22. Post-POC staging implementation
under AC-11 remains `OWNER_REVIEW_REQUIRED`.

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

Revision 07 was approved by the project owner on `2026-08-16` under `CHG-20260816-025` and
`ADR-20260816-014`. It authorizes the Senior to perform fresh decomposition/admission against
AC-18 through AC-22 and their Revision-07 corrections. It does not rewrite the historical
non-dispatchable leaves, create a ticket/receipt or grant dispatch, source, workspace, seed-pool,
role-binding or target-project effect authority.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `72438a30a4ad698be33292de8d63a7f2dc289daf` | Drafted Revision 06 to remove target-local Johnny ignore/worktree paths under `CHG-20260815-024`; owner approval pending. |
| 2026-08-15 | Project owner | Approved the exact Project-neutral Workspace Revision 06 and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-16 | Architecture owner / `main` / `2a8287831259243e230911e1082f0ec87895d3c5` | Drafted Revision 07 project roles, Context Library, immutable Johnny seed generations, minimal initialization and uninstall transition fence under `CHG-20260816-025`; exact owner approval pending. |
| 2026-08-16 | Project owner | Approved the exact Adaptive Project Orchestration Revision 07 and authorized fresh Senior decomposition only. |
