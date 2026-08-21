# 12｜foreign-state 的兩個 lease 在 try 之前取得

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（測試基礎設施；lease 家族第三例，前兩例為 C9 與本資料夾 10） |
| 第一步排查起點 | `modules/tickets/workflow-governance/10-lease-family-second-intermittent.md` › 完成回寫（同族的因果鏈與修法都在那裡） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-12`／branch `implement/gov-12-lease-acquisition` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `5567520`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Sonnet 5 high（一般票，依 `dispatch-model-profile.md` 分層） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `tests/test_codex_registration_foreign_state_isolation_acceptance.py` 與 `tests/test_bounded_child_process_runner.py` 的取得順序 |
| 禁止修改 | `tests/staging/environment_core/`（10 已修好共用配置器，不要再動）；`library/` 下任何產品程式碼 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/test_codex_registration_foreign_state_isolation_acceptance.py
modify = tests/test_bounded_child_process_runner.py
forbid = tests/staging/environment_core/
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

取得**多個** lease 的 cell，任何一個取得失敗都不會漏掉已經拿到的那些。

## 已確認的缺陷（governance 10 的實作者掃出，經審閱者核對）

`tests/test_codex_registration_foreign_state_isolation_acceptance.py:252-254`：

```
success_lease, success_oracle = _ready_oracle(allocator, "…e6a1")
compensation_lease, compensation_oracle = _ready_oracle(allocator, "…e6a2")
try:
```

兩個 lease 都在 `try:` **之前**取得，而 `_ready_oracle()` 自己會呼叫 `oracle.initialize()`。
第二次呼叫失敗時，**第一個 lease 已經在磁碟上而且沒有任何可及的參照**——連 `finally` 都
救不到它，因為變數從未被指派。

`tests/test_bounded_child_process_runner.py` 有幾個 cell 是同一個形狀（2–3 個 lease 在單一
`try:` 之前），觸發機率較低但形狀相同。

**10 已經把根因修在共用配置器**（unlink／rmdir 的有限重試），所以「暫時性封鎖」那一半不會
再咬人。本票處理的是另一半：**取得順序**造成的不可及參照，那是重試救不到的。

## TDD 設計

1. 正常行為：兩個 lease 都取得成功時，cell 原本要證明的隔離性質不變。
2. 規則違反／輸入錯誤：不適用（無外部輸入）。
3. 外部失敗／fail-closed：讓**第二次**取得失敗，斷言**第一個** lease 仍被拆除、
   runtime root 被清空。
4. 回歸保護：不得改動 `tests/staging/environment_core/`——10 已經修好那一層。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不新增路徑判斷 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | **是** | 第二次取得失敗必須讓第一個 lease 仍被拆除 |

## 完成定義與證據

- 列出所有取得多個 lease 的 cell，逐一標明取得是否在保護範圍內。
- **反向突變證據**：把修好的取得順序移回 `try:` 之前，對應測試要轉紅。
- **測試 venv 必須釘版本**：`pytest==9.1.1`（本專案所有既有綠燈的版本）。
  `requirements-dev.txt` 目前沒有宣告 pytest，見本資料夾 13。
- **不要在 repo tree 內建 venv**——中文路徑會讓 24 個無關 cell 假紅，見本資料夾 14。
  在 ASCII 路徑下建 venv。
- 全套件綠、零殘留，保留完整 `--tb=short` 輸出到檔案。

- **全套件責任**：三張票並行實作，實作者只跑本票邊界內的測試檔；全套件與殘留檢查由審閱者於整合前逐張執行（比照 governance 11 的責任轉移，這是審閱者的未完成義務，不得因實作者回報綠即視為滿足）。

## 正式環境移植 SOP

不適用。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 12
title = foreign-state 的兩個 lease 在 try 之前取得
state = IN_PROGRESS
stage = S | 掃描多 lease cell | OPEN
stage = F | 取得納入保護 | OPEN
stage = M | 突變驗證 | OPEN
```
