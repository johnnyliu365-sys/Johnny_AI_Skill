# 通用功能模組庫工單協作登錄

| 欄位 | 內容 |
| --- | --- |
| 對應規格 | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP` |
| 共同基準 | 待 docs-only commit |
| 整合負責人 | Codex／目前工作區 |
| 集群交接狀態 | `PLANNED` |

## 共同不可違反邊界

- 僅可在 `C:\Users\<user>\Desktop\AI控制工作workflow` 寫入。
- 來源專案A、來源專案B、來源專案C 與 來源專案D 均為唯讀參考；禁止新增、修改、搬移或刪除其中任何檔案或原始碼。
- 每張工單必須在本專案重新實作，不得直接複製來源程式碼、環境設定、資料、schema、provider 憑證或測試 fixture。
- 每個新增實作資料夾必須新增 README，且所有外部能力均以 fake adapter 驗證。

| 工單 | 責任邊界 | 交接狀態 |
| --- | --- | --- |
| `01-library-root-and-readmes` | 建立實作根目錄與導覽 README | `DONE` |
| `02-python-nlp-contracts` | 文字處理的強型別契約與正規化 | `PLANNED` |
| `03-python-nlp-rule-parsers` | 可解釋規則式欄位抽取 | `PLANNED` |
| `04-python-nlp-provider-boundaries` | 多模態／LLM provider port 與 fail-closed 結果 | `PLANNED` |
| `05-python-payment-contracts-ledger` | 金額、付款意圖、帳本與訂閱狀態 | `PLANNED` |
| `06-python-payment-provider-reconciliation` | fake provider、退款與對帳狀態機 | `PLANNED` |
| `07-python-reliability-core` | outbox、worker、expected-state guard 與停止控制 | `PLANNED` |
| `08-python-line-transport-identity` | 訊息 transport port 與唯一身份／顯示名稱分離 | `PLANNED` |
| `09-python-event-timeline-audit` | 可重播事件時間線與 audit 比對 | `PLANNED` |
| `10-python-engagement-rules` | 推薦、獎勵與任務的純規則核心 | `PLANNED` |
| `11-kotlin-offline-geo-resolution` | 離線地址與座標值物件 | `PLANNED` |
| `12-csharp-card-rules-engine` | 純 C# 卡牌規則核心 | `PLANNED` |
| `13-csharp-camouflage-state` | 純 C# 偽裝狀態機 | `PLANNED` |

## 工單順序、依賴與衝突檢查

1. Ticket 01 是所有實作目錄與 README 的前置條件。
2. Ticket 02 是 Ticket 03 與 04 的型別契約前置條件。
3. Ticket 05 是 Ticket 06 的金額、交易與帳本前置條件。
4. Tickets 07–13 可在各自前置條件完成後排程；每次仍只能有一張 `IN_PROGRESS`。
5. 無任何工單可寫入來源專案或觸發真實 provider。
