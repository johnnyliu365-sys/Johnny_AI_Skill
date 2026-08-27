# Context Load Telemetry POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| State | `APPROVED_BASELINE / REVISION_02_PROJECT_ISOLATION_APPROVED / REVISION_03_PROVIDER_USAGE_ARCHITECTURE_ACCEPTED / REVISION_04_LOCKED_STORAGE_APPROVED / REVISION_05_CLASSIFIED_FILE_LOCK_CAPABILITY_APPROVED / REVISION_06_LOCK_PORT_ADAPTER_AUTHORIZED / REVIEWER_DECOMPOSITION_AUTHORIZED` |
| Owner | `root/main` |
| Context | `doc/context/context-load-telemetry/main.md` |
| PRD reference | `PRD-20260803-006` |
| Change | `CHG-20260803-006`; project-isolation revision `CHG-20260815-024` / `ADR-20260815-013`; provider-usage architecture `ADR-20260824-019`; lock-bound storage `CHG-20260827-041` / `ADR-20260827-022`; classified lock capability `ADR-20260827-024` |

## Goal

Produce local, shareable evidence that a Router-selected ContextPacket reduces actual Agent input context compared with a matched baseline, without exporting source text, prompts, or secrets.

## Scope

- Strongly typed Pydantic telemetry records for router and baseline runs.
- Deterministic packet-token estimate for budget observation, clearly distinct from provider-reported usage.
- Metadata-only JSONL append/read support through an opaque
  `TelemetryStorageRef` resolved only beneath the per-user Johnny root.
- Fail-closed validation of router guards and matched baseline/router pairs.
- Aggregate median reduction only where both records supply provider-reported input-token counts.
- A provider-neutral terminal-usage evidence port and a separately authorized host capability
  probe; no unverified CLI/UI output is provider usage evidence.
- Unit tests and usage documentation.

## Non-goals

- Do not capture raw ContextPacket text, prompts, source URIs, provider credentials, source files, or company code.
- Do not make a production Agent supervisor, enforce all Agent tool I/O, install a service, or write raw telemetry into a target repository either automatically or through a caller-supplied path.
- Do not substitute an estimated token count for actual provider input usage when claiming reduction.
- Do not report a cost, currency, price, subscription allowance, or inferred saving. This
  revision measures actual provider token counts only.

## Data contract

Each `ContextUsageRecord` contains a run ID, comparison group and attempt, snapshot ID, mode, typed Router metadata, source fingerprints/revisions/spans, budget and estimated packet tokens, optional provider usage, quality outcome, and guard results. `SourceSnippet.text` is structurally absent from the record and all JSONL output.

A comparison pair is valid only when its baseline and router records share `(comparison_group_id, attempt, project_snapshot_id, provider, model)`. Any missing counterpart, provider input count, budget breach, undeclared source, or router quality regression is a validation failure.

### Revision 02 storage boundary

Production callers supply a validated opaque `TelemetryStorageRef`, never a raw
filesystem path. An injected Johnny-owned storage adapter resolves that identity
below the per-user Johnny root using the ownership ledger. The durable record,
CLI arguments, reports and errors contain no target path. Project detach removes
only that project's owned stream/mapping; plugin uninstall removes all
ledger-owned telemetry. Neither operation changes the target repository.

The existing `JsonlContextUsageStore.append(path=...)` interface remains legacy
POC code and is not admitted for controlled-target use. Until a reviewer-owned
ticket replaces or hardens it, it may be used only with disposable test fixtures
or paths internal to Johnny's own development repository. A validated aggregate
report needed as durable project review evidence may be exported only through a
separately authorized action into the project's normal evidence tree; raw JSONL
is never a project artifact.

### Revision 02 typed contracts

