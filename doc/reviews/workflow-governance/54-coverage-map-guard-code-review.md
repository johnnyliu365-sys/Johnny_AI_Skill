# REVIEW — ticket 54 Coverage-map guard

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `285e6df857a911cf79b4439d8bed8f9a43ee7cbf` on `cp/wave2-54-coverage-map-guard` (`8c91e85d` feature, `285e6df8` docstring and README only, on `c0ab4a08`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Summary | Enumeration, the five codes and the map read at the candidate are correct and cross-checked on real history. Blocking: a plain directory is accepted as `--repo` (S54-01); a `--specs` that names nothing passes (S54-02, ticket defect); two inputs exit 2 where the ticket asks for 1 or 3 (S54-03, S54-04); eight counter-mutations stay green (S54-07). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Identity / boundary / stdlib / typing | PASS | both commits Johnny Liu; README, script and test file only; no `Any`, no `type: ignore` |
| Ticket tests / mypy | PASS | 62 passed, 96 subtests; mypy --strict clean |
| Removed-test enumeration | PASS | module, class, nested class, async, moved, renamed, deleted and added specs, CRLF; real-history cross-check 20 = 20 and 0 = 0 |
| Five defect codes; map read at `--candidate`; map absent or not JSON | PASS | |
| `--specs` prefix cases | PASS with finding | `specs2`, trailing slash, backslash, `./` correct; `..` and absolute → 3; a `--specs` naming nothing → 0 (S54-02) |
| Faults → 2 | PARTIAL | unknown commits and unparseable specs → 2; a plain directory inside a repository → 0 (S54-01) |
| Usage → 3 | PARTIAL | a lone surrogate in `--map` or `--specs` → 2 (S54-04) |
| Red never 2 / fault never 1 | PARTIAL | non-UTF-8 spec path → 2 (S54-03); symlinked spec → 2 (S54-06) |
| One line per subject | PARTIAL | stdout always one line; the stderr parse-fault message and an echoed `--base` split (S54-05) |
| Receipt mutations M1–M21 | PASS | all red, each copy restored |
| Reviewer counter-mutations | FINDING | 17 of 25 red; C3–C7, C15, C16, C25 green (S54-07); C13 redundant |
| STATEMENT choices 1–13 and the two commits | ACCEPT | the second commit changes only the docstring and README (identical `ast` otherwise); gaps noted in S54-02, S54-04, S54-06, S54-07 |
| Receipt / fourth digest / payload closure | PASS | checker 0 defects; `355481dd…` recomputed |
| README | PASS (minor) | says `git show` where the script reads the blob by `ls-tree` and `cat-file`; the `CODE "<id>"` shape does not hold for `MAP_ROW_INVALID` |
| Full suite | PASS | 8 failed, all base names |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S54-01 | IMPLEMENTATION_DEFECT | Medium | `coverage_map.py:386`; tests `:521-525` | `rev-parse --git-dir` passes for any directory inside a work tree, so a plain directory is judged as the enclosing repository and exits 0; the test passes only because the system temp directory lies outside any repository | probes 8c, 8d |
| S54-02 | TICKET_DEFECT | Medium | ticket 54 defect-class row 2; `coverage_map.py:249-253` | the ticket names an empty `--specs` but gives no outcome; a `--specs` naming nothing at either commit exits 0 with `removed=0` while a test was removed | probes 5b–5e |
| S54-03 | IMPLEMENTATION_DEFECT | Low | `coverage_map.py:274-277` | a spec path that is not UTF-8 is a tool fault even when git serves it and nothing changed | probes 3a, 3b |
| S54-04 | IMPLEMENTATION_DEFECT | Low | `coverage_map.py:268, 396, 408-420` | a lone surrogate in `--map` or `--specs` passes argument checks and exits 2 with `UnicodeEncodeError` | probes 8i, 8j |
| S54-05 | IMPLEMENTATION_DEFECT | Low | `coverage_map.py:243, 179` | the parse-fault message appends the `SyntaxError` text, which repeats the raw path; a raw `--base` is echoed the same way; a newline splits the stderr line | probes 2b, 8k |
| S54-06 | TICKET_DEFECT | Low | `coverage_map.py:272` | the ticket is silent on symlinked spec files; the link blob is parsed as Python and faults even when nothing changed | probe 4 |
| S54-07 | EVIDENCE_DEFECT | Low | `coverage_map.py:221-234, 272, 401, 333-338`; tests | tests in `else`, `with`, `for`, `while`, `match`, `except` blocks, the submodule skip, a submodule map path and "a shape-invalid row covers nothing" are claimed but not pinned | counter-mutations C3–C7, C15, C16, C25 green |
| S54-08 | OUT_OF_SCOPE_HARDENING | Low | `coverage_map.py:241` | specs are parsed with the running interpreter's grammar; Python 3.12 syntax exits 2 under 3.11 | probe 8g |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | worktree identity, status, diff, `git show` | 0 |
| 2–4 | ticket tests; mypy; `Any` and import audit | 0; 0; 1 (no match) / 0 |
| 5 | `ast` comparison of the two commits; tests diff | 0 |
| 6 | probe suite on scratch repositories | 0 |
| 7–8 | receipt checker; four digests | 0 |
| 9 | real-history cross-check, two ranges | 0 |
| 10 | 46 mutations on a disposable copy | 0 |
| 11–13 | quiet-host wait; full suite; failure names against the base | 0; 1 (8 base); 0 |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a Linux or POSIX host (S54-03 and S54-04 reproduced through git plumbing and Windows wide argv only); SHA-256 object-format repositories; submodules beyond the counter-mutations; the implementer's own mutation driver; fast-forward onto the wave-2 tip.

```review-verdict
candidate: 285e6df857a911cf79b4439d8bed8f9a43ee7cbf
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/54-rev01-initial
reviewed_at: 2026-11-04
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `414822941e92f12cfa47323084ee735652747c83` (`41482294` correction 1 → `285e6df8` → `8c91e85d`, on `c0ab4a08`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review CodeReview §5 allows |
| Exit mapping | reviewed as 0/1/2/3 with exit 2 for tool faults (R4-7); the R4-2 table row awaits the owner's correction and is not raised against this candidate |
| Summary | S54-01 to S54-07 are closed: `--repo` top level, absent `--specs`, links and submodules, surrogate-escaped paths, the argument and row text rules and one-line stderr hold under probes, and the seat's 24 mutations are red. Open: an empty tree object is read as absent (S54-09); four counter-mutations stay green (S54-10). Both are Low and fail closed. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Identity / boundary / typing | PASS | three files; Johnny Liu; stdlib; trailer names the working model |
| Ticket tests / mypy | PASS | 84 passed, 198 subtests; mypy --strict clean |
| `--repo` | PASS | probes a1–a11 |
| `--specs` | PASS with finding | an empty tree object exits 2 (S54-09) |
| Links and submodules | PASS with finding | an empty tree object at the map path reads as absent (S54-09) |
| Non-UTF-8 paths; argument text rule; one-line output | PASS | |
| Block kinds | PASS with finding | second `except`, second `case`, helper nesting unpinned (S54-10) |
| Map row text values | PASS with finding | U+001F boundary unpinned (S54-10) |
| R4-2 | PASS with finding | S54-09 |
| Seat mutations | PASS | 24 of 24 red |
| Reviewer counter-mutations | FINDING | 27 run: 19 red; R11, R19, R20, R21 findings; R15, R23, R25, R26 not |
| Receipt / README / payload | PASS | checker 0 defects; digests recomputed; LF |
| Full suite | PASS | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S54-01, S54-03 to S54-06 | CLOSED |
| S54-02 | CLOSED except the empty tree object (S54-09) |
| S54-07 | CLOSED for the items named; same-family gaps in S54-10 |
| S54-08 | not taken, confirmed in the README |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S54-09 | IMPLEMENTATION_DEFECT | Low | `coverage_map.py:253, 316-321, 459, 469`; test `:645` | trees are inferred from file paths (`ls-tree -r` without `-t`): an empty tree object at `--specs` exits 2 "names no tree", and at the map path reads as absent | probes b5, c8 |
| S54-10 | EVIDENCE_DEFECT | Low | `coverage_map.py:94, 276-278, 288-289, 293-294`; tests | unpinned: U+001F in row fields; a second `case`; a second `except`; a `test_` function nested in a helper | R11, R19, R20, R21 green |
| S54-11 | OUT_OF_SCOPE_HARDENING | Low | `coverage_map.py:220-222, 233` | git inherits `GIT_DIR`; inside a hook a plain directory is accepted as `--repo` | probe a8 |
| S54-12 | OUT_OF_SCOPE_HARDENING | Low | `coverage_map.py:389` | a repeated JSON key keeps its last value | probes h1, h2 |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a Linux or POSIX host; SHA-256 repositories; nested submodule checkouts; the seat's own mutation driver; fast-forward onto the wave-2 tip.

```review-verdict
candidate: 414822941e92f12cfa47323084ee735652747c83
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/54-rev02-correction
reviewed_at: 2026-11-04
```
