# 工作進度索引

本檔只提供目前專案進度來源的入口，不是事件台帳、ticket 副本、handoff payload、
receipt registry 或授權來源。Router 與各角色不得為單次 dispatch、implementation、
review、correction 或 integration 在此追加紀錄。

## 正式來源索引

| 資訊 | 正式來源 |
| --- | --- |
| 專案邊界與功能索引 | [`../CONTEXT.md`](../CONTEXT.md) |
| 產品需求 | [`../PRD.md`](../PRD.md) |
| 需求變更 | [`RequirementChangeLog.md`](RequirementChangeLog.md) |
| 排程與里程碑 | [`../ProjectSchedule.md`](../ProjectSchedule.md) |
| 核准規格 | [`../modules/spec/`](../modules/spec/) |
| 工單樹 | [`../modules/tickets/`](../modules/tickets/) |
| 審閱樹 | [`reviews/`](reviews/) |
| 交接樹 | [`handoffs/`](handoffs/) |
| 架構決策 | [`adr/`](adr/) |
| 通用模組目錄 | [`../library/MODULE_CATALOG.md`](../library/MODULE_CATALOG.md) |

## 寫入規則

- 本檔只在專案層級的正式來源入口改變時，隨同該變更更新。
- ticket 的狀態、證據與例外只寫入該 ticket／review 的 exact leaf；本檔只引用索引。
- 角色完成工作時回傳 typed event 與 commit／leaf identifiers，不建立
  `WorkProgressReport.md`-only commit。
- 本檔不宣告 active dispatch，也不能產生、取代或補造 receipt／owner authority。

## 舊台帳溯源

2026-08-01 至 2026-08-15 的舊式扁平 PRG 台帳保留於 Git commit
`1672d0ed1be6b1a44fd4cf1fd01fb26563b83744` 及其歷史中，不在目前工作 Context
重複保存。需要稽核時應依 ticket、review 或 commit identifier 定點讀取，不得載入
完整舊台帳。
