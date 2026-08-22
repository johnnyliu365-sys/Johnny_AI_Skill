# 02｜plugin 出貨的是整個開發庫

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（owner 拍板：「安裝指引不該是要他們 clone，而是直接可以安裝」） |
| 第一步排查起點 | `.claude-plugin/marketplace.json` 的 `"source": "./"`——那一行的意思是「這個 repo 的全部」 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/plugin-02`／branch `implement/plugin-02-payload-boundary` |
| 實作語言 | JSON 宣告 ＋ Python 3.11（測試） |
| 狀態 | `OPEN` |
| 共同基準 | `5bfdc2a8`（worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Opus 5（難票：出貨閉包算錯的後果在本機看不見——我們永遠有完整 repo） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | plugin 的出貨宣告與其測試 |
| 禁止修改 | `windows_package_manifest.py`（Level 2 的 bundle 清單）；skill 的**規則內容**（只准改「去哪裡找檔案」的位置字句）；`README.md`（由審閱者於整合時改） |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = .claude-plugin/marketplace.json
modify = .claude-plugin/plugin.json
modify = tests/test_plugin_payload_boundary.py
create = tests/test_plugin_payload_boundary.py
forbid = library/local_orchestration/windows_package_manifest.py
forbid = README.md
modify = skills/apply-reusable-modules/SKILL.md
modify = skills/johnny-project-takeover/SKILL.md
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

裝 Level 1 的人，硬碟上只出現他要用的東西，而且那份東西**釘在一個具名版本上**。
他不會拿到我們的測試、我們的 runtime、我們的治理票，也不會拿到 89 個 commit 的開發歷史。

## 現況（2026-08-22，審閱者在本機實測）

`claude plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill` 執行的是**完整 git clone**。

| 落地內容 | 大小 | 使用者需要嗎 |
| --- | --- | --- |
| `tests/` | 3.1 MB | 否 |
| `library/` | 2.2 MB | 否（那是 Level 2 的 runtime） |
| `modules/` | 2.1 MB | 部分（含**全部治理票**） |
| `doc/` | 1.4 MB | 否 |
| `.git/` | 2.6 MB／89 commits | 否 |
| **`skills/` ＋ `commands/`** | **131 KB** | **是——這才是 plugin** |

而且該 clone 停在 `4cbc146`（0.4.7），不會自己更新。

## 這是同一個 repo 的兩條出貨路徑，只有一條有清單

`windows_package_manifest.py:24` 已經把 Level 2 管住了：

```python
_PAYLOAD_TREE_ROOTS: Final[frozenset[str]] = frozenset({"library", "skills"})
```

它**明確排除 `tests`**。Level 1 沒有等價物——`"source": "./"` 就是「剩下的全部」，
於是 plugin 出貨的正是 bundle 刻意排除的東西。**不是誰寫錯了，是這條路徑從來沒有被宣告過。**

## 審閱者實測的機制篩選（2026-08-22，已在 owner 本機跑過並全數還原）

實作者不必重跑這幾條，但採用任何一條前必須自行複驗。

| 機制 | 實測結果 | 判定 |
| --- | --- | --- |
| `marketplace add <owner/repo>` | 完整 git clone，12 MB ＋ 89 commits | 現況，就是要換掉的 |
| `marketplace add <raw URL 到 marketplace.json>` | **成功，不 clone**，快取 4 KB | 可用 |
| 承上，plugin `"source": "./"` | `ENOTDIR`——相對路徑指到檔案 | **不相容**，必須換 source 形式 |
| `"source": {"source":"url","url":"…github….git","sha":…}` | 安裝成功、**無 `.git`**、釘在 sha | 可用，但仍出貨整棵樹 |
| 同上但 `url` 指向 `file://` 本地 repo | **走 clone**：`.git` 在、12 MB、開發物全在 | 行為隨 URL 形式而異，**不得假設** |
| `.gitattributes` 的 `export-ignore` | `git archive` 層**有效**（tests／doc／tickets 歸零）；`file://` 路徑**完全不吃** | **不採用**——理由見下 |

### 為什麼 `export-ignore` 不採用

兩個理由，第二個才是決定性的：

1. 它只在 archive 路徑生效。實測 `file://` 走 clone 時完全無效，代表**生效與否取決於
   我們控制不了的取得方式**。
2. **它是黑名單。** 本票不可讓性質第 1 條要的是「列舉」——`export-ignore` 的語義是
   「repo 剩下的全部，扣掉這幾個」。明天新增一個開發用目錄，它會**靜默出貨**。
   那正是現在這個缺陷換一件衣服。

### 因此建議的落點（實作者可推翻，但必須論證）

**由白名單產生一條發佈分支**，marketplace 以釘住的 sha 指向它。白名單與
`_PAYLOAD_TREE_ROOTS` 同形但各自獨立，於是「新目錄預設不出貨」，而不是「新目錄預設出貨」。
產生步驟與既有 bundle 的清單機制是同一個形狀——那是現成的前例。

## 實測的閉包（審閱者量的，實作者須驗證）

| 類別 | 大小 | 判定 |
| --- | --- | --- |
| `skills/` ＋ `commands/` ＋ `.claude-plugin/` | 139 KB | **必須** |
| 根目錄 `*.md`（`SKILL.md:14` 硬寫 `../../Workflow.md`） | 116 KB | **必須** |
| `library/**/*.md`（`MODULE_CATALOG` ＋ 各模組 README） | 107 KB | **必須** |
| `modules/spec/` ＋ `modules/element/` ＋ `template/` | 280 KB | **必須** |
| `library/**/*.py` | 2.1 MB | **待實作者裁決**——`module-catalog-routing.md` 的路徑終點是「public API → exact contract」，若目錄卡片要能落到真實契約就需要它；若只需索引則不需要 |
| `tests/` 3.1 MB、`modules/tickets/` 1.9 MB、`doc/` 1.4 MB、`.git` 2.6 MB | 9.0 MB | **不可達，一律不出貨** |

