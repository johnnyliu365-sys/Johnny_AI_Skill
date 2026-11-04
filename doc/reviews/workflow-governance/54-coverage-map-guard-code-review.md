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

## Revision03 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `b111300eb02d541244b24123aff9ebc102e389a8` (`b111300e` pre-review addition → `f308f400` implementation 3 → `41482294` → `285e6df8` → `8c91e85d`, on `c0ab4a08`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the initial review of revision03 |
| Exit mapping | 0/1/2/3 with exit 2 for faults (R4-7); red before fault reviewed as binding; the R4-2 table row awaits the owner |
| Summary | S54-09 to S54-12 are closed; the git-environment rule holds under probes (replace refs on blobs, trees and commits, `core.useReplaceRefs`, `GIT_CONFIG_PARAMETERS`, partial clone, scrubbed variables); the regression pass is clean; every seat mutation is red. Open, evidence only: five red-before-fault edges (S54-13) and the `GIT_CONFIG_*` prefix (S54-14). Hardening: grafts move a relative `--base` (S54-15). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Identity / boundary / payload | PASS | three files per commit; Johnny Liu; trailer names the working model |
| Ticket tests / mypy | PASS | 113 passed, 238 subtests; mypy --strict clean |
| S54-09, S54-11, S54-12 | PASS | empty tree objects at `--specs` and at the map path; scrubbed variables; repeated keys in every position |
| Git-environment rule | PASS with findings | S54-14, S54-15 |
| Red before fault | PASS with finding | S54-13 |
| One line per subject; regression S54-01 to S54-08 | PASS | |
| Seat mutations | PASS | 25 of 25 and 6 of 6 red; seven re-expressed at the candidate, all red |
| Reviewer counter-mutations | FINDING | 16 run: 10 red, X5 to X10 green |
| Receipts / README | PASS | both receipts 0 defects; digests recomputed per commit; LF; P9 present |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S54-01 to S54-07, S54-09 to S54-12 | CLOSED |
| S54-08 | not taken, confirmed in the README |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S54-13 | EVIDENCE_DEFECT | Low (exit code in mutants; not safety) | `coverage_map.py:587, 406, 430, 635, 457-460`; tests `:917-987` | five red-before-fault edges unpinned: the `::` separator in the unknown-path match; a non-`ToolFault` error in three stages losing reds; a spec whose base blob cannot be read inventing `CARRIED_TARGET_MISSING` | X5 to X8, X10 green |
| S54-14 | EVIDENCE_DEFECT | Low | `coverage_map.py:259`; test `:1303` | the `GIT_CONFIG_*` removal is pinned for two names only | X9 green |
| S54-15 | OUT_OF_SCOPE_HARDENING | Low (safety: a removed test can escape with a relative revision and a local graft) | `coverage_map.py:292-296, 269` | `--no-replace-objects` does not disable grafts; with `info/grafts` or `GIT_GRAFT_FILE`, `--base main^` resolves to the grafted parent and a real removal gives `removed=0` | probes |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a Linux or POSIX host; SHA-256 repositories; lazy fetch over a network protocol; git older than 2.44; commit-graph content; the seat's own mutation drivers; fast-forward onto the wave-2 tip.

```review-verdict
candidate: b111300eb02d541244b24123aff9ebc102e389a8
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/54-rev03-initial
reviewed_at: 2026-11-04
```

## Revision03 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `763284bfa9dff9db330b9f6ec357ba836f7a837f` (`763284bf` correction 1 → `b111300e` → `f308f400` → `41482294` → `285e6df8` → `8c91e85d`, on `c0ab4a08`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review of revision03 CodeReview §5 allows |
| Exit mapping | 0/1/2/3 with exit 2 for faults (R4-7); red before fault binding; the R4-2 row and the object-store trust boundary await the owner and are not raised |
| Summary | S54-13 to S54-15 are closed as named: grafts in every form built no longer move a relative revision; the regression pass matches the initial review except the three graft probes, now correct; 13 of 14 seat mutations red and G2 equivalent. Open, evidence only: the unknown-path match is unpinned for a leading segment and for case (S54-16). Hardening, safety in the forged-store class: a forged commit-graph moves `--base main^` and a real removal exits 0 (S54-17). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Identity / boundary / payload | PASS | three files; Johnny Liu; trailer names the working model; stdlib only |
| Ticket tests / mypy | PASS | 122 passed, 249 subtests; mypy --strict clean |
| S54-13 | PASS with finding | five edges pinned; prefix and case of the unknown-path match unpinned (S54-16) |
| S54-14, S54-15 | PASS | the whole `GIT_CONFIG_*` family; grafts in the repository, a linked worktree's common directory and an inherited `GIT_GRAFT_FILE` in either case |
| Other history rewriting | FINDING (hardening) | replace refs and forged loose commits handled; a forged commit-graph moves relative revisions (S54-17) |
| Seat choices | ACCEPT | the random non-existent graft path fails closed |
| Red before fault / R4-2 / one line | PASS with finding | S54-16 in mutants only |
| Regression S54-01 to S54-12 | PASS | |
| Reverse mutations | seat 13 red, G2 equivalent; reviewer 16: 11 red, Y1 and Y2 findings, Y3, Y5, Y7 equivalent | |
| Receipt / README | PASS with note | the README claim about relative revisions is overstated under a forged commit-graph |
| Full suite | PASS under the host lock | second run 8 failed, all base names; a first run under heavy load had two extra `test_codex_lifecycle_oracle.py` failures that pass alone |

### Prior findings

| ID | Status |
| --- | --- |
| S54-01 to S54-07, S54-09 to S54-12, S54-14 | CLOSED |
| S54-08 | not taken |
| S54-13 | CLOSED for the five edges; same-family gap S54-16 |
| S54-15 | CLOSED for grafts; commit-graph door S54-17 |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S54-16 | EVIDENCE_DEFECT | Low (exit code in mutants; not safety) | `coverage_map.py:600-602`; test `:1043` | the unknown-path match is pinned for the separator and suffixes but not for a leading segment or for case; under either mutant a found red is dropped and the run exits 2 | Y1, Y2 green; probes |
| S54-17 | OUT_OF_SCOPE_HARDENING | safety (a removed test escapes with exit 0; needs write access to the commit-graph file) | `coverage_map.py:284`; README `:170`; docstring `:86` | git takes parents from the commit-graph; a forged one moves `main^` and other relative revisions; a full sha is unaffected; `-c core.commitGraph=false` neutralises it in plain git; an integration clone filled by fetch does not carry the seat's commit-graph | probes H5, CG1 |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a Linux or POSIX host; SHA-256 repositories; split commit-graph chains; git older than 2.54; `core.commitGraph=false` against the guard itself; fast-forward onto the wave-2 tip.

```review-verdict
candidate: 763284bfa9dff9db330b9f6ec357ba836f7a837f
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/54-rev03-correction
reviewed_at: 2026-11-05
```

### Control-plane disposition (2026-11-05): held for the owner

The blocking item, S54-16, is an evidence gap on a behaviourally correct candidate; S54-17 is a forged-store door of the class the fourth spec correction (R4-4 trust boundary) addresses, with a one-flag hardening available (`-c core.commitGraph=false` on every git child). Both outcomes depend on owner decisions now open: the convergence rule and the R4-4 trust boundary. The control plane does not open revision04. Under the proposed convergence rule this candidate would be approvable with S54-16 carried and S54-17 taken as the one-flag hardening in the next change; under the current rule revision04 opens on the owner's word.
