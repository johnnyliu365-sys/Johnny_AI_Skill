# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `19`；Owner 2026-10-18 本次 12 項指示、十種失敗情境、通用虛構情境、既有功能沿原 PRD 修訂及兩份 SPEC 限縮修正授權 |
| 工作基準 | `a1cb6c13adbeb52a4117991727dcc3d4af6d2a33`；分支 `codex/skill-improvement-checklist` |
| 主線 | 先對照、優先 02→04→05→06→07，再處理餘項與整合回放 |
| 負責 | Root 理解需求、衝突與派工；票級實作者依有效能力 Profile；獨立審閱另席 |
| 範圍 | 僅 Johnny skill、模板、現有 Router/Runner 入口與驗證；不改任何 target 產品，不部署、不推送 |

本表只保存進度與證據索引。需求權限沿既有 PRD／CHG／SPEC，單票授權沿既有 ticket；
Router、Reviewer、文件索引與結案規則仍各有唯一正文。`[x]` 只表示該項實作、必要驗證
與獨審均完成。`NOT_VERIFIED`、文件提案或未執行一律維持 `[ ]`。每次更新此 leaf 與
`doc/README.md` 連結，不複製整份需求進票。對真實專案的回放使用隔離 fixture；
通用 skill 不放特定 target 的路徑、SHA、票號或固定模型名稱；回放案例只用虛構通用情境。

