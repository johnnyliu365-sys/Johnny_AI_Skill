# 01｜建立模組庫根目錄與 README

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§使用者流程 AC-1） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 建立 `library/`、NLP、金流串接、功能集群與語言子目錄的 README 導覽 |
| 禁止修改 | 所有來源專案、任何實作原始碼、外部設定、Provider 與資料 |

## 使用者拍板與可觀察結果

使用者可從 `library/README.md` 尋找各集群，且每個本 ticket 新增的資料夾都有 README 說明用途與後續 ticket。

## 實作範圍、依賴與 ticket elements

- 實際原始碼路徑：本 ticket 不建立程式碼，只建立本專案 README。
- 依賴：無。
- 來源追溯：無程式碼複製；只引用本專案已建立的 SPEC。

## TDD 設計

1. 正常行為：檢查所有規格宣告的頂層集群與語言目錄皆有 README。
2. 輸入錯誤：缺少 README 或 README 未含責任／禁止用途時檢查失敗。
3. 回歸：README 不得包含來源專案的秘密、PII 或環境值。

## 完成定義與證據

- 新增目錄與 README 檢查通過。
- `git diff --check` 通過。
- README 明示來源專案完全唯讀。
