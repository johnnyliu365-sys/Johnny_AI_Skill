# Adaptive Project Orchestration — Router Phase Tickets

> Approved Router scope: [adaptive-project-orchestration.md](../../spec/adaptive-project-orchestration.md)
> revision 04 / AC-12 through AC-17 and the Router portions of AC-05 through AC-10.
> This set does not authorize initialization, staging, packaging or target-project effects.

## Serial closure order

| Ticket | Observable closure | State | Dependency |
| --- | --- | --- | --- |
| [01-route-instruction-contract](01-route-instruction-contract.md) | Every Router decision carries one versioned skill reference and one exact expected typed return; technical halts use the Profile's router-control fallback. | `COMPLETE / APPROVED / INTEGRATED` | `5c3445f` |
| [02a-shared-context-lifecycle-gate](02a-shared-context-lifecycle-gate.md) | Architecture-stage draft/revise/seal and change-control-only revision admission; later roles are exact sealed-revision readers. | `COMPLETE / APPROVED / INTEGRATED` | `9bf7d340` / `PRG-20260815-469` |
| [02b-agent-context-lease-invalidation-gate](02b-agent-context-lease-invalidation-gate.md) | One implementation-owner, ticket-bound Agent Context lease; correction invalidates and ticket switch closes the old view before a fresh identity exists. | `COMPLETE / APPROVED / INTEGRATED` | `9e3d92bc` / `PRG-20260815-477` |
| `02C-artifact-tree-lineage-gate` | One-path artifact resolution plus active PRD/CHG pairing and bounded archive/library indexes. | `READY_FOR_TICKET_DESIGN / NON_DISPATCHABLE` | R02B approved/integrated |
| `03-model-role-readiness-wake` | SPEC readiness and architecture-owner sleep/wake decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R02C approved/integrated |
| `04-low-model-ticket-admission` | Four-way low-model decomposition/admission decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R03 approved/integrated |
| `05-ui-design-source-routing` | Optional design-source capability decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R04 approved/integrated |
| `06-router-policy-acceptance` | Integrated Profile/Router acceptance and metadata-only serialization closure. | `CANDIDATE / NON_DISPATCHABLE` | R01-R05 approved/integrated |

No implementation ticket is currently active. R02C is the only dependency-satisfied design closure;
its file, allocation and receipt do not exist until the control reviewer freezes and commits them.
Later candidate labels are not implementation authority.
