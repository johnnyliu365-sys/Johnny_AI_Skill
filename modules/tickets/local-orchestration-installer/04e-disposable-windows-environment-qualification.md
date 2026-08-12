# 04E — Disposable Windows Environment Qualification

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / staging architecture and AC-08, AC-11 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 04D remote staging SHA approved |
| Environment | Owner-authorized disposable Windows user/VM/sandbox; never target project |
| Implementation owner | `UNALLOCATED` |
| XSS | `XSS_NOT_APPLICABLE` |

## Sole outcome

Qualify one standard-user Windows isolation provider for later exact staged
source/artifact tests. Do not run setup, uninstaller or host registration.

## Acceptance cells

- Prove Windows version/architecture, standard user/no elevation, isolated
  user/config/process/filesystem scope and no live Codex/target-project alias.
- Prove immutable explicit inputs, observable physical evidence, retention until
  product absence and later external boundary destruction.
- Preserve seeded foreign sentinels and target-repository snapshots byte/Git
  unchanged.
- Missing/admin-only/live-user/non-Windows/unbounded/ambiguous provider or
  failed cleanup/readback returns `ENVIRONMENT_UNAVAILABLE`; a temporary
  directory alone is insufficient.

This ticket proves environment capability only, not product lifecycle.
