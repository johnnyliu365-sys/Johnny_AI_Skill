# 01 — Private Router Metadata Gate（POC）

## 工單資訊

| 欄位 | 內容 |
| --- | --- |
| ID | `01-private-router-metadata-gate` |
| 狀態 | `DONE` |
| 類型 | POC／垂直切片 |
| Owner | Codex（目前 worktree） |
| Reviewer | 專案負責人指定的 reviewer |
| 交付環境 | 本機 POC（fake transport／fake entitlement） |
| 基準 commit | `d378076` |
| 規格 | [private-router-saas.md](../../spec/private-router-saas.md) § User Flow and Acceptance Criteria（AC-1～AC-7） |
| 需求／Context | `CHG-20260804-008`；[private-router-saas/main.md](../../../doc/context/private-router-saas/main.md) |

## 使用者可見的結果

本機薄插件只送出已驗證的匿名 metadata、帳號範圍 salted revision digest、階段事件、entitlement mode 與本機 redact 後的結構化摘要。Private Router 依 profile 與 entitlement 作出型別化決策；本機僅在決策允許時建立最小 ContextView／ContextPacket。

只要資料缺失、輸入無效、entitlement 不足、服務回應無效或 fake transport 失敗，流程停止於明確的 fail-closed 結果，不能猜測下一步、不能讀取原文，也不能呼叫下游 Agent／Skill。

## 核准後補充：安全自動接續

工單已於 `2026-08-04` 由專案負責人核准，並追加以下已核准行為：Router 必須把每次決策分類為 `AUTO_CONTINUE`、`WAIT_FOR_HUMAN` 或 `HALT`。只有一個合法 capability、足夠的 metadata、有效 entitlement、有效 response 與明確 Context grant 同時成立時，local runner 才能自動接續下一動作。

一般工作節點不得因為普通 `SUSPEND` 而無限等待；只有明確的 specification／ticket 人工核准閘門可得到 `WAIT_FOR_HUMAN`。缺資料、授權拒絕、服務失敗、response mismatch／replay、未宣告 transition、預算超限與執行 safety ceiling 一律 `HALT`，不以本機 Profile 猜測或 fallback。

## 範圍

### In scope

1. 建立 Pydantic（或等價嚴格型別）本機／服務邊界契約：匿名 metadata request、entitlement claim、typed router decision、穩定 error code、可驗證的 opaque request／decision ID。
2. 建立本機 normalizer，只接受 allowlist 欄位，拒絕路徑、URI、原文、prompt、程式碼、PII、secret 與未知欄位；revision 僅可為 account-scoped salted digest。
3. 將現有 `library/workflow_router` 的 profile／transition／ContextView 組裝接到 metadata-only decision gate；Context resolver 在有效 allow decision 前不得取用來源。
4. 實作 POC fake transport 與 fake entitlement provider，讓測試可模擬允許、未授權、服務故障與不合法回應，不建立實際網路連線或儲存。
5. 回傳使用者可理解的外部行動標籤與穩定錯誤碼；private policy、profile 細節與核心路由演算法不得透過契約、錯誤或 log 外洩。
6. 補齊 TDD、嚴格型別、隱私與 regression 測試及可重現證據。
7. 提供 bounded local continuation runner 與 test-only executor port；POC 不執行模型，但可自動消化一連串已核發的 metadata-only next-event，直到真正的人類核准閘門或 fail-closed 終點。

### Out of scope

- 真實 private Router 後端、MCP server、OAuth／帳號系統、資料庫、付款、訂閱、計量、部署、雲端 log 或外部網路。
- 將本機原文、ContextPacket、來源 URI／路徑、程式碼、prompt、PII、secret 傳送或持久化。
- 修改 Codex／Claude 插件安裝機制，或聲稱可阻止使用者改用其他工具。
- 擴張 POC profile 至 MVP／商用階段；那些轉換由後續已核准的變更處理。

## 目標檔案與影響範圍

實作前應先確認實際位置；預期最小範圍如下。任何新增檔案或路徑變更都需在實作開始前記入 Context：

```text
library/workflow_router/contracts.py        # 型別契約與穩定錯誤碼
library/workflow_router/profile.py          # POC profile／合法 transition
library/workflow_router/router.py           # metadata decision gate
library/workflow_router/graph.py            # ContextView 組裝與 gate 整合
library/workflow_router/integrations.py     # fake transport／entitlement 邊界
tests/test_private_router_metadata_gate.py  # 本工單專屬行為與隱私測試
```

不得為方便測試而把 raw source、ContextPacket 或 private policy 加入 request、log、fixture 或 assertion 訊息。

## 契約與不變量

1. **Metadata-only**：跨邊界 request 只有 allowlist 欄位；模型採 `extra="forbid"`（或等價機制）。`source_path`、`uri`、`content`、`prompt`、`code`、PII／secret 欄位一律不可接受。
2. **Digest-only**：revision identity 必須是 account-scoped salted digest；不得接受明文專案名、repo、檔名或路徑作為替代。
3. **Fail-closed**：所有未驗證 input、缺 entitlement、deny／expire claim、transport exception、格式錯誤 response 與未知 decision 都轉換為明確拒絕；不得 fallback 至 local allow 或猜測 transition。
4. **Single control point**：Agent／Skill 不自行選來源或管理 Context；只有 gate 收到有效 allow decision 後，才可要求既有 Context resolver 建立受預算限制的 ContextView／ContextPacket。
5. **No exfiltration**：任何外部 transport stub 的 captured request、log record 與錯誤內容均不得包含禁止欄位或 raw content。
6. **Opaque correlation**：request／decision correlation ID 必須有可驗證格式、精確比對與過期／replay 規則；不可以模糊字串或前綴判斷取代。

