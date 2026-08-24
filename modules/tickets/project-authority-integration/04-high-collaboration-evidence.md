# Ticket 04 — high-collaboration evidence

| Field | Value |
| --- | --- |
| Ticket ID | PAI-04-HIGH-COLLABORATION-EVIDENCE |
| State | PLANNED / NOT_ADMITTED / NON_DISPATCHABLE |
| Dependencies | PAI-01, PAI-02, and PAI-03 accepted |
| Source specification | Project authority integration SPEC Revision 03, ticket order item 04 |
| Declared source ownership | library/local_orchestration/project_authority/collaboration.py owns PullRequestReadPort and ProviderPolicyReadPort validation/profile admission. |
| Effect boundary | Deterministic fake PR/policy ports only; no provider read, UI action, policy configuration, merge, or credential. |

## Vertical closure reserved

For HIGH_COLLABORATION, prove with fakes that the current ticket PR head equals the candidate,
the base equals project_authority_ref, approval binds that head, ordinary UI bypass is blocked,
and changed heads invalidate approval. PR and CI remain review evidence rather than a second
integration authority. Unsupported or unproved enforcement remains its named finite capability
state.

This leaf is dependency-bound planning only. It cannot be dispatched until a later approved
admission closure names its exact test seam, commands, TDD matrix, preflight, and reviewer
counter-mutation. It grants no provider or repository effect.
