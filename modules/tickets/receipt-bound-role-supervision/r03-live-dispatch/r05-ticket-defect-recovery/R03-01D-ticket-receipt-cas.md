# R03-01D — TicketReceipt CAS store

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` / `R03-01D-CS-01` |
| Authority | `PRD-20260816-028` / `CHG-20260816-028`; [`REQ-20260816-028`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md); Revision 05 AC-44, AC-45; [`DEC-20260816-523`](DEC-20260816-523-r05-recovery-decomposition.md) |
| Context / dependency | [`Revision-05 Context`](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md); reviewed/integrated `R03-01C-CS-01`; then an exact owner-approved R03-01D grant |
| Model / resources | one `gpt-5.6-luna` / `xhigh` lane; integrated registry/state port, disposable owned root, and external typed-cache |
| Effect / XSS | canonical durable receipt state only; no delivery/claim settlement, task, host, target-project or external effect; `XSS_N/A` |

## Observable closure and exact writable scope

Issue and read one canonical `TicketReceipt` only from an exact approved record and live pending
descriptor. Same operation/request digest/candidate returns the prior receipt. A changed identity,
descriptor or generation, or a second `ACTIVE|QUARANTINED` receipt returns a finite conflict;
revocation readback precedes replacement. Registry generation and receipt state settle in one
R03-01B transaction. Storage failure, interruption and uncertain recovery never fall back to
memory or return/dispatch a receipt.

```text
library/local_orchestration/ticket_receipt_cas_store.py
library/local_orchestration/__init__.py
tests/test_ticket_receipt_cas_store.py
```

This module consumes the integrated registry and durable state port, owns no delivery/claim
behavior, makes no host call and cannot select a fake/process-local store or composition root.

## TDD and verification

| Cell | First red | Green proof |
| --- | --- | --- |
| `R03-01D-T01` issue/read CAS | `python -B -m unittest tests.test_ticket_receipt_cas_store.TicketReceiptCasTests` before store creation | exact issue/read and same-operation idempotence return the canonical stored receipt |
| `R03-01D-T02` conflict/revocation | `python -B -m unittest tests.test_ticket_receipt_cas_store.TicketReceiptConflictTests` before finite outcome reducer exists | descriptor/identity/generation conflicts and competing live receipt fail closed; revocation readback precedes replacement |
| `R03-01D-T03` restart/recovery | `python -B -m unittest tests.test_ticket_receipt_cas_store.TicketReceiptDurabilityTests` before durable transaction integration | new adapter over the same root proves the one-live-receipt invariant after interruption/restart |
| `R03-01D-T04` source gate | `python -B -m unittest tests.test_ticket_receipt_cas_store.TicketReceiptSourceGateTests` before store exists | reverse memory-fallback, fake-store, claim/host-call, broad-catch, dynamic/bypass mutations turn red then restore |

Run focused tests and strict explicit-package-base mypy over this file/test and direct R03-01A/B/C
contracts, with an owner-owned external cache; then compile, diff/scope/porcelain/cache readback.
Independent review uses a detached Senior-owned disposable clone/root and its full matrix.

## Return and rollback

One implementation commit is limited to the listed files. Return typed `COMPLETED`, `BLOCKED`, or
`CHANGE_DETECTED` with named evidence. Revert its later integration commit for rollback; remove
only proven owned runtime state. Only independent approval/integration of this closure permits
later R03-02 real-receipt admission; it does not itself issue a live dispatch.
