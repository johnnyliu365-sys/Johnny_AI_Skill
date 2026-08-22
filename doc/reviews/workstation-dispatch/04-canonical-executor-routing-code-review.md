# P8R-R04 Canonical executor routing — code review

| Field | Value |
| --- | --- |
| Ticket / closure | `P8R-EXECUTOR-ROUTING-04` / `CLOSURE-EXECUTOR-ROUTING-P8R-03` revision `03` (ticket revision `05`) |
| Requirement / Context / SPEC | `REQ-20260823-033` / `CTX-EXECUTOR-ROUTING-20260823-03` / `modules/spec/executor-routing.md` Revision 03 |
| Baseline | `eb7d250dcc74cbd0c78853310f8163698e305b79` |
| Reviewed source commit | `a23861e7cba3ccadca720c028cef815e3a9d602b` |
| Reviewed publication commit | `e86dbae946de355f94fcadd9eefe8b5b241567cc` |
| Local payload anchor | `refs/heads/publication-0.4.9` -> `f7b1c377fd6b4f7b1b23d3055d594a3f2bb5e851` |
| Implementation / review profiles | Luna / `xhigh`; Terra / `xhigh` |
| Conclusion | `APPROVED / GUARDED_INTEGRATION_COMPLETED` |

## Admission and scope

The frozen ticket was read from `main` before integration. The candidate changed exactly its
revision-05 boundary:

```text
modify .claude-plugin/marketplace.json
create library/local_orchestration/executor_routing.py
create tests/test_executor_routing.py
```

The candidate was clean, based on the committed `main` baseline, and fast-forwarded through
`admit_document_mutation`. The gate returned `INTEGRATED` with
`integrated_commit = e86dbae946de355f94fcadd9eefe8b5b241567cc`.

This POC review used the same-lifecycle completion path: reviewer dispatch, synchronous
completion return, reviewer verification, then guarded integration. No runner, durable queue,
dispatch receipt, live descriptor, host gateway, or workspace/profile readback was asserted or
needed for that path. The known host-readback gap remains explicitly outside this ticket and is
not represented as successful delivery.

## Independent verification evidence

| Check | Result |
| --- | --- |
| Focused executor-routing suite | PASS — `py -3.11 -m pytest tests/test_executor_routing.py -q`: 25 passed. |
| Strict types | PASS — `py -3.11 -m mypy --strict library/local_orchestration/executor_routing.py`: no issues. |
| Publication declaration | PASS — generator `--verify-only` accepted `f7b1c377fd6b4f7b1b23d3055d594a3f2bb5e851`. |
| Payload/tree binding | PASS — the local publication anchor contains `library/local_orchestration/executor_routing.py`; the development-only test file is correctly absent from the payload. |
| Scope / hygiene | PASS — `git diff --check` clean; only the three ticket-authorized paths changed. |
| Reverse mutation | PASS — RM1 and M1-M7 each turned its targeted committed test red, then source was restored byte-for-byte and focused checks were green again. |
| Main-shaped full regression | PASS for this closure — 1671 passed, 22 skipped, 3987 subtests passed in 420.13s. |

The reverse-mutation set verified: registry canonicalization cannot be bypassed; the routing-table
validation remains first; unavailable or over-ranked overrides are rejected; provenance and
freshness are enforced through typed fields; no default route appears; and provider-specific
literals remain absent from the resolver boundary.

## Findings and residual risk

No implementation or evidence finding remains open for this closure.

The full suite repeated three pre-existing environment failures outside the reviewed paths:

1. `tests/test_one_click_installer.py` has two assertions that decode a localized `cmd.exe`
   pause prompt as UTF-8 and consequently cannot observe the expected ASCII sentinel.
2. `tests/test_runtime_dependency_lock.py` observes pytest `9.0.3` while
   `requirements-dev.txt` declares `9.1.1`.

Neither failure concerns `executor_routing.py`, the generated marketplace pin, or the local
payload anchor. They are recorded as environmental follow-up, not as a basis to reject this
ticket.

## Handoff

`main` is at `e86dbae946de355f94fcadd9eefe8b5b241567cc` after guarded local integration.
The publication anchor is intentionally local only. At review time `origin/main` remains
`eb7d250dcc74cbd0c78853310f8163698e305b79` and
`origin/publication-0.4.9` remains `696319f843712ce68f385c9910092b886ce2d6aa`.
No remote publication ref, `main` push, release, deployment, provider invocation, or host wake
was performed or implied by this approval.
