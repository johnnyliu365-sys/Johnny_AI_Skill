# R03-00 BPB bootstrap provenance schema

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `SCHEMA-BPB-R03-00-01` / `r01` / `ACTIVE` |
| Authority | `BPB-R03-00-20260816-001`; `CR-BPB-R03-00-002`; `CR-BPB-R03-00-003` |
| Scope | `modules/tickets/receipt-bound-role-supervision/r03-live-dispatch/r05-bpb-bootstrap/` only |

This is the target-owned, bounded provenance partition for the one R03-00 manual bootstrap
route. It is not executable Router state, a `TicketReceipt`, a pending descriptor, an attempt,
or evidence that normal receipt-bound dispatch exists.

## Direct-child and immutability rules

Its `README.md` is a direct-child index only: ID, kind, revision, digest, lifecycle and exact
reference. A committed leaf is immutable. A correction adds a new leaf that names the exact
superseded reference; it never edits the original grant, attempt, result or review evidence.

## Allowed leaf transitions

| Kind | Precondition | Allowed lifecycle |
| --- | --- | --- |
| `BOOTSTRAP_DISPATCH_GRANT` | BPB review approved | `OWNER_APPROVAL_PENDING / NON_DISPATCHED`, then a separate explicit owner approval |
| `BOOTSTRAP_DISPATCH_ATTEMPT` | exact approved grant | committed claim-before-effect before one host call only |
| `BOOTSTRAP_DISPATCH_RESULT` | one committed attempt | `DELIVERED`, `NO_EFFECT` or `EFFECT_UNCERTAIN` only |
| `REVIEW_DECISION` | verified implementation return | `APPROVED`, `CHANGES_REQUESTED` or `BLOCKED` only |

No leaf authorizes a retry after uncertainty, receipt issuance, R03-01A through R03-01D,
normal capability activation, heartbeat, polling, task/worktree creation, push, release,
deployment or external effect.
