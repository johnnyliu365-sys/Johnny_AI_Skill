# Local Orchestration Adapter and Detachable Installer POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` |
| Status | `APPROVED` |
| Author | Codex / current `main` worktree / baseline `e04c2be` |
| Context | `doc/context/local-orchestration-installer/main.md` |
| PRD | `PRD.md §15` |
| Requirement change | `CHG-20260808-011`; reviewer-only role revision `CHG-20260811-012` |
| Common Context backlink | `CONTEXT.md › 衍生 SPEC 索引` |
| Implementation language | Python 3.11 for typed adapter/runtime contracts; Inno Setup script for the Windows installer package after its toolchain is pinned and verified. |

## Problem, goal and non-goals

The workflow must be installable as a local, detachable control plane and removable in one normal user action. The normal uninstaller must remove all content installed by this POC and nothing else. A target/company project must neither contain plugin files nor depend on them after installation, during use or after removal.

This POC includes a Windows per-user `Setup.exe` / uninstaller, installer-owned payload and state, metadata-only local orchestration adapter, host lifecycle adapters and a constrained local Git port. It excludes system-wide/admin install, target-project writes, target-project runtime/CI/deployment dependency, forced Agent turns/models, raw content storage, secrets, remote service, MCP server, Temporal server, database, SaaS, auto-push and auto-deploy.

## User flows and acceptance criteria

### Install control plane

1. The user launches `Setup.exe` and chooses one or more supported Agent hosts from those detected by the installer.
2. The installer validates a typed request, stages payload below its per-user root, validates each selected host lifecycle and writes the owned-install ledger only as one atomic successful installation.
3. It reports `INSTALLED` with an installation ID and supported-host results only when every selected host has a reversible, installer-owned registration receipt.

**AC-01 — Per-user ownership.** Installation requires no administrator elevation and creates no file, setting, Git change, symlink, package dependency or configuration inside a target project.

**AC-02 — Host lifecycle gate.** At least one host must be selected. For each selected host, `detect → register → verify → receipt` must succeed. A receipt must bind the installation ID and include the verifiable registration/payload cleanup proof required for `unregister → verify absent`. A missing executable, user auth/policy problem, incompatible lifecycle, foreign registration or missing removal method is `INSTALL_BLOCKED`; the installer cleans only its staging artifacts and issues no success receipt.

**AC-03 — Ownership model.** The ledger contains only a typed installation ID, package version, relative owned-path manifest/digests, host receipts and metadata-only runtime state references. It rejects absolute, traversal, URI, empty, foreign-root or unverified paths.

### Local runtime status and safe continuation

1. The installed user invokes the local status/resume entry point, or a verified host adapter supplies a typed metadata event.
2. The runtime validates the event, claims it at most once, reconstructs a metadata-only Router state and emits a finite status/result.
3. When a human approval or host capability is needed, it persists `NEEDS_USER_ACTION` / `HALTED`; it does not create a conversation, choose a model, read raw project content or manufacture a decision.

**AC-04 — Data minimisation and recovery.** Queue/checkpoint/ledger persistence must contain no ContextPacket text, source text, prompt, target project path/URI, Secret, PII or company code. Malformed, replayed, cross-installation, cross-project or unavailable-source events halt before routing. An interrupted valid operation can resume from its owned checkpoint without duplicating an effect.

**AC-05 — Guarded Git isolation.** Only a runtime use case, never the installer, may request Git work. Its injected port must require validated opaque project identity, explicit local project registration, per-project lock, clean expected base and fast-forward-only integration. A target outside the registry, a dirty/stale tree, a non-fast-forward or missing authority halts before any command.

### Remove control plane

1. The user launches the matching uninstaller once.
2. It verifies ledger identity and each manifest entry, stops only the owned runner, removes only receipt-matched host registrations, then deletes the verified owned root.
3. It reports `REMOVED`; a second invocation reports `NOT_INSTALLED` without mutation.

**AC-06 — One-click normal removal.** On an intact installation, one uninstaller invocation removes payload, launcher, runner, queue, checkpoint, ledger, logs and every host registration the installer created. The uninstaller must not leave a plugin/runtime component behind.

