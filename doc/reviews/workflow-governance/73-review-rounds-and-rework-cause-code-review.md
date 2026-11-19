# Ticket 73: initial review of closure revision03

- Candidate: `9ae502de5dbbf7e36b39179bcfbbc0a1d380519e` (branch `cp/wave3-73-rework`, two commits on base `50b4685e027c294fcac638f1d693c03be2bb0fb6`: `06667834`, then `9ae502de`).
- Ticket: `modules/tickets/workflow-governance/73-review-rounds-and-rework-cause.md` revision03, read at the candidate (unchanged from the base). Wording rationale: `doc/reviews/workflow-governance/73-review-rounds-and-rework-cause-ticket-review.md`.
- Dispatch: `doc/handoffs/2026/workflow-governance/dispatch/JAS-73-1.yaml` at `cp/wave3` (`5dc9d41b`), sha256 `bffe4ff1c013ea8b6f80d49ca9cc682fe432c0a9a5b4f3b886f7ac384e4135e6` (recomputed, equal).
- Receipt: `.worktrees/73-rework-out/RETURN.md`; `RETURN.as-returned.md` differs only by the appended `USAGE seat:implementation-standard/JAS73R1` cell (12 lines, with `effort: high`).
- Seat: independent `ticket-review`, run id `R73-1`, worktree `.worktrees/73-rework-review` detached at the candidate (porcelain, ignored files included, empty before and after). Scratch: `.worktrees/73-rework-review-scratch/R73-1` and the clone `R73-1-clone`, both removed after the run.
- References applied: `CodeReview.md` §2 to §5; `review-checks.md` (required dimensions, defect categories, reviewer counter-mutation points 1 to 5). Every pytest and mutation output below was read unfiltered (pytest `-q -rfEs`, written to a file and read in full, with no wrapper).
- Round: initial.

## Findings

| id | §4 class | severity | location | finding | evidence |
| --- | --- | --- | --- | --- | --- |
| S73-01 | TICKET_DEFECT | Medium. Does not block: the candidate does what item 4 states | ticket item 4 (red list); `rework_report.py` `judge`, `judge_block` | Item 2 says each review section ends with a `rework-record` block that directly follows its `review-verdict`. But item 4 has only one red for a missing block, `NO_REWORK_RECORD`, and it fires only when the record has no block at all. So if a reviewer leaves out the block in a later section, the report says exit 0 with too few rounds and a wrong `final`. Two blocks paired to one `review-verdict` also give exit 0, so one review counts twice. Ticket 71's and ticket 73's own reviews are the first records whose blocks reviewers write by hand, so this is the case most likely to happen next. The ticket does not name it, and the seat followed the ticket. | Probe P1: verdict A + block, then verdict B (`APPROVED`) with no block. Result: exit 0, `rounds=1 … final=CHANGES_REQUESTED`. Probe P2: one verdict, two blocks (rounds 1 and 2) give exit 0, `rounds=2`. In the ten real records every `review-verdict` has exactly one block after it: I counted the blocks against the verdicts in each record. Route: control plane. Smallest fix: one more red in this script, for a `review-verdict` block with no non-`RETURN` `rework-record` block, or more than one, before the next `review-verdict` block or the end of the record. Either amend the ticket so this correction carries it, or carry it to the next change of `rework_report.py`. |
| S73-02 | EVIDENCE_DEFECT | Low. Blocks at this initial review (§4: fixed once on the original ticket) | `tests/test_rework_report.py:279-284` (`test_candidate_values_outside_the_grammar_are_a_red`); `rework_report.py:231-232` | Defect row 4 requires a red for a 39- or 41-character candidate. The test checks only exit 1, and every case is a non-`RETURN` block paired with a `review-verdict` whose candidate is `a`×40. So `CANDIDATE_MISMATCH` already turns each case red, whatever the grammar check does. This is the overlap-masking shape. On the `RETURN` path there is no pairing, so nothing pins the grammar there. The candidate itself behaves correctly. | CM5: accepting upper-case hex turns nothing red (61 passed). CM5b: deleting the grammar check outright also turns nothing red (61 passed). Under CM5b, a `RETURN` block with a 39-character candidate gives exit 0 and a ticket line. At the candidate it gives exit 1 `VALUE_INVALID … is not 40 lower-case hex`. Smallest fix: assert the reason in that test (`VALUE_INVALID` and "is not 40 lower-case hex"). Add `RETURN`-block cases `returned(candidate=…)` for `a`×39, `a`×41 and `A`×40. Show CM5b red. |
| S73-03 | OUT_OF_SCOPE_HARDENING | Low. Does not block | `rework_report.py:194-202` (`disposition_approves`) vs `integrate.py:826-835` | Empty causes on a `CONVERGENCE_REVIEW_REQUIRED` round are accepted when any closed `convergence-disposition` for the candidate says `APPROVED`. `integrate.check_review` judges only the last disposition for the candidate, and also requires it to be well-formed. Suppose a record held an `APPROVED` disposition and then a later one that is not approved. The report would accept empty causes, while integration refuses the candidate. This is the first-match shape. The ticket's words ("has an `APPROVED` `convergence-disposition`") permit the reading, and no record has two dispositions. | Probe P3: `APPROVED`, then `CHANGES_REQUESTED`, for one candidate, with empty causes. Result: exit 0. Route: follow-up, at the next change of this script. Judge the last disposition for the candidate, as `integrate.py` does. |

