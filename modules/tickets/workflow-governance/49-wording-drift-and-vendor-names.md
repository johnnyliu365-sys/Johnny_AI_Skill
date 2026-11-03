# 49｜Vendor and model names out of governance documents

| Field | Binding |
| --- | --- |
| State / Closure | LOCAL_IMPLEMENTED / INDEPENDENT_REVIEW_PENDING (W1, W2 and source-project names done); 49-W1–W2 revision01 |
| Authority | `PRD-20261103-043` / `CHG-20261103-043`; REVIEW of ticket 47 finding F-12 |
| Baseline | branch `cp/wave1-gates-first` after ticket 47 revision02 |
| Grant / roles | Control plane authors; independent review |
| Profile / limits | COMPACT; documents only |

```johnny-boundary
modify = modules/spec/workflow-governance.md
modify = doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md
modify = modules/tickets/workflow-governance/47-gates-first-governance-rewrite.md
modify = modules/tickets/workflow-governance/48-port-gate-scripts.md
forbid = library/
forbid = skills/
forbid = tests/
```

## One observable behavior

No document on this line names the source project the gate scripts were ported from; governance documents name roles and profiles (`decision-support`, `ticket-review`, `implementation-standard`), never a vendor or model literal; ticket denylists for target names are expressed as a parameter file, not spelled in the ticket.

## Acceptance

| Cell | Check | Expected |
| --- | --- | --- |
| W1 | `git grep -nE "Opus|Sonnet|Haiku|Claude control plane" -- modules/spec modules/tickets/workflow-governance/47-*.md modules/tickets/workflow-governance/48-*.md modules/tickets/workflow-governance/49-*.md doc/requirements/active/2026/workflow-governance` | exactly one hit: this row, which carries the pattern. Closed tickets 01–23 are historical records outside this boundary and keep their text |
| W2 | ticket 48 cell P4 | reads its denylist from a parameter file named in the ticket, not from the ticket text |

## Ticket correction (control plane, before review)

| Cell | Was | Now |
| --- | --- | --- |
| W1 | scanned every ticket under `modules/tickets/workflow-governance`, including closed tickets 01–23 outside this boundary and this row itself, so zero hits was unreachable | scoped to the boundary files; this row is the one permitted occurrence of the pattern |