**AC-07 — Fail-closed removal.** Missing/tampered ledger, foreign receipt, non-descendant manifest path, runner-stop failure or host-unregister failure produces `UNINSTALL_BLOCKED`. It must retain only necessary owned recovery state, not report success and not delete an unknown path or any target-project content.

**AC-08 — Target-project non-interference.** Install, status, failed uninstall and successful uninstall must leave both an existing and an empty representative target repository byte-for-byte and Git-status unchanged.

### Install reviewer and implementation role profiles

1. A disposable Codex home first proves the documented custom-agent schema and exact multi-agent tool behavior without mutating the user's live Codex home.
2. Installation writes one reviewer profile with the required orchestration surface and one implementation profile whose multi-agent/thread-control surface is disabled, then records exact owned-profile receipts.
3. Removal deletes only receipt-matched owned profiles and verifies their absence while preserving foreign profiles byte-for-byte.

**AC-09 — Reviewer-only tool surface.** Only the reviewer profile may expose create/spawn/fork, dispatch/follow-up, steer, wait, interrupt and close. The implementation profile must prove these tools unavailable and the shared Router gate must return `HALT / ROLE_FORBIDDEN` for direct and indirect implementation-side attempts. If the current Codex custom-agent layer cannot reliably enforce this, Codex role-profile support is `INSTALL_BLOCKED`; prompt instructions are not an acceptable substitute.

**AC-10 — Role-profile ownership and removal.** Reviewer and implementation profile files/config entries are installer-owned only after exact digest and host readback. Normal uninstall removes both in one invocation and proves absence; foreign/manual profiles, global settings and target projects remain byte-for-byte/Git-status unchanged. Missing/tampered/foreign receipts block without broad deletion.

## Domain model, data flow and responsibility boundaries

| Layer | Named types / responsibility | Prohibited responsibility |
| --- | --- | --- |
| Domain | `InstallationId`, fixed `InstallRoot` (`%LOCALAPPDATA%\\JohnnyAIWorkflow`), `OwnedRelativePath`, `ArtifactDigest`, `HostId`, `HostRegistrationReceipt`, `HostRemovalProof`, `ProjectId`, `InstallerState`, `RuntimeState`, `UninstallResult` validate finite states and ownership invariants. | Strings/dynamic dictionaries used as paths, secrets, host state or project identity. |
| Application | `InstallControlPlane`, `ResumeOrchestration`, `ReadRuntimeStatus`, `UninstallControlPlane`, `GuardedIntegration` coordinate ports and map typed failures. | Direct filesystem, subprocess, host config or Git access. |
| Infrastructure | `OwnedFilesystemPort`, `InstallLedgerPort`, `RuntimeLifecyclePort`, `EventStorePort`, `HostLifecyclePort`, `ProjectRegistryPort`, `GuardedGitPort`, `ClockPort`, `ProcessPort` provide isolated effects. | Persisting raw Context or operating on unverified/foreign ownership. |
| Installer / equivalent UI | Setup/uninstaller displays typed progress/status and submits a validated command. | Business rules, filesystem deletion, direct host config or implicit singleton creation. |

The installer owns its root. The runtime owns only metadata inside that root. The host owns its own registration mechanism. A target project owns all of its files, Git state, code and data. No layer may infer another layer's ownership from a product name.

## API, event, storage, host, authority and operations

- External-facing local commands/events use Pydantic strict models and finite enums: `INSTALL_REQUESTED`, `INSTALL_SUCCEEDED`, `INSTALL_BLOCKED`, `RUNTIME_EVENT_RECEIVED`, `RUNTIME_HALTED`, `UNINSTALL_REQUESTED`, `REMOVED`, `NOT_INSTALLED`, `UNINSTALL_BLOCKED`.
- Each event includes typed correlation and installation IDs. It cannot contain raw source, prompt, ContextPacket, target project path/URI, Secret or PII.
- The sole durable stores are the owned-install ledger and bounded metadata queue/checkpoint below `InstallRoot`. There is no database, cache service, external provider, token or credential store.
- `HostLifecyclePort` is a capability boundary. A Codex/Claude adapter is production-supported only after a live lifecycle test proves user-scope registration and `HostRemovalProof` for every receipt-owned registration/payload it creates. Installer code must not edit hidden/unpublished host configuration formats.
- Installer and runtime logs use typed error codes plus redacted correlation/installation IDs. They may not include subprocess command arguments when those could reveal target/project data.
- Runtime process start/stop uses a recorded child process identity. Stop has a bounded timeout and requires exact ownership before termination.
- Codex role-profile records use finite `AgentRole`, `AgentProfileId`, `AgentToolPolicy`, `ReviewerOrchestrationGrant` and `AgentProfileRemovalProof` types. `agents.enabled=false` or any equivalent implementation-profile setting is accepted only after disposable behavioral proof in the installed Codex version; config shape alone is insufficient.

