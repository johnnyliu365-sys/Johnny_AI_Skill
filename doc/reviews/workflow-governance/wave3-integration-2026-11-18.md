# Wave 3 integration record (from 2026-11-18)

Integrations of REQ-20261103-043 wave 3 onto `cp/wave3`, by hand, in the wave-2 pattern:

1. a fresh clone with `transfer.fsckObjects`, `--no-hardlinks` and `core.autocrlf=false`;
2. a check that the fetched branch tip equals the approved candidate;
3. `merge --no-ff`, with the tip as the first parent and the candidate as the second (owner decision 2026-11-07 "1.A");
4. the full suite under the host lock;
5. a fast-forward push and the CI readback.

## Tickets 65 and 69 (2026-11-18 to 2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 65 retire the flow engine, the private router, the profile and the router telemetry | `b185dea9` | revision02 correction review `APPROVED` | `361ba136` |
| 69 token use per seat | `7cc0e08f` | revision01 correction review `CONVERGENCE_REVIEW_REQUIRED`, disposition `APPROVED` under rule B (S69-07, S69-08 carried) | `9b746c97` |

Integration clone: `C:/Temp/claude/jas-integ65`.

- **First run:** ticket 65 was merged alone on `dc4cc524`, and the full suite ran under the host lock: 5 failed, 3535 passed, 32 skipped. Every failure is a base name, so zero new red.
- **The tip moved:** before the push, the control plane pushed two docs-only commits (`369d6844`, `d4e432b5`), so the tip moved. Both merges were redone in order on `d4e432b5`: 65 as `361ba136`, then 69 as `9b746c97`.
- **Second run:** the full suite ran again on `9b746c97` under the host lock: 5 failed, 3628 passed, 32 skipped. Every failure is a base name, so zero new red.

| Check | Result |
| --- | --- |
| Pushed | `cp/wave3` at `9b746c97`, a fast-forward from `d4e432b5` |
| CI readback | run 44342660977 on `9b746c97`: `test (linux)` and `test (windows)` both `success` |

## USAGE cells (readiness criterion 5)

After integration, the control plane appended one `USAGE` cell per seat to each returned receipt. The script is `append_usage.py`, and it keeps the receipt as returned in `RETURN.as-returned.md`. The values are the host-reported usage, summed per unique message id, and they are the same values as in each review record.

- **P9 is not rerun** on a receipt that holds `USAGE` cells. That is the rule of ticket 69, S69-07.
- **E1 is rerun with the integrated `evidence_gate.py`:**

  | Receipt | sha256 after append | E1 with USAGE |
  | --- | --- | --- |
  | `.worktrees/65-retire-engine-and-private-router-out/RETURN.md` | `087fb799578ae1c46c1fa2303c5078c7cf8be6249bf1cd55006cbd722775aa9a` | exit 0, `cells=6 defects=0` |
  | `.worktrees/69-token-use-per-seat-out/RETURN.md` | `67f5f45a33bf99fe909ea905c637139a71dccb4422c2a58739666d8d69bab7ab` | exit 0, `cells=7 defects=0` |

- **`usage_report.py`** was run over both receipts with `template/doc/handoffs/governance/usage-expectation.TEMPLATE.json`, the values the owner confirmed on 2026-11-18 ("1A"). It exits 1:

  ```text
  seat:implementation-standard/65-impl implementation-standard output=88467 processed=23263970 WITHIN
  seat:ticket-review/65-rev02 ticket-review output=91014 processed=24146363 OVER_PROCESSED
  seat:implementation-standard/69-impl implementation-standard output=149575 processed=41813298 OVER_OUTPUT,OVER_PROCESSED
  seat:ticket-review/69-rev01 ticket-review output=97780 processed=17044392 WITHIN
  ```

  Each seat over its expectation is explained in its review record. Being over does not block integration (owner decision 2026-11-18 "1A").
