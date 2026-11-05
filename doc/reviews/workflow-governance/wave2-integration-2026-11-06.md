# Wave-2 integration record (2026-11-06): tickets 60, 57, 59 and 62

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

## Ticket 59 (second integration of the day)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 59 CI on Linux and Windows | `e067b81b` | revision02 initial review `APPROVED` | `ea51e1c1` |

A second fresh integration clone (`C:/Temp/claude/jas-integ3`, `transfer.fsckObjects=true`, `fetch.fsckObjects=true`, `core.autocrlf=false`) was made from `aeabe7a5`; the branch tip was checked equal to the candidate, and the merge had no conflict.

| Check | Result |
| --- | --- |
| Full suite in the integration clone under the host lock | 8 failed, 3393 passed, 36 skipped; every failure is a base name; zero new red. At acquisition one single-file pytest of another seat was running outside the lock (`tests/test_gate_index_pins.py`) |
| Lock release | the lock directory is renamed before it is removed, so a run that acquires the lock in the same second keeps its own. The release used for tickets 60 and 57 removed the directory in place, and a reviewer that acquired the lock in that second lost it (recorded in the ticket 59 revision02 review) |
| Pushed | `cp/wave2-gates` at `ea51e1c1` (fast-forward from `aeabe7a5`) |
| CI readback | run 42101907082 on `ea51e1c1`: `test (linux)` and `test (windows)` both `success`. This is the first CI run of the integrated branch, with tickets 51 to 57, 59 and 60 in it |

## Ticket 62 (third integration of the day)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 62 known failures CI registers | `bb9c4502` | revision01 correction review `APPROVED` (receipt rebuilt; candidate unchanged) | `68c318a5` |

A fresh integration clone (`C:/Temp/claude/jas-integ4`, `transfer.fsckObjects=true`, `fetch.fsckObjects=true`, `core.autocrlf=false`) was made from `78aeeedc`; the branch tip was checked equal to the candidate, and the merge had no conflict.

| Check | Result |
| --- | --- |
| Full suite in the integration clone under the host lock | 5 failed, 3397 passed, 36 skipped; every failure is a base name; zero new red (three base failures are now fixed). No other pytest was running at acquisition |
| Pushed | `cp/wave2-gates` at `68c318a5` (fast-forward from `78aeeedc`) |
| CI readback | run 42121310874 on `68c318a5`: `test (linux)` and `test (windows)` both `success`, with the registered lists at Linux 228 and Windows 44 rows |
