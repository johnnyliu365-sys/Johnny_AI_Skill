# 10 — Johnny Router composition root

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-04, AC-07–AC-12 / `ctx-plugin-distribution-r02` |
| Dependencies / implementation baseline | 04 `4fd29cd`, 05 `23d309`, 06 `510408e`, 07 `6a5b0f7`, 08 `574e6e8`, 09 `3900a1b` / current `main` `3900a1baa54daee64c54f62fb8a4d1a17f1da479` |
| Control / reviewer | Current architecture owner and reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior has no authority |
| Implementation allocation | ticket `ticket-pd10-router-composition-01`; role `role-impl-pd10-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pluginimpl2-01`; branch `codex/plugin-distribution-10-router-composition` / `branch-pd10composition-01`; receipt `receipt-pd10-20260818-001`; correlation `corr-pd10-20260818-001` |
| Dispatch mode | User-authorized one-time manual bootstrap forwarding while live Router dispatch remains unavailable; no live descriptor, host subscription, heartbeat, polling, automation, installation, publication or target-project effect |
| Implementation language / strict checker | Python 3.11.9 / `python -B -m mypy --strict library/local_orchestration/johnny_router_composition.py` |
| Profile / state / XSS | `plugin-distribution-poc-r02` v2 / POC / Luna xhigh / one implementation lane / no helper / `TICKET_REFROZEN / READY_LOW_MODEL / DISPATCH_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and public boundary

Create `library/local_orchestration/johnny_router_composition.py` and
`tests/test_plugin_distribution_router_composition.py` only. This is a library composition
root, not a CLI transport or a live Router. It must not alter
`johnny_router_contracts.py`, `johnny_router_cli.py`, any existing dependency, or Tickets 11/12.

The module exports these frozen, explicit domain values with no `Any`, dynamic map, filesystem
path, source text, receipt contents, host handle or exception text in result state:

```text
JohnnyRouterCompositionPorts = {
  runner_lifecycle: RunnerLifecyclePort | null,
  git_adapter: ReceiptBoundGitEventAdapter | null,
  review_store: SeniorReviewInboxStorePort | null,
  review_resolver: ReviewClusterBindingResolverPort | null,
  wake_attempt_boundary: RoleWakeAttemptBoundaryPort | null,
  host_wake_port: RoleWakePort | null
}
JohnnyRouterCompositionFailure = PROFILE_MISMATCH | RUNTIME_LOCK_MISMATCH |
                                  RUNNER_PORT_UNAVAILABLE | GIT_ADAPTER_UNAVAILABLE |
                                  REVIEW_STORE_UNAVAILABLE | REVIEW_RESOLVER_UNAVAILABLE |
                                  WAKE_ATTEMPT_BOUNDARY_UNAVAILABLE |
                                  HOST_WAKE_PORT_UNAVAILABLE
