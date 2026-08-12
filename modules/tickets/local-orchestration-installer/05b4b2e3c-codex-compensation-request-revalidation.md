# 05B4B2E3C — Codex Compensation Request Revalidation

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `COMPLETED / APPROVED / INTEGRATED` — merge `c042af1` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E3C-01` / Q1-Q6 |
| Dependency | E3A `b324f91` approved/integrated; existing private composition validation is read-only evidence |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Ticket-defect basis

The future E3 effect adapter must reject raw, subclass and recursively
constructed compensation requests before an oracle command. The only complete
recursive validator is currently private to compensation composition. Reusing
it by copy would create two competing admission rules and repeat the constructed
state defects already found in E1/E3B.

## One observable outcome

The compensation port module exposes one pure public exact request revalidator
that returns a recursively rebuilt `CodexCompensationPortRequest` or one closed
metadata-only rejection. It performs no effect and grants no port capability.

The exact public surface is
`revalidate_codex_compensation_port_request(value: object)`, returning either an
exact rebuilt request or `CodexCompensationPortValueRejected`. Its only reason is
`CodexCompensationPortValueRejectReason.INVALID_REQUEST`, and its fixed status is
`INVALID_VALUE`. No mismatch classification is invented without a separately
retained expected manifest.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `Q1` | First red proves the public request revalidator/result algebra is absent. |
| `Q2` | One exact request returns a recursively rebuilt equal request sharing no request, manifest or nested value identity with the caller. |
| `Q3` | Raw/null/container/subclass, missing/extra fields, constructed-invalid request/manifest and injected state on every manifest nested value return the closed rejection without exception. |
| `Q4` | Caller attribute/equality/hash/representation/serialization traps are never invoked before exact type/state admission. The rejection exports only finite status/reason and no manifest, path, diagnostic or exception text. |
| `Q5` | Existing port capability admission and compensation composition behavior remain unchanged; composition may consume the public validator but must not retain a duplicate recursive admission implementation. No callable or effect is added. |
| `Q6` | Reverse exact outer state, one nested state and rebuild identity independently; named tests turn red and exact blobs restore. Focused/full unittest, strict mypy, compile, source/scope/diff/ancestry/topology/residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. `library/local_orchestration/codex_compensation_port.py`.
2. `library/local_orchestration/codex_compensation_composition.py` only if needed to replace its duplicate private admission with the public result.
3. `tests/test_codex_compensation_port.py`.
4. `tests/test_codex_compensation_composition.py` only if path 2 changes.

No numeric line limit is an acceptance criterion. Return one implementation
commit changing only the paths actually needed above, then one
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260813-303`.

No oracle/adapter/environment, live Codex, filesystem/host/network,
target-project, other Agent, review/integration, staging push, package, release
or deployment action is authorized. No `Any`, `type: ignore`, broad catch,
dynamic member lookup, optional/`None` authority or historical-source copy.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E3C-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e3c_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e3c_20260813` / `rcpt_local_orchestration_install_05b4b2e3c_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e3c-20260813` / `q-local-orchestration-install-05b4b2e3c-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e3c-20260813-01` |
| Owner / lane | Existing task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-compensation-request-revalidation-05b4b2e3c` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `d5ff1297be90d223834aded354d9d33b6dbd4b35`; exact Q1-Q6; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved small-ticket work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E3C only |
| Lane readback | Idle task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2` clean at submitted HEAD `b230bbf736b04218f326a3b8617357ee335bbec0`; zero tracked/ignored/cache residue; exactly three worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-compensation-request-revalidation-05b4b2e3c` from the exact commit carrying this registry in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e3c_20260813`; `aln_local_orchestration_install_05b4b2e3c_20260813`; `rcpt_local_orchestration_install_05b4b2e3c_20260813`; `corr-local-orchestration-install-05b4b2e3c-20260813`; `q-local-orchestration-install-05b4b2e3c-20260813`; `scx-local-orchestration-install-05b4b2e3c-20260813-01` |

This is the single dispatch. Only the exact implementation paths actually
needed by Q1-Q6 and the later WPR-only `PRG-20260813-303` are writable.

## Completion

Implementation `32cd6535a3f856a691cea04db34459f3639683a5` and docs-only handoff
`b153636fe2acd37af0b376ee825e0cf9336b98b1` passed independent Q1-Q6 review
at `498394c` and guarded integration at `c042af1`. Post-merge focused 24/24 and
full 395/395 passed. The public pure request revalidator is now the only
recursive request-admission source for later compensation composition/adapter
work.
