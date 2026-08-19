# 03 — The Suite's Result Depends on Collection Order

| Field | Value |
| --- | --- |
| State | `CLOSED` |
| Severity | `P1` — it makes every "full suite green" claim conditional |
| Found | 2026-08-19, while qualifying W4 |
| Baseline | `main` = `e6d0240` |

## Correction: the first diagnosis was wrong

This ticket was opened claiming the suite's result depends on collection
order, because adding a file appeared to change the outcome. That was an
inference from a coincidence, and it is false. Run from a genuinely clean
state, the suite with an added trivial file passes `990 passed` with no
residue. The added file is innocent; something else was already true.

## The real finding, directly observed

The suite shares one project-owned runtime root, `tests/.johnny-runtime`,
and `DisposableEnvironmentAllocator` admits a provisioning request only when
**every** existing child of that root is in `_CLAIMED_MARKERS` — a
module-level dict, and therefore per-process.

An orphan lease directory is consequently unclaimable by construction: a new
process cannot have claimed it. `_prepare_runtime_parent` returns `False`,
every `provision` returns `INITIALIZATION_FAILED`, and roughly eighty
unrelated tests fail with `project-runtime provisioning must succeed`, which
names neither the cause nor the cure.

**How an orphan appears, reproduced:** two `pytest` processes running against
this checkout at the same time. Process A creates a lease; to process B that
lease is an unclaimed child, so B refuses everything (`84 failed`); whichever
process is interrupted or exits first can leave its lease behind. From then
on **every** future run is poisoned until a human deletes the directory. The
refusal itself is correct and deliberate (`ADR-20260813-007`: never delete
residue you cannot prove you own) — the defect is that a safe refusal is
delivered as eighty misleading failures and no path to recovery.

## What this cost, honestly

Several times this session a failing suite was diagnosed as "residue
pollution, clean and rerun". That diagnosis happened to be right, but it was
reached by pattern-matching rather than evidence, and the same reasoning
would have dismissed a real regression. That is the actual risk being fixed
here: not flaky tests, but a failure mode that trains the reader to ignore
failures.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `03-R1` | The mechanism is named by direct observation. **Done above**: per-process `_CLAIMED_MARKERS` versus a shared on-disk root; orphan created by concurrent processes, reproduced. |
| `03-R2` | A poisoned root is detected once, at the start of the run, and reported as a single named failure that states the path and the remedy. |
| `03-R3` | With a planted orphan lease, the guard fails and the diagnosis is unmistakable; without one, the suite is unaffected. Proven by reverse mutation. |
| `03-R4` | Nothing is auto-deleted and no existing assertion is weakened: `ADR-20260813-007` stands, and the guard only reports. |

## Closure evidence (2026-08-19, control-plane executed)

- `03-R1` Mechanism named by direct observation, not inference: per-process
  `_CLAIMED_MARKERS` against a shared on-disk root. Orphan creation
  reproduced by running two `pytest` processes against this checkout at once
  — `84 failed` in the second process, and a lease left behind afterwards.
- `03-R2` `tests/test_aaa_runtime_root_guard.py` reads the root once at import
  and fails a single named test stating the orphan paths, that this is not a
  code defect, the likely cause, and the exact remedy. The file name sorts
  first, so the diagnosis appears above the wreckage rather than under it.
- `03-R3` With a planted orphan lease the guard fails and is the first
  reported failure; with a clean root it passes silently and the suite is
  `990 passed, 16 skipped`.
- `03-R4` Nothing is deleted automatically and no assertion was weakened.
  `ADR-20260813-007` stands exactly as written: the allocator still refuses
  residue it cannot prove it owns. The guard only reports.

`mypy --strict` clean.

## The correction this ticket carries

The ticket was opened on a wrong diagnosis — "the result depends on collection
order" — reached by noticing that adding a file changed the outcome. Run from
a genuinely clean state, adding a file changes nothing. The real cause was
residue that was already present, and the added file was innocent. The
original claim is left visible above rather than edited away, because the
mistake is the point: the same pattern-matching that produced it is what this
guard exists to stop.

## Follow-up correction: an orphan lease is not normal

The closure above, and the guard's first wording, said "this is not a code
defect" with an ambiguous subject. Read plainly it says an orphan lease is
routine. It is not, and the distinction matters:

- The **refusal** to auto-delete is correct and stays (`ADR-20260813-007`).
- An **orphan lease** always means a lease was created and never torn down.
  That is a leak, not housekeeping.

Verified while making this correction: three consecutive single-process runs
of the environment-core and Codex acceptance suites leaked nothing, including
the cells that deliberately block teardown — those clean up after themselves.
So a normal run does not produce orphans, and one appearing means something
abnormal happened: concurrent `pytest` processes (reproduced), or a crashed
or killed run.

The guard's message now says so, and tells the reader to understand the cause
before deleting the evidence rather than clearing it reflexively. Deleting
first and asking later is the same habit that produced this ticket's wrong
opening diagnosis.
