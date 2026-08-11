# Local Orchestration Adapter and Detachable Installer — Ticket Set

> Approved SPEC: [local-orchestration-installer.md](../../spec/local-orchestration-installer.md) (`SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X`). Planning this set does not authorize source/test changes.

## Delivery objective

Deliver a Windows per-user local control plane that owns every installed component, preserves company projects, retains only metadata-only runtime state, and removes its owned payload plus receipt-proven Agent UI registrations with one normal uninstaller invocation.

## Reuse selection

| Selected module | Revision | Public contracts / patterns used | Explicit boundary |
| --- | --- | --- | --- |
| `workflow-router-poc` | `d94d8d5` | `ProjectId`, `RouterEvent`, `ContextView`, completion/return contracts and guarded-integration fail-closed pattern | The existing fake adapters are not a production host/Git implementation; no other module is imported by default. |

## Ticket status and dependency order

| Ticket | User-observable capability | State | Dependency |
| --- | --- | --- | --- |
| [01-owned-install-lifecycle](01-owned-install-lifecycle.md) | A small typed fake install/remove engine creates and removes exactly its owned fake files and host receipt, while rejecting foreign/tampered state. | `COMPLETE / APPROVED / INTEGRATED` — implementation `ddd9f55`, correction `040a0f6`, review `dc63364`, merge `491f98b` | Approved SPEC |
| [02-metadata-runtime-and-guarded-git](02-metadata-runtime-and-guarded-git.md) | A local metadata-only event resumes once and a registered temporary project receives only a typed fast-forward decision under exact identity/base/lock guards. | `COMPLETE / APPROVED / INTEGRATED` — implementation `6cc8fb5`, review `4527f49`, merge `92c58bf` | Ticket 01 satisfied by `491f98b` |
| [03-reversible-agent-host-lifecycle](03-reversible-agent-host-lifecycle.md) | A bounded recorded capability gate proves exact receipt/removal semantics while real Codex and Claude remain `UNVERIFIED` without live authority. | `COMPLETE / APPROVED / INTEGRATED` - implementation `16597b6`, correction `673ff7c`, review `5601594`, merge `60cb8cf` | Tickets 01 and 02 integrated |
| [05-codex-cli-host-adapter](05-codex-cli-host-adapter.md) | Historical monolithic Codex marketplace/plugin adapter attempt and its two bounded reviews. | `SUPERSEDED / CONVERGENCE_DECOMPOSED` — rejected branch/SHAs preserved; old allocation released and receipt closed | Replaced by sequential Tickets 05A–05C |
| [05a-codex-cli-preflight-contract](05a-codex-cli-preflight-contract.md) | Before mutation, official CLI schemas, canonical installer-owned source and collision-free state produce `ELIGIBLE`; every invalid/foreign boundary produces `INSTALL_BLOCKED` with zero mutation. | `COMPLETE / APPROVED / INTEGRATED` — implementation `97ab31c`, repaired handoff `fb755268`, review `d54c0bd`, merge `b22c6c4` | Tickets 01–03 integrated; allocation released |
| [05s-codex-lifecycle-contract-staging](05s-codex-lifecycle-contract-staging.md) | Rejected combined environment/process/protocol/oracle parent retained as evidence only. | `SUPERSEDED / DECOMPOSED / IMMUTABLE_REJECTED_EVIDENCE` — terminal CR-112..CR-117 | Ticket 05A integrated by `b22c6c4` |
| [05s1-disposable-environment-core](05s1-disposable-environment-core.md) | Provision and safely destroy one exact disposable environment; no child process or Codex behavior. | `COMPLETE / APPROVED / INTEGRATED` — correction `41d5ce4`, handoff `e1087d3`, review `17ea1d5`, merge `504a3ec` | Ticket 05A and decomposition `PRG-20260811-106` |
| [05s2-bounded-child-process-runner](05s2-bounded-child-process-runner.md) | Run one deterministic generic child with explicit argv/environment and finite timeout. | `COMPLETE / APPROVED / INTEGRATED` — revision-03 implementation `33a8fa9`, handoff `dba0621b`, review `c97b754`, merge `6e24e06` | 05S1 integrated by `504a3ec` |
| [05s3-codex-protocol-fixture](05s3-codex-protocol-fixture.md) | Validate documented Codex add/list/remove JSON shapes without lifecycle state. | `COMPLETE / APPROVED / INTEGRATED` — correction `4835b0f`, handoff `008fac8`, review `c518e62`, merge `43a1639`; CR-125 closed | 05S2 integrated by `6e24e06` |
| [05s4-codex-lifecycle-oracle](05s4-codex-lifecycle-oracle.md) | Persist exact owned/foreign lifecycle and payload truth without adapter transaction logic. | `COMPLETE / APPROVED / INTEGRATED` — correction `02f33ef`, handoff `52ab9c0`, review `68ff06b`, merge `4af381c`; CR-126/CR-127 closed | 05S3 integrated by `43a1639` |
| [05b-codex-cli-transactional-registration](05b-codex-cli-transactional-registration.md) | Historical transactional registration parent and terminal CR-98..CR-104 evidence. | `SUPERSEDED / CONVERGENCE_DECOMPOSED / IMMUTABLE_REJECTED_EVIDENCE` | Replaced by 05B1-05B4 after 05S4 integration |
| [05b1-codex-registration-contracts-and-journal](05b1-codex-registration-contracts-and-journal.md) | Strictly bind observed add fields to proof/receipt and model finite current-attempt authority without effects. | `COMPLETE / APPROVED / INTEGRATED` — correction `dc57ff9`, handoff `1df30ae`, review `36ec95c`, merge `bbc7de5`; CR-128..CR-132 closed | 05A and 05S1-05S4 integrated |
| [05b2-codex-command-attempt-classification](05b2-codex-command-attempt-classification.md) | Convert exact command-start truth into finite 05B1 journal transitions without effects. | `PLANNED / READY_FOR_DISPATCH` — unique closure and binding reserved | 05B1 integrated by `bbc7de5` |
| 05B3 exhaustive compensation | Remove plugin then marketplace, run all fresh absence probes and retain only unresolved authority. | `PLANNED / DEPENDENCY_WAIT` | 05B2 integrated |
| 05B4 registration composition | Compose fresh admission, proof, journal, compensation and 05S4 oracle into one finite registration result. | `PLANNED / DEPENDENCY_WAIT` | 05B3 integrated |
| [05c-codex-cli-receipt-removal](05c-codex-cli-receipt-removal.md) | Exact receipt removal verifies plugin, marketplace and path absence; replay is isolated and only the full lifecycle projects `SUPPORTED`. | `PLANNED / DEPENDENCY_WAIT / REFREEZE_REQUIRED` — future exact 05B integrated baseline and finite closure required before dispatch | Tickets 05A and 05B approved/integrated |
| [06a-codex-role-profile-capability-proof](06a-codex-role-profile-capability-proof.md) | Prove in a disposable Codex home that reviewer tools are present and implementation multi-agent tools are disabled; otherwise return a typed host block. | `COMPLETE / APPROVED_EVIDENCE / INSTALL_BLOCKED / INTEGRATED` — implementation `38e9a8b`, handoff `f6f186f`, review `62955ec`, merge `de4141e`; actual host `ROLE_ISOLATION_UNPROVEN / ACCESS_DENIED / OUTPUT_UNAVAILABLE` | Downstream role-profile path stopped |
| [06b-codex-role-profile-owned-lifecycle](06b-codex-role-profile-owned-lifecycle.md) | Receipt-own and completely remove reviewer/implementation custom-agent profiles while preserving foreign config. | `PLANNED / DEPENDENCY_WAIT` | 06A `SUPPORTED`; autonomous Ticket 04 integrated |
| [06c-reviewer-role-composition](06c-reviewer-role-composition.md) | Compose owned profiles with the reviewer-only authority gate and prove implementation direct/indirect denial. | `PLANNED / DEPENDENCY_WAIT` | autonomous Ticket 04 and local 06B integrated |
| [04-windows-setup-and-uninstaller-package](04-windows-setup-and-uninstaller-package.md) | One Windows setup/uninstall invocation packages the owned lifecycle with at least one verified host, leaving target repositories untouched. | `PLANNED / DEPENDENCY_WAIT` — Inno Setup 6.7.3 verified; waiting for Codex lifecycle plus reviewer-role clusters | Tickets 05A–05C and 06A–06C integrated |

