# Adaptive Project Orchestration — Router Phase Tickets

> Approved Router scope: [adaptive-project-orchestration.md](../../spec/adaptive-project-orchestration.md)
> revision 02 / AC-12 through AC-14 and the Router portions of AC-05 through AC-10.
> This set does not authorize initialization, staging, packaging or target-project effects.

## Serial closure order

| Ticket | Observable closure | State | Dependency |
| --- | --- | --- | --- |
| [01-route-instruction-contract](01-route-instruction-contract.md) | Every Router decision carries one versioned skill reference and one exact expected typed return; technical halts use the Profile's router-control fallback. | `CHANGES_REQUESTED / REVISION_03_REFROZEN` | CR-R01-001..003 closed; CR-R01-004 P0 typing; same lane/scope |
| `02-model-role-readiness-wake` | SPEC readiness and architecture-owner sleep/wake decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R01 approved/integrated |
| `03-low-model-ticket-admission` | Four-way low-model decomposition/admission decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R02 approved/integrated |
| `04-ui-design-source-routing` | Optional design-source capability decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R03 approved/integrated |
| `05-router-policy-acceptance` | Integrated Profile/Router acceptance and metadata-only serialization closure. | `CANDIDATE / NON_DISPATCHABLE` | R01-R04 approved/integrated |

Only R01 may become dispatchable now. Later files are created from the independently accepted
predecessor baseline; their candidate labels are not implementation authority.
