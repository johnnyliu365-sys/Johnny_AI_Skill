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

## PRG-20260802-010 — Claude Code Plugin Distribution POC

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

## PRG-20260808-015 — POC convergence planning Grill

| Field | Value |
| --- | --- |
| State | `HANDOFF` — no implementation ticket is opened |
| Trigger | Ticket 03 is integrated and its post-integration Grill completed at `43033bf` / `f3519ab`. |
| Traceability correction | Stable patch IDs prove approved Ticket-01 `67b049a` and rebased on-main `0dc4da5` are identical; Ticket 01 is therefore integrated through Ticket 02's reviewed baseline. Ticket-ledger states and obsolete active-allocation language are reconciled accordingly. |
| Scope decision | A real host wake-up, physical worktree, real Git, Temporal worker or MCP adapter remains out of scope for this local POC. It is deferred, not treated as a hidden implementation failure; any expansion must begin with `REQUIREMENT_CHANGED -> WAYFINDER`. |
| Grill decision | `GO -> HANDOFF`. No proposal is `PLANNED`, no valid new dispatch authority exists, and no new ticket is created. |
| Continuation / boundary | `ACTION_COMPLETED -> AUTO_CONTINUE -> HANDOFF`. No user wait, correction worktree, push, deployment or external action is granted. |

## PRG-20260808-016 — Local orchestration installer Wayfinder, Architecture and Grill

| Field | Value |
| --- | --- |
| State | `SPEC_DRAFT_AWAITING_OWNER_APPROVAL` |
| Trigger | Project owner requested a detachable installer whose normal one-click uninstaller removes plugin content rather than leaving local residue. |
| Change / baseline | `CHG-20260808-011` / `e04c2be` |
| Wayfinder | `GO`: Windows per-user install, runtime status and one-click owned removal have concrete observable interaction states, derived use cases, data owners and DI composition roots. |
| Architecture | `ADR-20260808-003` separates installer-owned root, metadata-only runner, receipt-based host lifecycle adapters and a runtime-only guarded Git port. It explicitly denies target-project and host-turn authority. |
| Grill | Normal uninstall may remove only digest/ledger-verified descendants and receipt-matched host registration. A foreign/tampered/failed lifecycle result is `UNINSTALL_BLOCKED`, never broad deletion or a false success. |
| Evidence / limitation | Workspace has Python 3.11 but no `iscc`/Inno Setup or NSIS compiler. The Codex manual helper could not run because Node.js is absent and this session exposes no OpenAI Docs MCP; consequently no undocumented host lifecycle command is assumed. |
| Continuation | `ACTION_COMPLETED → WAIT_FOR_HUMAN: SPEC_APPROVAL`. No ticket, source/test implementation, host configuration, installer binary, project mutation, merge, push or deployment is authorized yet. |

## PRG-20260808-017 — Local orchestration installer SPEC approval and ticket plan

| Field | Value |
| --- | --- |
| State | `TICKETS_PLANNED` |
| Approval | The project owner approved `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` on `2026-08-08 (Asia/Taipei)`. |
| Reuse selection | `workflow-router-poc@d94d8d5` only: public metadata/ProjectId/return contracts and guarded-integration pattern. Existing fake adapters are not treated as production host/Git capability; all unrelated modules are rejected. |
| Ticket plan | Four sequential vertical tickets: owned lifecycle, metadata runtime/guarded Git, reversible Agent host lifecycle, then Windows setup/uninstaller package. The first three are code/test work; the final package requires an available pinned Inno Setup compiler and at least one independently reversible host adapter. |
| Role topology | Control-plane/reviewer is Codex/current `main`; named implementation capability remains Codex implementation Agent in the existing separate `workflow-implementation` worktree. No ticket is yet selected, so no implementation allocation or source/test authority exists. |
| Capability discovery | `codex.exe` is discoverable but this session's direct `codex plugin --help` returned access denied; `claude` is absent. These are not substituted with hidden config edits. Ticket 03 must independently verify any claimed host lifecycle. |
| Continuation | `ACTION_COMPLETED → AUTO_CONTINUE → select Ticket 01 and prepare its docs-only handoff`, then one dispatch-confirmation wait. |

## PRG-20260808-018 — Ticket 01 selected; dispatch confirmation pending

| Field | Value |
| --- | --- |
| State | Superseded by `PRG-20260808-019` after the positive dispatch receipt. |
| Ticket / baseline | `01-owned-install-lifecycle` / reviewed ticket-set baseline `afee39d` |
| Handoff | `hnd_local_orchestration_install_01_20260808`; the current docs-only dispatch record is the required synchronization point before the implementation owner's first red test. |
| Roles | Control-plane/reviewer: Codex/current `main`. Implementation owner: named Codex implementation Agent in the separate `workflow-implementation` worktree. |
| Authority | No positive delivery confirmation has been received. The Router grants no source, Context, capability, branch/worktree mutation or implementation. |
| Single pending question | `工單 01-owned-install-lifecycle 是否已交付給 implementation owner Codex implementation Agent？` |
| Continuation | Positive `IMPLEMENTATION_DISPATCH_CONFIRMED` starts Ticket 01 and automatically routes the planning lane to the next Grill. Silence/negative remains `WAIT_FOR_HUMAN`; no second approval question exists. |

## PRG-20260808-019 — Ticket 01 dispatch receipt and Ticket 02 planning Grill

| Field | Value |
| --- | --- |
| Ticket 01 receipt | `rcpt_local_orchestration_install_01_20260808` — project owner replied `已交付` on `2026-08-08`; no second ticket approval was requested or required. |
| Granted Ticket-01 lane | The named Codex implementation Agent may synchronize the corrected dispatch-record `main` commit in `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`, perform only Ticket-01 TDD/source/test/verification work, and return typed completion evidence. |
| Handoff correction | The former textual path `...AI控制工作\workflow-implementation` did not exist; it was corrected to the actual worktree before first-red-test work. Receipt scope, reviewed source baseline `afee39d`, owner, ticket and requirements are unchanged. |
| Ticket 02 Grill | `GO → DEPENDENCY_WAIT`: existing public Router contracts/patterns are reusable, raw Context remains excluded, temporary repos are required, and exact registry/lock/clean-base/fast-forward guards remain mandatory. No new CHG/SPEC/ADR is required. |
| Planning state | Ticket 02 stays `PLANNED` and has no dispatch receipt until Ticket 01 is independently reviewed and integrated. Ticket 03/04 remain untouched. |
| Continuation | Ticket lane: `IMPLEMENT`. Planning lane: waits for typed Ticket-01 integration evidence, then automatically resumes Grill/dispatch eligibility. |

## PRG-20260808-020 — Ticket 01 stale-branch recovery and fresh allocation

| Field | Value |
| --- | --- |
| Trigger | The implementation owner reported clean historical worktree `codex/implementation-private-router-saas-01@3fa2270` cannot rebase to `main@863c76d`; conflicts occur in previous Router collaboration/contract/private-router source and tests. Rebase was correctly aborted; no source was changed. |
| Verification | `git merge-base --is-ancestor 3fa2270 863c76d` exits `1`: the old branch is not an ancestor of current main. Its clean HEAD and history are retained as historical evidence. |
| Classification | Allocation/branch-history conflict only — no requirements, SPEC, ticket scope, architecture, dependency, security boundary or acceptance criterion changed. `REQUIREMENT_CHANGED` is not emitted. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_fresh_20260808` / `aln_local_orchestration_install_01_20260808`: same ticket, owner, reviewer, user receipt and TDD; fresh branch name `codex/implementation-local-install-lifecycle-01` starts directly from this docs-only control-plane handoff commit. |
| Required owner action | In the existing owner worktree only, with clean status: create the fresh branch at the recorded current `main` handoff baseline. Do not merge, rebase, reset, cherry-pick, overwrite or reuse the historical branch. Then write/run Ticket-01 first red test. |
| Authority / continuation | Receipt `rcpt_local_orchestration_install_01_20260808` remains valid by allocation continuation; no second delivery question is permitted. Ticket lane returns to `IMPLEMENT`; planning lane remains at Ticket-02 `DEPENDENCY_WAIT`. |

## PRG-20260808-022 — Ticket 01 independent review return

| Field | Value |
| --- | --- |
| State | `CHANGES_REQUESTED → FRESH_REWORK_HANDOFF` |
| Reviewed range | Baseline `8e8caf7`; implementation `010110a`; docs-only handoff `7bc5fd5`; branch `codex/implementation-local-install-lifecycle-01`. |
| Independent evidence | `git diff --check`; 148 unittest tests; 148 pytest tests / 175 subtests; strict mypy across 71 files; 5-module in-memory compile; metadata/privacy scan all passed. |
| Blocking findings | CR-36: dynamic `object`/`getattr` proof boundary violates P0. CR-37: matching proof does not verify host absence. CR-38: rollback/deletion recovery failure can discard retry authority. Full evidence: `doc/reviews/local-orchestration-installer/01-owned-install-lifecycle-code-review.md`. |
| Scope classification | No requirement, SPEC, ticket acceptance, architecture or delivery-stage change. This is implementation correction; `REQUIREMENT_CHANGED` is not emitted. |
| Continuation | Original branch is historical evidence. Control plane creates a fresh rework handoff/allocation for the same ticket, owner and receipt; the planning lane remains Ticket-02 `DEPENDENCY_WAIT`. |

## PRG-20260808-023 — Ticket 01 fresh rework handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `ccb8164` records `CHANGES_REQUESTED` for CR-36 through CR-38. Implementation `010110a` and docs handoff `7bc5fd5` are immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_20260808` / `aln_local_orchestration_install_01_rework_20260808`; new branch `codex/implementation-local-install-lifecycle-01-rework` starts directly from this current docs-only handoff commit. |
| Scope | Repeat fresh red → minimal typed implementation → green for only CR-36 typed proof validation, CR-37 verified removal absence, and CR-38 durable recovery state. No target project, host configuration, installer package, Ticket 02+, merge/push/deploy or requirements change is permitted. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole positive dispatch authority. This is a corrected implementation allocation, not a new ticket approval/dispatch. |
| Required return | implementation commit plus docs-only handoff, first-red evidence for every CR, regression/type/compile/privacy/smoke evidence, then `COMPLETED → ACTION_COMPLETED → REVIEW`. |

