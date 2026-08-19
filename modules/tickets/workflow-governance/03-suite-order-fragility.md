# 03 — The Suite's Result Depends on Collection Order

| Field | Value |
| --- | --- |
| State | `OPEN` |
| Severity | `P1` — it makes every "full suite green" claim conditional |
| Found | 2026-08-19, while qualifying W4 |
| Baseline | `main` = `e6d0240` |

## The finding, sharply reproduced

Adding a **single test file containing one trivially passing test** turns the
full suite from `989 passed` into `984 passed, 7 failed`. The added file's
content is irrelevant: it defines nothing, imports nothing, and touches no
shared state. W4's file, which does real work, produced only one failure.

```text
suite as-is                     989 passed
suite + tests/test_whole_chain_qualification.py   988 passed, 1 failed
suite + a file with one `assertTrue(True)`        984 passed, 7 failed
```

The failures cluster in `test_disposable_environment_core` and the Codex
acceptance suites — the tests that share the project-owned disposable runtime
root at `tests/.johnny-runtime`.

## Why this matters more than any single failure

Every closure in this repository is evidenced partly by "full suite green".
That claim is only as strong as its reproducibility, and right now the result
is a function of collection order rather than of the code. Two consequences,
both already observed during this session:

- Real failures were dismissed as "residue pollution" after a clean rerun.
  Sometimes that diagnosis was right; there is currently no way to tell it
  apart from a genuine order-dependent defect.
- A future regression could hide simply by landing next to a file that shifts
  ordering.

## What is *not* yet known

Whether the shared runtime root is the mechanism, or merely where the symptom
surfaces. Do not assume: the E10 lesson was that two correct-looking segments
can hide a dead join, and the same discipline applies here. Reproduce with
`-p no:randomly` and an explicit `--co` ordering diff before naming a cause.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `03-R1` | The mechanism is named by direct observation: which shared state, written by which test, read by which other, and why ordering changes the outcome. |
| `03-R2` | The suite passes under at least three deliberately different collection orders, including reverse. |
| `03-R3` | A regression makes order-dependence visible rather than silent — a test that fails when the shared root is polluted, rather than the pollution silently breaking unrelated cells. |
| `03-R4` | The fix does not weaken any existing assertion to obtain green. |
