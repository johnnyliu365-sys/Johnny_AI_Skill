# 13 — Explicit telemetry report

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-14 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 04 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

Only an explicit user report request resolves receipt-indexed committed evidence and emits
separate input, cached-input and output token counts grouped by role/model/reasoning level with
original-currency price snapshot. JSON, CSV, terminal table and bar-chart data contain no raw
Context, prompt, source, path, Secret or PII. No background model or schedule is introduced.

Writable scope: `library/workflow_router/telemetry.py`,
`library/workflow_router/telemetry_cli.py`, `tests/test_plugin_distribution_telemetry_report.py`.

## TDD, verification and return

Closure `CLOSURE-PD-13-R03-01`: T1 exact token classes; T2 model/role/currency separation; T3 four
exports agree; T4 missing receipt finite failure; T5 raw-content rejection; T6 no implicit run.
First red: `python -m pytest -q tests/test_plugin_distribution_telemetry_report.py -k test_report_keeps_cached_input_separate_from_input_tokens`.
Verify with `python -m pytest -q tests/test_plugin_distribution_telemetry_report.py`,
`python -m mypy --strict library/workflow_router/telemetry.py library/workflow_router/telemetry_cli.py`
and `python -m pytest -q`; reverse-mutate raw-content denial. Delete fixtures; return typed evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `INTEGRATED / CLOSED` |
| Implementation | `feat: add explicit receipt-indexed telemetry report` on `claude/skill-plugin-parallel-control-42c487`; owner-authorized direct allocation |
| Closure | T1 input/cached-input/output stay separate through aggregation and cost math. T2 role/model/reasoning-level/currency groups never merge (5 distinct groups from 5 mixed records). T3 JSON, CSV, terminal table and bar-chart data expose identical token numbers per group. T4 unknown receipt → `RECEIPT_NOT_FOUND`; unavailable evidence → `EVIDENCE_UNAVAILABLE`; divergent snapshots → `PRICE_SNAPSHOT_CONFLICT`. T5 typed fields refuse paths/URIs/free text and forged `model_construct` records are re-proven and rejected as `RAW_CONTENT_REJECTED` before aggregation. T6 `explicit_user_request: Literal[True]` makes an implicit run untypable; a foreign request object blocks before touching the evidence source. |
| Verification | focused `7 passed, 8 subtests`; `mypy --strict --no-incremental` clean over telemetry.py, telemetry_cli.py and the test; existing `test_workflow_router.py` regression `60 passed, 220 subtests`; full `789 passed, 2594 subtests`; 219 Python files compiled in memory. |
| Reverse mutation | Raw-content denial bypassed → `test_raw_content_is_rejected` red on the forged-record cell; exact bytes restored; focused rerun `7 passed, 8 subtests`. |
| Boundary | No background model, schedule, polling or automatic run; no raw Context, prompt, source, path, Secret or PII in any export; existing context-load validation CLI behavior unchanged. |

Canonical SHA-256: `telemetry.py`
`5E0855454676CB34D46EE27EB9D01F950DB7C8B60C3B9EDB1BEDB18E48BB393C`;
`telemetry_cli.py` `BF004D2AB703E69CF358F8C3F5F02A54DD4D1AC7017AB0613E3F935D3B24E08F`;
`test_plugin_distribution_telemetry_report.py`
`DDC657721747AE34F02F9DDD49D569F575028327FF097D11BA83870540D19649`.
