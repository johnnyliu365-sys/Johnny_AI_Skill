# Ticket 05B4B2E6A Code Review - Foreign-State Isolation Acceptance

| Field | Value |
| --- | --- |
| Decision | `CHANGES_REQUESTED / EVIDENCE_DEFECT` |
| Finding | `CR-172` - owned marketplace/plugin uniqueness gates are not independently locked |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E6A-01` / A1-A8 revision 02 |
| Implementation | `d3b3174b97a9c1fd52d2e861fd10be83c8d10033` |
| Docs-only handoff | `ec0e80b45cf998378c420787ef16cdaf08d98c34` |
| Correction registry | `548166560b97e0eb81cecc80ad7dd3cb1405ce49` |
| Immutable archive SHA-256 | `52CD7DCD2872EDD97D904621688CA8B341B2FF0143364F176137AF2077E22611` |
| Restored adapter source blob | `cfba3269c3314b5cf783869712697f71f80514f4` |
| XSS | `XSS_NOT_APPLICABLE` |

## Scope and baseline

- The implementation and handoff ancestry and exact three-path/WPR-only scopes
  match the revision-02 dispatch.
- Owner1 branch is clean at the exact handoff and remains bound to the same
  permanent worktree; no helper or additional worktree was used.
- Independent immutable focused direct-adapter plus E6A tests pass `16/16`.
  The submitted full `450/450`, strict mypy `143/143` and compile `143/143`
  evidence is coherent, but terminal approval stops at the adversarial defect.

## CR-172

`_fresh_lists_match` correctly requires one owned marketplace and one owned
installed plugin. The direct negative test, however, supplies only two coupled
cases: both owned collections are zero, or both are duplicate. Consequently:

1. Removing the plugin count gate while retaining the marketplace gate leaves
   focused `16/16` green.
2. Removing the marketplace count gate while retaining the plugin gate also
   leaves focused `16/16` green.

The tests therefore do not prove either half of A2/A8 independently. A future
regression could delete one uniqueness check without detection. Both reviewer
mutations were reversed and the source blob restored exactly before the
immutable TEMP export was removed.

## Required correction

Change only `tests/test_codex_registration_oracle_adapter.py` so the negative
matrix independently proves these four cases while the opposite side remains
exactly one: marketplace zero, marketplace duplicate, installed plugin zero,
installed plugin duplicate. Keep the positive foreign/available case and the
E6A acceptance test unchanged. Independently remove each production gate and
show its matching matrix turns red, restore exact bytes, then rerun focused,
full, strict mypy, compile and residue gates.

This is an `EVIDENCE_DEFECT`, not a product defect, ticket defect or requirement
change. Same ticket, owner, branch, worktree, allocation, receipt, correlation
and implementation commit history remain valid; only an additive test
correction plus a new WPR-only correction handoff is required.
