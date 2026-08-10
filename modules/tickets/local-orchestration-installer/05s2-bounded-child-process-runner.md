# 05S2 — Bounded Child-Process Runner

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / verification support only |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `APPROVED / INTEGRATION_AUTHORIZED` |
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

- A strict request owns a NUL-free absolute executable locator, immutable
  argument vector, exact existing working directory beneath the supplied 05S1
  lease, the exact six-entry 05S1 overlay, a bounded positive run timeout and a
  distinct bounded positive termination timeout. Validation completes before
  process effects.
- Request construction and `run` admission both revalidate live ownership.
  The exact root, marker, five declared children, six overlay locators and cwd
  must still bind the same lease, resolve beneath the exact root and be
  non-reparse filesystem objects. A physical junction substitution before or
  after request construction fails before the process port is called.
- The effective argv is exactly `(executable, *original_arguments)`. Execution
  uses `shell=False`, the exact working directory and the supplied environment;
  no parent value is copied and no executable name is resolved through PATH.
- Results form a finite discriminated union with no `None` placeholder:
  success, nonzero exit, confirmed timeout-after-start, termination failure
  after start, executable unavailable before start, access denied before start
  and generic launch failure before start. `TERMINATION_FAILED` carries one
  exact reason from `KILL_OS_ERROR`, `REAP_TIMEOUT` or `REAP_OS_ERROR` and an
  `UNCONFIRMED` child state; it is never folded into pre-start launch failure.
- Windows launch classification uses concrete evidence: unavailable is only
  WinError 2/3, access denied is WinError 5, and every other pre-start
  `OSError` (including the independently probed WinError 206 oversized argv)
  is generic launch failure. A `FileNotFoundError` class alone is insufficient.
