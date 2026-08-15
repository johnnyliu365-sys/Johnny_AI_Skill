# PAG-02 — Exact progress-leaf reference policy

## Admission

| Field | Value |
| --- | --- |
| Ticket ID | `PAG-02-progress-leaf-reference-policy` |
| State | `PLANNED / READY_LOW_MODEL / NON_DISPATCHED` |
| Closure set | `PAG-02-CS-01` |
| Authority | `PRD-20260815-022` / `CHG-20260815-022`; [`REQ-20260815-022`](../../../../doc/requirements/active/2026/adaptive-orchestration/REQ-20260815-022.md); [`adaptive-project-orchestration.md`](../../../spec/adaptive-project-orchestration.md) Revision 05 AC-17; [`DEC-20260816-519`](DEC-20260816-519.md) |
| Baseline | reviewed integration commit of `PAG-01`, recorded by the later receipt; no baseline is inferred now |
| Context | sealed `CONTEXT.md`; no Context append/revision is authorised |
| Logical implementation owner | one `IMPLEMENTATION_OWNER`, `gpt-5.6-luna`, high reasoning; task/worktree/branch/receipt are `UNBOUND` until later Router admission |
| Reviewer | receipt-bound `SUPERVISOR_REVIEWER`, unbound until dispatch |
| Environment / resource plan | local Markdown/reference validation; one implementation lane; no helper or external capability |
| Dependency | `PAG-01` must be `COMPLETE / APPROVED / INTEGRATED` |
| Implementation language / strict checker | Markdown policy only; no production helper is authorised, so Python strict checking is `N/A`; deterministic link/reference and forbidden-legacy-wording checks are mandatory |
| XSS / UI | `N/A`: no rendered untrusted data or JavaScript/Native bridge capability |

## One observable closure

After the progress tree exists, every active governance, ticket-template, handoff-template, and
dispatch reference points to an exact progress leaf and no active rule requires a separate
`WorkProgressReport.md`-only append commit. Historical sealed tickets and reviews remain
unchanged Git evidence.

## Exact writable scope and policy boundary

Only these active documentation paths may change:

```text
AGENTS.md
Workflow.md
modules/tickets/TEMPLATE.md
doc/handoffs/README.md
skills/johnny-project-takeover/references/implementation-tdd.md
skills/johnny-project-takeover/references/specification-ticketing.md
```

The policy describes `doc/WorkProgressReport.md` only as the compatibility root index and requires
an exact `doc/progress/<year>/<month>/<day>/<PRG-ID>.md` reference for a new ticket or handoff. It
removes the active requirement that results are recorded in a separate WorkProgressReport-only
append commit. It must not edit any historical `modules/tickets/**` leaf other than this ticket,
any `doc/reviews/**` leaf, any requirement/SPEC/Context/ADR, or any source/test/runtime file.

## Finite TDD and review matrix

| Cell | First-red command and expected failure | Green acceptance |
| --- | --- | --- |
| `PAG-02-T01` active reference gate | repository documentation check fails while an active governed template/dispatch source still requires a WPR append or lacks exact-leaf wording | all six writable active sources resolve local links and describe exact-leaf evidence only |
| `PAG-02-T02` historical evidence guard | scope check fails when a sealed historical ticket/review path is included | only the six named active paths change; historical ticket/review hashes remain unchanged |
| `PAG-02-T03` direct-reference shape | documentation check fails when a sample reference is a root/index, raw PRG ID alone, absolute path, or missing date/leaf components | every normative new ticket/handoff example uses the exact relative progress-leaf shape |

The checker may be a checked test or bounded repository validation command, but it must
distinguish active policy sources from frozen historical evidence and must have no network,
filesystem mutation outside the named docs, or dynamic execution behavior.

## Verification, rollback and typed return

```powershell
python -m unittest discover -s tests
git diff --check
git diff --name-only <PAG-01-integration-commit>..HEAD
git status --short
```

Run the ticket's active-reference checker and local Markdown link check, record first-red output,
and prove that the integration diff changes only the six named files. Roll back only by reverting
the single policy integration commit; do not reset, amend, delete history, or modify historical
sealed evidence.

Return `ImplementationReturn.COMPLETED` with one docs-only commit, checker/link/diff evidence,
and exact new progress leaf reference. Return `BLOCKED` if `PAG-01` is not integrated or a
normative source outside the approved writable set is required. Return `CHANGE_DETECTED` if a
listed active policy source changes after receipt binding. No return grants review, merge, release,
deployment, or external effect.
