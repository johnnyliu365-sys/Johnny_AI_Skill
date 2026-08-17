# 06 — Receipt-bound Git subscription

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-07, AC-09, AC-10 / `ctx-plugin-distribution-r02` |
| Dependency / source baseline | Ticket 05 canonical `ProjectId` correction integrated at `31b3c79bc117c71c2059b6b4bb029387272e5f7e` / ticket closure `23d309ad47e5a1f1b9437bfccec254b30d993ded` |
| Control / reviewer | Current architecture owner and reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior has no authority |
| Implementation allocation | ticket `ticket-pd06-receipt-git-subscription-01`; role `role-impl-pd06-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pluginimpl2-01`; branch `codex/plugin-distribution-06-receipt-git-subscription` / `branch-pd06git-01`; receipt `receipt-pd06-20260817-001`; correlation `corr-pd06-20260817-001` |
| Dispatch mode | User-authorized one-time manual bootstrap forwarding while live Router dispatch is unavailable; no live Router descriptor, host subscription, heartbeat, polling, automation or target effect. |
| Implementation language / strict checker | Python 3.11.9 / `python -m mypy --strict library/local_orchestration/project_subscription_runtime.py` |
| Profile / state / XSS | `plugin-distribution-poc-r02` v2 / POC / Luna xhigh / one implementation lane / no helper / `TICKET_REFROZEN / READY_LOW_MODEL / DISPATCH_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

`ProjectSubscriptionRuntime` registers one existing exact receipt against one runner and native
Git-ref notification. A hint performs bounded ref/ancestry/changed-path/committed-handoff readback;
ordinary source commits stay silent. Foreign, stale, replayed or malformed binding rejects without
closing peer subscriptions. Existing receipt, Git adapter and supervision types are read-only.

Writable scope: `library/local_orchestration/project_subscription_runtime.py` and
`tests/test_plugin_distribution_git_subscription.py`. No host wake, polling or target write.

## TDD, verification and return

Closure `CLOSURE-PD-06-R03-01`: S1 exact registration; S2 source silence; S3 committed candidate;
S4 foreign/stale/replay rejection; S5 peer isolation/close. First red:
`python -m pytest -q tests/test_plugin_distribution_git_subscription.py -k test_foreign_receipt_handoff_never_emits_completion_candidate`.
Verify with `python -m pytest -q tests/test_plugin_distribution_git_subscription.py`,
`python -m mypy --strict library/local_orchestration/project_subscription_runtime.py` and
`python -m pytest -q`; reverse-mutate receipt matching. Delete fixture subscriptions only; return
typed commit/cell/digest/cleanup evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.

## Refreeze R04-01 — effective closure

This committed revision supersedes the stale `Sole closure and boundary` and `TDD, verification
and return` text above. It creates no new SPEC: it only makes the already-approved receipt,
runner and Git-adapter composition exact after Ticket 05 adopted the canonical `ProjectId`.

Writable scope remains exactly:

```text
library/local_orchestration/project_subscription_runtime.py
tests/test_plugin_distribution_git_subscription.py
```

The new runtime may import, but must not modify, these read-only existing contracts:
`TicketReceipt`, `ProjectRunnerRegistry`, `ProjectRunnerRegistryResult`,
`ReceiptBoundGitEventAdapter`, `GitRefRegistrationRequest`, `GitEventAdapterDecision`,
`GitEventRegistrationState`, `GitRefSignal`, `HandoffAdmissionContext` and `OpaqueMetadataId`.
Receipt `project_id: ProjectId` is passed directly to `ProjectRunnerRegistry`; subscription and
runner identities remain the existing opaque IDs.
No conversion, derived key, alias, package-root export or composition root belongs here.

All new DTOs are frozen strict Pydantic models with `extra="forbid"` and
`revalidate_instances="always"`; no `Any`, dynamic map, raw exception text, Git blob contents,
host handle or target path may enter their public result.

```text
ProjectSubscriptionRegistrationRequest = {
  receipt: TicketReceipt,
  git_request: GitRefRegistrationRequest,
  handoff_context: HandoffAdmissionContext
}
ProjectSubscriptionState = {
  receipt: TicketReceipt,
  registration: GitEventRegistrationState,
  handoff_context: HandoffAdmissionContext,
  runner_ref: OpaqueMetadataId
}
ProjectSubscriptionDecision = REGISTERED | SILENT | COMPLETION_CANDIDATE |
                              REJECTED | CLOSE_BLOCKED | CLOSED
ProjectSubscriptionFailure = INVALID_BINDING | INACTIVE_RECEIPT |
                             GIT_REGISTRATION_REJECTED |
                             RUNNER_REGISTRATION_REJECTED |
                             RUNNER_CLOSE_REJECTED
