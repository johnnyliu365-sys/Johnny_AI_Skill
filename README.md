# Johnny AI Skill

這是一套可隨時安裝或拔除的「個人 Agent workflow 外掛」。它用來接管新專案、既有專案或做到一半的專案，並把同一份 skill 同時提供給 Codex 與 Claude Code。

它不是公司專案的 runtime service、MCP server、hook、CI 依賴、Git submodule、symlink、package dependency 或原始碼 import。因此拔除後，公司的建置、測試、部署與既有程式不會受影響。

## 目前發行：0.4.8

0.4.8 把零件接成一條路，並且**在真安裝的 store 上驗證過整條路**。派工＝admit →
claim → spawn 一條路徑（`dispatch_session`），claim 先於 spawn，spawn 失敗立即補償；
補償後有具名的重派路（`redispatch_worker`）：撤銷舊 receipt、發後繼、走一模一樣的派工，
恰好一次由閘門自己讀帳本保全。整合只有一個出口——`integrate_next_work` 拉取佇列並經
文件閘門完成合併；實機驗證中 main 的移動第一次不經人手。commit 觸發從此有腳掌：
runner 的原生 ref watch 多了一個 tee，喚醒永遠先行，之後把 commit 交給佇列，重複由
`ORIGIN_ALREADY_QUEUED` 收斂。逐行實錄見 `doc/runbooks/live-verification-047.md`。

**誠實邊界**：`COMMIT_TRIGGER` 項目被拉到之後的處理政策尚未定義（消費端目前具名擱置、
不取走）；重派路要求 owner grant 與已補償的 claim，從未 claim 的 receipt 拒絕撤銷。

0.4.7 補上排程佇列（`work_queue`）。子代理回傳或 commit 觸發成立時，該做的下一件事
**落到持久佇列上**；主 session 手上的工作做完再拉下一件。**拉取而非推送**，所以不需要
偵測誰在忙、不需要中斷機制，而拉取發生在「一件工作結束」這個事件上，不是計時器上。

順序是**宣告的**：跨兩種來源的嚴格 FIFO，`sequence` 在序列化寫入的同一把鎖內指派，
而磁碟上的陣列順序刻意不要求與它一致——那個自由度是唯一能證明「服務順序來自紀錄欄位
而非檔案順序」的辦法。**佇列讀不到會具名拒絕，絕不回傳空佇列**：把兩者折疊會讓主
session 安靜停工且毫無訊號。

**誠實邊界**：閒置的消費者沒有「完成」可以抵達，所以無人執行時入列的工作要等下一件事
做完才被拿走——持久性成立，及時性不成立；拉走後死掉的消費者會讓 item 停在 `PULLED`，
讀得到但不會被重新入列。兩者都沒有用計時器假裝解決。

**尚未接線**：綁定、佇列、閘門三者都要控制面主動呼叫（見工單 P4）。

0.4.6 把治理從「寫在文件裡」變成「擋得住」。

**文件變更閘門**（`document_mutation_gate`）：每張票以機器可讀的 `johnny-boundary`
區塊宣告可改／可新增／可刪除的路徑，變更整合進 `main` 之前由閘門比對實際動到的檔案，
三種門檻各自具名拒絕。**邊界從 `main` 上的票讀，不從候選分支讀**——否則一個變更能在
同一個 commit 裡放寬用來審它自己的規則。刪除只接受精確路徑，不接受萬用字元。

**工單狀態頁**（`ticket_status_pipeline` + `ticket_status_template` +
`ticket_status_publish`）：一頁回答「哪張票、哪個階段、停在哪個 commit、接手要給對話
什麼指令」。狀態一律**讀票裡的宣告**，不從散文推測；解析失敗的票會就地標示為「讀不到」，
**絕不靜靜地變成空欄位**——短清單看起來像「沒事」，那是這頁最危險的失敗。

**工人與 receipt 的綁定**（`worker_assignment`）：claim／settle 配對寫在持久帳上，
跨行程恰好一次。「哪張票在誰手上」不再只存在於某個對話裡。

另含並行派工的實證（兩張票同時發放各拿到自己的 receipt、同票並行只成立一份、
repo 外的 worktree 被拒且不留發放紀錄）、`CLAUDE.md` 入口（本專案的規範入口是
`AGENTS.md`，但 Claude Code 只自動載入 `CLAUDE.md`），以及測試基礎設施的兩個
cp950 解碼修正與一個 1/11 機率的孤兒環境缺陷。