```text
TelemetryStorageLifecycle = ACTIVE | DETACHED | REMOVED
TelemetryStorageOperation = APPEND | READ | VALIDATE | DETACH | UNINSTALL
TelemetryStorageDecision = COMPLETED | STORAGE_REF_INVALID
                         | STORAGE_OWNERSHIP_MISMATCH | STORAGE_CLOSED
                         | STORAGE_BOUNDARY_VIOLATION | LOCK_CONTENDED
                         | RECORD_INVALID

TelemetryStorageRef = {
  storage_ref, project_id, stream_id,
  ownership_ledger_ref, storage_revision, lifecycle
}

AppendTelemetryStorageRequest = {
  storage_ref, expected_project_id, expected_storage_revision,
  operation=APPEND, record: ContextUsageRecord
}

NoRecordTelemetryStorageRequest = {
  storage_ref, expected_project_id, expected_storage_revision,
  operation=READ | VALIDATE | DETACH | UNINSTALL
}

TelemetryStorageRequest = AppendTelemetryStorageRequest
                      | NoRecordTelemetryStorageRequest

TelemetryStorageReadPayload = {
  records: tuple[ContextUsageRecord, ...]
}

CompletedAppendResponse = {
  storage_ref, storage_revision, operation=APPEND, decision=COMPLETED,
  lifecycle=ACTIVE, record_count
}
CompletedReadResponse = {
  storage_ref, storage_revision, operation=READ, decision=COMPLETED,
  lifecycle=ACTIVE, record_count, read_payload: TelemetryStorageReadPayload
}
CompletedValidateResponse = {
  storage_ref, storage_revision, operation=VALIDATE, decision=COMPLETED,
  lifecycle=ACTIVE, record_count, validation_report_ref
}
CompletedDetachResponse = {
  storage_ref, storage_revision, operation=DETACH, decision=COMPLETED,
  lifecycle=DETACHED, record_count
}
CompletedUninstallResponse = {
  storage_ref, storage_revision, operation=UNINSTALL, decision=COMPLETED,
  lifecycle=REMOVED, record_count
}
TelemetryStorageFailure = {
  storage_ref, storage_revision, operation,
  decision=STORAGE_REF_INVALID | STORAGE_OWNERSHIP_MISMATCH | STORAGE_CLOSED
         | STORAGE_BOUNDARY_VIOLATION | RECORD_INVALID,
  failure_ref
}

TelemetryStorageResponse = CompletedAppendResponse | CompletedReadResponse
                         | CompletedValidateResponse | CompletedDetachResponse
                         | CompletedUninstallResponse | TelemetryStorageFailure

TelemetryStoragePort.execute(request: TelemetryStorageRequest) -> TelemetryStorageResponse
```

### Revision 04 lock-bound storage admission

Every storage operation is serialized by an injected lock port over the exact opaque
`(storage_ref, project_id, stream_id, ownership_ledger_ref)` identity. The storage adapter has
one mandatory sequence: strict request admission, preliminary ownership/lifecycle candidate
lookup, exclusive lock attempt, then a complete second ownership/revision/lifecycle/containment
admission while holding the lock. Only then may it invoke the legacy JSONL codec or mutate a
ledger lifecycle. A failed second admission releases the lock and performs no stream effect.

The future contract has only metadata-only shapes:

```text
TelemetryStorageLockRequest = {
  storage_ref, expected_project_id, expected_storage_revision
}
TelemetryStorageLockToken = {
  lock_ref, storage_ref, project_id, stream_id,
  ownership_ledger_ref, storage_revision
}
TelemetryStorageLockAcquire = LOCK_ACQUIRED(token) | LOCK_CONTENDED
TelemetryStorageLockRelease = RELEASED | RELEASE_FAILED
TelemetryStorageLockPort = {
  try_acquire(request) -> TelemetryStorageLockAcquire,
  release(token) -> TelemetryStorageLockRelease
}
```

`LOCK_CONTENDED` becomes the same-named `TelemetryStorageFailure` decision with an opaque
failure reference. It is returned before any codec read/write/delete, validation report, ledger
advance, target effect, provider effect, retry or fabricated success. Lock tokens and outcomes
have no raw path or diagnostics. A release failure prevents a completed claim and returns the
existing `STORAGE_BOUNDARY_VIOLATION` finite failure; a later real lock-adapter ticket must prove
both acquisition and release by independent counter-mutation.

The existing `library/local_orchestration/file_lock.py` has no delivered MODULE_CATALOG card, so
Revision 04 does not import, copy or name it as a dependency. Before a production lock adapter is
implemented, its capability must be catalogued and selected by the reusable-module process, or a
new catalogued capability must be approved. Ticket 06's pre-Revision-04 candidate is preserved
as uncommitted review evidence and is non-integrable.

### Revision 05 classified nonblocking file-lock prerequisite

The owner authorizes one reusable-capability closure before any telemetry lock adapter. It
preserves the blocking public behavior of `ExclusiveFileLock` and
`ExclusiveWindowsFileLock`, including all six current consumers, and adds only this separate
public surface:

