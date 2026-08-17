# 11 — Attempt-owned install transaction

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-05, AC-06 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 10 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, fake effect ports only / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

One `PluginInstallTransaction` verifies archive/manifest/lock, presents the exact dependency plan,
and through injected ports creates only attempt-owned venv/plugin/launcher effects. Any missing
Git/Python, incompatible ABI, hash failure, interruption or registration readback failure
compensates only effects recorded by that attempt. Implementation uses fakes; no live install.

Writable scope: `library/local_orchestration/plugin_install_transaction.py`, repository-root
`install.ps1`, repository-root `johnny-router.ps1`, and
`tests/test_plugin_distribution_install_transaction.py`. Existing install/runtime contracts are
read-only dependencies.

## TDD, verification and return

Closure `CLOSURE-PD-11-R03-01`: I1 verified plan; I2 exact effect order/readback; I3 failure
compensation; I4 foreign/orphan preservation; I5 repeated attempt conflict. First red:
`python -m pytest -q tests/test_plugin_distribution_install_transaction.py -k test_hash_mismatch_compensates_only_attempt_owned_effects`.
Verify with `python -m pytest -q tests/test_plugin_distribution_install_transaction.py`,
`python -m mypy --strict library/local_orchestration/plugin_install_transaction.py`,
`pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw install.ps1)) | Out-Null; [scriptblock]::Create((Get-Content -Raw johnny-router.ps1)) | Out-Null"`
and `python -m pytest -q`; reverse-mutate ownership admission. Delete fake/temp
effects; return typed commit/cell/digest/cleanup evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
