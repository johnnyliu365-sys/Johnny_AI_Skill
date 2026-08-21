# Johnny AI Skill Codex Plugin Distribution Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` |
| Status | `APPROVED_REVISION_02 / IMPLEMENTATION_PENDING` |
| Package version | `johnny-ai-skill 0.4.0` |
| Author / worktree / baseline | Codex / `main` / `5bf3ad243a23027fe896b7984f6ca23551dbee4c` |
| Context | `doc/context/plugin-distribution/main.md` |
| PRD / change | `PRD-20260802-004` / `CHG-20260802-004` |
| Platform | Windows per-user |
| Implementation language | Python with `mypy --strict`; PowerShell only as the Windows bootstrap boundary |
| XSS classification | `XSS_NOT_APPLICABLE` |

## Problem, outcome and non-goals

The previous skill-only Git distribution cannot prove that the executable Router, reusable
library, event supervision and reversible runtime actually survive packaging. Revision 02
produces one deterministic, detachable Codex plugin bundle that can be installed, verified and
removed without adding a runtime, cache, governance checkout or hidden control file to a target
project.

The formal candidate is `johnny-ai-skill-0.4.0.zip` plus an externally recorded SHA-256. It is
eligible for Router binding only after clean package verification and the SourceProjectA acceptance
sequence in this specification.

This revision does not include `Setup.exe`, a public release, signing, auto-update, system-wide
installation, MCP server, Codex App, plugin hook, heartbeat, automation, cron, polling, Windows
service, paid Provider, Secret, push, tag, deployment or target-project dependency.

## Deterministic payload boundary

The archive builder starts from one exact clean Git commit and accepts only this logical payload:

- `.codex-plugin/plugin.json`;
- `skills/` and every directly referenced skill reference;
- `library/`, including Router, local orchestration and delivered reusable modules;
- `AGENTS.md`, `Workflow.md`, `CodeReview.md` and the existing `README.md`;
- the `install.ps1` bootstrap, `johnny-router` launcher/runtime composition root;
- a runtime dependency lock, package payload manifest and per-file SHA-256 values.

The archive excludes Git metadata, worktrees, `doc/`, `modules/spec/`, `modules/tickets/`,
`modules/element/`, `tests/`, Claude plugin metadata, build/staging/review evidence, caches,
coverage, telemetry data, receipts, queues, `.env`, Secrets and target content.

Archive order, path separators, timestamps, permissions and compression settings are
canonicalized. Two builds from the same source commit and toolchain must be byte-identical. The
plugin manifest has at most three default prompts and declares no MCP server, App or hook.

### Exact contract and creation locations

Ticket planning must use the following locations; no ticket may choose a parallel package,
launcher, lock or manifest contract:

| Concern | Public contract / composition source | Created or delivered artifact |
| --- | --- | --- |
| Runtime dependency lock | `library/local_orchestration/runtime_dependency_lock.py` | repository-root `requirements-runtime.lock` |
| Payload manifest and digest | `library/local_orchestration/windows_package_manifest.py` | archive-root `payload-manifest.json` |
| Deterministic payload selection and ZIP creation | `library/local_orchestration/plugin_bundle_builder.py` | Johnny-owned build output `johnny-ai-skill-0.4.0.zip`; never a target-project path |
| Router CLI request/result contract | `library/local_orchestration/johnny_router_contracts.py` | finite typed JSON on stdout; no durable target artifact |
| Router production dependency injection | `library/local_orchestration/johnny_router_composition.py` | one short-lived composition per CLI call and, only for admitted active tickets, one project runner |
| Router argument/exit-code boundary | `library/local_orchestration/johnny_router_cli.py` | no import-time process, filesystem, Git or host effect |
| User launch and bootstrap | repository-root `johnny-router.ps1` and `install.ps1` | receipt-owned launcher and venv under the per-user Johnny root |

`RuntimeDependencyLock`, `RuntimeDependency`, `LockedArtifact`, `PayloadManifest`,
`PayloadManifestEntry`, `JohnnyRouterRequest` and the closed `JohnnyRouterResult` union are the
public strong types. The lock parser, manifest builder and CLI reject unknown fields, dynamic
maps, unvalidated paths, unhashed dependencies and ambiguous commands before effect. Package
creation reads the committed lock and allowlist, emits the manifest, and then emits the ZIP;
`install.ps1` only consumes and verifies those artifacts. The old planned
`04A — Payload Manifest Contract` location is therefore reused rather than duplicated.

The minimum public fields are closed as follows; tickets may refine internal private types but
may not rename, omit or widen these boundary fields:

