# Environment Capability Bootstrap Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-ENVIRONMENT-CAPABILITY-BOOTSTRAP-20260815-01M0E2C4B6S8T0R2A4P6D8F0H2` |
| Status | `REVISION_01_APPROVED / REVISION_02_OWNER_REVIEW_REQUIRED` |
| Author / baseline | Architecture owner / `main` / `2701ed563f26e116db69e8e4fcb84024754c9498` |
| Context | `doc/context/environment-capability-bootstrap/main.md` |
| Shared Context | `CONTEXT.md` sealed by `CHG-20260816-025` |
| PRD / change | `PRD-20260815-024`, `PRD-20260816-025` / `CHG-20260815-024`, `CHG-20260816-025` |
| Architecture decision | `ADR-20260815-013`, `ADR-20260816-014` |
| Implementation language | Python 3.11, Pydantic/frozen typed contracts and `mypy --strict`; platform adapters remain injected boundaries |
| Delivery profile | `HIGH_ASSURANCE` for acquisition, activation, resource enforcement, credential and removal effects; pure planners/reducers may be separately admitted after approval |

## Problem and goal

The control plane currently assumes that required development tools and Python dependencies are
already available. That assumption prevents reliable validation and can tempt an Agent to
install or modify software during implementation. A general solution must bootstrap the minimum
capabilities needed to control a project while preserving the user's existing environment,
keeping Johnny outside the target project and making every Johnny-owned artifact removable.

The observable result is a typed `EnvironmentCapabilityPlan` and boundary-specific evidence that
states exactly which capabilities are reused, Johnny-owned, guided, not required or blocked. A
valid plan can launch only resource-enforced work. It never grants ticket or external-effect
authority.

## Scope

- One-shot discovery, compatibility evaluation and planning for Git, control Python,
  project-native runtimes, Docker, build and deployment tool capabilities.
- Per-user reversible acquisition and atomic activation of exact Johnny-owned artifacts.
- Separate `CONTROL_BOOTSTRAP`, `PROJECT_BASELINE` and `TICKET_OVERLAY` gates.
- Immutable side-by-side environment identity, cache/write isolation and resource enforcement.
- Boundary-only capability evidence, event-based install grants, drift handling, detach and
  plugin uninstall cleanup.
- Local-inference compatibility and one-shot CPU/RAM/GPU/VRAM reservation evidence. Local model
  download, training implementation, weights and dataset governance remain a future independent
  high-assurance scope.
- Root README guidance for setup, team handoff and removal.

## Out of scope

- No implementation ticket, source mutation, installer download, package build or live install.
- No package-manager replacement, global environment manager or target-project dependency
  manager.
- No automatic system/admin changes, EULA acceptance, reboot, login or credential creation.
- No deployment, push, release, signing, migration or Provider effect.
- No heartbeat, cron, watchdog, scheduled probe, background update or network retry loop.
- No macOS/Linux-host production claim in version one; Linux Docker guests are allowed.
- No plugin-specific file, worktree, environment manifest, cache or telemetry directory in a
  controlled project.

## Core invariants

### EC-01 — Parallel ownership

Target projects own their native manifests, source, tests, Context, SPEC, tickets, reviews and
handoffs. Johnny owns only its per-user runtime root, environments, caches, mappings, grants,
evidence and receipt bindings. Neither side imports, links, mounts as writable runtime state or
deletes the other. A target `.gitignore` is never changed for Johnny.

### EC-02 — Existing environment first

The planner first evaluates the user's/project's existing tool version against exact approved
project constraints and capability probes. A compatible tool is `REUSE_EXISTING` and remains
foreign-owned/read-only. Johnny never upgrades, downgrades, replaces or globally configures it.
An incompatible tool is not an error by itself: the plan may select a Johnny-owned side-by-side
artifact or `GUIDE_USER`. If neither is authorized and safe, the needed gate is blocked.

### EC-03 — Control Python separation

