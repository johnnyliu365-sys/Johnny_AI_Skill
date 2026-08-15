# DEC-20260816-522 — Revision-04 bootstrap re-admission

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `DEC-20260816-522` / `r01` / `ACTIVE` |
| Supersedes | only the Revision-03 admission status in frozen [`DEC-20260816-521`](../DEC-20260816-521-r03-live-dispatch-decomposition.md); it does not edit or unfreeze that leaf or any R03 ticket body |
| Authority | `PRD-20260816-027` / `CHG-20260816-027`; [`REQ-20260816-027`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-027.md); [`ADR-20260816-016`](../../../../../doc/adr/ADR-20260816-016-self-host-bootstrap-dispatch-exception.md); Revision 04 AC-31 through AC-38; sealed feature Context Revision 04 |
| Policy / registry commit | Receipt-bound Role Supervision Revision 04 / `f84b9e451d0d9840b8cfd10454f789291f4da0d0` |
| Normal Router policy | unchanged; the exact exception is bounded by [`Workflow.md#workflow-bootstrap-exception`](../../../../../Workflow.md#workflow-bootstrap-exception) |

## Additive admission decision

| Ticket | Exact immutable ticket ref | Re-admitted state | Dependency / next legal authority |
| --- | --- | --- | --- |
| `R03-01` | [`R03-01-live-artifact-registry-ticket-receipt-store.md`](../R03-01-live-artifact-registry-ticket-receipt-store.md) / `R03-01-CS-01` / `sha256:7eed669585f720aa8868a0c329dc138d75c86bb98137e07a48022474b7e45003` | `BOOTSTRAP_GRANT_AWAITING_OWNER_APPROVAL / NON_DISPATCHED` | only the exact draft [`BDG-R03-01-20260816-001`](BDG-R03-01-20260816-001.md), after explicit project-owner approval, may create one pre-call attempt leaf |
| `R03-02` | [`R03-02-task-workspace-admission-dispatch-claim-settlement.md`](../R03-02-task-workspace-admission-dispatch-claim-settlement.md) / `R03-02-CS-01` / `sha256:5daaf01e805a15f0b8dc759953928c412b8b26a528d58e9821a4261ca10464f1` | `RE_ADMITTED / FUTURE_REAL_RECEIPT_AND_TRANSPORT_GRANT_REQUIRED / NON_DISPATCHED` | R03-01 independently reviewed and integrated; then a real active receipt and a new transport grant are both required |
| `R03-03` | [`R03-03-senior-dispatch-gateway-capability-proof.md`](../R03-03-senior-dispatch-gateway-capability-proof.md) / `R03-03-CS-01` / `sha256:d30cbd9a0189006a712dbc0fb7b9c4c5c3bb8d3ac7019f07557fec046fbdb78d` | `RE_ADMITTED / HIGH_ASSURANCE_REQUIRED / NON_DISPATCHED` | R03-01 and R03-02 independently reviewed and integrated; real active receipt, transport grant, and separate ticket-specific owner approval are all required |

R03-01 is the only no-receipt phase. The draft grant is deliberately not a `TicketReceipt`,
`WorkReceipt`, `TicketDispatchReceipt`, attempt, host result, delivery assertion, or live
supervision capability claim. It binds a released existing owner and a fresh-branch preparation
requirement, but neither the owner nor the branch may be touched before owner approval.

The preflight found that the selected permanent implementation worktree is clean and bound to its
existing idle task, while its current branch does not descend from this policy/registry commit.
That makes `CREATE_FRESH_BRANCH_FROM_BASELINE` a required future owner action, not a reason to
reuse the old branch or create a second worktree. This decision records no raw filesystem path;
the opaque `WorktreeRef` is verified by task/workspace/Git evidence at the later attempt gate.

No grant is approved, attempt committed, receipt issued, branch/worktree/task created, owner
message sent, implementation started, review performed, integration attempted, wake registered,
or automatic action selected by this decision.
