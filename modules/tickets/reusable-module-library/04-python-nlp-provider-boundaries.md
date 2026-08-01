# 04｜Python NLP／多模態 Provider 邊界

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§NLP） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `DONE` |
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

## 完成紀錄

- 實作：`library/NLP/python/provider_ports/`，提供 provider port、文字分析請求、已驗證成功 DTO、失敗分類、retryability、唯一 raw payload validator 與不連網 fake provider。
- 行為：成功、暫時／永久失敗、逾時、驗證失敗與限流皆以具名型別回傳；未知、缺欄或多欄 payload 在 adapter 邊界回傳 `INVALID_STRUCTURE`，不會產生領域結果。
- 驗證：`python -m unittest discover -s tests`（16 passed）、`python -m mypy --strict library tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（16 source files 無問題）、`python -m py_compile ...` 與未知 payload 拒絕 smoke test 均通過。
- Review：`APPROVED`，詳見 `doc/reviews/reusable-module-library/04-python-nlp-provider-boundaries-code-review.md`。
- 先行回滾點：checkpoint `76c9cbd`，本地 tag `rollback/ticket-04-start-20260801`。
- Ticket commit：`02fa06f`（`feat: add typed NLP provider boundary`）。
- 來源專案未被修改、搬移、刪除或新增任何檔案。
