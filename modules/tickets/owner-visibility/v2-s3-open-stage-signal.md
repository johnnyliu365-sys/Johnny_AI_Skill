# V2-S3｜找回未完成階段的訊號

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（UI 樣式子票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/owner-visibility/v2-s2-two-quiet-states.md`（依賴） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | 無紀錄（早於本欄要求） |
| 實作者 | UI implementation owner |
| 審閱者 | 無紀錄（早於本欄要求） |
| 責任邊界 | `library/local_orchestration/ticket_status_template.py` 與它的測試 |
| 禁止修改 | 任何會與五種狀態色碰撞的顏色 |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

未完成的階段方塊重新有「看這裡」的份量，而且不再與任何狀態色碰撞。

核准的樣張裡，未完成階段是琥珀色外框加粗體——一個真的會抓住視線的訊號。為了解決綠色衝突，階段方塊被整組改成無彩色，當時就講明這是有代價的：外框加粗比琥珀安靜。`DONE` 改成灰色之後，無彩色的階段方塊處境更差了：它現在和一個狀態徽章共用無彩色。

不能重新引入會與五種狀態撞色的顏色，也不要讓未完成方塊比整列的狀態更搶眼——階段是列的細節，不是列的結論。上一輪提過的備案（一個離草綠 45° 以上的階段綠）仍然可用，但那會讓階段方塊重新進入色相競爭；若有不靠色相的做法，優先採用。

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

**N/A reason**：本票只改既有渲染模板內的樣式判斷，不建立新的 UI 組合邊界或依賴注入。

- 實際原始碼路徑：`library/local_orchestration/ticket_status_template.py`
- 公開契約／資料模型：無變更

## TDD 設計

1. 正常行為：未完成階段方塊與完成階段方塊呈現可量測的差異。
2. 規則違反／輸入錯誤：不適用（無外部輸入，純樣式渲染）。
3. 外部失敗／fail-closed：不適用（無外部依賴）。
4. 回歸保護：新差異不與任何狀態色碰撞；階段方塊的視覺響度不超過所在列的狀態徽章。

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
| S3-1 | 未完成方塊與完成方塊的差異可量測且達到設定門檻 | 測試 |
| S3-2 | 不與任何狀態色碰撞 | 沿用色相／無彩測試 |
| S3-3 | 階段方塊不比列的狀態搶眼 | 響度斷言 |

- **反向突變證據**（規則見 `implementation-tdd.md`，本欄只填證據）：`<待填：把兩種方塊做成相同外觀，S3-1 應轉紅；還原後轉綠>`
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（僅前端渲染樣式，無 migration、環境變數或部署影響）。

## 完成回寫

- 實際檔案：`<待填>`
- commit：`<待填>`
- WorkProgress：不適用

```johnny-status
id = V2-S3
title = 找回未完成階段的訊號
state = IN_PROGRESS
stage = D | 設計 | OPEN
stage = T | 測試 | OPEN
```
