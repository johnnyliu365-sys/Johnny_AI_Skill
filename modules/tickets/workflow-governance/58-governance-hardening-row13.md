# 58｜Governance hardening: change-log row 13 and the wave-1 carried findings

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1, R4-4; ticket 47 routed findings; ticket 48 carried findings） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/58-governance-hardening-row13-out/` / owner implementation seat / worktree `.worktrees/58-governance-hardening-row13` / branch `cp/wave2-58-governance-hardening-row13` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language）; Markdown for the two document edits |
| 狀態 | `INTEGRATED`（candidate `02814a05` integrated on `cp/wave2-gates` at `88321851` on 2026-11-06; CI run 42128071544 green on both jobs; record `doc/reviews/workflow-governance/wave2-integration-2026-11-06.md`） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/58-governance-hardening-row13` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/58-governance-hardening-row13-review` |
| 責任邊界 | a new governance-consistency test, two wave-1 scripts and their tests, the scripts README, one Workflow.md sentence and one runbook note |
| 禁止修改 | everything else; the committed ticket-47 and ticket-48 evidence scripts stay as they were reviewed |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = Workflow.md
modify = doc/runbooks/
modify = skills/johnny-project-takeover/scripts/index_pins.py
modify = skills/johnny-project-takeover/scripts/receipt_fence_check.py
modify = skills/johnny-project-takeover/scripts/README.md
modify = tests/test_gate_index_pins.py
modify = tests/test_gate_receipt_fence_check.py
create = tests/test_governance_consistency.py
forbid = doc/reviews/
forbid = skills/johnny-project-takeover/scripts/dispatch_lint.py
forbid = skills/johnny-project-takeover/scripts/evidence_gate.py
forbid = skills/johnny-project-takeover/scripts/requirement_snapshot.py
forbid = skills/johnny-project-takeover/scripts/contract_gate.py
forbid = skills/johnny-project-takeover/scripts/coverage_map.py
forbid = skills/johnny-project-takeover/scripts/preflight.py
forbid = skills/johnny-project-takeover/scripts/repair_guard.py
forbid = skills/johnny-project-takeover/scripts/integrate.py
forbid = library/
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
```

## 使用者拍板與可觀察結果

Wave 2 includes "the hardening routed from wave 1 (change-log row 13; ticket 47 and 48 carried findings)" (REQ-20261103-043). After this ticket the plugin's own test suite holds the consistency checks that ticket 47 ran as one-off evidence scripts, so a reworded document that brings a retired rule back goes red in CI; and the two wave-1 scripts close the gaps their review left.

### A. Governance consistency (new `tests/test_governance_consistency.py`)

The instruments of ticket 47 (`doc/reviews/workflow-governance/evidence/47/d7_sweep.py`, `d8_precedence.py`, and the D9 grep) are read, not edited; the new test carries their rules forward, sentence by sentence (paragraph-joined units including fenced blocks, as D7 does), with these additions:

