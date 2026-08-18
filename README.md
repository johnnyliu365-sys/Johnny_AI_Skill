# Johnny AI Skill

這是一套可隨時安裝或拔除的「個人 Agent workflow 外掛」。它用來接管新專案、既有專案或做到一半的專案，並把同一份 skill 同時提供給 Codex 與 Claude Code。

它不是公司專案的 runtime service、MCP server、hook、CI 依賴、Git submodule、symlink、package dependency 或原始碼 import。因此拔除後，公司的建置、測試、部署與既有程式不會受影響。

## 目前發行：0.4.0

0.4.0 完成 Router runtime 主線（runner registry、receipt Git subscription、Senior review
queue、host-wake gate、deterministic bundle、Router composition、install／uninstall
transaction、telemetry report）與 SourceProjectA scripted + real-role 雙重驗證，並完成 Wayfinder
收斂五連修（有界資訊缺口協議、範圍終止規則、intake 三模式、workload 強度自適應、
red 證據重定義）。兩個誠實邊界仍然生效：`install.ps1` 於使用者確認後停在
`LIVE_INSTALL_NOT_AUTHORIZED`（live 安裝效果綁定未落地），自動喚醒維持
`HOST_WAKE_CAPABILITY_UNAVAILABLE`（event runner 未落地）；skill-only 安裝與使用
不受影響。

0.3.2 將前端的組合式設計與依賴注入列為 SPEC／ticket 的阻擋規則，並將控制面 Agent 固定為 Wayfinder／Grill／ticket／review；正式實作必須交給另一位具名 implementation owner。

本版包含 Router 的 metadata-only context-load telemetry POC。它可在本機比對 baseline 與 Router run 的 provider input token、ContextView 預算、來源宣告與驗收品質；資料不含原文、prompt、來源 URI 或 Secret。受控專案正式使用仍需等待隔離修訂完成，raw JSONL 必須留在 Johnny-owned per-user storage，不得寫進 target project。

它不會自動截取 Codex 或 Claude Code 的 token。只有 Agent runner 回填 provider 實際 input token，且 JSONL 配對驗證通過時，才可宣稱 Router 真的降低了 context 負載。

## 內含哪些 skill

| Skill | 用途 |
| --- | --- |
| `johnny-project-takeover` | 先進入 Wayfinder，再依 Router 與 Workflow 收斂下一步，並以目標專案自身規範為優先。 |
| `apply-reusable-modules` | 從 `library/MODULE_CATALOG.md` 選擇最小且適合的 `READY` 模組；不會自動複製模組。 |

兩個平台共用此 repo 根目錄唯一的 `skills/`。Workflow、Defined Wayfinder、Router POC 與 module catalog 也都是同一份；差別只在各自的外掛描述檔。

## 在公司使用前先知道的事

把外掛安裝在你「個人」的 Codex 或 Claude Code 使用者範圍，**不要**複製或安裝到公司 repository。之後照常開啟公司專案，在 task 裡呼叫 skill 即可。

公司 repo 裡自己的 `AGENTS.md`、`Workflow.md`、安全規範、測試與 Git 政策仍是最高優先。Johnny AI Skill 只是外部控制平面，協助 Agent 判斷安全的下一步；它不會覆寫公司規範，也不會替公司專案增加依賴。

你的 GitHub 帳號必須能 clone 此 private repo。先讓 Git 或 SSH 完成正常登入；不要把 personal access token 寫進指令、設定檔或公司 repo。

## Codex 使用方式

### 0.4.0 完整 bundle 安裝

正式入口是經核准且 SHA-256 相符的 `johnny-ai-skill-0.4.0.zip` 內
`install.ps1`。在個人終端機、且不在公司專案資料夾內執行它。bootstrap 會先顯示
Codex、Git、Python 與核心 dependency 計畫；需要下載時必須由使用者確認。它只建立
per-user Johnny-owned runtime，不會把 plugin、venv、receipt 或 cache 複製到公司 repo。

`0.4.0` 實作與 SourceProjectA 驗證完成前，不得把目前的原始碼 checkout 或 `main` 當成已
核准 bundle。既有 `0.3.x` skill-only 安裝仍可使用 private Git marketplace，但不包含
Router runtime、event runner 或完整清除保證。

### 接管公司專案