## PRG-20260808-025 — Ticket 01 second independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `f297d4f`; implementation `fd429fd`, `a222d89`; final docs-only handoff `8e39c99`; branch `codex/implementation-local-install-lifecycle-01-rework`. |
| Passing corrections | CR-36 runtime proof typing and CR-37 typed absence validation pass focused reverse verification. Full regression, strict mypy, compile, diff and privacy checks also pass. |
| Blocking findings | CR-38 remains open because persisted recovery is never loaded/resumed; CR-39 host verification failure propagates `ValidationError`; CR-40 mandatory TDD cases and behavior-specific red evidence are incomplete. Reproduction and exact evidence are in `doc/reviews/local-orchestration-installer/01-owned-install-lifecycle-code-review.md`. |
| Scope classification | Implementation/evidence corrections only. Approved requirements, SPEC, ticket acceptance, architecture and delivery stage do not change; no `REQUIREMENT_CHANGED` event. |
| Continuation | Mark this branch historical and create another fresh allocation from the next docs-only control-plane handoff. Receipt `rcpt_local_orchestration_install_01_20260808` continues; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260808-026 — Ticket 01 fresh rework-2 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `f2b4a8e` records the second `CHANGES_REQUESTED`. `fd429fd`, `a222d89` and `8e39c99` are immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_2_20260808` / `aln_local_orchestration_install_01_rework_2_20260808`; branch `codex/implementation-local-install-lifecycle-01-rework-2` starts directly from this current docs-only handoff commit. |
| Scope | Fresh red → minimal typed implementation → green for CR-38 recovery resume, CR-39 finite zero/partial-receipt rollback and CR-40's complete approved ticket matrix. No target project, real host configuration, installer package, Ticket 02+, merge/push/deploy or requirements change. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole positive dispatch authority. This corrected allocation is not a new ticket approval/dispatch. |
| Required return | New implementation commit(s), then one final docs-only handoff. Evidence must name each behavior-specific first-red test/reason, recovery retry terminal outcomes, complete regression/type/compile/privacy/smoke results and target-repository non-interference across success and required failure paths. |

## PRG-20260809-028 — Ticket 01 third independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `15f6be8`; implementation `4b840cd`; docs-only handoff `7c73b14`; branch `codex/implementation-local-install-lifecycle-01-rework-2`. |
| Passing corrections | CR-38 normal partial-effect retries and CR-39 finite host-verification rollback pass; recovery-load reversal breaks the focused retry test as expected. Full regression, strict mypy, compile, diff and privacy checks pass. |
| Blocking findings | CR-40 matrix/red evidence remains incomplete. CR-41 typed recovery phase can skip host/files and falsely return `REMOVED`; CR-42 a Codex selection accepts a Claude receipt; CR-43 two installation IDs share the fixed root and corrupt each other. Exact probes are recorded in the formal review. |
| Scope classification | Implementation/contract/test correction only. Approved requirements, SPEC, architecture and delivery stage do not change; no `REQUIREMENT_CHANGED` event. |
| Continuation | Mark the rework-2 branch historical and create another fresh allocation. Receipt `rcpt_local_orchestration_install_01_20260808` continues; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-029 — Ticket 01 fresh rework-3 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `0300666` records the third `CHANGES_REQUESTED`. `4b840cd` and `7c73b14` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_3_20260809` / `aln_local_orchestration_install_01_rework_3_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-3` starts directly from this current docs-only handoff commit. |
| Scope | Fresh red → minimal typed implementation → green for CR-40 complete matrix/evidence, CR-41 evidence-bearing recovery phases, CR-42 exact selected-host receipt binding and CR-43 exclusive fixed-root ownership. No target project, real host configuration, installer package, Ticket 02+, merge/push/deploy or requirements change. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole positive dispatch authority. This corrected allocation is not a new ticket approval/dispatch. |
| Required return | New implementation commit(s), then one final docs-only handoff. Evidence must include valid-shaped phase-forgery rejection, host-mismatch rollback, two-ID interleaving/recovery, every named boundary/port subtest's first-red reason, full regression/type/compile/privacy/smoke and target-repository success/failure non-interference. |

## PRG-20260809-031 — Ticket 01 fourth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `7cc8b38`; implementation `c91041a`; docs-only handoff `ba74caf`; branch `codex/implementation-local-install-lifecycle-01-rework-3`. |
| Passing corrections | CR-41 evidence-bearing phases/live absence checks, CR-42 selected-host receipt binding and CR-43 exclusive active-owner gate pass focused tests and reverse mutation checks. Full 147-test regression, 224 subtests, strict mypy across 71 files, five-module compile, diff and privacy sentinels pass. |
| Blocking findings | CR-40 remains incomplete because finite failure-code tests do not assert clean/retryable effects and required boundary variants remain absent. CR-44 clears ledger/recovery before fallible owner release, leaving a stale owner with retries falsely reporting `NOT_INSTALLED`. CR-45 manifest mismatch and recovery-write failure can strand staged files or a live host receipt without durable recovery. Exact probes are recorded in the formal review. |
| Scope classification | Implementation/contract/test correction only. Approved requirements, SPEC, architecture and delivery stage do not change; no `REQUIREMENT_CHANGED` event. |
| Continuation | Mark rework-3 historical and automatically create a fresh allocation under receipt `rcpt_local_orchestration_install_01_20260808`; no second user dispatch question. Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-032 — Ticket 01 fresh rework-4 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `65252d6` records the fourth `CHANGES_REQUESTED`. `c91041a` and `ba74caf` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_4_20260809` / `aln_local_orchestration_install_01_rework_4_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-4` starts directly from this current docs-only handoff commit. |
| Scope | Fresh red → minimal typed implementation → green for CR-40's complete state/boundary matrix, CR-44 retryable owner-release finalization and CR-45 durable or verified-compensated effects after manifest/recovery-write failure. Preserve all closed CR-36 through CR-43 behavior. No target project, real host configuration, installer package, Ticket 02+, merge/push/deploy or requirements change. |
| Required red/green evidence | Separately prove owner-release failure retries to a terminal released owner; recovery-clear then owner-release faults cannot lose authority; manifest mismatch leaves no unowned staged path; recovery-write fault after a host effect leaves either verified clean state or durable resumable recovery; same-ID retry converges and a foreign ID cannot claim residue. Complete omitted installation-ID and owned-path boundary variants and assert filesystem/host/owner/ledger/recovery state for every fault. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole positive dispatch authority. This corrected allocation is not a new ticket approval/dispatch. |
| Required return | New implementation commit(s), then one final docs-only handoff with exact first-red names/reasons, retry terminal outcomes, complete regression/type/compile/privacy/smoke, target-repository non-interference and `git diff --check`. |

## PRG-20260809-034 — Ticket 01 fifth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `5142378`; implementation `7df74e1`, `e84dff0`, `14838d9`; docs-only handoff `f90877d`; branch `codex/implementation-local-install-lifecycle-01-rework-4`. |
| Passing evidence | Owner-release and recovery-clear focused sequences retry to `REMOVED`; cooperative manifest/checkpoint compensation passes. Full 143 unittest, 143 pytest/196 subtests, strict mypy 71 files, five-module compile, diff and privacy sentinels pass. |
| Blocking findings | CR-40 matrix/red evidence remains incomplete. CR-46 loses the terminal transition when ledger deletion succeeds but final checkpoint write fails. CR-38 is reopened because install clears an active uninstall recovery. CR-42 is reopened because rollback discards an actual mismatched returned host effect. CR-43 is reopened because the existing-ledger fast path returns `INSTALLED` before active-owner/physical validation. Exact probes are in the formal review. |
| Scope classification | Implementation/contract/test correction only. Approved SPEC, architecture, acceptance, delivery stage and receipt do not change; no `REQUIREMENT_CHANGED` event. |
| Continuation | Mark rework-4 historical and automatically create a fresh allocation under receipt `rcpt_local_orchestration_install_01_20260808`; no second user dispatch question. Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-035 — Ticket 01 fresh rework-5 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `58bf113` records the fifth `CHANGES_REQUESTED`. `7df74e1`, `e84dff0`, `14838d9` and `f90877d` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_5_20260809` / `aln_local_orchestration_install_01_rework_5_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-5` starts directly from this current docs-only handoff commit. |
| Scope | Fresh red → minimal typed implementation → green for CR-40's complete boundary/port/state matrix, CR-46 atomic/idempotent ledger-to-finalize transition, reopened CR-38 operation-safe recovery consumption, CR-42 actual returned host-effect ownership and CR-43 active-owner/physical validation on every existing-ledger route. Preserve all previously closed guards. No target project, real host configuration, installer package, Ticket 02+, merge/push/deploy or requirements change. |
| Required red/green evidence | Reproduce all four review probes exactly. Separately inject failure before ledger deletion and after deletion/before final checkpoint; prove retry reaches `REMOVED`. Prove same-ID install cannot clear an uninstall recovery. Prove a host that retains the returned mismatched receipt cannot leave a live effect. Prove a second typed ledger cannot bypass the active owner. Complete manifest/host-receipt absent-value cases and every named owner/ledger/recovery/host/filesystem/runtime/process port fault with full state and retry assertions. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole positive dispatch authority. This corrected allocation is not a new ticket approval/dispatch. |
| Required return | New implementation commit(s), then one final docs-only handoff with exact first-red names/reasons for every added behavior, retry terminal outcomes, complete regression/type/compile/privacy/smoke, target-repository non-interference and `git diff --check`. |

## PRG-20260809-037 — Ticket 01 sixth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `14be507`; implementation `a3dc5a2`; docs-only handoff `7573a74`; branch `codex/implementation-local-install-lifecycle-01-rework-5`. |
| Passing evidence | Submitted four focused behaviors pass. Full 135 unittest, 135 pytest/175 subtests, strict mypy 69 files, three-module compile, diff and privacy sentinels pass. |
| Blocking findings | CR-47 replaces the approved port-driven lifecycle with a mutable-memory toy and removes fixed root, payload/manifest/digest/path ownership, host proof/absence and injected effect ports. CR-40 remains incomplete. CR-48 malformed IDs throw or diverge across install/uninstall. CR-49 shape-valid unsupported recovery phases delete effects and clear another installation's owner. CR-46 and reopened CR-38/42/43 are not proven on the approved surface. |
| Scope classification | Implementation/contract/TDD correction only. The reduced implementation contract is rejected; approved SPEC, architecture, acceptance, stage and receipt remain unchanged. |
| Continuation | Mark rework-5 historical and automatically create a fresh allocation under receipt `rcpt_local_orchestration_install_01_20260808`; no second dispatch question. Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-038 — Ticket 01 fresh rework-6 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `862f3f6` records the sixth `CHANGES_REQUESTED`. `a3dc5a2` and `7573a74` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_6_20260809` / `aln_local_orchestration_install_01_rework_6_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-6` starts directly from this current docs-only handoff commit. |
| Non-negotiable implementation surface | Deliver domain/application/ports/test-adapters under `library/local_orchestration`: strict opaque installation/host/registration/proof/digest/path types; fixed install root; payload plus manifest/digest ownership; host-issued registration receipt, removal proof and absence evidence; injected filesystem, ownership-ledger, host, runtime, process and clock ports; finite install/uninstall use cases. Mutable `Memory` or hard-coded artifact/host sets may exist only as infrastructure fakes, never as the production application contract. |
| Correction scope | Fresh red → minimal full-surface implementation → green for CR-40 complete boundary/port/state matrix; CR-46 persistence split and retry; CR-48 identical strict ID validation; CR-49 operation/phase/evidence and exact-owner authority; reopened CR-38/42/43 exact probes. Preserve all earlier proof, absence, phase, receipt, fixed-root and target-project isolation guards. No target project, real host configuration, package, Ticket 02+, merge/push/deploy or requirements change. |
| Required red/green evidence | Record first-red name/reason for every final focused behavior before source correction. Run all seven root variants; five missing-value forms for installation ID, manifest, host receipt and owned path; direct/indirect ownership bypass; every filesystem/ledger/recovery/host/runtime/process/clock fault with full state and retry assertions; exact rework-4 and rework-5 probes; existing/empty Git snapshots across success and failure. Reverse at least owner, phase, returned-effect and terminal-checkpoint guards and prove focused tests fail. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole dispatch authority; no second confirmation is valid. |
| Required return | Full implementation commit(s), final docs-only handoff, exact red/green evidence, complete regression/strict typing/in-memory compile/privacy/smoke/diff evidence and no self-review/integration. |

## PRG-20260809-040 — Ticket 01 seventh independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `263e30c`; implementation `e6b067c`; docs-only handoff `f1301be`; branch `codex/implementation-local-install-lifecycle-01-rework-6`. |
| Reproduced passing evidence | 146 unittest; 146 pytest / 195 subtests; strict mypy 72 files; library compile and diff check all pass. |
| Blocking findings | CR-50: `FINALIZE` can clear owner/recovery while receipt/files remain live. CR-51/46: post-ledger-delete fault escapes and retry returns `NOT_INSTALLED`. CR-52: install reports success without writing payload files. CR-53: multi-host request records only the first host. CR-40: required manifest/receipt, port-fault/retry and Git non-interference matrices remain absent; stage fault propagates. |
| Scope classification | Implementation/TDD correction only; approved SPEC, architecture, ticket acceptance, delivery stage and receipt do not change. |
| Continuation | Mark rework-6 historical and automatically issue a fresh allocation under the existing receipt; no second dispatch question. Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-041 — Ticket 01 fresh rework-7 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `5f7467c` records the seventh `CHANGES_REQUESTED`. `e6b067c` and `f1301be` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_7_20260809` / `aln_local_orchestration_install_01_rework_7_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-7` starts directly from this current docs-only handoff commit. |
| Non-negotiable implementation surface | Retain the strict domain contracts and injected filesystem, ownership, ledger, host, runtime, process and clock ports. Installation must physically stage every manifest payload under the fixed temporary root, verify content digests, register every selected host and persist evidence-bearing recovery before fallible effects can become unreachable. Uninstall must converge from every persisted phase without clearing exact-owner authority until receipt-proven host and file absence is verified. |
| Correction scope | Fresh red → minimal full-surface implementation → green for CR-40 complete boundary/port/state/Git matrix, CR-46/51 retry after ledger deletion and checkpoint faults, CR-50 evidence-validated `FINALIZE`, CR-52 physical staging/digest verification and CR-53 all-selected-host processing. Preserve CR-36/37/38/39/41/42/43/48/49 and all previously closed isolation guards. |
| Required red/green evidence | Before source correction, reproduce the five review probes: live effects at `FINALIZE`; ledger-delete fault and retry; success without physical file; two selected hosts; filesystem-stage exception. Add all manifest/receipt absent variants, every declared port-operation fault with finite result plus clean-or-retryable state, and existing/empty Git snapshots. Record each first-red name and reason. |
| Receipt | `rcpt_local_orchestration_install_01_20260808` remains the sole dispatch authority; this automatic correction allocation requires no second user confirmation. |
| Required return | Full implementation commit(s), complete independent-ready verification, then one docs-only handoff commit. Progress-only final messages are not a handoff. |

