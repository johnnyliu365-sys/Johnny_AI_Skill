# 17｜審閱端的突變必須從另一道門進去

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（審閱規範補強；證據為 2026-08-21 連續五張票的實測） |
| 第一步排查起點 | `skills/johnny-project-takeover/references/review-checks.md` › `Defect categories` 的 `Test truthfulness` 列 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-17`／branch `implement/gov-17-reviewer-mutation` |
| 實作語言 | Markdown（policy reference）＋ Python 3.11（digest repin） |
| 狀態 | `DONE` |
| 共同基準 | `9125a91`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Sonnet 5 high（一般小票，依 `dispatch-model-profile.md` 分層） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `review-checks.md` 的 `Test truthfulness` 列與必要的新段落，加上兩處 digest repin |
| 禁止修改 | 其他 reference；`CodeReview.md`；`library/` 下 `profile.py` 以外的任何檔案 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/references/review-checks.md
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
forbid = skills/johnny-project-takeover/SKILL.md
forbid = CodeReview.md
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

審閱者做反向突變時，**從實作者沒走過的門進去**——因為實作者的突變只能證明
他自己那顆釘子有效，證明不了那顆釘子釘在對的地方。

## 證據：連續五張票，同一個形狀

2026-08-21，五張票的實作**修法全部正確**，第一版的**釘子全部錯位**，而且五次都是
審閱端從另一個方向突變才發現。實作者自己的突變每次都轉紅——那正是問題：
**突變與釘子出自同一個人對「這件事該怎麼壞」的想像。**

| 票 | 實作者的突變（有效） | 審閱者從另一道門進去 | 結果 |
| --- | --- | --- | --- |
| 12 | 拔掉 helper 的保護 | 把**被修好的 cell** 退回缺陷形狀 | 15 passed 零轉紅——釘子釘在模式**副本**上 |
| 13 | 無版本、範圍宣告、注入 runtime lock | 追加一行**矛盾並存**的 `pytest>=8` | 6 passed 零轉紅——解析器抓到第一個就停 |
| 14 | in-tree venv 下退掉修法 | 在 **ASCII venv**（＝整合閘門實際跑的環境）退掉修法 | 32 passed 零轉紅——回歸防護只活在沒人跑的環境 |
| 15 | 拔掉**新增的**兩行 | 拔掉**既有的** `__pycache__/` 行 | 14 passed 零轉紅——探測被 `*.py[cod]` 重疊遮蔽 |
| P5 | 三組（放行開著的 claim 等） | 把重複 claim 檢查改成只擋 `CLAIMED` | 2 紅（通過），但撞出第二個未具名的防線 → governance 16 |

五種錯位形狀彼此不同——**副本**、**首個匹配**、**環境限定**、**重疊遮蔽**、**呼叫端可偽造**
——所以這不是某個實作者的習慣問題，是「自己驗自己」這個結構的必然。

## 要寫進 reference 的內容（措辭由實作者定，性質不可讓）

1. **審閱者必須自己做至少一組反向突變**，且**入口必須與實作者回報的那幾組不同**。
   跟實作者同向重跑一次只是複驗他的結論，不是獨立證據。
2. **零轉紅是發現，不是通過。** 審閱者的突變沒有任何 cell 轉紅時，預設結論是
   「這個性質沒有被釘住」，不是「程式碼很穩固」。
3. 四個已知的錯位形狀要具名列出（副本、首個匹配、環境限定、重疊遮蔽），
   作為「從哪道門進去」的起點清單——不是窮舉，是提示。
4. **釘在被走的那條路上**：性質要釘在 production 實際經過的 choke point，
   不是釘在測試自己身上的模式副本。

## TDD 設計

1. 正常行為：`review-checks.md` 含上述四點，且 `Test truthfulness` 列指向新段落。
2. 規則違反／輸入錯誤：不適用（policy 文件，無輸入面）。
3. 外部失敗／fail-closed：不適用。
4. 回歸保護：**digest 重釘後 router 測試仍綠**；其他六份被釘的 reference 的 rev- 不得變動。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 無輸入面 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | **是** | rev- 與 content_digest 必須精確相等比較，前 16 hex 不得以前綴匹配蒙混 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 純文件與常數變更 |

## 這張票最容易被漏掉的一步

**`review-checks.md` 是 digest 釘死的政策檔。** 改內容**必須**同步重釘兩處：

- `library/workflow_router/profile.py` 的 `SkillReference(reference_id="review-checks", ...)`
- `tests/test_workflow_router.py` 的 `_EXPECTED_POLICIES` 對應項

計算方式：對檔案內容做 **LF 正規化**後取 sha256；
`content_digest` ＝ `sha256_` ＋ 完整 64 hex，`source_revision` ＝ `rev-` ＋ 前 16 hex。
目前值是 `rev-4b8527305609194a`。

**這一步控制面自己漏過兩次**（`context-routing.md`、`implementation-tdd.md`），
兩次都是改完就 commit、沒跑套件。**改完先跑 router 測試再說。**

## 完成定義與證據

- **反向突變證據**：把 repin 後的 rev- 改回舊值，`test_workflow_router.py` 要轉紅；
  還原後轉綠。這同時證明釘子有效與 repin 正確。
- 另一組：從 reference 移除新增的其中一點，指名的測試要轉紅。
- 實作者只跑 `tests/test_workflow_router.py`；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

- **全套件責任**：兩張票並行實作，實作者只跑本票邊界內的測試檔；全套件與殘留檢查由審閱者於整合前執行（比照 governance 11 的責任轉移，這是審閱者的未完成義務，不得因實作者回報綠即視為滿足）。

## 不在本票範圍

`CodeReview.md` 的審閱進場／證據／結論規範（那是它的職責，本票只補專門檢查表）；
把這條規則變成自動化檢查（規則先寫下來，工具化另議）。

## 正式環境移植 SOP

不適用（policy 文件與其 digest；隨下次發行進 bundle，不影響已安裝 runtime 的行為）。

## 完成回寫

- 實際檔案：`skills/johnny-project-takeover/references/review-checks.md`、`library/workflow_router/profile.py`、`tests/test_workflow_router.py`
- commit：`ca384c1`，經 `admit_document_mutation` 判為 `INTEGRATED`
- **落點**：新增 `## Reviewer counter-mutation` 段落，`Test truthfulness` 列指向它；四點各自成條，四種錯位形狀（Copy／First match／Environment-scoped／Overlap-masking）具名列出
- **repin 做對了**：`rev-4b8527305609194a` → `rev-0589a1d06beafc2b`，兩處一致，**審閱者獨立重算驗證相符**。這是控制面自己漏過兩次的步驟
- **反向突變**：實作者兩組（只還原 profile.py 的 rev-；移除第 2 點不重釘）——兩組都經 digest 轉紅
- **審閱者從第三道門進去，零轉紅**：把四點**整段反轉**（改成「重跑實作者的突變就足夠」「零轉紅代表釘得很穩」），並把兩處 digest **正確重釘** → **57 passed，零轉紅**
- **依本票自己剛寫下的規則，預設結論是「沒有被釘住」，追查後判為具名限制而非缺陷**：digest 是變更偵測器，不是內容斷言；真正擋住未授權改寫的是**整合閘門**——任何 candidate 要動 `review-checks.md`，票的 `johnny-boundary` 必須宣告 `modify`，否則 `admit_document_mutation` 拒絕（governance 08）。七份被釘的 reference 全數如此，要求本票獨自加內容斷言是超出專案慣例
- **仍然成立的限制**：一張宣告了 `modify = review-checks.md` 的票可以改寫這份規範而測試不反對。這與任何檔案相同，記錄在案而非假裝不存在
- **審閱者自己的錯**：第一次突變的 repin regex 改到了**所有** policy 條目，紅的是 shared-context 而非 review-checks——工具壞了不是發現。改成逐條目定點替換（加「舊值必須恰好出現一次」斷言）後才取得可信結果
- 全套件（受閘測試開啟）：1404 passed、1 skipped、3254 subtests、零 FAILED、無殘留

```johnny-status
id = 17
title = 審閱端的突變必須從另一道門進去
state = DONE
stage = W | 寫進 reference | DONE
stage = R | digest 重釘 | DONE
stage = M | 突變驗證 | DONE
```
