# E14｜Claude 分支喚醒命令

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理／基礎設施功能票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/event-runner-binding/e12-wake-command-discovery.md`（E12，已結案：本模組把同一份喚醒命令契約實作到第二個 host 上） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11 strict（TDD、需反向突變） |
| 狀態 | `DONE`（board 記為 `APPROVED`；已隨 v0.4.5 發行） |
| 共同基準 | `main`；本票落地並發行於 commit `da33781`（見完成回寫） |
| 實作者 | 無紀錄（早於本欄要求） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `library/local_orchestration/claude_wake_command.py` 及其測試 |
| 禁止修改 | 不得對使用者當下開啟的分頁／分支寫入（見下方「不授權事項」）；E12 建立的喚醒命令契約 |
| 環境 | `LOCAL`（對照 owner 的 Windows workstation 實測；`STAGING`／`PRODUCTION` 不適用） |

## 使用者拍板與可觀察結果

Router 能驅動 Claude Code 對話分支，每個 reviewer 一個分支，每次嘗試各自解析。交付物：
`library/local_orchestration/claude_wake_command.py`，可用

```text
py -3.11 -m library.local_orchestration.claude_wake_command {payload_file}
```

執行，這會成為 owner 的 `WakeCommandConfig.command` 向量。

**這台 host 實際提供什麼——量測而非假設**（對照 owner 的 Windows workstation，CLI
`2.1.234`）：

- CLI 裝在 `PATH` 之外的 `%APPDATA%\Claude\claude-code\<version>\claude.exe`，每個版本
  一個目錄。探索邏輯必須挑最高版本，不是找到的第一個。
- `claude -p` 恰好跑一個 turn 就結束。`--session-id <uuid>` 開一個具名分支，
  `--resume <id>` 接續一個已存的分支，`--fork-session` 分岔它——這些是讓「不同分支」成真
  的基本操作。
- `claude auth status` 印出 `{"loggedIn": …, "authMethod": …}`，不需要呼叫模型，是一個
  便宜的**必要**條件——僅止於必要，見下一點。
- **`claude auth status` 不驗證 token。** 只要環境裡有 token 就回報
  `{"loggedIn": true, "authMethod": "oauth_token"}`，而第一次真正呼叫仍可能失敗
  `401 Invalid bearer token`。這台 host 上量測到：status 說已登入，驅動卻回 401。只靠
  auth-status 的能力檢查因此會在一個什麼都驅動不了的 host 上回報 `PROVEN`——這正是探測
  路徑要求跑完一整個 turn 而非只看結束碼的原因。
- `claude setup-token` 發出的長期 token 以 `sk-ant-oat01-` 開頭（前綴寫死在 CLI 二進位
  檔裡）。存起來的值若不帶這個前綴就不是那個 issued token；瀏覽器步驟的 authorization
  code 是最容易被誤認成它的值。
- `claude agents --json` 列出現役 session（pid、sessionId、cwd），**不需要**認證就能
  跑——列舉是免費的，驅動不是。
- `claude setup-token` 發出長期 token，這是自動化該用的正確憑證：互動式 OAuth session
  會過期且無法無人值守地刷新，這正是這台 host 一開始被發現的方式（`loggedIn: false`，
  `claude -p` → `OAuth session expired and could not be refreshed`）。

**讀完整個介面之後確立的負面結果**：沒有任何介面能把一個 turn 送進使用者已經坐在裡面的
對話。所有頂層命令都列舉過了（`agents`、`auth`、`auto-mode`、`doctor`、`gateway`、
`import`、`install`、`mcp`、`plugin`、`project`、`setup-token`、`ultrareview`、
`update`）；沒有一個能把輸入注入正在跑的 session，`claude agents` 的選項全是給*未來*
被派發的 session 用的預設值，不是對現有 session 的控制。app 內建的 session-message 工具
只能被已經在 session 裡面的 agent 呼叫，而它自己的契約就排除了 orchestrate 背景工作。所以
這個通道跟 Antigravity 的形狀不同，這個差異絕不能被混淆：Antigravity **喚醒一個既有對話**
（E11 證明過一個真的 agent 讀了 payload 並採取行動）；Claude **驅動一個 Router 擁有的
分支**。owner 開著的視窗在這台 host 上不是喚醒目標。

## 實作範圍、依賴與 ticket elements

**目標解析是逐次嘗試進行的**，這正是「不同分支」這個複數會成真的原因。Router 渲染的喚醒
payload 是只帶識別碼的 `key=value` 文字，帶著 `reviewer_ref` 與 `project_id`
（`RoleWakeRequest.render_identifiers_only_payload`）。dispatcher 讀這兩個鍵，透過一份
owner 宣告的表在 `<johnny-root>/claude-branch-routes.json` 解析：

```json
{
  "routes": [
    {
      "reviewer_ref": "supervisor-reviewer",
      "session_id": "11111111-1111-4111-8111-111111111111",
      "project_id": "SourceProjectA"
    }
  ]
}
```

專案限定的路由優先於不限專案的路由。沒被對應到的 reviewer 以具名方式被拒絕為
`REVIEWER_NOT_MAPPED`；絕不會被送去別的分支——那是最不該發生的失敗。送到分支的訊息只帶
payload 的**路徑**，絕不帶內容本身，沿用 E12 的原則：識別碼留在檔案裡，不上命令列、不進
聊天訊息。

**探測誠實性——最容易腐壞的部分。** `probe_wake_capability` 對一個不點名任何 reviewer 的
拋棄式 payload（`{"probe":true,…}`）渲染宣告的命令，要求結束碼 0。若只要結束碼 0 就算
成功，`PROVEN` 就會變成「dispatcher 能讀一個檔案」的意思——這正是本專案反覆被咬過的假綠色
形狀（見 `PITFALL-REGISTER.md` family C）。所以探測路徑會對一個拋棄式分支做**真正端到端
的驅動**，並要求看到一個完成的模型 turn（stdout 裡的標記）才回報成功，光有結束碼不算數；
對應的反向突變在測試組裡。有兩個限制是刻意保留、日後不得抹掉的：探測只證明 host 能驅動
*某個* Claude 分支，**不**證明 reviewer 自己的分支可達，因為探測 payload 不點名任何
reviewer，路由失敗要在喚醒當下才會浮現；探測驅動的是一個全新的 `--session-id`，而真正的
喚醒用 `--resume`——這是被探測的呼叫與真正送出的呼叫之間唯一刻意的差異。探測也用一個快的
模型跑，因為 `probe_wake_capability` 把探測上限設在 30 秒，大模型的冷啟動 turn 可能超過。
探測逾時的 owner 會拿到 `PROBE_TIMEOUT` 與誠實的 `CANDIDATE_INBOX` 後備，絕不會拿到一個
假的喚醒宣稱。

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：無紀錄（早於本欄要求）。
- reviewer：控制面（Opus 5）；與實作者不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：純後端 dispatcher 模組（CLI 呼叫、路由表解析、subprocess 驅動），不觸及
任何正式 UI 邊界。

- 實際原始碼路徑：`library/local_orchestration/claude_wake_command.py`
- 公開契約／資料模型：`<johnny-root>/claude-branch-routes.json` 的路由表格式（見上方
  JSON 範例）；`RoleWakeRequest.render_identifiers_only_payload` 的識別碼 payload；
  `probe_wake_capability` 的探測契約

## TDD 設計

1. 正常行為：探索邏輯挑最高版本已安裝的 CLI（E14-R1）；不同 reviewer 各自到達不同分支
   且都能送達（E14-R3）。
2. 規則違反／輸入錯誤：未對應的 reviewer 以具名方式被拒絕，不會被誤送到別的分支
   （E14-R4）；未認證的 host 在花費一個 turn 之前就拒絕（E14-R2）。
3. 外部失敗／fail-closed：探測沒有真的跑完一個 turn 就不算成功，只有結束碼 0 不算數
   （E14-R6）；被現役 session 佔用的分支拒絕遞送，連清單讀不到時也拒絕，而不是放行
   （E14-R9）；被 app 分頁宣告佔用的分支拒絕遞送，即使背後的行程已經不在了（E14-R10）；
   探測逾時回報 `PROBE_TIMEOUT` 與 `CANDIDATE_INBOX`，絕不宣稱喚醒發生。
4. 回歸保護：訊息只帶 payload 路徑，不帶內容本身（E14-R5）；反向突變鑑別力（E14-R7）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑前綴比對（CLI 版本目錄挑選是取最大值，非前綴匹配） |
| 2 | null／空字串／陣列 | 否 | 不涉一般輸入格式驗證 |
| 3 | 權限繞過 | 是 | 直接：對現役 session（E14-R9）或 app 分頁（E14-R10）佔用的分支遞送被拒絕；間接：唯一的遞送路徑就是 dispatcher 本身，沒有另一條可繞過同一守衛的入口 |
| 4 | Token 格式與比較 | 是 | `sk-ant-oat01-` 前綴判斷，避免把瀏覽器 authorization code 誤認成 issued token；`AuthenticationGateTests` 斷言唯一的 subprocess 呼叫是 `auth status` |
| 5 | 錯誤碼是否一致 | 是 | 每個具名拒絕碼（`REVIEWER_NOT_MAPPED`、`BRANCH_HELD_BY_LIVE_SESSION`、`BRANCH_HELD_BY_APP_TAB`、`LIVE_SESSION_CHECK_FAILED`、`APP_CLAIM_CHECK_FAILED`、`PROBE_TIMEOUT`）必須各自唯一、可區分 |
| 6 | 例外是否會拋出 | 是 | 現役 session 清單讀不到、app 分頁宣告記錄讀不到時，兩者都必須 fail-closed（`LIVE_SESSION_CHECK_FAILED`／`APP_CLAIM_CHECK_FAILED`），不知道不等於知道分支是空的 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| E14-R1 | 探索挑最高版本已安裝的 CLI；非版本目錄被忽略；環境變數覆寫優先 | `ExecutableDiscoveryTests` |
| E14-R2 | 未認證的 host 在花費一個 turn 之前就拒絕 | `AuthenticationGateTests`——斷言唯一的 subprocess 呼叫是 `auth status` |
| E14-R3 | 不同 reviewer 到達不同分支 | `DeliveryTests.test_two_reviewers_reach_two_different_branches`——斷言兩筆記錄的 `--resume` id 不同 |
| E14-R4 | 未對應的 reviewer 被拒絕，不被誤送 | `DeliveryTests.test_unmapped_reviewer_is_refused_by_name_not_delivered_elsewhere`——斷言零次驅動呼叫 |
| E14-R5 | 訊息只帶 payload 路徑，不帶內容 | 同一格測試——斷言 `receipt_id` 與 action 都不在訊息裡 |
| E14-R6 | 探測要求跑完一個 turn，不是結束碼 0 | `ProbeHonestyTests.test_exit_zero_without_a_completed_turn_is_refused` |
| E14-R9 | 現役 session 佔用的對話被拒絕，清單讀不到也拒絕 | `LiveSessionGuardTests`；下方另有實機驗證 |
| E14-R10 | app 分頁宣告佔用的對話被拒絕，即使沒有活著的行程 | `AppTabClaimTests`；下方另有實機驗證 |
| E14-R7 | 測試有鑑別力 | 反向突變：路由改成永遠選第一筆，6 格轉紅；拿掉探測標記檢查，R6 轉紅；兩者皆已還原成綠 |

所有格子都透過一個記錄真實 argv 的 stub CLI 驅動真正的 subprocess 路徑，而不是 patch
模組內部——mock 過的 runner 抓不到命令形狀偷偷偏離 CLI 實際接受格式這件事。

**E14-R8 已關閉——實機量測。** 對照 owner 的 host、CLI `2.1.234`，用 `claude setup-token`
發出的 `sk-ant-oat01-` token（108 字元）經 `CLAUDE_CODE_OAUTH_TOKEN` 帶入，已認證：

1. **能力探測真的通過。** dispatcher 的探測路徑回傳
   `{"status": "CAPABILITY_PROVEN"}`，結束碼 0，耗時 **5.2 秒**——在 runtime 30 秒上限
   之內還有餘裕，這正是加入 deadline 預算的目的。
2. **分支各自獨立且持久。** 用 `--session-id` 開了兩個全新 session id，一個被告知
   `ALPHA-7731`，另一個 `BRAVO-4402`。分別用 `--resume` 接續，各自回傳**自己的** token，
   沒有一個帶到另一個的。所以平行的 Claude 分支是真的、彼此隔離、能撐過行程結束——不是
   剛好跑成功的單次呼叫。
3. **具名 reviewer 的分支真的收到喚醒。** 一份把 `supervisor-reviewer` 對應到分支 A 的
   路由表，加上一份指名該 reviewer 的 `ROLE_WAKE_V1` payload，在 8.7 秒內產出
   `{"status": "DELIVERED"}`。事後從分支 A **內部**詢問，該分支說出了它被交付的 payload
   路徑，被問到先前被告知什麼時仍答 `ALPHA-7731`。所以喚醒真的落進了 reviewer 自己的
   分支並延續它，而不是開了一個新的。

第 3 點是最關鍵的證據，是這個 host 版本的 E11：交付是從**接收端**確認的，不是從送出端自己
的回傳值。`DELIVERED` 狀態是對一個命令的宣稱；分支說出 payload 是對「什麼真的送達」的事實。

**owner 正在看的分頁——量測後禁止。** owner 問過自己的分頁會不會被看到移動。量測自 owner
特意開的一個拋棄式空白 workspace：`claude agents --json` 回報一個 app 分頁背後真實的
session id（`07199111-…`），所以 Router 確實能找到開著的分頁；先前「這在結構上不可能」的
說法講得太重——沒有*注入*介面，但接續同一個對話需要的 id 就在那裡。用 `claude -p
--resume` 驅動那個 id **成功**：4 秒內結束碼 0，那個對話自己的 transcript 從 31 行／
41,042 bytes 長到 41 行／49,516 bytes，沒有建立第二個檔案，那個 turn 真的落進了分頁的
對話裡。app 畫面**什麼都沒變**：owner 全程盯著那個分頁，回報沒有任何變化，而 app 的登記檔
時間戳仍停在它剛收到的那次寫入之前 76 秒。所以外部驅動一個開著的分頁，會產生 owner 看不到
的工作，而 app 繼續拿著一份跟檔案對不上的記憶體歷史——一份 transcript 兩個寫入者。能做這件
事不代表值得提供這個功能。

**E14-R9。** `live_session_ids` 在每次遞送前讀取清單，目標被佔用的喚醒以
`BRANCH_HELD_BY_LIVE_SESSION` 拒絕；讀不到清單也一樣拒絕（`LIVE_SESSION_CHECK_FAILED`）
——不知道不等於知道分支是空的，這個守衛若 fail-open 就沒有存在的意義。對同一個分頁實機
驗證：`{"code": "BRANCH_HELD_BY_LIVE_SESSION", "status": "REFUSED"}`，transcript
byte 數在前後完全一致，所以是拒絕真的阻止了寫入，不只是事後回報。

**E14-R10——行程存活不是該問的問題。** owner 回報一個他沒碰過的分頁離開了現役清單，之後
再查發現它的行程又回來了。行程來來去去，分頁本身卻整段時間開在螢幕上，所以只靠
`live_session_ids` 會在每一次行程空窗期都把那個對話當成是空的，並無聲寫進去。桌面 app 在
`%APPDATA%\Claude\claude-code-sessions\**\local_*.json` 底下每個 session 存一份 JSON
檔，每筆記錄同時帶著 app 自己的 `sessionId` 和它包住的 `cliSessionId`，所以這個宣稱比
行程活得久，且能從磁碟讀到。`app_claimed_session_ids` 在每次遞送前讀它，以
`BRANCH_HELD_BY_APP_TAB` 拒絕；解析不了的記錄，或裝了 app 卻沒有這份存放區，都以
`APP_CLAIM_CHECK_FAILED` 拒絕——讀不到的那筆記錄可能正是要緊的那筆。實機驗證：對照
owner 真實的登記檔，dispatcher 回傳 `BRANCH_HELD_BY_APP_TAB`，transcript byte 數不變。
這個守衛讀的是 app 自己擁有、卻沒有文件記載的狀態，這是刻意接受的，因為失敗模式只有一個
方向是安全的：格式一旦變動，讀取失敗，喚醒就被**拒絕**，絕不會被無聲放行；一個 fail-open
的守衛不值得擁有。

被喚醒的分支被問到收到了什麼；沒有被觀察到真的執行一次審閱並送出裁決——這最後一哩，跟
Antigravity 通道一樣，在這裡仍未被證明。這個結果也沒有改變上面的負面結論：沒有任何介面能
寫進 owner 正坐在裡面的對話，Router 驅動的是它自己擁有的分支。

- **反向突變證據**：E14-R7——路由改成永遠選第一筆，6 格轉紅；拿掉探測標記檢查，R6 轉紅；
  兩者皆已還原成綠。
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

無 migration。執行環境需在目標主機設定環境變數 `CLAUDE_CODE_OAUTH_TOKEN`，值為
`claude setup-token` 發出、`sk-ant-oat01-` 開頭的長期 token（互動式 OAuth token 無法
無人值守刷新，不適用）。路由表 `<johnny-root>/claude-branch-routes.json` 是每台 host
各自宣告的設定檔，隨 host 建立，不隨程式碼部署，也不需要遷移腳本。回滾：無紀錄（早於本欄
要求）。

## 完成回寫

- 實際檔案：`library/local_orchestration/claude_wake_command.py`
- commit：`da33781`（見上方共同基準；發行版本 `v0.4.5`）
- WorkProgress：不適用

```johnny-status
id = E14
title = Claude 分支喚醒命令
state = APPROVED
commit = da33781
released_in = v0.4.5
stage = R1 | 探索 | DONE
stage = R2 | 認證閘門 | DONE
stage = R3 | 分支路由 | DONE
stage = R4 | 具名拒絕 | DONE
stage = R5 | 訊息只帶路徑 | DONE
stage = R6 | probe 誠實性 | DONE
stage = R7 | 突變鑑別力 | DONE
stage = R8 | 實機驅動 | DONE
stage = R9 | 現役行程守衛 | DONE
stage = R10 | app 分頁守衛 | DONE
```
