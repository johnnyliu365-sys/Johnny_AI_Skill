# Local Orchestration Adapter and Detachable Installer — Wayfinder / Architecture / Grill Context

| Field | Value |
| --- | --- |
| Context state | `TICKET_02_IMPLEMENTING / TICKET_03_PLANNED` |
| Router event | `TICKET_DISPATCH_REQUIRED → IMPLEMENTATION_DISPATCH_CONFIRMED → IMPLEMENT` |
| Delivery stage | `POC` |
| Requirement change | `CHG-20260808-011` |
| Baseline | `491f98b` (`merge: integrate reopened owned lifecycle`) |
| Control-plane owner | Codex / current `main` worktree |
| Implementation owner | Codex implementation Agent / Ticket-02 allocation `aln_local_orchestration_install_02_20260809` |
| Required sources read | `AGENTS.md`, `Workflow.md` (Router, Wayfinder, Grill, change control, specification, tickets, role boundary), `Defined_wayfinder.md`, `CONTEXT.md`, `PRD.md`, `ProjectSchedule.md`, `doc/RequirementChangeLog.md`, existing plugin manifests / README, `library/workflow_router/`, and completed plugin / autonomous-collaboration POCs |

## Shared Context reference

- Common source: `CONTEXT.md › 已確認事實與共同邊界 › 現行目標是本機、可拔除的多 AI 協作／稽核控制平面`
- Fingerprint: `c173f741` (UTF-8 SHA-256 prefix at discovery)
- Binding fact: this is an external control plane, never a target-project dependency; removal must leave the target project operational.

## Existing-spec preflight

| Artifact | Status | Reusable, immutable fact | Disposition here |
| --- | --- | --- | --- |
| `modules/spec/plugin-distribution.md` | `APPROVED` | Codex plugin distribution is per-user and target-project independent. | Preserve the detachable boundary; add no in-project dependency. |
| `modules/spec/claude-code-plugin-distribution.md` | `APPROVED` | Claude and Codex share `skills/` source; lifecycle verification is host-environment dependent. | Reuse as a host-adapter input, not as evidence that automated lifecycle commands exist. |
| `modules/spec/autonomous-collaboration-audit.md` | `APPROVED` | Router external capabilities are injected; host/model creation and real Git were POC exclusions. | Extend only through this fresh change; do not imply the previous fake ports are real. |
| `modules/spec/context-load-telemetry.md` | `APPROVED` | Router persistence must be metadata-only; raw ContextPacket text is prohibited. | Retain as a non-negotiable runtime data boundary. |

## Wayfinder decision

```json
{
  "project_id": "local-orchestration-installer-poc",
  "decision": "GO",
  "decision_reasons": [
    "A Windows per-user install and detach flow is a concrete, testable user outcome.",
    "Every interaction can be mapped to an installer/command boundary, a typed use case, an owned data store and a returned state.",
    "Foreign-host registrations, raw-context storage and target-project changes have executable fail-closed boundaries."
  ],
  "product": {
    "target_users": ["The plugin owner operating Codex and/or Claude on Windows"],
    "core_problem": "A manually installed workflow plugin cannot prove what it owns or remove its local control-plane residue in one action.",
    "value_proposition": "Install a local automation control plane without coupling it to a company project; remove it cleanly with a matching uninstaller.",
    "mvp_scope": ["Per-user Windows install", "owned runtime and plugin payload", "metadata-only local adapter", "verified host registration", "one-click owned uninstall"],
    "out_of_scope": ["Target-project runtime/CI changes", "host-model forcing", "admin install", "remote service", "raw-context persistence"]
  },
  "business": {
    "model": "Non-commercial internal POC",
    "validation_method": "Clean-user-profile test harness plus two untouched representative target repositories",
    "success_metrics": ["all owned artifacts removed by normal uninstall", "target repository status is unchanged", "foreign registration is rejected", "interrupted uninstall is retryable"],
    "stop_conditions": ["no verified host install/remove lifecycle", "uninstaller would need to delete an unowned path", "a required state would contain raw ContextPacket content"]
  },
  "constraints": {
    "tech_limits": ["Windows-first and per-user", "no administrator elevation", "Python is available; Inno Setup/NSIS is not currently installed", "Codex/Claude lifecycle capability must be discovered and tested, not assumed"],
    "cost_ceiling": "No hosted service or paid runtime; build-tool provisioning is a local development prerequisite only."
  },
  "assumptions": ["The owner may select each supported host at install time.", "A host capability may be unavailable and must result in a safe blocked outcome.", "The actual installer format will be a self-contained Windows setup executable built from a version-pinned toolchain after a ticket validates the toolchain."]
}
```

