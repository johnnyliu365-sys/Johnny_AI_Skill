# Element：Ticket 11 Kotlin Offline Geo Resolution

## 對應

- SPEC：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`
- CHG：`CHG-20260801-001`
- Ticket：`11-kotlin-offline-geo-resolution`

## 實際原始碼與測試

- Domain core：`library/功能集群/kotlin/offline_geo_resolution/src/main/kotlin/reusable/offlinegeo/OfflineGeoResolver.kt`
- Executable TDD test：`library/功能集群/kotlin/offline_geo_resolution/src/test/kotlin/reusable/offlinegeo/OfflineGeoResolverTest.kt`
- Module contract：`library/功能集群/kotlin/offline_geo_resolution/README.md`

## 公開契約

- 值型別：`RawAddressKey`、`NormalizedAddressKey`、`RelaxedAddressKey`、`GeoCoordinate`。
- Policy：`AddressKeyPolicy`、`CoordinateValidator`、`FiniteCoordinateValidator`。
- Resolver：`OfflineGeoResolver.fromEntries()`、`OfflineGeoResolver.empty()`、`OfflineGeoResolver.resolve()`。
- 結果：`GeoResolutionResult` sealed interface 與 `GeoMatchKind` enum。

## 驗證證據

TDD 紅燈：只有測試存在時，Kotlin compiler 因上述正式型別尚未建立而以 exit code 1 失敗。

綠燈：Kotlin 2.3.21 以 `-Werror` 編譯正式原始碼與測試，執行 `OfflineGeoResolverTest` 成功。測試覆蓋正規化精確命中、唯一放寬命中、歧義拒絕、無效 key／座標，以及重複精確 key 的第一筆穩定性。

## 來源隔離

行為僅唯讀參照 來源專案C 的 `OfflineAddressResolver` 與其測試意圖。沒有讀取或複製 optional address pack、真實地址、座標、Android 資產、Provider 或其他來源專案檔案。
