# Johnny AI Skill 改進檢查表

| 欄位 | 值 |
| --- | --- |
| 文件身分 | `AI-SKILL-IMPROVEMENT-CHECKLIST`；本專案工作追蹤，非新 PRD／SPEC／Gate |
| Revision／來源 | `72`；沿用既有12項與acf0ffa1／ded322b3批准；Owner `batch-checklist-local-20261019-uncapped` 取消本批人為累計秒數／固定修正次數，舊帳不歸零；首次CVQ順序例外及所有安全／外部效應限制保留 |
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
| [ ] 12 回放與獨審 | `EXISTING_CASES_MAPPED / END_TO_END_NOT_VERIFIED` | Root沿既有案例／review；46增加受版控本地命令來源，未新增回放框架；30B／43仍未整合 | 46合法command-plan與拒絕／版本釘選／不同門突變均有獨審；整合後36tests／22subtests。04不重做，既有局部PASS沿用，候選不冒充整合版 | `PARTIAL_ONLY` | 完整01–10正式來源/effect回放仍缺；Owner已採納首次入口順序例外，但未授權Host測試；不是資格或總驗收 |

## 當前工程接續與精確證據（revision72）

H10E候選6d98edcc完成來源獨審、218tests／strict4及Root不同權限mask突變
紅→精確綠，3筆raw封存9c0f3267，組合6f563a7b兩CREATE／原50不變。
C10候選105877f0關閉F1/F2：跨寫入身分比較、原生close結果確認與剩餘owner
保留；原作者三組修正突變、Root不同retention門紅→還原綠、build零W/E。
8827753b封存78筆原始raw（含失敗不洗白），組合77a8cb4b五blob等受審版、
原52中兩指定wiring改／其餘50不變、總55；不同席位mapping/archive PASS。
只完成本地source engineering，不是主線整合或Host資格。H10F closure34／
23d0d794精確Grant已派原Luna席位，2CREATE+2最小B2 validator重用；C11在
原票準備共用checked-release遷移，避免目錄再複製檔案的資源生命週期程式。
不增加勾選；30B／43、真issuer正向、原生攔截與全部必要資格仍開放。

額度中斷後沿原批次接續：H10E closure33／Grantcc5861d2兩CREATE由原作者
實作；C10候選7300d83b經Root實測抓出跨寫入fileidentity漏驗與native close
結果未確認，原票原席位按65c81e0f／05f230a4修正F1/F2，尚未整合。
SafeFileHandle sealed的編譯失敗保留為測試工具失敗，不當成產品反例。
補充source helper派送遭agent thread limit，未重試或換席位規避。下一個
installed owner/DACL缺口已從固定來源窄查，不增加平行系統或提前發Grant。
證據見原30 review頂段；正式Host／issuer／30B／43及本清單未完成項維持開放。

H10D最終a027765b來源獨審PASS，234guarded tests／strict4、Root不同registry門
具名紅→精確還原綠；3a4572ba封存3筆可取得raw（舊失敗原輸出缺口明列UNKNOWN，
不偽造）。精確組合21ddef2a兩CREATE、原48路徑不變／總50，組合234tests／strict4
及另一席mapping/archive PASS。只完成source engineering staging，30B／43資格
及整批驗收仍未完成。C10原席位五路徑仍實作中，不讀未提交候選或先勾完成。

原票30 closure31 H10D19c2b34b（D01文字衝突已獨審修正）及closure32 C10
29a90ffd均DOC_PASS。Root依原批次分別核發0363eda9／5892c5c0精確source Grant，
Luna原席位在互斥worktree實作：H10D兩CREATE只做成功程序exit-proof收尾，
C10三CREATE／兩fake wiring MODIFY只做核准payload新檔保護建立；普通既有
constructor預查2PASS／.NET10.0.302離線build零W/E與fake self-test通過。
新功能仍IMPLEMENTING，沒有勾選或Host資格。補充只讀派送一次遭平台
agent thread limit reached；不重試、不換席位，先接現有兩作者回件。

H10C最終04667fcb經Root275tests／strict4、雙收集順序及不同final-PID突變
紅→精確還原綠；629d1266封存19筆raw與Grant10。精確組合63d44d47僅兩MOD，
兩blob與受審版本完全相同，其餘46／48路徑未變；組合275tests／strict4再次通過，
不同席位SOURCE_MAPPING_PASS及19筆archive byte/hash PASS。錯誤重複context搬移
在提交前被blob檢查攔下並精確還原，非產品修正。證據在原30 review頂段；
原生／Host資格、可信issuer正向驗收及30B／43仍未完成，不新增勾選。
下一步沿原票定界成功建立程序的有限收尾，不另建Runner或冒稱可正式resume。

