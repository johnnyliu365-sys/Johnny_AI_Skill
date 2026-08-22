# 05｜可達性量錯了對象

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（票 04 的殘留缺陷；票級獨立審查在乾淨 clone 上實測發現） |
| 第一步排查起點 | `library/local_orchestration/plugin_publication.py` 的 `publication_refs_reaching_commit`——它只掃 `refs/heads` 與 `refs/tags` |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/plugin-05`／branch `implement/plugin-05-fetchable-pin` |
| 實作語言 | Python 3.11 |
| 狀態 | `OPEN` |
| 共同基準 | 見派工訊息（worktree HEAD 為綁定 commit） |
| 實作者 | `implementation-standard`（一般票：判準明確、範圍小；若實作者論證不可再拆且有具名能力缺口，才走 `HardTicketAssessment` 升 `implementation-elevated`） |
| 審閱者 | `ticket-review`（票級獨立審查）。依 `ADR-20260823-014` 決策 5，票級審查與實作不得由同一個 profile 承擔；架構一致性審查在功能集群完成後另行進行，不在本票 |
| 責任邊界 | 可達性的量測對象與其具名狀態 |
| 禁止修改 | 票 03 的內容綁定（釘子與樹逐檔相符）；`payload` 宣告；釘住的 sha 值 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/plugin_publication.py
modify = tests/test_plugin_publication.py
forbid = .claude-plugin/plugin.json
forbid = .claude-plugin/marketplace.json
forbid = library/local_orchestration/windows_package_manifest.py
forbid = skills/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

**「使用者抓得到這個 commit」是一個被測試釘住的事實**，而且它在**乾淨 clone 上成立**——
不是只在做過這件事的那台機器上成立。

## 票 04 做對了什麼，以及它量錯了什麼

票 04 讓「刪掉錨定 ref → 轉紅」成真，那是它的最低成功條件，達成了。

但 `publication_refs_reaching_commit` 掃的是 `refs/heads` 與 `refs/tags`——**本機分支**。
於是兩個方向都錯：

| 情況 | 使用者抓得到嗎 | 現在的判定 |
| --- | --- | --- |
| 本機分支、從未 push | **抓不到** | 可達（**假綠**） |
| 在 origin 上、本機無分支 | **抓得到** | 不可達（**假紅**） |

第二列不是邊角案例——**`git clone` 只建立 `refs/heads/main` 一個本機分支**，
所以每一個乾淨 clone 都落在那一列。

## 實測證據（2026-08-23，審閱者在乾淨 clone 上量的）

```
git clone → refs/heads 只有 main
釘住的 f7b1c377 →  refs/heads|refs/tags 可達數：0
                   refs/remotes/origin/publication-0.4.9 → f7b1c377  ← 抓得到的正面證據
pytest tests/test_plugin_publication.py → 2 failed, 46 passed
```

同一台機器上、同一個 commit，在做過發佈的 checkout 裡是 46+2 全綠，在乾淨 clone 上兩紅。

## 這是登記簿 C13 那一族第二次出現

C13 是閉包測試依賴 harness 建的目錄；本票是可達性測試依賴本機分支。
**共同形狀：測試綁在做事那台機器的本機狀態上，而不是綁在 repo 事實上。**
兩次都在乾淨 clone 上翻臉，兩次都是在「使用者會拿到的形狀」上跑才看得見。

## 要達成的事（落點由實作者論證）

1. **量測對象改成「抓得到」**。`refs/remotes/*` 是「這個 commit 在某個遠端上」的證據，
   必須納入。落點由實作者論證：是把 remote-tracking 併入同一個查詢，
   還是分成兩次查詢後合併——寫下理由。
2. **「本機可達」與「遠端可達」必須是兩個具名狀態，不是一個布林。**
   票 04 的不可讓性質第 3 條原本就這樣要求，尚未落實。
   兩者的補救方式不同：前者要 push，後者不用做任何事。
3. **remote-tracking ref 的陳舊性要誠實**。它證明的是「上次 fetch 時它在遠端上」，
   不是「此刻仍在」。不得把它講成即時事實；該狀態的名字要說出這個限制。

## 不可讓的性質

1. **本機分支單獨存在不得判為「使用者抓得到」。** 從未 push 的本機分支是假綠，
   那正是票 04 存在的理由，不得在修正時反向再犯。
2. **乾淨 clone 上必須全綠。** 以測試釘住——不得只在做過發佈的 checkout 上驗。
3. **票 03 的內容綁定不變。** 本票不碰釘子的值，也不重生發佈樹。
4. **fail-closed 不變**：ref 查詢失敗仍必須具名拋出，不得退化成「沒有 ref」。

## TDD 設計

1. 正常行為：commit 在 origin 上且本機有分支 → 可達，且兩個具名狀態都為真。
2. 規則違反／輸入錯誤：只有本機分支、無遠端 → **具名為「未推送」**，不得判為抓得到。
3. 外部失敗／fail-closed：`for-each-ref` 失敗 → 具名拋出（票 04 已有，不得削弱）。
4. 回歸保護：票 04 的八個 cell 與票 02／03 的全部 cell 不改且維持綠。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | `refs/remotes/origin/publication-0.4.9` 與 `refs/heads/publication-0.4.9` 必須可分；前綴比對不得讓 `refs/headsX/` 混入 |
| 2 | null／空字串／陣列 | **是** | 「沒有任何 ref 可達」與「查詢失敗」必須可區分（票 04 已分，不得回退） |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | **是** | sha 必須完整小寫；ref 名稱必須完整，不得接受縮寫 |
| 5 | 錯誤碼是否一致 | **是** | 本機可達、遠端可達、未推送、查詢失敗——四個具名結果 |
| 6 | 例外是否會拋出 | **是** | 查詢失敗必須拋 |

## 完成定義與證據

- **反向突變證據**：至少三組——把 `refs/remotes/*` 拿掉（乾淨 clone 必須轉紅）、
  讓「只有本機分支」判為抓得到、把兩個具名狀態折回一個布林；
  各指名哪個測試轉紅、還原後轉綠。
- **必須貼出乾淨 clone 上的實測**：`git clone` 到一個新路徑、跑邊界內測試檔、全綠。
  **不得只在既有 checkout 上驗**——那正是本票要修的盲點。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行，
  且**審閱者必須至少在一個乾淨 clone 上跑過一次**。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

實際 push（需 owner 明確指示）；repo 公開；
`refs/remotes` 陳舊性的主動刷新（那需要網路，且 fetch 的時機是另一個設計問題——
本票只要求「說出它是上次 fetch 的事實」，不要求刷新它）。

## 正式環境移植 SOP

不適用（本機驗證邏輯；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 05
title = 可達性量錯了對象
state = OPEN
stage = M | 量測對象改為抓得到 | OPEN
stage = S | 本機／遠端兩個具名狀態 | OPEN
stage = C | 乾淨 clone 上全綠 | OPEN
stage = X | 突變驗證 | OPEN
```