1. 正常開啟公司 repository 的新 Codex task。
2. 輸入：

   ```text
   Use $johnny-project-takeover to take over this project safely.
   ```

3. 只有在要評估現有通用功能時，再輸入：

   ```text
   Use $apply-reusable-modules to select the smallest safe module set.
   ```

第一個 skill 會先讀取目標專案本地規範；只有在目標專案未建立流程時，才以本外掛的 Workflow 當作備援流程。

若要驗證 Router 是否降低 context，依 `library/workflow_router/README.md` 使用 Johnny-owned telemetry storage 保存配對資料，再執行 telemetry CLI；在隔離修訂實作完成前，不得把現有 raw-path POC API 指向受控 target project，也不要把公司原文或 prompt 交給外掛。

### 更新或拔除

`0.4.0` 的完整移除入口是：

```powershell
johnny-router uninstall
```

它會先停止 owned runner、取消 subscriptions、移除 ledger、receipt、queue、telemetry、
venv 與 launcher，再呼叫 Codex plugin remove 並驗證不存在。直接從 Codex UI 或
marketplace remove 只能移除 Codex 可見的 plugin，不能宣稱 Johnny runtime 已完整清除。

既有 `0.3.x` skill-only 安裝沒有 `0.4.0` runtime；其 marketplace 更新／移除流程仍以
該已安裝版本的 Codex 指令為準。任何版本的拔除都不得修改公司 repository。

## Claude Code 使用方式

Claude Code 透過 `.claude-plugin/plugin.json` 讀取同一個根目錄 `skills/`，因此 skill 會有 `johnny-ai-skill` 命名空間。

### 只需安裝一次

在個人終端機、且不在公司專案資料夾內執行：

```powershell
claude plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill
claude plugin install johnny-ai-skill@johnny-ai-skill --scope user
```

若 private repo 無法讀取，先確認同一帳號可用 Git 或 SSH clone。使用 GitHub CLI 時可安全地執行：

```powershell
gh auth login
gh auth setup-git
```

重新開啟 Claude Code session，或在既有 session 輸入 `/reload-plugins`。

### 接管公司專案

1. 如常用 Claude Code 開啟公司 repository。
2. 輸入：

   ```text
   /johnny-ai-skill:johnny-project-takeover
   ```

3. 需要選擇通用模組時才輸入：

   ```text
   /johnny-ai-skill:apply-reusable-modules
   ```

接著補上本次專案目標即可。Claude Code 先取得此共用 skill，但在採取任何動作前仍必須遵守公司專案的本地規範。

Context-load telemetry 同樣由本機 Agent runner 建立 JSONL 證據；Claude Code plugin 本身不攔截 token，也不把公司內容上傳或寫進 repo。

### 更新、驗證或拔除

```powershell
claude plugin marketplace update johnny-ai-skill
claude plugin update johnny-ai-skill@johnny-ai-skill
claude plugin uninstall johnny-ai-skill@johnny-ai-skill --scope user
claude plugin marketplace remove johnny-ai-skill --scope user
```

若要在本 repo 的 clone 根目錄進行一次 Claude Code 煙霧測試：

```powershell
claude plugin validate .
claude --plugin-dir .
```

Claude 的 `plugin.json` 故意不寫版本號，讓它以 Git commit SHA 辨識版本；每次新 commit 都可以被視為可更新版本，不需要重複維護第二份版本號。

## 拔除保證

這個外掛只裝在使用者範圍，不會被 commit 到目標專案。要完全拔除時，執行上方對應平台的移除命令，然後重新開啟 Agent session。公司專案會保留完全相同的 checkout、原始碼、依賴、CI、部署設定與 Git history；消失的只有這套可選的 workflow skill。

## Metadata-only policy 與 dispatch response

這個 plugin 是 local POC control plane。Policy source 只能在 ephemeral
boundary 以 typed metadata 通過；Router 不會保存或回傳 policy 原文。
固定 dispatch response 只能由同一個 Private Router 所擁有的 live pending
descriptor 產生，並綁定 reviewed ticket、handoff receipt、commits 與具名
implementation owner。偽造、replay、缺失或 mismatch descriptor 一律
fail-closed，不產生回應或 capability。