C6／H1／H2-A／C7已封存工程證據沿用，不重跑。H2-B a4a3d23c完成純peer／
record比對，Root274tests／strict3、不同門disposition突變紅→綠，來源獨審與
完整raw封存a0fa8996；原輸出缺口、既有pytest cache殘留仍保留，不冒充清理。
H3 factory修正兩個已重現缺陷（unsigned sentinel、原生state tuple），最終
8b0402通過Root289tests／strict2、owner-defaulted不同門紅→綠；作者十組完整
traceback紅→還原綠及原始記錄封存d38188d3，另一席只解碼資料驗證hash／內容。
CRLF/LF與多31項ledger的計數差異已實算核對，不是測錯版本。無Host資格。

H4最終37410685補下移native fake，Root152tests／strict2、不同OpenAsSelf門
紅→精確還原綠，來源獨審與完整作者raw封存0653eb35；三份資料解碼hash另席
驗證。舊selector ZERO_RED與owner-loss原始失敗仍在，不是Host資格。
H5原closure18兩檔owning pipe交接：A最終474e67c1，Root112H1／H3 patched
tests及strict2通過，不同錯owner交叉綁定具名紅→還原綠。原weakref NoneisNone
假綠已修成獨立非空／identity／lifetime斷言。B最終18bf1e9f，Root136H1／H3
guarded tests／strict2通過，cleanup-poison不同門三紅→精確還原三綠，來源獨審
與>500行責任檢視通過；五份原始作者raw封存b8fefab1、完整stdout讀回。
原guard／型別失敗不洗掉。H6closure20的A發現Close=17仍被Protocol當成合法，
cff4ee57限縮修正後Root62tests／strict2通過，membership-unavailable不同門
紅→還原綠，另一席複驗PASS；652e0e05接續同作者B。原報告聲稱四baseline紅，
實際raw三紅一綠，明確保留修正。B候選8c242768雖Root111tests／strict2綠，
獨審仍查出仿造owner通過與OpenProcessToken DLL錯綁；Root不同有效alias門
ZERO_RED暴露測試被invalid-zero條件遮蔽。原票d4385b68一次批次列三finding，
原作者同兩檔修正最終2ab6b93e；Root118guarded tests／strict2及不同thread門
具名紅→精確還原綠，另一席複驗PASS，2d347c21封存35原始JSONL、另一席
35/35完整byte/hash核對，三finding於來源層CLOSED。不把one-shot JSON／expected
值／強參照當成OS身份、獨占lease或Host資格，服務接線仍未完成。