`CONTROL_PYTHON` is a Johnny-owned pinned Python 3.11 runtime containing only the locked
control-plane dependency set, including strict mypy. It cannot be used as implicit
`PROJECT_PYTHON`, modify project lockfiles or import unapproved target packages. Project Python
comes only from project-native manifests/constraints and an exact `PROJECT_BASELINE` plan.

### EC-04 — Capability-gated installation

Automatic installation is legal only when the artifact is:

1. per-user and non-admin;
2. reversible through a Johnny ownership ledger;
3. exact-versioned and locked by digest;
4. acquired from a bundled or official allowlisted source;
5. signature/hash verified before activation;
6. free of an unaccepted EULA, login, reboot or system/global change.

Anything outside those conditions is `USER_ACTION_REQUIRED` or
`SEPARATE_APPROVAL_REQUIRED`. Approval describes the exact action and never broadens to future
versions or unrelated tools.

### EC-05 — Core and conditional tools

Git is a `CONTROL_BOOTSTRAP` requirement. An exact portable Git artifact is available as the
Johnny-owned fallback. The pinned `CONTROL_PYTHON` payload is also a control requirement.
Docker, project runtimes, SDKs, compilers and deployment tools are conditional and must not be
discovered, downloaded or blocked unless the current gate declares them.

### EC-06 — Immutable environment identity

Each Johnny-owned environment identity is derived from opaque project ID, capability kind,
platform/architecture and exact dependency-lock digest. A changed artifact or lock creates a new
candidate; it never mutates an active environment in place. The durable identity contains no
raw project path, repository URI or device fingerprint.

Read-only content caches may be shared after exact digest verification. Writable caches,
temporary files, logs, tool state, Docker names/volumes and process state are isolated by
ticket/worktree binding and cleaned through the ownership ledger.

### EC-07 — Atomic acquisition and activation

Acquisition stages into a new owned candidate, verifies source allowlist, version, digest and
signature, expands with path-traversal/reparse protection, runs a bounded capability probe and
atomically activates only the verified identity. Failure removes the candidate or retains exact
recovery evidence; the prior valid environment remains active. There is no background retry.

### EC-08 — Three admission gates

1. `CONTROL_BOOTSTRAP`: proves Router/control Git and `CONTROL_PYTHON` capabilities.
2. `PROJECT_BASELINE`: proves project-native manifest and base build/test tool compatibility.
3. `TICKET_OVERLAY`: proves only the extra tools and finite resource plan required by one exact
   ticket.

Handoff preparation before dispatch does not start implementation or consume ticket authority.
Implementation may not install, update or reconfigure a tool. Missing/drifted evidence returns
`ENVIRONMENT_CAPABILITY_CHANGED` and blocks/replans the affected gate before re-dispatch.

### EC-09 — Boundary-only evidence

Evidence is read at initial planning, after owned activation, before ticket dispatch, at a
declared review/build/deploy boundary and during detach/uninstall verification. Idle operation
performs zero model calls, Router turns, Git reads, environment probes, filesystem scans,
recurring timers and network requests.

`CapabilityEvidence` binds opaque project, gate, capability, source/ownership, exact version and
artifact/lock digest, adapter/probe revision, platform, finite resource-plan ref, observation
revision and result. It stores no Secret, raw path, URI, command output or device fingerprint.

### EC-10 — Resource plan and hard enforcement

Every launch plan contains finite positive caps for CPU, memory, disk/temp, processes,
containers, build workers and active lanes; unused dimensions are explicitly zero. The plan is
classified `LIGHT`, `STANDARD` or `HEAVY_APPROVAL` and is immutable for one exact work receipt;
an implementation plan must also bind its exact ticket. Retry, correction, commit, role
replacement and task restart do not reset or expand it.

| Class | CPU cap | Memory cap | Halt floor | Disk/temp | Processes | Containers | Workers | Lanes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `LIGHT` | lower of 25% of currently available CPU or one core-equivalent | lower of 25% of currently available RAM or 2 GiB | less than 1 GiB currently available RAM | 1 GiB | 8 | 0 | 1 | 1 |
| `STANDARD` | lower of 50% of currently available CPU or two core-equivalents | lower of 50% of currently available RAM or 4 GiB | less than 2 GiB currently available RAM | 5 GiB | 24 | 0 | 2 | 1 |
| `HEAVY_APPROVAL` | no default | no default | exact displayed plan | no default | no default | no default | no default | no default |

