# 12｜C# 卡牌規則引擎

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／C#） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 通用卡牌、資源、回合、動作合法性與效果解析的純領域模型 |
| 禁止修改 | PoliticsCardGame、Unity UI、政治題材、卡片內容、遊戲資產與建置流程 |

## 可觀察結果

以自訂卡片定義進行回合與動作驗證；非法資源、目標或狀態遭拒，結果可由不可變事件追溯。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/csharp/card_rules_engine/`。
- 參考：PoliticsCardGame 的 Model、GameEngine、GameActionValidator；只重建通用規則模式。

## TDD 設計

1. 正常：合法出牌、攻擊與回合切換。
2. 違規：資源不足、非法目標與錯誤回合遭拒。
3. 回歸：效果解析順序與結果事件可重現。
