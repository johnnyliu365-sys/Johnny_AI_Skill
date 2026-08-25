# Ticket 06 — deferred per-project live qualification

| Field | Value |
| --- | --- |
| Ticket ID | PAI-06-DEFERRED-PER-PROJECT-LIVE-QUALIFICATION |
| State | QUALIFIED_FOR_DEVELOPMENT_REPOSITORY / ORDINARY_ACTOR_ENFORCEMENT_PROVEN / ADMIN_ACTOR_UNPROVEN — evidence in [06-live-provider-qualification-evidence.md](../../../doc/reviews/project-authority-integration/06-live-provider-qualification-evidence.md); per-project qualification for any other project remains future verification |
| Dependencies | PAI-01 through PAI-05 accepted; exact per-project owner effect authority is required only when this verification is activated. |
| Source specification | Project authority integration SPEC Revision 11, ticket order item 06 |
| Planning baseline | main at 4df52d0df1fbe479cc9737d390df34d36e402b66 |
| Required future effects | Qualified live remote/provider readback only after exact owner, action, target, environment, receipt, baseline, correlation, and readback authority are committed. |

## Vertical closure reserved

When a named project elects `HIGH_COLLABORATION`, qualify its actual remote/provider capability
and record `PROVEN`, `UNPROVEN`, or `UNSUPPORTED` honestly. The later exact ticket must bind that
project's authority contract, repository identity, full authority ref, provider method, owner,
environment, baseline, correlation, readback, finite failure handling, and no-secret evidence
record. It must prove UI-bypass prevention and stale-approval invalidation by actual readback; it
may not infer a GitHub mechanism or promote a fake result to live capability.

This is a future verification contract, not a current blocker of PAI-08 and not an effect grant.
Until activated, it creates no credential, provider command, remote read, push, policy change, UI
action, receipt, runner, task, branch, worktree, or dispatch. PAI-08 may record only its deferred
state; it may not treat the record as `PROVEN`.
