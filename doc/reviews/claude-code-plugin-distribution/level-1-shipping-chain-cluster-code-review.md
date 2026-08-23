# Level 1 出貨鏈 功能集群 Code Review

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | Level 1 plugin 出貨鏈（票 01–05） |
| 共同基準 | `27916912e47bd00cbbd90dce24ecf8c1f80ca2d3` |
| 受審 commit | `45b7c914`（02）、`53c6d4e3`（03）、`9bb7097c`（04）、票 05 的整合鏈至 `27916912` |
| 審閱者 | 控制面（架構一致性審查，依 `ADR-20260823-014` 決策 5） |
| 修訂 | `REVISION_01`（2026-08-23）—— live CLI 證據推翻原 F1 處置，結論不變 |
| 結論 | `CHANGES_REQUESTED` —— **逐層通過，合成未通過；F3 為票 08 死結的根因** |

## Revision 01：原 F1 處置更正

原審查把缺陷定位在 marketplace cache，因而提出「README 改用 raw marketplace URL」。
這只修到第一個 cache。2026-08-23 在 repo 公開後以 Claude Code CLI `2.1.231`、隔離的
`CLAUDE_CONFIG_DIR` 實裝，raw URL 確實只快取 marketplace descriptor；然而
`plugin install` 仍 clone `source.url` 指向的開發 repository，checkout 釘住的 payload
commit 後把開發 `main` 與 object store 留在 plugin cache。

因此原 F1 的根因與處置均錯誤，不能再當 ticket authority。正確根因是
**plugin source repository 本身帶著開發 refs/history**；正確處置是
[`ADR-20260823-015`](../../adr/ADR-20260823-015-dedicated-plugin-publication-repository.md)
決定的獨立 payload-only publication repository。raw URL 仍是必要的 marketplace-cache
控制，但單獨使用不構成修復。

## 規格／需求變更追溯

原集群審查時沒有對應這項合成承諾的 SPEC 條目，源頭是 owner 的直述要求：
「讓使用者看到的安裝指引不是要他們 clone，而是直接可以安裝」（2026-08-22）。
Revision 01 已將 live evidence 與 topology change 正式登記為
`PRD-20260823-034` / `CHG-20260823-034`；既有 Claude distribution SPEC 現為
`STALE / REVISION_REQUIRED`，不是後續開票 authority。

該要求即是本次審查的驗收對象。逐票的追溯各自寫在
[`modules/tickets/claude-code-plugin-distribution/`](../../../modules/tickets/claude-code-plugin-distribution/) 內，
本文件不重抄。

## Context、tickets、elements 與實作衝突核對

**本審查問的不是「每張票有沒有做到它自己說的」——那是票級審查的事，已各自完成。
問的是「五張票合起來，有沒有達成 owner 要的那件事」。**

鏈有三環：

| 環節 | 由誰保證 | 狀態 |
| --- | --- | --- |
| 宣告 ↔ 釘住的樹 | 票 02（白名單）＋ 票 03（產生器與內容綁定） | **成立** |
| 釘子 ↔ 可達性 | 票 04（可推送錨定）＋ 票 05（量測對象修正） | **成立** |
| 可達性 ↔ **使用者實際打的指令** | 無人 | **斷** |

`README.md:39` 目前寫的入口是：

```text
claude plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill
```

那是 **owner/repo 形式**。2026-08-22 實測：該形式會把整個開發庫 clone 成 marketplace
快取（12 MB、89 個 commit）。raw URL 可以把這一端縮成單一 descriptor，但 marketplace
entry 內的 `source.url` 仍是
`https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git`。Claude 接著 clone 該 source，
所以換入口無法阻止開發 repository 進入 plugin cache。

修訂後的合成結果是：checkout 確實只有 243 檔；**兩種入口中 owner/repo 形式污染
marketplace cache，而 raw 形式仍會讓 plugin cache 的 `.git` 保留整個開發 object graph。**
兩個 cache 要由兩個不同控制關閉。