Observations that are not findings (no correction asked):
- **Receipt STATEMENT item 7** says run 44587772912 (`06667834`) "was red on Linux". Both jobs of that run failed (`test (windows)` too), and for the same reason: two `UNREGISTERED_FAILURE` lines from the payload-closure tests in each log. The statement is incomplete, not untrue. The second commit fixes both jobs.
- **The 147-failure full-suite capture** is not available for review. STATEMENT item 6 says the seat kept it. Item 20 then lists `JAS73R1-F1-run2-orphan-lease.txt` among the files removed before return, and `.worktrees/73-rework-scratch/` holds no `JAS73R1` file. The F1 cell is the clean third run, and it does not depend on that capture.
- **Receipt STATEMENT item 18** says "166 inserted lines". `git diff --shortstat 50b4685e 9ae502de -- doc/reviews` gives 160 insertions and no deletions, in the first commit only. The claim that matters, additions only, is true.
- **Review records 74, 75 and 76** have `APPROVED` blocks with empty causes. That is mechanical, whatever their non-blocking findings are.

## Per-check table

| # | check | result | evidence |
| --- | --- | --- | --- |
| 1a | Block grammar (item 2) | PASS | `read_block`/`judge_block` enforce five fields, order, single keys, 40-hex or `none` (in `RETURN` only), no-leading-zero round, the kind and verdict domains, `RETURN`⇒`CHANGE_DETECTED`. `RedTests` covers each. The grammar test is masked; see S73-02. |
| 1b | Pairing (item 2) | PASS (gap S73-01) | Pairs with the nearest `review-verdict` before the block. `NO_REVIEW_VERDICT` and `RETURN_AFTER_VERDICT` are tested. CM2 (pair with the first, not the nearest) turns 6 tests red, including the real-records pin. |
| 1c | Cause mapping (item 3) | PASS | Causes are empty for `APPROVED`. For `CONVERGENCE_REVIEW_REQUIRED` they are empty only with an `APPROVED` disposition for that candidate; otherwise they are not empty. They are not empty for `CHANGES_REQUESTED`, `BLOCKED` and `CHANGE_DETECTED`. All seven disposition cases are tested. CM1 (a disposition for any candidate) is red. |
| 1d | Report lines (item 4) | PASS | Exact per-ticket and TOTAL lines are pinned (`test_the_exact_lines_…`, `test_several_records_…`). A round with two causes counts once under each. `final` is the last verdict as recorded. |
| 1e | Every red of item 4 | PASS | One test per red. 61 passed, 87 subtests (`P1a`). |
| 1f | Exit codes, red before fault | PASS | Undecodable or missing record beside a red: exit 1, fault on stderr. Alone: exit 2. Usage: 3. Unexpected error: 2. My probes agree. Seat M1 #3 is red, and CM4 (a fault with no red exits 1) turns 4 tests red. |
| 1g | `integrate.check_review` unaffected (TDD 1) | PASS | Three tests: with and without the block, a convergence record, and a malformed block. `integrate.py` parses fences with the same regexes and keeps only its two tags. |
| 1h | Regression (TDD 4) | PASS | `tests/test_integrate.py` 207 passed, 1 skipped (Windows mode-bit), exit 0. `tests/test_gate_contract.py` 244 passed, 1 skipped (link), exit 0. Both files are unchanged. |
| 1i | Strict typing (P0) | PASS | `mypy --strict --python-version 3.11` on both files: no issues. No `Any`, no `type: ignore`. Standard library only. |
| 2a | Backfill derived from each record's own findings | PASS | I mapped every finding of the 17 review rounds by its first §4 class, independently. My mapping matches all 19 blocks: 65 `CPR,RU,ID` (S65-05 TICKET, S65-04 receipt claim contradicted, S65-01/02); 66 `CPR,ID`; 67 `ID`; 68 `CPR,ID` (S68-05 cites a true statement, so `ID`); 69 `ID`, then empty (`APPROVED` disposition for `7cc0e08f`); 70 `CPR,ID`, then empty (disposition for `548665e5`); 72 `RU,ID`, then empty (disposition for `8c770265`); 74/75/76 empty. All candidates equal their `review-verdict`. |
| 2b | Hard-to-map findings (STATEMENT item 16) | PASS | S65-04 → `RETURN_UNTRUE` is plain: STATEMENT item 5 said the helper "is also dropped", and it was not. S72-02 → `RETURN_UNTRUE` is a judgement, and I accept it. The STATEMENT stated an unqualified trailing-`; ` convention, which the reviewer's probe contradicts for a quoted value. That is the permitted `RETURN_UNTRUE` test. S66-01, S67-03, S68-05, S69-04, S68-08, S65-05 and S70-05 go by first class, as item 3 says. |
| 2c | Two `RETURN` blocks before the first review section | PASS | 65: lines 3-13, before `## Revision02 initial review` (line 15); base line 213 names the return. 70: lines 3-13, before line 15; base line 237. `candidate: none`, `DESIGN_UNFORESEEN`. |
| 2d | No finding text changed | PASS | `git diff 50b4685e 9ae502de -- doc/reviews`: 10 files, 160 insertions, 0 deletions. Besides the block lines, the only additions are one heading and one sentence before each `RETURN` block (65, 70). |
| 2e | O1 | PASS | My rerun over the ten records: exit 0, stderr empty. Output is byte-equal to the receipt's O1 (`TOTAL tickets=10 rounds=19 CONTROL_PLANE_RULE=4 RETURN_UNTRUE=2 DESIGN_UNFORESEEN=2 IMPLEMENTATION_DETAIL=7`). |
| 3 | Reds and rules added where the ticket is silent | ACCEPTED | `DUPLICATE_TICKET` and `TICKET_ID` follow from item 1 (one ticket per record, id before the first `-`) and from "per ticket, one line". "`RETURN` names only `DESIGN_UNFORESEEN`" follows from item 3's table: a `RETURN` round has no findings, and every `RETURN` block maps to that cause. "A record with a red prints no ticket line and is left out of TOTAL" keeps a partial count out of the totals. It does not change the exit code, and the README states it. "Any unclosed fence is red" is item 4's own wording ("an unclosed fence"), not a widening, and an open prose fence can swallow a block. Each is documented and tested. CM6 and CM7 turn them red. |
| 3b | Real-record pin (`RealRecordsTests`) | ACCEPTED | It pins the ten lines and the total exactly. A later edit of a backfilled block turns it red, which is intended. Records 71 and 73 are not in its list, so their own blocks will not disturb it. |
| 4 | Boundary | PASS | Changed: `CodeReview.md` (M), the scripts `README.md` (M), the ten records under `doc/reviews/workflow-governance/` (M), `rework_report.py` (A), `tests/test_rework_report.py` (A). No `forbid` path is touched. No `review-verdict` or `convergence-disposition` grammar changed. `cp/wave3` has moved on from `50b4685e`, but none of the later commits touches these paths. |
| 4b | README and CodeReview text (items 1, 2, 6) | PASS | README: intro "Twelve" with `rework_report.py`, tool-fault list extended, new section. The §3 bullet states scope, grammar, writers, causes and the report. `test_gate_contract.py` (README pin) passes unchanged. |
| 5a | Seat mutation evidence (M1) | PASS | Five mutations: diffs and full output are in `M1.txt`, which is raw-equal to the receipt block. Each exits 1 for the intended test: unknown cause, 4 SUBFAILED on the unknown-cause test; APPROVED causes, 3; fault suppresses reds, both red-before-fault tests; skipped round, 8; cross-check, 6. Each was restored with porcelain empty. |
| 5b | Reviewer counter-mutations (disposable clone at the candidate, full test file, no `-x`) | 6 red, 2 zero-red (S73-02) | CM1: any-candidate disposition, red (1). CM2: first, not nearest, verdict, red (6). CM3: `65`/`650` prefix collision, red (1). CM4: fault-only exits 1, red (4). CM5: upper-case hex candidate, **zero red**. CM5b: candidate grammar deleted, **zero red**. CM6: `RETURN` takes any causes, red (3). CM7: only an unclosed `rework-record` fence is red, red (1). Each restored, porcelain empty; the restored file passes (61 passed). |
| 6a | Receipt cells | PASS | P1, T1, M1, O1, C1, F1, P9 and E1 raw blocks are byte-equal to their LF capture files. Every cell names the candidate. The `tool_digest` sha256 values equal the three scripts at the candidate. |
| 6b | E1 / P9 rerun | PASS | E1 on `RETURN.md` with the appended USAGE cell gives `cells=8 defects=0`, exit 0. P9 on `RETURN.as-returned.md` gives defects 0, exit 0. |
| 6c | C1 / CI | PASS | Run 44589631425: headSha `9ae502de…`, `test (linux)` and `test (windows)` success. 14975 log lines, zero `UNREGISTERED_FAILURE` or `REGISTERED_NOT_FAILING`. Run 44587772912 (`06667834`) failed on both jobs, not only Linux; see the observations. |
| 6d | F1 | PASS | 5 failed, all five in the dispatch's registered list and in `jas48_F1_base.txt`, so zero new red. No orphan lease is left: `tests/.johnny-runtime` is absent in `73-rework`, `73-rework-review` and the main checkout. The host lock is absent. I did not rerun the full suite: it takes about 22 minutes, longer than a foreground command, and I start no background process. |
| 6e | STATEMENT | PASS with observations | Items 1-5, 8-17 and 19-21 match what I observed. I did not independently verify item 19 (CRLF→LF only); P1/T1/F1 content is consistent with it. Items 6, 7 and 18 (160, not 166, inserted lines): see the observations. |

