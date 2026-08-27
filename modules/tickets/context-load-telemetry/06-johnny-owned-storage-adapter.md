# 06｜Johnny-owned telemetry storage adapter

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-06-JOHNNY-OWNED-STORAGE-ADAPTER` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 03 / AC-06 through AC-08 |
| Requirement / Context / ADR | `PRD-20260803-006` / `CHG-20260803-006` / `doc/context/context-load-telemetry/main.md` Revision 03 / `ADR-20260824-019` / `TAD-TELEMETRY-R03-ARCHITECTURE-01` |
| State / closure | `BLOCKED / SUPERSEDED_BY_REVISION_04_LOCK_CONTRACT`; no source candidate is admissible under this closure revision. |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): begin the existing Context Governor Accounting path. `ADR-20260824-019` already authorizes pure no-effect decomposition. |
| Baseline / dependency | `38e4e97b86057f4682f114f9f13ab6d2ee00b02a`; Ticket 05 (`e509174`) is integrated and freezes the storage public contracts. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh. `READY_LOW_MODEL`; no elevation is authorized. |
| Worktree / branch / task | Allocated by reviewer at synchronous dispatch beneath `.worktrees/context-load-telemetry-06`; no receipt, descriptor, runner, queue or host workspace readback is required. |
| Delivery / language | `POC / STANDARD` floor; Python 3.11, frozen strict Pydantic contracts and `mypy --strict`; one implementer lane, no helpers. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Tests may create and remove only disposable files below a test-created Johnny root. No target-project, provider, credential, host CLI, process, network, Git, runner, queue, receipt or remote effect is authorized. |

## Revision 04 supersession

`ADR-20260827-022` and `CHG-20260827-041` establish that durable telemetry storage is a
cross-process boundary with a named `LOCK_CONTENDED` result and mandatory lock-bound
re-admission. This ticket was opened before that public contract existed. Its uncommitted
implementation candidate is preserved as review evidence only; it must not be committed,
integrated, rebased as a correction, or used as a substitute for the new contract. A later ticket
will first close the strict lock contract and capability-selection prerequisite, then reopen a
lock-bound adapter closure from a fresh main baseline.

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/telemetry_storage/
modify = tests/test_telemetry_storage_adapter.py
create = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
create = library/local_orchestration/telemetry_storage/composition.py
create = tests/test_telemetry_storage_adapter.py
create = modules/element/python/context-load-telemetry/06-johnny-owned-storage-adapter/
forbid = library/local_orchestration/telemetry_storage/contracts.py
forbid = library/local_orchestration/telemetry_storage/__init__.py
forbid = library/workflow_router/telemetry.py
forbid = library/workflow_router/telemetry_cli.py
forbid = library/workflow_router/__init__.py
forbid = library/local_orchestration/johnny_root_layout.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
```

## One observable closure

An injected adapter resolves an already-issued opaque `TelemetryStorageRef` through a
Johnny-owned, metadata-only ledger beneath `JohnnyRootLayout.telemetry_root`, then executes
exactly one valid `TelemetryStoragePort` operation. It accepts no caller path, root override,
target path, source text, prompt, URI, credential, raw host event, filter, pagination or dynamic
payload. A composition function is the only public construction point for the adapter; callers
depend on Ticket 05 contracts only.

This ticket admits only fixture-backed lifecycle evidence. The fixture creates a temporary,
absolute Johnny root and a pre-existing owned storage ledger. It proves the controlled target
repository bytes and Git status do not change. It does not register a project, mint a storage
reference, invoke a host, collect provider usage or render an aggregate report.

## Frozen adapter rules

1. The private ledger maps the exact tuple `(storage_ref, project_id, stream_id,
   ownership_ledger_ref)` to one relative stream location below `telemetry_root`; no public
   request, response, error or durable telemetry record contains that location.
2. The adapter validates in this order: strict request shape; ledger ownership including expected
   project and revision; `ACTIVE` lifecycle; resolved-path containment plus no reparse point;
   then record validation. It returns the finite Ticket 05 decision for the first failed class
   and no raw diagnostic.
