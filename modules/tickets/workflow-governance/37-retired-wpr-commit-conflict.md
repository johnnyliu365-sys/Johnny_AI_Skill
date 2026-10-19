# 37｜移除已退役 WPR 獨立提交要求

| 欄位 | 內容 |
| --- | --- |
| State | `ORIGINAL_SLICE_LOCAL_INTEGRATED` at `2f1c29cb`；current correction is closure02 NORMALIZATION only；清單11未結案 |
| Authority | Owner 2026-10-18 清單 11；既有 `Workflow.md` 治理文件歸屬及本票，不新增 PRD／SPEC／Gate |
| Baseline | 本票 docs-only commit；派工時精確 pin |
| Roles | 低成本實作席位；另一席獨立審閱；Root 整合 |
| Profile | `COMPACT`；無 Host、產品或外部 effect |

## 邊界與查重

### Same-lineage normalization correction / closure02 — 2026-10-20

Original37 completed slice remains valid; this is checklist11's remaining adjacent
conflict, not a reopened implementation-tdd repair or new requirement. Current
specification-ticketing.md Dispatch normalization still assigns transitions/IDs/
commits/review results/exceptions to Work Progress Report, whereas Workflow's
canonical ownership limits WPR to a short project-source index and forbids its
implementation/review write/return duty. Remove that competing authority assignment
only, retain WPR as an existing read-only index and exact ticket/review evidence.
Do not remove progress documents, change routing behavior, add stage/state/gate,
require future review evidence in an implementer return, or rework37's passed scope.

Parent batch-checklist-local-20261019-uncapped; existing approved requirement/SPEC/
Workflow references above remain authority. Planning6b86185e; exact source baseline
0d14087ddf09759ee805dd4ec378f4a5a038b16d (same relevant product/reference bytes).
COMPACT, Python strict, no Browser/Host/provider/effect, no new DTO or constructor.
Exact MODIFY ONLY skills/johnny-project-takeover/references/specification-ticketing.md,
library/workflow_router/profile.py, tests/test_workflow_router.py; CREATE0/DELETE0.
Reuse current LF-pinned SkillReference values and existing Router unittest cells.
Update only this reference's digest/revision pins after final reference byte.

AC37B1 replace obsolete WPR authoritative-record ownership with ticket/review exact
source/typed-return ownership, preserving WPR's nonauthoritative index role. AC37B2
test_dispatch_normalization_keeps_wpr_as_index_only in the existing Router test file rejects old positive
ownership duty while lawful normalization and existing completion timing pass.
AC37B3 old text restored => named baseline RED; candidate lawful suite GREEN;
actual old-duty mutation => named RED then exact restore GREEN. Reviewer uses a
different WPR-duty variation; string/pin consistency is governance-document evidence,
not proof of native interception or source authority. Existing Router behavior and
all unrelated source/policy pins unchanged. No new test helper/framework/script.
The old test_completion_evidence_does_not_require_a_separate_wpr_commit remains
GREEN by design; it covers closed closure01, NOT this Dispatch normalization
defect. Add the named normalization assertion first and record its baseline RED
against the active ownership sentence. Never manufacture red in the old completion
section or modify implementation-tdd/installed plugin cache.

Source owner /root/grant_transport_impl, Root reviewer/orchestrator; distinct
/root/ticket30_native_tools_review source/doc reviewer. New context
ctx-wg37-normalization-20261020; preregister .worktrees/skill-improvement-37-normalization
and matching -review, codex/same branches; Temp/johnny37-normalization-owner-20261020
and -review-20261020. One source lane only after H3 evidence return/release to hold.
TTL through review+seal, Recovery/evidence holds override; no cleanup or denied retry.
Conditional grant-wg37-normalization-20261020 revision01 is NOT_ACTIVE until exact
document independent review and fresh clean/nonreparse/Git/ordinary current
SkillReference preflight. Root then derives exact same-scope activation, no Owner
renewal. Run existing unittest Router suite, strict affected2Python files, reference
LF/pin consistency, memory compile/import and full-output named mutations only;
process-local pytest autoload disabled/no-cache if pytest used, outer60/child55.
Return candidate/files/checks/findings/deviations; no merge/push/Host qualification.

### Active closure02 exact boundary

```johnny-boundary
modify = skills/johnny-project-takeover/references/specification-ticketing.md
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
forbid = Workflow.md
forbid = CodeReview.md
forbid = modules/spec/
forbid = doc/requirements/
```

## Historical closure01 — completed, not current dispatch authority

The following original completion repair is retained as provenance only. Its old
reference path implementation-tdd.md is NOT authorized for closure02 mutation.

`Workflow.md` 治理文件歸屬明確禁止 `WorkProgressReport.md` 作為 implementation／review
寫入或 return target，也禁止獨立 WPR commit；原 implementation-tdd completion
衝突已由下列完成的舊修正移除，不是本次 Dispatch normalization 缺陷。

### Historical Work／驗收

1. 實作者回件時的 typed return 須識別 exact ticket、實作 commit 與可重現驗證
   evidence；獨立 review evidence 只在後續 REVIEW 形成。這取代獨立 WPR commit
   要求；保留實作 commit、必要測試、smoke 與 residue 條件。不得把
   `WorkProgressReport.md` 宣稱為已刪除的專案來源，也不得創造新的 WPR 回寫義務。
2. `implementation-tdd.md` 是既有 digest-pinned reference；依現有 LF digest 慣例
   同步更新 `profile.py` 與 `test_workflow_router.py` 的 revision/digest。
3. 自動測試拒絕再引入「獨立 WPR commit 為完成條件」的文字，並核對 Workflow 的
   canonical 禁止條款及 repin 一致；相關 Router 測試維持綠燈。
4. Reviewer 用反向突變把舊 WPR 義務放回 reference，具名格轉紅，還原後轉綠；
   確認未改別的 ticket completion 義務。

Run：`python -m pytest tests/test_workflow_router.py -q`、`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選 SHA、三個宣告路徑、測試及
反向突變結果、剩餘問題。實作者不整合、不推送。若須修改 `Workflow.md` 或
Router 行為才能完成，回 `CHANGE_DETECTED`。

## 實作與獨審

初版 `47860a37` 移除 WPR 義務，但把未來的 review evidence 寫成實作者回件前提；
獨審依 Closure 1 要求同票修正。原實作者 additive correction `fe40fe00` 改為 typed
return 只綁 ticket、commit 與驗證 evidence；原 reviewer 複驗時從不同入口重新引入
「回件前要有 review evidence」，具名格轉紅、還原綠。最終 54 tests／202 subtests
通過；三個落地 Git blob 與受審候選相同，本地受控整合 `2f1c29cb`。
詳見 `doc/reviews/workflow-governance/37-retired-wpr-commit-conflict-code-review.md`。
未推送、未發布；此票只修一處衝突，不宣稱清單 11 完成。
