# 05B4B2E5 — Codex Registration Compensation Acceptance

| Field | Value |
| --- | --- |
| Revision | `02` - non-high-risk ticket correction; implementation scope unchanged |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E5-01` / C1-C8 (revision-02 wording correction; acceptance items unchanged) |
| Dependency | E2 merge `d3d3c1d`, E3 merge `1517b03` and E4 merge `c1a5a7c` approved/integrated |
| Planned owner | Task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent `workflow-implementation`; no new worktree/helper |
| Profile / XSS | `STANDARD`; one implementation owner / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

Prove one real rollback lane only: in one fresh project-owned 05S1 lease, run
the existing E2 registration path through marketplace add, execute the real
plugin add once, replace only that one returned plugin-add response with one
declared started failure, consume the resulting exact compensation claim
through integrated E3, and prove complete owned absence. Foreign-state and
target-project isolation remain exclusively E6.

## Frozen design

- Add only `tests/test_codex_registration_compensation_acceptance.py`. This is
  an evidence-only acceptance ticket; it adds no new product/library/staging
  behavior or public entry point.
- The parent test creates one unique child TEMP and one fresh 05S1 lease, fixes
  the child logical `LOCALAPPDATA` to the integrated oracle root, initializes one
  exact `CodexLifecycleOracle`, and uses the integrated E1/E2 registration
  binding, port, forward coordinator and settlement authority.
- At the exact plugin-add transition, one class-level test wrapper calls the
  original oracle method exactly once so owned plugin state and payload are
  genuinely created, records the exact completed result, then substitutes only
  that returned value with `OracleBlocked(PROCESS_FAILED)` for E2. The same
  wrapper may remain installed as a passive action observer through E3 and as a
  replay-effect trap, but it must delegate every non-faulted oracle call to the
  exact original method. No earlier transition or compensation operation is
  replaced, fabricated or short-circuited.
- The started failure must yield one exact live
  `CodexRegistrationCompensationClaim`, never a receipt. The same lease, oracle
  and manifest-bound E3 adapter are passed to
  `settle_codex_registration_compensation`. Because the E3 factory requires its
  bound `CodexCompensationPortRequest` before settlement while settlement keeps
  the claim-owned projection private, this evidence-only fixture may perform
  one typed field-for-field projection from its admitted registration request
  into that adapter request. The projection may only bind the integrated E3
  adapter; it may not plan compensation, validate an outcome or response, or
  replace the request later supplied by settlement. The E3 adapter's integrated
  exact-request admission remains the proof that both projections match.
- Successful settlement must execute only this order after the failure:
  `PLUGIN_REMOVE -> MARKETPLACE_REMOVE -> PLUGIN_LIST -> MARKETPLACE_LIST ->
  ABSENCE`, return exact `CodexCompensated` with no reasons or unresolved
  authority, retain an empty owned oracle state, and leave the exact physical
  plugin payload plus logical installed path absent.
- Replaying the consumed claim must return the integrated finite claim block
  before any oracle action; state bytes and payload absence must remain
  unchanged. The test finally tears down only its exact lease and unique child
  TEMP and proves parent environment preservation.
- No global TEMP/staging scan, sibling-worktree inspection, foreign-state seed,
  target-project read/write, live Codex, host/network effect or package/install
  behavior belongs to this ticket.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `C1` | First red is missing `tests.test_codex_registration_compensation_acceptance`; the implementation commit adds exactly that one path. |
| `C2` | Exact lease/oracle/request admits the integrated E1/E2 chain and E3 adapter on the same identity. The one permitted typed fixture projection only supplies the E3 factory's required pre-settlement request; their already integrated negative admission matrices are not duplicated here. |
| `C3` | Registration actions are exactly `VERSION -> MARKETPLACE_ADD -> PLUGIN_ADD`. The one-shot plugin fault calls original `PLUGIN_ADD` once, proves the owned record/payload existed, then returns only declared `PROCESS_FAILED`; the authority emits one compensation claim and no receipt. |
| `C4` | Claim settlement invokes exact E3 action order `PLUGIN_REMOVE -> MARKETPLACE_REMOVE -> PLUGIN_LIST -> MARKETPLACE_LIST -> ABSENCE`, each exactly once, with the same lease/oracle/manifest identity. The passive wrapper observes these calls while delegating each one to the original oracle method. |
| `C5` | Result is exact `CodexCompensated`, reasons are empty and residual authority is empty. Empty plugin and marketplace lists plus admitted logical absence are part of the integrated reduction, not separately fabricated evidence. |
| `C6` | Persisted owned oracle state has no marketplace/plugin record and the exact lease-derived physical plugin payload is absent before teardown. The test scans no global or sibling root. |
| `C7` | Replaying the consumed exact claim cannot execute an oracle action or change state/payload bytes. Exact lease teardown and unique child-TEMP removal succeed; parent environment bytes are unchanged. |
| `C8` | Independently reverse the one-shot fault, compensation action order, claim replay gate and physical-payload absence assertion. Each named test turns red and exact bytes restore; focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix: only exact locators derived from the admitted lease and identity;
  no prefix-similar, parent, sibling or global cleanup target may pass.
- Authority: the exact live compensation claim may reach E3 once; its replay is
  blocked before effect. Dependency-owned fabricated/foreign matrices are not
  copied into this acceptance ticket.
- Error/exception: the injected fault is a finite declared oracle result; no
  raw exception, path, response or claim escapes the acceptance assertion.
- Test truth: the test must prove the real plugin side effect existed before
  rollback and prove both logical and physical absence afterward.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, HTML/DOM renderer, JavaScript
  context or privileged bridge exists.
- Task/worktree: owner task root, linked git-dir, branch, HEAD and clean
  tracked/ignored porcelain must match the dispatch registry before editing.

## Exact source and return

Writable implementation path only:

1. `tests/test_codex_registration_compensation_acceptance.py`

Return one implementation commit for that path, then one unique
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260814-355`. No
numeric line limit is an acceptance criterion.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f` / `CLOSURE-LOCAL-INSTALL-T05B4B2E5-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05b4b2e5_20260814_01` / `hnd_local_orchestration_install_05b4b2e5_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e5_20260814` / `rcpt_local_orchestration_install_05b4b2e5_20260814` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e5-20260814` / `q-local-orchestration-install-05b4b2e5-20260814` |
| Side context | `scx-local-orchestration-install-05b4b2e5-20260814-01` |
| Owner / lane | Existing owner1 task and permanent worktree; create only `codex/implementation-codex-registration-compensation-acceptance-05b4b2e5` from the later exact dispatch registry commit. |

