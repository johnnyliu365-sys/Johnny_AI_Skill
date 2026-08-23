# ADR-20260823-016｜Codex CLI 跨生命週期喚醒橋接

- 日期：`2026-08-23（Asia/Taipei）`
- 狀態：`ACCEPTED`
- 決策者：`owner`
- 關聯規格：[`modules/spec/receipt-bound-role-supervision.md`](../../modules/spec/receipt-bound-role-supervision.md)；任何實作前必須先以新的受管制需求變更擴充其 host 範圍。
- 關聯需求變更：不適用（本 ADR 只記錄架構決策，不授權 source mutation 或 provider effect）

## 背景與問題

`ADR-20260823-014` 已把 runner 的責任收窄為跨生命週期事件送達橋接：同步的
「派工 → 等待 → 收結果 → 審閱」同一生命週期流程以 host 原生 completion callback
為準，不需要 runner、queue、receipt 或 gateway。

Codex 的 `wait_agent` 只在 parent 尚存活時提供 completion callback；它不會在 parent
終止後復活 Desktop session。因此需要跨 session／跨機器交接時，不能把「重新叫醒原
Desktop parent」假定為現有能力。

本機 2026-08-23 的只讀 capability readback 為：已安裝 `codex-cli 0.146.1`，且 CLI
提供非互動的 `codex exec` 與 JSON 輸出；Windows 上 `codex app-server daemon` 明確拒絕
其 daemon lifecycle。這證明不能把 Windows 常駐 app-server 當作 Desktop parent resume
的 gateway，但尚未證明任何真實 Codex CLI 喚醒送達。

## 決策

1. 同一生命週期的派工一律維持 `wait_agent`／host 原生 callback 的同步路徑。沒有橋
   不是 admission blocker，也不得為此建立 heartbeat、polling 或 receipt。
2. 跨生命週期的 bridge 交付的是 target-owned、可驗證的 handoff artifact，不交付、
   不復原，也不宣稱能復原原本的 Desktop parent session。收到 artifact 的是新的 reviewer
   actor；它仍須依 Router 與 admission gate 做出自己的審閱／整合判定。
3. Codex 的跨生命週期候選實作採現有一次性 role-wake composition：
   `GitRefEventAdapter → HandoffValidator → CommandRoleWakePort`。新增的 host command
   僅可啟動一個帶明確 ticket、artifact ref、profile 與 workspace 的 one-shot `codex exec`
   actor。它的 terminal JSON／子行程結束是 completion event；不是週期性讀取 Git、thread
   或模型狀態。
4. capability 必須保留三態，不能折疊：

   | 狀態 | 意義與行為 |
   | --- | --- |
   | `NOT_REQUIRED` | host 原生 callback 能在同一生命週期送達；不啟動 bridge。 |
   | `AVAILABLE` | host 不原生送達，但已由一次性真實、具 receipt 的 CLI actor probe 證明送達。 |
   | `UNAVAILABLE` | host 不原生送達且 bridge 尚未證明或無法使用；由 owner 人工轉達或另起 actor，絕不宣稱已送達。 |

5. 在 `AVAILABLE` 證明之前，Windows Codex Desktop parent resume 是 `UNAVAILABLE`。
   不得用 `automation_update`、排程 timer、持續 polling、假 receipt、或未證明的 MCP
   thread-message interface 偽造它。若日後 host 提供可由本機 runner 呼叫、具身份與回讀
   的正式外部 thread-message endpoint，必須另行 qualification，不能由本 ADR 推定。
6. 真實 `codex exec` probe 會消耗 provider usage 並建立外部 process effect；它與純
   adapter 程式碼分為不同 ticket。後者可先以 fake port、嚴格 typed command／artifact
   驗證與反向突變測試完成；前者必須取得一次性的 owner effect authority，記錄模型、
   workspace、無寫入任務、預期 ACK 與實際 receipt。

## 替代方案與取捨

- **讓 parent 常駐並反覆 `wait_agent`**：同步流程可行，但不解決 parent 已終止的需求，
  且為等待而輪詢會浪費 token；不採用作為跨生命週期方案。
- **Windows `codex app-server daemon` 復原 Desktop parent**：本機 CLI 已回報 daemon
  lifecycle 僅支援 Unix，且尚無可驗證的 parent-revival contract；不採用。
- **durable queue／receipt 發行器當成預設**：會把選配 bridge 變成同步流程前置條件，
  違反 ADR-014；不採用。
- **owner 人工轉達**：在 `UNAVAILABLE` 時保留為誠實、可操作的 fallback；代價是人工
  介入，但不製造虛假的送達證據。

## 後果、風險與回復方式

實作者不會因 bridge 缺席而被阻擋；只有請求跨生命週期自動交接時才讀取其 capability。
新的 CLI actor 是可稽核的後繼審閱者，並非原 session 的延續。artifact 不得含 secret、
未提交 worktree 內容或未獲 admission 的 source authority。

實作順序固定如下：

1. 起草新的需求變更，界定 CLI host-effect、artifact schema 與 delivery profile；
2. 建立純 E15A adapter ticket，無真實 `codex exec`；
3. owner 逐次授權後才建立 E15B one-shot probe；只有驗證的 receipt 才可把 capability
   寫成 `AVAILABLE`；
4. E15C 才能把已證明的 adapter 接到既有 event runner。

若 adapter 或 probe 失敗，撤除其 composition／設定，capability 回到 `UNAVAILABLE`；
同步 `wait_agent` 流程與既有 admission gate 均不受影響。不得藉回復操作刪除歷史 handoff
evidence 或改寫已完成 receipt。

## 修訂／淘汰紀錄

- 本 ADR 補充並具體化 `ADR-20260823-014` 的跨生命週期 bridge；不取代其「同步流程不需
  bridge」決策。
- 其實作會在受管制需求變更與後續 ticket 中另行驗收；本 ADR 本身不是 CLI provider
  invocation authority。
