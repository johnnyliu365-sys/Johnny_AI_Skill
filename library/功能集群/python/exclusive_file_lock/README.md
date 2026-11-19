# Exclusive File Lock（Python）

| Field | Value |
| --- | --- |
| Module ID | exclusive-file-lock |
| Lifecycle | READY |
| Public import | library.功能集群.python.exclusive_file_lock: ExclusiveFileLock, FileLockAcquireDecision |
| Compatibility alias | ExclusiveWindowsFileLock is the same object and remains exported for existing consumers |
| Contract source | library/功能集群/python/exclusive_file_lock/file_lock.py |
| Behavior evidence | tests/test_exclusive_file_lock.py — Windows: 32 tests and 11 subtests passed, including blocking compatibility, child-process contention, and lifecycle evidence |
| Strict evidence | mypy --strict --python-version 3.11 library/功能集群/python/exclusive_file_lock/__init__.py library/功能集群/python/exclusive_file_lock/file_lock.py tests/test_exclusive_file_lock.py; compileall source passed |
| Catalog admission | ADR-20260827-023 at repository commit 0417ae4a0ef9efa75d3bd08ab4d5e5c45dc0b650 |
| Dependencies | Standard library only; no reusable-module dependency |

## Public capability

ExclusiveFileLock is an OS-visible, advisory, blocking exclusive lock over one dedicated lock-file
path. Cooperating independent processes using the same path cannot enter the protected section
simultaneously. Leaving the context closes the handle and releases the lock; a killed holder
leaves a later taker able to acquire it. `try_acquire()` is the explicit nonblocking companion:
it returns `FileLockAcquireDecision.ACQUIRED` while retaining the opened handle, or
`FileLockAcquireDecision.CONTENDED` after closing the contender handle. Explicit `release()`
drops and closes that retained handle, including after a release primitive error. The module binds
the platform primitive once at import: Windows uses msvcrt byte-region locking and POSIX source
uses fcntl.flock.

## Minimum reading path

1. This card.
2. library/功能集群/python/exclusive_file_lock/file_lock.py.
3. tests/test_exclusive_file_lock.py when behavior, platform evidence, lifecycle or contention semantics
   matter.

## Required use and prohibited use

- Use only inside an already-authorized local infrastructure adapter. The Path argument is an
  internal resolved location and must never cross an external, Router, telemetry, ticket, prompt,
  log or provider boundary.
- Every participating process must use the same dedicated lock path. The primitive is advisory:
  it does not protect bytes from a process that ignores the lock.
- Existing context-manager behavior remains blocking acquisition. On Windows, `LK_LOCK` retains
  its existing bounded retry window and can raise an `OSError`; only `errno.EACCES` from the
  separate `LK_NBLCK` path is classified as `CONTENDED`. POSIX source classifies only
  `EACCES`/`EAGAIN` from `LOCK_EX | LOCK_NB` as `CONTENDED`.
- This capability has no ownership token, timeout/retry policy, expected-revision check, telemetry
  failure mapping or storage/ledger semantics.
- It carries no telemetry, storage or ledger semantics.
- POSIX exclusivity is source-guarded here but not behavior-proven on this Windows host. Do not
  claim cross-platform runtime qualification without a POSIX evidence run.

## Selection record

~~~text
selected: exclusive-file-lock@6b5a7c1 (cataloged blocking baseline and this classified successor)
why: owner authorized the isolated nonblocking classification closure without changing blocking
     consumers.
read: this README -> library/功能集群/python/exclusive_file_lock/file_lock.py -> tests/test_exclusive_file_lock.py.
dependency: none.
boundary: only an already-authorized local infrastructure adapter may use this path; no telemetry,
ledger, provider, host or target-project state crosses this capability.
~~~
