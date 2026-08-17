# 04 — Profile-bound CLI preflight

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-04, AC-05 / `ctx-plugin-distribution-r02` |
| Requirement / baseline / dependency | `REQ-20260802-004` / planning `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` / 02 |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

`johnny_router_cli.main(argv, ports)` accepts the closed operation union and returns one typed
finite result before any process, filesystem, Git or host effect. `build_plugin_distribution_profile()`
constructs exact profile `plugin-distribution-poc-r02` v2 while preserving the base transition
graph; unknown operation, stale profile, missing Git/Python and incompatible Python fail closed.
Only `PREFLIGHT` executes in this ticket; every other valid operation returns a typed
`CAPABILITY_UNAVAILABLE` until its later composition dependency exists.

Writable scope: `library/workflow_router/profile.py`,
`library/local_orchestration/johnny_router_contracts.py`,
`library/local_orchestration/johnny_router_cli.py`, `tests/test_plugin_distribution_profile.py`,
`tests/test_plugin_distribution_cli.py`. No launcher or external effect.

## TDD, verification and return

Closure `CLOSURE-PD-04-R03-01`: C1 exact Profile; C2 preflight success; C3 finite probe failures;
C4 unknown/stale rejection before port call; C5 import-time silence. First red:
`python -m pytest -q tests/test_plugin_distribution_cli.py -k test_cli_unknown_operation_returns_blocked_without_port_call`.
Verify with `python -m pytest -q tests/test_plugin_distribution_profile.py tests/test_plugin_distribution_cli.py`,
`python -m mypy --strict library/workflow_router/profile.py library/local_orchestration/johnny_router_contracts.py library/local_orchestration/johnny_router_cli.py`
and `python -m pytest -q`; reverse-mutate operation admission. Return typed completion
with commit/cells/digests/cleanup; a required new operation is `CHANGE_DETECTED`.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
