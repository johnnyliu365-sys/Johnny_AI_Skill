# Ticket 05B4B2E3B Codex Oracle Owned-Absence Preservation Code Review

## Review decision

`CHANGES_REQUESTED / IMPLEMENTATION_DEFECT / CR-161`

The accepted-lifecycle behavior is correct, but the parent absence boundary
uses `isinstance` for `CodexPluginList`. A reviewer adversarial probe supplied
a subclass payload inside a constructed accepted response and received
`OracleAbsent`. Exact staging evidence must reject subclass and
constructed-invalid response shapes before absence can be proved.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e3b-codex-oracle-owned-absence-preservation`; `CLOSURE-LOCAL-INSTALL-T05B4B2E3B-01`; A1-A7 |
| Owner / branch | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; `codex/implementation-codex-owned-absence-05b4b2e3b` |
| Chain | Dispatch `59a30b92b1dda90a74f6e8dccd90bbfc25d0e207` -> implementation `790b5a0d51b9e7cd909e386803e8923bc0372dcc` -> docs-only handoff `04b4ff10df73cb6b3c743daf0a249f364736de7f` |
| Scope | Implementation is exactly the three authorized staging-oracle/test paths; handoff is WPR-only. Submitted lane is clean. |

## Closure verification

| Gate | Result |
| --- | --- |
| A1-A2 | PASS: first red reproduced deletion; child now retains state and returns fresh foreign plugin truth. |
| A3 | FAIL / CR-161: `isinstance(response.payload, CodexPluginList)` admits subclass payloads. Reviewer probe returned `OracleAbsent` for `DerivedPluginList`. |
| A4-A5 | PASS: valid empty state persists until teardown; foreign state and payload bytes remain identical. |
| A6 | PARTIAL: committed missing/tampered/state-residue/topology cases block, but subclass/constructed-invalid response evidence is not finite. |
| A7 | PASS for submitted three reversals and exact restoration; reviewer focused suite passed 23/23 in an owned external temp base. |
| CodeReview.md exact type/evidence | FAIL: absence success is reachable from a non-exact protocol payload. |
| XSS | `XSS_NOT_APPLICABLE`: no renderer, HTML/DOM or JavaScript context. |

## Required correction

Same ticket/owner/worktree/branch/allocation/receipt. Add one additive source/test
commit in the original `oracle.py` and focused-test scope. Require exact
`CodexProtocolAccepted` and exact `CodexPluginList`, revalidate the payload
before reading it, and finitely block subclass, constructed-raw,
missing/extra/injected-state and nested malformed entries. Reverse the exact
type/revalidation gate and restore exact blobs. Then return a WPR-only handoff.
