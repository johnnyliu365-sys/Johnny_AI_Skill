# 05B3C — Codex Compensation Composition

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 compensation seam |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Closure | Not frozen until 05B3A and 05B3B1 are independently approved and integrated |
| Dependency | 05B3A and 05B3B1 integrated |
| Owner / worktree | Unallocated; reviewer selects one released lane only after both dependencies close |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Compose the validated 05B3A capability with the reducer approved through 05B3B1: execute
only the planned operations in exact order, validate each returned observation
against the exact manifest, continue after every declared finite failure, and
return the reducer result. No runtime callable introspection is permitted.

The future refreeze may authorize only a new coordinator module, its test and
root exports. It must enumerate actual-operation exception propagation,
manifest mismatch, all five finite step failures, normalized outcome mapping,
metadata-only results and cross-module reverse mutations. It may not begin,
receive a receipt or select a branch before both dependencies are reviewed and
integrated.