## Frontend composition and dependency injection

This POC has no company-project frontend. Its formal interaction boundaries are the Windows setup/uninstall dialogs and local command status result.

- **Composition roots:** `Setup.exe` and uninstaller each assemble a fresh application graph per invocation. The runtime assembles a distinct graph per event-processing run.
- **Injected dependencies:** filesystem, ledger, host lifecycle, process lifecycle, event store, project registry, guarded Git, clock and notification ports are constructor/factory injected behind named interfaces.
- **Production bindings:** production may bind a Windows owned-root filesystem and a verified host adapter only after capability checks. A host command/result is not a global singleton or an implicit environment read.
- **Test substitutions:** fake filesystem confined to a temporary root, fake host lifecycle, fake process, deterministic clock, in-memory queue, registry and Git port. Tests must assert no effect was requested against a target repository.
- **States / accessibility:** setup and uninstall must expose success, progress, empty/no-host, error/blocked and retry state in text, without relying on colour alone. No permission beyond the invoking user is requested.

Compensation adapters cross a closed capability boundary. An untrusted adapter
candidate is admitted by built-in `type(candidate)` plus raw trusted getset
descriptors captured from immutable built-in `type.__dict__`; caller-owned
class descriptors and equality are never executed. Only raw plain instance
methods may enter a frozen typed capability before any no-compensation or
effect path. `object/type.__getattribute__` over caller-owned class metadata,
`inspect.signature()` over caller-controlled data and arbitrary callable
objects are forbidden. Compensation planning/reduction is a separate pure
domain capability. Its exact order is removal(s), plugin-list absence,
marketplace absence, then installed-location absence; its result preserves the
exact request/attempt-bound residual state. The later composition root alone
executes admitted operations and validates exact manifest-bound observations.

## Implementation handoff and return contract

- `ImplementationHandoff` must cite this approved SPEC, `CHG-20260808-011`, the Context, an approved vertical ticket, named implementation owner/reviewer, TDD cases, installer composition-root reference and exact host capability assumptions.
- `ImplementationReturn`: `COMPLETED → ACTION_COMPLETED`; `BLOCKED → HALT`; `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`. Discovery that a host API cannot meet reversible lifecycle requirements is `BLOCKED` or `CHANGE_DETECTED`; it cannot be replaced with an undocumented config edit.
- No handoff, work progress, receipt or return may include raw ContextPacket, source text, prompt, target path/URI, Secret, PII or company code.

## Test seams and TDD design

The ticket set must begin each listed behavior with a red test and retain its first-failure evidence.

1. **Normal install/remove:** valid staged payload plus reversible fake host creates a ledger/receipt; normal uninstall removes exactly every ledger-owned file and fake registration; re-running uninstall returns `NOT_INSTALLED`.
2. **Ownership / invalid input:** null, empty, whitespace, container, absolute, extra-prefix, trailing slash, casing, encoded, traversal and URI path values are rejected before filesystem or host effects.
3. **External failure / fail-closed:** host detect/register/unregister failure, missing process identity, timeout, ledger tamper, manifest digest mismatch, unavailable build artifact and foreign registration block with no false receipt/deletion.
4. **Runtime / Git regression:** malformed/replayed/cross-installation event, raw-content sentinel, unregistered project, dirty/stale/non-fast-forward Git request and duplicate queue claim halt before side effects.
5. **Target non-interference:** snapshot and Git-status tests across representative target repositories cover install, failed install, status, failed uninstall and successful uninstall.
6. **Packaging smoke:** a clean Windows user sandbox installs from the released `Setup.exe`, starts/stops only the owned runner, removes it once and confirms no registered owned host integration remains.
7. **Role-profile capability proof:** isolated Codex config loads the exact reviewer and implementation custom agents. Reviewer positive orchestration is observable; every implementation direct/indirect thread-control attempt is unavailable or `ROLE_FORBIDDEN`. Unsupported per-agent config is a typed block, not a green prompt assertion.
8. **Role-profile lifecycle:** exact owned install/readback/remove/absence, tampered receipt, same-name foreign profile, replay and foreign/global config preservation. Representative target repositories remain unchanged.

