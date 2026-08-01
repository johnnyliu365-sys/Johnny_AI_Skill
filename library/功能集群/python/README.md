# Python 其他功能集群

此目錄保存 Python 的通用可靠性與事件能力；各子模組必須以公開型別、fake adapter 與 deterministic 測試隔離來源專案。

## 責任

- 建立 `reliability_core/`、`line_transport/`、`identity_resolution/`、`event_timeline_audit/` 與 `engagement_rules/`。
- 將 outbox、worker、狀態轉換、停止控制與 identity display 等能力維持在無特定租戶／Provider 的邊界。

## 來源追溯

主要參考 來源專案D 的可靠性模式與 SourceProjectA 的推薦／獎勵規則分解；實作與測試只存在於本專案。

## 禁止用途

- 不得發送 LINE 訊息、處理真實租戶、讀取資料庫或啟用自動化。
- 不得使用未驗證動態事件、原始 payload、使用者 ID 或來源專案報表。
- 不得直接複製來源專案程式碼或測試 fixture。
