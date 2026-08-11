# Local Orchestration Adapter and Detachable Installer — Wayfinder / Architecture / Grill Context

| Field | Value |
| --- | --- |
| Context state | `TICKET_05B4_REFREEZE_READY` |
| Router event | `REVIEW_APPROVED(05B3C) / GUARDED_INTEGRATION / ACTION_COMPLETED / TICKET_SELECTED(05B4)` |
| Delivery stage | `POC` |
| Requirement change | `CHG-20260808-011` |
| Baseline | `3367136` (`docs: decompose 05B3B identity admission`) |
| Control-plane owner | Codex / current `main` worktree |
| Implementation owner | 05B3A, 05B3B1 and 05B3C are integrated and released; 05B3B is terminal rejected; 05B4 is unallocated pending control-plane refreeze |
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

## Risks, resolved capability and re-entry

- Inno Setup 6.7.3 is installed per user from the official Winget manifest. Its installer digest, valid Pyrsys B.V. signature, registry version and one successful bundled-example compile are verified. This is build-tool capability only; no release executable is claimed by this Context.
- The official Codex plugin CLI lifecycle was verified with one disposable owner-authorized local marketplace/plugin: add, install, structured list, exact source/installed hash equality, plugin remove, marketplace remove and final plugin/marketplace/path absence all succeeded. No target project or existing plugin was changed. This proves the public host mechanism, not production adapter correctness.
- Ticket 05 is the bounded adapter slice required to turn that evidence into reviewed source. Ticket 04 waits for Ticket 05 integration. A different CLI contract, hidden config requirement or inability to prove exact absence returns `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill` or typed `BLOCKED`; it cannot be replaced by broad cache deletion.

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

Ticket 03 is dispatched under `hnd_local_orchestration_install_03_20260809`,
allocation `aln_local_orchestration_install_03_20260809` and receipt
`rcpt_local_orchestration_install_03_20260809`. The existing implementation
worktree creates only `codex/implementation-host-capability-gate-03` from the
dispatch commit. No live host or schedule authority is included.

## Ticket 03 completion and Ticket 04 gate

Ticket 03 completed as the bounded recorded capability gate: implementation
`16597b6`, additive H7 proof-boundary correction `673ff7c`, final independent
review `5601594` and guarded merge `60cb8cf`. Final verification passed 9/9
Ticket tests, 156/156 full discovery, strict mypy, compile/source checks,
actual-Git isolation and the focused H7 reverse mutation. The sole
implementation worktree is clean and detached at the merge; its integrated
branch and allocation are released.

At Ticket-03 closure this result did not create a live host adapter: Codex and
Claude remained `UNVERIFIED`, no `ISCC.exe` was available, and Ticket 04 entered
`PLANNED / BLOCKED`. That historical halt was resolved by the later
owner-authorized `PRG-20260809-077` toolchain and disposable CLI capability
probe. It did not retroactively change Ticket-03 source or claim production
support.

Ticket 05 used the existing sole implementation worktree and remains the gate
for Ticket 04. Its correction review now requires convergence, so there is no
active implementation continuation. No additional worktree, second live
registration or schedule is authorized.

## Ticket 05 initial review and corrected closure

- Initial review: `PRG-20260809-079`; `dac99fd`; `CR-73..CR-79`.
- Corrected closure: `PRG-20260809-080`;
  `CLOSURE-LOCAL-INSTALL-T05-02`.

## Ticket 05 correction review convergence

- Correction return: `c2ea3f8`; `3f6c41a`; `13d02de`; `4c9525b`.
- Review: `PRG-20260809-081`; `593e33a`; `CR-80..CR-85`;
  `CONVERGENCE_REVIEW_REQUIRED`.

## Ticket 05 control-plane decomposition

