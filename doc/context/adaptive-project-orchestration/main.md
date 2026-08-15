# Adaptive Project Orchestration Context

| Field | Value |
| --- | --- |
| State | `REVISION_05_APPROVED / REVISION_06_APPROVED / REVISION_07_OWNER_REVIEW_REQUIRED` |
| Requirement / ADR | `CHG-20260813-016`, `CHG-20260813-017`, `CHG-20260814-019`, `CHG-20260815-020`, `CHG-20260815-022`, `CHG-20260815-024`, `CHG-20260816-025` / `ADR-20260813-008`, `ADR-20260813-009`, `ADR-20260814-011`, `ADR-20260815-013`, `ADR-20260816-014` |
| SPEC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Control owner | Codex / current `main` |

## Confirmed facts

- Johnny is an external control plane. Target-owned project documents, tickets,
  tests and product source remain in the user's repository.
- Installation cannot choose or mutate a target repository. It provides a
  README and initialization entry point; one explicit project initialization
  confirmation precedes target writes or reviewer activation.
- Target repositories contain only target-owned project artifacts and standard
  Git state. Johnny-specific ignore entries, manifests, runtime, cache,
  telemetry and worktree directories are forbidden. Ticket workspaces are
  standalone checkouts/clones under an opaque `ProjectId` mapping to a
  Johnny-owned per-user root, never linked `git worktree` entries in the
  target's common Git directory. Johnny may internally share an immutable,
  append-only content-addressed seed/object pool across its own standalone
  workspaces; target Git state never references that pool. Raw target paths are
  resolved transiently by the guarded Git boundary.
- Initialization binds exactly one architecture owner. The single project
  Senior is created or bound only after Grill/SPEC readiness near ticketing.
  Implementers are created or reused only for admitted ticket dispatch.
- A role identity is active in at most one project. A takeover may bind an exact
  existing conversation task or create a new task only after typed host readback.
- Workflow depth, implementation model capability and lane count must adapt to
  evidence of risk and complexity. Project size and source lines are not
  sufficient classifiers.
- Security, typed contracts, workspace identity, TDD, independent review and
  exact ownership are invariant across every delivery profile.
- Once the first POC is independently accepted, its exact commit/version
  identity is frozen. All later feature and architecture branches/worktrees
  derive from a verified staging SHA and return only through guarded
  integration. Staging is a development baseline, not a release assertion or
  a disposable effect-test environment.
- The highest-capability architecture owner and human owner close the SPEC. A
  typed readiness gate hands one exact approved revision to a Terra
  supervisor/reviewer, and the default implementation owner is Luna. Exact
  model IDs remain versioned Profile mappings and grant no authority.
- The supervisor may compile closed SPEC meaning into tickets but cannot infer
  requirements, public contracts, architecture or AC. Typed ambiguity/change/
  high-assurance/convergence conditions wake the architecture owner.
- Low-model admission requires one observable closure, one owner, one primary
  change/effect boundary, finite TDD, deterministic verification and zero open
  design decisions. File and line counts are not decomposition criteria.
- UI design input may be authorized Figma, screenshot, design brief or an
  existing design system. Figma is not mandatory; unavailable input waits or
  halts according to the approved SPEC. Design metadata alone is not an XSS
  trigger.
- Shared project Context is architecture-owned and sealed before SPEC. Later
  roles bind its exact revision and bounded source spans only; missing or
  changed facts return through change control and cannot be appended by a
  ticket, dispatch, implementation, monitoring or review lane.
- Every workflow/process/document artifact family is tree-indexed. Root and partition indexes
  list direct-child metadata only; one Router action follows only the branch needed for its
  exact leaf. This includes Context, SPEC, ticket, review, progress/evidence, ADR/security,
  requirement, archive and reusable-module families.
- Agent working Context is bounded by role and current closure. Implementation Context is
  single-ticket. A persistent project Implementer slot stores closed work in a target-owned
  Context Library tree, but every ticket resolves a new immutable `context_epoch_id`; prior
  ticket content never becomes implicit input to the next ticket. Repair work creates a new
  epoch that references only the exact historical ticket/commit/review leaves it needs.
- Active product requirements are one-to-one PRD/CHG leaves. Retired pairs leave the active tree
  and remain reachable only through an immutable archive-library leaf. Archive and reusable
  libraries must themselves partition as bounded trees; neither may become a flat global list.
- Initialization adopts existing same-purpose target documents and never creates an empty
  governance tree. A missing root README may be created only by an exact approved manifest and
  must explain Johnny's external, detachable relationship to the project.
- Initialization and workspace effects follow contract-first order: typed decision algebra,
  manifest validation/effect, architecture-owner readback, later Senior readback, then exact
  ticket receipt/resource/seed/workspace admission. All host/Git/path effects are injected at
  the Johnny Composition Root with closed first-failure precedence and result nullability.
- Detach/uninstall revokes live authority and removes exact ledger-proved Johnny-owned standalone
  workspaces and seed generations even when dirty. Unproved items are reported and skipped, but
  cannot block removal of the rest of the plugin or constrain a successor.

## Boundary

This Context seals the confirmed Revision 07 architecture facts for owner review. It preserves
the existing approved Router phase and Revision 06 evidence, but does not authorize new Senior
decomposition, rewrite the existing non-dispatchable admission leaf, create a receipt, move or
clean a worktree, modify a target project, package, push, release or deploy anything.
