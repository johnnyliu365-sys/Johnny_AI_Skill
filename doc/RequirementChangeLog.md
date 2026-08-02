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

## CHG-20260802-002｜新增可重用專案流程 Router 框架 POC

- 日期：2026-08-02（Asia/Taipei）
- 產品版本：`v0.2-router-poc`
- 狀態：已由使用者核准實作
- PRD 索引：`PRD.md §6`
- 規格索引：`SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H`（`APPROVED`）

### 決策摘要與理由

- 決策：在既有通用模組庫旁建立本機 Router framework POC，作為日後接管任何專案時的流程引擎。
- 理由：現有流程嚴謹但共享 Context 會持續膨脹；Router 以最小來源視圖、capability catalog 與一次性引用映射維持可追溯性。

### 需求變更內容

- 原有內容：Workflow 只定義 Router 的治理規則，沒有可執行的強型別核心。
- 變更後內容：新增 Pydantic 契約、LangGraph transition、Agents capability adapter、Temporal human-wait skeleton 與 MCP source port；POC 不連線任何外部服務。

### 影響與控制

- Context：中央僅保存來源 URI、revision、span、一次性引用 ID、引用者指紋與目標產物；原文僅屬引用 Agent 的工作區。
- 安全／成本：禁止 Secret、付費 Provider、網路呼叫與真實專案寫入。
- 升級：POC 證據完成後才可由新的 `REQUIREMENT_CHANGED` 申請 MVP，必須重跑 Wayfinder。

## CHG-20260802-003｜新增可重用模組選擇卡與可攜 Skill

- 日期：2026-08-02（Asia/Taipei）
- 版本：`v0.3-module-selector-poc`
- 狀態：已由使用者核准實作
- PRD 索引：`PRD.md §7`
- 規格索引：`SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H`（`APPROVED`）

### 決策

以短卡片和 `$apply-reusable-modules` 取代全量模組閱讀。卡片只提供選擇與最小閱讀路徑；採用、實作與外部操作仍受目標專案 Workflow 控制。
