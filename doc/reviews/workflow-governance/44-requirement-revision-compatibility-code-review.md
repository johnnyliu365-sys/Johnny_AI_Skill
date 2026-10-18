# Ticket 44 — local revision history compatibility review

Authority: `batch-checklist-local-20261018` -> Root-scoped
`grant-wg44-lineage-local-20261018`; original PRD/CHG and approved AC17 design.

Independent `/root/batch_authority_review` rejected document candidate
`67fe2cca` for omitting affected acceptance conditions required by AC17.
Revision02 at `4414c6a575bc107c7f25bcd2de1039900a33a3f0`, ticket blob
`a65bbe644b9126d3a742b14ee97ee85449d0e564`, was APPROVED after adding bounded
unique affected AC IDs, declared history AC membership, and missing/duplicate/
mismatch negative cases. Those values remain candidate metadata, not trusted
approval. No activation or replacement of the legacy validator was approved.

Root verified the two source/test blobs still match the source baseline
`101e16ad25799d2a9b3158a8afb9782bc836a5a3`, then allocated clean non-reparse
`.worktrees/skill-improvement-44-lineage`, branch
`codex/skill-improvement-44-lineage`, at exact reviewed commit `4414c6a575bc107c7f25bcd2de1039900a33a3f0`.
Author `/root/lineage_compat_impl`, distinct reviewer `/root/lineage_compat_review`.
STANDARD pure-data construction; command ceiling300s, single90s; no network,
helpers, new files or external effects. Type phase is reviewed before behavior.

Status: IMPLEMENTING_CONTRACTS. Full checklist11 remains open. Asset owner is
the named seat; teardown only after review, sealed evidence and local integration.

## Constructor review

Author candidate `c351f4bdb1767a5faaa497604dec1424ae53ff16` changed exactly the
two allowed files (+78 product/+84 test lines); legacy validate body unchanged.
Author55s command time. Independent `/root/lineage_compat_review` read exact
candidate in its registered clean non-reparse detached worktree, verified
strict ordinary DTO construction and ran12tests/25subtests, strict mypy,
import and diff checks: APPROVED_TYPE_PHASE_ONLY. No finding. Root continued
the same author to the pure method, conservatively75/300s cumulative pending
exact review command timing. Full behavior/mutation/integration not yet approved.

## Final local review and integration admission

Independent reviewer APPROVED `dfced43f8c3985722e06415773f75b7cb31a153f` against
allocation4414c6a5, exact ticket unchanged. L1–L4 inspected. Reviewer reversed
the terminal revision comparison (different from author's chain mutation):
`pytest -k revision_history_validation -vv -rA` produced2failed, including a
valid chain and the named terminal mismatch. Exact restoration followed by
full `tests/test_workflow_requirement_lineage.py`:14passed/30subtests;
Git diff exit0/clean. Strict mypy/import was independently green in type phase,
author reran strict/compile on final candidate. No external effects or legacy
validate change. Reviewer's actual command budget approx30s type+13s final;
conservative cumulative account155/300s including author120 (which had used
a20s review estimate). No budget reset.

Growth review:123 added production lines and246 test lines exceed the expected
signals, but checks cover separate DTO/chain/AC/terminal responsibilities and
reuse fixtures. Reviewer found no material duplicated logic; no artificial
compression or splitting required. This does not approve future unbounded growth.

Root authorizes an exact-blob replay of the two reviewed source commits only
onto the current control baseline, followed by existing document mutation gate.
Registered integration assets: owner Root; contained
`.worktrees/skill-improvement-44-land`, branch`codex/skill-improvement-44-land`;
temporary journal root `%TEMP%/Johnny-checklist44-20261018`. Create only if absent,
verify containment/non-reparse/clean first; TTL through candidate parity,
guarded integration, immutable evidence seal and independent readback. Then
remove only these registered clean/integrated resources and the exact journal.
Author/review worktrees are retained until that same seal confirms teardown.
No force/reset/clean, shared-history rewrite or unrelated asset removal.

### Local integration seal

Root replayed the two reviewed commits onto control baseline
`684b93cfee4c72f1c1428e3dca8228d0b4f58030`, yielding
`1aa5ed22bc270b8d8604be89c9f23b0942c8dee5`. Existing
`admit_document_mutation` read the boundary from the integration branch and
returned INTEGRATED at that exact SHA. Root read HEAD and both blobs back:
`requirement_lineage.py`=`22510970e0e6b2fe5b3a6c5143304b8084d7264f`;
`test_workflow_requirement_lineage.py`=`bf511e442d88ba580aba3d9ee6196f2ba915a7df`.
Both equal the independently reviewed candidate. On integrated source, full
lineage suite14passed/30subtests in1.11s. Integration command wall8.23s.

Journal exact path `C:/Users/GameBoy/AppData/Local/Temp/Johnny-checklist44-20261018/queue/document-mutation-journal.jsonl`:
389 bytes, one INTEGRATED event at `2026-10-18T13:19:58.425641+00:00`, principal
GameBoy, branchcodex/skill-improvement-checklist, candidate1aa5ed22, exactTicket44.
SHA256 `b5dd3d7c3be5251e2d7a2ec19f440e35edf733a3ef368b6d28ee7d71a0b92bd4`.
This immutable summary preserves all fields necessary for the gate outcome;
raw journal remains until independent seal readback. Cleanup pending that check.
