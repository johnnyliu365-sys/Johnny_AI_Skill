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

## Revision03 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `bea0cf0c674a49ad1225f0208b879246abe7b84c` (`bea0cf0c` correction 3 → `ac95c321` → `3c485efc` → `21ac4fda` → `dbd74358`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review CodeReview §5 allows for revision03 |
| Summary | Correction 3 closes S52-16 and S52-17 as dispositioned and the revision03 behaviour holds. The S52-17 guard runs before the name rules, so an invalid source name with a 256 to 4300-digit version argument exits 2 where it exited 1 before (S52-18); one counter-mutation turns nothing red (S52-19). The red-or-fault precedence is undefined in the ticket (S52-20). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 109 passed, 287 subtests; mypy --strict clean |
| S52-16 claim names ASCII | PASS | non-ASCII digit claim files no longer block `take`; no Unicode digit class remains |
| S52-17 over-long version argument | PARTIAL | one line, exit 2, no raw exception; the guard precedes the name rules (S52-18); second position untested (S52-19) |
| 255-digit bound | AGREE | a stored name holds at most 239 digits |
| take / verify / diff; codes; text values; ids; source_ref; repeated keys; names | PASS | 103 probe cases, 0 failures |
| Damaged versions | PASS except the combined case | S52-20 |
| Version claim under real races | PASS | 60 races, no duplicate, nothing left behind |
| R4-2 exit classes | PARTIAL | single inputs correct; combined red and fault drop the red (S52-18, S52-20) |
| Reverse mutations | PARTIAL | C6 (order) and C10 (first argument only) green; C9 equivalent |
| Receipt | PASS with S52-23 | checker 0 defects; digests recomputed; LF; no P9 section |
| Boundary / identity | PASS | trailer naming another model is a control-plane issue, not a finding |
| Full suite | PASS under the host lock | 8 failed, all base names; overlapped lock-less runs recorded |

### Prior findings

| ID | Status |
| --- | --- |
| S52-01 to S52-07 | CLOSED (revision02) |
| S52-10 to S52-16 | CLOSED |
| S52-17 | PARTIALLY CLOSED (S52-18, S52-19) |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S52-18 | IMPLEMENTATION_DEFECT | Low (blocking: a regression, untested) | `requirement_snapshot.py:781`, `:736-745`, before `run_diff` `:677-684` | the over-long fault is raised before the name rules, so `diff` with an invalid or case-variant source and a 256 to 4300-digit version exits 2 without `NAME_INVALID` | probes on both candidates; C6 green |
| S52-19 | EVIDENCE_DEFECT | Low (blocking) | tests `:1316` | the over-long argument is tested in the first position only; guarding the first argument alone stays green and prints the raw `ValueError` | C10 green |
| S52-20 | TICKET_DEFECT | Low (non-blocking for this candidate) | ticket 52 exit codes; `requirement_snapshot.py:686-687` | the ticket does not say which exit wins when a run meets a red and a fault; `diff` with v2 damaged and v9 missing exits 2 without `SNAPSHOT_DIGEST_MISMATCH` | probe |
| S52-21 | IMPLEMENTATION_DEFECT | Low (documentation) | `requirement_snapshot.py:53-56` | the docstring omits the claim-name and over-long rules the README states | read |
| S52-22 | OUT_OF_SCOPE_HARDENING | Low | `requirement_snapshot.py:595` | `casefold` makes NTFS-distinct non-ASCII directories collide with an ASCII source | probe |
| S52-23 | EVIDENCE_DEFECT | Low (non-blocking) | the seat's receipt | the P9 cell is absent from the receipt; the side file has CR bytes; the reviewer's checker run gives 0 defects | checker |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the POSIX publish branch; an ACL-unwritable root; a case-sensitive file system; any effect of the overlapping lock-less runs.

```review-verdict
candidate: bea0cf0c674a49ad1225f0208b879246abe7b84c
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/52-rev03-correction
reviewed_at: 2026-11-04
```

## Revision04 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `7649f1b8682c2c18a40485c898ccb54e46f1f231` (`7649f1b8` → `bea0cf0c` → `ac95c321` → `3c485efc` → `21ac4fda` → `dbd74358`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the initial review of revision04 |
| Read against | revision04 and its binding rules; R4-2 with the control plane's red-before-fault reading (awaiting owner confirmation); R4-5; R4-7 |
| Summary | Revision04 closes S52-18, S52-19, S52-21, S52-22, S52-23 and S52-20 as dispositioned; every earlier item still holds. Blocking: JSON nested about 1000 levels deep raises `RecursionError`, which takes the unexpected-error path and drops a red already found (S52-24). Five counter-mutations stay green (S52-25, S52-26, S52-27). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 139 passed, 313 subtests; mypy --strict clean |
| Red before fault: take, diff | PARTIAL | every combined red and fault exits 1 with the fault on stderr, except deep nesting (S52-24) |
| Red before fault: verify | PASS | |
| Check order | PASS | grammar, then names, then lookups |
| Seat choices | AGREE, AGREE, DISAGREE | the third (an unexpected error drops reds) is reachable by input (S52-24) |
| S52-21, S52-22 | PASS | docstring complete; ASCII-only collisions, and NTFS keeps the look-alikes distinct |
| Regression | PASS | 101 of 102 probe cases; the failure is S52-24 |
| Version claim under real races | PASS | 120 races, never a duplicate; a claimless mutant duplicated v2 in 20 of 20 |
| Reverse mutations | seat 18 red; reviewer 22: 17 red, C02, C10, C12, C15, C17 green | |
| Receipt / boundary | PASS | checker 0 defects with P9; digests recomputed; LF; additions-only tests; trailer names the working model |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S52-01 to S52-07, S52-10 to S52-19, S52-21 to S52-23 | CLOSED |
| S52-20 | CLOSED as dispositioned; the rule is still broken through the unexpected-error path (S52-24) |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S52-24 | IMPLEMENTATION_DEFECT | Low (blocking; changes an exit code) | `requirement_snapshot.py:372-376`, `:858-860`; README | a JSON input or stored version nested about 1000 levels deep raises `RecursionError`, which exits 2 at once and drops a red already found; the README says exit 2 only when no red was found | three probe cases |
| S52-25 | EVIDENCE_DEFECT | Low (blocking; evidence gap) | tests; `requirement_snapshot.py:709-712, 813-815` | unpinned: an unreadable present version collected rather than raised; leading zeros in version arguments | C02, C15 green |
| S52-26 | EVIDENCE_DEFECT | Low (blocking; evidence gap) | tests; `requirement_snapshot.py:103, 855-857` | one-line faults tested only for a newline through one path: NEL, U+2028, U+2029 and the top-level fault handler unpinned | C10, C17 green |
| S52-27 | OUT_OF_SCOPE_HARDENING | Low (non-blocking; read confinement) | tests; `requirement_snapshot.py:655` | take not reading under an invalid source name is untested (diff's is tested) | C12 green |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the POSIX publish branch; an ACL-unwritable root; a case-sensitive file system; non-ASCII folding on other file systems.

```review-verdict
candidate: 7649f1b8682c2c18a40485c898ccb54e46f1f231
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/52-rev04-initial
reviewed_at: 2026-11-04
```