## TDD 計畫與驗收

每一項先保留可重現的紅燈測試證據，再寫最小實作至綠燈；不得把測試一起寫成一開始即為綠燈的宣稱性測試。

| 類別 | Red → Green 測試 | 完成條件 |
| --- | --- | --- |
| 正常路徑 | 合法匿名 metadata + 有效 POC entitlement → typed allow decision → 只在此後建立 budgeted ContextView | AC-1、AC-2、AC-5；captured request 僅含 allowlist |
| 契約／空值 | 必填欄位的 `null`、空字串、空白、空陣列、空物件、未知欄位 → `ROUTER_INPUT_INVALID` | 不產生 context，不呼叫下游 agent／skill |
| 路徑前綴 | `source_path`、`uri`、`../`、Windows／POSIX 路徑型值即使有合法前綴也被拒絕 | 不以 substring／prefix 判斷路徑；request 不攜帶位置資訊 |
| 授權 | missing、expired、deny、scope mismatch claim；以及繞過 gate 直接要求 Context resolver | `ROUTER_ENTITLEMENT_DENIED`；resolver 不得被觸發 |
| correlation | malformed ID、不同 ID、過期 ID、replay ID | 精確驗證與比對；回傳 `ROUTER_RESPONSE_INVALID` 或 deny，無 fallback |
| 服務錯誤 | fake transport raise、timeout-like failure、malformed response、未知 decision | `ROUTER_SERVICE_UNAVAILABLE` 或 `ROUTER_RESPONSE_INVALID`；無 exception escape、無 local allow |
| 隱私回歸 | request capture、log/error capture、fixture 序列化掃描 | 不含 raw document／ContextPacket、路徑、URI、程式碼、prompt、PII、secret；AC-3、AC-4、AC-7 |

## Code Review 缺陷檢查（必填）

此表為 [CodeReview.md](../../../CodeReview.md) §2.1 的逐項處理；reviewer 必須查看真正執行過的測試和實作，不能只閱讀工單。

| 缺陷類型 | 本工單處理方式 | 必要證據 |
| --- | --- | --- |
| 1. 路徑前綴誤匹配 | 邊界完全不接受 path／URI；禁止欄位與 traversal-like 值一律 reject | red/green 測試與 captured request |
| 2. `null`／空字串／空陣列 | 每個 required field 與 claim collection 做 boundary validation | parameterized tests |
| 3. 授權繞過 | gate 前 resolver 不可達；direct／indirect bypass 都測試 | spy／fake resolver 未被呼叫的 assertion |
| 4. token 格式／比較 | opaque correlation ID schema、exact compare、expired／replay deny | malformed/mismatch/replay tests |
| 5. error code 一致性 | 外部只用 `ROUTER_INPUT_INVALID`、`ROUTER_ENTITLEMENT_DENIED`、`ROUTER_SERVICE_UNAVAILABLE`、`ROUTER_RESPONSE_INVALID` 等 enum | contract assertions；不得外洩內部原因 |
| 6. 外部 exception 行為 | fake transport exception 一律轉成 typed fail-closed result | no-throw boundary test |
| 7. 測試真實覆蓋行為 | 每個 AC 與前述六類缺陷列入 review traceability | reviewer 對 AC／測試／實作三方勾稽 |

## 驗證命令與證據

實作開始前先確認現有專案命令；預期最低驗證：

```powershell
python -m unittest discover -s tests
python -m mypy --strict library tests
python -m py_compile library/workflow_router/*.py
```

另需執行 captured-request／log privacy smoke test。若實際工具鏈不同，必須先更新工單與 Context，並說明等價嚴格型別與測試證據；不可直接略過。

## 完成定義

- [x] 所有 AC-1～AC-7 與本工單不變量有測試對應與綠燈結果。
- [x] 已驗證 `AUTO_CONTINUE` 不會在非人類節點中斷，且只在明確核准閘門回傳 `WAIT_FOR_HUMAN`。
- [x] 已保留每一類新行為的紅燈 → 最小實作 → 綠燈證據。
- [x] schema 拒絕未知與敏感欄位；strict type check 通過。
- [x] entitlement、服務故障、不合法 response、correlation mismatch 全部 fail-closed，且不建立 Context。
- [x] captured request、log／error 與 fixture 不含原文或禁止資料。
- [x] Code Review §2.1 七類逐項完成，並產生正式 review 證據。
- [x] 使用者可按外部行動標籤理解狀態，但不能由介面或錯誤推導 private routing algorithm。
- [x] 未增加真實網路、儲存、OAuth、付款或 runtime dependency。

## 核准閘門

專案負責人已於 `2026-08-04` 明確核准本工單。實作、全量驗證與正式 review 均完成；結論見 [Code Review](../../../doc/reviews/private-router-saas/01-private-router-metadata-gate-code-review.md)。
