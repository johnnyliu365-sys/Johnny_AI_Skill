# DEC-20260816-521 — Revision-03 live-dispatch prerequisite decomposition

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `DEC-20260816-521` / `r01` / `FROZEN` |
| Authority | `PRD-20260816-026` / `CHG-20260816-026`; `REQ-20260816-026`; `ADR-20260816-015`; Receipt-bound Role Supervision Revision 03 AC-24–AC-30 |
| Context / baseline | `doc/context/receipt-bound-role-supervision/main.md` Revision 03 / `d183140d09a1a25912102b862a92ef9b3aa190ad` |

Revision 03 has three ownership/effect closures: durable Johnny metadata and canonical receipt,
pure task/workspace admission plus claim settlement, and one privileged Senior-only gateway proof.
Tool inventory, fake success or an unsupported-host outcome never creates live dispatch capability.

| Candidate | Decision | Dependency | Reason |
| --- | --- | --- | --- |
| `R03-01-live-artifact-registry-ticket-receipt-store` | `READY_LOW_MODEL / NON_DISPATCHED` | none | Metadata registry and canonical receipt lifecycle are one bounded durable-storage closure. |
| `R03-02-task-workspace-admission-dispatch-claim-settlement` | `READY_LOW_MODEL / NON_DISPATCHED` | `R03-01` integrated | Pure readback/claim/settlement reducer; it cannot invoke a host gateway. |
| `R03-03-senior-dispatch-gateway-capability-proof` | `HIGH_ASSURANCE_REQUIRED / NON_DISPATCHED` | `R03-01`, `R03-02` integrated | Sole privileged composition; it must prove or truthfully deny host and supervision capability. |

No ticket, receipt, claim, task, branch, worktree, host call, wake, polling, heartbeat, push,
release or deployment is created here. Revision-01/02 admission leaves and the four admission
leaves at `471608b2abd361eeb16c29dc8728f85d173d8f57` remain immutable.
