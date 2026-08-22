# 03｜釘住的 sha 與它指向的樹互不相干

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（票 02 的第二階段；缺口由票 02 的實作者誠實標示，審閱者以突變證實） |
| 第一步排查起點 | `tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists`——它只問 commit 存不存在，不問樹裡有什麼 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/plugin-03`／branch `implement/plugin-03-publication-tree` |
| 實作語言 | Python 3.11 |
| 狀態 | `DONE`（釘子綁到樹；**可達性另見票 04**） |
| 共同基準 | 票 02 整合後的 main（worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Opus 5（難票：這是供應鏈的釘子，釘錯的後果是使用者拿到我們沒審過的東西） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 發佈樹的產生步驟、把釘子綁到樹的測試 |
| 禁止修改 | 票 02 落地的 `payload` 宣告內容（本票消費它，不改它）；`windows_package_manifest.py`；任何 skill 的內容 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/plugin_publication.py
create = library/local_orchestration/plugin_publication.py
modify = tests/test_plugin_publication.py
create = tests/test_plugin_publication.py
modify = tests/test_plugin_payload_boundary.py
modify = .claude-plugin/marketplace.json
forbid = .claude-plugin/plugin.json
forbid = library/local_orchestration/windows_package_manifest.py
forbid = skills/
forbid = README.md
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

**照安裝指引裝一次，硬碟上出現的東西等於我們宣告要出貨的東西**——不是「大致上」，
是可以逐檔比對的相等。

## 票 02 留下的確切狀態

票 02 做出了白名單宣告、閉包證明與 39 個 cell，全部正確。但它**只到宣告為止**：

- `payload` 這個 key **Claude Code 不讀**（`--strict` 警告 `Unknown field 'payload'`）。
  它現在的消費者只有我們自己的測試。
- `marketplace.json` 的 `sha` 釘在 `9073ac54`（v0.4.9），而**那棵樹是整個 repo**——
  797 個檔，含 `tests/` 147、`doc/` 177、`modules/tickets/` 196。

所以今天照這份宣告安裝，拿到的仍是全部。票 02 的實作者把這件事寫進回報並附了原型，
**沒有粉飾**——是票 02 的邊界沒有給產生器任何位置，那是審閱者的缺陷。

## 審閱者的突變證據（2026-08-22）

把 `sha` 改釘到 root commit `fcb46045`——**那棵樹只有 3 個檔、完全沒有 `skills/`**：

```
39 passed, 295 subtests passed
```

**零紅。** 一個宣稱要出貨 5 棵樹 7 個檔的 plugin，釘在一個連 `skills/` 都沒有的 commit 上，
整套測試通過。宣告與釘子是兩件互不相干的事實。

這是登記簿 D1（digest repin drift）在新位置再現一次：**證明講的是文件，不是那個成品。**

## 不可讓的性質

1. **產生器讀宣告，不得自帶清單。** 第二份清單就是第二個真相，而兩份必然漂移。
   以測試釘住：改宣告會改變產生的樹。
2. **釘子必須被綁到樹。** 給定 `marketplace.json` 的 `sha`，該 commit 的樹**必須逐檔等於**
   宣告的 payload。審閱者上面那個突變**必須轉紅**——這是本票最低限度的成功條件。
3. **不得信任「操作者有跑過」。** 樹與宣告的相符必須可由測試從 repo 事實重新計算，
   不得依賴任何人手動執行過某個步驟的記錄。
4. **產生發佈樹不得動 `main` 的樹。** main 仍然是完整開發庫。
5. **失敗必須具名且 fail-closed。** 宣告讀不到、樹算不出、sha 不存在、樹與宣告不符——
   四種各自具名。**讀不到不得等於空的。**

## 一件必須一起說清楚的事（不在實作邊界，但會決定指引怎麼寫）

`marketplace add <owner/repo>` **永遠是完整 clone**，跟宣告怎麼寫無關。不 clone 的唯一
路徑是 `marketplace add <指向 marketplace.json 的 raw URL>`（審閱者實測過）。

也就是說**安裝指引那一行是承重的**，不是裝飾。實作者要在回報中明確寫出：
本票落地後，使用者應該打的完整指令是什麼。**README 由審閱者於整合時改**，
但指令內容以實作者實測到的為準。

## TDD 設計

1. 正常行為：由宣告產生發佈樹，內容等於宣告的閉包；`marketplace.json` 的 sha 指向它。
2. 規則違反／輸入錯誤：宣告含被排除的樹 → 具名拒絕；sha 指向的樹多一個檔或少一個檔 → 紅。
3. 外部失敗／fail-closed：宣告檔不存在／不可解碼／sha 不存在 → 各自具名拋出，
   **不得回空集合或預設值**。
4. 回歸保護：票 02 的 39 個 cell 全部不改且維持綠；Level 2 的 bundle 測試不受影響。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | 逐檔比對時 `modules/` 與 `modules/tickets/`、`skills/` 與 `skills-old/` 必須可分 |
| 2 | null／空字串／陣列 | **是** | 空的樹、空的宣告、空的差異集三者各自明確；**「差異集為空」只有在真的相等時才成立** |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | **是** | sha 必須是完整小寫且存在；不得接受縮寫、tag 名或浮動 ref |
| 5 | 錯誤碼是否一致 | **是** | 宣告違反、樹不符、掃描失敗必須是三個可區分的名字 |
| 6 | 例外是否會拋出 | **是** | 任何一項算不出來都必須拋，不得靜默視為相符 |

## 完成定義與證據

- **反向突變證據**：至少三組，且**必須包含審閱者那一組**——把 sha 釘到 `fcb46045`
  （或任何不等於宣告的樹）**必須轉紅**；另外兩組自訂；各指名哪個測試轉紅、還原後轉綠。
- **實際貼出**：照本票落地後的指引裝一次，逐檔比對硬碟上的內容與宣告的 payload，
  貼出差異集為空的證據。
- 端到端安裝驗證**必須在隔離的 `CLAUDE_CONFIG_DIR` 中進行**，不得動 owner 的設定
  （票 02 的實作者用了這個手法，沿用）。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

改 `README.md` 的安裝章節（審閱者於整合時改，內容以本票實測到的指令為準）；
把發佈樹真的推上 GitHub（那需要 owner 明確指示，見下）；
票 02 回報中列出的 shipped prose 死連結（另票，審閱者的清單）。

## 正式環境移植 SOP

發佈樹一旦推上去並被 marketplace 指到，**所有新安裝立刻走它**。因此：
push 由 owner 明確指示；README 的指令與宣告必須同一次 push；
repo 目前是 private，公開前必須先確認這條路徑通。

## 完成回寫

- 實際檔案：`library/local_orchestration/plugin_publication.py`（新增）、
  `tests/test_plugin_publication.py`（新增，38 cell）、
  `tests/test_plugin_payload_boundary.py`（僅改 import，無任何 cell 被動）、
  `.claude-plugin/marketplace.json`（僅改 `sha`）
- commit：`53c6d4e3`，經 `admit_document_mutation` 判為 `INTEGRATED`
- **發佈樹 `b856cf88`**：242 個檔（原 797），零 `tests/`／`doc/`／`modules/`、
  無根 `CLAUDE.md`；parentless 且時間戳固定，因此可重現
- **產生器不自帶清單**：以 AST 走訪自身，斷言沒有任何字串常數是 payload 路徑，
  且其字面值與宣告條目交集為空；行為面則以「改宣告→樹跟著變」的擴/縮測試佐證。
  順手把票 02 測試檔裡重複的 `_FORBIDDEN_PREFIXES` 等收斂到生成器單一處，
  刪 141 行、加 21 行，**無任何 test 方法被改動**
- **SHA-1 不動點**：commit 無法包含一個記載自己 id 的檔案。發佈的那份
  `marketplace.json` 記 40 個零——解析不到任何物件因此 fail closed；
  記上一版的真實 id 會**出貨一個指向 797 檔整包的活釘子**，正是本票要擋的失敗
- **反向突變**：實作者五組，最值得指的是第五組——釘到**上一棵真實的發佈樹**
  （形狀對、內容舊），路徑檢查正確保持綠而內容檢查轉紅，證明綁的是內容不是形狀
- **審閱者打了三道門，兩道是關的**：
  1. 把佔位符換成活的 commit（0.4.9 整包），讓所有內部一致性檢查照樣通過
     → **5 紅**，含 `test_the_published_copy_records_an_id_that_names_nothing`
  2. 逐檔雜湊能否靜默漏掉非 ASCII 路徑（42/242 是中文路徑）
     → 關著（`ls-tree -r -z` ＋ `len(produced) != len(relatives)` 計數守衛）
  3. **刪掉唯一指向 `b856cf88` 的 ref → 零紅，79 passed**
- **第三道門是真的洞，已開票 04。** 釘子綁到了樹，沒綁到可達性；
  `refs/publication/*` 這個 namespace GitHub 不收（`git ls-remote origin` 回 0）
- **實作者回報的 fail-open，值得記登記簿**：`git update-index --add --stdin`
  對被忽略的路徑印 stderr 但**回傳 0**，payload 曾靜默變空；起因是文字模式 stdin
  把 `
` 改寫成 `
`，餵給 git 的路徑帶了尾隨 CR。兩條教訓：
  餵路徑給 git 一律用二進位模式；**零退出碼不是任何東西被暫存的證據**
- 全套件（審閱者執行）：1641 passed、22 skipped、3983 subtests、零 FAILED；
  受閘（`JOHNNY_LIVE_QUAL=1`）：28 passed、1 skipped、零 FAILED


```johnny-status
id = 03
title = 釘住的 sha 與它指向的樹互不相干
state = DONE
stage = G | 由宣告產生發佈樹 | DONE
stage = B | 釘子綁到樹 | DONE
stage = E | 端到端逐檔比對 | DONE
stage = M | 突變驗證（含審閱者那一組） | DONE
```
