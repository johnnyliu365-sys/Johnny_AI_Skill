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

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `INTEGRATED / CLOSED` |
| Implementation | `feat: add receipt-owned uninstall transaction` on `claude/skill-plugin-parallel-control-42c487`; owner-authorized direct allocation |
| Closure | U1 ordered removal: block → cancel subscriptions → stop runners → per-record ownership probe → remove in PLUGIN_PAYLOAD/VENV/LAUNCHER/QUEUE/TELEMETRY order → absence readback per record → ledger close last. U2 foreign preservation: one FOREIGN/UNKNOWN probe halts before any delete with every owned and foreign entry intact. U3 failed block/cancel/stop and failed removal halt with the ledger retained and exact removed/remaining split. U4 absence readback failure retains the ledger. U5 repeat run returns `NOT_INSTALLED`; an absent ledger with owned residue blocks as `RESIDUAL_OWNED_STATE`. Foreign ledger receipt and foreign request objects halt untouched. |
| Verification | focused `6 passed, 10 subtests`; `mypy --strict --no-incremental` clean over module and test; full `782 passed, 2586 subtests`; 218 Python files compiled in memory; zero cache/bytecode residue. |
| Reverse mutation | Ownership matching relaxed to admit FOREIGN probes → `test_foreign_path_halts_before_any_delete` red; exact bytes restored; focused rerun `6 passed, 10 subtests`. |
| Boundary | Fake effect ports only; no live uninstall, filesystem, Git, host or target-project effect; launcher and install files untouched. |

Canonical SHA-256: `plugin_uninstall_transaction.py`
`B188432EA57DBBB5E3B3D59CD5A3162E071BA70408444DEA3DD1C07FCB8EE8C6`;
`test_plugin_distribution_uninstall_transaction.py`
`2A09E9927642FE410EC266A5AA7DAE75DE151742B283177EBDB9F73B588B13BD`.
