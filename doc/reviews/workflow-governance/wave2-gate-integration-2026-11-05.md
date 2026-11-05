# Wave-2 gate integration record (2026-11-05)

## What landed

The six approved gate tickets were integrated onto `cp/wave2-gates` by hand, because the integration script (ticket 50) did not exist yet. The integration followed the R4-4 trust boundary the owner confirmed on 2026-11-05: every merge ran in a fresh integration clone filled from the repository with `transfer.fsckObjects=true` and `fetch.fsckObjects=true` (`git fsck` clean), and the result was fetched back with `fetch.fsckObjects=true` and fast-forwarded.

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 51 evidence gate | `e7594f65` | CodeReview §5 rule B (convergence disposition) | `6fbec950` |
| 52 requirement snapshot | `91beb02d` | rule B | `64251c9a` |
| 53 contract gate | `2a710426` | rule B | `c876bd46` |
| 54 coverage-map guard | `763284bf` | rule B | `8fc352d1` |
| 55 preflight gate | `c7a04099` | revision03 correction review `APPROVED` | `c3aa5a5f` |
| 56 tool-repair guard | `9dfe5eb4` | revision05 initial review `APPROVED` | `cbb8306d` |

Before each merge the branch tip was checked equal to the approved candidate. Each branch changed only its script, its test file and the scripts README; the only conflicts were in the README introduction. The introduction was rewritten to name the scripts present after each merge; every gate keeps its own section verbatim.

## Evidence

| Check | Result |
| --- | --- |
| The six gate test files and the payload boundary test in the integration clone | 1229 passed; one failure, `CommittedPinTests::test_the_pinned_sha_exists`, a base name |
| Full suite in the integration clone under the host lock | 8 failed, 3260 passed, 35 skipped; every failure is a base name in `jas48_F1_base.txt`; zero new red |
| Pushed | `cp/wave2-gates` at `9a26eeb1` (the integration commits plus tickets 50 and 57) |

## Commit attribution (owner decision 2026-11-05: keep as is)

The implementation seats of wave 2 ran on Claude Sonnet 5.5. Until the dispatch template was corrected on 2026-11-04, the dispatch files told them to sign their commits with a `Co-Authored-By: Claude Opus 5.5` trailer, so the following commits name the wrong model. The owner decided not to rewrite them, because rewriting would change every reviewed candidate sha. The model that did the work is Claude Sonnet 5.5 for each:

`7928d447`, `4bcc2873` (ticket 51); `dbd74358`, `21ac4fda`, `3c485efc`, `ac95c321`, `bea0cf0c` (ticket 52); `fd456159`, `5ea02c13`, `09af7a1f` (ticket 53); `8c91e85d`, `285e6df8` (ticket 54); `eb9014cc` (ticket 55); `02d40fd2` (ticket 56).

Every later seat commit names the model that did the work, and every dispatch since 2026-11-04 asks for that.