無相依工作37沿原票修Dispatch normalization的WPR權威衝突，另修兩個已核准
規則的舊pin；最終80cc4484獨審／Root55tests／202subtests／strict2通過，
空行後偷加／重複職責也具名紅→還原綠。來源APPROVED、尚未整合或結案。
本票48檔／85,672,176bytes快取，精確一次Remove-Item遭CreateProcess政策
啟動前拒絕，已STOP、不重試／換方法。兩份抄錄因時間戳誤植保留區分，Root
查核與修正證據1eff888f，舊錯selector／失敗suite／逾時均保留。
其餘工作不被此清理阻塞拖住。原30N5 closure19最終969aa0ee，Root103tests／
strict2及initial-response status不同門紅→還原綠，另一席讀完整15原始突變
trace／來源PASS；84c3e18c封存21原JSON，另席讀回hash／byte相同。01patch輸入
UNKNOWN與五次多餘重跑保留，不捏造恢復。C8最終57812f34三MODIFY沿用原生
工具輸出actual觀察值；Root離線.NET10.0.302零warnings/errors，三fake selectors
通過，不同file_id門具名紅→精確還原／重建綠。另一席完整來源與四target突變
trace複驗PASS；efa2badc封存12原始JSON，另席byte/hash讀回PASS。舊verify介面
不變，非原子OS write／running image證據，不另造Framework。33精確blob來源
組合3f1a9f08通過Root328tests／strict4與另一席mapping PASS；H6修正後才於
876223b3精確加兩blob，組合環境118tests／strict2通過，35blob／其餘基準檔
完全相同、另一席mapping PASS。這是source engineering staging，不是正式整合。
原票closure22／Grant113841b3的N6最終47216919，僅既有fixture／test兩MOD；
Root133guarded tests／strict2與不同Transfer-Encoding門紅→精確還原綠，來源獨審
PASS、089413d4封存19原始檔，另一席逐檔byte／hash核對PASS。舊突變test SHA
UNKNOWN不偽造還原；記憶體connection fake不啟動socket，真CLI相容仍未證明。
closure23／Grant298e5897的H7-A最終82107c1c，原規劃windows_service.py兩型別
49tests／strict2通過，Root不同scope門兩紅→精確還原綠，另一席來源PASS。
H7-B最終2106b8de僅同兩檔有界decoder／共用JSON helper，Root74guardedtests／
strict2與不同Unicode改寫門具名紅→精確還原綠、另一席來源PASS；306b2f9d封存
43原始records及舊14record prefix，另一席byte/hash驗證PASS。d7ca3e9c精確組合
兩受審blob後同74／strict2綠、原35blob不變、另一席mapping PASS。不宣稱provider
SDK攔截或Host egress資格；沒有可達provider API，不新建mock框架充數。
原票closure24補服務持有原生job的實際producer，不拿已結束C# fixture JSON當live
handle。Root票面import方向筆誤在實作前由作者抓出，0c10315f同票修正／獨審通過。
H8-A最終10863edb兩型別／測試檔（唯一model）Root49／strict2及不同memory比對門
具名紅→精確還原綠；實測Literal[1]誤收bool/float已以exact-int validator修正。
舊突變raw缺source身份未冒充恢復；r03新實測補三門hash／patch／完整紅綠，另一席
複驗缺口CLOSED。87b485a2封存16可用原始檔並經另一席byte/hash核對，接續同作者B，
只建job owner／限制讀回／有限Close／Recovery保留，尚不啟動程序或Host。
H8-B checkpoint9b42277f的未知建立未poison／並行發布競態及10a52885的alias
中斷失去owner已同票修正；最終5260cfbc Root94guarded／strict2、四必要門與
不同expiry門均具名紅→精確還原綠，真實兩thread fake不再被常數thread遮蔽。
187ffaf2來源封存、86697add精確組合1ae18b76共39paths／另一席mapping通過。
舊四門raw缺口仍UNKNOWN，以新實測補證不冒充恢復；合法生命週期仍通過。
>500實際結構審查確認單一job責任／共用fixture，不因行數拆出框架。
H9另管primary token，不混入job責任。A最終b99943a9兩CREATE，
Root29guarded tests／strict2／不同frozen門紅→精確還原綠，另一席來源PASS。
e80ee98e封存12作者原始records，另一席byte／hash讀回PASS，接續同作者B限同
兩檔token取得／限制／讀回／持有的離線fake驗證。實際WTS所需LocalSystem／SeTcb
尚未授權；現有runbook虛擬帳戶提案不能被源碼或Grant暗中換成新權限。此差異
須列入後續完整操作包。B最終f22a5aed僅同兩檔，未知WTS與BaseException保留／
poison、owner metadata驗證三finding來源CLOSED；Root75guarded／strict2、不同
LUID門具名紅→還原綠，另一席來源及證據PASS。四門patch由固定Git重建且對上
原RED SHA/blob，明標事後推導，不冒充原capture；舊cleanup patch仍UNKNOWN，
另做一次有限新cleanup紅→還原綠補證。04ba5ff8封存四原始檔，另一席byte/hash
核對PASS。精確組合b605c88c只加兩blob，原39不變／共41paths；組合環境75與
strict2綠，另一席mapping PASS。Root首輪strict與暫時突變重疊不作來源證據，
還原後strict另驗通過；歷史未洗掉。
H10A原票closure26最終ab4ef426僅兩CREATE，重用H7 fixture／標準quoting；Root
117guarded／strict2、不同NUL門兩紅→還原綠。作者突變使用較早test snapshot，
未冒充final；Root只補三組final test bytes具名紅→還原綠，不重跑無關suite。
來源與完整證據獨審PASS，b0051427封存三原始檔／另一席byte/hash通過。
精確組合00a9c90d只加兩blob，原41不變／共43paths；組合H10限定43tests及
strict2通過／另一席mapping PASS，不重跑H7。仍未啟動process或取得來源權威。
H10B1最終862f2089僅四既有檔修改，借用期間鎖定原owner／拒絕重入close；
Root實測200聚焦tests、strict4及實際載入來源通過，silent valid alias drift
不同門突變具名紅→精確還原綠，封存5ff96a1b；兩次作者ZERO_RED與早期型別
失敗照實保留，不洗成成功。精確組合beb7a463仍43paths，只替換四受審blob；
組合200tests／strict4通過，另一席資料byte/hash與mapping讀回PASS。B2原生
程序／thread保護與wide ABI原票closure28 bc192979文件複驗PASS，cf9c090f精確
兩CREATE准入。初候選0df6e061雖Root83聚焦tests／strict2通過，Root另實測
Recovery owner仍可取handle、重入Close造成兩次native呼叫，readonly保護被刪
負例仍綠；另有未具名state及range diff格式缺陷。6f75347d一次列出F1–F3／
E4–E5。最終f377e16f同兩檔修復，Root91guarded／strict2及原lifecycle probe全綠，
不同雙Close registry門具名紅→精確還原綠；另一席source／七final-byte pairs通過，
26867c76封存52原始檔並經另一席byte/hash核對。舊capture失敗／baseline誤標／
restore順序錯誤完整保留，不用新證據冒充修復舊raw。精確組合c1b60946僅加兩
blob、原43不變／共45paths，組合91／strict2綠，另一席mapping PASS。後續只在
H6 process reader辨識新owner，原票closure30 d06afcb7文件預審PASS；86e0891e
兩既有檔MODIFY精確Grant與fresh worktree/context准入，原作者實作中。H9共用
token／job helper不放寬。失敗不得把CloseHandle當termination，部分輸出保留
Recovery；不把純DTO當可信來源或隔離資格。獨立C9原票closure29 1035210e
僅三CREATE／兩MODIFY，新owned目錄creation-time保護工具初候選72309824
離線build綠，但Root查到例外誤判exists與DATA策略ZERO_RED。0e35ed59修正後
E2已閉合，F1跨層identity drift→later MISSING仍會降成clean refusal；Root
具名RED證實、精確還原。最終20639b8b同F1修復，Root離線build／fake self-test
綠，final postguard移除時183／80／一般拒絕三格同輪具名紅→精確還原綠，
不同DATA門final test也具名紅→還原綠。ec9e4eb1來源封存五原始檔，另一席
byte/hash讀回PASS；作者舊mutant SHA缺失仍DERIVED，不冒充恢復。精確組合
6c825a01三CREATE／兩MODIFY五blob相同，原45中兩檔按授權修改、其餘43不變，
共48paths。提交後.NET build零warning/error與fake self-test通過，SDK Git
版本metadata／DLL SHA明確讀回，另一席mapping PASS，不等於main整合。作者
初稱log prefix改變，直接byte與另一席核對證明原44613bytes／55797ef9仍完整；
13新record重複與錯誤hash觀察原因UNKNOWN，保留不重寫／不重跑舊七對。
以上仍僅offline fake驗證，不是Host資格。既有ACL覆寫／unsafe rollback
方案已撤回，沒有實作／效應授權。額度中斷後沿原Grant／worktree接續，
沒有重做04、重置舊帳或變更主線。額外唯讀helper續接回覆agent thread limit
reached，保留具體失敗、不原樣重試或繞路增派；Root自行準備必要後續。
01–12勾選維持原狀，真實Host及正式效應仍未驗收。
不新增Resolver／Gate／Runner；未啟動CLI／模型或實際Host，來源成果不冒充原生派送。

