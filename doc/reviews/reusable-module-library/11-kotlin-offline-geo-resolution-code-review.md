# Code Review：11 Kotlin Offline Geo Resolution

## 範圍

- SPEC：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`
- 變更：`CHG-20260801-001`
- Ticket：`11-kotlin-offline-geo-resolution`
- 審閱對象：`library/功能集群/kotlin/offline_geo_resolution/`、`library/功能集群/kotlin/README.md`、`library/MODULE_CATALOG.md` 與 `modules/element/kotlin/reusable-module-library/11-kotlin-offline-geo-resolution/README.md`

## 審閱結論

`APPROVED`

## 必要驗證項目與證據

| 項目 | 結果 | 證據 |
| --- | --- | --- |
| 清晰易懂與 P0 強型別 | 通過 | key、座標、entry 皆為具名 value type／data class；成功、無效、未知與歧義以 `GeoResolutionResult` sealed interface 表達；比對種類以 `GeoMatchKind` enum 表達。正式原始碼與測試均無 `Any` 或未驗證動態資料。 |
| 編碼規範與分層 | 通過 | `OfflineGeoResolver` 為純 domain core；正規化與放寬語法由 `AddressKeyPolicy` 注入，座標接受範圍由 `CoordinateValidator` 注入。沒有將來源專案的 Android、地名或地區商業規則帶入核心。 |
| 邏輯正確 | 通過 | 實作先查 exact key；未命中才查 policy 明確給出的 relaxed key；唯一候選成功、多候選回傳 `AmbiguousRelaxedKey`。重複 exact key 使用 `putIfAbsent` 保留第一筆，與參照 resolver 一致。 |
| 邊界與異常 | 通過 | 空白／無法正規化 key 回傳 `InvalidAddressKey`；不存在 key 回傳 `UnknownAddressKey`；`FiniteCoordinateValidator` 排除 `NaN` 與無限值；建表時被拒絕座標不進入索引。 |
| 安全與效能 | 通過 | 不讀寫檔案、asset、資料庫、網路、GPS、Provider 或使用者位置；不含真實地址、座標、國界或 secret。索引建置只使用本地 LinkedHashMap／LinkedHashSet，查詢為 map lookup。 |
| 測試覆蓋與 smoke test | 通過 | 可執行測試覆蓋正規化 exact fixture、唯一 relaxed、relaxed 歧義拒絕、空白 key、無效座標，以及重複 exact key 第一筆穩定性。Kotlin 2.3.21 以 `-Werror` 編譯並執行 test JAR 成功；同一 test JAR 執行作為主要查詢路徑 smoke test 成功。 |
| 依賴合理 | 通過 | 未新增 Gradle、Android、JUnit、網路或執行期第三方相依；模組僅使用 Kotlin/JVM 標準函式庫。Kotlin compiler 2.3.21 以官方 SHA-256 驗證後安裝為開發期工具。 |
| 專案規格符合性 | 通過 | 實作位於 Ticket 指定的 Kotlin 目錄；行為唯讀參照 來源專案C `OfflineAddressResolver` 與其測試意圖。排除 `OptionalOfflineAddressPack`、Android `Context`、asset、Provider 與所有來源資料；四個來源專案沒有被此 ticket 寫入。 |

## 可重跑命令

```text
C:\Users\<user>\Tools\kotlin-compiler-2.3.21\kotlinc\bin\kotlinc.bat -Werror library\功能集群\kotlin\offline_geo_resolution\src\main\kotlin\reusable\offlinegeo\OfflineGeoResolver.kt library\功能集群\kotlin\offline_geo_resolution\src\test\kotlin\reusable\offlinegeo\OfflineGeoResolverTest.kt -include-runtime -d %TEMP%\offline-geo-resolution-test.jar
java -jar %TEMP%\offline-geo-resolution-test.jar
python -m unittest discover -s tests
python -m mypy --strict library tests
git diff --check
```

驗證結果：Kotlin compiler／test JAR 成功；Python 回歸測試 `48 passed`；`mypy --strict` 顯示 `Success: no issues found in 54 source files`；`git diff --check` 通過。

## 後續限制

本模組不是地理編碼服務，不提供自由文字地址解析、國家／區域界限、反向地理編碼、導航、Provider、GPS、持久化、快取、同步、並發控制、日誌或權限判斷。採用端必須在已核准的邊界實作並測試自己的 key policy、地區驗證及資料取得流程。
