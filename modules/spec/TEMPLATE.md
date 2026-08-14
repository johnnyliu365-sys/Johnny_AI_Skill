# <功能名稱> 規格

| 欄位 | 內容 |
| --- | --- |
| 規格 ID | `SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`（例如 `SPEC-FM-P0-SEARCH-CONTROL-20260730-01KYS2QPQCZTY7GBZKW4K175NW`） |
| 規格狀態 | `DRAFT`／`APPROVED`／`SUPERSEDED` |
| 撰寫 AI 簽名 | `<AI>／<worktree>／基準 <commit SHA>` |
| 排查起點 Context | `doc/context/<feature>/<worktree-id>.md` |
| PRD 索引 | `PRD-YYYYMMDD-NNN`／不適用 |
| 需求變更 | `CHG-YYYYMMDD-NNN`／不適用 |
| Sealed Context binding | `<shared revision/digest + exact feature Context revision/digest>`／不適用 |
| 實作語言 | 本功能集群的實作語言，依 `CONTEXT.md` › `## 實作語言規範` 的統一後端語言。若本集群主張偏離，須在「風險」段落列出實測依據與對應的需求變更紀錄。 |

## 問題、目標與不做範圍

## 使用者流程與驗收條件

## 領域模型、資料流與責任邊界

## API／事件、資料庫、快取、Provider、權限與維運

## 前端組合與依賴注入（適用時必填）

- UI 組合層級與元件責任：`<screen / layout / components>`
- Composition Root、依賴 scope 與裝配位置：`<path / lifecycle>`
- 可注入介面與 production binding：`<API / state / navigation / clock / feature flag / analytics / i18n / permission>`
- test fake／stub 與替換方式：`<test composition>`
- loading／empty／error、權限與可存取性驗收：`<criteria>`

不得把業務規則或外部依賴隱藏於 UI 元件；無前端影響時，必須明記 `N/A`。

## 實作交接與回傳契約

- `ImplementationHandoff`：列出已核准 SPEC／ticket／Context／AC／TDD 的 metadata-only 引用、控制面 owner、implementation owner、reviewer，以及適用前端的 Composition Root／DI 引用。
- `ImplementationReturn`：明確列出 `COMPLETED → ACTION_COMPLETED`、`BLOCKED → HALT`、`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`；不得以回傳事件靜默變更需求、架構、公開契約、驗收或 UI/DI 邊界。
- 禁止在交接或回傳保存 raw ContextPacket、原始來源、prompt、path、URI、Secret 或 PII；只能保存不透明 ID、revision/span、side-context ID、consumer fingerprint 與 evidence digest。

## 測試切點與 TDD 設計

## 風險、相容性、回滾與部署前提

## 收斂與 lineage

- Sealed shared/feature Context binding：`<revision / digest / exact source refs>`
- Active requirement leaf：`<PRD/CHG IDs and REQ leaf path>`
- 關聯 CHG 的 SPEC 收斂結果：`<section / 不適用>`
- 新事實或缺口：`<REQUIREMENT_CHANGED / none>`；不得回寫 sealed Context。

## 修訂簽名

| 日期 | AI／worktree／基準 SHA | 摘要 |
| --- | --- | --- |
| `<ISO-8601>` | `<signature>` | `<revision>` |

## 核准紀錄

- 決策者：`<name>`
- 日期：`<Asia/Taipei date>`
- 核准範圍：`<scope>`
