# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `05`；Owner 2026-10-18 本次 12 項指示 |
| 工作基準 | `a1cb6c13adbeb52a4117991727dcc3d4af6d2a33`；分支 `codex/skill-improvement-checklist` |
| 主線 | 先對照、優先 02→04→05→06→07，再處理餘項與整合回放 |
| 負責 | Root 理解需求、衝突與派工；票級實作者依有效能力 Profile；獨立審閱另席 |
| 範圍 | Johnny skill、模板、現有 Router/Runner 入口與驗證；不改 Vita360 產品，不部署、不推送 |

本表只保存進度與證據索引。需求權限沿既有 PRD／CHG／SPEC，單票授權沿既有 ticket；
Router、Reviewer、文件索引與結案規則仍各有唯一正文。`[x]` 只表示該項實作、必要驗證
與獨審均完成。`NOT_VERIFIED`、文件提案或未執行一律維持 `[ ]`。每次更新此 leaf 與
`doc/README.md` 連結，不複製整份需求進票。對真實專案的回放使用隔離 fixture；
通用 skill 不放 Vita360 路徑、SHA、票號或固定模型名稱。

| 項目 | 狀態 | 作者／修改位置 | 驗證方式與目前結果 | 獨審結論 | 剩餘問題 |
| --- | --- | --- | --- | --- | --- |
| [ ] 01 主線與單票 | `PROJECTION_LOCAL_INTEGRATED / SOURCE_CLOSURE_OPEN` | Luna 改 `mainline_projection.py`、Context reference 與測試；`2fa4ca6f`，獨審見 `doc/reviews/workflow-governance/29-mainline-ticket-projection-code-review.md` | 13 tests、strict mypy 綠；Reviewer 對誤判結案及相依提前接續作兩次反向突變紅→綠 | `APPROVED_SLICE` | 可信主線來源、完整目標／交接持久化及正式結案准入尚未證明 |
| [ ] 02 已核准工作接續 | `OWNER_WAIT_LOCAL_INTEGRATED / B_CONTINUATION_OPEN` | Luna 候選 `e0bbe9e5` 改 Router／Profile／契約／測試／reference，Root 控制面分出 Ticket 30；`af24945f`，獨審見 `doc/reviews/workflow-governance/24-independent-admitted-ticket-continuation-code-review.md` | 81 tests／237 subtests、strict mypy 綠；Reviewer ticket 身分反向突變紅→綠，另一席確認六檔落地 blob 完全相同 | `APPROVED_A_SLICE` | 獨立 B 的 live 准入、相依與主線未完成證據仍缺；Ticket 30 未派工，不可勾選 |
| [ ] 03 派工完整最小 | `TEMPLATE_LOCAL_INTEGRATED / HOST_ADMISSION_OPEN` | Luna 候選 `e9bdc978` 改 ticket template／單一驗證檔；`cfa46704`，獨審見 `doc/reviews/workflow-governance/28-minimal-complete-dispatch-ticket-code-review.md` | 20 tests 綠；Expected 註解／fence／縮排碼與 stop 錯節四種獨立突變皆紅→綠；固定填票情境使用實際模板槽 | `APPROVED_TEMPLATE_SLICE` | Host dispatch preflight 尚未驗證票面完整性；不能宣稱實作者已被阻止猜 Expected |
| [x] 04 TEST → A → B | `COMPLETE_LOCAL / NO_PUSH` | Luna：Ticket 25 規則 `970b99cc`、Ticket 33 產品 A `ac369235`、Ticket 34 測試 B `b4a7dbe6`；獨審見 `doc/reviews/workflow-governance/33-shared-context-service-seam-code-review.md` 與 `34-shared-context-test-seam-transfer-code-review.md` | A 先在候選公開入口通過；Reviewer 改壞新 service 的 sealed read／writer role，公開 Router 格轉紅→綠。B 五格 contract-only 測試搬到聚焦檔、六格公開入口保留；Reviewer 改壞 service 與 contract guard，各自轉紅→綠；整合分支 61 tests／217 subtests、strict mypy 綠，五檔 Git blob 與各受審候選相同 | `APPROVED_A + APPROVED_B` | 此為本機 Johnny Router 能力回放；未推送／發布，不代表 Vita360 產品已拆分 |
| [ ] 05 候選來源與 Expected | `CONTRACT_LOCAL_INTEGRATED / HOST_GAP` | Luna 改既有 `TestBinding`／`ReviewAdmissionGate`；`beff0050`，審閱見 `doc/reviews/controlled-verification/cve-d10-candidate-source-observation-code-review.md` | 19 tests／50 subtests 綠、`mypy --strict` 綠、Expected 反向突變紅→綠；型別契約拒絕舊基準載入與 Expected 漂移 | `APPROVED_CONTRACT_ONLY` | 尚無合格 Host adapter 觀察實際載入來源及核准 Expected 的來源；不得把 port 自報當實測 |
| [ ] 06 共用樹覆蓋 | `WORKER_CLAIM_LOCAL_INTEGRATED / PREWRITE_GAP` | Luna 改既有 worker ledger／測試；`9cedb55f`，審閱見 `doc/reviews/workflow-governance/26-active-writer-worktree-branch-uniqueness-code-review.md` | 48 tests／77 subtests 綠；active worktree／branch 衝突轉紅再回綠；任意同步寫入的 HEAD／index／工作副本驗證仍 `NOT_VERIFIED` | `APPROVED_SLICE` | 缺受控 prewrite/commit 效應入口；不可把派工互斥說成整個工作樹防回退已完成 |
| [ ] 07 完成與證據 | `PARENT_FINDING_PROJECTION_LOCAL_INTEGRATED / FORMAL_CLOSURE_GAP` | Luna 改 `ticket_status_pipeline.py`／`ticket_status_template.py` 與測試；Ticket 27 `3196712d`、Ticket 35 `215a599f`；獨審見 `doc/reviews/workflow-governance/27-evidence-linked-ticket-status-projection-code-review.md` 與 `35-parent-finding-status-closure-code-review.md` | 最終 121 tests／205 subtests、strict mypy 綠；必要子票、OPEN Finding 與重複父票 ID 三項獨審反向突變紅→綠；可選未完成與無關票仍可顯示 | `APPROVED_PROJECTION_ONLY` | 證據來源真偽及正式 Router／Review 結案准入仍未實作；投影不得自行授權結票 |
| [ ] 08 測試依賴／退役 | `PURE_INVENTORY_LOCAL_INTEGRATED / HOST_CI_GAP` | Luna 改單責 AST inventory 與測試；`2a19406d`，獨審見 `doc/reviews/workflow-governance/32-test-consumer-inventory-code-review.md`；既有 `implementation-tdd.md` 保留退役條款 | 11 tests、strict mypy 綠；Reviewer 對漏掉 child-module 消費者拒收首版，修正後反向突變紅→綠；真實 CI/Host source 讀入、入口切換及退役准入 `NOT_VERIFIED` | `APPROVED_SLICE` | 解析器只處理呼叫端供給的來源；沒有可信 caller 與退役 effect gate，不得以空 inventory 判安全刪除 |
| [ ] 09 窄修窄審 | `CORRECTION_REPLAY_PARTIAL / GAP` | Root；既有 `CodeReview.md` §4–5、`implementation-authority.md`；Ticket 35 實作者原票修正、原 Sol reviewer 複驗，見 `doc/reviews/workflow-governance/35-parent-finding-status-closure-code-review.md` | Ticket 35 首審重複父票 ID finding → 原票 additive correction → 原 reviewer 新路徑反向突變紅→綠；Root 找到 `ticket_status_publish.publish` 真消費者，整合分支 pipeline／renderer／publisher 共 126 tests／205 subtests 綠；無關檔案未重審，舊必需子票／Finding PASS 證據有條件沿用 | `APPROVED_CASE_ONLY` | 尚需固定可重跑的影響／消費者判定與 finding↔Closure 錯標負例；一個真實回合不足以證明通用行為可強制 |
| [ ] 10 成本／外部呼叫／回報 | `MODEL_PROFILE_LOCAL_INTEGRATED / PAID_TEST_REPORTING_GAP` | Luna 改 `model-role-routing.md`、`delivery-profile.md` 與既有 policy/executor tests；`68a10057`，審閱見 `doc/reviews/workflow-governance/31-semantic-model-profile-boundary-code-review.md` | 36 tests／74 subtests 綠；普通開票低／高 profile 反向突變紅→綠，同步 readback 語義修正；本機付費服務攔截及固定回報欄位 `NOT_VERIFIED` | `APPROVED_SLICE` | 通用模型選擇不凍結名稱，但真實 Host qualification、付費 API 測試隔離與功能／腳本拆分回報仍缺 |
| [ ] 11 去重與衝突 | `NOT_STARTED` | Root；現有 Router、派工模板、Runner、Reviewer、結案入口 | 待 01–10 差異落定後做單一來源／重複責任檢查 | `NOT_REVIEWED` | 不建第二套流程或審批關卡 |
| [ ] 12 回放與獨審 | `NOT_STARTED` | Root；沿既有 tests／review 位置 | 01–10 正反案例待建立；自動／固定情境分別記錄限制 | `NOT_REVIEWED` | 錯誤拒絕與合法通過都必須證明 |

## 本輪窄查來源與下一步

- 現行主線 continuation：`Workflow.md` §0.1、`router-control.md` Continuation；單票與
  完成證據：`specification-ticketing.md`、`CodeReview.md`、`review_admission.py`。
- 現行 worktree 與 correction：`implementation-authority.md`；現行測試品質：
  `implementation-tdd.md`、`review-checks.md`。它們是可重用基礎，尚未證明本表情境。
- 04 的 TEST→A→B 本機閉包已完成；05／06／07 仍有 Host／正式結案外層缺口，不得誤勾。
  02 的初稿拒收，仍須修正真正 Owner effect／相依接續，不得重命名 dispatch wait 冒充。
  下一步依既有需求與 ticket 補足 02／05／06／07 的外層效應與驗收，再接續其他項目。

更新規則：每項補作者、精確改動位置、執行命令／退出碼／輸出摘要、候選 commit、
獨立審閱結論與未解 finding。只有從正式候選與可信執行紀錄取得證據，才可勾選。
