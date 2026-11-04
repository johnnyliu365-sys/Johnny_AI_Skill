# REVIEW — ticket 55 Preflight gate

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `eb9014cc179ccc58b92b22fe4c1c3875da58a010` on `cp/wave2-55-preflight-gate` (parent `fc83b087`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Reviewed against | ticket 55 revision01 with its disposition correction (text-value defects are exit 3); R4-2, R4-3, R4-7, R4-8 |
| Summary | Grammar, the `TOOL_UNSERVED` causes, exits 0/2/3 for dispatch input and the tree kill on timeout hold; all 53 seat mutations reproduce red; the receipt verifies. Open: the text-value rule is not applied to the arguments (S55-01, S55-02); the exit status decided by the last tool alone survives every test (S55-05). Two Windows launch questions go to the control plane (S55-03, S55-04). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 78 passed, 101 subtests; mypy --strict clean |
| CLI and grammar | PASS | 43 grammar probes (tabs, wrong indent, duplicate and unknown keys, NaN, deep nesting, escaped NUL and surrogate, UTF-16, CR-only, early end, second block, empty file) exit 3 naming the line; BOM, CRLF, mixed endings parse |
| `TOOL_UNSERVED` causes | PASS | each cause its own line; every tool tried; two failing tools, two lines |
| Text-value rule | FAIL | inside the dispatch PASS; in the arguments S55-01, S55-02 |
| R4-2 never 1, no traceback | PASS | a closed stdout gives exit 120 (S55-10) |
| No shell / cwd | PARTIAL | argv lists with `shell=False`; a `.cmd` argv0 interprets `&` (S55-03); a relative argv0 resolves against the gate's cwd (S55-04); S55-06 |
| Timeouts / process tree | PASS | parent and grandchild killed; disclosed limits S55-08, S55-11 |
| One line per failure | PASS | U+2028, NEL, backslashes and non-cp950 characters escaped |
| STATEMENT choices | AGREE (14 of 14) | whitespace-only `expect` noted in S55-12 |
| Reverse mutations | PASS for the seat's set | 53 of 53 red; reviewer counter-mutations K1, K2, K3, K4, K6 survive (S55-05, S55-07), K13 informational |
| Receipt | PASS | checker 0 defects; four digests recomputed; LF; raw blocks byte-identical; exit lists equal |
| Boundary | PASS | README, script, test file; one commit; Johnny Liu; stdlib; no `Any`; payload closure only the pinned-sha failure |
| Full suite | NOT RUN by the reviewer | host busy; the seat's F1 shows 8 base failures |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S55-01 | IMPLEMENTATION_DEFECT | Medium | `preflight.py:341-361`, `:371-376` | the dispatch-path argument is never checked against the text-value rule: LF, TAB or ESC in it is exit 2; a lone surrogate naming an existing file is exit 0 | probes |
| S55-02 | IMPLEMENTATION_DEFECT | Low | `preflight.py:61`, `:333-335` | `--timeout "5\n"` is accepted (`$` matches before a final LF; `float()` strips) | probe → 0 |
| S55-03 | TICKET_DEFECT | Medium | `preflight.py:260-268` | on Windows a `.cmd`/`.bat` argv0 runs through cmd.exe even with `shell=False`; `a&md,injected` created a directory; the ticket must decide | probe |
| S55-04 | TICKET_DEFECT | Medium | `preflight.py:260-268`, `:386` | the child's cwd is the dispatch directory but on Windows a relative argv0 resolves against the gate's cwd, running a different program; POSIX differs | probe |
| S55-05 | EVIDENCE_DEFECT | Medium | `preflight.py:395`; tests `:475-493` | exit status from the last tool alone survives every test; no test has an unserved tool followed by a served one | K1 green |
| S55-06 | EVIDENCE_DEFECT | Low | tests `:588-593` | the metacharacter test passes under `shell=True` because each argument contains spaces and is quoted | M12 replay |
| S55-07 | EVIDENCE_DEFECT | Low | `preflight.py:51, 113, 191, 375, 380` | unpinned: the U+001F edge, a tab-only line in the block, the 120-second default, escaping of the path in read diagnostics | K2, K3, K4, K6 green |
| S55-08 | OUT_OF_SCOPE_HARDENING | Low | `preflight.py:229` | `shutil.which("taskkill")` searches the current directory first on Windows; a planted `taskkill.cmd` ran | probe |
| S55-09 | OUT_OF_SCOPE_HARDENING | Low | `preflight.py:385-394` | an unexpected error in one tool ends the run; later tools are not tried | in-process probe |
| S55-10 | OUT_OF_SCOPE_HARDENING | Low | `preflight.py:396-399`, `:326-328` | a closed stdout or stderr gives exit 120, outside 0/2/3 | probe |
| S55-11 | OUT_OF_SCOPE_HARDENING | Info | `preflight.py:226-281` | a detached process from a successful start and an orphaned grandchild of a timed-out command keep running (disclosed; long-running servers are out of wave 2) | probe |
| S55-12 | OUT_OF_SCOPE_HARDENING | Info | various | accepted: whitespace-only `expect`; duplicate tool names; probe skipped after a failed start; `--` and `-` unknown options; FF, NBSP, U+FEFF at column 0 end the block | probes |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–3 | ticket tests; mypy; payload boundary | 0; 0; 1 (pinned sha only) |
| 4 | grammar (43), argument (11), shell (4) and process probes | per row |
| 5 | receipt checker; independent receipt verifier | 0 |
| 6–7 | 53 seat mutations; 14 counter-mutations | 53 red; 6 survive |
| 8 | diff greps and identity | clean |
| 9 | full suite | not run (host busy) |
| 10 | porcelain after cache cleanup | empty |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the full suite on the candidate; POSIX behaviour (process-group kill, argv0 resolution); a `CON` device as the dispatch path; a real disk-full error.

```review-verdict
candidate: eb9014cc179ccc58b92b22fe4c1c3875da58a010
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/55-rev01-initial
reviewed_at: 2026-11-04
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `ced8bd1fb38ebb2c89f6a51140001df340f37904` on `cp/wave2-55-preflight-gate` (parent `eb9014cc`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review CodeReview §5 allows |
| Reviewed against | closure revision02 with both disposition corrections; R4-2, R4-3, R4-7, R4-8 |
| Summary | Batch files are refused in every spelling, relative names join the dispatch directory, bare names come from PATH only, the planted taskkill is not used, any failure gives exit 2, the argument text rule holds, unwritable streams give exit 2, every subject prints on one line; the seat's 31 mutations are red and the receipt verifies. Open: a drive-relative argv0 with a separator is neither joined nor refused (S55-13); two new rules can be removed with every test green (S55-14, S55-15). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 117 passed, 204 subtests; mypy --strict clean |
| Launching argv0 | FAIL | `Z:sub\prog.exe` resolves to `Z:\sub\prog.exe` (S55-13); every other spelling as specified |
| Batch refusal; planted taskkill | PASS | six letter cases, trailing space and dot, PATHEXT lookup, short names and `\\?\` forms refused; planted taskkill variants not run |
| R4-2 never 1 | PASS for behaviour | 400 fuzzed dispatch files exit 3, 2 or 0 only; S55-14 |
| Any failure → 2; per-tool unexpected error; unwritable streams; usage and grammar → 3; argument text rule; one line per subject | PASS | |
| STATEMENT choices | AGREE 18 of 19 | item 7 partly contradicted by the code (S55-13) |
| Reverse mutations | seat 31 of 31 red; reviewer 18, 3 survive | K1, K2, K3 |
| Receipt / boundary | PASS | checker 0 defects; digests recomputed; LF; trailer names the working model |
| Full suite | PASS under the host lock | 8 failed, all base names; an unlocked full suite from another agent overlapped and is recorded |

### Prior findings

| ID | Status |
| --- | --- |
| S55-01, S55-02, S55-03, S55-05 to S55-10, S55-12 | CLOSED |
| S55-04 | PARTIALLY CLOSED (S55-13, S55-15) |
| S55-11 | not taken, as disposed |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S55-13 | IMPLEMENTATION_DEFECT | Low | `preflight.py:329-335` | the separator branch runs before the drive-relative check, so `Z:sub\prog.exe` becomes `Z:\sub\prog.exe`, neither joined nor refused; on another drive the result depends on the gate's per-drive directory | probe; nothing pins the current behaviour |
| S55-14 | EVIDENCE_DEFECT | Low | `preflight.py:544-547`; tests | the run-level unexpected-error handler is unpinned since its only test moved to the per-tool path | K1 green |
| S55-15 | EVIDENCE_DEFECT | Low | `preflight.py:313`; tests | PATHEXT from the environment is unpinned | K2 green |
| S55-16 | OUT_OF_SCOPE_HARDENING | Info | `preflight.py:303-304` | stripping quotes and blanks around a PATH entry has no test | K3 green |
| S55-17 | OUT_OF_SCOPE_HARDENING | Low | `preflight.py:363-386, 500-508` | after an unexpected error once a child started, the child keeps running alongside the next tools | in-process probe |
| S55-18 | OUT_OF_SCOPE_HARDENING | Low | `preflight.py:516-518` | dispatch path `CON` or `CONIN$` blocks on console input | probe |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: POSIX behaviour; S55-13 on a real second drive; a real disk-full error; a link from a non-batch name to a batch file.

```review-verdict
candidate: ced8bd1fb38ebb2c89f6a51140001df340f37904
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/55-rev02-correction
reviewed_at: 2026-11-04
```

## Revision03 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `3a7cb3ad97ff6448e75fee1efc5970021128cb6a` on `cp/wave2-55-preflight-gate` (parent `ced8bd1f`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the initial review of revision03 |
| Reviewed against | closure revision03 with the earlier disposition corrections; R4-2, R4-3, R4-7, R4-8 |
| Summary | The six closure items hold in behaviour and every earlier rule still holds; exits stay within 0/2/3; the seat's 26 mutations are red; the receipt verifies; no new red. Open, evidence only: the tree kill after an unexpected error (S55-19), the forward-slash share and extended-length drive spellings (S55-20) and the rooted-PATH-entry skip (S55-23) can be removed with every test green. Hardening: other device-namespace prefixes are opened and one read hung (S55-21); an interrupt exits outside 0/2/3 (S55-22). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 142 passed, 2 skipped (POSIX), 368 subtests; mypy --strict clean |
| Drive rule | PASS in behaviour; pin partial (S55-20) | 47 spellings probed |
| Run-level handler; PATHEXT; PATH quotes | PASS | |
| Child cleanup | PASS in behaviour; pin partial (S55-19) | child and grandchild killed before the next tool |
| Device names | PASS for the closure; S55-21 | 21 reserved spellings exit 3 unopened |
| Batch refusal; argv0; planted taskkill; any failure gives 2; streams; argument text; grammar; one line | PASS | 400 fuzzed dispatch files exit 0, 2 or 3 only |
| STATEMENT choices | AGREE 14 of 14 | |
| Reverse mutations | seat 26 of 26 red; reviewer 16, 5 survive | K1, K2, K3, K4, K22 |
| Receipt / boundary | PASS | checker 0 defects with P9; digests recomputed; LF; three files; trailer names the working model |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S55-13 | CLOSED in behaviour; pin partial (S55-20) |
| S55-14, S55-15, S55-16 | CLOSED |
| S55-17 | CLOSED in behaviour; tree part unpinned (S55-19) |
| S55-18 | CLOSED for the closure text; wider namespace in S55-21 |
| S55-01 to S55-10, S55-12 | still closed |
| S55-11 | not taken |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S55-19 | EVIDENCE_DEFECT | Low (evidence only) | `preflight.py:414-418`; tests `:1346-1422` | a plain kill instead of the tree kill stays green: the cleanup test starts no grandchild | K1 green |
| S55-20 | EVIDENCE_DEFECT | Low (evidence only) | `preflight.py:319-323`; tests `:1124-1135` | dropping the `splitdrive` clause stays green: forward-slash shares and `//?/` spellings are untested | K2 green |
| S55-21 | OUT_OF_SCOPE_HARDENING | Low (safety: an unbounded read) | `preflight.py:91, 506-515, 563-565`; README | `\\?\`, `\??\`, UNC loopback and `GLOBALROOT` reach devices and are opened; a read of an owned pipe hung; the README claims more than the code | probes |
| S55-22 | OUT_OF_SCOPE_HARDENING | Info | `preflight.py:591-595, 414` | an interrupt after a child started kills the tree, then exits 0xC000013A with a traceback | probe |
| S55-23 | EVIDENCE_DEFECT | Info | `preflight.py:332`; tests `:840-853` | admitting PATH entries by `isabs` stays green: no test has a rooted entry without a drive | K22 green |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: POSIX behaviour; a real second drive; a console device as the dispatch path; a real disk-full error.

```review-verdict
candidate: 3a7cb3ad97ff6448e75fee1efc5970021128cb6a
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/55-rev03-initial
reviewed_at: 2026-11-04
```

## Revision03 correction review

**Verdict: `APPROVED`**

| Field | Value |
| --- | --- |
| Candidate | `c7a0409930e7df74878eeb9863b4f74c87e734ae` on `cp/wave2-55-preflight-gate` (parent `3a7cb3ad`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review of revision03 that CodeReview §5 allows |
| Reviewed against | closure revision03 with "Correction 1 under revision03" and the earlier disposition corrections; R4-2, R4-3, R4-7, R4-8 |
| Summary | S55-19, S55-20 and S55-23 are pinned (the earlier K1, K2, K4, K22 are red). The plain-dispatch-path rule holds: an oracle sweep of 744,234 spellings found no namespace, share, NT-prefix or DOS-device path admitted, an owned pipe saw no client, and ordinary paths are still served. An interrupt after a child started kills its tree and exits 2 with one line. Every earlier rule holds, exits stay within 0/2/3, the receipt verifies, no new red. Open items are non-blocking hardening (S55-24 to S55-26). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 157 passed, 2 skipped (POSIX), 513 subtests; mypy --strict clean |
| S55-19, S55-20, S55-23 | PASS, pinned | K1, K2, K22, N7 to N10 red |
| S55-21 plain dispatch path | PASS | oracle sweep; 22 real runs exit 3; 14 plain spellings exit 0; S55-24 is Info |
| S55-22 interrupt | PASS for the closure | a real pending interrupt exits 2, one line, tree dead |
| R4-2 never 1, never outside 0/2/3 | PASS | 400 fuzzed dispatch files; S55-25 window is Info |
| Regression of every earlier rule | PASS | earlier probes rerun |
| STATEMENT choices | AGREE 15 of 16 | item 4 partly contradicted (S55-24) |
| Reverse mutations | seat 23 of 23 red; reviewer 20, 19 red | K3 equivalent on this host (`ntpath.splitdrive` gives a drive for every two-separator prefix) |
| Receipt / boundary | PASS | 0 defects with P9; digests recomputed; LF; three files; trailer names the working model |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S55-19 to S55-23 | CLOSED |
| S55-01 to S55-10, S55-12 to S55-18 | still closed |
| S55-11 | not taken, as disposed |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S55-24 | OUT_OF_SCOPE_HARDENING | Info | `preflight.py:533-543` vs `:526` | the namespace check does not strip a leading drive letter, so `C:GLOBALROOT\x` is admitted; Windows treats it as a plain file and no namespace is reached | oracle sweep (779 hits, all this shape) |
| S55-25 | OUT_OF_SCOPE_HARDENING | Info (exit code in a narrow window) | `preflight.py:618-628, 642-647` | an interrupt outside `main`'s handlers (start-up, imports, stream hardening, emitting) exits 0xC000013A with a traceback | probe I3 |
| S55-26 | OUT_OF_SCOPE_HARDENING | Info (a process can be left running; disclosed) | `preflight.py:425-429, 285-313` | a second interrupt during the tree kill, or a child that exits by itself, can leave a grandchild running; the interrupt is acted on when the wait returns, bounded by `--timeout` | probes I1, I2, I4 |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: POSIX behaviour; a real console Ctrl+C; a symbolic link to a device; a DOS-device mapping or a UNC current directory; a real second drive; a real disk-full error.

```review-verdict
candidate: c7a0409930e7df74878eeb9863b4f74c87e734ae
verdict: APPROVED
reviewer: seat:ticket-review/55-rev03-correction
reviewed_at: 2026-11-04
```