| Item | Reference / state |
| --- | --- |
| Decomposition | `PRG-20260810-082`; parent Ticket 05 `SUPERSEDED / CONVERGENCE_DECOMPOSED` |
| Ticket 05A event chain | `PRG-20260810-083 -> PRG-20260810-084 -> PRG-20260810-085 -> PRG-20260810-086 -> PRG-20260810-087 -> PRG-20260810-088 -> PRG-20260810-089 -> PRG-20260810-090 -> PRG-20260810-091 -> PRG-20260810-092 -> PRG-20260810-093 -> PRG-20260810-094` |
| Ticket 05A integration | `b22c6c4`; `DONE / APPROVED / INTEGRATED` |
| Ticket 05B | See the current reference below |
| Ticket 05C / 04 | `PLANNED / DEPENDENCY_WAIT` |

## Ticket 05B current reference

- Ticket / closure: `05b-codex-cli-transactional-registration` /
  `CLOSURE-LOCAL-INSTALL-T05B-02`.
- Event chain: `PRG-20260810-095 -> PRG-20260810-097 -> PRG-20260810-098 ->
  PRG-20260810-099 -> PRG-20260810-101`.
- Implementation return: `1a269411` / `ed74589`.
- Authoritative review: control commit `24227ac`, findings `CR-98..CR-104`.
- Current state: the old 05B closure is immutable
  `SUPERSEDED / CONVERGENCE_DECOMPOSED`. Integrated 05S1-05S4 permit new
  children 05B1-05B4; only pure no-effect 05B1 is dispatched. 05C/04 remain
  dependency-waiting.

## Staging-first convergence decision

The owner directed the control plane to establish isolation before rewriting
the blocked lifecycle tickets. The architecture now separates two evidence
levels:

- `05S` owns a disposable, stateful child-process/filesystem Codex contract
  staging environment. Fresh persisted state and actual sandbox files are the
  oracle for add/list/remove/absence; no result may be manufactured from the
  request or a queued fake response. It cannot invoke live Codex or touch a
  target project.
- Ticket 04 retains a later disposable Windows user-profile smoke gate for the
  real `Setup.exe`/uninstaller. Current host inspection found Windows Sandbox
  absent, Hyper-V management unavailable to this control process and Docker on
  an inactive Linux context; none is falsely recorded as a usable Windows
  package staging provider.

This is a verification-architecture refinement under the approved SPEC and
does not change AC-01 through AC-08. Ticket 05B stays paused as immutable
evidence. After 05S is independently approved and integrated, 05B, 05C and 04
must be refrozen with explicit staging evidence dependencies before dispatch.

The initial 05S implementation `18b99de` and handoff `2bed349` are immutable
evidence. Independent review found the harness was not a runtime-compatible
bounded command port, emitted non-official mutation DTOs, depended on a fixed
sibling worktree, leaked roots when that topology was absent, and accepted
incoherent persisted states. `CLOSURE-LOCAL-INSTALL-T05S-02` is the one permitted
same-branch correction; no new worktree or replacement branch is allowed.

Revision-02 corrections `ca5754d` and `832b1dc` plus handoff `ccb55bd` failed
terminal review with `CR-112..CR-117`. The required full command fails R12 from
a clean exported checkout; foreign installed truth lacks a physical payload;
SemVer, path-boundary and real process-exception evidence remain incomplete.
No additional implementation dispatch or downstream refreeze is active.

## Ticket 05S4 independent review boundary

The immutable `e4d00dd` handoff passes 6/6 focused, 201/201 full and strict
typing, but independent O4/O6 probes reproduce two blocking defects. Duplicate
foreign identities are accepted and returned as list truth (CR-126), and an
ordinary fixture failure after command creation leaves the fixed command file
(CR-127). Revision-02 keeps the same ticket, task, sole implementation
worktree and branch and may change only the four named oracle/test paths. 05B,
05C, Ticket 04 and the reviewer-only orchestration change remain blocked from
implementation while this sole lane is active.

## Reviewer-only Codex role-profile sequence

`CHG-20260811-012` leaves AC-01 through AC-08 and completed/active 05 tickets
unchanged. AC-09/AC-10 add a separate serial sequence:

1. `06A` proves in a disposable `CODEX_HOME` that the current Codex custom-agent
   layer can expose orchestration tools to reviewer while disabling them for
   implementation. Current shell discovery resolves the WindowsApps Codex
   executable but direct invocation returns access denied, so support is not
   presumed; an unprovable boundary is typed `ROLE_ISOLATION_UNPROVEN`.
2. Autonomous Ticket 04 implements the receipt-bound reviewer-only fake effect
   gate after 06A is reviewed `SUPPORTED`.
3. `06B` owns/reads/removes the two profiles and preserves foreign/global
   config; `06C` composes profile proof with the authority gate.
4. Windows package Ticket 04 waits for 05A-05C and 06A-06C.

05S4 revision-02 correction `02f33ef` / handoff `52ab9c0` passed its final
independent review: focused 10/10, full 205/205, strict type/compile over 102
files and the exact CR-126/CR-127 probes passed. Guarded integration is
complete at merge `4af381c`; the allocation is released and receipt closed.
The project owner then explicitly
authorized a second named implementer for independent work. Ticket 06A may run
in `workflow-implementer-2` while control reviews 05S4 because its four new
staging/test paths do not overlap the oracle correction. Each task is bound to
one ticket/worktree and cannot control the other; no automation, live Codex
mutation or target-project action is authorized.

Ticket 06A implementation `38e9a8b` and handoff `f6f186f` passed independent
review from a fresh immutable export: focused 11/11, full 206/206, strict
full-tree mypy/compile over 100 files, same-name foreign-sentinel preservation
and exact teardown all passed. The independently repeated actual installed-host
probe nevertheless returns `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN /
ACCESS_DENIED / OUTPUT_UNAVAILABLE`. Synthetic effective-readback injection is
contract evidence only and cannot replace host proof. The implementation is
integration-authorized as truthful fail-closed evidence; autonomous Ticket 04
and 06B/06C remain stopped pending separately authorized capability change.

Guarded merge `de4141e` preserves the control review as first parent and the
reviewed 06A handoff as second parent. The progress-ledger collision was
resolved without amending either immutable source commit: the lane-local
PRG-141 return is recorded on main as unique PRG-146. Post-merge focused
11/11, full 216/216 and strict mypy/compile over 106 files passed. 06A is
complete and integrated as truthful blocked evidence; its allocation is
released and receipt closed.

Owner decision `PRG-20260811-106` supersedes combined 05S as an implementation
lane. New children are serial and single-purpose: 05S1 owns only disposable
environment provision/teardown; 05S2 owns only a generic bounded child runner;
05S3 owns only documented Codex protocol fixtures; 05S4 owns only persisted
lifecycle/file truth. Transaction, compensation and receipts remain in 05B/05C,
and real `Setup.exe`/uninstaller isolation remains Ticket 04's separate Windows
provider gate. The control reviewer owns acceptance and may not patch the
implementation. Only 05S1 is selected, with no active dispatch.

05S1 dispatch is now authorized under ticket-doc baseline `3f685a9` and its
separate handoff-doc commit. Its implementation scope remains environment-only;
05S2–05S4 receive no authority from this dispatch.

Ticket 05B1 implementation `fbedefc` / handoff `6969d44` passed exact scope,
focused 4/4, full 209/209 and strict type/compile over 104 files, but its final
initial review found CR-128..CR-132. There is no independent expected auth
policy in the proof request, so an echoing proof fake issues a receipt for a
foreign observed policy. Proof-port exception semantics were not frozen;
`RuntimeError` currently escapes. The journal also accepts plugin attempt
states after a still-ambiguous or pre-existing marketplace, and committed TDD
omits required path/port cells. 05B1 is stopped for one control-plane refreeze;
05B2-05B4 remain blocked.

