# 05S4 — Codex Lifecycle Oracle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07 and AC-08 lifecycle seam |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `IN_PROGRESS / IMPLEMENTATION_DISPATCHED` |
| Dependency | Satisfied: 05S1, 05S2 and 05S3 independently approved and integrated by `504a3ec`, `6e24e06` and `43a1639` |
| Implementation language | Python 3.11 |
| Implementation responsibility | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, in the sole implementation worktree after exact receipt admission |
| Acceptance responsibility | Independent control-plane reviewer; no implementation writes |
| Environment | Disposable 05S1 environment and real 05S2 child only; no live Codex, target-project, installer, network, Secret, push, release or deployment |
| Dispatch binding | `hnd_local_orchestration_install_05s4_20260811` / `aln_local_orchestration_install_05s4_20260811` / `rcpt_local_orchestration_install_05s4_20260811` / `corr-local-orchestration-install-05s4-20260811` / `q-local-orchestration-install-05s4-20260811` |
| Ticket-doc baseline | `85ac8a015ca2a10c7ea6b502b7ccecb86ac11f81` |

## One outcome

Add a persisted test-only oracle behind the integrated environment, runner and
protocol fixture. Fresh state plus physical owned payloads answer exact
add/list/remove/absence queries. This ticket supplies deterministic truth to
future 05B/05C tests; it does not implement their transaction, compensation or
receipt logic.

## Exact source and composition boundary

Only these new paths may be implemented:

- `tests/staging/codex_lifecycle_oracle/__init__.py`
- `tests/staging/codex_lifecycle_oracle/contracts.py`
- `tests/staging/codex_lifecycle_oracle/oracle.py`
- `tests/staging/codex_lifecycle_oracle/oracle_child.py`
- `tests/staging/codex_lifecycle_oracle/protocol_runner.py`
- `tests/test_codex_lifecycle_oracle.py`

05S1, 05S2 and 05S3 source and tests are read-only dependencies. The composition
must supply one required, non-null `CodexLifecycleOracleRunner` implementing the
existing 05S3 `ProcessRunnerPort`. It validates the exact 05S3 request and then
uses the real integrated `BoundedChildProcessRunner` to invoke
`oracle_child.py`; it must return the real resulting observation, never forge
the original invocation. The oracle child reads one fixed strict command file,
freshly reads one fixed strict state file plus physical payloads below the
current `EnvironmentLease.codex_home`, and writes only the existing fixed 05S3
response file. No response value may be passed through the runner request,
queued in memory or synthesized by the parent.

The state/command filenames and owned payload subtrees are constants inside the
lease. Dynamic absolute paths, caller-selected roots, symlinks/reparse points,
historical rejected 05S source, production Codex adapters and optional effect
ports are prohibited. Command and response files are removed after each
operation; state and owned payloads persist only until final absence proof and
05S1 teardown.

