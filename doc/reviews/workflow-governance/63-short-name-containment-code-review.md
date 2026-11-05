# REVIEW — ticket 63 Short-name containment

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** The fix does what S59-04 asked for. A base spelt with an 8.3 short name is now the same directory as its long name. 38 of the 39 rows pass on the Windows runner and are removed. CI run 42108480717 is green on both jobs at the candidate. Every junction, symlink and short-name shape the ticket lists is still refused.

One finding blocks approval, S63-01. It is a containment bypass that the candidate introduces. The new alias check compares the long spelling and the resolution with `os.path.normcase`, which folds case. NTFS directories with per-directory case sensitivity keep `A` and `a` distinct. A junction `A` pointing at a sibling `a` is therefore accepted as the base once the base is spelt through a short-name parent. The base commit refused the same base. I reproduced this on this host without elevation (probe cs2/cs3). Under rule B this is a safety and confinement break and a P0 violation (AGENTS.md: paths reached through a junction are refused), so it blocks.

S63-02 is the same family, but it predates the candidate. The base check `resolved_base != base` uses pathlib equality, which folds with `str.lower`. That accepts a junction base whose name folds to its target's name, for example U+212A KELVIN SIGN → `k`, on both the base commit and the candidate. It does not block this candidate. The fix for S63-01 sits in the same file and should close it too.

