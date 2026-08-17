# 10 — Johnny Router composition root

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-04, AC-07–AC-12 / `ctx-plugin-distribution-r02` |
| Dependencies / planning baseline | 04, 05, 06, 07, 08, 09 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh after 08 approval, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

`build_johnny_router()` injects the exact lock, Profile, runner, subscription, queue and host-wake
ports into one short-lived CLI composition. Each operation selects at most one bounded action and
returns the closed result union. Runner ownership is delegated to the registry; unavailable host
wake remains fail-closed. Import and construction perform no process/filesystem/Git/host effect.

Writable scope: `library/local_orchestration/johnny_router_composition.py` and
`tests/test_plugin_distribution_router_composition.py`.

## TDD, verification and return

Closure `CLOSURE-PD-10-R03-01`: J1 ordinary construction; J2 one action per operation; J3 missing
port finite failure; J4 no import/build effect; J5 unavailable host non-binding. First red:
`python -m pytest -q tests/test_plugin_distribution_router_composition.py -k test_route_event_invokes_exactly_one_injected_action`.
Verify with `python -m pytest -q tests/test_plugin_distribution_router_composition.py`,
`python -m mypy --strict library/local_orchestration/johnny_router_composition.py` and
`python -m pytest -q`; reverse-mutate operation selection. Return typed evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
