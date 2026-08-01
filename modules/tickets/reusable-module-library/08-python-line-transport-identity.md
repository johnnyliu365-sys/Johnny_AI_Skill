# 08｜Python 訊息 Transport 與身份解析

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／LINE transport） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `DONE` |
| 環境 | `LOCAL` |
| 責任邊界 | 訊息 request／result port、redacted failure 與 stable identity／display label 分離 |
| 禁止修改 | LINE credentials、webhook、租戶檔、SourceProjectA／Dispatch 的 router 與外部發訊 |

## 可觀察結果

fake transport 可驗證成功與 provider 失敗；唯一 identity 不會被顯示名稱覆寫，未知身份預設 fail closed。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/python/line_transport/`、`identity_resolution/`。
- 參考：來源專案D 的 `line_messaging_adapter` 與 `driver_identity_resolver`；排除 tenant／LINE 專有格式。

## TDD 設計

1. 正常：fake sender 與顯示名稱 fallback。
2. 外部失敗：provider 失敗會被分類與遮罩。
3. 回歸：message request 不含 token 或隱含身份授權。

## 完成紀錄

- 實作提交：`fd5187b`（`feat: add fake message transport identity`）。
- 驗證：`python -m unittest discover -s tests`（33 passed）、`python -m mypy --strict ...`（40 source files 無問題）、`py_compile` 與 fake transport smoke test 均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/08-python-line-transport-identity-code-review.md`。
- 邊界確認：四個來源專案與所有外部服務均未修改、搬移、刪除、新增或啟動。
