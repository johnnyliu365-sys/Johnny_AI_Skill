# 05B4B2D — Codex Registration Compensation Settlement

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 compensation seam |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2D-01` / S1-S9 |
| Dependency | 05B4B2B2 integrated by `e7cd37b5abde7b9c693315e38fcd73dc0a001dc2` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; one new ticket branch in that same worktree, no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

Admit one compensation port without executing it, then consume exactly one
B2B1 compensation claim. Derive the complete compensation request and plan only
from the claim-owned B2B2 terminal decision or started-add recovery, execute
the existing exhaustive compensation composition once, and return only its
existing finite algebra or existing finite admission/claim rejection.

## Frozen design

- Add one public `settle_codex_registration_compensation(claim: object,
  port_candidate: object)` entry. It must safely call
  `admit_codex_compensation_port` before consuming the claim. Invalid/null/
  container/descriptor/trap candidates return the existing finite port
  rejection, perform zero operations and leave the exact claim live.
- Then call `consume_codex_registration_compensation_claim` exactly once.
  Invalid, raw DTO, wrong-kind, foreign, altered, fabricated, metadata-only or
  replayed values return the existing finite claim block and perform no
  compensation operation.
- For exact `CodexRegistrationCompensationRequired`, build the
  `CodexCompensationPortManifest` only from its claim-owned `request`: preflight
  installation/root/marketplace/source/plugin plus expected plugin ID/version,
  installed locator, auth policy and digest. Use its claim-owned plan; accept no
  caller manifest, raw terminal DTO or replacement field.
- For exact `CodexRegistrationAddRecovery`, build the same manifest only from
  its claim-owned request and derive the only legal plan from its claim-owned
  journal/request/attempt through `build_compensation_plan`. A non-required or
  invalid plan finite-fails before an operation.
- Pass one exact new `CodexCompensationPortRequest`, admitted capability and
  claim-owned/rebuilt plan into `compose_codex_compensation`. Do not duplicate
  its order, output validation, absence proof, residual journal or failure
  reduction logic.
- Declared malformed/wrong returned observations remain finite through the
  existing composition. RuntimeError, MemoryError, KeyboardInterrupt and
  SystemExit propagate unchanged after claim consumption; replay then blocks
  without additional operations.
- The entry owns no registry, clear/retry path, durable state, raw diagnostics,
  absolute-path output or lifecycle oracle. It does not execute forward
  registration or proof receipt settlement.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `S1` | First red imports absent `codex_registration_compensation_settlement` and fails with exact `ModuleNotFoundError`; production remains absent during red. |
| `S2` | Safe port admission precedes claim consumption. Invalid/null/container/property/descriptor/shape/trap candidates return existing `CodexCompensationPortRejected`, leave the exact claim usable and invoke zero caller operations. |
| `S3` | Invalid, raw DTO, wrong-kind, foreign, altered, fabricated, metadata-only and replayed claims return existing `INVALID_CLAIM` with zero compensation operations. One exact live compensation claim is consumed once inside settlement. |
| `S4` | Terminal compensation builds every manifest field only from the consumed B2B2 claim-owned request, uses its exact plan and returns the existing exhaustive composition result. Valid-but-replaced raw DTO/request/manifest values have no authority path. |
| `S5` | Started-add recovery builds every manifest field only from its consumed claim-owned request and rebuilds the sole plan only from its journal/preflight/attempt. Invalid/non-required plans finite-fail before effect. |
| `S6` | The admitted capability receives one exact request identity in the exact plan order; no unplanned operation runs. Existing malformed return, absence, residual-journal and finite failure behavior is preserved by composition. |
| `S7` | RuntimeError, MemoryError, KeyboardInterrupt and SystemExit propagate after consumption; replay performs zero additional calls. Synchronized duplicate settlement yields exactly one compensation sequence and one claim block. |
| `S8` | Source invokes no forward registration, proof receipt, oracle, process, raw filesystem, network, target-project or Agent effect and adds no `Any`, `type: ignore`, broad catch, optional/`None` port, dynamic lookup/signature or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| `S9` | Independently reverse admission-before-consumption, exact claim consumption, one manifest field source, terminal plan source, recovery plan source and consume-before-effect/replay. Each named committed test turns red and exact blobs restore; focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology and residue checks pass. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_compensation_settlement.py`.
2. New `tests/test_codex_registration_compensation_settlement.py`.

All integrated source/tests and package exports remain read-only. No numeric
line limit is an acceptance criterion. Return one exact two-path implementation
commit, then one `doc/WorkProgressReport.md`-only handoff reserved as
`PRG-20260812-260`.

No B2E/05C work, live Codex, user profile, process, raw filesystem, network,
target-project mutation, other Agent, review, integration, push, release or
deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2D-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2d_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2d_20260812` / `rcpt_local_orchestration_install_05b4b2d_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b2d-20260812` / `q-local-orchestration-install-05b4b2d-20260812` |
| Side context | `scx-local-orchestration-install-05b4b2d-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-registration-compensation-settlement-05b4b2d` from the exact dispatch commit. |

Freeze is not dispatch. A later dispatch registry must bind the exact freeze
commit and verified clean lane before implementation starts.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `e6d747bd04b90b922202b6eb8ded1e12c409c678`; exact S1-S9; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for this ticket only |
| Lane readback | Task is idle; existing `workflow-implementer-2` is clean at exact submitted HEAD `e12ee8bef24172db517bfb346bd7fd4f972a2759`; exactly three existing worktrees; B2D branch absent |
| Branch | Create only `codex/implementation-codex-registration-compensation-settlement-05b4b2d` from this exact dispatch-registry commit in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2d_20260812`; `aln_local_orchestration_install_05b4b2d_20260812`; `rcpt_local_orchestration_install_05b4b2d_20260812`; `corr-local-orchestration-install-05b4b2d-20260812`; `q-local-orchestration-install-05b4b2d-20260812`; `scx-local-orchestration-install-05b4b2d-20260812-01` |

This is the single dispatch. Only the exact two implementation paths and later
WPR-only PRG-20260812-260 are writable in this lane.

## Review decision

Terminal independent review of implementation `bf9278f182bf2a6e11e62e83c67f43e276e73dfe`
and WPR-only handoff `60a8311548edfd096733d1d7cf1e1eb928077f55`
is `APPROVED / READY_TO_MERGE` under S1-S9.
