# Plugin Distribution Context

## Wayfinder 決策

```text
Decision: GO
Target: Johnny_AI_Skill private GitHub repository
Problem: 既有可攜 skill 只能作為 repo 內來源，無法以可安裝、可停用與可移除的整套 plugin 供不同專案使用。
POC: 將 repository root 建為 Git marketplace 可安裝 plugin，並以主接管 skill 約束它只作外部控制平面。
Success: manifest、marketplace 與 bundled skills 可被靜態驗證；README 說明 Git 安裝、更新、移除與公司專案無 runtime 耦合的邊界。
Out of scope: 寫入個人 Codex 設定、安裝 plugin、公司專案寫入、MCP、hook、App、runtime package、Provider、Secret、部署。
Authority: 使用者於 2026-08-02 明確要求將整套 skill 作為可套用／拔除的 GitHub plugin，且公司專案在拔除後持續運行。
```

## Grill 收斂

- Plugin source 使用 Git repository root；marketplace 與 plugin 均以 `johnny-ai-skill` 為穩定識別。
- 預設 `main` 用於取得更新；需要可重現性時由目標專案 Context／ticket 記錄實際 commit SHA。
- 公司專案不得依賴 plugin checkout 或 cache。選中的模組若經核准實作，結果必須在公司 repository 中自有、測試與提交。
- 不宣告 `.mcp.json`、`.app.json`、hooks 或 assets；因此沒有背景服務、外部連線或自動執行面。
