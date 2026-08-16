# BPB R03-00 bridge route clarification

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `CR-BPB-R03-00-003` / `r01` / `SEALED / CLARIFICATION` |
| Authority | `BPB-R03-00-20260816-001`; `CR-BPB-R03-00-002`; project-owner clarification |
| Scope | Router continuation only; no bridge, Workflow, Router-source, grant, attempt, receipt, or dispatch mutation |
| Corrected next action | Senior drafts one exact `R03-00 BootstrapDispatchGrant` in `OWNER_APPROVAL_PENDING / NON_DISPATCHED` state |

This additive clarification preserves `CR-BPB-R03-00-001` and
`CR-BPB-R03-00-002` as immutable evidence. `CR-BPB-R03-00-002` correctly closes the teardown
evidence defect and approves BPB review; it does **not** authorize a claim-before-effect attempt
or host call.

The only next Router action is Senior drafting one exact R03-00 grant bound to the approved bridge,
ticket registry commit, ticket blob/digest, implementation binding, expected return, and fresh
ticket ContextView. Before a separate project-owner approval of that exact committed grant, its
state remains `OWNER_APPROVAL_PENDING / NON_DISPATCHED`.

No attempt, receipt, pending descriptor, implementation wake, host call, integration, R03-01A
through R03-01D admission, heartbeat, polling, push, release, or deployment is authorized by
this clarification. R03-00 is the policy-correction implementation prerequisite; only its later
completion, independent review, and guarded integration establish the Revision-05 executable
policy. Normal Router capability remains unavailable until the subsequent R03-01A–D, R03-02, and
R03-03 sequence is completed under their own gates.
