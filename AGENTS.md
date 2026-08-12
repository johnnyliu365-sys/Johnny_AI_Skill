# AI 協作入口與索引

> 本檔負責導覽、啟動規則與原始碼型別的 P0 要求。唯一工作標準以 [Workflow.md](Workflow.md) 為準；Code Review 的唯一實際驗證標準以 [CodeReview.md](CodeReview.md) 為準。不得在本檔或其他 Agent 指引建立競爭的流程或審閱規則。

## 目前 Bootstrap 邊界

本次建立規範時，僅允許維護 `AGENTS.md`、`Workflow.md` 與 `CodeReview.md`，不得新增、複製、搬移或刪除任何其他檔案。`template/` 是唯讀參考來源，不是本次要部署的產物。

未來若專案負責人明確啟用完整文件結構，才依 `template/README.md` 建立正式產物；未經明確授權，不得自行建立目錄、規格、工單、Context、ADR 或報告檔。

## 第一個必讀：唯一流程

在讀取程式碼、需求、資料、秘密或執行任何工具前，Agent 必須依序：

1. 閱讀 [工作流程圖](Workflow.md#workflow-flow)，確認目前關卡。
2. 完整閱讀 [Workflow.md](Workflow.md) 的適用章節與完成條件。
3. 檢查使用者本次授權、既有專案文件與目前工作區狀態。

流程圖只用來定位；完整 `Workflow.md` 才是每一關的強制規則。兩者不可互相取代。

<a id="p0-source-type"></a>

## P0：原始碼型別要求

此為所有實作與 Code Review 必須遵守的阻擋規則；任何違反均不得進入 commit、下一張 ticket 或交接。

- 所有原始碼必須以 **C++ 概念可讀的強型別**生成：不要求一律使用 C++，但必須讓讀者能從明確型別理解資料的意義、可否為空、輸入輸出與領域狀態。
- 變數、欄位、函式參數與回傳值、API／事件契約及領域模型必須使用具名、明確且可檢查的型別；以 enum、值物件、DTO 或等價模型表達有限狀態與領域概念。
- 禁止以 `any`、隱含型別、未驗證的動態物件或字串慣例掩蓋資料契約。外部輸入如不可避免為動態資料，必須在邊界立即驗證、正規化並轉換為強型別，且不得向內層傳遞未驗證資料。
- 使用的語言或工具必須啟用其可用的嚴格型別檢查；具體執行與分層規則依 [實作流程](Workflow.md#implementation) 辦理。
- 本檔與 `Workflow.md`、`CodeReview.md` 的文件歸屬、插件隔離及 target project 零複製規則，唯一依據 [Workflow.md 的「治理文件歸屬與插件隔離」](Workflow.md#governance-document-ownership)；不得在本檔另建競爭規則。

Policy／response P0：政策讀取只能在 ephemeral boundary 產生 metadata-only
結果，不得把原文放進 Router model、formatter、telemetry 或 error。固定
dispatch response 必須由同一個 Private Router 的 live pending descriptor
綁定 ticket、reviewed handoff、commit 與具名 implementation owner；複製、
偽造、replay、mismatch 或舊 `APPROVAL_GRANTED -> IMPLEMENT` 路徑一律
`HALT`，只有 Router-owned plan 可以產生固定回應。

## Workflow 導覽

Router anchor: `#workflow-router`; implementation role anchor: `#role-boundary`.

| 目前情境 | 必讀章節 | 允許的下一步 |
| --- | --- | --- |
| 流程事件、交付階段、context 或 skill／Agent 選擇 | [流程 Router](Workflow.md#workflow-router) | 讀取 Profile，解析最小 Context 視圖與唯一合法的下一步 |
| 尋找可重用原始碼模組 | [模組選擇卡](library/MODULE_CATALOG.md)／`$apply-reusable-modules` | 先選最少 READY 模組，再回到本流程取得採用與實作授權 |
| 需求、Bug、正式 UI 或邊界不清楚 | [需求釐清](Workflow.md#discovery) | `wayfinder → grill-with-docs` |
| 需求、UI、資料契約或權限已改變 | [變更控制](Workflow.md#change-control) | 影響分析、更新 Context、重走核准閘門 |
| 準備定義可驗收功能 | [規格](Workflow.md#specification) | 建立／修訂 SPEC，等待核准 |
| 規格已核准，準備分工 | [工單](Workflow.md#tickets) | 垂直切片、指定責任；依唯一交付確認開立 ticket lane |
| 已核准單張工單 | [實作](Workflow.md#implementation) | 逐行為 TDD：紅燈 → 最小實作 → 綠燈 |
| 進行或交付 Code Review | [Code Review 標準](CodeReview.md) | 唯一驗證項目、證據與審閱結論 |
| 多 Agent 或多 worktree | [協作](Workflow.md#collaboration) | 讀共同基準、確認 owner 與衝突 |
| 涉及 Secret、正式 Log、權限或外部 Provider | [安全](Workflow.md#security) | 先確認安全邊界與授權 |
| 不可信資料進入 Browser／WebView／HTML／DOM／JavaScript context | [XSS Review 強制閘門](Workflow.md#xss-review) | 先分類一般或 privileged XSS，將 source-to-sink 與 capability matrix 帶入 SPEC、ticket、TDD 與 review |
| 工單或功能集群完成 | [審閱與交接](Workflow.md#review-handoff) | commit、驗證、review、handoff／UAT |

## 預設角色邊界

除非專案負責人對單一 ticket 明確改派，使用本指引的控制面 Agent 的責任止於 `WAYFINDER`、Architecture／`grill-with-docs`、Context、SPEC、ticket、實作前 handoff、Code Review 與交接；正式原始碼與測試實作必須交給另一位具名 implementation owner。唯一詳細規則以 [Workflow.md §5.1](Workflow.md#role-boundary) 為準。

完成的 implementation 必須以 typed `ACTION_COMPLETED` 回到 Router；`ImplementationReturn` 的 `CHANGE_DETECTED` 必須回到 `REQUIREMENT_CHANGED`，不得由控制面猜測或靜默擴張範圍。

Agent-to-Agent orchestration 的唯一 owner 是 ticket 具名 reviewer。只有該
reviewer 可建立／派送／追送／steer／wait／interrupt／close implementation
Agent 或其 task；implementation owner 不得建立、委派、控制或等待任何
其他 Agent，也不得自行派下一票或升格為 reviewer。此限制必須由 host
tool surface 與 receipt-bound authority gate 強制，不得只依賴 prompt。
未匹配 reviewer、ticket、handoff、receipt、target owner 與 correlation 的
直接或間接 orchestration 一律 typed `HALT / ROLE_FORBIDDEN`。專案負責人
仍保有最終改派與停止權；model 名稱或推理等級不構成 authority。

任何工作或 commit 完成後，控制面 Agent 必須依 [流程 Router](Workflow.md#workflow-router) 產生 `ACTION_COMPLETED` 並先取得唯一 continuation；commit 不是可自行結束 task 的理由。`AUTO_CONTINUE`、`WAIT_FOR_HUMAN` 與 `HALT` 的唯一實際規則仍以 `Workflow.md` 為準。

## 唯一來源與未建立文件

完整專案啟用後，需求、事實、規格、工單、進度、安全與審閱必須各有唯一正式來源，路徑與內容規格由 `Workflow.md` 定義。

若該專案尚未建立必要產物，Agent 只能：

- 讀取已存在的檔案並說明缺口；
- 進入 `wayfinder`／`grill-with-docs` 收斂問題；
- 請求建立或補齊文件的明確授權。

不得猜測缺失內容、以聊天紀錄取代正式來源，或自行新增同用途的平行目錄。

## 不可違反的入口規則

- 不得從聊天內容直接修改正式程式、測試、資料庫或部署設定。
- `to-tickets` 核准前，不得開始正式實作、修改測試或新增 migration。
- Agent 只能寫入、stage、commit、merge、rebase、pull、push、stash 或切換自己的 worktree。
- 不得接收、輸出或保存明文 Secret；Log 必須先 redact／sanitize。
- 未核准、未提交、未簽署的 spike、截圖、聊天宣稱或其他 worktree 檔案，不能作為實作、審閱或合併依據。

## 完整專案啟用後的正式路徑

僅在專案負責人明確授權建立完整結構後，使用下列唯一位置：

```text
Workflow.md
AGENTS.md
CONTEXT.md
PRD.md
ProjectSchedule.md
doc/
  RequirementChangeLog.md
  WorkProgressReport.md
  security-agent-boundary.md
  context/<feature>/<worktree-id>.md
  reviews/<feature>/<cluster>-code-review.md
  adr/ADR-YYYYMMDD-NNN-<slug>.md
modules/
  spec/<feature>.md
  tickets/<feature>/README.md
  tickets/<feature>/NN-<slug>.md
  element/{typescript,python,java}/<feature>/<ticket-id>/
```

實際專案已有同用途目錄時必須沿用；禁止建立 `doc/specs/`、`doc/tickets/` 或其他同用途的平行來源。
