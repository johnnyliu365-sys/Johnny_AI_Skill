# 49｜Vendor and model names out of governance documents

| Field | Binding |
| --- | --- |
| State / Closure | CONVERGENCE_REPLANNED / INDEPENDENT_REVIEW_PENDING; 49-W1–W3 revision02 after the revision01 initial review returned CHANGES_REQUESTED (R49-01 to R49-05) |
| Authority | `PRD-20261103-043` / `CHG-20261103-043`; REVIEW of ticket 47 finding F-12 |
| Baseline | branch `cp/wave1-gates-first` after ticket 47 revision02 |
| Grant / roles | Control plane authors; independent review |
| Profile / limits | COMPACT; documents only |

```johnny-boundary
modify = modules/spec/workflow-governance.md
modify = doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md
modify = modules/tickets/workflow-governance/47-gates-first-governance-rewrite.md
modify = modules/tickets/workflow-governance/48-port-gate-scripts.md
modify = modules/tickets/workflow-governance/49-wording-drift-and-vendor-names.md
modify = modules/tickets/workflow-governance/README.md
create = doc/reviews/workflow-governance/49-wording-drift-and-vendor-names-code-review.md
create = doc/reviews/workflow-governance/evidence/49/
forbid = library/
forbid = skills/
forbid = tests/
```

## One observable behavior

No document on this line names the source project the gate scripts were ported from. In the boundary files, every live role, grant, authority, workspace and handoff statement names a role or a profile (`decision-support`, `ticket-review`, `implementation-standard`) or says "the control plane"; it never names a vendor or a model. Exempt as records of who acted at a dated baseline: the spec "Authoring AI / baseline" row, the spec Revision Signatures and Approval Record rows, and the tickets of the earlier line (01–23), which are outside this boundary. Denylists of target names are carried by the dispatch file of the run that uses them, never spelled in a ticket. No boundary file carries a host absolute path.

## Acceptance

| Cell | Check | Expected |
| --- | --- | --- |
| W1 | `git grep -nE "Opus|Sonnet|Haiku|Claude control plane|Codex control plane|Codex/current worktree" -- modules/spec/workflow-governance.md modules/tickets/workflow-governance/47-*.md modules/tickets/workflow-governance/48-*.md modules/tickets/workflow-governance/49-*.md modules/tickets/workflow-governance/README.md doc/requirements/active/2026/workflow-governance` | exactly three hits: this row (it carries the pattern), the spec "Authoring AI / baseline" row and the spec Revision Signatures row dated 2026-08-05 (dated records, exempt above) |
| W2 | `grep -n "| P4 |" modules/tickets/workflow-governance/48-port-gate-scripts.md` | the P4 cell names the dispatch file as the carrier of its denylist and spells no name (the entries are known to the dispatch, not to this ticket) |
| W3 | `git grep -nE "(^|[^A-Za-z])[A-Z]:[/\\\\]" -- <the W1 file list>` | zero hits (no host absolute path in any boundary file) |

## Ticket corrections (control plane)

| When | Cell | Was | Now |
| --- | --- | --- | --- |
| revision01, before review (defective: made in the implementation commit) | W1 | scanned every ticket under `modules/tickets/workflow-governance`, including this row itself, so zero hits was unreachable | scoped to named files |
| revision01, after the README edit (defective: order) | boundary | did not list the tickets README | row added |
| revision02 (R49-02) | closure | revision01 kept after an Expected change | rebuilt as revision02 in its own commit before the implementation commit |
| revision02 (R49-03) | W1 reason | said tickets 01–23 are "closed"; six are `IN_PROGRESS` | exemption restated: they are the earlier line's tickets, outside this boundary, kept as records; the W1 file list is explicit and includes the README |
| revision02 (R49-04) | W1 pattern | could not see "Codex control plane" or "Codex/current worktree" | pattern extended; dated records exempt by name |
| revision02 (R49-05) | boundary | this ticket's own leaf missing | row added, plus the review record and evidence directory |
| revision02 (R49-01) | W2 | required "a parameter file named in the ticket"; ticket 48 named none | the dispatch file is that parameter file; ticket 48 P4 names it as the carrier |
| revision02 (R49-06) | W3 | — | new cell: no host absolute paths in boundary files |
