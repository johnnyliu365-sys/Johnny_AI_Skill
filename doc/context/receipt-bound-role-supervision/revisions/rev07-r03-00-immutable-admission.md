# Receipt-bound Role Supervision Context Revision 07 — R03-00 immutable admission recovery

| Field | Value |
| --- | --- |
| Kind | `CONTEXT_REVISION_LEAF` |
| State | `SEALED / OWNER_APPROVED / SENIOR_BRIDGE_02_REVIEW_REQUIRED` |
| Parent Context | `doc/context/receipt-bound-role-supervision/main.md` Revision 06 |
| Requirement | `PRD-20260816-030` / `CHG-20260816-030` |
| Bridge | `BPB-R03-00-20260816-002` |
| Trigger | `UPSTREAM_DECISION_REQUIRED / BOOTSTRAP_POLICY_BRIDGE_MISSING` returned after the consumed `BDG-R03-00-20260816-001` delivery |

## Confirmed facts

- Registry `e0a710d217624cd90f902e14fe216d945e5ef0fa` immutably binds
  `R03-00-CS-01` as `PLANNED / HIGH_ASSURANCE_REQUIRED / BLOCKED / NON_DISPATCHED`. Its ticket
  source correctly caused Implementer-2 to halt before mutation.
- `BPB-R03-00-20260816-001`, its three review/clarification records,
  `BDG-R03-00-20260816-001`,
  `BDA-R03-00-20260816-001`, `BDR-R03-00-20260816-001` and delivery turn
  `01a00a4f-4ce7-7d03-8b42-6bbaff6bf2b1` are historical evidence. The grant was consumed and no
  retry or correction may reuse it.
- Exact claim/delivery commits `a7cb3d011594f4a08cfa7a925ae7888231ed381d` and
  `336238ed71c24dc0487013775cb269d884d186ce` remain the immutable provenance of that failed
  admission route; the latter is not an implementation-completion claim.
- A later bridge or grant cannot override the immutable state of the ticket source named by a
  dispatch registry. The recovery therefore needs a new ticket closure and registry, not an edit
  to `R03-00-CS-01` or its decision leaves.
- The successor bridge covers only `R03-00-CS-02`. It must receive independent Senior review
  before the Senior creates the successor ticket/admission source.
- The successor ticket source must itself be conditionally admitted for the BPB route and contain
  the exact execution bindings selected by the Senior. The later owner-approved grant must match
  its blob, digest, registry and execution identity.
- A fixed baseline that predates the grant cannot provide a fresh implementation branch with the
  grant or consuming claim. The successor grant therefore declares
  `baseline_rule=CLAIM_INTRODUCTION_COMMIT`; the commit that first introduces the consuming
  attempt becomes the execution baseline after Git readback.
- The attempt leaf avoids a self-referential hash. Its derived introduction commit ID is carried
  in the one-shot dispatch envelope and must contain the reviewed bridge, successor registry,
  ticket and approved grant.
- `HIGH_ASSURANCE_REQUIRED` does not itself force Terra. Senior selects the model/profile and the
  project owner approves the exact binding in the later grant.
- This is still a manual bootstrap route. No live Router, receipt issuer, event subscription,
  heartbeat, automation, recurring read or normal-dispatch capability is claimed.
- R03-01A through R03-01D remain blocked until a separately reviewed and integrated R03-00
  implementation exists.

## Continuation

The single next governed action is `REVIEW / SENIOR_POLICY_BRIDGE_02_REVIEW` over the exact
Architecture commit containing `BPB-R03-00-20260816-002`. Approval of this Context/SPEC does not
let Architecture create a ticket or let Senior skip that review. No successor ticket, grant,
attempt, host call or implementation authority exists yet.
