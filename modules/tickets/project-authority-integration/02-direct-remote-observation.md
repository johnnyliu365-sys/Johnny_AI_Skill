# Ticket 02 — direct remote observation

| Field | Value |
| --- | --- |
| Ticket ID | PAI-02-DIRECT-REMOTE-OBSERVATION |
| State | PLANNED / NOT_ADMITTED / NON_DISPATCHABLE |
| Dependency | PAI-01 accepted with its public contract revision frozen |
| Source specification | Project authority integration SPEC Revision 03, ticket order item 02 |
| Declared source ownership | library/local_orchestration/project_authority/observation.py owns DirectRemoteObservationPort and its validated adapter boundary. |
| Effect boundary | Fake/local deterministic observation only until a later exact ticket has owner-authorized live remote authority. |

## Vertical closure reserved

Validate direct observation of the declared repository/ref, preserve repository/ref/SHA/method/
observer/time/digest metadata, and prove REMOTE_TRACKING_CACHE cannot substitute for that
observation. The closure is independently observable through a deterministic fake port and
staleness/race cells, not through a live remote read.

No dispatch is authorized: this leaf has no exact focused test seam or verified command beyond
the approved specification. Its later admission must bind those exact paths, tests, strict-type
preflight, reviewer mutation, task/worktree/branch/receipt/correlation, and fake-only evidence.
It must not infer authority from main, origin, fetch, CI, PR, provider UI, or a process exit.
