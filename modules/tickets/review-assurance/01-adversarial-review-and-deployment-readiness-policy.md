# 01｜Adversarial review and deployment-readiness policy

| Field | Value |
| --- | --- |
| State | `APPROVED / DISPATCHABLE / CLOSURE_REVISION_02` |
| Feature / ticket | `review-assurance / 01-adversarial-review-and-deployment-readiness-policy` |
| Requirement / specification | `PRD-20260827-042` / `CHG-20260827-042`; `SPEC-AI-WORKFLOW-REVIEW-ASSURANCE-20260827-01KZ9A1B2C3D4E5F6G7H8J9K0L` |
| Context / ADR | `doc/context/review-assurance/main.md`; `ADR-20260827-030-adversarial-review-and-deployment-readiness.md` |
| Baseline | `ac68374546d3f324ca60c175014e7eb6bf2751f9` |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11 strict tests plus policy Markdown. The bounded implementation owner is `Luna / xhigh`; the named reviewer is `Terra / xhigh` and retains all conclusions/integration. |
| XSS / effects | `XSS_NOT_APPLICABLE`. This ticket changes only policy source and deterministic tests. It creates no Agent task, runner, queue, receipt, descriptor, host capability, provider call, secret/configuration access, production-data/account use, migration, release, deployment, publication, target-project or durable-storage effect. |
| Closure revision | `02` — reissued after initial review plus one correction exposed the inherited `COMPACT` helper-table contradiction. The sealed specification already authorizes optional `COMPACT` adversarial audit; this revision makes the table/role proof an explicit closure item. |

## Boundary declaration (machine-readable; the integration gate reads this before mutation)

```johnny-boundary
modify = CodeReview.md
modify = skills/johnny-project-takeover/SKILL.md
modify = skills/johnny-project-takeover/references/review-checks.md
modify = skills/johnny-project-takeover/references/adversarial-review.md
modify = skills/johnny-project-takeover/references/delivery-profile.md
modify = skills/johnny-project-takeover/references/model-role-routing.md
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
modify = tests/test_adversarial_review_policy.py
forbid = .claude-plugin/
forbid = install.ps1
forbid = johnny-router.ps1
forbid = README.md
forbid = requirements-runtime.lock
forbid = modules/tickets/
forbid = doc/
forbid = payload-manifest.json
```

## User decision and observable result

The owner authorized a reviewer-arranged adversarial subagent at ticket review and a deployment
challenge that tries to prove the candidate will fail. The observable result is policy that makes
the audit bounded, finite, same-lifetime-aware and non-authoritative; makes its requiredness
risk-scaled; and prevents release/deployment readiness from silently skipping applicable data,
compatibility, configuration, recovery or observability risks.

## Scope, dependency and roles

### Role assignment

| Role | Assignment / boundary |
| --- | --- |
| Reviewer / integration owner | Current Terra/xhigh supervisor. Reads actual candidate and retains review conclusion, counter-mutation, control-plane admission, push and remote readback. |
| Implementation owner | Reused Luna/xhigh agent in one repository-contained worktree. It makes no commit, no policy pin, no integration and no external effect. |
| Future adversarial auditor | Not invoked by this ticket. The delivered policy constrains it as a reviewer-owned read-only/no-code `RESEARCH_HELPER`, not an implementation owner or co-reviewer. |

### In scope

- `CodeReview.md`, the takeover skill index and three canonical review/profile/role references;
- a new `adversarial-review.md` reference containing plan/return and deployment-matrix contracts;
- correction of the stale universal receipt/descriptor wording in `review-checks.md`;
- repinning the changed `review-checks.md` bytes in both required policy-pin locations;
- deterministic tests for policy content, policy pinning and control-plane admission.

### Out of scope

- invoking an auditor, creating a runtime dispatch API or adding persistent state;
- granting access to production systems, data, accounts, secrets or environment configuration;
- deploying, releasing, publishing or regenerating/installing plugin payload;
- changing target-project governance documents.

## TDD design

| ID | First-red / green behavior |
| --- | --- |
| TARA1 | A new policy-contract test fails until `CodeReview.md` indexes the adversarial reference and preserves reviewer-only conclusion/integration. |
| TARA2 | It fails until the reference binds a same-lifetime direct audit lane, finite auditor returns, and explicitly excludes runner/queue/receipt/live descriptor prerequisites. |
| TARA3 | It fails until the `COMPACT` profile cell admits one optional adversarial plan but no ordinary helper; `STANDARD` stays optional; `HIGH_ASSURANCE`/proposed deployment are required; and named `UNAVAILABLE`/`BLOCKED` handling is present. |
| TARA4 | It fails until all required ticket-level and deployment matrix attack vectors are present with evidenced `NOT_APPLICABLE` and `NOT_AUTHORIZED` semantics. |
| TARA5 | It fails until the auditor/effect boundary rejects approval, integration, commit, push, secret, production-data/account, migration, release and deployment authority. |
| TARA6 | Existing Router profile tests fail if the changed `review-checks.md` is not exactly repinned in both required locations. |
| TARA7 | Existing control-plane tests prove a changed pinned policy without an exact repin cannot reach `main`. |

### Required reviewer reverse mutations

1. Remove the same-lifetime exception or reintroduce the old universal descriptor/receipt claim;
   `TARA2` must turn red.
2. Revert the `COMPACT` helper-table cell to `Not admitted`; `TARA3` must turn red.
3. Remove the deployment-matrix `NOT_APPLICABLE` evidence rule or the external-effect authority
   rule; `TARA4` or `TARA5` must turn red.
4. Restore the exact reviewed candidate before control-plane admission. Zero red is an
   `EVIDENCE_DEFECT`.

## Completion and evidence

The implementation return is `COMPLETED → ACTION_COMPLETED` only after the declared focused
tests, strict type check and full suite are reported. The reviewer independently verifies the
exact nine boundary paths, runs the reverse mutations through a different door, checks the
policy digest/repins, and runs `admit_control_plane_mutation`. Success is only the exact candidate
SHA reported as `integrated_commit`, followed by non-force push and exact `origin/main` SHA
readback. Review approval does not publish or deploy the plugin.

## Return and rollback

`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill` applies to any proposed runtime service,
physical host isolation requirement, new public Agent authority, or actual effect. A normal
policy/test defect receives one additive correction on the same candidate. Rollback after
integration is a new reviewed additive revert; never reset, amend, force or delete evidence.
