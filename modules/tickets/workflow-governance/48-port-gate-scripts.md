# 48｜Port three proven gate scripts into the plugin

| Field | Binding |
| --- | --- |
| State / Closure | PLANNED; 48-P1–P6 revision01 |
| Authority | `PRD-20261103-043` / `CHG-20261103-043`; `modules/spec/workflow-governance.md` Revision 04 R4-2 (dispatch lint, evidence gate precursor, index pins) |
| Baseline | branch `cp/wave1-gates-first` after ticket 47 |
| Grant / roles | Control plane dispatches; `implementation-standard` seat in a disposable clone; independent review by a `ticket-review` seat |
| Source of the scripts | a target project checkout, read only: `scripts/review/dispatch_lint.py` + `scripts/test_dispatch_lint.py`, `scripts/receipt_fence_check.py` + `scripts/test_receipt_fence_check.py`, `scripts/fix_artifact_index_pins.py` + `scripts/test_fix_artifact_index_pins.py` at a recorded commit; the seat records the source commit and the sha256 of each copied file |
| Workspace | a disposable clone of `cp/wave1-gates-first`, named by the dispatch |
| Profile / limits | STANDARD; Python 3.11 only, no new dependency; every target-specific path, ticket id, lane name or model name stripped or parameterised |
| Language / return | Python 3.11 strict; `ImplementationReturn` COMPLETED with commit, file list, pytest result, mutation proof per script |

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = modules/tickets/workflow-governance/README.md
create = skills/johnny-project-takeover/scripts/dispatch_lint.py
create = skills/johnny-project-takeover/scripts/receipt_fence_check.py
create = skills/johnny-project-takeover/scripts/index_pins.py
create = skills/johnny-project-takeover/scripts/README.md
create = tests/test_gate_dispatch_lint.py
create = tests/test_gate_receipt_fence_check.py
create = tests/test_gate_index_pins.py
forbid = library/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
forbid = doc/
```

## One observable behavior

A plugin user runs `python skills/johnny-project-takeover/scripts/dispatch_lint.py <dispatch.yaml>`
and gets `LINT PASS` with exit 0 or the rule ids R1–R5 with exit 1; runs
`receipt_fence_check.py <receipt> <heading> <evidence-root>` and gets the failure codes with
exit 1 or `failures=0` with exit 0; runs `index_pins.py --check <index.md>` and gets the stale
rows with exit 1 or exit 0. Usage errors exit 3. The three scripts carry no path, id or name
from any target project.

## Acceptance

| Cell | Check | Expected |
| --- | --- | --- |
| P1 | `pytest tests/test_gate_dispatch_lint.py` | self-test ported; fixtures generated in a temp dir; expectations derived from fixtures |
| P2 | `pytest tests/test_gate_receipt_fence_check.py` | as P1 |
| P3 | `pytest tests/test_gate_index_pins.py` | as P1; the index format is the generic `| id | kind | state | git:<sha> | sha256:<hex> | leaf |` row |
| P4 | `grep -rniE "<denylist>" skills/johnny-project-takeover/scripts tests/test_gate_*.py`, where `<denylist>` is carried by the P4 command of the dispatch file for this ticket (the parameter file of the run) and is not written in this ticket | zero hits |
| P5 | `.claude-plugin/plugin.json` payload | `skills` tree already covers the scripts; `tests/test_plugin_payload_boundary.py` still passes |
| P6 | exit codes | each script: 0 pass, 1 red, 3 usage, proven by one case each in its test |
| M1 | remove rule R3 from dispatch_lint | P1 red |
| M2 | make receipt_fence_check accept a fence without capture | P2 red |
| M3 | make index_pins ignore the digest column | P3 red |
