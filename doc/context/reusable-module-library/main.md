# 通用功能模組庫 Context

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | `reusable-module-library` |
| Agent／worktree | `Codex／目前工作區` |
| 共同基準 | `待 docs-only commit` |
| 狀態 | `AWAITING_TICKET_CONFIRMATION` |
| 責任邊界 | 本專案的通用模組、測試與 README 設計 |
| 禁止修改 | 四個來源專案、外部服務、資料、秘密與部署 |

## 共用 Context 引用

- `CONTEXT.md`：`已確認事實與共同邊界`
- 共用基準 commit：待文件基準提交。

## 已確認事實與約束

- 來源內容只能作為行為與設計參考，交付程式碼必須在本專案重新實作。
- 初始語言範圍為 Python、Kotlin 與 C#；各語言的實際來源根目錄與套件邊界需由 SPEC 確定。
- 任何涉及付款、外部訊息或模型 provider 的實作必須預設 fail-closed，並只提供 fake adapter 測試。

## 待決事項與跨集群依賴

- D-01：使用者已核准 `library/` 為通用程式碼根目錄，與 `modules/element/` 的索引職責分離。
- D-02：使用者已核准 Python、Kotlin 與 C# 的範圍；各 ticket 的實作順序待第二次核准。
- Ticket 01 已完成並建立 `library/` README 基準；下一張 Ticket 02 仍須使用者明確確認。
