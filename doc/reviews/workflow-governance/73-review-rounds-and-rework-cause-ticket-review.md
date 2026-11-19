# Ticket 73 — rule-only review before dispatch

Ticket: `modules/tickets/workflow-governance/73-review-rounds-and-rework-cause.md`. Process tier: strict. A rule-only review is outside the `CodeReview.md` §5 count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.

## Revision01 (commit `ecb66083`), independent `ticket-review` seat

**verdict: CHANGES_REQUESTED**

The seat read the ticket against the post-76 texts: the templates, `CodeReview.md` §3 to §5 with ticket 74's anchors, `rule-process-tier`, the REQ rows, the scripts and their README, and the existing review records. It modified nothing.

It confirmed four points:
- The new report is the owner's L-12 decision, so it does not count as a smallest-fix breach.
- `integrate.py` ignores any fence other than `review-verdict` and `convergence-disposition`.
- The block and the report name no provider or model.
- The backfill is possible from the existing records.

| id | severity | finding | revision02 |
| --- | --- | --- | --- |
| S73R-01 | High | The exit rule contradicted R4-2 (red before fault) | Item 4 states R4-2's order; TDD 3 has both cases |
| S73R-02 | High | The cause mapping was neither total nor exclusive, so real records could not be backfilled | Causes come from every finding except `OUT_OF_SCOPE_HARDENING`, one cause per class; the dispatch clause is dropped |
| S73R-03 | Medium | The verdict domain, the meaning of "final", and the cross-check were undefined | Five verdicts; causes are empty if and only if `APPROVED` or `CONVERGENCE_REVIEW_REQUIRED`; final is the last round's verdict as recorded; the cross-check is a red |
| S73R-04 | Medium | No mapping from record to ticket | One record per ticket; the ticket id is the file name up to its first `-`; rounds are counted in order of appearance |
| S73R-05 | Medium | Pre-dispatch ticket reviews would carry blocks and count as rounds | The block is in code-review records only; ticket reviews count in no round |
| S73R-06 | Medium | `kind` was not tied to the pre-dispatch label; a `CHANGE_DETECTED` return was forced into `INITIAL` | `kind` copies the label; a new kind `RETURN` with `candidate` a commit or `none`, placed before the first review section; `round` is separate from §5's count |
| S73R-07 | Medium | It was unclear who writes the block | The reviewer writes it; the control plane writes `RETURN` blocks; the implementation seat writes the backfill |
| S73R-08 | Medium | The block grammar and the output lines were underspecified | Field order, single keys, candidate form, no leading zero, cause list form, and both output lines are exact |
| S73R-09 | Low | A record without a block, and an unclosed fence, had no exit | Both are reds |
| S73R-10 | Medium | The backfill list was stale, and ticket 70's return was missing | Ten records are named; the two `RETURN` rounds are named with their source lines; 71 and 73 get blocks in their own reviews |
| S73R-11 | Low | "integrate tests pass unchanged with the new block" could not hold | A new test compares `integrate.check_review` with and without the block |
| S73R-12 | Low | Stale baseline and the claim "integrate reads only review-verdict" | Baseline after ticket 76; integrate reads `review-verdict` and `convergence-disposition` |
| S73R-13 | Low (note) | The README introduction and its script list are pinned | The introduction becomes "Twelve"; `test_gate_contract.py` joins the boundary |
| S73R-14 | Low | No `Process tier:` line | `Process tier: strict.` added |
| S73R-15 | Low (note) | The 禁止修改 row was wider than the forbid lines | The row now matches the block |
| S73R-16 | Low (note) | The ticket lacks the template rows for closure revision, strict checker, profile and XSS | Not changed; pinning the template is wave-4 work |
| S73R-17 | Low (note) | The end-of-wave review point is wave-4 work | Not carried by this ticket |

## Seat token use

| seat | model | effort | input | cache write | cache read | output |
| --- | --- | --- | --- | --- | --- | --- |
| rule-only review, revision01 | claude-opus-5-5 | high | 56 | 92600 | 2560344 | 28521 |
