# REVIEW — ticket 60 Gate hardening (carried findings)

## Revision01 initial review

**Verdict: `APPROVED`**

| Field | Value |
| --- | --- |
| Candidate | `1c0fb9179ad5a519daf0f77a4a607c84ed4548a5` on `cp/wave2-60-gate-hardening-carried` (`98e31351` S53-30 and S54-17 first, `6dc1dd25` the other rows, `1c0fb917` tests only, on `002f8550`) |
| Reviewer | independent `ticket-review` seat (run `60-rev01-initial`) in its own detached worktree `.worktrees/60-gate-hardening-carried-review`; authored nothing in this ticket; the initial review of closure revision01 |
| References | `CodeReview.md` (§5 rule B, adopted 2026-11-05), `review-checks.md`, ticket 60 revision01, the review records and convergence dispositions of tickets 51 to 56, the dispatch `JAS-60_dispatch.yaml` |
| Summary | Every row of the items table is done as stated. All 20 counter-mutations the ticket names and the three rule-named ones are red on the candidate (reviewer rerun, unfiltered output); 19 of the reviewer's 21 own doors are red. No exit code, defect code or binding rule changed. S53-30 and S54-17 are the first commit, and each was red before its fix. Four non-blocking findings: an inherited `GIT_TEST_COMMIT_GRAPH` switches the S54-17 hardening off (S60-01, forged-store class settled by R4-4, documentation claim too strong); two evidence gaps that a later regression could exploit (S60-03 SHA-256 width, S60-04 the standard-error flush window); the M1 capture is reduced (S60-05). One information note on residual interrupt windows (S60-02). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Identity | PASS | review worktree detached at the candidate, porcelain empty before and after; three commits on `002f8550`, which is an ancestor; author and committer Johnny Liu `<johnny.liu365@gmail.com>`; each commit ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the model the STATEMENT names as the one that did the work |
| Items table (18 rows) | PASS | see the row table below |
| First commit | PASS | `98e31351` holds S53-30 (contract tests only) and S54-17 (coverage-map script, tests, README); no other change to either gate precedes it. At `98e31351` with the base `coverage_map.py` the two S54-17 tests are red (4 subtests: the forged graph moves `main^`, `main~1`, `main^1`, `HEAD^`; and the flag test); with the fix green. At `98e31351` R1 and R1b are red (8 failed each). The full-digit pin (R1c, last 39 digits) arrived in `1c0fb917`, after `6dc1dd25` changed `contract_gate.py`; the ticket's S53-30 text (a last-digit difference) was already met by `98e31351` |
| Named counter-mutations | PASS | C01, C02, C07, C08, C09; K13 (anchored on the candidate's pattern), K30, K31, K32, K33, K34, K50; R1, R1b; Y1, Y2; K9: 17 of 17 red, each with its gate's full test file, no `-x` |
| Rule-named mutations | PASS | S54-17 without the flag (G17), S55-24 without the strip (N24), S52-41 without C1 escaping (N41, the pre-ticket pattern): 3 of 3 red |
| Reviewer counter-mutations | PASS with findings | 21 own doors: 19 red; V53b (hash compared on 40 digits) and V55c (standard-error flush outside the guard) green → S60-03, S60-04 |
| Behaviour diff 002f8550..candidate | PASS | listed below; no exit code, defect code or binding rule changed |
| Changed assertions | PASS | the only removed or rewritten existing assertions are those the STATEMENT names (a: S51-29 helper and its two assertions; b: S51-26 `OUTCOMES`; c: S52-40 `CONTROLS` and two tuples; d: S55-24 `NOT_PLAIN`, additions only); each follows the row that changes its rule |
| Red before fault | PASS | S51-26: value reds stand beside the three new fault kinds (C07, C08, V51b red); S53-31 kind fault beside a red exits 1 with the red on stdout |
| One-line escaping | PASS | S52-41: U+0080, U+0085, U+009B, U+009F escaped on the usage line and in a real fault path from a real directory name; U+00A0 printed as it is; the C0, DEL, U+2028 cases still escaped. The new contract-gate kind fault carries only a hex id and a kind matched by `OBJECT_HEADER` |
| Git environment rules | PASS with finding | coverage map: `-c core.commitGraph=false` on every git child (spy test, V54a red); `GIT_CONFIG_*` still dropped, so `GIT_CONFIG_PARAMETERS` cannot undo the flag; but `GIT_TEST_COMMIT_GRAPH` is inherited and re-enables the graph (S60-01) |
| JSON input rules | PASS | not touched by the diff |
| Exit 2 on unwritable stdout or stderr | PASS | preflight with stdout closed exits 2; a usage error with both closed exits 2; the new `_interrupted` returns 2 whether or not its line is written |
| S55-25 interrupt windows | PASS with findings | a `KeyboardInterrupt` injected at the first hit of every line of `preflight.py` in a served run and a usage-error run (232 points, main thread): 228 end with exit 2 and the line `preflight.py: tool fault: interrupted` last on stderr, no traceback; 4 escape, at two single-instruction points of `entry` (S60-02). After a served result was printed, an interrupt still gives exit 2 with the success line on stdout, as the STATEMENT says |
| S55-24 | PASS | `C:GLOBALROOT\x`, `c:globalroot/x`, `C:./GlobalRoot/x`, `C:GLOBALROOT`, `C:..\GLOBALROOT.yaml` exit 3, not opened; `C:d.yaml`, `C:\x\d.yaml`, `1:GLOBALROOT` stay plain (exit 2, file absent) |
| P1 (six test files) | PASS | 1235 passed, 4 skipped, 2559 subtests, exit 0 (same counts as the seat's P1) |
| T1 | PASS | `mypy --strict --python-version 3.11` on the six scripts: no issues, exit 0 |
| Typing / dependencies | PASS | no `Any`, no `type: ignore` in the six scripts or six test files; new imports `hashlib`, `struct` (tests, stdlib) |
| Boundary / names | PASS | 12 paths changed, all `modify` lines of the boundary block; `repair_guard.py` unchanged; no forbidden path; no target-project, model or vendor name in the diff |
| Payload | PASS | `tests/test_plugin_payload_boundary.py`: 1 failed (`CommittedPinTests::test_the_pinned_sha_exists`), 40 passed |
| Receipt checker (P9 tool) | PASS | `receipt_check.py` (sha256 `2106b1a3…`, the committed blob) on `RETURN.md` against the review worktree: 0 defects, exit 0 |
| Evidence gate on the receipt | PASS | `evidence_gate.py` with the nine `--tool` paths, `--require-cell` P1, T1, M1, F1, P9: `cells=5 defects=0`, exit 0 |
| Receipt, independent | PASS | `RETURN.md` LF only, ASCII; every raw block byte-identical to its capture; exit lists equal to the `exit=` lines in capture order (M1: 45); every `tool_digest` equals the sha256 of the blob at the candidate for all nine scripts; P1, T1, M1, F1 captures start with the sha256 of those nine; P9 starts with the sha256 of `receipt_check.py`, the script it ran; the STATEMENT section equals `statement.md` |
| M1 capture | PARTIAL | every mutation red by exit code, porcelain empty at the end; the tails are reduced (S60-05) |
| Seat F1 | VALID, with a note | the seat took the lock at 01:02:04 and finished at 01:15:52. The `mut.py` processes seen during it (PIDs 12800, 29512, 28188, started 01:02:11) are ticket 58's mutation runner, working in its own disposable copy `C:/Temp/claude/jas58-mut` on `test_governance_consistency.py` and two other non-gate files; not this seat's worker (its M1 had ended at 20:06 the day before). That runner shares no checkout or runtime root with the seat's worktree and could only add failures, not hide them; the seat's 8 failures are all base names. `F1.wait` recorded only pytest processes at acquisition, so the runner, which started 7 s later, is not in it. The reviewer's own F1 is the check |
| Full suite (reviewer) | PASS under the host lock | run id `60-rev01-initial`; waited from 01:50:59 (the locks of 50-rev01, 59-rev01, jas58 and jas57c in turn), took the lock with `mkdir` at 02:43:19 with the run id and time in `run.txt`; no other pytest or mutation process at acquisition or at the end (`Get-CimInstance Win32_Process`); `pytest tests -q`: 8 failed, 3306 passed, 35 skipped, exit 1; every failing name is in `jas48_F1_base.txt`, zero new red, `test_codex_lifecycle_oracle.py` green; lock removed at 02:56:07 because its file still named this run; porcelain empty |

### Behaviour changes, 002f8550..candidate

| Gate | Change | Exit / code / rule |
| --- | --- | --- |
| evidence gate | docstring and README only (S51-27 text) | unchanged |
| requirement snapshot | `LINE_BREAK_PATTERN` widened from `\x85` to `\x7f-\x9f`: every C1 control is escaped on every printed line | unchanged (input rules for text values unchanged; printing only) |
| contract gate | a blob entry served as another kind: the fault text now names the id and the kind (`another kind of object`, `mismatch`) | unchanged: `TOOL_FAULT`, exit 2, store not used again |
| coverage-map guard | `-c core.commitGraph=false` on every git child | unchanged; a relative revision now resolves from the commit objects |
| preflight gate | `C:GLOBALROOT…` (global root right after a drive letter and colon) refused | exit 3 instead of an open attempt (the row's rule) |
| preflight gate | an interrupt outside the inner handlers of `main` and in the final flush | exit 2 with one line instead of a traceback and the interpreter's interrupt status |
| repair guard | none (tests only) | unchanged |
| README | S51-27, S52-41, S53-31, S53-32, S54-17, S55-24, S55-25 sentences | describes the above |

### Ticket rows

| Gate | Row | Status | Evidence |
| --- | --- | --- | --- |
| evidence gate | S51-26 | DONE | three outcomes added to `DigestValueBeforeLookupTests`; C07, C08, V51b red |
| evidence gate | S51-27 | DONE | README and docstring; `NonBlobToolTests` (tree, absent path, path below a blob) both ways; the "submodule entry" spelling the text names is not among the tested spellings (not verified) |
| evidence gate | S51-28 | DONE | `DigestValueCountTests`; C01, C02, C09, V51a red |
| evidence gate | S51-29 | DONE | the helper uses the temporary directory only, with a `.git` file naming no git directory; judged by git's exit code; the test matches the gate's own text |
| requirement snapshot | S52-37 | DONE | K50, V52f red |
| requirement snapshot | S52-38 | DONE | `MoreStrayVersionNameTests`; K30, K31, K32, V52a, V52b, V52c red |
| requirement snapshot | S52-39 | DONE | `StrayClaimNameTests`; K33, K34, V52d, V52e red |
| requirement snapshot | S52-40 | DONE | K13 red |
| requirement snapshot | S52-41 | DONE | C1 range escaped; U+009B from a root path on the success and `unchanged` lines; N41, V52g red |
| contract gate | S53-30 | DONE (first commit) | R1, R1b red at `98e31351` and at the candidate; nine digit positions for blob and tree answers (`1c0fb917`); V53a, V53c red; SHA-256 width unpinned (S60-03) |
| contract gate | S53-31 | DONE | blob entry serving a tree and a commit, and beside a red; V53d red |
| contract gate | S53-32 | DONE | README sentence; agrees with SPEC R4-4 trust boundary text |
| coverage-map guard | S54-16 | DONE | Y1, Y2, V54b red |
| coverage-map guard | S54-17 | DONE (first commit) | flag on every child; forged-graph test proves plain git is moved, then requires the true result; G17, V54a red; red before the fix; residual door S60-01 |
| preflight gate | S55-24 | DONE | N24, V55a red; CLI probes exit 3 |
| preflight gate | S55-25 | DONE | eight interrupt-window tests (one through a child process) and one unchanged run; V55b, V55d red; 228 of 232 injection points exit 2; S60-02, S60-04 |
| repair guard | S56-27 | DONE | K9, V56a, V56b red |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S60-01 | IMPLEMENTATION_DEFECT | Low; safety-adjacent, in the forged-store class R4-4 settles (does not block under rule B, as S54-17 itself did not) | `coverage_map.py:261-272` (`git_environment`), `:285`; README S54-17 sentence; docstring `:83-84` | git reads a commit-graph whenever `GIT_TEST_COMMIT_GRAPH` is true, whatever `core.commitGraph` says. The guard drops the repository-selecting and `GIT_CONFIG_*` names but inherits `GIT_TEST_COMMIT_GRAPH`. With `GIT_TEST_COMMIT_GRAPH=1` (or `true`) in the environment and the forged graph of the S54-17 test, `--base main^ --candidate main` over a real removal exits 0 with `removed=0 defects=0`; without the variable it exits 1 `UNMAPPED_REMOVAL`. The README sentence this candidate adds ("a forged commit-graph file cannot move a parent") is therefore too strong. Needs write access to the store and control of the guard's environment; an integration clone filled by fetch carries no seat commit-graph. Fix: drop `GIT_TEST_COMMIT_GRAPH` (or every `GIT_TEST_*` name) from the child environment, with a test. Under rule B this is the "a regression would let a forbidden change pass" kind: it goes with the next change of this gate | probe `probe_cg_env.py`: plain exit 1; `GIT_TEST_COMMIT_GRAPH=1` exit 0; `=true` exit 0 |
| S60-02 | OUT_OF_SCOPE_HARDENING | Info (exit is the interpreter's interrupt status, never 0 or 1) | `preflight.py:662`, `:668`, `:672` | an interrupt landing exactly on `entry`'s `try` line, on its `return code` line, in `sys.exit(entry())` or during the import still escapes with a traceback. Each window is a few bytecodes wide and unreachable without tracing; the README's "any other window of the run" reads wider than that. Closing them needs a SIGINT handler or the wave-3 job object (S55-11, S55-26) | 4 of 232 injection points |
| S60-03 | EVIDENCE_DEFECT | Low (exploiting it needs a 160-bit SHA-256 prefix collision) | `contract_gate.py:606`; tests `ForgedObjects` near-miss tests | the full-width pin covers 40-digit ids only: a comparison truncated to the SHA-1 width (`hexdigest()[:40] != oid[:40]`) passes every test, so the last 24 digits of a SHA-256 id are unpinned although the docstring and README say SHA-256 repositories are read the same way. Behaviour is correct. Same kind as S53-30: goes with the next change of the contract gate | V53b green |
| S60-04 | EVIDENCE_DEFECT | Low (a regression changes 2 into the interpreter's interrupt status; never 0 or 1) | `preflight.py:660-669`; test `test_an_interrupt_in_the_final_flush_is_exit_two_with_one_line` | the final-flush test interrupts the first `_settle` call (standard output) only; moving `_settle("stderr")` outside the guard leaves every test green. Behaviour is correct | V55c green |
| S60-05 | EVIDENCE_DEFECT | Low (receipt only) | `.worktrees/60-gate-hardening-carried-out/M1.txt` | each mutation's tail keeps only the FAILED and SUBFAILED lines (cut at 25 with `... N more failing lines`, five times) and the summary; no assertion text, so the capture does not show that a mutant turned red for its intended reason (`review-checks.md`, counter-mutation point 5). The red decisions stand: the reviewer's unfiltered rerun of every named mutation is red | read; reviewer rerun |

No `TICKET_DEFECT` and no `REQUIREMENT_CHANGED` finding. Observation for the control plane, outside this ticket: ticket 50's `integrate.py` candidate also relies on `-c core.commitGraph=false` and does not name `GIT_TEST_COMMIT_GRAPH`; its clone is not seat-writable under R4-4, so S60-01 has no effect there, but the same one-line environment rule applies.

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `git status --porcelain`; `git log`, `git diff --stat` and per-commit `git show --stat` over `002f8550..HEAD`; `merge-base --is-ancestor` | 0; empty |
| 2 | `git diff 002f8550..HEAD -- skills/` and `-- tests/` (removed-line listing) | 0 |
| 3 | `mypy --strict --python-version 3.11 --no-incremental` on the six scripts | 0 |
| 4 | P1: `python -m pytest` on the six gate test files `-q -p no:cacheprovider` | 0 |
| 5 | `python -m pytest tests/test_plugin_payload_boundary.py -q -p no:cacheprovider -rfE` | 1 (the allowed test only) |
| 6 | `receipt_check.py RETURN.md <review worktree>`; `evidence_gate.py RETURN.md --repo … --candidate 1c0fb917… --evidence-root <out> --tool ×9 --require-cell ×5`; independent verifier `rverify.py` | 0; 0; 0 |
| 7 | first-red: `git archive 98e31351` into `C:/Temp/claude/jas60-rev01-first`, base `coverage_map.py` swapped in, `-k commit_graph`; R1, R1b on the commit-1 tree | 1 (5 red), 0 with the fix; 1, 1 |
| 8 | `rmut.py all 3`: 41 mutations, each in `C:/Temp/claude/jas60-rev01-mut/<id>` (copy of the scripts directory and the gate's own full test file), full file, no `-x` | 39 red, 2 green |
| 9 | `probe_interrupt.py` (232 injection points); `probe_cg_env.py`; S55-24 and S52-41 CLI probes; closed-stream probes | 0; 1 (2 of 3 red, the finding); — |
| 10 | process listing with `Get-CimInstance Win32_Process` (pytest, mutation workers) | 0 |
| 11 | full suite under the host lock, run id `60-rev01-initial` (`fullsuite.sh`) | 1 (8 failed, all base names) |
| 12 | `git status --porcelain` after every step | empty |

Raw logs: retained in `.worktrees/60-gate-hardening-carried-review-scratch/` (unfiltered pytest output of every mutation in `mutlog/`, `R_M.txt`, `R_P1.txt`, `R_payload.txt`, `R_rc48.txt`, `R_eg.txt`, `R_verify.txt`, `R_probe_interrupt.txt`, `R_probe_cg_env.txt`, `R_F1.txt`, `R_lock.log`, `R_procs_at_lock.txt`); not committed. No output-reducing wrapper sat between the reviewer and the commands; every red and green above was judged on the full pytest output.

Not verified: Linux and case-sensitive file systems; a real console Ctrl+C or Ctrl+Break delivered to a running preflight (interrupts were injected in-process, main thread only); the import-time window; the "submodule entry" spelling of S51-27; a SHA-256 repository for the contract-gate near-miss (only the width, by mutation); a split commit-graph chain (`info/commit-graphs`) and commit-graphs in alternates (`core.commitGraph=false` turns graph reading off unless `GIT_TEST_COMMIT_GRAPH` is set, S60-01; not probed); git other than 2.54.0.windows.1.

```review-verdict
candidate: 1c0fb9179ad5a519daf0f77a4a607c84ed4548a5
verdict: APPROVED
reviewer: seat:ticket-review/60-rev01-initial
reviewed_at: 2026-11-06
```
