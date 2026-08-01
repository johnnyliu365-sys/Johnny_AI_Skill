# 10｜Python 推薦、獎勵與任務純規則核心

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／互動） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 可設定的推薦資格、獎勵限額與任務進度規則 |
| 禁止修改 | SourceProjectA 健康資料、會員、經銷、點數、推播、資料庫與商業規則 |

## 可觀察結果

以自訂 policy 與事件輸入評估資格／進度；重複事件不重複獎勵，未知 policy 或事件預設拒絕。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/python/engagement_rules/`。
- 參考：SourceProjectA referral、reward、mission service 的去重與資格概念；排除所有健康、經銷、會員與資料庫欄位。

## TDD 設計

1. 正常：合格事件增加可解釋進度。
2. 違規：重複事件、無效 policy、已到上限與不合格狀態遭拒。
3. 回歸：獎勵事件以穩定 key 去重。
