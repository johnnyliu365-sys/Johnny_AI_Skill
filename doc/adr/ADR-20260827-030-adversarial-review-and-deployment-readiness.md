# ADR-20260827-030 — Reviewer-owned adversarial audit and deployment readiness

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260827-042` / `CHG-20260827-042`
- Refines: `CodeReview.md`, `review-checks.md`, `delivery-profile.md` and
  `model-role-routing.md`. It authorizes no deployment, migration, production-data access,
  credential access, release, provider or target-project action.

## Context

The present review policy correctly requires a reviewer counter-mutation, but a single reviewer
can still share the implementer's framing and overlook a missing acceptance condition or an
unvisited failure path. `HIGH_ASSURANCE` says adversarial verification is required, yet gives no
safe way to request it, preserve its limits, or distinguish an absent same-lifetime helper from a
failed cross-lifetime bridge. Deployment preparation has the same gap: a green test suite is not
evidence that migration, compatibility, configuration, interruption or recovery behavior has
been challenged.

## Decision

1. **The reviewer owns one optional independent audit.** After a candidate SHA and its approved
   Closure Set exist, the reviewer may allocate one bounded `RESEARCH_HELPER` with an
   adversarial-review plan. The helper has read-only/no-code intent and returns evidence only; it
   cannot approve, integrate, commit, push, dispatch another Agent, alter artifacts, obtain
   secrets or execute an external effect.
2. **Same-lifetime use is direct and honest.** The reviewer creates the task, waits once for its
   finite return, independently checks the candidate still matches the bound SHA, and writes the
   final review conclusion. This direct lane is `NOT_REQUIRED` for runner/queue/receipt/live
   descriptor/host-readback infrastructure. Cross-lifetime handoff retains its separate
   receipt-bound controls.
3. **Evidence intensity is risk-scaled.** An audit is optional for `COMPACT` and `STANDARD`
   review unless the ticket's approved matrix makes it required. It is required for
   `HIGH_ASSURANCE` review and before a proposed release/deployment. A required audit that cannot
   be performed returns a named block; it may not be replaced by an invented pass.
4. **The plan tries to disprove the implementation.** It selects applicable attacks across
   specification completeness, boundary inputs, state/order/repeatability, concurrency,
   errors/partial failure, authorization/isolation, consistency, regression and observability.
   Each finding remains subject to the reviewer's source and behavior verification.
5. **Every deployment proposal carries an applicability matrix.** The matrix is bound to the
   candidate/artifact/environment and classifies migration, historical data, encoding/locale,
   schema/app compatibility, rollback, configuration/secrets, permissions/drift, locks,
   duration/index/pools/workers/cache, interrupted deployment/migration, backup/restore, smoke
   and authorized account sampling. `NOT_APPLICABLE` requires a source-based reason;
   `NOT_AUTHORIZED` and `BLOCKED` remain visible.
6. **Review is not effect authority.** A matrix can plan a proof and expose a gap, but it cannot
   read secrets, touch production data, run a migration, use a real account, publish or deploy.
   Each such action needs a separately approved, target-bound effect ticket and post-effect
   readback under `security-boundary.md`.

## Consequences

- Code review gains an independent attack channel without making a second Agent a co-reviewer or
  constructing new runtime dispatch infrastructure.
- A deployment cannot be called ready merely because irrelevant checks were silently skipped.
- A high-assurance ticket that cannot obtain required adversarial evidence stops before
  integration/deployment instead of treating unavailable capability as a pass.
- Plugin source policy, its pinned `review-checks.md` reference and regression tests must change
  together. Publication of the resulting payload is a later distinct release effect.

## Alternatives rejected

- **A permanent adversarial runner/queue/receipt service.** Rejected: same-lifetime review needs
  none and the user explicitly rejects fabricated asynchronous infrastructure.
- **A universal mandatory helper.** Rejected: its cost exceeds value for bounded deterministic
  tickets and conflicts with profile-scaled ceremony.
- **Auditor-authorized real production probes.** Rejected: reviewer delegation cannot widen data,
  account, credential, release or deployment authority.
