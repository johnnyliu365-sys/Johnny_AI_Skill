# 05S Codex Lifecycle Contract Staging - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05s-codex-lifecycle-contract-staging` |
| Result | `CHANGES_REQUESTED / REVISION_02_CORRECTION_PREPARED` |
| Reviewer | Codex / current `main` worktree |
| Reviewed branch | `codex/implementation-codex-lifecycle-staging-05s` |
| Boundary | Control baseline `3047b4b`; implementation `18b99de`; docs-only handoff `2bed349` |
| Reviewed closure | `CLOSURE-LOCAL-INSTALL-T05S-01` / `S1..S7`, `E01..E08` |

## Independent verification

The implementation and handoff have valid ancestry, the implementation changes
only the six authorized test-support files, the handoff changes only
`doc/WorkProgressReport.md`, and the submitted implementation worktree is clean.
Production `library/local_orchestration` has no diff.

The first independent focused run used a disposable exported checkout. All eight
tests errored before their scenario because the test derives a fixed adjacent
control-worktree name and `CodexLifecycleSandbox.provision` resolves that path
with `strict=True`. Each failed provision created its temporary root before this
validation; the run left thirteen `codex-lifecycle-stage-*` directories. After
the reviewer created the missing implied sibling directory solely inside the
review temp parent, focused `8/8` passed and the exact full command
`python -m unittest discover -s tests -v` passed `180/180`. The default
`python -m unittest discover -v` discovered zero tests, so the handoff's phrase
“full unittest discovery” is not an exact replay command.

| Check | Result / evidence |
| --- | --- |
| Ancestry / scope / diff | PASS: `3047b4b -> 18b99de -> 2bed349`; six authorized Python files, then one docs-only file; `git diff --check` passed. |
| Relocatable focused run | FAIL: independent checkout produced `13` provisioning errors and `13` orphan roots until an assumed sibling directory was manually created. |
| Focused / full after topology workaround | PASS with workaround: focused `8/8`; exact full command `python -m unittest discover -s tests -v` `180/180`. |
| Strict typing | PASS independently: `mypy --strict --explicit-package-bases --no-incremental` passed `88` source files using a repository-external cache. |
| Downstream command-port compatibility | FAIL: `isinstance(sandbox, CodexCommandPort)` is `False`; the harness accepts command tails through `run`, has no finite timeout, and does not replace the executable token of a full Codex argv. |
| Official add/remove protocol | FAIL: marketplace add/remove emit nested list-style entries and plugin add/remove emit nested list-style entries. Required `marketplaceName`, `installedRoot`, `alreadyAdded`, `installedPath` and exact removal DTOs are absent. |
| Persisted truth | FAIL: reviewer probes accepted an owned plugin plus payload without an owned marketplace, an invalid semantic version, and a blank foreign record; all returned exit `0` instead of `STATE_INVALID`. |
| Foreign-state evidence | FAIL: E06 seeds only same-name collisions plus a sentinel. It does not seed unrelated marketplace/plugin records and carry them byte/value-identically through success, post-effect failure, compensation and retry. |
| Teardown / resource safety | FAIL: validation after `mkdtemp` leaks roots; child execution has no timeout; provision/initialization exceptions have no exact cleanup guard. |

## Closure mapping

| Item | Result | Independent result |
| --- | --- | --- |
| `S1` | FAIL | Root placement is bounded, but fixed sibling topology prevents independent checkout/CI execution and invalid forbidden-root input leaks a root. The required seven path-boundary cases are absent. |
| `S2` | FAIL | A real child process and persisted files exist, but the harness is not a drop-in command port and its add/remove JSON is incompatible with the official downstream contract. |
| `S3` | FAIL | Fresh reads occur, but recursive invariants are incomplete: invalid identity/foreign fields and plugin-without-marketplace state can produce success. |
| `S4` | PARTIAL | Pre/post add and pre-remove faults retain the expected basic residue, but execution is unbounded and process/provision exceptions are not finite or leak-free. |
| `S5` | FAIL evidence | Same-name collision preservation is covered; unrelated marketplace/plugin preservation across the required lifecycle paths is not. |
| `S6` | PARTIAL | Synthetic Git snapshots pass, but the recorded “shim executable” is argv element 2 while the actual executable is `sys.executable`; the harness does not implement the production command-port boundary. |
| `S7` | FAIL | Submitted green evidence is topology-dependent, the full command is not stated exactly, and failed provisioning leaves roots. |

