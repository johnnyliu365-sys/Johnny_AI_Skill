# Adaptive Project Orchestration Context — Revision 09

| Field | Value |
| --- | --- |
| Feature cluster | `adaptive-project-orchestration` |
| Artifact | `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED / SPEC_REVISION_09_REQUIRED` |
| Authority / change | Project owner acceptance of `ADR-20260828-031`, 2026-08-28 (Asia/Taipei) / `PRD-20260828-043` / `CHG-20260828-043` |
| Replaces | `doc/context/adaptive-project-orchestration/main.md` only for the managed-artifact mutation facts introduced by this change; the prior sealed leaf remains historical evidence for all earlier revisions. |
| Accepted baseline | `4a43b182b2913b1ea9a00b8dbec212eb84c89a33` |
| Responsibility boundary | Stable behavior and ownership facts for procedural managed-artifact mutation, Codex host feedback and repository admission. |
| Forbidden changes | Ticket state, dispatch/receipt, implementation source, installed hook, target-project mutation, publication, release or provider effect. |

## Stable facts revised under CHG-20260828-043

- Correct index maintenance is a managed operation result, not a fact an Agent must remember from
  shared Context. Creating, revising, replacing or archiving a managed artifact includes its
  matching direct-parent index mutation in one exact plan and one recoverable transaction.
- The provider-neutral planner receives one caller-selected root-to-leaf metadata path and an exact
  baseline. It does not scan sibling branches, inspect a transcript, execute a command or infer an
  index from an absolute path.
- Successful mutation requires candidate post-state resolution through the existing exact-path
  artifact-tree resolver. Partial leaf/index state, stale baseline, duplicate parent, dangling
  edge, cycle, stale edge metadata or mixed lifecycle is a finite failure, never partial success.
- A host behavior adapter is an early feedback surface only. The Codex adapter may block reliably
  classifiable raw managed writes and may request one bounded Stop repair; missing, disabled or
  unsupported hook coverage remains explicit and cannot weaken repository admission.
- Repository admission is the non-bypassable authority. It derives affected managed paths from the
  candidate diff, validates only their direct-parent chains before merge and performs no unrelated
  full-tree scan for source-only candidates.
- The behavior does not increase the number of required artifacts. Delivery profile continues to
  decide artifact quantity; the same index invariant applies to each artifact that is required or
  intentionally created.
- Hook inputs are untrusted and ephemeral. Durable evidence contains only finite decisions,
  normalized repository-relative opaque identities, revisions, digests and commit identities; it
  excludes command text, transcript, source body, Secret, URI and absolute target path.
- Plugin detach removes only the host adapter and plugin control plane. Target-owned documents,
  indexes and Git history remain independently usable.

## Architecture and downstream binding

- Accepted architecture: `doc/adr/ADR-20260828-031-procedural-managed-artifact-behavior.md`.
- Effective SPEC identity remains
  `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2`;
  Revision 09 must amend AC-17 rather than create a parallel specification.
- The Revision 09 SPEC draft must close provider-neutral planning, transactional write/post-check,
  repository admission, the Codex behavior adapter and installed qualification as serial,
  independently observable responsibilities.
- No ticket may be created until the project owner approves the exact Revision 09 SPEC draft.
  Plugin publication remains a separate effect ticket even after source closure.

## Seal and provenance

- Shared Context reference: `CONTEXT.md`, `SEALED / REVISION_02`; no shared fact is copied here.
- Requirement lineage: `PRD-20260815-022` / `CHG-20260815-022`, amended by
  `PRD-20260828-043` / `CHG-20260828-043`.
- This revision was sealed by the architecture owner from the exact owner-accepted ADR proposal.
  Later stages have read/reference capability only; changed facts require a new change and Context
  revision rather than editing this leaf in place.
