# Local Orchestration Adapter and Detachable Installer POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` |
| Status | `APPROVED` |
| Author | Codex / current `main` worktree / baseline `e04c2be` |
| Context | `doc/context/local-orchestration-installer/main.md` |
| PRD | `PRD-20260808-011`, `PRD-20260812-014`, `PRD-20260813-015`, `PRD-20260814-018` |
| Requirement change | `CHG-20260808-011`; version-one delivery revision `CHG-20260812-014`; project-owned disposable test runtime revision `CHG-20260813-015`; reviewer-owned gateway revision `CHG-20260814-018`; retired mechanism evidence `ARCH-REQ-20260815-003` |
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

### Install the reviewer-owned gateway and restricted implementation profile

1. A disposable Codex home first proves a supported transport can bind the
   exact implementation custom-agent configuration to a session in the exact
   assigned worktree and read back its effective multi-agent tool absence,
   without mutating the user's live Codex home.
2. Installation owns the exact restricted implementation profile and local
   Johnny gateway registration only after digest and effective host readback.
   It does not install a second Agent-control route.
3. The Router grants only the ticket's named reviewer a consumable gateway
   capability bound to one live pending descriptor. The implementation owner
   receives no gateway port, credential or alias.
4. Removal deletes only receipt-matched owned profile/gateway artifacts and
   verifies their absence while preserving foreign/global host state and target
   repositories byte-for-byte.

**AC-09 — Sole reviewer gateway and defense in depth.** Johnny's local
reviewer-owned orchestration gateway is the only permitted create/spawn/fork,
dispatch/follow-up, steer, wait, interrupt and close effect entrypoint. Every
effect binds the exact reviewer role/capability, project, ticket, reviewed
handoff, unconsumed receipt, target implementation owner, worktree, branch,
expected baseline, action, correlation and live `PendingDispatchDescriptor`.
The implementation owner receives no gateway port/credential and its effective
host session separately proves built-in multi-agent/thread-control tools absent.
Direct tools, MCP aliases, indirect adapters, copied/forged/replayed grants,
role substitution or any mismatch return `HALT / ROLE_FORBIDDEN` or the exact
typed binding error before effect. Config text and prompt assertions are not
proof. If a supported exact-profile launch/binding and effective-session
readback cannot be proven, support remains `INSTALL_BLOCKED /
ROLE_ISOLATION_UNPROVEN`.

**AC-10 — Restricted-profile/gateway ownership and removal.** Implementation
profile files/config entries and local gateway registration/state are
installer-owned only after exact digest and host readback. Normal uninstall
removes every receipt-matched owned artifact in one invocation and proves
absence; foreign/manual profiles, global settings, unrelated gateways and
target projects remain byte-for-byte/Git-status unchanged. Missing, tampered,
foreign or replayed receipts block without broad deletion. No network or MCP
service is introduced by this POC.

### Freeze and preserve the first packaged version

1. After all runtime and host prerequisites are independently approved and integrated, one bounded implementation ticket adds the pure typed payload-manifest contract and a second adds the Inno installer/build source. Each receives its own TDD, implementation, review and guarded integration. Verification may produce only disposable test output; no release artifact is accepted before staging.
2. After both source tickets are independently approved and integrated, the reviewer freezes one exact clean `main` commit as the complete version-one source candidate.
3. Before any release build or disposable Windows system integration is dispatched, the reviewer publishes exactly that commit to remote `staging` using branch creation or a verified fast-forward-only update, then independently reads back the same remote SHA.
4. Disposable-Windows environment qualification, release build, install verification, uninstall/absence verification and final artifact freeze consume that exact source/artifact lineage in separate serial tickets. The release build uses a clean export of the exact remote staging SHA.
5. After version one is frozen, later feature or architecture work starts from the current `staging` baseline through normal change control; it never rewrites the version-one release record or artifact identity.

**AC-11 — Staging warm-backup gate.** The remote `staging` ref must equal the reviewed complete version-one source candidate—including installer build source—before release build/system-integration begins. Dirty or incomplete source, absent authority, unexpected remote history, non-fast-forward update, failed fetch/readback or SHA mismatch returns a typed halt before build or install. The gate never force-pushes, deletes a remote ref, pushes `main`, creates a release or stores build artifacts/secrets in Git.

**AC-12 — Immutable version-one identity.** The version-one release record binds the exact source commit, remote staging SHA at build start, clean-export identity, Inno Setup version, owned payload manifest digest, setup and matching uninstaller digests, disposable install/uninstall evidence and independent review references. It is append-only: a changed source, manifest, toolchain or binary digest is a new candidate/version and cannot overwrite the first record or reuse its success claim.

### Keep disposable repository tests inside their owning plugin checkout