### Verification staging architecture

Verification has two non-interchangeable isolation gates:

1. **Codex lifecycle contract staging.** Before refreezing transactional
   registration or receipt removal, a disposable test-owned child process and
   filesystem environment must persist independent marketplace/plugin truth.
   Its list and absence results come from freshly validated state and actual
   sandbox files, never from the caller request or a queued fake response. It
   must expose an injectable bounded command port with the documented add,
   list and remove JSON shapes so the downstream adapter consumes the same
   strict DTO surface. Raw absolute sandbox paths may exist only as ephemeral
   child-protocol proof inputs; recorded evidence remains relative/metadata-only.
   The staging port must not invoke or modify the user's live Codex installation.
2. **Disposable Windows user staging.** Before Ticket 04 can complete, the built
   `Setup.exe` and matching uninstaller must run in a disposable Windows user
   profile or equivalent VM/sandbox that can prove per-user filesystem,
   configuration, process and host-registration cleanup. A temporary directory,
   Linux container or contract emulator is not sufficient for this packaging
   gate.

Both gates must preserve unrelated state and byte-plus-porcelain snapshots of
representative target repositories. The environment is destroyed only after
fresh absence proof is captured. Contract-staging evidence does not project a
host as production `SUPPORTED`, and the Windows staging gate cannot replace the
finite unit/fault matrix.

## Risks, compatibility, rollback and release prerequisites

- The initial platform is Windows per-user only. Other operating systems are explicitly unsupported rather than silently using unsafe path semantics.
- Inno Setup is selected for the self-contained setup/uninstaller package because it provides a paired Windows uninstaller; its compiler is not installed in this workspace and must be version-pinned, acquired under the owner’s normal tool-install authority and validated in an implementation ticket before release.
- Codex and Claude compatibility is adapter-specific. A verified adapter may be released; an unverified host remains unavailable without blocking the detachable core.
- Rollback is a forward release that invokes the matching uninstaller or removes the POC from an owned test user profile. It never deletes a target project. Recovery after `UNINSTALL_BLOCKED` must display the exact owned root and failed owned receipt, then require retry/independent verification.
- No public artifact, code signing, auto-update, remote distribution, support SLA or deployment is approved by this POC.

## Convergence and backlink

- Common Context backlink: add this SPEC ID, location, scope, `PRD.md §15` and `CHG-20260808-011` under `CONTEXT.md › 衍生 SPEC 索引`.
- Requirement-change convergence: `CHG-20260808-011` has this SPEC ID but remains `DRAFT` until explicit owner approval.
- Docs baseline: pending the docs-only commit that contains this specification.

## Revision signature

| Date | Author / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-08 | Codex / current `main` / `e04c2be` | Initial Wayfinder, Architecture and Grill convergence to draft specification. |
| 2026-08-08 | Project owner / current `main` | Approved the complete POC scope, including owned one-click uninstall and fail-closed host lifecycle boundary. |
| 2026-08-10 | Project owner and Codex / current `main` | Approved the two-gate verification architecture: stateful Codex contract staging before 05B/05C refreeze, then disposable Windows user staging before package acceptance. Product scope and AC-01 through AC-08 are unchanged. |
| 2026-08-11 | Project owner / `CHG-20260811-012` | Approved AC-09/AC-10 reviewer-only Codex role profiles, fail-closed host capability proof, receipt-bound removal and new Tickets 06A-06C. Existing AC-01 through AC-08 remain unchanged. |
| 2026-08-11 | Project owner / ADR-20260811-004 | Refined the unchanged AC-01/02/07/08 compensation seam into closed port admission, pure reduction and thin composition after terminal 05B3 convergence. |

## Approval record

- Decision maker: Project owner
- Date: `2026-08-08 (Asia/Taipei)`
- Approval scope: Full `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X`, including AC-09/AC-10; tickets may now be planned, but each implementation still requires its own delivery-confirmation receipt and only the named reviewer may orchestrate the implementation task.