Control review `97cce99` refreezes those findings as
`CLOSURE-LOCAL-INSTALL-T05B1-02`: a separate expected auth policy, a typed
proof-port failure with explicit unexpected/process-control propagation, the
seven exact legal journal states, and truthful path/port/exception tables. One
additive correction is dispatched to the same task, worktree and branch with
the original allocation/receipt; no new lane exists. The next review is final.

Final correction implementation `dc57ff9` and handoff `1df30ae` close
CR-128..CR-132. Independent immutable-export verification passes the full
suite and strict types; direct foreign-auth, 16-state journal, exception,
metadata-only receipt and three reverse-mutation probes all pass. Ticket 05B1
is `APPROVED / READY_TO_MERGE`; 05B2 remains dependency-waiting until guarded
integration completes.

Guarded merge `bbc7de5` integrates 05B1 after post-merge focused 7/7, full
223/223, strict mypy 108 files and zero-residue verification. Its allocation is
released and receipt closed. Ticket 05B2 command-attempt classification is now
the next unblocked serial child; 05B3-05B4 remain dependency-waiting.

Ticket 05B2 is refrozen as a pure production classifier: it consumes integrated
05B1 journals plus finite command-start truth, never imports the test-owned
05S2 runner, and performs no effect. Pre-start unavailable/access-denied/
generic-launch failure grants no authority; every started ambiguous failure grants only `MAY_EXIST`; exact
fresh/pre-existing confirmations map to `OWNED`/`PREEXISTING`. All other
command/journal pairs fail closed. The separate handoff record binds the exact
ticket-doc commit before dispatch.

The submitted 05S1 implementation `e0898cd` and handoff `ecce06a` failed the
independent E3/T3 physical root-reparse probe. A real Windows junction is a
`ReparsePoint`, but Python 3.11 `Path.is_symlink()` is false; teardown reads the
external marker and reports `CHILD_ESCAPE` instead of refusing it at the root
boundary. Review CR-118/CR-119 records the implementation and evidence defects.
05S1 is now `CONVERGENCE_REVIEW_REQUIRED`; no correction, merge or downstream
dispatch is active.

The project owner explicitly authorized one bounded 05S1 exception after that
review. Correction handoff
`hnd_local_orchestration_install_05s1_corr1_20260811` may change only the
environment reparse detector and its physical root-junction test on the same
branch and worktree. The test may use a finite `shell=False` process solely to
construct the Windows junction; no product process runner or 05S2 behavior is
authorized. Any blocker in the next review stops again.

The final exported review of correction `41d5ce4` and handoff `e1087d3`
passed E1-E4/T1-T4, including a physical Windows root junction that is blocked
before marker access. Focused 5/5, full 177/177, strict mypy across 86 files,
compile, source guards and zero-residue readbacks passed. 05S1 is
`APPROVED / INTEGRATION_AUTHORIZED`; 05S2 remains blocked until the guarded
integration is recorded.

Guarded merge `504a3ec` preserves both reviewed parents and all progress-ledger
records. Post-merge verification repeated focused 5/5, full 177/177, strict
mypy across 86 files, compile and zero-residue checks. 05S1 is
`COMPLETE / APPROVED / INTEGRATED`; the unique serial continuation is 05S2.

05S2 is frozen under closure `CLOSURE-LOCAL-INSTALL-T05S2-01`. It owns only a
strict generic child-process request/result union, exact argv/environment/cwd,
finite timeout termination and a deterministic fixture. Physical host probes
confirmed the intended Windows distinctions before dispatch: missing absolute
executable is WinError 2, an existing directory executable is WinError 5, and
oversized argv is FileNotFoundError-class WinError 206 and must map to generic
launch failure. No Codex, plugin, installation or target-project state is in
scope. 05S3 remains blocked.