Required strong types include strict frozen command/state/identity/digest
models, a finite `OracleBlockReason`, a finite `OracleChildExitCode` mapping
and a closed completed/blocked result union. Marketplace and plugin identities
must bind every list/add/remove field needed by the integrated protocol DTOs.
State records carry only lease-relative owned locators and SHA-256 digests; they
cannot carry an absolute path, URI, target-project locator, raw Context, Secret
or nullable ownership authority. A nonzero oracle-child exit remains the
protocol-facing `PROCESS_FAILED` result, while its exact finite exit-code
mapping supplies the internal test-only reason without exception text.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S4-01`

| ID | Oracle-only acceptance |
| --- | --- |
| `O1` | Explicit initialization of a newly provisioned exact lease atomically creates the empty strict state; fresh child runs then report empty marketplace/plugin lists. Exact marketplace add followed by exact plugin add creates the declared physical payloads and state, and fresh list child runs return the matching integrated protocol DTOs. |
| `O2` | Exact plugin removal before exact marketplace removal returns the matching remove DTOs. Subsequent fresh list child runs and physical readback prove both exact-owned identities and payloads absent before environment teardown. |
| `O3` | One coherent unrelated record and one coherent same-name foreign record, each with its own physical payload/digest proof, remain byte/value-identical across every owned add/remove operation and cannot authorize owned removal. |
| `O4` | Missing state after initialization, top-level extra field, explicit null collection, duplicate marketplace identity, duplicate plugin identity, state-present/file-absent, file-present/state-absent, stale digest, wrong file kind and reparse topology each return one finite named block/reject result before a false list or absence claim. |
| `O5` | Every list and absence result is produced by a new bounded child after fresh state and physical-file validation. The parent request selects only the surface/action; it cannot supply list entries, absence truth, an absolute path or a queued response. |
| `O6` | Named filesystem/process failures never report success or leak a raw ordinary exception; no command/response residue remains after an operation. Final absence proof precedes 05S1 teardown, which leaves no owned root while unrelated external bytes and both representative target-repository byte/porcelain snapshots remain unchanged. |

## TDD matrix and defect interception

Each behavior starts with a recorded first-red focused test before source is
added. The focused module must cover every cell below.

| CodeReview.md class | Required 05S4 cases |
| --- | --- |
| 1. Path-prefix boundary | For state, command and every owned payload locator: exact match, one-extra-character sibling, trailing separator, casing variation, URL-encoded input, `..` traversal and empty locator. Only the exact lease-relative ordinary-file/ordinary-directory topology may reach a filesystem effect. |
| 2. Null / empty / container | For command identity and persisted records: explicit null, omitted field, empty string, whitespace, empty list and empty object. All are invalid; none is equivalent to absence of the entire freshly provisioned state file. |
| 3. Authority bypass | Direct copied/tampered state, an exact-name foreign record, and indirect list/remove through the protocol runner all require the same lease owner, environment ID, relative locator and digest proof. No state record or product name alone authorizes deletion. |
| 4. Token format/comparison | No token or credential exists in this ticket. A source sentinel must reject token/secret fields and equality-based credential logic in the six authorized paths. |
| 5. Error-code consistency | Each O4/O6 failure asserts the exact unique internal `OracleBlockReason` and `OracleChildExitCode` mapping; the protocol-facing result remains one existing strict accepted/rejected shape and never leaks exception text or absolute paths. |
| 6. Exception propagation | Inject each filesystem read/write/replace/remove/digest failure and process-runner failure. Ordinary `OSError`/`ValueError` cells return the frozen finite result with truthful side-effect state; `MemoryError`, `KeyboardInterrupt` and `SystemExit` are not broadly caught or misclassified. |
| 7. Test truth | Map O1–O6 one-to-one to named tests. Reverse-mutate at least fresh-state reread, physical-digest validation, foreign preservation and final absence proof; each matching test must fail, then restore exact bytes before final verification. |

The smoke path is one real serial lifecycle:
`initialize → empty list → marketplace add → plugin add → fresh lists → plugin remove →
marketplace remove → fresh empty lists/physical absence → teardown`. It uses a
real subprocess and exact 05S1 filesystem boundaries, but never invokes or
modifies the user's live Codex installation.

## Completion, evidence and return

- Focused and full unittest suites, strict mypy over every repository Python
  file, in-memory compile, source/scope sentinel and `git diff --check` must
  pass. Repository `.mypy_cache`, `.pytest_cache`, `__pycache__`, fixed
  command/response files and `johnny-stage-env-*` roots must read back absent.
- Record the first-red test names/reasons, O1–O6 mapping, real-child invocation,
  physical before/after evidence, reverse mutations, target-repository
  byte/porcelain snapshots and clean tracked/ignored readback.
- Return one implementation commit containing only the six authorized Python
  paths, then one docs-only commit changing only `doc/WorkProgressReport.md`.
  The implementation owner makes no review, integration, 05B or 05C decision.

Fault timing, compensation, current-attempt authority and receipts remain
exclusively with 05B/05C. Any blocking review stops without automatic
correction. Only an independently approved and integrated 05S4 permits the
control plane to refreeze 05B and 05C.
