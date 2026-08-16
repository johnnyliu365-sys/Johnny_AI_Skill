# ADR-20260817-018 — Host-bound bootstrap admission and proved-no-effect recovery

- Date: `2026-08-17 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `CHG-20260817-031`
- Related specification: Receipt-bound Role Supervision Revision 07
- Narrowly supersedes: ADR-20260816-016 Decision 5 only where failure is proved to occur before
  host manager/adapter invocation

## Context

Bootstrap attempt BDA-003 bound an implementation task but not its actual host. Senior supplied
the calling environment host `slingshot:env_e_6a29e55ede90832fb63e141a9890800a` to the host tool,
which rejected the request because no `AppServerManager` was registered for that host. The target
task's authoritative host was `local`; an explicit read-only call to that host from the same
Senior context resolved successfully, and the target task had no new delivery turn.

The old bootstrap rule treated every exception after a committed claim as uncertain. That is
correct only once an adapter may have been invoked. Applying it to a rejected manager lookup
strands a provably unexecuted operation and repeatedly asks the owner for new grants without
improving safety.

## Decision

1. Every new bootstrap registry, grant and attempt binds `target_host_id` to the exact target
   task. Only authoritative target-task list/readback may produce that value.
2. Senior performs a read-only task/host/manager admission before committing a claim. Failure
   before claim consumes no grant or operation.
3. The dispatch port exposes a typed effect boundary. Host-manager lookup failure before adapter
   invocation is `PROVED_NO_EFFECT`; a timeout, transport loss or untyped exception at or after
   invocation remains `EFFECT_UNCERTAIN`.
4. A proved-no-effect result may continue only the same operation identity. It never authorizes a
   new grant, attempt, receipt, task or envelope identity.
5. Preserve BDR-003 as the contemporaneous settlement. An additive correction decision records
   the later evidence and may authorize one remaining call for the same operation after an exact
   Senior correction ticket and independent review.
6. For BDA-003 only, the continuation is bound to
   `bpb-r03-00-cs02-initial-20260817-003`, claim commit
   `ef2a5c1efd5029d8bb5698c0f9c44b0704d1f3d3`, target task
   `019ffb0c-db88-7303-895c-aecfadde7c8d` and host `local`. No BDG-004, BDA-004 or new owner grant
   is created.
7. The call sequence is one read-only host admission, one identifiers-only delivery and one
   bounded readback. No heartbeat, recurring read, timer, watcher or polling loop is introduced.

## Consequences

- Wrong-host failures halt before mutation without burning a one-shot grant or manufacturing
  uncertainty.
- Existing immutable evidence remains auditable while one exact provably unexecuted operation can
  finish without another ceremonial owner grant.
- The contract gains a host binding and effect-stage result, but idle CPU and model-token cost
  remain zero.
- Any missing stage evidence, identity mismatch, ambiguous post-invocation error or second-call
  request fails closed.

## Rejected alternatives

- Create BDG-004/BDA-004: rejected because it hides the wrong-host root cause and spends another
  owner interaction while the original operation is proved unexecuted.
- Treat the calling task's host as an implicit default: rejected because task identity does not
  imply host identity.
- Edit BDR-003 in place: rejected because contemporaneous evidence must remain immutable.
- Classify every exception as no-effect: rejected because an adapter may have accepted delivery
  before a timeout or transport failure.
- Heartbeat or repeated readback: rejected by owner policy and unnecessary for one-shot delivery.
