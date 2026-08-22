# 19｜閘門從來沒有判過控制面

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（外部參考啟發：GAL 的 time-of-check／time-of-use 第二張 receipt。查證後發現我們的缺口更根本） |
| 第一步排查起點 | `%LOCALAPPDATA%\JohnnyRouter\queue\document-mutation-journal.jsonl`（判決紀錄）與 `git rev-list` 對照 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-19`／branch `implement/gov-19-control-plane-gate` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `e0d318b`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Opus 5（難票：改變控制面自身義務，依 `dispatch-model-profile.md` 先派 Opus） |
| 審閱者 | 控制面（Opus 5）＋ owner（本票改變控制面自己的義務，值得 owner 過目） |
| 責任邊界 | 新增 `library/local_orchestration/control_plane_mutation.py` 與其測試 |
| 禁止修改 | `document_mutation_gate.py`（閘門本體不動，本票只是讓它多看見一類 commit） |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/control_plane_mutation.py
create = library/local_orchestration/control_plane_mutation.py
modify = tests/test_control_plane_mutation.py
create = tests/test_control_plane_mutation.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/dispatch_session.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

**每一個落在 main 上的 commit 都被判決過**，包括控制面自己寫的票、回寫、派工綁定與發行。
「這個 commit 憑什麼在 main 上」對任何一個 commit 都答得出來。

## 實測到的缺口（2026-08-22）

閘門模組誕生於 `a37daff6`（2026-08-21）。此後：

| 量 | 數字 |
| --- | --- |
| main 上的 commit | **76** |
| 閘門判決紀錄 | **14** |
| 未經判決 | **62** |

那 62 個不是漏網——是**設計上就沒有路徑**：控制面用 `git merge --ff-only` 從自己的
worktree 直接推進 main。類型分布：23 docs、16 ticket、8 release、6 dispatch 綁定等。

**閘門治理實作者，從來沒有治理過控制面。** 而控制面正是本專案歷史上出過最多事的角色：
未經授權 push、憑自己判斷刪掉 17 個測試（governance 08 的緣起）、`add -A` 掃進 783 個
檔案、三次在票裡宣告不存在的檔案。governance 08 為了「agent 不得自行增刪文件」而生，
卻從第一天就把寫這條規則的人排除在外。

外部參考（GAL）處理的是更窄的 time-of-check／time-of-use 窗口——precondition receipt
跑在 merge 之前，所以 merge 自身引入的漂移會逃過檢查，他們補一張 `--hygiene-only`
receipt 關窗。我們的 ff-only 讓那個特定窗口不存在（main 動過就 ff 失敗），
**但我們有一整類 commit 連第一張 receipt 都沒有。**

## 要達成的事

控制面的 commit 走一條**具名的、留痕的**入口，而不是 `git merge --ff-only`。

**這不是把控制面關進實作者的籠子。** 兩者的權限本來就不同：控制面**必須**能寫
`modules/tickets/`（實作者被禁止），因為開票是它的職責。要的是**留痕與可拒絕**，不是
把票變成無法開。

落點與判定條件由實作者論證，但下列性質不可讓：

1. **每次控制面整合都寫 journal**，帶 principal、變更路徑、判定結果。
2. **有一組控制面自己也不得違反的規則**，至少：不得在同一個 commit 內同時改
   `library/` 與 `modules/tickets/`（那正是「一邊改規則一邊改被規則管的東西」的形狀）；
   不得改 digest 釘死的檔案而不同步 repin。
3. **拒絕時 main 不得移動**——與既有閘門同樣的可證明性。
4. **不得成為繞過既有閘門的後門**：實作者的候選分支不得經由本入口整合；
   以命名空間或身分斷言證明兩條路徑不可互換。

## TDD 設計

1. 正常行為：一次合法的控制面整合留下 journal 條目，main 前進。
2. 規則違反／輸入錯誤：同 commit 同時動 `library/` 與 `modules/tickets/` → 具名拒絕；
   改政策檔未 repin → 具名拒絕。
3. 外部失敗／fail-closed：journal 寫不進去 → **拒絕整合**，不得「先合再說」。
4. 回歸保護：既有 `admit_document_mutation` 的行為與測試完全不變（本票不改它）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | `modules/tickets/` 與 `modules/tickets-archive/` 之類的前綴相似不得誤判 |
| 2 | null／空字串／陣列 | 是 | 空變更集、無 journal、無 principal 三者各自明確 |
| 3 | 權限繞過 | **是** | 本入口不得用來整合實作者候選；實作者入口不得用來整合控制面變更 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 混合變更、未 repin、journal 失敗各自具名 |
| 6 | 例外是否會拋出 | 是 | 每個失敗路徑 fail-closed |

## 完成定義與證據

- **反向突變證據**：至少三組——讓混合變更放行、讓 journal 失敗仍然整合、
  讓本入口接受實作者候選；各指名哪個測試轉紅、還原後轉綠。
- **本票自己的整合必須走新入口**（第一個使用者是它自己），journal 條目記入完成回寫。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。

## 不在本票範圍

追溯判決既有的 62 個 commit（歷史是歷史，本票只讓此後的都被看見）；
把控制面的權限縮到與實作者相同（那會讓開票變成不可能）。

## 正式環境移植 SOP

不適用（本機記帳；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 19
title = 閘門從來沒有判過控制面
state = IN_PROGRESS
stage = E | 具名入口 | OPEN
stage = R | 控制面自己的規則 | OPEN
stage = M | 突變驗證 | OPEN
```
