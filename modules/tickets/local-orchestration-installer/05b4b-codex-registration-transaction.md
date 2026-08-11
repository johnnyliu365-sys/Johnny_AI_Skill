# 05B4B — Codex Registration Transaction Convergence Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 |
| State | `CONVERGENCE_DECOMPOSED / CHILD_05B4B1_FROZEN / CHILD_05B4B2_DEPENDENCY_WAIT` |
| Dependency | 05A, 05S1-05S4, 05B1-05B3C, 05B4A and 05B4A1 approved and integrated |
| Historical evidence | Terminal rejected 05B review `24227ac`; rejected source is immutable evidence only |

## Convergence decision

The former 05B4B placeholder combined two independently rejectable boundaries:

1. pure sequencing and current-attempt authority reduction; and
2. effect execution, proof/receipt issuance, compensation execution and oracle acceptance.

That shape recreated the earlier full-transaction review surface and made one
defect invalidate unrelated behavior. This is a ticket decomposition under the
same product requirement, not `REQUIREMENT_CHANGED`.

| Child | One observable responsibility | Dependency |
| --- | --- | --- |
| [05B4B1](05b4b1-codex-registration-reducer.md) | Return only the next forward directive, exact proof request, exact compensation plan or metadata-only block from trusted phase/result values. It executes no effect and cannot return registration success or a receipt. | 05B4A1 integrated |
| 05B4B2 | Execute the admitted 05B4A capability according to reviewed B1 decisions; bind proof/receipt, 05B3C compensation and 05S4 oracle truth into the final finite registration result. | 05B4B1 integrated |

The children are serial. Only 05B4B1 is frozen and selected. 05B4B2 has no
allocation, receipt, branch or implementation authority and will receive its
own bounded closure only after independent 05B4B1 approval and integration.

05C remains dependency-waiting until 05B4B2 is complete. No live Codex,
target-project write, package, release or deployment authority is granted by
this parent.
