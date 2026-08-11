# 06B — Codex Role-profile Owned Lifecycle

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC revision 02 / AC-03, AC-06 through AC-10 |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Dependency | 06A independently approved as `SUPPORTED`; autonomous Ticket 04 approved/integrated |
| Responsibility | Existing implementation task/worktree after a unique ticket receipt; control `main` reviews |

## One outcome

Install, read back, receipt-bind, remove and prove absence for exactly one
reviewer and one implementation custom-agent profile inside the disposable
Codex lifecycle. Preserve foreign/manual agents and global config exactly.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T06B-01`

- `L1`: exact staged profile bytes/digests and finite roles create one atomic
  owned receipt only after host readback.
- `L2`: any collision, same-name foreign profile, tampered digest, missing
  removal proof or partial write compensates current-attempt owned effects and
  returns `INSTALL_BLOCKED` without broad clear/delete.
- `L3`: one receipt removal deletes reviewer and implementer profiles in order,
  freshly proves both absent and preserves foreign/global bytes. Replay returns
  the finite already-absent result with no effect.
- `L4`: existing/empty target repositories, live user Codex and all values
  outside the disposable lease remain byte/porcelain-identical.

TDD must enumerate locator, null/container, direct/indirect authority, stable
error, every write/read/remove/absence fault and reverse receipt/digest checks.
No real user installation, model turn, push, release or deployment.
