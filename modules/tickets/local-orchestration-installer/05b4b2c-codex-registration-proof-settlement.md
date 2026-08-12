# 05B4B2C — Codex Registration Proof Settlement

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 proof/receipt seam |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2C-01` / P1-P8 |
| Dependency | 05B4B2B1 approved and integrated by `0c4476f8d40b53292ea69d0daec084860beeaa03` |
| Planned owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; one new ticket branch in that same worktree, no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

Settle one exact live B2B1 proof claim through one freshly admitted integrated
registration port. Admission must finish before the claim is consumed. The
claim is then consumed inside the single effect entry, its rebuilt proof
request is passed once to the admitted `prove` operation through the existing
`issue_registration_receipt` validator, and the function returns only the
existing metadata-only receipt or finite registration rejection.

## Frozen design

- Add one public `settle_codex_registration_proof(claim: object,
  port_candidate: object)` entry. It first calls the integrated
  `admit_codex_registration_port`; invalid/null/container/trap candidates return
  a finite existing `INVALID_PROOF_PORT` rejection with the claim still live and
  zero caller operations.
- Only an exact newly admitted `CodexRegistrationPortCapability` may continue.
  The settlement must not call or expose its fresh-preflight, marketplace-add
  or plugin-add operations.
- The entry next calls the integrated B2B1 proof-claim consumer exactly once.
  Invalid, wrong-kind, foreign, altered or replayed values return the existing
  `CodexRegistrationSettlementClaimBlocked` and invoke no proof operation.
- An exact consumed `CodexRegistrationProofRequired` supplies the only proof
  request. Pass that request and the freshly admitted capability to the
  integrated `issue_registration_receipt`; do not duplicate, weaken or bypass
  its recursive request/proof matching.
- A valid proof returns the existing `CodexRegistrationReceipt`. Declared
  `CodexRegistrationProofPortFailure`, malformed proof and every field mismatch
  retain the existing finite rejection. RuntimeError, MemoryError,
  KeyboardInterrupt and SystemExit outside that declared exception propagate;
  because consumption precedes the call, replay remains blocked and the proof
  effect cannot be retried through the same claim.
- The entry owns no registry, clear/retry path, raw diagnostics, absolute-path
  output or durable state. It does not touch the lifecycle oracle.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `P1` | First red imports absent `codex_registration_proof_settlement` and fails with exact `ModuleNotFoundError`; production remains absent during red. |
| `P2` | Exact port admission performs zero operations. Invalid/null/container/property/descriptor/shape/trap candidates return finite `INVALID_PROOF_PORT`, leave the exact claim usable, and invoke no caller protocol. |
| `P3` | Invalid, wrong-kind, foreign, altered, metadata-only, fabricated and replayed claims return exact `INVALID_CLAIM` with zero proof calls. One exact live proof claim is consumed once inside settlement. |
| `P4` | A valid exact claim calls only `prove`, exactly once, with the rebuilt claim-owned proof request and returns the existing metadata-only `CodexRegistrationReceipt`; all other registration operations remain zero-call. |
| `P5` | Declared proof failure, malformed proof and every receipt-bound mismatch preserve the existing finite rejection reasons and never leak raw output, exception text or absolute observed paths. |
| `P6` | RuntimeError, MemoryError, KeyboardInterrupt and SystemExit propagate unchanged after exactly one proof call; replay of the consumed claim is blocked with zero additional calls. Synchronized duplicate settlement yields one proof call and one claim block. |
| `P7` | Source performs no add, compensation, oracle, process, filesystem, host, network or target-project effect and adds no `Any`, `type: ignore`, broad catch, optional/`None` port, dynamic lookup/signature or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| `P8` | Independently reverse admission-before-consumption, exact claim consumption, proof-only dispatch, integrated receipt validation and consume-before-effect/replay. Each named committed test turns red and exact blobs restore; focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology and residue checks pass. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_proof_settlement.py`.
2. New `tests/test_codex_registration_proof_settlement.py`.

All integrated source/tests and package exports remain read-only. No numeric
line limit is an acceptance criterion. Return one exact two-path implementation
commit, then one `doc/WorkProgressReport.md`-only handoff reserved as
`PRG-20260812-252`.

No B2B2/B2D/B2E/05C work, live Codex, process, filesystem, host, network,
target-project mutation, other Agent, review, integration, push, release or
deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2C-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2c_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2c_20260812` / `rcpt_local_orchestration_install_05b4b2c_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b2c-20260812` / `q-local-orchestration-install-05b4b2c-20260812` |
| Side context | `scx-local-orchestration-install-05b4b2c-20260812-01` |
| Owner / lane | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; later create only `codex/implementation-codex-registration-proof-settlement-05b4b2c` from the exact dispatch commit. |

Freeze is not dispatch. A later dispatch registry must bind the exact freeze
commit and verified clean lane before implementation starts.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `2183afb3956744163c22cb16f1c2285d0aa82de8`; exact P1-P8; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for this ticket only |
| Lane readback | Task is idle; existing `workflow-implementation` is clean at exact submitted HEAD `0378655864e4277d553558a40d5122702aa3d7d9`; exactly three existing worktrees |
| Branch | Create only `codex/implementation-codex-registration-proof-settlement-05b4b2c` from this exact dispatch-registry commit in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2c_20260812`; `aln_local_orchestration_install_05b4b2c_20260812`; `rcpt_local_orchestration_install_05b4b2c_20260812`; `corr-local-orchestration-install-05b4b2c-20260812`; `q-local-orchestration-install-05b4b2c-20260812`; `scx-local-orchestration-install-05b4b2c-20260812-01` |

This is the single dispatch. Only the exact two implementation paths and later
WPR-only PRG-20260812-252 are writable in this lane.

## Review decision

Terminal independent review of implementation `c27924f9cfe352bd88cb7ae9d28e244e72784547`
and WPR-only handoff `09467cd8b8a9f652648e8383750fa36d190a41fd`
is `APPROVED / READY_TO_MERGE` under P1-P8.
