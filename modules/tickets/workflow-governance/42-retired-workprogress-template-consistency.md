# 42｜工單模板不得要求已退役的 WorkProgress 回寫

| 欄位 | 內容 |
| --- | --- |
| State | `READY_FOR_IMPLEMENTATION / LOCAL_ONLY`；不宣稱 Host admission 完成 |
| Authority | 既有 `PRD-20260805-009`、`CHG-20260805-009`、已核准 workflow-governance SPEC；Owner 2026-10-18 checklist 11 衝突修正與持續執行授權；不建新 PRD |
| Baseline | `da03afa0dd6becc5529321fb9b7adb7247c9d80a` |
| Roles | Implementation Owner：低成本模型；獨立 Reviewer：另一席；Root 僅控制與整合 |
| Profile | `COMPACT`，僅本庫模板與既有測試，無 target、外部服務或發布效果 |

## 來源與目標

`Workflow.md` 的治理文件歸屬段已禁止 `WorkProgressReport.md` 成為 implementation／review 寫入或 return target，並退役獨立 WPR commit。兩份工單模板的「完成回寫」仍要求 `WorkProgress：PRG-YYYYMMDD-NNN`，使實作者面對互斥指示。本票只移除該錯誤義務，保留精確 commit／artifact 身分；不改 Workflow 正典，不引入新的進度文件或流程。

```johnny-boundary
modify = modules/tickets/TEMPLATE.md
modify = template/modules/tickets/TEMPLATE.md
modify = tests/test_ticket_template_contract.py
create = none
delete = none
forbid = Workflow.md
forbid = library/
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
```

## Work 與驗收

1. 兩份模板的活躍「完成回寫」只要求實際檔案及精確 commit／artifact identifiers，不要求 WorkProgress／PRG 寫入或 return；不得刪除其他派工、測試接線與審閱欄位。
2. 沿用 `tests/test_ticket_template_contract.py` 的 active-section helper，驗證兩份模板的完成欄位與 Workflow 正典一致。對任一模板回填已退役的 WorkProgress 活躍 bullet 時，具名負向格必須轉紅，精確還原後回綠。合法完成欄位保持綠燈。
3. 不建立新檔、共用件或測試框架；預期產品碼 0、既有模板各 -1 bullet、既有測試小幅增量；修正回合沿同一票預算。

Run：`python -m pytest tests/test_ticket_template_contract.py -q`；`git diff --check`。Reviewer 自行執行一次不同入口的反向突變並讀回候選 SHA／diff。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整 candidate SHA、三檔清單、命令與具名紅→綠、findings、scope deviations。Implementer 不整合、不 push。

## 非宣稱

模板一致性測試不能證明填票時的 Host 攔截、工作樹防回退或正式結案准入；這些仍由各自既有票與 checklist 未完成項追蹤。