```text
FileLockAcquireDecision = ACQUIRED | CONTENDED

ExclusiveFileLock.try_acquire() -> FileLockAcquireDecision
ExclusiveFileLock.release() -> None
```

`try_acquire` is valid only for an idle lock object. `ACQUIRED` means this instance owns the one
opened handle until its matching `release()`; `CONTENDED` means it owns no handle and created no
guarded-state effect. Repeated acquire, release without a successful acquire, and use after a
failed release are programming-state errors, not a third success-like decision. The established
`with ExclusiveFileLock(path):` path remains blocking and semantically unchanged.

The platform is still bound once at import. On Windows the nonblocking binding uses
`msvcrt.LK_NBLCK`. A real independent-holder probe on this Windows host observed the exact
contention signal `OSError(errno=EACCES)`, no `winerror`, and zero-millisecond elapsed time after
the instance opened its own handle. Only that signal from this owned `LK_NBLCK` call becomes
`CONTENDED`; every other `OSError` from opening, acquiring, releasing, or filesystem handling
propagates unchanged. On POSIX the source branch must request `fcntl.LOCK_EX | fcntl.LOCK_NB` and
may classify only `EACCES` or `EAGAIN`; its runtime behavior remains unproven on this Windows
host and must be recorded as such.

There is no timeout, retry, polling loop, background worker, process fallback, telemetry import,
lock token, storage/ledger effect, host/provider call, cost claim, target-project mutation, or
release in this capability closure. The later telemetry adapter alone maps a selected capability's
finite `CONTENDED` result to its metadata-only `LOCK_CONTENDED` response.

### Revision 06 local lock-port adapter

The owner authorizes one local implementation of the existing `TelemetryStorageLockPort` after
the selected `exclusive-file-lock` and `path-containment` cards are delivered. It receives only a
strict `TelemetryStorageLockRequest`; it derives no public path and exposes none. Its one
dedicated lock-file identity is the SHA-256 digest of the complete immutable
`(storage_ref, project_id, stream_id, ownership_ledger_ref, storage_revision)` tuple, encoded
with fixed labels and NUL separators. The adapter constructs the opaque `lock_ref` and all opaque
failure references from that digest, not from a caller-supplied string.

The adapter's sole owned effect is to create and retain a dedicated `*.lock` file below an
internally derived `JohnnyRootLayout.telemetry_root` child. Before directory creation or file
open, the exact candidate and its root must pass the selected containment predicate; a redirected
base or ancestor raises a sanitized adapter failure and leaves no outside effect. An independent
holder of the same derived location returns the existing `TelemetryStorageLockContended` result;
it owns no handle and receives no token. No retry, timeout, queue, runner or polling is allowed.

On acquisition, one adapter instance retains the real `ExclusiveFileLock` and the exact original
`TelemetryStorageLockToken` object. `release()` succeeds only for that still-held original
object; copied, forged, stale, cross-adapter or mismatched tokens return the existing finite
`TelemetryStorageLockReleaseFailed` result without unlocking anything. Release always clears the
retained state in a bounded `finally` path. A non-contention acquisition I/O failure stays a
sanitized adapter error; a release I/O failure becomes the finite release-failed DTO. Neither
failure contains a filesystem path, exception text, prompt, source text, credential or provider
data.

This adapter deliberately does not decide expected-project/revision equality, read a ledger or
stream, call `JsonlContextUsageStore`, advance a lifecycle/revision, convert lock results to
`TelemetryStorageResponse`, or perform the under-lock storage re-admission. Those remain the
next lock-bound storage-adapter closure. The adapter itself is one independently observable
`READY_LOW_MODEL` outcome: real same-location cross-process acquisition is classified as exactly
`LOCK_ACQUIRED` or `LOCK_CONTENDED`, then an acquired original token can be released.

Every identifier is a validated named type with a finite pattern. `record` is
present only for `APPEND`; other operation/payload combinations fail before I/O.
No production request or result has a filesystem-path field. Boundary adapters
validate dynamic JSON and filesystem/Git/provider output before constructing
these contracts; `Any`, implicit `any`, unvalidated mappings and stringly typed
lifecycle/decision values cannot enter the core.

### Revision 03 provider-usage evidence and comparison boundary

The `ADR-20260824-019` architecture closes the previously missing storage-operation matrix and
adds a provider-neutral boundary. A future `ProviderUsageEvidencePort` consumes only an
ephemeral terminal host event and returns one finite result:

