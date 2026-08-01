# 11｜Kotlin 離線地理解析

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／Kotlin） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 地址 key 正規化、離線表 lookup 與座標範圍驗證 |
| 禁止修改 | 來源專案C Android app、資產、位置資料、地圖 provider 與網路呼叫 |

## 可觀察結果

呼叫端可用明確地址／座標值物件進行離線查詢；未知地址與越界座標回傳具名結果，不猜測位置。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/kotlin/offline_geo_resolution/`。
- 參考：來源專案C `OfflineAddressResolver` 與位置分類；排除 Android Context、asset 與台灣實際地理資料。

## TDD 設計

1. 正常：正規化 key 命中手工 fixture。
2. 錯誤：空 key、重複 key、越界／無效座標遭拒。
3. 回歸：輸入集合的解析結果可重現。
