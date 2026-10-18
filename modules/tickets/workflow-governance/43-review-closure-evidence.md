# 43｜既有 Review 入口的候選結案證據

| 欄位 | 綁定 |
| --- | --- |
| State / Closure | `BUILD_ADMITTED_AFTER_DOCUMENT_REVIEW` / `43-C1–C4 revision01`；不聲稱真Host／來源已合格 |
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

在既有test_engineer_contracts新增單一具名 `ReviewClosureEvidence`，含
candidate_sha、reviewer_id、closure_revision（RevisionDigest）、review_verdict
（重用review_inbox_contracts.ReviewTicketVerdict）、required_children
（tuple[TestCellObservation,...]）、blocking_finding_ids（tuple[OpaqueMetadataId,...]）、
evidence_ref／evidence_digest。既有TestReviewAuthority新增可缺省的
closure_revision=None與required_child_ids=()，ResolvedTestEvidence新增
closure_evidence=None。舊資料仍可入review，但不能以缺少closure資料完成handoff。
Child IDs須唯一；不重造child狀態enum。必要child只有PASS可完成；optional children
不在authority的required集合，不能被加入該集合阻塞，也不能拿來補缺少的required。

同一gate在require_closure時要求：closure存在、authority revision存在且相符、
candidate等於binding.candidate且既有observed loaded source檢查仍通過、reviewer
等於binding.reviewer且既有三角色隔離仍有效、verdict為APPROVED、required child
IDs精確覆蓋且全部PASS、blocking findings空、evidence ref/digest合法。缺證據、
錯配或非PASS使用既有DENIED及最少必要具名reason；不自動改Finding、補核准或
關閉Ticket。可信讀回不可用時現有resolver必須回UNAVAILABLE。

## 有限驗收與實作順序

- 43-C1：正常constructor／roundtrip／strict拒絕錯primitive、未知enum、重複child／
  finding、空證據；只建上述型別和純建構測試，獨審pin後才接gate與Router。
- 43-C2：原review entry合法資料繼續通過；同報告缺closure不能REVIEW→HANDOFF；
  完整精確candidate／reviewer／revision／children／evidence才可走原handoff。
- 43-C3：參數化負例涵蓋錯candidate、作者冒充reviewer、stale revision、漏child、
  child FAIL/BLOCKED/INCONCLUSIVE、OPEN blockingfinding、來源unavailable。非必要
  工作不在required清單，不得因此攔住合法結案。沒有自報N/A豁免必要測試的欄位。
- 43-C4：Root及獨審確認實際Router路徑、既有consumer／回歸；作者至少改壞child
  reducer轉紅→還原；reviewer另改require_closure接線或reviewer比對轉紅→還原。
  Expected為票面固定值，不能從Actual產生；候選載入位置必須是作者worktree。

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
