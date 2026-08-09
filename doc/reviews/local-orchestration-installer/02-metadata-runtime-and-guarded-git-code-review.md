# 02 Metadata Runtime and Guarded Git Decision - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `02-metadata-runtime-and-guarded-git` |
| Result | `APPROVED / READY_TO_MERGE` |
| Reviewer | Codex / current `main` worktree |
| Single branch | `codex/implementation-local-metadata-git-02` |
| Closure | `CLOSURE-LOCAL-INSTALL-T02-01` / `D1..D8` |

## Boundary and revisions

The reviewed range is baseline `b44cd02`, implementation `6cc8fb5`, and
docs-only handoff `cc38c5d`. The implementation changes exactly the five
authorized production files and one test; the handoff changes only
`doc/WorkProgressReport.md`. No Ticket-01 source, real Git adapter,
target-project write, recovery engine, Ticket-03 behavior, schedule, or extra
implementation branch/worktree is included.

## Independent verification

| Check | Evidence |
| --- | --- |
| Scope / ceiling | Production `578 / 650`; test `333 / 500` non-blank lines. `git diff --check` passed. |
| Green run | Project Python 3.11 exact unittest: 8/8 passed. Strict mypy over six files: no issues. Compile and forbidden-capability scan passed. |
| Actual Git | An existing dirty temporary Git repo (`?? untracked.txt`) received an allowed decision and an empty repo received a lock-contended blocked decision. Every file digest and actual porcelain result was unchanged. |
| Reverse mutations | Eight isolated archives reversed D1..D8 independently. Every focused test failed for the intended reason; restored source passed. |
| Worktree | The implementation owner removed only reviewer-generated `__pycache__` directories and returned a clean branch without source/docs/commit/branch/worktree changes. |

## Closure mapping

| Closure | Result | Mutation-sensitive evidence |
| --- | --- | --- |
| `D1` | PASS | First claim completed; replay halted without a second Router/decision call. Removing the replay guard failed. |
| `D2` | PASS | Human wait stopped before the guarded decision. Bypassing that branch failed. |
| `D3` | PASS | Exact root passed; suffix, trailing separator, case, encoded separator, traversal and empty variants blocked. Removing locator equality failed. |
| `D4` | PASS | All five empty shapes were rejected for all six metadata values. Weakening nonblank validation failed. |
| `D5` | PASS | Direct/runtime paths enforced installation, project, root, clean base, fast-forward and lock gates with zero mutation. Removing the dirty guard failed. |
| `D6` | PASS | Four one-shot failures returned four distinct halt reasons without throw/mutation. Collapsing registry/decision reasons failed. |
| `D7` | PASS | Checkpoints/Router requests excluded locator and raw sentinels. Adding locator persistence failed; the independent actual-Git probe also passed. |
| `D8` | PASS | Five production files contain no forbidden effect/dynamic capability. Adding a subprocess marker failed the scan. |

## CodeReview.md checks

| Check | Result |
| --- | --- |
| Types and layering | PASS - immutable strict value models, finite enums/results and typed injected ports; no `Any` or `type: ignore`. |
| Logic / reachability | PASS - one runtime entry; direct and indirect paths converge on the same guard; all frozen failures are finite and effect-free. |
| Path and permission bypass | PASS - the seven-root matrix plus foreign installation/project/root, dirty/stale/non-fast-forward and lock cases are covered on both routes. |
| Test truthfulness | PASS - committed tests prove metadata/file-tree invariants; the reviewer separately used actual Git for porcelain/byte identity. |
| Security / privacy | PASS - persistence excludes locator/path/URI/raw fields; production has no Git command, subprocess, network, credential comparison or target-project write. |
| Dependencies / reuse | PASS - only existing public `ProjectId` and Pydantic are reused; Router engine, telemetry, Temporal, policy response and audit coordinator are absent. |

## Control-plane lane cleanup

Before the owner-requested cleanup Git listed four worktrees and six
implementation branches. Two extra worktrees were clean, inactive and fully
contained in `main`; they and three integrated branch refs were removed.
Rejected head `9eda250` and historical Router head `3fa2270` were retained as
archive tags, then their inactive branch refs were deleted. Git now lists only
`main` and the Ticket-02 branch across the control and sole implementation
worktrees. No commit was reset, overwritten, force-updated, pushed, deployed or
reused as implementation input.

## Conclusion

No open `IMPLEMENTATION_DEFECT`, `EVIDENCE_DEFECT`, `TICKET_DEFECT`,
`REQUIREMENT_CHANGED`, or blocking hardening item remains.

`APPROVED / READY_TO_MERGE`. Guarded local integration still requires a
conflict-free ancestry and merge-tree check. This does not authorize push,
deployment, schedule activation, real host/Git mutation, or Ticket-03 source.