**誠實邊界**：閘門擋在整合而非按鍵——Router 是函式庫不是檔案系統掛鉤，擋不住 agent
落鍵，能保證的是「未宣告的變更進不了 main」。`worker_assignment` 讓死掉的工人
**可被發現**而非**被偵測**：孤兒在有人讀取時浮現，不由計時器浮現；不加輪詢是刻意的，
代價是及時性。

0.4.5 讓 Router 能驅動 **Claude Code 的對話分支**，一個 reviewer 一條分支，
每次喚醒依 payload 的 `reviewer_ref` 查 owner 宣告的路由表決定目標
（`claude_wake_command`）。實機驗證：能力 probe 5.2 秒通過、兩條分支各自種入不同
token 後分別 resume 互不污染、具名 reviewer 的分支收到喚醒後自己說得出被交付的
payload 路徑且仍保有先前歷史。

**它不會驅動你正開著的對話。** 桌面 app 的三條顯示路徑都經實測堵死（驅動開著的
分頁會寫入存檔但畫面不動、背景 agent 不顯示、CLI session 沒有 MCP server），
所以外部驅動只會產生你看不見的工作，還會和 app 記憶體裡的舊歷史打架。兩道守衛
因此拒絕投遞：目標被現役行程持有（`BRANCH_HELD_BY_LIVE_SESSION`）或被 app 分頁
登記（`BRANCH_HELD_BY_APP_TAB`）都不送，讀不到清單時同樣拒絕——不知道不等於
知道它是空的。

誠實邊界：被喚醒的分支只驗到「它收到了」，未驗到它自行完成審查並提交 verdict；
喚醒失敗的原因目前仍未持久化（`CommandRoleWakePort` 丟棄子行程 stdout），所以
owner 狀態頁還讀不到那些代碼。本版另含尚未接線的 owner 狀態頁 generator
（`owner_status_surface`），目前沒有任何東西呼叫它。

0.4.4 修正一個 P0 誠實性缺陷（governance 04）：skill 通篇以直述句描寫喚醒
（「The Router wakes …」），agent 會把協定敘述讀成系統行為，對未 arm 的專案
報告從未發生的喚醒——owner 在真實專案上親眼抓到。現在每句喚醒都寫明
「狀態（`WAKE_REQUIRED`）＋機制（armed runner 才會送達）＋後備（否則由 owner
轉達）」，SKILL.md 新增 Automation readiness 節（agent 宣稱任何自動效果前必須
驗證四個可觀察前提），並明文規定：**不得報告未觀察到的喚醒——committed handoff
是 commit 的證據，不是送達的證據。**

0.4.3 讓完整的自動化迴路進入已安裝的 runtime。新增三個 CLI 家族：
`dispatch grant`／`dispatch issue`（受 owner 授權、worktree 包含性閘門與 journal
保護的 receipt 發放）、`runner subscribe`（從已核發 receipt 推導訂閱）、
`review submit`／`review consume`（verdict 綁定「已派工＋喚醒已送達」雙證據，
恰好一次轉為 RouterEvent，且**跨行程**成立——review 臨界區與既有 durable 元件
共用同一個 OS 級排它鎖）。隨附 Antigravity 喚醒命令（`antigravity_wake_command`，
每次呼叫自行探索 session 動態的 LS 位址與 token）、全鏈 gated qualification
（dispatch→runner→commit→喚醒→verdict→RouterEvent 一次跑完、零夾具）、
runtime root 污染的單點揭露 guard，以及稽核入口
`modules/tickets/PITFALL-REGISTER.md`。

派工後的監督—喚醒—回傳全自動；派工本身仍是刻意保留的控制面動作。已知誠實
缺口：被喚醒的 agent 自行執行 `review submit` 尚未實機驗證（機制已具備）。

0.4.2 修復 handoff 驅動喚醒（E10／CR-E7-01，見下方修正紀錄）並補齊發行與
安裝面：`johnny-install.cmd` 一鍵安裝入口（digest 釘死、所有 BLOCKED 退出可讀）、
release pin guard（版本升級忘記更新 wrapper 會轉紅、發行前 preflight 比對實建
bundle）、subscription builder（從已核發 receipt 推導 runner 訂閱，能力一律 probe
不接受宣稱，含新增的 monotonic one-shot deadline probe）、Antigravity 載入面
（`.agents/` 專案面與 per-user `skills.json` 註冊，單一真相來源零複製）、以及
agent worktree 位置治理（`.worktrees/` 包含性驗證，junction 一律拒絕）。

