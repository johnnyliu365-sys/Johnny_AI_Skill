# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `28`；沿用既有12項與acf0ffa1／ded322b3批准；Owner 2026-10-18 批次本地授權，逐票限縮、獨審及證據如下。非 push／正式啟用授權 |
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
| [ ] 01 主線與單票 | `PROJECTION_FIXTURE_DOCS_INTEGRATED / 30B_REVIEW_BLOCKED` | 原29／30A／30M不重做；30B作者Luna、不同Sol獨審，候選fd98f395尚未整合；[證據](reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md) | 原91tests沿用；30B140tests、strict／compile及不同入口反向突變；R2前綴誤判同票修正複驗閉合 | `FIXTURE_APPROVED / 30B_ENGINEERING_PARTIAL` | R1真control／Grant來源未驗證；必要合格隔離audit UNAVAILABLE；正式fresh來源／完整主線及結案未證明 |
| [ ] 02 已核准工作接續 | `OWNER_WAIT_FIXTURE_INTEGRATED / LOCAL_BATCH_EXECUTED / EFFECT_OPEN` | 原24／30A與Context04／SPEC03保留；本批Root限縮Grant、分開派30B／31B／43／44及獨審，未逐票詢問Owner | 30A91tests／精確cleanup證據保留；等待30B／43審查時31B與44繼續並本地整合；30B140tests只支持readback候選，不代表可派工 | `30A_APPROVED / 30B_REVIEW_BLOCKED` | 真來源、`admit_dispatch`發憑證前接線、原生spawn硬攔截及正式結案仍未驗證；批次自主工作的真實紀錄不是新Host gate資格 |
| [ ] 03 派工完整最小 | `TEMPLATE_AND_SCAFFOLD_LOCAL_INTEGRATED / HOST_ADMISSION_OPEN` | Luna 候選 `e9bdc978`、`3557bc20` 與 Ticket 40 `91ee17c3` 改本庫 ticket template、出貨 scaffold 與同一驗證檔；獨審見 `doc/reviews/workflow-governance/28-minimal-complete-dispatch-ticket-code-review.md`、`38-reuse-and-responsibility-dispatch-contract-code-review.md`、`40-scaffold-ticket-template-parity-code-review.md` | Ticket 40：44 tests 綠；八個 scaffold 反向突變與 reviewer 另兩個遮蔽突變紅→綠；受控 gate `INTEGRATED` `5776139a`，兩檔 Git blob 等於受審候選 | `APPROVED_TEMPLATE_SLICES` | Host dispatch preflight 尚未驗證填票完整性；文字模板不能阻止實作者猜 Expected，也不能自動識別檔內耦合 |
| [x] 04 TEST → A → B | `COMPLETE_LOCAL / NO_PUSH` | Luna：Ticket 25 規則 `970b99cc`、Ticket 33 產品 A `ac369235`、Ticket 34 測試 B `b4a7dbe6`；獨審見 `doc/reviews/workflow-governance/33-shared-context-service-seam-code-review.md` 與 `34-shared-context-test-seam-transfer-code-review.md` | A 先在候選公開入口通過；Reviewer 改壞新 service 的 sealed read／writer role，公開 Router 格轉紅→綠。B 五格 contract-only 測試搬到聚焦檔、六格公開入口保留；Reviewer 改壞 service 與 contract guard，各自轉紅→綠；整合分支 61 tests／217 subtests、strict mypy 綠，五檔 Git blob 與各受審候選相同 | `APPROVED_A + APPROVED_B` | 此為本機 Johnny Router 能力回放；未推送／發布，不代表任何 target 產品已拆分 |
| [ ] 05 候選來源與 Expected | `CONTRACT_LOCAL_INTEGRATED / HOST_GAP` | Luna 改既有 `TestBinding`／`ReviewAdmissionGate`；`beff0050`，審閱見 `doc/reviews/controlled-verification/cve-d10-candidate-source-observation-code-review.md` | 19 tests／50 subtests 綠、`mypy --strict` 綠、Expected 反向突變紅→綠；型別契約拒絕舊基準載入與 Expected 漂移 | `APPROVED_CONTRACT_ONLY` | 尚無合格 Host adapter 觀察實際載入來源及核准 Expected 的來源；不得把 port 自報當實測 |
| [ ] 06 共用樹覆蓋 | `WORKER_CLAIM_LOCAL_INTEGRATED / PREWRITE_GAP` | Luna 改既有 worker ledger／測試；`9cedb55f`，審閱見 `doc/reviews/workflow-governance/26-active-writer-worktree-branch-uniqueness-code-review.md` | 48 tests／77 subtests 綠；active worktree／branch 衝突轉紅再回綠；任意同步寫入的 HEAD／index／工作副本驗證仍 `NOT_VERIFIED` | `APPROVED_SLICE` | 缺受控 prewrite/commit 效應入口；不可把派工互斥說成整個工作樹防回退已完成 |
| [ ] 07 完成與證據 | `PROJECTION_INTEGRATED / CLOSURE_CANDIDATE_REVIEW_BLOCKED` | 原27／35投影保留；Luna票43 `d477020e` 改既有 TestEvidenceResolver／ReviewAdmission／Router 與兩測試檔；[獨審](reviews/workflow-governance/43-review-closure-evidence-code-review.md) | 原投影121tests／205subtests；43獨審19tests／58subtests、strict，child-binding及reviewer-identity不同門突變紅→還原綠；正常結案與必要證據拒絕均覆蓋 | `43_ENGINEERING_PASS / NOT_INTEGRATED` | HIGH_ASSURANCE必要合格隔離審查UNAVAILABLE；真實resolver來源也未qualified。不能用普通獨審或port回件代替，不能正式結票 |
| [ ] 08 測試依賴／退役 | `GIT_SOURCE_AND_SUITE_SLICES_LOCAL_INTEGRATED / CI_RETIREMENT_GAP` | Luna：Ticket 32 純 AST inventory `2a19406d`、Ticket 36 釘選 Git 唯讀 adapter `e1ca2d4b`、Ticket 39 literal SUITES 消費者 `e9177f80`；獨審見 `doc/reviews/workflow-governance/32-test-consumer-inventory-code-review.md`、`36-git-pinned-test-source-inventory-code-review.md` 與 `39-literal-suite-consumer-inventory-code-review.md`。本輪 Root 對本地 pin 與 origin 九個 branch tip 做 scoped CI path readback，位置／版本／命令見 Ticket 30 | Ticket 39 初審找出未知字串與 subscript mutation 兩項假空圖；同票修正後 32 tests／7 subtests、strict mypy 綠，巢狀索引反向突變紅→綠。本輪搜尋範圍內未見 CI 配置；未載入可信 CI 命令，也未測入口切換 | `APPROVED_INVENTORY_SLICES / CI_SCOPE_READBACK_ONLY` | 此範圍未見不等於全域無 CI；空 command list 不授權舊測試退役，retirement effect gate `NOT_VERIFIED` |
| [ ] 09 窄修窄審 | `CORRECTION_CASES_VERIFIED / CLOSURE_CANDIDATE_REVIEW_BLOCKED` | 原35 consumer回歸保留；31B原作者修四finding、原獨審複驗；43 candidate沿既有Closure／AC精確關聯，沒有新增分類引擎 | 原pipeline／renderer／publisher126tests／205subtests；31B65tests、不同門反向突變；43 exact finding/child/dependency sets負例在獨審19tests／58subtests內 | `CASE_PASS / 43_ENGINEERING_PASS` | 43正式審查未通過不得整合；影響與實際consumer範圍仍須reviewer證據，不把字串分類當語意判定，不以一回合代表全Host強制能力 |
| [ ] 10 成本／外部呼叫／回報 | `MODEL_AND_REPORT_LOCAL_INTEGRATED / PAID_TEST_ISOLATION_GAP` | 原模型切片68a10057；Luna31B改兩模板／既有test，原獨審者APPROVED e83a4a72，Root gate64157fbe；[證據](reviews/workflow-governance/31-semantic-model-profile-boundary-code-review.md) | 原36tests／74subtests保留；回報65tests，七欄刪除14紅→綠；獨審改活躍label紅→綠；三blob精確等於受審候選、整合後65綠。產品／純腳本案例明確分開 | `APPROVED_31B / LOCAL_INTEGRATED / CLEANUP_BLOCKED` | 付費API／正式credential之真Host網路隔離未qualified；模板不證明語意真偽。清理遭Host政策阻擋，資產保留；整項不勾選 |
| [ ] 11 去重與衝突 | `WPR_TEMPLATE_AND_HISTORY_LOCAL_INTEGRATED / ACTIVATION_OPEN` | 原37／38／40／42保留；Luna44在既有RequirementLineageGate增加純revision-history驗證、重用原test；[獨審](reviews/workflow-governance/44-requirement-revision-compatibility-code-review.md) | 原42之46tests／不同位置WPR突變證據保留；44獨審14tests／30subtests、鏈結與terminal不同門突變紅→綠、Root gate1aa5ed22與兩blob一致；獨立seal確認 | `APPROVED_44 / LOCAL_INTEGRATED / CLEANUP_BLOCKED` | 舊一對一validate維持生效；可信creation issuer／效應前grant讀回／原子consume及真Host尚缺，不用純history方法冒充正式身分遷移；清理政策阻擋 |
| [ ] 12 回放與獨審 | `EXISTING_CASES_MAPPED / END_TO_END_NOT_VERIFIED` | Root沿下列既有測試／原review映射，不新增回放框架；30B／43仍為未整合候選 | 已有局部正常／拒絕／反向突變證據可重用；04不重跑；此輪65模板及14lineage為實際整合後回歸，不將候選測試冒充整合版測試 | `PARTIAL_ONLY` | 完整01–10正式入口回放仍依賴可信來源及合格Host／受限效應；不得勾選總驗收 |

