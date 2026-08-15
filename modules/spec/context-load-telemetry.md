# Context Load Telemetry Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| State | `APPROVED_BASELINE / REVISION_02_PROJECT_ISOLATION_APPROVED / REVISION_03_OWNER_REVIEW_REQUIRED` |
| Owner | `root/main` |
| Context | `doc/context/context-load-telemetry/main.md` |
| PRD reference | `PRD-20260803-006`, `PRD-20260816-025` |
| Change | `CHG-20260803-006`; project-isolation `CHG-20260815-024` / `ADR-20260815-013`; evidence/reporting `CHG-20260816-025` / `ADR-20260816-014` |

## Goal

Produce receipt-indexed evidence of actual Johnny model usage and an on-demand, zero-inference
counterfactual showing how much input Context Johnny avoided, without exporting source text,
prompts, paths or Secrets. Output/cost projections must remain explicitly distinct from observed
provider usage.

## Scope

- Strongly typed provider-usage records for every receipt-bound model call, including input,
  cached input, optional cache-write input and output tokens plus role/model/strength/pricing
  metadata.
- A metadata-only `RuntimeEvidenceManifest` that indexes Context exposure, model-visible reads,
  final Git diff, optional gross-write evidence and provider usage without copying raw content.
- Segmented JSONL append/read support through an opaque `TelemetryStorageRef` resolved only
  beneath the per-user Johnny root.
- User-requested receipt-by-receipt recalculation, deterministic no-takeover baseline dry count,
  native-currency cost grouping and terminal/Markdown/JSON/CSV/SVG reports to stdout.
- Fail-closed distinction among observed, projected, estimated, not-observed, not-reported and
  unpriced values.

## Non-goals

- Do not capture raw ContextPacket text, prompts, source URIs, provider credentials, source files, or company code.
- Do not make a production Agent supervisor, enforce all Agent tool I/O, install a service, run a
  baseline model inference, or write raw telemetry/reports into a target repository either
  automatically or through a caller-supplied path.
- Do not substitute an Agent estimate, character count or proxy tokenizer count for actual
  provider usage. Do not perform continuous aggregation, report polling or automatic charts.

## Data contract

Each `ModelUsageRecord` binds one `TicketReceipt` or `StageWorkReceipt`, role/task, attempt,
project snapshot, context epoch, exact provider/model/revision, capability tier, reasoning
effort, service tier and pricing revision. Provider fields are:

```text
uncached_input_tokens = input_tokens - cached_input_tokens
total_tokens = input_tokens + output_tokens
```

`cached_input_tokens` is a subset of `input_tokens`; it is never added twice. Optional
`cache_write_input_tokens` is priced separately but remains part of input, not an extra token
total. Missing provider fields are `USAGE_NOT_REPORTED`, never estimated as actual.

The existing paired baseline/router record and median calculation are retained only as legacy
POC evidence. Revision 03 replaces them for controlled-target savings reports with the
receipt-indexed counterfactual contract below after exact owner approval.

### Revision 02 storage boundary

Production callers supply a validated opaque `TelemetryStorageRef`, never a raw
filesystem path. An injected Johnny-owned storage adapter resolves that identity
below the per-user Johnny root using the ownership ledger. The durable record,
CLI arguments, reports and errors contain no target path. Project detach removes
only that project's owned stream/mapping; plugin uninstall removes all
ledger-owned telemetry. Neither operation changes the target repository.

The existing `JsonlContextUsageStore.append(path=...)` interface remains legacy
POC code and is not admitted for controlled-target use. Until a Senior-owned
ticket replaces or hardens it, it may be used only with disposable test fixtures
or paths internal to Johnny's own development repository. A validated report is
emitted only to stdout on explicit user request. Johnny never selects an output
path or writes the report/raw JSONL into a controlled target; a human may
independently redirect terminal output outside the control-plane action.

### Revision 02 typed contracts