**沒有任何一張票寫錯。** 每張票的邊界內都正確，而且各自有反向突變證據。
錯的是它們合起來——這正是逐票審查在定義上看不到的那一類。

## 發現、風險與處置

### F1｜plugin source 與 development source 未隔離（`CHANGES_REQUESTED`）

票 02–05 把出貨從 797 檔壓到 243 檔、釘住版本、證明可達；但它們在開發 repository
裡產生與錨定 payload commit。Claude 為了取得該 commit 先 clone 同一 repository，
因此正確 checkout 與錯誤 object graph 可以同時成立。

處置：開發 repo 保留 payload 產生器與公開 raw marketplace descriptor；descriptor 的
`source.url` 改指獨立 publication repo。該 repo 的 default `main` 與版本 tags 只可達
parentless、精確 payload commits。README 同時改用 raw marketplace URL，分別關閉兩端。
repo 已公開，raw descriptor 與 pinned archive 均已線上驗證；尚未建立的 publication
repo 不得寫成存在或已驗證。

### F2｜合成承諾零測試覆蓋（`CHANGES_REQUESTED`，且應先於 F1）

`test_plugin_payload_boundary.py` 39 cells、`test_plugin_publication.py` 53 cells，
共 92 個 cell，每一層都被證明。掃過整個 `tests/`：
**沒有任何測試把「使用者打的指令」連到「硬碟上出現什麼」。**
（`marketplace add`／`plugin install`／`plugins/cache` 的字面命中全部落在
Codex lifecycle 的 staging 檔，與本集群無關。）

處置：新增端到端測試，斷言「照 README 的指令做，兩個 cache 都符合宣告」。除了
visible checkout 的 path/blob equality，必須列舉 plugin cache 的每個可達 ref/commit，
對每棵樹執行 payload difference；`.git` 中不得存在可達的 payload 外樹。已知開發
sentinel 必須不可讀，但 sentinel 不能取代全列舉。

**順序依賴**：先建立 F2 verifier 與本地正／反 fixture；F1 的 live cutover candidate
再以真實 CLI 跑到 green，才可一起整合 source URL、version、pin 與 README。沒有 F2，
F1 仍只是把一個沒被守住的敘述換成另一個。

### F3｜驗證 payload 的工具在 payload 裡（票 08 版本死結的根因）

票 08 目前是 `BLOCKED / REQUIREMENT_CHANGED / VERSION_TAG_COLLISION`。它的封鎖判定經
複驗成立，但**觸發它的是一個結構性質，而那個性質已經咬過三次**：

| # | 觸發 | 後果 |
| --- | --- | --- |
| 1 | README 修訂（08-22） | payload 變 → 重生 → 重釘，**兩次** |
| 2 | 票 04 的修正 | payload 變 → 必須重釘，而票 04 自己的不可讓性質禁止重釘（開票者的矛盾） |
| 3 | 票 10 的修正 | payload 變 → root 變 → 與已發佈的 `plugin-v0.4.10` 衝突，**票 08 死結** |

共同形狀一句話：**驗證 payload 的工具，本身在 payload 裡。**
`plugin_publication.py`（產生器）與 `claude_plugin_cache_closure.py`（檢查器）都在
`library/local_orchestration/`，而 `library` 是 payload 的枚舉樹，所以**修檢查器就會改變被檢查的東西**。
這與票 09 處理的 SHA-1 不動點同族，只是發生在程式碼層而非 manifest 層。

實測 `skills/` 與 `commands/` 對 `library/` 的**全部**引用只有三處：

```text
library/MODULE_CATALOG.md
library/workflow_router/
library/workflow_router/contracts.py
```

`library/local_orchestration/` —— **101 個 `.py`、1.5 MB —— 零 skill 引用**。
payload 內唯一提到它的是 `AGENTS.md:52` 的 `worktree_containment.py`：**101 個檔裡 1 個被引用。**

