# REVIEW — ticket 62 Known failures CI registers

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** The candidate code does what the ticket asks. Each fixed test passes in CI run 42107768107 on both jobs at the candidate. Each changed assertion follows current behaviour. None of them is a weakened test. The four pin rows per OS keep a cause I could confirm, and the generator gives the seat's `a6de33bd…` at the candidate. No finding against the code blocks approval.

One evidence finding blocks: S62-01. On the receipt as submitted, the R4-2 evidence gate (`evidence_gate.py`) exits 1 with `EXIT_MISMATCH M1`. The M1 cell lists `exit: 0`, but its capture holds `0,1,1,1,1,1,1,0`. A receipt that the R4-2 gate marks red is not complete evidence (CodeReview §5, last bullet), and approving over that red would treat a red gate as green. The correction is to rebuild the receipt only: no code change, no new commit and no new CI run. S62-02 and the receipt half of S62-03 can be fixed in the same rebuild. Under rule B none of the other findings blocks.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/62-registered-known-failures.md`, revision01 (state `IN_PROGRESS`: implementation returned, CHANGE_DETECTED for the marketplace re-pin routed to the owner, initial review dispatched) |
| Spec | workflow-governance Revision 04 R4-6; REQ-20261103-043 readiness criterion 2; ticket 59 findings S59-02, S59-03, S59-05 |
| Candidate | `bb9c4502ff4b0806787404d075f469fd42dea543` on `cp/wave2-62-registered-known-failures`. `git fetch` of `origin/cp/wave2-62-registered-known-failures` gives the same sha |
| Base | `92ee3a94b963747abede480f1f0a4936880a411e` (the dispatch base, parent of `076066f9`) |
| Commits | `076066f9` (fix) and `bb9c4502` (test). Author and committer on both: `Johnny Liu <johnny.liu365@gmail.com>`. Trailer on both: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-62_dispatch.yaml` (base, cells P1, T1, M1, C1, F1, P9; receipt rule "exit in capture order") |
| Review worktree | `.worktrees/62-registered-known-failures-review`, detached at the candidate; porcelain empty before and after every run |
| Receipt | `.worktrees/62-registered-known-failures-out/RETURN.md` (LF, 71983 bytes) |
| CI run | 42107768107, https://github.com/johnnyliu365-sys/Johnny_AI_Skill/actions/runs/42107768107, event `push`, `headSha` = candidate, both jobs `success`. The earlier run 42105962123 on `076066f9` was also `success`. Base comparison: run 42101907082 on `ea51e1c1` (the test tree is the same as at `92ee3a94`; between them only `doc/` and `modules/` change) |
| References applied | `CodeReview.md` (whole file, §5 rule B); `review-checks.md` (test truthfulness, reviewer counter-mutation points 1–5, token parsing, exception behaviour) |
| XSS / privileged JS | Not applicable: test files, a JSON list and a README; no browser, DOM or JavaScript surface |
| Agent control / task-worktree / profile fan-out / POC ancestry | Not applicable: no Agent control path, one implementer seat, no POC or staging. `gh run list` shows only two push runs on this branch, both on the seat's commits |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | acr6: what the changed live test pins | PASS (not weakened); S62-03a, S62-04 | The original live test called `_assert_exact_candidate_boundary(repository)`: baseline `6953f1e4` to `HEAD`, plus staged, unstaged and untracked paths, must equal the one test file. That held only while `HEAD` was the candidate. `5763caf5` is the integrated candidate of CAP-RWW6-01 (its review record and ticket name it), and `git diff --name-only 6953f1e4 5763caf5` is exactly that file. After integration, the `HEAD` form could never pass again. The new live test checks that `5763caf5` is an ancestor of `HEAD` and that the baseline-to-tip diff is the allowed set. That is a fact about the past. It goes red only if the tip leaves `HEAD`'s ancestry or the constants change. My RA3, a `--depth 1` clone without `5763caf5`, is red with `the candidate tip is not an ancestor of HEAD`, so the test fails closed and does not pass falsely. The rule itself, that a candidate's committed, staged, unstaged and untracked paths must equal the allowed set, is still pinned by the unchanged replica test: my RA2 (untracked component dropped) turns `test_acr6_committed_candidate_diff_and_forbidden_paths` red. My RA1 (an untracked file in the live checkout) is zero red. That is expected, because the live working tree is no longer the candidate, but it contradicts the STATEMENT's "the rule it pinned … is unchanged" (S62-03a) |
| 2 | acr6: is `5763caf5` present in every CI clone | PASS | Both jobs check out with `fetch-depth: 0` (Linux log line 36). `5763caf5` is an ancestor of `main`, `origin/main`, `cp/wave2-gates` and the candidate. A `pull_request` checkout with `fetch-depth: 0` also fetches the full history. A shallow clone is red (RA3), not falsely green |
| 3 | Router audit: which side is current | PASS | `router.py` (since `d06fd729`, 2026-09-24) suspends every transition into `REVIEW` with `TEST_REVIEW_NOT_ADMITTED` unless `state.review_scope_ref` and `event.test_report_ref` are both set and the gate admits the resolved report. `git log d06fd729.. -- library/workflow_router/router.py library/workflow_router/review_admission.py` is empty: the Router has not changed since. History probe RH: the unchanged pre-62 test **passes at `d06fd729^`** (`c8d1c88d`) and **fails at `d06fd729`** with `ADVANCE != SUSPEND`. So the SUSPEND comes from the admission gate, an intended Router change with its own tests (`tests/test_router_review_admission.py`, for example `test_bare_smoke_pass_is_refused_before_review`). It is not a later regression |
| 4 | Router audit: both branches pinned | PASS; S62-06 (pre-existing) | Bare audit: `SUSPEND`, `next_stage None`, `blockers[0].code == test_review_not_admitted`. Bound audit: `ADVANCE` to `REVIEW`, `resolver.calls == 1`. Seat MD1 (gate skipped) is red on the SUSPEND branch. My RD1 (the gate refuses every resolved report) is red at line 808 (`ADVANCE != SUSPEND`). My RD2 (admitted without consulting the resolver) is red at line 810 (`1 != 0`). My RD3 (a missing scope or report no longer suspends before the gate) is zero red in this file and in `test_router_review_admission.py`. With no resolver, the gate denies anyway (overlap-masking), so that arm is not pinned when a resolver is present: S62-06, outside the boundary |
| 5 | Refusal roster | PASS; S62-03b | The three enums exist at the candidate: `project_authority/contracts.py::_LifecycleFailure` (added by `6df6885e`, 2026-08-24), `project_authority/integration.py::AuthorityFinalizationFailure` (added by `98bafbab`, 2026-08-25, not `6df6885e` as the STATEMENT says) and `target_document_contracts.py::ManagedArtifactWriteFailure` (added by `1bca660f`, 2026-08-28). The roster test was last touched on 2026-08-24 (`84f41fc0`). The covered roster is unchanged. Counts 48→51 and 45→48 pass. My RE1 adds a new `Failure` enum to the library on the production side and is red (`uncovered_enums != _UNCOVERED_ROSTER`) |
| 6 | acr2/acr3 label `/` → `-` | PASS; S62-05 (pre-existing) | `_validate_bounded_label` is byte-unchanged (`[A-Za-z0-9._:+()=-]+`), so it is not loosened. The fix sits in `_linux_filesystem_backend`, a test helper. The new `test_acr2_linux_label_for_a_slash_named_filesystem_is_a_valid_token` fakes `stat` and runs on every host: it passed in my P1 on Windows and in both CI jobs. My RB2 (fix moved into the validator: `/` admitted and replace removed) turns the new test red. My RB1 (validator loosened, replace kept) is zero red: nothing pins the validator's refusal of a slash. That gap predates this ticket (S62-05) |
| 7 | File lock: does the POSIX path run on Linux CI | PASS | `file_lock.py` takes `fcntl.flock` whenever `sys.platform != "win32"`. Base Linux run 42101907082: `FAILED …test_a_waiter_is_held_out_and_then_let_in_rather_than_refused - ValueError: I/O operation on closed file`. Candidate Linux run: not in the FAILED list, not registered, checker exit 0. The test file has no skip, and the Linux skip count is 50 at base and 50 at the candidate. Linux went from 351 failed and 3176 passed to 345 failed and 3183 passed: six fixed tests plus one new test, so all six removed rows passed rather than being skipped. The base run is the natural reverse mutation on Linux: the closed-stdin form, red. My RC1 (closed-stdin form restored) is zero red on the Windows host. That is environment-scoped and expected: the guard lives in the Linux job, which runs on every push |
| 8 | Rows removed and kept, against CI | PASS | My own parse of the `FAILED` and `SUBFAILED` lines in both job logs. Linux: 227 ids plus the collection error `tests/test_codex_registration_contracts.py` = 228, equal to the registered set. Windows: 44 = 44. Base run: 233+1 = 234 and 47, equal to the base list. Every removed row is absent from the candidate's FAILED lines and present in the base run's. Windows went from 56 failed and 3358 passed to 53 failed and 3362 passed, with 34 skipped at both. The kept rows' failure texts: the four pin tests on both OS, `PinnedCommitError: the pinned sha names no commit in this repository: 0b3afd36…` (and `AssertionError … names no commit` for `test_the_pinned_sha_exists`); Windows acr2, `_PlatformProofUnavailable: LINUX`. `follow_up` counts: Linux 224 `environment` + 4 ticket 62; Windows 1 `environment` + 39 ticket 63 + 4 ticket 62. This matches `ci/README.md` |
| 9 | CHANGE_DETECTED (pin) | CONFIRMED; S62-08 | `git ls-remote` of the public `Johnny_AI_Skill_publication` gives `0b3afd36…` for `HEAD`, `refs/heads/main` and `refs/tags/plugin-v0.4.14` (lightweight). A blob-less fetch shows the commit has no `parent` line, and author and committer are `Johnny AI Skill <johnny-ai-skill@invalid> 0 +0000`. `git cat-file -t 0b3afd36…` in this repository fails. In a disposable clone with the tag fetched, three of the four pin tests pass and `test_l5_stale_candidate_pin_is_named_before_generation` fails (`live_diff.is_empty` false), as the seat says. The generator at the candidate, in a disposable clone, prints `publication commit a6de33bdd6eaab668f71f6b4d46557846f112805`, `repinned 0b3afd36… -> a6de33bd…`, `pin verified against the declaration`, exit 0. Neither `tests/` nor `ci/` is in the payload allowlist, so the value at `92ee3a94` and at the candidate is the same. Nothing was pushed or published, and the clone was discarded |
| 10 | Boundary | PASS | `git diff --name-only 92ee3a94 bb9c4502`: `ci/README.md`, `ci/registered-failures.json` and four test files, all `modify` paths of the boundary block. Nothing under `.claude-plugin/`, `skills/`, `.github/`, `template/` or the governance files. `git diff --check` is clean |
| 11 | Strong type | PASS for the diff; S62-07 (pre-existing) | `mypy --strict --python-version 3.11` on the four changed test files: `Success: no issues found in 4 source files`, exit 0. The diff adds no `Any`. `tests/test_refusal_guidance.py` already held an explicit `typing.Any` (line 21, `_entry` at 131–132, since `603a98db`). It is untouched by the diff but sits in a file this ticket modified: S62-07 |
| 12 | Ticket test files on the host (P1) | PASS | Same command as the seat's P1: `5 failed, 239 passed, 9 skipped, 420 subtests passed`, exit 1. The five failures are the four pin tests and acr2 (Windows, `_PlatformProofUnavailable: LINUX`), all registered rows the ticket keeps |
| 13 | `receipt_check.py` (P9) | PASS | `receipt defects: 0`, exit 0. All six cells `[ok]`, eight STATEMENT sections |
| 14 | `evidence_gate.py`, three wave-1 tools, six cells | **FAIL: S62-01** | `EXIT_MISMATCH M1: exit lists 0, capture holds 0,1,1,1,1,1,1,0` / `cells=6 defects=1`, exit 1. The three `tool_digest` values equal `sha256` of the blobs at the candidate. No other defect |
| 15 | LF, raw blocks, exit lists, M1 form | PARTIAL: S62-01, S62-02 | My own check: 0 CR in `RETURN.md` and in the six cell captures. Each fenced block is byte-identical to its capture. Exit fields equal the capture for P1 (1), T1 (0), C1 (0), F1 (1) and P9 (0), but not for M1 (S62-01). The M1 capture records the clone command (`git clone -c core.autocrlf=false --no-hardlinks …`), the diff, unfiltered pytest output and `porcelain=[]` after every restore. But MA1 and MA2 ran `-k acr6_exact` (`1 failed, 8 deselected`), not the full test file the dispatch asks for. The supporting capture `F1_other_pytest2.txt` holds 9 CR bytes (S62-02) |
| 16 | Seat F1 | PASS | `5 failed, 3397 passed, 36 skipped` under the lock acquired at 21:22:32Z. The failure set is a subset of the 12 base names. At acquisition the seat recorded no other pytest. An earlier capture with CR bytes, taken beside another seat's pytest, was discarded and named in the STATEMENT |
| 17 | My full suite under the host lock (F1) | PASS | `5 failed, 3397 passed, 36 skipped, 6839 subtests passed in 748.48s`, exit 1. The failures are the four pin tests and Windows acr2. All five are among the 12 base names in `C:/Temp/claude/jas48_F1_base.txt` (CR normalised, `^FAILED` lines), and nothing falls outside them: zero new red. Base names that no longer fail: `test_acr6_exact_test_only_boundary`, the router audit test and the roster test (fixed by this ticket), and `test_acr6_committed_candidate_diff_and_forbidden_paths`, `test_pinning_the_root_commit_is_rejected` and the two `test_workflow_router` temporal tests (not failing on the host at this candidate, as in ticket 59). Lock: acquired 21:46:23Z after a 31 s wait behind `run=jas63-F1b`; `owner.txt` = `run=62-rev01-initial-F1 2026-11-05T21:46:23Z`. At acquisition, the only process whose command line matched `pytest` was my own listing query, so no other pytest was running. Released 21:58:53Z by renaming to `jas-fullsuite.lock.released-62-rev01-initial-F1-1793915933` and removing it, after checking that `owner.txt` still named my run. Review worktree porcelain empty afterwards; 0 CR in `R_F1.txt`. All my mutation runs finished before I acquired the lock |
| 18 | Reviewer counter-mutations | 11 mutations and one history probe: 6 red, 5 zero red (each explained; S62-03a, S62-05, S62-06) | Table below |

