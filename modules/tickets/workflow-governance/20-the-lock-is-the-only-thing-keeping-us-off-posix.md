# 20｜把鎖換成跨平台，其餘一行不動

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（可攜性；公開後半數讀者裝不了是缺陷不是取捨） |
| 第一步排查起點 | `library/local_orchestration/file_lock.py`（65 行，整個 Windows 綁定就在這裡） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-20`／branch `implement/gov-20-portable-lock` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `cc9deda`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Opus 5（難票：換掉恰好一次的地基原語，依 `dispatch-model-profile.md` 先派 Opus） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `library/local_orchestration/file_lock.py` 與其測試 |
| 禁止修改 | **六個消費者一行都不准動**：`live_dispatch_metadata_boundary.py`、`review_return.py`、`review_return_consumption.py`、`windows_senior_review_inbox_store.py`、`worker_assignment.py`、`work_queue.py` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/file_lock.py
modify = tests/test_file_lock.py
create = tests/test_file_lock.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/live_dispatch_metadata_boundary.py
forbid = library/local_orchestration/review_return.py
forbid = library/local_orchestration/review_return_consumption.py
forbid = library/local_orchestration/windows_senior_review_inbox_store.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

同一份程式碼在 Windows 與 POSIX 上都取得**作業系統層級可見的互斥鎖**，
六個既有消費者一行不改，跨行程恰好一次的既有證據在兩個平台上都成立。

## 為什麼範圍這麼小

實測（2026-08-22）：整個 runtime 的 Windows 綁定只有兩處，而且**已經被介面隔離好了**：

| 綁定 | 範圍 |
| --- | --- |
| `ExclusiveWindowsFileLock` | **65 行、一個檔案**，用 stdlib `msvcrt`。六個模組 import 它，但全部透過同一個 class |
| `pywin32` | **一個檔案**（`windows_native_git_ref.py`，原生 ref watch）——**不在本票範圍**，見票 21 |

本票只換那 65 行的內部實作。這是當初 W5 把兩份私有複本合併成一份時就付好的代價——
那張票的 docstring 寫著「互斥原語的第二份實作，就是細微歧異被重新引入的方式」，
今天正好讓可攜性變成一個檔案的事。

## 不可讓的性質

現有 docstring 已經寫死了這把鎖的契約，換實作**不得改變其中任何一條**：

1. **OS 層級可見**——不是行程內的 threading 鎖。跨行程互斥是整個恰好一次的地基。
2. **阻塞式**——取不到就等，不是取不到就失敗。
3. **關檔即釋放**——異常終止的持有者不得把鎖卡死。
4. **advisory between cooperating processes**——語義不變。

POSIX 側用 `fcntl.flock`（或 `lockf`，由實作者論證取捨並寫下理由），Windows 側維持
`msvcrt`。平台選擇在 import 時決定，**不得在每次取鎖時分支**。

## 命名

`ExclusiveWindowsFileLock` 這個名字在跨平台之後就是謊。改名會動到六個消費者的 import
（本票禁止）。**解法：新名字為正名，舊名字保留為別名**，並用測試釘住兩者是同一個物件
（`is` 斷言，不是字串比對）。改 import 是另一張票的事。

## TDD 設計

1. 正常行為：兩個真行程競爭同一把鎖，恰好一個進入臨界區（比照既有跨行程 cell 的起跑閘門）。
2. 規則違反／輸入錯誤：鎖檔路徑不存在的目錄 → 具名失敗，不得無聲成功。
3. 外部失敗／fail-closed：持有者被強制終止 → 鎖必須可被下一個取得（關檔即釋放）。
4. 回歸保護：`test_worker_assignment.py`、`test_work_queue.py`、`test_dispatch_session.py`
   的既有跨行程 cell **完全不改**且維持綠——它們是這把鎖的真正驗收，本票的新測試是補充。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | 空路徑、不存在的父目錄各自具名 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | **是** | 取鎖失敗、釋放失敗、異常終止三條路徑的行為都不得改變 |

## 完成定義與證據

- **反向突變證據**：至少三組——把 OS 鎖換成行程內 threading 鎖（跨行程 cell 必須轉紅）、
  把阻塞改成非阻塞立即失敗、讓釋放不發生；各指名哪個測試轉紅、還原後轉綠。
  **第一組是本票的核心**：如果換成 threading 鎖而跨行程測試不紅，代表那些測試從一開始
  就沒有鑑別力，那比可攜性更嚴重，要立刻回報。
- **平台限制的誠實聲明**：本票只讓鎖可攜。實作者**不得**宣稱 runtime 已可在 POSIX 執行
  ——`windows_native_git_ref.py` 仍是 Windows-only（票 21）。回報時要說清楚剩下什麼。
- 實作者只跑邊界內測試檔＋上述三個既有跨行程測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

- **全套件責任**：多張票並行實作，實作者只跑本票指定的測試檔；全套件與殘留檢查由審閱者於整合前執行（比照 governance 11 的責任轉移，這是審閱者的未完成義務，不得因實作者回報綠即視為滿足）。

## 不在本票範圍

`pywin32` 與原生 ref watch（票 21）；六個消費者的 import 改名；
在真的 Linux／macOS 機器上執行驗證（本機沒有那些平台，**平台分支的正確性由測試與
程式碼審閱擔保，不得宣稱已在 POSIX 實機驗過**）。

## 正式環境移植 SOP

不適用（本機原語；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 20
title = 把鎖換成跨平台，其餘一行不動
state = IN_PROGRESS
stage = P | 平台分支實作 | OPEN
stage = C | 契約四條不變 | OPEN
stage = M | 突變驗證 | OPEN
```
