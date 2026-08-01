# 04｜Python NLP／多模態 Provider 邊界

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§NLP） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 模型／多模態 provider port、請求契約、結果驗證與失敗分類 |
| 禁止修改 | Gemini 或其他真實 Provider、API key、圖片資料、健康／營養領域規則 |

## 可觀察結果

呼叫端能以 fake provider 驗證成功、暫時失敗、永久失敗、結構無效與逾時結果；未驗證模型輸出不會進入領域結果。

## 實作範圍與來源追溯

- 前置依賴：Ticket 02。
- 預定實際程式碼：`library/NLP/python/provider_ports/`。
- 參考：SourceProjectA `來源專案的AI服務層` 的錯誤分類與結構化分析輸出；排除 prompt、個人化、營養、憑證與 HTTP 實作。

## TDD 設計

1. 正常：fake provider 回傳可驗證 DTO。
2. 外部失敗：timeout、auth、rate limit、永久錯誤均回傳具名失敗型別。
3. 回歸：未知 JSON／動態資料不得越過 adapter 邊界。
