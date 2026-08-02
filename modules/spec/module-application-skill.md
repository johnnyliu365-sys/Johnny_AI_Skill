# 可重用模組選擇 Skill POC 規格

| 欄位 | 內容 |
| --- | --- |
| 規格 ID | `SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H` |
| 狀態 | `APPROVED` |
| 專屬 Context | `doc/context/module-application-skill/main.md` |
| 需求變更 | `CHG-20260802-003` |

## 目標

讓 Agent 用一份短卡片選擇最少的既有通用模組，再依明確路徑讀取，而不是將整個 `library/` 放入 Context。

## 範圍

- `library/MODULE_CATALOG.md`：READY 模組、公開 import、相依與閱讀順序。
- `skills/apply-reusable-modules/`：可攜 Codex skill，指引選擇與安全採用。
- `library/README.md` 與 `template/README.md`：新專案的最小載入與版本化引用說明。

不做原始碼搬移、套件發行、全域安裝、Provider／網路、或未完成模組的自動補齊。

## 驗收條件

1. Skill 可以通過標準 validator，且沒有 TODO。
2. 每張 READY 卡只指向目前存在的 README、公開 import 和必要檔案。
3. 卡片與 skill 都明確禁止全量讀取、源碼複製及流程繞過。
4. 新專案模板說明固定版本引用，而不是複製整個資料夾。
