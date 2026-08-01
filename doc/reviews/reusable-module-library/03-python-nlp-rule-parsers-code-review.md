# Code Review：03 Python NLP 規則式欄位抽取器

## 範圍

- SPEC：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`
- 變更：`CHG-20260801-001`
- Ticket：`03-python-nlp-rule-parsers`
- 審閱對象：`library/NLP/python/rule_parser/`、`library/NLP/python/README.md` 與 `tests/test_nlp_rule_parser.py`

## 審閱結論

`APPROVED`

## 必要驗證項目與證據

| 項目 | 結果 | 證據 |
| --- | --- | --- |
| 清晰易懂與 P0 強型別 | 通過 | 公開 API 僅使用不可變 dataclass、Enum、具名值物件、tuple 與顯式 `None`；無 `Any` 或裸 `dict` 邊界。 |
| 編碼規範與分層 | 通過 | 契約位於 `contracts.py`，純解析行為位於 `parser.py`，公開 API 由 `__init__.py` 明確匯出。 |
| 邏輯正確 | 通過 | 完整、缺欄、重複欄位、跨 frame、空值、多完整 frame 與未知內容均有對應的狀態與理由。 |
| 邊界與異常 | 通過 | 規則組拒絕空值、重複名稱／token、相同分隔符與不合型別；解析不會跨 frame 拼接欄位。 |
| 安全與效能 | 通過 | 無網路、provider、資料庫、LINE、付款、地址資料、秘密或副作用；單次輸入只做有限次字串分割與線性規則掃描。 |
| 測試覆蓋與 smoke test | 通過 | `python -m unittest discover -s tests`：12 passed；跨 frame smoke test 通過。 |
| 依賴合理 | 通過 | 未新增執行期依賴；僅使用 Ticket 02 的本地文字契約。 |
| 專案規格符合性 | 通過 | 僅在本專案重建通用固定規則解析，保留四個來源專案唯讀邊界。 |

## 可重跑命令

```text
python -m unittest discover -s tests
python -m mypy --strict library tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py
python -m py_compile library/NLP/python/rule_parser/contracts.py library/NLP/python/rule_parser/parser.py library/NLP/python/rule_parser/__init__.py tests/test_nlp_rule_parser.py
```

上述嚴格型別檢查結果為「Success: no issues found in 11 source files」。Smoke test 驗證 `pickup=Home|dropoff=Station` 得到 `INCOMPLETE`／`SPLIT_ACROSS_FRAMES`，且 `extraction is None`。

## 工作區隔離註記

審閱期間發現 `AGENTS.md` 與 `Workflow.md` 有未暫存刪除，非本 Ticket 變更；它們已明確排除於提交範圍，未還原、暫存或修改。此 Ticket 只提交上列審閱對象與其必要 README／測試；四個來源專案均未被修改。

## 後續限制

本模組只能解析呼叫端明確提供的固定規則。自由文字意圖、LLM 或 provider 接入，必須留給後續已核准工單。
