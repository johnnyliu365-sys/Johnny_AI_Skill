# P1｜用 Router 記帳，管多個平行工人

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理／基礎設施功能票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/workstation-dispatch/w5-cross-process-exactly-once.md`（前例：W5 查出自寫元件完全沒有鎖，本票要問的正是同一族問題） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `main`，V2-S2 之後 |
| 實作者 | 控制面 |
| 審閱者 | 控制面（Opus 5）；與實作者不同 worktree |
| 責任邊界 | `dispatch_authority` 既有機制的並行安全性驗證；見下方「沒有被證明的」四項 |
| 禁止修改 | Router 側程式碼不得出現任何 host 專屬名詞（`subagent`／`claude`／`codex`） |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

同時有多張票在跑的時候，「哪張票在誰手上、在哪個 worktree、發過哪張 receipt」是**持久的
事實**，不是記在對話裡的東西。同一張票發不出第二份 receipt，兩個工人不會互相踩，每個
verdict 只被消費一次。

owner 指出 Codex 也有子代理，所以這條線是通用的，不是 Claude 專屬。這件事決定了邊界該
畫在哪：**host 生工人**（怎麼生是 host 的事——Claude 的 Agent 工具、Codex 的子代理、或
未來任何機制），**Router 只記帳**（某張票、某個 worktree、某個分支、某張 receipt）。
Router 這一側絕對不能出現 `subagent`、`claude`、`codex` 這些字——一旦出現，這條線就綁死
在一個 host 上，而它的價值正好來自不綁；這個性質要用測試守住，不能靠自律（見下方
P1-R5）。

## 實作範圍、依賴與 ticket elements

**已經有的，不要重造。** 查過了，Router 這側幾乎是齊的。`admit_dispatch` 已經是完整的
閘門：讀 owner 授權（沒有就 `DISPATCH_AUTHORITY_ABSENT`）→ `verify_worktree_contained`
（用解析後的真實路徑驗 worktree 在 repo 根目錄下，junction 一律拒絕）→ 登記 artifact
（identity 衝突會擋）→ CAS 發 receipt → 回讀驗證 `verify_receipt_claimable` → 全程寫
journal，帶 principal。`DispatchAdmissionRequest` 本來就帶 `worktree_fingerprint`、
`branch_fingerprint`、`repository_root`、`host_worktree_path`——「一個工人在某個
worktree 上為某張票工作」這個模型已經存在，只是從來沒有人拿它跑平行。
`review_return` / `review_return_consumption` 也已經有跨行程鎖與恰好一次消費（W5）。

**沒有被證明的，這才是這張票的內容：**

1. **並行發放安不安全。** 這是最可能有缺陷的地方，而且有前例：W5 查出自寫的元件完全
   沒有鎖，而更早的元件都有。兩個行程同時為不同票 `admit_dispatch`，或同時為同一張票，
   會發生什麼——沒有人測過。
2. **工人怎麼把 verdict 交回來。** 可以用 Bash 跑 runtime 的 `review submit`，機制上通，
   但沒實機驗過。
3. **對話死掉留下的孤兒 receipt。** 工人不在了、receipt 還在。這跟孤兒 lease 是同一族
   問題，那一族咬過我們一次。
4. **隔離 worktree 實際開在哪。** Agent 工具有 `isolation: worktree`，看起來開在
   `.claude/worktrees/`，但那是推測不是量測——owner 有明文規矩：不准在 repo 根目錄外面
   長資料夾。包含性閘門會擋，但要先知道它擋不擋得住。

**第一個交付物是測試，不是抽象。** 不要先寫新模組。先寫一個會失敗的測試，證明既有機制在
並行下成立或不成立。R1 到 R4 如果**通過**，代表 Router 這側本來就成立，缺的只有薄薄一層
黏合，那是好消息；如果**失敗**，就找到一個真缺陷——那更值得。兩種結果都不是白工。

**之後才做的（先不要做）：** 工人回傳 verdict 的實機驗證、孤兒 receipt 政策、把 V2 的
看板接到這些 receipt 上。等上面證明完再說。

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：控制面。
- reviewer：控制面（Opus 5）；與實作者不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：純 Router 側記帳與並行安全驗證，不觸及任何 UI 邊界。

- 實際原始碼路徑：`dispatch_authority`（既有模組，本票驗證其並行安全性，不重造）；新增的
  並行測試所在路徑由實作者決定
- 公開契約／資料模型：`DispatchAdmissionRequest`（既有：`worktree_fingerprint`、
  `branch_fingerprint`、`repository_root`、`host_worktree_path`）；本票不新增欄位，只
  驗證既有契約在並行下是否成立

## TDD 設計

1. 正常行為：兩張不同的票並行發放，各自拿到自己的 receipt，互不干擾（P1-R1）。
2. 規則違反／輸入錯誤：同一張票並行發放兩次，只有一份 receipt 成立，另一次拿到具名拒絕
   （P1-R2）。
3. 外部失敗／fail-closed：worktree 在 repo 根目錄外時被拒絕，且**沒有**發出 receipt
   （P1-R3）。
4. 回歸保護：journal 記得下每一次嘗試，包含被拒絕的（P1-R4）；Router 這側不含任何 host
   名詞，掃原始碼斷言零命中（P1-R5）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 不涉一般輸入格式驗證 |
| 3 | 權限繞過 | 是 | 直接：worktree 在 repo 根目錄外被拒絕（P1-R3）；間接：包含性閘門必須擋得住 junction／reparse point，不能靠另一條路徑繞過 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | `DISPATCH_AUTHORITY_ABSENT` 與並行重複發放的具名拒絕碼必須各自可區分，不得被同一個泛用錯誤蓋掉 |
| 6 | 例外是否會拋出 | 是 | 兩個行程同時 `admit_dispatch`（不同票／同一票）時，非贏家一側必須是具名拒絕，不是未捕捉例外 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| P1-R1 | 兩張不同的票並行發放，各拿到自己的 receipt，互不干擾 | 真的多行程，不是執行緒 |
| P1-R2 | 同一張票並行發放兩次，只有一份 receipt 成立，另一次拿到具名拒絕 | 同上；斷言恰好一次 |
| P1-R3 | worktree 在 repo 根目錄外時被拒絕，且**沒有**發出 receipt | 拒絕後查發放紀錄為空 |
| P1-R4 | journal 記得下每一次嘗試，包含被拒絕的 | 讀 journal 斷言 |
| P1-R5 | Router 這側不含任何 host 名詞 | 掃原始碼斷言 `subagent`／`claude`／`codex` 零命中——通用性用測試守住 |

- **反向突變證據**：`<待填>`（P1-R6：拿掉包含性閘門，P1-R3 應轉紅；還原後應轉綠——待實作完成後回填）。
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（Router 側記帳邏輯，無 migration、無新增環境變數）。

## 完成回寫

- 實際檔案：`<待填>`
- commit：`<待填>`
- WorkProgress：不適用

```johnny-status
id = P1
title = 用 Router 記帳管多個平行工人
state = IN_PROGRESS
stage = T | 並行證明 | DONE
stage = G | 黏合層 | OPEN
stage = V | 工人回傳 | OPEN
```
