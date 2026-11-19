# Ticket 75 — independent review, closure revision03, initial review

| field | value |
| --- | --- |
| ticket | `modules/tickets/workflow-governance/75-own-tickets-follow-the-harness.md` revision03, read at the candidate |
| candidate | `dd10fca6720d61e81adde7c8cd9cc8879815c6f6` (branch `cp/wave3-75-own-tickets`), one commit, parent `ed5605935f377729e36f681877ca87620cfcebdb` |
| review label | initial review of closure revision03 (`CodeReview.md` §5, rule-review-label) |
| reviewer | `ticket-review` seat, claude-opus-5-5, run id `R75-1`, worktree `.worktrees/75-own-tickets-review` detached at the candidate |
| dispatch | `doc/handoffs/2026/workflow-governance/dispatch/JAS-75-1.yaml`, sha256 `2cbb06108d7033455b47da4477983be2b15fb1dea7ae52c030f4dc4b0f85b393` (recomputed from the file and from the `d3d93907` blob; equal) |
| receipt | `.worktrees/75-own-tickets-out/RETURN.md` (with the control-plane USAGE cell) and `RETURN.as-returned.md` |
| references applied | `CodeReview.md` §2 to §5; `review-checks.md` (Required dimensions; Defect categories rows Missing values, Token parsing/comparison, Error-code consistency, Exception behavior, Test truthfulness; Reviewer counter-mutation points 1 to 5) |
| environment | `C:/Temp/claude/jas-venv` (Python 3.11), `PYTHONUTF8=1`; every pytest run directly, without an output-reducing wrapper; `-rfE` lists every failed cell and subtest |
| scratch | `.worktrees/75-own-tickets-review-scratch/R75-1/` (removed after the review; the commands and outputs quoted here are the record) |

## Findings

