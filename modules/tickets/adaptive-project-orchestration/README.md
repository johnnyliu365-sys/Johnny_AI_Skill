# Adaptive Project Orchestration — Router Phase Tickets

> Approved Router scope: [adaptive-project-orchestration.md](../../spec/adaptive-project-orchestration.md)
> revision 05 / AC-12 through AC-17 and the Router portions of AC-05 through AC-10.
> This set does not authorize initialization, staging, packaging or target-project effects.

## Serial closure order

| Ticket | Observable closure | State | Dependency |
| --- | --- | --- | --- |
| [01-route-instruction-contract](01-route-instruction-contract.md) | Every Router decision carries one versioned skill reference and one exact expected typed return; technical halts use the Profile's router-control fallback. | `COMPLETE / APPROVED / INTEGRATED` | `5c3445f` |
| [02a-shared-context-lifecycle-gate](02a-shared-context-lifecycle-gate.md) | Architecture-stage draft/revise/seal and change-control-only revision admission; later roles are exact sealed-revision readers. | `COMPLETE / APPROVED / INTEGRATED` | `9bf7d340` / `PRG-20260815-469` |
| [02b-agent-context-lease-invalidation-gate](02b-agent-context-lease-invalidation-gate.md) | One implementation-owner, ticket-bound Agent Context lease; correction invalidates and ticket switch closes the old view before a fresh identity exists. | `COMPLETE / APPROVED / INTEGRATED` | `9e3d92bc` / `PRG-20260815-477` |
| [02c1-artifact-tree-resolution-gate](02c1-artifact-tree-resolution-gate.md) | Generic bounded topology and exact one-path resolution for every declared workflow artifact family. | `COMPLETE / APPROVED / INTEGRATED` | `5b887c72` / `PRG-20260815-487` |
| [02c2-requirement-retirement-archive-lineage](02c2-requirement-retirement-archive-lineage.md) | One-to-one active PRD/CHG pairing, retirement and archive-only reachability. | `COMPLETE / APPROVED / INTEGRATED` | `701df3e` / R02C2A closed |
| [02c2a-requirement-lineage-source-gate-closure](02c2a-requirement-lineage-source-gate-closure.md) | One bounded test-only ACX6 guard covers every R02C2-owned `contracts.py` declaration/helper/import boundary and proves its own three rejection mutations. | `COMPLETE / APPROVED / INTEGRATED` | `701df3e` / `PRG-20260815-496` |
| [02c3-bounded-library-selection](02c3-bounded-library-selection.md) | One selected archive/reusable-library partition path resolves to one exact eligible leaf without discovery or sibling loading. | `COMPLETE / APPROVED / INTEGRATED` | `93a66a4` / `PRG-20260815-505` |
| [03-model-role-readiness-wake](03-model-role-readiness-wake.md) | Exact SPEC readiness and architecture-owner sleep/wake decision kernel. | `COMPLETE / APPROVED / INTEGRATED` | `aa313bf` / `PRG-20260815-513` |
| `04-low-model-ticket-admission` | Four-way low-model decomposition/admission decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R03 approved/integrated |
| `05-ui-design-source-routing` | Optional design-source capability decision kernel. | `CANDIDATE / NON_DISPATCHABLE` | R04 approved/integrated |
| `06-router-policy-acceptance` | Integrated Profile/Router acceptance and metadata-only serialization closure. | `CANDIDATE / NON_DISPATCHABLE` | R01-R05 approved/integrated |
| [project-isolation](project-isolation/README.md) | Revision 06 project-isolation admission partition. | `UPSTREAM_DECISION_REQUIRED / NON_DISPATCHABLE` | revision `01`; SHA-256 `68508a80a36ff23a2515bb1cee5ff8d5810ca707620ebe9a52f5fe948a8f25a2`; exact Revision 06 contract completion |
| [revision-07](revision-07/README.md) | Revision 07 fresh admission partition. | `UPSTREAM_DECISION_REQUIRED / NON_DISPATCHABLE` | revision `01`; SHA-256 `d0654c93909f3dca942d0fa10927a8a42fac297732d8d2f1cc13e3bf3ab30eed`; exact Revision 07 Port contracts required |

R02C1, R02C2, R02C2A, R02C3 and R03 are complete. R04 is the next serial candidate, but it
remains `CANDIDATE / NON_DISPATCHABLE` until its own approved ticket freeze, handoff and receipt
registry exist. Candidate labels are not implementation authority.

## Revision 06 partition

Revision 06 is a separate direct-child ticket partition. It does not reopen the completed Router
phase. Its admission decision is reachable only through
[`project-isolation/README.md`](project-isolation/README.md).

Revision 07 is separately indexed at [revision-07/README.md](revision-07/README.md). It neither
rewrites the Revision 06 decision leaf nor reopens the Router phase.

## Direct-child ticket partitions

| ID | Kind | Revision | Digest | Lifecycle | Exact reference |
| --- | --- | --- | --- | --- | --- |
| `PROGRESS-ARTIFACT-TREE` | `PARTITION_INDEX` | `r03` | `sha256:1a25ee27a16d06c1ce531c7d6472528d1788d03c1391bd2487bf7df7abe881f5` | `PLANNED` | [`progress-artifact-tree/README.md`](progress-artifact-tree/README.md) |