## 本批剩餘限制與接續邊界

本批已准入建置30B／31B／43／44均回件並完成可執行的獨審／修正；31B與44
完成本地受控整合，30B與43不得整合。這不是12項全部完成，也不是「等逐票批准」。
Root與獨立既有盤點席以現有票／review窄查，沒有把下列缺口另開成重複框架。

- **必要審查能力**：30B／43強制的qualified唯讀／no-code／no-delegation隔離audit
  不可用。CVQ-D9是來源整合、D10是contract-only，不能借PASS。未核准候選不能當
  下游實作authority；不自行降低HIGH_ASSURANCE或建立VM/Broker來繞過。
- **真實來源／授權**：30B的R1尚未有approved-control來源；改binding Grant ID仍能
  通過fake讀回。現有dispatch-authority僅owner-intent marker，不能當protected issuer。
  Context04仍只有本地證據；前次直接remote main觀察a1cb6c13/Context03，不宣稱本輪
  fresh。發佈來源、實際GET／Host qualification與正式effect均不由本批假造。
- **正式強制與CI**：05實際載入來源、06任意工具prewrite、10付費網路隔離、11可信
  creation/atomic-consume及01–03/07的effect，需要真來源／受控Host資格。08缺的是
  可信CI具體命令與入口切換證據，不是「無CI」；曾見active dynamic Dependency Graph，
  空命令集合不能退休舊測試。12保留上述實際限制，不重複建同樣fixture掩蓋缺口。
