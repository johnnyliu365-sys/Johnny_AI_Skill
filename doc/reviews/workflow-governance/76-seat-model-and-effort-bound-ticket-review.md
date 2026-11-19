# Ticket 76 — rule-only review before dispatch

Ticket: `modules/tickets/workflow-governance/76-seat-model-and-effort-bound.md`. Process tier: strict. This rule-only review is outside the `CodeReview.md` §5 count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.

## Revision01 (commit `4a3d447b`), independent `ticket-review` seat

**verdict: CHANGES_REQUESTED**

The seat was started with its model and effort named (`opus`, `high`), as ticket 76 will require. It took tickets 74 and 75 as landed, read the scripts, tests, templates, runbook and REQ rows, and checked one host transcript for the `"model"` and `"effort"` fields. It modified nothing and confirmed these as passing:
- the exit codes follow R4-2;
- there is no contradiction with ticket 74;
- the four test files exist;
- the registry's `xhigh` is as stated;
- the observed Sonnet and Opus bindings of tickets 65 to 72 are as stated.

| id | severity | finding | revision02 |
| --- | --- | --- | --- |
| S76R-01 | High | Two output tokens for "unrecorded", and no report line form | The exact usage_report line is given; evidence_gate prints nothing new |
| S76R-02 | Medium | Verdict order and combinations undefined | Fixed order: MODEL_MISMATCH, EFFORT_MISMATCH, OVER_OUTPUT, OVER_PROCESSED, EFFORT_UNRECORDED. `WITHIN` only when none applies. |
| S76R-03 | Medium | Value grammar open | One item matches `[A-Za-z0-9][A-Za-z0-9._-]*`. A list is joined by `,` with no blanks and no repeats. A breach is `USAGE_FIELD_INVALID` in the gate (exit 1) and a schema break in the report (exit 2). |
| S76R-04 | Medium | R8 not decidable | Top-level fields outside fences, with non-empty values that obey the grammar. R8 runs with or without `--ticket`, and its problem lines are given. |
| S76R-05 | Medium | `RECEIPT.TEMPLATE.md` lacked the `effort:` line and was outside the boundary | Added to the boundary, with the line and its placeholder |
| S76R-06 | Low | `template/README.md:56` would go stale | Added to the boundary |
| S76R-07 | High | Model names in a shipped template contradict the runbook's provider neutrality and REVISION_02 | The template holds placeholders. The host values go into the unshipped `doc/handoffs/2026/workflow-governance/usage-expectation.json`, recorded in the runbook as observed host data (REVISION_04). |
| S76R-08 | Low | `implementation-elevated` was called "observed", but no elevated seat has run; the calibration item named only one profile | Elevated is assumed equal to `ticket-review` until measured; the calibration item covers all three profiles |
| S76R-09 | Low (note) | R8 changes ticket 75's "without `--ticket` as before" regression for files with `profile:` | Stated as an allowed change that the STATEMENT names |
| S76R-10 | Low (note) | The figure 55 million was the correction seat; receipts were not named | Both 67 figures are given; the observation names the exact receipt directories; 71 has none |

## Revision02 (commit `b7bd2161`), correction rule-only review by the same seat

**verdict: APPROVED**

S76R-01 to S76R-10 are CLOSED. The seat checked the observation claims against the named receipts and found them true; ticket 67's two implementation cells processed 31831073 and 55068170 tokens. The edits introduced three Low gaps that do not block dispatch, each with an exact sentence.

| id | severity | finding | revision03 |
| --- | --- | --- | --- |
| N1 | Low | The R8 problem lines were open-ended, and list or quote handling in a dispatch value was unstated | The four lines are given exactly, in order; one item, optionally in one pair of double quotes; a list is invalid |
| N2 | Low | The unfilled template's placeholders break the value grammar, while the existing cross-check expects `WITHIN` | An unfilled template is a schema break; the cross-check fills both placeholders first |
| N3 | Low | `UNKNOWN_PROFILE` with an absent `effort:` line was undefined | `UNKNOWN_PROFILE` stands alone |

### Control-plane disposition

Revision03 adds only the reviewer's three sentences. The ticket is ready for dispatch after ticket 75 is integrated.

> Commit identifiers: the reviews ran on the local commits `6b738170` (revision01) and `90a620a4` (revision02). Those commits were rebased onto the ticket 67 integration before they were pushed, with no change in content, and became `4a3d447b` and `b7bd2161`. The record names the pushed commits.

## Seat token use

| seat | model | effort | input | cache write | cache read | output |
| --- | --- | --- | --- | --- | --- | --- |
| rule-only review, revision01 | claude-opus-5-5 | high | 60 | 139319 | 3071707 | 22638 |
| correction rule-only review, revision02 | claude-opus-5-5 | high | 8 | 16929 | 436959 | 5053 |
