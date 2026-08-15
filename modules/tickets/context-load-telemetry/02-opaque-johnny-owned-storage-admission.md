# Revision 02 Opaque Johnny-owned Telemetry Storage Admission Decision

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TAD-TELEMETRY-R02-STORAGE-01` / `TICKET_ADMISSION_DECISION` |
| Authority | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 02, AC-06 through AC-08 |
| Requirement / Context / ADR | `PRD-20260815-024` / `CHG-20260815-024` / `doc/context/context-load-telemetry/main.md` / `ADR-20260815-013` |
| Decision | `UPSTREAM_DECISION_REQUIRED` |
| State | `NON_DISPATCHABLE`; this is not an implementation ticket |
| Baseline | `7e7ddea5edf1a879eda1ee29f628a945eb0424d6` |
| XSS / effects | `XSS_NOT_APPLICABLE`; no Browser/WebView/DOM/JavaScript context is in scope. The present action authorizes no telemetry, filesystem, target, Git, host or network effect. |

## Decomposition result

Revision 02 supplies the core request/result vocabulary, but not enough public boundary detail to
admit a vertical implementation closure. The existing `JsonlContextUsageStore.append(path=...)`
and path-taking CLI are explicitly legacy and non-admitted for controlled targets; a reviewer may
not select a replacement port, filesystem layout or error precedence by convention.

| Candidate closure | Exact missing architecture contract | Why a reviewer cannot infer it |
| --- | --- | --- |
| Opaque storage admission and ownership resolution | Named finite field types/patterns for every `TelemetryStorageRef` field, plus a strict ownership-ledger lookup contract and canonical mapping from unknown, revoked, cross-project, escape/reparse/symlink and raw-path input to the declared decisions. | Revision 02 requires fail-closed behavior but does not bind those inputs to one exact decision or ledger proof shape. |
| Adapter execution and Composition Root | The injected Johnny-owned adapter protocol, its request/result/error boundaries, allowed storage-root derivation, and the Composition Root that prevents the legacy path API/CLI from bypassing it. | The SPEC says an adapter is injected but defines neither its public protocol nor the source-level dependency direction. |
| Lifecycle operations | Operation-specific result nullability/invariants for `APPEND`, `READ`, `VALIDATE`, `DETACH` and `UNINSTALL`, including record-count/report/failure reference meaning and exact lifecycle/error precedence. | `TelemetryStorageResult` marks three fields optional without defining which combinations are legal for each operation. That prevents a complete strict contract matrix and deterministic first-red TDD. |

## Required upstream amendment

The architecture owner must amend Revision 02 with the three contract families above. The amendment
must preserve the existing prohibition on raw target paths and explicitly name the future source
boundary that replaces or fences `telemetry.py`'s legacy `JsonlContextUsageStore` and
`telemetry_cli.py` path argument. Only then can a ticket bind Python 3.11/mypy-strict contracts,
one observable adapter closure, finite first-red TDD, a disposable Johnny-owned test root,
controlled-target non-mutation proof, resource plan, rollback and typed return.

No implementation owner, worktree, branch, receipt, source/test scope, cleanup operation or
telemetry effect is authorized by this decision.

## Router return

`UPSTREAM_DECISION_REQUIRED / TELEMETRY_STORAGE_ADAPTER_CONTRACT_UNDEFINED`
