# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `35`；沿用既有12項與acf0ffa1／ded322b3批准；Owner批次本地授權與首次CVQ順序例外；SAME900重新分配350/220/330，原帳與1500總上限保留。非 OS變更／Host測試／push／正式啟用授權 |
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
| [ ] 01 主線與單票 | `PROJECTION_FIXTURE_DOCS_INTEGRATED / 30B_REVIEW_BLOCKED` | 原29／30A／30M不重做；30B作者Luna、不同Sol獨審，候選0f6d467a尚未整合；[證據](reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md) | 原91tests沿用；原30B140tests、R2修正保留；最新43聚焦tests及public繞過突變2紅→還原2綠只證明containment | `FIXTURE_APPROVED / CONTAINMENT_ONLY` | 合法可信Grant讀回成功另列R1 OPEN；必要合格隔離audit UNAVAILABLE；正式fresh來源／完整主線及結案未證明 |
| [ ] 02 已核准工作接續 | `OWNER_WAIT_FIXTURE_INTEGRATED / LOCAL_BATCH_EXECUTED / EFFECT_OPEN` | 原24／30A與Context04／SPEC03保留；本批Root限縮Grant、分開派30B／31B／43／44及獨審，未逐票詢問Owner | 30A91tests／精確cleanup證據保留；等待30B／43審查時31B與44繼續並本地整合；30B140tests只支持readback候選，不代表可派工 | `30A_APPROVED / 30B_REVIEW_BLOCKED` | 真來源、`admit_dispatch`發憑證前接線、原生spawn硬攔截及正式結案仍未驗證；批次自主工作的真實紀錄不是新Host gate資格 |
| [ ] 03 派工完整最小 | `TEMPLATE_AND_CONTENT_LOCAL_INTEGRATED / HOST_ADMISSION_OPEN` | 原28/38/40模板證據沿用；Luna票45新增ticket_content.py及聚焦test，獨審見[45 review](reviews/workflow-governance/45-ticket-content-completeness-code-review.md) | 45獨審與整合後152tests、strict、F1–F3基準紅→綠、reviewer duplicate不同門8紅→還原綠；gate a29c0e53及兩blob一致 | `APPROVED_CONTENT_SLICE / CLEANUP_BLOCKED` | 真committed/approved來源與Host effect前接線仍缺；純內容診斷不證明Expected語意/授權/依賴ready，也不自動識別耦合 |
| [x] 04 TEST → A → B | `COMPLETE_LOCAL / NO_PUSH` | Luna：Ticket 25 規則 `970b99cc`、Ticket 33 產品 A `ac369235`、Ticket 34 測試 B `b4a7dbe6`；獨審見 `doc/reviews/workflow-governance/33-shared-context-service-seam-code-review.md` 與 `34-shared-context-test-seam-transfer-code-review.md` | A 先在候選公開入口通過；Reviewer 改壞新 service 的 sealed read／writer role，公開 Router 格轉紅→綠。B 五格 contract-only 測試搬到聚焦檔、六格公開入口保留；Reviewer 改壞 service 與 contract guard，各自轉紅→綠；整合分支 61 tests／217 subtests、strict mypy 綠，五檔 Git blob 與各受審候選相同 | `APPROVED_A + APPROVED_B` | 此為本機 Johnny Router 能力回放；未推送／發布，不代表任何 target 產品已拆分 |
| [ ] 05 候選來源與 Expected | `CONTRACT_LOCAL_INTEGRATED / HOST_GAP` | Luna 改既有 `TestBinding`／`ReviewAdmissionGate`；`beff0050`，審閱見 `doc/reviews/controlled-verification/cve-d10-candidate-source-observation-code-review.md` | 19 tests／50 subtests 綠、`mypy --strict` 綠、Expected 反向突變紅→綠；型別契約拒絕舊基準載入與 Expected 漂移 | `APPROVED_CONTRACT_ONLY` | 尚無合格 Host adapter 觀察實際載入來源及核准 Expected 的來源；不得把 port 自報當實測 |
| [ ] 06 共用樹覆蓋 | `WORKER_CLAIM_LOCAL_INTEGRATED / PREWRITE_GAP` | Luna 改既有 worker ledger／測試；`9cedb55f`，審閱見 `doc/reviews/workflow-governance/26-active-writer-worktree-branch-uniqueness-code-review.md` | 48 tests／77 subtests 綠；active worktree／branch 衝突轉紅再回綠；任意同步寫入的 HEAD／index／工作副本驗證仍 `NOT_VERIFIED` | `APPROVED_SLICE` | 缺受控 prewrite/commit 效應入口；不可把派工互斥說成整個工作樹防回退已完成 |
| [ ] 07 完成與證據 | `PROJECTION_INTEGRATED / CLOSURE_CANDIDATE_REVIEW_BLOCKED` | 原27／35投影保留；Luna票43 `d477020e` 改既有 TestEvidenceResolver／ReviewAdmission／Router 與兩測試檔；[獨審](reviews/workflow-governance/43-review-closure-evidence-code-review.md) | 原投影121tests／205subtests；43獨審19tests／58subtests、strict，child-binding及reviewer-identity不同門突變紅→還原綠；正常結案與必要證據拒絕均覆蓋 | `43_ENGINEERING_PASS / NOT_INTEGRATED` | HIGH_ASSURANCE必要合格隔離審查UNAVAILABLE；真實resolver來源也未qualified。不能用普通獨審或port回件代替，不能正式結票 |
| [ ] 08 測試依賴／退役 | `LOCAL_COMMAND_SOURCE_INTEGRATED / CI_RETIREMENT_GAP` | 原32／36／39沿用；Luna46新增test_command_source.py與唯一verification-commands.json，擴充既有Git adapter/test；[46 review](reviews/workflow-governance/46-versioned-local-test-commands-code-review.md)，gate a0bfc286 | 同一commit/digest讀命令與Python來源；獨審修復深層JSON錯誤；整合後36tests／22subtests、strict、compile/import及四blob一致；作者digest與獨審target-membership不同門突變紅→還原綠 | `APPROVED_LOCAL_SOURCE / CLEANUP_BLOCKED` | 新來源僅LOCAL_VERIFICATION_ONLY兩套聚焦命令，不是完整正式CI；Dependency Graph不是測試CI，其他外部CI UNKNOWN；覆蓋承接／入口切換及retirement effect未證明，禁止退役 |
| [ ] 09 窄修窄審 | `CORRECTION_CASES_VERIFIED / CLOSURE_CANDIDATE_REVIEW_BLOCKED` | 原35 consumer回歸保留；31B原作者修四finding、原獨審複驗；43 candidate沿既有Closure／AC精確關聯，沒有新增分類引擎 | 原pipeline／renderer／publisher126tests／205subtests；31B65tests、不同門反向突變；43 exact finding/child/dependency sets負例在獨審19tests／58subtests內 | `CASE_PASS / 43_ENGINEERING_PASS` | 43正式審查未通過不得整合；影響與實際consumer範圍仍須reviewer證據，不把字串分類當語意判定，不以一回合代表全Host強制能力 |
| [ ] 10 成本／外部呼叫／回報 | `MODEL_AND_REPORT_LOCAL_INTEGRATED / PAID_TEST_ISOLATION_GAP` | 原模型切片68a10057；Luna31B改兩模板／既有test，原獨審者APPROVED e83a4a72，Root gate64157fbe；[證據](reviews/workflow-governance/31-semantic-model-profile-boundary-code-review.md) | 原36tests／74subtests保留；回報65tests，七欄刪除14紅→綠；獨審改活躍label紅→綠；三blob精確等於受審候選、整合後65綠。產品／純腳本案例明確分開 | `APPROVED_31B / LOCAL_INTEGRATED / CLEANUP_BLOCKED` | 付費API／正式credential之真Host網路隔離未qualified；模板不證明語意真偽。清理遭Host政策阻擋，資產保留；整項不勾選 |
| [ ] 11 去重與衝突 | `WPR_TEMPLATE_AND_HISTORY_LOCAL_INTEGRATED / ACTIVATION_OPEN` | 原37／38／40／42保留；Luna44在既有RequirementLineageGate增加純revision-history驗證、重用原test；[獨審](reviews/workflow-governance/44-requirement-revision-compatibility-code-review.md) | 原42之46tests／不同位置WPR突變證據保留；44獨審14tests／30subtests、鏈結與terminal不同門突變紅→綠、Root gate1aa5ed22與兩blob一致；獨立seal確認 | `APPROVED_44 / LOCAL_INTEGRATED / CLEANUP_BLOCKED` | 舊一對一validate維持生效；可信creation issuer／效應前grant讀回／原子consume及真Host尚缺，不用純history方法冒充正式身分遷移；清理政策阻擋 |
| [ ] 12 回放與獨審 | `EXISTING_CASES_MAPPED / END_TO_END_NOT_VERIFIED` | Root沿既有案例／review；46增加受版控本地命令來源，未新增回放框架；30B／43仍未整合 | 46合法command-plan與拒絕／版本釘選／不同門突變均有獨審；整合後36tests／22subtests。04不重做，既有局部PASS沿用，候選不冒充整合版 | `PARTIAL_ONLY` | 完整01–10正式來源/effect回放仍缺；首次Host建構順序例外只是待Owner採納提案，不是資格或總驗收 |

