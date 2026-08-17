# Plugin Distribution ticket registry

| Field | Binding |
| --- | --- |
| SPEC / Context | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` Revision 02 / `ctx-plugin-distribution-r02` |
| Planning baseline | `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Profile | `plugin-distribution-poc-r02` v2 / POC / one Luna xhigh lane / no helper |
| Environment | Windows x64 / CPython 3.11.9 / `mypy --strict`; exact implementation worktree and baseline bind per selected ticket |
| Control owner and reviewer | Senior task `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b` |
| State | `REPLANNED / LIVE_ALLOCATION_REQUIRED / NOT_DISPATCHED` |

`LOW_MODEL_CANDIDATE` means the closure fits Luna xhigh after the Senior binds one exact owner,
task, worktree, branch, implementation baseline and receipt into the selected ticket and reruns
schema/type preflight. It is not `READY_LOW_MODEL` before that commit. Tickets are serial unless
the dependency graph and distinct live owners both permit parallel work. No ticket authorizes
heartbeat, polling, automation, publication, Router binding or writes to original SourceProjectA.

| Order | Ticket | Sole closure | Admission | Dependencies |
| --- | --- | --- | --- | --- |
| 01 | [Private Git plugin](01-private-git-plugin.md) | Historical skill-only package | `DONE / REVISION_01_ONLY` | — |
| 02 | [Runtime dependency lock](02-runtime-dependency-lock.md) | Exact environment-derived lock validates | `LOW_MODEL_CANDIDATE` | — |
| 03 | [Payload manifest](03-payload-manifest.md) | One canonical allowlisted manifest validates | `LOW_MODEL_CANDIDATE` | 02 |
| 04 | [Profile-bound CLI preflight](04-profile-cli-preflight.md) | Typed preflight returns before effect | `LOW_MODEL_CANDIDATE` | 02 |
| 05 | [Project runner registry](05-project-runner-registry.md) | One project has at most one runner | `LOW_MODEL_CANDIDATE` | 04 |
| 06 | [Receipt Git subscription](06-receipt-git-subscription.md) | One receipt admits only its committed handoff | `LOW_MODEL_CANDIDATE` | 05 |
| 07 | [Senior review queue](07-senior-review-queue.md) | FIFO batch and dependency cluster are deterministic | `LOW_MODEL_CANDIDATE` | 06 |
| 08 | [Host-wake gate](08-host-wake-gate.md) | Missing/uncertain host remains fail-closed | `HIGH_ASSURANCE_REQUIRED` | 07 |
| 09 | [Deterministic bundle](09-deterministic-bundle.md) | Identical input emits identical ZIP bytes | `LOW_MODEL_CANDIDATE` | 03 |
| 10 | [Router composition](10-router-composition.md) | CLI operation composes exactly one bounded action | `LOW_MODEL_CANDIDATE` | 04–09 |
| 11 | [Install transaction](11-install-transaction.md) | Attempt-owned install succeeds or rolls back | `LOW_MODEL_CANDIDATE` | 10 |
| 12 | [Uninstall transaction](12-uninstall-transaction.md) | Receipt-owned removal is complete and idempotent | `LOW_MODEL_CANDIDATE` | 11 |
| 13 | [Telemetry report](13-telemetry-report.md) | Explicit request exports token/cost data only | `LOW_MODEL_CANDIDATE` | 04 |
| 14 | [Scripted Vita qualification](14-scripted-vita-qualification.md) | Disposable no-model qualification preserves original | `LOW_MODEL_CANDIDATE` | 08, 12, 13 |
| 15 | [Real-role Vita smoke](15-real-role-vita-smoke.md) | One owner-controlled live smoke proves result or exact block | `HIGH_ASSURANCE_REQUIRED / OWNER_EFFECT_REQUIRED` | 14 |

Writable source paths do not overlap between active leaves. Ticket 15 is a Senior-controlled
verification gate, not a Luna coding dispatch.
