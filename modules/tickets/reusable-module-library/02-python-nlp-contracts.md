# 02｜Python NLP 強型別契約與文字正規化

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§NLP） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `DONE` |
| 環境 | `LOCAL` |
| 責任邊界 | Python 的 `TextInput`、`NormalizedText`、分類結果與欄位抽取 DTO |
| 禁止修改 | 來源 parser、LLM／HTTP 呼叫、LINE、資料庫、派單規則 |

## 可觀察結果

已驗證的文字輸入可正規化成具名不可變 DTO；空白、過長或未支援輸入得到顯式拒絕結果，不產生猜測欄位。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/NLP/python/text_contracts/`。
- 參考：來源專案C 的訂單契約與 來源專案D 的 `CustomerIntakeResult`／事件模型。
- 不得複製上述來源實作；只重建通用 DTO 與驗證規則。

## TDD 設計

1. 正常：繁體中文與 ASCII 混合文字得到可重現正規化。
2. 錯誤：空值、控制字元、超長與未驗證外部物件 fail closed。
3. 回歸：結果不使用 `Any`、裸 `dict` 或字串狀態機跨公開邊界。

## 完成紀錄

- 實作：`library/NLP/python/text_contracts/`，提供不可變 DTO、具名拒絕原因與純本地 Unicode 正規化。
- 開發期型別工具：使用者已授權並記錄 `mypy==2.3.0`；`python -m mypy --strict library tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py` 通過。
- 驗證：`python -m unittest discover -s tests`（5 passed）、`python -m py_compile ...` 與未驗證外部文字拒絕 smoke test 均通過。
- Review：`APPROVED`，詳見 `doc/reviews/reusable-module-library/02-python-nlp-contracts-code-review.md`。
- Ticket commit：`88fbfc0`（`feat: add typed NLP text contracts`）。
- 來源專案未被讀寫以外的任何方式觸及；沒有修改、搬移、刪除或新增其檔案。
