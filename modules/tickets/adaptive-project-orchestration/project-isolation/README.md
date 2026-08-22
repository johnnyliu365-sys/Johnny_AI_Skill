# Revision 06 Project Isolation Admission Index

| Child ID | Kind | Revision | SHA-256 | Lifecycle | State | Exact leaf |
| --- | --- | --- | --- | --- | --- | --- |
| `TAD-ADAPTIVE-R06-ISOLATION-01` | `TICKET_ADMISSION_DECISION` | `01` | `ef73ebcb12fd2b943e7193db9c001c3df1bf37d501001762a3a27fac68f2a241` | `ACTIVE` | `UPSTREAM_DECISION_REQUIRED / NON_DISPATCHABLE` | [r06-project-isolation-upstream-decision.md](r06-project-isolation-upstream-decision.md) |
| `TAD-ADAPTIVE-R07-HOST-CAPABILITY-01` | `IMPLEMENTATION_TICKET` | `01` | `2603966caef2e172b042635abe35ebf399dc5a95eea999589eee5e068852915d` | `ACTIVE` | `APPROVED_NOT_DISPATCHED` | [r07a-host-capability-readback-contract.md](r07a-host-capability-readback-contract.md) |

Revision 07 closes the public-contract upstream decision only for the direct, no-effect R07A
ticket. R07A is not a dispatch authority, receipt, source/test authority outside its boundary, or
permission to alter target Git state, create a workspace or Agent, reserve a task, control a host,
or access storage. Its succeeding workspace-verification, reservation and delivery closures remain
separate serial tickets.
