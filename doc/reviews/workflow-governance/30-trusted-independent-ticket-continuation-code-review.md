# Ticket 30 source-contract decision review — 2026-10-18

| Field | Evidence |
| --- | --- |
| Prior control baseline | `789302c4345aedb5439770ebb7aad1c9ac0f3cd8` |
| Initial decision candidate | `0bfb4a2869f9fbb73e67a3c1a436a8e341fd66c2` — two findings |
| Additive correction | `f13f35711594af241c83b803f91f0f472baa6241`; Ticket30 leaf blob `823ef2d0e86bbc74a8508263be1a8bde678f6324` |
| Independent reviewer | `/root/ticket42_review` (`gpt-6-sol/high`), different from the Architecture Owner analysis |
| Conclusion | `PASS` for bounded docs-only technical source contract; `NON_DISPATCHABLE` remains |

First review found that an index-only graph contradicted workflow-governance
SPEC AC9's committed-leaf derivation, and that existing `GitBlobReadResult`
has a string payload, insufficient for a raw-byte digest claim. The same-ticket
correction requires a unique machine-readable ticket fence in each committed
leaf, compares its graph/status fields with the index and rejects mismatches;
the candidate projection is built only from validated leaves. The bounded
readback port now names a raw-byte result using the existing finite status
enum, hashes those bytes, and strictly decodes UTF-8 before JSON parsing.

Reviewer readback of the exact correction found both findings closed,
one-file docs-only scope, clean worktree and `git diff --check` exit 0. No
runtime tests or external effects were performed; this is a source-contract
decision, not an implemented or qualified adapter. No target facts were
inferred from the human status table. Mainline migration, admitted declaration
readback, ticket-scoped Grant, Router/Host admission, and formal closure stay
unverified. No push or release occurred.

## 30A fixture ticket / decision package docs review — 2026-10-18

| Field | Evidence |
| --- | --- |
| Control baseline | `3ca02bd5e90611c101d97cc79f06b4751c70cd1c` |
| Initial docs candidate | `ed314dae` — Ticket 30, its registry row, checklist revision 24 |
| Same-ticket correction | `406817c485ddb5af78794d797e2f281c397abaaa`; Ticket 30 blob `ded322b3c7e82399c31ff4cf67d3dbf3237af3fb` |
| Independent reviewer | `/root/ticket30_docs_review`, read-only and separate from Root author |
| Conclusion | `PASS` for **docs-only preparation**; `SPEC_BOOTSTRAP_DECISION_REQUIRED / TICKET_GRANT_REQUIRED / NON_DISPATCHABLE` remain |

The independent reviewer found three defects in the first docs candidate:
the recommended `CONTEXT.md` anchor is sealed and needs an authorized
Architecture Owner `REVISE`; the existing workflow-governance SPEC still
forbids Ticket 30 dispatch until source and Host binding, so fixture bootstrap
requires an explicit bounded exception in the original Change Control; and
the nine-ref remote CI inventory needed its actual batch command and path
predicate, not only a main-branch example. Correction `406817c4` records
each constraint without writing Context/SPEC, activating a Grant, or treating
an empty CI command list as test-retirement authority. The reviewer reread
the exact correction and marked all three findings `CLOSED`.

The reviewer briefly reported an index mismatch, then checked the full
`406817c4` registry and checklist and withdrew it: both explicitly require
the SPEC bootstrap decision before Grant. Root ran
`python -m pytest tests/test_mainline_projection.py tests/test_ticket_template_contract.py -q`
(`59 passed`) and `git diff --check`; the reviewer checked the committed
docs with `git show --check`. No source adapter, true declaration readback,
`admit_dispatch`, native spawn, Host qualification, push or release was tested
or performed. Checklist 02/08 therefore remain unchecked.

## Owner-approved authority revision and 30A construction admission

Owner's subsequent decision pins `acf0ffa1780af3d229b7f80c6e063f6d642e6864`
and Ticket 30 blob `ded322b3c7e82399c31ff4cf67d3dbf3237af3fb`, approving
the two recommendations with exact constraints. Root acted as Architecture
Owner only for lawful Context `REVISE` and original CHG/SPEC/Ticket updates;
the separate implementer role remains mandatory for the two source/test files.

Independent `/root/ticket30_docs_review` read candidate `e551c556`, correction
`7779c815` and final bounded scope clarification `35b25d60`. The actual new
constructors cannot be preflighted while nonexistent: the reviewed same-ticket
type-only Phase A creates declarations/tests only, and requires actual
constructor/negative/round-trip/strict evidence and independent review before
Phase B behavior. Cumulative `CREATE` is measured against the original
dispatch baseline; Phase A does not reset scope or allow preexisting-file
modifications. Both findings are `CLOSED`; limited docs/ticket review `PASS`.
The reviewer confirmed old sealed03 commit/blob and CHG provenance, unchanged
stable facts, exact repository/ref/topology and unchanged final AC9–11/effect
requirements. The seal/active-boundary writeback only materializes this reviewed
conditional admission; it grants no formal source or Host qualification.

