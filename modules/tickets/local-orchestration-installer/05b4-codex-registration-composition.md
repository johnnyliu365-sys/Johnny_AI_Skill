# 05B4 — Codex Registration Composition Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| State | `CONVERGENCE_DECOMPOSED / CHILD_05B4A_SELECTED` |
| Dependency | 05A, 05S1-05S4, 05B1, 05B2, 05B3A, 05B3B1 and 05B3C integrated |
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
| 05B4B | Compose fresh preflight, marketplace/plugin add classification, proof/receipt, exact compensation and 05S4 oracle evidence into one finite registration result. | 05B4A approved and integrated |

05B4A and 05B4B remain serial because 05B4B consumes the exact reviewed port
contract. 05C remains blocked until 05B4B is approved and integrated. No child
may copy or cherry-pick rejected 05B source.
