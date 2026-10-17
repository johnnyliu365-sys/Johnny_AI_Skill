# Ticket 24 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/24-independent-admitted-ticket-continuation.md` |
| Candidate / base | `953c2ceac34ae065bc8f5cbc095cba90f5783d55` / `b899d8ce13753bbcaab3d7298416dd70dc4fa53c` |
| Reviewer | separate `gpt-6-sol/high` read-only review seat, `.worktrees/skill-improvement-02-review` |
| Conclusion | `CHANGES_REQUESTED`; no integration or checklist completion |

## Findings

1. The new test names ticket A as a SQL/irreversible effect, but calls `TICKET_DISPATCH_REQUIRED` and observes `TICKET_DISPATCH_CONFIRMATION_REQUIRED`. This is dispatch approval, not the specified Owner-effect wait. Current POC Profile declares no `EXTERNAL_DECISION_REQUIRED` route. The ticket's explicit stop condition therefore applies until a real scoped route or existing capability is proven; the test must not be relabeled as success.
2. Ticket B is built from its own synthetic pending descriptor; no shared mainline state, dependency evidence, or A wait is carried into the B decision. The test does not establish either a dependent-B refusal or that completion of B leaves the mainline open.
3. The candidate changes no `router-control.md` wording. That reference is digest-pinned in `library/workflow_router/profile.py` and `tests/test_workflow_router.py`; current ticket 24 does not allow repinning those files. The implementer correctly removed an attempted unpinned policy edit and reported this boundary.

## Evidence and disposition

- `python -m pytest tests/test_autonomous_collaboration.py -q`: 20 tests and 20 subtests passed; this green result covers the narrower dispatch path only.
- `git diff --check b899d8ce...953c2cea`: pass.
- Reviewer reverse mutation in an isolated review worktree made confirmed dispatch suspend in the real Router path: the new test turned red at its `ADVANCE` assertion; restoration turned it green. Review worktree was clean afterward. This proves the B assertion discriminates dispatch continuation, not the SQL scenario.
- Preserve candidate and history. Architecture Owner must first confine the actual Owner-effect wait and mainline/dependency evidence to the approved authority; if that needs new SPEC/permission, route only that item through Change Control. Other admitted checklist work continues.