- **清理**：44精確teardown在CreateProcess前被Host政策拒絕，未執行、未用等價指令
  重試。31B沿用同Root landing workspace避免再造資產；兩票journal與作者/reviewer
  worktrees留存，CLEANUP_BLOCKED。30B／43則因未結Review本就必須保留，Recovery不動。

恢復上述受影響工作的條件是取得適用Host/source的資格與必要外部effect授權，或
Owner按正式Change Control另核安全政策差異；本紀錄不自動要求／執行任一路線。
沒有push、release、deployment、Host activation、真target／付費API測試。04保持完成；
其他項保持未勾選，完整證據優先於表面完成率。

## 既有案例回放對照（不是另一套測試系統）

下列為可重用的已存在入口與各票既存執行證據，不表示本輪重新執行全部命令。
正常與拒絕條件在同一既有suite驗證；實際Host與模型行為不在純fixture的證明範圍。

| 項目 | 已有入口／固定情境 | 證據與限制 |
| --- | --- | --- |
| 01／02 | `tests/test_mainline_projection.py` 的 `test_waiting_ticket_does_not_block_independent_candidate_or_borrow_dependency`、`test_completing_independent_ticket_does_not_close_mainline_with_required_work_open`、`test_pending_optional_ticket_does_not_block_closure_candidate` | 29／30A原review；等待不凍結無相依票、必要主線不假完成、選配不無限阻擋。來源qualification／派工effect未證明 |
| 03 | `tests/test_ticket_template_contract.py` 的active-section／Expected／停止條件、filled虛構ticket | 28／38／40及31B review；缺欄、遮蔽與跨節內容拒絕，模板不是Host攔截 |
| 04 | 33／34既有review之service行為及承接突變 | 已完成，沿用61tests／217subtests，未重做 |
| 05 | `tests/test_review_admission.py` 的 `test_loaded_product_source_must_be_candidate_and_not_baseline`、`test_expected_must_match_resolver_approved_reference_and_digest` | D10既有19tests／50subtests；可信resolver的真Host觀察缺口保留 |
| 06 | `tests/test_worker_assignment.py` 的active-worktree／active-branch conflict、`test_different_receipts_racing_for_one_worktree_have_one_winner` | 26既有48tests／77subtests；拒絕並發claim但不冒充任意檔案寫入攔截 |
| 07／09 | 43候選`d477020e`的 `test_closure_requires_exact_identity_child_dependency_and_finding_sets`，原35consumer回歸及31B同作者／同reviewer修正 | 43僅工程驗證19tests／58subtests；未整合，不能在control HEAD聲稱這些新增case已存在；影響分析仍要真consumer證據 |
| 08 | `tests/test_test_dependency_inventory.py` 的literal SUITES／wrapper／dynamic unresolved；`test_test_dependency_source_adapter.py::...test_valid_empty_inventory_keeps_retirement_unauthorized` | 32／36／39review；追到間接使用者，未知不當作空圖，空清單不允許退役 |
| 10 | `tests/test_executor_routing.py` 的lowest-verified／lower-rank-reviewer拒絕；31B完整產品與純腳本兩例 | 原選模36tests／74subtests；31B整合65tests；付費網路隔離仍未測 |
| 11／12 | `tests/test_workflow_requirement_lineage.py` 原validate及新revision-history；原WPR一致性cells沿用同template suite | 44整合14tests／30subtests；舊legacy入口未退役，新能力未正式啟用；未另建永久減法Gate |

