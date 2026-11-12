# Wave 2 completion (2026-11-12)

Wave 2 of REQ-20261103-043 is complete on `cp/wave2-gates`. Every ticket of the wave is integrated, and both wave-2 acceptance criteria have committed evidence.

## Tickets

| Ticket | What it delivers | Integrated at |
| --- | --- | --- |
| 50 | merge-queue integration script (`integrate.py`): submit, land as a merge commit (owner decision 2026-11-07), read back | `b95b4acd` |
| 51 to 56 | evidence gate, requirement snapshot, contract gate, coverage-map guard, preflight gate, tool-repair guard | `6fbec950` to `cbb8306d` |
| 57 | state-file templates | `7da279a7` |
| 58 | governance consistency test and the wave-1 carried findings | `88321851` |
| 59 | CI on Linux and Windows with registered failures | `ea51e1c1` |
| 60 | gate hardening carried under rule B | `093f221e` |
| 61 | wave-2 acceptance 1, end to end | `4f6e1b5a` |
| 62 | known failures that CI registered, fixed or re-caused | `68c318a5` |
| 63 | path containment: short names, redirects decided from the file system (P0) | `5c704541` |
| 64 | integration-script hook tests on POSIX | `70a741f7` |

Integration records: `wave2-gate-integration-2026-11-05.md` and `wave2-integration-2026-11-06.md`.

## Acceptance

| Criterion (REQ-20261103-043, readiness) | Evidence | Status |
| --- | --- | --- |
| 1. On a fixture project, one ticket goes from a requirement snapshot through dispatch, implementation, independent review and merge-queue integration to a landed commit. The session is ended mid-ticket, and a new session finishes it from the files alone | Part A: `tests/test_wave2_end_to_end.py`. Part B: `wave2-acceptance-1/rerun/RUN.md`, the clean rerun, finished by a fresh session that read only the project and the plugin copy, and landed by `integrate.py` | met |
| 2. CI is green on Linux and Windows, apart from registered failures listed by name | `ci/registered-failures.json`, Linux 228 rows and Windows 5 rows, each with a cause. The owner decided on 2026-11-07 ("3.算") that registered known failures with a confirmed cause and an open follow-up meet the criterion. CI run 43200411926 on `15fe6136` is green on both jobs | met |

## Owner decisions taken during wave 2

| Date | Decision |
| --- | --- |
| 2026-11-05 | CodeReview §5 rule B. The queue lives on a queue branch. R4-2 exit column. R4-4 integration clone with `transfer.fsckObjects` (A). Keep the commits whose trailers name the wrong model as they are |
| 2026-11-07 | Land by merge commit (1.A). Marketplace re-pin waits for the wave-3 publication (2.B). Registered known failures meet criterion 2 (3.算). Every reparse point refuses, cloud-file tags included (4.A) |
| 2026-11-12 | Part B evidence keeps seat transcripts off the public repository, with hashes in the record (A). "ADR split" removed from wave 3. Merge `cp/wave2-gates` into `main` when wave 2 completes ("合") |

## Follow-up work found in wave 2

None of these blocks wave 2. Each is recorded in the review record or ticket named.

- **Templates (61 part B, both runs):**
  - the ticket template lacks rows for Profile, XSS, closure revision, strict checker, allocation and correlation;
  - it cites a `CodeReview.md §2.1` that no longer exists;
  - its state list has no `INTEGRATED` and does not say when `DONE` is set;
  - the state row holds only one receipt path;
  - the receipt template has no typed-return slot;
  - nothing guides a first dispatch's `preflight:` and `registry_commit`.
- **Rules:**
  - a receipt cannot name its own commit; both runs used "cells at the code commit, candidate = the tip that adds only receipts";
  - CodeReview §5 should say that a new closure revision's first review is its initial review (S61-07);
  - resume conventions for the dispatch location, the submitter on resume, worktree ownership and the review record path (S61-03).
- **Scripts:**
  - a committed script that decides the next step from the state files (S61-02);
  - the contract gate also catches literal expected values in `assertEqual`;
  - `integrate.py` runs git children under `LC_ALL=C` (S50-15).
- **Tests and hardening carried under rule B:**
  - S57-05/06/09/10/12
  - S58-06/12/14/15
  - S59-09/10/12/13/14
  - S60-01 to S60-05
  - S61-01/04
  - S62-04 to S62-07
  - S63-26 to S63-28
  - S64-01/02
- **Repository hygiene:** a test that caps the length of tracked paths. The ticket 61 record broke Windows CI from `f6c33831` until `15fe6136`.
- **Wave 3 (REQ-20261103-043):**
  - router library retirement, with router-era ADRs archived there;
  - publication 0.5, with the marketplace re-pin and the publication commit reachable from a ref;
  - readiness criteria 3 to 5: a Codex host run, an install by someone other than the owner, token use per seat;
  - a job object for the process tree (S55-11, S55-26, S60-02).