| 項目 | 狀態 | 作者／修改位置 | 驗證方式與目前結果 | 獨審結論 | 剩餘問題 |
| --- | --- | --- | --- | --- | --- |
| [ ] 01 主線與單票 | `PROJECTION_LOCAL_INTEGRATED / SOURCE_CLOSURE_OPEN` | Luna 改 `mainline_projection.py`、Context reference 與測試；`2fa4ca6f`，獨審見 `doc/reviews/workflow-governance/29-mainline-ticket-projection-code-review.md` | 13 tests、strict mypy 綠；Reviewer 對誤判結案及相依提前接續作兩次反向突變紅→綠 | `APPROVED_SLICE` | 可信主線來源、完整目標／交接持久化及正式結案准入尚未證明 |
| [ ] 02 已核准工作接續 | `OWNER_WAIT_LOCAL_INTEGRATED / B_CONTINUATION_OPEN` | Luna 候選 `e0bbe9e5` 改 Router／Profile／契約／測試／reference，Root 控制面分出 Ticket 30；`af24945f`；Ticket 30 票面收斂 `7e2dae94`。獨審見 Ticket 24 review 與 Ticket 30 leaf 末節 | 81 tests／237 subtests、strict mypy 綠；Reviewer ticket 身分反向突變紅→綠。Ticket 30 初稿因偽 Grant／硬編路徑與 grammar 被拒，同票撤回後 44 template tests、獨立票面複驗 PASS；現有 projection 仍只有 caller-built metadata，無可信 target-versioned 主線來源與逐票 B grant/readback | `APPROVED_A_SLICE / TICKET_30_DOCS_REVIEWED_ONLY` | 獨立 B 的 live 准入、相依與主線未完成證據仍缺；Ticket 30 仍不可派工，不能把 projection 當 authority |
| [ ] 03 派工完整最小 | `TEMPLATE_AND_SCAFFOLD_LOCAL_INTEGRATED / HOST_ADMISSION_OPEN` | Luna 候選 `e9bdc978`、`3557bc20` 與 Ticket 40 `91ee17c3` 改本庫 ticket template、出貨 scaffold 與同一驗證檔；獨審見 `doc/reviews/workflow-governance/28-minimal-complete-dispatch-ticket-code-review.md`、`38-reuse-and-responsibility-dispatch-contract-code-review.md`、`40-scaffold-ticket-template-parity-code-review.md` | Ticket 40：44 tests 綠；八個 scaffold 反向突變與 reviewer 另兩個遮蔽突變紅→綠；受控 gate `INTEGRATED` `5776139a`，兩檔 Git blob 等於受審候選 | `APPROVED_TEMPLATE_SLICES` | Host dispatch preflight 尚未驗證填票完整性；文字模板不能阻止實作者猜 Expected，也不能自動識別檔內耦合 |
| [x] 04 TEST → A → B | `COMPLETE_LOCAL / NO_PUSH` | Luna：Ticket 25 規則 `970b99cc`、Ticket 33 產品 A `ac369235`、Ticket 34 測試 B `b4a7dbe6`；獨審見 `doc/reviews/workflow-governance/33-shared-context-service-seam-code-review.md` 與 `34-shared-context-test-seam-transfer-code-review.md` | A 先在候選公開入口通過；Reviewer 改壞新 service 的 sealed read／writer role，公開 Router 格轉紅→綠。B 五格 contract-only 測試搬到聚焦檔、六格公開入口保留；Reviewer 改壞 service 與 contract guard，各自轉紅→綠；整合分支 61 tests／217 subtests、strict mypy 綠，五檔 Git blob 與各受審候選相同 | `APPROVED_A + APPROVED_B` | 此為本機 Johnny Router 能力回放；未推送／發布，不代表任何 target 產品已拆分 |
| [ ] 05 候選來源與 Expected | `CONTRACT_LOCAL_INTEGRATED / HOST_GAP` | Luna 改既有 `TestBinding`／`ReviewAdmissionGate`；`beff0050`，審閱見 `doc/reviews/controlled-verification/cve-d10-candidate-source-observation-code-review.md` | 19 tests／50 subtests 綠、`mypy --strict` 綠、Expected 反向突變紅→綠；型別契約拒絕舊基準載入與 Expected 漂移 | `APPROVED_CONTRACT_ONLY` | 尚無合格 Host adapter 觀察實際載入來源及核准 Expected 的來源；不得把 port 自報當實測 |
| [ ] 06 共用樹覆蓋 | `WORKER_CLAIM_LOCAL_INTEGRATED / PREWRITE_GAP` | Luna 改既有 worker ledger／測試；`9cedb55f`，審閱見 `doc/reviews/workflow-governance/26-active-writer-worktree-branch-uniqueness-code-review.md` | 48 tests／77 subtests 綠；active worktree／branch 衝突轉紅再回綠；任意同步寫入的 HEAD／index／工作副本驗證仍 `NOT_VERIFIED` | `APPROVED_SLICE` | 缺受控 prewrite/commit 效應入口；不可把派工互斥說成整個工作樹防回退已完成 |
| [ ] 07 完成與證據 | `PARENT_FINDING_PROJECTION_LOCAL_INTEGRATED / FORMAL_CLOSURE_GAP` | Luna 改 `ticket_status_pipeline.py`／`ticket_status_template.py` 與測試；Ticket 27 `3196712d`、Ticket 35 `215a599f`；獨審見 `doc/reviews/workflow-governance/27-evidence-linked-ticket-status-projection-code-review.md` 與 `35-parent-finding-status-closure-code-review.md` | 最終 121 tests／205 subtests、strict mypy 綠；必要子票、OPEN Finding 與重複父票 ID 三項獨審反向突變紅→綠；可選未完成與無關票仍可顯示 | `APPROVED_PROJECTION_ONLY` | 證據來源真偽及正式 Router／Review 結案准入仍未實作；投影不得自行授權結票 |
| [ ] 08 測試依賴／退役 | `GIT_SOURCE_AND_SUITE_SLICES_LOCAL_INTEGRATED / CI_RETIREMENT_GAP` | Luna：Ticket 32 純 AST inventory `2a19406d`、Ticket 36 釘選 Git 唯讀 adapter `e1ca2d4b`、Ticket 39 literal SUITES 消費者 `e9177f80`；獨審見 `doc/reviews/workflow-governance/32-test-consumer-inventory-code-review.md`、`36-git-pinned-test-source-inventory-code-review.md` 與 `39-literal-suite-consumer-inventory-code-review.md` | Ticket 39 初審找出未知字串與 subscript mutation 兩項假空圖；同票修正後 32 tests／7 subtests、strict mypy 綠，巢狀索引反向突變紅→綠；真 CI 命令仍未載入 | `APPROVED_INVENTORY_SLICES` | 真 CI 命令仍由 caller 供給；入口切換、前置紅燈後的實際消費者與退役 effect gate `NOT_VERIFIED`，空 inventory 不授權刪除 |
| [ ] 09 窄修窄審 | `CORRECTION_REPLAY_PARTIAL / GAP` | Root；既有 `CodeReview.md` §4–5、`implementation-authority.md`；Ticket 35 實作者原票修正、原 Sol reviewer 複驗，見 `doc/reviews/workflow-governance/35-parent-finding-status-closure-code-review.md` | Ticket 35 首審重複父票 ID finding → 原票 additive correction → 原 reviewer 新路徑反向突變紅→綠；Root 找到 `ticket_status_publish.publish` 真消費者，整合分支 pipeline／renderer／publisher 共 126 tests／205 subtests 綠；無關檔案未重審，舊必需子票／Finding PASS 證據有條件沿用 | `APPROVED_CASE_ONLY` | 尚需固定可重跑的影響／消費者判定與 finding↔Closure 錯標負例；一個真實回合不足以證明通用行為可強制 |
| [ ] 10 成本／外部呼叫／回報 | `MODEL_PROFILE_LOCAL_INTEGRATED / PAID_TEST_REPORTING_GAP` | Luna 改 `model-role-routing.md`、`delivery-profile.md` 與既有 policy/executor tests；`68a10057`，審閱見 `doc/reviews/workflow-governance/31-semantic-model-profile-boundary-code-review.md` | 36 tests／74 subtests 綠；普通開票低／高 profile 反向突變紅→綠，同步 readback 語義修正；本機付費服務攔截及固定回報欄位 `NOT_VERIFIED` | `APPROVED_SLICE` | 通用模型選擇不凍結名稱，但真實 Host qualification、付費 API 測試隔離與功能／腳本拆分回報仍缺 |
| [ ] 11 去重與衝突 | `WPR_AND_TEMPLATE_SLICES_LOCAL_INTEGRATED / CONSISTENCY_OPEN` | Luna 改既有 `implementation-tdd.md` 與 policy pin/test；Ticket 37 `2f1c29cb`。Ticket 38 `3557bc20` 補既有模板；Ticket 40 `91ee17c3` 補出貨 scaffold，未造平行框架；獨審見對應 `doc/reviews/workflow-governance/37-retired-wpr-commit-conflict-code-review.md`、`38-reuse-and-responsibility-dispatch-contract-code-review.md`、`40-scaffold-ticket-template-parity-code-review.md` | WPR 衝突 54 tests／202 subtests、兩項反向突變紅→綠；Ticket 40 scaffold 44 tests、八項內建及兩項 reviewer 反向突變紅→綠 | `APPROVED_SLICES` | 已核准 AC17 仍要求 PRD／CHG 一對一；新身分模型與主線／Host 准入仍只是未生效 SPEC 提案；需精確核准與遷移，並核對其餘入口衝突 |
| [ ] 12 回放與獨審 | `NOT_STARTED` | Root；沿既有 tests／review 位置 | 01–10 正反案例待建立；自動／固定情境分別記錄限制 | `NOT_REVIEWED` | 錯誤拒絕與合法通過都必須證明 |

