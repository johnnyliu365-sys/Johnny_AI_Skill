# 05｜Opaque storage port contracts

| Field | Value |
| --- | --- |
| Artifact ID / kind | TICKET-CONTEXT-TELEMETRY-05-STORAGE-CONTRACTS / IMPLEMENTATION_TICKET |
| SPEC / acceptance source | SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R Revision 03 / AC-06 through AC-08 |
| Requirement / Context / upstream | PRD-20260803-006 / CHG-20260803-006 / doc/context/context-load-telemetry/main.md Revision 03 / ADR-20260824-019 / TAD-TELEMETRY-R03-ARCHITECTURE-01 (c249a5b8885b73a8cb08b4940c4e9a378b89084f683f7e939a95026f421e664a, canonical Git blob) |
| State / closure | CONVERGENCE_REVIEW_REQUIRED; CLOSURE-CONTEXT-TELEMETRY-05-STORAGE-CONTRACTS, revision 02 |
| Approval authority | Project-owner directive, 2026-08-24 (Asia/Taipei): Revision 03 authorizes reviewer-owned decomposition and pure no-effect tickets. This opening grants no dispatch or external-effect authority. |
| Baseline / dependency | c1ee1fee384ad2109b672707e10a56e4bc66976d; no implementation ticket precedes it. |
| Control owner / reviewer | Current-session Codex reviewer; semantic ticket-review profile (current intent: Terra/xhigh), to be host-verified before dispatch. |
| Implementation owner | Unassigned until receipt admission; semantic implementation-standard profile (current intent: Luna/xhigh). READY_LOW_MODEL; no hard-ticket elevation is authorized. |
| Worktree / branch / task | Allocated by the reviewer at dispatch. This closure is synchronous, so no receipt or descriptor is issued or required — see `ADR-20260823-014` Decisions 2 and 3. |
| Delivery stage / profile / resources | POC delivery stage; STANDARD floor because this creates a public typed contract boundary and no committed WorkloadAssessment may claim COMPACT. One implementation lane, one independent reviewer, zero helpers. |
| Implementation language / checker | Python 3.11; frozen strict Pydantic models, explicit finite enums and complete annotations; mypy --strict. |
| XSS / effects | XSS_NOT_APPLICABLE; no Browser/WebView/HTML/DOM/JavaScript. No filesystem, process, Git, network, provider, credential, runner, task, receipt-consumption, host-control or target-project effect is authorized. |
| Environment / rollback | Local pure-Python tests only. Revert the one implementation commit if review rejects it; no external compensation exists or is needed. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/telemetry_storage/
modify = modules/element/python/context-load-telemetry/05-opaque-storage-port-contracts/
modify = tests/test_telemetry_storage_contracts.py
create = library/local_orchestration/telemetry_storage/
create = modules/element/python/context-load-telemetry/05-opaque-storage-port-contracts/
create = tests/test_telemetry_storage_contracts.py
forbid = library/local_orchestration/__init__.py
forbid = library/workflow_router/telemetry.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/__init__.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
```

## Observable closure

One importable pure-Python contract family gives a later Johnny-owned storage adapter exactly one
typed input/output port. A caller can construct one validated opaque storage reference and one
valid operation request, call a typed fake port, and receive exactly one finite response shape.
Malformed identifiers, payload combinations, result-shape violations, count mismatches and dynamic
extra fields fail at construction. No class resolves a ledger, accepts a path, opens a file, invokes
a CLI or makes a provider/host claim.

TicketDecompositionDecision = READY_LOW_MODEL. Revision 03 freezes the finite states,
request/response union, READ payload, dependency direction and no-effect boundary. This ticket
does not choose a storage layout, perform ownership lookup, serialize telemetry, attach a real
adapter or change a report. A discovered contradiction returns ImplementationReturn.CHANGE_DETECTED.

## Frozen public contracts and dependency direction

Create library/local_orchestration/telemetry_storage/__init__.py and
library/local_orchestration/telemetry_storage/contracts.py. The latter may import only these
public value types:

~~~text
library.workflow_router.contracts.OpaqueMetadataId
library.workflow_router.contracts.ProjectId
library.workflow_router.contracts.RevisionDigest
library.workflow_router.contracts.RouterModel
library.workflow_router.telemetry.ContextUsageRecord
library.workflow_router.telemetry.NonNegativeCount
~~~

OpaqueMetadataId retains its existing grammar ^[a-z][a-z0-9-]{2,127}$; ProjectId and
RevisionDigest retain their existing public strict grammars. Do not duplicate, loosen or replace
them. executor_routing.py is evidence of the strict frozen-Pydantic/opaque-ID convention only;
it is not a storage dependency and must not be imported.

~~~text
TelemetryStorageLifecycle = ACTIVE | DETACHED | REMOVED
TelemetryStorageOperation = APPEND | READ | VALIDATE | DETACH | UNINSTALL
TelemetryStorageDecision = COMPLETED | STORAGE_REF_INVALID
                         | STORAGE_OWNERSHIP_MISMATCH | STORAGE_CLOSED
                         | STORAGE_BOUNDARY_VIOLATION | RECORD_INVALID

TelemetryStorageRef = {
  storage_ref: OpaqueMetadataId, project_id: ProjectId,
  stream_id: OpaqueMetadataId, ownership_ledger_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, lifecycle: TelemetryStorageLifecycle
}
AppendTelemetryStorageRequest = {
  storage_ref: TelemetryStorageRef, expected_project_id: ProjectId,
  expected_storage_revision: RevisionDigest, operation: APPEND,
  record: ContextUsageRecord
}
NoRecordTelemetryStorageRequest = {
  storage_ref: TelemetryStorageRef, expected_project_id: ProjectId,
  expected_storage_revision: RevisionDigest,
  operation: READ | VALIDATE | DETACH | UNINSTALL
}
TelemetryStorageRequest = AppendTelemetryStorageRequest | NoRecordTelemetryStorageRequest
TelemetryStorageReadPayload = { records: tuple[ContextUsageRecord, ...] }
CompletedAppendResponse = { storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, operation: APPEND,
  decision=COMPLETED, lifecycle: ACTIVE, record_count: NonNegativeCount }
CompletedReadResponse = { storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, operation: READ,
  decision=COMPLETED, lifecycle: ACTIVE, record_count: NonNegativeCount,
  read_payload: TelemetryStorageReadPayload }
CompletedValidateResponse = { storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, operation: VALIDATE,
  decision=COMPLETED, lifecycle: ACTIVE, record_count: NonNegativeCount,
  validation_report_ref: OpaqueMetadataId }
CompletedDetachResponse = { storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, operation: DETACH,
  decision=COMPLETED, lifecycle: DETACHED, record_count: NonNegativeCount }
CompletedUninstallResponse = { storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, operation: UNINSTALL,
  decision=COMPLETED, lifecycle: REMOVED, record_count: NonNegativeCount }
TelemetryStorageFailure = { storage_ref: OpaqueMetadataId,
  storage_revision: RevisionDigest, operation: TelemetryStorageOperation,
  decision=STORAGE_REF_INVALID | STORAGE_OWNERSHIP_MISMATCH | STORAGE_CLOSED
         | STORAGE_BOUNDARY_VIOLATION | RECORD_INVALID,
  failure_ref: OpaqueMetadataId }
TelemetryStorageResponse = CompletedAppendResponse | CompletedReadResponse
                         | CompletedValidateResponse | CompletedDetachResponse
                         | CompletedUninstallResponse | TelemetryStorageFailure
TelemetryStoragePort.execute(request: TelemetryStorageRequest) -> TelemetryStorageResponse
~~~

Every response storage_ref is OpaqueMetadataId, not the full TelemetryStorageRef. Every response
storage_revision is RevisionDigest; every response operation is TelemetryStorageOperation; every
completed response lifecycle is TelemetryStorageLifecycle; and every completed response
record_count is NonNegativeCount. Every owned DTO inherits the existing public RouterModel and is
therefore frozen, strict, extra-forbidden, fully annotated and nested-instance revalidated.
CompletedReadResponse requires record_count == len(read_payload.records). validation_report_ref
and failure_ref are OpaqueMetadataId. validation_report_ref exists only on completed
VALIDATE; read_payload only on completed READ; no completed response has failure_ref; every
failure has exactly one failure_ref and no lifecycle, count, read payload or validation report.
The request's expected project/revision need not match its supplied ref in this pure layer; the
later ownership-ledger adapter owns that decision.

TelemetryStoragePort is a typed Protocol; this ticket supplies no production adapter. The
dependency direction is workflow_router value contracts <- telemetry_storage.contracts <- future
johnny_owned_adapter <- future composition. It may not import library.local_orchestration
package-root exports, legacy JsonlContextUsageStore, a filesystem API or any
host/provider/dispatch module. ContextUsageRecord is admitted only because its current schema
excludes raw source text, prompt, response, URI, credential, raw host event and filesystem path;
the new contracts may not add any such field.

Create modules/element/python/context-load-telemetry/05-opaque-storage-port-contracts/README.md.
It names exactly the contract module, focused test, reused value types, ticket/closure revision and
no-I/O boundary; it never copies production source.

### Reusable-module selection record

~~~text
selected: none
why: MODULE_CATALOG has no delivered telemetry-storage contract card.
read: library/MODULE_CATALOG.md -> catalog indexes -> no matching card.
convention reused: executor_routing.py at c1ee1fee uses strict frozen Pydantic models and
  OpaqueMetadataId-compatible identifiers; it is not imported.
boundary: storage semantics, port and response union are new Revision 03 contracts; no storage
  adapter, ledger or provider module is reusable in this closure.
~~~

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| SC1 | Ordinary public validators construct a valid reference, append request, each no-record request and all five completed response variants. The fixture constructs one valid metadata-only ContextUsageRecord without model_construct, casts or a dynamic mapping. |
| SC2 | Invalid public identifier grammar, None/wrong primitive, unknown enum, whitespace-only opaque ID, dynamic extra field and bypass construction cannot serve as success evidence; ordinary validation rejects them. |
| SC3 | APPEND requires exactly one record. READ, VALIDATE, DETACH and UNINSTALL reject a record or another payload field. The pure models do not decide ledger ownership or filesystem state. |
| SC4 | READ requires only matching read payload and record_count == len(records); VALIDATE only its report ref; append/detach/uninstall neither. Every failure requires a finite non-completed decision and failure ref, and exposes no completed-only field. |
| SC5 | A local typed fake implementing TelemetryStoragePort accepts a validated request and returns a validated response without filesystem, process, Git, network, provider, task or host operation. |
| SC6 | A bounded AST/source gate proves both owned Python modules contain complete annotations and no Any, object, cast, dynamic lookup, model_construct, model_copy, legacy codec/package-root local-orchestration import, pathlib, os, subprocess, socket, open, or process/network/dispatch/runner/host/provider import or callable effect entry. |
| SC7 | Focused tests, strict typecheck, compile validation, declared-boundary diff and no cache/runtime residue are green. New behavior records named green evidence; it must not manufacture a baseline-red claim. |
| SM1 | Remove a strict/extra-field or ordinary-validator guard; SC2 turns red, then byte-for-byte restoration returns green. |
| SM2 | Permit a record on a no-record operation or omit it from APPEND; SC3 turns red, then restoration returns green. |
| SM3 | Remove the read count invariant or permit a read/report/failure field on the wrong response; SC4 turns red, then restoration returns green. |
| SM4 | Add one forbidden I/O/host import or typing bypass to an owned source module; SC6 turns red, then restoration returns green. |
| SM5 | Add a direct `library.local_orchestration` package-root import to an owned source module; SC6 turns red, then restoration returns green. |

Strong-type preflight runs before implementation and again before review. It constructs every
ordinary public success path, then proves negative primitive, nullability, enum, extra-field and
response-shape cases. model_construct, model_copy, casts, Any, dynamic lookup and historical-object
reuse are negative-only evidence. Missing preflight is HALT / TICKET_SCHEMA_INVALID.

### Applicable review defect classes

| # | Category | Applies | Required case |
| --- | --- | --- | --- |
| 1 | Path identity/prefix | No | No path is accepted or resolved; SC6 rejects all path/I/O entry points. |
| 2 | Missing values | Yes | None, wrong primitive, empty/whitespace opaque ID, absent append record and empty read tuple are independently asserted. Empty read tuple is valid only with count zero. |
| 3 | Authorization bypass | No | No authorization or external capability exists in this pure contract closure. |
| 4 | Token parsing/comparison | No | No credential/token is parsed or compared. |
| 5 | Error-code consistency | Yes | Every non-completed storage decision is finite, retains one opaque failure ref, and cannot be a completed result. |
| 6 | Exception behavior | Yes | Validation failures raise Pydantic validation errors; the fake port has no dependency or effect whose exception could be swallowed. |

## Verification and review

Implementation-owner focused commands:

~~~text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_contracts.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/__init__.py library/local_orchestration/telemetry_storage/contracts.py tests/test_telemetry_storage_contracts.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/__init__.py library/local_orchestration/telemetry_storage/contracts.py
git diff --check <ticket-baseline> HEAD
~~~

The Terra/xhigh reviewer re-runs focused checks and strong-type preflight, validates ticket
blob/baseline/registry, verifies declared boundary and no-effect AST gate, replays all four
restored reverse mutations and performs an independent counter-mutation through a different path.
Zero-red is a finding. Full-suite and residue checks remain the reviewer's responsibility before
integration.

## Ownership, receipt and return

Dispatch for this closure is synchronous: the reviewer dispatches, waits for completion, reviews,
and integrates through `admit_document_mutation`. Per `ADR-20260823-014` Decision 3 that path
requires no live descriptor, receipt, queue or host gateway, and Decision 2 forbids blocking a
synchronous flow because such a bridge is absent. A receipt-bound descriptor is required only when
the dispatching reviewer and the returning implementer occupy different lifetimes — a handoff
across hosts, sessions or machines. This closure does not.

The implementation owner receives an identifier-only dispatch envelope. It modifies only this
ticket's boundary and cannot control another Agent, integrate, push, reserve a task, consume a
receipt or invoke a provider. The reviewer remains the sole orchestrator.

Return exactly ImplementationReturn.COMPLETED -> ACTION_COMPLETED with named TDD/type/mutation
evidence, BLOCKED -> HALT with the failed cell, or CHANGE_DETECTED -> REQUIREMENT_CHANGED.
No return authorizes adapter composition, storage write, target-project mutation, host delivery,
runner wake, merge, push, release or deployment.

## Convergence review disposition — revision 02

Closure revision 01 consumed its initial review and one additive correction review. The second
review found that SC6's frozen package-root-import prohibition had no authentic first-red proof:
a disposable `from library.local_orchestration import plugin_publication` mutation remained green.

This is an `EVIDENCE_DEFECT`, not a changed requirement, architecture, public contract, ownership
boundary, or a second independently observable responsibility. `TicketDecompositionDecision`
therefore remains `READY_LOW_MODEL`: do not split the ticket and do not elevate its
implementation model. The existing ticket worktree and branch remain the only implementation
lane; previously reviewed work is preserved as evidence and must not be reset, amended or
discarded.

Revision 02 authorizes exactly one further additive correction and one Terra/xhigh correction
review. The correction must make SC6 reject the direct package-root import in SM5 on the actual
owned contract path, restore it byte-for-byte, and rerun the complete frozen closure. A further
blocking review finding returns to control-plane convergence again; it does not authorize an
unbounded correction loop.

~~~johnny-status
id = 05
title = Opaque storage port contracts
state = CONVERGENCE_REVIEW_REQUIRED / CLOSURE_02_REDISPATCH_AUTHORIZED
stage = C | strict public request/response contracts | OPEN
stage = R | metadata-only READ and response exclusivity | OPEN
stage = M | five reverse mutations | OPEN
~~~