```text
LockedArtifact = { filename, sha256 }
RuntimeDependency = {
  normalized_name, exact_version, environment_marker?, source_kind,
  artifacts: tuple<LockedArtifact>[1..n]
}
RuntimeDependencyLock = {
  schema_version = 1, python_constraint, dependencies: tuple<RuntimeDependency>[1..n],
  lock_digest
}
PayloadManifestEntry = { archive_relative_path, sha256, byte_length }
PayloadManifest = {
  schema_version = 1, plugin_id, plugin_version, source_commit,
  dependency_lock_digest, entries: tuple<PayloadManifestEntry>[1..n]
}
JohnnyRouterOperation = PREFLIGHT | REGISTER_PROJECT | DETACH_PROJECT
                      | REGISTER_SUBSCRIPTION | CANCEL_SUBSCRIPTION
                      | ROUTE_EVENT | STATUS | UNINSTALL
JohnnyRouterRequest = one discriminated operation-specific request
JohnnyRouterResult = SUCCEEDED | BLOCKED | CAPABILITY_UNAVAILABLE | NOT_FOUND
                   | CONFLICT | HALTED
```

The lock digest is SHA-256 over canonical lock records excluding `lock_digest`. The payload
manifest digest is SHA-256 over the canonical UTF-8 JSON bytes; the manifest does not recursively
list itself. Entries are unique, ordinal-sorted canonical archive-relative paths and cover every
other ZIP payload file. `JohnnyRouterRequest` reuses existing exact domain requests from
`library/workflow_router` and `library/local_orchestration`; the CLI wrapper may add only
`request_id` and the operation discriminator. Results contain stable status/error codes and
opaque references, never raw exception text or target content.

## Runtime composition and lifetime

Router domain decisions execute as short-lived Python CLI calls. The first admitted
implementation dispatch for a project starts one hidden, Johnny-owned temporary runner for that
project. Further active tickets share the process but receive distinct receipt-bound
subscriptions. Each subscription binds:

- project, ticket, receipt and correlation;
- implementation task/thread/host;
- exact worktree, branch, baseline and Git ref;
- exact reserved handoff path and event-source identity.

The Windows adapter uses `ReadDirectoryChangesW` to receive exact ref hints. It performs no
recurring Git, filesystem or thread read. A hint causes bounded ref, ancestry, changed-path and
committed-blob readback. Ordinary source commits do not wake a model. A terminal handoff candidate
is accepted only after its complete binding validates.

The runner may outlive the terminal that started it. It must not register startup, a scheduled
task, service, automation, watchdog or heartbeat. It exits after the last subscription closes,
project detach or plugin uninstall. After an OS restart it remains stopped; the next explicit
plugin invocation may reconstruct only exact active metadata and reconcile the Git ref. It never
replays a consumed handoff.

## Host wake capability gate

Git proves a committed candidate, not a Codex callback. Production automatic wake requires an
injected `HostWakePort` that independently proves exact Senior task/thread/host availability,
receipt-bound event registration, claim-before-effect, one effect invocation and exact readback.
An uncertain effect is settled once and never retried.

When that capability is unavailable, the result is
`HOST_WAKE_CAPABILITY_UNAVAILABLE`. The runner may persist the candidate and issue a local
user-facing manual-forward notice, but may not claim automatic supervision, start a read loop or
bind Router. Heartbeat, recurring automation, cron, Git polling, thread polling and
`WAIT_FOR_HUMAN` masquerading as an event subscription are prohibited fallbacks.

The current Codex host does not expose a verified receipt-bound completion subscription.
Implementation may complete the port, fakes and fail-closed production boundary; the live
Router-ready claim remains blocked until the host capability passes.

## Role, queue and model behavior

### Versioned ProjectWorkflowProfile

The ticket-admission profile reference is
`plugin-distribution-poc-r02`; its `profile_version` is `2` and its versioned source is this exact
SPEC revision and commit. `library/workflow_router/profile.py::build_plugin_distribution_profile`
is the only creation location. It copies the transition rules, versioned policy references,
halt-return contract and POC delivery stage from `build_router_poc_profile()`, then binds this
profile identity and the following exact role metadata. It may not silently change Router
transitions or infer roles from Git authorship.

| ModelRole | Model ref | Capability ref | Capability evidence ref | Initial state |
| --- | --- | --- | --- | --- |
| `ARCHITECTURE_OWNER` | `model-gpt-5-6-sol-xhigh-architecture-r02` | `cap-plugin-distribution-architecture-r02` | `evidence-owner-approved-plugin-architecture-r02` | `ACTIVE` |
| `SUPERVISOR_REVIEWER` | `model-gpt-5-6-terra-high-senior-r02` | `cap-plugin-distribution-ticket-review-r02` | `evidence-owner-approved-terra-senior-r02` | `ACTIVE` |
| `IMPLEMENTATION_OWNER` | `model-gpt-5-6-luna-xhigh-implementer-r02` | `cap-plugin-distribution-implementation-r02` | `evidence-owner-approved-luna-implementer-r02` | `SLEEPING` |
| `RESEARCH_HELPER` | `model-gpt-5-6-luna-readonly-helper-r02` | `cap-plugin-distribution-readonly-research-r02` | `evidence-reviewer-owned-helper-policy-r02` | `SLEEPING` |

