# PAG-02 — Exact progress-leaf reference policy

## Admission

| Field | Value |
| --- | --- |
| Ticket ID | `PAG-02-progress-leaf-reference-policy` |
| State | `PLANNED / READY_LOW_MODEL / NON_DISPATCHED` |
| Closure set | `PAG-02-CS-02` |
| Authority | `PRD-20260815-022` / `CHG-20260815-022`; [`REQ-20260815-022`](../../../../doc/requirements/active/2026/adaptive-orchestration/REQ-20260815-022.md); [`adaptive-project-orchestration.md`](../../../spec/adaptive-project-orchestration.md) Revision 05 AC-17; [`DEC-20260816-520`](DEC-20260816-520.md) |
| Baseline | reviewed integration commit of `PAG-01`, recorded by the later receipt; no baseline is inferred now |
| Context | sealed `CONTEXT.md`; no Context append/revision is authorised |
| Logical implementation owner | one `IMPLEMENTATION_OWNER`, `gpt-5.6-luna`, xhigh reasoning; task/worktree/branch/receipt are `UNBOUND` until later Router admission |
| Reviewer | receipt-bound `SUPERVISOR_REVIEWER`, unbound until dispatch |
| Environment / resource plan | local Python 3.11 policy-test plus Markdown/reference validation; one implementation lane; no helper or external capability |
| Dependency | `PAG-01` must be `COMPLETE / APPROVED / INTEGRATED` |
| Implementation language / strict checker | Python 3.11 checked policy test plus Markdown; `python -m mypy --strict tests/test_progress_leaf_policy.py` is mandatory; no production helper is authorised |
| XSS / UI | `N/A`: no rendered untrusted data or JavaScript/Native bridge capability |

## One observable closure

After the progress tree exists, every active governance, ticket-template, handoff-template, and
dispatch reference points to an exact progress leaf and no active rule requires a separate
`WorkProgressReport.md`-only append commit. Historical sealed tickets and reviews remain
unchanged Git evidence.

## Exact writable scope and policy boundary

Only these seven active policy/template paths and one checked test may change:

```text
AGENTS.md
Workflow.md
modules/tickets/TEMPLATE.md
doc/handoffs/README.md
skills/johnny-project-takeover/references/implementation-tdd.md
skills/johnny-project-takeover/references/specification-ticketing.md
template/README.md
tests/test_progress_leaf_policy.py
```

The policy describes `doc/WorkProgressReport.md` only as the compatibility root index and requires
an exact `doc/progress/<year>/<month>/<day>/<PRG-ID>.md` reference for a new ticket or handoff. It
removes the active requirement that results are recorded in a separate WorkProgressReport-only
append commit. `template/README.md` scaffolds the `doc/progress/<year>/<month>/<day>/` partition
tree and identifies `WorkProgressReport.md` as a root index. The ticket must not edit any
historical `modules/tickets/**` leaf other than itself, any `doc/reviews/**` leaf, any
requirement/SPEC/Context/ADR, or any source/test/runtime path other than the one named policy test.

## Finite TDD and review matrix

| Cell | First-red command and expected failure | Green acceptance |
| --- | --- | --- |
| `PAG-02-T01` active reference gate | `python -m unittest tests.test_progress_leaf_policy.ProgressLeafPolicyTests.test_all_active_policy_and_bootstrap_sources_require_exact_progress_leafs` fails before policy wording/test implementation exists | all seven active policy/template sources resolve local links and describe exact-leaf evidence only |
| `PAG-02-T02` historical evidence guard | `python -m unittest tests.test_progress_leaf_policy.ProgressLeafPolicyTests.test_policy_scope_excludes_sealed_ticket_and_review_leaves` fails before the scope gate exists | only seven named policy/template paths plus the checked test change; historical ticket/review hashes remain unchanged |
| `PAG-02-T03` direct-reference and source gate | `python -m unittest tests.test_progress_leaf_policy.ProgressLeafPolicyTests.test_normative_examples_are_exact_relative_leaf_refs_and_checker_is_bounded` fails before the checker exists | every normative new ticket/handoff example uses the exact relative progress-leaf shape; the test has typed inputs/outputs and rejects dynamic execution, absolute paths, root/index refs, raw PRG IDs, and missing date/leaf components |

`tests/test_progress_leaf_policy.py` is the only checker. It must distinguish the seven active
policy/template sources from frozen historical evidence and have no network, filesystem mutation,
subprocess, dynamic execution, `Any`, cast, `type: ignore`, or source-discovery behavior outside
its explicit allowlist.

## Verification, rollback and typed return

```powershell
python -m unittest tests.test_progress_leaf_policy
python -m unittest discover -s tests
python -m mypy --strict tests/test_progress_leaf_policy.py
python -m py_compile tests/test_progress_leaf_policy.py
git diff --check
git diff --name-only <PAG-01-integration-commit>..HEAD
git status --short
```

Run the named active-reference checker and local Markdown link check, record first-red output, and
prove that the integration diff changes only the seven named policy/template paths plus the checked
test. Roll back only by reverting the single policy/test integration commit; do not reset, amend,
delete history, or modify historical sealed evidence.

Return `ImplementationReturn.COMPLETED` with one policy/test integration commit, checker/link/
diff/type/compile evidence, and exact new progress leaf reference. Return `BLOCKED` if `PAG-01` is
not integrated or a normative source outside the approved writable set is required. Return
`CHANGE_DETECTED` if a listed active policy source changes after receipt binding. No return grants
review, merge, release, deployment, or external effect.
