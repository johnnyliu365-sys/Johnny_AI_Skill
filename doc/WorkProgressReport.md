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

## PRG-20260802-002｜Ticket 07 Python 可靠性核心

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`07-python-reliability-core`。
- 實際內容：在 `library/功能集群/python/reliability_core/` 建立不可變 in-memory outbox 快照、scope 與 idempotency guard、單一 worker claim、`JobVersion` 預期狀態檢查、fake sender、audit 與 emergency stop；沒有外部訊息或持久化。
- 驗證：紅燈為找不到尚未建立的 `reliability_core` 模組；綠燈 `python -m unittest discover -s tests`（29 passed）；`python -m mypy --strict library ...`（34 source files 無問題）；`python -m py_compile ...` 與 `OutboxWorker`＋fake sender smoke test（`completed`、3 audit entries）均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/07-python-reliability-core-code-review.md`。
- Ticket commit：`7b56135`（`feat: add local reliability core`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`08-python-line-transport-identity`；必須等待使用者明確確認後才可開始。

## PRG-20260802-003｜Ticket 08 Python 訊息 Transport 與身份解析

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`08-python-line-transport-identity`。
- 實際內容：在 `library/功能集群/python/line_transport/` 建立具名 request／result port、受限的 redacted failure 與無網路 fake transport；在 `identity_resolution/` 建立不可變 stable identity directory、顯示名稱 fallback 與未知 identity fail-closed 結果。
- 驗證：紅燈為找不到尚未建立的 `identity_resolution` 模組；綠燈 `python -m unittest discover -s tests`（33 passed）；`python -m mypy --strict library ...`（40 source files 無問題）；`python -m py_compile ...` 與 fallback identity＋fake provider failure smoke test（`Unknown`、`provider_unavailable`）均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/08-python-line-transport-identity-code-review.md`。
- Ticket commit：`fd5187b`（`feat: add fake message transport identity`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`09-python-event-timeline-audit`；必須等待使用者明確確認後才可開始。

## PRG-20260802-004｜Ticket 09 Python 可重播事件時間線與 Audit

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`09-python-event-timeline-audit`。
- 實際內容：在 `library/功能集群/python/event_timeline_audit/` 建立有限通用事件、不可變 timeline state／audit、unknown unresolved、非法順序／重複 ID conflict，以及 deterministic SHA-256 output hash；不含 raw payload、log 或來源領域資料。
- 驗證：紅燈為找不到尚未建立的 `event_timeline_audit` 模組；綠燈 `python -m unittest discover -s tests`（37 passed）；`python -m mypy --strict library ...`（43 source files 無問題）；`python -m py_compile ...` 與兩次同 input replay 得到相同 hash 的 smoke test（`active`、unresolved 1）均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/09-python-event-timeline-audit-code-review.md`。
- Ticket commit：`655f09d`（`feat: add deterministic timeline audit`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`10-python-engagement-rules`；必須等待使用者明確確認後才可開始。

## PRG-20260802-005｜Ticket 10 Python 推薦、獎勵與任務純規則核心

- 狀態：`DONE`，等待使用者確認下一張工單。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`10-python-engagement-rules`。
- 實際內容：在 `library/功能集群/python/engagement_rules/` 建立可設定資格門檻、進度目標、獎勵允許上限、不可變 state、stable event key 去重與未知／不可能 state fail-closed 結果；不含真實點數、會員或權益。
- 驗證：紅燈為找不到尚未建立的 `engagement_rules` 模組；綠燈 `python -m unittest discover -s tests`（41 passed）；`python -m mypy --strict library ...`（46 source files 無問題）；`python -m py_compile ...` 與本地資格→進度→允許規則 smoke test（`reward_permitted`、1）均通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/10-python-engagement-rules-code-review.md`。
- Ticket commit：`f0a4bfc`（`feat: add engagement rules core`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 的所有檔案、原始碼、資料、設定與外部 Provider 均未觸及。
- 下一張候選：`11-kotlin-offline-geo-resolution`；必須等待使用者明確確認後才可開始。

## PRG-20260802-006｜Router framework POC 核心

- 狀態：`DONE`。
- 對應：`SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H`／`01-poc-router-core`／`CHG-20260802-002`。
- 實際內容：建立 Pydantic Router 契約、Profile transition、最小 Context descriptor／本地 packet 分離、metadata-only citation ledger、LangGraph 封閉分支、OpenAI Agents SDK capability adapter、Temporal human-wait skeleton 與 MCP resource adapter。
- 流程改變：`Workflow.md §0` 現在以 Profile 控制 `POC → MVP → COMMERCIAL`，升級一律經 `REQUIREMENT_CHANGED → WAYFINDER`；AGENTS 只保留該規則的索引。
- 驗證：TDD 紅燈為 `library.workflow_router` 不存在；綠燈 `python -m unittest discover -s tests`（48 passed）、`python -m mypy --strict library tests`（54 source files 無問題）、`python -m py_compile ...` 與無外部服務 smoke 均通過。
- Review：`APPROVED`，`doc/reviews/router-framework/01-poc-router-core-code-review.md`。
- 未修改邊界：沒有啟動模型、Temporal worker、MCP server、網路、資料庫、Secret、Provider 或被接管專案；未建立 commit 或 push。

