# V2-S1｜完成改灰色

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（UI 樣式子票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/owner-visibility/v2-ticket-status-surface.md`（母票 V2，五狀態與色票定義所在） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `DONE` |
| 共同基準 | 無紀錄（早於本欄要求） |
| 實作者 | UI implementation owner |
| 審閱者 | 無紀錄（早於本欄要求） |
| 責任邊界 | `library/local_orchestration/ticket_status_template.py` 與它的測試，只有這兩個 |
| 禁止修改 | 本票範圍外的其他檔案；下一張票 V2-S2 排在本票之後（等色票定案再動） |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

`DONE` 從黃底改成灰色，而且改完之後五種狀態仍然彼此分得出來。

灰色不是一個安全的顏色，這是本票的難處所在：

- **灰 vs 白。** `NEEDS_OWNER` 是白色。兩個都是無彩色，只剩明度可以分辨，而白卡片上的白徽章量過是 1.00:1。灰色徽章不能落在讓這兩個看起來像同一件事的位置。
- **灰 vs 階段方塊。** 上一輪為了解決綠色衝突，階段方塊被改成無彩色。現在 `DONE` 也是無彩色，同一列裡會出現「灰徽章＋灰方塊」，而這兩者意思完全不同——徽章講的是整張票的裁決，方塊講的是某個階段做完沒有。它們不能讀起來像同一套詞彙。

怎麼解由實作者決定，但兩組都必須用測試釘住，不能只靠肉眼。順帶一提：黃色離開狀態色票之後，警示三角就是全頁唯一的黃色，上一輪提的「兩個不同意思共用同一色系」自動消失，驗收時一併確認。

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：UI implementation owner。
- reviewer：控制面（Opus 5）；與實作者不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：本票只改既有渲染模板內的配色與樣式判斷，不建立新的 UI 組合邊界或依賴注入。

- 實際原始碼路徑：`library/local_orchestration/ticket_status_template.py`
- 公開契約／資料模型：無變更（見 V2 母票的 document／ticket 契約）

## TDD 設計

1. 正常行為：`DONE` 徽章渲染為灰色，其餘四種狀態維持既有渲染，五者兩兩仍可分辨。
2. 規則違反／輸入錯誤：不適用（無外部輸入，純樣式渲染）。
3. 外部失敗／fail-closed：不適用（無外部依賴）。
4. 回歸保護：既有十組徽章／底色對比門檻（≥4.5:1）不因本次改色而破。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不涉錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 純樣式渲染，無執行路徑分支 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| S1-1 | `DONE` 是灰色，五種狀態兩兩仍可分辨 | 既有的色相測試加上明度測試；無彩色的那幾個要靠明度而非色相 |
| S1-2 | 灰徽章與白徽章的對比達到自訂門檻 | 測試，門檻寫在斷言裡不是註解裡 |
| S1-3 | 狀態徽章與階段方塊不會被誤讀成同一套詞彙 | 結構或樣式上的斷言 |
| S1-4 | 十組徽章／底色對比仍 ≥4.5:1 | 既有測試沿用 |

- **反向突變證據**（規則見 `implementation-tdd.md`，本欄只填證據）：S1-2——把灰色調成與白色相近，對比測試轉紅；還原後轉綠。
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（僅前端渲染樣式，無 migration、環境變數或部署影響）。

## 完成回寫

- 實際檔案：`library/local_orchestration/ticket_status_template.py`
- commit：無紀錄（早於本欄要求）
- WorkProgress：不適用

```johnny-status
id = V2-S1
title = 完成改灰色
state = DONE
stage = C | 配色 | DONE
stage = T | 測試 | DONE
```
