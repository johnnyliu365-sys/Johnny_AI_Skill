# 14 — Scripted SourceProjectA package qualification

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-06, AC-10–AC-15 / `ctx-plugin-distribution-r02` |
| Dependencies / planning baseline | 08, 12, 13 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no model/helper during matrix / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

One deterministic qualification report installs the candidate only into a Johnny-owned disposable
copy and runs two bounded matrices: target preservation/install/uninstall, then Router transitions,
invalid handoffs, roles, FIFO and dependency clusters. The original
`D:\SourceProjectA\SourceProjectA\private-target-repo` is read-only pre/post evidence. Missing host wake remains
non-binding. All disposable copies, runtime, cache and generated evidence are deleted afterward.

Writable scope: `tests/test_plugin_distribution_vita_qualification.py` and
`tests/staging/plugin_distribution_vita/`. No original Vita or production effect.

## TDD, verification and return

Closure `CLOSURE-PD-14-R03-01`: V1 package-only install; V2 original identity preserved; V3 valid
matrix; V4 invalid bindings rejected; V5 FIFO/cluster; V6 uninstall and zero residue. First red:
`python -m pytest -q tests/test_plugin_distribution_vita_qualification.py -k test_qualification_preserves_original_vita_head_and_status`.
Verify with `python -m pytest -q tests/test_plugin_distribution_vita_qualification.py`,
`python -m mypy --strict tests/test_plugin_distribution_vita_qualification.py` and
`python -m pytest -q`, then prove staging/residue absence. Return typed evidence;
manual forwarding cannot satisfy host-wake or Router-binding cells.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
