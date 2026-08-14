# 05C2A — Codex Compensation Observation Admission

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06 and AC-07 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `02` |
| State | `COMPLETE / APPROVED / INTEGRATED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2A-01` / A1-A8 |
| Dependency | 05C1 and existing compensation port/composition independently approved and integrated |
| Profile / resource | `STANDARD`; one implementation owner, no helper; high reasoning preferred but model identity grants no authority |
| XSS | `XSS_NOT_APPLICABLE`: pure typed Python values; no Browser, WebView, HTML/DOM renderer, JavaScript context or privileged bridge |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

## One observable outcome

Given one exact compensation operation, one exact request and one already
returned value, produce the same strongly typed observation currently used by
the integrated compensation composition. Invalid operation or request identity
returns a finite metadata-only rejection before the returned value is read.

## Frozen public contract

- Extend `codex_compensation_composition.py` with one public pure entrypoint:
  `observe_codex_compensation_operation(operation: object, value: object,
  request: object) -> CodexCompensationObservationResult`.
- Add exact enum `CodexCompensationObservationRejectReason` with only
  `INVALID_OPERATION` and `INVALID_REQUEST`, plus strict frozen Pydantic result
  `CodexCompensationObservationRejected` whose status is
  `OBSERVATION_REJECTED` and whose reason is the enum.
- `CodexCompensationObservationResult` is the union of the existing
  `CodexCompensationObservation` and the new rejection DTO. No `Any`, optional
  port/callable, raw diagnostics or untyped dictionary is part of the contract.
- Admit only exact `CodexCompensationPortOperation`. Revalidate and rebuild the
  request through existing `revalidate_codex_compensation_port_request` before
  inspecting `value`; invalid operation wins over invalid request, which wins
  over any response classification.
- Dispatch the five exact operations to the existing private observation
  normalizers. Do not duplicate, fork or weaken their manifest/identity/list/
  failure admission. Preserve all ordinary validated-response mappings.
  Corrupted original Pydantic state is not an ordinary mapping: an exact-class
  response envelope, list entry or optional marketplace source carrying
  injected `__dict__`, `__pydantic_extra__`, `__pydantic_private__` or
  inconsistent field-set state must not confirm removal or prove absence. The
  shared private normalizers may be hardened only to map that corrupted state
  conservatively to their already-existing finite failure/truth result.
- The entrypoint receives a returned value only. It must not accept, admit,
  resolve or invoke a capability, method, function, descriptor or callable and
  must perform no filesystem, process, Codex, host, target-project or network
  effect.
- Existing `compose_codex_compensation` behavior and public contracts remain
  compatible. Refactoring it to call this entrypoint is optional only if exact
  behavior and all existing tests remain unchanged.

## Acceptance and TDD closure

| ID | Required evidence |
| --- | --- |
| `A1` | First red proves the public entrypoint, rejection DTO/enum/type alias and package exports do not exist; then exact success results for all five operations become green. |
| `A2` | For each operation, success, exact declared failure, foreign/mismatched identity and malformed value produce the same exact observation as the integrated private path; no historical-source copy is used. |
| `A3` | `None`, scalar/string, wrong enum, tuple/list/dict/set, subclass and trap-bearing operation candidates return `INVALID_OPERATION` without request/response member, equality or serialization access. |
| `A4` | Null/scalar/container, subclass, missing/extra/private, constructed-invalid and invalid-nested request matrices return `INVALID_REQUEST`; response traps are untouched. |
| `A5` | Top-level and nested extra/private/injected-field-state, subclass and constructed malformed response matrices remain finite. Corrupted removal proof maps to existing `DECLARED_FAILURE`; corrupted plugin/marketplace list envelope, entry or optional source maps to existing `MALFORMED`; corrupted installed-path proof maps to existing `MALFORMED`. Valid exact responses retain the existing `MISMATCH`, `UNPROVED`, residue or absence observations according to the exact operation; no broad clear or `None` port exists. |
| `A6` | Source inspection and behavior prove zero capability/callable admission or invocation, no `Any`, no `type: ignore`, no broad exception catch and no effect boundary. Existing compensation composition tests remain green. |
| `A7` | Independently reverse the operation dispatch, request-validation precedence and one response identity/mapping guard; each named test turns red, then exact bytes restore. |
| `A8` | Focused and full serial unittest, strict full-tree mypy, in-memory compile, source sentinel, exact diff/scope, tracked/ignored/cache readback and three-worktree topology all pass. |

