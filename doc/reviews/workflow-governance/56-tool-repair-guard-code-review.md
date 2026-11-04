# REVIEW — ticket 56 Tool-repair guard

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `02d40fd2b987abad412425d2031e4ac9cd0a7fbf` on `cp/wave2-56-tool-repair-guard` (one commit on `8db60c55`) |
| Ticket | revision01, blob `0be71391`, identical at the base, the candidate and the wave-2 tip |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Summary | Ticket tests, mypy, the receipt and the full suite pass, and most contracts hold under end-to-end probes. Blocking: a submodule pointer change can be hidden by tracked repository content and the guard exits 0 (S56-01); four text, case and stream defects (S56-02 to S56-05); six counter-mutations survive (S56-06). Two ticket defects go to the control plane (S56-07, S56-08). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 79 passed, 55 subtests; mypy --strict clean |
| Seat mutations | PASS | 37 of 37 red, first failing test as captured |
| Reviewer counter-mutations | FINDING | 15 run: 4 red, 3 equivalent (C1, C2, C9), 8 findings (S56-02, S56-04, S56-06) |
| Contracts by probe | PASS except the findings | allowlist and prefix cases, exact entries, Windows case variants, undecoded URL text, refused entries, empty lists, gate scripts always protected, renames on both sides, deletions, binaries, mode and type changes, merges, root commits, unknown commits, tags, linked and bare repositories, scrubbed environment |
| STATEMENT choices | 8 agree, 2 disagree | non-UTF-8 dispatch (S56-03); `casefold` (S56-04) |
| Receipt | PASS | checker 0 defects; four digests recomputed; LF; raw blocks byte-identical; exit lists equal |
| Boundary | PASS | three files as declared; Johnny Liu; stdlib; no `Any`; payload closure only the pinned-sha failure |
| Full suite | PASS | 8 failed, all base names; single-file runs of other seats overlapped, recorded |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S56-01 | IMPLEMENTATION_DEFECT | Medium (blocking) | `repair_guard.py:315` | `git diff` honours `submodule.<name>.ignore` from a tracked `.gitmodules` and `diff.ignoreSubmodules`; with `ignore = all` a commit that moves a gitlink outside the allowlist or under a protected entry gives `paths=0`, exit 0 | probe; `--ignore-submodules=none` shows the path |
| S56-02 | IMPLEMENTATION_DEFECT | Medium (blocking) | `repair_guard.py:185-194` | a raw control character inside a JSON string on a block line exits 3, while the escaped form, DEL, or a tab between tokens exits 1 | probes; C7 green |
| S56-03 | IMPLEMENTATION_DEFECT | Medium (blocking) | `repair_guard.py:388-390`; tests `:504` | invalid UTF-8 anywhere in the dispatch exits 3, also on lines the gate does not read, while the text rule makes it a red | probes; C8 turns exactly that test red |
| S56-04 | IMPLEMENTATION_DEFECT | Low (blocking) | `repair_guard.py:108-109` | full Unicode case folding widens the allowlist beyond what NTFS treats as one name (`strasse/` covers `straße/a.py`; `kit/` covers a Kelvin-sign path) | probes; C12 green |
| S56-05 | IMPLEMENTATION_DEFECT | Low (blocking) | `repair_guard.py:395-398, 413-417` | a closed stdout gives exit 120 | probe |
| S56-06 | EVIDENCE_DEFECT | Medium (blocking) | `repair_guard.py:269, 77-88, 226, 283-284, 314`; tests | unpinned: `--no-replace-objects` (a replace ref then hides a protected change), two scrubbed variables, the gate directory case rule, one-line multi-line git errors, the SHA-256 empty tree | C3–C6, C11, C15 green; C3 bypass reproduced |
| S56-07 | TICKET_DEFECT | Low | ticket 56 defect codes, text values | the text rule needs an exit-1 code the table does not name; precedence of usage, text reds and git output undefined | read |
| S56-08 | TICKET_DEFECT | Low | ticket 56 dispatch blocks; R4-8; R4-2 | the ticket requires `protected_paths:` which R4-8 does not name; R4-2 has no row for this gate | read |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: paths with a newline end to end (Git for Windows refuses them); Linux and macOS; SHA-256 repositories; grafts; very large commits; a full suite with no concurrent pytest at all.

