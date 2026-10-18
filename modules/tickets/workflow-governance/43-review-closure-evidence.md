# 43｜既有 Review 入口的候選結案證據

| 欄位 | 綁定 |
| --- | --- |
| State / Closure | `ENGINEERING_PASS / REVIEW_BLOCKED` / `43-C1–C4 revision02`；缺mandatory qualified Host audit，候選未整合、不重派修已通過code |
| Authority | Owner `batch-checklist-local-20261018`，既有 checklist07／09／12；原 PRD-20260805-009／CHG-20260805-009／SPEC workflow-governance revision03 AC11 Required replay #3 |
| Grant | Root delegated `grant-wg43-closure-local-20261018`；下列範圍內本地建置／測試／獨審，無新外部權限 |
| Baseline | Source `930fad32e15a76cd54423e34ea941a630af039da`；實作起點取本票／registry已提交且獨審通過之文件commit，Root先讀回並確認source blobs未變 |
| Owner / reviewer | Root control；`/root/review_closure_impl`，當下可用gpt-6-luna/xhigh；不同席 `/root/review_closure_review` gpt-6-sol/high；模型只屬本票分配資料 |
| Workspace | `.worktrees/skill-improvement-43-closure` / `codex/skill-improvement-43-closure`；獨審另用 `.worktrees/skill-improvement-43-review`，建立時核對Git/非reparse/clean/containment |
| Profile / budget | HIGH_ASSURANCE（正式Review的授權邊界）；本票命令累計上限300s、單命令90s；一次initial+一次correction，保留耗用，不以拆票重置；network=0、外部模型API=0、作者helper=0 |
| Scope | 下方五個既有檔；create/delete=none。原測試不能刪、不能降低Expected；其他專案與正式啟用不在範圍 |

```johnny-boundary
modify = library/workflow_router/test_engineer_contracts.py
modify = library/workflow_router/review_admission.py
modify = library/workflow_router/router.py
modify = tests/test_review_admission.py
modify = tests/test_router_review_admission.py
forbid = doc/
forbid = modules/
forbid = skills/
forbid = template/
forbid = library/local_orchestration/
```

## 既有重用、唯一責任與輸入輸出

重用現有 TestBinding／TestReviewAuthority／TestCellObservation／TestVerdict、
TestEvidenceResolver及ReviewAdmissionGate；Router已有REVIEW→HANDOFF同一入口。
不造新Resolver、Router、狀態機或新檔。source qualification仍由現有注入來源承擔；
本票用明標fake resolver驗確定性消費，不把port自報當真Host觀察。

目前入口只驗測試報告，不能證明結案時必要子項／blocking Finding已完成。本票在
同一resolved evidence加入最小closure metadata，將「進入review」與「review完成」
用request的 `require_closure: bool = False` 區分；Router只在實際REVIEW→HANDOFF
設True，任何其他review入口仍用原契約。不是新流程階段。

在既有test_engineer_contracts定義最小具名資料，不將測試PASS視為票級完成：

- `ChildClosureBinding`：child_ref（OpaqueMetadataId）、candidate_sha（CandidateSha）、
  closure_revision（RevisionDigest）。
- `ChildClosureObservation`：binding、verdict（重用ReviewTicketVerdict）、evidence_ref／
  evidence_digest。只有APPROVED才可支持child完成，不能接受TestCellObservation。
- `FindingClosureObservation`：finding_id、disposition（Literal OPEN/CLOSED）、
  evidence_ref／evidence_digest；不能自行改成optional或out-of-scope逃避既有finding。
- `ReviewClosureEvidence`：candidate_sha、reviewer_id、closure_revision、review_verdict、
  required_children／dependencies（各tuple[ChildClosureObservation,...]）、findings
  （tuple[FindingClosureObservation,...]）、evidence_ref／evidence_digest。

既有TestReviewAuthority新增closure_revision=None、required_children=()及
required_dependencies=()（各tuple[ChildClosureBinding,...]）、blocking_finding_ids=()。
全部集合IDs須唯一；child/dependency相同ID必須同版本，不可相互掩蓋。
ResolvedTestEvidence新增closure_evidence=None。舊資料仍可入review，但不能以缺少
closure資料完成handoff。Expected children/dependencies/finding集合來自現有可信resolver
讀回的authority，觀測不能任意省略；每個觀測必須有逐項evidence ref/digest且由resolver
確認可讀與版本。正式source qualification未證明時只能UNAVAILABLE，本地fake不升格。

AC-by-AC沿用現有authority.expected_cell_ids、approved_expected及report.cells逐項
identity/ref/digest/loadedcandidate的驗證，不另建重複AC集合；resolver必須回完整核准
集合及可讀證據，缺一cell不得通過。Optional children不在required集合，不把它們加入
阻塞集合，也不能拿來補缺少required；如另有optional工作，不輸入此必要閉包。