ProjectSubscriptionResult = {
  decision: ProjectSubscriptionDecision,
  state: ProjectSubscriptionState | null,
  runner_result: ProjectRunnerRegistryResult | null,
  git_decision: GitEventAdapterDecision | null,
  failure: ProjectSubscriptionFailure | null
}
ProjectSubscriptionRuntime = {
  register(ProjectSubscriptionRegistrationRequest) -> ProjectSubscriptionResult,
  observe(ProjectSubscriptionState, GitRefSignal) -> ProjectSubscriptionResult,
  close(ProjectSubscriptionState) -> ProjectSubscriptionResult
}
```

`REGISTERED`, `SILENT` and `COMPLETION_CANDIDATE` require one active state and no failure.
`CLOSE_BLOCKED` requires the unchanged state plus `RUNNER_CLOSE_REJECTED`. `REJECTED` requires
one finite failure and no state; `CLOSED` has neither state nor failure.

Before either injected dependency is called, `register` requires exact strong input types, an
`ACTIVE` receipt, and equality of every shared binding: project, ticket, receipt, worktree,
branch, baseline and correlation across receipt/request/context; receipt ticket revision equals
context ticket revision; request implementation task equals context target task; receipt
implementation owner equals context target role. Any mismatch is `REJECTED` before runner or
native-Git effect.

For an exact binding, arm `ReceiptBoundGitEventAdapter` first. It must produce an active
registration before `ProjectRunnerRegistry.register_subscription(receipt.project_id,
git_request.subscription_id)` is called. Only `SUBSCRIBED` or `REUSED` produces a state; every
other registry decision closes that exact Git registration and returns
`RUNNER_REGISTRATION_REJECTED`. A Git registration failure returns
`GIT_REGISTRATION_REJECTED` and never touches the runner registry. This ordering prevents a
failed Git registration from orphaning a newly started runner.

`observe` delegates once to the existing adapter with the state-bound context. Adapter
`REGISTERED` maps to `REGISTERED`; `SOURCE_ADVANCED` and `SILENT` map to `SILENT`; only
`TERMINAL_HANDOFF_ACCEPTED` maps to `COMPLETION_CANDIDATE`. A foreign signal, replay or ordinary
source commit never becomes a candidate. Adapter stale/invalid/readback terminal state releases
only its own runner subscription: success returns `REJECTED`; unavailable runner stop returns
`CLOSE_BLOCKED` with that state for a later explicit `close`. Peer IDs must never be removed or
closed.

`close` removes only `state.registration.subscription_id` from the matching receipt project
before closing that exact Git registration. A non-`REMOVED` runner result is `CLOSE_BLOCKED` and
leaves the Git registration active; `REMOVED` then closes that Git registration and returns
`CLOSED`. Repeated closure, foreign input, stale binding and malformed contracts remain finite
and never mutate a peer. No method may call a Router, Codex task/thread, supervision controller,
timer, callback loop, filesystem, process, network or provider.

## Refreeze R04-01 — TDD and return

Closure `CLOSURE-PD-06-R04-01`:

- S1: an exact active receipt binds the same `ProjectId` to one runner and one exact Git
  registration; public DTOs round-trip and malformed/legacy project IDs reject before either fake
  effect.
- S2: a native hint for an ordinary source commit returns `SILENT` with state retained; it creates
  no candidate or peer mutation.
- S3: only a committed valid terminal handoff maps to `COMPLETION_CANDIDATE`; the runtime makes no
  Router or host-wake call.
- S4: foreign receipt/request/context values reject before effects; foreign signal, stale binding,
  replay and malformed handoff never produce a candidate and affect no peer.
- S5: two subscriptions prove isolation; close removes/cancels only its own subscription, while
  unavailable stop returns `CLOSE_BLOCKED` and leaves its exact Git registration active.

First red is exactly:

```text
python -B -m pytest -q -p no:cacheprovider tests/test_plugin_distribution_git_subscription.py -k test_exact_receipt_project_binding_is_required_before_effects
```

Run the focused closure, the strict checker named in the binding table,
`python -B -m pytest -q -p no:cacheprovider`, and in-memory compilation of every Python source.
Reverse-mutate the pre-effect receipt-binding equality guard so the named S1 cell turns red,
restore exact bytes, rerun the focused cell, and remove every test/cache/bytecode residue before
one implementation commit. Add an AST/source gate proving this new runtime imports none of
`threading`, `time`, `watchdog`, `subprocess`, `pathlib`, `socket`, `requests`, `httpx` or any
Codex/thread-control module.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, `BLOCKED -> HALT` with its
failed cell and preserved branch state, or `CHANGE_DETECTED -> REQUIREMENT_CHANGED` only for a
conflict in the frozen dependencies. Do not alter this ticket, Ticket 05, any Router source, Git
adapter, receipt contract, supervision type, composition root or external project.