Only a ticket that explicitly requires the Docker capability may have a nonzero container cap.
`HEAVY_APPROVAL` is not a larger implicit preset: every dimension requires separate exact owner
approval.

- Windows Johnny-launched processes attach to a proved Job Object before untrusted/project work
  begins.
- Docker launches use native CPU, memory, process and storage controls plus namespaced resources.
- Build tools receive bounded worker/concurrency flags where supported.
- A required cap that cannot be hard-enforced is
  `HALT / RESOURCE_ENFORCEMENT_UNAVAILABLE`; an advisory-only fallback is forbidden.
- `HEAVY_APPROVAL` always requires a separately displayed exact plan and owner approval.

Capacity discovery is one-shot and stores only normalized available/cap values needed for the
decision, never hardware serials or a persistent device fingerprint.

### EC-10A — Local-model reservation priority

Every plan declares `HOSTED_INFERENCE`, `LOCAL_INFERENCE` or `LOCAL_TRAINING`.
`LOCAL_INFERENCE` first reserves the current model's required CPU, RAM, GPU and VRAM; Johnny may
plan only from the proved remainder. Insufficient residual capacity stops or postpones Johnny
work. It never terminates, pauses, reconfigures or steals resources from the local model.

`LOCAL_TRAINING` is always `HEAVY_APPROVAL`. While it is active, only Router/Senior control and
bounded read-only checks may run; Docker work, full test suites and other heavy tickets are
forbidden concurrently. This revision defines only resource/compatibility contracts. Model
download, tokenizer/model installation, training code, weight lifecycle, dataset ownership,
evaluation and release require a future separately approved high-assurance SPEC.

### EC-11 — Authority separation and one ticket receipt

`InstallGrant` authorizes activation of one exact tool artifact under the Johnny root. It has no
fixed time expiry but becomes invalid when the artifact identity changes, verification fails,
the owner revokes it or its owned installation is removed.

An `InstallGrant` and `CapabilityEvidence` never authorize ticket work. Each ticket has exactly
one valid Router receipt at a time. `ExecutionEnvironmentBinding` attaches the selected evidence
and resource plan to that same receipt; it is evidence, not a second execution receipt. A normal
same-ticket correction continues using the same valid receipt. Task/owner/worktree/baseline
replacement revokes the old binding and creates a replacement binding under the Router's exact
same-ticket authority rules.

External effects use a separate authority bound to exact owner, action, target, environment,
artifact digest and correlation. Development or install authority never implies deployment.

### EC-12 — Credential and login boundary

Credential requirements are `GUIDE_USER`. Login occurs only through an official UI, device-code
flow or OS credential store after separate approval. Johnny receives at most an opaque credential
alias and a finite capability result. Secret values, access tokens and raw provider output never
enter Router state, logs, receipts, plans or evidence.

### EC-13 — Detach and uninstall

`PROJECT_DETACH` closes that project's live execution bindings, grants/evidence mappings and
exact Johnny-owned writable state. Shared immutable artifacts/cache remain only when another
owned mapping still references them. It never changes the target project or foreign tools.

`PLUGIN_UNINSTALL` removes all exact ledger-owned runtime, tools, environments, cache, mappings,
InstallGrants, CapabilityEvidence and Router receipts/bindings. Missing/tampered ownership
evidence fails closed before broad deletion and reports bounded recovery state. Removal has no
expiry prerequisite and does not wait for the target project to adopt another workflow.

### EC-14 — Terminal, deployment and team portability

A ticket binding identifies the write-owning task/worktree, not a terminal window. A clean
terminal or machine may reproduce the project environment from project-native manifests and
bind the accepted commit/artifact through a new proved local environment. Deployment runners
may differ from development terminals and never depend on a Johnny path.

