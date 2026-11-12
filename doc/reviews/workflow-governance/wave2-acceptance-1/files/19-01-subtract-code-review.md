# calc Code Review — ticket 01 subtract

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | `calc` |
| 共同基準 | declared `8e6ae013374fb683e565be49b15488dc500a565f`; actual branch base `02ba789acc01d680433896efd8b05a41a8318b6d` (docs-only delta, see below) |
| 受審 commit | candidate `545adb36f1196a6462718361fc7b101d07517c11` (branch `seat/calc-subtract` on origin); implementation `bd3e756d2bdc6e18a70357cacc66e6bfefe7d216` |
| 審閱者 | `seat:ticket-review/61b-review` (authored nothing in this ticket) |
| 結論 | `CHANGES_REQUESTED` |

Initial review of the ticket's first closure. Governance read: plugin `AGENTS.md`, `Workflow.md`
(router, tickets, implementation, review-handoff), `CodeReview.md`, references `review-checks.md`,
`implementation-tdd.md`, `specification-ticketing.md`, `implementation-authority.md`, the
workflow-governance SPEC Revision 04 (R4-1 to R4-8), the plugin `template/` ticket, receipt and
review templates, and the gate-script README sections for `dispatch_lint.py`, `evidence_gate.py`
and `contract_gate.py`. All runs below were made in a `--no-hardlinks` review clone, never in the
seat's worktree.

## 規格／需求變更追溯

- Requirement `REQ-CALC-002`, snapshot `doc/requirements/snapshots/calc/2026-11-07-v1.json`
  version 1, status `active`. The row's `source_sha256`
  `0d0669c0763427f070c122fc6f82f00cf2ee5bb302028cd4e65442f1b5e26ea7` equals sha256 of
  `doc/requirements/sources/calc-rows.json` at the candidate.
- No SPEC document (`modules/spec/`), PRD or CHG exists in the fixture; the ticket records this.
  No requirement change was detected.

## Context、tickets、elements 與實作衝突核對

- Ticket `modules/tickets/calc/01-subtract.md`: blob at `02ba789` (state `PLANNED`) and at the
  candidate (state `DONE`, close-out fields filled). Diff between the two touches only the state
  word, the red-output line and the close-out section.
- Dispatch `doc/handoffs/2026/governance/dispatch/01-subtract.md`, unchanged since `02ba789`.
  sha256 of its committed bytes (LF, `text eol=lf`) is
  `443f120eb01133eed2366780f8413c3a38c64bae739306f7e0807392d03cf911`, equal to the
  `dispatch=sha256:` value in the state row at `02ba789` and at the candidate.
  `dispatch_lint.py` on it: `LINT PASS`, exit 0. Its six fields are the minimal envelope of
  `specification-ticketing.md` § Dispatch normalization.
- Worktree: `git worktree list` shows `.worktrees/calc-subtract` under the fixture root on
  `seat/calc-subtract` at the candidate, clean. Origin's `seat/calc-subtract` is the candidate.
- Implementation `bd3e756`: `src/calc.py` adds `subtract(a: int, b: int) -> int` returning
  `a - b`; `tests/test_calc.py` adds `SubtractTests` with the three cells of the ticket's TDD
  design (normal, negative result, zero and negatives). `add` and every other file untouched,
  within the ticket's 責任邊界／禁止修改.
- `git diff --name-status bd3e756 545adb3`: five added files under
  `doc/handoffs/2026/governance/receipts/` (the receipt and four captures under `evidence-01/`)
  and `M modules/tickets/calc/01-subtract.md`; zero bytes of diff under `src/` and `tests/`. The
  blobs of `src/calc.py` (`a1205596…cfc67`) and `tests/test_calc.py` (`d0bdbff6…ee0da`) are
  identical at both commits. **The cells run at `bd3e756` therefore stand for the candidate's
  code.**
- Declared baseline `8e6ae01` versus actual base `02ba789`: `02ba789` adds only `.gitignore`,
  the dispatch, the snapshot and the ticket; the ticket cannot name the commit that contains it.
  Not a finding.
- Applicability, with reasons: XSS not applicable (pure integer function, no browser, WebView,
  DOM or JavaScript, no renderer); security-boundary not applicable (no secret, formal log,
  provider, webhook or external effect); Agent control and task/worktree checked above; delivery
  profile fan-out not applicable (one implementer, no helper, no staging); performance: constant
  work per call. These are the reviewer's verified readings, not ticket fields (see F2).

## 發現、風險與處置

