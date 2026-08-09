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
| [02-metadata-runtime-and-guarded-git](02-metadata-runtime-and-guarded-git.md) | A local metadata-only event resumes once and a registered temporary project receives only a typed fast-forward decision under exact identity/base/lock guards. | `IN_PROGRESS / DISPATCHED` — closure `D1..D8`, five production files, one test, one implementation worktree and one Ticket-02 branch | Ticket 01 satisfied by `491f98b` |
| [03-reversible-agent-host-lifecycle](03-reversible-agent-host-lifecycle.md) | A host is reported supported only after its user-scope registration and exact cleanup proof can be verified. | `PLANNED` | Ticket 01 |
| [04-windows-setup-and-uninstaller-package](04-windows-setup-and-uninstaller-package.md) | One Windows setup/uninstall invocation packages the owned lifecycle with at least one verified host, leaving target repositories untouched. | `PLANNED` | Tickets 01, 02 and 03; available pinned Inno Setup toolchain |

## Roles and allocation

- Control-plane owner / reviewer: Codex / current `main` worktree.
- Named implementation capability: Codex implementation Agent / the single existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree. Ticket 01 was released after `491f98b`; Ticket 02 now owns the sole active lane on `codex/implementation-local-metadata-git-02` under its unique allocation and receipt.
- One implementation lane is active at a time. The implementation owner must not modify this control-plane worktree; the reviewer must not modify the implementation worktree.

## Dispatch and continuation rules

- Every ticket stays `PLANNED` until the control plane selects it. Selection changes only that ticket to `IN_PROGRESS`, creates a metadata-only `ImplementationHandoff`, and asks exactly one delivery-confirmation question.
- A positive delivery reply is the only implementation authority for the selected ticket. It starts that ticket lane and automatically returns the planning lane to Grill; there is no second ticket-approval wait.
- A host or build-tool limitation discovered during implementation returns `BLOCKED` or `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`; it never permits an undocumented host-config edit or a weaker uninstaller.
- `CHANGES_REQUESTED` never creates another worktree or branch. Ticket 01 permits one additive correction on its existing branch; a second failed review stops with `CONVERGENCE_REVIEW_REQUIRED`.
- Reuse is source-local: selected public patterns may be adapted into this repository's own versioned/tested source. No target project receives an import, symlink, submodule or runtime dependency on this repository.
