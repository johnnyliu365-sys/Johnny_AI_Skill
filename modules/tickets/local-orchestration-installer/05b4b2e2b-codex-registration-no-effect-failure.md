# 05B4B2E2B — Codex Registration No-Effect Failure Reasons

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 |
| State | `FROZEN / READY_FOR_DISPATCH` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E2B-01` / N1-N7 |
| Dependency | E2A integrated by `52a2a4e`; registration port/reducer integrated |
| Planned owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Ticket-defect basis

The E2 adapter must reject an invalid or request-mismatched add invocation
before invoking the oracle. The closed pre-start reason set cannot currently
say either fact. Mapping such a call to a started failure would invent an
effect; throwing would violate the finite port contract.

## One observable outcome

An exact marketplace/plugin add result can carry `INVALID_REQUEST` or
`REQUEST_MISMATCH` as a strict `NOT_STARTED` failure. Existing classification,
port revalidation and reducer behavior remain conservative: marketplace add
blocks without compensation; plugin add retains compensation for the already
owned marketplace, while never claiming the plugin command started.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `N1` | First red proves the two no-effect facts are absent from the closed pre-start algebra. |
| `N2` | Add exactly `INVALID_REQUEST` and `REQUEST_MISMATCH` to `CodexPreStartFailureReason`; their only legal start state is `NOT_STARTED`. |
| `N3` | Both add targets round-trip these reasons through the exact registration-port revalidators while wrong target, subclass, missing/extra and constructed-invalid values reject. |
| `N4` | Marketplace-add no-effect failure blocks with `MARKETPLACE_ADD_NOT_STARTED` and no compensation authority. |
| `N5` | Plugin-add no-effect failure never marks plugin ownership and compensates only the already-owned marketplace. |
| `N6` | No callable, exception, raw diagnostic, oracle data, path authority or effect is added; no broad catch, `Any`, `type: ignore` or dynamic lookup is introduced. |
| `N7` | Reverse both new reasons and the two reducer outcomes independently, restore exact blobs, then pass focused/full unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks. |

## Exact source and return

Writable implementation paths only:

1. `library/local_orchestration/codex_command_attempts.py`
2. `tests/test_codex_command_attempts.py`
3. `tests/test_codex_registration_port.py`
4. `tests/test_codex_registration_reducer.py`

No numeric line limit is an acceptance criterion. Return one implementation
commit over exactly those paths, then one `doc/WorkProgressReport.md`-only
handoff reserved as `PRG-20260813-291`.

No adapter/oracle/environment, live Codex, host/filesystem/network,
target-project, other Agent, review/integration, staging push, package, release
or deployment action is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E2B-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e2b_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e2b_20260813` / `rcpt_local_orchestration_install_05b4b2e2b_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e2b-20260813` / `q-local-orchestration-install-05b4b2e2b-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e2b-20260813-01` |
| Owner / lane | Existing task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; later create only `codex/implementation-codex-no-effect-failure-05b4b2e2b` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.
