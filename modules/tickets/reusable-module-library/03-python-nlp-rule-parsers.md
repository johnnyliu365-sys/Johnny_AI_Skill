# 03｜Python NLP 規則式欄位抽取器

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§NLP） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 從已正規化文字抽取明確標示欄位、回報歧義與保留解析理由 |
| 禁止修改 | 來源專案 parser、地址資料、派單／LINE 自動化、模型呼叫 |

## 可觀察結果

呼叫端可提供欄位規格與固定規則，取得 `COMPLETE`、`INCOMPLETE`、`AMBIGUOUS` 或 `REJECTED` 的明確結果；模組不補造缺少資料。

## 實作範圍與來源追溯

- 前置依賴：Ticket 02。
- 預定實際程式碼：`library/NLP/python/rule_parser/`。
- 參考：來源專案C 的 message-kind／frame-boundary 規則與 來源專案D 的 customer-intake parser；只抽取通用模式。

## TDD 設計

1. 正常：標記欄位與固定分隔符可抽取。
2. 違規：重複欄位、跨 frame 借值與缺欄位回傳歧義／不完整。
3. 回歸：相同輸入與規則必得相同結果與理由。
