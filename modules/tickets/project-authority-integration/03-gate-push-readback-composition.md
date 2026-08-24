# Ticket 03 — gate, push, and readback composition

| Field | Value |
| --- | --- |
| Ticket ID | PAI-03-GATE-PUSH-READBACK-COMPOSITION |
| State | PLANNED / NOT_ADMITTED / NON_DISPATCHABLE |
| Dependencies | PAI-01 and PAI-02 accepted |
| Source specification | Project authority integration SPEC Revision 05, ticket order item 03 |
| Planning baseline | main at b6353ac5a79ce2fd968862b55184ea04eeeeb1eb |
| Declared source ownership | library/local_orchestration/project_authority/integration.py owns injected NonForcePushPort orchestration. |
| Effect boundary | Fake NonForcePushPort and fake direct-readback only; no target remote mutation, push, force, credential, or provider invocation. |

## Vertical closure reserved

Compose the frozen pure reducer with fake non-force push and direct readback so gate success is
LOCAL_INTEGRATED only, while exact post-push remote SHA equality is required for
AUTHORITY_INTEGRATED and every absent/failed/ambiguous/mismatched readback remains
PUSH_UNCONFIRMED. A race, rejection, or mismatch fails closed without force or cache fallback.

This leaf is not admitted until its exact focused test seam, deterministic commands, strict-type
preflight, and reverse mutations are committed in an approved ticket revision. It creates no
remote, provider, receipt, descriptor, runner, agent task, branch, or external effect.
