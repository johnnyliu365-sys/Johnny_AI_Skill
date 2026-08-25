# Ticket 05 — profile and bridge alignment

| Field | Value |
| --- | --- |
| Ticket ID | PAI-05-PROFILE-AND-BRIDGE-ALIGNMENT |
| State | COMPLETED / ALREADY_SATISFIED / NO_SOURCE_MUTATION |
| Dependencies | PAI-01 through PAI-04 accepted |
| Source specification | Project authority integration SPEC Revision 05, ticket order item 05 |
| Planning baseline | main at b6353ac5a79ce2fd968862b55184ea04eeeeb1eb |
| Writable-source status | No additional writable/test seam is required: PAI-01 already integrated the complete finite bridge capability type. |
| Effect boundary | Documentation/control-plane alignment only when later admitted; no runner, queue, receipt issuer, polling, wake probe, or host effect. |

## Vertical closure reserved

Preserve separate maturity, assurance, and topology axes; require profile-scaled meaningful
counter-mutations; and align same-lifetime reviewer wait, review, and guarded integration with
the bridge-free rule. Cross-lifetime capability remains exactly NOT_REQUIRED, AVAILABLE, or
UNAVAILABLE; UNAVAILABLE means owner-mediated artifact relay and never a fabricated wake.

This leaf is intentionally non-dispatchable until an approved source/test-seam revision supplies
its exact writable boundary and verification. It may not turn cross-lifetime supervision into a
synchronous precondition or authorize any effect.

## Closure evidence

PAI-05 introduces no duplicate source change. PAI-01 was integrated at
`6df6885ea093f1e37899f5252f8e4a1cc4feadb9` and its public
`BridgeCapability` is already the exact closed three-state type:
`NOT_REQUIRED`, `AVAILABLE`, and `UNAVAILABLE`. The package exports that type and the current
production source has no other `BridgeCapability` consumer that could collapse
`NOT_REQUIRED` into `UNAVAILABLE`.

The reviewer re-read the integrated source and public export surface, then ran
`python -m pytest tests/test_project_authority_contracts.py -q` on 2026-08-25: **7 passed**.
The remaining profile/governance prose alignment is expressly deferred to PAI-07, which is the
release-bearing ticket; this closure does not alter skills, payload, or plugin version.
