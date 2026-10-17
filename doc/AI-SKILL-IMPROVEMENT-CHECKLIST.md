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
| [ ] 01 主線與單票 | `GAP_IDENTIFIED` | Root；既有 `Workflow.md` Router、`agent-context-lifecycle.md`、ticket template（未修改） | 現有單票 Context；「首張血壓測試完成、主線仍未完成」未回放 | `NOT_REVIEWED` | 主線剩餘票／交接與父項完成判定未明確驗證 |
| [ ] 02 已核准工作接續 | `REVIEW_CHANGES_REQUESTED` | Root 開 `workflow-governance/24`；Luna 改 `tests/test_autonomous_collaboration.py`；獨審見 `doc/reviews/workflow-governance/24-independent-admitted-ticket-continuation-code-review.md` | 候選 `953c2cea`：20 tests／20 subtests 綠；審閱反向突變轉紅再回綠，但只證明 dispatch confirmation 路徑 | `CHANGES_REQUESTED` | SQL／不可逆 effect Owner wait 在 Profile 無路由；主線相依、來源漂移、政策 digest pin 未處理；不整合、不勾選 |
| [ ] 03 派工完整最小 | `PARTIAL_EXISTING` | Root；`specification-ticketing.md` Ticket／Dispatch，`ticket-decomposition.md` | 局部 Closure／型別 preflight 已有；固定 Expected／失敗、邊界、停止及獨審情境 `NOT_VERIFIED` | `NOT_REVIEWED` | 需求重用與精簡投影需檢查實際 reader |
| [ ] 04 TEST → A → B | `SLICE_LOCAL_INTEGRATED / A_B_OPEN` | Luna 改 `implementation-tdd.md`、ticket template、profile pin 與既有 service 測試；`970b99cc`，審閱見 `doc/reviews/workflow-governance/25-refactor-test-seam-transfer-code-review.md` | 66 tests／225 subtests 綠；Reviewer 對 service 行為作反向突變紅→綠；並非實際 Router→service 產品拆分 | `APPROVED_SLICE` | 真正 A 候選版行為及其 B 依賴尚未回放；不可把腳本／規則改動寫成產品拆分完成 |
| [ ] 05 候選來源與 Expected | `CONTRACT_LOCAL_INTEGRATED / HOST_GAP` | Luna 改既有 `TestBinding`／`ReviewAdmissionGate`；`beff0050`，審閱見 `doc/reviews/controlled-verification/cve-d10-candidate-source-observation-code-review.md` | 19 tests／50 subtests 綠、`mypy --strict` 綠、Expected 反向突變紅→綠；型別契約拒絕舊基準載入與 Expected 漂移 | `APPROVED_CONTRACT_ONLY` | 尚無合格 Host adapter 觀察實際載入來源及核准 Expected 的來源；不得把 port 自報當實測 |
| [ ] 06 共用樹覆蓋 | `WORKER_CLAIM_LOCAL_INTEGRATED / PREWRITE_GAP` | Luna 改既有 worker ledger／測試；`9cedb55f`，審閱見 `doc/reviews/workflow-governance/26-active-writer-worktree-branch-uniqueness-code-review.md` | 48 tests／77 subtests 綠；active worktree／branch 衝突轉紅再回綠；任意同步寫入的 HEAD／index／工作副本驗證仍 `NOT_VERIFIED` | `APPROVED_SLICE` | 缺受控 prewrite/commit 效應入口；不可把派工互斥說成整個工作樹防回退已完成 |
| [ ] 07 完成與證據 | `STATUS_PROJECTION_LOCAL_INTEGRATED / CLOSURE_GAP` | Luna 改 `ticket_status_pipeline.py`／`ticket_status_template.py` 與測試；`3196712d`，審閱見 `doc/reviews/workflow-governance/27-evidence-linked-ticket-status-projection-code-review.md` | 108 tests／200 subtests、strict mypy 綠；必要 OPEN／NOT_VERIFIED 在錯誤 APPROVED 反向突變下轉紅，復原綠；可選未完成仍合法 | `APPROVED_SLICE` | 證據來源真偽、父項完成與 finding 責任／去向尚未形成結案准入 |
| [ ] 08 測試依賴／退役 | `GAP_IDENTIFIED` | Root；現有 CI／wrapper／runner 尚待窄查 | 間接 SUITES／subprocess 回放 `NOT_VERIFIED` | `NOT_REVIEWED` | 退役前須證明契約承接與入口切換 |
| [ ] 09 窄修窄審 | `PARTIAL_EXISTING` | Root；`CodeReview.md` §4–5、`implementation-authority.md` | 原票原 worktree 及影響面重驗已有；shared/support 真使用者回放 `NOT_VERIFIED` | `NOT_REVIEWED` | 有關 finding 不得標成範圍外 |
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
