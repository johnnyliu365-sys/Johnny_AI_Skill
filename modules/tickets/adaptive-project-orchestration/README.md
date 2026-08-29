# Adaptive Project Orchestration — Router Phase Tickets

> Approved Router scope: [adaptive-project-orchestration.md](../../spec/adaptive-project-orchestration.md)
> revision 05 / AC-12 through AC-17 and the Router portions of AC-05 through AC-10.
> This set does not authorize initialization, staging, packaging or target-project effects.

## Serial closure order

| Ticket | Observable closure | State | Dependency |
| --- | --- | --- | --- |
| [01-route-instruction-contract](01-route-instruction-contract.md) | Every Router decision carries one versioned skill reference and one exact expected typed return; technical halts use the Profile's router-control fallback. | `COMPLETE / APPROVED / INTEGRATED` | `5c3445f` |
| [02a-shared-context-lifecycle-gate](02a-shared-context-lifecycle-gate.md) | Architecture-stage draft/revise/seal and change-control-only revision admission; later roles are exact sealed-revision readers. | `COMPLETE / APPROVED / INTEGRATED` | `9bf7d340` / `PRG-20260815-469` |
| [02b-agent-context-lease-invalidation-gate](02b-agent-context-lease-invalidation-gate.md) | One implementation-owner, ticket-bound Agent Context lease; correction invalidates and ticket switch closes the old view before a fresh identity exists. | `COMPLETE / APPROVED / INTEGRATED` | `9e3d92bc` / `PRG-20260815-477` |
| [02c1-artifact-tree-resolution-gate](02c1-artifact-tree-resolution-gate.md) | Generic bounded topology and exact one-path resolution for every declared workflow artifact family. | `COMPLETE / APPROVED / INTEGRATED` | `5b887c72` / `PRG-20260815-487` |
| [02c2-requirement-retirement-archive-lineage](02c2-requirement-retirement-archive-lineage.md) | One-to-one active PRD/CHG pairing, retirement and archive-only reachability. | `COMPLETE / APPROVED / INTEGRATED` | `701df3e` / R02C2A closed |
| [02c2a-requirement-lineage-source-gate-closure](02c2a-requirement-lineage-source-gate-closure.md) | One bounded test-only ACX6 guard covers every R02C2-owned `contracts.py` declaration/helper/import boundary and proves its own three rejection mutations. | `COMPLETE / APPROVED / INTEGRATED` | `701df3e` / `PRG-20260815-496` |
| [02c3-bounded-library-selection](02c3-bounded-library-selection.md) | One selected archive/reusable-library partition path resolves to one exact eligible leaf without discovery or sibling loading. | `COMPLETE / APPROVED / INTEGRATED` | `93a66a4` / `PRG-20260815-505` |
| [03-model-role-readiness-wake](03-model-role-readiness-wake.md) | Exact SPEC readiness and architecture-owner sleep/wake decision kernel. | `COMPLETE / APPROVED / INTEGRATED` | `aa313bf` / `PRG-20260815-513` |
| `04-low-model-ticket-admission` | Four-way low-model decomposition/admission decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R03 approved/integrated |
| `05-ui-design-source-routing` | Optional design-source capability decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R04 approved/integrated |
| `06-router-policy-acceptance` | Integrated Profile/Router acceptance and metadata-only serialization closure. | `CANDIDATE / NON_DISPATCHABLE` | R01-R05 approved/integrated |
| [project-isolation](project-isolation/README.md) | Revision 06 project-isolation partition, amended by the approved Revision 07 host-gateway contract. | `R07A_BLOCKED_REQUIREMENT_CHANGED` | revision `02`; SHA-256 `9ce090d772813047f47689be76b9f80bd7bceba53659008366e9209f99f4c416`; `TAD-ADAPTIVE-R07-HOST-CAPABILITY-01` is blocked by `CHG-20260822-032` and is not an authorized implementation child |
| [09a-managed-artifact-planning-contract](09a-managed-artifact-planning-contract.md) | One pure tagged planner validates complete present/absent path transitions, document bindings and every induced selected-ancestor mutation through root. | `CLOSED / DONE / APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED` | candidate, gate result and remote readback `91da8135e301992635d716c6cefa068ad950d807`; review revision 01 |
| [09b-managed-artifact-transaction](09b-managed-artifact-transaction.md) | One managed-plan transaction writes every bound document atomically, restores exact prior bytes on any failure, and proves the candidate post-state before success. | `BLOCKED / CONVERGENCE_REVIEW_REQUIRED / MODEL_CAPABILITY_INSUFFICIENT / NOT_INTEGRATED / REVISION_11_SUCCESSOR_PENDING` | R09A integrated at `91da8135e301992635d716c6cefa068ad950d807`; review `09b-managed-artifact-transaction-code-review.md`; `PRD-20260828-044` / `ADR-20260828-032` |
| [09b1-recoverable-managed-artifact-contracts](09b1-recoverable-managed-artifact-contracts.md) | One strict, additive managed-artifact result contract represents normal outcome, runtime invariant failure and recovery-required stop without raw recovery data. | `COMPLETE / APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED / EVIDENCE_ORDERING_DEVIATION_ACCEPTED` | source `0b48120ed145a3c9a43989e2b353d2611a6f3052` is on `origin/main`; all technical review evidence is green and the owner accepted the recorded post-integration counter-mutation timing deviation |
| [09b2-recoverable-managed-artifact-writer](09b2-recoverable-managed-artifact-writer.md) | Superseded local runtime writer proposal; its recoverable-file design remains defect evidence only. | `SUPERSEDED / LOCAL_FILESYSTEM_MUTATION_ROUTE_RETIRED / NOT_INTEGRATED` | Approved Revision 13 selects Remote Authority Commit after all executed local tuples qualified `NO`; do not correct `f99d836` |
| [cap-rww6-01-atomic-conditional-replace-capability](cap-rww6-01-atomic-conditional-replace-capability.md) | One evidence-only qualification determines whether the exact Windows, Linux and current filesystem-abstraction tuples can atomically condition final mutation on an observed identity. | `COMPLETE / APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED / ALL_EXECUTED_TUPLES_NO / ARCHITECTURE_DECISION_REQUIRED` | gate/push/readback candidate `5763caf5dc26e382dd8092545fde053063792a37`; no result grants R09B2 repair authority |
| [cap-remote-authority-01-remote-authority-commit-capability](cap-remote-authority-01-remote-authority-commit-capability.md) | Evidence-only proof or fail-closed refusal of the Revision 13 Remote Authority Commit route on the declared authority remote and the owner-authorized isolated remote target. | `BLOCKED / REQUIREMENT_CHANGED / CANDIDATE_NOT_INTEGRATED` | Review `CR-CAPREMOTE-01` found a host-protected one-shot external-effect-grant requirement outside this ticket boundary; candidate `6783385` and the consumed/unretained first attempt are evidence only. |