### Rows of the ticket

| Row (ticket) | OS | Status at the candidate | Confirmed by |
| --- | --- | --- | --- |
| `test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists` | Linux, Windows | Kept, `follow_up` ticket 62; cause rewritten | CI text `names no commit`; ls-remote and the parentless publication commit; fetched-commit probe; tests untouched (cells 8, 9) |
| `test_plugin_publication.py` `test_l5_stale_candidate_pin_is_named_before_generation`, `test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable`, `test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor` | Linux, Windows | Kept, `follow_up` ticket 62; cause rewritten; CHANGE_DETECTED `a6de33bd…` | Same as above; generator rerun at the candidate (cell 9) |
| `test_atomic_conditional_replace_capability.py::test_acr6_exact_test_only_boundary` | Linux, Windows | Removed; passes in CI | Cells 1, 2, 8 |
| `test_guarded_integration_corrections.py::ReceiptBoundCorrectionTests::test_reviewed_router_profile_composes_return_integration_and_audit` | Linux, Windows | Removed; passes in CI | Cells 3, 4, 8 |
| `test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered` | Linux, Windows | Removed; passes in CI | Cells 5, 8 |
| `test_atomic_conditional_replace_capability.py::test_acr2_linux_requires_an_actual_linux_kernel_and_backend` | Linux | Removed; passes in CI | Cells 6, 8 |
| same acr2 | Windows | Kept, `environment` (no Linux backend, `_PlatformProofUnavailable: LINUX`) | CI Windows text; host P1 |
| `test_atomic_conditional_replace_capability.py::test_acr3_acm1_current_python_abstraction_final_window_qualifies_no` | Linux | Removed; passes in CI | Cells 6, 8 |
| `test_file_lock.py::BlockingAcquisitionTests::test_a_waiter_is_held_out_and_then_let_in_rather_than_refused` | Linux | Removed; passes in CI on the `fcntl.flock` path | Cells 7, 8 |
| Counts | — | Linux 234 → 228, Windows 47 → 44 | Cell 8; `ci/README.md` states both |

