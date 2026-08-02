# 通用功能模組庫 Context

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | `reusable-module-library` |
| Agent／worktree | `Codex／目前工作區` |
| 共同基準 | `88193ca`（Ticket 11 handoff）與本次 approval-state docs-only commit |
| 狀態 | `AWAITING_TICKET_APPROVAL` |
| 責任邊界 | 本專案的通用模組、測試與 README 設計 |
| 禁止修改 | 四個來源專案、外部服務、資料、秘密與部署 |

## 共用 Context 引用

- `CONTEXT.md`：`已確認事實與共同邊界`
- 共用基準實作 commit：`c255720`（`fix: reject invalid offline geo index entries`）；最近 handoff：`88193ca`。

## 已確認事實與約束

- 來源內容只能作為行為與設計參考，交付程式碼必須在本專案重新實作。
- 初始語言範圍為 Python、Kotlin 與 C#；各語言的實際來源根目錄與套件邊界需由 SPEC 確定。
- 任何涉及付款、外部訊息或模型 provider 的實作必須預設 fail-closed，並只提供 fake adapter 測試。

## 待決事項與跨集群依賴

- D-01：使用者已核准 `library/` 為通用程式碼根目錄，與 `modules/element/` 的索引職責分離。
- D-02：使用者已核准 Python、Kotlin 與 C# 的範圍；每一張 ticket 的實作仍須在開始前取得明確確認。
- Ticket 01 至 Ticket 11 均已完成；Kotlin offline geo resolution 已具備 APPROVED review 與可重跑驗證。
- Ticket 12、13 仍為 `PLANNED`／核准狀態 `PENDING`；兩者尚不足以構成完整遊戲模組集群，未取得實作授權。必須先定義並核准完整集群範圍、必要 tickets、依賴與驗收條件，再重新進入 `grill-with-docs → to-spec → to-tickets`。