| # | Class | Blocks approval | Closure item | Finding | Route |
| --- | --- | --- | --- | --- | --- |
| F1 | `TICKET_DEFECT` | yes | REQ-CALC-002 binding; Workflow §0 gate chain, R4-2, R4-6, R4-8 | `contract_gate.py` is red at the candidate: `NO_SPEC_FOR_REQUIREMENT REQ-CALC-002` (and `REQ-CALC-001`, already unbound at baseline), exit 1. Under the gate a spec is any `test_*.py` under the specs directory, so `tests/test_calc.py` is a spec; it carries no `# requirement:`, `# source:`, `# mutation:` declaration. The ticket's closure never names the contract gate, the declaration, the cited source, the mutation name, the one-contract-per-file layout (R4-6) or where expected values live (ledger, R4-8). The seat cannot design these without inventing contract. REQ-CALC-001 also needs a binding outside this ticket before the gate can go green at all. | Control plane revises the ticket (new closure revision) and decides REQ-CALC-001's binding; then seat correction. |
| F2 | `TICKET_DEFECT` | yes | `review-checks.md` § Ticket dispatch schema review | The ticket has no XSS classification, no Profile／resource, no named Closure revision, and 審閱者 is the placeholder `待指定`. That section makes missing fields `TICKET_SCHEMA_INVALID / NON_DISPATCHABLE` even when the implementation looks correct. Allocation and correlation are read as carried by `owner_task` and the dispatch digest under R4-1. | Same ticket revision as F1. |
| F3 | `EVIDENCE_DEFECT` | yes | AGENTS.md P0 source type; `implementation-tdd.md` § Type and layering gate, § Ticket completion | No strict type evidence. The receipt says strict type check was not run because the fixture declares no such tool. P0 requires the language's available strict checker and the reference names `mypy --strict` for Python; mypy 2.3.0 is installed in the interpreter the work used. Reviewer ran `mypy --strict --no-incremental src tests`: `Success: no issues found in 4 source files`, exit 0. So the P0 property holds in the code; the evidence is missing. | Seat adds a strict-type run cell in the correction. |
| F4 | `EVIDENCE_DEFECT` | yes | AGENTS.md start order step 5; R4-1; receipt template; `implementation-tdd.md` § Ticket completion | The receipt (a) holds no run cell and no statement for the contract gate, although the gate runs and exits 1; the reason given outside the receipt, that the fixture has no spec, is wrong in the gate's own terms; (b) carries no typed return (`ImplementationReturn: COMPLETED` / `ACTION_COMPLETED`); (c) has no statement for the choices made where the rules are silent (state `DONE` set before review; contract gate not run), which the receipt template requires; (d) does not name the smoke command (the reviewer's import-seam call reproduced `2 -2 0 2 5` exactly). | Seat adds the missing cells and statement lines in the correction. |
| F5 | `EVIDENCE_DEFECT` | yes | REQ-CALC-002 "for any two integers" | Reviewer counter-mutation 2 (64-bit wraparound) turned zero cells red: the clause is not pinned beyond small values. The candidate itself is correct (`subtract(2**64, -2**64) == 2**65` is `True`). | Seat adds a large-magnitude cell; control plane may add it to the TDD design in the F1 revision. |
| F6 | `OUT_OF_SCOPE_HARDENING` | no | none in this closure | Root of F2 and F4(b) is upstream: the plugin's shipped ticket template has no rows for XSS classification, Profile／resource or Closure revision that `review-checks.md` requires, and cites a `CodeReview.md §2.1` that no longer exists; the receipt template has no slot for the typed return. | Follow-up ticket in the plugin repository; not touched here. |

Seat choices where the plugin's rules are silent:

- **State `DONE` set before review.** Not a finding by itself. The state vocabulary keeps `DONE`
  separate from `REVIEW_APPROVED`, CodeReview §5 rule B sets `REVIEW_APPROVED` after review, and
  `integrate.py` reads the review record, not the state word. The choice was not recorded as a
  statement (F4c), and the completion it claims is not yet fully evidenced (F3, F4a).
- **`contract_gate.py` not run because the fixture has no spec.** A finding: the premise is
  false for the gate (`tests/test_calc.py` is a spec under its definition), the gate is red, and
  the omission is unrecorded. Ticket side F1 (`TICKET_DEFECT`), receipt side F4a
  (`EVIDENCE_DEFECT`).

Observations, not findings: the receipt's cells name `bd3e756` while the candidate is `545adb3`,
which is unavoidable (a receipt cannot name its own commit) and covered by the docs-only diff
above; `evidence_gate.py` against `545adb3` reports `CANDIDATE_MISMATCH` on all four cells by
construction. The state row keeps `dispatch=` after `DONE`; the digest still matches. The dispatch
file is `.md` rather than `<ticket>-<n>.yaml`; R4-1 makes the path a parameter.

