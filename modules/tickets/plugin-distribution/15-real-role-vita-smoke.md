# 15 — Owner-controlled real-role SourceProjectA smoke

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-10, AC-11, AC-12, AC-15 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 14 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; owner approval and fresh live role receipts required |
| State / XSS | `PLANNED / HIGH_ASSURANCE_REQUIRED / OWNER_EFFECT_REQUIRED / NOT_DISPATCHED`; `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

The Senior controls one isolated Python smoke ticket in a disposable Vita copy using exact Terra
Senior and Luna xhigh Implementer bindings. It proves implementation commit, committed handoff,
FIFO admission and independent review, or stops exactly at
`HOST_WAKE_CAPABILITY_UNAVAILABLE`. Manual forwarding never proves automatic wake or
`ROUTER_BINDING_ELIGIBLE`. This is an operational verification gate, not a coding ticket.

Repository writable scope: none. Temporary writable scope is one receipt-owned disposable copy
and its exact role branches/evidence; original Vita remains read-only. No network, business route,
database, Provider, Secret, publication or deployment.

## Verification and return

Closure `CLOSURE-PD-15-R03-01`: E1 live bindings; E2 isolated commit; E3 committed handoff; E4
FIFO/independent review; E5 exact unavailable-host block or verified callback; E6 canonical
uninstall and zero residue. Senior returns `ACTION_COMPLETED` with receipt/commit/review/cleanup
digests or the exact typed block. No heartbeat, polling, automation or retry after uncertain effect.

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `COMPLETED / OWNER_EXECUTED / CLOSED` |
| Execution | Owner-run on 2026-08-18/19 with two fresh live role sessions (Luna-tier implementer, Terra-tier reviewer; session identifiers owner-held in the host UI); receipt `receipt-vita-smoke-20260818-01`; correlation `corr-vita-smoke-20260818-01`; disposable copy cloned with `--no-hardlinks` into the user temp root, never the original. |
| E1 live bindings | Both sessions were newly created for this smoke; no prior receipt or conversation was replayed. Reviewer's first pass exposed a workspace mismatch (its checkout initially lacked the smoke branch), which was corrected before re-review — recorded as evidence that binding verification matters. |
| E2 isolated commit | Implementation commit `2183bd30113d1fb4391f02f64e18561bee5ad43b` on branch `codex/vita-smoke-01`: exactly `tools/johnny_smoke.py` (typed pure `smoke_signature(str) -> str`) plus `tests/test_johnny_smoke.py`; no push, no path outside the disposable copy. |
| E3 committed handoff | Handoff commit `a1b80d8b7a5f39d475baa1a400006e2b154d26da` (`HANDOFF-VITA-SMOKE-01.md`: receipt, branch, implementation SHA, terminal kind); correction commit `b23f16becacb4495c14ea0934eca890283ab4db2` replaced prose with `tests: 3 passed` metadata and added the precomputed non-ASCII vector test. |
| E4 independent review | Real reviewer returned `NOT_APPROVED` with two findings: ASCII-only test vectors (valid; fixed with known SHA-256 vector for a UTF-8 payload, 3/3 green) and handoff content beyond bare identifiers. The second finding traced to a dispatcher rule contradiction (`TICKET_DEFECT` on the dispatch prompts, not the implementer); after correction the reviewer confirmed every substantive cell (two-file scope, complete typing, genuine precomputed vector, no prose) and held only the identifier-scope reading. Owner ruling closed it against the canonical handoff contract, which requires the terminal kind and admits metadata results: `review = APPROVED_WITH_OWNER_RULING`. The finding→correction→re-verify→escalation→owner-decision chain executed exactly as designed. |
| E5 host wake | `HALT / HOST_WAKE_CAPABILITY_UNAVAILABLE` — the handoff reached the reviewer only through owner manual forwarding. No automatic wake and no `ROUTER_BINDING_ELIGIBLE` is claimed; this cell stays blocked until the 0.4.0 event runner provides a verified callback. |
| E6 uninstall and residue | Disposable content deleted; the empty directory shells stayed handle-locked until both role sessions closed, then removed — recorded as the required teardown order (close role sessions before workspace removal). `ZERO_RESIDUE_CONFIRMED` for `johnny-vita-smoke`. Original `私有目標repo` identity byte-identical before and after: HEAD `8aee42f662a652115c28a6d08d26c617f45a63e0`, porcelain status identical line for line. |
| Boundary | No network business route, database, Provider, Secret, publication or deployment; original Vita touched only by read-only Git identity queries. |
