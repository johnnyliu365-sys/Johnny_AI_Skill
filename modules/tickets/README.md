# 模組工單

此目錄只存放已獲 SPEC 核准後建立的垂直工單。`reusable-module-library` 的工單現為 `PLANNED`，待使用者第二次核准。

## 稽核入口

本專案踩過的雷、證據與修法的統整索引：[PITFALL-REGISTER.md](PITFALL-REGISTER.md)。
debug 或稽核任何一條線之前先讀它——多數「新」問題都是登記簿裡某一族的再現。

| Child ID | Kind | Revision | LF SHA-256 | Lifecycle | Reference |
| --- | --- | --- | --- | --- | --- |
| `PITFALL-REGISTER` | `AUDIT_REGISTER` | `20260907-D9` | `4217b0c2ce39ed2214d427d2bffd07950befb515a7c543115b2081c28e5132c7` | `ACTIVE` | [PITFALL-REGISTER.md](PITFALL-REGISTER.md) |

## Plugin adoption quality

| Child ID | Kind | Revision | LF SHA-256 | Lifecycle | Reference |
| --- | --- | --- | --- | --- | --- |
| `TICKET-PARTITION-PLUGIN-ADOPTION-QUALITY` | `PARTITION_INDEX` | `20260907-02` | `f192b189f448d88c418021d78e7a880d15fa7c4df6d78a38f4bb1a416eeb63ad` | `ACTIVE` | [plugin-adoption-quality/README.md](plugin-adoption-quality/README.md) |

## Controlled verification

| Child ID | Kind | Revision | LF SHA-256 | Lifecycle | Reference |
| --- | --- | --- | --- | --- | --- |
| `TICKET-PARTITION-CONTROLLED-VERIFICATION` | `PARTITION_INDEX` | `70` | `cf8cb46ae4a6cff0fb716f12f8952e0611acc5501ee4f7f2e59f55c86488dbbd` | `CVE_D9_INTEGRATION_PREPARATION` | [controlled-verification/README.md](controlled-verification/README.md) |

## MSIX capability and environment actions

[`local-orchestration-installer/README.md`](local-orchestration-installer/README.md)
indexes owner-authorized capability research and isolated-environment operational
actions and the approved MSIX SPEC revision 04's bounded successor work. Research
and environment evidence do not qualify package effects. The same index preserves
historical installer tickets and their blocked/retired status.

## Owner visibility

[`owner-visibility/`](owner-visibility/README.md)：Router 能驅動 Claude 分支後，owner 卻看不到任何進行中的工作。桌面 app 的三條顯示路徑都已實測堵死，所以可見介面必須做在 app 之外。V1 為 `OPEN`，已分派給 UI 實作負責人，第一階段只做靜態樣張供 owner 決定方向。
