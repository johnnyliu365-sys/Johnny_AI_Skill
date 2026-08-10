# 05S3 — Codex Protocol Fixture

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-08 protocol seam only |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 05S1 and 05S2 independently approved and integrated |
| Implementation responsibility | Future named owner in the sole implementation worktree; no active allocation |
| Acceptance responsibility | Independent control-plane reviewer; no implementation writes |

## One outcome

Provide deterministic child fixtures for the exact documented Codex marketplace
and plugin add/list/remove JSON surfaces. This ticket validates protocol shapes
only. It does not persist lifecycle state, decide ownership, perform
compensation or prove absence.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S3-01`

| ID | Protocol-only acceptance |
| --- | --- |
| `D1` | Marketplace add/list/remove success fixtures contain exactly the frozen documented fields and strict value types. |
| `D2` | Plugin add/list/remove success fixtures contain exactly the frozen documented fields and strict value types. |
| `D3` | For each surface, `{}`, malformed JSON, missing field, extra field, null and blank required text fail strict parsing. Version is treated according to the documented Codex field contract; this ticket does not invent a SemVer policy. |
| `D4` | Fixture selection is a finite enum and crosses the integrated bounded runner. No request value is reused as parsed response proof and no absolute fixture path becomes durable evidence. |

Only protocol contracts, deterministic fixture data/script and focused tests are
in scope. No marketplace/plugin persistence, filesystem payload, foreign state,
transaction journal or adapter production change is allowed. Any blocking
review stops without automatic correction. 05S4 remains blocked until approval
and integration.
