# REVIEW — ticket 69 Token use per seat

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** The `USAGE` cell in `evidence_gate.py` is right. It holds the
fields in the ticket's order, every refusal is a red with a named code listed in the README, it is
never required, and every existing evidence-gate test passes with no line of
`tests/test_gate_evidence.py` changed. The expectation template holds the ticket table's values.
CI run 44320582375 is green on both jobs at the candidate. The receipt is honest: P9 and E1 pass when
I rerun them, and the raw blocks and tool digests recompute.

`usage_report.py` misclassifies exits in three ways:

- it prints no red and exits 2 whenever any fault is met, which is the reverse of R4-2's
  red-before-fault rule (S69-01);
- a schema-valid count longer than 4300 digits ends in `unexpected ValueError`, exit 2, although
  the gate accepts it and the verdict is an over (S69-02);
- a `## USAGE <seat>` section that has lost its `cell:` line is red at the gate but invisible to
  the report, so a seat over its expectation is hidden and the report exits 0 (S69-03).

The runbook section also still says the owner has not confirmed the values, but the ticket blob
under review records the owner's confirmation of 2026-11-18 (S69-04).

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/69-token-use-per-seat.md`, revision01, read at `c4ec636a` (`git show c4ec636a:…`). Compared with the dispatch base `c5848465`, only two lines differ: the owner's confirmation of the expectation values, 2026-11-18 ("1A"), in the expectation paragraph and in the owner override row. The table values did not change |
| Spec | workflow-governance Revision 04 R4-2 (exit table, red before fault), R4-7 (receipt cell); REQ-20261103-043 readiness criterion 5 |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-69_dispatch.yaml` (base `c5848465830460188610bd399761e623fc9b8b96`) |
| Candidate | `393a0e80a6732a306843fe0383ea9a5c0d263a7a` on `cp/wave3-69-token-use`. `git ls-remote origin cp/wave3-69-token-use` returns the same sha. Four commits on `c5848465`: `e671c445`, `91fde38b`, `6d873fb2`, `393a0e80`. The base is an ancestor of the candidate. None of the candidate's paths changed on `cp/wave3` between `c5848465` and its tip `8384ffbb` |
| Commit identity | All four commits have `Johnny Liu <johnny.liu365@gmail.com>` as author, and each ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` |
| Changed paths | Modified: `doc/runbooks/dispatch-model-profile.md`, `skills/johnny-project-takeover/scripts/README.md`, `skills/johnny-project-takeover/scripts/evidence_gate.py`, `template/README.md`, `template/doc/handoffs/governance/RECEIPT.TEMPLATE.md`, `tests/test_gate_evidence.py`, `tests/test_state_file_templates.py`. Added: `skills/johnny-project-takeover/scripts/usage_report.py`, `template/doc/handoffs/governance/usage-expectation.TEMPLATE.json`, `tests/test_usage_report.py`. These are exactly the boundary's `modify` and `create` entries. No `forbid` path (`library/`, `Workflow.md`, `AGENTS.md`, `CodeReview.md`, `modules/spec/`) and no other gate script is touched |
| Review worktree | `.worktrees/69-token-use-per-seat-review`, detached at the candidate. Porcelain was empty before and after |
| Receipt | `.worktrees/69-token-use-per-seat-out/RETURN.md` (LF, 58353 bytes). Cells P1, T1, M1, C1, F1, P9, STATEMENT, E1 |
| CI run | 44320582375, https://github.com/johnnyliu365-sys/Johnny_AI_Skill/actions/runs/44320582375, event `push`, `headSha` = candidate, `headBranch` `cp/wave3-69-token-use`. `test (linux)` success, `test (windows)` success. Read only with `gh run view` |
| References applied | `AGENTS.md` (both P0 sections); `CodeReview.md` (whole file, §4, §5 rule B); `review-checks.md` (missing values, token parsing and comparison, error-code consistency, exception behaviour, test truthfulness and reviewer counter-mutation); workflow-governance R4-2 and R4-7 |
| XSS / privileged JS | Not applicable. There is no browser, DOM or JavaScript surface: these are stdlib command-line scripts, templates and their tests |
| Secret / provider / external effect | Not applicable. No secret, log, provider or webhook is involved. The only external effect is the seat's push of its own branch, which the dispatch allowed |
| Agent control / profile fan-out / POC ancestry | Not applicable. There is no Agent control path, there is one implementation seat, and there is no POC or staging |
| P0 source type | `mypy --strict --python-version 3.11` on both scripts exits 0 (`Success: no issues found in 2 source files`). No `Any` or `type: ignore`. Imports are stdlib only. JSON is narrowed with `isinstance` at the boundary into `Limits` and `Seat` |

### Seat's reported deviations

| Deviation | Judgement |
| --- | --- |
| `6d873fb2` made with `git commit --amend` on a local, unpushed commit, which the dispatch forbids | **Recorded, not a finding.** The prohibition is a process rule, and the seat disclosed the breach. The pushed history (`91fde38b` → `6d873fb2` → `393a0e80`) is additive. The first CI run 44316858420 is on `91fde38b`, which is still an ancestor. The receipt and CI bind the pushed tip. I verified the content of every commit from the diff itself, not from the seat's report. The seat must not repeat this in the correction |
| New codes in a separate `UsageCode` enum | **Accepted.** `tests/test_gate_evidence.py:406-409` pins `DefectCode` at exactly 14 members, and the ticket requires existing tests to pass unchanged. `Defect.code` is typed `DefectCode \| UsageCode`, and both render through `.value`. mypy --strict passes |
| `USAGE` block as a fenced example in the template preamble | **Accepted.** `tests/test_wave2_end_to_end.py:552-562` fills the template from the first section on and asserts that no placeholder is left. That file is outside the boundary. The preamble already holds placeholders in its table. `fill_usage` builds the cell from the example, and the gate and the report then read it (`test_the_filled_usage_cell_is_read_by_the_gate_and_the_report`) |
| `OVER_OUTPUT,OVER_PROCESSED` for a seat over both limits | **Accepted.** The ticket names both verdicts and no single word for both. The form is documented in the README and the docstring, and pinned by `test_both_over_lists_both_words` |
| Exit 2 beats exit 1 | **Rejected: S69-01.** The ticket's exit table is headed "Exit codes, as R4-2 sets them", and R4-2 fixes red before fault |
| `profile` must equal the profile the seat id names | **Accepted.** The seat id is `seat:<profile>/<run-id>` by definition (R4-7), so a cell whose two profiles differ contradicts itself |
| Heading must be `USAGE <seat>` | **Accepted.** The ticket's form is `## USAGE <seat>`. It is pinned in the gate by `test_a_heading_that_is_not_the_seat_is_a_red` (CM4 red) |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Boundary | PASS | `git diff --name-status c5848465 393a0e80` lists the ten boundary paths only (see Changed paths) |
| 2a | USAGE fields and their order | PASS | `USAGE_FIELDS` (`evidence_gate.py:92-102`) and `FIELDS` (`usage_report.py:46-56`) follow the ticket order exactly. `USAGE_FIELD_ORDER` compares the order of the fields present with the canonical subset (`evidence_gate.py:797-801`). Tests: `test_fields_out_of_order_are_a_red` and `test_fields_out_of_order_are_exit_two` |
| 2b | Each refusal and its code, all listed in the README | PASS | A missing field gives `USAGE_FIELD_MISSING`. A repeated field gives `USAGE_FIELD_REPEATED`. Wrong order gives `USAGE_FIELD_ORDER`. A negative or non-integer count gives `USAGE_COUNT_INVALID`, as do `+5`, `05`, `00`, `-0`, `1.5`, `1e3`, `١٢`, `１２`, `१`, `1٢`, `²` and a lone CR (probes 4e, 4f, 4c). A run field or a fence gives `USAGE_HAS_RUN_FIELDS`, and two cells for one seat give `USAGE_DUPLICATE_SEAT`. An empty or control-character model/source, the seat form, the profile mismatch, the heading and an unknown line give `USAGE_FIELD_INVALID`. All seven codes are in the module docstring and in `scripts/README.md` "The USAGE cell" |
| 2c | No USAGE cell is ever required by the gate | PASS | `test_a_usage_cell_is_never_required`. The seat's receipt has no USAGE cell and passes E1 (exit 0, `cells=7 defects=0`). A USAGE cell does not stand in for a run cell (`test_a_usage_cell_does_not_stand_for_a_run_cell` gives `NO_CELLS`) |
| 2d | `usage_report.py` line, verdicts and exit codes 0/1/2/3 | **FAIL: S69-01, S69-02, S69-03** | The line format, the processed sum and `>` hold (seat M4 and my CM3 red). Exit 0, 1 and 3 are right on a single input. Exit 2 suppresses every red line and wins over 1 (probe 4g). A 4301-digit count gives exit 2 `unexpected ValueError` (probe 4d). A `## USAGE` section without `cell:` is skipped (probe 3) |
| 2e | Repeated keys, NaN, Infinity refused | PASS | `object_pairs_hook=refuse_repeats` and `parse_constant=refuse_constant` (`usage_report.py:148-158, 178`). Probes refuse an inner and an outer repeated key, `NaN` and `-Infinity` (each exit 2, one line). The NaN test asserts the word `refused`, so removing `parse_constant` would turn it red rather than being masked by the integer check |
| 2f | Every printed subject escaped to one line | PASS (evidence notes in S69-06) | The gate renders every subject through `printable` (`repr`). The report escapes paths, seat, profile, heading and lines. Probes: U+2028 in seat → `\u2028` on one line in both scripts. A VT in a model/count is escaped. A path holding U+2028 is escaped. Note: U+2028 and U+0085 inside `model`/`source` are accepted by both scripts. That is the pre-existing `has_bad_text` definition (C0 and DEL only). Neither value is printed |
| 2g | Expectation template equals the ticket table | PASS | `usage-expectation.TEMPLATE.json`: implementation-standard 130000/24000000, implementation-elevated 130000/24000000, ticket-review 110000/23000000. LF, final newline. Pinned by `test_the_expectation_template_holds_the_three_profiles_with_the_proposed_values` |
| 2h | Runbook section says what the ticket says | **FAIL: S69-04** | The section names the file, says the control plane appends each cell after the seat returns, and says an over is a fact for the review record, not a block. Then `dispatch-model-profile.md:92` says "**The owner has not yet confirmed these values**". The ticket at `c4ec636a` says they were confirmed on 2026-11-18 |
| 3 | Existing evidence-gate tests unchanged and passing; no template-test assertion weakened | PASS | `git diff c5848465 HEAD -- tests/test_gate_evidence.py`: 139 lines added, 0 removed (only `UsageCellTests` and helpers appended). In `tests/test_state_file_templates.py`, each changed line keeps or tightens its assertion. `NEW_TEMPLATES` gains the fourth file, and the directory listing is still exact. The placeholder set is still exact equality, now body ∪ USAGE, with an added exact check of the example block. `receipt_problems` excludes USAGE from runs but adds three shape checks for it. The repeated-field case finds the field after the first `## `, which is the same body line the old `next(...)` found before the preamble held a `cell:` line. My run of the four P1 files: 379 passed, 1 skipped (symlink privilege), 537 subtests passed |
| 4 | Exit classification (R4-2) | **FAIL: S69-01, S69-02, S69-03** | See "Exit-classification probes" below |
| 5 | Receipt honest | PASS | P9 (`receipt_check.py`) on the receipt as returned: 7 `[ok]`, 1 `[statement]`, 0 defects, exit 0. E1 on the receipt as returned: `cells=7 defects=0`, exit 0. The tool digests of `dispatch_lint.py`, `receipt_fence_check.py`, `index_pins.py`, `evidence_gate.py` and `usage_report.py`, recomputed from `git show 393a0e80:<path> \| sha256sum`, equal the listed values. The raw blocks of T1, C1, F1 and M1 are byte-equal to their captures. T1 sha256 `78c63eba…6714c`, C1 `eb68aa80…403ff`, F1 `24fa6acf…4d20b`, M1 `ebcef608…d8436`, each equal for block and file. The F1 failure set (5 names) is a subset of the 12 base names in `jas48_F1_base.txt`. The P9 capture omits P9 and E1, consistent with "E1 runs last" |
| 6 | Real receipt with the implementation seat's USAGE | PASS (OVER_PROCESSED, exit 1, as expected) | See "usage_report on the real receipt" below. The evidence gate on the same receipt: `cells=7 defects=0`, exit 0 |
| 7 | Reviewer counter-mutations | Done; two zero-red | See the table below. CM1 and CM2 turn nothing red (S69-05) |
| 8 | Seat M1 | PASS | The capture records `git clone --no-hardlinks`, the HEAD, the porcelain before and after each restore, each diff and the unfiltered tail. All four mutations are red on named tests: a negative count → 4 subtests of `test_a_negative_count_is_a_red`; a run field → 5; the presence check dropped → 2 `PresenceTests`; `>=` → 3 |
| 9 | P9 checker against a receipt with a USAGE cell | Confirmed (S69-07) | `receipt_check.py` on the receipt with the item-6 USAGE cell appended: `[FAIL] USAGE seat:… (cell USAGE)` with 7 defects (missing candidate/capture/exit, three missing tool digests, no raw block), exit 1 |

