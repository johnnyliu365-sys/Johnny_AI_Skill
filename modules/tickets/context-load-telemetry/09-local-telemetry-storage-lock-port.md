# 09｜Local telemetry-storage lock port

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-09-LOCAL-LOCK-PORT` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 06 / AC-06, AC-13 through AC-15 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 06 / `ADR-20260827-022` through `ADR-20260827-024` |
| State / closure | `OPEN / APPROVED / READY_LOW_MODEL`; `CLOSURE-CONTEXT-TELEMETRY-09-LOCAL-LOCK-PORT`, revision 03 |
| Document revision | `03` — admission corrections preserve the pure contract package surface and keep worktree-state proof out of a persisted regression test. |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): authorized the one independently scoped local `TelemetryStorageLockPort` closure recorded by Specification Revision 06. |
| Source baseline / dependency | `dda74a25a5c83cf09500b886701c5e99d4b04c20`; the candidate must also descend from the committed current-main ticket authority. Ticket 07 (`0ded2ed`) freezes lock DTOs, Ticket 08 (`60d2ab0`) delivers the classified lock, and Revision 06 catalogs `path-containment`. Ticket 06 remains blocked and non-integrable. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL`, one synchronous owner lane and no helpers. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-09-local-lock-port` on `implement/context-load-telemetry-09-local-lock-port` from current committed `main` that descends from the source baseline, then binds that exact ticket revision and baseline to the owner. No runner, queue, receipt, descriptor, gateway, or host workspace readback is required. |
| Delivery / language | `POC / STANDARD` floor; Python 3.11, complete annotations, frozen strict DTOs, and `mypy --strict`. |
| XSS / effects | `XSS_NOT_APPLICABLE`. The adapter's only authorized effect is a dedicated lock file below an injected Johnny `telemetry` root. Tests may create/remove only disposable roots and child processes. No ledger/stream/JSONL, provider, credential, host CLI, target-project, Git, network, runner, queue, receipt, publication, release, or deployment effect is authorized. |

## Boundary declaration

```johnny-boundary
create = library/local_orchestration/telemetry_storage/local_lock_adapter.py
create = tests/test_telemetry_storage_lock_adapter.py
create = modules/element/python/context-load-telemetry/09-local-telemetry-storage-lock-port/
forbid = library/local_orchestration/telemetry_storage/__init__.py
forbid = library/local_orchestration/telemetry_storage/contracts.py
forbid = library/local_orchestration/file_lock.py
forbid = library/local_orchestration/path_containment.py
forbid = library/local_orchestration/johnny_root_layout.py
forbid = library/workflow_router/
forbid = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
forbid = library/local_orchestration/telemetry_storage/composition.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## Admission correction — revision 02

Revision 01 incorrectly required a package-root re-export. The pre-existing strict-contract
closure source-guards `telemetry_storage/__init__.py` as a pure `.contracts` re-export only;
adding a local filesystem adapter there turns every package-contract import into infrastructure
import and makes `tests/test_telemetry_storage_contracts.py::TestSourceBoundary::test_sc6_owned_modules_are_strict_and_effect_free`
red. The existing guard is the controlling source fact, so this correction changes no adapter
behavior or public lock DTO: the adapter is imported only from its exact module path and the
package init remains untouched. Rebase the same candidate branch onto this committed correction,
restore its out-of-bound init modification, and retain every permitted source/test change
additively.

## Admission correction — revision 03

Revision 02's initial LPA8 test tried to prove the declared candidate boundary by reading
`git status`. That condition is true only before the reviewer commits: after an admissible commit
the identical clean checkout has an empty status and the persisted test falsely fails. Candidate
diff and clean-worktree proof are review evidence, not a production regression property. Retain
the element-index/content checks in LPA8; remove every `git status`/candidate-path assertion from
the persisted test. The reviewer must instead inspect the exact Git diff before staging and again
the committed diff before integration.

## One observable closure

`LocalTelemetryStorageLockAdapter` is one importable local implementation of the existing
`TelemetryStorageLockPort`. Given a strict `TelemetryStorageLockRequest`, it derives the same
dedicated lock-file identity for every request with the same exact opaque stream tuple
`(storage_ref, project_id, stream_id, ownership_ledger_ref)`. It returns exactly one existing
`TelemetryStorageLockAcquired` with a fully bound original token, or exactly one existing
`TelemetryStorageLockContended` when an independent adapter/process holds that same location.
After a successful acquire, passing that exact original token back to the same adapter returns
`TelemetryStorageLockReleased` and frees the location for a later contender.

`TicketDecompositionDecision = READY_LOW_MODEL`: Revision 06 fixes the public DTOs, lock identity,
selected dependencies, finite result meanings, release ownership, path boundary, I/O failure
handling, effect scope, test fixture and out-of-scope storage behavior. This ticket implements one
adapter/effect boundary and one finite cross-process closure; no unresolved architecture or
product decision is delegated to the implementation owner.