R02C1, R02C2, R02C2A, R02C3 and R03 are complete. R04 is the next serial candidate, but it
remains `CANDIDATE / NON_DISPATCHABLE` until its own approved ticket freeze, handoff and receipt
registry exist. Candidate labels are not implementation authority.

R09A begins the separate Revision 10 managed-artifact sequence and does not reopen, replace or
authorize the legacy Router R04 candidate. R09A is closed. R09B is blocked after its one bounded
Luna correction review and is not integrated. Revision 11 is approved and authorizes reviewer
opening of one successor ticket only. R09B1 is that successor's contract-first vertical slice;
its source and closure are integrated after the owner accepted the recorded evidence-ordering
deviation. `CAP-RWW6-01` is complete: every executed tuple qualified `NO`. Approved Revision 13
supersedes R09B2 rather than correcting it. `CAP-REMOTE-AUTHORITY-01` was the only opened
successor, but its review returned `REQUIREMENT_CHANGED`: the test-only boundary cannot supply the
required host-protected one-shot external-effect grant, and its cleanup contract lacked remote
ownership/CAS and pre-cleanup-evidence fail-closed behavior. Its candidate and first unretained
probe are not repair authority. Neither the investigation nor `f99d836` may be treated as repair
authority. Revision 14 is a host-external-effect-gateway architecture draft only: it opens no
successor and cannot restart CAP-REMOTE until its exact owner approval and a separately approved
host-capability investigation. R09C–R09E and publication remain unopened.

## Revision 06 / Revision 07 partition

Revision 06 is a separate direct-child ticket partition. Approved Revision 07 closes its
host-gateway public-contract prerequisite without reopening the completed Router phase.
`CHG-20260822-032` blocks its first candidate before dispatch and returns the POC main line to
the scoped change-control route; no R07A ticket or receipt currently authorizes an implementation
lane.
