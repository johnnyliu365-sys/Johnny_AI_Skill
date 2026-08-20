# V2-S2｜兩個安靜的狀態要能不靠顏色分辨

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（UI 樣式子票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/owner-visibility/v2-s1-done-goes-grey.md`（依賴：色票定案前不要動） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `DONE` |
| 共同基準 | 無紀錄（早於本欄要求） |
| 實作者 | UI implementation owner |
| 審閱者 | 無紀錄（早於本欄要求） |
| 責任邊界 | `library/local_orchestration/ticket_status_template.py` 與它的測試 |
| 禁止修改 | 任何已定案的顏色；差異只能來自形狀、邊框、位置或密度 |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

`APPROVED` 和 `IN_PROGRESS` 不再只差顏色。

owner 連續兩輪提出這個缺口：三個需要人動手的狀態都已經有形狀差異（三角形、填滿、色條），但這兩個「不需要動作」的狀態只差藍與綠——對於分不出這兩個色相的人，這頁有兩種狀態是同一種。風險低不代表不用做：這頁的全部價值就是不用讀字也能分辨，留一半不成立就是留一半。

不要動任何已定案的顏色，差異要來自形狀、邊框、位置或密度，不是換色；也不要把 `APPROVED` 做得比需要人動手的狀態更搶眼——已經通過的東西應該是頁面上最安靜的。

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

1. 正常行為：`APPROVED` 與 `IN_PROGRESS` 兩種狀態呈現可辨識的非顏色差異。
2. 規則違反／輸入錯誤：不適用（無外部輸入，純樣式渲染）。
3. 外部失敗／fail-closed：不適用（無外部依賴）。
4. 回歸保護：五種狀態在灰階（無顏色資訊）下仍兩兩可分辨；`APPROVED` 的視覺響度不超過任一需動作狀態。

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
| S2-1 | 兩個狀態有顏色以外的差異 | 結構斷言，不是文案斷言 |
| S2-2 | 五種狀態在灰階下仍兩兩可分 | 測試：把顏色資訊拿掉之後仍有區別 |
| S2-3 | `APPROVED` 不比任何需要動作的狀態搶眼 | 沿用既有的響度斷言 |

- **反向突變證據**（規則見 `implementation-tdd.md`，本欄只填證據）：S2-1——移除新增的差異，測試轉紅；還原後轉綠。
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（僅前端渲染樣式，無 migration、環境變數或部署影響）。

## 完成回寫

- 實際檔案：`library/local_orchestration/ticket_status_template.py`
- commit：無紀錄（早於本欄要求）
- WorkProgress：不適用

```johnny-status
id = V2-S2
title = 兩個安靜的狀態要能不靠顏色分辨
state = DONE
stage = D | 設計 | DONE
stage = T | 測試 | DONE
```
