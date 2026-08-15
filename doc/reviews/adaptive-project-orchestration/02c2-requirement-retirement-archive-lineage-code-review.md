# Router R02C2 Requirement Retirement and Archive Lineage Gate Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `02c2-requirement-retirement-archive-lineage` / `CLOSURE-ADAPTIVE-ROUTER-R02C2-01` ACX1-ACX8 revision `r02c2-01` |
| Dispatch registry | `4bd9fb19ac5ee9c8ca38348e103fec0877d53885` / `PRG-20260815-489` |
| Implementation / handoff | `e24ad619684dfd08d7faa4161ab3dbe91170b7cb` / `49037f60b1061a1c893c8d5c0c15bc54388a4221` (`PRG-20260815-490`) |
| Branch / owner | `codex/implementation-router-requirement-lineage-r02c2` / task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` |
| Review result | `CHANGES_REQUESTED / EVIDENCE_DEFECT / SAME_BRANCH_CORRECTION` |

The submitted behavior, receipt binding and scope are valid. Approval is withheld only because
the ACX6 committed source guard does not cover all R02C2-owned source: it scans
`requirement_lineage.py` but not the ticket's new public contract declarations in
`contracts.py`. This is an evidence defect, not a request for wider behavior or architecture.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Immutable review snapshot | PASS: detached ZIP export at exact WPR handoff; no implementation-worktree mutation. |
| Focused / full | PASS: lineage `11/11`; artifact-tree/Router `63/63`; explicit serial suite `577/577` across `50` test modules. The first parallel attempt was discarded because two suites can share fixture names; the serial result is the valid evidence. |
| Strict typing / compile | PASS: strict mypy with explicit package bases and no incremental cache `154/154`; in-memory compile `154/154`. |
| Reviewer adversarial probes | PASS: active success; PRD/CHG mismatch; root binding mismatch; retirement with a still-live former active path; and stale archive digest each returned the frozen result (`5/5`). |
| Scope / ancestry / residue | PASS: implementation has exactly four authorized source/test paths; handoff changes only WPR; registry ancestry and diff check pass; submitted permanent lane is clean and topology remains exactly three worktrees. |

## Mandatory review checks

- **Clear strong types:** PASS for named PRD/CHG/archive IDs, finite lifecycle/reasons, frozen strict models and exact success/failure decision algebra.
- **Existing conventions:** PASS for the existing `ArtifactTreeResolver` seam and package exports.
- **Logic / edge behavior:** PASS for active leaf equality, retired active-path absence, exact archive leaf/digest proof, finite precedence and opacity of unselected siblings.
- **Security / performance:** PASS. The gate is pure metadata validation; no body/source, arbitrary mapping, dynamic lookup, broad catch, filesystem, Git, Agent, host, network or renderer capability exists. `XSS_NOT_APPLICABLE`.
- **Test truthfulness:** PASS for behavior and reversals; **FAIL** for ACX6 source-gate coverage.
- **Dependencies / scope:** PASS. No dependency change and no out-of-scope implementation path.
- **Specification conformity:** PASS for ACX1-ACX5 and ACX7-ACX8; **FAIL** ACX6 until the contract surface is guarded by committed test evidence.

## Finding

**CR-R02C2-001 — `EVIDENCE_DEFECT`, blocking.**
`tests/test_workflow_requirement_lineage.py` has one ACX6 sentinel, `test_source_gate_is_strong_typed_and_effect_free`, but it reads only `library/workflow_router/requirement_lineage.py`. R02C2 also introduces the three public ID aliases, three finite enums and four strict models in `library/workflow_router/contracts.py`. Consequently an `Any`/`object`/raw domain-string field, construction bypass, dynamic lookup, broad catch or effect import introduced into that owned public contract surface could pass the committed ACX6 sentinel.

## Required same-branch correction

Keep the ticket, implementation owner, permanent worktree, branch, allocation and receipt. Add one test-only correction in `tests/test_workflow_requirement_lineage.py` that parses and guards the R02C2-owned `Requirement*` public contract declarations in `contracts.py`, in addition to the existing `requirement_lineage.py` scan. The guard must remain bounded to those exact declarations; it must not falsely reject older unrelated Router code. It must prove that the new contract fields remain named, explicitly typed and free of the frozen ACX6 bypass forms.

No production-source change, new ticket/branch/worktree, helper, R02C3-R06 work, external effect, push, package/install, Secret, release or deployment is authorized. Return one additive correction commit and one WPR-only handoff after re-running the frozen gates. Any behavior or scope change is `CHANGE_DETECTED`.
