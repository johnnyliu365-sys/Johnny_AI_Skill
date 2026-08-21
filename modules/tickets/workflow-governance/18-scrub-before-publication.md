# 18｜公開前清洗：工作樹、歷史、發行資產三層

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（owner 拍板：repo 要公開，先弄乾淨） |
| 第一步排查起點 | 2026-08-21 洩漏審計（本票的「洩漏清單」節）；`tests/staging/plugin_distribution_vita/harness.py:31-32` 是最重的一處 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-18`／branch `implement/gov-18-scrub` |
| 實作語言 | Markdown＋Python 3.11（第一階段）；git filter-repo（第二階段，控制面） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | 綁定 commit（worktree HEAD，派工訊息載明） |
| 實作者 | 第一階段 Sonnet 5 high；第二、三階段控制面（發行工程，比照 D2） |
| 審閱者 | 控制面（Opus 5）＋ owner（公開鍵由 owner 已明示授權） |
| 責任邊界 | 全 repo 的字面清洗（見詞彙對照表）；歷史重寫與 release 重建 |
| 禁止修改 | 任何程式**行為**——本票只換字面，全套件必須維持綠 |
| 環境 | `LOCAL` → 對外（force-push、release 刪建、翻 public） |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = CONTEXT.md
modify = README.md
modify = doc/
modify = modules/
modify = library/
modify = tests/
modify = skills/
modify = .agents/
forbid = library/workflow_router/profile.py
forbid = johnny-install.cmd
```

（`profile.py` 與 wrapper 由控制面在第三階段隨 0.4.9 發行處理；digest 釘死的
reference 若被清洗命中，由控制面依 repin 程序另行處理——第一階段實作者**先回報再動**。）

## 使用者拍板與可觀察結果

repo 翻 public 之後，任何人翻遍**工作樹、全歷史、所有 release 資產**，都找不到
公司名、產品名、金流供應商名、來源專案識別、個人機器路徑。

## 洩漏清單（2026-08-21 審計實測，2026-08-22 控制面複查追加項見 7、8；原始字面
正本已移出本票，另存 repo 外供第二階段 filter-repo 使用，見「詞彙對照表」）

1. **寫死的公司路徑**：`tests/staging/plugin_distribution_vita/harness.py:31-32`
   （由公司產品名兩層目錄與私有目標 repo 名稱串接而成的絕對路徑，共兩條）。
2. **來源專案識別**：`CONTEXT.md` 的授權來源庫清單；plugin-distribution 票 14/15；
   `doc/context/plugin-distribution/main.md`；`doc/requirements/.../REQ-20260802-004.md`。
3. **技術輪廓**：reusable-module-library 票 05/06 與 review 05/06/10、
   `library/金流串接`與 `library/NLP` 各 README——三家金流供應商的名稱、
   來源專案的訂閱模組與 AI 服務層內部識別詞。
4. **個人機器路徑（第一人）**：`README.md`、plugin-distribution 票 14、harness、
   `tests/test_release_pin_guard.py` 的個人使用者家目錄路徑。
5. **已發行資產也洩**：payload 內 library README 同樣含上述名字——
   0.4.0–0.4.8 的所有 release zip 公開即洩。
6. **全歷史**：以上內容存在於歷代 commit，翻 public 即全部可讀。
7. **個人機器路徑（第二人，審計漏掉，2026-08-22 複查追加）**：約 50 個歷史工單的
   worktree／實作者綁定欄位、`doc/context`、`doc/reviews`、reusable-module-library
   README 的路徑限制行，含另一位個人使用者的家目錄路徑。
8. **來源專案通稱（2026-08-22 複查追加）**：`CONTEXT.md`、`library/NLP` 各
   README、review 11 等三十餘處，以產業代稱與空格分寫的完整片語稱呼來源專案 C
   與來源專案 D，未透過本票原已列出的識別詞，第一輪審計未涵蓋。

## 詞彙對照表（描述性索引；原始字面正本已存 repo 外供第二階段 filter-repo 使用，
第一階段依此類別替換——本表不再帶字面，避免本票自身在公開後成為新的洩漏源）

