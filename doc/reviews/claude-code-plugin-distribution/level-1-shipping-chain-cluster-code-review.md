# Level 1 出貨鏈 功能集群 Code Review

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | Level 1 plugin 出貨鏈（票 01–05） |
| 共同基準 | `27916912e47bd00cbbd90dce24ecf8c1f80ca2d3` |
| 受審 commit | `45b7c914`（02）、`53c6d4e3`（03）、`9bb7097c`（04）、票 05 的整合鏈至 `27916912` |
| 審閱者 | 控制面（架構一致性審查，依 `ADR-20260823-014` 決策 5） |
| 結論 | `CHANGES_REQUESTED` —— **逐層通過，合成未通過** |

## 規格／需求變更追溯

本集群無對應 SPEC 條目，源頭是 owner 的直述要求：
「讓使用者看到的安裝指引不是要他們 clone，而是直接可以安裝」（2026-08-22）。

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
快取（12 MB、89 個 commit）。**那是 Claude Code CLI 的取得行為，不是本專案的程式碼，
改宣告改不動它。** 不 clone 的路徑是 `marketplace add <指向 marketplace.json 的 raw URL>`
（同日實測：成功且只快取一個 4 KB 檔），而 README 沒有那一行。

因此合成後的實際結果是：plugin 快取確實只拿到 243 檔，**但 marketplace 快取仍是整包**。
使用者硬碟上依然有整個開發庫，只是換了一個目錄。

**沒有任何一張票寫錯。** 每張票的邊界內都正確，而且各自有反向突變證據。
錯的是它們合起來——這正是逐票審查在定義上看不到的那一類。

## 發現、風險與處置

### F1｜文件描述的入口繞過了整套機制（`CHANGES_REQUESTED`）

票 02–05 把出貨從 797 檔壓到 243 檔、釘住版本、證明可達，而使用者被告知要打的那一行
把這些全部繞過。這是 governance 04 那一族的變體：**不是文件描述了不存在的機制，
是文件描述的入口用不到已經存在的機制。**

處置：README 的 Level 1 入口改為 raw URL 形式。**但 repo 目前是 `PRIVATE`，
`raw.githubusercontent.com` 只服務公開 repo，該路徑現在回 404**——所以此改動
要嘛等公開後再落地並實測，要嘛落地時明文標示「未在線上驗證」。
**不得寫成已驗證。**

### F2｜合成承諾零測試覆蓋（`CHANGES_REQUESTED`，且應先於 F1）

`test_plugin_payload_boundary.py` 39 cells、`test_plugin_publication.py` 53 cells，
共 92 個 cell，每一層都被證明。掃過整個 `tests/`：
**沒有任何測試把「使用者打的指令」連到「硬碟上出現什麼」。**
（`marketplace add`／`plugin install`／`plugins/cache` 的字面命中全部落在
Codex lifecycle 的 staging 檔，與本集群無關。）

處置：新增端到端測試，斷言「照 README 的指令做，落地內容等於宣告的 payload」。

**順序依賴**：F2 必須先於 F1。沒有 F2，F1 改完也只是把一個沒被守住的敘述換成
另一個沒被守住的敘述——而本集群已經證明，敘述與機制會各自漂移。

### 風險：本集群的既有品質不受此二項影響

逐層機制是可用的、被測試釘住的，且已在乾淨 clone 上驗證。F1／F2 不是回退，
是把已經做好的東西接到使用者身上。

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

鏈的前兩環實測：

```text
釘住的 c3cb81c4 → 243 檔；tests/ doc/ modules/ 各 0
可達性         → refs/remotes/origin/publication-0.4.9 指向同一個 sha
repo 可見性    → PRIVATE
```

## 未解項與 handoff 結論

| 項目 | 處置 |
| --- | --- |
| F2 端到端測試 | 需開票；**先做** |
| F1 README 入口 | 需開票；依賴 F2，且在 repo 公開前無法線上驗證 |
| repo 公開 | owner 決定，不在本審查範圍 |

逐層 `APPROVED`；集群 `CHANGES_REQUESTED`。本審查未修改任何檔案，未動任何 ref，
所有探針已還原，工作區乾淨。
