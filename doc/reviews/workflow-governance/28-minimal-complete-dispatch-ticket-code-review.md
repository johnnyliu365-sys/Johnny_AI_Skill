# Ticket 28 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/28-minimal-complete-dispatch-ticket.md` |
| Candidate | `85b6bd6e207465c6da8baa7e296e75756170154d` |
| Reviewer | Separate `gpt-6-sol/high` seat; read-only candidate review |
| Conclusion | `CHANGES_REQUESTED`; not integrated |

The candidate changed only the ticket template and its new targeted test file; its
worktree and diff were clean. The 15 targeted tests passed. Independent reverse mutation
moved the Expected slot into an inert HTML comment. All 15 tests still passed, so the
test suite did not prove that the template retained a usable Expected field. The
fixed frontend scenario also used self-asserted constants rather than a filled-ticket
binding. This is a blocking test-evidence defect under the ticket's own requirement
that removing any key slot turns the named cell red.

Narrow correction remains on the original ticket and branch: assert the field's
fillable section/bullet semantics and exercise a filled-ticket scenario. No Host
dispatch admission was implemented or proved; even a corrected template candidate
cannot by itself close checklist item 03.

## Correction review and convergence

The additive correction `5b3df22133099f935f72107ba494cc532e6ac9fe` changed
only the targeted test file. Eighteen tests passed; the original HTML-comment
mutation now turned the named cell red, and the filled-ticket scenario exercised
real template labels. A distinct reviewer mutation removed the active Expected
bullet and placed a copy inside an inert Markdown fenced example. All 18 tests
still passed: the static checker treated example text as a fillable slot.

Conclusion: `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`. This was the
second review under the same closure revision; no automatic third correction is
authorized. The control plane must repair the acceptance/evidence method before
another implementation attempt. No candidate was integrated or pushed.
