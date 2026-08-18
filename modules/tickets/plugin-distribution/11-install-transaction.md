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

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `INTEGRATED / CLOSED` |
| Implementation | `f6bd96a` on `claude/skill-plugin-parallel-control-42c487`; owner-authorized direct allocation to the current lane |
| Closure | I1 verified plan: approved bundle digests, lock binding and capable host produce `INSTALLED` with the exact lock-derived plan. I2 exact order: archive read → probe → journal open → venv → record → plugin payload → record → launcher → record → registration readback → seal. I3 compensation: dependency hash mismatch, mid-sequence interruption and readback failure unwind only this attempt's recorded receipts in reverse; a failed removal yields `COMPENSATION_INCOMPLETE` naming the remainder. I4 foreign/orphan receipts survive success and compensation. I5 repeated attempt returns `ATTEMPT_CONFLICT` before any effect. `LOCK_MISMATCH` was removed as an unreachable sentinel: `RuntimeDependencyLock` is closed by construction, so a deviant lock rejects as `REQUEST_INVALID` at strict revalidation. |
| Verification | focused `7 passed, 15 subtests`; `mypy --strict --no-incremental` clean over module and test; `install.ps1` / `johnny-router.ps1` scriptblock parse checks pass under Windows PowerShell 5.1 (`pwsh` absent on this host; `#Requires -Version 5.1` makes 5.1 the binding parse floor); full `776 passed, 2576 subtests`; 216 Python files compiled in memory; zero cache/bytecode residue. |
| Reverse mutation | Ownership admission (`CONFLICT` gate) bypassed → I5 cell red; exact bytes restored; focused rerun `7 passed, 15 subtests`. |
| Boundary | Fake effect ports only; no live install, download, PATH/global change, Git effect or target-project write. `install.ps1` is read-only verification/plan/confirmation and stops at `LIVE_INSTALL_NOT_AUTHORIZED`; `johnny-router.ps1` forwards to the owned runtime or reports `JOHNNY_RUNTIME_NOT_INSTALLED`. |

Canonical SHA-256: `plugin_install_transaction.py`
`9AC2B2B2B3F9984110FCCB64E3D872A0F40472DFF36C4CFCC52DEF0558DC3B90`;
`test_plugin_distribution_install_transaction.py`
`E380F6B05BF8C7AEE4DC0CA22D21EFFA71303501FC402D62A4C05C87DD7C3EC7`;
`install.ps1` `2FCC7826A80628E7CD75D0B1B6EE3FF7963EDB4C811D0B444498F671EEA9458A`;
`johnny-router.ps1` `EFE285AD5C727ADF1A7F0754BD55F775F69FA89F66B2CF8D2201DAB6CDE3CED2`.
