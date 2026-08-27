# 08｜Classified nonblocking reusable file lock

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-08-CLASSIFIED-NONBLOCKING-FILE-LOCK` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 05 / AC-15 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 05 / `ADR-20260827-023` / `ADR-20260827-024` |
| State / closure | `OPEN / APPROVED_FOR_DISPATCH`; `CLOSURE-CONTEXT-TELEMETRY-08-CLASSIFIED-FILE-LOCK`, revision 01 |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): authorized the isolated classified nonblocking reusable-lock closure recorded by Specification Revision 05 and ADR-20260827-024. |
| Baseline / dependency | `033bb204b002e7bb7298159f6d522894cb42e07b`; Ticket 07 (`0ded2ed`) and the blocking-only catalog admission (`6b5a7c1`) are integrated. Ticket 06 remains blocked. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL`, one same-lifetime synchronous owner lane and no helpers. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-08-classified-file-lock` on `implement/context-load-telemetry-08-classified-file-lock` from this exact baseline. No runner, queue, receipt, descriptor, gateway, or host workspace readback is required. |
| Delivery / language | `POC / STANDARD` floor; Python 3.11, complete typed annotations and `mypy --strict`. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Tests may create/remove only disposable lock files and independent child processes beneath test-created temporary roots. No telemetry, ledger, provider, credential, host CLI, target-project, Git, network, runner, queue, receipt, release, or deployment effect is authorized. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/file_lock.py
modify = tests/test_file_lock.py
modify = library/功能集群/python/exclusive_file_lock/README.md
create = modules/element/python/context-load-telemetry/08-classified-nonblocking-file-lock/
forbid = library/local_orchestration/telemetry_storage/
forbid = library/workflow_router/
forbid = library/local_orchestration/johnny_root_layout.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

An authorized local infrastructure caller can use one existing `ExclusiveFileLock` instance to
attempt the same advisory one-byte lock without blocking. It receives exactly
`FileLockAcquireDecision.ACQUIRED` when it owns the instance's opened handle, or
`FileLockAcquireDecision.CONTENDED` when an independent process already holds that exact lock.
After `ACQUIRED`, explicit `release()` drops and closes the same handle. `CONTENDED` retains no
handle and performs no guarded-state effect. Every existing `with ExclusiveFileLock(path):`
caller remains blocking and behaviorally compatible.

`TicketDecompositionDecision = READY_LOW_MODEL`: this is one finite process-visible primitive,
one source module/test seam, one public enum, and one independently verifiable result. The
approved SPEC fixes the platform behavior, error distinction, ownership, and out-of-scope
boundaries; no unresolved product or adapter decision is delegated to the implementation owner.

This closure does not implement `TelemetryStorageLockPort`, select a telemetry adapter, mint a
telemetry token, resolve a storage ref, touch JSONL/ledger state, map to
`TelemetryStorageDecision.LOCK_CONTENDED`, alter six existing consumers, add a retry/timeout,
create a worker/queue/runner, invoke provider/host services, or publish a plugin.

## Frozen public contract and source rules

`library.local_orchestration.file_lock` exports these three names and no second lock class:

```text
FileLockAcquireDecision = ACQUIRED | CONTENDED

ExclusiveFileLock(lock_path: Path)
ExclusiveFileLock.__enter__() -> ExclusiveFileLock        # existing blocking semantics
ExclusiveFileLock.__exit__(...) -> None                   # existing blocking release semantics
ExclusiveFileLock.try_acquire() -> FileLockAcquireDecision
ExclusiveFileLock.release() -> None
ExclusiveWindowsFileLock is ExclusiveFileLock             # existing alias
```

`FileLockAcquireDecision` is a finite, named `str`-backed `Enum` with exactly the serializable
values `"acquired"` and `"contended"`. No string, Boolean, `None`, dynamic mapping, `Any`, or
exception instance is a successful result. `try_acquire` opens the already-selected dedicated
lock path exactly as the existing primitive does. It is valid only while `_handle` is absent;
calling it while this object holds a handle raises `RuntimeError`, not a third result.

On `ACQUIRED`, the instance retains that one opened handle. `release()` is valid only then; it
calls the already-bound release primitive and always closes and clears the retained handle in a
`finally` path. If release itself raises `OSError`, the error propagates after cleanup; a later
`release()` without a new acquire raises `RuntimeError`. A fresh `try_acquire()` after that
cleanup is allowed. On `CONTENDED`, the opened contender handle is closed and `_handle` is
absent before return.

The module chooses its platform primitive once at import, not per instance:

- Windows `_try_acquire` calls `msvcrt.locking(..., msvcrt.LK_NBLCK, 1)`. After successful open,
  only `OSError` with `errno == errno.EACCES` from that bound call returns `CONTENDED`; every
  other `OSError` propagates exactly. The actual two-process Windows evidence is
  `errno=13`, no `winerror`, and immediate return.
- POSIX `_try_acquire` calls `fcntl.flock(..., fcntl.LOCK_EX | fcntl.LOCK_NB)` and may return
  `CONTENDED` only for `errno.EACCES` or `errno.EAGAIN`; all other errors propagate. The
  Windows review can source-guard this branch but cannot claim it executed.
- The existing blocking `_acquire`/`_release` behavior remains bound and unchanged in meaning.
  No retry loop, timeout, sleep, polling, background thread/process, global state, or fallback
  from `try_acquire` to the blocking primitive is allowed.

Update the existing exact module card only after the source/test evidence is green. Its public
surface, strict evidence, Windows proof, POSIX limitation, error distinction, and prohibition on
direct `TelemetryStorageLockPort` use must remain truthful. Create
`modules/element/python/context-load-telemetry/08-classified-nonblocking-file-lock/README.md` as
an index to this ticket's source, test, card and ADR; it copies no production source.

### Reusable-module selection record

```text
selected: exclusive-file-lock@6b5a7c1 (blocking catalog baseline; this ticket is its approved
          classified-nonblocking successor)