```text
ProviderUsageEvidenceDecision = OBSERVED | HOST_USAGE_UNAVAILABLE
                              | HOST_USAGE_MALFORMED | HOST_USAGE_MISMATCH

ProviderUsageObservation = {
  host_run_fingerprint, provider, model,
  host_configuration_fingerprint, project_snapshot_id,
  provider_input_tokens, provider_output_tokens?, cached_input_tokens?
}
```

`provider_input_tokens` is mandatory only for `OBSERVED`; absent or non-finite usage is never
coerced to zero. The raw terminal event is validated at the adapter boundary then discarded. No
result carries prompt/response text, URI, raw host event, credential or a filesystem path.
Adapters first admit fake event fixtures only. A real host command is a separately authorized
provider effect and is not implied by this specification approval.

Usage reports have a finite class:

```text
UsageReportClass = LOAD_ESTIMATE | OBSERVED_USAGE | MATCHED_REDUCTION
```

Only `MATCHED_REDUCTION` may state a token reduction. It requires two fresh isolated records with
identical comparison group, attempt, project snapshot, provider, exact model, host-configuration
fingerprint, cache mode and frozen task contract, with randomized execution order and passing
quality gates. Resume, shared conversation, handoff, missing usage, mismatch or quality
regression rejects the pair. `OBSERVED_USAGE` may report one run's actual counts but never a
saving; `LOAD_ESTIMATE` remains explicitly estimated.

Revision 02's storage operation matrix is now fixed: `APPEND`, `READ`, `VALIDATE`, `DETACH` and
`UNINSTALL` require `ACTIVE`; only `APPEND` carries a record. The five validation precedence
classes and each operation's successful result are defined in `ADR-20260824-019`. `DETACHED` and
`REMOVED` reject every operation as `STORAGE_CLOSED`. The composition root alone resolves the
opaque ref through the ownership ledger and is the sole caller of the legacy path-taking codec.

The response fields above have this exact matrix. `storage_revision` is always present: it is the
new ledger revision after successful `APPEND`/`DETACH`/`UNINSTALL`, the expected revision after
successful `READ`/`VALIDATE`, and only the request's expected revision after a failure. Every
successful result has `lifecycle` and `record_count`; `APPEND` reports the post-append count,
`READ` the snapshot count, `VALIDATE` the validated count, and `DETACH`/`UNINSTALL` the removed
count. `validation_report_ref` is present only for successful `VALIDATE`; `failure_ref` is absent
on every success and required on every failure as an opaque finite-decision fingerprint. A failed
result has no `lifecycle`, `record_count` or `validation_report_ref`. These presence rules are
part of the strict constructor/preflight matrix, not renderer convention.

`READ` has no caller-selected query, filter, page or path. Its successful payload is the complete
immutable tuple of validated metadata-only `ContextUsageRecord` values in ledger append order, and
its `record_count` must equal its tuple length. The composition root supplies the only
`TelemetryStoragePort`; callers cannot instantiate its adapter. The future source direction is
`contracts <- johnny_owned_adapter <- composition`, while product callers depend only on
`contracts`. Only `johnny_owned_adapter` may import the legacy raw-path
`JsonlContextUsageStore`; `telemetry.py` is value types only and the legacy path-taking CLI is
unreachable from any controlled-target composition root.

## Acceptance criteria

1. JSONL output has one strict schema-validated record per line and never contains a supplied unique raw source string.
2. Router records expose only source fingerprint, kind, identifier, revision, span, and estimated size; ContextView raw-text separation remains intact.
3. Validator rejects invalid router guard states and incomplete/non-comparable pairs.
4. Validator reports median provider-input-token reduction and quality result for valid pairs.
5. All Router and project test/type gates pass.
6. Storage tests reject raw target paths, path escape, reparse/symlink,
   cross-project storage refs, unknown/revoked ownership and cleanup outside the
   exact ledger entry before filesystem effect.
7. A controlled target's bytes and Git status remain unchanged while telemetry
   is appended, read, validated, detached and uninstalled.
8. Contract matrices reject every operation/payload/lifecycle mismatch,
   malformed or cross-project reference, missing revision, dynamic extra field,
   raw path field and invalid finite value under Pydantic strict validation and
   `mypy --strict`.
