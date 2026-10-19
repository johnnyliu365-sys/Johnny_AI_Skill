# 45｜實際票面內容完整性診斷（不是派工授權）

| 欄位 | 值 |
| --- | --- |
| State / Closure | PREPARED / 45-C1–C4 revision01；文件獨審後本地 Grant 生效 |
| Authority | Owner batch-checklist-local-20261018 及2026-10-19續行；原 PRD-20260805-009／CHG-20260805-009、workflow-governance AC10；不新增PRD、不重開28/38/40 |
| Source baseline | 0cb5b6085d3dd0f1588569cbbcff5f820ff0d2a2；SPEC blob a700cad60de40096770582b04915bf490fd66a19、模板blob b88a909c935ce655c423838ee55f882ec0937fee；最終文件commit/leaf於派工前讀回 |
| Grant | Root delegated grant-wg45-content-local-20261019，僅本票兩檔、具名actor、下述有限命令；不簽發production Grant |
| Roles | Root control；/root/ticket45_content_impl（當前可用gpt-6-luna/xhigh）；獨立 /root/ticket45_content_review（gpt-6-sol/high）；作者不得派遣、核准自己或整合 |
| Workspace | author .worktrees/skill-improvement-45-content / codex/skill-improvement-45-content；review .worktrees/skill-improvement-45-review；建立時核對非reparse、Git root、clean、baseline |
| Profile / resources | STANDARD：新純驗證契約、有限不確定性、易回復；不產生授權判斷、Host/Git/網路/正式effect。總命令300s，author150/reviewer100/Root50，單次60s，initial+一次correction；30B599.2/600及所有原票耗用不重置或挪用 |
| Return | ImplementationReturn COMPLETED/BLOCKED/CHANGE_DETECTED，candidate/files/checks/findings/deviations/cumulative seconds；COMPLETED僅本切片，不是清單03完成 |

```johnny-boundary
modify = library/local_orchestration/ticket_content.py
modify = tests/test_ticket_content.py
create = library/local_orchestration/ticket_content.py
create = tests/test_ticket_content.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/mainline_source.py
forbid = library/local_orchestration/mainline_readback.py
forbid = library/workflow_router/
forbid = modules/
forbid = doc/
forbid = skills/
forbid = template/
```

modify permits later same-ticket corrections only after these two authorized creations;
it does not authorize another existing file. No deletion, new dependency or output artifact.
Root separately owns this leaf, feature README, checklist and its review record.

## One observable result / reuse

`inspect_ticket_content(payload: bytes) -> tuple[TicketContentIssue, ...]` returns
finite diagnostic issues for the existing ticket Markdown format. Empty tuple means
CONTENT_SHAPE_VALID only. It never means APPROVED, ADMITTED, committed, trusted or
semantically correct. Expected truth, grant validity, dependency readiness, source
revision/identity and live effects remain outside this pure function.

Reuse `document_mutation_gate.read_boundary` / `DocumentBoundary` for path grammar;
do not import test helpers, copy the whole template checker or create a Markdown
framework. The new module owns only instance-content diagnostics; the new test
owns parameterized fictional filled-ticket cases. Future direct consumer is
`dispatch_authority.admit_dispatch`; its wiring remains a separately bounded
HIGH_ASSURANCE source/effect phase. No Router, resolver, registry or Gate is added.
No existing source/test is retired; template suite remains its independent consumer.

## Finite contract

Use one strict frozen issue value with `field: TicketContentField` and
`reason: TicketContentReason`. Field enum: DOCUMENT, BOUNDARY, EXPECTED, ACCEPTANCE,
STOP, IMPLEMENTER, REVIEWER, CONTRACT, DEPENDENCIES, NEW_FILES. Reason enum:
INVALID_INPUT, MISSING, DUPLICATE, PLACEHOLDER, INVALID_BOUNDARY, SAME_REVIEWER,
MISSING_FILE_DECLARATION. No Any/cast/bypass constructor. Deterministic enum/field
order, no duplicate identical issues. Maximum UTF-8 payload 131072 bytes; empty,
invalid UTF-8 or wrong primitive yields DOCUMENT/INVALID_INPUT before parsing.

