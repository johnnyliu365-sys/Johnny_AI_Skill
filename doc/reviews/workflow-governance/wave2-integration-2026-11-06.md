# Wave-2 integration record (2026-11-06): tickets 60 and 57

## What landed

The integration script (ticket 50) is not approved yet, so the two approved tickets were integrated onto `cp/wave2-gates` by hand under the R4-4 trust boundary, as on 2026-11-05. The integration clone `C:/Temp/claude/jas-integ2` was made fresh from the repository with `transfer.fsckObjects=true` and `fetch.fsckObjects=true`, with `core.autocrlf=false`. The candidate branches were fetched into it with `fetch.fsckObjects=true`, and each tip was checked equal to the approved candidate before its merge.

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 60 gate hardening (carried findings) | `1c0fb917` | revision01 initial review `APPROVED` | `093f221e` |
| 57 state-file templates | `f423748b` | revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`, convergence disposition `APPROVED` (CodeReview §5 rule B) | `7da279a7` |

Neither merge had a conflict. In the clone the three governance templates are checked out LF with `attr/text eol=lf`, as the ticket 57 `.gitattributes` line requires.

## Evidence

| Check | Result |
| --- | --- |
| Full suite in the integration clone under the host lock | 8 failed, 3354 passed, 36 skipped; every failure is a base name in `jas48_F1_base.txt`; zero new red |
| Other processes at lock acquisition | no pytest or mutation process; only file watchers from earlier days |
| Pushed | `cp/wave2-gates` at `7da279a7` (fast-forward from `36db19b8`) |

Every seat commit in both candidates names the model that did the work.
