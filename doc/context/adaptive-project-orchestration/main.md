# Adaptive Project Orchestration Context

| Field | Value |
| --- | --- |
| State | `SPEC_REVISION_05_APPROVED / REVISION_06_APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED / ROUTER_PHASE_ACTIVE` |
| Requirement / ADR | `CHG-20260813-016`, `CHG-20260813-017`, `CHG-20260814-019`, `CHG-20260815-020`, `CHG-20260815-022`, `CHG-20260815-024` / `ADR-20260813-008`, `ADR-20260813-009`, `ADR-20260814-011`, `ADR-20260815-013` |
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
  target's common Git directory. Raw target paths are resolved transiently by
  the guarded Git boundary.
- Reviewer activation precedes implementer provisioning. Only a reviewer with
  an exact ticket receipt may create/reuse and control implementer tasks.
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
  single-ticket and is closed/replaced on ticket switch; prior ticket content never becomes
  implicit input to the next ticket.
- Active product requirements are one-to-one PRD/CHG leaves. Retired pairs leave the active tree
  and remain reachable only through an immutable archive-library leaf. Archive and reusable
  libraries must themselves partition as bounded trees; neither may become a flat global list.

## Boundary

This context authorizes the existing Router policy phase and reviewer
decomposition of the exact approved Revision 06 project-isolation closure. It
does not create a dispatch receipt, move or clean an existing worktree, modify a
target project, review/integrate the completed 06G0P return, resume 06G0-06G4,
package, push, release or deploy anything.
