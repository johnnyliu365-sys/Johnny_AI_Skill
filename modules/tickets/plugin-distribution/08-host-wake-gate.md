# 08 — Host-wake capability gate

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-11 / `ctx-plugin-distribution-r02` |
| Dependency / source baseline | Ticket 07 closure `6a5b0f742dad231e7e90363a4f2d639bf83d81cb` / current `main` |
| Control / reviewer | Current architecture owner and reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior has no authority |
| Implementation owner | Project-owner ticket-scoped direct-owner override: current architecture owner in `worktree-control-root-01`, branch `codex/plugin-distribution-08-host-wake-gate`; no implementer task, receipt, host dispatch, or live Router claim |
| Implementation language / strict checker | Python 3.11.9 / `python -B -m mypy --strict library/workflow_router/role_wake_contracts.py library/local_orchestration/role_wake_composition.py` |
| State / XSS | `TICKET_REFROZEN / HIGH_ASSURANCE_REQUIRED / DIRECT_OWNER_OVERRIDE / IMPLEMENTATION_READY`; `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

The existing receipt-bound `RoleWakeChain` already proves exact reviewer task/thread/host,
subscription and receipt bindings before the injected one-shot wake port is called. Its remaining
AC-11 defect is error collapse: an unavailable host capability currently shares the generic
`ROLE_WAKE_CHAIN_UNAVAILABLE` result with a foreign, stale or replayed binding. Add the finite
`HOST_WAKE_CAPABILITY_UNAVAILABLE` member and return it only when the otherwise typed preflight
input declares `RoleWakeCapabilityState.UNAVAILABLE`. Invalid input and every mismatched
receipt/task/host/subscription/baseline/correlation binding remain
`ROLE_WAKE_CHAIN_UNAVAILABLE` and create no proof or host effect.

Writable scope: `library/workflow_router/role_wake_contracts.py` and
`tests/test_role_wake_composition.py` only. `library/local_orchestration/role_wake_composition.py`
is read-only verification scope. Only existing in-memory fakes execute; no live host call,
heartbeat, polling, Router binding, manual-forward success claim, filesystem residue or target
project effect is allowed.

## TDD, verification and return

Closure `CLOSURE-PD-08-R04-01`:

- H1: the existing complete fake chain remains `PROVEN` and digest-bound.
- H2: only `RoleWakeCapabilityState.UNAVAILABLE` returns
  `HOST_WAKE_CAPABILITY_UNAVAILABLE`, with no proof and no host-port call.
- H3: foreign/stale/replayed or otherwise mismatched bindings still return
  `ROLE_WAKE_CHAIN_UNAVAILABLE`, with no proof and no host-port call.
- H4: the existing coordinator persists its claim before one fake host effect.
- H5: the existing uncertain-effect settlement remains non-retryable.

First red is exactly:

```text
python -B -m pytest -q -p no:cacheprovider tests/test_role_wake_composition.py -k test_unavailable_host_capability_has_exact_host_wake_failure
```

Run the focused closure, the named strict checker, in-memory compilation of the two writable
paths, and the full `tests/test_role_wake_composition.py` module. Reverse-mutate the unavailable
capability classification so the H2 cell turns red, restore exact bytes, rerun the focused cell,
and leave no cache or bytecode residue. The direct owner returns the normal completed evidence;
live host capability and Router binding remain later owner-controlled gates.
