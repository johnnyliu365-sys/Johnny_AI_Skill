# 04F — Windows Release Build

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-01 through AC-05, AC-09 through AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T04F-01` / evidence closure below |
| Dependency | 04D staged SHA and 04E Windows environment approved |
| Implementation language | `N/A` — reviewer-controlled build/evidence gate executing frozen Inno Setup 6.7.3 plus the approved Python 3.11 runner; no source edits |
| Owner / reviewer | Codex / current `main` worktree |
| Implementation owner | `N/A` — reviewer-controlled build/evidence gate; no source edits |
| Execution class | Reviewer-controlled clean-export build; no source edits |
| XSS | Inherit 04B classification; source drift invalidates candidate |

## Sole outcome

From a clean export of exact 04D remote SHA, build manifest-bound `Setup.exe`
and matching uninstaller payload. Do not install either artifact.

## Evidence closure

- Require SHA equality among 04C candidate, 04D readback and clean export; no
  overlay or historical-source copy.
- Reverify signed Inno Setup 6.7.3, manifest and every source/input digest.
- Compiler/source/manifest/output/Secret/digest failure is finite build block.
- Record setup/uninstaller SHA-256, manifest, command and export identity. No
  target project, host registration, install, push, release or deployment.
- Rebuild unchanged inputs reproduces defined deterministic fields; permitted
  non-determinism must already be frozen by 04B.

Only exact artifacts accepted here enter 04G/04H.
