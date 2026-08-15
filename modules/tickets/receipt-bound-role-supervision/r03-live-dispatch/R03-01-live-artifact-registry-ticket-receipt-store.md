# R03-01 — Durable approved-artifact registry and TicketReceipt store

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / READY_LOW_MODEL / NON_DISPATCHED` / `R03-01-CS-01` |
| Authority | `PRD-20260816-026` / `CHG-20260816-026`; [`REQ-20260816-026`](../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-026.md); [`ADR-20260816-015`](../../../../doc/adr/ADR-20260816-015-live-receipt-dispatch-settlement.md); Revision 03 AC-24, AC-25, AC-29; [`DEC-20260816-521`](DEC-20260816-521-r03-live-dispatch-decomposition.md) |
| Context / baseline | `doc/context/receipt-bound-role-supervision/main.md` Revision 03 / `d183140d09a1a25912102b862a92ef9b3aa190ad` |
| Language / model / resources | Python 3.11; `python -m mypy --strict library tests`; one `gpt-5.6-luna` xhigh implementation lane; local disposable owned metadata-root tests only |
| Effect / XSS | installer-owned metadata only; no host/task/worktree/Git/target effect; `XSS_N/A` |

## Observable closure and contracts

Given strict metadata-only input, atomically register one immutable reviewed ticket/handoff
artifact and compare-and-swap issue/read the one canonical `TicketReceipt` for its
project/ticket. Identical registration/issuance is idempotent. Changed identity bytes,
stale/closed/unreadable record, descriptor mismatch, conflicting issuance or second
`ACTIVE|QUARANTINED` receipt returns only its named finite rejection. No task admission, claim or
gateway call occurs.

Create only:

```text
library/workflow_router/live_dispatch_contracts.py
library/local_orchestration/live_dispatch_metadata_store.py
library/local_orchestration/__init__.py
tests/test_live_dispatch_metadata_store.py
```

`live_dispatch_contracts.py` owns strict frozen contracts and pure validation for
`ApprovedDispatchArtifactRecord`, register/read requests/results, `TicketReceipt`, issue/read
requests/results, named IDs/digests, and the derived-only legacy projection.
`live_dispatch_metadata_store.py` owns `LiveApprovedDispatchArtifactRegistryPort` and
`TicketReceiptStorePort` over the injected installer-owned journal/checkpoint boundary.
Composition injects it; it must not select a process-local fake/map, singleton, environment read,
target-local path, host gateway or claim store. `TicketDispatchReceipt` is never accepted or
persisted as live authority.

Finite algebra: receipt lifecycle `ACTIVE|REVOKED|CLOSED|QUARANTINED`; artifact registration
`REGISTERED|ALREADY_REGISTERED|IDENTITY_CONFLICT|STORAGE_UNAVAILABLE`; artifact read
`FOUND|NOT_FOUND|STALE_REVISION|CLOSED|STORAGE_UNAVAILABLE`; issuance
`ISSUED|ALREADY_ISSUED|ARTIFACT_NOT_APPROVED|PENDING_DESCRIPTOR_MISMATCH|RECEIPT_CONFLICT|STORAGE_UNAVAILABLE`.
Success requires exact record/receipt and no failure; rejection requires exactly one failure and
no record/receipt. Named non-null IDs, revisions, digests, expected return and descriptor binding
are mandatory. Raw path/URI/source/prompt/Context/Secret/PII, expiry, empty/whitespace/extra or
coerced values, `Any`, `object`, cast, bypass constructors, dynamic lookup and broad catch fail
at the boundary.

## TDD / preflight

| Cell | First-red command | Green proof |
| --- | --- | --- |
| `R03-01-T01` receipt contract | `python -m unittest tests.test_live_dispatch_metadata_store.LiveTicketReceiptContractTests.test_public_ticket_receipt_round_trip_rejects_legacy_projection_and_second_live_receipt` fails before module creation | ordinary construction/JSON round trips cover every field/lifecycle and all nullability/bypass negatives |
| `R03-01-T02` registry | `python -m unittest tests.test_live_dispatch_metadata_store.LiveArtifactRegistryTests.test_identical_registration_is_idempotent_and_identity_byte_collision_fails_closed` fails before registry creation | exact registration, collision, stale/closed/unavailable and interruption cases are finite; earlier failure causes zero issuance calls |
| `R03-01-T03` CAS store | `python -m unittest tests.test_live_dispatch_metadata_store.LiveTicketReceiptStoreTests.test_issue_exact_is_compare_and_swap_on_pending_descriptor_and_survives_restart` fails before store creation | duplicate request returns the exact prior receipt; conflict/revocation/storage failure fails closed; settlement does not consume receipt |
| `R03-01-T04` source gate | `python -m unittest tests.test_live_dispatch_metadata_store.LiveDispatchMetadataSourceGateTests.test_contract_and_store_are_strict_typed_and_owned_metadata_only` fails before module creation | reverse-mutate every named bypass/raw-field/fake/target-persistence gate to red, then restore exact bytes |

Run focused tests, `python -m unittest discover -s tests`, `python -m mypy --strict library tests`,
in-memory `compile()` of changed files, `git diff --check`, and exact scope/porcelain/cache
readback. Tests create no production root.

## Return and rollback

One integration commit contains exactly this scope. Revert it to roll back; remove only
adapter-proved owned records, never target files or Git history. `COMPLETED` returns commit and
all matrix evidence; `BLOCKED` covers corrupt/unavailable metadata; `CHANGE_DETECTED` covers
changed authority. Completion does not dispatch anything.