```text
TelemetryStorageLifecycle = ACTIVE | DETACHED | REMOVED
TelemetryStorageOperation = APPEND | READ | VALIDATE | SEAL | DETACH | UNINSTALL
TelemetryStorageDecision = COMPLETED | STORAGE_REF_INVALID
                         | STORAGE_OWNERSHIP_MISMATCH | STORAGE_CLOSED
                         | STORAGE_BOUNDARY_VIOLATION | RECORD_INVALID
                         | CURSOR_INVALID | LIMIT_INVALID | TELEMETRY_FAILED

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

### Revision 03 receipt stream and storage operations

One logical telemetry stream belongs to one `WorkReceipt`. Same-ticket correction appends to the
same `TicketReceipt` stream; a repair ticket has a new receipt and stream. A `StageWorkReceipt`
provides equivalent Architecture/Grill/SPEC/Senior provenance without execution authority.
Lifecycle is `ACTIVE -> SEALED -> DETACHED -> REMOVED`; there is no time expiry.

JSONL segments are at most 16 MiB beneath one logical stream. `APPEND` validates one record of at
most 64 KiB and updates rolling record count/digest. `READ` requires a cursor and returns at most
100 records or 1 MiB. Active streams receive incremental validation only; one full validation at
seal must fit the receipt's resource plan. No background scan, compaction, polling or aggregate
calculation occurs.

Idempotent retry uses the same operation/record identity. Corruption closes the stream as
`TELEMETRY_FAILED`; a replacement stream for the same receipt is forbidden. Ordinary product
work may still complete but is marked `TELEMETRY_UNAVAILABLE` and cannot claim savings.
Telemetry's own implementation tickets fail their acceptance closure. No raw-path fallback is
allowed.

### Revision 03 runtime evidence and usage collection

Execution persists only a `RuntimeEvidenceManifest` containing immutable metadata refs and
digests for:

- model-visible `CONTEXT_EXPOSURE` and `INTERACTIVE_MODEL_READ` items;
- exact result baseline/commit and final Git diff;
- optional write/commit evidence for gross churn;
- provider usage events and pricing snapshot;
- project, receipt, role, model profile, context epoch, attempt and evidence revision.

The preferred collection path is a receipt-bound `MODEL_USAGE_REPORTED` subscription with exact
`event_source_ref` and `subscription_id`. Its callback is ordinary bounded adapter code and does
not wake a model. At receipt close, one exact completion/readback reconciliation may fill or
deduplicate terminal provider data. If neither event nor readback exists, usage is
`USAGE_NOT_REPORTED`; Agent self-report and token estimates cannot replace it. Heartbeat and
recurring provider/thread reads are forbidden.

### Revision 03 measured dimensions

`CONTEXT_EXPOSURE` and `INTERACTIVE_MODEL_READ` count content actually made model-visible. The
same content exposed twice counts twice in cumulative input; reports also show `unique_source`
and `repeated_read`. Tool-internal Git, test, compiler, mypy and Docker I/O is recorded only as
bytes/CPU/I/O resource evidence, never as model tokens.

`FINAL_DELIVERED` is calculated from the exact baseline-to-result Git diff and reports added,
deleted and net characters/lines separately for production source, tests, config, migration,
docs, SPEC, ticket, review and Context. `GROSS_WRITTEN` uses bounded write/commit evidence to
include rewrites, corrections and churn. When write events are unavailable, gross is
`NOT_OBSERVED`; final diff remains calculable. Source characters are not provider output tokens.

Cost groups by role plus exact provider/model/revision, capability tier, reasoning effort,
service tier and pricing revision. Uncached input, cache read, cache write and output use
separate price buckets. Source priority is provider-reported cost, then versioned provider/user
price catalog, then `UNPRICED`. Records retain their price snapshot and provider-native currency;
there is no FX conversion. Local models are `UNPRICED_LOCAL` in this revision.

### Revision 03 user-requested report

No report runs automatically. On an explicit user request, the calculator starts from one
receipt, resolves the exact immutable evidence refs and recalculates every item. An active
receipt returns `PARTIAL / AS_OF` bound to the current evidence revision/digest; a sealed receipt
returns `FINAL`. Repeating the same receipt/evidence/rules verifies the same report ID and does
not create a duplicate.

The calculator is a Johnny-owned deterministic script/adapter, not an Agent role. Calculation
performs zero model calls and cannot wake Architecture, Senior, Implementer or Debugger.

Only a small `ReportCalculationManifest` is durable: receipt, evidence, model/tokenizer/pricing,
baseline/cache/output assumptions, results, digest and status. Rendered terminal, Markdown,
JSON, CSV and SVG output is produced on demand to stdout; diagnostics use stderr. Charts include
Johnny-versus-no-takeover input-token bars, token/cost by role/model/strength and ticket trends,
with observed versus projected labels. Raw prompt, source and path content never appears.

### Revision 03 no-takeover counterfactual

The default `NO_TAKEOVER_FULL_TRACKED_TEXT` baseline performs zero model inference and incurs no
provider token charge. It uses the exact Git snapshot and all eligible Git-tracked text in
source, tests, docs, project requirements and config, while excluding `.git`, binary files,
Secrets, dependencies/build caches, untracked files and every Johnny plugin, Router, skill and
Context-Library optimization input. If the selected text exceeds the exact model context window,
the result is `BASELINE_CONTEXT_OVERFLOW`; silent truncation is forbidden.

Comparison binds the same provider/model/revision, capability tier, reasoning effort, service
tier, pricing revision and task behavior. The primary `EQUAL_OUTPUT_ASSUMPTION` projects baseline
output tokens equal to observed Johnny output, so output cancels and the primary saving is input
Context. This is a projection, not an observed baseline run.

The primary cache case is `SAME_EXISTING_CACHE_ASSUMPTION`: the absolute cached input from the
Johnny run remains cached and added baseline Context is uncached. Reports also calculate
`COLD_CACHE_BASELINE` and `SAME_CACHE_RATIO_BASELINE`. Token evidence is exactly one of
`PROVIDER_DRY_COUNT` (zero inference/no billing), `EXACT_LOCAL_TOKENIZER`,
`VERSIONED_PROXY_TOKENIZER` or `CHAR_ONLY`. Proxy output is marked estimated; character-only
output cannot claim token or cost savings. Observed and projected values are never combined.

The calculation uses an approved low-resource execution plan and honors local-model reservation
priority. It never wakes a role, scans receipts other than those explicitly requested, or runs
on a schedule.

### Revision 03 adapter boundary and result precedence

The Johnny telemetry Composition Root injects `TelemetryOwnershipLedgerPort`,
`TelemetrySegmentStorePort`, `RuntimeEventSubscriptionPort`, `ProviderUsageReadbackPort`,
`GitEvidencePort`, `TokenizerPort`, `PricingCatalogPort` and `ReportStdoutPort`. Core validators
and calculators are pure and cannot resolve a path, call a provider, read Git or choose an output
destination directly.

Storage admission resolves in this order before I/O: schema/operation payload, opaque storage
reference, project/receipt match, lifecycle, ownership ledger, boundary/path proof, record or
cursor/limit validation, then rolling digest. A failing earlier decision cannot be replaced by a
later generic error.

Operation payloads and results are closed:

- `APPEND` requires one record and returns new revision/count/digest only;
- `READ` requires cursor/limit and returns next cursor plus bounded record refs only;
- `VALIDATE` takes no record/cursor and returns one validation report ref;
- `SEAL` takes the active revision and returns final count/digest/report ref;
- `DETACH`/`UNINSTALL` take ownership authority and return lifecycle/removal evidence only.

On `COMPLETED`, only the fields declared for that operation are present and `failure_ref` is
absent. On failure, all success payload fields are absent and one sanitized `failure_ref` is
present. Production constructors accept opaque refs, never a caller-selected path or output
file. The existing path-based store/CLI remains behind an explicit `TEST_FIXTURE_ONLY` adapter
and cannot be injected into controlled-target composition.

### Revision 03 typed contracts

```text
WorkReceiptKind = TICKET | STAGE_WORK
TelemetryStreamLifecycle = ACTIVE | SEALED | DETACHED | REMOVED | TELEMETRY_FAILED
UsageObservationState = REPORTED | USAGE_NOT_REPORTED
EvidenceObservationState = OBSERVED | NOT_OBSERVED
ReportLifecycle = PARTIAL_AS_OF | FINAL
TokenizerEvidenceKind = PROVIDER_DRY_COUNT | EXACT_LOCAL_TOKENIZER
                      | VERSIONED_PROXY_TOKENIZER | CHAR_ONLY