**AC-13 — Project-owned disposable test runtime.** Every 05S1-based repository
test environment must be an exact marker-bound child of the current plugin
checkout's `tests/.johnny-runtime/` directory. Each worktree therefore owns a
separate namespace. No such test may create, scan or clean an
`%TEMP%/johnny-stage-env-*` root, and no target project may supply or contain
the runtime root. Successful teardown leaves the exact project runtime
directory absent; pre-existing/unclaimed residue, unexpected siblings,
reparse/marker mismatch or incomplete cleanup fails closed without deleting
the residue. Tracked and ignored Git readback must expose any final residue.

## Domain model, data flow and responsibility boundaries

| Layer | Named types / responsibility | Prohibited responsibility |
| --- | --- | --- |
| Domain | `InstallationId`, fixed `InstallRoot` (`%LOCALAPPDATA%\\JohnnyAIWorkflow`), `OwnedRelativePath`, `ArtifactDigest`, `HostId`, `HostRegistrationReceipt`, `HostRemovalProof`, `ProjectId`, `InstallerState`, `RuntimeState`, `UninstallResult`, `ReviewerGatewayGrant`, `RestrictedSessionBinding`, `OrchestrationAction`, `GatewayDenial` validate finite states and ownership invariants. | Strings/dynamic dictionaries used as paths, secrets, host state, orchestration authority or project identity. |
| Application | `InstallControlPlane`, `ResumeOrchestration`, `ReadRuntimeStatus`, `AuthorizeReviewerGateway`, `ExecuteOrchestrationAction`, `UninstallControlPlane`, `GuardedIntegration` coordinate ports and map typed failures. | Direct filesystem, subprocess, host config, Agent task or Git access. |
| Infrastructure | `OwnedFilesystemPort`, `InstallLedgerPort`, `RuntimeLifecyclePort`, `EventStorePort`, `HostLifecyclePort`, `RestrictedSessionTransportPort`, `ReviewerOrchestrationPort`, `ProjectRegistryPort`, `GuardedGitPort`, `ClockPort`, `ProcessPort` provide isolated effects. | Persisting raw Context, exposing Agent-control to implementers or operating on unverified/foreign ownership. |
| Installer / equivalent UI | Setup/uninstaller displays typed progress/status and submits a validated command. | Business rules, filesystem deletion, direct host config or implicit singleton creation. |

The installer owns its root. The runtime owns only metadata inside that root. The host owns its own registration mechanism. A target project owns all of its files, Git state, code and data. No layer may infer another layer's ownership from a product name.

## API, event, storage, host, authority and operations

- External-facing local commands/events use Pydantic strict models and finite enums: `INSTALL_REQUESTED`, `INSTALL_SUCCEEDED`, `INSTALL_BLOCKED`, `RUNTIME_EVENT_RECEIVED`, `RUNTIME_HALTED`, `UNINSTALL_REQUESTED`, `REMOVED`, `NOT_INSTALLED`, `UNINSTALL_BLOCKED`.
- Each event includes typed correlation and installation IDs. It cannot contain raw source, prompt, ContextPacket, target project path/URI, Secret or PII.
- The sole durable stores are the owned-install ledger and bounded metadata queue/checkpoint below `InstallRoot`. There is no database, cache service, external provider, token or credential store.
- `HostLifecyclePort` is a capability boundary. A Codex/Claude adapter is production-supported only after a live lifecycle test proves user-scope registration and `HostRemovalProof` for every receipt-owned registration/payload it creates. Installer code must not edit hidden/unpublished host configuration formats.
- Installer and runtime logs use typed error codes plus redacted correlation/installation IDs. They may not include subprocess command arguments when those could reveal target/project data.
- Runtime process start/stop uses a recorded child process identity. Stop has a bounded timeout and requires exact ownership before termination.
- Codex role/gateway records use finite `AgentRole`, `AgentProfileId`,
  `AgentToolPolicy`, `ReviewerGatewayGrant`, `RestrictedSessionBinding`,
  `OrchestrationAction`, `GatewayDenial` and `AgentProfileRemovalProof` types.
  `agents.enabled=false`, `features.multi_agent=false` or any equivalent
  implementation-profile setting is accepted only after a supported disposable
  transport binds that exact profile/worktree and effective-session readback
  proves the forbidden tools absent; config shape alone is insufficient.

## Frontend composition and dependency injection

This POC has no company-project frontend. Its formal interaction boundaries are the Windows setup/uninstall dialogs and local command status result.

### XSS Review classification

Current POC scope is `XSS_NOT_APPLICABLE`: no untrusted data enters a Browser,
WebView, HTML/DOM renderer or JavaScript execution context. The Windows
setup/uninstall dialogs and local status projection consume only finite typed
models and expose no Native Bridge, IPC or Extension API to JavaScript.

