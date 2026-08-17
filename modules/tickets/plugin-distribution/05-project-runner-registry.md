# 05 — Project runner registry

| Field | Binding |
| --- | --- |
| SPEC / AC / requirement | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` Revision 02 / AC-07, AC-08 / `PRD-20260802-004` / `CHG-20260802-004` / `REQ-20260802-004` |
| Context / implementation baseline / dependency | `ctx-plugin-distribution-r02` / `1a3a289e4a318eeaebe5c25622f6c992b6464984` / Ticket 04 integrated at `4fd29cdcb92a6afe304ebc5cd2d4a6a5f337136d` |
| Closure | `CLOSURE-PD-05-R03-02`; replaces the unbound R03-01 ticket with the exact isolated runner lifecycle and registry contracts already closed by SPEC Revision 02 |
| Control / reviewer | Current architecture owner and reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior task is retired and has no authority over this ticket |
| Implementation allocation | ticket ref `ticket-pd05-runner-registry-01`; role `role-impl-pd05-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pluginimpl2-01`; branch `codex/plugin-distribution-05-project-runner-registry` / `branch-pd05runner-01`; receipt `receipt-pd05-20260817-001`; correlation `corr-pd05-20260817-001` |
| Dispatch mode | Owner-authorized manual bootstrap forwarding by the current reviewer; this ticket must not claim a live Router dispatch, host subscription, heartbeat, polling, automation or target effect |
| Implementation language / strict checker | Python 3.11.9 / `python -m mypy --strict library/local_orchestration/project_runner_registry.py` |
| Profile / state / XSS | `plugin-distribution-poc-r02` v2 / POC / Luna xhigh / one implementation lane / no helper / `TICKET_REFROZEN / READY_LOW_MODEL / DISPATCH_REQUIRED` / `XSS_NOT_APPLICABLE` |
| Boundary classification | In-memory strict requests, values and injected fake lifecycle port only; no import-time or runtime process, filesystem, Git, host, network, runner, receipt-store, target-project or provider effect |

## Sole closure and public contracts

Create `library/local_orchestration/project_runner_registry.py` with frozen, strict Pydantic
models (`extra="forbid"`, no `Any`, no dynamic map) and existing opaque metadata IDs. The public
boundary is closed as follows:

```text
RunnerLifecyclePort = {
  start(project_ref: OpaqueMetadataId) -> RunnerStartResult,
  stop(project_ref: OpaqueMetadataId, runner_ref: OpaqueMetadataId) -> RunnerStopResult
}
RunnerStartResult = STARTED(runner_ref) | CAPABILITY_UNAVAILABLE(null)
RunnerStopResult = STOPPED | CAPABILITY_UNAVAILABLE
ProjectRunnerRegistryResult = {
  decision: SUBSCRIBED | REUSED | REMOVED | DETACHED | UNINSTALLED |
            DUPLICATE_SUBSCRIPTION | FOREIGN_SUBSCRIPTION | NOT_FOUND |
            RUNNER_START_UNAVAILABLE | RUNNER_STOP_UNAVAILABLE,
  project_ref: OpaqueMetadataId,
  subscription_id: OpaqueMetadataId | null,
  runner_ref: OpaqueMetadataId | null
}
```

`ProjectRunnerRegistry` accepts the injected `RunnerLifecyclePort` and exposes exactly
`register_subscription(project_ref, subscription_id)`, `remove_subscription(project_ref,
subscription_id)`, `detach_project(project_ref)` and `uninstall_project(project_ref)`, each
returning `ProjectRunnerRegistryResult`. The ordinary constructors/validators and every public
method must reject blank/foreign/bypassed data through named finite results or validation; no
exception text or raw external value enters result state.

| Condition | Required result and lifecycle effect |
| --- | --- |
| first distinct subscription for a project, `start -> STARTED(runner_ref)` | `SUBSCRIBED`; exactly one `start`; retain that runner and subscription |
| later distinct subscription for the same project | `REUSED`; retain the same runner; zero additional lifecycle call |
| duplicate subscription on its project | `DUPLICATE_SUBSCRIPTION`; zero lifecycle call |
| a subscription ID already owned by another project | `FOREIGN_SUBSCRIPTION`; zero lifecycle call and no peer mutation |
| first subscription, `start -> CAPABILITY_UNAVAILABLE` | `RUNNER_START_UNAVAILABLE`; retain neither runner nor subscription |
| exact removal that leaves another subscription | `REMOVED`; zero `stop` |
| exact last removal, detach, or uninstall of an active project, `stop -> STOPPED` | respectively `REMOVED`, `DETACHED`, or `UNINSTALLED`; exactly one `stop(project_ref, runner_ref)` and clear only that project |
| required stop is unavailable | `RUNNER_STOP_UNAVAILABLE`; retain the exact project state and preserve all peers |
| missing project/subscription | `NOT_FOUND`; zero lifecycle call |

Fresh `ProjectRunnerRegistry` construction has no persisted state, performs zero lifecycle call,
and has no recovery/auto-start API. It must not import or access Git, a host, process launcher,
receipt store, filesystem, target project or provider. No package-root export, composition root,
subscription runtime, host wake, persistence or external effect belongs to this ticket.

Writable scope: `library/local_orchestration/project_runner_registry.py` and
`tests/test_plugin_distribution_runner_registry.py` only.

## TDD, verification and return

Closure `CLOSURE-PD-05-R03-02`:

- R1: the first subscription starts exactly once and returns the runner-bound `SUBSCRIBED` result.
- R2: a second distinct subscription to that project returns `REUSED` with no second start.
- R3: duplicate and foreign subscription IDs return their distinct finite result before a lifecycle call; affected and peer state remain isolated.
- R4: nonfinal removal has no stop; final removal, detach and uninstall stop exactly their own runner once; failed stop retains that project and does not alter peers.
- R5: a fresh registry invokes neither port method and cannot auto-start/recover a runner.
- R6: all public strict values construct and JSON-round-trip through their ordinary validators; malformed lifecycle result, nullability mismatch and foreign/bypassed IDs reject.

First red: `python -m pytest -q tests/test_plugin_distribution_runner_registry.py -k test_second_runner_for_same_project_is_rejected_before_start`.
Verify with `python -B -m pytest -q -p no:cacheprovider tests/test_plugin_distribution_runner_registry.py`,
the strict checker above, `python -B -m pytest -q -p no:cacheprovider`, and in-memory compile
every Python source. Reverse-mutate the project/foreign-subscription uniqueness guard so R3 turns
red; restore exact bytes and rerun the focused closure. Remove every test/cache/bytecode residue
before commit.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, `BLOCKED -> HALT` with its
failed cell and preserved branch state, or `CHANGE_DETECTED -> REQUIREMENT_CHANGED` with the
conflicting frozen reference. A need for persistence, restart recovery, Git, a receipt, a host
callback, process launcher, composition root or another operation is `CHANGE_DETECTED`; it does
not expand this ticket.

## Correction admission 01

| Field | Binding |
| --- | --- |
| State | `CHANGES_REQUESTED / IMPLEMENTATION_DEFECT / SAME_TICKET_ADDITIVE_CORRECTION` |
| Reviewed candidate | `51efa7cd508dfa645b2654d80759060e17536088` |
| Receipt / allocation | Retain `receipt-pd05-20260817-001`, the exact owner, worktree and branch already bound above; no new branch, receipt, task, source scope or effect authority |

Independent reproduction registered `subscription-one` for `project-alpha`, then called
`remove_subscription("project-beta", "subscription-one")`; it returned `NOT_FOUND`. This violates
the R3 row requiring a subscription ID owned by another project to return
`FOREIGN_SUBSCRIPTION` before a lifecycle call and without peer mutation.

Within the original two writable paths only, make `remove_subscription` distinguish a foreign
owner from an unknown subscription before its `NOT_FOUND` branch. Add the bounded removal case to
the existing R3 test: it must return `FOREIGN_SUBSCRIPTION`, make zero additional `start`/`stop`
call, and prove Alpha retains its subscription/runner. Reverse-mutate this foreign-owner guard so
that exact R3 cell turns red, restore exact bytes, rerun focused, strict, full and residue gates,
and create one additive implementation commit.
