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

## Ticket 72 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 72 dispatch lint: one action per line | `8c770265` | revision01 correction review `CONVERGENCE_REVIEW_REQUIRED`, disposition `APPROVED` under rule B (S72-05, S72-06 carried) | `fa4019fa` |

The integration clone `C:/Temp/claude/jas-integ-72` was made from `1d4145ea`, using the integration script `integ_one.sh`.

| Check | Result |
| --- | --- |
| Full suite in the integration clone under the host lock | 5 failed, 3644 passed, 32 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `fa4019fa`, a fast-forward from `1d4145ea` |
| CI readback | run 44381596401 on `fa4019fa`: `test (linux)` and `test (windows)` both `success` |
| USAGE | two cells were appended to `.worktrees/72-lint-out/RETURN.md` (sha256 `d3919b8941fef7e8502b0574078ca373509019464b42a4c29739c12c5f8c893d`); E1 gives exit 0 (`cells=7 defects=0`); `usage_report.py` gives exit 0 with both seats `WITHIN` |

From this integration onward, the control plane writes dispatches to the new R5: one action per line, with literal payloads in backticks and each enumerated item as its own list item (S72-05).

## Tickets 68 and 66 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 68 archive the router-era SPECs, SPEC archive rule, ADRs superseded | `c3ecdd6b` | revision01 correction review `APPROVED` | `8c4e9a77` |
| 66 retire the cross-lifetime bridge | `2d11118c` | revision01 correction review `APPROVED` | `cded7a27` |

The integration clone `C:/Temp/claude/jas-integ-6866` was made from `8b82a2b1`. Both candidates were merged in order. `REQ-20261103-043.md` merged automatically, without a conflict.

| Check | Result |
| --- | --- |
| Full suite on `cded7a27` in the integration clone under the host lock | 5 failed, 3140 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `cded7a27`, a fast-forward from `8b82a2b1` |
| CI readback | run 44390034272 on `cded7a27`: `test (linux)` and `test (windows)` both `success` |
| USAGE, ticket 68 | `.worktrees/68-archive-specs-out/RETURN.md` (sha256 `61da8e6790ca0334f6b3d7c2b6b938c766f1b6223eb483f02fbd8d755371c2a5`); E1 with L1 required gives exit 0 (`cells=8 defects=0`); both seats `WITHIN` |
| USAGE, ticket 66 | `.worktrees/66-retire-bridge-out/RETURN.md` (sha256 `91b44069dd9251f760194cfbea21c0b50a20c7d4132c30bafe64a57d13625365`); E1 gives exit 0 (`cells=6 defects=0`); the implementation seat is `OVER_PROCESSED` and the review seat is `OVER_OUTPUT,OVER_PROCESSED`, both explained in the review record |

The suite now holds 3140 passed tests, down from 3644 at ticket 72. The tests that ticket 66 retires account for the difference.

## Ticket 70 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 70 wave-2 template follow-ups, tracked-path length cap | `548665e5` | revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`, disposition `APPROVED` under rule B (S70-05 to S70-07 carried) | `277aa80b` |

The integration clone `C:/Temp/claude/jas-integ-70` was made from `68ace49c`.

| Check | Result |
| --- | --- |
| Full suite under the host lock | 5 failed, 3171 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `277aa80b`, a fast-forward from `68ace49c` |
| CI readback | run 44396032169 on `277aa80b`: `test (linux)` and `test (windows)` both `success` |
| USAGE | `.worktrees/70-templates-out/RETURN.md` (sha256 `de3fb29e913e884922770c02df7d651560acb1d0640ca6ca8fb774d74bf0484c`); E1 gives exit 0 (`cells=6 defects=0`); the implementation seat is `OVER_PROCESSED`, explained in the review record, and the review seat is `WITHIN` |


## Ticket 67 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 67 governance documents name no retired surface; exclusive-file-lock restored | `0f621d9c` | revision04 correction review `APPROVED` | `b97077e6` |

The integration clone `C:/Temp/claude/jas-integ-67` was made from `2b787737`.

| Check | Result |
| --- | --- |
| Full suite under the host lock | 5 failed, 3224 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `b97077e6`, a fast-forward from `2b787737` |
| CI readback | run 44455722140 on `b97077e6`: `test (linux)` and `test (windows)` both `success` |
| USAGE | `.worktrees/67-doc-sweep-out-c1/RETURN.md` (sha256 `630e88285879fccbe6fa37dda73f08bb7bc0337a7396c90d40f4a953b167b837`) with both seats' cells; E1 gives exit 0 (`cells=8 defects=0`); `usage_report.py` gives the implementation seat `OVER_OUTPUT,OVER_PROCESSED` and the review seat `WITHIN`, exit 1, explained in the review record. The first-pass receipt `.worktrees/67-doc-sweep-out/RETURN.md` (sha256 `3093251db52aa9274555c29ed5eb9a8b354b930cab31c7c8396c34308c3aad2d`) is kept beside it. |

