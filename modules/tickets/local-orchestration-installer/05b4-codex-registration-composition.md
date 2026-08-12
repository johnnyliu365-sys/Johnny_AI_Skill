# 05B4 — Codex Registration Composition Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| State | `CONVERGENCE_DECOMPOSED / CHILD_05B4B1_CR149_CORRECTION_DISPATCHED / CHILD_05B4B2_DEPENDENCY_WAIT` |
| Dependency | 05A, 05S1-05S4, 05B1, 05B2, 05B3A, 05B3B1, 05B3C, 05B4A and 05B4A1 integrated |
| Historical evidence | Terminal rejected 05B review `24227ac`; rejected source is evidence only and must not be reused |

## Refreeze decision

The former one-line 05B4 placeholder combined two independently rejectable
responsibilities: admitting a safe registration effect capability and running
the full registration transaction. Keeping them together would recreate the
old CR-99/CR-104 failure mode where caller-manufactured observations could look
like effect truth. This is ticket convergence, not a requirement change.

| Child | Observable responsibility | Dependency |
| --- | --- | --- |
| [05B4A](05b4a-codex-registration-port-capability.md) | Admit one closed four-operation registration port and freeze exact request/result envelopes without executing it. | Integrated 05A/05B1/05B2 |
| [05B4A1](05b4a1-codex-plugin-identity-authority.md) | Bind installer-controlled expected plugin ID into request and plugin-add observation validation. | 05B4A approved and integrated |
| [05B4B](05b4b-codex-registration-transaction.md) | Convergence parent that separates pure forward transaction decisions from every registration effect. | 05B4A1 approved and integrated |
| [05B4B1](05b4b1-codex-registration-reducer.md) | Purely reduce fresh-preflight and ordered add results into the next exact directive, proof request, compensation plan or finite block. | 05B4A1 approved and integrated |
| [05B4B2](05b4b2-codex-registration-transaction-coordinator.md) | Later own current generation and one-shot effect admission while composing the registration capability, proof/receipt, compensation and 05S4 oracle. | 05B4B1 revision 02 approved and integrated |

05B4A, 05B4A1, 05B4B1 and 05B4B2 remain serial because each downstream
boundary consumes an exact reviewed contract. The prior 05B4B shape is not
implementable as one ticket: it joined pure sequencing, four registration
effects, receipt authority, compensation and oracle acceptance into one review
surface. Splitting it is ticket convergence under unchanged requirements.

05B4B1 revision 01 is terminal rejected by CR-148 because the pure reducer
cannot distinguish first use from identical authorized-state replay without a
current-generation or consumption authority. Revision 02 removes object-identity
authority from B1 and reserves current generation plus one-shot lease consumption
for B2. B2 remains dependency-waiting and undispatched.

05C remains blocked until 05B4B2 is approved and integrated. No child may copy,
import or cherry-pick rejected 05B source.