Submitted 05S2 implementation `52d7455` and handoff `72ccfaa` failed terminal
review CR-120..CR-123. A physical replacement of the owned cwd by a Windows
junction was accepted and a real successful child wrote external bytes. An
embedded-NUL absolute executable crossed validation and leaked `ValueError`.
The committed late-sentinel timing is shorter than the fixture delay, and the
control-plane ticket omitted a finite termination-failure result/cleanup bound.
05S2 was `CONVERGENCE_REVIEW_REQUIRED`. Owner override
`OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01` now refreezes only the four
reviewed gaps as `CLOSURE-LOCAL-INSTALL-T05S2-02`: live non-reparse ownership,
NUL-free executable admission, truth-preserving late-write evidence and finite
kill/reap failure semantics. One additive correction is permitted on the same
branch/worktree; integration and 05S3 remain blocked pending the final review.

The final exported review of correction `34babbd` and handoff `c324c52` passes
the refrozen NUL, physical reparse, extended late-write and bounded kill/reap
matrix. It also independently proves CR-124: a first run-wait `OSError` is not
a timeout, but the current runner kills/reaps and returns confirmed
`TIMEOUT_AFTER_START`. The P3/T3 ticket design omitted a truthful finite state
for this started-child observation failure. The correction authorization is
consumed, so 05S2 is stopped without integration or downstream dispatch.

Owner authorization resumes 05S2 as revision 03 without reopening revision 02.
Closure `CLOSURE-LOCAL-INSTALL-T05S2-03` covers CR-124 only. It requires a
distinct `WAIT_FAILED_AFTER_START` result after first-wait `OSError` plus
successful bounded cleanup, and a required `RUN_TIMEOUT` or
`RUN_WAIT_OS_ERROR` trigger on every unconfirmed termination failure. The same
task, branch and worktree are retained; 05S3 remains blocked pending review.

The final revision-03 review approves implementation `33a8fa9` and handoff
`dba0621b`. Independent execution from a fresh immutable export passed focused
12/12, full 189/189, strict mypy and compile over 91 Python files, all six
trigger/cleanup failure cells, result-separation probes and zero-residue
readback. CR-124 is resolved and guarded integration is authorized. 05S3 is
still undispatched in this turn.

Guarded merge `6e24e06` preserves control approval `c97b754` and reviewed
handoff `dba0621b` as its two parents. The only conflict was the progress
ledger; all PRG-114 through PRG-124 records were retained once in order.
Post-merge focused 12/12, full 189/189, strict mypy and compile over 91 files
passed with zero residue. 05S2 is `COMPLETE / APPROVED / INTEGRATED`; 05S3 is
the next ready ticket but remains undispatched at the end of this turn.

Ticket 05B2 correction `8a7bf95` closes CR-133/CR-134 and guarded merge
`c97505c` integrates its strict command-attempt classifier after independent
focused 7/7, full 230/230 and strict-mypy verification. The next serial child
is 05B3, refrozen as a compensation-only coordinator rather than another full
transaction: an exact current-attempt manifest plus 05B1 journal authorize
only plugin-first current-attempt removals; five distinct typed port calls run
without finite-failure short-circuiting; fresh marketplace, plugin and
installed-path absence alone reduce retry authority. 05B4 remains blocked
until 05B3 is independently approved and integrated.

## Ticket 05B3 convergence decomposition

Terminal review `9716704` proved that unrestricted Python callable inspection
cannot satisfy the frozen zero-descriptor boundary. ADR-20260811-004 preserves
the required user behavior while replacing the implementation architecture:

- 05B3A owns only static plain-method admission into a frozen typed capability.
- 05B3B owns only pure plan/reduce behavior over integrated 05B1 journal truth.
- 05B3C later owns all execution and exact observation composition.

05B3A and 05B3B have disjoint files and no dependency on one another's
unintegrated source, so the two named owners may run concurrently. Their old
branches remain immutable references. Each owner must create its own single
ticket branch from the reviewed control handoff inside its existing worktree;
no new worktree, copied rejected source or cross-lane read/write is permitted.

## 05B3A / 05B3B allocation record