Root checks on the unchanged existing dependency/code baseline:
`python -m pytest tests/test_shared_context_service.py tests/test_ticket_template_contract.py -q`
returned `54 passed, 15 subtests passed`; ordinary observation/projection
dependencies via `python -m pytest tests/test_mainline_projection.py tests/test_project_authority_contracts.py -q`
returned `20 passed`; `git diff --check` passed. These are design/preflight
regressions, not the nonexistent 30A module's success evidence. The final
dispatch commit, leaf blob and worktree identity are independently read back
before the admitted type-only native delegation; exact values will be sealed
with implementation review evidence.

Final carrier review found the legacy integration parser requires a nonempty
`modify` list even for a create-only ticket. No gate change or extra source
permission was authorized. Root and the independent reviewer verified the
existing forbid-first evaluator can encode an empty effective modification set:
the schema-only `modify = AGENTS.md` sentinel is also unconditionally forbidden.
Public parser/evaluator probes allowed exactly the two CREATE paths, rejected
all 1,116 currently tracked MODIFY/DELETE paths, case variants of the sentinel,
modifications of the new paths, and an ungranted CREATE. Root's first cp950
text-decoding probe failed before evaluation; the explicit UTF-8 probe passed.
No effect API ran. The reviewer accepted this exact expression as no permission
expansion, subject to committed-ticket readback; the ticket documents its
non-authorizing meaning. Only the final cumulative two-file candidate may be
integrated; Phase A is not independently merged and used to reset the boundary.

## 30A Phase A and initial Phase B review

Dispatch baseline `d2f2aa1030e2d817f9e3a016e5dfacf11ce0c22d`, ticket blob
`4ac13403b75f265522633e6989a6c8e03b734b22`; implementation worktree
`.worktrees/skill-improvement-30a-fixture`, branch
`codex/skill-improvement-30a-fixture`, actor `/root/ticket30a_fixture_impl`
(`gpt-6-luna/xhigh`). Different reviewer `/root/ticket30a_fixture_review`
(`gpt-6-sol/high`) owns `.worktrees/skill-improvement-30a-review`.

Phase A `79c98d77b1f2a5b8d92bd36b42c42aac2ae910ec` was independently
`APPROVED`: 45 focused tests, strict mypy, compile and diff checks passed;
all eight failure enums and three blob statuses were constructed/round-tripped.
Reviewer disabled the request's WORKTREE_HEAD guard: five negatives failed
with DID NOT RAISE, then all five passed after exact restoration (source blob
`51aa7fbb0c385823366f309e9c73b4ea0536f5cc`). Root separately ran 32
constructor tests and strict mypy. Actual types, not prototypes, admitted Phase B.

Phase B `43c9ebf1081f189e9adeb87f3717b6b50a2ec1b9` had 83 focused tests,
strict mypy, compile and diff checks green; cumulative diff remained two CREATE
paths. Implementer digest and leaf-revision bypass mutations each made its
named cell fail, then restored 4/4 green. Independent reviewer mutation removed
the same-feature guard: the cross-feature case returned LEAF_NOT_FOUND instead
of INDEX_SCHEMA_INVALID; after restoration all three path cases passed and
source blob returned to `278e042a39f871c9e760713d461f54aefc2d2b43`.

Review was `CHANGES_REQUESTED`, not a false closure: F2 accepted a second
heading with trailing whitespace; a public 1,200-deep JSON probe raised
RecursionError; F3 safely reproduced inherited GIT_DIR redirecting fixture
initialization outside its own root. F1 allowed empty/duplicate bindings;
reviewer classified missing cardinality as TICKET_DEFECT, so Root clarified
the existing four-source completeness in same-ticket Closure revision 02.
No new field, resolver, SPEC, PRD, scope or budget was added. Original author
and reviewer continue all four findings and retain valid Phase A evidence.

Structural review inspected the 427-line product module as one source-assembly
responsibility and the 1,019-line test as constructor checks, private fixture
lifecycle/serialization and the same capability's case matrix. The threshold
triggered review, not automatic splitting/deletion; existing Git test helpers
were private unittest methods rather than an available shared harness. The
correction must remain parameterized and cannot grow a parallel framework.

## Closure02 correction, exact integration and evidence seal

The same independent reviewer accepted the bounded Closure02 clarification at
`bacab24ddd20d1aab5911315b53ff30926a4daa9` (ticket blob
`aa207e6f6b7edcfc16eefadd83520bbfce4af4eb`). Original owner correction
`629030f4678b5d600c9ad53baf60967c25ecefbc` normally merged that Root docs
carrier; Root's later ticket-only anchor clarification `5d0f8d4b` was also
independently accepted (ticket blob `8f950a67ab08b9c4d7a57922953c51eee0b2d0d6`).
The latter preserves original source scope and separately authorized Root
document revisions; it does not let an implementer filter its own changed paths.

