# REVIEW — ticket 51 Evidence gate

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `7928d447a9e44052d8581a9be7c87a1e1cc011e2` on `cp/wave2-51-evidence-gate` (parent `0dd0c78b`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Summary | Every closure cell reproduces; all 25 ticket mutations turn the test file red (the twelve code checks as 22 sub-mutations plus the three extras). One implementation defect is open (S51-01: a receipt red exits 2); two ticket gaps go back to the control plane (S51-02, S51-07). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 88 passed, 1 skipped (symlinks unavailable on this host); mypy --strict on the script clean (2 errors on the test file, not required) |
| Defect codes | PASS | each of the twelve codes exits 1 with the right line; a cell with two defects reports both |
| NF-16 escape shapes | PASS | section without `cell:` → `NOT_RUN`; statement opt-out → `STATEMENT_HAS_RUN_FIELDS`; missing `tool_digest:` label → `CELL_FIELD_MISSING`; missing capture → `CAPTURE_MISSING` exit 1; mixed candidates → `CANDIDATE_MISMATCH`; exit list contradicting the capture → `EXIT_MISMATCH`; empty run → `NO_CELLS` |
| Path confinement | PASS | absolute, `..`, drive, UNC, `.`, trailing slash, sibling directory, `NUL` and an outward junction → `CAPTURE_MISSING`, never read |
| Faults and usage | PASS, gap S51-01 | unknown candidate, tool absent at the candidate, receipt a directory or missing, `--repo` not a repository, evidence root missing → 2; bad arguments → 3; four receipt reds exit 2 (S51-01) |
| Reverse mutations | PASS, survivors noted | 22 sub-mutations plus the three extras red; of the reviewer's 20 doors, 6 survive (S51-01, S51-05, S51-06; two harmless overlaps) |
| E1 / E2 | PASS | the gate on its own receipt `cells=6 defects=0`; on the ticket 48 c10 receipt `cells=7 defects=0`; both byte-identical to the captures |
| Counter-mutations of a good receipt | PASS | CR, dropped LF, edited character, wrong digest, removed field, duplicate cell, statement with a capture, missing required cell, deleted capture, mixed candidate, edited exit list each give the right code; a CRLF copy of the receipt passes |
| Receipt | PASS | LF, blocks byte-identical, exit lists match, digests equal `git show 7928d447:…`; the ticket 48 checker reports only its hard-coded three-script list, as expected |
| Boundary | PASS | README, script and test file only; one commit; repository identity; stdlib only; no `Any`, no `type: ignore`; no target-project or vendor name |
| F1 | PASS | 8 failed, all base names; zero new red |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S51-01 | `IMPLEMENTATION_DEFECT` (defect-class row 5; R4-2) | Low | `evidence_gate.py:256-258`, `:245-247`, `:407-408` | A digest line naming a path git refuses (`../outside`, a drive path, an absolute path, pathspec magic) is a receipt red but exits 2. Check the path's form first → `TOOL_DIGEST_STALE`, then query with a literal root-relative path; one test per side. | probes R7, R8, R9, R17 → 2; the "ls-tree failure as absent" mutation survives |
| S51-02 | `TICKET_DEFECT` | Low | `evidence_gate.py:317-319`, `:295` | A run cell with a second, contradicting `candidate:`, `exit:`, `capture:` or `cell:` line, or a second fence, passes; the ticket names each field once but does not say what a repeat means. | probes R1–R4, R14 → 0 |
| S51-03 | `OUT_OF_SCOPE_HARDENING` | Low | `evidence_gate.py:386`, `:500-512` | The heading name and the `cell:` value are never compared. | probes R5, R6 |
| S51-04 | `OUT_OF_SCOPE_HARDENING` | Low | `evidence_gate.py:256` | `git ls-tree` paths are relative to the current directory, `git show` paths to the repository root: with `--repo` a subdirectory, a correct extra path reads as absent. | probes R12, R13 |
| S51-05 | `EVIDENCE_DEFECT` | Low | `evidence_gate.py:362`; no test | That an exit is a whole `exit=N` line is not pinned (`search` instead of `fullmatch` survives). | mutation survives |
| S51-06 | `OUT_OF_SCOPE_HARDENING` | Low | tests; `evidence_gate.py:270`, `:343-344` | The symlink-escape test skips here, so realpath confinement is unpinned (a junction needs no privilege); receipt BOM stripping has no test. Behaviour correct. | mutations survive; junction probe red |
| S51-07 | `TICKET_DEFECT` | Info | ticket TDD 4; R4-7 receipt cell | TDD 4 says seven NF-16 shapes and lists six; the ticket refines R4-7 (a missing field is `CELL_FIELD_MISSING` rather than `NOT_RUN`; capture relative to the evidence root rather than the repository) without saying so. | read |
| S51-08 | `OUT_OF_SCOPE_HARDENING` | Info | test file | `mypy --strict` on the test file finds 2 errors; only the script is required. | mypy exit 1 |
| S51-09 | `OUT_OF_SCOPE_HARDENING` (accepted decisions) | Info | various | case variants follow the file system; empty `capture:`/`exit:` → `CELL_FIELD_MISSING`; tool absent at the candidate → 2; short or upper-case `--candidate` → 3; malformed digest line → `TOOL_DIGEST_STALE`; lower-case `cell: statement` is a run cell; an unclosed fence stays red; duplicate arguments collapse. | probes |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–2 | ticket tests; mypy on the script / the test file | 0; 0 / 1 |
| 3–4 | 90 probe runs on scratch fixtures; BOM, unclosed fence, inline label; junction probe | per row; 1 |
| 5–6 | E1 and E2 with `cmp` against the captures | 0, identical |
| 7–9 | the ticket 48 checker; the reviewer's independent verifier; 15 receipt counter-mutations | 1 (three-script list only); 0; as expected |
| 10 | 45 mutations on a disposable copy | 39 red, 6 survivors |
| 11–13 | boundary and identity greps; full suite after a quiet-host check; porcelain | 0; 1 (8 base); empty |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the symlink branch (skipped; checked with a junction); case-sensitive file systems and Linux; a real permission-denied capture and a real missing git (mocks only); submodule entries in digest lines.

```review-verdict
candidate: 7928d447a9e44052d8581a9be7c87a1e1cc011e2
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/51-rev01-initial
reviewed_at: 2026-11-04
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `4bcc2873a19ead243945d17c8392cfe2a6dbad18` on `cp/wave2-51-evidence-gate` (one additive commit on `7928d447`) |
| Closure | ticket 51 closure revision02 (`fc83b087`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review CodeReview §5 allows |
| Summary | Every revision02 cell reproduces and the seat's nine mutations are red. S51-01 is only partly closed: digest paths that pass the form check still reach `git show` and exit 2 (S51-10). Nine of 22 counter-mutations survive, four of them changing the exit code (S51-11 to S51-13). An implementation defect remains after the correction, so the ticket goes back to the control plane. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / T1 | PASS | 123 passed, 1 skipped (symlink; the junction test ran), 54 subtests; mypy --strict clean on the script |
| FIELD_REPEATED | PASS | one defect per repeated field, in field order |
| CELL_NAME_MISMATCH | PASS, gap S51-12 | |
| Digest-path form → TOOL_DIGEST_STALE | PARTIAL | absolute, drive, `..`, leading `:`, empty, blank, NUL → 1; backslash, `//`, `/./`, `.`, a gitlink, a 33000-character path → 2 (S51-10) |
| Root-relative reads, subdirectory `--repo` | PASS | |
| Whole `exit=N` lines; junction escape; BOM and CRLF | PASS | |
| Text values | PASS for behaviour, gap S51-11 | every defect one line |
| R4-2: no red exits 2 | FAIL | S51-10 |
| R4-2: no fault exits 1 | PASS, gap S51-13 | |
| Seat's nine mutations | PASS | 9 of 9 red |
| Reviewer counter-mutations | FAIL | 22 run, 13 red, 9 survive |
| Changed existing assertions; seat's choices | PASS; AGREE | |
| Receipt | PASS, gap S51-14 | LF; blocks byte-identical; exit lists equal; digest recomputed; E2 missing |
| E2 (reviewer rerun) | observation | `cells=7 defects=0`, as in revision01 |
| Boundary | PASS | |
| Full suite | PASS | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S51-01 | PARTIALLY CLOSED (S51-10) |
| S51-02, S51-04, S51-05, S51-06, S51-07 | CLOSED |
| S51-03 | CLOSED in behaviour (S51-12) |
| S51-08 | not taken, as planned |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S51-10 | IMPLEMENTATION_DEFECT (R4-2; remainder of S51-01) | Medium | `evidence_gate.py:286-296`, `:277-281`, `:435-450` | existence is checked with `git ls-tree`, whose pathspec normalises `\`, `//`, `./` and `.` and lists gitlinks; the digest is read with `git show`, a literal lookup that refuses those paths, so a receipt red exits 2; a correct receipt plus one `tools\x.py` line exits 2 | nine probes → exit 2 |
| S51-11 | EVIDENCE_DEFECT | Low | tests `:718`, `:725`; `evidence_gate.py:97`, `:439` | the digest-path control check, DEL and the U+001F boundary are unpinned | C01, C02, C03 survive and change the exit |
| S51-12 | EVIDENCE_DEFECT | Low | tests `:559`; `evidence_gate.py:574` | case-insensitive names and a mismatch skipping the other checks survive | C04, C08 |
| S51-13 | EVIDENCE_DEFECT (R4-2 fault side) | Low | `evidence_gate.py:291-292` | an `ls-tree` failure reported as absent survives, turning a fault into a red | C09 |
| S51-14 | EVIDENCE_DEFECT | Info | the seat's receipt | E2 missing without a statement | reviewer rerun unchanged |
| S51-15 | OUT_OF_SCOPE_HARDENING | Info | `evidence_gate.py:60, 355, 380` | parser leniencies (indented or capitalised second field line, label trailing text, C1 controls in names, `::$DATA`); none an unflagged contradiction of a run field | probes |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: Linux and case-sensitive file systems; a real missing git; the symlink branch (a junction was used); submodules with a working tree.

```review-verdict
candidate: 4bcc2873a19ead243945d17c8392cfe2a6dbad18
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/51-rev02-correction
reviewed_at: 2026-11-04
```