Recognize only active top-level bullets in these exact existing sections (nested
### headings do not end a section):
- 使用者拍板與可觀察結果: 核准 Expected（使用者可觀察結果）、正常／失敗／邊界驗收、停止條件。
- 實作範圍、依賴與 ticket elements: implementation owner、reviewer、公開契約／資料模型、直接依賴與狀態、新增檔案責任。

Ignore HTML comments, fenced code (backtick/tilde including longer fences) and
indented code as field evidence. Missing/empty field -> MISSING; duplicates in
the required section -> DUPLICATE, never first-match. Remaining `<...>` scaffold
placeholder -> PLACEHOLDER; labels elsewhere cannot satisfy a missing field.
Reject duplicated required sections. Compare trimmed/backtick-unwrapped exact
implementer/reviewer values and diagnose SAME_REVIEWER when equal; this is textual
shape checking, not identity authentication.

Exactly one active `johnny-boundary` fence is allowed; comments, surrounding
example fences and indented code are not active boundary declarations. Feed only
that active declaration to the existing read_boundary (do not extend its grammar).
Missing/duplicate/invalid boundary returns its finite issue, never guesses paths.
If create is empty, NEW_FILES must contain a nonempty N/A reason. If create contains
exact paths, every path must appear in the active NEW_FILES value; missing paths
return MISSING_FILE_DECLARATION. Directory/pattern create is diagnosed with
MISSING_FILE_DECLARATION because exact created-file expansion requires a later
source-bound list; do not silently claim completeness. Presence of a path does not
prove responsibility/consumer/AC semantics. Those remain reviewer/source duties.

## Acceptance and verification

45-C1: fictional filled ticket with exact created file and distinct roles returns
empty issues; a second legal no-create ticket with N/A reason also returns empty.
Ordinary enum/issue constructors and invalid primitive tests run before behavior;
this staged local construction uses the existing AC10 build-before-activation
rule and cannot construct a live source/Grant. Strict frozen type validation.

45-C2: each required field missing, empty, scaffold, duplicated, moved or hidden
in comment/fence/indent is diagnosed. Same reviewer rejected; valid different role
strings continue. Duplicate sections, unknown/invalid path boundary, boundary
hidden in comment/example, two boundaries, exact missing new-file declaration,
wildcard/directory create and invalid input all have finite assertions. No real
repo, target, credentials, subprocess, network or native spawn in tested code.

45-C3: author reverses real active-field filtering and new-file coverage behavior
separately; named cells fail for intended reason, exact restoration returns green.
Reviewer uses a different door (duplicate/role/section boundary), raw output,
then restores and verifies. Zero red is finding, not pass. TEST→A→B N/A: no existing
responsibility is moved. Old template tests remain unchanged and green.

45-C4: focused `python -m pytest tests/test_ticket_content.py tests/test_ticket_template_contract.py -q`,
`python -m mypy --strict library/local_orchestration/ticket_content.py`, compile/import,
`git diff --check`; no unrelated suites or real CI/model calls. Smoke is public
inspector on filled fixture, not a duplicate validator. New product<=240 and tests
<=240 lines are structure-review signals, not compression requirements. Fixtures
inline/parameterized; no screenshot/report copies, prompt or ticket prose in code.

## Completion / holds

Independent source review and existing guarded local integration only after PASS.
No formal dispatch admission or configuration is switched on. No claim this fixes
30B trusted Grant, 43 isolated review, or closes checklist03/12. Escalate only
scope/budget/security expansion, not normal design choices. Resource owner is the
named seat/Ticket45, TTL through review + evidence seal; known cleanup denial
prevents automatic teardown retries, so preserve registered assets with hold and
mark CLEANUP_BLOCKED separately. Do not touch prior worktrees/journals/Recovery.
