# 06G0 — Restricted Implementation-session Transport Proof

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` revision 03 / AC-09 |
| Change / ADR | `CHG-20260814-018`; `ADR-20260814-010` |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T06G0-01` / T1-T6 |
| Delivery profile | `HIGH_ASSURANCE`; one implementer lane; no helper |
| Model capability | implementation owner: high-capability coding model, highest reasoning available; model is not authority |
| Reviewer | Control-plane `main`; sole Johnny gateway owner |
| Environment | Existing permanent implementation worktree after one exact receipt; disposable project-owned test runtime only |
| Dependency | 06G0P independently approved and integrated |

## One outcome

Determine whether one documented, supported local Codex transport can bind the
exact restricted implementation custom-agent configuration to an effective
session in the exact assigned worktree and read back the forbidden
multi-agent/thread-control tools as absent. Return `SUPPORTED` only from that
observation; otherwise return the exact finite `INSTALL_BLOCKED /
ROLE_ISOLATION_UNPROVEN` reason.

This ticket does not implement the Johnny gateway, create a real Agent task,
install a CLI, edit live Codex configuration or mutate a target project.

## Exact source boundary

- `tests/staging/codex_restricted_session_transport/__init__.py` (new)
- `tests/staging/codex_restricted_session_transport/capability_probe.py` (new)
- `tests/test_codex_restricted_session_transport_capability.py` (new)
- one append-only `doc/WorkProgressReport.md` handoff after the implementation
  commit

Reuse only the integrated public 05S1/05S2 and 06A contracts. Do not copy a
historical branch or modify 06A source/evidence.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `T1` | Admission accepts one exact documented transport kind, exact executable/tool identity, exact implementation profile digest, exact worktree identity and bounded observation schema. Empty, null-equivalent, container, wildcard, traversal, wrong case/suffix and caller-provided success are rejected before process or host effect. |
| `T2` | Candidate config sets both supported implementation-side multi-agent controls to disabled where documented. Static TOML/config parsing can only produce `CANDIDATE`; it cannot produce `SUPPORTED`. |
| `T3` | The bounded probe launches no model turn and creates no real task. It may execute only a documented metadata/capability readback against the disposable config boundary. Access denied, absent launch/profile-binding option, unsupported option, timeout, nonzero exit, malformed/ambiguous output or network/model requirement maps to one finite blocked reason. |
| `T4` | `SUPPORTED` requires fresh effective evidence that the exact profile digest and exact worktree binding were used and every create/spawn/fork/send/follow-up/steer/wait/interrupt/close capability is absent. Config bytes, prompt text, a synthetic fake or caller assertion cannot satisfy this result. |
| `T5` | Teardown proves the disposable root absent and preserves a same-name foreign profile plus two external Git/empty sentinels byte-for-byte and porcelain-clean. No live `%USERPROFILE%/.codex`, App state or target project is written. |
| `T6` | Committed tests reverse profile/worktree binding, one forbidden-tool absence and the `SUPPORTED` evidence guard; each mutation turns the governing test red and is restored exactly. Full strict typing, in-memory compile, source sentinel and tracked/ignored/cache absence pass. |

## Strong-type dispatch preflight

Before receipt issuance, reviewer and implementer must run ordinary public
constructor/validator/round-trip probes for integrated `AgentProfileSpec`,
`AgentProfileLocator`, `CodexExecutableLocator`, `MetadataDigest`,
`ToolSurface`, `EffectiveCapabilityReadback`, `UnavailableCapabilityReadback`
and `RoleProfileProbeResult`, including exact enum states and strict booleans.
The new staging module may introduce no public DTO/value/event; it must reuse
those integrated contracts. A committed AST gate must reject `Any`,
`type: ignore`, `object`/dynamic values, `Optional`/None-valued success ports,
casts, bypass model construction/update, dynamic member lookup, broad catches
and caller-supplied effective evidence. Its bounded reverse mutation is part of
T6. Missing/failed preflight is `HALT / TICKET_SCHEMA_INVALID` before first red.

## Boundaries and return

`XSS_NOT_APPLICABLE`. No Browser/WebView/DOM/JavaScript, Secret, network,
helper/subagent, new worktree, live Codex/home/App mutation, target-project
write, push, package, install, release or deployment. Return one implementation
commit and then one WPR-only handoff. `SUPPORTED` advances to independent review;
any blocked result is truthful terminal evidence and does not authorize 06G1.
