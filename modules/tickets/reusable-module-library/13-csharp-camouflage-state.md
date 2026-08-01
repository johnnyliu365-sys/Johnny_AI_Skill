# 13｜C# 偽裝狀態機

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／C#） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 純 C# 顏色／匹配／衰退／捕獲狀態機 |
| 禁止修改 | CamouflageHideSeek、Unity MonoBehaviour、場景、角色、輸入、資產與建置 |

## 可觀察結果

狀態機可套用顏色、依時間衰退、與環境比較並回報明確匹配結果；非法強度與時間輸入遭拒。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/csharp/camouflage_state/`。
- 參考：CamouflageHideSeek `CamouflageState`；只重建非 Unity 的純狀態邏輯。

## TDD 設計

1. 正常：套色、衰退、匹配更新。
2. 錯誤：非法強度、負時間與無顏色狀態有明確結果。
3. 回歸：相同輸入序列得到相同狀態。
