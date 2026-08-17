# 08 — Host-wake capability gate

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-11 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 07 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; stronger implementation owner and receipt required |
| State / XSS | `PLANNED / HIGH_ASSURANCE_REQUIRED / NOT_DISPATCHED`; `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

Injected `HostWakePort` proves exact Senior task/thread/host and receipt-bound registration before
one claim/effect/readback. Missing capability returns `HOST_WAKE_CAPABILITY_UNAVAILABLE`; uncertain
effect settles once without retry. Only fakes execute during implementation. No live host call,
heartbeat, polling, Router binding or manual-forward success claim is allowed.

Writable scope: `library/local_orchestration/role_wake_composition.py`,
`library/local_orchestration/host_contracts.py`, `library/local_orchestration/host_fakes.py`,
`tests/test_plugin_distribution_host_wake.py`.

## TDD, verification and return

Closure `CLOSURE-PD-08-R03-01`: H1 exact fake success; H2 unavailable fail-closed; H3
foreign/stale/replay block; H4 claim-before-effect; H5 uncertain settlement no retry. First red:
`python -m pytest -q tests/test_plugin_distribution_host_wake.py -k test_unavailable_host_never_marks_router_binding_eligible`.
After high-assurance allocation, verify with `python -m pytest -q tests/test_plugin_distribution_host_wake.py`,
`python -m mypy --strict library/local_orchestration/role_wake_composition.py library/local_orchestration/host_contracts.py library/local_orchestration/host_fakes.py`
and `python -m pytest -q`; reverse-mutate the claim gate. Return typed
commit/cell/digest/cleanup evidence; live capability remains a later owner-controlled gate.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
