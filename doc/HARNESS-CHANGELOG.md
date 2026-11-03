# Harness change log

One row per change that altered what the plugin does. Working history lives in Git; the revision-135 checklist stays on branch `codex/skill-improvement-checklist` at `doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` and is not carried onto this line. This table is not a progress tracker.

| Date | Change | Authority | Where |
| --- | --- | --- | --- |
| 2026-11-03 | Gates-first control plane: state in files, transitions by scripts; integration by script; stages by intake mode; four test layers; CI invariants only | `PRD-20261103-043` | `modules/spec/workflow-governance.md` Revision 04, `Workflow.md` section 0, `CodeReview.md` |

## Checklist items carried from revision 135

| Item | Status at freeze | Disposition under Revision 04 |
| --- | --- | --- |
| 01 主線與單票 | 30B review blocked | superseded by the contract gate (wave 2) |
| 02 已核准工作接續 | local integrated, effect open | state-in-files continuation (R4-1); grant-issuer and admit_dispatch residuals carried to wave 2 queue admission (R4-7) |
| 03 派工完整最小 | local integrated | dispatch lint script (wave 1); host-admission residuals carried to wave 2 |
| 04 TEST → A → B | complete local | kept; four layers (R4-6) |
| 05 候選來源與 Expected | contract local | contract gate provenance check (wave 2) |
| 06 共用樹覆蓋 | worker claim local | one writer per file; integration script (wave 2) |
| 07 完成與證據 | projection integrated | evidence gate (wave 2) |
| 08 測試依賴／退役 | local command source | coverage map script (wave 2) |
| 09 窄修窄審 | cases verified | kept as review policy |
| 10 成本／外部呼叫／回報 | local integrated | token column in receipts (wave 2) |
| 11 去重與衝突 | local integrated | requirement snapshot ids (wave 2) |
| 12 回放與獨審 | end to end not verified | first run on a target project (wave 2 acceptance) |
| 13 歷史 SPEC 舊規則殘留 | precedence notes (wave 1) | sentence-level sweep over every SPEC with the ticket 47 D7 instrument (wave 2); archive through requirement lineage when the router library retires (wave 3) |