Engineering teams can use their own tools when compatible. A successor who removes Johnny uses
the project's native documentation and manifests without any cleanup inside the repository.

### EC-15 — Platform support

Contracts are platform-neutral. Version-one production adapters support Windows 10/11 x64.
Linux containers are supported only through a proved Docker adapter. A macOS or Linux host, an
unsupported CPU architecture or an unproved Windows resource adapter returns a typed unsupported
result and halts only the stage that requires it.

## User and data flow

```text
Current Router gate + approved project/ticket refs
-> one-shot capability discovery (no effect)
-> normalize project-native constraints and existing versions
-> EnvironmentCapabilityPlan
   -> REUSE_EXISTING -> bounded probe
   -> INSTALL_JOHNNY_OWNED -> exact InstallGrant -> stage/verify/activate/probe
   -> GUIDE_USER / SEPARATE_APPROVAL_REQUIRED -> stop with exact instruction
   -> NOT_REQUIRED -> no discovery or effect
   -> BLOCKED / UNSUPPORTED -> typed HALT for the affected gate
-> CapabilityEvidence
-> finite ResourcePlan + hard-enforcement proof
-> same-ticket Router receipt environment binding
-> one bounded execution
-> boundary readback / close / detach / uninstall
```

Failure at one capability does not invalidate unrelated gates. For example, missing Docker does
not block a non-container documentation ticket, and a missing deployment tool cannot block
ordinary local unit tests.

## Strongly typed contract notation

The following is contract notation. Python uses frozen validated equivalents, explicit
nullability, finite enums and no `Any`.

```text
enum EnvironmentGate { CONTROL_BOOTSTRAP, PROJECT_BASELINE, TICKET_OVERLAY }
enum CapabilityKind {
  GIT, CONTROL_PYTHON, PROJECT_PYTHON, DOCKER, PROJECT_RUNTIME,
  BUILD_TOOL, DEPLOY_TOOL, CREDENTIAL_SESSION
}
enum CapabilityDisposition {
  REUSE_EXISTING, INSTALL_JOHNNY_OWNED, GUIDE_USER,
  SEPARATE_APPROVAL_REQUIRED, NOT_REQUIRED, BLOCKED
}
enum CapabilityResult {
  READY_EXISTING, READY_JOHNNY_OWNED, USER_ACTION_REQUIRED,
  APPROVAL_REQUIRED, UNSUPPORTED, DRIFTED, INVALID
}
enum OwnershipKind { FOREIGN_READ_ONLY, PROJECT_NATIVE, JOHNNY_OWNED }
enum ResourceClass { LIGHT, STANDARD, HEAVY_APPROVAL }
enum ComputeWorkloadKind { HOSTED_INFERENCE, LOCAL_INFERENCE, LOCAL_TRAINING }
enum EnvironmentLifecycle { CANDIDATE, ACTIVE, SUPERSEDED, DETACHING, REMOVED, RECOVERY_REQUIRED }

struct CapabilityRequirement {
  CapabilityKind kind;
  VersionConstraint constraint;
  bool required_for_gate;
  EvidenceRefs constraint_refs;
}

struct EnvironmentCapabilityPlanItem {
  CapabilityRequirement requirement;
  CapabilityDisposition disposition;
  OwnershipKind ownership;
  optional<ArtifactIdentity> artifact;
  optional<InstallGrantRef> required_install_grant;
  CapabilityProbeRevision probe_revision;
}

struct EnvironmentCapabilityPlan {
  PlanId plan_id;
  ProjectId project_id;
  EnvironmentGate gate;
  PlatformIdentity platform;
  tuple<EnvironmentCapabilityPlanItem> items;
  ResourcePlanRef resource_plan_ref;
  ContentDigest plan_digest;
}

struct InstallGrant {
  InstallGrantId grant_id;
  CapabilityKind capability;
  ArtifactIdentity artifact;
  OfficialSourceIdentity source;
  ArtifactDigest digest;
  SignatureIdentity signature;
  UserScope user_scope;
  InstallOperation operation;
  GrantLifecycle lifecycle;
}

struct CapabilityEvidence {
  CapabilityEvidenceId evidence_id;
  ProjectId project_id;
  EnvironmentGate gate;
  CapabilityKind capability;
  OwnershipKind ownership;
  VersionIdentity version;
  ArtifactDigest artifact_or_lock_digest;
  CapabilityProbeRevision probe_revision;
  ResourcePlanRef resource_plan_ref;
  ObservationRevision observation_revision;
  CapabilityResult result;
}

struct ResourcePlan {
  ResourcePlanId plan_id;
  WorkReceiptRef work_receipt_ref;
  optional<TicketRef> ticket_ref;
  ResourceClass class;
  ComputeWorkloadKind workload_kind;
  PositiveCpuCap cpu;
  PositiveByteCap memory;
  PositiveByteCap disk_and_temp;
  NonNegativeCount process_cap;
  NonNegativeCount container_cap;
  NonNegativeCount worker_cap;
  NonNegativeCount lane_cap;
  optional<LocalModelReservationRef> local_model_reservation_ref;
  ResourceEnforcerRevision enforcer_revision;
  ContentDigest plan_digest;
}

struct LocalModelReservation {
  LocalModelReservationId reservation_id;
  ComputeWorkloadKind workload_kind;
  PositiveCpuCap reserved_cpu;
  PositiveByteCap reserved_memory;
  optional<PositiveGpuCap> reserved_gpu;
  optional<PositiveByteCap> reserved_vram;
  CapacityObservationRevision observation_revision;
  ContentDigest reservation_digest;
}

struct ExecutionEnvironmentBinding {
  EnvironmentBindingId binding_id;
  TicketRef ticket_ref;
  ReceiptRef router_receipt_ref;
  TaskRef task_ref;
  WorktreeRef worktree_ref;
  CommitId baseline_commit;
  tuple<CapabilityEvidenceRef> evidence_refs;
  ResourcePlanRef resource_plan_ref;
  BindingLifecycle lifecycle;
}
```

