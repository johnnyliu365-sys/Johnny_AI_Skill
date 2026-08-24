# Project authority integration — ticket index

| Field | Value |
| --- | --- |
| Feature | project-authority-integration |
| Source specification | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4, Revision 04 |
| Requirement / decision | PRD-20260824-038 / CHG-20260824-038; ADR-20260824-020 |
| Context | doc/context/project-authority-integration/main.md |
| Registry baseline | main at ecbee4319ff6f7ceab878a3ddce5471154571890 |
| Index state | ACTIVE / TICKETS_OPENED / NO_DISPATCH |

This index contains direct-child metadata only. It opens no worktree, branch, receipt,
descriptor, runner, host gateway, agent task, remote operation, provider operation, push,
release, deployment, or credential access.

| Ticket | State | Exact dependency | Observable closure |
| --- | --- | --- | --- |
| [01-authority-contract-and-lifecycle.md](01-authority-contract-and-lifecycle.md) | READY_LOW_MODEL / NOT_DISPATCHED | none | Pure authority contract and lifecycle-reducer boundary |
| [02-direct-remote-observation.md](02-direct-remote-observation.md) | PLANNED / NOT_ADMITTED | 01 accepted | Direct-observation and cache-staleness port boundary |
| [03-gate-push-readback-composition.md](03-gate-push-readback-composition.md) | PLANNED / NOT_ADMITTED | 01 and 02 accepted | Fake-port gate/push/readback composition |
| [04-high-collaboration-evidence.md](04-high-collaboration-evidence.md) | PLANNED / NOT_ADMITTED | 01 through 03 accepted | Fake PR/provider-policy evidence admission |
| [05-profile-and-bridge-alignment.md](05-profile-and-bridge-alignment.md) | PLANNED / NOT_ADMITTED | 01 through 04 accepted | Profile-scaled review and bridge-state alignment |
| [06-live-provider-repository-qualification.md](06-live-provider-repository-qualification.md) | BLOCKED_OWNER_EFFECT_AUTHORITY | 01 through 05 accepted plus exact owner effect authority | Live provider/repository qualification |
| [07-governance-reference-release.md](07-governance-reference-release.md) | BLOCKED_OWNER_EFFECT_AUTHORITY | 01 through 06 accepted plus exact release authority | Level 1 governance-reference publication |
| [08-cluster-closure.md](08-cluster-closure.md) | PLANNED / NOT_ADMITTED | 01 through 07 accepted | Independent cluster review and release-gate closure |

No row is an implementation dispatch authorization. Ticket 01 alone has a complete
admission closure; every other leaf is a dependency-bound planning record until it receives its
own exact writable/test seam and the required approval or effect authority. At a later
same-lifetime synchronous dispatch, the reviewer establishes the exact ticket, worktree, branch,
task, and correlation binding from this committed tree and Git metadata; a receipt, live
descriptor, and host gateway are explicitly NOT_REQUIRED. Those cross-lifetime controls remain
separate and do not block the synchronous lane.