## PRG-20260802-007｜Module catalog 與可攜 skill

- 狀態：`DONE`。
- 對應：`SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H`／`01-module-catalog-skill`／`CHG-20260802-003`。
- 實際內容：建立 `library/MODULE_CATALOG.md`、`skills/apply-reusable-modules/`、library 最小載入入口與新專案版本化引用指引。
- 驗證：skill creator `quick_validate.py` 輸出 `Skill is valid!`；沒有 TODO；`git diff --check` 通過。
- 限制：未打包、未全域安裝、未移動既有模組，亦未對任何新專案執行寫入。

## PRG-20260802-008｜Ticket 11 Kotlin 離線地理解析

- 狀態：`DONE`，功能集群 `READY_TO_MERGE`。
- 對應：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`／`11-kotlin-offline-geo-resolution`／`CHG-20260801-001`。
- 實際內容：在 `library/功能集群/kotlin/offline_geo_resolution/` 建立純 Kotlin offline key resolver。公開型別包含 key／coordinate 值型別、`AddressKeyPolicy`、`CoordinateValidator`、建表 `Built`／`Rejected(reason)` 結果，以及查詢 `Resolved`／invalid／unknown／ambiguous 結果。
- 來源依據：唯讀參照 來源專案C `OfflineAddressResolver` 的 exact-first、unique-relaxed 與 ambiguous-reject 行為；沒有複製程式、地址、座標、Android asset 或 Provider。正式 ticket 對空 key、無效座標與重複 exact key 的 fail-closed 要求優先於來源的寬鬆建表策略。
- 驗證：初始 API 缺失與 fail-closed 契約各有一輪 TDD 紅燈；Kotlin 2.3.21 `-Werror` 編譯與 test JAR smoke 通過；`python -m unittest discover -s tests` 為 48 passed；`python -m mypy --strict library tests` 為 54 source files 無問題；`git diff --check` 通過。
- Review：`APPROVED`，`doc/reviews/reusable-module-library/11-kotlin-offline-geo-resolution-code-review.md`。
- Ticket commits：`e91f5c5`（`feat: add Kotlin offline geo resolution`）、`c255720`（`fix: reject invalid offline geo index entries`）。
- 未修改邊界：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 來源專案D 未被修改、搬移、刪除或新增任何檔案；沒有啟動 Android、外部 Provider、網路、資料庫、Secret 或部署。

## PRG-20260803-001｜C# 遊戲候選 ticket 核准等待

- 狀態：`AWAITING_TICKET_APPROVAL`。
- 對應：`12-csharp-card-rules-engine`、`13-csharp-camouflage-state`。
- 決定：兩張候選 ticket 單獨不足以構成完整遊戲模組集群，因此維持 `PLANNED`／核准狀態 `PENDING`，不進入 implement。
- 未執行：沒有建立或修改 C# 原始碼、測試、模組、element 索引、review、Unity 專案、資產或任何參照專案檔案。
- 重新評估條件：專案負責人定義完整集群範圍、必要 tickets、依賴與驗收條件後，重走 `grill-with-docs → to-spec → to-tickets` 並取得明確核准。

## PRG-20260802-009｜Johnny AI Skill private Git plugin

- 狀態：`DONE`。
- 對應：`SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H`／`01-private-git-plugin`／`CHG-20260802-004`。
- 實際內容：建立 repository-root `.codex-plugin/plugin.json`、private Git marketplace catalog、`$johnny-project-takeover` 與根目錄 README；既有 `$apply-reusable-modules` 一併由 plugin 載入。
- 拔除邊界：公司專案不得依賴 plugin checkout／cache、symlink、Git submodule、相對 import、package／CI dependency 或 hook；任何核准採用結果須由公司 repository 自有、測試與 commit，因此停用或移除 plugin 後公司專案仍可獨立運行。
- 驗證：兩個 skill 的 UTF-8 validator 均輸出 `Skill is valid!`；plugin validator、JSON parse、`git diff --check` 通過；`python -m unittest discover -s tests` 為 48 passed；`python -m mypy --strict library tests` 為 54 source files 無問題。
- Review：`APPROVED`，`doc/reviews/plugin-distribution/01-private-git-plugin-code-review.md`。
- Ticket commit：`cb2b3e4`（`feat: package detachable project takeover plugin`）。
- 未修改邊界：沒有安裝 plugin、寫入 `~/.codex`、修改公司專案、啟動 MCP／App／hook、使用 Secret、呼叫外部 Provider 或部署。

## PRG-20260802-005 — Claude Code Plugin Distribution POC

| Field | Value |
| --- | --- |
| State | `DONE` |
| Feature commit | `d662993` — `feat: add Claude Code plugin distribution` |
| Specification | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` |
| Ticket | `modules/tickets/claude-code-plugin-distribution/01-claude-code-plugin.md` |
| Delivered | Root Claude plugin manifest, root marketplace catalog, one shared `skills/` source, and Codex/Claude Code user-scope operating instructions. |
| Validation | Claude JSON contract, two skill validators, Codex plugin validator, `git diff --check`, 48 unit tests, and strict type checking across 54 source files all passed. |
| External follow-up | `claude` is absent from this workspace. After private-repo installation in Claude Code, run `claude plugin validate .` once; no claim of that local CLI validation is made here. |
| Detach guarantee | No company repository file or configuration was changed. Removing the user-scoped plugin removes only the agent workflow skills. |

