# V2-S4｜用詞與欄位名

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（UI／契約用詞子票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/owner-visibility/v2-s3-open-stage-signal.md`（依賴） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `IN_PROGRESS`（改名已派工；用詞裁決仍待 owner，兩者互不阻擋） |
| 共同基準 | 無紀錄（早於本欄要求） |
| 實作者 | `.worktrees/v2-s4`／branch `implement/v2-s4-rename`（一人原子完成改名） |
| 審閱者 | 無紀錄（早於本欄要求） |
| 責任邊界 | 控制面：`ticket_status_pipeline.py`、其契約、工單宣告；UI：`ticket_status_template.py` |
| 禁止修改 | 用詞裁決前不得改任何畫面文案（`完成`／`已通過` 等字樣） |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/ticket_status_pipeline.py
modify = library/local_orchestration/ticket_status_template.py
modify = tests/test_ticket_status_pipeline.py
modify = tests/test_ticket_status_template.py
modify = modules/tickets/owner-visibility/v2-document-sample.json
modify = modules/tickets/owner-visibility/v2-ticket-status-surface.md
modify = tests/test_ticket_status_publish.py
modify = modules/tickets/owner-visibility/v2-s4-naming.md
forbid = modules/tickets/TEMPLATE.md
forbid = library/local_orchestration/document_mutation_gate.py
```

## 使用者拍板與可觀察結果

畫面上的字和資料裡的欄位名，都說出它們真正的意思。

兩件待決事項：

1. **`完成` 這個詞看不出「還沒人審過」。** owner 指定了 `完成`，但 `完成` 和 `已通過` 放在一起時，光看「完成」兩個字並不會讓人想到「這件事還在等審查」——而那正是把兩個狀態拆開所要傳達的資訊。`完成待審` 會說出來。**這一項要 owner 先點頭才能改**，因為那是他選的詞。
2. **這個欄位（舊名意指「在等什麼」）現在裝的是退回原因。** `REJECTED` 用同一個欄位裝「為什麼沒過」，但那不是「在等什麼」。這個名字會誤導之後每一個讀這份資料的人。建議改成 `reason`。這是資料契約的改名。**先前寫的「管線先、UI 後」是錯的**：分兩步只在兩個負責人平行工作時才有意義，由一個人做時，中間那一刻畫面正讀著一個不存在的鍵。改名要**原子落地**——管線、契約、樣本、畫面在同一次變更裡一起改。

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：控制面（契約／管線部分）與 UI implementation owner（畫面部分）。
- reviewer：控制面（Opus 5）；與實作者不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：本票是既有契約欄位與畫面文案的改名，不建立新的 UI 組合邊界或依賴注入。

- 實際原始碼路徑：`library/local_orchestration/ticket_status_pipeline.py`、`library/local_orchestration/ticket_status_template.py`
- 公開契約／資料模型：舊欄位名 → `reason`（待 owner 裁決後執行）

## TDD 設計

1. 正常行為：owner 裁決後，畫面用詞與改名後的 `reason` 欄位在管線、契約、樣本、畫面四處一致。
2. 規則違反／輸入錯誤：不適用（純改名，無新輸入路徑）。
3. 外部失敗／fail-closed：不適用（無外部依賴）。
4. 回歸保護：全庫搜尋舊欄位名，斷言零命中；樣本文件仍能被畫面渲染。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不涉錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 純改名，無執行路徑分支 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| S4-1 | owner 對 `完成` 的用詞給出裁決，並記錄在這張票裡 | 票內文字 |
| S4-2 | 若裁決要改，畫面用詞跟著改 | 測試 |
| S4-3 | 欄位改名後，管線、契約、樣本、畫面四處一致 | 全套件綠，且樣本能被畫面渲染 |
| S4-4 | 沒有任何地方還讀得到舊欄位名 | 全庫搜尋，斷言零命中 |

- **反向突變證據**（規則見 `implementation-tdd.md`，本欄只填證據）：`<待填：裁決落地後補上>`
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（僅內部契約與畫面用詞改名，無 migration、環境變數或部署影響）。

## 完成回寫

- 實際檔案：`<待填>`
- commit：`<待填>`
- WorkProgress：不適用

```johnny-status
id = V2-S4
title = 用詞與欄位名
state = IN_PROGRESS
stage = N | 裁決用詞 | OPEN
stage = R | 欄位改名 | OPEN
```
