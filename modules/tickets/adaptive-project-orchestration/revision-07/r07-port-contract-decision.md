# Revision 07 Project-neutral Orchestration Admission Decision

| Field | Value |
| --- | --- |
| Artifact / authority | `TAD-ADAPTIVE-R07-01`; Adaptive Project Orchestration Revision 07, AC-18--AC-22 |
| Requirement / Context / ADR | `PRD-20260816-025` / `CHG-20260816-025` / `CONTEXT.md` seal and `doc/context/adaptive-project-orchestration/main.md` / `ADR-20260816-014` |
| Baseline / decision | `b6183658b7c16f9b0723482cee62fe89e677ebf3` / `UPSTREAM_DECISION_REQUIRED` |
| Effects / XSS | Role binding, target-manifest, seed and workspace effects are not admitted; `XSS_NOT_APPLICABLE` |

## Missing contract that blocks vertical tickets

Revision 07 names `TargetArtifactManifestPort`, `ProjectRoleBindingPort`, `SeedGenerationStore`,
`TicketWorkspacePort` and `OwnershipLedgerPort`, but defines none of their typed request,
readback/result or failure contracts. In particular, the read-only target-artifact probe output
needed to compare pre/post state, the role-binding host readback, ownership-ledger proof and
seed-store/object-set result shapes are absent.

The value contracts do not replace those Port contracts: they cannot say which dynamic adapter
output was accepted, which exact failure won, or how a pure validator obtains evidence without
inventing a port. Any initialization, role, Context-Library, seed or workspace ticket would lack
a finite first-red, Composition Root boundary, source location and rollback proof.

## Required route

`UPSTREAM_DECISION_REQUIRED / R07_PORT_INPUT_OUTPUT_AND_FAILURE_ALGEBRA_UNDEFINED`.
Architecture must amend the SPEC with one typed request/result/decision contract per named Port,
including nullability, first-failure precedence, ownership proof and no-effect readback semantics.
No receipt, owner, source/test scope, worktree, seed or target effect is authorized now.