## PRG-20260809-042 — Bounded continuous execution authority

| Field | Value |
| --- | --- |
| Authority | The project owner instructed the control plane to check the current implementer's eventual commits, continue opening tickets for that implementer, and avoid every non-essential interruption while the owner is away. |
| Scope | After each complete implementation/docs-only return, automatically perform independent review. A failed review creates and dispatches a fresh same-ticket allocation. An approved review performs only the verified guarded integration allowed by `Workflow.md`, then selects and dispatches the next unblocked `PLANNED` ticket under the currently approved installer SPEC. |
| Ticket-bound receipts | For each already-planned successor ticket, the control plane must still create a unique pending descriptor, handoff and ticket-bound receipt that cites this authority, exact ticket, owner, baseline and correlation. This authority removes a repetitive delivery-confirmation wait; it does not permit receipt reuse or identity mismatch. |
| Fixed owner / lane | Implementation owner remains Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245` in `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; only one implementation ticket lane may be active at a time. |
| Mandatory stop | Stop only for a concrete typed `HALT`, `CHANGE_DETECTED → REQUIREMENT_CHANGED`, Wayfinder `NO-GO`, missing external authority, unsupported host/tool evidence, or a requested operation outside the approved SPEC. Ordinary progress, commits, review corrections and ticket transitions are `AUTO_CONTINUE`. |
| Exclusions | No deployment, real host mutation, target-project write, new requirement, Secret handling, merge conflict shortcut, force operation, push or release is pre-authorized by this record. |

## PRG-20260809-043 — Ticket 01 eighth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `5e772ec`; implementation `49a250e`; docs-only handoff `aafe154`; branch `codex/implementation-local-install-lifecycle-01-rework-7`. |
| Reproduced passing evidence | 150 unittest; 150 pytest / 239 subtests; strict mypy 73 files; in-memory compile, source sentinel and diff check pass. |
| Blocking findings | CR-54: shape-valid tampered recovery deletes before authoritative ledger comparison. CR-55: a post-host recovery-checkpoint fault leaves a live registration with no durable receipt. CR-56: registration-ID mismatch is accepted as `INSTALLED`. CR-40 lacks these exact red/green paths. |
| Scope classification | Implementation/contract/TDD correction only; approved SPEC, ticket, architecture, delivery stage, implementation owner and receipt do not change. |
| Continuation | Mark rework-7 historical and automatically create a fresh allocation under the existing receipt and bounded authority `PRG-20260809-042`; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-044 — Ticket 01 fresh rework-8 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `0553920` records the eighth `CHANGES_REQUESTED`. `49a250e` and `aafe154` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_8_20260809` / `aln_local_orchestration_install_01_rework_8_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-8` starts directly from this current docs-only handoff commit. |
| Correction scope | Fresh behavior red → minimal full-surface implementation → green for CR-54 authoritative ledger/recovery matching before pre-finalize effects, CR-55 precommitted or otherwise durable deterministic host receipt authority across post-effect clock/checkpoint faults, and CR-56 complete receipt identity comparison. Preserve the 150-test rework-7 behavior, all accepted contracts/ports, physical staging, all-host processing, finite results, matrices, mutation guards and Git isolation. |
| Required red/green evidence | Reproduce all three independent probes before source correction. Add shape-valid manifest mismatch and receipt mismatch at `UNINSTALL_HOSTS` and `UNINSTALL_FILES` with zero port mutation; register-after-effect exception, post-register clock fault and post-register recovery-write fault with exact cleanup/retry; one-field receipt mismatch tests for installation, host, registration, manifest digest and owned paths. Reverse each new guard and prove its focused test fails. |
| Receipt / continuation authority | `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` remain valid. This correction allocation requires no second user confirmation. |
| Required return | Ticket-only implementation commit(s), full verification, then one docs-only handoff commit. No self-review, integration, push, deployment or progress-only final. |

## PRG-20260809-046 — Ticket 01 ninth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `ed1a282`; implementation `8a7b221`; docs-only handoff `8f867cc`; branch `codex/implementation-local-install-lifecycle-01-rework-8`. |
| Reproduced passing evidence | 151 unittest; 151 pytest / 250 subtests; strict mypy 73 files; diff check and clean worktree pass. CR-54/55/56 focused behavior passes. |
| Blocking findings | CR-57: returned removal/absence proofs are ignored, so shape-valid foreign proofs can produce `REMOVED` while a host registration remains live and owner/ledger/recovery are deleted. CR-58: install cleanup releases owner before fallible recovery clear, so that fault strands recovery with no owner and every retry remains `AUTHORITY_MISMATCH`. CR-40 lacks these exact adversarial and terminal-ordering probes. |
| Scope classification | Implementation/contract/TDD correction only; approved SPEC, ticket, architecture, delivery stage, owner, receipt and bounded continuation authority do not change. |
| Continuation | Mark rework-8 historical and automatically create a fresh same-ticket allocation under receipt `rcpt_local_orchestration_install_01_20260808` and authority `PRG-20260809-042`; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-047 — Ticket 01 fresh rework-9 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `884a6c5` records the ninth `CHANGES_REQUESTED`. `8a7b221` and `8f867cc` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_9_20260809` / `aln_local_orchestration_install_01_rework_9_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-9` starts directly from this current docs-only handoff commit. |
| Correction scope | Fresh behavior red → minimal full-surface implementation → green for CR-57 exact consumption of returned `RemovalProof`/`AbsenceProof` identities before terminal authority deletion and CR-58 retryable install-cleanup terminal ordering across recovery-clear/owner-release faults. Preserve CR-54/55/56, every passing strict contract/port, physical staging, all-host behavior, complete boundary/fault/Git matrix and finite public results. |
| Required red/green evidence | First reproduce a typed adversarial host/filesystem provider that returns shape-valid foreign or mismatched proofs without removing the requested effect; no case may return terminal success or clear owner/ledger/recovery. Reproduce cleanup `CLEAR_RECOVERY` failure after owner release and prove repeated calls currently remain `AUTHORITY_MISMATCH`. Add one-field proof mismatch/replay/absence matrices, every cleanup terminal ordering, exact authority retention and retry convergence. Reverse each new guard and prove the focused test fails. |
| Receipt / continuation authority | `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` remain valid. This correction allocation requires no second user confirmation. |
| Required return | Ticket-only implementation commit(s), full verification, then one docs-only handoff commit. No self-review, integration, push, deployment or progress-only final. |

## PRG-20260809-049 — Ticket 01 tenth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `8ea2983`; implementation `815d126`; docs-only handoff `5405c24`; branch `codex/implementation-local-install-lifecycle-01-rework-9`. |
| Reproduced passing evidence | 151 unittest; 151 pytest / 279 subtests; strict mypy 75 files; diff check and clean worktree pass. Submitted CR-57/58 focused tests pass. |
| Blocking findings | CR-59: installation/host/manifest/path actual-receipt mismatches retain a live registration outside recovery and retry remains `PROOF_MISMATCH`. CR-60: new install ignores stage/completion proof identity and existing-ledger install never verifies live effects, so both foreign-proof and stale-ledger probes return `INSTALLED` without files. CR-61: a constructed invalid nested root bypasses validation, executes ports and returns `INSTALLED`. CR-40 lacks or accepts these paths. |
| Scope classification | Implementation/contract/TDD correction only; approved SPEC, ticket, architecture, delivery stage, owner, receipt and bounded continuation authority do not change. |
| Continuation | Mark rework-9 historical and automatically create a fresh same-ticket allocation under receipt `rcpt_local_orchestration_install_01_20260808` and authority `PRG-20260809-042`; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-050 — Ticket 01 fresh rework-10 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `4eaeb3f` records the tenth `CHANGES_REQUESTED`. `815d126` and `5405c24` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_10_20260809` / `aln_local_orchestration_install_01_rework_10_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-10` starts directly from this current docs-only handoff commit. |
| Correction scope | Fresh behavior red → minimal full-surface implementation → green for CR-59 durable expected-intent/actual-observation cleanup across all receipt mismatch fields, CR-60 exact stage/completion/live-ledger effect proof before every `INSTALLED`, and CR-61 recursive strict revalidation of constructed nested command/domain inputs before ports. Preserve CR-54 through CR-58 and the complete passing proof/terminal/fault/Git surface. |
| Required red/green evidence | Reproduce four non-registration receipt mismatch first-call and retry residues; foreign stage/completion proof without requested files; stale exact-shaped ledger after host/files disappear; constructed invalid root/installation/manifest/artifact/path/host/receipt values with zero port calls. Add exact cleanup/retry, adversarial proof and reverse mutation tests for each guard. |
| Receipt / continuation authority | `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` remain valid. This correction allocation requires no second user confirmation. |
| Required return | Ticket-only implementation commit(s), full verification, then one docs-only handoff commit. No self-review, integration, push, deployment or progress-only final. |

## PRG-20260809-052 — Ticket 01 eleventh independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `85b7e96`; implementation `ea99ccc`; docs-only handoff `415f2bd`; branch `codex/implementation-local-install-lifecycle-01-rework-10`. |
| Reproduced passing evidence | 151 unittest; 151 pytest / 242 subtests; strict mypy 73 files; 54-module in-memory compile, diff check and clean worktrees pass. Submitted CR-59/60/61 focused behavior passes. |
| Blocking findings | CR-62 reopens fixed-root multi-install ownership and cross-install deletion. CR-63 permits forged recovery intent/phase evidence to delete real effects or return `REMOVED` while leaving them live. CR-64 accepts dot/drive/scheme-like owned locators, including uncaught post-effect `ValueError`. CR-65 discards typed runtime/process and checkpoint proofs, accepting foreign/no-op outcomes as terminal success. CR-40 omits these retained adversaries. |
| Scope classification | Implementation/contract/TDD correction only; approved SPEC, ticket, architecture, delivery stage, owner, receipt and bounded continuation authority do not change. |
| Continuation | Mark rework-10 historical and automatically create a fresh same-ticket allocation under receipt `rcpt_local_orchestration_install_01_20260808` and authority `PRG-20260809-042`; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-053 — Ticket 01 fresh rework-11 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `857fde2` records the eleventh `CHANGES_REQUESTED`. `ea99ccc` and `415f2bd` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_11_20260809` / `aln_local_orchestration_install_01_rework_11_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-11` starts directly from this current docs-only handoff commit. |
| Correction scope | Fresh behavior red → minimal full-surface implementation → green for CR-62 exclusive fixed-root ownership, CR-63 causal recovery/ledger/intent authority, CR-64 parsed canonical owned locators and CR-65 exact terminal/checkpoint proof consumption. Preserve the direct CR-59/60/61 corrections, CR-54 through CR-58, all-host physical staging, finite public results and complete fault/Git isolation surface. |
| Required red/green evidence | Before production code, reproduce: two installation IDs sharing the fixed root including interrupted recovery; forged `INSTALL/CLEANUP`, `UNINSTALL_HOSTS` and `FINALIZE` owner/intent/receipt/manifest evidence; raw and constructed dot/drive/UNC/device/scheme/encoded/non-normalized owned paths with zero effects; foreign/unavailable/replayed/no-op runtime, process, ledger-delete and recovery-checkpoint proofs. Every failure must retain exact retry authority, and reversing each guard must make its focused test fail. |
| Receipt / continuation authority | `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` remain valid. This correction allocation requires no second user confirmation. |
| Required return | Ticket-only implementation commit(s), full verification, then one docs-only handoff commit. No self-review, integration, push, deployment or progress-only final. |

