# 06G0P — Role-probe Result Contract Correction

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` revision 03 / AC-09 precondition |
| Change / ADR | `CHG-20260814-018`; `ADR-20260814-010` |
| State | `IN_PROGRESS / AWAITING_DELIVERY_CONFIRMATION` |
| Closure | `CLOSURE-LOCAL-INSTALL-T06G0P-01` / P1-P5 |
| Delivery profile | `STANDARD` with security escalation; one implementer; no helper |
| Reviewer | Control-plane `main`; sole Johnny gateway owner |
| Implementation owner | Task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2` |
| Planned branch | `codex/implementation-codex-role-probe-result-contract-06g0p` from exact dispatch baseline after confirmation |
| Dispatch binding | `hnd_local_orchestration_install_06g0p_20260814`; `aln_local_orchestration_install_06g0p_20260814`; question `q-local-orchestration-install-06g0p-20260814`; no receipt before positive confirmation |

## Preflight defect and one outcome

The exact current public constructor accepts a `RoleProfileProbeResult` with
`SUPPORTED / PROVEN / EFFECTIVE` while `process_evidence` is
`MALFORMED_OBSERVATION`. `SuccessfulProcessObservation` is currently projected
as `VERSION_OUTPUT_UNREADABLE`, a failure-named enum member that the role gate
treats as its success sentinel. This makes later transport evidence ambiguous.

Correct only this finite result contract: introduce one explicit successful
process-evidence state, map the existing successful observation to it, and make
`SUPPORTED` constructible only with that state plus existing proven/effective
requirements. Preserve every truthful blocked 06A outcome.

## Exact source boundary

- `tests/staging/codex_agent_profiles/contracts.py`
- `tests/staging/codex_agent_profiles/capability_probe.py`
- `tests/test_codex_agent_profile_capability.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `P1` | `ProcessEvidenceKind` contains one clearly named successful invocation state; successful bounded observation maps to it. No failure-named value acts as a success sentinel. |
| `P2` | `RoleProfileProbeResult(SUPPORTED, PROVEN, EFFECTIVE, successful-process-evidence, ...)` is ordinarily constructible and JSON round-trips with strict booleans/enums. |
| `P3` | `SUPPORTED` combined with every failure process evidence, including `MALFORMED_OBSERVATION`, fails public validation. Blocked results retain the exact successful or failure process observation plus their existing finite readback reason. |
| `P4` | Existing actual-host `ACCESS_DENIED / OUTPUT_UNAVAILABLE` path stays `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN`; no synthetic capability becomes supported. |
| `P5` | Committed tests reverse the supported-result validator and successful-observation mapping independently; each turns red and is restored. Strict mypy, compile, source sentinel, full tests and zero residue pass. |

## Strong-type and effect boundary

Reviewer preflight already reproduces the forbidden construct as the governing
red condition while all ordinary existing model round-trips remain valid. The
implementation pre-red must reproduce the same constructor defect before any
source change. The committed source gate rejects `Any`, `type: ignore`,
`object`, optional/None success values, casts, Pydantic bypass construction or
update, dynamic member lookup and broad catches in the exact three-file scope.

`XSS_NOT_APPLICABLE`. This is a pure staging-contract correction: no process,
Agent, gateway, filesystem, live Codex/home/App, target project, network, new
worktree, push, package, install, release or deployment effect. Return one
implementation commit and then one WPR-only handoff.
