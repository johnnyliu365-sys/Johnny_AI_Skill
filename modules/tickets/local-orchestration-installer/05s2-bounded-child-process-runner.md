# 05S2 — Bounded Child-Process Runner

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / verification support only |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 05S1 independently approved and integrated |
| Implementation responsibility | Future named owner in the sole implementation worktree; no active allocation |
| Acceptance responsibility | Independent control-plane reviewer; no implementation writes |

## One outcome

Run one deterministic generic fixture process inside an integrated 05S1
environment with an explicit executable, argument vector, working directory,
child environment and finite timeout. Return a strict process observation. This
ticket knows nothing about Codex, plugins, marketplaces or installation state.

## Authorized scope

Only a new `tests/staging/process_runner/` support package, one deterministic
fixture script, `tests/test_bounded_child_process_runner.py`, and a separate
docs-only handoff. Integrated 05S1 files are read-only unless a reviewed
`REQUIREMENT_CHANGED` decision says otherwise.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S2-01`

| ID | Process-only acceptance |
| --- | --- |
| `P1` | Exact executable and argv reach the generic fixture with `shell=False`; no command string or PATH lookup is accepted. |
| `P2` | The child receives the explicit 05S1 mapping and owned working directory; the parent environment and filesystem remain unchanged outside the environment root. |
| `P3` | Success, finite nonzero exit, timeout, unavailable executable, access denial and generic launch failure map to distinct strict results; timeout terminates the owned child. |
| `P4` | Observation records actual executable, original/effective argv, exit/result and whether a child started. It records no stdout/stderr content beyond bounded fixture metadata and no absolute path enters durable handoff evidence. |

The reviewer runs focused, full and strict-type checks from an exported checkout.
Any blocking review stops without automatic correction. 05S3 remains blocked
until approval and integration.
