# R03-00 CS-02 bootstrap provenance schema

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `SCHEMA-BPB-R03-00-02` / `r01` / `ACTIVE` |
| Authority | [BPB-R03-00-20260816-002](../../../../spec/receipt-bound-role-supervision/r06-r03-00-policy-bridge-02.md); [CR-BPB-R03-00-004](../../../../../doc/reviews/receipt-bound-role-supervision/BPB-R03-00-immutable-admission-review.md) |
| Scope | This direct-child partition only |

The README contains only direct-child metadata. A committed grant, attempt, result, or review leaf
is immutable; a correction adds a new leaf and never rewrites old evidence. This partition is
manual bootstrap provenance, not executable Router state, a receipt, a pending descriptor, or
normal capability proof.

| Kind | Required predecessor | Permitted transition |
| --- | --- | --- |
| `BOOTSTRAP_DISPATCH_GRANT` | exact CS-02 admission | `OWNER_APPROVAL_PENDING / NON_DISPATCHED`, then an independent exact owner approval |
| `BOOTSTRAP_DISPATCH_ATTEMPT` | exact approved grant | one committed claim before one host call |
| `BOOTSTRAP_DISPATCH_RESULT` | one committed attempt | `DELIVERED`, `NO_EFFECT`, or `EFFECT_UNCERTAIN` |

No leaf authorizes a retry after uncertainty, receipt issuance, normal capability activation,
heartbeat, polling, task/worktree creation, push, release, deployment, or external effect.
