# Code Review：01 Router framework POC 核心

## 範圍

- SPEC：`SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H`
- 變更：`CHG-20260802-002`
- Ticket：`01-poc-router-core`
- 審閱對象：`library/workflow_router/`、`tests/test_workflow_router.py`、`requirements-dev.txt` 與 Router 流程文件索引。

## 審閱結論

`APPROVED`

## 必要驗證項目與證據

| 項目 | 結果 | 證據 |
| --- | --- | --- |
| 清晰易懂與 P0 強型別 | 通過 | 所有跨邊界資料皆為 strict、frozen Pydantic model 或具名 dataclass；有限關卡、事件、交付成熟度、結果、阻擋碼與引用狀態皆為 Enum。`mypy --strict` 通過，未使用 `Any` 或未驗證動態輸入。 |
| 流程正確與 fail-closed | 通過 | `RouterEngine` 只依 Profile 的 `(stage, event)` 規則前進；缺 transition、來源、核准或 delivery stage 與 Profile 不符時輸出具名 `SUSPEND` blocker；`WAYFINDER_NO_GO` 只能到 `STOPPED`。 |
| Context 隔離與可追溯 | 通過 | `ContextPacket` 保存原文且不在 `RouterGraphState`、Temporal input 或 `CitationLedger` 中出現；ledger 只保存 `source + revision + span → side_context_id → consumer_fingerprint → target_artifact`。同 event retry 穩定重用 ID，新的 event 必定產生新 ID。 |
| LangGraph 邊界 | 通過 | 僅使用公開 `StateGraph`；graph 的動態分支被限制為 `complete`／`blocked`，Agent 不能提供任意 node 名稱。 |
| Agents、Temporal、MCP 邊界 | 通過 | Agents adapter 只解析 router allowlist 內 `CapabilityRef` 且沒有 handoff；MCP adapter 只讀指定 URI 並要求唯一 text resource；Temporal 使用 typed signal／query、Activity 與 durable wait，未將原文放入 workflow state。 |
| 測試與 smoke | 通過 | `python -m unittest discover -s tests`：48 passed，涵蓋 INTAKE、GO／NO-GO、核准、成熟度不符、引用重試、revision invalidation、LangGraph 分支與四框架無服務 adapter smoke。 |
| 依賴與安全 | 通過 | 開發依賴以範圍固定的 Pydantic、LangGraph、Temporal、OpenAI Agents SDK、MCP 與 mypy 組成；沒有 Secret、網路呼叫、真實模型、Temporal worker 或 MCP server。 |
| 規格與文件一致 | 通過 | `Workflow.md §0` 定義 Profile、POC→MVP→COMMERCIAL、descriptor／packet 分離及節點責任；`AGENTS.md` 僅作該章節索引，未重複定義流程。 |

## 可重跑命令

```text
python -m unittest discover -s tests
python -m mypy --strict library tests
python -m py_compile library/workflow_router/__init__.py library/workflow_router/contracts.py library/workflow_router/profile.py library/workflow_router/router.py library/workflow_router/graph.py library/workflow_router/integrations.py library/workflow_router/temporal_runtime.py tests/test_workflow_router.py
git diff --check
```

結果：48 tests passed；嚴格型別檢查為「Success: no issues found in 54 source files」；編譯與 diff whitespace 檢查通過。

## 已知邊界與下一步

本 POC 不執行真實模型、Temporal worker、MCP server、資料庫、網路或任何被接管專案的寫入。將任一真實專案接入前，必須以該專案的 POC Profile 重走 Wayfinder、Architecture、Grill、SPEC、ticket 與核准流程；不得將這個 POC 的 Profile 直接當作商用設定。
