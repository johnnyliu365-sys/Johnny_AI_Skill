# 05C2 — Codex Receipt Removal Composition Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06 and AC-07 |
| Revision | `02` — control-plane convergence decomposition |
| State | `CONVERGENCE_DECOMPOSED / NON_DISPATCHABLE` |
| Dependency | 05C1 independently approved and integrated by `9e0343a` |
| Replacement | Serial children 05C2A then 05C2B |
| Profile / XSS | `STANDARD`; one implementation owner per child, no helper / `XSS_NOT_APPLICABLE` |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

## Why this parent cannot be implemented safely

The revision-01 ticket required the receipt-removal coordinator to reuse the
integrated response admission and identity rules. Those rules exist only behind
five private functions in `codex_compensation_composition.py`. Its public
`compose_codex_compensation` entrypoint additionally requires a
journal-authorized registration compensation plan that a persisted uninstall
receipt neither has nor may synthesize.

Keeping this as one implementation ticket would therefore require at least one
forbidden design: import private helpers, duplicate hundreds of lines of exact
response admission, or invent a false registration journal. This is a
reviewer-owned `TICKET_DEFECT`; it is not a product requirement change and
creates no implementation authority.

## Convergence decomposition

1. **05C2A — compensation observation admission:** expose one pure public,
   request-bound observation admission API backed by the existing private
   normalizers. It invokes no operation and duplicates no response rules.
2. **05C2B — receipt removal coordinator:** consume 05C1, the admitted closed
   five-operation capability and 05C2A to perform pre-proof, ordered removal,
   post-proof and replay classification.

05C2B cannot dispatch until 05C2A is independently approved and integrated.
05C3 cannot dispatch until 05C2B is independently approved and integrated.
This parent remains immutable planning evidence and must never own a branch,
allocation, receipt or implementation commit.
