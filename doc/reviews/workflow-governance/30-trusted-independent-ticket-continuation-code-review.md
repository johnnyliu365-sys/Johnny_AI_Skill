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

Final carrier review found the legacy integration parser requires a nonempty
`modify` list even for a create-only ticket. No gate change or extra source
permission was authorized. Root and the independent reviewer verified the
existing forbid-first evaluator can encode an empty effective modification set:
the schema-only `modify = AGENTS.md` sentinel is also unconditionally forbidden.
Public parser/evaluator probes allowed exactly the two CREATE paths, rejected
all 1,116 currently tracked MODIFY/DELETE paths, case variants of the sentinel,
modifications of the new paths, and an ungranted CREATE. Root's first cp950
text-decoding probe failed before evaluation; the explicit UTF-8 probe passed.
No effect API ran. The reviewer accepted this exact expression as no permission
expansion, subject to committed-ticket readback; the ticket documents its
non-authorizing meaning. Only the final cumulative two-file candidate may be
integrated; Phase A is not independently merged and used to reset the boundary.

## 30A Phase A and initial Phase B review

Dispatch baseline `d2f2aa1030e2d817f9e3a016e5dfacf11ce0c22d`, ticket blob
`4ac13403b75f265522633e6989a6c8e03b734b22`; implementation worktree
`.worktrees/skill-improvement-30a-fixture`, branch
`codex/skill-improvement-30a-fixture`, actor `/root/ticket30a_fixture_impl`
(`gpt-6-luna/xhigh`). Different reviewer `/root/ticket30a_fixture_review`
(`gpt-6-sol/high`) owns `.worktrees/skill-improvement-30a-review`.

Phase A `79c98d77b1f2a5b8d92bd36b42c42aac2ae910ec` was independently
`APPROVED`: 45 focused tests, strict mypy, compile and diff checks passed;
all eight failure enums and three blob statuses were constructed/round-tripped.
Reviewer disabled the request's WORKTREE_HEAD guard: five negatives failed
with DID NOT RAISE, then all five passed after exact restoration (source blob
`51aa7fbb0c385823366f309e9c73b4ea0536f5cc`). Root separately ran 32
constructor tests and strict mypy. Actual types, not prototypes, admitted Phase B.

Phase B `43c9ebf1081f189e9adeb87f3717b6b50a2ec1b9` had 83 focused tests,
strict mypy, compile and diff checks green; cumulative diff remained two CREATE
paths. Implementer digest and leaf-revision bypass mutations each made its
named cell fail, then restored 4/4 green. Independent reviewer mutation removed
the same-feature guard: the cross-feature case returned LEAF_NOT_FOUND instead
of INDEX_SCHEMA_INVALID; after restoration all three path cases passed and
source blob returned to `278e042a39f871c9e760713d461f54aefc2d2b43`.

Review was `CHANGES_REQUESTED`, not a false closure: F2 accepted a second
heading with trailing whitespace; a public 1,200-deep JSON probe raised
RecursionError; F3 safely reproduced inherited GIT_DIR redirecting fixture
initialization outside its own root. F1 allowed empty/duplicate bindings;
reviewer classified missing cardinality as TICKET_DEFECT, so Root clarified
the existing four-source completeness in same-ticket Closure revision 02.
No new field, resolver, SPEC, PRD, scope or budget was added. Original author
and reviewer continue all four findings and retain valid Phase A evidence.

Structural review inspected the 427-line product module as one source-assembly
responsibility and the 1,019-line test as constructor checks, private fixture
lifecycle/serialization and the same capability's case matrix. The threshold
triggered review, not automatic splitting/deletion; existing Git test helpers
were private unittest methods rather than an available shared harness. The
correction must remain parameterized and cannot grow a parallel framework.
