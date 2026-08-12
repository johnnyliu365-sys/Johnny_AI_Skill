# 04 — Windows Setup and Uninstaller Package Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01 through AC-12 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260812-014` |
| State | `DECOMPOSED / NON_DISPATCHABLE` |
| Reviewer | Codex / current `main` worktree |
| Implementation owner | `N/A` — children require separate selection and dispatch |

## Historical outcome

This parent originally combined package assembly, physical installation,
physical uninstall and release evidence. That review surface is too broad to
attribute failures safely. Its intended user outcome remains authoritative,
but no implementation may be dispatched against this file.

## Serial children

| Order | Child | Sole acceptance responsibility |
| --- | --- | --- |
| 1 | [04A — Payload manifest contract](04a-payload-manifest-contract.md) | Implement the pure typed owned-payload manifest and digest contract. |
| 2 | [04B — Inno installer build source](04b-inno-installer-build-source.md) | Implement bounded `.iss`/build source against 04A; accept no release artifact. |
| 3 | [04C — Version-one candidate freeze](04c-version-one-candidate-freeze.md) | Select one exact clean, dependency-complete source commit containing 04A/04B. |
| 4 | [04D — Staging warm backup](04d-staging-warm-backup.md) | Publish only that SHA to remote `staging` and read it back. |
| 5 | [04E — Disposable Windows environment qualification](04e-disposable-windows-environment-qualification.md) | Prove a standard-user Windows isolation boundary before product effects. |
| 6 | [04F — Windows release build](04f-windows-release-build.md) | Build manifest-bound setup/uninstaller artifacts from a clean staging export; do not install them. |
| 7 | [04G — Disposable Windows install verification](04g-disposable-windows-install-verification.md) | Verify one clean per-user install in the qualified boundary. |
| 8 | [04H — Disposable Windows uninstall verification](04h-disposable-windows-uninstall-verification.md) | Verify one-click owned removal, replay absence and foreign/target preservation. |
| 9 | [04I — Version-one artifact freeze](04i-version-one-artifact-freeze.md) | Bind immutable source/toolchain/manifest/artifact/review evidence. |

Each child is frozen and dispatched only after its predecessor is independently
approved. No child inherits implementation authority, branch, worktree or
receipt from another. `CHANGES_REQUESTED` follows the normal same-ticket,
same-branch additive-correction rule; it does not reopen this parent.

The child files are approved planning skeletons, not frozen implementation
handoffs. Before selecting exactly one child, the reviewer must update that
child with exact writable paths, named implementation owner (or explicit
reviewer-only evidence gate), environment/SOP, CodeReview §2.1 category matrix,
first-red/reversal closure and one ticket-bound handoff/allocation/receipt.
No group dispatch, inherited receipt or implementation of a later child is
valid.

## Current gate

All children remain `PLANNED / DEPENDENCY_WAIT`. 04A cannot start until the
Codex lifecycle and reviewer-role prerequisites required by the approved SPEC
are independently resolved, approved and integrated. The active 05B4B2D lane
continues unchanged. No current push, build, install, release or deployment is
authorized by this decomposition.
