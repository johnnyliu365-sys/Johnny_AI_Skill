# Context Load Telemetry POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| State | `APPROVED_BASELINE / REVISION_02_PROJECT_ISOLATION_APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED` |
| Owner | `root/main` |
| Context | `doc/context/context-load-telemetry/main.md` |
| PRD reference | `PRD-20260803-006` |
| Change | `CHG-20260803-006`; project-isolation revision `CHG-20260815-024` / `ADR-20260815-013` |

## Goal

Produce local, shareable evidence that a Router-selected ContextPacket reduces actual Agent input context compared with a matched baseline, without exporting source text, prompts, or secrets.

## Scope

- Strongly typed Pydantic telemetry records for router and baseline runs.
- Deterministic packet-token estimate for budget observation, clearly distinct from provider-reported usage.
- Metadata-only JSONL append/read support through an opaque
  `TelemetryStorageRef` resolved only beneath the per-user Johnny root.
- Fail-closed validation of router guards and matched baseline/router pairs.
- Aggregate median reduction only where both records supply provider-reported input-token counts.
- Unit tests and usage documentation.

## Non-goals

- Do not capture raw ContextPacket text, prompts, source URIs, provider credentials, source files, or company code.
- Do not make a production Agent supervisor, enforce all Agent tool I/O, install a service, or write raw telemetry into a target repository either automatically or through a caller-supplied path.
- Do not substitute an estimated token count for actual provider input usage when claiming reduction.

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
                         | STORAGE_BOUNDARY_VIOLATION | RECORD_INVALID

TelemetryStorageRef = {
  storage_ref, project_id, stream_id,
  ownership_ledger_ref, storage_revision, lifecycle
}

TelemetryStorageRequest = {
  storage_ref, expected_project_id, expected_storage_revision,
  operation, record?
}

TelemetryStorageResult = {
  storage_ref, storage_revision, operation, decision,
  record_count?, validation_report_ref?, failure_ref?
}
```

Every identifier is a validated named type with a finite pattern. `record` is
present only for `APPEND`; other operation/payload combinations fail before I/O.
No production request or result has a filesystem-path field. Boundary adapters
validate dynamic JSON and filesystem/Git/provider output before constructing
these contracts; `Any`, implicit `any`, unvalidated mappings and stringly typed
lifecycle/decision values cannot enter the core.

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

## Approval

The project owner explicitly authorized the baseline implementation on
`2026-08-03` for personal local-project validation and approved the exact
Revision 02 project-isolation correction on `2026-08-15` under
`CHG-20260815-024`. The reviewer may decompose/open tickets for this exact
closure. Approval creates no dispatch receipt and grants no source,
target-project, telemetry-write, cleanup or external-effect authority. The
legacy raw-path POC remains prohibited for controlled-target use until the
approved tickets are implemented, independently reviewed and integrated.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `72438a30a4ad698be33292de8d63a7f2dc289daf` | Drafted Revision 02 to replace caller-selected target-local telemetry paths with a Johnny-owned opaque storage reference; owner approval pending. |
| 2026-08-15 | Project owner | Approved the exact Telemetry Storage Revision 02 and assigned ticket decomposition/opening to the reviewer. |
