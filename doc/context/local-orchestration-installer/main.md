# Local Orchestration Adapter and Detachable Installer — Wayfinder / Architecture / Grill Context

| Field | Value |
| --- | --- |
| Context state | `CODEX_CLI_CAPABILITY_VERIFIED / TICKET_05_DISPATCH_PREPARED / TICKET_04_DEPENDENCY_WAIT` |
| Router event | `ACTION_COMPLETED → TICKET_SELECTION → GRILL → IMPLEMENT` |
| Delivery stage | `POC` |
| Requirement change | `CHG-20260808-011` |
| Baseline | `a43da12` (`docs: close ticket 03 and halt ticket 04`) |
| Control-plane owner | Codex / current `main` worktree |
| Implementation owner | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245` / Ticket-05 allocation `aln_local_orchestration_install_05_20260809` after exact dispatch commit synchronization |
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

Initial review `dac99fd` returned `CHANGES_REQUESTED` with CR-73..CR-79. The
approved SPEC and user outcome are unchanged. CR-73 is a control-plane ticket
defect: the original closure omitted the installer-owned local marketplace
source required by the documented CLI. Corrected closure
`CLOSURE-LOCAL-INSTALL-T05-02` defines that source as an ephemeral, strictly
proved locator below the canonical installer root and aligns commands/JSON,
receipt identity, cleanup, absence proof and evidence matrices with the public
CLI. The same Ticket-05 task, worktree, branch, allocation and receipt remained
active for one additive correction. The correction review below supersedes
that active state; no further implementation continuation is permitted.

## Ticket 05 correction review convergence

The one permitted correction review covered implementation commits `c2ea3f8`,
`3f6c41a`, `13d02de` and final handoff `4c9525b`. Focused/full tests, strict
typing, in-memory compile and diff checks pass, but CR-80..CR-85 remain within
the frozen `CLOSURE-LOCAL-INSTALL-T05-02`: the adapter still rejects documented
CLI JSON while accepting empty mutation output; source/proof identity is not
bound to the canonical install root; real timeout/filesystem failures escape;
cleanup is not absence-verified; foreign same-name plugin state reaches
mutation; and red/reverse/byte-level Git evidence is not reproducible.

Router outcome is `CONVERGENCE_REVIEW_REQUIRED`. Ticket 05 returns to the
control plane for architecture/ticket decomposition. No third correction,
integration, new branch/worktree, Ticket-04 implementation, live registration,
target-project write, push, deployment or schedule is authorized.
Ticket 04 remains `PLANNED / DEPENDENCY_WAIT`.

## Ticket 05 control-plane decomposition

On 2026-08-10 the project owner instructed the control plane to begin the
Workflow §8.1 decomposition. The approved SPEC, host, one-click-removal outcome
and external capability evidence are unchanged; this is ticket architecture
repair, not a requirement change.

Parent Ticket 05 is `SUPERSEDED / CONVERGENCE_DECOMPOSED`. Its rejected branch
`codex/implementation-codex-cli-host-adapter-05`, implementation/docs SHAs,
reviews, allocation and receipt remain immutable evidence. The allocation is
released and the receipt is closed/non-reusable. Rejected source is not an
input to new implementation.

The finite replacement chain is:

1. Ticket 05A: documented CLI list DTOs, canonical installer-owned source proof,
   same-name/foreign-state collision gate and finite zero-mutation preflight.
2. Ticket 05B: documented add DTOs, exact receipt, effect journal before parse
   and absence-verified current-attempt compensation.
3. Ticket 05C: documented remove DTOs, strict receipt admission, conjunctive
   plugin/marketplace/path absence, replay isolation and full lifecycle support.

Only 05A is selected. It uses the same named implementation task and same sole
implementation worktree, but a single new-ticket branch from the clean control
baseline; the rejected parent branch remains only a Git reference. 05B, 05C and
04 remain dependency-waiting. No second worktree, concurrent branch, live Codex
mutation, target-project access, packaging, push, deployment or schedule is
authorized.

After the one permitted correction review, independent reconfirmation reproduced
explicit-null admission, prefixed version value and relative canonical-root
admission. The owner then explicitly ordered re-dispatch according to that
verified state. This is a single-use convergence override for one final additive
repair on the existing 05A branch/worktree with `gpt-5.6-terra` at `xhigh`.
Allocation and receipt stay unchanged; 05B, 05C and 04 remain blocked. Failure
of the following independent review ends this lane as `SUPERSEDE_REQUIRED`; it
does not authorize another same-ticket correction or any new branch/worktree.

The terminal review of final implementation `97ab31c` and handoff `4fc81a5`
passed A1 through A4, focused/full/type/compile/scope checks, the complete path
and authority-bypass probes, and five independent reverse mutations. It did not
close A5: implementation-local `.mypy_cache` files were rewritten inside the
owner turn despite the no-hidden-cache rule and the handoff's contrary claim,
and the branch-local handoff reused canonical progress ID
`PRG-20260810-087`. Ticket 05A is therefore `BLOCKED / SUPERSEDE_REQUIRED`.
No further 05A dispatch, branch/worktree, integration or Ticket 05B/05C/04
start is authorized without a new owner/control-plane decision.

The owner then granted exactly that bounded decision: one evidence-only cleanup
on the existing task/worktree/branch at `4fc81a5`. It permits removal of only
generated Python/mypy/pytest caches beneath the implementation worktree,
cache-free verification, and one docs-only correction that assigns the
branch-local final handoff reserved ID `PRG-20260810-091` and corrects its
hidden-state claim. It grants no source/test change, implementation commit,
new branch/worktree, integration or 05B/05C/04 start. The next review is limited
to CR-90, CR-91 and A5.

That bounded review passed. Repaired handoff `fb755268` changes only the branch
progress report; the assigned worktree and external reviewer cache are clean.
Independent focused `16/16`, full `172/172`, strict mypy `82` files, in-memory
compile, source sentinel and diff checks close CR-90, CR-91 and A5. Ticket 05A
is `APPROVED / READY_TO_MERGE`; integration and any 05B dispatch remain separate
Router actions.

The guarded integration preflight then found one append-only evidence-ledger
conflict: control `d54c0bd` and branch `fb755268` both extend
`doc/WorkProgressReport.md` from `d90b69e`. Source and tests are conflict-free,
but the ledger cannot be silently selected or overwritten. Integration is
`HALT / OWNER_RESOLUTION_REQUIRED`; 05B remains dependency-waiting.

The owner authorized a ledger-preserving resolution. Merge `b22c6c4` retains
both parents and every control/implementation progress record; only Git conflict
markers were removed. Post-merge focused `16/16`, full `172/172`, strict mypy
`82` files, compile, sentinel, diff and no-cache readbacks pass. Ticket 05A is
integrated, its allocation is released and its branch remains read-only
evidence. Ticket 05B is now the next unblocked planned ticket; no allocation or
dispatch was created by the merge authorization.
