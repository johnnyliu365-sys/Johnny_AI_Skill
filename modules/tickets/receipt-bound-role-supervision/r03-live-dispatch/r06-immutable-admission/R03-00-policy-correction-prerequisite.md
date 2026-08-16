# R03-00 policy correction prerequisite — CS-02

## Admission

| Field | Value |
| --- | --- |
| Ticket / closure / state | `R03-00-policy-correction-prerequisite` / `R03-00-CS-02` / `ADMITTED_FOR_BPB_ROUTE / HIGH_ASSURANCE_REQUIRED / OWNER_GRANT_REQUIRED` |
| Authority | [REQ-20260816-030](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-030.md); [immutable admission](../../../../../modules/spec/receipt-bound-role-supervision/r06-r03-00-immutable-admission.md); [BPB-002](../../../../../modules/spec/receipt-bound-role-supervision/r06-r03-00-policy-bridge-02.md); [CR-BPB-R03-00-004](../../../../../doc/reviews/receipt-bound-role-supervision/BPB-R03-00-immutable-admission-review.md); [DEC-20260816-525](DEC-20260816-525-r03-00-cs02-ticket-ref-correction.md) |
| Context / view | [Revision-07 Context](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev07-r03-00-immutable-admission.md) / `ctx-r03-00-cs02-001`; this ticket, its five authority artifacts, [implementation TDD](../../../../../skills/johnny-project-takeover/references/implementation-tdd.md), and the explicitly edited bootstrap anchors only |
| Bound implementation owner | `IMPLEMENTATION_OWNER_2` / task `019ffb0c-db88-7303-895c-aecfadde7c8d` / opaque worktree `worktree-implementation-02` / fresh branch `codex/implementation-r03-00-policy-correction-cs02` / `gpt-5.6-luna / xhigh` |
| Branch / baseline rule | The released owner branch is not descendant of this admission registry, so the named fresh branch is required. Execution baseline is derived only by a later `CLAIM_INTRODUCTION_COMMIT`; no earlier fixed baseline is legal. |
| Receipt / effects / XSS | No receipt exists. Local typed policy validation only; no host, task, worktree, Agent, Git, target-project, network, provider, install, release, deployment, secret, browser, WebView, DOM, or JavaScript effect. `XSS_NOT_APPLICABLE`. |

## One observable closure

Implement the typed, no-receipt bootstrap-policy decision for exact
`AI控制工作workflow / R03-00-policy-correction-prerequisite / R03-00-CS-02`.
It recognizes only BPB-002 after its approved review, yields a finite typed failure for every
other input, and makes a derived claim-introduction commit the sole execution-baseline rule for a
later owner-approved grant. It must not create a grant, attempt, receipt, pending descriptor,
owner selection, host call, or normal Router capability.

## Exact writable scope and Composition Root

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

`contracts.py` owns frozen public types. `bootstrap_policy.py` owns
validated boundary conversion and a finite `BootstrapPolicyDecision` algebra:
success contains only non-null validated route metadata; failure contains exactly one of
`IDENTITY_MISMATCH`, `PHASE_MISMATCH`,
`REVIEW_UNAPPROVED`, `TICKET_BINDING_MISMATCH`, or
`CLAIM_BASELINE_INVALID`. No `Any`, implicit null, dynamic mapping, or
string convention may cross its boundary.

`router.py` only consumes the injected decision. It does not parse Markdown, select
an owner, bind workspace/branch, make a host call, issue a receipt, create a pending descriptor,
or project this exception into normal dispatch. `__init__.py` exports the typed public
contract; tests are the composition seam.

| Condition | Required result | Required absence |
| --- | --- | --- |
| Exact project/ticket/closure, BPB-002 review, later valid claim metadata | success and `CLAIM_INTRODUCTION_COMMIT` rule | receipt, descriptor, owner wake, host effect |
| Wrong project, ticket, closure, review identity, or phase | exact finite identity/phase/review/ticket failure | every effect |
| Earlier baseline, missing/malformed/mismatched/non-derived claim commit | `CLAIM_BASELINE_INVALID` | every effect |
| Attempted normal-dispatch projection | finite failure | normal-capability claim and effect |

## Finite TDD and verification

| Cell | Exact first red | Green and reverse proof |
| --- | --- | --- |
| `R03-00-CS02-T01` | `python -B -m unittest tests.test_r05_bootstrap_policy.BootstrapAdmissionContractTests` before `bootstrap_policy.py` exists | exact identity succeeds; each wrong identity/phase/null-like input returns its named finite failure |
| `R03-00-CS02-T02` | `python -B -m unittest tests.test_r05_bootstrap_policy.ClaimIntroductionBaselineTests` before baseline validation | only a valid derived claim commit is accepted; absent, malformed, mismatched, non-ancestral, and fixed-earlier values fail closed |
| `R03-00-CS02-T03` | `python -B -m unittest tests.test_r05_bootstrap_policy.RouterBootstrapCompositionTests` before Router wiring | no policy result makes receipt/descriptor/owner/host/normal-dispatch effects |
| `R03-00-CS02-T04` | `python -B -m unittest tests.test_r05_bootstrap_policy.BootstrapPolicySourceGateTests` before public policy | admitting BPB-001 or CS-01, restoring fixed baseline, and dynamic normal projection turn red then restore |

```text
python -B -m unittest discover -s tests -p "test_*.py"
python -m mypy --strict --explicit-package-bases --no-incremental --cache-dir <owner-external-cache> library/workflow_router/contracts.py library/workflow_router/bootstrap_policy.py library/workflow_router/router.py library/workflow_router/__init__.py tests/test_r05_bootstrap_policy.py tests/test_plugin_policy_and_response.py
python -B -c "from pathlib import Path; paths=('library/workflow_router/contracts.py','library/workflow_router/bootstrap_policy.py','library/workflow_router/router.py','library/workflow_router/__init__.py','tests/test_r05_bootstrap_policy.py','tests/test_plugin_policy_and_response.py'); [compile(Path(p).read_text(encoding='utf-8'),p,'exec') for p in paths]"
git diff --check
```

Use and remove an owner-owned external mypy cache; prove exact scope and tracked/ignored/cache
readback.

## Resource, return, and rollback

One Luna xhigh high-assurance lane; no helper. A later Senior grant draft plus independent
owner approval are prerequisites, not work in this closure. Return `COMPLETED`,
`HALT / <finite reason>`, or `CHANGE_DETECTED` with implementation-commit
evidence only; no WPR append or docs-only handoff. Rollback reverts only a later reviewed
integration commit. This is `HIGH_ASSURANCE_REQUIRED` because it proves a privileged
bootstrap gate and its absence-of-effects contract as one vertical closure.
