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
