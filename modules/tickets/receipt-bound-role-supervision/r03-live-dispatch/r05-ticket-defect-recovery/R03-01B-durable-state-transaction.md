# R03-01B — Owned durable state transaction

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` / `R03-01B-CS-01` |
| Authority | `PRD-20260816-028` / `CHG-20260816-028`; [`REQ-20260816-028`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md); Revision 05 AC-42, AC-45; [`DEC-20260816-523`](DEC-20260816-523-r05-recovery-decomposition.md) |
| Context / dependency | [`Revision-05 Context`](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md); reviewed/integrated `R03-01A-CS-01`; then an exact owner-approved R03-01B grant |
| Model / resources | one `gpt-5.6-luna` / `xhigh` lane; Windows disposable owned-root fixture and external typed-cache only |
| Effect / XSS | Johnny-owned local runtime state only; no task, worktree, host, target-project, network, provider, or external effect; `XSS_N/A` |

## Observable closure and exact writable scope

Implement one concrete standard-library Windows adapter for the AC-41 read/CAS port. It accepts
only an opaque admitted `JohnnyOwnedStateRootCapability`, derives its own digest partition and
uses exactly the AC-42 checkpoint, bounded framed journal, lock and same-directory temporary
layout. One nonblocking one-byte lock attempt, prepared-frame flush, checkpoint atomic replace,
committed-frame flush, readback and finite recovery are one transaction closure.

```text
library/local_orchestration/live_dispatch_durable_state.py
library/local_orchestration/live_dispatch_state_root.py
library/local_orchestration/__init__.py
tests/test_live_dispatch_durable_state.py
```

Production construction cannot select a Protocol, map, singleton, test fake, database, service,
MCP, target path or raw locator. Contention, encoding/locking/I/O errors and ambiguous recovery
map only to AC-41 finite results; no broad catch, sleep, retry, timer, polling or heartbeat.

## TDD and verification

| Cell | First red | Green proof |
| --- | --- | --- |
| `R03-01B-T01` atomic generation CAS | `python -B -m unittest tests.test_live_dispatch_durable_state.DurableTransactionTests` before adapter creation | first write/read, identical operation, generation conflict and readback digest are exact finite results |
| `R03-01B-T02` lock/restart | `python -B -m unittest tests.test_live_dispatch_durable_state.DurableLockRestartTests` before lock/reopen implementation | two-process contention is `LOCK_UNAVAILABLE`; a newly constructed adapter over the same disposable root reads committed state |
| `R03-01B-T03` recovery | `python -B -m unittest tests.test_live_dispatch_durable_state.DurableRecoveryTests` before journal recovery exists | both interruption points, torn/mismatched frames and competing/open preparations settle only to named finite results |
| `R03-01B-T04` source/ownership gate | `python -B -m unittest tests.test_live_dispatch_durable_state.DurableStateSourceGateTests` before adapter exists | reverse fake-production, raw-path, unbounded-journal, broad-catch, retry/polling and target-persistence mutations turn red then restore |

Run focused tests and strict explicit-package-base mypy over the four listed files plus the
integrated R03-01A contract file, with an owner-owned external cache; then in-memory compile,
diff/scope/porcelain/cache readback. Disposable roots are deleted by the implementation owner;
review uses a separate Senior-owned disposable clone/root.

## Return and rollback

One implementation commit is limited to the listed files. `COMPLETED`, `BLOCKED`, and
`CHANGE_DETECTED` carry only typed evidence. Rollback reverts the later integration commit and
removes only adapter-proved owned runtime files. Completion unlocks only R03-01C admission.
