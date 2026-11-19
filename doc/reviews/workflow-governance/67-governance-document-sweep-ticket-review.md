# Ticket 67 — rule-only review before dispatch

Ticket: `modules/tickets/workflow-governance/67-governance-document-sweep.md`. Process tier: strict. This rule-only review is outside the `CodeReview.md` §5 count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.

## Revision01 (commit `4cf3f7a0`), independent `ticket-review` seat

**verdict: CHANGES_REQUESTED**

The seat read the ticket, the template, the REQ rows of 2026-11-18 and 2026-11-19, the sweep test, the old lock module and test at `c9af7725^`, and the cards. It ran two sweep simulations from scratch scripts outside the repository: one with the four exemptions removed, one with the new roots and term list. The working tree stayed clean.

| id | severity | finding | revision02 |
| --- | --- | --- | --- |
| S67R-01 | High | Removing the exemptions turns the SPEC's frozen R4-1 sentence red, while the ticket freezes it and forbids new hits | Item 4: `SPEC_R41_FROZEN`, honoured only in the SPEC while its status note is present; pinned by two tests |
| S67R-02 | High | `test_plugin_publication.py` and `test_plugin_payload_boundary.py` pin text the ticket must delete, and are outside the boundary | Both added to `modify`, with the assertions named in item 5; card paths in plain text |
| S67R-03 | High | As a `PATTERNS` row the check would read historical files (live-verification-047 red, `EXPECTED_TOLERATED` from 5 to 19) | Item 1: a separate check, never over historical files; `EXPECTED_TOLERATED` unchanged |
| S67R-04 | Medium | Unstated whether existing patterns read the new roots | Item 2: the existing patterns keep their roots |
| S67R-05 | Medium | Open term list; "pending descriptor", Private Router, `runner-subscriptions`, runner subcommands and "armed runner" prose missed | Item 1: closed regex list, with these added |
| S67R-06 | Medium | `退場` exempted the very AGENTS.md sentence to delete (退場前); `retired` exempted "until it is retired" | Item 1: completed-retirement forms only, with `退場前`/`until`/`before` excluded; injections added |
| S67R-07 | Medium | Pattern d's own `過渡` exemptions left Workflow.md:22 hidden | Item 3: d and e lose their bridge exemptions |
| S67R-08 | Medium | Two required mutations had no test that turns red | TDD 2: a b2 injection and one injection per new root |
| S67R-09 | Medium | "The paragraph states only…" struck still-valid rules in AGENTS.md | Item 5: delete only the last sentence |
| S67R-10 | Medium | Open invitations to write new rules (SKILL wake sentence, runbook, test replacement, containment base) | Item 5: deletion by default, new text only where given; tara2 `runner` listed |
| S67R-11 | Low | Lock restore: comment, `patch` targets, `TelemetryStorageLockPort` assertion and counts unspecified | Item 6: each allowed change named; 32 tests and 11 subtests |
| S67R-12 | Low | The `path-containment` card cites a deleted suite and was outside the boundary | Added to `modify`; names `tests/test_path_containment_short_names.py` |
| S67R-13 | Low | "README directly under a library package" was ambiguous | Item 2: two globs |
| S67R-14 | Low | Removing the only row leaves an empty catalog page that MODULE_CATALOG still links | The page and its MODULE_CATALOG row are deleted |
| S67R-15 | Low | e7 script: two imports still exist; observation list incomplete | Reworded ("four of its imports"); the first red run is authoritative |
| S67R-16 | Low | Free text allowed completion rows that the boundary block forbade | The control plane writes the completion rows |

## Revision02 (commit `71d43e6e`), correction rule-only review by the same seat

**verdict: CHANGES_REQUESTED**

The seat re-ran its simulations with the revision02 rules:
- `RETIRED_SURFACE` finds 38 hits over the 66 swept files, all inside the boundary.
- Removing the exemptions of patterns d and e turns nothing red outside the boundary.
- `EXPECTED_TOLERATED` is unchanged.

13 of the 16 revision01 findings are CLOSED. S67R-07 stays OPEN, and S67R-02 and S67R-10 close only with the follow-ups below.

| id | severity | finding | revision03 |
| --- | --- | --- | --- |
| S67R-07 | (open) | `Workflow.md:22` stays hidden by pattern d's `R4-1` exemption; the observation claiming it red was false | Item 5 names the exact deletion at `Workflow.md:22`; the false observation is removed |
| S67R-17 | Medium | Two SKILL.md hits had no authorized edit | `SKILL.md` added to the general deletion bullet |
| S67R-18 | Medium | The lists of assertions to change were incomplete (tara6; two README pins) | tara6 named; an assertion whose text lies in a deleted sentence is removed and named |
| S67R-19 | High | Deleting readiness items 2-4 turned a fail-closed check into a permissive one | Item 5 gives the exact replacement: no runner or wake capability exists, no automatic effect may be stated, and the honest statement holds unconditionally |
| S67R-20 | Low | No test exercised the exemption | Green case "the live descriptor was retired in wave 3"; mutation "drop the exemption" |
| S67R-21 | Low | The SPEC phrase alone matches no pattern | The injection is the SPEC's R4-1 sentence verbatim |
| S67R-22 | Low | Line versus sentence | The check reports a sentence, with the units and `sentence_of` of `PATTERNS` |
| S67R-23 | Low | "Delete the retired names" was undecidable in the runbook | The exact words are named; 最小派工訊息 is unchanged |

## Revision03 (commit `7f8781a0`), narrow check by the same seat

**verdict: APPROVED**

The seat re-ran the sweep simulation with the revision03 edits applied to a temporary copy, which it then deleted:
- every remaining `RETIRED_SURFACE` hit has an authorized edit;
- the two edited spots produce no hit;
- `EXPECTED_TOLERATED` is unchanged;
- the payload test loses only the token item 5 already expects.

S67R-07 and S67R-17 to S67R-23 are CLOSED.

| id | severity | finding | revision04 |
| --- | --- | --- | --- |
| S67R-24 | Low (note) | The SKILL.md replacement also deleted two rules that still govern the kept `status` and `uninstall` commands: how the runtime root resolves, and never to invoke a bare `johnny-router` name | The replacement text keeps both, in one sentence |

### Control-plane disposition

Revision04 adds one sentence to the exact SKILL.md replacement. The sentence restates the two existing rules the reviewer named; it writes no new rule. Under the smallest-fix practice (L-19), it does not go to another rule-only round. The ticket is ready for dispatch.

## Seat token use

| seat | model | input | cache write | cache read | output |
| --- | --- | --- | --- | --- | --- |
| rule-only review, revision01 | claude-opus-5-5 | 98 | 194381 | 6657194 | 53235 |
| correction rule-only review, revision02 | claude-opus-5-5 | 28 | 41148 | 2851565 | 22631 |
| narrow check, revision03 | claude-opus-5-5 | 14 | 23213 | 1481624 | 8137 |
