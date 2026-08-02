# 通用功能模組庫 PRD

## 1. 產品目標

建立一個本機、可重用的功能模組庫，讓後續專案可採用明確契約，而不是直接依賴 SourceProjectA、來源專案C、來源專案D 或遊戲專案的業務原始碼。

## 2. 目標使用者

- 需要快速採用文字理解、付款、可靠性或狀態機能力的專案開發者。
- 需要保留來源追溯、限制與驗證證據的維護者。

## 3. MVP 範圍

- Python NLP：規則式文字正規化、訊息分類、欄位抽取與可插拔 provider 邊界。
- Python 金流：金額／付款狀態契約、付款 provider port、訂閱帳本、退款與對帳的 idempotency 邊界。
- Python 通用可靠性：outbox、耐久 worker、expected-state guard、emergency stop、身份解析。
- Kotlin：離線地址正規化與解析的獨立候選集群。
- C#：卡牌規則引擎與偽裝狀態機的獨立遊戲候選集群；不得誤列為後端或金流功能。
- 每個功能資料夾提供 README 與可重現驗證方式。

## 4. 不做範圍

- 不搬動或改寫任何來源專案。
- 不使用、輸出或保存 secrets、PII、營運資料、環境檔或 tenant 設定。
- 不提供任何正式收款、LINE 訊息、派單、自動化、部署或資料庫操作能力。
- 不承諾與來源專案的資料表、外部 provider 或 UI 相容。

## 5. 成功標準

- 每個已交付模組只依賴其 README 列出的公開契約與套件。
- 每個模組有正常、輸入錯誤、外部失敗／fail-closed 與回歸測試。
- 可從 README 判斷是否適用、不可用於何種情境，以及原始參考來源。

## 6. 專案流程 Router 框架 POC

### 目標

建立可套用於不同專案的流程引擎；引擎不內建個別產品規則，而是以強型別 Profile 控制 `POC → MVP → COMMERCIAL` 的關卡、核准與能力選擇。

### POC 範圍

- 驗證 `RouterState`、`RouterEvent`、`RouterDecision`、`ContextView` 與引用映射的強型別契約。
- 以 LangGraph 執行封閉的 transition graph，禁止 LLM 或任意字串決定下一個節點。
- 將 `CapabilityRef` 解析為 OpenAI Agents SDK Agent 定義；本 POC 不呼叫模型。
- 以 Temporal workflow／signal／query 類別表達可持久化的人類等待；本 POC 不連接 Temporal server。
- 以 MCP resource URI 與 source port 表達 `required_sources`；本 POC 只使用本機 fake adapter。
- 每次旁路引用都產生新的 ID，映射到 Grill、SPEC 或 ticket，且原文不進共享 Context、checkpoint 或 ledger。

### 不做範圍

- 真實 LLM、付費 Provider、外部 MCP server、Temporal worker、資料庫、部署、Secret 或正式專案資料。
- 替任何被接管專案決定其 POC、MVP 或商用的商業門檻。

### POC 成功標準

1. 受驗證的 Profile 能將 `INTAKE` 路由到 `WAYFINDER`，並將已核准的 `WAYFINDER_GO` 路由到 `ARCHITECTURE`。
2. 相同來源段落的兩次真實引用產生不同 `side_context_id`；retry 不產生第二筆同一引用。
3. 來源 revision 改變後，相關引用可被標示為 `INVALIDATED`。
4. 已關閉引用能由 Context 反查使用它的 Grill、SPEC 或 ticket；中央映射不保存原文。

## 7. 可重用模組選擇 Skill POC

### 目標

將已交付的通用模組整理為最小選擇卡與可攜 skill，讓 AI 不需讀取整個 library 就能找到正確公開契約。

### 成功標準

- 每個 READY 模組有用途、公開 import、相依及最小閱讀順序。
- `$apply-reusable-modules` 強制先選卡，再讀取命中的最少檔案。
- 未交付模組不可被選擇；模組命中不能繞過目標專案的流程與核准。

## 8. Johnny AI Skill Plugin Distribution POC

### 目標

把本 repository 發行為可從 private GitHub marketplace 安裝的 Codex plugin，讓使用者可在不同公司專案開啟或接管時掛載整套 workflow；停用或移除時，公司專案仍完全獨立運作。

### POC 範圍

- `.codex-plugin/plugin.json`：穩定 plugin 身分與 `skills/` 入口。
- `.agents/plugins/marketplace.json`：以 repository-root Git URL 與 `main` 提供可安裝來源。
- `$johnny-project-takeover`：先讀取目標專案規範，再經 Router、Wayfinder、Grill、SPEC、ticket、review 與 handoff 的最小入口。
- 根目錄 README：私有安裝、使用、更新與拔除步驟，以及不耦合公司專案的契約。

### 不做範圍

- 不自動安裝到任何使用者帳號、不修改 `~/.codex`、不寫入公司專案。
- 不建立 runtime package、MCP server、App、hook、CI integration、Provider、Secret 或部署。
- 不把 plugin cache、checkout、Git submodule、symlink 或相對 import 視為公司專案的依賴管理。

### 成功標準

1. plugin manifest、marketplace JSON 與兩個 bundled skills 均通過結構驗證。
2. repository 可作為 Git marketplace 來源，且 plugin source 指向 repository root。
3. README 明確區分 plugin 控制平面與公司專案交付物，並提供無破壞性的拔除流程。
4. plugin 不宣告 MCP、App、hook 或其他會在公司專案外自動執行的元件。

## 9. Claude Code Plugin Distribution POC

The detachable Johnny AI Skill workflow must be available in Claude Code from the same private GitHub repository and the same root `skills/` source used by Codex. Installation is per-user and external to a company project; removal must leave that project's checkout, runtime, dependencies, CI, and deployment unchanged. The POC consists only of Claude plugin/marketplace metadata and clear operator instructions. It does not introduce MCP, hooks, a service, secrets, package imports, or target-repository files.

- Change: `CHG-20260802-005`
- Specification: `modules/spec/claude-code-plugin-distribution.md`
- External smoke test: `claude plugin validate .` runs only where Claude Code is installed.

## 10. Context Load Telemetry POC

The Router POC must produce local, metadata-only evidence for whether its selected ContextPacket reduces Agent input context without degrading acceptance quality. Each comparison uses matched baseline and router runs from the same project snapshot, provider, model, scenario, and attempt. Only provider-reported input-token counts may substantiate a reduction claim; estimates are used solely for ContextView budget observation. Evidence must contain no source text, prompt, URI, secret, or company code.

- Change: `CHG-20260803-006`
- Specification: `modules/spec/context-load-telemetry.md`
