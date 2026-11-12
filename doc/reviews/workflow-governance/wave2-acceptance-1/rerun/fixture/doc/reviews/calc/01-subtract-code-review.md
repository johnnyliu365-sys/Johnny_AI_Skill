# calc／01-subtract Code Review

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | `calc` (ticket `modules/tickets/calc/01-subtract.md`, REQ-CALC-002) |
| 共同基準 | `e54b8dfa40befb07f39dcfd6bdd31d3eb8993b55` (`main` = `origin/main` at review time) |
| 受審 commit | candidate `a09a5d90535a273fd44b714363bb924d97778a35` (branch `seat/calc-subtract`); implementation commit `d4fca80be98dfbabb2b8fd53fe13ae44414e89ed`; docs-only close-out `a09a5d9` on top of it |
| 審閱者 | `seat:ticket-review/61r-review` (authored nothing in this ticket) |
| 結論 | `CHANGES_REQUESTED` |

Initial review of this Closure revision. Review clone: `git clone --no-hardlinks` of `origin`
into a review scratch directory, checked out at `a09a5d9` (and at `d4fca80` for the mutations);
the seat worktree and the seat branch were not touched. Interpreter: the project's declared
`jas-venv` Python 3.11.9 with `PYTHONUTF8=1`. Every command was run directly, with no
output-reducing wrapper; the outputs quoted below are unfiltered.

References applied: plugin `AGENTS.md`, `CodeReview.md`, `Workflow.md` §0 Router,
`references/review-checks.md`, `references/specification-ticketing.md`,
`references/implementation-tdd.md`, `modules/spec/workflow-governance.md` R4-1, R4-2, R4-7, R4-8,
`skills/johnny-project-takeover/scripts/README.md`, `template/README.md`.

## 規格／需求變更追溯

- Requirement source `doc/requirements/sources/calc.md` (sha256
  `251f1368…67fa`) matches the `source_sha256` of both rows in
  `doc/requirements/snapshots/calc/2026-11-12-v1.json`; `requirement_snapshot.py verify` →
  `OK rows=2`, exit 0; the snapshot rows equal `doc/requirements/sources/calc-rows.json`.
- REQ-CALC-002: "subtract(a, b) returns a - b for any two integers", status `active`, v1. The
  ticket cites it directly from the snapshot (no SPEC; intake from snapshot per R4-5).
- No CHG or PRD is involved; nothing in the diff changes a requirement.

## Context、tickets、elements 與實作衝突核對

Ticket and dispatch:

- Ticket blob at `e54b8df` (PLANNED) carries
  `dispatch=sha256:e6ca4afb19c0b92acc868dee213cab4aa75adac126f0d92279652878dde06d2a`.
  `sha256sum` of `doc/handoffs/2026/governance/dispatch/calc-01-subtract.md` at `e54b8df` and at
  `a09a5d9` is that same value; the dispatch file has one commit (`e54b8df`). **Digest equals the
  state row.** The DONE row at `a09a5d9` drops the `dispatch=` part, as the template allows once
  the dispatch is no longer pending.
- Dispatch envelope: `ACTION_REQUIRED`, `dispatch_ref`, `ticket`, `receipt`, `owner_task`.
  `registry_commit` is absent and there is no `preflight:` block (finding F2).
- Ticket schema against `review-checks.md` › Ticket dispatch schema review: present — State,
  Implementation language, owner, worktree, branch, baseline, receipt. Absent — a finite
  `Acceptance Closure Set` with a revision, Profile / resource, XSS classification, strict
  checker, allocation, correlation (finding F3).
- Worktree binding: `git worktree list` shows `.worktrees/calc-subtract` under the repository
  root on `seat/calc-subtract` at `a09a5d9`, clean, ignored by `.gitignore:1:.worktrees/`, no
  junction under the root.

Implementation (`git diff e54b8df d4fca80`): `src/calc.py` adds
`def subtract(a: int, b: int) -> int: return a - b`; `tests/test_calc.py` imports `subtract` and
adds `SubtractTests` with `test_subtract` (5, 3 → 2), `test_subtract_negative_result`
(3, 5 → -2), `test_subtract_zero` (0, 0 → 0). `add` and its test are unchanged; no file outside
the ticket's 責任邊界 is touched; standard library only. Behaviour is correct for REQ-CALC-002
(Python `int` subtraction is exact for any two integers). Types are complete; my
`mypy --strict src tests` → `Success: no issues found in 4 source files`, exit 0.

