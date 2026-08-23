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
| W1 | Dispatch authority admission | `CLOSED` — grant + containment-gated + journaled issuance behind `johnny-router dispatch`; 10 tests, two reverse mutations; fixture-free dispatch→subscription chain proven |
| W2 | Reviewer return path | `CLOSED` — verdicts bound to a dispatched receipt **and** a delivered wake; append-only durable returns behind `johnny-router review`; 10 tests, two reverse mutations, closed-loop cell |
| W3 | Router consumption of reviewer returns | `CLOSED` — each verdict becomes exactly one validated `RouterEvent`; marker written before the event is handed back; 9 tests, two reverse mutations |
| W4 | Whole-chain qualification | `CLOSED` — dispatch to Router event in one gated run, nothing simulated, no issuing fixture; surfaced governance 03 |
| W5 | Exactly-once across processes | `CLOSED` — the review return/consume critical sections take the extracted OS-visible file lock; two-consumer and two-submit races proven single-effect; lock removal turns the race cell red |
| P8R-R02 | [Provider-neutral executor routing (superseded)](p8-provider-neutral-executor-routing.md) | `SUPERSEDED / CHG-20260822-032` — old high-assurance admission assumptions; not dispatch authority |
| P8R-R03 | [Provider-neutral executor routing](p8r-provider-neutral-executor-routing-r03.md) | `BLOCKED / REQUIREMENT_CHANGED / CHG-20260823-033` — frozen resolver-input and assessment-verification contract defect; not dispatch, commit, or integration authority |
| P8R-R04 | [Canonical provider-neutral executor routing](p8r-provider-neutral-executor-routing-r04.md) | `DONE / APPROVED / INTEGRATED` — POC/standard canonical resolver, independently reverse-mutated and locally publication-bound; it makes no host, receipt, runner or automatic-wake claim. The later current-release pin defect belongs to Ticket 08. |
