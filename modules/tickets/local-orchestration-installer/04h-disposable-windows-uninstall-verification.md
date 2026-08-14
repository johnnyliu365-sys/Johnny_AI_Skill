# 04H — Disposable Windows Uninstall and Absence Verification

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-06 through AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T04H-01` / uninstall acceptance cells below |
| Dependency | 04G approved; exact 04F artifact and 04E provider unchanged |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict`; setup/uninstaller processes are injected system effects |
| Environment | Fresh exact 04E-qualified Windows boundary |
| Implementation owner | `UNALLOCATED` |
| XSS | Inherit 04B/04F classification |

## Sole outcome

Install exact artifact, invoke matching normal uninstaller once, prove complete
owned removal and prove replay returns `NOT_INSTALLED` without mutation.

## Acceptance cells

- Remove all receipt-owned payload/runtime/state/host/profile data with fresh
  physical absence.
- Preserve foreign/manual registration, unrelated global config and target
  repositories byte/Git unchanged.
- Tampered/missing/foreign receipt, unsafe path, stop/unregister/filesystem
  failure and interruption return `UNINSTALL_BLOCKED`, retaining only owned
  retry state and never broad-deleting.
- Direct/replay/repair/indirect paths use same proof. Reverse deletion order,
  full absence and foreign preservation to named red tests before restore.

Sandbox destruction occurs only after product evidence and is not a substitute.
