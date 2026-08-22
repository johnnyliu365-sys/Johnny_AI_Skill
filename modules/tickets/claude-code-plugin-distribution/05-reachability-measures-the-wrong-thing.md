# 05｜可達性量錯了對象

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（票 04 的殘留缺陷；跨模型審閱者在乾淨 clone 上實測發現） |
| 第一步排查起點 | `library/local_orchestration/plugin_publication.py` 的 `publication_refs_reaching_commit`——它只掃 `refs/heads` 與 `refs/tags` |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | Revision 03／worktree `.worktrees/plugin-05-r03`／branch `implement/plugin-05-fetchable-pin-r03` |
| 實作語言 | Python 3.11 |
| 狀態 | `OPEN / CONVERGENCE_REPLAN / REVISION_03` |
| 共同基準 | 見派工訊息（worktree HEAD 為綁定 commit） |
| 實作者 | Luna / `xhigh`（一般票：判準明確、範圍小，但要動的是一個安全性質的量測對象） |
| 票級審閱者 | Terra / `xhigh`；能力強度不得低於實作者 |
| 功能集群審閱 | 全部票級整合後才由 Claude Code 進行架構一致性審閱；它不是本票的派工、票級審閱或整合前提。 |
| 責任邊界 | 可達性的量測對象與其具名狀態 |
| 禁止修改 | 票 03 的內容綁定（釘子與樹逐檔相符）；`payload` 宣告；釘住的 sha 值 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/plugin_publication.py
modify = tests/test_plugin_publication.py
modify = .claude-plugin/marketplace.json
forbid = .claude-plugin/plugin.json
forbid = library/local_orchestration/windows_package_manifest.py
forbid = skills/
forbid = modules/tickets/
```

## Revision 02 — typed reachability and generated-pin correction

`plugin_publication.py` is itself in the declared payload.  Therefore a source change in this
ticket necessarily creates a different publication tree and a different publication commit.
The implementation owner changes and commits only the two Python paths.  After Terra has reviewed
that source commit, Terra runs the declared generator on the same candidate branch, lets it update
the local publication anchor and `.claude-plugin/marketplace.json`, verifies the generated pin,
and creates the generated-pin commit before `admit_document_mutation`.  The SHA is never
hand-edited.  Remote push remains out of scope.

## Revision 03 — convergence replan

本票 Revision 02 的同一 closure 已完成一次 initial review 與一次 correction review。
初始實作 `539133f`、審閱者產生器／重釘 `8d28216`、第一個 correction `b7e17ec`
均保留為不可改寫的證據。在第二次 review 中，雖然候選 worktree 的 52 個 cell 都綠，
但以真正 fresh clone 執行時仍有兩個 real-pin cell 失敗：測試 helper 把
`refs/heads/publication-0.4.9` 當成 clone 一定存在的來源。這是 C13 型的
**evidence defect**，不是已核准的整合結果。

後續的 `e890c25` 已把測試暫時 remote 的 publication anchor 改為從已驗證的完整 pin SHA
建立；它在 fresh clone 得到 52 passed／279 subtests passed。但它是發現第二次 review
defect 後的補救證據，依 `CodeReview.md` 的 closure 上限，**不得直接合併或作為第三次
correction**。

因此本 Revision 03 明確授權新的 closure，而非 reset、amend、force 或刪除既有證據：

1. 同一位 Luna / `xhigh` 實作者在新的 worktree／branch 重新套用已留存的 source/test
   證據；可逐一 traceable cherry-pick `539133f`、`b7e17ec`、`e890c25`，或等價重作，
   但不可 cherry-pick `8d28216`，也不可產生 payload 或改 marketplace pin。
2. 重新套用後，實作者只提交 `library/local_orchestration/plugin_publication.py` 與
   `tests/test_plugin_publication.py`。其 fresh-clone helper 必須由**已驗證的完整 pin SHA**
   建立僅供測試的暫時 remote，不得假設任何本機 publication branch 在 clone 中存在。
3. Terra / `xhigh` 對 Revision 03 作新的 initial review；通過 source/test、反向突變與
   candidate 及 true fresh-clone 的測試後，才在同一候選 branch 跑產生器、驗證並提交
   `.claude-plugin/marketplace.json`。遠端 push 仍不在本票範圍。
4. 此 replan 不擴張任何可觀察行為、boundary 或外部權限；它只重置受 review-closure
   上限約束的審閱循環，並保留上述 commits 與 failure 為可稽核證據。

The ticket distinguishes the facts that require different remedies with the following strict,
public Python contracts:

```text
enum LocalPublicationReachability {
  LOCAL_REACHABLE,
  LOCAL_UNREACHABLE
}

