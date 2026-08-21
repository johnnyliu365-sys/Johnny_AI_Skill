# P7｜commit 事件到佇列之間沒有線

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（P6 實機功能驗證第三段的直接發現） |
| 第一步排查起點 | `library/local_orchestration/event_runner.py`（訊號 callback 在這裡）與 `work_queue.py:284`（現成的 `COMMIT_TRIGGER` 建構子在這裡）——兩者之間零引用 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/p7`／branch `implement/p7-commit-trigger-wire` |
| 實作語言 | Python 3.11 |
| 狀態 | `DONE` |
| 共同基準 | 綁定 commit（worktree HEAD，派工訊息載明） |
| 實作者 | Opus 5（難票：訊號 callback 語境＋跨兩份契約，依 `dispatch-model-profile.md` 先派 Opus） |
| 審閱者 | 控制面（Opus 5）；與實作者不同 worktree |
| 責任邊界 | 見邊界宣告；落點（改 runner 或新增黏合模組）由實作者論證 |
| 禁止修改 | `work_queue.py`、`dispatch_session.py`、`worker_assignment.py`、`dispatch_authority.py`、`document_mutation_gate.py` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/event_runner.py
modify = library/local_orchestration/commit_trigger_intake.py
create = library/local_orchestration/commit_trigger_intake.py
modify = tests/test_event_runner.py
modify = tests/test_event_runner_cli.py
modify = tests/test_commit_trigger_intake.py
create = tests/test_commit_trigger_intake.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/dispatch_session.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

真 commit 落在被訂閱的 ref 上時，佇列裡**出現一筆 `COMMIT_TRIGGER` 項目**，
`origin_ref` 指著那個 commit。Router 的第三隻腳從此有腳掌。

## P6 第三段的發現（2026-08-21）

- `WorkSource.COMMIT_TRIGGER` 在整個 library **沒有任何生產者**——只有 `work_queue`
  （收）與 `dispatch_session`（正確擱置）認識它。
- `event_runner` 的產品是**喚醒**（或誠實記錄 completion candidate），與 work queue
  之間**零引用**。
- `work_queue.py:284` 有現成的 commit-trigger 建構子（`source=COMMIT_TRIGGER`,
  `origin_ref=commit_ref`）——P3 把插座裝好了，沒有人插線。

P6 依自己的規則停下開票，**沒有**手動假造入列宣稱通過。

## 設計約束（落點由實作者論證，性質不可讓）

1. **不得輪詢**。runner 已有原生 exact-ref watch 的訊號 callback，線接在那裡，
   不新增任何計時器或掃描。
2. **入列失敗必須浮出**。commit 事件是真實發生的事，enqueue 失敗不得無聲消失——
   比照 runner 對喚醒失敗的誠實規則（記錄而非宣稱）。callback 語境內不得讓例外
   毀掉 runner 本體。
3. **佇列讀不到 ≠ 佇列是空的**（C 族），入列端同樣適用。
4. **host-agnostic**：不得出現 host 名詞（比照 `dispatch_authority` 由測試守住）。
5. **喚醒路徑不受影響**：runner 原本要做的事一件不少。

## TDD 設計

1. 正常行為：一次訊號 → 恰好一筆 `COMMIT_TRIGGER` 項目，`origin_ref`＝該 commit。
2. 規則違反／輸入錯誤：同一 commit 的重複訊號 → 依 `work_queue` 既有契約收斂或具名拒絕，
   不得產生兩筆。
3. 外部失敗／fail-closed：enqueue 失敗（儲存不可用）→ 具名記錄、runner 存活、
   喚醒路徑照走。
4. 回歸保護：runner 的既有測試與喚醒行為不變；掃原始碼斷言無 host 名詞、無計時器。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | ref 比對沿用 runner 既有的 exact-ref 機制，不新增 |
| 2 | null／空字串／陣列 | 是 | 空 commit ref、空訂閱、佇列空與讀取失敗可區分 |
| 3 | 權限繞過 | 否 | 入列不是特權動作；閘門仍在消費端 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 入列失敗、重複訊號、儲存不可用各自具名 |
| 6 | 例外是否會拋出 | **是** | callback 內的失敗不得毀掉 runner，也不得無聲吞掉 |

## 完成定義與證據

- **反向突變證據**：至少三組——拿掉入列呼叫（訊號不再產生項目）、讓入列失敗無聲消失、
  讓重複訊號產生兩筆；各指名哪個測試轉紅、還原後轉綠。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。
- **本票整合後，P6 第三段用它在實機上收尾**——真訂閱、真 commit、真入列，
  證據補進 `doc/runbooks/live-verification-047.md`。

## 不在本票範圍

commit-trigger 項目被拉到之後的處理政策（P6 也明文排除）；runner 的啟動／佈署方式。

## 正式環境移植 SOP

不適用（本機協調；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：`library/local_orchestration/commit_trigger_intake.py`（新增）、`event_runner.py`、`tests/test_commit_trigger_intake.py`（新增）
- commit：`ae514a8`，經 `admit_document_mutation` 判為 `INTEGRATED`
- **接點**：包住 supervision controller 交給 native factory 的 sink（tee），不開第二個 watch。**順序是決定**：controller 先、intake 後、不看 intake 結果——佇列問題永不延遲或吃掉喚醒；controller 自己的例外照舊上傳（吞掉會蓋住 supervision fault）
- **callback 全域契約**：`on_signal` total；失敗各自具名（`SIGNAL_INVALID`／`COMMIT_ABSENT`／`COMMIT_UNREADABLE`／`ENQUEUE_REFUSED` 帶佇列自己的原因／`INTAKE_FAULTED`），durable 記錄於 `commit-trigger-failures.jsonl`；連記錄都寫不進去的極限在 docstring 具名
- **重複收斂**：一個 commit 一個 origin，交給佇列的 `ORIGIN_ALREADY_QUEUED` 拒絕；**刻意不設「看過的 commit」備忘錄**——同一個問題的第二個答案終究會不一致。native watch 本來就會為一次更新觸發多次（loose ref 與 packed-refs），重複是常態
- **反向突變**：實作者三組（拿掉入列 → 7 紅＋1 SUBFAILED；失敗無聲 → 2 紅，設計使然——生產路徑沒人讀回傳值，記錄斷言正是這個 bug 的真實形狀；重複雙筆 → 7 紅）。審閱者從另一道門：**把 tee 反轉成 intake 先、喚醒只在 intake 成功後**——`test_supervision_sees_the_signal_before_the_queue_does` 恰好指名轉紅，還原後 44 綠。順序性質有被釘住
- **控制面的邊界錯誤（第三次）**：票宣告了不存在的 `tests/test_event_runner.py`。實作者未創建、未越界，把 runner 接線 cell 放進自己的測試檔並回報。無害（閘門不管未使用的宣告），記錄在案
- 全套件（受閘測試開啟）：1432 passed、1 skipped、3278 subtests、零 FAILED、無殘留
- **本 commit 本身就是第三段的實機觸發**：runner（pid 44908，repo 程式碼，armed 於 `refs/heads/main`）正在看著這次 ff——它入列的那筆 `COMMIT_TRIGGER` 就是 P6 第三段的證據

```johnny-status
id = P7
title = commit 事件到佇列之間沒有線
state = DONE
stage = W | 接線 | DONE
stage = H | 誠實失敗 | DONE
stage = M | 突變驗證 | DONE
```
