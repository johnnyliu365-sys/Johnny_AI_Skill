# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `02`；Owner 2026-10-18 本次 12 項指示 |
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
| [ ] 04 TEST → A → B | `SLICE_LOCAL_INTEGRATED / A_B_OPEN` | Luna 改 `implementation-tdd.md`、ticket template、profile pin 與既有 service 測試；`970b99cc`，審閱見 `doc/reviews/workflow-governance/25-refactor-test-seam-transfer-code-review.md` | 66 tests／225 subtests 綠；Reviewer 對 service 行為作反向突變紅→綠；並非實際 Router→service 產品拆分 | `APPROVED_SLICE` | 真正 A 候選版行為及其 B 依賴尚未回放；不可把腳本／規則改動寫成產品拆分完成 |
| [ ] 05 候選來源與 Expected | `CONTRACT_LOCAL_INTEGRATED / HOST_GAP` | Luna 改既有 `TestBinding`／`ReviewAdmissionGate`；`beff0050`，審閱見 `doc/reviews/controlled-verification/cve-d10-candidate-source-observation-code-review.md` | 19 tests／50 subtests 綠、`mypy --strict` 綠、Expected 反向突變紅→綠；型別契約拒絕舊基準載入與 Expected 漂移 | `APPROVED_CONTRACT_ONLY` | 尚無合格 Host adapter 觀察實際載入來源及核准 Expected 的來源；不得把 port 自報當實測 |
| [ ] 06 共用樹覆蓋 | `WORKER_CLAIM_LOCAL_INTEGRATED / PREWRITE_GAP` | Luna 改既有 worker ledger／測試；`9cedb55f`，審閱見 `doc/reviews/workflow-governance/26-active-writer-worktree-branch-uniqueness-code-review.md` | 48 tests／77 subtests 綠；active worktree／branch 衝突轉紅再回綠；任意同步寫入的 HEAD／index／工作副本驗證仍 `NOT_VERIFIED` | `APPROVED_SLICE` | 缺受控 prewrite/commit 效應入口；不可把派工互斥說成整個工作樹防回退已完成 |
| [ ] 07 完成與證據 | `STATUS_PROJECTION_LOCAL_INTEGRATED / CLOSURE_GAP` | Luna 改 `ticket_status_pipeline.py`／`ticket_status_template.py` 與測試；`3196712d`，審閱見 `doc/reviews/workflow-governance/27-evidence-linked-ticket-status-projection-code-review.md` | 108 tests／200 subtests、strict mypy 綠；必要 OPEN／NOT_VERIFIED 在錯誤 APPROVED 反向突變下轉紅，復原綠；可選未完成仍合法 | `APPROVED_SLICE` | 證據來源真偽、父項完成與 finding 責任／去向尚未形成結案准入 |
| [ ] 08 測試依賴／退役 | `READ_ONLY_INVENTORY / HOST_CAPABILITY_GAP` | Luna 唯讀盤點：`doc/runbooks/e7_owner_smoke.py` 與多個 `tests/` 模組存在間接 import；`implementation-tdd.md` 已有 B 承接後退役條款 | pytest 釘版與直接命令已查；SUITES／wrapper／literal subprocess 消費者圖及退役回放 `NOT_VERIFIED` | `NOT_REVIEWED` | 未有可信 consumer graph；不得以 CI 未列出或前置紅燈判斷測試無人使用 |
| [ ] 09 窄修窄審 | `INDEPENDENT_AUDIT_PARTIAL / GAP` | Root；既有 `CodeReview.md` §4–5、`implementation-authority.md`；Sol 獨立唯讀審計（2026-10-18） | Ticket 24/28 顯示同票追加修正及獨審拒收；15 tests／103 subtests 綠，但未證明共用支援檔真消費者、PASS 沿用與原 reviewer 身分複驗 | `PARTIAL / NOT_CLOSABLE` | 需要受影響消費者與 finding↔Closure 的可執行證據；不能靠政策文字打勾 |
| [ ] 10 成本／外部呼叫／回報 | `PARTIAL_EXISTING` | Root；`delivery-profile.md`、`security-boundary.md`、model profile（資料） | profile 與外部 effect 關卡已有；本機付費服務攔截及固定回報欄位 `NOT_VERIFIED` | `NOT_REVIEWED` | 模型升級理由及產品／腳本拆分需區分 |
| [ ] 11 去重與衝突 | `NOT_STARTED` | Root；現有 Router、派工模板、Runner、Reviewer、結案入口 | 待 01–10 差異落定後做單一來源／重複責任檢查 | `NOT_REVIEWED` | 不建第二套流程或審批關卡 |
| [ ] 12 回放與獨審 | `NOT_STARTED` | Root；沿既有 tests／review 位置 | 01–10 正反案例待建立；自動／固定情境分別記錄限制 | `NOT_REVIEWED` | 錯誤拒絕與合法通過都必須證明 |

## 本輪窄查來源與下一步

- 現行主線 continuation：`Workflow.md` §0.1、`router-control.md` Continuation；單票與
  完成證據：`specification-ticketing.md`、`CodeReview.md`、`review_admission.py`。
- 現行 worktree 與 correction：`implementation-authority.md`；現行測試品質：
  `implementation-tdd.md`、`review-checks.md`。它們是可重用基礎，尚未證明本表情境。
- 已完成 04／05／06／07 的局部候選、獨審與本地受控整合，但四項外層驗收仍開放。
  02 的初稿拒收，仍須修正真正 Owner effect／相依接續，不得重命名 dispatch wait 冒充。
  下一步依既有需求與 ticket 補足 02／05／06／07 的外層效應與驗收，再接續其他項目。

更新規則：每項補作者、精確改動位置、執行命令／退出碼／輸出摘要、候選 commit、
獨立審閱結論與未解 finding。只有從正式候選與可信執行紀錄取得證據，才可勾選。
