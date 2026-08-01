# Code Review：02 Python NLP 文字契約

## 範圍

- SPEC：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`
- 變更：`CHG-20260801-001`
- Ticket：`02-python-nlp-contracts`
- 審閱對象：`library/NLP/python/text_contracts/`、`tests/test_nlp_text_contracts.py` 與 `requirements-dev.txt`

## 審閱結論

`APPROVED`

## 驗收與證據

| 項目 | 結果 | 證據 |
| --- | --- | --- |
| 中文與 ASCII 文字的穩定正規化 | 通過 | `TextContractTests.test_normalizes_chinese_and_ascii_text_stably` |
| 空白、控制字元、過長文字與未驗證外部來源 fail closed | 通過 | `TextContractTests.test_rejects_blank_control_too_long_and_unvalidated_external_input` 與 smoke test |
| 分類與欄位擷取不跨公開邊界傳遞裸 `dict` 或字串狀態 | 通過 | `TextLabel`、`TextFieldName`、不可變 DTO 與 tuple 欄位集合 |
| Python 編譯檢查 | 通過 | `python -m py_compile ...` |
| 嚴格型別檢查 | 通過 | `python -m mypy --strict library tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`：7 個來源檔無問題 |
| 回歸測試 | 通過 | `python -m unittest discover -s tests`：5 項通過 |

## P0 型別與邊界檢查

- 公開模型全為 `@dataclass(frozen=True, slots=True)`、`Enum` 或具名值物件；未使用 `Any`、裸 `dict` 或未驗證動態物件。
- `TextInput` 在建構時驗證型別；`normalize_text` 對未驗證外部來源、控制字元、空白和超長文字回傳具名 `NormalizationRejected`，不產生假資料。
- 模組不含 HTTP、LLM、資料庫、LINE、支付或任何實體 provider 呼叫。

## 來源與安全檢查

- 所有新增檔案均位於目前工作區；未修改、搬移、刪除或新增任何引用專案檔案。
- 開發期型別工具固定記錄於 `requirements-dev.txt`，版本為 `mypy==2.3.0`。
- 未讀取、輸出或保存 Secret。

## 後續限制

此模組只負責文字契約與正規化。規則解析、provider 連接埠與任何業務意圖，仍須由後續已核准工單實作。