The other findings do not block: S63-03 and S63-04 are evidence defects, S63-05 and S63-06 are hardening, and S63-07 routes the 39th row. The stated cause of the 39th row is right, and it is a test defect, not a product defect.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/63-short-name-containment.md`, revision01. Read at `119a9bc1` on `cp/wave2-gates` (state `IN_PROGRESS`, initial review dispatched). It differs from the blob at the candidate only in its status row |
| Spec | workflow-governance Revision 04 R4-6; REQ-20261103-043 readiness criterion 2; ticket 59 review finding S59-04 |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-63_dispatch.yaml` (base `92ee3a94b963747abede480f1f0a4936880a411e`) |
| Candidate | `b74840f14dba469c68ae1cf5f6849ca468a09ad4` on `cp/wave2-63-short-name-containment`. `origin/cp/wave2-63-short-name-containment` is the same sha. Two commits on `92ee3a94`: `b6821f4b` and `b74840f1`. The base is an ancestor |
| Commit identity | On both commits, author and committer are `Johnny Liu <johnny.liu365@gmail.com>`. The trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` names the model that did the work, which is correct |
| Changed paths | `ci/README.md`, `ci/registered-failures.json`, `library/local_orchestration/path_containment.py`, and the new `tests/test_path_containment_short_names.py`. These are exactly the boundary block's `modify`/`create` entries, and no `forbid` path is touched |
| Review worktree | `.worktrees/63-short-name-containment-review`, detached at the candidate. Porcelain was empty before and after |
| Receipt | `.worktrees/63-short-name-containment-out/RETURN.md` (LF, 47978 bytes, 0 CR) |
| CI run | 42108480717, https://github.com/johnnyliu365-sys/Johnny_AI_Skill/actions/runs/42108480717, event `push`, `headSha` = candidate. `test (linux)` success, `test (windows)` success. The earlier run 42105264082 on `b6821f4b` failed on Windows for the 39th row |
| References applied | `AGENTS.md` (P0 permissions and ownership; P0 source type); `CodeReview.md` (whole file, §4, §5 rule B); `review-checks.md` (path identity/prefix, authorization bypass, exception behaviour, error-code consistency, test truthfulness and reviewer counter-mutation, task/worktree binding); `security-boundary.md` |
| XSS / privileged JS | Not applicable. There is no browser, DOM or JavaScript surface: this is a stdlib path predicate and its test |
| Secret / provider / external effect | Not applicable. No secret, log, provider or webhook is involved. The only effect is the CI push of the seat's own branch, which the dispatch authorised |
| Agent control / profile fan-out / POC ancestry | Not applicable. There is no Agent control path, one implementer seat, and no POC or staging. `gh run list` shows two push runs, both on the ticket branch |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | A short-name root and target are contained; the long name likewise | PASS | Probes A1 (short root → `True`; base commit → `False`), c2, c3, c9, c11. New tests `test_short_root_and_long_target_are_contained` and `test_long_root_and_short_target_are_contained` |
| 2 | Junction/symlink/reparse point inside the root pointing outside is refused; short name of an outside directory refused | PASS except S63-01 | Probes a1–a8 and b1, b2, b4 refused on both the candidate and the base. Symlinks need privilege 1314 on this host, so the symlink rows ran as junctions; see "Not verified". The case-twin junction base cs2/cs3 is accepted: S63-01 |
| 3 | A failed long-name lookup refuses | PASS | e2 (`GetLongPathNameW` error 2 → `None` → refused). R4 (the zero-return check dropped) turns `test_the_long_name_lookup_of_a_missing_path_is_none` red |
| 4 | Existing containment tests unchanged and passing | PASS | `git diff --name-only 92ee3a94 HEAD` names no existing test. My clone baseline ran `tests/test_worktree_containment.py`, `test_live_payload_ports.py`, the three telemetry storage test files and the new file: 55 passed, 22 subtests passed |
| 5 | The new test creates real 8.3 names only where the volume has them, and says so | PASS (note) | `_short_name` uses `GetShortPathNameW` on a real directory and skips with "this volume has no 8.3 short name …" when there is none. On the Windows runner, skips stayed at 34 against the base run 42101907082 (34), and the test count grew by exactly 13, so all 13 tests ran there. On Linux, 7 more skip and 6 more pass. Note: on POSIX the skip text says "volume", although the cause is the platform |
| 6 | 38 of the 39 rows removed and passing in CI | PASS | `rows.py`: Windows rows 47 → 9, 38 removed, 0 added, all 38 removed rows carried `follow_up` ticket 63. CI Windows `FAILED` set (9) equals the 9 registered rows, and no removed row fails. Linux rows (234) are unchanged |
| 7 | 39th row: cause and route | Cause right; route open (S63-07) | `plugin_bundle_builder.py:168` resolves the root with `resolve(strict=True)`. The test's `sentinel_is_symlink` compares against `symlink_path`, which is built from the unresolved `tempfile` name. Reproduced on the host: with `TMP` set to a short spelling (`JAS63_~1`) it fails `ENTRY_UNAVAILABLE != None`, and with the long spelling it passes. With `parent = Path(temp_name).resolve()` in a disposable clone, it passes under the short `TMP`. This is a test defect: a real symlink is still found by the real `is_symlink` on the long path |
| 8 | ctypes declarations and error handling | Declared; error code not read (S63-06) | `argtypes = [LPCWSTR, LPWSTR, DWORD]`, `restype = DWORD`. A zero return → `None` → refusal, and no exception is swallowed. `windll` is loaded without `use_last_error`, so `GetLastError` is never read |
| 9 | Strict type, stdlib, no `Any` | PASS | `mypy --strict --python-version 3.11 --no-incremental` on both files → exit 0. The same with `--platform linux` → exit 0. Imports are stdlib only. No explicit `Any`. `--disallow-any-expr` flags only the untyped ctypes call results (module line 36, test line 31), and each is converted to `int` at once |
| 10 | Receipt | `receipt_check.py` PASS; `evidence_gate.py` FAIL (S63-03) | `receipt_check.py` → 6 `[ok]`, 0 defects, exit 0. `evidence_gate.py` with the three wave-1 tools and P1, T1, M1, C1, F1, P9 → `EXIT_MISMATCH M1: exit lists 0, capture holds 0,0,0`, `cells=6 defects=1`, exit 1. My byte check: the receipt has 0 CR, and every raw block is byte-identical to its capture (P1, T1, M1, C1, F1, P9). The exit lists are equal except M1. The tool digests equal the sha256 of the three scripts at the candidate |
| 11 | M1 tails unfiltered; clone command recorded | PASS | The M1 capture records `git clone --no-hardlinks … C:/Temp/claude/jas63_mut` and the detach. Each mutation carries its diff, full pytest output with tracebacks, `pytest_exit` and an empty porcelain after restore. All three are red |
| 12 | Seat F1 | PASS | 8 failure names, all among the 12 base names in `jas48_F1_base.txt` |
| 13 | Reviewer F1 under the host lock | PASS | `python -m pytest tests -q -p no:cacheprovider` in the review worktree → 8 failed, 3406 passed, 36 skipped, 6839 subtests passed, exit 1. The 8 failure names are all among the 12 base names, with zero new red. They are the same 8 the seat reported |

### Bypass probes (a)–(h)

Run with `scratch/probe.py`, `probe_cs.py` and `probe_rp.py` against the candidate module and against the base module (`git show 92ee3a94:…`). Every link and directory lived in a fresh `%TEMP%` directory and was removed afterwards: junctions first, then the tree. `True` means accepted.

| Probe | Shape | Candidate | Base `92ee3a94` | Judgement |
| --- | --- | --- | --- | --- |
| (a) | Junction inside the root as target (long and short base); short name of that junction (a1, a2) | refused | refused | Holds |
| (a) | Junction as base; its short name as base; a junction whose target is spelt `OUTSID~1`; the same through a short parent; a junction to the root via a short-spelt target; a junction in an ancestor of the base, with a long or short root component (a3–a7b) | refused | refused | Holds: `GetLongPathNameW` keeps the junction's own name, so it never equals the resolution |
| (a) | Symlink as base (a8) | not run | not run | `os.symlink` → WinError 1314 (no privilege). The CI Linux job ran the two symlink redirect tests |
| (a) | **Case-twin junction base:** per-directory case-sensitive parent (`fsutil file setCaseSensitiveInfo … enable`, no elevation), junction `A` → real `a`, base spelt `<short parent>\A` (cs2, cs3) | **accepted** | refused | **Bypass introduced by the candidate: S63-01** |
| (a) | The same junction, base with long parent (cs1) | accepted | accepted | Pre-existing: S63-02 |
| (a) | Kelvin-sign junction `U+212A` → `k`, long parent (a9) | accepted | accepted | Pre-existing (pathlib `str.lower` fold): S63-02 |
| (a) | The same and Ohm-sign `U+2126` → `ω`, short parent (a9b, a9c) | refused | refused | `ntpath.normcase` (LCMapStringEx) does not fold them. My scan: 0 BMP characters that `normcase` folds but `RtlUpcaseUnicodeChar` keeps distinct; 200 for `str.lower`. Under R3 (pathlib equality in the new branch) both are accepted and no test goes red: S63-04 |
| (b) | Short name of an outside directory as target, with long or short base; root and outside both via the short parent (b1, b2, b4) | refused | refused | Holds. b3 (outside's short name as its own base) is trivially contained |
| (c) | Base upper-cased (c1) | accepted | accepted | Same directory, unchanged |
| (c) | Short base upper-cased, with trailing separator, with `.` component, with forward slashes (c2, c3, c9, c11) | accepted | refused | Intended widening: same directory, not a redirect |
| (c) | Short base with a trailing dot `CONTAI~1.` (c4) | accepted | refused | Win32 strips the dot. The same directory, so no bypass |
| (c) | Trailing space, `. .`, long base with trailing dot, `::$INDEX_ALLOCATION`, `..` (c5–c8, c10) | refused | refused | `GetLongPathNameW` keeps the input literally, so it is unequal: fail closed |
| (d) | `\\?\` and `\\.\` short and long bases (d1–d4); drive-relative `C:CONTAI~1`, relative short and long bases (d5–d7); `\\localhost\C$` and `\\?\UNC\localhost` (d8, d9) | refused | refused | Fail closed. `\\?\` keeps its prefix in the resolution, so a `C:` target is never inside it. `\\.\` resolves without the prefix, and the lookup keeps it |
| (e) | 1030-character base given through short names (e1) | accepted | refused | The retry with `needed + 1` works. A lookup failure (e2) refuses. Buffer logic: on success the return excludes the NUL, so it is `< size`; on a short buffer the required size includes the NUL, so it is `> size`; `needed < size` is exact. A path that grows between the two calls → `None` → refused. R5 (truncated buffer accepted) and R6 (no retry) fail closed and turn no test red: S63-05 |
| (f) | Third-party, non-surrogate reparse tag `0x4321` set by `FSCTL_SET_REPARSE_POINT` without elevation: dir inside the root as target (f1); leaf under it (f2); as base, long and short (f3, f4) | f1 accepted; f2–f4 refused | identical | Unchanged. `resolve` does not follow a non-surrogate tag; anything beneath it raises `OSError` 1920 and is refused. f1 is the pre-existing acceptance of an unopenable leaf; noted under S63-02 |
| (g) | POSIX | by reading and CI | — | `_long_name` returns the path unchanged and `normcase` is the identity, so any base whose `Path` differs from its resolution differs as a string: always refused, as before. The Linux job ran `test_a_redirected_base_is_refused` and `test_a_redirect_inside_the_root_pointing_outside_is_refused` with real symlinks (6 new passes). R8 (POSIX branch returns `path.resolve()`) is unreachable on this host; the Linux symlink test would catch it. Not run locally |
| (h) | TOCTOU between `resolve`, `GetLongPathNameW` and the target walk | by reading | — | Three separate path-based reads; no handle is held. A real directory swapped for a same-name junction after `resolve` gives the same long string and is accepted, but containment is anchored to the earlier real resolution. That is the predicate's existing check-then-use gap, not a new class. A junction swapped for a real directory makes the strings unequal → refused. No new exploitable window. The predicate stays check-then-use, as it was |

### Reviewer counter-mutations (disposable `git clone --no-hardlinks` copy at `C:/Temp/claude/jas63rev01_mut`, removed)

These doors differ from the seat's three (normalisation removed, redirect refusal removed, final check `return True`). Output was read from unfiltered pytest (`-q -rfEs`, no wrapper), and each mutation was restored with an empty porcelain. Baseline: 55 passed, 22 subtests passed.

| ID | Mutation | Result |
| --- | --- | --- |
| R1 | `".." in base.parts` guard removed | zero red. **Equivalent**: `GetLongPathNameW` keeps `..` literally (probe c10 under R1 still refused) |
| R2 | any successful long-name lookup accepted | red: `test_a_redirected_base_is_refused`, `test_a_short_name_root_does_not_hide_a_redirected_base`, `test_r4_a_junctioned_repository_root_is_refused` |
| R3 | comparison through pathlib equality (`str.lower` fold) | **zero red**. Under R3, the a9b and a9c junction bases are accepted (S63-04) |
| R4 | zero return of `GetLongPathNameW` not treated as failure | red: `test_the_long_name_lookup_of_a_missing_path_is_none` |
| R5 | truncated buffer accepted (`if True:`) | zero red; fails closed (e1 refused) (S63-05) |
| R6 | no retry with the larger buffer | zero red; fails closed (e1 refused) (S63-05) |
| R7 | target's existing ancestor `absolute()` instead of `resolve()` | red: 4 new tests and `test_r4_a_worktree_reached_through_a_junction_is_refused` |
| R8 | POSIX branch returns `path.resolve()` | zero red on this host. Environment-scoped: unreachable on win32; the Linux job's symlink redirect test would catch it |

The case-twin junction (S63-01) needs no mutation: the unmutated candidate accepts it and the whole suite stays green. That is itself a zero-red result for the ticket's category 3 "a short name that hides one (indirect)".

### Findings

| ID | Class | Blocks? | Finding | Route |
| --- | --- | --- | --- | --- |
| S63-01 | `IMPLEMENTATION_DEFECT` (safety/confinement; AGENTS.md P0) | **Yes** | `_is_same_directory_alias` treats "the case-folded long spelling equals the case-folded resolution" as proof that the base holds no redirect. Case folding is not the file system's identity. In a directory with per-directory case sensitivity (enabled here without elevation), a junction `A` → sibling `a` gives a long spelling `…\A` and a resolution `…\a`, and `normcase` makes them equal. With the base spelt through a short-name parent, the candidate accepts `resolves_within_root(<sP>\A\x, <sP>\A)` and `resolves_within_root(<P>\a\x, <sP>\A)`, both `True`; the base commit returns `False` for both. This breaks the ticket's frozen rule "Junctions, symlinks and other reparse points are still refused exactly as before", TDD 2, and defect category 3 "a short name that hides one (indirect)". The `ci/README.md` sentence "junctions, symlinks and reparse points are still refused" is then untrue. Fix inside the boundary: do not infer "no redirect" from a string comparison. On the alias branch, walk the existing components of the base and refuse when any has `FILE_ATTRIBUTE_REPARSE_POINT` (`os.lstat(...).st_file_attributes`; `lstat` does not follow), then accept the short-name alias. Add a test with a case-sensitive directory where `fsutil` allows it, saying so when it does not | This correction (same branch, additive) |
| S63-02 | `OUT_OF_SCOPE_HARDENING` relative to ticket 63's Closure; a pre-existing P0 confinement defect | No (present at `92ee3a94`, unchanged) | The base check `resolved_base != base` is pathlib equality, which on Windows folds with `str.lower`. That accepts a junction base whose name folds to its target's: U+212A KELVIN SIGN → `k` (a9), and `A` → `a` in a case-sensitive directory with a long parent (cs1). Both are `True` on the base commit and on the candidate. My scan finds 200 BMP characters that `str.lower` folds and NTFS keeps distinct. Separately, a leaf carrying a non-surrogate reparse tag is accepted as a target (f1), on both commits. The P0 rule "paths reached through a junction are refused" therefore did not hold before this ticket either | Control plane: the S63-01 reparse-attribute walk, applied to every base rather than only on the alias branch, closes it in the same file. Either widen ticket 63's Closure for this correction or open a security follow-up ticket |
| S63-03 | `EVIDENCE_DEFECT` (receipt) | No | `evidence_gate.py` exits 1: `EXIT_MISMATCH M1: exit lists 0, capture holds 0,0,0`. The M1 capture has three `exit=` lines (clone, checkout, final), and the receipt lists one. The dispatch requires "exit in capture order". `receipt_check.py` (P9) does not check this, so P9 passes | This correction's receipt |
| S63-04 | `EVIDENCE_DEFECT` (would let a widening pass; rule B: close in the next change of this gate) | No | The ticket's category 1 requires a "case" cell, and neither the new file nor the existing containment tests has one. No test pins the fold used in the alias comparison: R3 (pathlib equality) turns nothing red, yet it accepts the Kelvin- and Ohm-sign junction bases through a short parent | This correction (the S63-01 test covers it) |
| S63-05 | `OUT_OF_SCOPE_HARDENING` | No | The >1024-character path through the retry is not pinned: R5 and R6 turn nothing red. Both fail closed, so a regression would refuse a valid long path, not admit a redirect | Follow-up hardening |
| S63-06 | `OUT_OF_SCOPE_HARDENING` | No | `_long_name` sets `argtypes`/`restype` on the shared `ctypes.windll.kernel32.GetLongPathNameW` object on every call, which is a process-wide mutation. It loads without `use_last_error=True` and never reads `GetLastError`, so a failed lookup is indistinguishable from a redirect in diagnostics. The public refusal code (`WORKTREE_OUTSIDE_REPOSITORY_ROOT`) is fixed, and fail-closed holds. A module-level `ctypes.WinDLL("kernel32", use_last_error=True)` prototype would fix all three | Follow-up hardening |
| S63-07 | `TICKET_DEFECT` (no follow-up target) | No | The restored row `tests/test_plugin_distribution_bundle.py::PluginBundleBuilderTests::test_missing_changed_and_symlink_entries_block_with_finite_failures` still names ticket 63 as `follow_up`, but ticket 63 no longer owns it. Its new reason is right (cell 7). This is a test defect: the sentinel path is spelt from the unresolved temp name, while the builder walks `repository_root.resolve(strict=True)`. The ticket 59 registration had attributed it to `path_containment`, which was wrong. A one-line fixture change (`Path(temp_name).resolve()`) passes under a short `TMP` | Control plane: a follow-up ticket owning `tests/test_plugin_distribution_bundle.py`; then re-point the row's `follow_up` |

### Commands

From the main checkout unless noted. Python `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`. Scratch at `.worktrees/63-short-name-containment-review-scratch`.

- `git -C .worktrees/63-short-name-containment-review rev-parse HEAD` → `b74840f1…`; `git status --porcelain` → empty (before and after)
- `git log --format='%H an=%an <%ae> cn=%cn <%ce> %B' 92ee3a94..HEAD`; `git diff --stat 92ee3a94 HEAD` → the four paths; `git merge-base --is-ancestor 92ee3a94 HEAD` → yes; `git rev-parse origin/cp/wave2-63-short-name-containment` → candidate
- `gh run view 42108480717 --json headSha,headBranch,conclusion,status,event,url,jobs,workflowName`; `gh run view 42108480717 --log` → `run_log.txt`; `gh run view 42101907082 --log` → `run_base_log.txt`; `gh run list --branch cp/wave2-63-short-name-containment`
- `rows.py run_log.txt <review>` → registered rows against the CI Windows `FAILED` set, at the base and at the candidate
- `probe.py <module> new|old` → `probe_new.txt`, `probe_old.txt`; `probe_cs.py` → `probe_cs_new.txt`, `probe_cs_old.txt` (case-sensitive directory made with `fsutil file setCaseSensitiveInfo`, then removed); `probe_rp.py` → `probe_rp_new.txt`, `probe_rp_old.txt`; `casefold_scan.py` → `casefold_scan.txt`; `probe.py mutant_R{1,3,5,6}.py` → `probe_R*.txt`
- `TMP=<short> python -m pytest tests/test_plugin_distribution_bundle.py::…::test_missing_changed_and_symlink_entries_block_with_finite_failures -q -p no:cacheprovider` → 1 failed (`ENTRY_UNAVAILABLE != None`); the same with the long `TMP` → 1 passed; with the fixture resolved in the clone → 1 passed (`row39_fix.txt`)
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out>/RETURN.md <review>` → exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out>/RETURN.md --repo <review> --candidate b74840f1… --tool …/dispatch_lint.py --tool …/receipt_fence_check.py --tool …/index_pins.py --require-cell P1 --require-cell T1 --require-cell M1 --require-cell C1 --require-cell F1 --require-cell P9 --evidence-root <out>` → `EXIT_MISMATCH M1`, `cells=6 defects=1`, exit 1
- `receipt_bytes.py <out>` → 0 CR; every block equal to its capture; exit lists equal except M1
- `python -m mypy --strict --python-version 3.11 --no-incremental` on both files → exit 0; the same with `--platform linux` → exit 0; `--disallow-any-expr --follow-imports=silent` → only the two ctypes call results
- `git clone --no-hardlinks <review> C:/Temp/claude/jas63rev01_mut`, `checkout --detach b74840f1…`, then `mutate.py` → `mutations.txt` (8 mutations, porcelain empty after each). The clone was removed
- `locked_f1.py` → host lock `C:/Temp/claude/jas-fullsuite.lock`. While I waited, it was held by `58c2-f1-…` and then `integ-62-…`. I tried `mkdir` every 20 s and acquired it at 2026-11-05T22:24:49Z as `63-rev01-initial-F1`, writing `owner.txt` with the run id and time. At acquisition, `Get-CimInstance Win32_Process` (`procs_at_acquisition.txt`) showed one other pytest: `python -m pytest tests/test_governance_consistency.py -q -p no:cacheprovider` (PIDs 39988 and 30148, started 06:24:39 local, outside the lock, checkout not shown). It also showed my own lock runner. The full suite ran in the review worktree → `F1.txt`, exit 1. The lock was released at 22:36:26Z: after checking that `owner.txt` still named my run, I renamed the directory to `jas-fullsuite.lock.released-63-rev01-initial-F1-<uuid>` and removed it. No mutation worker or other pytest of mine ran while I held the lock

### Raw-log note

The captures in the scratch directory are unedited tool output: `probe_*.txt`, `casefold_scan.txt`, `mutations.txt`, `row39_fix.txt`, `F1.txt`, `procs_at_acquisition.txt`, `lock_log.txt`, `run_log.txt` and `run_base_log.txt`. In the probe table, paths are shortened by `summ.py` for width only. CI was read with `gh run view` only. Nothing was pushed, and no workflow run was triggered. The counter-mutations and F1 were judged on unfiltered pytest output; no wrapper reduced it. No tracked file was modified anywhere. The seat's own mutation clone `C:/Temp/claude/jas63_mut` still exists; it is not mine, and I did not touch it.

### Not verified

- Real symlinks on Windows: this host refuses `os.symlink` (WinError 1314). The Windows symlink shapes ran as junctions. The Linux job ran the symlink redirect tests.
- POSIX (g) was judged by reading the code and by the Linux CI counts. I ran no POSIX interpreter, and R8 was not run where it is reachable.
- A volume whose `$UpCase` table differs from `RtlUpcaseUnicodeChar`. My fold scan used the running system's table, not the volume's.
- Volume mount points, which need elevation, and cloud-file or dedup tags, of which none were present. (f) was covered with a third-party tag only.
- Whether the case-twin bypass (S63-01) can be reached on the GitHub runner. That does not matter for the finding.

```review-verdict
candidate: b74840f14dba469c68ae1cf5f6849ca468a09ad4
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/63-rev01-initial
reviewed_at: 2026-11-06
```
