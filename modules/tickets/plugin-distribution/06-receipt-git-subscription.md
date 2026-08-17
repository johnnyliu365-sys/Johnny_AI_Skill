# 06 — Receipt-bound Git subscription

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-07, AC-09, AC-10 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 05 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

`ProjectSubscriptionRuntime` registers one existing exact receipt against one runner and native
Git-ref notification. A hint performs bounded ref/ancestry/changed-path/committed-handoff readback;
ordinary source commits stay silent. Foreign, stale, replayed or malformed binding rejects without
closing peer subscriptions. Existing receipt, Git adapter and supervision types are read-only.

Writable scope: `library/local_orchestration/project_subscription_runtime.py` and
`tests/test_plugin_distribution_git_subscription.py`. No host wake, polling or target write.

## TDD, verification and return

Closure `CLOSURE-PD-06-R03-01`: S1 exact registration; S2 source silence; S3 committed candidate;
S4 foreign/stale/replay rejection; S5 peer isolation/close. First red:
`python -m pytest -q tests/test_plugin_distribution_git_subscription.py -k test_foreign_receipt_handoff_never_emits_completion_candidate`.
Verify with `python -m pytest -q tests/test_plugin_distribution_git_subscription.py`,
`python -m mypy --strict library/local_orchestration/project_subscription_runtime.py` and
`python -m pytest -q`; reverse-mutate receipt matching. Delete fixture subscriptions only; return
typed commit/cell/digest/cleanup evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