## PRG-20260809-055 — Ticket 01 twelfth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `50b0591`; implementation `f17da74`, `8193067`; docs-only handoff `95ec79a`; branch `codex/implementation-local-install-lifecycle-01-rework-11`. |
| Reproduced passing evidence | 149 unittest; 149 pytest / 262 subtests; strict mypy 72 files; 54-module in-memory compile, source sentinel, diff check and clean worktree pass. Submitted CR-62/64 and direct proof checks pass. |
| Blocking findings | CR-66 accepts predictable, shape-valid `FINALIZE` assertions as causal post-delete evidence and returns `REMOVED` while live host/files remain. CR-67 clears install recovery before owner release is proven, producing permanent `OWNER_WITHOUT_AUTHORITY`. CR-68 releases the owner after a recovery-write replay proof even though recovery was persisted, producing permanent `ORPHANED_AUTHORITY`. CR-40 omits all three exact sequences. |
| Scope classification | Implementation/contract/TDD correction only; approved SPEC, ticket, architecture, delivery stage, owner, receipt and bounded continuation authority do not change. |
| Continuation | Mark rework-11 historical and automatically create a fresh same-ticket allocation under receipt `rcpt_local_orchestration_install_01_20260808` and authority `PRG-20260809-042`; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-056 — Ticket 01 fresh rework-12 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `8361053` records the twelfth `CHANGES_REQUESTED`. `f17da74`, `8193067` and `95ec79a` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_12_20260809` / `aln_local_orchestration_install_01_rework_12_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-12` starts directly from this current docs-only handoff commit. |
| Correction scope | Fresh behavior red → minimal full-surface implementation → green for CR-66 causal pre-delete/post-delete terminal evidence with fresh terminal absence observation, CR-67 root-scoped retry-safe cleanup terminalization and CR-68 authoritative recovery-write mismatch/read-back handling. Preserve CR-59 through CR-65, the complete canonical path/root matrix, multihost physical lifecycle, finite public results and Git isolation. |
| Required red/green evidence | Before source implementation, reproduce all three review probes exactly: valid-shaped forged `FINALIZE` while host/files remain live; stage-proof failure paired with foreign/replayed/no-op owner release during install cleanup; recovery-write foreign/replayed/no-op proof after exact state persistence. Add every operation phase, one-fault terminal ordering and retry assertion. Reverse causal-finalize, owner-readback and persisted-recovery branches separately and prove focused tests fail. |
| Receipt / continuation authority | `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` remain valid. This correction allocation requires no second user confirmation. |
| Required return | Ticket-only implementation commit(s), full regression/strict typing/in-memory compile/sentinel/Git isolation evidence, then one docs-only handoff commit. No self-review, integration, push, deployment, historical-source reuse or progress-only final. |

## PRG-20260809-058 — Ticket 01 thirteenth independent review

| Field | Value |
| --- | --- |
| State | `REVIEW / CHANGES_REQUESTED` |
| Reviewed range | Baseline `88412e1`; implementation `71c6704`; docs-only handoff `ffeea79`; branch `codex/implementation-local-install-lifecycle-01-rework-12`. |
| Reproduced passing evidence | 140 unittest; 140 pytest / 233 subtests; strict mypy 72 files; 54-module in-memory compile, source sentinel, Git isolation, diff check and clean worktree pass. Submitted CR-66/67/68 focused cases pass. |
| Blocking findings | CR-69 strands a returned actual host receipt that differs from deterministic intent while clearing owner/ledger/recovery. CR-70 permits a forged `FINALIZE_INTENT` to delete the ledger before terminal absence and then block permanently. CR-71 reports ownerless ledger/live effects as `NOT_INSTALLED`. CR-72 accepts an ownerless forged install-cleanup record as destructive authority. CR-40 omits all four paths and the retained full matrix. |
| Scope classification | Implementation/contract/TDD correction only; approved SPEC, ticket, architecture, delivery stage, owner, receipt and bounded continuation authority do not change. |
| Continuation | Mark rework-12 historical and automatically create a fresh same-ticket allocation under receipt `rcpt_local_orchestration_install_01_20260808` and authority `PRG-20260809-042`; Ticket 02 remains `DEPENDENCY_WAIT`. |

## PRG-20260809-059 — Ticket 01 fresh rework-13 handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENT / FRESH_TDD_REWORK` |
| Review baseline | `cfb7fc4` records the thirteenth `CHANGES_REQUESTED`. `71c6704` and `ffeea79` join all older implementation branches as immutable historical evidence. |
| Fresh handoff / allocation | `hnd_local_orchestration_install_01_rework_13_20260809` / `aln_local_orchestration_install_01_rework_13_20260809`; branch `codex/implementation-local-install-lifecycle-01-rework-13` starts directly from this current docs-only handoff commit. |
| Correction scope | Fresh behavior red → minimal complete implementation → green for CR-69 durable actual-receipt binding/cleanup, CR-70 causal non-forgeable pre-delete transition and absence-before-ledger-delete ordering, CR-71 conjunction-based terminal absence, and CR-72 exact-owner authorization before every cleanup effect. Preserve CR-59 through CR-68, the complete canonical path/root matrix, all-host physical lifecycle, finite public results and Git isolation. |
| Required red/green evidence | Before source implementation, reproduce all four review probes exactly: returned actual receipt mismatch with live effect and no authority; exact-shaped forged `FINALIZE_INTENT` with live effects; ownerless exact ledger/live effects; ownerless exact-shaped `INSTALL_CLEANUP`. Extend actual-receipt field matrices, causal phase-transition matrices and owner/ledger/recovery/effect conjunction matrices. Reverse each guard separately and prove the focused test fails. |
| Receipt / continuation authority | `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` remain valid. This correction allocation requires no second user confirmation. |
| Required return | Ticket-only implementation commit(s), full regression/strict typing/in-memory compile/sentinel/Git isolation evidence, then one docs-only handoff commit. No self-review, integration, push, deployment, historical-source reuse or progress-only final. |

## PRG-20260809-060 — same-ticket correction branch policy

| Field | Value |
| --- | --- |
| Event | `REQUIREMENT_CHANGED / WORKFLOW_POLICY` |
| Owner decision | A normal `CHANGES_REQUESTED` must continue on the existing ticket branch with additive correction commits. Commit SHA records are the immutable review evidence; a review rejection alone must not create another branch or force source reconstruction. |
| Fresh-branch gate | A new branch is permitted only with recorded `FRESH_BRANCH_REQUIRED` evidence: approved requirement change, owner/worktree replacement, unsafe worktree contamination, or verified baseline conflict that cannot be handled safely with additive correction. |
| Automation effect | `ticket-01-implementer-watchdog` now retains the same ticket, owner, worktree, branch, allocation and receipt for ordinary corrections. It no longer rejects historical source reuse or creates a fresh allocation merely because review returned `CHANGES_REQUESTED`. |
| Active lane | Ticket 01 rework-13 remains active on its current branch; this policy does not interrupt, recreate or rewrite its in-progress implementation. |

## PRG-20260809-062 — break unbounded Ticket-01 review loop

| Field | Value |
| --- | --- |
| Event | `REQUIREMENT_CHANGED / REVIEW_CONVERGENCE` |
| Root cause | Ticket 01 used an unbounded “complete fault matrix”; CR-40 remained open in 11 review rounds while the two-outcome audit Router mapped every non-approval back to the same correction lane. Branch retention alone did not remove that loop. |
| Immediate control | `ticket-01-implementer-watchdog` is paused. The active rework-13 implementation task is not interrupted, but no automatic rework-14 or further correction may be dispatched under the old prompt. |
| Frozen closure | `CLOSURE-LOCAL-INSTALL-T01-20260809-01` freezes seven invariants and finite input/state/receipt/port/retry/terminal/Git matrices. The next review must run the whole set once and batch all findings. |
| Finding routes | `IMPLEMENTATION_DEFECT`／`EVIDENCE_DEFECT` permit one same-branch correction; `TICKET_DEFECT` returns to ticket design; `REQUIREMENT_CHANGED` returns to Grill/SPEC; `OUT_OF_SCOPE_HARDENING` becomes a later non-blocking ticket. |
| Loop breaker | A failed correction review emits `CONVERGENCE_REVIEW_REQUIRED`; it cannot automatically dispatch a third implementation attempt for the same Closure revision. |

## PRG-20260809-063 — revoke branch experiment and reopen minimal Ticket 01

| Field | Value |
| --- | --- |
| Event | `TICKET_DEFECT / OWNER_REOPEN` |
| Owner direction | The project owner rejected the fourteen-branch experiment and ordered Ticket 01 deleted or reopened as the original small task. |
| Rollback evidence | Fourteen `codex/implementation-local-install-lifecycle-01*` refs were deleted. The implementation worktree is clean and detached at `846caaf`; `main` contains no `library/local_orchestration`. Ticket 02 and Ticket 03 worktrees were untouched. |
| Root cause | Control-plane review repeatedly replaced one ticket branch with a fresh branch and expanded review findings into implementation scope instead of reviewing the approved small ticket and keeping corrections additive. |
| Reopened scope | Five production files, one test file, synchronous temporary fake lifecycle, hard line ceiling and finite closure `C1..C8`. Crash recovery, transition grants, exhaustive fault matrices and all real effects are excluded. |
| Handoff / allocation | `hnd_local_orchestration_install_01_reopen_20260809` / `aln_local_orchestration_install_01_reopen_20260809`; same implementation owner, existing worktree and receipt `rcpt_local_orchestration_install_01_20260808`; single branch `codex/implementation-local-install-lifecycle-01`. |
| Review rule | One complete batched review and at most one additive correction on the same branch. No new worktree/branch and no automatic third attempt. |
| Automation | Watchdog remains paused and is not part of the reopened dispatch. |

## PRG-20260809-064 — reopened Ticket 01 implementation handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMPLETED / INDEPENDENT_REVIEW_PENDING` |
| Ticket / closure | `01-owned-install-lifecycle` / `CLOSURE-LOCAL-INSTALL-T01-REOPEN-01` (`C1..C8`). |
| Implementation evidence | Ticket-only commit `ddd9f55`; branch `codex/implementation-local-install-lifecycle-01`; implementation baseline `8704ada`. |
| Red evidence | The first executable run named all eight `test_c1_*` through `test_c8_*` cuts and failed each with its corresponding “not implemented” assertion before production files existed. |
| Green evidence | Exact unittest: 8 passed. Strict mypy: 6 files, no issues. In-memory compile: 6 files. C1/C2 lifecycle smoke and C8 source sentinel: 3 passed. External C7 probe kept the existing temporary repository porcelain at `?? existing.txt` and the empty repository porcelain empty. `git diff --check` passed. |
| Scope / ceiling | Exactly five production files and `tests/test_owned_install_lifecycle.py`; production 517/600 non-blank lines, test 349/500. No historical Ticket-01 source, extra branch/worktree, real host/process/Git/project effect, Ticket 02+, merge, push, deployment or schedule action. |
| Handoff | `hnd_local_orchestration_install_01_reopen_20260809` / `aln_local_orchestration_install_01_reopen_20260809` / receipt `rcpt_local_orchestration_install_01_20260808`. Control-plane reviewer must independently inspect and execute `C1..C8`; implementation owner makes no review decision. |