### Reviewer counter-mutations

All ran in a disposable clone: `git clone -c core.autocrlf=false --no-hardlinks <review worktree> <scratch>/mut`, detached at the candidate. Each mutation ran on its full test file, with `python -m pytest <file> -q -p no:cacheprovider -rf` called directly and no output-reducing wrapper. I judged red or green from the full saved output (`R_M1.txt`). Each was restored with `porcelain=[]`. On the host, `test_acr2_linux_requires_…` fails in every run of the acr file (registered, Windows). It is the baseline and not counted as red below.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| RA1 | Environment | an untracked `tests/zz_untracked_probe.py` in the live checkout | Zero red (baseline only). Expected: the live working tree is no longer the candidate. Recorded against the STATEMENT (S62-03a) |
| RA2 | Copy → production of the rule | `_candidate_change_paths` drops `untracked` | Red: `test_acr6_committed_candidate_diff_and_forbidden_paths`. The HEAD-relative rule is still pinned |
| RA3 | Environment | `git clone --depth 1` (no `5763caf5`) | Red: `test_acr6_exact_test_only_boundary` (`the candidate tip is not an ancestor of HEAD`), plus the replica test. Fails closed |
| RB1 | Overlap-masking | `_validate_bounded_label` admits `/`, replace kept | Zero red: S62-05 |
| RB2 | Copy | validator admits `/` and replace removed (the fix moved into the validator) | Red: `test_acr2_linux_label_for_a_slash_named_filesystem_is_a_valid_token` |
| RC1 | Environment-scoped | `waiter.stdin.close()` restored | Zero red on the Windows host, as expected. The Linux red is base run 42101907082 (`ValueError: I/O operation on closed file`) |
| RD1 | Production | `ReviewAdmissionGate.evaluate` denies every resolved report | Red: line 808, `ADVANCE != SUSPEND` |
| RD2 | First match | the gate admits without calling the resolver | Red: line 810, `1 != 0` (`resolver.calls`) |
| RD3 | Overlap-masking | `if review_request is None` suspend removed | Zero red in `test_guarded_integration_corrections.py`: S62-06 |
| RD3b | Overlap-masking | RD3 against `tests/test_router_review_admission.py` | Zero red (5 passed): S62-06 |
| RH | History | the unchanged pre-62 Router test at `d06fd729^` and at `d06fd729` | Passes at the parent; fails at `d06fd729` (`ADVANCE != SUSPEND`) |
| RE1 | Production | a new `ReviewerProbeFailure(str, Enum)` in `library/workflow_router/telemetry.py` | Red: `test_every_failure_enum_in_the_library_is_covered_or_uncovered` |

