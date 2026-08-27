# Context-load telemetry 14 — Router-owned provisioning delegation contracts

| Field | Value |
| --- | --- |
| Ticket | [`14-router-owned-provisioning-delegation-contracts.md`](../../../../tickets/context-load-telemetry/14-router-owned-provisioning-delegation-contracts.md) |
| Private Router contract | `library/workflow_router/telemetry_provisioning_contracts.py` |
| Focused acceptance | `tests/test_telemetry_provisioning_contracts.py` |
| Frozen dependency | `library/workflow_router/policy_response.py` — `ApprovedDispatchArtifactRegistry` and `resolve_approved_dispatch_artifact` unchanged |
| Architecture | `ADR-20260827-029`; Context Revision 11; Specification Revision 11 / AC-22 |

This is an index, not a source copy. Ticket 14 creates only a private, typed, deterministic
Router authorization/denial contract over an already approved dispatch-artifact identity. It is
neither Host Bootstrap root readiness nor durable telemetry provisioning: it creates no root,
ledger, lock, stream, journal or report state, constructs no storage reference or locator, and
does not alter a public package export, composition factory, Router engine, provider/host/target
behavior, publication or release.