CVQ最終24c79d22在原lineage完成E01–E04同票修正。Root實際34行為tests、
202來源正反例、24檔strict、source graph及compile/import通過；公開outcome
join被刪除時具名紅→還原綠，合法pure與HostDiscovery注入案例仍可通過。
另一席來源窄複驗PASS，原CVQreview23／seal7d157e23保存精確blob與raw。
這是SOURCE_BEHAVIOR_STAGED_PASS／QUALIFIED_REVIEW_BLOCKED，不是實際Host
通過。舊default-pytest範圍／副作用UNKNOWN、逾時與Recovery不因新綠燈解除。

01–12勾選不變、04不重做；正式source／issuer／Host效應與30B／43尚未驗收。
沒有push／release／deploy／安裝／主機安全設定或正式閘門啟用。
本段先前revision由Git保留，不為相同進度重複堆疊另一份正文。

## 前次工程接續與精確證據（revision49歷史）

C5修正181d0dae只加32行原測試，產品blob28d3049d不變；Root實際hash-only／
size-only copy各具名紅→精確還原重建綠，獨立席source複驗，原30review封存
fe51585a。原ZERO_RED保留為已修正證據缺陷，不加入B2比較／拒絕。工程
staging合併B2與C5為51dc502f，三個B2與四個C5相關blob精確相同，offline
strict／default／enrollment通過；未採用至main，不是正式資格。C6原票closure12
接線既有parser／reader／verifier，精確六路徑先行文件審閱，沒有新框架或PRD。

CVQ behavior候選c258bbe8原31tests綠，但Root公開入口重現pure錯收RECOVERY_REQUIRED
與合法HostDiscovery錯拒；不同席source確認。同票doc16／closure06只准MODIFY
report與兩個原測試，獨立DOC PASS後4db46118啟用原作者修正，不重問SPEC。
原default pytest意外執行範圍／副作用UNKNOWN仍保留，沒有以後續測試洗成PASS。
所有勾選狀態不變，04不重跑；30B／43及Host／正式source／effect仍未驗收。

## 前次工程接續與精確證據（revision48歷史）

