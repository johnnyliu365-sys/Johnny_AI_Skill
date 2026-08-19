# Workstation Dispatch — Ticket Registry

The multi-model workstation line the E8 review pointed at: receipt issuance
stops being an importable function and becomes a control-plane process
privilege. This line owns "who may issue, from which principal, over which
boundary" — the question CLOSURE-E8-02 deliberately deferred.

| Field | Binding |
| --- | --- |
| Requirement | Owner directive 2026-08-19 ("你自己做大票"): the control plane implements phase C itself while E12/E13 run on the implementation lane |
| Baseline | `main` = `cf091c9` |
| Authority | Owner-direct allocation |
| Boundary | Additive only: no frozen contract is modified; the store's issuance semantics (CAS, ALREADY_ISSUED idempotence, RECEIPT_CONFLICT) stay exactly as reviewed |

| # | Ticket | State |
| --- | --- | --- |
| W1 | Dispatch authority admission | `OPEN` — control-plane executed |