3. `APPEND` writes one schema-validated metadata-only `ContextUsageRecord` through the legacy
   JSONL codec only after all prior checks pass. `READ` returns the complete immutable tuple in
   append order. `VALIDATE` runs the existing validator and returns only an opaque report
   fingerprint. `DETACH` and `UNINSTALL` remove only the exact ledger-owned stream and advance
   its lifecycle; a detached or removed ref rejects every later operation as `STORAGE_CLOSED`.
4. The adapter never creates a missing ledger, stream or directory for an invalid request. A
   fresh ledger/stream registration and a sanitized aggregate report are later closures.
5. `composition.py` may construct only this adapter from an injected layout and ledger port.
   It must not expose the legacy path-taking codec or allow callers to construct the adapter with
   a raw path.

## TDD acceptance matrix

| Cell | Required behavior |
| --- | --- |
| SA1 | An ordinary append followed by read preserves one metadata-only record and reports the required count/revision shape. |
| SA2 | A mismatched project, stream, ledger identity or expected revision fails `STORAGE_OWNERSHIP_MISMATCH` before any stream write. |
| SA3 | A non-active ref fails `STORAGE_CLOSED`; an escaped, symlinked or reparse-point stream location fails `STORAGE_BOUNDARY_VIOLATION`; both leave fixture bytes unchanged. |
| SA4 | Validate returns only the finite completed response and opaque report ref. Detach and uninstall remove only the exact owned stream; every later operation is closed. |
| SA5 | Missing, malformed or extra-field requests and invalid records fail with their declared finite decision and expose neither path nor raw validation detail. |
| SA6 | The composition root constructs the adapter only from injected Johnny-owned dependencies. A caller cannot supply a path or import the legacy codec through the composition public surface. |
| SA7 | A target-repository snapshot and `git status --porcelain` are byte-identical before and after every fixture test. |
| SA8 | Focused tests, strict mypy, compile validation, `git diff --check`, declared-boundary check and no cache/runtime residue are green. |
| SM1 | Temporarily bypass expected-project/revision comparison; SA2 turns red and byte-for-byte restoration returns green. |
| SM2 | Temporarily allow a path escape or reparse point; SA3 turns red and restoration returns green. |
| SM3 | Temporarily call the legacy codec before ledger/lifecycle admission; SA2 or SA3 turns red and restoration returns green. |
| SM4 | Temporarily add a raw-path public constructor argument or composition export; SA6 turns red and restoration returns green. |

## Implementation and review

The implementer edits only the declared boundary, does not commit, and returns
`ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with focused TDD/type/mutation evidence;
`BLOCKED` names the failed cell; `CHANGE_DETECTED` returns `REQUIREMENT_CHANGED`. The Terra/xhigh
reviewer personally re-runs all named checks, validates the ticket baseline and boundary, performs
an independent containment counter-mutation, commits the reviewed candidate, and submits it
through `admit_document_mutation`. No completion authorizes a real telemetry write outside a
temporary fixture, a host usage probe, provider access, cost calculation, report publication or
Context Compiler work.

### Verification commands

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_adapter.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/johnny_owned_adapter.py library/local_orchestration/telemetry_storage/composition.py tests/test_telemetry_storage_adapter.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/johnny_owned_adapter.py library/local_orchestration/telemetry_storage/composition.py
git diff --check <ticket-baseline> HEAD
```

### Reusable-module selection record

```text
selected: JohnnyRootLayout / JsonlContextUsageStore (existing source, not plugin runtime)
why: JohnnyRootLayout is the existing per-user ownership boundary and JsonlContextUsageStore is
the frozen legacy codec that ADR-019 permits only behind this adapter.
not selected: PluginUninstallLedger; its receipt-owned installation lifecycle is not a project
telemetry ownership ledger and must not be widened by this ticket.
```

```johnny-status
id = 06
title = Johnny-owned telemetry storage adapter
state = BLOCKED
stage = A | public lock contract absent at opening | BLOCKED
stage = L | fixture lifecycle and containment | SUPERSEDED
stage = R | reviewer counter-mutation | EVIDENCE_PRESERVED
```