## 驗證證據

Interpreter: the fixture's Python 3.11 venv with `PYTHONUTF8=1`. Gate scripts: the plugin's
`skills/johnny-project-takeover/scripts/`. Every pytest run was direct, `-p no:cacheprovider`,
with no output-reducing wrapper; the full output was read.

| Command (review clone) | Result |
| --- | --- |
| `evidence_gate.py doc/handoffs/2026/governance/receipts/01-subtract.md --repo . --candidate bd3e756d2bdc6e18a70357cacc66e6bfefe7d216 --tool src/calc.py --tool tests/test_calc.py --require-cell tests --require-cell smoke --require-cell mutation --require-cell restored` | `cells=4 defects=0`, exit 0 |
| same with `--candidate 545adb36f1196a6462718361fc7b101d07517c11`, no `--require-cell` | four `CANDIDATE_MISMATCH`, exit 1 (expected, see observations) |
| `dispatch_lint.py doc/handoffs/2026/governance/dispatch/01-subtract.md` | `LINT PASS`, exit 0 |
| `contract_gate.py --repo . --snapshot doc/requirements/snapshots/calc/2026-11-07-v1.json --specs tests` at `545adb3` | `NO_SPEC_FOR_REQUIREMENT` for REQ-CALC-001 and REQ-CALC-002, `requirements=2 specs=1 defects=2`, exit 1 |
| `python -m pytest -q -p no:cacheprovider` at `bd3e756` and at `545adb3` | `4 passed`, exit 0 at both |
| `python -c "from src.calc import subtract, add; print(subtract(5,3), subtract(3,5), subtract(0,0), subtract(-4,-6), add(2,3), subtract(2**64, -2**64)==2**65)"` | `2 -2 0 2 5 True`, exit 0 |
| `python -m mypy --strict --no-incremental src tests` | `Success: no issues found in 4 source files`, exit 0 (cache removed afterwards) |
| counter-mutation 1: `return a - b` → `return b - a` in `src/calc.py` | 3 failed, 1 passed, exit 1: `test_subtract` `-2 != 2`, `test_subtract_negative_result` `2 != -2`, `test_subtract_zero_and_negatives` `-2 != 2`; `test_add` green |
| restore by `git checkout -- src/calc.py` | sha256 back to `a1205596…cfc67`, `git status` clean, `4 passed`, exit 0 |
| counter-mutation 2: `return a - b` → `return ((a - b + 2**63) % 2**64) - 2**63` | `4 passed`, exit 0 — zero red (F5); `subtract(2**64, -2**64)` returned `0` under the mutation |
| restore by `git checkout -- src/calc.py` | sha256 back to `a1205596…cfc67`, `git status` clean, `4 passed`, exit 0 |

Counter-mutation 1 enters through operand order, a different door from the seat's operator swap
(`a + b`), and lands on the production function the tests import (`src.calc.subtract`), not on a
copy. Counter-mutation 2 probes the "any two integers" clause.

## 未解項與 handoff 結論

`CHANGES_REQUESTED`. The implementation is correct against REQ-CALC-002 and within scope; the
blocking items are the ticket's missing contract-gate binding and schema fields (F1, F2) and the
receipt's missing evidence (F3, F4, F5). Order: the control plane first issues a revised closure
for the ticket (F1, F2, and the F5 cell if it chooses); the seat then corrects additively on
`seat/calc-subtract` (no reset, amend or force) and reruns the receipt's cells at the correction
commit. F6 goes to a plugin follow-up ticket and does not block. No integration, push of the seat
branch or queue entry is authorised by this record.

```review-verdict
candidate: 545adb36f1196a6462718361fc7b101d07517c11
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/61b-review
reviewed_at: 2026-11-07
```

## Correction review

| 欄位 | 內容 |
| --- | --- |
| Closure | ticket 01 revision02 (`285843e47f32d72ef0effda385cff06e3d5e5424` on main), correction dispatch `doc/handoffs/2026/governance/dispatch/01-subtract-c1.md` |
| 受審 commit | candidate `45fc3873bb002d2dfd3fecd52eee31ad92de5f20` (tip of `seat/calc-subtract` on origin); correction `b00b521c23f6f8b6ec863cbae0509f93ddca4e52`; merge `007d1e7` |
| 審閱者 | `seat:ticket-review/61b-review` |
| 結論 | `CONVERGENCE_REVIEW_REQUIRED` — every unclosed finding is of a class that CodeReview §5 rule B lets through |