也就是說 Level 1 出貨的是 Level 2 的 runtime。使用者拿到一整套用不到的發佈工具，
**而正因為它被出貨，每一次修那套工具都會改變已發佈的成品。**

處置建議（落點由實作者論證）：`library` 由整棵樹改為只出貨實際可達的部分，
並以 `payload.files` 明列 `worktree_containment.py` 以維持閉包。Level 2 不受影響——
`_PAYLOAD_TREE_ROOTS` 是票 02 不可讓性質第 5 條要求的**獨立清單**，本改動不碰它。

**順序要求**：F3 必須先於「選定後繼版本」。若先選版本，同一個碰撞會在下一版重演——
任何對發佈工具的修正都會改變 payload，於是又需要一個新版本，而那個版本又鎖住下一次修正。

### 風險：本集群的既有品質不受此三項影響

逐層機制是可用的、被測試釘住的，且已在乾淨 clone 上驗證。F1／F2／F3 不是回退——
前兩項是把已經做好的東西接到使用者身上，F3 是拿掉一個從一開始就不該出貨的東西。

## 驗證證據

**從 `origin` clone 一份全新副本，在使用者拿到的形狀上跑全套件**：

```text
clone HEAD = 27916912
本機分支   = main（僅此一個）
釘子       = c3cb81c4550e6493f9d8478c4be31ffdad642f87
1679 passed, 22 skipped, 3982 subtests passed in 173.03s
零 FAILED（已另以 grep -E "^(FAILED|SUBFAIL|ERROR)" 確認，非僅看摘要——登記簿 D4）
```

**這是本集群第一次在乾淨 clone 上被完整驗證。** 2026-08-22 同樣形狀上量到的兩紅
（票 05 的可達性缺陷）已消失，登記簿 C13 的形狀在本集群內不再現形。

鏈的前兩環與新增失敗邊界實測：

```text
釘住的 c3cb81c4 → 243 檔；tests/ doc/ modules/ 各 0
可達性         → refs/remotes/origin/publication-0.4.9 指向同一個 sha
repo 可見性    → PUBLIC
raw marketplace cache → descriptor only
plugin checkout        → 243 files
plugin refs/heads/main → d35689a8 / 841 files
plugin .git            → 989 packed objects / 2,477,546 bytes
main:tests/test_plugin_publication.py → readable
```

## 未解項與 handoff 結論

| 項目 | 處置 |
| --- | --- |
| `CHG-20260823-034` / `ADR-20260823-015` | 架構決策已完成；Context/SPEC 尚待重訂 |
| F2 repository-closure verifier | 需開票；**先做**，含反向 fixture 與 real-CLI seam |
| F1 publication repo 與 source cutover | 需開票；依賴 F2；remote 建立/推送須具名 owner authority |
| README raw 入口與 live acceptance | 與 cutover 同候選落地；不得先讓 `main` 出現半套發布狀態 |
| F3 payload 過度包含 | 需開票；**必須先於「選定後繼版本」**，否則同一碰撞在下一版重演 |
| 票 08 後繼版本 | owner 決定；建議排在 F3 之後 |

逐層 `APPROVED`；集群 `CHANGES_REQUESTED`。Revision 01 只更正 finding authority，
沒有開票、建立 publication repo、移動 publication ref 或發布 release。

## 審查修訂紀錄

| Date | Baseline | Change |
| --- | --- | --- |
| 2026-08-23 | `d35689a8` | 公開 repo 上的隔離 live install 證明 raw URL 只修 marketplace cache；F1 改為 dedicated publication repository，F2 擴張為 installed Git reachable-tree closure。 |
| 2026-08-23 | `5c09d663` | 審票 08 時新增 F3：驗證 payload 的工具在 payload 裡，是三次重生／重釘／版本碰撞的共同根因。實測 `library/local_orchestration` 有 101 個 `.py`、1.5 MB、零 skill 引用。 |
