# 06A — Codex Role-profile Capability Proof

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC revision 02 / AC-09 and AC-10 feasibility |
| Change | `CHG-20260811-012` |
| State | `IN_PROGRESS / DISPATCH_CONFIRMED` |
| Dependency | 05S1/05S2/05S3 integrated; 05S4 revision-02 returned `COMPLETED`, and the project owner authorized a second non-overlapping implementation lane |
| Implementation owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`; branch `codex/implementation-codex-role-profile-proof-06a` recreated from the exact handoff baseline |
| Reviewer | Control-plane `main`; sole Agent-to-Agent orchestrator |
| Environment | Disposable `CODEX_HOME` only; no live user Codex mutation, target project, model turn, network, Secret, push, release or deployment |

## One outcome

Establish a deterministic host capability result for two Codex custom-agent
profiles. The reviewer profile must retain multi-agent tools; the implementation
profile must have them disabled by a supported config layer. If the installed
Codex build cannot be invoked or cannot prove the effective tool difference,
return typed `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN`; do not create a
prompt-only green result.

## Source boundary

Only these four new paths:

- `tests/staging/codex_agent_profiles/__init__.py`
- `tests/staging/codex_agent_profiles/contracts.py`
- `tests/staging/codex_agent_profiles/capability_probe.py`
- `tests/test_codex_agent_profile_capability.py`

Reuse integrated 05S1 disposable
environment and 05S2 bounded runner. Production installer/router source,
existing tests, user `%USERPROFILE%/.codex`, app data and target repositories
are read-only.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T06A-01`

| ID | Acceptance |
| --- | --- |
| `P1` | Strict frozen reviewer/implementation profile specs use official required fields (`name`, `description`, `developer_instructions`) and finite tool policy. Implementation config declares multi-agent disabled; reviewer config declares it enabled. |
| `P2` | The exact installed Codex executable/version is discovered without fallback wildcard. A bounded read-only probe loads both profiles from one disposable `CODEX_HOME` and records only version/digest/finite capability metadata. Access denied, absent command, unsupported config, model/network requirement or ambiguous readback is `ROLE_ISOLATION_UNPROVEN`. |
| `P3` | Effective reviewer evidence proves orchestration tools present and effective implementation evidence proves them absent. Config text equality, prompt assertions or a hand-built parser alone cannot project `SUPPORTED`. |
| `P4` | Teardown proves both owned profile files and the disposable root absent; a same-name foreign sentinel outside the lease plus existing/empty target-repository byte/porcelain snapshots remain unchanged. |

## TDD / return

Cover exact/suffix/case/encoded/traversal/empty executable/profile locators;
omission/null/empty/whitespace/list/object config values; foreign profile,
direct/indirect tool query, unsupported version, access denied, timeout,
malformed output and cleanup failure. Reverse the implementation disable flag
and reviewer enable expectation. Work alone; do not create, delegate to,
control or wait on another Agent. Return one implementation commit containing
only the four authorized paths and one `WorkProgressReport.md`-only handoff. A
reviewed `SUPPORTED` result unblocks autonomous Ticket 04; any other result is
a real typed stop for Codex role-profile installation.
