# V1｜Owner 狀態總覽介面（已被 V2 取代）

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理／基礎設施功能票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/event-runner-binding/e14-claude-branch-wake-command.md`（本票所有「host 實測事實」的出處） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（R2 產生器；R1 樣張僅 HTML／CSS，見下方責任邊界） |
| 狀態 | `SUPERSEDED`（三個 lane 的內容已被 V2 取代；量測事實與 R2/R3 的機制仍是後續票的依據，故一併轉換，不留唯一例外；board 未追蹤此票） |
| 共同基準 | `main` at `da33781`（E14 closed） |
| 實作者 | R1：owner 直接核准樣張；R2 起：控制面（owner 把後續實作重新指派給控制面，見下方角色指派） |
| 審閱者 | R1 由 owner 本人直接拍板核准，未經控制面二次審閱 |
| 責任邊界 | R1：一個自足 HTML 檔案（樣張）；R2：`library/local_orchestration/owner_status_surface.py`；R3：R2 所讀的既有 accessor；R4：toast 通知路徑（未關閉，見下方） |
| 禁止修改 | 目標專案任何檔案（僅寫入 per-user Johnny root）；不得引入 polling／heartbeat／timer／port |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

不開終端機、不讀 JSONL 檔，owner 就能看到哪些工人在跑、什麼在等他的決定、什麼已經完成。

兩個交付物，依序：R1 一個自足 HTML 檔案的靜態樣張，讓 owner 先反應（無產生器、無資料
管線），owner 可以說「對，我要看的就是這個」或在任何人動手寫機制之前先改方向；R2 是 owner
核准樣張之後才做的產生器，一個只用 stdlib 的 Python 模組，在狀態變化的當下用真實
Johnny-root 狀態重寫那頁。

**已建立、不要重新發現的事實**（量測自 owner 的 Windows host，證據在
`modules/tickets/event-runner-binding/e14-claude-branch-wake-command.md`）：

- 桌面 app 不能是這個介面。驅動一個已開分頁背後的對話會寫進 transcript 但畫面上什麼都不
  渲染（owner 全程盯著看，app 的登記檔時間戳停在它剛收到的那次寫入之前 76 秒）；
  `claude --bg` 背景 agent 被 `claude agents --json` 追蹤到，但 app 對它們什麼都不顯示；
  CLI session 沒有 MCP servers（`claude mcp list` → 無），所以 Router 驅動的工人也不能
  叫 app 自己的 session-message 通道。
- 這台 host 上，Windows toast 經由 PowerShell 的 WinRT `ToastNotificationManager` 真的
  會渲染，不必額外裝模組，owner 也看到了。owner 也判定它單獨不夠：只出現一次就消失，扛不
  住常駐狀態。
- **`TOAST_SENT` 不是「有人看到」的證明**，只代表 API 接受了這次呼叫。Focus Assist 會
  無聲吞掉 toast。這跟 `auth status` 宣稱 `loggedIn: true`、而伺服器後來用 401 拒絕那個
  token 是同一件事——API 自己回報的成功值不等於能力本身。

## 實作範圍、依賴與 ticket elements

**R1——先做靜態樣張，做完就停。** 一個自足 HTML 檔案，無 build step，除了可能用到的
Google Fonts 樣式表之外不對外發請求。內容要寫實，不放 lorem、不放 `TODO`、不放明顯假的
`foo`/`bar`；用專案真實詞彙：`reviewer_ref`、`project_id`、`ticket_reference`、
`receipt_id`、`attempt_id`，以及下面列的真實狀態名稱。三個 lane，依優先序排列——「owner
需要處理的排最前面」，因為這正是這頁存在的唯一理由：

| Lane | 內容 |
| --- | --- |
| Waiting on you | Router 拒絕或無法在沒有人的情況下推進的項目。每列要有：為什麼停了（具名代碼）、哪個專案哪張票、等了多久、owner 該做什麼 |
| Working | Router 正在驅動的分支：reviewer、專案、票、為什麼被喚醒、何時開始 |
| Done | 已完成的裁決：`APPROVAL_GRANTED` / `APPROVAL_DENIED`、專案、票、何時 |

「Waiting on you」的列至少要能代表這些真實拒絕碼，因為每一個都對應不同的 owner 動作，全部
長一個樣子這頁就沒用了：`BRANCH_HELD_BY_APP_TAB`（owner 在 app 裡開著那個對話，Router
拒絕寫入以免看不見；owner 動作：關掉分頁，或自己處理）、`REVIEWER_NOT_MAPPED`（那個
reviewer 沒有路由到任何分支；owner 動作：加路由）、`NOT_AUTHENTICATED` /
`DRIVE_FAILED`（host 無法驅動；owner 動作：重新認證）、`CANDIDATE_INBOX`（這個專案沒有
證實喚醒能力，項目被記錄但沒有人被喚醒；owner 動作：自己轉達）。

樣張的設計限制：這是一個操作介面，是被掃視而非被閱讀的，狀態要能從形狀一眼看出，不是只靠
文字；light 與 dark 都要處理好，包含 host 完全沒標記主題屬性的「system」狀態；過寬的列在
自己的容器內捲動，頁面本身不橫向捲動；時間戳是給人判斷「這個過期了嗎」用的，相對時間是
重點，絕對時間要有但是次要；不放裝飾性的儀表板擺設——沒有不畫真實東西的假 sparkline、沒有
虛榮總數、沒有沒單位的量表，頁面上每個元素都要能對應到 R3 列的真實狀態來源。

**R2——產生器。** 只有 R1 核准之後才開始。一個只用 stdlib 的模組，
`library/local_orchestration/owner_status_surface.py`，從真實狀態渲染核准後的頁面，並
原子寫入（temp file + `os.replace`，沿用 `event_runner._write_state` 既有的模式）到由
`JohnnyRootLayout` 推導、絕不可設定的路徑。硬限制：只能用 stdlib（runtime venv 是雜湊鎖定
的，新增依賴超出本票範圍會被拒絕）；不准 polling、不准 heartbeat、不准 timer、不准開
port——頁面只在狀態變化時被已經在處理該變化的機制重寫，瀏覽器自己的重新整理是唯一允許的
重複；絕不寫進目標專案，只寫 per-user 的 Johnny root；只讀不改它顯示的狀態，這個介面沒有
任何權限，不能宣稱、settle 或消費任何東西。

**R3——它渲染的狀態。** 透過既有的 accessor 讀取，不要硬編檔名；每一個都要先在程式碼裡
確認過才用，不要發明一個沒有東西寫過的來源：runner 狀態——`event_runner.runner_state_path`；
已武裝的訂閱——`event_runner.subscriptions_path`；沒有人被喚醒的項目——
`wake_candidate_inbox.read_candidates`；等待被消費的審閱回傳——`review_return` /
`review_return_consumption` 這對；派工歷史——`dispatch_authority` 寫的 dispatch
journal；喚醒嘗試結果，包含拒絕——role-wake attempt store。來源讀不到時，頁面要在那個
lane 的位置說明，絕不能把「這讀不到」渲染成看起來像「沒有東西在等」的空 lane——那樣會
毀掉這個介面存在的整個目的。

**R4——通知，擺在它該在的位置。** toast 是指標，不是紀錄本身：持久紀錄要**先**寫，寫完才
嘗試 toast；toast 能力要**被證實，不能被假設**，比照
`wake_capability.probe_wake_capability`——「通知能運作」這種對 owner 可見的宣稱，必須建立
在通知路徑真的跑過的基礎上，光是回傳值 `TOAST_SENT` 不能算數，要自己決定什麼才算數並寫下
為什麼有鑑別力；失敗或被吞掉的 toast 不改變項目狀態，它依然在頁面上、依然在檔案裡；每個
項目最多一個 toast，不重送、不催促、不做 digest timer（那就是 polling 了）。

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：R1 由 owner 本人核准方向；R2 起 owner 把實作直接重新指派給控制面
  （記錄於此，屬於本專案「控制面不得兼任實作」規則下的例外）。
- reviewer：R1 的審閱者是 owner 本人；R2/R3/R4 無紀錄（早於本欄要求）。
- **Owner override record**：owner 於 R1 核准後把 R2 起的實作直接指派給控制面；R4 仍未
  關閉。
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

- UI 組合邊界（screen／layout／component）：R1 為單一自足 HTML 檔案（無 build、單頁、
  三個 lane）；R2 起由 Python 產生器改寫同一頁面，非元件化框架。
- Composition Root 與依賴生命週期：`owner_status_surface.py` 在狀態變化當下被呼叫、整頁
  改寫（原子寫入：temp file + `os.replace`，沿用 `event_runner._write_state` 既有模式），
  無常駐 process、無 polling。
- 注入的具名介面：R3 列出的既有 accessor（`event_runner.runner_state_path`、
  `event_runner.subscriptions_path`、`wake_candidate_inbox.read_candidates`、
  `review_return`/`review_return_consumption`、`dispatch_authority` 的 dispatch
  journal、role-wake attempt store）——只讀，不寫。
- production binding 與 test fake／stub：production 呼叫這些 accessor 的即時實作；測試
  以可控的假來源（含可控的「讀不到」情境）替換，驗證每個 lane 各自失敗、互不牽連。
- 元件輸入／輸出、loading／empty／error、權限與可存取性驗收：來源讀不到時該 lane 顯示
  「讀不到」而非空清單（V1-R3）；light／dark／system 三態皆須正確；寬列於自己的容器內
  捲動，頁面本身不橫向捲動；無權限概念（單一 owner 本機頁面）。

- 實際原始碼路徑：R1 `v1-owner-status-surface.html`；R2/R3
  `library/local_orchestration/owner_status_surface.py`；R4（未關閉）
  `CommandRoleWakePort` 的 stdout 傳遞路徑
- 公開契約／資料模型：三個 lane（Waiting on you／Working／Done）＋ 四個具名拒絕碼
  （`BRANCH_HELD_BY_APP_TAB`／`REVIEWER_NOT_MAPPED`／`NOT_AUTHENTICATED`／
  `DRIVE_FAILED`／`CANDIDATE_INBOX`）與各自 owner 動作文字

## TDD 設計

1. 正常行為：R1 樣張內容經 owner 核准；R2 產生器把核准後的頁面用真實狀態渲染並原子寫入
   Johnny root。
2. 規則違反／輸入錯誤：不適用（無外部使用者輸入；來源是既有 accessor 讀出的既有狀態）。
3. 外部失敗／fail-closed：任何來源讀不到時，該 lane 顯示「讀不到」而非空清單，絕不讓
   「讀不到」偽裝成「沒有等待中項目」（V1-R3）；toast 送達失敗或被吞不改變項目本身狀態
   （V1-R5）。
4. 回歸保護：每個具名拒絕碼都各自映到自己的 owner 動作文字（V1-R4）；頁面上每個元素都能
   追溯到 R3 列出的來源欄位，沒有裝飾性假資料（V1-R6）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | 讀不到的來源必須顯示「讀不到」而非空清單——「空」與「不知道」必須分辨（V1-R3） |
| 3 | 權限繞過 | 否 | 單一 owner 本機頁面，無多使用者權限模型 |
| 4 | Token 格式與比較 | 否 | 頁面只讀狀態，不驗證身分 |
| 5 | 錯誤碼是否一致 | 是 | 四個具名拒絕碼必須各自可區分，且各自對應正確的 owner 動作（V1-R4） |
| 6 | 例外是否會拋出 | 是 | 產生器寫入必須是原子操作（temp file + `os.replace`），任何寫入中斷都不能留下半份檔案（V1-R2） |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| V1-R1 | 靜態樣張交付且經 owner 核准 | owner 的回應記錄在本票 |
| V1-R2 | 產生器在 Johnny root 下原子寫入頁面，只用 stdlib | 測試斷言絕不會觀察到半份檔案；import-surface 測試證明沒有第三方 import |
| V1-R3 | 讀不到的來源渲染成「讀不到」，絕不是空 lane | 用損毀的來源測試，斷言該 lane 這樣說；反向突變（吞掉錯誤、渲染成空）要轉紅 |
| V1-R4 | 每個需要 owner 動作的拒絕碼都帶著自己的動作文字到頁面上 | R1 列出的每個代碼各自測試 |
| V1-R5 | 持久紀錄先於 toast，失敗的 toast 不影響項目 | 用會失敗的 toast 路徑測試，斷言紀錄存在且項目仍正常渲染 |
| V1-R6 | 頁面上沒有裝飾性的東西 | 審閱：每個元素都能追溯到 R3 的一個欄位 |

**Delivery log（已記錄的實際結果，原樣保留）：**

- **R1 核准。** 樣張落地為 `v1-owner-status-surface.html`，owner 核准了方向。三個票上
  要求但樣張沒畫出來的東西，改在 R2 補：四個拒絕碼原本共用一種 chip 樣式、沒有列說明
  owner 該做什麼、沒有「讀不到來源」狀態；樣張也是英文，而不是派工要求的繁體中文。
- **R2/R3 落地。** `library/local_orchestration/owner_status_surface.py`，只用
  stdlib，原子寫入 `<johnny-root>/owner-status.html`，瀏覽器每 30 秒自我重新整理一次。
  每個來源各自獨立讀取，一個失敗不會讓另一個沉默；缺檔案回報為真的空，解析不了的檔案回報
  為讀不到（附路徑與解析錯誤），該 lane 帶 `不完整` 旗標，頁首也說明頁面不完整。
  **反向突變**確認測試組有鑑別力：在讀不到的 lane 底下渲染讓人安心的空訊息，會讓一格轉紅；
  吞掉來源錯誤會讓兩格轉紅；兩者都已還原成綠。17 cells，19 subtests。
- **R4——未關閉，卡在缺少的紀錄。** `CommandRoleWakePort` 用 `capture_output=True` 跑
  喚醒命令，然後**丟棄 stdout**：非零結束碼時回傳不帶理由的 `NO_EFFECT`。所以 dispatcher
  的具名拒絕碼——`BRANCH_HELD_BY_APP_TAB`、`REVIEWER_NOT_MAPPED`、
  `NOT_AUTHENTICATED`——被寫進沒有人讀的管線，磁碟上什麼都沒有。介面已經知道怎麼呈現
  它們，每個的 owner 動作文字也寫好測過了，但今天只有 `CANDIDATE_INBOX` 和
  `RUNNER_NOT_RUNNING` 能從真實狀態抵達頁面。關閉 R4 意味著讓這個理由變得持久：把子行程
  的具名代碼記錄成一個觀察值、放在這次嘗試旁邊，但不能讓它影響任何控制決策——port 的具型
  effect status 必須繼續只由結束碼與逾時行為決定，絕不能來自子行程印出的任何東西。

- **反向突變證據**：見上方 R2/R3 落地段落——拿掉「讀不到」的區塊渲染成安心空訊息會讓
  一格轉紅，吞掉來源錯誤會讓兩格轉紅，兩者皆已還原成綠。
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（僅寫入 per-user Johnny root 的靜態頁面，無 migration、無新增環境變數、無需回滾
程序）。

## 完成回寫

- 實際檔案：`v1-owner-status-surface.html`、`library/local_orchestration/owner_status_surface.py`（R4 尚未關閉，見上）
- commit：無紀錄（早於本欄要求）
- WorkProgress：不適用