### Exit-classification probes (hand-made receipts and expectation files; `probe.py`, `probe2.py`, `probe3.py` in the scratch directory)

The receipts are the seat's `RETURN.md` with cells appended. The gate runs with the E1 arguments against the out directory. The report runs with the template expectation unless the row says otherwise.

| Probe | Gate | Report | Judgement |
| --- | --- | --- | --- |
| Undecodable byte (`\xff\xfe`) in a USAGE `model` | 1 `USAGE_FIELD_INVALID` | 2, one line, `is not UTF-8` | Right (ticket TDD 6: an undecodable receipt is exit 2 with one line) |
| Undecodable expectation file | — | 2, one line | Right |
| BOM on the receipt | 0 | 0 (stripped) | Right, the same as the gate |
| BOM on the expectation file | — | 2, `starts with a byte order mark` | Right (input refused, not a red) |
| CRLF receipt; CRLF expectation | 0 | 0; 0 | Right |
| Lone CR inside a count / inside `source` | 1 `USAGE_COUNT_INVALID` / 1 `USAGE_FIELD_INVALID` | 2 / 2 | Right per the ticket (a schema break is 2) |
| Count of 4300 digits | 0 | 1 `OVER_OUTPUT` | Right |
| Count of 4301 or 20000 digits (output or input) | 0 | **2, `unexpected ValueError: Exceeds the limit (4300 digits)`** | **Wrong: S69-02.** Valid at the gate, and an over by value, so it should be 1 |
| Expectation limit of 4301 digits | — | 2, `not accepted JSON` | Acceptable: the expectation file is refused as input. 400 digits read fine |
| `+5`, `05`, `00`, `-0` | 1 | 2 | Right |
| ` 5`, `5 ` | 0 | 0 (value 5) | Both scripts strip horizontal space after the colon and at the end of the line. Consistent |
| JSON `+5`, `05` / `-0` / `1.0`, `1e3`, `true` | — | 2 / 1 (`-0` reads as 0) / 2 | Right. `-0` is the integer 0 in JSON |
| `١٢`, `１２`, `१`, `1٢`, `²` | 1 | 2 | Right on the candidate. The tests do not pin it past the first digit (S69-05) |
| A receipt without USAGE, alone | — | 1 `NO_USAGE` | Right |
| Over receipt + missing receipt | — | **2, no line printed** | **Wrong: S69-01** (R4-2: print every red, exit 1, fault on stderr) |
| `NO_USAGE` receipt + receipt with a broken USAGE cell | — | **2, `NO_USAGE` not printed** | **Wrong: S69-01** |
| `NO_USAGE` receipt + unreadable expectation | — | **2** | **Wrong: S69-01**: `NO_USAGE` needs no expectation |
| A directory as the receipt / as the expectation | — | 2 / 2 (`Permission denied` on Windows) | Right |
| Valid implementation cell + an over `ticket-review` cell without its `cell:` line | 1 `USAGE_FIELD_MISSING cell` | **0, one line, the over seat not listed** | **Wrong: S69-03** |
| The same with `cell: usage` | 1 (run-cell reds) | **0** | **Wrong: S69-03** |
| The same, cell intact | 0 | 1 `OVER_OUTPUT` listed | Right |