0.4.1 落地 0.4.0 的兩個誠實邊界。**Live 安裝效果綁定**：`install.ps1` 於使用者
確認後，由 stdlib-only bootstrap 建立 hash-locked control venv，再執行 typed、
journaled 的 install transaction；`johnny-router status`／`uninstall` 已在實機驗證
INSTALLED 與 ZERO_RESIDUE。**自動喚醒**：event runner 落地——wake capability 由
probe 實際執行宣告的 wake 命令證明；無 heartbeat／polling；runner 只對已在 durable
checkpoint 中驗證為 claimable 的 receipt arm 監督，且 composition 只持有 wake-scoped
三方法 boundary（read／claim／settle），不持有任何可發放 receipt 的物件。未證明 wake
capability 時誠實落到 candidate inbox（只登記完成候選，不宣稱喚醒）。receipt 發放
（dispatch authority）整合遞延至 multi-model workstation 線。本版經五輪外部審查後
APPROVED。

> **0.4.1 發行後修正（`E10` / `CR-E7-01`，2026-08-19 當日發現並修復）**：發行當下
> handoff 驅動的喚醒實際上不會送達——coordinator 拒絕未帶 review instruction 的
> handoff 喚醒，而 unbatched 組合移除了負責填入該指令的批次層卻未移交責任；長期
> 偽綠來自 E6 R3 只比對 `"handoff"` 子字串（期限 payload 的 `handoff_id=-` 欄位剛好
> 命中）。已由 `SingleHandoffReviewSubmission` 修復並以具鑑別力的 R3 實證：真
> detached runner、真 commit、期限未到期時送達 `action=REVIEW_HANDOFF`。反向突變
> （移除該修正）使 R3 轉紅。詳見
> [`modules/tickets/event-runner-binding/e10-handoff-driven-wake.md`](modules/tickets/event-runner-binding/e10-handoff-driven-wake.md)。
> 此修正隨 0.4.2 發行；0.4.1 zip 內的 runner 仍帶此缺陷，需要 commit 驅動喚醒者
> 請升級至 0.4.2。

0.4.0 完成 Router runtime 主線（runner registry、receipt Git subscription、Senior review
queue、host-wake gate、deterministic bundle、Router composition、install／uninstall
transaction、telemetry report）與 來源專案A scripted + real-role 雙重驗證，並完成 Wayfinder
收斂五連修（有界資訊缺口協議、範圍終止規則、intake 三模式、workload 強度自適應、
red 證據重定義）。該版的兩個誠實邊界（live 安裝停在
`LIVE_INSTALL_NOT_AUTHORIZED`、自動喚醒維持
`HOST_WAKE_CAPABILITY_UNAVAILABLE`）已由 0.4.1 落地取代；skill-only 安裝與使用
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

### 0.4.8 完整 bundle 安裝

正式的一鍵入口是隨 release 發布的 `johnny-install.cmd`，將其下載至與經核准且 SHA-256 相符的 `johnny-ai-skill-0.4.8.zip` 同一資料夾下雙擊執行（或在終端機直接執行 `install.ps1 -BundleZip <path>`）。它會先核驗 bundle SHA-256，並在確認相符後抽出 `install.ps1` 進行安裝引導。bootstrap 會先顯示 Codex、Git、Python 與核心 dependency 計畫；需要下載時必須由使用者輸入 `INSTALL` 確認。它只建立 per-user Johnny-owned runtime，不會把 plugin、venv、receipt 或 cache 複製到公司 repo。

不得把原始碼 checkout 或 `main` 當成已核准 bundle；正式入口永遠是 digest 與已核准
release 相符的 bundle。既有 `0.3.x` skill-only 安裝仍可使用 private Git
marketplace，但不包含 Router runtime、event runner 或完整清除保證。

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

安裝完成後的 runtime 位於 per-user 根目錄 `%LOCALAPPDATA%\JohnnyRouter`
（可用 `JOHNNY_ROOT` 覆寫）。本外掛**刻意不修改 `PATH`**，所以沒有全域
`johnny-router` 指令；入口是該根目錄下的 launcher 腳本，以完整路徑呼叫。

確認安裝狀態：

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\JohnnyRouter\launcher\johnny-router.ps1" status
```

`0.4.x` 完整 bundle 安裝的移除入口是同一個 launcher：

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\JohnnyRouter\launcher\johnny-router.ps1" uninstall
```