`MVP` 與 `COMMERCIAL` 是歷史／Profile-gated delivery stage，不是 plugin
自行推論的 active product objective；在核准的 project artifact 與 change
record 另行宣告前，預設仍是 `POC`。

## 環境能力啟動

> 正式契約為已核准的
> [`modules/spec/environment-capability-bootstrap.md`](modules/spec/environment-capability-bootstrap.md)。
> Senior 已可依該 SPEC 與 Plugin Distribution Revision 02 拆票；實作與驗證完成前，
> 不得宣稱 Johnny 已能自動安裝、限制專案工具或自動喚醒角色。

Johnny 優先使用使用者與專案既有且相容的 Git、Python、Docker、SDK 與建置工具，
不會靜默升級、降級、取代或修改全域設定。控制平面優先選用使用者已安裝、Python
3.11 以上且通過 compatibility probe 的 interpreter，並在 Johnny-owned root 建立獨立
`CONTROL_PYTHON` venv；不合格的較新版本也會停止而非猜測相容。專案自己的
Python／SDK 仍由專案原生 manifest 與 lockfile 決定。

能力依三個邊界驗證：

1. `CONTROL_BOOTSTRAP`：Router 所需 Git、控制 Python 與基本宿主能力。
2. `PROJECT_BASELINE`：專案原生 runtime、lockfile、建置與測試基準。
3. `TICKET_OVERLAY`：單一 ticket 額外需要的工具與有限資源計畫。

Johnny 只能自動安裝可逆、per-user、Johnny-owned 且已固定版本／hash／signature 的
artifact。需要管理員、全域／系統修改、EULA、重開機、登入或 credential 的步驟只會
引導並要求分離核准。Implementation 期間不安裝、不更新、不重設工具。

所有 Johnny-owned environment、cache、grant、evidence 與 receipt binding 都位於
per-user Johnny root，使用 opaque project/capability/lock identity；不在 target project
建立 `.johnny`、`.johnny-router`、隱藏 worktree、plugin manifest、runtime 或 cache。
實作 ticket 的 workspace 使用該 root 內的獨立 checkout／clone，不連結到 target 的
`.git/worktrees`；dispatch 不改 target Git，只有之後具名且 receipt-bound 的 integration
動作才能產生標準 Git effect。
每個 Johnny 啟動的 process/container 在執行專案工作前都必須有可讀回的 CPU、RAM、
disk/temp、process/container、worker 與 lane 硬限制；無法硬限制即停止，不降級為提示。

`PROJECT_DETACH` 只移除該專案的 Johnny-owned mapping／可寫狀態；
`PLUGIN_UNINSTALL` 依 ownership ledger 移除全部 Johnny-owned runtime、tool、environment、
cache、grant、evidence 與 receipt binding。兩者都不得修改 target project 或刪除使用者／
外部工具。新工程師可直接依專案原生文件與 manifests 接手。

Codex plugin manifest 沒有可依賴的 Johnny uninstall callback，因此 `0.4.0` 只有
`johnny-router uninstall` 可以宣稱完成上述 `PLUGIN_UNINSTALL`。若 host 缺少合法的
receipt-bound completion callback，Git event runner 只能登記完成候選並請使用者手動轉發；
不得改用 heartbeat、automation、cron、polling 或假稱 Router 已可綁定。

## Receipt-bound 角色監督與可拔除交接流程

> 狀態：SPEC 已核准，正式契約以
> [`modules/spec/receipt-bound-role-supervision.md`](modules/spec/receipt-bound-role-supervision.md)
> 為準。Reviewer 已可依該 SPEC 拆票；實作驗證前不得宣稱自動監督能力已可用。

這套流程的目標是在不犧牲權限、正確性與穩定交付的前提下減少模型喚醒。正常
implementation 期間不使用 heartbeat、定時 polling、cron、watchdog 或重複 thread
readback。任何 heartbeat 都必須另行取得使用者明確、範圍限定的同意；ticket 核准、
dispatch、`AUTO_CONTINUE` 或「持續監控」都不構成該同意。

### 快速判斷

