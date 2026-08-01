# 工作進度報告

## PRG-20260801-001｜通用功能模組庫文件基準

- 狀態：`TICKETING`
- 完成內容：已在使用者核准後啟用正式文件結構，建立共同 Context、PRD、需求變更、安全邊界與已核准 SPEC。
- 未開始內容：未建立實作模組、測試、Provider adapter、外部操作或來源程式碼複製；工單待第二次核准。
- 來源專案狀態：僅唯讀盤點。
- 下一閘門：使用者核准垂直工單的順序與範圍後，才可從 Ticket 01 的 TDD 開始。

## PRG-20260801-002｜Ticket 01 模組庫目錄與 README

- 狀態：`DONE`，等待使用者確認。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`01-library-root-and-readmes`。
- 實際內容：新增 `library/`、NLP、金流串接、功能集群與 Python／Kotlin／C# 語言目錄的 README；新增目錄契約測試與 ticket review report。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 驗證：紅燈為缺少 `library/README.md`；綠燈 `python -m unittest tests/test_library_readme_catalog.py`（2 passed）；`python -m py_compile tests/test_library_readme_catalog.py` 通過；root plus three functional categories 的 smoke test 通過；`git diff --check` 通過。
- 靜態型別工具：`mypy`、`pyright` 未安裝；沒有新增公開生產模組，測試採顯式型別註記。後續 Python 實作 ticket 需取得嚴格工具鏈決策。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/01-library-root-and-readmes-code-review.md`。
- Ticket commit：`9b218a9`（`docs: add reusable library catalog`）。
- 下一張候選：`02-python-nlp-contracts`；等待使用者明確確認。

## PRG-20260801-003｜Ticket 02 Python NLP 強型別文字契約

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`02-python-nlp-contracts`。
- 實際內容：在 `library/NLP/python/text_contracts/` 新增 `TextInput`、`NormalizedText`、分類結果、欄位擷取結果、具名拒絕結果與純本地 Unicode 正規化；每個公開狀態以 DTO、Enum 或具名值物件表示。
- 開發期工具：使用者已明確授權 `mypy --strict`；已安裝並以 `requirements-dev.txt` 固定 `mypy==2.3.0`。
- 驗證：紅燈為找不到尚未建立的 `text_contracts` 模組；綠燈 `python -m unittest discover -s tests`（5 passed）；`python -m mypy --strict library tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（7 source files 無問題）；`python -m py_compile ...` 與未驗證外部文字拒絕 smoke test 皆通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/02-python-nlp-contracts-code-review.md`。
- Ticket commit：`88fbfc0`（`feat: add typed NLP text contracts`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`03-python-nlp-rule-parsers`；必須等待使用者明確確認後才可開始。

## PRG-20260801-004｜Ticket 03 Python NLP 規則式欄位抽取器

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`03-python-nlp-rule-parsers`。
- 實際內容：在 `library/NLP/python/rule_parser/` 新增固定規則、frame 位置、解析理由與結果 DTO；從同一 frame 擷取實際標記值，不跨 frame 合併或補造資料。
- 驗證：紅燈為找不到尚未建立的 `rule_parser` 模組；綠燈 `python -m unittest discover -s tests`（12 passed）；`python -m mypy --strict library tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（11 source files 無問題）；`python -m py_compile ...` 與跨 frame 拒絕 smoke test 皆通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/03-python-nlp-rule-parsers-code-review.md`。
- Ticket commit：`d03880e`（`feat: add deterministic NLP rule parser`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`04-python-nlp-provider-boundaries`；必須等待使用者明確確認後才可開始。

## PRG-20260801-005｜Ticket 04 Python NLP Provider 邊界

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`04-python-nlp-provider-boundaries`。
- 實際內容：在 `library/NLP/python/provider_ports/` 新增請求／成功／失敗 DTO、Provider Protocol、retryability、唯一 raw payload validator 與無網路的 fake provider；不含實體 provider、HTTP、影像資料或憑證。
- 回滾點：開始前建立 checkpoint `76c9cbd` 與本地 tag `rollback/ticket-04-start-20260801`；Ticket 實作另有獨立 commit。
- 驗證：紅燈為找不到尚未建立的 `provider_ports` 模組；綠燈 `python -m unittest discover -s tests`（16 passed）；`python -m mypy --strict library tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（16 source files 無問題）；`python -m py_compile ...` 與未知 payload 拒絕 smoke test 皆通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/04-python-nlp-provider-boundaries-code-review.md`。
- Ticket commit：`02fa06f`（`feat: add typed NLP provider boundary`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`05-python-payment-contracts-ledger`；必須等待使用者明確確認後才可開始。

## PRG-20260801-006｜Ticket 05 Python 金流契約與訂閱帳本

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`05-python-payment-contracts-ledger`。
- 實際內容：在 `library/金流串接/python/payment_contracts/` 建立整數最小貨幣單位、幣別、付款意圖、idempotency key 與狀態；在 `subscription_ledger/` 建立不可變事件帳本、權益與具名拒絕結果。
- 驗證：紅燈為找不到尚未建立的金流模組；綠燈 `python -m unittest discover -s tests`（20 passed）；`python -m mypy --strict library tests/test_payment_contracts_ledger.py tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（23 source files 無問題）；`python -m py_compile ...` 與單一 idempotency key 授與一次權益 smoke test 均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/05-python-payment-contracts-ledger-code-review.md`。
- Ticket commit：`17ed764`（`feat: add payment contracts and ledger`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`06-python-payment-provider-reconciliation`；必須等待使用者明確確認後才可開始。

## PRG-20260802-001｜Ticket 06 Python 金流 Fake Provider 與對帳狀態機

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`06-python-payment-provider-reconciliation`。
- 實際內容：在 `library/金流串接/python/provider_ports/` 建立強型別授權、確認、退款結果與無網路 fake provider；在 `reconciliation/` 建立不可變 journal、重播保護與人工審查狀態機。
- 驗證：紅燈為找不到尚未建立的 provider／reconciliation 模組；綠燈 `python -m unittest discover -s tests`（25 passed）；`python -m mypy --strict library tests/test_payment_provider_reconciliation.py tests/test_payment_contracts_ledger.py tests/test_nlp_provider_ports.py tests/test_nlp_rule_parser.py tests/test_nlp_text_contracts.py tests/test_library_readme_catalog.py`（29 source files 無問題）；`python -m py_compile ...` 與 provider event 重播不產生第二筆權益 smoke test 均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/06-python-payment-provider-reconciliation-code-review.md`。
- Ticket commit：`6c7d9dc`（`feat: add fake payment reconciliation`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`07-python-reliability-core`；必須等待使用者明確確認後才可開始。