```review-verdict
candidate: 02d40fd2b987abad412425d2031e4ac9cd0a7fbf
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/56-rev01-initial
reviewed_at: 2026-11-04
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `8b084b506957c668f86d57932d1669aa8cc1bc18` on `cp/wave2-56-tool-repair-guard` (correction 1 on `02d40fd2`) |
| Ticket | closure revision02 (blob `d26b19ad` on the wave-2 branch) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review CodeReview §5 allows |
| Summary | S56-01 to S56-05 are closed under probes; tests, mypy, the receipt and the full suite pass. Blocking: a repository-local graft file or `GIT_GRAFT_FILE` re-parents the repair commit, and a commit that changes the gate scripts then exits 0 (S56-09, a live bypass); the replace-ref fix is pinned on the diff call only (S56-10). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 118 passed, 100 subtests; mypy --strict clean |
| Seat mutations | PASS | 25 of 25 red; M2 confirmed equivalent; per-code mutations rerun by the reviewer at the candidate, all red |
| Reviewer counter-mutations | FINDING | 9 run: 2 red, 7 green (S56-10, S56-11, S56-12, S56-13) |
| S56-01 by probe | PASS | a pointer change counts under every tracked, repository, global, system and environment configuration tried, and in a bare repository |
| Replace refs and environment | PASS except grafts | replace refs on the commit, parent and tree all red; fourteen `GIT_*` variables change nothing; shallow boundaries exit 2; grafts exit 0 (S56-09) |
| S56-02, S56-03, S56-04, S56-05 | PASS | including a full upcase-table check that protection never narrows |
| Seat choices | 2 agree, 2 partly disagree | S56-12, S56-13, S56-14 |
| Receipt / boundary | PASS | checker 0 defects; digests recomputed; LF; the M1 capture was edited after the run (S56-14) |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S56-01 to S56-04, S56-07 | CLOSED |
| S56-05 | CLOSED for the named cases (S56-12) |
| S56-06 | PARTLY OPEN (S56-09, S56-10) |
| S56-08 | control plane: correction proposed, awaiting the owner |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S56-09 | IMPLEMENTATION_DEFECT | High (blocking; lets a forbidden change pass) | `repair_guard.py:388` | `--no-replace-objects` does not switch off grafts: a graft line or `GIT_GRAFT_FILE` re-parents the repair onto a twin with the same tree, so a gate-script change gives `paths=0`, exit 0; also from the common directory of a linked worktree, for a grafted merge and for a grafted root | probes |
| S56-10 | EVIDENCE_DEFECT | Medium (blocking; safety unpinned) | `repair_guard.py:344`; tests | the parent query can drop `--no-replace-objects` with every test green; under that mutant a replacement passes a forbidden change | CM1 green |
| S56-11 | EVIDENCE_DEFECT | Low | `repair_guard.py:111, 179, 279, 370-371` | unpinned: `GIT_COMMON_DIR` scrub, bare-repository acceptance, a line ending in two carriage returns, one ASCII table letter | CM2, CM3, CM4, CM7 green |
| S56-12 | TICKET_DEFECT | Low (changes an exit code) | `repair_guard.py:504-508` | with a red and a dead stderr, the reds are delivered on stdout but the exit is 2; the ticket gives no precedence | probe; CM5 green |
| S56-13 | TICKET_DEFECT | Low | `repair_guard.py:305-306, 487` | with a text-defective dispatch, a gate-script change is not reported although that rule needs no entry | probe; CM6 green |
| S56-14 | EVIDENCE_DEFECT | Low | receipt M1 | the M1 capture was edited after the run to remove an equivalent survivor; the per-code mutations were not rerun at the candidate | comparison; reviewer rerun |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: paths with a newline end to end; Linux and macOS; short-name and trailing-dot aliases of the gate directory; very large commits; a full suite with no concurrent pytest.

```review-verdict
candidate: 8b084b506957c668f86d57932d1669aa8cc1bc18
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/56-rev02-correction
reviewed_at: 2026-11-04
```
