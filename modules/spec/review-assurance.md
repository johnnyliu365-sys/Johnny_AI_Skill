# Reviewer-owned adversarial review and deployment readiness specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-REVIEW-ASSURANCE-20260827-01KZ9A1B2C3D4E5F6G7H8J9K0L` |
| Status | `APPROVED` |
| Author / baseline | Architecture owner / `ac68374546d3f324ca60c175014e7eb6bf2751f9` |
| Context | `doc/context/review-assurance/main.md` (`GRILL_COMPLETE_TO_SPEC`) |
| Requirement | `PRD-20260827-042` / `CHG-20260827-042` |
| Delivery | `POC / HIGH_ASSURANCE`; policy-source implementation only |
| Approval | Project owner, 2026-08-27 (Asia/Taipei): ticket decomposition and the source-only policy implementation are authorized. Publication, release, deployment, migration, production-data/account and secret effects are not. |

## Problem, objective and exclusions

The system must let a reviewer use an independent adversarial perspective to try to prove a
candidate fails its approved contract, and must make deployment claims answerable through a
candidate-bound matrix. The system must not turn a helper into a reviewer, infer a runner/receipt
for a synchronous lane, fabricate capability evidence, or treat review evidence as external-effect
authority.

No target-product source, runtime service, queue, provider, credential, production record,
migration, deployment or publication is in scope for this cluster.

## Public policy contract

### Adversarial audit admission

`AdversarialReviewPlan` is a ticket-bound reviewer artifact with these closed fields:

| Field | Meaning |
| --- | --- |
| `candidate_commit` | Exact candidate SHA to inspect; a changed or unproved SHA invalidates the return. |
| `closure_revision` | Exact approved ticket Closure Set revision. |
| `profile_requirement` | `OPTIONAL` or `REQUIRED`; `HIGH_ASSURANCE` is always `REQUIRED`. |
| `attack_categories` | Non-empty finite selection from `SPEC_GAP`, `BOUNDARY_DATA`, `STATE_TRANSITION`, `CONCURRENCY`, `ERROR_PARTIAL_FAILURE`, `AUTHORIZATION`, `CONSISTENCY`, `IDEMPOTENCY`, `REGRESSION`, `OBSERVABILITY`, `DEPLOYMENT_READINESS`. |
| `isolation_disposition` | `PROVED_READ_ONLY_SNAPSHOT`, `READ_ONLY_INTENT_ONLY`, or `UNAVAILABLE`; the reviewer never overclaims this host capability. |
| `effect_scope` | Always `NO_EXTERNAL_EFFECT`; an external test is excluded and reported as a gap requiring separate authority. |

The auditor's finite return is `FINDINGS`, `NO_FINDINGS`, `BLOCKED`, `UNAVAILABLE` or
`NOT_APPLICABLE`, plus candidate identity, selected categories, evidence references and a
sanitized reason. The return is not an approval, integration request, implementation return or
effect receipt. The reviewer verifies each asserted finding against actual source/behavior and
then retains the only `APPROVED`, `CHANGES_REQUESTED` or `BLOCKED` conclusion.

### Deployment readiness matrix

`DeploymentReadinessMatrix` binds `candidate_commit`, artifact/version identity, declared target
environment, configuration revision and proposed effect scope. Each vector has one finite status:
`APPLICABLE`, `NOT_APPLICABLE`, `BLOCKED` or `NOT_AUTHORIZED`; `NOT_APPLICABLE` includes the
candidate evidence excluding it, and the latter two never count as proof.

The mandatory vector roster is:

1. specification/acceptance gap, boundary data, state order/repeat submission, concurrency,
   timeout/partial failure, authorization/tenant isolation, consistency, idempotency, regression
   and observability;
2. SQL migration, production-history compatibility, case/encoding/locale, schema compatibility,
   old-app/new-DB, new-app/old-DB and rollback compatibility;
3. environment/configuration/secret-alias and permission differences, staging/production drift,
   DB lock, large-table update/alter, index creation, connection pool, worker/cron/queue/cache
   interaction, deployment/migration interruption, rollback, backup/restore, smoke and
   authorized real-account sampling.

## Acceptance criteria

| ID | Acceptance criterion |
| --- | --- |
| ARA-01 | `CodeReview.md` exposes the adversarial-review reference and states that the reviewer alone owns review conclusion and integration. |
| ARA-02 | The policy admits one bounded same-lifetime reviewer-owned `RESEARCH_HELPER` audit with a finite return and no runner, queue, receipt, live descriptor or host-readback prerequisite. |
| ARA-03 | The policy says an audit is optional below `HIGH_ASSURANCE`, mandatory at `HIGH_ASSURANCE` and before a proposed release/deployment, and handles unavailable required evidence as `BLOCKED`. |
| ARA-04 | The attack roster covers all ten ticket-level categories named in the requirement without treating a test name or helper claim as proof. |
| ARA-05 | The deployment matrix has all declared operational/data compatibility vectors and an evidenced `NOT_APPLICABLE` path. |
| ARA-06 | Real production data/accounts, secret/configuration reads, migrations, release and deployment remain separate owner-scoped effects; the policy records missing authority rather than performing them. |
| ARA-07 | `review-checks.md` distinguishes same-lifetime review from the cross-lifetime receipt/descriptor route; it no longer makes the latter a universal multi-Agent prerequisite. |
| ARA-08 | `review-checks.md` repin values in `library/workflow_router/profile.py` and `tests/test_workflow_router.py` match its normalized content exactly. |

## Implementation boundary and handoff

Ticket 01 may update only the source policy documents, the one private Router policy pin and
regression tests declared in its exact `johnny-boundary` block. It may introduce no runtime
model call, background service, persistent queue/receipt/descriptor, effect adapter, deployment
command or host capability wrapper. The implementation owner returns `COMPLETED →
ACTION_COMPLETED`; an ambiguity or altered policy contract returns `CHANGE_DETECTED →
REQUIREMENT_CHANGED → Grill`.

## Verification and reverse mutation

The ticket must add an executable policy-contract test and run the existing policy-pin and
control-plane gate suites. Reviewer evidence must independently remove one same-lifetime
exception and one deployment-matrix guard from a disposable candidate copy, observe named red
cells, then restore the exact candidate before admission. A mutation that produces zero red is an
evidence defect, never a pass.

## Risk, rollback and deployment preconditions

The policy could over-block low-risk review, accidentally make a helper a co-reviewer, or imply
an unavailable host capability. The finite status matrix, profile scaling, reviewer-only verdict
and explicit `UNAVAILABLE`/`NOT_AUTHORIZED` states control those risks. Rollback is an additive
revert of the policy candidate; it does not roll back a deployment because this cluster executes
none. Packaging/publishing a changed plugin payload requires a separate release ticket, owner
authority and readback.

## Lineage and approval

- Sealed Context: `doc/context/review-assurance/main.md` at the documentation baseline commit.
- Requirement leaf: `doc/requirements/active/2026/workflow-governance/REQ-20260827-042.md`.
- Decision: `ADR-20260827-030-adversarial-review-and-deployment-readiness.md`.
- No unresolved product decision remains; policy wording and test implementation are Ticket 01's
  closed scope.

