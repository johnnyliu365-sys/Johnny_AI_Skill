# 專案流程 Router 框架 POC 規格

| 欄位 | 內容 |
| --- | --- |
| 規格 ID | `SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H` |
| 規格狀態 | `APPROVED` |
| 撰寫 AI／worktree | Codex／目前工作區 |
| 專屬 Context | `doc/context/router-framework/main.md` |
| PRD 索引 | `PRD-20260802-002` |
| 需求變更 | `CHG-20260802-002` |
| 共用 Context 回掛 | `CONTEXT.md §衍生 SPEC 索引` |

## 目標與不做範圍

建立一個不含個別產品規則的可重用 Python Router framework。各專案以已驗證的 Profile 定義自己的 POC、MVP 與商用階段門檻。

不做真實 LLM、Temporal server、外部 MCP、資料庫、部署、Provider、Secret 或商業決策。

## 架構與公開契約

```text
library/workflow_router/
  contracts.py       Pydantic 值物件、狀態、事件、決策與引用契約
  profile.py         Profile 與封閉 transition 規則
  router.py          純 Router engine、Context descriptor、citation ledger
  graph.py           LangGraph StateGraph adapter
  integrations.py    Agents SDK capability 與 MCP source port adapter
  temporal_runtime.py Temporal human approval workflow skeleton
```

- `RouterEngine` 只依 `ProjectWorkflowProfile` 對強型別 state/event 產生 `RouterDecision`。
- LangGraph 僅能跳至宣告的 `complete` 或 `blocked` 分支；不得接受 Agent 產生的任意節點名稱。
- Context 原文不進 graph state、checkpoint、Temporal history 或 citation ledger。
- `ContextReference` 關閉後形成 `source + revision + span → side_context_id → consumer_fingerprint → target_artifact` 映射。
- MCP adapter 只接受 `RouterDecision.required_sources`；Agents adapter 只解析 `eligible_capabilities`。
- Temporal workflow 只處理 typed signal、query 與持久等待；所有非決定性 I/O 留在 activity／adapter 邊界。

## 驗收條件

1. `INTAKE`、`WAYFINDER_GO`、`WAYFINDER_NO_GO` 及缺少核准的狀態都有可重現的 Router 結果。
2. 兩次不同 event 對同一 source span 引用，產生兩個不同 side Context ID；同一 event 重試保持同一 ID。
3. 已關閉引用可依 source 與 target 查詢；revision 更新可使引用失效。
4. 建立的 LangGraph 可以對合法結果走 `complete`，對 `SUSPEND`／`STOP` 走 `blocked`。
5. Agents、MCP 與 Temporal 類別可在無網路、無服務、無 API key 的環境被載入和以 fake adapter 驗證。

## 核准紀錄

- 決策者：使用者。
- 日期：2026-08-02（Asia/Taipei）。
- 核准範圍：Router framework POC 規格，以及下列單一垂直 ticket 的實作。

## 實作回掛

- 交付元素：`modules/element/python/router-framework/01-poc-router-core/README.md`。
- 驗證：48 tests passed；`python -m mypy --strict library tests` 在 54 個 source files 無問題；`py_compile` 通過。
- Review：`doc/reviews/router-framework/01-poc-router-core-code-review.md`（`APPROVED`）。
- 限制：此回掛僅證明本機 POC；要進入任一真實專案的 MVP 或商用 Profile，仍必須走新的 CHG 與完整 Workflow。
