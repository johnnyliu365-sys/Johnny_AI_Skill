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
