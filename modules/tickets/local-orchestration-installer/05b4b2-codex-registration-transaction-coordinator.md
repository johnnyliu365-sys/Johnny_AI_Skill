# 05B4B2 — Codex Registration Transaction Coordinator

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 |
| State | `PLANNED / DEPENDENCY_WAIT / REFREEZE_REQUIRED` |
| Dependency | 05B4B1 revision 02 independently approved and integrated |
| Allocation | None; no implementation owner, receipt, branch or effect authority |

## Reserved responsibility

This coordinator will be the sole owner of registration transaction currency
and effect admission. Its future reviewed closure must bind one exact attempt,
phase and monotonically advancing generation to a coordinator-owned one-shot
lease before invoking the admitted 05B4A capability.

At minimum, the future closure must prove:

- the exact live `(attempt_id, phase, generation, lease)` is consumed once;
- stale, copied, forged, cross-phase and already-consumed leases return a finite
  metadata-only replay block before any effect;
- concurrent duplicate submissions cannot execute the same phase twice;
- `STARTED` is recorded before an effect and ambiguous interruption retains
  `MAY_EXIST` compensation authority;
- only a reviewed B1 decision associated with the exact live transaction can
  reach preflight, add, proof, receipt or compensation execution;
- proof, receipt, 05B3C compensation and 05S4 lifecycle-oracle truth remain
  exact and receipt-bound.

B1 values are decision data, not leases or receipts. Copying or reconstructing
an exact B1 value grants no effect authority. The complete acceptance closure,
storage lifetime, concurrency model and cleanup policy will be frozen only
after B1 revision 02 is approved and integrated.

No live Codex, host, filesystem, target-project, network, push, release or
deployment authority is granted by this planned ticket.