Docs-only commit (`git diff --name-status d4fca80 a09a5d9`): exactly
`A …/receipts/calc-01-subtract.md`, `A …/receipts/calc-01-subtract/green.txt`,
`A …/mutation-red.txt`, `A …/mutation-restored.txt`, `M modules/tickets/calc/01-subtract.md`.
The ticket hunk changes only the 狀態 row, the 紅燈輸出 line and the 完成回寫 lines. The tool
blobs are identical at both commits (`src/calc.py` `66ac98b…`, `tests/test_calc.py` `a0c952c…`),
so the receipt's cells at `d4fca80` describe the code at the candidate.

Applicability records (CodeReview §2):

- XSS / privileged JS: not applicable — the diff is one pure integer function and its unit
  tests; no browser, WebView, DOM, JavaScript source or sink exists in the project. The ticket
  should still carry the classification (F3).
- Secret, formal log, Provider, webhook, external effect: none in the diff.
- Agent control, task/worktree: one implementer seat, no helper; worktree verified above.
- Profile fan-out: one lane; the ticket names no Profile (F3).
- POC/staging ancestry: environment `LOCAL`; ancestry is linear
  `a09a5d9 → d4fca80 → e54b8df = origin/main`; no POC, no staging.

## 發現、風險與處置

| # | Class | Blocking | Finding | Route |
| --- | --- | --- | --- | --- |
| F1 | `TICKET_DEFECT` | yes | Contract gate is red for this ticket's own requirement: `NO_SPEC_FOR_REQUIREMENT REQ-CALC-002`. `tests/test_calc.py` carries no `# requirement:` / `# source: … sha256:` / `# mutation:` first comment block (R4-8), and the ticket never asked for one (對應規格 ID 不適用, 完成定義 names only pytest). The gate chain of Workflow §0 (dispatch lint → preflight → contract gate → evidence gate → coverage map → integration) therefore does not pass for this candidate. The same run also reports `NO_SPEC_FOR_REQUIREMENT REQ-CALC-001`, which is pre-existing on `main` and outside this ticket (`add` is 禁止修改); see F6. | Control plane revises the ticket to name the spec contract for REQ-CALC-002 (declaration block, source digest, named mutation, expected values from a ledger per R4-6/R4-8); then an additive correction on `seat/calc-subtract`. |
| F2 | `TICKET_DEFECT` | yes | The dispatch cannot pass the preflight gate: `preflight.py` → `no preflight: block in the dispatch`, exit 3. The envelope also lacks `registry_commit`, which `specification-ticketing.md` › Dispatch normalization lists in the first dispatch envelope. `dispatch_lint.py` passes (it checks form only). | Control plane re-issues the dispatch with a `preflight:` item for pytest (and the strict checker of F4) and `registry_commit`, and records the new digest in the state row. |
| F3 | `TICKET_DEFECT` (`TICKET_SCHEMA_INVALID`) | yes | `review-checks.md` › Ticket dispatch schema review requires a finite Closure, Profile / resource, XSS classification, allocation and correlation; `specification-ticketing.md` also requires the strict checker. None is in the ticket. The rule states this holds "even if the implementation happens to look correct". | Same ticket revision as F1. |
| F4 | `EVIDENCE_DEFECT` | no (behaviour verified) | The receipt's STATEMENT says strict type check was not run because none is configured. `implementation-tdd.md` names `mypy --strict` for Python and ticket completion requires the type gate to pass or an authorized blocker; mypy 2.3.0 is installed in the project's declared interpreter. My run passes, so the candidate is correct; the receipt lacks the cell. Rooted in F3 (no strict checker named). | Add a `mypy --strict` run cell in the correction receipt. |
| F5 | `EVIDENCE_DEFECT` | no (behaviour correct) | Counter-mutation M2 (below) turned **zero** tests red: routing the subtraction through `float` passes all four tests, yet is wrong for integers beyond 2**53 (`int(float(2**53+1) - 0.0)` = 9007199254740992). The AC says "for any two integers"; no test pins that range. `test_subtract_zero` also discriminates none of M1, M2 or the implementer's `a + b`. | Add a cell with operands beyond the float mantissa (e.g. `2**64 + 1`, `-(2**64)`) in the same correction. |
| F6 | `OUT_OF_SCOPE_HARDENING` | no | (a) REQ-CALC-001 has no spec (pre-existing, contract gate red on `main`). (b) The contract gate's `LITERAL_EXPECTED` rule only inspects `assert` statements, so `self.assertEqual(subtract(5, 3), 2)` is invisible to it; a header added for F1 alone would turn the gate green while the expected values stay literals (overlap-masking door). (c) The plugin's `template/modules/tickets/TEMPLATE.md`, copied verbatim here, has no rows for the fields F3 requires. | Follow-up `PLANNED` tickets: (a) in this project; (b) and (c) in the plugin. |

