# 01 — Owned Install Lifecycle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-03, AC-06, AC-07, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `CHANGES_REQUESTED` — `4b840cd` is blocked by CR-40 through CR-43; receipt `rcpt_local_orchestration_install_01_20260808` continues to a fresh allocation without a second question |
| Language | Python 3.11, Pydantic strict models and standard-library filesystem test fakes |
| Baseline | `afee39d` (`docs: plan local orchestration installer tickets`) |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` / fresh branch `codex/implementation-local-install-lifecycle-01-rework-2` |
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
- `ImplementationHandoff`: all prior handoffs/allocations are historical. `hnd_local_orchestration_install_01_rework_2_20260808` retains the approved SPEC/ticket/Context/TDD, owner and receipt while binding fresh allocation `aln_local_orchestration_install_01_rework_2_20260808`. The dispatch-record commit that introduces this handoff is the branch start baseline before behavior-specific fresh red tests. It stores no raw payload, Context, path, URI, Secret or PII.
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
| Handoff reference | `hnd_local_orchestration_install_01_rework_2_20260808` |
| Required implementation baseline | The implementation owner creates `codex/implementation-local-install-lifecycle-01-rework-2` directly from this docs-only dispatch-record `main` commit in its own worktree; review baseline `f2b4a8e` and both prior implementation histories remain immutable evidence. It must not rebase, merge, reset, cherry-pick or reuse blocked branch/source. |
| Delivery receipt | `rcpt_local_orchestration_install_01_20260808` — project owner confirmed `已交付` on `2026-08-08`. |
| Allocation continuation | `aln_local_orchestration_install_01_rework_2_20260808` keeps the same ticket, implementation-owner identity and receipt; it replaces only the second review-blocked source allocation. No second dispatch question is valid. |
| Granted scope | Only this ticket's TDD, source, tests, verification and implementation/docs-only commits in the named implementation worktree. |
| Explicitly not granted | Any target-project write, host configuration, installer binary release, Ticket 02+ implementation, merge/push/deploy, source outside ticket scope or silent requirements change. |

## Review return

- Review: `doc/reviews/local-orchestration-installer/01-owned-install-lifecycle-code-review.md` (`CHANGES_REQUESTED`).
- Blocked histories: `010110a` / `7bc5fd5`; `fd429fd`, `a222d89` / `8e39c99`; `4b840cd` / `7c73b14`. None may be reset, overwritten, cherry-picked or reused.
- Corrected so far: CR-36/37 typed proof/absence validation; CR-38 normal recovery retry; CR-39 finite install verification rollback.
- Still required: CR-40 complete matrix/red evidence; CR-41 evidence-bearing recovery phases; CR-42 selected-host receipt binding; CR-43 exclusive fixed-root ownership. A new control-plane handoff creates another fresh branch; no new user dispatch is needed.
