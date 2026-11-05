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

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`.** Correction 1 (`00fdc179`) applies the revision02 rule. Every existing component of every base is examined with `os.lstat`, a reparse point refuses, and a component that cannot be examined refuses. My revision01 bypasses are now all refused: cs1–cs3, the Kelvin and Ohm junction bases, and the ancestor junction. The same holds for the new mount-point, alternate-stream, trailing-space/dot and beyond-MAX_PATH shapes. The 39th row is fixed in its test and passes on the runner. S63-01 to S63-07 are closed as specified. CI run 42123979062 is green on both jobs at the candidate. No common setup that I could test is over-refused.

Two new findings block approval:

- **S63-08 (confinement).** `resolves_within_root` now resolves the base twice. It checks the first resolution in `base_refusal_reason` and anchors containment on a second, unchecked `base.resolve()`. The base is swapped for a junction pointing outside right after the first resolve. The candidate then accepts a target under the junction. Under the identical swap the revision01 and base code refuse it (probe N2). The candidate has widened the check-then-use window into the predicate itself. The same split leaves a window between the `lstat` walk and the resolve that reopens the S63-01 case-twin shape.
- **S63-09 (P0 source type).** `_component_refusal` encodes a three-state result as `str | None`, with `""` meaning "missing component, stop". That is a string convention for a finite domain state, which AGENTS.md P0 forbids.

S63-10 also has to be closed in this correction under rule B: no test pins the ancestor half of the walk against case-folding junctions. My K2 mutation, which examines only the base itself, reopens AN1–AN3 and turns nothing red. The rest do not block: S63-11 and S63-13 are hardening, and S63-12 is a ticket defect for the control plane.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/63-short-name-containment.md`, closure revision02, read with `git show 8ed97a29:…`. It has the boundary block (five paths) and the "Revision02" section with its rule and findings table |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-63b_dispatch.yaml` (correction 1 on `b74840f1`) |
| Candidate | `00fdc179f07e7d57cd828634396e71af77ad352b` on `cp/wave2-63-short-name-containment`. `origin/cp/wave2-63-short-name-containment` is the same sha. It is one additive commit whose parent is `b74840f1` |
| Commit identity | Author and committer are `Johnny Liu <johnny.liu365@gmail.com>`. The trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` names the model that did the work, which is correct |
| Changed paths | `git diff --name-only 92ee3a94 HEAD`: `ci/README.md`, `ci/registered-failures.json`, `library/local_orchestration/path_containment.py`, `tests/test_path_containment_short_names.py`, `tests/test_plugin_distribution_bundle.py`. These are exactly the boundary block's entries, and no `forbid` path is touched |
| Review worktree | `.worktrees/63-short-name-containment-review`, detached at the candidate. Porcelain was empty before and after |
| Receipt | `.worktrees/63-short-name-containment-out-c1/RETURN.md` (LF, 65617 bytes, 0 CR) |
| CI run | 42123979062, event `push`, `headSha` = candidate, `test (linux)` success, `test (windows)` success. `gh run list` on the branch: 42105264082 failure (`b6821f4b`), 42108480717 success (`b74840f1`), 42123979062 success (`00fdc179`) |
| References applied | `AGENTS.md` (P0 permissions and ownership; P0 source type); `CodeReview.md` (§3–§5, rule B); `review-checks.md` (path identity, authorization bypass, exception behaviour, error-code consistency, test truthfulness with reviewer counter-mutation, task/worktree binding); `security-boundary.md` |
| XSS / secrets / Agent control / profile / POC | Not applicable, for the same reasons as revision01 |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Revision02 rule: every existing component of every base examined with `lstat`; a reparse point refuses; a component that cannot be examined refuses; the short-name lookup decides spelling only afterwards | PASS in effect, except S63-08 and S63-10 | `_redirected_component` walks `Path(*parts[:count])` from the volume root, and `_component_refusal` refuses on `S_ISLNK` or `FILE_ATTRIBUTE_REPARSE_POINT`. Any `OSError` other than not-found or not-a-directory refuses (K1 red). Only then does `base.resolve()` run, followed by `_is_same_directory_alias`. A relative base is refused |
| 2 | Revision01 probes rerun | PASS | All refuse except the intended same-directory spellings. a9 (Kelvin junction, long parent) is now **refused**; it was accepted at revision01 and at the base. cs1, cs2 and cs3 are refused, and the cs4 control is accepted. Table below |
| 3 | New probes | **FAIL: N2 (S63-08)**; N6 raises (S63-11) | Table below |
| 4 | Over-refusal on Windows | PASS on this host; process-mode dependency (S63-12) | Over-refusal table below |
| 5 | `base_refusal_reason` | Contract acceptable; see S63-09 | `(base: Path) -> str \| None`: `None` means the base can anchor; otherwise a free-text diagnostic that names the component, the resolution or the Windows error. The only caller is `resolves_within_root`; `worktree_containment.py` and `payload_effect_ports.py` still use the boolean. `__all__` exports it. Its result is diagnostic text, not a finite reason type, so nothing should branch on it. If a caller later needs the reason, it should get a named enum. Until then it could stay private. Its inner helper's `""` sentinel is S63-09 |
| 6 | ctypes | PASS | `ctypes.WinDLL("kernel32", use_last_error=True)` once at import, under `sys.platform == "win32"`. `argtypes`/`restype` are declared once. `set_last_error(0)` runs before the call, and `get_last_error()` is read on a zero return into a thread-local, then into the reason ("Windows error N"). The retry pins hold: M1d (R5) and M1e (R6) are red. M1f (`use_last_error=False`) is red through the real-lookup test. `test_the_kernel_function_is_declared_once_with_last_error` checks types and identity, not the `use_last_error` flag; M1f covers the flag |
| 7 | 39th row | PASS | The only edit to `tests/test_plugin_distribution_bundle.py` is `parent = Path(temp_name).resolve()` plus a comment; no assertion changed. The row is removed from `ci/registered-failures.json`. CI Windows `FAILED` set (8) equals the 8 registered rows, and the test is not among them. M1g (fixture back to the short spelling) is red under a short `TMP` with `ENTRY_UNAVAILABLE != None`, and the seat's M1base is green under the same `TMP` |
| 8 | No existing assertion weakened; revision01 rules still hold | PASS | `git diff b74840f1 HEAD -- tests/` removes one line, the fixture line above. The new file grows from 13 to 28 tests, all additions. In my clone, the new file plus the five existing containment test files gave 70 passed, 22 subtests passed. Windows CI: skips stay at 34, and the test count grows by exactly 15, so every new test ran on the runner. Linux: 12 more skip, 3 more pass |
| 9 | Receipt | PASS | `receipt_check.py` → 6 `[ok]`, 0 defects, exit 0. `evidence_gate.py` with the three wave-1 tools and P1, T1, M1, C1, F1, P9 → `cells=6 defects=0`, exit 0 (S63-03 closed). My byte check: 0 CR, every raw block byte-identical to its capture, every exit list equal to the capture's `exit=` lines (M1 `0,0,0` = clone, checkout, final). The STATEMENT says E1 ran last, but there is no E1 capture: a receipt cannot hold the gate's verdict on itself. My own run on the receipt as returned gives `defects=0` |
| 10 | M1: seven mutations red for the intended reason | PASS | Read unfiltered. M1a (walk removed) → the 4 case-fold junction tests and the cannot-be-examined test, all `True is not false`. M1b (walk only for short-name bases) → the 2 long-parent case-fold tests, Kelvin, Ohm and cannot-be-examined. M1c (R3, pathlib equality) → `test_a_lookup_that_differs_by_a_character_only_pathlib_folds_is_refused`. M1d (R5) → retry test, `WindowsPath('.')`. M1e (R6) → retry test, `!= None`. M1f → `0 not found in (2, 3)`. M1g → `ENTRY_UNAVAILABLE != None`. Each restore leaves an empty porcelain. The clone command and detach are recorded |
| 11 | Boundary, identity, stdlib, `Any`, mypy | PASS (with S63-09 note) | Five declared paths; Johnny Liu. Imports are stdlib only (`os`, `stat`, `sys`, `threading`, `pathlib`, `ctypes`, `ctypes.wintypes`). No explicit `Any`. `mypy --strict --python-version 3.11 --no-incremental` on the three changed Python files → exit 0, and with `--platform linux` → exit 0. `--disallow-any-expr` flags the ctypes call result (line 45), `getattr(_lookup_state, "error", 0)` (line 76) and `getattr(status, "st_file_attributes", 0)` (line 106), each narrowed by `int()` |
| 12 | Seat F1 | PASS | 8 failure names, all among the 12 base names. The seat's lock log names only its own runner at acquisition |
| 13 | Reviewer F1 under the host lock | PASS | `python -m pytest tests -q -p no:cacheprovider` in the review worktree → 8 failed, 3421 passed, 36 skipped, 6839 subtests passed, exit 1. The 8 names are all among the 12 base names, with zero new red, and they are the same 8 the seat reported |

