# R03-01C — Approved-artifact registry

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / READY_LOW_MODEL / BLOCKED / NON_DISPATCHED` / `R03-01C-CS-01` |
| Authority | `PRD-20260816-028` / `CHG-20260816-028`; [`REQ-20260816-028`](../../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-028.md); Revision 05 AC-43, AC-45; [`DEC-20260816-523`](DEC-20260816-523-r05-recovery-decomposition.md) |
| Context / dependency | [`Revision-05 Context`](../../../../../doc/context/receipt-bound-role-supervision/revisions/rev05-r03-ticket-defect-recovery.md); reviewed/integrated `R03-01B-CS-01`; then an exact owner-approved R03-01C grant |
| Model / resources | one `gpt-5.6-luna` / `xhigh` lane; integrated durable-state port plus disposable owned root and external typed-cache |
| Effect / XSS | durable approved-artifact state only; zero receipt, task, claim, host, target-project or external effect; `XSS_N/A` |

## Observable closure and exact writable scope

Register and read exactly one immutable `ApprovedDispatchArtifactRecord` through the integrated
generation-CAS state port. Same operation and bytes are idempotent. Any changed identity bytes,
stale generation, closed record, unavailable/corrupt store or failed durable settlement returns
the named finite result and makes zero downstream receipt/host calls. Restart and interruption
proof reconstruct a concrete durable adapter over the same disposable owned root.

```text
library/local_orchestration/approved_dispatch_artifact_registry.py
library/local_orchestration/__init__.py
tests/test_approved_dispatch_artifact_registry.py
```

The registry consumes R03-01A/01B contracts read-only and is the only artifact-record behavior
owner. It cannot reimplement the journal, use an in-memory map, accept an untyped blob, issue a
receipt, or select a composition root.

## TDD and verification

| Cell | First red | Green proof |
| --- | --- | --- |
| `R03-01C-T01` registration/read | `python -B -m unittest tests.test_approved_dispatch_artifact_registry.ApprovedArtifactRegistryTests` before registry creation | exact registration/read and identical idempotence preserve the stored record |
| `R03-01C-T02` identity/failure matrix | `python -B -m unittest tests.test_approved_dispatch_artifact_registry.ArtifactIdentityFailureTests` before finite reducer exists | every changed identity, stale/closed/unavailable/corrupt outcome is finite and invokes no receipt port |
| `R03-01C-T03` restart/interruption | `python -B -m unittest tests.test_approved_dispatch_artifact_registry.ArtifactRegistryDurabilityTests` before durable-port use | new concrete adapter reopens the same root; interrupted transaction never reports registration |
| `R03-01C-T04` source gate | `python -B -m unittest tests.test_approved_dispatch_artifact_registry.ArtifactRegistrySourceGateTests` before registry exists | reverse fake/map/blob/receipt/host/dynamic/bypass mutations turn red then restore |

Run focused tests and strict explicit-package-base mypy over this file/test and direct R03-01A/B
contracts, with an owner-owned external cache; then compile, diff/scope/porcelain/cache readback.
Independent review uses an isolated disposable clone/root.

## Return and rollback

One implementation commit is limited to the listed files. Typed `COMPLETED`, `BLOCKED`, or
`CHANGE_DETECTED` returns named evidence. Revert its later integration commit to roll back;
runtime cleanup removes only registry-proved owned files. Completion unlocks only R03-01D.
