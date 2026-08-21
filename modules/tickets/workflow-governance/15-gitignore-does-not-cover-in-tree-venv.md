# 15｜.gitignore 不擋 in-tree venv

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（repository 衛生；同族兩次目擊見下） |
| 第一步排查起點 | `.gitignore`（現有 7 行，無 venv 條目） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-15`／branch `implement/gov-15-ignore-venv` |
| 實作語言 | gitignore ＋ Python 3.11（釘住用的測試） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `d3498d1`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Sonnet 5 high（一般小票，依 `dispatch-model-profile.md` 分層） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `.gitignore` 與新測試檔 |
| 禁止修改 | `library/`；既有測試；`modules/tickets/` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = .gitignore
modify = tests/test_repository_hygiene.py
create = tests/test_repository_hygiene.py
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

在任何 worktree 裡建 `.venv/`、或測試流程留下 `suite.log`，`git status` 不再把它們
列成未追蹤項目，`git add -A` 也掃不進去。

## 同族兩次目擊（2026-08-21）

1. governance 14 的票**要求**在 worktree 內建 `.venv/` 做驗收，實作者回報它是
   「未忽略的未追蹤目錄」並明言 `git add -A` 會把它掃進去。
2. 當天稍晚，一個反斜線被吃掉的雜散 venv 目錄（783 個檔案、27 萬行）經 `add -A`
   進了收尾 commit 並 ff 進 main，靠 reset 兩個 checkout 才排除。origin 未受污染。

流程面的修正（收尾 commit 逐檔明確路徑）已生效，但流程規則只約束記得它的人；
ignore 條目約束所有人。

## TDD 設計

1. 正常行為：`git check-ignore` 對 `.venv/` 下的檔案與 `suite.log` 都回報被忽略。
2. 規則違反／輸入錯誤：不適用（無輸入面）。
3. 外部失敗／fail-closed：測試對 `git` 不可用時要 skip 而非假綠。
4. 回歸保護：既有 7 行條目全部仍然生效（逐條斷言，不只斷言新增的兩條）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | `.venv/` 條目不得連帶忽略 `.venv-notes.md` 這類前綴相似檔名；`suite.log` 不得連帶忽略 `suite.log.py` |
| 2 | null／空字串／陣列 | 否 | 無輸入面 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 無對外錯誤碼 |
| 6 | 例外是否會拋出 | 是 | git 不可用 → skip，不得假綠 |

## 完成定義與證據

- 缺陷修正 baseline-red：修法前 `git check-ignore .venv/x` 非零退出（就是現在的行為），修法後為零。
- **反向突變證據**：移除新增的 ignore 條目，指名的測試轉紅；還原後轉綠。
- 實作者只跑新測試檔；全套件與殘留檢查由審閱者於整合前執行（比照 governance 11 的責任轉移）。

## 不在本票範圍

清除歷史上已被追蹤的任何檔案（現況沒有）；`.claude/` 其他條目的調整。

## 正式環境移植 SOP

不適用（版控衛生，無 migration、無部署影響）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 15
title = .gitignore 不擋 in-tree venv
state = IN_PROGRESS
stage = F | ignore 條目 | OPEN
stage = T | 測試釘住 | OPEN
stage = M | 突變驗證 | OPEN
```
