# 10｜lease 家族的第二個間歇

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（測試基礎設施；來源為 `PITFALL-REGISTER.md` C10） |
| 第一步排查起點 | `modules/tickets/PITFALL-REGISTER.md` › C10 與 C9（因果鏈在那裡） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
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

- 實際檔案：待填
- commit：待填

```johnny-status
id = 10
title = lease 家族的第二個間歇
state = IN_PROGRESS
stage = S | 掃描全族 | OPEN
stage = F | 無條件拆除 | OPEN
stage = M | 突變驗證 | OPEN
```
