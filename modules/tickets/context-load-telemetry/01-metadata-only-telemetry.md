# 01 — Metadata-only Context Telemetry

| Field | Value |
| --- | --- |
| Parent specification | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| Owner | `root/main` |
| Context | `doc/context/context-load-telemetry/main.md` |
| Change | `CHG-20260803-006` |
| State | `DONE` |
| Environment | `LOCAL` |
| In scope | Router telemetry contracts, writer/reader, validator, tests, and documentation. |
| Out of scope | Company project writes, raw source export, external telemetry service, secret storage, and provider runtime integration. |

## TDD acceptance cases

1. A router record writes no raw source text or URI to JSONL and round-trips through strict validation.
2. A valid baseline/router pair reports provider-token reduction.
3. Missing provider usage, pair mismatch, budget breach, undeclared source, or quality regression fails validation.
4. Existing ContextView and CitationLedger raw-text exclusion remains covered.

## Implementation notes

- Caller selects an ignored output directory, normally `.johnny-router/`.
- The record stores hashes and counts only. The project owner may attach a sanitized JSONL copy to a later Codex task for analysis.
- Provider-reported usage is optional to record but mandatory for a reduction claim.

## Handoff

Static validation passed. `PENDING_FEATURE_COMMIT`: replace after the feature commit.
