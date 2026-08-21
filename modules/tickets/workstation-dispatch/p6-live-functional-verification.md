# P6｜實機功能驗證：三隻腳合起來走一遍

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（owner 拍板：POC 完成，發行前先驗證功能） |
| 第一步排查起點 | `C:\Users\User\AppData\Local\JohnnyRouter\queue\dispatch-journal.jsonl`（gov-15 試車的實錄，本票接著它往下走） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/p6`／branch `implement/p6-live-verification` |
| 實作語言 | Python 3.11（driver 腳本與 worker 交付物） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | 綁定 commit（worktree HEAD，派工訊息載明） |
| 實作者 | 分工特殊：**driver＝控制面**（派工與整合本來就是控制面的動作，也正是被驗的對象）；**worker＝Sonnet 5**（收到真派工、交真交付物） |
| 審閱者 | 控制面（Opus 5）＋ **owner**（本票的證據是 journal 實錄，owner 可自行核對） |
| 責任邊界 | 新增 `doc/runbooks/live-verification-047.md`（worker 的交付物＝驗證紀錄本身）；真 store 的 journal 條目 |
| 禁止修改 | `library/` 下任何產品程式碼——**驗證中發現缺陷一律開新票，不得在本票內修** |
| 環境 | `LOCAL`（真 JohnnyRouter store，非測試暫存） |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = doc/runbooks/live-verification-047.md
create = doc/runbooks/live-verification-047.md
forbid = library/
forbid = tests/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

Router 的三隻腳（帳本、排程器、commit 觸發）在**真安裝的 store** 上合起來完成一件真工作，
全程**沒有任何一步由控制面手動代勞**。owner 打開 journal 就能逐行對照。

## 為什麼需要這張票

零件各自全綠，但「功能」是零件合起來在真機上做成一件事。目前的真機紀錄：

- **派工前半**：gov-15 試車走過 grant → admit → claim → spawn 失敗 → 補償（真的）。
- **P5 重派路**：只在測試 store 上證過，**真 store 上那張被 brick 的 receipt 至今還躺著**。
- **回傳後半**：`record_worker_return` → `integrate_next_work` → 閘門整合，
  **在真 store 上一次都沒發生過**——gov-15 到 17 全部是控制面手動呼叫閘門。
- **commit 觸發**：從未在實機上發生。

## 三段驗證（順序即依賴）

### 第一段：計畫性失敗演練（P5 實機）

用本票自己的 receipt，**故意**先用會失敗的 spawn port 派一次：
admit → claim → spawn 失敗 → 補償 settle。然後走 `redispatch_worker`：
撤銷 → 新 receipt → 新 claim → 真 spawn。這重演 gov-15 被 brick 的完整路徑，
但這次有路回來。journal 應出現 `REVOCATION_*` 條目與 `superseded_by_receipt_id`。

### 第二段：完整往返（排程器實機）

第一段的真 spawn 生出真 worker（Sonnet 5），交付物是驗證紀錄檔本身。
worker 回報後：`record_worker_return`（settle ＋ 入列）→ 控制面審閱 → worker 的
branch 就緒 → `integrate_next_work` 拉取並**由它經閘門完成真的整合**。
**控制面不得手動 merge、不得手動組 DocumentMutationRequest**——那正是要驗的。

### 第三段：commit 觸發（實機首次）

用既有的 `runner subscribe` CLI（E13）對本 repo arm 一個訂閱，落一個真 commit，
觀察它以 `COMMIT_TRIGGER` 來源進入佇列、且消費端正確回報 `COMMIT_TRIGGER_PENDING`
不取走。這一段只驗「觸發 → 入列 → 具名擱置」，commit 觸發的後續處理政策不在本票範圍。

## TDD 設計

本票不寫新測試（`forbid = tests/`）——它的證據是 journal 與 store 的實際狀態：

1. 正常行為：三段各自的 journal 條目齊全，owner 可逐行核對。
2. 規則違反／輸入錯誤：第一段的失敗演練必須真的失敗、真的補償（不得跳過演練直接派成功）。
3. 外部失敗／fail-closed：任何一段卡住 → 停下、記錄、開新票；不得手動代勞後宣稱通過。
4. 回歸保護：驗證結束後真 store 無孤兒 claim、無 `PENDING` 殘留、
   佇列裡只剩第三段刻意留下的 `COMMIT_TRIGGER` 項目（它就是證據，含處理政策的新票開出前不清）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不新增路徑判斷 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | **是** | 全程走 grant 與閘門；控制面手動代勞任何一步即視為本票失敗 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 演練段的每個失敗都必須以具名代碼出現在 journal |
| 6 | 例外是否會拋出 | 否 | 不改產品程式碼 |

## 完成定義與證據

- `doc/runbooks/live-verification-047.md` 記錄三段的完整 journal 摘錄與時刻，
  以及「哪一步是誰做的」的清單——**控制面代勞清單必須為空**。
- 真 store 事後狀態：恰好一個 `REVOKED` receipt（演練的）、一個 `ACTIVE` 或已結清的
  後繼、無孤兒、佇列僅剩第三段的觸發項目。
- 發現的任何缺陷各自開票，編號記入 runbook。
- **本票通過後才有 0.4.8**——驗證是發行的前置條件（owner 拍板的順序）。

## 不在本票範圍

commit 觸發項目的後續處理政策（拉到之後做什麼——另票）；
gov-15 那張舊的 brick receipt（historical record，留在 journal 作為 P5 的緣起，不清理）。

## 正式環境移植 SOP

不適用（驗證動作；真 store 的變更即證據，隨 journal 留存）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = P6
title = 實機功能驗證：三隻腳合起來走一遍
state = IN_PROGRESS
stage = A | 失敗演練＋重派（P5 實機） | DONE
stage = B | 完整往返（排程器實機） | DONE
stage = C | commit 觸發（BLOCKED，等 P7 接線） | OPEN
```
