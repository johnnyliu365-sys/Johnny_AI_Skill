# Adaptive Project Orchestration Context

| Field | Value |
| --- | --- |
| State | `SPEC_DRAFT / OWNER_REVIEW_REQUIRED` |
| Requirement / ADR | `CHG-20260813-016`, `CHG-20260813-017` / `ADR-20260813-008`, `ADR-20260813-009` |
| SPEC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Control owner | Codex / current `main` |

## Confirmed facts

- Johnny is an external control plane. Target-owned project documents, tickets,
  tests and product source remain in the user's repository.
- Installation cannot choose or mutate a target repository. It provides a
  README and initialization entry point; one explicit project initialization
  confirmation precedes target writes or reviewer activation.
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

## Boundary

This context defines future product behavior. It does not move existing
worktrees, modify a target project, change the frozen 05S1R ticket, package,
push, release or deploy anything.
