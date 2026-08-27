# Ticket 09 — Local telemetry-storage lock port

This element indexes the bounded implementation of the existing
`TelemetryStorageLockPort` contract. The implementation is
[`local_lock_adapter.py`](../../../../../../library/local_orchestration/telemetry_storage/local_lock_adapter.py),
and its focused executable checks are
[`test_telemetry_storage_lock_adapter.py`](../../../../../../tests/test_telemetry_storage_lock_adapter.py).

## Authority and selected inputs

- Ticket: `modules/tickets/context-load-telemetry/09-local-telemetry-storage-lock-port.md`
- Existing contract: `library/local_orchestration/telemetry_storage/contracts.py`
- Selected reusable card: `exclusive-file-lock@60d2ab0`
  (`library/功能集群/python/exclusive_file_lock/README.md`)
- Selected reusable card: `path-containment@ccefa77`
  (`library/功能集群/python/path_containment/README.md`)
- Selected path predicate: `library/local_orchestration/path_containment.py`
- Selected layout: `library/local_orchestration/johnny_root_layout.py`
- ADRs: `ADR-20260827-022`, `ADR-20260827-023`, and `ADR-20260827-024`

The adapter derives its lock path from the injected typed `JohnnyRootLayout`,
uses the selected nonblocking file-lock primitive, and returns only the typed
lock DTOs. It does not duplicate the selected source modules, claim a platform
runtime, or expose paths and operating-system diagnostics in its failures.