- The runner receives one required, non-optional typed process port; the
  production binding is a concrete `subprocess` port and tests may inject a
  strict in-memory port only for otherwise non-deterministic kill/reap errors.
  After the run timeout, the runner issues one kill and a wait bounded by the
  distinct termination timeout. Only successful bounded reap returns confirmed
  timeout; kill error, cleanup wait timeout or cleanup wait error returns the
  matching termination-failure reason without leaking an exception. The
  physical fixture still proves normal timeout termination beyond its scheduled
  late-write deadline. Raw stdout/stderr is discarded at the port boundary.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S2-02`

Revision 01 remains immutable evidence for review `8d1767d`; revision 02 changes
only the four batched CR-120..CR-123 gaps below. It does not change the ticket's
generic process-only outcome or authorize 05S3 behavior.

| ID | Process-only acceptance |
| --- | --- |
| `P1` | Exact NUL-free executable and argv reach the generic fixture with `shell=False`; no command string or PATH lookup is accepted and malformed locators fail before the process port. |
| `P2` | Immediately before start, the root, marker, children, overlay and cwd still prove exact live non-reparse ownership by the same 05S1 lease. The child receives only that mapping; the parent environment and filesystem remain unchanged outside the environment root. |
| `P3` | Success, finite nonzero exit, confirmed timeout, typed termination failure, unavailable executable, access denial and generic launch failure map to distinct strict results. Normal timeout kills and reaps within the cleanup bound; failed kill/reap returns one finite unconfirmed reason. |
| `P4` | Observation records actual executable, original/effective argv, exit/result and whether a child started. It records no stdout/stderr content beyond bounded fixture metadata and no absolute path enters durable handoff evidence. |

## Finite TDD matrix

| Cell | Required first-red and green assertion |
| --- | --- |
| `T1` | Relative/NUL executable, command string, malformed argv, foreign/outside cwd, non-exact overlay and invalid run/termination timeout each fail before the process port. Constructing a valid request and then physically replacing its cwd by a junction also fails at `run` admission without an external write. |
| `T2` | A real absolute Python executable runs the deterministic fixture inside one 05S1 root. Fixture evidence proves exact arguments, cwd and six overlay keys/values. Physical junction substitutions before and after request construction are rejected; parent environment and bytes outside the root remain unchanged. |
| `T3` | Real success, nonzero and confirmed timeout are distinct. The committed timeout assertion waits beyond the fixture's scheduled late-write deadline. Missing executable, directory executable and oversized argv retain WinError 2/3, 5 and 206 mappings. A strict typed process port separately proves kill error, post-kill wait timeout and post-kill wait error map to the three named termination-failure reasons with no unbounded wait or leaked exception. |
| `T4` | Every union member records exact invocation and started/not-started truth; confirmed timeout has an exit code, while termination failure has a named unconfirmed reason and no optional placeholder. Every physical case restores any junction, tears down its exact 05S1 root and leaves zero staging roots, external writes or late child residue. |

### CodeReview.md §2.1 interception map

| Defect class | Disposition |
| --- | --- |
| 1 path prefix / physical redirection | Applicable; P2/T1/T2 require exact physical junction rejection before the process port. |
| 2 null / empty representations | No nullable field exists; empty argv is the one explicitly valid empty container, while missing, blank and NUL-bearing scalar elements remain strict T1 boundary failures. |
| 3 permission bypass | Not applicable: this ticket owns no protected resource or authorization entrypoint. |
| 4 token parsing/comparison | Not applicable: no credential or token is accepted. |
| 5 result-code consistency | Applicable; P3/T3 enumerate every pre-start, confirmed-timeout and unconfirmed-termination result. |
| 6 exception propagation | Applicable; P1/T1 and P3/T3 require malformed input and kill/reap failures to remain pre-effect validation or finite typed observations. |
| 7 test truthfulness | Reviewer must map P1-P4 to T1-T4, reverse-check the corrected boundary, and verify the committed wait exceeds the fixture deadline. |

## Evidence and loop boundary

The revision-02 correction must record first-red evidence against submitted HEAD
`72ccfaa`, return one additive implementation commit covering only the four
authorized correction files (`contracts.py`, `runner.py`, `fixture_child.py`
when needed, and the test file), and then one docs-only handoff. The existing
`__init__.py`, all 05S1 files and prior commits remain immutable.
The exact focused command is
`python -B -m unittest tests.test_bounded_child_process_runner -v`; the full
command remains `python -B -m unittest discover -s tests -v`. Strict full-tree
mypy uses a repository-external cache which is removed after use. The final
readback checks clean Git state, zero repository caches, zero new
`johnny-stage-env-*` roots and no late timeout sentinel.

The independent reviewer runs the same commands from a fresh export and repeats
the physical junction, NUL, WinError 5/206 and extended timeout probes plus the
typed termination-failure matrix. This is the one owner-authorized correction
review. Any blocker stops with no further correction dispatch, new branch/
worktree or 05S3. 05S3 remains blocked until 05S2 approval and guarded
integration.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05s2_r02_20260811` |
| Allocation | `aln_local_orchestration_install_05s2_r02_20260811` |
| Receipt | `rcpt_local_orchestration_install_05s2_r02_20260811` |
| Correlation / question | `corr-local-orchestration-install-05s2-r02-20260811` / `q-local-orchestration-install-05s2-r02-20260811` |
| Authority | Owner authorization in this task; override `OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01`; program authority `PRG-20260809-042`; review `8d1767d` |
| Ticket-doc baseline | This revision-02 refreeze commit; its exact SHA is bound by the separate correction-handoff record. |
| Worktree / branch | Reuse only `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` on existing branch `codex/implementation-bounded-child-process-runner-05s2` at exact HEAD `72ccfaab44429749c61a77177567deb81d7f29dc`. Do not create or switch a branch or worktree. |
| Historical-source boundary | Original implementation `52d7455`, handoff `72ccfaa`, review `8d1767d` and rejected combined 05S history remain immutable evidence. The correction is additive; no reset, amend, rebase, force, cherry-pick or source copy. |
| Required return | One additive implementation correction commit for CR-120..CR-123, exact revision-02 P1-P4/T1-T4 verification and clean readback, followed by one docs-only `doc/WorkProgressReport.md` handoff commit. No review, merge, downstream dispatch or host mutation. |

The previous allocation/receipt remain closed. The new revision-02 identifiers
exist only to prevent replay and must bind this ticket, owner, existing branch,
exact `72ccfaa` implementation HEAD, ticket-doc baseline and separate handoff-doc
commit. Any mismatch is `HALT` and grants no implementation authority.

## Independent review disposition

Implementation `52d7455` and docs-only handoff `72ccfaa` received
`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` in
`doc/reviews/local-orchestration-installer/05s2-bounded-child-process-runner-code-review.md`.
CR-120 proves a physical working-directory junction redirects a successful
child write outside the owned root. CR-121 records an accepted NUL executable
that leaks `ValueError`. CR-122 records a non-truthful late-sentinel timing
assertion. CR-123 is a control-plane ticket defect: the frozen union omitted a
finite started-child termination-failure outcome and cleanup budget. The
original allocation is released and its receipt remains closed against replay.
Owner override `OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01` subsequently
authorizes exactly the revision-02 refreeze and one additive same-branch
correction defined above; it does not reopen revision 01 or permit a second
correction.

## Revision-02 final review disposition

Correction `34babbd2ff200715c350b4a46c99d47db84de7e8` and docs-only handoff
`c324c52669cfa16c57433e0f0cf14ee2b00b0d69` close CR-120..CR-123, but the
final independent review records CR-124 as a `TICKET_DEFECT`. The required
`StartedChildProcess.wait()` port permits a concrete `OSError`; when the first
run wait raises that error, `runner.py:91-92` routes it through the timeout
path. An independent strict-port probe then killed and bounded-reaped the child
and returned `TIMEOUT_AFTER_START`, even though no `TimeoutExpired` occurred.
The frozen result union and TDD matrix do not contain an exact state for this
started-child observation failure, so P3/T3 result truth is not closed.

