# Ticket 35 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/35-parent-finding-status-closure.md` |
| Baseline | `39e4ac9722fef77c2cdf684ae404943a41b7f79f` |
| Initial candidate / correction | `f65120b970afcd44fa8f9efa8bca70e04c088a34` / `5c6b33a4416dda13a7b82cc5a5dbe3be52acfd96` |
| Reviewer | Separate `gpt-6-sol/high` seat in isolated worktree |
| Conclusion | Initial `CHANGES_REQUESTED / IMPLEMENTATION_DEFECT`; correction `APPROVED` |

Initial public `build_document` probe found two different-path parents sharing declared ID `P` both remained `APPROVED`, contrary to Ticket 35 Work §2. Same-ticket additive correction marks every duplicate declaration unreadable before parent propagation. The reviewer reran the public path: both duplicate parents are excluded, required child and unrelated ticket remain visible. Mutating the duplicate predicate (`>1` → `>2`) made the named test red; restoration made it green. Initial reviewer-owned mutations disabling required-child rejection and OPEN Finding rejection each made their named cells red and were restored to green. No other blocking finding remained.

The final candidate changed only the four ticket-declared paths. `python -m pytest tests/test_ticket_status_pipeline.py tests/test_ticket_status_template.py -q` returned 121 passed and 205 subtests; strict mypy on the two production modules passed, `git diff --check` was clean, and reviewer worktree was clean. Root cherry-picked both reviewed commits into `control/skill-improvement-35-land`, confirmed all four Git blobs equal the final reviewed candidate, and the existing control-plane mutation gate returned `INTEGRATED` at `215a599f5333ce18a81ea23f2b30b16c2766f18b`. No push or publication occurred.

The delivered capability is an owner-visible status projection, not a formal authorization decision. It does not authenticate referenced evidence or close a Ticket in Router/Review. Checklist 07 remains unchecked until those separate obligations are proven.
