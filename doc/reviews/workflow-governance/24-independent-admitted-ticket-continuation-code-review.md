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

## Closure revision 02 independent review

The additive replacement candidate `e0bbe9e5d9efe5dad1556d186e6dd425b54beec0`
(policy commit `8fd38454d831ef020ad3fd218b288c201c6a827b`) was reviewed by a
separate `gpt-6-sol/high` seat. The six changed paths were within the revised
boundary, the worktree and diff were clean, 81 targeted tests and 237 subtests
passed, and strict mypy passed for the three modified modules. The policy LF digest
matched its profile/test pins. The reviewer independently removed the ticket-ID
comparison in an isolated copy: the mismatched-metadata cell turned red, then green
after restoration.

Conclusion: `APPROVED_SLICE` for a narrowly ticket-scoped Owner-effect wait only.
The actual `IMPLEMENT + PENDING` route requires one Ticket source and matching
ticket/effect metadata; malformed or missing metadata halts, and waiting carries no
new capability, receipt or Host effect. The full ticket remains `BLOCKED`: the
Router's single-ticket state has no trusted shared mainline, dependency graph,
admitted B lane or live revision proof. Do not infer independent B continuation or
integrate the full Closure revision from this partial approval.

## Convergence split and local landing parity

Control commit `0eeef0e6` made Ticket 24 Closure revision03 A-only and preserved the
unmet B continuation in non-dispatchable Ticket 30. The original reviewer accepted
this split without weakening the A evidence or erasing B. The existing control-plane
gate integrated policy and runtime commits separately at `65b0d9b7` and
`af24945f897079f287305d171df618d1dc4d3fc5` after checking the final pin.
An independent second seat compared all six landed Git blobs with reviewed candidate
`e0bbe9e5`; all matched. At the landing SHA, 81 tests and 237 subtests and strict
mypy passed; the worktree and diff were clean. This admits only the Owner-effect
WAIT slice locally. It does not execute an effect or close checklist 02.
