# R04 bootstrap provenance schema

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `SCHEMA-R04-BOOTSTRAP-01` / `r01` / `ACTIVE` |
| Authority | `PRD-20260816-027` / `CHG-20260816-027`; `REQ-20260816-027`; `ADR-20260816-016`; Receipt-bound Role Supervision Revision 04 AC-31 through AC-38 |
| Scope | `modules/tickets/receipt-bound-role-supervision/r03-live-dispatch/r04-bootstrap/` only |

This bounded partition is the immutable, target-owned provenance tree for the sole project-specific
Revision-04 bootstrap route. It is not Router runtime state, a receipt, a dispatch descriptor, an
attempt, or live-capability evidence. The normal digest-bound Router policy remains unchanged;
[`Workflow.md#workflow-bootstrap-exception`](../../../../../Workflow.md#workflow-bootstrap-exception)
is the committed policy boundary that permits this additive tree.

## Direct-child rule

Its `README.md` is an index only. Every row contains only `ID`, `kind`, `revision`, `digest`,
`lifecycle`, and an exact direct reference. It contains no descendant inventory, contract prose,
chat, prompt, path, secret, result body, or copied evidence. Each leaf is immutable after commit;
any correction is a new direct child with `supersedes_ref` rather than an edit in place.

## Allowed immutable leaf kinds

| Kind | Required phase | May exist now | State transition boundary |
| --- | --- | --- | --- |
| `POLICY` | all | no; policy is the approved Revision-04 sources | architecture change control only |
| `DISPATCH_GRANT` | `R03_01_NO_RECEIPT` | one draft only | explicit project-owner approval |
| `DISPATCH_ATTEMPT` | any bootstrap dispatch | no | committed before exactly one host call; consumes one approved grant |
| `DISPATCH_RESULT` | after attempt | no | `DELIVERED`, `NO_EFFECT`, or `EFFECT_UNCERTAIN` only |
| `RELAY_OBSERVATION` | after user wake hint | no | records only literal plus grant ref and Senior ref |
| `REVIEW_DECISION` | after independently verified handoff | no | `APPROVED`, `CHANGES_REQUESTED`, or `BLOCKED` |
| `INTEGRATION_GRANT` | after exact approved review | no | separate guarded local-integration authority |
| `INTEGRATION_RESULT` | after integration grant | no | `INTEGRATED` or `INTEGRATION_BLOCKED` |
| `NORMAL_ACTIVATION` | after all R03 integrations | no | `NORMAL_ACTIVE`, `NORMAL_CAPABILITY_UNPROVEN`, or `NORMAL_ACTIVATION_BLOCKED` |

`CORRECTION_DISPATCH` and `TRANSPORT_*` are new grant leaves with the same `DISPATCH_GRANT`
kind, never edits to an initial grant. R03-02/R03-03 require a real active `TicketReceipt` plus a
separate transport grant; R03-03 additionally needs ticket-specific high-assurance owner approval.
No fourth ticket, generic fallback, retry after uncertainty, heartbeat, polling, task creation,
branch creation, host call, push, release, deployment, or target-project mutation is represented
by this schema.
