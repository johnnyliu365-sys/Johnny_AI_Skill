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
