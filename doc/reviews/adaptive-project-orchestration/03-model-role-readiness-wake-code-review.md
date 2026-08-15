# R03 Model-role readiness and wake gate — independent code review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `03-model-role-readiness-wake` / `CLOSURE-ADAPTIVE-ROUTER-R03-01` ACX1-ACX8 revision `r03-02` |
| Dispatch registry / receipt | `599c5d5cf24e35143752937306e1ec64ba39f4b9` (`PRG-20260815-507`) / `rcpt-adaptive-router-r03-20260815` |
| Implementation / handoff | `77d86a047767e797ddbb3fc86e5c6b320434ee35` / `3a8e306f534e59b22c054c6debd01008d93c978f` (`PRG-20260815-508`) |
| Owner / permanent lane | task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` / `codex/implementation-router-model-role-readiness-r03` |
| Review result | `CHANGES_REQUESTED / EVIDENCE_DEFECT / SAME_BRANCH_CORRECTION` |

The returned task, receipt binding, implementation ancestry, scope, clean worktree and ordinary
focused behavior checks are valid. Approval is withheld solely because ACX7 requires a source
gate that proves the exact decision predicates; the committed gate accepts altered comparison
operators and compound conditions that bypass the asserted semantics. This is an evidence defect,
not a production-behavior, architecture, requirement or ticket defect.

## Admission and independent verification

| Check | Result / evidence |
| --- | --- |
| Product/task readback | PASS: task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` is completed/idle at its exact permanent implementation root and returned `ACTION_COMPLETED / REVIEW_HANDOFF`. |
| Receipt / Git identity / ancestry | PASS: control is clean at registry `599c5d5`; implementation root, linked Git pointer and branch are exact; registry is an ancestor of `77d86a0`, which is an ancestor of `3a8e306`. |
| Scope / residue / topology | PASS: implementation changes exactly the six frozen paths, handoff changes only `doc/WorkProgressReport.md`, `git diff --check` passes, tracked/ignored porcelain is clean, and exactly three registered worktrees remain. |
| Focused behavior | PASS: independently ran readiness plus Router regression `61/61`. |
| Strict type / in-memory compile | PASS: strict mypy found no issue in `158` files with an external cache removed afterwards; in-memory Python compilation found `0` syntax errors across the same roots. |
| Full serial suite | INCONCLUSIVE: reviewer replay ran without an observed failure stream but reached the local 64-second command ceiling before aggregate completion. Submitted handoff evidence remains `604/604`; it is not substituted as an independent replay. |

## Mandatory review checks

- **Strong types, public contracts and profile construction:** PASS for finite strict models,
  frozen RouterModel boundaries and complete role assignments.
- **Logic and error behavior:** PASS for the tested deterministic decision order, owner wait,
  blocker priority, closure, open-design and supervisor cases.
- **Security, effects and dependencies:** PASS. The reviewed gate is pure metadata validation;
  no renderer, browser, privileged JavaScript, dynamic member lookup, host, filesystem, Git,
  Agent, network or external effect is present. `XSS_NOT_APPLICABLE`.
- **Test truthfulness:** FAIL for ACX7 exact semantic source-gate proof.
- **Ticket, receipt and source conformity:** PASS except ACX7 until the bounded test correction
  below is completed. No out-of-scope path or dependency was introduced.

## Finding

**CR-R03-001 — `EVIDENCE_DEFECT`, blocking ACX7.**

`tests/test_workflow_model_role_readiness.py::_source_gate` recognises a generic closure comparison
and any nested comparison containing `RoleActivityState.ACTIVE`; it does not assert the exact
operator or compared operands. It also recognises only the simple blocker attribute condition.
The reviewer altered source text in memory only and called the committed source gate; no altered
module was written, compiled, imported or executed:

| Semantic bypass | Exact mutation | Gate result |
| --- | --- | --- |
| Closure subset bypass | `closure_kinds != expected_closure_kinds` -> `closure_kinds <= expected_closure_kinds` | **ACCEPTED** |
| Closure reverse-subset bypass | `closure_kinds != expected_closure_kinds` -> `closure_kinds >= expected_closure_kinds` | **ACCEPTED** |
| Supervisor inverse bypass | `supervisor.activity_state is RoleActivityState.ACTIVE` -> `supervisor.activity_state is not RoleActivityState.ACTIVE` | **ACCEPTED** |
| Blocker compound bypass | `if request.blockers:` -> `if request.blockers and False:` | **ACCEPTED** |

The pristine production source still has the specified predicates and focused behavior tests pass;
this finding does not claim an observed runtime violation. It rejects the unsupported claim that
the committed source gate itself establishes ACX7's required exact semantic protection.

## Required same-branch correction

Keep the ticket, owner, permanent worktree, branch, allocation and receipt unchanged. Change only
`tests/test_workflow_model_role_readiness.py`, then create one WPR-only handoff. Strengthen the
bounded AST source gate so it proves all of the following exact conditions within
`ModelRoleReadinessGate.assess`:

1. the blocker branch is exactly the direct `request.blockers` truthiness condition;
2. closure is `closure_kinds != expected_closure_kinds` using `ast.NotEq` and those exact names;
3. supervisor activity is `supervisor.activity_state is RoleActivityState.ACTIVE` using `ast.Is`
   and those exact member operands.

Add the four in-memory reversals above to the committed test and prove each is rejected without
writing, compiling, importing or executing altered source. Retain the five ticket-mandated
reversals and generic type/effect checks. Re-run the ticket's focused/Router/full serial/strict
type/in-memory compile/source/scope/diff/ancestry/topology/porcelain/cache matrix. A production
change, broader test scope or any requirement change is `CHANGE_DETECTED`.

No new ticket, branch, worktree, receipt, allocation, helper, integration, push, package/install,
target-project, external/host/network effect, Secret, release or deployment is authorized.

## Correction terminal recheck

| Field | Result / evidence |
| --- | --- |
| Returned correction | Test-only `283f975f6be438e25227c0e2605f42e7d42bb2d3`; WPR-only `2f1d0d67e8ae70f15e0d11bd34d8b8c73444a197`; parent implementation `77d86a047767e797ddbb3fc86e5c6b320434ee35` remains immutable. |
| Exact source-gate replay | PASS: pristine source is accepted; closure `!=` -> `<=`, closure `!=` -> `>=`, supervisor `is` -> `is not`, and blocker truthiness -> `and False` are all rejected in memory without writing, compiling, importing or executing altered source. |
| Independent verification | PASS: readiness plus Router `62/62`; strict mypy has no issue in `158` files with external cache removed; in-memory Python compile `158/158`; correction scope is only the authorized test and handoff is WPR-only; ancestry, diff check, clean porcelain and exact three-worktree topology pass. Submitted serial evidence is `605/605`. |
| CR-R03-001 | CLOSED. The committed test source gate now binds the direct blocker condition, exact closure `ast.NotEq` operands and exact supervisor `ast.Is` operands, with the review's four mutation proofs. |
| Review result | `APPROVED / GUARDED_INTEGRATION_AUTHORIZED` |

Integrate only `2f1d0d67e8ae70f15e0d11bd34d8b8c73444a197` after a read-only merge guard proves
there is no source/test conflict. An append-only WPR overlap, if any, may be resolved only by
retaining the distinct PRG-509, PRG-510 and PRG-511 records exactly once and without altering
reviewed source/test commits. No push, release, deployment, package/install, target-project,
external or Secret effect is authorized.
