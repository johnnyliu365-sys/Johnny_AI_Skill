# 05B4B2 — Codex Registration Transaction Convergence Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 |
| State | `CONVERGENCE_DECOMPOSED / CHILD_05B4B2A_COMPLETE / CHILD_05B4B2B_COMPLETE / CHILD_05B4B2B1_FROZEN` |
| Dependency | 05B4B1 revision 02 approved and integrated by `d7c59349b436d552f2fab457a297e2eac6958093` |
| Allocation | B2A/B2B released; only freshly frozen B2B1 may receive the next dispatch; B2C-B2E remain unallocated |

## Convergence decision

The former B2 placeholder joined four independently rejectable boundaries:
transaction currency/concurrency, forward registration effects, proof/receipt
settlement, and compensation plus disposable-oracle acceptance. A defect in any
one would invalidate unrelated evidence and recreate the rejected monolithic
05B review surface. The product requirement and SPEC acceptance criteria are
unchanged; this is ticket decomposition.

| Child | One observable responsibility | Dependency |
| --- | --- | --- |
| [05B4B2A](05b4b2a-codex-registration-transaction-authority.md) | Own one process-local attempt, exact phase/generation and atomic one-shot start/complete authority without invoking an effect. | B1 integrated |
| [05B4B2B](05b4b2b-codex-registration-forward-composition.md) | Invoke only fresh-preflight/marketplace-add/plugin-add through an admitted registration capability and the B2A gate. | B2A integrated |
| [05B4B2B1](05b4b2b1-codex-registration-terminal-claim-authority.md) | Convert only an exact B2B terminal or started-add recovery into one non-transferable, one-shot proof or compensation claim without settlement effects. | B2B integrated |
| [05B4B2C](05b4b2c-codex-registration-proof-settlement.md) | Turn only an exact gated proof claim and matching proof into the existing metadata-only registration receipt. | B2B1 integrated |
| [05B4B2D](05b4b2d-codex-registration-compensation-settlement.md) | Turn only an exact gated compensation claim into the existing exhaustive compensation composition result. | B2B1 integrated; may later run in parallel with B2C |
| [05B4B2E](05b4b2e-codex-registration-lifecycle-acceptance.md) | Prove the composed success and failure paths in the disposable 05S1-05S4 environment, including complete removal/absence. | B2C and B2D integrated |

B2A-B2B1 are serial. After B2B1 integration, B2C and B2D have disjoint source
responsibilities and may be allocated to the two existing implementation
worktrees. B2E remains the final independent acceptance ticket.

No child may import or copy terminal rejected 05B source. No live Codex, user
profile, target project, network, package, push, release or deployment authority
is granted by this parent.
