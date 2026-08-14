# 06G3 — Reviewer Gateway Composition

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC revision 03 / AC-09 and AC-10 |
| Change | `CHG-20260814-018` |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 06G1 and 06G2 independently approved and integrated |
| Delivery profile | `HIGH_ASSURANCE`; one implementer; no helper |

## One outcome

Compose 06G1 admission with an injected fake `ReviewerOrchestrationPort` and
06G2 owned binding. Each reviewer action reaches exactly one fake effect under
its own consumable binding. The implementation composition root exposes no
gateway port or credential; built-in, alias and indirect attempts halt before
the fake. Removal closes the grant and replay remains effect-free.

No real task, Codex/App/filesystem/network/Git or target-project effect is in
scope. Freeze exact public port shape, constructor preflight, exhaustive
action/denial matrix and red-sensitive reversals before dispatch.
`XSS_NOT_APPLICABLE`.
