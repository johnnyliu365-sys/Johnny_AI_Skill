# 29｜工作主線與單票狀態分離

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN`；Owner 2026-10-18 改進清單項目 01 的最小獨立切片 |
| Authority | 既有 `PRD-20260805-009`／`CHG-20260805-009`、`modules/spec/workflow-governance.md` AC 1–4 及本次 Owner 明示的主線／單票區分；不新增 PRD |
| Source baseline | 本票所在控制面 commit；實作時精確 pin |
| Implementation language | Python 3.11、既有 skill reference Markdown |
| Implementation owner / reviewer | 不同席位，獨立 worktree |
| Profile | `STANDARD`；純 metadata 投影，不派工或執行 effect |

## 邊界宣告

```johnny-boundary
modify = skills/johnny-project-takeover/references/agent-context-lifecycle.md
modify = library/workflow_router/__init__.py
create = library/workflow_router/mainline_projection.py
create = tests/test_mainline_projection.py
forbid = modules/spec/
forbid = doc/requirements/
forbid = library/workflow_router/router.py
forbid = library/workflow_router/guarded_integration.py
```

先重用既有 `PlanningLaneState.active_ticket_refs`、`DependentProposal` 和 Review 的
dependency graph 概念；它們分別只覆蓋單次 dispatch、return wake 和審閱叢集，
不能直接冒充跨票工作主線。新模組限於一個純、不可變、metadata-only 的主線讀取
投影，不是第二個 Router、Grant、Ticket 狀態機或效應入口。建立新檔是因既有
`contracts.py` 已承載多種責任，主線投影有獨立輸入、輸出與驗收。

## Objective／Expected

Root 可保存完整主線目標、已准入的票與待辦；implementer Context 仍只綁一張票。
單票完成不是主線完成。投影只提出下一張需要由既有 Router **重新核對**的候選，
不得自己授予 dispatch、效應、整合或結案權限。

1. 輸入是 project／mainline／source revision 綁定的具名 ticket 節點：每節點有
   ticket/ref revision、required/optional、有限狀態、精確 dependency refs、
   admission/evidence refs（若適用）。拒絕重複、未知 dependency、自相依、循環、
   不合法狀態組合；只保留 metadata，無路徑、prompt 或來源正文。
2. 輸出分列 `ready_for_recheck`、`waiting`、`incomplete_required` 與
   `closure_candidate`。`ready_for_recheck` 不是已准入授權；每次 effect 前仍走
   原 Router／來源／Grant。`closure_candidate` 也不是正式 `DONE`，仍須由既有
   Review／證據准入確認。
3. 固定回放：前端工作主線有血壓測試 A、無相依測試 B、依賴 A 的 C。
   A 單票驗證完但 B/C 未完時 `closure_candidate=false`；A 等 Owner 時 B 可以是
   `ready_for_recheck`，C 不可以；B 完成後 A 仍待決，主線仍開放；optional 非必要
   待辦不會無限阻擋候選結案。
4. Skill 的 Agent Context reference 只補一條邊界：票級 view 關閉不等於主線完成；
   reviewer 回到既有 Router 依主線投影選下一個需重新准入的票。通用文字不放
   Vita360 路徑、票號、SHA、模型名。

Acceptance：正向與反向測試皆跑；對「首票完成→主線完成」及「相依票借行」
做 reviewer 自行反向突變，紅後還原綠。舊 ticket/dispatch/ref 讀取不變。
本票不宣稱已實現可信 target 主線 Source adapter 或正式結案 admission；若缺
這些仍保持清單 01 未勾選，不得用投影自報填滿證據。
Run：`python -m pytest tests/test_mainline_projection.py -q`、
`mypy --strict library/workflow_router/mainline_projection.py`、`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整候選 SHA、變更檔、
測試、未解來源與權限缺口。實作者不整合、不推送。