This closure does not read/create an ownership ledger or telemetry stream, invoke
`JsonlContextUsageStore`, decide expected project/revision equality, re-admit lifecycle or
containment under a lock, advance a revision, map a `TelemetryStorageResponse`, emit a report,
invoke a provider/host, write a target project, or revive Ticket 06's candidate. The next
lock-bound storage-adapter ticket owns those responsibilities.

## Frozen adapter rules

Create only `library/local_orchestration/telemetry_storage/local_lock_adapter.py`. It exports
only `LocalTelemetryStorageLockAdapter` and the sanitized
`TelemetryStorageLockAdapterError`; callers import those names from that exact module, never
the package root. `telemetry_storage/__init__.py` remains byte-identical to the source baseline.
`LocalTelemetryStorageLockAdapter(layout: JohnnyRootLayout)` is the only constructor; it accepts
no caller path, raw root string, digest, lock reference, callback, resolver, dynamic mapping, or
unvalidated input.

The module imports only these selected public surfaces:

```text
library.local_orchestration.file_lock: ExclusiveFileLock, FileLockAcquireDecision
library.local_orchestration.path_containment: resolves_within_root
library.local_orchestration.johnny_root_layout: JohnnyRootLayout
library.local_orchestration.telemetry_storage.contracts: existing lock request/token/result DTOs
```

Its internal path is exactly:

```text
layout.telemetry_root / "storage-locks" / (SHA-256(stream-identity) + ".lock")
```

`stream-identity` is UTF-8 bytes of the fixed version label plus these four validated values in
this order, separated by NUL bytes: `storage_ref`, `project_id`, `stream_id`, and
`ownership_ledger_ref`. `storage_revision`, `expected_project_id`, and
`expected_storage_revision` are not part of the lock key: a stale and a current request for one
stream must contend. The acquired `TelemetryStorageLockToken` carries all five reference
coordinates including the supplied `storage_revision`.

Before the directory is created and again before its lock file is opened, the selected
`resolves_within_root` predicate must accept both the derived lock root and candidate file under
`layout.telemetry_root`. A `False` result raises `TelemetryStorageLockAdapterError` with a stable
message that contains no path, exception text or metadata identity. The same sanitization rule
applies to non-contention `OSError` during mkdir/open/acquire. No non-contention failure may
return `LOCK_CONTENDED`.

The adapter retains one private pair of the real `ExclusiveFileLock` and the exact original
`TelemetryStorageLockToken` object for each acquired `lock_ref`. If that lock ref is already
held by the adapter, or the selected primitive returns `CONTENDED`, return
`TelemetryStorageLockContended(storage_ref, storage_revision, failure_ref)` with no token and
no retained contender handle. `lock_ref`, contention `failure_ref`, and release-failure
`failure_ref` are stable opaque IDs derived from the internal SHA-256 digest with fixed distinct
prefixes; callers never supply them.

`release(token)` succeeds only when the retained original token is the same object (`is`) as the
argument and remains held by this adapter. A copied, reconstructed, stale, cross-adapter or
mismatched token returns `TelemetryStorageLockReleaseFailed` using only the received token's
opaque fields; it does not unlock any held lock. For the original token, remove retained state in
a bounded `finally` path around the real release. A release `OSError` returns the finite
release-failed DTO with no exception or path detail. Do not add retry, timeout, sleep, polling,
worker, queue, runner, global singleton, raw diagnostic, or fallback to blocking acquisition.

Create `modules/element/python/context-load-telemetry/09-local-telemetry-storage-lock-port/README.md`
as a target-owned index to this ticket, exact adapter, focused tests, contracts, selected module
cards and ADR. It copies no production source and claims neither JSONL/storage behavior nor a
POSIX runtime qualification.

### Reusable-module selection record

