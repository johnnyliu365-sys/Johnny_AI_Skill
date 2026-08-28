# R09B1 recoverable managed-artifact contracts — element index

| Field | Binding |
| --- | --- |
| Ticket / closure | `TICKET-ADAPTIVE-R09B1-RECOVERABLE-MANAGED-ARTIFACT-CONTRACTS` / `CLOSURE-ADAPTIVE-R09B1-RECOVERABLE-MANAGED-ARTIFACT-CONTRACTS-01` |
| SPEC / requirement / context / ADR | Adaptive Project Orchestration Revision 11 / `PRD-20260828-044` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-11` / `ADR-20260828-032` |
| Source / test | `library/workflow_router/target_document_contracts.py` / `tests/test_managed_artifact_recovery_contracts.py` |
| Ownership | This element indexes additive strict result contracts only. It is not a recovery journal, lock, filesystem writer, resolver, target authority, plugin adapter or package export. |

The source accepts only finite typed outcome metadata. It never persists snapshot bytes or performs
an effect; private recovery persistence and all runtime validation remain a later ticket.