The one correction authorized by
`OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01` is consumed. This ticket is
stopped without a second correction, replacement branch/worktree, integration
or 05S3 dispatch. All submitted commits remain immutable evidence.

## Revision-03 owner-authorized closure — `CLOSURE-LOCAL-INSTALL-T05S2-03`

Owner authorization in this task creates
`OVR-LOCAL-INSTALL-T05S2-R03-20260811-01` and refreezes only CR-124. Revision
01 and revision 02 remain immutable. The generic runner outcome, test-only
environment and all earlier P1/P2/P4 behavior are unchanged.

### Finite started-child wait contract

- A first run wait that raises `subprocess.TimeoutExpired` remains the exact
  `RUN_TIMEOUT` trigger. Successful kill plus bounded reap returns
  `TIMEOUT_AFTER_START`.
- A first run wait that raises `OSError` is the distinct
  `RUN_WAIT_OS_ERROR` trigger. Successful kill plus bounded reap returns
  `WAIT_FAILED_AFTER_START`, never `TIMEOUT_AFTER_START`.
- `WAIT_FAILED_AFTER_START` is a strict union member with exact invocation,
  `STARTED`, `CONFIRMED_TERMINATED`, fixed reason `WAIT_OS_ERROR` and the exit
  code returned by bounded reap. It contains no raw exception or optional
  placeholder.
- If kill or bounded reap fails after either trigger, the existing
  `TERMINATION_FAILED` result remains `STARTED / UNCONFIRMED` with exact reason
  `KILL_OS_ERROR`, `REAP_TIMEOUT` or `REAP_OS_ERROR`, and now also carries the
  required trigger `RUN_TIMEOUT` or `RUN_WAIT_OS_ERROR`.
- No first-wait `OSError` may escape, be classified as a launch failure, or be
  reported as a confirmed timeout. Every path performs at most one kill and
  one reap bounded by the distinct termination timeout.

### Revision-03 acceptance delta

| ID | Exact acceptance |
| --- | --- |
| `P3-R03` | Timeout and first-wait OS error are distinct finite started-child results; confirmed timeout exists only after `TimeoutExpired` plus successful bounded cleanup. |
| `T3-R03-A` | A strict typed port raises first-wait `OSError`, then returns exit 137 from bounded reap; result is `WAIT_FAILED_AFTER_START / STARTED / CONFIRMED_TERMINATED / WAIT_OS_ERROR`, with run and termination timeout values observed separately. |
| `T3-R03-B` | For each trigger (`RUN_TIMEOUT`, `RUN_WAIT_OS_ERROR`), kill error, reap timeout and reap OS error return the exact `TERMINATION_FAILED` reason and required trigger with `UNCONFIRMED` child state. |
| `T3-R03-C` | Reverse assertion proves no first-wait `OSError` case returns `TIMEOUT_AFTER_START`, launch failure or an exception; normal real timeout and all revision-02 physical tests remain green. |

### Revision-03 implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05s2_r03_20260811` |
| Allocation | `aln_local_orchestration_install_05s2_r03_20260811` |
| Receipt | `rcpt_local_orchestration_install_05s2_r03_20260811` |
| Correlation / question | `corr-local-orchestration-install-05s2-r03-20260811` / `q-local-orchestration-install-05s2-r03-20260811` |
| Authority | Owner authorization in this task; override `OVR-LOCAL-INSTALL-T05S2-R03-20260811-01`; program authority `PRG-20260809-042`; final revision-02 review `5b4476c` / CR-124 |
| Submitted HEAD | Existing branch `codex/implementation-bounded-child-process-runner-05s2` at `c324c52669cfa16c57433e0f0cf14ee2b00b0d69` in the sole implementation worktree |
| Exact correction scope | `tests/staging/process_runner/contracts.py`, `tests/staging/process_runner/runner.py`, `tests/test_bounded_child_process_runner.py`, then a separate docs-only `doc/WorkProgressReport.md` handoff |
| Frozen boundary | No fixture, 05S1, production-library, Codex/plugin/install/target-project/live-host change; no new branch/worktree, reset, amend, rebase, force, merge, cherry-pick, stash or push |
| Return / stop | One additive implementation commit and one docs-only handoff, followed by one independent review. Any blocker stops without another correction or 05S3 dispatch. |

The ticket-doc baseline is this revision-03 refreeze commit; its exact SHA is
bound by the separate correction-handoff commit. Admission mismatch or replay
is `HALT` before any implementation write.
