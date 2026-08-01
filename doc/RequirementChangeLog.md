# 需求變更紀錄

本檔案是已確認需求與正式介面變更的唯一歷程；不取代 `grill-with-docs → CONTEXT.md → to-spec → to-tickets → TDD` 主線。

## CHG-20260801-001｜建立通用功能模組庫

- 日期：2026-08-01（Asia/Taipei）
- 產品版本：`v0.1`
- 狀態：已納入已核准 SPEC，待工單核准
- PRD 索引：`PRD.md §1–5`
- 規格索引：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（`APPROVED`）

### 決策摘要與理由

- 決策：在本專案建立通用模組庫，依 NLP、金流串接與其他同功能集群分類；來源專案保持唯讀。
- 理由：保留可重用能力，同時移除來源專案的業務耦合、秘密、環境與營運資料依賴。

### 需求變更內容

- 原有內容：本專案只有 AI 協作 Bootstrap 規範，沒有可重用功能模組。
- 變更後內容：啟用完整文件結構，經規格、工單與 TDD 後建立本機通用模組庫與 README。

### 變更後影響範圍

- 後端／API／Webhook：僅建立本機契約與 fake adapter；不連線或啟用外部服務。
- 資料庫／快取／Provider：建立可替換的抽象；不帶入來源 schema、資料或設定。
- 安全／成本／隱私／維運：禁止帶入 secrets、PII、tenant、營運資料與付款憑證。
- 規格／工單／TDD／`CONTEXT.md`：建立 `reusable-module-library` 的正式追溯鏈。

### 關聯技術方案與文件

- 可重用方案：來源專案C 的規則式文字解析；來源專案D 的 outbox、worker、state guard、emergency stop；SourceProjectA 的付款流程切分與多模態分析邊界；來源專案B 的強型別規則引擎。
- 排除方案：直接複製來源原始碼、來源資料表、Provider 設定、UI、部署配置或任何秘密。
