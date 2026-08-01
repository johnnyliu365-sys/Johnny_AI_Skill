# 05｜Python 金流契約與訂閱帳本

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§金流串接） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | `Money`、付款意圖、交易狀態、idempotency key、訂閱權益與 append-only 帳本事件 |
| 禁止修改 | SourceProjectA 的資料表、支付provider丙、支付provider甲、發票、真實付款與資料庫 |

## 可觀察結果

使用整數最小貨幣單位建立付款意圖後，重複 key 不產生第二筆權益；非法金額、無效狀態轉換與重複退款 fail closed。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/金流串接/python/payment_contracts/`、`subscription_ledger/`。
- 參考：SourceProjectA `來源專案的訂閱模組`、交易／分潤設計與 來源專案D 的 expected-state／outbox 模式。
- 不採用：來源 schema、會員／經銷／分潤商業規則與所有 provider 設定。

## TDD 設計

1. 正常：付款確認只產生一筆帳本與一次權益。
2. 違規：負金額、浮點輸入、無效幣別與重複 idempotency key 遭拒。
3. 回歸：取消、退款與訂閱到期為不同明確事件。
