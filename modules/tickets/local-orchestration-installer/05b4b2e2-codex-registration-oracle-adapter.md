# 05B4B2E2 — Codex Registration Oracle Adapter

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 |
| State | `FROZEN / READY_FOR_DISPATCH` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E2-02` / R1-R8 |
| Dependency | E1 `27c8305`, E2A `52a2a4e` and E2B `784d08a` approved/integrated; oracle absence hardening `dc07eec` present in baseline |
| Planned owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

One staging-only adapter binds an exact rebuilt registration request, exact E1
oracle identity and exact live disposable lease to the integrated four-operation
registration port. Fresh VERSION/add/list evidence is translated into the
existing finite port values, while invalid or mismatched calls cannot invoke the
oracle and no success path, version or proof is copied from caller authority.

## Logical-root precondition

E1 deliberately returns the deterministic logical root
`C:\Users\oracle\AppData\Local\JohnnyAIWorkflow`; production value validators
expand `%LOCALAPPDATA%\JohnnyAIWorkflow` in their own process. Reviewer probe
proved the same E1 marketplace observation is `REQUEST_MISMATCH` under the
ambient host but valid when the adapter process has
`LOCALAPPDATA=C:\Users\oracle\AppData\Local`.

The adapter must therefore fail closed before oracle effects unless its process
expansion equals the exact E1 fixed logical root. Focused success tests must run
in a dedicated child Python process launched with that logical environment; the
parent environment must be byte-for-byte unchanged after the child. Tests may
not patch the long-lived parent environment, manufacture a host path, or replace
the E1 fixed root. Physical payloads remain under the exact 05S1 lease.

## Frozen design

- Add only `tests/staging/codex_lifecycle_oracle/registration_adapter.py` and
  `tests/test_codex_registration_oracle_adapter.py`.
- A closed factory receives one exact recursively valid `EnvironmentLease`, one
  exact `CodexLifecycleOracle`, and one exact `OracleIdentityBound`. It returns
  an adapter or metadata-only finite rejection; no `None`, raw mapping, caller
  callable, dynamic lookup, broad catch or exception text crosses the boundary.
- The admitted adapter retains the rebuilt request/lease/identity. Every public
  operation first revalidates its exact input and compares all fixed fields to
  that retained authority before an oracle command is possible.
- Fresh preflight runs `VERSION`. It accepts only an exact VERSION response equal
  to the retained expected version; mismatch becomes `UNSUPPORTED_CLI`, while
  oracle/protocol blocks map to an existing finite `CodexBlockReason` without a
  raw reason or substituted version.
- Marketplace/plugin add run exactly their matching oracle action. Success DTOs
  are built only from the exact accepted payload plus retained rebuilt request,
  then passed through the integrated registration-port revalidator. A malformed,
  wrong-surface, wrong-identity or wrong-path response is a started finite
  failure, never success. Invalid/foreign request is the E2B `NOT_STARTED`
  failure and invokes the oracle zero times.
- After an exact add operation has invoked `CodexLifecycleOracle.run`, an
  `OracleBlocked` or malformed accepted envelope is conservatively returned as
  `CodexStartedFailureReason.MALFORMED_RESPONSE`; an exact accepted envelope
  whose identity/path fields disagree is `IDENTITY_MISMATCH`. This does not claim
  successful ownership; it preserves the existing started/ambiguous cleanup
  authority. The adapter must not guess a launch/exit reason that the oracle did
  not retain.
- `prove` is legal only after this exact adapter instance returned both accepted
  add results for the retained request. It requires exact matching proof input,
  then fresh marketplace and plugin list evidence for the same identity before
  returning the existing `CodexRegistrationProof`. Missing, duplicate, foreign,
  malformed or blocked evidence raises only the declared
  `CodexRegistrationProofPortFailure`; it never returns a fabricated proof.
- Adapter state may retain only rebuilt typed request/add observations and finite
  phase state. It stores no raw response, diagnostic, command, path outside those
  approved DTOs, global registry or target-project value.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `R1` | First red is the missing staging adapter module; integrated production/oracle files remain unchanged. |
| `R2` | Exact lease/oracle/E1 binding plus exact logical-root process expansion returns one candidate admitted by `admit_codex_registration_port`; invalid/subclass/constructed/mismatched inputs reject before an oracle command. |
| `R3` | Fresh VERSION is child-produced from persisted oracle state. Exact match accepts; expected-version substitution, caller identity version, wrong/malformed surface, state/process/protocol block or mismatch returns only the frozen finite rejection. |
| `R4` | Marketplace add executes once and returns exact confirmed/observation fields from the accepted payload. Invalid or foreign invocation executes zero times; malformed/wrong identity/path blocks without success. |
| `R5` | Plugin add executes once only after the exact owned marketplace transition and returns exact ID/name/marketplace/version/path/auth evidence. Invalid/foreign invocation and every malformed/mismatched response cannot claim plugin ownership. |
| `R6` | Proof before both exact adds, replayed/foreign proof input, missing/duplicate/mismatched fresh list entry or oracle block yields only `CodexRegistrationProofPortFailure`. Exact sequential adds plus fresh matching lists yield one proof matching every request field and both returned observations. |
| `R7` | Dedicated-child success matrix proves fixed logical `%LOCALAPPDATA%` equivalence, disposable physical payload isolation, exact teardown and unchanged parent environment. Ambient-host mismatch is a committed fail-closed test, not repaired by path rewriting. |
| `R8` | Independently reverse version source, add-payload identity/path validation, no-effect request gate and proof fresh-list gate. Each named test turns red and exact blobs restore; focused/full unittest, strict mypy, compile, source/scope/diff/ancestry/topology/residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. New `tests/staging/codex_lifecycle_oracle/registration_adapter.py`.
2. New `tests/test_codex_registration_oracle_adapter.py`.

No numeric line limit is an acceptance criterion. Return one exact two-path
implementation commit, then one `doc/WorkProgressReport.md`-only handoff reserved
as `PRG-20260813-302`.

The lane may create and remove only exact disposable roots it creates and can
prove through its lease. It must not enumerate, inspect, delete or infer anything
from other/global `johnny-stage-env-*` roots. No production source, E3-E6,
environment allocator, live Codex, host configuration, network, target-project,
other Agent, review/integration, staging push, package, release or deployment
action is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E2-02` |
| Handoff | `hnd_local_orchestration_install_05b4b2e2_r02_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e2_r02_20260813` / `rcpt_local_orchestration_install_05b4b2e2_r02_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e2-r02-20260813` / `q-local-orchestration-install-05b4b2e2-r02-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e2-r02-20260813-01` |
| Owner / lane | Existing task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; later create only `codex/implementation-codex-registration-oracle-adapter-05b4b2e2` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `d5ff1297be90d223834aded354d9d33b6dbd4b35`; exact R1-R8; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved small-ticket work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E2 only |
| Lane readback | Idle task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation` clean at submitted HEAD `7c17caf23a80d5c1bfc5bf81237ce0daba091607`; zero tracked/ignored/cache residue; exactly three worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-registration-oracle-adapter-05b4b2e2` from the exact commit carrying this registry in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e2_r02_20260813`; `aln_local_orchestration_install_05b4b2e2_r02_20260813`; `rcpt_local_orchestration_install_05b4b2e2_r02_20260813`; `corr-local-orchestration-install-05b4b2e2-r02-20260813`; `q-local-orchestration-install-05b4b2e2-r02-20260813`; `scx-local-orchestration-install-05b4b2e2-r02-20260813-01` |

This is the single dispatch. Only the exact two implementation paths and the
later WPR-only `PRG-20260813-302` are writable in this lane.

## Correction dispatch registry — CR-162 / CR-163 / CR-164

| Field | Value |
| --- | --- |
| Review | `CHANGES_REQUESTED` at `56e65bd7fd2d2ac538603bc162eefd17610aa574`; R2-R3 remain open. |
| FRESH_BRANCH_REQUIRED evidence | Original implementation task `019fcc9c-f34f-7d53-a313-c70c90bf3245` rejected the correction turn before work with product usage-limit `systemError`, retry time 2026-08-18 10:20. Its existing worktree remains clean at exact handoff `699cba8f1b844552a9b36baf926613594542ed4b`. Implementation owner/worktree replacement is therefore required; no correction mutation exists to preserve. |
| Replacement lane | Idle task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2` clean at submitted E3C handoff `b153636fe2acd37af0b376ee825e0cf9336b98b1`; exactly three worktrees; target correction branch absent. |
| Branch / base | In the same replacement worktree create only `codex/implementation-codex-registration-oracle-adapter-05b4b2e2-correction` from immutable E2 handoff `699cba8f1b844552a9b36baf926613594542ed4b`; no new worktree, merge, rebase, cherry-pick, reset or amend. |
| Binding | New correction handoff `hnd_local_orchestration_install_05b4b2e2_cr162_164_20260813`; allocation `aln_local_orchestration_install_05b4b2e2_cr162_164_20260813`; retained valid receipt `rcpt_local_orchestration_install_05b4b2e2_r02_20260813`; correlation `corr-local-orchestration-install-05b4b2e2-cr162-164-20260813`; question `q-local-orchestration-install-05b4b2e2-cr162-164-20260813`; side-context `scx-local-orchestration-install-05b4b2e2-cr162-164-20260813-01`. |
| Scope | Only the same two adapter/test implementation paths plus a later unique WPR-only correction handoff. Exact correction requirements are the review document; all original R1-R8 constraints remain. |