## 本批授權 — 2026-10-18

`batch-checklist-local-20261018` 的來源是本 session Owner 的明確決策：授權單位為
完成現有12項清單所需的 Johnny_AI_Skill 本地工作，包含30B及後續同範圍工作。
記錄基準為 `2e52772770e81669a7e1f92391a432572d4ead4b`。這是既有需求的執行授權，
不是新 PRD、第二套簽發器或把 Agent 自述轉成 Owner 批准。

Root 可拆票、選擇最小檔案範圍、簽發追溯本批的精確子票 Grant、安排具名作者與
不同席獨審、修正 findings、執行本地測試、提交及受控本地整合。每張子票仍須
綁定原需求／SPEC、exact baseline／leaf、角色／worktree、modify/create/delete、
AC／負例、資源上限與結果證據。作者不能批准自己；Grant 不得擴張本批目標。
既有已消耗額度及 findings 保留；新票不能重置累計耗用。一般同範圍工程選擇不再
要求逐票 Owner 批准；來源不符或超界仍只停止受影響工作。

不授權 push、release、deployment、正式啟用新派工／Host 閘門、其他專案、正式
敏感資料或新費用。外部驗收缺證據保持未完成；其他已准入本地工作接續。
30B 採既有候選600s命令累計／120s單命令上限，歷史30A耗用不重置；本輪測試
network=0，未執行候選中的真實外部GET。其 Grant 在原票內記錄及獨審後生效。
本段只解釋誰可限縮簽發已授權工作；不改兩份已核准 SPEC 的 AC 或安全不變量，
也不宣稱新硬性 Host 攔截已部署。精確票仍需批准，但批准者在本批內已由 Owner
委任 Root；SPEC「separately approved ticket」因此不要求再次人工確認。

## 歷次窄查與來源紀錄（截至 revision27）

以下保留原執行脈絡與當時未完成狀態；當前狀態以本表revision28及各原票最新review
段落為準。特別是30B已按本批Grant實作，31B固定回報與44純history已本地整合；
不得把歷史「待Grant／未開始」讀成還要Owner重複核准。

- 30M 在原 feature README、Ticket29／30 加入唯一機器契約，範圍限有證據的
  29投影→30可信接續，不冒充完整12項programme。Root逐項記批准來源、身分編碼、
  required／依賴、版本與owner/handoff；其他票未知關係未補造。bf7e1b9a/87b090ed
  的committedrawdigest／schema／投影通過，獨審APPROVED；獨審duplicatebinding
  反向輸入拒絕、原bytes恢復綠。91項聚焦回歸、strict／compile綠。本地control-plane
  gate已整合c07fe7d6並讀回精確HEAD／blobs，gate54tests／11subtests通過；最終
  seal/cleanup記既有review。01／02和全票30維持未勾選，文件不是來源/Host qualification。
- 30B真來源、無派工效應的四路徑票面／Grant候選已在原Ticket30準備，預設測試
  不上網；正式source GET另綁精確有界授權，不改fixture-only宣稱。直接遠端讀回
  main=`a1cb6c13`、Context03，尚無本地Context04；GitHub Actions卻有active
  Dependency Graph dynamic workflow，不能說無CI／無自動化，不能退役舊測試。
  精確命令、版本、限制和後續一次決策見既有Ticket30 review，不新造平行文件。

- 現行主線 continuation：`Workflow.md` §0.1、`router-control.md` Continuation；單票與
  完成證據：`specification-ticketing.md`、`CodeReview.md`、`review_admission.py`。
