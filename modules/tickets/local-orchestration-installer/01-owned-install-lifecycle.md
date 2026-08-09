# 01 — Owned Install Lifecycle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-03, AC-06, AC-07, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `CHANGES_REQUESTED` — rework-8 is blocked by CR-57/58 pending a fresh control-plane allocation; the existing receipt and bounded continuation authority remain valid |
| Language | Python 3.11, Pydantic strict models and standard-library filesystem test fakes |
| Baseline | `afee39d` (`docs: plan local orchestration installer tickets`) |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` / fresh branch `codex/implementation-local-install-lifecycle-01-rework-8` |
| Environment | Local Windows user-scope test sandbox only; no actual host configuration, target-project write or installer binary |

## User-observable outcome

Given a staged test payload and a reversible fake host, the local install command yields `INSTALLED` only with a typed ownership receipt. One normal uninstall yields `REMOVED` and deletes every receipt-owned local artifact; a repeat gives `NOT_INSTALLED`. A foreign, malformed or tampered ledger instead yields `INSTALL_BLOCKED` or `UNINSTALL_BLOCKED` with no deletion outside the owned root.

## Scope and boundary

In scope: new strongly typed installation domain/application contracts, fixed install-root policy, atomic owned ledger/manifest, fake host/process/filesystem ports, safe lifecycle command and tests. Proposed source paths: `library/local_orchestration/{__init__,contracts,installation,ports,fakes}.py` and `tests/test_owned_install_lifecycle.py`.

Out of scope: production Codex/Claude registration, real subprocess/process stop, Router event runtime, Git action, Inno Setup package, target project files, elevation, networking, raw Context or Secret persistence.

Frontend composition / DI: the equivalent command/UI is `InstallControlPlane` / `UninstallControlPlane`; its composition root constructor-injects `OwnedFilesystemPort`, `InstallLedgerPort`, `HostLifecyclePort`, `RuntimeLifecyclePort`, `ClockPort` and `ProcessPort`. Test fakes are confined to a temporary root. No global singleton or direct environment read is permitted.

## Handoff and role assignment

- Control-plane owner: Codex/current `main`; implementation owner: named Codex implementation Agent in the stated separate worktree; reviewer: Codex/current `main`.
- Owner override: `N/A`.
- `ImplementationHandoff`: all prior handoffs/allocations are historical. `hnd_local_orchestration_install_01_rework_8_20260809` retains the approved SPEC/ticket/Context/TDD, owner and receipt while binding fresh allocation `aln_local_orchestration_install_01_rework_8_20260809`. The dispatch-record commit that introduces this handoff is the branch start baseline before behavior-specific fresh red tests. It stores no raw payload, Context, path, URI, Secret or PII.
- `ImplementationReturn`: `COMPLETED → ACTION_COMPLETED`; `BLOCKED → HALT`; `CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`.

## TDD and defect checks

1. **Normal lifecycle red/green:** before implementation, a valid staged payload cannot produce an atomic owned ledger/receipt; then assert `INSTALLED`, normal `REMOVED`, and idempotent `NOT_INSTALLED`, with every deleted path proven under the fixed root.
2. **Path-prefix boundary:** separately red-test exact root, one-extra-character root, trailing separator, casing variant, URL-encoded form, `..` traversal and empty value. All but the canonical resolved root must halt before filesystem effects.
3. **Null / empty boundary:** individually test `None`, undefined-equivalent omitted field, `""`, whitespace and empty list/object for installation ID, manifest, host receipt and owned relative path; document equivalent absent-state outcomes.
4. **Ownership-bypass boundary:** direct uninstall with a foreign/tampered receipt and indirect deletion through a nested manifest/cleanup helper must both fail closed; no caller may obtain a deletion-capable port outside validated ownership.
5. **Token comparison:** there is no credential/token in this ticket. TDD must source-scan that no secret/token comparator is introduced; installation IDs and digests are typed identifiers, not authentication claims, and cannot authorize an unowned path.
6. **Stable errors / exception behavior:** all invalid ownership states expose the finite external result while internally retaining one unique reason code. Inject filesystem, ledger, fake-host and fake-process failures one at a time; assert whether the application returns `*_BLOCKED` without propagating an implementation exception and that no partial receipt/deletion occurs.
7. **Regression proof:** snapshot a representative existing and empty temporary Git repository before every success/failure path and prove byte tree and `git status --porcelain` are unchanged. Retain first red-test command/name/failure in the completion evidence.

## Completion evidence

- Required: first red evidence for every behavior; unit tests; strict mypy; compile; metadata/raw-content sentinel; local smoke of fake install/uninstall; target-repository snapshots; `git diff --check`; review report; WorkProgress and docs-only handoff commit.
- Formal-environment migration: N/A — this ticket is local test infrastructure, no migration, environment variable, deployment or target-project operation.

## Selected dispatch record

| Field | Value |
| --- | --- |
| Proposal selection | Control plane selected this first unblocked vertical ticket after `afee39d`. |
| Handoff reference | `hnd_local_orchestration_install_01_rework_8_20260809` |
| Required implementation baseline | The implementation owner creates `codex/implementation-local-install-lifecycle-01-rework-8` directly from this docs-only dispatch-record `main` commit in its own worktree; review baseline `0553920` and all prior implementation histories remain immutable evidence. It must not rebase, merge, reset, cherry-pick or reuse blocked branch/source. |
| Delivery receipt | `rcpt_local_orchestration_install_01_20260808` — project owner confirmed `已交付` on `2026-08-08`. |
| Allocation continuation | `aln_local_orchestration_install_01_rework_8_20260809` keeps the same ticket, implementation-owner identity and receipt; it replaces only the rework-7 review-blocked source allocation. No second dispatch question is valid. |
| Granted scope | Only this ticket's TDD, source, tests, verification and implementation/docs-only commits in the named implementation worktree. |
| Explicitly not granted | Any target-project write, host configuration, installer binary release, Ticket 02+ implementation, merge/push/deploy, source outside ticket scope or silent requirements change. |

## Review return

- Review: `doc/reviews/local-orchestration-installer/01-owned-install-lifecycle-code-review.md` (`CHANGES_REQUESTED`).
- Blocked histories: `010110a` / `7bc5fd5`; `fd429fd`, `a222d89` / `8e39c99`; `4b840cd` / `7c73b14`; `c91041a` / `ba74caf`; `7df74e1`, `e84dff0`, `14838d9` / `f90877d`; `a3dc5a2` / `7573a74`; `e6b067c` / `f1301be`; `49a250e` / `aafe154`. None may be reset, overwritten, cherry-picked or reused.
- Corrected and retained requirements: CR-36/37 typed proof/absence validation; CR-39 finite install verification rollback; CR-41 evidence-bearing recovery phases. Rework-4 demonstrates the intended owner-release/recovery-clear sequence and cooperative manifest/checkpoint compensation, but does not close all reachable paths.
- Still required: CR-40 complete state/evidence matrix; CR-46 retry after ledger deletion plus terminal-checkpoint failure; reopened CR-38 operation-safe recovery consumption, CR-42 actual returned-effect cleanup and CR-43 active-owner validation on every existing-ledger path. A new control-plane handoff creates another fresh branch; no new user dispatch is needed.

### Rework-3 review return

- Reviewed range: `7cc8b38 → c91041a → ba74caf` on `codex/implementation-local-install-lifecycle-01-rework-3`.
- Closed: CR-41 evidence-bearing/reverified recovery phases; CR-42 exact selected-host receipt binding; CR-43 exclusive active-owner gate.
- Still required: CR-40 must assert clean/retryable state for every failure and finish the omitted boundary variants; CR-44 must retain retry authority through owner release; CR-45 must prevent manifest/recovery-write failures from stranding staged or host effects.
- Classification: implementation/TDD correction only. The approved SPEC, architecture, ticket acceptance and receipt do not change; no `REQUIREMENT_CHANGED` event is emitted.

### Rework-4 review return

- Reviewed range: `5142378 → 7df74e1 → e84dff0 → 14838d9 → f90877d` on `codex/implementation-local-install-lifecycle-01-rework-4`.
- Passing evidence: owner-release and recovery-clear focused retries, cooperative manifest/checkpoint compensation, 143-test regression, 196 subtests, mypy/compile/diff/privacy checks.
- Blocking evidence: terminal checkpoint loss after ledger deletion cannot resume; install clears an uninstall recovery; an actual mismatched returned receipt effect remains live; an injected typed second ledger bypasses active owner; CR-40 matrix/red evidence remains incomplete.
- Classification: implementation/contract/TDD correction only. No approved requirement, architecture, ticket acceptance, delivery stage or receipt changes.

### Rework-5 review return

- Reviewed range: `14be507 → a3dc5a2 → 7573a74` on `codex/implementation-local-install-lifecycle-01-rework-5`.
- Passing evidence: submitted four-test state-machine behavior, full 135-test regression, 175 subtests, mypy/compile/diff/privacy checks.
- Blocking evidence: CR-47 removed the approved port-driven lifecycle surface; CR-40 remains incomplete; CR-48 malformed IDs throw or diverge by entrypoint; CR-49 shape-valid recovery clears foreign owner/effects; CR-46 and reopened CR-38/42/43 are not proven through the approved surface.
- Classification: implementation/architecture-contract/TDD correction only. The approved SPEC/ticket remain authoritative; the implementation's reduced contract is rejected, not treated as `REQUIREMENT_CHANGED`.

### Rework-6 review return

- Reviewed range: `263e30c → e6b067c → f1301be` on `codex/implementation-local-install-lifecycle-01-rework-6`.
- Passing evidence: full 146-test regression, 195 subtests, strict mypy across 72 files, compile and diff checks; strict contracts and injected ports are restored.
- Blocking evidence: CR-50 clears `FINALIZE` recovery while live effects remain; CR-51/46 loses retry authority after ledger-delete fault; CR-52 reports `INSTALLED` without physical staging; CR-53 ignores every selected host after the first; CR-40 port/boundary/Git matrix remains incomplete and port exceptions propagate.
- Classification: implementation/TDD correction only. Approved SPEC, ticket, architecture, receipt and delivery stage remain unchanged.

### Rework-7 review return

- Reviewed range: `5e772ec → 49a250e → aafe154` on `codex/implementation-local-install-lifecycle-01-rework-7`.
- Passing evidence: 150 unittest; 150 pytest / 239 subtests; strict mypy 73 files; in-memory compile, source sentinel, diff check, physical staging, all selected hosts and submitted boundary/fault/Git matrices pass.
- Blocking evidence: CR-54 deletes a shape-valid recovery target before matching the authoritative ledger; CR-55 can leave a live host registration outside persisted recovery after a later checkpoint fault; CR-56 accepts a registration-ID-only mismatch as `INSTALLED`; CR-40 lacks those exact ordering/mismatch tests.
- Classification: implementation/contract/TDD correction only. Approved SPEC, ticket, architecture, receipt, owner and delivery stage remain unchanged.

### Rework-8 review return

- Reviewed range: `ed1a282 → 8a7b221 → 8f867cc` on `codex/implementation-local-install-lifecycle-01-rework-8`.
- Passing evidence: 151 unittest; 151 pytest / 250 subtests; strict mypy 73 files; CR-54/55/56 exact recovery, durable intent and full receipt guards pass.
- Blocking evidence: CR-57 ignores returned removal/absence proof identity and can return `REMOVED` with a live host registration; CR-58 releases owner before a fallible cleanup recovery clear, leaving retries permanently `AUTHORITY_MISMATCH`; CR-40 omits both sequences.
- Classification: implementation/contract/TDD correction only. Approved SPEC, ticket, architecture, receipt, implementation owner and delivery stage remain unchanged.
