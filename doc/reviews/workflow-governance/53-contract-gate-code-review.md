# REVIEW — ticket 53 Contract gate

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `5ea02c134cfcfa7cde48593db98064aa872dee3c` on `cp/wave2-53-contract-gate` (`fd456159` feature, `5ea02c13` tests-only, on `c0ab4a08`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket |
| Summary | Blocking: on two valid specs the gate exits 2 after it has found a contract red (S53-01), against R4-2 and defect class 5. Two ticket defects (S53-05, S53-06) go to the control plane. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 71 passed, 1 skipped (no symlinks on this host); mypy --strict clean |
| Six R4-7 codes | PASS | each one line, exit 1; a correct fixture exits 0 |
| Literal-expected rule | PASS except S53-01, S53-07 | numbers, strings, bytes, constant displays, `in (1, 2)` red; `None`, `True`, `False`, ledger lookups, `...` not; a spec that does not parse is red |
| Declaration parsing | PASS | first comment block only; CRLF, CR, BOM; `./` and backslashes; `..`, UNC, ADS, trailing dot → SOURCE_MISSING; URL → exit 2 SOURCE_UNSERVABLE |
| Snapshot not R4-7 → 3; faults → 2 | PASS | |
| Red never exits 2 | FAIL | S53-01 |
| One line per defect | PARTIAL | lone surrogates escaped; a newline in a subject forges a line (S53-02) |
| STATEMENT choices | mixed | unknown key → LITERAL_EXPECTED: ticket defect (S53-05); no source → SOURCE_MISSING: agree; working tree only: agree with the ticket text, basis undefined (S53-06); `--specs` outside the repo → 3: agree; summary on stderr at exit 1: agree |
| Two commits | ACCEPTED | the script is byte-identical in both; the second touches only the test file; additive commits are what CodeReview §5 asks for |
| Reverse mutations | PASS | six codes and three extras red; 23 of 28 reviewer counter-mutations red, 3 survivors are findings (S53-02, S53-03), 2 overlap-masked |
| Receipt | PASS | checker 0 defects; four digests recomputed; LF |
| Boundary / identity / stdlib / typing / names | PASS | |
| README | PARTIAL | S53-04 |
| Full suite | PASS | 8 failed, all base names |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S53-01 | IMPLEMENTATION_DEFECT | Medium (blocking) | `contract_gate.py:305-312`, `:330`, `:462-464` | An assert with 900 or 1500 `not` before `x == 3` gives `TOOL_FAULT unexpected RecursionError`; `assert x == 0x` plus 4000 hex digits gives `TOOL_FAULT unexpected ValueError` while rendering the detail. Both sources compile; both are reds reported as faults. | probes; `compile()` check |
| S53-02 | IMPLEMENTATION_DEFECT | Low | `contract_gate.py:86-88`, `:406` | Only `detail` is sanitised: a snapshot id with `\n`, `\r`, U+2028 or NEL forges a second defect line; removing the detail sanitising leaves the tests green. | probes; counter-mutation green |
| S53-03 | EVIDENCE_DEFECT | Low | tests | no test with a correct first source and a bad later one (first-match shape); no test for case-sensitive spec names; behaviour correct | counter-mutations green; probes |
| S53-04 | IMPLEMENTATION_DEFECT | Low | `scripts/README.md:3`, `:7-8` | the introduction still says three scripts and omits `contract_gate.py` from the unexpected-error rule | read |
| S53-05 | TICKET_DEFECT | Medium (non-blocking for this candidate) | ticket 53 defect codes, defect-class rows 2 and 4 | left open: the code for an unknown key; which comment lines are declarations (`# SPDX-License-Identifier:` and `# Note:` are reds today); the code for an empty `requirement:`; a requirement with no source; stripping of snapshot ids; ids outside the ticket 52 character set; the stream of the summary line | probes |
| S53-06 | TICKET_DEFECT | Low (non-blocking) | ticket 53 source rows, exit-2 clause | the digest is over working-tree bytes without line-ending normalisation, while R4-7 cells use blobs at the candidate and R4-1 has any host resume from the files: on a target with `core.autocrlf=true` the same commit can be green on one host and red on another; the exit-2 clause names git, which the gate never reads | autocrlf false here; working bytes = blob |
| S53-07 | OUT_OF_SCOPE_HARDENING | Low | `contract_gate.py:286-312` | literal comparisons that pass: `(x == 3) is True`, `bool(x == 3)`, `all(v == 1 for v in xs)`, `x == --3`, `x == f'abc'`, `x == 1 + 2` | probes |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–4 | worktree identity and diff; process check; ticket tests; mypy | 0 |
| 5–7 | 88 probe runs; compile check; autocrlf and blob comparison | 0 |
| 8–10 | per-commit blob digests and diff; 37 mutations on a disposable copy; multi-source probe | 0 |
| 11–13 | receipt checker; four digests and CR count; boundary greps and README diff | 0 |
| 14–16 | quiet-host wait; full suite; porcelain | 0; 1 (8 base); empty |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a real symbolic-link escape; an unreadable file under a real ACL; POSIX behaviour; a junction under `--specs`; dispatch lint over the dispatch file.

```review-verdict
candidate: 5ea02c134cfcfa7cde48593db98064aa872dee3c
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/53-rev01-initial
reviewed_at: 2026-11-04
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | `09af7a1f4fbd82fa4a619e6f0d3ab4d6e636d950` on `cp/wave2-53-contract-gate` (`09af7a1f` correction 1 → `5ea02c13` → `fd456159`, on `c0ab4a08`) |
| Closure | revision02 |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the one correction review CodeReview §5 allows |
| Summary | The six revision01 doors are closed, but the S53-01 family stays open: a spec with a PEP 263 coding declaration (S53-08) and an over-long source path (S53-09) still turn a red into exit 2. The text-value rule is not applied to declaration values (S53-10); a README test fails once a ninth script exists (S53-11); three counter-mutations survive (S53-12). Implementation and evidence defects remain after the correction, so the ticket goes to convergence. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 102 passed, 149 subtests; mypy --strict clean |
| Six R4-7 codes; declaration keys; blobs at HEAD; untracked source; git failure → 2; empty values; snapshot ids; output streams | PASS | including autocrlf with a CRLF working copy |
| Unanalysable assert → LITERAL_EXPECTED | PARTIAL | deep nesting, huge literals, long chains → 1; a PEP 263 spec → 2 (S53-08) |
| R4-2 | FAIL | S53-08, S53-09 |
| Text values; one line per subject | PARTIAL | every subject escaped; declaration values not checked (S53-10) |
| S53-07 not taken | PASS | no regression |
| Reverse mutations | FAIL | seat's 17 red; reviewer's 40: 31 red, 4 equivalent, 5 findings (S53-12, S53-14) |
| Receipt / boundary / payload | PASS | checker 0 defects; four digests recomputed; LF |
| Full suite | NOT RUN by the reviewer | host never quiet for 30 minutes; the seat's F1 shows 8 base failures |

### Prior findings

| ID | Status |
| --- | --- |
| S53-01 | CLOSED for the reported doors; the family stays open through S53-08, S53-09 |
| S53-02, S53-03 | CLOSED |
| S53-04 | CLOSED for the current tree (S53-11) |
| S53-05 | CLOSED except the text rule on declaration values (S53-10) |
| S53-06 | CLOSED as written; `--repo` identity undefined (S53-13) |
| S53-07 | not taken; no regression |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S53-08 | IMPLEMENTATION_DEFECT | Medium (blocking) | `contract_gate.py:369-375, 386, 400, 532-534` | `ast.parse` honours a PEP 263 coding declaration but the detail text is decoded as UTF-8 with replacement; the segment is cut at offsets of the other decoding and raises `UnicodeDecodeError` outside the analysis guard: a latin-1 or cp950 spec with a non-ASCII literal exits 2 | probes A11–A13 |
| S53-09 | IMPLEMENTATION_DEFECT | Low (blocking) | `contract_gate.py:254-281, 296-297, 306` | a declared source path has no length bound and goes to git on the command line; 40000 characters give `WinError 206`, exit 2 | probes E1–E4 |
| S53-10 | IMPLEMENTATION_DEFECT | Low (blocking) | `contract_gate.py:214-232, 422` | declaration values are not checked against the text-value rule; `strip()` removes control characters and NEL, so `R-1` followed by U+001C binds `R-1` | probes B1–B5, B25 |
| S53-11 | IMPLEMENTATION_DEFECT | Low | tests `:1043-1059` | the README count test knows number words only up to eight; with the wave-2 scripts the directory holds nine | disposable copy: `None != 9` |
| S53-12 | EVIDENCE_DEFECT | Low | `contract_gate.py:287, 381, 313-314`; tests | unpinned: literal pathspecs, the parser exception set, an unreadable `ls-tree` entry read as untracked | R09, R26, R37 survive |
| S53-13 | TICKET_DEFECT | Low (non-blocking for this candidate) | ticket 53 source bytes, defect table, row 4 | `--repo` identity undefined (subdirectory, plain directory, inherited `GIT_DIR`); `SOURCE_MISSING` still says working tree; row 4 says stripped and never stripped | probes C8, C9, G2 |
| S53-14 | OUT_OF_SCOPE_HARDENING | Low | `contract_gate.py:170, 412, 527-533` | a repeated snapshot key is read last-wins; a junction under `--specs` is walked; fault and usage escaping unpinned | probes D10, D11, H1; R19, R20 survive |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: the full suite on this candidate; POSIX behaviour; a hanging git; an unreadable file under a real ACL.

```review-verdict
candidate: 09af7a1f4fbd82fa4a619e6f0d3ab4d6e636d950
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/53-rev02-correction
reviewed_at: 2026-11-04
```

## Revision03 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `4252fda6fce6dd6facc9d180e423f94cae224b52` (`4252fda6` implementation 3 → `09af7a1f` → `5ea02c13` → `fd456159`, on `c0ab4a08`) |
| Closure | revision03 with the git-environment disposition correction |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the initial review of revision03 |
| Summary | The revision03 design holds: every failure derived from a spec's bytes is a red, source paths are canonical and looked up literally through standard input, replace refs, grafts, scrubbed variables and lazy fetch cannot change the blob read, S53-08 to S53-14 are closed, the seat's 39 mutants are red without `-x`. No implementation defect. Blocking evidence: six counter-mutations survive (S53-20) and the receipt lacks two required removal mutants (S53-19). Ticket defects: an unservable blob reported as a red (S53-15), a tracked symlink source that lets cited content drift (S53-16, safety), one fault hiding every red (S53-17), two wording conflicts (S53-18). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 160 passed, 1 skipped (no file-symlink privilege), 458 subtests; mypy --strict clean |
| Per-spec guard | PASS | 23 hostile specs (encodings, PEP 263, deep nesting, huge literals, parser and analyser exceptions) all exit 1 |
| Source paths and literal lookup | PASS | 31 path shapes resolve only to themselves or are refused before any lookup |
| Git environment | PASS | replaced commits, configuration that turns replace refs back on, grafts, scrubbed variables, a planted `git.exe` |
| `--repo` top level; snapshot; links | PASS | junction not walked; file symlinks untested on this host |
| R4-2 and one line | PASS for single-cause runs | combined red and fault: S53-17 |
| Seat choices | judged | symlink as link text opens S53-16; dot segments agreed; `-x` acceptable after a full rerun; mid-work rule accepted |
| Reverse mutations | FAIL | seat 39 of 39 red; reviewer 52: 44 red, 2 equivalent, 6 findings (S53-20) |
| Receipt | PARTIAL | checker 0 defects; digests recomputed; LF; two removal mutants missing (S53-19) |
| Boundary | PASS | three files; Johnny Liu; trailer names the working model |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S53-01 to S53-06, S53-08, S53-09, S53-11 to S53-14 | CLOSED |
| S53-07 | not taken; no regression |
| S53-10 | CLOSED for values; key pattern and separator unpinned (S53-20) |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S53-15 | TICKET_DEFECT | Medium (changes an exit code; fails closed) | ticket "Source bytes"; `contract_gate.py:376-377, 441-442` | an object HEAD names but the store cannot serve answers `missing` and is reported as `SOURCE_MISSING`, a fault reported as a red; with `GIT_NO_LAZY_FETCH=1` every non-local blob of a blobless clone does this | probes: pruned blob, blobless clone |
| S53-16 | TICKET_DEFECT | Medium (safety: a contract stays green while its cited content changes) | ticket "Source bytes"; `contract_gate.py:448-455`; test `:963` | a tracked symlink source is digested as its link text; after the target changes and is committed the gate still exits 0 | probes H1, H2 |
| S53-17 | TICKET_DEFECT | Medium (changes an exit code; hides reds, never passes) | `contract_gate.py:601, 607-609, 714-716`; test `:642` | one fault (a URL source, an unreadable spec, a git fault) drops every red and exits 2 | probes E1 to E4 |
| S53-18 | TICKET_DEFECT | Low (wording) | ticket TDD 4 and "Declaration values"; tests `:1532, :1822` | TDD 4 says a TAB around a value is a red while "Declaration values" removes it; TDD 4 says usage prints one line while the candidate prints a banner and one line | probes |
| S53-19 | EVIDENCE_DEFECT | Low (evidence gap only) | receipt M1 | removal mutants for `SOURCE_MISSING` and `RETIRED_REQUIREMENT_BOUND` missing; the tests pin them | reviewer R23 to R26 red |
| S53-20 | EVIDENCE_DEFECT | Low (R51 safety-adjacent; others evidence) | `contract_gate.py:81, 83, 441, 453, 464, 497` | unpinned: chained comparisons beyond the first comparator; Unicode whitespace as the path-digest separator and in the key pattern; the `--batch` size check; `missing` as an exact answer; `-True` as a signed number | R51, R09, R10, R15, R16, R21 green |
| S53-21 | OUT_OF_SCOPE_HARDENING | Low | `contract_gate.py:426-455` | HEAD is resolved again per lookup in two processes per source, so a commit landing mid-run can mix trees | read |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a real file symlink under `--specs`; POSIX behaviour; a hanging git; HEAD moving mid-run.

```review-verdict
candidate: 4252fda6fce6dd6facc9d180e423f94cae224b52
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/53-rev03-initial
reviewed_at: 2026-11-04
```

## Revision04 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `ebbb4947cc6586c412c61cd57158289389ebc391` (`ebbb4947` correction 1 → `4252fda6` → `09af7a1f` → `5ea02c13` → `fd456159`) |
| Reviewer | independent `ticket-review` seat in its own detached worktree; authored nothing in this ticket; the initial review of revision04 |
| Summary | The revision04 design holds: one commit per run even when HEAD moves, link and gitlink sources at any depth are `SOURCE_MISSING`, absent and unservable are told apart (pruned blob, tree and root tree, blobless and treeless clones, a corrupt loose object), red before fault holds in every combination tried. No implementation defect. Blocking evidence: 9 counter-mutations survive (S53-22 to S53-26), two of them safety-adjacent. For the control plane: precondition faults end the run before reds are looked for (S53-27, wording) and a forged loose object passes (S53-28). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Ticket tests / mypy | PASS | 212 passed, 1 skipped, 571 subtests; mypy --strict clean |
| One commit per run; link and gitlink sources; absent vs unservable; red before fault; wording | PASS | real-git probes; S53-22 and S53-27 noted |
| Regression (guard, decoding, canonical paths, git environment, `--repo`, snapshot, declaration values, links) | PASS | 18 hostile specs, 22 path shapes, a SHA-256 repository probe |
| R4-2 / one line | PASS | |
| Seat choices | AGREE | tree walk by object id; unservable vs fault; withheld `NO_SPEC_FOR_REQUIREMENT`; URL-only source; remapped R15, R16; E6 equivalent |
| Reverse mutations | FAIL | seat 58 red, E6 equivalent; reviewer 30: 20 red, K18 equivalent, 9 survivors |
| Receipt / boundary | PASS | checker 0 defects; digests recomputed; LF; three files; trailer names the working model |
| Full suite | PASS under the host lock | 8 failed, all base names |

### Prior findings

| ID | Status |
| --- | --- |
| S53-01 to S53-21 | CLOSED (S53-16 gitlink-in-the-middle unpinned: S53-22; S53-17 preconditions: S53-27); S53-07 not taken |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| S53-22 | EVIDENCE_DEFECT | Low, safety-adjacent | `contract_gate.py:689` | no test has a gitlink in the middle of a source path; descending into it stays green | K1 green |
| S53-23 | EVIDENCE_DEFECT | Low, safety-adjacent | `contract_gate.py:891` | no test declares a digest equal except late characters; an 8-character compare stays green | K18b green |
| S53-24 | EVIDENCE_DEFECT | Low (exit code in mutants) | `contract_gate.py:103, 642` | no SHA-256 repository is tested | K6, K7 green |
| S53-25 | EVIDENCE_DEFECT | Low (exit code in mutants) | `contract_gate.py:364, 954` | URL schemes other than http(s) and the withholding of `NO_SPEC_FOR_REQUIREMENT` after an unexpected error are unpinned | K34, K10 green |
| S53-26 | EVIDENCE_DEFECT | Low (evidence only) | `contract_gate.py:654-660, 673` | the batch-reader tree side is unpinned: store marked broken, answered subtree id, answered kind | K5, K65, K67 green |
| S53-27 | TICKET_DEFECT | Low, non-blocking (fails closed) | ticket "Red before fault"; `contract_gate.py:919-928` | an unreadable snapshot, `--repo` not the top level or `--specs` not a directory ends the run at once; the ticket does not name the precondition faults | read |
| S53-28 | OUT_OF_SCOPE_HARDENING | Medium, safety (a seat that can write the shared store) | `contract_gate.py:700-709, 649-660` | the gate does not hash the objects it reads; an overwritten loose blob passes with the forged digest | probe |
| S53-29 | OUT_OF_SCOPE_HARDENING | Info | `contract_gate.py:414-416, 437` | with no commit the fault detail is empty | probe |

Raw logs: retained in the review seat's scratch directory under `.worktrees/`; not committed.

Not verified: a real file symlink under `--specs`; POSIX behaviour; a hanging git; an unreadable file under a real ACL.

```review-verdict
candidate: ebbb4947cc6586c412c61cd57158289389ebc391
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/53-rev04-initial
reviewed_at: 2026-11-05
```
