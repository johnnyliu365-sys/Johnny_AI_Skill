# 06｜mklink 輸出解碼

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理／測試基礎設施缺陷，非產品行為；來源為 `PITFALL-REGISTER.md` E 族） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/PITFALL-REGISTER.md` › E 族（cp950 主控台） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／無 receipt／owner 待填／worktree 待填／branch 待填／baseline `bed244d` |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `bed244d` |
| 實作者 | 重派：`.worktrees/gov-06`／branch `implement/gov-06-mklink-decode` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `tests/test_disposable_environment_core.py` 的 `t3` cell 之解碼方式 |
| 禁止修改 | `shell=False`、`check=False`、5 秒逾時；`library/` 下任何產品程式碼；其他 cell |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/test_disposable_environment_core.py
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

`t3` 執行後不再產生 `PytestUnhandledThreadExceptionWarning`，且 `mklink` 失敗時
stderr 會出現在斷言訊息裡。

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：由 chip 啟動的獨立 session。
- reviewer：控制面（Opus 5）。
- **Owner override record**：本票為**補開**。實作者由 chip 直接啟動，未經派工，
  且在 root checkout 而非綁定 worktree 工作，與 `Workflow.md` §5 不一致。
  owner 於 2026-08-20 按下 chip 即為啟動授權；審閱者與實作者不同 worktree，
  控制面未實作，故無控制面兼任實作之例外。
- `ImplementationHandoff`：本票 revision；chip prompt 內容不作為契約來源。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：本票只改測試內的 subprocess 解碼方式，不觸及任何正式 UI 邊界。

- element 路徑：不適用（既有測試檔內修正）
- 實際原始碼路徑：`tests/test_disposable_environment_core.py`
- 公開契約／資料模型：無變更

## TDD 設計

1. 正常行為：`mklink` 成功時，cell 通過且不產生 unhandled thread exception。
2. 規則違反／輸入錯誤：`mklink` 因參數錯誤失敗時，斷言訊息包含 stderr 內容。
3. 外部失敗／fail-closed：輸出含無法以 cp950 或 UTF-8 解碼的位元組時，不拋例外。
4. 回歸保護：`t3` 原本要證明的性質（junction 實體 root 在讀 marker 前被擋下）不變。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 本票不涉路徑比對；`t3` 既有的 junction 斷言不變動 |
| 2 | null／空字串／陣列 | 是 | stderr 為空、只有空白、以及 `None`（未擷取）三種都不得拋例外 |
| 3 | 權限繞過 | 否 | 不涉權限判斷 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | 是 | 解碼失敗不得傳播為 unhandled thread exception；`returncode` 判斷不受影響 |

## 完成定義與證據

- 單跑 `t3` 通過且該次執行的警告數比修前少一。
- 全套件綠、零殘留，且列出**完整**的 `FAILED`／`SUBFAILED` 清單。
- **紅燈輸出**：`<待填：每個行為第一次失敗的測試名稱與失敗原因>`

## 正式環境移植 SOP

不適用（僅測試程式碼，無 migration、環境變數或部署影響）。

## 完成回寫

- 實際檔案：`<待填>`
- commit：`<待填>`
- WorkProgress：不適用

```johnny-status
id = 06
title = mklink 輸出解碼
state = IN_PROGRESS
stage = F | 修法 | OPEN
stage = V | 驗證 | OPEN
```
