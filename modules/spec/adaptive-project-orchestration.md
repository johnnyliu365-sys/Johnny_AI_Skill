# Adaptive Project Orchestration Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Status | `REVISION_03 / ROUTER_PHASE_APPROVED / OTHER_PHASES_OWNER_REVIEW_REQUIRED` |
| Author / baseline | Codex control plane / current `main` |
| Context | `doc/context/adaptive-project-orchestration/main.md` |
| PRD | `PRD.md §17` |
| Requirement change / ADR | `CHG-20260813-016`, `CHG-20260813-017`, `CHG-20260814-019`, `CHG-20260815-020` / `ADR-20260813-008`, `ADR-20260813-009`, `ADR-20260814-011` |
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
   identity, status, existing Johnny artifacts, host capabilities and proposed
   local execution layout.
3. Johnny renders an exact initialization plan. One explicit confirmation
   authorizes only that plan.
4. Initialization writes the target-owned project artifacts and narrow ignore
   rule, establishes `.johnny/worktrees/` as the local execution root, and
   opens/binds the reviewer when supported. It creates no implementer yet.
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
until a target repository passes preflight and the user confirms one exact
`ProjectInitializationPlan`.

### AC-02 — Target-owned project material

After confirmation, Context, PRD, requirement changes, specifications, tickets,
progress/review evidence, tests and product source remain target-owned and
target-versioned. Johnny's `AGENTS.md`, `Workflow.md` and `CodeReview.md` remain
plugin-owned and are not copied into the target repository.

### AC-03 — Project-local execution root

Implementation worktrees are exact marker/receipt-bound children of the target
repository's ignored `.johnny/worktrees/` root. A path escape, reparse/symlink,
foreign child, dirty/stale base, ownership mismatch or non-empty unauthorized
root halts before Git or host effect. Existing worktrees are never moved by
path manipulation; adoption requires a separate verified migration or fresh
receipt-bound creation.

### AC-04 — Reviewer-first activation

Initialization creates or binds exactly one reviewer task only after host
capability and workspace identity readback. It creates no implementer.
Implementer worktrees/tasks are created or reused only by that reviewer after
a ticket-specific dispatch receipt. Unsupported automation returns a finite
manual-handoff/block result and cannot claim automatic activation.

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
SharedContextOperation = CREATE | REVISE | READ_REFERENCE
SharedContextLifecycle = ARCHITECTURE_DRAFT | SEALED
SharedContextMutationDecision = ALLOW | REQUIRE_CHANGE_CONTROL
                              | FORBID_ROLE_OR_STAGE | STALE_REVISION

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
  target_artifact_manifest, ignore_rule, execution_root_ref,
  reviewer_profile_ref, host_capability_refs, plan_digest
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
  project_id, context_ref, expected_revision?, operation, actor_role,
  process_stage, approved_change_ref?
}
```

All persisted forms are metadata-only and contain opaque references rather
than raw project paths, source, prompts, Secrets or PII.

## TDD and review closure

1. Installation proves zero target-project/Git/task effects.
2. Initialization rejects wrong repository identity, dirty/stale base, missing
   confirmation, altered plan digest, path escape/reparse, foreign workspace,
   unsupported reviewer activation and replay before effect.
3. Exact confirmed initialization writes only the manifest, ignore rule and
   owned execution root, then readbacks reviewer binding; retry is idempotent.
4. Classification tables cover every factor and hard escalation trigger;
   missing/constructed/extra/null/wrong finite values fail closed.
5. A tiny but privileged-XSS/payment/Secret example selects
   `HIGH_ASSURANCE`; a large generated but local reversible change cannot gain
   more implementers without disjoint ownership evidence.
6. Resource plans reject unavailable model tiers, zero implementers for source
   work, overlapping lanes, excessive counts, implementation-owned helpers and
   copied/replayed authority.
7. Reverse mutations must expose removal of each hard escalation rule,
   default-one implementer, disjoint-lane gate, reviewer-only helper ownership,
   plan-digest binding and exact workspace-root validation.
8. Review must independently verify the selected profile against the actual
   diff/risk, not merely accept the Router label.
9. Post-POC transition rejects an unreviewed/ambiguous POC commit, altered plan,
   dirty or stale base, wrong ancestry, unexpected local/remote ref, divergence,
   force/reset/delete semantics and mismatched SHA readback before effect.
10. Every later ticket rejects a branch/worktree not descended from its exact
    admitted staging SHA. Tests independently prove that staging integration
    cannot mutate the frozen POC/version record or claim release, and that
    disposable environment success cannot grant Git baseline authority.
11. SPEC-readiness tests reject missing owner approval and every independently
    omitted contract/classification field; only the exact complete revision can
    put the architecture owner to sleep.
12. Wake-routing tests cover ambiguous/contradictory SPEC, undefined contract,
    architecture/cross-ticket conflict, requirement change, unprovable AC, new
    external boundary, hard assurance trigger and bounded model insufficiency.
13. Ticket-admission tests cover each missing closure dimension, multi-owner or
    multi-effect slices, horizontal split and unresolved decisions. Reverse
    mutation of every admission gate changes `READY_LOW_MODEL` to the exact
    non-ready decision.
14. UI-source tests cover every source/capability combination, exact Figma
    required/unrequired distinctions, fallback, human wait and halt. XSS remains
    based on runtime source/sink data rather than design-source kind.
15. Every new decision returns the exact versioned policy reference and expected
    typed return. Missing, stale or competing route references halt before
    capability, task, worktree, Git or host effect.
16. Shared-Context tests admit create only in the early architecture sequence,
    admit revision only with architecture ownership, exact prior revision and
    approved change authority, and reject every ticket/supervisor/implementation/
    review write before filesystem effect. Content-schema tests reject progress,
    ticket, commit, test and review material without using a line-count limit.

## Candidate vertical ticket sequence

Only the Router phase below is currently authorized for formal tickets. Each
item is a separate low-model-admitted closure and must pass independent review
before its dependent starts:

1. Versioned skill-reference and expected-return Router contracts.
2. Shared-Context lifecycle and mutation-authority gate.
3. SPEC-readiness plus model-role sleep/wake decision kernel.
4. Low-model ticket-admission decision kernel.
5. Optional UI design-source decision kernel.
6. Integrated Profile/Router acceptance across references, Context authority, wake, admission and
   metadata-only serialization.

Initialization, project-local worktree lifecycle, post-POC staging, installer
composition and packaging remain later phases and are not ticket-authorized by
this revision. The completed 06G0P return remains immutable but its independent
review/integration and dependent 06G tickets are paused until Router acceptance.

## Approval

The project owner approved the product direction and post-POC staging
requirement on `2026-08-13`, approved the tiered model/decomposition/UI
direction and Router-first implementation on `2026-08-14`, and required
architecture-owned sealed shared Context on `2026-08-15`. Revision 03
authorizes only AC-12 through AC-15 together with the Router portions of
AC-05 through AC-10 and the six Router ticket candidates above. Exact
initialization and staging implementation tickets under AC-01 through AC-04 and
AC-11 remain `OWNER_REVIEW_REQUIRED`.

This approval does not rewrite historical POC evidence, review/integrate 06G0P,
authorize target-project mutation, or authorize push, package, install, release
or deployment. Every Router implementation still requires its own committed
ticket, receipt, named implementation owner and independent review.