## PRG-20260809-065 — Ticket 01 C2 evidence correction handoff

| Field | Value |
| --- | --- |
| State | `CORRECTION_COMPLETED / CORRECTION_REVIEW_PENDING` |
| Review / finding | Independent review commit `148f14f`; `CR-REOPEN-01` / `EVIDENCE_DEFECT` / `C2`. |
| Additive correction | Commit `040a0f6` adds only a direct physical-absence assertion for `payload/plugin.txt` to the existing C2 test. Production files are unchanged from `ddd9f55`. |
| Reverse-mutation evidence | Replacing the fake filesystem's physical `target.unlink()` with a no-op made focused C2 fail because `FileNotFoundError` was not raised; restoring the unlink made focused C2 pass. |
| Green evidence | Full `C1..C8`: 8 passed. Strict mypy: 6 files, no issues. In-memory compile and C8 sentinel passed. Actual temporary Git porcelain remained `?? existing.txt` / empty. `git diff --check` passed. Production remains 517/600 non-blank lines; test is 351/500. |
| Scope / continuation | Same branch, worktree, allocation, handoff and receipt. No production change, extra file/branch/worktree, merge, push, deployment or schedule action. The control-plane reviewer owns the correction decision. |

## PRG-20260809-066 — reopened Ticket 01 approved and integrated

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED → REVIEW_APPROVED → GUARDED_INTEGRATION → ACTION_COMPLETED` |
| Final evidence | Implementation `ddd9f55`; additive C2 evidence correction `040a0f6`; handoffs `c29f8ed` / `3c27261`; final review `dc63364`. |
| Review result | `APPROVED / READY_TO_MERGE`; all C1..C8 items passed and `CR-REOPEN-01` was closed by a successful reverse mutation. |
| Integration | Merge commit `491f98b` combined the reviewed branch into `main` without conflict, force, reset, overwrite or push. |
| Integrated verification | 8/8 unittest, strict mypy over six files, in-memory compile and diff check passed on `main`; actual temporary Git non-interference passed during final correction review. |
| Scope result | Exactly five production files (`517 / 600` non-blank lines) and one test file (`351 / 500`); no historical lifecycle framework, real host/process/Git/project effect or Ticket 02+ implementation entered Ticket 01. |
| Allocation / continuation | Ticket-01 allocation released. Ticket 02 is dependency-unblocked but remains `PLANNED` until its own unique allocation and receipt. Watchdog remains paused; no schedule was created or resumed. |

## PRG-20260809-067 — bounded Ticket 02 dispatch

| Field | Value |
| --- | --- |
| Router event | `TICKET_DISPATCH_REQUIRED → IMPLEMENTATION_DISPATCH_CONFIRMED → AUTO_CONTINUE / IMPLEMENT` |
| Ticket / closure | `02-metadata-runtime-and-guarded-git` / `CLOSURE-LOCAL-INSTALL-T02-01` (`D1..D8`). |
| Scope repair | The prior open-ended runtime/registry/Git ticket was bounded to five production files, one test, a 650/500 non-blank line ceiling and a typed decision only. Real Git commands and recovery/state-machine expansion are excluded. |
| Reuse selection | Only `workflow-router-poc@24387c2` public `ProjectId` and finite event/status vocabulary are selected. The Router engine, telemetry, Temporal, policy response and audit coordinator are rejected as unnecessary. |
| Handoff / allocation | `hnd_local_orchestration_install_02_20260809` / `aln_local_orchestration_install_02_20260809`; receipt `rcpt_local_orchestration_install_02_20260809`; correlation `corr-local-orchestration-install-02-20260809`; authority `PRG-20260809-042`. |
| Owner boundary | The existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` remains the only implementation worktree. Ticket 02 uses exactly one branch, `codex/implementation-local-metadata-git-02`; Ticket 01 source and branch are immutable evidence. |
| Not authorized | Another worktree/branch, Ticket 01 modification, real Git/host/project mutation, Ticket 03+, merge, push, deployment or schedule action. |

## PRG-20260809-068 -- bounded Ticket 02 implementation handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMPLETED / INDEPENDENT_REVIEW_PENDING` |
| Ticket / closure | `02-metadata-runtime-and-guarded-git` / `CLOSURE-LOCAL-INSTALL-T02-01` (`D1..D8`). |
| Baseline / implementation | Exact baseline `b44cd0200d4541fa62a34d8a128f28acb2988d1a`; implementation commit `6cc8fb50498f2091c71b16a4483e98c2ce1de8e0`; branch `codex/implementation-local-metadata-git-02`. |
| Red evidence | The first executable run named all eight `D1` through `D8` cuts and failed each: claim-once runtime, human-wait routing, canonical registry admission, strict metadata boundary, shared guarded decision, declared failure containment, privacy/repository isolation and source sentinel were all absent before production implementation. |
| Green evidence | Exact unittest `tests.test_metadata_runtime_and_guarded_git`: 8 passed. Strict mypy: six authorized files, no issues. In-memory compile: six files. Focused D1/D2/D8 smoke: 3 passed. `git diff --check` passed. |
| Actual Git isolation | An external temporary repository retained its pre-existing porcelain exactly as `?? existing.txt`; a second empty repository remained empty; recursive byte snapshots before and after the guarded decision were identical. No production code invoked Git, subprocess, network, target-project write or background execution. |
| Reverse-mutation evidence | D1 replay-guard bypass returned completion; D2 human-wait bypass returned completion; D3 locator equality bypass admitted suffix/case mismatch; D4 nonblank-ID bypass admitted empty identifiers; D5 dirty guard bypass allowed fast-forward; D6 reason collapse lost `REGISTRY_RESOLVE_FAILED`; D7 locator persistence exposed the private key; D8 a `subprocess` source marker defeated the sentinel. Each focused test failed under its mutation and passed after restoration. |
| Boundary result | Only the selected public `ProjectId` contract is reused. The event store receives only `EventId`; the Router receives a sanitized `RouterResumeRequest` with no locator; persisted checkpoints are metadata-only. Every decision is bound to the exact project, registration, installation locator and repository snapshot, or returns a finite typed block/halt result. |
| Scope / ceiling | Exactly five authorized production files and `tests/test_metadata_runtime_and_guarded_git.py`; production 578/650 non-blank lines, test 333/500. Ticket 01 contracts, ports, lifecycle, fakes and tests are unchanged. |
| Handoff authority | Handoff `hnd_local_orchestration_install_02_20260809`; allocation `aln_local_orchestration_install_02_20260809`; receipt `rcpt_local_orchestration_install_02_20260809`; authority `PRG-20260809-042`. The implementation owner makes no review or integration decision. |

## PRG-20260809-069 - stale-lane rollback and Ticket 02 approval

| Field | Value |
| --- | --- |
| Owner direction | Audit the runaway Ticket-01 era once, remove useless worktrees/branches, retain only the documented control and sole implementation worktrees, and do not resume a schedule. |
| Pre-cleanup evidence | Git listed four worktrees and six implementation branches. `workflow-ticket-02@90e9191` and `workflow-ticket-03@43033bf` were clean, inactive and fully contained in `main`; the completed Ticket-01 branch was also integrated. |
| Historical disposition | Rejected `9eda250` and historical Router `3fa2270` were retained as `archive/blocked-plugin-policy-response-03-9eda250` and `archive/historical-private-router-saas-01-3fa2270`; their obsolete branch refs were deleted. |
| Post-cleanup state | Exactly two worktrees remain: control `main` and `workflow-implementation`. Exactly two local branches remain: `main` and current `codex/implementation-local-metadata-git-02`. The implementation owner removed only reviewer-generated bytecode caches and returned a clean worktree. |
| Ticket-02 range | Baseline `b44cd02`; implementation `6cc8fb5`; docs-only handoff `cc38c5d`; formal review `doc/reviews/local-orchestration-installer/02-metadata-runtime-and-guarded-git-code-review.md`. |
| Independent result | `APPROVED / READY_TO_MERGE`: D1..D8 passed once, all eight reverse mutations failed as intended, strict mypy/compile/scope checks passed, and actual allowed/blocked temporary Git repos retained identical bytes and porcelain. |
| Merge resolution | The only merge-tree conflict was the two append-only progress sections at EOF. Both were retained in chronological order as PRG-068 handoff and PRG-069 review; no source or test conflict existed. |
| Safety | No reset, force, overwrite, push, deployment, target-project write, real host effect, schedule creation or schedule resume occurred. |