### Bypass probes

`True` means accepted. Candidate `00fdc179`, against revision01 `b74840f1` and base `92ee3a94` where they differ. All links, case-sensitive directories, mount points and the subst drive lived in fresh `%TEMP%` directories or session mappings, and were removed afterwards: links first, by explicit list, then the tree.

**Revision01 probes, rerun**

| Probe | Shape | Candidate | rev01 | Base |
| --- | --- | --- | --- | --- |
| (a) a1–a7b | junction or its short name inside the root as target; junction, its short name, a junction to a short-spelt target, an ancestor junction (long and short) as base | refused | refused | refused |
| (a) a8 | symlink as base | not run (WinError 1314) | — | — |
| (a) cs1 / cs2 / cs3 | case-twin junction `A` → `a`; long parent / short parent / target under real `a` | **refused** | accepted / **accepted** / **accepted** | accepted / refused / refused |
| (a) cs4 | real `a` via short parent (control) | accepted | — | — |
| (a) a9 / a9b / a9c | Kelvin junction long parent / Kelvin short parent / Ohm short parent | **refused** / refused / refused | accepted / refused / refused | accepted / refused / refused |
| (b) b1, b2, b4 | short name of an outside directory as target | refused | refused | refused |
| (c) c1–c4, c9, c11 | case, trailing separator or dot, `.` and forward-slash spellings of the same directory | accepted (same directory) | accepted | c1 only |
| (c) c5–c8, c10 | trailing space, `. .`, long base with a dot, `::$INDEX_ALLOCATION`, `..` | refused | refused | refused |
| (d) d1–d9 | `\\?\`, `\\.\`, drive-relative, relative, `\\localhost\C$`, `\\?\UNC\…` | refused | refused | refused |
| (e) e1 / e2 | 1030-character base via short names / missing base | accepted / refused | same | refused / refused |
| (f) f1 / f2–f4 | third-party non-surrogate reparse tag: leaf inside the root as target / beneath it or as base | accepted / refused | same | same (S63-13) |
| (g) | POSIX | By reading and CI. `S_ISLNK` refuses a symlink component, and the spelling comparison refuses as before. The Linux job ran the symlink tests, with 3 more passing. K8 (`S_ISLNK` removed) is overlap-masked by the spelling comparison | — | — |
| (h) | TOCTOU | see N2 and S63-08 | — | — |

**New probes**

| Probe | Shape | Candidate | rev01 | Base | Judgement |
| --- | --- | --- | --- | --- | --- |
| N1 / N1b | a reparse point in the target: a junction inside the root pointing at a child of the root / a Kelvin junction pointing at a sibling inside the root | accepted / accepted | same | same | Pre-existing; resolves inside the root; the revision02 rule covers bases only (S63-13) |
| AN1–AN4 | case-twin and Kelvin junctions in an **ancestor** of the base, long and short parent | refused (all four) | accepted ×3 / refused | accepted ×2 / refused ×2 | Closed by the walk; unpinned (K2, S63-10) |
| N2 | base swapped for a junction to outside right after the first `resolve` of the base, target `base\x` | **accepted** | refused | refused | **S63-08**: the second, unchecked `base.resolve()` becomes the anchor |
| N2′ | a component swapped between the `lstat` walk and `resolve` | by reading: refused for a plain junction (the spelling differs); **accepted for a case-twin junction** (`normcase` equal) | — | — | Part of S63-08 |
| N3 / N3b / N3c | volume mount point of `C:` (made with `FSCTL_SET_REPARSE_POINT`, tag `0xA0000003`, no elevation) as base / base below it / as target | refused / refused / refused | refused | refused | Holds: "component … is a reparse point" |
| N4 / N4b / N4c | subst drive `Q:` → temp parent: base on it / its root as base / target via `Q:` with a `C:` base | refused / refused / accepted | same | same | Unchanged: a subst base resolves to its `C:` spelling ("not the same spelling"). A target through it resolves inside |
| — | mapped network drive | not made | — | — | I did not create a `net use` mapping, to avoid a credential prompt and session configuration. The UNC forms d8 and d9 refuse |
| N6 / N6b | `lstat` succeeds but `st_file_attributes` is unavailable (an `os.stat_result` built without it; `None`) on the root / on a junction base | **raises `TypeError`** / **raises `TypeError`** | accepted / refused | accepted / refused | Unreachable through CPython's `os.lstat` on Windows, which always fills the field. The exception escapes `resolves_within_root`, which catches only `OSError` (S63-11) |
| N7 / N7b / N7c | a junction base spelt `J::$INDEX_ALLOCATION` / `J ` / `J.` | refused ×3 | refused | refused | `lstat` reports the junction's attribute through each spelling |
| N8 / N8b | a junction 598 characters deep (beyond MAX_PATH; `LongPathsEnabled=1`) as base / the same depth without a junction | refused / accepted | refused / accepted | same | Holds |

### Over-refusal on Windows

| Setup | Candidate | Base | Note |
| --- | --- | --- | --- |
| This repository, `C:/Users/User/Desktop/Johnny_AI_Skill` | accepted | accepted | No component carries a reparse bit (`lstat` attributes `0x11`, `0x10`, `0x11`, `0x36`, `0x10`) |
| `%TEMP%` working directory | accepted | accepted | The GitHub runner's `C:/Users/RUNNER~1/…` is accepted: 38 + 1 rows pass in CI |
| Drive root `C:\` as base | accepted | accepted | |
| Long path, 598 and 1030 characters, long and short spellings | accepted | accepted (long spelling) | `LongPathsEnabled=1` on this host |
| OneDrive folder `C:/Users/User/OneDrive` and its subfolder | accepted in this process | accepted | PowerShell shows `ReparsePoint` (cloud tags). Python's default placeholder mode is `PHCM_DISGUISE_PLACEHOLDER` (1), so `lstat` and `GetFileAttributesW` report `0x31`/`0x10`. After `RtlSetProcessPlaceholderCompatibilityMode(PHCM_EXPOSE_PLACEHOLDERS)` in a separate process, both read `0x431`/`0x410`, and `base_refusal_reason` refuses: "component C:\Users\User\OneDrive is a reparse point". This depends on the process's mode (S63-12). Desktop is not redirected to OneDrive on this host |
| Base on a subst drive or volume mount point | refused | refused | Unchanged. A mount point is a name-surrogate redirect |

### Status of S63-01 to S63-07

| ID | Status | Evidence |
| --- | --- | --- |
| S63-01 | **Closed**; a race variant is reopened in S63-08 | cs2/cs3 refused; `test_a_case_twin_junction_base_through_a_short_parent_is_refused`; M1a and M1b red |
| S63-02 | **Closed** for the base; the target side stays as before (S63-13) | a9 and cs1 refused; Kelvin, Ohm and long-parent case-twin tests; the walk applies to every base (M1b red) |
| S63-03 | **Closed** | M1 `exit: 0,0,0`; `evidence_gate.py` → `defects=0` |
| S63-04 | **Closed** | M1c (R3) red; my K7 (`str.casefold`) red |
| S63-05 | **Closed** | M1d (R5) and M1e (R6) red |
| S63-06 | **Closed** | `WinDLL(..., use_last_error=True)` once; types declared once; error read into the reason; M1f red |
| S63-07 | **Closed** | fixture resolved; row removed; passes in CI 42123979062; M1g red |

### Reviewer counter-mutations (disposable `git clone --no-hardlinks` copy at `C:/Temp/claude/jas63rev02_mut`, removed)

These doors differ from the seat's seven. Output was read from unfiltered pytest (`-q -rfEs`), and each mutation was restored with an empty porcelain. Baseline: 70 passed, 22 subtests passed.

| ID | Mutation | Result |
| --- | --- | --- |
| K1 | every `lstat` `OSError` treated as a missing component | red: `test_a_component_that_cannot_be_examined_is_a_refusal` |
| K2 | only the base itself examined, not its ancestors | **zero red**. Under K2, AN1–AN3 are accepted (S63-10) |
| K3 | the volume root not examined | zero red. **Equivalent**: a volume root cannot carry a reparse point |
| K4 | the Windows reparse attribute ignored | red: the 4 case-fold junction tests |
| K5 | the absolute-path requirement removed | zero red. Equivalent in effect: a relative base still differs from its resolution and is refused |
| K6 | the walk continues past a missing component | zero red. Equivalent: nothing below a missing component exists |
| K7 | alias compared with `str.casefold` | red: the pathlib-fold case test |
| K8 | the `S_ISLNK` check removed | zero red. Overlap-masked: on Windows a symlink also carries the reparse bit, and on POSIX the spelling comparison refuses a symlink base |

### New findings

| ID | Class | Blocks? | Finding | Route |
| --- | --- | --- | --- | --- |
| S63-08 | `IMPLEMENTATION_DEFECT` (confinement; AGENTS.md P0) | **Yes** | `resolves_within_root` calls `base_refusal_reason(base)`, which walks the components with `lstat` and then resolves the base, and then calls `resolved_base = base.resolve()` a **second** time. The anchor of the containment check is therefore a resolution nobody checked. Probe N2 swaps the base for a junction pointing outside immediately after the first resolve. The candidate accepts `resolves_within_root(base\x, base)`, while revision01 and the base commit refuse under the identical swap, because their anchor is the resolution they compared. By reading, the same split between the walk and the resolve lets a component swapped for a case-twin junction in that window pass the `normcase` comparison. That reopens S63-01 as a race. Fix inside the boundary: resolve once, and anchor on the resolution that was checked (for example, a private helper that returns the checked resolution or a typed refusal). Then walk the components of the resolved path too, so a swap between the walk and the resolve is seen. The residual check-then-use gap after the predicate returns is inherent and not part of this finding | This correction |
| S63-09 | `IMPLEMENTATION_DEFECT` (AGENTS.md P0 source type) | **Yes** | `_component_refusal(component) -> str \| None` encodes three states, with `None` for an ordinary component, `""` for a missing component (stop the walk) and text for a refusal. `_redirected_component` branches on `refusal == ""`. A finite domain state carried as a string convention is what the P0 forbids ("有限領域狀態 … 不得把 … 字串慣例向內傳遞"). Lesser instances: the last error is held as a dynamic attribute on a `threading.local` and read with `getattr(..., "error", 0)` (an `Any` expression), and the attribute is read with `getattr(status, "st_file_attributes", 0)`. The fix is mechanical: an `Enum` (or a frozen dataclass) for the component state, and a typed holder for the last error | This correction |
| S63-10 | `EVIDENCE_DEFECT` (would let a bypass pass; rule B: close in the next change of this gate, here this correction) | No by class; must close now | The ancestor half of the walk is not pinned against the shapes it exists for. K2 (only the base examined) turns nothing red, because `test_a_junction_in_an_ancestor_of_the_base_is_refused` uses a junction whose spelling differs and is refused by the spelling comparison anyway (overlap masking). Under K2, AN1 (case-twin ancestor, long parent), AN2 (case-twin ancestor, short parent) and AN3 (Kelvin ancestor, long parent) are accepted. Add those three as tests | This correction |
| S63-11 | `OUT_OF_SCOPE_HARDENING` | No | When `st_file_attributes` is `None` or absent, `int(getattr(status, "st_file_attributes", 0))` either raises `TypeError`, which escapes `resolves_within_root` (it catches only `OSError`, probe N6), or defaults to `0`, which reads as "not a reparse point". That contradicts the rule "a component that cannot be examined is refused". It cannot be reached through CPython's `os.lstat` on Windows | Follow-up hardening, or fold into the S63-09 typing change |
| S63-12 | `TICKET_DEFECT` | No | The rule refuses any `FILE_ATTRIBUTE_REPARSE_POINT`, which includes non-surrogate tags that are not redirects: cloud-file placeholders (OneDrive), dedup, WCI. On this host the OneDrive folders are accepted only because Python runs with placeholders disguised by default. A process with placeholders exposed refuses them. A repository inside a OneDrive-synced folder, a common Windows 11 default for Desktop and Documents, would then fail. Python 3.11's `lstat` follows non-surrogate tags, so `st_reparse_tag` reads `0` and the tag cannot be used to tell them apart | Control plane: state whether the rule refuses name-surrogate tags only (junction, symlink, mount point; `IsReparseTagNameSurrogate`) plus anything that cannot be opened, or every reparse point. Either way, say what a OneDrive-hosted repository gets |
| S63-13 | `OUT_OF_SCOPE_HARDENING` (pre-existing; P0 reading) | No | On the target side, a junction inside the root that points inside the root (N1, N1b), and a leaf with a non-surrogate tag (f1), are accepted, as at revision01 and the base. Containment holds, because the target resolves inside the root. But AGENTS.md P0 says a path *reached through* a junction is refused, and the revision02 rule covers bases only | Control plane: whether the P0 covers worktree paths reached through an in-root junction; if so, a follow-up ticket for `worktree_containment` |

### Commands

From the main checkout unless noted. Python `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`. Scratch at `.worktrees/63-short-name-containment-review-scratch/rev02`.

- `git -C <review> rev-parse HEAD` → `00fdc179…`; `git status --porcelain` → empty (before and after); `git log --format=… b74840f1..HEAD`; `git diff --stat b74840f1 HEAD`; `git diff --name-only 92ee3a94 HEAD` → five paths; `git diff b74840f1 HEAD -- tests/ | grep '^-'` → one line
- `git show 8ed97a29:modules/tickets/workflow-governance/63-short-name-containment.md` (boundary and Revision02)
- `gh run view 42123979062 --json headSha,headBranch,conclusion,event,jobs`; `gh run view 42123979062 --log` → `run_log.txt`; `gh run list --branch cp/wave2-63-short-name-containment`; `../rows.py run_log.txt <review>` → Windows 47 → 8, 39 removed, CI `FAILED` set = registered rows
- `receipt_check.py <out-c1>/RETURN.md <review>` → exit 0; `evidence_gate.py … --candidate 00fdc179… --tool …dispatch_lint.py --tool …receipt_fence_check.py --tool …index_pins.py --require-cell P1 … P9 --evidence-root <out-c1>` → `cells=6 defects=0`, exit 0; `../receipt_bytes.py <out-c1>` → 0 CR, all blocks equal, exit lists equal
- `../probe.py <module> rev02` → `probe_rev02.txt`; `../probe_rp.py` → `probe_rp_rev02.txt`; `../probe_cs.py` (fresh case-sensitive temp directory via `fsutil file setCaseSensitiveInfo`, removed) → `probe_cs_rev02.txt`
- `probe_r2.py <module> rev02|rev01|base` → `probe_r2_*.txt` (N1–N8, O1–O5; subst `Q:` created and removed; mount point made and removed)
- `probe_ancestor.py <module> rev02|K2|rev01|base` → `probe_ancestor.txt`
- OneDrive: `os.lstat` / `GetFileAttributesW` in the default mode, and again after `RtlSetProcessPlaceholderCompatibilityMode(2)` in a separate process → `onedrive.txt`; `Get-Item … | Attributes` in PowerShell; registry reads of `LongPathsEnabled` and the Desktop shell folder (read only)
- `mypy --strict --python-version 3.11 --no-incremental` on the three changed Python files → exit 0; the same with `--platform linux` → exit 0; `--disallow-any-expr --follow-imports=silent` per file
- `git clone --no-hardlinks <review> C:/Temp/claude/jas63rev02_mut`, `checkout --detach 00fdc179…`, `mutate2.py` → `mutations2.txt` (K1–K8); the clone was removed
- `locked_f1.py` → host lock `C:/Temp/claude/jas-fullsuite.lock`. While I waited, it was held by `integ-58-…`. I tried `mkdir` every 20 s and acquired it at 2026-11-05T23:14:11Z as `63-rev02-initial-F1`, writing `owner.txt` with the run id and time. At acquisition, `Get-CimInstance Win32_Process` (`procs_at_acquisition.txt`) showed no other pytest; the only python processes were my own lock runner and its launcher. The full suite ran in the review worktree → `F1.txt`, exit 1. The lock was released at 23:25:00Z: after checking that `owner.txt` still named my run, I renamed the directory to `jas-fullsuite.lock.released-63-rev02-initial-F1-<uuid>` and removed it. No mutation worker or other pytest of mine ran while I held the lock

### Raw-log note

The captures in `rev02/` are unedited tool output: `probe_*.txt`, `probe_ancestor.txt`, `onedrive.txt`, `mutations2.txt`, `F1.txt`, `procs_at_acquisition.txt`, `lock_log.txt` and `run_log.txt`. The probe tables shorten paths for width only. CI was read with `gh run view` only. Nothing was pushed, and no workflow run was triggered. Counter-mutations and F1 were judged on unfiltered pytest output. No tracked file was modified anywhere.

### Not verified

- Real Windows symlinks (WinError 1314 on this host). The symlink shapes ran as junctions, and the Linux job ran the symlink tests.
- POSIX was judged by reading the code and by the Linux CI counts; I ran no POSIX interpreter.
- A mapped network drive was not created. The UNC forms were probed instead.
- Whether a real OneDrive sync client, as opposed to this host's folders with no running client, changes the default-mode result. Dedup and WCI tags are also unverified: none were present.
- The TOCTOU variant N2′ (a swap between the `lstat` walk and the resolve) was judged by reading. N2 (a swap after the first resolve) was run with a patched `Path.resolve` that performs the swap.
- A host with `LongPathsEnabled=0`.

```review-verdict
candidate: 00fdc179f07e7d57cd828634396e71af77ad352b
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/63-rev02-initial
reviewed_at: 2026-11-06
```
