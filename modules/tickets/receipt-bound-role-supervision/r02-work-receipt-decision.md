# Revision 02 Receipt-bound Supervision Admission Decision

| Field | Value |
| --- | --- |
| Artifact / authority | `TAD-SUPERVISION-R02-01`; Receipt-bound Role Supervision Revision 02, AC-20--AC-22 |
| Requirement / Context / ADR | `PRD-20260816-025` / `CHG-20260816-025` / `CONTEXT.md` seal and `doc/context/receipt-bound-role-supervision/main.md` / `ADR-20260816-014` |
| Baseline / decision | `b6183658b7c16f9b0723482cee62fe89e677ebf3` / `UPSTREAM_DECISION_REQUIRED` |
| Effects / XSS | Event subscription, role wake and diagnostic activation are not admitted; `XSS_NOT_APPLICABLE` |

## Missing contract that blocks vertical tickets

AC-20 declares `WorkReceipt = TicketReceipt | StageWorkReceipt`, but no `TicketReceipt` public
structure, constructor invariants or receipt-admission result/decision algebra exists anywhere in
the approved SPEC set. `StageWorkReceipt` alone cannot be round-tripped or safely discriminated
as a closed union. AC-21 names a registration record but not its request, callback payload/result,
cancellation result or unavailable/reconciliation decision. AC-22 names `DiagnosticRoleBinding`
but not the bounded finding result contract.

Implementing any union, runtime-event or diagnostic ticket would require invented nullability,
error precedence and callback authority semantics. Host/Agent-control work is high-assurance
once contracts exist, but the present failure is earlier: no strict public contract can pass the
required constructor, negative and reversal preflight.

## Required route

`UPSTREAM_DECISION_REQUIRED / TICKET_RECEIPT_EVENT_AND_DIAGNOSTIC_RESULT_CONTRACT_UNDEFINED`.
No receipt, subscription, diagnostic role, source/test scope, dispatch or polling fallback is
created. A sealed amendment must define the missing union members and operation results before
fresh decomposition.