同一gate在require_closure時要求：closure存在、authority revision存在且相符、
candidate等於binding.candidate且既有observed loaded source檢查仍通過、reviewer
等於binding.reviewer且既有三角色隔離仍有效、verdict為APPROVED、required child及
dependency的binding精確覆蓋且全部APPROVED、finding IDs精確覆蓋且全部CLOSED、
各項evidence ref/digest合法。缺證據、
錯配或非PASS使用既有DENIED及最少必要具名reason；不自動改Finding、補核准或
關閉Ticket。可信讀回不可用時現有resolver必須回UNAVAILABLE。

## 有限驗收與實作順序

- 43-C1：正常constructor／roundtrip／strict拒絕錯primitive、未知enum、重複child／
  finding、空證據；只建上述型別和純建構測試，獨審pin後才接gate與Router。
- 43-C2：原review entry合法資料繼續通過；同報告缺closure不能REVIEW→HANDOFF；
  完整精確candidate／reviewer／revision／children／evidence才可走原handoff。
- 43-C3：參數化負例涵蓋錯candidate、作者冒充reviewer、stale revision、漏child、
  child未APPROVED但測試PASS、錯child版本、漏dependency、漏finding或OPEN finding、
  漏AC cell及來源unavailable。非必要
  工作不在required清單，不得因此攔住合法結案。沒有自報N/A豁免必要測試的欄位。
- 43-C4：Root及獨審確認實際Router路徑、既有consumer／回歸；作者至少改壞child
  reducer轉紅→還原；reviewer另改require_closure接線或reviewer比對轉紅→還原。
  Expected為票面固定值，不能從Actual產生；候選載入位置必須是作者worktree。

固定拒絕矩陣（保持原驗證先執行，再依此順序；多錯同現命中第一項）：
closure/authority revision缺失→CLOSURE_UNAVAILABLE；父candidate/reviewer/revision
錯配→CLOSURE_BINDING_MISMATCH；review verdict非APPROVED→CLOSURE_NOT_APPROVED；
child/dependency集合或binding錯配→CLOSURE_CHILD_MISMATCH；child/dependency
非APPROVED→CLOSURE_CHILD_INCOMPLETE；finding集合錯配→CLOSURE_FINDING_MISMATCH；
任一OPEN→CLOSURE_FINDING_OPEN。新reason的verdict固定BLOCKED，status DENIED；
原source/report/AC錯配沿用原reason／verdict，不用新reason遮蔽它們。
非法primitive／重複ID／空evidence由普通constructor拒絕，resolver傳非法物件依原
RESOLVER_FAILURE；無有效resolver沿原EVIDENCE_UNAVAILABLE。不新增Router狀態。

預期增量產品≤150行／測試≤180行，是結構審查訊號，不強制拆檔／壓縮。既有
test helpers沿用，禁止獨立大腳本。此為新增缺失驗證，非責任搬移，TEST→A→B
為N/A；新型別建構再接行為順序仍須保留。

Commands：`python -m pytest tests/test_review_admission.py tests/test_router_review_admission.py -q`；
`python -m mypy --strict library/workflow_router/test_engineer_contracts.py library/workflow_router/review_admission.py library/workflow_router/router.py`；
compile/import上述三模組、`git diff --check`；有實際consumer失敗才擴大相關回歸。
禁stress／背景輪詢／paidcalls。Review必需candidate-bound AdversarialReviewPlan：
SPEC_GAP／STATE_TRANSITION／AUTHORIZATION／REGRESSION；NO_EXTERNAL_EFFECT；
缺少已qualified read-only isolation維持REVIEW_BLOCKED，不把prompt當證明。

Return：IMPLEMENTED/BLOCKED/CHANGE_DETECTED、candidate、baseline、paths、cells、
命令結果/累計秒數、findings、deviations、未驗證項。作者只commit自己worktree，
不能整合/自核准；Root既有document mutation gate本地整合。Asset owner=具名席，
TTL=review與evidence seal後，僅精確已整合乾淨worktree/ref可teardown，Recovery保留。
不push、不部署、不正式啟用Host；本票不宣稱完成整項07／09或清單12。

## 結果

候選`d477020e0fb010ea12d610e3588630284472ecf8`，獨審ENGINEERING_PASS：
19tests/58subtests、strict3modules通過，作者child-binding與reviewer identity
兩門突變紅→精確還原。必要HIGH_ASSURANCE隔離audit仍UNAVAILABLE，最終BLOCKED。
不整合、不刪作者／review工作樹、不重跑已證明的code；其他合法本地工作繼續。
完整證據在 `doc/reviews/workflow-governance/43-review-closure-evidence-code-review.md`。
