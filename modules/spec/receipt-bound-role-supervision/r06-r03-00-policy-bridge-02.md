# BPB-R03-00-20260816-002 — R03-00 immutable-admission policy bridge

| Field | Value |
| --- | --- |
| Kind / revision | `BOOTSTRAP_POLICY_BRIDGE` / `r02` |
| Lifecycle | `OWNER_APPROVED / SENIOR_REVIEW_REQUIRED / NO_SUCCESSOR_TICKET_OR_GRANT` |
| Project | `AI控制工作workflow` |
| Parent SPEC | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` Revision 06 |
| Requirement | `PRD-20260816-030` / `CHG-20260816-030` |
| Context | `doc/context/receipt-bound-role-supervision/revisions/rev07-r03-00-immutable-admission.md` |
| Historical route | `BPB-R03-00-20260816-001` / `R03-00-CS-01` / consumed; never reusable |
| Ticket / future closure | `R03-00-policy-correction-prerequisite` / `R03-00-CS-02` |
| Ticket blob / digest / registry | `UNBOUND_UNTIL_APPROVED_BRIDGE_REVIEW_AND_SENIOR_TICKET_CREATION` |
| Permitted phase | `R03_00_POLICY_CORRECTION_NO_RECEIPT` only |
| Baseline rule | `CLAIM_INTRODUCTION_COMMIT` |
| Normal capability claim | `NONE / UNAVAILABLE_UNTIL_PROVEN` |

## Purpose and exact scope

This bridge corrects the immutable-admission and stale-baseline defects exposed by the first
R03-00 delivery. It is a successor route, not an amendment to CS-01 or a retry of the consumed
grant. It authorizes no ticket, owner, task, worktree, model, ContextView, grant, attempt, receipt,
host call or source effect by itself.

The bridge covers only the exact future closure `R03-00-CS-02`. It does not cover the old closure,
R03-01A through R03-01D, another project, another ticket or any post-integration action. BPB-001
remains historical and cannot be reused. Any scope mismatch returns
`HALT / BOOTSTRAP_SCOPE_FORBIDDEN` before effect.

## Independent review-before-ticket gate

The Senior first performs one independent docs/policy review of the exact commit introducing this
bridge and records an additive review under `doc/reviews/receipt-bound-role-supervision/`. The
review validates:

1. exact project, parent SPEC, requirement, Context, ticket and future closure;
2. the historical fence over CS-01, BPB-001, old review/clarification records, old
   grant/attempt/result and Implementer halt;
3. explicit exclusion of R03-01A through R03-01D and all normal-capability claims;
4. the CS-02 state grammar and complete execution-binding requirement;
5. the `CLAIM_INTRODUCTION_COMMIT` rule, no self-referential hash and derived envelope field;
6. ordered bridge-review, ticket-registry, grant-approval, attempt and one-host-call gates; and
7. no heartbeat, recurring read, polling, automation or external deployment effect.

Only `APPROVED` review permits Senior to create CS-02 and its new immutable registry. Bridge review
does not itself create or approve that ticket, and it does not permit a grant. `CHANGES_REQUESTED`,
missing evidence or mismatch leaves the route without a successor ticket.

## Successor ticket and grant gates

- CS-02 itself must state
  `ADMITTED_FOR_BPB_ROUTE / HIGH_ASSURANCE_REQUIRED / OWNER_GRANT_REQUIRED`, contain every actual
  execution binding and omit the three forbidden blocking tokens defined by AC-50.
- Senior records a new immutable registry/decision set that binds the exact ticket blob/digest and
  BPB-002. No prior registry or leaf is edited.
- Only after successful ticket admission may Senior draft one successor
  `BootstrapDispatchGrant`. The grant binds the new registry/blob/digest and exact execution
  identity, including the selected model/profile.
- Project owner must approve the exact committed grant. Bridge approval is not grant approval.
- The consuming attempt's introduction commit is the execution baseline. Its derived commit ID is
  included as `claim_commit` in the one-shot envelope and verified before mutation.
- Every later correction requires a new lawful ticket/admission or correction source and a new
  owner-approved grant. Nothing in the consumed route is replayed.

## Terminal and failure rules

| Event | Bridge result |
| --- | --- |
| R03-00 CS-02 reviewed and integrated | `CLOSED / POLICY_INTEGRATED`; later phases use the integrated policy only. |
| `EFFECT_UNCERTAIN` | `QUARANTINED`; no retry, replacement grant or reconciliation without new Architecture/owner decision. |
| `TICKET_DEFECT` or `REQUIREMENT_CHANGED` | `CLOSED_FOR_CHANGE`; return to Architecture/change control. |
| owner revocation | `CLOSED / REVOKED`; no new effect. |
| identity, digest, ancestry, order or review mismatch | `HALT / BOOTSTRAP_SCOPE_FORBIDDEN`; zero effect. |

R03-00 completion alone does not dispatch R03-01A. Independent review and guarded integration are
still required before Senior may re-admit any replacement phase.

## Approval record

- Architecture/Grill decision: new immutable CS-02 source plus claim-introduction baseline; old
  route preserved and consumed.
- Project owner decision/date: `APPROVED` / `2026-08-16 (Asia/Taipei)`.
- Approval effect: seal this bridge for independent Senior review only. No ticket, registry,
  grant, attempt, receipt, task, worktree, branch, dispatch, implementation, integration,
  heartbeat, push, release or deployment is created by this approval.
