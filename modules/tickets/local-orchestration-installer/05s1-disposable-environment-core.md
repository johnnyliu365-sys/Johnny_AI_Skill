# 05S1 — Disposable Environment Core

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / verification support for AC-02, AC-03, AC-06, AC-07 and AC-08 |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `IN_PROGRESS / DISPATCH_AUTHORIZED` |
| Dependency | Ticket 05A integrated by `b22c6c4`; rejected parent 05S is immutable evidence only |
| Implementation responsibility | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, in the sole implementation worktree after exact receipt admission |
| Acceptance responsibility | Control-plane reviewer in the control worktree; the reviewer may execute and inspect but may not patch implementation |
| Environment level | Test-owned filesystem and process-environment profile; not Windows Sandbox, VM, container, live Codex or package staging |

## One outcome

Create and destroy one uniquely owned disposable environment. Given one strict
opaque `EnvironmentOwnerId`, provision returns typed relative/absolute locators
for an exact temporary root and its profile, local-app-data, roaming-app-data,
temp and Codex-home children.
Teardown removes only that marker-bound root. This ticket executes no child
process and models no Codex command or plugin state.

## Authorized scope

```text
tests/staging/environment_core/__init__.py
tests/staging/environment_core/contracts.py
tests/staging/environment_core/environment.py
tests/test_disposable_environment_core.py
doc/WorkProgressReport.md       # separate docs-only handoff only
```

Production source is read-only. Do not add a CLI shim, subprocess call, Codex
DTO, persisted marketplace/plugin model, SemVer policy, foreign-state fixture,
Git repository fixture, installer execution, target-project access, broad
delete, `Any`, `type: ignore` or optional effect port.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S1-01`

| ID | Environment-only acceptance |
| --- | --- |
| `E1` — exact provision | An allocator accepting only a strict opaque `EnvironmentOwnerId` creates one unique direct child of the resolved OS temp directory. A strict marker binds that owner, the generated environment ID and exact root. All declared child directories are beneath that root and exist. |
| `E2` — no ambient mutation | Provision returns a fixed-key environment overlay without changing the parent process environment. Only `USERPROFILE`, `LOCALAPPDATA`, `APPDATA`, `TEMP`, `TMP` and `CODEX_HOME` appear, and every value is owned beneath the root. No parent value is copied by this ticket. |
| `E3` — exact teardown | Teardown revalidates the root, generated ID and marker, refuses a missing/mismatched marker or reparse escape, and removes exactly the owned root without following an external link. Repeated teardown returns one finite already-absent result. |
| `E4` — exception safety | Finite faults after root creation and after marker creation leave zero new environment roots. Invalid typed values fail before filesystem effects. A successful lifecycle ends with an absent exact root and unchanged parent environment. |

## Finite TDD matrix

| Cell | Required first-red and green assertion |
| --- | --- |
| `T1` | Provision two distinct owner IDs: generated IDs and roots differ; both roots are direct OS-temp children and neither is inside either repository worktree. Empty, malformed and replayed owner values fail before effects. |
| `T2` | Parent environment snapshot is byte/value-identical before and after provision/teardown; returned child mapping contains only declared keys and owned values. |
| `T3` | Missing marker, wrong marker, root symlink/reparse and child escape each block deletion; an intact root tears down and replay reports already absent. |
| `T4` | Fault after root and fault after marker each produce zero residual `johnny-stage-env-*` roots; unrelated sibling bytes remain unchanged. |

## Evidence and loop boundary

Implementation must return one implementation commit and one docs-only handoff.
The exact focused command is
`python -B -m unittest tests.test_disposable_environment_core -v`; the exact
full command is `python -B -m unittest discover -s tests -v`. Strict full-tree
mypy uses a validated repository-external cache which is removed after use.
Final evidence checks only owned environment-root absence and clean Git state;
it does not require Python to avoid its normal cache behavior when `-B` is not
used.

The reviewer batches all findings in one review. Any blocking result stops at
`CONVERGENCE_REVIEW_REQUIRED`; it does not automatically dispatch a correction,
create another branch or expand this closure. 05S2 cannot start until 05S1 is
independently approved and safely integrated.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05s1_20260811` |
| Allocation | `aln_local_orchestration_install_05s1_20260811` |
| Receipt | `rcpt_local_orchestration_install_05s1_20260811` |
| Correlation / question | `corr-local-orchestration-install-05s1-20260811` / `q-local-orchestration-install-05s1-20260811` |
| Authority | Owner instruction to decompose and establish the environment first; decomposition record `PRG-20260811-106`; continuing authority `PRG-20260809-042` |
| Ticket-doc baseline | `3f685a9` |
| Worktree / branch | Reuse only `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`. From clean state, create exactly one new-ticket branch `codex/implementation-disposable-environment-core-05s1` at the exact reviewed handoff baseline. Do not create another worktree. |
| Historical-source boundary | Branch `codex/implementation-codex-lifecycle-staging-05s` and commits `ca5754d`, `832b1dc`, `ccb55bd` are immutable rejected evidence. Do not copy, cherry-pick or reuse their source/tests. |
| Required return | One implementation commit changing only the four authorized Python files, exact E1–E4/T1–T4 verification and clean readback, followed by one docs-only `doc/WorkProgressReport.md` handoff commit. No review, merge, downstream dispatch or host mutation. |

The dispatch prompt must bind this ticket, owner, handoff, allocation, receipt,
correlation, ticket-doc commit and the separate handoff-doc commit. A mismatch
is `HALT` and grants no implementation authority.
