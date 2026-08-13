# 05B4B2E3D — Codex Oracle Compensation Response Admission

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 |
| State | `FROZEN / READY_FOR_DISPATCH / REVISION_02` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E3D-01` / P1-P8 |
| Dependency | E2 merge `d3d3c1d`, E3A `b324f91`, E3B `dc07eec` and E3C `c042af1` approved/integrated |
| Planned owner | Local project `3a624854-bf2f-4aa8-9b04-5f73e9ab2a28`; task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent worktree `wtr_workflow_implementer_2_20260813_01` |
| Control / reviewer | Current control task is both ticket author and independent reviewer; it must not implement source/tests |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

One pure staging boundary receives an expected compensation `OracleAction` and
one untrusted `OracleRunResult`, then returns exactly one recursively rebuilt
typed protocol response, one typed installed-path absence, or one metadata-only
finite rejection. The future E3 effect adapter can consume this boundary without
copying response validators or manufacturing success from a block, wrong surface,
constructed value or caller-provided payload.

## Frozen design

- Add only `tests/staging/codex_lifecycle_oracle/response_admission.py` and
  `tests/test_codex_oracle_response_admission.py`.
- The public function accepts `object` plus an exact `OracleAction`; it returns a
  closed union of accepted protocol response, accepted absence, or rejected
  metadata. No `None`, raw mapping, exception text, caller callable, path,
  command, diagnostic or dynamic member lookup crosses the boundary.
- Supported protocol actions are `PLUGIN_REMOVE`, `MARKETPLACE_REMOVE`,
  `PLUGIN_LIST` and `MARKETPLACE_LIST`. Exact `OracleAbsent` is accepted only
  for `ABSENCE`. Every other action/result combination is finite rejection.
- An accepted protocol value must be rebuilt from exact built-in state at every
  Pydantic node. Subclasses, missing/extra fields, constructed or injected
  nested values, wrong surface/payload pairs and caller-controlled property,
  equality, hash, repr or serialization execution reject before any value is
  exposed.
- Exact `OracleBlocked` maps to one finite dependency-blocked reason without
  retaining its raw reason. Wrong result type, malformed state and
  action/surface mismatch remain separately finite so E3 can map them to its
  existing `DEPENDENCY_BLOCKED` or `EVIDENCE_INVALID` values without guessing.
- This ticket is pure projection only. It may not call `CodexLifecycleOracle`,
  inspect a lease, allocate/delete files, mutate state, import E2's private
  helpers, build the E3 port, or perform removal/list/absence effects.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `P1` | First red is the missing response-admission module. The implementation commit changes exactly the two frozen paths. |
| `P2` | Non-`OracleAction`, unsupported action, non-run-result, subclass and constructed/extra top-level values return one finite invalid/malformed rejection without exception or caller protocol execution. |
| `P3` | Exact `PLUGIN_REMOVE` plus exact matching `CodexPluginRemove` is rebuilt and accepted; wrong surface, wrong payload, missing/extra/injected field and malformed nested value reject. |
| `P4` | Exact `MARKETPLACE_REMOVE` plus exact matching `CodexMarketplaceRemove` is rebuilt and accepted; the same finite negative matrix rejects. |
| `P5` | Exact `PLUGIN_LIST` recursively rebuilds installed/available entries, optional marketplace source and primitive fields; duplicate/foreign entries remain data, while subclasses and malformed/constructed nodes reject. |
| `P6` | Exact `MARKETPLACE_LIST` recursively rebuilds entries and optional marketplace source; subclasses and malformed/constructed nodes reject. |
| `P7` | Exact `OracleAbsent` is accepted only for `ABSENCE`; absence under another action and completed response under `ABSENCE` reject. Exact `OracleBlocked` always returns metadata-only dependency-blocked evidence and never leaks its reason. |
| `P8` | Independently reverse action/surface matching, one recursive exact-state guard and the absence gate. Each named test turns red and exact blobs restore; focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix class: not applicable; no path comparison is introduced. Source
  scan must confirm no path, filesystem or locator authority enters this module.
- Authority-bypass class: the boundary is pure and exposes no effect capability;
  unsupported/wrong action cannot obtain an accepted response.
- Exception/error class: every named invalid shape and exact `OracleBlocked`
  returns a finite value; no raw reason or exception text is retained.
- Test-truth class: P3, P5 and P7 each have a named reversal in P8.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, renderer, DOM, JavaScript or
  privileged bridge exists.
- Task/worktree class: product task root, filesystem identity and linked Git
  worktree metadata must match the permanent owner worktree before dispatch.

## Exact source, return and boundary

Return one exact two-path implementation commit, then one unique
`doc/WorkProgressReport.md`-only handoff. No numeric line limit is an acceptance
criterion. No E3 effect adapter, E4-E6, live Codex, environment mutation,
filesystem/network/target-project effect, Agent control, staging push, package,
release or deployment is authorized.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed ticket / handoff | Ticket freeze `4c70988596e783a5e73199ec8327230e29f685c7`; reviewed handoff is the control commit carrying this registry. |
| Delivery authority | Project-owner standing instruction to resume and continue the approved automated workflow; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E3D only. |
| Product binding | Project `3a624854-bf2f-4aa8-9b04-5f73e9ab2a28`; task `019ffb0c-db88-7303-895c-aecfadde7c8d`; workspace `wsb_local_orchestration_install_05b4b2e3d_20260813_01`; worktree `wtr_workflow_implementer_2_20260813_01`; readback digest `979cf788a0150f4a9cee82ea5f3c0e53a8d552c8be871f55d0aa70f19d9ff85b`. |
| Binding | `hnd_local_orchestration_install_05b4b2e3d_r01_20260813`; `aln_local_orchestration_install_05b4b2e3d_r01_20260813`; `rcpt_local_orchestration_install_05b4b2e3d_r01_20260813`; `corr-local-orchestration-install-05b4b2e3d-r01-20260813`; `q-local-orchestration-install-05b4b2e3d-r01-20260813`; `scx-local-orchestration-install-05b4b2e3d-r01-20260813-01`. |
| Branch | Create only `codex/implementation-codex-oracle-response-admission-05b4b2e3d` from the exact registry commit in the same permanent worktree; no new worktree. |
| Writable paths | The two frozen implementation paths, followed by a unique `PRG-20260813-317` WPR-only handoff. |

This is the single E3D dispatch. The receipt is one-use and cannot authorize E3,
another ticket, another owner or another task.

## Halt record

| Field | Value |
| --- | --- |
| Typed result | `HALT / SCOPE_VIOLATION`; no implementation commit or WPR handoff exists. |
| Violation | During full-suite diagnosis, the implementation owner deleted one pre-existing `%TEMP%/johnny-stage-env-*` test-residue directory before the reviewer steer arrived. The directory had an environment owner marker and was not a target-project or worktree path, but cleanup of pre-existing host residue was outside this pure-projection ticket. |
| Preserved lane | Branch remains at registry `472201b1f82416d0fc00ec03582d0175f9f97048`; only the two frozen files plus generated `__pycache__` directories are untracked. No tracked/source/docs commit exists. |
| Evidence before halt | First red was missing module; focused `10/10`, focused strict mypy and compile passed. Host full suite ran `419` tests and failed the two existing residue assertions before the out-of-scope cleanup. |
| Continuation | Receipt is suspended. Reviewer must not accept, commit, clean, reset or redispatch this lane without a project-owner disposition that explicitly covers the preserved uncommitted work and the host-residue incident. |

## Requirement-change disposition

`CHG-20260813-015` replaces the globally shared OS-TEMP 05S1 root with the
project-owned `tests/.johnny-runtime/` namespace. This ticket cannot resume or
use its old full-suite evidence until 05S1R is independently approved and
integrated, then E3D is refrozen against that baseline. The two uncommitted
implementation paths and generated cache residue remain preserved; this record
does not authorize their deletion, commit, cleanup or reuse.

## Revision-02 baseline refreeze and dispatch registry

Project-owner continuation authority resolves the prior owner-disposition halt.
05S1R/05S1R1 are approved and integrated by `d399364`; the preserved two-path
same-lane WIP is therefore admitted for additive completion. It is not a
historical implementation source and may not be copied to another branch or
worktree.

| Field | Value |
| --- | --- |
| Reviewed authority | This control commit is the reviewed handoff; foundation merge `d399364`; completion record `2c8376f`; unchanged closure P1-P8. |
| Product binding | Project `3a624854-bf2f-4aa8-9b04-5f73e9ab2a28`; task `019ffb0c-db88-7303-895c-aecfadde7c8d`; workspace `wsb_local_orchestration_install_05b4b2e3d_20260814_02`; worktree `wtr_workflow_implementer_2_20260813_01`; readback digest `f830fb9af17a5c68a8174e0041a458c6f39a46654bdaa5337afbde222ed4e84f`. |
| Binding | `hnd_local_orchestration_install_05b4b2e3d_r02_20260814`; `aln_local_orchestration_install_05b4b2e3d_r02_20260814`; `rcpt_local_orchestration_install_05b4b2e3d_r02_20260814`; `corr-local-orchestration-install-05b4b2e3d-r02-20260814`; `q-local-orchestration-install-05b4b2e3d-r02-20260814`; `scx-local-orchestration-install-05b4b2e3d-r02-20260814-01`. |
| Preserved blobs | `response_admission.py` SHA-256 `a87dfd78ef2d1cdc782033fce016db3104943f6b52fe52e5214f207fee385a40`; focused test SHA-256 `db17a9d01e14ecbd1a1f0e73da8aaf76cb31201464ffde3194bc168d57ba1a79`. |
| Baseline admission | On the existing E3D branch, verify both hashes, fast-forward the exact control registry commit while preserving both blobs, then verify both hashes again. Any mismatch is typed `HALT`; no reset, stash, rebase, copy or new branch/worktree. |
| Cleanup authority | Remove only the two exact generated untracked `__pycache__` directories already listed in the halt readback, inside the bound worktree. Never inspect, enumerate or delete OS-global TEMP/staging residue. |
| Writable paths | The original two frozen implementation paths, followed by unique `PRG-20260814-337` WPR-only handoff. |

The new receipt is one-use and replaces the suspended revision-01 receipt. Full
verification must use the project-owned runtime; no host-global cleanup may be
used to manufacture a green result.
