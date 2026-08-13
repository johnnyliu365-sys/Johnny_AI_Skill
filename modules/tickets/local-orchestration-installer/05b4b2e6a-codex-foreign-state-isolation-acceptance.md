# 05B4B2E6A - Codex Foreign-State Isolation Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `DISPATCH_CONFIRMED / IN_PROGRESS` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E6A-01` / A1-A8 |
| Dependency | E6P guarded merge `7334cc5314592ac159e9418a145121d31e4156d5` |
| Planned owner | Existing owner1 task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent `workflow-implementation`; no new worktree/helper |
| Profile / XSS | `STANDARD`; one implementation owner / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

Prove only that the accepted success and compensation transactions preserve one
seeded foreign marketplace/plugin identity and its payload bytes. This is a
staging-oracle acceptance test, not new product behavior, target-project
coverage or another registration/compensation implementation.

## Frozen design

- Add only `tests/test_codex_registration_foreign_state_isolation_acceptance.py`.
  Production and staging-oracle source are read-only dependencies.
- The parent test owns two fresh disposable 05S1 leases: one for the integrated
  success entrypoint and one for the integrated compensation entrypoint. Each
  lease gets one exact initialized oracle and one exact owned request.
- Before each transaction, use the integrated oracle seed APIs to create one
  strongly typed foreign marketplace/plugin record plus payload. Choose
  prefix-similar foreign identity/path values that would expose broad-prefix
  matching without leaving the admitted lease.
- Snapshot exact foreign record tuples and exact foreign payload bytes before
  the transaction. Run only `run_registration_success_acceptance` or
  `run_registration_compensation_acceptance` with the same lease/oracle/request.
- After each transaction, prove the accepted owned result is correct and every
  foreign record tuple and payload byte is exactly unchanged. Owned success may
  remain present; owned compensation must be logically and physically absent.
- Tear down only the exact two caller-owned leases. Do not scan global TEMP,
  sibling worktrees, a target project or any path not derived from the lease.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `A1` | First red is the missing acceptance-test module; the implementation commit adds exactly the frozen test path. |
| `A2` | Each of two fresh leases seeds one exact strongly typed foreign marketplace/plugin identity and payload through integrated oracle APIs before the owned transaction. |
| `A3` | The success entrypoint returns its exact accepted result and produces the integrated owned success state. |
| `A4` | Success leaves the foreign marketplace/plugin record tuples and exact payload bytes identical to their pre-transaction snapshots. |
| `A5` | The compensation entrypoint returns exact accepted compensation with the integrated owned logical/physical absence and replay facts. |
| `A6` | Compensation leaves the foreign marketplace/plugin record tuples and exact payload bytes identical to their pre-transaction snapshots. |
| `A7` | Prefix-similar foreign identifiers/paths remain isolated; exact lease teardown succeeds and no target-project/global/sibling path is inspected or mutated. |
| `A8` | Reverse success record, success payload, compensation record, compensation payload and prefix-isolation gates; each turns red and exact bytes restore. Focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix: prefix-similar foreign state must survive both transactions
  byte-for-byte; only exact owned identity may change.
- Authority: use only integrated exact lease/oracle/request admission and the
  two accepted entrypoints; no fabricated claim, port or historical source.
- Error/exception: closed typed results only; no raw path, command, oracle state
  or exception escapes.
- Test truth: snapshots cover both logical records and physical bytes before
  and after both real accepted transactions.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, HTML/DOM renderer, JavaScript
  context or privileged bridge exists.

## Exact source and return

Writable implementation path only:

1. `tests/test_codex_registration_foreign_state_isolation_acceptance.py`

Return one implementation commit for that path, then one unique
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260814-367`. No
numeric line limit is an acceptance criterion.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f` / `CLOSURE-LOCAL-INSTALL-T05B4B2E6A-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05b4b2e6a_20260814_01` / `hnd_local_orchestration_install_05b4b2e6a_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e6a_20260814` / `rcpt_local_orchestration_install_05b4b2e6a_20260814` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e6a-20260814` / `q-local-orchestration-install-05b4b2e6a-20260814` |
| Side context | `scx-local-orchestration-install-05b4b2e6a-20260814-01` |
| Owner / lane | Existing owner1 task and permanent worktree; create only `codex/implementation-codex-foreign-state-isolation-05b4b2e6a` from the later exact dispatch registry commit. |

Freeze is not dispatch. Exact clean lane/readback, target-branch absence and a
second control commit carrying the dispatch registry are required before edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze / authority | Freeze `1204ed4c90e5195807238114d3df2d52abe3296e`; project-owner standing auto-continue under `PRG-20260809-042`; this control commit is the reviewed dispatch handoff. |
| Exact lane readback | Owner1 task is idle; permanent top-level and linked git-dir match; clean E6P branch at exact handoff `43b7d45b26e01087a6bfbbe1657187956ecce9e7`; tracked/ignored porcelain are empty; exactly three worktrees; target E6A branch is absent. |
| Branch admission | From the exact clean owner1 worktree, create only `codex/implementation-codex-foreign-state-isolation-05b4b2e6a` at the exact commit carrying this registry. Do not merge/copy a historical branch, create another worktree, reset, rebase, amend, force, stash or alter another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05b4b2e6a_20260814_01`; handoff `hnd_local_orchestration_install_05b4b2e6a_20260814`; allocation `aln_local_orchestration_install_05b4b2e6a_20260814`; receipt `rcpt_local_orchestration_install_05b4b2e6a_20260814`; correlation `corr-local-orchestration-install-05b4b2e6a-20260814`; question `q-local-orchestration-install-05b4b2e6a-20260814`; side context `scx-local-orchestration-install-05b4b2e6a-20260814-01`. |
| Writable return | Exactly the one frozen test path, one implementation commit, then only PRG-367 in one WPR-only handoff commit. |

This one-use receipt authorizes only E6A A1-A8 on the exact owner1 task/worktree.
The owner cannot orchestrate another Agent, issue a review decision, dispatch a
next ticket or perform push/package/install/staging/release/deployment work.