N4-A1最終5449c063：Root98tests／strict3files／memory compile、候選實際import、
獨立literal合法positive與bytearray拒絕通過。Root不同門改壞header endian，兩具名
positive轉紅→精確還原綠；作者unknown欄位突變舊raw遭截斷仍缺失，Root另做全新
6具名紅→還原6綠並封存完整輸出，不冒充恢復舊紀錄。原30review封存74fd796a，
不同席source PASS；depth負例與unknown欄位重疊，沒有宣稱獨立證明depth謂詞。
此為3MODIFY來源工程staging，不是可信Grant／服務或Host資格，仍未正式整合。

同票C5 closure11／74fd796a已接續原作者：只CREATE2／MODIFY2，沿用既有readback
型別、C4 CodeRoot與C2 configuration reader，不掃可變DataRoot ledger／evidence。
原票605c18b9獨立DOC PASS；Root新鮮8a24／隔離WT／角色／正常constructor讀回通過。
實際基準不含另一條hold分支的F1共用builder（77ce25），f2da6b09僅更正驗證綁定：
不得用會嘗試os.symlink的舊physical fixture；直接offline dotnet介面，不新增腳本。
CVQ behavior仍在實作／局部驗證；一次空node清單意外啟動default pytest已止住，
原退出／完整測試範圍與可能副作用仍UNKNOWN，獨立後讀回只有該PID／PPID不存在。
該事件見CVQ schema review16／3841cf92，不算PASS；後續具名受控實跑獨立記帳。
04不重跑，其他原項與30B／43資格hold不變；無Host資格測試／安裝／權限／推送／發布。

## 前次工程接續與精確證據（revision47歷史）

C4最終8a24b9eb：初稿兩個volume ZERO_RED保留，原作者僅補18行既有測試。
Root獨立非增量build、default／真實owned fixture、直接載入候選DLL與literal7物件／
44bytes通過；全域file-volume及重讀directory-volume兩謂詞各具名紅→精確還原綠。
原Root不同門immediate-child突變證據沿用，獨立席窄複驗PASS，原30review封存468e9c6b。
這僅來源工程staging，不是Host／保護來源資格；未整合、不勾選總項、不清理hold。

接續已有DOC PASS的同票N4-A1 closure10，只MODIFY既有client／export／protocol test
三路徑、零CREATE／DELETE；重用bounded frame parser，不造service／DTO佔位框架。
Root2388e2讀回兩個隔離worktree exact20bd、乾淨／non-reparse／Git綁定、正常request
constructor／wire roundtrip及既有61tests通過；d6c7d288啟用限縮Grant後接續原實作者。
完整CVQ behavior closure06另席在已驗證constructor基準6f392ec4建置，原票doc15／
Grant啟用f276218e；尚未收到不可變候選，不列為完成或Host證據。30B／43保持hold。
這輪沒有Host測試、安裝、權限設定、push／release／deployment；01–12狀態不變。

## 前次工程接續與精確證據（revision46歷史）

本次精確Owner決策已啟用CVQ SPEC10§15／wire06§10，提案92e28d33與獨審
54a6b35f不重問；簽章版11／07在CVQcontrol00528cb9，沒有改既有隔離不變量。
新constructor初稿5f7ae38b雖有45tests綠，Root仍查出必填欄位被錯設預設值，
同票6f392ec4修正；獨立來源席複驗、Root45tests／2605subtests、strict18files、
compile/import與不同property-origin及required-default實際謂詞紅→精確還原綠。
完整port方法新實跑1test／11subtests，舊55s逾時及作者原始輸出缺失未冒充通過。
證據在CVQ原schema review14／seal09ab5ec5；只SOURCE_SCHEMA_PREFLIGHT_PASS，
原票behavior closure06已準備ac87669b，尚不代表完整CaseResult驗證或真實Host通過。

C3初稿2f6b3fd5被Root查出兩個ZERO_RED，原作者同票7b2184df只修三檔；Root實際
native後頁錯誤、volume、size三門各自具名紅→精確還原／非增量重建綠，131物件
合法positive與literalhash／size、實際DLL載入來源均通過，獨立席窄複驗PASS。
原30review／seal5c19eee0，E01/E02只在來源工程層關閉，未整合／未qualified。
接續同票C4 closure09只CREATE2／MODIFY2，重用C3與B1完成全樹有界組合；
DOC PASS及新鮮7b／角色／Git綁定後bd505245准入派原作者，不等待Owner重批。
fixture先登記owner／TTL／teardown後才建立，7物件／44bytes，既有hold不清除。
30B／43、真實保護來源、隔離資格及effect驗收仍開放，01–12勾選狀態不變；
只有04已完成。沒有Host測試、安裝、ACL／帳號／服務變更、push或發布。

## 前次工程接續與精確證據（revision45歷史）