| id | §4 class | severity | location | finding | evidence |
| --- | --- | --- | --- | --- | --- |
| S75-01 | `OUT_OF_SCOPE_HARDENING` | Info | `skills/johnny-project-takeover/scripts/dispatch_lint.py` `check_dispatch_digest` (`cell.count(DIGEST_TOKEN)`, `DIGEST_RUN`) | The token has no leading boundary and the run has no trailing class beyond `[0-9A-Za-z]`: `x`+`dispatch=sha256:<hex>`, `<hex>_tail` and `<hex>-tail` all pass with the right digest. Item 2 asks for exactly one `dispatch=sha256:` substring and ignores everything after the alphanumeric run, so this is the frozen contract, not a defect. A wrong digest still cannot pass, so no unsafe dispatch is admitted. | Case run `R75-1_cases`: `prefixed-token xdispatch`, `match-underscore-tail`, `match-hyphen-tail` each exit 0, `LINT PASS`. Smallest fix if wanted: a wave-4 sentence in item 2's successor requiring a non-alphanumeric character (or cell start) before the token; no change to this ticket. |
| S75-02 | `OUT_OF_SCOPE_HARDENING` | Info | `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (control-plane tool, outside the boundary) | The P9 checker treats the control-plane `USAGE` cell as a run cell, so P9 rerun on the receipt *after* the USAGE append reports 7 defects (no candidate/capture/exit/tool_digest/raw block on that cell). P9 on the as-returned receipt is 0 defects, and E1 (`evidence_gate.py`, the authoritative gate, run last) gives `cells=7 defects=0` on the appended receipt. Not a candidate defect; it only matters if anyone reruns P9 after the append. | P9 rerun on a copy of `RETURN.as-returned.md` with its captures: `receipt defects: 0`, exit 0. On a copy of `RETURN.md`: `[FAIL] USAGE ... receipt defects: 7`, exit 1. Smallest fix: run P9 before the USAGE append (as the seat did), or teach that checker to skip `cell: USAGE`; carry to the control plane, not this ticket. |

No `IMPLEMENTATION_DEFECT`, `EVIDENCE_DEFECT`, `TICKET_DEFECT` or `REQUIREMENT_CHANGED` finding. No blocking finding.

## Per-check table

| # | check | result | evidence |
| --- | --- | --- | --- |
| 1a | R7 pass cases: digest then end of cell, ` (`, `(`, `; `, `（` | PASS | Each a separate process of the candidate script (`python -I dispatch_lint.py <dispatch> --ticket <t>`): exit 0, stdout `LINT PASS`, stderr empty. |
| 1b | Which cell: the first row whose first cell is exactly `狀態` | PASS | first row wrong digest + later row right → exit 1 `R7 ... found <other> (a different digest)`; first row empty + later right → exit 1 `found an empty state cell`; first right + later wrong → exit 0. Decoys `狀態說明`, `前狀態`, third-column 狀態, no leading pipe are pinned by `test_only_a_row_whose_first_cell_is_exactly_the_state_cell_counts`. |
| 1c | Absent row / empty row | PASS | no row → exit 1 `found no state row`; `\| 狀態` without a second pipe → exit 1 `found no state row`; empty cell, blank cell, `\| 狀態 \|` → exit 1 `found an empty state cell`. |
| 1d | Exactly one `dispatch=sha256:` | PASS | none (`PLANNED`) → exit 1 `found no dispatch=sha256:`; two separated and two glued (`dispatch=sha256:dispatch=sha256:<hex>`) → exit 1 `found 2 dispatch=sha256: in the state cell`. |
| 1e | Token boundary, lengths 63 and 65, `<hex>x`, empty run | PASS | 63 → `(63 characters, not 64)`; `<hex>0` → `(65 characters, not 64)`; `<hex>x` → `(65 characters, not 64)`; nothing after token → `found nothing (0 characters, not 64)`; full-width digit `０` ending the run → 63 characters. All exit 1, one `R7` line. See S75-01 for the leading side. |
| 1f | Upper-case hex | PASS | all upper-case of the right digest and one upper-case letter → exit 1 `(not 64 lower-case hex digits)`. |
| 1g | Every R7 line names expected and found | PASS | Every red line has the form `R7 state row: expected dispatch=sha256:<sha of the dispatch bytes>, found <...>`. |
| 1h | Unreadable and non-UTF-8 ticket: exit 3, empty stdout, before R1 to R7 | PASS | absent path, a directory, bytes `ff fe 00 ff` → exit 3, stdout empty, stderr `usage:` line + error line. A dispatch with R2 and R5 violations plus a non-UTF-8 ticket → exit 3, stdout empty. Code: ticket read sits before `lint()` in `main`. |
| 1i | No output change without `--ticket` | PASS | Differential run, base `ed560593` script vs candidate, no `--ticket`, on all 780 tracked `*.yaml`/`*.yml`/`*.md` files plus 9 edge files (CRLF, CR-only, mixed, BOM, NEL/U+2028, non-UTF-8, empty, 2100-char line, CRLF fence), each without and with `--chat-words note`, plus four usage-error argvs: `runs=1582 files=789 diffs=0` on exit and stdout; stderr equal once the `USAGE` string's new ` [--ticket <ticket-file>]` suffix is removed. The read change (`read_text` → `read_bytes().decode`) is output-neutral because `lint()` uses `splitlines()`. |
| 1j | Control-plane spot check, repeated | PASS | Candidate script, main checkout (HEAD `d3d93907`, porcelain empty before and after): `JAS-75-1.yaml --ticket` ticket 75 → `LINT PASS`, exit 0; same with the `d3d93907` blobs → exit 0; `JAS-74-1.yaml --ticket` ticket 75 → `R7 state row: expected dispatch=sha256:1066881111e9…3bfb, found 2cbb06108d70…b393 (a different digest)`, `LINT FAIL (1)`, exit 1. |
| 1k | Observation run, repeated | PASS | Seven stored files against their tickets in the main checkout: JAS-65 exit 1 R5=20; JAS-66 exit 1 R5=19; JAS-67 exit 0; JAS-68 exit 1 R5=16; JAS-69 exit 1 R5=18; JAS-70 exit 1 R5=19; JAS-72 exit 1 R5=17; R7=0 and other rules=0 on all seven. Equals receipt item 28 line for line. `.gitattributes` keeps `doc/handoffs/*/*/dispatch/*` `-text` (`i/lf w/lf`), so the digest is checkout-independent. |
| 1l | Script text | PASS | Module docstring, `USAGE`, README usage line, README:7 sentence and the README section all name R7 and `--ticket`; `test_the_usage_line_and_docstring_name_the_ticket_option_and_r7` pins two of them. |
| 2a | Four target rows | PASS | `Closure revision`, `Strict checker`, `Profile / resource`, `XSS classification` are byte-identical to `template/modules/tickets/TEMPLATE.md:13-16`, placed after 實作語言 as there. |
| 2b | Exact 狀態 row form and eight states | PASS | Row text equals item 1's form character for character: `` `<STATE>`; dispatch=sha256:<64 lower-case hex> (`<repository-relative dispatch path>`)（<optional note>） ``. Note lists `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `SUPERSEDED`, `REVIEW_APPROVED`, `INTEGRATED`, `CONVERGENCE_REPLANNED`; digest written at dispatch, none for a never-dispatched ticket; names R7. |
| 2c | Two deviations | PASS | Note states digest kept after `INTEGRATED` (owner decision 2026-11-19 "A"; the target keeps it "while a dispatch is pending") and receipt path kept in the Agent Context binding row. |
| 2d | §2 citation | PASS | Heading now identical to target `template/modules/tickets/TEMPLATE.md:40` (`CodeReview.md` §2 + review-checks "Defect categories"); `§2.1` gone. |
| 2e | Kept reverse-mutation wording, no `Process tier:` line, other sections unchanged | PASS | 完成定義 still carries `反向突變證據` (line 117), no `紅燈輸出`; `grep "Process tier"` on the template: none. Section outline before/after identical apart from the 11-line offset; boundary block, 角色指派 and 前端組合 hunks untouched (diff has three hunks: rows, note, heading). |
| 3 | README holds only the generic order and naming | PASS | Five steps match item 3 (base precedes the recording commit; digest written in the control plane's checkout, not the leaf; lint with `--ticket` then dispatch only on exit 0; `<ticket>-<n>.yaml` with `<n>` the dispatch revision; recorded file never rewritten). Added lines grep for `JAS`, `workflow-governance`, `2026`, `ticket 7`, `doc/handoffs`, `wave`, `owner`: no hit. |
| 4 | Boundary (`git diff ed560593 dd10fca6`) | PASS | `--name-status`: M `modules/tickets/TEMPLATE.md`, M `skills/johnny-project-takeover/scripts/README.md`, M `skills/johnny-project-takeover/scripts/dispatch_lint.py`, M `tests/test_gate_dispatch_lint.py`; each is a `modify =` line; nothing under `template/`, `library/`, `AGENTS.md`, `Workflow.md`, `CodeReview.md`, `references/`, no other gate script, no existing ticket. One commit, parent `ed560593`, no amend. Test diff removes only the docstring line it rewords (R1-R6 → R1-R7); no existing assertion changed. |
| 5a | Implementer mutations (M1), repeated | PASS (3/3 red) | On a disposable copy of the two candidate blobs, whole test file, no `-x`: upper-case accepted → 2 failed (`test_one_upper_case_digit_is_red`, `test_upper_case_hex_is_red_even_when_it_is_the_right_digest`); missing digest skipped → 4 subtests of `test_a_cell_without_the_token_is_red`; first-16 compare → subtests 16, 17, 32, 63 of `test_the_whole_digest_is_compared_not_a_prefix`. Same cells as M1.txt. |
| 5b | Reviewer counter-mutations (six, other doors) | PASS (6/6 red) | A *first match* (read the last 狀態 row) → `test_the_first_state_row_is_the_one_read`. B *copy* (digest over the newline-translated decoded text, not the bytes) → `test_the_digest_is_of_the_file_bytes`. C *overlap-masking* (drop the doubled-token check) → `test_two_tokens_in_the_cell_are_red_even_when_both_match`. D token boundary (`[0-9A-Za-z]{0,64}`, ignore what follows the 64th char) → `test_a_run_that_continues_with_a_letter_is_red` + 2 subtests of `test_a_run_of_63_or_65_characters_is_red`. E exit class (non-UTF-8 ticket decoded with replacement → red instead of 3) → `test_a_non_utf8_ticket_exits_3_with_empty_stdout`. F cell identity (`狀態 in first`) → 2 decoy subtests. Each restored; sha256 of the restored file equals `532e7028…7d55`; restored run 74 passed, 94 subtests. |
| 6a | P1, T1 | TRUE | P1 rerun: `74 passed, 94 subtests passed`, exit 0. T1 rerun: `mypy --strict --python-version 3.11` on script and test: `Success: no issues found in 2 source files`, exit 0. |
| 6b | tool_digest | TRUE | sha256 at the candidate: `dispatch_lint.py` `532e7028…7d55`, `index_pins.py` `63eff436…b7ccf`, `receipt_fence_check.py` `8b3f845c…441c`, as in every cell. P9's checker lists `dispatch_lint.py` in `SCRIPTS` (line 17), so the seat's note that P9 needed it is true. |
| 6c | C1 | TRUE | `gh run view 44481492675`: headSha `dd10fca6…`, conclusion `success`, `test (linux)` and `test (windows)` both `success`. |
| 6d | F1 | TRUE | Rerun of `python -m pytest tests -q -p no:cacheprovider -rfE` in this worktree under the host lock `C:/Temp/claude/jas-fullsuite.lock` (absent before; acquired by `mkdir` with owner `R75-1` at 16:18:14+08:00, no other pytest process on the host at that moment, released at 16:35:57 after the owner matched): `5 failed, 3274 passed, 22 skipped, 7773 subtests passed`, exit 1. The five failures are the receipt's five, by name, and all five are in the registered base list `C:/Temp/claude/jas48_F1_base.txt`; zero new red. Worktree porcelain empty afterwards, HEAD still the candidate. |
| 6e | E1 and P9 | TRUE | E1 rerun on a copy of the appended receipt, `--repo` this worktree, `--evidence-root` the out directory: `cells=7 defects=0`, exit 0 (as the control plane reports). P9 rerun on the as-returned receipt: 0 defects, exit 0 (see S75-02 for the appended copy). |
| 6f | Receipt statements | TRUE, one weak spot | Items 9 to 28 match my case run and observation run (digests differ only because my fixture differs). Item 29 matches the test diff. Item 33's process listing at lock acquisition was cut at 20 lines, as the seat itself says; the lock protocol, the CI run and my own F1 rerun make the result independent of that listing, so it is noted, not a finding. Item 35: `.worktrees/75-own-tickets-scratch/` exists and is empty, as stated, and no `jas75s1` file remains in the out directory. |

## Review-checks dimensions

- Strong typing: `str | None`, `list[str]`, `bytes`; no `Any`; mypy strict clean (P0 source type holds).
- Logic and boundary: the cell parser, token count, run extraction and three-step classification match item 2 case for case; order of checks gives one R7 line per run.
- Error-code consistency: 0 / 1 / 3 only; no R7 path can raise (every branch returns a list), and a bad ticket is exit 3 with empty stdout, decided before any rule.
- Security and performance: one file read each, one sha256; no new external effect.
- Test truthfulness: each item-2 case and each category-table case has its own test; nine mutations (three implementer, six reviewer) all red on the intended cell.
- XSS / privileged JS, Agent authority, profile, POC: not applicable (a command-line script and a markdown template; no UI, no agent control, no deployment).

```review-verdict
candidate: dd10fca6720d61e81adde7c8cd9cc8879815c6f6
verdict: APPROVED
round: initial
closure_revision: revision03
reviewer: ticket-review seat (claude-opus-5-5), run R75-1
reviewed_at: 2026-11-19
blocking_findings: none
carried: S75-01 (OUT_OF_SCOPE_HARDENING, Info), S75-02 (OUT_OF_SCOPE_HARDENING, Info)
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/jas75s1` | claude-sonnet-5-5 | 146 | 190937 | 9515278 | 56665 | 9706361 | WITHIN |
| `seat:ticket-review/R75-1` | claude-opus-5-5 | 84 | 326439 | 4534073 | 33800 | 4860596 | WITHIN |

Both seats ran with their model and effort named: the implementation seat ran `claude-sonnet-5-5` at `high` on all 199 messages, and the review seat ran `claude-opus-5-5` at `high`.

### Disposition of the non-blocking findings (control plane)

| Item | Class | Disposition |
| --- | --- | --- |
| S75-01: R7's token has no leading boundary, and its run ends at the first non-alphanumeric character, as item 2 asks; a wrong digest still fails | OUT_OF_SCOPE_HARDENING, Info | Wave 4 |
| S75-02: the P9 checker reads an appended USAGE cell as a run cell | OUT_OF_SCOPE_HARDENING, Info | Already the runbook rule since ticket 69 (S69-07): P9 judges the receipt as returned, and after the append only E1 is rerun |
