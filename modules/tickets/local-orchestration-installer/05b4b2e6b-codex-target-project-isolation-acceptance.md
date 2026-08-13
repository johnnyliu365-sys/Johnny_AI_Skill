# 05B4B2E6B - Codex Target-Project Isolation Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `COMPLETE / APPROVED / INTEGRATED` - guarded merge `0e0934d` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E6B-01` / B1-B8 |
| Dependency | E6P guarded merge `7334cc5314592ac159e9418a145121d31e4156d5` |
| Planned owner | Existing owner2 task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent `workflow-implementer-2`; no new worktree/helper |
| Profile / XSS | `STANDARD`; one implementation owner / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

Prove only that accepted success and compensation transactions cannot change
two external synthetic target-project repositories. This is disposable
acceptance evidence, not real target-project access, Git product behavior or a
second registration/compensation implementation.

## Frozen design

- Add only
  `tests/test_codex_registration_target_project_isolation_acceptance.py`.
  Production and staging-oracle source are read-only dependencies.
- The parent test owns one unique system-TEMP root and creates exactly two
  synthetic sentinel Git repositories beneath it. Each repository has committed
  text and binary sentinels and begins with clean tracked/ignored porcelain.
- Git subprocesses use argument vectors with `shell=False`; commits use only
  command-scoped `-c user.name=...` and `-c user.email=...`. Never change global
  or user Git configuration.
- Snapshot canonical roots, HEAD/tree/index identity, exact tracked paths and
  bytes, tracked porcelain and ignored porcelain for both repositories.
- Run integrated success and compensation entrypoints in separate disposable
  oracle leases whose requests never reference either sentinel repository.
- After each transaction and once more before cleanup, prove both complete
  repository snapshots are identical. Also prove no untracked/ignored file,
  lock, config, ref, index mutation or nested repository appeared.
- Tear down only the exact leases and parent-owned TEMP root. Never read or
  write a real target project, sibling worktree or global filesystem location.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `B1` | First red is the missing acceptance-test module; the implementation commit adds exactly the frozen test path. |
| `B2` | Parent creates exactly two unique synthetic Git repositories under one ticket-owned system-TEMP root, each with committed text/binary sentinels and initially clean tracked/ignored porcelain. |
| `B3` | Exact pre-transaction snapshots cover canonical root, HEAD/tree/index identity, tracked paths/bytes and tracked/ignored porcelain for both repositories. |
| `B4` | Success runs only inside a separate disposable oracle lease whose request does not reference either repository; both complete repository snapshots remain exact afterward. |
| `B5` | Compensation runs only inside another disposable oracle lease whose request does not reference either repository; both complete repository snapshots remain exact afterward. |
| `B6` | Final readback proves no untracked/ignored file, lock, config, ref, index mutation or nested repository exists in either sentinel repository. |
| `B7` | Git uses argument-vector `shell=False` calls and command-scoped identity only; exact lease/TEMP teardown succeeds and no real target project or sibling/global path is inspected or mutated. |
| `B8` | Reverse success bytes, success porcelain, compensation bytes, compensation porcelain and two-repository coverage gates; each turns red and exact bytes restore. Focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix: the two sentinel repositories are independent exact roots;
  prefix, parent, sibling or global matching cannot authorize access.
- Authority: accepted oracle transactions receive no target-project reference;
  Git is test-owned readback/setup only and never part of product effects.
- Error/exception: subprocess failures stay inside finite test assertions; no
  path, command, environment or exception enters product metadata.
- Test truth: exact committed bytes and Git identities are snapshotted for two
  repositories before, between and after both transactions.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, HTML/DOM renderer, JavaScript
  context or privileged bridge exists.

## Exact source and return

Writable implementation path only:

1. `tests/test_codex_registration_target_project_isolation_acceptance.py`

Return one implementation commit for that path, then one unique
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260814-368`. No
numeric line limit is an acceptance criterion.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f` / `CLOSURE-LOCAL-INSTALL-T05B4B2E6B-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05b4b2e6b_20260814_01` / `hnd_local_orchestration_install_05b4b2e6b_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e6b_20260814` / `rcpt_local_orchestration_install_05b4b2e6b_20260814` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e6b-20260814` / `q-local-orchestration-install-05b4b2e6b-20260814` |
| Side context | `scx-local-orchestration-install-05b4b2e6b-20260814-01` |
| Owner / lane | Existing owner2 task and permanent worktree; create only `codex/implementation-codex-target-project-isolation-05b4b2e6b` from the later exact dispatch registry commit. |

Freeze is not dispatch. Exact clean lane/readback, target-branch absence and a
second control commit carrying the dispatch registry are required before edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze / authority | Freeze `1204ed4c90e5195807238114d3df2d52abe3296e`; project-owner standing auto-continue under `PRG-20260809-042`; this control commit is the reviewed dispatch handoff. |
| Exact lane readback | Owner2 task is completed/not loaded and has no active turn; permanent top-level and linked git-dir match; clean E3 handoff `f71cd870fe38779dac83ff175d52d25a19713efa`; tracked/ignored porcelain are empty; exactly three worktrees; target E6B branch is absent. |
| Branch admission | From the exact clean owner2 worktree, create only `codex/implementation-codex-target-project-isolation-05b4b2e6b` at the exact commit carrying this registry. Do not merge/copy a historical branch, create another worktree, reset, rebase, amend, force, stash or alter another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05b4b2e6b_20260814_01`; handoff `hnd_local_orchestration_install_05b4b2e6b_20260814`; allocation `aln_local_orchestration_install_05b4b2e6b_20260814`; receipt `rcpt_local_orchestration_install_05b4b2e6b_20260814`; correlation `corr-local-orchestration-install-05b4b2e6b-20260814`; question `q-local-orchestration-install-05b4b2e6b-20260814`; side context `scx-local-orchestration-install-05b4b2e6b-20260814-01`. |
| Writable return | Exactly the one frozen test path, one implementation commit, then only PRG-368 in one WPR-only handoff commit. |

This one-use receipt authorizes only E6B B1-B8 on the exact owner2 task/worktree.
The owner cannot orchestrate another Agent, issue a review decision, dispatch a
next ticket or perform push/package/install/staging/release/deployment work.