同票F1最終7fa12f0c已把共用候選build與實體fixture拆開，預設零symlink探測，
非真實reparse/denied/fault仍標INJECTED。獨審發現DLL綁定oracle退化後，原作者
同票補實際fixture建構的獨立預期斷言；Root9項聚焦實跑、strict與import通過，
另改壞真builder非增量選項具名紅→精確還原綠，原獨審複驗E01關閉。seal eb5507d0
及無損raw JSON格式修正d58ebc70，前次Root cp950缺輸出仍UNVERIFIED、不冒充PASS。
這僅SOURCE_TEST_INFRA_ENGINEERING_STAGED_PASS，未整合、不提升Host資格。

C2最終b42ae444沿原CREATE2/MODIFY4，closure07／Grant revision02經DOC PASS與
Root9ff8cca3精確啟用。Root實跑獨立4097／196625-byte Expected、現有writer拒絕、
missing／directory／empty／oversize與exclusive reopen，原兩個zero-red各已具名紅→
精確還原綠，原獨審窄複驗E01–E03關閉，seal c5d98249。strict／compile／import及
N1實際getter通過，歷史缺輸出與失敗保留。這僅SOURCE_FILE_READBACK_ENGINEERING_STAGED_PASS，
不是保護來源或Host資格，未整合。接續同票有界封閉目錄讀回建置，不重做已關閉C2或04。
F1與C2不同worktree，沒有自動混入彼此改動。
01–12勾選狀態不變；原生服務/保護安裝與完整來源/資格/Host效應仍未完成。

## 前次工程接續與精確證據（revision43歷史）

N3B2最終bf5a4a3c：純比對具合法正例；Root實際code-payload／namespace與不同門
DACL謂詞轉紅、精確還原綠，獨立席窄複驗通過。原zero-red及修正沿用，工程seal
3c87ef77；未整合、非Host資格。C1類別移動cee79331：8,078 bytes／class digest
等價，Root新執行同fixture基準→候選實際getter JSON一致；搬移後不同原生謂詞
轉紅→還原綠，另一席核對無finding，seal283dd8c9。作者歷史命令缺口仍UNVERIFIED，
沒有用新重跑冒充舊證據。兩切片僅SOURCE_ENGINEERING_STAGED_PASS。
下一步是沿原票補同handle讀回能力，不把已關閉純比對或04重做；實際Host／可信
來源／資格及正式整合仍未具備。全部12項勾選狀態不變。

## 前次工程接續與精確證據（revision42歷史）

N3B1最終3b2da4b0已完成建構preflight：來源181行／既有入口只加一行接線，
讀回測試獨立責任檔，沿用同一typed fixture及builder，沒有新框架。Root具名
root-kind／failed-metadata實際謂詞紅→精確還原綠，另走作者不同的data-count門
紅→綠；兩個zero-red舊紀錄及作者修正保留，獨立席窄複驗無finding。seal d7f5e7cc。
這只提供immutable observations/result constructors，沒有把MATCH DTO當實際比對通過。

同票B2純比對MODIFY3／CREATE0獨立DOC PASS 4a2e2e28，Root已讀回精確3b2基準、
Grant／角色／worktree後513b25ad派原作者；不等Owner重批一般工程。重用ProtectionPlan
導出檔案DACL，保留原N1輸出，純合法正例及權限／hash／inventory負例獨審後才收。
原生reader、服務安裝、Host campaign與正式來源資格均尚未完成或啟用。

CVQ新增input/full-case provenance契約差異已一次提出精確SPEC核准包，並非重問已
批准readonly設計／秒數；等待此項不阻塞B2本地工作。所有01–12必要驗收狀態不變。

## 前次工程接續與精確證據（revision41歷史）

N2最終候選1e6847c9（不是沿用舊binary）完成J1–J5來源工程seal：作者kill-on-close
及Root不同門readback-equality具名紅→精確還原綠，另一席窄複驗。Root最後固定
fixture於實際EXE/DLL雙digest釘選後5.343秒通過，原始JSON／命令在377f24ed與
原30review。保留全部失敗、J3 UNKNOWN及Recovery，沒有宣稱正式Host或來源合格。

N3A最終cb877f73建構preflight完成；產品blob6cac5030、Root strict PASS。
原five zero-red及自我roundtrip漏測都保留；原作者只修既有測試的獨立Expected，
Root實際五個guard及不同counting-stream門均紅→還原綠，最後digest writer也
具名紅→精確還原／非增量重建綠，另一席只讀複驗PASS。證據e7760267／原30review。
這是constructor/parser來源工程，不是B verifier、protected issuer或Host資格。

CVQ Phase A7da40704不重做；現有port確實缺少入口input與完整CaseResult的可信
來源證據，最小SPEC10／wire06提案92e28d33已不同席DOC_PASS，seal54a6b35f。
既有SPEC09／wire05仍有效，只有新增public port/fail-stop/full-result差異待精確
正式核准；不當成已批准或全部拒絕的功能完成，也不阻塞N3等獨立本地工作。

