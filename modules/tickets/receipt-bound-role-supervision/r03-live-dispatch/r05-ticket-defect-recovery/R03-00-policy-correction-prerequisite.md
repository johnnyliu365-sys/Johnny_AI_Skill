# R03-00 — Revision-05 bootstrap policy correction prerequisite

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / HIGH_ASSURANCE_REQUIRED / BLOCKED / NON_DISPATCHED` / `R03-00-CS-01` |
| Authority | `PRD-20260816-028` / `CHG-20260816-028`; [`REQ-20260816-028`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md); Revision 05 AC-40, AC-45, AC-47; [`DEC-20260816-523`](DEC-20260816-523-r05-recovery-decomposition.md) |
| Context / baseline | [`Revision-05 Context`](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md) / `07744bb95fa1be3d6728f81ba0076b192ac1782a` |
| Model / resources | high-assurance implementation admission required; no owner, task, worktree, branch, grant, receipt, or ContextView bound in this draft |
| Effect / XSS | control-policy and local Router validation only; no host/Agent/Git/target/external effect; `XSS_N/A` |

## Observable closure and scope

Align written Workflow and CodeReview bootstrap rules with one executable typed Router policy that
recognizes only Revision-05 `R03-01A` through `R03-01D`, rejects all other no-receipt bootstrap
identities, preserves claim-before-effect/manual-relay/one-grant requirements, and cannot claim
normal receipt-dispatch capability. The policy either admits an exact valid bridge/grant or returns
a finite blocker before any implementation-owner or host effect.

Only this later implementation commit may modify:

```text
Workflow.md
CodeReview.md
library/workflow_router/contracts.py
library/workflow_router/bootstrap_policy.py
library/workflow_router/router.py
library/workflow_router/__init__.py
tests/test_r05_bootstrap_policy.py
tests/test_plugin_policy_and_response.py
```

`bootstrap_policy.py` owns validated Revision-05 identity/phase policy; `router.py` consumes
it as a composition dependency. Neither parses Markdown, makes a host call, issues a receipt,
selects an owner, or creates a pending dispatch. No old grant/attempt/result or failed source bytes
are authority.

## TDD and verification

| Cell | First red | Green proof |
| --- | --- | --- |
| `R03-00-T01` policy identity | `python -B -m unittest tests.test_r05_bootstrap_policy.BootstrapIdentityTests` after the test exists but before `bootstrap_policy.py` exists | every allowed phase, wrong project/ticket/revision/order and missing bridge returns a finite typed result |
| `R03-00-T02` Router composition | `python -B -m unittest tests.test_r05_bootstrap_policy.RouterBootstrapCompositionTests` before Router wiring | no policy result creates a receipt, pending descriptor, owner wake or host effect; invalid/unsupported bridge fails closed |
| `R03-00-T03` source gate | `python -B -m unittest tests.test_r05_bootstrap_policy.BootstrapPolicySourceGateTests` before public policy exists | reverse mutations for raw policy text, Revision-04-only fallback, dynamic lookup and normal-dispatch projection turn red then restore |

Verification: focused tests; strict explicit-package-base mypy over exactly listed Python files
using an owner-owned external cache; in-memory compile; scope/diff checks; isolated independent
review matrix. The obsolete `python -m mypy --strict library tests` is not a substitute.

## Return and rollback

Return `COMPLETED`, `BLOCKED`, or `CHANGE_DETECTED` with named evidence; completion does not
dispatch R03-01A. Rollback reverts only this future policy integration commit. Current disposition:
`UPSTREAM_DECISION_REQUIRED / BOOTSTRAP_POLICY_BRIDGE_MISSING`; no implementation, grant, attempt,
dispatch, or integration is legal until an exact owner-approved bridge exists.
