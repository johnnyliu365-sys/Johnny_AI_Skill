# Project authority integration — ticket index

| Field | Value |
| --- | --- |
| Feature | project-authority-integration |
| Source specification | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4, Revision 09 |
| Requirement / decision | PRD-20260824-038 / CHG-20260824-038; ADR-20260824-020 |
| Context | doc/context/project-authority-integration/main.md |
| Registry provenance baseline | main at b6353ac5a79ce2fd968862b55184ea04eeeeb1eb |
| Ticket 01 implementation admission baseline | Reviewer-established at same-lifetime dispatch: the exact HEAD SHA of clean current integration main that already contains the approved ticket tree. |
| Index state | ACTIVE / TICKETS_OPENED / NO_DISPATCH |

This index contains direct-child metadata only. It opens no worktree, branch, receipt,
descriptor, runner, host gateway, agent task, remote operation, provider operation, push,
release, deployment, or credential access.

| Ticket | State | Exact dependency | Observable closure |
| --- | --- | --- | --- |
| [01-authority-contract-and-lifecycle.md](01-authority-contract-and-lifecycle.md) | COMPLETED / INTEGRATED at 6df6885ea093f1e37899f5252f8e4a1cc4feadb9 | none | Pure authority contract and lifecycle-reducer boundary |
| [02-direct-remote-observation.md](02-direct-remote-observation.md) | COMPLETED / INTEGRATED at 9b8e82a48b0997fc63deaf04d931e93857d96246 | 01 completed/integrated at 6df6885ea093f1e37899f5252f8e4a1cc4feadb9 | Direct-observation and cache-staleness port boundary |
| [03-gate-push-readback-composition.md](03-gate-push-readback-composition.md) | READY_LOW_MODEL / NOT_DISPATCHED | 01 and 02 integrated | Fake-port gate/push/readback composition |
| [04-high-collaboration-evidence.md](04-high-collaboration-evidence.md) | PLANNED / NOT_ADMITTED | 01 through 03 accepted | Fake PR/provider-policy evidence admission |
| [05-profile-and-bridge-alignment.md](05-profile-and-bridge-alignment.md) | PLANNED / NOT_ADMITTED | 01 through 04 accepted | Profile-scaled review and bridge-state alignment |
| [06-live-provider-repository-qualification.md](06-live-provider-repository-qualification.md) | BLOCKED_OWNER_EFFECT_AUTHORITY | 01 through 05 accepted plus exact owner effect authority | Live provider/repository qualification |
| [07-governance-reference-release.md](07-governance-reference-release.md) | BLOCKED_OWNER_EFFECT_AUTHORITY | 01 through 06 accepted plus exact release authority | Level 1 governance-reference publication |
| [08-cluster-closure.md](08-cluster-closure.md) | PLANNED / NOT_ADMITTED | 01 through 07 accepted | Independent cluster review and release-gate closure |

No row is an implementation dispatch authorization. Tickets 01 and 02 are completed and
integrated. Every remaining leaf is a dependency-bound planning record until it receives its own
exact writable/test seam and the required approval or effect authority. At a later
same-lifetime synchronous dispatch, the reviewer creates the implementation worktree and branch
from clean current integration main that already contains this approved ticket tree, then records
that exact HEAD SHA as the reviewer-established `implementation-admission-baseline` in the
dispatch, return, and independent-review evidence. A receipt, live descriptor, and host gateway
are explicitly NOT_REQUIRED. Those cross-lifetime controls remain separate and do not block the
synchronous lane. Ticket 01's source candidate starts from that runtime-bound SHA; neither this
ticket's registry provenance SHA nor any source-specification SHA may be used as a source-diff
start point. This rule keeps later documents-only ticket corrections from making an implementation
baseline stale. Its named `implementation-scope-evidence` is the sorted, duplicate-free union of
the tracked `git diff --name-only` paths from that SHA and
`git ls-files --others --exclude-standard`; it must equal Ticket 01's four declared paths, with no
ticket document or any other path. The tracked diff alone is intentionally insufficient when the
candidate creates untracked paths.
