# Johnny AI Skill Plugin Distribution POC 規格

| 欄位 | 內容 |
| --- | --- |
| 規格 ID | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` |
| 狀態 | `APPROVED` |
| 專屬 Context | `doc/context/plugin-distribution/main.md` |
| 需求變更 | `CHG-20260802-004` |

## 目標

將 `Johnny_AI_Skill` 包裝為 private GitHub 可安裝、可停用、可拔除的 Codex plugin，並確保它不是任何被接管公司專案的 runtime dependency。

## 範圍

- `.codex-plugin/plugin.json`：`johnny-ai-skill` metadata 與 `./skills/` 入口。
- `.agents/plugins/marketplace.json`：同一 private repository 的 Git repository-root source。
- `skills/johnny-project-takeover/`：目標專案規範優先、Router 最小載入、Wayfinder 與可拔除邊界。
- `README.md`：安裝、接管、更新與移除操作說明。

## 驗收條件

1. `quick_validate.py` 對 `johnny-project-takeover` 與 `apply-reusable-modules` 都輸出 `Skill is valid!`。
2. `validate_plugin.py .` 通過，兩份 JSON 可解析，且 `git diff --check` 無輸出。
3. manifest 未宣告 `mcpServers`、`apps` 或 hooks；repository root 沒有 `.mcp.json`、`.app.json`、`hooks/` 或 `assets/`。
4. skill 與 README 禁止 target project 建立 plugin cache／checkout 的 symlink、submodule、runtime import、CI dependency 或 hook。
5. 不修改公司專案、使用者的 `~/.codex` 設定或任何外部 Provider。
