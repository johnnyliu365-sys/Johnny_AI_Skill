# Ticket 75 — rule-only review before dispatch

Ticket: `modules/tickets/workflow-governance/75-own-tickets-follow-the-harness.md`. Process tier: strict. This rule-only review is outside the `CodeReview.md` §5 count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.

## Revision01 (commit `22610af5`), independent `ticket-review` seat

**verdict: CHANGES_REQUESTED**

The seat read the ticket, both ticket templates, dispatch_lint and its tests, the REQ rows of 2026-11-19, the dispatch-digest note, the seven stored dispatch files and their state rows, and `.gitattributes`, and took tickets 67 and 74 as landed. It ran `dispatch_lint.py` seven times, read-only. Its findings on the record itself:
- all seven blob digests equal their state rows;
- `.gitattributes` keeps the dispatch files' bytes exact;
- the README note is honest;
- nothing outside the boundary pins the template or the lint's output.

| id | severity | finding | revision02 |
| --- | --- | --- | --- |
| S75R-01 | High | "Takes the target grammar" while giving a third form; the state vocabulary and the deviations were unstated | The exact repository form is given, with the target's eight states and the two deliberate deviations stated |
| S75R-02 | Medium | R7's token boundary was undefined | Which cell, exactly one token, a 64-character run of lower-case hex, the rest ignored; each case gets its verdict |
| S75R-03 | Low | Empty row versus absent row | Both are R7 red (exit 1); only an unreadable or non-UTF-8 ticket is exit 3 |
| S75R-04 | Medium | "Exit 3 as R4-2 sets" was the wrong citation | Cites dispatch_lint's own classification (README:7, :30); empty stdout, decided before R1 to R7; the older spec:171 against README:7 difference goes to wave 4 |
| S75R-05 | Low | README:7, the usage line and `USAGE` would go stale | All three are named |
| S75R-06 | Medium | The `Process tier:` template line contradicts ticket 74, which leaves it to wave 4 | Dropped from this ticket |
| S75R-07 | Medium | Six of the seven stored dispatch files fail R5, which predates them, so "each passes" was wrong | The observation expects no `R7` line, JAS-67 exit 0, and the other six exit 1 on R5 only |
| S75R-08 | Low (note) | The target's "紅燈輸出" slot contradicts `implementation-tdd.md` | The template keeps its reverse-mutation wording |
| S75R-09 | Low | `JAS-NN.yaml` lets a recorded file be rewritten by a later revision | New files are `JAS-<NN>-<n>.yaml`; a recorded file is never rewritten |
| S75R-10 | Low (note) | The base, the checkout `--ticket` reads, and ticket 75's own dispatch were unstated | All three are stated |

## Revision02 (commit `c5636f19`), correction rule-only review by the same seat

**verdict: CHANGES_REQUESTED**

S75R-01 to S75R-10 are CLOSED. The edits introduced two findings, each with an exact fix.

| id | severity | finding | revision03 |
| --- | --- | --- | --- |
| S75R-11 | Medium | Item 3 sent repository-specific text (the `JAS-` prefix, the seven files, ticket 75's own dispatch) into the plugin's script README, which ships to target projects and knows no target project | The README section keeps only the generic order and the R4-1 naming `<ticket>-<n>.yaml`. The repository facts go into the control-plane "Dispatch digests" note. |
| S75R-12 | Low | The category table said "two `dispatch=` tokens", while item 2 counts `dispatch=sha256:` | The table says "two `dispatch=sha256:` tokens" |

### Control-plane disposition

Revision03 applies the reviewer's exact fixes and changes nothing else. Under the smallest-fix practice (L-19), it does not go to a third rule-only round, as with tickets 67 and 74. Ticket 75 is ready for dispatch after ticket 74 is integrated.

## Seat token use

| seat | model | input | cache write | cache read | output |
| --- | --- | --- | --- | --- | --- |
| rule-only review, revision01 | claude-opus-5-5 | 76 | 103811 | 3905535 | 30756 |
| correction rule-only review, revision02 | claude-opus-5-5 | 8 | 14417 | 440050 | 4691 |
