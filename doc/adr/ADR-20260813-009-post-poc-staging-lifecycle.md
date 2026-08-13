# ADR-20260813-009 — Post-POC Staging Development Lifecycle

## Status

`ACCEPTED_REQUIREMENT / SPECIFICATION_IN_PROGRESS`

## Context

The existing installer convergence rule preserves this repository's first
packaged version, but it does not yet define the general lifecycle that Johnny
applies to a user's target project. A user without software-delivery experience
must not accidentally continue development on the only accepted POC commit or
confuse a test sandbox, an integration branch and a released product.

## Decision

1. The first POC becomes a development boundary only after independent review,
   owner acceptance and exact commit readback. Its version/source identity is
   immutable evidence.
2. Johnny prepares a typed `StagingTransitionPlan` that binds the repository,
   accepted POC commit, expected local staging state, frozen-version reference
   and plan digest. One explicit confirmation authorizes only the planned local
   ref effect.
3. Remote staging publication is separately authorized. It may create or
   verified-fast-forward the exact ref only after remote-history admission and
   must read back the expected SHA. It never force-pushes, resets, deletes or
   silently resolves divergence.
4. After staging admission, every later feature or architecture ticket records
   the exact staging SHA as its expected base. Reviewer-created implementation
   branches/worktrees must descend from that SHA and may return only through
   independent review and guarded staging integration.
5. Staging is an integration baseline, not a release. Stable promotion,
   packaging and deployment retain separate gates and immutable identities.
6. Disposable environments remain the only place for bounded install,
   uninstall, host and other effect verification. They do not grant Git ref or
   promotion authority.

## Consequences

- Novice users receive a recoverable default: the accepted POC remains intact
  while continued development occurs on an explicit integration lineage.
- A repository with no remote may use a verified local staging ref, but Johnny
  cannot claim remote backup or perform a push without separate authority.
- Wrong ancestry, stale/dirty baselines, divergence and mismatched readback
  halt before source, Git, Agent or host effects.
- This ADR changes future adaptive-orchestration behavior only. It performs no
  branch creation, push, target-project mutation, package, release or deploy.

## Rejected alternatives

- Continue directly on the accepted POC/stable branch: rejected because it
  destroys the rollback and comparison baseline.
- Treat a disposable test directory as staging: rejected because test isolation
  and version-control authority solve different problems.
- Automatically push staging during installation or project bootstrap:
  rejected because remote mutation requires separate explicit authority and
  history admission.
