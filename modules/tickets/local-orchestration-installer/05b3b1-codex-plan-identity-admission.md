# 05B3B1 — Recursive Codex Plan Identity Admission

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02 and AC-07 compensation-state seam |
| State | `PLANNED / OWNER_AUTHORIZED / DISPATCH_READY` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B3B1-01` / I1-I5 |
| Dependency | Integrated 05B1/05B2/05B3A; terminal 05B3B submission `4d5bbefe42e1d1ae3206b29e877f0556bda3ce4c`; ADR-20260811-004 revision 03 |
| Control / implementation / reviewer | Current `main` / task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` / independent current `main` reviewer |
| Worktree / branch | Existing `workflow-implementer-2` / existing `codex/implementation-codex-compensation-reducer-05b3b`; additive child-ticket commits only |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

An exact compensation plan with a recursively valid current-attempt identity
continues to reduce deterministically. An exact plan model whose exact identity
contains one missing or malformed nested field returns the metadata-only finite
result `COMPENSATION_BLOCKED / PLAN_INVALID` before equality, serialization or
any other operation on that field can run.

This is a new convergence child, not a third correction of
`CLOSURE-LOCAL-INSTALL-T05B3B-02`. The rejected parent commits remain immutable
ancestors and are not approved by this ticket. The terminal child review must
review the complete resulting reducer and rerun parent R1-R5 plus child I1-I5
before the branch may be integrated.

## Exact source boundary

Only these existing paths may change:

1. `library/local_orchestration/codex_compensation_reducer.py`
2. `tests/test_codex_compensation_reducer.py`

Every other source, test and root export is read-only. No port, callable,
command, path access, live Codex state, target-project write or host effect is
accepted. No new dependency is authorized.

## Frozen admission design

- Before rebuild comparison, the supplied plan identity must be the exact
  `CodexCompensationPlanIdentity` type and its four fields must respectively be
  the exact `CodexPreflightRequest`, `CodexRegistrationAttemptId`,
  `CodexAttemptEffectState` and `CodexAttemptEffectState` types.
- A rejected nested value must not be serialized, compared, hashed, formatted,
  represented or dynamically inspected. Do not add a `BaseException` catch or
  catch process-control exceptions; the proof is that untrusted operations are
  unreachable.
- Only after recursive admission may the implementation rebuild a trusted plan
  from its already validated journal/request/attempt. The accepted result is
  that trusted rebuild. Any supplied-plan mismatch remains `PLAN_INVALID`.
- Expected application validation failures remain finite under the existing
  narrow exception boundary. No raw exception text or malformed value appears
  in a result or handoff.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `I1` | Recursively exact identity admission occurs before any comparison or serialization of a supplied identity field. All valid required/no-compensation plans retain the exact parent R1-R5 results and serialization. |
| `I2` | For each of `request`, `attempt_id`, `marketplace_state` and `plugin_state`, cross exactly seven `model_construct()` substitutions: missing, `None`, `""`, `" "`, `[]`, `{}` and an unrelated plain object. All 28 cells return exactly metadata-only `COMPENSATION_BLOCKED / PLAN_INVALID` without an escaping exception. |
| `I3` | For each of the four fields, cross equality/format trap values configured to raise `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit`. All 16 cells return `PLAN_INVALID` and no trap method runs; process-control exceptions are not swallowed by a broad catch. |
| `I4` | Independently (a) remove one recursive identity-field type guard and (b) restore supplied-identity serialization before admission. Each isolated reversal turns its named committed test red and is restored. The terminal reviewer also reruns all six parent R4 reversals. |
| `I5` | Focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff checks and tracked/ignored/cache readback pass. The two authorized paths are the only implementation-commit changes and the return commit changes only `doc/WorkProgressReport.md`. |

## TDD and review mapping

- **First red:** on exact clean baseline `4d5bbef`, add the four plain-object
  nested-identity cells before production changes. The expected baseline failure
  is an escaping `PydanticSerializationError`, not an invented assertion.
- **Null/empty/container (CodeReview class 2):** the 28-cell I2 table is the
  complete frozen matrix; do not replace it with “all malformed values”.
- **Authority bypass / error code (classes 3/5):** a constructed exact wrapper
  never bypasses recursive identity admission, and every cell has the one
  public finite reason `PLAN_INVALID`.
- **Exception propagation (class 6):** I3 proves traps are never invoked. A
  broad catch that converts process-control exceptions is non-conforming.
- **Truthfulness (class 7 / CR):** record the exact first-red test and the two
  isolated I4 reversals. The reviewer independently reruns them and parent R4.
- **Path/token classes (1/4):** not applicable; this pure boundary accepts no
  path, URI, credential or token.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B3B1-01` |
| Handoff | `hnd_local_orchestration_install_05b3b1_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b3b1_20260812` / `rcpt_local_orchestration_install_05b3b1_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b3b1-20260812` / `q-local-orchestration-install-05b3b1-20260812` |
| Side context | `scx-local-orchestration-install-05b3b1-20260812-01` |
| Authority | Owner instruction on 2026-08-12 to use implementer-2 at the upgraded model; exact reviewed control freeze commit is recorded in PRG-20260812-182. |
| Lane admission | Exact clean submitted HEAD `4d5bbefe42e1d1ae3206b29e877f0556bda3ce4c` in the existing branch/worktree. Do not create/switch/reset/rebase/merge/cherry-pick a branch or worktree. |
| Return | One additive exact-scope implementation commit, then one `doc/WorkProgressReport.md`-only handoff reserved as unique `PRG-20260812-183`. |

## Stop rule

The independent review after this return is terminal for this child closure.
Any remaining blocker returns `CONVERGENCE_REVIEW_REQUIRED`; there is no
automatic correction, branch/worktree replacement, integration or 05B3C
dispatch.
