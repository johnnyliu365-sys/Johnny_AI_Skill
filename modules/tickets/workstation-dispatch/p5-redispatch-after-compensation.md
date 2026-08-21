# P5｜補償之後沒有重派的路

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（P4 接線路徑首次實車試駕的直接發現） |
| 第一步排查起點 | `library/local_orchestration/live_dispatch_metadata_boundary.py` 的 `_receipt_key`（(project, ticket) 一票一收據）與 line 485 附近（lifecycle 只有讀取端） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/p5`／branch `implement/p5-redispatch` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | worktree HEAD（派工訊息載明） |
| 實作者 | Opus 5（難票，依 `dispatch-model-profile.md` 先派 Opus） |
| 審閱者 | 控制面（Opus 5）；與實作者不同 worktree |
| 責任邊界 | 見邊界宣告；設計決定落點，但每個落點都要在宣告內 |
| 禁止修改 | `document_mutation_gate.py`、`work_queue.py`、任何既有票 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/dispatch_session.py
modify = library/local_orchestration/dispatch_authority.py
modify = library/local_orchestration/live_dispatch_metadata_boundary.py
modify = library/local_orchestration/worker_assignment.py
modify = tests/test_dispatch_session.py
modify = tests/test_dispatch_authority.py
modify = tests/test_live_dispatch_metadata_boundary.py
modify = tests/test_worker_assignment.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/work_queue.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

spawn 失敗被補償之後，同一張票**可以再次派出**，且過程不削弱恰好一次：
任何時刻同一張票仍然至多一個活的 claim。

## 實車證據（2026-08-21，JohnnyRouter dispatch-journal 實錄）

governance 15 首次走接線路徑，driver 的 spawn port 有 bug（AttributeError）：

| 時刻 | receipt | 結果 |
| --- | --- | --- |
| 13:15:12 | 001 | `DISPATCHED` → spawn 失敗 → 補償 settle（fail-closed 正確運作） |
| 13:15:39 | 001 | admission **冪等收斂**再次 `DISPATCHED`，然後 `CLAIM_REFUSED`——claim 已結清 |
| 13:15:58 | 002（同 handoff） | `RECEIPT_CONFLICT` |
| 13:17:01 | 002（**新** handoff，新身分） | `RECEIPT_CONFLICT`——receipt 鍵是 (project, ticket)，身分換了也沒用 |

三個事實相乘：receipt 鍵＝一票一收據；claim 結清後不得再 claim；
**lifecycle（REVOKED／CLOSED）只有讀取端在用，沒有任何 API 能轉換它**。
所以一次 spawn 失敗＝這張票永久退出接線路徑。補償關帳關得對，但沒有人能重開帳。

## 設計要求（落點由實作者決定，性質不可讓）

1. **必須存在一條具名的重派路**：補償後的票能拿到新的可 claim 狀態。
   一個候選形狀：補償時（或經明確入口）把舊 receipt 轉入終態（如 `REVOKED`），
   終態 receipt 不再佔用 (project, ticket) 鍵，新 receipt 可發。是否採用由實作者論證。
2. **恰好一次不得削弱**：同一張票任何時刻至多一個 `ACTIVE` receipt、至多一個未結清
   claim。重派路不得變成雙派工的門。
3. **每一步具名**：重開帳是顯著動作，journal 要留痕（誰、何時、原 receipt、新 receipt）。
4. **正常路徑不動**：現有 27＋ 個 dispatch_session cell 與四個上游模組的既有測試不受影響。

## TDD 設計

1. 正常行為：dispatch → spawn 失敗 → 補償 → 重派 → 新 receipt 新 claim → 正常回傳入列。
2. 規則違反／輸入錯誤：對**未補償**（claim 還開著）的票走重派路 → 具名拒絕。
3. 外部失敗／fail-closed：重派中途失敗不得留下「舊帳已關、新帳未開」以外的中間態；
   任何中間態都要可讀、可續傳或可具名拒絕。
4. 回歸保護：跨行程並行重派同一張票，恰好一個成功（真行程，比照 P1／P2 前例）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | 無此 receipt、無此 claim、空 journal 三者各自具名 |
| 3 | 權限繞過 | **是** | 重派路不得繞過 grant；不得讓一般呼叫端直接改 lifecycle |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 「claim 還開著」「receipt 已終態」「儲存失敗」各自可區分 |
| 6 | 例外是否會拋出 | 是 | 每個儲存失敗路徑 fail-closed |

## 完成定義與證據

- 完整往返在真 store 上重演本票「實車證據」的四步，第四步改為成功重派。
- **反向突變證據**：至少三組——重派路對開著的 claim 放行、終態 receipt 仍佔鍵、
  補償後直接二次 claim 成功；各指名哪個測試轉紅、還原後轉綠。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- 全程 `pytest==9.1.1`、venv 建在 repo 外 ASCII 路徑。

## 不在本票範圍

孤兒 receipt 的逾時政策（無計時器原則不變）；host 端 spawn 的可靠性。

## 正式環境移植 SOP

不適用（本機記帳；lifecycle 若加欄位，store 的 schema_revision 遞增由實作者依既有慣例處理並在測試釘住）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = P5
title = 補償之後沒有重派的路
state = IN_PROGRESS
stage = D | 設計與重派路 | OPEN
stage = X | 恰好一次保全 | OPEN
stage = M | 突變驗證 | OPEN
```