enum RemotePublicationReachability {
  REMOTE_REACHABLE_AT_LAST_FETCH,
  NOT_PUSHED
}

struct PublicationReachability {
  LocalPublicationReachability local_state;
  RemotePublicationReachability remote_state;
  tuple<PushableRefName> local_refs;
  tuple<RemoteTrackingRefName> remote_tracking_refs;
}
```

`publication_refs_reaching_commit(root, sha)` returns this value object, not a tuple or a boolean.
`require_reachable_publication_ref(root, sha, ref)` preserves its existing purpose: it requires the
named **local** pushable anchor.  Add `require_fetchable_publication_ref(root, sha, ref)`, which
requires `REMOTE_REACHABLE_AT_LAST_FETCH` for the corresponding branch tracking ref and otherwise
raises the existing reachability error.  A tracking ref is evidence only of the last successful
fetch; no name or result may claim current remote truth.  A local tag remains a valid local
anchor, but without a remote-tracking branch it has `NOT_PUSHED` and is not fetchability evidence.

## Corrected observable result

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
3. **票 03 的內容綁定不變。** 本票以產生器重生發佈樹與釘子；新的釘子必須和
   新的 payload tree 精確相符，不得手改 SHA，也不得讓 source 與 pin 分兩次整合。
4. **fail-closed 不變**：ref 查詢失敗仍必須具名拋出，不得退化成「沒有 ref」。

## TDD 設計

1. 正常行為：用暫時 bare remote 建出 `origin/publication-1.2.3`，再在乾淨 clone
   執行候選程式；`LOCAL_REACHABLE` 與 `REMOTE_REACHABLE_AT_LAST_FETCH` 都成立，
   `require_fetchable_publication_ref` 成功。
2. 規則違反／輸入錯誤：只有本機分支、無 remote-tracking ref →
   `LOCAL_REACHABLE / NOT_PUSHED`，`require_fetchable_publication_ref` 具名拒絕，
   不得判為抓得到。
3. 邊界：本機 tag 保留其 local-anchor 成功性，但回傳
   `LOCAL_REACHABLE / NOT_PUSHED`；它不能被當成遠端 fetchability 證據。
4. 外部失敗／fail-closed：`for-each-ref` 失敗 → 具名拋出（票 04 已有，不得削弱）。
5. 回歸保護：票 04 的 local-anchor／刪 anchor／不合法 namespace 細胞與票 02／03
   的全部 cell 維持綠；只有舊 tag cell 的「等同遠端可達」期待依本票改為第 3 點。

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

- **反向突變證據**：至少三組——把 `refs/remotes/*` 查詢拿掉（乾淨 clone 的
  fetchability cell 必須轉紅）、讓「只有本機分支」判為抓得到、把兩個具名狀態折回
  一個布林；
  各指名哪個測試轉紅、還原後轉綠。
- **必須貼出乾淨 clone 上的實測**：測試先建立僅供測試的 bare remote，將候選 branch
  與 publication anchor 推入該暫時 remote，再 `git clone` 到新路徑並跑邊界內測試檔。
  這是對 candidate 的本機 clone-shaped 證據，並非實際 `origin` 的 push。不得只在
  既有 checkout 上驗——那正是本票要修的盲點。
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