## 本批剩餘限制與接續邊界（revision31歷史；最新判定見下節）

本批已准入建置30B／31B／43／44均回件並完成可執行的獨審／修正；10-19另完成
30B公開入口偽造Grant的限縮修正0f6d467a，原獨審確認PASS_CONTAINMENT_ONLY；31B與44
完成本地受控整合，30B與43不得整合。這不是12項全部完成，也不是「等逐票批准」。
Root與獨立既有盤點席以現有票／review窄查，沒有把下列缺口另開成重複框架。

- **必要審查能力**：30B／43強制的qualified唯讀／no-code／no-delegation隔離audit
  不可用。CVE-D9是來源整合、D10是contract-only，不能借PASS。未核准候選不能當
  下游實作authority；不自行降低HIGH_ASSURANCE或建立VM/Broker來繞過。
- **真實來源／授權**：30B原fd98f395可被grant-forged騙出candidate；新候選0f6d467a
  已封住公開入口，43聚焦tests及strict mypy通過、獨審繞過突變2紅→還原2綠。
  可信來源仍未具備，公開入口一律在factory/clock前拒絕；不冒稱正式R1通過。
  已通過的演算法fixture另走私有未准入seam，不是假authority；現有dispatch-authority
  僅owner-intent marker，不能當protected issuer。
  Context04仍只有本地證據；前次直接remote main觀察a1cb6c13/Context03，不宣稱本輪
  fresh。發佈來源、實際GET／Host qualification與正式effect均不由本批假造。