All runs in the same `--no-hardlinks` review clone, refreshed from origin; the seat's worktree,
the queue and the plugin repository were not touched.

### Admission

- Correction dispatch: sha256 of the committed bytes is
  `306cc4f3e2db8dadb6ffde776b08a7211a1956365101041b17501bc356b311ac`, equal to the state row of
  revision02; `dispatch_lint.py` `LINT PASS`, exit 0. Its `registry_commit` is the initial review
  commit `5a51205`.
- Merge `007d1e7`: the ticket blob at the merge is `b3639aa3…`, identical to the revision02 blob at
  `285843e`, so main's ticket was taken whole. The merge differs from `285843e` only by the seat's
  revision01 files (old receipt and `evidence-01/`, `src/calc.py`, `tests/test_calc.py`).
- Correction `b00b521` changes only `tests/test_calc.py` (contract declaration, ledger-driven
  asserts, a beyond-64-bit test) and adds `tests/ledger/calc.json`. `src/calc.py` is unchanged
  since `bd3e756` (blob `a1205596…cfc67`). Everything is inside revision02's 責任邊界 and boundary
  block; `add` is unchanged.
- `git diff --name-status b00b521 45fc387`: nine added files, the receipt `01-subtract-c1.md` and
  eight captures under `receipts/evidence-01-c1/`; zero bytes under `src/` and `tests/`, and
  identical blobs for all three tool files. **The cells at `b00b521` stand for the candidate.**

### Initial findings

| # | Status | Evidence |
| --- | --- | --- |
| F1 | closed | `contract_gate.py --repo . --snapshot doc/requirements/snapshots/calc/2026-11-07-v1.json --specs tests` at `b00b521` and at `45fc387`: `requirements=2 specs=1 defects=0`, exit 0. Both requirements are declared, the source digest matches, three mutations are named, the asserts read the ledger. |
| F2 | closed | Revision02 adds Profile `POC`, XSS not applicable, Closure revision02, and names the reviewer. |
| F3 | closed | `mypy --strict --python-version 3.11 --no-incremental src tests` at both commits: `Success: no issues found in 4 source files`, exit 0; receipt cell `mypy`. |
| F4 | closed except (d) | The receipt has the `contract` cell (a), `ImplementationReturn: COMPLETED -> ACTION_COMPLETED` (b), and statements for DONE before review, the merge resolution and the kept revision01 receipt (c). The smoke command (d) is still described in prose, not given literally: see G1. |
| F5 | closed | The reviewer's 64-bit wraparound mutation is now red: `test_subtract_beyond_64_bits` fails with `assert 0 == 36893488147419103232`, the other four stay green, exit 1; restored to the same sha256, 5 passed. |
| F6 | carried | Plugin template follow-up; out of scope here, unchanged. |

### New findings

| # | Class | Rule B | Finding | Disposition |
| --- | --- | --- | --- | --- |
| G1 | `EVIDENCE_DEFECT` | does not block | The receipt's smoke statement paraphrases the command instead of giving the command line revision02 asked for. The output `2 -2 0 2 5 True` is exactly what the reviewer's import-seam command produces, so the behavior is confirmed. | Follow-up: record the literal command the next time this receipt form is used. |
| G2 | `EVIDENCE_DEFECT` | does not block, but it is the kind that would let a regression through, so it must be fixed in the next change to this spec | Every test iterates a slice of the ledger and asserts per row; none asserts its slice is non-empty. Reviewer counter-mutation 3 removed the beyond-64-bit ledger row **and** applied the 64-bit wraparound in `src/calc.py`: 5 passed, exit 0, and `contract_gate.py` still exited 0. `test_subtract_beyond_64_bits` passed having asserted nothing. A ledger edit can silently empty a cell. The candidate itself is correct. | Next change to `tests/test_calc.py` or the ledger: pin each cell's row count, or assert it is non-empty. |
| G3 | `OUT_OF_SCOPE_HARDENING` | does not block | Revision02's Agent Context binding row still names receipt `01-subtract.md`, while the state row names `01-subtract-c1.md`. The state row decides (R4-1), so nothing is ambiguous. | Control plane tidies the row at close-out. |
| G4 | `OUT_OF_SCOPE_HARDENING` | does not block | The correction dispatch has no `correction_ref` field (`specification-ticketing.md` § Dispatch normalization) and names a new receipt rather than the original. The review commit is present as `registry_commit`, and ticket, receipt and owner all resolve. | Control plane; consider aligning the reference and the R4-era dispatch form. |

