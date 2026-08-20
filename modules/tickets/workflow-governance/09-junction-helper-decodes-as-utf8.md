# 09｜junction 輔助函式的 UTF-8 解碼

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（測試基礎設施缺陷；同族見 `PITFALL-REGISTER.md` E 族 cp950 主控台） |
| 第一步排查起點 | `modules/tickets/workflow-governance/06-mklink-output-decoded-as-utf8.md`（同一個缺陷、已完成的修法） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／無 receipt／worktree `.worktrees/gov-09`／branch `implement/gov-09-junction-decode` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `tests/test_bounded_child_process_runner.py` 的 `_make_junction` |
| 禁止修改 | `shell=False`、`check=False`、`timeout=5`；其他 cell；`library/` 下任何檔案 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/test_bounded_child_process_runner.py
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

全套件警告數從 **7 降到 0**，且 `mklink` 失敗時 stderr 會出現在斷言訊息裡。

## 缺陷（已定位，不需重新調查）

`tests/test_bounded_child_process_runner.py` 的 `_make_junction`（約第 553 行）以
`encoding="utf-8", errors="strict"` 執行 `cmd.exe /d /c mklink /J`。本機主控台是
cp950，`mklink` 的在地化輸出解不動，`UnicodeDecodeError` 在 subprocess 自己的
reader thread 裡拋出，pytest 以 `PytestUnhandledThreadExceptionWarning` 呈現。
該函式被呼叫多次，因此產生七個警告。

**修法已存在**：governance 06 對 `tests/test_disposable_environment_core.py` 的
`t3` 做過完全相同的修正，已整合進 `main`。照那個形狀做即可——拿掉 `encoding=`／
`errors=`，讓 `capture_output` 回傳位元組，在**呼叫端**以 `errors="replace"` 解碼。

**額外一項**：此處的 `self.assertEqual(0, result.returncode)` 連 stderr 都沒有傳進
斷言訊息，比 `t3` 更糟——真的失敗時什麼線索都沒有。解碼後的 stderr 要傳進去。

## TDD 設計

1. 正常行為：junction 建立成功時，該 cell 通過且不產生 unhandled thread exception。
2. 規則違反／輸入錯誤：`mklink` 失敗時，斷言訊息包含解碼後的 stderr。
3. 外部失敗／fail-closed：輸出含無法解碼的位元組時不拋例外。
4. 回歸保護：junction 的 reparse point 斷言與既有行為不變。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | stderr 為 `None`、空 bytes、純空白三種都不得拋例外 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | 是 | 解碼失敗不得傳播為 unhandled thread exception |

## 完成定義與證據

- 單跑 `tests/test_bounded_child_process_runner.py`：警告 **7 → 0**，測試仍全過。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。
- **反向突變證據**：把 `errors="replace"` 改回 `errors="strict"`，警告應重新出現；還原後歸零。
- 缺陷修正 baseline-red：本缺陷以警告呈現而非測試失敗，故以警告數為 baseline 證據
  （修法前 7、修法後 0）。

## 正式環境移植 SOP

不適用。

## 完成回寫

- 實際檔案：`<待填>`
- commit：`<待填>`

```johnny-status
id = 09
title = junction 輔助函式的 UTF-8 解碼
state = IN_PROGRESS
stage = F | 修法 | OPEN
stage = V | 驗證 | OPEN
```
