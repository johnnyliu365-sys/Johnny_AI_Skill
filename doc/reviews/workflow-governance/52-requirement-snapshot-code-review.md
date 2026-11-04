# REVIEW — ticket 52 Requirement snapshot CLI

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `dbd743588da810592eeba824b4d566f2ec88849a` on `cp/wave2-52-requirement-snapshot` (parent `0dd0c78b`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Summary | Most of the candidate works and is well tested. Two blocking defects: a lone-surrogate string, a red of the input, exits 2 (S52-01); two concurrent `take` runs on one source with different dates both publish the same version (S52-03, 13 of 40 real two-process trials). Three smaller defects fit the same correction (S52-02, S52-04, S52-05); S52-06 is hardening; S52-07 is a ticket gap for the control plane. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | `64 passed, 128 subtests`; mypy --strict on the script clean (the test file has 3 strict errors, outside the ticket gate) |
| take v1 / v2 / unchanged; verify; diff | PASS | reordered keys and rows through a CRLF input print `unchanged` and leave the tree byte-identical; verify `OK rows=2`; diff `added / removed / changed` |
| Canonical digest; `taken_at` outside it | PASS | independent recomputation equals the stored digest; independent of key order, row order and line endings |
| Every defect code (exit 1, no write) | PASS | all eight codes, tree unchanged |
| Defect classes 1, 2, 4 | PASS | path names (traversal, separators, drive, trailing dot, case collision, Windows reserved names) NAME_INVALID; null and empty values ROW_FIELD_TYPE; digest formats DIGEST_FORMAT |
| Defect class 5 | PARTIAL | an id with an embedded newline breaks the one-line shape (S52-02) |
| Defect class 6 | PARTIAL | a write failure mid-file leaves no partial file, exit 2; a lone surrogate (a red) also exits 2 (S52-01) |
| Exclusive create / no overwrite | PARTIAL | same-date races never produce two v2 files; different-date races do (S52-03) |
| Seat choices the ticket left open | AGREE except the concurrent-writer claim | unexpected row field, blank id, non-UTC `taken_at` in a file → 1; damaged latest version → 1; non-UTC `--taken-at` → 3; missing or duplicated versions in diff → 2; Windows reserved names NAME_INVALID; "a concurrent writer exits 2" holds only for the same date (S52-03) |
| Reverse mutations | PASS | the eight code checks and the four ticket extras red; 28 of 29 reviewer counter-mutations red; next version by count + 1 survives (S52-04) |
| Receipt | PASS | the ticket 48 checker exit 0; the fourth digest verified; no CR; exit lists match |
| Boundary | PASS | README, script and test file only; repository identity; stdlib only; no `Any`; no target-project or vendor name |
| README | FAIL (Low) | S52-05 |
| F1 | PASS | 8 failed, all base names; zero new red |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S52-01 | IMPLEMENTATION_DEFECT | Medium (blocking) | `requirement_snapshot.py:153-157`, reached from :488 and :360 | A row string holding a lone surrogate escape is valid JSON but cannot be encoded as UTF-8; `take` and `verify` exit 2 with `tool fault: UnicodeEncodeError`: a red of the input reported as a tool fault, against R4-2. (Accepted as a fault: input nested 100000 deep, a parser limit.) | probes: lone surrogate in a title, exit 2; verify of a file holding one, exit 2 |
| S52-02 | IMPLEMENTATION_DEFECT | Low | `requirement_snapshot.py:100-101`, :548-554, :235 | An id with an embedded newline is accepted and printed raw, so one defect prints as two lines and diff prints a forged line. | probes |
| S52-03 | IMPLEMENTATION_DEFECT | Medium (blocking) | `requirement_snapshot.py:503-512`, :424-441 | Exclusive create guards the dated file name, not the version number: two writers with different dates both publish `-v2`, each exit 0, and every later `take` exits 2 until a file is deleted. | injected interleaving; real two-process runs 13/40 |
| S52-04 | EVIDENCE_DEFECT | Low | tests (no version-gap case) | Computing the next version as count + 1 leaves all tests green; the code is correct (v1 and v3 present → v4). | mutation; gap probe |
| S52-05 | IMPLEMENTATION_DEFECT | Low | `scripts/README.md:120-123`; `requirement_snapshot.py:29` | The README's NAME_INVALID list omits the reserved device names; it says SNAPSHOT_DIGEST_MISMATCH appears only for verify and a damaged latest version while `diff` reports it for any damaged version; the docstring says "verify only". | probes |
| S52-06 | OUT_OF_SCOPE_HARDENING | Low | `requirement_snapshot.py:535-541` | `diff --source S` skips the case-collision rule that `take` applies. | probe |
| S52-07 | TICKET_DEFECT | Low (non-blocking for this candidate) | ticket 52 defect codes and file format | The ticket leaves open: how take and diff treat a damaged stored version; the code for a blank id and unexpected fields; whether `../../..`, `~/x` or `""` are repository-relative `source_ref`; the allowed characters of `requirement_id`; version uniqueness under exclusive create. | probes |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | worktree identity, status, log, `git diff --name-only 0dd0c78b..HEAD` | 0 |
| 2 | process check before each pytest | 0 |
| 3–5 | CLI probes; race probes (injected and two-process) | 0 |
| 6–8 | ticket tests; mypy on the script; mypy on the test file (informational) | 0; 0; 1 |
| 9 | 42 mutations on a disposable mirror, each restored and sha-checked | 0 |
| 10–12 | the ticket 48 receipt checker; fourth digest; CR and exit-list comparison | 0 |
| 13 | gap probe | 0 |
| 14–15 | full suite in the review worktree; cache cleanup and porcelain | 1 (8 base); 0 |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the POSIX publish branch (host is Windows only); a truly unwritable root through ACLs; behaviour on a case-sensitive file system; per-subtest failure names for every counter-mutation.

```review-verdict
candidate: dbd743588da810592eeba824b4d566f2ec88849a
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/52-rev01-initial
reviewed_at: 2026-11-04
```

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `3c485efc65ba861a2dc6a716897e3c055d7397b1` (`3c485efc` README fix → `21ac4fda` correction → `dbd74358`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree |
| Summary | Every closure cell behaves correctly. Two reviewer counter-mutations turned nothing red (S52-10) and the docstring disagrees with the README and the code on what `verify` checks (S52-11); neither fix changes behaviour. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 93 passed, 238 subtests; mypy --strict clean |
| take / verify / diff; every code; text values; id character set; source_ref; damaged versions; diff case collision; exit codes | PASS | as specified in revision02 |
| Version uniqueness | PASS | 60 real two-process races with different dates: no duplicate, loser exits 2 naming the claim, nothing left behind; injected interleavings and stale claims as specified |
| Seat design choices | AGREE | any claim blocks take; text-rule violation reported alongside a format code; `file:` stays SOURCE_REF_ABSOLUTE |
| Changed assertion and 29 new tests | PASS | |
| Reverse mutations | PARTIAL | 10 of 10 receipt mutations red; 27 of 30 reviewer counter-mutations red; C24 and C25 green (S52-10); C07 green but caught by the narrower id rule |
| Receipt / boundary / identity / payload / F1 | PASS | checker 0 defects; fourth digest recomputed; 8 base failures only |

### Prior findings

| ID | Status |
| --- | --- |
| S52-01, S52-02, S52-03, S52-04, S52-06, S52-07 | CLOSED |
| S52-05 | PARTIALLY CLOSED (S52-11) |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S52-10 | EVIDENCE_DEFECT | Low (blocking: a zero-red counter-mutation is a finding) | `requirement_snapshot.py:304`, `:220`; tests | One-line output is not tested where a raw value is echoed in a detail: dropping `!r` from the SOURCE_REF_ABSOLUTE or NAME_INVALID detail leaves every test green. The code is correct. | C24, C25 green |
| S52-11 | IMPLEMENTATION_DEFECT | Low | `requirement_snapshot.py:47-49` vs README `:147-148` and `run_verify` | The docstring says the case-variant rule is applied by take, verify and diff alike; README and code apply only the name rules in verify. | probe |
| S52-12 | TICKET_DEFECT | Low (non-blocking for this candidate) | ticket 52 NAME_INVALID | The ticket applies the case-variant rule to verify, which has no root, and does not say whether verify checks the file's `source` against its directory. | probe |
| S52-13 | OUT_OF_SCOPE_HARDENING | Low | `requirement_snapshot.py:406-418` | a top-level `source` or `source_sha256` breaking the text rule gets only NAME_INVALID or DIGEST_FORMAT, not also ROW_FIELD_TYPE | probe |
| S52-14 | OUT_OF_SCOPE_HARDENING | Low | `requirement_snapshot.py:82-83, 86` | `\d` without `re.ASCII` matches Unicode digits in version file names | probe |
| S52-15 | OUT_OF_SCOPE_HARDENING | Low | `requirement_snapshot.py:368-374` | a repeated JSON key silently keeps the last value | probe |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the POSIX publish branch; an ACL-unwritable root; a case-sensitive file system; whether the four sequential race outcomes overlapped.

```review-verdict
candidate: 3c485efc65ba861a2dc6a716897e3c055d7397b1
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/52-rev02-initial
reviewed_at: 2026-11-04
```

## Revision03 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `ac95c321f9496ac2d97fabd5fdc1f6c18d928346` (`ac95c321` correction 2 → `3c485efc` → `21ac4fda` → `dbd74358`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Summary | Correction 2 closes S52-10, S52-11, S52-12, S52-13 and S52-15, and the revision02 behaviour holds. S52-14 named three `\d` patterns and only two were converted: the claim-file pattern still matches Unicode digits, and no test covers it (S52-16). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 107 passed, 280 subtests; mypy --strict clean on the script |
| S52-10 echoed details | PASS | every echoed value on one line in take and diff |
| S52-11 / S52-12 verify scope | PASS | code, docstring, README and ticket agree; verify applies the name rules only |
| S52-13 top-level text rule | PASS | NAME_INVALID or DIGEST_FORMAT plus ROW_FIELD_TYPE |
| S52-14 ASCII digits | PARTIAL | file names and arguments ASCII only; the claim pattern still `\d` (S52-16) |
| S52-15 repeated keys | PASS | rows, top level, nested, stored files; one line per key |
| take / verify / diff; codes; damaged versions; source_ref; id set; names | PASS | as specified |
| Version claim under real races | PASS | 60 two-process races: no duplicate, loser exits 2; a claimless mutant duplicated v2 in 20 of 20 |
| R4-2 exit classes | PASS | a red never exits 2 (apart from the accepted parser depth limit); a fault never exits 1; S52-17 |
| Reverse mutations | PARTIAL | seat's 5 red; reviewer's 30: 28 red, C04 and C05 green but equivalent (the values cannot hold a line break); nothing pins the claim-name rule |
| Receipt / boundary / identity / payload | PASS | checker 0 defects; four digests recomputed; LF; additions-only test change |
| Full suite | NOT RUN by the reviewer | host busy for 30 minutes; the seat's F1 shows 8 base failures |

### Prior findings

| ID | Status |
| --- | --- |
| S52-01 to S52-07 | CLOSED (revision02) |
| S52-10, S52-11, S52-12, S52-13, S52-15 | CLOSED |
| S52-14 | PARTIALLY CLOSED (S52-16) |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S52-16 | IMPLEMENTATION_DEFECT | Low (blocking: a closure rule partly applied and untested) | `requirement_snapshot.py:92` | the claim-file pattern uses `\d`, so a claim file named with a non-ASCII digit blocks `take` (exit 2) while the same digit in a version file name is ignored | probe; with `[0-9]` the suite stays green, so nothing pins either form |
| S52-17 | OUT_OF_SCOPE_HARDENING | Low (non-blocking) | `requirement_snapshot.py:725-729` | a version argument longer than 4300 digits gives exit 2 with a raw `ValueError` message | probe |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the full suite in the review worktree; the POSIX publish branch; an ACL-unwritable root; a case-sensitive file system.

```review-verdict
candidate: ac95c321f9496ac2d97fabd5fdc1f6c18d928346
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/52-rev03-initial
reviewed_at: 2026-11-04
```
