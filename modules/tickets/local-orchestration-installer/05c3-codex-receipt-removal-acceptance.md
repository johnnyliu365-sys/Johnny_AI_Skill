# 05C3 — Codex Receipt Removal Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C3-01` / A1-A8 |
| Dependency | 05C2B independently approved and integrated |
| Profile / XSS | `STANDARD`; one implementation owner, no helper / `XSS_NOT_APPLICABLE` |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

## Reserved responsibility

Using only the integrated project-owned disposable staging lease and oracle,
prove `register -> receipt -> remove -> fresh absence -> replay` end to end.
The same transactions must preserve seeded foreign state/payloads and two
external sentinel repositories byte-for-byte with unchanged Git porcelain.

## Frozen behavior pending dependency readback

- Acceptance-only staging/test changes; no new product behavior.
- One fresh success transaction produces the actual integrated receipt. The
  exact receipt is then consumed by 05C1/05C2B through an admitted oracle port.
- First removal returns `REMOVED`, exact owned plugin/marketplace/logical and
  physical payload state is absent, and second removal returns mutation-free
  `NOT_INSTALLED`.
- Foreign prefix-similar marketplace/plugin records and payload bytes remain
  exact across success, removal and replay.
- Existing and empty external sentinel repositories remain byte-identical and
  Git-clean. No target-project path enters a product DTO or effect request.
- Reverse receipt binding, remove order, each of three absence conjuncts,
  replay zero-removal and both isolation gates independently.
- This contract-staging evidence does not by itself claim live-host
  `SUPPORTED`; that projection still requires the separately approved host and
  disposable-Windows gates fixed by the SPEC.

This child will be refrozen against the exact integrated 05C2B API before lane
admission. No implementation authority exists now.
