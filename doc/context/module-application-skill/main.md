# Module Application Skill Context

## Wayfinder 決策

```text
Decision: GO
Target: 已完成的本機可重用 Python 模組
Problem: AI 為找尋可用能力而載入整個 library，造成 Context／token 膨脹，且容易讀到不相干或未完成模組。
POC: 以單一短卡片目錄加上一個可攜 Codex skill，強制先選擇、再按最小閱讀順序載入。
Success: 已交付卡片可精確對應現有 12 個 READY 模組；未命中需求明確 fail closed；skill 格式通過驗證。
Out of scope: 打包發行、全域安裝、移動既有模組、實際跨專案寫入、將未完成 Kotlin／C# 候選偽裝成可用模組。
Authority: 使用者於 2026-08-02 的「整理起來」授權本機 POC 與單一文件／skill ticket。
```

## Grill 收斂

- 卡片內容只能含用途、公開 import、直接相依與最小閱讀路徑；不得收錄原始碼或長篇摘要。
- 選擇器只降低載入量，不提供採用或實作權限；目標專案仍依自己的 Workflow 執行。
- `workflow-router-poc` 只標為 POC，不能與可用領域模組混淆。
