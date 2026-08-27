# 07｜Lock-bound storage contracts

| Field | Value |
| --- | --- |
| Artifact ID / kind | TICKET-CONTEXT-TELEMETRY-07-LOCK-BOUND-STORAGE-CONTRACTS / IMPLEMENTATION_TICKET |
| SPEC / acceptance source | SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R Revision 04 / AC-06 through AC-08 and AC-13 through AC-14 |
| Requirement / Context / ADR | PRD-20260827-041 / CHG-20260827-041 / doc/context/context-load-telemetry/main.md Revision 04 / ADR-20260827-022 |
| State / closure | OPEN / READY_LOW_MODEL; CLOSURE-CONTEXT-TELEMETRY-07-LOCK-CONTRACTS, revision 01 |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): selected the Revision 04 lock-bound Accounting path. ADR-20260827-022 authorizes this pure strict-contract closure only. |
| Baseline / dependency | 95811446cb56a777a31c0f37e04b283fa819e42c; Ticket 05 (e509174) is integrated; Ticket 06 is blocked and non-integrable. |
| Control owner / reviewer | ticket-review semantic profile — Terra/xhigh. |
| Implementation owner | implementation-standard semantic profile — Luna/xhigh; one synchronous owner lane and no helpers. |
| Worktree / branch / task | Allocated by the reviewer at same-lifetime synchronous dispatch. No runner, queue, receipt, descriptor, gateway or host workspace readback is required. |
| Delivery / language | POC / STANDARD floor; Python 3.11 with frozen strict Pydantic models and mypy --strict. |
| XSS / effects | XSS_NOT_APPLICABLE. No filesystem, process, lock acquisition, provider, credential, host CLI, task, runner, queue, receipt, network, Git, remote or target-project effect is authorized. |

## Boundary declaration

~~~johnny-boundary
modify = library/local_orchestration/telemetry_storage/contracts.py
modify = library/local_orchestration/telemetry_storage/__init__.py
modify = tests/test_telemetry_storage_contracts.py
create = modules/element/python/context-load-telemetry/07-lock-bound-storage-contracts/
forbid = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
forbid = library/local_orchestration/telemetry_storage/composition.py
forbid = library/local_orchestration/file_lock.py
forbid = library/workflow_router/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
~~~

## Observable closure

One importable, strict, metadata-only lock contract family extends the existing telemetry-storage
boundary. A caller can construct a lock request for a validated opaque storage reference, a fake
port can return either a bound lock token or a finite contention result, and the caller can
validate a finite release result. TelemetryStorageFailure accepts LOCK_CONTENDED but no completed
response can claim it. All malformed identity, decision, field-exclusivity and dynamic extra-field
cases fail at ordinary validation. The closure contains no lock implementation or real
serialization: a Protocol only declares the future dependency seam.

TicketDecompositionDecision = READY_LOW_MODEL. Revision 04 already fixes the observable result,
identity binding, no-effect contention rule, re-admission sequence and adapter prerequisite. This
ticket freezes its strict public DTO/port shapes and test seam only. It does not select a reusable
lock capability, import file_lock.py, create a lock file, open a stream, compose an adapter,
implement retry/timeout/lease ownership, advance a ledger, create a report, or invoke a provider.
A contradiction returns ImplementationReturn.CHANGE_DETECTED.

## Frozen public contracts and dependency direction

Modify only library/local_orchestration/telemetry_storage/contracts.py and its explicit
re-exports in __init__.py. Retain all existing public value types and their grammars. The contract
module may continue to import only OpaqueMetadataId, ProjectId, RevisionDigest, RouterModel,
ContextUsageRecord, NonNegativeCount, Pydantic configuration/validator symbols, and
standard-library enum/typing symbols. Do not add an import from any lock, filesystem, package-root
local-orchestration, host, provider, dispatch or workflow implementation module.

~~~text
TelemetryStorageDecision += LOCK_CONTENDED

TelemetryStorageLockDecision = LOCK_ACQUIRED | LOCK_CONTENDED
                             | RELEASED | RELEASE_FAILED

TelemetryStorageLockRequest = {
  storage_ref: TelemetryStorageRef,
  expected_project_id: ProjectId,
  expected_storage_revision: RevisionDigest
}
TelemetryStorageLockToken = {
  lock_ref: OpaqueMetadataId,
  storage_ref: OpaqueMetadataId,
  project_id: ProjectId,
  stream_id: OpaqueMetadataId,
  ownership_ledger_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest
}
TelemetryStorageLockAcquired = {
  decision: LOCK_ACQUIRED,
  lock_token: TelemetryStorageLockToken
}
TelemetryStorageLockContended = {
  decision: LOCK_CONTENDED,
  storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest,
  failure_ref: OpaqueMetadataId
}
TelemetryStorageLockAcquire = TelemetryStorageLockAcquired
                            | TelemetryStorageLockContended

TelemetryStorageLockReleased = {
  decision: RELEASED,
  lock_ref: OpaqueMetadataId,
  storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest
}
TelemetryStorageLockReleaseFailed = {
  decision: RELEASE_FAILED,
  lock_ref: OpaqueMetadataId,
  storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest,
  failure_ref: OpaqueMetadataId
}
TelemetryStorageLockRelease = TelemetryStorageLockReleased
                            | TelemetryStorageLockReleaseFailed
TelemetryStorageLockPort = {
  try_acquire(request: TelemetryStorageLockRequest) -> TelemetryStorageLockAcquire,
  release(token: TelemetryStorageLockToken) -> TelemetryStorageLockRelease
}
~~~

