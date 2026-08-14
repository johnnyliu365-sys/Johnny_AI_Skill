# Ticket 05C2A Code Review — Codex Compensation Observation Admission

| Field | Value |
| --- | --- |
| Decision | `CHANGES_REQUESTED / SAME_LANE_CORRECTION` |
| Finding | `CR-174` |
| Classification | `TICKET_DEFECT + IMPLEMENTATION_DEFECT + EVIDENCE_DEFECT` against revision-01 A5/A6 |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2A-01` / A1-A8 revision 02 |
| Implementation | `3b1706889fbc6e5323ce9ba561825f908b4e0dca` |
| Docs-only handoff | `9f25ef56892b9b9a9a51e470838a383c0f17e500` |
| Dispatch registry | `0ee852309cef799ccac94b5dd5d59cd3c4fd0a7b` / schema gate passed |
| Immutable archive SHA-256 | `756843E8AF749F9D160A24A423CEB4F8CC9ED0A632678D8B42AC00A100E09817` |
| XSS | `XSS_NOT_APPLICABLE` |

## Scope and independent verification

- The implementation descends from the exact registry and changes only the
  three frozen paths; the handoff changes only `doc/WorkProgressReport.md` and
  carries PRG-390 once. The submitted lane is clean and exactly three
  registered worktrees remain.
- In a reviewer-owned immutable TEMP export, focused composition tests passed
  `17/17`, explicit serial discovery passed `482/482`, strict mypy passed all
  `146` Python source files, and in-memory compilation passed all `146` files.
  The external mypy cache was removed and read back absent.
- Exact operation admission, request-before-response precedence, five-operation
  dispatch, public exports and the strict frozen rejection DTO conform to the
  frozen contract. No capability/callable/effect admission, `Any`,
  `type: ignore`, broad catch, renderer or XSS sink was found.
- The independent A5 corruption matrix failed: adding non-empty
  `__pydantic_extra__` or `__pydantic_private__` to each exact successful
  response still returned `CONFIRMED` or `PROVED_ABSENT` for all five
  operations.

## CR-174

The public observer dispatches directly to the integrated private normalizers,
but those normalizers validate visible fields without requiring exact original
state on the response envelope, list entries or optional marketplace source.
Consequently, caller-corrupted Pydantic objects can be accepted as affirmative
removal/absence evidence. In a removal path, unvalidated hidden state must not
be allowed to prove that an owned plugin, marketplace or installed path is gone.

The committed `test_a5_response_subclasses_constructed_values_and_traps_remain_finite`
covers subclass, missing constructed fields and one trap. It has no direct
top-level extra/private matrix and no representative nested entry/source
injection, so the green suite does not intercept the defect.

Revision 01 also created a ticket contradiction: A5 explicitly required
extra/private response coverage while the frozen contract prohibited any
mapping-semantic change without separating valid response semantics from
corrupted instance storage. Revision 02 resolves that reviewer-owned defect:
ordinary validated mappings remain unchanged; corrupted storage maps through
the same shared normalizers to existing conservative finite results.

## Required bounded correction

On the same ticket, owner, worktree, branch, allocation, receipt and correlation:

1. Change only `library/local_orchestration/codex_compensation_composition.py`
   and `tests/test_codex_compensation_composition.py`; keep package exports
   byte-identical.
2. Before any affirmative result, require exact original Pydantic state for the
   top-level response and for admitted nested plugin/marketplace entry/source
   models. Use fixed storage only; do not invoke caller descriptors,
   serialization, equality or dynamic member lookup.
3. Map corrupted removal proofs to existing `DECLARED_FAILURE`, corrupted list
   envelopes/entries/sources to existing `MALFORMED`, and corrupted installed
   path proof to existing `MALFORMED`. Do not add an enum/result or broaden the
   public contract.
4. Add a bounded table-driven CR-174 matrix for both extra/private top-level
   state across all five operations and representative nested entry/source
   state. Reverse the shared original-state guard and require the named test to
   turn red, then restore exact bytes.
5. Rerun focused/full serial unittest, strict full-tree mypy, in-memory compile,
   source/scope/diff/ancestry/topology/residue checks and the existing A7
   reversals. Append only reserved PRG-20260814-393 in a WPR-only handoff.

No new branch/worktree/helper, public API, effect, live Codex/host/target-project
access, push/staging publication, package/build/install, Secret, release or
deployment is authorized.
