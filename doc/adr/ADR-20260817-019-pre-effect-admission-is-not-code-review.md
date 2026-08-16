# ADR-20260817-019 — Pre-effect admission is not Code Review

- Date: `2026-08-17 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `CHG-20260817-032`
- Related specification: Receipt-bound Role Supervision Revision 08
- Narrowly supersedes: ADR-20260817-018 Decision 5's pre-effect independent-review requirement

## Context

The host-bound correction ticket is owned and executed by the Senior. Before its host effect,
there is no implementation, correction record, diff, test result or handoff to review. Requiring
formal Code Review at that point created an empty stage, left no distinct work product, and caused
the non-dispatchable control ticket to be sent to the Implementer, who correctly halted without
mutation.

The actual safety need is deterministic admission immediately before the effect: exact source
authority, target task/host, prior no-effect evidence, current task revision, clean worktree and
unchanged dispatch identity. That is an admission gate, not post-work review.

## Decision

1. The Senior is the sole Reviewer/orchestrator and the effect owner for this one bootstrap
   correction. No second Reviewer is created.
2. Replace the pre-effect `REVIEW` stage with `MANUAL_BOOTSTRAP / SENIOR_PRE_EFFECT_ADMISSION`.
3. Admission independently reads authoritative Git/task/host/worktree evidence but produces no
   Code Review conclusion. Failure halts before correction or host effect.
4. The user-origin wrong-ticket turn is reconciled as out-of-band, non-operational evidence. It
   neither authorizes implementation nor consumes the existing dispatch operation.
5. After successful admission, the owner-approved SPEC directly authorizes Senior to commit the
   additive correction/continuation record and perform the one remaining same-operation call.
6. Normal independent Code Review remains required after the Implementer produces real work and
   evidence.

## Consequences

- The bootstrap path has no empty review loop and no extra model/task wake.
- The Implementer receives only the original implementation ticket after all pre-effect gates.
- Safety is preserved through exact readback and commit-before-effect evidence rather than a
  review label with nothing to inspect.
- Existing Revision-07 and ticket commits remain immutable historical sources; additive
  decisions record the correction.

## Rejected alternatives

- A second Reviewer: rejected by the one-Senior-per-project role model and unnecessary here.
- Senior formally reviewing its own unexecuted control ticket: rejected because no completed
  Closure Set exists.
- Sending the control ticket to an Implementer: rejected because it is explicitly non-dispatched
  and carries no implementation lane.
- Another owner approval/grant/attempt: rejected because the exact same-operation continuation is
  already owner-approved and the original adapter invocation is proved not to have occurred.