All owned DTOs inherit the existing frozen strict _StorageModel; all discriminant validators reject
the wrong finite decision. TelemetryStorageLockToken is the only acquire-success identity and
includes all five opaque storage identity coordinates plus revision. Acquire contention exposes
neither a token nor release data; released and release-failed responses expose no token, and only
the failed release has one opaque failure_ref. TelemetryStorageFailure must accept
TelemetryStorageDecision.LOCK_CONTENDED and still reject COMPLETED; it retains its existing
no-success-field shape. As in Ticket 05, request expected project/revision equality with the
embedded reference is not decided in the pure contract layer; the later adapter re-admits it while
holding a real selected lock.

The dependency direction remains:

~~~text
workflow_router value contracts
  <- telemetry_storage.contracts (this ticket's pure lock DTO/Protocol)
  <- future selected lock adapter
  <- future lock-bound storage adapter and composition
~~~

Create modules/element/python/context-load-telemetry/07-lock-bound-storage-contracts/README.md.
It indexes only the exact contract module, focused test, inherited public value types, closure
revision and no-I/O boundary. It does not copy source or claim a lock implementation.

### Reusable-module selection record

~~~text
selected: none
why: this closure creates only pure public DTO and Protocol shapes; it executes no reusable
     locking behavior. MODULE_CATALOG has no delivered cross-process-lock card.
read: library/MODULE_CATALOG.md -> catalog indexes -> no matching card.
deferred: a later real adapter must first catalog and select one READY lock capability. The
          un-catalogued library/local_orchestration/file_lock.py is forbidden here.
~~~

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| LC1 | Ordinary public validators construct one valid request, fully bound token, acquired result, contended result, released result, release-failed result, and TelemetryStorageFailure(LOCK_CONTENDED). A local typed fake TelemetryStorageLockPort round-trips one request and token without I/O. |
| LC2 | Invalid opaque/project/revision grammar, None, wrong primitive, unknown decision, unknown enum, dynamic extra field, missing required field and bypass construction cannot serve as success evidence. |
| LC3 | An acquired result requires exactly a token; contention requires exactly storage identity/revision/failure; released requires no failure; release-failed requires exactly one failure; cross-shape fields are rejected. The token must expose all required exact-identity coordinates. |
| LC4 | TelemetryStorageFailure accepts exactly the new finite LOCK_CONTENDED failure decision and retains its failure shape; a completed response or lock success/release decision cannot be constructed as a storage failure. |
| LC5 | The bounded AST/source gate extends Ticket 05's exact import/call/decorator allowlists for the altered public shapes. It rejects Any, object, cast, dynamic lookup, bypass constructors, package-root imports, every plain import, all filesystem/process/network/provider/dispatch/host imports and callable effect entry. |
| LC6 | Focused tests, strict typecheck, compile validation, declared-boundary diff and no cache/runtime residue pass. New contract code records no claim that a real lock was acquired, released or contended. |
| LM1 | Remove LOCK_CONTENDED from the finite storage-failure set; LC4 turns red, then byte-exact restoration returns green. |
| LM2 | Remove one token identity coordinate or permit a wrong decision/field combination; LC2 or LC3 turns red, then restoration returns green. |
| LM3 | Add one forbidden I/O/host import, Any, dynamic lookup or deferred import/call to the owned contract module; LC5 turns red, then restoration returns green. |
| LM4 | Widen the TelemetryStorageLockPort fake/Protocol with an adapter effect or allow a package-root local-orchestration import; LC5/LC6 turns red, then restoration returns green. |

Strong-type preflight runs before implementation and before review. It builds every listed public
success shape through its ordinary constructor; negative evidence covers nullability, primitive,
grammar, enum, strict-extra and union-shape rejection. model_construct, model_copy, casts, Any,
dynamic lookup and historical-object reuse are negative-only evidence. Missing preflight is
HALT / TICKET_SCHEMA_INVALID.

## Verification and review

Implementation-owner focused commands:

~~~text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_contracts.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/__init__.py library/local_orchestration/telemetry_storage/contracts.py tests/test_telemetry_storage_contracts.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/__init__.py library/local_orchestration/telemetry_storage/contracts.py
git diff --check 95811446cb56a777a31c0f37e04b283fa819e42c HEAD
~~~

The Terra/xhigh reviewer reruns focused checks and the strong-type preflight, validates the exact
ticket blob and baseline, verifies the four-path boundary and no-effect AST gate, replays LM1–LM4
with byte-exact restoration, and independently counter-mutates one different lock-result field.
No real locking claim is admissible evidence. Full-suite and residue checks are the reviewer's
responsibility before integration.

## Ownership and return

This closure is same-lifetime synchronous: the reviewer dispatches, waits, receives the return,
reviews and integrates. It requires no runner, queue, receipt, descriptor, gateway or host
workspace readback. The implementation owner receives an identifier-only dispatch envelope,
modifies only this declared boundary, does not commit or push, and cannot control another agent,
select a lock capability or perform a runtime effect.

Return exactly ImplementationReturn.COMPLETED -> ACTION_COMPLETED with named TDD/type/mutation
evidence; BLOCKED -> HALT with the failed cell; or CHANGE_DETECTED -> REQUIREMENT_CHANGED.
No return authorizes a real adapter, storage change, target mutation, host delivery, merge, push,
release or deployment.

~~~johnny-status
id = 07
title = Lock-bound telemetry storage contracts
state = OPEN
stage = C | strict lock DTO and Protocol contract | OPEN
stage = M | reverse-mutation proof | PENDING
stage = R | Terra/xhigh review | PENDING
~~~
