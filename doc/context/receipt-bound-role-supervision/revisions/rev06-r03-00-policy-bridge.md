# Receipt-bound Role Supervision Context Revision 06 — R03-00 policy bridge

| Field | Value |
| --- | --- |
| Kind | `CONTEXT_REVISION_LEAF` |
| State | `SEALED / OWNER_APPROVED / SENIOR_REVIEW_REQUIRED` |
| Parent Context | `doc/context/receipt-bound-role-supervision/main.md` Revision 05 |
| Requirement | `PRD-20260816-029` / `CHG-20260816-029` |
| Bridge | `BPB-R03-00-20260816-001` |
| Trigger | `UPSTREAM_DECISION_REQUIRED / BOOTSTRAP_POLICY_BRIDGE_MISSING` from `DEC-20260816-523` |

## Confirmed facts

- The current Revision-04 exception cannot admit the new policy-correction ticket, and a ticket
  cannot create its own dispatch authority.
- The only approved escape from that cycle is one manual, no-receipt bridge for the exact R03-00
  ticket. It is not an executable allowlist replacement or normal capability proof.
- Senior remains the sole Agent-to-Agent orchestrator. Architecture owns only the bridge policy;
  it does not select an Implementer, task, worktree, branch, baseline, model or dispatch action.
- Senior review of the exact bridge commit must be `APPROVED` before a grant may be drafted. Every
  host effect then requires its own project-owner-approved grant and claim-before-effect record.
- R03-01A through R03-01D receive no authority from this revision and remain blocked until R03-00
  is reviewed and integrated.
- `EFFECT_UNCERTAIN` quarantines without retry. Integration, owner revocation, requirement change
  or ticket defect terminates or reroutes the bridge exactly as its policy leaf declares.
- No heartbeat, recurring read, polling, automation, push, release or deployment is authorized.

## Continuation

The only next Router action is `REVIEW / SENIOR_POLICY_BRIDGE_REVIEW` over the exact committed
bridge. Until an approved review exists, the return remains `WAIT_FOR_HUMAN / BRIDGE_REVIEW` and
no grant or implementation dispatch is legal.
