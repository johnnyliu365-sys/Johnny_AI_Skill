# Code Review：07 Python 可靠性核心

## 範圍

- SPEC：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`
- 變更：`CHG-20260801-001`
- Ticket：`07-python-reliability-core`
- 審閱對象：`library/功能集群/python/reliability_core/`、`library/功能集群/python/README.md` 與 `tests/test_reliability_core.py`

## 審閱結論

`APPROVED`

## 必要驗證項目與證據

| 項目 | 結果 | 證據 |
| --- | --- | --- |
| 清晰易懂與 P0 強型別 | 通過 | scope、一次性鍵、job、worker、版本與 audit sequence 均為不可變具名值物件；狀態與拒絕原因使用 Enum；輸入／結果以 DTO、union 與 `OutboxSender` Protocol 表達，無 `Any`、裸 `dict` 或字串狀態機。 |
| 編碼規範與分層 | 通過 | `reliability_core/` 只含純記憶體快照、狀態轉換、worker façade 與 fake sender；無持久化、排程、HTTP、Provider SDK 或來源專案依賴。 |
| 邏輯正確 | 通過 | 同 key 僅建立一次；claim 僅接受 `PENDING`；處理前同時驗證 `CLAIMED`、worker 擁有權與 `JobVersion`；成功與 fake 失敗都留下明確 terminal state 及 audit。 |
| 邊界與異常 | 通過 | 未註冊 scope、重複 key、找不到 job、非 pending claim、非 claimed process、過期版本、worker 不符與 emergency stop 均 fail closed；注入 sender 以 runtime-checkable Protocol 在公開邊界驗證。 |
| 安全與效能 | 通過 | fake sender 絕不連網，僅增加本地計數；沒有真實 tenant、訊息、payload、資料庫、憑證、Secret 或 PII。每次轉換只掃描小型不可變 tuple，無 I/O、資源配置或背景工作。 |
| 測試覆蓋與 smoke test | 通過 | 行為測試覆蓋 enqueue→claim→complete、重複 key、未知 scope、第二 worker、stale version、sender failure、emergency stop 與 worker façade。`python -m unittest discover -s tests`：29 passed；本地 smoke 流程輸出 `completed` 與 audit 數 3。 |
| 依賴合理 | 通過 | 未新增執行期依賴；僅使用 Python 標準函式庫的 dataclass、Enum、Protocol 與 TypeAlias。 |
| 專案規格符合性 | 通過 | 功能與 Ticket 07 的 outbox、worker、expected-state guard、emergency stop 與 audit 結果一致；未修改四個來源專案，也未啟動任何外部副作用。 |

## 可重跑命令

```text
python -m unittest discover -s tests
python -m mypy --strict library tests/test_reliability_core.py tests/test_payment_provider_reconciliation.py tests/test_payment_contracts_ledger.py tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py
python -m py_compile library/功能集群/__init__.py library/功能集群/python/__init__.py library/功能集群/python/reliability_core/__init__.py library/功能集群/python/reliability_core/reliability_core.py tests/test_reliability_core.py
```

嚴格型別檢查結果為「Success: no issues found in 34 source files」。Smoke test 使用 `OutboxWorker` 與 `FakeOutboxSender(SUCCESS)`，完成的 job 狀態為 `completed`，audit 數量為 3。

## 工作區隔離註記

工作區既有的 `Workflow.md` 修改及未追蹤的 `Defined_wayfinder.md`、`template/` 均不屬於本 Ticket，已排除於提交範圍。四個來源專案未被修改、搬移、刪除或新增任何檔案。

## 後續限制

此模組是單一程序內的不可變 fake-first 狀態機，沒有持久化、跨程序原子 claim、併發鎖、重試排程、實際投遞、授權、Provider、LINE、資料庫或訊息佇列。採用端若需要上述能力，須在核准的外部邊界另立需求、規格與工單。