### usage_report on the real receipt (item 6)

The receipt is `RETURN.md` as returned, with this cell appended (scratch `item6/RETURN-with-usage.md`):

```text
## USAGE seat:implementation-standard/69-impl-rev01
cell: USAGE
seat: seat:implementation-standard/69-impl-rev01
profile: implementation-standard
model: claude-sonnet-5-5
input_tokens: 276
cache_write_tokens: 271788
cache_read_tokens: 26475429
output_tokens: 111397
source: host transcript usage, summed per unique message id
```

```text
$ python -I -X utf8 skills/johnny-project-takeover/scripts/usage_report.py --expectation template/doc/handoffs/governance/usage-expectation.TEMPLATE.json item6/RETURN-with-usage.md
seat:implementation-standard/69-impl-rev01 implementation-standard output=111397 processed=26747493 OVER_PROCESSED
exit=1
```

Processed is 276 + 271788 + 26475429 = 26747493, which is above 24000000, and output 111397 is within 130000. **The implementation seat is over its processed-token expectation by 2747493 tokens (11.4 %).** Under the owner's decision, this is a fact recorded here and not a defect: it does not block integration. The likely cause is visible in the receipt's process record, namely the two CI rounds (a first failing run 44316858420), the restarted F1 and the rerun M1. Each means long re-reads of a cached context. `evidence_gate.py` on the same receipt: `cells=7 defects=0`, exit 0.

### Reviewer counter-mutations (disposable `git clone --no-hardlinks --no-checkout` of the review worktree at `.worktrees/69-token-use-per-seat-review-scratch/cmclone` (removed after the run), detached at the candidate; full test file each, not `-x`; restored, porcelain empty after each; log `counter_out.txt`)