CacheBaselineKind = SAME_EXISTING_CACHE_ASSUMPTION
                  | COLD_CACHE_BASELINE | SAME_CACHE_RATIO_BASELINE
PricingState = PROVIDER_REPORTED | CATALOG_PRICED | UNPRICED | UNPRICED_LOCAL

ModelUsageRecord = {
  usage_record_id, project_id, work_receipt_ref, role_ref, task_ref,
  attempt, project_snapshot_id, context_epoch_ref,
  provider, model, model_revision, capability_tier, reasoning_effort,
  service_tier, input_tokens, cached_input_tokens,
  cache_write_input_tokens?, output_tokens, provider_cost?,
  pricing_revision?, native_currency?, observation_state, evidence_ref,
  record_digest
}

RuntimeEvidenceManifest = {
  manifest_ref, project_id, work_receipt_ref, role_ref, model_profile_ref,
  context_epoch_ref, attempt, context_exposure_refs, interactive_read_refs,
  baseline_commit, result_commit?, final_diff_ref?, gross_write_refs,
  provider_usage_refs, acceptance_outcome_ref?, pricing_snapshot_ref?, evidence_revision,
  evidence_digest, lifecycle
}

ReportCalculationManifest = {
  report_id, work_receipt_ref, evidence_manifest_ref, evidence_revision,
  model_profile_ref, tokenizer_evidence_ref, pricing_snapshot_ref?,
  baseline_kind, cache_baseline_kind, equal_output_assumption,
  calculation_rules_revision, result_refs, report_lifecycle, report_digest
}
```

## Acceptance criteria

1. Every JSONL line and report manifest passes strict schema validation and contains no supplied
   unique raw source, prompt, path, URI, Secret or Provider payload.
2. Model-usage records validate `0 <= cached_input_tokens <= input_tokens`, keep optional cache
   writes separate for price calculation, compute total as input plus output and bind exact role,
   model/strength/tier/pricing and one valid receipt.
3. A `TicketReceipt` and `StageWorkReceipt` both index usage evidence but cannot be converted or
   combined. Same-ticket correction remains one stream; repair ticket creates a new stream.
4. Segmentation/operation tests enforce 16 MiB segments, 64 KiB records, cursor reads limited to
   100 records or 1 MiB, rolling digest/count, incremental active validation and one seal scan.
5. Corruption produces `TELEMETRY_FAILED` with no replacement stream. Ordinary product work may
   close `TELEMETRY_UNAVAILABLE`, while telemetry-feature tickets fail. No fallback path exists.
6. Storage tests reject raw target paths, path escape, reparse/symlink, cross-project refs,
   unknown/revoked ownership and cleanup outside the exact ledger entry before filesystem
   effect. A controlled target's bytes and Git status remain unchanged through the lifecycle.
7. Runtime-event matrices require exact event source/subscription/receipt/role/task/revision,
   deduplicate callbacks and permit exactly one terminal reconciliation. Missing usage is
   `USAGE_NOT_REPORTED`; no heartbeat, recurring read or Agent estimate appears.
8. Exposure tests count repeated model-visible content repeatedly while reporting unique/repeat
   dimensions. Tool-internal I/O never becomes a token metric.
9. Final-diff tests classify added/deleted/net characters and lines by artifact category.
   `GROSS_WRITTEN` includes correction/churn only when write evidence exists and otherwise returns
   `NOT_OBSERVED`; neither metric is provider output tokens.
10. Cost tests keep exact model/revision/strength/service/pricing groups separate, apply distinct
    uncached/cache-read/cache-write/output buckets, preserve native currency and produce
    `UNPRICED`/`UNPRICED_LOCAL` without FX invention.
11. No report runs before explicit user request. Active evidence yields receipt/digest-bound
    `PARTIAL / AS_OF`; sealed evidence yields `FINAL`. Identical inputs verify one report ID.
12. Counterfactual input contains all and only eligible Git-tracked text at the exact snapshot,
    excludes Johnny optimization inputs and forbidden paths, performs zero inference and returns
    `BASELINE_CONTEXT_OVERFLOW` rather than truncating.
13. The primary result uses exact same model/task/pricing identity,
    `EQUAL_OUTPUT_ASSUMPTION` and `SAME_EXISTING_CACHE_ASSUMPTION`; cold-cache and same-ratio
    scenarios are separate and visibly projected.
14. Tokenizer evidence tests keep provider dry count, exact local tokenizer, versioned proxy and
    character-only modes distinct. Proxy results are estimated; character-only cannot claim
    token or cost savings; observed and projected values never mix.
15. Terminal/Markdown/JSON/CSV/SVG renderers write aggregate-only output to stdout and bounded
    diagnostics to stderr. No production CLI accepts an output/raw storage path. Bar charts show
    Johnny versus no-takeover input, observed/projected marks, role/model/strength and ticket
    trends.
16. User-requested calculation respects the exact low-resource/local-model reservation plan,
    resolves only requested receipt branches and performs no role wake, schedule or recurring
    scan.
17. The legacy paired-run/median POC remains testable historical behavior but cannot be used as
    the default Revision-03 controlled-target claim or trigger provider model calls.
18. All public contracts pass strict construction/roundtrip/rejection matrices and
    `mypy --strict`; boundary adapters normalize dynamic input without `Any` entering the core.
19. Adapter-composition and precedence tests prove each operation's exact payload/result
    nullability, first-failure mapping, injected-only I/O ports and the non-injectability of the
    legacy raw-path store/CLI in controlled-target mode.

## Approval

The project owner explicitly authorized the baseline implementation on
`2026-08-03` for personal local-project validation and approved the exact
Revision 02 project-isolation correction on `2026-08-15` under
`CHG-20260815-024`. The Senior may decompose/open tickets for that exact
closure. Approval creates no dispatch receipt and grants no source,
target-project, telemetry-write, cleanup or external-effect authority. The
legacy raw-path POC remains prohibited for controlled-target use until the
approved tickets are implemented, independently reviewed and integrated.

Revision 03 was drafted under `CHG-20260816-025` and `ADR-20260816-014` after owner-approved
Architecture/Grill convergence. Its exact text remains `OWNER_REVIEW_REQUIRED`. It supersedes
the matched-provider-run default only after approval and grants no Senior decomposition, ticket,
dispatch, telemetry write, provider call, report execution or target-project authority.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `72438a30a4ad698be33292de8d63a7f2dc289daf` | Drafted Revision 02 to replace caller-selected target-local telemetry paths with a Johnny-owned opaque storage reference; owner approval pending. |
| 2026-08-15 | Project owner | Approved the exact Telemetry Storage Revision 02 and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-16 | Architecture owner / `main` / `2a8287831259243e230911e1082f0ec87895d3c5` | Drafted Revision 03 receipt-indexed runtime evidence, provider usage/cost, user-requested calculation and zero-inference no-takeover counterfactual under `CHG-20260816-025`; exact owner approval pending. |
