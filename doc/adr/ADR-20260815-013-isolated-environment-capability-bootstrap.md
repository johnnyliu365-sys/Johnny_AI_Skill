# ADR-20260815-013 — Isolated environment capability bootstrap

- Date: `2026-08-15 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related specification: `SPEC-AI-WORKFLOW-ENVIRONMENT-CAPABILITY-BOOTSTRAP-20260815-01M0E2C4B6S8T0R2A4P6D8F0H2`
- Related change: `CHG-20260815-024`

## Context

Johnny cannot reliably control, validate or dispatch a project when Git, Python, Docker or a
project-specific build tool is missing or incompatible. Blind installation would pollute the
user machine or target project; repeated probes and background updates would also spend CPU,
I/O and model tokens. The control plane therefore needs a bounded environment capability
system that preserves the user's existing toolchain and remains completely detachable.

## Decision

1. Capability planning is a one-shot, effect-free operation. It resolves only capabilities
   required by the current gate and returns a typed plan before any install, login or process
   launch.
2. A compatible existing user/project tool is reused first. Johnny does not change its version
   or configuration. Incompatibility produces a Johnny-owned side-by-side environment or a
   guided user action; it never silently mutates the original tool.
3. Git is required for control. The package includes an exact portable Git fallback. A pinned
   Johnny-owned Python 3.11 `CONTROL_PYTHON` with locked dependencies and strict mypy is also
   bundled. Docker and heavy/build/deploy tools are conditional.
4. Automatic installation is limited to reversible per-user Johnny-owned artifacts. Admin,
   system/global configuration, EULA, reboot, login, credential or external-effect work needs a
   separate displayed plan and approval.
5. All Johnny-owned environments and state live beneath the per-user Johnny root. Environment
   identity uses opaque project/capability/lock digests. Target projects contain only their
   native manifests and normal project artifacts, never Johnny runtime state or paths.
6. Resource plans are finite and hard-enforced for every Johnny-launched process/container.
   Windows uses a proved Job Object adapter; Docker uses native resource flags. Absence of a
   required enforcement capability is `HALT / RESOURCE_ENFORCEMENT_UNAVAILABLE`.
7. Admission is separated into `CONTROL_BOOTSTRAP`, `PROJECT_BASELINE` and `TICKET_OVERLAY`.
   Implementation cannot install or change a tool. Boundary drift closes the affected evidence
   and requires re-planning/re-dispatch; there is no periodic monitoring.
8. `InstallGrant`, `CapabilityEvidence`, ticket Router receipt and external-effect authority are
   independent. One ticket has one Router receipt at a time. Environment execution evidence
   binds that same receipt and never creates an execution receipt.
9. Install grants have no time expiry. They remain usable only for their exact artifact identity
   and are invalidated by artifact change, failed readback, explicit revocation or owned-state
   removal. This does not extend ticket authority.
10. `PROJECT_DETACH` and `PLUGIN_UNINSTALL` are separate exact-owned operations. Neither may
    alter a target project or foreign/user tool. Plugin removal deletes Johnny-owned grants,
    evidence, receipts/bindings, environments and cache using its ownership ledger.
11. Version one supports Windows 10/11 x64 hosts. Linux containers are allowed through Docker;
    unsupported host platforms fail closed. Contracts remain platform-neutral for future
    adapters.

## Alternatives rejected

- Install all tools globally: rejected because ownership, rollback and team compatibility
  cannot be proven.
- Force Johnny's versions over project/user versions: rejected because it can break native
  build and deployment workflows.
- Put `.johnny`, worktrees, telemetry or environment manifests in the target repository:
  rejected because it couples and pollutes the controlled project.
- Re-probe tools on a schedule or use a background updater: rejected because idle CPU/I/O and
  network effects are unnecessary and do not grant authority.
- Use soft advisory CPU limits only: rejected because an Agent command could exceed the plan.
- Treat an install grant or environment proof as a ticket receipt: rejected because tool
  ownership and implementation authority have different lifecycles.

## Consequences and recovery

- First use may require a bounded bootstrap, but later tickets can reuse exact compatible
  evidence without model wake or repeated installation.
- Immutable side-by-side environments consume disk until exact detach/uninstall cleanup; shared
  caches must be read-only and bounded.
- Tool/artifact drift stops only the stage that needs that capability. A source/build tool does
  not block unrelated planning, and a deployment tool does not authorize deployment.
- Atomic activation keeps the previous valid Johnny-owned environment available until the new
  candidate passes verification. Failed staging is removed without altering the active version.
- A successor can ignore Johnny state and use project-native manifests. Removing Johnny cannot
  block project build, test, deployment or engineering handoff.
