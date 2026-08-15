# Revision 06 Project Isolation Admission Decision

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TAD-ADAPTIVE-R06-ISOLATION-01` / `TICKET_ADMISSION_DECISION` |
| Authority | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 06, AC-01 through AC-04 |
| Requirement / Context / ADR | `PRD-20260815-024` / `CHG-20260815-024` / `doc/context/adaptive-project-orchestration/main.md` / `ADR-20260815-013` |
| Decision | `UPSTREAM_DECISION_REQUIRED` |
| State | `NON_DISPATCHABLE`; this is not an implementation ticket |
| Baseline | `7e7ddea5edf1a879eda1ee29f628a945eb0424d6` |
| XSS / effects | `XSS_NOT_APPLICABLE`; no Browser/WebView/DOM/JavaScript, filesystem, Git, Agent, host, target, network or storage effect is authorized |

## Decomposition result

No independently observable vertical implementation closure can be admitted without inventing a
public contract. The approved acceptance criteria establish the isolation invariant but leave the
following contract surfaces open.

| Candidate closure | Exact missing architecture contract | Why a reviewer cannot infer it |
| --- | --- | --- |
| `AC-01/AC-02 initialization and target ownership` | The element type, allowed names, ownership proof, digest and exact validation/error algebra for `ProjectInitializationPlan.target_artifact_manifest`. | The plan may write only listed target-owned artifacts, but the list's typed shape and failure precedence are not declared. A ticket cannot define what may be written. |
| `AC-03 standalone workspace` | A strict request/result/decision contract that binds repository identity, expected baseline, workspace identity, receipt identity, ownership-ledger proof, remote-removal proof and all pre-Git halt reasons. | `JohnnyTicketWorkspaceStorageRef` identifies only a storage root and lifecycle. It does not bind the requested checkout or define the result/error mapping needed to prove AC-03 before Git effect. |
| `AC-04 reviewer-first activation` | A strict host-readback request/result/decision algebra defining capability identity, workspace identity, one-reviewer binding, replay/duplicate handling and the finite manual-handoff/block result. | AC-04 requires a finite result but does not declare its values, nullability, error precedence or Composition Root boundary. |

## Required upstream amendment

The architecture owner must add the three exact contract families above to the approved Revision 06
SPEC (or a linked approved ADR with a SPEC amendment), including named finite types, nullability,
error/decision precedence, operation-specific invariants and the Composition Root dependency
direction. It must also state whether the three closures are serial dependencies or independently
admissible after their public contracts exist.

Until that amendment is sealed, there is no source creation location, TDD first-red, resource plan,
implementation owner, worktree, branch, receipt, rollback operation or typed implementation return
to bind. Creating any of those would be a false dispatch artifact.

## Router return

`UPSTREAM_DECISION_REQUIRED / PROJECT_ISOLATION_PUBLIC_CONTRACTS_UNDEFINED`
