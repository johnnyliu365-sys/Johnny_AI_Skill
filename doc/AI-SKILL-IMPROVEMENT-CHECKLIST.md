# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `01`；Owner 2026-10-18 本次 12 項指示 |
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
| [ ] 02 已核准工作接續 | `IMPLEMENTATION_IN_REVIEW` | Root 開 `workflow-governance/24`；Luna 改 `tests/test_autonomous_collaboration.py` | 候選 `953c2cea`：20 tests／20 subtests 綠；尚需獨審確認回放不是把 dispatch confirmation 假裝 SQL effect | `PENDING` | `router-control.md` 受兩處 digest pin 保護，現票未准改 pin；有界 correction 待獨審 |
| [ ] 03 派工完整最小 | `PARTIAL_EXISTING` | Root；`specification-ticketing.md` Ticket／Dispatch，`ticket-decomposition.md` | 局部 Closure／型別 preflight 已有；固定 Expected／失敗、邊界、停止及獨審情境 `NOT_VERIFIED` | `NOT_REVIEWED` | 需求重用與精簡投影需檢查實際 reader |
| [ ] 04 TEST → A → B | `PARTIAL_EXISTING` | Root；`implementation-tdd.md` 與 `review-checks.md` | 既有行為測試和反向突變規則；router→service 的真正 service 突變情境 `NOT_VERIFIED` | `NOT_REVIEWED` | 拆分前依賴／接線與突變目標遷移 |
| [ ] 05 候選來源與 Expected | `CONTRACT_IMPLEMENTING` | Root 開 `controlled-verification/cve-d10`；Luna 處理既有 `TestBinding`／`ReviewAdmissionGate` | 舊基準載入、新候選、Expected 漂移的 typed admission 尚待候選結果；真實 Host 觀察 adapter 尚無，不能宣稱整項完成 | `NOT_REVIEWED` | 契約通過後仍需合格執行端的實際載入來源證據 |
| [ ] 06 共用樹覆蓋 | `PARTIAL_EXISTING / CAPABILITY_GAP` | Root；`implementation-authority.md`、`guarded_integration.py`、`document_mutation_gate.py`、`target_document_management.py`（未修改） | 現有 worktree 隔離、main revision check、document CAS；同樹舊副本回退、index／工作副本與未追蹤檔保護 `NOT_VERIFIED` | `NOT_REVIEWED` | 無通用受控 prewrite/commit 效應入口；不能把 integration 的乾淨樹檢查宣稱成每次寫入的原子 CAS |
| [ ] 07 完成與證據 | `PARTIAL_EXISTING` | Root；`review_admission.py`、`CodeReview.md`、`implementation-tdd.md` | BLOCKED／INCONCLUSIVE 拒入 review 已有；必要子項 NOT VERIFIED 與可選待辦回放 `NOT_VERIFIED` | `NOT_REVIEWED` | 父項完成、階段狀態與 finding 去向的實際來源 |
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
- 下一張最小獨立切片優先 02／07 的「有證據才接續」與 05 的「候選來源讀回」；
  04 的測試接線和 06 的共用樹防回退各有不同效應邊界，依既有 ticket 派工順序處理。

更新規則：每項補作者、精確改動位置、執行命令／退出碼／輸出摘要、候選 commit、
獨立審閱結論與未解 finding。只有從正式候選與可信執行紀錄取得證據，才可勾選。
