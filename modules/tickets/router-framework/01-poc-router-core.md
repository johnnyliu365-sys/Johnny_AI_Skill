# 01｜Router framework POC 核心

| 欄位 | 內容 |
| --- | --- |
| 對應規格 | `SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H` |
| 需求變更 | `CHG-20260802-002` |
| 狀態 | `DONE` |
| 環境 | `LOCAL` |
| Owner | Codex／目前工作區 |

## 可觀察結果

開發者可以以一個強型別 Profile 對 Router event 求得唯一合法決策、最小來源 descriptor 與 capability allowlist；兩次 Context 引用可由不同 ID 追溯至 Grill、SPEC 或 ticket，且共享儲存不含原文。

## In Scope

- `library/workflow_router/` 與 `tests/test_workflow_router.py`。
- Pydantic、LangGraph、OpenAI Agents SDK、Temporal、MCP 的公開介面 adapter。
- 本機 fake source、citation ledger 與無網路測試。

## Out of Scope

- 任何真實模型、Temporal worker、MCP server、網路、資料庫、Secret、部署或專案自動寫入。

## TDD 切點

1. 紅燈：Router 模組不存在，無法驗證 INTAKE、GO、NO-GO 與 fail-closed。
2. 綠燈：Profile 的封閉 transition 只產生合法 `RouterDecision`。
3. 回歸：不同 event 的同段引用 ID 不同；同 event retry 相同；中央 ledger 不保存原文；更新 revision 後引用失效。
4. Smoke：LangGraph、Agents SDK、Temporal 與 MCP adapter 在無外部服務環境可載入，並完成一輪 fake route。

## 完成條件

- `python -m unittest discover -s tests`、`python -m mypy --strict library tests`、`python -m py_compile` 與指定 smoke test 通過。
- 更新 element 索引、Progress、review report 與 Context／SPEC 回掛。

## 完成紀錄

- 實作：`library/workflow_router/` 的 contracts、Profile、Router engine、Context resolver／ledger、LangGraph、Agents SDK／MCP adapter 與 Temporal human-wait skeleton。
- 證據：48 tests passed；`mypy --strict` 在 54 個 source files 無問題；`py_compile` 通過；無網路 adapter smoke 通過。
- 交付索引：`modules/element/python/router-framework/01-poc-router-core/README.md`。
- 審閱：`doc/reviews/router-framework/01-poc-router-core-code-review.md`（`APPROVED`）。
