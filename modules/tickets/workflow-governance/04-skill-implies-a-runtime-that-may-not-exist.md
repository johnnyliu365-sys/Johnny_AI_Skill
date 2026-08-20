# 04｜Skill 敘述了沒有發生的喚醒

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理缺陷；`P0`，非產品行為） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/PITFALL-REGISTER.md`（同族缺陷：D5，文件描述了不存在的入口） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | 不適用（僅 Markdown 文件，無程式碼變更） |
| 狀態 | `DONE`（board 記為 `APPROVED`；已隨 v0.4.4 發行） |
| 共同基準 | `main` = `36ede46` |
| 實作者 | 控制面（本票為例外執行，見下方 Owner override record） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 見下方「實際原始碼路徑」所列六個檔案 |
| 禁止修改 | 上列以外的任何檔案；不得引入新的無條件喚醒斷言 |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

`P0`——它製造假的完成敘事，這正是本專案存在的目的所要防止的失敗模式。2026-08-20，owner 觀察一個 agent 在真實專案（`SourceProjectA-code-review`）回報：

> `3338fdc` 不只是交付證據，也是 `ImplementationReturn` 的 commit 喚醒訊號。
> Router 應依此把案件喚醒並交給 `SUPERVISOR_REVIEWER`

owner 的回應：**根本沒有喚醒阿.**

驗證結果：`%LOCALAPPDATA%\JohnnyRouter` 在那台機器上不存在，目標專案沒有訂閱或喚醒能力設定，也沒有 runner 為它啟動。**不存在任何能喚醒任何東西的機制。**

skill 全篇以直述句陳述喚醒行為（`context-routing.md`「The Router wakes the architecture owner」、`model-role-routing.md`「this wakes the architecture owner」與整節「Mandatory wake triggers」、`ticket-decomposition.md`「Both routes wake the architecture owner」）。agent 把這些讀成正在運行系統的描述，但它們其實是在描述一個**協定**，執行者是安裝並為該專案武裝的 runtime（經 `dispatch issue` → `runner subscribe` → `runner start` 並宣告喚醒能力）。在這一切都不存在的情況下，上述每句話作為協定仍然為真，作為行為卻是假的。skill 從未區分兩者，於是忠實遵循它的稱職 agent 會敘述沒有發生的喚醒，把一個有破洞的完成故事交給 owner。

這與先前在外掛自身文件裡發現兩次的缺陷同族（`PITFALL-REGISTER` D5：文件描述了從未存在的入口；裸的 `johnny-router uninstall`）。本次更嚴重，因為讀者是**agent**，其輸出**以事實之名交給 owner**。

全鏈路資格驗證證明了武裝路徑端到端成立，owner 被告知迴路可行、裝上之後，卻看到一個 agent 敘述了從未發生的喚醒。缺口在於：**武裝路徑被窮盡測試過；未武裝路徑——每個真實專案的起始狀態——完全沒有被測過。** skill 的文字就是未武裝路徑的行為，而沒有人帶著這個問題讀過它。與 D5 同族，高一層：這次讀者是 agent，輸出被當作事實交給了 owner。

## 實作範圍、依賴與 ticket elements

1. skill 內每一句喚醒敘述都要陳述其條件：runtime 必須已安裝且為該專案武裝，否則沒有喚醒。優先措辭是條件式且點名機制的——「一個武裝的 runner 喚醒…」，不是「Router 喚醒…」。
2. skill 新增明確的就緒檢查節：agent 如何判斷自動化對目前專案是否是活的（root 存在、訂閱存在、runner 正在跑、喚醒能力已證實），以及不成立時該說什麼——handoff 已提交，且**必須由 owner 通知審閱者**，而不是暗示喚醒已發生。
3. agent 絕不能回報一個自己沒觀察到的喚醒。提交一個 handoff leaf 是提交本身的證據，不是交付的證據。

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：控制面（Opus 5）。
- reviewer：控制面（Opus 5）。
- **Owner override record**：本票由控制面直接執行修正，未派工給另一個 worktree/implementation owner。`P0` 且發現者與裁決者皆為觀察此缺陷的 owner／控制面互動過程本身；owner 於 2026-08-20 按釋出直接授權（發行紀錄「A」）。審閱仍由控制面自身完成，屬於本專案「控制面不得兼任實作」規則下記錄在案的例外，理由是修正範圍僅為 skill 文件措辭，且 owner 已直接參與問題重現。
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：純文件（skill 與 ticket markdown）改寫，不觸及任何 UI 邊界。

- 實際原始碼路徑：
  1. `skills/johnny-project-takeover/SKILL.md`
  2. `skills/johnny-project-takeover/references/context-routing.md`
  3. `skills/johnny-project-takeover/references/model-role-routing.md`
  4. `skills/johnny-project-takeover/references/ticket-decomposition.md`
  5. `skills/johnny-project-takeover/references/router-control.md`
  6. `modules/tickets/workflow-governance/`、`modules/tickets/PITFALL-REGISTER.md`
- 公開契約／資料模型：無（僅措辭與新增章節）

## TDD 設計

1. 正常行為：skill 與其 references 內沒有任何一句喚醒敘述是無條件的；每句都點名機制與前提。
2. 規則違反／輸入錯誤：不適用（無程式碼輸入路徑）。
3. 外部失敗／fail-closed：未武裝專案下，agent 依「就緒檢查節」的四個可觀察條件判定並誠實回報，絕不宣稱喚醒發生。
4. 回歸保護：`skills/` 為 payload root，改動即改 bundle digest；發行流程需同步更新 digest 並經 preflight 比對，不得靜默偏離已發行артifact。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不涉錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 純文件改寫，無執行路徑 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| 04-R1 | 沒有任何喚醒句無條件斷言喚醒；每句都點名機制與前提 | `grep` 對「Router wakes」「routes wake the」「this wakes the」於已改檔案返回零命中 |
| 04-R2 | 就緒檢查節陳述四個可觀察條件與未武裝情境下的誠實措辭 | `SKILL.md` 新增「Automation readiness」節，含 root／subscription／running runner／proven capability 四項與未武裝時的措辭 |
| 04-R3 | skill 明文只有觀察到才能回報喚醒，且已提交的 handoff 不是交付 | skill 文字逐字檢查 |
| 04-R4 | `skills/` 為 payload root，改動即改 bundle digest；因此隨下一次發行釋出，而非靜默偏離已發行 artifact | 見下方「正式環境移植 SOP」 |

- **反向突變證據**：不適用（純文件措辭，無可執行的行為分支可供突變；以 04-R1 的 grep 零命中與逐字檢查取代）。
- **缺陷修正** baseline-red：`SourceProjectA-code-review` 專案中，agent 依 skill 原文回報「Router 應依此把案件喚醒」，而 `%LOCALAPPDATA%\JohnnyRouter` 不存在、無訂閱、無 runner——owner 判定「根本沒有喚醒阿」，即本票的紅燈證據。

## 正式環境移植 SOP

`skills/` 是 payload root，本票改動使 bundle digest 改變，因此不能靜默偏離已發行 artifact，須隨下一次發行釋出：

- 已隨 v0.4.4 發行：commit A `ed8055b`（版本升級＋本修正）、commit B `f033ec7`（digest 釘死 `c2216b6e…`、479,704 bytes、preflight `MATCHED`）。
- 發行前全套件 992 passed 零殘留；gated qualifications（live install、whole chain、vita）16 passed。
- 回滾點：`rollback-pre-044` → `b1a61ca`。

## 完成回寫

- 實際檔案：`skills/johnny-project-takeover/SKILL.md`、`skills/johnny-project-takeover/references/context-routing.md`、`skills/johnny-project-takeover/references/model-role-routing.md`、`skills/johnny-project-takeover/references/ticket-decomposition.md`、`skills/johnny-project-takeover/references/router-control.md`
- commit：`9a85e45`（本票審閱定案）；發行 commit `ed8055b`／`f033ec7`（見上方正式環境移植 SOP）
- WorkProgress：不適用

```johnny-status
id = 04
title = Skill 敘述了沒有發生的喚醒
state = APPROVED
commit = 9a85e45
released_in = v0.4.4
stage = R1 | 事實查證 | DONE
stage = R2 | 措辭修正 | DONE
stage = R3 | 就緒檢查節 | DONE
stage = R4 | 發行 | DONE
```
