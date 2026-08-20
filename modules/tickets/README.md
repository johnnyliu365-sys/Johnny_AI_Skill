# 模組工單

此目錄只存放已獲 SPEC 核准後建立的垂直工單。`reusable-module-library` 的工單現為 `PLANNED`，待使用者第二次核准。

## 稽核入口

本專案踩過的雷、證據與修法的統整索引：[PITFALL-REGISTER.md](PITFALL-REGISTER.md)。
debug 或稽核任何一條線之前先讀它——多數「新」問題都是登記簿裡某一族的再現。

## Owner visibility

[`owner-visibility/`](owner-visibility/README.md)：Router 能驅動 Claude 分支後，owner 卻看不到任何進行中的工作。桌面 app 的三條顯示路徑都已實測堵死，所以可見介面必須做在 app 之外。V1 為 `OPEN`，已分派給 UI 實作負責人，第一階段只做靜態樣張供 owner 決定方向。
