# Atomic conditional replace capability Context

| Field | Value |
| --- | --- |
| Artifact ID / revision | `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-12` / `REVISION_12` |
| State | `SEALED / SPEC_REVISION_12_REQUIRED / CAPABILITY_INVESTIGATION_ONLY` |
| Requirement / ADR | `PRD-20260828-045` / `CHG-20260828-045` / `ADR-20260828-033` |
| Authority | Project owner decision, 2026-08-28 (Asia/Taipei) |
| Supersession | Extends the Revision 11 transaction fact only; it does not replace R09A planning, R09B1 result contracts or RWW6. |

## Confirmed facts

- The final managed target mutation needs a platform/backend-specific `AtomicConditionalReplace`
  capability. A digest comparison followed by ordinary replacement, rename or unlink leaves a
  TOCTOU interval and is not proof.
- The capability is qualified separately for Windows, Linux and the current filesystem abstraction.
  Each exact tuple has only `YES`, `NO` or `CONDITIONAL`; a conditional result names runtime-
  detectable constraints and otherwise fails closed.
- R09B2 is blocked pending `CAP-RWW6-01`. Its non-integrated candidates, including `f99d836`, are
  defect evidence only and must not receive a further implementer correction.
- The investigation is evidence-only. It must state the native primitive (or absence), race model,
  failure semantics and an adversarial reproduction that acts after the last observed-identity read.
- No unqualified backend may execute the R09B2 target-document write path. If no supported backend
  is proved, the next event is architecture/SPEC escalation rather than implicit weakening of RWW6.

## Boundary

This Context authorizes only an Atomic Conditional Replace capability investigation and its exact
evidence. It does not authorize source repair of R09B2, target mutation, a new runtime adapter,
plugin/CLI behavior, host/provider effect, publication, installation, release or deployment.
