# 05B4B2E3A — Codex Compensation Port Finite Failure

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 effect boundary |
| State | `IMPLEMENTATION_DISPATCH_CONFIRMED / IMPLEMENT` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E3A-01` / F1-F8 |
| Dependency | Compensation port/composition integrated; E1 integrated by `27c8305200f61d9658aa5b2b32bd15a7db4d0b4c` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Ticket-defect basis

E3 must map every finite oracle block without throwing or claiming removal or
absence success. The integrated five-operation port aliases accept success
values only, while composition intentionally lets ordinary dependency
exceptions propagate. The adapter cannot implement a truthful failure path
until the port algebra has a closed, request-bound failure value.

## One observable outcome

Every admitted compensation operation may return one exact metadata-only
`CodexCompensationPortOperationFailed` bound to the same manifest and named
operation. Composition converts a matching removal failure to declared failure
and a matching list/absence failure to `UNPROVED`; it never converts a failure
into confirmed removal or proved absence.

## Frozen design

- Add `CodexCompensationPortOperation` with exactly `REMOVE_PLUGIN`,
  `REMOVE_MARKETPLACE`, `LIST_PLUGINS`, `LIST_MARKETPLACES` and
  `PROVE_INSTALLED_PATH_ABSENT`; add `CodexCompensationPortFailureReason` with
  exactly `REQUEST_INVALID`, `DEPENDENCY_BLOCKED` and `EVIDENCE_INVALID`.
  One frozen strict `CodexCompensationPortOperationFailed` contains only exact
  manifest, operation, `FAILED` status and reason. It carries no exception,
  message, path, raw oracle state or diagnostic.
- Extend each operation alias only with that failure envelope. Capability
  admission and its no-descriptor/no-execution behavior remain unchanged.
- Composition accepts a failure only when the envelope and recursively retained
  manifest have exact declared original state, the manifest equals the current
  request field by field and the operation matches the invoked step.
- Matching removal failure becomes existing `CodexRemovalFailed`. Matching
  plugin-list failure yields both existing proof truths as `UNPROVED`;
  matching marketplace-list or installed-path failure yields `UNPROVED`.
  Wrong operation, foreign manifest, malformed/subclass/injected state remains
  fail-closed and cannot produce confirmation or `PROVED_ABSENT`.
- This ticket does not catch dependency exceptions and does not implement an
  oracle adapter. E3 must later return this finite value instead of throwing.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `F1` | First red proves the integrated port has no finite operation-failure value and composition cannot reduce one. |
| `F2` | All five exact operation aliases admit their matching failure envelope without changing capability-admission shape or callable count. |
| `F3` | Exact matching removal failures reduce only to declared removal failures and preserve corresponding residual authority. |
| `F4` | Exact matching list/path failures reduce only to `UNPROVED` and never to `MALFORMED`, `CONFIRMED` or `PROVED_ABSENT`. |
| `F5` | Wrong operation/manifest, raw/subclass/container/null, missing/extra/constructed-invalid and injected original state cannot claim success or absence and invoke no caller protocol. |
| `F6` | Failure serialization is metadata-only and contains no callable, exception text, raw diagnostic, absolute path or oracle state. Existing ordinary-exception propagation is unchanged. |
| `F7` | Source adds no `Any`, `type: ignore`, broad catch, optional authority, dynamic lookup/signature or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| `F8` | Reverse operation matching, manifest matching and failure normalization independently. Each named test turns red, exact blobs restore, and focused/full unittest, strict mypy, compile, source/scope/diff/ancestry/topology/residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. `library/local_orchestration/codex_compensation_port.py`
2. `library/local_orchestration/codex_compensation_composition.py`
3. `tests/test_codex_compensation_port.py`
4. `tests/test_codex_compensation_composition.py`

No numeric line limit is an acceptance criterion. Return one implementation
commit over exactly those paths, then one `doc/WorkProgressReport.md`-only
handoff reserved as `PRG-20260813-284`.

No E3 adapter, registration, oracle/environment effect, live Codex,
host/network/target-project, other Agent, review/integration, staging push,
package, release or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E3A-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e3a_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e3a_20260813` / `rcpt_local_orchestration_install_05b4b2e3a_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e3a-20260813` / `q-local-orchestration-install-05b4b2e3a-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e3a-20260813-01` |
| Owner / lane | Existing task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; `workflow-implementer-2`; later create only `codex/implementation-codex-compensation-finite-failure-05b4b2e3a` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `341a58bcfc8b6553db149a56ac005ac9fafec373`; exact F1-F8; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner instruction to continue approved small-ticket work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E3A only |
| Lane readback | Idle task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2` clean at exact submitted HEAD `658f3d7e886d1fd5ddca7bc2c39a8cd887afa4d0`; zero tracked/ignored/cache residue; exactly three worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-compensation-finite-failure-05b4b2e3a` from the exact commit carrying this registry in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e3a_20260813`; `aln_local_orchestration_install_05b4b2e3a_20260813`; `rcpt_local_orchestration_install_05b4b2e3a_20260813`; `corr-local-orchestration-install-05b4b2e3a-20260813`; `q-local-orchestration-install-05b4b2e3a-20260813`; `scx-local-orchestration-install-05b4b2e3a-20260813-01` |

This is the single dispatch. Only the four exact implementation paths and a
later WPR-only `PRG-20260813-284` are writable in this lane.
