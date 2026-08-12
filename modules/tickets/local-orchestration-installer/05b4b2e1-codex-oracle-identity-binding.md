# 05B4B2E1 — Codex Oracle Identity Binding

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 staging seam |
| State | `CHANGES_REQUESTED / CORRECTION_PENDING` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E1-01` / I1-I8 |
| Dependency | E0 integrated by `3fc2f99f9cd4a7fff3e100918089ffed99cc16ab` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

Purely rebuild one exact integrated `CodexRegistrationPortRequest` and map it
to a deterministic 05S4 `OracleIdentity`. The binding supplies the disposable
oracle with exact request identity and canonical logical marketplace/plugin
paths without invoking an oracle command or treating fixture-only labels as
receipt authority.

## Frozen design

- Add a test-staging module
  `tests/staging/codex_lifecycle_oracle/identity_binding.py`. It may import the
  integrated public `revalidate_registration_port_request` and the E0
  `OracleIdentity`; it must not duplicate production request validators.
- Return a closed typed result: `OracleIdentityBound` containing a recursively
  rebuilt `CodexRegistrationPortRequest` and a new exact `OracleIdentity`, or
  `OracleIdentityBindingRejected` with one finite named reason. Never return
  `None`, a raw mapping, tuple or exception as an ordinary result.
- Use named staging-only constants for the fixed logical root
  `C:\Users\oracle\AppData\Local\JohnnyAIWorkflow`, plugin `source` and
  `installPolicy`. These constants are fixture inputs only and cannot enter a
  production receipt, manifest proof, Router state, telemetry or error text.
- Map marketplace, plugin name, plugin ID, version and auth policy only from
  the rebuilt request. Derive `marketplace_root` and `plugin_installed_path`
  by joining the fixed logical root with the rebuilt request's exact owned
  relative source/installed locators using Windows path semantics. Both paths
  must be exact normalized descendants and satisfy the E0 logical-path
  contract; no current host path or environment variable is read.
- A raw value, subclass, constructed-invalid request, malformed nested value,
  source mismatch, invalid logical result or caller-protocol trap must return
  the finite rejection before a bound identity exists. No caller-controlled
  comparison, hashing, path conversion, representation or serialization may
  run before the integrated request revalidator has admitted exact types.
- This ticket has no port/callable and performs no oracle command, process,
  filesystem, environment, network, target-project, Agent or package effect.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `I1` | First red is the missing `identity_binding` staging module while integrated production and E0 files remain unchanged. |
| `I2` | One exact request returns `OracleIdentityBound`; its retained request is a recursively rebuilt equal value with no nested object identity shared with the caller. |
| `I3` | The identity maps exact marketplace name, plugin name, expected plugin ID, expected version and expected auth policy from the rebuilt request; fixture `source` and `installPolicy` equal only their named staging constants. |
| `I4` | Marketplace root equals the fixed logical root plus exact `source_locator`; plugin installed path equals the same root plus exact `installed_locator`. Case, segments and separators are preserved exactly, both paths pass E0 validation and neither is replaced by an oracle physical locator. |
| `I5` | Raw/subclass/container/null, missing/extra/constructed-invalid nested fields, source mismatch, relative/URI/traversal/alternate-separator and caller-protocol traps return `OracleIdentityBindingRejected` without an exception or partial identity. |
| `I6` | The binding module exposes no command, oracle, port, callable authority, environment access or mutable global registry; it cannot execute an effect. Fixed staging labels do not appear in production receipt/proof modules. |
| `I7` | Source adds no `Any`, `type: ignore`, broad catch, optional/`None` authority, dynamic lookup/signature or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| `I8` | Independently reverse request revalidation, marketplace/path field source and plugin/path/auth field source. Each named committed test turns red and exact blobs restore; focused/full unittest, strict mypy, compile, source/scope/diff/ancestry/topology and residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. New `tests/staging/codex_lifecycle_oracle/identity_binding.py`.
2. New `tests/test_codex_oracle_identity_binding.py`.

All integrated production source, E0 oracle source/tests and package exports are
read-only. No numeric line limit is an acceptance criterion. Return one exact
two-path implementation commit, then one `doc/WorkProgressReport.md`-only
handoff reserved as `PRG-20260813-274`.

No E2-E6/05C/package work, live Codex, host/filesystem/environment/network,
target-project, other Agent, review/integration, push, release or deployment is
authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E1-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e1_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e1_20260813` / `rcpt_local_orchestration_install_05b4b2e1_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e1-20260813` / `q-local-orchestration-install-05b4b2e1-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e1-20260813-01` |
| Owner / lane | Existing task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; `workflow-implementer-2`; later create only `codex/implementation-codex-oracle-identity-binding-05b4b2e1` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `d25e6fcae3c273f94efe5cf68e3dc5b078e235ed`; exact I1-I8; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved small-ticket work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E1 only |
| Lane readback | Task is idle/not-loaded; existing `workflow-implementer-2` is clean at exact submitted HEAD `60a8311548edfd096733d1d7cf1e1eb928077f55`; zero tracked/ignored/cache residue; exactly three existing worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-oracle-identity-binding-05b4b2e1` from the exact commit carrying this dispatch registry in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e1_20260813`; `aln_local_orchestration_install_05b4b2e1_20260813`; `rcpt_local_orchestration_install_05b4b2e1_20260813`; `corr-local-orchestration-install-05b4b2e1-20260813`; `q-local-orchestration-install-05b4b2e1-20260813`; `scx-local-orchestration-install-05b4b2e1-20260813-01` |

This is the single dispatch. Only the exact two implementation paths and a
later WPR-only `PRG-20260813-274` are writable in this lane.

## Initial independent review

Review `doc/reviews/local-orchestration-installer/05b4b2e1-codex-oracle-identity-binding-code-review.md`
records `CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION`. CR-159 proves that
injected extra state on most exact nested request models is erased during
rebuilding and then accepted, contrary to I5. The same ticket, owner,
worktree, branch, allocation, receipt and correlation are retained. No new
branch or worktree is permitted.
