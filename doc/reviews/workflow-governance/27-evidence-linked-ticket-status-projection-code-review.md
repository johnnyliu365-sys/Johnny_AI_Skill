# Ticket 27 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/27-evidence-linked-ticket-status-projection.md` |
| Candidate / local admission | `a77925d8c85cbce72174809ff038686753c67e93` / `3196712db39178de77de01a19cdbd49271a20de4` |
| Reviewer | Separate `gpt-6-sol/high` seat; no implementation edits |
| Conclusion | `APPROVED` for opt-in status projection; checklist 07 remains open |

The four admitted blobs exactly match the reviewed candidate; no intervening commit
changed those paths. The revised ticket boundary parses with only the four declared
modifications and no create/delete permission. Fresh targeted tests passed: 108 tests
and 200 subtests; strict mypy passed on both production modules. The reviewer changed
the APPROVED guard to REJECTED: required OPEN and NOT_VERIFIED cells turned red;
restoration returned both to green. The current three-column status format remains
supported, while the opt-in five-column format distinguishes required and optional
evidence. Admission used the existing document mutation gate without push.

Evidence refs are untrusted displayed claims, not proof that review or source binding
occurred. Parent aggregation, finding owner/disposition and real closure admission
remain outside this slice and checklist 07 remains unchecked.
