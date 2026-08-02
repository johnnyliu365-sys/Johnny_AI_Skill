# Johnny AI Skill

這是一套可安裝、可停用、可移除的 Codex workflow plugin。它提供專案接管流程、Router／Wayfinder 規範，以及最小化的通用模組選擇能力；它不是公司專案的套件、runtime service、MCP server、hook 或 CI 依賴。

## 核心契約

| 層級 | 放置位置 | 移除 Johnny AI Skill 後 |
| --- | --- | --- |
| workflow、Wayfinder、Router 與 module catalog | plugin 的安裝快取 | 不再提供給 Agent；公司專案不受影響 |
| 公司專案的程式、設定、CI、資料與部署 | 公司自己的 repository | 照常建置、測試、部署與維護 |
| 經核准 ticket 產生的公司專案變更 | 公司自己的 commit | 保留且不依賴 plugin |

不得讓公司專案以 symlink、Git submodule、相對路徑 import、package dependency、CI dependency 或 hook 依賴本 plugin 的 checkout／cache。若經核准採用通用模組的行為，該實作必須由公司專案自己持有、測試與提交；plugin 只保留為版本化的設計與來源參照。

## 安裝：從 private GitHub repo 掛載

前提是目前帳號可讀取 [johnnyliu365-sys/Johnny_AI_Skill](https://github.com/johnnyliu365-sys/Johnny_AI_Skill)。在任意本機目錄執行：

```powershell
codex plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill --ref main
```

重新啟動 ChatGPT desktop／Codex，開啟 Plugins Directory，選擇 **Johnny AI Skill** marketplace 並安裝 `johnny-ai-skill`。接著在公司專案的工作區中使用：

```text
Use $johnny-project-takeover to take over this project safely.
```

需要現有通用功能時，使用：

```text
Use $apply-reusable-modules to select the smallest safe module set.
```

首次只做 Intake → Wayfinder。Agent 必須依 plugin 的 `Workflow.md` 與 `Defined_wayfinder.md` 走關卡；公司專案已有 `AGENTS.md` 或 workflow 時，該專案規範優先，plugin 不會自動覆寫或複製任何檔案。

## 接管中的公司專案

1. 在公司專案開啟 Codex task 並安裝／啟用 plugin；不要複製本 repo 到公司 repo。
2. Plugin 先讀取公司專案既有規範，再依 `POC` 初始階段執行 Wayfinder。
3. 所有公司專案的 Context、SPEC、ticket、程式、測試與 commit 都存在公司 repo；只有明確核准後才寫入。
4. 已完成的公司專案變更必須自行通過其 build、test 與 deployment 驗證，不得把 plugin 當作執行條件。

`AGENTS.md` 若被公司專案採用為本機 Agent 入口，必須位於該專案的 `.gitignore` 範圍；本 plugin 不會自動建立它。

## 拔除

1. 先確認公司專案沒有未提交的工作，並在公司 repo 自行跑完其驗證命令。
2. 在 Plugins Directory 停用或解除安裝 `johnny-ai-skill`。
3. 若連 marketplace 來源也不再需要，再執行：

```powershell
codex plugin marketplace remove johnny-ai-skill
```

拔除後，plugin 的 skill、Workflow、Router 指引與 module catalog 不再注入 Agent context；公司專案的程式與既有交付物維持原狀並可繼續運行。

## 更新

此 repo 的 marketplace 使用 `main`。更新後執行：

```powershell
codex plugin marketplace upgrade johnny-ai-skill
```

重新啟動 ChatGPT desktop／Codex，再開啟新的 task，讓新 task 載入更新後的 plugin。需要可重現性時，將公司專案 Context 或 ticket 記錄使用的 Johnny AI Skill commit SHA。