why: ADR-20260827-023 requires a separate capability closure rather than translating every
     blocking-lock OSError into telemetry contention.
read: library/MODULE_CATALOG.md -> catalog/capabilities/README.md ->
      功能集群/python/exclusive_file_lock/README.md -> file_lock.py -> tests/test_file_lock.py.
restriction: this ticket improves the reusable primitive only. It neither selects it for nor
             imports it into TelemetryStorageLockPort or a storage adapter.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| FL1 | Ordinary public construction returns `ACQUIRED` on an available disposable lock. `release()` clears it; another fresh acquire succeeds. The existing context-manager tests still prove blocking exclusion, release, abandoned-holder recovery, advisory semantics, alias identity, and all six consumers. |
| FL2 | A real independent child process holds the same disposable one-byte lock before the contender runs. The contender returns exactly `CONTENDED`, retains no handle, and cannot enter the guarded witness. After holder release, a fresh contender can acquire and release. No timing threshold is success evidence; the bound nonblocking primitive and finite result are. |
| FL3 | A missing parent, empty/unusable path, and an injected non-contention `OSError(errno.EIO)` propagate by name and leave no retained handle. They never return `CONTENDED`; no directory is invented for an invalid path. |
| FL4 | Lifecycle misuse is not silently reclassified: double `try_acquire` while held and `release()` while idle raise `RuntimeError`; a release primitive error is re-raised only after the retained handle is cleared. Enum validation rejects an unknown serialized value. |
| FL5 | The bounded AST/source gate proves one import-time platform branch; `ExclusiveFileLock` names no platform module; Windows nonblocking acquisition uses only `LK_NBLCK` and classifies only `errno.EACCES`; POSIX uses `LOCK_EX | LOCK_NB` and classifies only `EACCES`/`EAGAIN`; blocking acquisition remains `LK_LOCK` / `LOCK_EX`; no retry/sleep/timeout/worker/fallback construct exists. |
| FL6 | The updated module card and element index name the exact public API, real Windows evidence, source-only POSIX limitation, and the continuing direct-telemetry prohibition. Focused tests, strict type check, compilation, boundary diff, and residue check pass. |
| LM1 | Replace Windows `LK_NBLCK` with `LK_LOCK`; FL5 turns red before any potentially blocking process test, then byte-exact restoration returns green. |
| LM2 | Broaden the nonblocking `OSError` handler so `EIO` becomes `CONTENDED`; FL3 turns red, then byte-exact restoration returns green. |
| LM3 | Remove the `finally` cleanup/clear after explicit release failure; FL4 turns red, then byte-exact restoration returns green. |
| LM4 | Remove `LOCK_NB` from the POSIX source branch or widen its errno allowlist; FL5 turns red, then byte-exact restoration returns green. |

Strong-type preflight constructs both enum values and ordinary public success paths without casts,
`Any`, bypass constructors, historical-object reuse, dynamic lookup, or mocks as success
evidence. Negative-only tests may inject a bound primitive failure to prove propagation. This is
new behavior, so no ceremonial baseline-red claim is admissible; FL1–FL6 discriminating tests and
LM1–LM4 restored reverse mutations are required instead.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_file_lock.py
py -3.11 -m mypy --strict library/local_orchestration/file_lock.py tests/test_file_lock.py
py -3.11 -m compileall -q library/local_orchestration/file_lock.py
git diff --check 033bb204b002e7bb7298159f6d522894cb42e07b HEAD
git status --short
```

The Terra/xhigh reviewer independently verifies the exact ticket blob/baseline/boundary and
re-runs all commands. The reviewer performs an own reverse mutation through a different door
than LM1–LM4 — for example, alter the Windows `EACCES` classifier so the real FL2 process path
does not return `CONTENDED` — restores byte-exactly, then re-runs focused tests. The reviewer
also confirms no telemetry-storage import or effect, no change to a current consumer, and no
claim of POSIX runtime qualification. Full-suite/residue checks and guarded integration are the
reviewer’s responsibility.

## Ownership and return

This closure is same-lifetime synchronous: the Terra/xhigh reviewer dispatches, waits, receives,
reviews, writes the candidate commit, and submits it to the integration gate. It requires no
runner, queue, receipt, descriptor, gateway, or host workspace readback. The Luna/xhigh
implementation owner modifies only this declared boundary and does not commit, push, alter
requirements, select the later telemetry adapter, or control another agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with FL/LM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes telemetry storage, provider usage, cost comparison, target mutation,
integration, push, publication, release, or deployment.

```johnny-status
id = 08
title = Classified nonblocking reusable file lock
state = OPEN
stage = C | frozen reusable-lock contract and TDD matrix | DONE
stage = M | Luna/xhigh implementation | PENDING
stage = R | Terra/xhigh review and guarded integration | PENDING
```
