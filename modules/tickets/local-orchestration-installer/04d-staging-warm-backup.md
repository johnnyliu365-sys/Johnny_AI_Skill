# 04D — Staging Warm Backup

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-11 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 04C approved with one exact complete-source candidate SHA |
| Owner / reviewer | Codex / current `main` worktree |
| Implementation owner | `N/A` — reviewer-only remote evidence gate |
| Execution class | Reviewer-owned exact remote gate; no implementation lane |
| External authority | Owner-authorized only for future exact `staging` create/fast-forward and readback |
| XSS | `XSS_NOT_APPLICABLE` |

## Sole outcome

Make remote `refs/heads/staging` equal the exact 04C candidate and prove
readback. Do not build, install, push `main`, tag/release or publish a binary.

## Safe gate

1. Fetch refs. If `staging` exists, prove it is an ancestor of candidate;
   otherwise record exact absence.
2. Reconfirm candidate identity, complete source and clean status.
3. Create or fast-forward only `origin/staging` to exact full SHA. Never force,
   delete a ref or silently resolve divergence.
4. Read remote ref back and require byte-equal SHA.
5. Return `STAGING_BACKED_UP`; auth failure, divergence, rejected update or
   mismatch is a finite halt before 04E/04F.

Evidence is metadata-only and never records credentials or tokens.