沒有新增完成勾選；以下revision40的狀態為歷史快照，不取代上表必要驗收。

## 前次工程接續與精確證據（revision40歷史）

CVQ唯讀schema候選7da40704已完成來源建構preflight；Root33個實際謂詞突變中
兩個zero-red測試缺口已由原作者同票補回，Root／另一席窄複驗通過。review06
與D8索引在CVQcontrol67b965a7，僅SOURCE_SCHEMA_PREFLIGHT_PASS，behavior尚未
准入。現有Found approval／三ports沒有能綁定入口拒絕的可信evidence subject，
原契約修訂評估中；不拿request_ref、caller欄位或fixture假造拒絕證據來源。

N2候選e84333eb同票修正B1～B6；Root實際謂詞紅→精確還原／非增量重建綠，
獨立席位窄複驗無finding。Root一次固定原生fixture通過正常／child1816拒絕／
timeout／cancel／故障注入，5.312秒，完整輸出及精確EXE／DLL見原30review。
原生失敗紀錄、J3歷史UNKNOWN、RecoveryRequired與未合格audit全部保留。
此為SOURCE_ENGINEERING_OBSERVED_FIXTURE_PASS，不是Host qualified或已整合。
修掉原始碼還原仍載入增量舊DLL的B5，既有builder強制--no-incremental且有
命令／輸出binding測試；這不是05完整Host loaded-source驗收，故不勾選。

N3 constructor最小切片原30內準備且不同席DOC複驗PASS a64fb8da，已派原作者
到獨立contained worktree，只CREATE2/MODIFY3且無OS/effect；配置檔DataRoot、
程式及dependency CodeRoot，修掉與runbook衝突。B verifier/readback尚未派工。
全部主項狀態仍依上表，只有04打勾；不把工程fixture或一般獨審當正式資格。

## 前次工程接續與精確證據（revision39歷史）

B3同名Field缺陷已在b55b47e7修復，只有既有gate/driver兩檔修改；作者Luna、
不同Sol evidence peer與Root分工。合法Pydantic別名仍綠，直接／巢狀shadow與
rebound拒絕，失敗反例保留。Root跑38既有constructor/domain tests全綠；接受A
的product/tests/catalog/fixtures與485d882f空diff，沒有重做04或歷史A突變。
Root完成20實際predicate紅→精確還原綠（SG19真正graph-edge另補，原consumer
wiring只算附加證據）、缺annotation、rebound/else/after-branch、computed facade，
171negative／31positive corpus移除判別及實際unused renamed forbidden import。
原review18／B3doc15與D8在CVQcontrol4873ebf8；獨立DOC窄複驗PASS。
結論只SOURCE_ENGINEERING_STAGED_PASS，qualified review／integration仍blocked。

同一批次內已把原CVQ-01編成doc11／closure04 constructor successor at0508be61：
重用6既有product檔、8既有tests、1source policy，CREATE0；原3ports／roster／
prerequisite contracts及symbols/gate/corpus不動。只建核准readonly wire delta，
不把純constructor說成evaluator／真Host通過；精確Grant待不同席DOC與新鮮綁定。

原生N2 PhaseA39f23b85被獨審F-N2-A1拒收：Assign失敗時Job不能終止尚未加入的
suspended process。原作者同票eeb2eaaa補exact-process-handle termination與
partial-create Recovery result；Root不同席建構複驗PASS，記dafb5391，未執行
Job/Host。為避免405行values再混入OSadapter與lifecycle，原Grant revision02
於200900dd精確增加NativeJobContracts.cs／WindowsJobPort.cs；獨立DOC PASS，
共5CREATE/3MODIFY，仍原Ticket30與原baseline，無新framework或權限。作者正按
原J1–J5建有界owned native fixture，非真Codex/Claude Host或隔離資格。

30B／43、合法正式Grant正向、protected issuer/observer、實際Host qualification
及正式來源／effect驗收仍OPEN。這是持續建置進度，不是剩餘項全部外部blocked
的結論；沒有新增完成勾選，也沒有Host安全設定、push、release或deployment。

## 有效本地授權修訂（revision38）

Owner明確取代原本按票／角色累計命令秒數與固定初次加一次修正限制，涵蓋30B／30G／
B3原F01；不採前次500秒提案、不再用舊上限要求續准。舊帳、失敗、偏差、UNKNOWN／
UNRECONCILED及未解Finding全部保留，持續計時而非歸零。相關既有治理reference、
原票30／registry及CVQ原B3票／registry同步綁定此次決策並獨立核對。
單次逾時、程序／資產監控仍有效；同失敗無新證據不原樣重試，改RCA或有依據的修法。
沒有取消來源／Grant／Review／Host qualification、平台限制或安全閘門，沒有付費擴容。
已重現Field缺陷優先實作；其他已准入本地原生工具／觀察能力接續，不以進度回報停工。
本節不新增完成勾選；01～12仍依各自實作、驗證、獨審及必要資格證據判定。