## 本輪窄查來源與下一步

- 現行主線 continuation：`Workflow.md` §0.1、`router-control.md` Continuation；單票與
  完成證據：`specification-ticketing.md`、`CodeReview.md`、`review_admission.py`。
- 現行 worktree 與 correction：`implementation-authority.md`；現行測試品質：
  `implementation-tdd.md`、`review-checks.md`。它們是可重用基礎，尚未證明本表情境。
- 04 的 TEST→A→B 本機閉包已完成；05／06／07 仍有 Host／正式結案外層缺口，不得誤勾。
- 原有功能的修正、返工、補測與延伸不得新建重複 PRD；沿原需求身分修訂並保留核准與版本關聯。原有 `PRD-20260815-022` 和 `PRD-20260805-009` leaf 現記錄**已獨審的設計基準、runtime 待生效**，前者含 AC-17 身分替代摘要；沒有另建 PRD。現行 runtime 的 `adaptive-project-orchestration.md` revision05 AC-17、`requirement-lineage.md` 與 validator 仍要求一對一。須完成相容性遷移、Host 能力及測試收斂，不能把設計基準冒充執行中的閘門。
- 本輪沿**原 PRD／原 SPEC**完成兩份限定修正：AC-17 受審 `4531d00f`／blob `9c88d20e`，治理 AC9–11 受審 `8eae1af4`／blob `6fd8c309`；Ticket 41 精確 blob replay 經 document mutation gate 本地整合於 `76d1f942`，獨審與 83 tests／242 subtests 見 `doc/reviews/workflow-governance/41-bounded-spec-correction-integration-code-review.md`。Owner 本輪授權與獨審使其成為**設計基準**，不用重問同一 SPEC；現行一對一 validator、Ticket 30 的缺口、實作 Grant、Host 硬性准入與正式結案 effect 仍未完成。出貨 scaffold 的窄修不能代替外層入口。
- Ticket 41 同票修正了 SPEC 本文仍稱「獨審待完成」的狀態矛盾：受審設計內容不變，狀態綁定候選 `3856557c`（AC-17 獨審 PASS；治理同 blob 獨審 PASS），從控制基準 `04686524` replay 後由文件閘門整合於 `cca2db71`。現行兩份 SPEC blob 分別為 `ffb5304e`／`4323863f`；83 tests／242 subtests 通過。這不關閉 Host/Grant/runtime 缺口，也不解除 Ticket 41 的 `CLEANUP_BLOCKED`。
- 程式與測試腳本禁止按票堆疊成混合責任巨石。現有 `johnny-boundary` 的 `create` 預設拒絕、Git diff 比對與 `TEST → A → B` 已提供部分硬性保護；它們**不會**判斷檔案內部耦合。剩餘缺口是對真實候選的重用／新增責任／成長與相依結構證據的正式拒收入口；不得只靠文字、行數上限或新增平行 Gate 宣稱完成。
- 窄查 `library/`、`tests/` 的 Python 檔案：`tests/test_workflow_router.py` 約 3561 行且含 Router、Context telemetry、route instruction、Agent Context lease 四組測試類；`library/workflow_router/contracts.py` 約 1734 行含多個領域契約。這是結構審查觸發訊號，**不是**自動拆檔、刪測試或判定全部違規的證據；後續只能隨受影響能力做 TEST→A→B 承接。
- 本地整合分支對 01～10 已改動的 13 個相關測試檔作一次合併回歸：`330 passed, 568 subtests passed`；8 項 pytest collection warnings 是匯入的 `Test*` 型別非測試類別，沒有失敗。這不替代各票獨審或未合格 Host effect。
- 本輪 Ticket 40 與兩份尚未生效的 SPEC 提案後再驗證：`python -m pytest tests/test_plugin_payload_boundary.py tests/test_ticket_template_contract.py tests/test_workflow_requirement_lineage.py -q` 為 `96 passed, 223 subtests passed`；主線、Review、依賴與工作樹八檔聚焦回歸為 `177 passed, 226 subtests passed`。後者 6 個 pytest collection warnings 是匯入的 `Test*` 型別，不是失敗；這些綠燈不能代替 Host 派工、可信載入來源或正式結案 effect 證據。
  02 的初稿拒收，仍須修正真正 Owner effect／相依接續，不得重命名 dispatch wait 冒充。
  下一步依既有需求與 ticket 補足 02／05／06／07 的外層效應與驗收，再接續其他項目。

更新規則：每項補作者、精確改動位置、執行命令／退出碼／輸出摘要、候選 commit、
獨立審閱結論與未解 finding。只有從正式候選與可信執行紀錄取得證據，才可勾選。
