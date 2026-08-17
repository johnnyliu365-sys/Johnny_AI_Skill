# 12 — Receipt-owned uninstall transaction

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-06, AC-13 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 11 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, fake effect ports only / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

`PluginUninstallTransaction` blocks new work, closes exact subscriptions/runners, removes only
receipt-owned plugin/venv/launcher/queue/telemetry state, verifies absence and is idempotent.
Unknown, foreign or failed-removal state halts without deleting the ownership ledger or any target
content. Implementation uses fakes; no live uninstall.

Writable scope: `library/local_orchestration/plugin_uninstall_transaction.py` and
`tests/test_plugin_distribution_uninstall_transaction.py`. Launcher and install files are read-only.

## TDD, verification and return

Closure `CLOSURE-PD-12-R03-01`: U1 ordered owned removal; U2 foreign preservation; U3 failed stop
halts with ledger; U4 absence readback; U5 repeat idempotence. First red:
`python -m pytest -q tests/test_plugin_distribution_uninstall_transaction.py -k test_foreign_path_halts_before_any_delete`.
Verify with `python -m pytest -q tests/test_plugin_distribution_uninstall_transaction.py`,
`python -m mypy --strict library/local_orchestration/plugin_uninstall_transaction.py` and
`python -m pytest -q`; reverse-mutate ownership matching. Delete fake records only; return typed evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
