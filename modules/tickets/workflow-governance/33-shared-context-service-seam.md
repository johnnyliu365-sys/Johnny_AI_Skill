# 33｜Shared Context 決策責任拆分（TEST → A）

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN / DISPATCHABLE`；A 通過獨審前，後續 B 不得派工 |
| Authority | 沿用 `PRD-20260805-009`／`CHG-20260805-009`、`modules/spec/workflow-governance.md`、Ticket 25 已整合的 TEST→A→B 規則；不建立新需求 |
| Baseline | 派工時精確釘選控制分支 HEAD；實作者以自己的 repo-contained worktree 工作 |
| Profile／roles | `STANDARD`；實作者為當前已驗證可勝任的低成本模型，另一席獨立審閱；審閱強度不得低於實作 |
| Nature | 現有純 Python Router 責任拆分；不含 Host、Git、網路或產品外部 effect |

## 邊界宣告

```johnny-boundary
modify = library/workflow_router/router.py
modify = tests/test_workflow_router.py
create = library/workflow_router/shared_context_service.py
create = tests/test_shared_context_service.py
forbid = modules/spec/
forbid = doc/requirements/
forbid = skills/
forbid = library/workflow_router/contracts.py
```

兩個新檔各有獨立責任：純 Shared Context 決策與其聚焦測試。優先重用既有 contracts、profile、測試 fixture，不建立第二個 Router、狀態機或泛用框架；不碰其他 Router 能力。原始碼不得混入 Owner prompt／工單敘事。

## TEST：先固定能力與承接證據

- 公開產品入口：`RouterEngine.decide_shared_context_access(request, state, profile)`。
- 現有行為：context/profile 不匹配、revision stale、角色與 capability、sealed read 的 stage/lifecycle、draft 建立／修訂、已核准變更、seal，以及非法操作都必須維持既有決策與 resulting state。
- 先跑 `tests/test_workflow_router.py` 的 shared-context 行為格並記錄基準結果；列出哪些測試真正穿過公開入口，哪些只驗 contract。若既有 cell 不足，先在既有測試補公開入口行為斷言，再移產品邏輯。
- mutation target 在 A 後必須是新 service 裡的實際分支；獨審將其故意放寬或改錯，使公開 Router 行為格轉紅，精確還原後轉綠。只測 Router 是否委派不足以承接。

## A：單一責任搬遷

把 `router.py` 的 Shared Context lifecycle/role/stage/revision 決策，連同只屬於此能力的決策建構 helper，搬到 `shared_context_service.py`。`RouterEngine.decide_shared_context_access` 保留公開簽章與薄委派；不得改變既有輸入、輸出、優先順序或權限。聚焦 service 測試放在 `tests/test_shared_context_service.py`；既有公開入口測試保留到 B 的承接核准，不得先刪。

## Acceptance／停止

- 正常：既有公開入口與 service 聚焦測試都通過；Router 不再持有 Shared Context 規則；新 service 的行為 mutation 會讓公開入口 cell 紅→還原綠。
- 失敗／邊界：候選版載入來源必須是本票 candidate，不得只跑舊 baseline；任何測試只驗委派、改變 decision precedence、舊公開行為消失或新增 framework 都拒收。
- A 通過後只回 `ACTION_COMPLETED` 供主審處理；B（測試 seam/退役）必須依賴 A 的審閱與候選行為證據，另票精確授權。
- 遇既有 SPEC 語意不足、需新增產品能力或越界路徑，回 `CHANGE_DETECTED`，不得自行擴張。

Run：`python -m pytest tests/test_workflow_router.py tests/test_shared_context_service.py -q`、strict mypy（若目前設定覆蓋該模組）、`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選完整 SHA、實際修改檔案、基準與候選命令、公開入口 cell、service mutation 紅／綠證據、finding、偏差。
