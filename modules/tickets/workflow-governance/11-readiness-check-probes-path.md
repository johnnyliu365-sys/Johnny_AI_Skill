# 11｜就緒檢查探測 PATH，而安裝器從不碰 PATH

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理缺陷；同族為本資料夾 04「Skill 敘述了沒有發生的喚醒」） |
| 第一步排查起點 | `skills/johnny-project-takeover/SKILL.md` › `Automation readiness` 第 3、4 點 |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-11`／branch `implement/gov-11-readiness-path` |
| 實作語言 | Markdown（skill 文件）＋ Python 3.11（釘住用的測試） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `82866fb` |
| 實作者 | Sonnet 5 high（owner 指定） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `skills/johnny-project-takeover/SKILL.md` 的就緒檢查段落，與釘住它的測試 |
| 禁止修改 | `install.ps1`（不碰 PATH 是設計，不是缺陷）；`launcher/`；`library/` 下任何產品程式碼；其他 reference |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/SKILL.md
modify = tests/test_workflow_router.py
forbid = install.ps1
forbid = library/
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

新專案的第一份接管報告**不再帶一個假的紅點**。就緒檢查第 3、4 點能真的執行並回傳結果，
而不是因為指令名稱解析不到就宣告「無法證明」。

## 實測到的事實（2026-08-21，0.4.7 已安裝）

SKILL.md 目前把兩個檢查寫成裸指令：

```
3. a runner is running for it (`johnny-router runner status` reports `RUNNING`);
4. a wake capability is proven (`johnny-router wake-capability probe`).
```

裸指令名稱隱含它在 PATH 上。但 `install.ps1` 第 12 行明文宣告這支安裝器
**永不修改 PATH**——那是刻意的隔離保證，不是缺陷，所以裸名稱**永遠解析不到**。

**兩個指令本身是好的。** 用推導路徑跑，兩個都正常回應：

```
launcher\johnny-router.ps1 runner status
  → {"runner_state": null, "status": "NOT_RUNNING"}
launcher\johnny-router.ps1 wake-capability probe
  → {"automatic_wake": false, "channel": "CANDIDATE_INBOX",
     "failure": "NOT_CONFIGURED", "status": "UNAVAILABLE"}
```

所以缺陷不在能力，在**檢查探測了錯的地方**：它問「PATH 上有沒有這個名字」，
而應該問「推導出來的 launcher 路徑跑得出什麼」。

## 錯誤的方向是保守的，但仍然要修

這個缺陷不會造成假綠——它把「可證明的事」報成「無法證明」，方向是安全的。
但它讓**每一個新專案的第一份報告都帶一個不存在的紅點**，而 owner 學會忽略
一個常態性的紅點之後，就會連真的紅點一起忽略。這是 04 的鏡像：04 是敘述沒發生的事，
本票是否認發生得了的事，兩者都腐蝕同一件東西——報告與現實的對應。

## 修法方向（實作者可另擇，但要寫下理由）

第 3、4 點改為指名**推導路徑**，與第 1 點同一個推導來源：
`%LOCALAPPDATA%\JohnnyRouter\launcher\johnny-router.ps1`，且**必須沿用第 1 點已經
承認的 `JOHNNY_ROOT` 覆寫**——第 1 點認得覆寫而第 3、4 點不認得，就是新的同族缺陷。

## TDD 設計

1. 正常行為：就緒檢查段落指名可推導的 launcher 路徑，且該路徑由 root 推導而來。
2. 規則違反／輸入錯誤：段落中不得再出現隱含 PATH 的裸指令形式。
3. 外部失敗／fail-closed：`JOHNNY_ROOT` 被覆寫時，四點檢查指向同一個 root，
   不得第 1 點跟著覆寫、第 3、4 點指向預設位置。
4. 回歸保護：四點檢查的**語意不變**——任一點缺席仍然是「沒有自動化被 arm」，
   本票只改「去哪裡問」，不改「答案怎麼判讀」。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | 推導路徑必須來自 root，不得字串拼接出可被 `JOHNNY_ROOT` 繞開的位置 |
| 2 | null／空字串／陣列 | 是 | `JOHNNY_ROOT` 為空字串與未設定兩者行為必須一致 |
| 3 | 權限繞過 | 否 | 不涉權限判斷 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 純文件與斷言變更 |

## 完成定義與證據

- 由測試釘住：就緒檢查段落不含隱含 PATH 的裸指令，且四點指向同一個 root 推導。
- **反向突變證據**：把第 3 點改回裸指令形式，指名的測試要轉紅；還原後轉綠。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。
  **本票的全套件由審閱者跑，不由實作者跑**：governance 10 同時在跑，兩個行程並行會踩共享
  runtime root（登記簿 C1／B2）。實作者只跑 `tests/test_workflow_router.py`；
  全套件與殘留檢查是**審閱者的未完成義務**，不得因為實作者回報綠就視為已滿足。
- **已代為查證，實作者仍須自行確認**：`SKILL.md` **不在** `_EXPECTED_POLICIES`
  的 digest 釘死清單內（該清單目前是 7 份 `references/*.md`），故本票**不需要 repin**
  `profile.py` 與 `test_workflow_router.py` 的 rev-。動手前自己再確認一次——
  漏掉 repin 是本專案發生過兩次的缺陷。

## 不在本票範圍

把 launcher 加進 PATH（安裝器的隔離保證明文禁止），以及 runner 的實機 arm。

## 正式環境移植 SOP

不適用（skill 文件與測試，無 migration、無新增環境變數）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 11
title = 就緒檢查探測 PATH，而安裝器從不碰 PATH
state = IN_PROGRESS
stage = F | 改為推導路徑 | OPEN
stage = T | 測試釘住 | OPEN
stage = M | 突變驗證 | OPEN
```