```text
selected: exclusive-file-lock@60d2ab0; path-containment@ccefa77
why: the first is the delivered finite real OS lock; the second is the delivered exact derived-
     path containment predicate. Together they meet the frozen local lock-file boundary.
read: exclusive-file-lock README -> file_lock.py -> test_file_lock.py;
      path-containment README -> path_containment.py -> test_worktree_containment.py.
dependency: standard-library SHA-256 only.
rejected: JsonlContextUsageStore (legacy stream codec), PluginUninstallLedger (install receipt
          lifecycle), Ticket 06's preserved candidate, and any runner/queue/receipt mechanism.
boundary: neither selected capability supplies ownership-ledger admission, lifecycle/revision
          transition, storage response mapping, provider use, target mutation or release.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| LPA1 | With a disposable absolute `JohnnyRootLayout`, one ordinary strict request acquires a real lock through `LocalTelemetryStorageLockAdapter`; its token has exactly the request reference's five coordinates, a valid generated opaque `lock_ref`, and no serialized filesystem path. Its original token releases to `TelemetryStorageLockReleased`. |
| LPA2 | A real independent child process holds the exact same request's derived lock before a contender attempts it. The contender returns exactly `TelemetryStorageLockContended`, has no token/retained handle, and does not enter the guarded witness. After holder release, a fresh contender acquires/releases. No elapsed-time threshold is evidence. |
| LPA3 | Two requests with the same four-coordinate stream identity but different storage revisions contend; changing any one of those four coordinates yields a distinct independently acquirable lock. This proves revision is not a lock key while every stream-identity coordinate is. |
| LPA4 | Reconstructed, stale, cross-adapter and mismatched tokens return `TelemetryStorageLockReleaseFailed` without releasing the held lock; the held original token still releases exactly once. After release the original/replayed token fails and a fresh adapter can acquire. |
| LPA5 | A redirected Johnny root or existing lock-root ancestor is rejected before any lock-file effect and raises only `TelemetryStorageLockAdapterError` without a raw path/exception. Normal disposable-root creation remains contained under its telemetry root. |
| LPA6 | Injected non-contention acquire/open/mkdir `OSError` becomes the sanitized adapter error, never contention. An injected release `OSError` returns only `TelemetryStorageLockReleaseFailed`, clears retained state, and leaves no completed/released claim. |
| LPA7 | Bounded source/AST gates prove exact selected imports, SHA-256/four-coordinate key construction, two containment checks before effect, original-token identity (`is`), no raw-path constructor/output, no legacy codec/ledger/storage operation/provider/host import, and no retry/sleep/polling/queue/runner/dynamic lookup/`Any`/cast/fallback. They also prove `telemetry_storage/__init__.py` has no candidate diff and retains its existing pure `.contracts` imports. |
| LPA8 | Focused tests, strict type check, compilation and no cache/runtime residue pass. The persisted test proves the element index names exact evidence and limitations honestly; the reviewer independently proves the declared-boundary diff and clean worktree before commit/integration, rather than encoding transient `git status` in a committed test. |
| LM1 | Add `storage_revision` to the lock-key payload; LPA3 turns red, then byte-exact restoration returns green. |
| LM2 | Change the contention path to `LOCK_ACQUIRED` or permit an acquired token for it; LPA2 turns red, then restoration returns green. |
| LM3 | Replace original-token object identity with value equality; LPA4 turns red, then restoration returns green. |
| LM4 | Remove either containment check or let a non-contention `OSError` become contention; LPA5/LPA6/LPA7 turns red, then restoration returns green. |

Strong-type preflight constructs all supplied strict contract values and ordinary adapter success
paths without casts, `Any`, bypass constructors, dynamic lookup, raw paths, historical-object
reuse, mocks or strings as success evidence. Negative-only injection may replace a bound local
primitive to prove sanitization. This is new behavior, so no ceremonial baseline-red claim is
admissible; LPA1–LPA8 and restored LM1–LM4 are the required discriminating evidence.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_lock_adapter.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_contracts.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/local_lock_adapter.py tests/test_telemetry_storage_lock_adapter.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/local_lock_adapter.py
git diff --check dda74a25a5c83cf09500b886701c5e99d4b04c20 HEAD
git status --short
```

The Terra/xhigh reviewer validates the exact ticket blob/baseline/boundary and reusable-module
selection, reruns focused/type/compile gates, verifies that the child proof uses the real
adapter/selected lock rather than a copy, and checks no Ticket 06 source was used. The reviewer
counter-mutates through a distinct door from LM1–LM4: replace the adapter's generated `lock_ref`
prefix while retaining the path digest so production release lookup loses its bound token;
LPA1/LPA4 must turn red. Restore bytes exactly and rerun focused evidence. Full-suite/residue
checks and guarded integration are the reviewer's responsibility; known clean-baseline failures
must be reported, not attributed to this ticket.

## Ownership and return

This closure is same-lifetime synchronous: the Terra/xhigh reviewer dispatches, waits, receives
the return, reviews, writes the candidate commit, and submits it to the integration gate. It
requires no runner, queue, receipt, descriptor, gateway or host workspace readback. The
Luna/xhigh implementation owner modifies only this declared boundary, does not commit or push,
and cannot change requirements, architecture, contracts, selected modules, model profile, or
control another agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with LPA/LM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes a ledger/stream codec effect, storage-operation implementation, provider or
host use, cost claim, target mutation, integration, push, publication, release, or deployment.

```johnny-status
id = 09
title = Local telemetry-storage lock port
state = OPEN
stage = C | Revision 06 lock-port contract and TDD matrix | READY_LOW_MODEL
stage = M | Luna/xhigh same-lifetime implementation | PENDING
stage = R | Terra/xhigh review and guarded integration | PENDING
```
