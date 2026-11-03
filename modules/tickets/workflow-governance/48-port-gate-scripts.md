# 48｜Port three proven gate scripts into the plugin

| Field | Binding |
| --- | --- |
| State / Closure | CONVERGENCE_REPLANNED / CORRECTION_DISPATCHED; 48-P1–P9 revision02 after the revision01 initial review returned CHANGES_REQUESTED with TICKET_DEFECT F-02 |
| Authority | `PRD-20261103-043` / `CHG-20261103-043`; `modules/spec/workflow-governance.md` Revision 04 R4-2 (dispatch lint, evidence gate precursor, index pins) |
| Baseline | branch `cp/wave1-gates-first` after ticket 47; candidate commits c1 `1d9f2a96`, c2 `c41cc29d` on branch `cp/wave1-ticket48-candidate` (base `f4d43817`); the correction is an additive commit c3 on that branch; the control plane cherry-picks c1–c3 onto the branch tip at integration (no rebase by the seat) |
| Grant / roles | Control plane dispatches; `implementation-standard` seat in a disposable clone; independent review by a `ticket-review` seat |
| Source of the scripts | a target project checkout, read only: `scripts/review/dispatch_lint.py` + `scripts/test_dispatch_lint.py`, `scripts/receipt_fence_check.py` + `scripts/test_receipt_fence_check.py`, `scripts/fix_artifact_index_pins.py` + `scripts/test_fix_artifact_index_pins.py` at a recorded commit; the seat records the source commit and the sha256 of each copied file |
| Workspace | a disposable clone of `cp/wave1-gates-first`, named by the dispatch |
| Profile / limits | STANDARD; Python 3.11 only, no new dependency; every target-specific path, ticket id, lane name or model name stripped or parameterised |
| Language / return | Python 3.11 strict; `ImplementationReturn` COMPLETED with commit, file list, pytest result, mutation proof per script |

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = modules/tickets/workflow-governance/README.md
modify = modules/tickets/workflow-governance/48-port-gate-scripts.md
create = doc/reviews/workflow-governance/48-port-gate-scripts-code-review.md
create = doc/reviews/workflow-governance/evidence/48/
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
forbid = doc/*.md
forbid = doc/requirements/
forbid = doc/adr/
forbid = doc/archive/
forbid = doc/context/
forbid = doc/handoffs/
forbid = doc/runbooks/
forbid = doc/reviews/*.md
```

## One observable behavior

A plugin user runs `python skills/johnny-project-takeover/scripts/dispatch_lint.py <dispatch.yaml>`
and gets `LINT PASS` with exit 0 or the rule ids R1–R5 with exit 1; runs
`receipt_fence_check.py <receipt> <heading> <evidence-root>` and gets the failure codes with
exit 1 or `failures=0` with exit 0; runs `index_pins.py --check <index.md>` and gets the stale
rows with exit 1 or exit 0. Usage errors exit 3. Tool faults exit 2: `receipt_fence_check.py` when the
evidence or scan root is not a readable directory; `index_pins.py` when the history is shallow
(`SHALLOW_HISTORY`), when `git` cannot start or the directory is not a repository, or when the
`--json` path cannot be written. `dispatch_lint.py` reads one file and has no tool fault: a
missing or unreadable file is a usage error. No option can make a rule vacuous: an empty
`--chat-words` list or an empty `--sealed-state` is a usage error. The three scripts carry no
path, id or name from any target project.

## Acceptance

| Cell | Check | Expected |
| --- | --- | --- |
| P1 | `pytest tests/test_gate_dispatch_lint.py` | self-test ported; fixtures generated in a temp dir; expectations derived from fixtures |
| P2 | `pytest tests/test_gate_receipt_fence_check.py` | as P1 |
| P3 | `pytest tests/test_gate_index_pins.py` | as P1; the index format is the generic `| id | kind | state | git:<sha> | sha256:<hex> | leaf |` row |
| P4 | `grep -rniE "<denylist>" skills/johnny-project-takeover/scripts tests/test_gate_*.py`, where `<denylist>` is carried by the P4 command of the dispatch file for this ticket (the parameter file of the run) and is not written in this ticket | zero hits |
| P5 | `.claude-plugin/plugin.json` payload | `skills` tree already covers the scripts; `tests/test_plugin_payload_boundary.py` still passes |
| P6 | exit codes | `dispatch_lint` 0/1/3; `receipt_fence_check` 0/1/2/3 (2 = evidence or scan root not a readable directory); `index_pins` 0/1/2/3 (2 = `SHALLOW_HISTORY`, `git` not startable or not a repository, `--json` path not writable; 3 = bad option, index argument missing, not a file or not UTF-8); one test case per code per script |
| P7 | options cannot void a rule | `--chat-words` with an empty or blank list → exit 3 with usage; `--sealed-state` empty or blank → exit 3; the sealed word matches the whole stripped state cell, never a substring; one test per case |
| P8 | generic source cases restored | tests cover: pin-shape negatives (bare 40- and 64-hex, `sha256=` form, only one side present); the three-row `MALFORMED_PIN` orphan canary; a `../leaf` parent-relative leaf; `SEALED_PIN_MISSING`; every word of the default R3 list (subTest over the list itself, not a copy); R5 on line 1 |
| P9 | receipt cells | every cell carries `cell`, `candidate`, `tool_digest` (one `path=sha256` line per script at the candidate), `capture` (path relative to the receipt's directory), `exit`; captures written with LF; the control plane commits receipt and captures under `doc/reviews/workflow-governance/evidence/48/` at integration |
| M1 | remove rule R3 from dispatch_lint | P1 red |
| M2 | make receipt_fence_check accept a fence without capture | P2 red |
| M3 | make index_pins ignore the digest column | P3 red |
| M4 | index_pins accepts a bare 40- or 64-hex cell as a pin | P3 red |
| M5 | index_pins drops the `MALFORMED_PIN` orphan finding | P3 red |
| M6 | index_pins replaces the leading `./` strip loop by `lstrip("./")` | P3 red |
| M7 | index_pins replaces `SEALED_PIN_MISSING` by a silent `continue` | P3 red |
| M8 | index_pins exits 1 instead of 2 on `SHALLOW_HISTORY` | P3 red |
| M9 | dispatch_lint default R3 list cut to three words | P1 red |
| M10 | dispatch_lint R5 skips line 1 | P1 red |
| M11 | dispatch_lint accepts an empty `--chat-words` list | P1 red |
| M12 | index_pins `--sealed-state` matches as a substring | P3 red |

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/48-port-gate-scripts-code-review.md`. F-02 is a `TICKET_DEFECT`: the ticket listed 0/1/3 for every script while R4-2 and R4-7 require tool faults to exit 2; the closure is rebuilt before the correction (CodeReview.md §4 item 3). The correction is one additive commit c3 on `cp/wave1-ticket48-candidate` by an `implementation-standard` seat; revision02 then gets its initial review.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| F-01 | IMPLEMENTATION_DEFECT | P6: non-UTF-8 index → 3; unwritable `--json` → 2; no uncaught exception reaches the caller as exit 1 |
| F-02 | TICKET_DEFECT | P6 re-frozen with the tool-fault exit per script; `SHALLOW_HISTORY` and git-not-startable → 2; README exit paragraph follows |
| F-03 | IMPLEMENTATION_DEFECT | P7 and M11, M12 |
| F-04 | EVIDENCE_DEFECT | P8 and M4–M7, M9, M10 |
| F-05 | EVIDENCE_DEFECT | P9; the P4 rerun uses the current cell wording (scripts and `tests/test_gate_*.py`) |
| F-06 | OUT_OF_SCOPE_HARDENING | carried to the wave-2 evidence-gate ticket: a run that checked nothing never exits 0 |
| Admission note | — | c3 is additive on the candidate branch; the control plane cherry-picks c1–c3 onto the branch tip after `APPROVED`; the dependency "ticket 47 reviewed" is cleared before integration, not before this correction |