Raw PATH values, environment dictionaries, subprocess JSON and provider payloads are parsed and
normalized only at adapter boundaries. They never travel inward as strings or dynamic objects.

## Composition and dependency injection

The per-user Johnny launcher/installer is the Composition Root. It constructs a fresh bounded
graph for planning, activation, launch or removal; no global singleton is inferred from the
environment.

| Port | Responsibility | Forbidden behavior |
| --- | --- | --- |
| `CapabilityDiscoveryPort` | Read one named tool/platform capability once. | Repository-wide scan, recurring probe, persistent device fingerprint. |
| `ProjectConstraintPort` | Read exact project-native manifest constraints through approved refs. | Write target files or invent version constraints. |
| `ArtifactAcquisitionPort` | Stage one exact bundled/allowlisted artifact. | Arbitrary URL/package install, retry loop or activation. |
| `ArtifactVerificationPort` | Verify version, digest, signature and safe expansion. | Trust filename, caller claim or unsigned mutable latest. |
| `OwnedEnvironmentStore` | Create/activate/remove exact ledger-owned immutable environments. | Delete arbitrary/foreign paths or target content. |
| `CapabilityProbePort` | Prove one finite required behavior. | Treat command presence/version text alone as full capability. |
| `ResourceEnforcerPort` | Attach hard process/container/build caps before work. | Advisory-only limits or post-launch attachment race. |
| `CredentialGuidancePort` | Open/describe approved official login and return opaque alias/result. | Read, log or persist a Secret. |
| `CapabilityEvidenceStore` | Persist validated metadata-only plan/evidence/grant/binding. | Store raw path, command output, source, prompt, Secret or PII. |

Tests use deterministic fakes for every port. Windows Job Object, filesystem, process, Docker,
official acquisition and credential adapters require separate high-assurance tickets and live
staging acceptance before a production capability claim.

## Acceptance criteria

1. An existing compatible Git/Python/project tool is reused without any byte, configuration,
   environment-variable or Git-status change to that tool or target project.
2. An incompatible existing tool is preserved; the plan chooses an exact Johnny-owned
   side-by-side artifact, guided user action or typed block.
