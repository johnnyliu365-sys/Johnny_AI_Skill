# 07 — Senior FIFO and dependency-cluster review queue

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-12 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 06 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

Committed candidates enter FIFO. One Senior claim freezes the current batch; later arrivals wait
without a second wake. Tickets retain individual states, declared dependency clusters are reviewed
together, and a new cluster revision invalidates only affected inspections before a decision.

Writable scope: `library/local_orchestration/senior_review_inbox.py`,
`library/local_orchestration/senior_review_inbox_state.py`,
`library/local_orchestration/windows_senior_review_inbox_store.py`,
`tests/test_plugin_distribution_review_queue.py`.

## TDD, verification and return

Closure `CLOSURE-PD-07-R03-01`: Q1 FIFO; Q2 closed batch; Q3 busy Senior no second wake; Q4
individual status; Q5 cluster consistency; Q6 revision invalidation. First red:
`python -m pytest -q tests/test_plugin_distribution_review_queue.py -k test_arrival_after_claim_waits_for_next_batch_without_second_wake`.
Verify with `python -m pytest -q tests/test_plugin_distribution_review_queue.py`,
`python -m mypy --strict library/local_orchestration/senior_review_inbox.py library/local_orchestration/senior_review_inbox_state.py library/local_orchestration/windows_senior_review_inbox_store.py`
and `python -m pytest -q`; reverse-mutate claim closure. Delete fixture store;
return typed commit/cell/digest/cleanup evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