All four findings are `CLOSED`. New defect tests first reproduced eight red
cells on the defective code. Correction requires exactly four unique binding
kinds, counts trailing-space headings, maps RecursionError to finite failure,
and strips ambient GIT_* values before any fixture command while using a
test-owned empty global config. The original reviewer ran all 20 affected cells
with unreduced output and the full 91 focused tests, strict mypy, compile and
diff checks. Independent cross-feature mutation made its named cell red
(LEAF_NOT_FOUND instead of INDEX_SCHEMA_INVALID), restored 3/3 green, and restored
source blob `22a23be723bc34d9144575a81238d79ff5579485`; review worktree clean.
Verdict `APPROVED`. Earlier constructor/valid-case evidence remains in force.

Final candidate `b7e9e2f35bd997c65df80541ec0196a000ab3e46` only normally
merged the reviewed docs carrier into the reviewed correction; source and test
blobs remained `22a23be723bc34d9144575a81238d79ff5579485` and
`ff6f66e8c6cd07fb956de3be72507038e2254ad0`. The trusted control branch
`codex/skill-improvement-checklist` was clean at
`5d0f8d4bab982b6b1944d24a512a6f24bb8e799a`; its diff to the candidate was
exactly the two CREATE paths, with no preexisting source/test changes from the
original `d2f2aa10` source baseline. `admit_document_mutation` read the boundary
from that trusted branch, returned `INTEGRATED`, and read back the exact final
candidate SHA. This is local integration only; `main`/origin were not pushed.

Post-integration Root used one Python process to assert the imported module
file belongs to the integrated control worktree and verify both exact reviewed
Git blob hashes, then invoked
`pytest.main(['tests/test_mainline_source.py', 'tests/test_mainline_projection.py', '-q'])`:
91 passed. `python -m mypy --strict library/local_orchestration/mainline_source.py`
and `python -m compileall -q library/local_orchestration/mainline_source.py`
passed. This actual-load observation applies to this local fixture run, not a
generic Host/Expected qualification or checklist05 closure. The unchanged
existing integration gate regression also passed 65 tests and three subtests.

The synthetic decoy left by the first intentionally red GIT_DIR test had a
policy-blocked recursive cleanup attempt. Later repros gained finally cleanup.
Root and reviewer independently read the exact owned decoy path under
`pytest-308/test_fixture_git_environment_i0/redirected-git-dir` as absent;
neither claimed to have deleted it. No unrelated Recovery Hold was touched.

Integration journal seal, **before teardown**: owned temp root
`C:\Users\GameBoy\AppData\Local\Temp\johnny-ticket30a-integration-h7rtk9vz`,
owner `ticket30a-root`, TTL this integration session until sealed evidence and
exact teardown, contains one `queue/document-mutation-journal.jsonl` record.
It binds Ticket30, integration branch, outcome INTEGRATED, candidate/detail
both `b7e9e2f35bd997c65df80541ec0196a000ab3e46`, no offending path, and full
file SHA-256 `74351bf0dccb2714df25cf2f126b815f1e44fe031944095fc0df9719d0bc50ce`.
This record and exact source commits remain versioned before journal removal.
Dedicated clean implementation/review worktrees and the integrated branch are
also teardown-pending; no unregistered/user asset is a cleanup target.

### Exact cleanup readback

Independent reviewer read the committed seal `d88eecde48f8f4620e9d0b2395d6f334405a45ab`
and the live 394-byte/one-record journal; metadata, SHA-256 and both integrated
source/test blobs matched. The known decoy path was independently absent again.
Root then checked both exact registered worktree paths remain inside the named
repository `.worktrees` directory, have no reparse point, are clean, and point
to commits already reachable from the control branch. Normal `git worktree remove`
removed only `.worktrees/skill-improvement-30a-fixture` and
`.worktrees/skill-improvement-30a-review`; `git branch -d` removed only their
integrated implementation branch. No force/reset/clean or history rewrite ran.

Root checked the exact owned journal hierarchy has no reparse points, only its
queue child and the sealed single journal file, and rechecked SHA-256. Native
`Remove-Item -LiteralPath` removed that file and its now-empty queue/root
directories without recursion. Final `Test-Path` for both worktrees and journal
root returned false. The initial read-only inventory command had a PowerShell
pipeline syntax error before execution; the corrected inventory passed before
any teardown. No user, formal-source, other-ticket or Recovery asset was removed.
Reviewed/integrated commits and permanent regression tests remain in Git.
30A fixture slice is `CLEANUP_CONFIRMED / COMPLETE_LOCAL`; full Ticket30, true
source/Host qualification, push, publication and dependent checklist closure
remain outside this result. The two-file construction allocation is released.

## 30M document migration — authority and read-only source inventory

Owner's next-stage authority is recorded before migration at `a7bc0101`, based on
clean `d00018aa0117032ecba132e545a3085b29ec870a`. Root owns the control-plane
document worktree `control/skill-improvement-30m-docs`; only README, leaves29/30,
this review and the existing checklist may change. No source/test/Context/SPEC
mutation, new PRD, push, release or deployment is authorized. The same ticket
retains all earlier findings, consumed allocation, tests and Recovery boundaries.

