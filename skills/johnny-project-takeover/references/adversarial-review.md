# Adversarial review and deployment readiness

Read this reference for reviewer-owned adversarial verification or a proposed release/deployment.
It defines evidence policy only. It creates no runtime Agent service, runner, queue, receipt,
descriptor, host gateway or external-effect authority.

## Reviewer-owned audit contract

The reviewer may create one bounded, same-lifetime `RESEARCH_HELPER` audit after binding the exact
candidate commit and approved Closure Set. The helper is read-only/no-code and tries to disprove
the candidate; it is not a co-reviewer. The same-lifetime route is direct: the reviewer invokes the
helper and waits once for its finite return. A runner, queue, receipt, live descriptor and host readback
are `NOT_REQUIRED` for this route. Cross-lifetime handoff keeps the separate receipt and
live-descriptor controls from `review-checks.md`.

The closed `AdversarialReviewPlan` binds:

- `candidate_commit`: the exact candidate SHA under review;
- `closure_revision`: the approved ticket Closure Set revision;
- `profile_requirement`: `OPTIONAL` or `REQUIRED`;
- `attack_categories`: a non-empty finite selection from the attack roster below;
- `isolation_disposition`: `PROVED_READ_ONLY_SNAPSHOT`, `READ_ONLY_INTENT_ONLY` or
  `UNAVAILABLE`;
- `effect_scope`: always `NO_EXTERNAL_EFFECT`.

The helper's finite return is one of `FINDINGS`, `NO_FINDINGS`, `BLOCKED`, `UNAVAILABLE` or
`NOT_APPLICABLE`, and carries only the candidate identity, selected categories, evidence
references and a sanitized reason. A helper return is evidence only: it cannot approve, cannot
integrate, cannot issue an implementation return and cannot act as an effect receipt. The reviewer
independently verifies every finding against source and behavior and alone owns the final review
conclusion and integration.

## Requiredness and unavailable evidence

The audit is optional for `COMPACT` and `STANDARD` unless an approved ticket matrix requires it.
It is mandatory for `HIGH_ASSURANCE` and before a proposed release/deployment. If a mandatory
audit or required isolation/evidence capability is unavailable, the reviewer returns `BLOCKED`;
missing evidence is never silently treated as a pass. A genuinely excluded surface may return
`NOT_APPLICABLE` only with candidate-bound evidence naming the inspected source surface that
excludes it.

## Adversarial attack roster

Every selected plan must try to disprove the candidate across the applicable categories:

1. `SPEC_GAP` — requirement and acceptance completeness;
2. `BOUNDARY_DATA` — null, empty, malformed, oversized and hostile boundary values;
3. `STATE_TRANSITION` — order, repeat submission and lifecycle transitions;
4. `CONCURRENCY` — interleaving and competing operations;
5. `ERROR_PARTIAL_FAILURE` — timeout, exception and partial failure;
6. `AUTHORIZATION` — authorization and tenant isolation;
7. `CONSISTENCY` — cross-view and persisted-state agreement;
8. `IDEMPOTENCY` — retries and duplicate requests;
9. `REGRESSION` — compatibility with existing behavior;
10. `OBSERVABILITY` — safe, sufficient evidence without secrets or raw production data;
11. `DEPLOYMENT_READINESS` — release and deployment assumptions represented in the matrix.

The test name, helper claim or a green suite is not proof by itself. The reviewer must bind each
finding or no-finding to reproducible candidate evidence.

## Deployment readiness matrix

`DeploymentReadinessMatrix` binds the candidate commit, artifact/version identity, declared target
environment, configuration revision and proposed effect scope. Every vector has exactly one of
these finite statuses: `APPLICABLE`, `NOT_APPLICABLE`, `BLOCKED` or `NOT_AUTHORIZED`.
`NOT_APPLICABLE` requires evidence naming the candidate surface that excludes the vector; `BLOCKED`
and `NOT_AUTHORIZED` remain visible and never count as proof of readiness.

The matrix includes these ticket-level and operational/data vectors:

- specification/acceptance gap, boundary data, state order/repeat submission, concurrency,
  timeout/partial failure, authorization/tenant isolation, consistency, idempotency, regression
  and observability;
- SQL migration, production-history compatibility, case/encoding/locale, schema compatibility,
  old-app/new-DB, new-app/old-DB and rollback compatibility;
- environment/configuration/secret-alias and permission differences, staging/production drift,
  DB lock, large-table update/alter, index creation, connection pool, worker/cron/queue/cache
  interaction, deployment/migration interruption, rollback, backup/restore, smoke and
  authorized real-account sampling.

An applicable vector needs candidate-bound evidence. A vector that would require an unavailable
capability is `BLOCKED`; a vector outside the admitted authority is `NOT_AUTHORIZED`. The matrix
cannot turn an excluded check into a readiness claim.

## Authority and effect boundary

The helper and its evidence cannot approve, cannot integrate, cannot commit, cannot push, cannot
dispatch another Agent, cannot modify artifacts, cannot obtain secrets, cannot read configuration,
cannot access production data or a production account, cannot run a migration, cannot publish,
cannot release and cannot deploy. Production data/accounts, secret reads,
migrations, release and deployment are separate owner-scoped external effects requiring their own
approved target-bound ticket and readback. If such proof is needed but not authorized, record
`NOT_AUTHORIZED` or `BLOCKED`; do not perform the effect or infer its result.
