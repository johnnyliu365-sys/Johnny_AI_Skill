# 12｜Lock-bound telemetry transaction adapter

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-12-LOCK-BOUND-TRANSACTION-ADAPTER` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 09 / AC-13, AC-14, AC-16–AC-20 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 09 / `ADR-20260827-022`, `025`–`027` |
| State / closure | `CLOSED / DONE / APPROVED / INTEGRATED`; `CLOSURE-CONTEXT-TELEMETRY-12-LOCK-BOUND-TRANSACTION-ADAPTER`, revision 02 |
| Document revision | `02` |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): Revision 07 authorizes the durable controlled storage boundary. Revisions 08–09 / ADR `026`–`027` close its private ledger and transaction protocol; no new owner product decision or public contract is introduced. |
| Source baseline / dependency | `589b85bad484a2bced18d035ac716ebde0e4bc2d`; candidate must descend from committed ticket authority. Ticket 09 (`096d471`) supplies exact locking; Ticket 11 (`e05f03a`) supplies corrected private per-stream ledger/CAS. Ticket 06 remains `SUPERSEDED` and non-integrable. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; one synchronous owner lane and no helper. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-12-lock-bound-transaction-adapter` on `implement/context-load-telemetry-12-lock-bound-transaction-adapter` from committed `main` that descends from the source baseline, then binds its exact ticket revision and baseline. This same-lifetime lane needs no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11, full annotations, strict finite DTOs, `mypy --strict`, forced-interruption/restart/TOCTOU/release evidence and full review. The public contract and private protocol are closed, so Luna/xhigh implementation plus Terra/xhigh review is the appropriate initial assignment. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Only disposable test roots may receive owned stream/journal/ledger effects. No provider, credential, host CLI, target-project, Git, network, runner, queue, receipt, publication, release or deployment effect is authorized. |

## Boundary declaration

```johnny-boundary
create = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
modify = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
create = tests/test_johnny_owned_telemetry_storage_adapter.py
modify = tests/test_johnny_owned_telemetry_storage_adapter.py
create = modules/element/python/context-load-telemetry/12-lock-bound-transaction-adapter/
modify = modules/element/python/context-load-telemetry/12-lock-bound-transaction-adapter/
forbid = library/local_orchestration/telemetry_storage/__init__.py
forbid = library/local_orchestration/telemetry_storage/contracts.py
forbid = library/local_orchestration/telemetry_storage/ownership_ledger.py
forbid = library/local_orchestration/telemetry_storage/local_lock_adapter.py
forbid = library/local_orchestration/telemetry_storage/composition.py
forbid = library/local_orchestration/johnny_root_layout.py
forbid = library/local_orchestration/path_containment.py
forbid = library/local_orchestration/file_lock.py
forbid = library/workflow_router/telemetry.py
forbid = library/workflow_router/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create the direct private `JohnnyOwnedTelemetryStorageAdapter`, an implementation of the existing
`TelemetryStoragePort`. It receives an injected `JohnnyRootLayout`, private
`TelemetryOwnershipLedgerPort`, and existing `TelemetryStorageLockPort`. It is not re-exported or
bound into composition. The only controlled source direction is:

```text
contracts <- johnny_owned_adapter <- composition
```

For every request it performs preliminary exact ownership admission, acquires the exact lock,
recovers the pending transaction using `resolve_current`, then performs fresh exact
project/revision/lifecycle/containment admission before any codec effect. `LOCK_CONTENDED`
returns the existing finite failure with no ledger/stream/journal/report effect. Any lock,
ledger, journal, containment, codec, filesystem, unexpected response or release failure is
sanitized `STORAGE_BOUNDARY_VIOLATION`; release failure overrides an otherwise complete result.

Only this direct module may import and call `JsonlContextUsageStore.read`; it must never import or
call `JsonlContextUsageStore.append`. It strictly decodes existing metadata-only records and
writes canonical JSONL itself. It must not expose a stream, journal, snapshot, root or exception
path in any public response/failure ref.

The private transaction directory is exactly:

```text
telemetry_root/storage-transactions/<sha256(exact immutable identity)>/
  journal.json
  pre.stream
  post.stream