## Correction requested (same ticket, same branch, additive commit)

1. S73-02: in `test_candidate_values_outside_the_grammar_are_a_red`, assert the `VALUE_INVALID` candidate reason. Add `RETURN`-block cases for a 39-character, a 41-character and an upper-case candidate. Show in M1 that deleting the candidate grammar check turns them red.
2. Rerun P1, T1, the affected M1 entry, and E1 last.

S73-01 goes to the control plane. It decides whether this correction also adds the red named there, by a ticket amendment, or whether the red is carried. S73-03 is a follow-up for the next change of `rework_report.py`.

```review-verdict
candidate: 9ae502de5dbbf7e36b39179bcfbbc0a1d380519e
verdict: CHANGES_REQUESTED
round: initial
reviewer: seat:ticket-review/R73-1
reviewed_at: 2026-11-19T19:43:37Z
blocking: S73-02
```

```rework-record
candidate: 9ae502de5dbbf7e36b39179bcfbbc0a1d380519e
round: 1
kind: INITIAL
verdict: CHANGES_REQUESTED
causes: CONTROL_PLANE_RULE,IMPLEMENTATION_DETAIL
```

## Residue (run id R73-1)

I removed `.worktrees/73-rework-review-scratch/R73-1/` (probe records, scripts, captures and CI logs) and `.worktrees/73-rework-review-scratch/R73-1-clone`. I also removed the ignored `skills/johnny-project-takeover/scripts/__pycache__/` that my in-process `integrate` import wrote in the review worktree. Its porcelain, ignored files included, is empty again. I took no host lock. No background process is left: the one pytest that the host moved to the background ran to completion, and no Python process is running. PROCESSES_LEFT=0.

