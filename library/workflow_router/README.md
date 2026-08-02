# Workflow Router POC

此模組是「可套用於不同專案的流程引擎」POC，不是任何專案的產品實作。

## 節點與責任

- `contracts.py`：Pydantic 強型別的 `RouterState`、`RouterEvent`、`RouterDecision`、`ContextView` 與引用邊。
- `profile.py`：個別專案的 POC／MVP／商用關卡、來源需求和 capability allowlist；核心不硬編碼商業規則。
- `router.py`：純 transition、最小來源選擇、暫存 Context packet 和 metadata-only citation ledger。
- `graph.py`：LangGraph 只在 `complete`／`blocked` 的封閉分支中執行 transition。
- `integrations.py`：OpenAI Agents SDK 只解析已選中的 capability；MCP 只讀已選中的 source URI。
- `temporal_runtime.py`：Temporal signal、query 和持久化 human wait；不在 Workflow 內執行 I/O。

原文只存在 `ContextPacket`，此物件不可放入 graph state、checkpoint、Temporal history 或 `CitationLedger`。Ledger 只投影：

```text
source + revision + span → side_context_id → consumer_fingerprint → target_artifact
```

本 POC 不啟動模型、Temporal worker 或 MCP server。
