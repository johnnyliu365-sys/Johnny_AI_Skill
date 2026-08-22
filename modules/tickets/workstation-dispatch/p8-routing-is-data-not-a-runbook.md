# P8｜模型分層是資料，不是 runbook

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（外部參考啟發：GAL 的 `config.json#executorRouting` 與 `routing.rs`） |
| 第一步排查起點 | `doc/runbooks/dispatch-model-profile.md`（規則現在活在這裡，只靠人記得讀） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 新增 `library/local_orchestration/executor_routing.py` 與其測試 |
| 禁止修改 | `dispatch_session.py`、`dispatch_authority.py`、`worker_assignment.py`、`work_queue.py`、`document_mutation_gate.py` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/executor_routing.py
create = library/local_orchestration/executor_routing.py
modify = tests/test_executor_routing.py
create = tests/test_executor_routing.py
forbid = library/local_orchestration/dispatch_session.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

「這張票該派給哪一層」由**可讀的資料**回答，而不是由控制面記得去讀一份 runbook。
派工時查得到、對不上時具名拒絕。

## 為什麼

本專案自己反覆學到同一件事：**規則只約束記得它的人，閘門約束所有人**（governance 08、
11、15、17 各自從不同方向撞到）。而模型分層是本專案**唯一還純靠自律**的核心規則——
它活在 `dispatch-model-profile.md`，控制面沒讀就會自己編一套，而編出來的程序不會報錯。

實測前例：控制面曾經完全沒讀 `model-role-routing.md`，把 UI／CSS 工作全派在自己那一層，
燒掉 114 萬 token。那不是判斷失誤，是規則沒有落點。

外部參考（GAL，`crates/dispatch/src/routing.rs`）把同一件事做成 `RoutingTable` 型別解析
`config.json#executorRouting`。方向對，我們自己也早該這樣。

## 要達成的事

一個可讀的路由表：**角色×難度 → 執行層**，加上解析與查詢。至少要能表達現行規則：

- 一般小票 → Sonnet 5 high
- 不能拆的困難票 → Opus 5 Extra
- **Opus 實際做過且失敗** → Fable 5（不是預判「這題很難」就直接升）
- owner 明示指派 → 覆寫，但**必須留下 override 紀錄**

**升級條件是狀態，不是形容詞。** 「Opus 試過且失敗」是可查證的事實（該票有過一次
Opus 實作且未通過審閱），路由表必須要求那個事實，不接受呼叫端自稱「這題很難」。

## TDD 設計

1. 正常行為：給定角色與難度，查得到唯一的執行層。
2. 規則違反／輸入錯誤：未涵蓋的組合 → **具名拒絕，不得回傳預設值**；
   宣稱升級但無失敗紀錄 → 具名拒絕。
3. 外部失敗／fail-closed：路由表讀不到 → 具名拒絕，**不得退化成「用預設層」**
   （那是 C 族在派工上的形狀——安靜地用錯模型，沒有任何訊號）。
4. 回歸保護：本模組不得取得發放 receipt、claim 或整合的能力；以命名空間斷言證明。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑 |
| 2 | null／空字串／陣列 | **是** | 空路由表、未涵蓋組合、空角色三者各自具名，且**都不得是「放行」** |
| 3 | 權限繞過 | **是** | owner 覆寫必須帶紀錄；呼叫端不得自稱難度繞過升級條件 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | **是** | 未涵蓋、讀取失敗、升級條件不滿足、覆寫無紀錄各自可區分 |
| 6 | 例外是否會拋出 | 是 | 每個讀取失敗路徑 fail-closed |

## 完成定義與證據

- **反向突變證據**：至少三組——讓未涵蓋組合回傳預設層、讓讀取失敗回傳預設層、
  讓升級不檢查失敗紀錄；各指名哪個測試轉紅、還原後轉綠。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

把路由表接進 `dispatch_session`（接線另票——先讓資料存在且可查，再談誰呼叫它）；
自動偵測難度（難度由開票者判斷，本票只負責「判斷結果 → 執行層」的映射）。

## 正式環境移植 SOP

不適用（本機資料與查詢；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = P8
title = 模型分層是資料，不是 runbook
state = IN_PROGRESS
stage = D | 路由表與解析 | OPEN
stage = E | 升級條件是狀態 | OPEN
stage = M | 突變驗證 | OPEN
```
