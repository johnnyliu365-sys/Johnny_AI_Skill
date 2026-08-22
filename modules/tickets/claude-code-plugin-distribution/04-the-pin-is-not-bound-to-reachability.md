# 04｜釘子沒有綁到可達性

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（票 03 的殘留缺口，審閱者以突變證實） |
| 第一步排查起點 | `refs/publication/0.4.9`——它是唯一指向釘住 commit 的 ref，而那個 namespace GitHub 不服務 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/plugin-04`／branch `implement/plugin-04-reachable-pin` |
| 實作語言 | Python 3.11 |
| 狀態 | `OPEN` |
| 共同基準 | `53c6d4e3`（worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Sonnet 5 high（一般票：形狀明確，判準可量——一個 cell 加一個 namespace 決定） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 發佈 commit 的錨定 ref 與證明它可達的測試 |
| 禁止修改 | 票 03 的產生器邏輯與 `payload` 宣告；`.claude-plugin/plugin.json` |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/plugin_publication.py
modify = tests/test_plugin_publication.py
forbid = .claude-plugin/plugin.json
forbid = library/local_orchestration/windows_package_manifest.py
forbid = skills/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

**釘住的 commit 是「推得出去、拿得回來」的東西**，不是「剛好還在某台機器的 object store 裡」。

## 審閱者的突變證據（2026-08-22）

刪掉 `refs/publication/0.4.9`——**唯一**指向 `b856cf88` 的 ref：

```
79 passed, 574 subtests passed
```

**零紅。** 那個 commit 是 parentless，刪掉 ref 之後沒有任何東西指著它，離一次
`git gc` 一步之遙，而且不可能被 push 出去——**測試分不出「使用者拿得到」和
「我本機還在」。**

再查證：`git ls-remote origin 'refs/publication/*'` 回 **0 個**。
那個 namespace GitHub 不收。票 03 的實作者自己備註要改推成
`refs/heads/publication-0.4.9`——**他們知道，但沒有任何測試釘住它。**

## 這是 D7 往上一層

票 03 把釘子綁到了**樹**（給定 sha，樹的內容必須逐檔相符）。本票綁的是另一半：
**那個 sha 必須從一個推得出去的 ref 可達。** 一個沒人抓得到的 commit 不是發佈，
即使它的樹完全正確。

## 不可讓的性質

1. **錨定 ref 必須在可推送的 namespace**：`refs/heads/*` 或 `refs/tags/*`。
   `refs/publication/*` 不算——已實測 origin 不收。
2. **可達性必須被測試釘住**：拿掉錨定 ref，套件**必須轉紅**。審閱者上面那個突變
   是本票最低限度的成功條件。
3. **可達 ≠ 已推送。** 本機測得到的是「從某個可推送 namespace 的 ref 可達」；
   「已經在 origin 上」需要網路且需要 owner 授權，**不得由測試假裝驗過**。
   兩者必須是可區分的具名狀態。
4. **不得改動釘住的 sha 值。** 本票只換錨定方式，不重新產生發佈樹——
   換了 sha 就等於繞過票 03 的內容綁定。

## TDD 設計

1. 正常行為：釘住的 sha 從一個 `refs/heads/*`／`refs/tags/*` 的 ref 可達。
2. 規則違反／輸入錯誤：錨定 ref 在不可推送的 namespace → 具名拒絕。
3. 外部失敗／fail-closed：ref 查不到／`for-each-ref` 算不出來 → **具名拋出，
   不得當作「沒有 ref」而回可達為假以外的任何靜默結果**；「讀不到 ≠ 不存在」。
4. 回歸保護：票 02 的 39 個 cell 與票 03 的 40 個 cell 全部不改且維持綠。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | `refs/heads/publication-0.4.9` 與 `refs/publication/0.4.9` 必須可分；不得以子字串比對 |
| 2 | null／空字串／陣列 | **是** | 「沒有任何 ref 指向它」與「ref 查詢失敗」必須可區分 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | **是** | sha 必須完整小寫且與票 03 釘的完全相同 |
| 5 | 錯誤碼是否一致 | **是** | 不可推送 namespace、無 ref、查詢失敗 三者具名 |
| 6 | 例外是否會拋出 | **是** | 查詢失敗必須拋 |

## 完成定義與證據

- **反向突變證據**：至少三組，**必須包含審閱者那一組**——刪掉錨定 ref 必須轉紅；
  另加「把 ref 換到不可推送 namespace」與一組自訂；各指名哪個測試轉紅、還原後轉綠。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

**實際 push**（需 owner 明確指示）；repo 公開（同上）；
公開後的線上安裝驗證——`raw.githubusercontent.com` 只服務公開 repo，
現在對本 repo 回 404，**在公開前這條路徑無法驗證，不得宣稱驗過**。

## 正式環境移植 SOP

錨定 ref 換 namespace 後，push 指令會變。實作者必須寫出**確切的 push 指令**，
但不得執行。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 04
title = 釘子沒有綁到可達性
state = OPEN
stage = R | 可推送 namespace 的錨定 | OPEN
stage = T | 可達性被測試釘住 | OPEN
stage = M | 突變驗證（含審閱者那一組） | OPEN
```
