# 01 — Owned Install Lifecycle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-03, AC-06, AC-07, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED` |
| Language | Python 3.11, Pydantic strict models and standard-library filesystem test fakes |
| Baseline | Ticket-set documentation commit (to be recorded in selected handoff) |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / `workflow-implementation` / `codex/implementation-private-router-saas-01` after explicit dispatch |
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
- `ImplementationHandoff`: created only when this ticket is selected; it must carry the approved SPEC/ticket/Context references, dedicated `handoff_ref`, TDD reference, role IDs and the selected docs baseline. It stores no raw payload, Context, path, URI, Secret or PII.
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