| 情況 | 是否需要受控替換 | 處理方式 |
| --- | --- | --- |
| 同一 task 重開 PowerShell、IDE、命令或子程序 | 否 | 保留原 execution binding。 |
| 同一 task 經 Host 證明原地換模型 | 否 | 建立新 binding revision 並 readback。 |
| 更換 Agent task、有效寫入者、主機或機器 | 是 | checkpoint（可用時）→撤銷舊寫入權→readback→新 task/binding/correlation；只有 Router 可在必要時先撤銷再替換同票 receipt。 |
| Luna xhigh 三十分鐘仍未完成或停止未完成 | 是 | 先判定 ticket 複雜度；可拆則拆小，不可拆才將當票替換為 Terra high。 |
| Terra-or-higher 兩小時無 Git ref 活動且停止未完成 | 否（第一次） | Reviewer 唯讀診斷後可送一次同票 `CONTINUE_IMPLEMENTATION`。 |
| Terra-or-higher 再次停止未完成 | 升級決策 | `MODEL_CAPABILITY_INSUFFICIENT` 經 Router 喚醒架構者。 |
| 使用者拔除插件 | 不受 Router 阻擋 | 插件立即失去控制作用；新工程師可自由選擇自己的流程。 |

### Attached 狀態下的正常流程

```text
Reviewer 派送 exact ticket
→ Host readback 證明 task/worktree/branch/baseline 且可執行
→ 開始模型對應的一次性監督期限
→ exact Git ref 事件（普通 source commit 不喚醒模型）
→ git show 讀取 committed handoff leaf
→ 驗證 receipt/task/branch/ancestry/digest/terminal kind
→ RoleWakePort 喚醒 named Reviewer 一次
→ Reviewer 唯讀診斷並交回 Router 決策
```

完整 `GitRefEventAdapter -> HandoffValidator -> RoleWakePort` 與
`SupervisionLeasePort -> RoleWakePort` 能力在 dispatch 前必須可讀回證明。缺少任何一段即
`HALT / ROLE_WAKE_CHAIN_UNAVAILABLE`，不改用 active-turn wait、heartbeat 或 polling。

### 換終端、模型與工程師

綁定單位是持有寫入權的 execution session/task，不是終端視窗。受控替換時，舊 task
和新 task 不得同時寫入。舊 task 可用時先提交 bounded checkpoint；不可用時只能從最後
已提交且驗證過的 commit/handoff 恢復。新機器使用乾淨 checkout/worktree，不搬移舊機器
路徑。

同一票因 Luna 無法合法拆分而升級 Terra high 時，override 僅限當次 ticket。提交 terminal
handoff 後 override 失效，下一張新票回到 Profile 預設 Luna xhigh。

### Handoff 台帳

目標專案保存自己的 plugin-neutral handoff tree；本專案的設計索引位於
[`doc/handoffs/README.md`](doc/handoffs/README.md)。正式結構為：

```text
doc/handoffs/index.json
doc/handoffs/<year>/index.json
doc/handoffs/<year>/<feature>/index.json
doc/handoffs/<year>/<feature>/<ticket-id>/index.json
doc/handoffs/<year>/<feature>/<ticket-id>/<handoff-id>.json
```

每層 index 只列直接子節點的 ID、kind、revision、digest、lifecycle 與 exact ref；內容只在
exact leaf。更正建立新 leaf 並指向前一 leaf，不改寫 sealed 歷史。不得保存 Secret、PII、
prompt、raw Context 或未驗證 host payload。

### 插件拔除與新工程師接手

使用者可以先拔除插件，不需要 Router 核准，也不必先 checkpoint、push、readback 或等待
外部 effect 完成。拔除不得修改或刪除目標專案的 source、CI、資料或正式 artifacts。

拔除後，新工程師可以使用任何工具與流程；舊 README、manifest、handoff 與 receipt ref 只是
歷史線索，不再對新工程師形成 authority。插件不保證保存未提交內容，也不保證取消或完成
正在進行的外部操作。新工程師若自願重新採用 Johnny，必須重新 takeover 並建立新的
task、receipt 與 correlation；舊 live receipt 不得重播。

### 部署邊界

開發 task/receipt 不授權 push、merge、release、signing、migration 或 deployment。部署可在
不同 runner/終端執行，但必須另外綁定 exact owner、action、environment、accepted commit／
artifact digest、effect receipt 與 correlation，並在 effect 後讀回結果。插件不是 runtime、
CI、build 或 deployment dependency；拔除插件不會變更已部署系統。
