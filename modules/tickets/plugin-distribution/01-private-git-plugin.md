# 01｜Private Git plugin

| 欄位 | 內容 |
| --- | --- |
| 對應規格 | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` |
| 需求變更 | `CHG-20260802-004` |
| 狀態 | `DONE` |

## 可觀察結果

private GitHub repository 可作為 Codex marketplace 來源，並安裝 repository-root 的 `johnny-ai-skill`。主 skill 只提供工作流程控制平面；解除安裝後，公司專案沒有任何 runtime、CI 或 source-path 依賴。

## 完成證據

- `.codex-plugin/plugin.json` 指向 `./skills/`，並以 `johnny-ai-skill` 作為 manifest name。
- `.agents/plugins/marketplace.json` 以 repository-root Git URL、`main` 和完整 policy 提供同名 plugin。
- 兩份 skill 均通過 UTF-8 模式的 standard validator；plugin validator、JSON parse 與 `git diff --check` 均通過。
- 未建立或宣告 MCP、App、hook、runtime service、使用者設定或公司專案檔案。
- 功能 commit：`cb2b3e4`（`feat: package detachable project takeover plugin`）。
