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
