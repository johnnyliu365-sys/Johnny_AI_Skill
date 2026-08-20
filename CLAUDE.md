# CLAUDE.md

這個檔案存在的唯一理由：Claude Code 自動載入 `CLAUDE.md`，不自動載入
`AGENTS.md`。本專案的入口是 **[`AGENTS.md`](AGENTS.md)**，其他 agent host 讀的
也是那一份。**這裡不放規則，只把你送到規則那裡**——多一份副本就會漂移，而漂移的
副本比沒有更糟。

## 動手前

先讀 [`AGENTS.md`](AGENTS.md) 的「啟動順序」，然後照它走。它會把你路由到
[`Workflow.md`](Workflow.md) 與被指定的 skill reference。

不要載入完整 Workflow、全部 references 或整個 library。

## 這一條最常被違反

> 找不到、讀不到、版本不符或索引競爭時，在 mutation 前 `HALT / ROUTE_REFERENCE_INVALID`，
> **不得憑記憶補規則**。 —— `AGENTS.md`

實測的失敗形狀（2026-08-20 那一週，記在
[`doc/runbooks/dispatch-model-profile.md`](doc/runbooks/dispatch-model-profile.md)）：
規範就在庫裡，但沒進 context，於是被「生成一個看起來合理的版本」取代——票的格式、
模型分層、worktree 歸屬、派工長度全都是這樣編出來的。

**編造出來的程序不會報錯。** 它產出結構完整、術語正確的東西，沒有任何訊號顯示它沒被
查證過。所以「我好像知道該怎麼寫」就是要去讀的時候，不是可以動手的時候。

## 三份你八成需要但不會自己想到要開的檔案

| 要做什麼 | 先讀哪一份 |
| --- | --- |
| 寫任何一張票 | [`modules/tickets/TEMPLATE.md`](modules/tickets/TEMPLATE.md)——欄位是固定的，不要自創 |
| 派工給實作者 | [`doc/runbooks/dispatch-model-profile.md`](doc/runbooks/dispatch-model-profile.md)——角色分層、依難度選模型、最小派送 |
| debug 任何「奇怪」的問題 | [`modules/tickets/PITFALL-REGISTER.md`](modules/tickets/PITFALL-REGISTER.md)——多數「新」問題是某一族的再現 |

## 本機環境

`py -3.11`（無 `python`）、無 pwsh、主控台 cp950、工作副本 CRLF。
**同一個 checkout 一次只能跑一個 pytest**——並行會污染共享 runtime root，
那是登記簿 C1／B2 那一族。
