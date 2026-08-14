# 05C2A — Codex Compensation Observation Admission

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06 and AC-07 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `01` |
| State | `FROZEN / READY_FOR_LANE_ADMISSION` |
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
  failure admission. Do not change their existing mapping semantics.
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
| `A5` | Extra/private/subclass/constructed malformed response matrices remain finite existing `DECLARED_FAILURE`, `MALFORMED`, `MISMATCH`, `UNPROVED`, residue or absence observations according to the exact operation; no broad clear or `None` port exists. |
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