| 類別描述 | 替換 |
| --- | --- |
| 公司產品名（含全大寫變體） | `來源專案A`（英文脈絡 `SourceProjectA`） |
| 私有目標 repo 名稱 | `私有目標repo`（路徑中直接刪除該段） |
| 金流供應商甲的名稱（含中文全稱） | `支付provider甲` |
| 金流供應商乙的名稱 | `支付provider乙` |
| 金流供應商丙的名稱 | `支付provider丙` |
| 來源專案 B 的公司代稱 | `來源專案B` |
| 來源專案 C 的產業代稱與代管應用程式名稱 | `來源專案C` |
| 來源專案 D 的服務代稱（程式識別詞與空格分寫片語兩種寫法） | `來源專案D` |
| 來源專案的 AI 服務層內部識別詞 | `來源專案的AI服務層` |
| 來源專案的訂閱模組內部識別詞 | `來源專案的訂閱模組` |
| 個人使用者家目錄路徑（第一人；含反斜線變體） | `<repo-root>` 或 `%USERPROFILE%` 佔位 |
| 公司產品名的磁碟機路徑寫死片段 | 整行刪除（harness 改為只認環境變數） |
| 個人使用者名（第二人） | `<user>`（僅替換使用者名段，路徑其餘部分保留） |

**明示保留（具名殘留，不是遺漏）**：裸字 `vita` 作為測試 fixture 代號
（`receipt-vita-feature-001` 等）與 `JOHNNY_VITA_ORIGINAL` 環境變數名——原詞
消失後，`vita` 只是一個拉丁字，改名要動 52＋ 處測試 id 而不減任何資訊量。
git author（`johnny.liu365@gmail.com`）保留——與 GitHub 帳號同一身分，公開不增加新資訊。
約 62 檔含 `C:\Users\User\AppData\Local\JohnnyRouter\...` 路徑保留不清（2026-08-22
裁決追加）——`User` 為通用使用者名、`JohnnyRouter` 為本專案自己文件化的安裝根目錄，
公開不洩漏個人資訊，接受不清。

## 三階段

1. **工作樹清洗**（implementer）：照 repo 外原始字面對照表全 repo 替換；harness 改純環境變數；
   驗收＝原始字面（正本存於 repo 外）grep 工作樹**零命中**（含 `.agents/`，**含本票自身**）
   ＋全套件綠。**digest 釘死的檔案被命中就停下回報**，repin 由控制面做。
2. **歷史重寫**（控制面）：`git filter-repo --replace-text` 用 repo 外保存的原始字面對照表正本、
   fresh clone 操作、force-push main、刪除 origin 全部舊 tag、重寫前的完整 mirror 存本機私檔一份。
3. **release 重建**（控制面）：刪除 GitHub releases 0.4.0–0.4.8（資產洩漏，不可留公開）、
   從清洗後的 main 走 D2 發 **0.4.9** 作為第一個公開版、翻 public、
   對**公開後的 repo** 重跑一次審計 grep 作最終驗收。

## TDD 設計

1. 正常行為：全套件綠——清洗只換字面不換行為。
2. 規則違反／輸入錯誤：原始字面（正本存於 repo 外）grep 工作樹零命中，含本票自身。
3. 外部失敗／fail-closed：第二階段前先在 mirror clone 上驗證重寫結果的 grep 零命中，
   才 force-push；第三階段翻 public 前先確認 releases 已刪。
4. 回歸保護：`JOHNNY_VITA_ORIGINAL` 覆寫路徑仍可讓 vita qual 在有原庫的機器上跑。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | 替換不得誤傷子字串（如 `LINE` 不得動到 `BASELINE`／`PIPELINE`）——用完整詞邊界 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 已審計：全歷史零完整 token |
| 5 | 錯誤碼是否一致 | 否 | 不改行為 |
| 6 | 例外是否會拋出 | 否 | 不改行為 |

## 完成定義與證據

- 工作樹、重寫後歷史（所有 commit）、公開後 repo 三層各一次 grep 零命中報告。
- 全套件綠、零殘留。
- 0.4.9 發行完成（D2 兩段式、重新下載驗 digest）。
- 重寫前 mirror 的本機保存位置記入完成回寫。

## 不在本票範圍

memory 目錄（repo 外）；`JohnnyRouter` root（repo 外）；已安裝機器的舊 payload
（隨 0.4.9 更新自然汰換）。

## 正式環境移植 SOP

不適用（本票即發行工程本身）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 18
title = 公開前清洗：三層
state = IN_PROGRESS
stage = S | 工作樹清洗 | OPEN
stage = H | 歷史重寫 | OPEN
stage = R | release 重建與公開 | OPEN
```