Read-only helper `/root/mainline_membership_inventory` checked approved Context04,
REQ-20260805-009, SPEC03 and exact leaves. It found evidence for a bounded29→30
continuation graph, not full-programme membership. Root explicitly selected this
limited scope under the current document-migration authority. The index records
source versions, technical ID encoding, exact admission/review refs, per-node
meaning, owners and handback. The historical completed contracts were not reopened.
Ticket02's historical human row/leaf conflict and unspecified full-programme edges
are disclosed but not silently repaired or used as authority. Current documents
are not passed to the fixture-only public request under a synthetic observation.

Fresh read-only source audit, 2026-10-18 local time18:44 (all exit0):

```powershell
git remote -v
git ls-remote --symref origin HEAD
git ls-remote --heads origin
gh api repos/johnnyliu365-sys/Johnny_AI_Skill
gh api repos/johnnyliu365-sys/Johnny_AI_Skill/git/trees/a1cb6c13adbeb52a4117991727dcc3d4af6d2a33 --method GET -f recursive=1
gh api repos/johnnyliu365-sys/Johnny_AI_Skill/actions/workflows
gh api repos/johnnyliu365-sys/Johnny_AI_Skill/actions/runs --method GET -f branch=main -f per_page=5
gh api repos/johnnyliu365-sys/Johnny_AI_Skill/hooks
git rev-list --left-right --count a1cb6c13adbeb52a4117991727dcc3d4af6d2a33...d00018aa0117032ecba132e545a3085b29ec870a
git diff --name-only a1cb6c13adbeb52a4117991727dcc3d4af6d2a33..d00018aa0117032ecba132e545a3085b29ec870a
```

The credential-free origin is the approved GitHub repository; direct remote HEAD
and exact main are `a1cb6c13adbeb52a4117991727dcc3d4af6d2a33`. Provider tree SHA
matches and `truncated=false`. Context there is still rev03/blob
`9096c68199994b1414862828ffb0ce060f8482d7`; remote feature README blob is
`373d3e756bd965c8b5fb1f6b4862cf8f78a39395`, not this migration. Local Context04
blob is `06baa4dea5db1c3370086552c35a1d8f721ad47e`. No local branch/tracking
entry substitutes for that direct observation. Other eight branch tips matched
the previous recorded scoped inventory, but were not re-materialized as sources.

On that exact remote main tree, searched `.github/`, `.gitlab-ci*`, `.circleci/`,
azure-pipelines, Jenkinsfile, `.buildkite/`, `.travis*`, appveyor,
bitbucket-pipelines, `.drone*`, `.woodpecker*`, Makefile, Taskfile, justfile,
package.json, pyproject.toml, tox.ini, noxfile.py, Cargo.toml and go.mod:
**此範圍未見** checked-in CI entrypoints. Earlier branch-tip audit stays historical
evidence only. Actions API nevertheless returned **one active** workflow:
ID339484080, `Dependency Graph`, path `dynamic/dependabot/update-graph`.
Five returned main-filtered runs are successful `event=dynamic`; latest returned
run32693024347, head `bd2d9adaa586412de76ed8c3961ae1c697410554` is not current
main and is not its CI proof. Repo webhooks API returned `[]`; organization/
GitHub-App/other provider automations are not excluded. Thus a future push may
trigger provider automation; no claim of no CI/no effects, no fabricated test
command list and no test-retirement permission follow.

At d000 the branch is0 behind/124 ahead, with87 net changed paths versus the
direct remote SHA. The full range includes reviewed local product/test slices,
other design baselines and templates. It must not be mislabeled as this five-doc
change. The upcoming30B decision package therefore recommends local construction
first and no push; any broader publication needs explicit exact-range approval.
Raw API bodies/tokens are not persisted; only this bounded identity/result record
is retained. No Host qualification or model call was performed by the audit.

### 30M validation / independent review

Root validated exact candidate `bf7e1b9abee6423300e99a1388cc32068881d582`
from committed Git bytes, not working-copy text. Existing `_parse_index` /
`_parse_leaf` are used only as pure document-schema validators; no real-document
`GitObservation` is constructed or sent to the fixture-only public entry.
Each mirrored field and raw-byte SHA-256 matched. Four binding revision blobs
equal the same artifacts at the candidate commit. Normal constructors built the
existing MainlineTicket/ProjectionRequest and the actual projection returned:
ready=[], waiting=[wg-ticket-30], incomplete_required=[wg-ticket-30],
closure_candidate=false. Ticket29 completion did not close the mainline.

Leaf29 blob `71a7c78e7d2a5b999b4663360516647c60848826`, raw digest
`sha256_d6d3b25dd516ea4f2fb9daf90f1b39917e0f5bc9ecc3e647492656f411efe94f`;
leaf30 blob `08146ff8e8afc9c886293bdcb57e4d5d2e94257b`, raw digest
`sha256_f8d700a279a81dacfce6af7e5ea6d1359765061552f44035188856b64d970785`.
Index blob `a32c08cfbfb1148ddcb7126c2e123404bce9329c`. Root staged the final
leaf bytes, computed digests from `git show :<leaf>` after the last leaf edit,
updated the index, committed and recomputed from exact candidate blobs. CRLF
working-copy conversion was not used to calculate a Git source digest.

