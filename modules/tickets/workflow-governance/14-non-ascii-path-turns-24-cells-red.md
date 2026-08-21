# 14｜非 ASCII 路徑讓 24 個 cell 假紅

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（測試基礎設施；登記簿 E 族＝cp950／編碼，換一個面向出現） |
| 第一步排查起點 | `tests/test_claude_wake_command.py:88`（`_write_stub` 的 `.encode("ascii")`） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `tests/` 底下所有把路徑編成 ASCII 的位置 |
| 禁止修改 | `library/` 下任何產品程式碼；`tests/staging/environment_core/` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/test_claude_wake_command.py
modify = tests/test_antigravity_wake_command.py
forbid = library/
forbid = tests/staging/environment_core/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

在 repo tree 內建 venv 的人**不會拿到 24 個與他的改動無關的紅燈**。

## 實測到的事實（2026-08-21）

governance 10 的實作者照派工指令在 worktree 內建 venv，全套件回報
**24 failed**。逐一追下去，24 個全部源自同一行：

```
tests/test_claude_wake_command.py:88
('@echo off\r\n"%s" …' % sys.executable).encode("ascii")
```

`sys.executable` 走的是這個 checkout 的路徑，而本專案的路徑是
`…\Desktop\AI控制工作workflow\…`——**含中文**，`encode("ascii")` 直接
`UnicodeEncodeError`。

審閱者用 ASCII 路徑下的 venv 重跑同一棵樹：**1298 passed、零 FAILED**。
唯一的變數就是 venv 的位置。

`encode("ascii")` 在 `tests/` 與 `library/` 共有 **6 處**，不只這一個。
**要全部檢查**，判斷哪些會承載路徑——只修看到失敗的那一個，就是 10 那張票
明文禁止的做法換一個檔案重演。

## 這個缺陷的代價不是紅燈，是歸因

24 個紅燈全部指向 wake command，跟當時那張票（disposable environment 拆除）
毫無關係。實作者必須先證明「這 24 個跟我無關」才能回報，而**證明一件事與自己無關
比修好它更花時間**。更糟的形狀是相信了它們「本來就紅」，於是真的回歸被同一批雜訊蓋掉。

## TDD 設計

1. 正常行為：ASCII 路徑下的 venv，這些 cell 行為不變。
2. 規則違反／輸入錯誤：路徑含非 ASCII 字元時，寫出的 shim 仍然可用，不拋編碼例外。
3. 外部失敗／fail-closed：真正無法表示的位元組要以具名失敗呈現，
   **不得**改成無聲吞掉或以 `errors="replace"` 產生一個壞掉但看起來成功的 shim。
4. 回歸保護：各 cell 原本要證明的性質不變——本票只改編碼，不改被測行為。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | 空路徑、純 ASCII 路徑、含中文路徑三者各自明確 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | **是** | 非 ASCII 路徑不得拋 `UnicodeEncodeError`；真正的編碼失敗仍須具名 |

## 完成定義與證據

- 列出**全部 6 處** `encode("ascii")`，逐一標明是否承載路徑、是否需要修。
- **反向突變證據**：把修好的編碼改回 `encode("ascii")`，對應測試在含非 ASCII 路徑的
  情境下要轉紅；還原後轉綠。
- **驗收必須在 repo tree 內的 venv 跑一次**——這張票的整個意義就是那個情境，
  在 ASCII 路徑下驗收等於沒驗。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。

## 不在本票範圍

把專案搬到 ASCII 路徑（那是規避，不是修正——owner 的工作副本就在這個路徑上），
以及 `library/` 內任何 `encode("ascii")` 的產品程式碼行為變更。

## 正式環境移植 SOP

不適用（僅測試程式碼）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 14
title = 非 ASCII 路徑讓 24 個 cell 假紅
state = IN_PROGRESS
stage = S | 掃描全部 6 處 | OPEN
stage = F | 修正編碼 | OPEN
stage = M | 突變驗證 | OPEN
```
