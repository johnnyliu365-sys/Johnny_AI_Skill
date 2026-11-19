# Ticket 76: initial review of closure revision03

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/76-seat-model-and-effort-bound.md` revision03, read at the candidate. The blob on `cp/wave3` differs only in the state-row digest. |
| Candidate | `78810fa6ca29fe6463efadc530547c52d93b4916` (`cp/wave3-76-seat-binding`). Commits `9ed4ae71` and `78810fa6`, additive on base `aa5d1d0d`. The remote ref equals the candidate. |
| Dispatch | `JAS-76-1.yaml` at `cp/wave3`. Recomputed sha256 `277328602a04edfe8b3847cb58a4126966eb3dd1c4ee895e139990458dcbe426` matches. The candidate's lint with `--ticket` gives `LINT PASS`, exit 0, including R8. |
| Label | Initial review of closure revision03, as labelled by the control plane before dispatch |
| Reviewer | `ticket-review` seat, run id `R76-1`, worktree `.worktrees/76-seat-binding-review` (detached at the candidate, porcelain empty before and after) |
| References | `CodeReview.md` §2 to §5; `skills/johnny-project-takeover/references/review-checks.md` (defect categories, test truthfulness, reviewer counter-mutation) |
| Interpreter | `C:/Temp/claude/jas-venv/Scripts/python.exe`, `PYTHONUTF8=1`, one pytest at a time. I ran no output-reducing wrapper. Every pytest output was written in full to a file and read from there. |

## Findings

No finding blocks approval. Every row below is either an accepted interpretation or a process note. Each one names the smallest fix or where it should be carried, as §4 asks.

| id | §4 class | severity | location | finding | evidence |
| --- | --- | --- | --- | --- | --- |
| S76-01 | OUT_OF_SCOPE_HARDENING | Info | `dispatch_lint.py` `check_seat_binding`; scripts README R8 paragraph | **The seat's reading: a repeated top-level `model:` or `effort:` is invalid** (STATEMENT 18). Item 5 does not say this.<br>**Accepted.** It fails closed. It closes the "first match" door, where a later, contradictory value would pass unseen. It agrees with "one item" and with the gate's `USAGE_FIELD_REPEATED` stance. The docstring, the README and a test all state it.<br>**Smallest fix:** none needed. If the owner wants it frozen, add one sentence to item 5 the next time a ticket touches R8. | CM01 (first-value-only) turns `test_a_field_given_twice_is_invalid` red. |
| S76-02 | OUT_OF_SCOPE_HARDENING | Info | `dispatch_lint.py` `lint()` and `main()` | **The seat's other R8 readings** (STATEMENT 19), all accepted:<br>- R8 lines come after the R1 to R6 lines and before R7. This matches item 5's "after the per-line rules". R7 is not a per-line rule, and its text is unchanged.<br>- Fence tracking is the same expression the per-line rules use.<br>- Indented, list-item and fenced `profile:`, `model:` and `effort:` fields are not top-level, which matches "column 0, outside a code fence".<br>- `model_name:` is another field.<br>**Smallest fix:** none. | CM02 (column 0 dropped), CM03 (fence ignored) and CM04 (order swapped) are each red. `SeatBindingProcessTests.test_r8_runs_with_ticket_and_the_digest_rule_still_runs` pins `R8` then `R7`. |
| S76-03 | OUT_OF_SCOPE_HARDENING | Low | `JAS-76-1.yaml` cell T1 (control-plane dispatch, not the candidate) | **The dispatch's T1 asserted `exit=0`, which the base could not reach.** I extracted the six T1 files at `aa5d1d0d` and ran mypy `--strict --python-version 3.11`: `Found 20 errors in 2 files`.<br>**The seat's typing-only fix is acceptable** (STATEMENT 23):<br>- Both files are in the boundary block.<br>- `evidence_gate.py` does `import subprocess` (line 74), so patching `subprocess.run` patches the same module attribute as `evidence_gate.subprocess.run`.<br>- The spies' new explicit keywords (`capture_output`, `input`, `env`) are exactly what the only `subprocess.run` call site in `evidence_gate.py:435` passes.<br>- `setattr` on the fixture spec is equivalent to the `**override` call.<br>- No assertion changed.<br>**Smallest fix:** the control plane checks each T1-type cell at the base before writing an `exit=0` assert into a dispatch. | Base mypy: 20 errors, exit 1. Candidate mypy on the same six files: `Success`, exit 0. `tests/test_state_file_templates.py` is also clean under strict. The four ticket test files at the candidate: 507 passed, 1 skipped (symlink, pre-existing), 865 subtests. |
| S76-04 | OUT_OF_SCOPE_HARDENING | Info | historical dispatches `JAS-65`, `66`, `67`, `68`, `69`, `70` and `72` | **These dispatches now also print the two R8 "without" lines.** JAS-67 fails on R8 alone, and the others already failed R5. No test or gate lints them. The STATEMENT names this (24), and item 5 allows the change for files that carry `profile:`.<br>**Smallest fix:** none. They are closed records. | The candidate's lint over all ten committed dispatches: JAS-74-1, 75-1 and 76-1 `LINT PASS`. The rest show `R8 profile: without model:` and `R8 profile: without effort:`. |
| S76-05 | OUT_OF_SCOPE_HARDENING | Info | `76-seat-binding-out/OBS.txt`, `CASES.txt` | **The observation run and the case list are captures in the out directory, not run cells.** E1 therefore does not bind them to a tool digest or an exit code. This matches the dispatch, which lists them as STATEMENT items, not cells.<br>**Smallest fix:** none. I reran the observation independently (check 1.6). | My rerun matches STATEMENT 20, line for line. |

## Per-check table

| # | check | result | evidence |
| --- | --- | --- | --- |
| 1.1 | Value grammar (item 1) | PASS | **Same item regex everywhere.** `usage_report.py`, `evidence_gate.py` and `dispatch_lint.py` each use `[A-Za-z0-9][A-Za-z0-9._-]*`, ASCII and `fullmatch`.<br>**A list** splits on `,`, every item must match, and `len(set) == len` refuses repeats. Comparison is plain `==`, so it is case-sensitive.<br>**Tests:** blank, empty, `a, b`, `a ,b`, `a,`, `,a`, `a,,b`, `a,a` and `a,b,a` are each `USAGE_FIELD_INVALID` in the gate and exit 2 in the report. So are a leading `-`, `.` or `_`, and non-ASCII.<br>**Counter-mutations:** CM06 (repeats accepted) and CM08 (model unchecked) are red. |
| 1.2 | Expectation shape; an unfilled template is a schema break (item 2) | PASS | **Shape.** `ENTRY_KEYS` is exactly model, effort and the two limits. A missing or unknown key is `InputFault`, exit 2. Model and effort must each be a `str` holding one item.<br>**Unfilled template.** `<host-model>` breaks the grammar, giving exit 2 (`test_the_unfilled_template_is_a_schema_break` and the template cross-check). The cross-check fills both placeholders with the fixture values (`a-model`, `high`) and gets `WITHIN`.<br>**Key order** is pinned by `UsageExpectationTemplateTests`.<br>**Counter-mutation:** CM10 (a list accepted in the expectation) is red. |
| 1.3 | `effort:` line position and backward compatibility (item 3) | PASS | **Gate.** `USAGE_FIELDS` puts `effort` after `model`, and `effort` is in `USAGE_OPTIONAL_FIELDS`. The line out of place is `USAGE_FIELD_ORDER`, exit 1. A cell without it gives `cells=2 defects=0` with no new output.<br>**Report.** The line out of place is exit 2.<br>**Template.** The receipt template has `effort: <effort>` directly after `model:`, and this is pinned.<br>**Older receipts.** All eight older USAGE receipts parse under the new grammar (check 1.6).<br>**Counter-mutations:** CM07 (effort mandatory) and CM12 (position unenforced) are red. |
| 1.4 | Report line and verdict order (item 4) | PASS | **Line format.** The line is `<seat> <profile> model=<list> effort=<list or UNRECORDED> output=<n> processed=<n> <verdict>`.<br>**Word order** is fixed: MODEL_MISMATCH, EFFORT_MISMATCH, OVER_OUTPUT, OVER_PROCESSED, EFFORT_UNRECORDED. `WITHIN` appears only when the list is empty, and `UNKNOWN_PROFILE` returns before any word.<br>**Reds.** `is_red` treats only `WITHIN` and `EFFORT_UNRECORDED` alone as not red.<br>**Faults.** Reds print first, and a fault without a red is exit 2.<br>**Mutation evidence.** The seat's five M1 mutations are each red (10, 6, 1, 43 and 2 failures). My CM09 (the overlap shape: red skipped when the verdict ends in EFFORT_UNRECORDED), CM11 (UNKNOWN_PROFILE not alone), CM13 (prefix model compare) and CM14 (EFFORT_UNRECORDED first) are each red. |
| 1.5 | R8: four exact lines and their order (item 5) | PASS | **Through the CLI:**<br>- missing model and effort print `R8 profile: without model:` then `R8 profile: without effort:`, exit 1;<br>- `model: "a b"` with an empty effort prints `R8 model: invalid` then `R8 effort: invalid`;<br>- a CRLF dispatch with `model: High` and `effort: "xhigh"` gives `LINT PASS`.<br>**Without a `profile:` field**, R8 is silent.<br>**Counter-mutations:** CM01 to CM05 are each red. CM05 (R8 without a profile) turns ticket 75's "without `--ticket` as before" test red, so that guard is live. |
| 1.6 | Observation run (TDD 1) | PASS | I reran the candidate report with the repository expectation on the eight named receipts.<br>- Every cell prints `EFFORT_UNRECORDED`.<br>- Ticket 67's two implementation cells print `MODEL_MISMATCH` (`claude-opus-5-5`, processed 31831073 and 55068170).<br>- No implementation cell of tickets 65, 66, 68, 69, 70 or 72 mismatches.<br>- The OVER words come from the unchanged limits.<br>- Exits are 1, 1, 0, 1, 1, 0, 1 and 1, as in STATEMENT 20. |
| 2 | No shipped file names a provider or model | PASS | I ran `git grep -iE "claude-\|sonnet\|opus\|haiku\|anthropic\|openai\|gpt-\|gemini"` at the candidate over the payload trees named in `.claude-plugin/plugin.json`: `commands`, `skills`, `template` and `library/*`. It finds nothing.<br>None of the diff's added lines in the shipped trees carries such a name.<br>Two tests pin this for both templates. |
| 3 | Host values only in unshipped files | PASS | Host model names appear only in:<br>- `doc/handoffs/2026/workflow-governance/usage-expectation.json`;<br>- the runbook's REVISION_04 entry, which item 2 requires;<br>- tests.<br>None of the three is in the payload allowlist. |
| 4 | Runbook REVISION_04; registry unchanged | PASS | **REVISION_04 entry.** It records the observed host values as observed data, not dispatch policy, assumes elevated equal to review, and names the `xhigh` against `high` difference as an owner calibration item.<br>**Token-use section.** It carries item 6's three statements.<br>**Registry.** The diff does not touch the provider-neutral registry table.<br>**Revision row.** It reads `2026-11-19 / REVISION_04`. |
| 5 | Boundary (`git diff aa5d1d0d 78810fa6`) | PASS | Thirteen files changed. Each is a `modify` or `create` line of the boundary block. No forbidden path is touched (`library/`, `AGENTS.md`, `Workflow.md`, `CodeReview.md`, the skill references). |
| 6 | The seat's interpretations and typing fixes | ACCEPTED | See S76-01, S76-02 and S76-03.<br>The existing-test changes (STATEMENT 21) are each forced by the new entry keys, the new fixture line or the new report line, or are optional-field skips. None weakens an assertion. |
| 7 | Mutation evidence and counter-mutations | PASS | **The seat's M1.** Five mutations, each red, each restored with porcelain empty; the restored files pass (93 and 98).<br>**My counter-mutations.** Fourteen, CM01 to CM14, run in a `git clone --no-hardlinks` of the candidate. Each targets a door different from M1: first match, column 0, fence, order, gating, gate repeats, gate optionality, gate model grammar, overlap masking in `is_red`, expectation lists, UNKNOWN_PROFILE alone, effort position, prefix compare, and word order.<br>**Result.** All 14 are red for the intended test, each restored with porcelain empty.<br>**Capture.** Full unfiltered output with diffs is in `CM.txt` beside this file. |
| 8 | The receipt is true | PASS | **Return as returned.** `RETURN.md` differs from `RETURN.as-returned.md` only by the appended USAGE cell.<br>**E1 rerun.** The candidate's gate with the dispatch's E1 arguments gives `cells=7 defects=0`, exit 0, on both copies.<br>**Usage report on the receipt.** `model=claude-sonnet-5-5 effort=high output=99639 processed=21192435 WITHIN`, exit 0. 234 + 539108 + 20653093 = 21192435.<br>**USAGE cell against the host transcript.** The seat's transcript holds 110 unique message ids. All 211 assistant records say `claude-sonnet-5-5` / `high`. The sums equal the cell exactly.<br>**F1.** The failure set equals the five registered base failures.<br>**CI.** `gh run view 44496858941` gives head `78810fa6`, conclusion success, both `test (windows)` and `test (linux)` success.<br>**Commits.** Both trailers name Claude Sonnet 5.5, the model that did the work. |
| P0 | Strong types | PASS | `Seat.effort: str \| None`. `Limits` holds typed strings. JSON values are narrowed with `isinstance` at the boundary. There is no `Any` and no `type: ignore`. |
| — | Full suite | NOT RERUN | I relied on the seat's F1, run under the host lock and matching the registered list, and on CI run 44496858941, green on both jobs. I did not take the host lock. |

## Residue

- **Run id `R76-1`.** Under `.worktrees/76-seat-binding-review-scratch/R76-1`: the candidate clone, the base extract, the mypy caches, the lint fixtures, and the drivers `R76-1_cm.py` and `R76-1_usage.py`. All were removed, together with the empty scratch directory I created.
- **Left in this directory:** `REVIEW.md` and `CM.txt`.
- **Processes:** no background process remains. `PROCESSES_LEFT=0`.

```review-verdict
candidate: 78810fa6ca29fe6463efadc530547c52d93b4916
verdict: APPROVED
round: initial
closure_revision: revision03
reviewer: ticket-review seat R76-1 (claude-opus-5-5, high)
reviewed_at: 2026-11-19
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/jas76s1` | claude-sonnet-5-5 | 234 | 539108 | 20653093 | 99639 | 21192435 | WITHIN |
| `seat:ticket-review/R76-1` | claude-opus-5-5 | 110 | 206988 | 7662340 | 38428 | 7869438 | WITHIN |

Both seats ran with their model and effort named. The implementation seat ran `claude-sonnet-5-5` at `high`; the reviewer confirmed it on all 211 assistant records. The review seat ran `claude-opus-5-5` at `high`. The implementation seat handed back twice as INCOMPLETE, because its turn was cut while CI ran. The control plane told it the CI result, and it finished in a third pass. Its token use above covers all three passes, and is within the expectation.

### Disposition of the non-blocking findings (control plane)

| Item | Class | Disposition |
| --- | --- | --- |
| S76-01, S76-02: the seat's R8 readings (a repeated `model:` or `effort:` is invalid; R8 lines print after R1 to R6 and before R7; fences tracked as for the per-line rules; only column-0 fields are top-level) | Info | Accepted; counter-mutations pin each reading |
| S76-03: the dispatch's T1 asked for exit 0, which the base could not reach (20 strict errors at `aa5d1d0d`); the seat's typing-only fix is accepted | Low (control plane) | From the next dispatch on, the control plane runs each exit-0 cell at the base before it writes the assertion |
| S76-04: the closed dispatch files JAS-65 to 72 now also print R8 lines | Info | Closed records; no action |
| S76-05: OBS.txt and CASES.txt are captures, not receipt cells, as the dispatch said | Info | No action |