The same direct stdin verification (no generated script/clone/temp repository)
checked three negative inputs: append-byte digest drift, index/leaf status mismatch,
and unknown dependency. Each was rejected at its actual schema/projection check.
The comparison is document validation, not a qualified true-source/effect gate.
Unreduced command output was read; focused regression remained:

```text
python -m pytest tests/test_mainline_source.py tests/test_mainline_projection.py -q
91 passed in 23.51s
python -m mypy --strict library/local_orchestration/mainline_source.py
Success: no issues found in 1 source file
python -m compileall -q library/local_orchestration/mainline_source.py
git diff --check
```

All exited0; source/test untouched and worktree clean. The initial shell execution
yielded its session and was resumed for completion, not relaunched. No lost
attempt/time was reset. Independent targeted review and guarded integration remain
pending; this record does not claim their PASS. The final decision seal will pin
completed versions and the30B Grant candidate without treating it as issued.

Independent `/root/ticket30m_docs_review` (`gpt-6-sol/high`, separate clean
detached `.worktrees/skill-improvement-30m-review`) returned **APPROVED**, no
blocking30M-D1–D4 findings, for bf7e1b9a plus the review-only87b090ed carrier.
It independently recomputed technicalProjectId, both migration-revision formulas,
all committedrawdigests/mirrors, exactbindingblobs, and29admission/review refs.
The normalized bounded graph returned the same open30/falseclosure. This approves
only the evidenced two-node continuation slice, not full-programme membership.

Its different-door in-memory counter-mutation replaced the PRD binding with a
duplicateContext binding in the **actual committed index**. The existing parser
rejected it with `ValidationError: source bindings must contain each required
kind exactly once`; original bytes parsed equal after restoration. A separate
index-only status change exposed the actualleafmirror mismatch. No artifact or
source file was mutated, no fixture-public request was called, and unreduced
output was read. The reviewer ran diffcheck and independently verified clean
worktree/exactcandidate/five-doc scope; it explicitly did not claim independent
networkreadback or repeat Root's91-test run. Earlier30A review remains valid.

The only subsequent pre-integration changes are this report, a human registry
progress row and checklist progress text. No leaf/schema/source/version/digest
change is permitted without recomputation and original-reviewer affected recheck.
Root will use the existing control-plane gate and independent exact-blob readback;
review approval itself grants no push or new30B source/test authority.

### 30M guarded local integration

Independent reviewer re-bound `c07fe7d62418f50d9268f98ceb03fa45e9550bdf`:
only this report, checklist progress and a human index row changed from the
approved87b090ed. Machine JSON was byte-identical, both leaves and source code
unchanged; original APPROVED applied. Root ran the existing control-plane gate
regression: `python -m pytest tests/test_control_plane_mutation.py -q` exited0,
**54 passed,11 subtests passed in38.60s**. No unrelated04/Host tests were rerun.

Root asserted clean control HEAD=d000 and exact control candidate ref=c07 before
calling `admit_control_plane_mutation(JohnnyRootLayout(owned_temp),
ControlPlaneMutationRequest(repository_root=control_worktree,
integration_branch='codex/skill-improvement-checklist',
candidate_ref='control/skill-improvement-30m-docs',principal=host_user))`.
Result=`INTEGRATED`, failure=null, integrated_commit=c07fe7d6; actual HEAD matched.
The diff was exactly five allowed Markdown files, with no create/delete or
source/test change. This is LOCAL_INTEGRATED, never AUTHORITY_INTEGRATED.

Journal owner=Root/Ticket30M, exact root
`C:\Users\GameBoy\AppData\Local\Temp\johnny-ticket30m-integration-9mehmg_0`,
TTL=this session through evidence seal+independent readback, teardown=exact
registered journal and empty parent directories only. Actual journal is
`queue/document-mutation-journal.jsonl`; an initial read mistakenly looked for
`control-plane-mutation-journal.jsonl`, found nothing and made no mutation.
No missing evidence was invented. The final journal seal below precedes teardown.

Current metadata carrier updates only the registry/checklist/report with that
observed result. Ticket29/30 finalbytes/digests and the machineJSON remain exact;
the entire README blob changes legitimately with its human status row and must
be pinned anew. The original reviewer rechecks that narrow carrier before its
local gate. No independent network/readback or Host claim is introduced.

## Final30M decision seal / 30B exact candidate — 2026-10-18

Independent reviewer APPROVED the narrow8c9be916 carrier: only progress/report
text changed, machineJSON/leaves/source unchanged. Root then used the same
control-plane gate, exact checked-clean c07 base and same registered journal
root. Result INTEGRATED, no failure, actual control HEAD independently readable
as **`8c9be91650d3cfb59d53c24b55b9a65fb72118b3`**. This is the reviewed,
locally integrated **30B implementation baseline** and maximum proposed
publication target, not a moving HEAD. Subsequent review/cleanup ledger commits
do not automatically extend that implementation or remote range.

