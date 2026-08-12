# 04C — Version-one Candidate Freeze

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-01 through AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 04A/04B approved and integrated; all package prerequisites complete |
| Owner / reviewer | Codex / current `main` worktree |
| Implementation owner | `N/A` — reviewer-only evidence gate |
| Execution class | Reviewer-owned evidence gate; no source/test implementation lane |
| XSS | `XSS_NOT_APPLICABLE`; reclassify if delivery surface changes |

## Sole outcome

Select one exact clean `main` commit containing reviewed 04A/04B source as the
complete version-one candidate. Do not push, build, install or mutate a host.

## Required evidence

- Exact full SHA and clean tracked/ignored/cache readback.
- Every upstream ticket, review and guarded integration.
- Full tests, strict typing, compilation/source sentinels and target-project
  non-interference current at that SHA.
- Complete manifest/installer source graph; Inno Setup 6.7.3 preflight; no
  Secret or generated release binary in Git.
- `CANDIDATE_FROZEN` or finite blocker. Missing/abbreviated SHA, dirty state,
  incomplete dependency or stale evidence fails closed.

Completion authorizes only 04D selection, not release build.
