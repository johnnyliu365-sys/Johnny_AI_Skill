# Code Review — 01 Private Router Metadata Gate

| Field | Value |
| --- | --- |
| Ticket | `01-private-router-metadata-gate` |
| Review basis | approved ticket, `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26`, `CHG-20260804-008` |
| Baseline | `bc3f19e` |
| Reviewer | Codex / current worktree |
| Date | 2026-08-04 (Asia/Taipei) |
| Result | `APPROVED` |

## Reviewed behaviour

- `ContinuationDirective` makes `AUTO_CONTINUE`, `WAIT_FOR_HUMAN`, and `HALT` mutually constrained at the Router decision boundary.
- The POC profile advances automatically through declared safe stages, waits only at specification and ticket approval gates, and halts other invalid or undeclared transitions.
- The metadata-only private boundary rejects unknown/sensitive fields before transport, validates exact opaque correlation IDs, fails closed on denied entitlement, transport failure, malformed or mismatched response, and exposes only product-language actions.
- Local Context is reachable through `LocalContextGate` only after a valid automatic plan and exact source-kind/budget match. The underlying local resolver now rejects Context packets exceeding the Router budget.
- The test-only runner has an explicit step ceiling. It demonstrates automatic continuation but deliberately does not execute a model, deploy MCP, OAuth, payment, storage, or network service.

## TDD and validation evidence

| Evidence | Result |
| --- | --- |
| Initial red test | `python -m unittest tests.test_private_router_metadata_gate -v` failed with `ModuleNotFoundError: library.workflow_router.private_router` before implementation. |
| Targeted green tests | `tests.test_private_router_metadata_gate` passed after implementation, including automatic flow to the first human gate. |
| Full regression smoke | `python -m unittest discover -s tests` — 64 tests passed. |
| Strict type check | `python -m mypy --strict library tests` — success, 58 source files. |
| Compile check | `python -m py_compile` over every `library/workflow_router/*.py` file — passed. |
| Plugin validation | Codex and Claude JSON manifests parsed; Codex version is `0.3.1`; takeover skill contains all three continuation directives. |
| Diff hygiene | `git diff --check` — passed. |

## CodeReview.md §2.1 traceability

| # | Required defect class | TDD / review evidence | Result |
| --- | --- | --- | --- |
| 1 | Path-prefix mismatch | `test_metadata_normalizer_rejects_sensitive_unknown_or_empty_input_before_transport` rejects `source_path`, `uri`, `filename`, and `../` inputs before transport. No service contract accepts a locator. | Pass |
| 2 | `null`, empty string, arrays | The same test covers `null`, empty source kinds/digests and empty summary. Strict Pydantic models reject unknown/empty invalid shapes. | Pass |
| 3 | Authorization bypass | `test_denied_entitlement_and_service_failure_do_not_open_context_or_fallback_locally` denies an exact-mismatch entitlement and proves `LocalContextGate` raises before Context resolution. | Pass |
| 4 | Token format / comparison | `test_malformed_ids_and_response_replay_or_mismatch_fail_closed` rejects malformed correlation IDs and mismatched response request IDs; retry stability/different-event IDs are proved by `test_response_correlation_is_exact_retry_stable_and_has_no_source_sentinel`. | Pass |
| 5 | Stable external errors | Tests assert the four mandatory boundary codes: `ROUTER_INPUT_INVALID`, `ROUTER_ENTITLEMENT_DENIED`, `ROUTER_SERVICE_UNAVAILABLE`, and `ROUTER_RESPONSE_INVALID`; `ROUTER_POLICY_BLOCKED` covers valid policy halts without disclosing internal details. | Pass |
| 6 | External exception behaviour | `RaisingService` raises a timeout-like exception; the client produces a no-throw `HALT` with `ROUTER_SERVICE_UNAVAILABLE`. | Pass |
| 7 | Tests cover described behaviour | New tests cover auto continuation to SPEC wait, TICKETS wait, Context gate/budget, privacy sentinel, malformed input/response, entitlement denial, service failure, correlation, and source ambiguity. Existing Router, graph, Temporal, telemetry, and full-suite tests pass. | Pass |

## Review findings and disposition

One pre-existing behaviour conflict was found during implementation: all `SUSPEND` outcomes were treated as a Temporal human wait, so missing data or other fail-closed cases could stall a task. It is resolved by the continuation directive, LangGraph’s `continue` / `waiting` / `halted` branches, and Temporal waiting only for `WAIT_FOR_HUMAN`.

No unaddressed P0 typing, authorization, privacy, Context-budget, or test-evidence issue remains within this POC ticket. The POC is approved for handoff. A real SaaS transport, OAuth, payment, persistence, deployment, and autonomous host-side model scheduling remain expressly out of scope and require the later MVP change path.