JohnnyRouterCompositionStatus = COMPOSED | BLOCKED
JohnnyRouterCompositionResult = {
  status: JohnnyRouterCompositionStatus,
  composition: JohnnyRouterComposition | null,
  failure: JohnnyRouterCompositionFailure | null
}
JohnnyRouterComposition = {
  profile: ProjectWorkflowProfile,
  runtime_lock: RuntimeDependencyLock,
  runner_registry: ProjectRunnerRegistry,
  subscription_runtime: ProjectSubscriptionRuntime,
  review_inbox: SeniorReviewInboxCoordinator,
  role_wake: RoleWakeCoordinator,
  bundle_builder: PluginBundleBuilder
}
build_johnny_router(
  profile: ProjectWorkflowProfile,
  runtime_lock: RuntimeDependencyLock,
  ports: JohnnyRouterCompositionPorts
) -> JohnnyRouterCompositionResult
```

`build_johnny_router()` accepts only the exact value of
`build_plugin_distribution_profile()` and the exact value of `build_approved_runtime_lock()`.
Each unavailable or malformed dependency is rejected as its corresponding finite failure before
constructing a component. `COMPOSED` contains every named component and no failure; `BLOCKED`
contains exactly one failure and no composition. Ordinary construction must create, call, start,
stop, register, observe, close, queue, settle, wake, install, publish or otherwise invoke none of
the injected ports.

On success, construct exactly this dependency graph without an operation dispatcher:

```text
runner_lifecycle -> ProjectRunnerRegistry
ProjectRunnerRegistry + git_adapter -> ProjectSubscriptionRuntime
wake_attempt_boundary + host_wake_port -> DurableRoleWakeAttemptStore + RoleWakeCoordinator
review_store + review_resolver + RoleWakeCoordinator -> SeniorReviewInboxCoordinator
```

The returned root exposes that runtime, inbox, wake coordinator, Profile, lock and a fresh
`PluginBundleBuilder` only for a later caller with already-validated typed input. It does not
parse argv, print, select a `JohnnyRouterOperation`, invoke a component method, generate a bundle,
make a Git readback, persist state, or call a host. Ticket 11 owns installation and Ticket 12 owns
uninstallation; neither behavior may be introduced here.

Writable scope is exactly the two new paths above. Existing public contracts are read-only:
`ProjectWorkflowProfile`, `build_plugin_distribution_profile`, `RuntimeDependencyLock`,
`build_approved_runtime_lock`, `RunnerLifecyclePort`, `ProjectRunnerRegistry`,
`ReceiptBoundGitEventAdapter`, `ProjectSubscriptionRuntime`, `SeniorReviewInboxCoordinator`,
`SeniorReviewInboxStorePort`, `ReviewClusterBindingResolverPort`, `RoleWakeAttemptBoundaryPort`,
`RoleWakePort`, `DurableRoleWakeAttemptStore`, `RoleWakeCoordinator` and `PluginBundleBuilder`.

## TDD, verification and return

Closure `CLOSURE-PD-10-R04-01`:

- J1: exact Profile, approved lock and passive fakes produce `COMPOSED`; every public component
  has the declared concrete type and the Profile/lock are preserved by value.
- J2: import and ordinary construction invoke no injected port method. The fake counters for
  runner lifecycle, Git adapter, review store/resolver, wake-attempt boundary and host wake stay
  zero; no filesystem, process, Git, queue, host or target-project effect occurs.
- J3: mismatched Profile/lock plus each missing or malformed injected dependency return only its
  corresponding `BLOCKED` member, carry no composition, and invoke no peer port.
- J4: public values construct through their ordinary constructors; `COMPOSED` and `BLOCKED`
  nullability is exact, foreign/dynamic inputs reject before reaching a component, and no result
  exposes a raw injected port.
- J5: an unavailable `host_wake_port` blocks as `HOST_WAKE_PORT_UNAVAILABLE`; it does not bind a
  subscription, inbox, wake attempt or host action.

First red is exactly:

```text
python -B -m pytest -q -p no:cacheprovider tests/test_plugin_distribution_router_composition.py -k test_builds_bound_components_without_port_effects
```

Run the focused closure; direct dependency regressions
`tests/test_plugin_distribution_profile.py`,
`tests/test_plugin_distribution_runner_registry.py`,
`tests/test_plugin_distribution_git_subscription.py`, `tests/test_senior_review_inbox.py` and
`tests/test_role_wake_composition.py`; the named strict checker; and in-memory compilation of the
two new paths. Reverse-mutate the `host_wake_port` availability gate so the named J5 cell turns
red, restore exact bytes, rerun the focused cell and remove every cache/bytecode residue before
one implementation commit. Return exactly `ImplementationReturn.COMPLETED → ACTION_COMPLETED`,
`BLOCKED → HALT` with its failed closure cell and preserved branch state, or
`CHANGE_DETECTED → REQUIREMENT_CHANGED` only for a conflict in the frozen read-only contracts.