3. `CONTROL_PYTHON` is pinned Python 3.11 with a locked control dependency digest and strict
   mypy; it cannot satisfy `PROJECT_PYTHON` implicitly.
4. Missing Docker/build/deploy capability blocks only a gate that declares it required.
5. Automatic installation rejects admin/global/system/EULA/reboot/login cases before effect.
6. Acquisition rejects wrong source, mutable version, hash/signature mismatch, unsafe archive
   path, reparse escape, interrupted activation and cross-installation ownership.
7. Activation is atomic and preserves the previous active environment on every candidate
   failure.
8. No plan, receipt, evidence, log or error contains target path/URI, raw environment, Secret,
   device fingerprint, source or prompt.
9. A target repository snapshot and Git-status oracle remain byte-for-byte unchanged for
   discovery, planning, reuse, install success/failure, launch, detach and uninstall.
10. A process cannot begin ticket work before Job Object/native container/build limits are
    proved attached. Reverse-bypassing enforcement must turn the matching gate red.
11. Quiet armed state produces zero model calls, Router turns, probes, Git reads, filesystem
    scans, timers, update requests and network retries.
12. Capability drift closes the affected evidence and blocks execution before tool use; it does
    not silently update or continue.
13. One exact InstallGrant can be reused only for the same artifact identity until an event
    invalidates it. It cannot dispatch a ticket.
14. Each ticket has one Router receipt at a time. Environment binding uses that receipt and
    rejects a second/execution receipt, wrong ticket/task/worktree/baseline or replayed binding.
15. Same-ticket correction preserves the valid ticket receipt; a replaced task/owner/worktree
    closes the old environment binding before the new writer starts.
16. Credential flow returns only an opaque alias/capability result and rejects Secret-bearing
    input at every public boundary.
17. `PROJECT_DETACH` removes only exact project-owned Johnny mappings/writable state and
    preserves shared referenced artifacts, foreign tools and all target bytes.
18. `PLUGIN_UNINSTALL` removes every ledger-owned environment/cache/grant/evidence/receipt
    binding and preserves foreign tools and target projects. Tampered ownership halts broad
    deletion and produces bounded recovery evidence.
19. Windows 10/11 x64 and Linux-Docker support are explicit; unsupported host/architecture
    returns a finite halt without partial install.
20. The root README explains existing-tool priority, three gates, permissions, resource plans,
    detach/uninstall, team handoff and the absence of target-project coupling.
21. Exact-cap tests prove every `LIGHT`/`STANDARD` lower-of calculation, RAM halt floor, fixed
    disk/process/container/worker/lane cap and immutable no-reset behavior. Only Docker tickets
    admit nonzero containers; every `HEAVY_APPROVAL` dimension requires exact approval.
22. Local-model matrices deduct CPU/RAM/GPU/VRAM reservations before Johnny planning, halt on
    insufficient remainder without model process effect, prohibit heavy concurrency during
    training and reject download/training/dataset/weight behavior as out of scope.

## TDD and independent review matrix

- Pure plan matrix: every capability kind × required/not-required × compatible/incompatible ×
  ownership × disposition, including finite precedence and malformed input rejection.
- Authority matrix: absent/wrong/revoked/cross-artifact InstallGrant; grant used as ticket
  receipt; second execution receipt; wrong ticket/task/worktree/baseline/evidence.
- Acquisition matrix: bundled/official source, version, digest, signature, archive traversal,
  reparse, interrupted staging, activation and rollback.
- Resource matrix: Job Object/Docker/build success plus unavailable, attach-race, cap bypass,
  child escape, wrong namespace and HEAVY-without-approval rejection.
- Isolation matrix: two foreign tool installations, two target repositories, two opaque project
  IDs, two ticket writable roots, shared read-only cache and complete detach/uninstall byte/Git
  oracles.
- Drift matrix: tool replacement, digest change, manifest/lock change, adapter revision change
  and evidence replay at every declared boundary; no periodic probe path exists.