This classification is not inherited by a future thin plugin UI. Any ticket
that introduces Browser/WebView/HTML/DOM/JavaScript rendering must re-enter the
[Workflow XSS gate](../../Workflow.md#xss-review). If that JavaScript context
can reach host or extension capabilities, it is `PRIVILEGED_XSS_REVIEW` and
must freeze the complete source-to-sink and JavaScript-to-host capability
matrices before implementation.

- **Composition roots:** `Setup.exe` and uninstaller each assemble a fresh application graph per invocation. The runtime assembles a distinct graph per event-processing run.
- **Injected dependencies:** filesystem, ledger, host lifecycle, process lifecycle, event store, project registry, guarded Git, clock and notification ports are constructor/factory injected behind named interfaces.
- **Production bindings:** production may bind a Windows owned-root filesystem and a verified host adapter only after capability checks. A host command/result is not a global singleton or an implicit environment read.
- **Test substitutions:** fake filesystem confined to the current plugin
  checkout's exact `tests/.johnny-runtime/` lease, fake host lifecycle, fake
  process, deterministic clock, in-memory queue, registry and Git port. The
  root is never caller-selected or located in a target project. Tests must
  assert no effect was requested against a target repository or OS-global
  `johnny-stage-env-*` namespace.
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
7. **Restricted-session transport proof:** isolated Codex config uses a supported
   transport to bind the exact implementation profile and exact assigned
   worktree. Effective readback proves built-in multi-agent/thread-control tools
   absent. Missing transport/profile binding, access denied, ambiguous output or
   config-only evidence is a typed block, not a green prompt assertion.
8. **Reviewer gateway authority:** one exact reviewer grant and live pending
   descriptor reaches each named fake orchestration effect once. Implementation
   direct tools, gateway calls, MCP aliases, indirect adapters, forged/copied/
   replayed grants and every project/ticket/handoff/receipt/owner/worktree/
   branch/baseline/action/correlation mismatch reach zero effects.
9. **Restricted-profile/gateway lifecycle:** exact owned install/readback/remove/
   absence, tampered receipt, same-name foreign profile, unrelated gateway,
   replay and foreign/global config preservation. Representative target
   repositories remain unchanged.

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

Remote Git `staging` is a third, delivery-only boundary and must not be confused
with either test environment above. It is a warm backup and future development
baseline for one reviewed source commit; it does not by itself prove install,
uninstall, host support or binary correctness.

## Risks, compatibility, rollback and release prerequisites

- The initial platform is Windows per-user only. Other operating systems are explicitly unsupported rather than silently using unsafe path semantics.
- Inno Setup is selected for the self-contained setup/uninstaller package because it provides a paired Windows uninstaller. Version 6.7.3 has been acquired and signature/version/compile verified; the package-assembly ticket must re-read and bind that exact compiler identity before accepting an artifact.
- Codex and Claude compatibility is adapter-specific. A verified adapter may be released; an unverified host remains unavailable without blocking the detachable core.
- Rollback is a forward release that invokes the matching uninstaller or removes the POC from an owned test user profile. It never deletes a target project. Recovery after `UNINSTALL_BLOCKED` must display the exact owned root and failed owned receipt, then require retry/independent verification.
- No public artifact, code signing, auto-update, remote distribution, support SLA or deployment is approved by this POC.

## Convergence and backlink

- Common Context backlink: add this SPEC ID, location, scope, `PRD-20260808-011` and `CHG-20260808-011` under `CONTEXT.md › 衍生 SPEC 索引`.
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
| 2026-08-12 | Project owner / `CHG-20260812-013` | Added the mandatory XSS classification. Current POC remains `XSS_NOT_APPLICABLE`; future renderer or privileged JavaScript work must re-enter the tiered XSS gate. |
| 2026-08-12 | Project owner / `CHG-20260812-014` / ADR-20260812-006 | Required exact complete-source publication to remote `staging` before release build/system integration, decomposed manifest/source/environment/build/install/uninstall acceptance into serial tickets and made the first packaged version an immutable source/toolchain/manifest/artifact evidence record. |
| 2026-08-13 | Project owner / `CHG-20260813-015` / ADR-20260813-007 | Replaced the shared OS-TEMP 05S1 test root with one exact project-owned runtime namespace per plugin checkout/worktree. Added AC-13 and returned dependent in-flight acceptance tickets to change control. |
| 2026-08-14 | Project owner / `CHG-20260814-018` / ADR-20260814-010 | Approved revision 03: Johnny becomes the sole reviewer-owned orchestration gateway; implementers receive no gateway capability and must also prove effective host multi-agent tools absent. 06A remains evidence, 06B/06C are superseded by 06G0P-06G4; schema preflight places 06G0P before transport proof. |

## Approval record

- Decision maker: Project owner
- Date: `2026-08-08 (Asia/Taipei)`
- Approval scope: Full `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X`, including owner-approved revision 03 of AC-09/AC-10 and AC-11 through AC-13; tickets may now be planned, but each implementation still requires its own delivery-confirmation receipt and only the named reviewer through Johnny's gateway may orchestrate the implementation task. The owner separately authorized only the future exact 04D staging publication after 04A/04B integration and 04C approval.
