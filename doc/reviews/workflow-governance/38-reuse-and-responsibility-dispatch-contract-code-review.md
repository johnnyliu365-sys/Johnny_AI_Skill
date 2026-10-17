# Ticket 38 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/38-reuse-and-responsibility-dispatch-contract.md` |
| Baseline | `6927c539edf1377d365d5a360f02066a2737c73f` |
| Initial candidate / correction head | `f95face63650331083dfe5a7e9d630d8f2f39114` / `3557bc208c2a1ecc37bd0af18f5544aa15ef775c` |
| Reviewer | Separate `gpt-6-sol/high` seat in isolated review worktree |
| Conclusion | Initial `CHANGES_REQUESTED`; one bounded correction review `APPROVED` |

The initial template named new-file responsibility but allowed a directory-wide `create`
without listing each expected code/script file. Its fictional sample also used `.tmp/`,
which this repository does not ignore and would pollute the worktree. The same implementer
corrected both under the original ticket: even a directory/pattern grant now requires an
exact per-file responsibility/consumer/AC/dependency entry, and temporary output is stated
as an OS temp path outside the Git worktree. A final sample-only correction made its budget
count (`product 1/2`) agree with the two declared created files.

The reviewer independently changed the second exact filename in the filled-ticket sample
back to a directory-only entry: the named filled-ticket test turned red, then returned green
after restoration. A separate mutation moved the temp output root into the worktree: the
outside-worktree assertion turned red, then returned green. At the final candidate,
`python -m pytest tests/test_ticket_template_contract.py -q` passed 35 tests;
`git diff --check` passed. The diff from baseline is exactly
`modules/tickets/TEMPLATE.md` and `tests/test_ticket_template_contract.py`; both implementation
and review worktrees were clean.

The existing document-mutation gate returned `INTEGRATED` at the exact reviewed candidate
`3557bc208c2a1ecc37bd0af18f5544aa15ef775c`. This closes the template slice only.
Neither these static tests nor the template prove that a Host rejects an incomplete filled
ticket before dispatch or that semantic coupling inside a code/script file can be detected.
Checklist 03 and 11 therefore remain unchecked. No target project, push or release changed.
