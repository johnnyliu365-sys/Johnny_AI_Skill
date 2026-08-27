# Context Load Telemetry Context

| Field | Value |
| --- | --- |
| Feature | `context-load-telemetry` |
| Worktree | `root/main` |
| State | `BASELINE_DONE / REVISION_02_APPROVED / REVISION_03_PROVIDER_USAGE_ARCHITECTURE_ACCEPTED / REVISION_04_LOCKED_STORAGE_APPROVED / REVISION_05_CLASSIFIED_FILE_LOCK_CAPABILITY_APPROVED / REVISION_06_LOCK_PORT_ADAPTER_AUTHORIZED / REVIEWER_DECOMPOSITION_AUTHORIZED` |
| In scope | Router context measurement, metadata-only JSONL evidence, baseline/router comparison, local validation, and Johnny-owned opaque telemetry storage. |
| Out of scope | Raw prompt capture, source text or path persistence, provider credentials, a production Agent supervisor, target-local Johnny storage, or changes to target company repositories. |

## Confirmed decisions

- A measurement record must contain no source text, user prompt, secret, or raw URI. It retains only typed identifiers, revisions, spans, SHA-256 fingerprints, counts, and provider usage metadata.
- A router run measures a `ContextPacket` locally and records the associated `ContextView` metadata. A baseline run uses the same record schema but has no `ContextView`.
- A valid comparison requires the same comparison group, attempt number, project snapshot, provider, and model. Provider-reported input tokens are required to claim actual context reduction.
- A budget breach, undeclared source, mismatched comparison pair, missing usage, or quality regression makes the validation report fail rather than produce a misleading reduction claim.
- Raw JSONL is Johnny-owned per-user control state. A target repository receives
  no `.johnny-router`, ignore rule or telemetry path. Only a separately
  authorized sanitized aggregate review artifact may enter the target's normal
  evidence tree.
- The current raw-path `JsonlContextUsageStore` is legacy POC behavior. It is not
  admitted for controlled-target use and requires an approved Revision 02
  implementation ticket before production use.
- Actual provider usage has three distinct report classes: `LOAD_ESTIMATE`,
  `OBSERVED_USAGE`, and `MATCHED_REDUCTION`. Only the last may say that tokens were reduced;
  it requires two fresh isolated, randomized-order, quality-preserving runs with identical
  provider/model/configuration/snapshot/task bindings.
- A provider adapter receives one terminal host event ephemerally, validates it into typed
  metadata and discards its raw contents. Missing or malformed usage is named unavailable, not
  zero or an estimate. Host probes are paid external effects and require their own ticket-bound
  owner authority.
- The opaque storage contract now fixes the lifecycle/operation matrix and validation precedence.
  `TelemetryStoragePort.execute` is the sole caller contract; its `READ` response is a complete,
  immutable metadata-only record tuple, and the Johnny-root composition adapter is the only path
  resolver and user of the legacy codec. `DETACHED` and `REMOVED` stores cannot be recreated by a
  telemetry request.
- Cost and billing claims remain out of scope. Provider token reduction cannot be converted to
  money without a separately approved pricing requirement.
- Johnny-owned durable telemetry storage is a cross-process boundary. Every operation must
  acquire an exact opaque-stream lock before its final ownership/lifecycle/containment admission;
  unavailable ownership is distinct from `LOCK_CONTENDED`, and lock contention performs no
  stream or ledger effect. The existing `exclusive-file-lock` catalog card is READY only for
  blocking exclusion and remains forbidden for direct telemetry `try_acquire` use until its
  separately approved classified nonblocking successor closure is delivered and selected.
- The classified successor preserves all six current blocking consumers. Its new API may return
  only `ACQUIRED` or `CONTENDED`: Windows contention is the locally observed immediate
  `LK_NBLCK`/`errno.EACCES` outcome after a successful open; unrelated `OSError` values remain
  errors. This infrastructure closure is not a telemetry adapter and does not produce telemetry.
- Revision 06 authorizes exactly one local `TelemetryStorageLockPort` implementation. It derives
  one opaque lock identity and one internal dedicated path from the complete immutable storage
  reference, uses the delivered `exclusive-file-lock` only after
  `path-containment` rejects redirected roots/ancestors, and returns the existing strict acquire
  and release DTOs. The adapter may hold lock-file state only; it does not read or create a
  ledger/stream, invoke `JsonlContextUsageStore`, re-admit a storage operation, or touch a target
  project. The future storage adapter retains all preliminary and under-lock ledger/lifecycle/
  containment admission.

## Related sources

| Source | State | Decision |
| --- | --- | --- |
| `modules/spec/router-framework.md` | `APPROVED` | Reuse the Router State/Event/Profile and metadata-only Context contract. |
| `library/workflow_router/contracts.py` | `READY` | Extend only with strongly typed telemetry contracts. |
| `library/workflow_router/router.py` | `READY` | Reuse ContextResolver output without persisting packet text. |
| `tests/test_workflow_router.py` | `READY` | Preserve current router and citation invariants. |
| `doc/adr/ADR-20260824-019-provider-usage-telemetry-evidence.md` | `ACCEPTED` | Defines the Revision 03 storage, host-evidence, comparison and probe boundary. |

## Acceptance evidence

- Typed telemetry records can be written to and restored from JSONL without raw source text.
- Paired baseline/router validation calculates reduction only from provider-reported input token data.
- Invalid evidence is reported fail-closed.
- Existing Router tests and strict type checking remain green.

## Owner-backlink status

Baseline feature implementation committed as `319ae97` (`feat: add router
context load telemetry`). Revision 03 now authorizes decomposition of pure storage and
provider-event-admission tickets. No host usage schema has yet been proven, no real provider usage
has been collected, and the legacy raw-path API remains non-admitted for controlled targets.

Revision 04 is authorized by `PRD-20260827-041` / `CHG-20260827-041` and
`ADR-20260827-022`. It blocks Ticket 06's pre-lock candidate from integration and requires a
strict lock-contract closure before any durable adapter or actual Accounting data path.

Revision 05 additionally authorizes the classified nonblocking file-lock prerequisite under
`ADR-20260827-024`. Its only permitted implementation is the reusable primitive and disposable
process fixtures; Ticket 06 remains blocked until a later lock adapter is separately opened.

Revision 06 now authorizes that independently scoped local lock-port adapter from the current
authority line. It selects `exclusive-file-lock@60d2ab0` and the existing containment predicate
newly cataloged as `path-containment@42b2be1`; it does not reactivate or reuse Ticket 06's
preserved candidate.
