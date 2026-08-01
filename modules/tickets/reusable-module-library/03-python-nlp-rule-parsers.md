# 03｜Python NLP 規則式欄位抽取器

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§NLP） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `DONE` |
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

## 完成紀錄

- 實作：`library/NLP/python/rule_parser/`，提供固定標記／分隔符規則、不可變結果、具名狀態與解析理由。
- 行為：只從同一 frame 的實際標記值建立欄位；缺欄、重複欄位、空值、多個完整 frame、未知內容與跨 frame 欄位皆回傳明確結果，絕不補值。
- 驗證：`python -m unittest discover -s tests`（12 passed）、`python -m mypy --strict library tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（11 source files 無問題）、`python -m py_compile ...` 與跨 frame 拒絕 smoke test 均通過。
- Review：`APPROVED`，詳見 `doc/reviews/reusable-module-library/03-python-nlp-rule-parsers-code-review.md`。
- Ticket commit：`d03880e`（`feat: add deterministic NLP rule parser`）。
- 來源專案未被修改、搬移、刪除或新增任何檔案。
