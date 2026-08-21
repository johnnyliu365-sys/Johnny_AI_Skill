# 13｜pytest 沒有被任何地方宣告

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（開發環境宣告缺口；由 governance 10 派工時暴露） |
| 第一步排查起點 | `requirements-dev.txt`（目前只 scoped 給 mypy，見檔頭註解） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-13`／branch `implement/gov-13-pytest-declaration` |
| 實作語言 | 相依宣告（`requirements-dev.txt`）＋ Python 3.11（釘住用的測試） |
| 狀態 | `DONE` |
| 共同基準 | `c2b720f` |
| 實作者 | Sonnet 5 high（一般小票，依 `dispatch-model-profile.md` 分層） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `requirements-dev.txt` 與釘住它的測試 |
| 禁止修改 | `requirements-runtime.lock`（那是執行期鎖定，pytest 不屬於執行期）；`library/` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = requirements-dev.txt
modify = tests/test_runtime_dependency_lock.py
create = tests/test_runtime_dependency_lock.py
forbid = requirements-runtime.lock
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

照著專案的相依宣告建一個 venv，**就能跑測試**，而且跑出來的綠燈可以回答
「是哪一個 pytest 跑的」。

## 現在的斷點

`pytest` 在整個 repo 裡**沒有被任何地方宣告**——不在 `requirements-dev.txt`
（它自己的檔頭寫明 scoped 給 mypy 型別檢查），不在任何 `.toml`／`.cfg`／`.ini`。

2026-08-21 派 governance 10 時實測到後果：實作者照派工指令建 venv，裝完
`requirements-dev.txt` 之後**沒有 pytest**，只好自己 `pip install pytest`（無版本），
拿到當時的 latest。這次剛好落在 `9.1.1`——跟本專案所有既有綠燈同一版——但那是運氣。

**沒有釘版本的測試環境會讓「全套件綠」變成無法回答的宣稱**：綠是哪個 pytest 跑的？
下次重建還會是同一個嗎？這兩個問題現在都沒有答案。

## 要達成的事

在 `requirements-dev.txt` 加入 `pytest==9.1.1`，並用測試釘住它與
`requirements-runtime.lock` 的**分工**：pytest 是開發期相依，**不得**進入執行期鎖定
（Router 的 runtime venv 實測沒有 pytest，也不需要）。

版本選 `9.1.1` 的理由：本專案所有既有綠燈都是它跑出來的，包含 0.4.7 發行前的驗證。
這是**對齊現況**，不是新選一個。

## TDD 設計

1. 正常行為：`requirements-dev.txt` 宣告了釘死版本的 pytest。
2. 規則違反／輸入錯誤：不得以範圍宣告（`>=`／`~=`）代替釘死。
3. 外部失敗／fail-closed：pytest **不得**出現在 `requirements-runtime.lock`——
   測試框架洩進執行期會讓 bundle 變大且擴大攻擊面。
4. 回歸保護：既有的 runtime lock 內容與其驗證不受影響。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | 空行、註解行不得被誤讀成宣告 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | **是** | 版本字串必須是精確相等比較，`9.1.1` 不得匹配 `9.1.10` |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 純宣告與斷言變更 |

## 完成定義與證據

- **反向突變證據**：把 `pytest==9.1.1` 改成 `pytest`（無版本）與改成 `pytest>=9`，
  兩者都要讓指名的測試轉紅；還原後轉綠。
- 另一組：把 pytest 加進 `requirements-runtime.lock`，要有測試轉紅。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。

## 不在本票範圍

升級 pytest 版本、或改動 `requirements-dev.txt` 既有的其他相依。本票只補上缺的宣告。

## 正式環境移植 SOP

不適用（開發期相依，不進 bundle、不影響已安裝的 runtime）。

## 完成回寫

- 實際檔案：`requirements-dev.txt`、`tests/test_runtime_dependency_lock.py`（新增）
- commit：`973e079`，經 `admit_document_mutation` 判為 `INTEGRATED`
- **釘住三件事**：宣告必須是精確 `==`；pytest **不得**出現在 `requirements-runtime.lock`（出貨的 bundle 沒有測試框架，也不需要）；**正在執行的 pytest 版本必須等於宣告的版本**。第三件才是本票的重點——檔案寫 9.1.1 而實際跑 9.2 的情況會通過前兩項檢查。
- **反向突變**：實作者三組（無版本、範圍宣告、pytest 注入 runtime lock）。審閱者另做一組不同方向的：追加一行 `pytest>=8` 與 `pytest==9.1.1` **並存且矛盾** → **6 passed 零轉紅**，因為解析器抓到第一個就停。補 `test_exactly_one_pytest_declaration_line_is_present` 後重跑同一組突變，**恰好 1 紅**，還原後 8 passed。
- **審閱者發現的第二個缺口**：宣告從未跟實際執行的 pytest 對照（`__version__` 零命中），補 `RunningPytestVersionMatchesDeclarationTests`，失敗訊息同時帶出兩個版本值。
- **控制面自己的錯**：本票的 `johnny-boundary` 只寫了 `modify`、沒寫 `create`，與票的文字要求（新增測試）矛盾。閘門會據此拒絕一個合法交付。已於 `1569619` 補上——修的是宣告去對齊票，不是放寬邊界去遷就實作者。
- 全套件（受閘測試開啟）：1326 passed、1 skipped、3133 subtests、零 FAILED、無殘留。

```johnny-status
id = 13
title = pytest 沒有被任何地方宣告
state = DONE
stage = D | 補上宣告 | DONE
stage = T | 測試釘住分工 | DONE
stage = M | 突變驗證 | DONE
```