## 本輪原生工具與CVQ實際驗證（revision37歷史）

N1九檔工程證據如下保留，未重做04，也未將任何其他主項假勾。
CVQ舊指向已改讀可信control55b9a91c、既有修復候選2e889401；沒有重派已回件F01。
Root在原CVQ票doc11／163bf203綁定本批首次入口工程暫存例外，獨立文件preflightPASS；
當前結果封存在75d165b5e3b9e4e26b8b36af240d218b06447f4f：B3doc12／review16，
LF分別6cdd1882d379b02386b211de490173d4b41760bd63b63e1d48b77c21b58e7930、
09411689d3e622bae0e407163ab1a98ec4147005b69d228e77dbc590df57bb9b。
不同席文件複驗PASS（0.725s）；只證明紀錄／digest一致，不是合格隔離或程式PASS。

實際補齊strict21綠；20個具名rule-owner wiring反向突變紅→還原綠、三個額外必經門，
真實nine-source packet的unused renamed forbidden import拒絕→原packet綠。
campaign12.9977218秒，原始輸出未縮減，磁碟source未改。這不是20個內部謂詞各自完整證明。
strict命令完整非同步耗時未instrument，記UNVERIFIED，不拿poll等待總和冒充原始時間。
未變的A測試／fixture／catalog／product及間接imports獨立核對後沿用原證據，不重跑整批。

普通獨立peer又找到F01 schema callable identity漏口；Root用REAL PositiveInteger alias
加同名typed helper Field重現inspect_sources回空，4.4530727秒，packet沒有執行。
**這是失敗反例，不是綠燈**。B3 CHANGES_REQUESTED／CONVERGENCE_REVIEW_REQUIRED；
其餘final F01/nonvacuity/full-boundary campaign未跑，不在已知錯誤候選上燒預算。
單次續修額度已消耗，不自動再派；F02/F03/F04及原A證據不重審。資格hold仍獨立存在。

原有各項剩餘驗收仍如下表及既有逐項依賴矩陣，沒有新增Agent、Gate或第二套框架。
N2作者可用26.23不足45；Reviewer累計183.407/220；Root330保守保留含UNRECONCILED舊帳，
不假稱330全為量測耗時。新增500／B3一次限縮修正窗口只是合併提案，NOT_GRANTED；
精確角色分配、四個source切片、後續資格路徑和可直接回覆文字見原[runbook](runbooks/grant-and-readonly-host-implementation.md#consolidated-remaining-source-decision--proposal-not_granted)。
不要求現在核准尚未建好的安全設定；服務payload／protected observer未建妥就不能提出假執行包。

## 原生工具局部工程證據（revision36歷史，N1結果沿用）

原票30N1沿原需求與同一Grant完成九個CREATE，候選
`0a2e0661eef741be1b9df103ae8874c284cf60f8`／tree
`9774ca07aad0048d9d9a092ab73f4206c88a421e`。作者Luna、不同Sol席位獨審；
Root只做控制文件。原生強型別manifest/整份DACL計畫、readonly owner/DACL/
volume/file identity及真實候選CLI四個聚焦tests通過，strict mypy/in-memory compile通過。
作者pipe-mask source mutation紅→精確還原綠；獨審實際getter-success source mutation
`MISSING/exit1`→精確還原重建`OBSERVED/exit0`。兩輪既有finding均有修正/複驗；
不是單憑編譯、自述或測試物件突變。完整命令、未縮減輸出及不同build hashes見
[原票30 review](reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md)。

這是SOURCE_ENGINEERING_PASS，不是qualified audit/正式整合/Host資格/可信issuer。
真實reparse fixture遇1314，該負例及denied/native fault是明示INJECTED；不得假勾。
九檔與fixtures保留QUALIFIED_REVIEW_HOLD，不改Recovery、不重試舊清理。只有04維持勾選。
原帳599.2、角色舊帳161/84及Root舊時間UNRECONCILED/reserve200保留；N1累計作者132.77、
reviewer94.523，不重置。N2票面已獨審但NOT_GRANTED：保留old30G correction30後，
作者可用26.23小於規劃45；不是平台額度不足或總1500已耗盡。

來源窄查另確認CVQ control55b9a91c已有B3修復候選2e889401，而不是runbook舊指向27bb。
原B3document10/section14與review15/section19保留strict結果UNVERIFIED、最終campaign及
qualified audit缺口；不重派作者修已回件的F01，不借用舊PASS或普通subagent冒充資格。

## 本批剩餘限制與接續邊界（revision31歷史；最新判定見上節及後續記錄）

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
