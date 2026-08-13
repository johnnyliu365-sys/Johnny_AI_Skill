# Ticket 05B4B2E6A Code Review - Foreign-State Isolation Acceptance

| Field | Value |
| --- | --- |
| Decision | `APPROVED / READY_TO_MERGE` |
| Finding | `CR-172` closed by independent owned marketplace/plugin uniqueness matrices |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E6A-01` / A1-A8 revision 02 |
| Implementation | `d3b3174b97a9c1fd52d2e861fd10be83c8d10033` |
| Docs-only handoff | `ec0e80b45cf998378c420787ef16cdaf08d98c34` |
| Test-only correction | `55b265b3904596c057feaa1127de9788122dfda7` |
| Correction handoff | `6f926995e0aa6250e34d095dd08406908c4834a2` |
| Correction registry | `548166560b97e0eb81cecc80ad7dd3cb1405ce49` |
| Correction dispatch registry | `d929114c24221493b2cbccc0eb8ddcaec2669b85` |
| Final immutable archive SHA-256 | `D83377B3C470D9EF1C1298E899188063BB87AC41630B0BB2E77BB4CA17166F5F` |
| Restored adapter source blob | `cfba3269c3314b5cf783869712697f71f80514f4` |
| XSS | `XSS_NOT_APPLICABLE` |

## Scope and baseline

- The implementation and handoff ancestry and exact three-path/WPR-only scopes
  match the revision-02 dispatch.
- Owner1 branch is clean at the exact handoff and remains bound to the same
  permanent worktree; no helper or additional worktree was used.
- Independent immutable focused direct-adapter plus E6A tests pass `16/16`.
  The final immutable archive passes direct-adapter plus E6A plus E6B focused
  `28/28`, full serial `462/462`, strict mypy `144/144` and in-memory compile
  `144/144`.

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

## Correction review and closure

- Correction `55b265b3904596c057feaa1127de9788122dfda7` changes only
  `tests/test_codex_registration_oracle_adapter.py`; handoff
  `6f926995e0aa6250e34d095dd08406908c4834a2` changes only
  `doc/WorkProgressReport.md`. The original staging adapter and E6A acceptance
  blobs are unchanged.
- The negative matrix now holds the opposite collection at exact one for each
  of marketplace zero, marketplace duplicate, installed-plugin zero and
  installed-plugin duplicate. Each rejected proof also preserves oracle state.
- In the reviewer-owned immutable TEMP archive, deleting only the marketplace
  count gate makes the named matrix red. After exact restoration, deleting only
  the plugin count gate independently makes the same matrix red. The adapter
  restores to Git blob `cfba3269c3314b5cf783869712697f71f80514f4`, and the
  named test returns green.
- Commit ancestry, exact scopes, one PRG-375 occurrence, the permanent
  implementation worktree clean readback and the three-worktree topology are
  coherent. XSS remains not applicable and no live Codex, target project,
  push, staging publication, package, install, release or deployment occurred.

CR-172 is closed. A1-A8 revision 02 is independently proven and the ticket is
`APPROVED / READY_TO_MERGE`.
