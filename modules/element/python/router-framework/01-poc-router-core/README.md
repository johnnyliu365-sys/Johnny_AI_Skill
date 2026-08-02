# Router framework POC 核心｜元素索引

| 欄位 | 內容 |
| --- | --- |
| 對應 SPEC | `SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H` |
| 對應 Ticket | `01-poc-router-core` |
| 語言 | Python 3.11 |
| 狀態 | `DONE` |

## 責任與程式對應

- `library/workflow_router/contracts.py`：Pydantic 強型別 Router／引用契約；`ContextPacket` 與持久化 descriptor 分離。
- `library/workflow_router/profile.py`：每個專案的 Profile、交付成熟度與封閉 transition 規則。
- `library/workflow_router/router.py`：純 decision、最小來源解析及不保存原文的 citation ledger。
- `library/workflow_router/graph.py`：LangGraph 的 `complete`／`blocked` 封閉分支。
- `library/workflow_router/integrations.py`：OpenAI Agents SDK capability 與 MCP resource 的公開介面 adapter。
- `library/workflow_router/temporal_runtime.py`：Temporal typed signal、query、Activity 與 human-wait skeleton。
- `tests/test_workflow_router.py`：POC 的行為、fail-closed、引用映射與無外部服務 smoke 證據。

## 驗證

```text
python -m unittest discover -s tests
python -m mypy --strict library tests
python -m py_compile library/workflow_router/__init__.py library/workflow_router/contracts.py library/workflow_router/profile.py library/workflow_router/router.py library/workflow_router/graph.py library/workflow_router/integrations.py library/workflow_router/temporal_runtime.py tests/test_workflow_router.py
```

驗證結果：48 tests passed；`mypy --strict` 在 54 個 source files 無問題；編譯檢查通過。本元素不啟動模型、Temporal worker、MCP server、網路或外部 Provider。

## 禁止用途

- 不可將 `ContextPacket` 原文寫入共享 Context、LangGraph checkpoint、Temporal history 或 citation ledger。
- 不可繞過 Profile 的 transition／authority／source／capability allowlist。
- 不可將 POC 的結果自動宣稱為 MVP 或商用標準；升級必須經由 CHG 與新的 Profile。
