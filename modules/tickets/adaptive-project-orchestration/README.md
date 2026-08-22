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
| [project-isolation](project-isolation/README.md) | Revision 06 project-isolation partition, amended by the approved Revision 07 host-gateway contract. | `R07A_APPROVED_NOT_DISPATCHED` | revision `02`; SHA-256 `fe177bb6b527ff60419c53b2c339ea50c9aaab2ab703fd031c0ff1e090ce4109`; `TAD-ADAPTIVE-R07-HOST-CAPABILITY-01` is the only authorized direct implementation child |

R02C1, R02C2, R02C2A, R02C3 and R03 are complete. R04 is the next serial candidate, but it
remains `CANDIDATE / NON_DISPATCHABLE` until its own approved ticket freeze, handoff and receipt
registry exist. Candidate labels are not implementation authority.

## Revision 06 / Revision 07 partition

Revision 06 is a separate direct-child ticket partition. Approved Revision 07 closes its
host-gateway public-contract prerequisite without reopening the completed Router phase. Its first
authorized no-effect implementation ticket is reachable only through
[`project-isolation/README.md`](project-isolation/README.md); the leaf's own ticket and receipt
remain mandatory before any implementation lane.
