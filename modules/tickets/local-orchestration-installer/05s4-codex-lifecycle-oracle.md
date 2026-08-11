# 05S4 — Codex Lifecycle Oracle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07 and AC-08 lifecycle seam |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `PLANNED / READY / NOT_DISPATCHED` |
| Dependency | Satisfied: 05S1, 05S2 and 05S3 independently approved and integrated by `504a3ec`, `6e24e06` and `43a1639` |
| Implementation responsibility | Future named owner in the sole implementation worktree; no active allocation |
| Acceptance responsibility | Independent control-plane reviewer; no implementation writes |

## One outcome

Add a persisted test-only oracle behind the integrated environment, runner and
protocol fixture. Fresh state plus physical owned payloads answer exact
add/list/remove/absence queries. This ticket supplies deterministic truth to
future 05B/05C tests; it does not implement their transaction, compensation or
receipt logic.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S4-01`

| ID | Oracle-only acceptance |
| --- | --- |
| `O1` | Empty state, exact marketplace add and exact plugin add produce fresh list results through the integrated protocol fixture. |
| `O2` | Exact plugin removal before marketplace removal produces fresh exact-owned absence and physical payload absence. |
| `O3` | Valid unrelated and same-name foreign records remain byte/value-identical and are never treated as owned removal authority. Foreign records reported installed must have their own coherent physical fixture proof. |
| `O4` | Missing/extra/null state, duplicate identity, state/file disagreement in either direction and stale digest block list and absence truth with one finite reason; no SemVer rule beyond the integrated protocol contract is added here. |

Only the oracle state/filesystem layer and focused tests are in scope. Fault
timing, compensation, current-attempt authority and receipts remain exclusively
with 05B/05C. Any blocking review stops without automatic correction. Only an
approved and integrated 05S4 permits the control plane to refreeze 05B and 05C.
