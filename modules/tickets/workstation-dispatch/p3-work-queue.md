# P3｜排程佇列

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（Router 排程能力；上游為 P2 已完成的工人綁定） |
| 第一步排查起點 | `library/local_orchestration/worker_assignment.py`（claim／settle 的既有形狀） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/p3`／branch `implement/p3-work-queue` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 新增 `library/local_orchestration/work_queue.py` 與其測試 |
| 禁止修改 | `worker_assignment.py`、`dispatch_authority.py`、`document_mutation_gate.py`、`event_runner.py`、任何既有票 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/work_queue.py
modify = tests/test_work_queue.py
create = library/local_orchestration/work_queue.py
create = tests/test_work_queue.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/event_runner.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

子代理回傳、或 commit 觸發成立時，該做的下一件事**落到持久佇列上**。主 session 手上
的工作做完之後，向佇列要下一件，接著做。回傳不會因為當下有人在忙而消失。

## owner 定的模型：拉取，不是推送

Router 是**帳本＋commit 觸發＋工作排程器**。工人由 host 生（子代理），回傳結構性地
回到派工者手上。

**主 session 忙碌時不中斷它**，回傳先落到佇列；session 做完當下的工作再向佇列拿下一件。
因此本模組**不需要偵測 session 忙不忙**，也不需要中斷機制——消費者在自然邊界主動拉取。

這也是為什麼它不違反禁止輪詢：拉取發生在「一件工作結束」這個事件上，不是計時器上。

## 這條規則決定成敗

**佇列讀不到，不等於佇列是空的。**

讀取失敗必須以具名拒絕回傳，**絕不得回傳「沒有待辦」**。一個把讀取失敗折疊成空佇列的
實作，會讓主 session 安靜地停止工作，而且沒有任何訊號——這是本專案登記簿 C 族在排程器
上的形狀，比其他任何缺陷都貴。

## TDD 設計

1. 正常行為：入列一件、拉取拿到它，欄位與入列時一致。
2. 規則違反／輸入錯誤：同一件被兩個拉取者同時拉 → 只有一個拿到，另一個拿到具名結果
   （不是同一件的複本）。**跨行程，真行程不是執行緒**。
3. 外部失敗／fail-closed：儲存讀不到、記錄壞掉 → 具名拒絕，**不得回傳空佇列**。
4. 回歸保護：`worker_assignment` 的既有行為不受影響；本模組不得取得 claim 指派或發
   receipt 的能力。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | **是** | 空佇列、空 id、空來源三者行為各自明確；且**空佇列與讀取失敗必須是可區分的兩個結果** |
| 3 | 權限繞過 | 是 | 本模組不得能發 receipt 或 claim 指派；以命名空間斷言證明 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 讀取失敗、重複拉取、來源不明各自具名 |
| 6 | 例外是否會拋出 | 是 | 每個儲存失敗路徑都 fail-closed |

## 完成定義與證據

- 兩種入列來源都成立：工人回傳（已 settle 的指派）與 commit 觸發。
- 跨行程拉取恰好一次（**真行程＋起跑閘門**——本專案有前例：子行程各自載入完才開始
  動作，時間差遠大於被保護的窗口，會讓沒有鎖的實作也通過）。
- 順序是**明確宣告的**，不是「剛好是檔案順序」。選什麼順序由實作者決定，但要寫下來
  並用測試釘住。
- **反向突變證據**：至少三組——拿掉跨行程鎖、把讀取失敗改成回傳空佇列、拿掉順序保證；
  各指名哪個測試轉紅、還原後轉綠。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。

## 不在本票範圍

把佇列接到實際的子代理派工與整合流程（接線），以及 commit 觸發的實機驗證。
本票只做佇列本身。

## 正式環境移植 SOP

不適用（本機記帳，無 migration 或部署影響）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = P3
title = 排程佇列
state = IN_PROGRESS
stage = Q | 佇列 | OPEN
stage = X | 跨行程恰好一次 | OPEN
stage = M | 突變驗證 | OPEN
```