不含 `library/**/*.py` 時約 **640 KB**；含則約 **2.7 MB**。兩者都遠小於現在的 12 MB。

## 一個必須一起改的敘述缺陷

`skills/apply-reusable-modules/SKILL.md:12` 目前寫著：

> Locate the checked-out `Johnny_AI_Skill` repository containing `library/MODULE_CATALOG.md`.

**這句話把「整個 repo 在硬碟上」寫成了 skill 的前提**——所以現況不是宣告寫漏了，
是 skill 的敘述與宣告互相支撐。只改宣告而不改這句，skill 會去找一個不存在的 checkout。
`skills/johnny-project-takeover/SKILL.md:14` 的 `../../Workflow.md` 同理，需確認新版面下仍成立。

只准改「去哪裡找」，**不得改任何規則內容**——以 diff 逐行說明每一處改動屬於位置而非規則。


## 最容易做錯的地方：出貨閉包

skills 會讀 `AGENTS.md`、`Workflow.md`、`Defined_wayfinder.md`、`template/`、
以及 `modules/` 的一部分。**排掉一份 skill 實際會讀的檔案，plugin 就對外壞掉，
而我們在本機永遠看不到**——因為我們手上一直有完整 repo。

所以本票的核心不是「刪掉大的」，是**證明宣告出去的集合對 skill 的實際引用是封閉的**。

## 不可讓的性質

1. **出貨內容必須是列舉的**，不得是「repo 剩下的全部」。
2. **閉包必須被測試證明**：對宣告的 payload 掃出 skill／command 的所有檔案引用，
   任一引用落在 payload 之外 → 紅。**不得以「本機跑得起來」代替**。
3. **`tests/`、`doc/`、`modules/tickets/` 不得出現在 plugin 出貨內容中**，以測試釘住。
4. **版本必須釘住**：出貨宣告帶具名 sha 或 tag，不得是浮動的 `main`。
5. **兩份清單各自獨立**：Level 1 的宣告與 `_PAYLOAD_TREE_ROOTS` 不得共用一份資料而
   讓改一邊靜默改另一邊；各自被各自的測試釘住。
6. **既有安裝不得被靜默破壞**：改法若使既有 `extraKnownMarketplaces` 宣告失效，
   必須明說並寫進遷移步驟。

## TDD 設計

1. 正常行為：宣告的 payload 含 `.claude-plugin/`、`skills/`、`commands/` 與其閉包；查得到釘住的版本。
2. 規則違反／輸入錯誤：payload 宣告含 `tests/`／`doc/`／`modules/tickets/` → 紅；版本欄位為浮動 ref → 紅。
3. 外部失敗／fail-closed：**引用掃描讀不到某個 skill 檔 → 具名失敗，不得當作「零引用」通過**
   （「讀不到 ≠ 空的」，登記簿 C 族）。
4. 回歸保護：`test_antigravity_registration.py` 與既有 `test_plugin_distribution_*` 全部不改且維持綠。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | `modules/` 與 `modules/tickets/` 必須可分；前綴比對不得讓 `skills-old/` 混進 `skills/` |
| 2 | null／空字串／陣列 | **是** | 引用掃描結果為空，必須能區分「真的沒有引用」與「檔案讀不到」 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | **是** | 釘住的 sha 必須是完整且存在的 commit，不得接受縮寫或不存在的值 |
| 5 | 錯誤碼是否一致 | 是 | 閉包違反與宣告違反必須是兩個可區分的名字 |
| 6 | 例外是否會拋出 | **是** | 掃描失敗必須拋，不得回空集合 |

## 完成定義與證據

- **反向突變證據**：至少三組——把 `tests/` 加回 payload、讓引用掃描在讀不到檔案時回空集合、
  把釘住的 sha 換成浮動 ref；各指名哪個測試轉紅、還原後轉綠。
- **實際貼出改動前後使用者硬碟上的差異**（大小、目錄清單、是否含 `.git`）——本票的產出是那個差異。
- 至少一次**真正的端到端安裝**：以改動後的宣告 `marketplace add` ＋ `plugin install`，
  驗證兩個 skill 與兩個 command 都載入得起來，並**在測完後還原 owner 的安裝**。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

改 `README.md` 的安裝章節（**由審閱者於整合時改，且必須在機制落地之後**——
先寫「直接安裝」而機制還在 clone，就是 governance 04 那一族：文件描寫一個不存在的機制）；
Level 2 bundle 的任何改動；把 payload 搬進子目錄的 repo 重構若實作者論證後不採用 `git-subdir`。

## 正式環境移植 SOP

宣告改動一經 push 即對所有新安裝生效——**這是少數不需要發行就會影響公開使用者的改動**。
因此整合後的 push 必須由 owner 明確指示，且 README 與宣告必須同一次 push。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 02
title = plugin 出貨的是整個開發庫
state = OPEN
stage = D | 出貨閉包 | OPEN
stage = P | 宣告與釘版 | OPEN
stage = E | 端到端安裝驗證 | OPEN
stage = M | 突變驗證 | OPEN
```
