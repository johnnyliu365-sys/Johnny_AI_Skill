# 07｜Python 可靠性核心

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／可靠性） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | in-memory fake-backed outbox、worker、expected-state guard 與 emergency stop 契約 |
| 禁止修改 | 來源專案D 資料庫、tenant 設定、LINE server、真實訊息或來源檔案 |

## 可觀察結果

相同 idempotency key 只產生一件工作；一次僅一個 worker claim；預期狀態衝突不假成功；緊急停止攔截待送工作並保留 audit。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/python/reliability_core/`。
- 參考：來源專案D `outbox_store`、`durable_job_worker`、`state_transition_guard`、`tenant_mode_control`。

## TDD 設計

1. 正常：enqueue、claim、complete 的單一工作流。
2. 違規：重複 key、stale expected state、未知 scope 均遭拒。
3. 外部失敗：sender failure 可稽核，emergency stop 轉為 blocked 而不送出。