| Source | Rule the test pins |
| --- | --- |
| Row 13 sweep | The D7 retired-rule patterns run over the routed set (D7's roots) **and** over every SPEC under `modules/spec/` and every runbook under `doc/runbooks/`. A hit in the routed set is red. A hit in a historical SPEC or a dated runbook is red unless that file carries the precedence note D8 recognises; the test reports every tolerated hit by file and count in its output. |
| Row 13 / N8-04: both halves of R4-1 | No routed sentence states that a pending dispatch is a queue row or entry (English and Chinese forms, for example 派工以整合佇列列表示), and no routed sentence states that the queue holds anything other than integration candidates; `AGENTS.md`, `Workflow.md` section 0 and `modules/spec/workflow-governance.md` R4-1 each state both halves positively (dispatch = ticket state row plus dispatch-file digest; queue = integration candidates only). |
| R3-07 | Every routed sentence that names who executes integration names the integration script run by whoever holds budget; a sentence that names the reviewer, a fixed integrator, or "the reviewer who approved it" as the one who executes, merges, pushes, lands or commits on behalf (審閱者…代為 commit) is red. |
| N9-06 (D7 gaps) | The exemption for "integration script" no longer masks a reviewer named as executor in the same sentence; merge, push and land verbs join the executor patterns; the Chinese 代為 commit form and the queue-row dispatch form are patterns. Each of the eight injections the ticket 47 review used, and the F-07 one ("by the reviewer who approved it"), is a test case that goes red. |
| N9-04 (D8 gap) | Absence of the precedence note on `modules/spec/TEMPLATE.md` and `modules/spec/README.md` is checked with the same regular expression that checks presence, so a reworded note is caught. |
| N9-05 (D9 gap) | The precedence sentence is pinned by rule and place: it sits inside `Workflow.md` section 0, states that Revision 04 (R4-1, R4-4) prevails over the noted documents, and states that reading them through the note is not a competing reference; reversing the precedence or moving the sentence out of section 0 is red. |

### B. N9-03: the precedence waiver wording

`Workflow.md` section 0's precedence sentence covers SPECs that predate Revision 04 and, after this ticket, also dated handover runbooks under `doc/runbooks/` that carry the same precedence note; the note in `doc/runbooks/handover-2026-08-22-plugin-distribution.md` then cites that sentence instead of granting itself the waiver. No other wording in either file changes. A dated runbook under `doc/runbooks/` that the widened sweep finds with a retired-rule sentence and no precedence note gains that note as its first quoted line (the D8 form) and nothing else; each such file is named in the STATEMENT section. The test of part A pins the widened sentence.

### C. Ticket 48 carried findings

| Finding | Script | Work |
| --- | --- | --- |
| F-06 | `receipt_fence_check.py` | a run that checked nothing never exits 0: a section with zero fences, and `--scan` of a directory with no receipts, are exit 1 with a named code; `--help` exits 3 like the other two wave-1 scripts; extra positional arguments to `--scan` are exit 3; `--require-cmd`, parsed and never used, is removed (giving it is exit 3) |
| NF-04 | `index_pins.py` | `git ls-files` runs with `-c core.quotepath=false` and `-z`, so a tracked leaf with a non-ASCII name resolves; a test with such a leaf |
| NF-08 | `index_pins.py` | decision: an unborn `HEAD` stays a fault (exit 2), because git cannot serve a history that does not exist; the README states it and a test pins it |
| NF-17 | `index_pins.py` | a sealed row whose revision cell names an object whose type (`cat-file -t`) is not `commit`, such as an annotated tag, is exit 1 with a named code |
| NF-16 | `evidence/48/receipt_check.py` | no edit: the evidence gate of ticket 51 closed these gaps as a general instrument; the scripts README says the evidence gate supersedes it for new receipts |

Every change in part C keeps the exit-code contract of R4-2, escapes every printed subject to one line, and adds the git environment rules of the wave-2 gates to the git calls it touches: `--no-replace-objects`, `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, and these variables removed (revision02 names the list): `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_PREFIX`, `GIT_QUARANTINE_PATH`, `GIT_REPLACE_REF_BASE`, `GIT_GRAFT_FILE`, `GIT_SHALLOW_FILE`, every name starting `GIT_CONFIG` and every name starting `GIT_TEST_` (case-insensitive). An inherited variable is an environment input, so it never changes a verdict: with any of them set, a correct index gives the same result as without it.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/58-governance-hardening-row13`.
- reviewer：`ticket-review` seat in `.worktrees/58-governance-hardening-row13-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; ticket 47 (D7, D8, D9, N8-04, N9-03 to N9-06, R3-07) and its review record; ticket 48 and its review record (F-06, NF-04, NF-08, NF-16, NF-17); `doc/HARNESS-CHANGELOG.md` row 13.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a test, two command-line scripts and two document sentences; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the new codes of part C named in the README; the test's patterns held as data with one comment per source finding.

## TDD 設計

1. 正常行為：the consistency test passes on the branch as it stands after the part B edit; the two scripts pass their existing tests.
2. 規則違反／輸入錯誤：each row of part A has injection cases (a copy of the document with the retired sentence restored, built in a temporary directory) that go red; each row of part C has a test.
3. 外部失敗／fail-closed：a missing routed file is red, not skipped; an unreadable SPEC is red; git failing in `index_pins.py` stays exit 2.
4. 回歸保護：the eight ticket-47 injections and the F-07 injection; the tolerated-hit report lists every historical SPEC hit.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | sweep roots (`modules/spec/` versus a similarly named directory); non-ASCII leaf names (NF-04) |
| 2 | null／空字串／陣列 | 是 | zero fences and an empty scan (F-06); an empty SPEC file |
| 3 | 權限繞過 | 是 | a reviewer named as integrator through every pattern (R3-07, N9-06) |
| 4 | Token 格式與比較 | 是 | the precedence-note regex for presence and absence (N9-04); the object type check (NF-17) |
| 5 | 錯誤碼是否一致 | 是 | F-06 and NF-17 reds are exit 1; unborn `HEAD` exit 2; usage exit 3 |
| 6 | 例外是否會拋出 | 是 | git failures in `index_pins.py`; an undecodable document in the sweep |

## 完成定義與證據

- `python -m pytest tests/test_governance_consistency.py tests/test_gate_index_pins.py tests/test_gate_receipt_fence_check.py -q` exit 0; `mypy --strict --python-version 3.11` on the two changed scripts and the new test exit 0; stdlib only; no `Any`.
- **反向突變證據**：for each pattern and rule of part A remove it → its injection stays green → that is the evidence it is needed (each injection red with the rule, green without it); for each row of part C remove its check → its test red → restore. An equivalent survivor stays in the M1 capture, marked, with its reason.
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts at the commit; every cell runs at the committed candidate; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9) and the evidence gate of ticket 51 on the same receipt (cell E1).
- `tests/test_plugin_payload_boundary.py` passes apart from `CommittedPinTests::test_the_pinned_sha_exists`; full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local scripts, tests and governance documents.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record section "Revision01 initial review". S58-04 is a `TICKET_DEFECT`: part C named "repository-selecting `GIT_*`" without a list, and the wave-2 gates disagree. Part C above now names the list: the thirteen names `evidence_gate.py` removes, every `GIT_CONFIG*` name and every `GIT_TEST_*` name (the last after S60-01). This is a closure rebuild: the work is one additive correction commit on the revision01 candidate `49c2c43c`, and the next review is the revision02 initial review. The wording "runbooks 目錄" in `Workflow.md` section 0 is accepted as it is (S58-07): it is unambiguous and part A pins it by rule and place.

| Finding | Class | Work in correction 1 |
| --- | --- | --- |
| S58-01 | IMPLEMENTATION_DEFECT | a Chinese negation exempts a sentence only when it negates the reviewer as executor (for example 不由審閱者, 審閱者不得…); the reviewer's CM1 sentence is an injection that goes red |
| S58-02 | IMPLEMENTATION_DEFECT | a backticked field name is exempt only in the field-list form R4-7 uses (read from the review record); CM2 is an injection that goes red |
| S58-03 | IMPLEMENTATION_DEFECT | the precedence rule is pinned exactly (與 R4-1、R4-4 衝突處以本修訂為準, with no 不 or 以外 between the parts); every case asserts that its phrase is present before it changes it; both CM3 doors are cases |
| S58-04 | TICKET_DEFECT | `index_pins.py` removes the full list above; a graft file in the environment no longer turns a correct pin `STALE`; the ticket 48 test that pinned an inherited shallow file as a tool fault changes to "an inherited shallow file changes nothing", named in the STATEMENT; `receipt_fence_check.py` follows the same list where it runs git |
| S58-05 | EVIDENCE_DEFECT | the tolerated-hit report is part of the test result (a test asserts the set of tolerated files and counts), and P1 runs with `-rA` |
| S58-08 | EVIDENCE_DEFECT | a test runs `--self-note` on a section with zero fences: exit 1 `NO_FENCES` |
| S58-09 | EVIDENCE_DEFECT | the spy test injects and asserts every name of the list, one by one |

Carried, no work here: S58-06 (vocabulary and paraphrase gaps in the sweep) goes with the next change of the consistency test. Routed outside this ticket: `contract_gate.py` removes only nine of the listed names, and `coverage_map.py` and `integrate.py` keep `GIT_TEST_*`; each closes with the next change of its gate (with S60-01 and S60-03), and ticket 50's revision02 states the full list.

### Correction 2 under revision02 (after the revision02 initial review `CHANGES_REQUESTED`)

No ticket defect was found, so revision02 stands. S58-10: a Chinese negation after the reviewer exempts a sentence only when an executor verb follows it directly (代為, 整合, 合併, 推送, 落地, 執行, commit); the before-form gets the same check; the reviewer's CM10 sentence is an injection that goes red. S58-11: the field-list lookahead accepts only what R4-7 uses (`from`, and a closing bracket or full stop if the entry list needs one); CM12 and CM13 are injections that go red. S58-13: E1 runs last, on the receipt as returned, and the STATEMENT describes the mutation clones as the capture does. Carried, no work here: S58-12 (English negation markers anywhere in the sentence) goes with S58-06 to the next change of the consistency test. The next review is the one correction review of revision02.

### Carried after approval (CodeReview §5 rule B)

S58-06, S58-12, S58-14 and S58-15 go to the next change of `tests/test_governance_consistency.py`. The disposition and its reasons are in the review record.
