# Ticket 74 — rule-only review before dispatch

Ticket: `modules/tickets/workflow-governance/74-wave3-rule-texts.md`. Process tier: strict. This rule-only review is outside the `CodeReview.md` §5 count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.

## Revision01 (commit `04b2e11a`), independent `ticket-review` seat

**verdict: CHANGES_REQUESTED**

The seat read the ticket, the template, the REQ rows 26–30, the source findings (S61-03, S61-07, C10, S72-05) and every target section, and took ticket 67 as landed. It modified nothing.

| id | severity | finding | revision02 |
| --- | --- | --- | --- |
| S74R-01 | High | The residue rule would have the seat delete its allocated worktree, branch and receipt directory | Rule 2 covers only what the seat starts for its run; the worktree, branch and receipt directory are handed back |
| S74R-02 | High | Resume rules contradict the worktree, correction and FRESH_BRANCH_REQUIRED rules | S61-03 leaves this ticket and goes to wave 4 (it needs `AGENTS.md` and `template/`) |
| S74R-03 | High | The pre-dispatch rule review could use up the §5 initial review | Rule 3: the rule-only review is outside the §5 count |
| S74R-04 | High | The light tier allowed unreviewed edits to gate-read records and decisions | Rule 3: records are append-only, not tickets, and edit no gate-read field or recorded decision |
| S74R-05 | Medium | The strict list omitted rule-bearing files | Rule 3: the list adds SKILL.md, scripts and their README, both ticket templates, `.agents/` rules, registered failures, the governance SPEC and rule-pinning tests |
| S74R-06 | Medium | "Candidate" named two different commits; E1 would mismatch | Rule 1: the receipt's `candidate:` and E1 are the cells' commit; the review and queue candidate is the receipt-adding commit |
| S74R-07 | Low | "Digests only" contradicted `index_pins.py` | Rule 1 uses the source wording |
| S74R-08 | Medium | Rule 7 paths conflicted with AGENTS.md and forbidden `template/` | Dropped with S61-03 (wave 4) |
| S74R-09 | Medium | S72-05 wording deviated from its source and collided with the envelope rule | Rule 7 uses the source wording and applies to the dispatch file only |
| S74R-10 | Medium | "Known debt" bypassed §4 and §5 carry destinations; "severity Low" was undefined | Rule 4: rule-B non-blocking findings only; carry to the destinations §4 and §5 allow |
| S74R-11 | Medium | Rule 1 had no section; a rule's block was undefined; `rule B` failed in Chinese | Rule 1 gets a new last section; a block runs from anchor to anchor or heading; `rule B` or `規則 B`; the Workflow §3 sentence is given |
| S74R-12 | Low | Review seats return a review record, not a STATEMENT | "STATEMENT or review record" |
| S74R-13 | Low | CRR is not a conclusion; resume answers were unrecorded choices | Rule 6 reworded; resume moved to wave 4 |
| S74R-14 | Low | The runbook is "profile data", not policy | Rule 5 moves to `implementation-authority.md`; the runbook leaves the boundary |
| S74R-15 | Low | Collision with ticket 67's rewrites | Revision02 states a post-67 placement check before dispatch |

## Revision02 (commit `71d43e6e`), correction rule-only review by the same seat

**verdict: CHANGES_REQUESTED**

All 15 revision01 findings are CLOSED (S74R-04 and S74R-11 with new findings). The seat modified nothing.

| id | severity | finding | revision03 |
| --- | --- | --- | --- |
| S74R-16 | Medium | Rule 2 forbade removing untagged residue, while kept sentences require a seat to clear caches in its own worktree | Rule 2: files the seat's own commands write inside its worktree are its own, and it removes them |
| S74R-17 | High | The records definition made the control plane's own state-row and index transitions, and ticket writing, into tickets | Records include the transitions a governance rule assigns to the control plane, and writing or revising a ticket (reviewed under that ticket's tier) |
| S74R-18 | Medium | `dispatch_ref` is a bridge-route field, so rule 7 could have no scope | Rule 7 applies to the dispatch file whose digest the state row carries (R4-1); the test term is `dispatch file` |
| S74R-19 | Medium | Mid-list placement made rule 6's block swallow the rule B bullets, so its term test could not go red | Rule 6 goes after the last bullet of §5 |
| S74R-20 | Low | No template line, and open tickets lack the tier line | The tier line applies to tickets opened after this rule; the template line and the open tickets are wave-4 work |
| S74R-21 | Low | Undecided where appended `USAGE` cells go | Rule 1: appended after the candidate is set, in a record commit |
| S74R-22 | Low | The repository puts anchors above headings, which would empty a new section's block | In a new section, the anchor goes below the heading |

## Revision03 (commit `48f8b91d`), narrow check by the same seat

**verdict: CHANGES_REQUESTED**

S74R-16 to S74R-22 are CLOSED. The edits introduced one Medium finding and two notes, each with an exact replacement phrase.

| id | severity | finding | revision04 |
| --- | --- | --- | --- |
| S74R-23 | Medium | The closed list of control-plane transitions omitted `BLOCKED` and `SUPERSEDED` (discovery-change.md) | "They include …", plus `BLOCKED` or `SUPERSEDED` under a requirement change |
| S74R-24 | Low | The Workflow §3 sentence was stricter than rule 3 | "Every ticket opened after this rule names its process tier." |
| S74R-25 | Low | Caches versus "no seat removes an untagged one" | "… an untagged one outside its allocated worktree" |

### Control-plane disposition

Revision04 applies the reviewer's exact phrases and changes nothing else. Under the smallest-fix practice (L-19), it is not sent for a fourth rule-only round. Ticket 74 is ready for dispatch once ticket 67 is integrated and the post-67 placement check named in the ticket passes. The implementation review then judges the rule texts under `CodeReview.md`.

## Seat token use

| seat | model | input | cache write | cache read | output |
| --- | --- | --- | --- | --- | --- |
| rule-only review, revision01 | claude-opus-5-5 | 74 | 107376 | 3880208 | 35183 |
| correction rule-only review, revision02 | claude-opus-5-5 | 12 | 135594 | 679821 | 12656 |
| narrow check, revision03 | claude-opus-5-5 | 10 | 15110 | 726438 | 4161 |
