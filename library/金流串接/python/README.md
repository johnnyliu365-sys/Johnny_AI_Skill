# Python 金流串接模組

此目錄是 Python 金流核心的語言根目錄。每個子模組只處理明確的領域契約與 fake-backed 行為，不能持有真實憑證或 Provider SDK 設定。

## 責任

- 使用整數最小貨幣單位或等價不可變值物件表示金額。
- 以 Enum 與不可變事件表示付款、退款、對帳與訂閱狀態。
- 用穩定 idempotency key 與 append-only audit 防止重複副作用。

## 公開模組規劃

- `payment_contracts/`、`subscription_ledger/`、`provider_ports/` 與 `reconciliation/` 將分別由已核准工單建立。

## 來源追溯

僅參考 SourceProjectA 的付款流程分層；本專案不保證、也不嘗試相容其資料表、商品、會員、分潤、發票或 provider。

## 禁止用途

- 不得連線真實付款／發票 Provider、資料庫或 webhook。
- 不得保存、輸出或請求支付憑證、卡號、帳戶、交易資料或 PII。
- 不得將 fake provider 視為正式收款驗證。
