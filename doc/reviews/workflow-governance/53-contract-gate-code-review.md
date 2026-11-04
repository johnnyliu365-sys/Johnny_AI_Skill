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
