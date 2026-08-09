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
| [05-codex-cli-host-adapter](05-codex-cli-host-adapter.md) | One exact installer-owned Codex marketplace/plugin registration is receipt-bound, verified and completely removed without touching another plugin or target project. | `BLOCKED / CONVERGENCE_REVIEW_REQUIRED` - correction review found CR-80..CR-85; no third same-closure correction or integration | Tickets 01–03 integrated; control-plane decomposition required |
| [04-windows-setup-and-uninstaller-package](04-windows-setup-and-uninstaller-package.md) | One Windows setup/uninstall invocation packages the owned lifecycle with at least one verified host, leaving target repositories untouched. | `PLANNED / DEPENDENCY_WAIT` - Inno Setup 6.7.3 verified; waiting only for Ticket 05 approval/integration | Ticket 05 integrated |

## Roles and allocation

- Control-plane owner / reviewer: Codex / current `main` worktree.
- Named implementation capability: Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-luna`, reasoning `xhigh`, in the single existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree. Tickets 01–03 are released; the worktree is clean and detached at `60cb8cf` before Ticket-05 dispatch.
- Ticket 05's existing branch is preserved as blocked correction evidence; `CONVERGENCE_REVIEW_REQUIRED` leaves no active implementation continuation. No additional worktree or review-time branch is authorized. Ticket 04 remains dependency-waiting. The implementation owner must not modify this control-plane worktree; the reviewer must not modify the implementation worktree.

## Dispatch and continuation rules

- Every ticket stays `PLANNED` until the control plane selects it. Selection changes only that ticket to `IN_PROGRESS`, creates a metadata-only `ImplementationHandoff`, and asks exactly one delivery-confirmation question.
- A positive delivery reply is the only implementation authority for the selected ticket. It starts that ticket lane and automatically returns the planning lane to Grill; there is no second ticket-approval wait.
- A host or build-tool limitation discovered during implementation returns `BLOCKED` or `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`; it never permits an undocumented host-config edit or a weaker uninstaller.
- `CHANGES_REQUESTED` never creates another worktree or branch. The selected ticket permits at most one additive correction on its existing branch; a second failed review stops with `CONVERGENCE_REVIEW_REQUIRED`.
- Reuse is source-local: selected public patterns may be adapted into this repository's own versioned/tested source. No target project receives an import, symlink, submodule or runtime dependency on this repository.