## Functional Architecture Brief

| Frontend / equivalent interaction slice | Observable states | Derived use case / domain rules | Data pipeline and owner | Composition and DI boundary |
| --- | --- | --- | --- | --- |
| `INSTALL_CONTROL_PLANE` — user runs Setup and selects one or more supported agent hosts | `INSTALLED`, progress, no host detected, `INSTALL_BLOCKED`, accessibility-safe result text | Validate install request; detect `ABSENT` / `OWNED` / `FOREIGN`; stage payload; register each selected host; issue receipt only when every selected host succeeds. Foreign or non-removable registration must never be overwritten. | Input choices → `InstallerRequest` validation → `INSTALL_REQUESTED` → installer-owned ledger at fixed `%LOCALAPPDATA%\\JohnnyAIWorkflow` → `InstallProjection`. No target-project data is accepted or stored. | Installer composition root creates `HostLifecyclePort`, `OwnedFilesystemPort`, `RuntimeLifecyclePort`, `InstallLedgerPort`, `ClockPort`, `ProcessPort`; test fakes replace all effects. One invocation is one lifetime scope. |
| `LOCAL_RUNTIME_STATUS` — user or host invokes status/resume command | `IDLE`, `RUNNING`, `WAITING_FOR_EVENT`, `HALTED`, `NEEDS_USER_ACTION`; missing/corrupt state is `HALTED` | Validate metadata event; claim queue item once; rebuild a metadata-only Router state; emit safe status. It cannot create a host conversation, read raw Context or infer an absent decision. | Typed event → Pydantic validation → queue/checkpoint owned by runtime → selected Router port → redacted status projection. Queue retention is bounded; uninstall deletes it as owned state. | Runtime composition root injects `EventStorePort`, `RouterPort`, `ProjectRegistryPort`, `GuardedGitPort`, `HostNotificationPort`, `ClockPort`; all production effects are replaceable in tests. |
| `REMOVE_CONTROL_PLANE` — user runs the matching uninstaller | `REMOVED`, progress, `NOT_INSTALLED`, `UNINSTALL_BLOCKED`, retry guidance | Verify ledger identity and each owned relative path; stop owned runtime; remove only receipt-matched host registrations; delete the owned root. Any unknown path, failed stop or failed unregister retains the ledger and stops deletion. | Uninstall request → `OwnedInstallLedger` verification → lifecycle events → host cleanup receipts → owned-root deletion → result projection. Target repositories, their Git state and their files are absent from the command model. | Uninstaller composition root injects the same ports with a deletion-capable `OwnedFilesystemPort` constrained to the verified root. Tests use fake processes, hosts and a sandboxed filesystem. |

## Architecture decision

[ADR-20260808-003](../../adr/ADR-20260808-003-local-orchestration-installer.md) is the Architecture handoff. It adopts a ports-and-adapters local composition root with two separate ownership domains:

1. **Installer-owned user root** — payload, runner, ledger, queue, checkpoints, logs and launcher are all descendants of the fixed `%LOCALAPPDATA%\\JohnnyAIWorkflow` Windows per-user directory. The ledger contains a versioned installation ID, path-relative artifact manifest/digests and host registration receipts. It never contains raw Context, target-project paths or credentials.
2. **Target-project registry** — a project can be represented only by a validated opaque `ProjectId` and an explicit local registration supplied at runtime. A guarded Git adapter resolves the actual path only inside its local injected implementation, requires a clean expected base and permits no operation outside that registered root. The installer never calls it.

