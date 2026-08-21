# 10｜lease 家族的第二個間歇

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（測試基礎設施；來源為 `PITFALL-REGISTER.md` C10） |
| 第一步排查起點 | `modules/tickets/PITFALL-REGISTER.md` › C10 與 C9（因果鏈在那裡） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-10`／branch `implement/gov-10-lease-family` |
| 實作語言 | Python 3.11 |
| 狀態 | `DONE` |
| 共同基準 | `09ec337`（worktree HEAD） |
| 實作者 | Sonnet 5 high（一般票，依 `dispatch-model-profile.md` 分層） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `tests/staging/environment_core/` 與使用 disposable environment 的測試檔 |
| 禁止修改 | `library/` 下任何產品程式碼 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/staging/environment_core/
modify = tests/test_codex_receipt_removal_acceptance.py
modify = tests/test_codex_lifecycle_oracle.py
modify = tests/test_disposable_environment_core.py
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

使用 disposable environment 的 cell **不會因為一次暫時性的 Windows 檔案鎖就留下孤兒**——
不只是 `cr167` 那一個。

## 已知事實（C9／C10，不要重跑獵捕）

C9 的因果鏈已定位：Windows share-mode 讓**改名**（不只刪除）被讀者擋住，例外從斷言區
拋出，環境沒被拆除，後續每個用 disposable environment 的 cell 連鎖失敗。

**C9 的修法只治了 `cr167` 一個 cell。** 根因（B2）沒有消失。C10 是同族第二次出現，
落在 `test_codex_receipt_removal_acceptance` 的 `a4`。

## 要達成的事

**掃過所有使用 `DisposableEnvironmentAllocator` 的 cell**，找出哪些的拆除不是落在
每一條路徑上（斷言失敗、例外、改名／刪除被擋），把它們修成無條件拆除。

做法由實作者決定——共用的 helper、context manager、或 `addCleanup` 都可以。
**但不得只修看到過失敗的那兩個 cell**：這一族的特徵就是「這次是哪個 cell 純屬運氣」。

## TDD 設計

1. 正常行為：每個受影響的 cell 正常路徑不變。
2. 規則違反／輸入錯誤：不適用（無外部輸入）。
3. 外部失敗／fail-closed：模擬拆除被擋（`PermissionError WinError 5`），
   斷言 runtime root 仍被清空。
4. 回歸保護：各 cell 原本要證明的安全性質不得被削弱。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不新增路徑判斷 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | **是** | 每個 cell 的拆除都必須在例外與斷言失敗時仍然執行 |

## 完成定義與證據

- 列出**所有**使用 disposable environment 的 cell，逐一標明其拆除是否無條件。
- **反向突變證據**：把任一個修好的拆除移回只在成功路徑執行，對應測試要轉紅。
- 全套件綠、零殘留，跑完保留 `--tb=short` 的完整輸出到檔案
  （C10 的取證缺口就是只留了失敗行、沒留原因）。

## 正式環境移植 SOP

不適用。

## 完成回寫

- 實際檔案：`tests/staging/environment_core/environment.py`、`tests/test_codex_receipt_removal_acceptance.py`、`tests/test_disposable_environment_core.py`
- commit：`733168e`，經 `admit_document_mutation` 判為 `INTEGRATED`（第一次提交時被判 `INTEGRATION_FAILED`／不能 ff，rebase 到 main 後重驗才通過）
- **根因修在共用配置器**：`_unlink_past_transient_block`／`_rmdir_past_transient_block`，比照既有的 `_rename_past_transient_block`。最後一次嘗試在 try 之外，所以永久性封鎖仍會拋出——會吞掉最後一次失敗的 retry 等於回報一個沒發生的拆除。17 個檔案的所有 cell 都受益，不用逐一改。
- **兩個呼叫點漏了拆除**：`_ready()` 在 `provision()` 之後、呼叫端的 try 之外呼叫 `initialize()`；核心檔兩個 cell 完全沒有 cleanup。
- **反向突變**：實作者一組（拿掉 unlink retry → `05_r3_a` 紅）。審閱者另做一組**不同方向**的：把永久封鎖吞掉 → **25 passed，零轉紅**。
- **為什麼原本抓不到**：`05_r3_b` 只釘 `teardown()` 的可觀察狀態，而那個狀態有兩條路可以抵達——unlink 真的拋出，或 unlink 吞掉後父目錄非空、`rmdir` 以 `OSError [WinError 145]` 失敗，被寬 `except OSError` 報成同一個 `BLOCKED`／`DELETE_FAILED`。**同一個結果，兩條路**，所以它分不出真修好和假修好。補的 `test_05_r3_c_a_...` 直接測 helper 本身，審閱者重跑突變後**恰好 1 紅**，還原後 26 passed。
- **未達成且未偽裝**：`test_codex_registration_foreign_state_isolation_acceptance.py` 有同族的**已確認活缺陷**（兩個 lease 在 try 之前取得，第二個失敗會漏掉兩個），在 `modify` 白名單外，實作者停在邊界沒有擅自擴大。另開票處理。
- 全套件（受閘測試開啟）：1318 passed、1 skipped、3134 subtests、零 FAILED、無殘留。

```johnny-status
id = 10
title = lease 家族的第二個間歇
state = DONE
stage = S | 掃描全族 | DONE
stage = F | 無條件拆除 | DONE
stage = M | 突變驗證 | DONE
```
