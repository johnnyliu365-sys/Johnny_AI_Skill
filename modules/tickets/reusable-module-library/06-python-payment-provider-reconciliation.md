# 06｜Python 金流 Fake Provider 與對帳狀態機

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§金流串接） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `DONE` |
| 環境 | `LOCAL` |
| 責任邊界 | payment provider port、fake provider、退款結果與可重複對帳 |
| 禁止修改 | 真實 支付provider丙、支付provider甲、支付provider乙、憑證、HTTP、Webhook、發票與來源程式 |

## 可觀察結果

對相同 provider 事件重播時不會重複發放權益；未知／衝突結果保留為人工審查狀態而非猜測成功。

## 實作範圍與來源追溯

- 前置依賴：Ticket 05。
- 預定實際程式碼：`library/金流串接/python/provider_ports/`、`reconciliation/`。
- 參考：SourceProjectA 支付provider丙／支付provider甲 對帳與續訂流程的狀態分解，不重用其路由、簽章、設定或 API 格式。

## TDD 設計

1. 正常：fake authorization／confirm／refund 產生可驗證結果。
2. 外部失敗：timeout、重播、未知 transaction 與 conflicting final state fail closed。
3. 回歸：對帳永遠檢查既有處理權與帳本事件。

## 完成紀錄

- 實作：`library/金流串接/python/provider_ports/` 與 `reconciliation/`，提供授權／確認／退款 port、無網路 fake provider、不可變對帳 journal 與人工審查結果。
- 行為：相同 provider event ID 重播只得到已處理結果；timeout、未知交易、所有權不符、journal 遺失但帳本已處理、以及最終狀態衝突均停在人工審查，絕不猜測成功。
- 驗證：`python -m unittest discover -s tests`（25 passed）、`python -m mypy --strict library tests/test_payment_provider_reconciliation.py tests/test_payment_contracts_ledger.py tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（29 source files 無問題）、`python -m py_compile ...` 與 provider event 重播不新增權益 smoke test 均通過。
- Review：`APPROVED`，詳見 `doc/reviews/reusable-module-library/06-python-payment-provider-reconciliation-code-review.md`。
- Ticket commit：`6c7d9dc`（`feat: add fake payment reconciliation`）。
- 來源專案未被修改、搬移、刪除或新增任何檔案。