```

The strict internal journal has schema version `1`, opaque identity/ref, operation, expected and
next revisions, pre/post lifecycle, internal relative stream locator, pre/post existence,
SHA-256, record count and phase `PREPARED | STREAM_APPLIED | LEDGER_APPLIED`. All paths are
derived and containment-checked; journal/snapshots use same-directory temporary write,
flush/fsync and owned replacement. Fixed names are implementation constants, never caller input.

For `APPEND`, a missing owned stream is an empty pre-state; canonical post bytes append exactly
one record and lifecycle stays `ACTIVE`. `DETACH`/`UNINSTALL` decode the pre-stream for removed
count, use absent post-stream state, and CAS the matching `DETACHED`/`REMOVED` tombstone. `READ`
returns all strictly decoded records in ledger order at unchanged expected revision. `VALIDATE`
uses `ContextUsageValidator().validate(records=records)` with its fixed default and returns
`validation-<sha256(identity + current revision + canonical report JSON)>`; no report file is
created. Journal recovery accepts only this grid:

| Phase | Stream / ledger observation | Required recovery |
| --- | --- | --- |
| `PREPARED` | pre / pre | discard journal; retain pre-state |
| `PREPARED` | post / pre | restore exact pre snapshot; discard |
| `STREAM_APPLIED` | post / pre | restore exact pre snapshot; discard |
| `STREAM_APPLIED` | post / post | retain post-state; discard (CAS completed before phase update) |
| `LEDGER_APPLIED` | post / post | retain post-state; discard |
| any | malformed, third, missing-required or incompatible state | retain journal; `STORAGE_BOUNDARY_VIOLATION`; never guess repair |

Deterministic post revision is exactly:

```text
rev-<sha256("telemetry-storage-revision-v1" + NUL + storage_ref + NUL + project_id + NUL +
            stream_id + NUL + ownership_ledger_ref + NUL + expected_revision + NUL + operation +
            NUL + post_lifecycle + NUL + sha256(stream_locator) + NUL + pre_sha256 + NUL +
            post_sha256)>
```

## Frozen implementation rules

Do not modify a public contract, package export, ledger, lock adapter, legacy codec, composition
or provider/host layer. Preserve public response constructors exactly. A request must never
provision/register/repair/discover an entry, migrate the aggregate ledger, touch an unrelated
stream/entry/report, retry/sleep/poll, or translate a non-contention failure into
`LOCK_CONTENDED`.

Journal recovery is deliberately before final exact admission: recovery lookup ignores only the
candidate revision, then final normal ledger resolution checks it. It may not treat malformed or
incompatible state as a cue to invent post-state. A failed restoration/cleanup retains the journal
and returns only the finite boundary result. Tests may patch bounded real adapter seams to force
phases; no test-only production provision API or global singleton is permitted.

Create `modules/element/python/context-load-telemetry/12-lock-bound-transaction-adapter/README.md`
as the target-owned index to this ticket, exact adapter/test sources, contracts, Tickets 09/11,
`path-containment@cf9e126`, `exclusive-file-lock@60d2ab0` and ADR `027`. It copies no source and
claims neither composition nor target/provider/release behavior.

### Reusable-module selection record

```text
selected: exclusive-file-lock@60d2ab0 through the delivered local lock port;
          path-containment@cf9e126 for every internal ledger/stream/journal path.
why: finite exact cross-process exclusion and containment before an owned filesystem effect.
read: each card -> public contract -> named behavior evidence; Ticket 09 is the local adapter.
rejected: JsonlContextUsageStore.append; aggregate-ledger migration; Ticket 06 candidate;
          provider/host/runner paths.