### New findings

| ID | Class | Blocks | Finding | Route |
| --- | --- | --- | --- | --- |
| S62-01 | `EVIDENCE_DEFECT` (receipt; R4-2 evidence gate red) | **Yes**, under §5 "evidence complete" | The M1 cell lists `exit: 0`. Its capture holds the exit lines `0,1,1,1,1,1,1,0`: the clone, six red mutations and the final summary. The dispatch requires "exit in capture order", and `evidence_gate.py` with the three wave-1 tools gives `EXIT_MISMATCH M1 … cells=6 defects=1`, exit 1. `receipt_check.py` does not catch it. The capture itself is correct and every mutation is red, so the candidate code is not affected. But the receipt as submitted fails the R4-2 gate, and approving over that red would treat a red gate as green | Correction: rebuild `RETURN.md` with M1 `exit: 0, 1, 1, 1, 1, 1, 1, 0` (or one capture per mutation), rerun P9 on the rebuilt receipt, and confirm `evidence_gate.py` `defects=0`. No code change, no new commit and no new CI run |
| S62-02 | `EVIDENCE_DEFECT` (receipt form) | No | (a) MA1 and MA2 ran with `-k acr6_exact` (`1 failed, 8 deselected`). The dispatch says each mutation runs with its full test file. (b) The supporting capture `F1_other_pytest2.txt` holds 9 CR bytes (PowerShell `Format-List` output), and the receipt rule is LF | Same receipt rebuild: rerun MA1 and MA2 on the full file, normalise the capture |
| S62-03 | `EVIDENCE_DEFECT` (STATEMENT accuracy) | No | (a) acr6: "The rule it pinned … is unchanged" overstates the change. The live test no longer reads staged, unstaged or untracked paths (RA1 zero red). That half is still pinned by the replica test (RA2 red), and the STATEMENT should say where it lives. (b) The roster STATEMENT gives `6df6885e` as the origin of `AuthorityFinalizationFailure`. That enum was added by `98bafbab` (2026-08-25), a later commit of the same `project_authority` package. The in-code comment ("same feature") is loosely true, and the STATEMENT should name the commit | Same receipt rebuild (STATEMENT only; the code comment need not change) |
| S62-04 | `OUT_OF_SCOPE_HARDENING` | No | `test_acr6_exact_test_only_boundary` is now a historical-record check. It can go red only if `5763caf5` leaves `HEAD`'s ancestry (RA3) or its constants change. That is the honest residue of a candidate-time test after integration, and I do not count it as weakened. But the same pattern (a "live" boundary test that reads `HEAD`) will go stale for every future candidate-boundary test | Control plane: decide whether candidate-time boundary tests should be written against a fixed tip from the start, or retired after integration |
| S62-05 | `OUT_OF_SCOPE_HARDENING` (pre-existing) | No | No test pins that `_validate_bounded_label` refuses a path-like label (RB1 zero red). The ticket did not ask for it, and the validator is test-harness code | Follow-up hardening ticket (test file) |
| S62-06 | `OUT_OF_SCOPE_HARDENING` (pre-existing, outside the boundary) | No | The Router's "missing scope or report → suspend before the gate" arm is not pinned while a resolver is present. Every bare-entry test uses `RouterEngine()` with no resolver, whose gate denies anyway (RD3, RD3b zero red). My RD3 form crashes rather than admits, so this is not shown to be a "would let a bad change through" gap | Follow-up hardening ticket on `tests/test_router_review_admission.py` |
| S62-07 | `OUT_OF_SCOPE_HARDENING` (pre-existing P0 debt) | No for this candidate | `tests/test_refusal_guidance.py` holds an explicit `typing.Any` (line 21; `_entry(**overrides: Any) -> dict[str, Any]` at 131–132; since `603a98db`). The ticket modified that file but not those lines, and the diff adds no `Any`. `tests/test_managed_artifact_planning.py` and `tests/test_ui_reference_renderer_admission.py` also import `Any`. This is source-type P0 debt on the base, not something this candidate introduced or passed inward | Control plane: a dedicated P0 cleanup ticket for the three test files. If the control plane reads the ticket's "no `Any`" as file-level rather than diff-level, this becomes a `TICKET_DEFECT` |
| S62-08 | `REQUIREMENT_CHANGED` (confirms the seat's CHANGE_DETECTED) | No (rows stay registered, as the ticket says) | Pin `a6de33bd…` confirmed at the candidate. For the owner's re-pin: `_clone_real_publication` calls `require_existing_commit(_REPO_ROOT, sha)`, and the tests expect the anchor `refs/heads/publication-0.4.14` (`_RELEASE_VERSION`). So the four rows turn green in CI only when the pinned commit is also reachable from a ref of this repository (like the existing `refs/heads/publication-0.4.9`), not only from the publication repository. The value changes whenever a payload path changes before publication | Owner publication step, as routed |

S59-02, S59-03 and S59-05, the ticket 59 findings routed here, are closed by this candidate. The acr2/acr3 and file-lock rows are fixed and gone (S59-02, S59-03). Of the seven OS-independent rows per OS (S59-05), three are fixed and gone, and the four pin rows carry a confirmed cause with ticket 62 as `follow_up`, pending the owner's re-pin.

### Commands

- `git fetch origin cp/wave2-62-registered-known-failures` → `bb9c4502…`; `git log --format='%H %an <%ae> | %cn <%ce>%n%B' 92ee3a94..bb9c4502`; `git diff --stat|--name-only|--check 92ee3a94 bb9c4502`
- `git log -- tests/test_atomic_conditional_replace_capability.py`; `git diff --name-only 6953f1e4 5763caf5`; `git merge-base --is-ancestor 5763caf5 {main,origin/main,cp/wave2-gates,HEAD}`; `git grep 5763caf5 92ee3a94 -- doc modules`
- `git show d06fd729 -- library/workflow_router/router.py`; `git log d06fd729.. -- library/workflow_router/router.py library/workflow_router/review_admission.py` (empty)
- `git log -S"class <enum>" -- <file>` for the three enums
- `gh run view 42107768107 --json headSha,conclusion,event,headBranch,url,jobs`; `gh run view 42107768107 --job {127527021140,127527021360} --log`; `gh run view 42101907082 --job {127506578548,127506577809} --log`; `gh run list --branch cp/wave2-62-registered-known-failures`; my parser `parse_ci.py` over `FAILED`/`ERROR`/`SUBFAILED(...)` lines against `ci/registered-failures.json` at the candidate and at `92ee3a94`
- `git ls-remote https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication`; `git fetch --filter=blob:none … refs/tags/plugin-v0.4.14` into a scratch bare repository; `git cat-file -p 0b3afd36…`
- In a `--no-hardlinks` scratch clone at the candidate: `python -m library.local_orchestration.plugin_publication --repo . --manifest .claude-plugin/plugin.json --marketplace .claude-plugin/marketplace.json --ref refs/heads/publication-gen` → `a6de33bd…`, exit 0 (then restored and the ref deleted); the tag fetched, then the four pin tests → `1 failed, 3 passed`
- `python -m pytest <the seven P1 files> -q -rfEs -p no:cacheprovider` → `5 failed, 239 passed, 9 skipped`, exit 1
- `python -m mypy --strict --python-version 3.11 <four changed test files>` → exit 0
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out>/RETURN.md <review>` → `receipt defects: 0`, exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out>/RETURN.md --repo <review> --candidate bb9c4502… --tool skills/johnny-project-takeover/scripts/dispatch_lint.py --tool skills/johnny-project-takeover/scripts/receipt_fence_check.py --tool skills/johnny-project-takeover/scripts/index_pins.py --require-cell P1 --require-cell T1 --require-cell M1 --require-cell C1 --require-cell F1 --require-cell P9 --evidence-root <out>` → `EXIT_MISMATCH M1 …`, `cells=6 defects=1`, exit 1
- my receipt check `rcheck.py` (CR count, fenced block versus capture, exit field versus `exit=` lines)
- the counter-mutation scripts `muts.py` and `muts2.py`, plus the shallow-clone run, appended to `R_M1.txt`
- F1: `python -m pytest tests -q -p no:cacheprovider` in the review worktree, under `C:/Temp/claude/jas-fullsuite.lock` (mkdir to acquire, `owner.txt` with the run id and time, the process list at acquisition, release by rename then remove after the owner check) → `5 failed, 3397 passed, 36 skipped`, exit 1

### Raw-log note

Every pytest, mypy, gate and git command was run directly, with no output-reducing wrapper. Full outputs were saved under `.worktrees/62-registered-known-failures-review-scratch/` (`R_P1.txt`, `R_T1.txt`, `R_P9.txt`, `R_GATE.txt`, `R_M1.txt`, `R_F1.txt`, `R_F1_lock.txt`, `R_F1_other_pytest.txt`, the four CI job logs and `gen_bb9c4502.txt`). Red and green were judged from those full files. In the conversation I only displayed excerpts of them (grep and tail).

### Not verified

- A Linux-side counter-mutation of the POSIX `fcntl.flock` path (for example `LOCK_EX` → `LOCK_EX | LOCK_NB`). Neither the seat nor I ran one: the host has no Linux Python (WSL holds only `docker-desktop`). The POSIX evidence is the base Linux red and the candidate Linux green.
- Per-test pass status in CI. The workflow uploads no junit artifact. "Passed, not skipped" for the removed rows comes from the FAILED lists, the unchanged skip counts and the exact passed-count deltas (+7 Linux, +4 Windows).
- The publication itself. `a6de33bd…` was generated in a discarded clone only. The version bump, the anchor ref and the publication push are the owner's.
- The Windows-host behaviour of `_linux_filesystem_backend` against a real `stat` (the new test fakes it; Windows acr2 stays an environment row).

```review-verdict
candidate: bb9c4502ff4b0806787404d075f469fd42dea543
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/62-rev01-initial
reviewed_at: 2026-11-06
```

## Revision01 correction review

**Verdict: `APPROVED`.** Correction 1 rebuilt only the receipt, as the initial review asked. It closes S62-01, S62-02 and S62-03:
- On the receipt as returned, the R4-2 evidence gate gives `cells=6 defects=0` and `receipt_check.py` gives 0 defects.
- Every exit list follows its capture in order.
- MA1 and MA2 are rerun on the full test file, and every referenced capture is LF.
- The two STATEMENT corrections are accurate.

The candidate is still `bb9c4502` with no new commit, so the initial review's code findings stand unchanged. No finding blocks approval. S62-04 to S62-08 are carried as Correction 1 routes them.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/62-registered-known-failures.md`, revision01, section "Correction 1" read at `cp/wave2-gates` `0c46ff07` |
| Candidate | `bb9c4502ff4b0806787404d075f469fd42dea543`, unchanged. Local `cp/wave2-62-registered-known-failures`, `git ls-remote origin refs/heads/cp/wave2-62-registered-known-failures` and the seat worktree HEAD all name it. The seat worktree's porcelain is empty |
| Commits | None new. `gh run list --branch cp/wave2-62-registered-known-failures` still shows only 42107768107 (`bb9c4502`) and 42105962123 (`076066f9`) |
| Receipt | `.worktrees/62-registered-known-failures-out-c1/RETURN.md` (LF, 75409 bytes) |
| Review worktree | `.worktrees/62-registered-known-failures-review`, detached at the candidate; porcelain empty before and after |
| Scratch | `.worktrees/62-registered-known-failures-review-scratch/rev01c/` (`C_P9.txt`, `C_GATE.txt`, this section) |
| Full suite | Not rerun. The candidate is unchanged, the seat's F1 capture is byte-identical to the one checked in the initial review, and my own locked F1 at this candidate (initial review, cell 17) stands |
| References applied | `CodeReview.md` §5 (correction review, rule B); `review-checks.md` (receipt evidence; reviewer counter-mutation point 5, unfiltered output) |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| C1 | `receipt_check.py` | PASS | `receipt defects: 0`, exit 0; P1, T1, M1, C1, F1 and P9 `[ok]`; eight STATEMENT sections |
| C2 | `evidence_gate.py`, three wave-1 tools, six cells | PASS | `cells=6 defects=0`, exit 0 (`C_GATE.txt`). It matches the seat's own gate capture `E1.txt` |
| C3 | Exit lists against captures | PASS | My check (`rcheck.py`): P1 `1`=`1`, T1 `0`=`0`, M1 `0, 1, 1, 1, 1, 1, 1, 0` = capture `0,1,1,1,1,1,1,0`, C1 `0`=`0`, F1 `1`=`1`, P9 `0`=`0`. Every fenced block is byte-identical to its capture, and every cell names the candidate |
| C4 | LF | PASS | 0 CR in `RETURN.md` and in all nine files of the out directory, including `F1_other_pytest_lf.txt` (281 bytes). That file equals the earlier `F1_other_pytest2.txt` with its CR bytes removed, byte for byte. The receipt names `F1_other_pytest2.txt` only to say it is no longer referenced. The only other `.txt` names in the receipt (`rev04-D1.txt`, `rev05-D4.txt`) are file paths inside pytest assertion output, not capture references |
| C5 | New M1 capture | PASS | The first line records the clone command (`git clone -c core.autocrlf=false --no-hardlinks …/62-registered-known-failures C:/Temp/claude/jas62-mut/clone`), then `clone HEAD bb9c4502…`. MA1 now runs `pytest tests/test_atomic_conditional_replace_capability.py` (full file): `2 failed, 7 passed`, red on `test_acr6_exact_test_only_boundary` besides the host baseline acr2. MA2 (full file): `3 failed, 6 passed`, red on `test_acr6_exact_test_only_boundary` and `test_acr6_committed_candidate_diff_and_forbidden_paths`. MB1, MC1, MD1 and ME1 were rerun with the same results as before. Each run has its diff and unfiltered pytest output, and `porcelain=[]` after every restore. No `-k` or `deselected` remains |
| C6 | Unchanged captures | PASS | `cmp`: `F1.txt`, `P1.txt`, `T1.txt`, `C1.txt` and `F1_lockwait2.txt` are byte-identical to the captures I checked in the initial review |
| C7 | STATEMENT corrections | PASS | `diff` of the STATEMENT sections between the two receipts. The acr6 STATEMENT now says the live test is narrower: it pins a fact about `5763caf5` and no longer reads staged, unstaged or untracked paths, and the replica test still pins the full rule. That matches my RA1 (zero red) and RA2 (red). The roster STATEMENT now gives `_LifecycleFailure` 6df6885e, `AuthorityFinalizationFailure` 98bafbab (2026-08-25) and `ManagedArtifactWriteFailure` 1bca660f, which matches `git log -S`. The host-runs STATEMENT names the LF copy. No other receipt line changed except the M1 block, M1 `exit:`, the P9 capture and timing or temp-path lines inside pytest output |

### Status of the revision01 findings

| ID | Class | Status | Note |
| --- | --- | --- | --- |
| S62-01 | `EVIDENCE_DEFECT` | **Closed** | Cells C1, C2, C3 |
| S62-02 | `EVIDENCE_DEFECT` | **Closed** | Cells C4, C5 |
| S62-03 | `EVIDENCE_DEFECT` | **Closed** | Cell C7 |
| S62-04 | `OUT_OF_SCOPE_HARDENING` | Carried | To a later hardening change (Correction 1) |
| S62-05 | `OUT_OF_SCOPE_HARDENING` | Carried | With S62-06 (Correction 1) |
| S62-06 | `OUT_OF_SCOPE_HARDENING` | Carried | To a later hardening change (Correction 1) |
| S62-07 | `OUT_OF_SCOPE_HARDENING` (pre-existing P0 debt) | Carried | To a P0 cleanup ticket for the three test files (Correction 1) |
| S62-08 | `REQUIREMENT_CHANGED` | Carried | To the owner's publication step. The four pin rows stay registered until the pinned commit is also reachable from a ref in this repository (Correction 1) |

### New findings

None.

### Commands

- `git fetch origin cp/wave2-62-registered-known-failures cp/wave2-gates`; `git rev-parse cp/wave2-62-registered-known-failures`; `git ls-remote origin refs/heads/cp/wave2-62-registered-known-failures`; `git -C .worktrees/62-registered-known-failures rev-parse HEAD` and `status --porcelain`; `gh run list --branch cp/wave2-62-registered-known-failures`
- `git show 0c46ff07:modules/tickets/workflow-governance/62-registered-known-failures.md` (section "Correction 1")
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out-c1>/RETURN.md <review>` → `receipt defects: 0`, exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out-c1>/RETURN.md --repo <review> --candidate bb9c4502… --tool skills/johnny-project-takeover/scripts/dispatch_lint.py --tool skills/johnny-project-takeover/scripts/receipt_fence_check.py --tool skills/johnny-project-takeover/scripts/index_pins.py --require-cell P1 --require-cell T1 --require-cell M1 --require-cell C1 --require-cell F1 --require-cell P9 --evidence-root <out-c1>` → `cells=6 defects=0`, exit 0
- `rcheck.py <out-c1>` (CR counts, fenced block versus capture, exit field versus `exit=` lines)
- `cmp` of F1, P1, T1, C1 and F1_lockwait2 between the two out directories; `tr -d '\r' < F1_other_pytest2.txt | cmp - F1_other_pytest_lf.txt`
- `diff` of the two `RETURN.md` files and of their STATEMENT sections; `grep` of the new `M1.txt` for its commands, summaries and `exit=` lines

All commands were run directly, with no output-reducing wrapper. The gate outputs are saved in full.

### Not verified

- I did not rerun the seat's six mutations. I read their new capture. My own counter-mutations from the initial review stand, because the candidate is unchanged.
- No full suite, as stated in the field table.
- Everything listed under "Not verified" in the initial review still applies: the Linux-side flock mutation, per-test CI pass status, and the publication itself.

```review-verdict
candidate: bb9c4502ff4b0806787404d075f469fd42dea543
verdict: APPROVED
reviewer: seat:ticket-review/62-rev01-correction
reviewed_at: 2026-11-06
```
