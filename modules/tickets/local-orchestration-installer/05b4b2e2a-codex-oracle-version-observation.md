# 05B4B2E2A — Codex Oracle Version Observation

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 staging seam |
| State | `IMPLEMENTATION_DISPATCH_CONFIRMED / IMPLEMENT` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E2A-01` / V1-V8 |
| Dependency | E1 integrated by `27c8305200f61d9658aa5b2b32bd15a7db4d0b4c` |
| Planned owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Ticket-defect basis

E2 must return `CodexFreshPreflightAccepted` only from a fresh observed Codex
CLI version. The integrated oracle exposes add/list/remove surfaces only. Its
command identity contains the caller's expected plugin version, so copying that
value into preflight would manufacture success from caller data. E2 remains
blocked until this ticket supplies an independent child-observed version.

## One observable outcome

One fresh oracle `VERSION` action launches the bounded child, validates the
persisted exact oracle state and returns a strict `CodexVersionObservation`
whose value comes only from the oracle's independently initialized state. The
command identity's plugin version cannot select or alter the observation.

## Frozen design

- Add one strict `VERSION` protocol surface and one strict payload containing
  only a nonblank `version` field. The protocol parser/fixture rejects missing,
  extra, duplicate, malformed and surface-discriminator mismatches with the
  existing finite protocol reasons.
- Add `OracleAction.VERSION`. Persist one named staging-only Codex CLI version
  in `OracleState` during `initialize`; it is not accepted from an E2 request,
  command identity, environment variable or host Codex installation.
- The oracle child validates the exact persisted state including that version,
  emits it for `VERSION`, and performs zero marketplace/plugin/foreign/payload
  mutation. A command identity carrying a different plugin version must still
  receive the persisted oracle version.
- Preserve command/response cleanup, bounded child execution, exact
  lease/state/topology gates and all existing finite failure mapping. This
  ticket does not decide E2 eligibility or build a registration port.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `V1` | First red shows `VERSION` protocol/action/state do not exist before implementation. |
| `V2` | Exact protocol parsing accepts only the one-field version payload under the VERSION discriminator; malformed and cross-surface payloads reject finitely. |
| `V3` | Oracle initialization writes one named staging version independently of every command identity and request value. |
| `V4` | A fresh VERSION run returns that persisted value through a new child process; a different `identity.plugin_version` cannot affect it. |
| `V5` | Missing/extra/constructed-invalid state version and invalid lease/command/state/topology/process/cleanup paths return existing finite blocks without partial success. |
| `V6` | VERSION leaves state bytes, payload tree and owned/foreign collections unchanged and leaves no command/response residue. |
| `V7` | Source adds no `Any`, `type: ignore`, broad catch, caller-selected executable/path, live Codex or target-project effect. `XSS_NOT_APPLICABLE`. |
| `V8` | Reverse the surface discriminator, caller-independent state source and zero-mutation evidence independently. Each named test turns red, exact blobs restore, and focused/full unittest, strict mypy, compile, scope/diff/ancestry/topology/residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. `tests/staging/codex_protocol/contracts.py`
2. `tests/staging/codex_protocol/fixture_child.py`
3. `tests/staging/codex_lifecycle_oracle/contracts.py`
4. `tests/staging/codex_lifecycle_oracle/oracle.py`
5. `tests/staging/codex_lifecycle_oracle/oracle_child.py`
6. `tests/test_codex_protocol_fixture.py`
7. `tests/test_codex_lifecycle_oracle.py`

No numeric line limit is an acceptance criterion. Return one implementation
commit over exactly those paths, then one `doc/WorkProgressReport.md`-only
handoff reserved as `PRG-20260813-283`.

No E2 adapter, compensation, environment allocation, live Codex, host/network,
target-project, other Agent, review/integration, staging push, package, release
or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E2A-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e2a_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e2a_20260813` / `rcpt_local_orchestration_install_05b4b2e2a_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e2a-20260813` / `q-local-orchestration-install-05b4b2e2a-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e2a-20260813-01` |
| Owner / lane | Existing task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; `workflow-implementation`; later create only `codex/implementation-codex-oracle-version-observation-05b4b2e2a` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `341a58bcfc8b6553db149a56ac005ac9fafec373`; exact V1-V8; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner instruction to continue approved small-ticket work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E2A only |
| Lane readback | Idle task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation` clean at exact submitted HEAD `002b2982cbf111262865946dc16d83c23a7bc879`; zero tracked/ignored/cache residue; exactly three worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-oracle-version-observation-05b4b2e2a` from the exact commit carrying this registry in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e2a_20260813`; `aln_local_orchestration_install_05b4b2e2a_20260813`; `rcpt_local_orchestration_install_05b4b2e2a_20260813`; `corr-local-orchestration-install-05b4b2e2a-20260813`; `q-local-orchestration-install-05b4b2e2a-20260813`; `scx-local-orchestration-install-05b4b2e2a-20260813-01` |

This is the single dispatch. Only the seven exact implementation paths and a
later WPR-only `PRG-20260813-283` are writable in this lane.
