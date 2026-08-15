# Context Load Telemetry Context

| Field | Value |
| --- | --- |
| Feature | `context-load-telemetry` |
| Worktree | `root/main` |
| State | `BASELINE_DONE / REVISION_02_APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED` |
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

## Related sources

| Source | State | Decision |
| --- | --- | --- |
| `modules/spec/router-framework.md` | `APPROVED` | Reuse the Router State/Event/Profile and metadata-only Context contract. |
| `library/workflow_router/contracts.py` | `READY` | Extend only with strongly typed telemetry contracts. |
| `library/workflow_router/router.py` | `READY` | Reuse ContextResolver output without persisting packet text. |
| `tests/test_workflow_router.py` | `READY` | Preserve current router and citation invariants. |

## Acceptance evidence

- Typed telemetry records can be written to and restored from JSONL without raw source text.
- Paired baseline/router validation calculates reduction only from provider-reported input token data.
- Invalid evidence is reported fail-closed.
- Existing Router tests and strict type checking remain green.

## Owner-backlink status

Baseline feature implementation committed as `319ae97` (`feat: add router
context load telemetry`). Revision 02 storage isolation is approved for
reviewer ticket decomposition but is not implemented, reviewed or integrated;
the legacy raw-path API remains non-admitted for controlled targets.
