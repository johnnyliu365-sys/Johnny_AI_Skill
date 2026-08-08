# 04 — Windows Setup and Uninstaller Package

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01 through AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED` |
| Language | Inno Setup script plus Python 3.11 packaged runner; pinned compiler version required |
| Baseline | Tickets 01–03 reviewed/integrated baseline and one or more verified host lifecycle adapters |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / a fresh synchronized separate worktree after explicit dispatch |
| Environment | Windows user-scope sandbox; no administrator elevation, target project or production deployment |

## User-observable outcome

The owner runs one `Setup.exe`, selects at least one genuinely supported host, and receives `INSTALLED` only after the packaged local root and host receipt are verified. Running the matching uninstaller once stops the owned runner, removes all receipt-owned registrations/payload, and deletes `%LOCALAPPDATA%\\JohnnyAIWorkflow`; rerunning reports `NOT_INSTALLED`. Both representative target repositories remain unchanged.

## Scope and boundary

In scope: pinned Inno Setup build configuration, payload manifest generation, user-scope setup/uninstaller wiring, process/host lifecycle invocation, install/update/remove result presentation and clean-user-profile smoke automation. Proposed paths: `installer/JohnnyAIWorkflow.iss`, `installer/README.md`, package build script, release manifest and `tests/test_windows_package_contract.py`.

Out of scope: admin/system installation, arbitrary install path, code signing/public distribution, auto-update, support SLA, host model execution, target project manipulation, direct cache deletion, secrets, networking, push or deployment.

Frontend composition / DI: setup/uninstaller screens are composition-only and receive typed install/remove projections from the packaged runner. Production bindings are the pinned Inno package plus verified host adapters; tests fake package/process/host files. Success, progress, no-host, blocked and retry text must be accessible without colour.

## Handoff and role assignment

- Roles stay separated: Codex/current `main` plans/reviews; the named implementation Agent works only in its own synchronized worktree; owner override `N/A`.
- Dispatch requires proof that the exact Inno Setup compiler version is available under normal owner authority and at least one Ticket-03 host adapter is independently reversible. Otherwise this ticket remains `PLANNED` or returns `BLOCKED`; it must not substitute a script that leaves files behind.
- Handoff references the exact integrated tickets, package manifest, target-repository snapshot fixtures and clean-user-profile smoke plan. Returns follow the global typed completion contract.

## TDD and defect checks

1. **Normal package red/green:** before installer wiring, a clean-user sandbox lacks owned payload/receipt; green builds `Setup.exe`, installs one verified fake/real host, observes `INSTALLED`, then one uninstaller invocation removes every owned artifact and returns `NOT_INSTALLED` on replay.
2. **Path-prefix boundary:** package/root verification must test exact root, one-extra-character directory, trailing separator, casing, URL encoding, traversal and empty path. The uninstaller cannot schedule deletion outside the fixed root.
3. **Null / empty boundary:** test `None`, omitted/undefined-equivalent, empty, whitespace and empty container package manifest, install ID, host selection and receipt; setup blocks before unpack/process action.
4. **Authority bypass:** direct uninstaller launch, interrupted update and indirect package-repair path all require the same verified owned ledger/host proof. A foreign/manual plugin or arbitrary target directory cannot be claimed by package name.
5. **Token comparison:** packaging contains no credential/token. Source/artifact scan must assert no secret token is embedded or equality-compared; any host login remains outside package scope.
6. **Stable errors / exception behavior:** inject compiler unavailable, archive/digest mismatch, host failure, runner-stop timeout, removal failure and filesystem error. Assert consistent external blocked result, unique internal reason and no false success or orphaned partial registration.
7. **Regression proof:** clean user profile smoke plus existing/empty target repository snapshots cover install, failed install, status, failed uninstall and successful uninstall. Mutation of a manifest entry, host receipt or deletion guard must fail its corresponding test; preserve all first red evidence.

## Completion evidence

- Required: red evidence; package build/version proof; unit/contract tests; strict type check; compile; exact one-click install/uninstall smoke in clean user profile; all receipt-owned host cleanup proof; target-repository snapshots; `git diff --check`; independent review; WorkProgress docs handoff.
- Formal-environment migration: N/A — package installation is local user-scope only. Recovery is the matching uninstaller; failure requires `UNINSTALL_BLOCKED` retry, not manual project cleanup.
