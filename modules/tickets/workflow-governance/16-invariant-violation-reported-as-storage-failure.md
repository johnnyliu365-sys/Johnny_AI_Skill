# 16｜不變式違反被報成儲存問題

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（P5 審閱時的旁生髮現；缺陷屬 P2 既有程式碼） |
| 第一步排查起點 | `library/local_orchestration/worker_assignment.py` 的 `except (OSError, ValidationError, ValueError)` 各處 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-16`／branch `implement/gov-16-named-invariant-failure` |
| 實作語言 | Python 3.11 |
| 狀態 | `DONE` |
| 共同基準 | `9125a91`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Sonnet 5 high（一般小票，依 `dispatch-model-profile.md` 分層） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `worker_assignment.py` 與 `work_queue.py` 的例外分流與失敗碼 |
| 禁止修改 | `dispatch_authority.py`、`dispatch_session.py`、`document_mutation_gate.py`、`live_dispatch_metadata_boundary.py` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/worker_assignment.py
modify = library/local_orchestration/work_queue.py
modify = tests/test_worker_assignment.py
modify = tests/test_work_queue.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/dispatch_session.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/live_dispatch_metadata_boundary.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

帳本自己的不變式被違反時，回報的名字**說的是不變式**，不是「儲存壞了」。
去查磁碟的人不會白查一輪。

## 實測到的事實（2026-08-21，P5 審閱期間）

審閱者為了驗 P5 的恰好一次，把 `claim_worker_assignment` 的重複檢查改成只擋 `CLAIMED`。
預期是看到 `RECEIPT_ALREADY_CLAIMED` 消失，實際看到的是：

```
AssertionError: 'STORAGE_UNAVAILABLE' != 'RECEIPT_ALREADY_CLAIMED'
```

追下去發現**第二道防線存在而且有效**：`_AssignmentLedger.identities_are_unique`
這個 model validator 會拋 `ValueError("a receipt may appear at most once in the ledger")`，
寫入因此失敗、恰好一次仍然成立。**防禦縱深是真的。**

問題在名字：那個 `ValueError` 被

```python
except (OSError, ValidationError, ValueError):
    return WorkerClaimResult.refused(WorkerClaimFailure.STORAGE_UNAVAILABLE)
```

接住，於是「帳本的不變式被違反」與「磁碟讀不到」共用同一個名字。

## 為什麼值得修

`STORAGE_UNAVAILABLE` 會把讀到它的人送去查磁碟、查權限、查鎖——一個不存在的方向。
而真正發生的是程式邏輯違反了帳本自己宣告的不變式，那是**程式缺陷，不是環境問題**，
兩者該做的事完全相反。

這也是登記簿 C 族的近親：C 族是「壞事被報成好事」，這裡是「壞事被報成**另一種**壞事」，
一樣讓下一個人往錯的方向走。

## TDD 設計

1. 正常行為：真正的儲存失敗（`OSError`）仍然回報 `STORAGE_UNAVAILABLE`。
2. 規則違反／輸入錯誤：不變式違反（validator 拋出）回報**新的具名失敗**，
   與 `STORAGE_UNAVAILABLE` 可區分。
3. 外部失敗／fail-closed：兩者都仍然 fail-closed——不得因為分流而讓任何一邊變成成功。
4. 回歸保護：`work_queue.py` 有同形狀的 except 分流，一併檢查；
   既有的 `RECEIPT_ALREADY_CLAIMED` 等失敗碼語意不變。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | **是** | 不變式違反與儲存失敗必須是兩個可區分的名字，這就是本票 |
| 6 | 例外是否會拋出 | **是** | 分流後兩條路都仍須 fail-closed，不得有任何一條變成放行 |

## 完成定義與證據

- **反向突變證據**：把新的具名失敗折回 `STORAGE_UNAVAILABLE`，指名的測試要轉紅；
  另一組：讓不變式違反不再被捕捉（例外逸出），也要有測試轉紅。
- 掃出 `worker_assignment.py` 與 `work_queue.py` 內**所有**同形狀的 except 分流，
  逐一標明是否需要分流——只修看到的那一個，是本專案已經記取兩次的教訓
  （C9→C10、governance 10 的全族掃描）。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

- **全套件責任**：兩張票並行實作，實作者只跑本票邊界內的測試檔；全套件與殘留檢查由審閱者於整合前執行（比照 governance 11 的責任轉移，這是審閱者的未完成義務，不得因實作者回報綠即視為滿足）。

## 不在本票範圍

`live_dispatch_metadata_boundary.py` 與 `document_mutation_gate.py` 的例外分流
（各自有票、各自的邊界）；把 validator 的訊息文字變成對外契約。

## 正式環境移植 SOP

不適用（本機記帳；新增失敗碼不影響已安裝的 runtime 行為）。

## 完成回寫

- 實際檔案：`library/local_orchestration/worker_assignment.py`、`work_queue.py` 與兩個測試檔
- commit：`e7cc1f0`，經 `admit_document_mutation` 判為 `INTEGRATED`
- **掃描**：六處同形狀 except，**分流兩處**（`claim_worker_assignment`、`enqueue_work`），其餘四處逐一追可達性後判定不需分流：`settle_worker_assignment`／`pull_work` 只把已驗證的項目一對一替換（lifecycle 翻轉），不可能新造重複；兩個 read 路徑必須維持 `STORAGE_UNAVAILABLE`，既有 cell 有此要求
- **可達路徑比審閱者發現的更深**：`receipt_ref`／`origin_ref` 有顯式守衛，**`claim_id`／`item_id` 是新 UUID、全域沒有任何顯式檢查**，validator 是它們背後唯一的防線。新測試從這個未守衛的欄位觸發碰撞，所以既有的 `RECEIPT_ALREADY_CLAIMED`／`ORIGIN_ALREADY_QUEUED` 語意完全未動
- **分流的形狀**：在帳本建構那一行外面包一層窄 try，而**不是**把外層 except 依例外型別拆開——外層仍必須接住 `_load()` 讀到壞檔時的 `ValidationError`
- 新失敗碼：`ASSIGNMENT_INVARIANT_VIOLATED`、`QUEUE_INVARIANT_VIOLATED`
- **反向突變**：實作者兩組（折回 `STORAGE_UNAVAILABLE`；讓例外逸出）。審閱者從第三道門進去——**兩個 handler 一字未動**，只把建構搬出內層 try（未來為了可讀性把值提前的典型重構）→ `InvariantViolationTests` 轉紅，跨行程 cell 也跟著具名失敗；還原後 101 綠。這證明釘子釘在**被走的那條路**上，不是釘在 handler 上
- 全套件（受閘測試開啟）：1408 passed、1 skipped、3254 subtests、零 FAILED、無殘留

```johnny-status
id = 16
title = 不變式違反被報成儲存問題
state = DONE
stage = S | 掃描同形狀分流 | DONE
stage = F | 具名分流 | DONE
stage = M | 突變驗證 | DONE
```
