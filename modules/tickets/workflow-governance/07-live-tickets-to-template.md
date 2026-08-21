# 07｜活票轉換為標準格式

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（文件治理；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/workflow-governance/06-mklink-output-decoded-as-utf8.md`（已轉換的基準） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／無 receipt／worktree `.worktrees/gov-07`／branch `implement/gov-07-ticket-format`／baseline `ef6afea` |
| 實作語言 | 不適用（僅 Markdown 文件） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `ef6afea` |
| 實作者 | Sonnet 5（一般小票；基準已轉換的 06 為樣板） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 下列九個檔案的**結構**改寫 |
| 禁止修改 | 任何 `.py`、`library/`、`tests/`、其他票、`TEMPLATE.md` 本身；以及各票 `johnny-status` 區塊內的**值** |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

九張活票全部符合 `TEMPLATE.md` 的表頭欄位與章節結構，且看板顯示的內容不變。

歷史票（未上板者）本次**不動**——owner 決定等它們被當成重要參考時再轉。

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：`<派工時填入>`；於 `.worktrees/gov-07` 實作。
- reviewer：控制面（Opus 5）；與實作者不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：純文件改寫，不觸及任何 UI 邊界。

- 實際原始碼路徑：
  1. `event-runner-binding/e14-claude-branch-wake-command.md`
  2. `owner-visibility/v1-owner-status-surface.md`
  3. `owner-visibility/v2-ticket-status-surface.md`
  4. `owner-visibility/v2-s1-done-goes-grey.md`
  5. `owner-visibility/v2-s2-two-quiet-states.md`
  6. `owner-visibility/v2-s3-open-stage-signal.md`
  7. `owner-visibility/v2-s4-naming.md`
  8. `workflow-governance/04-skill-implies-a-runtime-that-may-not-exist.md`
  9. `workflow-governance/05-a-blocked-rename-leaves-an-orphan.md`
  10. `workstation-dispatch/p1-parallel-worker-dispatch.md`

  （`v1` 已 `SUPERSEDED` 但仍在庫中，一併轉換以免留下唯一的例外。）

## 轉換規則

**保留**：該票獨有的契約——結果、驗收表、邊界、已記錄的證據與 commit。

**搬走或刪除**：全域規則的副本。文件層級規定 ticket「不得承載未核准需求或全域規則
副本」。凡是「一次只能跑一個 pytest」「不要截斷輸出」「反向突變的定義」這類每張票都
適用的規則，刪掉——它們已經在 `Workflow.md`、`implementation-tdd.md`、
`PITFALL-REGISTER.md`。票裡只留指向它們的一行。

**不得改動**：各票 ```johnny-status``` 區塊內的任何值（`id`／`title`／`state`／
`commit`／`released_in`／`stage` 行）。看板從那裡讀，改動會讓狀態失真。區塊位置可移動，
內容一個字元都不能變。

**已結案的票**：`反向突變證據` 與 `完成回寫` 欄位填入該票已記錄的實際證據；沒有記錄
的填「無紀錄（早於本欄要求）」，**不要回頭補造**。

## TDD 設計

不適用（無程式碼變更）。驗證改以下列可觀察檢查取代。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不涉錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 無執行路徑 |

## 完成定義與證據

- 十個檔案都通過：`grep -q "^| 對應規格 ID |"`。
- 看板輸出**逐字不變**：轉換前後各跑一次
  `build_document(repository_root)`，比對 `tickets` 清單相等（`generated_at` 與
  `head` 除外）。這是本票唯一有鑑別力的檢查——它會抓到任何被改壞的 `johnny-status`。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。
- **反向突變證據**：不適用（無行為變更）。改以上述看板逐字比對為證。
- 缺陷修正 baseline-red：不適用。

## 正式環境移植 SOP

不適用。

## 完成回寫

- 實際檔案：十張活票（`modules/tickets/` 下 e14／v1／v2／v2-s1~s4／04／05／p1）
- commit：`implement/gov-07-ticket-format`，看板比對逐字相同（11 張）
- WorkProgress：不適用

```johnny-status
id = 07
title = 活票轉換為標準格式
state = DONE
stage = C | 轉換 | DONE
stage = V | 看板比對 | DONE
```
