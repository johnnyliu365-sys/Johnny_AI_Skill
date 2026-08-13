# ADR-20260813-007: Project-owned disposable test runtime

- Date: `2026-08-13` (Asia/Taipei)
- Status: `ACCEPTED`
- Decision maker: Project owner
- Requirement change: `CHG-20260813-015`
- Related specification: `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-13

## Problem

Integrated 05S1 places every disposable environment at a globally shared
`%TEMP%/johnny-stage-env-*` location. A failed or interrupted test can leave a
directory that a later run in another worktree discovers. The later owner then
cannot tell from locality alone whether it owns that residue, and broad cleanup
would cross the ticket's authority boundary. This caused E3D to delete a
pre-existing test residue outside its pure-projection scope.

## Decision

1. Every 05S1-based repository test environment is rooted under the exact
   current plugin checkout at `tests/.johnny-runtime/`. This means each Git
   worktree receives a separate physical runtime namespace automatically.
2. The root applies only to this plugin repository and its detached test
   exports. It is never created in, derived from, or copied to a target/company
   project and it does not change the installed product root.
3. Each lease remains one marker-bound direct child named
   `johnny-stage-env-<generated-id>`. Its child `TEMP`, `TMP`, profile,
   app-data and `CODEX_HOME` directories remain inside that exact lease.
4. The runtime parent is repository-ignored by the exact
   `/tests/.johnny-runtime/` rule, but final verification must include ignored
   readback. Successful teardown removes the exact lease and removes the
   runtime parent only when it is empty.
5. An unclaimed pre-existing lease, unexpected sibling, marker mismatch,
   reparse point or non-empty runtime parent returns a finite residue/ownership
   block. Provision and ordinary teardown never scan or delete an OS-global
   staging namespace and never clean a previous run automatically.
6. The migration removes the `from_system_temp` construction path and updates
   every integrated direct caller atomically. No compatibility fallback may
   keep creating `%TEMP%/johnny-stage-env-*` roots.
7. E3D and E4 return to `REQUIREMENT_CHANGED` until the migration is
   independently approved and integrated. Their current uncommitted work is
   preserved pending explicit owner disposition; it is not accepted evidence.

## Consequences

- Residue becomes attributable to one checkout/worktree and is visible through
  the required ignored-status check.
- A crash can dirty only the plugin test namespace, never the OS-global TEMP or
  a target project. Exact cleanup still requires marker-bound authority.
- The foundation migration touches the environment allocator and its existing
  direct test callers in one bounded ticket so no half-migrated fallback can be
  integrated.
- Existing 05S1-05S4 commits/reviews remain immutable historical evidence. The
  new ticket supersedes only their root-location assumption for future tests.
- No package, installer, live Codex, target-project, network, push, release or
  deployment authority follows from this decision.
