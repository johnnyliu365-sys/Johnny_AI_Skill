# Exclusive File Lock（Python）

| Field | Value |
| --- | --- |
| Module ID | exclusive-file-lock |
| Lifecycle | READY |
| Public import | library.local_orchestration.file_lock: ExclusiveFileLock |
| Compatibility alias | ExclusiveWindowsFileLock is the same object and remains exported for existing consumers |
| Contract source | library/local_orchestration/file_lock.py |
| Behavior evidence | tests/test_file_lock.py — Windows: 18 tests and 17 subtests passed at catalog admission |
| Strict evidence | mypy --strict library/local_orchestration/file_lock.py tests/test_file_lock.py; compileall source passed |
| Catalog admission | ADR-20260827-023 at repository commit 0417ae4a0ef9efa75d3bd08ab4d5e5c45dc0b650 |
| Dependencies | Standard library only; no reusable-module dependency |

## Public capability

ExclusiveFileLock is an OS-visible, advisory, blocking exclusive lock over one dedicated lock-file
path. Cooperating independent processes using the same path cannot enter the protected section
simultaneously. Leaving the context closes the handle and releases the lock; a killed holder
leaves a later taker able to acquire it. The module binds the platform primitive once at import:
Windows uses msvcrt byte-region locking and POSIX source uses fcntl.flock.

## Minimum reading path

1. This card.
2. library/local_orchestration/file_lock.py.
3. tests/test_file_lock.py when behavior, platform evidence, lifecycle or contention semantics
   matter.

## Required use and prohibited use

- Use only inside an already-authorized local infrastructure adapter. The Path argument is an
  internal resolved location and must never cross an external, Router, telemetry, ticket, prompt,
  log or provider boundary.
- Every participating process must use the same dedicated lock path. The primitive is advisory:
  it does not protect bytes from a process that ignores the lock.
- Existing public behavior is blocking acquisition. On Windows, msvcrt.LK_LOCK has a bounded retry
  window and can raise an OSError; this card does not classify that exception as contention.
- This current API has no nonblocking acquisition result, ownership token, timeout/retry policy,
  expected-revision check, telemetry failure mapping or storage/ledger semantics.
- Therefore this revision is not selected for TelemetryStorageLockPort.try_acquire and may not be
  imported by the future telemetry adapter merely because this card is READY.
- POSIX exclusivity is source-guarded here but not behavior-proven on this Windows host. Do not
  claim cross-platform runtime qualification without a POSIX evidence run.

## Selection record

~~~text
selected: exclusive-file-lock@0417ae4 (cataloged blocking capability)
why: owner authorized audit and catalog admission of the existing shared OS-visible primitive.
read: this README -> library/local_orchestration/file_lock.py -> tests/test_file_lock.py.
dependency: none.
telemetry result: rejected for direct TelemetryStorageLockPort adoption. Revision 04 requires a
  finite named LOCK_CONTENDED path; this module currently blocks and exposes only an unclassified
  OSError after Windows bounded contention.
boundary: a successor capability ticket must add and prove a separate classified nonblocking
  acquisition surface without changing the six existing blocking consumers.
~~~
