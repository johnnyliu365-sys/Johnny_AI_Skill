# 05S2 — Bounded Child-Process Runner

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / verification support only |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |
| Dependency | 05S1 independently approved and integrated by `504a3ec` |
| Implementation language | Python 3.11 |
| Implementation responsibility | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, in the sole implementation worktree after exact receipt admission |
| Acceptance responsibility | Independent control-plane reviewer in the control worktree; no implementation writes |
| Environment level | Test-owned 05S1 filesystem/process environment only; no live Codex, target project, package manager, installer or host registration |

## One outcome

Run one deterministic generic fixture process inside an integrated 05S1
environment with an explicit executable, argument vector, working directory,
child environment and finite timeout. Return a strict process observation. This
ticket knows nothing about Codex, plugins, marketplaces or installation state.

## Authorized scope

```text
tests/staging/process_runner/__init__.py
tests/staging/process_runner/contracts.py
tests/staging/process_runner/runner.py
tests/staging/process_runner/fixture_child.py
tests/test_bounded_child_process_runner.py
doc/WorkProgressReport.md       # separate docs-only handoff only
```

Integrated 05S1 files are read-only but may be imported. Production source is
read-only. Do not add Codex DTOs, plugin/marketplace state, registration,
installer logic, target-project access, a command string, PATH lookup, inherited
ambient environment, `Any`, `type: ignore`, an optional effect port or a broad
process-kill shortcut. Raw stdout/stderr content must not cross the runner
boundary or enter durable evidence.

## Frozen process contract

- A strict request owns an absolute executable locator, immutable argument
  vector, exact existing working directory beneath the supplied 05S1 lease,
  the exact six-entry 05S1 overlay and a bounded positive timeout. Validation
  completes before process effects.
- The effective argv is exactly `(executable, *original_arguments)`. Execution
  uses `shell=False`, the exact working directory and the supplied environment;
  no parent value is copied and no executable name is resolved through PATH.
- Results form a finite discriminated union with no `None` placeholder:
  success, nonzero exit, timeout-after-start, executable unavailable before
  start, access denied before start and generic launch failure before start.
- Windows launch classification uses concrete evidence: unavailable is only
  WinError 2/3, access denied is WinError 5, and every other pre-start
  `OSError` (including the independently probed WinError 206 oversized argv)
  is generic launch failure. A `FileNotFoundError` class alone is insufficient.
- Timeout must kill and wait for the one started child before returning. The
  deterministic fixture proves its observations through a file inside the
  owned environment root; the runner redirects raw stdout/stderr away and
  returns only typed executable/argv/result/start metadata.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S2-01`

| ID | Process-only acceptance |
| --- | --- |
| `P1` | Exact executable and argv reach the generic fixture with `shell=False`; no command string or PATH lookup is accepted. |
| `P2` | The child receives the explicit 05S1 mapping and owned working directory; the parent environment and filesystem remain unchanged outside the environment root. |
| `P3` | Success, finite nonzero exit, timeout, unavailable executable, access denial and generic launch failure map to distinct strict results; timeout terminates the owned child. |
| `P4` | Observation records actual executable, original/effective argv, exit/result and whether a child started. It records no stdout/stderr content beyond bounded fixture metadata and no absolute path enters durable handoff evidence. |

## Finite TDD matrix

| Cell | Required first-red and green assertion |
| --- | --- |
| `T1` | Relative executable, command string, malformed argv, foreign/outside working directory, non-exact overlay and invalid timeout each fail before child effects. Exact typed input preserves original and effective argv without coercion. |
| `T2` | A real absolute Python executable runs the deterministic fixture inside one 05S1 root. The fixture file proves exact arguments, working directory and six overlay keys/values; parent environment and bytes outside the root remain unchanged. |
| `T3` | Real success, real nonzero exit and real timeout are distinct. Timeout leaves no late completion sentinel. A missing absolute executable yields unavailable, an existing directory used as executable yields WinError 5/access denied, and an oversized real argv yielding WinError 206 maps to generic launch failure rather than unavailable. |
| `T4` | Every union member records exact executable, original/effective argv and started/not-started truth without optional placeholders or raw output. Every case tears down its exact 05S1 root and leaves zero new staging roots or child-completion residue. |

## Evidence and loop boundary

Implementation must record first-red evidence, return one implementation commit
covering only the five authorized Python files, and then one docs-only handoff.
The exact focused command is
`python -B -m unittest tests.test_bounded_child_process_runner -v`; the full
command remains `python -B -m unittest discover -s tests -v`. Strict full-tree
mypy uses a repository-external cache which is removed after use. The final
readback checks clean Git state, zero repository caches, zero new
`johnny-stage-env-*` roots and no late timeout sentinel.

The independent reviewer runs the same commands from a fresh export and repeats
the physical WinError 5/206 and timeout probes. Any blocking result stops at
`CONVERGENCE_REVIEW_REQUIRED`; it does not automatically authorize a correction,
new branch/worktree or 05S3. 05S3 remains blocked until 05S2 approval and
guarded integration.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05s2_20260811` |
| Allocation | `aln_local_orchestration_install_05s2_20260811` |
| Receipt | `rcpt_local_orchestration_install_05s2_20260811` |
| Correlation / question | `corr-local-orchestration-install-05s2-20260811` / `q-local-orchestration-install-05s2-20260811` |
| Authority | Continuing owner instruction; program authority `PRG-20260809-042`; 05S1 integration `PRG-20260811-113` / `504a3ec` |
| Ticket-doc baseline | This ticket-freeze commit; its exact SHA is bound by the separate PRG-114 handoff record. |
| Worktree / branch | Reuse only `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`. From clean submitted 05S1 HEAD `e1087d3`, create exactly one new-ticket branch `codex/implementation-bounded-child-process-runner-05s2` at the exact handoff-doc baseline. Do not create another worktree. |
| Historical-source boundary | Rejected combined 05S commits `ca5754d`, `832b1dc` and `ccb55bd` remain immutable evidence; do not copy, cherry-pick or reuse their process-runner source/tests. Integrated 05S1 at `504a3ec` is the only staging dependency. |
| Required return | One implementation commit changing only the five authorized Python files, exact P1-P4/T1-T4 verification and clean readback, followed by one docs-only `doc/WorkProgressReport.md` handoff commit. No review, merge, downstream dispatch or host mutation. |

The dispatch prompt must bind this ticket, owner, handoff, allocation, receipt,
correlation, exact ticket-doc baseline and separate handoff-doc commit. Any
mismatch is `HALT` and grants no implementation authority.

## Independent review disposition

Implementation `52d7455` and docs-only handoff `72ccfaa` received
`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` in
`doc/reviews/local-orchestration-installer/05s2-bounded-child-process-runner-code-review.md`.
CR-120 proves a physical working-directory junction redirects a successful
child write outside the owned root. CR-121 records an accepted NUL executable
that leaks `ValueError`. CR-122 records a non-truthful late-sentinel timing
assertion. CR-123 is a control-plane ticket defect: the frozen union omitted a
finite started-child termination-failure outcome and cleanup budget. No
automatic correction, merge or 05S3 dispatch is authorized. The allocation is
released and the receipt is closed against replay.
