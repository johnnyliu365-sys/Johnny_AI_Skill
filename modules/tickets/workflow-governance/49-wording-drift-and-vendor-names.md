# 49｜Vendor and model names out of governance documents

| Field | Binding |
| --- | --- |
| State / Closure | CONVERGENCE_REPLANNED / INDEPENDENT_REVIEW_PENDING; 49-W1–W5 revision04 (revision03 corrected before evidence: captures place added) after the revision02 initial review returned CHANGES_REQUESTED (N49-01 TICKET_DEFECT, N49-04); revision01 initial review CHANGES_REQUESTED (R49-01 to R49-05) |
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

No document on this line names the source project the gate scripts were ported from. In the boundary files, every live role, grant, authority, workspace, location and handoff statement names a role or a profile (`decision-support`, `ticket-review`, `implementation-standard`), says "the control plane", or uses a ref or file name; it never uses a vendor or model name as a role holder or a location. Exempt as records of who acted at a dated baseline: the spec "Authoring AI / baseline" row, the spec Revision Signatures and Approval Record rows, and the tickets of the earlier line (01–23), which are outside this boundary. A literal may appear where it is the object of a check or a finding: this ticket's W1 row and corrections table, and the review record. Denylists of target names are carried by the dispatch file of the run that uses them, never spelled in a ticket. No boundary file carries a host absolute path.

## Acceptance

The file list `<B>` of W1, W3, W4 and W5 is exactly the boundary set above:
`modules/spec/workflow-governance.md doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md modules/tickets/workflow-governance/47-gates-first-governance-rewrite.md modules/tickets/workflow-governance/48-port-gate-scripts.md modules/tickets/workflow-governance/49-wording-drift-and-vendor-names.md modules/tickets/workflow-governance/README.md doc/reviews/workflow-governance/49-wording-drift-and-vendor-names-code-review.md doc/reviews/workflow-governance/evidence/49`.

| Cell | Check | Expected |
| --- | --- | --- |
| W1 | `git grep -nE "Opus|Sonnet|Haiku|Claude control plane|Codex control plane|Codex/current worktree|Codex branch" -- <B>` | every hit is in one of these places and the capture lists each hit under its place: (a) this W1 row; (b) the spec "Authoring AI / baseline" row and the spec Revision Signatures row dated 2026-08-05; (c) a row of this ticket's "Ticket corrections" table; (d) a line of the review record; (e) a capture under `evidence/49/` that records a W1 or W5 run. No hit anywhere else |
| W2 | `grep -n "| P4 |" modules/tickets/workflow-governance/48-port-gate-scripts.md` | the P4 cell names the dispatch file as the carrier of its denylist and spells no name |
| W3 | `git grep -nE "(^|[^A-Za-z])[A-Z]:[/\\\\]" -- <B>` | zero hits (no host absolute path in any boundary file, review record or capture of this ticket) |
| W4 | `git diff --name-only 7335e78..HEAD` | every path is in this boundary block or in ticket 47's; the capture lists each path under the ticket it belongs to; no forbid path of either ticket outside the other's boundary |
| W5 | `git grep -niE "codex|claude|anthropic|openai|gpt|gemini|opus|sonnet|haiku|fable" -- <B>` | every hit is classified in the capture as one of: functional host or file or ref name; dated record; object of a check or finding (W1 places a–e). Zero hits classified as a live role holder or location |

## Ticket corrections (control plane)

| When | Cell | Was | Now |
| --- | --- | --- | --- |
| revision01, before review (defective: made in the implementation commit) | W1 | scanned every ticket under `modules/tickets/workflow-governance`, including this row itself, so zero hits was unreachable | scoped to named files |
| revision01, after the README edit (defective: order) | boundary | did not list the tickets README | row added |
| revision02 (R49-02) | closure | revision01 kept after an Expected change | rebuilt as revision02 in its own commit before the implementation commit |
| revision02 (R49-03) | W1 reason | said tickets 01–23 are "closed"; six are `IN_PROGRESS` | exemption restated: they are the earlier line's tickets, outside this boundary, kept as records |
| revision02 (R49-04) | W1 pattern | could not see the two other control-plane vendor literals left in the spec header rows and the README authority paragraph | pattern extended to them; dated records exempt by name |
| revision02 (R49-05) | boundary | this ticket's own leaf missing | row added, plus the review record and evidence directory |
| revision02 (R49-01) | W2 | required "a parameter file named in the ticket"; ticket 48 named none | the dispatch file is that parameter file; ticket 48 P4 names it as the carrier |
| revision02 (R49-06) | W3 | — | new cell: no host absolute paths in boundary files |
| revision02, defective again (N49-01): the R49-04 row above spelled the literals it describes, so W1 "exactly three hits" was unreachable as frozen, and the row was reworded in the implementation commit `fb55623f` | W1 | count-based Expected | revision03, frozen in its own commit before any fix: Expected names the permitted places (a)–(d); the corrections table and the review record may quote a literal as the object of a check |
| revision03 (N49-04) | W1, W3 file list | the REQ directory instead of the REQ file; the two `create` entries missing | `<B>` is exactly the boundary set |
| revision03 (N49-02) | receipt | Boundary had no row; Observable behavior had no capture | W4 and W5 added as cells with captures |
| revision03 (N49-03) | W1 pattern | "Codex branch" (ticket 47, a live location statement) invisible | pattern extended; the implementation names the ref instead |
| revision03 (N49-05) | — | raw pytest captures under `evidence/47/` carry host paths | routed to ticket 47 as a wave-2 evidence-gate rule (the capture step strips the checkout and interpreter roots); not a cell of this ticket |
| revision04, frozen before any evidence of revision03 was produced (self-found while running W1) | W1, W5 | the permitted places (a)–(d) left out the captures under `evidence/49/`, which quote the hits of every W1 and W5 run, so "no hit anywhere else" was unreachable | place (e) added; `<B>` unchanged |