---

## Correction review (round: correction)

- Candidate: `b5121ee0c6258f820a9af04854b5a65581b0d1b6`. It is one additive commit on `9ae502de` (reviewed above) and changes only `tests/test_rework_report.py`: 20 lines added, 1 removed. `rework_report.py`, the records and the documents are byte-identical to `9ae502de`.
- Receipt: `.worktrees/73-rework-out-c1/RETURN.md`. The as-returned copy differs only by the appended `USAGE seat:implementation-standard/JAS73R1C1` cell.
- Authority: S73-02 of the initial findings above. S73-01 and S73-03 are carried to wave 4 by the control plane and are not re-raised here.
- Seat: the same `ticket-review` seat, run id `R73-2`. The worktree is detached at the candidate, with porcelain (ignored files included) empty before and after. I did not re-review unchanged parts. Output was read unfiltered (`-q -rfEs` to a file, read in full).

### S73-02

| id | status | evidence |
| --- | --- | --- |
| S73-02 | CLOSED | `test_candidate_values_outside_the_grammar_are_a_red` now asserts `VALUE_INVALID` and "is not 40 lower-case hex" for each value. New `test_a_return_block_candidate_outside_the_grammar_is_a_red_with_its_reason`: on the unpaired `RETURN` path, 39 and 41 characters, upper-case, `g`-digits, `NONE`, empty and 64 characters each give exactly one red with that reason. New `…_of_forty_lower_case_hex_digits_or_none_is_accepted` pins the accepted side. I reran my counter-mutations in a fresh disposable clone at the candidate, on the full test file, without `-x`. **CM5** (upper-case hex): red, 2 SUBFAILED (both tests, `A`×40); zero red before. **CM5b** (grammar check deleted): red, 14 SUBFAILED (7 values × 2 tests); zero red before. Two more doors of my own: **CM5c** (`[0-9a-f]{39,41}`) is red, 4 SUBFAILED (39 and 41, both tests). **CM5d** (`none` accepted in any case) is red, 2 SUBFAILED (`NONE`, both tests). Each was restored with porcelain empty; the restored file passes (63 passed, 96 subtests). |

