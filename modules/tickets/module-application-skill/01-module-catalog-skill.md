# 01｜Module catalog 與可攜 skill

| 欄位 | 內容 |
| --- | --- |
| 對應規格 | `SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H` |
| 需求變更 | `CHG-20260802-003` |
| 狀態 | `DONE` |

## 可觀察結果

Agent 可從 `library/MODULE_CATALOG.md` 選出卡片，並由 `$apply-reusable-modules` 以 README → 公開 API → 精確契約的順序最小化讀取。

## 完成證據

- `skills/apply-reusable-modules/` 已由 skill creator 初始化並經 `quick_validate.py` 驗證。
- 目錄包含 12 個現有 READY 模組與 1 個 Router POC 卡片；未完成 Kotlin／C# 候選被明確排除。
- `git diff --check` 通過。
