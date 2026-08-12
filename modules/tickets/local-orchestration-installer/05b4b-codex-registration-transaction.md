# 05B4B — Codex Registration Transaction Convergence Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 |
| State | `CONVERGENCE_DECOMPOSED / CHILD_05B4B1_INTEGRATED / CHILD_05B4B2_DECOMPOSED` |
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
| [05B4B2](05b4b2-codex-registration-transaction-coordinator.md) | Convergence parent for transaction authority, forward effects, settlement and disposable lifecycle acceptance. | 05B4B1 revision 02 integrated |
| [05B4B2A](05b4b2a-codex-registration-transaction-authority.md) | Own exact process-local attempt/phase/generation and atomic one-shot lease consumption without effects. | 05B4B1 revision 02 integrated |

The children are serial. 05B4B1 revision 01 stopped at terminal review with
CR-148 / `TICKET_DEFECT`: a pure reducer cannot itself distinguish first use
from replay of the identical authorized state without a current-generation or
consumption authority. 05B4B2 is decomposed after revision-02 integration.
B2A has the sole frozen closure; B2B-B2E have no allocation, receipt, branch
or implementation authority.

The reviewed convergence resolution keeps B1 stateless and moves the impossible
stale-consumption claim to B2's explicit transaction authority. B1 copies are
decision data only; B2A leases will later be the sole phase-admission grants.

05C remains dependency-waiting until 05B4B2 is complete. No live Codex,
target-project write, package, release or deployment authority is granted by
this parent.