### Did the correction introduce a defect

None found.
- The one removed line takes `"none"` out of the value loop. It is not dropped: a separate assertion right after the loop checks exit 1 with `VALUE_INVALID` and "candidate none", the reason that belongs to it. `test_candidate_none_outside_a_return_block_is_a_red` is unchanged. No existing assertion is weakened, and no test is skipped or deleted.
- The mixed accepted value `"0123456789abcdef" * 2 + "01234567"` is 40 characters.
- `mypy --strict --python-version 3.11` on the script and the test: no issues. `tests/test_rework_report.py`: 63 passed, 96 subtests, exit 0.

### Receipt truth

| check | result |
| --- | --- |
| Raw blocks equal capture files | PASS: P1, T1, M1, O1, C1, F1, P9 and E1 are byte-equal. All are LF (zero CR in the captures and the receipt). |
| Every cell at the candidate; tool digests | PASS: `candidate: b5121ee0…` in every cell. The `tool_digest` values equal the sha256 of the three scripts at the candidate. |
| E1 rerun by the reviewer | PASS: `cells=8 defects=0`, exit 0, on `RETURN.md` with the USAGE cell. P9 on `RETURN.as-returned.md`: defects 0, exit 0. |
| M1 | PASS: the five original mutations plus CM5 (2 failed) and CM5b (14 failed). Each exits 1, each was restored with porcelain empty, and my own reruns give the same counts. |
| O1 | PASS: my rerun at the candidate is byte-equal to `O1.txt` (apart from its `exit=` line), exit 0. |
| C1 / CI run 44601755370 | PASS: headSha `b5121ee0…`, `test (linux)` and `test (windows)` success. 14978 log lines, zero `UNREGISTERED_FAILURE` or `REGISTERED_NOT_FAILING`. |
| F1 | PASS: 5 failed, exactly the five registered base failures, so zero new red. `tests/.johnny-runtime` is absent in `73-rework`, and the host lock is absent. I did not rerun it and took no lock. |
| STATEMENT (11 items) | PASS: items 1 to 11 match what I observed, including test counts, mutation counts, the CI run, and residue (no `JAS73R1C1` file is left in `73-rework-scratch`). I did not independently verify the CRLF→LF conversion of item 8; the captures are consistent with it. |

