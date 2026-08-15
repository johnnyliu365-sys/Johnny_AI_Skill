# Context Load Telemetry Context

| Field | Value |
| --- | --- |
| Feature | `context-load-telemetry` |
| Worktree | `root/main` |
| State | `BASELINE_DONE / REVISION_02_APPROVED / REVISION_03_OWNER_REVIEW_REQUIRED` |
| Requirement / ADR | `PRD-20260803-006`, `PRD-20260816-025` / `CHG-20260803-006`, `CHG-20260816-025` / `ADR-20260815-013`, `ADR-20260816-014` |
| In scope | Receipt-indexed runtime evidence, provider usage/cost metadata, user-requested itemized report calculation, zero-inference no-takeover counterfactuals, charts and Johnny-owned opaque telemetry storage. |
| Out of scope | Raw prompt/source/path persistence, Provider credentials, Agent-estimated actual usage, automatic reports, baseline inference runs by default, target-local Johnny storage, or changes to target company repositories. |

## Confirmed decisions

- A measurement record must contain no source text, user prompt, secret, or raw URI. It retains only typed identifiers, revisions, spans, SHA-256 fingerprints, counts, and provider usage metadata.
- Every model call records provider-reported input, cached-input, optional cache-write-input and
  output tokens when available, plus role, exact model/revision, capability tier, reasoning
  effort, service tier, price revision and a `TicketReceipt` or `StageWorkReceipt` reference.
  Missing provider usage is `USAGE_NOT_REPORTED`; an Agent estimate never replaces it.
- Runtime operation stores only a small `RuntimeEvidenceManifest` with immutable references to
  Context exposure, interactive model-visible reads, Git write/diff results and provider usage.
  It performs no continuous aggregate or report calculation.
- The Johnny Composition Root injects ownership/segment/event/provider/Git/tokenizer/pricing/
  stdout ports. Storage error precedence and operation-specific result nullability are closed;
  the legacy caller-path store/CLI is test-fixture-only and cannot enter controlled-target
  composition.
- When the user requests a report, a script starts from the receipt and recalculates each
  referenced item. Repeated exposure counts repeatedly for cumulative input while unique-source
  and repeated-read totals are shown separately. Tool-internal Git/test/compiler/mypy/Docker I/O
  is resource evidence, not model tokens.
- `FINAL_DELIVERED` comes from the exact baseline-to-result Git diff by artifact category.
  `GROSS_WRITTEN` requires write/commit evidence and may be `NOT_OBSERVED`. Source characters are
  never labeled provider output tokens.
- The default no-takeover baseline uses the same Git snapshot and eligible Git-tracked text,
  excludes Johnny Router/skill/Context-management inputs and performs zero model calls.
  Projected output equality and cache behavior are explicit assumptions. Provider dry count,
  exact local tokenizer, versioned proxy tokenizer and character-only modes remain visibly
  distinct.
- Raw JSONL and report manifests are Johnny-owned per-user control state. A target repository receives
  no `.johnny-router`, ignore rule or telemetry path. Only a separately
  user-controlled shell redirection may place rendered output elsewhere; Johnny itself writes
  reports only to stdout and never into the target evidence tree.
- The current raw-path `JsonlContextUsageStore` is legacy POC behavior. It is not
  admitted for controlled-target use and requires an approved Revision 02
  implementation ticket before production use.

## Related sources

| Source | State | Decision |
| --- | --- | --- |
| `modules/spec/router-framework.md` | `APPROVED` | Reuse the Router State/Event/Profile and metadata-only Context contract. |
| `library/workflow_router/contracts.py` | `READY` | Extend only with strongly typed telemetry contracts. |
| `library/workflow_router/router.py` | `READY` | Reuse ContextResolver output without persisting packet text. |
| `tests/test_workflow_router.py` | `READY` | Preserve current router and citation invariants. |

## Acceptance evidence

- Typed telemetry records can be written to and restored without raw source text.
- User-requested calculation resolves one exact receipt/evidence revision and returns `PARTIAL`
  for active work or `FINAL` for sealed work without automatic rerun.
- Provider-observed usage, tokenizer-based projection, character counts and unobserved data are
  never mixed. Cost remains separated by exact model/strength/tier/pricing revision and native
  currency.
- Existing Router tests and strict type checking remain green.

## Owner-backlink status

Baseline feature implementation committed as `319ae97` (`feat: add router
context load telemetry`). Revision 02 storage isolation is approved but its Senior admission
returned `UPSTREAM_DECISION_REQUIRED`; it is not implemented, reviewed or integrated. Revision
03 supplies the missing architecture for owner review. The legacy raw-path API remains
non-admitted for controlled targets.