The profile uses `ctx-plugin-distribution-r02` as `shared_context_ref` and
`cap-plugin-distribution-architecture-owner-r02` as
`architecture_owner_capability_ref`. The four evidence references are capability-selection
evidence resolved by the exact rows above and versioned by the enclosing SPEC commit; they are
not implementation authority. Exact task/thread/host/worktree/branch/baseline and
receipt evidence remains a separate live admission requirement. The current unavailable host
wake observation is versioned as `evidence-host-wake-unavailable-r02` and can only select the
fail-closed/manual-forward result; it cannot grant automatic wake or Router binding.

The specialized Debugger policy remains GPT-5.6 Sol xhigh, but Debugger is not a fifth
`ModelRole`: it is a Senior-requested, ticket-bound correction assignment using a fresh receipt.
The implementation ticket for this Profile owns
`tests/test_plugin_distribution_profile.py` and must prove exact construction, distinct opaque
references, the unchanged transition graph and rejection of stale/mismatched profile refs.

Plugin-created identity is not authority. A pre-existing Codex role becomes legal only after the
user designates it and exact role/model/task/thread/host/project/worktree/branch/baseline/receipt
readback succeeds. An unregistered branch is ignored. An ordinary source commit on a watched ref
is not completion. An invalid or foreign handoff halts and isolates that ticket. Git author name
or email is never identity proof.

Each project has at most one Architecture Owner and one Senior; Implementer count follows the
approved resource plan. Completion candidates enter the existing FIFO review inbox. A busy Senior
receives no second wake. Claim closes one batch snapshot. Tickets retain individual states;
dependent tickets form a review cluster and must be inspected together before dependency-
consistent decisions. A new committed revision in a cluster invalidates affected prior
inspections. Wake instructions contain only exact commit, artifact reference, section anchor and
digest.

The current default Profile maps the highest-capability model to Architecture Owner, Terra to
Senior and Luna xhigh to Implementer. Debugger is GPT-5.6 Sol xhigh. Luna's non-resettable limit,
ticket-repair-first rule and one-run Terra-high escalation remain defined by receipt-bound role
supervision. Model identity grants no authority.

## Python and dependency isolation

Bootstrap prefers a user-installed Python 3.11-or-newer interpreter only after an exact
compatibility probe succeeds. An unqualified future version is unsupported rather than assumed
compatible. The installer creates a Johnny-owned venv and never edits global site-packages,
`PATH`, a target venv, target manifest or target lockfile.

Core runtime dependencies are hash-locked `pydantic` and, on Windows, `pywin32`. LangGraph,
Temporal, OpenAI Agents SDK and MCP integrations are optional and lazy; their absence cannot make
the core Router import fail. The regular ZIP carries no third-party wheels. `install.ps1` displays
the exact package/version/source plan and obtains user confirmation before using a local pip cache
or network download. A missing hash or incompatible wheel blocks and rolls back. `mypy`, type
stubs and test tools are development-only.

## Install, status and uninstall interfaces

`install.ps1` validates the archive/payload identity, detects Codex/Git/Python/native-notification
capability, creates the owned venv/root, registers the local plugin through supported Codex
plugin/marketplace commands and reads back the exact plugin ID, version and installed path. It
does not edit private Codex configuration or any target project. A failed attempt removes only
receipt-proven content created by that attempt.

The logical CLI exposes strict finite operations for preflight, project registration/detach,
subscription registration/cancel, event routing, status and uninstall. Machine-facing results are
typed JSON with stable status/error codes; raw exception text, prompts, source and target content
do not enter durable state.

`johnny-router uninstall` is the only route allowed to claim complete removal. It blocks new
dispatch, stops owned runners, closes subscriptions, removes receipts, ledger, queue, telemetry,
venv and owned launcher, invokes the supported Codex plugin removal and verifies absence.
Direct UI/native plugin removal cannot claim Johnny runtime cleanup. A later install must detect
orphan state and fail closed rather than silently adopt or delete it.

## Data and document ownership

Johnny-owned durable storage contains only opaque identifiers, finite states, digests, numeric
usage and original-currency pricing metadata. It contains no raw Context, prompt, source,
target-project URI/path, Secret or PII. A live runner may hold the exact repository path only in
memory; restart recovery requires the project to be explicitly reopened and rebound.

