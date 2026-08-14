# 05B4B2E — Codex Registration Lifecycle Acceptance Parent

| Field | Value |
| --- | --- |
| State | `CONVERGENCE_DECOMPOSED / NON_DISPATCHABLE / CHILD_E0_FROZEN` |
| Closure | `N/A` — immutable non-dispatchable decomposition parent; E0-E6 own separate closures |
| Implementation language | `N/A` — immutable non-dispatchable decomposition parent; child tickets explicitly bind Python 3.11 strict typing |
| Dependency | 05B4B2C and 05B4B2D independently approved and integrated |
| Allocation | None; a parent ticket never receives implementation authority |

## Decomposition decision

The former responsibility combined an oracle contract correction, identity
mapping, two effect adapters, success settlement, compensation settlement,
absence, foreign-state preservation and target-project isolation. Those are
different failure boundaries and cannot be independently accepted in one
implementation return.

This parent is therefore immutable planning evidence only. Delivery is split
into the following bounded children:

1. `05B4B2E0` extends 05S4 with one persisted logical installed path while
   preserving its separate disposable physical payload locator.
2. `05B4B2E1` purely binds one validated registration request to one exact
   oracle identity; it performs no effect.
3. `05B4B2E2` adapts only fresh preflight, marketplace add, plugin add and
   registration proof to 05S4.
4. `05B4B2E3` adapts only plugin removal, marketplace removal, list proofs and
   installed-path absence to 05S4.
5. `05B4B2E4` proves the complete registration-success/receipt lane.
6. `05B4B2E5` proves declared failure, exhaustive compensation and absence.
7. `05B4B2E6` proves foreign-state and target-project byte/Git isolation across
   the accepted lifecycle.

E2 and E3 may run in parallel only after E0 and E1 are independently approved
and integrated. E4-E6 remain dependency ordered. Every child receives its own
closure, allocation, receipt, review and guarded integration. No numeric line
limit is an acceptance criterion.

No child may execute live Codex, mutate a real host, install a package, touch a
target project, push, release or deploy. All lifecycle effects stay within the
disposable 05S1-05S4 boundary. `XSS_NOT_APPLICABLE`: this cluster adds no
Browser, WebView, HTML/DOM renderer or JavaScript execution context.
