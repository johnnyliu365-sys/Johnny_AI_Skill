# R02C2A — Requirement-lineage Contract Source-gate Closure

| Field | Value |
| --- | --- |
| Parent / reason | R02C2 candidate `5cbe34f2fba1e5bfad3227132394dfcc782916cd`; `CR-R02C2-001` and `CR-R02C2-002` exposed incomplete ACX6 evidence coverage, not a behavior or product-requirement defect. |
| SPEC / Context | Existing R02C2 ACX6 only; `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 05 / `doc/context/adaptive-project-orchestration/main.md` at `SPEC_REVISION_05_APPROVED / ROUTER_PHASE_ACTIVE`. No Context or SPEC fact is changed. |
| State / closure | `PLANNED / NON_DISPATCHED`; `CLOSURE-ADAPTIVE-ROUTER-R02C2A-01`, ACX-A1 through ACX-A6, revision `r02c2a-01`. |
| Implementation language / checker | Python 3.11; `python -B -m mypy --strict --explicit-package-bases --no-incremental library tests`. |
| Delivery profile | `STANDARD`; one `gpt-5.6-luna` max implementation owner; no helper. |
| Control / implementation owner | Reviewer task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; existing implementation task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`. |
| Lane / branch evidence | Same permanent implementation worktree only. `FRESH_BRANCH_REQUIRED`: R02C2's reviewed candidate is immutable evidence; a child ticket must branch from exact handoff `5cbe34f2fba1e5bfad3227132394dfcc782916cd` into `codex/implementation-router-requirement-lineage-source-gate-r02c2a`, carrying only the stopped, uncommitted test WIP after exact diff admission. No new worktree. |
| Planned binding | Handoff `hnd-adaptive-router-r02c2a-20260815`; allocation `aln-adaptive-router-r02c2a-20260815`; receipt `rcpt-adaptive-router-r02c2a-20260815`; correlation `corr-adaptive-router-r02c2a-20260815`; question `q-adaptive-router-r02c2a-20260815`; side Context `scx-adaptive-router-r02c2a-20260815-01`; expected return `ret-requirement-lineage-source-gate-review-handoff-r02c2a`. |
| XSS / effects | `XSS_NOT_APPLICABLE`; test-only AST/text analysis of repository source. No Browser/WebView/HTML/DOM/JS context, source body parsing, filesystem/product effect, Git effect, Agent, host or network port. |

## One observable outcome

`test_source_gate_is_strong_typed_and_effect_free` is a bounded, deterministic ACX6 gate. It
accepts the exact R02C2 `contracts.py` boundary and rejects three in-memory source mutations:

1. a forbidden module import;
2. a dynamic/effect bypass in `_lineage_metadata_is_safe`; and
3. an untyped/raw domain field in one named R02C2 contract model.

It never writes or executes mutated source, scans no unrelated module, and does not change
`RequirementLineageGate` runtime behavior.

## Exact source boundary

Writable implementation path: `tests/test_workflow_requirement_lineage.py` only.

Read-only dependencies: the complete R02C2 candidate (`contracts.py`, `requirement_lineage.py`,
`__init__.py`), all Router/artifact-tree tests, ticket/Context/SPEC/review records. The final
handoff may append only `doc/WorkProgressReport.md` in its own commit.

The guard's contract-source manifest is exact and finite:

```text
module import boundary of library/workflow_router/contracts.py
RequirementId / RequirementChangeId / RequirementArchiveId
RequirementLifecycle / RequirementLineageDecisionKind / RequirementLineageInvalidReason
_lineage_metadata_is_safe
RequirementArchiveBundle / RequirementLineageRecord
RequirementLineageValidationRequest / RequirementLineageValidationDecision
```

All other `contracts.py` declarations are out of scope. The test may use AST plus test-local
typed helpers only; it must not use Git, subprocess, dynamic member access, `eval`, `exec`,
runtime import of mutated text, a writable port or a broad exception.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `ACX-A1` | The source gate accepts the exact canonical `contracts.py` and `requirement_lineage.py` sources, and the public lineage import/behavior checks remain green. |
| `ACX-A2` | It permits only the canonical ordinary import boundary for `contracts.py`; an injected forbidden import is rejected by an in-memory mutation without executing that source. |
| `ACX-A3` | It asserts `_lineage_metadata_is_safe` has exactly its named typed input/output and bounded pure AST shape; injected dynamic/effect bypass text is rejected in memory. |
| `ACX-A4` | It asserts the three aliases, three enums and four strict `RouterModel` declarations have the frozen named fields/finite values; an injected raw/untyped contract field is rejected in memory. |
| `ACX-A5` | The guard remains bounded to the listed manifest. No production `contracts.py`, `requirement_lineage.py` or `__init__.py` bytes change; existing active/retired path behavior, public exports and three R02C2 reversals remain unchanged. |
| `ACX-A6` | Dedicated source-gate/lineage test, artifact-tree/Router regression, explicit serial full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology/porcelain/cache readback all pass. |

## Admission, TDD and return

The stopped old branch has exactly one uncommitted test-file WIP. It is not authority and must
not be reset, discarded, staged or committed before this ticket's admission. Read its exact diff;
after creating the authorized child branch from `5cbe34f2...`, retain it only if it is contained
within the one writable path and can be made to satisfy ACX-A1 through ACX-A6. Otherwise return
`CHANGE_DETECTED`—never overwrite or delete it.

First red is an in-memory contract-source mutation that the pre-ticket source gate fails to
reject. Record that failure before completing the bounded source-analyzer helper and the three
negative mutation proofs. Return one test-only implementation commit, then one WPR-only handoff
with first-red output, ACX mapping, mutation proofs, exact commands and clean readback.

No new worktree, branch other than the named child branch, production-source change, R02C3-R06,
helper/subagent, self-review/integration, external effect, push, package/install, Secret, release
or deployment is authorized.
