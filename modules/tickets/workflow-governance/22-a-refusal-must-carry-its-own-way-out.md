# 22｜拒絕必須帶著自己的出口

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（owner 拍板：公開之後，撞牆的人不一定是資深工程師） |
| 第一步排查起點 | `install.ps1` 的 `Write-TypedResult`（只有 `Status` 與 `Code` 兩個參數——結構上沒有地方放解方） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 ＋ PowerShell（安裝器） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5）＋ owner（本票定義的分類會約束往後每一張票） |
| 責任邊界 | 新增 `library/local_orchestration/refusal_guidance.py` 與其測試；`install.ps1` 的輸出結構；**首批**具名拒絕的分類 |
| 禁止修改 | 任何拒絕的**判定邏輯**——本票只加「這個拒絕之後怎麼辦」，不改「什麼時候拒絕」 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/refusal_guidance.py
create = library/local_orchestration/refusal_guidance.py
modify = tests/test_refusal_guidance.py
create = tests/test_refusal_guidance.py
modify = install.ps1
modify = tests/test_one_click_installer.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/control_plane_mutation.py
forbid = library/local_orchestration/dispatch_session.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

撞到拒絕的人拿得到**下一步**，而不只是一個代碼。而且**agent 知道自己該不該動手**——
因為每個拒絕都宣告了它屬於哪一類。

## 為什麼現在做，而且排在省 token 之前

repo 公開了。裝這套東西的人不一定是資深工程師，可能是 vibe coder。他今天雙擊
`johnny-install.cmd`、把檔案放在自己專案資料夾裡，看到的字面上就是這一行，然後視窗關掉：

```json
{"status":"BLOCKED","code":"INSTALL_BLOCKED_INSIDE_REPOSITORY"}
```

他猜不到「要換一個不是 git repo 的資料夾」——那是他不可能知道的規則。而
`Write-TypedResult` 只有 `Status` 與 `Code` 兩個參數，**結構上連想加解方都加不進去**。

## 真正的讀者是 agent，這決定了設計

這是一套 AI agent 控制平面。vibe coder 的體驗被 Claude Code／Codex 中介——**他不會讀
`RULE_AND_SUBJECT_IN_ONE_CHANGE`，agent 會。**

所以目標不是「把訊息寫親切」，是**讓拒絕帶著足夠的結構，使 agent 知道自己能不能處理**。

## 三個類別，混淆會出事

| 類別 | agent 該做的 | 例 |
| --- | --- | --- |
| `AGENT_MAY_RESOLVE` | 做掉，告知一聲 | 工作樹不乾淨 → commit／stash；分支不對 → checkout |
| `OWNER_MUST_DECIDE` | 停下，列出需要人給的東西 | `OWNER_INPUT_REQUIRED`；要不要 `git init` |
| `NEVER_AUTO_RESOLVE` | 停下並解釋，**繞過即災難** | `DIGEST_MISMATCH`、邊界違反、`POLICY_REPIN_STALE` |

**第三類是本票的重點。** 一個「樂於助人」的 agent 遇到 `DIGEST_MISMATCH` 去重算 digest，
就徹底廢掉整條供應鏈檢查——而且它會回報「已解決」。使用者看不出發生了什麼。

那是 governance 04 那一族換一個身分：**這次說謊的不是我們的文件，是我們沒攔住的
那個熱心 agent。** 目前三類長得一模一樣（一個代碼字串），所以 agent 只能猜，
而猜錯第三類的代價最高。

## 範圍：先建機制，覆蓋會被撞到的

全庫有 **47 個 `Failure` enum**。一次全部分類會變成永遠做不完的票。本票只做：

1. **機制**：分類與指引的資料結構、查詢入口、以及「未分類即紅」的檢查器。
2. **首批覆蓋**——使用者與 agent 真的會撞到的三處：
   - `install.ps1` 的全部 BLOCKED 代碼（**含輸出結構**，目前放不下解方）
   - `document_mutation_gate` 的 `DocumentMutationFailure`
   - `control_plane_mutation` 的 `ControlPlaneMutationFailure`
3. **未覆蓋者明確列出**：檢查器要能回報「哪些 enum 尚未分類」，且該清單**不得為空卻通過**
   ——未覆蓋是已知狀態，不是隱藏狀態。

其餘 44 個 enum 由後續票分批接手（見「不在本票範圍」）。

## 不可讓的性質

1. **分類不得有預設值。** 新增一個拒絕代碼而未分類 → 檢查器紅。不得因為漏填就自動
   歸入最寬鬆的類別。
2. **`NEVER_AUTO_RESOLVE` 的指引不得包含繞過方法。** 它的下一步是「停下並向人解釋」，
   不是「這樣可以跳過」。以測試釘住：該類的指引文字不得出現繞過性動詞。
3. **本票不改任何判定邏輯。** 什麼時候拒絕完全不動；只加拒絕之後的事。
   以全套件維持綠且既有拒絕的 enum 值一字不變證明。
4. **指引與代碼同處**——不得放在另一份文件裡靠人同步。分類是程式碼裡的資料。

## TDD 設計

1. 正常行為：給定一個已分類的代碼，查得到類別與下一步。
2. 規則違反／輸入錯誤：未分類的代碼 → **具名失敗**，不得回傳預設類別；
   `NEVER_AUTO_RESOLVE` 帶繞過性指引 → 檢查器紅。
3. 外部失敗／fail-closed：分類表讀不到 → 具名拒絕，不得退化成「全部當可解決」。
4. 回歸保護：三處首批目標的既有 enum 值與判定行為完全不變；全套件綠。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑 |
| 2 | null／空字串／陣列 | **是** | 空指引、空分類表、未覆蓋清單為空 三者各自明確；**未覆蓋清單為空不得等於「全部已分類」除非真的如此** |
| 3 | 權限繞過 | **是** | `NEVER_AUTO_RESOLVE` 的指引不得成為繞過說明書 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | **是** | 既有代碼值一字不得變——外部已經在讀它們 |
| 6 | 例外是否會拋出 | 是 | 查詢失敗 fail-closed |

## 完成定義與證據

- **反向突變證據**：至少三組——讓未分類代碼取得預設類別、讓 `NEVER_AUTO_RESOLVE`
  的指引通過繞過性文字檢查、讓未覆蓋清單被靜默清空；各指名哪個測試轉紅、還原後轉綠。
- **實際貼出 vibe coder 現在會看到什麼 vs 修改後會看到什麼**——本票的產出是那個差異。
- 安裝器輸出的格式變更**不得破壞既有解析**：`test_one_click_installer.py` 有解析它的
  cell，新增欄位而非改變既有欄位。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

其餘 44 個 `Failure` enum 的分類（分批另票；本票的檢查器負責讓它們**可見**）；
把指引接進 skill 的敘述層（讓 agent 在對話裡照著說——另票）；
指引的多語化。

## 正式環境移植 SOP

安裝器輸出結構變更會出現在下一個發行的 bundle 中。既有欄位不變、只增不改，
所以舊的解析方式仍然有效——這一點由 `test_one_click_installer.py` 的既有 cell 擔保。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 22
title = 拒絕必須帶著自己的出口
state = IN_PROGRESS
stage = M | 分類機制 | OPEN
stage = C | 首批覆蓋三處 | OPEN
stage = X | 突變驗證 | OPEN
```
