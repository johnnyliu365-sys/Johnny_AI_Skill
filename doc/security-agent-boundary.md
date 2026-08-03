# 通用功能模組庫安全邊界

## 允許

- 唯讀參考使用者授權的本機來源專案。
- 在本專案重新實作強型別契約、fake adapter、測試與 README。

## 禁止

- 讀取、輸出、複製或保存 `.env`、憑證、token、PII、租戶資料、營運資料、raw log、資料庫匯出或付款資訊。
- 對來源專案或外部 Provider 執行寫入、訊息發送、付款、退款、部署、資料庫、Webhook 或環境設定操作。
- 將來源專案的資料表、商業規則、群組設定或 UI 視為通用契約。

## 付款與訊息模組的額外規則

- 所有付款流程一律以 fake provider、明確金額型別、伺服器定義商品、idempotency key 與 append-only audit 為最低前提。
- 所有出站訊息一律以 fake provider、tenant／scope 隔離、outbox 與緊急停止測試為最低前提。
- README 不得包含任何敏感範例值。

## Private Router SaaS POC 額外規則

- POC 的 service 邊界只可接收嚴格驗證的假名化帳號／專案識別、帳號範圍 salted revision digest、有限列舉的階段事件、權利模式與結構化 redacted 摘要欄位；不接受自由文字、動態物件或未宣告欄位。
- 禁止將原始碼、文件原文、檔案名稱、路徑、URI、prompt、`ContextPacket`、side-context 原文、Secret、PII、完整 telemetry JSONL 或客戶專案 Log 傳送、儲存或輸出至 Router SaaS。
- 指紋僅供一致性與失效判斷，不可宣稱為匿名化證明；禁止傳送未加鹽、可由低熵內容反推的內容雜湊。
- 私有 Router 缺少有效 entitlement、核准、必要 metadata、能力、服務可用性或合格回應時必須 fail-closed。不得因服務失敗改用本機私有 Profile、未審核 fallback 或猜測性決策。
- POC 不使用真實 OAuth、付款、webhook、雲端資料庫、模型、Provider credential 或部署；任何引入這些能力的需求必須以新的 MVP CHG 重跑 Wayfinder。
