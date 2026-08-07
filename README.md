# Johnny AI Skill

這是一套可隨時安裝或拔除的「個人 Agent workflow 外掛」。它用來接管新專案、既有專案或做到一半的專案，並把同一份 skill 同時提供給 Codex 與 Claude Code。

它不是公司專案的 runtime service、MCP server、hook、CI 依賴、Git submodule、symlink、package dependency 或原始碼 import。因此拔除後，公司的建置、測試、部署與既有程式不會受影響。

## 現行 policy 與固定交付回應

目前目標是 `non-commercial`、可拔除的多 AI 協作／稽核控制平面。既有 private Router SaaS、價格、entitlement 或服務化文字都是歷史 POC 記錄，不是現行產品承諾。

套用 plugin 時先詢問 `可用 coding Agent 數量為 1 或 2？`；在 ticket 與文件交接完成後，控制面只輸出一次固定回應，再提出唯一的 dispatch-confirmation 問題：

```text
工單 ready
- commit：<ticket docs commit>
- 工單：<ticket reference>

文件交接
- commit：<handoff docs commit>
- implementation owner：<named owner>
- 工單 <ticket reference> 是否已交付給 implementation owner <named owner>？
```

未收到這個精確交付確認前，不授予 branch、worktree、source、Context 或 implementation capability；`WAIT_FOR_HUMAN` 只表示這個決策，其他未授權、無效或不可用狀況一律 `HALT`。

## 目前發行：0.3.2

0.3.2 將前端的組合式設計與依賴注入列為 SPEC／ticket 的阻擋規則，並將控制面 Agent 固定為 Wayfinder／Grill／ticket／review；正式實作必須交給另一位具名 implementation owner。

本版包含 Router 的 metadata-only context-load telemetry。它可在本機比對 baseline 與 Router run 的 provider input token、ContextView 預算、來源宣告與驗收品質；資料只寫入你指定的 ignored JSONL，絕不輸出原文、prompt、來源 URI 或 Secret。

它不會自動截取 Codex 或 Claude Code 的 token。只有 Agent runner 回填 provider 實際 input token，且 JSONL 配對驗證通過時，才可宣稱 Router 真的降低了 context 負載。

## 內含哪些 skill

| Skill | 用途 |
| --- | --- |
| `johnny-project-takeover` | 先進入 Wayfinder，再依 Router 與 Workflow 收斂下一步，並以目標專案自身規範為優先。 |
| `apply-reusable-modules` | 從 `library/MODULE_CATALOG.md` 選擇最小且適合的 `READY` 模組；不會自動複製模組。 |

兩個平台共用此 repo 根目錄唯一的 `skills/`。Workflow、Defined Wayfinder、Router POC 與 module catalog 也都是同一份；差別只在各自的外掛描述檔。

## 在公司使用前先知道的事

把外掛安裝在你「個人」的 Codex 或 Claude Code 使用者範圍，**不要**複製或安裝到公司 repository。之後照常開啟公司專案，在 task 裡呼叫 skill 即可。

公司 repo 裡自己的 `AGENTS.md`、`Workflow.md`、安全規範、測試與 Git 政策仍是最高優先。Johnny AI Skill 只是外部控制平面，協助 Agent 判斷安全的下一步；它不會覆寫公司規範，也不會替公司專案增加依賴。

你的 GitHub 帳號必須能 clone 此 private repo。先讓 Git 或 SSH 完成正常登入；不要把 personal access token 寫進指令、設定檔或公司 repo。

## Codex 使用方式

### 只需安裝一次

在個人終端機、且不在公司專案資料夾內執行：

```powershell
codex plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill --ref main
```

重新啟動 Codex（或重新整理 Plugins Directory），找到 **Johnny AI Skill** marketplace，安裝 `johnny-ai-skill`。這個動作不會把任何檔案複製到公司 repo。

### 接管公司專案

1. 正常開啟公司 repository 的新 Codex task。
2. 輸入：

   ```text
   Use $johnny-project-takeover to take over this project safely.
   ```

3. 只有在要評估現有通用功能時，再輸入：

   ```text
   Use $apply-reusable-modules to select the smallest safe module set.
   ```

第一個 skill 會先讀取目標專案本地規範；只有在目標專案未建立流程時，才以本外掛的 Workflow 當作備援流程。

若要驗證 Router 是否降低 context，依 `library/workflow_router/README.md` 在本機 ignored `.johnny-router/router-usage.jsonl` 保存配對資料，再執行 telemetry CLI；不要把公司原文或 prompt 交給外掛。

### 更新或拔除

```powershell
codex plugin marketplace upgrade johnny-ai-skill
codex plugin marketplace remove johnny-ai-skill
```

拔除的只有你 Codex 環境中的 skill 與指引；公司 repository 不會被修改。

## Claude Code 使用方式

Claude Code 透過 `.claude-plugin/plugin.json` 讀取同一個根目錄 `skills/`，因此 skill 會有 `johnny-ai-skill` 命名空間。

### 只需安裝一次

在個人終端機、且不在公司專案資料夾內執行：

```powershell
claude plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill
claude plugin install johnny-ai-skill@johnny-ai-skill --scope user
```

若 private repo 無法讀取，先確認同一帳號可用 Git 或 SSH clone。使用 GitHub CLI 時可安全地執行：

```powershell
gh auth login
gh auth setup-git
```

重新開啟 Claude Code session，或在既有 session 輸入 `/reload-plugins`。

### 接管公司專案

1. 如常用 Claude Code 開啟公司 repository。
2. 輸入：

   ```text
   /johnny-ai-skill:johnny-project-takeover
   ```

3. 需要選擇通用模組時才輸入：

   ```text
   /johnny-ai-skill:apply-reusable-modules
   ```

接著補上本次專案目標即可。Claude Code 先取得此共用 skill，但在採取任何動作前仍必須遵守公司專案的本地規範。

Context-load telemetry 同樣由本機 Agent runner 建立 JSONL 證據；Claude Code plugin 本身不攔截 token，也不把公司內容上傳或寫進 repo。

### 更新、驗證或拔除

```powershell
claude plugin marketplace update johnny-ai-skill
claude plugin update johnny-ai-skill@johnny-ai-skill
claude plugin uninstall johnny-ai-skill@johnny-ai-skill --scope user
claude plugin marketplace remove johnny-ai-skill --scope user
```

若要在本 repo 的 clone 根目錄進行一次 Claude Code 煙霧測試：

```powershell
claude plugin validate .
claude --plugin-dir .
```

Claude 的 `plugin.json` 故意不寫版本號，讓它以 Git commit SHA 辨識版本；每次新 commit 都可以被視為可更新版本，不需要重複維護第二份版本號。

## 拔除保證

這個外掛只裝在使用者範圍，不會被 commit 到目標專案。要完全拔除時，執行上方對應平台的移除命令，然後重新開啟 Agent session。公司專案會保留完全相同的 checkout、原始碼、依賴、CI、部署設定與 Git history；消失的只有這套可選的 workflow skill。