| Exact approved document input | Blob at8c9be916 |
| --- | --- |
| Context04 | `06baa4dea5db1c3370086552c35a1d8f721ad47e` |
| SPEC03 | `a700cad60de40096770582b04915bf490fd66a19` |
| Canonical PRD/CHG leaf | `1bc5e679944aeb6d7b830ccbf2b3fd768b599548` |
| Mainline index README | `4c0f6d55099eada140d84459210f65fed2fd36cd` |
| Ticket29 | `71a7c78e7d2a5b999b4663360516647c60848826` |
| Ticket30 /30B exact contract | `08146ff8e8afc9c886293bdcb57e4d5d2e94257b` |
| Reused30A product/test | `22a23be723bc34d9144575a81238d79ff5579485` / `ff6f66e8c6cd07fb956de3be72507038e2254ad0` |

Ticket29/30 raw digests remain exactly d6d3…e94f and f8d7…0785 (full values
above and in the index). Final index raw SHA256 is
`34612470130450329c62216ba95d2f9239443320f62c69774b0b6f348edc3139`.
The observed8c9be916 tree is `27e49ebc12b72be53719fa31f51560bda4c9d5a8`.
No source/test was edited. Root's guarded result and independent carrier
rebind satisfy30M-D4 locally;30A's consumed Grant remains consumed.

### Only Owner decisions remaining in this package

**1 — recommend APPROVE the prepared30B construction Grant, not new policy.**
`grant-ticket30b-readback-20261018`, NOT_ISSUED, binds exactly the baseline,
Ticket30 and index blobs in this seal; originalPRD/CHG/SPEC; proposed actors,
worktrees and MODIFY2/CREATE2 paths in Ticket30 §30B. Local tests network=0;
new command allocation600s/max120s each, prior expenditure preserved; existing
independent review, initial+onecorrection, exactdiff and guarded local integration.
New constructor seam is reviewed before behavior as already written in the
same candidate, no new authority issuer. After source publication and independent
review, conditionally permit one public GET-only readback, ≤10GET/200s,
≤20s/request/2MiB/blob, no retries/models/credentials/writes. Absent those
conditions, true-source positive verification stays UNAVAILABLE/NOT_VERIFIED;
local construction can proceed under its own valid Grant. No Host qualification,
receipt/spawn/interception, formal closure or release/deployment is authorized.

Exact reply:
> 核准Ticket30B：baseline `8c9be91650d3cfb59d53c24b55b9a65fb72118b3`，
> ticket blob `08146ff8e8afc9c886293bdcb57e4d5d2e94257b`，index blob
> `4c0f6d55099eada140d84459210f65fed2fd36cd`；依該票四路徑、30B-R1～R4、
> 原角色／worktree與600s新增命令額度，保留歷史耗用，完成本地實作、獨審、
> 同票一次修正及受控整合。測試預設network=0；條件式核准source正式到位、
> 獨審及effect前授權讀回後的一次10GET/200s公開唯讀驗證。不授權其他效果，
> 不啟用Host/dispatch/正式結案；不push、不release、不deployment。

**2 — recommend NO PUSH of the broader range at this point.** The directly
read old remoteSHA is `a1cb6c13adbeb52a4117991727dcc3d4af6d2a33` (rechecked
unchanged after the first local integration). If the owner instead authorizes
publication, the exact maximum range is:
`a1cb6c13adbeb52a4117991727dcc3d4af6d2a33..8c9be91650d3cfb59d53c24b55b9a65fb72118b3`,
129 commits,87 netpaths. This includes the earlier local checklist slices,
not just the five30M docs; no implicit approval of its other candidates or
activation follows. Complete range can be enumerated without asking the owner
to reconstruct it:

```text
git rev-list --reverse a1cb6c13adbeb52a4117991727dcc3d4af6d2a33..8c9be91650d3cfb59d53c24b55b9a65fb72118b3
git diff --raw --no-abbrev --no-renames a1cb6c13adbeb52a4117991727dcc3d4af6d2a33 8c9be91650d3cfb59d53c24b55b9a65fb72118b3 --
```

SHA256 of the exact first command's raw stdout bytes:
`e03faec67e1b8ba6a89a60964e1ea22f10eaca194e9ba42a2140117e3f333b75`;
second stdout bytes:
`be2e7c255968002b6c1da21539eebac5a6aba83dd590c3a6ac175349b80e9853`.
Target repository=`johnnyliu365-sys/Johnny_AI_Skill`, ref=`refs/heads/main`.
Any approved push must be nonforce, oldref reread exactly equal before push,
ancestry/scope/required review checked under existingpromotion; no rebase/force,
newcommit inclusion or providerMerge. Known dynamic DependencyGraph may run;
unobserved App/org automation remains UNKNOWN. Push completion requires direct
ls-remote exactnewSHA plus provider blob reads at thatSHA for Context04,
index andleaves/digests. Otherwise PUSH_UNCONFIRMED. A newremoteSHA halts only
this publication, not independent lawful local work. No push was executed.

### Journal seal before restricted teardown