## PRG-20260809-070 - Ticket 02 integrated and lane released

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED → REVIEW_APPROVED → GUARDED_INTEGRATION → ACTION_COMPLETED` |
| Evidence | Implementation `6cc8fb5`; handoff `cc38c5d`; review `4527f49`; merge `92c58bf`. |
| Integrated verification | 8/8 unittest, strict mypy over six files, in-memory compile and diff check passed on committed `main`. |
| Merge resolution | The only conflict was the append-only WorkProgress EOF; PRG-068 implementation handoff and PRG-069 review/cleanup were both preserved. No source/test conflict existed. |
| Lane release | Allocation `aln_local_orchestration_install_02_20260809` released. The sole implementation worktree is clean and detached at `92c58bf`; the integrated Ticket-02 branch was deleted. |
| Repository state | Two worktrees remain, and `main` is the only local branch. Rejected/historical heads remain only as the two recorded archive tags. |
| Continuation | Ticket 03 remains `PLANNED` and unallocated until a separate bounded dispatch. The watchdog stays paused; no schedule was created or resumed. |

## PRG-20260809-071 - bound Ticket 03 host capability gate

| Field | Value |
| --- | --- |
| Router event | `TICKET_SELECTION → GRILL → TICKET_REPAIR / PLANNED` |
| Root defect | The prior draft mixed two live hosts, process execution, external account/policy discovery, broad fault coverage and packaging preparation, and incorrectly requested a fresh worktree. |
| Bounded result | Closure `CLOSURE-LOCAL-INSTALL-T03-01` freezes H1..H8; exactly four production files, one test and 550/450 non-blank ceilings. Only strict contracts, one synchronous capability gate and recorded fakes are authorized. |
| Reuse result | No catalog module selected. `identity-resolution` is not host-install authority and Router code is unrelated; only integrated `InstallationId` may be reused. |
| Live boundary | No production Codex/Claude adapter, command, subprocess, login, host config/cache edit or real host mutation. Both hosts remain `UNVERIFIED`; a support claim requires external authority and change control. |
| Lane boundary | Existing sole implementation worktree only; one branch is permitted only after a unique Ticket-03 dispatch commit, allocation and receipt. No schedule was created or resumed. |

## PRG-20260809-072 - bounded Ticket 03 dispatch

| Field | Value |
| --- | --- |
| Router event | `TICKET_DISPATCH_REQUIRED → IMPLEMENTATION_DISPATCH_CONFIRMED → AUTO_CONTINUE / IMPLEMENT` |
| Ticket / closure | `03-reversible-agent-host-lifecycle` / `CLOSURE-LOCAL-INSTALL-T03-01` (`H1..H8`). |
| Handoff / allocation | `hnd_local_orchestration_install_03_20260809` / `aln_local_orchestration_install_03_20260809`; receipt `rcpt_local_orchestration_install_03_20260809`; correlation `corr-local-orchestration-install-03-20260809`; authority `PRG-20260809-042`. |
| Owner boundary | Existing sole `workflow-implementation` worktree; one new-ticket branch `codex/implementation-host-capability-gate-03`. Tickets 01/02 remain immutable and released. |
| Granted scope | Four production files, one test, 550/450 line ceilings, recorded fakes and H1..H8 evidence. No catalog module is imported beyond integrated `InstallationId`. |
| Not authorized | Another worktree/branch, real Codex/Claude command, subprocess/network/login/config mutation, Ticket-01/02 changes, packaging, merge, push, deployment or schedule action. |

## PRG-20260809-073 - bounded Ticket 03 implementation handoff

| Field | Value |
| --- | --- |
| State | `IMPLEMENTATION_COMPLETED / INDEPENDENT_REVIEW_PENDING` |
| Ticket / closure | `03-reversible-agent-host-lifecycle` / `CLOSURE-LOCAL-INSTALL-T03-01` (`H1..H8`). |
| Baseline / implementation | Exact dispatch baseline `963319b930bfdfbd3851ee6c98343d6218684ff9`; implementation commit `16597b676103df4eb5a9c9673de07bd9b2c29f9e`; branch `codex/implementation-host-capability-gate-03`. |
| Red evidence | Before production files existed, the first exact unittest run executed eight named tests and failed H1 through H8 independently with the public Ticket-03 contract reported as not implemented. |
| Green evidence | Exact H1..H8 unittest: 8 passed. Full project discovery: 155 passed. Strict mypy: five authorized files, no issues. In-memory compile: five files. H1/H2/H8 smoke and `git diff --check` passed. |
| Actual Git isolation | A supported recorded fake and an unavailable blocked fake ran between snapshots of one existing and one empty actual temporary Git repository. Both recursive byte snapshots were identical, existing porcelain remained `?? existing.txt`, and empty porcelain remained empty. |
| Reverse-mutation evidence | H1 retained the registration after unregister; H2 bypassed recorded-request revalidation; H3 relaxed the canonical key; H4 relaxed opaque evidence validation; H5 accepted a foreign receipt; H6 collapsed unavailable into access-denied; H7 added a source sentinel to the blocked report; H8 inserted a forbidden capability marker. Every corresponding focused test exited nonzero and passed after exact restoration. |
| Capability boundary | The only reusable type is integrated `InstallationId`. `CODEX` and `CLAUDE` public queries always return `UNVERIFIED` with zero lifecycle calls. Only host `RECORDED` can enter the fake lifecycle, and even a non-validating copied public-host request is revalidated and blocked before effects. No production adapter or live support claim exists. |
| Scope / ceiling | Exactly four authorized production files and `tests/test_reversible_agent_host_lifecycle.py`; production 545/550 non-blank lines and test 317/450. Ticket-01/02 source and tests are unchanged; no additional file, branch or worktree was created. |
| Handoff authority | Handoff `hnd_local_orchestration_install_03_20260809`; allocation `aln_local_orchestration_install_03_20260809`; receipt `rcpt_local_orchestration_install_03_20260809`; correlation `corr-local-orchestration-install-03-20260809`; authority `PRG-20260809-042`. The implementation owner makes no review or integration decision. |

## PRG-20260809-074 - Ticket 03 H7 proof-boundary correction handoff

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED → REVIEW → VALIDATION_FAILED → RETRY / AUTO_CONTINUE` |
| Initial review | Control commit `b343df4`; report `doc/reviews/local-orchestration-installer/03-reversible-agent-host-lifecycle-code-review.md`; result `CHANGES_REQUESTED`. |
| Batched finding | H7 `IMPLEMENTATION_DEFECT` plus `EVIDENCE_DEFECT`: a non-validating nested removal-proof evidence value returned by the lifecycle port can reach a `SUPPORTED` serialized report; the committed H7 test does not inject that port output. |
| Reproduction | Reviewer returned a forged `HostEvidenceId.model_construct(value="SECRET-SENTINEL")` inside the removal proof and a valid absent result. `verify_recorded` returned `SUPPORTED` and the sentinel appeared in `model_dump_json()`. |
| Verification already passed | Exact H1..H8 8/8; full discovery 155/155; strict mypy 5 files; compile, scope/ceiling, actual-Git isolation and eight original reverse mutations. Only the H7 output-boundary probe failed. |
| Correction lane | Same Ticket 03 owner, sole implementation worktree, branch `codex/implementation-host-capability-gate-03`, allocation `aln_local_orchestration_install_03_20260809`, receipt `rcpt_local_orchestration_install_03_20260809`; closure unchanged. |
| Required return | One additive implementation correction commit, one docs-only correction handoff, focused H7 regression/reverse mutation, full H1..H8, full suite, strict mypy, compile/source/scope/Git checks and clean status. |
| Prohibited | Reset/amend/force/overwrite, another branch/worktree, live host action, target-project write, push/deploy or schedule action. This is the only correction review for this closure. |

## PRG-20260809-075 - Ticket 03 H7 proof-boundary correction implementation handoff

| Field | Value |
| --- | --- |
| State | `CORRECTION_COMPLETED / INDEPENDENT_CORRECTION_REVIEW_PENDING` |
| Ticket / closure | `03-reversible-agent-host-lifecycle` / unchanged `CLOSURE-LOCAL-INSTALL-T03-01` (`H1..H8`). |
| Review / correction authority | Initial review `b343df4` (`CHANGES_REQUESTED`); correction record `PRG-20260809-074`; expected control baseline `976d436e484201a3f0039c61907de93dae324d15`; bounded owner authority `PRG-20260809-042`. |
| Existing lane | Same branch `codex/implementation-host-capability-gate-03`, sole implementation worktree, handoff `hnd_local_orchestration_install_03_20260809`, allocation `aln_local_orchestration_install_03_20260809` and receipt `rcpt_local_orchestration_install_03_20260809`. No branch or worktree was added or switched. |
| Additive correction | Source-and-test commit `673ff7c50121db21460c87d1cbb28731ce358f49` recursively reconstructs the lifecycle-returned `AgentHostRemovalProof` at the Gate boundary. Invalid nested evidence now returns `REMOVAL_PROOF_MISMATCH` before absence verification or `SUPPORTED` / `REMOVED` serialization. |
| First red evidence | `test_h7_forged_nested_removal_evidence_fails_before_absence_check` returned `SUPPORTED`; its serialized removal proof contained `SECRET-SENTINEL`. The adversarial lifecycle supplied a nominal proof whose nested `HostEvidenceId` used non-validating construction and otherwise returned a valid absence command. |
| Green evidence | Focused H7 passed; exact H1..H8 module passed 9/9; full discovery passed 156/156; strict mypy passed for all five authorized files; in-memory compile passed for the same five files; `git diff --check` and the production forbidden-capability scan passed. Production is 549/550 and the test is 351/450 non-blank lines. |
| Actual Git isolation | Supported, unavailable-blocked and forged-proof probes ran between recursive SHA-256 snapshots of one existing and one empty actual temporary Git repository. Both remained byte-identical; porcelain remained `?? existing.txt` and empty respectively. |
| Reverse mutation | Removing only the Gate proof reconstruction made the focused H7 test fail again with `SUPPORTED` and the serialized sentinel. Restoring it made the focused test and full verification pass. |
| Scope / handoff | Only `host_lifecycle.py` and the existing Ticket-03 test changed in the correction commit; this entry is the separate docs-only handoff. No review decision, live host action, target-project write, Ticket-01/02 edit, merge, push, deployment or schedule action was performed. |

## PRG-20260809-076 - Ticket 03 approved, integrated and lane released

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED → CORRECTION_REVIEW / VALIDATION_PASSED → HANDOFF / AUTO_CONTINUE` |
| Ticket / closure | `03-reversible-agent-host-lifecycle` / `CLOSURE-LOCAL-INSTALL-T03-01` (`H1..H8`) complete |
| Revisions | Initial implementation `16597b6`; H7 correction `673ff7c`; implementation handoffs `62394f1` and `633505e`; final review `5601594`; guarded merge `60cb8cf` |
| Final verification | Ticket module 9/9, full discovery 156/156, strict mypy five files, compile/source scans, actual-Git isolation and focused H7 reverse mutation all passed |
| Merge resolution | merge-tree found only append-only `doc/WorkProgressReport.md` contention. PRG-073 implementation evidence, PRG-074 correction handoff and PRG-075 correction evidence were explicitly retained in order; no source/test conflict existed |
| Capability boundary | Recorded fake is supported; Codex and Claude remain `UNVERIFIED`. No live adapter, command, subprocess, login, target-project write, push, deployment or schedule action occurred |
| Lane release | Allocation `aln_local_orchestration_install_03_20260809` released. The sole implementation worktree is clean and detached at `60cb8cf`; the fully integrated Ticket-03 branch was deleted. Exactly two worktrees and only local branch `main` remain |
| Next Router decision | `HALT / EXTERNAL_DECISION_REQUIRED`: Ticket 04 lacks explicit authority for a verified live host lifecycle and lacks an available pinned Inno Setup compiler (`ISCC.exe` absent from PATH and standard locations). No implementation ticket is dispatched |

## PRG-20260809-077 — pinned Inno toolchain and isolated Codex lifecycle proof

| Field | Value |
| --- | --- |
| Router event | `EXTERNAL_AUTHORITY_GRANTED → CAPABILITY_PROBE → ACTION_COMPLETED → TICKET_SELECTION` |
| Owner authority | Obtain and configure a fixed Inno Setup compiler version, then perform one Codex test registration and complete removal verification without touching a target project. Continue under the documented role/worktree rules. |
| Inno Setup proof | Official Winget package `JRSoftware.InnoSetup` version 6.7.3 installed per user. Installer SHA-256 `9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732`; installed `ISCC.exe` Authenticode status `Valid`, signer Pyrsys B.V.; registry version 6.7.3. The bundled example compiled successfully and produced SHA-256 `175F51A04F601A432EF01107F67971A805A99601D1E2CCD2199DC5BC9C3BEF77`. |
| Codex capability proof | Codex CLI 0.144.0-alpha.4 registered marketplace `johnny-lifecycle-probe-market`, installed `johnny-lifecycle-probe@johnny-lifecycle-probe-market` version 1.0.0 and reported it installed/enabled. Installed manifest SHA-256 `57B378A1E86B9C6A323EB7C86B0A4731A466C16E28720E5644337E808E626AF5` and skill SHA-256 `710EB1AF1B830201B3B31EBDA0062788B74A72B7EBD2CA8791A9221E84E836BA` exactly matched the disposable source. |
| Removal proof | Exact `plugin remove` and `plugin marketplace remove` returned the same plugin/marketplace identity. Final structured lists contained neither identity, the exact installed path did not exist, and the disposable temporary source root was safely deleted. Existing installed plugins were not removed. |
| Isolation | No target-project path was supplied to any command; no target-project file/Git state, existing plugin, implementation worktree, branch, push, deployment or schedule was changed. No Secret/login or hidden configuration edit was used. |
| Routing correction | The toolchain and public CLI mechanism are verified, but Ticket 03 still contains no production Codex adapter. Treating the probe as source would be a false support claim. Ticket 05 now owns the finite adapter slice; Ticket 04 moves from external halt to dependency wait. |
| Ticket-05 lane | Closure `CLOSURE-LOCAL-INSTALL-T05-01` K1–K8; handoff `hnd_local_orchestration_install_05_20260809`; allocation `aln_local_orchestration_install_05_20260809`; receipt `rcpt_local_orchestration_install_05_20260809`; correlation `corr-local-orchestration-install-05-20260809`; authority `PRG-20260809-042` plus this owner-granted capability run. Exactly one new-ticket branch may be created in the existing sole implementation worktree; review corrections stay additive on that branch. |
| Ticket-04 gate | Inno Setup 6.7.3 is ready. Packaging remains `PLANNED / DEPENDENCY_WAIT` only until Ticket 05 is independently approved and integrated. |

## PRG-20260809-079 — Ticket 05 initial review requires CLI-contract correction

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED → REVIEW / VALIDATION_FAILED → TICKET_REPAIR` |
| References | Branch `codex/implementation-codex-cli-host-adapter-05`; implementation `0c2ab95`; handoff `39936fc`; closure `CLOSURE-LOCAL-INSTALL-T05-01`; review `dac99fd`; `CR-73..CR-79`; report `doc/reviews/local-orchestration-installer/05-codex-cli-host-adapter-code-review.md`; result `CHANGES_REQUESTED / TICKET_REPAIR` |

