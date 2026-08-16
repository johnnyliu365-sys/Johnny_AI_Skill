# BPB-R03-00-20260816-001 — R03-00 bootstrap policy bridge

| Field | Value |
| --- | --- |
| Kind / revision | `BOOTSTRAP_POLICY_BRIDGE` / `r01` |
| Lifecycle | `OWNER_APPROVED / SENIOR_REVIEW_REQUIRED / NON_DISPATCHED` |
| Project | `AI控制工作workflow` |
| Parent SPEC | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` Revision 05 |
| Requirement | `PRD-20260816-029` / `CHG-20260816-029` |
| Context | `doc/context/receipt-bound-role-supervision/revisions/rev06-r03-00-policy-bridge.md` |
| Approved Revision-05 baseline | `07744bb95fa1be3d6728f81ba0076b192ac1782a` |
| Ticket registry commit | `e0a710d217624cd90f902e14fe216d945e5ef0fa` |
| Ticket / closure | `R03-00-policy-correction-prerequisite` / `R03-00-CS-01` |
| Ticket blob / SHA-256 | `a6e176f0550907806538587323cb5c75fcff8f8f` / `35b0579e8ac43dece2d0a406d496fa431cd109807b1c095e6dff5c3b223d7f06` |
| Permitted phase | `R03_00_POLICY_CORRECTION_NO_RECEIPT` only |
| Normal capability claim | `NONE / UNAVAILABLE_UNTIL_PROVEN` |

## Purpose and exact scope

This bridge breaks only the circular dependency in which R03-00 must implement the Revision-05
written and executable allowlist but cannot be dispatched by the Revision-04 allowlist. It is a
temporary owner policy for one exact project/ticket identity. It is not a `TicketReceipt`, a
pending dispatch descriptor, an executable-policy substitute or evidence that normal dispatch is
available.

It supersedes only Revision-04 AC-31's fourth-ticket rejection for this exact R03-00 identity.
The Revision-04 executable three-ticket allowlist is not edited or widened by the bridge; every
other AC-31 rejection and AC-32 through AC-35 invariant remains in force.

The bridge does not cover `R03-01A`, `R03-01B`, `R03-01C`, `R03-01D`, any revised R03-00 closure,
another project or any post-integration action. A mismatch returns
`HALT / BOOTSTRAP_SCOPE_FORBIDDEN` before Agent, Git, host or source effect.

## Review-before-grant gate

The Senior first performs one independent docs/policy review of the exact bridge commit and
records it under `doc/reviews/receipt-bound-role-supervision/`. Review validates:

1. project, parent SPEC, requirement, Context, registry commit, ticket blob and SHA-256;
2. the one-ticket allowlist and explicit exclusion of R03-01A through R03-01D;
3. consistency with Revision-04 AC-32 through AC-35 and Revision-05 AC-39 through AC-47;
4. absence of receipt, pending descriptor, owner/task/worktree/model selection or capability
   claims; and
5. the quarantine, closure, no-heartbeat and no-external-effect boundaries.

Only `APPROVED` review may let the Senior draft one exact initial `BootstrapDispatchGrant` for
R03-00. `CHANGES_REQUESTED`, missing evidence or mismatch leaves this bridge
`NON_DISPATCHED`; the bridge may not approve itself.

## Grant, relay, correction and integration

- The Senior alone selects and binds the implementation owner, task, worktree, branch, baseline,
  model/profile, ContextView, expected return and action in a separately committed grant.
- The project owner must approve that exact grant before the Senior commits one consuming attempt
  and performs one host call. Architecture does not create, approve or transmit the grant.
- User relay contains only `BOOTSTRAP_RETURN_AVAILABLE` plus `grant_ref`; it is a wake hint, not
  completion evidence or authority. No heartbeat, recurring read or timed polling is permitted.
- Every review correction requires a new one-shot owner-approved grant bound to the same ticket
  digest and exact review decision. A previous grant or attempt is never reused.
- An independently `APPROVED` R03-00 implementation review may use the existing AC-35 guarded
  integration grant. Integration authorizes no push, release or deployment.

## Terminal and failure rules

| Event | Bridge result |
| --- | --- |
| R03-00 reviewed and integrated | `CLOSED / POLICY_INTEGRATED`; Revision-05 executable policy becomes the only later route. |
| `EFFECT_UNCERTAIN` | `QUARANTINED`; no retry, replacement grant or reconciliation without a new Architecture/owner decision. |
| `TICKET_DEFECT` or `REQUIREMENT_CHANGED` | `CLOSED_FOR_CHANGE`; return to Architecture/change control. |
| owner revocation | `CLOSED / REVOKED`; no new effect. |
| identity, digest, order or review mismatch | `HALT / BOOTSTRAP_SCOPE_FORBIDDEN`; zero effect. |

R03-00 completion alone does not dispatch R03-01A. Only independent review plus guarded
integration closes the bridge and permits Senior to re-admit the first replacement phase under
the newly integrated policy. Every A–D phase keeps its own ticket, dependency and grant gate.

## Approval record

- Architecture/Grill decision: one-ticket R03-00 bridge; direct A–D coverage rejected.
- Project owner decision/date: `APPROVED` / `2026-08-16 (Asia/Taipei)`.
- Approval effect: seal this policy for independent Senior review only. No grant, attempt,
  receipt, task, worktree, branch, dispatch, implementation, integration, heartbeat, push,
  release or deployment is created by this approval.
