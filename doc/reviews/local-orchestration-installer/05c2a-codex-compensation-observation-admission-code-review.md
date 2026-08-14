# Ticket 05C2A Code Review — Codex Compensation Observation Admission

| Field | Value |
| --- | --- |
| Decision | `APPROVED / READY_TO_MERGE` |
| Finding | `CR-174` — closed by same-lane revision-02 correction |
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

## Final correction review

The retained lane merged correction registry
`b5be2b0ee2b4cd3ac275738cec127f529f13f580` through the sole WPR-conflict merge
`dfe486b70f98e91d0580f28fbd63539d2042a769`. Additive correction
`5082cf9d34f3d555b12a2d34d9f21fff317e4568` changes exactly the composition
source and direct test; handoff `7ba15c9d5513d08d2d2f1ef23e4ca06d164d3525`
changes only WPR and carries PRG-393 once. The package export blob remains
identical to the initial implementation and the lane is clean with exactly
three worktrees.

From immutable handoff archive SHA-256
`1CE6A5A10019FCB4BB61EA152DA2C52C1325130A8451A82EA6015D93E9C5BE75`, the
reviewer independently obtained focused `18/18`, full serial `483/483`, strict
mypy over `146` source files and in-memory compile over `146` files. A separate
12-cell matrix covered direct `__dict__` injection, missing required field-set
state and valid omitted optional source behavior. Reversing the shared
extra/private-state guard made the committed CR-174 test fail all 16 named
corruption cases; restoring it returned exact Git blobs
`8cce40a989da3bda6b0b0b5663aae8aedec9925e` and
`13ad81bd0e13a914a1f7bed9c18e24d691fa3db3` and the test passed again.

CR-174 is closed. Exact original state is required before any removal
confirmation or absence proof, while valid optional-field omission and all
ordinary mappings remain compatible. No capability/callable/effect boundary,
renderer/XSS sink, live Codex/host/target-project action or residue exists.

## Guarded integration

The approved handoff was merged into control by
`e2e2fe986243fa64f7ce9a67903904310341597b`. Read-only merge-tree and the
actual merge found only the expected WPR conflict; the reviewer preserved
PRG-390 through PRG-394 once and did not resolve any source/test conflict.
Integrated focused `18/18` and strict mypy over `146` files pass. Ticket 05C2A
is `COMPLETE / APPROVED / INTEGRATED`.
