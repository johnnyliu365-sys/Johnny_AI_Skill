# 05B4A — Codex Registration Port Capability

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 registration seam |
| State | `FROZEN / DISPATCH_PENDING` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4A-01` / A1-A7 |
| Dependency | Integrated 05A preflight, 05B1 contracts and 05B2 classifier; 05B3C remains read-only |
| Owner / worktree | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Given an adapter candidate, admit exactly four plain instance operations for a
single current registration attempt without resolving or executing any caller
descriptor. Public admission output is metadata-only. Invalid candidates,
method shapes and recursively malformed request/result envelopes fail finitely
before any operation is called.

This ticket freezes the boundary only. It must not run preflight, add, proof,
receipt, compensation, oracle, process, filesystem, host or target-project
effects and must not manufacture a final registration result.

## Frozen boundary

- New `CodexRegistrationPortRequest` binds one exact `CodexPreflightRequest`,
  `CodexRegistrationAttemptId`, expected `CodexCliVersion`, source and installed
  `OwnedRelativePath`, `ArtifactDigest` and expected `CodexAuthPolicy`. Source
  must equal the preflight marketplace source; no field is nullable.
- Fresh preflight output is either an exact request-bound accepted envelope
  carrying `CodexPreflightEligible`, or an exact request-bound rejected envelope
  carrying one existing finite `CodexBlockReason`.
- Marketplace add success binds the exact request, one
  `CodexMarketplaceAddConfirmed` and one `CodexMarketplaceAddObservation`.
  Plugin add success analogously binds `CodexPluginAddConfirmed` and
  `CodexPluginAddObservation`. A command failure binds the exact request and
  exactly one existing `CodexPreStartFailure` or `CodexStartedFailure`; its
  target must match the operation that returned it.
- Pure public validators are fixed as
  `revalidate_registration_port_request(value)`,
  `revalidate_fresh_preflight_result(value, expected_request)`,
  `revalidate_marketplace_add_result(value, expected_request)` and
  `revalidate_plugin_add_result(value, expected_request)`. They accept
  `object`, never invoke the adapter, and return either the exact rebuilt value
  or one metadata-only `CodexRegistrationPortValueRejected`. Its finite reasons
  are exactly `INVALID_REQUEST`, `REQUEST_MISMATCH`, `INVALID_RESULT`,
  `TARGET_MISMATCH` and `VERSION_MISMATCH`; raw validation text is absent.
- The four operation names and arguments are fixed:
  `fresh_preflight(CodexRegistrationPortRequest)`,
  `add_marketplace(CodexRegistrationPortRequest)`,
  `add_plugin(CodexRegistrationPortRequest)`, and
  `prove(CodexRegistrationProofRequest)`. The proof return is the integrated
  `CodexRegistrationProof`; no parallel receipt/proof algebra is allowed.
- Admission inspects only raw class dictionaries across the MRO and immutable
  function code/default metadata. It accepts only plain instance functions
  with exactly `self` plus one required request. It must not use candidate
  `getattr`/`hasattr`, `inspect.signature`, descriptor resolution, annotations,
  wrapper metadata, defaults, variadics, keyword-only arguments, properties,
  static methods or class methods.
- A private factory token is the only construction authority for the frozen
  capability. Its public metadata contains only `ADMITTED` and literal
  operation count `4`; serialization, repr, errors and handoff never expose
  bound functions or raw absolute paths.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `A1` | Exact request construction and `revalidate_registration_port_request` accept one fully bound value. Cross every root field with missing, `None`, empty/whitespace where textual, list, dict and plain-object substitutions; all return `INVALID_REQUEST` before equality, serialization or caller trap invocation. Source/preflight mismatch is explicitly rejected. |
| `A2` | The three result validators rebuild exact accepted/rejected preflight, marketplace success, plugin success and command-failure envelopes against the expected request. Wrong operation target, cross-request/attempt/version/locator/digest/auth values and recursively malformed nested fields return the exact finite value reason. Ephemeral observed absolute add paths exist only inside typed add observations. |
| `A3` | One valid adapter with the four exact methods is admitted without executing a method. Capability metadata is exactly `ADMITTED / 4`; direct/forged construction and copied token attempts fail. |
| `A4` | Null/text/container candidate, missing method, property, static/class method, non-function, zero/two request parameters, defaults, variadics and keyword-only forms return one finite `INVALID_PORT` reason with zero caller code, descriptor, annotation or representation trap invocation. Inherited plain methods remain admissible. |
| `A5` | Candidate/metaclass `__getattribute__`, descriptor `__get__`, annotations, signature/default wrapper and MRO/dictionary trap probes prove admission does not dynamically resolve or execute caller members. `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` traps remain uninvoked. |
| `A6` | The new module imports only integrated contracts. It does not change or call 05A, 05B1, 05B2, 05B3A/B1/C or 05S4; no live/staging effect, target-project path, raw output, Secret, `Any`, `type: ignore`, broad catch, optional/`None` port or historical-source reuse is present. |
| `A7` | First red is exact missing-module failure. Independently reverse request/source binding, wrong-target rejection, descriptor-free admission and private construction authority; all four isolated mutations turn committed tests red and are restored. Focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff and tracked/ignored/cache checks pass. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_port.py`.
2. New `tests/test_codex_registration_port.py`.
3. Export-only `library/local_orchestration/__init__.py`.

The implementation return is one exact-scope implementation commit followed by
one `doc/WorkProgressReport.md`-only handoff. No dependency edit, new worktree,
cross-lane read, review, integration, downstream dispatch, push, release or
deployment is authorized.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4A-01` |
| Handoff | `hnd_local_orchestration_install_05b4a_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4a_20260812` / `rcpt_local_orchestration_install_05b4a_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4a-20260812` / `q-local-orchestration-install-05b4a-20260812` |
| Side context | `scx-local-orchestration-install-05b4a-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; create only branch `codex/implementation-codex-registration-port-05b4a` from the later exact dispatch registry commit. |
| Return | Exact-scope implementation commit, then WPR-only handoff reserved as PRG-20260812-193. |
