# R03-01A — Durable metadata contract freeze

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` / `R03-01A-CS-01` |
| Authority | `PRD-20260816-028` / `CHG-20260816-028`; [`REQ-20260816-028`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md); Revision 05 AC-41, AC-45; [`DEC-20260816-523`](DEC-20260816-523-r05-recovery-decomposition.md) |
| Context / dependency | [`Revision-05 Context`](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md); reviewed/integrated `R03-00-CS-01`; then an exact owner-approved R03-01A grant |
| Model / resources | one `gpt-5.6-luna` / `xhigh` lane; one fresh ticket-bound ContextView; external typed-cache and no filesystem runtime root |
| Effect / XSS | pure constructor/validator/serialization closure; no filesystem, lock, registry, receipt, claim, host, Agent, target, or external effect; `XSS_N/A` |

## Observable closure and exact writable scope

Create strict ordinary constructors, validators and canonical serialization for AC-41
`LiveDispatchMetadataState`, read/write request/results, generation, partition, operation,
digest, journal phase, artifact-record and receipt/claim tuple types, plus the finite owned-root
capability admission result. Every success variant has exact required values and no failure;
every rejection has one finite failure and no state. `MetadataPartitionRef` derives from
validated project/ticket identity and is never a path. No storage port is called.

```text
library/workflow_router/live_dispatch_metadata_contracts.py
library/workflow_router/__init__.py
tests/test_live_dispatch_metadata_contracts.py
```

The contract module may expose protocols and opaque type boundaries, but no process-local map,
filesystem locator, environment read, serializer bypass, `Any`, `object`, cast, dynamic lookup,
or test-factory import may cross the public boundary. Production composition remains absent.

## TDD and verification

| Cell | First red | Green proof |
| --- | --- | --- |
| `R03-01A-T01` ordinary contract | `python -B -m unittest tests.test_live_dispatch_metadata_contracts.ContractRoundTripTests` before the production module exists | every public input/result/state ordinary construct → canonical JSON → reconstruct round trip succeeds |
| `R03-01A-T02` finite failures | `python -B -m unittest tests.test_live_dispatch_metadata_contracts.ContractFailureMatrixTests` before finite result algebra exists | wrong enum/nullability/tuple/digest/identity and success-with-failure or failure-with-state are rejected |
| `R03-01A-T03` partition/capability | `python -B -m unittest tests.test_live_dispatch_metadata_contracts.PartitionCapabilityTests` before derivation/admission exists | invalid identity, ledger mismatch, root mismatch and unavailable are finite; no raw locator is exposed |
| `R03-01A-T04` strong-type gate | `python -B -m unittest tests.test_live_dispatch_metadata_contracts.ContractSourceGateTests` before the module exists | bounded reverse mutations for `Any`, cast, dynamic lookup, bypass construction and raw path turn red then restore |

Run the focused command and
`python -m mypy --strict --explicit-package-bases --no-incremental --cache-dir <owner-external-cache> library/workflow_router/live_dispatch_metadata_contracts.py tests/test_live_dispatch_metadata_contracts.py`,
in-memory compile, `git diff --check`, exact scope/porcelain/cache readback. Independent review
runs its full matrix only in a detached Senior-owned disposable clone.

## Return and rollback

One implementation commit is limited to the listed files. `COMPLETED` returns the commit and
named evidence; `BLOCKED` returns a finite contract/preflight blocker; `CHANGE_DETECTED` returns
to change control. Revert that one future commit for rollback. Completion unlocks only R03-01B
admission, not a grant or dispatch.