Exact previously registered file:
`C:\Users\GameBoy\AppData\Local\Temp\johnny-ticket30m-integration-9mehmg_0\queue\document-mutation-journal.jsonl`.
Length2590 bytes, **four** JSONLrecords, SHA256
`8d845fcb7688c4a5ecbfc0d73e4874d479331a9460bed2a69690f90963c7319a`.
Records1/2 bind c07 with the five docs and outcomes ADMITTED/INTEGRATED;
records3/4 bind8c9be916 with only report/checklist/humanREADME progress and
outcomes ADMITTED/INTEGRATED. All have CONTROL_PLANE, host/principalGameBoy,
samecontrolintegrationbranch, no failure/offendingpath. An initial informal
"one record" expectation was corrected by independent actualJSONL readback;
no history was rewritten to fit it. This durable metadata+exactdigest is sealed
before removal. Necessary reviewed scripts/tests/commits remain in Git.

Only pending teardown targets are the two registered30M worktrees, their fully
integrated control branch, and this exactjournal/emptyparents, after independent
seal readback. Owner+TTL were recorded beforecreation. No force/reset/clean,
recursivebroaddelete, formalbranchrewrite or immediateGC is allowed. Other
programme tickets, R0/DAP/TAL and all Recovery holds are unchanged. FullTicket30
and checklist01/02 stay open; current Router return is ACTION_COMPLETED for
30M, then only30B implementation waits for this new preciseGrant. No other
source/test work with an existing independent validGrant was identified in this
boundedfeature inspection; none is revoked by the proposed new gates.

### Final independent readback and cleanup confirmed

The original independent reviewer read committed seal
`07b1e4123500fd3006db063e7704969bc1ba4dff` and the actual2590-byte/four-record
journal before teardown. SHA256, both gate outcomes, exact five-/three-doc
diffs, baseline8c, every pinnedblob/rawleafdigest, index mirrors, tree and
129-commit/87-path range/stdoutdigests all matched. The reviewer confirmed
GrantNOT_ISSUED/no push/no Host claim and both exact registered worktrees clean;
normal restricted teardown was permitted. No new full review or91-test rerun.

Root rechecked absolute paths are inside this repository's `.worktrees`, all
containment/target entries are non-reparse, exact Git roots/registration match,
both tracked/untracked statuses are clean, and both HEADs are ancestors of the
preserved control branch. Normal `git worktree remove` removed only
`.worktrees/skill-improvement-30m-docs` and `.worktrees/skill-improvement-30m-review`;
normal `git branch -d` removed only their fully integrated
`control/skill-improvement-30m-docs` ref. Root rechecked the journal's four lines,
digest, non-reparse identity and sole-child hierarchy, then native
`Remove-Item -LiteralPath` removed only its exact file and emptyqueue/root,
without recursion/force. Final Test-Path returnedfalse for allthree targets.

All source, tests, reviewed commits and seal evidence remain reachable from
`codex/skill-improvement-checklist`; no user/Recovery/other-ticket asset was
removed. Control worktree is clean. `30M = COMPLETE_LOCAL / CLEANUP_CONFIRMED`;
`ACTION_COMPLETED` returns to the existing Router. Only the new30B source/test
Grant and optional futurepublication require new authority; no source/test
implementation has begun. FullTicket30/checklist01/02 are not closed. The
30B baseline remains8c and the exactcandidate leaf/indexpins above do not move
with this cleanup-ledger-only commit.

## Batch delegation and 30B admission — 2026-10-18

Owner's `batch-checklist-local-20261018` authorizes Root-scoped local child Grants.
Independent `/root/batch_authority_review` APPROVED docs candidate
`930fad32e15a76cd54423e34ea941a630af039da` against `2e52772770e81669a7e1f92391a432572d4ead4b`.
Its sole finding (implementation no-helper versus mandatory reviewer audit) was
closed in that additive correction; qualified audit absence remains blocking.
Ticket blob `fb189f91d163c71f300b8bd40d24064dbc37c66e`, index blob
`40299be8a0ba9e21ac5f7cf88deba0cbc175a6f5`, checklist blob
`3b9f5e38f0aaa3195d39b43af07538c40204f8d3`; committed ticket SHA256
`32c6a4470d3181b24701fa484973ccf42797dbc50420e00d969fe48a20366b44`
matches index. Root and independent reviewer read the unique existing boundary
parser and committed mirrors; source/test blobs equal the previous8c baseline.
The earlier requirement to return to Owner per child is superseded only inside
this delegated batch. No new SPEC approval, runtime activation or external effect.

30B Grant is now effective for local construction. Bind source/allocation baseline
`930fad32e15a76cd54423e34ea941a630af039da`, exact ticket blob above, author
`/root/ticket30b_readback_impl`, reviewer `/root/ticket30b_readback_review`,
repository `.worktrees/skill-improvement-30b-readback`, branch
`codex/skill-improvement-30b-readback`. Root retains review/integration authority.
Before dispatch existing DTO preflight command
`python -m pytest tests/test_mainline_source.py -q -k 'path or result or request or observation or round_trip'`
passed38, deselected40 in4.10s; cumulative30B commands4.10/600s. Root's first
boundary check incorrectly passed the whole Markdown to the body-only parser;
the corrected unique-fence extraction passed, no product change or hidden retry.
New actual type-only constructors must pass independent review before behavior.
Network0, no formal effect. `ACTION_COMPLETED → AUTO_CONTINUE → IMPLEMENT`.

