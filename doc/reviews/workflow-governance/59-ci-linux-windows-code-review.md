# REVIEW — ticket 59 CI on Linux and Windows

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** The workflow, the checker and the CI evidence do what the ticket asks. Run 42016463075 is green on both jobs, at the candidate, and the junit checker decided the result. One finding blocks approval: S59-01, an explicit `typing.Any` in the ticket's test file, which breaks the source-type P0. The fix is mechanical. The same correction should also close S59-02, -03, -06, -07 and -11, which are all inside the five boundary paths. S59-04, -05 and -08 go to the control plane. Under rule B none of them blocks on its own.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/59-ci-linux-windows.md`, revision01 (state `IN_PROGRESS`, initial review dispatched) |
| Spec | workflow-governance Revision 04 R4-6; REQ-20261103-043 readiness criterion 2, as the ticket quotes it |
| Candidate | `3ab5ac439eb726ec28e5e455f2cb44ccfb1bd9f8` on `cp/wave2-59-ci-linux-windows`; `origin/cp/wave2-59-ci-linux-windows` is the same sha |
| Base | `e760d2e8ad41563f18bab7ed367c2eeeeafcf3a9` (the dispatch base, an ancestor of the candidate) |
| Commits | `3450a5ff`, `aa4206b8`, `1d1d1933`, `3ab5ac43`. Author and committer on all four: `Johnny Liu <johnny.liu365@gmail.com>`. Trailer on all four: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` (the model that did the work; correct) |
| Review worktree | `.worktrees/59-ci-linux-windows-review`, detached at the candidate, porcelain empty before and after |
| Receipt | `.worktrees/59-ci-linux-windows-out/RETURN.md` (LF, 90108 bytes) |
| CI run | 42016463075, https://github.com/johnnyliu365-sys/Johnny_AI_Skill/actions/runs/42016463075, `headSha` = candidate, event `push` |
| References applied | `CodeReview.md` (whole file, §5 rule B); `review-checks.md` (test truthfulness, reviewer counter-mutation, error-code consistency, exception behaviour, path identity, authorization) |
| XSS / privileged JS | Not applicable. No browser, DOM or JavaScript surface: a YAML workflow and a stdlib command-line checker |
| Agent control / task-worktree / profile fan-out / POC ancestry | Not applicable. No Agent control path; one implementer seat; no POC or staging. The seat pushed only its own branch: `gh run list` shows four push runs, all on `cp/wave2-59-ci-linux-windows` |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1a | Triggers, matrix, Python, checkout, identity, `PYTHONUTF8` | PASS | `push: branches: ["**"]` and `pull_request`. Matrix is `ubuntu-latest`/linux and `windows-latest`/windows with `fail-fast: false`. Python `3.11` (the runners logged 3.11.17 and 3.11.9). `fetch-depth: 0` with `persist-credentials: false`. Neutral identity `ci <ci@users.noreply.invalid>`. Job-level `PYTHONUTF8: "1"` |
| 1b | Checker's exit is the job's result | PASS (behaviour); not pinned (S59-06) | The pytest step ends in `\|\| echo "pytest exit=$?"`, and the checker step has no `continue-on-error`. Steps 6 and 7 both `success` in both jobs. In the log both jobs show `pytest exit=1`, then the checker step with no output and exit 0 |
| 1c | Actions pinned to a full sha with a version comment | PASS | `actions/checkout@d23441a4…af803` (`# v6.1.0`) and `actions/setup-python@ece7cb06…61a1` (`# v6.3.0`). `gh api repos/<repo>/git/ref/tags/<tag>` shows each tag pointing at that same commit |
| 1d | No secret read; `contents: read` | PASS (behaviour); partly pinned (S59-07) | One top-level `permissions: contents: read`; no `secrets.`, no `github.token`, no `GITHUB_TOKEN` |
| 1e | `--continue-on-collection-errors` | Justified; ticket text to follow (S59-08) | Run 42009508339 (before the flag): the Linux job shows `Interrupted: 1 error during collection` and `1 error in 4.61s`, so no test ran. In my real-pytest probe, a module that fails to import becomes `<testcase classname="" name="tests.test_b_broken"><error/>`. The checker maps that to `tests/test_b_broken.py`, and an unregistered one gives `UNREGISTERED_FAILURE tests/test_b_broken.py`, exit 1. Registering it gives exit 0. The registered Linux collection error, `tests/test_codex_registration_contracts.py`, is listed by name |
| 2a | Row counts; reasons against the CI log | PASS with exceptions (S59-02, S59-03) | 234 Linux and 47 Windows rows; 27 and 7 distinct reasons; no reason says "flaky". I parsed the `FAILED`, `SUBFAILED(...)` and collection `ERROR` lines of run 42016463075. Linux: 204 FAILED + 147 SUBFAILED = 233 unique ids, plus the collection error = 234, the same set as registered. Windows: 45 + 11 = 47, the same set. I read the failure text of 46 Linux rows (at least one per reason, two where the reason had two or more rows) and of all 47 Windows rows. Every sampled text matches its reason, except the three Linux rows in S59-02 and S59-03 |
| 2b | Any product or test defect registered as `environment` | FINDINGS (S59-02, -03, -04) | Linux: `test_acr2`/`test_acr3` (a test validator bug on a real Linux kernel) and `test_file_lock` (a POSIX `communicate()` misuse on a shipped POSIX code path). Windows: the 39 rows under the 8.3 short temp path (a containment refusal on a supported platform) |
| 2c | Linux 234 versus the host base | Explained below; meets the criterion's letter for the genuine environment rows | See "Linux groups" |
| 2d | No test skipped, deleted or weakened | PASS | `git diff --name-only e760d2e8 3ab5ac43` shows exactly the five created paths. No existing test file changed; no `skip`/`xfail`/marker added; no conftest change |
| 3a | Exits 0/1/2/3 and the three codes | PASS | 38/38 ticket tests pass. My probes: an interrupted session (a test calling `pytest.exit()` or raising `KeyboardInterrupt`) writes an empty `<testcase/>`, which the checker refuses (`INPUT_ERROR a testcase has no name`, exit 2), so an interrupted run is a fault, not green. `pytest.exit()` at import becomes a collection error, red. A bad `--os` value with a newline gives exit 3 and an escaped message |
| 3b | `REGISTERED_NOT_FAILING` | PASS | Skipped or absent registered test → exit 1 (test and mutation MK red) |
| 3c | Errors count as failures; exact ids | PASS | A real teardown error gives `<error>`, counted as failed. A unittest `subTest` failure gives one `<testcase>` with `<failure>`; a `subtests` fixture failure gives one `<testcase>` with two `<failure>`. Case (`Tests/…` vs `tests/…`) is compared exactly. Case folding and whitespace stripping are not pinned (S59-10) |
| 3d | Malformed XML/JSON exit 2; DOCTYPE and entities refused | PASS for UTF-8; gap for other encodings (S59-09) | A nested-entity expansion attack ("billion laughs") is stopped by expat 2.6.0 (`ParseError`, exit 2). A UTF-16 report with a DOCTYPE and an internal entity gets past the byte search and the entity is expanded |
| 3e | Every printed subject on one escaped line | PASS | `t[&#x85;&#x2028;&#13;&#9;\]` printed as `t[\x85\u2028\r\t\\]` on one line; `INPUT_ERROR` and usage lines escaped; output pure ASCII |
| 3f | Reviewer counter-mutations | 16 run: 9 red, 7 zero red (S59-06, -07, -10) | `R_M2.txt`; table below |
| 4 | CI evidence | PASS | `gh run view 42016463075 --json headSha,conclusion,jobs`: headSha = candidate; `test (linux)` and `test (windows)` both `success`, with step 7 "Compare failures with the registered list" `success` in each. Both logs show `pytest exit=1` before the checker (Linux `351 failed, 3081 passed, 49 skipped, 2 errors`; Windows `56 failed, 3263 passed, 33 skipped`). So the green comes from the junit checker, not from a pytest exit of 0 |
| 5 | `ci/README.md` host-versus-runner differences | PASS with gaps (S59-11) | The 8.3 path (`C:/Users/RUNNER~1`) is named with its cause. Line endings are named, and the log confirms them: Windows `file:C:/Program Files/Git/etc/gitconfig true`, Linux `core.autocrlf is not set`. Of the four host-only failures, three have a cause; `test_pinning_the_root_commit_is_rejected` has none. None of the four failed on the host at the candidate in either locked run (the seat's and mine) |
| 6a | `receipt_check.py` | PASS | exit 0, `receipt defects: 0`, with P1, T1, M1, C1, F1 and P9 all `[ok]` |
| 6b | `evidence_gate.py` with the three wave-1 tools | PASS | `--candidate 3ab5ac43… --tool dispatch_lint.py --tool receipt_fence_check.py --tool index_pins.py --require-cell P1 … P9 --evidence-root <out>` → `cells=6 defects=0`, exit 0. The three digests equal `sha256` of the blobs at the candidate |
| 6c | LF, raw blocks, exit lists | PASS | My own check: 0 CR in the receipt and in every capture. Each fenced block is byte-identical to its capture. Each `exit:` equals the `exit=` lines of its capture (0, 0, 0, 0, 1, 0) |
| 6d | C1 holds `gh run view --json jobs` | PASS | Keys `conclusion, headSha, jobs, url`; both job conclusions `success` |
| 6e | Seat F1 ran beside an unlocked pytest | Valid as seat evidence; superseded by my F1 | The seat recorded `pytest tests/test_governance_consistency.py` (PIDs 49748/16084) starting eight seconds before its locked run. That run's failures are 8 of the 12 base names and none outside them. Contamination of a shared runtime root adds red; it does not turn red green. My locked F1 gives the same 8 |
| 7 | Boundary, identity, stdlib, names, payload | PASS except S59-01 | Five created paths only. Identity and trailers as in the field table. Imports are stdlib only. No target-project name and no company address in the diff or the commit messages (scan: 0); the `claude`/`codex` strings are existing test-module names. `tests/test_plugin_payload_boundary.py`: `1 failed, 40 passed`, the failure being only `CommittedPinTests::test_the_pinned_sha_exists`. **Explicit `Any` in the test file: S59-01** |
| 8a | `mypy --strict --python-version 3.11` on the checker | PASS | `Success: no issues found in 1 source file`, exit 0. The remaining implicit `Any` (from `json.loads` and argparse's `Namespace`) is narrowed by `isinstance` before use. That matches the approved wave-1 scripts (`index_pins.py` 12 and `receipt_fence_check.py` 7 `--disallow-any-expr` hits), so it is not a finding |
| 8b | Ticket test file | PASS | `38 passed`, exit 0 (`R_P1.txt`). Not a ticket requirement, but `mypy --strict` on the test file gives 2 `var-annotated` errors (lines 227, 233), recorded under S59-01 |
| 8c | Full suite under the host lock | PASS | `8 failed, 3298 passed, 35 skipped, 6504 subtests passed in 923.98s`, exit 1. The failure set is a subset of the 12 base names, with nothing outside them. The base names that did not fail: `test_acr6_committed_candidate_diff_and_forbidden_paths`, `test_pinning_the_root_commit_is_rejected`, and the two `test_workflow_router` temporal tests |

### Linux groups (234 rows against 8 shared base failures)

| Rows | Cause | Judgement |
| --- | --- | --- |
| 96 | `tests/staging/*` harness reads `os.stat_result.st_file_attributes` (Windows only), directly (77), in a child process (15), plus its knock-on expected-error text (2) and the leftover `tests/.johnny-runtime` it leaves behind (2) | Genuine environment: Windows-only test staging code |
| 84 | Windows-form path models (`CodexObservedAbsolutePath`, `EnvironmentLocator`, `CodexExecutableLocator`, `RegistryLocator`, `JohnnyRootLayout`: 74), `os.environ['LOCALAPPDATA']` (9), and the import-time collection error (1) | Genuine environment: Windows-only product contracts |
| 27 | Windows batch shims run through `cmd.exe` (20); `cmd.exe` and `powershell.exe` absent (7) | Genuine environment |
| 17 | pywin32 or native ref notification (9); `PureWindowsPath` workspace (5); MoveFileEx proof (1); backslash rendering (1); a case-insensitive filesystem assumption (1); the Windows `WinError 5` expectation is counted above | Genuine environment, though each test hard-codes Windows behaviour |
| 7 | The OS-independent main failures (pinned sha `0b3afd36…` ×4, `test_acr6_exact_test_only_boundary`, the router `AUDIT_COMPLETED`, the refusal roster) | Not environment. Honestly registered with `follow_up` = ticket 59 as a placeholder (S59-05) |
| 3 | `test_acr2`/`test_acr3` and `test_file_lock` | Mislabelled as environment (S59-02, S59-03) |

Registering the rows, rather than fixing or marking them, is the only route the ticket leaves open: it forbids skipping or weakening tests, and every product and test path outside the five created files is off limits. Each row is listed by name and has a reason. `REGISTERED_NOW_PASSING` and `REGISTERED_NOT_FAILING` keep the list from going stale. That meets "apart from registered environment failures, each listed by name" for the 224 genuine environment rows. It does not meet it, as written, for the 3 mislabelled rows or the 7 OS-independent rows, which are not environment failures. The Windows 8.3 group (S59-04) is a borderline case. The cost is coverage: on Linux the job checks about 3081 passing tests, and a registered test is blind to any new failure inside it (S59-10).

### Reviewer counter-mutations (disposable copy, never the worktree)

Doors other than the seat's four (prefix comparison, errors as passes, a row without a reason, the now-passing check dropped). Output read unfiltered from pytest (`-rf`, no wrapper). The copy was built from `git show HEAD:<path>`, given its own `pytest.ini`, and removed afterwards. The baseline copy passed 38/38.

| ID | Mutation | Result |
| --- | --- | --- |
| MA | checker step `… --junit "$RUNNER_TEMP/junit.xml" \|\| true` | **zero red** (S59-06) |
| MB | `continue-on-error: true` on the checker step | **zero red** (S59-06) |
| MC | `id-token: write` added under top-level `permissions` | **zero red** (S59-07) |
| MD | job env `T: ${{ github.token }}` | **zero red** (S59-07) |
| ME | collection-error id not mapped to the module file | red: `test_a_collection_error_is_the_module_file` |
| MF | subjects not escaped | red: newline and non-ASCII tests |
| MG | skipped registered test reported as now passing | red: `test_a_registered_test_that_is_skipped_or_absent_…` |
| MH | DOCTYPE/entity refusal removed | red: `test_a_report_with_the_wrong_root_or_a_doctype_is_exit_2` |
| MI | class chain dropped from the id | red: `test_class_qualified_ids_are_built_from_the_classname` |
| MJ | ids compared case-insensitively | **zero red** (S59-10) |
| MK | absent or skipped registered tests accepted | red: three tests |
| ML | input fault exits 1 instead of 2 | red: 15 `SchemaAndInputTests` |
| MM | real list: a reason saying "flaky" | red: `test_every_row_has_a_cause_and_a_follow_up` |
| MN | real list: `follow_up` = "someone should look" | **zero red** (S59-10) |
| MO | repeated test id accepted | red: `test_a_repeated_test_id_is_exit_2` |
| MP | registered ids `.strip()`ped | **zero red** (S59-10) |

### Findings

| ID | Class | Blocks | Finding | Route |
| --- | --- | --- | --- | --- |
| S59-01 | `IMPLEMENTATION_DEFECT` (P0 source type) | **Yes** | `tests/test_ci_registered_failures.py:11,47,174` uses an explicit `typing.Any` (`registered: Any`, `listed(**extra: Any) -> dict[str, Any]`). AGENTS.md P0 forbids `Any` in source, and every earlier wave-2 review recorded "no `Any`" across all of a ticket's paths. It is the only explicit `Any` in the five paths; `object` and `dict[str, object]` express the same intent ("any JSON value, possibly malformed"). Also fix: `mypy --strict` on the test file reports `Need type annotation for "empty"` at lines 227 and 233. Judgement call: if the control plane decides P0 does not cover test files, this finding drops to non-blocking and the verdict would be `APPROVED` | Original ticket, additive correction |
| S59-02 | `IMPLEMENTATION_DEFECT` (row reason and follow-up) | No | The Linux rows `test_acr2_linux_requires_an_actual_linux_kernel_and_backend` and `test_acr3_acm1_current_python_abstraction_final_window_qualifies_no` are `environment`, but the runner does have an actual Linux kernel. The CI traceback shows the test's own `_validate_bounded_label` rejecting `'linux-fs:ext2/ext3'` because of its `/` (`identity fields must not contain paths or raw bodies`, test line 244). The reason's "the host qualifies through WSL Ubuntu" is also contradicted by the host base, where it fails with `_PlatformProofUnavailable: LINUX`. Name the real cause and set `follow_up` to a follow-up ticket | Correction rewrites the rows. Control plane: follow-up ticket for the label validator in `tests/test_atomic_conditional_replace_capability.py` |
| S59-03 | `IMPLEMENTATION_DEFECT` (row reason and follow-up) | No | The Linux row `test_file_lock.py::BlockingAcquisitionTests::test_a_waiter_is_held_out_and_then_let_in_rather_than_refused`. Its reason names a 3 s timing window and a `-9` kill. The failure is actually `ValueError: I/O operation on closed file`: the test closes `waiter.stdin`, then calls `communicate(timeout=…)`, and on POSIX `_communicate` flushes stdin. The `-9` comes from cleanup. `library/local_orchestration/file_lock.py` ships a POSIX `fcntl.flock` path, so this is not a missing runner capability: the POSIX blocking behaviour goes untested in CI | Correction rewrites the row. Control plane: follow-up ticket for the test |
| S59-04 | `TICKET_DEFECT` (no follow-up target) | No | The 39 Windows rows under `C:/Users/RUNNER~1/…` are `environment`. The cause is `path_containment.resolves_within_root`, which returns `False` whenever `base.resolve() != base`. That treats an 8.3 short-name alias of the repository root as a redirect, so every fixture built from `tempfile` on the runner is refused (`WORKTREE_OUTSIDE_REPOSITORY_ROOT`). This is a product-or-fixture defect on the supported platform: any user whose repository path has a short-name component is affected. It is not a capability the runner lacks. The seat's STATEMENT itself says it "may also merit a ticket" | Control plane: a follow-up ticket (normalise long names before comparing, or resolve the fixture root); the rows' `follow_up` then names it |
| S59-05 | `TICKET_DEFECT` (no follow-up target) | No | Seven rows per OS name the ticket's own path as `follow_up`: the pinned sha `0b3afd3645946f97662c336f0e6ac0dcae502e69` (×4), `test_acr6_exact_test_only_boundary`, `test_reviewed_router_profile_composes_return_integration_and_audit` (`SUSPEND` vs `ADVANCE`), and `test_every_failure_enum_in_the_library_is_covered_or_uncovered`. These are known failures on main, not environment failures, and ticket 59 cannot fix them | Control plane: four follow-up tickets, rows re-pointed. The owner confirms that registering known main failures is acceptable under criterion 2 |
| S59-06 | `EVIDENCE_DEFECT` (would let a red pass) | No (rule B: close at the next change of this gate) | "The checker's exit is the job's result" is not pinned. MA (`\|\| true` on the checker step) and MB (`continue-on-error: true`) turn no test red. `test_the_pytest_exit_is_not_the_job_result` only checks for `\|\|` on the pytest line. Pin it: the checker line ends at the junit argument, no `continue-on-error` anywhere, and no `\|\|`/`;` after the checker | This correction (the test file is in scope) |
| S59-07 | `EVIDENCE_DEFECT` (would let a widening pass) | No (rule B: next change) | The permission and secret locks are partial. MC (an extra `id-token: write` under the single `permissions:` block) and MD (`${{ github.token }}`) turn no test red. Pin the permissions block to exactly one entry and refuse `github.token` | This correction |
| S59-08 | `TICKET_DEFECT` | No | The frozen pytest command lacks `--continue-on-collection-errors`. The deviation is justified (cell 1e): a new collection error goes red and the registered one is named. Its cost: the 7 tests in `tests/test_codex_registration_contracts.py`, and any test added there later, never run on Linux | Control plane amends the ticket text to the command as built |
| S59-09 | `OUT_OF_SCOPE_HARDENING` | No | The DOCTYPE/ENTITY refusal is a byte search on the raw file, so a UTF-16 report with `<!DOCTYPE … <!ENTITY e "tests.test_x">` parses, and the entity is expanded into the classname (exit 1 rather than 2). An external `SYSTEM` DOCTYPE in UTF-16 gives exit 0 (`ElementTree` fetches nothing). The report is written by pytest in the same job, so the exposure is small. The README claim "a report that declares a DOCTYPE or an entity is exit 2" holds only for ASCII-compatible encodings. Refuse through an expat `StartDoctypeDeclHandler` / `EntityDeclHandler`, or decode first | Follow-up hardening ticket |
| S59-10 | `OUT_OF_SCOPE_HARDENING` | No | Comparator and schema doors not pinned: case folding (MJ) and whitespace stripping (MP) give zero red. `follow_up` accepts any non-empty string (MN zero red), though the ticket's domain is a ticket path or `environment`. Duplicate JSON keys are accepted with the last one winning (a list with `"linux"` twice silently drops the first array). Registration works per node id, so a registered test with subtests hides a new failing subtest in the same test | Follow-up hardening ticket |
| S59-11 | `EVIDENCE_DEFECT` (README accuracy) | No | `ci/README.md`: (a) `test_pinning_the_root_commit_is_rejected` is listed as a host failure with no cause. The base capture shows `PinnedCommitError … fcb4604572e7a325b970c19303829c42226802ed` in the clone `C:/Temp/claude/jas48_base`. (b) None of the four "host failures that do not fail on a runner" failed on the host at the candidate in two locked runs, so they belong to the base capture, not to the current host, and the README should say so. (c) The "Linux runner" paragraph says every Linux failure is a Windows-only facility or an OS-independent failure, which S59-02 and S59-03 contradict | This correction |

### Commands

From the main checkout unless noted. Python `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`. Scratch at `.worktrees/59-ci-linux-windows-review-scratch`.

- `git -C .worktrees/59-ci-linux-windows-review rev-parse HEAD` → `3ab5ac43…`; `git status --porcelain` → empty (before and after)
- `git log --format='%H %an <%ae> c=%cn <%ce> %B' e760d2e8..HEAD`; `git diff --name-only e760d2e8 HEAD` → the five paths
- `gh run list --branch cp/wave2-59-ci-linux-windows` → 42009508339 failure, 42011080430 failure, 42013690230 success, 42016463075 success
- `gh run view 42016463075 --json headSha,headBranch,conclusion,status,event,url,jobs,workflowName` → `run.json`
- `gh run view 42016463075 --log` → `run_log.txt` (21284 lines); `gh run view 42009508339 --log-failed` → `run1_failed.txt`
- `cmp.py` (summary-line parse versus the list) → Linux 233 + 1 collection error = 234, the same set; Windows 47, the same set
- `msg.py` (samples rows with their failure text) for Linux (2 per reason) and Windows (all)
- `gh api repos/actions/{checkout,setup-python}/git/ref/tags/{v6.1.0,v6.3.0}` and `…/commits/<sha>` → pins confirmed
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out>/RETURN.md .worktrees/59-ci-linux-windows-review` → exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out>/RETURN.md --repo <review> --candidate 3ab5ac43… --tool …/dispatch_lint.py --tool …/receipt_fence_check.py --tool …/index_pins.py --require-cell P1 --require-cell T1 --require-cell M1 --require-cell C1 --require-cell F1 --require-cell P9 --evidence-root <out>` → `cells=6 defects=0`, exit 0
- My own byte, exit and C1 shape check on the receipt (inline script) → all equal, 0 CR
- `python -m mypy --strict --python-version 3.11 --no-incremental ci/check_registered_failures.py` → exit 0; the same on the test file → exit 1, 2 errors; `--disallow-any-expr` comparison on the checker and the wave-1 scripts
- `python -m pytest tests/test_ci_registered_failures.py -q -p no:cacheprovider` → 38 passed, exit 0
- `python -m pytest tests/test_plugin_payload_boundary.py -q -p no:cacheprovider -rf` → only `CommittedPinTests::test_the_pinned_sha_exists` failed
- Real-pytest probes in `scratch/proj` and `scratch/proj2` (own `pytest.ini`): subtests, teardown error, collection error, `pytest.exit()` in a test and at import, `KeyboardInterrupt`, each fed to the candidate checker
- Checker probes in `scratch/probes`: UTF-16 DOCTYPE with internal and external entities, nested-entity expansion, control and non-ASCII escaping, case variant, BOM JSON, duplicate JSON keys, `NaN`
- `scratch/tools/mutate.py` → `R_M2.txt` (16 counter-mutations, copy removed)
- `scratch/tools/f1_locked.sh` → host lock, held by `50-rev01-initial` from 17:34:58Z. I waited 30 s at a time and acquired it at 2026-11-05T18:02:02Z as `59-rev01-initial`, writing `owner.txt` (run id and start). `Get-CimInstance Win32_Process` at acquisition (`R_procs_at_acquisition.txt`): one other pytest, `pytest tests/test_integrate.py -q -p no:cacheprovider -rfE` (PIDs 8948 and 28052, started 01:59:28 local, outside the lock), plus an unrelated `grep.exe` from 2026-10-28. `python -m pytest tests -q -p no:cacheprovider` in the review worktree → `R_F1.txt`, exit 1. Released at 18:17:28Z after checking that `owner.txt` still named my run id. No other pytest of mine ran while I held the lock

### Raw-log note

The `R_*.txt` captures and `run_log.txt` in the scratch directory are unedited tool output. CI logs were read with `gh run view --log` and `--log-failed` only. Nothing was pushed and no workflow run was triggered. The full-suite capture `R_F1.txt` was read in full for its `FAILED` lines; no wrapper reduced it. The counter-mutation results come from unfiltered pytest output (`-rf`). The excerpts above are trimmed only for width.

### Not verified

- I did not run the workflow on GitHub myself (prohibited). The CI evidence is run 42016463075 as read back, plus run 42013690230 on `1d1d1933`, which was also green.
- The `pull_request` trigger has not been exercised by any run; every run was `push`.
- Whether `resolves_within_root`'s 8.3 refusal is intended (S59-04) needs the owner of that module. I read the code, not its design history.
- I did not check whether any later edit to the list keeps the Windows set identical across runs. The README says it was identical in runs 42009508339 and 42011080430, and I checked only 42016463075.
- I did not test the checker with pytest versions other than 9.1.1 (`requirements-dev.txt`), whose junit shape I verified.

```review-verdict
candidate: 3ab5ac439eb726ec28e5e455f2cb44ccfb1bd9f8
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/59-rev01-initial
reviewed_at: 2026-11-06
```
