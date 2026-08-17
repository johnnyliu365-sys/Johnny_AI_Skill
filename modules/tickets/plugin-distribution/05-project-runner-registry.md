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

## Correction admission 02 — canonical receipt project identity

| Field | Binding |
| --- | --- |
| State | `CHANGES_REQUESTED / UPSTREAM_CONTRACT_DEFECT / SAME_TICKET_ADDITIVE_CORRECTION` |
| Reviewed baseline | `eff1bc023c45f0a6de5459ce1b16d22a3c3a1018` (Ticket 05 integrated closure) |
| Trigger | Ticket 06 admission found that the runner registry's `OpaqueMetadataId` project key cannot equal or validate the receipt boundary's canonical `ProjectId` (`prj_[0-9a-f]{16}`). |
| Allocation | Retain ticket `ticket-pd05-runner-registry-01`, receipt `receipt-pd05-20260817-001`, owner `01a00eac-b464-7ee1-ac76-465477768e02`, worktree `worktree-pluginimpl2-01`, and branch `codex/plugin-distribution-05-project-runner-registry`; user-authorized manual bootstrap forwarding only, with no live Router/host claim or new effect authority. |

This correction supersedes only the original closure's use of `OpaqueMetadataId` for the
*project* key.  Import and use the existing `ProjectId` value type for every project value at
the `ProjectRunnerRegistry` boundary: `RunnerLifecyclePort.start`,
`RunnerLifecyclePort.stop`, `ProjectRunnerRegistryResult.project_ref`, internal request/state
models, lookup/replacement/removal helpers, and all four public registry methods.  The method
and result field name remains `project_ref`; its type is now exactly `ProjectId`.  Do not create
a conversion, derived key, alias, or parallel mapping.  `subscription_id` and `runner_ref`
remain `OpaqueMetadataId` exactly as before.

Within the original two writable paths only, replace project fixtures with distinct valid
`ProjectId` values and add one named TDD cell proving that a valid receipt-compatible project ID
flows through start/result state while `project-alpha` is rejected by the ordinary public
validator before any fake lifecycle call.  Existing lifecycle, duplicate/foreign subscription,
stop, isolation and no-recovery behavior must remain unchanged.  The first-red command is
`python -B -m pytest -q -p no:cacheprovider tests/test_plugin_distribution_runner_registry.py -k test_project_id_is_required_and_receipt_compatible`.

Run the focused closure, `python -m mypy --strict
library/local_orchestration/project_runner_registry.py`, the cache-free full suite and the
existing in-memory compile gate.  Reverse-mutate the `ProjectId` boundary (or its ordinary
validator path) so the new named cell fails, byte-restore it, then remove all cache/bytecode
residue.  Return one additive implementation commit with the named cell, strict/full results,
reverse result and residue evidence.  Any need to change receipt contracts, Git adapters,
composition roots, host behavior or Ticket 06 is `CHANGE_DETECTED`.

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `INTEGRATED / CLOSED` |
| Implementation / correction / integration | `51efa7cd508dfa645b2654d80759060e17536088` / `a184c2009ccbec8f281185b9d43541735b2a5bcf` / `eff1bc023c45f0a6de5459ce1b16d22a3c3a1018` |
| Independent closure | focused `10 passed`; strict `mypy --no-incremental` passed; full `744 passed, 2,537 subtests`; 208 Python files compiled in memory. |
| Correction closure | foreign Alpha subscription removed through Beta returns `FOREIGN_SUBSCRIPTION`, makes no additional lifecycle call, and Alpha retains its runner/subscription. |
| Reverse / residue | Owner's R3 foreign-owner guard turned red and was byte-restored; reviewer rerun found `POST_CORRECTION_CLEAN=PASS` with no cache/bytecode residue. |
| Review | `APPROVED`; only injected in-memory lifecycle fakes were exercised. No process, filesystem, Git, host, network, receipt-store or target-project effect was introduced. |

Canonical Git-blob SHA-256: `project_runner_registry.py` `B83F50266D996F7CA71A87B8F32286A0B158EE8CF595FB1EE684CBAA8899D66C`; `test_plugin_distribution_runner_registry.py` `1BBFD26DFDD15A7392484A4369D1A6FB01592284B3181F03DFD37092961C26F3`.
