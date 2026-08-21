# 10｜Python 推薦、獎勵與任務純規則核心

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／互動） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `DONE` |
| 環境 | `LOCAL` |
| 責任邊界 | 可設定的推薦資格、獎勵限額與任務進度規則 |
| 禁止修改 | 來源專案A 健康資料、會員、經銷、點數、推播、資料庫與商業規則 |

## 可觀察結果

以自訂 policy 與事件輸入評估資格／進度；重複事件不重複獎勵，未知 policy 或事件預設拒絕。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/python/engagement_rules/`。
- 參考：來源專案A referral、reward、mission service 的去重與資格概念；排除所有健康、經銷、會員與資料庫欄位。

## TDD 設計

1. 正常：合格事件增加可解釋進度。
2. 違規：重複事件、無效 policy、已到上限與不合格狀態遭拒。
3. 回歸：獎勵事件以穩定 key 去重。

## 完成紀錄

- 實作提交：`f0a4bfc`（`feat: add engagement rules core`）。
- 驗證：`python -m unittest discover -s tests`（41 passed）、`python -m mypy --strict ...`（46 source files 無問題）、`py_compile` 與本地 policy smoke test 均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/10-python-engagement-rules-code-review.md`。
- 邊界確認：四個來源專案與所有外部服務均未修改、搬移、刪除、新增或啟動。
