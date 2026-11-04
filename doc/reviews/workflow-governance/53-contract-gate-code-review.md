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