| Ticket | Owner / existing worktree | Recorded branch | Handoff / allocation / receipt | Current disposition |
| --- | --- | --- | --- | --- |
| 05B3A | task `019fcc9c-f34f-7d53-a313-c70c90bf3245` / `workflow-implementation` | `codex/implementation-codex-safe-port-capability-05b3a` | correction `hnd_local_orchestration_install_05b3a_r02_20260812`; released `aln_local_orchestration_install_05b3a_20260811`; closed `rcpt_local_orchestration_install_05b3a_20260811` | Integrated by `8a13eb7`; no active lane |
| 05B3B | task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` / `workflow-implementer-2` | `codex/implementation-codex-compensation-reducer-05b3b` | parent correction handoff and old allocation/receipt closed | Terminal rejected handoff `4d5bbef`; immutable ancestor only |
| 05B3B1 | task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` / `workflow-implementer-2` | existing `codex/implementation-codex-compensation-reducer-05b3b` | closed `hnd_local_orchestration_install_05b3b1_20260812`; released `aln_local_orchestration_install_05b3b1_20260812`; closed `rcpt_local_orchestration_install_05b3b1_20260812` | Integrated by `ac91290`; no active lane |

The previous 05B3 allocation is closed as terminal rejected evidence; the
completed 06A and 05B3A allocations were released by guarded integration.
No implementation lane is active. The owners may not read the other's worktree
or use uncommitted cross-lane source; 05B3C remains unallocated until its
control-plane ticket refreeze and receipt are committed.

Revision-02 independent reviews are recorded in the unique review reports.
05B3A closes CR-137 through CR-139 and is integrated by `8a13eb7`.
05B3B closes CR-140 through CR-143 but exposes CR-144/CR-145: a recursively
malformed exact plan identity can escape as `PydanticSerializationError`.
Workflow.md §8.1 therefore requires control-plane convergence; no third
correction, 05B3B integration or 05B3C dispatch is authorized.

## Ticket 05B3B1 convergence child

Owner authorization selects one finite child for CR-144/CR-145. 05B3B1 owns
only recursive plan-identity admission before comparison/serialization. It
uses a new closure, allocation and receipt but retains implementer-2's existing
clean worktree and branch; no `FRESH_BRANCH_REQUIRED` evidence exists. The
terminal review must validate the complete resulting reducer against parent
R1-R5 and child I1-I5. 05B3C remains unallocated until that child is approved
and integrated.

Terminal review `382cc954eb3f59bbeb3656a1dcfe9d78ab686a59` approved the child,
and guarded merge `ac912904ccf83a71c87512d2e8b29e5f6f45fa8b` integrated the
reviewed handoff. The allocation is released and the receipt is closed. 05B3C
is now eligible only for a fresh control-plane ticket refreeze; no
implementation dispatch has occurred.

## Ticket 05B3C composition freeze

Closure `CLOSURE-LOCAL-INSTALL-T05B3C-01` owns only the new coordinator, its
focused test and root exports. C1-C8 freeze zero-call admission, exact five-step
mapping, five finite return failures, manifest-bound observation truth, all 20
operation exception cells and five independent reversals. Implementer-2 is
selected in the existing worktree; one new ticket branch from the reviewed
control baseline is allowed. The reviewed freeze is `df24448`; dispatch is
bound to PRG-20260812-187 and no new worktree is allowed.

Terminal independent review approved implementation `b44cb38` and docs-only
handoff `6d7dd37`. Exact C1-C8, five isolated reversals, focused/full/type/
compile, dependency-blob, scope and residue checks passed. Guarded integration
is the only legal continuation. 05B4 retains the separate responsibility for
fresh registration admission and exact receipt/proof/journal/oracle binding.

Guarded merge `d8f6127` integrated the exact reviewed 05B3C handoff with the
formal review as first parent. Post-merge focused 6/6, full 260/260, strict
mypy and compile over 116 files, exact blob, source/diff and residue checks
passed. The allocation is released and the receipt is closed. 05B4 is now
eligible only for control-plane refreeze; no implementation dispatch exists.