## PRG-20260803-006 — Context Load Telemetry POC

| Field | Value |
| --- | --- |
| State | `DONE` |
| Feature commit | `319ae97` — `feat: add router context load telemetry` |
| Specification | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| Ticket | `modules/tickets/context-load-telemetry/01-metadata-only-telemetry.md` |
| Delivered | Strict telemetry schema, source fingerprints, metadata-only JSONL store, matched baseline/router validator, local CLI, and source-gateway mismatch guard. |
| Safety | Output structurally excludes `SourceSnippet.text` and source URIs. Missing provider usage, a guard violation, incomplete pair, or quality regression fails the reduction claim. |
| Validation | 55 unit tests, strict type checking across 56 source files, compile check, and diff check passed. |
| Operator handoff | Create ignored `.johnny-router/router-usage.jsonl`, append paired records after each completed run, then run `python -m library.workflow_router.telemetry_cli .johnny-router/router-usage.jsonl --minimum-reduction-bps 5000`. |

## Plugin Release 0.3.0

| Field | Value |
| --- | --- |
| State | `DONE` |
| Feature commit | `368d513` (`release: package plugin version 0.3.0`) |
| Specification | `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` |
| Ticket | `modules/tickets/plugin-release-telemetry/01-package-current-skill.md` |
| Delivered | Codex plugin `0.3.0`, updated Claude Code metadata, shared takeover-skill release guidance, and README instructions for the Router telemetry evidence boundary. |
| Validation | Both skill validators, the Codex plugin validator, all plugin JSON parsing, 55 unit tests, strict type checking across 56 source files, and `git diff --check` passed. |
| Detach guarantee | The plugin remains user-scoped and contains no target-project file, runtime dependency, hook, MCP service, or secret. |
| Operator handoff | Update Codex or Claude Code from the private Git marketplace, then restart or reload the plugin. Collect Router reduction evidence only through local metadata-only JSONL and the validator. |

## PRG-20260805-001｜Workflow governance continuation and implementation handoff

