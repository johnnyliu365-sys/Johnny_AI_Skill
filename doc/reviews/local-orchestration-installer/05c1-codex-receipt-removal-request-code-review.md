# Ticket 05C1 Code Review — Codex Receipt Removal Request

| Field | Value |
| --- | --- |
| Decision | `CHANGES_REQUESTED / CORRECTION_REQUIRED` |
| Finding | `CR-173` — constructed-invalid invocation identity is compared before validation |
| Classification | `IMPLEMENTATION_DEFECT + EVIDENCE_DEFECT` against revision-02 R4 |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C1-01` / R1-R7 revision 02 |
| Implementation | `ec53d3af854348a2f7385e485d17f3e2a84b98d8` |
| Docs-only handoff | `fb748f4fd1b7d1f5862c55fa1484151602f174e0` |
| Control correction | `103ae5385e9571c8ebd7496145b945634738e99f` / `PRG-20260814-381` |
| Immutable archive SHA-256 | `6CA7429DC5CB9100BAB2E85564FDC5D092B0B1A82BFE5D7EE9F14F646636CDE9` |
| XSS | `XSS_NOT_APPLICABLE` |

## Scope and independent verification

- Dispatch registry `dd7f66d4535a03e55d8134febe8093f9b98cea72` is an ancestor
  of the implementation and WPR-only handoff. The implementation changes only
  the two frozen new paths plus export-only `__init__.py`; the handoff changes
  only `doc/WorkProgressReport.md`, with one PRG-380 occurrence.
- The owner2 worktree is clean on the exact 05C1 branch/handoff and remains the
  only owner of the existing permanent lane. Exactly three worktrees exist.
- In the reviewer-owned immutable export, focused tests pass `12/12`, the
  explicit serial full suite passes `474/474`, strict mypy passes `146` source
  files and compilation passes. No forbidden dependency, renderer/XSS sink,
  host key, port/effect or target-project access was found.
- Reviewer reversals independently changed the receipt-identity error gate,
  source mapping and plugin mapping; their named tests turned red. The touched
  export was discarded and the same verified archive was re-expanded, restoring
  source/test SHA-256 to `0E6F4FA1BA909EEF5303945FB21EDAC1C0A68D09A37F84CE5BBF24AA09EF6D7E`
  and `805654497CE96569470646648411D09CC059A5A0496626361EFE60515247FFAC`.

## Closure mapping

| Item | Result |
| --- | --- |
| R1/R2 | Exact receipt succeeds and all ten manifest values, including the two renamed fields, map correctly. |
| R3 | Valid unequal installation IDs return `RECEIPT_MISMATCH`. |
| R4 | **Fail:** a constructed-invalid invocation root returns `RECEIPT_MISMATCH` instead of `INVALID_INVOCATION`; the committed test requires the same wrong result. Other null/type/state matrices are finite. |
| R5 | Exact-type admission rejects subclass traps before descriptor, equality or serialization hooks. |
| R6 | All three reviewer reversals turn their named committed tests red. |
| R7 | Focused/full/type/compile/scope/topology checks pass; only CR-173 blocks approval. |

## CR-173

`build_codex_receipt_removal_request` reads raw installation/root strings and
compares them to the rebuilt receipt before rebuilding and validating the
invocation values. Consequently, an `InstallRoot.model_construct` value such as
`%LOCALAPPDATA%\\OtherJohnnyAIWorkflow` has exact-looking storage, reaches the
identity comparison and returns `RECEIPT_MISMATCH`. Revision-02 R4 requires
invalid invocation data to fail as `INVALID_INVOCATION`; there cannot be a
second valid `InstallRoot` under the approved canonical-root contract.

The direct test `test_R3_root_mismatch_is_receipt_mismatch` and PRG-380 claim
the same incorrect classification, so the evidence currently makes the defect
green instead of intercepting it.

## Required bounded correction

On the same ticket, owner, worktree, branch, allocation and receipt:

1. In `codex_receipt_removal_request.py`, rebuild/validate invocation
   `InstallationId` and `InstallRoot` before identity comparison. Remove the
   raw pre-validation comparison/helper if it becomes unused. Only two valid
   unequal installation IDs may produce `RECEIPT_MISMATCH`.
2. In the direct test, replace the root-mismatch positive expectation with
   bounded invalid-invocation cases for constructed noncanonical root and
   constructed invalid installation ID; add/retain invalid receipt-root
   evidence as `INVALID_RECEIPT`.
3. Rerun focused/full/strict/compile and the three unchanged reversals. Append
   one correction WPR record that explicitly supersedes only PRG-380's root
   classification claim.

No export/API redesign, new path, new branch/worktree, new error code or 05C2
behavior is authorized. The control-side missing language/root contradiction is
already corrected by revision 02 and is not an implementer finding.
