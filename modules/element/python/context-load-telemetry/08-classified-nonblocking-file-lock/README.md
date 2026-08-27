# Classified nonblocking reusable file lock

This target-owned element indexes closure
`TICKET-CONTEXT-TELEMETRY-08-CLASSIFIED-NONBLOCKING-FILE-LOCK`, revision 01.

Source and evidence:

- `library/local_orchestration/file_lock.py`
- `tests/test_file_lock.py`
- `library/功能集群/python/exclusive_file_lock/README.md`
- `ADR-20260827-024`

The public surface is `ExclusiveFileLock`, its existing
`ExclusiveWindowsFileLock` alias, and `FileLockAcquireDecision`. The explicit
`try_acquire()` path is nonblocking and returns `ACQUIRED` or `CONTENDED`; the
existing context-manager path remains blocking and explicit `release()` closes
an acquired handle. Tests prove the Windows
process contention path and guard the POSIX branch from source only on this
Windows host. This element does not implement or connect
`TelemetryStorageLockPort` and contains no production source copy.