## PRG-20260809-080 — Ticket 05 corrected closure and same-lane handoff

| Field | Value |
| --- | --- |
| Router event | `TICKET_REPAIR_COMPLETED → CORRECTION_HANDOFF → IMPLEMENT / AUTO_CONTINUE` |
| References | Review `dac99fd`; closure `CLOSURE-LOCAL-INSTALL-T05-02`; handoff `hnd_local_orchestration_install_05_cr1_20260809`; task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; branch `codex/implementation-codex-cli-host-adapter-05`; allocation `aln_local_orchestration_install_05_20260809`; receipt `rcpt_local_orchestration_install_05_20260809` |

## PRG-20260809-081 — Ticket 05 correction review requires convergence

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED → CORRECTION_REVIEW / VALIDATION_FAILED → CONVERGENCE_REVIEW_REQUIRED` |
| References | Branch `codex/implementation-codex-cli-host-adapter-05`; implementations `c2ea3f8`, `3f6c41a`, `13d02de`; handoffs `09b4824`, `4c9525b`; review `593e33a`; `CR-80..CR-85`; report `doc/reviews/local-orchestration-installer/05-codex-cli-host-adapter-code-review.md`; result `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |

## PRG-20260810-082 — Ticket 05 convergence decomposition and Ticket 05A dispatch

| Field | Value |
| --- | --- |
| Router event | `CONVERGENCE_REVIEW_REQUIRED → TICKET_DECOMPOSITION → TICKET_DISPATCH_REQUIRED → IMPLEMENT / AUTO_CONTINUE` |
| References | Authority `PRG-20260809-042`; parent Ticket 05 `SUPERSEDED / CONVERGENCE_DECOMPOSED`; child ticket `05a-codex-cli-preflight-contract`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; handoff `hnd_local_orchestration_install_05a_20260810`; allocation `aln_local_orchestration_install_05a_20260810`; receipt `rcpt_local_orchestration_install_05a_20260810`; correlation `corr-local-orchestration-install-05a-20260810`; task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; branch `codex/implementation-codex-cli-preflight-05a` |

## PRG-20260810-084 - Ticket 05A independent review

| Field | Value |
| --- | --- |
| Router event | `REVIEW_HANDOFF -> CODE_REVIEW -> CHANGES_REQUESTED -> IMPLEMENT / AUTO_CONTINUE` |
| References | Baseline `d90b69e`; branch `codex/implementation-codex-cli-preflight-05a`; implementation `88f7aae`; handoff `67dc1db`; review `1cc4e99`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; `CR-86..CR-89`; result `CHANGES_REQUESTED` |

## PRG-20260810-085 - Ticket 05A single correction dispatch

| Field | Value |
| --- | --- |
| Router event | `CHANGES_REQUESTED -> CORRECTION_HANDOFF -> IMPLEMENT / AUTO_CONTINUE` |
| References | Review `1cc4e99`; `CR-86..CR-89`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; handoff `hnd_local_orchestration_install_05a_corr1_20260810`; allocation `aln_local_orchestration_install_05a_20260810`; receipt `rcpt_local_orchestration_install_05a_20260810`; correlation `corr-local-orchestration-install-05a-corr1-20260810`; branch HEAD `67dc1db` |

## PRG-20260810-087 - Ticket 05A correction review

| Field | Value |
| --- | --- |
| Router event | `CORRECTION_COMPLETED -> CODE_REVIEW -> CHANGES_REQUESTED -> CONVERGENCE_REVIEW_REQUIRED / WAIT_FOR_HUMAN` |
| References | Implementation `b6594b9`; handoff `59c3f96`; review `277a0d0`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; `CR-86..CR-89`; result `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |

## PRG-20260810-088 - Ticket 05A owner convergence override and final correction dispatch

| Field | Value |
| --- | --- |
| Router event | `CONVERGENCE_REVIEW_REQUIRED -> OWNER_SCOPED_OVERRIDE -> CORRECTION_HANDOFF -> IMPLEMENT / AUTO_CONTINUE` |
| References | Input `b6594b9` / `59c3f96`; dispatch `83e34c3`; handoff `hnd_local_orchestration_install_05a_corr2_owner_20260810`; allocation `aln_local_orchestration_install_05a_20260810`; receipt `rcpt_local_orchestration_install_05a_20260810`; correlation `corr-local-orchestration-install-05a-corr2-owner-20260810` |

## PRG-20260810-089 - Ticket 05A terminal review blocked

| Field | Value |
| --- | --- |
| Router event | `FINAL_CORRECTION_COMPLETED -> CODE_REVIEW -> VALIDATION_FAILED -> BLOCKED / SUPERSEDE_REQUIRED` |
| References | Control `83e34c3`; implementation `97ab31c`; handoff `4fc81a5`; review `ea372b7`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; `CR-90..CR-91`; result `BLOCKED / SUPERSEDE_REQUIRED` |

## PRG-20260810-090 - Ticket 05A evidence-only cleanup authorization

| Field | Value |
| --- | --- |
| Router event | `BLOCKED -> OWNER_SCOPED_OVERRIDE -> EVIDENCE_CLEANUP_HANDOFF -> IMPLEMENT / AUTO_CONTINUE` |
| References | Review `ea372b7`; handoff `hnd_local_orchestration_install_05a_evidence_cleanup_20260810`; allocation `aln_local_orchestration_install_05a_evidence_cleanup_20260810`; receipt `rcpt_local_orchestration_install_05a_evidence_cleanup_20260810`; correlation `corr-local-orchestration-install-05a-evidence-cleanup-20260810`; task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; branch `codex/implementation-codex-cli-preflight-05a`; HEAD `4fc81a5` |

## PRG-20260810-092 - Ticket 05A evidence repair approved

| Field | Value |
| --- | --- |
| Router event | `EVIDENCE_CLEANUP_COMPLETED -> CODE_REVIEW -> VALIDATION_PASSED -> APPROVED / READY_TO_MERGE` |
| References | Authority `9d3fd4d`; implementation `97ab31c`; repaired handoff `fb755268`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; `CR-90..CR-91`; result `APPROVED / READY_TO_MERGE` |

## PRG-20260810-093 - Ticket 05A guarded integration halted

| Field | Value |
| --- | --- |
| Router event | `REVIEW_APPROVED -> GUARDED_INTEGRATION_PREFLIGHT -> CONFLICT_DETECTED -> HALT / OWNER_RESOLUTION_REQUIRED` |
| References | Base `d90b69e`; control `d54c0bd`; branch `fb755268`; result `HALT / OWNER_RESOLUTION_REQUIRED` |

## PRG-20260810-083 - Ticket 05A Codex CLI contract and ownership preflight handoff

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED -> IMPLEMENTATION_COMPLETED -> REVIEW_HANDOFF` |
| References | Ticket `05a-codex-cli-preflight-contract`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; baseline `d90b69e`; authority `PRG-20260809-042`; handoff `hnd_local_orchestration_install_05a_20260810`; allocation `aln_local_orchestration_install_05a_20260810`; receipt `rcpt_local_orchestration_install_05a_20260810`; correlation `corr-local-orchestration-install-05a-20260810`; branch `codex/implementation-codex-cli-preflight-05a`; implementation `88f7aae`; docs handoff `67dc1db` |

## PRG-20260810-086 - Ticket 05A CR-86 to CR-89 correction handoff

| Field | Value |
| --- | --- |
| References | Review `1cc4e99`; handoff `hnd_local_orchestration_install_05a_corr1_20260810`; allocation `aln_local_orchestration_install_05a_20260810`; receipt `rcpt_local_orchestration_install_05a_20260810`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; branch `codex/implementation-codex-cli-preflight-05a`; implementation `b6594b9f9acf1cd2d905b0614ddce23db268510c`; docs handoff `59c3f96762d65cdc5e39f53cecffdea0428fbc16` |

## PRG-20260810-091 - Ticket 05A owner-overridden final correction handoff

| Field | Value |
| --- | --- |
| References | Dispatch `83e34c3`; review `277a0d0`; handoff `hnd_local_orchestration_install_05a_corr2_owner_20260810`; allocation `aln_local_orchestration_install_05a_20260810`; receipt `rcpt_local_orchestration_install_05a_20260810`; closure `CLOSURE-LOCAL-INSTALL-T05A-01`; branch `codex/implementation-codex-cli-preflight-05a`; implementation `97ab31c694db97363f61fa6f437b6decf22a1a41`; original handoff `4fc81a5`; evidence authority `9d3fd4d`; terminal review `ea372b7`; repaired handoff `fb755268` |

## PRG-20260810-094 - Ticket 05A integrated with ledger-preserving resolution

| Field | Value |
| --- | --- |
| Router event | `OWNER_RESOLUTION_GRANTED -> GUARDED_INTEGRATION -> VALIDATION_PASSED -> HANDOFF / AUTO_CONTINUE` |
| References | Merge `b22c6c4`; parents `5281739` / `fb755268`; implementation `97ab31c`; review `d54c0bd`; Ticket 05A `DONE / APPROVED / INTEGRATED` |

## PRG-20260810-095 - Ticket 05B transactional registration dispatch

| Field | Value |
| --- | --- |
| Router event | `OWNER_DISPATCH_GRANTED -> TICKET_SELECTED -> IMPLEMENTATION_HANDOFF -> IMPLEMENT / AUTO_CONTINUE` |
| References | Dependency `b22c6c4`; authority `PRG-20260809-042`; ticket `05b-codex-cli-transactional-registration`; closure `CLOSURE-LOCAL-INSTALL-T05B-01`; handoff `hnd_local_orchestration_install_05b_20260810`; allocation `aln_local_orchestration_install_05b_20260810`; receipt `rcpt_local_orchestration_install_05b_20260810`; correlation `corr-local-orchestration-install-05b-20260810`; task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; branch `codex/implementation-codex-cli-registration-05b` |

## PRG-20260810-097 - Ticket 05B initial review blocked on ticket design

| Field | Value |
| --- | --- |
| Router event | `IMPLEMENTATION_COMPLETED -> CODE_REVIEW -> VALIDATION_FAILED -> BLOCKED / TICKET_DEFECT` |
| References | Dispatch `f68d9d6`; implementation `5e919069`; handoff `ef1cf42`; review `f02704f`; `CR-92..CR-97`; result `BLOCKED / TICKET_DEFECT` |

## PRG-20260810-098 - Ticket 05B finite revision-02 refreeze

| Field | Value |
| --- | --- |
| Router event | `TICKET_DEFECT -> TICKET_REPAIR -> CLOSURE_REFROZEN -> TICKETS / WAIT_FOR_HUMAN` |
| References | Ticket `05b-codex-cli-transactional-registration`; closure `CLOSURE-LOCAL-INSTALL-T05B-02`; refreeze commit `a7dd4a4`; prior review `f02704f`; retained HEAD `ef1cf42`; continuation `WAIT_FOR_HUMAN` |

## PRG-20260810-099 - Ticket 05B revision-02 correction dispatch

| Field | Value |
| --- | --- |
| Router event | `OWNER_DISPATCH_CONFIRMED -> CORRECTION_HANDOFF -> IMPLEMENT / AUTO_CONTINUE` |
| References | Authority `PRG-20260809-042`; closure `CLOSURE-LOCAL-INSTALL-T05B-02`; refreeze `a7dd4a4`; review `f02704f`; handoff `hnd_local_orchestration_install_05b_corr1_r02_20260810`; allocation `aln_local_orchestration_install_05b_20260810`; receipt `rcpt_local_orchestration_install_05b_20260810`; correlation `corr-local-orchestration-install-05b-corr1-r02-20260810`; required HEAD `ef1cf42` |