## CodeReview.md mandatory checks

- **Clear strong types:** PARTIAL. Named immutable models are present, but the
  copied child models drift from the controller models: the child omits semantic
  version and nonblank foreign-record validation, producing false success.
- **Existing coding conventions:** PASS. Python 3.11, Pydantic, argument vectors
  and `shell=False` follow the repository's current test-support conventions.
- **Logic correctness:** FAIL due protocol incompatibility and false-success
  acceptance of incoherent persisted state.
- **Edge cases:** FAIL due missing path/null matrices, unbounded execution and
  non-exception-safe provisioning.
- **Security / performance:** FAIL resource isolation because a normal
  invalid topology leaks temporary roots. No live Codex, target-project, network,
  Secret or user-state mutation was observed.
- **Test coverage / smoke:** FAIL closure despite workaround-green `180/180`.
  Test names overclaim unrelated-state and recursive-state coverage.
- **Dependency reasonableness:** PASS. No dependency was added, upgraded or
  duplicated, and production dependency files have no diff.
- **Project specification:** FAIL because the result cannot yet serve as the
  isolated oracle for 05B/05C.
- **Path-prefix boundary (CodeReview.md §2.1 class 1):** FAIL ticket design. The
  required equal, prefix-plus-character, trailing slash, case, encoded,
  traversal and empty cases were not frozen or tested.
- **Authority bypass (class 3):** FAIL. Persisted `owned=true` plus coherent
  payload can bypass the required marketplace ownership relation.
- **Test truthfulness (class 7):** FAIL. E06 does not exercise unrelated
  marketplace/plugin entries; E05 does not cover several accepted malformed or
  incoherent states; the default discovery command runs zero tests.

## Batched findings

1. **CR-105 — `TICKET_DEFECT`, S1/S3/S7.** Closure revision 01 omitted the
   mandatory seven path cases, the complete null/empty/whitespace/container
   state cases, exact exception propagation assertions and exact full-suite
   command. Refreeze a finite revision-02 matrix before correction.
2. **CR-106 — `IMPLEMENTATION_DEFECT`, S2/S6.** `sandbox.py:146-160` exposes
   `run(command_tail)` rather than a `CodexCommandPort.execute(full_argv,
   timeout_seconds)` replacement. It has no timeout and records the interpreter
   separately from the claimed shim executable. Downstream adapter tests cannot
   inject this object directly.
3. **CR-107 — `IMPLEMENTATION_DEFECT`, S2.** `shim.py:230-249,282-360` emits
   custom nested mutation shapes instead of the official add/remove DTOs frozen
   by 05B. Strict downstream parsing will reject every successful mutation.
4. **CR-108 — `IMPLEMENTATION_DEFECT`, S1/S7.** `sandbox.py:48-54,65-77`
   creates a root before resolving forbidden roots and has no failure cleanup.
   Independent replay left thirteen orphan roots. The fixed adjacent worktree
   name in `test_codex_lifecycle_staging.py:10-12` also makes tests dependent on
   one developer's directory topology.
5. **CR-109 — `IMPLEMENTATION_DEFECT`, S3.** Controller and child state models
   are not equivalent, and `_assert_state_truth` does not require an owned
   plugin to have its exact owned marketplace. Invalid semantic version, blank
   foreign record and plugin-without-marketplace probes all returned success.
6. **CR-110 — `EVIDENCE_DEFECT`, S5/E06.** The committed E06 test covers only
   same-name collision and one sentinel; it does not preserve unrelated
   marketplace/plugin records through success, post-effect failure,
   compensation and retry as claimed.
7. **CR-111 — `EVIDENCE_DEFECT`, S7.** The handoff gives counts but not the
   exact full-suite command. `python -m unittest discover -v` runs zero tests in
   this repository; only the unstated `-s tests` form reproduces `180/180`.

## Conclusion

`CHANGES_REQUESTED`. This is the single initial review for 05S. All discovered
blocking findings are batched above. The control plane refreezes closure
revision 02 and permits one additive correction on the same ticket, task,
worktree, branch, allocation and receipt. No new branch/worktree, production
source change, downstream 05B/05C/04 dispatch, integration, live Codex action,
push, release or deployment is authorized.