它會先停止 owned runner、取消 subscriptions、移除 ledger、receipt、queue、telemetry、
venv 與 launcher，再呼叫 Codex plugin remove 並驗證不存在。直接從 Codex UI 或
marketplace remove 只能移除 Codex 可見的 plugin，不能宣稱 Johnny runtime 已完整清除。

已安裝的情況下重跑 installer 會以 `VENV_ALREADY_PRESENT` 擋下且不動既有 runtime；
要重裝請先執行上面的移除入口。

既有 `0.3.x` skill-only 安裝沒有 `0.4.x` runtime；其 marketplace 更新／移除流程仍以
該已安裝版本的 Codex 指令為準。任何版本的拔除都不得修改公司 repository。

## Antigravity 使用方式

Antigravity 從 customization root 的 `skills.json` 掃描 `entries[].path` 尋找
skill 目錄，因此不需要複製任何 skill 檔案——註冊的是指向本 repo `skills/` 的
單一項目，維持唯一真相來源。

在本 repo 內工作時，`.agents/skills.json` 已提交在版控中，開啟工作區即自動生效
（其 `path` 為 workspace-relative，由 Antigravity 相對 repository root 解析）。
`.agents/plugins/johnny-ai-skill/` 另附一條 worktree 位置規則。

要在所有專案都可用，註冊到 per-user customization root（`~/.gemini/config/`）：

```powershell
py -3.11 -c "from pathlib import Path; import sys; sys.path.insert(0, r'<repo-root>'); from library.local_orchestration.antigravity_registration import default_customization_root, register_johnny_skills; print(register_johnny_skills(default_customization_root(), Path(r'<repo-root>\skills'))[0].value)"
```

註冊是冪等的（重複執行只會有一個項目），移除只拿掉 Johnny 自己的項目，使用者原有
的其他 entries 逐位元組保留，且不會刪除非 Johnny 建立的設定檔。

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

兩種入口，用途不同：

- **Slash command（確定性）**——治理流程的進入點應該是確定的，不取決於模型
  是否判斷該載入。0.4.3 新增 `commands/`，因此 `/johnny-ai-skill:...` 現在
  是真的存在的指令。（0.4.2 以前的 README 就寫著這個指令，但外掛當時只有
  `skills/`、沒有 `commands/`，該指令從未存在——這是文件缺陷，已於 0.4.3
  以「補上指令」而非「刪掉文件」的方式修正。）
- **自然語言（機率性）**——模型依 skill 的 `description` 自行判斷何時載入。
  適合你沒有明確要進入治理流程、只是在描述問題的情況。

1. 如常用 Claude Code 開啟公司 repository。
2. 確定性入口：

   ```text
   /johnny-ai-skill:johnny-project-takeover 本次專案目標
   ```

3. 需要選擇通用模組時：

   ```text
   /johnny-ai-skill:apply-reusable-modules 你需要的能力
   ```

   兩者都可改用自然語言指名，例如
   `Use the johnny-project-takeover skill to take over this project safely.`

接著補上本次專案目標即可。Claude Code 先取得此共用 skill，但在採取任何動作前仍必須遵守公司專案的本地規範。

安裝後需重開 session（或 `/reload-plugins`）才會載入。若 `claude` 不在 `PATH`
上，CLI 位於 `%APPDATA%\Claude\claude-code\<版本>\claude.exe`；該路徑含版本號，
升級後會變動。

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

Codex plugin manifest 沒有可依賴的 Johnny uninstall callback，因此 `0.4.x` 只有
`johnny-router uninstall` 可以宣稱完成上述 `PLUGIN_UNINSTALL`。若 host 缺少合法的
receipt-bound completion callback，Git event runner 只能登記完成候選並請使用者手動轉發；
不得改用 heartbeat、automation、cron、polling 或假稱 Router 已可綁定。

## Receipt-bound 角色監督與可拔除交接流程

> 狀態：SPEC 已核准，正式契約以
> [`modules/spec/receipt-bound-role-supervision.md`](modules/spec/receipt-bound-role-supervision.md)
> 為準。0.4.1 的 event runner 已通過 gated qualification（exact Git ref 事件驅動、
> receipt 驗證後喚醒一次）。自動喚醒仍以 probe 證明的 wake capability 為前提；
> 未證明時 runner 只登記完成候選，不宣稱喚醒。

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
