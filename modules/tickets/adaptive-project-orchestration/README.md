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
| [02c1-artifact-tree-resolution-gate](02c1-artifact-tree-resolution-gate.md) | Generic bounded topology and exact one-path resolution for every declared workflow artifact family. | `READY_FOR_DISPATCH_REGISTRY / NON_DISPATCHABLE` | `3139bcc` / `PRG-20260815-479` |
| `02C2-requirement-retirement-archive-lineage` | One-to-one active PRD/CHG pairing, retirement and archive-only reachability. | `CANDIDATE / NON_DISPATCHABLE` | R02C1 approved/integrated |
| `02C3-bounded-library-selection` | Bounded archive/reusable-library partition indexes and one-leaf selection. | `CANDIDATE / NON_DISPATCHABLE` | R02C2 approved/integrated |
| `03-model-role-readiness-wake` | SPEC readiness and architecture-owner sleep/wake decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R02C3 approved/integrated |
| `04-low-model-ticket-admission` | Four-way low-model decomposition/admission decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R03 approved/integrated |
| `05-ui-design-source-routing` | Optional design-source capability decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R04 approved/integrated |
| `06-router-policy-acceptance` | Integrated Profile/Router acceptance and metadata-only serialization closure. | `CANDIDATE / NON_DISPATCHABLE` | R01-R05 approved/integrated |

No implementation ticket is currently active. R02C1 is the only dependency-satisfied closure;
its allocation and receipt do not exist until the control reviewer commits the dispatch registry.
Later candidate labels are not implementation authority.