The runner is not a hidden model executor. It consumes validated metadata events, resumes local checkpoints and emits `HALTED` / notification state when a human or host capability is required. Host-specific Codex and Claude behavior lives behind `HostLifecyclePort`; the core installer/runtime has no platform-specific configuration knowledge.

## Grill findings and decision

| Question | Finding / control |
| --- | --- |
| Can uninstall prove it owns every deletion target? | Yes only with a valid installation ID, digest-verified relative manifest and resolved descendant path. Missing, tampered or foreign state is `UNINSTALL_BLOCKED`, never recursive deletion. |
| Can existing manual marketplace installs be safely handled? | Yes: classify as `FOREIGN` and refuse to install or remove. This prevents a one-click uninstaller from deleting the owner's separately installed plugin. |
| Does a host registration have a reversible contract? | Unknown until its adapter passes detect/register/unregister and returns proof that its receipt-owned registration and any receipt-owned host payload no longer exist. It is a blocking capability, not a reason to manipulate hidden host config. |
| Can the local runtime reduce workflow pauses without impersonating a host? | Yes: it durably processes typed local events and safe continuations; it queues/announces host work rather than attempting to create a Codex/Claude turn. |
| Could adapter state leak project or Context contents? | No valid design path needs that data. The POC permits only opaque IDs, revision/evidence digests and finite stage/status fields. Tests must sentinel-check the persisted representations. |
| Can real Git expand the plugin into target-project coupling? | No. It is a separately injected, project-registered runtime port with expected-base/clean-tree/fast-forward-only constraints. The installer has no Git authority. |

**Grill decision: `GO → SPEC_DRAFT`.** The normal success path gives the requested one-click removal. The only allowed exception is an unsafe or failed external lifecycle action, which must stop with an explicit retryable blocked result instead of deleting unowned content or falsely claiming removal.

## Risks, unresolved capability and re-entry

- Current workspace inspection found Python but not an Inno Setup/NSIS compiler. A ticket must pin and verify the build tool; no release executable is claimed by this Context.
- The Codex manual helper could not run because Node.js is absent, and no OpenAI Docs MCP was exposed in this session. Therefore no undocumented Codex lifecycle command is assumed. The host-adapter ticket must use a live supported host and record its verified lifecycle behavior before declaring it supported.
- The owner must explicitly approve the draft SPEC before ticket planning. A host limitation discovered after approval is `BLOCKED` or `REQUIREMENT_CHANGED → Grill`, not a silent scope expansion.

## Approved SPEC and smallest reusable-module selection

The owner approved this SPEC on `2026-08-08`. Ticket planning is now authorized; source/test implementation is not authorized until a selected ticket receives its own dispatch receipt.

```text
selected: workflow-router-poc@d94d8d5
why: The local runtime needs existing strong types for Router events, completion/implementation returns, opaque ProjectId and metadata-only Context, plus the guarded-integration fail-closed pattern.
read: library/workflow_router/README.md → library/workflow_router/__init__.py → library/workflow_router/contracts.py (ProjectId, RouterEvent, ContextView, CompletionEvidence, ImplementationHandoff, ImplementationReturn) → library/workflow_router/guarded_integration.py
dependency: Pydantic, LangGraph, Temporal, MCP; this POC uses only the public typed contracts/patterns selected by each ticket.
boundary: Do not treat the POC's fake adapters as real host/Git operations. Do not import unrelated reliability, event, payment, identity or messaging modules.
```

## Derived SPEC index

### `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` — Local Orchestration Adapter and Detachable Installer POC

- Specification: `modules/spec/local-orchestration-installer.md` (`APPROVED` on `2026-08-08`).
- Context: `doc/context/local-orchestration-installer/main.md`.
- Scope: installer-owned Windows local control plane and clean owned uninstall; no target-project dependency.
- PRD / change: `PRD.md §15` / `CHG-20260808-011`.
- Common Context backlink: published by `d94d8d5`; ticket-set backlink pending the next docs-only commit.

## Ticket 01 completion and released allocation

