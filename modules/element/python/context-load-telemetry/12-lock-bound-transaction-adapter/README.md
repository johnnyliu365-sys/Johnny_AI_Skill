# Context-load telemetry 12 — Lock-bound transaction adapter

| Field | Value |
| --- | --- |
| Ticket | [`12-lock-bound-transaction-adapter.md`](../../../../tickets/context-load-telemetry/12-lock-bound-transaction-adapter.md) |
| Private implementation | `library/local_orchestration/telemetry_storage/johnny_owned_adapter.py` |
| Focused acceptance | `tests/test_johnny_owned_telemetry_storage_adapter.py` |
| Public contract | `library/local_orchestration/telemetry_storage/contracts.py` — unchanged |
| Dependencies | Ticket 09 exact lock port (`096d471`); Ticket 11 per-stream ledger (`e05f03a`) |
| Architecture / reusable selection | `ADR-20260827-027`; `exclusive-file-lock@60d2ab0` via local port; `path-containment@cf9e126` |

This is an index, not a source copy. Ticket 12 creates only the private lock-bound storage adapter
and its disposable-root tests. It does not bind composition, create a public provision API,
migrate the aggregate ledger, perform provider/host/target-project effects, publish or release.