## PRG-20260810-101 - Ticket 05B terminal revision-02 review

| Field | Value |
| --- | --- |
| Router event | `CORRECTION_COMPLETED -> CODE_REVIEW -> CHANGES_REQUESTED -> CONVERGENCE_REVIEW_REQUIRED` |
| References | Closure `CLOSURE-LOCAL-INSTALL-T05B-02`; implementation `1a26941176b4ce3c122c41644817e3429cb7c8a5`; handoff `ed74589c12072d5d70e168735e6ccc440c681ced`; review commit `24227ac`; report `doc/reviews/local-orchestration-installer/05b-codex-cli-transactional-registration-code-review.md`; `CR-98..CR-104` |
| Decision | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`; no automatic continuation |

## PRG-20260810-102 — staging-first convergence and Ticket 05S dispatch preparation

| Field | Value |
| --- | --- |
| Router event | `OWNER_REQUIREMENT_CONFIRMED → ARCHITECTURE / GRILL → SPEC_REVISION → TICKET_SELECTED → IMPLEMENTATION_HANDOFF` |
| Owner decision | Establish an isolated install/remove verification environment first; only after it is independently approved may the control plane refreeze 05B, 05C and Ticket 04. |
| Capability evidence | Windows 10 Pro reports a hypervisor, but `WindowsSandbox.exe` is absent; Hyper-V management is unavailable to the current control process; Docker is an inactive `desktop-linux` context. No provider is misreported as usable Windows package staging. |
| Selected first gate | Ticket `05s-codex-lifecycle-contract-staging`; closure `CLOSURE-LOCAL-INSTALL-T05S-01`; stateful test-owned child process and persisted filesystem oracle; no live Codex/target-project mutation. |
| Handoff identifiers | `hnd_local_orchestration_install_05s_20260810`; `aln_local_orchestration_install_05s_20260810`; `rcpt_local_orchestration_install_05s_20260810`; `corr-local-orchestration-install-05s-20260810`; task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; branch `codex/implementation-codex-lifecycle-staging-05s`. |
| Downstream boundary | 05B remains terminal blocked evidence and is not patched in this commit. 05C/04 remain dependency-waiting. Their acceptance closures will be revised only after 05S implementation, review and guarded integration. |

## PRG-20260810-104 — Ticket 05S initial review and revision-02 refreeze

| Field | Value |
| --- | --- |
| Router event | `IMPLEMENTATION_COMPLETED → ACTION_COMPLETED → REVIEW_HANDOFF → CHANGES_REQUESTED → TICKET_REFREEZE` |
| References | Control baseline `3047b4b`; implementation `18b99de`; docs-only handoff `2bed349`; implementation handoff record `PRG-20260810-103` on the submitted branch; review `doc/reviews/local-orchestration-installer/05s-codex-lifecycle-contract-staging-code-review.md`; findings `CR-105..CR-111`. |
| Independent green evidence | Valid ancestry/scope and clean submitted worktree. After a review-only topology workaround, focused `python -m unittest -v tests.test_codex_lifecycle_staging` passed `8/8`, full `python -m unittest discover -s tests -v` passed `180/180`, and strict mypy passed `88` files. Production source has zero diff. |
| Blocking evidence | A disposable exported checkout initially produced `13` focused provisioning errors and left `13` new staging roots because the tests assumed a fixed adjacent control worktree and validation occurred after `mkdtemp`. Runtime protocol probes showed the sandbox is not a `CodexCommandPort`, has no timeout, and emits non-official add/remove DTOs. Fresh-state probes returned success for plugin-without-marketplace, invalid semantic version and blank foreign record. Default `python -m unittest discover -v` discovered `0` tests. |
| Decision | `CHANGES_REQUESTED`. Refrozen closure `CLOSURE-LOCAL-INSTALL-T05S-02` adds `C1..C7/R01..R12`. One additive correction is authorized on the same task, worktree, branch, allocation and receipt; initial commits remain immutable. |
| Correction identity | Handoff `hnd_local_orchestration_install_05s_20260810`; allocation `aln_local_orchestration_install_05s_20260810`; receipt `rcpt_local_orchestration_install_05s_20260810`; correction correlation `corr-local-orchestration-install-05s-r02-20260810`; branch `codex/implementation-codex-lifecycle-staging-05s`. |
| Prohibited continuation | No new branch/worktree, production-source change, 05B/05C/04 implementation, integration, live Codex mutation, target-project write, push, release or deployment. |

## PRG-20260811-105 — Ticket 05S terminal revision-02 review

| Field | Value |
| --- | --- |
| Router event | `CORRECTION_COMPLETED → TERMINAL_CODE_REVIEW → CHANGES_REQUESTED → CONVERGENCE_REVIEW_REQUIRED` |
| References | Control baseline `3685f0e`; implementation corrections `ca5754d6a4f8ad271f57b3312e5f1c7171169f0c` and `832b1dcf1a0607059d9ffbb854740ce238ee949c`; docs-only handoff `ccb55bd75c2c24b658828a554dd441fb54733752`; closure `CLOSURE-LOCAL-INSTALL-T05S-02`; findings `CR-112..CR-117` |
| Passing evidence | Valid ancestry and authorized four-file implementation scope; clean implementation worktree; focused `20/20`; strict mypy `88` files; in-memory compile `4` files; production source unchanged; `git diff --check` clean; terminal runs left zero staging roots. |
| Blocking replay | From a disposable export with zero initial cache and staging roots, exact `python -m unittest discover -s tests -v` ran 192 tests and failed R12 after creating 24 `__pycache__` directories. The submitted `192`-pass/zero-cache claim is not replayable as written. |
| Blocking probes | A foreign plugin without any physical payload is emitted as `installed=true` with exit zero. Version validation accepts invalid `01.0.0` and rejects valid prerelease/build SemVer. R01 and R06 do not execute the frozen path and real process-exception matrices. The branch handoff also collides with existing identifier `PRG-20260810-104`. |
| Decision | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`; no second automatic correction, new branch/worktree, merge, downstream refreeze or dispatch. Submitted commits remain immutable rejected evidence. |

## PRG-20260811-106 — Ticket 05S decomposition and environment-first selection

| Field | Value |
| --- | --- |
| Router event | `CONVERGENCE_REVIEW_REQUIRED → OWNER_DECOMPOSITION → TICKETS → WAIT_FOR_DISPATCH` |
| Owner direction | Split the work into small tickets, establish the environment first, separate acceptance responsibility and prevent another automatic correction loop. |
| Superseded evidence | Combined 05S and commits `ca5754d`, `832b1dc`, `ccb55bd` remain immutable rejected evidence; none may be copied, cherry-picked, merged or used as approval. |
| New sequence | `05S1 disposable environment core → 05S2 bounded child-process runner → 05S3 Codex protocol fixture → 05S4 Codex lifecycle oracle`; 05B/05C refreeze waits for 05S4; Ticket 04 retains the separate real Windows package-staging gate. |
| Responsibility boundary | Each implementation owner changes only its ticket scope. The independent control-plane reviewer owns acceptance and cannot patch implementation. A blocking review stops at `CONVERGENCE_REVIEW_REQUIRED`; no automatic correction, new branch or replacement worktree. |
| Current continuation | 05S1 is `PLANNED / SELECTED_NEXT / NOT_DISPATCHED`. No allocation, receipt, implementation branch, task message, merge, live host mutation, target-project write, push, release or deployment occurred. |

## PRG-20260811-107 — Ticket 05S1 environment-core handoff

| Field | Value |
| --- | --- |
| Router event | `TICKETS → TICKET_DISPATCH_REQUIRED → IMPLEMENTATION_DISPATCH_CONFIRMED / IMPLEMENT` |
| Ticket / closure | `05s1-disposable-environment-core`; `CLOSURE-LOCAL-INSTALL-T05S1-01`; E1–E4/T1–T4 |
| Binding identifiers | Handoff `hnd_local_orchestration_install_05s1_20260811`; allocation `aln_local_orchestration_install_05s1_20260811`; receipt `rcpt_local_orchestration_install_05s1_20260811`; correlation `corr-local-orchestration-install-05s1-20260811`; question `q-local-orchestration-install-05s1-20260811`; owner task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Baseline | Ticket-doc commit `3f685a9`; this record's commit is the required handoff-doc commit and must be read back before implementation. |
| Scope | Four test-support Python files only. Provision/teardown and environment overlay; no subprocess, Codex DTO/state, installer, target-project, live host or historical-source reuse. |
| Branch/worktree | Reuse the sole clean implementation worktree and create only `codex/implementation-disposable-environment-core-05s1` from the exact handoff baseline. No new worktree. |
| Return / loop rule | One implementation commit plus one docs-only handoff. Reviewer batches one independent review; blocking findings stop without automatic correction or replacement branch. 05S2–05S4 remain dependency-waiting. |

## PRG-20260811-108 - Ticket 05S1 disposable environment core implementation handoff

| Field | Value |
| --- | --- |
| Router event | `ACTION_COMPLETED -> IMPLEMENTATION_COMPLETED -> REVIEW_HANDOFF` |
| Ticket / closure | `05s1-disposable-environment-core`; `CLOSURE-LOCAL-INSTALL-T05S1-01`; E1-E4 / T1-T4 |
| Authority and binding | Authority `PRG-20260809-042`; decomposition `PRG-20260811-106`; dispatch `PRG-20260811-107`; handoff `hnd_local_orchestration_install_05s1_20260811`; allocation `aln_local_orchestration_install_05s1_20260811`; receipt `rcpt_local_orchestration_install_05s1_20260811`; correlation `corr-local-orchestration-install-05s1-20260811`; question `q-local-orchestration-install-05s1-20260811` |
| Baseline and owner | Required handoff baseline `f88e10f73f9014fb276d99974eaf1a2074c9a7d0`; ticket-doc `3f685a9`; implementation task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; branch `codex/implementation-disposable-environment-core-05s1`; implementation `e0898cdca76c360713bef35b1848c0b8b8bd3681` |
| Implementation scope | Only `tests/staging/environment_core/__init__.py`, `contracts.py`, `environment.py`, and `tests/test_disposable_environment_core.py`; no production-library change, subprocess, CLI/Codex state, target-project access, host mutation, Git fixture, or historical-source reuse. |
| First-red evidence | Before the four staging modules existed, exact focused command failed T1-T4 with `ModuleNotFoundError: No module named 'tests.staging'`; this is the recorded first-red boundary for the new environment-only surface. |
| Green behavior | T1 provisions distinct direct OS-temp roots and rejects malformed/constructed/replayed owners before effects. T2 returns only the six fixed overlay keys and preserves parent environment values. T3 blocks missing/mismatched marker, reparse and child-escape deletion, then permits exact teardown and finite replay. T4 clears only owned faulted roots and preserves an unrelated sibling. |
| Reparse evidence | The execution account's physical symbolic-link probe returned `WinError 1314`; T3 therefore uses a typed `Path.is_symlink` test probe to exercise the same production refusal branch. The production path still checks actual reparse/symlink state before deletion; this limitation is disclosed for independent review. |
| Verification | `python -B -m unittest tests.test_disposable_environment_core -v`: 4/4 passed. `python -B -m unittest discover -s tests -v`: 176/176 passed. `python -B -m mypy --strict --explicit-package-bases --no-incremental --cache-dir <validated OS-temp>`: 86 source files, success; temporary cache removed and read back absent. In-memory `compile`: 4/4 files. Forbidden-source sentinel and `git diff --check`: passed. |
| Scope/state readback | Four implementation files, 478 nonblank lines total; generated repository caches removed after verification; owned `johnny-stage-env-*` root residue: 0; no merge, push, deployment, review, integration, downstream dispatch, or schedule action. |
| Review handoff | Independent control-plane review is required. This implementation owner makes no approval or integration decision. |