No `IMPLEMENTATION_DEFECT`. No `TICKET_DEFECT` is left that changes an exit classification,
breaks the safety or scope boundary, or violates P0.

Observations, not findings: the ticket keeps `IN_PROGRESS` and its 紅燈輸出／完成回寫
placeholders, as revision02 directs (DONE and write-back belong to the control plane after
approval). The test module's `__main__` entry runs under `unittest`, where bare `assert` would
be stripped by `python -O`. The configured spec command is pytest, which rewrites the asserts
(counter-mutation 4).

### Verification

Interpreter: the fixture's Python 3.11 venv, `PYTHONUTF8=1`. pytest ran directly with
`-p no:cacheprovider` and no output-reducing wrapper, and the full output was read.

| Command (review clone) | Result |
| --- | --- |
| `evidence_gate.py doc/handoffs/2026/governance/receipts/01-subtract-c1.md --repo . --candidate b00b521c23f6f8b6ec863cbae0509f93ddca4e52 --tool src/calc.py --tool tests/test_calc.py --tool tests/ledger/calc.json` with `--require-cell` for tests, smoke, mypy, contract, mutation-add, mutation-subtract, mutation-wrap, restored | `cells=8 defects=0`, exit 0 |
| `contract_gate.py` (as F1) at `b00b521` and `45fc387` | `defects=0`, exit 0 at both |
| `python -m mypy --strict --python-version 3.11 --no-incremental src tests` at both | success, exit 0 (cache removed) |
| `python -m pytest -q -p no:cacheprovider` at both | `5 passed`, exit 0 |
| reviewer mutation 2 (64-bit wraparound) at `45fc387` | 1 failed (`test_subtract_beyond_64_bits`), 4 passed, exit 1; restored, sha256 `a1205596…cfc67`, 5 passed |
| counter-mutation 3 (new door, ledger vacuity): drop the beyond-64-bit row from `tests/ledger/calc.json` and apply the wraparound | `5 passed`, exit 0, contract gate exit 0: **zero red**, G2; both files restored to sha256 `a1205596…cfc67` / `c3720198…fb8d`, 5 passed |
| counter-mutation 4 (new door, environment): `return a - b` → `return a + b` under `PYTHONOPTIMIZE=1` | 4 failed, 1 passed, exit 1: pytest's assert rewriting keeps the asserts under `-O`; restored, 5 passed |

### Conclusion

`CONVERGENCE_REVIEW_REQUIRED`. F1, F2, F3 and F5 are closed, and F4 is closed except the literal
smoke command. Every unclosed finding is an `EVIDENCE_DEFECT` (G1, G2) or an
`OUT_OF_SCOPE_HARDENING` (F6, G3, G4), none of which blocks approval under CodeReview §5
rule B. The control plane may therefore record a convergence disposition for this candidate,
carrying G2 to the next change of this spec. This review does not authorise a third correction,
integration or any push of the seat branch.

```review-verdict
candidate: 45fc3873bb002d2dfd3fecd52eee31ad92de5f20
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/61b-review
reviewed_at: 2026-11-07
```

## Convergence disposition (control plane, CodeReview §5 rule B)

The correction review closed F1 to F5 except the smoke-command line (G1). No open finding changes an exit code or touches safety, confinement or P0: G1 and G2 are evidence gaps on a behaviourally correct candidate, and G3, G4 and F6 are out-of-scope hardening. Every open finding is therefore in the class that does not block approval, and the reviewer's verdict block above is unchanged.

| Finding | Class | Carried to |
| --- | --- | --- |
| F6 | OUT_OF_SCOPE_HARDENING | a plugin ticket for the ticket and receipt templates |
| G1 | EVIDENCE_DEFECT | the next receipt of this project: smoke commands as command lines |
| G2 | EVIDENCE_DEFECT | the next change of `tests/test_calc.py` or the ledger: each ledger slice asserted non-empty |
| G3 | OUT_OF_SCOPE_HARDENING | the next ticket revision: the Agent Context binding row follows the state row |
| G4 | OUT_OF_SCOPE_HARDENING | the next correction dispatch: a `correction_ref` field |

```convergence-disposition
candidate: 45fc3873bb002d2dfd3fecd52eee31ad92de5f20
reviewer_verdict: CONVERGENCE_REVIEW_REQUIRED (seat:ticket-review/61b-review)
disposition: APPROVED
rule: CodeReview §5 rule B (owner-approved 2026-11-05)
carried:
  - F6
  - G1
  - G2
  - G3
  - G4
```