## Roles and allocation

- Control-plane owner / reviewer: Codex / current `main` worktree.
- Named implementation capabilities: task `019fcc9c-f34f-7d53-a313-c70c90bf3245` owns only the existing `workflow-implementation` lane and active Ticket 05B1; task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` owns only `workflow-implementer-2` and returned Ticket 06A. Each owner works alone and may not control the other task.
- Parent Ticket 05, combined Ticket 05S and old 05B remain immutable rejected evidence; 05S1-05S4 and 05B1 are integrated. 06A evidence is independently approved but its actual host result is fail-closed, so autonomous Ticket 04 and 06B/06C remain blocked; 05B2 is now the next dependency-free child while 05B3-05B4, 05C and package Ticket 04 remain dependency-waiting. Implementation owners must not modify the control worktree or one another's worktree; the reviewer must not modify either implementation worktree.
- Only the named reviewer may send/steer/wait/interrupt/close the implementation task. The implementation owner works alone on the dispatched ticket and may not create or control another Agent. Tickets 06A-06C turn this from a policy statement into a proven host profile plus receipt-bound authority boundary.

## Dispatch and continuation rules

- Every ticket stays `PLANNED` until the control plane selects it. Selection changes only that ticket to `IN_PROGRESS`, creates a metadata-only `ImplementationHandoff`, and asks exactly one delivery-confirmation question.
- A positive delivery reply is the only implementation authority for the selected ticket. It starts that ticket lane and automatically returns the planning lane to Grill; there is no second ticket-approval wait.
- A host or build-tool limitation discovered during implementation returns `BLOCKED` or `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`; it never permits an undocumented host-config edit or a weaker uninstaller.
- `CHANGES_REQUESTED` never creates another worktree or branch. The selected ticket permits at most one additive correction on its existing branch; a second failed review stops with `CONVERGENCE_REVIEW_REQUIRED`. Further work requires either a documented owner-scoped single-use override or a reviewed ticket decomposition; neither creates an automatic loop.
- A parent stopped by `CONVERGENCE_REVIEW_REQUIRED` is not corrected again. Its finite child tickets each receive a new ticket-bound receipt. Write-heavy dependent or overlapping children remain serial; independently scoped children may use distinct owner-bound worktrees only after explicit owner authorization and reviewer-recorded allocation.
- Reuse is source-local: selected public patterns may be adapted into this repository's own versioned/tested source. No target project receives an import, symlink, submodule or runtime dependency on this repository.
