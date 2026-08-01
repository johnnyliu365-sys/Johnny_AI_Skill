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