- Ticket: `01-owned-install-lifecycle`, selected from the committed ticket set `afee39d`.
- Reopen: the owner revoked fourteen unmerged experimental branches. They were deleted without integrating `library/local_orchestration` into `main`.
- Handoff / allocation: `hnd_local_orchestration_install_01_reopen_20260809` / `aln_local_orchestration_install_01_reopen_20260809` retain receipt `rcpt_local_orchestration_install_01_20260808` and the same named implementation owner.
- Execution boundary: the existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` is the only implementation worktree. It uses one branch, `codex/implementation-local-install-lifecycle-01`, for the reopened implementation and its single permitted correction.
- Scope: five production files, one test file and finite closure `C1..C8`; historical source and CR-36..72 are not implementation inputs.
- Completion: implementation `ddd9f55`, evidence correction `040a0f6`, final independent review `dc63364`, guarded integration `491f98b`; the implementation remained within the five-file / one-test ceiling.
- Planning continuation: Ticket 02's dependency is satisfied and it is `PLANNED / READY_FOR_SELECTION`; it has no implementation allocation or source authority yet.

## Ticket 02 Grill convergence

| Grill question | Finding / bounded decision |
| --- | --- |
| Does Ticket 02 duplicate or silently widen Ticket 01? | No. Ticket 01 owns only installation ownership/lifecycle fakes. Ticket 02 begins only after its reviewed integration and owns runtime event/checkpoint, project registry and guarded Git ports. |
| Can existing Router contracts be reused without importing fake external behavior? | Yes. Reuse public `ProjectId`, `RouterEvent`, completion/return and Context descriptor types plus the guarded-integration error pattern. The existing fake integration adapter remains a reference only. |
| Is a real target project or path persisted / required? | No. Tests must use temporary repositories. Runtime persistence is installation-bound metadata; the injected registry resolves any local root only at its effect boundary and never serializes it. |
| Is real Git authority constrained enough? | Only with opaque project identity, explicit registration, per-project lock, clean expected base and fast-forward-only operation. Missing or stale state, conflicts, dirty tree, replay or cross-project request halts before Git. |
| Is a new SPEC/ADR/CHG needed? | No. These are already accepted AC-04/05/08 boundaries. Changing them, adding push/deploy/reset/merge commit, or carrying raw source would be `REQUIREMENT_CHANGED`. |

**Planning Grill result: `GO → IMPLEMENT`.** Ticket 02 is bounded by closure D1..D8 and dispatched under `hnd_local_orchestration_install_02_20260809` / `rcpt_local_orchestration_install_02_20260809`. Its implementation is isolated to the single existing implementation worktree and one Ticket-02 branch; Ticket 03 remains `PLANNED` with no source authority.

## Ticket 02 completion

Implementation `6cc8fb5`, handoff `cc38c5d`, review `4527f49` and guarded
merge `92c58bf` completed D1..D8 within the five-file / one-test ceiling.
Independent review covered the green suite, strict mypy, compile/source checks,
eight reverse mutations, and actual temporary-Git byte/porcelain invariance.
The merge retained both append-only progress records with no source/test
conflict, and post-merge verification passed again.

Allocation `aln_local_orchestration_install_02_20260809` is released. The sole
implementation worktree is clean and detached at `92c58bf`; the Ticket-02
branch was deleted. No schedule was created or resumed. Ticket 03 remains
`PLANNED` until its own bounded dispatch, allocation, receipt and branch exist.

## Ticket 03 Grill convergence

The original Ticket-03 draft mixed two live hosts, process execution, policy and
login discovery, a full error matrix, removal proof and packaging preparation,
and incorrectly required a fresh worktree. The bounded ticket now owns only a
recorded reversible capability gate in four production files and one test under
finite closure H1..H8.

No reusable-module catalog entry matches host registration authority:
`identity-resolution` is not an authorization boundary and Router behavior is
unrelated. Ticket 03 reuses only integrated `InstallationId`. Current evidence
authorizes no live Codex/Claude action, so both must remain `UNVERIFIED`; a real
support claim requires separate external test authority and change control.

**Planning Grill result: `GO → PLANNED / BOUNDED`.** The ticket is safe to
dispatch only to the existing sole implementation worktree with one new-ticket
branch. Ticket 04 remains dependency-waiting; no schedule is involved.
