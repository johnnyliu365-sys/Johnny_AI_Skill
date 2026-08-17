# 05 — Project runner registry

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-07, AC-08 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 04 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

One `ProjectRunnerRegistry` admits at most one active temporary runner for one opaque project and
tracks zero-or-more distinct subscription IDs. Adding the first subscription starts through an
injected `RunnerLifecyclePort`; removing the last, detach or uninstall stops exactly that runner.
Duplicate/foreign IDs and restart auto-start reject. No Git readback or host wake exists here.

Writable scope: `library/local_orchestration/project_runner_registry.py` and
`tests/test_plugin_distribution_runner_registry.py`.

## TDD, verification and return

Closure `CLOSURE-PD-05-R03-01`: R1 first start; R2 same-project reuse; R3 foreign/duplicate block;
R4 last-close/detach/uninstall stop; R5 no auto-start recovery. First red:
`python -m pytest -q tests/test_plugin_distribution_runner_registry.py -k test_second_runner_for_same_project_is_rejected_before_start`.
Verify with `python -m pytest -q tests/test_plugin_distribution_runner_registry.py`,
`python -m mypy --strict library/local_orchestration/project_runner_registry.py` and
`python -m pytest -q`; reverse-mutate the uniqueness guard. Rollback closes fixture runners only.
Return typed commit/cell/digest/cleanup evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
