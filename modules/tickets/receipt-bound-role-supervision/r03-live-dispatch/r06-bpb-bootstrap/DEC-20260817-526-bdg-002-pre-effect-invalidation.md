# DEC-20260817-526 BDG-002 pre-effect envelope invalidation

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `DEC-20260817-526` / `r01` / `ACTIVE / PRE_EFFECT_GRANT_CORRECTION` |
| Superseded grant | [BDG-R03-00-20260816-002](BDG-R03-00-20260816-002.md), explicitly owner-approved, is `INVALID_BEFORE_EFFECT / UNCONSUMED`. |
| Exact defect | BDG-002's six-field envelope omits the required derived `claim_commit`; AC-52 and Workflow require it before Implementer mutation. |
| Absent effects | No committed BDA, claim commit, host call, branch, Implementer message, or implementation effect exists. The uncommitted BDA-002 draft is discarded and has no authority. |
| Replacement authority | [BPB-002](../../../../spec/receipt-bound-role-supervision/r06-r03-00-policy-bridge-02.md), [AC-52](../../../../spec/receipt-bound-role-supervision/r06-r03-00-immutable-admission.md), and [BDG-R03-00-20260816-003](BDG-R03-00-20260816-003.md). |

BDG-003 is the only candidate for a later exact owner approval. This decision creates no receipt,
attempt, claim, host effect, branch, dispatch, implementation, or integration.
