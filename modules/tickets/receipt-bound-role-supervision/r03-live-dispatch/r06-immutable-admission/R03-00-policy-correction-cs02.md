# R03-00 Revision-06 immutable-admission policy correction

## Admission

| Field | Value |
| --- | --- |
| Ticket / closure / state | `R03-00-policy-correction-cs02` / `R03-00-CS-02` / `ADMITTED_FOR_BPB_ROUTE / HIGH_ASSURANCE_REQUIRED / OWNER_GRANT_REQUIRED` |
| Authority | [REQ-20260816-030](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-030.md); [immutable admission](../../../../../modules/spec/receipt-bound-role-supervision/r06-r03-00-immutable-admission.md); [BPB-002](../../../../../modules/spec/receipt-bound-role-supervision/r06-r03-00-policy-bridge-02.md); [CR-BPB-R03-00-004](../../../../../doc/reviews/receipt-bound-role-supervision/BPB-R03-00-immutable-admission-review.md) |
| Context / view | [Revision-07 Context](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev07-r03-00-immutable-admission.md) / `ctx-r03-00-cs02-001`; only this ticket, the four authority artifacts in this row, [implementation TDD](../../../../../skills/johnny-project-takeover/references/implementation-tdd.md), and the anchored bootstrap sections edited below are loaded |
| Bound implementation owner | `IMPLEMENTATION_OWNER_2` / task `019ffb0c-db88-7303-895c-aecfadde7c8d` / opaque worktree `worktree-implementation-02` / fresh branch `codex/implementation-r03-00-policy-correction-cs02` / `gpt-5.6-luna / xhigh` |
| Branch / baseline rule | The named fresh branch is required because the released owner branch is not descendant of this admission registry. Its execution baseline is derived only by a later `CLAIM_INTRODUCTION_COMMIT`; no fixed earlier baseline is valid. |
| Receipt / effects / XSS | No receipt exists in this closure. Local typed policy validation only; no host, task, worktree, Agent, Git, target-project, network, provider, install, release, deployment, secret, browser, WebView, DOM, or JavaScript effect. `XSS_NOT_APPLICABLE`. |

## Observable closure

Implement the one typed, no-receipt bootstrap-policy decision for exact
`AI控制工作workflow / R03-00 / R03-00-CS-02`. It must admit only the
approved BPB-002 route after its review, retain a finite typed failure for every other input,
and make a derived claim-introduction commit the only possible execution baseline for a later
owner-approved grant. This closure does not create a grant, attempt, receipt, pending descriptor,
owner selection, host call, or normal Router capability.

## Exact writable scope and ownership

Only the implementation commit may modify:

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

`contracts.py` owns the frozen public value types. `bootstrap_policy.py`
owns boundary validation and a named finite `BootstrapPolicyDecision` algebra:
success contains only validated route metadata; failure contains exactly one member of
`IDENTITY_MISMATCH`, `PHASE_MISMATCH`,
`REVIEW_UNAPPROVED`, `TICKET_BINDING_MISMATCH`, or
`CLAIM_BASELINE_INVALID`. It accepts no `Any`, dynamic object, implicit
null, string convention, or unvalidated external mapping inward.

`router.py` consumes that injected decision only. It must not parse Markdown, select
an owner, bind a worktree or branch, make a host call, issue a receipt, construct a pending
descriptor, or project this exceptional route into normal dispatch. `__init__.py`
exports only the typed public contract. Tests are the composition seam.

## Contract and finite failure matrix

| Input condition | Required typed decision | Effect invariant |
| --- | --- | --- |
| Exact project, `R03-00`, `R03-00-CS-02`, BPB-002 review, and later valid claim-introduction metadata | success with exact route metadata and `CLAIM_INTRODUCTION_COMMIT` rule | no receipt, descriptor, owner wake, or host effect |
| Project, ticket, closure, review identity, or phase differs | one exact identity/phase/review/ticket failure | no effect |
| Earlier fixed baseline, absent claim commit, malformed commit identifier, or non-derived baseline | `CLAIM_BASELINE_INVALID` | no effect |
| Attempt to use an exceptional result as normal dispatch | finite failure | no normal-capability claim or effect |

All nullable input is normalized at the boundary into an explicit optional named field before
the algebra. A successful decision has non-null route metadata; every failed decision has no
grant, receipt, descriptor, owner, host, or transport output.

## Finite TDD plan

| Cell | Exact first-red command | Green and adversarial proof |
| --- | --- | --- |
| `R03-00-CS02-T01` admission identity | `python -B -m unittest tests.test_r05_bootstrap_policy.BootstrapAdmissionContractTests` before `bootstrap_policy.py` exists | exact route succeeds; wrong project, ticket, closure, review, phase, and null-like input each return the named finite failure |
| `R03-00-CS02-T02` claim baseline | `python -B -m unittest tests.test_r05_bootstrap_policy.ClaimIntroductionBaselineTests` before claim-baseline validation | only a valid derived claim commit is accepted; absent, malformed, mismatched, non-ancestral, and reintroduced fixed-earlier baselines fail closed |
| `R03-00-CS02-T03` Router composition | `python -B -m unittest tests.test_r05_bootstrap_policy.RouterBootstrapCompositionTests` before Router wiring | policy consumption cannot create receipt/descriptor, select or wake owner, call host, or activate normal dispatch |
| `R03-00-CS02-T04` source gates | `python -B -m unittest tests.test_r05_bootstrap_policy.BootstrapPolicySourceGateTests` before public policy | reverse mutations that admit BPB-001 or CS-01, restore an earlier baseline, or dynamically project to normal dispatch each turn red and are restored |

Run focused cells above, then:

```text
python -B -m unittest discover -s tests -p "test_*.py"
python -m mypy --strict --explicit-package-bases --no-incremental --cache-dir <owner-external-cache> library/workflow_router/contracts.py library/workflow_router/bootstrap_policy.py library/workflow_router/router.py library/workflow_router/__init__.py tests/test_r05_bootstrap_policy.py tests/test_plugin_policy_and_response.py
python -B -c "from pathlib import Path; paths=('library/workflow_router/contracts.py','library/workflow_router/bootstrap_policy.py','library/workflow_router/router.py','library/workflow_router/__init__.py','tests/test_r05_bootstrap_policy.py','tests/test_plugin_policy_and_response.py'); [compile(Path(p).read_text(encoding='utf-8'),p,'exec') for p in paths]"
git diff --check
```

Use an owner-owned external mypy cache and remove it before completion. Also prove exact scope,
tracked/ignored porcelain, and cache readback.

## Resource, dependency, return, and rollback

One high-assurance Luna xhigh lane; no helper or parallel lane. Dependency is the sealed BPB-002
review and this admission registry. A later Senior-only grant draft and independent owner approval
are required before any execution claim; they are not part of this ticket.

Return exactly `COMPLETED`, `HALT / <finite reason>`, or
`CHANGE_DETECTED` with implementation-commit evidence only. No WorkProgressReport
append or docs-only handoff is authorized. Rollback reverts only the later reviewed integration
commit; it never rewrites historical evidence.

## Ticket decomposition decision

`HIGH_ASSURANCE_REQUIRED`: this is one independently observable vertical closure
because it changes the privileged bootstrap-policy gate while proving its absence-of-effects
contract. It is not split by file count or implementation duration.