- 現行 worktree 與 correction：`implementation-authority.md`；現行測試品質：
  `implementation-tdd.md`、`review-checks.md`。它們是可重用基礎，尚未證明本表情境。
- 04 的 TEST→A→B 本機閉包已完成；05／06／07 仍有 Host／正式結案外層缺口，不得誤勾。
- 原有功能的修正、返工、補測與延伸不得新建重複 PRD；沿原需求身分修訂並保留核准與版本關聯。原有 `PRD-20260815-022` 和 `PRD-20260805-009` leaf 現記錄**已獨審的設計基準、runtime 待生效**，前者含 AC-17 身分替代摘要；沒有另建 PRD。現行 runtime 的 `adaptive-project-orchestration.md` revision05 AC-17、`requirement-lineage.md` 與 validator 仍要求一對一。須完成相容性遷移、Host 能力及測試收斂，不能把設計基準冒充執行中的閘門。
- 本輪沿**原 PRD／原 SPEC**完成兩份限定修正：AC-17 受審 `4531d00f`／blob `9c88d20e`，治理 AC9–11 受審 `8eae1af4`／blob `6fd8c309`；Ticket 41 精確 blob replay 經 document mutation gate 本地整合於 `76d1f942`，獨審與 83 tests／242 subtests 見 `doc/reviews/workflow-governance/41-bounded-spec-correction-integration-code-review.md`。Owner 本輪授權與獨審使其成為**設計基準**，不用重問同一 SPEC；現行一對一 validator、Ticket 30 的缺口、實作 Grant、Host 硬性准入與正式結案 effect 仍未完成。出貨 scaffold 的窄修不能代替外層入口。
- Ticket 41 同票修正了 SPEC 本文仍稱「獨審待完成」的狀態矛盾：受審設計內容不變，狀態綁定候選 `3856557c`（AC-17 獨審 PASS；治理同 blob 獨審 PASS），從控制基準 `04686524` replay 後由文件閘門整合於 `cca2db71`。現行兩份 SPEC blob 分別為 `ffb5304e`／`4323863f`；83 tests／242 subtests 通過。唯一隔離 journal 的兩筆證據與 SHA-256 已先封存，再精確清理，`Test-Path` 讀回不存在；Ticket 41 僅設計切片 `CLEANUP_CONFIRMED`，Host/Grant/runtime 缺口仍開放。
- 程式與測試腳本禁止按票堆疊成混合責任巨石。現有 `johnny-boundary` 的 `create` 預設拒絕、Git diff 比對與 `TEST → A → B` 已提供部分硬性保護；它們**不會**判斷檔案內部耦合。剩餘缺口是對真實候選的重用／新增責任／成長與相依結構證據的正式拒收入口；不得只靠文字、行數上限或新增平行 Gate 宣稱完成。
- 窄查 `library/`、`tests/` 的 Python 檔案：`tests/test_workflow_router.py` 約 3561 行且含 Router、Context telemetry、route instruction、Agent Context lease 四組測試類；`library/workflow_router/contracts.py` 約 1734 行含多個領域契約。這是結構審查觸發訊號，**不是**自動拆檔、刪測試或判定全部違規的證據；後續只能隨受影響能力做 TEST→A→B 承接。
- 本地整合分支對 01～10 已改動的 13 個相關測試檔作一次合併回歸：`330 passed, 568 subtests passed`；8 項 pytest collection warnings 是匯入的 `Test*` 型別非測試類別，沒有失敗。這不替代各票獨審或未合格 Host effect。
- 本輪 Ticket 40 與兩份尚未生效的 SPEC 提案後再驗證：`python -m pytest tests/test_plugin_payload_boundary.py tests/test_ticket_template_contract.py tests/test_workflow_requirement_lineage.py -q` 為 `96 passed, 223 subtests passed`；主線、Review、依賴與工作樹八檔聚焦回歸為 `177 passed, 226 subtests passed`。後者 6 個 pytest collection warnings 是匯入的 `Test*` 型別，不是失敗；這些綠燈不能代替 Host 派工、可信載入來源或正式結案 effect 證據。
  02 的初稿拒收，仍須修正真正 Owner effect／相依接續，不得重命名 dispatch wait 冒充。
  下一步依既有需求與 ticket 補足 02／05／06／07 的外層效應與驗收，再接續其他項目。

更新規則：每項補作者、精確改動位置、執行命令／退出碼／輸出摘要、候選 commit、
獨立審閱結論與未解 finding。只有從正式候選與可信執行紀錄取得證據，才可勾選。