Plugin governance, skills, runtime and receipts remain in the plugin/user boundary. Target
Context, PRD/CHG, SPEC, ticket, review evidence, source and tests remain target-owned and
target-versioned. Install, preflight, failure, detach and uninstall never write or delete a target
file. Authorized workflow stages may write target-owned artifacts only through their existing
contracts; they never copy plugin governance into the project.

Telemetry retains separate input, cached-input and output token counts, role, model, reasoning
level, receipt, price snapshot and original currency. It runs only on explicit user request,
derives report inputs from receipt-indexed committed evidence, and can export JSON, CSV, terminal
tables and bar-chart data. It does not run or wake a model in the background.

## Acceptance criteria

| AC | Required evidence |
| --- | --- |
| AC-01 | Two builds from the same clean source/toolchain produce identical ZIP bytes and SHA-256. |
| AC-02 | The payload allowlist is complete and every excluded tree/sentinel is absent. |
| AC-03 | A machine without the development checkout loads both skills, Router core and module catalog from the extracted package. |
| AC-04 | Core import and routing pass when every optional dependency is absent. |
| AC-05 | Success, missing Git/Python, incompatible Python, hash mismatch, dependency failure and interruption return finite install results with exact rollback. |
| AC-06 | Representative existing and empty target repositories remain byte- and Git-status-identical across install, failure, runtime and uninstall. |
| AC-07 | One project has one runner; multiple receipt subscriptions remain isolated and one failure cannot close another. |
| AC-08 | Terminal closure does not stop active supervision; OS restart does not auto-start it; explicit restart safely reconciles exact refs. |
| AC-09 | Source commits stay silent; only an exact committed handoff becomes a completion candidate. |
| AC-10 | Foreign role/receipt/task/host/worktree/branch/baseline/correlation, malformed handoff and replay all fail before accepted completion. |
| AC-11 | Missing production host callback returns `HOST_WAKE_CAPABILITY_UNAVAILABLE` and cannot become an automatic-supervision or Router-ready claim. |
| AC-12 | FIFO, closed batch snapshot, individual status, dependency-cluster review and revision invalidation pass the complete scripted matrix. |
| AC-13 | Canonical uninstall removes every receipt-owned effect, preserves foreign/user/target state and makes repeat uninstall idempotent. |
| AC-14 | Telemetry is user-triggered, model/role/token-class separated and exportable without raw Context. |
| AC-15 | The SourceProjectA sequence passes completely before `ROUTER_BINDING_ELIGIBLE`; manual host forwarding cannot satisfy the live automatic-wake cell. |

## SourceProjectA package verification

The original `D:\SourceProjectA\SourceProjectA` is read-only. Record its HEAD and tracked
status, create a Johnny-owned disposable copy, install only from the candidate ZIP and run:

1. a no-model script matrix for new/changed requirement, Grill, Context, SPEC, ticket, document
   management, stage changes, assignment, model selection, role boundaries, FIFO/cluster review
   and invalid commits;
2. one real isolated Python ticket with no business route, network, database, Provider, Secret or
   production effect, using Terra Senior and Luna xhigh Implementer;
3. exact implementation commit, committed handoff, queue admission and independent review;
4. canonical uninstall, owned-residue absence and deletion of the disposable copy.

The original repository must end at the same HEAD and status. Every verification-only file,
cache and runtime is deleted. When the host wake capability is absent, manual forwarding may
exercise the remaining path but the live wake cell and AC-15 stay blocked.

## Release, ticketing and rollback

This approval authorizes only specification revision and later ticket planning. It does not
authorize package publication, push, tag, GitHub release, deployment or Router binding. After all
acceptance gates, the owner may separately approve publication of the exact tested ZIP digest;
rebuilding creates a different candidate.

Senior decomposes the approved revision into independently observable vertical tickets for:
payload/import isolation, CLI/bootstrap, runner/subscription lifecycle, host wake capability,
deterministic build, clean install/uninstall, scripted Vita verification and real-role smoke.
Every implementation ticket uses first-red TDD, `mypy --strict` and temporary-artifact cleanup.
It may add only its ticket and approved source/test/config changes; it does not create another
SPEC, ADR or review document and never modifies the original SourceProjectA repository.

Rollback before publication deletes only the local candidate and receipt-owned test/runtime
state. Rollback after installation uses `johnny-router uninstall`. Target projects are never a
rollback target.

## Revision signature

| Date | Decision |
| --- | --- |
| 2026-08-02 | Project owner approved the skill-only private Git plugin POC. |
| 2026-08-17 | Project owner approved Revision 02: complete versioned Codex bundle, isolated dependency/runtime, native Git event runner, fail-closed host wake gate, reversible install/uninstall and SourceProjectA package verification. |