Freeze is not dispatch. Exact clean lane/readback, target-branch absence and a
second control commit carrying the dispatch registry are required before the
owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze / authority | Freeze `d1ffe1697001ee123bd60e311a89efed23eefb07`; project-owner standing auto-continue under `PRG-20260809-042`; this control commit is the reviewed dispatch handoff. |
| Exact lane readback | Owner1 top-level `C:/Users/<user>/Desktop/AI控制工作workflow-implementation` and linked git-dir match; task is idle; clean branch `codex/implementation-codex-registration-success-acceptance-05b4b2e4` at `63b84949b2a9c7dd27872a6c0f56aa02207ed65b`; tracked/ignored counts are zero; exactly three worktrees; target E5 branch is absent. |
| Branch admission | From the clean owner1 worktree, create only `codex/implementation-codex-registration-compensation-acceptance-05b4b2e5` at the exact commit carrying this registry. Do not merge/copy/reuse E4 source as a baseline, create another worktree or alter another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05b4b2e5_20260814_01`; handoff `hnd_local_orchestration_install_05b4b2e5_20260814`; allocation `aln_local_orchestration_install_05b4b2e5_20260814`; receipt `rcpt_local_orchestration_install_05b4b2e5_20260814`; correlation `corr-local-orchestration-install-05b4b2e5-20260814`; question `q-local-orchestration-install-05b4b2e5-20260814`; side context `scx-local-orchestration-install-05b4b2e5-20260814-01`. |
| Writable return | Exactly the one frozen test path, one implementation commit, then only PRG-355 in one WPR-only handoff commit. |

This one-use receipt authorizes only E5 C1-C8 on the exact owner1 task/worktree.
The owner cannot orchestrate another Agent, issue a review decision, dispatch a
next ticket or perform push/package/install/staging/release/deployment work.

## Revision-02 correction record

The terminal reviewer found two mutually incompatible revision-01 statements:
the E3 factory requires a compensation request before settlement but the ticket
forbade the only typed fixture projection available through public APIs, and the
ticket required exact compensation action observation while also requiring the
observer to be removed before compensation. Revision 02 resolves only those
ticket defects. It does not change C1-C8, the one-file implementation scope,
the owner, branch, allocation, receipt, correlation or product behavior. The
immutable implementation `2bf7dd842f2bef0c55a0448c282189f3067d33fc` already
matches the corrected design and may proceed directly to independent terminal
review without an implementation rewrite.