### 30B constructor phase

Author candidate `f13108b531b4b18c366b6803250899e038431a40` adds only the two
authorized new files (156 product/249 test lines). Author26tests, strict mypy,
compile and diff checks passed; first collection failed on an import and was
corrected, not omitted from timing. Total author/preflight commands74.25s.
Root allocated exact detached candidate in non-reparse contained
`.worktrees/skill-improvement-30b-readback-review`. Independent
`/root/ticket30b_readback_review` inspected the constructors/effect absence,
ran26tests (1.90s pytest), and rejected a raw enum-string probe as expected.
APPROVED_TYPE_PHASE_ONLY, no blocking finding; no audit/Host/integration claim.
Conservative cumulative budget charge87/600s includes independent commands.
Same author now continues behavior under the existing four-path Grant, without
network or actual dispatch. New phase does not reset budget or findings.

### 30B behavior, correction and final review boundary

Author `d798135002dc749dd367e53ecb253234a267ea9f` implements only the four
authorized paths. Focused command
`python -m pytest tests/test_mainline_source.py tests/test_mainline_projection.py tests/test_mainline_readback.py tests/test_project_authority_observation.py -q`
passed137; strict mypy on mainline_source/mainline_readback, compileall and diff
checks passed. Author bypassed identity and raw-anchor digest checks separately:
named tests failed with a leaked candidate, then passed after exact restoration.
No actual network, target reads, receipt, dispatch or native spawn.

Independent `/root/ticket30b_readback_review` found a real R2 defect: non-Context
revision validation accepted a prefix instead of the full approved SHA. Changing
only a PRD index revision's suffix while retaining approved raw bytes produced
a candidate; reviewer-owned negative cell failed, then was removed byte-exact.
Separately, removing final-ref `expected_sha` binding caused the existing moved-ref
cell to fail; restoring the exact source returned it to green. The initial
116-case source/readback suite was accidentally run twice by the reviewer;
both command durations were charged, not erased or called necessary work.

Same author additive correction `fd98f3958fa2d9ceca6d8a925efa27302c061df2`
reuses `_DocumentBinding.commit_sha` for all four anchors (no new DTO family).
Ordinary constructors and strict type checks passed before the comparison fix.
PRD/CHG/SPEC suffix-only substitutions first failed3cases, then passed after exact
full-SHA equality was required. Author full four-module suite140passed in42.14s,
strict mypy/compile/diff green. Same independent reviewer closed R2: focused3cases
passed, complete140passed in37.95s, exact candidate/ticket blob and clean tree
read back. The prior final-ref mutation remains valid for its unchanged path.

R1 remains UNVERIFIED, not PASS: a normally constructed binding with only its
grant_id changed to `grant-forged` still produced a candidate after10 fake
transport calls. This DTO explicitly is not authority; there is no production
admitted-control/Grant source readback in these four files. It cannot be used as
an authenticated effect entry. The ticket excludes arbitrary malicious
same-process callers, but that exclusion is not proof of a real trusted caller.
Root narrowly checked existing `dispatch_authority.py` (control b28b3ae2): its
`read_dispatch_grant` reads an owner-intent marker; the module explicitly states
it is not a cryptographic/process privilege boundary. Reusing that reader or
adding another fake approval bool would not qualify R1. No second authority
engine, Host privilege change or activation was added to conceal this gap.

Final verdict: ENGINEERING_PARTIAL / R2_CLOSED / R1_UNVERIFIED /
REVIEW_BLOCKED. Required HIGH_ASSURANCE qualified read-only adversarial audit
is also UNAVAILABLE. Existing CVQ-D9 source integration and D10 contract tests
are not a qualified actual Host/binary/config/source-isolation/no-code/
no-delegation observation. No integration; no whole-ticket or01/02 checkbox.

Structural review explicitly inspected the approximately875-line readback module
and770-line tests before correction: above350-line signals, but bounded DTO,
fixed GET transport and coordinator with shared parser/assembly; no new files
beyond the approved two, no duplicate graph/parser or parallel framework.
This is not permission for unbounded growth; final correction is +50/-9 over
two existing candidate files. Independent reviewer found no additional blocking
structural defect in this correction. Estimates are command-wall time only:
prior390/600s conservative, correction80s, finalreview45s =515/600s. Initial and
correction attempts remain in history; no budget reset or additional attempt.

Preserve author/reviewer worktrees, exact candidate ref and review evidence.
They are not cleanup-eligible while required review/source evidence is unresolved.
No R0, DAP-00 or Recovery hold changed. Other local batch work completed31B/44
without waiting for this candidate. Subsequent dependent dispatch/source effect
work cannot borrow this unapproved candidate as implementation authority.
