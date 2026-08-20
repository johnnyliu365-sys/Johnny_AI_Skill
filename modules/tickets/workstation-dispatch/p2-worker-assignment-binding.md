# P2｜工人與 receipt 的綁定

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（Router 記帳能力；上游為 P1 已證明的並行發放） |
| 第一步排查起點 | `library/local_orchestration/dispatch_authority.py`（發放端，本票的上游） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/p2`／branch `implement/p2-worker-binding` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 新增 `library/local_orchestration/worker_assignment.py` 與其測試 |
| 禁止修改 | `dispatch_authority.py`、`document_mutation_gate.py`、`ticket_status_pipeline.py`、任何既有票 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/worker_assignment.py
modify = tests/test_worker_assignment.py
create = library/local_orchestration/worker_assignment.py
create = tests/test_worker_assignment.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/ticket_status_pipeline.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

「哪張票在誰手上」是**持久的事實**，不是控制面記在對話裡的東西。一個工人不見了，
會以孤兒的形式**浮出來**，而不是無聲消失。

## 現在的斷點

Router 知道 receipt 發給了某個 owner id，但**不知道那個 id 對應的工人存不存在**。
2026-08-21 的實例：一個 session 死了一小時，控制面完全不知道——那份對應關係只存在
於對話裡，對話一斷就沒了。

## 分工不變：Router 不知道「子代理」是什麼

owner 的路線是通用的（Codex 也有子代理）。**本模組不得出現 subagent、claude、codex
等 host 名詞**，比照 `dispatch_authority` 由測試守住。工人怎麼生是 host 的事；
本模組只記「某張 receipt、某個 worktree、某個分支、某個不透明的工人參照」。

## 設計約束

**不得輪詢、不得心跳、不得計時器。** 本專案已明文禁止，而且理由成立：心跳會把
「還活著」變成一個需要持續花費的宣稱。

因此存活性用**宣告＋結算**表達，與既有的 wake attempt 同形狀：派工時 claim，
工人回來時 settle。孤兒的定義是「claim 了但從未 settle」，而且它**在有人讀取時才被
發現**，不由計時器發現。

`receipt-bound-role-supervision` 已有 lease 的既有語彙，先讀它再決定要不要沿用。

## TDD 設計

1. 正常行為：claim 一筆指派後讀得回來，欄位與 claim 時一致。
2. 規則違反／輸入錯誤：同一張 receipt claim 兩次 → 具名拒絕（一張票不得同時在兩個
   工人手上，這是整條線的核心性質）。
3. 外部失敗／fail-closed：儲存讀不到、記錄壞掉 → 拒絕並具名，**不得當成「沒有指派」**。
   不知道有沒有人在做，不等於沒有人在做。
4. 回歸保護：`admit_dispatch` 的既有行為與測試不受影響；本模組不得取得發放能力。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | worktree 路徑比對：相等、多一字元、尾斜線、大小寫、路徑遍歷、空路徑 |
| 2 | null／空字串／陣列 | 是 | 無指派、空 receipt id、空工人參照三者行為各自明確 |
| 3 | 權限繞過 | 是 | 本模組不得能發 receipt；以命名空間斷言證明（型別身分，不是字串比對） |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 重複 claim、儲存失敗、結算不符各自具名 |
| 6 | 例外是否會拋出 | 是 | 每個儲存失敗路徑都 fail-closed |

## 完成定義與證據

- 跨行程的重複 claim 恰好一次成立（**真行程，不是執行緒**——本專案有前例：
  執行緒共用檔案 handle，會在真行程互撞時仍然通過）。
- 孤兒（claim 未 settle）讀得出來，並帶得出是哪張 receipt、哪個 worktree。
- **反向突變證據**：至少三組——拿掉重複 claim 的檢查、把儲存失敗改成回傳空、
  讓 settle 不比對 receipt；各指名哪個測試轉紅、還原後轉綠。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。

## 正式環境移植 SOP

不適用（本機記帳，無 migration 或部署影響）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = P2
title = 工人與 receipt 的綁定
state = IN_PROGRESS
stage = C | claim／settle | OPEN
stage = O | 孤兒可見 | OPEN
stage = M | 突變驗證 | OPEN
```