- Static/source gates: no `Any`, bypass constructors, target-local `.johnny`/`.johnny-router`,
  recurring timer/update loop, unbounded process launch, raw path/Secret field, second receipt or
  installer call inside implementation composition.
- Verification: focused tests, full regression, in-memory compile, `mypy --strict`, package/build
  smoke where applicable, target non-interference readback and independent reverse-mutation of
  every semantic source gate.

## Operations, compatibility and rollback

- Existing project-native manifests and user tools are authoritative compatibility inputs and
  remain untouched.
- No environment installation is allowed during implementation. Missing capability returns a
  typed change and requires a new approved environment plan before re-dispatch.
- Logs are local metadata-only bounded diagnostics. Production command output and Secrets are
  not durable evidence.
- Rollback deactivates the exact new Johnny-owned environment and reselects the prior verified
  owned identity. It never changes a foreign tool or target manifest.
- Detach/uninstall are ownership-ledger operations, not recursive deletion from a caller path.
- Deployment tickets bind accepted commit/artifact evidence and their own effect authority; they
  may run on a different terminal/runner and cannot depend on a development environment path.

## Candidate decomposition boundaries

After exact owner approval, the reviewer may compile this SPEC into independently observable
vertical closures, expected to include:

1. pure capability/compatibility plan and finite status contracts;
2. InstallGrant and CapabilityEvidence lifecycle/admission;
3. immutable owned-environment identity and atomic activation transaction;
4. CONTROL_PYTHON plus portable Git payload/verification composition;
5. project-native baseline and ticket-overlay evidence binding to the same Router receipt;
6. Windows Job Object and Docker/build resource-enforcement adapters;
7. project detach/plugin uninstall settlement and target/foreign isolation acceptance;
8. integrated Windows high-assurance acceptance and root README operations guide.

Revision 02 adds the exact cap, one-shot immutability and local-model reservation contracts. It
is not an authorized ticket sequence until the owner approves the exact revision and the Senior
performs a fresh decomposition. Existing admission evidence remains immutable.

These are not tickets and grant no dispatch authority. Shared contracts and transaction
boundaries must be frozen before dependent adapter tickets. Reviewer returns
`SPLIT_REQUIRED`, `UPSTREAM_DECISION_REQUIRED` or `HIGH_ASSURANCE_REQUIRED` rather than filling
an architecture gap.

## Convergence and approval

- Architecture/Grill direction was confirmed by the project owner through `2026-08-16
  (Asia/Taipei)`.
- XSS classification: `N/A`; no Browser/WebView/HTML/DOM/JavaScript renderer is introduced.
- Secret, login, acquisition, install, process launch, Docker and removal are effect/security
  boundaries and require exact ticket-level treatment after approval.
- Current Router return: `ACTION_COMPLETED -> WAIT_FOR_HUMAN / REVISION_02_SPEC_APPROVAL`.
- No ticket, dispatch, implementation, install, download, login, push, release or deployment is
  authorized by this draft.

## Revision signatures

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-15 | Architecture owner / `main` / `2701ed563f26e116db69e8e4fcb84024754c9498` | Initial independent draft after owner-completed environment Grill. |
| 2026-08-15 | Project owner | Approved the exact Environment Capability Bootstrap SPEC and assigned ticket decomposition/opening to the reviewer. |
| 2026-08-16 | Architecture owner / `main` / `2a8287831259243e230911e1082f0ec87895d3c5` | Drafted Revision 02 exact LIGHT/STANDARD caps, immutable ticket plans and local-model resource reservation under `CHG-20260816-025`; exact owner approval pending. |

## Approval record

- Decision maker: project owner.
- Exact SPEC revision: Revision 01 `APPROVED` on `2026-08-15 (Asia/Taipei)`; Revision 02
  `OWNER_REVIEW_REQUIRED`.
- Approval effect: Revision 01 authorizes only its prior reviewer decomposition; Revision 02
  grants no Senior decomposition or ticket authority before exact approval.
- It does not authorize dispatch, implementation, install, download, login, heartbeat, push,
  release or deployment.