9. Provider-usage adapters reject a missing, malformed, mismatched, replayed or extra-field
   terminal event before a telemetry record is appended; the discarded raw event cannot appear in
   state, JSONL, report or error output.
10. `OBSERVED_USAGE` cannot serialize or render a reduction claim; only a valid,
    quality-preserving `MATCHED_REDUCTION` pair can report actual provider input-token reduction.
11. A host capability probe has one ticket-bound, owner-authorized external-effect attempt. A
    missing/changed host schema returns a named unavailable/malformed result and creates no claim.
12. Pair experiments use fresh isolated sessions and preserve target-project bytes/Git state;
    they never reuse a conversation or read the paired run's content.
13. A contended lock returns `LOCK_CONTENDED` before every stream/ledger/report effect. A
    holder release is required on every terminal path, and a release failure cannot serialize a
    completed lifecycle result.
14. A competing-process fixture proves that only the lock holder can advance a lifecycle or
    change owned stream bytes; malformed/revoked/stale input is re-admitted under lock before
    any codec operation.
15. Before an adapter is opened, the reusable file-lock primitive proves a finite immediate
    `ACQUIRED`/`CONTENDED` result against a real independent holder, preserves every existing
    blocking consumer, and propagates non-contention I/O errors rather than relabeling them.

## Approval

The project owner explicitly authorized the baseline implementation on
`2026-08-03` for personal local-project validation and approved the exact
Revision 02 project-isolation correction on `2026-08-15` under
`CHG-20260815-024`. The reviewer may decompose/open tickets for this exact
closure. Approval creates no dispatch receipt and grants no source,
target-project, telemetry-write, cleanup or external-effect authority. The
legacy raw-path POC remains prohibited for controlled-target use until the
approved tickets are implemented, independently reviewed and integrated.

The project owner additionally authorized Revision 03's provider-usage architecture on
`2026-08-24`. It authorizes reviewer decomposition and pure no-effect tickets only; it grants no
provider invocation, credential access, host configuration, telemetry write, cleanup or external
effect authority.

The project owner selected the Revision 04 lock-bound storage requirement on `2026-08-27` under
`PRD-20260827-041` / `CHG-20260827-041`. It authorizes architecture revision and pure
strict-contract decomposition only. It does not authorize a real lock implementation, real
telemetry storage, host/provider invocation, cost claim, target-project mutation or external
effect.

The project owner additionally authorized the Revision 05 classified nonblocking file-lock
capability on `2026-08-27`. It authorizes the isolated primitive and disposable process-fixture
closure described above, but not a telemetry adapter, telemetry stream/ledger effect,
provider/host invocation, cost claim, target-project mutation, publication, release, or
deployment.

The project owner additionally authorized Revision 06's one local lock-port adapter on
`2026-08-27`. It authorizes the strict `TelemetryStorageLockPort` implementation and disposable
root/process evidence defined above, plus only its dedicated Johnny-root lock-file effect. It
does not authorize telemetry stream/ledger work, the legacy codec, a storage operation adapter,
provider/host invocation, cost claim, target-project mutation, publication, release, or
deployment.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `72438a30a4ad698be33292de8d63a7f2dc289daf` | Drafted Revision 02 to replace caller-selected target-local telemetry paths with a Johnny-owned opaque storage reference; owner approval pending. |
| 2026-08-15 | Project owner | Approved the exact Telemetry Storage Revision 02 and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-24 | Project owner / `main` / `1849515f911d1376d800fe1b19e0e07b5227028b` | Accepted Revision 03 provider-usage evidence architecture: typed storage matrix, provider-neutral terminal evidence, observed-versus-matched reporting, and isolated authorized probes. |
| 2026-08-27 | Project owner / `main` / `39f5d883622572f10323527ce32c9eecaaafd5d0` | Selected Revision 04: telemetry storage must be lock-bound; contention is a named no-effect result and the un-catalogued lock module is not implicitly reusable. |
| 2026-08-27 | Project owner / `main` / `6b5a7c163aa6c2eb2834956f9486072d0047d988` | Authorized Revision 05: preserve the blocking reusable lock API while adding a separately classified nonblocking primitive; all unrelated I/O errors remain errors. |
| 2026-08-27 | Project owner / `main` / `42b2be1b0659c3e1cb9f8e039d1b827f7b74be85` | Authorized Revision 06: implement one separately scoped local `TelemetryStorageLockPort` with selected lock/containment capabilities and no storage-operation effect. |
