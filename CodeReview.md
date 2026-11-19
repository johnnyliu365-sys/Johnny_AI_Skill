# Code Review 入口與結論標準

> 本檔是 Johnny 流程的 Code Review 唯一入口，定義審閱 admission、必要證據、
> finding 路由、收斂與結論。專業檢查方法不在此重抄；審閱者必須完整讀取本檔
> 索引的適用 skill reference。

文件歸屬與 target project 零複製規則以
[Workflow.md 的治理文件歸屬](Workflow.md#governance-document-ownership)為準。

## 1. Review admission

開始前必須獨立讀回並互相核對：

- exact ticket blob、receipt、registry commit 與具 revision 的有限
  `Acceptance Closure Set`；
- approved SPEC、Context、CHG、implementation language 與 baseline；
- 實際 diff、implementation commit、docs-only handoff commit 與 worktree identity；
- first-red、green、strict type、build、smoke、reverse mutation 及安全證據；
- delivery profile/resource plan 與適用專業分類。

缺失、靠聊天／父工單／相鄰票推定或識別碼不一致時，先分類為
`TICKET_DEFECT`／`EVIDENCE_DEFECT` 或 `BLOCKED`，不得審查臆測的實作契約。

## 2. 必要檢查索引

每次 review 都檢查清晰與強型別、既有編碼／分層規則、邏輯、邊界與例外、安全
與效能、測試真實性、依賴合理性，以及 SPEC／ticket／Context 符合性。

依本票條件讀取下列 canonical references：

| 條件 | 必讀 reference |
| --- | --- |
| 所有 implementation review；也用於 ticket TDD matrix | [`review-checks.md`](skills/johnny-project-takeover/references/review-checks.md) |
| Adversarial review or deployment readiness | [`adversarial-review.md`](skills/johnny-project-takeover/references/adversarial-review.md) |
| 強型別 ticket/schema/dispatch | [`specification-ticketing.md`](skills/johnny-project-takeover/references/specification-ticketing.md) |
| Agent authority、task/worktree、correction | [`implementation-authority.md`](skills/johnny-project-takeover/references/implementation-authority.md) |
| TDD、strict type、smoke、completion | [`implementation-tdd.md`](skills/johnny-project-takeover/references/implementation-tdd.md) |
| XSS 或 Browser/WebView/DOM/JavaScript | [`xss-review.md`](skills/johnny-project-takeover/references/xss-review.md) |
| Secret、正式 Log、Provider、Webhook 或 external effect | [`security-boundary.md`](skills/johnny-project-takeover/references/security-boundary.md) |
| Profile、fan-out、POC/staging | [`delivery-profile.md`](skills/johnny-project-takeover/references/delivery-profile.md) |
| 模型角色 handover、休眠／喚醒或 capability escalation | [`model-role-routing.md`](skills/johnny-project-takeover/references/model-role-routing.md) |
| 低階模型 ticket admission 或 convergence replan | [`ticket-decomposition.md`](skills/johnny-project-takeover/references/ticket-decomposition.md) |
| 正式 UI、design source 或 visual acceptance | [`ui-design-handoff.md`](skills/johnny-project-takeover/references/ui-design-handoff.md) |
| artifact tree、Agent Context 換票／關閉 | [`artifact-tree-routing.md`](skills/johnny-project-takeover/references/artifact-tree-routing.md)、[`agent-context-lifecycle.md`](skills/johnny-project-takeover/references/agent-context-lifecycle.md) |
| PRD／CHG lineage 或 archive | [`requirement-lineage.md`](skills/johnny-project-takeover/references/requirement-lineage.md) |
| reusable module catalog／card | [`module-catalog-routing.md`](skills/johnny-project-takeover/references/module-catalog-routing.md) |
| 實作語言 | [`language-policy.md`](skills/johnny-project-takeover/references/language-policy.md) |

The reviewer alone owns the final review conclusion. Integration is executed by the versioned
integration script from the merge queue by whoever holds budget (Revision 04 R4-4); the review
`APPROVED` is its admission, not its executor. An adversarial helper may return evidence and
findings, but it is never a co-reviewer and cannot replace that conclusion.

不適用也必須記錄可驗證理由，尤其是 XSS、privileged capability、Agent control、
task/worktree、Profile fan-out 與 POC/staging ancestry。

## 3. 證據方法

- 將每個 AC／Closure item 一對一連到測試與可觀察斷言，不接受「整體有覆蓋」。
- 一次跑完整 Closure Set，批次列出同一 baseline 可發現的全部 blocking findings。
- 使用 bounded reverse mutation 證明關鍵測試／gate 真的會轉紅，並精確還原。
- source scan、snapshot、型別 checker 或測試名稱只可作輔助，不得取代行為證據。
- 重新讀回 host/Git/filesystem/renderer 等真實邊界；不接受 prompt、聊天、自述或
  constructed evidence 充當 authority。
- Review report 記錄命令、結果、檔案／位置、適用 reference、未解風險與 commit
  identity；不得重抄 ticket 正文。
- Review record 以 `review-verdict` 區塊收尾（workflow-governance R4-7）：`candidate`、`verdict`、
  `reviewer`、`reviewed_at`；整合腳本只讀該區塊，不讀散文結論。
- Each review section of a code-review record (`doc/reviews/<feature>/<ticket>-…-code-review.md`, one ticket per record) ends with a fenced `rework-record` block that directly follows the section's `review-verdict` block (ticket 73). A pre-dispatch rule-only review (`…-ticket-review.md`) carries no block and counts in no round.
  - The reviewer writes the block at the end of its own section. It holds exactly these five lines, in this order, each key once: `candidate` (40 lower-case hex, or `none` in a `RETURN` block), `round` (1, 2, 3 … in order of appearance in the record, no leading zero; it is the record's own counter and does not replace the §5 count), `kind` (`INITIAL` or `CORRECTION`, copying the label of `rule-review-label`, or `RETURN`), `verdict` (the section's `review-verdict` verdict), and `causes`.
  - A `CHANGE_DETECTED` return before any review is a round too. Its `RETURN` block stands before the first review section, with `verdict: CHANGE_DETECTED` and the returned commit or `none` as `candidate`; the control plane writes it.
  - `causes` is empty, or causes joined by `,` with no blank and no repeat, in this order: `CONTROL_PLANE_RULE`, `RETURN_UNTRUE`, `DESIGN_UNFORESEEN`, `IMPLEMENTATION_DETAIL`. They come from every finding the section asks to have corrected, which is every §4 class except `OUT_OF_SCOPE_HARDENING`. A finding's class is the first §4 class named in its class cell. `TICKET_DEFECT` gives `CONTROL_PLANE_RULE`. An `EVIDENCE_DEFECT` whose finding cites a return or receipt statement that the evidence contradicts gives `RETURN_UNTRUE`. `REQUIREMENT_CHANGED` and every `RETURN` block give `DESIGN_UNFORESEEN`. `IMPLEMENTATION_DEFECT` and every other `EVIDENCE_DEFECT` give `IMPLEMENTATION_DETAIL`.
  - The causes are empty for `APPROVED`. For `CONVERGENCE_REVIEW_REQUIRED` they are empty only when the record holds an `APPROVED` `convergence-disposition` for that candidate, and otherwise not empty. For `CHANGES_REQUESTED`, `BLOCKED` and `CHANGE_DETECTED` they are not empty.
  - `rework_report.py` (see its README section) sums the rounds and the causes per ticket. `integrate.py` still reads only the `review-verdict` and `convergence-disposition` blocks and ignores every other fence.

## 4. Finding 路由

每項 finding 必須引用既有 Closure item；無法引用者不得偽裝成 implementation
defect。分類固定為：

1. `IMPLEMENTATION_DEFECT`：違反凍結 AC／不變量／matrix；原票原 branch additive
   correction。
2. `EVIDENCE_DEFECT`：凍結項目的 test/red/smoke/verification 證據不足；原票一次
   補齊。
3. `TICKET_DEFECT`：應在 ticket/TDD/schema 預先定義卻缺失；回控制面修 ticket，
   重建 Closure revision 後才能實作。
4. `REQUIREMENT_CHANGED`：新增／改變 AC、架構、公開契約或安全邊界；回 Grill、
   SPEC 與 tickets。
5. `OUT_OF_SCOPE_HARDENING`：不違反目前 Closure 的改善；另開後續 `PLANNED`
   ticket，不阻擋本票。

<a id="rule-smallest-fix"></a>

對於依 §5 規則 B 不擋核准的 finding，reviewer 指出能關閉它的最小修正，或提議將它移交至 §4 第 5 項與 §5 規則 B 允許的去處。

修正不新增機制（script、gate、schema 或規則），除非該 finding 非此不能關閉，且 reviewer 說明原因。

## 5. 結論與收斂

結論只能是 `APPROVED`、`CHANGES_REQUESTED` 或 `BLOCKED`。

- 任一未處理且影響正確性、安全、資料隔離、可用性、效能或核准契約的問題，
  不得 `APPROVED`。
- `CHANGES_REQUESTED` 預設保留 ticket、owner、worktree、branch、allocation 與有效
  receipt；以新的 additive correction commit 修正，不得 reset/amend/force。
- 修正後重跑受影響驗證、smoke 與適用 review references。
- 同一 Closure revision 最多一次 initial review 加一次 correction review。第二次
  仍有 implementation/evidence defect，結論附 `CONVERGENCE_REVIEW_REQUIRED` 並回
  控制面做架構／ticket 分解；不得自動第三次 correction。
- 收斂規則 B（owner 2026-11-05 核准）：correction review 之後仍未關閉的 finding 分兩類。
  - 擋住核准：會改變結束碼分類（R4-2 紅燈與故障互相誤判）、破壞安全或範圍邊界、或違反 P0
    的 `IMPLEMENTATION_DEFECT` 與 `TICKET_DEFECT`。
  - 不擋核准：候選行為正確、只是測試沒有釘住的 `EVIDENCE_DEFECT`，以及 `OUT_OF_SCOPE_HARDENING`。
    其中「若日後退化會放行不該放行的變更」的證據缺口，必須在同一閘門的下一次改動補上；其餘移交
    後續強化 ticket。
  - 結論為 `CONVERGENCE_REVIEW_REQUIRED`、且未關閉的 finding 全屬「不擋核准」時，控制面在審查紀錄
    附「收斂處置」段：逐項列出 finding、類別與移交去處，並附 `convergence-disposition` 區塊
    （`candidate`、`reviewer_verdict`、`disposition: APPROVED`、`rule: CodeReview §5 rule B`、
    `carried:` 清單）。reviewer 原本的 `review-verdict` 區塊不改。票面狀態改為 `REVIEW_APPROVED`。
  - 只要有一項屬「擋住核准」，照上一條回控制面重新規劃，不得套用本規則。
- 只有全部 blocking findings 關閉、證據完整，且結論 `APPROVED` 或附有依規則 B 的 `convergence-disposition`，整合腳本才可把候選列入
  guarded integration／handoff（Revision 04 R4-4）。Review approval 不自動授權 push、release、部署、
  付費、正式權限或其他外部 effect。

<a id="rule-review-label"></a>

- 新 closure revision 的第一次 review 是它的 initial review；計數重新開始。
- 控制面在派工前於 review request 標明每次 review 的標籤：initial 或 correction，連同其 closure revision。結論回來之後，不得改標。
- 結論依回傳原樣記錄，包括附帶的 `CONVERGENCE_REVIEW_REQUIRED`。
