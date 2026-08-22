# 23｜會放棄的阻塞鎖會弄丟工作

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（實測缺陷；票 20 的實作者已誠實標示此不對稱，審閱者讀過而未追） |
| 第一步排查起點 | `library/local_orchestration/file_lock.py` 的 Windows 分支（`msvcrt.LK_LOCK` 的有界重試）與 `work_queue.py` 的 `except (OSError, ValidationError, ValueError)` |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `file_lock.py` 的等待語義與其測試；受影響消費者的失敗分流 |
| 禁止修改 | 鎖的**互斥**語義（票 20 剛釘住的四條契約中的其餘三條） |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/file_lock.py
modify = library/local_orchestration/work_queue.py
modify = library/local_orchestration/worker_assignment.py
modify = tests/test_file_lock.py
modify = tests/test_work_queue.py
modify = tests/test_worker_assignment.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/control_plane_mutation.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

一個合法的等待者**不會因為等太久而弄丟它的工作**。若真的等不到，
使用者拿到的是一個說出「這是競爭」的具名結果，而不是一個看起來像磁碟壞掉的字。

## 實測證據（2026-08-22，全套件執行中）

`test_work_queue.py::CrossProcessPullTests::test_four_processes_enqueueing_at_once_lose_no_return`

```
AssertionError: 'REFUSED' != 'ENQUEUED'
[{'status': 'ENQUEUED', 'origin_ref': 'claim-aaa', 'sequence': 2},
 {'status': 'REFUSED', 'failure': 'STORAGE_UNAVAILABLE', 'origin_ref': None},
 {'status': 'ENQUEUED', 'origin_ref': 'claim-ccc', 'sequence': 3},
 {'status': 'ENQUEUED', 'origin_ref': 'claim-ddd', 'sequence': 1}]

AssertionError: every concurrent return must survive:
['claim-aaa', 'claim-ccc', 'claim-ddd'] != ['claim-aaa', 'claim-bbb', 'claim-ccc', 'claim-ddd']
```

**`claim-bbb` 的工作真的不見了。** 那不是測試瑕疵——佇列的核心承諾就是「並行回傳不會因為
當下有人在忙而消失」。

**重現性**：全套件中出現一次；事後在 main 與候選 worktree 上單獨連跑該 cell 共 **8 次全綠**。
只在整套件執行、機器負載高時出現。

## 診斷（待實作者驗證，不得直接採信）

`msvcrt.locking(..., LK_LOCK, 1)` 是**有界**重試（CPython 行為：約 10 次、每次約 1 秒），
耗盡後拋 `OSError`。該 `OSError` 落進消費者既有的 `except (OSError, ValidationError, ValueError)`
而被折成 `STORAGE_UNAVAILABLE`。

於是「我等不到鎖」與「磁碟讀不到」共用同一個名字——**這正是 governance 16 修過的那一族，
在鎖上再現一次**。而 16 只分流了不變式違反，沒有分流競爭。

**票 20 的實作者已經寫下這個不對稱**（「Windows 阻塞約 10 秒後拋出，POSIX `LOCK_EX`
無限期阻塞……兩者都是『等待而非快速失敗』」），並判定改動任一側會變更該票不得觸碰的契約。
那個判斷在當時是對的。**是審閱者讀過那段話而沒有追下去**——本票是那個疏漏的補救。

## 要達成的事（落點由實作者論證）

1. **等待不得有界，或界限不得等於丟工作。** 兩條路徑各有代價，實作者論證後擇一並寫下理由：
   - 讓 Windows 側也無限期等待（與 POSIX 對齊；代價是真死鎖時會永久卡住）
   - 保留界限，但耗盡時回傳**具名的競爭失敗**而非 `STORAGE_UNAVAILABLE`，且呼叫端據此重試
2. **競爭與儲存失敗必須可區分。** 不論選哪條路，「等不到鎖」不得再與「磁碟壞掉」同名。
3. **票 20 釘住的其餘三條契約不變**：OS 層級可見、關檔即釋放、advisory。

## TDD 設計

1. 正常行為：無競爭時取鎖行為不變。
2. 規則違反／輸入錯誤：不適用（無外部輸入）。
3. 外部失敗／fail-closed：**強制耗盡等待預算**（人為長時間持有），斷言結果是具名的競爭
   失敗或成功取得，**永不是工作消失**。
4. 回歸保護：票 20 的 `PosixBranchSourceGuardTests` 與四條契約測試全部不變且維持綠；
   跨行程恰好一次的既有 cell 不得被削弱。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | **是** | 競爭耗盡與儲存失敗必須是兩個可區分的名字，這就是本票 |
| 6 | 例外是否會拋出 | **是** | 等待耗盡不得以工作消失收場 |

## 完成定義與證據

- **反向突變證據**：至少三組——把競爭失敗折回 `STORAGE_UNAVAILABLE`、讓等待耗盡靜默丟棄
  工作、把新的等待語義改回有界且無具名結果；各指名哪個測試轉紅、還原後轉綠。
- **必須有一個確定性重現該缺陷的 cell**——不得依賴機器負載。人為持有鎖超過預算即可。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

真死鎖的偵測與逾時政策（那需要計時器，本專案明文禁止——若選擇無限期等待，
「卡住」的處理屬另一個設計問題）；POSIX 側的實機驗證。

## 正式環境移植 SOP

不適用（本機原語；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 23
title = 會放棄的阻塞鎖會弄丟工作
state = IN_PROGRESS
stage = D | 確定性重現 | OPEN
stage = F | 等待語義與具名競爭 | OPEN
stage = M | 突變驗證 | OPEN
```