Observations (not findings): the `mutation-red` capture shows only `git diff --stat`, but the
failure values `8 != 2` / `8 != -2` corroborate the stated `a + b` mutation; the
`mutation-restored` capture prints `?? doc/handoffs/2026/governance/receipts/` before
"tree clean after restore" — that untracked path is the receipt being written, and no tracked
file is listed, so the restore is genuine.

## 驗證證據

All commands run in the review clone, `PYTHONUTF8=1`, interpreter `jas-venv` Python 3.11.9,
scripts from the plugin copy `skills/johnny-project-takeover/scripts/`.

| Gate / check | Command (abridged) | Result | Exit |
| --- | --- | --- | --- |
| pytest at candidate | `python -m pytest -q -p no:cacheprovider` @ `a09a5d9` | `4 passed` | 0 |
| strict type | `python -m mypy --strict src tests` @ `a09a5d9` | `Success: no issues found in 4 source files` | 0 |
| dispatch lint | `dispatch_lint.py doc/handoffs/2026/governance/dispatch/calc-01-subtract.md` | `LINT PASS` | 0 |
| preflight | `preflight.py <same dispatch>` | `error: no preflight: block in the dispatch` (F2) | 3 |
| requirement snapshot | `requirement_snapshot.py verify doc/requirements/snapshots/calc/2026-11-12-v1.json` | `OK rows=2` | 0 |
| contract gate | `contract_gate.py --repo . --snapshot <v1> --specs tests` | `NO_SPEC_FOR_REQUIREMENT REQ-CALC-001`, `NO_SPEC_FOR_REQUIREMENT REQ-CALC-002`, `requirements=2 specs=1 defects=2` (F1, F6a) | 1 |
| evidence gate | `evidence_gate.py <receipt> --repo . --candidate d4fca80be98dfbabb2b8fd53fe13ae44414e89ed --tool src/calc.py --tool tests/test_calc.py` | `cells=3 defects=0` | 0 |
| evidence gate, required cells | same plus `--require-cell green-tests --require-cell mutation-red --require-cell mutation-restored` | `cells=3 defects=0` | 0 |
| evidence gate at queue candidate | same with `--candidate a09a5d90535a273fd44b714363bb924d97778a35` | three `CANDIDATE_MISMATCH` (expected: the cells ran at the implementation commit; the tool blobs are identical at both commits) | 1 |
| coverage map | `coverage_map.py --repo . --base e54b8df --candidate a09a5d9… --map doc/handoffs/2026/governance/coverage-map.json --specs tests` (also `--base origin/main`) | `removed=0 defects=0` | 0 |
| index pins | `index_pins.py --check` | `drift=0 files=0 defects=0 indexes=0` (no pinned index in the project) | 0 |
| repair guard | `repair_guard.py --repo . --repair a09a5d9 --dispatch <dispatch>` | `no repair_allowlist: line in the dispatch`. Not applicable: neither `d4fca80` nor `a09a5d9` is a tool-repair commit (R4-3, R4-8) | 3 |
| receipt fence check | `receipt_fence_check.py <receipt> "## green-tests" doc/handoffs/2026/governance/receipts` | `CMD_MISSING`. Not applicable: superseded by the evidence gate for R4-7 cell receipts (scripts README) | 1 |
| integration | `integrate.py` | not run (outside this seat's authority) | — |
| diff scope | `git diff --name-status d4fca80 a09a5d9` | receipt, three captures, ticket only | — |
| dispatch digest | `sha256sum` of the dispatch at `e54b8df` and `a09a5d9` | `e6ca4afb…d2a` both, equals PLANNED row | — |

Reviewer counter-mutation (review-checks › Reviewer counter-mutation), at `d4fca80`, run
directly with `pytest -q -p no:cacheprovider -rA` (unfiltered), each restored with
`git checkout -- src/calc.py`, followed by an empty `git status --porcelain` and a green suite:

- M1, operand order (a door the implementer did not use: their mutation was `a + b`):
  `return a - b` → `return b - a`. Red: `test_subtract` (`-2 != 2`),
  `test_subtract_negative_result` (`2 != -2`); green: `test_add`, `test_subtract_zero`; exit 1.
  Non-commutativity is pinned on the production seam `from src.calc import subtract`.
- M2, integer range: `return a - b` → `return int(float(a) - float(b))`. **Zero red**, all four
  tests pass, exit 0 → F5.
- Restore: `4 passed`, exit 0; clone returned to `a09a5d9`.

## 未解項與 handoff 結論

`CHANGES_REQUESTED`. The implementation is correct and strictly typed; the blocking items are
control-plane defects (F1, F2, F3): the contract gate is red for REQ-CALC-002 and the ticket and
dispatch are not schema-complete, so the candidate cannot pass the R4-2 gate chain. Route: the
control plane revises the ticket (Closure revision, Profile, XSS classification, strict checker,
spec contract for REQ-CALC-002, a large-integer cell) and re-dispatches with a `preflight:` block
and `registry_commit`; the implementer then makes an additive correction on
`seat/calc-subtract` (no reset, amend or force) that also closes F4 and F5, and the correction
review reruns every gate above. F6 goes to follow-up tickets and does not block. This record
does not submit, land or authorize any push of the candidate.

```review-verdict
candidate: a09a5d90535a273fd44b714363bb924d97778a35
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/61r-review
reviewed_at: 2026-11-12
```

## Correction review

| 欄位 | 內容 |
| --- | --- |
| 受審 commit | candidate `068a57044246e2b195aafa18e23d74cb0697de15` (tip of `seat/calc-subtract`); correction commit `3c51c45fe5b958e9aed7f601649ab1d98062b8bb`; merge of `origin/main` `b70830c`; receipt-only commit `068a570` |
| 共同基準 | `486840032ea90c56e538de2d17ae81a6dda26d2b` (`main` = `origin/main`; ticket revision02 and dispatch `calc-01-subtract-c1.md`), which is also the merge base of the candidate |
| 審閱者 | `seat:ticket-review/61r-review` |
| 結論 | `CONVERGENCE_REVIEW_REQUIRED`: no blocking finding remains; one open `EVIDENCE_DEFECT` and two `OUT_OF_SCOPE_HARDENING` items, all in the non-blocking class of CodeReview §5 rule B |

This is the correction review of ticket 01, as the control plane designated it. Revision02 calls
itself "Closure revision revision02". If the control plane counts revision02 as a new Closure
revision, this review is that revision's initial review, and the verdict would be
`CHANGES_REQUESTED` for C1 alone. The control plane decides that reading; the findings are the same
either way. Same review clone (`--no-hardlinks`), fetched to the new tips; same interpreter and
`PYTHONUTF8=1`. Every test run was read unfiltered (`pytest -q -rA`, no output-reducing wrapper).

### Admission

- Ticket revision02 on `main` at `4868400` has the State row `IN_PROGRESS`, with
  `dispatch=sha256:6527eb9f62e0f59ace3dcf9c6f01a0003c5cd74418cd7bc1d83f1c6ff32fa43c`.
  `sha256sum doc/handoffs/2026/governance/dispatch/calc-01-subtract-c1.md` gives the same value.
  The dispatch has one commit (`4868400`). It carries `registry_commit` `3e0fb3a` (this record),
  `correction_ref`, `receipt`, `owner_task` and a `preflight:` block.
- **The merge took main's revision02 ticket whole.** The ticket blob is `de529b3…` at `4868400`,
  `b70830c`, `3c51c45` and `068a570`. `git diff 4868400 b70830c -- modules/tickets/calc/01-subtract.md`
  is empty. The review record (`1750f8e…`) and the c1 dispatch (`52f89d5…`) are also the same on
  both sides. The merge's parents are `a09a5d9` and `4868400`.
- Correction commit `git diff --name-status b70830c 3c51c45`: `M tests/test_calc.py` and
  `A tests/ledger/calc.json`. Both are inside the revision02 `johnny-boundary` block. `src/calc.py`
  is unchanged (blob `66ac98b…`), and `add` is untouched.
- **`git diff 3c51c45 068a570` touches only the receipt and its captures**: it adds
  `receipts/calc-01-subtract-c1.md` and ten files under `receipts/calc-01-subtract-c1/`, nothing
  else. The three tool blobs (`src/calc.py`, `tests/test_calc.py`, `tests/ledger/calc.json`) are
  identical at `3c51c45` and `068a570`.
- Ledger check: `tests/ledger/calc.json` holds only `int` values and no repeated `name`. The
  expected values are arithmetically right: 2**64+1 − (−2**64) = 2**65+1; −2**64 − 1.

### Closure of F1 to F5

| Initial finding | Status | Evidence (my runs) |
| --- | --- | --- |
| F1 contract gate red | closed | `contract_gate.py --repo . --snapshot doc/requirements/snapshots/calc/2026-11-12-v1.json --specs tests` → `requirements=2 specs=1 defects=0`, exit 0. The header declares REQ-CALC-001 and REQ-CALC-002, source `calc.md` at its real sha256, and four mutations. No assertion holds a literal expected value; `assertEqual` reads `case["expected"]` from the ledger. |
| F2 preflight / envelope | closed | `preflight.py …/calc-01-subtract-c1.md` → `tools=2 served=2`, exit 0; `dispatch_lint.py` → `LINT PASS`, exit 0; `registry_commit` present |
| F3 ticket schema | closed | Revision02 names the Closure set (revision02), Profile `POC`, resources, XSS not applicable with a reason, strict checker, allocation and correlation |
| F4 strict checker | closed | `mypy --strict --python-version 3.11 src tests` → `Success: no issues found in 4 source files`, exit 0; receipt cell `strict` |
| F5 integer range | closed | My float mutation M2, below, now turns 3 tests red |

### Gates, run by me at the candidate

| Gate / check | Result | Exit |
| --- | --- | --- |
| `pytest -q -p no:cacheprovider` @ `068a570` | `7 passed` | 0 |
| `mypy --strict --python-version 3.11 src tests` | no issues in 4 files | 0 |
| `dispatch_lint.py` c1 dispatch | `LINT PASS` | 0 |
| `preflight.py` c1 dispatch | `tools=2 served=2` | 0 |
| `requirement_snapshot.py verify` v1 | `OK rows=2` | 0 |
| `contract_gate.py` (as above) | `requirements=2 specs=1 defects=0` | 0 |
| `evidence_gate.py …/calc-01-subtract-c1.md --repo . --candidate 3c51c45fe5b958e9aed7f601649ab1d98062b8bb --tool src/calc.py --tool tests/test_calc.py --tool tests/ledger/calc.json` plus `--require-cell` for all ten run cells | `cells=10 defects=0` | 0 |
| `coverage_map.py --base 4868400 --candidate 068a570 --map doc/handoffs/2026/governance/coverage-map.json --specs tests` (also `--base a09a5d9`) | `removed=0 defects=0`. The three original test names survive. | 0 |
| `index_pins.py --check` | `drift=0 files=0 defects=0 indexes=0` | 0 |
| `repair_guard.py --repair 3c51c45 --dispatch <c1>` | `no repair_allowlist: line`. Not applicable: `3c51c45` is not a tool-repair commit. | 3 |
| `receipt_fence_check.py` | Not applicable: superseded by the evidence gate for R4-7 cell receipts (unchanged from the initial review) | — |
| `integrate.py` | not run (outside this seat) | — |

### The open choice: mutation `add-subtracts-operands`

The spec header of `tests/test_calc.py` declares `mutation: add-subtracts-operands`. The receipt
STATEMENT says it was declared but not run, "because add is outside this ticket's boundary". That
reason does not hold, for two reasons:

- The boundary (`禁止修改 add`) governs what the candidate commits. A bounded reverse mutation is
  applied and then restored byte for byte, so it commits nothing. The seat itself temporarily
  edited `src/calc.py`, the file that holds `add`, for its three `subtract` mutations.
- Revision02 puts the REQ-CALC-001 contract binding inside the Closure set. That binding includes
  the declared mutation. `implementation-tdd.md` asks for reverse-mutation evidence for each named
  behaviour.

The contract gate only counts `mutation:` declarations. A mutation that is declared but never run
is therefore exactly what the gate cannot see.

I ran it (M3, below): `test_add` turns red (`-1 != 5`) and the suite is green after the restore. The
mutation is real, and the property is pinned at the production seam. What is missing is the seat's
evidence of it → C1.

### Reviewer counter-mutations

All at `3c51c45`, each followed by `git checkout --`, an empty `git status --porcelain` and a green
suite (`7 passed`). The clone was then returned to `068a570`, clean.

- M2, float routing (the same mutation as my initial review): `return int(float(a) - float(b))`.
  Red: `test_subtract_beyond_64_bit` (`36893488147419103232 != 36893488147419103233`),
  `test_subtract_beyond_float_mantissa` (`9007199254740992 != 9007199254740993`),
  `test_subtract_large_negative` (`-18446744073709551616 != -18446744073709551617`); exit 1.
- M3, the declared `add-subtracts-operands`: in `add`, `return a + b` → `return a - b`. Red:
  `test_add` (`-1 != 5`); exit 1.
- M4, a new door that neither the seat nor I had used, 64-bit two's-complement wrap:
  `return ((a - b + 2**63) % 2**64) - 2**63`. Red: `test_subtract_beyond_64_bit` (`1 != 36893488147419103233`),
  `test_subtract_large_negative` (`-1 != -18446744073709551617`); exit 1.
- M5, the "first match" door on the oracle layer: I appended a contradictory ledger row
  `{"name": "basic", "a": 5, "b": 3, "expected": 999}`. **Zero red**: `7 passed`, exit 0. `_case` returns
  the first row with a matching name, so a later contradictory row is never read → C2.

### Findings

| # | Class | Blocking (§5 rule B) | Finding | Carry to |
| --- | --- | --- | --- | --- |
| C1 | `EVIDENCE_DEFECT` | no: candidate correct, property pinned (M3 red) | The declared mutation `add-subtracts-operands` is in the Closure (REQ-CALC-001 binding) and has no run cell in the receipt. The seat's stated reason misreads the boundary. | The next change to `tests/test_calc.py`, or a follow-up ticket: add `mut-add-subtracts` and its restored cell |
| C2 | `OUT_OF_SCOPE_HARDENING` | no | Ledger lookup is first-match. A duplicate `name` with a different `expected` is silently ignored (M5, zero red). The current ledger has no duplicates, so no Closure item is violated. A later "correction" appended to the ledger would not take effect, and nothing would say so. | Follow-up `PLANNED` ticket: assert unique ledger names and that every ledger row is consumed by a test |
| C3 | `OUT_OF_SCOPE_HARDENING` | no | `_load` assigns `json.loads(...)` (an `Any`) to `dict[str, list[Case]]` without validating it, which mypy accepts. A ledger value written as a float would be accepted unchecked: `9007199254740993.0` loads as `9007199254740992.0` and would mask M2. The current values are all `int` (checked above). This is test-layer code reading a tracked fixture, not product source under P0. | Same follow-up ticket: validate each row's types when loading |

No `IMPLEMENTATION_DEFECT` and no `TICKET_DEFECT` remains. Nothing changes an exit-code
classification or a security or scope boundary, and nothing violates P0. F1 to F5 are closed. C1
is not the kind of gap that "would let through a change it should not" (M3 shows the test already
catches that regression), so under rule B it may be carried rather than fixed before landing. The
control plane decides the disposition. This seat does not write a `convergence-disposition` block,
and does not submit, land or push the candidate.

```review-verdict
candidate: 068a57044246e2b195aafa18e23d74cb0697de15
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/61r-review
reviewed_at: 2026-11-12
```

## Control plane note on the cadence

Revision02 is a new closure revision; the ticket's Revision02 section says so. The review above is therefore revision02's initial review, not its correction review. Under CodeReview §5 an initial review returns `APPROVED` or `CHANGES_REQUESTED`, so the control plane reads its outcome as `CHANGES_REQUESTED` for C1 only. C1 is the run cell missing from the receipt for the declared mutation `add-subtracts-operands`. C2 and C3 are carried as hardening of the test ledger. The reviewer's verdict block above is left as written. The next review is revision02's one correction review.

## Revision02 correction review

| 欄位 | 內容 |
| --- | --- |
| 受審 commit | candidate `4d68e3b1f8ccf22f19ff76a006f7370eb8cf7f0c` (tip of `seat/calc-subtract`). It consists of the merge of `origin/main` `92d59c0623bfbf3e8c9f6e1509e0289c0d4321f6` (docs only) and, on top, the c2 receipt-only commit `4d68e3b`. |
| 共同基準 | `20d7ce4de5289249f1f78ff48d9f64be1ec98958` (`main` = `origin/main`, carrying the control-plane note above); it is the merge base of the candidate |
| 審閱者 | `seat:ticket-review/61r-review` |
| 結論 | `APPROVED` |

This is the one correction review of revision02, following the control-plane note above. Same
`--no-hardlinks` review clone, fetched to the new tips; same interpreter and `PYTHONUTF8=1`. Test
runs were read unfiltered (`pytest -q -rA`).

### Admission

- **`git diff --name-status 068a570 4d68e3b`** adds and changes only three things:
  - `M doc/reviews/calc/01-subtract-code-review.md`, which arrives through merge `92d59c0`
    (parents `068a570`, `20d7ce4`). The blob at `4d68e3b` is `603f49a…`, identical to `main` at
    `20d7ce4`, so the seat authored nothing under the forbidden `doc/reviews/`.
  - `A receipts/calc-01-subtract-c2.md`.
  - `A` its two captures under `receipts/calc-01-subtract-c2/`.

  `git diff 068a570 92d59c0` is the review record only; `git diff 92d59c0 4d68e3b` is the c2
  receipt and its captures only.
- **The tool blobs are identical** at `3c51c45`, `92d59c0` and `4d68e3b`: `src/calc.py`
  `66ac98b…`, `tests/test_calc.py` `91d5e5b…`, `tests/ledger/calc.json` `cb0a556…`. The ticket blob
  `de529b3…` (revision02) is also unchanged.
- **The c1 receipt and its ten captures are unchanged.** The c1 blob is `50a104d…` at `068a570`
  and at `4d68e3b`, and `git diff --stat 068a570 4d68e3b` over the c1 and initial receipts is empty.
- **The dispatch digest still equals the state row:** `sha256sum` of the c1 dispatch is
  `6527eb9f…fa43c`, the same as the `IN_PROGRESS` row.

### C1 closed

- `evidence_gate.py receipts/calc-01-subtract-c2.md --repo . --candidate 92d59c0623bfbf3e8c9f6e1509e0289c0d4321f6 --tool src/calc.py --tool tests/test_calc.py --tool tests/ledger/calc.json --require-cell mut-add-subtracts --require-cell mut-add-subtracts-restored`
  → `cells=2 defects=0`, exit 0.
- `evidence_gate.py receipts/calc-01-subtract-c1.md --candidate 3c51c45fe5b958e9aed7f601649ab1d98062b8bb`, with
  the same three tools and `--require-cell` for all ten cells → `cells=10 defects=0`, exit 0.
- Cross-check: c2 against `3c51c45` gives two `CANDIDATE_MISMATCH`, exit 1. The gate does bind each
  receipt to its own commit.
- The c2 `mut-add-subtracts` capture shows the diff `return a + b` → `return a - b` in `add` and
  `test_add` red (`-1 != 5`). My own run of the same mutation at `92d59c0` gives the same red
  (exit 1), then `7 passed` after the restore.
- The c2 STATEMENT withdraws the earlier boundary reason as wrong and names c1 as the receipt it
  adds to.

### Is a second, additive receipt acceptable evidence?

Yes, for these reasons:

- CodeReview §5 asks that a correction keep the valid receipt and add to it, without
  reset, amend or force. Keeping c1 byte-identical and adding c2 does exactly that.
- The evidence gate binds a receipt to one `--candidate`. A cell run at `92d59c0` therefore cannot
  be added to c1 without breaking c1's gate, unless all ten cells are rerun.
- Each receipt passes its own gate on its own commit, and the tool blobs are identical across
  `3c51c45`, `92d59c0` and `4d68e3b`. Together the two receipts describe the candidate's code.
- c2 states its relation to c1 and its commit; its captures sit under the same evidence root.

One condition for close-out: the state row names one receipt path, and that path is c1. c1
cannot point forward to c2. When the control plane writes the `DONE` row, it should name c2
beside c1, so that a session resuming from the ticket and its receipt (R4-1) reaches the C1
evidence. The template has a single receipt slot → D2.

### Earlier closures still hold (run at `4d68e3b`)

| Gate / check | Result | Exit |
| --- | --- | --- |
| `pytest -q -p no:cacheprovider` | `7 passed` | 0 |
| `mypy --strict --python-version 3.11 src tests` | no issues in 4 files | 0 |
| `dispatch_lint.py` c1 dispatch | `LINT PASS` | 0 |
| `preflight.py` c1 dispatch | `tools=2 served=2` | 0 |
| `requirement_snapshot.py verify` v1 | `OK rows=2` | 0 |
| `contract_gate.py --repo . --snapshot … --specs tests` | `requirements=2 specs=1 defects=0` | 0 |
| `coverage_map.py --base 20d7ce4 --candidate 4d68e3b …` (also `--base 068a570`) | `removed=0 defects=0` | 0 |
| `index_pins.py --check` | `drift=0 files=0 defects=0 indexes=0` | 0 |
| `repair_guard.py --repair 4d68e3b --dispatch <c1>` | `no repair_allowlist: line`. Not applicable: no tool-repair commit. | 3 |
| `receipt_fence_check.py` | not applicable: superseded by the evidence gate for cell receipts | — |
| `integrate.py` | not run (outside this seat) | — |

F1 to F5 stay closed. My M2 (float), M4 (64-bit wrap) and the seat's three subtract mutations
were run at `3c51c45`, and the tool blobs are unchanged since.

### Reviewer counter-mutation

At `92d59c0`, restored each time with `git checkout --` and an empty `git status --porcelain`; the
clone was then returned to `4d68e3b`, clean.

- M6, the declared `add-subtracts-operands`, rerun independently: `test_add` red (`-1 != 5`), exit 1.
- M7, a new door: float routing on the REQ-CALC-001 contract that this spec now binds,
  `add`: `return a + b` → `return int(float(a) + float(b))`. **Zero red**: `7 passed`, exit 0. The
  mutant is wrong beyond 2**53 (`2**53+1 + 0` gives `9007199254740992`). The ledger's only `add`
  case is (2, 3) → D1.

### Findings

| # | Class | Blocking | Finding | Carry to |
| --- | --- | --- | --- | --- |
| D1 | `OUT_OF_SCOPE_HARDENING` | no | `add` is not pinned beyond small integers (M7, zero red). This violates no revision02 Closure item: REQ-CALC-001 binds the contract only, `add` is `禁止修改`, and the TDD design asks only that the existing `add` test stay green. The candidate's `add` is unchanged since the skeleton and correct. | A follow-up `PLANNED` ticket for REQ-CALC-001 range cells. It can share the ledger-hardening ticket of C2/C3. |
| D2 | `OUT_OF_SCOPE_HARDENING` | no | The ticket state row and the plugin template hold one receipt path. A correction that adds a receipt has no slot in the state file, so c2 is reachable only through its own STATEMENT and this record. | Control-plane close-out: name c2 in the `DONE` row. Plugin follow-up: let the template's state row list additive receipts. |

C2 and C3 remain carried as the control-plane note says. No `IMPLEMENTATION_DEFECT`,
`EVIDENCE_DEFECT` or `TICKET_DEFECT` is open. C1 is closed with gate-verified evidence, and
every earlier closure still holds. This approval admits the candidate to the queue under
R4-4/R4-7. It does not itself submit, land, push the candidate or authorize any external effect.

```review-verdict
candidate: 4d68e3b1f8ccf22f19ff76a006f7370eb8cf7f0c
verdict: APPROVED
reviewer: seat:ticket-review/61r-review
reviewed_at: 2026-11-12
```

