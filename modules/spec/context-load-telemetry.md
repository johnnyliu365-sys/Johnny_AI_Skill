# Context Load Telemetry POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| State | `APPROVED` |
| Owner | `root/main` |
| Context | `doc/context/context-load-telemetry/main.md` |
| PRD reference | `PRD.md §10` |
| Change | `CHG-20260803-006` |

## Goal

Produce local, shareable evidence that a Router-selected ContextPacket reduces actual Agent input context compared with a matched baseline, without exporting source text, prompts, or secrets.

## Scope

- Strongly typed Pydantic telemetry records for router and baseline runs.
- Deterministic packet-token estimate for budget observation, clearly distinct from provider-reported usage.
- Metadata-only JSONL append/read support under a caller-selected ignored directory.
- Fail-closed validation of router guards and matched baseline/router pairs.
- Aggregate median reduction only where both records supply provider-reported input-token counts.
- Unit tests and usage documentation.

## Non-goals

- Do not capture raw ContextPacket text, prompts, source URIs, provider credentials, source files, or company code.
- Do not make a production Agent supervisor, enforce all Agent tool I/O, install a service, or write telemetry into a target repository automatically.
- Do not substitute an estimated token count for actual provider input usage when claiming reduction.

## Data contract

Each `ContextUsageRecord` contains a run ID, comparison group and attempt, snapshot ID, mode, typed Router metadata, source fingerprints/revisions/spans, budget and estimated packet tokens, optional provider usage, quality outcome, and guard results. `SourceSnippet.text` is structurally absent from the record and all JSONL output.

A comparison pair is valid only when its baseline and router records share `(comparison_group_id, attempt, project_snapshot_id, provider, model)`. Any missing counterpart, provider input count, budget breach, undeclared source, or router quality regression is a validation failure.

## Acceptance criteria

1. JSONL output has one strict schema-validated record per line and never contains a supplied unique raw source string.
2. Router records expose only source fingerprint, kind, identifier, revision, span, and estimated size; ContextView raw-text separation remains intact.
3. Validator rejects invalid router guard states and incomplete/non-comparable pairs.
4. Validator reports median provider-input-token reduction and quality result for valid pairs.
5. All Router and project test/type gates pass.

## Approval

The project owner explicitly authorized implementation on `2026-08-03` for personal local-project validation.
