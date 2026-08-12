# 04I — Version-one Artifact Freeze

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 04G/04H approved against same 04E provider and 04F artifacts |
| Owner / reviewer | Codex / current `main` worktree |
| Implementation owner | `N/A` — reviewer-only evidence/handoff gate |
| Execution class | Reviewer-owned evidence gate; no source/artifact edits |
| XSS | Inherit closed 04A-04H classifications |

## Sole outcome

Create append-only version-one record and handoff. Do not rebuild, modify,
publicly release or deploy the artifact.

## Required identity

- exact 04C source and 04D staging SHA;
- clean export, Inno 6.7.3 and payload-manifest SHA-256;
- exact 04F setup and uninstaller SHA-256;
- 04E environment, 04G install, 04H uninstall/absence, target isolation and
  independent review references;
- finite support/blocked host matrix and exclusions.

All values are full and mutually consistent. Changed source/toolchain/manifest/
binary is a new version and cannot replace this record. Later work starts from
current `staging` via change control; staging moves only by guarded fast-forward.