The CodeReview.md defect classes are closed explicitly: path-prefix and
permission classes are not applicable because this ticket has no path/effect
authority; null-equivalent input, token/identity comparison, finite error
classification, undeclared exception behavior and test-truthfulness are covered
by A2-A8. A discovered requirement change returns typed `CHANGE_DETECTED`; it
must not be silently implemented.

## Exact writable scope and return

Writable implementation paths only:

1. `library/local_orchestration/codex_compensation_composition.py`
2. `tests/test_codex_compensation_composition.py`
3. export-only `library/local_orchestration/__init__.py`

Return one implementation commit changing only these paths, then one
WPR-only handoff commit. No new module, other source/test/document path, live
effect, new worktree, helper Agent, branch fan-out, package/install, push,
release or deployment is authorized. There is no numeric line criterion.

## Planned binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C2A-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c2a_20260814_01` / `hnd_local_orchestration_install_05c2a_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2a_20260814` / `rcpt_local_orchestration_install_05c2a_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2a-20260814` / `q-local-orchestration-install-05c2a-20260814` |
| Side context | `scx-local-orchestration-install-05c2a-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; freeze is not dispatch. |

The reviewer must read back one exact clean existing implementation lane and
record a separate control commit containing its owner, worktree, branch,
baseline and one-use receipt before dispatch.

## Dispatch registry

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS` against exact frozen ticket commit `f72ed955c92ae7790198d3c15e3c2b3c3565c602`: State, Closure, Python 3.11 strict implementation language, `STANDARD` resource profile, `XSS_NOT_APPLICABLE`, exact writable scope and A1-A8 are explicit. |
| Authority / reviewer | Project-owner standing auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation owner | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`. No helper or second owner. |
| Lane readback | Task `notLoaded`/idle; exact top-level and linked git-dir verified; clean branch `codex/implementation-codex-foreign-state-isolation-05b4b2e6a` at released handoff `6f926995e0aa6250e34d095dd08406908c4834a2`; tracked/ignored/cache residue empty; exactly three worktrees; target branch absent. |
| Branch / baseline | In the same permanent worktree create only `codex/implementation-codex-compensation-observation-05c2a` at the exact control commit carrying this registry. Do not merge/copy a historical branch, create a worktree, reset, rebase, amend, force, stash or write another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05c2a_20260814_01`; handoff `hnd_local_orchestration_install_05c2a_20260814`; allocation `aln_local_orchestration_install_05c2a_20260814`; receipt `rcpt_local_orchestration_install_05c2a_20260814`; correlation `corr-local-orchestration-install-05c2a-20260814`; question `q-local-orchestration-install-05c2a-20260814`; side context `scx-local-orchestration-install-05c2a-20260814-01`. |
| Return | One implementation commit changing exactly the three frozen paths, then append only reserved `PRG-20260814-390` in one WPR-only handoff commit. |

This receipt authorizes only A1-A8. The implementation owner must independently
re-read this exact ticket blob and return `HALT / TICKET_SCHEMA_INVALID` before
red tests if any schema identity differs. The owner may not orchestrate another
Agent, self-review/integrate, dispatch a next ticket, push/publish staging,
package/install, release or deploy.

## Revision-02 correction freeze

