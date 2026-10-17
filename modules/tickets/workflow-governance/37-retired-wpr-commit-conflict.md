# 37｜移除已退役 WPR 獨立提交要求

| 欄位 | 內容 |
| --- | --- |
| State | `SLICE_LOCAL_INTEGRATED` at `2f1c29cb`；清單 11 的其他一致性檢查仍開放 |
| Authority | Owner 2026-10-18 清單 11；既有 `Workflow.md` 治理文件歸屬及本票，不新增 PRD／SPEC／Gate |
| Baseline | 本票 docs-only commit；派工時精確 pin |
| Roles | 低成本實作席位；另一席獨立審閱；Root 整合 |
| Profile | `COMPACT`；無 Host、產品或外部 effect |

## 邊界與查重

`Workflow.md` 治理文件歸屬明確禁止 `WorkProgressReport.md` 作為 implementation／review
寫入或 return target，也禁止獨立 WPR commit；`implementation-tdd.md` Ticket completion
卻仍要求 WPR 在分開的 docs-only commit 記錄結果。只消除後者的相反義務，沿用
既有 typed `ImplementationReturn` 與後續 ticket／review evidence，不建立第二份台帳。

```johnny-boundary
modify = skills/johnny-project-takeover/references/implementation-tdd.md
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
forbid = Workflow.md
forbid = CodeReview.md
forbid = modules/spec/
forbid = doc/requirements/
```

## Work／驗收

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