| Field | Value |
| --- | --- |
| State | `DONE` |
| Specification | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` |
| Ticket | `01-enforce-continuation-and-handoff` |
| Change / Context | `CHG-20260805-009` / `doc/context/workflow-governance/main.md` |
| Implementation owner / worktree | Codex implementation Agent / `codex/implementation-private-router-saas-01` |
| Implementation commits | `d7e40cf` (`feat: enforce workflow implementation handoff`, externally advanced/indeterminate provenance), `eb4bb8f` (`fix: halt blocked implementation returns`, assigned implementation owner), `7faa590` (`fix: preserve legacy completion rules`, assigned implementation owner), `af6bf43` (`fix: require ticket implementation handoff`, assigned implementation owner), and `a17bec3` (`test: cover implementation handoff shape`, assigned implementation owner). |
| Delivered | Typed `CompletionEvidence`, `ImplementationHandoff`, `ImplementationReturn`, explicit human-wait reasons, fail-closed return routing at both Private Router and direct `RouterEngine` entrypoints, an explicitly Profile-declared `TICKETS + APPROVAL_GRANTED -> IMPLEMENT` handoff requirement, backward-compatible legacy `ACTION_COMPLETED` profile support, strict direct/private handoff boundary tests, frontend composition/DI template requirements, and continuous `ACTION_COMPLETED` policy guidance. |
| TDD red evidence | Initial completion/handoff tests failed at import with `ImportError: cannot import name 'CompletionActionKind'`; the P1 direct-core test then failed because a `BLOCKED` return produced `RouterOutcome.ADVANCE` instead of `SUSPEND`; the legacy profile test then failed because empty `accepted_completion_actions` was rejected. The handoff P1 test then proved bare approved `TICKETS` events advanced to `IMPLEMENT` instead of suspending, and the private-request boundary initially rejected `implementation_handoff` as an extra field. Locator/null/empty boundary cases were newly added but passed on the first run because strict `extra="forbid"`, opaque IDs, and `min_length` had already implemented the required protection; no false red output is claimed. |
| Validation | `python -m unittest discover -s tests` — 73 passed; `python -m mypy --strict library tests` — 58 source files clean; the literal Windows PowerShell `python -m py_compile library/workflow_router/*.py` failed with `[Errno 22] Invalid argument` because `*.py` was not expanded; control plane approved `Get-ChildItem -LiteralPath 'library/workflow_router' -Filter '*.py' -File | ForEach-Object { python -m py_compile $_.FullName }`, which passed for the same module set; `git diff --check` passed. |
| Smoke / privacy | Metadata-only `CompletionEvidence` rerouted `ARCHITECTURE → GRILL`; direct `BLOCKED` `ImplementationReturn` produced `SUSPEND + HALT`, no next stage, source, capability, or Context grant; bare approved ticket events halt on both direct and Private Router paths, while an allowlisted metadata-only handoff advances to `IMPLEMENT`. Handoffs are rejected on undeclared transitions, when paired with a return, without a frontend Composition Root reference, or with colliding control/implementation owners. The targeted contract field sentinel found no raw source/path/URI/prompt/secret/PII declaration. |
| Review / merge | Independent control-plane review is `APPROVED`: `doc/reviews/workflow-governance/01-enforce-continuation-and-handoff-code-review.md`. Review reran 73 tests, strict typing for 58 source files, syntax compilation, whitespace checks, and a disposable-worktree mutation proof. Reviewed implementation was integrated into `main` by `2f545c8`; no push was performed. |

## PRG-20260807-002 — Guarded integration audit implementation handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / baseline | `02-guarded-integration-audit` / ticket docs `911218d`, handoff `1d4292a`, reviewed ticket-01 dependency `67b049a` |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-guarded-integration-audit-02` |
| Implementation commit | `afa6da8` — `feat: add guarded integration audit coordinator` |
| Docs-only handoff commit | This docs-only handoff commit — `docs: hand off guarded integration audit` |
| Delivered | Typed metadata-only implementation-return event validation; independent planning/ticket lane IDs; clean expected-main revision and conflict guards; exclusive injected integration lock/port; duplicate correlation/event replay and one-active-`PENDING_AUDIT` guards; dependent proposal wake-up; one Grill audit request; `APPROVED → REVIEW` only; `CHANGES_REQUESTED → correction_worktree`; no handoff, push, deploy or dependent implementation grants. |
| TDD red evidence | Before the implementation module existed, `python -B -m unittest tests.test_guarded_integration_audit -v` failed at import with `ModuleNotFoundError: No module named 'library.workflow_router.guarded_integration'`. |
| Validation | `python -B -m unittest discover -s tests` — 80 passed; `python -m mypy --strict library tests` — 60 source files clean; in-memory compilation — 11 `workflow_router` modules; `git diff --check` passed. |
| Smoke / privacy / mutation | Metadata-only privacy sentinel and approved/correction smoke passed. Temporary in-memory mutations that bypassed the revision or lock guard were both detected by the guarded-integration tests. No raw Context, source, prompt, path, URI, Secret, PII or production data was persisted. |
| Review / integration | Independent control-plane review is pending. Main and Ticket-01 worktrees were not modified; no merge, push or deployment was performed. |

## PRG-20260808-002 — Ticket 02 correction handoff (CR-12 through CR-15)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `02-guarded-integration-audit` / `c78af90` (`CHANGES_REQUESTED → IMPLEMENT`) |
| Reviewed source baseline | Ticket 01 public contracts replayed as complete reviewed commits through `67b049a`; current main was rebased first; no source-only cherry-pick was used. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-guarded-integration-audit-02` |
| Implementation commit | `b53cc55` (`fix: bind guarded integration to reviewed ticket lanes`) |
| CR-12 / CR-13 correction | Guarded integration now requires an exact immutable `CollaborationDispatchPlan` receipt/lane match (ticket, positive confirmed state, handoff, owner, reviewer, worktree, branch, correlation, expected main revision, and planning/ticket Context/event IDs); missing, forged, replayed, or mismatched returns halt before integration, audit, or wake. Any active `PENDING_AUDIT` blocks every other ticket, and the trusted main snapshot advances only at the completed integration boundary. |
| CR-14 correction | Reviewed Router contracts now declare `IMPLEMENTATION_RETURNED`, `INTEGRATION_COMPLETED`, and `AUDIT_COMPLETED`; the POC Profile declares return → smoke, integration → audit wait, and approved audit → review transitions. `GuardedIntegrationRouterAdapter` emits only those typed Router events; changes-requested emits no delivery event. |
| TDD red evidence | New correction tests initially failed because `IMPLEMENTATION_RETURNED` was absent from the reviewed contracts; after contract/profile/registry implementation, direct and injected unregistered returns, lane mismatches, seven locator forms, cross-ticket pending audit, revision advancement, and Router composition pass fail-closed. |
| Validation | `python -B -m unittest discover -s tests` — 102 passed; `python -m pytest -q` — 102 passed / 105 subtests; `python -m mypy --strict --no-incremental library tests` — 63 source files clean; in-memory compilation of all 11 `workflow_router` modules; `git diff --check` clean; metadata-only privacy/source sentinel clean aside from intentional marker strings in validation code. |
| Docs-only handoff | This entry is the docs-only handoff commit following `b53cc55`; no raw Context, source text, prompt, path, URI, Secret, PII, production data, merge, push, or deployment was recorded. Independent review is required before any integration. |

## PRG-20260808-003 ??Ticket 02 correction handoff (CR-19 through CR-22)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `02-guarded-integration-audit` / `79aa649` (`CHANGES_REQUESTED ??IMPLEMENT`) |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-guarded-integration-audit-02` |
| Implementation commit | `67745a3` (`fix: close guarded integration audit corrections`) |
| CR-19 correction | Actor authority is now the exact named `capability_id` at proposal, handoff, pending-dispatch, receipt, coordinator, and return boundaries. A descriptive `agent_profile` cannot equal a capability ID or substitute for control, implementation-owner, or reviewer identity. Direct and injected forged owner/reviewer returns halt before integration or audit side effects. |
| CR-20 / CR-21 correction | A completed integration creates the trusted `PENDING_AUDIT` state and advances the trusted revision before the fallible audit sink is called; the exclusive section is released only afterward. The retained pending state blocks every later ticket and supports idempotent audit retry without another integration. The adapter emits the reviewed integration event only after a successful initial delivery or retry. |
| CR-22 correction | `GRILL + INTEGRATION_COMPLETED` now advances automatically to the declared Grill capability and carries no human-wait reason. Approved and correction audit dispositions retain their reviewed continuation routes. |
| TDD red evidence | The pre-correction direct reviewer-profile forgery reached `PENDING_AUDIT`; a reentrant second ticket reached a second pending path after lock release; an audit-sink failure left no pending guard; and the profile returned a human wait for normal audit. Each new regression test failed before the correction and passes afterward. |
| Validation | `python -m pytest -q` ??107 passed / 111 subtests; `python -m mypy --strict library` ??48 source files clean; `python -m compileall -q library` ??48 modules; metadata-only model-field privacy sentinel passed; CR-21 retry smoke passed; `git diff --check` passed. No repository lint or formatter configuration is declared. |
| Review / integration | No merge, push, deployment, external provider, main-worktree mutation, or other-ticket mutation was performed. Independent control-plane review is required before any fast-forward integration. |

## PRG-20260808-005 ??Ticket 02 correction handoff (CR-24)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `02-guarded-integration-audit` / `0beac6d` (`CHANGES_REQUESTED ??IMPLEMENT`) |
| Reviewed baseline | `0beac6d`; the implementation branch was rebased to this current main baseline before the CR-24 red-test and validation cycle. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-guarded-integration-audit-02` |
| Implementation commit | `906679a` (`fix: require delivered audit decisions`) |
| CR-24 correction | `handle_audit()` now consumes a matching decision only from coordinator-owned `DELIVERED` state. `RETRYABLE` halts with `AUDIT_NOT_DELIVERED`; `DELIVERING` remains `AUDIT_DELIVERY_ACTIVE`. Both paths preserve pending state and emit no review, correction, or Router completion event. |
| TDD red evidence | Before the correction, failed initial and failed retry delivery tests reached the missing non-delivery transition and allowed the old audit-consumption path; the independent review reproduced `APPROVED → CODE_REVIEW` without a successful sink delivery. Committed tests cover both `APPROVED` and `CHANGES_REQUESTED` after each failed delivery path, including pending retention, zero additional integration, and no Router event. |
| Validation | `python -B -m unittest discover -s tests` ??113 passed; `python -m pytest -q` ??113 passed / 115 subtests; `python -m mypy --strict --no-incremental library tests` ??63 source files clean; `python -m compileall -q library` ??48 Python files; metadata-only model-field privacy sentinel passed; CR-24 and retained CR-23 smoke tests passed; `git diff --check` passed. |
| Review / integration | No merge, push, deployment, external provider, main-worktree mutation, or other-ticket mutation was performed. Independent control-plane review is required before any fast-forward integration. |

## PRG-20260808-004 ??Ticket 02 correction handoff (CR-23)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `02-guarded-integration-audit` / `ae888f9` (`CHANGES_REQUESTED ??IMPLEMENT`) |
| Reviewed baseline | `ae888f9`; the implementation branch was rebased to this current main baseline before the CR-23 validation rerun. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-guarded-integration-audit-02` |
| Implementation commit | `8b3109a` (`fix: guard audit delivery reentry`) |
| CR-23 correction | Pending audit delivery is a coordinator-owned typed state machine: `RETRYABLE`, `DELIVERING`, and `DELIVERED`. Admission is marked `DELIVERING` before the injected sink call; a re-entrant or concurrent retry returns `AUDIT_DELIVERY_ACTIVE` with no sink request or Router event. Sink failure resets only to `RETRYABLE`; success transitions once to `DELIVERED`, wakes dependents once, and emits one integration event. A delivered sequential retry is idempotent and emits no duplicate event. |
| TDD red evidence | Independent review reproduced two audit requests and two equivalent events when the sink re-entered before the old delivered flag was written; the failure-plus-retry path reproduced three requests. Committed tests now cover initial and post-failure re-entry plus deterministic concurrent delivery, with one integration, one successful audit delivery, and one event. |
| Validation | `python -B -m unittest discover -s tests` ??111 passed; `python -m pytest -q` ??111 passed / 111 subtests; `python -m mypy --strict --no-incremental library tests` ??63 source files clean; `python -m compileall -q library` ??48 Python files; metadata-only model-field privacy sentinel passed; CR-23 re-entry/concurrency smoke passed; `git diff --check` passed. |
| Review / integration | No merge, push, deployment, external provider, main-worktree mutation, or other-ticket mutation was performed. Independent control-plane review is required before any fast-forward integration. |

## PRG-20260808-006 — Ticket 03 implementation allocation switch

| Field | Value |
| --- | --- |
| State | `IN_PROGRESS → IMPLEMENT` — no human wait; Ticket-03 has an existing valid dispatch receipt |
| Trigger | Ticket-02 independent approval and fast-forward integration (`906679a` / `90e9191`), followed by dependency-corrected planning Grill at `0d52903` |
| Released allocation | Ticket 02 / `worktree-ticket-02` / `codex/implementation-guarded-integration-audit-02`; read-only historical integration evidence |
| Active allocation | Ticket 03 / `worktree-ticket-03` / Codex implementation Agent; this is the sole active implementation lane |
| Receipt / fresh handoff | Existing receipt `c569056`; `handoff-ticket-03-resume-20260808-01`; no second dispatch confirmation or approval is allowed |
| Required branch | Owner creates `codex/implementation-plugin-policy-and-response-03-rework` from reviewed main baseline `0d52903` inside the assigned Ticket-03 worktree, then begins a fresh red/green TDD cycle |
| Blocked evidence | `codex/implementation-plugin-policy-and-response-03` at `9eda250` remains CR-16 through CR-18 historical evidence only; no reset, overwrite, cherry-pick, or source reuse |
| Owner preflight | Owner may remove only the known test-generated Python bytecode cache in its own Ticket-03 worktree before creating the branch. No other worktree may be mutated. |
| Scope / integration | This record changes allocation only. It grants no merge, push, deployment, host configuration, target-project mutation, Secret, provider, or other-ticket authority. |

## PRG-20260808-007 — Ticket 03 fresh implementation handoff (CR-16 through CR-18)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / receipt | `03-plugin-policy-and-response` / `c569056` (fresh handoff; no second confirmation) |
| Reviewed source baseline | `0d52903`; old blocked implementation `4d68938` and handoff `9eda250` were not reused. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commit | `a2c82d7` (`feat: bind plugin response to pending dispatch`) |
| CR-16 correction | Policy source reads return only typed metadata or a stable halt error. Raw source text, prompts, paths, URIs, secrets, PII and exception detail cannot enter a Router model, formatter, telemetry or error. |
| CR-17 correction | Fixed response rendering is available only through the same Private Router's live pending-plan identity. Ticket, reviewed handoff, commit references and named owner must match; forged, replayed, absent, mismatched or formatter-mutated input halts. The executable `TICKETS + APPROVAL_GRANTED -> IMPLEMENT` path remains fail-closed in the reviewed baseline. |
| TDD red evidence | Before `policy_response.py` existed, `python -m pytest -q tests/test_plugin_policy_and_response.py` failed during collection with `ModuleNotFoundError: No module named 'library.workflow_router.policy_response'`. Fresh tests cover raw sentinel rejection, private-plan ownership, exact response fields/question, formatter exceptions/mutation, absent/mismatched/replayed dispatch and legacy direct/private routing. |
| Validation | `python -B -m unittest discover -s tests` — 122 passed; `python -m pytest -q` — 122 passed / 115 subtests; `python -m mypy --strict --no-incremental library tests` — 65 source files clean; `python -m compileall -q library/workflow_router` — 13 modules; metadata-only privacy/source sentinel, smoke and `git diff --check` passed. |
| Review / integration | No merge, push, deployment, external provider, main-worktree mutation or other-ticket mutation was performed. Independent control-plane review is required before any fast-forward integration. |

## PRG-20260808-008 — Ticket 03 correction handoff (CR-25 and CR-26)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `03-plugin-policy-and-response` / `9215546` (`CHANGES_REQUESTED → IMPLEMENT`) |
| Receipt / baseline | `c569056` remains valid; implementation reworked from `0d52903` without reusing `4d68938` or `9eda250`. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commit | `fb0d94d` (`fix: bind dispatch response to router artifacts`) |
| CR-25 correction | Module-level trusted rendering is now fail-closed and cannot accept a structural fake owner. Exact live-plan identity is checked only inside `PrivateRouterClient`; copied plans, alternate clients, absent/replayed plans and indirect helper calls produce no text. |
| CR-26 correction | Reviewed ticket/handoff commit references are carried into the Router-created `PendingDispatchDescriptor` from the validated handoff. Rendering uses only those immutable pending values; caller artifacts are equality assertions and forged valid-shaped commits, ticket, handoff or owner values halt. |
| TDD red evidence | Before correction, a fake `PendingDispatchPlanOwner` rendered and `deadbee`/`cafe123` artifact commits rendered. New regressions cover fake owner, copied/alternate plan, valid-shaped forged commits, ticket/handoff/owner mismatch, replay and all seven path/URI boundary forms. |
| Validation | `python -B -m unittest discover -s tests` — 125 passed; `python -B -m pytest -q -p no:cacheprovider` — 125 passed / 122 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; `python -B -m compileall -q library/workflow_router` — 13 modules; privacy/source sentinel, smoke and `git diff --check` passed. |
| Review / integration | No merge, push, deployment, external provider, main-worktree mutation or other-ticket mutation was performed. Independent control-plane review is required before any fast-forward integration. |

## PRG-20260808-009 — Ticket 03 correction handoff (CR-27 and CR-28)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `03-plugin-policy-and-response` / `5d55586` (`CHANGES_REQUESTED → IMPLEMENT`) |
| Receipt / baseline | `c569056` remains valid; branch was rebased onto current control-plane `main` at `5d55586` before this red/green cycle. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commit | `ea556b0` (`fix: halt dispatch without reviewed artifacts`) |
| CR-27 correction | Router admission now requires both reviewed ticket and handoff commit references before creating a pending dispatch. Missing either or both values halt in direct Router and Private Router paths with no pending descriptor, receipt acceptance or implementation lane. |
| CR-28 correction | TDD now individually asserts exact, one-extra-character prefix, trailing slash, casing, URL-encoded, traversal and empty path/URI variants for both commit fields, plus null, undefined-equivalent, empty, whitespace and empty-container values. |
| TDD red evidence | Before the admission guard, missing reviewed commits returned `WAIT_FOR_HUMAN` and a matching dispatch could advance; before the expanded boundary cases, only alternative locator strings were covered. New direct/private regressions fail before pending state or lane creation. |
| Validation | `python -B -m unittest discover -s tests` — 127 passed; `python -B -m pytest -q -p no:cacheprovider` — 127 passed / 130 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; `python -B -m compileall -q library/workflow_router` — 13 modules; privacy/source sentinel, smoke and `git diff --check` passed. |
| Review / integration | No merge, push, deployment, external provider, main-worktree mutation or other-ticket mutation was performed. Independent control-plane review is required before any fast-forward integration. |

## PRG-20260808-010 — Ticket 03 correction handoff (CR-29 through CR-31)

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `03-plugin-policy-and-response` / `870013c` (`CHANGES_REQUESTED → IMPLEMENT`) |
| Receipt / baseline | `c569056` remains valid; the complete rework branch was rebased onto current control-plane `main` at `870013c` before handoff. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commits | `0dda8fc` (`fix: require approved dispatch artifact registry`) and `95bf7cf` (`test: cover omitted dispatch commit values`) |
| CR-29 correction | Private Router and direct Router admission now require an injected typed `ApprovedDispatchArtifactRegistry`. It resolves exact ticket, reviewed handoff, and named implementation-owner identity, then requires both incoming commit references to equal the registered reviewed commits. Missing or substituted ticket, handoff, owner, or valid-shaped commit metadata halts before question, pending descriptor, receipt acceptance, rendering, or implementation lane. Duplicate registry identities are rejected. |
| CR-30 correction | TDD covers both commit fields independently for omission, `None`, empty, whitespace, `[]`, `{}`, and the seven path/URI boundary forms; private-boundary regressions verify no pending descriptor or lane is created. |
| TDD red evidence | Before registry injection, valid-shaped raw handoff commit substitutions reached the pending/render path. Before the expanded boundary matrix, the test used a literal `undefined` marker and tuple-only empty-container coverage. New direct/private tests now fail closed for registered-identity, ticket, handoff, owner, omission, null, whitespace, empty-container, replay and path/URI substitutions. |
| Validation | `python -B -m unittest discover -s tests` — 129 passed; `python -B -m pytest -q -p no:cacheprovider` — 129 passed / 161 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; `python -B -m compileall -q library/workflow_router` — 13 modules; metadata-only privacy/source sentinel and plugin dispatch smoke passed; `git diff --check` clean. |
| Docs-only handoff | This entry and the Workflow registry rule are the docs-only handoff following `95bf7cf`; no raw Context, source text, prompt, path, URI, Secret, PII, production data, merge, push, or deployment was recorded. Independent review is required before integration. |

## PRG-20260808-011 — Ticket 03 project-scope registry correction handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `03-plugin-policy-and-response` / `1bcfebf` (`CHANGES_REQUESTED → IMPLEMENT`) |
| Receipt / baseline | `c569056` remains valid; the complete rework branch was rebased onto current control-plane `main` at `1bcfebf` before this cycle. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commit | `46347a6` (`fix: bind dispatch artifacts to project identity`) |
| Project-scope correction | `ApprovedDispatchArtifactRegistry` identity is now `(project_id, ticket_reference, handoff_reference, implementation_owner_id)`; both direct Router and Private Router resolve and compare the project before creating pending state or granting a lane. Cross-project valid-shaped requests halt closed. |
| TDD red/green evidence | Added direct and private cross-project regressions using an otherwise exact reviewed handoff; the alternate project cannot reuse the registered artifact record and produces no pending descriptor or implementation lane. Existing forged identity, commit, omission, replay and path/URI regressions remain active. |
| Validation | `python -B -m unittest discover -s tests` — 130 passed; `python -B -m pytest -q -p no:cacheprovider` — 130 passed / 161 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; `python -B -m compileall -q library/workflow_router` — 13 modules; metadata-only privacy/source sentinel, plugin dispatch smoke and `git diff --check` passed. |
| Docs-only handoff | This entry is the docs-only handoff following `46347a6`; no raw Context, source text, prompt, path, URI, Secret, PII, production data, merge, push, or deployment was recorded. Independent review is required before integration. |

## PRG-20260808-012 — Ticket 03 evidence and opaque-project correction handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / review return | `03-plugin-policy-and-response` / `46fe254` (`CHANGES_REQUESTED → IMPLEMENT`) |
| Receipt / baseline | `c569056` remains valid; the complete rework branch was rebased onto current control-plane `main` at `46fe254` before this cycle. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commit | `f6b9c32` (`fix: validate project scoped dispatch identity`) |
| CR-33 correction | Ticket-03 records now form the unique chronological sequence PRG-006 through PRG-012. Erratum mapping: the former duplicate fresh-handoff PRG-006 is PRG-007; former PRG-007, PRG-008, PRG-009 and PRG-010 are respectively PRG-008, PRG-009, PRG-010 and PRG-011. Historical validation facts and commit references are unchanged. |
| CR-34 correction | The private cross-project regression now grants the same account both projects, retains an approved-artifact record only for the original project, proves dispatch admission halts before service/pending/rendering, and proves a forged confirmation receipt obtains no response or ticket-lane capability. |
| CR-35 correction | One named `ProjectId` type validates approved-artifact registration, registry resolution, private requests and entitlement grants. Omission, null, empty, whitespace, empty containers, all seven locator variants, URI, traversal and arbitrary nonblank values fail closed; current opaque project IDs remain valid. |
| TDD red evidence | `test_approved_artifact_project_id_rejects_non_opaque_boundary_values` initially failed for eight accepted path, URI, traversal and arbitrary-nonblank cases. CR-34 was an evidence-strengthening correction over already-working project equality; the committed two-entitlement test adds a service-call mutation assertion and makes no false red claim. |
| Validation | `python -B -m unittest discover -s tests` — 131 passed; `python -B -m pytest -q -p no:cacheprovider` — 131 passed / 175 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; `python -B -m compileall -q library/workflow_router` — 13 modules; metadata-only privacy/source sentinel, plugin dispatch smoke and `git diff --check` passed. |
| Docs-only handoff | This entry is the docs-only handoff following `f6b9c32`; no raw Context, source text, prompt, path, URI, Secret, PII, production data, merge, push or deployment was recorded. Independent review is required before integration. |

## PRG-20260808-013 — Ticket 03 rebase and fresh handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMMITTED_PENDING_REVIEW` |
| Ticket / receipt | `03-plugin-policy-and-response` / `c569056` (receipt remains valid; no second confirmation) |
| Rebase baseline | The implementation worktree was clean and the complete rework branch was rebased without merge commit or reset onto `main@b34e59e`, which records the independent final review approval. |
| Implementation owner / branch | Codex implementation Agent / `codex/implementation-plugin-policy-and-response-03-rework` |
| Implementation commit | `0a5b757` (`fix: validate project scoped dispatch identity`) — the rebased equivalent of the reviewed implementation; no source or test scope was changed by the rebase. |
| Revalidation | `python -B -m unittest discover -s tests` — 131 passed; `python -B -m pytest -q -p no:cacheprovider` — 131 passed / 175 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; in-memory compilation — 13 `workflow_router` modules; metadata-only privacy/source sentinel, plugin dispatch smoke and `git diff --check` passed. |
| Handoff | This docs-only handoff records the rebased commit for independent control-plane review. No merge, push, deployment, external provider, main-worktree mutation, raw Context, source text, prompt, path, URI, Secret, PII or production data was recorded. |

## PRG-20260808-014 — Ticket 03 guarded integration and Grill audit

| Field | Value |
| --- | --- |
| State | `INTEGRATED` |
| Trigger / completed return | Ticket-03 rebase handoff `0a5b757` / `43033bf`, preserving receipt `c569056` and the final independent review evidence |
| Guarded integration | The control-plane worktree fast-forwarded clean `main` from `b34e59e` to `43033bf`. No merge commit, reset, push, deployment, external provider, host configuration or target-project write occurred. |
| Post-integration Grill | `APPROVED -> REVIEW`; the approved source snapshot is unchanged by the rebase, and the existing final independent code review remains the review gate. No requirement, architecture, security, ownership, UI, data, authority or delivery change was found. |
| Independent verification | `python -B -m unittest discover -s tests` — 131 passed; `python -B -m pytest -q -p no:cacheprovider` — 131 passed / 175 subtests; `python -B -m mypy --strict --no-incremental library tests` — 65 source files clean; in-memory compilation — 13 Router modules; `git diff --check` passed. |
| Continuation / boundary | `ACTION_COMPLETED -> AUTO_CONTINUE -> HANDOFF`. No correction route, new ticket, dispatch question, user wait, push, deployment or external action is granted by this record. |