Output was read unfiltered: pytest ran directly through `subprocess`, with no wrapper, and the last 25 lines plus the diff of each run are in the log.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM1 | First match (leading digit masks the rest) | gate `USAGE_COUNT` `0\|[1-9][0-9]*` → `0\|[1-9]\d*` | **zero red** (237 passed). The gate would then accept `1٢`. The only non-ASCII case in `test_a_non_integer_count_is_a_red` is a single `١`, which `[1-9]` already refuses (S69-05) |
| CM2 | First match, on the report | report `COUNT` → `0\|[1-9]\d*` | **zero red** (47 passed). The report would then read `1٢` as `int('1٢') == 12` and `１２` would still be refused. A count would be silently misread (S69-05) |
| CM3 | Copy (the processed sum) | processed without `cache_write_tokens` | red: `test_one_line_per_seat_and_exit_zero_when_all_are_within`, `test_an_unknown_profile_is_listed_and_exit_one`, `test_one_over_the_processed_maximum_is_over_processed` |
| CM4 | Gate heading rule removed | `if section.heading != f"USAGE {seat}"` → `if False` | red: `test_a_heading_that_is_not_the_seat_is_a_red` |
| CM5 | Overlap masking (report's own duplicate-seat check vs the per-cell checks) | `if seat.seat in seen` → `if False` | red: `test_two_usage_cells_for_one_seat_are_exit_two` |
| CM6 | Recognition by heading dropped in the gate | `is_usage` → `value == USAGE_CELL` only | red: `test_a_missing_field_is_named_for_each_field` (subtest `name='cell'`: `NOT_RUN` instead of `USAGE_FIELD_MISSING`) |
| CM7 | Environment-scoped (escape) | `NO_USAGE` line without `printable` | red on this Windows host only: `test_a_receipt_without_a_usage_cell_is_exit_one`, because `repr` doubles the backslashes of a Windows temp path. A POSIX temp path holds nothing `repr` changes, and the expected value is built with the script's own `printable` (copy), so on the Linux job this mutation would stay green (S69-06) |
| CM8 | Gate control-character rule for `model`/`source` | `not values[name] or has_bad_text(...)` → `not values[name]` | **zero red** (237 passed). The gate would then accept a VT or other C0 character inside `model`/`source`; only the empty value and a control character in a count are pinned (S69-06) |

### Findings

| ID | Class | Blocks? | Severity | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S69-01 | `IMPLEMENTATION_DEFECT` (R4-2 exit classification) | **Yes** (§5 rule B: changes the red/fault classification) | High | `skills/johnny-project-takeover/scripts/usage_report.py:346-352`; `skills/johnny-project-takeover/scripts/README.md:812-815`; docstring `usage_report.py:19-22`; `tests/test_usage_report.py:241-246` | When any fault is met, `execute` prints the faults and returns 2 without printing any red line. So `NO_USAGE`, `UNKNOWN_PROFILE` and over verdicts for readable receipts vanish and the exit is 2. The ticket's exit table is "as R4-2 sets them", and R4-2 (owner-confirmed 2026-11-05) says that when one run meets a red and a fault, the gate prints every red it can find and exits 1, with each fault on stderr. Only faults that leave nothing to check end the run at once. An unreadable receipt among several, or an unreadable expectation beside a receipt without USAGE, leaves reds to find. The README's own preamble (line 11) says the gates "report every red they can find even when a fault was met on the way". The test `test_a_fault_wins_over_a_red_…` pins the wrong order | Probes 4g: over + missing receipt → 2, 0 stdout lines. `NO_USAGE` + broken → 2. `NO_USAGE` + unreadable expectation → 2 | This correction: print every red found (with an unreadable expectation, `NO_USAGE` still counts; per-seat verdicts that need it are not computed), each fault on stderr, exit 1 if any red else 2. Fix the README sentence, the docstring and the test |
| S69-02 | `IMPLEMENTATION_DEFECT` (R4-2: a red reported as a fault; the gate and the report disagree) | **Yes** (exit classification) | Low (no host reports such counts), but the exit class is wrong | `usage_report.py:279-280` | The grammar is "decimal digits without a sign or a leading zero", with no bound, and the gate accepts any length. `int()` refuses more than 4300 digits under Python 3.11's default limit and raises `ValueError`. That is not an `InputFault`, so it reaches the catch-all in `main` and exits 2 with `unexpected ValueError`. The correct verdict is over (exit 1) | Probe 4d: 4300 digits → 1 `OVER_OUTPUT`; 4301 and 20000 digits (output or input) → 2 `unexpected ValueError: Exceeds the limit (4300 digits)…`. The gate gives 0 for both | This correction: either compare without the conversion limit (for example compare lengths, then strings, for the verdict, and sum with an explicit bounded rule), or bound the digit count in the grammar of both scripts identically with a named refusal. Add a test either way |
| S69-03 | `IMPLEMENTATION_DEFECT` (the gate and the report disagree on what is a USAGE cell; a schema break exits 0) | **Yes** (exit classification: a fault or red reported as a pass) | Medium | `usage_report.py:226-233` vs `evidence_gate.py:247-249` | The gate treats a section as USAGE when its `cell:` is `USAGE`, or when it has no `cell:` line and its heading is `USAGE` or `USAGE <…>` (the seat's own convention, in the STATEMENT). The report recognises a section only by a first `cell:` line equal to `USAGE`. A `## USAGE <seat>` section that lost its `cell:` line, or spells it `cell: usage`, is a red at the gate but is silently skipped by the report. When the receipt holds another valid cell, the report exits 0, and an over seat is never listed. The ticket gives the report presence and comparison ("`usage_report.py` enforces presence"), and by its own README such a cell "breaks its schema" (exit 2) | Probe 3: valid implementation cell + over `ticket-review` cell without `cell:` → gate 1 `USAGE_FIELD_MISSING cell`; report 0 with one line. With `cell: usage` → gate 1; report 0. Intact → report 1 `OVER_OUTPUT` | This correction: recognise USAGE sections in the report by the same rule as the gate (a heading `USAGE`/`USAGE <…>` makes the section a USAGE cell whatever its `cell:` line says, or the gate's rule exactly). A malformed one is then exit 2. Add the two probe cases as tests |
| S69-04 | `IMPLEMENTATION_DEFECT` (ticket/Context conformity; documentation) | Yes (must be corrected before integration; not an exit-class issue) | Medium | `doc/runbooks/dispatch-model-profile.md:88-93` | The runbook section says "**The owner has not yet confirmed these values**; they are confirmed before ticket 69 is integrated, and until then a verdict compares against an unconfirmed proposal". The ticket blob under review (`c4ec636a`) records "The owner confirmed them on 2026-11-18 ("1A", REQ-20261103-043)". The seat wrote to the dispatch, which predates the confirmation, so the cause is the post-dispatch ticket edit, not a seat error. Shipped as is, the governance runbook would state something false | `git diff c5848465 c4ec636a -- modules/tickets/workflow-governance/69-token-use-per-seat.md` shows the two changed lines. The table values did not change and the template already equals them | This correction: state that the owner confirmed the values on 2026-11-18 ("1A", REQ-20261103-043) |
| S69-05 | `EVIDENCE_DEFECT` (would let a regression admit a wrong count; rule B: close in the next change of this gate) | No (candidate behaviour is right) | Medium | `tests/test_gate_evidence.py:2147-2150`; `tests/test_usage_report.py:209-212` | Non-ASCII digits are refused by the candidate (probe 4f), but no test pins it past the first character. The gate's case list has a lone `١`, which `[1-9]` refuses whatever follows. The report's list has no non-ASCII digit at all. With `\d` in place of `[0-9]` (CM1, CM2), every test stays green. The gate would then accept `1٢`, and the report would read it as 12 | CM1 zero red; CM2 zero red; `int('1٢') == 12` on the venv | This correction: add `1٢`, `１２` and `+5` to both lists (gate: `USAGE_COUNT_INVALID`; report: exit 2) |
| S69-06 | `EVIDENCE_DEFECT` (escape and control-character pins) | No | Low | `tests/test_usage_report.py:173-177`; `tests/test_gate_evidence.py:2176-2183` | (a) The `NO_USAGE` subject's escape is pinned only through the backslashes of a Windows temp path, against an expected value built with the script's own `printable`. On the Linux job, CM7 would stay green (environment-scoped and copy doors). (b) The gate's refusal of a control character inside `model`/`source` is not pinned: CM8 removes it and every test stays green (`test_an_empty_model_or_source_is_a_red` covers only the empty value; the control-character test uses `output_tokens`). The candidate refuses it (probe2: VT in `model` → `USAGE_FIELD_INVALID`), and the report's test pins it there | CM7: red on Windows only, through backslash doubling; CM8 zero red | This correction or the next change of these scripts: pin `NO_USAGE` with a literal expected escape of a path holding a character `repr` changes on every OS (for example U+2028), and pin a control character in `model`/`source` at the gate |
| S69-07 | `OUT_OF_SCOPE_HARDENING` (follow-up; not a defect of this ticket) | No | Medium for the process | `doc/reviews/workflow-governance/evidence/48/receipt_check.py:88-93` | Confirmed: the wave-1 P9 checker skips only sections whose `cell:` is `STATEMENT`, and judges every other section with a `cell:` line as a run cell. A receipt with the control plane's appended `USAGE` cell therefore fails P9 (7 defects, exit 1). The checker is outside this ticket's boundary, and the ticket's order of operations (P9 and E1 on the receipt as returned, then the control plane appends `USAGE`) is met. Every later dispatch that runs P9 on a receipt after the append would go red | P9 on `item6/RETURN-with-usage.md` → `[FAIL] USAGE seat:implementation-standard/69-impl-rev01 (cell USAGE)`, `--- receipt defects: 7`, exit 1. On the receipt as returned → exit 0 | Control plane: either judge P9 before the append (state it in each dispatch), or open a follow-up that retires P9 in favour of E1 (which already knows USAGE) or teaches `receipt_check.py` to skip `cell: USAGE` |

### Commands

```text
git -C .worktrees/69-token-use-per-seat-review diff --name-status c5848465 HEAD
git show c4ec636a:modules/tickets/workflow-governance/69-token-use-per-seat.md
git diff c5848465 c4ec636a -- modules/tickets/workflow-governance/69-token-use-per-seat.md
git ls-remote origin cp/wave3-69-token-use
gh run view 44320582375 --json headSha,conclusion,jobs,url,headBranch,event
python -m pytest tests/test_gate_evidence.py tests/test_usage_report.py tests/test_state_file_templates.py tests/test_ci_registered_failures.py -q -rfEs -p no:cacheprovider   (review worktree; 379 passed, 1 skipped, 537 subtests passed)
python -m mypy --strict --python-version 3.11 skills/johnny-project-takeover/scripts/evidence_gate.py skills/johnny-project-takeover/scripts/usage_report.py   (Success)
python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py .worktrees/69-token-use-per-seat-out/RETURN.md .worktrees/69-token-use-per-seat-review   (exit 0)
python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py ../69-token-use-per-seat-out/RETURN.md --repo . --candidate 393a0e80… --tool …/evidence_gate.py --tool …/usage_report.py --evidence-root ../69-token-use-per-seat-out --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1   (exit 0, cells=7 defects=0)
python -I -X utf8 probe.py / probe2.py / probe3.py   (scratch; output in probe_out.txt and above)
python -I counter.py CM1 … CM8   (scratch clone; log counter_out.txt)
```

All Python ran under `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`.

### Not verified

- I did not run the full suite under the host lock. The seat's F1 (5 failures, all in the base list) and CI run 44320582375 (both jobs green at the candidate) are the full-suite evidence. The host lock was not taken by this review.
- CM7's Linux behaviour is reasoned, not run: this host has no Linux runner, and I triggered no CI.
- The seat's first CI run 44316858420 and the amended local commit's previous content were not inspected beyond the seat's statement and the ancestry of `91fde38b`.
- The `implementation-elevated` profile has no measured basis (the ticket says so). Its values were checked only for equality with the ticket table.
- U+2028 and U+0085 inside `model`/`source` are accepted by both scripts under the pre-existing `has_bad_text` definition (C0 controls and DEL). Neither value is printed, so the one-line property of the output holds. I did not raise it as a finding.

```review-verdict
candidate: 393a0e80a6732a306843fe0383ea9a5c0d263a7a
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/69-rev01-initial
reviewed_at: 2026-11-18
```

```rework-record
candidate: 393a0e80a6732a306843fe0383ea9a5c0d263a7a
round: 1
kind: INITIAL
verdict: CHANGES_REQUESTED
causes: IMPLEMENTATION_DETAIL
```

## Revision01 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`, with every open finding non-blocking under CodeReview §5 rule B. No blocking finding remains: no exit-code misclassification, no safety or confinement issue and no P0 issue. The only open finding is S69-08. It is an evidence residue of S69-06: the candidate behaves correctly, but on POSIX the tests do not pin it, and a regression would not let a change pass. It therefore goes to a follow-up hardening ticket. S69-07 is answered by a runbook rule, and the P9 checker itself stays a control-plane follow-up. The control plane may record the rule B convergence disposition (`carried: S69-07, S69-08`).** Correction 1 (`7cc0e08f`) closes every blocking finding of the initial review:

- S69-01: `usage_report.py` now prints every red it finds before any fault, puts each fault on standard error, and exits 1 when it found a red and 2 only when it met a fault and no red. That is R4-2.
- S69-02: a count of any length is a value.
- S69-03: the report reads USAGE sections exactly as the gate does and never skips one.
- S69-04: the runbook records the owner's confirmation.

S69-05 is closed, and S69-06 is closed apart from one environment-scoped residue (S69-08). S69-07 is answered by a runbook rule. `evidence_gate.py` is byte-unchanged. CI run 44331023638 is green on both jobs at the candidate. The receipt passes P9 and E1 on my rerun.

The coordinator's correction message said "exit is 2 if any fault occurred". Under L-20 that sentence is superseded, and I judged the candidate against R4-2 and this record, as the coordinator directs. The seat's STATEMENT records that it followed R4-2.

| Field | Value |
| --- | --- |
| Ticket | Unchanged: revision01 at `c4ec636a` (see the initial review) |
| Candidate | `7cc0e08fa5cdf2d573c6c00806d59f09d1778d98` on `cp/wave3-69-token-use`; `git ls-remote` returns the same sha. It is one commit on `393a0e80`, which is an ancestor, so the change is additive. Author `Johnny Liu <johnny.liu365@gmail.com>`, trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. The remote tip moved from `393a0e80` to its child `7cc0e08f`, with no amend, rebase or force |
| Changed paths (`393a0e80..7cc0e08f`) | `doc/runbooks/dispatch-model-profile.md`, `skills/johnny-project-takeover/scripts/README.md`, `skills/johnny-project-takeover/scripts/usage_report.py`, `tests/test_gate_evidence.py`, `tests/test_usage_report.py`. All are in the boundary. `git diff --quiet 393a0e80 HEAD -- skills/johnny-project-takeover/scripts/evidence_gate.py` succeeds, so the gate is unchanged. No `forbid` path is touched. None of these paths changed on `cp/wave3` between `c5848465` and its tip `369d6844` |
| Review worktree | `.worktrees/69-token-use-per-seat-review`, detached at the candidate; porcelain was empty before and after |
| Receipt | `.worktrees/69-token-use-per-seat-out/RETURN.md`, rebuilt for `7cc0e08f` (LF, 83702 bytes, 0 CR). Cells: P1, T1, M1 (8 mutations), C1, F1, P9, STATEMENT, E1 |
| CI run | 44331023638, https://github.com/johnnyliu365-sys/Johnny_AI_Skill/actions/runs/44331023638, event `push`, `headSha` = candidate. `test (linux)` success, `test (windows)` success (read with `gh run view` only) |
| References applied | As in the initial review, plus CodeReview §5 rule B for classifying what remains open |
| P0 source type | `mypy --strict --python-version 3.11` on both scripts gives `Success: no issues found in 2 source files`. No `Any`, no `type: ignore`, stdlib only. `Limits` and `Seat` now carry decimal strings, as their comments say. `int()` is applied only to single ASCII digits inside `add_decimal`, after the `COUNT` regex has admitted the text |

### Finding dispositions

| ID | Initial class / blocks | Seat's disposition | Verification | Status |
| --- | --- | --- | --- | --- |
| S69-01 | `IMPLEMENTATION_DEFECT`, R4-2 / yes | Every red printed, faults on stderr, exit 1 with a red, else 2 | **Code:** `execute` prints the red lines first, then every fault on stderr. It returns `EXIT_RED` if any red, else `EXIT_FAULT` if any fault, else 0. An unreadable expectation sets `limits = None`: `NO_USAGE` still counts and no verdict is computed. **Probes:** over + missing receipt gives 1, the over line and one stderr line. `NO_USAGE` + broken receipt gives 1. `NO_USAGE` + unreadable expectation gives 1. Over + unknown + broken + missing gives 1 with both red lines and two stderr lines. Broken expectation + receipt with seats + `NO_USAGE` gives 1 with only `NO_USAGE`. Seats without an expectation give 2 with empty stdout. A fault alone gives 2. **Docs and tests:** the README, the docstring and the old test are corrected. **Counter-mutations:** CM9 and CM10 red | **Closed** |
| S69-02 | `IMPLEMENTATION_DEFECT`, R4-2 / yes | Counts compared as decimal text, no `int()` | **Code:** `add_decimal` adds digit by digit with carry. `is_greater` compares by length, then by text. That is sound because `COUNT` admits no leading zero, limits come from `str(int)`, and `add_decimal` never makes one. **Probes:** 4301-digit and 20000-digit output counts and a 4301-digit input count give 1 (`OVER_OUTPUT` / `OVER_PROCESSED`); they gave 2 `unexpected ValueError` before. A 4300-digit count gives 1. A 400-digit limit reads fine. **Pins:** `DecimalCountTests` (5000-digit counts, a 10^400 limit equal and one over, a carry across the three counts, the helpers) and, in the gate, `test_a_count_of_any_length_is_valid`. **Counter-mutation:** CM14 red. **Property check:** 20000 random pairs of integers below 10^40 give `add_decimal` = `str(a+b)` and `is_greater` = `a > b` on every pair. An expectation limit above 4300 digits is still exit 2 (`not accepted JSON`). That is an input refusal of the expectation file, judged acceptable in the initial review | **Closed** |
| S69-03 | `IMPLEMENTATION_DEFECT` / yes | Recognised exactly as the gate | **Code:** `split_usage_sections` takes the first `cell:` line, like the gate's `fields["cell"]`. `cell: USAGE` makes a USAGE cell. A heading `USAGE` or `USAGE <…>` with no `cell:` line makes a USAGE cell too, and `parse_usage` names the missing field. A USAGE heading with any other `cell:` value raises `InputFault`. That is stricter than the gate, which reads such a section as a run cell and reds it; neither passes it. **Probes:** an over review cell without `cell:` gives gate 1 `USAGE_FIELD_MISSING cell` and report 2 (it was 0). `cell: usage` gives gate 1 and report 2 (was 0). `cell: P1` under a USAGE heading gives gate 1 and report 2. An intact over cell gives report 1. **Pins:** `RecognitionTests`. The seat's M1 drops both new branches (red). **Counter-mutations:** CM11 and CM12 red | **Closed** |
| S69-04 | `IMPLEMENTATION_DEFECT`, conformity / yes | Runbook records the confirmation | `dispatch-model-profile.md` now says "The owner confirmed these values on 2026-11-18 ("1A", `REQ-20261103-043`)". The "not yet confirmed" sentence is gone. The values still equal the ticket table and the template | **Closed** |
| S69-05 | `EVIDENCE_DEFECT` / no | Non-ASCII digit pins | The gate's list adds `1٢`, `5٢`, `１２`, `१`, `²` and `1²`. The report's list adds `٢`, `1٢`, `5٢`, `１２`, `१`, `²` and `1²`. CM1 and CM2 (`\d`) are now both red (`1٢`, `5٢`); both were zero red before | **Closed** |
| S69-06 | `EVIDENCE_DEFECT` / no | Control-character pins; `NO_USAGE` escape through `no_usage_line` | **(b)** `test_a_control_character_in_model_or_source_is_a_red` covers VT, NUL, DEL and ESC in both fields. CM8 is now red: 8 subtests, where it was zero red before. **(a)** `PrintedSubjectTests` calls `no_usage_line` with U+2028, LF and VT paths and checks literal expected escapes on every OS. CM7 is red, including on `PrintedSubjectTests`. **Residue (S69-08):** the `NO_USAGE` line that `execute` prints is not pinned to the helper on POSIX. CM7b is red here only | **Closed** apart from the residue, which stays open as S69-08 (`EVIDENCE_DEFECT`, non-blocking) |
| S69-07 | `OUT_OF_SCOPE_HARDENING` / no | Runbook rule: P9 before the append, E1 alone after | The runbook gains the order of the receipt checks. P9 judges the receipt as returned. After appending USAGE cells, the control plane reruns E1 only. P9 is not rerun on such a receipt, and the reason is stated. `receipt_check.py` is unchanged (it is outside the boundary). My rerun matches the rule: P9 as returned gives 0; P9 with the item-6 cell gives 1 (7 defects); E1 with the item-6 cell gives 0 | **Answered** by a process rule in this ticket. Retiring P9, or teaching it USAGE, stays a control-plane follow-up |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Boundary | PASS | Five boundary paths; the gate is unchanged; no forbidden path |
| 2 | P1 test files and strict type | PASS | In the review worktree, `tests/test_gate_evidence.py tests/test_usage_report.py tests/test_state_file_templates.py tests/test_ci_registered_failures.py` gives 399 passed, 1 skipped (symlink privilege), 562 subtests passed, exit 0 (scratch `corr_P1.txt`). mypy --strict: Success |
| 3 | Existing assertions | PASS | **`tests/test_gate_evidence.py`:** one ticket-69 test's case list is longer (`١` is respelt `١`, the same character) and two tests are added. No line from before ticket 69 changed. **`tests/test_usage_report.py`:** one assertion is reversed on purpose, as S69-01 requires: `test_a_fault_wins_over_a_red…` becomes `test_a_red_and_a_fault_in_one_run_print_the_red_and_exit_one`, and the STATEMENT names it. One case list is longer and four classes are added. **`tests/test_state_file_templates.py`:** unchanged in this commit |
| 4 | Exit classification (R4-2), re-probed | PASS | Every probe of the initial review reran against `7cc0e08f` (scratch `corr/probe_out.txt`, `corr/probe2_out.txt`, `corr/probe3_out.txt`). Compared with the initial run, only the six intended exits changed: three counts over 4300 digits (2 to 1) and three red-plus-fault cases (2 to 1). The S69-03 cases go from 0 to 2. The undecodable, BOM, CRLF, lone CR, sign, leading-zero, non-ASCII and directory probes are unchanged |
| 5 | Receipt honest | PASS | **P9 and E1:** P9 on the receipt as returned gives 7 `[ok]`, 1 `[statement]`, 0 defects, exit 0. E1 as returned gives `cells=7 defects=0`, exit 0. **Tool digests,** recomputed from `git show 7cc0e08f:<path>`: `dispatch_lint` `3f5730c9…`, `receipt_fence_check` `8b3f845c…`, `index_pins` `63eff436…`, `evidence_gate` `89f8839b…` (unchanged), `usage_report` `63d25443…`. Each is listed in all 7 run cells. **Captures:** the raw blocks of P1, T1, C1, F1 and M1 are byte-equal to their captures, with no CR. **F1:** 5 failures, all in `jas48_F1_base.txt`. **M1:** the clone command and HEAD `7cc0e08f` are recorded; 8 mutations, each `exit=1`, with porcelain empty after each restore. **C1** matches my `gh run view` |
| 6 | Item 6 | PASS (OVER_PROCESSED, exit 1, as expected) | See the next section |
| 7 | Counter-mutations | Done | See the table below |

### usage_report on the real receipt (item 6, rerun at `7cc0e08f`)

The receipt is the rebuilt `RETURN.md` with the same implementation-seat cell appended (scratch `corr/item6/RETURN-with-usage.md`):

```text
## USAGE seat:implementation-standard/69-impl-rev01
cell: USAGE
seat: seat:implementation-standard/69-impl-rev01
profile: implementation-standard
model: claude-sonnet-5-5
input_tokens: 276
cache_write_tokens: 271788
cache_read_tokens: 26475429
output_tokens: 111397
source: host transcript usage, summed per unique message id
```

```text
$ python -I -X utf8 skills/johnny-project-takeover/scripts/usage_report.py --expectation template/doc/handoffs/governance/usage-expectation.TEMPLATE.json corr/item6/RETURN-with-usage.md
seat:implementation-standard/69-impl-rev01 implementation-standard output=111397 processed=26747493 OVER_PROCESSED
exit=1
```

The verdict is the same as at `393a0e80`, now computed by the decimal-text path. The implementation seat is over its processed expectation by 2747493 tokens (11.4 %). Under the owner's decision this is a fact recorded here, not a block on integration. On the same receipt, `evidence_gate.py` gives `cells=7 defects=0`, exit 0. `receipt_check.py` gives exit 1, which is what the S69-07 rule expects.

### Reviewer counter-mutations

All ran in a disposable `git clone --no-hardlinks --no-checkout` of the review worktree at scratch `corr/cmclone`, detached at `7cc0e08f`. Each run used its full test file and was restored, with porcelain empty afterwards. The clone was removed after the run. Output was read unfiltered from `subprocess`; the log is `corr/counter_out.txt`.

| ID | Aimed at | Mutation | Result |
| --- | --- | --- | --- |
| CM1 (rerun) | S69-05, gate | `USAGE_COUNT` `[0-9]` → `\d` | red: `test_a_non_integer_count_is_a_red` (`1٢`, `5٢`). It was zero red |
| CM2 (rerun) | S69-05, report | `COUNT` `[0-9]` → `\d` | red: `test_a_negative_or_non_integer_count_is_exit_two` (`1٢`, `5٢`). It was zero red |
| CM7 (rerun) | S69-06 | `no_usage_line` without `printable` | red: `test_the_no_usage_subject_is_escaped_on_every_platform` (platform-independent), plus three `NO_USAGE` output tests |
| CM7b (new) | S69-06, environment-scoped door | `execute` appends an inline `NO_USAGE` line, bypassing the helper | red only here, in three tests, through Windows backslashes. It would stay green on Linux (S69-08) |
| CM8 (rerun) | S69-06, gate | control-character check on `model`/`source` dropped | red: `test_a_control_character_in_model_or_source_is_a_red`, all 8 subtests (VT, NUL, DEL and ESC in `model` and `source`). It was zero red |
| CM9 (new) | S69-01, ordering door | `if red:` → `if red and not faults:` (the fault wins again) | red: 6 tests (`test_a_red_and_a_fault_in_one_run…`, four `RedBeforeFaultTests`, `test_such_a_section_beside_a_red_still_lets_the_red_stand`). This goes in the same direction as the seat's S69-01 mutation, spelt differently. CM10 is the independent door |
| CM10 (new) | S69-01, fault-as-red door | an unreadable expectation sets `limits = {}`, so every seat turns into an `UNKNOWN_PROFILE` red | red: 24 (every `ExpectationSchemaTests` fault case and `test_the_verdicts_that_need_the_expectation_are_not_computed_without_it`) |
| CM11 (new) | S69-03, prefix door | the heading rule uses `startswith("USAGE")` without the space | red: `test_a_section_with_another_heading_and_no_cell_line_is_not_a_usage_cell` |
| CM12 (new) | S69-03, case-fold door | `cell.upper() == "USAGE"` | red: `test_a_misspelt_cell_line_under_a_usage_heading_is_not_skipped` (`usage`, `Usage`) |
| CM14 (new) | S69-02, comparison door | `is_greater` without the length step (text order only) | red: 12 tests, including `test_the_decimal_helpers` and `test_a_count_equal_to_a_long_limit_is_within_and_one_more_is_over` |

### Findings of this review

| ID | Class | Blocks? | Severity | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S69-08 | `EVIDENCE_DEFECT` (residue of S69-06, still open after the correction) | No. Rule B: the candidate's behaviour is correct and only unpinned. A regression would break the one-line output but would not let a change pass, so this goes to a follow-up hardening ticket | Low | `tests/test_usage_report.py:173-177` and `RedBeforeFaultTests` | The tests check the `NO_USAGE` line that `execute` prints against `usage_report.printable(str(path))` of a plain temp path. Only Windows backslashes make `repr` change that path, so on POSIX nothing pins that `execute` goes through the escaping helper. `PrintedSubjectTests` pins only the helper itself | CM7b is red on this Windows host only | Follow-up hardening ticket (rule B carry): run `execute` on a receipt whose path holds a character that `repr` changes on every OS (for example U+2028), and compare against a literal expected line |
Not raised, but recorded:

- A section headed `Usage <seat>`, or `USAGE\t<seat>`, with no `cell:` line is not a USAGE cell for the gate either. The gate reds it as `NOT_RUN`, while the report skips it and exits 0 when another cell is valid (probe 3 additions). That is consistent with the S69-03 rule "exactly as the gate reads it", and the gate is where such a section is caught.
- U+2028 and U+0085 in `model`/`source` are still accepted by both scripts, under the pre-existing `has_bad_text` (noted in the initial review).

### Not verified

- I did not run the full suite. The coordinator said not to, because ticket 65's integration holds the host lock, and I did not take the lock. The full-suite evidence is the seat's F1 at `7cc0e08f` (5 failures, all in the base list) and CI run 44331023638.
- CM7b's Linux result is reasoned, not run; I triggered no CI.
- I checked the seat's eight M1 mutations from the capture (diffs, exits, porcelain) but did not rerun them. They come in through different doors from mine (CM9 to CM14).

```review-verdict
candidate: 7cc0e08fa5cdf2d573c6c00806d59f09d1778d98
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/69-rev01-correction
reviewed_at: 2026-11-18
```

```rework-record
candidate: 7cc0e08fa5cdf2d573c6c00806d59f09d1778d98
round: 2
kind: CORRECTION
verdict: CONVERGENCE_REVIEW_REQUIRED
causes:
```

## Convergence disposition (control plane, 2026-11-18)

The revision01 correction review returned `CONVERGENCE_REVIEW_REQUIRED`: every blocking finding (S69-01 to S69-04) is closed, and the open findings are non-blocking under CodeReview §5 rule B.

| Finding | Class | Carried to |
| --- | --- | --- |
| S69-07 | OUT_OF_SCOPE_HARDENING | the runbook rule (P9 before USAGE is appended, E1 alone after) answers it for wave 3; making the wave-1 receipt checker read informational cells is the wave-4 item "isolated parse failures in the wave-1 scripts" |
| S69-08 | EVIDENCE_DEFECT | the next change of `usage_report.py`: pin on POSIX that the NO_USAGE line goes through the escaping helper |

The control plane notes one error of its own: the correction message said "exit is 2 if any fault occurred", which contradicts R4-2. The seat followed R4-2 and the reviewer judged against it; the sentence is superseded (lesson L-20).

```convergence-disposition
candidate: 7cc0e08fa5cdf2d573c6c00806d59f09d1778d98
reviewer_verdict: CONVERGENCE_REVIEW_REQUIRED
disposition: APPROVED
rule: CodeReview §5 rule B (owner-approved 2026-11-05)
carried:
  - S69-07
  - S69-08
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"). These values become the receipt's `USAGE` cells once this ticket is integrated.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/69-impl` | claude-sonnet-5-5 | 374 | 570152 | 41242772 | 149575 | 41813298 | OVER_OUTPUT,OVER_PROCESSED |
| `seat:ticket-review/69-rev01` | claude-opus-5-5 | 176 | 471742 | 16572474 | 97780 | 17044392 | WITHIN |

The implementation seat covers the first implementation and correction 1, in one seat; the review seat covers both reviews. The implementation seat is over both expectations: output by 19575 tokens (15.1 %) and processed by 17813298 tokens (74.2 %). Facts on record: the seat ran two rounds (185 host messages), the correction reran every cell including the full suite, after the initial review returned four blocking findings. The first round alone was within output (111397) and over processed by 2747493. Over is explained here and does not block integration (owner decision 2026-11-18 "1A"); the rework rounds behind it are what ticket 73 records.
