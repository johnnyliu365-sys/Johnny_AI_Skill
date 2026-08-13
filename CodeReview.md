# Code Review 標準

> 本文件是本工作流程中 Code Review 的唯一實際驗證標準。`Workflow.md` 僅規定何時進入審閱與如何交接；所有審閱判斷均以本文件為準。

本檔與 `AGENTS.md`、`Workflow.md` 的文件歸屬、插件隔離及 target project 零複製規則，唯一依據 [Workflow.md 的「治理文件歸屬與插件隔離」](Workflow.md#governance-document-ownership)；不得另行建立競爭規則。

## 1. 適用範圍與原則

- 每張完成的 ticket 與每個待交接的功能集群，都必須依本標準進行審閱。
- 審閱以已核准的 spec、ticket、`CONTEXT.md` 與可重跑的驗證結果為事實依據；沒有證據的判斷不得視為通過。
- 發現問題時應指出影響、位置、重現或驗證方式，以及建議處置；不以主觀偏好取代既定規範。

## 2. 必要驗證項目

| 項目 | 驗證標準 |
| --- | --- |
| 清晰易懂 | 以 [AGENTS.md 的「P0：原始碼型別要求」](AGENTS.md#p0-source-type) 為必要依據：原始碼必須符合其中「C++ 概念可讀的強型別」要求，使資料意義、可否為空、輸入輸出與領域狀態可由型別直接理解；再檢查命名、結構、抽象與註解是否表達意圖，以及重複、隱性副作用與不必要複雜度是否已消除或有合理說明。 |
| 既定編碼規範 | 程式碼遵循專案既有的風格、分層、型別、格式化、lint 與架構規則；例外必須有明確理由。 |
| 邏輯正確 | 實作符合已核准的需求與業務規則，資料流、狀態轉換、權限判斷與輸出結果正確。 |
| 邊界與異常 | 空值、缺值、無效輸入、極端值、併發或重試情境，以及外部服務失敗等情況皆有適當處理與可理解的失敗行為。 |
| 安全與效能 | 不引入未授權存取、資料外洩、注入、機密曝露或資料隔離風險；不存在明顯的效能瓶頸、資源洩漏或不必要的高成本操作。 |
| 測試覆蓋 | 測試覆蓋新增或變更的核心行為、重要分支、邊界與異常；測試可重跑，且 smoke test 已通過。覆蓋是否足夠以風險與行為證據判斷，不僅以百分比判斷。 |
| 依賴合理 | 新增、升級或保留的依賴有必要性、相容性與維護性依據；沒有可避免的重複、過時或高風險依賴。 |
| 專案規格符合性 | 實作、測試、設定與文件符合已核准的 spec、ticket 與 `CONTEXT.md`；差異已取得核准並完成追溯。 |
| Agent 角色權限 | 涉及多 Agent／task 控制時，reviewer 是唯一可達 orchestration effect 的角色；implementation owner 的直接與間接 create/spawn/fork/send/follow-up/steer/wait/interrupt/close 均在 effect 前固定回 `HALT / ROLE_FORBIDDEN`。必須反證 copied/forged/replayed reviewer、錯 ticket/handoff/receipt/target/correlation 與一般 capability 字串不能授權；prompt 或 model 選擇不得充當安全邊界。 |
| Task／worktree 綁定 | implementation task 的產品層 active workspace root 必須精確綁定 ticket 的 owner worktree，且正規化絕對根、解析後 filesystem identity 與 Git worktree metadata 三者一致。prompt／handoff 路徑、shell `cd`、command working directory、環境變數或 sibling 可讀權限均不是綁定；缺失、不可讀回或不一致必須在問題、pending、receipt、branch、source 或 host／Git effect 前固定回 `HALT / TASK_WORKSPACE_MISMATCH`。不得用控制面 project 或新建 Codex-managed worktree代替既有永久 implementation worktree。 |
| XSS 與宿主能力 | 任何不可信資料進入 Browser、WebView、HTML／DOM Renderer 或 JavaScript execution context 的功能，都必須依 [Workflow.md 的 XSS Review 強制閘門](Workflow.md#xss-review)審查 source-to-sink、實際 renderer 行為與繞過路徑。JavaScript 可達 Native Bridge、IPC、Extension API 或其他 privileged capability 時，必須升級審查 JavaScript → host effect 的完整 capability graph，並證明所有未授權路徑在 effect 前 fail closed。 |

## 2.1 缺陷分類與攔截點

下列九類是本專案已知且可被系統性攔截的缺陷。**「攔截點」決定責任歸屬**：標 `TDD` 者，工單的「TDD 設計」必須逐一列出對應案例，未列出即為工單缺陷而非實作缺陷；標 `CR` 者，審閱報告必須逐項記錄結果。

| # | 類別 | 攔截點 |
| --- | --- | --- |
| 1 | 路徑前綴誤匹配 | TDD 邊界 ＋ CR 檢查是否漏 |
| 2 | null／空字串／陣列 | TDD |
| 3 | 權限繞過 | TDD ＋ CR |
| 4 | Token 格式與比較 | TDD |
| 5 | 錯誤碼是否一致 | TDD |
| 6 | 例外是否會拋出 | TDD |
| 7 | 測試是否真的涵蓋描述 | CR |
| 8 | XSS 與 privileged JavaScript capability | Architecture／SPEC／TDD ＋ CR |
| 9 | Implementation task／worktree 綁定錯置 | Architecture／ticket／TDD ＋ CR |

### 1. 路徑前綴誤匹配

以字串前綴、包含或未正規化的路徑做路由或授權判定，導致範圍過寬（不該匹配的被匹配）或過窄（該匹配的漏掉）。

**TDD 必要案例（七種，缺一即 `CHANGES_REQUESTED`）**：剛好相等、前綴後多一字元、尾斜線有無、大小寫變化、URL 編碼、路徑遍歷（`..`）、空路徑。

**CR 必要動作**：將七種列表逐一對到測試。漏掉的那一種就是會被利用的那一種。

### 2. null、空字串、陣列

「不存在」的多種表述未被一致處理，各自走到不同分支。

**TDD 必要案例（五種）**：`null`、`undefined`、`''`、純空白、空容器（`[]`／`{}`）。並明確斷言**哪些等價**（例如空字串與純空白皆視同未設定）。

### 3. 權限繞過

重點不是「有沒有做檢查」，而是「**有沒有一條路徑可以不經過該檢查抵達受保護資源**」。

**TDD 必要案例**：(a) 直接存取——無憑證、錯憑證、過期憑證；(b) **間接存取**——經由其他已註冊入口、內部呼叫或背景工作抵達同一資源。

**CR 必要動作**：**從唯一系統組裝入口出發列舉所有可達路徑**，確認每條都經過同一判定點。繞過路徑通常存在於另一張 ticket，因此必須在功能集群層審閱執行。

多 Agent 功能另須從 reviewer 與 implementation owner 兩個 profile 各自
列舉所有 thread-control 工具。reviewer 的正向案例必須精確綁定 receipt；
implementation owner 的直接工具、間接 adapter、偽造 reviewer identity、
重播 receipt 與錯 target 都必須在任何 host effect 前 `ROLE_FORBIDDEN`。

### 4. Token 格式與比較

兩件獨立的事，常被當成一件：**解析**是否嚴謹、**比較**是否為固定時間。

**TDD 必要案例**：
- 格式：缺前綴、多重空白、大小寫變化、前後空白、空 token、超長、非 ASCII。
- 比較：**以來源掃描斷言未使用 `===`／`==` 比對憑證**，必須走固定時間比較函式。以計時方式驗證固定時間並不穩定，來源斷言才可重跑。

### 5. 錯誤碼是否一致

同一語意在不同層回不同碼，或對外碼與對內碼混用而形成側通道／診斷缺口。

**TDD 必要案例**：每個失敗原因斷言**兩件事**——(a) 對外回應碼與形狀固定不變，不因原因不同而可區分；(b) 對內結構化日誌帶有正確且唯一的原因碼。

只驗對外，對內診斷能力會靜默流失；只驗對內，則洩漏側通道。**工單若只規定「失敗回某碼」而未規定哪些原因必須保持可區分，屬工單缺陷。**

### 6. 例外是否會拋出

兩個相反方向都算缺陷：**該拋沒拋**（吞掉錯誤回成功）與**不該拋卻拋**（附屬失敗炸掉主流程）。

**TDD 必要案例**：對每個外部依賴各注入一次失敗，斷言兩件事——(a) 主流程的可觀察行為（回應形狀、狀態、副作用是否已落地）；(b) 例外是否傳播，明確斷言 throw 或不 throw，不得留白。

### 7. 測試是否真的涵蓋描述

測試名稱或 AC 描述與實際斷言不一致。三種型態：名稱說 A 但只驗 B；斷言實作細節而非可觀察行為；**紅燈從未真的紅過**（先寫原始碼再補測試，測試被實作形狀反向決定）。

**CR 必要動作（測試無法驗證自己）**：
1. 逐條把 AC 對到具體測試，**一對一列出**，不接受「整體有覆蓋」。
2. 確認斷言的是外部可觀察行為。
3. **反向驗證**：移除或反轉該實作後，該測試必須失敗。這是唯一能證明測試真的驗到那件事的方法。
4. 檢查紅燈證據是否真實（工單所記紅燈輸出、commit 順序、測試先於實作）。

### 8. XSS 與 privileged JavaScript capability

任何使用 Browser、WebView、HTML／DOM Renderer 或 JavaScript execution context 呈現不可信資料的功能，都必須進入 XSS Review。若 JavaScript execution context 可存取 Native Bridge、IPC、Extension API 或其他 privileged capability，XSS 必須升級審查；此時成功的 XSS 不只影響網頁 session，也可能取得宿主程式能力。

**TDD 必要案例**：逐格引用 ticket 的 XSS matrix，驗證適用的 script／event handler、危險 URL scheme、SVG／foreign-content、attribute／URL／CSS／template breakout、編碼變體、stored／reflected／DOM-based source、二次 decode 及 navigation／reload。每格須在隔離 renderer 中斷言攻擊 marker 未執行，而不只比對字串或 snapshot；sanitizer／encoder 單元測試不得取代 renderer 行為測試。

`PRIVILEGED_XSS_REVIEW` 另須以 fake bridge／IPC／Extension capability 驗證：惡意 script、錯 origin／frame／caller、錯或多餘 schema 欄位、未授權 action、replay、間接 adapter 與 navigation 後 context，全部在 host effect 前 fail closed；唯一精確授權的正向案例仍須成功。測試不得觸發真實宿主、target project、filesystem、process、credential 或 extension effect。

**CR 必要動作**：

1. 先核對 `XSS_NOT_APPLICABLE`／`STANDARD_XSS_REVIEW`／`PRIVILEGED_XSS_REVIEW` 分類及其 Architecture／SPEC 依據；漏分或降級即 `TICKET_DEFECT` 或 `REQUIREMENT_CHANGED`。
2. 從每個 untrusted source 追到每個 parsing／storage／transformation 與 DOM／HTML／script sink，列出 framework escape、sanitizer、Trusted Types、CSP、sandbox、origin 與 navigation 邊界；禁止以工具名稱代替可達性證據。
3. 搜尋並審查 `innerHTML`、`outerHTML`、`insertAdjacentHTML`、`document.write`、HTML template／markdown converter、script URL、動態 code evaluation 及框架等價 escape hatch；每個可達 sink 都要對應 TDD 格或明確不可達證據。
4. 升級審查時，從 JavaScript context 反向列舉 Native Bridge、IPC、Extension API 與其他 privileged port 的所有直接／間接入口，核對 origin／frame／caller、schema、action allowlist、authorization、replay 與 effect-before-gate；任一路徑可繞過即 `CHANGES_REQUESTED`。
5. 對至少一個凍結的攻擊格反轉 sanitizer／encoder／sink gate 或 privileged capability gate，確認 committed test 轉紅並精確還原。

### 9. Implementation task／worktree 綁定錯置

task 在控制面 project 或其他 workspace 啟動，只靠 prompt、handoff 文字或 shell `cd` 指向 implementation worktree，並不會改變產品層 sandbox／Git authority；這種錯置可能讓 source 可讀卻無法安全建立 linked-worktree `index.lock`，也可能讓錯誤 task 取得不屬於它的 effect 範圍。

**TDD 必要案例**：唯一正向案例必須由產品層 task readback、filesystem identity 與 Git worktree metadata 證明精確綁定後才可進入 dispatch。負向至少包括控制面 project root、sibling、parent、child、前綴相似路徑、prompt-only `cd`、command working directory override、環境變數指向、缺少／不可讀回 workspace、錯 Git worktree pointer、錯 project／task／owner／handoff／allocation／correlation；每一格都必須在交付問題、pending、receipt、branch、source 或 host／Git effect 前固定得到 `HALT / TASK_WORKSPACE_MISMATCH`。測試使用 fake product／filesystem／Git readback，不得建立真實 worktree 或修改其他 lane。

**CR 必要動作**：

1. 從產品層重新讀回 task 的 project ID、task ID 與 active workspace root，不接受 prompt、聊天或實作者自述。
2. 獨立讀回 ticket owner worktree 的 canonical root、filesystem identity 與 Git worktree metadata，逐項對到 opaque binding evidence。
3. 反證在控制面 project 啟動後執行 `cd`、指定 command working directory 或提供 sibling write permission，仍不能通過 admission。
4. 變更 task／workspace 時，確認舊 task 與 commits 被保留為不可變證據，且新 handoff、allocation、correlation、question 與 workspace binding 已建立；只有 scope 未變且 receipt 有效、未消耗時才可沿用 receipt。

## 3. 審閱證據與結論

- Review report 必須逐項記錄上述驗證結果，並附上相關檔案／位置、測試或命令輸出、smoke test 結果，以及未解決風險。
- Review 開始前必須讀取 ticket 的具 revision `Acceptance Closure Set`。每個 blocking finding 都必須引用一個既有 Closure item；無法引用者不得直接判為 implementation defect。
- 同一輪必須一次跑完全部 Closure items 並批次回傳 findings。禁止在 correction 完成後才新增原本可於同一份 baseline 發現的逐輪探索性 blocking probe。
- 同時必須逐項記錄 §2.1 中攔截點含 `CR` 的五類（1 路徑前綴、3 權限繞過、7 測試涵蓋、8 XSS 與 privileged JavaScript capability、9 task／worktree 綁定）的檢查結果與依據；第 8 類若分類為 `XSS_NOT_APPLICABLE`，仍須記錄可驗證理由。
- 若發現缺陷屬於 §2.1 中攔截點為 `TDD` 的類別，而**該工單的「TDD 設計」並未列出對應案例**，審閱結論仍為 `CHANGES_REQUESTED`，但根因記為**工單缺陷**，並同時修正工單；不得僅要求實作者補測試而讓同類缺口在下一張工單重現。
- 每項 finding 必須標記 `IMPLEMENTATION_DEFECT`、`EVIDENCE_DEFECT`、`TICKET_DEFECT`、`REQUIREMENT_CHANGED` 或 `OUT_OF_SCOPE_HARDENING`。只有前兩類可在 Closure Set 不變時回原 implementation lane；`TICKET_DEFECT` 回工單設計、`REQUIREMENT_CHANGED` 回變更控制、`OUT_OF_SCOPE_HARDENING` 另開後續 ticket 且不阻擋目前工單。
- 結論僅可為 `APPROVED`、`CHANGES_REQUESTED` 或 `BLOCKED`。若有未處理且會影響正確性、安全性、資料隔離、可用性、效能或規格符合性的問題，不得標記為 `APPROVED`。
- `CHANGES_REQUESTED` 或 `BLOCKED` 的項目修正後，必須重新執行受影響的驗證、Smoke Test 與必要的審閱項目。
- 同一 Closure revision 最多執行一次 correction review；第二次仍未通過時結論必須附帶 `CONVERGENCE_REVIEW_REQUIRED`，回控制面做架構／ticket 分解，不得直接觸發第三次 implementation correction。