gap: transaction journal and controlled canonical writer are target-owned private infrastructure.
boundary: no composition, provisioning, target, provider, publication, release or deployment.
```

## High-assurance adversarial matrix

| Risk | Required ticket evidence | Excluded follow-on concern |
| --- | --- | --- |
| Stream/ledger mixed state after interruption | TTA3/TTA4/TTM1 force every journal phase and restart; next operation sees exact pre or post only. | Composition lifetime. |
| Caller bypasses fresh under-lock admission | TTA2/TTM2 mutate ledger between preliminary and final admission; no codec effect occurs. | Provisioning workflow. |
| Incorrect state/collision makes a false success | TTA4/TTM3 reject malformed or third journal state and retain it. | Migration tooling. |
| Codec or path exposes uncontrolled effect | TTA1/TTA5/TTM4 prove sole read, no legacy append, record rejection, containment and target isolation. | Provider observation. |
| Auxiliary release hides a completed response | TTA6/TTM5 force release failure after success and require boundary failure. | Lock primitive implementation. |

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| TTA1 | With a test-seeded active owned entry, `APPEND` canonicalizes one record, advances to the exact deterministic revision and returns `CompletedAppendResponse`; `READ` returns the full immutable tuple/count at unchanged expected revision. No public response contains a path. |
| TTA2 | Missing/mismatched/closed/stale entry and an injected under-lock TOCTOU ledger change return exactly `STORAGE_OWNERSHIP_MISMATCH` or `STORAGE_CLOSED`, before codec/journal/stream effect. Real independent same-identity holder returns `LOCK_CONTENDED` with zero effect. |
| TTA3 | `VALIDATE` returns deterministic opaque report ref without a report file; invalid decoded record is `RECORD_INVALID`. `DETACH` and `UNINSTALL` separately return matching tombstone lifecycle/revision and removed count while leaving unrelated seeded streams unchanged. |
| TTA4 | Force interruption/failure before journal, after `PREPARED`, after stream application, after ledger CAS and after `LEDGER_APPLIED`; restart a fresh adapter. Every admitted next `READ`/`VALIDATE` observes only byte-identical complete pre or post state. |
| TTA5 | Malformed journal/snapshot, incompatible phase/state, redirected root/stream/journal ancestor, aggregate ledger, codec I/O and failed restore/cleanup return `STORAGE_BOUNDARY_VIOLATION`, retain unsafe journal where required, and reveal no path/exception/raw record. Disposable target sentinel and Git status stay unchanged. |
| TTA6 | Source/AST gates prove only `johnny_owned_adapter.py` calls `JsonlContextUsageStore.read`, no controlled source calls its `append`, all five public response shapes are constructed through normal contracts, no public export/composition/provision/migration, no `Any`/cast/dynamic map/retry/sleep/poll, and release failure overrides an otherwise successful response. |
| TTA7 | Focused tests, storage contracts, strict type, compilation and diff checks pass. Fixture seeding, forced failure and process helpers are test-local only. |
| TTM1 | Reverse-mutate recovery to accept a mixed stream/ledger state; TTA4 turns red, then byte-exact restoration returns green. |
| TTM2 | Reverse-mutate final normal admission away after lock/recovery; TTA2 turns red, then restoration returns green. |
| TTM3 | Reverse-mutate deterministic revision input or validation-report input; TTA1/TTA3 turns red, then restoration returns green. |
| TTM4 | Reverse-mutate the controlled writer to call legacy `append` or bypass containment; TTA5/TTA6 turns red, then restoration returns green. |
| TTM5 | Reverse-mutate release-failure override into completed response; TTA6 turns red, then restoration returns green. |

Strong-type preflight constructs every existing public request/success/failure DTO and internal
journal value via ordinary strict constructors. No caller path, raw mapping, cast, dynamic member
lookup or bypass constructor is success evidence. The reverse-mutation cells are mandatory; this
new adapter has no ceremonial baseline-red claim.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_johnny_owned_telemetry_storage_adapter.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_ownership_ledger.py tests/test_telemetry_storage_lock_adapter.py tests/test_telemetry_storage_contracts.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/johnny_owned_adapter.py tests/test_johnny_owned_telemetry_storage_adapter.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
git diff --check 589b85bad484a2bced18d035ac716ebde0e4bc2d HEAD
git status --short
```

The Terra/xhigh reviewer validates ticket blob/baseline/boundary/protocol, reruns every focused,
strict and compilation gate, independently reverse-mutates a production recovery or release path
that the implementer did not choose, verifies all five finite operation matrices and compares any
full-suite failure against clean main with untruncated traceback. The reviewer also proves the
candidate is source-direction-only and that no target or Git sentinel changes occurred.

Return exactly one `ImplementationReturn`: `COMPLETED` with command/evidence references,
`BLOCKED` with the named blocker and zero scope expansion, or `CHANGE_DETECTED` for a
contradiction in committed authority. The implementation owner does not commit, push, call the
document gate, edit ticket/docs, create another worktree or delegate. The reviewer alone reviews,
commits, admits document mutation, pushes and reads back the authority ref.

## Completion record

Luna/xhigh returned `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with no commit, push,
document-gate call, ticket/document edit or scope expansion. Terra/xhigh independently reviewed
the two declared candidate paths, source direction and response construction; reran the focused,
storage-contract, strict-type and compilation gates; and verified all five operation/recovery
matrices.

The independent reviewer counter-mutation changed the real `STREAM_APPLIED` recovery condition
from `ledger_pre` to `ledger_post`. The forced `AFTER_LEDGER_CAS` restart then retained one
pre-state record where TTA4 requires the two-record post-state; restoring the exact production
condition returned TTA4 to green. This is reviewer evidence distinct from the implementation
owner's recorded mutation set.

The reviewer committed candidate `c359d92efc6eb2ca4aeb5c613f4fe7c976cd6e74` on
`implement/context-load-telemetry-12-lock-bound-transaction-adapter`. It descends from committed
Ticket 12 authority `4d747f6253c6d2741af980f3b9ff82c68df8fedb` and changes only
`johnny_owned_adapter.py` and its direct test. `admit_document_mutation` read the ticket boundary
from `main`, read the candidate change set from Git, and returned `INTEGRATED` with that exact
candidate SHA. The source integration was non-force pushed to `origin/main`; fresh direct remote
readback returned `c359d92efc6eb2ca4aeb5c613f4fe7c976cd6e74`.

The exact source review is
`doc/reviews/context-load-telemetry/12-lock-bound-transaction-adapter-code-review.md`. Its full
suite result records only the three failures reproduced against clean main; no global-green claim
is made. This closure does not bind the private adapter into composition or widen its public
surface.
