# 通用功能模組庫規格

| 欄位 | 內容 |
| --- | --- |
| 規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP` |
| 規格狀態 | `APPROVED` |
| 撰寫 AI 簽名 | `Codex／目前工作區／基準待提交` |
| 排查起點 Context | `doc/context/reusable-module-library/main.md` |
| PRD 索引 | `PRD.md §1–5` |
| 需求變更 | `CHG-20260801-001` |
| 共用 Context 回掛 | `CONTEXT.md §衍生 SPEC 索引` |

## 問題、目標與不做範圍

### 問題

現有能力散落在四個領域專案，並與資料庫、LINE、付款 provider、Android、Unity、租戶或健康業務模型耦合，無法安全直接套用。

### 目標

在本專案重建具名、強型別、可測試且不含敏感資料的通用功能模組；每一模組有獨立 README 與來源追溯。

### 不做範圍

- 不移動、修改或直接複製來源專案的程式碼。
- 不建立真的付款、退款、LINE 發訊、派單、AI provider 呼叫、部署或資料庫連線。
- 不保證既有 UI、資料表、業務流程或外部 API 相容。

## 使用者流程與驗收條件

1. 開發者可從頂層 README 找到 `NLP`、`金流串接` 或其他功能集群。
2. 每個功能資料夾的 README 可說明責任、公開型別、使用範例、依賴、禁止用途、來源與測試命令。
3. 模組只依賴本專案定義的契約與 fake adapter；輸入錯誤與未知 provider 結果 fail closed。
4. 任何來源專案檔案的 hash、路徑與內容不被更動；本專案實作有自己的測試與 README。

## 領域模型、資料流與責任邊界

### 建議目錄架構（待核准）

```text
library/
  README.md
  NLP/
    README.md
    python/
      README.md
      text_contracts/
      rule_parser/
      provider_ports/
  金流串接/
    README.md
    python/
      README.md
      payment_contracts/
      subscription_ledger/
      provider_ports/
      reconciliation/
  功能集群/
    README.md
    python/
      reliability_core/
      line_transport/
      identity_resolution/
    kotlin/
      offline_geo_resolution/
    csharp/
      card_rules_engine/
      camouflage_state/
```

`modules/element/` 仍只保存 ticket 與實際程式碼的索引；`library/` 才是本專案重新實作的通用程式碼根目錄。

### 功能邊界

- `NLP`：以規則式、可解釋的文字正規化、分類與欄位抽取為優先；模型 provider 只能透過 port 接入，不能生成未證實的領域事實。
- `金流串接`：以 `Money`、付款意圖、交易狀態、idempotency key、帳本事件與 provider result 等契約為核心；支付provider丙、支付provider甲、發票與資料庫只可作 adapter 範例，不可直接啟用。
- `功能集群/python`：提供 outbox、worker、狀態轉換、LINE transport、緊急停止與顯示身份解析等通用可靠性能力。
- `功能集群/kotlin`：提供離線地址正規化與座標範圍驗證；不包含 來源專案C 運行時或資產資料。
- `功能集群/csharp`：提供純規則卡牌核心與偽裝狀態機；Unity UI、場景與建置流程排除。

## API／事件、資料庫、快取、Provider、權限與維運

- Python 公開 API 使用 dataclass、Enum、Protocol 與顯式 nullability；禁止 `Any` 與未驗證 `dict` 跨模組邊界。
- Kotlin 使用 data class、sealed interface／enum class；C# 使用 record、enum 與明確 collection 型別。
- 所有 provider 由 Fake 實作測試；真實 HTTP、Secrets、資料庫、Redis、LINE 或金流 SDK 不在第一批範圍。
- 金流以整數最小貨幣單位或等價不可變金額型別表示，不使用浮點數。

## 測試切點與 TDD 設計

- NLP：正規化、訊息分類、完整／不完整欄位、歧義輸入與不允許自動補值。
- 金流：非法金額、重複 idempotency key、合法／非法狀態遷移、provider timeout／未知結果與 append-only audit。
- 可靠性：outbox claim、重試、預期狀態衝突、emergency stop、身份隔離。
- Kotlin／C#：領域值物件、狀態轉換與非法動作拒絕。

## 風險、相容性、回滾與部署前提

- 風險：來源程式以動態資料、資料庫 schema 或業務術語表達隱含契約。緩解：逐 ticket 建立顯式 DTO、fixture 與 fail-closed 測試。
- 風險：付款、訊息或 ML 名稱可能讓使用者誤認可直接上線。緩解：README 明示僅提供本機 fake adapter，禁止用於真實交易或外部操作。
- 回滾：每張 ticket 獨立 commit；不觸及來源專案或外部狀態，因此只需移除本專案的該 ticket commit。

## 收斂與回掛

- 共用 Context 回掛內容：本 SPEC 的 ID、路徑、候選集群與來源唯讀邊界已列於 `CONTEXT.md`。
- 關聯 CHG 的 SPEC 收斂結果：`doc/RequirementChangeLog.md §CHG-20260801-001`。
- 回掛共同基準 commit：待文件基準提交。

## 修訂簽名

| 日期 | AI／worktree／基準 SHA | 摘要 |
| --- | --- | --- |
| 2026-08-01 | Codex／目前工作區／待提交 | 建立 DRAFT SPEC 與待決目錄架構。 |
| 2026-08-01 | Codex／目前工作區／待提交 | 使用者核准目錄架構、語言與唯讀來源邊界。 |

## 核准紀錄

- 決策者：使用者。
- 日期：2026-08-01（Asia/Taipei）。
- 核准範圍：`library/` 目錄架構、Python／Kotlin／C# 功能集群與來源專案唯讀邊界；工單另待核准。