### Conclusion

S73-02, the only blocking finding of the initial round, is closed. The correction introduces no defect, and the receipt is true. S73-01 and S73-03 stay with the control plane for wave 4. No finding of this review is open, so `CONVERGENCE_REVIEW_REQUIRED` is not attached.

```review-verdict
candidate: b5121ee0c6258f820a9af04854b5a65581b0d1b6
verdict: APPROVED
round: correction
reviewer: seat:ticket-review/R73-2
reviewed_at: 2026-11-19T20:10:24Z
open_findings: none
carried_by_control_plane: S73-01, S73-03 (wave 4)
```

```rework-record
candidate: b5121ee0c6258f820a9af04854b5a65581b0d1b6
round: 2
kind: CORRECTION
verdict: APPROVED
causes:
```

### Residue (run id R73-2)

I removed `.worktrees/73-rework-review-scratch/R73-2/` (the mutation script, captures and CI log) and the clone `.worktrees/73-rework-review-scratch/R73-2-clone`. I took no host lock and started no background process. PROCESSES_LEFT=0.

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/JAS73R1C1` | claude-sonnet-5-5 | 334 | 619231 | 38138671 | 129756 | 38758236 | OVER_PROCESSED |
| `seat:ticket-review/R73-2` | claude-opus-5-5 | 142 | 455112 | 10877128 | 55067 | 11332382 | WITHIN |

Both seats ran with their model and effort named: implementation `claude-sonnet-5-5` at `high`, review `claude-opus-5-5` at `high`. The implementation seat is over its processed expectation. Its first pass ran two full suites: one it stopped itself, which left an orphan lease, and one that then failed 147 tests because of that lease, before the clean F1 rerun. The correction pass added a third full suite. Over-expectation is recorded here and does not block.

### Disposition of the non-blocking findings (control plane)

| Item | Class | Disposition |
| --- | --- | --- |
| S73-01: no red for a review section without a block, or for two blocks paired to one `review-verdict` | TICKET_DEFECT, Medium | Wave 4 (REQ-20261120-044, carried items) |
| S73-03: the report accepts any APPROVED disposition for the candidate, while `integrate.py` judges only the last one | OUT_OF_SCOPE_HARDENING, Low | Wave 4 |
