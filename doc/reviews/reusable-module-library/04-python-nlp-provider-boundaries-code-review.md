# Code Review：04 Python NLP Provider 邊界

## 範圍

- SPEC：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`
- 變更：`CHG-20260801-001`
- Ticket：`04-python-nlp-provider-boundaries`
- 審閱對象：`library/NLP/python/provider_ports/`、`library/NLP/python/README.md` 與 `tests/test_nlp_provider_ports.py`

## 審閱結論

`APPROVED`

## 必要驗證項目與證據

| 項目 | 結果 | 證據 |
| --- | --- | --- |
| 清晰易懂與 P0 強型別 | 通過 | 公開 API 使用不可變 dataclass、Enum、Protocol、具名值物件、union 與顯式 `None`；無 `Any`、裸 `dict` 或動態 payload 進入結果 DTO。 |
| 編碼規範與分層 | 通過 | `contracts.py` 定義 port 與領域契約，`validator.py` 是唯一 raw payload 邊界，`fake_provider.py` 是純本地測試 adapter。 |
| 邏輯正確 | 通過 | 成功結果會綁定原請求文字與允許標籤；暫時、永久、逾時、驗證、限流與結構無效皆有具名分類及固定 retryability。 |
| 邊界與異常 | 通過 | validator 僅接受完整且無未知欄位的字串鍵 payload；缺欄、額外欄、未知標籤、布林或非法信心值一律回傳 `INVALID_STRUCTURE`。 |
| 安全與效能 | 通過 | 無 HTTP、Gemini、影像資料、API key、prompt、secret、資料庫或日誌；只處理單一小型 mapping 並立即轉換或拒絕。 |
| 測試覆蓋與 smoke test | 通過 | `python -m unittest discover -s tests`：16 passed；未知 payload 無法跨 adapter 的 smoke test 通過。 |
| 依賴合理 | 通過 | 未新增執行期依賴；僅沿用既有本地文字契約與 `mypy` 開發期工具。 |
| 專案規格符合性 | 通過 | 僅重建通用 port、驗證與 fake adapter；所有來源專案維持唯讀。 |

## 可重跑命令

```text
python -m unittest discover -s tests
python -m mypy --strict library tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py
python -m py_compile library/NLP/python/provider_ports/contracts.py library/NLP/python/provider_ports/validator.py library/NLP/python/provider_ports/fake_provider.py library/NLP/python/provider_ports/__init__.py tests/test_nlp_provider_ports.py
```

嚴格型別檢查結果為「Success: no issues found in 16 source files」。Smoke test 以含未知欄位的 raw payload 驗證得到 `ProviderFailure(INVALID_STRUCTURE)`，沒有產生 `ProviderSuccess`。

## 工作區隔離註記

開始前已建立 checkpoint `76c9cbd` 與本地 rollback tag `rollback/ticket-04-start-20260801`。工作區既有的 `Workflow.md` 修改及未追蹤的 `Defined_wayfinder.md`、`template/` 均不屬於本 Ticket，已排除於提交範圍；四個來源專案沒有被修改。

## 後續限制

本模組只提供本地 fake port 與 adapter-boundary 驗證。任何實體 provider、網路、影像、憑證或領域決策都必須經過新的需求、規格與工單核准。
