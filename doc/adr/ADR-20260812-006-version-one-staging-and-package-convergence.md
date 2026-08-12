# ADR-20260812-006: Version-one staging and package convergence

- Date: `2026-08-12` (Asia/Taipei)
- Status: `ACCEPTED`
- Decision maker: Project owner
- Requirement change: `CHG-20260812-014`
- Related specification: `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-11 and AC-12

## Problem

The former Windows package ticket mixed source-candidate selection, remote
backup, installer compilation, physical install, physical uninstall and final
release evidence. A failure could therefore be misclassified or trigger broad
rework. The repository also lacked a remote `staging` ref and an explicit
immutable identity for the first packaged version.

## Decision

1. Existing POC prerequisites continue on reviewed `main`. No active
   implementation branch is interrupted or rebased for this decision.
2. Local package Ticket 04 becomes a non-dispatchable parent. Serial children
   04A-04I separately own payload manifest, installer build source, complete
   candidate freeze, staging warm backup, disposable-Windows environment
   qualification, release build, disposable install verification, disposable
   uninstall/absence verification and version-one artifact freeze.
3. 04A independently integrates the pure payload-manifest contract; 04B does
   the same for Inno installer/build source. Both may create only disposable
   test output. 04C may then select one exact clean complete-source `main`
   commit. 04D creates or fast-forwards remote `staging` to exactly that commit
   and reads it back.
   Dirty state, absent authority, unexpected remote history, non-fast-forward
   movement or SHA mismatch is `HALT / STAGING_DIVERGED`; force is forbidden.
4. The release build uses a clean export of that exact staging candidate.
   Environment and system-integration children consume immutable upstream
   source/artifact evidence and do not refreeze a different source
   opportunistically.
5. The final first-version record binds source/staging SHA, Inno Setup 6.7.3,
   payload manifest digest, setup/uninstaller digests and the exact install,
   removal, absence, target-isolation and review evidence. A different input or
   output is a new candidate/version and cannot overwrite this identity.
6. After version one is frozen, later functionality or architecture begins
   from the current `staging` baseline and re-enters change control, SPEC and
   ticket planning. The version-one record remains append-only.

## Consequences

- Remote `staging` is a warm source backup and future development baseline; it
  is not a test fixture, a binary release, or proof that installation works.
- Failures are attributable to one acceptance responsibility instead of one
  monolithic package ticket.
- `origin/main` is not pushed by this decision, and no public release,
  deployment, code-signing, Secret handling or target-project mutation is
  authorized.
- The already running 05B4B2D implementation continues unchanged. Package
  children remain dependency-waiting until their exact prerequisites pass.
