# 02 — Metadata Runtime and Guarded Git

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-04, AC-05, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED` |
| Language | Python 3.11 / Pydantic strict; public types/patterns selected from `workflow-router-poc@d94d8d5` |
| Baseline | Ticket 01 reviewed/integrated documentation and source baseline |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / a fresh synchronized separate worktree after explicit dispatch |
| Environment | Local metadata store and temporary Git repositories only; no company project, host configuration, push or deployment |

## User-observable outcome

A validated local metadata event resumes one safe Router continuation or returns finite `HALTED` / `NEEDS_USER_ACTION`. It never persists raw Context. A runtime request may touch a temporary registered Git repository only when opaque project identity, explicit registration, expected clean base, per-project lock and fast-forward condition all match; every other path leaves it unchanged.

## Scope and boundary

In scope: `InstallationId`-bound metadata event/checkpoint store, replay claim, status projection, project registry and injected guarded Git adapter. Proposed paths: `library/local_orchestration/{runtime,event_store,project_registry,guarded_git}.py`, public exports and `tests/test_metadata_runtime_and_guarded_git.py`.

Reuse only: `library.workflow_router` public `ProjectId`, `RouterEvent`, completion/return and Context descriptor contracts, plus guarded integration's error/state pattern. Do not change current Router POC behavior or treat its fake integration port as real Git.

Out of scope: host lifecycle, installer UI/package, automatic Agent turn, raw source access, target company project registration by installer, push, deploy, reset, merge commit, network or database.

Frontend composition / DI: `ResumeOrchestration` and `ReadRuntimeStatus` are equivalent command boundaries. A runtime composition root injects `EventStorePort`, `RouterPort`, `ProjectRegistryPort`, `GuardedGitPort`, `ClockPort` and notification port; temporary-repo/clock/router/Git fakes are used in tests.

## Handoff and role assignment

- Roles remain separated: control-plane/reviewer Codex/current `main`; implementation owner Codex implementation Agent in its dedicated worktree; owner override `N/A`.
- Dispatch handoff must cite the exact Ticket-01 integrated baseline and the public `workflow-router-poc@d94d8d5` contracts. It may carry opaque project/correlation/evidence IDs but no actual project path or ContextPacket.
- A missing registry, dirty/stale base, lock contention, replay or host-needed status produces a typed halt/blocked return. Any need to widen Git permissions is `CHANGE_DETECTED → Grill`.

## TDD and defect checks

1. **Normal runtime red/green:** an unseen valid metadata event initially has no claim/checkpoint; green claims it once, resumes one allowed Router continuation and returns a finite status. A valid temporary registered repo under clean exact base exercises one allowed fast-forward-only adapter result.
2. **Path-prefix boundary:** individually test registered exact root, one-extra-character sibling, trailing separator, casing, URL-encoded locator, traversal and empty locator; noncanonical values cannot be registered, resolved or passed to Git.
3. **Null / empty boundary:** test `None`, omitted/undefined-equivalent, `""`, whitespace and empty container for event, project identity, revision/base, correlation and registry request. Record which absent forms map to the same finite halt.
4. **Authority bypass:** verify direct adapter calls and indirect runtime/retry/background path both require the same installation-bound registry, project ID, lock and exact base. No event can grant Git authority merely by carrying a valid-looking project ID.
5. **Token comparison:** no credential/token is in this ticket. Source-scan that no token equality comparison is introduced; opaque IDs are validated identifiers, and no raw authorization secret is stored or compared.
6. **Stable errors / exception behavior:** separately inject event store, router, registry, lock and Git subprocess-port failures. Assert external finite error shape, unique internal code, whether errors are contained (expected) rather than thrown, and zero Git side effect on failure.
7. **Regression proof:** test replay, cross-installation/cross-project event, raw source/Context sentinel, dirty tree, stale base, non-fast-forward, duplicate queue claim and mutation of each required guard. Preserve first red evidence.

## Completion evidence

- Required: red evidence; unit/integration tests against temporary repositories; strict mypy; compile; privacy sentinel; runtime smoke; target-repository non-interference snapshot; `git diff --check`; review and docs-only handoff.
- Formal-environment migration: N/A — no production repository, push, deployment or secret is allowed.
