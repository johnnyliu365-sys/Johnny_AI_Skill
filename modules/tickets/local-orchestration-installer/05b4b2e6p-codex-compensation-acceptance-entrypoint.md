# 05B4B2E6P - Codex Compensation Acceptance Entrypoint

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E6P-01` / P1-P8 |
| Dependency | E5 guarded merge `ce7a1c2e63feb7ec7eff8b3201a23fa25c7dc16d` |
| Planned owner | Existing owner1 task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent `workflow-implementation`; no new worktree/helper |
| Profile / XSS | `STANDARD`; one implementation owner / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

Extract only the already accepted integrated E5 compensation flow into one
reusable staging-only typed function so E6A/E6B can seed and inspect the same
lease/oracle around it. This is a refactor of accepted evidence, not new product
behavior and not a second compensation implementation.

## Frozen design

- Add `tests/staging/codex_lifecycle_oracle/registration_compensation_acceptance.py`.
  It exposes one exact `run_registration_compensation_acceptance(lease, oracle,
  request)` entrypoint and closed accepted/rejected result types.
- Update only `tests/test_codex_registration_compensation_acceptance.py` to use
  that entrypoint while preserving the integrated E5 disposable-child proof,
  action order, physical/logical absence, replay-zero-effect and teardown tests.
- Move the existing E5 transaction behavior; do not copy it. The staging
  entrypoint allocates no environment/TEMP, launches no child, inspects no
  global/sibling path and performs no teardown. Its caller owns lifecycle.
- Exact `EnvironmentLease`, exact `CodexLifecycleOracle` and rebuilt
  `CodexRegistrationPortRequest` are required before any oracle call. `None`,
  subclasses, constructed-invalid and mismatched identities return a finite
  typed rejection before effect.
- The entrypoint uses integrated E1/E2/E3 only: original plugin add executes
  once, only its result is substituted with `PROCESS_FAILED`, the exact live
  claim settles once, and replay is blocked before effect. No fake port,
  duplicated reducer/plan/response validator or historical source is allowed.
- The revision-02 field-for-field adapter-request projection is permitted only
  to bind the E3 factory and must match settlement's supplied request through
  integrated E3 admission. Accepted metadata contains only finite phases and
  boolean absence/replay facts; no raw path, command, claim, oracle state or
  exception escapes.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `P1` | First red is the missing staging entrypoint import; implementation changes exactly the two frozen paths. |
| `P2` | Exact lease/oracle/request returns exact accepted type; invalid, subclass, constructed-invalid and identity-mismatched inputs return declared rejected reasons before any oracle action. |
| `P3` | The entrypoint delegates to integrated E1/E2/E3 and observes exact order `VERSION -> MARKETPLACE_ADD -> PLUGIN_ADD -> PLUGIN_REMOVE -> MARKETPLACE_REMOVE -> PLUGIN_LIST -> MARKETPLACE_LIST -> ABSENCE`. |
| `P4` | Original plugin add executes exactly once and owned record/payload genuinely exist before only its returned value becomes `PROCESS_FAILED`; no other action is substituted. |
| `P5` | Exact live claim settles to `CodexCompensated` with empty reasons/authority; owned logical state and exact physical payload are absent. |
| `P6` | Consumed-claim replay performs zero oracle calls and cannot change state bytes or payload absence. No claim, effect port, command, raw path or exception escapes the typed result. |
| `P7` | Existing E5 parent/child TEMP preservation and exact lease teardown remain green; the entrypoint itself owns no allocation, child process or cleanup. E6A/E6B behavior is not implemented here. |
| `P8` | Reverse invalid-before-effect, one-shot fault, action order, physical absence and replay gates; each turns red and exact bytes restore. Focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix: only exact paths derived from the admitted lease/identity; no
  prefix, sibling, target-project or global cleanup target.
- Authority: one live claim may settle once; replay blocks before any effect.
- Error/exception: closed result union and enum reasons only; no broad catch,
  raw exception, command, response, claim or path in outward metadata.
- Test truth: E5's real disposable child remains the behavior proof; extraction
  must not replace it with mocks or copy its assertions into a weaker fixture.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, HTML/DOM renderer, JavaScript
  context or privileged bridge exists.

## Exact source and return

Writable implementation paths only:

1. `tests/staging/codex_lifecycle_oracle/registration_compensation_acceptance.py`
2. `tests/test_codex_registration_compensation_acceptance.py`

Return one implementation commit for those paths, then one unique
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260814-361`. No
numeric line limit is an acceptance criterion.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f` / `CLOSURE-LOCAL-INSTALL-T05B4B2E6P-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05b4b2e6p_20260814_01` / `hnd_local_orchestration_install_05b4b2e6p_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e6p_20260814` / `rcpt_local_orchestration_install_05b4b2e6p_20260814` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e6p-20260814` / `q-local-orchestration-install-05b4b2e6p-20260814` |
| Side context | `scx-local-orchestration-install-05b4b2e6p-20260814-01` |
| Owner / lane | Existing owner1 task and permanent worktree; create only `codex/implementation-codex-compensation-acceptance-entrypoint-05b4b2e6p` from the later exact dispatch registry commit. |

Freeze is not dispatch. Exact clean lane/readback, target-branch absence and a
second control commit carrying the dispatch registry are required before edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze / authority | Freeze `8312eae827d5643d2a74905088d2922580de8d82`; project-owner standing auto-continue under `PRG-20260809-042`; this control commit is the reviewed dispatch handoff. |
| Exact lane readback | Owner1 task is idle; permanent top-level and linked git-dir match; clean E5 branch at exact handoff `5dd0f635bbdcc29ba0aa74d63ad849d2fe4158e4`; tracked/ignored counts are zero; exactly three worktrees; target E6P branch is absent. |
| Branch admission | From the exact clean owner1 worktree, create only `codex/implementation-codex-compensation-acceptance-entrypoint-05b4b2e6p` at the exact commit carrying this registry. Do not merge/copy a historical branch, create another worktree, reset, rebase, amend, force, stash or alter another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05b4b2e6p_20260814_01`; handoff `hnd_local_orchestration_install_05b4b2e6p_20260814`; allocation `aln_local_orchestration_install_05b4b2e6p_20260814`; receipt `rcpt_local_orchestration_install_05b4b2e6p_20260814`; correlation `corr-local-orchestration-install-05b4b2e6p-20260814`; question `q-local-orchestration-install-05b4b2e6p-20260814`; side context `scx-local-orchestration-install-05b4b2e6p-20260814-01`. |
| Writable return | Exactly the two frozen source/test paths, one implementation commit, then only PRG-361 in one WPR-only handoff commit. |

This one-use receipt authorizes only E6P P1-P8 on the exact owner1 task/worktree.
The owner cannot orchestrate another Agent, issue a review decision, dispatch a
next ticket or perform push/package/install/staging/release/deployment work.