- **正式強制與CI**：05實際載入來源、06任意工具prewrite、10付費網路隔離、11可信
  creation/atomic-consume及01–03/07的effect，需要真來源／受控Host資格。08缺的是
  可信CI具體命令與入口切換證據，不是「無CI」；曾見active dynamic Dependency Graph，
  空命令集合不能退休舊測試。12保留上述實際限制，不重複建同樣fixture掩蓋缺口。
- **清理**：44精確teardown在CreateProcess前被Host政策拒絕，未執行、未用等價指令
  重試。31B沿用同Root landing workspace避免再造資產；兩票journal與作者/reviewer
  worktrees留存，CLEANUP_BLOCKED。30B／43則因未結Review本就必須保留，Recovery不動。

10-19具體工具／現場證據已封存在既有[票30審閱](reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md#local-blocker-investigation--2026-10-19)：
原始cleanup call `call_559be669d1134a79b54b135b6772388e` 的請求完整保存，回件為
`CreateProcess ... blocked by policy`，儲存的錯誤本身已截去2706字元，缺段不猜。
未找到候選綁定的隔離qualification call/receipt，記MISSING，不宣稱測試失敗。
目前spawn schema沒有每席sandbox／工具限制參數；danger-full-access由父席繼承，
不能靠prompt變成no-code/no-delegation。現場core binary為codex-cli0.163.0-alpha.10.2，
不等於Desktop資格。獨立文件審閱APPROVED_DOC_EVIDENCE_ONLY；無刪除重試或權限變更。
31B／44的功能驗收不受清理阻塞否定，但不得假結票；30B／43維持未整合。

恢復上述受影響工作的條件是取得適用Host/source的資格與必要外部effect授權，或
Owner按正式Change Control另核安全政策差異；本紀錄不自動要求／執行任一路線。
沒有push、release、deployment、Host activation、真target／付費API測試。04保持完成；
其他項保持未勾選，完整證據優先於表面完成率。

本輪最終文件證據獨審：`/root/batch_authority_review` 對209af56b確認上述狀態、
唯一04勾選、29／30 raw-LF digest與鏡像一致；僅兩處CVE-D9引用誤植，Root在
`5aeeb9b4b56898e878fd18c528fd3e431ab47426` 精確修正，同席複驗
`APPROVED_DOC_EVIDENCE_ONLY`。受審checklist blob
`8e4dcff2d5b02cc22a85f4b004beaf655f3704e9`、票30review blob
`3145dbb072b1ba39c67a2f15a9047524f4e9dc8b`；本段是其結果台帳，不擴大其審查範圍。
本地文件動作回傳ACTION_COMPLETED；未完成票保持各自REVIEW_BLOCKED／
CLEANUP_BLOCKED／NOT_VERIFIED，不能用本文件批准解除來源或Host限制。

## 2026-10-19 原生工具續行（revision35）

Owner核准同900角色轉配350/220/330，非歸零或新費用。原30G author161/reviewer84、
Root全部原帳及中止紀錄保留；舊控制端精確總額UNRECONCILED，保守預留200而非假稱已恢復。
原Ticket30N1已限縮九CREATE、零既有source修改；先type constructor/nullable編譯，再原生
唯讀getter與候選執行檔測試。先獨審票面，精確子Grant生效才派工，不偷擴30G六檔切片。
目標是設定描述元產生與唯讀觀察工具，非已安裝服務／受保護觀察者／CVQ合格；原生guard、
服務與首次Host操作按實際依賴續行，另守原例外／授權。當前未新增完成勾選，30G/30B/43持續hold。

## 2026-10-19 30G源碼工程閉包與安裝準備（revision34，歷史）

作者 /root/ticket30g_source_impl、不同席 /root/ticket30g_source_review；候選
20bd6e3036608d61feb687ea6e0ff6b7953d3e11 對6f6c938cd3d6eeff9e07cdffddfcbfdcbdc08cd0
恰六個CREATE、零MODIFY/DELETE。grant_authority/contracts、ledger、client與兩組
聚焦測試分責任；有效行數176/259/156、tests282/328，無額外框架或持久探針。
G1兩finding同票窄修複驗；雙席92tests、strict、compile/import，作者公開fixture smoke綠。
作者CAS1紅、peer/plan13紅；獨審stored-plan-digest不同門1紅；精確還原後均綠。
完整版本／命令／未驗證限制見原[30 review](reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md)。

結果僅ENGINEERING_PASS / SOURCE_ONLY_UNQUALIFIED；合法源碼記錄成功不等於真實可信
Grant，最終合格隔離audit仍缺，候選未整合。30B／43保持REVIEW_BLOCKED，本表不新增勾選。
原599.2保留；追加900不重置。runbook§6已準備帳戶/SID、權限、版本、通訊/網路、
命令、驗證、還原明細並獨立文件複驗；尚未建好的原生payload/config/observer明示
NOT_BUILT。沒有OS設定、Host測試、push/release/deployment、正式閘門或遭拒清理重試。
接續限縮原生實作／精確操作manifest及另行外部確認，不能拿本切片解除原有審查要求。

## 2026-10-19 30G-SOURCE續行（revision33，歷史）

Owner已核准runbookrevision02首次CVQ順序例外（非Host測試）及原Ticket30六CREATE／
零MODIFY/DELETE源碼建置；原599.2/600保留，追加900分450/300/150，總上限1500。
Root依原變更流程修票／獨審後派生開發子Grant，不再逐票問同一核准。當前30G為
文件准入；先新契約constructor實測，再帳本／client；有正常成功及錯配／重放拒絕，
但每項成功明標SOURCE_ONLY_UNQUALIFIED。HIGH_ASSURANCE最終audit未被本次例外取消，
候選封存不冒充正式資格／整合；30B/43與01/02仍未完成，04不重做。
同一runbook將準備帳戶/SID、服務、保護路徑/DACL、binary/config版本、IPC/網路、
命令/驗證/還原明細，未建立/未建置值不編造；實際安全操作仍須一次精確確認。

## 2026-10-19 核心實現方案與獨立本地續行（revision32歷史）

本輪完成[Grant／原生唯讀Host實現方案](runbooks/grant-and-readonly-host-implementation.md)
revision02。普通獨立架構／文件審閱APPROVED_AS_PROPOSAL，受審b77fc961／blob
a9786cb7e8b1e8aa2eda1c74742c3e0596a8ac7e。這不是再次核准既有SPEC；真正新差異
是首次CVQ建構／獨審的受限順序例外、本機受保護信任邊界設定及30B源碼預算增額。
既有本地批次不能暗中授予這三項。最終五項隔離／六前提不降級，暫定證據不發資格。

專案要實作受保護Grant ledger／IPC／client與既有CVQ的原生CLI adapter；現有
CLI旗標及CodexSandboxService不是成品issuer或qualification。Owner只需一次決定
是否接受方案內的新增授權包，提供OS同意／存取，不需自己設計或供應成品。
精確六create的30G-SOURCE與建議額外900命令秒已列；30B原599.2/600原帳保留，
總上限1500僅為提案，未核發實作Grant或執行native操作。30B／43仍REVIEW_BLOCKED。

不依賴這些新權限的46已完成：作者352a0829→單次修正2ba55781、不同席獨審APPROVED，
Root沿既有gate整合a0bfc286e2102b9ccfc2575f58bbb2e08b8f44b0，四blob精確相同；
整合後36tests／22subtests、strict、compile/import綠。命令由新的受版控JSON唯一維護，
只證明兩組本地聚焦驗證，不冒稱完整CI或退役授權；08／12仍不勾選。
原始工具紀錄恢復作者／reviewer記帳，含獨立seal後保守146.77/150與83/100，Root全額計50，
總上界279.77/300。非平台額度、非預算重置；清理保留既有CLEANUP_BLOCKED，不重試。
精確命令／SHA與可信遠端補查在方案§4：已讀Actions只見Dependency Graph，固定main
的workflow目錄404但同SHA其他檔可讀，不能混同「無權限」或斷言全域無CI。
未執行任何服務安裝／權限變更／資格攻擊／外部模型請求／push／release／deploy。

## 2026-10-19 逐項依賴核對與可准入續行

核對基準 `0cb5b6085d3dd0f1588569cbbcff5f820ff0d2a2`；Root與不同席
`/root/batch_authority_review`對照實際AC、票面、程式消費者及既存證據。
這是剩餘驗收對照，不以票號排序發明主線依賴，也不是另一套Gate。
**不是所有剩餘工作都被Host阻塞**：03的實際票面內容診斷可先建置，已沿
AC10派出[票45](../modules/tickets/workflow-governance/45-ticket-content-completeness.md)，
文件獨審APPROVED、Grant生效；現已獨審通過並gate整合a29c0e53，152tests再次通過。
不改30B/43的HIGH_ASSURANCE要求；原未完成主項不因此勾選。

| 項目 | 尚缺的必要驗收 | 實際依賴與查證位置 | 本地處置／最小外部輸入 |
| --- | --- | --- | --- |
| 01 | 真實可信完整主線讀回、必要項未完不假結案 | 29投影/30A解析已整合；30B public候選0f6d467a只有拒絕；SPEC AC9、mainline_readback.py | 維持正向Grant驗收OPEN；需要受保護issuer的實際讀取入口及新鮮正式來源。清單本身不證明完整主線已核准 |
| 02 | 合法獨立B在真來源及效應前准入後繼續；缺授權B/C拒絕 | 24 owner-wait、29/30 fixture與批次31B/44實際續行；dispatch_authority.py::admit_dispatch目前owner-intent marker | 不凍結45；最終需要qualified來源/攔截，正式啟用仍未授權 |
| 03 | 已提交且核准的完整票，在真正spawn/receipt之前檢查 | 28/38/40只驗模板；45已補實際內容診斷，仍不驗provenance；SPEC AC10及dispatch_session.py::admit_dispatch呼叫 | 45純content正反例已整合；真來源綁定及effect wiring後續HIGH_ASSURANCE，不以普通review替代 |
| 04 | 無本批本地缺口 | 25/33/34，61tests/217subtests及service行為突變 | COMPLETE_LOCAL，沿用證據不重跑 |
| 05 | 實際載入候選SHA及獨立核准Expected來源可觀測，不接受自報 | D10票明禁executor/adapter；TestBinding/TestEvidenceResolver、review_admission.py、router.py注入點已有19tests/50subtests | 需實際執行Host提供外於受測程式的版本觀察、核准Expected讀回及防竄改證據；新port/fake不能補足 |
| 06 | 寫入/提交前核對HEAD/index/workcopy，避免舊副本回退 | 26 scope排除任意寫入；worker_assignment.py claim在dispatch_session.py消費，不攔截filesystem/commit | 需真實寫入工具的可攔截effect入口及原子/隔離保護。再造未消費pure checker不能證明阻止覆蓋 |
| 07 | 正式父項結案受exact candidate/獨立review/可讀回AC證據約束 | 27/35純投影；43 candidate d477020e，19tests/58subtests工程PASS但未整合 | 缺43必要隔離audit及真resolver；候選/Review hold保留，不重派已綠實作 |
| 08 | 實際CI命令/間接呼叫入口與覆蓋承接，才可退役 | 32/36/39沿用；46已補同commit/digest本地command-plan入口，舊caller宣告入口未冒充可信來源 | 本地唯一命令來源已可自行建立／驗證；正式CI消費、完整suite選擇／覆蓋承接仍待後續；已查來源未建立測試CI，其他外部CI UNKNOWN，不要求Owner拼成品 |
| 09 | 窄修窄審之PASS在正式證據路徑有條件沿用，不能逃避真正finding | 31B原作者/原reviewer同票修正已證明；35 projection與43 closure consumer | 原局部PASS保留；正式43 evidence path仍受其隔離審查/來源阻塞，無新無關重審 |
| 10 | 本機測試不能無聲呼叫付費API或正式credential | 31模型映射與31B七欄回報已整合；報告格式不等於網路隔離 | 需測試Host的credential遮蔽與egress阻擋可觀察能力；不得透過真付費呼叫測試。清理另列，不抹消功能PASS |
| 11 | PRD revision新模式可信creation grant/單次consume/遷移驗證後才替換舊規則 | 37/38/40/42衝突已修；44 history方法不發權；AC17、現有owner-intent marker非protected issuer | 缺可信簽發及效應邊界；舊一對一validate保持有效。無消費者證明不得刪除舊能力 |
| 12 | 01–10之必要正反情境在其實際來源/effect完成回放及獨審 | 下節既存案例表區分fixture、候選、整合、Host；45新增instance內容例已獨審整合而非新框架 | 可測45已完成；其餘只隨各自上列證據取得後補驗，不重跑04或把全fixture綠當全批完成 |

### 30B正向驗收不是安全封堵

原`grant-forged`在fd98f395產生candidate的反例與0f6d467a回歸保留。
另列未完成的正向：**合法Grant必須從不可由caller改寫的可信來源讀回，精確綁定
project/ticket/stage/actor/baseline/operation與有效期限，在同一新鮮正式觀察SHA
讀index/leaves後成功回candidate**；偽造、錯配、失效及重放仍在effect前拒絕。
private演算法fixture成功不能充當這項PASS，全部public拒絕也不能。

已窄查`library/local_orchestration`及`library/workflow_router`的Grant/issuer/
signature/approval入口：`dispatch_authority.create_dispatch_grant/read_dispatch_grant`
明示owner-intent marker、同程序可建立；project_authority只歸約傳入觀察；沒有
在此範圍找到qualified production issuer。缺的是可信來源及其保護/讀回契約，
不是Root缺少本地程式修改授權。新增一個相信caller的Resolver會重演同一缺陷。
在實際來源可指定後，本地adapter/負例可沿原30B修最小allowlist，不重問整批授權；
若要新credential、OS權限或可信服務設定，則是尚未授權的外部能力。
30B累計保留599.2/600命令秒，上限不因新子票重置；下一實作嘗試還需精確追加
執行額度或可信更正帳目，不能把純調查當成預算重生。尚未安排重試。

### 最小Host能力需求（不指定未驗證環境）

沿用CVQ Manifest/QualificationCase/Observation/CapabilityKey/Report；不新建VM、
Broker或第二Runner。下列是需要取得的能力與證據，不是已測試或已qualified。
原始查證和失敗呼叫見票30既有review，未找回的qualification原始紀錄標MISSING。

| 必須限制什麼 | Qualification必須怎麼證明 | 現場具體缺口 |
| --- | --- | --- |
| 精確Host surface/binary/config不可偷換 | pin產品surface、binary hash、有效設定、工具清單，執行前後獨立讀回，變動拒絕 | 已讀core CLI0.163.0-alpha.10.2，不是Desktop資格；現行spawn沒有逐席sandbox/工具policy參數 |
| 僅讀核准candidate快照，不接其他worktree/secrets | allowlisted source快照identity/digest；越界/連結/替換來源嘗試被外部observer確認拒絕 | 目前子席同filesystem權限；prompt中的路徑限制非隔離 |
| 禁止寫入 | 所有檔案/工具/API寫入路徑，包括alias與間接入口，在effect前拒絕；canary前後讀回不變 | danger-full-access繼承；未有candidate-bound寫入deny證據 |
| 禁止程式執行 | 禁shell/interpreter/eval/任意腳本及間接執行；只允許資格指定的唯讀操作 | 工具schema未能移除exec或證明間接路徑封閉；禁止語句不算 |
| 禁止再派工 | spawn/followup/跨thread控制/MCP alias與間接adapter都被工具dispatcher拒絕 | collaboration提供delegation能力，沒有已驗證的每席移除入口 |
| 未知旁路default-deny | 新增/未知tool、未登錄alias或設定漂移拒絕而非默認放行 | 無實際dispatcher拒絕觀察；不重跑一般helper冒充qualification |
| 可信觀察與Review獨立性 | observer不受被審負載控制；記工具請求、deny、effect前後、candidate/模型/成本/終態 | 精確隔離qualification call/receipt未找到，MISSING；ordinary獨審只證明工程檢查 |
| 成本與外部網路/credential | 有界模型Session與總成本、無正式credential、未授權egress拒絕且可讀回 | 本批未授權新費用/帳號或Host設定；schema/prompt不提供可證明的成本上限 |

最小外部決策不是「再批准本地工作」：需要能提供上述精確surface限制及可信
observer的原生Host配置/權限與其資格執行授權；有具體surface才安排一次有限CVQ，
不聲稱換CLI/Desktop/VM就會成功。若沒有可用能力，維持REVIEW_BLOCKED；政策改動
須另走正式Change Control，不由本輪自行降級。正式遠端來源publication、真正
Grant簽發設定、付費/真Host呼叫與新正式閘門啟用均仍不在本批內。

### CI唯讀補查（2026-10-19）

命令（只讀repo Actions metadata，未下載含敏感內容的job log）：
`gh api repos/johnnyliu365-sys/Johnny_AI_Skill/actions/workflows`；
`gh api 'repos/johnnyliu365-sys/Johnny_AI_Skill/actions/runs?per_page=5'`；
`gh api repos/johnnyliu365-sys/Johnny_AI_Skill/actions/runs/32693024347/jobs`。
回件workflow總數1：339484080，Dependency Graph，active，
`dynamic/dependabot/update-graph`，updated_at2026-08-21T23:21:28+08:00。
run總數9，本次取最近5筆；最新32693024347綁head
`bd2d9adaa586412de76ed8c3961ae1c697410554`、event dynamic、success。
job97329979967 `update-pip-graph`五步：Set up job、Create job directory、
Run Dependabot、Post Run Dependabot、Complete job，均success。
此metadata沒有正式測試命令，不推論其餘run或其他CI系統不存在。
延用前輪本地/九個遠端branch tree之範圍內未見配置結果，不重做全repo盤點。

## 既有案例回放對照（不是另一套測試系統）

下列為可重用的已存在入口與各票既存執行證據，不表示本輪重新執行全部命令。
正常與拒絕條件在同一既有suite驗證；實際Host與模型行為不在純fixture的證明範圍。

| 項目 | 已有入口／固定情境 | 證據與限制 |
| --- | --- | --- |
| 01／02 | `tests/test_mainline_projection.py` 的 `test_waiting_ticket_does_not_block_independent_candidate_or_borrow_dependency`、`test_completing_independent_ticket_does_not_close_mainline_with_required_work_open`、`test_pending_optional_ticket_does_not_block_closure_candidate` | 29／30A原review；等待不凍結無相依票、必要主線不假完成、選配不無限阻擋。來源qualification／派工effect未證明 |
| 03 | 原template suite，加`tests/test_ticket_content.py`的實際filled內容、缺欄/placeholder/重複/新檔對照及H1/H2/H3回歸 | 45及原28／38／40／31B review；152聚焦tests，合法內容繼續、違反形狀拒絕；不等於Host攔截 |
| 04 | 33／34既有review之service行為及承接突變 | 已完成，沿用61tests／217subtests，未重做 |
| 05 | `tests/test_review_admission.py` 的 `test_loaded_product_source_must_be_candidate_and_not_baseline`、`test_expected_must_match_resolver_approved_reference_and_digest` | D10既有19tests／50subtests；可信resolver的真Host觀察缺口保留 |
| 06 | `tests/test_worker_assignment.py` 的active-worktree／active-branch conflict、`test_different_receipts_racing_for_one_worktree_have_one_winner` | 26既有48tests／77subtests；拒絕並發claim但不冒充任意檔案寫入攔截 |
| 07／09 | 43候選`d477020e`的 `test_closure_requires_exact_identity_child_dependency_and_finding_sets`，原35consumer回歸及31B同作者／同reviewer修正 | 43僅工程驗證19tests／58subtests；未整合，不能在control HEAD聲稱這些新增case已存在；影響分析仍要真consumer證據 |
| 08 | 原literal SUITES／wrapper／dynamic unresolved；46的committed command-plan、未知target、digest／workingcopy／HEAD／replace釘選與closed JSON案例 | 32／36／39沿用，46獨審／整合後36tests／22subtests；retirement永遠False，本地manifest不冒充CI |
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
