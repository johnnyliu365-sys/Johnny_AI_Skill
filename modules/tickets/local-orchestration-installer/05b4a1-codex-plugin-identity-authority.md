# 05B4A1 — Codex Plugin Identity Authority

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 registration seam |
| State | `COMPLETE / APPROVED / INTEGRATED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4A1-01` / I1-I6 |
| Dependency | 05B4A approved and integrated by `5f30a717e16cbdc126a685e48542c11337310bbf` |
| Owner / worktree | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Bind the installer-controlled expected Codex plugin ID into every registration
request before an effect. A plugin-add observation is accepted only when its
`plugin_id` equals that exact authority. This makes an ambiguous started
plugin-add attempt compensable without trusting a missing, foreign or
caller-manufactured returned ID.

This is a prerequisite contract ticket, not a reopened 05B4A correction and
not registration composition. The product requirement and approved 05B4A
capability behavior do not change.

## Freeze evidence and boundary

The integrated `CodexRegistrationPortRequest` binds installation, preflight,
attempt, version, locators, digest and auth policy but has no expected plugin
ID. `revalidate_plugin_add_result` therefore rebuilds any valid
`CodexPluginId` and cannot compare it to installer authority. Meanwhile the
integrated `CodexCompensationPortManifest` requires an exact plugin ID even
when a started add returns no usable observation. Dispatching 05B4B without
this prerequisite would force caller-manufactured identity or make exhaustive
compensation impossible.

- Add required `expected_plugin_id: CodexPluginId` to
  `CodexRegistrationPortRequest`. It has no default and is never nullable.
- Recursive request rebuilding and every request-equality path include the
  exact plugin ID before comparison of a supplied nested value.
- Exact plugin-add success requires
  `observation.plugin_id == expected_request.expected_plugin_id`; a different
  otherwise-valid ID returns existing metadata-only `REQUEST_MISMATCH`.
- Fresh-preflight, marketplace and plugin result envelopes remain bound to the
  whole exact request, including the new authority.
- Capability admission, its four operations, `ADMITTED / 4`, transfer guards,
  error/repr rules and all integrated dependency types remain unchanged.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `I1` | First red proves the current request rejects the new required field and the current plugin-result validator accepts an otherwise exact foreign plugin ID. Production is unchanged during this red. |
| `I2` | Request construction and `revalidate_registration_port_request` require an exact `CodexPluginId`. Missing, `None`, empty, whitespace, list, dict, plain object and constructed raw-string shapes fail finitely as `INVALID_REQUEST`; no equality, serialization or caller trap executes first. |
| `I3` | Exact expected plugin ID survives request rebuilding. Fresh, marketplace and plugin envelopes carrying a request with another plugin ID return `REQUEST_MISMATCH`; exact-ID envelopes rebuild into distinct exact values. |
| `I4` | Plugin-add observation IDs are crossed across exact, case-changed, prefix-plus-character and unrelated valid values. Only the exact ID succeeds; every other valid ID returns `REQUEST_MISMATCH` with no raw value in result, repr or error. |
| `I5` | Existing A1-A7 capability behavior remains green: metadata `ADMITTED / 4`, zero operation calls, descriptor/metaclass traps uninvoked, and all five structural/copy/pickle transfer probes remain blocked. No integrated dependency or package export changes. |
| `I6` | Independently reverse expected-ID request equality and plugin-observation ID binding; both named committed tests turn red and are restored. Focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff and tracked/ignored/cache readbacks pass. |

## Exact source and return

1. Existing `library/local_orchestration/codex_registration_port.py`.
2. Existing `tests/test_codex_registration_port.py`.

No package-root, dependency, staging, compensation or transaction-composition
file may change. Rejected 05B/05B3 source is evidence only and must not be
copied, imported, cherry-picked or used as an implementation source. No
numeric line count is an acceptance criterion.

Return one exact two-path implementation commit followed by one
`doc/WorkProgressReport.md`-only handoff reserved as PRG-20260812-201. No
`Any`, `type: ignore`, broad catch, dynamic member/signature lookup, optional
port, new dependency, live Codex/host/target-project/network effect, review,
integration, 05B4B/05C work, push, release or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4A1-01` |
| Handoff | `hnd_local_orchestration_install_05b4a1_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4a1_20260812` / `rcpt_local_orchestration_install_05b4a1_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4a1-20260812` / `q-local-orchestration-install-05b4a1-20260812` |
| Side context | `scx-local-orchestration-install-05b4a1-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only branch `codex/implementation-codex-plugin-identity-authority-05b4a1` from the exact dispatch registry commit. |
| Return | Exact two-path implementation commit, then WPR-only PRG-20260812-201. |

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `741ae0b300321f0f95341c322b9262909a8e6b4b`; exact I1-I6 |
| Delivery confirmation | Owner instruction `開始吧`; question `q-local-orchestration-install-05b4a1-20260812` is answered positively for this ticket only |
| Lane admission | Existing clean `workflow-implementer-2` at `7ce9bb36e90af669daa5dfa2999638a112f4cde3`; three-worktree topology unchanged |
| Required branch | Create only `codex/implementation-codex-plugin-identity-authority-05b4a1` directly from the exact later dispatch-registry commit in the same worktree; no merge, rebase, cherry-pick or new worktree |
| Authority | `hnd_local_orchestration_install_05b4a1_20260812`; `aln_local_orchestration_install_05b4a1_20260812`; `rcpt_local_orchestration_install_05b4a1_20260812`; `corr-local-orchestration-install-05b4a1-20260812`; `scx-local-orchestration-install-05b4a1-20260812-01` |

## Independent review disposition

Implementation `76f0b9681264e359873354145e1ddcaa92aaf894` and
docs-only handoff `30d6bcff91368c162664dc2eef7dee5a7c543950` are
`APPROVED / READY_TO_MERGE`. The formal review is
`doc/reviews/local-orchestration-installer/05b4a1-codex-plugin-identity-authority-code-review.md`.

I1-I6 are closed without a correction request. Only guarded integration is
the next legal action. Ticket 05B4B remains undispatched until this reviewed
contract is integrated.

## Completion

Guarded merge `3399cf934874f3304959ef0b6913548c0d767e01`
integrates the reviewed handoff with formal review
`42e1590126cdc7f922269b2d7e4012862e85f15a` as first parent. Post-merge
verification passed. Allocation `aln_local_orchestration_install_05b4a1_20260812`
is released and receipt `rcpt_local_orchestration_install_05b4a1_20260812` is
closed against replay. 05B4B may now be refrozen by the control plane; this
completion is not an implementation dispatch.
