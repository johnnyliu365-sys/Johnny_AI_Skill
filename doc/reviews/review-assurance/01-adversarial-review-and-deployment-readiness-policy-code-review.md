# Ticket 01 — Adversarial review and deployment-readiness policy: code review

| Field | Value |
| --- | --- |
| Conclusion | `APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED` |
| Ticket / closure | `review-assurance/01-adversarial-review-and-deployment-readiness-policy` / revision `02` |
| Authority | `PRD-20260827-042` / `CHG-20260827-042`; `SPEC-AI-WORKFLOW-REVIEW-ASSURANCE-20260827-01KZ9A1B2C3D4E5F6G7H8J9K0L`; `ADR-20260827-030` |
| Ticket baselines / candidate | `f0bb733fa07167de69c7ac30ee71c3b57cacdf07` / closure-revision-02 baseline `e5e749d8de17337caa36fd0b2369560355be096b` / `9c87915267d909c88ac9f3490609d4ccb6c4a0e7` |
| Candidate branch | `control/review-assurance-01-adversarial-review-and-deployment-readiness-policy` |
| Reviewer / implementation | `ticket-review` — Terra/xhigh / `implementation-standard` — Luna/xhigh |
| Scope | The exact nine paths declared in the ticket boundary; no runtime or external-effect behavior. |

## Admission and boundary

The candidate descends from the revision-02 ticket baseline, was clean before control-plane
admission, and modified exactly:

1. `CodeReview.md`;
2. `skills/johnny-project-takeover/SKILL.md`;
3. `review-checks.md`, `adversarial-review.md`, `delivery-profile.md` and
   `model-role-routing.md` below the takeover references;
4. `library/workflow_router/profile.py`;
5. `tests/test_workflow_router.py` and `tests/test_adversarial_review_policy.py`.

The candidate did not change the ticket, payload declaration, package version, installer,
runtime provider/host integration, queue, receipt, runner, deployment or target project. The
only changed pinned reference is `review-checks.md`; its normalized SHA-256 was independently
recomputed and matched both policy pin sites.

This policy is itself a same-lifetime reviewer-owned lane. No runner, queue, receipt, descriptor
or host-readback capability was assumed. The policy truthfully limits a future helper to evidence;
the current ticket did not invoke one.

## Closure evidence

| Closure item | Reviewer evidence |
| --- | --- |
| TARA1 | `CodeReview.md` indexes the new policy and states that the reviewer alone concludes and integrates. |
| TARA2 | The audit plan binds candidate SHA/Closure Set, uses one direct same-lifetime `RESEARCH_HELPER` wait, has finite return states, and explicitly keeps runner/queue/receipt/live descriptor/host readback `NOT_REQUIRED`. |
| TARA3 | The profile and role docs now distinguish ordinary research from one adversarial plan: COMPACT has no ordinary helper but may use one optional auditor; STANDARD is optional; HIGH_ASSURANCE/proposed release/deployment must use one. Missing required evidence is `BLOCKED`. |
| TARA4 | The reference enumerates spec gap, boundary data, state, concurrency, errors, authorization, consistency, idempotency, regression, observability and deployment vectors; matrix statuses include evidenced `NOT_APPLICABLE` and visible `NOT_AUTHORIZED`/`BLOCKED`. |
| TARA5 | A helper cannot approve, integrate, commit, push, dispatch, alter artifacts, read secret/configuration/production data, use a production account, migrate, publish, release or deploy. Those actions require target-bound owner authority and readback. |
| TARA6–7 | The universal cross-lifetime descriptor/receipt wording is corrected, and `review-checks.md` is exactly re-pinned in the private profile and its Router regression expectation. |

Reviewer-run commands:

```text
py -3.11 -m pytest tests/test_adversarial_review_policy.py tests/test_workflow_router.py tests/test_control_plane_mutation.py -q
# 118 passed, 298 subtests passed

py -3.11 -m mypy --strict library/workflow_router/profile.py tests/test_adversarial_review_policy.py tests/test_workflow_router.py
# Success: no issues found in 3 source files

py -3.11 -m compileall -q library/workflow_router tests/test_adversarial_review_policy.py tests/test_workflow_router.py
git diff --check
```

## Convergence and reviewer counter-mutation

Revision 01's first correction resolved a HIGH_ASSURANCE helper ambiguity. The next independent
review found that the inherited COMPACT table cell still said the helper was not admitted while
the sealed specification authorized a compact optional adversarial audit. Per the convergence
limit, this became `TICKET_DEFECT / CONVERGENCE_REVIEW_REQUIRED`; the reviewer raised the ticket
to closure revision 02 and rebased the candidate before a fresh review, rather than issuing a
third correction on the old closure.

For revision 02, the reviewer used two mutations different from the implementer's compact-table
mutation:

1. changed the actual direct-lane declaration from `NOT_REQUIRED` to `BRIDGE_REQUIRED`; TARA2
   failed with the missing `NOT_REQUIRED` proof;
2. changed the HIGH_ASSURANCE role contract from `must consume` to `may consume`; TARA3 failed
   on the exact required-audit assertion.

Both were restored byte-for-byte before final verification and admission. They prove the tests
pin the policy doors reviewers actually read, rather than merely matching a test fixture.

## Regression and residual risk

The candidate full suite result was:

```text
1848 passed, 31 skipped, 3873 subtests passed in 565.01s
```

It has three failures. The reviewer ran the same three cells on clean `main`; all failed
unchanged, so no ticket regression is claimed:

1. stale plugin-publication metadata pin;
2. refusal-guidance enum roster drift;
3. installed pytest `9.0.3` versus declared `9.1.1`.

No global-green claim is made. The shipped policy defines evidence only; it does not physically
guarantee read-only host isolation. The isolation disposition remains explicit, and a required
unavailable capability blocks rather than fabricating a pass.

## Integration evidence

The reviewer committed candidate `9c87915267d909c88ac9f3490609d4ccb6c4a0e7`.
`admit_control_plane_mutation` returned `INTEGRATED` with exactly that SHA.
A non-force push followed, and direct `git ls-remote origin refs/heads/main` readback returned
the same SHA. This documents-only closure must itself be pushed and read back before it is final.

