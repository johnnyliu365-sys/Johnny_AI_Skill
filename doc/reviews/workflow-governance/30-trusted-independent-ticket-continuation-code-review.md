# Ticket 30 source-contract decision review — 2026-10-18

| Field | Evidence |
| --- | --- |
| Prior control baseline | `789302c4345aedb5439770ebb7aad1c9ac0f3cd8` |
| Initial decision candidate | `0bfb4a2869f9fbb73e67a3c1a436a8e341fd66c2` — two findings |
| Additive correction | `f13f35711594af241c83b803f91f0f472baa6241`; Ticket30 leaf blob `823ef2d0e86bbc74a8508263be1a8bde678f6324` |
| Independent reviewer | `/root/ticket42_review` (`gpt-6-sol/high`), different from the Architecture Owner analysis |
| Conclusion | `PASS` for bounded docs-only technical source contract; `NON_DISPATCHABLE` remains |

First review found that an index-only graph contradicted workflow-governance
SPEC AC9's committed-leaf derivation, and that existing `GitBlobReadResult`
has a string payload, insufficient for a raw-byte digest claim. The same-ticket
correction requires a unique machine-readable ticket fence in each committed
leaf, compares its graph/status fields with the index and rejects mismatches;
the candidate projection is built only from validated leaves. The bounded
readback port now names a raw-byte result using the existing finite status
enum, hashes those bytes, and strictly decodes UTF-8 before JSON parsing.

Reviewer readback of the exact correction found both findings closed,
one-file docs-only scope, clean worktree and `git diff --check` exit 0. No
runtime tests or external effects were performed; this is a source-contract
decision, not an implemented or qualified adapter. No target facts were
inferred from the human status table. Mainline migration, admitted declaration
readback, ticket-scoped Grant, Router/Host admission, and formal closure stay
unverified. No push or release occurred.

## 30A fixture ticket / decision package docs review — 2026-10-18

| Field | Evidence |
| --- | --- |
| Control baseline | `3ca02bd5e90611c101d97cc79f06b4751c70cd1c` |
| Initial docs candidate | `ed314dae` — Ticket 30, its registry row, checklist revision 24 |
| Same-ticket correction | `406817c485ddb5af78794d797e2f281c397abaaa`; Ticket 30 blob `ded322b3c7e82399c31ff4cf67d3dbf3237af3fb` |
| Independent reviewer | `/root/ticket30_docs_review`, read-only and separate from Root author |
| Conclusion | `PASS` for **docs-only preparation**; `SPEC_BOOTSTRAP_DECISION_REQUIRED / TICKET_GRANT_REQUIRED / NON_DISPATCHABLE` remain |

The independent reviewer found three defects in the first docs candidate:
the recommended `CONTEXT.md` anchor is sealed and needs an authorized
Architecture Owner `REVISE`; the existing workflow-governance SPEC still
forbids Ticket 30 dispatch until source and Host binding, so fixture bootstrap
requires an explicit bounded exception in the original Change Control; and
the nine-ref remote CI inventory needed its actual batch command and path
predicate, not only a main-branch example. Correction `406817c4` records
each constraint without writing Context/SPEC, activating a Grant, or treating
an empty CI command list as test-retirement authority. The reviewer reread
the exact correction and marked all three findings `CLOSED`.

The reviewer briefly reported an index mismatch, then checked the full
`406817c4` registry and checklist and withdrew it: both explicitly require
the SPEC bootstrap decision before Grant. Root ran
`python -m pytest tests/test_mainline_projection.py tests/test_ticket_template_contract.py -q`
(`59 passed`) and `git diff --check`; the reviewer checked the committed
docs with `git show --check`. No source adapter, true declaration readback,
`admit_dispatch`, native spawn, Host qualification, push or release was tested
or performed. Checklist 02/08 therefore remain unchecked.

## Owner-approved authority revision and 30A construction admission

Owner's subsequent decision pins `acf0ffa1780af3d229b7f80c6e063f6d642e6864`
and Ticket 30 blob `ded322b3c7e82399c31ff4cf67d3dbf3237af3fb`, approving
the two recommendations with exact constraints. Root acted as Architecture
Owner only for lawful Context `REVISE` and original CHG/SPEC/Ticket updates;
the separate implementer role remains mandatory for the two source/test files.

Independent `/root/ticket30_docs_review` read candidate `e551c556`, correction
`7779c815` and final bounded scope clarification `35b25d60`. The actual new
constructors cannot be preflighted while nonexistent: the reviewed same-ticket
type-only Phase A creates declarations/tests only, and requires actual
constructor/negative/round-trip/strict evidence and independent review before
Phase B behavior. Cumulative `CREATE` is measured against the original
dispatch baseline; Phase A does not reset scope or allow preexisting-file
modifications. Both findings are `CLOSED`; limited docs/ticket review `PASS`.
The reviewer confirmed old sealed03 commit/blob and CHG provenance, unchanged
stable facts, exact repository/ref/topology and unchanged final AC9–11/effect
requirements. The seal/active-boundary writeback only materializes this reviewed
conditional admission; it grants no formal source or Host qualification.

Root checks on the unchanged existing dependency/code baseline:
`python -m pytest tests/test_shared_context_service.py tests/test_ticket_template_contract.py -q`
returned `54 passed, 15 subtests passed`; ordinary observation/projection
dependencies via `python -m pytest tests/test_mainline_projection.py tests/test_project_authority_contracts.py -q`
returned `20 passed`; `git diff --check` passed. These are design/preflight
regressions, not the nonexistent 30A module's success evidence. The final
dispatch commit, leaf blob and worktree identity are independently read back
before the admitted type-only native delegation; exact values will be sealed
with implementation review evidence.