After the integration, the control plane rebased its four unpushed ticket-76 commits onto `b97077e6` before pushing them. The content is unchanged; the old and new commit identifiers are mapped in the ticket-76 review record.

## Ticket 74 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 74 wave-3 rule texts at named anchors | `4943d76c` | revision04 initial review `APPROVED` (S74-01 to S74-05 recorded and carried) | `f257bffa` |

The integration clone `C:/Temp/claude/jas-integ-74` was made from `ef87d8ac`.

| Check | Result |
| --- | --- |
| Full suite under the host lock | 5 failed, 3240 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `f257bffa`, a fast-forward from `ef87d8ac` |
| CI readback | run 44474507317 on `f257bffa`: `test (linux)` and `test (windows)` both `success` |
| USAGE | `.worktrees/74-rule-texts-out/RETURN.md` (sha256 `b2c33f235f1420c0add13989e551a3b2bef0f273757abea9e509eb583ab4367c`) with both seats' cells; E1 gives exit 0 (`cells=7 defects=0`); `usage_report.py` gives both seats `WITHIN`, exit 0 |

## Ticket 75 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 75 the repository's own ticket template follows the harness; dispatch lint R7 checks the dispatch digest | `dd10fca6` | revision03 initial review `APPROVED` (S75-01 and S75-02 recorded) | `aa5d1d0d` |

The integration clone `C:/Temp/claude/jas-integ-75` was made from `f42444a4`.

| Check | Result |
| --- | --- |
| Full suite under the host lock | 5 failed, 3274 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `aa5d1d0d`, a fast-forward from `f42444a4` |
| CI readback | run 44491650931 on `aa5d1d0d`: `test (linux)` and `test (windows)` both `success` |
| USAGE | `.worktrees/75-own-tickets-out/RETURN.md` (sha256 `7b0c3410630ec48be10a1032235af7a7ec54bb2b01f6466e7964114a4b7300c5`) with both seats' cells; E1 gives exit 0 (`cells=7 defects=0`); `usage_report.py` gives both seats `WITHIN`, exit 0 |

From this integration on, the control plane lints every dispatch with `--ticket` before it goes out.

## Ticket 76 (2026-11-19)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 76 seat model and effort bound to the profile; USAGE effort line; mismatch verdicts; dispatch lint R8 | `78810fa6` | revision03 initial review `APPROVED` (S76-01 to S76-05 recorded) | `82a250a8` |

The integration clone `C:/Temp/claude/jas-integ-76` was made from `ecb66083`.

| Check | Result |
| --- | --- |
| Full suite under the host lock | 5 failed, 3335 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `82a250a8`, a fast-forward from `ecb66083` |
| CI readback | run 44505684582 on `82a250a8`: `test (linux)` and `test (windows)` both `success` |
| USAGE | `.worktrees/76-seat-binding-out/RETURN.md` (sha256 `15119b07b26f8b5dfdb3a448381f0ccd4cf520dc01a76c51310bba292df467c6`) with both seats' cells, each with an `effort:` line read from the host transcript. E1 with the integrated gate gives exit 0 (`cells=7 defects=0`). The integrated `usage_report.py`, run with the repository's own `doc/handoffs/2026/workflow-governance/usage-expectation.json`, gives `model=claude-sonnet-5-5 effort=high … WITHIN` and `model=claude-opus-5-5 effort=high … WITHIN`, exit 0. |

From this integration on, every USAGE cell the control plane appends carries the seat's effort, and every usage report runs with the repository's own expectation file.

## Ticket 73 (2026-11-20)

| Ticket | Approved candidate | Approval | Integration commit |
| --- | --- | --- | --- |
| 73 rework-record block and `rework_report.py`; the wave-3 code-review records backfilled | `b5121ee0` | revision03 correction review `APPROVED` (S73-01 and S73-03 carried to wave 4) | `3cd4bf5d` |

The integration clone `C:/Temp/claude/jas-integ-73` was made from `7b25dabd`.

| Check | Result |
| --- | --- |
| Full suite under the host lock | 5 failed, 3398 passed, 22 skipped; every failure is a base name, so zero new red |
| Pushed | `cp/wave3` at `3cd4bf5d`, a fast-forward from `7b25dabd` |
| CI readback | run 44608980985 on `3cd4bf5d`: `test (linux)` and `test (windows)` both `success` |
| USAGE | `.worktrees/73-rework-out-c1/RETURN.md` (sha256 `a98b9bb4711f9484bb6311cf618ed4bf87e4d8958fecac4973edc0137b5f624a`) with both seats' cells and `effort:` lines; E1 gives exit 0 (`cells=8 defects=0`); `usage_report.py` with the repository's expectation gives the implementation seat `OVER_PROCESSED` and the review seat `WITHIN`, explained in the review record |
| Rework report, first run on the integrated tree | over the wave-3 code-review records: `TOTAL tickets=11 rounds=21 CONTROL_PLANE_RULE=5 RETURN_UNTRUE=2 DESIGN_UNFORESEEN=2 IMPLEMENTATION_DETAIL=8`, exit 0 |
