# DEC-20260816-523 — Revision-05 R03 recovery decomposition

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `DEC-20260816-523` / `r01` / `ACTIVE / POLICY_BRIDGE_REQUIRED` |
| Authority | `PRD-20260816-028` / `CHG-20260816-028`; [`REQ-20260816-028`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md); Revision 05 AC-39–AC-47 |
| Context / review | [`Revision-05 Context`](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md); [`CR-R03-01-001`](../../../../../doc/reviews/receipt-bound-role-supervision/R03-01-bootstrap-code-review.md) |
| Evidence baseline | `07744bb95fa1be3d6728f81ba0076b192ac1782a` |

`R03-01-CS-01`, `BDG-R03-01-20260816-001`, its attempt/result leaves,
`224b0242df876f6a41fd1b7e8f139195e9f40e42`, and `CR-R03-01-001` remain immutable historical
evidence. No ticket below authorizes source reuse, correction of that attempt, receipt, task,
worktree, branch, grant, or dispatch.

| Candidate | Observable closure | Decision | Exact dependency |
| --- | --- | --- | --- |
| `R03-00-policy-correction-prerequisite` | Make Revision-05 bootstrap policy consistent in `Workflow.md`, `CodeReview.md`, and executable Router policy. | `HIGH_ASSURANCE_REQUIRED / BLOCKED / NON_DISPATCHED` | A project-owner-approved bridge that admits this policy ticket under the current Revision-04 allowlist. |
| `R03-01A-contract-freeze` | Construct, validate, serialize and reject invalid durable metadata contracts and owned-root capability admission results without an effect. | `READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` | `R03-00` reviewed/integrated; then its own no-receipt grant. |
| `R03-01B-durable-state-transaction` | One owned-root checkpoint/journal read-CAS transaction with finite recovery and restart proof. | `READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` | `R03-01A` reviewed/integrated; then its own grant. |
| `R03-01C-approved-artifact-registry` | Immutable approved-artifact registration/read through the integrated durable transaction. | `READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` | `R03-01B` reviewed/integrated; then its own grant. |
| `R03-01D-ticket-receipt-cas` | Canonical TicketReceipt issue/read CAS and one-live-receipt invariant through registry/state. | `READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` | `R03-01C` reviewed/integrated; then its own grant. |

The policy prerequisite is circular under the current executable policy: `Workflow.md` still
allowlists only Revision-04 `R03-01` through `R03-03`, while AC-47 forbids treating
Revision-05 documents as an executable-policy replacement. A ticket cannot create its own
dispatch route. Required Router return:
`UPSTREAM_DECISION_REQUIRED / BOOTSTRAP_POLICY_BRIDGE_MISSING`. Architecture and the owner must
provide one exact, reviewable bridge before any grant or implementation may exist. This decision
does not invent that bridge.

After `R03-01D` is independently reviewed and integrated, only then may the existing logical
`R03-02` enter its separately governed real-receipt route; `R03-03` remains high assurance.