Independent review of implementation `3b1706889fbc6e5323ce9ba561825f908b4e0dca`
and handoff `9f25ef56892b9b9a9a51e470838a383c0f17e500` opened CR-174.
Revision 01 named extra/private response state in A5 but also said not to change
existing mapping semantics, without distinguishing ordinary validated values
from caller-corrupted Pydantic storage. That ambiguity is a reviewer-owned
`TICKET_DEFECT`; accepting all five corrupted success responses is the bounded
`IMPLEMENTATION_DEFECT`, and the missing direct matrix is an `EVIDENCE_DEFECT`.

The correction remains on the same ticket, owner, permanent worktree, branch,
allocation, receipt and correlation. It may change only
`codex_compensation_composition.py` and its direct test; package exports are
already correct and must remain byte-identical. Add bounded table-driven tests
for top-level response extra/private state and representative nested plugin and
marketplace entry/source injected state. Independently reverse the shared
original-state guard and require the named CR-174 test to turn red, then restore
exact bytes. Preserve operation/request precedence and every ordinary A1-A7
result. Return one additive correction commit and reserved PRG-20260814-393 in
one WPR-only handoff commit after the complete A8 matrix.

## Revision-02 correction dispatch registry

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS` against exact refreeze/finding commit `e7738ba11310379437be5598ed68b2181c20eb71`: revision 02 State, Closure A1-A8, Python 3.11 strict implementation language, `STANDARD` one-owner/no-helper profile, `XSS_NOT_APPLICABLE`, exact two-path correction scope and CR-174 outcome are explicit. |
| Authority / reviewer | Project-owner standing auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation lane | Existing owner task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; same branch `codex/implementation-codex-compensation-observation-05c2a`; clean handoff `9f25ef56892b9b9a9a51e470838a383c0f17e500`; exactly three worktrees and zero tracked/ignored/cache residue. |
| Merge admission | Merge only the exact control commit carrying this registry. Read-only merge-tree proves the only overlap is append-only `doc/WorkProgressReport.md`; preserve PRG-390 through PRG-392 exactly once. Any other conflict, changed implementation blob, dirty lane or topology drift is typed `HALT`. |
| Binding | Retain workspace `wsb_local_orchestration_install_05c2a_20260814_01`, handoff `hnd_local_orchestration_install_05c2a_20260814`, allocation `aln_local_orchestration_install_05c2a_20260814`, receipt `rcpt_local_orchestration_install_05c2a_20260814`, correlation `corr-local-orchestration-install-05c2a-20260814`, question and side context. |
| Correction / return | Change only composition source and its direct test; preserve export blob from implementation `3b1706889fbc6e5323ce9ba561825f908b4e0dca`; one additive correction commit followed by unique PRG-393 WPR-only handoff. |

This registry does not authorize a new branch, worktree, owner, helper, public
contract, effect, package/install, push, release or deployment.

## Revision-02 final review

CR-174 is closed by correction `5082cf9d34f3d555b12a2d34d9f21fff317e4568`
and WPR-only handoff `7ba15c9d5513d08d2d2f1ef23e4ca06d164d3525`.
Independent immutable-snapshot review passed focused `18/18`, full serial
`483/483`, strict mypy and compile over `146` files, an additional 12-cell
original-state/optional-field matrix, and a shared-guard reversal that failed
all 16 committed CR-174 cells before exact restoration. A1-A8 are approved;
guarded integration remains reviewer-owned.

## Guarded integration

Review `5e7e489b62174ef10b16358e938a065e10f39fa8` and exact handoff
`7ba15c9d5513d08d2d2f1ef23e4ca06d164d3525` were guarded-merged as
`e2e2fe986243fa64f7ce9a67903904310341597b`. The only conflict was the
predicted append-only WPR overlap; PRG-390 through PRG-394 remain exactly once.
Post-merge focused `18/18` and strict mypy over `146` files pass with the
external cache removed. This ticket is complete and releases 05C2B for exact
refreeze; it creates no authority to package, install, push or deploy.
